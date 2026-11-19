
from web3 import Web3
from datetime import datetime

# Connect to Ganache
GANACHE_URL = "http://127.0.0.1:7545"

web3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if not web3.is_connected():
    raise ConnectionError("Ganache connection failed")

# Read current blockchain timestamp
latest_block = web3.eth.get_block("latest")
current_time = latest_block.timestamp

submission_deadline = 1795064597
reveal_deadline = 1795068197

print("Current blockchain time:",
      datetime.fromtimestamp(current_time))

# Calculate time required to cross submission deadline
if current_time < submission_deadline:
    seconds_to_advance = submission_deadline - current_time + 30

    print("Advancing blockchain by:",
          seconds_to_advance, "seconds")

    # Advance Ganache time
    result = web3.provider.make_request(
        "evm_increaseTime",
        [seconds_to_advance]
    )

    print("Time advancement:", result)

    # Mine a new block with the advanced timestamp
    mine_result = web3.provider.make_request(
        "evm_mine",
        []
    )

    print("Mining result:", mine_result)

else:
    print("Submission deadline has already passed.")

# Verify updated blockchain time
new_block = web3.eth.get_block("latest")

print("\nUpdated blockchain time:",
      datetime.fromtimestamp(new_block.timestamp))

print("New Unix timestamp:", new_block.timestamp)

print("Submission deadline:", submission_deadline)
print("Reveal deadline:", reveal_deadline)

if submission_deadline <= new_block.timestamp <= reveal_deadline:
    print("\nSUCCESS: Reveal period is now active!")

elif new_block.timestamp > reveal_deadline:
    print("\nWARNING: Reveal deadline has expired!")

else:
    print("\nSubmission period is still active.")


from web3 import Web3
from datetime import datetime

# Connect to Ganache
web3 = Web3(
    Web3.HTTPProvider("http://127.0.0.1:7545")
)

if not web3.is_connected():
    raise ConnectionError("Ganache connection failed")

# Read current blockchain time
latest_block = web3.eth.get_block("latest")
current_time = latest_block.timestamp

# Tender deadlines
submission_deadline = 1795064597
reveal_deadline = 1795068197

print("Current blockchain time:",
      datetime.fromtimestamp(current_time))

# Advance time if reveal deadline has not passed
if current_time <= reveal_deadline:

    seconds_to_advance = max(
        1, reveal_deadline - current_time + 30
    )

    result = web3.provider.make_request(
        "evm_increaseTime",
        [seconds_to_advance]
    )

    print("Time advancement:", result)

    # Mine a new block
    mine_result = web3.provider.make_request(
        "evm_mine",
        []
    )

    print("Mining result:", mine_result)

# Verify updated time
new_block = web3.eth.get_block("latest")

print("\nUpdated blockchain time:",
      datetime.fromtimestamp(new_block.timestamp))

print("New Unix timestamp:", new_block.timestamp)

if new_block.timestamp > reveal_deadline:
    print("\nSUCCESS: Reveal deadline has passed!")
else:
    print("\nReveal deadline has not passed yet.")
