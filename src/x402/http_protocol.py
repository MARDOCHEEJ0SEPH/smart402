"""
X402 HTTP Protocol Implementation

This module implements the X402 protocol - an HTTP extension for
machine-readable commercial terms and automatic payments.

As specified in the Smart402 plan, X402 enables:
- Machine-to-machine payment negotiation
- Automatic condition detection
- Blockchain settlement integration
- Multi-sig dispute resolution
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import hashlib
import json


class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    CONDITIONS_MET = "conditions_met"
    PAYMENT_INITIATED = "payment_initiated"
    PAYMENT_COMPLETED = "payment_completed"
    DISPUTED = "disputed"
    RESOLVED = "resolved"
    FAILED = "failed"


class DisputeResolutionMethod(Enum):
    """Dispute resolution methods"""
    MULTISIG_2_OF_3 = "multisig_2_of_3"
    MULTISIG_3_OF_5 = "multisig_3_of_5"
    ORACLE_ARBITRATION = "oracle_arbitration"
    SMART_CONTRACT_AUTO = "smart_contract_auto"


@dataclass
class X402Headers:
    """
    X402 HTTP headers for machine-readable commercial terms

    These headers enable automatic payment processing when included
    in HTTP responses or requests.
    """
    contract_id: str
    parties: List[str]
    payment_token: str = "USDC"
    settlement_blockchain: str = "Polygon"
    settlement_address: str = ""
    payment_amount: Optional[float] = None
    payment_frequency: str = "monthly"
    payment_conditions: List[str] = field(default_factory=list)
    dispute_resolution: str = DisputeResolutionMethod.MULTISIG_2_OF_3.value
    webhook_endpoint: str = ""
    rate_limit: str = "100/hour"
    contract_version: str = "1.0"

    def to_http_headers(self) -> Dict[str, str]:
        """
        Convert to HTTP header dictionary

        Returns:
            Dictionary of X402 headers ready to be added to HTTP response
        """
        headers = {
            'X402-Contract-ID': self.contract_id,
            'X402-Parties': ','.join(self.parties),
            'X402-Payment-Token': self.payment_token,
            'X402-Settlement-Blockchain': self.settlement_blockchain,
            'X402-Settlement-Address': self.settlement_address,
            'X402-Payment-Frequency': self.payment_frequency,
            'X402-Dispute-Resolution': self.dispute_resolution,
            'X402-Webhook-Endpoint': self.webhook_endpoint,
            'X402-Rate-Limit': self.rate_limit,
            'X402-Contract-Version': self.contract_version
        }

        if self.payment_amount:
            headers['X402-Payment-Amount'] = str(self.payment_amount)

        if self.payment_conditions:
            headers['X402-Payment-Conditions'] = json.dumps(self.payment_conditions)

        return headers

    @classmethod
    def from_http_headers(cls, headers: Dict[str, str]) -> 'X402Headers':
        """
        Parse X402 headers from HTTP response

        Args:
            headers: HTTP headers dictionary

        Returns:
            X402Headers object
        """
        parties = headers.get('X402-Parties', '').split(',')

        payment_conditions = []
        conditions_json = headers.get('X402-Payment-Conditions', '')
        if conditions_json:
            try:
                payment_conditions = json.loads(conditions_json)
            except json.JSONDecodeError:
                payment_conditions = []

        return cls(
            contract_id=headers.get('X402-Contract-ID', ''),
            parties=[p.strip() for p in parties if p.strip()],
            payment_token=headers.get('X402-Payment-Token', 'USDC'),
            settlement_blockchain=headers.get('X402-Settlement-Blockchain', 'Polygon'),
            settlement_address=headers.get('X402-Settlement-Address', ''),
            payment_amount=float(headers['X402-Payment-Amount']) if 'X402-Payment-Amount' in headers else None,
            payment_frequency=headers.get('X402-Payment-Frequency', 'monthly'),
            payment_conditions=payment_conditions,
            dispute_resolution=headers.get('X402-Dispute-Resolution', 'multisig_2_of_3'),
            webhook_endpoint=headers.get('X402-Webhook-Endpoint', ''),
            rate_limit=headers.get('X402-Rate-Limit', '100/hour'),
            contract_version=headers.get('X402-Contract-Version', '1.0')
        )


@dataclass
class PaymentCondition:
    """
    Single payment condition that must be met
    """
    condition_id: str
    description: str
    data_source: str
    validation_method: str
    expected_value: Any
    current_value: Optional[Any] = None
    is_met: bool = False
    last_checked: Optional[datetime] = None

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate if condition is met

        Args:
            context: Current data context

        Returns:
            True if condition is satisfied
        """
        self.last_checked = datetime.now()

        # Get current value from context
        self.current_value = context.get(self.condition_id)

        # Evaluate based on validation method
        if self.validation_method == "equals":
            self.is_met = self.current_value == self.expected_value
        elif self.validation_method == "greater_than":
            self.is_met = float(self.current_value or 0) > float(self.expected_value)
        elif self.validation_method == "less_than":
            self.is_met = float(self.current_value or 0) < float(self.expected_value)
        elif self.validation_method == "boolean":
            self.is_met = bool(self.current_value)
        elif self.validation_method == "exists":
            self.is_met = self.current_value is not None
        else:
            self.is_met = False

        return self.is_met


