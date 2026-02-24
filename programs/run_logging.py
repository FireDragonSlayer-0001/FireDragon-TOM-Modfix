from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path


class ProgramLogger:
    def __init__(self, program_name: str) -> None:
        self.program_name = program_name
        self.run_id = os.environ.get("TOM_RUN_ID") or datetime.now().strftime("%Y%m%d-%H%M%S")

        logs_root_env = os.environ.get("TOM_LOGS_ROOT")
        if logs_root_env:
            logs_root = Path(logs_root_env)
        else:
            logs_root = Path(__file__).resolve().parent.parent / "Logs"

        self.run_dir = logs_root / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)

        self.main_log_path = self.run_dir / "main.log"
        self.detail_log_path = self.run_dir / f"{self.program_name}.log"

    def detail(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}"
        print(message)
        with self.detail_log_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def main_summary(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] [{self.program_name}] {message}"
        with self.main_log_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def detail_summary(self, heading: str, groups: dict[str, list[str]]) -> None:
        with self.detail_log_path.open("a", encoding="utf-8") as fh:
            fh.write("\n=== SUMMARY ===\n")
            fh.write(heading + "\n")
            for label, entries in groups.items():
                ordered = sorted(entries)
                joined = ", ".join(ordered) if ordered else "(none)"
                fh.write(f"- {label}: {len(ordered)}\n")
                fh.write(f"  Mods: {joined}\n")
