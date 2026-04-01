"""Classification service."""
from abc import ABC, abstractmethod
import numpy as np


class ClassificationStrategy(ABC):
    """Strategy pattern for classification algorithms."""

    @abstractmethod
    def train(
        self,
        features: np.ndarray,
        labels: list[str],
        validation_split: float = 0.2,
    ) -> dict:
        """Train classifier."""
        pass

    @abstractmethod
    def predict(self, features: np.ndarray) -> dict:
        """Make prediction."""
        pass


class ClassificationService:
    """Service managing classification operations."""

    def __init__(self, strategy: ClassificationStrategy) -> None:
        """Initialize with classification strategy."""
        self._strategy = strategy

    def train_with_validation(
        self,
        features: np.ndarray,
        labels: list[str],
        test_size: float = 0.2,
        min_validation_images: int = 100,
    ) -> dict:
        """Train and validate classifier."""
        result = self._strategy.train(features, labels, test_size)

        if result["validation_size"] < min_validation_images:
            raise ValueError(
                f"Validation set size {result['validation_size']} "
                f"is below minimum {min_validation_images}"
            )

        return result

    def predict(self, features: np.ndarray) -> dict:
        """Make prediction."""
        return self._strategy.predict(features)
