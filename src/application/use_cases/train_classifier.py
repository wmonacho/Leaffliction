"""Part 4 - Train classifier use case."""
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import numpy as np
from src.domain.repositories import ImageRepository
from src.application.services import FeatureExtractionService, ClassificationService


@dataclass
class TrainingResult:
    """Result of model training."""

    training_size: int
    validation_size: int
    validation_accuracy: float
    num_classes: int
    class_names: list[str]


class TrainClassifierUseCase:
    """Train disease classifier (Part 4 - train.py)."""

    def __init__(
        self,
        image_repository: ImageRepository,
        feature_extraction_service: FeatureExtractionService,
        classification_service: ClassificationService,
    ) -> None:
        """Initialize with dependencies."""
        self._repository = image_repository
        self._feature_service = feature_extraction_service
        self._classification_service = classification_service

    def execute(
        self,
        dataset_path: Path,
        test_size: float = 0.2,
        min_validation_images: int = 100,
    ) -> TrainingResult:
        """Train classifier on dataset."""
        # Load all images
        images = self._repository.load_from_directory(dataset_path)

        if not images:
            raise ValueError(f"No images found in {dataset_path}")

        # Extract features
        features = np.array(
            [self._feature_service.extract(image.array) for image in images]
        )
        labels = [image.label for image in images]

        # Train and validate
        result = self._classification_service.train_with_validation(
            features=features,
            labels=labels,
            test_size=test_size,
            min_validation_images=min_validation_images,
        )

        return TrainingResult(
            training_size=result["training_size"],
            validation_size=result["validation_size"],
            validation_accuracy=result["validation_accuracy"],
            num_classes=result["num_classes"],
            class_names=result["class_names"],
        )
