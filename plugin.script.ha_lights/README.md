# Home Assistant Lights — Addon Kodi

Addon Kodi permettant de contrôler les lumières Home Assistant directement depuis l'interface Kodi, avec un système de pilotage automatique basé sur la lecture vidéo.

---


### Pilotage automatique — 2 règles indépendantes

Le plugin propose deux règles de pilotage entièrement configurables et indépendantes, permettant par exemple de gérer deux pièces ou deux groupes de lumières différemment.

Chaque règle dispose de :
- Activation / désactivation individuelle
- Groupe de lumières dédié défini dans le fichier de configuration
- Délai avant extinction paramétrable au lancement d'une vidéo (en secondes)
- Remontée automatique de la luminosité à un niveau configurable lors d'une pause
- Allumage automatique X minutes avant la fin du film (durée paramétrable)
- Restauration automatique de l'état d'origine des lumières à l'arrêt ou la fin de la vidéo

---

## Installation

### Créer un token Home Assistant

1. Ouvrir Home Assistant
2. Cliquer sur votre profil (icône en bas à gauche)
3. Descendre jusqu'à **Jetons d'accès longue durée**
4. Cliquer **Créer un jeton** et lui donner un nom (ex: "Kodi")
5. Copier le token généré — il ne sera affiché qu'une seule fois

## Configuration

Toute la configuration se fait dans un seul fichier : `resources/lib/config.py`

```python
# URL de votre serveur Home Assistant
HA_URL   = "http://192.168.1.10:8123"

# Token d'accès longue durée Home Assistant
# Profil HA → Jetons d'accès longue durée → Créer un jeton
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Lumières pilotées par la Regle 1 (entity_id Home Assistant)
RULE1_ENTITIES = ["light.salon", "light.cuisine"]

# Lumières pilotées par la Regle 2
RULE2_ENTITIES = ["light.chambre", "light.couloir"]
```

### 1. Copier le dossier de l'addon

Télécharger le dossier `plugin.script.ha_lights` et le copier dans le répertoire des addons Kodi :

| Système | Chemin |
|---|---|
| Windows | `C:\Users\<user>\AppData\Roaming\Kodi\addons\` |
| Linux | `~/.kodi/addons/` |
| macOS | `~/Library/Application Support/Kodi/addons/` |
| Raspberry Pi / OSMC | `/home/osmc/.kodi/addons/` |

### 2. Activer l'addon

Dans Kodi : **Paramètres → Addons → Mes addons → Scripts → Home Assistant Lights → Activer**

### 3. Redémarrer Kodi

---

Les paramètres de comportement (délais, luminosité en pause, minuterie fin de film) se configurent directement depuis l'interface Kodi dans le menu de chaque règle.

---

## Utilisation

Lancer l'addon depuis **Programmes → Scripts → Home Assistant Lights**

### Menu principal

| Entrée | Description |
|---|---|
| Regle 1 | Configuration et activation de la règle 1 |
| Regle 2 | Configuration et activation de la règle 2 |
| Parametres | Options générales de l'addon |

### Menu d'une règle

| Entrée | Description |
|---|---|
| Activer cette regle | Active ou désactive le pilotage automatique |
| Lumieres pilotees | Affiche les lumières définies dans config.py |
| Delai avant extinction | Nombre de secondes avant d'éteindre au lancement |
| Luminosite en pause | Active la remontée de luminosité lors d'une pause |
| Niveau luminosite pause | Pourcentage de luminosité en pause |
| Allumer avant la fin | Active l'allumage automatique avant la fin du film |
| Minutes avant la fin | Nombre de minutes avant la fin pour allumer |

---

## Structure des fichiers

```
plugin.script.ha_lights/
  addon.xml                    # Déclaration de l'addon
  default.py                   # Interface et menus Kodi
  service.py                   # Service d'arrière-plan (détection lecture)
  resources/
    settings.xml               # Paramètres configurables via Kodi
    lib/
      config.py                # Fichier de configuration principal
      ha_client.py             # Client API Home Assistant
      player_monitor.py        # Détection des événements de lecture
```

---

## Compatibilité

- Kodi 19 (Matrix) et supérieur
- Python 3
- Home Assistant 2021.x et supérieur
- Windows, Linux, macOS, Raspberry Pi / OSMC

---


## Licence

MIT License — libre d'utilisation, modification et distribution.
