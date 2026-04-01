"""Leaf image entity."""
from dataclasses import dataclass
from pathlib import Path
import numpy as np


@dataclass(frozen=True)
class LeafImage:
    """Immutable leaf image entity - core business object."""

    id: str  # filename without extension
    path: Path
    array: np.ndarray
    label: str  # disease type or 'healthy'
    plant_type: str  # Apple or Grape

    def get_shape(self) -> tuple[int, int, int]:
        """Get image dimensions (height, width, channels)."""
        return self.array.shape

    def get_filename(self) -> str:
        """Get original filename."""
        return self.path.name
