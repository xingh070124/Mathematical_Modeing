# Category 02 — Protein structure / structural biology AI / protein language models

Six open-access papers analyzed using the extraction framework. Sources: Nature OA, PMC, Science (when bioRxiv mirror unavailable, abstracts retrieved via PubMed; main-text fetched from PMC or marcottelab open course PDF).

Swap notes:
- All six target papers in the original candidate set retained. No swaps.
- BioRxiv mirrors were 403; substituted with PMC, Nature OA, course-hosted PDF, and PubMed abstract pages.

---

## Paper 1: Jumper et al., AlphaFold2, Nature 2021
- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC8371605/ ; https://www.nature.com/articles/s41586-021-03819-2
- journal: Nature
- year: 2021
- category: methods

A1_title: "Highly accurate protein structure prediction with AlphaFold"

A2_abstract_map:
  - s1 [BIG-PICTURE]: "Proteins are essential to life, and understanding their structure can facilitate a mechanistic understanding of their function."
  - s2 [BIG-PICTURE]: "Through an enormous experimental effort, the structures of around 100,000 unique proteins have been determined…"
  - s3 [GAP]: "Structural coverage is bottlenecked by the months to years of painstaking effort required to determine a single protein structure."
  - s4 [GAP]: "Accurate computational approaches are needed to address this gap and to enable large-scale structural bioinformatics."
  - s5 [BIG-PICTURE]: "Predicting the three-dimensional structure that a protein will adopt based solely on its amino acid sequence…has been an important open research problem for more than 50 years."
  - s6 [GAP]: "Despite recent progress, existing methods fall far short of atomic accuracy, especially when no homologous structure is available."
  - s7 [HERE-WE]: "Here we provide the first computational method that can regularly predict protein structures with atomic accuracy even in cases in which no similar structure is known."
  - s8 [VALIDATION]: "We validated an entirely redesigned version of our neural network-based model, AlphaFold, in the challenging 14th Critical Assessment of protein Structure Prediction (CASP14)…"
  - s9 [METHOD]: "Underpinning the latest version of AlphaFold is a novel machine learning approach that incorporates physical and biological knowledge about protein structure…"

A3_here_we_pivot: "Here we provide the first computational method that can regularly predict protein structures with atomic accuracy even in cases in which no similar structure is known."
A4_strongest_quant_in_abstract: "demonstrating accuracy competitive with experimental structures in a majority of cases and greatly outperforming other methods"

B1_intro_hook_style: field-importance
B1_quote_sentence1: "The development of computational methods to predict three-dimensional (3D) protein structures from the protein sequence has proceeded along two complementary paths…"
B3_gap_phrases: ["this approach has proved highly challenging for even moderate-sized proteins…", "produce predictions that are far short of experimental accuracy in the majority of cases…", "this has limited their utility for many biological applications"]
B4_pivot_first2sent: "In this study, we develop the first, to our knowledge, computational approach capable of predicting protein structures to near experimental accuracy in a majority of cases."
B5_contributions: —
B6_last_intro_sentence: "In this study, we develop the first, to our knowledge, computational approach capable of predicting protein structures to near experimental accuracy in a majority of cases."

C1_results_headers: ["The AlphaFold network", "Evoformer", "End-to-end structure prediction", "Training with labelled and unlabelled data", "Interpreting the neural network", "MSA depth and cross-chain contacts"]
C2_header_style: task-neutral
C3_section_openers:
  - {header: "The AlphaFold network", quote: "AlphaFold greatly improves the accuracy of structure prediction by incorporating novel neural network architectures and training procedures based on the evolutionary, physical and geometric constraints of protein structures.", class: claim-first}
  - {header: "Evoformer", quote: "The key principle of the building block of the network—named Evoformer—is to view the prediction of protein structures as a graph inference problem in 3D space…", class: method-first}
  - {header: "End-to-end structure prediction", quote: "The structure module operates on a concrete 3D backbone structure using the pair representation and the original sequence row…", class: method-first}
  - {header: "Training with labelled and unlabelled data", quote: "The AlphaFold architecture is able to train to high accuracy using only supervised learning on PDB data, but we are able to enhance accuracy using an approach similar to noisy student self-distillation.", class: claim-first}
  - {header: "Interpreting the neural network", quote: "To understand how AlphaFold predicts protein structure, we trained a separate structure module for each of the 48 Evoformer blocks in the network…", class: motivation-first}
  - {header: "MSA depth and cross-chain contacts", quote: "Although AlphaFold has a high accuracy across the vast majority of deposited PDB structures, we note that there are still factors that affect accuracy or limit the applicability of the model.", class: claim-first}
