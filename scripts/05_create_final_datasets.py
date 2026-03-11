import pandas as pd
import json
from pathlib import Path

def create_metadata():
    """Create metadata about the dataset."""
    
    # Load all datasets
    drugs = pd.read_csv('data/processed/drug_master.csv')
    interactions = pd.read_csv('data/processed/interactions.csv')
    drug_info = pd.read_csv('data/processed/drug_info.csv')
    side_effects = pd.read_csv('data/processed/side_effects.csv')
    
    metadata = {
        'generated_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_drugs': len(drugs),
        'total_interactions': len(interactions),
        'total_side_effects': len(side_effects),
        'drugs_with_info': len(drug_info),
        'severity_breakdown': {
            'high': int((interactions['severity_clean'] == 'High').sum()),
            'medium': int((interactions['severity_clean'] == 'Medium').sum()),
            'low': int((interactions['severity_clean'] == 'Low').sum())
        },
        'categories': drugs['category'].value_counts().to_dict(),
        'data_sources': [
            'RxNorm Interaction API (NIH)',
            'OpenFDA Drug Labels API',
            'ClinCalc Top Drugs Database',
            'Educational pharmacology references'
        ],
        'version': '1.0.0'
    }
    
    return metadata

def create_network_data():
    """
    Create optimized network data structure for visualization.
    """
    
    interactions = pd.read_csv('data/processed/interactions.csv')
    drugs = pd.read_csv('data/processed/drug_master.csv')
    
    # Create nodes (all drugs that have interactions)
    drugs_in_network = set(interactions['drug_a_name']).union(set(interactions['drug_b_name']))
    
    nodes = []
    for drug_name in drugs_in_network:
        drug_info = drugs[drugs['generic_name'] == drug_name]
        if len(drug_info) > 0:
            nodes.append({
                'id': drug_name,
                'label': drug_name,
                'group': drug_info.iloc[0]['category'],
                'rxcui': str(drug_info.iloc[0]['rxcui'])
            })
    
    # Create edges (interactions)
    edges = []
    for idx, row in interactions.iterrows():
        edges.append({
            'from': row['drug_a_name'],
            'to': row['drug_b_name'],
            'severity': row['severity_clean'],
            'color': row['severity_color'],
            'title': f"{row['drug_a_name']} + {row['drug_b_name']}: {row['severity_clean']}",
            'description': row['description'][:200] + '...' if len(row['description']) > 200 else row['description']
        })
    
    network_data = {
        'nodes': nodes,
        'edges': edges
    }
    
    return network_data

def create_search_index():
    """
    Create optimized search index for drug name matching (Patient Analyzer).
    Includes common misspellings and variations.
    """
    
    drugs = pd.read_csv('data/processed/drug_master.csv')
    
    search_index = []
    
    for idx, row in drugs.iterrows():
        generic = row['generic_name'].lower()
        brands = row['brand_names'].lower() if pd.notna(row['brand_names']) else ''
        
        # Add all variations
        variations = [generic]
        
        # Add brand names
        if brands:
            variations.extend([b.strip() for b in brands.split(',')])
        
        # Add common variations
        variations.append(generic.replace('-', ' '))
        variations.append(generic.replace(' ', ''))
        
        search_index.append({
            'rxcui': str(row['rxcui']),
            'generic_name': row['generic_name'],
            'search_terms': variations,
            'category': row['category']
        })
    
    return search_index

def create_quick_lookup():
    """
    Create quick lookup dictionaries for app performance.
    """
    
    drugs = pd.read_csv('data/processed/drug_master.csv')
    interactions = pd.read_csv('data/processed/interactions.csv')
    side_effects = pd.read_csv('data/processed/side_effects.csv')
    
    # Drug RxCUI to name mapping
    rxcui_to_name = dict(zip(drugs['rxcui'].astype(str), drugs['generic_name']))
    name_to_rxcui = dict(zip(drugs['generic_name'], drugs['rxcui'].astype(str)))
    
    # Interactions by drug
    interactions_by_drug = {}
    for drug_name in drugs['generic_name']:
        drug_interactions = interactions[
            (interactions['drug_a_name'] == drug_name) | 
            (interactions['drug_b_name'] == drug_name)
        ]
        interactions_by_drug[drug_name] = len(drug_interactions)
    
    # Side effects by drug
    side_effects_by_drug = {}
    for drug_name in drugs['generic_name']:
        drug_effects = side_effects[side_effects['drug_name'] == drug_name]
        side_effects_by_drug[drug_name] = {
            'common': drug_effects[drug_effects['severity'] == 'Common']['side_effect'].tolist(),
            'serious': drug_effects[drug_effects['severity'] == 'Serious']['side_effect'].tolist()
        }
    
    lookup = {
        'rxcui_to_name': rxcui_to_name,
        'name_to_rxcui': name_to_rxcui,
        'interactions_count': interactions_by_drug,
        'side_effects': side_effects_by_drug
    }
    
    return lookup

