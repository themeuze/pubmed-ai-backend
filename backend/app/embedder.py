import logging
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any
import os
from .config import current_config

logger = logging.getLogger(__name__)

class PubMedEmbedder:
    def __init__(self, model_name: str = None):
        """
        Initialize the embedder with a sentence transformer model.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        config = current_config.get_embedder_config()
        self.model_name = model_name or config["model_name"]
        self.chunk_size = config["chunk_size"]
        self.chunk_overlap = config["chunk_overlap"]
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def create_document_chunks(self, article: Dict[str, Any], chunk_size: int = None, overlap: int = None) -> List[Dict[str, Any]]:
        """
        Split an article into smaller chunks for better embedding.
        
        Args:
            article: PubMed article dictionary
            chunk_size: Maximum number of characters per chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of document chunks with metadata
        """
        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.chunk_overlap
        
        chunks = []
        
        # Combine title and abstract
        full_text = f"Title: {article.get('title', '')}\n\nAbstract: {article.get('abstract', '')}"
        
        if len(full_text) <= chunk_size:
            chunks.append({
                'text': full_text,
                'pmid': article.get('pmid'),
                'title': article.get('title'),
                'authors': article.get('authors', []),
                'chunk_id': 0
            })
        else:
            # Split into overlapping chunks
            start = 0
            chunk_id = 0
            
            while start < len(full_text):
                end = start + chunk_size
                chunk_text = full_text[start:end]
                
                chunks.append({
                    'text': chunk_text,
                    'pmid': article.get('pmid'),
                    'title': article.get('title'),
                    'authors': article.get('authors', []),
                    'chunk_id': chunk_id
                })
                
                start = end - overlap
                chunk_id += 1
                
                if start >= len(full_text):
                    break
        
        return chunks
    
    def embed_text(self, text: str) -> List[float]:
        """
        Create embeddings for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of float values representing the embedding
        """
        if self.model is None:
            raise ValueError("Model not loaded")
        
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            raise
    
    def embed_articles(self, articles: List[Dict[str, Any]], chunk_size: int = None) -> List[Dict[str, Any]]:
        """
        Create embeddings for a list of articles.
        
        Args:
            articles: List of PubMed articles
            chunk_size: Maximum chunk size for text splitting
            
        Returns:
            List of articles with embeddings and chunks
        """
        chunk_size = chunk_size or self.chunk_size
        embedded_articles = []
        
        for article in articles:
            try:
                # Create chunks
                chunks = self.create_document_chunks(article, chunk_size)
                
                # Create embeddings for each chunk
                for chunk in chunks:
                    embedding = self.embed_text(chunk['text'])
                    chunk['embedding'] = embedding
                
                embedded_articles.append({
                    'article': article,
                    'chunks': chunks
                })
                
            except Exception as e:
                logger.error(f"Error processing article {article.get('pmid', 'unknown')}: {e}")
                continue
        
        return embedded_articles
    
    def embed_query(self, query: str) -> List[float]:
        """
        Create embedding for a search query.
        
        Args:
            query: Search query text
            
        Returns:
            List of float values representing the query embedding
        """
        return self.embed_text(query) 