#!/usr/bin/env python3
from __future__ import annotations

import argparse
import bisect
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

THEOREM_LIKE = {
    "theorem",
    "lemma",
    "proposition",
    "corollary",
    "claim",
    "remark",
    "assumption",
    "definition",
    "fact",
    "example",
}
BLOCK_ENVS = THEOREM_LIKE | {"proof"}
REF_COMMANDS = [
    "ref",
    "eqref",
    "autoref",
    "cref",
    "Cref",
    "vref",
    "Vref",
    "pageref",
    "nameref",
    "labelcref",
]
CITE_COMMANDS = [
    "cite",
    "citet",
    "citep",
    "citealp",
    "citealt",
    "citeauthor",
    "Citeauthor",
    "Citet",
    "Citep",
    "citeyear",
    "citeyearpar",
    "nocite",
    "parencite",
    "textcite",
]


@dataclass
class Occurrence:
    file: str
    line: int
    command: str
    key: str


@dataclass
class Block:
    file: str
    env: str
    start_line: int
    end_line: int
    label: str | None = None


def strip_comments(text: str) -> str:
    out_lines = []
    for raw_line in text.splitlines():
        line = []
        escaped = False
        for ch in raw_line:
            if ch == "%" and not escaped:
                break
            line.append(ch)
            escaped = ch == "\\"
        out_lines.append("".join(line))
    return "\n".join(out_lines) + "\n"


def line_starts(text: str) -> list[int]:
    starts = [0]
    for index, char in enumerate(text):
        if char == "\n":
            starts.append(index + 1)
    return starts


def line_number(starts: list[int], pos: int) -> int:
    return bisect.bisect_right(starts, pos)


def compile_command_regex(commands: list[str]) -> re.Pattern[str]:
    joined = "|".join(sorted(map(re.escape, commands), key=len, reverse=True))
    return re.compile(
        rf"\\(?P<cmd>{joined})\*?(?:\[[^\]]*\])*" r"\{(?P<arg>[^}]*)\}",
        re.MULTILINE,
    )


REF_RE = compile_command_regex(REF_COMMANDS)
CITE_RE = compile_command_regex(CITE_COMMANDS)
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
BEGIN_END_RE = re.compile(r"\\(begin|end)\{([A-Za-z*]+)\}")
BIB_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,")


def parse_tex_file(path: Path) -> dict[str, object]:
    raw = path.read_text(encoding="utf-8")
    cleaned = strip_comments(raw)
    starts = line_starts(cleaned)

    labels: list[Occurrence] = []
    refs: list[Occurrence] = []
    cites: list[Occurrence] = []
    warnings: list[str] = []
    blocks: list[Block] = []
    stack: list[tuple[str, int]] = []

    for match in LABEL_RE.finditer(cleaned):
        labels.append(
            Occurrence(
                file=str(path),
                line=line_number(starts, match.start()),
                command="label",
                key=match.group(1).strip(),
            )
        )

    for regex, bucket in ((REF_RE, refs), (CITE_RE, cites)):
        for match in regex.finditer(cleaned):
            keys = [piece.strip() for piece in match.group("arg").split(",") if piece.strip()]
            for key in keys:
                bucket.append(
                    Occurrence(
                        file=str(path),
                        line=line_number(starts, match.start()),
                        command=match.group("cmd"),
                        key=key,
                    )
                )

    for match in BEGIN_END_RE.finditer(cleaned):
        kind, env = match.group(1), match.group(2)
        line = line_number(starts, match.start())
        if kind == "begin":
            stack.append((env, line))
            continue

        if stack and stack[-1][0] == env:
            begin_env, begin_line = stack.pop()
            if begin_env in BLOCK_ENVS:
                blocks.append(Block(file=str(path), env=begin_env, start_line=begin_line, end_line=line))
            continue

        recover_index = None
        for index in range(len(stack) - 1, -1, -1):
            if stack[index][0] == env:
                recover_index = index
                break

        if recover_index is None:
            warnings.append(f"{path}:{line}: unmatched \\end{{{env}}}")
            continue

        while len(stack) - 1 > recover_index:
            dangling_env, dangling_line = stack.pop()
            warnings.append(
                f"{path}:{line}: expected \\end{{{dangling_env}}} for block opened at line {dangling_line}"
            )

        begin_env, begin_line = stack.pop()
        if begin_env in BLOCK_ENVS:
            blocks.append(Block(file=str(path), env=begin_env, start_line=begin_line, end_line=line))

    for env, begin_line in reversed(stack):
        warnings.append(f"{path}:{begin_line}: unclosed \\begin{{{env}}}")

    return {
        "labels": labels,
        "refs": refs,
        "cites": cites,
        "blocks": blocks,
        "warnings": warnings,
    }


def assign_labels(blocks: list[Block], labels: list[Occurrence]) -> None:
    by_file: dict[str, list[Block]] = defaultdict(list)
    for block in blocks:
        by_file[block.file].append(block)
    for file_blocks in by_file.values():
        file_blocks.sort(key=lambda block: (block.start_line, -(block.end_line - block.start_line)))

    for label in labels:
        candidates = [
            block
            for block in by_file.get(label.file, [])
            if block.start_line <= label.line <= block.end_line
        ]
        if not candidates:
            continue
        candidates.sort(key=lambda block: (block.end_line - block.start_line, -block.start_line))
        block = candidates[0]
        if block.env in THEOREM_LIKE and block.label is None:
            block.label = label.key


