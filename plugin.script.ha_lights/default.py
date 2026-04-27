"""
Plugin Kodi - Home Assistant Lights Controller v2.2
"""
import sys
import os

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')
sys.path.insert(0, os.path.join(ADDON_PATH, 'resources', 'lib'))

from ha_client import HomeAssistantClient
from config import HA_URL, HA_TOKEN, RULE1_ENTITIES, RULE2_ENTITIES

try:
    from urllib.parse import parse_qs, urlencode
except ImportError:
    from urlparse import parse_qs
    from urllib import urlencode

HANDLE   = int(sys.argv[1]) if len(sys.argv) > 1 else -1
BASE_URL = sys.argv[0] if sys.argv else ''


# --- Helpers ------------------------------------------------------------------

def get_client():
    url   = HA_URL   if HA_URL   else ADDON.getSetting('ha_url')
    token = HA_TOKEN if HA_TOKEN else ADDON.getSetting('ha_token')
    if not url or not token:
        xbmcgui.Dialog().ok('Home Assistant Lights',
            'URL et token non configures.\nModifiez le fichier config.py')
        return None
    return HomeAssistantClient(url, token)


def notify(message, icon=xbmcgui.NOTIFICATION_INFO):
    if ADDON.getSetting('show_notifications') == 'true':
        xbmcgui.Dialog().notification('HA Lights', message, icon, 3000)


def confirm(message):
    if ADDON.getSetting('confirm_action') == 'true':
        return xbmcgui.Dialog().yesno('Confirmation', message)
    return True


def build_url(params):
    return '{}?{}'.format(BASE_URL, urlencode(params))


def get_params():
    if len(sys.argv) > 2 and sys.argv[2]:
        return {k: v[0] for k, v in parse_qs(sys.argv[2].lstrip('?')).items()}
    return {}


def state_label(state):
    return 'Allumee' if state == 'on' else 'Eteinte'


def bool_label(value):
    return 'Actif' if value == 'true' else 'Inactif'


# --- Menu principal -----------------------------------------------------------

def show_main_menu():
    rule1_on   = ADDON.getSetting('rule1_enabled')
    rule2_on   = ADDON.getSetting('rule2_enabled')
    rule1_name = ADDON.getSetting('rule1_name') or 'Regle 1'
    rule2_name = ADDON.getSetting('rule2_name') or 'Regle 2'

    items = [
        ('Toutes les lumieres',                                               {'action': 'list_lights'},              True),
        ('Tout allumer',                                                      {'action': 'all_on'},                   False),
        ('Tout eteindre',                                                     {'action': 'all_off'},                  False),
        ('{} [{}]'.format(rule1_name, 'ON' if rule1_on == 'true' else 'OFF'),{'action': 'rule_menu', 'rule': 'rule1'}, True),
        ('{} [{}]'.format(rule2_name, 'ON' if rule2_on == 'true' else 'OFF'),{'action': 'rule_menu', 'rule': 'rule2'}, True),
        ('Parametres',                                                        {'action': 'settings'},                 False),
    ]
    for label, params, is_folder in items:
        li = xbmcgui.ListItem(label=label)
        li.setProperty('IsPlayable', 'false')
        xbmcplugin.addDirectoryItem(HANDLE, build_url(params), li, is_folder)
    xbmcplugin.endOfDirectory(HANDLE)


# --- Menu regle ---------------------------------------------------------------

