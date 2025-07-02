"""
UniProt API utility for fetching protein information.
"""

import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
import time


class UniProtAPI:
    """UniProt API client for fetching protein data."""
    
    def __init__(self):
        self.base_url = "https://rest.uniprot.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BioSheetAgent/1.0 (https://github.com/your-repo)'
        })
    
    def get_protein_info(self, uniprot_id: str) -> Dict:
        """
        Fetch protein information from UniProt.
        
        Args:
            uniprot_id: UniProt accession number (e.g., 'P01308')
            
        Returns:
            Dictionary containing protein information
        """
        url = f"{self.base_url}/uniprotkb/{uniprot_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_protein_data(data)
            
        except requests.RequestException as e:
            print(f"Error fetching protein {uniprot_id}: {e}")
            return {}
    
    def search_proteins(self, query: str, limit: int = 100) -> List[Dict]:
        """
        Search for proteins using UniProt query.
        
        Args:
            query: Search query (e.g., 'insulin AND organism_id:9606')
            limit: Maximum number of results
            
        Returns:
            List of protein information dictionaries
        """
        url = f"{self.base_url}/uniprotkb/search"
        params = {
            'query': query,
            'fields': 'accession,id,protein_name,gene_names,organism_name,function,subcellular_location,pathway,disease',
            'size': limit
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            proteins = []
            for result in data.get('results', []):
                protein_info = self._parse_protein_data(result)
                proteins.append(protein_info)
            
            return proteins
            
        except requests.RequestException as e:
            print(f"Error searching proteins: {e}")
            return []
    
    def _parse_protein_data(self, data: Dict) -> Dict:
        """Parse UniProt protein data into standardized format."""
        protein_info = {
            'uniprot_id': data.get('primaryAccession', ''),
            'entry_name': data.get('uniProtkbId', ''),
            'protein_name': '',
            'gene_names': [],
            'organism': data.get('organism', {}).get('scientificName', ''),
            'function': '',
            'location': [],
            'pathways': [],
            'diseases': [],
            'synonyms': []
        }
        
        # Extract protein name
        if 'proteinDescription' in data:
            protein_info['protein_name'] = data['proteinDescription'].get('recommendedName', {}).get('fullName', {}).get('value', '')
        
        # Extract gene names
        if 'genes' in data:
            for gene in data['genes']:
                if 'geneName' in gene:
                    protein_info['gene_names'].append(gene['geneName']['value'])
        
        # Extract function
        if 'comments' in data:
            for comment in data['comments']:
                if comment.get('commentType') == 'FUNCTION':
                    protein_info['function'] = comment.get('texts', [{}])[0].get('value', '')
                    break
        
        # Extract subcellular location
        if 'comments' in data:
            for comment in data['comments']:
                if comment.get('commentType') == 'SUBCELLULAR_LOCATION':
                    locations = []
                    for location in comment.get('subcellularLocations', []):
                        if 'location' in location:
                            locations.append(location['location']['value'])
                    protein_info['location'] = locations
        
        # Extract pathways
        if 'dbReferences' in data:
            for ref in data['dbReferences']:
                if ref.get('type') == 'KEGG':
                    protein_info['pathways'].append(ref.get('id', ''))
        
        # Extract diseases
        if 'comments' in data:
            for comment in data['comments']:
                if comment.get('commentType') == 'DISEASE':
                    for disease in comment.get('diseases', []):
                        protein_info['diseases'].append(disease.get('diseaseId', ''))
        
        # Extract synonyms
        if 'proteinDescription' in data:
            for alt_name in data['proteinDescription'].get('alternativeNames', []):
                protein_info['synonyms'].append(alt_name.get('fullName', {}).get('value', ''))
        
        return protein_info
    
    def get_organism_proteins(self, organism_id: str, limit: int = 100) -> List[Dict]:
        """
        Get proteins for a specific organism.
        
        Args:
            organism_id: NCBI taxonomy ID (e.g., '9606' for human)
            limit: Maximum number of results
            
        Returns:
            List of protein information dictionaries
        """
        query = f"organism_id:{organism_id}"
        return self.search_proteins(query, limit)
    
    def get_proteins_by_keyword(self, keyword: str, organism_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Search proteins by keyword.
        
        Args:
            keyword: Search keyword
            organism_id: Optional organism filter
            limit: Maximum number of results
            
        Returns:
            List of protein information dictionaries
        """
        query = keyword
        if organism_id:
            query += f" AND organism_id:{organism_id}"
        
        return self.search_proteins(query, limit)


# Example usage
if __name__ == "__main__":
    api = UniProtAPI()
    
    # Test with insulin
    insulin = api.get_protein_info('P01308')
    print("Insulin protein info:")
    print(insulin)
    
    # Test search
    hormones = api.get_proteins_by_keyword('hormone', '9606', 5)
    print(f"\nFound {len(hormones)} human hormone proteins") 