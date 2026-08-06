# 05 — Medical / Clinical AI: writing-pattern extracts

Category: clinical / medical AI — radiology, pathology, foundation models, federated benchmarking, multimodal clinical AI.
Six open-access papers, 2023-2024. Quotes are verbatim (≤25 words each).

---

## Paper 1: Ma et al., *Nature Communications* 2024 — MedSAM

- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC10803759/
- journal: Nature Communications
- year: 2024
- category: methods / foundation model

**A1_title:** "Segment anything in medical images" — short noun-phrase tool-name title (no colon, no claim).

**A2_abstract_map:**
- {n:1, role: BIG-PICTURE, quote: "Medical image segmentation is a critical component in clinical practice, facilitating accurate diagnosis, treatment planning, and disease monitoring."}
- {n:2, role: GAP, quote: "However, existing methods, often tailored to specific modalities or disease types, lack generalizability across the diverse spectrum of medical image segmentation tasks."}
- {n:3, role: HERE-WE, quote: "Here we present MedSAM, a foundation model designed for bridging this gap by enabling universal medical image segmentation."}
- {n:4, role: METHOD-INTRO, quote: "The model is developed on a large-scale medical image dataset with 1,570,263 image-mask pairs, covering 10 imaging modalities and over 30 cancer types."}
- {n:5, role: KEY-RESULT-1 / VALIDATION, quote: "We conduct a comprehensive evaluation on 86 internal validation tasks and 60 external validation tasks, demonstrating better accuracy and robustness than modality-wise specialist models."}
- {n:6, role: IMPLICATION, quote: "By delivering accurate and efficient segmentation across a wide spectrum of tasks, MedSAM holds significant potential to expedite the evolution of diagnostic tools…"}

**A3_here_we_pivot:** "Here we present MedSAM, a foundation model designed for bridging this gap by enabling universal medical image segmentation."

**A4_strongest_quant_in_abstract:** "1,570,263 image-mask pairs, covering 10 imaging modalities and over 30 cancer types" / "86 internal validation tasks and 60 external validation tasks".

**B1_intro_hook_style:** field-importance / definitional opening.
**B1_quote_sentence1:** "Segmentation is a fundamental task in medical imaging analysis, which involves identifying and delineating regions of interest (ROI) in various medical images, such as organs, lesions, and tissues."

**B3_gap_phrases:**
- "However, a significant limitation of many current medical image segmentation models is their task-specific nature."
- "This lack of generality poses a substantial obstacle to the wider application of these models in clinical practice."
- "the applicability of the segmentation foundation models (e.g., SAM) to medical image segmentation remains limited due to the significant differences between natural images and medical images."

**B4_pivot_first2sent:**
- "Considering these challenges, we argue that a more practical approach is to develop a promptable 2D segmentation model."
- "The model can be easily adapted to specific tasks based on user-provided prompts, offering enhanced flexibility and adaptability."

**B5_contributions:** narrated, not enumerated; embedded in pivot paragraph and last-intro preview.

**B6_last_intro_sentence:** "These results highlight the potential of MedSAM as a new paradigm for versatile medical image segmentation."

**C1_results_headers:**
- "MedSAM: a foundation model for promptable medical image segmentation"
- "Quantitative and qualitative analysis"
- "The effect of training dataset size"
- "MedSAM can improve the annotation efficiency"

**C2_header_style:** mixed — first header is tool-introduction (declarative noun phrase), second neutral task, third+fourth declarative findings.

**C3_section_openers:**
- {header: "MedSAM…", quote: "MedSAM aims to fulfill the role of a foundation model for universal medical image segmentation.", class: claim-first}
- {header: "Quantitative and qualitative analysis", quote: "[opening leads into Fig. 3c segmentation examples; result-first]", class: motivation/method-first}
- {header: "Effect of training dataset size", quote: "We also investigated the effect of varying dataset sizes on MedSAM's performance because the training dataset size has been proven to be pivotal in model performance.", class: motivation-first}

**C4_figure_callouts:**
- "(Fig. 1 and Supplementary Tables 1–4) This large-scale dataset allows MedSAM to learn a rich representation of medical images…"
- "Figure 3c visualizes some randomly selected segmentation examples where MedSAM obtained a median DSC score, including liver tumor in CT images, brain tumor in MR images…"

**C5_quant_with_stats:** "MedSAM obtained median DSC scores of 87.8% (IQR: 85.0-91.4%) on the nasopharynx cancer segmentation task, demonstrating 52.3%, 15.5%, and 22.7 improvements over SAM, the specialist U-Net, and DeepLabV3+, respectively."

**C6_baseline_comparison:** "Overall, SAM obtained the lowest performance on most segmentation tasks although it performed promisingly on some RGB image segmentation tasks, such as polyp (DSC: 91.3%, IQR: 81.2–95.1%) segmentation in endoscopy images."

**C7_robustness_phrase:** "We also investigated the effect of varying dataset sizes on MedSAM's performance because the training dataset size has been proven to be pivotal in model performance."

**C8_generalization_phrase:** "Although this task had never been seen during training, MedSAM still exhibited superior performance compared to the SAM."

**D1_discussion_open:** "We introduce MedSAM, a deep learning-powered foundation model designed for the segmentation of a wide array of anatomical structures and lesions across diverse medical imaging modalities." (restate-finding)

