# Review Protocol

This protocol is the forcing layer for proof review. It is intentionally strict: the point is to *prevent* silent rubber-stamping, not to make the reviewer comfortable.

The correctness bar is publication-grade. A target is only `closed: verified as written` if every non-trivial inference has been re-derived by the reviewer, the constants have been checked, and the adversarial pass could not break it.

## Required Artifacts

For every target, create or update exactly one review note:

```text
docs/proof-review/appendix-notes/<target>.md
```

and update exactly one tracker row in:

```text
docs/proof-review/appendix-review-tracker.md
```

No proof review is complete unless both artifacts are updated.

Use `protocol/note-template.md` as the starting point. Do not invent your own layout.

For locked long proofs listed in `docs/proof-review/appendix-chunk-blueprints.md`, use the exact chunk boundaries and local goals from that file.

## Structural Lint Gate

Every note must pass:

```bash
python3 <skill-path>/scripts/lint-notes.py docs/proof-review/appendix-notes/<target>.md
```

before the tracker row may move past `in progress`. The linter enforces:

- presence of every mandatory section,
- at least one chunk subsection per required chunk,
- at least `3` four-field ledger items per `verified` chunk,
- `Why valid` fields of at least 30 characters,
- non-empty `### Constant ledger` (or explicit `N/A — no constants` marker) per chunk,
- `### Upstream deps used` declared per chunk,
- no chunk `verified` while any declared upstream dep is not `closed:` in the tracker,
- verdict regression: no `closed: verified as written` verdict while any tracker gate dep is not `closed: verified as written`,
- `## Mirror Diff` is non-`N/A` only if it contains `(re-checked: ...)` entries,
- `## Pass B: Adversarial Log` contains `independent chunk map` or `fresh chunk map` (enforced only for `closed: verified as written` verdicts),
- external theorem keywords (Bernstein / de Bruijn / Stam / Fubini / Markov / Pinsker / Fano / etc.) require `_external-lemmas` link.

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

`plausible pending dependency` is the maximum state a chunk or row may reach while its upstream dependency rows are still open.

## Mandatory Workflow

### 1. Claim The Target

- Mark exactly one tracker row `in progress`.
- Open the statement and proof span.
- Copy the note template into the target note.

### 2. Structural Pass

Identify the exact statement and proof span:

```bash
python3 <skill-path>/scripts/extract-proof-structure.py <file>.tex --label <label>
```

Full mechanical audit (once per campaign or after structural edits):

```bash
python3 <skill-path>/scripts/tex-proof-sanity.py <file1>.tex <file2>.tex --bib <bib>.bib
```

### 3. Make A Chunk Map Before Semantic Review

Rules for chunking:

- Split by logical moves, not equal line counts.
- Prefer paragraph boundaries, displayed equation clusters, and case splits.
- A chunk should have one local goal.
- Default maximum size is `25` proof lines per chunk.
- A chunk may exceed `25` lines only if a single displayed derivation or case split would otherwise be broken unnaturally; in that case it may not exceed `35` lines, and the note must justify the larger chunk.
- Do not reduce the required chunk count from the tracker.
- If the target has a locked blueprint, do not change chunk boundaries unless the note explains exactly why the blueprint fails.

## Per-Target Checklist

Every target note must answer:

- What is the exact statement being proved?
- What assumptions are explicit / inherited?
- Which local and external references are imported?
- Which dependencies have actually been checked?
- Which parameters are fixed constants and which still vary?
- Which norm/metric/probability object is being controlled at each step?
- Where could quantifiers, endpoint regimes, or asymptotic uniformity fail?
- What is the final verdict?

If the proof says "as above" / "similarly" / "exactly as in":

- Which earlier proof is being mirrored?
- Which lines are genuinely identical after renaming?
- Which lines changed because parameters, thresholds, tails, or regimes changed?
- Which mirrored steps were re-checked rather than inherited?

## Per-Chunk Checklist

Every chunk must answer:

- Local claim?
- Which previous results or assumptions used?
- Are all hypotheses of imported results available here?
- Is every displayed equality/inequality direction justified?
- Are domains, positivity, measurability, integrability conditions needed?
- Is any expectation bound being upgraded to high probability?
- Are constants and asymptotic dependencies preserved?
- Edge case that could break this chunk?
- Status: `verified` / `plausible pending dependency` / `plausible but unverified` / `broken`

