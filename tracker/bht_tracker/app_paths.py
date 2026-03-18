import os
import sys
from dataclasses import dataclass
from pathlib import Path


def _env_first(*names: str) -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return ""


def get_app_dir() -> Path:
    """
    Returns the directory this app should treat as its working folder:
    - When packaged (PyInstaller): folder containing tracker.exe / tracker binary
    - When running as .py: folder containing this script
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def find_existing_path(candidates: list[Path]) -> Path | None:
    for path in candidates:
        try:
            if path.exists():
                return path
        except Exception:
            pass
    return None


def get_bundle_outer_dir(here: Path) -> Path | None:
    """
    When running inside:
      tracker.app/Contents/MacOS/tracker
    return the folder containing tracker.app:
      .../tracker
    Otherwise return None.
    """
    try:
        if (
            here.name == "MacOS"
            and here.parent.name == "Contents"
            and here.parent.parent.suffix == ".app"
        ):
            return here.parent.parent.parent
    except Exception:
        pass
    return None


@dataclass(frozen=True)
class PathContext:
    here: Path
    bundle_outer_dir: Path | None
    config_path: Path
    pid_path: Path
    model_path: Path
    video_file: Path | None


def resolve_model_path(here: Path, bundle_outer_dir: Path | None) -> Path:
    env_model = _env_first("BHT_MODEL_PATH", "HTVA_MODEL_PATH")
    if env_model:
        return Path(env_model)

    model_candidates = [
        here / "face_landmarker.task",
        here / "_internal" / "face_landmarker.task",
    ]

    if bundle_outer_dir is not None:
        model_candidates.extend([
            bundle_outer_dir / "face_landmarker.task",
            here.parent / "Resources" / "face_landmarker.task",
            here.parent / "Frameworks" / "face_landmarker.task",
        ])

    model_path = find_existing_path(model_candidates)
    if model_path is None:
        return here / "_internal" / "face_landmarker.task"
    return model_path


def resolve_video_file(here: Path, bundle_outer_dir: Path | None) -> Path | None:
    video_candidates = [
        here / "test.mp4",
    ]

    if bundle_outer_dir is not None:
        video_candidates.extend([
            bundle_outer_dir / "test.mp4",
            here.parent / "Resources" / "test.mp4",
        ])

    return find_existing_path(video_candidates)


def build_paths() -> PathContext:
    here = get_app_dir()
    bundle_outer_dir = get_bundle_outer_dir(here)

    return PathContext(
        here=here,
        bundle_outer_dir=bundle_outer_dir,
        config_path=here / "config.json",
        pid_path=here / "tracker_pid.txt",
        model_path=resolve_model_path(here, bundle_outer_dir),
        video_file=resolve_video_file(here, bundle_outer_dir),
    )


def build_model_search_report(paths: PathContext) -> str:
    tried_lines = [
        str(paths.here / "face_landmarker.task"),
        str(paths.here / "_internal" / "face_landmarker.task"),
    ]

    if paths.bundle_outer_dir is not None:
        tried_lines.extend([
            str(paths.bundle_outer_dir / "face_landmarker.task"),
            str(paths.here.parent / "Resources" / "face_landmarker.task"),
            str(paths.here.parent / "Frameworks" / "face_landmarker.task"),
        ])

    return "\n".join(f"  - {p}" for p in tried_lines)


def build_video_search_report(paths: PathContext) -> str:
    tried_lines = [
        str(paths.here / "test.mp4"),
    ]

    if paths.bundle_outer_dir is not None:
        tried_lines.extend([
            str(paths.bundle_outer_dir / "test.mp4"),
            str(paths.here.parent / "Resources" / "test.mp4"),
        ])

    return "\n".join(f"  - {p}" for p in tried_lines)