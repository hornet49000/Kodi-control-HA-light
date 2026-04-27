"""
Client API pour Home Assistant
"""
import json

try:
    # Python 3 (Kodi 19+)
    import urllib.request as urllib2
    from urllib.error import URLError, HTTPError
except ImportError:
    # Python 2 (Kodi 18)
    import urllib2
    from urllib2 import URLError, HTTPError


class HomeAssistantClient:
    def __init__(self, url, token):
        self.url = url.rstrip('/')
        self.token = token
        self.headers = {
            'Authorization': 'Bearer {}'.format(token),
            'Content-Type': 'application/json',
        }

    def _request(self, method, endpoint, data=None):
        url = '{}/api/{}'.format(self.url, endpoint.lstrip('/'))
        req_data = json.dumps(data).encode('utf-8') if data else None
        req = urllib2.Request(url, req_data, self.headers)
        req.get_method = lambda: method
        try:
            response = urllib2.urlopen(req, timeout=10)
            return json.loads(response.read().decode('utf-8'))
        except HTTPError as e:
            raise Exception('Erreur HTTP {}: {}'.format(e.code, e.reason))
        except URLError as e:
            raise Exception('Impossible de joindre Home Assistant: {}'.format(e.reason))
        except Exception as e:
            raise Exception('Erreur: {}'.format(str(e)))

    def test_connection(self):
        """Teste la connexion à Home Assistant"""
        try:
            result = self._request('GET', '/')
            return True, result.get('message', 'OK')
        except Exception as e:
            return False, str(e)

    def get_lights(self):
        """Récupère toutes les entités lumière"""
        states = self._request('GET', 'states')
        lights = []
        for state in states:
            entity_id = state.get('entity_id', '')
            if entity_id.startswith('light.'):
                lights.append({
                    'entity_id': entity_id,
                    'name': state.get('attributes', {}).get('friendly_name', entity_id),
                    'state': state.get('state', 'unknown'),
                    'brightness': state.get('attributes', {}).get('brightness'),
                    'color_temp': state.get('attributes', {}).get('color_temp'),
                    'rgb_color': state.get('attributes', {}).get('rgb_color'),
                    'supported_features': state.get('attributes', {}).get('supported_features', 0),
                })
        lights.sort(key=lambda x: x['name'])
        return lights

    def get_light_state(self, entity_id):
        """Récupère l'état d'une lumière spécifique"""
        return self._request('GET', 'states/{}'.format(entity_id))

    def turn_on(self, entity_id, brightness=None, color_temp=None, rgb_color=None):
        """Allume une lumière"""
        data = {'entity_id': entity_id}
        if brightness is not None:
            data['brightness'] = brightness
        if color_temp is not None:
            data['color_temp'] = color_temp
        if rgb_color is not None:
            data['rgb_color'] = rgb_color
        return self._request('POST', 'services/light/turn_on', data)

    def turn_off(self, entity_id):
        """Éteint une lumière"""
        return self._request('POST', 'services/light/turn_off', {'entity_id': entity_id})

    def toggle(self, entity_id):
        """Bascule une lumière (allume/éteint)"""
        return self._request('POST', 'services/light/toggle', {'entity_id': entity_id})

    def turn_on_all(self):
        """Allume toutes les lumières"""
        return self._request('POST', 'services/light/turn_on', {'entity_id': 'all'})

    def turn_off_all(self):
        """Éteint toutes les lumières"""
        return self._request('POST', 'services/light/turn_off', {'entity_id': 'all'})

    def get_groups(self):
        """Récupère les groupes de lumières"""
        states = self._request('GET', 'states')
        groups = []
        for state in states:
            entity_id = state.get('entity_id', '')
            if entity_id.startswith('group.') or entity_id.startswith('light.'):
                attrs = state.get('attributes', {})
                if 'entity_id' in attrs:  # C'est un groupe
                    groups.append({
                        'entity_id': entity_id,
                        'name': attrs.get('friendly_name', entity_id),
                        'state': state.get('state', 'unknown'),
                        'members': attrs.get('entity_id', []),
                    })
        return groups
