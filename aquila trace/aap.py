from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from dash import Dash, dcc, html

from models.anomaly_detector import AnomalyDetector
from models.risk_scorer import RiskScorer
from analytics.graph_analysis import build_transaction_graph, find_key_nodes
from utils.data_loader import load_transactions, preprocess

app = FastAPI(title="AquilaTrace Full Platform")

@app.get("/analyze")
def analyze_transactions():
    df = load_transactions()
    df = preprocess(df)
    features = df[["log_amount", "cross_border"]]

    anomaly_model = AnomalyDetector()
    anomaly_model.train(features)
    anomalies = anomaly_model.detect(features)
    df["anomaly"] = anomalies

    labels = [0] * len(df)
    risk_model = RiskScorer()
    risk_model.train(features, labels)
    df["risk_score"] = risk_model.score(features)

    G = build_transaction_graph(df)
    key_nodes = find_key_nodes(G)
    suspicious = df[df["anomaly"] == -1]

    return {
        "suspicious_transactions": suspicious.to_dict(orient="records"),
        "high_risk_accounts": key_nodes
    }

dash_app = Dash(__name__)
df = pd.read_csv("data/transactions.csv")
G = nx.from_pandas_edgelist(df, source="sender", target="receiver", edge_attr="amount", create_using=nx.DiGraph())
pos = nx.spring_layout(G, dim=3)

edge_x, edge_y, edge_z = [], [], []
for edge in G.edges():
    x0, y0, z0 = pos[edge[0]]
    x1, y1, z1 = pos[edge[1]]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]
    edge_z += [z0, z1, None]

edge_trace = go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode='lines', line=dict(width=2))
node_x, node_y, node_z = [], [], []
for node in G.nodes():
    x, y, z = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_z.append(z)

node_trace = go.Scatter3d(
    x=node_x, y=node_y, z=node_z,
    mode='markers+text', text=list(G.nodes()), textposition="top center",
    marker=dict(size=6)
)

fig = go.Figure(data=[edge_trace, node_trace])
fig.update_layout(title="AquilaTrace 3D Intelligence Network")

dash_app.layout = html.Div([
    html.H1("AquilaTrace Dashboard"),
    dcc.Graph(figure=fig)
])

app.mount("/dashboard", WSGIMiddleware(dash_app.server))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)