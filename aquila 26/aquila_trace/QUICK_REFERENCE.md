# AquilaTrace Quick Reference Guide

## Installation (1 minute)

```bash
cd aquila_trace
pip install -e .
python -m spacy download en_core_web_sm
```

## Run Tutorial (2 minutes)

```bash
python tutorial.py
```

This demonstrates all core capabilities with real data and output.

## Quick API Server (30 seconds)

```bash
python main.py api --reload
# Open http://localhost:8000/docs
```

---

## By Use Case

### 1️⃣ Detect Fraud in Transactions

```python
from src.api import AquilaTraceOrchestrator, TransactionData
from src.core.config import Config

orchestrator = AquilaTraceOrchestrator(Config())

# Check if transaction is fraudulent
transaction = TransactionData(
    timestamp="2024-01-15T10:30:00",
    source="account_001",
    destination="account_999",
    amount=45000.0
)

result = orchestrator.analyze_transaction(transaction)
print(f"Risk: {result['risk_level']}")  # high, medium, low
```

### 2️⃣ Rate Entity Risk (Person/Account)

```python
import pandas as pd

# All transactions for entity
transactions = pd.read_csv("entity_transactions.csv")

risk = orchestrator.analyze_entity_risk("person_001", transactions)
print(f"Risk Level: {risk.risk_level}")
print(f"Recommendation: {risk.recommendation}")
```

### 3️⃣ Find Anomalies in Network

```python
# Load transaction network data
transactions = pd.read_csv("transactions.csv")

anomalies = orchestrator.detect_network_anomalies(transactions)
print(f"Anomalies: {anomalies['anomalies_detected']}")
print(f"Total: {anomalies['total_transactions']}")
```

### 4️⃣ Analyze Text for Crime Indicators

```python
texts = [
    "Verify your account immediately",
    "Normal conversation here",
    "Send cryptocurrency to wallet XYZ"
]

results = orchestrator.analyze_text_batch(texts)
for result in results:
    print(f"Text: {result['text'][:50]}...")
    print(f"Language: {result['language']['code']}")
    print(f"Entities: {result['entities']}")
```

### 5️⃣ Check Blockchain Addresses

```python
# Analyze Bitcoin address
analysis = orchestrator.analyze_blockchain_address(
    "1A1z7agoat2Pt7VXXLgp2DMC3qA2J6hbSi",
    chain="bitcoin"
)

print(f"Risk: {analysis['risk_score']:.2f}")
print(f"Mixer: {analysis['is_mixer']}")
```

### 6️⃣ Map Financial Network

```python
from src.graph import GCNModel, FinancialNetworkAnalyzer

gnn = GCNModel(input_dim=16, hidden_dim=32)
analyzer = FinancialNetworkAnalyzer(gnn)

# Define your financial network
entities = ["person_A", "wallet_B", "exchange_C"]
relationships = [
    (0, 1, "owns"),
    (1, 2, "transfers_to")
]

graph = analyzer.build_network_graph(entities, relationships)

# Find key players
hubs = analyzer.detect_financial_hubs(graph)
for node_id, score in hubs:
    print(f"{entities[node_id]}: {score:.2f}")

# Predict future connections
predictions = analyzer.predict_future_connections(graph)
for src, dst, prob in predictions:
    print(f"{entities[src]} → {entities[dst]}: {prob:.1%}")
```

### 7️⃣ Train Custom ML Model

```python
from src.ml import MLRegistry
import numpy as np

ml = MLRegistry(Config().ml_config.__dict__)
models = ml.create_supervised_models()

# Your data
X_train = np.random.randn(1000, 20)  # 1000 samples, 20 features
y_train = np.random.randint(0, 2, 1000)  # 0 or 1

# Train XGBoost
xgb = models['xgboost']
xgb.fit(X_train, y_train)

# Predict
predictions = xgb.predict(X_test)
probabilities = xgb.predict_proba(X_test)
```

### 8️⃣ Process & Feature Engineer Data

```python
from src.data import DataPipeline
import pandas as pd

pipeline = DataPipeline(Config().ml_config.__dict__)

# Load transactions
transactions = pd.DataFrame({
    'timestamp': pd.date_range('2024-01-01', periods=1000),
    'source': ['account_' + str(i % 100) for i in range(1000)],
    'destination': ['account_' + str(i % 100) for i in range(1000)],
    'amount': np.random.uniform(100, 10000, 1000)
})

# Process
processed = pipeline.process_transactions(transactions)

# Get features for ML
X, feature_names = pipeline.create_feature_matrix(transactions)
print(f"Features: {feature_names}")
```

### 9️⃣ Extract Entities from Text

```python
from src.nlp import NamedEntityRecognizer

ner = NamedEntityRecognizer()

text = "John Smith sent $5000 to Ahmed Hassan in Cairo"

# All entities
all_entities = ner.extract_entities(text)

# Financial entities
entities = ner.extract_financial_entities(text)
print(f"Persons: {entities['persons']}")
print(f"Money: {entities['money']}")
print(f"Locations: {entities['locations']}")
```

### 🔟 Classify Suspicious Content

