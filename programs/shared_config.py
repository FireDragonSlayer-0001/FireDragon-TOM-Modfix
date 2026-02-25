from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "source_folder": "Source",
    "output_folder": "Output",
    "shippable_output_dir": "Output",
    "alternative_output_dir": "Alternative Output",
    "replace_directory": "",
    "programs_folder": "programs",
    "main_script": "programs/check_source_and_extract_to_output.py",
    "flatten_script": "programs/flatten_single_nested_mod_folder.py",
    "rename_script": "programs/rename_duplicate_mod_folders.py",
    "validate_script": "programs/validate_output_structure.py",
    "alternative_builder_script": "programs/build_alternative_output_for_broken_mods.py",
    "safe_replace_script": "programs/safe_replace_from_alternative_output.py",
    "manual_fixing_required_dir": "Manual Fixing Required",
    "auto_update_tools": False,
    "do_move": False,
    "overwrite_files": True,
    "enable_alternative_output": False,
    "enable_safe_replace": False,
    "replace_dry_run": True,
    "replace_backup_enabled": False,
}

# Backward-compatible aliases for historical/alternate config key naming.
# Keys are normalized by lowercasing and removing non-alphanumeric chars.
_CONFIG_KEY_ALIASES: dict[str, str] = {
    "sourcefolder": "source_folder",
    "outputfolder": "output_folder",
    "shippableoutputdir": "shippable_output_dir",
    "alternativeoutputdir": "alternative_output_dir",
    "replacedirectory": "replace_directory",
    "programsfolder": "programs_folder",
    "mainscript": "main_script",
    "flattenscript": "flatten_script",
    "renamescript": "rename_script",
    "validatescript": "validate_script",
    "alternativebuilderscript": "alternative_builder_script",
    "safereplacescript": "safe_replace_script",
    "manualfixingrequireddir": "manual_fixing_required_dir",
    "autoupdatetools": "auto_update_tools",
    "domove": "do_move",
    "overwritefiles": "overwrite_files",
    "enablealternativeoutput": "enable_alternative_output",
    "enablesafereplace": "enable_safe_replace",
    "replacedryrun": "replace_dry_run",
    "replacebackupenabled": "replace_backup_enabled",
}


def _normalize_key(key: str) -> str:
    return "".join(ch for ch in key.lower() if ch.isalnum())


def _normalize_config_keys(loaded: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(loaded)

    for key, value in loaded.items():
        if key in DEFAULT_CONFIG:
            continue

        canonical = _CONFIG_KEY_ALIASES.get(_normalize_key(key))
        if canonical and canonical not in loaded:
            normalized[canonical] = value

    return normalized


def _apply_back_compat(config: dict[str, Any]) -> None:
    shippable = config.get("shippable_output_dir")
    legacy = config.get("output_folder")

    if not shippable and legacy:
        config["shippable_output_dir"] = legacy
    if not legacy and shippable:
        config["output_folder"] = shippable


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    if config_path is None:
        config_path = Path(__file__).resolve().parent.parent / "config.json"

    config = dict(DEFAULT_CONFIG)
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as fh:
            loaded = json.load(fh)
            if isinstance(loaded, dict):
                config.update(_normalize_config_keys(loaded))

    _apply_back_compat(config)
    return config


def root_from_config(config_path: Path | None = None) -> Path:
    if config_path is None:
        return Path(__file__).resolve().parent.parent
    return config_path.resolve().parent
