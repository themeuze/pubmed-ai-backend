from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import os
from dotenv import load_dotenv

# Import our RAG system
from .rag_system import PubMedRAGSystem

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PubMed RAG System for Eqology",
    description="Een RAG systeem voor het zoeken en bevragen van PubMed artikelen met Mistral LLM",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize RAG system
rag_system = None

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system on startup."""
    global rag_system
    try:
        logger.info("Starting PubMed RAG System...")
        rag_system = PubMedRAGSystem()
        logger.info("RAG System initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG System: {e}")
        raise

# Pydantic models for request/response
class SearchRequest(BaseModel):
    query: str
    max_results: int = 100

class QuestionRequest(BaseModel):
    question: str
    n_results: int = 5
    article_id: Optional[str] = None  # Optional specific article ID

class SearchResponse(BaseModel):
    success: bool
    message: str
    articles_processed: int
    total_chunks: Optional[int] = None

class QuestionResponse(BaseModel):
    success: bool
    response: str
    context_count: int
    context_sources: List[Dict[str, Any]]
    article_focused: bool = False

class SystemStatsResponse(BaseModel):
    vector_store: Dict[str, Any]
    embedder_model: Optional[str]
    chat_model: Optional[str]

class ArticleResponse(BaseModel):
    pmid: str
    title: str
    authors: List[str]

class CoverageRequest(BaseModel):
    query: str

class CoverageResponse(BaseModel):
    success: bool
    total_pubmed: int
    in_vector: int
    missing: int
    message: str

class IndexMissingRequest(BaseModel):
    query: str
    limit: int = 20

class IndexMissingResponse(BaseModel):
    success: bool
    message: str
    articles_processed: int
    total_chunks: Optional[int] = None

# API Endpoints
@app.get("/")
async def root():
    """Serve the web interface."""
    return FileResponse("app/static/index.html")

@app.get("/gui")
async def gui():
    """Alternative endpoint for the web interface."""
    return FileResponse("app/static/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG System not initialized")
    
    return {
        "status": "healthy",
        "rag_system_initialized": rag_system is not None
    }

@app.post("/search", response_model=SearchResponse)
async def search_articles(request: SearchRequest):
    """
    Search PubMed and index articles in the vector store.
    """
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG System not initialized")
    
    try:
        result = rag_system.search_and_index_articles(request.query, request.max_results)
        return SearchResponse(**result)
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question and get an answer using the RAG system.
    Can focus on a specific article if article_id is provided.
    """
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG System not initialized")
    
    try:
        result = rag_system.ask_question(request.question, request.n_results, request.article_id)
        return QuestionResponse(**result)
    except Exception as e:
        logger.error(f"Error in ask endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats():
    """
    Get system statistics.
    """
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG System not initialized")
    
    try:
        stats = rag_system.get_system_stats()
        return SystemStatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error in stats endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear")
async def clear_database():
    """
    Clear all data from the vector store.
    """
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG System not initialized")
    
    try:
        success = rag_system.clear_database()
        if success:
            return {"message": "Database cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear database")
    except Exception as e:
        logger.error(f"Error in clear endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Example usage endpoints
@app.get("/examples")
async def get_examples():
    """Get example queries and questions."""
    return {
        "search_examples": [
            "omega-3 fatty acids health benefits",
            "vitamin D supplementation",
            "probiotics gut health",
            "antioxidants aging",
            "collagen skin health"
        ],
        "question_examples": [
            "Wat zijn de gezondheidsvoordelen van omega-3 vetzuren?",
            "Hoe effectief is vitamine D suppletie?",
            "Welke probiotica zijn het beste voor darmgezondheid?",
            "Wat is de rol van antioxidanten bij veroudering?",
            "Hoe werkt collageen voor huidgezondheid?"
        ]
    }

@app.get("/articles", response_model=List[ArticleResponse])
async def get_recent_articles():
    """
    Get a list of recently indexed articles.
    """
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG System not initialized")
    
    try:
        articles = rag_system.get_recent_articles()
        return articles
    except Exception as e:
        logger.error(f"Error in articles endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/coverage", response_model=CoverageResponse)
async def check_coverage(request: CoverageRequest):
    """
    Check coverage of a search term: total PubMed articles vs articles in vectorstore.
    """
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG System not initialized")
    
    try:
        result = rag_system.check_coverage(request.query)
        return CoverageResponse(**result)
    except Exception as e:
        logger.error(f"Error in coverage endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/index_missing", response_model=IndexMissingResponse)
async def index_missing_articles(request: IndexMissingRequest):
    """
    Index missing articles for a search term up to the specified limit.
    """
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG System not initialized")
    
    try:
        result = rag_system.index_missing_articles(request.query, request.limit)
        return IndexMissingResponse(**result)
    except Exception as e:
        logger.error(f"Error in index_missing endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 