<div align="center">

# 🌿 Leaffliction

**Analyse et classification de l'état de santé des feuilles par traitement d'images**

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![uv](https://img.shields.io/badge/uv-package%20manager-DE5FE9?logo=astral&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-2.4+-013243?logo=numpy&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-3.0+-150458?logo=pandas&logoColor=white)

---

</div>

## 📖 À propos

**Leaffliction** est un programme conçu pour analyser et classifier l'état de santé des feuilles de différentes cultures agricoles. En se basant sur l'analyse d'images, il permet de déterminer si une plante est **saine** ou si elle est atteinte d'une **maladie spécifique**.

Le projet se concentre actuellement sur deux cultures majeures :

| Culture | Maladies détectées |
|---|---|
| 🍏 **Pommier** (Apple) | Black Rot, Rouille (Rust), Tavelure (Scab) |
| 🍇 **Vigne** (Grape) | Esca, Black Rot, Taches foliaires (Leaf Spot) |

### 🎯 Pourquoi ce projet ?

La détection précoce des maladies des plantes est un enjeu crucial en agriculture. Un diagnostic tardif peut entraîner :
- 📉 Des **pertes de récolte** significatives
- 💊 Une **surutilisation de pesticides** néfaste pour l'environnement
- 💰 Des **coûts supplémentaires** pour les agriculteurs

Leaffliction vise à fournir un outil rapide et automatisé pour aider à identifier ces maladies à partir d'une simple photo de feuille.

---

## 🛠️ Installation

Ce projet utilise [uv](https://github.com/astral-sh/uv), un gestionnaire de paquets et de projets Python ultra-rapide écrit en Rust.

### Prérequis

- Python **3.12** ou supérieur
- `curl` (pour installer `uv`)

### Étapes

1. **Installer `uv`** (si ce n'est pas déjà fait) :
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Cloner le dépôt et se placer dans le dossier** :
   ```bash
   git clone <votre-repo-url>
   cd Leaffliction
   ```

3. **Synchroniser l'environnement et installer les dépendances** :
   ```bash
   uv sync
   ```

4. **Lancer le programme** :
   ```bash
   uv run python main.py
   ```

---

## 📁 Structure du projet

```
Leaffliction/
├── main.py              # Point d'entrée du programme
├── pyproject.toml       # Configuration du projet et dépendances
├── README.md
└── leaves/
    └── images/          # Jeu de données d'images de feuilles
        ├── Apple_healthy/
        ├── Apple_Black_rot/
        ├── Apple_rust/
        ├── Apple_scab/
        ├── Grape_healthy/
        ├── Grape_Black_rot/
        ├── Grape_Esca/
        └── Grape_spot/
```

---

## 🔁 Pipeline

`train` et `predict` appliquent **exactement** le même prétraitement, défini une seule fois dans [`code/preprocess.py`](code/preprocess.py). Aucun des deux programmes ne redimensionne ni ne normalise les images lui-même.

| Étape | Choix | Détail |
|---|---|---|
| Entrée du modèle | Image **originale** | Pas de masque PlantCV : le CNN apprend à ignorer le fond, et `predict` reste rapide et robuste |
| Lecture | `load_image(path)` | OpenCV lit en BGR, l'image est convertie en **RGB** immédiatement |
| Taille | `IMG_SIZE = (128, 128)` | `cv2.resize` avec `INTER_AREA` (les images augmentées n'ont pas toutes la même taille) |
| Normalisation | pixels `/ 255` → `float32` dans `[0, 1]` | Faite dans `preprocess()` uniquement, pas de couche `Rescaling` dans le modèle |
| Classes | `sorted()` des dossiers du dataset | L'indice de sortie du modèle correspond à la position dans cette liste |

La liste des classes est enregistrée dans `classes.json` à côté du modèle (`save_class_names`). `predict` la relit avec `load_class_names` et ne dépend donc pas de la présence du dataset.

Les scripts de la partie 3 ([`Augmentation.py`](code/Augmentation.py), [`Transformation.py`](code/Transformation.py)) sont importables : leur dossier de sortie est passé en paramètre, et aucune fenêtre ne s'ouvre à l'import.

---

## 🔬 Galerie des maladies

Voici un aperçu visuel des différentes afflictions que le modèle peut rencontrer et classifier, directement issues de notre jeu de données.

### 🍏 Pommier (Apple)

<table>
  <tr>
    <td align="center">
      <img src="leaves/images/Apple_healthy/image (1).JPG" width="200"><br>
      <b>🍃 Saine</b><br>
      <sub>Feuille en parfaite santé,<br>couleur uniforme et vive.</sub>
    </td>
    <td align="center">
      <img src="leaves/images/Apple_Black_rot/image (1).JPG" width="200"><br>
      <b>🍂 Black Rot</b><br>
      <sub>Infection fongique causant des<br>lésions brunes concentriques.</sub>
    </td>
    <td align="center">
      <img src="leaves/images/Apple_rust/image (1).JPG" width="200"><br>
      <b>🍁 Rouille (Rust)</b><br>
      <sub>Pustules orangées sur la face<br>inférieure des feuilles.</sub>
    </td>
    <td align="center">
      <img src="leaves/images/Apple_scab/image (1).JPG" width="200"><br>
      <b>🥀 Tavelure (Scab)</b><br>
      <sub>Taches sombres et veloutées<br>causées par <i>Venturia inaequalis</i>.</sub>
    </td>
  </tr>
</table>

### 🍇 Vigne (Grape)

<table>
  <tr>
    <td align="center">
      <img src="leaves/images/Grape_healthy/image (1).JPG" width="200"><br>
      <b>🍇 Saine</b><br>
      <sub>Feuille vigoureuse sans<br>aucun signe de maladie.</sub>
    </td>
    <td align="center">
      <img src="leaves/images/Grape_Esca/image (1).JPG" width="200"><br>
      <b>🥀 Esca</b><br>
      <sub>Maladie du bois provoquant<br>un dessèchement « en tigrure ».</sub>
    </td>
    <td align="center">
      <img src="leaves/images/Grape_Black_rot/image (1).JPG" width="200"><br>
      <b>🍂 Black Rot</b><br>
      <sub>Taches brunes cerclées de noir<br>sur feuilles et baies.</sub>
    </td>
    <td align="center">
      <img src="leaves/images/Grape_spot/image (1).JPG" width="200"><br>
      <b>🦠 Leaf Spot</b><br>
      <sub>Taches foliaires réduisant la<br>capacité de photosynthèse.</sub>
    </td>
  </tr>
</table>

---

## 📦 Dépendances

| Paquet | Version | Utilisation |
|---|---|---|
| [NumPy](https://numpy.org/) | ≥ 2.4.3 | Calcul numérique et manipulation de tableaux |
| [Pandas](https://pandas.pydata.org/) | ≥ 3.0.1 | Analyse et structuration des données |

---

<div align="center">
  <sub>Projet réalisé dans le cadre du cursus <b>42</b> 🎓</sub>
</div>