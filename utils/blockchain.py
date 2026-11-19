
import json
import os

import streamlit as st
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

GANACHE_URL = os.getenv("GANACHE_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ABI_PATH = os.path.join(
    BASE_DIR,
    "contracts",
    "TenderManagement_abi.json"
)


@st.cache_resource
def connect_blockchain():

    if not GANACHE_URL:
        raise ValueError("GANACHE_URL is missing from .env")

    if not CONTRACT_ADDRESS:
        raise ValueError("CONTRACT_ADDRESS is missing from .env")

    if not os.path.exists(ABI_PATH):
        raise FileNotFoundError(
            f"ABI file not found: {ABI_PATH}"
        )

    w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

    if not w3.is_connected():
        raise ConnectionError("Cannot connect to Ganache.")

    address = Web3.to_checksum_address(CONTRACT_ADDRESS)

    code = w3.eth.get_code(address)

    if not code or code == b"\x00":
        raise ValueError("No contract deployed at this address.")

    with open(ABI_PATH, "r", encoding="utf-8-sig") as file:
        artifact = json.load(file)

    if isinstance(artifact, list):
        abi = artifact
    elif isinstance(artifact, dict) and "abi" in artifact:
        abi = artifact["abi"]
    else:
        raise ValueError("Invalid ABI JSON format.")

    contract = w3.eth.contract(
        address=address,
        abi=abi
    )

    return w3, contract


def get_accounts(w3):
    return w3.eth.accounts


def get_contract_owner(contract):
    return contract.functions.owner().call()


def get_next_tender_id(contract):
    return contract.functions.nextTenderId().call()
