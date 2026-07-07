# Drug Discovery & Molecular ML — Nature-style Writing Extracts

Six open-access papers analyzed for rhetorical/structural patterns. All quotes are verbatim from the original English text.

---

## Paper 1: Lu et al., DynamicBind (Nature Communications, 2024)
- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC10844226/
- journal: Nature Communications
- year: 2024
- category: methods

A1_title: "DynamicBind: predicting ligand-specific protein-ligand complex structure with a deep equivariant generative model"

A2_abstract_map:
  - s1 [field-level setup]: "While significant advances have been made in predicting static protein structures, the inherent dynamics of proteins, modulated by ligands, are crucial for understanding protein function and facilitating drug discovery."
  - s2 [gap, prior limitation]: "Traditional docking methods, frequently used in studying protein-ligand interactions, typically treat proteins as rigid."
  - s3 [gap, alternative limitation]: "While molecular dynamics simulations can propose appropriate protein conformations, they're computationally demanding due to rare transitions between biologically relevant equilibrium states."
  - s4 [pivot/contribution]: "In this study, we present DynamicBind, a deep learning method that employs equivariant geometric diffusion networks to construct a smooth energy landscape, promoting efficient transitions between different equilibrium states."
  - s5 [property claim]: "DynamicBind accurately recovers ligand-specific conformations from unbound protein structures without the need for holo-structures or extensive sampling."
  - s6 [headline result]: "Remarkably, it demonstrates state-of-the-art performance in docking and virtual screening benchmarks."
  - s7 [generalization]: "Our experiments reveal that DynamicBind can accommodate a wide range of large protein conformational changes and identify cryptic pockets in unseen protein targets."
  - s8 [outlook/impact]: "As a result, DynamicBind shows potential in accelerating the development of small molecules for previously undruggable targets and expanding the horizons of computational drug discovery."

A3_here_we_pivot: "Here, we present DynamicBind, a geometric deep generative model designed for 'dynamic docking'..."
A4_strongest_quant_in_abstract: "demonstrates state-of-the-art performance in docking and virtual screening benchmarks" (qualitative; numbers held for results)

B1_intro_hook_style: field-progress hook → narrowing to docking
B1_quote_sentence1: "Remarkable progress has been achieved in the realm of protein structure prediction from sequence data."
B3_gap_phrases:
  - "typically treat proteins as rigid"
  - "rare transitions between biologically relevant equilibrium states"
  - "without the need for holo-structures or extensive sampling"
B4_pivot_first2sent: "Here, we present DynamicBind, a geometric deep generative model designed for 'dynamic docking'... Unlike traditional docking methods that treat proteins as mostly rigid entities, DynamicBind efficiently adjusts the protein conformation from its initial AlphaFold prediction to a holo-like state."
B5_contributions: implicit in the "Here, we present..." pivot — unifies conformation generation and pose prediction in one model.
B6_last_intro_sentence: — (not extracted)

C1_results_headers:
  - "DynamicBind architectures"
  - "DynamicBind achieves higher accuracy in ligand pose prediction and improves the initial AlphaFold-predicted protein conformations"
  - "DynamicBind can capture ligand-specific protein conformational changes"
  - "DynamicBind covers multi-scale protein conformation changes"
  - "DynamicBind reveals cryptic pockets significant to drug discovery"
  - "DynamicBind achieves better screening performance in an antibiotics benchmark"
C2_header_style: declarative subject-verb headers, almost all start with the method name "DynamicBind <verb> ..."
C3_section_openers:
  - {header: "DynamicBind architectures", quote: "DynamicBind executes 'dynamic docking', a process that performs prediction of the protein–ligand complex structure while accommodating substantial protein conformational changes.", class: definition}
  - {header: "Higher accuracy", quote: "To evaluate our method, we first utilized the PDBbind dataset and, in line with previous works, we trained the model using a chronological, time-based split of the training, validation, and test sets.", class: setup}
  - {header: "Ligand-specific changes", quote: "Conventional docking protocols usually perform protein conformation sampling as a separate step from the docking process.", class: contrast-with-prior}
  - {header: "Cryptic pockets", quote: "The dynamic nature of proteins often gives rise to cryptic pockets.", class: motif}

C4_figure_callouts:
  - "As illustrated in Fig. 1a, at each step, the features and the coordinates of the protein and the ligand are fed into an SE(3)-equivariant interaction module."
  - "As shown in Fig. 2a and b, DynamicBind predicts more cases with ligand RMSD below various thresholds than other baselines."

C5_quant_with_stats:
  - "it achieves the fraction of ligand RMSD below 2 Å (5 Å), being 33% (65%) on the PDBbind test set and 39% (68%) on the MDT test set"
  - "the auROC score, with ligand RMSD below 2 Å as the true positive, is 0.764"
  - "DynamicBind has 63.67 million parameters and was trained for 5 days on eight Nvidia A100 80GB GPUs"
C6_baseline_comparison: "The success rate of DynamicBind (0.33) is 1.7 times higher than the best baseline DiffDock (0.19) under the more stringent condition"
C7_robustness_phrase: "DynamicBind surpasses both common docking methods like VINA and DOCK6.9... achieving the mean average area under the receiver operating characteristic curve (auROC) of 0.68"
C8_generalization_phrase: "DynamicBind can accommodate a wide range of large protein conformational changes and identify cryptic pockets in unseen protein targets"

