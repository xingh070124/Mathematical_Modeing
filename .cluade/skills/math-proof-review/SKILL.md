---
name: math-proof-review
description: >
  Rigorous correctness audit for mathematical proofs in LaTeX papers.
  Use when the user asks to review, audit, or verify a theorem, lemma,
  proposition, corollary, or derivation in a .tex file.
---

# Math Proof Review

Review proofs as if the goal is to break them, not paraphrase them. Re-derive each nontrivial step from stated assumptions and cited results. Keep a sharp distinction between `verified`, `plausible but unverified`, and `broken`.

## How It Works

This skill runs a two-pass, dependency-gated campaign over every proof-bearing target in a LaTeX paper.

- **Pass A (constructive)**: re-derive the proof step by step, filling a four-field step ledger and constant ledger for every chunk.
- **Pass B (adversarial)**: run as a **subagent** (isolated context), independently sketch the chunk map and dangerous steps, then systematically attack the proof. Only after writing the attack log may it consult Pass A.
- **Phase E (consistency sweep)**: after all targets close, audit dependency edges, hypothesis matching, constant propagation, symbol consistency, and mirror diffs across the entire campaign.

## Two-Pass Execution Model

Pass B **must** run in isolated context to prevent confirmation bias from Pass A. The agent achieves this automatically by spawning a subagent:

### Per-target workflow

```
┌─────────────────────────────────────────────────────────┐
│ Main agent (Pass A)                                     │
│  1. Claim target, build chunk map                       │
│  2. Constructive re-derivation → step ledger            │
│  3. Fill constant ledger, mark `needs second pass`      │
│  4. Spawn subagent for Pass B ───────────────────────┐  │
│  5. Read subagent result, update verdict + tracker   │  │
└──────────────────────────────────────────────────────┼──┘
                                                       │
┌──────────────────────────────────────────────────────▼──┐
│ Subagent (Pass B) — fresh context, no Pass A loaded     │
│  Allowed to read:                                       │
│   - protocol/review-protocol.md                         │
│   - docs/proof-review/appendix-review-tracker.md        │
│   - docs/proof-review/appendix-chunk-blueprints.md      │
│   - docs/proof-review/appendix-notes/_external-lemmas.md│
│   - raw TeX source files                                │
│  Must NOT read: the target note's Pass A ledger         │
│                                                         │
│  Steps:                                                 │
│   1. Read raw proof from TeX                            │
│   2. Write independent chunk-map sketch                 │
│   3. Write 3 most dangerous steps                      │
│   4. Run all attack categories                          │
│   5. THEN open Pass A, cross-reference                  │
│   6. Write verdict into ## Pass B: Adversarial Log      │
│   7. Run lint-notes.py                                  │
└─────────────────────────────────────────────────────────┘
```

### Subagent prompt template

The main agent should spawn the Pass B subagent with a prompt like:

```
Run Pass B (adversarial) on `<label>` in `<file>.tex`.

You are a fresh reviewer. You have NOT seen any prior analysis of this proof.

Protocol: read protocol/review-protocol.md and protocol/pass-b-common.md.

Your job:
1. Read the raw proof at <file>.tex:<start>-<end>.
2. Write into docs/proof-review/appendix-notes/<target>.md section "## Pass B: Adversarial Log":
   - Independent chunk-map sketch (do NOT open any other section of this note first)
   - Your 3 most dangerous steps
   - Attack log (endpoint, quantifier, cited theorem, regularity, direction, regime, constants, mirror)
3. ONLY AFTER writing the above, read the rest of the note and cross-reference with Pass A.
4. Write your Pass B verdict.
5. Run: python3 <skill-path>/scripts/lint-notes.py docs/proof-review/appendix-notes/<target>.md

Report: final verdict and any issues found.
```

The subagent's isolated context guarantees it cannot be influenced by Pass A reasoning in the parent agent's memory. This is stronger than the "fresh session" rule — it is mechanically enforced, not honor-system.

### Parallelization

Multiple Pass B subagents can run in parallel on independent targets (targets with no dependency edge between them). The main agent should:

1. Identify independent targets from the dependency graph.
2. Spawn multiple Pass B subagents simultaneously.
3. Collect results and update tracker/verdicts.

For dependent targets, run sequentially in topological order.

## Campaign Bootstrap

When the user says "review all proofs" or similar, the agent should:

1. **Find all `.tex` files** in the repository and **scan** them for all theorem-like environments with `\label{}`. Standard environments (`theorem`, `lemma`, `proposition`, `corollary`, `claim`, etc.) are recognized automatically; custom environments defined via `\newtheorem{}` are also auto-discovered.
2. **Build a dependency graph** by tracing `\ref{}` citations within proofs back to other labeled targets.
3. **Create the campaign directory** at `docs/proof-review/` with:
   - `appendix-review-tracker.md` — one row per target (label, proof lines, estimated chunks, gate deps, status `not started`)
   - `appendix-notes/` directory for review notes
   - `appendix-notes/_external-lemmas.md` — empty, to be filled as external theorems are encountered
   - Copy `protocol/note-template.md` into the campaign directory
4. **Estimate required chunks** per target: `max(1, ceil(proof_lines / 25))`.
5. **For long proofs (>= 5 chunks)**: create `appendix-chunk-blueprints.md` with locked chunk boundaries chosen by logical moves, not equal line counts.
6. **Determine phase ordering** from the dependency graph (leaves first, then dependents).
7. **Begin Pass A** on the first eligible target.

If the user instead says "review `<label>`" for a single target, skip the full bootstrap — just set up that one target's tracker row and note.

