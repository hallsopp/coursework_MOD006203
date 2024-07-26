import streamlit as st
import pandas as pd
import numpy as np
import random
import lib
import matplotlib.pyplot as plt
import plotly.graph_objects as go


def dynamic_page():
    st.title("Dynamic modelling of TUNA knockdown")

    st.write(
        """
        ***
        Now that the coexpression network has been identified and the modules constructed, the dynamic modelling of \
        gene expression changes over time can be examined. To do this, the `maroon` module will be used with \
        the objective of predicting the gene expression changes over time for the genes in this module. The model \
        built is a simple logistic growth/decay model (considering network edge weights/interactions), where the rate \
        of decay is optimised to fit the observed data. \
        This is because of the observations made in the WGCNA analysis, where the genes in the module \
        were observed to be up-regulated over time, and we make the assumption that the expression will eventually \
        decay to a steady state.

        The model could be used to predict how the module reacts to different perturbations, such as gene knockdowns, \
        or other treatments.

        ***
        """
    )

    st.write(
        """
        The function to differentiate the gene expression changes over time is as follows:
        """
    )
    st.code(
        """
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
        """
    )

    st.write(
        """
        The objective function to optimise the parameters using squared error loss is as follows:
        """
    )
    st.code(
        """
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
        """
    )

    st.write(
        """
        Then the optimisation and integration functions are defined as follows:
        """
    )
    st.code(
        """
        def optimise_params(
            objective_function:FunctionType,
            initial_params:np.ndarray,
            adj_matrix:np.ndarray,
            initial_conditions:np.ndarray,
            time_points:np.ndarray,
            observed_data:pd.DataFrame
        ) -> OptimizeResult:
            result = minimise(objective_function, initial_params, args=(adj_matrix, initial_conditions, time_points, observed_data))
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
        """
    )

    st.write(
        """
        ***

        The initial conditions for the model are the median TPM values for the genes in the module at the first time point \
        (day 2 control). \

        The model is then optimized to fit the observed data by minimising the squared error loss between the observed \
        and modeled data. The optimised decay rates are then used to predict the gene expression changes over time for the \
        genes in the module. \

        Initially, the model is built with only the top 10 genes in the module. The user can then select additional genes to \
        include in the model and adjust the decay rate, carrying capacity, and maximum number of days \
        to see how the model predictions change.

        ***
        """
    )

    if not 'tpm' or not 'adjmat' or not 'metadata' or not 'hyp' in st.session_state:
        st.error("Please load the data first. Head to the home page, then come back here.")

    tpm = st.session_state.tpm
    adjmat = st.session_state.adjmat
    metadata = st.session_state.metadata
    hyp = st.session_state.hyp

    median_tpm = lib.calculate_median_tpm(tpm, metadata)
    module_genes = adjmat.index.tolist()
    genes = hyp.index.tolist()[0:10]

    observed_time_points = np.arange(median_tpm.shape[1])

    with st.form('Model feature definition'):
        options = st.multiselect('Select genes to model', module_genes, genes)
        decay_rate = st.slider('Decay rate', 0.0, 1.0, 0.5)
        carrying_capacity = st.slider('Carrying capacity (maximum gene expression value)', 0.1, 100.0, 10.0)
        num_days = st.number_input('Number of days to predict', min_value=1, max_value=30, value=7)

        submitted = st.form_submit_button('Run model')

        if submitted:
            module_genes = options
            init_conditions = median_tpm.loc[module_genes].iloc[:, 0].values
            init_params = np.concatenate([np.ones(len(module_genes)) * decay_rate, np.ones(len(module_genes)) * carrying_capacity])
            time_points = np.linspace(0, num_days, num_days + 1)

            result = lib.optimize_params(
                lib.objective_function,
                init_params,
                adjmat.values,
                init_conditions,
                observed_time_points,
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

            st.write(f"Optimised decay rates: {result.x}")

            fig = go.Figure()

            # Add traces for observed and modeled data
            for i, gene in enumerate(module_genes):
                fig.add_trace(go.Scatter(x=time_points, y=median_tpm.loc[gene, :], mode='lines+markers', name=f'Observed {gene}', line=dict(dash='dash')))
                fig.add_trace(go.Scatter(x=time_points, y=model_predictions[:, i], mode='lines', name=f'Modelled {gene}'))

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
