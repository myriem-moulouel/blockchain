import socket
import threading as th
import pickle
import sys

from hashlib import sha256

class Wallet:
    """
    Possède à la fois le code du client et du serveur (fait les deux).
    """

    def __init__(self):
        # Choose a random port to open the server on.
        self.address = "localhost"
        self.port = int(sys.argv[1])

        self.port_dest = sys.argv[2]
        self.message = sys.argv[3]


        self._connect(int(sys.argv[2]))

    def _send_msg(self, socket, msg):
        socket.send(bytes(msg,"utf-8"))


    def _receive_msg(self, socket):
        msg = socket.recv(4096)
        return msg.decode("utf-8")


    

    def _connect(self, port):
        print("-----------------RECEIVE_TRANSACTION")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            address = "localhost"
            client_socket.connect((address, port))

            #send a message
            self._send_msg(client_socket,f"RECEIVE_TRANSACTION")

            #receive a message
            msg = self._receive_msg(client_socket)
            if msg == "LISTEN -> Accepted":

                #send a message
                self._send_msg(client_socket, self.message)



n = Wallet()
