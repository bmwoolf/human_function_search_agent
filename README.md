# Human Function Search Agent (Atlas)

A tool that automates the creation of structured biological metadata spreadsheets for 5 domains: Human Cells, Enzymes, Hormones, Endogenous Amino Acids, and Foreign Amino Acids.

## Goals

- Use UniProt, PubMed, and KEGG APIs to extract structured metadata
- Normalize into consistent CSV schemas
- Output downloadable .csv and .xlsx files
- Package as a CLI or Streamlit-based agent for user interaction


## Data Schema

Each entity (cell, enzyme, hormone, amino acid) will be stored with the following schema:

| Column | Description | Example |
|--------|-------------|---------|
| Name | Primary identifier | "Insulin", "Glucose-6-phosphate dehydrogenase" |
| Type | Entity category | "hormone", "enzyme", "cell", "amino_acid" |
| Function | Primary biological function | "Regulates blood glucose levels" |
| Location | Organ/system location | "Pancreas", "Liver", "Bloodstream" |
| Related molecules | Associated genes, proteins, etc. | "INS gene, GLUT4 transporter" |
| Related systems | Biological systems involved | "Endocrine, Digestive" |
| Diseases/dysfunctions | Associated conditions | "Diabetes mellitus, Insulin resistance" |
| Source links | UniProt/PubMed/KEGG references | "P01308, PMID:12345678, KEGG:C00031" |
| Synonyms | Alternative names | "Human insulin, Regular insulin" |

## Installation

1. Clone the repository:
```bash
git clone https://github.com/bmwoolf/human_function_search_agent.git
cd human_function_search_agent
```

2. **Create and activate a virtual environment:**
```bash
python3 -m venv env
source env/bin/activate  # On Windows use: env\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Data Sources

- **UniProt**: Protein sequence and annotation data
- **PubMed**: Scientific literature and research papers
- **KEGG**: Pathway and molecular interaction databases

## Usage

### Command Line Interface
```bash
python agent/main.py --entity-type hormone --output-format csv
```

### Streamlit Interface
```bash
streamlit run agent/main.py
```

## Scripts

- `fetch_amino_acids.py`: Extract endogenous amino acid data
- `fetch_enzymes.py`: Extract enzyme information
- `fetch_cells.py`: Extract human cell data
- `fetch_hormones.py`: Extract hormone information
- `fetch_foreign_amino_acids.py`: Extract foreign amino acid data

## Development

### Adding New Entity Types
1. Create a new fetch script in `scripts/`
2. Update the schema in `utils/` if needed
3. Add corresponding data file in `data/`

### API Integration
- UniProt API: `utils/uniprot_api.py`
- PubMed API: `utils/pubmed_scraper.py`
- KEGG API: `utils/kegg_api.py`

## License
MIT

## Project Structure

```
human_function_search_agent/
├── README.md
├── requirements.txt
├── notebooks/
│   └── exploration.ipynb
├── scripts/
│   ├── fetch_amino_acids.py
│   ├── fetch_enzymes.py
│   ├── fetch_cells.py
│   ├── fetch_hormones.py
│   └── fetch_foreign_amino_acids.py
├── data/
│   ├── amino_acids.csv
│   ├── hormones.csv
│   ├── enzymes.csv
│   ├── human_cells.csv
│   └── foreign_amino_acids.csv
├── utils/
│   ├── uniprot_api.py
│   ├── pubmed_scraper.py
│   └── kegg_api.py
└── agent/
    └── main.py
```