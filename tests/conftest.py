import matplotlib
import numpy as np
import pytest
from PIL import Image

# Backend sans fenêtre : aucun plt.show() ne bloque pendant les tests
matplotlib.use("Agg")


def make_leaf_image(size=(64, 48)):
    """Image RGB synthétique : fond gris clair + ellipse verte (la "feuille")."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w]
    inside = ((xx - w / 2) / (w / 3)) ** 2 + ((yy - h / 2) / (h / 3)) ** 2 <= 1
    arr = np.full((h, w, 3), 200, dtype=np.uint8)
    arr[inside] = (40, 160, 40)
    return Image.fromarray(arr)


@pytest.fixture
def leaf_image():
    return make_leaf_image()


@pytest.fixture
def leaf_path(tmp_path):
    path = tmp_path / "leaf.JPG"
    make_leaf_image().save(path)
    return path


@pytest.fixture
def dataset_dir(tmp_path):
    """Mini dataset : 3 classes avec des effectifs différents + bruit."""
    root = tmp_path / "images"
    counts = {"Apple_healthy": 3, "Apple_rust": 2, "Grape_Esca": 1}
    for name, n in counts.items():
        class_dir = root / name
        class_dir.mkdir(parents=True)
        for i in range(n):
            make_leaf_image().save(class_dir / f"image ({i + 1}).JPG")
    (root / "Apple_healthy" / "notes.txt").write_text("pas une image")
    (root / "empty_class").mkdir()
    return root, counts