**D2_limitation:** "One such limitation is the modality imbalance in the training set, with CT, MRI, and endoscopy images dominating the dataset."

**D3_outlook:** "Since MedSAM has learned rich and representative medical image features…, it can be fine-tuned to effectively segment new tasks from less-represented modalities or intricate structures like vessels."

**D4_paper_closing_sentence:** "MedSAM, as the inaugural foundation model in medical image segmentation, holds great potential to accelerate the advancement of new diagnostic and therapeutic tools, and ultimately contribute to improved patient care."

**G1_hedges_used:** demonstrate, indicate, propose, suggest, consistent with.
**G2_strong_verbs:** enable, outperform, achieve, identify.
**G3_paragraph_connectives:** "However,"; "In contrast,".
**G4_taken_together:** Not present.

**notable:** Tool-name-only title (3 words). Pivot paragraph framed as a *design argument* ("we argue that a more practical approach…") rather than the typical "Here we present X" — unusual for a foundation-model paper.

---

## Paper 2: Chen et al., *Nature Medicine* 2024 — UNI

- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC11403354/
- journal: Nature Medicine
- year: 2024
- category: methods / foundation model

**A1_title:** "Towards a general-purpose foundation model for computational pathology" — hedged-aspirational ("Towards…") noun phrase, no colon.

**A2_abstract_map:**
- {n:1, role: BIG-PICTURE, quote: "Quantitative evaluation of tissue images is crucial for computational pathology (CPath) tasks, requiring the objective characterization of histopathological entities from whole-slide images (WSIs)."}
- {n:2, role: GAP, quote: "The high resolution of WSIs and the variability of morphological features present significant challenges, complicating the large-scale annotation of data for high-performance applications."}
- {n:3, role: GAP / PRIOR-WORK-LIMIT, quote: "…current efforts have proposed the use of pretrained image encoders…but have not been extensively developed and evaluated across diverse tissue types at scale."}
- {n:4, role: HERE-WE / METHOD-INTRO, quote: "We introduce UNI, a general-purpose self-supervised model for pathology, pretrained using more than 100 million images from over 100,000 diagnostic H&E-stained WSIs (>77 TB of data) across 20 major tissue types."}
- {n:5, role: VALIDATION, quote: "The model was evaluated on 34 representative CPath tasks of varying diagnostic difficulty."}
- {n:6, role: KEY-RESULT-2, quote: "In addition to outperforming previous state-of-the-art models, we demonstrate new modeling capabilities in CPath such as resolution-agnostic tissue classification…"}
- {n:7, role: IMPLICATION, quote: "UNI advances unsupervised representation learning at scale in CPath…enabling data-efficient artificial intelligence models that can generalize and transfer…"}

**A3_here_we_pivot:** "We introduce UNI, a general-purpose self-supervised model for pathology, pretrained using more than 100 million images from over 100,000 diagnostic H&E-stained WSIs (>77 TB of data) across 20 major tissue types."

**A4_strongest_quant_in_abstract:** ">100 million images from over 100,000 diagnostic H&E-stained WSIs (>77 TB of data)" / "34 representative CPath tasks" / "108 cancer types in the OncoTree classification system".

**B1_intro_hook_style:** field-importance opening grounded in clinical practice complexity.
**B1_quote_sentence1:** "The clinical practice of pathology involves performing a large range of tasks: from tumor detection and subtyping to grading and staging, and, given the thousands of possible diagnoses, a pathologist must be adept at solving an incredibly diverse group of problems, often simultaneously."

**B3_gap_phrases:**
- "However, current pretrained models for CPath remain constrained by the limited size and diversity of pretraining data"
- "remains constrained by the limited size and diversity of pretraining data, given that the TCGA comprises mostly primary cancer histology slides"
- "limited evaluation of generalization performance across diverse tissue types"

**B4_pivot_first2sent:**
- "In this work we build upon these prior efforts by introducing a general-purpose, self-supervised vision encoder for pathology, UNI, a large vision transformer (ViT-Large or ViT-L) pretrained on one of the largest histology slide collections…"
- "Mass-100K is a pretraining dataset that consists of more than 100 million tissue patches from 100,426 diagnostic H&E WSIs across 20 major tissue types collected from MGH and BWH, as well as the GTEx consortium…"

**B5_contributions:** narrated; "build upon these prior efforts by introducing…" rather than enumerated First/Second/Third.

**B6_last_intro_sentence:** "Following the conventional nomenclature of self-supervised models in computer vision, labels such as 'foundation model' may create misleading expectations." — unusually self-deflating closer.

**C1_results_headers:**
- "Pretraining Scaling Laws in CPath"
- "Weakly supervised slide classification"
- "Label efficiency of few-shot slide classification"
- "Supervised ROI classification in linear classifiers"
- "ROI retrieval"
- "Robustness to high image resolution"
- "ROI cell type segmentation"
- "Few-shot ROI classification with class prototypes"
- "Prompt-based slide classification using class prototypes"

**C2_header_style:** task/capability noun phrases (neutral) — no declarative findings.

