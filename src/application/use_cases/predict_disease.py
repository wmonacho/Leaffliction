"""Part 4 - Predict disease use case."""
from pathlib import Path
from src.domain.entities import ClassificationResult
from src.domain.repositories import ImageRepository
from src.application.services import FeatureExtractionService, ClassificationService


class PredictDiseaseUseCase:
    """Predict disease from leaf image (Part 4 - predict.py)."""

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

    def execute(self, image_path: Path) -> ClassificationResult:
        """Predict disease for a single image."""
        # Load image
        leaf_image = self._repository.load_from_path(image_path)

        # Extract features
        features = self._feature_service.extract(leaf_image.array)

        # Predict
        prediction = self._classification_service.predict(features)

        return ClassificationResult(
            predicted_disease=prediction["disease"],
            confidence=prediction["confidence"],
            original_image=leaf_image.array,
            transformed_image=prediction.get("transformed_image", leaf_image.array),
        )
