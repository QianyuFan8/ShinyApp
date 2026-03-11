import pandas as pd
import re
from collections import Counter
from pathlib import Path

# Load drug info
drug_info_df = pd.read_csv('data/processed/drug_info.csv')
drug_master_df = pd.read_csv('data/processed/drug_master.csv')

# Merge to get category
drug_info_df = drug_info_df.merge(
    drug_master_df[['generic_name', 'category']], 
    on='generic_name', 
    how='left'
) 

# Common side effect keywords to extract
# Based on FDA MedDRA terminology and common adverse reactions
COMMON_SIDE_EFFECTS = [
    # Gastrointestinal
    "nausea", "vomiting", "diarrhea", "constipation", "abdominal pain",
    "stomach pain", "dyspepsia", "indigestion", "heartburn", "gi upset",
    "dry mouth", "loss of appetite", "anorexia",
    
    # Neurological
    "headache", "dizziness", "drowsiness", "sedation", "fatigue",
    "weakness", "insomnia", "sleep disturbance", "tremor", "confusion",
    "vertigo", "somnolence",
    
    # Cardiovascular
    "hypotension", "hypertension", "tachycardia", "palpitations",
    "chest pain", "edema", "swelling",
    
    # Dermatological
    "rash", "itching", "pruritus", "urticaria", "hives", "skin irritation",
    "sweating", "flushing",
    
    # Musculoskeletal
    "muscle pain", "myalgia", "arthralgia", "joint pain", "back pain",
    "muscle weakness", "muscle cramps",
    
    # Respiratory
    "cough", "dyspnea", "shortness of breath", "nasal congestion",
    "pharyngitis", "upper respiratory infection",
    
    # Metabolic
    "weight gain", "weight loss", "hyperglycemia", "hypoglycemia",
    
    # Psychiatric
    "anxiety", "depression", "nervousness", "agitation", "irritability",
    
    # Other
    "fever", "chills", "malaise", "blurred vision", "visual disturbance",
    "tinnitus", "taste disturbance", "xerostomia", "urinary retention",
    "sexual dysfunction", "erectile dysfunction", "decreased libido"
]

# Serious side effects keywords
SERIOUS_SIDE_EFFECTS = [
    # Life-threatening
    "hemorrhage", "bleeding", "anaphylaxis", "angioedema", "seizure",
    "stroke", "heart attack", "myocardial infarction", "arrhythmia",
    "cardiac arrest", "respiratory failure", "liver failure",
    "renal failure", "kidney failure",
    
    # Severe reactions
    "stevens-johnson syndrome", "toxic epidermal necrolysis",
    "agranulocytosis", "aplastic anemia", "thrombocytopenia",
    "neutropenia", "pancreatitis", "hepatotoxicity", "nephrotoxicity",
    
    # Severe bleeding/clotting
    "intracranial bleeding", "gastrointestinal bleeding", "gi bleeding",
    "hematoma", "thrombosis", "embolism",
    
    # Other serious
    "suicidal ideation", "suicide attempt", "hallucinations",
    "neuroleptic malignant syndrome", "serotonin syndrome",
    "rhabdomyolysis", "hepatitis", "jaundice", "hypersensitivity",
    "anaphylactic shock"
]

def extract_side_effects(text, drug_name):
    """
    Extract side effects from adverse reactions text.
    Returns list of (effect, severity) tuples.
    """
    if pd.isna(text) or text == 'Information not available from FDA database.':
        return []
    
    text_lower = text.lower()
    effects_found = []
    
    # Check for serious effects first
    for effect in SERIOUS_SIDE_EFFECTS:
        if effect in text_lower:
            # Remove duplicates by using effect base name
            base_effect = effect.replace("_", " ").title()
            effects_found.append({
                'drug_name': drug_name,
                'side_effect': base_effect,
                'severity': 'Serious',
                'found_in_text': True
            })
    
    # Check for common effects
    for effect in COMMON_SIDE_EFFECTS:
        if effect in text_lower:
            base_effect = effect.replace("_", " ").title()
            # Don't add if already in serious
            if not any(e['side_effect'].lower() == base_effect.lower() and e['severity'] == 'Serious' 
                      for e in effects_found):
                effects_found.append({
                    'drug_name': drug_name,
                    'side_effect': base_effect,
                    'severity': 'Common',
                    'found_in_text': True
                })
    
    return effects_found

