// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import "@chainlink/contracts/src/v0.8/ConfirmedOwner.sol";

/**
 * @title RobotServiceContract
 * @dev Smart402-powered autonomous robot service marketplace
 * Enables trustless rental, task execution, and payment for robot services
 */
contract RobotServiceContract is
    Ownable,
    ReentrancyGuard,
    Pausable,
    ChainlinkClient,
    ConfirmedOwner
{
    using Chainlink for Chainlink.Request;

    // ==================== Structs ====================

    struct Robot {
        string robotId;
        address owner;
        RobotType robotType;
        RobotStatus status;
        uint256 hourlyRate; // in USDC (6 decimals)
        uint256 totalUptime;
        uint256 tasksCompleted;
        uint256 reputationScore; // 0-10000 (100.00%)
        string metadataURI; // IPFS or Arweave URI
        bool isActive;
    }

    struct ServiceContract {
        bytes32 contractId;
        address client;
        string robotId;
        uint256 startTime;
        uint256 endTime;
        uint256 totalCost;
        uint256 paidAmount;
        ContractStatus status;
        string taskDescription;
        bytes32[] milestones;
        bool autoRenew;
    }

    struct Milestone {
        bytes32 milestoneId;
        bytes32 contractId;
        string description;
        uint256 amount;
        bool completed;
        bool paid;
        uint256 completedAt;
        bytes32 chainlinkRequestId;
    }

    struct TelemetryData {
        string robotId;
        uint256 timestamp;
        bytes32 dataHash;
        bool verified;
        bytes32 chainlinkRequestId;
    }

    // ==================== Enums ====================

    enum RobotType { Industrial, Warehouse, Service, Mobile, Drone, Specialized }
    enum RobotStatus { Available, Busy, Maintenance, Offline, Error }
    enum ContractStatus { Pending, Active, Completed, Cancelled, Disputed }

    // ==================== State Variables ====================

    IERC20 public paymentToken; // USDC or other stablecoin
    uint256 public platformFee = 250; // 2.5% (basis points)
    uint256 public constant PRECISION = 10000;

    mapping(string => Robot) public robots;
    mapping(bytes32 => ServiceContract) public contracts;
    mapping(bytes32 => Milestone) public milestones;
    mapping(string => TelemetryData[]) public telemetryHistory;
    mapping(address => uint256) public escrowBalance;
    mapping(bytes32 => bytes32) public chainlinkRequests; // requestId => contractId

    string[] public robotIds;
    bytes32[] public activeContracts;

    // Chainlink Configuration
    uint256 private chainlinkFee;
    bytes32 private jobId;

    // ==================== Events ====================

    event RobotRegistered(string indexed robotId, address indexed owner, RobotType robotType);
    event RobotStatusUpdated(string indexed robotId, RobotStatus newStatus);
    event ContractCreated(bytes32 indexed contractId, string indexed robotId, address indexed client);
    event ContractStarted(bytes32 indexed contractId);
    event ContractCompleted(bytes32 indexed contractId, uint256 totalPaid);
    event MilestoneCreated(bytes32 indexed milestoneId, bytes32 indexed contractId);
    event MilestoneCompleted(bytes32 indexed milestoneId, uint256 amount);
    event PaymentProcessed(bytes32 indexed contractId, uint256 amount, address indexed recipient);
    event TelemetryVerified(string indexed robotId, bytes32 dataHash, bytes32 requestId);
    event DisputeRaised(bytes32 indexed contractId, address indexed raiser);
    event FundsDeposited(address indexed user, uint256 amount);
    event FundsWithdrawn(address indexed user, uint256 amount);

    // ==================== Constructor ====================

    constructor(
        address _paymentToken,
        address _chainlinkToken,
        address _chainlinkOracle,
        bytes32 _jobId
    ) ConfirmedOwner(msg.sender) {
        paymentToken = IERC20(_paymentToken);
        setChainlinkToken(_chainlinkToken);
        setChainlinkOracle(_chainlinkOracle);
        jobId = _jobId;
        chainlinkFee = (1 * LINK_DIVISIBILITY) / 10; // 0.1 LINK
    }

    // ==================== Robot Management ====================

    /**
     * @dev Register a new robot to the marketplace
     */
    function registerRobot(
        string memory _robotId,
        RobotType _robotType,
        uint256 _hourlyRate,
        string memory _metadataURI
    ) external whenNotPaused {
        require(bytes(robots[_robotId].robotId).length == 0, "Robot already registered");
        require(_hourlyRate > 0, "Invalid hourly rate");

        robots[_robotId] = Robot({
            robotId: _robotId,
            owner: msg.sender,
            robotType: _robotType,
            status: RobotStatus.Available,
            hourlyRate: _hourlyRate,
            totalUptime: 0,
            tasksCompleted: 0,
            reputationScore: 5000, // Start at 50%
            metadataURI: _metadataURI,
            isActive: true
        });

        robotIds.push(_robotId);

        emit RobotRegistered(_robotId, msg.sender, _robotType);
    }

    /**
     * @dev Update robot status
     */
    function updateRobotStatus(string memory _robotId, RobotStatus _newStatus) external {
        require(robots[_robotId].owner == msg.sender, "Not robot owner");

        robots[_robotId].status = _newStatus;

        emit RobotStatusUpdated(_robotId, _newStatus);
    }

    /**
     * @dev Update robot hourly rate
     */
    function updateRobotRate(string memory _robotId, uint256 _newRate) external {
        require(robots[_robotId].owner == msg.sender, "Not robot owner");
        require(_newRate > 0, "Invalid rate");

        robots[_robotId].hourlyRate = _newRate;
    }

    // ==================== Contract Management ====================

    /**
     * @dev Create a new service contract
     */
    function createContract(
        string memory _robotId,
        uint256 _durationHours,
        string memory _taskDescription,
        bool _autoRenew
    ) external whenNotPaused returns (bytes32) {
        require(robots[_robotId].isActive, "Robot not active");
        require(robots[_robotId].status == RobotStatus.Available, "Robot not available");
        require(_durationHours > 0, "Invalid duration");

        bytes32 contractId = keccak256(abi.encodePacked(
            msg.sender,
            _robotId,
            block.timestamp,
            _taskDescription
        ));

        uint256 totalCost = robots[_robotId].hourlyRate * _durationHours;

        // Require client to deposit funds
        require(
            paymentToken.transferFrom(msg.sender, address(this), totalCost),
            "Payment transfer failed"
        );

        contracts[contractId] = ServiceContract({
            contractId: contractId,
            client: msg.sender,
            robotId: _robotId,
            startTime: 0, // Will be set when started
            endTime: 0,
            totalCost: totalCost,
            paidAmount: 0,
            status: ContractStatus.Pending,
            taskDescription: _taskDescription,
            milestones: new bytes32[](0),
            autoRenew: _autoRenew
        });

        activeContracts.push(contractId);
        escrowBalance[msg.sender] += totalCost;

        emit ContractCreated(contractId, _robotId, msg.sender);

        return contractId;
    }

    /**
     * @dev Start an approved contract
     */
    function startContract(bytes32 _contractId) external {
        ServiceContract storage serviceContract = contracts[_contractId];
        require(serviceContract.status == ContractStatus.Pending, "Contract not pending");
        require(
            msg.sender == serviceContract.client ||
            msg.sender == robots[serviceContract.robotId].owner,
            "Not authorized"
        );

        serviceContract.status = ContractStatus.Active;
        serviceContract.startTime = block.timestamp;

        robots[serviceContract.robotId].status = RobotStatus.Busy;

        emit ContractStarted(_contractId);
    }

    /**
     * @dev Complete a contract and process payment
     */
    function completeContract(bytes32 _contractId) external nonReentrant {
        ServiceContract storage serviceContract = contracts[_contractId];
        require(serviceContract.status == ContractStatus.Active, "Contract not active");
        require(msg.sender == robots[serviceContract.robotId].owner, "Not robot owner");

        serviceContract.status = ContractStatus.Completed;
        serviceContract.endTime = block.timestamp;

        // Calculate actual duration and cost
        uint256 actualHours = (serviceContract.endTime - serviceContract.startTime) / 3600;
        uint256 actualCost = robots[serviceContract.robotId].hourlyRate * actualHours;

        if (actualCost > serviceContract.totalCost) {
            actualCost = serviceContract.totalCost;
        }

        // Calculate platform fee
        uint256 fee = (actualCost * platformFee) / PRECISION;
        uint256 robotOwnerPayment = actualCost - fee;

        // Process payment
        address robotOwner = robots[serviceContract.robotId].owner;

        require(paymentToken.transfer(robotOwner, robotOwnerPayment), "Payment failed");
        require(paymentToken.transfer(owner(), fee), "Fee transfer failed");

        serviceContract.paidAmount = actualCost;
        escrowBalance[serviceContract.client] -= actualCost;

        // Refund unused funds
        uint256 refund = serviceContract.totalCost - actualCost;
        if (refund > 0) {
            require(paymentToken.transfer(serviceContract.client, refund), "Refund failed");
            escrowBalance[serviceContract.client] -= refund;
        }

        // Update robot stats
        robots[serviceContract.robotId].status = RobotStatus.Available;
        robots[serviceContract.robotId].tasksCompleted += 1;
        robots[serviceContract.robotId].totalUptime += (serviceContract.endTime - serviceContract.startTime);

        emit ContractCompleted(_contractId, actualCost);
        emit PaymentProcessed(_contractId, robotOwnerPayment, robotOwner);
    }

    // ==================== Milestone Management ====================

    /**
     * @dev Add milestone to a contract
     */
    function addMilestone(
        bytes32 _contractId,
        string memory _description,
        uint256 _amount
    ) external returns (bytes32) {
        ServiceContract storage serviceContract = contracts[_contractId];
        require(msg.sender == serviceContract.client, "Not contract client");
        require(serviceContract.status == ContractStatus.Pending, "Contract already started");

        bytes32 milestoneId = keccak256(abi.encodePacked(
            _contractId,
            _description,
            block.timestamp
        ));

        milestones[milestoneId] = Milestone({
            milestoneId: milestoneId,
            contractId: _contractId,
            description: _description,
            amount: _amount,
            completed: false,
            paid: false,
            completedAt: 0,
            chainlinkRequestId: bytes32(0)
        });

        serviceContract.milestones.push(milestoneId);

        emit MilestoneCreated(milestoneId, _contractId);

        return milestoneId;
    }

    /**
     * @dev Complete milestone and release payment
     */
    function completeMilestone(bytes32 _milestoneId) external nonReentrant {
        Milestone storage milestone = milestones[_milestoneId];
        ServiceContract storage serviceContract = contracts[milestone.contractId];

        require(!milestone.completed, "Already completed");
        require(msg.sender == robots[serviceContract.robotId].owner, "Not authorized");

        milestone.completed = true;
        milestone.completedAt = block.timestamp;

        // Release milestone payment
        address robotOwner = robots[serviceContract.robotId].owner;
        uint256 fee = (milestone.amount * platformFee) / PRECISION;
        uint256 payment = milestone.amount - fee;

        require(paymentToken.transfer(robotOwner, payment), "Payment failed");
        require(paymentToken.transfer(owner(), fee), "Fee transfer failed");

        milestone.paid = true;
        serviceContract.paidAmount += milestone.amount;
        escrowBalance[serviceContract.client] -= milestone.amount;

        emit MilestoneCompleted(_milestoneId, payment);
        emit PaymentProcessed(milestone.contractId, payment, robotOwner);
    }

    // ==================== Chainlink Oracle Integration ====================

    /**
     * @dev Request telemetry verification from Chainlink oracle
     */
    function requestTelemetryVerification(
        string memory _robotId,
        bytes32 _dataHash
    ) external returns (bytes32 requestId) {
        Chainlink.Request memory req = buildChainlinkRequest(
            jobId,
            address(this),
            this.fulfillTelemetryVerification.selector
        );

        req.add("robotId", _robotId);
        req.addBytes("dataHash", abi.encodePacked(_dataHash));

        requestId = sendChainlinkRequest(req, chainlinkFee);

        chainlinkRequests[requestId] = _dataHash;

        return requestId;
    }

    /**
     * @dev Chainlink callback for telemetry verification
     */
    function fulfillTelemetryVerification(
        bytes32 _requestId,
        bool _verified
    ) public recordChainlinkFulfillment(_requestId) {
        bytes32 dataHash = chainlinkRequests[_requestId];

        // Store verified telemetry
        // (Implementation depends on specific telemetry structure)

        emit TelemetryVerified("", dataHash, _requestId);
    }

    // ==================== Dispute Management ====================

    /**
     * @dev Raise a dispute for a contract
     */
    function raiseDispute(bytes32 _contractId) external {
        ServiceContract storage serviceContract = contracts[_contractId];
        require(
            msg.sender == serviceContract.client ||
            msg.sender == robots[serviceContract.robotId].owner,
            "Not authorized"
        );
        require(
            serviceContract.status == ContractStatus.Active ||
            serviceContract.status == ContractStatus.Completed,
            "Invalid contract status"
        );

        serviceContract.status = ContractStatus.Disputed;

        emit DisputeRaised(_contractId, msg.sender);
    }

    // ==================== View Functions ====================

    function getRobot(string memory _robotId) external view returns (Robot memory) {
        return robots[_robotId];
    }

    function getContract(bytes32 _contractId) external view returns (ServiceContract memory) {
        return contracts[_contractId];
    }

    function getMilestone(bytes32 _milestoneId) external view returns (Milestone memory) {
        return milestones[_milestoneId];
    }

    function getActiveContractCount() external view returns (uint256) {
        return activeContracts.length;
    }

    function getRobotCount() external view returns (uint256) {
        return robotIds.length;
    }

    // ==================== Admin Functions ====================

    function setPlatformFee(uint256 _newFee) external onlyOwner {
        require(_newFee <= 1000, "Fee too high"); // Max 10%
        platformFee = _newFee;
    }

    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }

    function withdrawLINK() external onlyOwner {
        LinkTokenInterface link = LinkTokenInterface(chainlinkTokenAddress());
        require(link.transfer(msg.sender, link.balanceOf(address(this))), "Unable to transfer");
    }
}
