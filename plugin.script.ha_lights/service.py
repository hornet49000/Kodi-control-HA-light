"""
Service d'arrière-plan — démarre avec Kodi et écoute les événements de lecture.
Ce fichier est lancé automatiquement grâce à l'extension xbmc.service dans addon.xml.
"""
import sys
import os
import xbmc
import xbmcaddon

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')
sys.path.insert(0, os.path.join(ADDON_PATH, 'resources', 'lib'))

from player_monitor import LightPlayerMonitor

if __name__ == '__main__':
    xbmc.log('HALights Service: démarrage', xbmc.LOGINFO)
    monitor = LightPlayerMonitor()

    # Boucle principale : reste vivant tant que Kodi tourne
    while not xbmc.Monitor().abortRequested():
        xbmc.Monitor().waitForAbort(10)

    xbmc.log('HALights Service: arrêt', xbmc.LOGINFO)
