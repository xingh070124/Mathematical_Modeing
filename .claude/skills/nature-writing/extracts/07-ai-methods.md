# Category 07 — Pure AI methodology papers (2024–2026), Nature-family

Eight open-access papers in which **AI itself is the contribution** (not AI applied to a science domain). Coverage spans 7 sub-areas: LLM-agent planning architecture (Webb), scaling-law / capacity-density methodology (Xiao), novel non-optimization training algorithm (Whitelam), RL-for-reasoning emergence (DeepSeek-R1), meta-learned RL algorithm discovery (Oh / DiscoRL), hallucination detection methodology (Farquhar / semantic entropy), human-aligned visual representation distillation (Muttenthaler / AligNet), and AI-evaluation methodology (Zhou / ADeLe). Three Nature-family journals represented (Nature, Nature Machine Intelligence, Nature Communications).

This file complements `06-ml.md` (ChemCrow, AlphaGeometry, MolE, SemanticLens, Cancer-Imaging-FM, FunSearch) — none repeated.

---

## Paper 1: Webb, T. W., Mondal, S. S., Jang, C., Chang, K., Frankland, S. M., Lake, B. M., Cohen, J. D. & Russin, J. "A brain-inspired agentic architecture to improve planning with LLMs." Nature Communications 16, 8804 (2025).
- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC12485071/ ; https://www.nature.com/articles/s41467-025-63804-5
- journal: Nature Communications
- year: 2025
- category: method (LLM agent / planning / cognitive-neuro-inspired architecture)

A1_title: "A brain-inspired agentic architecture to improve planning with LLMs"
A2_abstract_map:
  - S1 (BIG-PICTURE / GAP) — "Large language models (LLMs) demonstrate impressive performance on a wide variety of tasks, but they often struggle with tasks that require multi-step reasoning or goal-directed planning."
  - S2 (motivation / cross-domain analogy) — "To address this, we take inspiration from the human brain, in which planning is accomplished via component processes that are predominantly associated with specific brain regions."
  - S3 (mechanism preview) — "These processes include conflict monitoring, state prediction, state evaluation, task decomposition, and task coordination."
  - S4 (capability gap) — "We find that LLMs are often capable of carrying out these functions in isolation, but struggle to autonomously coordinate them in the service of a goal."
  - S5 (HERE-WE / propose) — "Therefore, we propose a modular agentic architecture - the Modular Agentic Planner (MAP) - in which planning is performed via the interaction of specialized brain-inspired LLM modules."
  - S6 (VALIDATION) — "We evaluate MAP on three challenging planning tasks – graph traversal, Tower of Hanoi, and the PlanBench benchmark – as well as an NLP task requiring multi-step reasoning (strategyQA)."
  - S7 (KEY-RESULT-1, KEY-RESULT-2) — "We find that MAP yields significant improvements over both standard LLM methods and competitive agentic baselines, can be effectively combined with smaller and more cost-efficient LLMs, and displays superior transfer across tasks."
  - S8 (IMPLICATION) — "These results demonstrate the benefit of utilizing knowledge from cognitive neuroscience to improve planning in LLMs."
A3_here_we_pivot: "Therefore, we propose a modular agentic architecture - the Modular Agentic Planner (MAP) - in which planning is performed via the interaction of specialized brain-inspired LLM modules."
A4_strongest_quant_in_abstract: not numerical — abstract uses "significant improvements", "superior transfer"; numbers (Llama3-70b vs GPT-4) deferred to body.

B1_intro_hook_style: capability-gap framing of LLMs (recent-advance recap with negative twist).
B1_quote_sentence1: "Large Language Models (LLMs) have become widely accepted as highly capable generalist systems with a surprising range of emergent capacities."
B3_gap_phrases:
  - "A particularly notable shortcoming is their poor ability to plan or perform faithful multi-step reasoning."
  - "This work raises the question of how LLMs can be improved so as to enable a capacity for planning."
  - implicit: LLMs cannot autonomously coordinate planning sub-functions
B4_pivot_first2sent: "With this goal in mind, we propose the Modular Agentic Planner (MAP), an agentic architecture composed of modules that are specialized to perform specific PFC-inspired functions within the planning process."
B5_contributions: (1) PFC-decomposition recipe (conflict / state-prediction / evaluation / decomposition / coordination); (2) MAP modules implemented as prompted LLM specialists; (3) tree-search built from the proposal+predict+evaluate triad; (4) gains on ToH / CogEval / PlanBench / StrategyQA; (5) cross-task transfer; (6) module-ablation evidence.
B6_last_intro_sentence: "Taken together, these results indicate the potential of a brain-inspired approach to improve the reasoning and planning capabilities of LLMs."

C1_results_headers: ["Problem solving: Tower of Hanoi", "Navigation: CogEval", "Planning: PlanBench", "Real-world reasoning: StrategyQA", "Transfer experiments"]
C2_header_style: **task-domain colon scheme** — pairs an abstract capability label with a concrete task name ("Problem solving: Tower of Hanoi"). Capability-anchored, benchmark-named.
C3_section_openers:
  - {header: "Tower of Hanoi", quote: "Figure 2B shows the results for the ToH task.", class: figure-first}
  - {header: "CogEval", quote: "Figure 3B shows the results for the graph traversal tasks from the CogEval benchmark.", class: figure-first}
  - {header: "PlanBench", quote: "Table 3 shows the results for the PlanBench dataset, where MAP outperformed all of the baselines that we considered.", class: claim-first via figure}
  - {header: "Transfer experiments", quote: "Finally, we performed transfer experiments to study whether few-shot in-context learning would support generalization to different planning tasks.", class: motivation-first}
C4_figure_callouts:
  - "Figure 1 depicts the MAP architecture."
  - "The agent receives states from the environment and high-level goals. These are processed by a set of specialized LLM modules."
C5_quant_with_stats: "In experiments on 3-disk ToH problems, we found that MAP still outperformed other baselines that employed the same Llama3-70b language model, and even outperformed the best GPT-4 baseline, GPT-4 ICL (Table 2), suggesting that smaller LLMs may enable a more cost-efficient version of the proposed approach."
C6_baseline_comparison: "outperformed both the GPT-4 CoT and ToT baselines"
C7_robustness_phrase: "Ablating the tree search and TaskDecomposer module also resulted in significantly fewer solved problems"
C8_generalization_phrase: "displays superior transfer across tasks"; "few-shot in-context learning would support generalization to different planning tasks".

D1_discussion_open: "In this work, we have proposed the MAP architecture, a modular agentic approach aimed at improving planning with LLMs."
D2_limitation: "Although even this setting is challenging for LLMs, it will be important in future work to investigate how the proposed approach can be extended to more complex open-ended environments."
D3_outlook: positions cognitive-neuroscience-inspired modular decomposition as a generic recipe for LLM agents.
D4_paper_closing_sentence: "We look forward to investigating these possibilities in future work."

E1_methods_subheads: ["Experiment details", "Algorithms"]
F1_caption: "Figure 1 depicts the MAP architecture." — short noun-phrase ("Overview of MAP") style typical for architecture figures.
G1_hedges_used: "may", "potential", "challenging", "look forward to".
G2_strong_verbs: "outperformed", "demonstrate", "improve", "yields significant improvements", "displays superior transfer".
G3_paragraph_connectives: "With this goal in mind", "Taken together", "Finally", "In this work".
G4_taken_together: B6 explicit — "Taken together, these results indicate the potential of a brain-inspired approach…"

