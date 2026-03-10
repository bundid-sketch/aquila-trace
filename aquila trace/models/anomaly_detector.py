"""Anomaly detection model for transaction analysis."""
import logging
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Optional

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Detects anomalous transactions using Isolation Forest.
    """
    
    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        """
        Initialize the anomaly detector.
        
        Args:
            contamination: Expected proportion of anomalies in the dataset.
            random_state: Random seed for reproducibility.
        """
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100
        )
        self.trained = False
        logger.info("AnomalyDetector initialized")
    
    def train(self, features: np.ndarray) -> None:
        """
        Train the anomaly detection model.
        
        Args:
            features: Training features (n_samples, n_features).
        """
        try:
            if features.shape[0] < 10:
                logger.warning("Training with fewer than 10 samples")
            
            self.model.fit(features)
            self.trained = True
            logger.info(f"AnomalyDetector trained on {features.shape[0]} samples")
        except Exception as e:
            logger.error(f"Error training AnomalyDetector: {e}")
            raise
    
    def detect(self, features: np.ndarray) -> np.ndarray:
        """
        Detect anomalies in the given features.
        
        Args:
            features: Features to analyze (n_samples, n_features).
            
        Returns:
            Array of predictions (-1 for anomalies, 1 for normal).
        """
        if not self.trained:
            logger.warning("Detecting anomalies with untrained model")
        
        try:
            predictions = self.model.predict(features)
            n_anomalies = np.sum(predictions == -1)
            logger.info(f"Detected {n_anomalies} anomalies out of {len(features)} samples")
            return predictions
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            raise
    
    def get_anomaly_scores(self, features: np.ndarray) -> np.ndarray:
        """
        Get anomaly scores (negative = more anomalous).
        
        Args:
            features: Features to analyze.
            
        Returns:
            Anomaly scores.
        """
        return self.model.score_samples(features)
