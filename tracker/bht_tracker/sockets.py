import socket


def create_pose_socket() -> socket.socket:
    return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def create_control_socket(ctrl_port: int) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    sock.bind(("127.0.0.1", ctrl_port))
    return sock


def check_quit_signal(ctrl_sock: socket.socket) -> bool:
    try:
        data, _addr = ctrl_sock.recvfrom(128)
        return data.strip().upper() == b"QUIT"
    except BlockingIOError:
        return False
    except Exception:
        return False


def send_pose(sock: socket.socket, udp_ip: str, udp_port: int, x: float, y: float, z: float) -> None:
    msg = f"{x:.4f} {y:.4f} {z:.4f}".encode("utf-8")
    sock.sendto(msg, (udp_ip, udp_port))