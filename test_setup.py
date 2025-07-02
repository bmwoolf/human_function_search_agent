"""
Test script to verify BioSheetAgent setup.
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import pandas as pd
        print("✓ pandas imported successfully")
    except ImportError as e:
        print(f"✗ pandas import failed: {e}")
        return False
    
    try:
        import requests
        print("✓ requests imported successfully")
    except ImportError as e:
        print(f"✗ requests import failed: {e}")
        return False
    
    try:
        from utils.uniprot_api import UniProtAPI
        print("✓ UniProtAPI imported successfully")
    except ImportError as e:
        print(f"✗ UniProtAPI import failed: {e}")
        return False
    
    try:
        from utils.pubmed_scraper import PubMedScraper
        print("✓ PubMedScraper imported successfully")
    except ImportError as e:
        print(f"✗ PubMedScraper import failed: {e}")
        return False
    
    try:
        from utils.kegg_api import KEGGAPI
        print("✓ KEGGAPI imported successfully")
    except ImportError as e:
        print(f"✗ KEGGAPI import failed: {e}")
        return False
    
    return True


def test_api_connections():
    """Test basic API connections."""
    print("\nTesting API connections...")
    
    try:
        from utils.uniprot_api import UniProtAPI
        uniprot = UniProtAPI()
        # Test a simple search
        results = uniprot.get_proteins_by_keyword("insulin", organism_id='9606', limit=1)
        if results:
            print("✓ UniProt API connection successful")
        else:
            print("⚠ UniProt API returned no results (may be rate limited)")
    except Exception as e:
        print(f"✗ UniProt API test failed: {e}")
    
    try:
        from utils.kegg_api import KEGGAPI
        kegg = KEGGAPI()
        # Test a simple compound lookup
        glucose = kegg.get_compound_info("C00031")
        if glucose:
            print("✓ KEGG API connection successful")
        else:
            print("⚠ KEGG API returned no results")
    except Exception as e:
        print(f"✗ KEGG API test failed: {e}")


def test_fetcher_classes():
    """Test that fetcher classes can be instantiated."""
    print("\nTesting fetcher classes...")
    
    try:
        from scripts.fetch_hormones import HormoneFetcher
        fetcher = HormoneFetcher()
        print("✓ HormoneFetcher instantiated successfully")
    except Exception as e:
        print(f"✗ HormoneFetcher instantiation failed: {e}")
    
    try:
        from scripts.fetch_enzymes import EnzymeFetcher
        fetcher = EnzymeFetcher()
        print("✓ EnzymeFetcher instantiated successfully")
    except Exception as e:
        print(f"✗ EnzymeFetcher instantiation failed: {e}")
    
    try:
        from scripts.fetch_amino_acids import AminoAcidFetcher
        fetcher = AminoAcidFetcher()
        print("✓ AminoAcidFetcher instantiated successfully")
    except Exception as e:
        print(f"✗ AminoAcidFetcher instantiation failed: {e}")
    
    try:
        from scripts.fetch_cells import CellFetcher
        fetcher = CellFetcher()
        print("✓ CellFetcher instantiated successfully")
    except Exception as e:
        print(f"✗ CellFetcher instantiation failed: {e}")
    
    try:
        from scripts.fetch_foreign_amino_acids import ForeignAminoAcidFetcher
        fetcher = ForeignAminoAcidFetcher()
        print("✓ ForeignAminoAcidFetcher instantiated successfully")
    except Exception as e:
        print(f"✗ ForeignAminoAcidFetcher instantiation failed: {e}")


def test_agent():
    """Test the main BioSheetAgent class."""
    print("\nTesting BioSheetAgent...")
    
    try:
        from agent.main import BioSheetAgent
        agent = BioSheetAgent()
        print("✓ BioSheetAgent instantiated successfully")
        print(f"  Available entity types: {list(agent.entity_types.keys())}")
    except Exception as e:
        print(f"✗ BioSheetAgent instantiation failed: {e}")


def test_directory_structure():
    """Test that the directory structure is correct."""
    print("\nTesting directory structure...")
    
    required_dirs = ['scripts', 'utils', 'data', 'agent', 'notebooks']
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✓ {dir_name}/ directory exists")
        else:
            print(f"✗ {dir_name}/ directory missing")
    
    required_files = [
        'requirements.txt',
        'README.md',
        'scripts/fetch_hormones.py',
        'scripts/fetch_enzymes.py',
        'scripts/fetch_amino_acids.py',
        'scripts/fetch_cells.py',
        'scripts/fetch_foreign_amino_acids.py',
        'utils/uniprot_api.py',
        'utils/pubmed_scraper.py',
        'utils/kegg_api.py',
        'agent/main.py',
        'notebooks/exploration.ipynb'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} missing")


def main():
    """Run all tests."""
    print("🧬 BioSheetAgent Setup Test")
    print("=" * 40)
    
    # Test directory structure
    test_directory_structure()
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please check your installation.")
        return
    
    # Test API connections
    test_api_connections()
    
    # Test fetcher classes
    test_fetcher_classes()
    
    # Test main agent
    test_agent()
    
    print("\n" + "=" * 40)
    print("✅ Setup test completed!")
    print("\nTo run BioSheetAgent:")
    print("1. CLI: python agent/main.py fetch --entity-type hormones")
    print("2. Streamlit: streamlit run agent/main.py")
    print("3. Individual scripts: python scripts/fetch_hormones.py")


if __name__ == "__main__":
    main() 