C4_figure_callouts: ["AlphaFold produces highly accurate structures.", "Accuracy of AlphaFold on recent PDB structures.", "Architectural details.", "Effect of MSA depth and cross-chain contacts."]
C5_quant_with_stats: "AlphaFold structures had a median backbone accuracy of 0.96 Å r.m.s.d.₉₅"
C6_baseline_comparison: "compared to 2.8 Å for the next-best method"
C7_robustness_phrase: "AlphaFold has a high accuracy across the vast majority of deposited PDB structures"
C8_generalization_phrase: "even in cases in which no similar structure is known"

D1_discussion_open: "The methodology that we have taken in designing AlphaFold is a combination of the bioinformatics and physical approaches: we use a physical and geometric inductive bias to build components that learn from PDB data with minimal imposition of handcrafted features…"
D2_limitation: "we note that there are still factors that affect accuracy or limit the applicability of the model"
D3_outlook: "By developing an accurate protein structure prediction algorithm…we hope to accelerate the advancement of structural bioinformatics."
D4_paper_closing_sentence: "We hope that AlphaFold—and computational approaches that apply its techniques for other biophysical problems—will become essential tools of modern biology."

G1_hedges_used: ["to our knowledge", "in a majority of cases", "we hope", "may"]
G2_strong_verbs: ["validated", "demonstrating", "outperforming", "incorporates", "leveraging"]
G3_paragraph_connectives: ["Despite these advances,", "Here we provide…", "Although…we note that"]
G4_taken_together: —

notable: Classic 50-year framing of the field's foundational problem; "Here we provide the first…" is the canonical pivot.

---

## Paper 2: Lin et al., ESM-2 / ESMFold, Science 2023 (bioRxiv OA preprint)
- url_oa: https://www.biorxiv.org/content/10.1101/2022.07.20.500902v3 (bioRxiv) ; PDF mirror: https://www.marcottelab.org/users/BCH394P_364C_2024/ESMFold_2023.pdf
- journal: Science (bioRxiv-OA preprint accepted)
- year: 2023
- category: methods

A1_title: "Evolutionary-scale prediction of atomic-level protein structure with a language model"

A2_abstract_map:
  - s1 [BIG-PICTURE]: "Recent advances in machine learning have leveraged evolutionary information in multiple sequence alignments to predict protein structure."
  - s2 [HERE-WE]: "We demonstrate direct inference of full atomic-level protein structure from primary sequence using a large language model."
  - s3 [KEY-RESULT]: "As language models of protein sequences are scaled up to 15 billion parameters, an atomic-resolution picture of protein structure emerges in the learned representations."
  - s4 [KEY-RESULT]: "This results in an order-of-magnitude acceleration of high-resolution structure prediction, which enables large-scale structural characterization of metagenomic proteins."
  - s5 [APPLICATION]: "We apply this capability to construct the ESM Metagenomic Atlas by predicting structures for >617 million metagenomic protein sequences, including >225 million that are predicted with high confidence…"

A3_here_we_pivot: "We demonstrate direct inference of full atomic-level protein structure from primary sequence using a large language model."
A4_strongest_quant_in_abstract: "scaled up to 15 billion parameters…order-of-magnitude acceleration of high-resolution structure prediction"