notable: **Cognitive-neuroscience hook** — the "brain-inspired" framing is the contribution lever, not just a metaphor. Section headers use a "**capability: task**" colon scheme (Problem solving: Tower of Hanoi) — distinct from MolE-style claim headers and from Pai-style numbered use cases. Limitations are framed as **future-work expansions** rather than caveats. Closing sentence is unusually short ("We look forward…") — almost epistolary.

---

## Paper 2: Xiao, C., Cai, J., Zhao, W., Zeng, G., Lin, B. Y., Han, X., Shi, Z., Zhao, Y., Liu, Z. & Sun, M. "Densing law of LLMs." Nature Machine Intelligence (2025).
- url_oa: https://arxiv.org/abs/2412.04315 ; https://arxiv.org/html/2412.04315v2 ; Nature record https://www.nature.com/articles/s42256-025-01137-0
- journal: Nature Machine Intelligence
- year: 2025
- category: method (empirical scaling-law / capacity-density methodology)

A1_title: "Densing law of LLMs"
A2_abstract_map:
  - S1 (BIG-PICTURE) — "Large Language Models (LLMs) have emerged as a milestone in artificial intelligence, and their performance can improve as the model size increases."
  - S2 (GAP) — "However, this scaling brings great challenges to training and inference efficiency, particularly for deploying LLMs in resource-constrained environments, and the scaling trend is becoming increasingly unsustainable."
  - S3 (HERE-WE / METRIC-INTRO) — "This paper introduces the concept of `capacity density' as a new metric to evaluate the quality of the LLMs across different scales and describes the trend of LLMs in terms of both effectiveness and efficiency."
  - S4 (METHOD-MECHANISM) — "To calculate the capacity density of a given target LLM, we first introduce a set of reference models and develop a scaling law to predict the downstream performance of these reference models based on their parameter sizes."
  - S5 (METHOD-DEFINITION) — "We then define the *effective parameter size* of the target LLM as the parameter size required by a reference model to achieve equivalent performance, and formalize the capacity density as the ratio of the effective parameter size to the actual parameter size of the target LLM."
  - S6 (FRAMING) — "Capacity density provides a unified framework for assessing both model effectiveness and efficiency."
  - S7 (KEY-RESULT-1) — "Our further analysis of recent open-source base LLMs reveals an empirical law (the densing law)that the capacity density of LLMs grows exponentially over time."
  - S8 (KEY-RESULT-2 / quantitative) — "More specifically, using some widely used benchmarks for evaluation, the capacity density of LLMs doubles approximately every three months."
  - S9 (IMPLICATION) — "The law provides new perspectives to guide future LLM development, emphasizing the importance of improving capacity density to achieve optimal results with minimal computational overhead."
A3_here_we_pivot: "To this end, we introduce the concept of capability density, which serves as a metric for evaluating and comparing the training quality of LLMs on various scales."
A4_strongest_quant_in_abstract: "the capacity density of LLMs doubles approximately every three months."

B1_intro_hook_style: milestone framing + scaling-cost paradox.
B1_quote_sentence1: "Large Language Models (LLMs) have emerged as a milestone in artificial intelligence, and their performance can improve as the model size increases."
B3_gap_phrases:
  - "this scaling brings great challenges to training and inference efficiency"
  - "the scaling trend is becoming increasingly unsustainable"
  - "However, by comparing some models with their compressed counterparts, we can observe that the widely used pruning and distillation methods usually result in smaller models with lower density than the original models."
B4_pivot_first2sent: "To this end, we introduce the concept of capability density, which serves as a metric for evaluating and comparing the training quality of LLMs on various scales."
B5_contributions: (1) capacity-density metric; (2) effective-parameter-size machinery via reference-model scaling law; (3) empirical "densing law" (exponential growth, doubling every 3 months); (4) corollaries on inference cost, deployability, and Moore-densing co-trajectory.
B6_last_intro_sentence: not separately verifiable; contributions are previewed in S7–S9.

C1_results_headers: ["3 Density Evolution", "3.1 Evaluation Settings", "3.2 Loss and Performance Estimation Results", "3.3 Densing Law", "3.4 Corollaries of Densing Law"]
C2_header_style: **numbered scientific-paper sections** ("3 Density Evolution"); each subsection a phenomenon name. Hierarchical, methodology-driven.
C3_section_openers:
  - {header: "3 Density Evolution", quote: "After defining LLM density, we analyze 29 widely-used open-source pre-trained base models from recent years.", class: dataset-first}
  - {header: "3.1 Evaluation Settings", quote: "In this work, we adopt the following widely-used datasets for evaluation: MMLU…", class: protocol-first}
C4_figure_callouts:
  - "Figure 1 presents the capability density of popular LLMs, measured by their performance on 55 widely-used benchmarks."
  - "We present the estimation results of the two-step process in Figure 2."
C5_quant_with_stats: "A≈0.007, which means the maximum density of LLMs doubles approximately every three months."
C6_baseline_comparison: implicit — references models compared against pruned/distilled counterparts and across model families.
C7_robustness_phrase: "we adopt the following widely-used datasets for evaluation" — robustness via benchmark breadth.
C8_generalization_phrase: "the capacity density of LLMs grows exponentially over time"; cross-benchmark stability.

D1_discussion_open: "Accurate Capability Measurement Capability density reflects the abilities of an LLM per unit of parameters."
D2_limitation: "Comprehensive evaluation: With the development of LLMs, the capabilities of LLMs significantly expand…" (limitation framed as benchmark-coverage gap); "The capability density measurement of LLMs relies on existing benchmarks to evaluate model performance."
D3_outlook: "encourage the LLM community to continue enhancing model capability density and achieving optimal performance with minimal computational costs."
D4_paper_closing_sentence: "We discuss several corollaries based on the law, and hope that the law and its corollaries will encourage the LLM community to continue enhancing model capability density and achieving optimal performance with minimal computational costs."

E1_methods_subheads: not enumerated verbatim.
F1_caption: "Figure 1 presents the capability density of popular LLMs…" — declarative + chart-anchored.
G1_hedges_used: "approximately", "increasingly", "may", "hope".
G2_strong_verbs: "introduces", "reveals", "doubles", "formalize", "guide".
G3_paragraph_connectives: "However", "More specifically", "To this end", "Accurate Capability Measurement".
G4_taken_together: implicit in S9 ("The law provides new perspectives…").

notable: **Title is a *law* claim** ("Densing law of LLMs") — declares an empirical regularity as the contribution, in the tradition of Kaplan/Chinchilla scaling laws. **Doubling-rate as headline number** ("every three months") replaces the conventional FLOPs/params figure as the metric of progress. Authored by a Tsinghua group — a 2025 example of Chinese AI research with clean Nature-MI rhetoric.

---

## Paper 3: Whitelam, S. "Sufficient is better than optimal for training neural networks." Nature Communications 16, 18044 (2025).
- url_oa: https://arxiv.org/abs/2410.19912 ; https://arxiv.org/html/2410.19912 ; https://www.nature.com/articles/s41467-025-66983-3
- journal: Nature Communications
- year: 2025
- category: method (novel training algorithm — physics-inspired non-optimization)

