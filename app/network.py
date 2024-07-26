import streamlit as st
import lib

def network_page():
    st.title("Network Analysis")

    if not 'adjmat' or not 'hyp' in st.session_state:
        st.error("Please load the data first. Head to the home page, then come back here.")

    adjmat = st.session_state.adjmat
    hyp = st.session_state.hyp

    st.write(
        """
        ***
        After identifying the modules of co-expressed genes using the WGCNA analysis, we can now examine \
        the network structure of these modules. In order to do this, the modules adjacency matrices \
        were used to construct visual graphs using the `PyWGCNA` package.

        The function `CoexpressionModulePlot` was used to generate the network plots, this function plots the top 10 \
        genes with the highest connectivity and betweeness centrality in their individual networks. The function also highlights \
        the genes that are present in both modules, and the edges between them.

        ***
        """
    )

    st.code(
        """
        floralwhite_maroon = tuna_kd_wgcna.CoexpressionModulePlot(modules=['floralwhite', 'maroon'])
        maroon_gainsboro = tuna_kd_wgcna.CoexpressionModulePlot(modules=['gainsboro', 'maroon'])
        floralwhite_gainsboro = tuna_kd_wgcna.CoexpressionModulePlot(modules=['floralwhite', 'gainsboro'])
        """
    )

    st.write(
        """
        ***

        #### Floralwhite and Maroon
        """
    )
    st.image("data/wgcna/figures/network/floralwhite_maroon.png")
    st.write(
        """
        Here, both the floralwhite and maroon modules had a positive correlation with expression across time, \
        so unsurprisingly, the network shows a degree of connectivity between the two modules. The nodes \
        Pdk1, Wls and Vezf1 have high measures of connectivity and betweeness, which potentially suggests \
        that they are the upstream regulators of the modules, and are more directly impacted by the knockdown of \
        the *TUNA* non-coding RNA.
        """
    )

    st.write(
        """
        ***

        #### Maroon and Gainsboro
        """
    )
    st.image("data/wgcna/figures/network/maroon_gainsboro.png")
    st.write(
        """
        Here, maroon and gainsboro had opposite corellations with expression across time, so the network \
        shows less connectivity, but still some overlapping. With Plk2 showing high connectivity and betweeness, \
        it could account for the small subset of genes that were actually negatively correlated with treatment that \
        appeared in the maroon module.
        """
    )

    st.write(
        """
        ***

        #### floralwhite (right) and Gainsboro (left)
        """
    )
    st.image("data/wgcna/figures/network/floralwhite_gainsboro.png")
    st.write(
        """
        Here, floralwhite and gainsboro had opposite corellations with expression across time, so the network \
        also shows less connectivity, but still some overlapping. Here, Arap2 and Tor1aip2 seem to form a bridge \
        between the two modules, and could be potential targets for further investigation.

        ***
        """
    )

    st.subheader("Maroon module network")
    st.write(
        """
        We can plot the top 20 hub genes for `maroon` as their own network using the [Graphvis](https://graphviz.org/) \
        package.

        *Too many genes make the webserver crash, otherwise the entire module could have been plotted! If the graphs \
        are not showing, please close the tab and open a new one. I am not sure why...*

        ***
        """
    )

    st.dataframe(hyp.drop(columns=['gene_name', 'gene_biotype']))

    genes = hyp.index.tolist()
    to_genes = adjmat.loc[genes, genes]

    graph_1 = lib.create_graphviz_graph(to_genes)

    st.graphviz_chart(graph_1.source)

    st.write(
        """
        ***

        The top connectivity genes include *Wls* and *Perp*, we can remove them from the network to see how it changes:
        """
    )

    genes = hyp.index.tolist()[2:]
    to_genes = adjmat.loc[genes, genes]

    graph = lib.create_graphviz_graph(to_genes)

    st.graphviz_chart(graph.source)

    st.write(
        """
        There is not an awful lot of change in the network structure, which suggests that the top 2 genes are \
        not the only ones that are important in the network. This is a good sign, as it suggests that the network \
        is robust to perturbations in the top genes. \

        But it is also important to consider that these are just the top 20 hub genes and their connections to each other. \
        The full network would be much larger and more complex, and would likely have higher levels of instability from removing \
        the top genes.
        """
    )
