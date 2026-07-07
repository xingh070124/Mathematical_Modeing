# Single-Cell Genomics & Transcriptomics Methods — Writing Pattern Extracts

Category: scRNA-seq / scATAC-seq / spatial omics / foundation models for cells.
Six open-access papers (2021-2025) across Nature, Nature Methods, Nature Communications.

Note on swap: scGPT (Nature Methods 2024) was attempted as candidate #6 but the publisher version returned redirect/auth errors and the bioRxiv mirror returned 403. It was swapped for **CellFM** (Nature Communications 2025), an open-access foundation-model paper with closely matching scope.

---

## Paper 1: Theodoris et al., "Transfer learning enables predictions in network biology" (Geneformer)
- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC10949956/  (publisher: https://www.nature.com/articles/s41586-023-06139-9)
- journal: Nature
- year: 2023
- category: methods

A1_title: "Transfer learning enables predictions in network biology"

A2_abstract_map:
  - s1 [GAP]: "Mapping gene networks requires large amounts of transcriptomic data… which impedes discoveries in settings with limited data…"
  - s2 [BIG-PICTURE]: "Recently, transfer learning has revolutionized fields such as natural language understanding and computer vision by leveraging deep learning models pretrained on large-scale general datasets…"
  - s3 [HERE-WE]: "Here, we developed a context-aware, attention-based deep learning model, Geneformer, pretrained on a large-scale corpus of ~30 million single cell transcriptomes…"
  - s4 [KEY-RESULT]: "During pretraining, Geneformer gained a fundamental understanding of network dynamics, encoding network hierarchy in the model's attention weights in a completely self-supervised manner."
  - s5 [VALIDATION]: "Fine-tuning towards a diverse panel of downstream tasks… demonstrated that Geneformer consistently boosted predictive accuracy."
  - s6 [VALIDATION]: "Applied to disease modeling with limited patient data, Geneformer identified candidate therapeutic targets for cardiomyopathy."
  - s7 [IMPLICATION]: "Overall, Geneformer represents a pretrained deep learning model from which fine-tuning towards a broad range of downstream applications can be pursued…"

A3_here_we_pivot: "Here, we developed a context-aware, attention-based deep learning model, Geneformer, pretrained on a large-scale corpus of ~30 million single cell transcriptomes…"
A4_strongest_quant_in_abstract: "pretrained on a large-scale corpus of ~30 million single cell transcriptomes"

B1_intro_hook_style: biological-motivation
B1_quote_sentence1: "Mapping the gene regulatory networks that drive disease progression enables screening for molecules that correct the network by normalizing core regulatory elements…"
B3_gap_phrases: ["However, mapping the gene network architecture requires large amounts of transcriptomic data…", "which impedes network-correcting drug discovery in settings with limited data", "Although data remains limited in these settings…"]
B4_pivot_first2sent: "Here, we developed a context-aware, attention-based deep learning model, Geneformer, pretrained on large-scale transcriptomic data to enable predictions in settings with limited data. We assembled a large-scale pretraining corpus, Genecorpus-30M…"
B5_contributions: "We then pretrained Geneformer on this corpus using a self-supervised masked learning objective… Furthermore, fine-tuning Geneformer towards a diverse panel of downstream tasks… demonstrated that Geneformer consistently boosted predictive accuracy."
B6_last_intro_sentence: "Overall, Geneformer represents a pretrained deep learning model from which fine-tuning towards a broad range of downstream applications can be pursued to accelerate discovery of key network regulators and candidate therapeutic targets."

C1_results_headers: ["Geneformer architecture and pretraining", "Context-awareness and batch integration", "Gene dosage sensitivity predictions", "Chromatin dynamics predictions", "Network dynamics predictions", "Pretraining encoded network hierarchy", "In silico gene network analysis", "In silico treatment analysis"]
C2_header_style: task-neutral (mostly noun phrases naming the task; one declarative-finding: "Pretraining encoded network hierarchy")
C3_section_openers:
  - {header: "Geneformer architecture and pretraining", quote: "Geneformer is a context-aware, attention-based deep learning model pretrained on large-scale transcriptomic data to enable predictions in network biology…", class: method-first}
  - {header: "Context-awareness and batch integration", quote: "For each single cell transcriptome presented to Geneformer, the model embeds each gene into a 256-dimensional space…", class: method-first}
  - {header: "Gene dosage sensitivity predictions", quote: "We next tested whether Geneformer could boost predictions with limited data in a diverse set of downstream fine-tuning applications.", class: motivation-first}
  - {header: "Chromatin dynamics predictions", quote: "Bivalent chromatin structure is known to mark key developmental genes in embryonic stem cells (ESCs)…", class: motivation-first}
  - {header: "Network dynamics predictions", quote: "Determining the hierarchy in gene networks enables the design of therapies targeting normalization of core regulatory elements…", class: motivation-first}
  - {header: "Pretraining encoded network hierarchy", quote: "To investigate how the model was learning network dynamics during the pretraining stage, we examined the pretrained Geneformer attention weights.", class: motivation-first}
  - {header: "In silico gene network analysis", quote: "Given the gene embeddings reflect the joint output of the attention weights of the network, we tested whether the pretrained Geneformer already encoded network connections…", class: motivation-first}
  - {header: "In silico treatment analysis", quote: "We next tested whether our in silico perturbation strategy could be applied to model human disease and reveal candidate therapeutic targets.", class: motivation-first}
C4_figure_callouts: ["as shown in Fig. 1", "as indicated in Extended Data Fig.", "demonstrated in Fig. 2"]
C5_quant_with_stats: "AUC 0.91" / "AUC 0.93"
C6_baseline_comparison: "near random" (used to characterize alternative methods); "significantly larger effect than"
C7_robustness_phrase: "We next tested whether…", "To investigate whether…", "To rule out…"
C8_generalization_phrase: "Fine-tuning towards a diverse panel of downstream tasks… demonstrated that Geneformer consistently boosted predictive accuracy."

D1_discussion_open: "In sum, we developed a context-aware deep learning model, Geneformer, pretrained on large-scale transcriptomic data to enable predictions in settings with limited data."
D2_limitation: —
D3_outlook: "In silico treatment analysis using limited data may thus enable therapeutic discovery in innumerable diseases that have been previously impeded by limited data due to being rare or affecting clinically inaccessible tissue."
D4_paper_closing_sentence: "Overall, Geneformer represents a pretrained deep learning model whose fundamental understanding of network dynamics can now be democratized to a broad range of downstream applications to accelerate discovery of key network regulators and candidate therapeutic targets in settings with limited data."

G1_hedges_used: [suggest, may, can, demonstrated, consistent, supports]
G2_strong_verbs: [develop, pretrain, enable, boost, identify, reveal, accelerate, democratize]
G3_paragraph_connectives: ["We next tested whether…", "Furthermore", "Notably", "Interestingly", "Overall"]
G4_taken_together: "Together, these results show…" (used in similar form throughout)

notable: Opens "In sum" in Discussion (instead of standard "In summary"); ends Introduction by literally previewing each Result paragraph's headline finding — the intro is essentially a verbal table of contents.

---

## Paper 2: Heimberg et al., "A cell atlas foundation model for scalable search of similar human cells" (SCimilarity)
- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC11864978/  (publisher: https://www.nature.com/articles/s41586-024-08411-y)
- journal: Nature
- year: 2024
- category: methods

A1_title: "A cell atlas foundation model for scalable search of similar human cells"

A2_abstract_map:
  - s1 [BIG-PICTURE]: "Single-cell RNA sequencing has profiled hundreds of millions of human cells across organs, diseases, development and perturbations to date."
  - s2 [GAP/PROMISE]: "Mining these growing atlases could reveal cell–disease associations, identify cell states in unexpected tissue contexts and relate in vivo biology to in vitro models."
  - s3 [HERE-WE]: "Here we develop SCimilarity, a metric-learning framework to learn a unified and interpretable representation that enables rapid queries of tens of millions of cell profiles…"
  - s4 [KEY-RESULT]: "We use SCimilarity to query a 23.4-million-cell atlas of 412 single-cell RNA-sequencing studies for macrophage and fibroblast profiles from interstitial lung disease…"
  - s5 [VALIDATION]: "The top scoring in vitro hit for the macrophage query was a 3D hydrogel system, which we experimentally demonstrated reproduces this cell state."
  - s6 [IMPLICATION]: "SCimilarity serves as a foundation model for single-cell profiles that enables researchers to query for similar cellular states across the human body…"

A3_here_we_pivot: "Here we develop SCimilarity, a metric-learning framework to learn a unified and interpretable representation that enables rapid queries of tens of millions of cell profiles…"
A4_strongest_quant_in_abstract: "we use SCimilarity to query a 23.4-million-cell atlas of 412 single-cell RNA-sequencing studies"

B1_intro_hook_style: field-importance
B1_quote_sentence1: "Over 100 million individual cells have been profiled using single-cell (scRNA-seq) or single-nucleus (snRNA-seq) RNA-sequencing analysis…"
B3_gap_phrases: ["Despite this promise and rapid data growth, current models were not designed to search for similar cell profiles in massive corpora", "are hampered by challenges in dataset curation and harmonization", "no methods to search for complete cell profiles"]
B4_pivot_first2sent: "Here we introduce SCimilarity—a deep-metric-learning foundation model that quantifies similarity between single-cell profiles and provides a single-cell reference to query for comparable cell states across tissues and diseases."
B5_contributions: "We illustrate the power of SCimilarity by searching a learned reference of 23.4 million cells with query profiles of macrophage and fibroblast subsets from interstitial lung disease (ILD)…"
B6_last_intro_sentence: "…showing how SCimilarity provides a powerful framework for scalable cell search across organs, systems and conditions to generate biological insights and experimentally testable hypotheses from the Human Cell Atlas."

C1_results_headers: ["A similarity metric for scRNA-seq", "Training on a large, diverse atlas", "Loss functions for sensitive cell search", "Generalization across platforms", "Integration without batch correction", "Cell type matching through similarity", "Interpretable features drive SCimilarity", "Cell search across tissues and diseases", "Important FM features match known signatures", "Search for ex vivo human cell model"]
C2_header_style: mixed (task-neutral plus declarative-finding: "Interpretable features drive SCimilarity"; "Important FM features match known signatures")
C3_section_openers:
  - {header: "A similarity metric for scRNA-seq", quote: "SCimilarity blends unsupervised representation learning and supervised metric learning through simultaneously optimizing two objectives…", class: method-first}
  - {header: "Training on a large, diverse atlas", quote: "To test the SCimilarity framework, we aggregated sc/snRNA-seq datasets across human biology.", class: motivation-first}
  - {header: "Loss functions for sensitive cell search", quote: "Testing 18 different parameter combinations for SCimilarity's objective function… revealed that the two loss function components gave rise to different model behaviours.", class: claim-first}
  - {header: "Generalization across platforms", quote: "SCimilarity was trained on both scRNA-seq and scRNA-seq studies and embeds both data types well…", class: claim-first}
  - {header: "Integration without batch correction", quote: "SCimilarity quantifies a confidence level for each cell's representation…", class: method-first}
  - {header: "Cell type matching through similarity", quote: "SCimilarity annotated query cell types by finding the cells in the annotated reference that are most similar to their profiles.", class: method-first}
  - {header: "Interpretable features drive SCimilarity", quote: "To probe SCimilarity's model and annotations, we quantified the importance of each gene for each cell type using Integrated Gradients…", class: motivation-first}
  - {header: "Cell search across tissues and diseases", quote: "We used SCimilarity's embedding to query for cells across the 23.4-million-cell reference…", class: method-first}
  - {header: "Important FM features match known signatures", quote: "We hypothesized that SCimilarity's detection of FM-like cells across ILD studies reflects a shared biological state…", class: motivation-first}
  - {header: "Search for ex vivo human cell model", quote: "Researching the role of novel cell states like FMs in disease requires modelling, perturbing and studying them in vitro, but identifying culture conditions remains challenging.", class: motivation-first}
C4_figure_callouts: ["as demonstrated for", "as shown in", "revealing similar cell profiles", "providing a powerful framework"]
C5_quant_with_stats: —
C6_baseline_comparison: "substantially more correlated with", "significantly outperforming", "comparable to"
C7_robustness_phrase: "we next asked", "to rule out", "As a negative control", "As a case study", "To validate"
C8_generalization_phrase: "As SCimilarity can generalize to cells and datasets not seen in the training, cell profiles can be filtered or added without recomputing the existing embeddings."

D1_discussion_open: "SCimilarity offers a unique approach based on metric learning for cell searches across hundreds of studies, thousands of samples and tens of millions (and more) of cells."
D2_limitation: "Nevertheless, users should always interpret cross-technology integrations with care."
D3_outlook: "The strong performance of SCimilarity's learned representation for both the integration and querying tasks may suggest that it can perform well for other tasks, but these need to be assessed in future studies."
D4_paper_closing_sentence: "The strong performance of SCimilarity's learned representation for both the integration and querying tasks may suggest that it can perform well for other tasks, but these need to be assessed in future studies."

G1_hedges_used: [may, suggest, can, hypothesized, although, nevertheless]
G2_strong_verbs: [develop, query, embed, generalize, enable, demonstrate, reveal]
G3_paragraph_connectives: ["we next asked", "To validate", "As a case study", "To rule out"]
G4_taken_together: —

notable: Discussion ends on a hedged "may suggest…but these need to be assessed in future studies" — unusually self-limiting closing for a Nature paper. Headers mix declarative claims with task-neutral phrasing in the same Results section.

---

## Paper 3: Biancalani et al., "Deep learning and alignment of spatially resolved single-cell transcriptomes with Tangram"
- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC8566243/  (publisher: https://www.nature.com/articles/s41592-021-01264-7)
- journal: Nature Methods
- year: 2021
- category: methods

A1_title: "Deep learning and alignment of spatially resolved single-cell transcriptomes with Tangram"

A2_abstract_map:
  - s1 [BIG-PICTURE]: "Charting an organs' biological atlas requires us to spatially resolve the entire single-cell transcriptome, and to relate such cellular features to the anatomical scale."
  - s2 [GAP]: "Single-cell and single-nucleus RNA-seq (sc/snRNA-seq) can profile cells comprehensively, but lose spatial information."
  - s3 [GAP]: "Spatial transcriptomics allows for spatial measurements, but at lower resolution and with limited sensitivity."
  - s4 [GAP]: "Targeted in situ technologies solve both issues, but are limited in gene throughput."
  - s5 [HERE-WE]: "To overcome these limitations we present Tangram, a method that aligns sc/snRNA-seq data to various forms of spatial data collected from the same region…"
  - s6 [GENERALIZATION]: "Tangram can map any type of sc/snRNA-seq data, including multimodal data such as those from SHARE-seq, which we used to reveal spatial patterns of chromatin accessibility."
  - s7 [VALIDATION]: "We demonstrate Tangram on healthy mouse brain tissue, by reconstructing a genome-wide anatomically integrated spatial map at single-cell resolution of the visual and somatomotor areas."

A3_here_we_pivot: "To overcome these limitations we present Tangram, a method that aligns sc/snRNA-seq data to various forms of spatial data collected from the same region…"
A4_strongest_quant_in_abstract: — (no numerical claim in abstract; relies on technology breadth: "MERFISH, STARmap, smFISH, Spatial Transcriptomics (Visium) and histological images")

B1_intro_hook_style: field-importance
B1_quote_sentence1: "A Human Cell Atlas should combine high-resolution molecular and histological mapping with anatomical and functional data."
B3_gap_phrases: ["each of the currently available technologies addresses only some of the challenge of resolving entire transcriptomes in space at single-cell resolution"]
B4_pivot_first2sent: "Here, we present Tangram, a deep-learning framework to address two challenges: learn spatial gene-expression maps transcriptome-wide at single-cell resolution, and relate those to histological and anatomical information from the same specimens."
B5_contributions: "Here, we present Tangram, a deep-learning framework to address two challenges: learn spatial gene-expression maps transcriptome-wide at single-cell resolution, and relate those to histological and anatomical information from the same specimens."
B6_last_intro_sentence: "Here, we present Tangram, a deep-learning framework to address two challenges: learn spatial gene-expression maps transcriptome-wide at single-cell resolution, and relate those to histological and anatomical information from the same specimens."

C1_results_headers: ["Tangram: learning of spatially resolved single-cell transcriptomes by alignment", "Tangram maps cells with MERFISH measurements to generate genome-scale high-resolution expression maps", "Accurate correction of transcripts measured with STARmap", "Single-cell deconvolution and histological data incorporation with Spatial Transcriptomics", "Tangram imputation of dropouts in Spatial Transcriptomics", "Spatial localization of chromatin-accessibility patterns with SHARE-seq", "Tangram helps detect cell-type patterns conserved across species", "A learned histological, anatomical, and molecular atlas of the somatomotor mouse cortex at single-nucleus resolution"]
C2_header_style: declarative-finding (most headers begin with "Tangram <verbs>" — claim-first style)
C3_section_openers:
  - {header: "Tangram: learning of spatially resolved single-cell transcriptomes by alignment", quote: "We developed Tangram, an algorithm that uses sc/snRNA-seq data as 'puzzle pieces' to align in space to match 'the shape' of the spatial data (Fig. 1a).", class: method-first}
  - {header: "Tangram maps cells with MERFISH measurements…", quote: "To apply Tangram, we collected 160,000 snRNA-seq profiles using droplet-based RNA-seq (10Xv3)…", class: motivation-first}
  - {header: "Accurate correction of transcripts measured with STARmap", quote: "To further investigate Tangram's correction of low-quality in situ transcripts, we analyzed a STARmap dataset…", class: motivation-first}
  - {header: "Single-cell deconvolution… with Spatial Transcriptomics", quote: "Next, we focused on the deconvolution challenge in the context of lower resolution Spatial Transcriptomics (Visium) data…", class: motivation-first}
  - {header: "Tangram imputation of dropouts…", quote: "Next, we probabilistically mapped the MOp snRNA-seq profiles corresponding to the dissected region for all three Visium slices (Methods).", class: method-first}
  - {header: "Spatial localization of chromatin-accessibility patterns with SHARE-seq", quote: "We next used Tangram's successful spatial mapping through RNA as a scaffold to map additional molecular profiles with no available spatial data.", class: motivation-first}
  - {header: "Tangram helps detect cell-type patterns conserved across species", quote: "We next tested how Tangram performs when the input scRNA-seq and spatial data are derived from different species (Extended Data Fig. 3).", class: motivation-first}
  - {header: "A learned histological, anatomical, and molecular atlas…", quote: "To demonstrate the integration of molecular and anatomical features, we developed an additional module in Tangram…", class: motivation-first}
C4_figure_callouts: ["Tangram learns spatial alignment of sc/snRNA-seq data (Fig. 1a)", "From the learned mapping function, Tangram can…expand from measured subset of genes to genome-wide profiles (Fig. 1b)", "correct low-quality spatial measurements (Fig. 1c)"]
C5_quant_with_stats: "75% of the 253 MERFISH genes are predicted with a correlation of >40%"
C6_baseline_comparison: "98% of nonsparse genes (sparsity < 50%) are correctly predicted by our model"; "about 80% of the transcriptome measured in Visium was highly sparse"
C7_robustness_phrase: "To verify that these distributions were not an artifact of our probabilistic approach", "We hypothesized that this poorer agreement could be due to technical 'dropouts'", "Supporting this hypothesis…"
C8_generalization_phrase: "Tangram is applicable to other organs, as well as disease tissue."

D1_discussion_open: "Genes in organs are expressed in spatially organized patterns at different scales, and understanding these patterns is central to unraveling biological function."
D2_limitation: "For full integration across scales, Tangram's registration pipeline requires a CCF, which is currently available for a few organs, and is most advanced for the mouse brain."
D3_outlook: "However, efforts are underway to construct analogous reference maps for different organs, towards the construction of cell atlases of all organs in mice and humans."
D4_paper_closing_sentence: "However, efforts are underway to construct analogous reference maps for different organs, towards the construction of cell atlases of all organs in mice and humans."

G1_hedges_used: [can, suggests, may, hypothesized, supporting, could]
G2_strong_verbs: [present, develop, align, map, deconvolve, impute, reveal, demonstrate]
G3_paragraph_connectives: ["Next,", "We next tested", "To further investigate", "We hypothesized", "Supporting this hypothesis"]
G4_taken_together: —

notable: Aggressive declarative-finding section headers ("Tangram maps…", "Tangram imputation…", "Accurate correction…") — almost every Results header carries the answer in it. The Introduction is unusually short — final pivot sentence and final intro sentence are the same.

---

## Paper 4: Luecken et al., "Benchmarking atlas-level data integration in single-cell genomics" (scIB)
- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC8748196/  (publisher: https://www.nature.com/articles/s41592-021-01336-8)
- journal: Nature Methods
- year: 2022
- category: benchmark

A1_title: "Benchmarking atlas-level data integration in single-cell genomics"

A2_abstract_map:
  - s1 [BIG-PICTURE]: "Single-cell atlases often include samples that span locations, laboratories and conditions, leading to complex, nested batch effects in data."
  - s2 [GAP]: "Thus, joint analysis of atlas datasets requires reliable data integration."
  - s3 [HERE-WE]: "To guide integration method choice, we benchmarked 68 method and preprocessing combinations on 85 batches of gene expression, chromatin accessibility and simulation data from 23 publications, altogether representing >1.2 million cells…"
  - s4 [METHOD]: "We evaluated methods according to scalability, usability and their ability to remove batch effects while retaining biological variation using 14 evaluation metrics."
  - s5 [KEY-RESULT]: "We show that highly variable gene selection improves the performance of data integration methods, whereas scaling pushes methods to prioritize batch removal over conservation of biological variation."
  - s6 [KEY-RESULT]: "Overall, scANVI, Scanorama, scVI and scGen perform well, particularly on complex integration tasks…"
  - s7 [IMPLICATION]: "Our freely available Python module and benchmarking pipeline can identify optimal data integration methods for new data, benchmark new methods and improve method development."

A3_here_we_pivot: "Here, we present a benchmarking study of data integration methods in complex integration tasks, such as tissue or organ atlases."
A4_strongest_quant_in_abstract: "we benchmarked 68 method and preprocessing combinations on 85 batches… representing >1.2 million cells distributed in 13 atlas-level integration tasks"

B1_intro_hook_style: field-importance
B1_quote_sentence1: "The complexity of single-cell omics datasets is increasing."
B3_gap_phrases: ["Such complexity… creates inevitable batch effects", "Therefore, the development of data integration methods… has become a priority: a grand challenge in single-cell RNA-seq data analysis"]
B4_pivot_first2sent: "Here, we present a benchmarking study of data integration methods in complex integration tasks, such as tissue or organ atlases. Specifically, we benchmarked 16 popular data integration tools on 13 data integration tasks consisting of up to 23 batches and 1 million cells…"
B5_contributions: "Moreover, we use 14 metrics to evaluate the integration methods on their ability to remove batch effects while conserving biological variation. We focus in particular on assessing the conservation of biological variation beyond cell identity labels via new integration metrics on trajectories or cell-cycle variation."
B6_last_intro_sentence: "If cell annotations are available, scGen and scANVI outperform most other methods across tasks, and Harmony and LIGER are effective for scATAC-seq data integration on window and peak feature spaces."

C1_results_headers: ["Single-cell integration benchmarking (scIB)", "Benchmarking data integration: the human immune cell task", "Balancing batch removal and biological variance conservation", "Scaling shifts integration performance toward batch removal", "scANVI, Scanorama and scVI perform best for scRNA-seq", "scATAC-seq integration performance depends on feature space", "Scalability and usability"]
C2_header_style: declarative-finding (most headers state the conclusion: "Scaling shifts…", "scANVI, Scanorama and scVI perform best…", "scATAC-seq integration performance depends on…")
C3_section_openers:
  - {header: "Single-cell integration benchmarking (scIB)", quote: "We benchmarked 16 popular data integration methods on 13 preprocessed integration tasks: two simulation tasks, five scRNA-seq tasks and six scATAC-seq tasks (Fig. 1).", class: method-first}
  - {header: "Benchmarking data integration: the human immune cell task", quote: "To demonstrate our evaluation pipeline, we first focus on the human immune cell integration task (Supplementary Note 3).", class: motivation-first}
  - {header: "Balancing batch removal and biological variance conservation", quote: "Considering the results of the five scRNA-seq and two simulation tasks… we found that the varying complexity of tasks affects the ranking of integration methods…", class: claim-first}
  - {header: "Scaling shifts integration performance toward batch removal", quote: "Given the lack of best-practice for preprocessing raw data for data integration, we assessed whether integration methods perform better with HVG selection or scaling.", class: motivation-first}
  - {header: "scANVI, Scanorama and scVI perform best for scRNA-seq", quote: "To evaluate overall performance of data integration methods across scRNA-seq and simulation tasks, methods can be ranked by their overall scores.", class: motivation-first}
  - {header: "scATAC-seq integration performance depends on feature space", quote: "Several of the benchmarked data integration methods have been used to integrate datasets across modalities.", class: motivation-first}
  - {header: "Scalability and usability", quote: "Monitoring the CPU time and peak memory use reported by our Snakemake pipeline (Extended Data Fig. 7 and Methods), we found that ComBat, BBKNN and SAUCIE performed best in terms of runtime…", class: claim-first}
C4_figure_callouts: ["Fig. 1. Design of single-cell integration benchmarking (scIB).", "Extended Data Fig. 4. Scatter plots summarizing integration performance"]
C5_quant_with_stats: "for HVGs, 74% of comparisons had a higher overall score; 81% had better batch removal"
C6_baseline_comparison: "only 27% of integration outputs performed better than the best unintegrated result"; "mean bio-conservation score for integration outputs on gene activity space is substantially lower than on peaks and windows (genes 0.39; peaks 0.61; windows 0.59)"
C7_robustness_phrase: "To demonstrate our evaluation pipeline, we first focus on…", "To test whether performance of scRNA-seq integration methods transfers…", "To evaluate the impact of feature spaces on data integration…"
C8_generalization_phrase: "scaling resulted in higher batch removal scores (79% of comparisons) but lower bio-conservation (72%)"

D1_discussion_open: "We benchmarked 16 integration methods with four preprocessing combinations on 13 integration tasks via 14 metrics that measure tradeoffs between batch integration and conservation of biological variance."
D2_limitation: "the use of Harmony is appropriate for simple integration tasks with distinct batch and biological structure; however, this method typically ranks outside the top three when used for complex real data scenarios"
D3_outlook: "we have provided the reproducible scIB-pipeline Snakemake pipeline and the scIB python module for users to easily benchmark their particular integration scenario."
D4_paper_closing_sentence: "In addition, we expect that this work will become a reference for method developers, who can build on the presented scenarios and metrics to assess the performance of their newly developed methods on atlas-level data integration tasks."

G1_hedges_used: [can, may, suggest, however, in agreement with, depend on]
G2_strong_verbs: [benchmark, evaluate, demonstrate, outperform, balance, guide, enable]
G3_paragraph_connectives: ["Considering the results of…", "Given the lack of…", "Overall,", "In contrast,", "Methods that used…"]
G4_taken_together: —

notable: Benchmark-paper template par excellence: every Results header is itself a finding ("Scaling shifts…", "scANVI, Scanorama and scVI perform best…"). Last intro sentence pre-announces the final method ranking — abstract, intro, and discussion all repeat the same numerical claims with slight rephrasing.

---

## Paper 5: Kamimoto et al., "Dissecting cell identity via network inference and in silico gene perturbation" (CellOracle)
- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC9946838/  (publisher: https://www.nature.com/articles/s41586-022-05688-9)
- journal: Nature
- year: 2023
- category: methods (with application validation)

A1_title: "Dissecting cell identity via network inference and in silico gene perturbation"

A2_abstract_map:
  - s1 [BIG-PICTURE]: "Cell identity is governed by the complex regulation of gene expression, represented as gene-regulatory networks."
  - s2 [HERE-WE]: "Here we use gene-regulatory networks inferred from single-cell multi-omics data to perform in silico transcription factor perturbations, simulating the consequent changes in cell identity using only unperturbed wild-type data."
  - s3 [VALIDATION]: "We apply this machine-learning-based approach, CellOracle, to well-established paradigms—mouse and human haematopoiesis, and zebrafish embryogenesis—and we correctly model reported changes in phenotype…"
  - s4 [KEY-RESULT]: "Through systematic in silico transcription factor perturbation in the developing zebrafish, we simulate and experimentally validate a previously unreported phenotype that results from the loss of noto…"
  - s5 [KEY-RESULT]: "Furthermore, we identify an axial mesoderm regulator, lhx1a."
  - s6 [IMPLICATION]: "Together, these results show that CellOracle can be used to analyse the regulation of cell identity by transcription factors, and can provide mechanistic insights into development and differentiation."

A3_here_we_pivot: "Here we use gene-regulatory networks inferred from single-cell multi-omics data to perform in silico transcription factor perturbations…"
A4_strongest_quant_in_abstract: — (no numbers in abstract; emphasis on biological-validation language)

B1_intro_hook_style: technical-paradigm + recent-advance
B1_quote_sentence1: "The expansion of single-cell technologies into perturbational omics is enabling the development of methods to characterize cell identity."
B3_gap_phrases: ["but cannot be readily used in many biological contexts", "many approaches still require experimental perturbation data for model training, and thus their scale and application are limited", "previous deep-learning-based models represent a 'black box', which restricts the interpretation…"]
B4_pivot_first2sent: "Here we present a strategy that overcomes these limitations by combining computational perturbation with GRN modelling. CellOracle integrates multimodal data to build custom GRN models that are specifically designed to simulate shifts in cell identity following transcription factor (TF) perturbation…"
B5_contributions: "We apply CellOracle to well-characterized biological systems: haematopoiesis in mice and humans; and the differentiation of axial mesoderm into notochord and prechordal plate in zebrafish."
B6_last_intro_sentence: "Together, these results show that CellOracle can be used to infer and interpret cell-type-specific GRN configurations at high resolution, enabling mechanistic insights into the regulation of cell identity."

C1_results_headers: ["In silico gene perturbation using CellOracle", "GRN inference and benchmarking with CellOracle", "GRN analysis and TF KO in haematopoiesis", "Systematic TF KO simulations in zebrafish", "Experimental validation of noto LOF", "Discovery of axial mesoderm regulators"]
C2_header_style: task-neutral (descriptive noun phrases naming the activity rather than the finding)
C3_section_openers:
  - {header: "In silico gene perturbation using CellOracle", quote: "To gain mechanistic insight into the regulation of cell identity, we developed an in silico strategy to simulate changes in cell identity upon TF perturbation.", class: motivation-first}
  - {header: "GRN inference and benchmarking with CellOracle", quote: "The CellOracle GRN model must represent regulatory connections as a directed network edge to support signal propagation in response to TF perturbation.", class: method-first}
  - {header: "GRN analysis and TF KO in haematopoiesis", quote: "For validation, we aimed to reproduce known TF regulation of mouse haematopoiesis, a well-characterized differentiation paradigm…", class: motivation-first}
  - {header: "Systematic TF KO simulations in zebrafish", quote: "Next, we applied CellOracle to systematically perturb TFs across zebrafish development.", class: motivation-first}
  - {header: "Experimental validation of noto LOF", quote: "Next, we experimentally validated the predicted expansion of prechordal plate after noto LOF.", class: motivation-first}
  - {header: "Discovery of axial mesoderm regulators", quote: "To identify novel TFs required for axial mesoderm differentiation, we prioritized TFs according to predicted KO phenotypes…", class: motivation-first}
C4_figure_callouts: — (paper relies on Extended Data and main Figs; specific quoted callouts not extracted)
C5_quant_with_stats: "Inference performance as assessed by the area under the receiver operating characteristic (AUROC) ranged from 0.66 to 0.85"
C6_baseline_comparison: "85% of the top 30 TFs ranked by this objective, systematic perturbation strategy are reported regulators"; "more than 80% of the top 30 TFs in this analysis were associated with somite differentiation"
C7_robustness_phrase: "To further examine", "To test whether", "We next sought to", "In agreement with previous observations"
C8_generalization_phrase: "Together, these results show that CellOracle can be used to infer and interpret cell-type-specific GRN configurations at high resolution…"

D1_discussion_open: "The emerging discipline of perturbational single-cell omics enables regulators of cell identity and behaviour to be modelled and predicted."
D2_limitation: "However, this approach requires experimentally perturbed training data, which limits its scalability." (about competitor scGen — limitation framed by contrast)
D3_outlook: "in the context of human development, we have recently applied CellOracle to predict candidate regulators of medium spiny neuron maturation in human fetal striatum…"
D4_paper_closing_sentence: "For example, in the context of human development, we have recently applied CellOracle to predict candidate regulators of medium spiny neuron maturation in human fetal striatum, demonstrating the power of in silico perturbation where experimental approaches cannot be deployed."

G1_hedges_used: [can, may, suggest, however, in agreement with, together, supporting]
G2_strong_verbs: [present, integrate, simulate, perturb, predict, validate, identify, dissect]
G3_paragraph_connectives: ["Next,", "For validation,", "Together,", "Furthermore,", "In agreement with"]
G4_taken_together: "Together, these results show that CellOracle can be used to analyse the regulation of cell identity…" (used in both abstract and last intro sentence)

notable: Heavy use of "Together, these results show…" as both abstract closer and last-intro-sentence — the same template sentence twice. The Discussion's first paragraph structures the limitations of competitor methods (scGen) before re-pitching CellOracle, an unusually combative competitor framing.

---

## Paper 6: Zeng et al., "CellFM: a large-scale foundation model pre-trained on transcriptomics of 100 million human cells"
- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC12092794/  (publisher: https://www.nature.com/articles/s41467-025-59926-5)
- journal: Nature Communications
- year: 2025
- category: methods
- swap_note: replaces scGPT (paywalled / 403 on bioRxiv mirrors after two attempts)

A1_title: "CellFM: a large-scale foundation model pre-trained on transcriptomics of 100 million human cells"

A2_abstract_map:
  - s1 [BIG-PICTURE]: "Single-cell sequencing provides transcriptomic profiling at single-cell resolution, uncovering cellular heterogeneity with unprecedented precision."
  - s2 [GAP]: "Yet, current single cell data analysis suffers from the inherent data noises, batch effects, and sparsity, highlighting the requirement of a unified model to represent cellular states."
  - s3 [RECENT-ADVANCE]: "To circumvent this problem, many recent efforts focus on training single-cell foundation models based on large datasets."
  - s4 [GAP]: "However, current human foundation models are still limited by the sizes of training data and model parameters."
  - s5 [HERE-WE]: "Here, we have collected a diverse dataset of 100 million human cells, on which we train a single-cell foundation model (CellFM) containing 800 million parameters."
  - s6 [METHOD]: "To balance efficiency and performance, the model is trained through a modified RetNet framework on the MindSpore."
  - s7 [KEY-RESULT]: "Extensive experiments have shown that CellFM outperforms existing models in cell annotation, perturbation prediction, gene function prediction, and gene-gene relationship capturing."

A3_here_we_pivot: "Here, we have collected a diverse dataset of 100 million human cells, on which we train a single-cell foundation model (CellFM) containing 800 million parameters."
A4_strongest_quant_in_abstract: "100 million human cells, on which we train a single-cell foundation model (CellFM) containing 800 million parameters"

B1_intro_hook_style: recent-advance / field-importance
B1_quote_sentence1: "Single-cell RNA sequencing (scRNA-seq) technologies have revolutionized molecular biology by enabling the measurement of transcriptome profiles with unparalleled scale and precision."
B3_gap_phrases: — (limited extraction; gap framed in abstract via "current human foundation models are still limited by the sizes of training data and model parameters")
B4_pivot_first2sent: "Here, we collect a lot of single-cell datasets from public databases and then make these data cleansing and standardization of unified formats, resulting in compiling a dataset of approximately 100 million human cells…"
B5_contributions: "we train a single-cell foundation model (CellFM) containing 800 million parameters" (from abstract); "Extensive experiments have shown that CellFM outperforms existing models in cell annotation, perturbation prediction, gene function prediction, and gene-gene relationship capturing"
B6_last_intro_sentence: "Here, we collect a lot of single-cell datasets from public databases and then make these data cleansing and standardization of unified formats, resulting in compiling a dataset of approximately 100 million human cells sequenced through various technologies."

C1_results_headers: ["Overview of cellFM", "CellFM improves the accuracy of gene function prediction", "CellFM enables predicting perturbation responses", "Reverse perturbation prediction in silico using CellFM", "Cell type annotation with CellFM", "Deciphering gene relationships with CellFM", "CellFM efficiently identified genes most affected by perturbations"]
C2_header_style: declarative-finding (most begin with "CellFM <verbs>")
C3_section_openers:
  - {header: "Overview of cellFM", quote: "Single-cell sequencing technology is crucial for revealing the detailed landscape of cellular diversity and function at the single-cell resolution.", class: motivation-first}
  - {header: "CellFM improves the accuracy of gene function prediction", quote: "Gene function prediction is a cornerstone for deciphering the roles and properties of genes under diverse conditions.", class: motivation-first}
  - {header: "CellFM enables predicting perturbation responses", quote: "Recent advancements in sequencing and gene editing have enabled large-scale experimental perturbation simulations to study changes in gene expression and cellular behavior.", class: motivation-first}
  - {header: "Reverse perturbation prediction in silico using CellFM", quote: "Beyond forecasting the outcomes of gene perturbations, the accurate prediction of CRISPR target genes that prompt cellular recovery from disease states is equally significant.", class: motivation-first}
  - {header: "Cell type annotation with CellFM", quote: "Cell type annotation is a cornerstone of single-cell data analysis, essential for uncovering the cellular heterogeneity within biological samples.", class: motivation-first}
  - {header: "Deciphering gene relationships with CellFM", quote: "The intricate interplay among target genes within a Gene Regulatory Network (GRN) is pivotal for orchestrating key biological processes.", class: motivation-first}
  - {header: "CellFM efficiently identified genes most affected by perturbations", quote: "In this section, we analyzed the perturbed genes in the perturbation experiments and their most significantly affected genes through the attention map.", class: method-first}
C4_figure_callouts: ["as shown in Fig. 1", "As depicted in Fig. 3", "As illustrated in Fig. 4", "As shown in Supplementary Fig."]
C5_quant_with_stats: "5.68% and 5.86% increase over the top two competing models"
C6_baseline_comparison: "2.02% higher than the second-ranked single-cell foundation model"; "18.1% higher than scGPT"; "81.8% of the top 10 predictions"
C7_robustness_phrase: "To make a fair comparison, we adopted a zero-shot learning strategy", "To ensure a fair comparison", "we next asked", "To further assess CellFM's capability"
C8_generalization_phrase: "Extensive experiments have shown that CellFM outperforms existing models in cell annotation, perturbation prediction, gene function prediction, and gene-gene relationship capturing."

D1_discussion_open: "To aid efficient analysis of the single-cell data and harness the wealth of knowledge contained within single-cell atlas datasets, we have introduced a state-of-the-art foundation model known as CellFM."
D2_limitation: "Finally, the model's construction did not leverage existing biological prior knowledge, which could affect its depth and accuracy in interpreting biological phenomena."
D3_outlook: —
D4_paper_closing_sentence: "Finally, the model's construction did not leverage existing biological prior knowledge, which could affect its depth and accuracy in interpreting biological phenomena."

G1_hedges_used: [can, could, may, suggest, affect]
G2_strong_verbs: [introduce, train, outperform, predict, decipher, identify, enable]
G3_paragraph_connectives: ["To make a fair comparison", "To ensure a fair comparison", "Beyond forecasting", "we next asked"]
G4_taken_together: —

notable: Atypical for a Nature-family paper, the Discussion ends on a self-stated limitation rather than an outlook ("did not leverage existing biological prior knowledge, which could affect its depth and accuracy"). Section openers begin with "X is a cornerstone…" / "X is crucial…" — repeated rhetorical template. Numerical contrasts call competitors out by name ("18.1% higher than scGPT").

---

## Cross-paper observations for this category

- **"Here we…" pivot is universal and short.** Every paper deploys a single sentence beginning with "Here we develop / Here we present / Here we use / Here we introduce…". It carries the entire method positioning and is usually the third or fourth sentence of the abstract. The pivot sentence almost always restates the method name, the data scale, and one differentiating verb ("foundation", "metric-learning", "context-aware", "GRN modelling").

- **Abstracts are scale-quant heavy in the noun phrase, not in the comparison.** Numbers in the abstract describe corpus / model size ("23.4-million-cell atlas", "~30 million single cell transcriptomes", "100 million human cells", "800 million parameters") rather than performance deltas. Performance deltas are deferred to the Discussion or a later "outperforms existing models" line.

- **Two distinct Results-header styles coexist and are stable per paper.** Older / methods-only papers (Tangram, CellOracle) prefer task-neutral noun-phrase headers ("GRN inference and benchmarking with CellOracle"). Newer / benchmark / FM papers (scIB, SCimilarity, CellFM) push declarative-finding headers where the header itself is a result claim ("scANVI, Scanorama and scVI perform best for scRNA-seq"; "CellFM improves the accuracy of gene function prediction"). Geneformer mixes both.

- **Section-opener templates cluster around three classes.** (a) **method-first** ("X is a context-aware, attention-based deep learning model…"), (b) **motivation-first** ("To investigate / To gain mechanistic insight / Determining the hierarchy in gene networks enables…"), (c) **claim-first** ("Considering the results… we found that…"). Motivation-first dominates in subsections that introduce a new analysis; method-first dominates in the first Results subsection that defines the architecture.

- **"We next…" / "To rule out…" / "We hypothesized…" are the recurring robustness verbs.** Across all six papers the same compact rhetorical moves recur: "We next tested whether", "We next asked", "To rule out", "To verify that these distributions were not an artifact of our probabilistic approach", "We hypothesized…", "Supporting this hypothesis…". This is the lexical signature of robustness-paragraph writing in the field.

- **"Together, these results show…" is the canonical synthesis sentence.** It appears in CellOracle's last-intro-sentence (and again later); SCimilarity uses it implicitly via "We illustrate the power of…showing how…"; Geneformer uses "Overall, Geneformer represents…". The category strongly converges on a single multi-purpose synthesis template ("Overall / Together / In sum…").

- **Introductions preview the Results table-of-contents.** In Geneformer, scIB, and CellOracle, the last paragraph of the Introduction enumerates each downstream task and pre-announces the bottom-line for each — the intro reads like a structured abstract of the Results section. Tangram is the exception (a single-sentence final-intro pivot).

- **Discussion openers are reflective, often repeating a high-level abstract sentence.** "We benchmarked 16 integration methods…", "SCimilarity offers a unique approach…", "In sum, we developed a context-aware deep learning model…", "To aid efficient analysis…we have introduced…". The Discussion's first sentence is typically a one-line restatement of the method's framing, followed by the strongest result.

- **Limitation paragraphs are short and tucked in.** Five of six papers contain exactly one explicit limitation sentence ("users should always interpret cross-technology integrations with care", "did not leverage existing biological prior knowledge", "Tangram's registration pipeline requires a CCF, which is currently available for a few organs"). Limitation paragraphs are not a separate subsection.

- **Closing sentences favor an outlook "applicable to other organs / democratized / future studies".** Tangram, Geneformer, and SCimilarity all close on a generalization/outlook beat. Benchmark (scIB) closes on community service ("we expect that this work will become a reference for method developers"). Application paper (CellOracle) closes with a fresh application teaser. Foundation-model paper (CellFM) atypically closes on a limitation.

- **The "foundation model" framing is now lexically standardized.** "Foundation model", "self-supervised", "pretrained on N million cells", "transfer learning", "fine-tuning towards downstream tasks" appear nearly verbatim across SCimilarity, Geneformer, scGPT, CellFM. This forms a portable rhetorical template: (1) parallel-to-NLP statement, (2) scale claim, (3) downstream-task list, (4) interpretability/embedding claim.