A1_title: "Sufficient is better than optimal for training neural networks"
A2_abstract_map:
  - S1 (BIG-PICTURE / paradox hook) — "The broad range of neural network training techniques that invoke optimization but rely on ad hoc modification for validity suggests that optimization-based training is misguided."
  - S2 (GAP) — "Shortcomings of optimization-based training are brought to particularly strong relief by the problem of overfitting, where naive optimization produces spurious outcomes."
  - S3 (CROSS-DOMAIN MOTIVATION) — "The broad success of neural networks for modelling physical processes has prompted advances that are based on inverting the direction of investigation and treating neural networks as if they were physical systems in their own right."
  - S4 (RESEARCH-QUESTION) — "These successes raise the question of whether broader, physical perspectives could motivate the construction of improved training algorithms."
  - S5 (HERE-WE / paradox-claim) — "Here, we introduce simmering, a physics-based method that trains neural networks to generate weights and biases that are merely 'good enough', but which, paradoxically, outperforms leading optimization-based approaches."
  - S6 (KEY-RESULT) — "Using classification and regression examples we show that simmering corrects neural networks that are overfit by Adam, and show that simmering avoids overfitting if deployed from the outset."
  - S7 (IMPLICATION) — "Our results question optimization as a paradigm for neural network training, and leverage information-geometric arguments to point to the existence of classes of sufficient training algorithms that do not take optimization as their starting point."
A3_here_we_pivot: "Here, we introduce simmering, a physics-based method that trains neural networks to generate weights and biases that are merely 'good enough', but which, paradoxically, outperforms leading optimization-based approaches."
A4_strongest_quant_in_abstract: no number — abstract relies on the *paradoxical-better-than-optimal* lexical claim ("merely 'good enough', but which, paradoxically, outperforms").

B1_intro_hook_style: **methodological-paradox** opening — accuses the dominant paradigm (optimization) of being "misguided".
B1_quote_sentence1: "The broad range of neural network training techniques that invoke optimization but rely on ad hoc modification for validity suggests that optimization-based training is misguided."
B3_gap_phrases:
  - "rely on ad hoc modification for validity"
  - "naive optimization produces spurious outcomes"
  - "These successes raise the question of whether broader, physical perspectives could motivate the construction of improved training algorithms."
B4_pivot_first2sent: "Here, we introduce simmering, a physics-based method that trains neural networks to generate weights and biases that are merely 'good enough', but which, paradoxically, outperforms leading optimization-based approaches."
B5_contributions: (1) physics-thermostat dynamics replacing gradient descent; (2) a single small-but-finite "simmering" temperature as the core hyperparameter; (3) empirical demonstration of overfit correction post-Adam; (4) overfit avoidance from-scratch; (5) ensemble-derived uncertainty estimates; (6) information-geometric argument for "sufficient" training.
B6_last_intro_sentence: not retrievable verbatim; section flows into "Sufficient Training by Simmering" Results header.

C1_results_headers: ["Sufficient Training by Simmering", "Ab Initio Sufficient Training", "Generalized Sufficient Training"]
C2_header_style: **declarative noun-phrase claims** ("Sufficient Training by Simmering"); each header asserts the method is "sufficient", echoing the title.
C3_section_openers:
  - {header: "Sufficient Training by Simmering" (overall results), quote: "Although neural networks' universal estimation capability allows them to represent many complex data relationships, that capability makes training generalizable networks challenging.", class: motivation-first}
C4_figure_callouts:
  - "Fig. 1a shows the evolution of the loss, with a clear divergence of the training and test loss during the Adam training stage."
  - "Fig. 2a shows results for classification and Fig. 2b shows results for regression."
C5_quant_with_stats: "During simmering, the thermostat temperature was increased from Tinitial=0 to Ttarget=0.05 in steps of ΔT=0.01 every 1000 iterations, with a learning rate of Δt=0.002."
C6_baseline_comparison: against Adam (used both as the baseline trainer and as the "overfit-victim" being repaired).
C7_robustness_phrase: "simmering corrects neural networks that are overfit by Adam, and … avoids overfitting if deployed from the outset" — robustness-as-repair phrasing.
C8_generalization_phrase: "classes of sufficient training algorithms that do not take optimization as their starting point" — lifts simmering to a class of methods.

D1_discussion_open: no separate Discussion section — the paper merges Discussion into Methods/Results closing.
D2_limitation: "The exact way in which changing gαγ(β,D) affects ∂θy is problem-dependent."
D3_outlook: implicit in S7 — "point to the existence of classes of sufficient training algorithms".
D4_paper_closing_sentence: not retrievable as a discrete closing line; paper transitions from main text directly to acknowledgements.

E1_methods_subheads: physics-thermostat sampling (Langevin-like); detailed-balance argument.
F1_caption: "Fig. 1a shows the evolution of the loss…" — declarative chart-anchored.
G1_hedges_used: "merely", "may", "tend to", "questions".
G2_strong_verbs: "introduces", "outperforms", "corrects", "avoids", "questions [the paradigm]".
G3_paragraph_connectives: "Here", "Using …", "Although", "These successes raise the question".
G4_taken_together: implicit in S7 ("Our results question optimization as a paradigm…").

notable: **Single-author paper** (rare for ML/AI in Nature-family). **Philosophical-rebuttal title** — "Sufficient is better than optimal" overtly contradicts the field's foundational verb ("optimize"). The hook is a **methodological paradox** — "ad hoc modification for validity suggests … misguided" — strong negative claim against the entire optimization paradigm. Closing is non-rhetorical (transitions to acknowledgements without a "future-vision" sentence) — unusual for Nature-family AI papers which typically deploy a closing telescope-verb.

---

## Paper 4: DeepSeek-AI; Guo, D., Yang, D., Zhang, H., Song, J., Zhang, R., Xu, R. et al. "DeepSeek-R1 incentivizes reasoning in LLMs through reinforcement learning." Nature 645, 633–638 (2025).
- url_oa: https://arxiv.org/abs/2501.12948 ; https://arxiv.org/html/2501.12948v1 ; Nature record https://www.nature.com/articles/s41586-025-09422-z
- journal: Nature
- year: 2025
- category: method (RL training methodology / reasoning emergence in LLMs)

A1_title: "DeepSeek-R1 incentivizes reasoning in LLMs through reinforcement learning"
A2_abstract_map:
  - S1 (BIG-PICTURE) — "General reasoning represents a long-standing and formidable challenge in artificial intelligence."
  - S2 (RECENT-ADVANCE) — "Recent breakthroughs, exemplified by large language models (LLMs) and chain-of-thought prompting, have achieved considerable success on foundational reasoning tasks."
  - S3 (GAP) — "However, this success is heavily contingent upon extensive human-annotated demonstrations, and models' capabilities are still insufficient for more complex problems."
  - S4 (HERE-WE) — "Here we show that the reasoning abilities of LLMs can be incentivized through pure reinforcement learning (RL), obviating the need for human-labeled reasoning trajectories."
  - S5 (KEY-MECHANISM / emergence claim) — "The proposed RL framework facilitates the emergent development of advanced reasoning patterns, such as self-reflection, verification, and dynamic strategy adaptation."
  - S6 (KEY-RESULT) — "Consequently, the trained model achieves superior performance on verifiable tasks such as mathematics, coding competitions, and STEM fields, surpassing its counterparts trained via conventional supervised learning on human demonstrations."
  - S7 (KEY-RESULT-2 / generalization) — "Moreover, the emergent reasoning patterns exhibited by these large-scale models can be systematically harnessed to guide and enhance the reasoning capabilities of smaller models."
A3_here_we_pivot: "Here we show that the reasoning abilities of LLMs can be incentivized through pure reinforcement learning (RL), obviating the need for human-labeled reasoning trajectories."
A4_strongest_quant_in_abstract: no abstract-level number — keyword "pure" RL and "obviating" are the lexical hooks. Quantitative weight (AIME 15.6→71.0%, +majority-vote 86.7%) deferred to Results.

