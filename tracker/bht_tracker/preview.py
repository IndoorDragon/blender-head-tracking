import cv2

from .settings import TrackerSettings


WINDOW_NAME = "Blender Head Tracking — Webcam Tracker"


def setup_preview_window(settings: TrackerSettings) -> None:
    if not settings.show_preview:
        return

    try:
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        if settings.force_preview_size:
            cv2.resizeWindow(WINDOW_NAME, settings.preview_w, settings.preview_h)
    except Exception:
        pass


def auto_fit_preview_window_if_needed(
    *,
    frame_width: int,
    frame_height: int,
    settings: TrackerSettings,
    win_autofit_done: bool,
) -> bool:
    if not (
        settings.show_preview
        and settings.is_win
        and settings.auto_fit_win_preview
        and (not settings.force_preview_size)
        and (not win_autofit_done)
    ):
        return win_autofit_done

    try:
        cv2.resizeWindow(WINDOW_NAME, int(frame_width), int(frame_height))
    except Exception:
        pass

    return True


def draw_hud(frame, cam_idx: int, msg_line: str) -> None:
    source_label = "video file" if cam_idx == -1 else f"camera index: {cam_idx}"
    cv2.putText(
        frame,
        f"Source: {source_label}   (N=next, P=prev, R=recenter, Q=quit)",
        (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (50, 255, 50),
        2,
    )
    if msg_line:
        cv2.putText(
            frame,
            msg_line,
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (50, 255, 50),
            2,
        )


def draw_tracking_overlay(frame, *, minx: float, miny: float, maxx: float, maxy: float, cx: float, cy: float, x: float, y: float, z: float) -> None:
    h, w = frame.shape[:2]
    p1 = (int(minx * w), int(miny * h))
    p2 = (int(maxx * w), int(maxy * h))

    cv2.rectangle(frame, p1, p2, (0, 255, 0), 2)
    cv2.circle(frame, (int(cx * w), int(cy * h)), 5, (0, 255, 0), -1)
    cv2.putText(
        frame,
        f"x={x:+.2f} y={y:+.2f} z={z:+.2f}",
        (10, h - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2,
    )


def draw_no_face(frame) -> None:
    h, _w = frame.shape[:2]
    cv2.putText(
        frame,
        "No face detected",
        (10, h - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2,
    )


def show_preview(frame, *, cam_index: int, info_msg: str) -> None:
    draw_hud(frame, cam_index, info_msg)
    cv2.imshow(WINDOW_NAME, frame)