**C3_section_openers:**
- {header: "Pretraining Scaling Laws…", quote: "A pivotal characteristic of foundation models lies in their capability to deliver improved downstream performance on various tasks when trained on larger datasets.", class: motivation-first}
- {header: "Weakly supervised slide classification", quote: "Furthermore, we investigate UNI's capabilities across a diverse range of 15 slide-level classification tasks…", class: method-first}
- {header: "Label efficiency…", quote: "We additionally evaluate UNI in few-shot MIL across all slide-level tasks.", class: method-first}
- {header: "Supervised ROI classification…", quote: "In addition to slide-level tasks, we also assess UNI on a diverse range of 11 ROI-level tasks…", class: method-first}

**C4_figure_callouts:**
- "On OT-43 and OT-108, we observe a +4.2% performance increase (P < 0.001, two-sided paired permutation test) in top-1 accuracy when scaling UNI…"
- "Figure 2e and Extended Data Figs. 5 and 6 show how UNI highlights finer-grained visual features when evaluating high-resolution images."

**C5_quant_with_stats:** "On OT-43, UNI achieves a top-5 accuracy of 93.8% and an AUROC of 0.976, outperforming the next best-performing model (REMEDIS) by +6.3% and +0.022 on these respective metrics (both P < 0.001)."

**C6_baseline_comparison:** "Across all 15 slide-level tasks, UNI consistently outperforms other pretrained encoders (average performance increases of +26.4% over ResNet-50, +8.3% over CTransPath, and +10.0% over REMEDIS)…"

**C7_robustness_phrase:** "To assess scaling trends, we also pretrain UNI across varying data scales, with Mass-100K subsetted to create Mass-22K (16 million images, 21,444 WSIs) and Mass-1K (1 million images, 1,404 WSIs)."

**C8_generalization_phrase:** "On comparison of existing leaderboards, we find that ABMIL with UNI features outperforms many sophisticated MIL architectures."

**D1_discussion_open:** "In this study, we demonstrate the versatility of UNI, a general-purpose, self-supervised model pretrained on one of the largest histology slide collections (for self-supervised learning) to date in CPath." (restate-finding)

**D2_limitation:** "Our study also does not evaluate the best-performing ViT-Giant architecture in DINOv2, an even larger model that would likely translate well in CPath but demands more computational resources for pretraining."

**D3_outlook:** "Future work will focus on using UNI as the building block for slide-level self-supervised models and general slide-level pathology AI development in anatomic pathology."

**D4_paper_closing_sentence:** Closer block: "Altogether, our findings highlight the strength of having a better-pretrained encoder versus developing task-specific models that target narrow clinical problems, which we hope would shift research directions in CPath toward the development of generalist AI models…" (Visible final synthesis sentence; full paper closing truncated in retrieval.)

**G1_hedges_used:** demonstrate, indicate, suggest, consistent with, establish, propose.
**G2_strong_verbs:** outperform, enable, achieve, identify, advance, generalize.
**G3_paragraph_connectives:** "Overall, we find that UNI is able to classify rare cancers…"; "Altogether, our findings highlight the strength of…".
**G4_taken_together:** Uses "Altogether," and "Overall," in equivalent function — not the canonical "Taken together".

**notable:** Hedged "Towards…" title, scaling-laws-first Results structure (mirroring NLP foundation-model papers), and a self-cautioning last-intro sentence about the term "foundation model".

---

## Paper 3: Lu et al., *Nature Medicine* 2024 — CONCH

- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC11384335/
- journal: Nature Medicine
- year: 2024
- category: methods / vision-language foundation model

**A1_title:** "A visual-language foundation model for computational pathology" — neutral noun-phrase title with indefinite article.

**A2_abstract_map:**
- {n:1, role: BIG-PICTURE, quote: "The accelerated adoption of digital pathology and advances in deep learning have enabled development of robust models for various pathology tasks."}
- {n:2, role: GAP, quote: "However, model training is often difficult due to label scarcity in the medical domain, and a model's usage is limited by specific task and disease."}
- {n:3, role: GAP-2, quote: "Additionally, most models in histopathology leverage only image data, a stark contrast to how humans teach and reason about histopathologic entities."}
- {n:4, role: HERE-WE, quote: "We introduce CONtrastive learning from Captions for Histopathology (CONCH), a visual-language foundation model developed using diverse sources of histopathology images and biomedical text."}
- {n:5, role: VALIDATION, quote: "Evaluated on a suite of 14 diverse benchmarks, CONCH transfers to wide range of downstream tasks involving histopathology images and/or text."}
- {n:6, role: KEY-RESULT-1, quote: "CONCH achieves state-of-the-art performance on histology image classification, segmentation, captioning, and text-to-image and image-to-text retrieval."}
- {n:7, role: IMPLICATION, quote: "CONCH represents substantial leap over concurrent visual-language pretrained systems for histopathology, with potential to facilitate machine learning-based workflows."}

**A3_here_we_pivot:** "We introduce CONtrastive learning from Captions for Histopathology (CONCH), a visual-language foundation model developed using diverse sources of histopathology images and biomedical text."

**A4_strongest_quant_in_abstract:** "Evaluated on a suite of 14 diverse benchmarks" / "state-of-the-art performance on histology image classification, segmentation, captioning, and…retrieval".

**B1_intro_hook_style:** field-importance grounded in clinical gold-standard claim.
**B1_quote_sentence1:** "The gold standard for diagnosis of many diseases remains examination of tissue by a pathologist."

