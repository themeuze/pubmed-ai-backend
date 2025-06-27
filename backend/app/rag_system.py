import logging
from typing import List, Dict, Any, Optional
from .scraper import search_pubmed, fetch_in_batches, fetch_articles_by_pmids
from .embedder import PubMedEmbedder
from .vector_store import PubMedVectorStore
from .chat import get_chat_backend

logger = logging.getLogger(__name__)

class PubMedRAGSystem:
    def __init__(self, vector_store_path: str = "./chroma_db"):
        """
        Initialize the complete RAG system.
        
        Args:
            vector_store_path: Path for the vector database
        """
        self.embedder = None
        self.vector_store = None
        self.chat = None
        self.vector_store_path = vector_store_path
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all RAG components."""
        try:
            logger.info("Initializing RAG system components...")
            
            # Initialize embedder
            self.embedder = PubMedEmbedder()
            
            # Initialize vector store
            self.vector_store = PubMedVectorStore(self.vector_store_path)
            
            # Initialize chat (Ollama of transformers)
            self.chat = get_chat_backend()
            
            logger.info("All RAG components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing RAG components: {e}")
            raise
    
    def search_and_index_articles(self, query: str, max_results: int = 100) -> Dict[str, Any]:
        """
        Search PubMed and index articles in the vector store.
        
        Args:
            query: PubMed search query
            max_results: Maximum number of articles to fetch
            
        Returns:
            Dictionary with indexing results
        """
        try:
            logger.info(f"Searching PubMed for: {query}")
            
            # Search PubMed
            id_list, webenv, query_key, total_count = search_pubmed(query, max_results)
            
            if not id_list:
                return {
                    'success': False,
                    'message': 'No articles found for the query',
                    'articles_processed': 0
                }
            
            # Fetch articles in batches
            articles = fetch_in_batches(webenv, query_key, total_count, max_results)
            
            if not articles:
                return {
                    'success': False,
                    'message': 'Failed to fetch articles',
                    'articles_processed': 0
                }
            
            logger.info(f"Fetched {len(articles)} articles, creating embeddings...")
            
            # Create embeddings
            embedded_articles = self.embedder.embed_articles(articles)
            
            # Add to vector store
            success = self.vector_store.add_articles(embedded_articles)
            
            if success:
                return {
                    'success': True,
                    'message': f'Successfully indexed {len(articles)} articles',
                    'articles_processed': len(articles),
                    'total_chunks': sum(len(article_data['chunks']) for article_data in embedded_articles)
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to add articles to vector store',
                    'articles_processed': 0
                }
                
        except Exception as e:
            logger.error(f"Error in search_and_index_articles: {e}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'articles_processed': 0
            }
    
    def ask_question(self, question: str, n_results: int = 5, article_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Ask a question and get an answer using the RAG system.
        
        Args:
            question: User's question
            n_results: Number of similar documents to retrieve
            article_id: Optional specific article ID to focus on
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            logger.info(f"Processing question: {question}")
            
            # Create query embedding
            query_embedding = self.embedder.embed_query(question)
            
            # Search for similar documents
            if article_id:
                # Search only within the specific article
                similar_docs = self.vector_store.search_similar_in_article(query_embedding, article_id, n_results)
                logger.info(f"Searching within specific article: {article_id}")
            else:
                # Search across all articles
                similar_docs = self.vector_store.search_similar(query_embedding, n_results)
                logger.info(f"Searching across all articles")
            
            if not similar_docs:
                if article_id:
                    return {
                        'success': False,
                        'response': f'Geen relevante informatie gevonden in het geselecteerde artikel om je vraag te beantwoorden.',
                        'context_count': 0,
                        'context_sources': []
                    }
                else:
                    return {
                        'success': False,
                        'response': 'Geen relevante artikelen gevonden om je vraag te beantwoorden.',
                        'context_count': 0,
                        'context_sources': []
                    }
            
            # Generate response using Mistral
            chat_response = self.chat.chat(question, similar_docs)
            
            return {
                'success': True,
                'response': chat_response['response'],
                'context_count': chat_response['context_count'],
                'context_sources': chat_response['context_sources'],
                'article_focused': article_id is not None
            }
            
        except Exception as e:
            logger.error(f"Error in ask_question: {e}")
            return {
                'success': False,
                'response': f'Er is een fout opgetreden: {str(e)}',
                'context_count': 0,
                'context_sources': []
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG system.
        
        Returns:
            Dictionary with system statistics
        """
        try:
            vector_stats = self.vector_store.get_collection_stats()
            
            return {
                'vector_store': vector_stats,
                'embedder_model': self.embedder.model_name if self.embedder else None,
                'chat_model': self.chat.model_name if self.chat else None
            }
            
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {}
    
    def clear_database(self) -> bool:
        """
        Clear all data from the vector store.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.vector_store.clear_collection()
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            return False
    
    def get_recent_articles(self) -> List[Dict[str, Any]]:
        """
        Get a list of recently indexed articles.
        
        Returns:
            List of article dictionaries
        """
        try:
            return self.vector_store.get_recent_articles()
        except Exception as e:
            logger.error(f"Error getting recent articles: {e}")
            return []

    def check_coverage(self, query: str) -> Dict[str, Any]:
        """
        Check coverage of a search term: total PubMed articles vs articles in vectorstore.
        
        Args:
            query: PubMed search query
            
        Returns:
            Dictionary with coverage statistics
        """
        try:
            logger.info(f"Checking coverage for: {query}")
            
            # Get total count from PubMed
            id_list, webenv, query_key, total_count = search_pubmed(query, 1)  # Just get count
            
            if total_count == 0:
                return {
                    'success': False,
                    'total_pubmed': 0,
                    'in_vector': 0,
                    'missing': 0,
                    'message': 'No articles found for this query'
                }
            
            # Get PMIDs already in vectorstore for this query
            existing_pmids = self.vector_store.get_pmids_for_query(query)
            
            missing_count = total_count - len(existing_pmids)
            
            return {
                'success': True,
                'total_pubmed': total_count,
                'in_vector': len(existing_pmids),
                'missing': missing_count,
                'message': f'Coverage check completed for "{query}"'
            }
            
        except Exception as e:
            logger.error(f"Error in check_coverage: {e}")
            return {
                'success': False,
                'total_pubmed': 0,
                'in_vector': 0,
                'missing': 0,
                'message': f'Error checking coverage: {str(e)}'
            }

    def index_missing_articles(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """
        Index missing articles for a search term up to the specified limit.
        
        Args:
            query: PubMed search query
            limit: Maximum number of articles to index
            
        Returns:
            Dictionary with indexing results
        """
        try:
            logger.info(f"Indexing missing articles for: {query} (limit: {limit})")
            
            # Get existing PMIDs to avoid duplicates
            existing_pmids = set(self.vector_store.get_pmids_for_query(query))
            
            # Search PubMed for all articles
            id_list, webenv, query_key, total_count = search_pubmed(query, 1000)  # Get up to 1000 articles
            
            if not id_list:
                return {
                    'success': False,
                    'message': 'No articles found for this query',
                    'articles_processed': 0
                }
            
            # Filter out already indexed PMIDs
            missing_pmids = [pmid for pmid in id_list if pmid not in existing_pmids]
            
            if not missing_pmids:
                return {
                    'success': True,
                    'message': 'All articles for this query are already indexed',
                    'articles_processed': 0
                }
            
            # Limit the number of articles to process
            missing_pmids = missing_pmids[:limit]
            
            # Fetch the missing articles
            articles = fetch_articles_by_pmids(missing_pmids)
            
            if not articles:
                return {
                    'success': False,
                    'message': 'Failed to fetch missing articles',
                    'articles_processed': 0
                }
            
            logger.info(f"Fetched {len(articles)} missing articles, creating embeddings...")
            
            # Create embeddings
            embedded_articles = self.embedder.embed_articles(articles)
            
            # Add to vector store
            success = self.vector_store.add_articles(embedded_articles)
            
            if success:
                return {
                    'success': True,
                    'message': f'Successfully indexed {len(articles)} missing articles',
                    'articles_processed': len(articles),
                    'total_chunks': sum(len(article_data['chunks']) for article_data in embedded_articles)
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to add articles to vector store',
                    'articles_processed': 0
                }
                
        except Exception as e:
            logger.error(f"Error in index_missing_articles: {e}")
            return {
                'success': False,
                'message': f'Error indexing missing articles: {str(e)}',
                'articles_processed': 0
            } 