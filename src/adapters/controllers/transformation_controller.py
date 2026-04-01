"""Transformation controller."""
from pathlib import Path
from src.application.use_cases.transform_images import TransformImagesUseCase
from src.adapters.presenters import TransformationPresenter


class TransformationController:
    """CLI controller for Part 3 - Image Transformation."""

    def __init__(
        self,
        transform_use_case: TransformImagesUseCase,
        presenter: TransformationPresenter,
    ) -> None:
        """Initialize with dependencies."""
        self._use_case = transform_use_case
        self._presenter = presenter

    def handle_single_image(self, image_path: Path) -> None:
        """Handle single image transformation."""
        result = self._use_case.execute_single_image(image_path)
        self._presenter.present_single(result, image_path)

    def handle_directory(self, input_dir: Path, output_dir: Path) -> None:
        """Handle directory transformation."""
        results = self._use_case.execute_directory(input_dir, output_dir)
        self._presenter.present_directory(results, output_dir)