def show_rule_menu(rule):
    name     = ADDON.getSetting('{}_name'.format(rule))             or rule
    enabled  = ADDON.getSetting('{}_enabled'.format(rule))
    pause_on = ADDON.getSetting('{}_pause_enabled'.format(rule))
    pause_br = ADDON.getSetting('{}_pause_brightness'.format(rule)) or '50'
    delay    = ADDON.getSetting('{}_start_delay_sec'.format(rule))  or '0'
    end_on   = ADDON.getSetting('{}_end_enabled'.format(rule))
    end_min  = ADDON.getSetting('{}_end_before_min'.format(rule))   or '5'

    # Lumieres : depuis config.py ou depuis les parametres
    if rule == 'rule1':
        entities = RULE1_ENTITIES
    else:
        entities = RULE2_ENTITIES
    nb_ent = '{} lumiere(s) (config.py)'.format(len(entities)) if entities else 'aucune (config.py)'

    items = [
        ('Activer cette regle        [{}]'.format(bool_label(enabled)),                  {'action': 'rule_toggle',      'rule': rule}, False),
        ('Lumieres pilotees          [{}]'.format(nb_ent),                               {'action': 'rule_info_lights', 'rule': rule}, False),
        ('Delai avant extinction     [{}s]'.format(delay),                               {'action': 'rule_set_delay',   'rule': rule}, False),
        ('Luminosite en pause        [{} - {}%]'.format(bool_label(pause_on), pause_br), {'action': 'rule_pause_toggle','rule': rule}, False),
        ('Niveau luminosite pause    [{}%]'.format(pause_br),                            {'action': 'rule_pause_level', 'rule': rule}, False),
        ('Allumer avant la fin       [{} - {}min]'.format(bool_label(end_on), end_min),  {'action': 'rule_end_toggle',  'rule': rule}, False),
        ('Minutes avant la fin       [{}min]'.format(end_min),                           {'action': 'rule_end_min',     'rule': rule}, False),
        ('Renommer cette regle       [{}]'.format(name),                                 {'action': 'rule_rename',      'rule': rule}, False),
    ]
    for label, params, is_folder in items:
        li = xbmcgui.ListItem(label=label)
        li.setProperty('IsPlayable', 'false')
        xbmcplugin.addDirectoryItem(HANDLE, build_url(params), li, is_folder)
    xbmcplugin.endOfDirectory(HANDLE)


def rule_toggle(rule):
    current = ADDON.getSetting('{}_enabled'.format(rule))
    new_val = 'false' if current == 'true' else 'true'
    ADDON.setSetting('{}_enabled'.format(rule), new_val)
    notify('Regle {}'.format('activee' if new_val == 'true' else 'desactivee'))
    xbmc.executebuiltin('Container.Refresh')


def rule_rename(rule):
    current = ADDON.getSetting('{}_name'.format(rule)) or rule
    new_name = xbmcgui.Dialog().input('Nom de la regle', current,
        type=xbmcgui.INPUT_ALPHANUM)
    if new_name:
        ADDON.setSetting('{}_name'.format(rule), new_name.strip())
    xbmc.executebuiltin('Container.Refresh')


def rule_set_delay(rule):
    current = ADDON.getSetting('{}_start_delay_sec'.format(rule)) or '0'
    val = xbmcgui.Dialog().numeric(0, 'Delai avant extinction (secondes)', current)
    if val is not None:
        ADDON.setSetting('{}_start_delay_sec'.format(rule), str(int(val)))
        notify('Delai regle a {}s'.format(int(val)))
    xbmc.executebuiltin('Container.Refresh')


def rule_info_lights(rule):
    if rule == 'rule1':
        entities = RULE1_ENTITIES
    else:
        entities = RULE2_ENTITIES
    if entities:
        xbmcgui.Dialog().ok('Lumieres de {}'.format(rule),
            'Definies dans config.py :\n\n{}'.format('\n'.join(entities)))
    else:
        xbmcgui.Dialog().ok('Lumieres de {}'.format(rule),
            'Aucune lumiere definie.\nAjoutez les entity_id dans config.py')


def rule_pause_toggle(rule):
    current = ADDON.getSetting('{}_pause_enabled'.format(rule))
    new_val = 'false' if current == 'true' else 'true'
    ADDON.setSetting('{}_pause_enabled'.format(rule), new_val)
    notify('Luminosite pause {}'.format('activee' if new_val == 'true' else 'desactivee'))
    xbmc.executebuiltin('Container.Refresh')


