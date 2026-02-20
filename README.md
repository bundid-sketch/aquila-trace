# aquila-trace
NIRU
Frontend (React)
        ↓
FastAPI Backend
        ↓
MongoDB
        ↓
Anomaly Detection Engine (Scikit-learn ready)
pip install fastapi uvicorn pymongo passlib[bcrypt] python-jose scikit-learn numpy
aquila_trace/
 ├── main.py
 ├── database.py
 ├── models.py
 ├── auth.py
 └── anomaly.py
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["aquila_trace"]
users_collection = db["users"]
logs_collection = db["logs"]
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    password: str

class Log(BaseModel):
    source_ip: str
    event_type: str
    bytes_transferred: int
    timestamp: str
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

SECRET_KEY = "supersecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    import numpy as np
from sklearn.ensemble import IsolationForest

model = IsolationForest(contamination=0.05)

# Dummy initial training
X_train = np.random.rand(100, 2)
model.fit(X_train)

def detect_anomaly(bytes_transferred):
    prediction = model.predict([[bytes_transferred, 0.5]])
    return "anomaly" if prediction[0] == -1 else "normal"
from fastapi import FastAPI, HTTPException, Depends
from models import User, Log
from database import users_collection, logs_collection
from auth import hash_password, verify_password, create_access_token
from anomaly import detect_anomaly

app = FastAPI()

@app.post("/register")
def register(user: User):
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="User exists")
    
    users_collection.insert_one({
        "username": user.username,
        "password": hash_password(user.password)
    })
    return {"message": "User created"}

@app.post("/login")
def login(user: User):
    db_user = users_collection.find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user.username})
    return {"access_token": token}

@app.post("/ingest-log")
def ingest_log(log: Log):
    status = detect_anomaly(log.bytes_transferred)
    
    logs_collection.insert_one({
        "source_ip": log.source_ip,
        "event_type": log.event_type,
        "bytes_transferred": log.bytes_transferred,
        "timestamp": log.timestamp,
        "status": status
    })
    
    return {"status": status}

@app.get("/dashboard")
def dashboard():
    total_logs = logs_collection.count_documents({})
    anomalies = logs_collection.count_documents({"status": "anomaly"})
    
    return {
        "total_logs": total_logs,
        "anomalies": anomalies
    }
    npx create-react-app aquila-ui
cd aquila-ui
npm install axios
import React, { useState } from "react";
import axios from "axios";

function App() {
  const [stats, setStats] = useState(null);

  const fetchDashboard = async () => {
    const res = await axios.get("http://localhost:8000/dashboard");
    setStats(res.data);
  };

  return (
    <div style={{ padding: "40px" }}>
      <h1>AquilaTrace Dashboard</h1>
      <button onClick={fetchDashboard}>Load Stats</button>

      {stats && (
        <div>
          <p>Total Logs: {stats.total_logs}</p>
          <p>Anomalies: {stats.anomalies}</p>
        </div>
      )}
    </div>
  );
}

export default App;
uvicorn main:app --reload
npm start
      ┌─────────────────────────┐
                │   Endpoint / Sensors    │
                │ (EDR, Firewall, IDS)    │
                └───────────┬─────────────┘
                            ↓
                ┌─────────────────────────┐
                │    Log Ingestion API    │
                │  (mTLS + Token Auth)    │
                └───────────┬─────────────┘
                            ↓
                ┌─────────────────────────┐
                │  Kafka Event Streaming  │
                └───────────┬─────────────┘
                            ↓
        ┌────────────────────────────────────────┐
        │  Real-Time Processing Cluster         │
        │ (Flink / Spark Streaming)             │
        └───────────┬─────────────┬─────────────┘
                    ↓             ↓
        ┌─────────────────┐  ┌──────────────────┐
        │ Feature Store   │  │ Threat Intelligence│
        │ (Redis / Feast) │  │ Enrichment Engine  │
        └─────────┬───────┘  └──────────┬───────┘
                  ↓                     ↓
        ┌────────────────────────────────────────┐
        │      ML Detection Microservices        │
        │ IsolationForest / LSTM / GNN           │
        └───────────┬────────────────────────────┘
                    ↓
        ┌─────────────────────────┐
        │  Threat Scoring Engine  │
        └───────────┬─────────────┘
                    ↓
        ┌─────────────────────────┐
        │    SOC Dashboard        │
        │  (Role-Based Access)    │
        └─────────────────────────┘

Risk Score = 
  (Anomaly Score × 0.4)
