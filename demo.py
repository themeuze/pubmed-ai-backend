#!/usr/bin/env python3
"""
Demo script voor PubMed RAG System
Toont hoe het systeem werkt met mock data
"""

import json
import time
from typing import List, Dict, Any

class MockPubMedRAGSystem:
    """Mock RAG system voor demo doeleinden"""
    
    def __init__(self):
        self.articles = []
        self.embedded_articles = []
        
    def search_and_index_articles(self, query: str, max_results: int = 100) -> Dict[str, Any]:
        """Mock search and index functionality"""
        print(f"🔍 Zoeken naar: {query}")
        print(f"📊 Maximum resultaten: {max_results}")
        
        # Simulate processing time
        time.sleep(2)
        
        # Mock articles
        mock_articles = [
            {
                "pmid": "12345678",
                "title": "Omega-3 Fatty Acids and Cardiovascular Health: A Comprehensive Review",
                "abstract": "This study examines the effects of omega-3 fatty acids on cardiovascular health. Results show significant improvements in heart function and reduced inflammation markers.",
                "authors": ["Smith, J.", "Johnson, A.", "Brown, M."]
            },
            {
                "pmid": "12345679", 
                "title": "The Role of Omega-3 in Brain Development and Cognitive Function",
                "abstract": "Research indicates that omega-3 fatty acids play a crucial role in brain development and cognitive function, particularly in children and elderly populations.",
                "authors": ["Davis, R.", "Wilson, K.", "Miller, P."]
            },
            {
                "pmid": "12345680",
                "title": "Omega-3 Supplementation and Inflammatory Response",
                "abstract": "Clinical trials demonstrate that omega-3 supplementation significantly reduces inflammatory markers and improves immune system function.",
                "authors": ["Garcia, L.", "Martinez, S.", "Rodriguez, T."]
            }
        ]
        
        # Simulate embedding process
        print("🧠 Artikelen worden geëmbed en geïndexeerd...")
        time.sleep(3)
        
        self.articles = mock_articles[:max_results]
        
        return {
            'success': True,
            'message': f'Successfully indexed {len(self.articles)} articles',
            'articles_processed': len(self.articles),
            'total_chunks': len(self.articles) * 2  # Mock chunks
        }
    
    def ask_question(self, question: str, n_results: int = 5) -> Dict[str, Any]:
        """Mock question answering functionality"""
        print(f"💬 Vraag: {question}")
        print(f"📚 Aantal relevante documenten: {n_results}")
        
        # Simulate processing time
        time.sleep(2)
        
        # Mock response based on question
        if "omega-3" in question.lower() or "omega" in question.lower():
            response = """Op basis van de wetenschappelijke artikelen kan ik de volgende gezondheidsvoordelen van omega-3 vetzuren identificeren:

1. **Cardiovasculaire gezondheid**: Omega-3 vetzuren verbeteren de hartfunctie en verminderen ontstekingsmarkers in het lichaam.

2. **Hersenfunctie**: Ze spelen een cruciale rol in de hersenontwikkeling en cognitieve functie, vooral bij kinderen en ouderen.

3. **Ontstekingsremmend**: Supplementatie met omega-3 vermindert significant ontstekingsmarkers en verbetert de immuunfunctie.

Deze bevindingen zijn gebaseerd op klinische studies en systematische reviews van wetenschappelijke literatuur."""
        else:
            response = "Ik heb geen specifieke informatie gevonden over dit onderwerp in de geïndexeerde artikelen. Probeer een vraag te stellen over omega-3 vetzuren of voeg meer relevante artikelen toe aan de database."
        
        return {
            'success': True,
            'response': response,
            'context_count': min(n_results, len(self.articles)),
            'context_sources': [
                {
                    'pmid': article['pmid'],
                    'title': article['title'],
                    'distance': 0.1 + i * 0.1
                }
                for i, article in enumerate(self.articles[:n_results])
            ]
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Mock system statistics"""
        return {
            'vector_store': {
                'total_chunks': len(self.articles) * 2,
                'collection_name': 'pubmed_articles'
            },
            'embedder_model': 'all-MiniLM-L6-v2',
            'chat_model': 'mistralai/Mistral-7B-Instruct-v0.2'
        }

def demo_workflow():
    """Demonstrate the complete RAG workflow"""
    print("🚀 PubMed RAG System Demo")
    print("=" * 50)
    
    # Initialize mock system
    rag_system = MockPubMedRAGSystem()
    
    # Step 1: Search and index articles
    print("\n📚 Stap 1: Zoeken en indexeren van artikelen")
    print("-" * 40)
    
    search_result = rag_system.search_and_index_articles(
        query="omega-3 fatty acids health benefits",
        max_results=3
    )
    
    if search_result['success']:
        print(f"✅ {search_result['message']}")
        print(f"📊 Artikelen verwerkt: {search_result['articles_processed']}")
        print(f"🧩 Totaal chunks: {search_result['total_chunks']}")
    else:
        print(f"❌ Fout: {search_result['message']}")
        return
    
    # Step 2: Ask questions
    print("\n💬 Stap 2: Vragen stellen")
    print("-" * 40)
    
    questions = [
        "Wat zijn de gezondheidsvoordelen van omega-3 vetzuren?",
        "Hoe effectief is omega-3 voor hartgezondheid?",
        "Wat is de rol van omega-3 in hersenontwikkeling?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n🤔 Vraag {i}: {question}")
        print("-" * 30)
        
        answer = rag_system.ask_question(question, n_results=3)
        
        if answer['success']:
            print("🤖 Antwoord:")
            print(answer['response'])
            print(f"\n📚 Bronnen gebruikt: {answer['context_count']}")
            for source in answer['context_sources']:
                print(f"   - {source['title']} (PMID: {source['pmid']})")
        else:
            print(f"❌ Fout: {answer['response']}")
    
    # Step 3: System statistics
    print("\n📊 Stap 3: Systeem statistieken")
    print("-" * 40)
    
    stats = rag_system.get_system_stats()
    print(f"🧩 Totaal chunks in database: {stats['vector_store']['total_chunks']}")
    print(f"🧠 Embedder model: {stats['embedder_model']}")
    print(f"💬 Chat model: {stats['chat_model']}")
    
    print("\n🎉 Demo voltooid!")
    print("\n💡 In de echte applicatie:")
    print("   - Artikelen worden opgehaald van PubMed API")
    print("   - Tekst wordt geëmbed met sentence-transformers")
    print("   - Vector database gebruikt ChromaDB")
    print("   - Antwoorden worden gegenereerd met Mistral LLM")
    print("   - Web interface beschikbaar op http://localhost:8000")

if __name__ == "__main__":
    demo_workflow() 