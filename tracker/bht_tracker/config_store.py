import json
import os
from pathlib import Path


def load_config(config_path: Path) -> dict:
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(config_path: Path, config: dict) -> None:
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception:
        pass


def write_pid_file(pid_path: Path) -> None:
    try:
        pid_path.write_text(str(os.getpid()), encoding="utf-8")
    except Exception:
        pass


def remove_pid_file(pid_path: Path) -> None:
    try:
        if pid_path.exists():
            pid_path.unlink()
    except Exception:
        pass