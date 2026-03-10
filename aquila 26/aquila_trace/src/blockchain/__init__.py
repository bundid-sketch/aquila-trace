"""Blockchain Analytics module for cryptocurrency transaction analysis."""

from typing import Dict, List, Tuple, Optional, Set, Any
import numpy as np
import logging
from abc import ABC, abstractmethod
import hashlib
import requests
from collections import defaultdict, deque


logger = logging.getLogger(__name__)


class BlockchainAddress:
    """Represents a blockchain address with behavioral patterns."""
    
    def __init__(self, address: str, chain: str = "bitcoin"):
        self.address = address
        self.chain = chain
        self.transactions = []
        self.balance = 0.0
        self.first_seen = None
        self.last_seen = None
        self.transaction_count = 0
        self.fingerprint = None
        self.tags = set()
        self.risk_score = 0.0
    
    def add_fingerprint_features(self, features: Dict[str, Any]) -> None:
        """Add behavioral fingerprint features."""
        self.fingerprint = features
    
    def calculate_risk_score(self) -> float:
        """Calculate address risk score based on behavioral patterns."""
        score = 0.0
        
        # High transaction frequency
        if self.transaction_count > 1000:
            score += 0.3
        elif self.transaction_count > 100:
            score += 0.1
        
        # Address reuse across multiple wallets
        if "reused" in self.tags:
            score += 0.2
        
        # Connection to known bad actors
        if "high_risk_connection" in self.tags:
            score += 0.4
        
        # Mixer/tumbler usage
        if "mixer_interaction" in self.tags:
            score += 0.35
        
        self.risk_score = min(score, 1.0)
        return self.risk_score


class TransactionGraph:
    """Graph structure for cryptocurrency transaction networks."""
    
    def __init__(self):
        self.addresses: Dict[str, BlockchainAddress] = {}
        self.edges: List[Tuple[str, str, float, str]] = []  # (src, dst, amount, txid)
        self.clusters: List[Set[str]] = []
    
    def add_address(self, address: str, chain: str = "bitcoin") -> BlockchainAddress:
        """Add address to graph."""
        if address not in self.addresses:
            self.addresses[address] = BlockchainAddress(address, chain)
        return self.addresses[address]
    
    def add_transaction(self, src: str, dst: str, amount: float, txid: str, timestamp: int) -> None:
        """Add transaction edge to graph."""
        self.add_address(src)
        self.add_address(dst)
        
        self.addresses[src].transactions.append({
            'txid': txid,
            'to': dst,
            'amount': amount,
            'timestamp': timestamp,
            'type': 'outgoing'
        })
        
        self.addresses[dst].transactions.append({
            'txid': txid,
            'from': src,
            'amount': amount,
            'timestamp': timestamp,
            'type': 'incoming'
        })
        
        self.edges.append((src, dst, amount, txid))
    
    def get_address_balance(self, address: str) -> float:
        """Calculate current balance of address."""
        if address not in self.addresses:
            return 0.0
        
        addr = self.addresses[address]
        balance = 0.0
        for tx in addr.transactions:
            if tx['type'] == 'incoming':
                balance += tx['amount']
            else:
                balance -= tx['amount']
        
        addr.balance = balance
        return balance


class MixerDetector:
    """Detect mixer/tumbler usage patterns."""
    
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold
    
    def detect_mixer_pattern(self, graph: TransactionGraph, address: str) -> Tuple[bool, float]:
        """
        Detect if address interacts with mixers.
        
        Returns:
            (is_mixer_interaction, confidence_score)
        """
        if address not in graph.addresses:
            return False, 0.0
        
        addr = graph.addresses[address]
        mixer_indicators = 0.0
        
        # Multiple outputs from single input (hops through mixer)
        if len(addr.transactions) > 0:
            inputs = sum(1 for tx in addr.transactions if tx['type'] == 'incoming')
            outputs = sum(1 for tx in addr.transactions if tx['type'] == 'outgoing')
            
            if inputs > 0 and outputs / inputs > 3:
                mixer_indicators += 0.3
        
        # Rapid transaction sequence (typical of mixers)
        if len(addr.transactions) > 1:
            timestamps = sorted([tx['timestamp'] for tx in addr.transactions])
            time_diffs = np.diff(timestamps)
            
            if len(time_diffs) > 0 and np.mean(time_diffs) < 3600:  # < 1 hour average
                mixer_indicators += 0.25
        
        # Very fast fund movement (mixing characteristic)
        if len(addr.transactions) > 10:
            ratio = sum(1 for tx in addr.transactions if tx['type'] == 'outgoing') / len(addr.transactions)
            if ratio > 0.8:
                mixer_indicators += 0.3
        
        return mixer_indicators >= self.threshold, mixer_indicators
    
    def detect_mixer_cluster(self, graph: TransactionGraph) -> List[Set[str]]:
        """Detect clusters of addresses that are mixers."""
        mixer_clusters = []
        
        for address in graph.addresses:
            is_mixer, score = self.detect_mixer_pattern(graph, address)
            if is_mixer:
                graph.addresses[address].tags.add("mixer_interaction")
        
        return mixer_clusters


