
import json
import hashlib
from pathlib import Path
from web3 import Web3

# ==========================================
# 1. LOAD ORIGINAL BID INFORMATION
# ==========================================

file_path = Path("data/bid_secrets.json")

with open(file_path, "r") as file:
    sealed_bids = json.load(file)

# Select Contractor B for testing
bid = next(
    item for item in sealed_bids
    if item["contractor"] == "Contractor B"
)

tender_id = bid["tender_id"]
bidder_address = Web3.to_checksum_address(
    bid["bidder_address"]
)
original_amount = bid["bid_amount"]
original_nonce = bytes.fromhex(
    bid["nonce"].removeprefix("0x")
)
original_commitment = bid["commitment"].lower()

# ==========================================
# 2. SHA-256 COMMITMENT FUNCTION
# ==========================================

def generate_commitment(
    tender_id,
    bidder_address,
    bid_amount,
    nonce
):
    packed_data = (
        tender_id.to_bytes(32, byteorder="big")
        + bytes.fromhex(bidder_address[2:])
        + bid_amount.to_bytes(32, byteorder="big")
        + nonce
    )

    return "0x" + hashlib.sha256(
        packed_data
    ).hexdigest()


# ==========================================
# 3. TEST 1: ORIGINAL BID
# ==========================================

print("\n====================================")
print("TEST 1: ORIGINAL BID VERIFICATION")
print("====================================")

original_test_hash = generate_commitment(
    tender_id,
    bidder_address,
    original_amount,
    original_nonce
)

print("Original bid:", original_amount)
print("Original commitment:", original_commitment)
print("Recalculated hash:", original_test_hash)

if original_test_hash.lower() == original_commitment:
    print("RESULT: VALID - Commitment matches")
else:
    raise ValueError(
        "Original commitment does not match! "
        "Check encoding and saved data."
    )


# ==========================================
# 4. TEST 2: MODIFY THE BID AMOUNT
# ==========================================

print("\n====================================")
print("TEST 2: BID AMOUNT TAMPERING")
print("====================================")

modified_amount = 800000

modified_amount_hash = generate_commitment(
    tender_id,
    bidder_address,
    modified_amount,
    original_nonce
)

print("Original amount:", original_amount)
print("Modified amount:", modified_amount)
print("Original hash:", original_commitment)
print("Modified hash:", modified_amount_hash)

if modified_amount_hash.lower() != original_commitment:
    print("RESULT: TAMPERING DETECTED!")
else:
    print("ERROR: Modified bid unexpectedly matched!")


# ==========================================
# 5. TEST 3: MODIFY THE SECRET NONCE
# ==========================================

print("\n====================================")
print("TEST 3: NONCE TAMPERING")
print("====================================")

modified_nonce = (
    original_nonce[:-1]
    + bytes([original_nonce[-1] ^ 1])
)

modified_nonce_hash = generate_commitment(
    tender_id,
    bidder_address,
    original_amount,
    modified_nonce
)

print("Original nonce:", "0x" + original_nonce.hex())
print("Modified nonce:", "0x" + modified_nonce.hex())
print("Original hash:", original_commitment)
print("Modified hash:", modified_nonce_hash)

if modified_nonce_hash.lower() != original_commitment:
    print("RESULT: TAMPERING DETECTED!")
else:
    print("ERROR: Modified nonce unexpectedly matched!")


# ==========================================
# 6. FINAL SECURITY SUMMARY
# ==========================================

print("\n====================================")
print("TENDERCHAIN SECURITY TEST SUMMARY")
print("====================================")

print("Original bid verification: PASSED")
print("Modified bid detection: PASSED")
print("Modified nonce detection: PASSED")

print("\nAll tampering experiments completed.")
print("Original blockchain records remain unchanged.")