@dataclass
class PaymentFlow:
    """
    Complete payment flow as per Smart402 spec:
    1. Condition Detection
    2. X402 Negotiation
    3. Payment Execution
    4. Confirmation
    """
    contract_id: str
    conditions: List[PaymentCondition]
    payment_amount: float
    payment_token: str = "USDC"
    settlement_blockchain: str = "Polygon"
    status: PaymentStatus = PaymentStatus.PENDING
    transaction_hash: Optional[str] = None
    initiated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    webhook_notifications: List[Dict] = field(default_factory=list)

    def check_conditions(self, context: Dict[str, Any]) -> bool:
        """
        Check if all payment conditions are met

        Args:
            context: Current data from oracles/APIs

        Returns:
            True if all conditions satisfied
        """
        all_met = True

        for condition in self.conditions:
            if not condition.evaluate(context):
                all_met = False

        if all_met:
            self.status = PaymentStatus.CONDITIONS_MET

        return all_met

    def initiate_payment(self, settlement_address: str) -> Dict[str, Any]:
        """
        Initiate blockchain payment

        Args:
            settlement_address: Blockchain address for settlement

        Returns:
            Payment initiation result
        """
        if self.status != PaymentStatus.CONDITIONS_MET:
            return {
                'success': False,
                'error': 'Conditions not met'
            }

        self.status = PaymentStatus.PAYMENT_INITIATED
        self.initiated_at = datetime.now()

        # Generate transaction hash (in production, this would be from blockchain)
        tx_data = f"{self.contract_id}:{self.payment_amount}:{settlement_address}:{self.initiated_at}"
        self.transaction_hash = hashlib.sha256(tx_data.encode()).hexdigest()

        return {
            'success': True,
            'tx_hash': self.transaction_hash,
            'amount': self.payment_amount,
            'token': self.payment_token,
            'blockchain': self.settlement_blockchain,
            'settlement_address': settlement_address
        }

    def confirm_payment(self, tx_hash: str) -> bool:
        """
        Confirm payment completion

        Args:
            tx_hash: Transaction hash from blockchain

        Returns:
            True if confirmed successfully
        """
        if tx_hash == self.transaction_hash:
            self.status = PaymentStatus.PAYMENT_COMPLETED
            self.completed_at = datetime.now()
            return True

        return False

    def send_webhook_notification(self, webhook_url: str, event: str, data: Dict) -> None:
        """
        Send webhook notification for payment events

        Args:
            webhook_url: Webhook endpoint URL
            event: Event type (condition_met, payment_initiated, payment_completed)
            data: Event data
        """
        notification = {
            'timestamp': datetime.now().isoformat(),
            'event': event,
            'contract_id': self.contract_id,
            'data': data,
            'webhook_url': webhook_url
        }

        self.webhook_notifications.append(notification)

        # In production, this would make actual HTTP POST to webhook_url
        # For now, we just log it
        print(f"Webhook notification: {event} -> {webhook_url}")


