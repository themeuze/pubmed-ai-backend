from Bio import Entrez
import logging
from .parser import parse_pubmed_article
from .config import current_config
import time
import random  # extra import voor jitter
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Entrez
Entrez.email = current_config.NCBI_EMAIL
Entrez.api_key = current_config.NCBI_API_KEY
Entrez.timeout = current_config.NCBI_TIMEOUT

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
    
    try:
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
        
    except Exception as e:
        logger.error(f"Error in search_pubmed: {str(e)}")
        logger.error(f"Query: '{query}', max_results: {max_results}, use_history: {use_history}")
        logger.error(f"Entrez email: {Entrez.email}, API key set: {bool(Entrez.api_key)}")
        raise

def fetch_in_batches(webenv, query_key, total_count, max_results=None, batch_size=500):
    logger.info("Fetching articles in batches...")
    
    # Limit the total count to max_results if specified
    if max_results and max_results < total_count:
        total_count = max_results
        logger.info(f"Limiting fetch to {max_results} articles")

    sleep_time = 0.34
    articles = []

    for start in range(0, int(total_count), batch_size):
        current_batch_size = min(batch_size, total_count - start)
        logger.info(f"Fetching records {start} to {start + current_batch_size}...")

        def fetch_batch():
            handle = Entrez.efetch(
                db="pubmed",
                query_key=query_key,
                WebEnv=webenv,
                retstart=start,
                retmax=current_batch_size,
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
                
                # Stop if we've reached max_results
                if max_results and len(articles) >= max_results:
                    logger.info(f"Reached max_results limit ({max_results}), stopping fetch")
                    return articles

        time.sleep(sleep_time)

    return articles

def fetch_articles_by_pmids(pmids, batch_size=50):
    """
    Fetch specific articles by their PMIDs.
    
    Args:
        pmids: List of PMIDs to fetch
        batch_size: Number of PMIDs to fetch per batch
        
    Returns:
        List of parsed articles
    """
    logger.info(f"Fetching {len(pmids)} articles by PMIDs...")
    
    articles = []
    sleep_time = 0.34
    
    for i in range(0, len(pmids), batch_size):
        batch_pmids = pmids[i:i + batch_size]
        logger.info(f"Fetching batch {i//batch_size + 1}: PMIDs {batch_pmids[0]} to {batch_pmids[-1]}...")
        
        def fetch_batch():
            handle = Entrez.efetch(
                db="pubmed",
                id=",".join(batch_pmids),
                retmode="xml"
            )
            records = Entrez.read(handle)
            handle.close()
            return records
        
        records = retry_request(fetch_batch)
        if records is None:
            logger.error(f"Skipping batch starting at {i} due to repeated failures.")
            continue
        
        for article in records['PubmedArticle']:
            parsed_article = parse_pubmed_article(article)
            if parsed_article:
                articles.append(parsed_article)
        
        time.sleep(sleep_time)
    
    logger.info(f"Successfully fetched {len(articles)} articles")
    return articles
