"""Task 2:
Find duplicate Mod_* folders under output and rename extra copies with a random suffix.

Duplicate detection is done inside each parent directory. If multiple folders share the same
base name after stripping a trailing `_<5 alnum chars>` suffix, all but the first are renamed.
"""

from __future__ import annotations

import argparse
import random
import re
import string
from pathlib import Path

MOD_PREFIX = "Mod_"
SUFFIX_RE = re.compile(r"^(?P<base>.+)_([A-Za-z0-9]{5})$")
ALNUM = string.ascii_letters + string.digits


def random_suffix(length: int = 5) -> str:
    return "".join(random.choices(ALNUM, k=length))


def normalized_key(name: str) -> str:
    if not name.startswith(MOD_PREFIX):
        return name

    match = SUFFIX_RE.match(name)
    if not match:
        return name

    return match.group("base")


def unique_renamed_path(folder: Path) -> Path:
    base_name = folder.name
    while True:
        candidate = folder.with_name(f"{base_name}_{random_suffix(5)}")
        if not candidate.exists():
            return candidate


def rename_duplicates_in_parent(parent: Path) -> int:
    renamed = 0
    groups: dict[str, list[Path]] = {}

    for child in parent.iterdir():
        if child.is_dir() and child.name.startswith(MOD_PREFIX):
            key = normalized_key(child.name)
            groups.setdefault(key, []).append(child)

    for _, folders in groups.items():
        if len(folders) < 2:
            continue

        folders.sort(key=lambda p: p.name)
        for duplicate in folders[1:]:
            new_path = unique_renamed_path(duplicate)
            duplicate.rename(new_path)
            print(f"[RENAME] {duplicate} -> {new_path.name}")
            renamed += 1

    return renamed


def scan_output(output_root: Path) -> int:
    if not output_root.exists() or not output_root.is_dir():
        print(f"[ERROR] output root does not exist or is not a folder: {output_root}")
        return 1

    total_renamed = 0
    for parent in [output_root, *[p for p in output_root.rglob("*") if p.is_dir()]]:
        total_renamed += rename_duplicates_in_parent(parent)

    print(f"\n=== DONE ===\nTotal renamed folders: {total_renamed}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rename duplicate Mod_* folders by appending random 5-char alnum suffixes."
    )
    parser.add_argument("output_root", type=Path, help="Path to output root directory.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return scan_output(args.output_root)


if __name__ == "__main__":
    raise SystemExit(main())
