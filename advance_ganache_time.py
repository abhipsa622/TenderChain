
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from web3 import Web3

# Load project configuration
load_dotenv()

GANACHE_URL = os.getenv("GANACHE_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

if not GANACHE_URL or not CONTRACT_ADDRESS:
    raise ValueError("Check GANACHE_URL and CONTRACT_ADDRESS in .env")

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if not w3.is_connected():
    raise ConnectionError("Cannot connect to Ganache.")

# Load contract ABI
abi_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "contracts",
    "TenderManagement_abi.json"
)

with open(abi_path, "r", encoding="utf-8") as file:
    abi_data = json.load(file)

abi = abi_data["abi"] if isinstance(abi_data, dict) else abi_data

contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=abi
)

# Read Tender 4 details
TENDER_ID = 4

details = contract.functions.getTenderDetails(TENDER_ID).call()

reveal_deadline = int(details[5])
is_closed = bool(details[6])

if is_closed:
    print("Tender 4 is already closed.")
    raise SystemExit

latest_block = w3.eth.get_block("latest")
current_timestamp = int(latest_block.timestamp)

print("Current Ganache time:",
      datetime.fromtimestamp(current_timestamp))
print("Reveal deadline:",
      datetime.fromtimestamp(reveal_deadline))

# Advance blockchain time beyond the reveal deadline
seconds_to_advance = max(
    reveal_deadline - current_timestamp + 60,
    1
)

print("\nAdvancing Ganache time by",
      seconds_to_advance, "seconds...")

increase_result = w3.provider.make_request(
    "evm_increaseTime",
    [seconds_to_advance]
)

if increase_result.get("error"):
    raise RuntimeError(increase_result["error"])

# Mine a new block at the advanced timestamp
mine_result = w3.provider.make_request(
    "evm_mine",
    []
)

if mine_result.get("error"):
    raise RuntimeError(mine_result["error"])

# Verify the new blockchain time
new_block = w3.eth.get_block("latest")
new_timestamp = int(new_block.timestamp)

print("\nNew Ganache time:",
      datetime.fromtimestamp(new_timestamp))
print("New block number:", new_block.number)

if new_timestamp >= reveal_deadline:
    print("\nSUCCESS: Reveal deadline has passed.")
    print("You can now close Tender 4 from Streamlit.")
else:
    print("\nERROR: Blockchain time is still before the deadline.")
