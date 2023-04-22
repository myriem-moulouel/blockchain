import socket
import threading as th
import pickle
import sys

from hashlib import sha256

from datetime import datetime





class UTXO():
    
    def __init__(self, src, dest, montant, frais):
        now = datetime.now()
        self.id = now.strftime("%d%m%Y%H%M%S%f")
        self.src = src
        self.dest = dest
        self.montant = montant
        self.date = now.strftime("%d/%m/%Y %H:%M:%S")
        self.frais = frais

    def print_id(self):
        print(self.id)
        print(self.date)


class Wallet:
    """
    Possède à la fois le code du client et du serveur (fait les deux).
    """

    def __init__(self):
        # Choose a random port to open the server on.
        self.address = "localhost"
        self.port = int(sys.argv[1])
        

        self.port_dest = sys.argv[2]
        self.name = sys.argv[3]
        
        self.message = ""

        todo = input("write : 'send' OR 'check' : ") # choose to send an UTXO or check UTXO existance

        if todo == "send":
            self.push_utxo()
            self.send_UTXO(int(self.port_dest))

        elif todo == "check":
            self.check_UTXO(int(self.port_dest))


    def _send_msg(self, socket, msg):
        socket.send(bytes(msg,"utf-8"))


    def _receive_msg(self, socket):
        msg = socket.recv(4096)
        return msg.decode("utf-8")



    # envoyer une transaction
    def push_utxo(self):

        Name_dest = input("Put the name of the wallet to sand money : ")
        montant = input("Put the amount : ")
        utxo = UTXO(self.name, Name_dest, montant, 0)
        self.message = str(utxo.id)+", "+str(utxo.src)+", "+str(utxo.dest)+", "+str(utxo.montant)+", "+str(utxo.date)+", "+str(utxo.frais)

    def send_UTXO(self, port):
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

    def check_UTXO(self, port):
        id = input("Put the id of the transacation : ")
        print("-----------------CHECK_TRANSACTION")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            address = "localhost"
            client_socket.connect((address, port))

            #send a message
            self._send_msg(client_socket,f"CHECK_TRANSACTION")

            #receive a message
            msg = self._receive_msg(client_socket)
            if msg == "LISTEN -> Accepted":

                #send a message
                self._send_msg(client_socket, id)

                msg = self._receive_msg(client_socket)

                print(msg)


n = Wallet()