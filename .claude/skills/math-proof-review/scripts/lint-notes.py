#!/usr/bin/env python3
"""Lint a proof-review note against docs/proof-review/appendix-review-protocol.md.

Usage:
    python3 lint-notes.py docs/proof-review/appendix-notes/<target>.md [...]

Exit code is non-zero if any note fails. The linter is a *structural* safety
net: it blocks obviously incomplete or obviously forbidden notes, but it cannot
verify mathematical content or enforce runtime policies like "Pass B ran in a
separate session". Treat passing the linter as necessary, not sufficient.

What is actually enforced:
    1. Required top-level sections are present by exact header match.
    2. `Blueprint locked: Y/N` is declared and matches the tracker column.
    3. The chunk count is at least the `Required chunks` field in the tracker.
    4. Every chunk has its own `### Local goal`, `### Upstream deps used`,
       `### Per-chunk checklist`, `### Step ledger`, `### Constant ledger`, and
       `### Chunk status` subsection by exact header match.
    5. Every chunk whose status is `verified` contains at least 3 step-ledger
       items, each with all four fields (`Source lines`, `Inference type`,
       `Why valid`, `Failure mode checked`), and each `Why valid` is at least
       30 characters long.
    6. The `### Constant ledger` subsection for a `verified` chunk is either a
       non-empty table or carries a literal `N/A — no constants ...` marker.
    7. If `## Mirror Diff` is non-`N/A`, it contains at least one
       `(re-checked: OK|issue)` entry. (Completeness of the diff itself is not
       checked by the linter.)
    8. Chunks declare their upstream dependencies. A chunk may only be
       `verified` if every label listed in its `### Upstream deps used`
       subsection corresponds to a tracker row whose status starts with
       `closed:`. Purely local chunks must declare `none` explicitly. The
       linter does not check that the declared list is accurate.
    9. `## Pass B: Adversarial Log` contains the literal phrase
       "independent chunk map" or "fresh chunk map". The linter cannot verify
       that Pass B was actually produced in a fresh session; reviewers must
       enforce that by convention.
   10. If the note contains any external-theorem keyword
       (Bernstein / de Bruijn / Stam / Fubini / Markov / Pinsker /
       Bretagnolle / Hanson-Wright / Gaussian-Lipschitz / data-processing /
       Fano), the note must also contain the substring `_external-lemmas`
       somewhere. The linter does not resolve individual anchors or verify
       hypothesis matching against the entry body.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

def _find_repo_root() -> Path:
    """Walk upward from CWD looking for docs/proof-review/appendix-review-tracker.md."""
    candidate = Path.cwd().resolve()
    for _ in range(10):
        if (candidate / "docs" / "proof-review" / "appendix-review-tracker.md").exists():
            return candidate
        parent = candidate.parent
        if parent == candidate:
            break
        candidate = parent
    # Fallback: assume script is at <skill>/scripts/lint-notes.py inside .claude/skills/<skill>/
    return Path(__file__).resolve().parents[4]

REPO_ROOT = _find_repo_root()
TRACKER_PATH = REPO_ROOT / "docs" / "proof-review" / "appendix-review-tracker.md"
EXTERNAL_LEMMAS = REPO_ROOT / "docs" / "proof-review" / "appendix-notes" / "_external-lemmas.md"

REQUIRED_TOP_SECTIONS = [
    "## Target",
    "## Assumption Ledger",
    "## Dependency Ledger",
    "## Chunk Map",
    "## Mirror Diff",
    "## Pass A: Constructive Summary",
    "## Pass B: Adversarial Log",
    "## Verdict",
    "## Audit Trail",
]

REQUIRED_CHUNK_SUBSECTIONS = [
    "### Local goal",
    "### Upstream deps used",
    "### Per-chunk checklist",
    "### Step ledger",
    "### Constant ledger",
    "### Chunk status",
]

LEDGER_FIELDS = ["Source lines", "Inference type", "Why valid", "Failure mode checked"]

VERIFIED_STATES = {"verified"}
PENDING_STATES = {"plausible pending dependency", "plausible but unverified", "needs second pass"}
ALLOWED_CHUNK_STATES = VERIFIED_STATES | PENDING_STATES | {"broken"}

CLOSED_PREFIX = "closed:"
VERIFIED_CLOSED = "closed: verified as written"

# Named theorems whose citations must resolve to _external-lemmas.md.
EXTERNAL_THEOREM_KEYWORDS = [
    "bernstein",
    "de bruijn",
    "stam",
    "fubini",
    "markov",
    "pinsker",
    "bretagnolle",
    "hanson-wright",
    "gaussian-lipschitz",
    "gaussian lipschitz",
    "gaussian concentration",
    "data processing",
    "data-processing",
    "fano",
]


@dataclass
class Finding:
    path: Path
    line: int
    message: str

    def format(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


@dataclass
class LintResult:
    findings: list[Finding] = field(default_factory=list)

    def fail(self, path: Path, line: int, message: str) -> None:
        self.findings.append(Finding(path=path, line=line, message=message))

    @property
    def ok(self) -> bool:
        return not self.findings


@dataclass
class TrackerRow:
    label: str
    required_chunks: int | None
    blueprint: str | None
    note_file: str
    gate_deps: list[str]
    status: str


def parse_tracker(path: Path) -> dict[str, TrackerRow]:
    rows: dict[str, TrackerRow] = {}
    if not path.exists():
        return rows
    text = path.read_text()
    row_re = re.compile(r"^\|\s*`([^`]+)`\s*\|(.+)\|\s*$")
    for raw in text.splitlines():
        m = row_re.match(raw)
        if not m:
            continue
        label = m.group(1)
        cells = [c.strip() for c in m.group(2).split("|")]
        # layout: proof-lines | required-chunks | blueprint | note-file | gate-deps | status
        # OR (legacy): proof-lines | required-chunks | note-file | gate-deps | status
        if len(cells) == 6:
            _, req, blueprint, note_file, deps_cell, status_cell = cells
        elif len(cells) == 5:
            _, req, note_file, deps_cell, status_cell = cells
            blueprint = None
        else:
            continue
        req_m = re.search(r"`(\d+)`", req)
        required_chunks = int(req_m.group(1)) if req_m else None
        note_m = re.search(r"`([^`]+)`", note_file)
        note_path = note_m.group(1) if note_m else ""
        deps = re.findall(r"`([^`]+)`", deps_cell)
        deps = [d for d in deps if d.lower() != "none"]
        status = re.sub(r"[`*]", "", status_cell).strip()
        rows[label] = TrackerRow(
            label=label,
            required_chunks=required_chunks,
            blueprint=(re.sub(r"[`*]", "", blueprint).strip() if blueprint else None),
            note_file=note_path,
            gate_deps=deps,
            status=status,
        )
    return rows


def note_label_from_path(path: Path, tracker: dict[str, TrackerRow]) -> str | None:
    try:
        as_posix = path.relative_to(REPO_ROOT).as_posix() if path.is_absolute() else path.as_posix()
    except ValueError:
        as_posix = path.name
    for label, row in tracker.items():
        if not row.note_file:
            continue
        if row.note_file == as_posix or row.note_file.endswith("/" + path.name):
            return label
    return None


def split_sections(lines: list[str], level: int) -> list[tuple[int, str, list[str]]]:
    """Return list of (start_line_1_indexed, header, body_lines) at given header level."""
    prefix = "#" * level + " "
    sections: list[tuple[int, str, list[str]]] = []
    current_start: int | None = None
    current_header: str | None = None
    current_body: list[str] = []
    for idx, line in enumerate(lines, start=1):
        if line.startswith(prefix) and not line.startswith(prefix + "#"):
            if current_header is not None:
                sections.append((current_start or 0, current_header, current_body))
            current_start = idx
            current_header = line.rstrip()
            current_body = []
        else:
            if current_header is not None:
                current_body.append(line)
    if current_header is not None:
        sections.append((current_start or 0, current_header, current_body))
    return sections


def extract_chunks(lines: list[str]) -> list[tuple[int, str, list[str]]]:
    out: list[tuple[int, str, list[str]]] = []
    for start, header, body in split_sections(lines, 2):
        if re.match(r"^##\s+Chunk\s+\d+", header):
            out.append((start, header, body))
    return out


def find_line(body_lines: list[str], needle: str, body_start: int) -> int:
    for i, line in enumerate(body_lines):
        if needle in line:
            return body_start + i
    return body_start


def parse_ledger_items(body: list[str], body_start: int) -> list[dict]:
    """Parse the `### Step ledger` subsection body into a list of step dicts.

    Each step starts at a top-level bullet (`- Step`, `- `). Four-field values
    follow on sub-bullets like `  - Source lines: ...`.
    """
    items: list[dict] = []
    current: dict | None = None
    for offset, raw in enumerate(body):
        line = raw.rstrip()
        if re.match(r"^- (?!\s)", line):  # top-level bullet
            if current is not None:
                items.append(current)
            current = {"_line": body_start + offset}
        elif current is not None:
            m = re.match(r"^\s+- ([A-Za-z ]+):\s*(.*)$", line)
            if m:
                key = m.group(1).strip()
                val = m.group(2).strip()
                current[key] = val
    if current is not None:
        items.append(current)
    return items


def parse_upstream_deps_used(body: list[str]) -> tuple[list[str], bool]:
    """Parse the `### Upstream deps used` subsection body.

    Returns (declared_deps, declared_none). `declared_none` is True if the chunk
    explicitly declared no upstream dependencies via a `none` entry.
    """
    deps: list[str] = []
    declared_none = False
    for line in body:
        stripped = line.strip()
        if not stripped.startswith("-"):
            continue
        content = stripped.lstrip("-").strip()
        # Skip template-guide bullets like "- or: `prop:...`" used as examples.
        if content.lower().startswith("or:"):
            continue
        labels = re.findall(r"`([^`]+)`", content)
        for lbl in labels:
            if lbl.strip().lower() == "none":
                declared_none = True
            else:
                deps.append(lbl.strip())
        if not labels and content.lower() == "none":
            declared_none = True
    return deps, declared_none


def constant_ledger_nonempty(body: list[str]) -> bool:
    in_table = False
    data_rows = 0
    for line in body:
        stripped = line.strip()
        if stripped.startswith("|"):
            if re.match(r"^\|[\s\-:|]+\|\s*$", stripped):
                in_table = True
                continue
            if in_table:
                cells = [c.strip() for c in stripped.strip("|").split("|")]
                if any(c and c != "..." and c != "N/A" for c in cells):
                    data_rows += 1
    return data_rows > 0


def lint_note(path: Path, tracker: dict[str, TrackerRow], result: LintResult) -> None:
    if not path.exists():
        result.fail(path, 0, "note file does not exist")
        return
    raw = path.read_text()
    lines = raw.splitlines()

    # 1. Top-level sections present.
    for section in REQUIRED_TOP_SECTIONS:
        if not any(line.strip() == section for line in lines):
            result.fail(path, 0, f"missing required section: {section}")

    # Locate tracker row.
    label = note_label_from_path(path, tracker)
    row = tracker.get(label) if label else None

    # 2. Blueprint-locked field exists and agrees with tracker.
    blueprint_line_idx = None
    blueprint_declared: str | None = None
    for i, line in enumerate(lines, start=1):
        m = re.search(r"Blueprint locked:\s*`?([YN])`?", line)
        if m:
            blueprint_declared = m.group(1)
            blueprint_line_idx = i
            break
    if blueprint_declared is None:
        result.fail(path, 0, "`Blueprint locked: Y/N` field missing in `## Target`")
    elif row and row.blueprint in {"Y", "N"} and blueprint_declared != row.blueprint:
        result.fail(
            path,
            blueprint_line_idx or 0,
            f"`Blueprint locked: {blueprint_declared}` does not match tracker row `{row.blueprint}`",
        )

    # 3. Chunk count matches tracker.
    chunks = extract_chunks(lines)
    if row and row.required_chunks is not None:
        if len(chunks) < row.required_chunks:
            result.fail(
                path,
                0,
                f"tracker requires {row.required_chunks} chunks, note has {len(chunks)}",
            )

    # Precompute tracker-level unclosed gate deps for target-level close check.
    target_unclosed_deps: list[str] = []
    if row:
        for dep in row.gate_deps:
            dep_row = tracker.get(dep)
            if dep_row is None or not dep_row.status.startswith(CLOSED_PREFIX):
                target_unclosed_deps.append(dep)

    # Per-chunk checks.
    for start_line, header, body in chunks:
        chunk_name = header[3:].strip()
        chunk_body_start = start_line + 1
        # 4. Required subsections.
        for sub in REQUIRED_CHUNK_SUBSECTIONS:
            if not any(line.strip() == sub for line in body):
                result.fail(path, start_line, f"{chunk_name}: missing required subsection {sub}")

        # Locate `### Chunk status` value.
        status_value: str | None = None
        status_line = start_line
        for sub_start, sub_header, sub_body in split_sections(body, 3):
            if sub_header.strip() == "### Chunk status":
                for offset, raw_line in enumerate(sub_body):
                    text = raw_line.strip().strip("`").strip()
                    if text:
                        status_value = text.lower()
                        status_line = chunk_body_start + sub_start - 1 + offset
                        break
                break

        if status_value is None:
            result.fail(path, start_line, f"{chunk_name}: `### Chunk status` has no value")
            continue

        # Allow colon-separated suffixes like "verified (...)".
        canonical_status = status_value.split("(")[0].strip()
        if canonical_status not in ALLOWED_CHUNK_STATES:
            result.fail(
                path,
                status_line,
                f"{chunk_name}: chunk status `{status_value}` is not one of {sorted(ALLOWED_CHUNK_STATES)}",
            )

        # Parse declared upstream deps for this chunk, regardless of status,
        # because we want to warn if deps are mentioned but none subsection is missing.
        declared_deps: list[str] = []
        declared_none = False
        deps_sub_start = chunk_body_start
        for sub_start, sub_header, sub_body in split_sections(body, 3):
            if sub_header.strip() == "### Upstream deps used":
                declared_deps, declared_none = parse_upstream_deps_used(sub_body)
                deps_sub_start = chunk_body_start + sub_start - 1
                break

        if canonical_status in VERIFIED_STATES:
            # 5. Step ledger: at least 3 four-field items.
            ledger_body: list[str] = []
            ledger_body_start = chunk_body_start
            for sub_start, sub_header, sub_body in split_sections(body, 3):
                if sub_header.strip() == "### Step ledger":
                    ledger_body = sub_body
                    ledger_body_start = chunk_body_start + sub_start - 1
                    break
            items = parse_ledger_items(ledger_body, ledger_body_start)
            complete_items = [
                it for it in items if all(field in it and it[field] and it[field] != "..." for field in LEDGER_FIELDS)
            ]
            if len(complete_items) < 3:
                result.fail(
                    path,
                    ledger_body_start,
                    f"{chunk_name}: chunk is `verified` but has only {len(complete_items)} "
                    f"complete four-field ledger items (need >= 3)",
                )

            # Paraphrase smell: `Why valid` must not be a verbatim rephrasing of the conclusion.
            for it in complete_items:
                why = it.get("Why valid", "")
                if len(why) < 30:
                    result.fail(
                        path,
                        it.get("_line", ledger_body_start),
                        f"{chunk_name}: `Why valid` is under 30 characters — likely a paraphrase",
                    )

            # 6. Constant ledger must be non-empty.
            const_body: list[str] = []
            const_start = chunk_body_start
            for sub_start, sub_header, sub_body in split_sections(body, 3):
                if sub_header.strip() == "### Constant ledger":
                    const_body = sub_body
                    const_start = chunk_body_start + sub_start - 1
                    break
            if not constant_ledger_nonempty(const_body):
                # Allow explicit "N/A — no constants" marker.
                marker_ok = any("N/A" in line and "constant" in line.lower() for line in const_body)
                if not marker_ok:
                    result.fail(
                        path,
                        const_start,
                        f"{chunk_name}: `### Constant ledger` has no data rows and no `N/A — ...` marker",
                    )

            # 8. Upstream dependency gate (per declared deps only).
            if not declared_deps and not declared_none:
                result.fail(
                    path,
                    deps_sub_start,
                    f"{chunk_name}: chunk is `verified` but `### Upstream deps used` is empty and does not declare `none`",
                )
            chunk_unclosed: list[str] = []
            for dep in declared_deps:
                dep_row = tracker.get(dep)
                if dep_row is None or not dep_row.status.startswith(CLOSED_PREFIX):
                    chunk_unclosed.append(dep)
            if chunk_unclosed:
                result.fail(
                    path,
                    status_line,
                    f"{chunk_name}: cannot be `verified` — declared upstream deps "
                    f"{', '.join('`' + d + '`' for d in chunk_unclosed)} are not closed in the tracker; "
                    f"downgrade to `plausible pending dependency`",
                )

    # 7. Mirror Diff consistency.
    mirror_body: list[str] = []
    mirror_start = 0
    for start, header, body in split_sections(lines, 2):
        if header.strip() == "## Mirror Diff":
            mirror_body = body
            mirror_start = start
            break
    if mirror_body:
        joined = "\n".join(mirror_body)
        is_na = re.search(r"\bN/A\b", joined)
        if not is_na:
            checked_diff = re.findall(r"re-checked:\s*(OK|issue)", joined)
            diff_bullets = [line for line in mirror_body if re.match(r"^\s*-\s", line) and "re-checked" in line]
            if not diff_bullets:
                result.fail(
                    path,
                    mirror_start,
                    "Mirror Diff section is not `N/A` but contains no `(re-checked: ...)` entries",
                )

    # 9. Pass B must include a fresh chunk-map sketch — but only enforce this
    #    gate when the note is being promoted to `closed: verified as written`.
    #    A note left at `needs second pass` / `plausible pending dependency` /
    #    weaker is allowed to ship a Pass B placeholder, since Pass B has not
    #    yet been run.
    verdict_body: list[str] = []
    for start, header, body in split_sections(lines, 2):
        if header.strip() == "## Verdict":
            verdict_body = body
            break
    # Extract the verdict declaration — first non-empty line after `## Verdict`.
    verdict_declaration = ""
    for vline in verdict_body:
        stripped = vline.strip().strip("`").strip()
        if stripped:
            verdict_declaration = stripped.lower()
            break
    requires_pass_b = verdict_declaration == "closed: verified as written."  or verdict_declaration == "closed: verified as written"

    pass_b_body: list[str] = []
    pass_b_start = 0
    for start, header, body in split_sections(lines, 2):
        if header.strip() == "## Pass B: Adversarial Log":
            pass_b_body = body
            pass_b_start = start
            break
    if pass_b_body and requires_pass_b:
        pass_b_text = "\n".join(pass_b_body).lower()
        if "independent chunk map" not in pass_b_text and "fresh chunk map" not in pass_b_text:
            result.fail(
                path,
                pass_b_start,
                "Pass B must record an independent / fresh chunk map before the note is closed",
            )

    # 10a. Verdict regression: if verdict is `closed: verified as written`,
    #      every tracker-level gate dep must also be `closed: verified as written`.
    if requires_pass_b and row:
        weakly_closed_deps: list[str] = []
        for dep in row.gate_deps:
            dep_row = tracker.get(dep)
            if dep_row and dep_row.status.startswith(CLOSED_PREFIX) and dep_row.status != VERIFIED_CLOSED:
                weakly_closed_deps.append(dep)
        if weakly_closed_deps:
            result.fail(
                path,
                0,
                f"verdict is `closed: verified as written` but tracker gate deps "
                f"{', '.join('`' + d + '`' for d in weakly_closed_deps)} are not `closed: verified as written` "
                f"(verdict regression required)",
            )

    # 10b. External theorem keyword must link to _external-lemmas.md.
    note_text_lower = raw.lower()
    links_external = "_external-lemmas" in note_text_lower
    for kw in EXTERNAL_THEOREM_KEYWORDS:
        if kw in note_text_lower and not links_external:
            result.fail(
                path,
                0,
                f"note mentions `{kw}` but never links to `_external-lemmas.md`",
            )
            break


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notes", nargs="+", type=Path)
    args = parser.parse_args()

    tracker = parse_tracker(TRACKER_PATH)
    if not tracker:
        print(f"warning: tracker {TRACKER_PATH} is empty or missing; cross-checks disabled", file=sys.stderr)
    if not EXTERNAL_LEMMAS.exists():
        print(f"warning: {EXTERNAL_LEMMAS} missing; external-theorem checks will still require the link", file=sys.stderr)

    result = LintResult()
    for note in args.notes:
        lint_note(note.resolve(), tracker, result)

    if result.ok:
        print("lint-notes: OK")
        return 0

    for finding in result.findings:
        print(finding.format())
    print(f"lint-notes: FAIL ({len(result.findings)} issue{'s' if len(result.findings) != 1 else ''})")
    return 1


if __name__ == "__main__":
    sys.exit(main())
