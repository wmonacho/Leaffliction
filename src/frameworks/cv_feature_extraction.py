"""Scikit-learn based feature extraction."""
import numpy as np
import cv2
from src.application.services.feature_extraction import FeatureExtractionStrategy


class HistogramFeatureExtractor(FeatureExtractionStrategy):
    """Extract color histogram features."""

    def extract(self, image: np.ndarray) -> np.ndarray:
        """Extract color histogram features from image."""
        histograms = []
        
        # Handle both RGB and BGR images
        num_channels = min(3, image.shape[2] if len(image.shape) > 2 else 1)
        
        for i in range(num_channels):
            # Compute histogram with 32 bins per channel
            hist = cv2.calcHist([image], [i], None, [32], [0, 256])
            histograms.append(hist.flatten())
        
        # Concatenate all histograms
        features = np.concatenate(histograms)
        return features


class ColorMomentsFeatureExtractor(FeatureExtractionStrategy):
    """Extract color moments (mean, std, skewness) as features."""

    def extract(self, image: np.ndarray) -> np.ndarray:
        """Extract color moments features."""
        features = []
        
        # Get color channels
        num_channels = min(3, image.shape[2] if len(image.shape) > 2 else 1)
        
        for i in range(num_channels):
            channel = image[:, :, i].astype(np.float32) / 255.0
            
            # Mean
            mean = np.mean(channel)
            features.append(mean)
            
            # Standard deviation
            std = np.std(channel)
            features.append(std)
            
            # Skewness
            flattened = channel.flatten()
            skewness = np.mean((flattened - mean)**3) / (std**3 + 1e-6)
            features.append(skewness)
        
        return np.array(features)


class HybridFeatureExtractor(FeatureExtractionStrategy):
    """Combine multiple feature extraction methods."""

    def __init__(
        self,
        histogram_extractor: HistogramFeatureExtractor,
        moments_extractor: ColorMomentsFeatureExtractor,
    ) -> None:
        """Initialize with multiple extractors."""
        self.histogram = histogram_extractor
        self.moments = moments_extractor

    def extract(self, image: np.ndarray) -> np.ndarray:
        """Extract combined features."""
        hist_features = self.histogram.extract(image)
        moments_features = self.moments.extract(image)
        return np.concatenate([hist_features, moments_features])
