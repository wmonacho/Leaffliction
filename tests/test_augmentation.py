import pytest

import Augmentation

EXPECTED_KEYS = [
    "original", "mirror", "flip", "posterize",
    "contrast", "rotation", "projective",
]


@pytest.fixture(autouse=True)
def no_display(monkeypatch):
    monkeypatch.setattr(Augmentation, "display", lambda *a, **k: None)


@pytest.mark.parametrize("func", [
    Augmentation.mirror,
    Augmentation.flip,
    Augmentation.posterize,
    Augmentation.contrast,
    Augmentation.projective,
])
def test_transform_keeps_size(func, leaf_image):
    assert func(leaf_image).size == leaf_image.size


def test_mirror_twice_is_identity(leaf_image):
    twice = Augmentation.mirror(Augmentation.mirror(leaf_image))
    assert list(twice.getdata()) == list(leaf_image.getdata())


def test_rotation_expands_canvas(leaf_image):
    w, h = leaf_image.size
    rw, rh = Augmentation.rotation(leaf_image).size
    assert rw > w and rh > h


def test_process_returns_all_transformations(leaf_path):
    assert list(Augmentation.process(str(leaf_path))) == EXPECTED_KEYS


def test_process_single_image_saves_files(leaf_path, tmp_path):
    out = tmp_path / "out"
    Augmentation.process_single_image(str(leaf_path), str(out))
    saved = sorted(p.name for p in out.iterdir())
    assert saved == sorted(f"leaf_{k}.JPG" for k in EXPECTED_KEYS)


def test_process_directory_mirrors_tree(dataset_dir, tmp_path):
    root, counts = dataset_dir
    out = tmp_path / "augmented"
    Augmentation.process_directory(str(root), str(out))
    for name, n in counts.items():
        files = list((out / name).iterdir())
        assert len(files) == n * len(EXPECTED_KEYS)