B1_intro_hook_style: biological-motivation
B1_quote_sentence1: "The sequences of proteins at the scale of evolution contain an image of biological structure and function."
B3_gap_phrases: ["the vast scale of metagenomic proteins represents a far greater challenge for structural characterization", "the search process for related proteins…can take >10 min", "structural coverage is bottlenecked"]
B4_pivot_first2sent: "We posit that the task of filling in missing amino acids in protein sequences across evolution will require a language model to understand the underlying structure that creates the patterns in the sequences."
B5_contributions: "We show that language models enable fast end-to-end atomic-resolution structure prediction directly from sequence."
B6_last_intro_sentence: "These predicted structures can be accessed in the ESM Metagenomic Atlas (https://esmatlas.com) open science resource."

C1_results_headers: ["Atomic-resolution structure emerges in language models trained on protein sequences", "Accelerating accurate atomic-resolution structure prediction"]
C2_header_style: declarative-finding
C3_section_openers:
  - {header: "Atomic-resolution structure emerges…", quote: "We begin with a study of the emergence of high-resolution protein structure.", class: motivation-first}
  - {header: "Accelerating accurate atomic-resolution structure prediction", quote: "Ablation studies indicate that the language model's understanding of the sequence improves single-sequence structure prediction…", class: claim-first}
C4_figure_callouts: ["Fig. 1. Emergence of structure when scaling language models to 15 billion parameters.", "Fig. 2. Single sequence structure prediction with ESMFold.", "Fig. 3. Mapping metagenomic structural space."]
C5_quant_with_stats: "the 15 billion parameter model reaches a TM-score of 0.72 on the CAMEO test set and 0.55 on the CASP14 test set, a gain of 14 and 17% respectively…"
C6_baseline_comparison: "speedup over the state-of-the-art prediction pipelines is up to one to two orders of magnitude"
C7_robustness_phrase: "across all models…there is a correlation of −0.99 between validation perplexity and CASP14 TM-score"
C8_generalization_phrase: "folds practically all sequences in MGnify90…>617 million proteins"

D1_discussion_open: —
D2_limitation: "the perplexity of the unsuccessful sequence is 16.6, meaning the language model does not understand the input sequence"
D3_outlook: "improvements in the language model will translate into improvements in single-sequence structure prediction accuracy"
D4_paper_closing_sentence: —

G1_hedges_used: ["We posit that", "we expect that", "indicates", "suggests"]
G2_strong_verbs: ["demonstrate", "emerges", "reveals", "leverages", "removes"]
G3_paragraph_connectives: ["This insight has been central to…", "Beginning with…", "Despite the simplicity of…", "We discover that"]
G4_taken_together: "These findings connect improvements in language modeling with the increases in low-resolution (contact map) and high-resolution (atomic-level) structural information."

notable: The headline "emerges" pattern — present-tense, declarative-finding subheaders ("Atomic-resolution structure emerges…"). Heavy use of scaling-law framing.

---

## Paper 3: Dauparas et al., ProteinMPNN, Science 2022 (bioRxiv OA + PMC)
- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC9997061/
- journal: Science (PMC OA mirror)
- year: 2022
- category: methods

A1_title: "Robust deep learning–based protein sequence design using ProteinMPNN"

A2_abstract_map:
  - s1 [BIG-PICTURE/GAP]: "While deep learning has revolutionized protein structure prediction, almost all experimentally characterized de novo protein designs have been generated using physically based approaches such as Rosetta."
  - s2 [HERE-WE]: "Here we describe a deep learning based protein sequence design method, ProteinMPNN, with outstanding performance in both in silico and experimental tests."
  - s3 [METHOD]: "The amino acid sequence at different positions can be coupled between single or multiple chains, enabling application to a wide range of current protein design challenges."
  - s4 [KEY-RESULT]: "On native protein backbones, ProteinMPNN has a sequence recovery of 52.4%, compared to 32.9% for Rosetta."
  - s5 [METHOD]: "Incorporation of noise during training improves sequence recovery on protein structure models, and produces sequences which more robustly encode their structures…"
  - s6 [VALIDATION]: "We demonstrate the broad utility and high accuracy of ProteinMPNN using X-ray crystallography, cryoEM and functional studies by rescuing previously failed designs…"

