"""
PDF processing utilities for document section extraction.
"""

import fitz  # PyMuPDF
import re
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF text extraction and section identification."""
    
    def __init__(self):
        """Initialize PDF processor."""
        self.section_patterns = [
            r'^(Abstract|Introduction|Background|Literature Review|Methodology|Methods|Results|Discussion|Conclusion|References).*$',
            r'^(\d+\.?\s+[A-Z][^.]*?)$',
            r'^([A-Z][A-Z\s]+)$',
            r'^([A-Z][a-z\s]+:?\s*)$'
        ]
    
    def extract_sections(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract sections from PDF with proper structure detection.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of section dictionaries
        """
        try:
            doc = fitz.open(pdf_path)
            sections = []
            current_section = None
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Extract text with formatting
                blocks = page.get_text("dict")["blocks"]
                
                for block in blocks:
                    if "lines" not in block:
                        continue
                    
                    for line in block["lines"]:
                        line_text = ""
                        font_sizes = []
                        
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text:
                                line_text += text + " "
                                font_sizes.append(span["size"])
                        
                        line_text = line_text.strip()
                        if not line_text:
                            continue
                        
                        # Determine if this is a section header
                        avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 12
                        is_header = self._is_section_header(line_text, avg_font_size)
                        
                        if is_header:
                            # Save previous section
                            if current_section and current_section['content'].strip():
                                sections.append(current_section)
                            
                            # Start new section
                            current_section = {
                                'document': Path(pdf_path).stem,
                                'section_title': line_text,
                                'page_number': page_num + 1,
                                'content': '',
                                'font_size': avg_font_size
                            }
                        else:
                            # Add to current section
                            if current_section:
                                current_section['content'] += line_text + "\n"
                            else:
                                # Create default section if none exists
                                current_section = {
                                    'document': Path(pdf_path).stem,
                                    'section_title': 'Content',
                                    'page_number': page_num + 1,
                                    'content': line_text + "\n",
                                    'font_size': 12
                                }
            
            # Add final section
            if current_section and current_section['content'].strip():
                sections.append(current_section)
            
            doc.close()
            
            # Clean up sections
            sections = self._cleanup_sections(sections)
            
            logger.info(f"Extracted {len(sections)} sections from {pdf_path}")
            return sections
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            return []
    
    def _is_section_header(self, text: str, font_size: float) -> bool:
        """
        Determine if text is likely a section header.
        
        Args:
            text: Text to analyze
            font_size: Font size of the text
            
        Returns:
            True if likely a header
        """
        # Check length (headers are usually short)
        if len(text) > 100:
            return False
        
        # Check against patterns
        for pattern in self.section_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        
        # Check font size (headers are usually larger)
        if font_size > 14:
            return True
        
        # Check if all caps (common for headers)
        if text.isupper() and len(text) > 3:
            return True
        
        return False
    
    def _cleanup_sections(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean up and merge sections.
        
        Args:
            sections: Raw sections
            
        Returns:
            Cleaned sections
        """
        cleaned_sections = []
        
        for section in sections:
            # Skip very short sections
            if len(section['content'].strip()) < 50:
                continue
            
            # Clean content
            content = re.sub(r'\n+', '\n', section['content'])
            content = re.sub(r'\s+', ' ', content)
            section['content'] = content.strip()
            
            # Ensure section title is clean
            section['section_title'] = re.sub(r'\s+', ' ', section['section_title']).strip()
            
            cleaned_sections.append(section)
        
        return cleaned_sections
