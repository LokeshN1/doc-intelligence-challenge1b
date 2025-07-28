"""
Ranking engine for section and subsection prioritization.
"""

import logging
from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from models.embeddings import EmbeddingEngine

logger = logging.getLogger(__name__)

class RankingEngine:
    """Handles ranking of sections and subsections."""
    
    def __init__(self, embedding_engine: EmbeddingEngine):
        """
        Initialize ranking engine.
        
        Args:
            embedding_engine: Embedding engine instance
        """
        self.embedding_engine = embedding_engine
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def rank_sections(self, sections: List[Dict], persona: str, job_to_be_done: str) -> List[Dict]:
        """
        Rank sections based on relevance to persona and job.
        
        Args:
            sections: List of section dictionaries
            persona: Persona description
            job_to_be_done: Job description
            
        Returns:
            Ranked list of sections
        """
        if not sections:
            return []
        
        logger.info(f"Ranking {len(sections)} sections...")
        
        # Create query context
        query = f"{persona} {job_to_be_done}"
        
        # Compute hybrid scores
        for i, section in enumerate(sections):
            hybrid_score = self._compute_hybrid_score(
                section, query, persona, job_to_be_done
            )
            section['final_score'] = hybrid_score
            section['importance_rank'] = i  # Will be updated after sorting
        
        # Sort by final score
        sections.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Update importance ranks
        for i, section in enumerate(sections):
            section['importance_rank'] = i
        
        # Apply diversity filter to prevent over-representation
        ranked_sections = self._apply_diversity_filter(sections)
        
        logger.info(f"Section ranking complete. Top score: {ranked_sections[0]['final_score']:.3f}")
        
        return ranked_sections
    
    def rank_subsections(self, subsections: List[Dict], persona: str, job_to_be_done: str) -> List[Dict]:
        """
        Rank subsections based on relevance.
        
        Args:
            subsections: List of subsection dictionaries
            persona: Persona description
            job_to_be_done: Job description
            
        Returns:
            Ranked list of subsections
        """
        if not subsections:
            return []
        
        logger.info(f"Ranking {len(subsections)} subsections...")
        
        query = f"{persona} {job_to_be_done}"
        
        # Compute scores for subsections
        for subsection in subsections:
            hybrid_score = self._compute_hybrid_score(
                subsection, query, persona, job_to_be_done, is_subsection=True
            )
            subsection['final_score'] = hybrid_score
        
        # Sort by score
        subsections.sort(key=lambda x: x['final_score'], reverse=True)
        
        logger.info(f"Subsection ranking complete. Top score: {subsections[0]['final_score']:.3f}")
        
        return subsections
    
    def _compute_hybrid_score(self, item: Dict, query: str, persona: str, job_to_be_done: str, is_subsection: bool = False) -> float:
        """
        Compute hybrid ranking score combining multiple factors.
        
        Args:
            item: Section or subsection dictionary
            query: Query context
            persona: Persona description
            job_to_be_done: Job description
            is_subsection: Whether item is a subsection
            
        Returns:
            Hybrid score
        """
        # Get text content
        if is_subsection:
            text = item.get('refined_text', '')
        else:
            text = f"{item.get('section_title', '')} {item.get('content', '')}"
        
        if not text:
            return 0.0
        
        # 1. Semantic similarity (70% weight)
        semantic_score = self.embedding_engine.compute_similarity(text, query)
        
        # 2. TF-IDF similarity (20% weight)
        tfidf_score = self._compute_tfidf_similarity(text, query)
        
        # 3. Position boost (10% weight) - earlier sections get slight boost
        position_boost = self._get_position_boost(item)
        
        # 4. Existing relevance score bonus
        existing_relevance = item.get('relevance_score', 0.0)
        
        # Combine scores
        hybrid_score = (
            semantic_score * 0.7 +
            tfidf_score * 0.2 +
            position_boost * 0.1 +
            existing_relevance * 0.1
        )
        
        return min(1.0, hybrid_score)
    
    def _compute_tfidf_similarity(self, text: str, query: str) -> float:
        """
        Compute TF-IDF based similarity.
        
        Args:
            text: Text to compare
            query: Query text
            
        Returns:
            TF-IDF similarity score
        """
        try:
            # Fit TF-IDF on both texts
            corpus = [text, query]
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)
            
            # Compute cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
        
        except Exception as e:
            logger.warning(f"TF-IDF computation failed: {e}")
            return 0.0
    
    def _get_position_boost(self, item: Dict) -> float:
        """
        Get position-based boost score.
        
        Args:
            item: Section or subsection dictionary
            
        Returns:
            Position boost score
        """
        page_number = item.get('page_number', 1)
        
        # Earlier pages get higher boost
        if page_number <= 3:
            return 0.3
        elif page_number <= 10:
            return 0.2
        else:
            return 0.1
    
    def _apply_diversity_filter(self, sections: List[Dict], max_per_doc: int = 3) -> List[Dict]:
        """
        Apply diversity filter to prevent over-representation from single documents.
        
        Args:
            sections: Ranked sections
            max_per_doc: Maximum sections per document
            
        Returns:
            Filtered sections with diversity
        """
        doc_counts = {}
        filtered_sections = []
        
        for section in sections:
            doc_name = section.get('document', '')
            current_count = doc_counts.get(doc_name, 0)
            
            if current_count < max_per_doc:
                filtered_sections.append(section)
                doc_counts[doc_name] = current_count + 1
            elif len(filtered_sections) < 10:  # Always keep top 10 regardless
                filtered_sections.append(section)
        
        # Update ranks after filtering
        for i, section in enumerate(filtered_sections):
            section['importance_rank'] = i
        
        return filtered_sections
