import time

import cv2
import mediapipe as mp

from .app_paths import build_paths, build_video_search_report
from .camera import open_camera_auto, try_open_cam
from .config_store import load_config, remove_pid_file, save_config, write_pid_file
from .mediapipe_runner import create_landmarker, validate_model_path
from .preview import (
    auto_fit_preview_window_if_needed,
    draw_no_face,
    draw_tracking_overlay,
    setup_preview_window,
    show_preview,
)
from .settings import load_settings
from .sockets import check_quit_signal, create_control_socket, create_pose_socket, send_pose


def _parse_saved_camera_index(config: dict) -> int | None:
    value = config.get("camera_index")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _clamp(value: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def run_tracker() -> None:
    settings = load_settings()
    paths = build_paths()

    validate_model_path(paths)

    pose_sock = create_pose_socket()
    ctrl_sock = create_control_socket(settings.ctrl_port)

    config = load_config(paths.config_path)
    cfg_cam = _parse_saved_camera_index(config)
    preferred_cam = settings.cam_index if settings.cam_index is not None else cfg_cam

    cap = None
    cam_index = 0
    using_video_file = False

    cap, cam_index = open_camera_auto(preferred_cam, settings)

    if cap.isOpened():
        using_video_file = False
    else:
        try:
            cap.release()
        except Exception:
            pass

        if paths.video_file is not None:
            cap = cv2.VideoCapture(str(paths.video_file))
            if not cap.isOpened():
                raise RuntimeError(f"Found fallback video but could not open it: {paths.video_file}")
            cam_index = -1
            using_video_file = True
        else:
            searched = build_video_search_report(paths)
            raise RuntimeError(
                "Could not open any webcam and fallback video was not found.\n"
                f"Searched for test.mp4 in:\n{searched}"
            )

    config["camera_index"] = cam_index
    save_config(paths.config_path, config)

    write_pid_file(paths.pid_path)

    setup_preview_window(settings)

    win_autofit_done = False
    baseline_set = False
    base_x = 0.0
    base_y = 0.0
    base_size = 0.0

    last_send = 0.0
    period = 1.0 / max(1.0, settings.send_hz)

    if using_video_file and paths.video_file is not None:
        info_msg = f"Using fallback video: {paths.video_file.name}"
    else:
        info_msg = f"Using camera {cam_index} (saved to {paths.config_path.name})"

    try:
        with create_landmarker(paths.model_path) as landmarker:
            start_time = time.time()

            while True:
                if check_quit_signal(ctrl_sock):
                    break

                ok, frame = cap.read()

                if (not ok or frame is None) and using_video_file:
                    try:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    except Exception:
                        pass
                    ok, frame = cap.read()

                if not ok or frame is None:
                    continue

                h, w = frame.shape[:2]

                win_autofit_done = auto_fit_preview_window_if_needed(
                    frame_width=w,
                    frame_height=h,
                    settings=settings,
                    win_autofit_done=win_autofit_done,
                )

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

                timestamp_ms = int((time.time() - start_time) * 1000)
                result = landmarker.detect_for_video(mp_image, timestamp_ms)

                if result.face_landmarks:
                    lms = result.face_landmarks[0]
                    xs = [p.x for p in lms]
                    ys = [p.y for p in lms]

                    minx, maxx = min(xs), max(xs)
                    miny, maxy = min(ys), max(ys)

                    cx = (minx + maxx) * 0.5
                    cy = (miny + maxy) * 0.5
                    face_size = max(maxx - minx, maxy - miny)

                    if not baseline_set:
                        base_x = cx
                        base_y = cy
                        base_size = face_size
                        baseline_set = True

                    x = (cx - base_x) * 2.0 * settings.x_gain
                    y = (cy - base_y) * 2.0 * settings.y_gain

                    z = 0.0
                    if base_size > 1e-6:
                        z = ((face_size / base_size) - 1.0) * settings.z_gain

                    x = _clamp(x)
                    y = _clamp(y)
                    z = _clamp(z)

                    now = time.time()
                    if now - last_send >= period:
                        send_pose(pose_sock, settings.udp_ip, settings.udp_port, x, y, z)
                        last_send = now

                    if settings.show_preview:
                        draw_tracking_overlay(
                            frame,
                            minx=minx,
                            miny=miny,
                            maxx=maxx,
                            maxy=maxy,
                            cx=cx,
                            cy=cy,
                            x=x,
                            y=y,
                            z=z,
                        )
                else:
                    if settings.show_preview:
                        draw_no_face(frame)

                if settings.show_preview:
                    show_preview(frame, cam_index=cam_index, info_msg=info_msg)
                    info_msg = ""

                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        break
                    elif key == ord("r"):
                        baseline_set = False
                        info_msg = "Recentered baseline"
                    elif key in (ord("n"), ord("p")) and not using_video_file:
                        step = 1 if key == ord("n") else -1
                        next_idx = (cam_index + step) % settings.max_cam_try

                        new_cap = try_open_cam(next_idx, settings)
                        if new_cap:
                            cap.release()
                            cap = new_cap
                            cam_index = next_idx
                            baseline_set = False
                            win_autofit_done = False

                            config["camera_index"] = cam_index
                            save_config(paths.config_path, config)

                            info_msg = f"Switched to camera {cam_index} (saved)"
                        else:
                            info_msg = f"Camera {next_idx} unavailable"

    finally:
        try:
            if cap is not None:
                cap.release()
        except Exception:
            pass

        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

        try:
            ctrl_sock.close()
        except Exception:
            pass

        try:
            pose_sock.close()
        except Exception:
            pass

        remove_pid_file(paths.pid_path)