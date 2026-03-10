"""Machine Learning module for supervised and unsupervised learning."""

from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
import joblib
from pathlib import Path
import logging

import xgboost as xgb
import lightgbm as lgb
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.svm import OneClassSVM
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    precision_recall_curve, f1_score
)

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.cluster import DBSCAN
from hdbscan import HDBSCAN


logger = logging.getLogger(__name__)


class BaseModel(ABC):
    """Abstract base class for all models."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """Initialize base model."""
        self.name = name
        self.config = config
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
    
    @abstractmethod
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> None:
        """Fit the model."""
        pass
    
    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        pass
    
    def save(self, filepath: Path) -> None:
        """Save model to disk."""
        joblib.dump(self.model, str(filepath))
        logger.info(f"Model {self.name} saved to {filepath}")
    
    def load(self, filepath: Path) -> None:
        """Load model from disk."""
        self.model = joblib.load(str(filepath))
        self.is_trained = True
        logger.info(f"Model {self.name} loaded from {filepath}")


class SupervisedModel(BaseModel):
    """Base class for supervised learning models."""
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """Evaluate model performance."""
        predictions = self.predict(X_test)
        probas = self.predict_proba(X_test) if hasattr(self, 'predict_proba') else None
        
        metrics = {
            "accuracy": (predictions == y_test).mean(),
            "f1_score": f1_score(y_test, predictions, average='weighted', zero_division=0),
        }
        
        if probas is not None:
            try:
                metrics["auc_roc"] = roc_auc_score(y_test, probas[:, 1], multi_class='ovr')
            except:
                pass
        
        logger.info(f"Model {self.name} evaluation metrics: {metrics}")
        return metrics


class XGBoostModel(SupervisedModel):
    """XGBoost classifier for financial crime detection."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("XGBoost", config)
        self.model = xgb.XGBClassifier(
            use_label_encoder=False,
            eval_metric='logloss',
            random_state=config.get('random_state', 42),
            n_jobs=-1,
            **config.get('xgboost_params', {})
        )
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit XGBoost model."""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(
            X_scaled, y,
            eval_set=[(X_scaled, y)],
            early_stopping_rounds=self.config.get('early_stopping_patience', 10),
            verbose=False
        )
        self.is_trained = True
        logger.info("XGBoost model trained successfully")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if not self.is_trained:
            raise ValueError("Model must be fitted before prediction")
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities."""
        if not self.is_trained:
            raise ValueError("Model must be fitted before prediction")
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)


class LightGBMModel(SupervisedModel):
    """LightGBM classifier for financial crime detection."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("LightGBM", config)
        self.model = lgb.LGBMClassifier(
            random_state=config.get('random_state', 42),
            n_jobs=-1,
            **config.get('lightgbm_params', {})
        )
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit LightGBM model."""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y, verbose=False)
        self.is_trained = True
        logger.info("LightGBM model trained successfully")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if not self.is_trained:
            raise ValueError("Model must be fitted before prediction")
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities."""
        if not self.is_trained:
            raise ValueError("Model must be fitted before prediction")
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)


class RandomForestModel(SupervisedModel):
    """Random Forest classifier."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("RandomForest", config)
        self.model = RandomForestClassifier(
            n_estimators=config.get('n_estimators', 100),
            random_state=config.get('random_state', 42),
            n_jobs=-1,
            **config.get('rf_params', {})
        )
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit Random Forest model."""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
        logger.info("Random Forest model trained successfully")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if not self.is_trained:
            raise ValueError("Model must be fitted before prediction")
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities."""
        if not self.is_trained:
            raise ValueError("Model must be fitted before prediction")
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)


class SimpleNeuralNetwork(nn.Module):
    """Simple feedforward neural network for tabular data."""
    
    def __init__(self, input_dim: int, hidden_dims: List[int], num_classes: int = 2):
        super().__init__()
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.2))
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, num_classes))
        self.network = nn.Sequential(*layers)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        return self.network(x)


class NeuralNetworkModel(SupervisedModel):
    """Neural Network classifier using PyTorch."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("NeuralNetwork", config)
        self.input_dim = None
        self.num_classes = 2
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.epochs = config.get('epochs', 100)
        self.batch_size = config.get('batch_size', 32)
        self.learning_rate = config.get('learning_rate', 0.001)
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit neural network model."""
        self.input_dim = X.shape[1]
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = SimpleNeuralNetwork(
            self.input_dim,
            hidden_dims=[128, 64, 32],
            num_classes=self.num_classes
        ).to(self.device)
        
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        criterion = nn.CrossEntropyLoss()
        
        X_tensor = torch.FloatTensor(X_scaled).to(self.device)
        y_tensor = torch.LongTensor(y).to(self.device)
        
        dataset = TensorDataset(X_tensor, y_tensor)
        dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
        
        self.model.train()
        for epoch in range(self.epochs):
            total_loss = 0
            for batch_X, batch_y in dataloader:
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
            
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch+1}/{self.epochs}, Loss: {total_loss/len(dataloader):.4f}")
        
        self.is_trained = True
        logger.info("Neural Network model trained successfully")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if not self.is_trained:
            raise ValueError("Model must be fitted before prediction")
        X_scaled = self.scaler.transform(X)
        self.model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X_scaled).to(self.device)
            outputs = self.model(X_tensor)
            predictions = torch.argmax(outputs, dim=1)
        return predictions.cpu().numpy()