def load_bib_keys(paths: list[Path]) -> dict[str, list[str]]:
    key_locations: dict[str, list[str]] = defaultdict(list)
    for path in paths:
        if not path.exists():
            continue
        text = strip_comments(path.read_text(encoding="utf-8"))
        starts = line_starts(text)
        for match in BIB_RE.finditer(text):
            key = match.group(1).strip()
            location = f"{path}:{line_number(starts, match.start())}"
            key_locations[key].append(location)
    return key_locations


def format_occurrences(occurrences: list[Occurrence]) -> list[str]:
    return [f"{item.file}:{item.line}: \\{item.command}{{{item.key}}}" for item in occurrences]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit LaTeX proof files for missing refs/cites, duplicate labels, and block structure."
    )
    parser.add_argument("tex_files", nargs="+", help="LaTeX source files to inspect")
    parser.add_argument("--bib", nargs="*", default=None, help="Bib files to inspect for citation keys")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Return a nonzero status code on any issue")
    args = parser.parse_args()

    tex_paths = [Path(name) for name in args.tex_files]
    bib_paths = [Path(name) for name in args.bib] if args.bib is not None else []
    if args.bib is None:
        seen = set()
        for tex_path in tex_paths:
            for bib_path in sorted(tex_path.parent.glob("*.bib")):
                if bib_path not in seen:
                    bib_paths.append(bib_path)
                    seen.add(bib_path)

    all_labels: list[Occurrence] = []
    all_refs: list[Occurrence] = []
    all_cites: list[Occurrence] = []
    all_blocks: list[Block] = []
    warnings: list[str] = []

    for tex_path in tex_paths:
        parsed = parse_tex_file(tex_path)
        all_labels.extend(parsed["labels"])
        all_refs.extend(parsed["refs"])
        all_cites.extend(parsed["cites"])
        all_blocks.extend(parsed["blocks"])
        warnings.extend(parsed["warnings"])

    assign_labels(all_blocks, all_labels)

    label_locations: dict[str, list[str]] = defaultdict(list)
    for label in all_labels:
        label_locations[label.key].append(f"{label.file}:{label.line}")
    duplicate_labels = {
        key: locations for key, locations in sorted(label_locations.items()) if len(locations) > 1
    }
    defined_labels = set(label_locations)

    bib_key_locations = load_bib_keys(bib_paths)
    defined_bib_keys = set(bib_key_locations)

    undefined_refs = [item for item in all_refs if item.key not in defined_labels]
    undefined_cites = [item for item in all_cites if item.key not in defined_bib_keys]
    unlabeled_blocks = [
        {
            "file": block.file,
            "env": block.env,
            "start_line": block.start_line,
            "end_line": block.end_line,
        }
        for block in sorted(all_blocks, key=lambda block: (block.file, block.start_line))
        if block.env in THEOREM_LIKE and block.label is None
    ]

    issues_found = bool(duplicate_labels or undefined_refs or undefined_cites or warnings)
    payload = {
        "tex_files": [str(path) for path in tex_paths],
        "bib_files": [str(path) for path in bib_paths],
        "duplicate_labels": duplicate_labels,
        "undefined_refs": [
            {
                "file": item.file,
                "line": item.line,
                "command": item.command,
                "key": item.key,
            }
            for item in undefined_refs
        ],
        "undefined_cites": [
            {
                "file": item.file,
                "line": item.line,
                "command": item.command,
                "key": item.key,
            }
            for item in undefined_cites
        ],
        "environment_warnings": warnings,
        "unlabeled_theorem_like_blocks": unlabeled_blocks,
    }

    if args.json:
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        print("LaTeX proof sanity audit")
        print(f"  tex files: {', '.join(payload['tex_files'])}")
        if bib_paths:
            print(f"  bib files: {', '.join(payload['bib_files'])}")
        print(f"  duplicate labels: {len(duplicate_labels)}")
        print(f"  undefined refs: {len(undefined_refs)}")
        print(f"  undefined cites: {len(undefined_cites)}")
        print(f"  environment warnings: {len(warnings)}")
        print(f"  unlabeled theorem-like blocks: {len(unlabeled_blocks)}")

        if duplicate_labels:
            print("\nDuplicate labels")
            for key, locations in duplicate_labels.items():
                print(f"  {key}")
                for location in locations:
                    print(f"    - {location}")

        if undefined_refs:
            print("\nUndefined refs")
            for line in format_occurrences(undefined_refs):
                print(f"  - {line}")

        if undefined_cites:
            print("\nUndefined cites")
            for line in format_occurrences(undefined_cites):
                print(f"  - {line}")

        if warnings:
            print("\nEnvironment warnings")
            for warning in warnings:
                print(f"  - {warning}")

        if unlabeled_blocks:
            print("\nUnlabeled theorem-like blocks")
            for block in unlabeled_blocks:
                print(
                    "  - "
                    f"{block['file']}:{block['start_line']}-{block['end_line']} "
                    f"({block['env']})"
                )

        if not issues_found:
            print("\nNo hard failures found.")

    return 1 if args.strict and issues_found else 0


if __name__ == "__main__":
    raise SystemExit(main())
