import os
import subprocess
from types import FunctionType
import pandas as pd
import PyWGCNA
import streamlit as st
import numpy as np
from scipy.integrate import odeint
from scipy.optimize import minimize, OptimizeResult
import graphviz

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
        pd.read_csv('data/GSE46730_RNA-seq-Nianwei.txt', sep='\t', index_col=0),
        pd.read_csv('data/wgcna/figures/maroon_adjmat.csv', index_col=0),
        pd.DataFrame({
            'sample': ["SRR847690", "SRR847691", "SRR847692", "SRR847693", "SRR847694", "SRR847695", "SRR847696", "SRR847697", "SRR847698", "SRR847699", "SRR847700", "SRR847701"],
            'time': ["day_2", "day_2", "day_2", "day_2", "day_2", "day_2", "day_4", "day_4", "day_4", "day_6", "day_6", "day_6"],
            'treatment': ["control", "control", "control", "treated", "treated", "treated", "treated", "treated", "treated", "treated", "treated", "treated"]
        }),
        pd.read_csv('data/wgcna/figures/top_20_hub_genes_maroon.csv', index_col=0),
    )

def init_wgcna(expr_data:pd.DataFrame) -> PyWGCNA.WGCNA:
    obj = PyWGCNA.WGCNA(
        geneExp = expr_data,
        name = 'TUNA_kd',
        species = 'mus musculus',
        outputPath = 'data/wgcna/',
        save=True
    )
    obj.preprocess()
    obj.findModules()
    return obj

# Define a function to load the data and set global variables
def initialize_data():
    if not all([key in st.session_state for key in ['counts', 'deg', 'tpm', 'adjmat', 'metadata', 'hyp']]):
        with st.spinner("Loading data..."):
            deg, counts, tpm, adjmat, metadata, hyp = load_data()
            st.session_state.counts = counts
            st.session_state.deg = deg
            st.session_state.tpm = tpm
            st.session_state.adjmat = adjmat
            st.session_state.metadata = metadata
            st.session_state.hyp = hyp
        st.success("Data loaded successfully!")

def gene_network_dynamics(
    y:np.ndarray,
    t:float,
    adj_matrix:np.ndarray,
    params:np.ndarray
) -> np.ndarray:
    dydt = np.zeros(len(y))
    for i in range(len(y)):
        interaction_sum = 0
        for j in range(len(y)):
            interaction_sum += adj_matrix[i, j] * y[j]
        r_i = params[i]
        K_i = params[len(y) + i]
        dydt[i] = r_i * y[i] * (1 - y[i] / K_i) + interaction_sum
    return dydt

def objective_function(
    params:np.ndarray,
    adj_matrix:np.ndarray,
    initial_conditions:np.ndarray,
    time_points:np.ndarray,
    observed_data:pd.DataFrame
) -> float:
    solution = integrate_model(gene_network_dynamics, initial_conditions, time_points, adj_matrix, params)

    # Calculate the error
    error = np.sum((solution - observed_data.values.T) ** 2)

    return error

def calculate_median_tpm(tpm:pd.DataFrame, metadata:pd.DataFrame) -> pd.DataFrame:
    tpm_copy = tpm.copy()

    # Check if the index is already a column to avoid duplication
    if 'index' in tpm_copy.columns:
        tpm_copy.reset_index(drop=True, inplace=True)
    else:
        tpm_copy.reset_index(inplace=True)

    tpm_long = tpm_copy.melt(id_vars=["Name"], var_name="sample", value_name="tpm")
    merged_df = tpm_long.merge(metadata, on="sample")
    median_tpm = merged_df.groupby(['Name', 'time', 'treatment'])['tpm'].median().reset_index()
    median_tpm_wide = median_tpm.pivot_table(index="Name", columns=['time', 'treatment'], values='tpm')

    median_tpm_wide.columns = [f"{time}_{treatment}" for time, treatment in median_tpm_wide.columns]
    return median_tpm_wide

def optimize_params(
    objective_function:FunctionType,
    initial_params:np.ndarray,
    adj_matrix:np.ndarray,
    initial_conditions:np.ndarray,
    time_points:np.ndarray,
    observed_data:pd.DataFrame
) -> OptimizeResult:
    result = minimize(objective_function, initial_params, args=(adj_matrix, initial_conditions, time_points, observed_data))
    return result

def integrate_model(
    gene_network_dynamics:FunctionType,
    initial_conditions:np.ndarray,
    time_points:np.ndarray,
    adj_matrix:np.ndarray,
    params:np.ndarray
):
    solution = odeint(gene_network_dynamics, initial_conditions, time_points, args=(adj_matrix, params))
    return solution

def transform_df(df):
    melted_df = pd.melt(df, id_vars=['Gene_ID', 'Gene_name'], var_name='contrast', value_name='value')
    melted_df[['contrast', 'measurement']] = melted_df['contrast'].str.rsplit('.', n=1, expand=True)

    reshaped_df = melted_df.pivot_table(index=['Gene_ID', 'Gene_name', 'contrast'], columns='measurement', values='value', dropna=False).reset_index()

    reshaped_df.columns.name = None  # Remove the axis name
    reshaped_df = reshaped_df.rename(columns={'log2foldchange': 'log2FoldChange', 'pvalue': 'pvalue'})

    return reshaped_df

def create_graphviz_graph(adj_matrix):
    graph = graphviz.Digraph()

    # Add nodes
    for node in adj_matrix.columns:
        graph.node(node)

    # Add edges with weights
    for i, row in adj_matrix.iterrows():
        for j, val in row.items():
            if val != 0:  # Include only non-zero weights
                graph.edge(i, j)

    return graph
