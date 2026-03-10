# AquilaTrace Core Implementation Guide

This guide shows how to implement and use each core capability of AquilaTrace.

## 1. Setup & Initialization

### Step 1: Install Dependencies
```bash
cd aquila_trace

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install core package
pip install -e .

# Install spaCy model for NER
python -m spacy download en_core_web_sm
```

### Step 2: Initialize Configuration
```python
from src.core.config import Config
from src.core.logger import setup_logging

# Load configuration from environment
config = Config.from_env()

# Setup logging
logger = setup_logging(__name__, level=config.log_level)
logger.info("AquilaTrace initialized")
```

## 2. Machine Learning Implementation

### Train Supervised Models
```python
import numpy as np
import pandas as pd
from src.ml import MLRegistry, XGBoostModel

# Initialize registry
config = Config()
ml_registry = MLRegistry(config.ml_config.__dict__)

# Create models
supervised_models = ml_registry.create_supervised_models()
# Returns: xgboost, lightgbm, random_forest, neural_network

# Prepare data
X_train = np.random.randn(1000, 20)  # 1000 samples, 20 features
y_train = np.random.randint(0, 2, 1000)  # Binary classification
X_test = np.random.randn(200, 20)
y_test = np.random.randint(0, 2, 200)

# Train XGBoost model
xgb_model = supervised_models['xgboost']
xgb_model.fit(X_train, y_train)

# Make predictions
predictions = xgb_model.predict(X_test)
probabilities = xgb_model.predict_proba(X_test)

# Evaluate
metrics = xgb_model.evaluate(X_test, y_test)
print(f"Accuracy: {metrics['accuracy']:.2%}")
print(f"F1-Score: {metrics['f1_score']:.2%}")

# Save model
from pathlib import Path
xgb_model.save(Path("models/xgboost_model.pkl"))
```

### Anomaly Detection
```python
from src.ml import IsolationForestModel, MLRegistry

# Create unsupervised models
unsupervised_models = ml_registry.create_unsupervised_models()
# Returns: dbscan, hdbscan, isolation_forest, one_class_svm

# Train Isolation Forest
iso_forest = unsupervised_models['isolation_forest']
iso_forest.fit(X_train)

# Detect anomalies (-1 for anomalies, 1 for normal)
predictions = iso_forest.predict(X_test)
anomalies = X_test[predictions == -1]

# Get anomaly scores
scores = iso_forest.anomaly_scores(X_test)
high_risk = X_test[scores > 0.7]  # Top 30% anomalies

print(f"Anomalies detected: {(predictions == -1).sum()}")
print(f"Anomaly percentage: {(predictions == -1).mean():.2%}")
```

### Ensemble Training
```python
# Train ensemble of models
results = ml_registry.train_ensemble(X_train, y_train)

for model_name, metrics in results.items():
    print(f"{model_name}: {metrics}")
    # Example:
    # xgboost: {'accuracy': 0.94, 'f1_score': 0.92, ...}
    # lightgbm: {'accuracy': 0.92, 'f1_score': 0.90, ...}
```

## 3. Graph Neural Network Implementation

### Build Financial Network
```python
import torch
from src.graph import GCNModel, FinancialNetworkAnalyzer

# Initialize GNN model
gnn_model = GCNModel(
    input_dim=64,      # Node feature dimension
    hidden_dim=128,    # Hidden layer dimension
    output_dim=2,      # Output classes
    num_layers=3,      # 3 GNN layers
    dropout=0.2
)

# Create analyzer
analyzer = FinancialNetworkAnalyzer(gnn_model)

# Define your financial network
entities = [
    "person_001",              # Index 0
    "wallet_btc_123",          # Index 1
    "merchant_store_X",        # Index 2
    "exchange_kraken",         # Index 3
    "person_002"               # Index 4
]

relationships = [
    (0, 1, "owns"),         # person_001 owns wallet
    (1, 2, "transfers_to"), # wallet transfers to merchant
    (2, 3, "deposits_to"),  # merchant deposits to exchange
    (3, 4, "sends_to"),     # exchange sends to person
    (0, 3, "user_of"),      # person is user of exchange
]

# Build network graph
graph = analyzer.build_network_graph(
    entities=entities,
    relationships=relationships
)

print(f"Graph created: {graph.x.shape[0]} nodes, {graph.edge_index.shape[1]} edges")
```

