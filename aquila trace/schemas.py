"""Pydantic schemas for request/response validation."""
from typing import List, Optional
from pydantic import BaseModel, Field


class TransactionAnalysisRequest(BaseModel):
    """Request model for transaction analysis."""
    file_path: Optional[str] = Field(default=None, description="Custom path to transactions CSV file")


class SuspiciousTransaction(BaseModel):
    """Model for a suspicious transaction."""
    transaction_id: Optional[str] = None
    sender: str
    receiver: str
    amount: float
    anomaly_score: float
    risk_score: float


class KeyNode(BaseModel):
    """Model for a key node in the transaction network."""
    node: str
    in_degree: int
    out_degree: int
    betweenness: float
    combined_score: float


class AnalysisResponse(BaseModel):
    """Response model for transaction analysis."""
    total_transactions: int
    total_suspicious: int
    anomalies_percentage: float
    suspicious_transactions: List[SuspiciousTransaction]
    high_risk_accounts: List[KeyNode]
    graph_stats: dict


class HealthCheck(BaseModel):
    """Health check response."""
    status: str
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
