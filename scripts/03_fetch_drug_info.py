# import requests
# import pandas as pd
# import json
# import time
# from tqdm import tqdm

# # Load drug master
# drugs_df = pd.read_csv('data/processed/drug_master.csv')

# # OpenFDA API base
# OPENFDA_BASE = "https://api.fda.gov/drug/label.json"

# def fetch_drug_label(generic_name, rxcui):
#     """
#     Fetch drug label from OpenFDA.
#     """
#     # Try searching by generic name
#     query = f"openfda.generic_name:{generic_name.lower()}"
#     params = {
#         'search': query,
#         'limit': 1
#     }
    
#     try:
#         response = requests.get(OPENFDA_BASE, params=params, timeout=10)
        
#         if response.status_code == 200:
#             data = response.json()
            
#             if 'results' not in data or len(data['results']) == 0:
#                 return None
            
#             result = data['results'][0]
            
#             # Extract relevant sections
#             label_info = {
#                 'rxcui': rxcui,
#                 'generic_name': generic_name,
#                 'indications': result.get('indications_and_usage', [''])[0] if 'indications_and_usage' in result else '',
#                 'warnings': result.get('warnings', [''])[0] if 'warnings' in result else '',
#                 'contraindications': result.get('contraindications', [''])[0] if 'contraindications' in result else '',
#                 'adverse_reactions': result.get('adverse_reactions', [''])[0] if 'adverse_reactions' in result else '',
#                 'dosage': result.get('dosage_and_administration', [''])[0] if 'dosage_and_administration' in result else '',
#             }
            
#             return label_info
#         else:
#             return None
            
#     except Exception as e:
#         print(f"Error for {generic_name}: {e}")
#         return None

# def main():
#     print("Fetching drug information from OpenFDA...")
#     print(f"Total drugs: {len(drugs_df)}")
#     print()
    
#     drug_info_list = []
    
#     for idx, row in tqdm(drugs_df.iterrows(), total=len(drugs_df), desc="Fetching"):
#         generic_name = row['generic_name']
#         rxcui = row['rxcui']
        
#         label_info = fetch_drug_label(generic_name, rxcui)
        
#         if label_info:
#             # Add category info from master
#             label_info['category'] = row['category']
#             label_info['brand_names'] = row['brand_names']
#             drug_info_list.append(label_info)
#         else:
#             # Create placeholder
#             drug_info_list.append({
#                 'rxcui': rxcui,
#                 'generic_name': generic_name,
#                 'category': row['category'],
#                 'brand_names': row['brand_names'],
#                 'indications': 'Information not available from FDA database.',
#                 'warnings': 'Information not available from FDA database.',
#                 'contraindications': 'Information not available from FDA database.',
#                 'adverse_reactions': 'Information not available from FDA database.',
#                 'dosage': 'Information not available from FDA database.',
#             })
        
#         # Be respectful to API
#         time.sleep(0.5)
    
#     # Convert to DataFrame
#     drug_info_df = pd.DataFrame(drug_info_list)
    
#     # Save
#     drug_info_df.to_csv('data/processed/drug_info.csv', index=False)
#     drug_info_df.to_json('data/processed/drug_info.json', orient='records', indent=2)
    
#     print(f"\nFetched information for {len(drug_info_df)} drugs")
#     print(f"Saved to:")
#     print(f"- data/processed/drug_info.csv")
#     print(f"- data/processed/drug_info.json")
    
#     # Statistics
#     has_info = (drug_info_df['indications'] != 'Information not available from FDA database.').sum()
#     print(f"\nStatistics:")
#     print(f"Drugs with FDA label data: {has_info}/{len(drug_info_df)}")

# if __name__ == '__main__':
#     main()

import pandas as pd
import requests
import json
from pathlib import Path
import time
from datetime import datetime

# def fetch_drug_info(drug_name, brand_names, rxcui):
#     """
#     Fetch FDA drug label information from OpenFDA API.
#     """
    
#     url = "https://api.fda.gov/drug/label.json"
    
#     # Build search terms - try brand names first
#     search_terms = []
    
#     # 1. Try brand names (most accurate)
#     if pd.notna(brand_names) and brand_names:
#         brand_list = [b.strip() for b in str(brand_names).split(',')]
#         for brand in brand_list[:3]:  # Try first 3 brands
#             if brand:  # Skip empty strings
#                 search_terms.append(f'openfda.brand_name:"{brand}"')
    
#     # 2. Try generic name
#     search_terms.append(f'openfda.generic_name:"{drug_name}"')
    
#     # Try each search term
#     for search_term in search_terms:
#         params = {
#             'search': search_term,
#             'limit': 1
#         }
        
#         try:
#             response = requests.get(url, params=params, timeout=10)
            
