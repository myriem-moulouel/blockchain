import hashlib

import pickle

from wallet import UTXO



def sha256(string):
    # Create a new SHA-256 hash object
    return hashlib.sha256(string.encode()).hexdigest()



def sha256(obj: any) -> str:
    """
    Returns a hexdigest of the value passed.
    """
    return hashlib.sha256(pickle.dumps(obj)).hexdigest()



def sha256_sum(hash1, hash2):
    """
    Inputs : 2 hashes 
    Output : 1 hash that represent the sum of the two ones
    """
    # Convert the input hashes to integers
    int1 = int(hash1, 16)
    int2 = int(hash2, 16)
    # Add the integers together
    int_sum = int1 + int2
    # Convert the result back to a hash
    hex_sum = hex(int_sum)[2:]
    sha = hashlib.sha256()
    sha.update(hex_sum.encode())
    return sha.hexdigest()


class Merkel_leaf():
    def __init__(self, transaction):
        """
        The merkle leaf structure 
        hash : the hash of the transaction
        transaction : 
        """
        self.hash = sha256(transaction) # a hashcode that refers to the transaction (sha256)
        self.parent = None
        self.transaction = transaction # id of the transaction
     
    def __str__(self):
        return "("+str(self.transaction)+")"

class Merkel_node(Merkel_leaf):
    def __init__(self) -> None:
        """
        A merkle node structure 

        """
        self.left = None
        self.right = None
        self.hash = None
        self.parent = None

    
    def _initialise(self, left, right):
        left.parent = self
        right.parent = self
        self.left = left
        self.right = right
        self.hash = sha256_sum(left.hash, right.hash)
        


    def __str__(self):
        result = "|  "+self.left.__str__() + "[" + str(f"node") + "]" + self.right.__str__()+"  |"

        return result

class Merkel_tree(Merkel_node):
    def __init__(self, UTXO) -> None:
        self.dict_hash_to_addr = {}
        self.root_node = None
        self.__initialise(UTXO)
    

    def __initialise(self, UTXO: list):
        # print(UTXO)
        if len(UTXO) > 0:
            liste_leafs = [Merkel_leaf( UTXO[i]) for i in range(len(UTXO))] 
            for leaf in liste_leafs:
                # store the address of the leaf, to be able to jump into it, and then make the ascent until we reach the root
                self.dict_hash_to_addr[leaf.hash] = leaf

            liste_nodes = liste_leafs
            liste_a_traiter = []
            

            while (liste_a_traiter != None):
                liste_a_traiter = []

                while (len(liste_nodes) > 1):
                    left = liste_nodes.pop(0) # pop the first elem
                    right = liste_nodes.pop(0) # pop the second elem
                    # Create the node that represent the concatenation of the 2 nodes, and add it to the list 
                    racine = Merkel_node()
                    racine._initialise(left, right)
                    liste_a_traiter.append(racine)
                    
                if(len(liste_nodes) == 1):
                    last_elem = liste_nodes.pop(0)
                    liste_a_traiter.append(last_elem)
                
                liste_nodes = liste_a_traiter

                if len(liste_nodes) == 1:
                    self.root_node = liste_nodes[0]
                    liste_a_traiter = None
            
    
    def transaction_in_merkle(self, hash_transaction):
        if hash_transaction not in self.dict_hash_to_addr.keys():
            return []

        leaf_transaction = self.dict_hash_to_addr[hash_transaction]
        iterator = leaf_transaction

        hash_list = []

        while iterator.parent != None:
            parent = iterator.parent
            if parent.left == iterator:
                hash_list.append(parent.right.hash)
            else:
                hash_list.append(parent.left.hash)
            
            iterator = parent

        return hash_list
    

    def get_hash_block(self):
        if self.root_node:
            return self.root_node.hash
        else:
            return None

    def __str__(self):
        return self.root_node.__str__()


def is_in_node(tree: Merkel_tree, transaction):
    """
    Input : transaction , Merkel_tree
    Output : char => 1 if the transaction is in the block
             char => 0 if the transaction is'nt in the block
    """
    
    hash_t = sha256(transaction)

    hash_list = tree.transaction_in_merkle(hash_t)

    res = hash_t

    for i in range(len(hash_list)) :
        res = sha256_sum(res, hash_list[i])
    
    if res == tree.get_hash_block():
        return "1"
    else:
        return "0"


# ================== MAIN CODE ============
"""
Simulation of the behaviour of a person that demand if his transaction is included in the block
"""

#liste_transaction = ["t1", "t2", "t3", "t4", "t5", "t6", "t7","t8"]
#tree = Merkel_tree(liste_transaction)

#transaction = "t8"
#sis_in_node(tree, transaction)
