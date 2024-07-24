import os
import subprocess
import pandas as pd
import PyWGCNA

def generate_deg() -> None:
    if os.path.exists('data/DESeq2_combined_results.csv'):
        pass
    else:
        subprocess.run(['Rscript', 'deseq.R'])

def load_data() -> tuple:
    generate_deg()
    return (
        pd.read_csv('data/DESeq2_combined_results.txt', sep='\t'),
        pd.read_csv('data/E-GEOD-46730-raw-counts.txt', sep='\t'),
        pd.read_csv('data/GSE46730_RNA-seq-Nianwei.txt', sep='\t', index_col=0)
    )

def init_wgcna(expr_data:pd.DataFrame) -> PyWGCNA.WGCNA:
    obj = PyWGCNA.WGCNA(
        geneExp = expr_data,
        name = 'TUNA_kd',
        species = 'mus musculus',
        outputPath = 'data/wgcna/'
    )
    return obj
