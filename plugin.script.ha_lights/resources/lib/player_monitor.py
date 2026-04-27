"""
Moniteur de lecture Kodi - Pilotage automatique - Regle 1 et Regle 2
"""
import threading
import time
import xbmc
import xbmcaddon

ADDON_ID = 'plugin.script.ha_lights'


def get_addon():
    return xbmcaddon.Addon(ADDON_ID)

def get_setting(key):
    return get_addon().getSetting(key)

def get_setting_bool(key):
    return get_addon().getSetting(key) == 'true'

def get_setting_int(key, default=0):
    try:
        return int(get_addon().getSetting(key))
    except (ValueError, TypeError):
        return default

def _load_config():
    import sys, os
    addon_path = get_addon().getAddonInfo('path')
    lib_path   = os.path.join(addon_path, 'resources', 'lib')
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)
    from config import HA_URL, HA_TOKEN, RULE1_ENTITIES, RULE2_ENTITIES
    return HA_URL, HA_TOKEN, RULE1_ENTITIES, RULE2_ENTITIES

def _make_client():
    import sys, os
    addon_path = get_addon().getAddonInfo('path')
    lib_path   = os.path.join(addon_path, 'resources', 'lib')
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)
    from ha_client import HomeAssistantClient
    ha_url, ha_token, _, _ = _load_config()
    url   = ha_url   if ha_url   else get_setting('ha_url')
    token = ha_token if ha_token else get_setting('ha_token')
    if not url or not token:
        return None
    return HomeAssistantClient(url, token)

def notify(msg, duration=4000):
    xbmc.executebuiltin('Notification(HA Lights, {}, {}, )'.format(msg, duration))

def _entity_list(raw):
    if not raw:
        return []
    return [e.strip() for e in raw.split(',') if e.strip()]


class TimerManager:
    def __init__(self):
        self._timers = {}

    def cancel(self, name):
        t = self._timers.pop(name, None)
        if t:
            t.cancel()

    def cancel_all(self):
        for name in list(self._timers.keys()):
            self.cancel(name)

    def schedule(self, name, delay_seconds, callback):
        self.cancel(name)
        t = threading.Timer(delay_seconds, callback)
        t.daemon = True
        self._timers[name] = t
        t.start()


