# Literature Synthesis Matrix (Single-Cell RNA-seq Study)

Every reference below is a real peer-reviewed publication verified via CrossRef (`tools/verify_citations.py`).

| Study | Scope | Key Finding / Best Practice | Relevance to Study |
|---|---|---|---|
| **Sade-Feldman et al. (2018)**, *Cell*, [10.1016/j.cell.2018.10.038](https://doi.org/10.1016/j.cell.2018.10.038) | scRNA-seq of 16,291 immune cells from melanoma checkpoint-therapy patients | Balance of effector/memory vs. exhausted CD8+ T-cell states predicts response to anti-PD-1 checkpoint blockade. | Directly motivates **H1** (CD8+ state expansion) and **H2** (cytotoxic vs. exhaustion transcriptional shift). |
| **Luecken & Theis (2019)**, *Molecular Systems Biology*, [10.15252/msb.20188746](https://doi.org/10.15252/msb.20188746) | Comprehensive scRNA-seq analysis best-practices tutorial | Establishes standard QC covariates (UMI count, detected genes, `%MT` fraction), normalization, and marker-based annotation workflows. | Guides our cell-level QC filter thresholds and diagnostic visualizations. |
| **Squair et al. (2021)**, *Nature Communications*, [10.1038/s41467-021-25960-2](https://doi.org/10.1038/s41467-021-25960-2) | Benchmark of single-cell differential expression methods across biological replicates | Cell-level DE tests treat cells as independent replicates and produce massive false discoveries; donor-level **pseudobulk** aggregation restores Type I error control. | Underpins **H2** and our Figure 2B pseudoreplication audit. |
| **Wolf et al. (2018)**, *Genome Biology*, [10.1186/s13059-017-1382-0](https://doi.org/10.1186/s13059-017-1382-0) | Scalable Python single-cell analysis (`Scanpy`) | Standardizes Python-native preprocessing, embedding, and marker visualization for scRNA-seq datasets. | Contextualizes how this lightweight NumPy/SciPy teaching benchmark scales directly to `Scanpy` / `AnnData`. |
| **Benjamini & Hochberg (1995)**, *JRSS-B*, [10.1111/j.2517-6161.1995.tb02031.x](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x) | Multiple-testing methodology | Controls false discovery rate (FDR) across transcriptome-wide tests. | Applied to all pseudobulk and cell-level DE comparisons. |
