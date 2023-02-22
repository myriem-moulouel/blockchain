import socket
import threading as th
import pickle
import sys

class Wallet():
    def __init__(self) -> None:
        self.Name = int(sys.argv[1])
        self.port1 = int(sys.argv[2])  # connexion port of the wallet
        self.port2 = int(sys.argv[3])  # Connexion port to a node


    # Se connecter sur un noeud du port2
    def _connect(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            address = "localhost"
            client_socket.connect((address, self.port2))

            #receive a message
            print(self._receive_msg(client_socket))

            #send a message
            self._send_msg(client_socket,f" I'm the wallet {self.Name}, thank you for accepting the connection from {self.address, self.port}!")
            

    # envoyer une transaction
    def push_utxo(self, Name2, montant):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            address = "localhost"
            client_socket.connect((address, self.port2))

            #send a message
            self._send_msg(client_socket,f"Sending {montant} to {Name2}")

    def get_sold(self):
        # Calculer les UTXO sur la blockchain
        #
