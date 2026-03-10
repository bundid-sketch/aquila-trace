"""Data pipeline and feature engineering for AquilaTrace."""

from typing import Dict, List, Tuple, Optional, Any, Union
import numpy as np
import pandas as pd
import logging
from abc import ABC, abstractmethod
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.feature_extraction.text import TfidfVectorizer
import featuretools as ft


logger = logging.getLogger(__name__)


class DataValidator:
    """Validate and clean financial data."""
    
    @staticmethod
    def validate_transaction_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate transaction dataframe.
        
        Args:
            df: Transaction dataframe
            
        Returns:
            (is_valid, list of issues found)
        """
        issues = []
        
        required_columns = ['timestamp', 'source', 'destination', 'amount']
        for col in required_columns:
            if col not in df.columns:
                issues.append(f"Missing required column: {col}")
        
        if 'timestamp' in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                issues.append("timestamp column is not datetime type")
        
        if 'amount' in df.columns:
            if df['amount'].isnull().any():
                issues.append(f"Found {df['amount'].isnull().sum()} null amounts")
            if (df['amount'] < 0).any():
                issues.append("Found negative amounts")
        
        if df.isnull().any().any():
            null_counts = df.isnull().sum()
            issues.append(f"Found null values: {null_counts[null_counts > 0].to_dict()}")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare transaction data."""
        df = df.copy()
        
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle nulls
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        
        # Remove outliers (IQR method)
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            df = df[(df[col] >= Q1 - 1.5 * IQR) & (df[col] <= Q3 + 1.5 * IQR)]
        
        logger.info(f"Cleaned transaction data: {df.shape[0]} records")
        return df