D1_discussion_open: "DynamicBind unifies two conventionally separated steps, protein conformation generation, and ligand pose prediction, into a single framework. As an end-to-end deep learning method, it is orders of magnitude faster than traditional MD simulations in sampling extensive protein conformational changes."
D2_limitation: "DynamicBind, while demonstrating state-of-the-art performance in our benchmarks, still presents opportunities for improvement, especially in enhancing its ability to generalize to proteins with low sequence homology compared to those in the training set."
D3_outlook: "By adopting a self-distillation approach analogous to AlphaFold, we could augment our training set by integrating high-confidence predictions of the complex structures of protein–ligand pairs that previously only had affinity data available."
D4_paper_closing_sentence: same as D3.

G1_hedges_used: "Remarkably", "still presents opportunities for improvement", "shows potential in"
G2_strong_verbs: "unifies", "accommodates", "surpasses", "recovers", "demonstrates"
G3_paragraph_connectives: "As a result", "Remarkably", "While ... While ..."
G4_taken_together: implied via "As a result, DynamicBind shows potential ..."

notable: Almost every Results header begins with the method name as the syntactic subject. The discussion explicitly contrasts limitation (sequence-homology generalization) immediately before the outlook (self-distillation), a clean limitation→remedy pivot.

---

## Paper 2: Wong et al., Discovery of a structural class of antibiotics with explainable deep learning (Nature, 2024)
- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC10866013/
- journal: Nature
- year: 2024
- category: application (discovery story with method)

A1_title: "Discovery of a structural class of antibiotics with explainable deep learning"

A2_abstract_map:
  - s1 [field crisis hook]: "The discovery of novel structural classes of antibiotics is urgently needed to address the ongoing antibiotic resistance crisis."
  - s2 [gap]: "Deep learning approaches have aided in exploring chemical spaces; yet, these models are typically black box in nature and do not provide chemical insights."
  - s3 [hypothesis pivot]: "Here, we reasoned that the chemical substructures associated with antibiotic activity learned by neural network models can be identified and used to predict structural classes of antibiotics."
  - s4 [approach]: "We tested this hypothesis by developing an explainable, substructure-based approach for the efficient, deep learning-guided exploration of chemical spaces."
  - s5 [scale]: "We determined the antibiotic activities and human cell cytotoxicity profiles of 39,312 compounds and applied ensembles of graph neural networks to predict antibiotic activity and cytotoxicity for 12,076,365 compounds."
  - s6 [method core]: "Using explainable graph algorithms, we identified substructure-based rationales for compounds with high predicted antibiotic activity and low predicted cytotoxicity."
  - s7 [empirical]: "We empirically tested 283 compounds and found that compounds exhibiting antibiotic activity against Staphylococcus aureus were enriched in putative structural classes arising from rationales."
  - s8 [discovery payload]: "Of these structural classes of compounds, one is selective against methicillin-resistant S. aureus (MRSA) and vancomycin-resistant enterococci, evades substantial resistance, and reduces bacterial titers in mouse models of MRSA skin and systemic thigh infection."
  - s9 [meta-claim]: "Our approach enables the deep learning-guided discovery of structural classes of antibiotics and demonstrates that machine learning models in drug discovery can be explainable, providing insights into the chemical substructures that underlie selective antibiotic activity."

A3_here_we_pivot: "Here, we reasoned that the chemical substructures associated with antibiotic activity learned by neural network models can be identified and used to predict structural classes of antibiotics."
A4_strongest_quant_in_abstract: "predict antibiotic activity and cytotoxicity for 12,076,365 compounds" (scale flex); "reduces bacterial titers in mouse models of MRSA skin and systemic thigh infection" (in vivo)

B1_intro_hook_style: societal-crisis hook
B1_quote_sentence1: "The ongoing antibiotic resistance crisis threatens to render current antibiotics ineffective and increase morbidity from bacterial infections."
B3_gap_phrases:
  - "models are typically black box in nature"
  - "do not provide chemical insights"
  - "novel structural classes of antibiotics is urgently needed"
B4_pivot_first2sent: "Here, we aimed to vastly expand graph neural network models for antibiotic discovery by training on large datasets measuring antibiotic activity and human cell cytotoxicity, and we hypothesized that model predictions could be explained on the level of chemical substructures using graph search algorithms."
B5_contributions: explainability rationale → predicting structural classes; in vivo MRSA validation; selectivity vs cytotoxicity.
B6_last_intro_sentence: — (the pivot above effectively closes intro)

C1_results_headers:
  - "Models for antibiotic activity"
  - "Models for human cell cytotoxicity"
  - "Filtering and visualizing chemical space"
  - "Rationales predict antibiotic classes"
  - "Novel, filtered substructures"
  - "A structural class of antibiotics from rationales"
  - "Mechanism of action and resistance"
  - "Toxicology, chemical properties, and in vivo efficacy"
C2_header_style: short noun-phrase headers; arc moves model → filter → rationale → class → mechanism → in vivo. Classic Stokes-style discovery pipeline.
C3_section_openers:
  - {header: "Models for antibiotic activity", quote: "In this study, we focus on discovering structural classes of antibiotics that are effective against Staphylococcus aureus, a Gram-positive pathogen resistant to many first-line antibiotics and a major cause of difficult-to-treat nosocomial and bloodstream infections.", class: scope-setting}
  - {header: "Filtering and visualizing chemical space", quote: "Satisfied with the performance of our models, we retrained ensembles of 20 Chemprop models with the entirety of each of the training datasets, resulting in four ensembles predicting antibiotic activity, HepG2 cytotoxicity, HSkMC cytotoxicity, and IMR-90 cytotoxicity.", class: methodological-transition}
  - {header: "Rationales predict antibiotic classes", quote: "As graph neural networks make predictions based on the information contained in the atoms and bonds of each molecule, we hypothesized that compounds with high antibiotic prediction scores contain substructures (\"rationales\") that largely determine their scores.", class: hypothesis-frame}
  - {header: "A structural class of antibiotics from rationales", quote: "Testing for growth inhibition, we found that four out of the nine procured hits (44%) associated with groups G1-G5 exhibited activity against S. aureus, with minimal inhibitory concentrations (MICs) ≤32 μg/mL.", class: result-with-numbers}