B1_intro_hook_style: AGI-progress framing.
B1_quote_sentence1: "In recent years, Large Language Models (LLMs) have been undergoing rapid iteration and evolution, progressively diminishing the gap towards Artificial General Intelligence (AGI)."
B3_gap_phrases:
  - "However, the challenge of effective test-time scaling remains an open question for the research community."
  - "this success is heavily contingent upon extensive human-annotated demonstrations"
  - implicit: prior reasoning gains came from supervised CoT, not autonomous discovery
B4_pivot_first2sent: abstract S4 functions as the body pivot — "Here we show that the reasoning abilities of LLMs can be incentivized through pure reinforcement learning (RL)…".
B5_contributions: (1) DeepSeek-R1-Zero — RL-only training pipeline starting from base model, no SFT; (2) DeepSeek-R1 — multi-stage RL with cold-start data and rejection sampling; (3) emergent reasoning patterns (self-reflection, verification); (4) distillation pipeline transferring R1 reasoning into Qwen / Llama dense models at 1.5B–70B; (5) open weights and open-distilled-models release.
B6_last_intro_sentence: "We open-source the distilled Qwen and Llama series. Notably, our distilled 14B model outperforms state-of-the-art open-source QwQ-32B-Preview by a large margin, and the distilled 32B and 70B models set a new record on the reasoning benchmarks among dense models."

C1_results_headers: ["3.1 DeepSeek-R1 Evaluation", "3.2 Distilled Model Evaluation"] (preprint structure; Nature version uses similar two-tier results split).
C2_header_style: numbered subsections, **model-name-anchored** ("DeepSeek-R1 Evaluation") rather than capability or task headers.
C3_section_openers:
  - {header: "DeepSeek-R1 Evaluation", quote: "For education-oriented knowledge benchmarks such as MMLU, MMLU-Pro, and GPQA Diamond, DeepSeek-R1 demonstrates superior performance compared to DeepSeek-V3.", class: claim-first}
C4_figure_callouts:
  - "Figure 2: AIME accuracy of DeepSeek-R1-Zero during training. For each question, we sample 16 responses and calculate the overall average accuracy to ensure a stable evaluation."
  - "Figure 3: The average response length of DeepSeek-R1-Zero on the training set during the RL process."
C5_quant_with_stats: "The pass@1 score on AIME 2024 increases from 15.6% to 71.0%, and with majority voting, the score further improves to 86.7%, matching the performance of OpenAI-o1-0912."
C6_baseline_comparison: "matching the performance of OpenAI-o1-0912" — closed-API anchoring; also DeepSeek-V3 (its own SFT predecessor) as the no-RL baseline.
C7_robustness_phrase: "we sample 16 responses and calculate the overall average accuracy to ensure a stable evaluation"; rejection-sampling for robustness in stage 2.
C8_generalization_phrase: "emergent reasoning patterns exhibited by these large-scale models can be systematically harnessed to guide and enhance the reasoning capabilities of smaller models" — distillation-as-generalization.

D1_discussion_open: "In this work, we share our journey in enhancing model reasoning abilities through reinforcement learning."
D2_limitation: "Language Mixing: DeepSeek-R1 is currently optimized for Chinese and English, which may result in language mixing issues when handling queries in other languages."
D3_outlook: "Future versions will address this by implementing rejection sampling on software engineering data or incorporating asynchronous evaluations during the RL process to improve efficiency."
D4_paper_closing_sentence: "Future versions will address this by implementing rejection sampling on software engineering data or incorporating asynchronous evaluations during the RL process to improve efficiency."

E1_methods_subheads: GRPO algorithm; rule-based reward design (accuracy + format); cold-start SFT data; multi-stage training pipeline; distillation procedure.
F1_caption: "Figure 2: AIME accuracy of DeepSeek-R1-Zero during training." — declarative + protocol detail.
G1_hedges_used: "may", "currently", "share our journey", "future versions will".
G2_strong_verbs: "incentivizes", "obviating", "facilitates", "surpassing", "harnessed", "set a new record".
G3_paragraph_connectives: "However", "Notably", "Moreover", "Consequently", "In this work".
G4_taken_together: implicit — the closing-paragraph structure substitutes for "taken together".

notable: **Verb-driven title** — "incentivizes" is a strong, agentic verb (rare in titles). **Emergence as result** — the paper claims emergent behaviours (self-reflection, verification, dynamic strategy adaptation) as *first-class results*, not side observations. **Numbered enumerated limitations** (Language Mixing / Prompting Engineering / Software Engineering Tasks) — same enumerated-caveat pattern noted in Pai et al. (06-ml.md Paper 5) and FunSearch. **Authors-as-organization byline** ("DeepSeek-AI") — Nature-style company-author convention now extended from DeepMind to Chinese AI labs.

---

## Paper 5: Oh, J., Farquhar, G., Schroecker, Y., Chen, R., Whiteson, S., Singh, S. & Silver, D. "Discovering state-of-the-art reinforcement learning algorithms." Nature 648, 312–319 (2025).
- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC12695655/ ; https://www.nature.com/articles/s41586-025-09761-x
- journal: Nature
- year: 2025
- category: method (meta-learning / AI-discovers-algorithm / RL methodology)

A1_title: "Discovering state-of-the-art reinforcement learning algorithms"
A2_abstract_map:
  - S1 (BIG-PICTURE / biology analogy) — "Humans and other animals use powerful reinforcement learning (RL) mechanisms that have been discovered by evolution over many generations of trial and error."
  - S2 (CONTRAST) — "By contrast, artificial agents typically learn using handcrafted learning rules."
  - S3 (GAP / longevity) — "Despite decades of interest, the goal of autonomously discovering powerful RL algorithms has proven to be elusive."
  - S4 (HERE-WE) — "Here we show that it is possible for machines to discover a state-of-the-art RL rule that outperforms manually designed rules."
  - S5 (METHOD) — "This was achieved by meta-learning from the cumulative experiences of a population of agents across a large number of complex environments."
A3_here_we_pivot: "Here we show that it is possible for machines to discover a state-of-the-art RL rule that outperforms manually designed rules."
A4_strongest_quant_in_abstract: no number — qualitative "state-of-the-art" + "outperforms manually designed rules"; numbers (Disco57 IQM 13.86) deferred to Results.

B1_intro_hook_style: **goal-of-AI** statement (first-principles framing).
B1_quote_sentence1: "The primary goal of artificial intelligence is to design agents that, like humans, can predict and act in complex environments to achieve goals."
B3_gap_phrases:
  - "Unlike humans, whose learning mechanism has been naturally discovered by biological evolution, RL algorithms are typically manually designed."
  - "the goal of autonomously discovering powerful RL algorithms has proven to be elusive"
  - implicit: hand-tuned RL hyperparameters do not transfer
B4_pivot_first2sent: "In this work, we introduce an autonomous method for discovering RL rules solely through the experience of many generations of agents interacting with various environments."
B5_contributions: (1) meta-network parametrization of an RL update rule; (2) population-based training across diverse environments as the "evolutionary" loop; (3) **Disco57 / DiscoRL** — a discovered rule beating MuZero/IMPALA on Atari IQM; (4) zero-shot generalization to ProcGen/Crafter/NetHack/Sokoban; (5) emergent novel prediction semantics distinct from value functions.
B6_last_intro_sentence: "To choose a general space of discovery, we observe that the essential component of standard RL algorithms is a rule that updates one or more predictions, as well as the policy itself, towards targets that are functions of quantities such as future rewards and future predictions."

