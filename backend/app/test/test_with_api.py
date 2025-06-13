from Bio import Entrez
import os
from dotenv import load_dotenv

# Load de environment variabelen
load_dotenv()

# Configure Entrez
Entrez.email = "dirksmaurits@gmail.com"  # <-- zet hier je eigen email neer
Entrez.api_key = os.getenv("75bb3e7e2ec6a7c5febfdadd1ff38a2fe70a")

# Testfunctie
def test_entrez_api():
    try:
        handle = Entrez.esearch(db="pubmed", term="cancer", retmax=5)
        record = Entrez.read(handle)
        handle.close()

        print(f"Aantal gevonden artikelen: {record['Count']}")
        print(f"De eerste ID's: {record['IdList']}")

    except Exception as e:
        print(f"Fout bij API call: {e}")

if __name__ == "__main__":
    test_entrez_api()
