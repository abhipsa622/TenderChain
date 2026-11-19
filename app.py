
import streamlit as st
import pandas as pd
from datetime import datetime

from utils.blockchain import (
    connect_blockchain,
    get_accounts,
    get_contract_owner,
    get_next_tender_id
)

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="TenderChain Dashboard",
    page_icon="🔗",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM HEADER
# --------------------------------------------------

st.title("🔗 TenderChain")
st.markdown("### Transparent Public Procurement & Tender Bidding")

st.caption(
    "A blockchain-based platform for transparent, "
    "secure and tamper-resistant tender management."
)

st.divider()

# --------------------------------------------------
# BLOCKCHAIN CONNECTION
# --------------------------------------------------

try:
    w3, contract = connect_blockchain()

    accounts = get_accounts(w3)
    owner = get_contract_owner(contract)
    next_id = get_next_tender_id(contract)

    latest_block = w3.eth.get_block("latest")
    block_timestamp = latest_block.timestamp

    st.success("Connected successfully to Ganache and TenderManagement!")

except Exception as error:
    st.error(f"Blockchain connection failed: {error}")
    st.stop()


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.title("TenderChain")
st.sidebar.caption("Procurement Management System")

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Create Tender",
        "Contractor Registration",
        "Sealed Bid Submission",
        "Reveal & Verification",
        "Results & Audit Trail"
    ]
)

st.sidebar.divider()
st.sidebar.write("**Blockchain:** Ganache")
st.sidebar.write(f"**Current Block:** {w3.eth.block_number}")


# --------------------------------------------------
# FETCH TENDER RECORDS
# --------------------------------------------------

def fetch_tenders():

    tenders = []

    for tender_id in range(1, next_id):

        details = contract.functions.getTenderDetails(
            tender_id
        ).call()

        (
            returned_id,
            title,
            description,
            tender_owner,
            submission_deadline,
            reveal_deadline,
            closed,
            winner,
            winning_bid
        ) = details

        bidders = contract.functions.getRegisteredBidders(
            tender_id
        ).call()

        submitted_count = 0
        revealed_count = 0

        for bidder in bidders:

            bid_details = contract.functions.getBidDetails(
                tender_id,
                bidder
            ).call()

            commitment, submitted, revealed, amount = bid_details

            if submitted:
                submitted_count += 1

            if revealed:
                revealed_count += 1

        tenders.append({
            "Tender ID": returned_id,
            "Title": title,
            "Description": description,
            "Owner": tender_owner,
            "Submission Deadline": submission_deadline,
            "Reveal Deadline": reveal_deadline,
            "Closed": closed,
            "Winner": winner,
            "Winning Bid": winning_bid,
            "Registered Bidders": len(bidders),
            "Submitted Bids": submitted_count,
            "Revealed Bids": revealed_count
        })

    return tenders


# --------------------------------------------------
# OVERVIEW PAGE
# --------------------------------------------------

if page == "Overview":

    st.subheader("Dashboard Overview")

    try:
        tenders = fetch_tenders()

        total_tenders = len(tenders)
        closed_tenders = sum(
            1 for tender in tenders if tender["Closed"]
        )
        open_tenders = total_tenders - closed_tenders

        total_bidders = sum(
            tender["Registered Bidders"] for tender in tenders
        )

        # -----------------------------
        # KPI METRICS
        # -----------------------------

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Tenders", total_tenders)
        col2.metric("Open Tenders", open_tenders)
        col3.metric("Closed Tenders", closed_tenders)
        col4.metric("Registered Bidders", total_bidders)

        st.divider()

        # -----------------------------
        # BLOCKCHAIN INFORMATION
        # -----------------------------

        st.subheader("Blockchain Information")

        c1, c2 = st.columns(2)

        with c1:
            st.write("**Smart Contract Address**")
            st.code(contract.address)

            st.write("**Contract Owner**")
            st.code(owner)

        with c2:
            st.metric("Current Block Number", w3.eth.block_number)
            st.metric("Available Ganache Accounts", len(accounts))

        st.divider()

        # -----------------------------
        # TENDER TABLE
        # -----------------------------

        st.subheader("Tender Records")

        if tenders:

            table_data = []

            for tender in tenders:

                status = (
                    "Closed" if tender["Closed"] else "Not Closed"
                )

                table_data.append({
                    "Tender ID": tender["Tender ID"],
                    "Tender Title": tender["Title"],
                    "Registered Bidders": tender["Registered Bidders"],
                    "Submitted Bids": tender["Submitted Bids"],
                    "Revealed Bids": tender["Revealed Bids"],
                    "Status": status
                })

            df = pd.DataFrame(table_data)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            # -----------------------------
            # INDIVIDUAL TENDER DETAILS
            # -----------------------------

            st.divider()
            st.subheader("Tender Details")

            selected_id = st.selectbox(
                "Select Tender ID",
                [t["Tender ID"] for t in tenders]
            )

            selected = next(
                t for t in tenders
                if t["Tender ID"] == selected_id
            )

            st.markdown(f"### {selected['Title']}")

            st.write(selected["Description"])

            d1, d2 = st.columns(2)

            with d1:
                st.write("**Submission Deadline**")
                st.write(
                    datetime.fromtimestamp(
                        selected["Submission Deadline"]
                    ).strftime("%d %b %Y, %I:%M %p")
                )

                st.write("**Registered Bidders**")
                st.write(selected["Registered Bidders"])

                st.write("**Submitted Bids**")
                st.write(selected["Submitted Bids"])

            with d2:
                st.write("**Reveal Deadline**")
                st.write(
                    datetime.fromtimestamp(
                        selected["Reveal Deadline"]
                    ).strftime("%d %b %Y, %I:%M %p")
                )

                st.write("**Revealed Bids**")
                st.write(selected["Revealed Bids"])

                st.write("**Tender Status**")
                st.write(
                    "Closed" if selected["Closed"] else "Not Closed"
                )

            if selected["Closed"] and selected["Winner"] != "0x" + "0" * 40:
                st.success("Winning Bid Information")

                st.write("**Winner Address**")
                st.code(selected["Winner"])

                st.metric(
                    "Winning Bid",
                    f"₹ {selected['Winning Bid']:,}"
                )

            else:
                st.info("Winning bid information is not available.")

        else:
            st.info("No tenders have been created yet.")

    except Exception as error:
        st.error(f"Unable to fetch tender records: {error}")


