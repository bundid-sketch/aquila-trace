"""REST API and Orchestration for AquilaTrace platform."""

from typing import Dict, List, Optional, Any
import logging
from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
import asyncio
from datetime import datetime
import json

from ..core.config import Config
from ..core.logger import setup_logging
from ..ml import MLRegistry
from ..graph import FinancialNetworkAnalyzer, GCNModel
from ..nlp import CyberIntelligencePipeline
from ..blockchain import BlockchainAnalyzer
from ..data import DataPipeline
import pandas as pd


logger = logging.getLogger(__name__)


# Pydantic models for API
class TransactionData(BaseModel):
    """Transaction data model."""
    timestamp: str
    source: str
    destination: str
    amount: float
    currency: str = "USD"
    transaction_id: str = ""


class EntityData(BaseModel):
    """Entity data model."""
    entity_id: str
    entity_type: str  # person, organization, wallet, account
    attributes: Dict[str, Any] = {}


class AnalysisRequest(BaseModel):
    """Generic analysis request."""
    data_type: str  # transaction, entity, text, blockchain
    data: Dict[str, Any]
    analysis_type: str  # anomaly, risk_score, classification


class TextAnalysisRequest(BaseModel):
    """Text analysis request."""
    texts: List[str]
    analysis_type: str = "comprehensive"


class BlockchainAnalysisRequest(BaseModel):
    """Blockchain analysis request."""
    addresses: List[str]
    chain: str = "bitcoin"
    analysis_type: str  # address_analysis, flow_analysis, cluster_detection


class AnomalyDetectionResponse(BaseModel):
    """Response for anomaly detection."""
    anomalies: List[Dict[str, Any]]
    anomaly_count: int
    contamination_rate: float


class RiskAssessmentResponse(BaseModel):
    """Response for risk assessment."""
    entity_id: str
    risk_score: float
    risk_level: str  # low, medium, high, critical
    risk_factors: List[str]
    recommendation: str


class ClassificationResponse(BaseModel):
    """Response for classification."""
    predictions: List[Dict[str, Any]]
    model_name: str
    confidence_scores: List[float]


