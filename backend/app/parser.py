import logging
import random
import time  # Import the time module


logger = logging.getLogger(__name__)

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

def parse_pubmed_article(article):
    """Parset één PubMed XML artikel naar een Python dict."""
    try:
        pmid = article['MedlineCitation']['PMID']
        article_data = article['MedlineCitation']['Article']

        title = article_data.get('ArticleTitle', '')
        abstract_list = article_data.get('Abstract', {}).get('AbstractText', [""])
        abstract = " ".join(abstract_list)

        # Authors parsing
        authors_list = article_data.get('AuthorList', [])
        authors = []
        for author in authors_list:
            lastname = author.get('LastName', '')
            firstname = author.get('ForeName', '')
            full_name = f"{firstname} {lastname}".strip()
            if full_name:
                authors.append(full_name)

        # Journal
        jounral = article_data.get('Journal', {}).get('Title', '')

        # Publication Date
        pub_date = article_data.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {})
        year = pub_date.get('Year', '')
        month = pub_date.get('Month', '')
        day = pub_date.get('Day', '')
        
        # Format publication date
        publication_date = f"{year}-{month}-{day}".strip('-')

        return {
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "authors": authors
        }
    except Exception as e:
        logger.warning(f"Error parsing article: {e}")
        return None