#             if response.status_code == 200:
#                 data = response.json()
                
#                 if 'results' in data and len(data['results']) > 0:
#                     result = data['results'][0]
                    
#                     # Validate result - check if drug name appears in content
#                     indications = extract_field(result, 'indications_and_usage').lower()
#                     description = extract_field(result, 'description').lower()
                    
#                     # Simple validation
#                     drug_name_lower = drug_name.lower()
#                     if drug_name_lower in indications or drug_name_lower in description:
#                         # Good match - extract information
#                         info = {
#                             'generic_name': drug_name,
#                             'rxcui': str(rxcui),
#                             'indications': extract_field(result, 'indications_and_usage'),
#                             'warnings': extract_field(result, 'boxed_warning'),  # Use boxed_warning
#                             'contraindications': extract_field(result, 'contraindications'),
#                             'adverse_reactions': extract_field(result, 'adverse_reactions'),
#                             'dosage': extract_field(result, 'dosage_and_administration'),
#                             'source': 'OpenFDA API',
#                             'search_term_used': search_term,
#                             'fda_application_number': get_nested(result, ['openfda', 'application_number'])
#                         }
                        
#                         print(f"Found for {drug_name} via: {search_term[:50]}...")
#                         return info
#                     else:
#                         # Name doesn't match - might be wrong product
#                         print(f"Skipped mismatch for {drug_name} via: {search_term[:50]}...")
#                         continue
                    
#             elif response.status_code == 404:
#                 # No results for this search term
#                 continue
#             else:
#                 print(f"HTTP {response.status_code} for {drug_name}")
#                 continue
                
#         except requests.exceptions.Timeout:
#             print(f"Timeout for {drug_name}")
#             continue
#         except requests.exceptions.RequestException as e:
#             print(f"Request error for {drug_name}: {str(e)[:50]}")
#             continue
#         except json.JSONDecodeError:
#             print(f"JSON decode error for {drug_name}")
#             continue
#         except Exception as e:
#             print(f"Unexpected error for {drug_name}: {str(e)[:50]}")
#             continue
    
#     # No data found for any search term
#     print(f"No FDA label found for {drug_name}")
#     return create_empty_info(drug_name, rxcui)