@dataclass
class RateAdjustment:
    """
    Dynamic rate adjustment based on performance or market conditions
    """
    base_rate: float
    adjustment_factors: Dict[str, float]
    min_rate: float
    max_rate: float

    def calculate_adjusted_rate(self, metrics: Dict[str, float]) -> float:
        """
        Calculate adjusted rate based on performance metrics

        Args:
            metrics: Current performance metrics

        Returns:
            Adjusted rate
        """
        adjusted_rate = self.base_rate

        for factor, weight in self.adjustment_factors.items():
            metric_value = metrics.get(factor, 1.0)
            adjusted_rate *= (1 + (metric_value - 1.0) * weight)

        # Clamp to min/max
        adjusted_rate = max(self.min_rate, min(self.max_rate, adjusted_rate))

        return adjusted_rate


@dataclass
class MultiSigEscrow:
    """
    Multi-signature escrow for dispute resolution

    As specified in Smart402 plan:
    - 2-of-3 multisig wallet
    - Vendor, reseller, and arbitrator each have one key
    - Requires 2 signatures to release funds
    """
    escrow_id: str
    contract_id: str
    amount: float
    token: str
    signers: List[str]  # [vendor, reseller, arbitrator]
    signatures_required: int = 2
    signatures_collected: List[str] = field(default_factory=list)
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.now)

    def add_signature(self, signer: str, signature: str) -> bool:
        """
        Add signature from one of the signers

        Args:
            signer: Signer address
            signature: Cryptographic signature

        Returns:
            True if signature added successfully
        """
        if signer not in self.signers:
            return False

        if signer in self.signatures_collected:
            return False  # Already signed

        self.signatures_collected.append(signer)

        return True

    def can_release_funds(self) -> bool:
        """
        Check if enough signatures collected to release funds

        Returns:
            True if can release
        """
        return len(self.signatures_collected) >= self.signatures_required

    def release_funds(self, recipient: str) -> Dict[str, Any]:
        """
        Release escrowed funds to recipient

        Args:
            recipient: Address to receive funds

        Returns:
            Release result
        """
        if not self.can_release_funds():
            return {
                'success': False,
                'error': f'Need {self.signatures_required} signatures, have {len(self.signatures_collected)}'
            }

        self.status = "released"

        # Generate transaction hash
        tx_data = f"{self.escrow_id}:{recipient}:{self.amount}:{datetime.now()}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()

        return {
            'success': True,
            'tx_hash': tx_hash,
            'amount': self.amount,
            'token': self.token,
            'recipient': recipient,
            'signers': self.signatures_collected
        }


