"""Image path value object."""
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ImagePath:
    """Immutable value object for image paths with validation."""

    path: Path

    def __post_init__(self) -> None:
        """Validate image path exists and is an image file."""
        if not self.path.exists():
            raise ValueError(f"Image path does not exist: {self.path}")

        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp"}
        if self.path.suffix.lower() not in valid_extensions:
            raise ValueError(
                f"Invalid image extension: {self.path.suffix}. "
                f"Must be one of {valid_extensions}"
            )

    def __str__(self) -> str:
        return str(self.path)
