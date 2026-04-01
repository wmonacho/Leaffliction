"""Prediction presenter."""
import cv2
import matplotlib.pyplot as plt
from src.domain.entities import ClassificationResult


class PredictionPresenter:
    """Present prediction results."""

    def present(self, result: ClassificationResult) -> None:
        """Display prediction with images."""
        # Create figure with original and transformed
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle(
            f"Prediction: {result.predicted_disease} ({result.confidence:.2%})"
        )

        # Original
        axes[0].imshow(cv2.cvtColor(result.original_image, cv2.COLOR_BGR2RGB))
        axes[0].set_title("Original Image")
        axes[0].axis("off")

        # Transformed
        axes[1].imshow(cv2.cvtColor(result.transformed_image, cv2.COLOR_BGR2RGB))
        axes[1].set_title("Transformed Image")
        axes[1].axis("off")

        plt.tight_layout()
        plt.savefig("prediction.png")
        plt.show()

        # Console output
        print(f"\n🍃 Disease Prediction")
        print(f"   Disease: {result.predicted_disease}")
        print(f"   Confidence: {result.confidence:.2%}")
