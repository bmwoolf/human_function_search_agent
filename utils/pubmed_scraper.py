"""
PubMed API utility for fetching scientific literature information.
"""

import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
import time
from urllib.parse import quote


class PubMedScraper:
    """PubMed API client for fetching scientific literature data."""
    
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BioSheetAgent/1.0 (https://github.com/your-repo)'
        })
        self.api_key = None  # Optional NCBI API key for higher rate limits
    
    def set_api_key(self, api_key: str):
        """Set NCBI API key for higher rate limits."""
        self.api_key = api_key
    
    def search_publications(self, query: str, max_results: int = 100) -> List[Dict]:
        """
        Search PubMed for publications.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of publication dictionaries
        """
        # First, search for IDs
        search_url = f"{self.base_url}/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json'
        }
        
        if self.api_key:
            params['api_key'] = self.api_key
        
        try:
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            id_list = data.get('esearchresult', {}).get('idlist', [])
            
            if not id_list:
                return []
            
            # Then fetch details for each ID
            return self._fetch_publication_details(id_list)
            
        except requests.RequestException as e:
            print(f"Error searching PubMed: {e}")
            return []
    
    def _fetch_publication_details(self, pmid_list: List[str]) -> List[Dict]:
        """Fetch detailed information for a list of PMIDs."""
        if not pmid_list:
            return []
        
        # Join PMIDs with commas
        pmid_string = ','.join(pmid_list)
        
        fetch_url = f"{self.base_url}/efetch.fcgi"
        params = {
            'db': 'pubmed',
            'id': pmid_string,
            'retmode': 'xml'
        }
        
        if self.api_key:
            params['api_key'] = self.api_key
        
        try:
            response = self.session.get(fetch_url, params=params)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            publications = []
            
            for pubmed_article in root.findall('.//PubmedArticle'):
                publication = self._parse_publication_xml(pubmed_article)
                if publication:
                    publications.append(publication)
            
            return publications
            
        except (requests.RequestException, ET.ParseError) as e:
            print(f"Error fetching publication details: {e}")
            return []
    
    def _parse_publication_xml(self, pubmed_article) -> Optional[Dict]:
        """Parse a single PubMed article XML element."""
        try:
            # Extract basic information
            pmid_elem = pubmed_article.find('.//PMID')
            pmid = pmid_elem.text if pmid_elem is not None else ''
            
            # Extract title
            title_elem = pubmed_article.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else ''
            
            # Extract abstract
            abstract_elem = pubmed_article.find('.//Abstract/AbstractText')
            abstract = abstract_elem.text if abstract_elem is not None else ''
            
            # Extract authors
            authors = []
            author_list = pubmed_article.find('.//AuthorList')
            if author_list is not None:
                for author in author_list.findall('Author'):
                    last_name = author.find('LastName')
                    first_name = author.find('ForeName')
                    if last_name is not None and first_name is not None:
                        authors.append(f"{first_name.text} {last_name.text}")
            
            # Extract journal information
            journal_elem = pubmed_article.find('.//Journal/Title')
            journal = journal_elem.text if journal_elem is not None else ''
            
            # Extract publication date
            pub_date_elem = pubmed_article.find('.//PubDate')
            pub_date = ''
            if pub_date_elem is not None:
                year_elem = pub_date_elem.find('Year')
                month_elem = pub_date_elem.find('Month')
                if year_elem is not None:
                    pub_date = year_elem.text
                    if month_elem is not None:
                        pub_date = f"{month_elem.text} {pub_date}"
            
            # Extract keywords
            keywords = []
            keyword_list = pubmed_article.find('.//KeywordList')
            if keyword_list is not None:
                for keyword in keyword_list.findall('Keyword'):
                    if keyword.text:
                        keywords.append(keyword.text)
            
            # Extract MeSH terms
            mesh_terms = []
            mesh_heading_list = pubmed_article.find('.//MeshHeadingList')
            if mesh_heading_list is not None:
                for mesh_heading in mesh_heading_list.findall('MeshHeading'):
                    descriptor = mesh_heading.find('DescriptorName')
                    if descriptor is not None and descriptor.text:
                        mesh_terms.append(descriptor.text)
            
            return {
                'pmid': pmid,
                'title': title,
                'abstract': abstract,
                'authors': authors,
                'journal': journal,
                'publication_date': pub_date,
                'keywords': keywords,
                'mesh_terms': mesh_terms
            }
            
        except Exception as e:
            print(f"Error parsing publication XML: {e}")
            return None
    
    def get_publication_by_pmid(self, pmid: str) -> Optional[Dict]:
        """
        Get a single publication by PMID.
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Publication dictionary or None if not found
        """
        publications = self._fetch_publication_details([pmid])
        return publications[0] if publications else None
    
    def search_by_author(self, author_name: str, max_results: int = 50) -> List[Dict]:
        """
        Search publications by author name.
        
        Args:
            author_name: Author name (e.g., "Smith J")
            max_results: Maximum number of results
            
        Returns:
            List of publication dictionaries
        """
        query = f"{author_name}[Author]"
        return self.search_publications(query, max_results)
    
    def search_by_journal(self, journal_name: str, max_results: int = 50) -> List[Dict]:
        """
        Search publications by journal name.
        
        Args:
            journal_name: Journal name
            max_results: Maximum number of results
            
        Returns:
            List of publication dictionaries
        """
        query = f"{journal_name}[Journal]"
        return self.search_publications(query, max_results)
    
    def search_recent_publications(self, query: str, days: int = 30, max_results: int = 50) -> List[Dict]:
        """
        Search for recent publications.
        
        Args:
            query: Search query
            days: Number of days to look back
            max_results: Maximum number of results
            
        Returns:
            List of publication dictionaries
        """
        # Add date filter to query
        date_query = f"{query} AND {days}d[dp]"
        return self.search_publications(date_query, max_results)
    
    def get_citations(self, pmid: str) -> List[Dict]:
        """
        Get publications that cite a given PMID.
        
        Args:
            pmid: PubMed ID
            
        Returns:
            List of citing publication dictionaries
        """
        query = f"{pmid}[uid]"
        return self.search_publications(query, 100)


# Example usage
if __name__ == "__main__":
    scraper = PubMedScraper()
    
    # Search for insulin-related publications
    publications = scraper.search_publications("insulin diabetes", 5)
    print(f"Found {len(publications)} publications")
    
    for pub in publications:
        print(f"PMID: {pub['pmid']}")
        print(f"Title: {pub['title']}")
        print(f"Authors: {', '.join(pub['authors'][:3])}")
        print("-" * 50) 