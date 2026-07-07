# Review Note: `<label>`

Copy this file to `docs/proof-review/appendix-notes/<target>.md` at the start of a review. Do not delete any section — if a section does not apply, write `N/A` and a one-line justification.

## Target

- Statement: <one-sentence plain-English summary>
- Label: `<label>`
- Statement lines: `<file>:<start>-<end>`
- Proof lines: `<file>:<start>-<end>`
- Files: `<file(s)>`
- Blueprint locked: `Y` / `N` (must match tracker)

## Assumption Ledger

- Explicit assumptions (from the statement):
  - ...
- Inherited section/setup assumptions:
  - ...
- Parameters treated as constants in this target:
  - ...
- Parameters still varying:
  - ...

## Dependency Ledger

- Local references imported (label, fragment of the statement actually used):
  - ...
- External references imported (must each link to an entry in `_external-lemmas.md`):
  - ...
- Dependencies still unchecked (tracker rows not yet closed):
  - ...

## Chunk Map

_(Must appear before any verdict. For blueprint-locked targets this must match `appendix-chunk-blueprints.md` exactly.)_

- `Chunk 1`: `<file>:<start>-<end>` — local goal: ...
- `Chunk 2`: ...
- ...

## Chunk 1

### Local goal

...

### Upstream deps used

_(List **tracker labels of other targets** — cross-target dependencies only — whose results this chunk's reasoning actually goes through. Write `none` if the chunk uses no result from another tracker row. Same-target chunk-to-chunk dependencies belong in the per-chunk checklist's "Imported results used in this chunk" line, not here. The linter uses this field to decide what to gate, so declare it honestly.)_

- `none`
- or: `prop:appendix-rate-smoothing`, `lem:appendix-rate-one-shot-kl`, ...

### Per-chunk checklist

- Local claim: ...
- Imported results used in this chunk: ...
- Hypotheses of those imports available here: ...
- Inequality direction check: ...
- Domain / positivity / measurability / integrability conditions needed: ...
- Expectation -> high-probability upgrade (if any): ...
- Edge case that could break this chunk: ...

### Step ledger

_(At least 3 entries unless genuinely trivial. Every `verified` entry needs all four fields.)_

- Step 1
  - Source lines: `<file>:<line>-<line>` or `<dependency-label>`
  - Inference type: `direct from text` / `algebra/calculation` / `standard theorem` / `conditioning/measurability` / `coupling` / `probability inequality` / `asymptotic comparison`
  - Why valid: <1-3 sentences that actually derive the inference, not a paraphrase>
  - Failure mode checked: <what could break, why it does not>
  - Status: `verified` / `plausible pending dependency` / `plausible but unverified` / `broken`
- Step 2
  - ...
- Step 3
  - ...

### Constant ledger

_(Any numerical constant introduced, fixed, or used as a downstream threshold in this chunk goes here. Parameters named in the proposition's statement — `R`, `d`, `tau`, etc. — do not count. For pure identity derivations with no constants, use the literal marker `N/A — no numerical constants in this chunk.` instead of an empty table.)_

| Symbol | Value / expression | Source | Downstream requirement | OK? |
| --- | --- | --- | --- | --- |
| ... | ... | ... | ... | ... |

### Chunk status

`verified` / `plausible pending dependency` / `plausible but unverified` / `broken`

---

## Chunk 2

_(repeat the same structure)_

---

## Mirror Diff

_(Only required if the proof says "similarly", "exactly as", "by the same argument as", or otherwise reuses another proof's structure. Otherwise write `N/A — not a mirror proof`.)_

- Mirrored source: `<label of earlier proof>`
- Differences that were re-checked:
  - ...: (re-checked: OK / issue — ledger pointer ...)
- Differences that were *not* re-checked (must be empty before closing): ...

## Pass A: Constructive Summary

- Fragile steps identified: ...
- Overall constructive verdict (before Pass B): ...

## Pass B: Adversarial Log

_(Must be produced in a fresh session whose loaded context is limited to: `appendix-review-protocol.md`, `appendix-review-tracker.md`, `appendix-chunk-blueprints.md`, `_external-lemmas.md`, and the raw source files. The Pass A ledger for this target must NOT be loaded until after the independent chunk map and dangerous-step list below are written. Operating in a single-session flow and just "pretending not to look" does not satisfy this rule.)_

- Fresh independent chunk map sketch:
  - ...
- Three most dangerous steps (independent guess):
  - ...
- Attacks attempted:
  - Endpoint / boundary regimes: ...
  - Quantifier drift: ...
  - Misuse of cited theorem: ...
  - Hidden regularity / measurability: ...
  - Wrong inequality direction: ...
  - Unsupported regime switch: ...
  - Constants chosen in the wrong order: ...
  - Fake mirror analogy: ...
- Pass B verdict: confirms / downgrades Pass A because ...

## Verdict

- Final tracker state: one of the states in `appendix-review-protocol.md`.
- Justification: ...
- Open blockers / next actions: ...

## Audit Trail

- Pass A session: <date, reviewer>
- Pass B session: <date, reviewer — must differ from Pass A context>
- Linter run: <command + result>
- External lemma entries touched: ...
