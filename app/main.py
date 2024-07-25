import streamlit as st
import pandas as pd
import lib
import stats
import wgcna
import dynamic

def home():
    st.set_page_config(layout="wide")
    st.title("Analysis of LincRNA *TUNA* Knock-down in MESCs")

    lib.initialize_data()

    counts = st.session_state.counts
    deg = st.session_state.deg
    tpm = st.session_state.tpm

    st.write("### Differentially Expressed Genes (DEGs)")
    st.data_editor(deg)

    st.write("### Count Data")
    st.data_editor(counts)

pg = st.navigation([
    st.Page(home, title="Home", icon="🏠"),
    st.Page(wgcna.wgcna_page, title="WGCNA", icon="📊"),
    st.Page(stats.stats_page, title="Statistical Modelling", icon="📊"),
    st.Page(dynamic.dynamic_page, title="Dynamic Modelling", icon="📊")
])
pg.run()
