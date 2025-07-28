#!/usr/bin/env python3
"""
Persona-Driven Document Intelligence System
Adobe Hackathon 2025 - Challenge 1B
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.embeddings import EmbeddingEngine
from utils.pdf_processor import PDFProcessor
from utils.persona_analyzer import PersonaAnalyzer
from utils.ranking_engine import RankingEngine
from utils.json_formatter import JSONFormatter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PersonaDocumentIntelligence:
    """Main system class for persona-driven document intelligence."""
    
    def __init__(self):
        """Initialize the system components."""
        logger.info("Initializing Persona-Driven Document Intelligence System...")
        
        # Initialize components
        self.pdf_processor = PDFProcessor()
        self.embedding_engine = EmbeddingEngine()
        self.persona_analyzer = PersonaAnalyzer(self.embedding_engine)
        self.ranking_engine = RankingEngine(self.embedding_engine)
        self.json_formatter = JSONFormatter()
        
        logger.info("System initialization complete!")
    
    def process_documents(self, input_dir: str, output_dir: str):
        """
        Process documents with persona-driven intelligence.
        
        Args:
            input_dir: Directory containing PDFs and config.json
            output_dir: Directory to save results
        """
        start_time = time.time()
        
        try:
            # Load configuration
            config_path = os.path.join(input_dir, 'config.json')
            if not os.path.exists(config_path):
                raise FileNotFoundError("config.json not found in input directory")
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            persona = config.get('persona', '')
            job_to_be_done = config.get('job_to_be_done', '')
            
            if not persona or not job_to_be_done:
                raise ValueError("Both 'persona' and 'job_to_be_done' must be specified in config.json")
            
            logger.info(f"Processing for persona: {persona}")
            logger.info(f"Job to be done: {job_to_be_done}")
            
            # Find PDF files
            pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
            if not pdf_files:
                raise FileNotFoundError("No PDF files found in input directory")
            
            logger.info(f"Found {len(pdf_files)} PDF files to process")
            
            # Process PDFs
            documents = []
            for pdf_file in pdf_files:
                pdf_path = os.path.join(input_dir, pdf_file)
                logger.info(f"Processing {pdf_file}...")
                
                sections = self.pdf_processor.extract_sections(pdf_path)
                documents.append({
                    'filename': pdf_file,
                    'path': pdf_path,
                    'sections': sections,
                    'total_pages': len(set(s['page_number'] for s in sections))
                })
            
            # Analyze with persona context
            logger.info("Analyzing documents with persona context...")
            analysis_results = self.persona_analyzer.analyze_documents(
                documents, persona, job_to_be_done
            )
            
            # Rank sections and subsections
            logger.info("Ranking sections and subsections...")
            ranked_sections = self.ranking_engine.rank_sections(
                analysis_results['sections'], persona, job_to_be_done
            )
            
            ranked_subsections = self.ranking_engine.rank_subsections(
                analysis_results['subsections'], persona, job_to_be_done
            )
            
            # Format output
            processing_time = time.time() - start_time
            output_data = self.json_formatter.format_output(
                documents=documents,
                persona=persona,
                job_to_be_done=job_to_be_done,
                sections=ranked_sections,
                subsections=ranked_subsections,
                processing_time=processing_time
            )
            
            # Save results
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, 'analysis_result.json')
            
            with open(output_path, 'w') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Analysis complete! Results saved to {output_path}")
            logger.info(f"Processing time: {processing_time:.2f} seconds")
            
            # Print summary
            print(f"\nProcessing Complete!")
            print(f"Documents processed: {len(documents)}")
            print(f"Sections extracted: {len(ranked_sections)}")
            print(f"Subsections analyzed: {len(ranked_subsections)}")
            print(f"Processing time: {processing_time:.2f}s")
            print(f"Results saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error during processing: {str(e)}")
            raise

def main():
    """Main entry point."""
    input_dir = os.getenv('INPUT_DIR', './input')
    output_dir = os.getenv('OUTPUT_DIR', './output')
    
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' not found!")
        sys.exit(1)
    
    try:
        # Initialize and run system
        system = PersonaDocumentIntelligence()
        system.process_documents(input_dir, output_dir)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
