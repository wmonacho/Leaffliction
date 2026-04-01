"""Model training - Part 4."""
import argparse
import sys
from pathlib import Path
from src.application.use_cases.train_classifier import TrainClassifierUseCase
from src.adapters.repositories.file_image_repository import FileImageRepository
from src.adapters.presenters.training_presenter import TrainingPresenter
from src.adapters.controllers.training_controller import TrainingController
from src.application.services.feature_extraction import FeatureExtractionService
from src.application.services.classification import ClassificationService
from src.frameworks.cv_feature_extraction import (
    HistogramFeatureExtractor,
)
from src.frameworks.sklearn_classification import RandomForestClassification


def main() -> int:
    """Train disease classifier."""
    parser = argparse.ArgumentParser(
        description="Train disease classifier on leaf images"
    )
    parser.add_argument("dataset_path", help="Path to dataset directory")
    parser.add_argument(
        "-t",
        "--test-size",
        type=float,
        default=0.2,
        help="Test/validation set size (default: 0.2)",
    )
    
    args = parser.parse_args()
    dataset_path = Path(args.dataset_path)
    
    try:
        # Dependency injection
        repository = FileImageRepository()
        
        # Feature extraction
        feature_extractor = HistogramFeatureExtractor()
        feature_service = FeatureExtractionService(feature_extractor)
        
        # Classification
        classifier = RandomForestClassification()
        classification_service = ClassificationService(classifier)
        
        presenter = TrainingPresenter()
        use_case = TrainClassifierUseCase(
            repository, feature_service, classification_service
        )
        controller = TrainingController(use_case, presenter)
        
        # Execute
        controller.handle(dataset_path, args.test_size)
        
        # Save model
        classifier.save("model.pkl")
        print("✅ Model saved to model.pkl")
        
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
