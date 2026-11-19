
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// ======================================================
// TENDERCHAIN
// Blockchain-Based Transparent Public Procurement
// ======================================================

contract TenderManagement {

    // ==================================================
    // 1. STATE VARIABLES
    // ==================================================

    address public owner;

    uint256 public nextTenderId = 1;

    // ==================================================
    // 2. TENDER STRUCTURE
    // ==================================================

    struct Tender {

        uint256 id;

        string title;

        string description;

        address authority;

        uint256 submissionDeadline;

        uint256 revealDeadline;

        bool closed;

        address winner;

        uint256 winningBid;
    }

    // ==================================================
    // 3. BID STRUCTURE
    // ==================================================

    struct Bid {

        bytes32 commitment;

        bool submitted;

        bool revealed;

        uint256 amount;
    }

    // ==================================================
    // 4. MAPPINGS
    // ==================================================

    mapping(uint256 => Tender) private tenders;

    mapping(uint256 => mapping(address => Bid))
        private bids;

    mapping(uint256 => mapping(address => bool))
        public registeredBidders;

    mapping(uint256 => address[]) private bidderLists;

    // ==================================================
    // 5. EVENTS
    // ==================================================

    event TenderCreated(
        uint256 indexed tenderId,
        string title,
        address indexed authority
    );

    event BidderRegistered(
        uint256 indexed tenderId,
        address indexed bidder
    );

    event BidSubmitted(
        uint256 indexed tenderId,
        address indexed bidder,
        bytes32 commitment
    );

    event BidRevealed(
        uint256 indexed tenderId,
        address indexed bidder,
        uint256 amount
    );

    event BidVerified(
        uint256 indexed tenderId,
        address indexed bidder,
        bool valid
    );

    event WinnerDeclared(
        uint256 indexed tenderId,
        address indexed winner,
        uint256 winningBid
    );

    // ==================================================
    // 6. MODIFIERS
    // ==================================================

    modifier onlyOwner() {

        require(
            msg.sender == owner,
            "Only tender authority can perform this action"
        );

        _;
    }

    // ==================================================
    // 7. CONSTRUCTOR
    // ==================================================

    constructor() {

        owner = msg.sender;
    }

    // ==================================================
    // 8. CREATE TENDER
    // ==================================================

    function createTender(
        string memory _title,
        string memory _description,
        uint256 _submissionDeadline,
        uint256 _revealDeadline
    )
        public
        onlyOwner
        returns (uint256)
    {

        require(
            bytes(_title).length > 0,
            "Tender title required"
        );

        require(
            _submissionDeadline > block.timestamp,
            "Submission deadline must be in future"
        );

        require(
            _revealDeadline > _submissionDeadline,
            "Reveal deadline must be after submission"
        );

        uint256 tenderId = nextTenderId;

        tenders[tenderId] = Tender({

            id: tenderId,

            title: _title,

            description: _description,

            authority: msg.sender,

            submissionDeadline: _submissionDeadline,

            revealDeadline: _revealDeadline,

            closed: false,

            winner: address(0),

            winningBid: 0
        });

        nextTenderId++;

        emit TenderCreated(
            tenderId,
            _title,
            msg.sender
        );

        return tenderId;
    }

    // ==================================================
    // 9. REGISTER BIDDER
    // ==================================================

    function registerBidder(
        uint256 _tenderId
    )
        public
    {

        require(
            _tenderId > 0 && _tenderId < nextTenderId,
            "Tender does not exist"
        );

        Tender storage tender = tenders[_tenderId];

        require(
            !tender.closed,
            "Tender is closed"
        );

        require(
            block.timestamp < tender.submissionDeadline,
            "Registration deadline passed"
        );

        require(
            !registeredBidders[_tenderId][msg.sender],
            "Already registered"
        );

        registeredBidders[_tenderId][msg.sender] = true;

        bidderLists[_tenderId].push(msg.sender);

        emit BidderRegistered(
            _tenderId,
            msg.sender
        );
    }

    // ==================================================
    // 10. SUBMIT SEALED BID
    // ==================================================

    function submitBid(
        uint256 _tenderId,
        bytes32 _commitment
    )
        public
    {

        Tender storage tender = tenders[_tenderId];

        require(
            _tenderId > 0 && _tenderId < nextTenderId,
            "Tender does not exist"
        );

        require(
            !tender.closed,
            "Tender is closed"
        );

        require(
            registeredBidders[_tenderId][msg.sender],
            "Bidder not registered"
        );

        require(
            block.timestamp < tender.submissionDeadline,
            "Submission deadline passed"
        );

        require(
            !bids[_tenderId][msg.sender].submitted,
            "Bid already submitted"
        );

        require(
            _commitment != bytes32(0),
            "Invalid commitment"
        );

        bids[_tenderId][msg.sender].commitment = _commitment;

        bids[_tenderId][msg.sender].submitted = true;

        emit BidSubmitted(
            _tenderId,
            msg.sender,
            _commitment
        );
    }

    // ==================================================
    // 11. REVEAL BID
    // ==================================================

    function revealBid(
        uint256 _tenderId,
        uint256 _bidAmount,
        bytes32 _nonce
    )
        public
    {

        Tender storage tender = tenders[_tenderId];

        Bid storage bid = bids[_tenderId][msg.sender];

        require(
            _tenderId > 0 && _tenderId < nextTenderId,
            "Tender does not exist"
        );

        require(
            !tender.closed,
            "Tender is closed"
        );

        require(
            block.timestamp >= tender.submissionDeadline,
            "Submission period not finished"
        );

        require(
            block.timestamp < tender.revealDeadline,
            "Reveal deadline passed"
        );

        require(
            bid.submitted,
            "No bid submitted"
        );

        require(
            !bid.revealed,
            "Bid already revealed"
        );

        // Recalculate SHA-256 commitment

        bytes32 calculatedHash = sha256(
            abi.encodePacked(
                _tenderId,
                msg.sender,
                _bidAmount,
                _nonce
            )
        );

        // Verify original commitment

        bool valid = (
            calculatedHash == bid.commitment
        );

        emit BidVerified(
            _tenderId,
            msg.sender,
            valid
        );

        require(
            valid,
            "Bid verification failed"
        );

        bid.amount = _bidAmount;

        bid.revealed = true;

        emit BidRevealed(
            _tenderId,
            msg.sender,
            _bidAmount
        );
    }

    // ==================================================
    // 12. CLOSE TENDER AND DECLARE WINNER
    // ==================================================

    function closeTender(
        uint256 _tenderId
    )
        public
        onlyOwner
    {

        Tender storage tender = tenders[_tenderId];

        require(
            _tenderId > 0 && _tenderId < nextTenderId,
            "Tender does not exist"
        );

        require(
            !tender.closed,
            "Tender already closed"
        );

        require(
            block.timestamp >= tender.revealDeadline,
            "Reveal period not finished"
        );

        address winningAddress = address(0);

        uint256 lowestBid = type(uint256).max;

        address[] storage bidders = bidderLists[_tenderId];

        // Find the lowest valid revealed bid

        for (uint256 i = 0; i < bidders.length; i++) {

            address bidder = bidders[i];

            Bid storage bid = bids[_tenderId][bidder];

            if (
                bid.submitted &&
                bid.revealed &&
                bid.amount > 0 &&
                bid.amount < lowestBid
            ) {

                lowestBid = bid.amount;

                winningAddress = bidder;
            }
        }

        tender.closed = true;

        tender.winner = winningAddress;

        if (winningAddress != address(0)) {

            tender.winningBid = lowestBid;

        } else {

            tender.winningBid = 0;
        }

        emit WinnerDeclared(
            _tenderId,
            winningAddress,
            tender.winningBid
        );
    }

    // ==================================================
    // 13. GET TENDER DETAILS
    // ==================================================

    function getTenderDetails(
        uint256 _tenderId
    )
        public
        view
        returns (
            uint256,
            string memory,
            string memory,
            address,
            uint256,
            uint256,
            bool,
            address,
            uint256
        )
    {

        Tender storage tender = tenders[_tenderId];

        require(
            _tenderId > 0 && _tenderId < nextTenderId,
            "Tender does not exist"
        );

        return (

            tender.id,

            tender.title,

            tender.description,

            tender.authority,

            tender.submissionDeadline,

            tender.revealDeadline,

            tender.closed,

            tender.winner,

            tender.winningBid
        );
    }

    // ==================================================
    // 14. GET BID DETAILS
    // ==================================================

    function getBidDetails(
        uint256 _tenderId,
        address _bidder
    )
        public
        view
        returns (
            bytes32,
            bool,
            bool,
            uint256
        )
    {

        require(
            _tenderId > 0 && _tenderId < nextTenderId,
            "Tender does not exist"
        );

        Bid storage bid = bids[_tenderId][_bidder];

        return (

            bid.commitment,

            bid.submitted,

            bid.revealed,

            bid.amount
        );
    }

    // ==================================================
    // 15. GET REGISTERED BIDDERS
    // ==================================================

    function getRegisteredBidders(
        uint256 _tenderId
    )
        public
        view
        returns (address[] memory)
    {

        require(
            _tenderId > 0 && _tenderId < nextTenderId,
            "Tender does not exist"
        );

        return bidderLists[_tenderId];
    }

}
