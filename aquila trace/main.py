"""
AquilaTrace Full Platform - Transaction Analysis and Visualization
A comprehensive FastAPI application for detecting anomalies and risks in transaction networks.
"""
import logging
from typing import Optional
from functools import lru_cache
from contextlib import asynccontextmanager

import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from dash import Dash, dcc, html
import dash

from config import settings
from schemas import (
    TransactionAnalysisRequest, 
    AnalysisResponse, 
    SuspiciousTransaction,
    KeyNode,
    HealthCheck,
    ErrorResponse
)
from models.anomaly_detector import AnomalyDetector
from models.risk_scorer import RiskScorer
from analytics.graph_analysis import build_transaction_graph, find_key_nodes, get_graph_statistics
from utils.data_loader import load_transactions, preprocess, get_feature_columns

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Cache Management
# ============================================================================

class ModelCache:
    """Singleton cache for trained models."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.anomaly_detector = None
            cls._instance.risk_scorer = None
            cls._instance.df_cache = None
        return cls._instance
    
    def clear(self):
        """Clear all cached models."""
        self.anomaly_detector = None
        self.risk_scorer = None
        self.df_cache = None
        logger.info("Model cache cleared")


# ============================================================================
# Startup and Shutdown Events
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown.
    """
    logger.info("AquilaTrace Platform starting up...")
    yield
    logger.info("AquilaTrace Platform shutting down...")
    cache = ModelCache()
    cache.clear()


# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title=settings.API_TITLE,
    description="Advanced anomaly detection and risk analysis for transaction networks",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for dashboard integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Core Analysis Functions
# ============================================================================

def analyze_transactions(df: pd.DataFrame) -> tuple:
    """
    Analyze transactions for anomalies and risk scores.
    
    Args:
        df: Preprocessed transaction DataFrame.
        
    Returns:
        Tuple of (df with predictions, anomalies_count).
    """
    cache = ModelCache()
    feature_cols = get_feature_columns()
    
    # Ensure required features exist
    for col in feature_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required feature column: {col}")
    
    features = df[feature_cols].values
    
    # Anomaly Detection
    logger.info("Running anomaly detection...")
    anomaly_model = cache.anomaly_detector or AnomalyDetector()
    anomaly_model.train(features)
    cache.anomaly_detector = anomaly_model if settings.CACHE_MODELS else None
    
    anomalies = anomaly_model.detect(features)
    anomaly_scores = anomaly_model.get_anomaly_scores(features)
    df["anomaly"] = anomalies
    df["anomaly_score"] = anomaly_scores
    
    # Risk Scoring
    logger.info("Running risk scoring...")
    labels = (anomalies == -1).astype(int)  # Use anomalies as labels
    risk_model = cache.risk_scorer or RiskScorer()
    risk_model.train(features, labels)
    cache.risk_scorer = risk_model if settings.CACHE_MODELS else None
    
    risk_scores = risk_model.score(features)
    df["risk_score"] = risk_scores
    
    # Count anomalies
    anomalies_count = (anomalies == -1).sum()
    
    return df, anomalies_count