### Detect Hubs and Vulnerabilities
```python
# Detect financial hubs (high-risk intermediaries)
hubs = analyzer.detect_financial_hubs(graph, top_k=3)

for node_id, centrality_score in hubs:
    print(f"{entities[node_id]}: Risk Score = {centrality_score:.3f}")
    # Example output:
    # exchange_kraken: Risk Score = 0.850
    # wallet_btc_123: Risk Score = 0.620
    # merchant_store_X: Risk Score = 0.580

# Predict future connections (link prediction)
future_connections = analyzer.predict_future_connections(graph, top_k=5)

for src_id, dst_id, probability in future_connections:
    print(f"{entities[src_id]} -> {entities[dst_id]}: {probability:.2%} likely")
    # Example:
    # person_001 -> exchange_kraken: 85% likely
    # wallet_btc_123 -> person_002: 72% likely

# Detect suspicious clusters (network clusters resembling extremist structures)
clusters = analyzer.detect_suspicious_clusters(graph, similarity_threshold=0.7)

for i, cluster in enumerate(clusters):
    member_names = [entities[node_id] for node_id in cluster]
    print(f"Cluster {i}: {member_names}")
```

## 4. NLP Implementation

### Initialize NLP Pipeline
```python
from src.nlp import (
    CyberIntelligencePipeline,
    NamedEntityRecognizer,
    TextClassifier,
    SemanticSimilarityAnalyzer
)

config = Config()

# Option 1: Full pipeline
nlp_pipeline = CyberIntelligencePipeline(config.nlp_config.__dict__)

# Option 2: Individual components
ner = NamedEntityRecognizer()
classifier = TextClassifier(classifier_type="zero-shot")
similarity = SemanticSimilarityAnalyzer()
```

### Extract Named Entities
```python
# Sample text
text = "John Smith from USA sent $5000 to Ahmed Hassan in Cairo using cryptocurrency"

# Extract entities
entities = ner.extract_entities(text)
# Output: [('John Smith', 'PERSON', 0, 10), ('USA', 'GPE', 16, 19), ...]

# Extract financial entities specifically
financial_entities = ner.extract_financial_entities(text)
print(financial_entities)
# Output: {
#     'persons': ['John Smith', 'Ahmed Hassan'],
#     'money': ['$5000'],
#     'locations': ['USA', 'Cairo'],
#     'organizations': [],
#     'dates': []
# }
```

### Classify Suspicious Content
```python
# Detect scam messages
scam_analysis = classifier.classify_scam_message(
    "Urgent: Verify your account immediately or it will be closed"
)
print(scam_analysis)
# Output: {
#     'text': '...',
#     'classifications': [
#         {'label': 'advance_fee_fraud', 'score': 0.85},
#         {'label': 'money_laundering', 'score': 0.12},
#         ...
#     ]
# }

# Detect terror propaganda
propaganda_analysis = classifier.classify_terror_propaganda(
    "Join our cause and become part of the global jihad movement"
)
print(propaganda_analysis)
# Output: {
#     'propaganda_score': 0.92,
#     'classifications': [...]
# }
```

### Analyze Text Similarity
```python
# Compare two texts
similarity = similarity.compute_similarity(
    "Transfer $1000 to account 123456",
    "Send $999 to account 123456"
)
print(f"Similarity: {similarity:.2%}")  # Output: Similarity: 94%

# Find similar texts in corpus
query = "Emergency bank verification required"
corpus = [
    "Your account has been locked, verify identity",
    "Please update your payment method",
    "Congratulations on your bonus!",
    "Urgent: Confirm your banking credentials"
]

similar = similarity.find_similar_texts(query, corpus, top_k=2)
for text, score in similar:
    print(f"{text}: {score:.2%}")

# Cluster similar texts
all_texts = [
    "Verify your account now",
    "Confirm identity immediately",
    "Check your balance",
    "Update payment method",
    "Send verification code"
]

text_clusters = similarity.cluster_texts_by_similarity(
    all_texts,
    similarity_threshold=0.7
)
for cluster in text_clusters:
    print([all_texts[i] for i in cluster])
```

### Batch Text Analysis
```python
# Analyze multiple texts at once
texts = [
    "Urgent account verification needed",
    "Hello, how are you today?",
    "Transfer $500 to wallet XYZ"
]

analyses = nlp_pipeline.analyze_batch(texts)

for analysis in analyses:
    print(f"Text: {analysis['text'][:50]}...")
    print(f"Language: {analysis['language']}")
    print(f"Entities: {analysis['entities']}")
    print(f"Scam Risk: {analysis['scam_classification']}")
```

