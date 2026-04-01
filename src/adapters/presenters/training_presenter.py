"""Training presenter."""
from src.application.use_cases.train_classifier import TrainingResult


class TrainingPresenter:
    """Present training results."""

    def present(self, result: TrainingResult) -> None:
        """Display training metrics."""
        print(f"\n🧠 Model Training Complete")
        print(f"   Training Set Size: {result.training_size}")
        print(f"   Validation Set Size: {result.validation_size}")
        print(f"   Validation Accuracy: {result.validation_accuracy:.2%}")
        print(f"   Number of Classes: {result.num_classes}")
        print(f"   Classes: {', '.join(result.class_names)}")

        if result.validation_accuracy >= 0.90:
            print(f"\n✅ Target accuracy (90%) ACHIEVED!")
        else:
            print(
                f"\n⚠️  Target accuracy (90%) not met. "
                f"Current: {result.validation_accuracy:.2%}"
            )
