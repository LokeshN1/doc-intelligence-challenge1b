"""
Embedding engine for semantic similarity computation.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
import logging
from typing import List, Union
import torch

logger = logging.getLogger(__name__)

class EmbeddingEngine:
    """Handles text embeddings and similarity computations."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize embedding engine.
        
        Args:
            model_name: Name of the sentence transformer model
        """
        logger.info(f"Loading embedding model: {model_name}")
        
        # Ensure CPU-only execution
        torch.set_num_threads(4)
        device = 'cpu'
        
        self.model = SentenceTransformer(model_name, device=device)
        self.model_name = model_name
        
        logger.info("Embedding model loaded successfully")
    
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Encode texts into embeddings.
        
        Args:
            texts: Single text or list of texts
            
        Returns:
            Numpy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
        
        # Encode with optimized parameters for CPU
        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            convert_to_tensor=False,
            normalize_embeddings=True
        )
        
        return embeddings
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        embeddings = self.encode([text1, text2])
        
        # Compute cosine similarity
        similarity = np.dot(embeddings[0], embeddings[1])
        return float(similarity)
    
    def compute_similarities(self, query: str, texts: List[str]) -> List[float]:
        """
        Compute similarities between query and multiple texts.
        
        Args:
            query: Query text
            texts: List of texts to compare against
            
        Returns:
            List of similarity scores
        """
        all_texts = [query] + texts
        embeddings = self.encode(all_texts)
        
        query_embedding = embeddings[0]
        text_embeddings = embeddings[1:]
        
        similarities = []
        for text_embedding in text_embeddings:
            similarity = np.dot(query_embedding, text_embedding)
            similarities.append(float(similarity))
        
        return similarities
    
    def create_context_embedding(self, persona: str, job_to_be_done: str) -> np.ndarray:
        """
        Create context embedding from persona and job description.
        
        Args:
            persona: Persona description
            job_to_be_done: Job to be done description
            
        Returns:
            Context embedding
        """
        context_text = f"Persona: {persona}. Task: {job_to_be_done}"
        return self.encode(context_text)
