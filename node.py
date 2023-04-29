import socket
import threading as th
import pickle
import sys
import time
import re

from merkel_tree import Merkel_tree, is_in_node

from hashlib import sha256

from datetime import datetime

import copy

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
        block["nonce"] = str(n)
        hx = hash_object(block)
        if hx[0:difficulty] == "0" * difficulty:
            return block
        n += 1

def represents_int(s):
    try: 
        int(s)
    except ValueError:
        return False
    else:
        return True


class Node:
    """
    Possède à la fois le code du client et du serveur (fait les deux).
    """

    def __init__(self):
        # Choose a random port to open the server on.
        self.time_elapsed = 100
        self.counter = 1
        self.address = "localhost"
        self.port = int(sys.argv[1])

        self.list_connections = []
        self.len_connections = 0
        # semaphore for minage
        self.v = th.Lock()

        print("On est sur l'adresse et le port suivant", self.address, self.port)
        self._listen_thread = th.Thread(target=self._listen)
        self._minage_thread = th.Thread(target=self.minage)

        self.transaction_file = "file"+str(self.port)+".txt"
        

        self.blockchain = []
        self.tmp_block = []


        if len(sys.argv)>2:
            self._connect(int(sys.argv[2]))
        else:
            print("no connection")
        self.run_thread()
        
        self._stop_event = th.Event()
        self.start = time.time()


    def run_thread(self):
        self._listen_thread.start()
        self._minage_thread.start()


    def read_transactions(self):
        lignes = []
        try:
            with open(self.transaction_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if len(re.findall("^.*\{$", line))!=1 and len(re.findall("^.*\}$", line))!=1 :
                        lignes.append(line.split(",")[0].split("\t")[1])
                f.close()
            return lignes
        except IOError:
            return lignes


    def _send_msg(self, socket, msg):
        socket.send(bytes(msg,"utf-8"))


    def _receive_msg(self, socket):
        msg = socket.recv(4096)
        return msg.decode("utf-8")


    def _listen(self):
        print("-----------------LISTEN")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.address, self.port))
            server_socket.listen()
            while not self._stop_event.is_set():
                connection, address = server_socket.accept()

                #receive a massage
                msg_from_connect1 = self._receive_msg(connection)
                if msg_from_connect1 == "CONNECT":

                    #send a message
                    self._send_msg(connection, f"LISTEN -> Accepted")

                    #receive a massage
                    msg_from_connect = self._receive_msg(connection)
                    
                    print(msg_from_connect)
                    port = msg_from_connect[69:74]
                    if represents_int(port):
                        self.list_connections.append(int(port))

                    b = th.Thread(target=self.broadcast_connexions)
                    b.start()
                    connection.close()

                elif msg_from_connect1 == "BROADCAST_CONNEXIONS":

                    #send a message
                    self._send_msg(connection, f"LISTEN -> Accepted")

                    #receive a massage
                    msg_from_connect = self._receive_msg(connection)
                    
                    #send a message
                    self._send_msg(connection, f"LISTEN -> Here my list of connections { self.list_connections }")

                    #receive a massage
                    msg_from_connect2 = self._receive_msg(connection)
                    print(msg_from_connect2)
                    #msg_from_connect2 = self._receive_msg(connection)[40:-1]
                    #print(msg_from_connect2.split(","))

                    connection.close()

                elif msg_from_connect1 == "CHECK_TRANSACTION":

                    #send a message
                    self._send_msg(connection, f"LISTEN -> Accepted")

                    #receive a massage
                    utxo = self._receive_msg(connection)

                    self.transactions = self.read_transactions()
                    print(self.transactions)

                    m_tree = Merkel_tree(self.transactions)

                    response = is_in_node(m_tree, utxo)

                    self._send_msg(connection, response)

                    connection.close()

                elif msg_from_connect1 == "RECEIVE_TRANSACTION":

                    #send a message
                    self._send_msg(connection, f"LISTEN -> Accepted")

                    #receive a massage
                    msg_from_wallet = self._receive_msg(connection)
                    self.broadcast_messages(msg_from_wallet)


                    self.v.acquire()
                    self.tmp_block.append(msg_from_wallet+"\n")
                    self.v.release()
                    connection.close()

                elif msg_from_connect1 == "BROADCAST_MESSAGES":
                    print("BROADCAST_MESSAGES")

                    #send a message
                    self._send_msg(connection, f"LISTEN -> Accepted")

                    #receive a massage
                    msg_from_connect = self._receive_msg(connection)
                    print(msg_from_connect)

                    #self.broadcast_messages(msg_from_connect)
                    
                    #f = open(self.transaction_file, 'a')
                    #f.write(msg_from_connect+"\n")
                    #f.close()

                    connection.close()

                elif msg_from_connect1 == "MINAGE":
                    print("MINAGE")

                    #send a message
                    self._send_msg(connection, f"LISTEN -> Accepted")

                    #receive a massage
                    msg_from_connect = self._receive_msg(connection)
                    print(msg_from_connect)

                    connection.close()

            print("connection is closed")


    def _connect(self, port):
        print("-----------------CONNECT")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            address = "localhost"
            client_socket.connect((address, port))

            self.list_connections.append(port)

            #send a message
            self._send_msg(client_socket,f"CONNECT")

            #receive a message
            msg = self._receive_msg(client_socket)
            if msg == "LISTEN -> Accepted":

                #send a message
                self._send_msg(client_socket,f"CONNECT -> thank you for accepting the connection from {self.address, self.port}!")


    def broadcast_connexions(self):
        # quand on se connecte à un noeud, le noeud nou sfournit sa liste de connexion
        # et on se connecte à tous ces autres neouds
        print("-----------------BROADCAST_CONNEXIONS")        
        for i in range(len(self.list_connections)):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                address = "localhost"
                port = int(self.list_connections[i])
                client_socket.connect((address, port))

                #send a message
                self._send_msg(client_socket,f"BROADCAST_CONNEXIONS")

                #receive a message
                msg = self._receive_msg(client_socket)
                if msg == "LISTEN -> Accepted":

                    #send a message
                    self._send_msg(client_socket,f"BROADCAST_CONNEXIONS -> thank you for accepting the connection from {self.address, self.port}!")

                    #receive a message
                    print(self._receive_msg(client_socket))

                    #send a message
                    self._send_msg(client_socket,f"BROADCAST_CONNEXIONS -> Here my list of connections { self.list_connections }")


    def broadcast_messages(self, message):
        # quand on se connecte à un noeud, le noeud nou sfournit sa liste de connexion
        # et on se connecte à tous ces autres neouds
        print("-----------------BROADCAST_MESSAGES")
        for i in range(len(self.list_connections)):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                address = "localhost"
                port = int(self.list_connections[i])
                client_socket.connect((address, port))

                #send a message
                self._send_msg(client_socket,f"BROADCAST_MESSAGES")

                #receive a message
                msg = self._receive_msg(client_socket)
                if msg == "LISTEN -> Accepted":

                    #send a message
                    self._send_msg(client_socket, message)


    # chauqe lapse de temps, on lance le minage
    # stocke toutes les transactions dans son block et il l'envoie à toutes ses connexions
    # Chercher sur le minage
    def minage(self):
        th.Timer(self.time_elapsed, self.minage).start()

        if len(self.tmp_block) > 0:
            self.v.acquire()
            tmp = copy.deepcopy(self.tmp_block)
            self.tmp_block = []
            self.v.release()

            now = datetime.now().strftime("%d%m%Y%H%M%S%f") #id du block
            dict_block = {"id":now, "UTXO": tmp}
            dict_block = compute_pow(dict_block)
            self.blockchain.append(dict_block)

            f = open(self.transaction_file, 'a')
            block = now+":{\n\tUTXO:{\n"
            f.write(block)

            for line in tmp:
                f.write("\t\t"+line)
                block=block+"\t\t"+line

            f.write("\t}\n\tnonce:{\n\t\t"+str(self.blockchain[-1].get("nonce"))+"\n\t}\n}\n")
            block=block+"\t}\n\tnonce:{\n\t\t"+str(self.blockchain[-1].get("nonce"))+"\n\t}\n}\n"

            f.close()
            
            print("-----------------MINAGE")
            for i in range(len(self.list_connections)):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                    address = "localhost"
                    port = int(self.list_connections[i])
                    client_socket.connect((address, port))

                    #send a message
                    self._send_msg(client_socket,f"MINAGE")

                    #receive a message
                    msg = self._receive_msg(client_socket)
                    if msg == "LISTEN -> Accepted":

                        #send a message
                        self._send_msg(client_socket, block)


n = Node()