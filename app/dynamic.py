import streamlit as st
import pandas as pd
import numpy as np
import random
import lib
import matplotlib.pyplot as plt
import plotly.graph_objects as go


def dynamic_page():
    st.title("Dynamic modelling of TUNA knockdown")

    st.write("***")

    if not 'tpm' or not 'adjmat' or not 'metadata' or not 'hyp' in st.session_state:
        st.error("Please load the data first. Head to the home page, then come back here.")

    tpm = st.session_state.tpm
    adjmat = st.session_state.adjmat
    metadata = st.session_state.metadata
    hyp = st.session_state.hyp

    median_tpm = lib.calculate_median_tpm(tpm, metadata)
    module_genes = adjmat.index.tolist()
    genes = hyp.index.tolist()[0:10]

    time_points = np.arange(median_tpm.shape[1])

    with st.form('Model feature definition'):
        options = st.multiselect('Select genes to model', module_genes, genes)
        decay_rate = st.slider('Decay rate', 0.0, 1.0, 0.5)

        submitted = st.form_submit_button('Run model')

        if submitted:
            module_genes = options
            init_conditions = median_tpm.loc[module_genes].iloc[:, 0].values
            init_params = np.ones(len(module_genes)) * decay_rate

            result = lib.optimize_params(
                lib.objective_function,
                init_params,
                adjmat.values,
                init_conditions,
                time_points,
                median_tpm.loc[module_genes]
            )

            model_predictions = lib.integrate_model(
                lib.gene_network_dynamics,
                init_conditions,
                time_points,
                adjmat.values,
                result.x
            )

            st.write("***")

            st.write(f"Optimized decay rates: {result.x}")

            fig = go.Figure()

            # Add traces for observed and modeled data
            for i, gene in enumerate(module_genes):
                fig.add_trace(go.Scatter(x=time_points, y=median_tpm.loc[gene, :], mode='lines+markers', name=f'Observed {gene}', line=dict(dash='dash')))
                fig.add_trace(go.Scatter(x=time_points, y=model_predictions[:, i], mode='lines', name=f'Modeled {gene}'))

            # Update layout
            fig.update_layout(
                title=f'Model Fit for Module: Maroon',
                xaxis_title='Time',
                yaxis_title='Gene Expression (TPM)',
                legend_title='Legend',
                height=900
            )

            # Display the plot in Streamlit
            st.plotly_chart(fig)
