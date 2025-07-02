"""
Script to fetch foreign amino acid data from UniProt, PubMed, and KEGG.
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


class ForeignAminoAcidFetcher:
    """Fetcher for foreign amino acid data."""
    
    def __init__(self):
        self.uniprot = UniProtAPI()
        self.pubmed = PubMedScraper()
        self.kegg = KEGGAPI()
        
        # Non-standard/foreign amino acids
        self.foreign_amino_acids = [
            'selenocysteine', 'pyrrolysine', 'hydroxyproline', 'hydroxylysine',
            'gamma-carboxyglutamic acid', 'citrulline', 'ornithine', 'taurine',
            'beta-alanine', 'gamma-aminobutyric acid', 'dopamine', 'serotonin',
            'histamine', 'carnosine', 'anserine', 'homocysteine', 'cystathionine',
            'sarcosine', 'betaine', 'creatine', 'carnitine', 'acetylcarnitine'
        ]
        
        # KEGG compound IDs for some foreign amino acids
        self.foreign_aa_kegg_ids = {
            'selenocysteine': 'C00768',
            'pyrrolysine': 'C16138',
            'hydroxyproline': 'C01157',
            'hydroxylysine': 'C00956',
            'gamma-carboxyglutamic acid': 'C02051',
            'citrulline': 'C00327',
            'ornithine': 'C00077',
            'taurine': 'C00245',
            'beta-alanine': 'C00099',
            'gamma-aminobutyric acid': 'C00334',
            'dopamine': 'C03758',
            'serotonin': 'C00780',
            'histamine': 'C00388',
            'carnosine': 'C00386',
            'anserine': 'C01262',
            'homocysteine': 'C00155',
            'cystathionine': 'C02291',
            'sarcosine': 'C00213',
            'betaine': 'C00719',
            'creatine': 'C00300',
            'carnitine': 'C00318',
            'acetylcarnitine': 'C02571'
        }
    
    def fetch_foreign_aa_data(self, amino_acid: str) -> Dict:
        """
        Fetch comprehensive data for a specific foreign amino acid.
        
        Args:
            amino_acid: Name of the foreign amino acid to fetch
            
        Returns:
            Dictionary containing foreign amino acid data
        """
        print(f"Fetching data for {amino_acid}...")
        
        aa_data = {
            'Name': amino_acid,
            'Type': 'foreign_amino_acid',
            'Function': '',
            'Location': '',
            'Related molecules': '',
            'Related systems': '',
            'Diseases/dysfunctions': '',
            'Source links': '',
            'Synonyms': ''
        }
        
        # Get KEGG compound information
        kegg_id = self.foreign_aa_kegg_ids.get(amino_acid.lower())
        if kegg_id:
            compound_info = self.kegg.get_compound_info(kegg_id)
            if compound_info:
                aa_data['Function'] = compound_info.get('name', '')
                aa_data['Related molecules'] = ', '.join(compound_info.get('enzymes', []))
                aa_data['Source links'] += f"KEGG:{kegg_id} "
        
        # Search UniProt for amino acid-related proteins
        uniprot_results = self.uniprot.get_proteins_by_keyword(
            f"{amino_acid} metabolism", organism_id='9606', limit=5
        )
        
        if uniprot_results:
            # Use the first result as primary data
            primary_protein = uniprot_results[0]
            
            if not aa_data['Function']:
                aa_data['Function'] = primary_protein.get('function', '')
            
            aa_data['Location'] = ', '.join(primary_protein.get('location', []))
            aa_data['Related molecules'] += ', ' + ', '.join(primary_protein.get('gene_names', []))
            aa_data['Diseases/dysfunctions'] = ', '.join(primary_protein.get('diseases', []))
            aa_data['Synonyms'] = ', '.join(primary_protein.get('synonyms', []))
            
            # Add UniProt ID to source links
            uniprot_id = primary_protein.get('uniprot_id', '')
            if uniprot_id:
                aa_data['Source links'] += f"UniProt:{uniprot_id} "
        
        # Search PubMed for recent publications
        pubmed_results = self.pubmed.search_publications(
            f"{amino_acid} non-standard amino acid", max_results=5
        )
        
        if pubmed_results:
            pmids = [pub['pmid'] for pub in pubmed_results]
            aa_data['Source links'] += f"PubMed:{','.join(pmids)} "
        
        # Search KEGG for pathways
        kegg_pathways = self.kegg.search_pathways(f"{amino_acid} metabolism")
        if kegg_pathways:
            pathway_ids = [path['pathway_id'] for path in kegg_pathways[:3]]
            aa_data['Source links'] += f"KEGG_pathway:{','.join(pathway_ids)} "
            
            # Add pathway information to related systems
            pathway_names = [path['name'] for path in kegg_pathways[:3]]
            aa_data['Related systems'] = ', '.join(pathway_names)
        
        # Add common functions for specific amino acids
        function_mapping = {
            'selenocysteine': 'Selenium-containing amino acid, antioxidant function',
            'pyrrolysine': 'Rare amino acid found in archaea and bacteria',
            'hydroxyproline': 'Modified proline, important in collagen structure',
            'hydroxylysine': 'Modified lysine, important in collagen cross-linking',
            'gamma-carboxyglutamic acid': 'Vitamin K-dependent modification, blood clotting',
            'citrulline': 'Urea cycle intermediate, nitric oxide precursor',
            'ornithine': 'Urea cycle intermediate, polyamine synthesis',
            'taurine': 'Sulfonic acid derivative, bile acid conjugation',
            'beta-alanine': 'Beta amino acid, carnosine synthesis',
            'gamma-aminobutyric acid': 'Neurotransmitter, inhibitory function',
            'dopamine': 'Neurotransmitter, reward and movement',
            'serotonin': 'Neurotransmitter, mood and sleep regulation',
            'histamine': 'Inflammatory mediator, gastric acid secretion',
            'carnosine': 'Dipeptide, muscle buffering and antioxidant',
            'anserine': 'Dipeptide, similar to carnosine',
            'homocysteine': 'Methionine metabolism intermediate',
            'cystathionine': 'Cysteine biosynthesis intermediate',
            'sarcosine': 'Glycine metabolism intermediate',
            'betaine': 'Methyl donor, osmolyte',
            'creatine': 'Energy metabolism, muscle function',
            'carnitine': 'Fatty acid transport, energy metabolism',
            'acetylcarnitine': 'Carnitine derivative, energy metabolism'
        }
        
        if not aa_data['Function'] and amino_acid in function_mapping:
            aa_data['Function'] = function_mapping[amino_acid]
        
        return aa_data
    
    def fetch_all_foreign_aas(self) -> pd.DataFrame:
        """
        Fetch data for all foreign amino acids in the list.
        
        Returns:
            DataFrame containing foreign amino acid data
        """
        aa_data_list = []
        
        for amino_acid in tqdm(self.foreign_amino_acids, desc="Fetching foreign amino acids"):
            try:
                aa_data = self.fetch_foreign_aa_data(amino_acid)
                aa_data_list.append(aa_data)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error fetching {amino_acid}: {e}")
                continue
        
        return pd.DataFrame(aa_data_list)
    
    def save_to_csv(self, df: pd.DataFrame, filename: str = '../data/foreign_amino_acids.csv'):
        """Save foreign amino acid data to CSV file."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_csv(filename, index=False)
        print(f"Foreign amino acid data saved to {filename}")
    
    def save_to_excel(self, df: pd.DataFrame, filename: str = '../data/foreign_amino_acids.xlsx'):
        """Save foreign amino acid data to Excel file."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_excel(filename, index=False)
        print(f"Foreign amino acid data saved to {filename}")


def main():
    """Main function to run foreign amino acid data fetching."""
    fetcher = ForeignAminoAcidFetcher()
    
    print("Starting foreign amino acid data collection...")
    aa_df = fetcher.fetch_all_foreign_aas()
    
    if not aa_df.empty:
        print(f"Collected data for {len(aa_df)} foreign amino acids")
        
        # Save to both CSV and Excel
        fetcher.save_to_csv(aa_df)
        fetcher.save_to_excel(aa_df)
        
        # Display summary
        print("\nForeign amino acid data summary:")
        print(aa_df[['Name', 'Function', 'Location']].head())
    else:
        print("No foreign amino acid data collected.")


if __name__ == "__main__":
    main() 