## Required Artifacts Per Target

For every reviewed target, update exactly two persistent artifacts:

1. **One review note** in `docs/proof-review/appendix-notes/<target>.md`, built from `protocol/note-template.md`.
2. **One tracker row** in `docs/proof-review/appendix-review-tracker.md`.

A target review is not complete unless both are updated and `lint-notes.py` passes on the note.

## Protocol Files

All review rules live in `protocol/`:

| File | Purpose |
|---|---|
| `protocol/review-protocol.md` | The forcing layer: status machine, mandatory workflow, per-target and per-chunk checklists, anti-hallucination rule, constant ledger rule, external theorem rule, mirror rule, two-pass requirement, dependency gate, close conditions, Phase E checklist |
| `protocol/note-template.md` | The only acceptable note layout |
| `protocol/prompt-templates.md` | Copy-paste prompts for Pass A, Pass B, batch mode, Phase E |
| `protocol/pass-b-common.md` | Common Pass B protocol (session hygiene, allowed files, attack categories) |

**Read `protocol/review-protocol.md` before any semantic judgment.** It is the forcing layer — intentionally strict to prevent silent rubber-stamping.

## Scripts

| Script | Purpose |
|---|---|
| `scripts/lint-notes.py` | Structural safety net — enforces mandatory sections, chunk count, four-field ledger, constant ledger, upstream deps, Pass B phrase, external theorem linking, verdict regression |
| `scripts/extract-proof-structure.py` | Extract theorem/proof blocks with line numbers from any TeX file |
| `scripts/tex-proof-sanity.py` | Mechanical audit: duplicate labels, undefined refs/cites, environment mismatches |

Run `lint-notes.py` on every note before moving its tracker row past `in progress`. Run `tex-proof-sanity.py` once at campaign start and after structural TeX edits.

## Non-Negotiables

- No `verified` verdict without a step ledger.
- No step marked `verified` without all four fields: `Source lines`, `Inference type`, `Why valid` (>= 30 chars, must derive, not paraphrase), `Failure mode checked`.
- No target closed without both Pass A and Pass B.
- No target closed more strongly than its weakest upstream dependency (verdict regression).
- No external theorem cited without a verbatim entry in `_external-lemmas.md`.
- No mirror step marked `verified` without a complete `## Mirror Diff`.

## Status Machine

Use only these tracker states:

- `not started`
- `in progress`
- `blocked on dependency`
- `plausible pending dependency`
- `needs second pass`
- `closed: verified as written`
- `closed: claim likely true but proof incomplete`
- `closed: serious gap`
- `closed: false/contradicted`

## Tracker Format

```markdown
| Target | Proof lines | Required chunks | Blueprint | Note file | Gate deps | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `lem:foo` | `file.tex:100-150` | `3` | `N` | `docs/proof-review/appendix-notes/lem-foo.md` | `none` | `not started` |
```

## Campaign End: Deliverables to the User

After Phase E completes, the agent must present a **final report** containing:

1. **Scorecard**: `N/N targets closed: verified as written`, with any weaker verdicts listed explicitly.
2. **Issue list**, grouped by severity:

### Severity levels

| Level | Meaning | User action |
|---|---|---|
| **S0: false/contradicted** | The claim is wrong or a counterexample exists | Retract or re-state the theorem. Agent provides the counterexample or identifies the false step. |
| **S1: serious gap** | A critical step is unsupported and blocks the theorem as stated | Must supply a new argument. Agent describes exactly what is missing, what it would need to establish, and (if possible) sketches a repair strategy. |
| **S2: proof incomplete** | Claim is likely true but written proof has a hole | Must add the missing argument. Agent identifies the gap, explains why the claim likely survives, and suggests the simplest patch. |
| **S3: missing hypothesis** | Statement lacks an assumption that the proof uses | Add the hypothesis to the statement. Agent gives the exact TeX patch and confirms all call sites already satisfy it. |
| **S4: exposition only** | No correctness issue, but a one-line remark would help | Optional. Agent notes it but does not block closure. |

### Per-issue format

Each issue in the report must include:

```
## Issue #N — [S0/S1/S2/S3/S4]: one-line title

- **Target**: `<label>`
- **Location**: `<file>:<lines>`
- **What's wrong**: <1-3 sentences: the specific step/claim that fails>
- **Evidence**: <the attack that found it, or the counterexample>
- **Impact**: <which downstream targets are blocked>
- **Suggested fix**: <exact TeX patch if S3/S4, or repair strategy if S1/S2>
- **Confidence**: <how sure the agent is that the claim itself is true/false>
- **What the user needs to decide**: <if the fix isn't mechanical, what judgment call remains>
```

For S0/S1 issues, the agent should also state:
- whether the main theorem (the paper's headline result) is affected
- whether a simple fix exists or the proof strategy needs rethinking
- what the minimum viable patch would be (even if ugly)

### After the user addresses issues

- **S3/S4 fixes** (mechanical): agent verifies the patch, promotes rows, done.
- **S2 fixes** (new argument added): agent re-runs Pass A on the patched proof chunk, then a targeted Pass B subagent on that chunk only. If it passes, promotes.
- **S1 fixes** (substantial new proof): agent runs full Pass A + Pass B on the rewritten target from scratch.
- **S0** (retraction/restatement): agent re-evaluates all downstream targets that depended on the old claim.

3. **Verdict after fixes**: state what the tracker will look like once the user applies the fixes.

## Default Communication

Keep user-facing summaries concise. Focus on: findings, what was verified, what remains blocked or unverified.
