#!/usr/bin/env python3
import os
import sys
import csv
import argparse
import random
from collections import Counter
from typing import NamedTuple
from PIL import Image
from preprocess import IMG_SIZE

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MIN_CLASSES = 2
MIN_VAL_IMAGES = 100
# Suffixes added by Augmentation.process() to the original file name
AUGMENTATION_SUFFIXES = (
    "_original", "_mirror", "_flip", "_posterize",
    "_contrast", "_rotation", "_projective")


class Sample(NamedTuple):
    """One image of the dataset."""
    path: str
    label: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train a leaf disease classification model.",
        epilog="Example: ./train.py ./leaves/images/")

    parser.add_argument(
        "source",
        help="directory containing one subdirectory of images per class")
    parser.add_argument(
        "--epochs", type=int, default=10,
        help="number of passes over the dataset (default: %(default)s)")
    parser.add_argument(
        "--img-size", type=int, default=IMG_SIZE[0],
        help="image side length in pixels (default: %(default)s)")
    parser.add_argument(
        "--output", default="leaffliction.zip",
        help="name of the output zip (default: %(default)s)")
    parser.add_argument(
        "--seed", type=int, default=42,
        help="random seed (default: %(default)s)")
    parser.add_argument(
        "--val-ratio", type=float, default=0.2,
        help="share of images kept for validation (default: %(default)s)")
    parser.add_argument(
        "--val-file", default="validation.csv",
        help="CSV file listing the validation images "
             "(default: %(default)s)")

    args = parser.parse_args()

    if args.epochs < 1:
        parser.error("--epochs must be at least 1.")
    if args.img_size < 1:
        parser.error("--img-size must be at least 1.")
    if args.seed < 0:
        parser.error("--seed must be a positive number.")
    if not 0 < args.val_ratio < 1:
        parser.error("--val-ratio must be strictly between 0 and 1.")

    return args


def warn(message: str) -> None:
    print(f"Warning: {message}", file=sys.stderr)


def is_readable_image(path: str) -> bool:
    """Return True if the file is a readable image, False otherwise."""
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception as e:
        warn(f"unreadable image skipped: {path} ({e})")
        return False


def is_image_file(filename: str) -> bool:
    return os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS


def scan_class_dir(class_dir: str) -> list[str]:
    """Return the paths of the valid images of a class directory."""
    paths = []
    for root, _, files in os.walk(class_dir):
        for filename in sorted(files):
            path = os.path.join(root, filename)
            if is_image_file(filename) and is_readable_image(path):
                paths.append(path)
    return paths


def list_class_dirs(source: str) -> list[str]:
    """Return the subdirectories of source, sorted (= class order)."""
    if not os.path.isdir(source):
        raise ValueError(f"'{source}' is not a valid directory.")

    class_dirs = sorted(
        d for d in os.listdir(source)
        if os.path.isdir(os.path.join(source, d)))
    if not class_dirs:
        raise ValueError(f"'{source}' does not contain any subdirectory.")
    return class_dirs


def load_dataset(source: str) -> tuple[list[Sample], dict[str, int]]:
    """Scan source and return (samples, class_to_index).

    samples        : list of Sample(path, label)
    class_to_index : dict {class_name: index}

    Raise ValueError with a clear message if the dataset is unusable.
    """
    paths_by_class: dict[str, list[str]] = {}
    for class_name in list_class_dirs(source):
        paths = scan_class_dir(os.path.join(source, class_name))
        if paths:
            paths_by_class[class_name] = paths
        else:
            warn(f"class '{class_name}' contains no image, skipped.")

    if not paths_by_class:
        raise ValueError(f"'{source}' does not contain any valid image.")
    if len(paths_by_class) < MIN_CLASSES:
        raise ValueError(
            f"the dataset must contain at least {MIN_CLASSES} classes "
            f"(found: {', '.join(paths_by_class)}).")

    class_to_index = {name: i for i, name in enumerate(paths_by_class)}
    samples = [
        Sample(path, class_to_index[name])
        for name, paths in paths_by_class.items()
        for path in paths]
    return samples, class_to_index


def split_dataset(
    samples: list[Sample],
    val_ratio: float,
    seed: int
) -> tuple[list[Sample], list[Sample]]:
    """Split samples into (train, val), class by class.

    Each class keeps the same proportion of images in validation.
    The same seed always gives the same split.
    """
    paths_by_label: dict[int, list[str]] = {}
    for sample in samples:
        paths_by_label.setdefault(sample.label, []).append(sample.path)

    # Local generator, so the global random state is left untouched
    rng = random.Random(seed)
    train: list[Sample] = []
    val: list[Sample] = []
    for label, paths in paths_by_label.items():
        rng.shuffle(paths)
        n_val = max(1, round(len(paths) * val_ratio))
        val += [Sample(path, label) for path in paths[:n_val]]
        train += [Sample(path, label) for path in paths[n_val:]]
    return train, val


def original_name(path: str) -> str:
    """Return the image name without extension or augmentation suffix.

    "Apple_rust/image (1)_mirror.JPG" -> "image (1)"
    """
    name = os.path.splitext(os.path.basename(path))[0]
    for suffix in AUGMENTATION_SUFFIXES:
        if name.endswith(suffix):
            return name[:-len(suffix)]
    return name


def check_no_leak(train: list[Sample], val: list[Sample]) -> None:
    """Raise ValueError if an image, or a variant of it, is in both sets."""
    train_keys = {(s.label, original_name(s.path)) for s in train}
    val_keys = {(s.label, original_name(s.path)) for s in val}
    leaks = train_keys & val_keys
    if leaks:
        examples = ", ".join(sorted(name for _, name in leaks)[:3])
        raise ValueError(
            f"{len(leaks)} image(s) present in both train and validation "
            f"(e.g. {examples}). Run train on the original images, "
            "not on an augmented directory.")


def check_val_size(val: list[Sample]) -> None:
    if len(val) < MIN_VAL_IMAGES:
        raise ValueError(
            f"the validation set has {len(val)} images, at least "
            f"{MIN_VAL_IMAGES} are required (increase --val-ratio "
            "or use a bigger dataset).")


def save_split(
    samples: list[Sample],
    class_names: list[str],
    path: str
) -> None:
    """Write samples to a CSV file with the columns path,label."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["path", "label"])
        for sample in samples:
            writer.writerow([sample.path, class_names[sample.label]])


def print_split_summary(
    train: list[Sample],
    val: list[Sample],
    class_to_index: dict[str, int]
) -> None:
    train_counts = Counter(s.label for s in train)
    val_counts = Counter(s.label for s in val)
    width = max(len(name) for name in [*class_to_index, "Total"])

    print(f"{len(class_to_index)} classes, "
          f"{len(train) + len(val)} images:")
    print(f"  {'Class':<{width}}  {'Train':>6}  {'Val':>6}")
    for name, index in class_to_index.items():
        print(f"  {name:<{width}}  {train_counts[index]:>6}  "
              f"{val_counts[index]:>6}")
    print(f"  {'Total':<{width}}  {len(train):>6}  {len(val):>6}")


def main() -> None:
    args = parse_args()
    try:
        samples, class_to_index = load_dataset(args.source)
        train, val = split_dataset(samples, args.val_ratio, args.seed)
        check_no_leak(train, val)
        check_val_size(val)
        save_split(val, list(class_to_index), args.val_file)
    except (ValueError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    print_split_summary(train, val, class_to_index)
    print(f"Validation images saved to {args.val_file}")


if __name__ == "__main__":
    main()
