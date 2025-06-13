# backend/app/test/test_Entrez.py

import sys
import os
from dotenv import load_dotenv

# Zorg dat je bij de backend/app modules kan komen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

# Hier wordt je API key geladen voor Entrez (in scraper.py heb je dit waarschijnlijk al)
# Dus je hoeft dat hier niet nogmaals te doen

from scraper import search_pubmed, fetch_in_batches

# Test parameters
query = "Omega3 fatty acids and depression"
max_results = 1000  # maximaal aantal PubMed artikelen ophalen
batch_size = 500

# Start de search
ids, webenv, query_key, total_count = search_pubmed(query, max_results=max_results)

# Batch ophalen
articles = fetch_in_batches(webenv, query_key, total_count, batch_size=batch_size)

# Resultaat tonen
print(f"Totaal opgehaald: {len(articles)} artikelen\n")

# Print eerste paar resultaten als controle
for article in articles[:5]:  # alleen eerste 5 laten zien
    print(article)
    print("-" * 80)
