import socket
import threading as th
import pickle

from hashlib import sha256


def is_local_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            return s.connect_ex(("localhost", port)) == 0
        except socket.gaierror:
            return False


def get_available_port() -> int | None:
    """
    Returns the first available local port available.
    By local, we mean on the primary network interface.
    """
    for p in range(1025, 65536):
        if not is_local_port_in_use(p):
            return p


def get_primary_ip_address() -> str:
    """
    Gets the IP address of the interface used to connect to the internet.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # doesn't have to be reachable
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]


def hash_object(obj: any) -> str:
    """
    Returns a hexdigest of the value passed.
    """
    return sha256(pickle.dumps(obj)).hexdigest()


def compute_pow(block: dict, difficulty: int = 5) -> dict:
    """
    Takes a block and returns it with the appropriate nonce.
    This nonce is computed with a Proof-of-Work algorithm.
    """
    n = 0
    while True:
        block["nonce"] = n
        hx = hash_object(block)
        if hx[0:difficulty] == "0" * difficulty:
            return block
        n += 1


class Node:
    """
    Possède à la fois le code du client et du serveur (fait les deux).


    """

    known_peers: list[str] = []

    def __init__(self):
        # Choose a random port to open the server on.
        self.address = get_primary_ip_address()
        self.port = get_available_port()
        self.open_server(self.port)
        self._stop_event = th.Event()
        self._listen_thread = th.Thread(target=self._listen)

    def open_server(self, port: int):
        self._listen_thread.start()

    def _receive_all(
            self, sock: socket.socket, address_check: str | None = None
    ) -> tuple[bytes, tuple[str, int]]:
        """
        Receives all parts of a network-sent message.
        Takes a socket object and returns a tuple with
        (1) the complete message as bytes
        (2) a tuple with (1) the address and (2) distant port of the sender.
        """
        data = bytes()
        while True:
            part, addr = sock.recvfrom(4096)
            if address_check:
                if addr == address_check:
                    data += part
            else:
                data += part
            if len(part) < 4096:
                # Either 0 or end of data
                break
        return data, addr

    def _listen(self):
        with socket.socket() as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.address, self.port))
            server_socket.listen()
            while not self._stop_event.is_set():
                connection, address = server_socket.accept()
                raw_request, _ = self._receive_all(connection, address)
                try:
                    request = Request.from_bytes(raw_request)
                except pydantic.ValidationError:
                    pass
                else:
                    handle_queue.put((request, address))
                connection.close()
