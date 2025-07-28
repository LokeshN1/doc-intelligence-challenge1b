"""
Persona-aware document analysis utilities.
"""

import logging
from typing import List, Dict, Any
import re
from models.embeddings import EmbeddingEngine

logger = logging.getLogger(__name__)

class PersonaAnalyzer:
    """Analyzes documents with persona context."""
    
    def __init__(self, embedding_engine: EmbeddingEngine):
        """
        Initialize persona analyzer.
        
        Args:
            embedding_engine: Embedding engine instance
        """
        self.embedding_engine = embedding_engine
    
    def analyze_documents(self, documents: List[Dict], persona: str, job_to_be_done: str) -> Dict[str, Any]:
        """
        Analyze documents with persona context.
        
        Args:
            documents: List of document dictionaries
            persona: Persona description
            job_to_be_done: Job to be done description
            
        Returns:
            Analysis results with sections and subsections
        """
        logger.info("Starting persona-aware document analysis...")
        
        # Create context for analysis
        context = f"{persona} needs to {job_to_be_done}"
        
        sections = []
        subsections = []
        
        for doc in documents:
            doc_sections = self._analyze_document_sections(
                doc, context, persona, job_to_be_done
            )
            
            sections.extend(doc_sections['sections'])
            subsections.extend(doc_sections['subsections'])
        
        logger.info(f"Analysis complete: {len(sections)} sections, {len(subsections)} subsections")
        
        return {
            'sections': sections,
            'subsections': subsections,
            'context': context
        }
    
    def _analyze_document_sections(self, document: Dict, context: str, persona: str, job_to_be_done: str) -> Dict[str, List]:
        """
        Analyze sections of a single document.

        Args:
            document: Document dictionary
            context: Analysis context
            persona: Persona description
            job_to_be_done: Job description

        Returns:
            Dictionary with sections and subsections
        """
        sections = []
        subsections = []

        for section in document['sections']:
            # Analyze section relevance
            section_relevance = self._compute_section_relevance(
                section, context, persona, job_to_be_done
            )

            if section_relevance > 0.3:  # Threshold for relevance
                sections.append({
                    'document': section['document'],
                    'section_title': section['section_title'],
                    'page_number': section['page_number'],
                    'content': section['content'],
                    'relevance_score': section_relevance,
                    'persona_match': self._assess_persona_match(section['content'], persona),
                    'job_relevance': self._assess_job_relevance(section['content'], job_to_be_done)
                })

                # Extract subsections
                section_subsections = self._extract_subsections(section, context, persona, job_to_be_done)
                subsections.extend(section_subsections)

        # Return the full list of subsections, not the last section's subsections
        return {'sections': sections, 'subsections': subsections}

    
    def _compute_section_relevance(self, section: Dict, context: str, persona: str, job_to_be_done: str) -> float:
        """
        Compute relevance score for a section.
        
        Args:
            section: Section dictionary
            context: Analysis context
            persona: Persona description
            job_to_be_done: Job description
            
        Returns:
            Relevance score (0-1)
        """
        # Combine section title and content for analysis
        section_text = f"{section['section_title']} {section['content'][:500]}"
        
        # Compute semantic similarity with context
        similarity = self.embedding_engine.compute_similarity(section_text, context)
        
        # Boost for persona-specific keywords
        persona_boost = self._get_persona_boost(section_text, persona)
        
        # Boost for job-specific keywords
        job_boost = self._get_job_boost(section_text, job_to_be_done)
        
        # Combined score
        relevance = similarity + (persona_boost * 0.2) + (job_boost * 0.2)
        
        return min(1.0, relevance)
    
    def _extract_subsections(self, section: Dict, context: str, persona: str, job_to_be_done: str) -> List[Dict]:
        """
        Extract and analyze subsections from a section.
        
        Args:
            section: Section dictionary
            context: Analysis context
            persona: Persona description
            job_to_be_done: Job description
            
        Returns:
            List of subsection dictionaries
        """
        subsections = []
        content = section['content']
        
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n') if p.strip() and len(p.strip()) > 100]
        
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph) < 100:  # Skip very short paragraphs
                continue
            
            # Compute relevance
            relevance = self.embedding_engine.compute_similarity(paragraph, context)
            
            if relevance > 0.4:  # Higher threshold for subsections
                subsections.append({
                    'document': section['document'],
                    'section_title': section['section_title'],
                    'refined_text': paragraph,
                    'page_number': section['page_number'],
                    'relevance_score': relevance,
                    'subsection_index': i
                })
        
        return subsections
    
    def _assess_persona_match(self, content: str, persona: str) -> float:
        """Assess how well content matches the persona."""
        return self.embedding_engine.compute_similarity(content, persona)
    
    def _assess_job_relevance(self, content: str, job_to_be_done: str) -> float:
        """Assess how relevant content is to the job."""
        return self.embedding_engine.compute_similarity(content, job_to_be_done)
    
    def _get_persona_boost(self, text: str, persona: str) -> float:
        """Get boost score based on persona-specific keywords."""
        persona_lower = persona.lower()
        text_lower = text.lower()
        
        boost = 0.0
        
        # Extract key terms from persona
        if 'researcher' in persona_lower:
            keywords = ['research', 'study', 'analysis', 'methodology', 'findings', 'literature']
        elif 'student' in persona_lower:
            keywords = ['learn', 'understand', 'concept', 'example', 'definition', 'explanation']
        elif 'analyst' in persona_lower:
            keywords = ['data', 'trend', 'performance', 'metrics', 'analysis', 'insights']
        else:
            keywords = []
        
        for keyword in keywords:
            if keyword in text_lower:
                boost += 0.1
        
        return min(0.5, boost)
    
    def _get_job_boost(self, text: str, job_to_be_done: str) -> float:
        """Get boost score based on job-specific keywords."""
        job_lower = job_to_be_done.lower()
        text_lower = text.lower()
        
        boost = 0.0
        
        # Extract key terms from job description
        job_keywords = re.findall(r'\b\w+\b', job_lower)
        important_keywords = [w for w in job_keywords if len(w) > 4 and w not in ['that', 'with', 'from', 'this', 'they']]
        
        for keyword in important_keywords[:10]:  # Limit to top 10 keywords
            if keyword in text_lower:
                boost += 0.05
        
        return min(0.3, boost)
