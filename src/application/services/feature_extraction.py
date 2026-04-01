"""Feature extraction service."""
from abc import ABC, abstractmethod
import numpy as np


class FeatureExtractionStrategy(ABC):
    """Strategy pattern for feature extraction."""

    @abstractmethod
    def extract(self, image: np.ndarray) -> np.ndarray:
        """Extract feature vector from image."""
        pass


class FeatureExtractionService:
    """Service to extract features from images."""

    def __init__(self, strategy: FeatureExtractionStrategy) -> None:
        """Initialize with extraction strategy."""
        self._strategy = strategy

    def extract(self, image: np.ndarray) -> np.ndarray:
        """Extract features from image."""
        features = self._strategy.extract(image)
        # Normalize features
        norm = np.linalg.norm(features)
        return features / norm if norm > 0 else features
