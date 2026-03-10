"""Configuration management for AquilaTrace application."""
import os
from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings."""
    
    # API Configuration
    API_TITLE: str = "AquilaTrace Full Platform"
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "10000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Data Configuration
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    TRANSACTIONS_FILE: str = os.path.join(DATA_DIR, "transactions.csv")
    
    # Model Configuration
    ANOMALY_DETECTION_THRESHOLD: float = -1.0  # Isolation Forest outlier threshold
    RISK_SCORE_THRESHOLD: float = 0.7
    
    # Cache Configuration
    CACHE_MODELS: bool = True
    MODEL_CACHE_TTL: int = 3600  # 1 hour in seconds


settings = Settings()