**B3_gap_phrases:**
- "However, the process of data collection and annotation of whole-slide images (WSIs) is labor intensive and is not scalable."
- "with thousands of possible diagnoses, training separate models for every step is untenable."
- "the number of studies integrating vision and language data for representation learning in computational pathology is small."

**B4_pivot_first2sent:**
- "Given the diversity of tasks, the difficulty in acquiring large datasets of rare diseases, and the central nature of language to practice of pathology, there is a need for high-performing visual-language foundation models."
- "We introduce CONtrastive learning from Captions for Histopathology (CONCH), a visual-language foundation model developed using diverse sources."

**B5_contributions:** narrated; need-statement followed by single "We introduce…" sentence.

**B6_last_intro_sentence:** "We demonstrate that our model achieves state-of-the-art performance across all benchmarks relative to other visual-language foundation models."

**C1_results_headers:**
- "Zero-shot classification of diverse tissues and diseases"
- "Few-shot classification with task-specific supervised learning"
- "Application to classification of rare diseases"
- "Zero-shot cross-modal retrieval"
- "Zero-shot segmentation"

**C2_header_style:** capability-style noun phrases ("Zero-shot X", "Few-shot Y") — neutral task headers, not declarative findings.

**C3_section_openers:**
- {header: "Zero-shot classification…", quote: "Contrastively aligned visual-language pretraining allows the model to be directly applied.", class: method-first}
- {header: "Few-shot classification…", quote: "The zero-shot recognition capability of contrastive pretrained visual-language models enables efficient application.", class: motivation-first}
- {header: "Application to…rare diseases", quote: "While previous investigations have focused on evaluating zero-shot and few-shot performance on relatively narrow tasks.", class: motivation-first / gap-first}
- {header: "Zero-shot cross-modal retrieval", quote: "By learning an aligned latent space for visual and language embeddings, our model is capable.", class: method-first}

**C4_figure_callouts:**
- "In an example of a breast IDC slide, we found regions highlighted in heatmap closely resembled tumor regions delineated by pathologist annotation."
- "For each nc, we sampled five different sets of training examples and trained weakly supervised ABMIL model."

**C5_quant_with_stats:** "For NSCLC subtyping and RCC subtyping, CONCH achieved zero-shot accuracy of 90.7% and 90.2%, outperforming PLIP by 12.0% and 9.8% (P < 0.01)."

**C6_baseline_comparison:** "CONCH achieved balanced accuracy score of 37.1% on 30-class subtyping problem, surpassing BiomedCLIP (+17.0%, P < 0.01)."

**C7_robustness_phrase:** "We additionally performed ablation experiments to investigate effect of data filtering, different pretraining algorithms and unimodal pretraining."

**C8_generalization_phrase:** "These results demonstrate potential utility of strong pretrained visual-language model as effective image-only encoder for weakly supervised learning."

**D1_discussion_open:** "Most previous tools in computational pathology have attempted to extract meaningful patterns from image data and/or structured patient data." (frame-in-field)

**D2_limitation:** "A key limitation of our study is scale of data pretraining, which still pales in comparison to billion-scale datasets used in general machine learning."

**D3_outlook:** "We leave its implementation and evaluation to future studies, as fine-grained visual concepts at cellular or subcellular level remain outside scope."

**D4_paper_closing_sentence:** "These observations suggest we still potentially have long way to go before achieving goal of building foundation model capable of truly universal zero-shot recognition."

**G1_hedges_used:** suggest, indicate, demonstrate, propose, consistent with.
**G2_strong_verbs:** enable, outperform, achieve, identify, facilitates, accelerated.
**G3_paragraph_connectives:** "However,"; "Additionally,"; "Given,"; "While".
**G4_taken_together:** Not present in canonical form; uses "These findings demonstrate…" / "These observations suggest…".

**notable:** Closing sentence is *unusually humble* for a SOTA paper ("we still potentially have long way to go"); rare-disease section explicitly motivated by gap-against-prior-work ("While previous investigations have focused on…narrow tasks").

---

## Paper 4: Vorontsov et al., *Nature Medicine* 2024 — Virchow

- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC11485232/
- journal: Nature Medicine
- year: 2024
- category: methods / foundation model + clinical-grade evaluation

**A1_title:** "A foundation model for clinical-grade computational pathology and rare cancers detection" — capability-claim noun phrase ("for X and Y").

**A2_abstract_map:**
- {n:1, role: BIG-PICTURE, quote: "The analysis of histopathology images with artificial intelligence aims to enable clinical decision support systems and precision medicine."}
- {n:2, role: GAP / METHOD-MOTIVATION, quote: "The success of such applications depends on the ability to model the diverse patterns observed in pathology images."}
- {n:3, role: HERE-WE, quote: "To this end, we present Virchow, the largest foundation model for computational pathology to date."}
- {n:4, role: KEY-RESULT-1, quote: "…we demonstrate that a large foundation model enables pan-cancer detection, achieving 0.95 specimen-level area under the (receiver operating characteristic) curve across nine common and seven rare cancers."}
- {n:5, role: KEY-RESULT-2 / DATA-EFFICIENCY, quote: "Furthermore, we show that with less training data, the pan-cancer detector built on Virchow can achieve similar performance to tissue-specific clinical-grade models in production…"}
- {n:6, role: IMPLICATION, quote: "Virchow's performance gains highlight the value of a foundation model and open possibilities for many high-impact applications with limited amounts of labeled training data."}

