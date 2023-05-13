import pickle
from hashlib import sha256

DIFFICULTY = 5      # Difficulty to compute the hash of the block
INIT_CREDIT = 100   # the credit by default of every wallet

def hash_object(obj: any) -> str:
    """
    Returns a hexdigest of the value passed.
    """
    return sha256(pickle.dumps(obj)).hexdigest()

def hash_utxo(obj: any) -> str:
    """
    Returns a hexdigest of the value passed.
    """
    return int.from_bytes(sha256(pickle.dumps(obj)).digest(), byteorder="big")

def represents_int(s):
    try: 
        int(s)
    except ValueError:
        return False
    else:
        return True