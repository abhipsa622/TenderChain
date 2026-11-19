
import json
import hashlib
import secrets
from pathlib import Path
from web3 import Web3

# ==========================================
# 1. CONNECT TO GANACHE
# ==========================================

GANACHE_URL = "http://127.0.0.1:7545"

web3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if not web3.is_connected():
    raise ConnectionError("Cannot connect to Ganache")

accounts = web3.eth.accounts

print("Connected to Ganache")
print("Chain ID:", web3.eth.chain_id)

# ==========================================
# 2. TENDER CONFIGURATION
# ==========================================

TENDER_ID = 1

contractors = [
    {
        "name": "Contractor A",
        "account": accounts[1],
        "bid_amount": 1050000
    },
    {
        "name": "Contractor B",
        "account": accounts[2],
        "bid_amount": 980000
    },
    {
        "name": "Contractor C",
        "account": accounts[3],
        "bid_amount": 1100000
    }
]

# ==========================================
# 3. GENERATE SHA-256 COMMITMENTS
# ==========================================

sealed_bids = []

for contractor in contractors:

    bidder_address = Web3.to_checksum_address(
        contractor["account"]
    )

    bid_amount = contractor["bid_amount"]

    # Generate a cryptographically secure
    # random 32-byte nonce
    nonce = secrets.token_bytes(32)

    # Solidity abi.encodePacked equivalent:
    # uint256 + address + uint256 + bytes32

    packed_data = (
        TENDER_ID.to_bytes(32, byteorder="big")
        + bytes.fromhex(bidder_address[2:])
        + bid_amount.to_bytes(32, byteorder="big")
        + nonce
    )

    # Calculate SHA-256 commitment
    commitment = hashlib.sha256(
        packed_data
    ).hexdigest()

    sealed_bids.append({
        "contractor": contractor["name"],
        "tender_id": TENDER_ID,
        "bidder_address": bidder_address,
        "bid_amount": bid_amount,
        "nonce": "0x" + nonce.hex(),
        "commitment": "0x" + commitment
    })

    print("\n------------------------------")
    print(contractor["name"])
    print("------------------------------")
    print("Bidder address:", bidder_address)
    print("Commitment:", "0x" + commitment)

# ==========================================
# 4. SAVE SECRET BID INFORMATION
# ==========================================

output_folder = Path("data")
output_folder.mkdir(exist_ok=True)

output_file = output_folder / "bid_secrets.json"

with open(output_file, "w") as file:
    json.dump(sealed_bids, file, indent=4)

print("\n================================")
print("SEALED BIDS GENERATED SUCCESSFULLY")
print("================================")

print("Secret bid details saved to:")
print(output_file)

print("\nKeep this file private until reveal.")
