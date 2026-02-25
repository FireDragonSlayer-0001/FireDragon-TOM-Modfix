"""Safely replace exact matching mods from Alternative Output into a target directory."""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path

try:
    from run_logging import ProgramLogger
    from shared_config import config_bool, load_config, root_from_config
except ModuleNotFoundError:
    from programs.run_logging import ProgramLogger
    from programs.shared_config import config_bool, load_config, root_from_config


def backup_target_folder(target_folder: Path, logger: ProgramLogger) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_folder = target_folder.with_name(f"{target_folder.name}__backup_{timestamp}")
    shutil.copytree(target_folder, backup_folder)
    logger.detail(f"[BACKUP] {target_folder.name} -> {backup_folder.name}")
    return backup_folder


def safe_replace(alternative_output_dir: Path, replace_directory: Path, dry_run: bool, backup_enabled: bool) -> int:
    logger = ProgramLogger("06_safe_replace")

    if not alternative_output_dir.exists() or not alternative_output_dir.is_dir():
        logger.detail(f"[ERROR] alternative output dir missing/invalid: {alternative_output_dir}")
        logger.main_summary("failed: alternative_output_dir missing/invalid")
        return 1

    if not replace_directory.exists() or not replace_directory.is_dir():
        logger.detail(f"[ERROR] replace directory missing/invalid: {replace_directory}")
        logger.main_summary("failed: replace_directory missing/invalid")
        return 1

    replaced = 0
    skipped_not_present = 0
    skipped_invalid_path = 0
    dry_run_skipped = 0
    errors = 0

    replaced_mods: list[str] = []
    skipped_not_present_mods: list[str] = []
    skipped_invalid_mods: list[str] = []
    dry_run_mods: list[str] = []
    error_mods: list[str] = []

    for source_mod in alternative_output_dir.iterdir():
        if not source_mod.is_dir():
            continue

        target_mod = replace_directory / source_mod.name
        if not target_mod.exists():
            logger.detail(f"[SKIP] {source_mod.name}: not present in replace_directory")
            skipped_not_present += 1
            skipped_not_present_mods.append(source_mod.name)
            continue

        if not target_mod.is_dir():
            logger.detail(f"[WARN] {source_mod.name}: matched target exists but is not a directory")
            skipped_invalid_path += 1
            skipped_invalid_mods.append(source_mod.name)
            continue

        try:
            if dry_run:
                logger.detail(f"[DRY ] {source_mod.name}: would replace existing target folder")
                dry_run_skipped += 1
                dry_run_mods.append(source_mod.name)
                continue

            if backup_enabled:
                backup_target_folder(target_mod, logger)

            shutil.rmtree(target_mod)
            shutil.copytree(source_mod, target_mod)

            logger.detail(f"[REPL] {source_mod.name}: replaced exact-name matched target folder")
            replaced += 1
            replaced_mods.append(source_mod.name)
        except Exception as exc:
            logger.detail(f"[ERR ] {source_mod.name}: {exc}")
            errors += 1
            error_mods.append(source_mod.name)

    logger.detail("\n=== DONE ===")
    logger.detail(f"Replaced: {replaced}")
    logger.detail(f"Skipped (not present in target): {skipped_not_present}")
    logger.detail(f"Skipped (invalid path): {skipped_invalid_path}")
    logger.detail(f"Dry-run skipped: {dry_run_skipped}")
    logger.detail(f"Errors: {errors}")
    logger.main_summary(
        "replaced="
        f"{replaced}, skipped_not_present={skipped_not_present}, skipped_invalid={skipped_invalid_path}, "
        f"dry_run_skipped={dry_run_skipped}, errors={errors}"
    )
    logger.detail_summary(
        "Safe replace outcome",
        {
            "Replaced": replaced_mods,
            "Skipped (not present in target)": skipped_not_present_mods,
            "Skipped (invalid path)": skipped_invalid_mods,
            "Dry-run skipped": dry_run_mods,
            "Errors": error_mods,
        },
    )

    return 0 if errors == 0 else 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safely replace exact-name matched mods from Alternative Output.")
    parser.add_argument("--config", type=Path, default=Path("config.json"), help="Path to shared config file.")
    parser.add_argument("alternative_output_dir", type=Path, nargs="?", help="Alternative Output directory override.")
    parser.add_argument("replace_directory", type=Path, nargs="?", help="Replace directory override.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    root = root_from_config(args.config)

    if not config_bool(config.get("enable_safe_replace", False), default=False):
        logger = ProgramLogger("06_safe_replace")
        logger.detail("[INFO] Safe replace is disabled by config (enable_safe_replace=false).")
        logger.main_summary("skipped: enable_safe_replace=false")
        return 0

    alternative_output_dir = args.alternative_output_dir or (
        root / config.get("alternative_output_dir", "Alternative Output")
    )
    configured_replace_dir = str(config.get("replace_directory", "")).strip()
    if args.replace_directory is not None:
        replace_directory = args.replace_directory
    elif configured_replace_dir:
        replace_directory = (
            Path(configured_replace_dir)
            if Path(configured_replace_dir).is_absolute()
            else (root / configured_replace_dir)
        )
    else:
        logger = ProgramLogger("06_safe_replace")
        logger.detail("[ERROR] replace_directory is empty in config; safe replace requires an explicit target directory.")
        logger.main_summary("failed: replace_directory empty")
        return 1

    dry_run = config_bool(config.get("replace_dry_run", True), default=True)
    backup_enabled = config_bool(config.get("replace_backup_enabled", False), default=False)

    return safe_replace(
        alternative_output_dir=alternative_output_dir,
        replace_directory=replace_directory,
        dry_run=dry_run,
        backup_enabled=backup_enabled,
    )


if __name__ == "__main__":
    raise SystemExit(main())
