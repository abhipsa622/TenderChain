
import hashlib
import secrets
import json
import os


def generate_nonce():
    """Generate a cryptographically random 32-byte nonce."""
    return secrets.token_bytes(32)


def generate_commitment(tender_id, bidder_address, bid_amount, nonce):
    """
    Match Solidity:
    sha256(abi.encodePacked(
        uint256 tenderId,
        address bidder,
        uint256 bidAmount,
        bytes32 nonce
    ))
    """

    tender_bytes = int(tender_id).to_bytes(32, byteorder="big")

    bidder_bytes = bytes.fromhex(
        bidder_address[2:]
    )

    if len(bidder_bytes) != 20:
        raise ValueError("Invalid Ethereum address.")

    amount_bytes = int(bid_amount).to_bytes(
        32,
        byteorder="big"
    )

    if len(nonce) != 32:
        raise ValueError("Nonce must be exactly 32 bytes.")

    packed_data = (
        tender_bytes
        + bidder_bytes
        + amount_bytes
        + nonce
    )

    return hashlib.sha256(packed_data).digest()


def save_bid_secret(
    tender_id,
    bidder_address,
    bid_amount,
    nonce,
    commitment,
    transaction_hash
):
    """Save the bidder's private reveal information locally."""

    folder = "data"
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, "bid_secrets.json")

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                records = json.load(file)
            except json.JSONDecodeError:
                records = []
    else:
        records = []

    if not isinstance(records, list):
        raise ValueError("Bid secrets file must contain a JSON list.")

    record = {
        "tender_id": int(tender_id),
        "bidder": bidder_address,
        "bid_amount": int(bid_amount),
        "nonce": "0x" + nonce.hex(),
        "commitment": "0x" + commitment.hex(),
        "transaction_hash": transaction_hash,
        "status": "submitted"
    }

    # Avoid accidentally overwriting a previous bid secret.
    for existing in records:
        if (
            existing["tender_id"] == int(tender_id)
            and existing["bidder"].lower() == bidder_address.lower()
        ):
            raise ValueError(
                "A secret record already exists for this tender and bidder. "
                "Do not overwrite it."
            )

    records.append(record)

    temp_path = file_path + ".tmp"

    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)

    os.replace(temp_path, file_path)

    return file_path
