"""
Configuration settings voor PubMed RAG System
"""

import os
from typing import Dict, Any

class Config:
    """Main configuration class"""
    
    # PubMed API settings
    NCBI_EMAIL = "dirksmaurits@gmail.com"
    NCBI_API_KEY = "75bb3e7e2ec6a7c5febfdadd1ff38a2fe70a"
    NCBI_TIMEOUT = 30
    
    # Vector store settings
    VECTOR_STORE_PATH = "./chroma_db"
    COLLECTION_NAME = "pubmed_articles"
    
    # Embedding settings
    EMBEDDER_MODEL = "all-MiniLM-L6-v2"  # Lightweight and fast
    CHUNK_SIZE = 512
    CHUNK_OVERLAP = 50
    
    # LLM settings
    LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
    LLM_MAX_LENGTH = 1024
    LLM_TEMPERATURE = 0.7
    
    # Search settings
    DEFAULT_MAX_RESULTS = 100
    DEFAULT_N_RESULTS = 5
    BATCH_SIZE = 500
    
    # Performance settings
    USE_GPU = True
    QUANTIZATION = True  # Use 8-bit quantization for memory efficiency
    
    @classmethod
    def get_embedder_config(cls) -> Dict[str, Any]:
        """Get embedder configuration"""
        return {
            "model_name": cls.EMBEDDER_MODEL,
            "chunk_size": cls.CHUNK_SIZE,
            "chunk_overlap": cls.CHUNK_OVERLAP
        }
    
    @classmethod
    def get_llm_config(cls) -> Dict[str, Any]:
        """Get LLM configuration"""
        return {
            "model_name": cls.LLM_MODEL,
            "max_length": cls.LLM_MAX_LENGTH,
            "temperature": cls.LLM_TEMPERATURE,
            "use_gpu": cls.USE_GPU,
            "quantization": cls.QUANTIZATION
        }
    
    @classmethod
    def get_vector_store_config(cls) -> Dict[str, Any]:
        """Get vector store configuration"""
        return {
            "persist_directory": cls.VECTOR_STORE_PATH,
            "collection_name": cls.COLLECTION_NAME
        }
    
    @classmethod
    def get_search_config(cls) -> Dict[str, Any]:
        """Get search configuration"""
        return {
            "default_max_results": cls.DEFAULT_MAX_RESULTS,
            "default_n_results": cls.DEFAULT_N_RESULTS,
            "batch_size": cls.BATCH_SIZE
        }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    
    # Use smaller models for development
    EMBEDDER_MODEL = "all-MiniLM-L6-v2"
    LLM_BACKEND = "ollama"  # 'transformers' of 'ollama'
    LLM_MODEL = "mistral"  # Modelnaam voor Ollama
    OLLAMA_BASE_URL = "http://localhost:11434"  # Use localhost with host network

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = "INFO"
    
    # Use full models for production
    EMBEDDER_MODEL = "all-mpnet-base-v2"  # Better quality embeddings
    LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
    
    # Optimize for performance
    USE_GPU = True
    QUANTIZATION = True

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    
    # Use minimal models for testing
    EMBEDDER_MODEL = "all-MiniLM-L6-v2"
    LLM_MODEL = "microsoft/DialoGPT-small"
    
    # Disable GPU for testing
    USE_GPU = False
    QUANTIZATION = False

# Environment-based configuration
def get_config():
    """Get configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig
    elif env == "testing":
        return TestingConfig
    else:
        return DevelopmentConfig

# Export current configuration
current_config = get_config() 