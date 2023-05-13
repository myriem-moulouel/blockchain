from datetime import datetime
from merkel_tree import Merkel_tree
from utils import *


class Block:
    def __init__(self, adress, UTXO, previous) -> None:
        now = datetime.now()
        self.id = now.strftime("%d%m%Y%H%M%S%f")
        self.UTXO = UTXO
        self.date = now.strftime("%d/%m/%Y %H:%M:%S")
        self.adress = adress
        self.previous = previous # hash du block précedant
        self.recompense = 6

        self.header = None # le hash de la racine de l'arbre de merkel        
        self.merkel_tree = None
        self.frais = 0

        self.nonce = None
        self.hash = None
        
    def set_attributs(self):
        self.merkel_tree = Merkel_tree(self.UTXO)
        self.header = self.merkel_tree.get_hash_block()
        for utxo in self.UTXO:
            self.frais += int(utxo.frais)
        

    def compute_pow(self):
        """
        Takes a block and returns it with the appropriate nonce.
        This nonce is computed with a Proof-of-Work algorithm.
        """
        n = 0
        while True:
            self.nonce = str(n)
            hx = hash_object(self)
            if hx[0:DIFFICULTY] == "0" * DIFFICULTY:
                self.hash = hx
                return 
            n += 1

    def __getstate__(self):
        state = {}
        state['id'] = self.id
        state['UTXO'] = pickle.dumps(self.UTXO)
        state['date'] = self.date
        state['adress'] = self.adress
        state['previous'] = self.previous
        state['recompense'] = self.recompense
        state['header'] = self.header
        #state['merkel_tree'] = pickle.dumps(self.merkel_tree)
        state['frais'] = self.frais
        state['nonce'] = self.nonce
        state['hash'] = self.hash
        return state

    def __setstate__(self, state):
        self.id = state['id']
        self.UTXO = pickle.loads(state['UTXO'])
        self.date = state['date']
        self.adress = state['adress']
        self.previous = state['previous']
        self.recompense = state['recompense']
        self.header = state['header']
        #self.merkel_tree = pickle.loads(state['merkel_tree'])
        self.frais = state['frais']
        self.nonce = state['nonce']
        self.hash = state['hash']

    def __str__(self):
        return str(self.__getstate__())


class BlockChain:
    def __init__(self, blocks) -> None:
        self.blocks = blocks