def rule_pause_level(rule):
    current = ADDON.getSetting('{}_pause_brightness'.format(rule)) or '50'
    val = xbmcgui.Dialog().numeric(0, 'Luminosite en pause (0-100%)', current)
    if val is not None:
        ADDON.setSetting('{}_pause_brightness'.format(rule), str(max(0, min(100, int(val)))))
        notify('Luminosite pause : {}%'.format(int(val)))
    xbmc.executebuiltin('Container.Refresh')


def rule_end_toggle(rule):
    current = ADDON.getSetting('{}_end_enabled'.format(rule))
    new_val = 'false' if current == 'true' else 'true'
    ADDON.setSetting('{}_end_enabled'.format(rule), new_val)
    notify('Allumage pre-fin {}'.format('active' if new_val == 'true' else 'desactive'))
    xbmc.executebuiltin('Container.Refresh')


def rule_end_min(rule):
    current = ADDON.getSetting('{}_end_before_min'.format(rule)) or '5'
    val = xbmcgui.Dialog().numeric(0, 'Minutes avant la fin du film', current)
    if val is not None:
        ADDON.setSetting('{}_end_before_min'.format(rule), str(max(1, int(val))))
        notify('Allumage {} min avant la fin'.format(int(val)))
    xbmc.executebuiltin('Container.Refresh')


# --- Liste lumieres -----------------------------------------------------------

def show_lights_list():
    client = get_client()
    if not client:
        return
    try:
        lights = client.get_lights()
    except Exception as e:
        xbmcgui.Dialog().ok('Erreur', str(e))
        return
    if not lights:
        xbmcgui.Dialog().ok('HA Lights', 'Aucune lumiere trouvee.')
        return

    for light in lights:
        eid        = light['entity_id']
        name       = light['name']
        state      = light['state']
        brightness = light.get('brightness')
        br_pct     = int(brightness / 255 * 100) if brightness else None

        label = '{} - {}'.format(name, state_label(state))
        if br_pct and state == 'on':
            label += ' ({}%)'.format(br_pct)

        li = xbmcgui.ListItem(label=label)
        li.setProperty('IsPlayable', 'false')
        li.setInfo('video', {'title': label, 'plot': 'Entite : {}'.format(eid)})
        li.addContextMenuItems([
            ('Allumer',            'RunPlugin({})'.format(build_url({'action': 'turn_on',        'entity_id': eid}))),
            ('Eteindre',           'RunPlugin({})'.format(build_url({'action': 'turn_off',       'entity_id': eid}))),
            ('Basculer',           'RunPlugin({})'.format(build_url({'action': 'toggle',         'entity_id': eid}))),
            ('Reglage luminosite', 'RunPlugin({})'.format(build_url({'action': 'set_brightness', 'entity_id': eid}))),
        ])
        xbmcplugin.addDirectoryItem(HANDLE,
            build_url({'action': 'light_menu', 'entity_id': eid, 'name': name, 'state': state}),
            li, True)
    xbmcplugin.endOfDirectory(HANDLE)


def show_light_menu(entity_id, name, state):
    actions = [
        ('Allumer',                                                 {'action': 'turn_on',        'entity_id': entity_id}),
        ('Eteindre',                                                {'action': 'turn_off',       'entity_id': entity_id}),
        ('Basculer (actuellement : {})'.format(state_label(state)), {'action': 'toggle',         'entity_id': entity_id}),
        ('Regler la luminosite',                                    {'action': 'set_brightness', 'entity_id': entity_id}),
    ]
    for label, params in actions:
        li = xbmcgui.ListItem(label=label)
        li.setProperty('IsPlayable', 'false')
        xbmcplugin.addDirectoryItem(HANDLE, build_url(params), li, False)
    xbmcplugin.endOfDirectory(HANDLE)


