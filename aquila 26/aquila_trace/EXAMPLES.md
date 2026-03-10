# Example Usage of AquilaTrace

This script demonstrates comprehensive usage of the AquilaTrace platform.

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.core.config import Config
from src.ml import MLRegistry, XGBoostModel, IsolationForestModel
from src.data import DataPipeline
from src.nlp import CyberIntelligencePipeline
from src.blockchain import BlockchainAnalyzer
from src.graph import FinancialNetworkAnalyzer, GCNModel
from src.api import AquilaTraceOrchestrator, TransactionData

# Initialize configuration
config = Config.from_env()

# Example 1: Transaction Data Analysis
print("=" * 50)
print("EXAMPLE 1: Transaction Analysis")
print("=" * 50)

# Create sample transaction data
transactions = pd.DataFrame({
    'timestamp': pd.date_range(start='2024-01-01', periods=100, freq='H'),
    'source': np.random.choice(['account_001', 'account_002', 'account_003'], 100),
    'destination': np.random.choice(['account_004', 'account_005', 'account_006'], 100),
    'amount': np.random.uniform(100, 10000, 100),
})

# Initialize data pipeline
data_pipeline = DataPipeline(config.ml_config.__dict__)

# Process transactions
processed_transactions = data_pipeline.process_transactions(transactions)
print(f"Processed {len(processed_transactions)} transactions")
print(processed_transactions.head())

# Create feature matrix
X, feature_names = data_pipeline.create_feature_matrix(transactions)
print(f"Feature matrix shape: {X.shape}")
print(f"Features: {feature_names}")

# Example 2: Machine Learning Models
print("\n" + "=" * 50)
print("EXAMPLE 2: Machine Learning Models")
print("=" * 50)

# Initialize ML registry
ml_registry = MLRegistry(config.ml_config.__dict__)

# Create supervised models
supervised_models = ml_registry.create_supervised_models()
print(f"Created supervised models: {list(supervised_models.keys())}")

# Create unsupervised models
unsupervised_models = ml_registry.create_unsupervised_models()
print(f"Created unsupervised models: {list(unsupervised_models.keys())}")

# Sample labels for training (binary classification: suspicious=1, normal=0)
y = np.random.randint(0, 2, len(X))

# Train XGBoost model
xgb_model = supervised_models['xgboost']
xgb_model.fit(X[:80], y[:80])
predictions = xgb_model.predict(X[80:])
probabilities = xgb_model.predict_proba(X[80:])
print(f"XGBoost predictions: {predictions[:5]}")
print(f"Probabilities: {probabilities[:5]}")

# Train Isolation Forest for anomaly detection
iso_forest = unsupervised_models['isolation_forest']
iso_forest.fit(X)
anomalies = iso_forest.predict(X)
anomaly_scores = iso_forest.anomaly_scores(X)
print(f"Anomalies detected: {(anomalies == -1).sum()}")
print(f"Anomaly scores (sample): {anomaly_scores[:5]}")

# Example 3: NLP Analysis
print("\n" + "=" * 50)
print("EXAMPLE 3: NLP and Text Analysis")
print("=" * 50)

# Initialize NLP pipeline
nlp_pipeline = CyberIntelligencePipeline(config.nlp_config.__dict__)

# Sample texts for analysis
sample_texts = [
    "Urgent: Your bank account has been limited. Click here to verify your identity immediately.",
    "Legitimate payment for invoice #12345. Reference: Project Alpha",
    "Cryptocurrency transfer to wallet address. Please confirm transaction.",
    "We need immediate funds transfer for urgent security matter. Contact provided.",
]

# Analyze texts
text_analyses = []
for text in sample_texts:
    analysis = nlp_pipeline.analyze_text(text)
    text_analyses.append(analysis)
    print(f"\nText: {text[:50]}...")
    print(f"Language: {analysis['language']}")
    print(f"Entities: {analysis['entities']}")
    print(f"Scam Classification: {analysis['scam_classification']['classifications'][0]}")

# Example 4: Blockchain Analysis
print("\n" + "=" * 50)
print("EXAMPLE 4: Blockchain Analysis")
print("=" * 50)

# Initialize blockchain analyzer
blockchain = BlockchainAnalyzer(config.blockchain_config.__dict__)

# Add sample transactions to blockchain graph
blockchain.graph.add_transaction(
    src="1A1z7agoat2Pt7VXXLgp2DMC3qA2J6hbSi",
    dst="3J98t1WpEZ73CNw9viecrnyiWrnqRhWNLy",
    amount=2.5,
    txid="tx_001",
    timestamp=int(datetime.now().timestamp())
)

blockchain.graph.add_transaction(
    src="3J98t1WpEZ73CNw9viecrnyiWrnqRhWNLy",
    dst="1A1z7agoat2Pt7VXXLgp2DMC3qA2J6hbSi",
    amount=2.3,
    txid="tx_002",
    timestamp=int((datetime.now() - timedelta(hours=1)).timestamp())
)

# Analyze addresses
address = "1A1z7agoat2Pt7VXXLgp2DMC3qA2J6hbSi"
analysis = blockchain.analyze_address(address)
print(f"\nAddress Analysis: {address}")
print(f"Risk Score: {analysis['risk_score']:.2f}")
print(f"Is Mixer: {analysis['is_mixer']}")
print(f"Tags: {analysis['tags']}")

