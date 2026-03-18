import os
import sys
from dataclasses import dataclass

import cv2


def _env_first(*names: str, default: str) -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return default


def _env_bool(*names: str, default: str) -> bool:
    return _env_first(*names, default=default) != "0"


def _env_int(*names: str, default: str) -> int:
    return int(_env_first(*names, default=default))


def _env_float(*names: str, default: str) -> float:
    return float(_env_first(*names, default=default))


@dataclass(frozen=True)
class TrackerSettings:
    is_win: bool
    is_mac: bool
    is_linux: bool

    udp_ip: str
    udp_port: int
    ctrl_port: int

    send_hz: float
    x_gain: float
    y_gain: float
    z_gain: float
    show_preview: bool

    force_mjpg: bool
    force_preview_size: bool

    preview_w: int
    preview_h: int
    capture_w: int
    capture_h: int

    auto_fit_win_preview: bool

    cam_index: int | None
    max_cam_try: int

    backend_override: str
    backend: int


def resolve_backend(backend_override: str, *, is_win: bool, is_mac: bool, is_linux: bool) -> int:
    backend_map = {
        "any": cv2.CAP_ANY,
        "v4l2": getattr(cv2, "CAP_V4L2", cv2.CAP_ANY),
        "dshow": getattr(cv2, "CAP_DSHOW", cv2.CAP_ANY),
        "msmf": getattr(cv2, "CAP_MSMF", cv2.CAP_ANY),
        "avfoundation": getattr(cv2, "CAP_AVFOUNDATION", cv2.CAP_ANY),
        "gstreamer": getattr(cv2, "CAP_GSTREAMER", cv2.CAP_ANY),
    }

    if backend_override in backend_map:
        return backend_map[backend_override]

    if is_win:
        return getattr(cv2, "CAP_DSHOW", cv2.CAP_ANY)
    if is_mac:
        return getattr(cv2, "CAP_AVFOUNDATION", cv2.CAP_ANY)
    if is_linux:
        return getattr(cv2, "CAP_V4L2", cv2.CAP_ANY)
    return cv2.CAP_ANY


def load_settings() -> TrackerSettings:
    is_win = sys.platform.startswith("win")
    is_mac = sys.platform == "darwin"
    is_linux = sys.platform.startswith("linux")

    default_force_mjpg = "1" if is_linux else "0"
    default_force_size = "1" if is_linux else "0"

    default_capture_w = "1280" if is_linux else "640"
    default_capture_h = "720" if is_linux else "480"

    default_preview_w = "960" if is_linux else "640"
    default_preview_h = "540" if is_linux else "480"

    cam_index_env = _env_first("BHT_CAM_INDEX", "HTVA_CAM_INDEX", default="")
    cam_index = int(cam_index_env) if cam_index_env.isdigit() else None

    backend_override = _env_first("BHT_CAP_BACKEND", "HTVA_CAP_BACKEND", default="").lower()
    backend = resolve_backend(
        backend_override,
        is_win=is_win,
        is_mac=is_mac,
        is_linux=is_linux,
    )

    return TrackerSettings(
        is_win=is_win,
        is_mac=is_mac,
        is_linux=is_linux,

        udp_ip=_env_first("BHT_UDP_IP", "HTVA_UDP_IP", default="127.0.0.1"),
        udp_port=_env_int("BHT_UDP_PORT", "HTVA_UDP_PORT", default="5005"),
        ctrl_port=_env_int("BHT_CTRL_PORT", "HTVA_CTRL_PORT", default="5006"),

        send_hz=_env_float("BHT_SEND_HZ", "HTVA_SEND_HZ", default="60"),
        x_gain=_env_float("BHT_X_GAIN", "HTVA_X_GAIN", default="1.2"),
        y_gain=_env_float("BHT_Y_GAIN", "HTVA_Y_GAIN", default="1.0"),
        z_gain=_env_float("BHT_Z_GAIN", "HTVA_Z_GAIN", default="1.0"),
        show_preview=_env_bool("BHT_SHOW_PREVIEW", "HTVA_SHOW_PREVIEW", default="1"),

        force_mjpg=_env_bool("BHT_FORCE_MJPG", "HTVA_FORCE_MJPG", default=default_force_mjpg),
        force_preview_size=_env_bool("BHT_FORCE_SIZE", "HTVA_FORCE_SIZE", default=default_force_size),

        preview_w=_env_int("BHT_PREVIEW_W", "HTVA_PREVIEW_W", default=default_preview_w),
        preview_h=_env_int("BHT_PREVIEW_H", "HTVA_PREVIEW_H", default=default_preview_h),
        capture_w=_env_int("BHT_CAPTURE_W", "HTVA_CAPTURE_W", default=default_capture_w),
        capture_h=_env_int("BHT_CAPTURE_H", "HTVA_CAPTURE_H", default=default_capture_h),

        auto_fit_win_preview=_env_bool("BHT_WIN_AUTOFIT", "HTVA_WIN_AUTOFIT", default="1"),

        cam_index=cam_index,
        max_cam_try=6,

        backend_override=backend_override,
        backend=backend,
    )