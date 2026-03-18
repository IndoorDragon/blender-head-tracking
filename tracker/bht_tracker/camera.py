import cv2

from .settings import TrackerSettings


def configure_capture(cap: cv2.VideoCapture, settings: TrackerSettings) -> None:
    """
    Apply camera settings.

    IMPORTANT:
    - On Linux/V4L2, forcing size + MJPG often fixes black frames.
    - On Windows, forcing MJPG/size can slow camera negotiation, so defaults are OFF there.
      (But you can still force it via env vars if needed.)
    """
    if settings.force_preview_size:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(settings.capture_w))
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(settings.capture_h))

    if settings.force_mjpg:
        try:
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        except Exception:
            pass

    try:
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    except Exception:
        pass


def try_open_cam(index: int, settings: TrackerSettings) -> cv2.VideoCapture | None:
    """
    Try to open a camera index with:
    1) chosen platform backend
    2) CAP_ANY fallback
    """
    cap = cv2.VideoCapture(index, settings.backend)
    if cap.isOpened():
        configure_capture(cap, settings)
        return cap
    cap.release()

    cap = cv2.VideoCapture(index, cv2.CAP_ANY)
    if cap.isOpened():
        configure_capture(cap, settings)
        return cap
    cap.release()

    return None


def open_camera_auto(preferred: int | None, settings: TrackerSettings) -> tuple[cv2.VideoCapture, int]:
    if preferred is not None:
        cap = try_open_cam(preferred, settings)
        if cap:
            return cap, preferred

    for idx in range(settings.max_cam_try):
        cap = try_open_cam(idx, settings)
        if cap:
            return cap, idx

    if settings.is_linux:
        cap = cv2.VideoCapture("/dev/video0", settings.backend)
        if cap.isOpened():
            configure_capture(cap, settings)
            return cap, 0
        cap.release()

        cap = cv2.VideoCapture("/dev/video0", cv2.CAP_ANY)
        if cap.isOpened():
            configure_capture(cap, settings)
            return cap, 0
        cap.release()

    cap = cv2.VideoCapture(0, cv2.CAP_ANY)
    if cap.isOpened():
        configure_capture(cap, settings)
    return cap, 0