def add_educational_effects(drug_name, category):
    """
    Add known educational side effects based on drug category.
    This ensures we have side effect information even if OpenFDA data is sparse.
    """
    educational_effects = {
        'Anticoagulant': [
            ('Bleeding', 'Serious'),
            ('Easy Bruising', 'Common'),
            ('Nausea', 'Common'),
            ('Hemorrhage', 'Serious'),
            ('Intracranial Bleeding', 'Serious'),
        ],
        'NSAID': [
            ('GI Upset', 'Common'),
            ('Nausea', 'Common'),
            ('Heartburn', 'Common'),
            ('GI Bleeding', 'Serious'),
            ('Kidney Problems', 'Serious'),
            ('Ulcers', 'Serious'),
        ],
        'Beta Blocker': [
            ('Fatigue', 'Common'),
            ('Dizziness', 'Common'),
            ('Bradycardia', 'Serious'),
            ('Hypotension', 'Common'),
            ('Cold Extremities', 'Common'),
        ],
        'SSRI': [
            ('Nausea', 'Common'),
            ('Headache', 'Common'),
            ('Insomnia', 'Common'),
            ('Sexual Dysfunction', 'Common'),
            ('Serotonin Syndrome', 'Serious'),
            ('Suicidal Ideation', 'Serious'),
        ],
        'Statin': [
            ('Muscle Pain', 'Common'),
            ('Headache', 'Common'),
            ('Nausea', 'Common'),
            ('Rhabdomyolysis', 'Serious'),
            ('Liver Problems', 'Serious'),
        ],
        'ACE Inhibitor': [
            ('Cough', 'Common'),
            ('Dizziness', 'Common'),
            ('Hypotension', 'Common'),
            ('Angioedema', 'Serious'),
            ('Hyperkalemia', 'Serious'),
        ],
        'PPI': [
            ('Headache', 'Common'),
            ('Diarrhea', 'Common'),
            ('Nausea', 'Common'),
            ('Abdominal Pain', 'Common'),
            ('Vitamin B12 Deficiency', 'Serious'),
        ],
        'Benzodiazepine': [
            ('Drowsiness', 'Common'),
            ('Dizziness', 'Common'),
            ('Confusion', 'Common'),
            ('Memory Problems', 'Common'),
            ('Respiratory Depression', 'Serious'),
            ('Dependence', 'Serious'),
        ],
        'Corticosteroid': [
            ('Increased Appetite', 'Common'),
            ('Weight Gain', 'Common'),
            ('Insomnia', 'Common'),
            ('Mood Changes', 'Common'),
            ('Hyperglycemia', 'Serious'),
            ('Osteoporosis', 'Serious'),
        ],
        'Diuretic': [
            ('Increased Urination', 'Common'),
            ('Dizziness', 'Common'),
            ('Dehydration', 'Common'),
            ('Electrolyte Imbalance', 'Serious'),
            ('Hypotension', 'Common'),
        ],
    }
    
    effects = []
    if category in educational_effects:
        for effect, severity in educational_effects[category]:
            effects.append({
                'drug_name': drug_name,
                'side_effect': effect,
                'severity': severity,
                'found_in_text': False  # Educational supplement
            })
    
    return effects

def main():
    print("Processing side effects from adverse reactions...")
    print(f"Total drugs: {len(drug_info_df)}")
    print()
    
    all_side_effects = []
    
    for idx, row in drug_info_df.iterrows():
        drug_name = row['generic_name']
        category = row['category']
        adverse_text = row['adverse_reactions']
        
        # Extract from FDA text
        extracted = extract_side_effects(adverse_text, drug_name)
        all_side_effects.extend(extracted)
        
        # Add educational effects (ensures coverage)
        educational = add_educational_effects(drug_name, category)
        
        # Combine, removing duplicates
        existing_effects = {e['side_effect'].lower() for e in extracted}
        for edu_effect in educational:
            if edu_effect['side_effect'].lower() not in existing_effects:
                all_side_effects.append(edu_effect)
    
    print(f"Extracted {len(all_side_effects)} side effect records")
    
    # Convert to DataFrame
    side_effects_df = pd.DataFrame(all_side_effects)
    
    # Remove exact duplicates
    side_effects_df = side_effects_df.drop_duplicates(subset=['drug_name', 'side_effect'])
    
    print(f"   After deduplication: {len(side_effects_df)} unique drug-effect pairs")
    
    # Add display order (serious first, then common)
    side_effects_df['severity_order'] = side_effects_df['severity'].map({
        'Serious': 1,
        'Common': 2
    })
    
    side_effects_df = side_effects_df.sort_values(['drug_name', 'severity_order', 'side_effect'])
    
    # Save
    side_effects_df.to_csv('data/processed/side_effects.csv', index=False)
    side_effects_df.to_json('data/processed/side_effects.json', orient='records', indent=2)
    
    print(f"\nSide effects saved:")
    print(f"- data/processed/side_effects.csv")
    print(f"- data/processed/side_effects.json")
    
    # Statistics
    print(f"\nStatistics:")
    print(f"Total side effects: {len(side_effects_df)}")
    print(f"Drugs with side effects: {side_effects_df['drug_name'].nunique()}")
    print(f"Severity breakdown:")
    print(side_effects_df['severity'].value_counts())
    print(f"\nTop 10 most common side effects:")
    print(side_effects_df['side_effect'].value_counts().head(10))
    print(f"\nSource breakdown:")
    print(f"- From FDA text: {side_effects_df['found_in_text'].sum()}")
    print(f"- Educational supplements: {(~side_effects_df['found_in_text']).sum()}")

if __name__ == '__main__':
    main()