C4_figure_callouts:
  - "Schematic of the approach: Graph neural networks predict the chemical properties of >10⁹ molecules in silico, in contrast to expensive and time-consuming experimental screening of large chemical libraries."
  - "Illustration of the Monte Carlo tree search method resulting in chemical structure rationales (graph substructures) with high predicted antibiotic activity."

C5_quant_with_stats:
  - "39,312 compounds" (training screen)
  - "AUPRC was 0.364"
  - "12,076,365 compounds" computationally evaluated
  - "3,646 compounds passing antibiotic and cytotoxicity filters (0.03% of all assessed)"
  - "Four out of nine procured hits (44%)" exhibited activity
  - "median MICs for compounds 1 and 2 were 4 and 3 μg/mL"
  - "~1.2 logs reduction in bacterial load in mouse models"
C6_baseline_comparison: "none of the 45 procured hits with rationales not associated with G1-G5, and 17 of the 187 procured hits with no rationale (9.1%), exhibited activity"
C7_robustness_phrase: "evades substantial resistance"
C8_generalization_phrase: "selective against methicillin-resistant S. aureus (MRSA) and vancomycin-resistant enterococci"

D1_discussion_open: "The need to discover novel structural classes of antibiotics is pressing given the antibiotic resistance crisis. This challenge has manifested in the 38-year interval between the introduction of the fluoroquinolone class of antibiotics in 1962 and the next new structural class, the oxazolidinones, in 2000."
D2_limitation: "The approach presented here—which includes in silico predictions of compound cytotoxicity and stringent medicinal chemistry filtering steps that might inform work in other areas of drug discovery—could be further refined to consider more detailed representations of chemical space and factors important to antibiotic activity, such as protein binding in serum."
D3_outlook: "with which we may begin to efficiently explore novel chemical spaces and gain specific insights into the chemical substructures that underlie biological activity"
D4_paper_closing_sentence: "The discovery of structural classes using explainable deep learning could facilitate the process of identifying and optimizing potential leads by focusing on key scaffolds of interest, with which we may begin to efficiently explore novel chemical spaces and gain specific insights into the chemical substructures that underlie biological activity."

G1_hedges_used: "could be further refined", "may begin to", "putative structural classes"
G2_strong_verbs: "evades", "reduces", "enriched", "predict", "exhibited"
G3_paragraph_connectives: "Building on", "Intriguingly", "Given the favorable", "As graph neural networks ..."
G4_taken_together: "Our approach enables the deep learning-guided discovery of structural classes of antibiotics and demonstrates that machine learning models in drug discovery can be explainable"

notable: Discussion opens with a striking historical fact ("38-year interval ... fluoroquinolone class of antibiotics in 1962 and the next new structural class, the oxazolidinones, in 2000.") to set societal stakes — Nature loves this kind of historical anchor. Abstract sentence 8 is a single dense sentence packing four claims (selectivity, two pathogens, resistance, two mouse models) — characteristic of biomedical Nature flagship abstracts.

---

## Paper 3: Stokes et al., A deep learning approach to antibiotic discovery — Halicin (Cell, 2020)
- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC8349178/
- journal: Cell
- year: 2020
- category: application (discovery story)

A1_title: "A deep learning approach to antibiotic discovery"

A2_abstract_map:
  - s1 [crisis hook]: "Due to the rapid emergence of antibiotic-resistant bacteria, there is a growing need to discover new antibiotics."
  - s2 [response]: "To address this challenge, we trained a deep neural network capable of predicting molecules with antibacterial activity."
  - s3 [headline discovery]: "We performed predictions on multiple chemical libraries and discovered a molecule from the Drug Repurposing Hub – halicin – that is structurally divergent from conventional antibiotics and displays bactericidal activity against a wide phylogenetic spectrum of pathogens, including *Mycobacterium tuberculosis* and carbapenem-resistant Enterobacteriaceae."
  - s4 [in vivo]: "Halicin also effectively treated *Clostridioides difficile* and pan-resistant *Acinetobacter baumannii* infections in murine models."
  - s5 [scale validation]: "Additionally, from a discrete set of 23 empirically tested predictions from >10⁷ million molecules curated from the ZINC15 database, our model identified eight antibacterial compounds that are structurally distant from known antibiotics."
  - s6 [meta-claim]: "This work highlights the utility of deep learning approaches to expand our antibiotic arsenal through the discovery of structurally distinct antibacterial molecules."

A3_here_we_pivot: "Here, we demonstrate how the combination of *in silico* predictions and empirical investigations can lead to the discovery of new antibiotics."
A4_strongest_quant_in_abstract: ">10⁷ million molecules curated from the ZINC15 database, our model identified eight antibacterial compounds"

B1_intro_hook_style: historical/medical-cornerstone hook
B1_quote_sentence1: "Since the discovery of penicillin, antibiotics have become the cornerstone of modern medicine."
B3_gap_phrases:
  - "growing need to discover new antibiotics"
  - "structurally divergent from conventional antibiotics"
  - "structurally distant from known antibiotics"
