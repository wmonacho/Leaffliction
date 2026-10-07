import numpy as np
import pytest

pytestmark = pytest.mark.slow

Transformation = pytest.importorskip("Transformation")


@pytest.fixture
def bgr_leaf(leaf_image):
    return np.array(leaf_image)[:, :, ::-1].copy()


def test_create_mask_is_binary_and_finds_leaf(bgr_leaf):
    mask = Transformation.create_mask_step(bgr_leaf)
    assert mask.shape == bgr_leaf.shape[:2]
    assert set(np.unique(mask)) <= {0, 255}
    h, w = mask.shape
    assert mask[h // 2, w // 2] == 255  # centre = feuille
    assert mask[0, 0] == 0              # coin = fond


def test_mask_step_whitens_background(bgr_leaf):
    mask = Transformation.create_mask_step(bgr_leaf)
    masked = Transformation.mask_step(bgr_leaf, mask)
    assert tuple(masked[0, 0]) == (255, 255, 255)