**A3_here_we_pivot:** "To this end, we present Virchow, the largest foundation model for computational pathology to date."

**A4_strongest_quant_in_abstract:** "achieving 0.95 specimen-level area under the (receiver operating characteristic) curve across nine common and seven rare cancers."

**B1_intro_hook_style:** clinical-importance assertion (one-line).
**B1_quote_sentence1:** "Pathologic analysis of tissue is essential for the diagnosis and treatment of cancer."

**B3_gap_phrases:**
- "However, given the incredible gains in performance of computer vision…"
- "more recent studies attempt to unlock new insights…and reveal undiscovered outcomes such as prognosis and therapeutic response."
- "This offers a distinct advantage over current diagnostic-specific methods…which, limited to a subset of pathology images, are less likely to reflect…"

**B4_pivot_first2sent:**
- "Here, we present a million-image-scale pathology foundation model, Virchow, named in honor of Rudolf Virchow…"
- "Virchow is trained on data from approximately 100,000 patients corresponding to approximately 1.5 million H&E stained WSIs…"

**B5_contributions:** narrated; the historical-figure naming choice is integrated into the pivot.

**B6_last_intro_sentence:** "If trained with a sufficiently large quantity of digitized WSIs in the pathology domain, such a model could form the basis for clinically robust prediction of both common and rare cancers…"

**C1_results_headers:**
- "Virchow enables pan-cancer detection"
- "Toward clinical-grade performance"
- "Biomarker detection in routine imaging obviates additional testing"
- "Tile-level benchmarks and qualitative analysis demonstrate generalizability"

**C2_header_style:** declarative-finding headers ("X enables Y", "X obviates Y", "X demonstrate Y") — strong claim-style.

**C3_section_openers:**
- {header: "Virchow enables pan-cancer detection", quote: "A key aim of our work was to develop a single model to detect cancer, including rare cancers…", class: motivation-first}
- {header: "Toward clinical-grade performance", quote: "A promise of foundation models is improved generalization; however, this claim is difficult to verify…", class: motivation-first / gap-first}
- {header: "Biomarker detection…obviates additional testing", quote: "The prediction of biomarkers from standard H&E stained images can reduce the reliance on testing using additional methods…", class: claim-first/motivation}
- {header: "Tile-level benchmarks…generalizability", quote: "To directly evaluate tile-level embeddings without the confounder of training an aggregator network…", class: method-first}

**C4_figure_callouts:**
- "Virchow embeddings yielded the best cancer detection performance on all cancer types (Fig. 2a)."
- "The Virchow-based pan-cancer detection model, trained on cancers across numerous tissues, performs nearly as well as the prostate, breast and BLN clinical specialist models (Fig. 3c)…"

**C5_quant_with_stats:** "Overall the pan-cancer model achieved an AUC of 0.950 with Virchow embeddings, 0.940 with UNI, 0.932 with Phikon and 0.907 with CTransPath (Fig. 2b); all significantly different with P < 0.0001)."

**C6_baseline_comparison:** "Virchow embeddings outperform or match all baseline models on all tested cancer types, notably including rare cancers and out-of-distribution (OOD) data."

**C7_robustness_phrase:** "To provide evidence for potential focus areas for future advances in computational pathology, qualitative analysis is also performed, characterizing the error patterns…"

**C8_generalization_phrase:** "Although AUC cannot be exactly compared across data subsets, we can observe that all models achieve a similar AUC on both internal and external data, suggesting that they generalize well…"

**D1_discussion_open:** "The value of a pathology foundation model is twofold: generalizability and training data efficiency." (claim-first / thesis-restate)

**D2_limitation:** "The training dataset is acquired from one center with limited scanner types."

**D3_outlook:** "It remains an open question at what point the model and data scale are saturated."

**D4_paper_closing_sentence:** "In this work, we have demonstrated that this approach can form the foundation for clinical-grade models in cancer pathology."

**G1_hedges_used:** demonstrate, suggest, indicate, consistent with, propose, establish.
**G2_strong_verbs:** enable, outperform, achieve, identify.
**G3_paragraph_connectives:** "Furthermore, we show that…"; "Overall, our investigation into scaling behavior suggests…".
**G4_taken_together:** Not canonical; "Overall, our results provide evidence that…" plays this role.

**notable:** Distinctive use of declarative-finding Results headers (atypical in pathology — closer to Nature original-research style); "Toward clinical-grade…" header signals an explicit aspirational frame mid-paper.

---

## Paper 5: Karargyris et al., *Nature Machine Intelligence* 2023 — MedPerf

- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC11068064/
- journal: Nature Machine Intelligence
- year: 2023
- category: methods / federated benchmarking infrastructure (Perspective-style)

**A1_title:** "Federated benchmarking of medical artificial intelligence with MedPerf" — task + tool ("X with Y") title.