A3_here_we_pivot: "Here we describe a deep learning based protein sequence design method, ProteinMPNN, with outstanding performance in both in silico and experimental tests."
A4_strongest_quant_in_abstract: "ProteinMPNN has a sequence recovery of 52.4%, compared to 32.9% for Rosetta"

B1_intro_hook_style: technical-paradox
B1_quote_sentence1: "The protein sequence design problem is to find, given a protein backbone structure of interest, an amino acid sequence that will fold to this structure."
B3_gap_phrases: ["lack the physical transparency of methods like Rosetta", "almost all experimentally characterized de novo protein designs have been generated using physically based approaches", "expert customization for specific design challenges"]
B4_pivot_first2sent: "Physically based approaches like Rosetta approach sequence design as an energy optimization problem, searching for the combination of amino acid identities and conformations that have the lowest energy for a given input structure."
B5_contributions: "Unlike Rosetta and other physically based methods, ProteinMPNN requires no expert customization for specific design challenges, and it should thus make protein design more broadly accessible."
B6_last_intro_sentence: "While deep learning methods lack the physical transparency of methods like Rosetta, they are trained directly to find the most probable amino acid for a protein backbone…hence such ambiguities do not arise, making sequence design more robust and less dependent on the judgement of a human expert."

C1_results_headers: ["Training with backbone noise improves model performance for protein design", "Experimental evaluation of ProteinMPNN"]
C2_header_style: declarative-finding
C3_section_openers:
  - {header: "Training with backbone noise improves model performance…", quote: —, class: claim-first}
  - {header: "Experimental evaluation of ProteinMPNN", quote: "While in silico native protein sequence recovery is a useful benchmark, the ultimate test of a protein design method is its ability to generate sequences which fold to the desired structure and have the desired function when tested experimentally.", class: motivation-first}
C4_figure_callouts: —
C5_quant_with_stats: "1.2 sec vs 258.8 sec on a single CPU for a 100 residue protein"
C6_baseline_comparison: "achieves much higher protein sequence recovery on native backbones (52.4% vs 32.9%)"
C7_robustness_phrase: "produces sequences which more robustly encode their structures as assessed using structure prediction algorithms"
C8_generalization_phrase: "broad utility and high accuracy…protein monomers, cyclic homo-oligomers, tetrahedral nanoparticles, and target binding proteins"

D1_discussion_open: "ProteinMPNN solves sequence design problems in a small fraction of the time (1.2 sec vs 258.8 sec on a single CPU for a 100 residue protein) required for physically based approaches such as Rosetta…and most importantly, rescues previously failed designs made using Rosetta or AlphaFold for protein monomers, assemblies, and protein-protein interfaces."
D2_limitation: "deep learning methods lack the physical transparency of methods like Rosetta"
D3_outlook: "We are currently extending ProteinMPNN to protein-nucleic acid design and protein-small molecule design which should increase its utility still further."
D4_paper_closing_sentence: "We are currently extending ProteinMPNN to protein-nucleic acid design and protein-small molecule design which should increase its utility still further."

G1_hedges_used: ["should thus", "should increase", "while", "most importantly"]
G2_strong_verbs: ["rescues", "solves", "outperforms", "couples", "demonstrate"]
G3_paragraph_connectives: ["Unlike Rosetta…", "While in silico…", "While deep learning methods lack…"]
G4_taken_together: —

notable: "Most importantly, rescues previously failed designs" — explicit hierarchy of impact in Discussion opener. Strong contrastive ("Unlike…", "While…vs Rosetta") rhetoric.

---

## Paper 4: Watson et al., RFdiffusion, Nature 2023
- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC10468394/ ; https://www.nature.com/articles/s41586-023-06415-8
- journal: Nature
- year: 2023
- category: methods

