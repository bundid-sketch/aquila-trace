"""Risk scoring model for transaction analysis."""
import logging
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class RiskScorer:
    """
    Scores risk levels for transactions using a trained classifier.
    """
    
    def __init__(self, random_state: int = 42):
        """
        Initialize the risk scorer.
        
        Args:
            random_state: Random seed for reproducibility.
        """
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=random_state,
            max_depth=10
        )
        self.scaler = StandardScaler()
        self.trained = False
        logger.info("RiskScorer initialized")
    
    def train(self, features: np.ndarray, labels: np.ndarray) -> None:
        """
        Train the risk scoring model.
        
        Args:
            features: Training features (n_samples, n_features).
            labels: Binary labels (0 = low risk, 1 = high risk).
        """
        try:
            if features.shape[0] != len(labels):
                raise ValueError("Features and labels must have same length")
            
            features_scaled = self.scaler.fit_transform(features)
            self.model.fit(features_scaled, labels)
            self.trained = True
            logger.info(f"RiskScorer trained on {features.shape[0]} samples")
        except Exception as e:
            logger.error(f"Error training RiskScorer: {e}")
            raise
    
    def score(self, features: np.ndarray) -> np.ndarray:
        """
        Score risk level for given features.
        
        Args:
            features: Features to score (n_samples, n_features).
            
        Returns:
            Risk scores between 0 and 1 (higher = more risky).
        """
        if not self.trained:
            logger.warning("Scoring with untrained model")
            return np.random.random(features.shape[0])
        
        try:
            features_scaled = self.scaler.transform(features)
            # Get probability of high risk class
            probabilities = self.model.predict_proba(features_scaled)
            risk_scores = probabilities[:, 1]  # Probability of class 1
            return risk_scores
        except Exception as e:
            logger.error(f"Error scoring risk: {e}")
            raise
    
    def get_feature_importance(self) -> dict:
        """
        Get feature importance scores.
        
        Returns:
            Dictionary mapping feature names to importance scores.
        """
        if not self.trained:
            return {}
        
        return {
            f"feature_{i}": score 
            for i, score in enumerate(self.model.feature_importances_)
        }