C1_results_headers: ["Atari", "Generalization", "Complex and diverse environments", "Efficiency and scalability", "Effect of discovering new predictions"]
C2_header_style: **benchmark-and-property** mix — single-word benchmark names ("Atari", "Generalization") plus property-anchored phrases ("Effect of discovering new predictions"); declarative-claim-as-header is absent in favour of neutral nouns.
C3_section_openers:
  - {header: "Atari", quote: "The Atari benchmark, one of the most studied benchmarks in the history of RL, consists of 57 Atari 2600 games.", class: definition-first}
  - {header: "Generalization", quote: "We further investigated the generality of Disco57 by evaluating it on a variety of held-out benchmarks that it was never exposed to during discovery.", class: protocol-first}
C4_figure_callouts:
  - "**a**, Discovery. Multiple agents, interacting with various environments, are trained in parallel according to the learning rule, defined by the meta-network."
  - "**a**–**f**, Performance of DiscoRL compared to human-designed RL rules on Atari (**a**), ProcGen (**b**), DMLab (**c**), Crafter (**d**; figure inset shows results for 1 million environment steps), NetHack (**e**), and Sokoban (**f**)."
C5_quant_with_stats: "Disco57 achieved an IQM of 13.86, outperforming all existing RL rules on the Atari benchmark, with a substantially higher wall-clock efficiency compared with the state-of-the-art MuZero."
C6_baseline_comparison: "outperforming all existing RL rules on the Atari benchmark"; explicit IMPALA comparison with matched settings.
C7_robustness_phrase: "For a fair comparison, we trained an agent with the importance weighted actor-learner architecture (IMPALA) algorithm using the same settings as Disco57."
C8_generalization_phrase: "evaluating it on a variety of held-out benchmarks that it was never exposed to during discovery"; "performance and generality of DiscoRL improves further as more diverse and complex environments are used in discovery."

D1_discussion_open: "Enabling machines to discover learning algorithms for themselves is one of the most promising ideas in artificial intelligence owing to its potential for open-ended self-improvement."
D2_limitation: not flagged as a discrete limitation paragraph — the paper closes on outlook rather than caveat.
D3_outlook: "the design of RL algorithms for advanced AI may in the future be led by machines that can scale effectively with data and compute."
D4_paper_closing_sentence: "This suggests that the design of RL algorithms for advanced AI may in the future be led by machines that can scale effectively with data and compute."

E1_methods_subheads: meta-network architecture; agent populations; benchmark suites; IMPALA-matched controls.
F1_caption: bold-letter panel labels ("**a**, Discovery."), Nature-house declarative micro-titles per panel.
G1_hedges_used: "may", "elusive", "promising", "potential".
G2_strong_verbs: "discover", "outperforms", "surpass", "scale effectively", "led by machines".
G3_paragraph_connectives: "By contrast", "Despite decades", "Here we show", "We further investigated".
G4_taken_together: D4 closing performs the role ("This suggests…").

notable: **Biology-vs-engineering analogy** as opener — same cross-engineering-domain hook pattern noted in SemanticLens (06-ml.md Paper 4). **Title is a verb-noun-phrase** ("Discovering …") — present-participle voice signals the paper *is* the discovery process. **No discrete limitations paragraph** — this is unusual among 2024-25 NMI/NC AI papers (which typically enumerate caveats); Nature-published DeepMind work tends to omit the limitations bullet list and substitute outlook.

---

## Paper 6: Farquhar, S., Kossen, J., Kuhn, L. & Gal, Y. "Detecting hallucinations in large language models using semantic entropy." Nature 630, 625–630 (2024).
- url_oa: https://pmc.ncbi.nlm.nih.gov/articles/PMC11186750/ ; Nature record https://www.nature.com/articles/s41586-024-07421-0
- journal: Nature
- year: 2024
- category: method (uncertainty estimation / hallucination detection methodology)

A1_title: "Detecting hallucinations in large language models using semantic entropy"
A2_abstract_map:
  - S1 (BIG-PICTURE / problem) — "Large language model (LLM) systems, such as ChatGPT or Gemini, can show impressive reasoning and question-answering capabilities but often 'hallucinate' false outputs and unsubstantiated answers."
  - S2 (STAKES / examples) — "Answering unreliably or without the necessary information prevents adoption in diverse fields, with problems including fabrication of legal precedents or untrue facts in news articles and even posing a risk to human life in medical domains such as radiology."
  - S3 (GAP / partial-prior) — "Encouraging truthfulness through supervision or reinforcement has been only partially successful."
  - S4 (RESEARCH-NEED) — "Researchers need a general method for detecting hallucinations in LLMs that works even with new and unseen questions to which humans might not know the answer."
  - S5 (HERE-WE) — "Here we develop new methods grounded in statistics, proposing entropy-based uncertainty estimators for LLMs to detect a subset of hallucinations—confabulations—which are arbitrary and incorrect generations."
  - S6 (METHOD-MECHANISM) — "Our method addresses the fact that one idea can be expressed in many ways by computing uncertainty at the level of meaning rather than specific sequences of words."
  - S7 (KEY-RESULT / generalization) — "Our method works across datasets and tasks without a priori knowledge of the task, requires no task-specific data and robustly generalizes to new tasks not seen before."
  - S8 (IMPACT) — "By detecting when a prompt is likely to produce a confabulation, our method helps users understand when they must take extra care with LLMs and opens up new possibilities for using LLMs that are otherwise prevented by their unreliability."
A3_here_we_pivot: "Here we develop new methods grounded in statistics, proposing entropy-based uncertainty estimators for LLMs to detect a subset of hallucinations—confabulations—which are arbitrary and incorrect generations."
A4_strongest_quant_in_abstract: no number — abstract is qualitative ("works across datasets", "robustly generalizes"); the headline AUROC 0.790 is in Results.

B1_intro_hook_style: **stakes-quote** opener — "users cannot trust" framing.
B1_quote_sentence1: "'Hallucinations' are a critical problem for natural language generation systems using large language models (LLMs), such as ChatGPT or Gemini, because users cannot trust that any given output is correct."
B3_gap_phrases:
  - "users cannot trust that any given output is correct"
  - "Encouraging truthfulness through supervision or reinforcement has been only partially successful."
  - "Researchers need a general method for detecting hallucinations in LLMs that works even with new and unseen questions to which humans might not know the answer."
B4_pivot_first2sent: "To detect confabulations, we use probabilistic tools to define and then measure the 'semantic' entropy of the generations of an LLM—an entropy that is computed over meanings of sentences."
B5_contributions: (1) confabulations sub-class definition; (2) semantic entropy estimator (cluster-and-aggregate); (3) discrete approximation usable without log-probs (works on GPT-4); (4) generalization across LLaMA / Falcon / Mistral 7B–70B; (5) extension to long-form biographies via factoid decomposition.
B6_last_intro_sentence: "One exciting aspect of our approach is the way it makes use of classical probabilistic machine learning methods and adapts them to the unique properties of modern LLMs and free-form language generation."

C1_results_headers: ["Detecting confabulations in QA and math", "Detecting confabulations in biographies"]
C2_header_style: **task-and-domain noun-phrase** ("Detecting confabulations in QA and math") — gerund-led, capability-and-domain pair.
C3_section_openers:
  - {header: "Detecting confabulations in QA and math", quote: "In Fig. 2, we show that both semantic entropy and its discrete approximation outperform our best baselines for sentence-length generations.", class: claim-first}
  - {header: "Detecting confabulations in biographies", quote: "Semantic entropy is most natural for sentences that express a single proposition but the idea of semantic equivalence is trickier to apply to longer passages which express many propositions which might only agree partially.", class: motivation-first}
C4_figure_callouts:
  - "An overview of semantic entropy and confabulation detection."
  - "Semantic entropy outperforms leading baselines and naive entropy. AUROC (scored on the y-axes) measures how well methods predict LLM mistakes, which correlate with confabulations."
