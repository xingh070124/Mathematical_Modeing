#!/usr/bin/env python3
from __future__ import annotations

import argparse
import bisect
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict
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
TARGET_ENVS = THEOREM_LIKE | {"proof"}
BEGIN_RE = re.compile(r"\\begin\{(?P<env>[A-Za-z*]+)\}(?:\[(?P<title>[^\]]*)\])?")
END_RE = re.compile(r"\\end\{(?P<env>[A-Za-z*]+)\}")
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")


@dataclass
class Block:
    file: str
    env: str
    start_line: int
    end_line: int
    start_pos: int
    end_pos: int
    title: str | None = None
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


NEWTHEOREM_RE = re.compile(r"\\newtheorem\{([A-Za-z*]+)\}")


def discover_custom_envs(path: Path) -> None:
    """Scan for \\newtheorem{...} declarations and add them to THEOREM_LIKE."""
    raw = path.read_text(encoding="utf-8")
    for m in NEWTHEOREM_RE.finditer(raw):
        env_name = m.group(1)
        THEOREM_LIKE.add(env_name)
        TARGET_ENVS.add(env_name)


def parse_blocks(path: Path) -> list[Block]:
    raw = path.read_text(encoding="utf-8")
    cleaned = strip_comments(raw)
    starts = line_starts(cleaned)

    events = []
    for match in BEGIN_RE.finditer(cleaned):
        events.append(("begin", match.start(), match))
    for match in END_RE.finditer(cleaned):
        events.append(("end", match.start(), match))
    events.sort(key=lambda item: item[1])

    stack: list[tuple[str, int, int, str | None]] = []
    blocks: list[Block] = []
    for kind, pos, match in events:
        env = match.group("env")
        if kind == "begin":
            stack.append((env, pos, line_number(starts, pos), match.groupdict().get("title")))
            continue
        if stack and stack[-1][0] == env:
            begin_env, begin_pos, begin_line, title = stack.pop()
            if begin_env in TARGET_ENVS:
                blocks.append(
                    Block(
                        file=str(path),
                        env=begin_env,
                        start_line=begin_line,
                        end_line=line_number(starts, pos),
                        start_pos=begin_pos,
                        end_pos=pos,
                        title=title.strip() if title else None,
                    )
                )
            continue

        for index in range(len(stack) - 1, -1, -1):
            if stack[index][0] == env:
                begin_env, begin_pos, begin_line, title = stack.pop(index)
                if begin_env in TARGET_ENVS:
                    blocks.append(
                        Block(
                            file=str(path),
                            env=begin_env,
                            start_line=begin_line,
                            end_line=line_number(starts, pos),
                            start_pos=begin_pos,
                            end_pos=pos,
                            title=title.strip() if title else None,
                        )
                    )
                break

    labels = []
    for match in LABEL_RE.finditer(cleaned):
        labels.append((match.group(1).strip(), line_number(starts, match.start())))

    blocks.sort(key=lambda block: (block.start_pos, block.end_pos))
    for label, line in labels:
        candidates = [block for block in blocks if block.start_line <= line <= block.end_line]
        if not candidates:
            continue
        candidates.sort(key=lambda block: (block.end_line - block.start_line, -block.start_line))
        block = candidates[0]
        if block.env in THEOREM_LIKE and block.label is None:
            block.label = label

    return blocks


def attach_proofs(blocks: list[Block]) -> dict[tuple[str, int, int], Block | None]:
    attached: dict[tuple[str, int, int], Block | None] = {}
    by_file: dict[str, list[Block]] = defaultdict(list)
    for block in blocks:
        by_file[block.file].append(block)

    for file_blocks in by_file.values():
        file_blocks.sort(key=lambda block: block.start_pos)
        theorem_blocks = [block for block in file_blocks if block.env in THEOREM_LIKE]
        proof_blocks = [block for block in file_blocks if block.env == "proof"]
        for index, theorem_block in enumerate(theorem_blocks):
            next_theorem_pos = (
                theorem_blocks[index + 1].start_pos if index + 1 < len(theorem_blocks) else float("inf")
            )
            proof = None
            for candidate in proof_blocks:
                if theorem_block.end_pos < candidate.start_pos < next_theorem_pos:
                    proof = candidate
                    break
            attached[(theorem_block.file, theorem_block.start_line, theorem_block.end_line)] = proof

    return attached


def print_block(path: Path, block: Block) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    header = f"{block.env} {block.file}:{block.start_line}-{block.end_line}"
    if block.label:
        header += f" label={block.label}"
    if block.title:
        header += f" title={block.title}"
    print(header)
    for line_no in range(block.start_line, block.end_line + 1):
        if 1 <= line_no <= len(lines):
            print(f"{line_no:5d}: {lines[line_no - 1]}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract theorem/proof structure from LaTeX sources.")
    parser.add_argument("tex_files", nargs="+", help="LaTeX files to inspect")
    parser.add_argument("--label", help="Print the full block for the theorem-like block carrying this label")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--envs", help="Comma-separated extra environment names to treat as theorem-like (e.g. 'ourtheorem,mainresult')")
    args = parser.parse_args()

    if args.envs:
        for env_name in args.envs.split(","):
            env_name = env_name.strip()
            if env_name:
                THEOREM_LIKE.add(env_name)
                TARGET_ENVS.add(env_name)

    # Auto-discover custom theorem environments from \newtheorem{} declarations.
    for tex_file in args.tex_files:
        discover_custom_envs(Path(tex_file))

    blocks: list[Block] = []
    for tex_file in args.tex_files:
        blocks.extend(parse_blocks(Path(tex_file)))
    blocks.sort(key=lambda block: (block.file, block.start_pos))
    proof_map = attach_proofs(blocks)

    if args.label:
        target = next((block for block in blocks if block.label == args.label), None)
        if target is None:
            print(f"Label not found: {args.label}", file=sys.stderr)
            return 1
        print_block(Path(target.file), target)
        attached = proof_map.get((target.file, target.start_line, target.end_line))
        if attached is not None:
            print()
            print_block(Path(attached.file), attached)
        return 0

    records = []
    for block in blocks:
        record = asdict(block)
        if block.env in THEOREM_LIKE:
            proof = proof_map.get((block.file, block.start_line, block.end_line))
            record["attached_proof"] = (
                None
                if proof is None
                else {
                    "file": proof.file,
                    "start_line": proof.start_line,
                    "end_line": proof.end_line,
                }
            )
        records.append(record)

    if args.json:
        json.dump(records, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    for block in blocks:
        line = f"{block.file}:{block.start_line}-{block.end_line} [{block.env}]"
        if block.label:
            line += f" label={block.label}"
        if block.title:
            line += f" title={block.title}"
        if block.env in THEOREM_LIKE:
            proof = proof_map.get((block.file, block.start_line, block.end_line))
            if proof is not None:
                line += f" proof={proof.file}:{proof.start_line}-{proof.end_line}"
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
