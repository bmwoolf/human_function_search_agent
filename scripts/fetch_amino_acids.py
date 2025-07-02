"""
Script to fetch endogenous amino acid data from UniProt, PubMed, and Reactome.
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
# from utils.kegg_api import KEGGAPI  # KEGG temporarily disabled, need commercial license
from utils.reactome_api import ReactomeAPI


class AminoAcidFetcher:
    """Fetcher for endogenous amino acid data."""
    
    def __init__(self):
        self.uniprot = UniProtAPI()
        self.pubmed = PubMedScraper()
        # self.kegg = KEGGAPI()  # KEGG temporarily disabled, need commercial license
        self.reactome = ReactomeAPI()
        
        # Standard 20 amino acids
        self.amino_acids = [
            'alanine', 'arginine', 'asparagine', 'aspartic acid', 'cysteine',
            'glutamic acid', 'glutamine', 'glycine', 'histidine', 'isoleucine',
            'leucine', 'lysine', 'methionine', 'phenylalanine', 'proline',
            'serine', 'threonine', 'tryptophan', 'tyrosine', 'valine'
        ]
        
        # KEGG compound IDs for amino acids (for reference, not used currently)
        self.amino_acid_kegg_ids = {
            'alanine': 'C00041',
            'arginine': 'C00062',
            'asparagine': 'C00152',
            'aspartic acid': 'C00049',
            'cysteine': 'C00097',
            'glutamic acid': 'C00025',
            'glutamine': 'C00064',
            'glycine': 'C00037',
            'histidine': 'C00135',
            'isoleucine': 'C00407',
            'leucine': 'C00123',
            'lysine': 'C00047',
            'methionine': 'C00073',
            'phenylalanine': 'C00079',
            'proline': 'C00148',
            'serine': 'C00065',
            'threonine': 'C00188',
            'tryptophan': 'C00078',
            'tyrosine': 'C00082',
            'valine': 'C00183'
        }
    
    def fetch_amino_acid_data(self, amino_acid: str) -> Dict:
        """
        Fetch comprehensive data for a specific amino acid.
        
        Args:
            amino_acid: Name of the amino acid to fetch
            
        Returns:
            Dictionary containing amino acid data
        """
        print(f"Fetching data for {amino_acid}...")
        
        amino_acid_data = {
            'Name': amino_acid,
            'Type': 'amino_acid',
            'Function': '',
            'Location': '',
            'Related molecules': '',
            'Related systems': '',
            'Diseases/dysfunctions': '',
            'Source links': '',
            'Synonyms': ''
        }
        
        # KEGG API temporarily disabled
        # kegg_id = self.amino_acid_kegg_ids.get(amino_acid.lower())
        # if kegg_id:
        #     try:
        #         compound_info = self.kegg.get_compound_info(kegg_id)
        #         print(f"KEGG compound info: {compound_info}")
        #     except Exception as e:
        #         print(f"[ERROR] KEGG API call failed: {e}")
        #         compound_info = None
        #     if compound_info:
        #         amino_acid_data['Function'] = compound_info.get('name', '')
        #         amino_acid_data['Related molecules'] = ', '.join(compound_info.get('enzymes', []))
        #         amino_acid_data['Source links'] += f"KEGG:{kegg_id} "
        
        # Search UniProt for amino acid-related proteins
        try:
            uniprot_results = self.uniprot.get_proteins_by_keyword(
                f"{amino_acid} AND organism_id:9606", limit=5
            )
            print(f"UniProt results: {uniprot_results}")
        except Exception as e:
            print(f"[ERROR] UniProt API call failed: {e}")
            uniprot_results = []
        
        if uniprot_results:
            primary_protein = uniprot_results[0]
            if not amino_acid_data['Function']:
                amino_acid_data['Function'] = primary_protein.get('function', '')
            amino_acid_data['Location'] = ', '.join(primary_protein.get('location', []))
            amino_acid_data['Related molecules'] += ', ' + ', '.join(primary_protein.get('gene_names', []))
            amino_acid_data['Diseases/dysfunctions'] = ', '.join(primary_protein.get('diseases', []))
            amino_acid_data['Synonyms'] = ', '.join(primary_protein.get('synonyms', []))
            uniprot_id = primary_protein.get('uniprot_id', '')
            if uniprot_id:
                amino_acid_data['Source links'] += f"UniProt:{uniprot_id} "
        
        # Search PubMed for recent publications
        pubmed_results = self.pubmed.search_publications(
            f"{amino_acid} amino acid metabolism", max_results=5
        )
        if pubmed_results:
            pmids = [pub['pmid'] for pub in pubmed_results]
            amino_acid_data['Source links'] += f"PubMed:{','.join(pmids)} "
        
        # KEGG API temporarily disabled
        # try:
        #     kegg_pathways = self.kegg.search_pathways(f"{amino_acid} metabolism")
        #     print(f"KEGG pathways: {kegg_pathways}")
        # except Exception as e:
        #     print(f"[ERROR] KEGG API call failed: {e}")
        #     kegg_pathways = []
        # if kegg_pathways:
        #     pathway_ids = [path['pathway_id'] for path in kegg_pathways[:3]]
        #     amino_acid_data['Source links'] += f"KEGG_pathway:{','.join(pathway_ids)} "
        #     pathway_names = [path['name'] for path in kegg_pathways[:3]]
        #     amino_acid_data['Related systems'] = ', '.join(pathway_names)

        # Reactome API for pathway data
        reactome_pathways = []
        try:
            # Try amino acid name first
            reactome_pathways = self.reactome.search_pathways(amino_acid)
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
            # If still no results, try '<amino acid> metabolism'
            if not reactome_pathways:
                metabolism_term = f"{amino_acid} metabolism"
                reactome_pathways = self.reactome.search_pathways(metabolism_term)
                print(f"Reactome pathways (by metabolism): {reactome_pathways}")
            # If still no results, try known stable IDs for major amino acids
            if not reactome_pathways:
                known_pathways = {
                    'alanine': [{'stId': 'R-HSA-352230', 'displayName': 'Amino acid metabolism', 'url': 'https://reactome.org/content/detail/R-HSA-352230'}],
                    'arginine': [{'stId': 'R-HSA-352230', 'displayName': 'Amino acid metabolism', 'url': 'https://reactome.org/content/detail/R-HSA-352230'}],
                    'asparagine': [{'stId': 'R-HSA-352230', 'displayName': 'Amino acid metabolism', 'url': 'https://reactome.org/content/detail/R-HSA-352230'}],
                    'aspartic acid': [{'stId': 'R-HSA-352230', 'displayName': 'Amino acid metabolism', 'url': 'https://reactome.org/content/detail/R-HSA-352230'}],
                    'cysteine': [{'stId': 'R-HSA-352230', 'displayName': 'Amino acid metabolism', 'url': 'https://reactome.org/content/detail/R-HSA-352230'}],
                    'glutamic acid': [{'stId': 'R-HSA-352230', 'displayName': 'Amino acid metabolism', 'url': 'https://reactome.org/content/detail/R-HSA-352230'}],
                    'glutamine': [{'stId': 'R-HSA-352230', 'displayName': 'Amino acid metabolism', 'url': 'https://reactome.org/content/detail/R-HSA-352230'}],
                    'glycine': [{'stId': 'R-HSA-352230', 'displayName': 'Amino acid metabolism', 'url': 'https://reactome.org/content/detail/R-HSA-352230'}],
                    'histidine': [{'stId': 'R-HSA-352230', 'displayName': 'Amino acid metabolism', 'url': 'https://reactome.org/content/detail/R-HSA-352230'}],
                    'isoleucine': [{'stId': 'R-HSA-352230', 'displayName': 'Amino acid metabolism', 'url': 'https://reactome.org/content/detail/R-HSA-352230'}],
                    'leucine': [{'stId': 'R-HSA-352230', 'displayName': 'Amino acid metabolism', 'url': 'https://reactome.org/content/detail/R-HSA-352230'}],
                    'lysine': [{'stId': 'R-HSA-352230', 'displayName': 'Amino acid metabolism', 'url': 'https://reactome.org/content/detail/R-HSA-352230'}],
                    'methionine': [{'stId': 'R-HSA-352230', 'displayName': 'Amino acid metabolism', 'url': 'https://reactome.org/content/detail/R-HSA-352230'}],
                    'phenylalanine': [{'stId': 'R-HSA-352230', 'displayName': 'Amino acid metabolism', 'url': 'https://reactome.org/content/detail/R-HSA-352230'}],
                    'proline': [{'stId': 'R-HSA-352230', 'displayName': 'Amino acid metabolism', 'url': 'https://reactome.org/content/detail/R-HSA-352230'}],
                    'serine': [{'stId': 'R-HSA-352230', 'displayName': 'Amino acid metabolism', 'url': 'https://reactome.org/content/detail/R-HSA-352230'}],
                    'threonine': [{'stId': 'R-HSA-352230', 'displayName': 'Amino acid metabolism', 'url': 'https://reactome.org/content/detail/R-HSA-352230'}],
                    'tryptophan': [{'stId': 'R-HSA-352230', 'displayName': 'Amino acid metabolism', 'url': 'https://reactome.org/content/detail/R-HSA-352230'}],
                    'tyrosine': [{'stId': 'R-HSA-352230', 'displayName': 'Amino acid metabolism', 'url': 'https://reactome.org/content/detail/R-HSA-352230'}],
                    'valine': [{'stId': 'R-HSA-352230', 'displayName': 'Amino acid metabolism', 'url': 'https://reactome.org/content/detail/R-HSA-352230'}]
                }
                
                if amino_acid.lower() in known_pathways:
                    reactome_pathways = known_pathways[amino_acid.lower()]
                    print(f"Reactome pathways (by stable ID): {reactome_pathways}")
        except Exception as e:
            print(f"[ERROR] Reactome API call failed: {e}")
            reactome_pathways = []
        if reactome_pathways:
            pathway_ids = [p.get('stId') for p in reactome_pathways[:3] if p.get('stId')]
            amino_acid_data['Source links'] += f"Reactome:{','.join(pathway_ids)} "
            pathway_names = [p.get('displayName') for p in reactome_pathways[:3] if p.get('displayName')]
            amino_acid_data['Related systems'] = ', '.join(pathway_names)
        
        return amino_acid_data
    
    def fetch_all_amino_acids(self) -> pd.DataFrame:
        """
        Fetch data for all amino acids in the list.
        
        Returns:
            DataFrame containing amino acid data
        """
        amino_acid_data_list = []
        
        for amino_acid in tqdm(self.amino_acids, desc="Fetching amino acids"):
            try:
                amino_acid_data = self.fetch_amino_acid_data(amino_acid)
                amino_acid_data_list.append(amino_acid_data)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error fetching {amino_acid}: {e}")
                continue
        
        return pd.DataFrame(amino_acid_data_list)
    
    def save_to_csv(self, df: pd.DataFrame, filename: str = 'data/amino_acids.csv'):
        """Save amino acid data to CSV file."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_csv(filename, index=False)
        print(f"Amino acid data saved to {filename}")
    
    def save_to_excel(self, df: pd.DataFrame, filename: str = 'data/amino_acids.xlsx'):
        """Save amino acid data to Excel file."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_excel(filename, index=False)
        print(f"Amino acid data saved to {filename}")


def main():
    """Main function to run amino acid data fetching."""
    fetcher = AminoAcidFetcher()
    
    print("Starting amino acid data collection...")
    amino_acid_df = fetcher.fetch_all_amino_acids()
    
    if not amino_acid_df.empty:
        print(f"Collected data for {len(amino_acid_df)} amino acids")
        
        # Save to both CSV and Excel
        fetcher.save_to_csv(amino_acid_df)
        fetcher.save_to_excel(amino_acid_df)
        
        # Display summary
        print("\nAmino acid data summary:")
        print(amino_acid_df[['Name', 'Function', 'Location']].head())
    else:
        print("No amino acid data collected.")


if __name__ == "__main__":
    main() 