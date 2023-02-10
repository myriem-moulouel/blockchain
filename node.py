import socket
import threading as th
import pickle
import sys

from hashlib import sha256

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
        self.address = "localhost"
        self.port = int(sys.argv[1])

        self.list_adresses = []
        self.list_connections = set()

        print("On est sur l'adresse et le port suivant", self.address, self.port)
        self._listen_thread = th.Thread(target=self._listen)
        if len(sys.argv)>2:
            self._connect(int(sys.argv[2]))
        else:
            print("no connection")
        self.run_thread()
        
        self._stop_event = th.Event()
        


    def run_thread(self):
        self._listen_thread.start()


    def _send_msg(self, socket, msg):
        socket.send(bytes(msg,"utf-8"))


    def _receive_msg(self, socket):
        msg = socket.recv(4096)
        return msg.decode("utf-8")


    def _listen(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.address, self.port))
            server_socket.listen()
            while not self._stop_event.is_set():
                connection, address = server_socket.accept()
                print(f"connection from{address} has been established")
                self.list_adresses.append(address)
                self.list_connections.add(connection)
                #send a message
                self._send_msg(connection, f"You're connected to {self.address, self.port}")
                
                #receive a massage
                print(self._receive_msg(connection))

            for connection in self.list_connections:
                connection.close()

            print("connection is closed")


    def _connect(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            address = "localhost"
            client_socket.connect((address, port))

            self.list_adresses.append((address, port))
            self.list_connections.add(client_socket)
            #receive a message
            print(self._receive_msg(client_socket))
            #send a message
            self._send_msg(client_socket,f"thank you for accepting the connection from {self.address, self.port}!")
        


n = Node()