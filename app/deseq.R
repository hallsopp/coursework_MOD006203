# Load the DESeq2 library
library(DESeq2)
library(tibble)
library(dplyr)

# Load the raw count data
raw_data <- read.table("data/E-GEOD-46730-raw-counts.txt", header = TRUE, row.names = 1)
gene_data <- read.table("data/mart_export.txt", header = TRUE, fill = TRUE) %>%
    mutate(Gene_name = ifelse(Gene_name == "" | is.na(Gene_name), Gene_stable_ID, Gene_name)) %>%
    rename(Gene_ID = Gene_stable_ID)

# Create the design matrix
design_matrix <- data.frame(
    sample = c("SRR847690", "SRR847691", "SRR847692", "SRR847693", "SRR847694", "SRR847695", "SRR847696", "SRR847697", "SRR847698", "SRR847699", "SRR847700", "SRR847701"),
    time = c("day_2", "day_2", "day_2", "day_2", "day_2", "day_2", "day_4", "day_4", "day_4", "day_6", "day_6", "day_6"),
    treatment = c("control", "control", "control", "treated", "treated", "treated", "treated", "treated", "treated", "treated", "treated", "treated")
)

design_matrix$time <- factor(design_matrix$time)
design_matrix$treatment <- factor(design_matrix$treatment)

design_matrix$group <- factor(paste(design_matrix$time, design_matrix$treatment, sep = "_"))

# Convert to DESeq2 dataset
dds <- DESeqDataSetFromMatrix(
    countData = raw_data,
    colData = design_matrix,
    design = ~group
)

dds$group <- relevel(dds$group, ref = "day_2_control")

# Run the DESeq2 analysis
dds <- DESeq(dds)

# Perform contrasts and add the contrast information to each result
contrast_day2 <- results(dds, contrast = c("group", "day_2_treated", "day_2_control"))
contrast_day2$contrast <- "day_2_treated_vs_day_2_control"

contrast_day4 <- results(dds, contrast = c("group", "day_4_treated", "day_2_control"))
contrast_day4$contrast <- "day_4_treated_vs_day_2_control"

contrast_day6 <- results(dds, contrast = c("group", "day_6_treated", "day_2_control"))
contrast_day6$contrast <- "day_6_treated_vs_day_2_control"

# Combine results into one dataframe
all_results <- rbind(
    as.data.frame(contrast_day2),
    as.data.frame(contrast_day4),
    as.data.frame(contrast_day6)
)

new_col <- rownames_to_column(all_results, var = "Gene_ID")

combined_results <- left_join(new_col, gene_data, by = "Gene_ID")

# Save the combined results to a file
write.table(combined_results, file = "data/DESeq2_combined_results.txt", quote = FALSE, row.names = FALSE, sep = "\t")