```python
from src.nlp import TextClassifier

clf = TextClassifier()

# Detect scams
scam_result = clf.classify_scam_message(
    "Verify your account or it will be closed"
)
print(scam_result['classifications'])

# Detect propaganda
prop_result = clf.classify_terror_propaganda(
    "Join our movement for global..." 
)
print(f"Propaganda score: {prop_result['propaganda_score']:.2f}")
```

---

## REST API Endpoints

### Check Health
```bash
curl http://localhost:8000/health
```

### Analyze Transaction
```bash
curl -X POST http://localhost:8000/api/v1/transaction/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2024-01-15T10:30:00",
    "source": "account_001",
    "destination": "account_999",
    "amount": 45000.0
  }'
```

### Assess Entity Risk
```bash
curl -X POST http://localhost:8000/api/v1/entity/risk-assessment \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "person_001",
    "transactions": [...]
  }'
```

### Analyze Text
```bash
curl -X POST http://localhost:8000/api/v1/text/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Verify account now", "Hello"],
    "analysis_type": "comprehensive"
  }'
```

### Analyze Blockchain
```bash
curl -X POST http://localhost:8000/api/v1/blockchain/address-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": ["1A1z7agoat2Pt7VXXLgp2DMC3qA2J6hbSi"],
    "chain": "bitcoin"
  }'
```

### Detect Anomalies
```bash
curl -X POST http://localhost:8000/api/v1/anomalies/detect \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [...]
  }'
```

---

## Configuration Options

### Environment Variables (.env)
```bash
AQUILA_ENV=development
AQUILA_LOG_LEVEL=DEBUG
AQUILA_API_PORT=8000
AQUILA_BATCH_SIZE=32
AQUILA_LEARNING_RATE=0.001
```

### YAML Config (configs/default_config.yaml)
```yaml
ml:
  epochs: 100
  batch_size: 32

graph:
  embedding_dim: 256
  num_layers: 3

nlp:
  max_sequence_length: 512
  
blockchain:
  mixer_detection_threshold: 0.85
```

---

## Common Commands

### Start Development Server
```bash
python main.py api --reload --port 8000
```

### Run Tutorial
```bash
python tutorial.py
```

### Run Tests
```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html
```

### Analyze Data File
```bash
python main.py analyze --input data.csv --type transaction --output results.json
```

### View Configuration
```bash
python main.py config --show
```

### Save/Load Configuration
```bash
python main.py config --save my_config.yaml
python main.py config --load my_config.yaml
```

---

## File Locations

| Item | Location |
|------|----------|
| Source Code | `src/` |
| Tests | `tests/` |
| Configuration | `configs/` |
| Documentation | `README.md`, `*.md` |
| Models | `models/` (created after training) |
| Logs | `logs/` (created after first run) |
| Data | `data/` (for your datasets) |

---

## Learning Path

1. **5 min**: Run `python tutorial.py`
2. **15 min**: Read `QUICKSTART.md`
3. **30 min**: Explore `IMPLEMENTATION.md`
4. **1 hour**: Try code examples from `EXAMPLES.md`
5. **2 hours**: Read source code in `src/`
6. **1 hour**: Study `ARCHITECTURE.md`
7. **Deploy**: Follow `DEPLOYMENT.md`

---

## Troubleshooting

### Port in Use
```bash
python main.py api --port 8001
```

### Missing Dependencies
```bash
pip install -e .
python -m spacy download en_core_web_sm
```

### Slow Performance
- Reduce batch size in config
- Use CPU instead of GPU
- Reduce model size (embedding_dim, num_layers)

### Database Errors
- Check PostgreSQL is running
- Verify connection strings in .env
- Reset database if needed

---

## Key Classes & Functions

### Core
- `Config` - Configuration management
- `setup_logging` - Initialize logger
- `AquilaTraceOrchestrator` - Main engine

### ML
- `XGBoostModel` - Supervised learning
- `IsolationForestModel` - Anomaly detection
- `MLRegistry` - Model management

### NLP
- `NamedEntityRecognizer` - Extract entities
- `TextClassifier` - Classify texts
- `SemanticSimilarityAnalyzer` - Compare texts
- `CyberIntelligencePipeline` - Full NLP pipeline

### Blockchain
- `BlockchainAnalyzer` - Analyze addresses
- `MixerDetector` - Detect mixers
- `SmurfingDetector` - Detect structuring

### Graph
- `GCNModel` - Graph Convolutional Network
- `FinancialNetworkAnalyzer` - Network analysis

### Data
- `DataValidator` - Validate data
- `FeatureEngineer` - Create features
- `DataPipeline` - Full processing pipeline

### API
- `TransactionData` - Transaction model
- `create_app` - Create FastAPI app

---

## Next Steps

✅ **Immediate**: Run `python tutorial.py`
✅ **Quick Start**: Follow `QUICKSTART.md`
✅ **Implementation**: Read `IMPLEMENTATION.md`
✅ **Examples**: Study `EXAMPLES.md`
✅ **API**: Start with `python main.py api --reload`
✅ **Production**: See `DEPLOYMENT.md`

---

**You have everything you need to detect financial crime with AquilaTrace!** 🚀
