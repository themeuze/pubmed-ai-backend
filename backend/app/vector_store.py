import logging
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import os
import json

logger = logging.getLogger(__name__)

class PubMedVectorStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the vector store with ChromaDB.
        
        Args:
            persist_directory: Directory to persist the vector database
        """
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client and collection."""
        try:
            # Create persist directory if it doesn't exist
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="pubmed_articles",
                metadata={"description": "PubMed articles for Eqology RAG system"}
            )
            
            logger.info(f"Vector store initialized at {self.persist_directory}")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    def add_articles(self, embedded_articles: List[Dict[str, Any]]) -> bool:
        """
        Add embedded articles to the vector store.
        
        Args:
            embedded_articles: List of articles with embeddings and chunks
            
        Returns:
            True if successful, False otherwise
        """
        try:
            documents = []
            embeddings = []
            metadatas = []
            ids = []
            
            for article_data in embedded_articles:
                article = article_data['article']
                chunks = article_data['chunks']
                
                for chunk in chunks:
                    # Create unique ID for each chunk
                    chunk_id = f"{article['pmid']}_{chunk['chunk_id']}"
                    
                    documents.append(chunk['text'])
                    embeddings.append(chunk['embedding'])
                    metadatas.append({
                        'pmid': article['pmid'],
                        'title': article['title'],
                        'authors': json.dumps(article['authors']),
                        'chunk_id': chunk['chunk_id']
                    })
                    ids.append(chunk_id)
            
            # Add to collection in batches
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                end_idx = min(i + batch_size, len(documents))
                
                self.collection.add(
                    documents=documents[i:end_idx],
                    embeddings=embeddings[i:end_idx],
                    metadatas=metadatas[i:end_idx],
                    ids=ids[i:end_idx]
                )
            
            logger.info(f"Added {len(documents)} chunks to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding articles to vector store: {e}")
            return False
    
    def search_similar(self, query_embedding: List[float], n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents using query embedding.
        
        Args:
            query_embedding: Embedding of the search query
            n_results: Number of results to return
            
        Returns:
            List of similar documents with metadata
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            return {
                'total_chunks': count,
                'collection_name': self.collection.name
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
    
    def clear_collection(self) -> bool:
        """
        Clear all data from the collection.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_collection(name=self.collection.name)
            self.collection = self.client.create_collection(
                name="pubmed_articles",
                metadata={"description": "PubMed articles for Eqology RAG system"}
            )
            logger.info("Collection cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False
    
    def search_similar_in_article(self, query_embedding: List[float], article_id: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents within a specific article.
        
        Args:
            query_embedding: Embedding of the search query
            article_id: PubMed ID of the article to search within
            n_results: Number of results to return
            
        Returns:
            List of similar documents with metadata
        """
        try:
            # Search with filter for specific article
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where={"pmid": article_id},
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                })
            
            logger.info(f"Found {len(formatted_results)} chunks in article {article_id}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching within article {article_id}: {e}")
            return []
    
    def get_recent_articles(self) -> List[Dict[str, Any]]:
        """
        Get a list of recently indexed articles.
        
        Returns:
            List of article metadata
        """
        try:
            # Get all documents to extract unique articles
            results = self.collection.get(
                include=['metadatas']
            )
            
            # Extract unique PMIDs and their metadata
            articles = {}
            for metadata in results['metadatas']:
                pmid = metadata['pmid']
                if pmid not in articles:
                    articles[pmid] = {
                        'pmid': pmid,
                        'title': metadata['title'],
                        'authors': json.loads(metadata['authors']) if metadata['authors'] else []
                    }
            
            # Convert to list and return recent articles (last 50)
            article_list = list(articles.values())
            return article_list[-50:]  # Return last 50 articles
            
        except Exception as e:
            logger.error(f"Error getting recent articles: {e}")
            return []

    def get_pmids_for_query(self, query: str) -> List[str]:
        """
        Get PMIDs of articles that are already in the vectorstore.
        This is a simplified version that returns all PMIDs since we don't store query associations.
        
        Args:
            query: PubMed search query (not used in current implementation)
            
        Returns:
            List of PMIDs already in the vectorstore
        """
        try:
            # Get all documents to extract PMIDs
            results = self.collection.get(
                include=['metadatas']
            )
            
            # Extract unique PMIDs
            pmids = set()
            for metadata in results['metadatas']:
                pmids.add(metadata['pmid'])
            
            return list(pmids)
            
        except Exception as e:
            logger.error(f"Error getting PMIDs: {e}")
            return [] 