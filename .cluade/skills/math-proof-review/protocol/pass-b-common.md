# Common Pass B Protocol

This protocol applies to every Pass B (adversarial) invocation.

## Session Hygiene

- **Fresh context required.** Pass B must run in a context that has never seen Pass A reasoning for the same target. The preferred mechanism is a **subagent** spawned by the main agent — the subagent's context is mechanically isolated. If subagents are unavailable, use a separate Claude Code session.
- **Do NOT read the Pass A ledger** in the target's note until AFTER you have written your independent chunk map and dangerous-step list into `## Pass B: Adversarial Log`.
- Work on exactly one target per invocation (unless running Batch Mode).

## Files Allowed Before Writing

Load only:

- `protocol/review-protocol.md` (forcing rules)
- `docs/proof-review/appendix-review-tracker.md` (status and gate deps)
- `docs/proof-review/appendix-chunk-blueprints.md` (if applicable)
- `docs/proof-review/appendix-notes/_external-lemmas.md` (read-only)
- the raw TeX source files

You may open the target note only to find the `## Pass B: Adversarial Log` subsection as a write target. Do not scroll to Pass A content until your independent sketches are written.

## Step-By-Step

1. **Skim the raw proof.** Read the statement and proof body once, without reviewer notes.
2. **Write into `## Pass B: Adversarial Log`:**
   - a fresh, independent chunk-map sketch matching the required chunk count
   - your own list of the **three most dangerous steps**
   - an initial attack plan
3. **Attack.** For each category, write `Tried: ... / Result: {succeeded | partial | failed}`:
   - endpoint / boundary regimes
   - quantifier drift
   - misuse of a cited theorem
   - hidden regularity / measurability / integrability
   - wrong inequality direction
   - unsupported regime switch
   - constants chosen in the wrong order
   - fake mirror analogy
   - target-specific focus items (if provided)
4. **Cross-reference.** Only after the above is written, open Pass A and compare. Record disagreements.
5. **Run the linter.** Fix any failures in the Pass B subsection.
6. **Update `## Verdict`** to reflect the Pass B verdict.
7. **Update the tracker row.**

## Batch Mode

When running multiple targets in one session (for unattended execution):

1. Collect all non-closed targets from the tracker.
2. Process in dependency order (targets with all deps closed go first).
3. For each target:
   - State: "Beginning Pass B for `<label>`. Resetting reasoning about prior targets."
   - Do NOT read Pass A until independent sketches are written (this rule applies per-target even in batch).
   - Follow the common protocol above.
   - Update tracker before moving to the next target.
   - State: "Closing `<label>`. Next target: `<next>`."
4. Run Phase E sweep last.
5. Produce a single final summary.

## Verdict Rules

Choose:

- `closed: verified as written` — Pass B confirms Pass A, every chunk `verified`, all gate deps `closed: verified as written`, linter passes.
- `closed: claim likely true but proof incomplete` — claim seems correct but a real gap exists.
- `closed: serious gap` — substantive problem found.
- `closed: false/contradicted` — explicit counterexample.
- `plausible pending dependency` — only obstacle is an unclosed upstream.
- `needs second pass` — genuinely inconclusive (use sparingly).
