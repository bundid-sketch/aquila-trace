"""Graph analysis utilities for transaction networks."""
import logging
from typing import List, Dict, Any

import pandas as pd
import networkx as nx

logger = logging.getLogger(__name__)


def build_transaction_graph(df: pd.DataFrame) -> nx.DiGraph:
    """
    Build a directed graph from transaction data.
    
    Args:
        df: DataFrame with columns 'sender', 'receiver', and 'amount'.
        
    Returns:
        Directed graph with transaction information.
    """
    try:
        if "sender" not in df.columns or "receiver" not in df.columns:
            logger.warning("Missing sender/receiver columns. Creating empty graph.")
            return nx.DiGraph()
        
        G = nx.from_pandas_edgelist(
            df,
            source="sender",
            target="receiver",
            edge_attr="amount" if "amount" in df.columns else None,
            create_using=nx.DiGraph()
        )
        
        logger.info(f"Built transaction graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        return G
    except Exception as e:
        logger.error(f"Error building transaction graph: {e}")
        return nx.DiGraph()


def find_key_nodes(G: nx.DiGraph, top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Find key nodes in the transaction network using multiple centrality measures.
    
    Args:
        G: Transaction graph.
        top_n: Number of top nodes to return.
        
    Returns:
        List of dicts with node info and centrality scores.
    """
    if not G.nodes():
        logger.warning("Empty graph provided")
        return []
    
    try:
        # Calculate different centrality measures
        in_degree = dict(G.in_degree())
        out_degree = dict(G.out_degree())
        betweenness = nx.betweenness_centrality(G)
        
        # Normalize and combine scores
        key_nodes = []
        for node in G.nodes():
            combined_score = (
                in_degree.get(node, 0) * 0.3 +
                out_degree.get(node, 0) * 0.3 +
                betweenness.get(node, 0) * 0.4
            )
            
            key_nodes.append({
                "node": str(node),
                "in_degree": in_degree.get(node, 0),
                "out_degree": out_degree.get(node, 0),
                "betweenness": float(betweenness.get(node, 0)),
                "combined_score": float(combined_score)
            })
        
        # Sort by combined score and return top N
        key_nodes = sorted(key_nodes, key=lambda x: x["combined_score"], reverse=True)[:top_n]
        logger.info(f"Found {len(key_nodes)} key nodes")
        return key_nodes
    except Exception as e:
        logger.error(f"Error finding key nodes: {e}")
        return []


def get_graph_statistics(G: nx.DiGraph) -> Dict[str, Any]:
    """
    Get overall statistics about the transaction graph.
    
    Args:
        G: Transaction graph.
        
    Returns:
        Dictionary with graph statistics.
    """
    try:
        stats = {
            "num_nodes": G.number_of_nodes(),
            "num_edges": G.number_of_edges(),
            "density": nx.density(G),
            "is_connected": nx.is_strongly_connected(G),
            "num_weakly_connected_components": nx.number_weakly_connected_components(G)
        }
        return stats
    except Exception as e:
        logger.error(f"Error calculating graph statistics: {e}")
        return {}
