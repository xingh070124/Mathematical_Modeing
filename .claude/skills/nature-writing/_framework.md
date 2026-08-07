# Analytical Framework — what to extract from each paper

Used as the extraction prompt for subagents. Goal: per-paper, return a compact structured record of writing patterns. Quote actual phrases (≤25 words each) — do NOT paraphrase, because we want the real lexical patterns.

## A. Title & Abstract

- **A1. Title pattern**: declarative finding ("X enables Y"), tool-name colon ("Foo: a method for ..."), question, or noun phrase. Quote the title.
- **A2. Abstract sentence map**: number each sentence; for each, label its rhetorical role from this set:
  - BIG-PICTURE / FIELD-IMPORTANCE
  - GAP / UNRESOLVED-PROBLEM
  - HERE-WE / METHOD-INTRO
  - KEY-RESULT-1 (quantitative)
  - KEY-RESULT-2 (generalization or second axis)
  - VALIDATION / BENCHMARK
  - IMPLICATION / OUTLOOK
- **A3. Quote the "Here we" pivot sentence verbatim** (the one that announces what the paper does).
- **A4. Quote the strongest quantitative claim** in the abstract.

## B. Introduction (first ~3–6 paragraphs)

- **B1. Opening hook style**: which of {field-importance statement, surprising fact / number, recent-advance recap, biological/physical motivation, technical paradox}. Quote sentence 1.
- **B2. Funnel structure**: in what paragraph does the topic narrow from broad → specific? Note ¶ count.
- **B3. Gap signaling phrases**: quote 2–3 phrases like "However,", "remains unclear", "limited by", "no general method exists".
- **B4. "Here we" pivot paragraph**: quote the first 2 sentences that introduce *this paper's* contribution.
- **B5. Contribution preview**: are contributions enumerated ("First… Second… Third…") or narrated? Quote the list/sentence.
- **B6. Last-paragraph-of-intro pattern**: does it preview results, list contributions, or state significance? Quote the last sentence.

## C. Results — section-level structure

- **C1. Number and titles of Results subsections.** Quote each header.
- **C2. Header style**: declarative finding ("Method X recovers Y"), neutral task ("Benchmarking on Z"), or question.
- **C3. For each Results subsection, quote the opening sentence.** Classify it as: claim-first, motivation-first, or method-first.
- **C4. Figure call-out phrasing**: quote 2 examples of how figures are introduced (e.g. "we found that … (Fig. 1a)", "Figure 1 shows …").
- **C5. Quantitative + statistical reporting style**: quote one passage that reports numbers + uncertainty + test (e.g. "AUC 0.92 ± 0.03, P < 1e-5, two-sided t-test, n=…").
- **C6. Baseline comparison phrasing**: quote one passage where the paper compares to prior method.
- **C7. Robustness/ablation framing**: quote one phrase like "We next asked whether …" / "To rule out …" / "As a control, …".
- **C8. Generalization framing**: quote a phrase that lifts a single result to a general claim.

## D. Discussion / Conclusion

- **D1. Opening sentence of Discussion**: restate finding, frame in field, or limitation-first? Quote.
- **D2. Limitation phrasing**: quote one limitation sentence.
- **D3. Outlook phrasing**: quote one "future work / will enable" sentence.
- **D4. Closing sentence of paper**: quote it.

## E. Methods (only if visible / accessible)

- **E1. Top-level methods subheadings**: list them.
- **E2. Reproducibility / data-availability sentence**: quote.

## F. Figures & captions

- **F1. Caption-title pattern**: are caption titles full declarative sentences ("X improves Y across Z") or noun phrases ("Overview of method")? Quote one.
- **F2. Panel-letter usage**: how many panels in main figures (typical), and how dense.

## G. Cross-cutting linguistic devices

- **G1. Hedging vocabulary** present: list which appear — "suggest", "indicate", "demonstrate", "establish", "consistent with", "we propose".
- **G2. Strong-claim verbs** present: "enable", "outperform", "achieve", "establish", "identify".
- **G3. Connectives between paragraphs**: quote 2 — e.g. "We next asked", "To test this", "Building on this", "Taken together".
- **G4. "Taken together / collectively / together these" usage**: quote if present.

## Output format per paper

```yaml
paper:
  cite: "First-author et al., Journal Year"
  url: "..."
  category: "methods | application | theory"
A1_title: "..."
A2_abstract_map:
  - {n: 1, role: "BIG-PICTURE", quote: "..."}
  - ...
A3_here_we: "..."
A4_strongest_quant: "..."
B1_hook_style: "..."
B1_quote: "..."
B3_gap_phrases: ["...", "...", "..."]
B4_pivot: "..."
B5_contribution: "..."
B6_last_intro: "..."
C1_headers: ["...", "..."]
C2_header_style: "..."
C3_openers: [{header: "...", quote: "...", class: "claim-first"}, ...]
C4_figcalls: ["...", "..."]
C5_quant: "..."
C6_baseline: "..."
C7_ablation: "..."
C8_generalization: "..."
D1_disc_open: "..."
D2_limitation: "..."
D3_outlook: "..."
D4_closing: "..."
E1_methods_subheads: ["..."]
F1_caption: "..."
G1_hedges_used: ["..."]
G2_strong_verbs_used: ["..."]
G3_connectives: ["...", "..."]
G4_taken_together: "..."
notable: "anything striking / unusual / template-worthy"
```

Keep quotes exact and ≤25 words; truncate with "…" if needed. Skip a field rather than guess.
