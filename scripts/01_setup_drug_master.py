import pandas as pd
import json

# Top 100 most prescribed drugs in USA (2023-2024)
# Source: ClinCalc DrugStats Database
# https://clincalc.com/DrugStats/

top_100_drugs = [
    # Cardiovascular (20)
    {"generic_name": "Lisinopril", "brand_names": "Prinivil, Zestril", "category": "ACE Inhibitor", "rxcui": "29046"},
    {"generic_name": "Atorvastatin", "brand_names": "Lipitor", "category": "Statin", "rxcui": "83367"},
    {"generic_name": "Amlodipine", "brand_names": "Norvasc", "category": "Calcium Channel Blocker", "rxcui": "17767"},
    {"generic_name": "Metoprolol", "brand_names": "Lopressor, Toprol-XL", "category": "Beta Blocker", "rxcui": "6918"},
    {"generic_name": "Losartan", "brand_names": "Cozaar", "category": "ARB", "rxcui": "52175"},
    {"generic_name": "Simvastatin", "brand_names": "Zocor", "category": "Statin", "rxcui": "36567"},
    {"generic_name": "Furosemide", "brand_names": "Lasix", "category": "Diuretic", "rxcui": "4603"},
    {"generic_name": "Hydrochlorothiazide", "brand_names": "Microzide", "category": "Diuretic", "rxcui": "5487"},
    {"generic_name": "Carvedilol", "brand_names": "Coreg", "category": "Beta Blocker", "rxcui": "20352"},
    {"generic_name": "Clopidogrel", "brand_names": "Plavix", "category": "Antiplatelet", "rxcui": "32968"},
    {"generic_name": "Warfarin", "brand_names": "Coumadin, Jantoven", "category": "Anticoagulant", "rxcui": "11289"},
    {"generic_name": "Apixaban", "brand_names": "Eliquis", "category": "Anticoagulant", "rxcui": "1364430"},
    {"generic_name": "Rivaroxaban", "brand_names": "Xarelto", "category": "Anticoagulant", "rxcui": "1114195"},
    {"generic_name": "Spironolactone", "brand_names": "Aldactone", "category": "Diuretic", "rxcui": "9997"},
    {"generic_name": "Diltiazem", "brand_names": "Cardizem", "category": "Calcium Channel Blocker", "rxcui": "3443"},
    {"generic_name": "Verapamil", "brand_names": "Calan", "category": "Calcium Channel Blocker", "rxcui": "11170"},
    {"generic_name": "Propranolol", "brand_names": "Inderal", "category": "Beta Blocker", "rxcui": "8787"},
    {"generic_name": "Atenolol", "brand_names": "Tenormin", "category": "Beta Blocker", "rxcui": "1202"},
    {"generic_name": "Digoxin", "brand_names": "Lanoxin", "category": "Cardiac Glycoside", "rxcui": "3407"},
    {"generic_name": "Rosuvastatin", "brand_names": "Crestor", "category": "Statin", "rxcui": "301542"},
    
    # Diabetes (8)
    {"generic_name": "Metformin", "brand_names": "Glucophage", "category": "Antidiabetic", "rxcui": "6809"},
    {"generic_name": "Glipizide", "brand_names": "Glucotrol", "category": "Sulfonylurea", "rxcui": "4815"},
    {"generic_name": "Insulin Glargine", "brand_names": "Lantus", "category": "Insulin", "rxcui": "274783"},
    {"generic_name": "Sitagliptin", "brand_names": "Januvia", "category": "DPP-4 Inhibitor", "rxcui": "665033"},
    {"generic_name": "Empagliflozin", "brand_names": "Jardiance", "category": "SGLT2 Inhibitor", "rxcui": "1545653"},
    {"generic_name": "Dulaglutide", "brand_names": "Trulicity", "category": "GLP-1 Agonist", "rxcui": "1551291"},
    {"generic_name": "Insulin Aspart", "brand_names": "Novolog", "category": "Insulin", "rxcui": "253182"},
    {"generic_name": "Glyburide", "brand_names": "DiaBeta", "category": "Sulfonylurea", "rxcui": "4821"},
    
    # Pain/NSAIDs (12)
    {"generic_name": "Ibuprofen", "brand_names": "Advil, Motrin", "category": "NSAID", "rxcui": "5640"},
    {"generic_name": "Naproxen", "brand_names": "Aleve, Naprosyn", "category": "NSAID", "rxcui": "7258"},
    {"generic_name": "Acetaminophen", "brand_names": "Tylenol", "category": "Analgesic", "rxcui": "161"},
    {"generic_name": "Aspirin", "brand_names": "Bayer, Ecotrin", "category": "NSAID", "rxcui": "1191"},
    {"generic_name": "Meloxicam", "brand_names": "Mobic", "category": "NSAID", "rxcui": "6960"},
    {"generic_name": "Tramadol", "brand_names": "Ultram", "category": "Opioid", "rxcui": "10689"},
    {"generic_name": "Gabapentin", "brand_names": "Neurontin", "category": "Anticonvulsant", "rxcui": "4493"},
    {"generic_name": "Pregabalin", "brand_names": "Lyrica", "category": "Anticonvulsant", "rxcui": "187832"},
    {"generic_name": "Cyclobenzaprine", "brand_names": "Flexeril", "category": "Muscle Relaxant", "rxcui": "3112"},
    {"generic_name": "Baclofen", "brand_names": "Lioresal", "category": "Muscle Relaxant", "rxcui": "1292"},
    {"generic_name": "Methocarbamol", "brand_names": "Robaxin", "category": "Muscle Relaxant", "rxcui": "6878"},
    {"generic_name": "Diclofenac", "brand_names": "Voltaren", "category": "NSAID", "rxcui": "3355"},
    
    # Mental Health (15)
    {"generic_name": "Sertraline", "brand_names": "Zoloft", "category": "SSRI", "rxcui": "36437"},
    {"generic_name": "Escitalopram", "brand_names": "Lexapro", "category": "SSRI", "rxcui": "321988"},
    {"generic_name": "Fluoxetine", "brand_names": "Prozac", "category": "SSRI", "rxcui": "4493"},
    {"generic_name": "Citalopram", "brand_names": "Celexa", "category": "SSRI", "rxcui": "2556"},
    {"generic_name": "Paroxetine", "brand_names": "Paxil", "category": "SSRI", "rxcui": "32937"},
    {"generic_name": "Bupropion", "brand_names": "Wellbutrin", "category": "Antidepressant", "rxcui": "42347"},
    {"generic_name": "Duloxetine", "brand_names": "Cymbalta", "category": "SNRI", "rxcui": "72625"},
    {"generic_name": "Venlafaxine", "brand_names": "Effexor", "category": "SNRI", "rxcui": "39786"},
    {"generic_name": "Trazodone", "brand_names": "Desyrel", "category": "Antidepressant", "rxcui": "10737"},
    {"generic_name": "Amitriptyline", "brand_names": "Elavil", "category": "TCA", "rxcui": "704"},
    {"generic_name": "Alprazolam", "brand_names": "Xanax", "category": "Benzodiazepine", "rxcui": "596"},
    {"generic_name": "Lorazepam", "brand_names": "Ativan", "category": "Benzodiazepine", "rxcui": "6470"},
    {"generic_name": "Clonazepam", "brand_names": "Klonopin", "category": "Benzodiazepine", "rxcui": "2598"},
    {"generic_name": "Diazepam", "brand_names": "Valium", "category": "Benzodiazepine", "rxcui": "3322"},
    {"generic_name": "Zolpidem", "brand_names": "Ambien", "category": "Sedative", "rxcui": "39993"},
    
    # GI (8)
    {"generic_name": "Omeprazole", "brand_names": "Prilosec", "category": "PPI", "rxcui": "7646"},
    {"generic_name": "Pantoprazole", "brand_names": "Protonix", "category": "PPI", "rxcui": "40790"},
    {"generic_name": "Lansoprazole", "brand_names": "Prevacid", "category": "PPI", "rxcui": "17128"},
    {"generic_name": "Esomeprazole", "brand_names": "Nexium", "category": "PPI", "rxcui": "283742"},
    {"generic_name": "Famotidine", "brand_names": "Pepcid", "category": "H2 Blocker", "rxcui": "4278"},
    {"generic_name": "Ranitidine", "brand_names": "Zantac", "category": "H2 Blocker", "rxcui": "8987"},
    {"generic_name": "Ondansetron", "brand_names": "Zofran", "category": "Antiemetic", "rxcui": "38400"},
    {"generic_name": "Metoclopramide", "brand_names": "Reglan", "category": "Antiemetic", "rxcui": "6915"},
    
    # Respiratory (8)
    {"generic_name": "Albuterol", "brand_names": "ProAir, Ventolin", "category": "Beta-2 Agonist", "rxcui": "435"},
    {"generic_name": "Montelukast", "brand_names": "Singulair", "category": "Leukotriene Inhibitor", "rxcui": "88249"},
    {"generic_name": "Fluticasone", "brand_names": "Flovent", "category": "Corticosteroid", "rxcui": "202421"},
    {"generic_name": "Budesonide", "brand_names": "Pulmicort", "category": "Corticosteroid", "rxcui": "1998"},
    {"generic_name": "Prednisone", "brand_names": "Deltasone", "category": "Corticosteroid", "rxcui": "8640"},
    {"generic_name": "Methylprednisolone", "brand_names": "Medrol", "category": "Corticosteroid", "rxcui": "6902"},
    {"generic_name": "Dexamethasone", "brand_names": "Decadron", "category": "Corticosteroid", "rxcui": "3264"},
    {"generic_name": "Salmeterol", "brand_names": "Serevent", "category": "Beta-2 Agonist", "rxcui": "36117"},
    
    # Antibiotics (10)
    {"generic_name": "Amoxicillin", "brand_names": "Amoxil", "category": "Penicillin", "rxcui": "723"},
    {"generic_name": "Azithromycin", "brand_names": "Zithromax", "category": "Macrolide", "rxcui": "18631"},
    {"generic_name": "Doxycycline", "brand_names": "Vibramycin", "category": "Tetracycline", "rxcui": "3640"},
    {"generic_name": "Ciprofloxacin", "brand_names": "Cipro", "category": "Fluoroquinolone", "rxcui": "2551"},
    {"generic_name": "Levofloxacin", "brand_names": "Levaquin", "category": "Fluoroquinolone", "rxcui": "82122"},
    {"generic_name": "Cephalexin", "brand_names": "Keflex", "category": "Cephalosporin", "rxcui": "2231"},
    {"generic_name": "Clindamycin", "brand_names": "Cleocin", "category": "Lincosamide", "rxcui": "2582"},
    {"generic_name": "Trimethoprim-Sulfamethoxazole", "brand_names": "Bactrim", "category": "Sulfonamide", "rxcui": "10831"},
    {"generic_name": "Metronidazole", "brand_names": "Flagyl", "category": "Nitroimidazole", "rxcui": "6922"},
    {"generic_name": "Nitrofurantoin", "brand_names": "Macrobid", "category": "Nitrofuran", "rxcui": "7517"},
    
    # Other (19)
    {"generic_name": "Levothyroxine", "brand_names": "Synthroid", "category": "Thyroid", "rxcui": "10582"},
    {"generic_name": "Vitamin D", "brand_names": "Cholecalciferol", "category": "Supplement", "rxcui": "316672"},
    {"generic_name": "Vitamin B12", "brand_names": "Cyanocobalamin", "category": "Supplement", "rxcui": "3310"},
    {"generic_name": "Folic Acid", "brand_names": "", "category": "Supplement", "rxcui": "4419"},
    {"generic_name": "Iron Sulfate", "brand_names": "Feosol", "category": "Supplement", "rxcui": "5640"},
    {"generic_name": "Calcium Carbonate", "brand_names": "Tums", "category": "Supplement", "rxcui": "2122"},
    {"generic_name": "Tamsulosin", "brand_names": "Flomax", "category": "Alpha Blocker", "rxcui": "77492"},
    {"generic_name": "Finasteride", "brand_names": "Proscar", "category": "5-Alpha Reductase", "rxcui": "4469"},
    {"generic_name": "Sildenafil", "brand_names": "Viagra", "category": "PDE5 Inhibitor", "rxcui": "136411"},
    {"generic_name": "Tadalafil", "brand_names": "Cialis", "category": "PDE5 Inhibitor", "rxcui": "349332"},
    {"generic_name": "Cetirizine", "brand_names": "Zyrtec", "category": "Antihistamine", "rxcui": "2270"},
    {"generic_name": "Loratadine", "brand_names": "Claritin", "category": "Antihistamine", "rxcui": "6472"},
    {"generic_name": "Fexofenadine", "brand_names": "Allegra", "category": "Antihistamine", "rxcui": "83160"},
    {"generic_name": "Diphenhydramine", "brand_names": "Benadryl", "category": "Antihistamine", "rxcui": "3498"},
    {"generic_name": "Pseudoephedrine", "brand_names": "Sudafed", "category": "Decongestant", "rxcui": "8787"},
    {"generic_name": "Potassium Chloride", "brand_names": "K-Dur", "category": "Electrolyte", "rxcui": "8591"},
    {"generic_name": "Magnesium Oxide", "brand_names": "", "category": "Supplement", "rxcui": "6675"},
    {"generic_name": "Multivitamin", "brand_names": "", "category": "Supplement", "rxcui": "7238"},
    {"generic_name": "Fish Oil", "brand_names": "Omega-3", "category": "Supplement", "rxcui": "849574"},
]

# Convert to DataFrame
df = pd.DataFrame(top_100_drugs)

# Add search fields for fuzzy matching
df['search_terms'] = df.apply(
    lambda row: f"{row['generic_name']},{row['brand_names']},{row['category']}".lower(),
    axis=1
)

# Add display name (for UI)
df['display_name'] = df.apply(
    lambda row: f"{row['generic_name']}" + (f" ({row['brand_names'].split(',')[0]})" if row['brand_names'] else ""),
    axis=1
)

# Save
df.to_csv('data/processed/drug_master.csv', index=False)
df.to_json('data/processed/drug_master.json', orient='records', indent=2)

print(f"Created drug master list with {len(df)} drugs")
print(f"Saved to: data/processed/drug_master.csv")
print(f"\nCategories:")
print(df['category'].value_counts())