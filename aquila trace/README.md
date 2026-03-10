# AquilaTrace Full Platform

Advanced anomaly detection and risk analysis platform for transaction networks using machine learning and network analysis.

## Features

✨ **Core Capabilities**
- **Anomaly Detection**: Isolation Forest-based detection of suspicious transactions
- **Risk Scoring**: Random Forest classifier for transaction risk assessment
- **Network Analysis**: Graph-based analysis to identify key actors and patterns
- **Interactive Dashboard**: Real-time 3D visualization of transaction networks
- **REST API**: Comprehensive API for integration and automation
- **Caching**: Intelligent model caching for performance optimization

## Project Structure

```
aquila-trace/
├── main.py                      # FastAPI application entry point
├── config.py                    # Configuration management
├── schemas.py                   # Pydantic request/response models
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
│
├── models/                      # Machine learning models
│   ├── anomaly_detector.py      # Isolation Forest anomaly detection
│   └── risk_scorer.py           # Random Forest risk scoring
│
├── analytics/                   # Network and transaction analysis
│   └── graph_analysis.py        # NetworkX-based graph analysis
│
├── utils/                       # Utility functions
│   └── data_loader.py           # Data loading and preprocessing
│
└── data/                        # Data directory
    └── transactions.csv         # Transaction dataset
```

## Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Setup

1. **Clone or download the project**
2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # or
   source venv/bin/activate      # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings if needed
   ```

5. **Prepare data**
   - Place your transactions CSV file in the `data/` directory
   - Expected columns: `sender`, `receiver`, `amount`, `sender_country`, `receiver_country`

## Usage

### Running the Application

```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 10000 --reload
```

The application will be available at:
- **API**: http://localhost:10000
- **Dashboard**: http://localhost:10000/dashboard
- **API Docs**: http://localhost:10000/docs

### API Endpoints

#### Health Check
```
GET /health
```
Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

#### Full Analysis
```
POST /analyze
```
Perform comprehensive transaction analysis including anomaly detection and risk scoring.

**Request (Optional):**
```json
{
  "file_path": "data/transactions.csv"
}
```

**Response:**
```json
{
  "total_transactions": 1000,
  "total_suspicious": 45,
  "anomalies_percentage": 4.5,
  "suspicious_transactions": [
    {
      "transaction_id": "TXN001",
      "sender": "ACC123",
      "receiver": "ACC456",
      "amount": 50000.0,
      "anomaly_score": -2.34,
      "risk_score": 0.85
    }
  ],
  "high_risk_accounts": [
    {
      "node": "ACC789",
      "in_degree": 125,
      "out_degree": 89,
      "betweenness": 0.45,
      "combined_score": 87.3
    }
  ],
  "graph_stats": {
    "num_nodes": 542,
    "num_edges": 1203,
    "density": 0.0082,
    "is_connected": false,
    "num_weakly_connected_components": 12
  }
}
```

#### Quick Analysis
```
GET /analyze/quick?threshold=0.5
```
Get a summary analysis without full details.

**Query Parameters:**
- `threshold` (float, 0-1): Risk score threshold for flagging transactions

**Response:**
```json
{
  "total_transactions": 1000,
  "high_risk_count": 234,
  "high_risk_percentage": 23.4,
  "avg_risk_score": 0.42,
  "max_risk_score": 0.98
}
```

### Dashboard

Navigate to http://localhost:10000/dashboard for an interactive interface featuring:
- Real-time 3D transaction network visualization
- Key metrics and statistics
- Recent suspicious transactions list
- Auto-refresh functionality

## Configuration

Configure the application via environment variables in `.env`:

```env
# API Settings
API_HOST=0.0.0.0
API_PORT=10000
DEBUG=False

# Data
DATA_DIR=data
TRANSACTIONS_FILE=data/transactions.csv

# Models
ANOMALY_DETECTION_THRESHOLD=-1.0
RISK_SCORE_THRESHOLD=0.7

# Caching
CACHE_MODELS=True
MODEL_CACHE_TTL=3600
```

## Data Requirements

### Input CSV Format

Your transactions CSV should contain:

| Column | Type | Description |
|--------|------|-------------|
| sender | string | Source account identifier |
| receiver | string | Destination account identifier |
| amount | float | Transaction amount |
| sender_country | string | Sender's country code (optional) |
| receiver_country | string | Receiver's country code (optional) |
| id | string | Transaction ID (optional) |

### Example
```csv
sender,receiver,amount,sender_country,receiver_country
ACC001,ACC002,1000.50,US,GB
ACC003,ACC004,50000.00,HK,CN
```

## Models and Algorithms

### Anomaly Detection
- **Algorithm**: Isolation Forest
- **Purpose**: Detect unusual transaction patterns
- **Output**: -1 for anomalies, 1 for normal transactions
- **Features**: log_amount, cross_border

### Risk Scoring
- **Algorithm**: Random Forest Classifier
- **Purpose**: Predict transaction risk level
- **Output**: Probability score (0-1), higher = more risky
- **Features**: log_amount, cross_border

### Network Analysis
- **Metrics**:
  - In-degree: Number of incoming transactions
  - Out-degree: Number of outgoing transactions
  - Betweenness Centrality: Importance in transaction flow
  - Combined Score: Weighted combination of above metrics

## Performance Optimization

- **Model Caching**: Trained models are cached to avoid retraining
- **Async Endpoints**: Non-blocking API responses
- **Lazy Loading**: Data loaded on-demand
- **Configurable Cache TTL**: Adjust model refresh rate

## Troubleshooting

### File Not Found Error
- Ensure CSV file exists in the `DATA_DIR`
- Check file path in `.env`
- Verify file format and permissions

### Memory Issues
- Reduce dataset size for initial testing
- Increase `MODEL_CACHE_TTL` to reduce retraining frequency
- Monitor system resources during large analyses

### Slow Performance
- Check CSV file size and complexity
- Verify network graph size (# of nodes/edges)
- Adjust Plotly graph rendering settings for dashboard

## Dependencies

- **FastAPI**: Modern web framework
- **Pandas**: Data manipulation
- **Scikit-learn**: Machine learning models
- **NetworkX**: Graph analysis
- **Plotly**: Interactive visualizations
- **Dash**: Web-based dashboard
- **Pydantic**: Data validation

## Future Enhancements

- [ ] Real-time streaming analysis
- [ ] Advanced graph algorithms (community detection)
- [ ] Custom model training UI
- [ ] Export analysis reports
- [ ] Multi-user authentication
- [ ] Time-series analysis
- [ ] Explainable AI features

## License

MIT License

## Support

For issues or questions, check the logs directory or review API documentation at `/docs`.