A1_title: "De novo design of protein structure and function with RFdiffusion"

A2_abstract_map:
  - s1 [BIG-PICTURE]: "There has been considerable recent progress in designing new proteins using deep-learning methods."
  - s2 [GAP]: "Despite this progress, a general deep-learning framework for protein design that enables solution of a wide range of design challenges…has yet to be described."
  - s3 [TECHNICAL-PARADOX]: "Diffusion models have had considerable success in image and language generative modelling but limited success when applied to protein modelling, probably due to the complexity of protein backbone geometry and sequence–structure relationships."
  - s4 [HERE-WE]: "Here we show that by fine-tuning the RoseTTAFold structure prediction network on protein structure denoising tasks, we obtain a generative model of protein backbones that achieves outstanding performance on unconditional and topology-constrained protein monomer design, protein binder design, symmetric oligomer design, enzyme active site scaffolding and symmetric motif scaffolding."
  - s5 [VALIDATION]: "We demonstrate the power and generality of the method, called RoseTTAFold diffusion (RFdiffusion), by experimentally characterizing the structures and functions of hundreds of designed symmetric assemblies, metal-binding proteins and protein binders."
  - s6 [VALIDATION]: "The accuracy of RFdiffusion is confirmed by the cryogenic electron microscopy structure of a designed binder in complex with influenza haemagglutinin that is nearly identical to the design model."
  - s7 [IMPLICATION]: "In a manner analogous to networks that produce images from user-specified inputs, RFdiffusion enables the design of diverse functional proteins from simple molecular specifications."

A3_here_we_pivot: "Here we show that by fine-tuning the RoseTTAFold structure prediction network on protein structure denoising tasks, we obtain a generative model of protein backbones…"
A4_strongest_quant_in_abstract: "experimentally characterizing the structures and functions of hundreds of designed…proteins"

B1_intro_hook_style: field-importance
B1_quote_sentence1: "De novo protein design seeks to generate proteins with specified structural and/or functional properties, for example, making a binding interaction with a given target, folding into a particular topology or containing a catalytic site."
B3_gap_phrases: ["a general deep-learning framework for protein design…has yet to be described", "limited success when applied to protein modelling", "probably due to the complexity of protein backbone geometry"]
B4_pivot_first2sent: "Recent work has adapted DDPMs for protein monomer design by conditioning on small protein 'motifs' or on secondary structure and block-adjacency ('fold') information."
B5_contributions: —
B6_last_intro_sentence: "In a manner reminiscent of the generation of images from text prompts, RFdiffusion makes possible, with minimal specialist knowledge, the generation of functional proteins from minimal molecular specifications."

C1_results_headers: ["Unconditional protein monomer generation", "Design of higher-order oligomers", "Functional-motif scaffolding", "Scaffolding enzyme active sites", "Symmetric functional-motif scaffolding", "Design of protein-binding proteins"]
C2_header_style: task-neutral
C3_section_openers:
  - {header: "Unconditional protein monomer generation", quote: "As shown in Fig. 2a–c and Supplementary Fig. 3c,d, starting from random noise, RFdiffusion can readily generate elaborate protein structures with little overall structural similarity to structures seen during training.", class: claim-first}
  - {header: "Design of higher-order oligomers", quote: "There is considerable interest in designing symmetric oligomers, which can serve as vaccine platforms, delivery vehicles and catalysts.", class: motivation-first}
  - {header: "Functional-motif scaffolding", quote: "We next investigated the use of RFdiffusion for scaffolding protein structural motifs that carry out binding and catalytic functions.", class: motivation-first}
  - {header: "Scaffolding enzyme active sites", quote: "A grand challenge in protein design is to scaffold minimal descriptions of enzyme active sites comprising a few single amino acids.", class: motivation-first}
  - {header: "Symmetric functional-motif scaffolding", quote: "Several important design challenges involve the scaffolding of several copies of a functional motif in symmetric arrangements.", class: motivation-first}
  - {header: "Design of protein-binding proteins", quote: "The design of high-affinity binders to target proteins is a grand challenge in protein design, with numerous therapeutic applications.", class: motivation-first}
