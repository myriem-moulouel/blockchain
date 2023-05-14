# Blockchain

## Usage

Ce projet nécessite Python >= 3.9.

## Technical notes

À l'instar des réseaux décentralisés classiques,
nous utilisons des nœuds de confiance pour que les pairs se découvrent.

## Execution
- Start a node with : python node.py 10050 (port number)
- Start another node with connecting it to the previus one : python node.py 10051 10050
- Start a wallet with a port number and connect it to a node : python wallet.py 10001 10050 myriem
- Once you are connected to the wallet you will choose one of the three options : send, check, credit
  - send : send an amount of money from your wallet to another wallet (if the dest wallet doesn't exist, we will create it directly in order to simplify the simulation)
  - check : check if the transaction that you create before is included in the blockchain
  - credit : return the amount of credit available in your wallet (by default all wallets have 100 => you can change it with modifying the init_credit in utils.py file)

## Libraries to install

library : crypto

  ```pip3 install crypto```

if it doesn't work, try :

  ```pip3 uninstall crypto```

  ```pip3 uninstall pycrypto```

  ```pip3 install pycryptodome```



## Start the program
Put different ports for every node


Exemple of architecture:

![image](https://github.com/myriem-moulouel/blockchain/assets/60098131/0b5bcb68-07c8-4a95-ba38-c4a60a1b8320)




#### The first node

```python node.py 10050```

![image](https://github.com/myriem-moulouel/blockchain/assets/60098131/d79b27c8-6699-4f90-90c1-03bd3d54a804)



#### Seconde node

```python node.py 10051 10050```

![image](https://github.com/myriem-moulouel/blockchain/assets/60098131/8bcb081f-43a3-44d3-8932-1e363267430d)


#### Third node

```python node.py 10052 10051```

![image](https://github.com/myriem-moulouel/blockchain/assets/60098131/8d88d2d9-af37-4ca7-9926-ec56d782cb24)



#### The wallet

```python wallet.py 10053 10050 koceila```

![image](https://github.com/myriem-moulouel/blockchain/assets/60098131/39675b1e-8205-4557-82a6-5b8859bfd305)
