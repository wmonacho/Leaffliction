"""Disease prediction - Part 4."""
import argparse
import sys
from pathlib import Path
from src.application.use_cases.predict_disease import PredictDiseaseUseCase
from src.adapters.repositories.file_image_repository import FileImageRepository
from src.adapters.presenters.prediction_presenter import PredictionPresenter
from src.adapters.controllers.prediction_controller import PredictionController
from src.application.services.feature_extraction import FeatureExtractionService
from src.application.services.classification import ClassificationService
from src.frameworks.cv_feature_extraction import HistogramFeatureExtractor
from src.frameworks.sklearn_classification import RandomForestClassification


def main() -> int:
    """Predict disease from leaf image."""
    parser = argparse.ArgumentParser(
        description="Predict disease from a leaf image"
    )
    parser.add_argument("image_path", help="Path to leaf image")
    parser.add_argument(
        "-m",
        "--model",
        default="model.pkl",
        help="Path to trained model (default: model.pkl)",
    )
    
    args = parser.parse_args()
    image_path = Path(args.image_path)
    model_path = Path(args.model)
    
    try:
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        # Dependency injection
        repository = FileImageRepository()
        
        # Feature extraction
        feature_extractor = HistogramFeatureExtractor()
        feature_service = FeatureExtractionService(feature_extractor)
        
        # Classification
        classifier = RandomForestClassification()
        classifier.load(str(model_path))
        classification_service = ClassificationService(classifier)
        
        presenter = PredictionPresenter()
        use_case = PredictDiseaseUseCase(
            repository, feature_service, classification_service
        )
        controller = PredictionController(use_case, presenter)
        
        # Execute
        controller.handle(image_path)
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