# ============================================================================
# API Routes
# ============================================================================

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    return HealthCheck(status="healthy")


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: TransactionAnalysisRequest = None):
    """
    Analyze transactions for anomalies and risk scores.
    
    Args:
        request: Optional request with custom file path.
        
    Returns:
        Analysis results including suspicious transactions and high-risk accounts.
    """
    try:
        file_path = request.file_path if request else None
        
        # Load and preprocess data
        logger.info("Loading transaction data...")
        df = load_transactions(file_path)
        df = preprocess(df)
        
        # Analyze transactions
        df, anomalies_count = analyze_transactions(df)
        
        # Build transaction network
        logger.info("Building transaction network...")
        G = build_transaction_graph(df)
        key_nodes = find_key_nodes(G, top_n=10)
        graph_stats = get_graph_statistics(G)
        
        # Extract suspicious transactions
        suspicious = df[df["anomaly"] == -1].copy()
        suspicious_list = []
        
        for _, row in suspicious.iterrows():
            suspicious_list.append(
                SuspiciousTransaction(
                    transaction_id=str(row.get("id", "unknown")),
                    sender=str(row.get("sender", "unknown")),
                    receiver=str(row.get("receiver", "unknown")),
                    amount=float(row.get("amount", 0)),
                    anomaly_score=float(row.get("anomaly_score", 0)),
                    risk_score=float(row.get("risk_score", 0))
                )
            )
        
        # Convert key_nodes to response model
        key_nodes_response = [KeyNode(**node) for node in key_nodes]
        
        return AnalysisResponse(
            total_transactions=len(df),
            total_suspicious=anomalies_count,
            anomalies_percentage=(anomalies_count / len(df) * 100) if len(df) > 0 else 0,
            suspicious_transactions=suspicious_list,
            high_risk_accounts=key_nodes_response,
            graph_stats=graph_stats
        )
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/analyze/quick")
async def quick_analyze(threshold: float = Query(0.5, ge=0, le=1)):
    """
    Get a quick analysis summary.
    
    Args:
        threshold: Risk score threshold for flagging transactions.
        
    Returns:
        Quick analysis summary.
    """
    try:
        df = load_transactions()
        df = preprocess(df)
        df, _ = analyze_transactions(df)
        
        high_risk = df[df["risk_score"] >= threshold]
        
        return {
            "total_transactions": len(df),
            "high_risk_count": len(high_risk),
            "high_risk_percentage": (len(high_risk) / len(df) * 100) if len(df) > 0 else 0,
            "avg_risk_score": float(df["risk_score"].mean()),
            "max_risk_score": float(df["risk_score"].max())
        }
    except Exception as e:
        logger.error(f"Error in quick analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Dash Dashboard Setup
# ============================================================================

def create_dash_app() -> Dash:
    """Create and configure the Dash dashboard."""
    dash_app = Dash(__name__, server=app, url_base_pathname="/dashboard/")
    
    # Create placeholder figure
    fig = create_network_visualization()
    
    dash_app.layout = html.Div([
        html.Div(className="header", children=[
            html.H1("AquilaTrace Intelligence Dashboard", style={"textAlign": "center", "marginBottom": 20}),
            html.P("Advanced Anomaly Detection and Risk Analysis for Transaction Networks", 
                   style={"textAlign": "center", "color": "#666"})
        ], style={"padding": "20px", "backgroundColor": "#f5f5f5"}),
        
        html.Div(className="controls", children=[
            html.Button("Refresh Analysis", id="refresh-btn", n_clicks=0,
                       style={"padding": "10px 20px", "marginRight": "10px"}),
            dcc.Interval(id="update-interval", interval=300000, n_intervals=0)  # 5 min refresh
        ], style={"padding": "20px", "marginBottom": "20px"}),
        
        html.Div(className="metrics-row", children=[
            html.Div(id="metrics-output", style={"padding": "20px"})
        ], style={"marginBottom": "20px"}),
        
        html.Div(className="graph-container", children=[
            dcc.Loading(
                id="loading",
                type="default",
                children=[
                    dcc.Graph(id="network-graph", figure=fig)
                ]
            )
        ], style={"padding": "20px", "backgroundColor": "#ffffff", "marginBottom": "20px"}),
        
        html.Div(className="data-table", children=[
            html.H3("Recent Suspicious Transactions"),
            html.Div(id="suspicious-table", style={"overflowX": "auto"})
        ], style={"padding": "20px"})
    ], style={"fontFamily": "Arial, sans-serif", "padding": "20px"})
    
    # Callbacks for interactivity
    @dash_app.callback(
        [dash.dependencies.Output("network-graph", "figure"),
         dash.dependencies.Output("metrics-output", "children"),
         dash.dependencies.Output("suspicious-table", "children")],
        [dash.dependencies.Input("refresh-btn", "n_clicks"),
         dash.dependencies.Input("update-interval", "n_intervals")]
    )
    def update_dashboard(n_clicks, n_intervals):
        """Update dashboard with latest analysis."""
        try:
            df = load_transactions()
            df = preprocess(df)
            df, anomalies_count = analyze_transactions(df)
            
            G = build_transaction_graph(df)
            fig = create_network_visualization(G, df)
            
            # Metrics display
            metrics = html.Div([
                html.Div([
                    html.H4(f"{len(df)}"),
                    html.P("Total Transactions")
                ], style={"display": "inline-block", "marginRight": "50px"}),
                html.Div([
                    html.H4(f"{anomalies_count}"),
                    html.P("Suspicious Transactions")
                ], style={"display": "inline-block", "marginRight": "50px"}),
                html.Div([
                    html.H4(f"{(anomalies_count/len(df)*100):.1f}%"),
                    html.P("Anomaly Rate")
                ], style={"display": "inline-block"})
            ])
            
            # Suspicious transactions table
            suspicious = df[df["anomaly"] == -1].head(10)
            table = html.Table([
                html.Tr([
                    html.Th("Sender"), html.Th("Receiver"), 
                    html.Th("Amount"), html.Th("Risk Score")
                ])
            ] + [
                html.Tr([
                    html.Td(str(row.get("sender", "?"))),
                    html.Td(str(row.get("receiver", "?"))),
                    html.Td(f"${row.get('amount', 0):.2f}"),
                    html.Td(f"{row.get('risk_score', 0):.2f}")
                ]) for _, row in suspicious.iterrows()
            ], style={"width": "100%", "borderCollapse": "collapse"})
            
            return fig, metrics, table
            
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
            return create_network_visualization(), html.P(f"Error: {str(e)}"), html.P("No data available")
    
    return dash_app


def create_network_visualization(G: Optional[nx.DiGraph] = None, df: Optional[pd.DataFrame] = None) -> go.Figure:
    """
    Create an interactive 3D network visualization.
    
    Args:
        G: NetworkX graph object. If None, creates an empty figure.
        df: Transaction DataFrame for coloring nodes by risk.
        
    Returns:
        Plotly figure object.
    """
    if G is None or G.number_of_nodes() == 0:
        return go.Figure(
            data=[],
            layout=go.Layout(
                title="Transaction Network (No data available)",
                margin=dict(l=0, r=0, b=0, t=0)
            )
        )
    
    try:
        pos = nx.spring_layout(G, dim=3, k=0.5, iterations=50)
        
        # Create edge traces
        edge_x, edge_y, edge_z = [], [], []
        for edge in G.edges():
            x0, y0, z0 = pos[edge[0]]
            x1, y1, z1 = pos[edge[1]]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]
            edge_z += [z0, z1, None]
        
        edge_trace = go.Scatter3d(
            x=edge_x, y=edge_y, z=edge_z,
            mode='lines',
            line=dict(width=1, color='rgba(125,125,125,0.5)'),
            hoverinfo='none'
        )
        
        # Create node traces with risk coloring
        node_x, node_y, node_z = [], [], []
        node_colors = []
        node_text = []
        
        for node in G.nodes():
            x, y, z = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_z.append(z)
            
            # Color by risk if DataFrame provided
            if df is not None and node in df.get("sender", []).values:
                risk = df[df["sender"] == node]["risk_score"].mean()
                node_colors.append(risk)
            else:
                node_colors.append(0.5)
            
            node_text.append(str(node))
        
        node_trace = go.Scatter3d(
            x=node_x, y=node_y, z=node_z,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            textfont=dict(size=8),
            marker=dict(
                size=5,
                color=node_colors,
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="Risk Score"),
                opacity=0.8
            ),
            hoverinfo='text',
            hovertext=node_text
        )
        
        fig = go.Figure(data=[edge_trace, node_trace])
        fig.update_layout(
            title="AquilaTrace 3D Intelligence Network",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=40),
            scene=dict(
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                zaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating network visualization: {e}")
        return go.Figure().add_annotation(text=f"Error: {str(e)}")


# Create and mount dashboard
dash_app = create_dash_app()
app.mount("/dashboard", WSGIMiddleware(dash_app.server))


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting AquilaTrace on {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level="info" if not settings.DEBUG else "debug"
    )