class Smurf ingDetector:
    """Detect structuring/smurfing patterns (coordinated small transactions)."""
    
    def __init__(self, amount_threshold: float = 10000, time_window: int = 86400):
        self.amount_threshold = amount_threshold
        self.time_window = time_window
    
    def detect_smurfing(self, graph: TransactionGraph, 
                       addresses: List[str]) -> Tuple[bool, float]:
        """
        Detect smurfing pattern (multiple small coordinated transactions).
        
        Returns:
            (is_smurfing, confidence_score)
        """
        if len(addresses) < 2:
            return False, 0.0
        
        transactions = []
        for addr in addresses:
            if addr in graph.addresses:
                transactions.extend(graph.addresses[addr].transactions)
        
        if not transactions:
            return False, 0.0
        
        # Check for similar amounts
        amounts = [tx['amount'] for tx in transactions]
        if len(amounts) > 0:
            std_dev = np.std(amounts)
            mean_amount = np.mean(amounts)
            
            # Low variance in amounts is suspicious
            if std_dev < mean_amount * 0.1:  # Coefficient of variation < 0.1
                # Check timing coordination
                timestamps = [tx['timestamp'] for tx in transactions]
                time_diffs = np.diff(sorted(timestamps))
                
                if len(time_diffs) > 0 and np.mean(time_diffs) < self.time_window:
                    return True, 0.8
        
        return False, 0.3


class AddressClusterer:
    """Cluster addresses likely to be controlled by same entity."""
    
    def cluster_by_common_input(self, graph: TransactionGraph) -> List[Set[str]]:
        """
        Heuristic clustering: addresses that share common inputs.
        Used to identify wallets controlled by same user.
        """
        clusters = []
        clustered = set()
        
        # Build mapping of inputs to outputs
        input_to_outputs = defaultdict(set)
        
        for src, dst, _, _ in graph.edges:
            input_to_outputs[src].add(dst)
        
        # Cluster connected addresses
        for source in input_to_outputs:
            if source not in clustered:
                cluster = self._bfs_cluster(source, input_to_outputs, graph.edges)
                if cluster:
                    clusters.append(cluster)
                    clustered.update(cluster)
        
        return clusters
    
    def _bfs_cluster(self, start: str, input_to_outputs: Dict, 
                     edges: List[Tuple[str, str, float, str]]) -> Set[str]:
        """BFS-based clustering."""
        cluster = set()
        queue = deque([start])
        visited = {start}
        
        while queue:
            node = queue.popleft()
            cluster.add(node)
            
            # Add related addresses
            if node in input_to_outputs:
                for output in input_to_outputs[node]:
                    if output not in visited:
                        visited.add(output)
                        queue.append(output)
        
        return cluster if len(cluster) > 1 else set()


