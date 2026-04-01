"""Image transformation - Part 3."""
import argparse
import sys
from pathlib import Path
from src.application.use_cases.transform_images import TransformImagesUseCase
from src.adapters.repositories.file_image_repository import FileImageRepository
from src.adapters.presenters.transformation_presenter import TransformationPresenter
from src.adapters.controllers.transformation_controller import TransformationController
from src.application.services.image_transformation import ImageTransformationService
from src.frameworks.cv_transformations import (
    FlipTransformation,
    RotateTransformation,
    SkewTransformation,
    ShearTransformation,
    CropTransformation,
    DistortionTransformation,
)


def main() -> int:
    """Transform leaf images."""
    parser = argparse.ArgumentParser(
        description="Transform leaf images and extract features"
    )
    parser.add_argument(
        "input",
        help="Path to image or directory",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output directory (for batch processing)",
    )
    
    args = parser.parse_args()
    input_path = Path(args.input)
    
    try:
        # Dependency injection
        repository = FileImageRepository()
        
        # Create transformation service
        transformations = {
            "flip": FlipTransformation(),
            "rotate": RotateTransformation(45),
            "skew": SkewTransformation(),
            "shear": ShearTransformation(),
            "crop": CropTransformation(),
            "distortion": DistortionTransformation(),
        }
        transformation_service = ImageTransformationService(transformations)
        
        presenter = TransformationPresenter()
        use_case = TransformImagesUseCase(repository, transformation_service)
        controller = TransformationController(use_case, presenter)
        
        # Execute
        if input_path.is_file():
            controller.handle_single_image(input_path)
        elif input_path.is_dir():
            output_dir = Path(args.output) if args.output else input_path / "transformed"
            controller.handle_directory(input_path, output_dir)
        else:
            raise FileNotFoundError(f"Path not found: {input_path}")
        
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
