# PubMed RAG System Setup Guide

## 🚀 Snelle Start

### 1. Vereisten Controleren

Zorg dat je de volgende software hebt geïnstalleerd:
- Docker en Docker Compose
- Minimaal 16GB RAM (32GB aanbevolen)
- 50GB vrije schijfruimte
- NVIDIA GPU (optioneel, maar aanbevolen voor betere performance)

### 2. Systeem Starten

```bash
# Clone de repository (als je dat nog niet hebt gedaan)
git clone <repository-url>
cd rag_backend

# Start het systeem
./start.sh
```

Of handmatig:
```bash
# Build en start met Docker Compose
docker-compose up --build -d

# Wacht tot het systeem volledig is opgestart (ongeveer 2-3 minuten)
```

### 3. Toegang tot de Applicatie

- **Web Interface**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 📋 Gedetailleerde Setup

### Environment Variables

Maak een `.env` bestand aan in de root directory:

```bash
# NCBI API Key (optioneel - voor hogere rate limits)
# Krijg een gratis API key op: https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
NCBI_API_KEY=your_api_key_here

# Environment (development/production/testing)
ENVIRONMENT=development

# Docker memory limit (aanbevolen: 32GB voor Mistral LLM)
DOCKER_MEMORY_LIMIT=32g
```

### Docker Memory Instellingen

Voor optimale performance met Mistral LLM:

1. **Docker Desktop (Windows/Mac)**:
   - Open Docker Desktop
   - Ga naar Settings > Resources
   - Verhoog Memory naar 32GB
   - Verhoog CPUs naar minimaal 4

2. **Docker op Linux**:
   ```bash
   # Voeg toe aan /etc/docker/daemon.json
   {
     "default-shm-size": "2G",
     "memory": "32g"
   }
   ```

### GPU Support (NVIDIA)

Voor GPU acceleratie:

1. **Installeer NVIDIA Docker**:
   ```bash
   # Ubuntu/Debian
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update && sudo apt-get install -y nvidia-docker2
   sudo systemctl restart docker
   ```

2. **Test GPU**:
   ```bash
   docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
   ```

## 🔧 Configuratie

### Model Instellingen

De applicatie gebruikt standaard:
- **Embedder**: `all-MiniLM-L6-v2` (snel en efficiënt)
- **LLM**: `mistralai/Mistral-7B-Instruct-v0.2` (hoogwaardige antwoorden)
- **Vector Database**: ChromaDB (persistente opslag)

### Performance Optimalisatie

Voor betere performance:

1. **Gebruik een NCBI API key** voor hogere rate limits
2. **Verhoog Docker memory** naar 32GB
3. **Gebruik GPU** voor snellere LLM inferentie
4. **Pas batch sizes aan** in `backend/app/config.py`

## 📖 Gebruik

### Web Interface

1. **Artikelen Zoeken**:
   - Voer een PubMed zoekopdracht in
   - Stel het maximum aantal artikelen in
   - Klik op "Zoek en Indexeer"

2. **Vragen Stellen**:
   - Voer een vraag in over de geïndexeerde artikelen
   - Stel het aantal relevante documenten in
   - Klik op "Vraag Beantwoorden"

### API Gebruik

```bash
# Artikelen zoeken
curl -X POST "http://localhost:8001/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "vitamin D supplementation",
    "max_results": 25
  }'

# Vraag stellen
curl -X POST "http://localhost:8001/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Hoe effectief is vitamine D suppletie?",
    "n_results": 5
  }'

# Statistieken bekijken
curl "http://localhost:8001/stats"
```

## 🧪 Testen

### Demo Uitvoeren

```bash
# Voer de demo uit om het systeem te testen
python3 demo.py
```

### Systeem Testen

```bash
# Test alle API endpoints
python3 test_system.py
```

### Logs Bekijken

```bash
# Bekijk real-time logs
docker-compose logs -f rag-backend

# Bekijk specifieke logs
docker-compose logs rag-backend | grep ERROR
```

## 🔍 Troubleshooting

### Veelvoorkomende Problemen

1. **Out of Memory Errors**:
   ```bash
   # Verhoog Docker memory limits
   # Herstart Docker en probeer opnieuw
   docker-compose down
   docker-compose up --build -d
   ```

2. **Slow Startup**:
   - Eerste keer duurt langer (modellen worden gedownload)
   - Controleer internetverbinding
   - Gebruik een snellere internetverbinding

3. **PubMed API Errors**:
   - Controleer internetverbinding
   - Voeg een NCBI API key toe
   - Wacht en probeer opnieuw (rate limiting)

4. **GPU niet herkend**:
   ```bash
   # Test GPU
   nvidia-smi
   
   # Controleer Docker GPU support
   docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
   ```

### Debug Mode

Voor debugging, voeg toe aan `.env`:
```bash
ENVIRONMENT=development
DEBUG=true
```

### Log Levels

Pas log levels aan in `backend/app/config.py`:
```python
LOG_LEVEL = "DEBUG"  # Voor meer details
LOG_LEVEL = "INFO"   # Standaard
LOG_LEVEL = "WARNING"  # Alleen waarschuwingen
```

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8001/health
```

### Systeem Statistieken

```bash
curl http://localhost:8001/stats
```

### Performance Monitoring

```bash
# Docker stats
docker stats

# Container logs
docker-compose logs rag-backend
```

## 🛑 Stoppen en Opruimen

### Systeem Stoppen

```bash
# Stop de applicatie
docker-compose down

# Stop en verwijder volumes (database wordt gewist)
docker-compose down -v
```

### Data Behouden

De vector database wordt opgeslagen in `./backend/chroma_db/`. 
Deze map wordt automatisch gemount in de Docker container.

### Volledige Reset

```bash
# Stop alles
docker-compose down -v

# Verwijder alle data
rm -rf backend/chroma_db/*

# Herstart
docker-compose up --build -d
```

## 📞 Support

Voor problemen of vragen:
1. Bekijk de logs: `docker-compose logs rag-backend`
2. Controleer de health endpoint: http://localhost:8001/health
3. Test de demo: `python3 demo.py`
4. Neem contact op met het development team 