class X402Protocol:
    """
    Main X402 Protocol handler

    Orchestrates the complete payment flow:
    1. Parse X402 headers from HTTP response
    2. Monitor payment conditions
    3. Trigger payment when conditions met
    4. Handle disputes via multi-sig escrow
    """

    def __init__(self):
        self.active_flows: Dict[str, PaymentFlow] = {}
        self.escrows: Dict[str, MultiSigEscrow] = {}

    def create_payment_flow(
        self,
        contract_id: str,
        conditions: List[PaymentCondition],
        payment_amount: float,
        payment_token: str = "USDC",
        settlement_blockchain: str = "Polygon"
    ) -> PaymentFlow:
        """
        Create new payment flow

        Args:
            contract_id: Contract identifier
            conditions: List of payment conditions
            payment_amount: Amount to pay
            payment_token: Payment token (default USDC)
            settlement_blockchain: Target blockchain

        Returns:
            PaymentFlow object
        """
        flow = PaymentFlow(
            contract_id=contract_id,
            conditions=conditions,
            payment_amount=payment_amount,
            payment_token=payment_token,
            settlement_blockchain=settlement_blockchain
        )

        self.active_flows[contract_id] = flow

        return flow

    def process_x402_response(self, headers: Dict[str, str], body: Dict[str, Any]) -> Optional[PaymentFlow]:
        """
        Process HTTP response with X402 headers

        Args:
            headers: HTTP response headers
            body: Response body with data

        Returns:
            PaymentFlow if X402 headers present
        """
        # Check if X402 headers present
        if 'X402-Contract-ID' not in headers:
            return None

        # Parse X402 headers
        x402_headers = X402Headers.from_http_headers(headers)

        # Create payment conditions from header
        conditions = [
            PaymentCondition(
                condition_id=cond,
                description=cond,
                data_source="http_response",
                validation_method="boolean",
                expected_value=True
            )
            for cond in x402_headers.payment_conditions
        ]

        # Create payment flow
        flow = self.create_payment_flow(
            contract_id=x402_headers.contract_id,
            conditions=conditions,
            payment_amount=x402_headers.payment_amount or 0,
            payment_token=x402_headers.payment_token,
            settlement_blockchain=x402_headers.settlement_blockchain
        )

        return flow

    def create_escrow(
        self,
        contract_id: str,
        amount: float,
        token: str,
        vendor: str,
        reseller: str,
        arbitrator: str
    ) -> MultiSigEscrow:
        """
        Create multi-sig escrow for dispute resolution

        Args:
            contract_id: Contract ID
            amount: Escrow amount
            token: Token type
            vendor: Vendor address
            reseller: Reseller address
            arbitrator: Arbitrator address

        Returns:
            MultiSigEscrow object
        """
        escrow_id = hashlib.sha256(f"{contract_id}:{datetime.now()}".encode()).hexdigest()[:16]

        escrow = MultiSigEscrow(
            escrow_id=escrow_id,
            contract_id=contract_id,
            amount=amount,
            token=token,
            signers=[vendor, reseller, arbitrator],
            signatures_required=2
        )

        self.escrows[escrow_id] = escrow

        return escrow

    def get_payment_status(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current payment status for contract

        Args:
            contract_id: Contract ID

        Returns:
            Status dictionary
        """
        if contract_id not in self.active_flows:
            return None

        flow = self.active_flows[contract_id]

        return {
            'contract_id': contract_id,
            'status': flow.status.value,
            'payment_amount': flow.payment_amount,
            'conditions_met': all(c.is_met for c in flow.conditions),
            'conditions': [
                {
                    'id': c.condition_id,
                    'description': c.description,
                    'is_met': c.is_met,
                    'current_value': c.current_value,
                    'expected_value': c.expected_value
                }
                for c in flow.conditions
            ],
            'transaction_hash': flow.transaction_hash,
            'initiated_at': flow.initiated_at.isoformat() if flow.initiated_at else None,
            'completed_at': flow.completed_at.isoformat() if flow.completed_at else None
        }


# Example usage and testing
if __name__ == "__main__":
    # Create X402 protocol handler
    protocol = X402Protocol()

    # Example: Create payment flow for SaaS reseller
    conditions = [
        PaymentCondition(
            condition_id="monthly_revenue_reported",
            description="Monthly revenue has been reported",
            data_source="reseller_api",
            validation_method="boolean",
            expected_value=True
        ),
        PaymentCondition(
            condition_id="revenue_amount",
            description="Revenue exceeds minimum threshold",
            data_source="reseller_api",
            validation_method="greater_than",
            expected_value=100000
        ),
        PaymentCondition(
            condition_id="uptime_sla",
            description="Uptime SLA met (99%)",
            data_source="monitoring_api",
            validation_method="greater_than",
            expected_value=0.99
        )
    ]

    flow = protocol.create_payment_flow(
        contract_id="saas_reseller_001",
        conditions=conditions,
        payment_amount=15000,  # 15% of $100k
        payment_token="USDC",
        settlement_blockchain="Polygon"
    )

    print(f"Created payment flow: {flow.contract_id}")
    print(f"Status: {flow.status.value}")

    # Simulate condition checking
    context = {
        "monthly_revenue_reported": True,
        "revenue_amount": 120000,
        "uptime_sla": 0.995
    }

    if flow.check_conditions(context):
        print("All conditions met!")

        # Initiate payment
        result = flow.initiate_payment("0x1234567890abcdef")
        print(f"Payment initiated: {result['tx_hash']}")

        # Confirm payment
        flow.confirm_payment(result['tx_hash'])
        print(f"Payment completed at: {flow.completed_at}")

    # Create multi-sig escrow for dispute
    escrow = protocol.create_escrow(
        contract_id="saas_reseller_001",
        amount=15000,
        token="USDC",
        vendor="0xvendor",
        reseller="0xreseller",
        arbitrator="0xarbitrator"
    )

    print(f"\nCreated escrow: {escrow.escrow_id}")

    # Add signatures
    escrow.add_signature("0xvendor", "sig1")
    escrow.add_signature("0xarbitrator", "sig2")

    if escrow.can_release_funds():
        release = escrow.release_funds("0xreseller")
        print(f"Funds released: {release['tx_hash']}")