C5_quant_with_stats: "Averaged across the 30 combinations of tasks and models we study, semantic entropy achieves the best AUROC value of 0.790 whereas naive entropy (0.691), P(True) (0.698) and the embedding regression baseline (0.687) lag behind it. Semantic entropy performs well consistently, with stable performance (between 0.78 and 0.81 AUROC) across the different model families (LLaMA, Falcon and Mistral) and scales (from 7B to 70B parameters) which we study."
C6_baseline_comparison: "Our methods also outperform the supervised embedding regression method both in- and out-of-distribution."; "Semantic entropy also outperforms P(True) which is supervised 'in-context'; that is, it is adapted to the deployment task with a few training examples provided in the LLM prompt itself."
C7_robustness_phrase: "stable performance (between 0.78 and 0.81 AUROC) across the different model families (LLaMA, Falcon and Mistral) and scales (from 7B to 70B parameters)"
C8_generalization_phrase: "robustly generalizes to new tasks not seen before"; "without a priori knowledge of the task".

D1_discussion_open: "Our probabilistic approach, accounting for semantic equivalence, detects an important class of hallucinations: those that are caused by a lack of LLM knowledge."
D2_limitation: "Our method explicitly does not directly address situations in which LLMs are confidently wrong because they have been trained with objectives that systematically produce dangerous behaviour, cause systematic reasoning errors or are systematically misleading the user."
D3_outlook: positions semantic entropy as a building block for trustworthy LLM deployment.
D4_paper_closing_sentence: "We hope to inspire a fruitful exchange of well-studied methods and emerging new problems by highlighting the importance of meaning when addressing language-based machine learning problems."

E1_methods_subheads: semantic clustering via bidirectional entailment; discrete entropy estimator; biographical fact decomposition.
F1_caption: "An overview of semantic entropy and confabulation detection." — short noun-phrase.
G1_hedges_used: "subset of", "may", "explicitly does not directly address", "only partially successful".
G2_strong_verbs: "outperform", "robustly generalizes", "detects", "addresses".
G3_paragraph_connectives: "However", "As a result", "Here we", "By detecting".
G4_taken_together: implicit in S8 ("By detecting…opens up new possibilities…").

notable: **Sub-typing the problem in the title** — "hallucinations" via "semantic entropy" but the abstract narrows to **confabulations** as a precise sub-class. Defining a fine-grained sub-class is a rhetorical move that limits scope while preserving rigor — distinctive among LLM-safety abstracts. **Honest limitation** — the paper explicitly disclaims systematic-misleading detection, a sharp caveat. AUROC is reported with **count-of-experiments anchor** ("Averaged across the 30 combinations of tasks and models") — a transparency pattern.

---

## Paper 7: Muttenthaler, L. et al. (Google DeepMind / Helmholtz Munich). "Aligning machine and human visual representations across abstraction levels." Nature 648, 165–173 (2025).
- url_oa: https://arxiv.org/abs/2409.06509 ; https://arxiv.org/html/2409.06509v4 ; Nature record https://www.nature.com/articles/s41586-025-09631-6
- journal: Nature
- year: 2025
- category: method (representation-distillation / human-aligned VLM / interpretability-via-alignment)

A1_title: "Aligning machine and human visual representations across abstraction levels"
A2_abstract_map:
  - S1 (BIG-PICTURE) — "Deep neural networks have achieved success across a wide range of applications, including as models of human behavior and neural representations in vision tasks."
  - S2 (GAP) — "However, neural network training and human learning differ in fundamental ways, and neural networks often fail to generalize as robustly as humans do raising questions regarding the similarity of their underlying representations."
  - S3 (RESEARCH-QUESTION) — "What is missing for modern learning systems to exhibit more human-aligned behavior?"
  - S4 (DIAGNOSIS) — "We highlight a key misalignment between vision models and humans: whereas human conceptual knowledge is hierarchically organized from fine- to coarse-scale distinctions, model representations do not accurately capture all these levels of abstraction."
  - S5 (METHOD / pivot) — "To address this misalignment, we first train a teacher model to imitate human judgments, then transfer human-aligned structure from its representations to refine the representations of pretrained state-of-the-art vision foundation models via finetuning."
  - S6 (KEY-RESULT-1 / human-anchored) — "These human-aligned models more accurately approximate human behavior and uncertainty across a wide range of similarity tasks, including a new dataset of human judgments spanning multiple levels of semantic abstractions."
  - S7 (KEY-RESULT-2 / ML benchmarks) — "They also perform better on a diverse set of machine learning tasks, increasing generalization and out-of-distribution robustness."
  - S8 (IMPLICATION) — "Thus, infusing neural networks with additional human knowledge yields a best-of-both-worlds representation that is both more consistent with human cognitive judgments and more practically useful, thus paving the way toward more robust, interpretable, and human-aligned artificial intelligence systems."
A3_here_we_pivot: "To address this misalignment, we first train a teacher model to imitate human judgments, then transfer human-aligned structure from its representations to refine the representations of pretrained state-of-the-art vision foundation models via finetuning."
A4_strongest_quant_in_abstract: no headline number — abstract uses comparative qualitative claims ("more accurately approximate", "increasing generalization"); body reports 36–69% accuracy ranges.

B1_intro_hook_style: **negative-capability** opening ("fail in ways that humans would not").
B1_quote_sentence1: "While deep learning has recently driven rapid progress in areas of artificial intelligence such as natural language processing and computer vision, even the best of these systems often fail in ways that humans would not."
B3_gap_phrases:
  - "even the best of these systems often fail in ways that humans would not"
  - "model representations tend to fail to capture the full multi-level conceptual structure of human knowledge"
  - "What is missing for modern learning systems to exhibit more human-aligned behavior?"
B4_pivot_first2sent: "Here, we highlight a key misalignment between humans and deep learning models that may underlie some of these differences..."
B5_contributions: (1) AligNet — human-judgement-distilled teacher; (2) soft-alignment fine-tuning recipe; (3) new multi-abstraction-level human-judgement dataset; (4) consistency improvements on triplet odd-one-out tasks; (5) generalization gains on downstream ML benchmarks (OOD robustness, few-shot).
B6_last_intro_sentence: "establishes a principle for aligning models to humans—focusing on the multi-scale relational structure of human knowledge."

C1_results_headers: ["2.1 Toward more human-aligned models", "2.1.1 Alignment at multiple levels of abstraction", "2.2 Aligned models reflect the conceptual hierarchy", "2.3 Alignment improves generalization and out-of-distribution robustness"]
C2_header_style: **claim-as-header / capability-anchored** ("Aligned models reflect the conceptual hierarchy"; "Alignment improves generalization") — declarative-finding style à la MolE Section 4.
C3_section_openers:
  - {header: "2.1 Toward more human-aligned models", quote: "To build foundation models with more human-aligned behavior we inject additional supervision about human behavior into the model representations…", class: method-first}
  - {header: "2.2 Aligned models reflect the conceptual hierarchy", quote: "While the model representations are dissimilar before alignment, they become more aligned with each other after soft-alignment.", class: claim-first via contrast}
  - {header: "2.3 Alignment improves generalization", quote: "We investigated how alignment improves generalization and out-of-distribution robustness across a variety of downstream tasks.", class: motivation-first}
C4_figure_callouts:
  - "Figure 1: a: An example of the triplet odd-one-out task where a human and a neural network model choose…"
  - "Figure 2: Human alignment results. a: Odd-one-out accuracies on the THINGS dataset…"
