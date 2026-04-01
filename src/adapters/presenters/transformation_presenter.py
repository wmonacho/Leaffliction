"""Transformation presenter."""
import cv2
import matplotlib.pyplot as plt
from pathlib import Path
from src.application.use_cases.transform_images import TransformationOutput


class TransformationPresenter:
    """Present image transformation results."""

    def present_single(self, result: TransformationOutput, image_path: Path) -> None:
        """Display single image with all transformations."""
        # Create figure with original + 6 transformations
        fig, axes = plt.subplots(2, 4, figsize=(16, 8))
        fig.suptitle(f"Image Transformations: {image_path.name}")

        # Original image
        axes[0, 0].imshow(cv2.cvtColor(result.original, cv2.COLOR_BGR2RGB))
        axes[0, 0].set_title("Original")
        axes[0, 0].axis("off")

        # 6 transformations
        for idx, (name, transformed) in enumerate(result.transformations.items(), 1):
            row = idx // 4
            col = idx % 4
            axes[row, col].imshow(cv2.cvtColor(transformed, cv2.COLOR_BGR2RGB))
            axes[row, col].set_title(name.title())
            axes[row, col].axis("off")

        # Histogram
        axes[1, 3].plot(result.histogram)
        axes[1, 3].set_title("Color Histogram")
        axes[1, 3].set_xlabel("Pixel Value")
        axes[1, 3].set_ylabel("Frequency")

        plt.tight_layout()
        plt.savefig(f"{image_path.stem}_transformations.png")
        plt.show()

    def present_directory(
        self, results: list[TransformationOutput], output_dir: Path
    ) -> None:
        """Report on directory transformations."""
        print(f"\n✅ Transformations Complete")
        print(f"   Processed: {len(results)} images")
        print(f"   Output Directory: {output_dir}")
