
from web3 import Web3

# Connect to Ganache
web3 = Web3(
    Web3.HTTPProvider("http://127.0.0.1:7545")
)

# Get test accounts
accounts = web3.eth.accounts

# Select sender and receiver
sender = accounts[0]
receiver = accounts[1]

# Get sender's transaction count
nonce = web3.eth.get_transaction_count(sender)

# Create transaction
transaction = {
    "from": sender,
    "to": receiver,
    "value": Web3.to_wei(1, "ether"),
    "gas": 21000,
    "gasPrice": web3.eth.gas_price,
    "nonce": nonce,
    "chainId": web3.eth.chain_id
}

# Sign using Ganache's unlocked test account
# Ganache permits eth_sendTransaction through its RPC.
tx_hash = web3.eth.send_transaction(transaction)

# Wait for transaction confirmation
receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

print("Transaction Successful!")
print("Transaction Hash:", tx_hash.hex())
print("Block Number:", receipt["blockNumber"])
print("Transaction Status:", receipt["status"])
