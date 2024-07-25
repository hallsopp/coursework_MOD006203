import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

def wgcna_page():
    st.title("Weighted Gene Co-expression Network Analysis (WGCNA)")

    st.write("***")
    st.caption(
        """
        PyWGCNA was not run on this webserver, it was run on a machine with enough RAM. \
        The following figures are saved locally and displayed here.
        """
    )

    st.subheader("Sample heirarchical clustering for outlier detection")
    pdf_viewer("data/wgcna/figures/sample_clustering_cleaning.pdf", width = 1000)

    st.subheader("Scale-free network power estimation")
    pdf_viewer("data/wgcna/figures/summary_power.pdf", width = 800)

    st.write("***")

    st.subheader("Module relationships")
    pdf_viewer("data/wgcna/figures/eigenesgenes.pdf", width = 1000)

    st.subheader("Module-trait relationships")
    pdf_viewer("data/wgcna/figures/module-traitRelationships.pdf", width = 2000)

    st.subheader("Modules with significant correlation with Day + Treatment")
    st.write("##### Maroon (upregulated)")
    pdf_viewer("data/wgcna/figures/module_heatmap_eigengene_maroon.pdf", width = 700)

    st.write("##### Floralwhite (upregulated)")
    pdf_viewer("data/wgcna/figures/module_heatmap_eigengene_floralwhite.pdf", width = 700)

    st.write("##### Gainsboro (downregulated)")
    pdf_viewer("data/wgcna/figures/module_heatmap_eigengene_gainsboro.pdf", width = 700)
