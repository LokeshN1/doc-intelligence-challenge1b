"""
JSON output formatting utilities.
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class JSONFormatter:
    """Handles JSON output formatting according to challenge specifications."""
    
    def format_output(self, documents: List[Dict], persona: str, job_to_be_done: str, 
                     sections: List[Dict], subsections: List[Dict], processing_time: float) -> Dict[str, Any]:
        """
        Format analysis results into required JSON structure.
        
        Args:
            documents: Processed documents
            persona: Persona description
            job_to_be_done: Job description
            sections: Ranked sections
            subsections: Ranked subsections
            processing_time: Processing time in seconds
            
        Returns:
            Formatted output dictionary
        """
        logger.info("Formatting output JSON...")
        
        # Format metadata
        metadata = self._format_metadata(documents, persona, job_to_be_done, processing_time)
        
        # Format extracted sections
        extracted_sections = self._format_extracted_sections(sections)
        
        # Format subsection analysis
        subsection_analysis = self._format_subsection_analysis(subsections)
        
        output = {
            "metadata": metadata,
            "extracted_sections": extracted_sections,
            "subsection_analysis": subsection_analysis
        }
        
        # Validate output
        self._validate_output(output)
        
        logger.info("JSON formatting complete")
        
        return output
    
    def _format_metadata(self, documents: List[Dict], persona: str, job_to_be_done: str, processing_time: float) -> Dict[str, Any]:
        """Format metadata section."""
        input_documents = []
        
        for doc in documents:
            input_documents.append({
                "filename": doc['filename'],
                "pages": doc['total_pages']
            })
        
        return {
            "input_documents": input_documents,
            "persona": persona,
            "job_to_be_done": job_to_be_done,
            "processing_timestamp": datetime.utcnow().isoformat() + "Z",
            "processing_time_seconds": round(processing_time, 2),
            "total_sections_extracted": len(input_documents),
            "system_version": "1.0.0"
        }
    
    def _format_extracted_sections(self, sections: List[Dict]) -> List[Dict[str, Any]]:
        """Format extracted sections."""
        formatted_sections = []
        
        for section in sections[:15]:  # Limit to top 15 sections
            formatted_section = {
                "document": section.get('document', ''),
                "page_number": section.get('page_number', 1),
                "section_title": section.get('section_title', ''),
                "importance_rank": section.get('importance_rank', 0),
                "relevance_score": round(section.get('final_score', 0.0), 3)
            }
            
            formatted_sections.append(formatted_section)
        
        return formatted_sections
    
    def _format_subsection_analysis(self, subsections: List[Dict]) -> List[Dict[str, Any]]:
        """Format subsection analysis."""
        formatted_subsections = []
        
        for subsection in subsections[:20]:  # Limit to top 20 subsections
            formatted_subsection = {
                "document": subsection.get('document', ''),
                "section_title": subsection.get('section_title', ''),
                "refined_text": subsection.get('refined_text', '')[:500],  # Limit text length
                "page_number": subsection.get('page_number', 1),
                "relevance_score": round(subsection.get('final_score', 0.0), 3)
            }
            
            formatted_subsections.append(formatted_subsection)
        
        return formatted_subsections
    
    def _validate_output(self, output: Dict[str, Any]) -> None:
        """Validate output format."""
        required_keys = ['metadata', 'extracted_sections', 'subsection_analysis']
        
        for key in required_keys:
            if key not in output:
                raise ValueError(f"Missing required key: {key}")
        
        # Validate metadata
        metadata_keys = ['input_documents', 'persona', 'job_to_be_done', 'processing_timestamp']
        for key in metadata_keys:
            if key not in output['metadata']:
                raise ValueError(f"Missing metadata key: {key}")
        
        logger.info("Output validation successful")
