import socket
import concurrent.futures
import argparse


def scan_port(host: str, port: int) -> None:
    scan_tcp_port(host, port)
    scan_udp_port(host, port)


def scan_tcp_port(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        try:
            sock.connect((host, port))
            print(f"TCP {port} is open")
        except socket.err:
            pass


def scan_udp_port(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(5)
        try:
            sock.sendto(b"abc", (host, port))
            data, _ = sock.recvfrom(1024)
            print(f"UDP {port} is open")
        except socket.error:
            pass


def get_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Port scanner')

    parser.add_argument("host", type=str, help="host")
    parser.add_argument("min_port", type=int, help="Minimum port number")
    parser.add_argument("max_port", type=int, help="Maximum port number")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_argument_parser()
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        port_tasks = [executor.submit(scan_port, args.host, port) for port in range(args.min_port, args.max_port + 1)]
