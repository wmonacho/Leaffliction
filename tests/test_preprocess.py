import numpy as np
import pytest

import preprocess


def test_load_image_returns_rgb(leaf_path):
    img = preprocess.load_image(str(leaf_path))
    assert img.ndim == 3 and img.shape[2] == 3
    # le centre de la feuille synthétique est vert en RGB (pas en BGR)
    r, g, b = img[img.shape[0] // 2, img.shape[1] // 2]
    assert g > r and g > b


def test_load_image_invalid_path_raises(tmp_path):
    with pytest.raises(ValueError):
        preprocess.load_image(str(tmp_path / "missing.jpg"))


def test_preprocess_shape_dtype_and_range(leaf_path):
    out = preprocess.preprocess(preprocess.load_image(str(leaf_path)))
    assert out.shape == (*preprocess.IMG_SIZE, 3)
    assert out.dtype == np.float32
    assert 0.0 <= out.min() and out.max() <= 1.0


def test_get_class_names_sorted_dirs_only(dataset_dir):
    root, counts = dataset_dir
    (root / "stray_file.txt").write_text("x")
    names = preprocess.get_class_names(str(root))
    assert names == sorted([*counts, "empty_class"])


def test_class_names_roundtrip(tmp_path):
    names = ["Apple_healthy", "Apple_rust", "Grape_Esca"]
    preprocess.save_class_names(names, str(tmp_path))
    assert (tmp_path / preprocess.CLASSES_FILE).exists()
    assert preprocess.load_class_names(str(tmp_path)) == names
