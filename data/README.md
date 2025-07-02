# Data Directory

This directory contains the generated biological data files from BioSheetAgent.

## Expected Files

After running the data collection scripts, you should see the following files:

### CSV Files
- `hormones.csv` - Hormone data with function, location, and related information
- `enzymes.csv` - Enzyme data with catalytic functions and pathways
- `amino_acids.csv` - Standard 20 amino acids with metabolic information
- `human_cells.csv` - Human cell types with tissue locations and functions
- `foreign_amino_acids.csv` - Non-standard amino acids and derivatives

### Excel Files
- `hormones.xlsx` - Same data as CSV but in Excel format
- `enzymes.xlsx` - Same data as CSV but in Excel format
- `amino_acids.xlsx` - Same data as CSV but in Excel format
- `human_cells.xlsx` - Same data as CSV but in Excel format
- `foreign_amino_acids.xlsx` - Same data as CSV but in Excel format

### Report Files
- `*_report.md` - Summary reports for each data collection run

## Data Schema

Each file contains the following columns:

| Column | Description |
|--------|-------------|
| Name | Primary identifier of the biological entity |
| Type | Entity category (hormone, enzyme, amino_acid, cell, foreign_amino_acid) |
| Function | Primary biological function |
| Location | Organ/system location |
| Related molecules | Associated genes, proteins, hormones, etc. |
| Related systems | Biological systems involved |
| Diseases/dysfunctions | Associated conditions |
| Source links | UniProt/PubMed/KEGG references |
| Synonyms | Alternative names |

## Usage

To generate these files, run one of the following commands:

```bash
# CLI interface
python agent/main.py fetch --entity-type hormones --output-format both

# Streamlit interface
streamlit run agent/main.py

# Individual scripts
python scripts/fetch_hormones.py
python scripts/fetch_enzymes.py
python scripts/fetch_amino_acids.py
python scripts/fetch_cells.py
python scripts/fetch_foreign_amino_acids.py
```

## Data Sources

The data is collected from:
- **UniProt**: Protein sequence and annotation data
- **PubMed**: Scientific literature and research papers  
- **KEGG**: Pathway and molecular interaction databases 