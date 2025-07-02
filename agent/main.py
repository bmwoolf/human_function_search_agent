"""
BioSheetAgent - Main application for biological data collection and spreadsheet generation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import click
import streamlit as st
from typing import List, Dict, Optional
import time
from datetime import datetime

from scripts.fetch_hormones import HormoneFetcher
from scripts.fetch_enzymes import EnzymeFetcher
from scripts.fetch_amino_acids import AminoAcidFetcher
from scripts.fetch_cells import CellFetcher
from scripts.fetch_foreign_amino_acids import ForeignAminoAcidFetcher


class BioSheetAgent:
    """Main agent for biological data collection and spreadsheet generation."""
    
    def __init__(self):
        self.fetchers = {
            'hormones': HormoneFetcher(),
            'enzymes': EnzymeFetcher(),
            'amino_acids': AminoAcidFetcher(),
            'cells': CellFetcher(),
            'foreign_amino_acids': ForeignAminoAcidFetcher()
        }
        
        self.entity_types = {
            'hormones': 'Hormones',
            'enzymes': 'Enzymes', 
            'amino_acids': 'Endogenous Amino Acids',
            'cells': 'Human Cells',
            'foreign_amino_acids': 'Foreign Amino Acids'
        }
    
    def fetch_entity_data(self, entity_type: str) -> pd.DataFrame:
        """
        Fetch data for a specific entity type.
        
        Args:
            entity_type: Type of entity to fetch
            
        Returns:
            DataFrame containing entity data
        """
        if entity_type not in self.fetchers:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        fetcher = self.fetchers[entity_type]
        
        if entity_type == 'hormones':
            return fetcher.fetch_all_hormones()
        elif entity_type == 'enzymes':
            return fetcher.fetch_all_enzymes()
        elif entity_type == 'amino_acids':
            return fetcher.fetch_all_amino_acids()
        elif entity_type == 'cells':
            return fetcher.fetch_all_cells()
        elif entity_type == 'foreign_amino_acids':
            return fetcher.fetch_all_foreign_aas()
    
    def save_data(self, df: pd.DataFrame, entity_type: str, format: str = 'csv'):
        """
        Save data to file.
        
        Args:
            df: DataFrame to save
            entity_type: Type of entity
            format: Output format ('csv' or 'xlsx')
        """
        if format == 'csv':
            filename = f'data/{entity_type}.csv'
            df.to_csv(filename, index=False)
            print(f"Data saved to {filename}")
        elif format == 'xlsx':
            filename = f'data/{entity_type}.xlsx'
            df.to_excel(filename, index=False)
            print(f"Data saved to {filename}")
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def generate_summary_report(self, entity_type: str, df: pd.DataFrame) -> str:
        """
        Generate a summary report for the collected data.
        
        Args:
            entity_type: Type of entity
            df: DataFrame containing the data
            
        Returns:
            Summary report string
        """
        report = f"""
# BioSheetAgent Data Collection Report

## Entity Type: {self.entity_types.get(entity_type, entity_type)}
## Collection Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
## Total Records: {len(df)}

## Data Summary:
- **Name**: {len(df['Name'].dropna())} records with names
- **Function**: {len(df['Function'].dropna())} records with function data
- **Location**: {len(df['Location'].dropna())} records with location data
- **Related molecules**: {len(df['Related molecules'].dropna())} records with molecule data
- **Related systems**: {len(df['Related systems'].dropna())} records with system data
- **Diseases/dysfunctions**: {len(df['Diseases/dysfunctions'].dropna())} records with disease data
- **Source links**: {len(df['Source links'].dropna())} records with source data
- **Synonyms**: {len(df['Synonyms'].dropna())} records with synonym data

## Sample Data:
{df.head().to_string()}

## Data Quality:
- Complete records: {len(df.dropna())} / {len(df)} ({len(df.dropna())/len(df)*100:.1f}%)
- Records with function data: {len(df['Function'].dropna())} / {len(df)} ({len(df['Function'].dropna())/len(df)*100:.1f}%)
- Records with location data: {len(df['Location'].dropna())} / {len(df)} ({len(df['Location'].dropna())/len(df)*100:.1f}%)