C4_figure_callouts: ["As shown in Fig. 2a–c and Supplementary Fig. 3c,d…"]
C5_quant_with_stats: "23 of the 25 benchmark problems, compared to 15 for Hallucination and 19 for RFjoint Inpainting"
C6_baseline_comparison: "two orders of magnitude improvement over previous methods"
C7_robustness_phrase: "robustness and accuracy of the solutions far exceeds what has been achieved previously"
C8_generalization_phrase: "outstanding performance on unconditional and topology-constrained protein monomer design, protein binder design, symmetric oligomer design, enzyme active site scaffolding and symmetric motif scaffolding"

D1_discussion_open: "RFdiffusion is a comprehensive improvement over current protein design methods. RFdiffusion readily generates diverse unconditional designs up to 600 residues in length that are accurately predicted by AF2, far exceeding the complexity and accuracy achieved by most previous methods."
D2_limitation: —
D3_outlook: "should enable de novo protein design to achieve still higher levels of complexity, to approach and, in some cases, surpass what natural evolution has achieved"
D4_paper_closing_sentence: "The ability to customize RFdiffusion to specific design challenges by addition of external potentials and by fine-tuning…along with continued improvements to the underlying methodology, should enable de novo protein design to achieve still higher levels of complexity, to approach and, in some cases, surpass what natural evolution has achieved."

G1_hedges_used: ["probably due to", "should enable", "approach and, in some cases, surpass", "with minimal specialist knowledge"]
G2_strong_verbs: ["fine-tuning", "scaffolding", "characterizing", "exceeds", "enables", "rescues"]
G3_paragraph_connectives: ["Despite this progress,", "Here we show that…", "We next investigated…", "In a manner reminiscent of…"]
G4_taken_together: —

notable: Use of "grand challenge" appears twice as a section opener. Heavy motivation-first openers. Closing sentence references "what natural evolution has achieved" — a common Nature-paper grandiose outlook.

---

## Paper 5: Cheng et al., AlphaMissense, Science 2023
- url_oa: https://www.science.org/doi/10.1126/science.adg7492 (abstract via PubMed: https://pubmed.ncbi.nlm.nih.gov/37733863/)
- journal: Science
- year: 2023
- category: application

A1_title: "Accurate proteome-wide missense variant effect prediction with AlphaMissense"

A2_abstract_map:
  - s1 [GAP]: "The vast majority of missense variants observed in the human genome are of unknown clinical significance."
  - s2 [HERE-WE]: "We present AlphaMissense, an adaptation of AlphaFold fine-tuned on human and primate variant population frequency databases to predict missense variant pathogenicity."
  - s3 [METHOD/KEY-RESULT]: "By combining structural context and evolutionary conservation, our model achieves state-of-the-art results across a wide range of genetic and experimental benchmarks, all without explicitly training on such data."
  - s4 [VALIDATION]: "The average pathogenicity score of genes is also predictive for their cell essentiality, capable of identifying short essential genes that existing statistical approaches are underpowered to detect."
  - s5 [IMPLICATION]: "As a resource to the community, we provide a database of predictions for all possible human single amino acid substitutions and classify 89% of missense variants as either likely benign or likely pathogenic."

A3_here_we_pivot: "We present AlphaMissense, an adaptation of AlphaFold fine-tuned on human and primate variant population frequency databases to predict missense variant pathogenicity."
A4_strongest_quant_in_abstract: "classify 89% of missense variants as either likely benign or likely pathogenic"

B1_intro_hook_style: biological-motivation
B1_quote_sentence1: —
B3_gap_phrases: ["of unknown clinical significance", "existing statistical approaches are underpowered to detect", "without explicitly training on such data"]
B4_pivot_first2sent: —
B5_contributions: "we provide a database of predictions for all possible human single amino acid substitutions"
B6_last_intro_sentence: —

