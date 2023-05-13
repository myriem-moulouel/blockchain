import socket
import threading as th
import pickle
import sys
import time
from hashlib import sha256
from datetime import datetime
import copy


from merkel_tree import Merkel_tree, is_in_node
from wallet import UTXO
from blockchain import Block, BlockChain
from utils import *


class Node:
    """
    Couche P2P
    Possède à la fois le code du client et du serveur (fait les deux).
    """

    def __init__(self):
        self.pubkeys_file = "pubkeys.txt"

        # Choose a random port to open the server on.
        self.time_elapsed = 10
        self.counter = 1
        self.address = "localhost"
        self.port = int(sys.argv[1])

        self.list_connections = []
        self.len_connections = 0
        # semaphore for minage
        self.v = th.Lock()

        print("On est sur l'adresse et le port suivant", self.address, self.port)

        self.transaction_file = "file"+str(self.port)+".txt"
        self.blockchain = self.read_blockchain()

        self._listen_thread = th.Thread(target=self._listen)
        self._minage_thread = th.Thread(target=self.minage)

        self.tmp_block = []

        self.read_transactions()

        if len(sys.argv)>2:
            self._connect(int(sys.argv[2]))
        else:
            print("no connection")
        self.run_thread()
        
        self._stop_event = th.Event()
        self.start = time.time()


    def read_blockchain(self):
        try:
            list_blocks = []
            with open(self.transaction_file, 'rb') as f:
                while True:
                    try:
                        list_blocks.append(pickle.load(f))
                    except EOFError:
                        break
                f.close()

                return BlockChain(list_blocks)
                
        except FileNotFoundError:
            return BlockChain([])
        
    def read_pubkeys(self):
        try:
            wallet_adresses = {}
            with open(self.pubkeys_file, 'r') as f:
                for l in f:
                    composantes = l.split()
                    name = composantes[0]
                    n = composantes[1]
                    e = composantes[2]

                    wallet_adresses[name] = {"n": n, "e": e}
                    
                f.close()

                return wallet_adresses
                
        except FileNotFoundError:
            return {}

    def run_thread(self):
        self._listen_thread.start()
        self._minage_thread.start()

    def read_transactions(self):
        transactions = []
        for block in self.blockchain.blocks:
            utxo = block.UTXO
            for i in range(len(utxo)):
                transactions.append(utxo[i])
        return transactions

    def _send_msg(self, socket, msg):
        socket.send(bytes(msg,"utf-8"))

    def _send_object(self, socket, msg):
        socket.send(msg)

    def _receive_msg(self, socket):
        msg = socket.recv(4096)
        return msg.decode("utf-8")
    
    def _receive_object(self, socket):
        return pickle.loads(socket.recv(4096))

    def Unlock(self, utxo):
        pubkeys = self.read_pubkeys()

        #check if the utxo is valide
        name = utxo.src
        if name in pubkeys:
            signature = utxo.signature
            utxo.signature = None
            hash = hash_utxo(utxo.__getstate__())

            hashFromSignature = pow(signature, int(pubkeys[name]["e"]), int(pubkeys[name]["n"]))

            utxo.signature = signature

            if (hash == hashFromSignature) :
                print('utxo signature is valid')
                return True
            print('utxo signature is not valid')
            return False

        else:
            print('utxo signature is not valid')
            return False

    def compute_credit(self, name):
        credit = INIT_CREDIT
        blocks = self.blockchain.blocks
        for block in blocks:
            for utxo in block.UTXO:
                if utxo.src == name:
                    credit += -float(utxo.montant) - float(utxo.frais)
                if utxo.dest == name:
                    credit += float(utxo.montant)
        
        return credit

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
                    list_id = [tr.id for tr in self.transactions]
                    print(self.transactions, list_id)

                    m_tree = Merkel_tree(list_id)

                    response = is_in_node(m_tree, utxo)
                    if response =="1":
                        self._send_msg(connection, "transaction "+str(utxo)+" is in the block")
                    if response =="0":
                        self._send_msg(connection, "transaction "+str(utxo)+" is not in the block")

                    connection.close()

                elif msg_from_connect1 == "CHECK_CREDIT":

                    #send a message
                    self._send_msg(connection, f"LISTEN -> Accepted")

                    #receive the name of the wallet
                    name = self._receive_msg(connection)

                    credit = self.compute_credit(name)

                    self._send_msg(connection, str(credit))

                    connection.close()

                elif msg_from_connect1 == "RECEIVE_TRANSACTION":

                    #send a message
                    self._send_msg(connection, f"LISTEN -> Accepted")

                    #receive a massage
                    msg_from_wallet = self._receive_object(connection)
                    print("i'm here")

                    # P2PK Unlock
                    reponse_script = self.Unlock(msg_from_wallet)

                    # If the signature is valid
                    if reponse_script:
                        credit = self.compute_credit(msg_from_wallet.src)
                        
                        # if credit sufficient
                        if (credit - float(msg_from_wallet.montant) - float(msg_from_wallet.frais)) > 0:
                            print("utxo valid")
                            self.broadcast_messages(msg_from_wallet)

                            self.v.acquire()
                            self.tmp_block.append(msg_from_wallet)
                            self.v.release()
                        else:
                            print("utxo not valid")
                    
                    connection.close()

                elif msg_from_connect1 == "BROADCAST_MESSAGES":
                    print("BROADCAST_MESSAGES")

                    #send a message
                    self._send_msg(connection, f"LISTEN -> Accepted")

                    #receive a massage
                    msg_from_connect = self._receive_object(connection)

                    # P2PK Unlock
                    reponse_script = self.Unlock(msg_from_connect)

                    # If the signature is valid
                    if reponse_script:
                        credit = self.compute_credit(msg_from_connect.src)
                        
                        # if credit sufficient
                        if (credit - float(msg_from_connect.montant) - float(msg_from_connect.frais)) > 0:
                            print("utxo valid")
                            print(msg_from_connect)


                            # check wether the utxo received has already been sent to this node
                            self.transactions = self.read_transactions()
                            list_id = [tr.id for tr in self.transactions]

                            for tr in self.tmp_block:
                                list_id.append(tr.id)


                            m_tree = Merkel_tree(list_id)

                            response = is_in_node(m_tree, msg_from_connect.id)

                            print("----------------")
                            print("check wether the utxo received has already been sent to this node")
                            print("----------------")
                            if is_in_node(m_tree, msg_from_connect.id) == "0":
                                self.broadcast_messages(msg_from_connect)

                                self.v.acquire()
                                self.tmp_block.append(msg_from_connect)
                                self.v.release()



                    connection.close()

                elif msg_from_connect1 == "MINAGE":
                    print("MINAGE")

                    #send a message
                    self._send_msg(connection, f"LISTEN -> Accepted")

                    #receive a block
                    block = self._receive_object(connection)

                    # verify the hash code
                    hash_send = block.hash
                    block.hash = None
                    
                    hash_computed = hash_object(block)
                    block.hash = hash_send
                    
                    if (hash_send == hash_computed) & (hash_send[0:DIFFICULTY] == "0"*DIFFICULTY):
                        print("block : Hash verified")
                        
                        self.transactions = self.read_transactions()
                        list_id = [tr.id for tr in self.transactions]

                        print("________________________")
                        print("those are the transactions in the blocks")
                        print(self.transactions, list_id)
                        print("\n")

                        m_tree = Merkel_tree(list_id)

                        block_verified = True
                        for utxo in block.UTXO:
                            response = is_in_node(m_tree, utxo.id)
                            if response=="1":
                                block_verified = False
                        if block_verified:
                            print("block : verified")
                        else:
                            print("At least, one transaction already exists")
                    else:
                        print("Hash of the block is not valid")


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

    def broadcast_messages(self, utxo):
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
                    self._send_object(client_socket, pickle.dumps(utxo))


    # chauqe lapse de temps, on lance le minage
    # stocke toutes les transactions dans son block et il l'envoie à toutes ses connexions
    # Chercher sur le minage
    def minage(self):
        th.Timer(self.time_elapsed, self.minage).start()

        if len(self.tmp_block) > 0:


            self.v.acquire()
            # list des UTXO recues
            tmp = copy.deepcopy(self.tmp_block)
            self.tmp_block = []
            self.v.release()

            try:
                previous = self.blockchain.blocks[-1].hash
            except IndexError:
                previous = None
            block = Block(self.port, tmp, previous)
            block.set_attributs()
            block.compute_pow()

            self.blockchain.blocks.append(block)

            f = open(self.transaction_file, 'ab')
            pickle.dump(block,f)
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
                        print("block sent")
                        self._send_object(client_socket, pickle.dumps(block))

if __name__ == '__main__':
    n = Node()