class UnsupervisedModel(BaseModel):
    """Base class for unsupervised learning models."""
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Get cluster labels."""
        pass


class DBSCANModel(UnsupervisedModel):
    """DBSCAN clustering for anomaly detection."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("DBSCAN", config)
        self.model = DBSCAN(
            eps=config.get('eps', 0.5),
            min_samples=config.get('min_samples', 5)
        )
    
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> None:
        """Fit DBSCAN model."""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_trained = True
        logger.info("DBSCAN model trained successfully")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Get cluster labels (-1 for outliers)."""
        if not self.is_trained:
            raise ValueError("Model must be fitted before prediction")
        X_scaled = self.scaler.transform(X)
        # DBSCAN doesn't have a predict method, use fit_predict on new data
        return self.model.fit_predict(X_scaled)


class HDBSCANModel(UnsupervisedModel):
    """HDBSCAN clustering for robust anomaly detection."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("HDBSCAN", config)
        self.model = HDBSCAN(
            min_cluster_size=config.get('min_cluster_size', 5),
            min_samples=config.get('min_samples', 5),
            cluster_selection_epsilon=config.get('cluster_selection_epsilon', 0.0)
        )
    
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> None:
        """Fit HDBSCAN model."""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_trained = True
        logger.info("HDBSCAN model trained successfully")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Get cluster labels."""
        if not self.is_trained:
            raise ValueError("Model must be fitted before prediction")
        X_scaled = self.scaler.transform(X)
        return self.model.fit_predict(X_scaled)


class IsolationForestModel(UnsupervisedModel):
    """Isolation Forest for anomaly detection."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("IsolationForest", config)
        self.model = IsolationForest(
            contamination=config.get('contamination', 0.1),
            random_state=config.get('random_state', 42),
            n_jobs=-1
        )
    
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> None:
        """Fit Isolation Forest model."""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_trained = True
        logger.info("Isolation Forest model trained successfully")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict anomalies (-1 for anomalies, 1 for normal)."""
        if not self.is_trained:
            raise ValueError("Model must be fitted before prediction")
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def anomaly_scores(self, X: np.ndarray) -> np.ndarray:
        """Get anomaly scores."""
        if not self.is_trained:
            raise ValueError("Model must be fitted before prediction")
        X_scaled = self.scaler.transform(X)
        return self.model.score_samples(X_scaled)


class OneClassSVMModel(UnsupervisedModel):
    """One-Class SVM for outlier detection."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("OneClassSVM", config)
        self.model = OneClassSVM(
            nu=config.get('nu', 0.1),
            kernel=config.get('kernel', 'rbf'),
            gamma=config.get('gamma', 'auto')
        )
    
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> None:
        """Fit One-Class SVM model."""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_trained = True
        logger.info("One-Class SVM model trained successfully")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict outliers (-1 for outliers, 1 for inliers)."""
        if not self.is_trained:
            raise ValueError("Model must be fitted before prediction")
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)


class MLRegistry:
    """Registry for managing multiple ML models."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models: Dict[str, BaseModel] = {}
    
    def register_model(self, name: str, model: BaseModel) -> None:
        """Register a model."""
        self.models[name] = model
        logger.info(f"Model {name} registered")
    
    def get_model(self, name: str) -> BaseModel:
        """Get a registered model."""
        if name not in self.models:
            raise ValueError(f"Model {name} not found in registry")
        return self.models[name]
    
    def create_supervised_models(self) -> Dict[str, SupervisedModel]:
        """Create all supervised learning models."""
        models = {
            "xgboost": XGBoostModel(self.config),
            "lightgbm": LightGBMModel(self.config),
            "random_forest": RandomForestModel(self.config),
            "neural_network": NeuralNetworkModel(self.config),
        }
        for name, model in models.items():
            self.register_model(name, model)
        return models
    
    def create_unsupervised_models(self) -> Dict[str, UnsupervisedModel]:
        """Create all unsupervised learning models."""
        models = {
            "dbscan": DBSCANModel(self.config),
            "hdbscan": HDBSCANModel(self.config),
            "isolation_forest": IsolationForestModel(self.config),
            "one_class_svm": OneClassSVMModel(self.config),
        }
        for name, model in models.items():
            self.register_model(name, model)
        return models
    
    def train_ensemble(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train an ensemble of supervised models."""
        results = {}
        for name, model in self.models.items():
            if isinstance(model, SupervisedModel):
                try:
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y, test_size=0.2, random_state=42
                    )
                    model.fit(X_train, y_train)
                    metrics = model.evaluate(X_test, y_test)
                    results[name] = metrics
                    logger.info(f"Model {name} ensemble metrics: {metrics}")
                except Exception as e:
                    logger.error(f"Error training model {name}: {str(e)}")
        return results
