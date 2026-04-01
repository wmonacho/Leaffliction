"""Disease entity representing a leaf condition."""
from enum import Enum


class DiseaseType(str, Enum):
    """Enumeration of all supported diseases."""

    # Apple diseases
    APPLE_HEALTHY = "Apple_healthy"
    APPLE_BLACK_ROT = "Apple_Black_rot"
    APPLE_RUST = "Apple_rust"
    APPLE_SCAB = "Apple_scab"

    # Grape diseases
    GRAPE_HEALTHY = "Grape_healthy"
    GRAPE_ESCA = "Grape_Esca"
    GRAPE_BLACK_ROT = "Grape_Black_rot"
    GRAPE_SPOT = "Grape_spot"

    def get_plant_type(self) -> str:
        """Extract plant type from disease name."""
        return self.value.split("_")[0]

    def is_healthy(self) -> bool:
        """Check if this is a healthy leaf."""
        return "healthy" in self.value.lower()
