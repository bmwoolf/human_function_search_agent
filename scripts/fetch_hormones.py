"""
Script to fetch hormone data from UniProt, PubMed, and KEGG.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from typing import List, Dict
from tqdm import tqdm
import time
import requests

from utils.uniprot_api import UniProtAPI
from utils.pubmed_scraper import PubMedScraper
# from utils.kegg_api import KEGGAPI
from utils.reactome_api import ReactomeAPI


class HormoneFetcher:
    """Fetcher for hormone-related biological data."""
    
    def __init__(self):
        self.uniprot = UniProtAPI()
        self.pubmed = PubMedScraper()
        # self.kegg = KEGGAPI()  # KEGG temporarily disabled, need commercial license at $5k/year
        self.reactome = ReactomeAPI()
        
        # Only fetch insulin for debugging
        self.hormone_list = [
            'insulin',
            # 'glucagon',
            # 'testosterone',
            # 'estrogen',
            # 'cortisol',
            # 'thyroxine',
            # 'adrenaline',
            # 'noradrenaline',
            # 'melatonin',
            # 'growth hormone',
            # 'prolactin',
            # 'oxytocin',
            # 'vasopressin',
            # 'leptin',
            # 'ghrelin',
            # 'thyroid stimulating hormone',
            # 'follicle stimulating hormone',
            # 'luteinizing hormone',
            # 'adrenocorticotropic hormone',
            # 'aldosterone'
        ]
    
    def fetch_hormone_data(self, hormone_name: str) -> Dict:
        """
        Fetch comprehensive data for a specific hormone.
        
        Args:
            hormone_name: Name of the hormone to fetch
            
        Returns:
            Dictionary containing hormone data
        """
        print(f"Fetching data for {hormone_name}...")
        
        hormone_data = {
            'Name': hormone_name,
            'Type': 'hormone',
            'Function': '',
            'Location': '',
            'Related molecules': '',
            'Related systems': '',
            'Diseases/dysfunctions': '',
            'Source links': '',
            'Synonyms': ''
        }
        
        # Search UniProt for hormone proteins
        try:
            uniprot_results = self.uniprot.get_proteins_by_keyword(
                f"{hormone_name} AND organism_id:9606", limit=10
            )
            print(f"UniProt results: {uniprot_results}")
        except Exception as e:
            print(f"[ERROR] UniProt API call failed: {e}")
            uniprot_results = []
        
        if uniprot_results:
            primary_protein = uniprot_results[0]
            hormone_data['Function'] = primary_protein.get('protein_name', '')
            hormone_data['Location'] = ', '.join(primary_protein.get('subcellular_location', []))
            hormone_data['Related molecules'] = ', '.join(primary_protein.get('gene_names', []))
            hormone_data['Diseases/dysfunctions'] = ', '.join(primary_protein.get('disease', []))
            hormone_data['Synonyms'] = ', '.join(primary_protein.get('protein_name', []))
            uniprot_id = primary_protein.get('accession', '')
            if uniprot_id:
                hormone_data['Source links'] += f"UniProt:{uniprot_id} "
        
        # Search PubMed for recent publications
        pubmed_results = self.pubmed.search_publications(
            f"{hormone_name} hormone", max_results=5
        )
        if pubmed_results:
            pmids = [pub['pmid'] for pub in pubmed_results]
            hormone_data['Source links'] += f"PubMed:{','.join(pmids)} "
        
        # KEGG API temporarily disabled
        # try:
        #     kegg_pathways = self.kegg.search_pathways(hormone_name)
        #     print(f"KEGG pathways: {kegg_pathways}")
        # except Exception as e:
        #     print(f"[ERROR] KEGG API call failed: {e}")
        #     kegg_pathways = []
        # if kegg_pathways:
        #     pathway_ids = [path['pathway_id'] for path in kegg_pathways[:3]]
        #     hormone_data['Source links'] += f"KEGG:{','.join(pathway_ids)} "
        #     pathway_names = [path['name'] for path in kegg_pathways[:3]]
        #     hormone_data['Related systems'] = ', '.join(pathway_names)

        # Reactome API for pathway data
        reactome_pathways = []
        try:
            # Try hormone name first
            reactome_pathways = self.reactome.search_pathways(hormone_name)
            print(f"Reactome pathways (by name): {reactome_pathways}")
            # If no results, try gene symbol from UniProt
            if not reactome_pathways and uniprot_results and uniprot_results[0].get('gene_names'):
                gene_symbol = uniprot_results[0]['gene_names'][0]
                reactome_pathways = self.reactome.search_pathways(gene_symbol)
                print(f"Reactome pathways (by gene): {reactome_pathways}")
            # If still no results, try UniProt accession
            if not reactome_pathways and uniprot_results and uniprot_results[0].get('uniprot_id'):
                uniprot_id = uniprot_results[0]['uniprot_id']
                reactome_pathways = self.reactome.get_pathways_for_uniprot(uniprot_id)
                print(f"Reactome pathways (by UniProt): {reactome_pathways}")
        except Exception as e:
            print(f"[ERROR] Reactome API call failed: {e}")
            reactome_pathways = []
        if reactome_pathways:
            pathway_ids = [p.get('stId') for p in reactome_pathways[:3] if p.get('stId')]
            hormone_data['Source links'] += f"Reactome:{','.join(pathway_ids)} "
            pathway_names = [p.get('displayName') for p in reactome_pathways[:3] if p.get('displayName')]
            hormone_data['Related systems'] = ', '.join(pathway_names)
        # Display more UniProt fields in output
        if uniprot_results:
            primary_protein = uniprot_results[0]
            hormone_data['Function'] = primary_protein.get('function', '')
            hormone_data['Location'] = ', '.join(primary_protein.get('location', []))
            hormone_data['Related molecules'] = ', '.join(primary_protein.get('gene_names', []))
            hormone_data['Diseases/dysfunctions'] = ', '.join(primary_protein.get('diseases', []))
            hormone_data['Synonyms'] = ', '.join(primary_protein.get('synonyms', []))
        
        return hormone_data
    
    def fetch_all_hormones(self) -> pd.DataFrame:
        """
        Fetch data for all hormones in the list.
        
        Returns:
            DataFrame containing hormone data
        """
        hormone_data_list = []
        
        for hormone in tqdm(self.hormone_list, desc="Fetching hormones"):
            try:
                hormone_data = self.fetch_hormone_data(hormone)
                hormone_data_list.append(hormone_data)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error fetching {hormone}: {e}")
                continue
        
        return pd.DataFrame(hormone_data_list)
    
    def save_to_csv(self, df: pd.DataFrame, filename: str = '../data/hormones.csv'):
        """Save hormone data to CSV file."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_csv(filename, index=False)
        print(f"Hormone data saved to {filename}")
    
    def save_to_excel(self, df: pd.DataFrame, filename: str = '../data/hormones.xlsx'):
        """Save hormone data to Excel file."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_excel(filename, index=False)
        print(f"Hormone data saved to {filename}")


def main():
    """Main function to run hormone data fetching."""
    fetcher = HormoneFetcher()
    
    print("Starting hormone data collection...")
    hormone_df = fetcher.fetch_all_hormones()
    
    if not hormone_df.empty:
        print(f"Collected data for {len(hormone_df)} hormones")
        
        # Save to both CSV and Excel
        fetcher.save_to_csv(hormone_df)
        fetcher.save_to_excel(hormone_df)
        
        # Display summary
        print("\nHormone data summary:")
        print(hormone_df[['Name', 'Function', 'Location']].head())
    else:
        print("No hormone data collected.")


if __name__ == "__main__":
    main() 