# Generate risk report
report = blockchain.generate_risk_report()
print(f"\nBlockchain Risk Report:")
print(f"Total Addresses: {report['total_addresses']}")
print(f"High Risk Count: {report['high_risk_count']}")
print(f"Medium Risk Count: {report['medium_risk_count']}")

# Example 5: Graph Neural Networks
print("\n" + "=" * 50)
print("EXAMPLE 5: Graph Neural Networks")
print("=" * 50)

# Create financial network
gnn_model = GCNModel(
    input_dim=16,
    hidden_dim=32,
    output_dim=2,
    num_layers=3
)
financial_analyzer = FinancialNetworkAnalyzer(gnn_model)

# Define entities and relationships
entities = ["person_001", "wallet_A", "merchant_B", "exchange_C", "person_002"]
relationships = [
    (0, 1, "owns"),        # person owns wallet
    (1, 2, "transfer_to"),  # wallet transfers to merchant
    (2, 3, "deposits_to"),  # merchant deposits to exchange
    (3, 4, "sends'),        # exchange sends to person
]

# Build network graph
graph = financial_analyzer.build_network_graph(
    entities=entities,
    relationships=relationships
)

# Detect financial hubs
hubs = financial_analyzer.detect_financial_hubs(graph, top_k=3)
print(f"\nDetected Financial Hubs:")
for node_id, score in hubs:
    print(f"  {entities[node_id]}: {score:.3f}")

# Predict future connections
predictions = financial_analyzer.predict_future_connections(graph, top_k=5)
print(f"\nPredicted Future Connections:")
for src, dst, score in predictions[:3]:
    print(f"  {entities[src]} -> {entities[dst]}: {score:.3f}")

# Detect suspicious clusters
clusters = financial_analyzer.detect_suspicious_clusters(graph, similarity_threshold=0.7)
print(f"\nDetected Suspicious Clusters: {len(clusters)}")

# Example 6: Orchestration - Complete Analysis
print("\n" + "=" * 50)
print("EXAMPLE 6: Complete Orchestration")
print("=" * 50)

# Initialize orchestrator
orchestrator = AquilaTraceOrchestrator(config)

# Analyze a transaction through orchestrator
transaction = TransactionData(
    timestamp="2024-01-15T10:30:00",
    source="account_001",
    destination="account_999",
    amount=45000.0,
    currency="USD",
    transaction_id="tx_high_50001"
)

tx_analysis = orchestrator.analyze_transaction(transaction)
print(f"\nTransaction Analysis:")
print(f"Is Anomaly: {tx_analysis['is_anomaly']}")
print(f"Anomaly Score: {tx_analysis['anomaly_score']:.2f}")
print(f"Risk Level: {tx_analysis['risk_level']}")

# Assess entity risk
risk_assessment = orchestrator.analyze_entity_risk("entity_001", transactions)
print(f"\nEntity Risk Assessment:")
print(f"Entity ID: {risk_assessment.entity_id}")
print(f"Risk Score: {risk_assessment.risk_score:.2f}")
print(f"Risk Level: {risk_assessment.risk_level}")
print(f"Risk Factors: {risk_assessment.risk_factors}")
print(f"Recommendation: {risk_assessment.recommendation}")

# Detect network anomalies
network_anomalies = orchestrator.detect_network_anomalies(transactions)
print(f"\nNetwork Anomaly Detection:")
print(f"Total Transactions: {network_anomalies['total_transactions']}")
print(f"Anomalies Detected: {network_anomalies['anomalies_detected']}")
print(f"Anomaly Percentage: {network_anomalies['anomaly_percentage']:.2f}%")

print("\n" + "=" * 50)
print("EXAMPLE USAGE COMPLETE")
print("=" * 50)
```

## Running the Example

```bash
python examples/comprehensive_example.py
```

## API Usage Examples

### Transaction Analysis via REST API

```bash
curl -X POST http://localhost:8000/api/v1/transaction/analyze \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your-api-key" \\
  -d '{
    "timestamp": "2024-01-15T10:30:00",
    "source": "account_001",
    "destination": "account_999",
    "amount": 45000.0,
    "currency": "USD"
  }'
```

### Entity Risk Assessment

```bash
curl -X POST http://localhost:8000/api/v1/entity/risk-assessment \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your-api-key" \\
  -d '{
    "entity_id": "entity_001",
    "transactions": [
      {
        "timestamp": "2024-01-15T10:00:00",
        "source": "account_001",
        "destination": "account_002",
        "amount": 1000.0
      }
    ]
  }'
```

## Advanced Configuration

Create a custom configuration file (`configs/custom_config.yaml`):

```yaml
ml:
  supervised_models:
    - xgboost
    - lightgbm
  unsupervised_models:
    - isolation_forest
    - hdbscan
  batch_size: 64
  learning_rate: 0.001

graph:
  embedding_dim: 256
  num_layers: 4
  dropout_rate: 0.3

nlp:
  max_sequence_length: 512
  supported_languages:
    - en
    - ar
    - fr
    - sw

blockchain:
  supported_chains:
    - bitcoin
    - ethereum
  mixer_detection_threshold: 0.85
```

Load the custom configuration:

```python
config = Config.from_yaml('configs/custom_config.yaml')
orchestrator = AquilaTraceOrchestrator(config)
```