class RuleHandler:
    """Gere le pilotage pour une regle independante (rule1 ou rule2)."""

    def __init__(self, rule, timers, player):
        self.rule   = rule
        self.timers = timers
        self.player = player
        self.saved  = {}
        self.armed  = False

    def _s(self, key):
        return get_setting('{}_{}'.format(self.rule, key))

    def _sb(self, key):
        return get_setting_bool('{}_{}'.format(self.rule, key))

    def _si(self, key, default=0):
        return get_setting_int('{}_{}'.format(self.rule, key), default)

    def _entities(self):
        _, _, rule1_ent, rule2_ent = _load_config()
        if self.rule == 'rule1' and rule1_ent:
            return rule1_ent
        if self.rule == 'rule2' and rule2_ent:
            return rule2_ent
        return _entity_list(self._s('entities'))

    def _save_states(self):
        client = _make_client()
        if not client:
            return
        self.saved = {}
        for eid in self._entities():
            try:
                st = client.get_light_state(eid)
                self.saved[eid] = {
                    'state':      st.get('state', 'off'),
                    'brightness': st.get('attributes', {}).get('brightness', 255),
                }
            except Exception:
                self.saved[eid] = {'state': 'off', 'brightness': 255}

    def _restore_states(self):
        client = _make_client()
        if not client or not self.saved:
            return
        for eid, saved in self.saved.items():
            try:
                if saved['state'] == 'on':
                    client.turn_on(eid, brightness=saved['brightness'])
                else:
                    client.turn_off(eid)
            except Exception:
                pass
        notify('{} - lumieres restaurees'.format(self.rule))
        self.saved = {}

    def _do_turn_off(self):
        client = _make_client()
        if not client:
            return
        for eid in self._entities():
            try:
                client.turn_off(eid)
            except Exception:
                pass
        notify('{} - lumieres eteintes'.format(self.rule))

    def _do_pause_on(self):
        if not self._sb('pause_enabled'):
            return
        pct        = self._si('pause_brightness', 50)
        brightness = int(pct / 100.0 * 255)
        client     = _make_client()
        if not client:
            return
        for eid in self._entities():
            try:
                client.turn_on(eid, brightness=brightness)
            except Exception:
                pass
        notify('{} - pause {}%'.format(self.rule, pct))

    def _do_resume_off(self):
        client = _make_client()
        if not client:
            return
        for eid in self._entities():
            try:
                client.turn_off(eid)
            except Exception:
                pass
        notify('{} - reprise, lumieres eteintes'.format(self.rule))

    def _do_pre_end_on(self):
        client = _make_client()
        if not client:
            return
        for eid in self._entities():
            try:
                client.turn_on(eid)
            except Exception:
                pass
        mins = self._si('end_before_min', 5)
        notify('{} - allumage {} min avant la fin'.format(self.rule, mins))
        self.armed = False

    def _arm_end_timer(self):
        if not self._sb('end_enabled'):
            return
        total = 0
        for _ in range(20):
            total = self.player.getTotalTime()
            if total > 0:
                break
            time.sleep(0.5)
        if total <= 0:
            return

        end_before = self._si('end_before_min', 5) * 60
        elapsed    = self.player.getTime()
        delay      = max(0, (total - elapsed) - end_before)

        if delay < 5:
            self._do_pre_end_on()
            return

        self.armed = True
        self.timers.schedule('{}_end'.format(self.rule), delay, self._do_pre_end_on)
        xbmc.log('HALights: {} timer fin arme dans {:.0f}s'.format(self.rule, delay), xbmc.LOGINFO)

    def on_start(self):
        if not self._sb('enabled') or not self._entities():
            return
        self._save_states()
        self.timers.cancel('{}_end'.format(self.rule))
        self.armed = False

        delay = self._si('start_delay_sec', 0)
        if delay > 0:
            self.timers.schedule('{}_off'.format(self.rule), delay, self._do_turn_off)
            notify('{} - extinction dans {}s'.format(self.rule, delay))
        else:
            self._do_turn_off()

        t = threading.Thread(target=self._arm_end_timer)
        t.daemon = True
        t.start()

    def on_pause(self):
        if not self._sb('enabled'):
            return
        self.timers.cancel('{}_end'.format(self.rule))
        self._do_pause_on()

    def on_resume(self):
        if not self._sb('enabled'):
            return
        self._do_resume_off()
        if not self.armed:
            t = threading.Thread(target=self._arm_end_timer)
            t.daemon = True
            t.start()

    def on_stop(self):
        self.timers.cancel('{}_off'.format(self.rule))
        self.timers.cancel('{}_end'.format(self.rule))
        self.armed = False
        if self._sb('enabled'):
            self._restore_states()


class LightPlayerMonitor(xbmc.Player):

    def __init__(self):
        super(LightPlayerMonitor, self).__init__()
        self._timers  = TimerManager()
        self._playing = False
        self._rule1   = RuleHandler('rule1', self._timers, self)
        self._rule2   = RuleHandler('rule2', self._timers, self)

    def onPlayBackStarted(self):
        if not self.isPlayingVideo():
            return
        self._playing = True
        self._rule1.on_start()
        self._rule2.on_start()

    def onPlayBackPaused(self):
        if not self._playing:
            return
        self._rule1.on_pause()
        self._rule2.on_pause()

    def onPlayBackResumed(self):
        if not self._playing:
            return
        self._rule1.on_resume()
        self._rule2.on_resume()

    def onPlayBackStopped(self):
        self._on_stop()

    def onPlayBackEnded(self):
        self._on_stop()

    def _on_stop(self):
        if not self._playing:
            return
        self._playing = False
        self._rule1.on_stop()
        self._rule2.on_stop()