# --------------------------------------------------
# OTHER MODULES - TO BE DEVELOPED
# --------------------------------------------------



elif page == "Create Tender":

    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo

    st.subheader("Create Tender")
    st.write("Create Tender ID 3 using Ganache blockchain time.")

    india_tz = ZoneInfo("Asia/Kolkata")

    # Read actual blockchain timestamp
    latest_block = w3.eth.get_block("latest")
    chain_time = datetime.fromtimestamp(
        latest_block.timestamp, india_tz
    )

    default_submission = chain_time + timedelta(minutes=15)
    default_reveal = chain_time + timedelta(minutes=75)
    st.success(
        "Connected to Ganache. Deadlines are calculated from blockchain time."
    )

    st.write("**Current Ganache Time:**")
    st.code(chain_time.strftime("%d %B %Y, %I:%M:%S %p IST"))

    st.write("**Government Authority / Contract Owner:**")
    st.code(owner)

    with st.form("create_tender_4_form"):

        title = st.text_input(
            "Tender Title",
            value="Smart City Infrastructure Project"
        )

        description = st.text_area(
            "Tender Description",
            value="Development and construction of urban infrastructure."
        )

        st.markdown("### Submission Deadline")

        col1, col2 = st.columns(2)

        with col1:
            submission_date = st.date_input(
                "Submission Date",
                value=default_submission.date(),
                min_value=chain_time.date()
            )

        with col2:
            submission_time = st.time_input(
                "Submission Time",
                value=default_submission.time().replace(
                    second=0, microsecond=0
                )
            )

        st.markdown("### Reveal Deadline")

        col3, col4 = st.columns(2)

        with col3:
            reveal_date = st.date_input(
                "Reveal Date",
                value=default_reveal.date(),
                min_value=chain_time.date()
            )

        with col4:
            reveal_time = st.time_input(
                "Reveal Time",
                value=default_reveal.time().replace(
                    second=0, microsecond=0
                )
            )

        submit_tender = st.form_submit_button(
            "Create Tender 4 on Blockchain",
            type="primary",
            use_container_width=True
        )

    if submit_tender:

        submission_datetime = datetime.combine(
            submission_date,
            submission_time,
            tzinfo=india_tz
        )

        reveal_datetime = datetime.combine(
            reveal_date,
            reveal_time,
            tzinfo=india_tz
        )

        submission_timestamp = int(
            submission_datetime.timestamp()
        )

        reveal_timestamp = int(
            reveal_datetime.timestamp()
        )

        # Recheck blockchain time before transaction
        latest_block = w3.eth.get_block("latest")
        current_chain_timestamp = latest_block.timestamp

        if not title.strip() or not description.strip():
            st.error("Enter both tender title and description.")

        elif submission_timestamp <= current_chain_timestamp:
            st.error(
                "Submission deadline must be later than current Ganache time."
            )

        elif reveal_timestamp <= submission_timestamp:
            st.error(
                "Reveal deadline must be later than submission deadline."
            )

        elif owner.lower() not in [a.lower() for a in accounts]:
            st.error("Contract owner account is not available in Ganache.")

        else:

            try:
                next_id_before = contract.functions.nextTenderId().call()

                if next_id_before != 4:
                    st.warning(
                        f"The next available Tender ID is {next_id_before}, "
                        "not 4. Check the Overview before proceeding."
                    )

                else:
                    with st.spinner("Creating Tender 4 on Ganache..."):

                        tx_hash = contract.functions.createTender(
                            title.strip(),
                            description.strip(),
                            submission_timestamp,
                            reveal_timestamp
                        ).transact({
                            "from": owner
                        })

                        receipt = w3.eth.wait_for_transaction_receipt(
                            tx_hash
                        )

                    if receipt.status == 1:

                        st.success("Tender 4 successfully created!")

                        st.write("**Tender ID:**", next_id_before)
                        st.write("**Transaction Hash:**")
                        st.code(tx_hash.hex())

                        st.write("**Block Number:**", receipt.blockNumber)

                        st.write(
                            "**Submission Deadline:**",
                            submission_datetime.strftime(
                                "%d %B %Y, %I:%M %p IST"
                            )
                        )

                        st.write(
                            "**Reveal Deadline:**",
                            reveal_datetime.strftime(
                                "%d %B %Y, %I:%M %p IST"
                            )
                        )

                    else:
                        st.error("Tender creation transaction failed.")

            except Exception as error:
                st.error(f"Tender creation failed: {error}")
elif page == "Contractor Registration":

    st.subheader("Contractor Registration")

    st.markdown(
        "Register contractors for an available public tender."
    )

    try:
        tenders = fetch_tenders()

        if not tenders:
            st.warning("No tenders are available.")
            st.stop()

        # Select tender
        tender_options = {
            f"{t['Tender ID']} - {t['Title']}": t["Tender ID"]
            for t in tenders
        }

        selected_tender_label = st.selectbox(
            "Select Tender",
            list(tender_options.keys())
        )

        tender_id = tender_options[selected_tender_label]

        tender = next(
            t for t in tenders
            if t["Tender ID"] == tender_id
        )

        st.write("**Tender Description:**")
        st.write(tender["Description"])

        st.write(
            "**Submission Deadline:**",
            datetime.fromtimestamp(
                tender["Submission Deadline"]
            ).strftime("%d %b %Y, %I:%M %p")
        )

        st.divider()

        st.markdown("### Select Contractor Account")

        contractor_accounts = [
            account for account in accounts
            if account.lower() != owner.lower()
        ]

        selected_account = st.selectbox(
            "Ganache Contractor Account",
            contractor_accounts
        )

        st.caption(
            "The selected Ganache account will be used "
            "to send the registration transaction."
        )

        already_registered = contract.functions.registeredBidders(
            tender_id,
            selected_account
        ).call()

        if already_registered:
            st.success("This account is already registered for this tender.")

        else:
            st.info("This account is not yet registered.")

        if st.button(
            "Register Contractor on Blockchain",
            type="primary",
            disabled=already_registered
        ):

            try:
                with st.spinner("Registering contractor..."):

                    tx_hash = contract.functions.registerBidder(
                        tender_id
                    ).transact({
                        "from": selected_account
                    })

                    receipt = w3.eth.wait_for_transaction_receipt(
                        tx_hash
                    )

                if receipt.status == 1:

                    st.success(
                        "Contractor successfully registered!"
                    )

                    st.write("**Tender ID:**", tender_id)
                    st.write("**Contractor Address:**")
                    st.code(selected_account)

                    st.write("**Transaction Hash:**")
                    st.code(tx_hash.hex())

                    st.write("**Block Number:**", receipt.blockNumber)

                else:
                    st.error("Registration transaction failed.")

            except Exception as error:
                st.error(f"Registration failed: {error}")

        st.divider()

        # Display registered bidders
        st.markdown("### Registered Contractors")

        registered_accounts = contract.functions.getRegisteredBidders(
            tender_id
        ).call()

        if registered_accounts:

            registration_data = []

            for index, bidder in enumerate(registered_accounts, start=1):
                registration_data.append({
                    "Serial Number": index,
                    "Contractor Address": bidder
                })

            st.dataframe(
                pd.DataFrame(registration_data),
                use_container_width=True,
                hide_index=True
            )

            st.metric(
                "Total Registered Contractors",
                len(registered_accounts)
            )

        else:
            st.info("No contractors have registered for this tender yet.")

    except Exception as error:
        st.error(f"Unable to load contractor registration: {error}")


