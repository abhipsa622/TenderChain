
import json
from pathlib import Path

# ==========================================
# LOAD ORIGINAL SEALED BID INFORMATION
# ==========================================

file_path = Path("data/bid_secrets.json")

with open(file_path, "r") as file:
    sealed_bids = json.load(file)

print("\n===================================")
print("TENDERCHAIN - BID REVEAL DETAILS")
print("===================================")

for bid in sealed_bids:

    print("\n-----------------------------------")
    print("Contractor:", bid["contractor"])
    print("Tender ID:", bid["tender_id"])
    print("Bidder Address:", bid["bidder_address"])
    print("Bid Amount:", bid["bid_amount"])
    print("Secret Nonce:", bid["nonce"])
    print("Original Commitment:", bid["commitment"])
    print("-----------------------------------")

print("\nAll original bid details retrieved.")
print("Use these exact values during reveal.")
