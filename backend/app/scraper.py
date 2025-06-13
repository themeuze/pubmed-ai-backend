from Bio import Entrez
import logging
from parser import parse_pubmed_article
import time
import random  # extra import voor jitter
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Entrez
Entrez.email = "dirksmaurits@gmail.com"
Entrez.api_key = os.getenv("NCBI_API_KEY", "")  # Zorg dat je een NCBI API key hebt ingesteld in je .env bestand
Entrez.timeout = 30  # Timeout in seconds for requests

if Entrez.api_key:
    logger.info("NCBI API key loaded and active.")
else:
    logger.info("No NCBI API key set, using default limits.")


# Retry helper
def retry_request(func, max_retries=3, backoff_factor=1.0):
    """
    Algemene retry-wrapper voor netwerk calls.
    """
    for attempt in range(1, max_retries + 1):
        try:
            return func()
        except Exception as e:
            wait_time = backoff_factor * (2 ** (attempt - 1)) + random.uniform(0, 0.1)
            logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {wait_time:.2f} seconds...")
            time.sleep(wait_time)
    logger.error(f"All {max_retries} attempts failed.")
    return None

def search_pubmed(query, max_results=1000, use_history=True):
    logger.info(f"Searching PubMed for query: '{query}'")

    handle = Entrez.esearch(
        db="pubmed",
        term=query,
        retmax=max_results,
        usehistory="y" if use_history else "n"
    )
    record = Entrez.read(handle)
    handle.close()

    id_list = record["IdList"]
    total_count = int(record["Count"])
    logger.info(f"Found {total_count} articles, returning {len(id_list)} IDs.")

    if use_history:
        webenv = record["WebEnv"]
        query_key = record["QueryKey"]
        return id_list, webenv, query_key, total_count

    return id_list, None, None, total_count

def fetch_in_batches(webenv, query_key, total_count, batch_size=500):
    logger.info("Fetching articles in batches...")

    sleep_time = 0.34
    articles = []

    for start in range(0, int(total_count), batch_size):
        logger.info(f"Fetching records {start} to {start + batch_size}...")

        def fetch_batch():
            handle = Entrez.efetch(
                db="pubmed",
                query_key=query_key,
                WebEnv=webenv,
                retstart=start,
                retmax=min(batch_size, total_count - start),
                retmode="xml"
            )
            records = Entrez.read(handle)
            handle.close()
            return records

        records = retry_request(fetch_batch)
        if records is None:
            logger.error(f"Skipping batch starting at {start} due to repeated failures.")
            continue

        for article in records['PubmedArticle']:
            parsed_article = parse_pubmed_article(article)
            if parsed_article:
                articles.append(parsed_article)

        time.sleep(sleep_time)

    return articles