## 5. Blockchain Implementation

### Analyze Blockchain Addresses
```python
from src.blockchain import BlockchainAnalyzer

# Initialize analyzer
analyzer = BlockchainAnalyzer(config.blockchain_config.__dict__)

# Add known high-risk addresses
analyzer.add_known_bad_address(
    "1A1z7agoat2Pt7VXXLgp2DMC3qA2J6hbSi",
    reason="Known terrorist financing address"
)

# Add sample transactions
import time
analyzer.graph.add_transaction(
    src="1A1z7agoat2Pt7VXXLgp2DMC3qA2J6hbSi",
    dst="3J98t1WpEZ73CNw9viecrnyiWrnqRhWNLy",
    amount=2.5,
    txid="tx_001",
    timestamp=int(time.time())
)

# Analyze specific address
analysis = analyzer.analyze_address("1A1z7agoat2Pt7VXXLgp2DMC3qA2J6hbSi")
print(analysis)
# Output: {
#     'address': '1A1z...',
#     'balance': 2.5,
#     'transaction_count': 1,
#     'risk_score': 0.75,
#     'is_mixer': False,
#     'mixer_score': 0.3,
#     'tags': ['high_risk_connection']
# }
```

### Detect Coordinated Behavior
```python
# Check for smurfing (structured small transactions)
addresses = [
    "address_1",
    "address_2",
    "address_3"
]

coordinated = analyzer.detect_coordinated_behavior(addresses)
print(coordinated)
# Output: {
#     'addresses': [...],
#     'is_smurfing': True,
#     'smurfing_score': 0.75,
#     'common_sources': [...],
#     'common_destinations': [...]
# }
```

### Trace Transaction Flows
```python
# Trace funds from source
flow_analysis = analyzer.analyze_transaction_flow(
    source_address="1A1z7agoat2Pt7VXXLgp2DMC3qA2J6hbSi",
    depth=3  # Follow 3 hops
)

print(flow_analysis)
# Shows complete transaction flow tree
```

### Generate Risk Report
```python
# Get comprehensive blockchain risk report
report = analyzer.generate_risk_report()

print(f"Total Addresses Analyzed: {report['total_addresses']}")
print(f"High Risk: {report['high_risk_count']}")
print(f"Medium Risk: {report['medium_risk_count']}")
print(f"Address Clusters: {report['total_clusters']}")

for address, risk_score in report['high_risk_addresses'][:5]:
    print(f"  {address}: {risk_score:.2f}")
```

## 6. Data Pipeline Implementation

### Process Transactions
```python
from src.data import DataPipeline

# Create pipeline
pipeline = DataPipeline(config.ml_config.__dict__)

# Load transaction data
transactions = pd.DataFrame({
    'timestamp': pd.date_range('2024-01-01', periods=1000, freq='H'),
    'source': np.random.choice(['acc_001', 'acc_002', 'acc_003'], 1000),
    'destination': np.random.choice(['acc_004', 'acc_005', 'acc_006'], 1000),
    'amount': np.random.uniform(100, 50000, 1000),
})

# Process transactions
processed = pipeline.process_transactions(transactions)
print(f"Processed {len(processed)} transactions")
print(processed.head())

# Create feature matrix for ML
X, feature_names = pipeline.create_feature_matrix(transactions)
print(f"Feature matrix shape: {X.shape}")
print(f"Features: {feature_names}")
```

### Extract Entity Profile
```python
# Get behavioral profile for entity
profile = pipeline.get_entity_profile("acc_001", transactions)

print(profile)
# Output: {
#     'entity_id': 'acc_001',
#     'behavioral_features': {
#         'transaction_frequency': 45,
#         'avg_amount': 12500.0,
#         'total_volume': 562500.0,
#         'unique_counterparties': 12,
#         'incoming_ratio': 0.35
#     },
#     'network_features': {
#         'network_density': 0.42,
#         'unique_sources': 45,
#         'unique_destinations': 48,
#         'avg_transaction_amount': 11234.5,
#         ...
#     }
# }
```

## 7. REST API Implementation

### Start API Server
```bash
# Development mode with auto-reload
python main.py api --reload --host 0.0.0.0 --port 8000

# Production mode
AQUILA_ENV=production python main.py api --workers 4
```

