from pathlib import Path

import mediapipe as mp

from .app_paths import PathContext, build_model_search_report


def validate_model_path(paths: PathContext) -> None:
    if paths.model_path.exists():
        return

    tried_msg = build_model_search_report(paths)
    raise FileNotFoundError(
        f"Model file not found: {paths.model_path}\n"
        f"Required: face_landmarker.task must ship with the app.\n"
        f"Tried:\n"
        f"{tried_msg}\n"
        f"Or set BHT_MODEL_PATH / HTVA_MODEL_PATH to an absolute path."
    )


def create_landmarker(model_path: Path):
    base_options = mp.tasks.BaseOptions
    face_landmarker_options = mp.tasks.vision.FaceLandmarkerOptions
    running_mode = mp.tasks.vision.RunningMode
    face_landmarker = mp.tasks.vision.FaceLandmarker

    options = face_landmarker_options(
        base_options=base_options(model_asset_path=str(model_path)),
        running_mode=running_mode.VIDEO,
        num_faces=1,
    )

    return face_landmarker.create_from_options(options)