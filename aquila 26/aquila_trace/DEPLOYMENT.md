# AquilaTrace - Installation and Deployment Guide

## System Requirements

- Python 3.10+
- 16GB RAM (minimum, 32GB recommended)
- GPU support: NVIDIA CUDA 11.8+ (optional but recommended)
- PostgreSQL 12+
- Redis 6.0+
- MongoDB 4.4+ (optional)

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/aquilatrace/aquila-trace.git
cd aquila-trace
```

### 2. Set Up Python Environment

#### Using venv
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Using conda
```bash
conda create -n aquila-trace python=3.10
conda activate aquila-trace
```

### 3. Install Dependencies
```bash
# Install core dependencies
pip install -e .

# Install development dependencies (for testing)
pip install -e ".[dev]"

# Install spaCy model
python -m spacy download en_core_web_sm
```

### 4. Configure Environment

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```
AQUILA_ENV=development
AQUILA_DEBUG=true
AQUILA_LOG_LEVEL=DEBUG
AQUILA_POSTGRES_URL=postgresql://user:password@localhost/aquila_trace
AQUILA_REDIS_URL=redis://localhost:6379/0
AQUILA_API_PORT=8000
```

### 5. Set Up Databases

#### PostgreSQL
```bash
# Create database
createdb aquila_trace

# Create user
createuser aquila
ALTER ROLE aquila WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE aquila_trace TO aquila;

# Run migrations (if applicable)
alembic upgrade head
```

#### Redis
```bash
# Start Redis (if not running as service)
redis-server

# Or using Docker
docker run -d -p 6379:6379 redis:latest
```

### 6. Verify Installation
```bash
python -c "from src import *; print('AquilaTrace installed successfully')"
```

## Running AquilaTrace

### Development Server
```bash
python main.py api --reload --host 0.0.0.0 --port 8000
```

Access API at: `http://localhost:8000/docs`

### Production Server
```bash
# Using uvicorn directly
uvicorn src.api:app --host 0.0.0.0 --port 8000 --workers 4

# Or using main.py
AQUILA_ENV=production python main.py api --workers 4
```

### Run Tests
```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html
```

## Docker Deployment

### Build Docker Image
```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy application
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "main.py", "api"]
```

### Build and Run
```bash
# Build image
docker build -t aquila-trace:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -e AQUILA_ENV=production \
  -e AQUILA_POSTGRES_URL=postgresql://user:password@postgres:5432/aquila_trace \
  -e AQUILA_REDIS_URL=redis://redis:6379/0 \
  --name aquila-trace \
  aquila-trace:latest

# View logs
docker logs -f aquila-trace
```

## Kubernetes Deployment

### Create ConfigMap
```bash
kubectl create configmap aquila-config \
  --from-file=configs/default_config.yaml
```

### Deploy to Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aquila-trace
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aquila-trace
  template:
    metadata:
      labels:
        app: aquila-trace
    spec:
      containers:
      - name: aquila-trace
        image: aquila-trace:latest
        ports:
        - containerPort: 8000
          name: api
        env:
        - name: AQUILA_ENV
          value: "production"
        - name: AQUILA_POSTGRES_URL
          valueFrom:
            secretKeyRef:
              name: aquila-secrets
              key: postgres-url
        - name: AQUILA_REDIS_URL
          valueFrom:
            secretKeyRef:
              name: aquila-secrets
              key: redis-url
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: aquila-trace-service
spec:
  selector:
    app: aquila-trace
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f aquila-k8s.yaml
```

## Performance Optimization

### GPU Support
```bash
# Install CUDA support
pip install torch --index-url https://download.pytorch.org/whl/cu118

# Verify GPU
python -c "import torch; print(torch.cuda.is_available())"
```

### Caching
Configure Redis caching in `.env`:
```
AQUILA_ENABLE_CACHING=true
AQUILA_REDIS_URL=redis://localhost:6379/0
```

### Database Optimization
```sql
-- Create indexes for common queries
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX idx_transactions_source ON transactions(source);
CREATE INDEX idx_transactions_destination ON transactions(destination);
CREATE INDEX idx_addresses_address ON addresses(address);
```

### Monitoring
```bash
# Start Prometheus metrics
# Add monitoring endpoints to your config
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Connection Error
```bash
# Test connection
psql -U aquila -d aquila_trace -h localhost

# Check PostgreSQL service
systemctl status postgresql
```

### Out of Memory
```bash
# Increase batch size or reduce model size
# Edit configs/default_config.yaml:
# batch_size: 16 (reduce from 32)
# embedding_dim: 128 (reduce from 256)
```

### GPU Memory Errors
```bash
# Use CPU instead
AQUILA_DEVICE=cpu python main.py api
```

## Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database connection
python -c "from src.core.config import Config; from sqlalchemy import create_engine; print('OK' if create_engine(Config().database_config.postgres_url).connect() else 'FAILED')"

# Redis
redis-cli ping
```

## Backup and Recovery

```bash
# Backup PostgreSQL database
pg_dump -U aquila aquila_trace > backup.sql

# Restore
psql -U aquila aquila_trace < backup.sql

# Backup MongoDB collections
mongodump --db aquila_trace --out ./backup

# Restore
mongorestore --db aquila_trace ./backup/aquila_trace
```

## Scaling Considerations

1. **Horizontal Scaling**: Add more API instances behind load balancer
2. **Database Scaling**: Use PostgreSQL replication for read scaling
3. **Caching**: Implement Redis clustering for cache scaling
4. **Model Serving**: Deploy models to separate inference service
5. **Job Queue**: Use Celery/RQ for background processing

## Support

For issues or questions:
- Check logs: `tail -f logs/aquila_trace.log`
- Review documentation: https://aquila-trace.readthedocs.io
- Create GitHub issue: https://github.com/aquilatrace/aquila-trace/issues
