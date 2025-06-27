# PubMed RAG System voor Eqology

Een volledig werkende RAG (Retrieval-Augmented Generation) applicatie voor het zoeken en bevragen van PubMed artikelen met behulp van Mistral LLM. Speciaal ontwikkeld voor Eqology resellers om makkelijk wetenschappelijke informatie op te zoeken.

## 🚀 Features

- **PubMed Scraping**: Automatisch ophalen van wetenschappelijke artikelen uit PubMed
- **Vector Embedding**: Geavanceerde tekst embedding met sentence-transformers
- **Vector Database**: Snelle semantische zoekopdrachten met ChromaDB
- **Mistral LLM**: Lokale uitvoering van Mistral-7B voor natuurlijke taalverwerking
- **REST API**: Volledige FastAPI backend met automatische documentatie
- **Web Interface**: Moderne, gebruiksvriendelijke frontend
- **Docker Support**: Eenvoudige deployment met Docker Compose

## 📋 Vereisten

- Docker en Docker Compose
- NVIDIA GPU (aanbevolen voor Mistral LLM)
- NCBI API Key (optioneel, voor hogere rate limits)
- Minimaal 16GB RAM (32GB aanbevolen)
- 50GB vrije schijfruimte

## 🛠️ Installatie

### 1. Clone de repository
```bash
git clone <repository-url>
cd rag_backend
```

### 2. Configureer environment variables
Maak een `.env` bestand aan in de root directory:
```bash
# NCBI API Key (optioneel)
NCBI_API_KEY=your_ncbi_api_key_here
```

### 3. Start de applicatie
```bash
docker-compose up --build
```

De applicatie is nu beschikbaar op:
- **Web Interface**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 📖 Gebruik

### Web Interface

1. **Zoek en Indexeer Artikelen**:
   - Voer een PubMed zoekopdracht in (bijv. "omega-3 fatty acids health benefits")
   - Stel het maximum aantal artikelen in
   - Klik op "Zoek en Indexeer"

2. **Stel Vragen**:
   - Voer een vraag in over de geïndexeerde artikelen
   - Stel het aantal relevante documenten in
   - Klik op "Vraag Beantwoorden"

3. **Systeem Beheer**:
   - Bekijk statistieken over de vector database
   - Wis de database indien nodig

### API Endpoints

#### Zoeken en Indexeren
```bash
POST /search
{
  "query": "omega-3 fatty acids health benefits",
  "max_results": 50
}
```

#### Vraag Stellen
```bash
POST /ask
{
  "question": "Wat zijn de gezondheidsvoordelen van omega-3 vetzuren?",
  "n_results": 5
}
```

#### Systeem Statistieken
```bash
GET /stats
```

#### Database Wissen
```bash
DELETE /clear
```

## 🔧 Configuratie

### Model Configuratie

De applicatie gebruikt standaard:
- **Embedder**: `all-MiniLM-L6-v2` (sentence-transformers)
- **LLM**: `mistralai/Mistral-7B-Instruct-v0.2`
- **Vector Database**: ChromaDB met persistente opslag

### Performance Optimalisatie

Voor betere performance:
1. **GPU Gebruik**: Zorg dat NVIDIA Docker runtime is geïnstalleerd
2. **Memory**: Verhoog Docker memory limits naar 32GB
3. **API Key**: Gebruik een NCBI API key voor hogere rate limits

## 📊 Voorbeeld Workflow

### 1. Artikelen Zoeken
```bash
curl -X POST "http://localhost:8001/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "vitamin D supplementation",
    "max_results": 25
  }'
```

### 2. Vraag Stellen
```bash
curl -X POST "http://localhost:8001/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Hoe effectief is vitamine D suppletie voor botgezondheid?",
    "n_results": 5
  }'
```

### 3. Statistieken Bekijken
```bash
curl "http://localhost:8001/stats"
```

## 🏗️ Architectuur

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PubMed API    │    │   Scraper       │    │   Parser        │
│                 │───▶│                 │───▶│                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mistral LLM   │◀───│   RAG System    │◀───│   Embedder      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │   Vector Store  │
                                              │   (ChromaDB)    │
                                              └─────────────────┘
```

## 🔍 Troubleshooting

### Veelvoorkomende Problemen

1. **Out of Memory Errors**:
   - Verhoog Docker memory limits
   - Gebruik een kleinere Mistral model variant
   - Verminder batch sizes

2. **Slow Response Times**:
   - Controleer GPU beschikbaarheid
   - Verlaag het aantal resultaten
   - Optimaliseer vector database queries

3. **PubMed API Errors**:
   - Controleer internetverbinding
   - Voeg een NCBI API key toe
   - Implementeer rate limiting

### Logs Bekijken
```bash
docker-compose logs -f rag-backend
```

## 📝 Licentie

Dit project is ontwikkeld voor Eqology resellers. Alle rechten voorbehouden.

## 🤝 Bijdragen

Voor vragen of problemen, neem contact op met het development team.

## 📞 Support

- **Email**: support@eqology.com
- **Documentation**: http://localhost:8001/docs (wanneer applicatie draait)

*** App structure ***

rag_backend/
├── backend
│   ├── app
│   │   ├── __init__.py
│   │   ├── scraper.py
│   │   └── test/
│   │       └── test_Entrez.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
└── README.md

