"""
Reactome API utility for fetching pathway and biological process data.
"""

import requests
from typing import List, Dict

class ReactomeAPI:
    """Reactome API client for pathway data."""
    def __init__(self):
        self.base_url = "https://reactome.org/ContentService/data"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BioSheetAgent/1.0 (https://github.com/your-repo)'
        })

    def get_pathways_for_uniprot(self, uniprot_id: str) -> List[Dict]:
        """
        Get Reactome pathways for a given UniProt accession.
        Args:
            uniprot_id: UniProt accession (e.g., 'P01308')
        Returns:
            List of pathway dicts
        """
        url = f"{self.base_url}/participants/{uniprot_id}/pathways"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[Reactome] Error fetching pathways for {uniprot_id}: {e}")
            return []

    def search_pathways(self, query: str, species: str = "Homo sapiens") -> List[Dict]:
        """
        Search Reactome for pathways by keyword.
        Args:
            query: Search term (e.g., 'insulin')
            species: Species name (default: 'Homo sapiens')
        Returns:
            List of pathway dicts
        """
        url = f"{self.base_url}/events/search/{query}"
        params = {"species": species}
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[Reactome] Error searching pathways for '{query}': {e}")
            return []

# Example usage
if __name__ == "__main__":
    api = ReactomeAPI()
    print("Testing Reactome pathway search for 'insulin':")
    pathways = api.search_pathways("insulin")
    for p in pathways[:3]:
        print(f"- {p.get('displayName')} (ID: {p.get('stId')})")
    print("\nTesting Reactome pathways for UniProt P01308 (insulin):")
    up_pathways = api.get_pathways_for_uniprot("P01308")
    for p in up_pathways[:3]:
        print(f"- {p.get('displayName')} (ID: {p.get('stId')})") 