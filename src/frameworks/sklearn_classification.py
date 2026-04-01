"""Scikit-learn based classification."""
from typing import Optional
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
from src.application.services.classification import ClassificationStrategy


class RandomForestClassification(ClassificationStrategy):
    """Random Forest classifier implementation."""

    def __init__(self, n_estimators: int = 100, random_state: int = 42) -> None:
        """Initialize random forest."""
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model: Optional[RandomForestClassifier] = None
        self.label_encoder: Optional[LabelEncoder] = None
        self.classes: list[str] = []

    def train(
        self,
        features: np.ndarray,
        labels: list[str],
        validation_split: float = 0.2,
    ) -> dict:
        """Train and validate classifier."""
        # Encode labels
        self.label_encoder = LabelEncoder()
        encoded_labels = self.label_encoder.fit_transform(labels)
        self.classes = list(self.label_encoder.classes_)

        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            features,
            encoded_labels,
            test_size=validation_split,
            random_state=self.random_state,
            stratify=encoded_labels,
        )

        # Train model
        self.model = RandomForestClassifier(
            n_estimators=self.n_estimators, random_state=self.random_state
        )
        self.model.fit(X_train, y_train)

        # Validate
        val_accuracy = self.model.score(X_val, y_val)

        return {
            "training_size": len(X_train),
            "validation_size": len(X_val),
            "validation_accuracy": val_accuracy,
            "num_classes": len(self.classes),
            "class_names": self.classes,
        }

    def predict(self, features: np.ndarray) -> dict:
        """Make prediction on features."""
        if self.model is None:
            raise RuntimeError("Model not trained. Call train() first.")

        # Ensure features is 2D
        if features.ndim == 1:
            features = features.reshape(1, -1)

        # Predict
        prediction_idx = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]

        predicted_label = self.label_encoder.inverse_transform([prediction_idx])[0]
        confidence = float(np.max(probabilities))

        return {
            "disease": predicted_label,
            "confidence": confidence,
            "probabilities": {
                cls: float(prob)
                for cls, prob in zip(self.classes, probabilities)
            },
        }

    def save(self, model_path: str) -> None:
        """Save trained model to disk."""
        if self.model is None:
            raise RuntimeError("No model to save")
        joblib.dump(
            {
                "model": self.model,
                "label_encoder": self.label_encoder,
                "classes": self.classes,
            },
            model_path,
        )

    def load(self, model_path: str) -> None:
        """Load trained model from disk."""
        data = joblib.load(model_path)
        self.model = data["model"]
        self.label_encoder = data["label_encoder"]
        self.classes = data["classes"]