C5_quant_with_stats: "All performance increases are statistically significant at α=0.05; for details see the SI. The base models achieved low accuracies of 36.09% (ViT-B) − 57.38% (DINOv2 ViT-B). AligNet models significantly improved; all models performed well, with accuracies of 65.70% (DINOv1 ViT-B) − 68.56% (DINOv2 ViT-B)."
C6_baseline_comparison: "These human-aligned models more accurately approximate human behavior and uncertainty"; comparison vs base ViT-B / DINOv1 / DINOv2 / SigLIP / CLIP.
C7_robustness_phrase: "across various levels of visual abstraction"; "out-of-distribution robustness".
C8_generalization_phrase: "infusing neural networks with additional human knowledge yields a best-of-both-worlds representation"; OOD generalization framed as the *transfer* of human-priors.

D1_discussion_open: "The differences between natural intelligence and the capabilities of neural networks are the subject of long-standing debates."
D2_limitation: "Human representations may vary systematically across individuals, cultures, and so on. Finally, human judgment is full of flaws, intrinsic contradictions and discrepancies."
D3_outlook: "We hope that our work will inspire more general approaches to (softly) aligning models by distilling human priors into their representations."
D4_paper_closing_sentence: "We hope that our work will inspire more general approaches to (softly) aligning models by distilling human priors into their representations."

E1_methods_subheads: AligNet teacher construction; soft-label fine-tuning loss; THINGS triplet dataset; multi-level human-judgement collection.
F1_caption: "Figure 1: a: An example of the triplet odd-one-out task where a human and a neural network model choose…" — protocol-anchored, panel-letter dense.
G1_hedges_used: "may", "tend to", "softly", "intrinsic contradictions and discrepancies".
G2_strong_verbs: "approximate", "transfer", "outperform", "establishes", "infusing".
G3_paragraph_connectives: "However", "While", "Thus", "Here, we highlight".
G4_taken_together: S8 functions as the integrative summary ("Thus, infusing neural networks…").

notable: **Cognitive-science alignment as the contribution** — neither pure ML benchmark nor pure cognitive-science modelling, but a *hybridization*. **Limitation acknowledges that the supervision target is itself flawed** ("human judgment is full of flaws, intrinsic contradictions") — an unusually self-critical limitation among AI-method papers; flips the usual asymmetry where humans are treated as gold standard. **Headers mix numbered scientific-paper sections (2.1.1) with claim-anchored phrasing** — a hybrid Nature / arXiv-physics style.

---

## Paper 8: Zhou, L., Pacchiardi, L., Martínez-Plumed, F., Collins, K. M., Moros-Daval, Y., Zhang, S., Zhao, Q., Huang, Y., Sun, L., Prunty, J. E., Li, Z., Sánchez-Monzón, P., Schellaert, W., Ó hÉigeartaigh, S., Tešić, J., Hernández-Orallo, J. et al. "General scales unlock AI evaluation with explanatory and predictive power." Nature 652, 58–67 (2026).
- url_oa: https://arxiv.org/abs/2503.06378 ; https://arxiv.org/html/2503.06378 ; Nature record https://www.nature.com/articles/s41586-026-10303-2
- journal: Nature
- year: 2026
- category: method (AI evaluation methodology / measurement framework)

A1_title: "General scales unlock AI evaluation with explanatory and predictive power"
A2_abstract_map:
  - S1 (BIG-PICTURE / stakes) — "Ensuring safe and effective use of AI requires understanding and anticipating its performance on novel tasks, from advanced scientific challenges to transformed workplace activities."
  - S2 (GAP) — "So far, benchmarking has guided progress in AI, but it has offered limited explanatory and predictive power for general-purpose AI systems, given the low transferability across diverse tasks."
  - S3 (HERE-WE) — "In this paper, we introduce general scales for AI evaluation that can explain what common AI benchmarks really measure, extract ability profiles of AI systems, and predict their performance for new task instances, in- and out-of-distribution."
  - S4 (METHOD-MECHANISM) — "Our fully-automated methodology builds on 18 newly-crafted rubrics that place instance demands on general scales that do not saturate."
  - S5 (KEY-RESULT-1) — "Illustrated for 15 large language models and 63 tasks, high explanatory power is unleashed from inspecting the demand and ability profiles…"
  - S6 (KEY-RESULT-2 / surprise) — "Surprisingly, high predictive power at the instance level becomes possible using these demand levels, providing superior estimates over black-box baseline predictors…"
  - S7 (IMPLICATION) — "The scales, rubrics, battery, techniques and results presented here represent a major step for AI evaluation, underpinning the reliable deployment of AI in the years ahead."
A3_here_we_pivot: "In this paper, we introduce general scales for AI evaluation that can explain what common AI benchmarks really measure, extract ability profiles of AI systems, and predict their performance for new task instances, in- and out-of-distribution."
A4_strongest_quant_in_abstract: "15 large language models and 63 tasks" + "18 newly-crafted rubrics" — count-anchored breadth, not a delta.

B1_intro_hook_style: **safety-stakes** opening — frames evaluation as a deployment safety problem.
B1_quote_sentence1: "Ensuring safe and effective use of AI requires understanding and anticipating its performance on novel tasks, from advanced scientific challenges to transformed workplace activities."
B3_gap_phrases:
  - "limited explanatory and predictive power for general-purpose AI systems"
  - "low transferability across diverse tasks"
  - "The traditional performance-oriented evaluation approach has shown limited predictive power at the instance level, inside or outside the benchmark."
B4_pivot_first2sent: "Here, we will put this design criterion to the test." (followed by methodology setup).
B5_contributions: (1) 18 cognitive-demand rubrics covering breadth × depth × novelty axes; (2) ADeLe battery of 63 tasks × 15 LLMs; (3) explanatory power — benchmark sensitivity/specificity profiles; (4) ability-profile visualisation via non-saturating characteristic curves; (5) instance-level performance prediction with OOD validity; (6) Delphi-consensus validation against GPT-4o annotations.
B6_last_intro_sentence: not retrievable as a discrete sentence; intro flows into RQ1–RQ4 result enumeration.

C1_results_headers: ["3.1 Annotation and Scales Analysis: Distinguishing Levels and Dimensions", "3.2 Explanatory Power Analysis: Profiling Benchmark Demands", "3.3 Explanatory Power Analysis: Profiling LLM Abilities", "3.4 Predictive Power Analysis: Anticipating Performance with Assessors"]
C2_header_style: **two-part colon scheme** — "Capability-Type: What-It-Does" (Annotation … : Distinguishing Levels and Dimensions). Each header is essentially a research-question label.
C3_section_openers (RQ-style):
  - {header: "3.1 Annotation and Scales", quote: "RQ1 examines whether humans can reliably distinguish rubric levels across dimensions.", class: research-question-first}
  - {header: "3.2 Profiling Benchmark Demands", quote: "RQ2 investigates benchmark sensitivity and specificity through demand profiling.", class: research-question-first}
  - {header: "3.3 Profiling LLM Abilities", quote: "RQ3 explores whether non-saturating visualizations reveal model capability evolution.", class: research-question-first}
  - {header: "3.4 Predictive Power Analysis", quote: "RQ4 tests instance-level prediction robustness across distribution conditions.", class: research-question-first}
C4_figure_callouts:
  - "Figure 3: The characteristic curve of Llama-3.1-405B-Instruct for dimension KNn (Knowledge of Natural Sciences)"
  - "Figure 4: Correlations of the demand level using all the items in the ADeLe battery for all pairs of the 18 demands"