**A2_abstract_map:**
- {n:1, role: BIG-PICTURE, quote: "Medical artificial intelligence (AI) has tremendous potential to advance healthcare by supporting and contributing to the evidence-based practice of medicine, personalizing patient treatment, reducing costs…"}
- {n:2, role: GAP / NEED, quote: "Unlocking this potential requires systematic, quantitative evaluation of the performance of medical AI models on large-scale, heterogeneous data capturing diverse patient populations."}
- {n:3, role: HERE-WE, quote: "Here, to meet this need, we introduce MedPerf, an open platform for benchmarking AI models in the medical domain."}
- {n:4, role: METHOD-INTRO, quote: "MedPerf focuses on enabling federated evaluation of AI models, by securely distributing them to different facilities, such as healthcare organizations."}
- {n:5, role: METHOD-PROPERTY, quote: "This process of bringing the model to the data empowers each facility to assess and verify the performance of AI models in an efficient and human-supervised process, while prioritizing privacy."}
- {n:6, role: SCOPE-OVERVIEW, quote: "We describe…the design philosophy of MedPerf, its current implementation status and real-world deployment, our roadmap and…the use of MedPerf with multiple international institutions…"}
- {n:7, role: CALL-TO-ACTION, quote: "Finally, we welcome new contributions by researchers and organizations to further strengthen MedPerf as an open benchmarking platform."}

**A3_here_we_pivot:** "Here, to meet this need, we introduce MedPerf, an open platform for benchmarking AI models in the medical domain."

**A4_strongest_quant_in_abstract:** Strongest quant lives in body, not abstract: "benchmarking 41 models in 32 sites across six continents" (FeTS challenge).

**B1_intro_hook_style:** policy / regulatory recap (recent-developments lead-in).
**B1_quote_sentence1:** "As medical artificial intelligence (AI) has begun to transition from research to clinical care, national agencies around the world have started drafting regulatory frameworks to support and account for a new class of interventions based on AI models."

**B3_gap_phrases:**
- "Despite the clear need for access to larger and more diverse datasets, data owners are constrained by substantial regulatory, legal and public perception risks"
- "Sharing data also requires up-front investment"
- "Even if a data owner (such as a hospital) is willing to pay these costs and accept these risks, benefits can be uncertain"

**B4_pivot_first2sent:**
- "Here we introduce MedPerf, a platform focused on overcoming these obstacles to broader data access for AI model evaluation."
- "MedPerf is an open benchmarking platform that combines: (1) a lower-risk approach to testing models on diverse data, without directly sharing the data; with (2) the appropriate infrastructure, technical support and organizational coordination…"

**B5_contributions:** enumerated inside the pivot — uses "(1)…(2)…" style for the platform's two pillars.

**B6_last_intro_sentence:** "This approach aims to catalyse wider adoption of medical AI, leading to more efficacious, reproducible and cost-effective clinical practice, with ultimately improved patient outcomes."

**C1_results_headers:**
- "Evaluation on global federated datasets"
- "MedPerf roadmap"
- "Related work"

**C2_header_style:** noun-phrase neutral headers; one infrastructural ("roadmap").

**C3_section_openers:**
- {header: "Evaluation on global federated datasets", quote: "Here we introduce MedPerf, a platform focused on overcoming these obstacles to broader data access for AI model evaluation.", class: claim-first / restate}

**C4_figure_callouts:**
- "Machine learning models are distributed to data owners for local evaluation on their premises without the need or requirement to extract their data to a central location." (Fig. 1)
- "For the MICCAI FeTS 2022 challenge, our MedPerf platform facilitated the distribution, execution and collection of model results from 32 hospitals across Africa, North America, South America, Asia, Australia and Europe." (Fig. 2)

**C5_quant_with_stats:** "In the FeTS challenge—the first federated learning challenge ever conducted—MedPerf successfully demonstrated its scalability and user-friendliness when benchmarking 41 models in 32 sites across six continents."

**C6_baseline_comparison:** "Furthermore, MedPerf was validated through a series of pilot studies with academic groups involved in multi-institutional collaborations…"

**C7_robustness_phrase:** "We also collected feedback from FeTS and the pilots' participating teams regarding their experience with MedPerf."

**C8_generalization_phrase:** "Although the initial uses of MedPerf were in radiology and surgery, MedPerf can easily be used in other biomedical tasks such as computational pathology, genomics, NLP, or…structured data from the patient medical record."

**D1_discussion_open:** "MedPerf is a benchmarking platform designed to quantitatively evaluate AI models 'in the wild,' considering unseen data from out-of-sample distinct sources, and thereby helping address inequities, bias and fairness in AI models." (definition-restate)

**D2_limitation:** "However, we cannot achieve these benefits without the help of the technical and medical community."

**D3_outlook:** "We believe open, inclusive efforts such as MedPerf can drive innovation and bridge the gap between AI research and real-world clinical impact."

**D4_paper_closing_sentence:** "With MedPerf, we aspire to bring such a community of stakeholders together as a critical step toward realizing the grand potential of medical AI, and we invite participation at ref. [26]."

**G1_hedges_used:** aims to, can, potentially, demonstrate.
**G2_strong_verbs:** enable, empower, facilitate, demonstrate, outperform, achieve, identify.
**G3_paragraph_connectives:** "Furthermore,"; "Finally,"; "Moreover,"; "Notably".
**G4_taken_together:** "Collectively, all studies were intentionally designed to include a diverse set of clinical areas and data modalities to test MedPerf's infrastructure adaptability."

