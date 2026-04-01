"""Classification result entity."""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class ClassificationResult:
    """Immutable classification result."""

    predicted_disease: str
    confidence: float
    original_image: np.ndarray
    transformed_image: np.ndarray

    def __post_init__(self) -> None:
        """Validate confidence is between 0 and 1."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
