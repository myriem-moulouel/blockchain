import socket
import threading as th
import pickle
import sys

from hashlib import sha256

from datetime import datetime

import struct

from Crypto.PublicKey import RSA


def hash_utxo(obj: any) -> str:
    """
    Returns a hexdigest of the value passed.
    """
    return int.from_bytes(sha256(pickle.dumps(obj)).digest(), byteorder="big")


class UTXO:
    
    def __init__(self, src, dest, montant):
        now = datetime.now()
        self.id = now.strftime("%d%m%Y%H%M%S%f")
        self.src = src
        self.dest = dest
        self.montant = montant
        self.date = now.strftime("%d/%m/%Y %H:%M:%S")
        self.frais = float(montant)*0.01
        self.signature = None

        self.id = self.id+str(hash_utxo(self))

    def __getstate__(self):
        return {'id': self.id, 'src': self.src, 'dest': self.dest, 'montant': self.montant, 'date': self.date, 'frais': self.frais, 'signature': self.signature}

    def __setstate__(self, state):
        self.id = state['id']
        self.src = state['src']
        self.dest = state['dest']
        self.montant = state['montant']
        self.date = state['date']
        self.frais = state['frais']
        self.signature = state['signature']

    def __str__(self):
        return str(self.__getstate__())




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

        self.pubkeys_file = "pubkeys.txt"
        self.privkey_file = "priv_"+self.name+".txt"

        pubkeys = self.read_pubkeys()
        privkeys = self.read_privkeys()


        if (self.name in pubkeys) and (self.name in privkeys):
            self.pubkey = {"n": pubkeys[self.name]["n"], "e":pubkeys[self.name]["e"]}
            self.privkey = {"n": privkeys[self.name]["n"], "d":privkeys[self.name]["d"]}
        else:

            (self.pubkey, self.privkey) = self.create(self.name)


        todo = input("write : 'send' OR 'check' OR 'credit': ") # choose to send an UTXO or check UTXO existance

        if todo == "send":
            self.push_utxo()
            self.send_UTXO()

        elif todo == "check":
            self.check_UTXO()

        elif todo == "credit":
            self.check_credit()



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
        
    def read_privkeys(self):
        try:
            wallet_privkey = {}
            with open(self.privkey_file, 'r') as f:
                l = f.readline()
                composantes = l.split()
                name = composantes[0]
                n = composantes[1]
                d = composantes[2]

                wallet_privkey[name] = {"n": n, "d": d}
                    
                f.close()

                return wallet_privkey
                
        except FileNotFoundError:
            return {}



    def _send_msg(self, socket, msg):
        socket.send(bytes(msg,"utf-8"))

    def _send_utxo(self, socket, msg):
        socket.send(msg)

    def _receive_msg(self, socket):
        msg = socket.recv(4096)
        return msg.decode("utf-8")

    def Lock(self):
        hash = hash_utxo(self.utxo.__getstate__())
        self.utxo.signature = pow(hash, int(self.privkey["d"]), int(self.privkey["n"]))

    def create(self, name):
        """create private and public keys if they don't exist"""
        pubkeys = self.read_pubkeys()
        if not(name in pubkeys):

            # If the wallet doesn't exist, create it
            keyPair = RSA.generate(bits=1024)
            pubkey = {"n": keyPair.n, "e":keyPair.e}
            privkey = {"n": keyPair.n, "d":keyPair.d}

            f = open(self.pubkeys_file, 'a')
            f.write(name+" "+str(pubkey["n"])+" "+str(pubkey["e"])+"\n")
            f.close()

            f = open("priv_"+name+".txt", 'a')
            f.write(name+" "+str(privkey["n"])+" "+str(privkey["d"])+"\n")
            f.close()
            return (pubkey, privkey)



    # envoyer une transaction
    def push_utxo(self):

        Name_dest = input("Put the name of the wallet to sand money : ")
        montant = input("Put the amount : ")
        self.utxo = UTXO(self.name, Name_dest, montant)
        self.create(Name_dest)

    def send_UTXO(self):
        print("-----------------RECEIVE_TRANSACTION")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            address = "localhost"
            client_socket.connect((address, int(self.port_dest)))

            #send a message
            self._send_msg(client_socket,f"RECEIVE_TRANSACTION")

            #receive a message
            msg = self._receive_msg(client_socket)
            if msg == "LISTEN -> Accepted":

                self.Lock()
                print("UTXO desc : \n",self.utxo)
                #send a message
                self._send_utxo(client_socket, pickle.dumps(self.utxo))

    def check_credit(self):
        print("-----------------CHECK_CREDIT")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            address = "localhost"
            client_socket.connect((address, int(self.port_dest)))

            #send a message
            self._send_msg(client_socket,f"CHECK_CREDIT")

            #receive a message
            msg = self._receive_msg(client_socket)
            if msg == "LISTEN -> Accepted":

                #send a name of the wallet
                self._send_msg(client_socket, self.name)

                msg = self._receive_msg(client_socket)

                print("The credit of "+self.name+"= "+msg)

    def check_UTXO(self):
        id = input("Put the id of the transacation : ")
        print("-----------------CHECK_TRANSACTION")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            address = "localhost"
            client_socket.connect((address, int(self.port_dest)))

            #send a message
            self._send_msg(client_socket,f"CHECK_TRANSACTION")

            #receive a message
            msg = self._receive_msg(client_socket)
            if msg == "LISTEN -> Accepted":

                #send a message
                self._send_msg(client_socket, id)

                msg = self._receive_msg(client_socket)

                print(msg)



if __name__ == '__main__':
    n = Wallet()