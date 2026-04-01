"""Training controller."""
from pathlib import Path
from src.application.use_cases.train_classifier import TrainClassifierUseCase
from src.adapters.presenters import TrainingPresenter


class TrainingController:
    """CLI controller for Part 4 - Training."""

    def __init__(
        self,
        train_use_case: TrainClassifierUseCase,
        presenter: TrainingPresenter,
    ) -> None:
        """Initialize with dependencies."""
        self._use_case = train_use_case
        self._presenter = presenter

    def handle(self, dataset_path: Path, test_size: float = 0.2) -> None:
        """Handle training request."""
        result = self._use_case.execute(dataset_path, test_size)
        self._presenter.present(result)