+ (Threat Intel Match × 0.3)
+ (Behavior Deviation × 0.2)
+ (Privilege Level × 0.1)
                 ┌─────────────────────────┐
                 │   External Sensors      │
                 │ (EDR, IDS, Firewall)    │
                 └───────────┬─────────────┘
                             ↓
                 ┌─────────────────────────┐
                 │  API Gateway (mTLS)     │
                 └───────────┬─────────────┘
                             ↓
                 ┌─────────────────────────┐
                 │ Kafka Event Bus Cluster │
                 └───────────┬─────────────┘
                             ↓
        ┌─────────────────────────────────────────────┐
        │              Processing Layer               │
        └─────────────────────────────────────────────┘
          ↓             ↓             ↓             ↓
  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐
  │ Enrichment │ │ Feature     │ │ ML Inference│ │ Rule Engine │
  │ Service    │ │ Engineering │ │ Service     │ │ Service     │
  └──────┬─────┘ └──────┬─────┘ └──────┬─────┘ └──────┬─────┘
         ↓              ↓              ↓              ↓
               ┌────────────────────────────┐
               │   Threat Scoring Service   │
               └────────────┬───────────────┘
                            ↓
                 ┌─────────────────────────┐
                 │  Alerting Microservice  │
                 └────────────┬────────────┘
                              ↓
                 ┌─────────────────────────┐
                 │   SOC Dashboard (UI)    │
                 └─────────────────────────┘
bytes_zscore
login_fail_rate_5min
hour_of_day
geo_distance_change
privilege_weight
event_frequency
feature_vectors
anomaly_scores
Anomaly score
+ Threat intel weight
+ Privilege level
+ Asset sensitivity
+ Historical risk
aquila-trace-cluster
│
├── namespace: ingestion
├── namespace: processing
├── namespace: ml
├── namespace: dashboard
├── namespace: monitoring
aquila_trace/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── auth.py
│   ├── anomaly.py
│   ├── scoring.py
│   ├── alerts.py
│   └── config.py
│
├── simulate_logs.py
├── requirements.txt
├── .env
└── README.md
pip install python-dotenv
SECRET_KEY=supersecretkey123
MONGO_URI=mongodb://localhost:27017
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
MONGO_URI = os.getenv("MONGO_URI")
from pymongo import MongoClient
from .config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["aquila_trace"]

users_collection = db["users"]
logs_collection = db["logs"]
alerts_collection = db["alerts"]
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    password: str
    role: str = "analyst"  # analyst or admin

class Log(BaseModel):
    source_ip: str
    event_type: str
    bytes_transferred: int
    timestamp: str
    from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from .config import SECRET_KEY

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
        def detect_anomaly(bytes_transferred: int):
    if bytes_transferred > 50000000:
        return 0.95
    elif bytes_transferred > 10000000:
        return 0.75
    elif bytes_transferred < 1000:
        return 0.60
    return 0.10
    def calculate_risk(anomaly_score, event_type):
    weight = 1.0
def calculate_risk(anomaly_score, event_type):
    weight = 1.0

    if event_type == "login_failed":
        weight = 1.2
    elif event_type == "port_scan":
        weight = 1.5
    elif event_type == "file_download":
        weight = 1.3

    risk = anomaly_score * 100 * weight
    return min(int(risk), 100)
    from fastapi import FastAPI, Depends
from .models import User, Log
from .database import users_collection, logs_collection
from .auth import hash_password, verify_password, create_access_token, verify_token
from .anomaly import detect_anomaly
from .scoring import calculate_risk
from .alerts import create_alert

app = FastAPI()

@app.post("/register")
def register(user: User):
    users_collection.insert_one({
        "username": user.username,
        "password": hash_password(user.password),
        "role": user.role
    })
    return {"message": "User created"}

@app.post("/login")
def login(user: User):
    db_user = users_collection.find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["password"]):
        return {"error": "Invalid credentials"}

    token = create_access_token({
        "sub": user.username,
        "role": db_user["role"]
    })

    return {"access_token": token}

@app.post("/ingest-log")
def ingest_log(log: Log, user=Depends(verify_token)):
    anomaly_score = detect_anomaly(log.bytes_transferred)
    risk_score = calculate_risk(anomaly_score, log.event_type)

    log_data = log.dict()
    log_data["risk_score"] = risk_score
    logs_collection.insert_one(log_data)

    create_alert(log_data, risk_score)

    return {"risk_score": risk_score}

@app.get("/alerts")
def get_alerts(user=Depends(verify_token)):
    return list(users_collection.database["alerts"].find({}, {"_id": 0}))
    uvicorn app.main:app --reload
    http://127.0.0.1:8000/docs