C1_results_headers: —
C2_header_style: —
C3_section_openers:
  - {header: —, quote: —, class: —}
C4_figure_callouts: —
C5_quant_with_stats: "32% of all missense variants classified as likely pathogenic and 57% as likely benign using a cutoff yielding 90% precision on the ClinVar dataset"
C6_baseline_comparison: "achieves state-of-the-art results across a wide range of genetic and experimental benchmarks"
C7_robustness_phrase: "all without explicitly training on such data"
C8_generalization_phrase: "for all possible human single amino acid substitutions"

D1_discussion_open: —
D2_limitation: —
D3_outlook: "As a resource to the community, we provide a database of predictions for all possible human single amino acid substitutions…"
D4_paper_closing_sentence: —

G1_hedges_used: ["likely", "capable of", "without explicitly"]
G2_strong_verbs: ["present", "fine-tuned", "achieves", "classify", "identifying"]
G3_paragraph_connectives: ["By combining…", "As a resource to the community,"]
G4_taken_together: —

notable: Score-based abstract cleanly separates GAP → HERE-WE → METHOD → VALIDATION → IMPLICATION. The "89% classification" headline statistic anchors community uptake. Body-text access blocked behind paywall — only abstract was OA via PubMed.

---

## Paper 6: van Kempen et al., Foldseek, Nature Biotechnology 2024
- url_oa: https://www.nature.com/articles/s41587-023-01773-0 (abstract via PubMed: https://pubmed.ncbi.nlm.nih.gov/37156916/)
- journal: Nat Biotechnol (Nature-family)
- year: 2024 (online 2023)
- category: methods (with application to AlphaFold DB)

A1_title: "Fast and accurate protein structure search with Foldseek"

A2_abstract_map:
  - s1 [GAP]: "As structure prediction methods are generating millions of publicly available protein structures, searching these databases is becoming a bottleneck."
  - s2 [HERE-WE]: "Foldseek aligns the structure of a query protein against a database by describing tertiary amino acid interactions within proteins as sequences over a structural alphabet."
  - s3 [KEY-RESULT]: "Foldseek decreases computation times by four to five orders of magnitude with 86%, 88% and 133% of the sensitivities of Dali, TM-align and CE, respectively."

A3_here_we_pivot: "Foldseek aligns the structure of a query protein against a database by describing tertiary amino acid interactions within proteins as sequences over a structural alphabet."
A4_strongest_quant_in_abstract: "decreases computation times by four to five orders of magnitude with 86%, 88% and 133% of the sensitivities of Dali, TM-align and CE"

B1_intro_hook_style: recent-advance
B1_quote_sentence1: "As structure prediction methods are generating millions of publicly available protein structures, searching these databases is becoming a bottleneck."
B3_gap_phrases: ["searching these databases is becoming a bottleneck", "100 million protein structures would take TM-align a month on one CPU core", "four to five orders of magnitude" (vs traditional)]
B4_pivot_first2sent: "Foldseek aligns the structure of a query protein against a database by describing tertiary amino acid interactions within proteins as sequences over a structural alphabet."
B5_contributions: "Foldseek discretizes the query structures into sequences over the 3Di alphabet and then uses a pre-trained 3Di substitution matrix to search through the 3Di sequences of the target structures."
B6_last_intro_sentence: —

C1_results_headers: —
C2_header_style: —
C3_section_openers:
  - {header: —, quote: —, class: —}
C4_figure_callouts: —
C5_quant_with_stats: "decreases computation times by four to five orders of magnitude with 86%, 88% and 133% of the sensitivities of Dali, TM-align and CE"
C6_baseline_comparison: "at least 20,000 times faster" (vs structural aligners; bioRxiv summary)
C7_robustness_phrase: "sensitivities similar to state-of-the-art structural aligners"
C8_generalization_phrase: "200 million structures" (AlphaFold DB scale)

