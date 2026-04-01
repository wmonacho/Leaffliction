"""Part 3 - Transform images use case."""
from pathlib import Path
from dataclasses import dataclass
import numpy as np
from src.domain.entities import LeafImage
from src.domain.repositories import ImageRepository
from src.application.services import ImageTransformationService


@dataclass
class TransformationOutput:
    """Result of image transformation."""

    original: np.ndarray
    transformations: dict[str, np.ndarray]
    histogram: np.ndarray


class TransformImagesUseCase:
    """Transform images and extract features (Part 3)."""

    def __init__(
        self,
        image_repository: ImageRepository,
        transformation_service: ImageTransformationService,
    ) -> None:
        """Initialize with dependencies."""
        self._repository = image_repository
        self._transformation_service = transformation_service

    def execute_single_image(self, image_path: Path) -> TransformationOutput:
        """Transform a single image and return all transformations."""
        image = self._repository.load_from_path(image_path)
        return self._transform_image(image)

    def execute_directory(
        self, input_dir: Path, output_dir: Path
    ) -> list[TransformationOutput]:
        """Transform all images in directory and save results."""
        images = self._repository.load_from_directory(input_dir)
        results = []

        for image in images:
            result = self._transform_image(image)
            self._save_transformations(result, output_dir, image.id)
            results.append(result)

        return results

    def _transform_image(self, image: LeafImage) -> TransformationOutput:
        """Apply all transformations to a single image."""
        transformations = self._transformation_service.apply_all_transformations(
            image.array
        )
        histogram = self._transformation_service.compute_histogram(image.array)

        return TransformationOutput(
            original=image.array,
            transformations=transformations,
            histogram=histogram,
        )

    def _save_transformations(
        self, result: TransformationOutput, output_dir: Path, image_id: str
    ) -> None:
        """Save all transformations to disk."""
        output_dir.mkdir(parents=True, exist_ok=True)

        for name, transformed_image in result.transformations.items():
            self._repository.save(
                LeafImage(
                    id=f"{image_id}_{name}",
                    path=output_dir / f"{image_id}_{name}.jpg",
                    array=transformed_image,
                    label=name,
                    plant_type="unknown",
                ),
                output_dir / f"{image_id}_{name}.jpg",
            )
