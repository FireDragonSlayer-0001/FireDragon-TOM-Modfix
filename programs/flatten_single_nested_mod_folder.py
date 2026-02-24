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

from run_logging import ProgramLogger
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
    logger = ProgramLogger("04_flatten")

    if not output_root.exists() or not output_root.is_dir():
        logger.detail(f"[ERROR] output root does not exist or is not a folder: {output_root}")
        logger.main_summary("failed: output root missing/invalid")
        return 1

    checked = 0
    flattened = 0
    moved_items = 0
    skipped_items = 0

    flattened_mods: list[str] = []
    skipped_mods: list[str] = []

    for folder in output_root.iterdir():
        if not folder.is_dir():
            continue

        checked += 1
        children = list(folder.iterdir())
        if len(children) != 1:
            logger.detail(f"[SKIP] {folder.name}: expected exactly 1 child, found {len(children)}")
            skipped_mods.append(folder.name)
            continue

        nested = children[0]
        if not nested.is_dir() or not nested.name.startswith(MOD_PREFIX):
            logger.detail(f"[SKIP] {folder.name}: only child is not a '{MOD_PREFIX}*' folder")
            skipped_mods.append(folder.name)
            continue

        logger.detail(f"[FIX ] {folder.name}: flattening nested folder '{nested.name}'")
        moved, skipped = move_contents_up(nested, folder)
        moved_items += moved
        skipped_items += skipped

        if not any(nested.iterdir()):
            nested.rmdir()
            flattened += 1
            flattened_mods.append(folder.name)
        else:
            logger.detail(f"  [WARN] Nested folder not empty, not removed: {nested}")
            skipped_mods.append(folder.name)

    logger.detail("\n=== DONE ===")
    logger.detail(f"Checked folders: {checked}")
    logger.detail(f"Flattened folders: {flattened}")
    logger.detail(f"Moved items: {moved_items}")
    logger.detail(f"Skipped items: {skipped_items}")
    logger.main_summary(
        f"checked={checked}, flattened={flattened}, moved_items={moved_items}, skipped_items={skipped_items}"
    )
    logger.detail_summary(
        "Per-mod flatten outcome",
        {
            "Flattened folders": flattened_mods,
            "Skipped/unchanged folders": skipped_mods,
        },
    )
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
        output_root = root_from_config(args.config) / config.get("shippable_output_dir", config.get("output_folder", "Output"))
    return flatten_output(output_root)


if __name__ == "__main__":
    raise SystemExit(main())