**notable:** Hybrid Perspective/methods piece: closes with explicit *call-to-action* ("we invite participation at ref. [26]"), enumerates contributions inside the pivot using "(1)…(2)…", and the paragraph connective "Collectively," is used canonically.

---

## Paper 6: Ferber et al., *Nature Communications* 2024 — GPT-4V in-context pathology (applied/clinical-validation)

- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC11582649/
- journal: Nature Communications
- year: 2024
- category: applied / clinical-validation of generalist VLM

**A1_title:** "In-context learning enables multimodal large language models to classify cancer pathology images" — declarative-finding ("X enables Y to do Z") sentence-style title.

**A2_abstract_map:**
- {n:1, role: BIG-PICTURE / STATUS-QUO, quote: "Medical image classification requires labeled, task-specific datasets which are used to train deep learning networks de novo, or to fine-tune foundation models."}
- {n:2, role: GAP, quote: "However, this process is computationally and technically demanding."}
- {n:3, role: BACKGROUND-CONTRAST, quote: "In language processing, in-context learning provides an alternative, where models learn from within prompts, bypassing the need for parameter updates."}
- {n:4, role: GAP-2, quote: "Yet, in-context learning remains underexplored in medical image analysis."}
- {n:5, role: HERE-WE, quote: "Here, we systematically evaluate the model Generative Pretrained Transformer 4 with Vision capabilities (GPT-4V) on cancer image processing with in-context learning on three cancer histopathology tasks…"}
- {n:6, role: KEY-RESULT-1, quote: "Our results show that in-context learning is sufficient to match or even outperform specialized neural networks trained for particular tasks, while only requiring a minimal number of samples."}
- {n:7, role: SYNTHESIS, quote: "In summary, this study demonstrates that large vision language models trained on non-domain specific data can be applied out-of-the box to solve medical image-processing tasks in histopathology."}
- {n:8, role: IMPLICATION, quote: "This democratizes access of generalist AI models to medical experts without technical background especially for areas where annotated data is scarce."}

**A3_here_we_pivot:** "Here, we systematically evaluate the model Generative Pretrained Transformer 4 with Vision capabilities (GPT-4V) on cancer image processing with in-context learning on three cancer histopathology tasks of high importance: Classification of tissue subtypes in colorectal cancer, colon polyp subtyping and breast tumor detection in lymph node sections."

**A4_strongest_quant_in_abstract:** Abstract is qualitative; strongest quant in body: "classification accuracy of 83.3% for MHIST (CI: 0.733–0.917) and 88.3% for PatchCamelyon (CI: 0.8–0.95)."

**B1_intro_hook_style:** sweeping field claim (one-liner).
**B1_quote_sentence1:** "Artificial intelligence (AI) is about to transform healthcare."

**B3_gap_phrases:**
- "However, these foundation models need a substantial volume of domain-specific images during training and are restricted to vision applications only."
- "Yet, in-context learning remains underexplored in medical image analysis."
- "A major shortcoming is the restriction to text-based tasks."

**B4_pivot_first2sent:**
- "Building on the trend of large vision language foundation models, we hypothesize that the principles applied for in-context learning of text-based models can be equally effective when extended to multimodal scenarios, such as medical imaging."
- "In the non-medical setting, robust evidence for in-context learning with images has already been established."

**B5_contributions:** narrated as a hypothesis-test, not enumerated.

**B6_last_intro_sentence:** "This advancement casts doubt on the necessity of developing task-specific deep learning models in the future and democratizes access to generalist AI models to accelerate medical research."

**C1_results_headers:**
- "In-context learning with medical images improves classification accuracy for histopathology"
- "Vision-language models can achieve performance on par with retrained vision classifiers"
- "In-context learning reduces the performance gap between generalist and histopathology foundation models"
- "Image in-context learning improves text-based reasoning"

**C2_header_style:** declarative-finding sentence-style headers ("X improves Y", "X can achieve Y on par with Z", "X reduces gap…").

**C3_section_openers:**
- {header: "In-context learning…improves classification accuracy", quote: "In this study, we hypothesize that few-shot prompting can improve the performance of foundation vision models.", class: motivation/hypothesis-first}
- {header: "Vision-language models can achieve…on par with retrained classifiers", quote: "Next, we compare few-shot sampling with the previous status-quo in image classification.", class: method-first}
- {header: "In-context learning reduces the performance gap…", quote: "In a subsequent evaluation, we tested GPT-4V on the CRC100K dataset.", class: method-first}
- {header: "Image in-context learning improves text-based reasoning", quote: "Vision-Language Models enable multimodal understanding.", class: claim-first}

**C4_figure_callouts:**
- "As shown in Fig. 2A, GPT-4V only marginally surpasses the expectation of random guessing when used in a zero-shot setting, attaining an accuracy of 61.7% (CI: 0.5–0.733)."
- "In-context learning changes this situation: We see a consistent improvement in classification accuracy with increasing numbers of few-shot samples."

**C5_quant_with_stats:** "The ten-shot in-context learning GPT-4V approach not only matches but exceeds the performance of all other models (Fig. 3A), leading to a classification accuracy of 83.3% for MHIST (CI: 0.733–0.917) and 88.3% for PatchCamelyon (CI: 0.8–0.95)."

