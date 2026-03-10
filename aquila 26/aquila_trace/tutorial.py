"""
Quick hands-on tutorial for AquilaTrace core capabilities.
Run this script to learn by doing!

Execute: python tutorial.py
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys

print("=" * 70)
print("AQUILATRACE CORE CAPABILITIES TUTORIAL")
print("=" * 70)

# Check imports
print("\n[1] Checking imports...")
try:
    from src.core.config import Config
    from src.core.logger import setup_logging
    from src.ml import MLRegistry, XGBoostModel
    from src.data import DataPipeline
    from src.nlp import CyberIntelligencePipeline, NamedEntityRecognizer, TextClassifier
    from src.blockchain import BlockchainAnalyzer
    from src.graph import GCNModel, FinancialNetworkAnalyzer
    from src.api import AquilaTraceOrchestrator, TransactionData
    print("✓ All imports successful!")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Install with: pip install -e .")
    sys.exit(1)

# Initialize
print("\n[2] Initializing AquilaTrace...")
config = Config()
logger = setup_logging(__name__, level="INFO")
print("✓ Configuration loaded")

# ============================================================================
# TUTORIAL 1: MACHINE LEARNING
# ============================================================================
print("\n" + "=" * 70)
print("TUTORIAL 1: MACHINE LEARNING")
print("=" * 70)

print("\n[1.1] Creating sample financial data...")
# Create realistic transaction data
np.random.seed(42)
n_samples = 500

# Normal transactions
normal_amounts = np.random.normal(5000, 1000, n_samples // 2)
normal_data = np.random.randn(n_samples // 2, 10)

# Suspicious transactions (higher amounts, unusual patterns)
suspicious_amounts = np.random.normal(50000, 10000, n_samples // 2)
suspicious_data = np.random.randn(n_samples // 2, 10) * 3  # Higher variance

# Combine
X = np.vstack([normal_data, suspicious_data])
y = np.hstack([np.zeros(n_samples // 2), np.ones(n_samples // 2)])

print(f"✓ Created {len(X)} samples with {X.shape[1]} features")

print("\n[1.2] Training ML models...")
ml_registry = MLRegistry(config.ml_config.__dict__)

# Create and train supervised models
supervised = ml_registry.create_supervised_models()
X_train, X_test = X[:400], X[400:]
y_train, y_test = y[:400], y[400:]

xgb = supervised['xgboost']
xgb.fit(X_train, y_train)
metrics = xgb.evaluate(X_test, y_test)
print(f"✓ XGBoost trained")
print(f"  - Accuracy: {metrics['accuracy']:.2%}")
print(f"  - F1-Score: {metrics['f1_score']:.2%}")

print("\n[1.3] Anomaly Detection...")
unsupervised = ml_registry.create_unsupervised_models()
iso_forest = unsupervised['isolation_forest']
iso_forest.fit(X)
anomalies = iso_forest.predict(X)
anomaly_count = (anomalies == -1).sum()
print(f"✓ Isolation Forest trained")
print(f"  - Anomalies detected: {anomaly_count} ({anomaly_count/len(X):.1%})")

# ============================================================================
# TUTORIAL 2: DATA PROCESSING
# ============================================================================
print("\n" + "=" * 70)
print("TUTORIAL 2: DATA PIPELINE")
print("=" * 70)

print("\n[2.1] Processing transaction data...")
# Create sample transactions
transactions = pd.DataFrame({
    'timestamp': pd.date_range('2024-01-01', periods=200, freq='6H'),
    'source': np.random.choice(['Alice', 'Bob', 'Charlie'], 200),
    'destination': np.random.choice(['David', 'Eve', 'Frank'], 200),
    'amount': np.random.uniform(100, 10000, 200),
})

pipeline = DataPipeline(config.ml_config.__dict__)
processed = pipeline.process_transactions(transactions)
print(f"✓ Processed {len(processed)} transactions")

X_features, feature_names = pipeline.create_feature_matrix(transactions)
print(f"✓ Created feature matrix: {X_features.shape}")
print(f"  - Features: {', '.join(feature_names[:5])}...")

# ============================================================================
# TUTORIAL 3: NLP
# ============================================================================
print("\n" + "=" * 70)
print("TUTORIAL 3: NATURAL LANGUAGE PROCESSING")
print("=" * 70)

print("\n[3.1] Named Entity Recognition...")
ner = NamedEntityRecognizer()
text = "John Smith from USA sent $5000 to Ahmed Hassan in Cairo on 2024-01-15"
entities = ner.extract_financial_entities(text)
print(f"✓ Text: {text}")
print(f"  - Persons: {entities['persons']}")
print(f"  - Money: {entities['money']}")
print(f"  - Locations: {entities['locations']}")

print("\n[3.2] Text Classification...")
classifier = TextClassifier()
scam_text = "URGENT: Verify your account immediately or it will be closed!"
result = classifier.classify_scam_message(scam_text)
top_label = result['classifications'][0]
print(f"✓ Analyzed: {scam_text}")
print(f"  - Top classification: {top_label['label']} ({top_label['score']:.1%})")

print("\n[3.3] Full NLP Pipeline...")
nlp = CyberIntelligencePipeline(config.nlp_config.__dict__)
sample_texts = [
    "Please verify your banking credentials urgently",
    "Hello, how are you doing today?",
    "Transfer $1000 to wallet address 123abc"
]
analyses = nlp.analyze_batch(sample_texts)
for i, text in enumerate(sample_texts):
    entities_found = sum(len(v) for v in analyses[i]['entities'].values())
    print(f"✓ Text {i+1}: Found {entities_found} entities")

# ============================================================================
# TUTORIAL 4: BLOCKCHAIN
# ============================================================================
print("\n" + "=" * 70)
print("TUTORIAL 4: BLOCKCHAIN ANALYTICS")
print("=" * 70)

print("\n[4.1] Building blockchain graph...")
blockchain = BlockchainAnalyzer(config.blockchain_config.__dict__)

# Add sample transactions
addresses = {
    "addr_1": "1A1z7agoat2Pt7VXXLgp2DMC3qA2J6hbSi",
    "addr_2": "3J98t1WpEZ73CNw9viecrnyiWrnqRhWNLy",
    "addr_3": "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",
}

base_time = int(datetime.now().timestamp())
blockchain.graph.add_transaction(
    src=addresses["addr_1"],
    dst=addresses["addr_2"],
    amount=2.5,
    txid="tx_001",
    timestamp=base_time
)
blockchain.graph.add_transaction(
    src=addresses["addr_2"],
    dst=addresses["addr_3"],
    amount=2.3,
    txid="tx_002",
    timestamp=base_time - 3600
)

print(f"✓ Created blockchain graph with {len(blockchain.graph.addresses)} addresses")

print("\n[4.2] Analyzing address risk...")
analysis = blockchain.analyze_address(addresses["addr_1"])
print(f"✓ Address: {addresses['addr_1'][:20]}...")
print(f"  - Risk Score: {analysis['risk_score']:.2f}")
print(f"  - Is Mixer: {analysis['is_mixer']}")
print(f"  - Tags: {analysis['tags']}")

print("\n[4.3] Generating risk report...")
report = blockchain.generate_risk_report()
print(f"✓ Risk Report:")
print(f"  - Total Addresses: {report['total_addresses']}")
print(f"  - High Risk: {report['high_risk_count']}")
print(f"  - Clusters Found: {report['total_clusters']}")

# ============================================================================
# TUTORIAL 5: GRAPH NEURAL NETWORKS
# ============================================================================
print("\n" + "=" * 70)
print("TUTORIAL 5: GRAPH NEURAL NETWORKS")
print("=" * 70)

print("\n[5.1] Building financial network...")
gnn_model = GCNModel(input_dim=16, hidden_dim=32, output_dim=2, num_layers=3)
gnn_analyzer = FinancialNetworkAnalyzer(gnn_model)

entities = [
    "merchant_A",
    "wallet_1",
    "person_X",
    "exchange_B",
    "person_Y"
]

relationships = [
    (0, 1, "owns"),
    (1, 2, "transfers_to"),
    (2, 3, "user_of"),
    (3, 4, "sends_to"),
]

graph = gnn_analyzer.build_network_graph(entities, relationships)
print(f"✓ Network built: {graph.x.shape[0]} nodes, {graph.edge_index.shape[1]} edges")

print("\n[5.2] Detecting financial hubs...")
hubs = gnn_analyzer.detect_financial_hubs(graph, top_k=3)
print(f"✓ Top financial hubs:")
for node_id, score in hubs:
    print(f"  - {entities[node_id]}: {score:.3f}")

print("\n[5.3] Predicting future connections...")
predictions = gnn_analyzer.predict_future_connections(graph, top_k=3)
print(f"✓ Predicted connections:")
for src, dst, prob in predictions:
    print(f"  - {entities[src]} → {entities[dst]}: {prob:.1%}")

# ============================================================================
# TUTORIAL 6: ORCHESTRATION
# ============================================================================
print("\n" + "=" * 70)
print("TUTORIAL 6: ORCHESTRATION & API")
print("=" * 70)

print("\n[6.1] Initialize Orchestrator...")
orchestrator = AquilaTraceOrchestrator(config)
print("✓ Orchestrator ready")

print("\n[6.2] Analyze single transaction...")
transaction = TransactionData(
    timestamp="2024-01-15T10:30:00",
    source="account_001",
    destination="account_999",
    amount=45000.0,
    currency="USD",
    transaction_id="tx_high_001"
)

result = orchestrator.analyze_transaction(transaction)
print(f"✓ Transaction Analysis:")
print(f"  - Is Anomaly: {result['is_anomaly']}")
print(f"  - Anomaly Score: {result['anomaly_score']:.2f}")
print(f"  - Risk Level: {result['risk_level']}")

print("\n[6.3] Entity risk assessment...")
# Create sample transactions for entity
entity_transactions = pd.DataFrame({
    'timestamp': pd.date_range('2024-01-01', periods=50, freq='H'),
    'source': ['entity_001'] * 50,
    'destination': np.random.choice(['entity_002', 'entity_003'], 50),
    'amount': np.random.uniform(1000, 20000, 50),
})

risk = orchestrator.analyze_entity_risk("entity_001", entity_transactions)
print(f"✓ Entity Risk Assessment:")
print(f"  - Risk Score: {risk.risk_score:.2f}")
print(f"  - Risk Level: {risk.risk_level}")
print(f"  - Factors: {', '.join(risk.risk_factors)}")
print(f"  - Recommendation: {risk.recommendation}")

print("\n[6.4] Detect anomalies in network...")
anomaly_result = orchestrator.detect_network_anomalies(transactions)
print(f"✓ Network Anomaly Detection:")
print(f"  - Total Transactions: {anomaly_result['total_transactions']}")
print(f"  - Anomalies Found: {anomaly_result['anomalies_detected']}")
print(f"  - Anomaly Rate: {anomaly_result['anomaly_percentage']:.1%}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("TUTORIAL COMPLETE!")
print("=" * 70)

print("\n✓ You've successfully demonstrated:")
print("  1. Machine Learning (classification & anomaly detection)")
print("  2. Data Pipeline (processing & feature engineering)")
print("  3. NLP (entity extraction & text classification)")
print("  4. Blockchain Analysis (address risk scoring)")
print("  5. Graph Neural Networks (hub detection & link prediction)")
print("  6. Orchestration (unified analysis engine)")

print("\nNext steps:")
print("  - Start API: python main.py api --reload")
print("  - View docs: http://localhost:8000/docs")
print("  - Read implementation guide: IMPLEMENTATION.md")
print("  - Explore examples: EXAMPLES.md")
print("  - Check source code: src/")

print("\n" + "=" * 70)
