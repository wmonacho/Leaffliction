"""Prediction controller."""
from pathlib import Path
from src.application.use_cases.predict_disease import PredictDiseaseUseCase
from src.adapters.presenters import PredictionPresenter


class PredictionController:
    """CLI controller for Part 4 - Prediction."""

    def __init__(
        self,
        predict_use_case: PredictDiseaseUseCase,
        presenter: PredictionPresenter,
    ) -> None:
        """Initialize with dependencies."""
        self._use_case = predict_use_case
        self._presenter = presenter

    def handle(self, image_path: Path) -> None:
        """Handle prediction request."""
        result = self._use_case.execute(image_path)
        self._presenter.present(result)
