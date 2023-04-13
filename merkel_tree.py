"""
Implementation of the Merkle Tree.

Documentation:
https://en.bitcoin.it/wiki/Protocol_documentation#Merkle_Trees
"""

from __future__ import annotations

from typing import Optional

from blockchain.crypt import hash_object


def concat(h1: str, h2: str) -> str:
    return hash_object(h1 + h2)


class Leaf:
    """A leaf of the tree is a transaction.

    Attributes
    ----------
    hash : str
        The hash of the transaction
    parent : Optional[MerkleNode]
        The parent of the leaf
    transaction : str
        A JSON document containing the information about the transaction
    """

    def __init__(self, transaction: dict):
        self.hash: str = hash_object(transaction)
        self.parent: Optional[MerkleNode] = None
        self.transaction: dict = transaction

    def __contains__(self, hexdigest: str) -> bool:
        return hexdigest == self.hash

    def __str__(self):
        return f"({self.transaction})"


class MerkleNode:

    def __init__(self, left: Leaf | MerkleNode, right: Leaf | MerkleNode) -> None:
        self.left = left
        self.right = right
        self.left.parent = self
        self.right.parent = self
        self.hash = concat(left.hash, right.hash)
        self.parent = None

    def __contains__(self, hexdigest: str) -> bool:
        return hexdigest in self.left or hexdigest in self.right

    def __str__(self):
        return f"|  {self.left!s} [node] {self.right!s}  |"


class MerkleTree(MerkleNode):

    """Root node of the Merkle tree.

    Attributes
    ----------
    leaf_map : dict[str, Leaf]
        A dictionary that maps the hash of transactions to their respective leaf.
    """

    def __init__(self, UTXO: list) -> None:
        self.leaf_map = {}
        self.root_node = None
        self.__initialise(UTXO)
        super().__init__()

    def __initialise(self, UTXO: list):
        transactions = [Leaf(transaction_info) for transaction_info in UTXO]
        self.leaf_map = {leaf.hash: leaf for leaf in transactions}

        nodes = transactions
        liste_a_traiter = []

        while liste_a_traiter is None:
            liste_a_traiter = []

            while len(nodes) > 1:
                left = nodes.pop(0)  # pop the first elem
                right = nodes.pop(0)  # pop the second elem
                # Create the node that represent the concatenation of the 2 nodes, and add it to the list 
                racine = MerkleNode(left, right)
                liste_a_traiter.append(racine)

            if len(nodes) == 1:
                last_elem = nodes.pop(0)
                liste_a_traiter.append(last_elem)
            
            nodes = liste_a_traiter

            if len(nodes) == 1:
                self.root_node = nodes[0]
                liste_a_traiter = None

    def transaction_in_merkle(self, hexdigest: str) -> list[str]:
        if hexdigest not in self.leaf_map.keys():
            return []

        transaction = self.leaf_map[hexdigest]

        hash_list = []

        while transaction.parent is not None:
            parent = transaction.parent
            if parent.left == transaction:
                hash_list.append(parent.right.hash)
            else:
                hash_list.append(parent.left.hash)

            transaction = parent

        return hash_list


# Simulation of the behaviour of a person that demand if his transaction is included in the block


def is_in_node(tree: MerkleTree, transaction):
    
    hash_t = hash_object(transaction)

    hash_list = tree.transaction_in_merkle(hash_t)

    res = hash_t

    for h in hash_list:
        res = concat(res, h)

    print("\nhash of the transaction =", hash_t)
    print("\nres of computation = ", res)
    print("\nblock hashcode header = ", tree.hash)

    if res == tree.hash:
        print("transaction is in the block")
    else:
        print("transaction is not in the block")


if __name__ == "__main__":
    liste_transaction = ["t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8"]
    tree = MerkleTree(liste_transaction)

    transaction = "t8"
    is_in_node(tree, transaction)
