"""Print the latest record stored in the deployed AIRecord contract.

Run from the repo root:  python -m scripts.read_record
"""

from web3 import Web3

from app.abi import ABI
from app.config import get_settings

settings = get_settings()
w3 = Web3(Web3.HTTPProvider(settings.rpc_url))
contract = w3.eth.contract(address=Web3.to_checksum_address(settings.contract_address), abi=ABI)

print("Connected to AIRecord contract!")
print("Latest saved record:", contract.functions.getRecord().call())