B4_pivot_first2sent: "Here, we demonstrate how the combination of *in silico* predictions and empirical investigations can lead to the discovery of new antibiotics. Our approach consists of three stages."
B5_contributions: explicitly enumerated three-stage approach: "First, we trained a deep neural network model... Second, we applied the resulting model to several discrete chemical libraries... lastly selected a list of candidates based on a pre-specified prediction score threshold, chemical structure, and availability."
B6_last_intro_sentence: ends the intro with a candidate-selection criterion sentence (above).

C1_results_headers:
  - "Initial model training and the identification of halicin"
  - "Halicin is a broad-spectrum bactericidal antibiotic"
  - "Halicin dissipates the ∆pH component of the proton motive force"
  - "Halicin displays efficacy in murine models of infection"
  - "Predicting new antibiotic candidates from vast chemical libraries"
C2_header_style: declarative-claim subject headers; subject is the molecule ("Halicin <does X>")
C3_section_openers:
  - {header: "Initial model training", quote: "Initially, we desired to obtain a training dataset *de novo* that was inexpensive, chemically diverse, and did not require sophisticated laboratory resources.", class: motivation}
  - {header: "Broad-spectrum bactericidal", quote: "Given that halicin displayed potent growth inhibitory activity against *E. coli*, we next performed time- and concentration-dependent killing assays to determine whether this compound inhibited growth through a bactericidal or bacteriostatic mechanism.", class: bridge-experiment}
  - {header: "Murine models", quote: "Given that halicin displays broad-spectrum bactericidal activity and is not highly susceptible to plasmid-borne antibiotic-resistance elements or *de novo* resistance mutations at high frequency, we next asked whether this compound might have utility as an antibiotic *in vivo*.", class: scope-escalation}

C4_figure_callouts:
  - "Modern approaches to antibiotic discovery often include screening large chemical libraries for those that elicit a phenotype of interest."
  - "Halicin is shown as a black and yellow circle."

C5_quant_with_stats:
  - "training dataset of 2,335 molecules"
  - "120 molecules with growth inhibitory activity (5.14%)"
  - "ROC-AUC of 0.896 on test data"
  - "MIC of 2 µg/ml for halicin against E. coli"
  - "107,349,233 molecules from ZINC15 database screened"
  - "8 of 23 empirically tested ZINC15 predictions showed antibacterial activity"
  - "5 of 6 mice treated with halicin contained <10³ CFU/g in wound infection model"
C6_baseline_comparison: prior screening hit rates contrasted implicitly: "8 of 23 empirically tested predictions" vs typical primary screen hit rates.
C7_robustness_phrase: "not highly susceptible to plasmid-borne antibiotic-resistance elements or *de novo* resistance mutations at high frequency"
C8_generalization_phrase: "wide phylogenetic spectrum of pathogens"

D1_discussion_open: "The prevalence of antibiotic resistance is rapidly increasing on a global scale. Concurrently, the steadily declining productivity in clinically implementing new antibiotics due to the high risk of early discovery and low return on investment is exacerbating this problem."
D2_limitation: "It is important to emphasize that machine learning is imperfect. Therefore, the success of deep neural network model-guided antibiotic discovery rests heavily on the coupling of these approaches to appropriate experimental designs."
D3_outlook: "Deep learning approaches could therefore enable us to expand our antibiotic arsenal and help outpace the dissemination of resistance."
D4_paper_closing_sentence: same as D3.

G1_hedges_used: "could", "might have utility", "machine learning is imperfect"
G2_strong_verbs: "discovered", "displays", "treated", "outpace", "dissipates"
G3_paragraph_connectives: "Given that ...", "Concurrently", "Initially", "Additionally"
G4_taken_together: "This work highlights the utility of deep learning approaches to expand our antibiotic arsenal..."

notable: First Cell-style sentence opens with the historical anchor ("Since the discovery of penicillin..."). The intro explicitly numbers ("Our approach consists of three stages. First... Second... lastly..."), an unusually didactic move that became a template for later ML-bio papers. Discussion uses a forthright limitation: "It is important to emphasize that machine learning is imperfect."

---

## Paper 4: Swanson et al., SyntheMol (Nature Machine Intelligence, 2024; workshop preprint NeurIPS 2023 GenAI & Biology)
- url_oa: https://www.nature.com/articles/s42256-024-00809-7 (NeurIPS workshop PDF used for verbatim text)
- journal: Nature Machine Intelligence (with NeurIPS 2023 workshop precursor)
- year: 2024
- category: methods + application (discovery)

A1_title: "Generative AI for designing and validating easily synthesizable and structurally novel antibiotics"

A2_abstract_map:
  - s1 [crisis hook]: "The rise of pan-resistant bacteria is creating an urgent need for structurally novel antibiotics."
  - s2 [field claim, generic]: "AI methods can discover new antibiotics, but existing methods have significant limitations."
  - s3 [gap A]: "Property prediction models, which evaluate molecules one-by-one for a given property, scale poorly to large chemical spaces."
  - s4 [gap B]: "Generative models, which directly design molecules, rapidly explore vast chemical spaces but generate molecules that are challenging to synthesize."
  - s5 [pivot]: "Here, we introduce SyntheMol, a generative model that designs easily synthesizable compounds from a chemical space of 30 billion molecules."
  - s6 [application choice]: "We apply SyntheMol to design molecules that inhibit the growth of Acinetobacter baumannii, a burdensome bacterial pathogen."
  - s7 [validation payoff]: "We synthesize 58 generated molecules and experimentally validate them, with six structurally novel molecules demonstrating potent activity against A. baumannii and several other phylogenetically diverse bacterial pathogens."

