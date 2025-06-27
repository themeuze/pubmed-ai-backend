#!/bin/bash

# PubMed RAG System Startup Script
# Voor Eqology resellers

echo "🚀 Starting PubMed RAG System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# NCBI API Key (optioneel - voor hogere rate limits)
# Krijg een gratis API key op: https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
NCBI_API_KEY=

# Docker memory limit (aanbevolen: 32GB voor Mistral LLM)
# DOCKER_MEMORY_LIMIT=32g
EOF
    echo "✅ .env file created. You can add your NCBI API key if needed."
fi

# Check available memory
TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
if [ "$TOTAL_MEM" -lt 16 ]; then
    echo "⚠️  Warning: Less than 16GB RAM detected. Performance may be limited."
    echo "   Recommended: 32GB RAM for optimal performance with Mistral LLM"
fi

# Check for NVIDIA GPU
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU detected"
    GPU_AVAILABLE=true
else
    echo "⚠️  No NVIDIA GPU detected. Mistral LLM will run on CPU (slower)"
    GPU_AVAILABLE=false
fi

# Create necessary directories
mkdir -p backend/chroma_db
mkdir -p backend/app/static

# Build and start the application
echo "🔨 Building and starting the application..."
docker-compose up --build -d

# Wait for the application to start
echo "⏳ Waiting for application to start..."
sleep 30

# Check if the application is running
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ Application is running successfully!"
    echo ""
    echo "🌐 Access the application:"
    echo "   Web Interface: http://localhost:8001"
    echo "   API Documentation: http://localhost:8001/docs"
    echo "   Health Check: http://localhost:8001/health"
    echo ""
    echo "📖 Quick Start:"
    echo "   1. Open http://localhost:8001 in your browser"
    echo "   2. Search for articles (e.g., 'omega-3 fatty acids')"
    echo "   3. Ask questions about the indexed articles"
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs: docker-compose logs -f rag-backend"
    echo "   Stop app: docker-compose down"
    echo "   Restart app: docker-compose restart"
else
    echo "❌ Application failed to start. Check logs with:"
    echo "   docker-compose logs -f rag-backend"
    exit 1
fi 