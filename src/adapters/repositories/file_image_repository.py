"""File-based image repository implementation."""
from pathlib import Path
import cv2
import numpy as np
from src.domain.entities import LeafImage
from src.domain.repositories import ImageRepository


class FileImageRepository(ImageRepository):
    """Repository implementation using filesystem storage."""

    def load_from_path(self, path: Path) -> LeafImage:
        """Load single image from path."""
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")

        # Read image
        image_array = cv2.imread(str(path))
        if image_array is None:
            raise ValueError(f"Failed to read image: {path}")

        # Parse label from directory structure
        plant_type = path.parent.parent.name  # e.g., "leaves"
        label = path.parent.name  # e.g., "Apple_healthy"
        image_id = path.stem  # filename without extension

        return LeafImage(
            id=image_id,
            path=path,
            array=image_array,
            label=label,
            plant_type=plant_type,
        )

    def load_from_directory(
        self, directory: Path, recursive: bool = True
    ) -> list[LeafImage]:
        """Load all images from directory and subdirectories."""
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        pattern = "**/*.jpg" if recursive else "*.jpg"
        image_paths = list(directory.glob(pattern))

        # Also look for other formats
        for ext in ["*.jpeg", "*.png", "*.bmp"]:
            pattern = f"**/{ext}" if recursive else ext
            image_paths.extend(directory.glob(pattern))

        images = []
        for image_path in image_paths:
            try:
                images.append(self.load_from_path(image_path))
            except (ValueError, FileNotFoundError) as e:
                print(f"Warning: Skipping {image_path}: {e}")

        return images

    def save(self, image: LeafImage, output_path: Path) -> None:
        """Save image to filesystem."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        success = cv2.imwrite(str(output_path), image.array)
        if not success:
            raise IOError(f"Failed to save image: {output_path}")

    def save_batch(self, images: list[LeafImage], output_dir: Path) -> None:
        """Save multiple images to directory."""
        output_dir.mkdir(parents=True, exist_ok=True)
        for image in images:
            self.save(image, output_dir / image.get_filename())
