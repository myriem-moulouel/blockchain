import socket


def is_local_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            return s.connect_ex(("localhost", port)) == 0
        except socket.gaierror:
            return False


def get_available_port() -> int:
    """
    Returns the first available local port available.
    By local, we mean on the primary network interface.
    """
    for p in range(1025, 65536):
        if not is_local_port_in_use(p):
            return p
    else:
        raise Exception("Could not find any available port.")


def get_primary_ip_address() -> str:
    """
    Gets the IP address of the interface used to connect to the internet.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # doesn't have to be reachable
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
