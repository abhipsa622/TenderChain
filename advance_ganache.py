
from web3 import Web3
from datetime import datetime

GANACHE_URL = "http://127.0.0.1:7545"

w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if not w3.is_connected():
    print("ERROR: Ganache is not connected.")
    raise SystemExit

# Read current blockchain time
block = w3.eth.get_block("latest")

print("Current blockchain time:")
print(datetime.fromtimestamp(block.timestamp).strftime(
    "%d %B %Y, %I:%M:%S %p"
))

print("Current block:", block.number)

# Advance time by 13 minutes
result = w3.provider.make_request(
    "evm_increaseTime", [780]
)

print("\nTime advancement result:", result)

# Mine a new block
mine_result = w3.provider.make_request(
    "evm_mine", []
)

print("Mining result:", mine_result)

# Verify the new blockchain time
new_block = w3.eth.get_block("latest")

print("\nNEW BLOCKCHAIN TIME:")
print(datetime.fromtimestamp(new_block.timestamp).strftime(
    "%d %B %Y, %I:%M:%S %p"
))

print("New block number:", new_block.number)
