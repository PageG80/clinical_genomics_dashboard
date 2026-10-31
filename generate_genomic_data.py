import os
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_genomic_dataset(num_records=1000, db_path="data/genomics_registry.db"):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    np.random.seed(42) 
    
    genes_variants = {
        "BRCA1": ["p.Cys61Gly", "p.Arg1443Ter", "p.Glu185X", "p.Ser1719Pro"],
        "BRCA2": ["p.Lys3326Ter", "p.Ser1982Arg", "p.Asn372His"],
        "TP53": ["p.Arg248Trp", "p.Arg175His", "p.Gly241Ala", "p.Arg273His"],
        "EGFR": ["p.Leu858Arg", "p.Thr790Met", "p.Gly719Ser", "p.exon19del"],
        "KRAS": ["p.Gly12Asp", "p.Gly12Val", "p.Gln61His"],
        "PTEN": ["p.Arg130Ter", "p.IVS4+1G>A", "p.Pro167Ser"],
        "PIK3CA": ["p.Glu542Lys", "p.Glu545Lys", "p.His1047Arg"],
        "ALK": ["p.F1164L", "p.C1156Y", "p.L1196M"],
        "BRAF": ["p.Val600Glu", "p.Val600Lys", "p.Gly466Glu"]
    }
    
    genes = list(genes_variants.keys())
    acmg_classes = [
        "Pathogenic", 
        "Likely Pathogenic", 
        "Variant of Uncertain Significance (VUS)", 
        "Benign", 
        "Likely Benign"
    ]
    acmg_weights = [0.25, 0.15, 0.35, 0.15, 0.10] 
    
    patient_ids = [f"PT-{np.random.randint(10000, 99999)}" for _ in range(num_records)]
    biosample_ids = [f"BS-{np.random.randint(100000, 999999)}" for _ in range(num_records)]
    
    selected_genes = np.random.choice(genes, num_records)
    selected_variants = [np.random.choice(genes_variants[g]) for g in selected_genes]
    selected_acmg = np.random.choice(acmg_classes, num_records, p=acmg_weights)
    
    start_date = datetime.now() - timedelta(days=365)
    collection_dates = [start_date + timedelta(days=int(np.random.randint(0, 350))) for _ in range(num_records)]
    
    tat_days = np.random.gamma(shape=4, scale=3, size=num_records).astype(int) + 7
    report_dates = [col + timedelta(days=int(tat)) for col, tat in zip(collection_dates, tat_days)]
    
    df = pd.DataFrame({
        "patient_id": patient_ids,
        "biosample_id": biosample_ids,
        "gene": selected_genes,
        "variant_nomenclature": selected_variants,
        "acmg_classification": selected_acmg,
        "collection_date": [d.strftime("%Y-%m-%d") for d in collection_dates],
        "report_date": [d.strftime("%Y-%m-%d") for d in report_dates],
        "turnaround_days": tat_days
    })
    
    conn = sqlite3.connect(db_path)
    df.to_sql("variant_registry", conn, if_exists="replace", index=False)
    conn.close()
    
    print(f"[SUCCESS] Generated {num_records} synthetic clinical genomics records at '{db_path}'.")

if __name__ == "__main__":
    generate_genomic_dataset()