## Anti-Hallucination Rule

For every nontrivial step marked `verified`, include all of:

- **Source lines**: exact line span or dependency label.
- **Inference type**: one of `direct from text`, `algebra/calculation`, `standard theorem`, `conditioning/measurability`, `coupling`, `probability inequality`, `asymptotic comparison`.
- **Why valid**: 1-3 sentences that actually *derive* the inference, not paraphrase the conclusion. The linter rejects entries under 30 characters.
- **Failure mode checked**: what could go wrong and why it does not.

If you cannot fill all four fields, the step is not `verified`.

Dangerous step types that must never be waved through:

- conditioning and "fix internal randomness" arguments
- transcript-coupling arguments
- "by Markov", "by Fubini", "by de Bruijn", "by Stam", "by Bernstein"
- switching from pointwise to average or from average to high probability
- asymptotic domination such as `<= C(...)`
- "exactly as in the previous proof" mirror steps

## Constant Ledger Rule

Every chunk must include a `### Constant ledger` subsection listing:

- every numerical constant introduced, fixed, or used as a downstream threshold,
- where it comes from,
- what downstream inequality needs it,
- whether that requirement is satisfied.

Free constants must be tracked end-to-end. A pure identity derivation may use:

```text
N/A — no numerical constants in this chunk.
```

## External Theorem Rule

Every external theorem used must have its statement recorded **verbatim** — with full hypotheses and exact constants — in `docs/proof-review/appendix-notes/_external-lemmas.md` before being cited in a `verified` step. The note must link to the relevant entry.

## Mirror Rule

When a proof reuses another proof's structure:

- The note must include a `## Mirror Diff` subsection.
- List the differences line by line: parameter renames, threshold values, regime splits, tail types.
- Every difference must carry `(re-checked: OK)` or `(re-checked: issue)`.
- A mirror step may not be marked `verified` until the Mirror Diff is complete.

## Two-Pass Requirement

### Pass A: Constructive

- Re-derive the proof step by step.
- Fill the full step ledger and constant ledger.
- Mark fragile or missing steps immediately.

### Pass B: Adversarial

- **Run in a fresh session.** Do not load the Pass A ledger before writing a fresh, independent chunk map and dangerous-step list.
- Actively try to break the argument: endpoint failures, quantifier drift, misuse of cited theorems, hidden regularity, wrong inequality direction, unsupported regime changes, constants in the wrong order, fake mirror analogies.
- Pass B leaves its own log in the note.

Do not mark the row closed after Pass A alone.

## Dependency Gate

Every chunk declares `### Upstream deps used` listing tracker labels of cross-target dependencies, or `none`.

- A chunk may be `verified` only if every declared dep is `closed:` in the tracker.
- A chunk with sound local reasoning but open deps is `plausible pending dependency`.
- A target may not be `closed: verified as written` while any tracker gate dep is open.
- A target may not be `closed: verified as written` while any tracker gate dep is weaker than `closed: verified as written` (verdict regression).

## Close Conditions

Use `closed: verified as written` only if:

- every mandatory section is present,
- every required chunk is present and `verified`,
- every nontrivial `verified` step has all four fields,
- every imported dependency is checked and its upstream row is `closed: verified as written`,
- every external theorem has a verbatim entry in `_external-lemmas.md`,
- every mirror step has a complete Mirror Diff entry,
- every constant is tracked and consistent end-to-end,
- the linter passes,
- Pass B has run in a fresh session and left its log,
- Pass B found no unresolved issue.

Otherwise choose a weaker close state.

## Phase E Consistency Sweep Checklist

The final sweep must produce explicit findings for each of:

- **Dependency edge audit**: for every upstream->downstream edge, confirm the upstream statement matches how the downstream uses it.
- **Hypothesis matching**: every hypothesis of an upstream result is established before citation.
- **Constant propagation**: free constants that flow across targets are compatible.
- **Symbol consistency**: key symbols have the same meaning everywhere.
- **Mirror sanity**: every Mirror Diff is complete and no `(re-checked: issue)` is unresolved.
- **Unclosed blockers**: list every target still at `plausible pending dependency`.
- **Verdict regression check**: no downstream is closed more strongly than its upstream.
