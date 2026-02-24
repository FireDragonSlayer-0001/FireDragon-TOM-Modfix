"""Task 2:
Find duplicate `Mod_` folders under output and rename extra copies.

Rules:
- `Mod_` is a fixed prefix and is never changed.
- Duplicate comparison is based on the exact suffix after `Mod_` across the output tree.
- If duplicates are found, all but the first are renamed to `Mod_<random 5 alnum chars>`.
"""

from __future__ import annotations

import argparse
import random
import string
from pathlib import Path

from run_logging import ProgramLogger
from shared_config import load_config, root_from_config

MOD_PREFIX = "Mod_"
ALNUM = string.ascii_letters + string.digits


def random_suffix(length: int = 5) -> str:
    return "".join(random.choices(ALNUM, k=length))


def suffix_after_prefix(name: str) -> str:
    return name[len(MOD_PREFIX) :]


def unique_renamed_path(folder: Path) -> Path:
    while True:
        candidate = folder.with_name(f"{MOD_PREFIX}{random_suffix(5)}")
        if not candidate.exists():
            return candidate


def rename_duplicates_in_output(output_root: Path, logger: ProgramLogger) -> tuple[int, list[str], list[str]]:
    renamed = 0
    groups: dict[str, list[Path]] = {}
    renamed_details: list[str] = []
    duplicate_mod_names: list[str] = []

    mod_folders = [output_root, *output_root.rglob("*")]
    for child in mod_folders:
        if child.is_dir() and child.name.startswith(MOD_PREFIX):
            key = suffix_after_prefix(child.name)
            groups.setdefault(key, []).append(child)

    for _, folders in groups.items():
        if len(folders) < 2:
            continue

        folders.sort(key=lambda p: str(p))
        duplicate_mod_names.append(folders[0].name)
        for duplicate in folders[1:]:
            new_path = unique_renamed_path(duplicate)
            duplicate.rename(new_path)
            detail = f"{duplicate} -> {new_path.name}"
            logger.detail(f"[RENAME] {detail}")
            renamed_details.append(detail)
            renamed += 1

    return renamed, duplicate_mod_names, renamed_details


def scan_output(output_root: Path) -> int:
    logger = ProgramLogger("02_rename")

    if not output_root.exists() or not output_root.is_dir():
        logger.detail(f"[ERROR] output root does not exist or is not a folder: {output_root}")
        logger.main_summary("failed: output root missing/invalid")
        return 1

    total_renamed, duplicate_mod_names, renamed_details = rename_duplicates_in_output(output_root, logger)

    logger.detail("\n=== DONE ===")
    logger.detail(f"Total renamed folders: {total_renamed}")
    logger.main_summary(
        f"duplicate_groups={len(duplicate_mod_names)}, renamed={total_renamed}"
    )
    logger.detail_summary(
        "Duplicate rename outcome",
        {
            "Duplicate mod groups found": duplicate_mod_names,
            "Renamed duplicate folders": renamed_details,
        },
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rename duplicate Mod_ folders by replacing duplicate suffixes with random 5-char alnum values."
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
    return scan_output(output_root)


if __name__ == "__main__":
    raise SystemExit(main())