class BlockchainAnalyzer:
    """Main blockchain analytics engine."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.graph = TransactionGraph()
        self.mixer_detector = MixerDetector()
        self.smurfing_detector = Smurf ingDetector()
        self.address_clusterer = AddressClusterer()
        self.known_bad_addresses = set()
        logger.info("Initialized Blockchain Analyzer")
    
    def add_known_bad_address(self, address: str, reason: str = "") -> None:
        """Register known high-risk address."""
        self.known_bad_addresses.add(address)
    
    def analyze_address(self, address: str) -> Dict[str, Any]:
        """Comprehensive analysis of a blockchain address."""
        if address not in self.graph.addresses:
            addr_obj = self.graph.add_address(address)
        else:
            addr_obj = self.graph.addresses[address]
        
        # Check against known bad addresses
        if address in self.known_bad_addresses:
            addr_obj.tags.add("high_risk_connection")
        
        # Detect mixer interaction
        is_mixer, mixer_score = self.mixer_detector.detect_mixer_pattern(self.graph, address)
        if is_mixer:
            addr_obj.tags.add("mixer_interaction")
        
        # Calculate risk score
        risk_score = addr_obj.calculate_risk_score()
        
        analysis = {
            "address": address,
            "balance": self.graph.get_address_balance(address),
            "transaction_count": len(addr_obj.transactions),
            "tags": list(addr_obj.tags),
            "risk_score": risk_score,
            "mixer_score": mixer_score,
            "is_mixer": is_mixer,
        }
        
        logger.info(f"Analyzed address {address}: risk_score={risk_score:.2f}")
        return analysis
    
    def detect_coordinated_behavior(self, addresses: List[str]) -> Dict[str, Any]:
        """Detect coordinated financial behavior across multiple addresses."""
        is_smurfing, smurfing_score = self.smurfing_detector.detect_smurfing(
            self.graph, addresses
        )
        
        # Detect common connections
        common_sources = None
        common_destinations = None
        
        for addr in addresses:
            if addr in self.graph.addresses:
                sources = set(tx.get('from') for tx in self.graph.addresses[addr].transactions 
                            if tx['type'] == 'incoming')
                dests = set(tx.get('to') for tx in self.graph.addresses[addr].transactions 
                           if tx['type'] == 'outgoing')
                
                if common_sources is None:
                    common_sources = sources
                    common_destinations = dests
                else:
                    common_sources &= sources
                    common_destinations &= dests
        
        return {
            "addresses": addresses,
            "is_smurfing": is_smurfing,
            "smurfing_score": smurfing_score,
            "common_sources": list(common_sources) if common_sources else [],
            "common_destinations": list(common_destinations) if common_destinations else [],
        }
    
    def analyze_transaction_flow(self, source_address: str, depth: int = 3) -> Dict[str, Any]:
        """Trace and analyze transaction flow from source address."""
        visited = set()
        flow_tree = {}
        
        def traverse(address: str, current_depth: int):
            if current_depth > depth or address in visited:
                return {}
            
            visited.add(address)
            addr_info = self.analyze_address(address)
            
            next_hops = {}
            if address in self.graph.addresses:
                for tx in self.graph.addresses[address].transactions:
                    if tx['type'] == 'outgoing':
                        next_addr = tx.get('to')
                        if next_addr and next_addr not in visited:
                            next_hops[next_addr] = traverse(next_addr, current_depth + 1)
            
            addr_info['next_hops'] = next_hops
            return addr_info
        
        flow_tree = traverse(source_address, 0)
        
        return {
            "source": source_address,
            "max_depth": depth,
            "flow_analysis": flow_tree,
        }
    
    def cluster_addresses(self) -> List[Set[str]]:
        """Cluster addresses likely controlled by same entity."""
        clusters = self.address_clusterer.cluster_by_common_input(self.graph)
        self.graph.clusters = clusters
        logger.info(f"Identified {len(clusters)} address clusters")
        return clusters
    
    def generate_risk_report(self) -> Dict[str, Any]:
        """Generate comprehensive risk report for all addresses."""
        high_risk = []
        medium_risk = []
        low_risk = []
        
        for address, addr_obj in self.graph.addresses.items():
            analysis = self.analyze_address(address)
            risk_score = analysis['risk_score']
            
            if risk_score >= 0.7:
                high_risk.append((address, risk_score))
            elif risk_score >= 0.4:
                medium_risk.append((address, risk_score))
            else:
                low_risk.append((address, risk_score))
        
        # Sort by risk score
        high_risk.sort(key=lambda x: x[1], reverse=True)
        medium_risk.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "total_addresses": len(self.graph.addresses),
            "high_risk_count": len(high_risk),
            "medium_risk_count": len(medium_risk),
            "low_risk_count": len(low_risk),
            "high_risk_addresses": high_risk[:20],  # Top 20
            "medium_risk_addresses": medium_risk[:20],
            "total_clusters": len(self.graph.clusters),
        }
