"""
Script to fetch enzyme data from UniProt, PubMed, and KEGG.
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


class EnzymeFetcher:
    """Fetcher for enzyme-related biological data."""
    
    def __init__(self):
        self.uniprot = UniProtAPI()
        self.pubmed = PubMedScraper()
        self.kegg = KEGGAPI()
        
        # Common human enzymes to fetch
        self.enzyme_list = [
            'glucose-6-phosphate dehydrogenase', 'hexokinase', 'pyruvate kinase',
            'lactate dehydrogenase', 'creatine kinase', 'alkaline phosphatase',
            'aspartate aminotransferase', 'alanine aminotransferase',
            'gamma-glutamyl transferase', 'amylase', 'lipase', 'trypsin',
            'chymotrypsin', 'pepsin', 'carbonic anhydrase', 'catalase',
            'superoxide dismutase', 'glutathione peroxidase', 'cytochrome oxidase',
            'ATP synthase', 'DNA polymerase', 'RNA polymerase', 'helicase',
            'ligase', 'kinase', 'phosphatase', 'protease', 'nuclease'
        ]
    
    def fetch_enzyme_data(self, enzyme_name: str) -> Dict:
        """
        Fetch comprehensive data for a specific enzyme.
        
        Args:
            enzyme_name: Name of the enzyme to fetch
            
        Returns:
            Dictionary containing enzyme data
        """
        print(f"Fetching data for {enzyme_name}...")
        
        enzyme_data = {
            'Name': enzyme_name,
            'Type': 'enzyme',
            'Function': '',
            'Location': '',
            'Related molecules': '',
            'Related systems': '',
            'Diseases/dysfunctions': '',
            'Source links': '',
            'Synonyms': ''
        }
        
        # Search UniProt for enzyme proteins
        uniprot_results = self.uniprot.get_proteins_by_keyword(
            enzyme_name, organism_id='9606', limit=10
        )
        
        if uniprot_results:
            # Use the first result as primary data
            primary_protein = uniprot_results[0]
            
            enzyme_data['Function'] = primary_protein.get('function', '')
            enzyme_data['Location'] = ', '.join(primary_protein.get('location', []))
            enzyme_data['Related molecules'] = ', '.join(primary_protein.get('gene_names', []))
            enzyme_data['Diseases/dysfunctions'] = ', '.join(primary_protein.get('diseases', []))
            enzyme_data['Synonyms'] = ', '.join(primary_protein.get('synonyms', []))
            
            # Add UniProt ID to source links
            uniprot_id = primary_protein.get('uniprot_id', '')
            if uniprot_id:
                enzyme_data['Source links'] += f"UniProt:{uniprot_id} "
        
        # Search PubMed for recent publications
        pubmed_results = self.pubmed.search_publications(
            f"{enzyme_name} enzyme", max_results=5
        )
        
        if pubmed_results:
            pmids = [pub['pmid'] for pub in pubmed_results]
            enzyme_data['Source links'] += f"PubMed:{','.join(pmids)} "
        
        # Search KEGG for pathways
        kegg_pathways = self.kegg.search_pathways(enzyme_name)
        if kegg_pathways:
            pathway_ids = [path['pathway_id'] for path in kegg_pathways[:3]]
            enzyme_data['Source links'] += f"KEGG:{','.join(pathway_ids)} "
            
            # Add pathway information to related systems
            pathway_names = [path['name'] for path in kegg_pathways[:3]]
            enzyme_data['Related systems'] = ', '.join(pathway_names)
        
        return enzyme_data
    
    def fetch_all_enzymes(self) -> pd.DataFrame:
        """
        Fetch data for all enzymes in the list.
        
        Returns:
            DataFrame containing enzyme data
        """
        enzyme_data_list = []
        
        for enzyme in tqdm(self.enzyme_list, desc="Fetching enzymes"):
            try:
                enzyme_data = self.fetch_enzyme_data(enzyme)
                enzyme_data_list.append(enzyme_data)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error fetching {enzyme}: {e}")
                continue
        
        return pd.DataFrame(enzyme_data_list)
    
    def save_to_csv(self, df: pd.DataFrame, filename: str = '../data/enzymes.csv'):
        """Save enzyme data to CSV file."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_csv(filename, index=False)
        print(f"Enzyme data saved to {filename}")
    
    def save_to_excel(self, df: pd.DataFrame, filename: str = '../data/enzymes.xlsx'):
        """Save enzyme data to Excel file."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_excel(filename, index=False)
        print(f"Enzyme data saved to {filename}")


def main():
    """Main function to run enzyme data fetching."""
    fetcher = EnzymeFetcher()
    
    print("Starting enzyme data collection...")
    enzyme_df = fetcher.fetch_all_enzymes()
    
    if not enzyme_df.empty:
        print(f"Collected data for {len(enzyme_df)} enzymes")
        
        # Save to both CSV and Excel
        fetcher.save_to_csv(enzyme_df)
        fetcher.save_to_excel(enzyme_df)
        
        # Display summary
        print("\nEnzyme data summary:")
        print(enzyme_df[['Name', 'Function', 'Location']].head())
    else:
        print("No enzyme data collected.")


if __name__ == "__main__":
    main() 