"""Graph Neural Network module for financial network analysis."""

from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, GATConv, RGCNConv, MessagePassing
from torch_geometric.data import Data, HeteroData, DataLoader
import networkx as nx
from abc import ABC, abstractmethod
import logging


logger = logging.getLogger(__name__)


class GNNModel(nn.Module, ABC):
    """Base class for Graph Neural Network models."""
    
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, 
                 num_layers: int = 3, dropout: float = 0.2):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.num_layers = num_layers
        self.dropout = dropout
    
    @abstractmethod
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor, 
                edge_attr: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass."""
        pass


class GCNModel(GNNModel):
    """Graph Convolutional Network for node classification."""
    
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int = 2,
                 num_layers: int = 3, dropout: float = 0.2):
        super().__init__(input_dim, hidden_dim, output_dim, num_layers, dropout)
        
        self.convs = nn.ModuleList()
        self.bns = nn.ModuleList()
        
        # First layer
        self.convs.append(GCNConv(input_dim, hidden_dim))
        self.bns.append(nn.BatchNorm1d(hidden_dim))
        
        # Hidden layers
        for _ in range(num_layers - 2):
            self.convs.append(GCNConv(hidden_dim, hidden_dim))
            self.bns.append(nn.BatchNorm1d(hidden_dim))
        
        # Output layer
        self.convs.append(GCNConv(hidden_dim, output_dim))
    
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor,
                edge_attr: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass."""
        for i, conv in enumerate(self.convs[:-1]):
            x = conv(x, edge_index)
            x = self.bns[i](x)
            x = F.relu(x)
            x = F.dropout(x, p=self.dropout, training=self.training)
        
        # Output layer (no activation)
        x = self.convs[-1](x, edge_index)
        return x