C5_quant_with_stats: "Inter-rater agreement (rWG index) for the 18 demands ranges between 0.70 and 0.91 (averaging 0.83), with Delphi consensus compared against GPT-4o showing Spearman correlation between 0.75 and 0.94 (averaging 0.86)."
C6_baseline_comparison: "providing superior estimates over strong black-box baseline predictors, especially in out-of-distribution settings (new tasks and benchmarks)."
C7_robustness_phrase: "in- and out-of-distribution"; non-saturating characteristic curves.
C8_generalization_phrase: "high predictive power at the instance level"; "across in- and out-of-distribution settings".

D1_discussion_open: not retrievable as a discrete sentence; the paper closes via implications-of-methodology.
D2_limitation: "The current battery includes only a modest number of benchmarks specifically exploring agent-like functions, thus limiting empirical evidence in these areas."
D3_outlook: "underpinning the reliable deployment of AI in the years ahead."
D4_paper_closing_sentence: "The scales, rubrics, battery, techniques and results presented here represent a major step for AI evaluation, underpinning the reliable deployment of AI in the years ahead."

E1_methods_subheads: rubric-design protocol; Delphi consensus and GPT-4o annotation; non-saturating-curve fitting; assessor models for prediction.
F1_caption: "Figure 3: The characteristic curve of Llama-3.1-405B-Instruct for dimension KNn (Knowledge of Natural Sciences)" — protocol-and-target dense.
G1_hedges_used: "limited", "approximately", "modest", "may", "in the years ahead".
G2_strong_verbs: "unlock", "introduce", "explain", "extract", "predict", "underpinning".
G3_paragraph_connectives: "So far", "Surprisingly", "In this paper", "Here, we will put this design criterion to the test."
G4_taken_together: S7 ("The scales, rubrics, battery…represent a major step…").

notable: **Title verb "unlock"** is unusual in evaluation literature — turns measurement methodology into a *capability gain*. Headers are explicit **Research-Questions (RQ1–RQ4)** with colon-separated capability labels — a deliberate *psychometrics* style transferred into AI methodology. Quantitative passages emphasise **inter-rater agreement coefficients** rather than benchmark accuracies — a measurement-validation pattern (rWG, Spearman) imported from psychometrics, not standard ML. Authors include cognitive scientists + AI safety researchers — interdisciplinary byline reflected in vocabulary.

---

## Cross-paper observations

These are *new* patterns this batch (07) reveals beyond what 06-ml.md surfaced.

1. **Two new abstract hooks**: (a) **Capability-paradox / paradigm-rebuttal** — Whitelam's "optimization-based training is misguided" and "merely 'good enough', but … paradoxically, outperforms" — opens by attacking the field's foundational verb. (b) **Empirical-law / measurement** — Xiao's "Densing law" and Zhou's "general scales" frame the paper as a *new ruler*, not a new tool. Both differ from the engineering-analogy hook (SemanticLens) and the easy-to-evaluate hook (FunSearch) in 06-ml.

2. **Mechanistic / interpretability-adjacent papers prefer claim-anchored or RQ-anchored headers, *not* method-anchored.** Muttenthaler: "Aligned models reflect the conceptual hierarchy"; Zhou: "Profiling Benchmark Demands"; Webb: "Problem solving: Tower of Hanoi" (capability-colon-task). Method-named headers ("Architecture", "Training procedure") appear nowhere in this batch — consistent with 06-ml's finding but extended: even pure-methodology papers prefer **what-it-does** over **what-it-is** in section titles.

3. **LLM-agent papers uniformly under-report prompts and decoding details in main text.** Webb's MAP paper names modules but defers prompts to SI; ChemCrow (06-ml) does the same. **No paper in either batch reports temperature / top-p / max-tokens in the main text.** API-version pinning and seed disclosure appear only in Methods or SI — a gap SKILL §6 may want to standardize.

4. **Alignment / safety / evaluation papers carry *honestly self-critical* limitations.** Farquhar: "Our method explicitly does not directly address situations in which LLMs are confidently wrong because they have been trained with objectives that systematically produce dangerous behaviour…" — actively lists what the method *cannot* catch. Muttenthaler: "human judgment is full of flaws, intrinsic contradictions and discrepancies" — admits the supervision target itself is unreliable. Zhou: "limiting empirical evidence in these areas". This is **stricter than the named-bullet limitation pattern** of Pai et al. / FunSearch in 06-ml — these papers concede *correctness* gaps, not just scope gaps.

5. **Closing-sentence telescope-verbs in 2024-26 AI methodology**: "We hope to inspire" (Farquhar, Muttenthaler) → invitational; "represent a major step … underpinning" (Zhou) → infrastructural; "may in the future be led by machines" (Oh) → autonomy-shifting; "We look forward to investigating" (Webb) — short and epistolary; "encourage the LLM community … to continue enhancing" (Xiao) → community-summons. **New verbs not in 06-ml: "underpinning", "incentivizes" (in title), "unlock" (in title).** "Envision", "demonstrate", "promising" remain common.

6. **Quant-density peak shifts from abstract S5 to abstract S6–S8 in this batch.** Of 8 papers, 5 (Xiao, DeepSeek-R1, Oh, Farquhar, Muttenthaler) place strongest claim verbs ("doubles every 3 months", "surpassing", "outperforms", "robustly generalizes", "increasing generalization") in S6–S7 rather than S4–S5. **Method-introduction sentence (pivot) tends to land at S3–S5 rather than the canonical S3** — pure-AI methodology papers spend earlier sentences on stakes-framing and gap-naming.

7. **Numbers in pure-AI methodology abstracts are about *scale of evidence*, not *delta of metric*.** Zhou: "15 large language models and 63 tasks" + "18 newly-crafted rubrics". Xiao: "every three months". Webb: no numbers (lets emergence narrative carry). Farquhar: no numbers in abstract. Compare to 06-ml application papers (Pai: "11,467 lesions"; MolE: "842 million graphs") — application-flavored AI papers headline data-scale; pure-AI-methods papers headline **scale-of-evaluation** or **rate-of-trend**.

8. **Cross-engineering analogies persist (SemanticLens), now joined by *cross-evolution* and *cross-psychometrics* hooks.** Oh / DiscoRL: "Humans and other animals use powerful reinforcement learning … discovered by evolution" — biology-as-method-source. Zhou / ADeLe: rWG inter-rater agreement, Delphi consensus, characteristic curves — psychometrics imported wholesale. The pattern is: pure-AI methodology papers reach into **a non-CS measurement tradition** (engineering systems, psychometrics, statistical mechanics — Whitelam's thermostat dynamics) for both rhetoric and method.

9. **Title patterns split sharply by claim-type.**
   - **Discovery-as-title** (Oh: "Discovering …"; Romera-Paredes 06-ml: "Mathematical discoveries from …") — present-participle, the title *is* the contribution being announced.
   - **Capability-as-title** (DeepSeek-R1: "incentivizes reasoning …"; Zhou: "unlock AI evaluation …") — verb-led, agentic.
   - **Law / regularity title** (Xiao: "Densing law of LLMs") — declares an empirical law.
   - **Negative-frame title** (Whitelam: "Sufficient is better than optimal …") — overtly contradicts dominant view.
   - **Method-name colon** is absent in this batch — none of the 8 use the "Foo: a method for X" stem common in MolE-style papers.

10. **Reproducibility / open-weights signaling has migrated from Methods section to *intro-final-paragraph* and even to the abstract.** DeepSeek-R1 intro closes with "We open-source the distilled Qwen and Llama series" — open-source release is part of the contribution preview, not Methods. Oh's DiscoRL has accompanying GitHub published at acceptance. This intensifies the 06-ml trend (SemanticLens GitHub URL in abstract): **open-release is now near-mandatory and rhetorically foregrounded** for Nature-family AI methodology papers, especially for Chinese / DeepMind-affiliated work.