elif page == "Sealed Bid Submission":

    from utils.bidding import (
        generate_nonce,
        generate_commitment,
        save_bid_secret
    )

    st.subheader("Sealed Bid Submission")

    st.markdown(
        "Submit your bid securely using SHA-256 cryptographic commitments."
    )

    st.warning(
        "Your bid amount and nonce remain private during submission. "
        "Keep your local bid secrets safe for the reveal stage."
    )

    try:
        tenders = fetch_tenders()

        if not tenders:
            st.info("No tenders are available.")
            st.stop()

        # --------------------------------------------------
        # SELECT TENDER
        # --------------------------------------------------

        tender_options = {
            f"{t['Tender ID']} - {t['Title']}": t["Tender ID"]
            for t in tenders
        }

        selected_label = st.selectbox(
            "Select Tender",
            list(tender_options.keys())
        )

        tender_id = tender_options[selected_label]

        selected_tender = next(
            t for t in tenders
            if t["Tender ID"] == tender_id
        )

        st.write("**Tender Description:**")
        st.write(selected_tender["Description"])

        # Use the latest blockchain timestamp, not the computer clock.
        latest_block = w3.eth.get_block("latest")
        chain_timestamp = latest_block.timestamp

        st.write("**Blockchain Time:**")
        st.write(
            datetime.fromtimestamp(
                chain_timestamp
            ).strftime("%d %b %Y, %I:%M:%S %p")
        )

        st.write("**Submission Deadline:**")
        st.write(
            datetime.fromtimestamp(
                selected_tender["Submission Deadline"]
            ).strftime("%d %b %Y, %I:%M %p")
        )

        st.divider()

        # --------------------------------------------------
        # VALIDATE TENDER
        # --------------------------------------------------

        if selected_tender["Closed"]:
            st.error("This tender is already closed.")
            st.stop()

        if chain_timestamp >= selected_tender["Submission Deadline"]:
            st.error("The submission deadline has passed.")
            st.stop()

        # --------------------------------------------------
        # SELECT REGISTERED CONTRACTOR
        # --------------------------------------------------

        registered_accounts = contract.functions.getRegisteredBidders(
            tender_id
        ).call()

        if not registered_accounts:
            st.warning("No contractors are registered for this tender.")
            st.stop()

        st.markdown("### Contractor Account")

        bidder = st.selectbox(
            "Select your registered Ganache account",
            registered_accounts
        )

        bid_details = contract.functions.getBidDetails(
            tender_id,
            bidder
        ).call()

        existing_commitment, submitted, revealed, existing_amount = bid_details

        if submitted:
            st.success("A bid has already been submitted by this account.")

            st.write("**Existing Commitment:**")
            st.code(
                "0x" + bytes(existing_commitment).hex()
            )

            st.info("A second bid cannot be submitted by this account.")

        else:

            # --------------------------------------------------
            # ENTER BID
            # --------------------------------------------------

            st.markdown("### Enter Confidential Bid")

            bid_amount = st.number_input(
                "Bid Amount (₹)",
                min_value=1,
                max_value=10**12,
                value=1000000,
                step=10000
            )

            st.caption(
                "The bid amount will not be included in the "
                "on-chain submission transaction."
            )

            st.divider()

            # --------------------------------------------------
            # SUBMIT SEALED BID
            # --------------------------------------------------

            if st.button(
                "Generate & Submit Sealed Bid",
                type="primary",
                use_container_width=True
            ):

                try:
                    # Recheck chain time immediately before submission.
                    latest_block = w3.eth.get_block("latest")
                    chain_timestamp = latest_block.timestamp

                    if chain_timestamp >= selected_tender["Submission Deadline"]:
                        st.error("The submission deadline has passed.")
                        st.stop()

                    # Recheck that no bid has been submitted.
                    current_details = contract.functions.getBidDetails(
                        tender_id,
                        bidder
                    ).call()

                    if current_details[1]:
                        st.error("A bid has already been submitted.")
                        st.stop()

                    # Generate random nonce.
                    nonce = generate_nonce()

                    # Generate exact Solidity-compatible SHA-256 commitment.
                    commitment = generate_commitment(
                        tender_id,
                        bidder,
                        int(bid_amount),
                        nonce
                    )

                    st.write("**Generated Commitment:**")
                    st.code("0x" + commitment.hex())

                    with st.spinner(
                        "Submitting commitment to Ganache..."
                    ):

                        tx_hash = contract.functions.submitBid(
                            tender_id,
                            commitment
                        ).transact({
                            "from": bidder
                        })

                        receipt = w3.eth.wait_for_transaction_receipt(
                            tx_hash
                        )

                    if receipt.status == 1:

                        # Confirm that the commitment was recorded.
                        saved_details = contract.functions.getBidDetails(
                            tender_id,
                            bidder
                        ).call()

                        onchain_commitment = bytes(saved_details[0])

                        if (
                            not saved_details[1]
                            or onchain_commitment != commitment
                        ):
                            st.error(
                                "Transaction mined, but commitment "
                                "confirmation did not match. "
                                "Do not attempt to submit another bid."
                            )
                            st.stop()

                        # Save reveal details locally.
                        secret_path = save_bid_secret(
                            tender_id=tender_id,
                            bidder_address=bidder,
                            bid_amount=int(bid_amount),
                            nonce=nonce,
                            commitment=commitment,
                            transaction_hash=tx_hash.hex()
                        )

                        st.success(
                            "Sealed bid successfully submitted and verified on-chain!"
                        )

                        st.write("**Tender ID:**", tender_id)

                        st.write("**Bidder Address:**")
                        st.code(bidder)

                        st.write("**Commitment:**")
                        st.code("0x" + commitment.hex())

                        st.write("**Transaction Hash:**")
                        st.code(tx_hash.hex())

                        st.write("**Block Number:**", receipt.blockNumber)

                        st.info(
                            "Your bid amount and nonce have been saved "
                            "locally for the reveal stage."
                        )

                        st.write("**Secret file:**", secret_path)

                        st.warning(
                            "Do not share the bid secrets file or nonce "
                            "before the reveal period."
                        )

                    else:
                        st.error("Bid submission transaction failed.")

                except Exception as error:
                    st.error(f"Bid submission failed: {error}")

    except Exception as error:
        st.error(f"Unable to load sealed bidding page: {error}")



