"""Configuration management for AquilaTrace platform."""

import os
import json
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from pathlib import Path
import yaml


@dataclass
class MLConfig:
    """Machine Learning configuration."""
    supervised_models: list = field(default_factory=lambda: [
        "xgboost", "lightgbm", "random_forest", "logistic_regression", "neural_network"
    ])
    unsupervised_models: list = field(default_factory=lambda: [
        "dbscan", "hdbscan", "autoencoder", "isolation_forest", "one_class_svm"
    ])
    feature_selection_method: str = "mutual_information"
    cross_validation_folds: int = 5
    test_split_ratio: float = 0.2
    random_state: int = 42
    batch_size: int = 32
    learning_rate: float = 0.001
    epochs: int = 100
    early_stopping_patience: int = 10


@dataclass
class GraphConfig:
    """Graph Neural Network configuration."""
    gnn_models: list = field(default_factory=lambda: ["gcn", "gat", "rgcn", "temporal_gnn"])
    embedding_dim: int = 256
    num_layers: int = 3
    dropout_rate: float = 0.2
    aggregation: str = "mean"
    use_attention: bool = True
    temporal_window_size: int = 30  # days


@dataclass
class NLPConfig:
    """Natural Language Processing configuration."""
    transformer_models: list = field(default_factory=lambda: [
        "bert", "roberta", "distilbert", "finbert", "sbert"
    ])
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    max_sequence_length: int = 512
    batch_size: int = 32
    num_topics: int = 50
    min_language_confidence: float = 0.7
    supported_languages: list = field(default_factory=lambda: [
        "en", "ar", "fr", "sw", "ha", "yo", "ig"
    ])


@dataclass
class BlockchainConfig:
    """Blockchain Analytics configuration."""
    supported_chains: list = field(default_factory=lambda: [
        "bitcoin", "ethereum", "ripple", "monero"
    ])
    clustering_algorithm: str = "dbscan"
    fingerprint_feature_count: int = 100
    mixer_detection_threshold: float = 0.85
    address_reuse_detection: bool = True
    transaction_timeout_minutes: int = 60


@dataclass
class DatabaseConfig:
    """Database configuration."""
    postgres_url: str = "postgresql://user:password@localhost/aquila_trace"
    redis_url: str = "redis://localhost:6379/0"
    mongodb_url: str = "mongodb://localhost:27017"
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False


@dataclass
class APIConfig:
    """API Server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = False
    enable_cors: bool = True
    enable_auth: bool = True
    jwt_secret: str = "your-secret-key"
    api_version: str = "v1"


@dataclass
class Config:
    """Main configuration class for AquilaTrace."""
    
    # Environment
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Core configurations
    ml_config: MLConfig = field(default_factory=MLConfig)
    graph_config: GraphConfig = field(default_factory=GraphConfig)
    nlp_config: NLPConfig = field(default_factory=NLPConfig)
    blockchain_config: BlockchainConfig = field(default_factory=BlockchainConfig)
    database_config: DatabaseConfig = field(default_factory=DatabaseConfig)
    api_config: APIConfig = field(default_factory=APIConfig)
    
    # Paths
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)
    data_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent / "data")
    models_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent / "models")
    logs_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent / "logs")
    
    # Feature flags
    enable_anomaly_detection: bool = True
    enable_entity_linking: bool = True
    enable_link_prediction: bool = True
    enable_blockchain_analysis: bool = True
    enable_nlp_analysis: bool = True
    
    def __post_init__(self):
        """Create necessary directories."""
        for directory in [self.data_dir, self.models_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        config = cls()
        
        # Override from environment
        config.environment = os.getenv("AQUILA_ENV", config.environment)
        config.debug = os.getenv("AQUILA_DEBUG", "").lower() in ["true", "1", "yes"]
        config.log_level = os.getenv("AQUILA_LOG_LEVEL", config.log_level)
        
        # Database configuration
        config.database_config.postgres_url = os.getenv(
            "AQUILA_POSTGRES_URL",
            config.database_config.postgres_url
        )
        config.database_config.redis_url = os.getenv(
            "AQUILA_REDIS_URL",
            config.database_config.redis_url
        )
        config.database_config.mongodb_url = os.getenv(
            "AQUILA_MONGODB_URL",
            config.database_config.mongodb_url
        )
        
        # API configuration
        config.api_config.host = os.getenv("AQUILA_API_HOST", config.api_config.host)
        config.api_config.port = int(os.getenv("AQUILA_API_PORT", config.api_config.port))
        config.api_config.jwt_secret = os.getenv("AQUILA_JWT_SECRET", config.api_config.jwt_secret)
        
        return config
    
    @classmethod
    def from_yaml(cls, filepath: str) -> "Config":
        """Load configuration from YAML file."""
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Load configuration from dictionary."""
        config = cls()
        
        if "ml" in data:
            config.ml_config = MLConfig(**data["ml"])
        if "graph" in data:
            config.graph_config = GraphConfig(**data["graph"])
        if "nlp" in data:
            config.nlp_config = NLPConfig(**data["nlp"])
        if "blockchain" in data:
            config.blockchain_config = BlockchainConfig(**data["blockchain"])
        if "database" in data:
            config.database_config = DatabaseConfig(**data["database"])
        if "api" in data:
            config.api_config = APIConfig(**data["api"])
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "environment": self.environment,
            "debug": self.debug,
            "log_level": self.log_level,
            "ml": self.ml_config.__dict__,
            "graph": self.graph_config.__dict__,
            "nlp": self.nlp_config.__dict__,
            "blockchain": self.blockchain_config.__dict__,
            "database": self.database_config.__dict__,
            "api": self.api_config.__dict__,
        }
    
    def to_yaml(self, filepath: str) -> None:
        """Save configuration to YAML file."""
        with open(filepath, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)
