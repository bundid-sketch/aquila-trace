"""Natural Language Processing module for cyber intelligence and financial communication analysis."""

from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import logging
from abc import ABC, abstractmethod

import torch
from transformers import AutoTokenizer, AutoModel, pipeline
import spacy
from sentence_transformers import SentenceTransformer
import fasttext


logger = logging.getLogger(__name__)


class NLPModel(ABC):
    """Base class for NLP models."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
    
    @abstractmethod
    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts to embeddings."""
        pass


class TransformerEmbeddingModel(NLPModel):
    """Transformer-based embedding model using Hugging Face."""
    
    def __init__(self, model_name: str = "bert-base-uncased", device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        super().__init__(model_name)
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(device)
        self.model.eval()
        logger.info(f"Loaded transformer model: {model_name}")
    
    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Encode texts using transformer model."""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            encoded = self.tokenizer(batch, padding=True, truncation=True, return_tensors="pt")
            
            with torch.no_grad():
                encoded = {k: v.to(self.device) for k, v in encoded.items()}
                outputs = self.model(**encoded)
                # Use [CLS] token embedding
                batch_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
            
            embeddings.append(batch_embeddings)
        
        return np.vstack(embeddings) if embeddings else np.array([])


class SentenceTransformerModel(NLPModel):
    """Sentence Transformer for semantic similarity."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        super().__init__(model_name)
        self.model = SentenceTransformer(model_name)
        logger.info(f"Loaded Sentence Transformer model: {model_name}")
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts using Sentence Transformer."""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings


class FinBERTModel(NLPModel):
    """Domain-adapted FinBERT for financial communications."""
    
    def __init__(self, model_name: str = "ProsusAI/finbert"):
        super().__init__(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()
        logger.info(f"Loaded FinBERT model: {model_name}")
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode financial texts using FinBERT."""
        embeddings = []
        
        for text in texts:
            encoded = self.tokenizer(text, padding=True, truncation=True, return_tensors="pt")
            
            with torch.no_grad():
                encoded = {k: v.to(self.device) for k, v in encoded.items()}
                outputs = self.model(**encoded)
                embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()
            
            embeddings.append(embedding)
        
        return np.vstack(embeddings) if embeddings else np.array([])


class NamedEntityRecognizer:
    """Extract named entities from text using spaCy."""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(model_name)
        except:
            logger.warning(f"spaCy model {model_name} not found. Installing...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", model_name])
            self.nlp = spacy.load(model_name)
        
        logger.info(f"Loaded spaCy model: {model_name}")
    
    def extract_entities(self, text: str) -> List[Tuple[str, str, int, int]]:
        """
        Extract named entities from text.
        
        Returns:
            List of (text, entity_type, start, end) tuples
        """
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append((ent.text, ent.label_, ent.start_char, ent.end_char))
        
        return entities
    
    def extract_financial_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract financial-specific entities."""
        entities = self.extract_entities(text)
        
        financial_entities = {
            "persons": [],
            "organizations": [],
            "money": [],
            "dates": [],
            "locations": [],
        }
        
        for text_span, ent_type, _, _ in entities:
            if ent_type in ["PERSON", "ORG", "MONEY", "DATE", "GPE", "LOC"]:
                if ent_type == "PERSON":
                    financial_entities["persons"].append(text_span)
                elif ent_type == "ORG":
                    financial_entities["organizations"].append(text_span)
                elif ent_type == "MONEY":
                    financial_entities["money"].append(text_span)
                elif ent_type == "DATE":
                    financial_entities["dates"].append(text_span)
                elif ent_type in ["GPE", "LOC"]:
                    financial_entities["locations"].append(text_span)
        
        return financial_entities


class TextClassifier:
    """Classify texts for financial crime and terrorism financing patterns."""
    
    def __init__(self, classifier_type: str = "zero-shot"):
        self.classifier_type = classifier_type
        
        if classifier_type == "zero-shot":
            self.classifier = pipeline("zero-shot-classification", device=0 if torch.cuda.is_available() else -1)
        else:
            self.classifier = pipeline("text-classification", device=0 if torch.cuda.is_available() else -1)
        
        logger.info(f"Initialized {classifier_type} text classifier")
    
    def classify_scam_message(self, text: str) -> Dict[str, Any]:
        """Detect scam patterns in messages."""
        labels = [
            "advance_fee_fraud",
            "money_laundering",
            "terrorism_financing",
            "legitimate_transaction",
            "suspicious_activity"
        ]
        
        result = self.classifier(text, labels, multi_class=True)
        
        return {
            "text": text,
            "classifications": [
                {"label": label, "score": score}
                for label, score in zip(result["labels"], result["scores"])
            ]
        }
    
    def classify_terror_propaganda(self, text: str) -> Dict[str, Any]:
        """Detect terror-related content and propaganda."""
        labels = [
            "extremist_content",
            "recruitment",
            "fundraising",
            "tactical_discussion",
            "legitimate_content"
        ]
        
        result = self.classifier(text, labels, multi_class=True)
        
        return {
            "text": text,
            "propaganda_score": result["scores"][0],  # Top label score
            "classifications": [
                {"label": label, "score": score}
                for label, score in zip(result["labels"], result["scores"])
            ]
        }


class SemanticSimilarityAnalyzer:
    """Analyze semantic similarity between texts."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        logger.info(f"Initialized Semantic Similarity Analyzer with {model_name}")
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts."""
        embeddings = self.model.encode([text1, text2])
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        return float(similarity)
    
    def find_similar_texts(self, query: str, corpus: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        """Find similar texts in a corpus."""
        query_embedding = self.model.encode(query)
        corpus_embeddings = self.model.encode(corpus)
        
        similarities = []
        for i, corpus_embedding in enumerate(corpus_embeddings):
            similarity = np.dot(query_embedding, corpus_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(corpus_embedding)
            )
            similarities.append((corpus[i], float(similarity)))
        
        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def cluster_texts_by_similarity(self, texts: List[str], similarity_threshold: float = 0.7) -> List[List[int]]:
        """Cluster texts based on semantic similarity."""
        embeddings = self.model.encode(texts)
        
        # Compute similarity matrix
        similarity_matrix = np.zeros((len(texts), len(texts)))
        for i in range(len(texts)):
            for j in range(len(texts)):
                similarity_matrix[i, j] = np.dot(embeddings[i], embeddings[j]) / (
                    np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
                )
        
        # Greedy clustering
        clusters = []
        visited = set()
        
        for i in range(len(texts)):
            if i in visited:
                continue
            
            cluster = [i]
            visited.add(i)
            
            for j in range(i + 1, len(texts)):
                if j not in visited and similarity_matrix[i, j] >= similarity_threshold:
                    cluster.append(j)
                    visited.add(j)
            
            clusters.append(cluster)
        
        return clusters


class MultilingualAnalyzer:
    """Analyze text in multiple African languages."""
    
    def __init__(self):
        try:
            self.fasttext_model = fasttext.load_model("cc.en.300.bin")
        except:
            logger.warning("FastText model not found. Language detection may be limited.")
            self.fasttext_model = None
        
        self.supported_languages = {
            "en": "English",
            "ar": "Arabic",
            "fr": "French",
            "sw": "Swahili",
            "ha": "Hausa",
            "yo": "Yoruba",
            "ig": "Igbo",
        }
        logger.info("Initialized Multilingual Analyzer")
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """Detect language of text."""
        if self.fasttext_model:
            predictions = self.fasttext_model.predict(text.replace('\n', ' '), k=1)
            lang_code = predictions[0][0].replace('__label__', '')
            confidence = predictions[1][0]
            return lang_code, float(confidence)
        
        # Fallback: simple keyword-based detection
        arabic_keywords = ['أن', 'في', 'هو', 'على']
        french_keywords = ['le', 'de', 'et', 'à', 'un']
        
        if any(kw in text for kw in arabic_keywords):
            return "ar", 0.5
        elif any(kw in text for kw in french_keywords):
            return "fr", 0.5
        else:
            return "en", 0.7
    
    def get_language_name(self, lang_code: str) -> str:
        """Get full language name from code."""
        return self.supported_languages.get(lang_code, "Unknown")
    
    def translate_to_english(self, text: str, source_lang: str) -> str:
        """Translate text to English (placeholder)."""
        # In production, use translation API (Google Translate, etc.)
        logger.info(f"Would translate text from {source_lang} to English")
        return text


class CyberIntelligencePipeline:
    """End-to-end pipeline for cyber intelligence and financial communication analysis."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.embedding_model = SentenceTransformerModel()
        self.ner = NamedEntityRecognizer()
        self.classifier = TextClassifier()
        self.similarity_analyzer = SemanticSimilarityAnalyzer()
        self.multilingual = MultilingualAnalyzer()
        logger.info("Initialized Cyber Intelligence Pipeline")
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive text analysis for financial crime detection.
        
        Returns:
            Analysis results including entities, classification, embeddings
        """
        # Language detection
        lang, confidence = self.multilingual.detect_language(text)
        
        # Entity extraction
        entities = self.ner.extract_financial_entities(text)
        
        # Text embedding
        embedding = self.embedding_model.encode([text])[0]
        
        # Classification
        scam_classification = self.classifier.classify_scam_message(text)
        
        analysis = {
            "text": text,
            "language": {
                "code": lang,
                "name": self.multilingual.get_language_name(lang),
                "confidence": float(confidence)
            },
            "entities": entities,
            "embedding": embedding.tolist() if isinstance(embedding, np.ndarray) else embedding,
            "scam_classification": scam_classification,
        }
        
        logger.info(f"Analyzed text: detected {sum(len(v) for v in entities.values())} entities")
        return analysis
    
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze batch of texts."""
        results = []
        for text in texts:
            results.append(self.analyze_text(text))
        return results