elif page == "Reveal & Verification":

    import json
    import os

    from utils.bidding import generate_commitment

    # ==================================================
    # CONFIGURATION
    # ==================================================

    REVEAL_TENDER_ID = 4

    st.subheader("Reveal & Verification")

    st.markdown(
        "Reveal submitted bids and verify their SHA-256 commitments "
        "against the deployed TenderManagement smart contract."
    )

    SECRET_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data",
        "bid_secrets.json"
    )

    # ==================================================
    # LOAD BID SECRET RECORDS
    # ==================================================

    if not os.path.exists(SECRET_PATH):

        st.error("bid_secrets.json file was not found.")
        st.stop()

    try:

        with open(
            SECRET_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            bid_records = json.load(file)

        if not isinstance(bid_records, list):
            st.error("Invalid bid secrets file format.")
            st.stop()

    except Exception as error:

        st.error(f"Unable to read bid secrets: {error}")
        st.stop()

    # Filter records for Tender ID 4

    tender_4_records = [
        record for record in bid_records
        if int(record.get("tender_id", 0)) == REVEAL_TENDER_ID
    ]

    st.metric(
        "Saved Bid Records for Tender 4",
        len(tender_4_records)
    )

    if not tender_4_records:

        st.warning(
            "No saved bid records found for Tender ID 4."
        )
        st.stop()

    # ==================================================
    # FETCH TENDER DETAILS FROM BLOCKCHAIN
    # ==================================================

    try:

        details = contract.functions.getTenderDetails(
            REVEAL_TENDER_ID
        ).call()

        (
            tender_id,
            title,
            description,
            tender_owner,
            submission_deadline,
            reveal_deadline,
            closed,
            winner,
            winning_bid
        ) = details

    except Exception as error:

        st.error(f"Unable to fetch Tender 4: {error}")
        st.stop()

    # ==================================================
    # DISPLAY TENDER INFORMATION
    # ==================================================

    st.divider()

    st.markdown(f"### {title}")

    st.write("**Tender ID:**", tender_id)

    st.write("**Description:**", description)

    st.write("**Submission Deadline:**")

    st.write(
        datetime.fromtimestamp(
            submission_deadline
        ).strftime("%d %B %Y, %I:%M:%S %p")
    )

    st.write("**Reveal Deadline:**")

    st.write(
        datetime.fromtimestamp(
            reveal_deadline
        ).strftime("%d %B %Y, %I:%M:%S %p")
    )

    # ==================================================
    # CHECK LATEST GANACHE BLOCK TIME
    # ==================================================

    latest_block = w3.eth.get_block("latest")

    chain_timestamp = latest_block.timestamp

    st.write("**Current Blockchain Time:**")

    st.write(
        datetime.fromtimestamp(
            chain_timestamp
        ).strftime("%d %B %Y, %I:%M:%S %p")
    )

    st.write("**Current Block Number:**", latest_block.number)

    st.divider()

    # ==================================================
    # CHECK TENDER STATUS
    # ==================================================

    if closed:

        st.error("Tender 4 is already closed.")

        st.write("**Winner:**")
        st.code(winner)

        st.metric(
            "Winning Bid",
            f"₹ {winning_bid:,}"
        )

        st.stop()

    if chain_timestamp < submission_deadline:

        st.warning(
            "The submission period is still active. "
            "Bids can only be revealed after the submission deadline."
        )

        st.stop()

    if chain_timestamp >= reveal_deadline:

        st.error(
            "The reveal deadline has passed. "
            "The smart contract will reject reveal transactions."
        )

        st.stop()

    st.success(
        "The reveal period is currently active."
    )

    # ==================================================
    # SELECT CONTRACTOR
    # ==================================================

    st.divider()

    st.markdown("### Select Contractor")

    contractor_options = {
        f"Contractor {index + 1} - {record['bidder']}": index
        for index, record in enumerate(tender_4_records)
    }

    selected_contractor = st.selectbox(
        "Select a saved bid",
        list(contractor_options.keys())
    )

    record_index = contractor_options[selected_contractor]

    record = tender_4_records[record_index]

    bidder = record["bidder"]

    bid_amount = int(record["bid_amount"])

    nonce_hex = record["nonce"]

    st.write("**Contractor Address:**")

    st.code(bidder)

    st.write(
        "**Local Bid Status:**",
        record.get("status", "submitted")
    )

    # ==================================================
    # FETCH ON-CHAIN BID DETAILS
    # ==================================================

    try:

        onchain_details = contract.functions.getBidDetails(
            REVEAL_TENDER_ID,
            bidder
        ).call()

        onchain_commitment = bytes(onchain_details[0])

        submitted = onchain_details[1]

        revealed = onchain_details[2]

        onchain_amount = int(onchain_details[3])

    except Exception as error:

        st.error(f"Unable to fetch bid details: {error}")
        st.stop()

    if not submitted:

        st.error(
            "No submitted bid exists on-chain for this contractor."
        )

        st.stop()

    st.write("**On-chain Commitment:**")

    st.code("0x" + onchain_commitment.hex())

    # ==================================================
    # CHECK WHETHER ALREADY REVEALED
    # ==================================================

    if revealed:

        st.success(
            "This bid has already been revealed successfully on-chain."
        )

        st.metric(
            "Revealed Bid Amount",
            f"₹ {onchain_amount:,}"
        )

        st.info(
            "No additional reveal transaction is required."
        )

        st.stop()

    # ==================================================
    # VERIFY LOCAL NONCE AND COMMITMENT
    # ==================================================

    try:

        nonce = bytes.fromhex(
            nonce_hex.removeprefix("0x")
        )

        if len(nonce) != 32:

            raise ValueError(
                "The saved nonce must contain exactly 32 bytes."
            )

        calculated_commitment = generate_commitment(
            REVEAL_TENDER_ID,
            bidder,
            bid_amount,
            nonce
        )

        saved_commitment = bytes.fromhex(
            record["commitment"].removeprefix("0x")
        )

        if calculated_commitment != saved_commitment:

            st.error(
                "The saved bid amount and nonce do not match "
                "the locally saved commitment."
            )

            st.stop()

        if calculated_commitment != onchain_commitment:

            st.error(
                "The calculated SHA-256 commitment does not match "
                "the commitment stored on Ganache. "
                "The bid will not be revealed."
            )

            st.stop()

        st.success(
            "SHA-256 verification successful! "
            "Local and on-chain commitments match."
        )

    except Exception as error:

        st.error(
            f"Commitment verification failed: {error}"
        )

        st.stop()

    # ==================================================
    # REVEAL BID
    # ==================================================

    st.divider()

    st.markdown("### Reveal Bid")

    st.info(
        "The bid amount will become publicly visible on the blockchain "
        "after successful reveal."
    )

    if st.button(
        "Reveal & Verify Bid on Blockchain",
        type="primary",
        use_container_width=True
    ):

        try:

            # Recheck latest blockchain time

            latest_block = w3.eth.get_block("latest")

            current_timestamp = latest_block.timestamp

            if current_timestamp < submission_deadline:

                st.error(
                    "The submission period has not ended."
                )

                st.stop()

            if current_timestamp >= reveal_deadline:

                st.error(
                    "The reveal deadline has passed."
                )

                st.stop()

            # Recheck current on-chain bid details

            current_details = contract.functions.getBidDetails(
                REVEAL_TENDER_ID,
                bidder
            ).call()

            if not current_details[1]:

                st.error(
                    "No bid has been submitted by this account."
                )

                st.stop()

            if current_details[2]:

                st.warning(
                    "This bid has already been revealed."
                )

                st.stop()

            if bytes(current_details[0]) != calculated_commitment:

                st.error(
                    "The on-chain commitment does not match. "
                    "Reveal cancelled."
                )

                st.stop()

            # Submit reveal transaction

            with st.spinner(
                "Revealing bid on Ganache..."
            ):

                tx_hash = contract.functions.revealBid(
                    REVEAL_TENDER_ID,
                    bid_amount,
                    nonce
                ).transact({
                    "from": bidder
                })

                receipt = w3.eth.wait_for_transaction_receipt(
                    tx_hash
                )

            if receipt.status != 1:

                st.error(
                    "Reveal transaction failed."
                )

                st.stop()

            # ==================================================
            # VERIFY REVEAL ON-CHAIN
            # ==================================================

            verified_details = contract.functions.getBidDetails(
                REVEAL_TENDER_ID,
                bidder
            ).call()

            verified_revealed = verified_details[2]

            verified_amount = int(verified_details[3])

            if (
                not verified_revealed
                or verified_amount != bid_amount
            ):

                st.error(
                    "Transaction was mined, but the revealed bid "
                    "could not be confirmed correctly."
                )

                st.stop()

            # ==================================================
            # UPDATE LOCAL JSON RECORD
            # ==================================================

            with open(
                SECRET_PATH,
                "r",
                encoding="utf-8"
            ) as file:

                all_records = json.load(file)

            for saved_record in all_records:

                if (
                    int(saved_record["tender_id"]) == REVEAL_TENDER_ID
                    and saved_record["bidder"].lower() == bidder.lower()
                ):

                    saved_record["status"] = "revealed"

                    saved_record["reveal_transaction_hash"] = (
                        tx_hash.hex()
                    )

                    break

            temp_path = SECRET_PATH + ".tmp"

            with open(
                temp_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    all_records,
                    file,
                    indent=4
                )

            os.replace(
                temp_path,
                SECRET_PATH
            )

            # ==================================================
            # DISPLAY SUCCESS
            # ==================================================

            st.success(
                "Bid successfully revealed and verified on blockchain!"
            )

            st.metric(
                "Revealed Bid Amount",
                f"₹ {bid_amount:,}"
            )

            st.write("**Contractor Address:**")

            st.code(bidder)

            st.write("**Verified Commitment:**")

            st.code(
                "0x" + calculated_commitment.hex()
            )

            st.write("**Reveal Transaction Hash:**")

            st.code(
                tx_hash.hex()
            )

            st.write(
                "**Block Number:**",
                receipt.blockNumber
            )

            st.info(
                "The local bid record has been updated to 'revealed'."
            )

        except Exception as error:

            st.error(
                f"Bid reveal failed: {error}"
            )

    # ==================================================
    # DISPLAY REVEAL PROGRESS
    # ==================================================

    st.divider()

    st.markdown("### Reveal Progress")

    progress_data = []

    for saved_record in tender_4_records:

        saved_bidder = saved_record["bidder"]

        details = contract.functions.getBidDetails(
            REVEAL_TENDER_ID,
            saved_bidder
        ).call()

        progress_data.append({
            "Contractor": saved_bidder,
            "Submitted": details[1],
            "Revealed": details[2],
            "Bid Amount": (
                f"₹ {int(details[3]):,}"
                if details[2] else "Hidden"
            )
        })

    st.dataframe(
        pd.DataFrame(progress_data),
        use_container_width=True,
        hide_index=True
    )

    revealed_count = sum(
        1 for item in progress_data if item["Revealed"]
    )

    st.metric(
        "Revealed Bids",
        f"{revealed_count} / {len(progress_data)}"
    )



    # --------------------------------------------------
    # LOAD PRIVATE BID RECORDS
    # --------------------------------------------------

    if not os.path.exists(SECRET_PATH):
        st.error("Bid secrets file was not found.")
        st.stop()

    try:
        with open(SECRET_PATH, "r", encoding="utf-8") as file:
            bid_records = json.load(file)

        if not isinstance(bid_records, list):
            st.error("Invalid bid secrets file format.")
            st.stop()

    except Exception as error:
        st.error(f"Unable to read bid secrets: {error}")
        st.stop()

    tender_3_records = [
        record for record in bid_records
        if int(record["tender_id"]) == 3
    ]

    st.metric("Saved Bid Records for Tender 3", len(tender_3_records))

    if not tender_3_records:
        st.warning("No saved bid records found for Tender ID 3.")
        st.stop()

    # --------------------------------------------------
    # READ TENDER DETAILS
    # --------------------------------------------------

    try:
        details = contract.functions.getTenderDetails(3).call()

        (
            tender_id,
            title,
            description,
            tender_owner,
            submission_deadline,
            reveal_deadline,
            closed,
            winner,
            winning_bid
        ) = details

        latest_block = w3.eth.get_block("latest")
        chain_timestamp = latest_block.timestamp

        st.markdown(f"### {title}")

        st.write("**Tender ID:**", tender_id)

        st.write(
            "**Submission Deadline:**",
            datetime.fromtimestamp(
                submission_deadline
            ).strftime("%d %B %Y, %I:%M:%S %p")
        )

        st.write(
            "**Reveal Deadline:**",
            datetime.fromtimestamp(
                reveal_deadline
            ).strftime("%d %B %Y, %I:%M:%S %p")
        )

        st.write(
            "**Current Blockchain Time:**",
            datetime.fromtimestamp(
                chain_timestamp
            ).strftime("%d %B %Y, %I:%M:%S %p")
        )

    except Exception as error:
        st.error(f"Unable to fetch Tender 3: {error}")
        st.stop()

    # --------------------------------------------------
    # CHECK REVEAL WINDOW
    # --------------------------------------------------

    if closed:
        st.error("Tender 3 is already closed. No more bids can be revealed.")
        st.stop()

    if chain_timestamp < submission_deadline:
        st.warning(
            "The submission period is still active. "
            "Bids can only be revealed after the submission deadline."
        )
        st.stop()

    if chain_timestamp >= reveal_deadline:
        st.error(
            "The reveal deadline has passed. "
            "The smart contract will reject reveal transactions."
        )
        st.stop()

    st.success("The tender is currently within its reveal period.")

    st.divider()

    # --------------------------------------------------
    # SELECT CONTRACTOR
    # --------------------------------------------------

    st.markdown("### Select Contractor")

    contractor_options = {
        f"Contractor {index + 1} - {record['bidder']}":
            index
        for index, record in enumerate(tender_3_records)
    }

    selected_contractor = st.selectbox(
        "Choose a saved bid",
        list(contractor_options.keys())
    )

    record_index = contractor_options[selected_contractor]
    record = tender_3_records[record_index]

    bidder = record["bidder"]
    bid_amount = int(record["bid_amount"])
    nonce_hex = record["nonce"]

    st.write("**Bidder Address:**")
    st.code(bidder)

    st.write("**Saved Bid Status:**", record.get("status", "submitted"))

    # --------------------------------------------------
    # CHECK ON-CHAIN BID
    # --------------------------------------------------

    onchain_details = contract.functions.getBidDetails(
        3,
        bidder
    ).call()

    onchain_commitment = bytes(onchain_details[0])
    submitted = onchain_details[1]
    revealed = onchain_details[2]
    onchain_amount = int(onchain_details[3])

    if not submitted:
        st.error("No submitted bid exists on-chain for this account.")
        st.stop()

    if revealed:
        st.success("This bid has already been revealed on-chain.")
        st.write("**Revealed Bid Amount:**")
        st.metric("Bid Amount", f"₹ {onchain_amount:,}")
        st.stop()

    # --------------------------------------------------
    # RECALCULATE SHA-256 COMMITMENT
    # --------------------------------------------------

    try:
        nonce = bytes.fromhex(nonce_hex.removeprefix("0x"))

        if len(nonce) != 32:
            raise ValueError("Saved nonce must contain exactly 32 bytes.")

        calculated_commitment = generate_commitment(
            3,
            bidder,
            bid_amount,
            nonce
        )

        saved_commitment = bytes.fromhex(
            record["commitment"].removeprefix("0x")
        )

        if calculated_commitment != saved_commitment:
            st.error(
                "Saved bid amount and nonce do not match the saved commitment."
            )
            st.stop()

        if calculated_commitment != onchain_commitment:
            st.error(
                "The recalculated commitment does not match the "
                "commitment stored on Ganache. Do not reveal this bid."
            )
            st.stop()

        st.success(
            "SHA-256 verification successful! "
            "The saved details match the on-chain commitment."
        )

    except Exception as error:
        st.error(f"Local commitment verification failed: {error}")
        st.stop()

    # --------------------------------------------------
    # REVEAL BID
    # --------------------------------------------------

    st.markdown("### Reveal Bid")

    st.info(
        "Your bid amount will become visible on-chain after successful reveal."
    )

    if st.button(
        "Reveal & Verify Bid on Blockchain",
        type="primary",
        use_container_width=True
    ):

        try:
            # Recheck the latest block timestamp immediately before reveal.
            latest_block = w3.eth.get_block("latest")
            current_timestamp = latest_block.timestamp

            if current_timestamp < submission_deadline:
                st.error("Submission period has not ended.")

            elif current_timestamp >= reveal_deadline:
                st.error("Reveal deadline has passed.")

            else:

                # Recheck current on-chain status.
                current_details = contract.functions.getBidDetails(
                    3,
                    bidder
                ).call()

                if not current_details[1]:
                    st.error("No bid has been submitted by this account.")

                elif current_details[2]:
                    st.warning("This bid has already been revealed.")

                elif bytes(current_details[0]) != calculated_commitment:
                    st.error("On-chain commitment has changed. Reveal cancelled.")

                else:

                    with st.spinner("Revealing bid on Ganache..."):

                        tx_hash = contract.functions.revealBid(
                            3,
                            bid_amount,
                            nonce
                        ).transact({
                            "from": bidder
                        })

                        receipt = w3.eth.wait_for_transaction_receipt(
                            tx_hash
                        )

                    if receipt.status != 1:
                        st.error("Reveal transaction failed.")

                    else:

                        # Confirm reveal on-chain.
                        verified_details = contract.functions.getBidDetails(
                            3,
                            bidder
                        ).call()

                        if (
                            not verified_details[2]
                            or int(verified_details[3]) != bid_amount
                        ):
                            st.error(
                                "Transaction mined, but on-chain reveal "
                                "confirmation did not match the saved bid."
                            )
                            st.stop()

                        # Update the matching record in the original JSON file.
                        with open(
                            SECRET_PATH,
                            "r",
                            encoding="utf-8"
                        ) as file:
                            all_records = json.load(file)

                        for saved_record in all_records:
                            if (
                                int(saved_record["tender_id"]) == 3
                                and saved_record["bidder"].lower()
                                == bidder.lower()
                            ):
                                saved_record["status"] = "revealed"
                                saved_record["reveal_transaction_hash"] = (
                                    tx_hash.hex()
                                )
                                break

                        temp_path = SECRET_PATH + ".tmp"

                        with open(
                            temp_path,
                            "w",
                            encoding="utf-8"
                        ) as file:
                            json.dump(all_records, file, indent=4)

                        os.replace(temp_path, SECRET_PATH)

                        st.success(
                            "Bid successfully revealed and verified on-chain!"
                        )

                        st.metric(
                            "Revealed Bid Amount",
                            f"₹ {bid_amount:,}"
                        )

                        st.write("**Bidder Address:**")
                        st.code(bidder)

                        st.write("**Transaction Hash:**")
                        st.code(tx_hash.hex())

                        st.write("**Block Number:**", receipt.blockNumber)

                        st.info(
                            "The bid record has been updated to 'revealed' "
                            "in bid_secrets.json."
                        )

        except Exception as error:
            st.error(f"Bid reveal failed: {error}")

elif page == "Results & Audit Trail":

    import os
    import json
    import pandas as pd
    from datetime import datetime

    # ==================================================
    # CONFIGURATION
    # ==================================================

    TENDER_ID = 4

    SECRET_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data",
        "bid_secrets.json"
    )

    st.header("Results & Audit Trail")

    st.markdown(
        "View revealed bids, close the tender through the smart contract, "
        "and verify the final procurement result."
    )

    # ==================================================
    # LOAD SAVED BID RECORDS
    # ==================================================

    if not os.path.exists(SECRET_PATH):

        st.error("bid_secrets.json was not found.")
        st.stop()

    try:

        with open(SECRET_PATH, "r", encoding="utf-8") as file:
            all_records = json.load(file)

        tender_records = [
            record for record in all_records
            if int(record.get("tender_id", 0)) == TENDER_ID
        ]

    except Exception as error:

        st.error(f"Unable to load bid records: {error}")
        st.stop()

    # ==================================================
    # FETCH TENDER DETAILS
    # ==================================================

    try:

        details = contract.functions.getTenderDetails(
            TENDER_ID
        ).call()

        (
            tender_id,
            title,
            description,
            tender_owner,
            submission_deadline,
            reveal_deadline,
            closed,
            winner,
            winning_bid
        ) = details

    except Exception as error:

        st.error(f"Unable to fetch Tender 4: {error}")
        st.stop()

    st.subheader(title)

    st.write("**Tender ID:**", tender_id)
    st.write("**Description:**", description)

    st.write(
        "**Submission Deadline:**",
        datetime.fromtimestamp(
            submission_deadline
        ).strftime("%d %B %Y, %I:%M:%S %p")
    )

    st.write(
        "**Reveal Deadline:**",
        datetime.fromtimestamp(
            reveal_deadline
        ).strftime("%d %B %Y, %I:%M:%S %p")
    )

    st.write("**Government Authority / Owner:**")
    st.code(tender_owner)

    st.write(
        "**Tender Status:**",
        "Closed" if closed else "Open"
    )

    st.divider()

    # ==================================================
    # FETCH REGISTERED BIDDERS AND THEIR BID DETAILS
    # ==================================================

    try:

        registered_bidders = (
            contract.functions.getRegisteredBidders(
                TENDER_ID
            ).call()
        )

    except Exception as error:

        st.error(f"Unable to fetch registered bidders: {error}")
        st.stop()

    if not registered_bidders:

        st.warning("No contractors are registered for Tender 4.")
        st.stop()

    results = []

    for bidder in registered_bidders:

        try:

            bid_details = contract.functions.getBidDetails(
                TENDER_ID,
                bidder
            ).call()

            commitment = "0x" + bytes(
                bid_details[0]
            ).hex()

            submitted = bool(bid_details[1])
            revealed = bool(bid_details[2])
            amount = int(bid_details[3])

            results.append({
                "Contractor Address": bidder,
                "Submitted": submitted,
                "Revealed": revealed,
                "Bid Amount": (
                    amount if revealed else None
                ),
                "Commitment": commitment
            })

        except Exception as error:

            st.error(
                f"Could not retrieve bid for {bidder}: {error}"
            )

    if not results:
        st.warning("No bid details could be retrieved.")
        st.stop()

    results_df = pd.DataFrame(results)

    # ==================================================
    # DISPLAY BID SUMMARY
    # ==================================================

    st.subheader("Revealed Bid Results")

    revealed_results = [
        item for item in results
        if item["Submitted"] and item["Revealed"]
    ]

    st.dataframe(
        pd.DataFrame([
            {
                "Contractor Address": item["Contractor Address"],
                "Submitted": item["Submitted"],
                "Revealed": item["Revealed"],
                "Bid Amount (INR)": (
                    f"₹ {item['Bid Amount']:,}"
                    if item["Revealed"] else "Hidden"
                )
            }
            for item in results
        ]),
        use_container_width=True,
        hide_index=True
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Registered Contractors",
        len(registered_bidders)
    )

    col2.metric(
        "Submitted Bids",
        sum(1 for item in results if item["Submitted"])
    )

    col3.metric(
        "Revealed Bids",
        len(revealed_results)
    )

    st.divider()

    # ==================================================
    # WINNER PREVIEW
    # ==================================================

    if revealed_results:

        lowest_bid = min(
            item["Bid Amount"]
            for item in revealed_results
        )

        lowest_bidder = next(
            item["Contractor Address"]
            for item in revealed_results
            if item["Bid Amount"] == lowest_bid
        )

        st.subheader("Lowest Revealed Bid")

        st.metric(
            "Lowest Bid Amount",
            f"₹ {lowest_bid:,}"
        )

        st.write("**Lowest Bidder Address:**")
        st.code(lowest_bidder)

        if not closed:

            st.caption(
                "This is a preview based on revealed bids. "
                "The official winner is recorded when the contract is closed."
            )

    else:

        st.warning("No bids have been revealed yet.")

    st.divider()

    # ==================================================
    # CLOSE TENDER
    # ==================================================

    st.subheader("Close Tender & Declare Winner")

    if closed:

        st.success(
            "Tender 4 has already been closed on the blockchain."
        )

        st.write("**Official Winner Address:**")
        st.code(winner)

        st.metric(
            "Official Winning Bid",
            f"₹ {int(winning_bid):,}"
        )

    else:

        all_submitted_revealed = all(
            item["Submitted"] and item["Revealed"]
            for item in results
        )

        if not all_submitted_revealed:

            st.warning(
                "All submitted bids must be revealed before "
                "the tender can be closed."
            )

        else:

            st.success(
                "All registered contractors have submitted and "
                "revealed their bids."
            )

            # Get contract owner and Ganache accounts

            try:

                contract_owner = (
                    contract.functions.owner().call()
                )

                ganache_accounts = w3.eth.accounts

            except Exception as error:

                st.error(f"Unable to fetch accounts: {error}")
                st.stop()

            st.write("**Contract Owner:**")
            st.code(contract_owner)

            if contract_owner not in ganache_accounts:

                st.error(
                    "The contract owner account is not available "
                    "in the connected Ganache accounts."
                )

            else:

                selected_account = st.selectbox(
                    "Select Government Authority Account",
                    ganache_accounts,
                    index=ganache_accounts.index(contract_owner)
                )

                if selected_account.lower() != contract_owner.lower():

                    st.error(
                        "Please select the actual contract owner account."
                    )

                else:

                    st.warning(
                        "Closing the tender is a permanent "
                        "on-chain action for this tender."
                    )

                    confirm_close = st.checkbox(
                        "I confirm that all revealed bids have been checked "
                        "and I want to close Tender ID 4."
                    )

                    if st.button(
                        "Close Tender 4 on Blockchain",
                        type="primary",
                        use_container_width=True,
                        disabled=not confirm_close
                    ):

                        try:

                            # Check the tender again before closing

                            latest_details = (
                                contract.functions.getTenderDetails(
                                    TENDER_ID
                                ).call()
                            )

                            if latest_details[6]:

                                st.error(
                                    "This tender is already closed."
                                )
                                st.stop()

                            # Submit closing transaction

                            with st.spinner(
                                "Closing Tender 4 on Ganache..."
                            ):

                                tx_hash = (
                                    contract.functions.closeTender(
                                        TENDER_ID
                                    ).transact({
                                        "from": selected_account
                                    })
                                )

                                receipt = (
                                    w3.eth.wait_for_transaction_receipt(
                                        tx_hash
                                    )
                                )

                            if receipt.status != 1:

                                st.error(
                                    "Tender closing transaction failed."
                                )
                                st.stop()

                            # Fetch final on-chain result

                            final_details = (
                                contract.functions.getTenderDetails(
                                    TENDER_ID
                                ).call()
                            )

                            final_closed = final_details[6]
                            final_winner = final_details[7]
                            final_winning_bid = int(final_details[8])

                            if not final_closed:

                                st.error(
                                    "Transaction was mined, but the "
                                    "contract does not report the tender "
                                    "as closed. Please inspect the contract."
                                )
                                st.stop()

                            # Save transaction details in session state

                            st.session_state[
                                "tender4_close_tx"
                            ] = tx_hash.hex()

                            st.session_state[
                                "tender4_close_block"
                            ] = receipt.blockNumber

                            # Display confirmation

                            st.success(
                                "Tender 4 successfully closed on blockchain!"
                            )

                            st.write("**Official Winner:**")
                            st.code(final_winner)

                            st.metric(
                                "Winning Bid",
                                f"₹ {final_winning_bid:,}"
                            )

                            st.write("**Closing Transaction Hash:**")
                            st.code(tx_hash.hex())

                            st.write(
                                "**Closing Block Number:**",
                                receipt.blockNumber
                            )

                            st.info(
                                "The official winner and winning bid "
                                "have been retrieved from the smart contract."
                            )

                        except Exception as error:

                            st.error(
                                f"Unable to close Tender 4: {error}"
                            )

    st.divider()

    # ==================================================
    # TRANSACTION AUDIT TRAIL
    # ==================================================

    st.subheader("Transaction Audit Trail")

    audit_rows = []

    for record in tender_records:

        audit_rows.append({

            "Tender ID": record.get("tender_id"),

            "Contractor": record.get("bidder"),

            "Bid Status": record.get("status", "submitted"),

            "Commitment": record.get("commitment", "Not available"),

            "Submission Transaction": record.get(
                "transaction_hash",
                record.get("submit_transaction_hash", "Not saved")
            ),

            "Reveal Transaction": record.get(
                "reveal_transaction_hash",
                "Not saved"
            )
        })

    if audit_rows:

        st.dataframe(
            pd.DataFrame(audit_rows),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No local audit records found for Tender 4.")

    # ==================================================
    # CLOSING TRANSACTION RECORD
    # ==================================================

    close_tx = st.session_state.get(
        "tender4_close_tx"
    )

    close_block = st.session_state.get(
        "tender4_close_block"
    )

    if close_tx:

        st.subheader("Tender Closing Transaction")

        st.write("**Transaction Hash:**")
        st.code(close_tx)

        st.write("**Block Number:**", close_block)

    # ==================================================
    # FINAL STATUS
    # ==================================================

    if closed:

        st.success(
            "Tender 4 is permanently closed on the blockchain."
        )
