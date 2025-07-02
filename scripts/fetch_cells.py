"""
Script to fetch human cell data from UniProt, PubMed, and KEGG.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from typing import List, Dict
from tqdm import tqdm
import time

from utils.uniprot_api import UniProtAPI
from utils.pubmed_scraper import PubMedScraper
from utils.kegg_api import KEGGAPI


class CellFetcher:
    """Fetcher for human cell-related biological data."""
    
    def __init__(self):
        self.uniprot = UniProtAPI()
        self.pubmed = PubMedScraper()
        self.kegg = KEGGAPI()
        
        # Common human cell types to fetch
        self.cell_types = [
            'hepatocyte', 'neuron', 'cardiomyocyte', 'erythrocyte', 'leukocyte',
            'fibroblast', 'epithelial cell', 'endothelial cell', 'adipocyte',
            'osteocyte', 'chondrocyte', 'myocyte', 'keratinocyte', 'melanocyte',
            'enterocyte', 'pneumocyte', 'nephron', 'beta cell', 'alpha cell',
            'dendritic cell', 'macrophage', 'lymphocyte', 'platelet', 'stem cell'
        ]
    
    def fetch_cell_data(self, cell_type: str) -> Dict:
        """
        Fetch comprehensive data for a specific cell type.
        
        Args:
            cell_type: Name of the cell type to fetch
            
        Returns:
            Dictionary containing cell data
        """
        print(f"Fetching data for {cell_type}...")
        
        cell_data = {
            'Name': cell_type,
            'Type': 'cell',
            'Function': '',
            'Location': '',
            'Related molecules': '',
            'Related systems': '',
            'Diseases/dysfunctions': '',
            'Source links': '',
            'Synonyms': ''
        }
        
        # Search UniProt for cell-specific proteins
        uniprot_results = self.uniprot.get_proteins_by_keyword(
            f"{cell_type} specific", organism_id='9606', limit=10
        )
        
        if uniprot_results:
            # Use the first result as primary data
            primary_protein = uniprot_results[0]
            
            cell_data['Function'] = primary_protein.get('function', '')
            cell_data['Location'] = ', '.join(primary_protein.get('location', []))
            cell_data['Related molecules'] = ', '.join(primary_protein.get('gene_names', []))
            cell_data['Diseases/dysfunctions'] = ', '.join(primary_protein.get('diseases', []))
            cell_data['Synonyms'] = ', '.join(primary_protein.get('synonyms', []))
            
            # Add UniProt ID to source links
            uniprot_id = primary_protein.get('uniprot_id', '')
            if uniprot_id:
                cell_data['Source links'] += f"UniProt:{uniprot_id} "
        
        # Search PubMed for recent publications
        pubmed_results = self.pubmed.search_publications(
            f"{cell_type} human cell", max_results=5
        )
        
        if pubmed_results:
            pmids = [pub['pmid'] for pub in pubmed_results]
            cell_data['Source links'] += f"PubMed:{','.join(pmids)} "
        
        # Search KEGG for cell-related pathways
        kegg_pathways = self.kegg.search_pathways(f"{cell_type} cell")
        if kegg_pathways:
            pathway_ids = [path['pathway_id'] for path in kegg_pathways[:3]]
            cell_data['Source links'] += f"KEGG:{','.join(pathway_ids)} "
            
            # Add pathway information to related systems
            pathway_names = [path['name'] for path in kegg_pathways[:3]]
            cell_data['Related systems'] = ', '.join(pathway_names)
        
        # Add tissue/organ information based on cell type
        tissue_mapping = {
            'hepatocyte': 'Liver',
            'neuron': 'Brain, Nervous system',
            'cardiomyocyte': 'Heart',
            'erythrocyte': 'Blood',
            'leukocyte': 'Blood, Immune system',
            'fibroblast': 'Connective tissue',
            'epithelial cell': 'Epithelial tissue',
            'endothelial cell': 'Blood vessels',
            'adipocyte': 'Adipose tissue',
            'osteocyte': 'Bone',
            'chondrocyte': 'Cartilage',
            'myocyte': 'Muscle',
            'keratinocyte': 'Skin',
            'melanocyte': 'Skin',
            'enterocyte': 'Intestine',
            'pneumocyte': 'Lung',
            'nephron': 'Kidney',
            'beta cell': 'Pancreas',
            'alpha cell': 'Pancreas',
            'dendritic cell': 'Immune system',
            'macrophage': 'Immune system',
            'lymphocyte': 'Immune system',
            'platelet': 'Blood',
            'stem cell': 'Various tissues'
        }
        
        if not cell_data['Location'] and cell_type in tissue_mapping:
            cell_data['Location'] = tissue_mapping[cell_type]
        
        return cell_data
    
    def fetch_all_cells(self) -> pd.DataFrame:
        """
        Fetch data for all cell types in the list.
        
        Returns:
            DataFrame containing cell data
        """
        cell_data_list = []
        
        for cell_type in tqdm(self.cell_types, desc="Fetching cells"):
            try:
                cell_data = self.fetch_cell_data(cell_type)
                cell_data_list.append(cell_data)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error fetching {cell_type}: {e}")
                continue
        
        return pd.DataFrame(cell_data_list)
    
    def save_to_csv(self, df: pd.DataFrame, filename: str = '../data/human_cells.csv'):
        """Save cell data to CSV file."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_csv(filename, index=False)
        print(f"Cell data saved to {filename}")
    
    def save_to_excel(self, df: pd.DataFrame, filename: str = '../data/human_cells.xlsx'):
        """Save cell data to Excel file."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_excel(filename, index=False)
        print(f"Cell data saved to {filename}")


def main():
    """Main function to run cell data fetching."""
    fetcher = CellFetcher()
    
    print("Starting human cell data collection...")
    cell_df = fetcher.fetch_all_cells()
    
    if not cell_df.empty:
        print(f"Collected data for {len(cell_df)} cell types")
        
        # Save to both CSV and Excel
        fetcher.save_to_csv(cell_df)
        fetcher.save_to_excel(cell_df)
        
        # Display summary
        print("\nCell data summary:")
        print(cell_df[['Name', 'Function', 'Location']].head())
    else:
        print("No cell data collected.")


if __name__ == "__main__":
    main() 