"""Task 3:
Check whether output folder structure is proper based on root `First.py` expectations.

Rule used from `First.py`:
- A folder is considered bugged when it contains BOTH `ModProject` and `debug` directories.
In output, such a structure should generally not remain after extraction.
"""

from __future__ import annotations

import argparse
from pathlib import Path

BUGGED_MARKERS = {"ModProject", "debug"}


def has_bugged_structure(folder: Path) -> bool:
    names = {p.name for p in folder.iterdir() if p.is_dir()}
    return BUGGED_MARKERS.issubset(names)


def validate_output(output_root: Path) -> int:
    if not output_root.exists() or not output_root.is_dir():
        print(f"[ERROR] output root does not exist or is not a folder: {output_root}")
        return 1

    checked = 0
    invalid = 0

    for mod_folder in output_root.iterdir():
        if not mod_folder.is_dir():
            continue

        checked += 1
        if has_bugged_structure(mod_folder):
            print(
                f"[BAD ] {mod_folder.name}: still contains both '{sorted(BUGGED_MARKERS)[0]}' "
                f"and '{sorted(BUGGED_MARKERS)[1]}'"
            )
            invalid += 1
        else:
            print(f"[OK  ] {mod_folder.name}")

    print("\n=== DONE ===")
    print(f"Checked folders: {checked}")
    print(f"Invalid folders: {invalid}")
    return 0 if invalid == 0 else 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate output folder structure.")
    parser.add_argument("output_root", type=Path, help="Path to output root directory.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return validate_output(args.output_root)


if __name__ == "__main__":
    raise SystemExit(main())
