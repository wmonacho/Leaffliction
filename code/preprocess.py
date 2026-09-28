import os
import json
import cv2
import numpy as np

IMG_SIZE = (128, 128)
CLASSES_FILE = "classes.json"


def load_image(path):
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"Impossible de lire l'image : {path}")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def preprocess(img_rgb):
    img = cv2.resize(img_rgb, IMG_SIZE, interpolation=cv2.INTER_AREA)
    return img.astype(np.float32) / 255.0


def get_class_names(dataset_dir):
    return sorted(
        d for d in os.listdir(dataset_dir)
        if os.path.isdir(os.path.join(dataset_dir, d)))


def save_class_names(class_names, model_dir):
    with open(os.path.join(model_dir, CLASSES_FILE), "w") as f:
        json.dump(class_names, f, indent=2)


def load_class_names(model_dir):
    with open(os.path.join(model_dir, CLASSES_FILE)) as f:
        return json.load(f)