class AquilaTraceOrchestrator:
    """Main orchestration engine for AquilaTrace."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.from_env()
        self.ml_registry = MLRegistry(self.config.ml_config.__dict__)
        self.data_pipeline = DataPipeline(self.config.ml_config.__dict__)
        self.nlp_pipeline = CyberIntelligencePipeline(self.config.nlp_config.__dict__)
        self.blockchain_analyzer = BlockchainAnalyzer(self.config.blockchain_config.__dict__)
        
        # Initialize GNN
        self.gnn_model = GCNModel(
            input_dim=self.config.graph_config.embedding_dim,
            hidden_dim=self.config.graph_config.embedding_dim,
            output_dim=2,
            num_layers=self.config.graph_config.num_layers
        )
        self.financial_network_analyzer = FinancialNetworkAnalyzer(self.gnn_model)
        
        logger.info("Initialized AquilaTrace Orchestrator")
    
    def analyze_transaction(self, transaction: TransactionData) -> Dict[str, Any]:
        """Analyze single transaction for anomalies and risk."""
        # Create simple dataframe for feature extraction
        df = pd.DataFrame([{
            'timestamp': transaction.timestamp,
            'source': transaction.source,
            'destination': transaction.destination,
            'amount': transaction.amount,
        }])
        
        # Extract features
        features, feature_names = self.data_pipeline.create_feature_matrix(df)
        
        # Get anomaly scores
        iso_forest = self.ml_registry.models.get('isolation_forest')
        if iso_forest is None:
            iso_forest = self.ml_registry.create_unsupervised_models()['isolation_forest']
        
        anomaly_prediction = iso_forest.predict(features)
        anomaly_score = abs(iso_forest.anomaly_scores(features)[0])
        
        return {
            'transaction_id': transaction.transaction_id,
            'is_anomaly': int(anomaly_prediction[0]) == -1,
            'anomaly_score': float(anomaly_score),
            'risk_level': 'high' if anomaly_score > 0.7 else 'medium' if anomaly_score > 0.4 else 'low',
        }
    
    def analyze_entity_risk(self, entity_id: str, 
                           transactions_df: pd.DataFrame) -> RiskAssessmentResponse:
        """Analyze risk profile of entity."""
        # Get entity profile
        profile = self.data_pipeline.get_entity_profile(entity_id, transactions_df)
        
        # Calculate risk score
        risk_score = 0.0
        risk_factors = []
        
        # High transaction frequency
        if profile['behavioral_features'].get('transaction_frequency', 0) > 100:
            risk_score += 0.2
            risk_factors.append("High transaction frequency")
        
        # High volume
        if profile['behavioral_features'].get('total_volume', 0) > 1000000:
            risk_score += 0.2
            risk_factors.append("High transaction volume")
        
        # Low incoming ratio (mostly outgoing - suspicious)
        incoming_ratio = profile['behavioral_features'].get('incoming_ratio', 0)
        if incoming_ratio < 0.2:
            risk_score += 0.3
            risk_factors.append("Low incoming transaction ratio")
        
        risk_score = min(risk_score, 1.0)
        
        if risk_score >= 0.7:
            risk_level = "critical"
            recommendation = "Block transactions, escalate to compliance"
        elif risk_score >= 0.5:
            risk_level = "high"
            recommendation = "Enhanced monitoring and verification required"
        elif risk_score >= 0.3:
            risk_level = "medium"
            recommendation = "Monitor for suspicious patterns"
        else:
            risk_level = "low"
            recommendation = "Standard monitoring"
        
        return RiskAssessmentResponse(
            entity_id=entity_id,
            risk_score=float(risk_score),
            risk_level=risk_level,
            risk_factors=risk_factors,
            recommendation=recommendation
        )
    
    def analyze_text_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze batch of texts for financial crime indicators."""
        results = []
        for text in texts:
            analysis = self.nlp_pipeline.analyze_text(text)
            results.append(analysis)
        
        return results
    
    def analyze_blockchain_address(self, address: str, chain: str = "bitcoin") -> Dict[str, Any]:
        """Comprehensive blockchain address analysis."""
        return self.blockchain_analyzer.analyze_address(address)
    
    def detect_network_anomalies(self, transactions_df: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomalies in transaction network."""
        # Create features
        features, features_names = self.data_pipeline.create_feature_matrix(transactions_df)
        
        # Use ensemble of anomaly detectors
        hdbscan_model = self.ml_registry.models.get('hdbscan')
        if hdbscan_model is None:
            hdbscan_model = self.ml_registry.create_unsupervised_models()['hdbscan']
        
        clusters = hdbscan_model.predict(features)
        anomalies = transactions_df[clusters == -1]
        
        return {
            'total_transactions': len(transactions_df),
            'anomalies_detected': len(anomalies),
            'anomaly_percentage': float(len(anomalies) / len(transactions_df) * 100) if len(transactions_df) > 0 else 0,
            'anomalous_record_ids': anomalies.index.tolist() if hasattr(anomalies, 'index') else [],
        }


def create_app(config: Optional[Config] = None) -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="AquilaTrace API",
        description="Advanced Financial Crime and Terrorism Financing Detection Platform",
        version="1.0.0"
    )
    
    config = config or Config.from_env()
    logger.info(f"Starting AquilaTrace API in {config.environment} mode")
    
    # Initialize orchestrator
    orchestrator = AquilaTraceOrchestrator(config)
    
    # API Key validation (simple example)
    async def verify_api_key(x_api_key: str = Header(...)):
        if config.environment == "development":
            return True
        if x_api_key != config.api_config.jwt_secret:
            raise HTTPException(status_code=401, detail="Invalid API Key")
        return True
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "AquilaTrace",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }
    
    @app.post("/api/v1/transaction/analyze")
    async def analyze_transaction(
        transaction: TransactionData,
        api_key_valid: bool = Depends(verify_api_key)
    ):
        """Analyze single transaction."""
        try:
            result = orchestrator.analyze_transaction(transaction)
            return JSONResponse(
                status_code=200,
                content=result
            )
        except Exception as e:
            logger.error(f"Error analyzing transaction: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/entity/risk-assessment")
    async def assess_entity_risk(
        entity_id: str,
        transactions: List[TransactionData],
        api_key_valid: bool = Depends(verify_api_key)
    ):
        """Assess risk profile of entity."""
        try:
            # Convert to dataframe
            tx_list = [
                {
                    'timestamp': tx.timestamp,
                    'source': tx.source,
                    'destination': tx.destination,
                    'amount': tx.amount,
                }
                for tx in transactions
            ]
            df = pd.DataFrame(tx_list)
            
            result = orchestrator.analyze_entity_risk(entity_id, df)
            return JSONResponse(
                status_code=200,
                content=json.loads(result.model_dump_json())
            )
        except Exception as e:
            logger.error(f"Error assessing entity risk: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/text/analyze")
    async def analyze_texts(
        request: TextAnalysisRequest,
        api_key_valid: bool = Depends(verify_api_key)
    ):
        """Analyze texts for financial crime indicators."""
        try:
            results = orchestrator.analyze_text_batch(request.texts)
            return JSONResponse(
                status_code=200,
                content={"analyses": results}
            )
        except Exception as e:
            logger.error(f"Error analyzing texts: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/blockchain/address-analysis")
    async def analyze_blockchain_address(
        request: BlockchainAnalysisRequest,
        api_key_valid: bool = Depends(verify_api_key)
    ):
        """Analyze blockchain address."""
        try:
            results = []
            for address in request.addresses:
                result = orchestrator.analyze_blockchain_address(address, request.chain)
                results.append(result)
            
            return JSONResponse(
                status_code=200,
                content={"addresses": results}
            )
        except Exception as e:
            logger.error(f"Error analyzing blockchain address: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/anomalies/detect")
    async def detect_anomalies(
        transactions: List[TransactionData],
        api_key_valid: bool = Depends(verify_api_key)
    ):
        """Detect anomalies in transaction data."""
        try:
            # Convert to dataframe
            tx_list = [
                {
                    'timestamp': tx.timestamp,
                    'source': tx.source,
                    'destination': tx.destination,
                    'amount': tx.amount,
                }
                for tx in transactions
            ]
            df = pd.DataFrame(tx_list)
            
            result = orchestrator.detect_network_anomalies(df)
            return JSONResponse(
                status_code=200,
                content=result
            )
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/batch-analysis")
    async def batch_analysis(
        request: AnalysisRequest,
        background_tasks: BackgroundTasks,
        api_key_valid: bool = Depends(verify_api_key)
    ):
        """Submit batch analysis job."""
        # In production, use job queue (Celery, RQ, etc.)
        logger.info(f"Batch analysis job submitted: {request.data_type}")
        
        return JSONResponse(
            status_code=202,
            content={
                "status": "accepted",
                "job_id": "job_" + str(datetime.now().timestamp()).replace(".", ""),
                "message": "Batch analysis job queued for processing"
            }
        )
    
    @app.get("/api/v1/config")
    async def get_config(api_key_valid: bool = Depends(verify_api_key)):
        """Get platform configuration (admin only)."""
        if config.environment != "development":
            raise HTTPException(status_code=403, detail="Not available in production")
        
        return JSONResponse(
            status_code=200,
            content=config.to_dict()
        )
    
    return app


if __name__ == "__main__":
    config = Config.from_env()
    app = create_app(config)
    
    uvicorn.run(
        app,
        host=config.api_config.host,
        port=config.api_config.port,
        workers=config.api_config.workers,
        log_level=config.log_level.lower()
    )
