
from web3 import Web3

# Connect to Ganache
GANACHE_URL = "http://127.0.0.1:7545"

web3 = Web3(Web3.HTTPProvider(GANACHE_URL))

# Check blockchain connection
if web3.is_connected():

    print("Successfully connected to Ganache!")

    print("Chain ID:", web3.eth.chain_id)

    print("Latest Block:", web3.eth.block_number)

    # Retrieve accounts
    accounts = web3.eth.accounts

    print("\nAvailable Accounts:")

    for i, account in enumerate(accounts):
        print(f"Account {i+1}: {account}")

    print("\nTotal Accounts:", len(accounts))

else:
    print("Connection failed!")
    print("Check whether Ganache is running.")
