# Prompt Templates

Paste these directly into Claude Code. They assume the strict version of `protocol/review-protocol.md`.

## Bootstrap a Campaign

```text
Review all proofs in `<file>.tex`.

Scan for all theorem/lemma/proposition/corollary environments with \label{}.
Build a dependency graph, create a tracker, estimate chunk counts, and begin
Pass A on the first eligible target in dependency order.

Follow the math-proof-review skill protocol strictly.
```

## Review One Target — Pass A Only

```text
Review `<label>` in `<file>.tex` using the math-proof-review skill.

This is Pass A (constructive) ONLY. Do not close the target.

Requirements:
- Follow protocol/review-protocol.md strictly. Correctness-only.
- For every nontrivial verified step include Source lines, Inference type,
  Why valid, and Failure mode checked.
- Fill the constant ledger for every chunk.
- Record every external theorem in _external-lemmas.md verbatim.
- If the proof is mirrored, fill the Mirror Diff section line by line.
- Run lint-notes.py and fix everything.
- End at state `needs second pass`.
```

## Review One Target — Pass B Only (Fresh Session)

```text
Run Pass B (adversarial) on `<label>`.

This session must be fresh. Do NOT read the existing Pass A ledger until
after the steps below.

Requirements:
- Load only the protocol, tracker, blueprints, external lemmas, and raw TeX.
- Write into ## Pass B: Adversarial Log:
  1. a fresh, independent chunk-map sketch
  2. your own list of the three most dangerous steps
  3. the attacks you tried and whether each succeeded
- Only after those are written may you open the Pass A ledger.
- Run lint-notes.py before finalizing.
- Update the tracker row to the strongest justified state.
```

## Batch Pass B (Overnight)

```text
Run batch Pass B for all remaining targets in the tracker.

Process in dependency order. For each target:
- State "Beginning Pass B for <label>" before starting.
- Write independent chunk map and dangerous-step list BEFORE reading Pass A.
- Follow the common Pass B protocol.
- Update the tracker before moving to the next target.

After all targets: run the Phase E consistency sweep and write _appendix-summary.md.
Report a single summary at the end.
```

## Continue From The Tracker

```text
Continue the proof-review campaign from the tracker.

Work on exactly one target at a time in dependency order.
Default to Pass A only for any new target; stop at `needs second pass`.
Do not close a target whose gate dependencies are still open.
Run lint-notes.py before exiting.
```

## Final Consistency Sweep (Phase E)

```text
Run the campaign-wide consistency sweep.

Open the tracker and every note in docs/proof-review/appendix-notes/.
Follow the Phase E Consistency Sweep Checklist in review-protocol.md.
Each checklist item must produce an explicit entry in _appendix-summary.md.
Do not silently change verdicts. If a row needs weakening, update note and
tracker explicitly and flag in the summary.
```
