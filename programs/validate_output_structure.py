"""Task 3:
Check whether output folder structure is proper after extraction.

Rule used by the extractor:
- A folder is considered bugged when it contains BOTH `ModProject` and `debug` directories.
In output, such a structure should generally not remain after extraction.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from run_logging import ProgramLogger
from shared_config import load_config, root_from_config

BUGGED_MARKERS = {"ModProject", "debug"}


def has_bugged_structure(folder: Path) -> bool:
    names = {p.name for p in folder.iterdir() if p.is_dir()}
    return BUGGED_MARKERS.issubset(names)


def validate_output(output_root: Path) -> int:
    logger = ProgramLogger("03_validate")

    if not output_root.exists() or not output_root.is_dir():
        logger.detail(f"[ERROR] output root does not exist or is not a folder: {output_root}")
        logger.main_summary("failed: output root missing/invalid")
        return 1

    checked = 0
    invalid = 0

    valid_mods: list[str] = []
    invalid_mods: list[str] = []

    for mod_folder in output_root.iterdir():
        if not mod_folder.is_dir():
            continue

        checked += 1
        if has_bugged_structure(mod_folder):
            logger.detail(
                f"[BAD ] {mod_folder.name}: still contains both '{sorted(BUGGED_MARKERS)[0]}' "
                f"and '{sorted(BUGGED_MARKERS)[1]}'"
            )
            invalid += 1
            invalid_mods.append(mod_folder.name)
        else:
            logger.detail(f"[OK  ] {mod_folder.name}")
            valid_mods.append(mod_folder.name)

    logger.detail("\n=== DONE ===")
    logger.detail(f"Checked folders: {checked}")
    logger.detail(f"Invalid folders: {invalid}")
    logger.main_summary(f"checked={checked}, invalid={invalid}, valid={len(valid_mods)}")
    logger.detail_summary(
        "Output validation outcome",
        {
            "Valid output folders": valid_mods,
            "Invalid output folders": invalid_mods,
        },
    )
    return 0 if invalid == 0 else 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate output folder structure.")
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
    return validate_output(output_root)


if __name__ == "__main__":
    raise SystemExit(main())