def create_app_config():
    """
    Create configuration file for the Shiny app.
    """
    
    config = {
        'app_title': 'RxCheck: Drug Interaction Checker',
        'app_version': '1.0.0',
        'data_files': {
            'drugs': 'data/processed/drug_master.csv',
            'interactions': 'data/processed/interactions.csv',
            'drug_info': 'data/processed/drug_info.csv',
            'side_effects': 'data/processed/side_effects.csv',
            'network': 'data/processed/network_data.json',
            'search_index': 'data/processed/search_index.json',
            'lookup': 'data/processed/quick_lookup.json',
            'metadata': 'data/processed/metadata.json'
        },
        'severity_colors': {
            'High': '#E74C3C',
            'Medium': '#F39C12',
            'Low': '#27AE60'
        },
        'ui_settings': {
            'max_drugs_select': 10,
            'max_network_depth': 3,
            'default_network_depth': 2,
            'max_csv_upload_mb': 10
        }
    }
    
    return config

def main():
    print("Creating final optimized datasets...")
    print()
    
    # Create metadata
    print("Creating metadata...")
    metadata = create_metadata()
    with open('data/processed/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    print("data/processed/metadata.json")
    
    # Create network data
    print("\nCreating network visualization data...")
    network_data = create_network_data()
    with open('data/processed/network_data.json', 'w') as f:
        json.dump(network_data, f, indent=2)
    print(f"data/processed/network_data.json")
    print(f"Nodes: {len(network_data['nodes'])}, Edges: {len(network_data['edges'])}")
    
    # Create search index
    print("\nCreating search index...")
    search_index = create_search_index()
    with open('data/processed/search_index.json', 'w') as f:
        json.dump(search_index, f, indent=2)
    print(f"data/processed/search_index.json")
    print(f"Entries: {len(search_index)}")
    
    # Create quick lookup
    print("\nCreating quick lookup tables...")
    lookup = create_quick_lookup()
    with open('data/processed/quick_lookup.json', 'w') as f:
        json.dump(lookup, f, indent=2)
    print("data/processed/quick_lookup.json")
    
    # Create app config
    print("\nCreating app configuration...")
    config = create_app_config()
    with open('data/processed/app_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    print("data/processed/app_config.json")
    
    # Create data summary report
    print("\nCreating data summary report...")
    
    summary_report = f"""
RxCheck Data Summary Report
Generated: {metadata['generated_date']}
{'=' * 60}

DATASET STATISTICS:
  Total Drugs: {metadata['total_drugs']}
  Total Interactions: {metadata['total_interactions']}
  Total Side Effects: {metadata['total_side_effects']}
  
INTERACTION SEVERITY:
  High Risk: {metadata['severity_breakdown']['high']}
  Medium Risk: {metadata['severity_breakdown']['medium']}
  Low Risk: {metadata['severity_breakdown']['low']}

DRUG CATEGORIES:
"""
    
    for category, count in sorted(metadata['categories'].items(), key=lambda x: x[1], reverse=True):
        summary_report += f"  {category}: {count}\n"
    
    summary_report += f"""
DATA FILES CREATED:
  drug_master.csv ({metadata['total_drugs']} drugs)
  interactions.csv ({metadata['total_interactions']} interactions)
  drug_info.csv ({metadata['drugs_with_info']} profiles)
  side_effects.csv ({metadata['total_side_effects']} effects)
  network_data.json (visualization data)
  search_index.json (fuzzy matching)
  quick_lookup.json (performance optimization)
  metadata.json (dataset info)
  app_config.json (app settings)

DATA SOURCES:
"""
    
    for source in metadata['data_sources']:
        summary_report += f"  • {source}\n"
    
    summary_report += f"""
STATUS: All datasets ready for Shiny app!

NEXT STEPS:
  1. Run the Shiny app: python app/app.py
  2. Test all three tabs
  3. Upload sample CSV to test Patient Analyzer
  
REMINDER: This is an educational tool only.
    Not for clinical decision-making.
    
{'=' * 60}
"""
    
    with open('data/processed/DATA_SUMMARY.txt', 'w') as f:
        f.write(summary_report)
    
    print("data/processed/DATA_SUMMARY.txt")
    
    # Print summary to console
    print("\n" + "="*60)
    print(summary_report)
    
    # Calculate total file size
    data_dir = Path('data/processed')
    total_size = sum(f.stat().st_size for f in data_dir.glob('*') if f.is_file())
    total_size_mb = total_size / (1024 * 1024)
    
    print(f"\nTOTAL DATA SIZE: {total_size_mb:.2f} MB")
    
    if total_size_mb < 100:
        print("Within 100MB requirement for project submission!")
    else:
        print("Exceeds 100MB - may need to reduce data")
    
    print("\nDATA PIPELINE COMPLETE!")
    print("Ready to build Shiny app!")

if __name__ == '__main__':
    main()