A3_here_we_pivot: "Here, we introduce SyntheMol, a generative model that designs easily synthesizable compounds from a chemical space of 30 billion molecules."
A4_strongest_quant_in_abstract: "58 generated molecules and experimentally validate them, with six structurally novel molecules demonstrating potent activity"

B1_intro_hook_style: scale-of-mortality hook with concrete numbers
B1_quote_sentence1: "The global dissemination of antibiotic resistance determinants is one of the most significant challenges of modern medicine."
B3_gap_phrases:
  - "evaluate molecules one-by-one, which is time consuming for large chemical spaces"
  - "generated compounds are often synthetically intractable, thereby preventing experimental validation"
  - "very few studies synthesized and experimentally tested any generated molecules"
B4_pivot_first2sent: "In this study, we developed SyntheMol, a generative AI model that uses a Monte Carlo tree search to assemble novel compounds using ∼132,000 molecular building blocks with known reactivities and 13 well-validated chemical synthesis reactions (Figure 1). The resulting chemical space contains nearly 30 billion molecules that are easy to synthesize, with synthesis success rates of over 80% within 3 to 4 weeks."
B5_contributions: SyntheMol = MCTS-guided assembly over Enamine REAL space with 13 reactions; experimental validation of 58 compounds; 6 active hits.
B6_last_intro_sentence: "We trained SyntheMol to design molecules with antibiotic activity against A. baumannii, and we synthesized and experimentally validated 58 generated molecules, with six showing potent activity against A. baumannii and several other phylogenetically diverse bacterial pathogens."

C1_results_headers:
  - "Property Prediction Models"
  - "SyntheMol"
  - "Generation Results" (subsections: "Generating cLogP Molecules", "Generating Antibiotics", "Filtering Antibiotics")
  - "In Vitro Validation of Generated Molecules" (subsections: "A. Baumannii Validation", "Broad-Spectrum Validation")
C2_header_style: noun-phrase, methodology-then-validation arc
C3_section_openers:
  - {header: "Property Prediction Models", quote: "To establish a training dataset, we physically screened 13,524 molecules and measured growth inhibition of A. baumannii ATCC 17978 when treated with each chemical, resulting in 470 active compounds and 13,054 inactive compounds.", class: data-construction}
  - {header: "SyntheMol", quote: "We designed SyntheMol, a generative model that builds easily synthesizable molecules from a combinatorial chemical space, which consists of readily purchasable molecular building blocks along with well-validated chemical reactions that combine two or three building blocks.", class: definition}
  - {header: "Generation Results", quote: "Prior to running SyntheMol for antibiotic discovery, we evaluated it in silico using cLogP, the computed octanol-water partition coefficient.", class: sanity-check}
  - {header: "A. Baumannii Validation", quote: "We validate those 58 synthesized molecules by performing growth inhibition assays against A. baumannii ATCC 17978, the same strain used for training set curation.", class: experimental-bridge}

C4_figure_callouts:
  - "Figure 2: cLogP for random REAL molecules and molecules generated by SyntheMol with a Chemprop predictor for cLogP trained for 1 or 30 epochs."
  - "Figure 4: (a) A heat map summarizing the minimum inhibitory concentrations (MIC) of the 58 synthesized molecules generated by SyntheMol against A. baumannii ATCC 17978 with or without a permeabilzation agent."

C5_quant_with_stats:
  - "ROC-AUCs in the range 0.80–0.84 and PRC-AUCs in the range 0.35–0.40"
  - "61.42% were active, representing a 1,396x increase in hit rate compared to 0.044% active molecules in a random sample"
  - "2,868 (12%) of the 24,335 generated molecules scoring ≥ 0.5 compared to 1 (0.004%) of 25,000 random REAL molecules"
  - "58 (83%) were synthesized in 4 weeks"
  - "minimum inhibitory concentration (MIC) ≤ 8 µg/mL ... a remarkable 10% hit rate"
C6_baseline_comparison: "As a control, we tested 58 randomly selected molecules from the Enamine REAL Space. None of these compounds displayed antibacterial activity against A. baumannii ATCC 17978..."
C7_robustness_phrase: "synthesis success rates of over 80% within 3 to 4 weeks"
C8_generalization_phrase: "broad-spectrum antibacterial activity against all species except P. aeruginosa"

D1_discussion_open (Conclusion): "We developed SyntheMol, a novel generative AI model for small molecule drug design that uses molecular property prediction models in conjunction with MCTS to explore a vast combinatorial chemical space for promising molecules."
D2_limitation: "broad-spectrum antibacterial activity against all species except P. aeruginosa, which is likely due to the impermeability commonly displayed by the cell envelope of this species" (within-results limitation phrasing)
D3_outlook: "This work demonstrates the utility of generative AI to design structurally novel, synthetically tractable, and effective small molecule antibiotic candidates."
D4_paper_closing_sentence: same as D3.

G1_hedges_used: "likely due to", "Remarkably", "potentially"
G2_strong_verbs: "synthesize", "validate", "explore", "assemble"
G3_paragraph_connectives: "Remarkably", "However, a major limitation ...", "In contrast", "As a control"
G4_taken_together: "This work demonstrates the utility of generative AI..."

notable: The "two-gap" abstract structure (s3 = property models scale poorly; s4 = generative models are unsynthesizable; s5 = SyntheMol resolves both) is a clean rhetorical template — a "neither prior approach was good enough; here is the synthesis" move. The control experiment ("we tested 58 randomly selected molecules ... None displayed activity") is a textbook way to establish enrichment in a discovery paper.