class GATModel(GNNModel):
    """Graph Attention Network for node classification."""
    
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int = 2,
                 num_layers: int = 3, dropout: float = 0.2, heads: int = 8):
        super().__init__(input_dim, hidden_dim, output_dim, num_layers, dropout)
        self.heads = heads
        
        self.convs = nn.ModuleList()
        self.bns = nn.ModuleList()
        
        # First layer
        self.convs.append(GATConv(input_dim, hidden_dim, heads=heads, dropout=dropout))
        self.bns.append(nn.BatchNorm1d(hidden_dim * heads))
        
        # Hidden layers
        for _ in range(num_layers - 2):
            self.convs.append(GATConv(hidden_dim * heads, hidden_dim, heads=heads, dropout=dropout))
            self.bns.append(nn.BatchNorm1d(hidden_dim * heads))
        
        # Output layer
        self.convs.append(GATConv(hidden_dim * heads, output_dim, heads=1, dropout=dropout))
    
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor,
                edge_attr: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass."""
        for i, conv in enumerate(self.convs[:-1]):
            x = conv(x, edge_index)
            x = self.bns[i](x)
            x = F.relu(x)
        
        # Output layer
        x = self.convs[-1](x, edge_index)
        return x


class RGCNModel(GNNModel):
    """Relational Graph Convolutional Network for heterogeneous graphs."""
    
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int = 2,
                 num_layers: int = 3, dropout: float = 0.2, num_relations: int = 10):
        super().__init__(input_dim, hidden_dim, output_dim, num_layers, dropout)
        self.num_relations = num_relations
        
        self.convs = nn.ModuleList()
        self.bns = nn.ModuleList()
        
        # First layer
        self.convs.append(RGCNConv(input_dim, hidden_dim, num_relations=num_relations))
        self.bns.append(nn.BatchNorm1d(hidden_dim))
        
        # Hidden layers
        for _ in range(num_layers - 2):
            self.convs.append(RGCNConv(hidden_dim, hidden_dim, num_relations=num_relations))
            self.bns.append(nn.BatchNorm1d(hidden_dim))
        
        # Output layer
        self.convs.append(RGCNConv(hidden_dim, output_dim, num_relations=num_relations))
    
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor,
                edge_type: torch.Tensor) -> torch.Tensor:
        """Forward pass with relation types."""
        for i, conv in enumerate(self.convs[:-1]):
            x = conv(x, edge_index, edge_type)
            x = self.bns[i](x)
            x = F.relu(x)
            x = F.dropout(x, p=self.dropout, training=self.training)
        
        x = self.convs[-1](x, edge_index, edge_type)
        return x


class LinkPredictor(nn.Module):
    """Module for link prediction in networks."""
    
    def __init__(self, hidden_dim: int):
        super().__init__()
        self.lin1 = nn.Linear(2 * hidden_dim, hidden_dim)
        self.lin2 = nn.Linear(hidden_dim, 1)
    
    def forward(self, z: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """Predict links. z: node embeddings, edge_index: edges to predict."""
        x_i = z[edge_index[0]]
        x_j = z[edge_index[1]]
        x = torch.cat([x_i, x_j], dim=-1)
        x = self.lin1(x)
        x = F.relu(x)
        x = self.lin2(x)
        return x.squeeze()


class FinancialNetworkAnalyzer:
    """Analyze financial networks for terrorism financing patterns."""
    
    def __init__(self, gnn_model: GNNModel, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.gnn_model = gnn_model.to(device)
        self.device = device
        self.link_predictor = LinkPredictor(gnn_model.hidden_dim).to(device)
    
    def build_network_graph(self, 
                           entities: List[str],
                           relationships: List[Tuple[int, int, str]],
                           entity_features: Optional[np.ndarray] = None) -> Data:
        """
        Build a PyTorch Geometric graph from entities and relationships.
        
        Args:
            entities: List of entity IDs (persons, wallets, organizations, etc.)
            relationships: List of (src_idx, dst_idx, relation_type) tuples
            entity_features: Node feature matrix
            
        Returns:
            PyTorch Geometric Data object
        """
        num_nodes = len(entities)
        
        # Create edge index
        edge_index = torch.tensor(
            [[r[0] for r in relationships], [r[1] for r in relationships]],
            dtype=torch.long,
            device=self.device
        )
        
        # Create node features (if not provided, use one-hot encoding)
        if entity_features is None:
            x = torch.eye(num_nodes, dtype=torch.float32, device=self.device)
        else:
            x = torch.tensor(entity_features, dtype=torch.float32, device=self.device)
        
        # Create edge types
        relation_types = [r[2] for r in relationships]
        edge_type_mapping = {rel_type: idx for idx, rel_type in enumerate(set(relation_types))}
        edge_type = torch.tensor(
            [edge_type_mapping[rel_type] for rel_type in relation_types],
            dtype=torch.long,
            device=self.device
        )
        
        graph = Data(x=x, edge_index=edge_index, edge_type=edge_type)
        logger.info(f"Financial network graph created with {num_nodes} nodes and {len(relationships)} edges")
        return graph
    
    def detect_financial_hubs(self, graph: Data, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Detect high-risk financial hubs using node centrality measures.
        
        Args:
            graph: PyTorch Geometric Data object
            top_k: Number of top hubs to return
            
        Returns:
            List of (node_id, centrality_score) tuples
        """
        edge_index = graph.edge_index.cpu().numpy()
        
        # Create NetworkX graph
        G = nx.DiGraph()
        G.add_nodes_from(range(graph.x.shape[0]))
        G.add_edges_from(zip(edge_index[0], edge_index[1]))
        
        # Compute various centrality measures
        betweenness = nx.betweenness_centrality(G)
        closeness = nx.closeness_centrality(G)
        eigenvector = nx.eigenvector_centrality_numpy(G)
        
        # Combine centrality measures
        combined_scores = {}
        for node_id in range(G.number_of_nodes()):
            combined_scores[node_id] = (
                0.4 * betweenness.get(node_id, 0) +
                0.3 * closeness.get(node_id, 0) +
                0.3 * eigenvector.get(node_id, 0)
            )
        
        # Get top-k hubs
        hubs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        logger.info(f"Detected {len(hubs)} financial hubs")
        return hubs
    
    def predict_future_connections(self, graph: Data, top_k: int = 20) -> List[Tuple[int, int, float]]:
        """
        Predict future connections in the financial network using link prediction.
        
        Args:
            graph: PyTorch Geometric Data object
            top_k: Number of top predictions to return
            
        Returns:
            List of (src_node, dst_node, prediction_score) tuples
        """
        self.gnn_model.eval()
        self.link_predictor.eval()
        
        with torch.no_grad():
            # Get node embeddings from GNN
            embeddings = self.gnn_model(graph.x, graph.edge_index, graph.edge_type)
            
            # Generate candidate edges (all non-existing edges)
            known_edges = set(zip(graph.edge_index[0].cpu().numpy(), graph.edge_index[1].cpu().numpy()))
            num_nodes = graph.x.shape[0]
            
            candidates = []
            for i in range(num_nodes):
                for j in range(num_nodes):
                    if i != j and (i, j) not in known_edges:
                        candidates.append((i, j))
            
            # Predict link probabilities
            if candidates:
                candidate_edges = torch.tensor(candidates, dtype=torch.long, device=self.device).t()
                predictions = torch.sigmoid(self.link_predictor(embeddings, candidate_edges))
                
                # Get top-k predictions
                top_indices = torch.topk(predictions, min(top_k, len(candidates)))[1]
                result = []
                for idx in top_indices:
                    src, dst = candidates[idx]
                    score = predictions[idx].item()
                    result.append((int(src), int(dst), float(score)))
                
                logger.info(f"Predicted {len(result)} future connections")
                return result
        
        return []
    
    def detect_suspicious_clusters(self, graph: Data, 
                                   similarity_threshold: float = 0.7) -> List[List[int]]:
        """
        Detect clusters of entities resembling known extremist structures.
        
        Args:
            graph: PyTorch Geometric Data object
            similarity_threshold: Threshold for cluster similarity
            
        Returns:
            List of entity clusters
        """
        self.gnn_model.eval()
        
        with torch.no_grad():
            # Get node embeddings
            embeddings = self.gnn_model(graph.x, graph.edge_index, graph.edge_type)
            
            # Normalize embeddings
            embeddings = F.normalize(embeddings, p=2, dim=1)
            
            # Compute similarity matrix
            similarity_matrix = torch.mm(embeddings, embeddings.t())
            
            # Clustering using similarity threshold
            clusters = []
            visited = set()
            
            for node in range(graph.x.shape[0]):
                if node in visited:
                    continue
                
                cluster = [node]
                visited.add(node)
                
                for other_node in range(graph.x.shape[0]):
                    if other_node not in visited:
                        similarity = similarity_matrix[node, other_node].item()
                        if similarity >= similarity_threshold:
                            cluster.append(other_node)
                            visited.add(other_node)
                
                if len(cluster) > 1:
                    clusters.append(cluster)
            
            logger.info(f"Detected {len(clusters)} suspicious clusters")
            return clusters
    
    def perform_entity_linking(self, entities: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Link related entities across different data sources.
        
        Args:
            entities: Dictionary of entity information
            
        Returns:
            Dictionary mapping entity IDs to linked entities
        """
        links = {}
        
        for entity_id, entity_data in entities.items():
            linked = []
            
            # Link by common attributes (simplified example)
            for other_id, other_data in entities.items():
                if entity_id != other_id:
                    # Check for common attributes
                    common_attrs = set(entity_data.get('attributes', [])) & set(other_data.get('attributes', []))
                    if len(common_attrs) > 0:
                        linked.append(other_id)
            
            links[entity_id] = linked
        
        logger.info(f"Performed entity linking for {len(links)} entities")
        return links