def fetch_drug_info(drug_name, brand_names, rxcui):
    """
    Fetch FDA drug label information from OpenFDA API.
    """
    
    url = "https://api.fda.gov/drug/label.json"
    
    # Build search terms - try brand names first
    search_terms = []
    
    # 1. Try brand names (most accurate)
    if pd.notna(brand_names) and brand_names:
        brand_list = [b.strip() for b in str(brand_names).split(',')]
        for brand in brand_list[:3]:
            if brand:
                search_terms.append(f'openfda.brand_name:"{brand}"')
    
    # 2. Try generic name
    search_terms.append(f'openfda.generic_name:"{drug_name}"')
    
    # Try each search term
    for search_term in search_terms:
        params = {
            'search': search_term,
            'limit': 1
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'results' in data and len(data['results']) > 0:
                    result = data['results'][0]
                    
                    # Extract information (no strict validation - trust brand name search)
                    info = {
                        'generic_name': drug_name,
                        'rxcui': str(rxcui),
                        'indications': extract_field(result, 'indications_and_usage'),
                        'warnings': extract_field(result, 'boxed_warning'),
                        'contraindications': extract_field(result, 'contraindications'),
                        'adverse_reactions': extract_field(result, 'adverse_reactions'),
                        'dosage': extract_field(result, 'dosage_and_administration'),
                        'source': 'OpenFDA API',
                        'search_term_used': search_term,
                        'fda_application_number': get_nested(result, ['openfda', 'application_number'])
                    }
                    
                    print(f"  ✓ Found for {drug_name} via: {search_term[:50]}...")
                    return info
                    
            elif response.status_code == 404:
                continue
            else:
                print(f"  ⚠ HTTP {response.status_code} for {drug_name}")
                continue
                
        except requests.exceptions.Timeout:
            print(f"  ⏱ Timeout for {drug_name}")
            continue
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Request error for {drug_name}: {str(e)[:50]}")
            continue
        except json.JSONDecodeError:
            print(f"  ✗ JSON decode error for {drug_name}")
            continue
        except Exception as e:
            print(f"  ✗ Unexpected error for {drug_name}: {str(e)[:50]}")
            continue
    
    # No data found
    print(f"  ○ No FDA label found for {drug_name}")
    return create_empty_info(drug_name, rxcui)

def extract_field(result, field_name):
    """
    Extract and clean a field from FDA API result.
    """
    if field_name not in result:
        return 'Information not available from FDA database.'
    
    value = result[field_name]
    
    # Handle list (most FDA fields are lists)
    if isinstance(value, list):
        if len(value) == 0:
            return 'Information not available from FDA database.'
        # Join all items with space
        text = ' '.join(str(item) for item in value)
    else:
        text = str(value)
    
    # Clean up whitespace
    text = text.strip()
    text = ' '.join(text.split())  # Normalize whitespace
    
    # Return cleaned text or default
    if text and text != 'nan':
        return text
    else:
        return 'Information not available from FDA database.'

def get_nested(dictionary, keys, default=''):
    """
    Safely get nested dictionary value.
    """
    try:
        value = dictionary
        for key in keys:
            value = value[key]
        
        if isinstance(value, list):
            return value[0] if len(value) > 0 else default
        return value if value else default
    except (KeyError, TypeError, IndexError):
        return default

def create_empty_info(drug_name, rxcui):
    """
    Create empty info dictionary for drugs without FDA labels.
    """
    return {
        'generic_name': drug_name,
        'rxcui': str(rxcui),
        'indications': 'Information not available from FDA database.',
        'warnings': 'Information not available from FDA database.',
        'contraindications': 'Information not available from FDA database.',
        'adverse_reactions': 'Information not available from FDA database.',
        'dosage': 'Information not available from FDA database.',
        'source': 'N/A',
        'search_term_used': '',
        'fda_application_number': ''
    }

def main():
    print("="*70)
    print("Drug Information Collection from OpenFDA")
    print("="*70)
    print()
    
    # Load drug master list
    try:
        drugs_df = pd.read_csv('data/processed/drug_master.csv')
        print(f"Loaded {len(drugs_df)} drugs from master list")
    except FileNotFoundError:
        print("Error: drug_master.csv not found!")
        print("Please run scripts/01_setup_drug_master.py first")
        return
    except Exception as e:
        print(f"Error loading drug_master.csv: {e}")
        return
    
    print(f"\nFetching FDA drug labels...")
    print(f"   Strategy: Brand names → Generic names")
    print(f"   Using boxed_warning for concise safety info")
    print(f"   Rate limit: ~3 requests/second")
    print()
    
    # Fetch info for each drug
    drug_info_list = []
    start_time = time.time()
    
    for idx, row in drugs_df.iterrows():
        drug_name = row['generic_name']
        brand_names = row.get('brand_names', '')
        rxcui = row['rxcui']
        
        print(f"[{idx+1:3d}/{len(drugs_df)}] {drug_name:<30}", end=' ')
        
        info = fetch_drug_info(drug_name, brand_names, rxcui)
        drug_info_list.append(info)
        
        # Rate limiting - be respectful to the API
        time.sleep(0.3)
    
    elapsed_time = time.time() - start_time
    
    # Create DataFrame
    drug_info_df = pd.DataFrame(drug_info_list)
    
    # Ensure output directory exists
    Path('data/processed').mkdir(parents=True, exist_ok=True)
    
    # Save to CSV and JSON
    drug_info_df.to_csv('data/processed/drug_info.csv', index=False)
    drug_info_df.to_json('data/processed/drug_info.json', orient='records', indent=2)
    
    print()
    print("="*70)
    print("Drug Information Collection Complete")
    print("="*70)
    
    # Calculate statistics
    found_count = len(drug_info_df[drug_info_df['source'] == 'OpenFDA API'])
    not_found_count = len(drug_info_df[drug_info_df['source'] == 'N/A'])
    success_rate = (found_count / len(drug_info_df) * 100) if len(drug_info_df) > 0 else 0
    
    print(f"\nStatistics:")
    print(f"   Total drugs processed:  {len(drug_info_df)}")
    print(f"   FDA labels found:       {found_count}")
    print(f"   Not found:              {not_found_count}")
    print(f"   Success rate:           {success_rate:.1f}%")
    print(f"   Time elapsed:           {elapsed_time:.1f} seconds")
    
    print(f"\nFiles saved:")
    print(f"   ✓ data/processed/drug_info.csv")
    print(f"   ✓ data/processed/drug_info.json")
    
    # Sample of found drugs
    found_drugs = drug_info_df[drug_info_df['source'] == 'OpenFDA API']['generic_name'].head(5).tolist()
    if found_drugs:
        print(f"\nSample of drugs with FDA labels:")
        for drug in found_drugs:
            print(f"   • {drug}")
    
    # Sample of not found drugs
    not_found_drugs = drug_info_df[drug_info_df['source'] == 'N/A']['generic_name'].head(5).tolist()
    if not_found_drugs:
        print(f"\nSample of drugs without FDA labels:")
        for drug in not_found_drugs:
            print(f"   • {drug}")

if __name__ == '__main__':
    main()