---

## Paper 5: Wang et al., RetroExplainer (Nature Communications, 2023)
- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC10547708/
- journal: Nature Communications
- year: 2023
- category: methods

A1_title: "Retrosynthesis prediction with an interpretable deep-learning framework based on molecular assembly tasks"

A2_abstract_map:
  - s1 [field framing]: "Automating retrosynthesis with artificial intelligence expedites organic chemistry research in digital laboratories."
  - s2 [gap]: "However, most existing deep-learning approaches are hard to explain, like a 'black box' with few insights."
  - s3 [pivot]: "Here, we propose RetroExplainer, formulizing the retrosynthesis task into a molecular assembly process, containing several retrosynthetic actions guided by deep learning."
  - s4 [components]: "To guarantee a robust performance of our model, we propose three units: a multi-sense and multi-scale Graph Transformer, structure-aware contrastive learning, and dynamic adaptive multi-task learning."
  - s5 [benchmark headline]: "The results on 12 large-scale benchmark datasets demonstrate the effectiveness of RetroExplainer, which outperforms the state-of-the-art single-step retrosynthesis approaches."
  - s6 [interpretability claim]: "In addition, the molecular assembly process renders our model with good interpretability, allowing for transparent decision-making and quantitative attribution."
  - s7 [downstream/multi-step]: "When extended to multi-step retrosynthesis planning, RetroExplainer has identified 101 pathways, in which 86.9% of the single reactions correspond to those already reported in the literature."
  - s8 [outlook]: "As a result, RetroExplainer is expected to offer valuable insights for reliable, high-throughput, and high-quality organic synthesis in drug development."

A3_here_we_pivot: "Here, we propose RetroExplainer, formulizing the retrosynthesis task into a molecular assembly process, containing several retrosynthetic actions guided by deep learning."
A4_strongest_quant_in_abstract: "101 pathways, in which 86.9% of the single reactions correspond to those already reported in the literature"

B1_intro_hook_style: domain-utility hook
B1_quote_sentence1: "Retrosynthesis aims to identify a set of appropriate reactants for the efficient synthesis of target molecules, which is indispensable and fundamental in computer-assisted synthetic planning."
B3_gap_phrases:
  - "hard to explain, like a 'black box' with few insights"
  - "limited in its flexibility in generating rare LGs"
  - "unable to predict more detailed reaction information"
B4_pivot_first2sent: "In this study, we propose RetroExplainer, a chemical knowledge and DL-guided molecular assembly approach for retrosynthesis prediction with quantitative interpretability."
B5_contributions: three units (MSMS-GT, SACL, DAMT); molecular assembly formulation; multi-step extension via Retro*.
B6_last_intro_sentence: — (closes with the contribution sentence above)

C1_results_headers:
  - "Performance comparison on USPTO benchmark datasets"
  - "RetroExplainer provides interpretable insights"
  - "Extending RetroExplainer to retrosynthesis pathway planning"
  - "Influence of reaction types"
C2_header_style: descriptive, scope-defining; the second/third headers begin with the method name
C3_section_openers:
  - {header: "Performance comparison", quote: "To assess the effectiveness of RetroExplainer, we compared it with 21 comparative retrosynthesis approaches on three commonly used USPTO benchmark datasets (USPTO-50K, USPTO-FULL, and USPTO-MIT).", class: benchmark-setup}
  - {header: "Interpretable insights", quote: "Inspired by the SN2 mechanism, we designed a transparent decision process via DL-guided molecular assembly for the interpretable retrosynthesis prediction.", class: design-rationale}
  - {header: "Pathway planning", quote: "In order to improve the practicality of our RetroExplainer for pathway planning, we incorporated our model with the Retro* algorithm along with a list of purchasable molecules.", class: capability-extension}

C4_figure_callouts:
  - "The pipeline of RetroExplainer. We formulated the whole process as four distinct phases: (1) molecular graph encoding, (2) multi-task learning, (3) decision-making, and (4) prediction or multi-step pathway planning."
  - "The searching routes of two predictions, including reactions with and without leaving groups."

C5_quant_with_stats:
  - "Top-1 accuracy on USPTO-50K: 66.8% (vs. LocalRetro 63.9%)"
  - "Top-3 accuracy on USPTO-50K: 88.0%"
  - "Top-5 accuracy on USPTO-50K: 92.5%"
  - "USPTO-FULL top-1 accuracy: 51.4% (vs. R-SMILES 48.9%)"
  - "86.9% of 153 reactions found in literature"
C6_baseline_comparison: "we compared it with 21 comparative retrosynthesis approaches"
C7_robustness_phrase: "robust performance of our model" (abstract); ablations in dedicated subsection.
C8_generalization_phrase: "12 large-scale benchmark datasets"

D1_discussion_open: "Although RetroExplainer achieves impressive performance and interpretability, there are several limitations in our proposed method that deserve further research in the future."
D2_limitation: "our LGM method is limited in its flexibility in generating rare LGs"; "our RetroExplainer is unable to predict more detailed reaction information, such as reaction operations, temperature, and duration"
D3_outlook: "is expected to offer valuable insights for reliable, high-throughput, and high-quality organic synthesis in drug development" (abstract carry-over)
D4_paper_closing_sentence: "The complete training phase for the USPTO-50K dataset takes around 40 hours when the reaction type is provided and 38 hours when it is not provided, utilizing a single RTX3090 GPU core." (final substantive sentence)

