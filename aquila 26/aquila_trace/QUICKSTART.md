# QUICKSTART.md - Get Started with AquilaTrace in 5 Minutes

## 1. Install (2 minutes)

```bash
# Clone the repository
git clone https://github.com/aquilatrace/aquila-trace.git
cd aquila-trace

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
python -m spacy download en_core_web_sm
```

## 2. Configure (1 minute)

```bash
# Copy environment template
cp .env.example .env

# For development, default settings work fine
# Edit .env only if using custom databases
```

## 3. Run API Server (1 minute)

```bash
python main.py api --reload
```

Server starts at: `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs`

## 4. Try It Out (1 minute)

### Transaction Analysis
```bash
curl -X POST http://localhost:8000/api/v1/transaction/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2024-01-15T10:30:00",
    "source": "account_001",
    "destination": "account_999",
    "amount": 45000.0,
    "currency": "USD"
  }'
```

### Health Check
```bash
curl http://localhost:8000/health
```

## 5. Next Steps

- Read [README.md](README.md) for full documentation
- Check [EXAMPLES.md](EXAMPLES.md) for code examples
- Review [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- Explore API docs at `http://localhost:8000/docs`

## Common Operations

### Analyze Transaction Data
```python
from src.api import TransactionData, AquilaTraceOrchestrator
from src.core.config import Config

config = Config.from_env()
orchestrator = AquilaTraceOrchestrator(config)

transaction = TransactionData(
    timestamp="2024-01-15T10:30:00",
    source="account_001",
    destination="account_999",
    amount=45000.0
)

result = orchestrator.analyze_transaction(transaction)
print(f"Risk Level: {result['risk_level']}")
```

### Train ML Model
```python
from src.ml import MLRegistry
from src.core.config import Config
import pandas as pd
import numpy as np

# Load data
config = Config.from_env()
registry = MLRegistry(config.ml_config.__dict__)

# Create supervised models
models = registry.create_supervised_models()

# Sample data
X = np.random.randn(100, 10)
y = np.random.randint(0, 2, 100)

# Train
xgb_model = models['xgboost']
xgb_model.fit(X[:80], y[:80])

# Predict
predictions = xgb_model.predict(X[80:])
```

### Analyze Text
```python
from src.nlp import CyberIntelligencePipeline
from src.core.config import Config

config = Config.from_env()
nlp = CyberIntelligencePipeline(config.nlp_config.__dict__)

text = "Urgent: Your account verification required immediately"
analysis = nlp.analyze_text(text)
print(analysis)
```

### Blockchain Analysis
```python
from src.blockchain import BlockchainAnalyzer
from src.core.config import Config

config = Config.from_env()
analyzer = BlockchainAnalyzer(config.blockchain_config.__dict__)

analyzer.graph.add_transaction(
    src="1A1z...",
    dst="3J98...",
    amount=2.5,
    txid="tx_001",
    timestamp=1705220000
)

analysis = analyzer.analyze_address("1A1z...")
print(f"Risk Score: {analysis['risk_score']}")
```

## Troubleshooting

**Port already in use:**
```bash
# Use different port
python main.py api --port 8001
```

**Module not found:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -e .
```

**Spacy model missing:**
```bash
python -m spacy download en_core_web_sm
```

## Getting Help

- **Documentation**: https://aquila-trace.readthedocs.io
- **Issues**: https://github.com/aquilatrace/aquila-trace/issues
- **Discussions**: https://github.com/aquilatrace/aquila-trace/discussions

---

**That's it! You're ready to detect financial crime with AquilaTrace.** 🚀
