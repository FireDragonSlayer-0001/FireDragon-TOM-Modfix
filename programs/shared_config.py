from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "source_folder": "Source",
    "output_folder": "Output",
    "programs_folder": "programs",
    "main_script": "programs/check_source_and_extract_to_output.py",
    "flatten_script": "programs/flatten_single_nested_mod_folder.py",
    "auto_update_tools": False,
    "do_move": False,
    "overwrite_files": True,
}


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    if config_path is None:
        config_path = Path(__file__).resolve().parent.parent / "config.json"

    config = dict(DEFAULT_CONFIG)
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as fh:
            loaded = json.load(fh)
            if isinstance(loaded, dict):
                config.update(loaded)

    return config


def root_from_config(config_path: Path | None = None) -> Path:
    if config_path is None:
        return Path(__file__).resolve().parent.parent
    return config_path.resolve().parent