G1_hedges_used: "is expected to", "deserve further research", "limited in its flexibility"
G2_strong_verbs: "outperforms", "renders", "identifies", "extends"
G3_paragraph_connectives: "However", "In addition", "When extended", "As a result", "Although"
G4_taken_together: "As a result, RetroExplainer is expected to offer valuable insights..."

notable: Discussion opens unusually with a frank concession ("Although RetroExplainer achieves impressive performance and interpretability, there are several limitations ...") — a confident-but-self-aware opener. Multi-step pathway claim (101 pathways, 86.9% literature-matched) is the kind of "downstream evidence" Nature Communications methods papers like to anchor.

---

## Paper 6: Cretu et al. / Atz et al., DRAGONFLY — Prospective de novo drug design with deep interactome learning (Nature Communications, 2024)
- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC11035696/
- journal: Nature Communications
- year: 2024
- category: methods + application (prospective design, X-ray validation)

A1_title: "Prospective de novo drug design with deep interactome learning"

A2_abstract_map:
  - s1 [field definition]: "De novo drug design aims to generate molecules from scratch that possess specific chemical and pharmacological properties."
  - s2 [pivot]: "We present a computational approach utilizing interactome-based deep learning for ligand- and structure-based generation of drug-like molecules."
  - s3 [novelty/positioning]: "This method capitalizes on the unique strengths of both graph neural networks and chemical language models, offering an alternative to the need for application-specific reinforcement, transfer, or few-shot learning."
  - s4 [capability]: "It enables the 'zero-shot' construction of compound libraries tailored to possess specific bioactivity, synthesizability, and structural novelty."
  - s5 [prospective task]: "In order to proactively evaluate the deep interactome learning framework for protein structure-based drug design, potential new ligands targeting the binding site of the human peroxisome proliferator-activated receptor (PPAR) subtype gamma are generated."
  - s6 [validation chain]: "The top-ranking designs are chemically synthesized and computationally, biophysically, and biochemically characterized."
  - s7 [bioactivity payload]: "Potent PPAR partial agonists are identified, demonstrating favorable activity and the desired selectivity profiles for both nuclear receptors and off-target interactions."
  - s8 [structural validation]: "Crystal structure determination of the ligand-receptor complex confirms the anticipated binding mode."
  - s9 [meta-claim]: "This successful outcome positively advocates interactome-based de novo design for application in bioorganic and medicinal chemistry, enabling the creation of innovative bioactive molecules."

A3_here_we_pivot: "To address the goal of studying the drug-target interactome comprehensively, we propose an approach that combines a CLM with interactome-based deep learning."
A4_strongest_quant_in_abstract: qualitative strength via experimental ladder ("synthesized and computationally, biophysically, and biochemically characterized" + "Crystal structure determination ... confirms the anticipated binding mode")

B1_intro_hook_style: definitional/textbook hook
B1_quote_sentence1: "Computational de novo design encompasses the autonomous generation of new molecules with desired properties from scratch."
B3_gap_phrases:
  - "alternative to the need for application-specific reinforcement, transfer, or few-shot learning"
  - "zero-shot construction of compound libraries"
  - "comparably cumbersome, requiring 10 and 5 synthesis steps"
B4_pivot_first2sent: "To address the goal of studying the drug-target interactome comprehensively, we propose an approach that combines a CLM with interactome-based deep learning."
B5_contributions: DRAGONFLY = CLM + GNN over a drug-target interactome graph; zero-shot design; prospective PPARγ validation including X-ray.
B6_last_intro_sentence: — (pivot above)

C1_results_headers:
  - "DRAGONFLY enables ligand- and structure-based molecular design"
  - "DRAGONFLY considers synthesizability, novelty, bioactivity, and physicochemical properties for ligand design"
  - "DRAGONFLY outperforms standard chemical language models for molecular design"
  - "Structure-based design with DRAGONFLY generates potential novel ligands"
  - "Molecules generated with DRAGONFLY potently and selectively activate PPARγ"
C2_header_style: every header is "DRAGONFLY <verb>..." — most aggressive method-name-as-subject convention in this set.
C3_section_openers:
  - {header: "Ligand- and structure-based design", quote: "The central component of DRAGONFLY is its drug-target interactome, which captures the connections between small-molecule ligands and their macromolecular targets.", class: definition}
  - {header: "Synthesizability/novelty", quote: "The theoretical evaluation of DRAGONFLY focused on investigating the incorporation of specific physical and chemical properties into the DRAGONFLY model, as depicted in Fig. 2a.", class: setup-for-quant}
  - {header: "Outperforms RNNs", quote: "The evaluation criteria, which encompassed synthesizability, novelty, and predicted bioactivity were applied to evaluate virtual libraries generated de novo.", class: criterion-restatement}
  - {header: "Structure-based PPARγ design", quote: "DRAGONFLY was utilized in a prospective manner for structure-based ligand design targeting human PPARγ.", class: prospective-pivot}
  - {header: "Potent PPAR activation", quote: "Subsequent biological testing of the three molecules (1–3) in a cell-based reporter gene assay confirmed the intended activity profiles.", class: experimental-confirmation}

C4_figure_callouts:
  - "Compound 1 bound in the orthosteric site lined by helices H3 and H11."
  - "The buried propionic acid head group is engaged in four intermolecular hydrogen bridges."

C5_quant_with_stats:
  - "Interactome: ~360,000 ligands, 2989 targets, and around 500,000 bioactivities"
  - "Pearson correlation coefficients (r) greater than or equal to 0.95 for all assessed physical and chemical properties"
  - "mean absolute errors (MAEs) for the predicted pIC50 values were equal to or less than 0.6"
  - "Compound 1: EC50(PPARγ) = 1.5 ± 0.2 μM, EC50(PPARδ) = 0.24 ± 0.05 μM, KD = 0.8 ± 0.1 μM"
  - "Compound 2: EC50 value of 2.3 ± 0.7 μM"
