"""OpenCV-based image transformations."""
import cv2
import numpy as np
from src.application.services.image_transformation import ImageTransformationStrategy


class FlipTransformation(ImageTransformationStrategy):
    """Horizontal flip transformation."""

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply horizontal flip."""
        return cv2.flip(image, 1)

    def get_name(self) -> str:
        return "flip"


class RotateTransformation(ImageTransformationStrategy):
    """Rotation transformation."""

    def __init__(self, angle: float = 45.0) -> None:
        """Initialize with rotation angle in degrees."""
        self.angle = angle

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply rotation."""
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, self.angle, 1.0)
        return cv2.warpAffine(image, matrix, (w, h), borderMode=cv2.BORDER_REFLECT)

    def get_name(self) -> str:
        return "rotate"


class SkewTransformation(ImageTransformationStrategy):
    """Skew transformation (perspective transform)."""

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply skew transformation."""
        h, w = image.shape[:2]
        pts1 = np.float32([[50, 50], [200, 50], [10, 200]])
        pts2 = np.float32([[10, 100], [200, 50], [100, 250]])
        matrix = cv2.getAffineTransform(pts1, pts2)
        return cv2.warpAffine(image, matrix, (w, h))

    def get_name(self) -> str:
        return "skew"


class ShearTransformation(ImageTransformationStrategy):
    """Shear transformation."""

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply shear transformation."""
        h, w = image.shape[:2]
        pts1 = np.float32([[0, 0], [w, 0], [0, h]])
        pts2 = np.float32([[0, h * 0.2], [w, 0], [0, h]])
        matrix = cv2.getAffineTransform(pts1, pts2)
        return cv2.warpAffine(image, matrix, (w, h))

    def get_name(self) -> str:
        return "shear"


class CropTransformation(ImageTransformationStrategy):
    """Center crop transformation."""

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply center crop."""
        h, w = image.shape[:2]
        h_crop, w_crop = h // 2, w // 2
        return image[h_crop // 2 : h_crop // 2 + h_crop, w_crop // 2 : w_crop // 2 + w_crop]

    def get_name(self) -> str:
        return "crop"


class DistortionTransformation(ImageTransformationStrategy):
    """Barrel/pincushion distortion transformation."""

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply distortion."""
        h, w = image.shape[:2]
        # Create distortion map
        map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))
        
        # Apply barrel distortion
        center_x, center_y = w / 2, h / 2
        radius_x, radius_y = w / 2, h / 2
        
        norm_x = (map_x - center_x) / radius_x
        norm_y = (map_y - center_y) / radius_y
        
        # Distortion factor
        r = np.sqrt(norm_x**2 + norm_y**2)
        distortion = 1 + 0.3 * (r**2)
        
        map_x = (center_x + norm_x * radius_x * distortion).astype(np.float32)
        map_y = (center_y + norm_y * radius_y * distortion).astype(np.float32)
        
        return cv2.remap(image, map_x, map_y, cv2.INTER_LINEAR)

    def get_name(self) -> str:
        return "distortion"
