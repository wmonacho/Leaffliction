"""Image transformation service."""
from abc import ABC, abstractmethod
import numpy as np


class ImageTransformationStrategy(ABC):
    """Strategy pattern for image transformations."""

    @abstractmethod
    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply transformation."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get transformation name."""
        pass


class ImageTransformationService:
    """Service to apply various image transformations."""

    def __init__(self, strategies: dict[str, ImageTransformationStrategy]) -> None:
        """Initialize with transformation strategies."""
        self._strategies = strategies

    def apply_all_transformations(
        self, image: np.ndarray
    ) -> dict[str, np.ndarray]:
        """Apply all registered transformations."""
        return {
            name: strategy.apply(image) for name, strategy in self._strategies.items()
        }

    def apply_transformation(
        self, image: np.ndarray, name: str
    ) -> np.ndarray:
        """Apply a specific transformation."""
        if name not in self._strategies:
            raise ValueError(f"Unknown transformation: {name}")
        return self._strategies[name].apply(image)

    @staticmethod
    def compute_histogram(image: np.ndarray) -> np.ndarray:
        """Compute color histogram for RGB/BGR image."""
        import cv2

        histograms = []
        for i in range(min(3, image.shape[2] if len(image.shape) > 2 else 1)):
            hist = cv2.calcHist([image], [i], None, [256], [0, 256])
            histograms.append(hist.flatten())

        return np.concatenate(histograms) if histograms else np.array([])