### Use API Programmatically
```python
from src.api import TransactionData, AquilaTraceOrchestrator

# Initialize orchestrator
orchestrator = AquilaTraceOrchestrator(config)

# Analyze single transaction
transaction = TransactionData(
    timestamp="2024-01-15T10:30:00",
    source="account_001",
    destination="account_999",
    amount=45000.0,
    currency="USD",
    transaction_id="tx_001"
)

result = orchestrator.analyze_transaction(transaction)
print(result)
# Output: {
#     'transaction_id': 'tx_001',
#     'is_anomaly': True,
#     'anomaly_score': 0.78,
#     'risk_level': 'high'
# }
```

### Entity Risk Assessment Via API
```python
from src.api import TransactionData

# Create sample transactions
transactions = [
    TransactionData(
        timestamp="2024-01-15T10:00:00",
        source="account_001",
        destination="account_002",
        amount=1000.0
    ),
    TransactionData(
        timestamp="2024-01-15T11:00:00",
        source="account_001",
        destination="account_003",
        amount=1500.0
    ),
    # ... more transactions
]

# Assess risk
risk = orchestrator.analyze_entity_risk("account_001", pd.DataFrame([
    {
        'timestamp': tx.timestamp,
        'source': tx.source,
        'destination': tx.destination,
        'amount': tx.amount
    }
    for tx in transactions
]))

print(f"Entity: {risk.entity_id}")
print(f"Risk Level: {risk.risk_level}")
print(f"Risk Score: {risk.risk_score:.2f}")
print(f"Recommendation: {risk.recommendation}")
```

## 8. Complete Integration Example

```python
from src.core.config import Config
from src.api import AquilaTraceOrchestrator
import pandas as pd

# 1. Initialize everything
config = Config.from_env()
orchestrator = AquilaTraceOrchestrator(config)

# 2. Load data
transactions = pd.read_csv("transactions.csv")
texts = ["text1", "text2", "text3"]
addresses = ["addr1", "addr2"]

# 3. Run analyses in parallel
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor() as executor:
    # Transaction analysis
    tx_future = executor.submit(
        orchestrator.detect_network_anomalies,
        transactions
    )
    
    # Text analysis
    text_future = executor.submit(
        orchestrator.analyze_text_batch,
        texts
    )
    
    # Blockchain analysis
    bc_future = executor.submit(
        lambda: [orchestrator.analyze_blockchain_address(addr) for addr in addresses]
    )
    
    # Get results
    tx_results = tx_future.result()
    text_results = text_future.result()
    bc_results = bc_future.result()

# 4. Combine results
combined_analysis = {
    'transactions': tx_results,
    'texts': text_results,
    'blockchain': bc_results
}

print(combined_analysis)
```

## 9. Configuration & Customization

### Environment Variables
```bash
# .env file
AQUILA_ENV=development
AQUILA_LOG_LEVEL=DEBUG
AQUILA_BATCH_SIZE=32
AQUILA_LEARNING_RATE=0.001
AQUILA_API_PORT=8000
```

### YAML Configuration
```yaml
# configs/custom_config.yaml
ml:
  batch_size: 64
  epochs: 200
  learning_rate: 0.0005

graph:
  embedding_dim: 512
  num_layers: 4

nlp:
  max_sequence_length: 1024
  supported_languages:
    - en
    - ar
    - fr
    - sw
```

Load custom config:
```python
config = Config.from_yaml('configs/custom_config.yaml')
orchestrator = AquilaTraceOrchestrator(config)
```

## 10. Testing Implementation

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_aquila_trace.py::TestMLModels -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

Test your own code:
```python
def test_custom_analysis():
    config = Config()
    orchestrator = AquilaTraceOrchestrator(config)
    
    # Your test
    transaction = TransactionData(...)
    result = orchestrator.analyze_transaction(transaction)
    
    assert result['risk_level'] in ['low', 'medium', 'high', 'critical']
```

---

## Next Steps

1. **Start with QUICKSTART.md** - Get running in 5 minutes
2. **Run examples** - Execute EXAMPLES.md code
3. **Explore APIs** - Visit http://localhost:8000/docs
4. **Customize config** - Modify for your use case
5. **Integrate data** - Connect your data sources
6. **Deploy** - Follow DEPLOYMENT.md for production

You now have a complete, production-ready implementation!
