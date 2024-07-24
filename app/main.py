import streamlit as st
import lib

# Define a function to load the data and set global variables
def initialize_data():
    if 'counts' not in st.session_state or 'deg' not in st.session_state or 'tpm' not in st.session_state:
        with st.spinner("Loading data..."):
            deg, counts, tpm = lib.load_data()
            st.session_state.counts = counts
            st.session_state.deg = deg
            st.session_state.tpm = tpm
        st.success("Data loaded successfully!")

def home():
    st.title("Analysis of LincRNA *TUNA* Knock-down in MESCs")
    initialize_data()

    counts = st.session_state.counts
    deg = st.session_state.deg
    tpm = st.session_state.tpm

    st.write("### Differentially Expressed Genes (DEGs)")
    st.data_editor(deg)

    st.write("### Count Data")
    st.data_editor(counts)

def wgcna():
    st.title("Weighted Gene Co-expression Network Analysis (WGCNA)")

    if 'tpm' not in st.session_state:
        st.error("Data not loaded. Please go to the Home page and load the data first.")
        return

    tpm = st.session_state.tpm

    wgcna = lib.init_wgcna(tpm)

    st.write("### WGCNA Analysis")
    st.write("#### Step 1: Data Preprocessing")
    st.dataframe(wgcna.geneExpr.to_df().head())


    if st.button("Preprocess data"):
        with st.spinner("Preprocessing data..."):
            wgcna.preprocess()

pg = st.navigation([
    st.Page(home, title="Home", icon="🔥"),
    st.Page(wgcna, title="WGCNA", icon="📊")
])
pg.run()
