"""
KEGG API utility for fetching pathway and molecular interaction data.
"""

import requests
from typing import Dict, List, Optional
import time


class KEGGAPI:
    """KEGG API client for fetching pathway and molecular data."""
    
    def __init__(self):
        self.base_url = "https://rest.kegg.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BioSheetAgent/1.0 (https://github.com/your-repo)'
        })
    
    def get_pathway_info(self, pathway_id: str) -> Dict:
        """
        Get pathway information by KEGG pathway ID.
        
        Args:
            pathway_id: KEGG pathway ID (e.g., 'hsa04910' for insulin signaling)
            
        Returns:
            Dictionary containing pathway information
        """
        url = f"{self.base_url}/get/{pathway_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            return self._parse_pathway_data(response.text, pathway_id)
            
        except requests.RequestException as e:
            print(f"Error fetching pathway {pathway_id}: {e}")
            return {}
    
    def search_pathways(self, query: str, organism: str = 'hsa') -> List[Dict]:
        """
        Search for pathways by query.
        
        Args:
            query: Search query
            organism: Organism code (default: 'hsa' for human)
            
        Returns:
            List of pathway information dictionaries
        """
        url = f"{self.base_url}/find/{organism}/pathway/{query}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            pathways = []
            for line in response.text.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        pathway_id = parts[0]
                        pathway_name = parts[1]
                        pathways.append({
                            'pathway_id': pathway_id,
                            'name': pathway_name
                        })
            
            return pathways
            
        except requests.RequestException as e:
            print(f"Error searching pathways: {e}")
            return []
    
    def get_compound_info(self, compound_id: str) -> Dict:
        """
        Get compound information by KEGG compound ID.
        
        Args:
            compound_id: KEGG compound ID (e.g., 'C00031' for glucose)
            
        Returns:
            Dictionary containing compound information
        """
        url = f"{self.base_url}/get/{compound_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            return self._parse_compound_data(response.text, compound_id)
            
        except requests.RequestException as e:
            print(f"Error fetching compound {compound_id}: {e}")
            return {}
    
    def search_compounds(self, query: str) -> List[Dict]:
        """
        Search for compounds by query.
        
        Args:
            query: Search query
            
        Returns:
            List of compound information dictionaries
        """
        url = f"{self.base_url}/find/compound/{query}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            compounds = []
            for line in response.text.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        compound_id = parts[0]
                        compound_name = parts[1]
                        compounds.append({
                            'compound_id': compound_id,
                            'name': compound_name
                        })
            
            return compounds
            
        except requests.RequestException as e:
            print(f"Error searching compounds: {e}")
            return []
    
    def get_gene_info(self, gene_id: str) -> Dict:
        """
        Get gene information by KEGG gene ID.
        
        Args:
            gene_id: KEGG gene ID (e.g., 'hsa:3630' for insulin)
            
        Returns:
            Dictionary containing gene information
        """
        url = f"{self.base_url}/get/{gene_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            return self._parse_gene_data(response.text, gene_id)
            
        except requests.RequestException as e:
            print(f"Error fetching gene {gene_id}: {e}")
            return {}
    
    def search_genes(self, query: str, organism: str = 'hsa') -> List[Dict]:
        """
        Search for genes by query.
        
        Args:
            query: Search query
            organism: Organism code (default: 'hsa' for human)
            
        Returns:
            List of gene information dictionaries
        """
        url = f"{self.base_url}/find/{organism}/{query}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            genes = []
            for line in response.text.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        gene_id = parts[0]
                        gene_name = parts[1]
                        genes.append({
                            'gene_id': gene_id,
                            'name': gene_name
                        })
            
            return genes
            
        except requests.RequestException as e:
            print(f"Error searching genes: {e}")
            return []
    
    def get_pathway_genes(self, pathway_id: str) -> List[Dict]:
        """
        Get genes involved in a pathway.
        
        Args:
            pathway_id: KEGG pathway ID
            
        Returns:
            List of gene information dictionaries
        """
        url = f"{self.base_url}/link/{pathway_id}/gene"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            genes = []
            for line in response.text.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        pathway = parts[0]
                        gene_id = parts[1]
                        gene_info = self.get_gene_info(gene_id)
                        if gene_info:
                            genes.append(gene_info)
            
            return genes
            
        except requests.RequestException as e:
            print(f"Error fetching pathway genes: {e}")
            return []
    
    def get_pathway_compounds(self, pathway_id: str) -> List[Dict]:
        """
        Get compounds involved in a pathway.
        
        Args:
            pathway_id: KEGG pathway ID
            
        Returns:
            List of compound information dictionaries
        """
        url = f"{self.base_url}/link/{pathway_id}/compound"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            compounds = []
            for line in response.text.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        pathway = parts[0]
                        compound_id = parts[1]
                        compound_info = self.get_compound_info(compound_id)
                        if compound_info:
                            compounds.append(compound_info)
            
            return compounds
            
        except requests.RequestException as e:
            print(f"Error fetching pathway compounds: {e}")
            return []
    
    def _parse_pathway_data(self, data: str, pathway_id: str) -> Dict:
        """Parse KEGG pathway data."""
        pathway_info = {
            'pathway_id': pathway_id,
            'name': '',
            'description': '',
            'genes': [],
            'compounds': [],
            'diseases': [],
            'references': []
        }
        
        lines = data.split('\n')
        for line in lines:
            if line.startswith('NAME'):
                pathway_info['name'] = line.split('NAME')[1].strip()
            elif line.startswith('DESCRIPTION'):
                pathway_info['description'] = line.split('DESCRIPTION')[1].strip()
            elif line.startswith('DISEASE'):
                disease = line.split('DISEASE')[1].strip()
                pathway_info['diseases'].append(disease)
            elif line.startswith('REFERENCE'):
                ref = line.split('REFERENCE')[1].strip()
                pathway_info['references'].append(ref)
        
        return pathway_info
    
    def _parse_compound_data(self, data: str, compound_id: str) -> Dict:
        """Parse KEGG compound data."""
        compound_info = {
            'compound_id': compound_id,
            'name': '',
            'formula': '',
            'molecular_weight': '',
            'pathways': [],
            'enzymes': []
        }
        
        lines = data.split('\n')
        for line in lines:
            if line.startswith('NAME'):
                compound_info['name'] = line.split('NAME')[1].strip()
            elif line.startswith('FORMULA'):
                compound_info['formula'] = line.split('FORMULA')[1].strip()
            elif line.startswith('EXACT_MASS'):
                compound_info['molecular_weight'] = line.split('EXACT_MASS')[1].strip()
            elif line.startswith('PATHWAY'):
                pathway = line.split('PATHWAY')[1].strip()
                compound_info['pathways'].append(pathway)
            elif line.startswith('ENZYME'):
                enzyme = line.split('ENZYME')[1].strip()
                compound_info['enzymes'].append(enzyme)
        
        return compound_info
    
    def _parse_gene_data(self, data: str, gene_id: str) -> Dict:
        """Parse KEGG gene data."""
        gene_info = {
            'gene_id': gene_id,
            'name': '',
            'definition': '',
            'pathways': [],
            'orthologs': []
        }
        
        lines = data.split('\n')
        for line in lines:
            if line.startswith('NAME'):
                gene_info['name'] = line.split('NAME')[1].strip()
            elif line.startswith('DEFINITION'):
                gene_info['definition'] = line.split('DEFINITION')[1].strip()
            elif line.startswith('PATHWAY'):
                pathway = line.split('PATHWAY')[1].strip()
                gene_info['pathways'].append(pathway)
            elif line.startswith('ORTHOLOGY'):
                ortholog = line.split('ORTHOLOGY')[1].strip()
                gene_info['orthologs'].append(ortholog)
        
        return gene_info


# Example usage
if __name__ == "__main__":
    api = KEGGAPI()
    
    # Test pathway search
    insulin_pathways = api.search_pathways("insulin")
    print(f"Found {len(insulin_pathways)} insulin-related pathways")
    
    # Test compound search
    glucose = api.get_compound_info("C00031")
    print(f"Glucose info: {glucose['name']}")
    
    # Test gene search
    insulin_gene = api.get_gene_info("hsa:3630")
    print(f"Insulin gene: {insulin_gene['name']}") 