def action_turn_on(entity_id):
    client = get_client()
    if not client or not confirm('Allumer {} ?'.format(entity_id)):
        return
    try:
        client.turn_on(entity_id)
        notify('{} allumee'.format(entity_id))
        xbmc.executebuiltin('Container.Refresh')
    except Exception as e:
        notify('Erreur : {}'.format(e), xbmcgui.NOTIFICATION_ERROR)


def action_turn_off(entity_id):
    client = get_client()
    if not client or not confirm('Eteindre {} ?'.format(entity_id)):
        return
    try:
        client.turn_off(entity_id)
        notify('{} eteinte'.format(entity_id))
        xbmc.executebuiltin('Container.Refresh')
    except Exception as e:
        notify('Erreur : {}'.format(e), xbmcgui.NOTIFICATION_ERROR)


def action_toggle(entity_id):
    client = get_client()
    if not client:
        return
    try:
        client.toggle(entity_id)
        notify('{} basculee'.format(entity_id))
        xbmc.executebuiltin('Container.Refresh')
    except Exception as e:
        notify('Erreur : {}'.format(e), xbmcgui.NOTIFICATION_ERROR)


def action_set_brightness(entity_id):
    client = get_client()
    if not client:
        return
    try:
        st = client.get_light_state(entity_id)
        current_pct = int(st.get('attributes', {}).get('brightness', 128) / 255 * 100)
    except Exception:
        current_pct = 50
    val = xbmcgui.Dialog().numeric(0, 'Luminosite (0-100%)', str(current_pct))
    if val is None:
        return
    try:
        pct = max(0, min(100, int(val)))
        client.turn_on(entity_id, brightness=int(pct / 100 * 255))
        notify('Luminosite {}% pour {}'.format(pct, entity_id))
    except Exception as e:
        notify('Erreur : {}'.format(e), xbmcgui.NOTIFICATION_ERROR)


def action_all_on():
    client = get_client()
    if not client or not confirm('Allumer toutes les lumieres ?'):
        return
    try:
        client.turn_on_all()
        notify('Toutes les lumieres allumees')
    except Exception as e:
        notify('Erreur : {}'.format(e), xbmcgui.NOTIFICATION_ERROR)


def action_all_off():
    client = get_client()
    if not client or not confirm('Eteindre toutes les lumieres ?'):
        return
    try:
        client.turn_off_all()
        notify('Toutes les lumieres eteintes')
    except Exception as e:
        notify('Erreur : {}'.format(e), xbmcgui.NOTIFICATION_ERROR)


# --- Router ------------------------------------------------------------------

def router():
    params = get_params()
    action = params.get('action', '')
    rule   = params.get('rule', '')

    if not action:                      show_main_menu()
    elif action == 'list_lights':       show_lights_list()
    elif action == 'light_menu':
        show_light_menu(params.get('entity_id',''), params.get('name',''), params.get('state',''))
    elif action == 'rule_menu':         show_rule_menu(rule)
    elif action == 'rule_toggle':       rule_toggle(rule)
    elif action == 'rule_rename':       rule_rename(rule)
    elif action == 'rule_set_delay':    rule_set_delay(rule)
    elif action == 'rule_info_lights':  rule_info_lights(rule)
    elif action == 'rule_pause_toggle': rule_pause_toggle(rule)
    elif action == 'rule_pause_level':  rule_pause_level(rule)
    elif action == 'rule_end_toggle':   rule_end_toggle(rule)
    elif action == 'rule_end_min':      rule_end_min(rule)
    elif action == 'turn_on':          action_turn_on(params.get('entity_id',''))
    elif action == 'turn_off':         action_turn_off(params.get('entity_id',''))
    elif action == 'toggle':           action_toggle(params.get('entity_id',''))
    elif action == 'set_brightness':   action_set_brightness(params.get('entity_id',''))
    elif action == 'all_on':           action_all_on()
    elif action == 'all_off':          action_all_off()
    elif action == 'settings':         ADDON.openSettings()
    else:
        xbmcgui.Dialog().ok('Erreur', 'Action inconnue : {}'.format(action))


if __name__ == '__main__':
    router()