class FeatureEngineer:
    """Engineer financial features from raw data."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_dict = {}
    
    def extract_temporal_features(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Extract time-based features."""
        df = transactions_df.copy()
        
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['month'] = df['timestamp'].dt.month
            df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        return df
    
    def extract_transaction_features(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Extract transaction-level features."""
        df = transactions_df.copy()
        
        # Amount-based features
        df['amount_log'] = np.log1p(df['amount'])
        df['amount_zscore'] = (df['amount'] - df['amount'].mean()) / df['amount'].std()
        
        # Direction features
        df['is_circular'] = (df['source'] == df['destination']).astype(int)
        
        return df
    
    def extract_entity_features(self, transactions_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Extract entity-level aggregated features."""
        entity_features = {}
        
        # Source entity features
        source_features = transactions_df.groupby('source').agg({
            'amount': ['sum', 'mean', 'std', 'count', 'min', 'max'],
            'destination': 'nunique',
        }).fillna(0)
        
        source_features.columns = ['_'.join(col).strip() for col in source_features.columns]
        source_features.columns = [f'source_{col}' for col in source_features.columns]
        entity_features['source'] = source_features
        
        # Destination entity features
        dest_features = transactions_df.groupby('destination').agg({
            'amount': ['sum', 'mean', 'std', 'count', 'min', 'max'],
            'source': 'nunique',
        }).fillna(0)
        
        dest_features.columns = ['_'.join(col).strip() for col in dest_features.columns]
        dest_features.columns = [f'dest_{col}' for col in dest_features.columns]
        entity_features['destination'] = dest_features
        
        return entity_features
    
    def extract_network_features(self, transactions_df: pd.DataFrame) -> Dict[str, float]:
        """Extract network structure features."""
        features = {}
        
        # Network density
        unique_sources = transactions_df['source'].nunique()
        unique_dests = transactions_df['destination'].nunique()
        possible_edges = unique_sources * unique_dests
        actual_edges = len(transactions_df)
        
        features['network_density'] = actual_edges / possible_edges if possible_edges > 0 else 0
        
        # Network size
        features['unique_sources'] = unique_sources
        features['unique_destinations'] = unique_dests
        features['total_transactions'] = len(transactions_df)
        
        # Average transaction size
        features['avg_transaction_amount'] = transactions_df['amount'].mean()
        features['median_transaction_amount'] = transactions_df['amount'].median()
        features['std_transaction_amount'] = transactions_df['amount'].std()
        
        return features
    
    def extract_behavioral_features(self, entity_id: str, 
                                   transactions_df: pd.DataFrame) -> Dict[str, Any]:
        """Extract behavioral features for specific entity."""
        entity_txs = transactions_df[
            (transactions_df['source'] == entity_id) | 
            (transactions_df['destination'] == entity_id)
        ]
        
        if len(entity_txs) == 0:
            return {}
        
        features = {
            'transaction_frequency': len(entity_txs),
            'avg_amount': entity_txs['amount'].mean(),
            'total_volume': entity_txs['amount'].sum(),
            'unique_counterparties': len(
                set(entity_txs[entity_txs['source'] == entity_id]['destination'].unique()) |
                set(entity_txs[entity_txs['destination'] == entity_id]['source'].unique())
            ),
            'incoming_ratio': len(entity_txs[entity_txs['destination'] == entity_id]) / len(entity_txs) if len(entity_txs) > 0 else 0,
        }
        
        return features


class NLPFeatureExtractor:
    """Extract features from text data."""
    
    def __init__(self, max_features: int = 100):
        self.vectorizer = TfidfVectorizer(max_features=max_features, lowercase=True)
        self.fitted = False
    
    def extract_text_features(self, texts: List[str]) -> np.ndarray:
        """Extract TF-IDF features from texts."""
        if not self.fitted:
            features = self.vectorizer.fit_transform(texts)
            self.fitted = True
        else:
            features = self.vectorizer.transform(texts)
        
        return features.toarray()
    
    def extract_keyword_features(self, texts: List[str]) -> Dict[str, float]:
        """Extract keyword-based fraud indicators."""
        suspicious_keywords = {
            'urgent': ['urgent', 'immediate', 'rush', 'quickly'],
            'money_related': ['transfer', 'payment', 'deposit', 'withdrawal', 'crypto'],
            'deceptive': ['verify', 'confirm', 'update', 'click', 'confirm identity'],
            'threat': ['risk', 'problem', 'issue', 'suspended', 'limited'],
        }
        
        features = {category: 0.0 for category in suspicious_keywords}
        
        for text in texts:
            text_lower = text.lower()
            for category, keywords in suspicious_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    features[category] += 1
        
        # Normalize
        total_texts = len(texts) if texts else 1
        for key in features:
            features[key] /= total_texts
        
        return features


class FeatureNormalizer:
    """Normalize numerical features."""
    
    def __init__(self, method: str = "standard"):
        self.method = method
        
        if method == "standard":
            self.scaler = StandardScaler()
        elif method == "minmax":
            self.scaler = MinMaxScaler()
        elif method == "robust":
            self.scaler = RobustScaler()
        else:
            raise ValueError(f"Unknown normalization method: {method}")
    
    def fit_transform(self, features: np.ndarray) -> np.ndarray:
        """Fit and transform features."""
        return self.scaler.fit_transform(features)
    
    def transform(self, features: np.ndarray) -> np.ndarray:
        """Transform features using fitted scaler."""
        return self.scaler.transform(features)


class DataPipeline:
    """End-to-end data pipeline orchestration."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.validator = DataValidator()
        self.feature_engineer = FeatureEngineer()
        self.nlp_extractor = NLPFeatureExtractor()
        self.normalizer = FeatureNormalizer(method="standard")
        self.processed_data = {}
        logger.info("Initialized Data Pipeline")
    
    def process_transactions(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Process and engineer transaction features."""
        # Validate
        is_valid, issues = self.validator.validate_transaction_data(transactions_df)
        if not is_valid:
            logger.warning(f"Data validation issues: {issues}")
        
        # Clean
        df = self.validator.clean_transactions(transactions_df)
        
        # Extract features
        df = self.feature_engineer.extract_temporal_features(df)
        df = self.feature_engineer.extract_transaction_features(df)
        
        self.processed_data['transactions'] = df
        logger.info(f"Processed transactions: {df.shape}")
        return df
    
    def process_texts(self, texts: List[str], 
                     extract_embeddings: bool = True) -> Dict[str, Any]:
        """Process text data and extract NLP features."""
        result = {
            'texts': texts,
            'keyword_features': self.nlp_extractor.extract_keyword_features(texts),
        }
        
        if extract_embeddings:
            result['tfidf_features'] = self.nlp_extractor.extract_text_features(texts)
        
        self.processed_data['text'] = result
        logger.info(f"Processed {len(texts)} texts")
        return result
    
    def create_feature_matrix(self, transactions_df: pd.DataFrame,
                             feature_columns: Optional[List[str]] = None) -> Tuple[np.ndarray, List[str]]:
        """Create normalized feature matrix for ML models."""
        processed_df = self.process_transactions(transactions_df)
        
        # Select numerical features
        if feature_columns is None:
            feature_columns = processed_df.select_dtypes(include=[np.number]).columns.tolist()
            # Remove redundant time columns
            feature_columns = [col for col in feature_columns if col not in ['timestamp']]
        
        X = processed_df[feature_columns].values
        
        # Normalize
        X_normalized = self.normalizer.fit_transform(X)
        
        logger.info(f"Created feature matrix: {X_normalized.shape}")
        return X_normalized, feature_columns
    
    def get_entity_profile(self, entity_id: str, 
                          transactions_df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive behavioral profile for entity."""
        profile = {
            'entity_id': entity_id,
            'behavioral_features': self.feature_engineer.extract_behavioral_features(
                entity_id, transactions_df
            ),
            'network_features': self.feature_engineer.extract_network_features(
                transactions_df
            ),
        }
        
        return profile
