![Banner](assets/github_banner.png)

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

## Future Enhancements 

Honestly, I started this project with extreme skepticism- agents are super hypey and over-inflated in the short-term, but I think this project has the potential to evolve into a comprehensive scientific database search service. Searching across these hundreds of scientific databases totally sucks. Here are exciting possibilities for future development:

### **Expanded Database Integration**
With 100+ scientific databases available, we could integrate:

#### **Molecular & Protein Databases**
- **PDB** (Protein Data Bank) - 3D protein structures
- **Pfam** - Protein families and domains
- **InterPro** - Protein signatures and families
- **STRING** - Protein-protein interactions
- **IntAct** - Molecular interaction data
- **BioGRID** - Genetic and protein interactions

#### **Chemical & Metabolite Databases**
- **ChEBI** - Chemical entities of biological interest
- **PubChem** - Chemical compound database
- **HMDB** (Human Metabolome Database) - Metabolite data
- **DrugBank** - Drug and drug target information
- **BindingDB** - Protein-ligand binding data
- **ChemSpider** - Chemical structure database

#### **Genomic & Transcriptomic Databases**
- **Ensembl** - Genome annotation
- **NCBI Gene** - Gene information
- **GTEx** - Gene expression data
- **ENCODE** - Functional genomics
- **UCSC Genome Browser** - Genome visualization
- **GEO** (Gene Expression Omnibus) - Expression data

#### **Disease & Clinical Databases**
- **OMIM** - Human genes and genetic disorders
- **ClinVar** - Clinical variant interpretations
- **DisGeNET** - Disease-gene associations
- **Orphanet** - Rare diseases
- **GWAS Catalog** - Genome-wide association studies
- **PharmGKB** - Pharmacogenomics

#### **Pathway & Systems Biology**
- **Reactome** (already integrated) - Biological pathways
- **WikiPathways** - Community-curated pathways
- **KEGG** (license required) - Metabolic pathways
- **BioCyc** - Metabolic pathway databases
- **Pathway Commons** - Pathway integration
- **SMPDB** - Small molecule pathways

### **Advanced Search & Analytics**
- **Semantic search** using embeddings
- **Cross-database queries** (IE "Find all proteins involved in diabetes that have 3D structures")
- **Similarity search** (find similar molecules, proteins, pathways)
- **Network analysis** (protein interaction networks, metabolic networks)
- **Machine learning** for data prediction and classification
- **Natural language queries** ("What proteins are involved in insulin signaling?")

### **Data Visualization & Exploration**
- **Interactive network graphs** for protein interactions
- **3D molecular viewers** for protein structures
- **Pathway diagrams** with interactive elements
- **Heatmaps** for expression data
- **Choropleth maps** for disease prevalence
- **Timeline visualizations** for research trends

### **Web Service & API Development**
- **RESTful API** for programmatic access
- **GraphQL interface** for flexible queries
- **Real-time search** across all databases
- **Federated search** capabilities
- **API rate limiting** and authentication
- **Webhook notifications** for data updates

### **AI-Powered Features**
- **Automated literature mining** and summarization
- **Drug repurposing** suggestions
- **Disease mechanism** hypothesis generation
- **Personalized medicine** insights
- **Research trend** analysis and prediction
- **Automated data curation** and quality control

### **Platform Enhancements**
- **Multi-language support** (Python, R, JavaScript APIs)
- **Cloud deployment** (AWS, Google Cloud, Azure)
- **Containerization** (Docker, Kubernetes)
- **Database optimization** (PostgreSQL, MongoDB, Neo4j)
- **Caching layers** (Redis, Memcached)
- **Load balancing** and auto-scaling

### **User Interface Improvements**
- **Modern web dashboard** with React/Vue.js
- **Mobile-responsive** design
- **Progressive Web App** (PWA) capabilities
- **Dark/light theme** support
- **Customizable dashboards** for different user types
- **Collaborative features** (sharing, commenting, annotations)

### **Enterprise Features**
- **User authentication** and role-based access
- **Data privacy** and GDPR compliance
- **Audit logging** and compliance reporting
- **API key management** and usage analytics
- **White-label solutions** for institutions
- **Custom database** integration services

### **Community & Ecosystem**
- **Plugin system** for third-party integrations
- **Open API marketplace** for database providers
- **Community-contributed** data sources
- **Educational resources** and tutorials
- **Research collaboration** tools
- **Open source** contributions and forks

### **Scalability & Performance**
- **Distributed computing** for large-scale data processing
- **Streaming data** pipelines for real-time updates
- **Edge computing** for low-latency access
- **CDN integration** for global performance
- **Database sharding** and partitioning
- **Microservices architecture** for modular scaling

## License
MIT

```