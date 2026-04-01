"""Abstract repository for image persistence (DIP)."""
from abc import ABC, abstractmethod
from pathlib import Path
from src.domain.entities import LeafImage


class ImageRepository(ABC):
    """Abstract repository following Dependency Inversion Principle."""

    @abstractmethod
    def load_from_path(self, path: Path) -> LeafImage:
        """Load image from filesystem."""
        pass

    @abstractmethod
    def load_from_directory(
        self, directory: Path, recursive: bool = True
    ) -> list[LeafImage]:
        """Load all images from directory."""
        pass

    @abstractmethod
    def save(self, image: LeafImage, output_path: Path) -> None:
        """Save image to filesystem."""
        pass

    @abstractmethod
    def save_batch(self, images: list[LeafImage], output_dir: Path) -> None:
        """Save multiple images to directory."""
        pass
