"""Task 4:
Flatten output folders that contain only a single nested `Mod_*` folder.

For each direct child folder under output:
- if its only item is a directory named `Mod_*`, move the contents of that nested
  folder into the parent folder,
- then remove the now-empty nested `Mod_*` folder.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from shared_config import load_config, root_from_config

MOD_PREFIX = "Mod_"


def move_contents_up(nested_mod_folder: Path, parent_folder: Path) -> tuple[int, int]:
    moved = 0
    skipped = 0

    for item in nested_mod_folder.iterdir():
        target = parent_folder / item.name
        if target.exists():
            print(f"  [SKIP] Target already exists: {target}")
            skipped += 1
            continue

        shutil.move(str(item), str(target))
        moved += 1

    return moved, skipped


def flatten_output(output_root: Path) -> int:
    if not output_root.exists() or not output_root.is_dir():
        print(f"[ERROR] output root does not exist or is not a folder: {output_root}")
        return 1

    checked = 0
    flattened = 0
    moved_items = 0
    skipped_items = 0

    for folder in output_root.iterdir():
        if not folder.is_dir():
            continue

        checked += 1
        children = list(folder.iterdir())
        if len(children) != 1:
            print(f"[SKIP] {folder.name}: expected exactly 1 child, found {len(children)}")
            continue

        nested = children[0]
        if not nested.is_dir() or not nested.name.startswith(MOD_PREFIX):
            print(f"[SKIP] {folder.name}: only child is not a '{MOD_PREFIX}*' folder")
            continue

        print(f"[FIX ] {folder.name}: flattening nested folder '{nested.name}'")
        moved, skipped = move_contents_up(nested, folder)
        moved_items += moved
        skipped_items += skipped

        if not any(nested.iterdir()):
            nested.rmdir()
            flattened += 1
        else:
            print(f"  [WARN] Nested folder not empty, not removed: {nested}")

    print("\n=== DONE ===")
    print(f"Checked folders: {checked}")
    print(f"Flattened folders: {flattened}")
    print(f"Moved items: {moved_items}")
    print(f"Skipped items: {skipped_items}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Flatten output folders where the only child is a nested Mod_* folder."
    )
    parser.add_argument("output_root", type=Path, nargs="?", help="Path to output root directory.")
    parser.add_argument("--config", type=Path, default=Path("config.json"), help="Path to shared config file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.output_root is not None:
        output_root = args.output_root
    else:
        config = load_config(args.config)
        output_root = root_from_config(args.config) / config.get("output_folder", "Output")
    return flatten_output(output_root)


if __name__ == "__main__":
    raise SystemExit(main())
