import hashlib

def sha256(string):
    # Create a new SHA-256 hash object
    return hashlib.sha256(string.encode()).hexdigest()

def sha256_sum(hash1, hash2):
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
        #self.length = len(str(s))
        self.hash = sha256(transaction) # a hashcode that refers to the transaction (sha256)
        self.parent = None
        self.transaction = transaction # a json file that contains all the informations about the transaction
     
    def __str__(self):
        return "("+str(self.transaction)+")"

class Merkel_node(Merkel_leaf):
    def __init__(self) -> None:
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
        return self.root_node.hash

    def __str__(self):
        return self.root_node.__str__()

"""
Simulation of the behaviour of a person that demand if his transaction is included in the block

"""
def is_in_node(tree: Merkel_tree, transaction):
    
    hash_t = sha256(transaction)

    hash_list = tree.transaction_in_merkle(hash_t)

    res = hash_t

    for i in range(len(hash_list)) :
        res = sha256_sum(res, hash_list[i])

    #print("\nhash of the transaction =", hash_t)
    #print("\nres of computation = ",res)
    #print("\nblock hashcode header = ", tree.get_hash_block())

    if res == tree.get_hash_block():
        #print("transaction is in the block")
        return "transaction "+str(transaction)+" is in the block"
    else:
        #print("transaction is not in the block")
        return "transaction "+str(transaction)+" is not in the block"


# ================== MAIN CODE ============

#liste_transaction = ["t1", "t2", "t3", "t4", "t5", "t6", "t7","t8"]
#tree = Merkel_tree(liste_transaction)

#transaction = "t8"
#sis_in_node(tree, transaction)
