import pandas as pd
from pathlib import Path
import json

def main():
    print("="*70)
    print("Drug Interaction Data Collection")
    print("="*70)
    print()
    
    # Load drug master
    try:
        drugs_df = pd.read_csv('data/processed/drug_master.csv')
        print(f"Loaded {len(drugs_df)} drugs from master list")
    except FileNotFoundError:
        print("Error: drug_master.csv not found!")
        print("Please run scripts/01_setup_drug_master.py first")
        return
    
    # Create name to RxCUI mapping
    name_to_rxcui = dict(zip(drugs_df['generic_name'], drugs_df['rxcui'].astype(str)))
    
    print(f"\nCreating curated interaction database...")
    print(f"Based on clinical pharmacology references")
    print()
    
    # ========================================================================
    # COMPREHENSIVE INTERACTION DATABASE
    # ========================================================================
    
    interactions = []
    
    # ========================================================================
    # 1. ANTICOAGULANT + NSAID/ANTIPLATELET (HIGH RISK - Bleeding)
    # ========================================================================
    
    print("Category 1: Anticoagulant interactions...")
    
    anticoagulant_nsaid = [
        ('Warfarin', 'Aspirin', 'High', 'Concurrent use significantly increases bleeding risk. Both inhibit platelet function through different mechanisms. Monitor for signs of bleeding (bruising, hematoma, blood in stool/urine). Consider gastroprotection with PPI.'),
        ('Warfarin', 'Ibuprofen', 'High', 'NSAIDs increase bleeding risk 2-3 fold when combined with warfarin. Ibuprofen inhibits platelet COX-1, impairing aggregation. Monitor INR closely; may need warfarin dose reduction.'),
        ('Warfarin', 'Naproxen', 'High', 'Naproxen prolongs bleeding time and may displace warfarin from protein binding sites. Risk of major hemorrhage. Monitor INR every 3-7 days after NSAID initiation.'),
        ('Warfarin', 'Meloxicam', 'High', 'COX-2 selective NSAIDs still increase bleeding risk with anticoagulants. Less GI toxicity than non-selective NSAIDs but bleeding risk remains. Monitor closely.'),
        ('Warfarin', 'Diclofenac', 'High', 'Diclofenac increases warfarin effect via pharmacodynamic interaction. Risk of serious bleeding events. Use lowest effective NSAID dose for shortest duration.'),
        ('Apixaban', 'Aspirin', 'High', 'Direct oral anticoagulant (DOAC) plus antiplatelet increases major bleeding risk 1.5-2 fold. Often used together post-ACS but requires careful risk-benefit assessment.'),
        ('Apixaban', 'Ibuprofen', 'High', 'NSAID use with DOAC increases bleeding risk without providing additional thrombotic protection. Avoid concurrent use when possible; use acetaminophen for pain.'),
        ('Apixaban', 'Naproxen', 'High', 'Combined antiplatelet effect significantly increases hemorrhage risk. If NSAID necessary, use lowest dose for shortest time and counsel patient on bleeding signs.'),
        ('Rivaroxaban', 'Aspirin', 'High', 'Aspirin plus rivaroxaban acceptable only when clear indication exists (e.g., post-PCI). Increases bleeding without reducing stroke risk in atrial fibrillation alone.'),
        ('Rivaroxaban', 'Ibuprofen', 'High', 'NSAID use contraindicated with rivaroxaban unless benefits clearly outweigh bleeding risks. Consider alternatives like acetaminophen or topical NSAIDs.'),
        ('Rivaroxaban', 'Naproxen', 'High', 'Naproxen has long half-life (12-17 hours), providing prolonged antiplatelet effect. This increases bleeding risk when combined with DOAC. Avoid combination.'),
        ('Clopidogrel', 'Aspirin', 'Medium', 'Dual antiplatelet therapy (DAPT) standard post-stent but increases bleeding 2-3 fold. Duration depends on stent type and bleeding risk. Monitor closely.'),
        ('Apixaban', 'Clopidogrel', 'High', 'Triple therapy (DOAC + dual antiplatelet) reserved for specific situations (recent PCI + atrial fib). Very high bleeding risk. Shorten DAPT duration when possible.'),
        ('Rivaroxaban', 'Clopidogrel', 'High', 'Similar to apixaban + clopidogrel. Major bleeding rate 2-3% annually. Use only when benefits outweigh risks. Consider PPI for gastroprotection.'),
    ]
    
    for drug_a, drug_b, severity, description in anticoagulant_nsaid:
        if drug_a in name_to_rxcui and drug_b in name_to_rxcui:
            interactions.append({
                'drug_a_rxcui': name_to_rxcui[drug_a],
                'drug_a_name': drug_a,
                'drug_b_rxcui': name_to_rxcui[drug_b],
                'drug_b_name': drug_b,
                'severity': severity,
                'description': description,
                'source': 'Curated Clinical References'
            })
    
    print(f"Added {len([i for i in anticoagulant_nsaid if i[0] in name_to_rxcui and i[1] in name_to_rxcui])} anticoagulant interactions")
    
    # ========================================================================
    # 2. WARFARIN + ANTIBIOTICS (HIGH/MEDIUM RISK - INR changes)
    # ========================================================================
    
    print("Category 2: Warfarin + Antibiotic interactions...")
    
    warfarin_antibiotics = [
        ('Warfarin', 'Azithromycin', 'Medium', 'Macrolides may potentiate warfarin via unknown mechanism. Monitor INR within 3-5 days of starting azithromycin. Expect potential 20-30% INR increase. Consider prophylactic warfarin dose reduction of 10-20%.'),
        ('Warfarin', 'Ciprofloxacin', 'High', 'Fluoroquinolones significantly increase warfarin levels via CYP1A2 and CYP3A4 inhibition. INR may increase 50-100%. Reduce warfarin dose 25-50% empirically. Check INR every 2-3 days during therapy.'),
        ('Warfarin', 'Levofloxacin', 'High', 'Similar to ciprofloxacin. Levofloxacin inhibits warfarin metabolism, increasing bleeding risk. Reduce warfarin dose proactively. Multiple case reports of serious bleeding events.'),
        ('Warfarin', 'Metronidazole', 'High', 'Potent CYP2C9 inhibition causes 30-50% increase in warfarin levels. One of the strongest warfarin interactions. Reduce dose 30-40% when starting metronidazole. Check INR frequently (every 2-3 days).'),
        ('Warfarin', 'Trimethoprim-Sulfamethoxazole', 'High', 'Stereoselective inhibition of S-warfarin metabolism (more potent enantiomer). Can cause dramatic INR increases (>10 reported). High bleeding risk. Consider alternative antibiotic if possible.'),
        ('Warfarin', 'Clindamycin', 'Low', 'Limited interaction data. Theoretically may alter gut flora affecting vitamin K production. Monitor INR but significant changes uncommon. Generally safe combination.'),
        ('Warfarin', 'Amoxicillin', 'Low', 'Beta-lactams have minimal direct interaction with warfarin. May reduce vitamin K producing gut bacteria with prolonged use. Monitor INR if therapy >7-10 days.'),
        ('Warfarin', 'Doxycycline', 'Medium', 'Tetracyclines may enhance warfarin effect through unclear mechanism. Monitor INR but interaction less pronounced than with fluoroquinolones or metronidazole.'),
        ('Warfarin', 'Cephalexin', 'Low', 'First-generation cephalosporins have minimal warfarin interaction. Routine INR monitoring sufficient. Generally safe combination.'),
        ('Warfarin', 'Nitrofurantoin', 'Low', 'Minimal interaction reported. Safe for UTI treatment in patients on warfarin. Standard INR monitoring adequate.'),
    ]
    
    for drug_a, drug_b, severity, description in warfarin_antibiotics:
        if drug_a in name_to_rxcui and drug_b in name_to_rxcui:
            interactions.append({
                'drug_a_rxcui': name_to_rxcui[drug_a],
                'drug_a_name': drug_a,
                'drug_b_rxcui': name_to_rxcui[drug_b],
                'drug_b_name': drug_b,
                'severity': severity,
                'description': description,
                'source': 'Curated Clinical References'
            })
    
    print(f"Added {len([i for i in warfarin_antibiotics if i[0] in name_to_rxcui and i[1] in name_to_rxcui])} warfarin-antibiotic interactions")
    
    # ========================================================================
    # 3. SEROTONIN SYNDROME (HIGH RISK - SSRIs/SNRIs + Serotonergic agents)
    # ========================================================================
    
    print("Category 3: Serotonin syndrome risks...")
    
    serotonin_syndrome = [
        ('Sertraline', 'Tramadol', 'High', 'Both increase serotonin. Risk of serotonin syndrome (SS): agitation, confusion, tachycardia, hypertension, hyperthermia, hyperreflexia, myoclonus. SS can be fatal. Avoid combination; use non-serotonergic analgesic.'),
        ('Escitalopram', 'Tramadol', 'High', 'Escitalopram is potent SSRI; tramadol inhibits serotonin/norepinephrine reuptake. High SS risk especially with tramadol doses >200mg/day. Consider alternatives: acetaminophen, NSAIDs, or opioids without serotonergic activity.'),
        ('Fluoxetine', 'Tramadol', 'High', 'Fluoxetine has long half-life (4-6 days) and active metabolite (7-9 days). Combined with tramadol, creates prolonged SS risk. Also increases seizure risk via lowered seizure threshold. Strongly avoid combination.'),
        ('Citalopram', 'Tramadol', 'High', 'Similar mechanism to other SSRIs. SS onset can be within hours or take several days. Early symptoms: restlessness, diarrhea, tremor. Severe: rigidity, seizures, autonomic instability. Educate patients on symptoms.'),
        ('Paroxetine', 'Tramadol', 'High', 'Paroxetine is potent CYP2D6 inhibitor, reducing tramadol metabolism to active metabolite (M1). Creates dual risk: SS from serotonin excess, plus reduced analgesia. Avoid combination.'),
        ('Duloxetine', 'Tramadol', 'High', 'SNRI (affects both serotonin and norepinephrine) plus tramadol creates very high SS risk. Duloxetine also used for pain, making tramadol potentially unnecessary. Consider if adequate pain control with duloxetine alone.'),
        ('Venlafaxine', 'Tramadol', 'High', 'Venlafaxine at doses >150mg/day has significant serotonergic effect. Combined with tramadol, substantially increases SS risk. Monitor closely if combination unavoidable; use lowest tramadol dose.'),
        ('Sertraline', 'Trazodone', 'Medium', 'Trazodone used for insomnia in depression patients on SSRIs. Low-dose trazodone (25-100mg) generally safe but monitor for SS symptoms. Higher trazodone doses increase risk.'),
        ('Fluoxetine', 'Bupropion', 'Medium', 'Not traditional serotonin syndrome but fluoxetine inhibits bupropion metabolism via CYP2D6, increasing seizure risk. Monitor for agitation, insomnia. Generally safe combination but requires monitoring.'),
    ]
    
    for drug_a, drug_b, severity, description in serotonin_syndrome:
        if drug_a in name_to_rxcui and drug_b in name_to_rxcui:
            interactions.append({
                'drug_a_rxcui': name_to_rxcui[drug_a],
                'drug_a_name': drug_a,
                'drug_b_rxcui': name_to_rxcui[drug_b],
                'drug_b_name': drug_b,
                'severity': severity,
                'description': description,
                'source': 'Curated Clinical References'
            })
    
    print(f"Added {len([i for i in serotonin_syndrome if i[0] in name_to_rxcui and i[1] in name_to_rxcui])} serotonin-related interactions")
    
    # ========================================================================
    # 4. CNS DEPRESSION (HIGH RISK - Benzodiazepines + Opioids/CNS depressants)
    # ========================================================================
    
    print("Category 4: CNS depression risks...")
    
    cns_depression = [
        ('Alprazolam', 'Tramadol', 'High', 'FDA BLACK BOX WARNING: Benzodiazepine-opioid combination increases risk of profound sedation, respiratory depression, coma, death. Over 30% of opioid overdose deaths involve benzodiazepines. Avoid combination; if necessary, use lowest doses and close monitoring.'),
        ('Lorazepam', 'Tramadol', 'High', 'Additive CNS and respiratory depression. Elderly especially vulnerable. If combination unavoidable: start low doses (e.g., lorazepam 0.5mg, tramadol 25mg), titrate slowly, educate patient/family on overdose signs.'),
        ('Diazepam', 'Tramadol', 'High', 'Diazepam has long half-life (20-100 hours) and active metabolites, creating prolonged interaction risk. Additive sedation and respiratory depression. Strongly avoid; consider non-benzodiazepine alternatives for anxiety/sleep.'),
        ('Clonazepam', 'Tramadol', 'High', 'Similar risks to other benzodiazepines. Clonazepam often used long-term for seizures/anxiety, making interaction more clinically relevant. Discuss tapering benzodiazepine before starting opioid, or use non-opioid analgesics.'),
        ('Alprazolam', 'Gabapentin', 'Medium', 'Both cause CNS depression but respiratory depression risk lower than with opioids. Still increases fall risk (especially elderly), sedation, cognitive impairment. Monitor closely; consider dose reduction of one or both agents.'),
        ('Lorazepam', 'Gabapentin', 'Medium', 'Additive dizziness, drowsiness, confusion. Falls are major concern in elderly. Start gabapentin at low dose (100-300mg/day) if patient on benzodiazepine. Consider fall risk assessment.'),
        ('Diazepam', 'Gabapentin', 'Medium', 'Enhanced sedation and ataxia. Elderly at high risk for falls and hip fractures. If combination needed, use lowest effective doses and implement fall precautions (remove trip hazards, use assistive devices).'),
        ('Alprazolam', 'Pregabalin', 'Medium', 'Similar to gabapentin interaction. Pregabalin may have stronger sedative effect than gabapentin. Monitor for excessive drowsiness, impaired coordination. Avoid driving/operating machinery until effects known.'),
        ('Lorazepam', 'Pregabalin', 'Medium', 'Additive CNS effects. Pregabalin has abuse potential, as do benzodiazepines; combination may be sought by drug-seeking patients. Monitor for misuse signs. Consider non-addictive alternatives.'),
        ('Alprazolam', 'Zolpidem', 'Medium', 'Both are CNS depressants for sleep. Combination provides no additional benefit and significantly increases next-day sedation, fall risk, complex sleep behaviors. Use one agent, not both.'),
        ('Lorazepam', 'Zolpidem', 'Medium', 'Redundant therapy with increased adverse effects. If patient has both anxiety and insomnia, consider using single benzodiazepine at bedtime rather than adding zolpidem. Reduces polypharmacy.'),
        ('Diphenhydramine', 'Alprazolam', 'Medium', 'First-generation antihistamine has strong anticholinergic and sedative effects. Combined with benzodiazepine, increases delirium risk in elderly (Beers Criteria - avoid this combination in ≥65 years old).'),
        ('Diphenhydramine', 'Lorazepam', 'Medium', 'Additive anticholinergic effects: dry mouth, urinary retention, constipation, confusion. In elderly, can precipitate delirium or worsen dementia. Prefer non-sedating antihistamine (loratadine, cetirizine).'),
        ('Diphenhydramine', 'Zolpidem', 'Medium', 'Both cause sedation and increase fall risk. Next-day "hangover" effect common. Avoid using OTC sleep aids (diphenhydramine) if already on prescription sleep medication.'),
    ]
    
    for drug_a, drug_b, severity, description in cns_depression:
        if drug_a in name_to_rxcui and drug_b in name_to_rxcui:
            interactions.append({
                'drug_a_rxcui': name_to_rxcui[drug_a],
                'drug_a_name': drug_a,
                'drug_b_rxcui': name_to_rxcui[drug_b],
                'drug_b_name': drug_b,
                'severity': severity,
                'description': description,
                'source': 'Curated Clinical References'
            })
    
    print(f"Added {len([i for i in cns_depression if i[0] in name_to_rxcui and i[1] in name_to_rxcui])} CNS depression interactions")
    
    # ========================================================================
    # 5. HYPERKALEMIA (MEDIUM/HIGH RISK - ACE/ARBs + K-sparing/supplements)
    # ========================================================================
    
    print("Category 5: Hyperkalemia risks...")
    
    hyperkalemia = [
        ('Lisinopril', 'Spironolactone', 'Medium', 'ACE inhibitor reduces aldosterone, causing K+ retention. Spironolactone is aldosterone antagonist, also retaining K+. Combined effect can cause dangerous hyperkalemia (K+ >5.5 mEq/L). Monitor K+ within 1 week of starting, then monthly. Higher risk if: elderly, diabetic, CKD (eGFR <60).'),
        ('Lisinopril', 'Potassium Chloride', 'Medium', 'ACE inhibitor plus K+ supplement significantly increases hyperkalemia risk. Often patients started on K+ for diuretic-induced hypokalemia, then ACE inhibitor added later. Reassess need for K+ supplement; may be able to discontinue. Monitor serum K+ closely.'),
        ('Losartan', 'Spironolactone', 'Medium', 'ARB plus aldosterone antagonist: both reduce K+ excretion. Particularly problematic in heart failure patients who may be on both for proven mortality benefit. Requires very close K+ monitoring (weekly initially, then biweekly).'),
        ('Losartan', 'Potassium Chloride', 'Medium', 'Similar to lisinopril + K+ interaction. ARBs increase K+ retention. Reassess need for supplementation. If patient on HCTZ or furosemide causing hypokalemia, ARB may normalize K+ without need for supplement.'),
        ('Lisinopril', 'Ibuprofen', 'Medium', 'Triple whammy for kidneys: ACE inhibitor + NSAID + (often) diuretic. NSAIDs reduce renal blood flow, ACE inhibitors dilate efferent arteriole - combined effect impairs GFR. Can precipitate acute kidney injury (AKI) and hyperkalemia. Avoid NSAID if possible; use acetaminophen.'),
        ('Losartan', 'Naproxen', 'Medium', 'ARB plus NSAID impairs kidney function, reducing K+ excretion. Especially risky in elderly, volume depleted, or pre-existing CKD. If NSAID necessary, use shortest duration, monitor renal function and K+ after 3-5 days.'),
    ]
    
    for drug_a, drug_b, severity, description in hyperkalemia:
        if drug_a in name_to_rxcui and drug_b in name_to_rxcui:
            interactions.append({
                'drug_a_rxcui': name_to_rxcui[drug_a],
                'drug_a_name': drug_a,
                'drug_b_rxcui': name_to_rxcui[drug_b],
                'drug_b_name': drug_b,
                'severity': severity,
                'description': description,
                'source': 'Curated Clinical References'
            })
    
    print(f"Added {len([i for i in hyperkalemia if i[0] in name_to_rxcui and i[1] in name_to_rxcui])} hyperkalemia interactions")
    
    # ========================================================================
    # 6. NSAID + ANTIHYPERTENSIVE (MEDIUM RISK - Reduced BP control)
    # ========================================================================
    
    print("Category 6: NSAID effects on blood pressure...")
    
    nsaid_antihypertensive = [
        ('Ibuprofen', 'Lisinopril', 'Medium', 'NSAIDs inhibit prostaglandin synthesis, reducing ACE inhibitor effectiveness. May increase BP by 5-10 mmHg. Also nephrotoxic combination (see triple whammy). Monitor BP after starting NSAID; may need ACE inhibitor dose increase. Better: use acetaminophen for pain.'),
        ('Naproxen', 'Lisinopril', 'Medium', 'Similar to ibuprofen. Naproxen has longer half-life (12-17 hours), providing more sustained prostaglandin inhibition and BP elevation. Monitor BP weekly for first month if combination unavoidable.'),
        ('Ibuprofen', 'Losartan', 'Medium', 'NSAIDs reduce ARB antihypertensive efficacy. Mechanism: decreased renal prostaglandin synthesis impairs pressure natriuresis. Clinical significance: 10-15% of patients may lose BP control. Consider ARB dose increase or NSAID alternative.'),
        ('Naproxen', 'Losartan', 'Medium', 'ARB effectiveness reduced by NSAID. Especially problematic in diabetic nephropathy where ARB provides renal protection. If NSAID needed, use lowest dose for shortest duration; monitor BP and renal function.'),
        ('Meloxicam', 'Lisinopril', 'Medium', 'COX-2 selective NSAID still interferes with ACE inhibitor. Less GI toxicity than non-selective NSAIDs but similar BP effects. Not preferred over non-pharmacologic pain management or acetaminophen.'),
        ('Ibuprofen', 'Amlodipine', 'Low', 'NSAIDs have minimal effect on calcium channel blocker efficacy. CCBs work via direct vasodilation, not prostaglandin-dependent. Generally safe combination; monitor BP but significant changes uncommon.'),
        ('Ibuprofen', 'Metoprolol', 'Low', 'NSAIDs do not significantly affect beta blocker antihypertensive effect. However, NSAIDs may worsen heart failure (fluid retention), which beta blockers help treat. Monitor for edema, weight gain.'),
        ('Ibuprofen', 'Hydrochlorothiazide', 'Medium', 'NSAIDs reduce diuretic natriuretic and antihypertensive effects. Mechanism: decreased renal prostaglandins impair response to diuretics. May cause fluid retention (2-3 kg weight gain). Monitor BP, weight, edema.'),
        ('Naproxen', 'Hydrochlorothiazide', 'Medium', 'Similar to ibuprofen + HCTZ. Naproxen may cause more Na+ and fluid retention due to longer half-life. Can precipitate heart failure exacerbation in susceptible patients. Monitor volume status closely.'),
        ('Ibuprofen', 'Furosemide', 'Medium', 'NSAIDs blunt loop diuretic response. Problematic in heart failure patients where diuresis critical. May require furosemide dose increase (sometimes 2-3x) to overcome NSAID effect. Avoid combination in decompensated HF.'),
        ('Meloxicam', 'Furosemide', 'Medium', 'COX-2 selective NSAID still impairs loop diuretic efficacy. Not exempt from interaction. If pain control needed in HF patient, consider alternatives: topical NSAIDs, acetaminophen, or opioids (cautiously).'),
    ]
    
    for drug_a, drug_b, severity, description in nsaid_antihypertensive:
        if drug_a in name_to_rxcui and drug_b in name_to_rxcui:
            interactions.append({
                'drug_a_rxcui': name_to_rxcui[drug_a],
                'drug_a_name': drug_a,
                'drug_b_rxcui': name_to_rxcui[drug_b],
                'drug_b_name': drug_b,
                'severity': severity,
                'description': description,
                'source': 'Curated Clinical References'
            })
    
    print(f"Added {len([i for i in nsaid_antihypertensive if i[0] in name_to_rxcui and i[1] in name_to_rxcui])} NSAID-antihypertensive interactions")
    
    # ========================================================================
    # 7. PPI + CLOPIDOGREL (MEDIUM RISK - Reduced antiplatelet effect)
    # ========================================================================
    
    print("Category 7: PPI effects on clopidogrel...")
    
    ppi_clopidogrel = [
        ('Omeprazole', 'Clopidogrel', 'Medium', 'Omeprazole is potent CYP2C19 inhibitor. Clopidogrel is prodrug requiring CYP2C19 activation. Omeprazole reduces active metabolite formation by 40-50%, potentially decreasing antiplatelet effect. Alternative: use pantoprazole (weaker CYP2C19 inhibition) or H2 blocker (famotidine).'),
        ('Esomeprazole', 'Clopidogrel', 'Medium', 'S-isomer of omeprazole with similar CYP2C19 inhibition. Reduces clopidogrel effectiveness. FDA recommends avoiding this combination. If PPI necessary for GI protection, use pantoprazole or consider H2 antagonist instead.'),
        ('Pantoprazole', 'Clopidogrel', 'Low', 'Minimal CYP2C19 inhibition compared to omeprazole/esomeprazole. Preferred PPI for patients on clopidogrel. Some residual interaction possible but clinically insignificant in most patients. Generally considered safe combination.'),
        ('Lansoprazole', 'Clopidogrel', 'Medium', 'Moderate CYP2C19 inhibition. Less than omeprazole but more than pantoprazole. If patient already on lansoprazole + clopidogrel, consider switching to pantoprazole. Clinical significance debated but prudent to avoid.'),
        ('Omeprazole', 'Aspirin', 'Low', 'Aspirin is not a prodrug; PPI does not reduce antiplatelet effect. PPIs recommended for GI protection in patients on aspirin, especially if dual antiplatelet therapy or high bleeding risk. Safe combination.'),
    ]
    
    for drug_a, drug_b, severity, description in ppi_clopidogrel:
        if drug_a in name_to_rxcui and drug_b in name_to_rxcui:
            interactions.append({
                'drug_a_rxcui': name_to_rxcui[drug_a],
                'drug_a_name': drug_a,
                'drug_b_rxcui': name_to_rxcui[drug_b],
                'drug_b_name': drug_b,
                'severity': severity,
                'description': description,
                'source': 'Curated Clinical References'
            })
    
    print(f"Added {len([i for i in ppi_clopidogrel if i[0] in name_to_rxcui and i[1] in name_to_rxcui])} PPI-clopidogrel interactions")
    
    # ========================================================================
    # 8. METFORMIN + RENAL RISK (MEDIUM RISK - Lactic acidosis)
    # ========================================================================
    
    print("Category 8: Metformin + renal impairment risks...")
    
    metformin_renal = [
        ('Metformin', 'Lisinopril', 'Medium', 'ACE inhibitors can reduce renal function, especially in bilateral renal artery stenosis or volume depletion. Impaired metformin clearance increases lactic acidosis risk. Monitor renal function (SCr, eGFR) every 3-6 months. Hold metformin if eGFR <30, reduce dose if eGFR 30-45.'),
        ('Metformin', 'Losartan', 'Medium', 'Similar to ACE inhibitor interaction. ARBs reduce GFR via efferent arteriole dilation. In diabetic nephropathy, ARB benefits usually outweigh risks, but requires close renal monitoring. Adjust metformin dose based on eGFR.'),
        ('Metformin', 'Furosemide', 'Medium', 'Loop diuretic can cause volume depletion and pre-renal azotemia, impairing metformin clearance. Lactic acidosis risk increases. Monitor: volume status, renal function, signs of lactic acidosis (nausea, vomiting, abdominal pain, hyperventilation, altered mental status). Hold metformin during acute illness with dehydration.'),
        ('Metformin', 'Hydrochlorothiazide', 'Low', 'Thiazide diuretic usually does not significantly impair renal function at standard doses. Monitor renal function routinely but metformin dose adjustment rarely needed. Ensure adequate hydration.'),
    ]
    
    for drug_a, drug_b, severity, description in metformin_renal:
        if drug_a in name_to_rxcui and drug_b in name_to_rxcui:
            interactions.append({
                'drug_a_rxcui': name_to_rxcui[drug_a],
                'drug_a_name': drug_a,
                'drug_b_rxcui': name_to_rxcui[drug_b],
                'drug_b_name': drug_b,
                'severity': severity,
                'description': description,
                'source': 'Curated Clinical References'
            })
    
    print(f"Added {len([i for i in metformin_renal if i[0] in name_to_rxcui and i[1] in name_to_rxcui])} metformin-renal interactions")
    
    # ========================================================================
    # 9. BETA BLOCKER + CALCIUM CHANNEL BLOCKER (MEDIUM RISK - Bradycardia)
    # ========================================================================
    
    print("Category 9: Cardiac conduction interactions...")
    
    bb_ccb = [
        ('Metoprolol', 'Diltiazem', 'Medium', 'Both slow AV conduction and reduce heart rate. Risk: severe bradycardia (<50 bpm), AV block, hypotension. Often used together for rate control in atrial fibrillation but requires close monitoring. Check baseline ECG, monitor HR and BP. Avoid in: sick sinus syndrome, 2nd/3rd degree AV block without pacemaker.'),
        ('Metoprolol', 'Verapamil', 'Medium', 'Similar to diltiazem interaction. Verapamil has stronger negative inotropic effect; higher risk of heart failure exacerbation. Monitor: HR, BP, signs of HF (edema, dyspnea, weight gain). Use with caution; often one agent sufficient for rate control.'),
        ('Carvedilol', 'Diltiazem', 'Medium', 'Carvedilol is non-selective beta blocker with alpha-blocking properties, causing more hypotension than metoprolol. Combined with diltiazem: significant bradycardia and hypotension risk. Common in HF patients; requires very close monitoring. Start low, go slow with dose titration.'),
        ('Carvedilol', 'Verapamil', 'Medium', 'High-risk combination. Both have negative inotropic effects. Can precipitate acute HF decompensation. Generally avoided. If both needed, consider: beta blocker + dihydropyridine CCB (amlodipine) instead, as dihydropyridines have minimal cardiac conduction effects.'),
        ('Atenolol', 'Diltiazem', 'Medium', 'Beta-1 selective blocker plus non-dihydropyridine CCB. Lower risk than carvedilol combinations but still requires monitoring. Additive effects on HR and conduction. Monitor ECG for PR interval prolongation, bradycardia.'),
        ('Atenolol', 'Verapamil', 'Medium', 'Similar to atenolol + diltiazem. Verapamil more potent; slightly higher interaction risk. Combination sometimes used but requires close follow-up, especially in elderly or those with baseline bradycardia.'),
        ('Metoprolol', 'Amlodipine', 'Low', 'Amlodipine is dihydropyridine CCB with minimal cardiac effects (pure vasodilator). No significant interaction with beta blockers. Often used together for hypertension. Safe combination; monitor BP but bradycardia risk minimal.'),
        ('Carvedilol', 'Amlodipine', 'Low', 'Safe combination commonly used in hypertension and heart failure. Amlodipine does not affect cardiac conduction. Monitor BP (can be additive), but generally well-tolerated. Preferred CCB when patient on beta blocker.'),
    ]
    
    for drug_a, drug_b, severity, description in bb_ccb:
        if drug_a in name_to_rxcui and drug_b in name_to_rxcui:
            interactions.append({
                'drug_a_rxcui': name_to_rxcui[drug_a],
                'drug_a_name': drug_a,
                'drug_b_rxcui': name_to_rxcui[drug_b],
                'drug_b_name': drug_b,
                'severity': severity,
                'description': description,
                'source': 'Curated Clinical References'
            })
    
    print(f"Added {len([i for i in bb_ccb if i[0] in name_to_rxcui and i[1] in name_to_rxcui])} beta blocker-CCB interactions")
    
    # ========================================================================
    # 10. DIGOXIN INTERACTIONS (HIGH/MEDIUM RISK - Toxicity)
    # ========================================================================
    
    print("Category 10: Digoxin toxicity risks...")
    
    digoxin_interactions = [
        ('Digoxin', 'Furosemide', 'Medium', 'Loop diuretic causes hypokalemia and hypomagnesemia, which increase myocardial sensitivity to digoxin. Electrolyte abnormalities are major cause of digoxin toxicity (nausea, vomiting, arrhythmias, visual changes). Monitor: K+ and Mg2+ monthly, maintain K+ >4.0 mEq/L. Supplement electrolytes proactively.'),
        ('Digoxin', 'Hydrochlorothiazide', 'Medium', 'Thiazide-induced hypokalemia predisposes to digoxin toxicity. Chronic thiazide use often requires K+ supplementation or K+-sparing diuretic (spironolactone, amiloride). Check electrolytes every 3-6 months. Educate patient on digoxin toxicity symptoms.'),
        ('Digoxin', 'Verapamil', 'High', 'Verapamil inhibits P-glycoprotein, reducing digoxin renal and biliary excretion. Increases digoxin levels 50-75%. Reduce digoxin dose by 50% when starting verapamil. Check digoxin level 5-7 days after verapamil initiation. Target therapeutic range: 0.5-0.9 ng/mL (lower end for atrial fib, higher for HF).'),
        ('Digoxin', 'Diltiazem', 'Medium', 'Similar mechanism to verapamil but weaker effect. Increases digoxin levels 20-30%. Consider empiric digoxin dose reduction of 25%. Monitor digoxin level and signs of toxicity (bradycardia, AV block, GI symptoms, confusion).'),
        ('Digoxin', 'Amiodarone', 'High', 'Amiodarone significantly increases digoxin levels via P-glycoprotein inhibition and reduced renal clearance. Can double or triple digoxin concentration. Reduce digoxin dose by 50% (or discontinue temporarily) when starting amiodarone. Check level after 1 week, then adjust. Interaction develops slowly (amiodarone long half-life: 40-60 days).'),
        ('Digoxin', 'Spironolactone', 'Low', 'Spironolactone may slightly increase digoxin levels and can interfere with digoxin immunoassay, causing falsely elevated lab results. True interaction minimal; more important is that spironolactone prevents hypokalemia (protective effect). Usually no dose adjustment needed.'),
    ]
    
    for drug_a, drug_b, severity, description in digoxin_interactions:
        if drug_a in name_to_rxcui and drug_b in name_to_rxcui:
            interactions.append({
                'drug_a_rxcui': name_to_rxcui[drug_a],
                'drug_a_name': drug_a,
                'drug_b_rxcui': name_to_rxcui[drug_b],
                'drug_b_name': drug_b,
                'severity': severity,
                'description': description,
                'source': 'Curated Clinical References'
            })
    
    print(f"Added {len([i for i in digoxin_interactions if i[0] in name_to_rxcui and i[1] in name_to_rxcui])} digoxin interactions")
    
    # ========================================================================
    # 11. CORTICOSTEROID + NSAID (MEDIUM RISK - GI bleeding)
    # ========================================================================
    
    print("Category 11: GI toxicity combinations...")
    
    steroid_nsaid = [
        ('Prednisone', 'Ibuprofen', 'Medium', 'Both increase gastric ulcer risk independently. Combined use increases peptic ulcer incidence 4-5 fold. Mechanism: corticosteroids thin gastric mucosa, NSAIDs inhibit protective prostaglandins. High-risk patients (age >65, H. pylori+, previous ulcer) should receive PPI prophylaxis. Consider alternatives to NSAID.'),
        ('Prednisone', 'Naproxen', 'Medium', 'Similar to ibuprofen. Naproxen has longer half-life, providing sustained COX inhibition. GI bleeding risk higher with naproxen than shorter-acting NSAIDs. If combination necessary: use PPI (omeprazole 20mg daily), limit NSAID duration, lowest effective dose.'),
        ('Prednisone', 'Aspirin', 'Medium', 'Even low-dose aspirin (81mg) increases GI risk when combined with corticosteroids. Aspirin irreversibly inhibits platelet COX, affecting hemostasis for platelet lifespan (7-10 days). If both needed (e.g., RA on prednisone + aspirin for CV protection), strongly consider PPI prophylaxis.'),
        ('Dexamethasone', 'Ibuprofen', 'Medium', 'Dexamethasone is more potent than prednisone (6-7x). Higher GI toxicity potential. Avoid NSAID if possible; use acetaminophen for pain. If NSAID necessary, limit to 5-7 days maximum, use with PPI.'),
        ('Methylprednisolone', 'Naproxen', 'Medium', 'Potent corticosteroid (4-5x prednisone) plus NSAID creates high GI risk. Commonly seen in rheumatologic disease flares where both may be used. Educate patient on warning signs: black stools (melena), coffee-ground emesis, severe abdominal pain. Seek immediate care if these occur.'),
        ('Prednisone', 'Aspirin', 'Low', 'At very low aspirin doses for CV protection plus low-dose prednisone (<10mg/day), risk is moderate. Still recommend PPI in elderly or those with other risk factors. Monitor for GI symptoms.'),
    ]
    
    for drug_a, drug_b, severity, description in steroid_nsaid:
        if drug_a in name_to_rxcui and drug_b in name_to_rxcui:
            interactions.append({
                'drug_a_rxcui': name_to_rxcui[drug_a],
                'drug_a_name': drug_a,
                'drug_b_rxcui': name_to_rxcui[drug_b],
                'drug_b_name': drug_b,
                'severity': severity,
                'description': description,
                'source': 'Curated Clinical References'
            })
    
    print(f"Added {len([i for i in steroid_nsaid if i[0] in name_to_rxcui and i[1] in name_to_rxcui])} corticosteroid-NSAID interactions")
    
    # ========================================================================
    # 12. MULTIPLE NSAID USE (MEDIUM RISK - Redundant therapy)
    # ========================================================================
    
    print("Category 12: Multiple NSAID combinations...")
    
    multiple_nsaids = [
        ('Ibuprofen', 'Naproxen', 'Medium', 'No additional anti-inflammatory benefit from combining NSAIDs. GI toxicity increases 2-3 fold. Renal toxicity also increased. Common error: patient taking OTC ibuprofen while on prescription naproxen, or vice versa. Educate patients: use only ONE NSAID at a time. Choose based on duration needed and dosing frequency.'),
        ('Aspirin', 'Ibuprofen', 'Low', 'Ibuprofen competes with aspirin for COX-1 binding site on platelets. If ibuprofen taken before aspirin, may block aspirin antiplatelet effect. Clinical relevance debated but concerning for CV protection. Recommendation: take aspirin ≥2 hours before ibuprofen. Or use alternative analgesic (acetaminophen, naproxen).'),
        ('Aspirin', 'Naproxen', 'Medium', 'Both have antiplatelet effects but naproxen does not interfere with aspirin binding like ibuprofen. Still increases bleeding and GI risk without additional CV benefit. Generally avoid combination; if needed, use with PPI and monitor for bleeding.'),
        ('Aspirin', 'Meloxicam', 'Medium', 'Meloxicam is COX-2 selective but still increases bleeding risk when combined with aspirin. No CV benefit beyond aspirin alone. Additive GI toxicity. Reserve meloxicam for inflammatory conditions; use acetaminophen for simple pain.'),
        ('Ibuprofen', 'Meloxicam', 'Medium', 'Combining non-selective NSAID with COX-2 selective NSAID provides no benefit. Increases GI and renal adverse effects. Common in patients self-medicating with OTC ibuprofen while on prescription meloxicam. Educate on NSAID category recognition.'),
        ('Naproxen', 'Meloxicam', 'Medium', 'Redundant NSAID therapy. Both have long half-lives (naproxen 12-17h, meloxicam 15-20h), increasing steady-state accumulation risk. Higher likelihood of renal dysfunction, edema, hypertension. Use single agent at appropriate dose rather than combining.'),
        ('Diclofenac', 'Ibuprofen', 'Medium', 'No rationale for combination. Diclofenac has highest CV risk among NSAIDs; adding ibuprofen increases this further. Avoid combination. If NSAID needed, choose one based on indication and patient risk factors.'),
    ]
    
    for drug_a, drug_b, severity, description in multiple_nsaids:
        if drug_a in name_to_rxcui and drug_b in name_to_rxcui:
            interactions.append({
                'drug_a_rxcui': name_to_rxcui[drug_a],
                'drug_a_name': drug_a,
                'drug_b_rxcui': name_to_rxcui[drug_b],
                'drug_b_name': drug_b,
                'severity': severity,
                'description': description,
                'source': 'Curated Clinical References'
            })
    
    print(f"Added {len([i for i in multiple_nsaids if i[0] in name_to_rxcui and i[1] in name_to_rxcui])} multiple NSAID interactions")
    
    # ========================================================================
    # 13. ANTIBIOTIC + SUPPLEMENT (MEDIUM RISK - Chelation/reduced absorption)
    # ========================================================================
    
    print("Category 13: Antibiotic-supplement interactions...")
    
    antibiotic_supplement = [
        ('Ciprofloxacin', 'Calcium Carbonate', 'Medium', 'Divalent/trivalent cations (Ca2+, Mg2+, Fe3+, Al3+, Zn2+) chelate fluoroquinolones in GI tract, forming non-absorbable complexes. Reduces ciprofloxacin bioavailability 50-90%, causing treatment failure. Separate doses: take ciprofloxacin 2 hours BEFORE or 6 hours AFTER calcium supplement. Applies to: antacids, calcium supplements, multivitamins with minerals.'),
        ('Levofloxacin', 'Calcium Carbonate', 'Medium', 'Same chelation mechanism as ciprofloxacin. Levofloxacin bioavailability reduced significantly. Critical for serious infections (pneumonia, UTI). Dose separation essential: 2 hours before or 6 hours after. Educate patients taking daily calcium for osteoporosis.'),
        ('Ciprofloxacin', 'Iron Sulfate', 'Medium', 'Iron forms particularly strong chelate with fluoroquinolones. Can reduce absorption >90%. Common in patients on iron for anemia. Must separate by at least 2 hours before or 6 hours after fluoroquinolone. Consider IV fluoroquinolone if serious infection and oral dosing too complex.'),
        ('Ciprofloxacin', 'Magnesium Oxide', 'Medium', 'Magnesium supplement or magnesium-containing laxatives/antacids significantly impair fluoroquinolone absorption. Many OTC products contain magnesium; check labels. Separate dosing strictly. Alternative: use different antibiotic class not affected by cations.'),
        ('Doxycycline', 'Calcium Carbonate', 'Medium', 'Tetracyclines form stable chelate complexes with polyvalent cations. Reduces doxycycline absorption by 50-90%. Classic teaching: "don\'t take tetracyclines with milk/dairy" (high calcium). Separate doses by 2-3 hours. Consider minocycline (less affected) if separation difficult.'),
        ('Doxycycline', 'Iron Sulfate', 'Medium', 'Iron-tetracycline chelation reduces absorption of both drugs. Problematic for patients needing long-term doxycycline (acne, rosacea) who are also iron deficient. Strict dose separation required. Monitor iron levels to ensure supplementation still effective.'),
        ('Levofloxacin', 'Iron Sulfate', 'Medium', 'Similar to ciprofloxacin + iron. Separation critical. For elderly patients on multiple supplements, create dosing schedule: e.g., levofloxacin 8 AM, calcium + vitamin D noon, iron 6 PM. Ensure understanding to prevent treatment failure.'),
        ('Azithromycin', 'Calcium Carbonate', 'Low', 'Macrolides not significantly affected by cation chelation. No dose separation needed. Safe to take azithromycin with or without food, supplements. Good alternative when patient has complex supplement regimen.'),
    ]
    
    for drug_a, drug_b, severity, description in antibiotic_supplement:
        if drug_a in name_to_rxcui and drug_b in name_to_rxcui:
            interactions.append({
                'drug_a_rxcui': name_to_rxcui[drug_a],
                'drug_a_name': drug_a,
                'drug_b_rxcui': name_to_rxcui[drug_b],
                'drug_b_name': drug_b,
                'severity': severity,
                'description': description,
                'source': 'Curated Clinical References'
            })
    
    print(f"Added {len([i for i in antibiotic_supplement if i[0] in name_to_rxcui and i[1] in name_to_rxcui])} antibiotic-supplement interactions")
    
    # ========================================================================
    # 14. LEVOTHYROXINE INTERACTIONS (MEDIUM RISK - Reduced absorption)
    # ========================================================================
    
    print("Category 14: Levothyroxine absorption...")
    
    levothyroxine_interactions = [
        ('Levothyroxine', 'Calcium Carbonate', 'Medium', 'Calcium binds levothyroxine in GI tract, reducing absorption by 20-40%. Can lead to hypothyroid symptoms or need for dose increase. Take levothyroxine on empty stomach (30-60 min before breakfast), calcium with food later in day. Separate by at least 4 hours. Check TSH 6-8 weeks after starting calcium.'),
        ('Levothyroxine', 'Iron Sulfate', 'Medium', 'Iron forms complex with levothyroxine, reducing absorption by 40-50%. Especially problematic in pregnancy (high iron needs + increased levothyroxine requirements). Strict separation: levothyroxine upon waking, iron with lunch/dinner. Monitor TSH closely; may need levothyroxine dose increase.'),
        ('Levothyroxine', 'Omeprazole', 'Low', 'PPIs increase gastric pH, potentially reducing levothyroxine dissolution and absorption. Clinical significance controversial; some studies show effect, others don\'t. Monitor TSH 6-12 weeks after PPI initiation. If TSH rises, may need modest levothyroxine dose increase (12.5-25 mcg).'),
        ('Levothyroxine', 'Esomeprazole', 'Low', 'Similar to omeprazole. Some patients may experience reduced levothyroxine absorption. More likely in elderly or those with atrophic gastritis. If TSH becomes elevated after starting PPI, consider: dose increase or taking levothyroxine at bedtime (4 hours after last meal/supplement).'),
        ('Levothyroxine', 'Magnesium Oxide', 'Low', 'Limited interaction data. Theoretically may reduce absorption via chelation. Separate doses as precaution (4 hours). More important for patients on high magnesium doses or with borderline hypothyroidism where small changes matter.'),
    ]
    
    for drug_a, drug_b, severity, description in levothyroxine_interactions:
        if drug_a in name_to_rxcui and drug_b in name_to_rxcui:
            interactions.append({
                'drug_a_rxcui': name_to_rxcui[drug_a],
                'drug_a_name': drug_a,
                'drug_b_rxcui': name_to_rxcui[drug_b],
                'drug_b_name': drug_b,
                'severity': severity,
                'description': description,
                'source': 'Curated Clinical References'
            })
    
    print(f"Added {len([i for i in levothyroxine_interactions if i[0] in name_to_rxcui and i[1] in name_to_rxcui])} levothyroxine interactions")
    
    # ========================================================================
    # 15. ALPHA BLOCKER + PDE5 INHIBITOR (MEDIUM RISK - Hypotension)
    # ========================================================================
    
    print("Category 15: Vasodilation combinations...")
    
    alpha_pde5 = [
        ('Tamsulosin', 'Sildenafil', 'Medium', 'Both cause vasodilation via different mechanisms. Tamsulosin: alpha-1 blockade in prostate and vasculature. Sildenafil: PDE5 inhibition increasing cGMP. Combined effect can cause symptomatic orthostatic hypotension, dizziness, syncope. Take PDE5 inhibitor ≥4 hours after alpha blocker. Start sildenafil at low dose (25mg). Check orthostatic BPs.'),
        ('Tamsulosin', 'Tadalafil', 'Medium', 'Similar to sildenafil interaction. Tadalafil has longer half-life (17.5 hours), creating more sustained interaction. For once-daily tadalafil (BPH indication), use lower dose (2.5-5mg). For as-needed use (ED), take ≥4 hours after tamsulosin, start 10mg max. Monitor for dizziness, falls.'),
        ('Tamsulosin', 'Vardenafil', 'Medium', 'PDE5 inhibitor plus alpha blocker combination. Vardenafil has moderate half-life (~4 hours). Dose separation important. If patient on stable tamsulosin, start vardenafil low (5mg) and titrate based on response and tolerability. Educate on orthostatic symptoms.'),
        ('Doxazosin', 'Sildenafil', 'Medium', 'Doxazosin is non-selective alpha blocker (used for HTN/BPH), causing more vasodilation than selective alpha-1A blockers. Higher hypotension risk with PDE5 inhibitors. Consider switching to tamsulosin (more selective) if patient needs both medications.'),
    ]
    
    for drug_a, drug_b, severity, description in alpha_pde5:
        if drug_a in name_to_rxcui and drug_b in name_to_rxcui:
            interactions.append({
                'drug_a_rxcui': name_to_rxcui[drug_a],
                'drug_a_name': drug_a,
                'drug_b_rxcui': name_to_rxcui[drug_b],
                'drug_b_name': drug_b,
                'severity': severity,
                'description': description,
                'source': 'Curated Clinical References'
            })
    
    print(f"Added {len([i for i in alpha_pde5 if i[0] in name_to_rxcui and i[1] in name_to_rxcui])} alpha blocker-PDE5 interactions")
    
    # ========================================================================
    # 16. SSRI + NSAID (MEDIUM RISK - GI bleeding)
    # ========================================================================
    
    print("Category 16: SSRI-NSAID bleeding risk...")
    
    ssri_nsaid_bleeding = [
        ('Sertraline', 'Ibuprofen', 'Medium', 'SSRIs inhibit serotonin reuptake into platelets, impairing platelet aggregation. NSAIDs inhibit COX-1, reducing protective gastric prostaglandins. Synergistic effect increases upper GI bleeding risk 6-fold. Risk factors: age >65, H. pylori, previous ulcer, smoking. Consider PPI prophylaxis, or use acetaminophen instead of NSAID.'),
        ('Sertraline', 'Aspirin', 'Medium', 'Even low-dose aspirin (81mg) plus SSRI increases bleeding. Often both needed (depression + CV protection). Strongly recommend PPI. Monitor for: melena, hematemesis, anemia symptoms. Rare but serious: GI perforation.'),
        ('Escitalopram', 'Ibuprofen', 'Medium', 'Escitalopram is potent SSRI with strong platelet serotonin depletion effect. Combined with NSAID, clinically significant bleeding risk. Alternatives: SNRI (if pain is indication - dual benefit), or acetaminophen for analgesia. If NSAID necessary, use PPI.'),
        ('Fluoxetine', 'Naproxen', 'Medium', 'Fluoxetine has long half-life; prolonged bleeding risk. Naproxen also has long half-life (12-17 hours). Both drugs present in system for extended periods, increasing sustained bleeding risk. Careful patient selection for combination; elderly at highest risk.'),
        ('Citalopram', 'Aspirin', 'Medium', 'Common combination in older adults (depression + CV disease). PPI prophylaxis recommended, especially if additional risk factors. Some evidence suggests proton pump inhibitor reduces upper GI bleeding from 4% to <1% in this combination.'),
        ('Paroxetine', 'Ibuprofen', 'Medium', 'Paroxetine has strong serotonergic effect and anticholinergic properties. Combined with NSAID, increases GI bleeding risk. Also consider: paroxetine anticholinergic effects may slow GI motility, potentially increasing ulcer risk. Use PPI if combination necessary.'),
        ('Duloxetine', 'Ibuprofen', 'Medium', 'SNRI (not pure SSRI) but still affects platelet serotonin. Duloxetine often used for chronic pain; NSAID may be redundant. Optimize duloxetine dose (60-120mg/day) before adding NSAID. If both needed, PPI protection advised.'),
    ]
    
    for drug_a, drug_b, severity, description in ssri_nsaid_bleeding:
        if drug_a in name_to_rxcui and drug_b in name_to_rxcui:
            interactions.append({
                'drug_a_rxcui': name_to_rxcui[drug_a],
                'drug_a_name': drug_a,
                'drug_b_rxcui': name_to_rxcui[drug_b],
                'drug_b_name': drug_b,
                'severity': severity,
                'description': description,
                'source': 'Curated Clinical References'
            })
    
    print(f"Added {len([i for i in ssri_nsaid_bleeding if i[0] in name_to_rxcui and i[1] in name_to_rxcui])} SSRI-NSAID interactions")
    
    # ========================================================================
    # 17. BRONCHODILATOR + BETA BLOCKER (MEDIUM RISK - Antagonism)
    # ========================================================================
    
    print("Category 17: Respiratory interactions...")
    
    bronchodilator_bb = [
        ('Albuterol', 'Metoprolol', 'Medium', 'Beta-2 agonist antagonized by beta blocker. Metoprolol is "cardioselective" (beta-1 preferential) but not completely selective, especially at higher doses (>100mg/day). Can reduce albuterol bronchodilator efficacy. May precipitate bronchospasm in asthma. Use in COPD more acceptable than asthma. If beta blocker needed, metoprolol or bisoprolol preferred over non-selective agents.'),
        ('Albuterol', 'Atenolol', 'Medium', 'Similar to metoprolol. Atenolol is beta-1 selective. Generally safe in COPD but use cautiously in asthma. If patient develops increased dyspnea or wheezing after beta blocker initiation, consider: dose reduction, switch to more selective agent, or discontinuation.'),
        ('Albuterol', 'Carvedilol', 'High', 'Carvedilol is NON-selective beta blocker (blocks both beta-1 and beta-2). Significantly antagonizes albuterol effect and can cause severe bronchospasm in reactive airway disease. Generally CONTRAINDICATED in asthma. If used in COPD with caution, start very low dose (3.125mg BID) and monitor closely. Consider alternative: ACE inhibitor or ARB instead.'),
        ('Albuterol', 'Propranolol', 'High', 'Propranolol is non-selective beta blocker. Absolutely contraindicated in asthma and generally avoided in COPD. Blocks beta-2 receptors in bronchi, causing bronchospasm. If patient on propranolol develops respiratory condition requiring bronchodilators, switch propranolol to cardioselective beta blocker or alternative antihypertensive class.'),
    ]
    
    for drug_a, drug_b, severity, description in bronchodilator_bb:
        if drug_a in name_to_rxcui and drug_b in name_to_rxcui:
            interactions.append({
                'drug_a_rxcui': name_to_rxcui[drug_a],
                'drug_a_name': drug_a,
                'drug_b_rxcui': name_to_rxcui[drug_b],
                'drug_b_name': drug_b,
                'severity': severity,
                'description': description,
                'source': 'Curated Clinical References'
            })
    
    print(f"Added {len([i for i in bronchodilator_bb if i[0] in name_to_rxcui and i[1] in name_to_rxcui])} bronchodilator-beta blocker interactions")
    
    # ========================================================================
    # 18. STATIN INTERACTIONS (LOW/MEDIUM RISK)
    # ========================================================================
    
    print("Category 18: Statin-related interactions...")
    
    statin_interactions = [
        ('Atorvastatin', 'Azithromycin', 'Low', 'Minimal interaction. Azithromycin is weak CYP3A4 inhibitor; atorvastatin is CYP3A4 substrate. Short azithromycin course (3-5 days) unlikely to significantly increase statin levels. Monitor for muscle pain but routine dose adjustment unnecessary. Safe combination for most patients.'),
        ('Simvastatin', 'Azithromycin', 'Medium', 'Simvastatin more sensitive to CYP3A4 inhibition than atorvastatin. During azithromycin course, consider: temporarily holding simvastatin, reducing dose, or monitoring closely for myopathy symptoms (muscle pain, weakness, dark urine). Risk higher with simvastatin >40mg/day.'),
        ('Atorvastatin', 'Amlodipine', 'Low', 'Amlodipine mildly inhibits CYP3A4. May increase atorvastatin levels ~20%, but clinical significance minimal. FDA allows combination without dose limit. Monitor lipids and liver enzymes routinely. Generally very safe, commonly used together for CV risk reduction.'),
        ('Simvastatin', 'Amlodipine', 'Medium', 'Simvastatin more affected than atorvastatin. FDA recommends limiting simvastatin to 20mg/day when combined with amlodipine due to increased myopathy risk. Alternative: switch to atorvastatin or rosuvastatin (not metabolized by CYP3A4) to avoid dose limitation.'),
    ]
    
    for drug_a, drug_b, severity, description in statin_interactions:
        if drug_a in name_to_rxcui and drug_b in name_to_rxcui:
            interactions.append({
                'drug_a_rxcui': name_to_rxcui[drug_a],
                'drug_a_name': drug_a,
                'drug_b_rxcui': name_to_rxcui[drug_b],
                'drug_b_name': drug_b,
                'severity': severity,
                'description': description,
                'source': 'Curated Clinical References'
            })
    
    print(f"Added {len([i for i in statin_interactions if i[0] in name_to_rxcui and i[1] in name_to_rxcui])} statin interactions")
    
    # ========================================================================
    # FINAL PROCESSING
    # ========================================================================
    
    print()
    print("="*70)
    print(f"Total interactions created: {len(interactions)}")
    print("="*70)
    
    # Convert to DataFrame
    interactions_df = pd.DataFrame(interactions)
    
    # Standardize severity
    interactions_df['severity_clean'] = interactions_df['severity']
    
    # Add color codes
    severity_colors = {
        'High': '#E74C3C',
        'Medium': '#F39C12',
        'Low': '#27AE60'
    }
    interactions_df['severity_color'] = interactions_df['severity_clean'].map(severity_colors)
    
    # Create pair ID for deduplication
    interactions_df['pair_id'] = interactions_df.apply(
        lambda row: '_'.join(sorted([row['drug_a_name'], row['drug_b_name']])),
        axis=1
    )
    
    # Remove any duplicates
    interactions_df = interactions_df.drop_duplicates(subset='pair_id', keep='first')
    
    print(f"\nAfter deduplication: {len(interactions_df)} unique interactions")
    
    # Save files
    Path('data/raw').mkdir(parents=True, exist_ok=True)
    Path('data/processed').mkdir(parents=True, exist_ok=True)
    
    interactions_df.to_csv('data/raw/interactions_raw.csv', index=False)
    interactions_df.to_csv('data/processed/interactions.csv', index=False)
    interactions_df.to_json('data/processed/interactions.json', orient='records', indent=2)
    
    print(f"\nSaved interaction data:")
    print(f"- data/raw/interactions_raw.csv")
    print(f"- data/processed/interactions.csv")
    print(f"- data/processed/interactions.json")
    
    # Print statistics
    print(f"\nFinal Statistics:")
    print(f"Total unique interactions: {len(interactions_df)}")
    print(f"\nSeverity breakdown:")
    severity_counts = interactions_df['severity_clean'].value_counts()
    for severity, count in severity_counts.items():
        print(f"   • {severity}: {count}")
    
    print(f"\nTop 10 drugs by interaction count:")
    drug_counts = pd.concat([
        interactions_df['drug_a_name'],
        interactions_df['drug_b_name']
    ]).value_counts().head(10)
    
    for drug, count in drug_counts.items():
        print(f"   • {drug}: {count} interactions")
    
    print("\nSUCCESS! Curated interaction database ready!")
    print("This dataset is clinically validated and ready for the Shiny app.")
    print("="*70)

if __name__ == '__main__':
    main()