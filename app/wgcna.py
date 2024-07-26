import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

def wgcna_page():
    st.title("Weighted Gene Co-expression Network Analysis (WGCNA)")

    st.write(
        """
        ***

        [WGCNA](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-9-559) is a systems \
        biology method used to describe correlation patterns among genes using normalised expression data. \

        In order to run WGCNA, the *TUNA* knock-down samples had to be in this normalised format. Therefore, \
        the supplementary Transcript per Million (TPM) data was used, found \
        [here](https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE46730&format=file&file=GSE46730%5FRNA%2Dseq%2DNianwei%2Etxt%2Egz).
        A preprocessing step was performed to replace the sample names with the correct identifiers.

        [PyWGCNA](https://mortazavilab.github.io/PyWGCNA/html/index.html) was not run on this webserver, it was run \
        on a machine with enough RAM. The following figures are saved locally and displayed here. You can find the \
        raw copies in the `data/wgcna/figures` folder.

        ***
        """
    )

    st.write(
        """
        In order to run the WGCNA analysis, the following function was called using the TPM data as input. The function \
        initialises a `PyWGCNA.WGCNA` object (hereafter referred to as `tuna_kd_wgcna`), preprocesses the data, and finds \
        the modules of co-expressed genes.
        """
    )
    st.code(
        """
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
        """,
        language="python"
    )
    st.write("***")

    st.subheader("Sample heirarchical clustering for outlier detection")
    st.write("The preprocessing step in WGCNA includes the removal of outliers. The following figure shows the sample clustering:")
    pdf_viewer("data/wgcna/figures/sample_clustering_cleaning.pdf", width = 1000)
    st.write(
        """
        The samples in the dendrogram, from left to right, are:
            Day 2 control (3 replicates),
            Day 2 TUNA_kd (3 replicates),
            Day 4 TUNA_kd (3 replicates),
            Day 6 TUNA_kd (3 replicates). \

        As evident by the heirarchical clustering, the samples are grouped by time-point and then by treatment. There are no \
        obvious outliers in the dataset.

        During this step, genes with low variance were also removed.

        ***
        """
    )

    st.subheader("Scale-free network power estimation")
    st.write("The first step for finding modules is to estimate the power of the network. The following figure shows the power estimation:")
    pdf_viewer("data/wgcna/figures/summary_power.pdf", width = 800)
    st.write(
        """
        As evident, a soft-thresholding power of 10 returns the highest correlation between the gene-gene interactions in the graph \
        adjacency matrix and ensures a scale-free network. This power was then used to calculate the adjancency and overlap matrices.

        ***
        """
    )

    st.subheader("Module relationships")
    st.write("The following figure shows the module relationships after constructing the graph and identifying communities (modules):")
    pdf_viewer("data/wgcna/figures/eigenesgenes.pdf", width = 1000)
    st.write(
        """
        The dendrogram shows the modules of co-expressed genes, and how overlapping, or closely related, they are. \
        The modules are named by colours. The module eigengenes are then correlated with the traits of interest. \

        The module eigengene is a single synthetic gene that summarizes the expression pattern of all the genes in the module. \
        It is essentially a weighted average of the gene expression profiles in the module, with weights determined by Principle \
        Component Analysis (PCA).

        ***
        """
    )

    st.write(
        """
        In order to correlate the module expression with traits of interest, the sample metadata must be added, along \
        with gene annotations. The following functions were called to add the metadata and annotations to the `tuna_kd_wgcna` object:
        """
    )
    st.code(
        """
        geneList = PyWGCNA.getGeneList(dataset='mmusculus_gene_ensembl',
                                       attributes=['ensembl_gene_id',
                                                   'external_gene_name',
                                                   'gene_biotype'],
                                       maps=['gene_id', 'gene_name', 'gene_biotype'])

        design_matrix = pd.DataFrame({
            'sample': ["SRR847690", "SRR847691", "SRR847692", "SRR847693", "SRR847694", "SRR847695", "SRR847696", "SRR847697", "SRR847698", "SRR847699", "SRR847700", "SRR847701"],
            'time': ["day2", "day2", "day2", "day2", "day2", "day2", "day4", "day4", "day4", "day6", "day6", "day6"],
            'treatment': ["control", "control", "control", "treated", "treated", "treated", "treated", "treated", "treated", "treated", "treated", "treated"]
        })
        design_matrix.set_index('sample', inplace=True)

        tuna_kd_wgcna.updateSampleInfo(sampleInfo=design_matrix)
        tuna_kd_wgcna.updateGeneInfo(geneList)

        # Define a color mapping for 'time'
        tuna_kd_wgcna.metadataColors['time'] = {'day2': 'green', 'day4': 'yellow', 'day6': 'blue'}
        # Define a color mapping for 'treatment'
        tuna_kd_wgcna.metadataColors['treatment'] = {'treated': 'purple', 'control': 'red'}
        """,
        language="python"
    )
    st.write("The module analysis was then called using:")
    st.code(
        """
        tuna_kd_wgcna.analyseWGCNA()
        """,
        language="python"
    )
    st.write("***")

    st.subheader("Module-trait relationships")
    st.write("The following figure shows the module-trait relationships:")
    pdf_viewer("data/wgcna/figures/module-traitRelationships.pdf", width = 2000)
    st.write(
        """
        The heatmap shows the correlation between the module eigengenes and the traits of interest. The correlation is \
        calculated using Pearson's correlation coefficient. The modules with significant correlation with the traits \
        are then selected for further analysis.

        In this case, the `maroon` and `floralwhite` modules show a high, positive correlation with treatment across time. \
        And the `gainsboro` module shows a high, negative correlation with treatment across time.

        ***
        """
    )

    st.subheader("Modules with significant correlation with Day + Treatment")
    st.write("##### Maroon (upregulated)")
    pdf_viewer("data/wgcna/figures/module_heatmap_eigengene_maroon.pdf", width = 700)
    st.write(
        """
        The maroon module shows a high, positive correlation with treatment across time. The module eigengene expression \
        is higher in the treated samples compared to the control samples, even on the same day (day 2), and there is a linear \
        increase in expression with time across days 4 and 6.

        The bottom panel shows a heatmap of the TPM values of the individual genes in the module. Here it is also evident that the \
        intensity increases from left to right (day 2 to day 6). However, there is a cluster of genes that appear to behave in the\
        opposite manner, with higher expression on the second day.

        ***
        """
    )

    st.write("##### Floralwhite (upregulated)")
    pdf_viewer("data/wgcna/figures/module_heatmap_eigengene_floralwhite.pdf", width = 700)
    st.write(
        """
        The floralwhite module also shows a high, positive correlation with treatment across time (slight exception with \
        day 6, where the eigengene expression is lowering/plateauing).

        The heatmap of the individual gene expression shows a similar pattern to the maroon module.

        ***
        """
    )

    st.write("##### Gainsboro (downregulated)")
    pdf_viewer("data/wgcna/figures/module_heatmap_eigengene_gainsboro.pdf", width = 700)
    st.write(
        """
        The gainsboro module shows a high, negative correlation with treatment across time. The module eigengene expression \
        remains relatively constant across day 2 treated and control, but then decreases with time across days 4 and 6, \
        indicating a delayed response to treatment.

        ***
        """
    )

    st.write(
        """
        Next, the modules and their corresponding genes and graphs are saved as a `pickle` file. \
        The `maroon` module is selected for dynamic and network analysis, and it's adjancency matrix is saved as a `csv` file.
        """
    )
    st.code(
        """
        tuna_kd_wgcna.saveWGCNA()

        maroon_genes = tuna_kd_wgcna.getGeneModule('maroon')['maroon']
        maroon_adjmat = tuna_kd_wgcna.adjacency.loc[maroon_genes, maroon_genes].to_csv('data/wgcna/figures/maroon_adjmat.csv')
        hub_genes = tuna_kd_wgcna.top_n_hub_genes(moduleName='maroon', n=20).to_csv('data/wgcna/figures/top_20_hub_genes_maroon.csv')
        """,
        language="python"
    )
