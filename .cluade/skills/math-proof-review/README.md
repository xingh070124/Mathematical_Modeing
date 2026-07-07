# math-proof-review

A Claude Code skill for rigorous correctness audits of mathematical proofs in LaTeX papers.

## Quick Start

```bash
cd your-paper/
git clone https://github.com/XunZhiyang/math-proof-review .claude/skills/math-proof-review
```

Then open Claude Code and say:

```
Review all proofs in this paper
```

The agent will find all `.tex` files, scan for theorem/lemma/proposition environments, build a dependency-ordered tracker, and begin a two-pass review campaign.

## What It Does

For each proof-bearing target (theorem, lemma, proposition, corollary):

1. **Pass A (constructive)**: re-derives the proof step by step with a four-field step ledger (`Source lines`, `Inference type`, `Why valid`, `Failure mode checked`) and constant ledger per chunk.
2. **Pass B (adversarial)**: independently sketches the chunk map and dangerous steps, then systematically attacks endpoints, quantifiers, cited theorem hypotheses, hidden regularity, inequality directions, constant ordering, and mirror analogies.
3. **Dependency gate**: no target closes before its upstream dependencies.
4. **Phase E sweep**: audits dependency edges, hypothesis matching, constant propagation, and symbol consistency across the entire campaign.

## Structure

```
math-proof-review/
├── SKILL.md                         # Auto-discovered by Claude Code
├── protocol/
│   ├── review-protocol.md           # Forcing layer (status machine, checklists, rules)
│   ├── note-template.md             # Mandatory note layout
│   ├── prompt-templates.md          # Copy-paste prompts for Pass A/B/E
│   └── pass-b-common.md             # Common adversarial protocol
├── scripts/
│   ├── lint-notes.py                # Structural safety net
│   ├── extract-proof-structure.py   # Extract theorem/proof blocks from TeX
│   └── tex-proof-sanity.py          # Mechanical audit (refs, cites, labels)
└── examples/
    └── example-note.md              # A completed 7-chunk review note for reference
```

## What the Agent Creates in Your Repo

```
your-paper/
├── docs/proof-review/
│   ├── appendix-review-tracker.md   # One row per target
│   ├── appendix-chunk-blueprints.md # Locked boundaries for long proofs
│   └── appendix-notes/
│       ├── _external-lemmas.md      # Verbatim external theorem entries
│       ├── _appendix-summary.md     # Phase E sweep output
│       ├── lem-foo.md               # Review note per target
│       └── ...
```

## Requirements

- Claude Code (CLI, desktop, or IDE extension)
- Python 3.9+ (for the linter and TeX scripts)
- A LaTeX paper with `\begin{theorem}...\end{theorem}` style environments

## License

MIT
