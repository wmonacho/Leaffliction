#!/usr/bin/env python3
import os
import sys
import argparse
from collections import Counter
from PIL import Image
from preprocess import IMG_SIZE

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MIN_CLASSES = 2


def parse_args():
    parser = argparse.ArgumentParser(
        description="Entraîne un modèle de classification "
                    "d'images de feuilles.",
        epilog="Exemple : ./train.py ./leaves/images/")

    parser.add_argument(
        "source",
        help="dossier contenant un sous-dossier d'images par classe")
    parser.add_argument(
        "--epochs", type=int, default=10,
        help="nombre de passes sur le dataset (défaut : %(default)s)")
    parser.add_argument(
        "--img-size", type=int, default=IMG_SIZE[0],
        help="côté des images en pixels (défaut : %(default)s)")
    parser.add_argument(
        "--output", default="leaffliction.zip",
        help="nom du zip produit (défaut : %(default)s)")
    parser.add_argument(
        "--seed", type=int, default=42,
        help="graine aléatoire (défaut : %(default)s)")

    args = parser.parse_args()

    if args.epochs < 1:
        parser.error("--epochs doit être au moins 1.")
    if args.img_size < 1:
        parser.error("--img-size doit être au moins 1.")
    if args.seed < 0:
        parser.error("--seed doit être un nombre positif.")

    return args


def warn(message):
    print(f"Warning : {message}", file=sys.stderr)


def is_readable_image(path):
    """Renvoie True si le fichier est une image lisible, False sinon."""
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception as e:
        warn(f"image illisible ignorée : {path} ({e})")
        return False


def is_image_file(filename):
    return os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS


def scan_class_dir(class_dir):
    """Renvoie la liste des chemins d'images valides d'un dossier de classe."""
    paths = []
    for root, _, files in os.walk(class_dir):
        for filename in sorted(files):
            path = os.path.join(root, filename)
            if is_image_file(filename) and is_readable_image(path):
                paths.append(path)
    return paths


def list_class_dirs(source):
    """Renvoie les sous-dossiers de source, triés (= ordre des classes)."""
    if not os.path.isdir(source):
        raise ValueError(f"'{source}' n'est pas un dossier valide.")

    class_dirs = sorted(
        d for d in os.listdir(source)
        if os.path.isdir(os.path.join(source, d)))
    if not class_dirs:
        raise ValueError(f"'{source}' ne contient aucun sous-dossier.")
    return class_dirs


def load_dataset(source):
    """Scanne source et renvoie (samples, class_to_index).

    samples        : liste de tuples (chemin, label)
    class_to_index : dict {nom_de_classe: index}

    Lève ValueError avec un message clair si le dataset est inutilisable.
    """
    paths_by_class = {}
    for class_name in list_class_dirs(source):
        paths = scan_class_dir(os.path.join(source, class_name))
        if paths:
            paths_by_class[class_name] = paths
        else:
            warn(f"la classe '{class_name}' ne contient aucune image, "
                 "elle est ignorée.")

    if not paths_by_class:
        raise ValueError(f"'{source}' ne contient aucune image valide.")
    if len(paths_by_class) < MIN_CLASSES:
        raise ValueError(
            f"le dataset doit contenir au moins {MIN_CLASSES} classes "
            f"(trouvée(s) : {', '.join(paths_by_class)}).")

    class_to_index = {name: i for i, name in enumerate(paths_by_class)}
    samples = [
        (path, class_to_index[name])
        for name, paths in paths_by_class.items()
        for path in paths]
    return samples, class_to_index


def print_summary(samples, class_to_index):
    counts = Counter(label for _, label in samples)
    width = max(len(name) for name in class_to_index)

    print(f"Nombre de classes : {len(class_to_index)}")
    print(f"Nombre total d'images : {len(samples)}")
    for name, index in class_to_index.items():
        print(f"  [{index}] {name:<{width}}  {counts[index]:>5} images")


def main():
    args = parse_args()
    try:
        samples, class_to_index = load_dataset(args.source)
    except (ValueError, OSError) as e:
        print(f"Erreur : {e}", file=sys.stderr)
        sys.exit(1)
    print_summary(samples, class_to_index)


if __name__ == "__main__":
    main()