## Files Generated:
- `data/{entity_type}.csv`
- `data/{entity_type}.xlsx`
        """
        return report


@click.group()
def cli():
    """BioSheetAgent - Biological data collection and spreadsheet generation."""
    pass


@cli.command()
@click.option('--entity-type', '-e', 
              type=click.Choice(['hormones', 'enzymes', 'amino_acids', 'cells', 'foreign_amino_acids']),
              required=True, help='Type of entity to fetch')
@click.option('--output-format', '-f', 
              type=click.Choice(['csv', 'xlsx', 'both']), 
              default='both', help='Output format')
@click.option('--generate-report', '-r', is_flag=True, help='Generate summary report')
def fetch(entity_type, output_format, generate_report):
    """Fetch biological data for specified entity type."""
    agent = BioSheetAgent()
    
    click.echo(f"Starting data collection for {entity_type}...")
    
    try:
        df = agent.fetch_entity_data(entity_type)
        
        if df.empty:
            click.echo("No data collected.")
            return
        
        click.echo(f"Collected {len(df)} records for {entity_type}")
        
        # Save data
        if output_format in ['csv', 'both']:
            agent.save_data(df, entity_type, 'csv')
        
        if output_format in ['xlsx', 'both']:
            agent.save_data(df, entity_type, 'xlsx')
        
        # Generate report
        if generate_report:
            report = agent.generate_summary_report(entity_type, df)
            report_filename = f'data/{entity_type}_report.md'
            with open(report_filename, 'w') as f:
                f.write(report)
            click.echo(f"Report saved to {report_filename}")
        
        # Display summary
        click.echo("\nData Summary:")
        click.echo(df[['Name', 'Function', 'Location']].head().to_string())
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.option('--all', is_flag=True, help='Fetch all entity types')
@click.option('--output-format', '-f', 
              type=click.Choice(['csv', 'xlsx', 'both']), 
              default='both', help='Output format')
def fetch_all(all, output_format):
    """Fetch data for all entity types."""
    if not all:
        click.echo("Use --all flag to fetch all entity types")
        return
    
    agent = BioSheetAgent()
    
    for entity_type in agent.entity_types.keys():
        click.echo(f"\nFetching {entity_type}...")
        try:
            df = agent.fetch_entity_data(entity_type)
            
            if not df.empty:
                if output_format in ['csv', 'both']:
                    agent.save_data(df, entity_type, 'csv')
                
                if output_format in ['xlsx', 'both']:
                    agent.save_data(df, entity_type, 'xlsx')
                
                click.echo(f"✓ Collected {len(df)} records for {entity_type}")
            else:
                click.echo(f"✗ No data collected for {entity_type}")
                
        except Exception as e:
            click.echo(f"✗ Error fetching {entity_type}: {e}")


def streamlit_app():
    """Streamlit web application for BioSheetAgent."""
    st.set_page_config(
        page_title="BioSheetAgent",
        page_icon="🧬",
        layout="wide"
    )
    
    st.title("🧬 BioSheetAgent")
    st.markdown("Biological data collection and spreadsheet generation tool")
    
    # Sidebar
    st.sidebar.header("Configuration")
    
    entity_type = st.sidebar.selectbox(
        "Select Entity Type",
        list(BioSheetAgent().entity_types.keys()),
        format_func=lambda x: BioSheetAgent().entity_types[x]
    )
    
    output_format = st.sidebar.selectbox(
        "Output Format",
        ["CSV", "Excel", "Both"]
    )
    
    generate_report = st.sidebar.checkbox("Generate Summary Report")
    
    # Main content
    st.header(f"Data Collection: {BioSheetAgent().entity_types[entity_type]}")
    
    if st.button("🚀 Start Data Collection"):
        agent = BioSheetAgent()
        
        with st.spinner(f"Collecting {entity_type} data..."):
            try:
                df = agent.fetch_entity_data(entity_type)
                
                if not df.empty:
                    st.success(f"✅ Collected {len(df)} records!")
                    
                    # Save data
                    if output_format in ["CSV", "Both"]:
                        agent.save_data(df, entity_type, 'csv')
                        st.info(f"📄 CSV saved to data/{entity_type}.csv")
                    
                    if output_format in ["Excel", "Both"]:
                        agent.save_data(df, entity_type, 'xlsx')
                        st.info(f"📊 Excel saved to data/{entity_type}.xlsx")
                    
                    # Display data
                    st.subheader("Collected Data")
                    st.dataframe(df)
                    
                    # Generate report
                    if generate_report:
                        report = agent.generate_summary_report(entity_type, df)
                        st.subheader("Summary Report")
                        st.markdown(report)
                        
                        # Save report
                        report_filename = f'data/{entity_type}_report.md'
                        with open(report_filename, 'w') as f:
                            f.write(report)
                        st.info(f"📋 Report saved to {report_filename}")
                    
                    # Statistics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Records", len(df))
                    with col2:
                        st.metric("With Function", len(df['Function'].dropna()))
                    with col3:
                        st.metric("With Location", len(df['Location'].dropna()))
                    with col4:
                        st.metric("Complete Records", len(df.dropna()))
                        
                else:
                    st.error("No data collected.")
                    
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Instructions
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### Instructions:
    1. Select the entity type to collect
    2. Choose output format
    3. Click "Start Data Collection"
    4. Wait for data collection to complete
    5. Download generated files from the data/ directory
    """)


if __name__ == "__main__":
    import sys
    import os

    # Robust Streamlit detection
    is_streamlit = (
        "streamlit" in sys.modules
        or any("streamlit" in arg for arg in sys.argv)
        or os.environ.get("STREAMLIT_RUN_CONTEXT") is not None
    )

    if is_streamlit:
        streamlit_app()
    else:
        cli() 