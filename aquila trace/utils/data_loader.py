"""Data loading and preprocessing utilities."""
import logging
from typing import Optional

import pandas as pd
import numpy as np

from config import settings

logger = logging.getLogger(__name__)


def load_transactions(file_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load transaction data from CSV file.
    
    Args:
        file_path: Path to CSV file. Uses default from config if not provided.
        
    Returns:
        DataFrame with transaction data.
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file is empty or malformed.
    """
    file_path = file_path or settings.TRANSACTIONS_FILE
    
    try:
        df = pd.read_csv(file_path)
        
        if df.empty:
            raise ValueError(f"Transaction file {file_path} is empty")
            
        logger.info(f"Loaded {len(df)} transactions from {file_path}")
        return df
        
    except FileNotFoundError:
        logger.error(f"Transaction file not found: {file_path}")
        raise
    except pd.errors.ParserError as e:
        logger.error(f"Error parsing CSV file: {e}")
        raise ValueError(f"Malformed CSV file: {e}")


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess transaction data for analysis.
    
    Args:
        df: Raw transaction DataFrame.
        
    Returns:
        Preprocessed DataFrame with additional features.
    """
    df = df.copy()
    
    # Create log-transformed amount features
    if "amount" in df.columns:
        df["log_amount"] = np.log1p(df["amount"].abs())
    
    # Create cross-border flag
    if "sender_country" in df.columns and "receiver_country" in df.columns:
        df["cross_border"] = (df["sender_country"] != df["receiver_country"]).astype(int)
    else:
        df["cross_border"] = 0
    
    # Handle missing values
    df = df.fillna(0)
    
    logger.info(f"Preprocessed {len(df)} transactions")
    return df


def get_feature_columns() -> list[str]:
    """Get list of feature columns for model training."""
    return ["log_amount", "cross_border"]