**C6_baseline_comparison:** "Initially, the performance deficit of GPT-4V in zero-shot classification relative to kNN stood at 61.7% and 62.5% for Phikon and UNI respectively."

**C7_robustness_phrase:** "From a zero-shot baseline that again barely achieves a better classification than random guessing…we see that in both datasets, random image sampling can improve classification accuracy."

**C8_generalization_phrase:** "In summary, our findings underline the potential of few-shot image learning in GPT-4V, even in a multilabel classification setting."

**D1_discussion_open:** "Foundation models have demonstrated substantial promise in medical image processing." (frame-in-field)

**D2_limitation:** "Some limitations of our work are that experiments were restricted to a yet small sample size due to the preview status of the GPT-4V API, which currently only permits a limited number of requests."

**D3_outlook:** "Following the current paradigm of AI scaling laws, it can be estimated that we have not yet reached a plateau in the performance benefits from even more powerful foundation models in the future."

**D4_paper_closing_sentence:** "Nevertheless, we believe that in-context learning with images holds great potential for improving the performance of vision language models on biomedical image classification tasks and beyond."

**G1_hedges_used:** demonstrate, indicate, suggest, consistent with, establish.
**G2_strong_verbs:** enable, outperform, achieve, democratizes.
**G3_paragraph_connectives:** "However,"; "Yet,".
**G4_taken_together:** "Collectively, these findings suggest that employing few-shot learning techniques can enhance the model's capacity to analyze and interpret test images more accurately."

**notable:** Sentence-style declarative Results headers (very Nature-flagship in tone). The intro hook is the shortest in the set ("Artificial intelligence (AI) is about to transform healthcare."). Two-step gap structure: status-quo gap ("computationally and technically demanding") + opportunity gap ("Yet…remains underexplored").

---

## Cross-paper observations

- **Title formula split.** Foundation-model papers cluster on hedged/aspirational noun phrases ("Towards a general-purpose…", "A foundation model for X", "A visual-language foundation model for Y"). The applied/clinical-validation paper (Ferber) uses a sentence-style declarative title ("X enables Y to do Z"). MedSAM is the outlier with a 3-word tool-name-only title.
- **Abstract pivot is uniformly "Here we" / "We introduce" / "We present".** All six pivot via a single sentence; none uses a multi-sentence ramp. The pivot sentence almost always names the tool in caps or italics, then immediately states the dataset scale or task count ("100 million images", "1.5 million WSIs", "14 diverse benchmarks", "86 internal + 60 external tasks", "32 sites across six continents", "three cancer histopathology tasks").
- **Gap signaling is dense and patterned.** "However," "Yet," "remains limited/underexplored," and "lack of generality" are the four reusable templates. Multiple papers stack two gaps (a status-quo limitation + an unsolved opportunity).
- **Quantitative + statistics style.** Standard form: "achieves AUC X.XXX, outperforming baseline by ΔX.X% (P < 0.001, two-sided test)" — UNI and Virchow are the strictest about pairing every comparison with a P-value; CONCH and Ferber use confidence intervals; MedSAM uses IQR.
- **Results headers split into three styles.** (a) Capability/task noun phrases ("Zero-shot classification…", "Weakly supervised slide classification") — UNI, CONCH. (b) Declarative findings ("X enables Y", "X improves Y") — Virchow, Ferber. (c) Tool-introduction ("MedSAM: a foundation model…") — MedSAM. Top journals tolerate either style as long as the section opener restates the claim.
- **Section openers favor motivation-first / hypothesis-first** over claim-first in pathology foundation-model papers (UNI, CONCH, Ferber repeatedly open with "A pivotal characteristic of…", "While previous investigations have focused on…", "In this study, we hypothesize that…"). Virchow is the exception, opening some sections with explicit goal statements.
- **Discussion opening template.** Either (i) restate the central finding ("We introduce X, …" / "In this study, we demonstrate the versatility of X…") or (ii) frame in field ("The gold standard for…", "Foundation models have demonstrated substantial promise…"). All six avoid limitation-first openings.
- **Limitations are explicit but compact** — typically one sentence naming a concrete dataset/scale/scanner constraint ("modality imbalance", "one center with limited scanner types", "small sample size due to preview API", "scale of data pretraining…pales in comparison to billion-scale datasets").
- **Closing sentences are aspirational.** All six end on patient-care / democratization / community framing rather than on a technical claim. MedSAM and Virchow close with "clinical-grade" / "improved patient care"; MedPerf closes with a direct call to participate; CONCH uniquely closes with humility ("we still potentially have long way to go").
- **Connective vocabulary.** "Furthermore," "Overall," "Altogether," and "Collectively," are the dominant Nature-family paragraph connectives in this set; the canonical "Taken together" appears rarely — "Collectively," (MedPerf, Ferber) and "Altogether," (UNI) are the live substitutes. Hedges concentrate on "demonstrate / suggest / indicate / consistent with"; strong verbs concentrate on "enable / outperform / achieve / advance / democratize".
- **Foundation-model papers report scaling experiments as a dedicated Results section** (UNI: "Pretraining Scaling Laws in CPath"; Virchow: scale framed in Discussion outlook; MedSAM: "The effect of training dataset size") — this has become an expected component of NMI/Nature Medicine foundation-model writing rather than an optional ablation.
