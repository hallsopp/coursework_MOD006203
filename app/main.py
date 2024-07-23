import streamlit as st
import lib

# Define a function to load the data and set global variables
def initialize_data():
    if 'counts' not in st.session_state or 'deg' not in st.session_state:
        with st.spinner("Loading data..."):
            deg, counts = lib.load_data()
            st.session_state.counts = counts
            st.session_state.deg = deg
        st.success("Data loaded successfully!")

def home():
    st.title("Analysis of LincRNA *TUNA* Knock-down in MESCs")
    initialize_data()

    counts = st.session_state.counts
    deg = st.session_state.deg

    st.write("### Differential Expressed Genes (DEGs)")
    st.data_editor(deg)

    st.write("### Count Data")
    st.data_editor(counts)

def eda():
    st.title("Weighted Gene Co-expression Network Analysis (WGCNA)")

    if 'counts' not in st.session_state or 'deg' not in st.session_state:
        st.error("Data not loaded. Please go to the Home page and load the data first.")
        return

    counts = st.session_state.counts
    deg = st.session_state.deg



pg = st.navigation([
    st.Page(home, title="Home", icon="🔥"),
    st.Page(eda, title="WGCNA", icon="📊")
])
pg.run()