C6_baseline_comparison: "DRAGONFLY vs. RNN novelty: 99.7 ± 0.1% vs. 92.2 ± 0.4%"
C7_robustness_phrase: "favorable activity and the desired selectivity profiles for both nuclear receptors and off-target interactions"
C8_generalization_phrase: "zero-shot construction of compound libraries tailored to possess specific bioactivity, synthesizability, and structural novelty"

D1_discussion_open: "The generative deep learning method referred to as DRAGONFLY was evaluated in the context of ligand-based and structure-based molecular design tasks. The collective results specifically highlight the success of structure-based de novo design of potent partial agonists for PPARγ."
D2_limitation: "The chemical synthesis of two top-ranking de novo designs, designated as compounds 1 and 2, along with regioisomer 3, turned out to be comparably cumbersome, requiring 10 and 5 synthesis steps, respectively."; "Further studies will be essential to combine DRAGONFLY with scoring functions not involving known active query ligands for bioaffinity assessment."
D3_outlook: "By leveraging data-driven deep learning and interaction networks, this approach offers new avenues for foundation models enabling tailored molecular design strategies and the discovery of innovative drug candidates."
D4_paper_closing_sentence: same as D3.

G1_hedges_used: "comparably cumbersome", "Further studies will be essential", "potential new ligands"
G2_strong_verbs: "potently activate", "advocates", "confirms", "outperforms", "enables"
G3_paragraph_connectives: "Subsequent ...", "In order to proactively evaluate ...", "Collective results"
G4_taken_together: "The collective results specifically highlight the success of structure-based de novo design of potent partial agonists for PPARγ."

notable: Abstract sentences 6-8 read like a 3-step experimental ladder ("synthesized → biophysically/biochemically characterized → crystal structure confirms binding mode") — a rhetorical move that signals "we did the full chain." The verb "advocates" in s9 is unusually strong for an abstract closing sentence and reads as a deliberate rhetorical flourish.

---

## Cross-paper observations

- **Method-name-as-subject is the dominant header convention.** DynamicBind, RetroExplainer, and especially DRAGONFLY ("DRAGONFLY enables...", "DRAGONFLY considers...", "DRAGONFLY outperforms...") use the model name as the syntactic subject of nearly every Results subsection. This signals confidence and creates a "method as protagonist" narrative.

- **Two-gap abstracts are the standard rhetorical scaffold.** SyntheMol explicitly contrasts two prior approaches (property prediction scales poorly; generative models are unsynthesizable) before introducing the synthesis. Wong/Stokes use "deep learning works ... but is black-box". DynamicBind uses "rigid docking ... or expensive MD". All converge on the same pattern: state two complementary failures of prior work, then resolve both.

- **"Here, we ..." remains the canonical pivot sentence.** Every paper has an explicit "Here, we ..." (or "In this study, we ...") sentence that introduces the method or hypothesis — usually as the third or fourth sentence of the abstract or the last sentence of the introduction.

- **Discovery papers package the experimental ladder into one dense abstract sentence.** Wong's MRSA sentence packs four claims (selectivity, two pathogens, resistance, two mouse models) into one sentence; DRAGONFLY's "synthesized and computationally, biophysically, and biochemically characterized" + crystal-structure confirmation does the same. This compression signals to reviewers that the in vivo / structural validation chain is complete.

- **Quantitative anchors in abstracts use scale, fold-change, or hit-rate.** "12,076,365 compounds", "30 billion molecules", "1,396x increase in hit rate", "86.9% of single reactions correspond to those already reported in the literature". Method papers favor benchmark-relative numbers; discovery papers favor scale-of-screen and in-vivo phenotypic numbers.

- **Limitations are stated, but immediately reframed as future-work pivots.** RetroExplainer explicitly acknowledges "several limitations" at the start of the discussion. DynamicBind names a generalization limit and then proposes self-distillation as the remedy. The pattern is "limitation X → remedy Y" within the same paragraph, never a standalone limitation paragraph.

- **Crisis hooks dominate antibiotic-discovery papers.** Stokes 2020 ("Since the discovery of penicillin..."), Wong 2024 ("ongoing antibiotic resistance crisis"), SyntheMol ("rise of pan-resistant bacteria"). All three open with a public-health framing before any technical detail. Method-only papers (DynamicBind, RetroExplainer, Uni-Mol+, DRAGONFLY) instead open with a field-progress or definitional hook.

- **Strong control comparisons are explicit and named.** SyntheMol: "we tested 58 randomly selected molecules ... None of these compounds displayed antibacterial activity." Wong et al.: contrasts hit rates between rationale-bearing (44%) and non-rationale (9.1%) compounds. The explicit "as a control" or paired comparison is treated as load-bearing evidence rather than a footnote.

- **In vivo / structural validation is the closer for discovery papers.** Stokes ends with murine efficacy. Wong ends with MRSA mouse models. DRAGONFLY ends with X-ray crystal structure. The sequence is consistent: in silico → in vitro → cellular → in vivo / structural.

- **Hedging is sparing and concentrated in the discussion.** "could", "may", "is expected to", "shows potential" appear almost exclusively in discussion/outlook paragraphs. Abstracts use unhedged active verbs ("identifies", "outperforms", "demonstrates", "discovers", "confirms"). The asymmetry is a reliable Nature-family marker.
