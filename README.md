# 💡 Home Assistant Lights — Addon Kodi

Contrôle vos lumières Home Assistant directement depuis l'interface Kodi.

---

## 📦 Installation

### 1. Préparer le dossier
Copier le dossier `plugin.script.ha_lights` dans le répertoire des addons Kodi :

| Système       | Chemin                                               |
|---------------|------------------------------------------------------|
| Linux         | `~/.kodi/addons/`                                    |
| Windows       | `C:\Users\<user>\AppData\Roaming\Kodi\addons\`       |
| macOS         | `~/Library/Application Support/Kodi/addons/`        |
| Raspberry Pi  | `/home/osmc/.kodi/addons/` ou `/home/pi/.kodi/addons/` |

### 2. Activer l'addon
1. Ouvrir Kodi → **Paramètres** → **Addons**
2. Aller dans **Mes addons** → **Scripts**
3. Trouver **Home Assistant Lights** et l'activer

### 3. Créer un token Home Assistant
1. Ouvrir Home Assistant → Profil (icône en bas à gauche)
2. Descendre jusqu'à **Jetons d'accès longue durée**
3. Cliquer **Créer un jeton**, lui donner un nom (ex: "Kodi")
4. Copier le token généré (**il ne sera affiché qu'une seule fois**)

### 4. Configurer l'addon
1. Faire un clic droit sur l'addon → **Paramètres**
2. Renseigner :
   - **URL Home Assistant** : ex. `http://192.168.1.10:8123`
   - **Token d'accès** : le token copié à l'étape précédente
3. Tester via le menu **Tester la connexion**

---

## 🎮 Utilisation

Lancer un film et le plugin fera le reste automatiquement.

---

## ⚙️ Options

| Option                       | Description                                  |
|------------------------------|----------------------------------------------|
| Demander confirmation        | Affiche une popup avant chaque action        |
| Afficher les notifications   | Toast en bas d'écran après chaque action     |

---

## 🔧 Compatibilité

- Kodi 18 (Leia) et supérieur
- Home Assistant 2021.x et supérieur
- Python 2 et Python 3