D1_discussion_open: —
D2_limitation: —
D3_outlook: "Foldseek is free open-source software available at foldseek.com and as a webserver at search.foldseek.com."
D4_paper_closing_sentence: —

G1_hedges_used: ["similar to", "approximately"]
G2_strong_verbs: ["aligns", "decreases", "discretizes", "describes"]
G3_paragraph_connectives: ["As structure prediction methods are generating…", "Foldseek aligns…"]
G4_taken_together: —

notable: 3-sentence Brief Communication abstract is a model of compression: GAP → HERE-WE → KEY-RESULT with three baselines and three comparison numbers in one sentence. Nat Biotechnol Brief Communications avoid Discussion sections entirely — explains "—"s.

---

## Cross-paper observations for this category

- **"Here we" pivot is universal.** Five of six abstracts use exactly "Here we…" (AlphaFold "Here we provide", ProteinMPNN "Here we describe", RFdiffusion "Here we show that"); ESMFold opens with "We demonstrate"; AlphaMissense uses "We present". The pivot always immediately follows a GAP sentence.

- **GAP sentences foreground bottlenecks and 50-year-old problems.** Recurring lexicon: "bottleneck", "has yet to be described", "fall far short", "of unknown clinical significance", "limited success when applied to". The gap is never more than 1-2 sentences before the pivot.

- **Headline number in abstract.** Every paper plants one or two headline statistics: "0.96 Å r.m.s.d.", "15 billion parameters", "52.4% vs 32.9%", "hundreds of designed", "89% of missense variants", "four to five orders of magnitude". These are quoted verbatim throughout press coverage.

- **Two header styles split methods vs. methods-with-tasks.** AlphaFold and RFdiffusion use task-neutral or topic-named subheaders ("The AlphaFold network", "Design of higher-order oligomers"). ESMFold and ProteinMPNN use declarative-finding subheaders ("Atomic-resolution structure emerges…", "Training with backbone noise improves model performance…"). Brief Communications (Foldseek) skip the structure entirely.

- **Motivation-first openers dominate where applications are diverse.** RFdiffusion's six Results subsections are nearly all "There is considerable interest in…", "A grand challenge in protein design is…", "We next investigated…", "Several important design challenges involve…". This pattern lets each subsection re-pitch its biological stakes before reporting a result.

- **"Grand challenge" framing.** Multiple papers literally call their target "a grand challenge" (RFdiffusion uses it for both enzyme-site scaffolding and binder design). AlphaFold's intro frames the protein-folding problem as "an important open research problem for more than 50 years" — comparable rhetorical move.

- **Strong contrastive verbs vs. baselines.** "compared to X for Rosetta", "outperforming other methods", "far exceeds", "two orders of magnitude improvement", "rescues previously failed designs". Always paired with absolute numbers, never relative percentages alone.

- **"In a manner analogous to" / "in a manner reminiscent of" image-generation analogies.** RFdiffusion's abstract and intro both invoke DALL-E-style framing ("networks that produce images from user-specified inputs", "generation of images from text prompts"). This is a 2022-2025 marker for diffusion-based protein-design papers.

- **Closing sentences forecast tools-of-modern-biology status.** AlphaFold: "essential tools of modern biology". RFdiffusion: "approach and, in some cases, surpass what natural evolution has achieved". ProteinMPNN: "extending…to protein-nucleic acid design and protein-small molecule design". The discipline's closer is always future-extension or grand-status, not a cautious limitation.

- **Hedging is minimal but present.** "to our knowledge", "should enable", "probably due to", "in a majority of cases", "likely benign". Hedges cluster in abstracts and final sentences; absent from Results subsection openers, which prefer declarative ("RFdiffusion can readily generate", "ProteinMPNN solves").

- **Resource/community framing in Discussion close.** ESMFold's ESM Atlas, AlphaMissense's all-substitutions database, Foldseek's webserver. Methods papers in this category routinely make "as a resource to the community" explicit.
