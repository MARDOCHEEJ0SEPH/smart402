"""
Contract Class

Represents a Smart402 contract instance with full lifecycle management.
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime


class ContractStatus(Enum):
    """Contract status enumeration."""

    DRAFT = "draft"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class Contract:
    """
    Smart402 contract instance.

    Example:
        >>> contract = Contract(ucl=ucl_data, aeo=aeo_data, x402=client, options={})
        >>> await contract.deploy(network='polygon')
        >>> await contract.start_monitoring(frequency='hourly')
    """

    def __init__(
        self,
        ucl: Dict[str, Any],
        aeo: Dict[str, Any],
        x402: Any,
        options: Dict[str, Any],
    ):
        """
        Initialize contract instance.

        Args:
            ucl: UCL contract data
            aeo: AEO metadata
            x402: X402 client instance
            options: SDK options
        """
        self.ucl = ucl
        self.aeo = aeo
        self.x402 = x402
        self.options = options
        self.id = ucl["contract_id"]
        self._status = ContractStatus.DRAFT
        self._deployed_address: Optional[str] = None
        self._transaction_hash: Optional[str] = None

    async def deploy(
        self,
        network: Optional[str] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Deploy contract to blockchain.

        Args:
            network: Blockchain network
            gas_limit: Gas limit for deployment
            gas_price: Gas price

        Returns:
            Deployment result dictionary

        Example:
            >>> result = await contract.deploy(network='polygon')
            >>> print(f"Deployed to: {result['address']}")
        """
        if self._status == ContractStatus.DEPLOYED:
            raise ValueError("Contract already deployed")

        self._status = ContractStatus.DEPLOYING

        try:
            # Compile UCL to Solidity
            solidity = await self.compile("solidity")

            # Deploy to blockchain
            deployment = await self.x402.deploy(
                code=solidity,
                network=network or self.options.get("network", "polygon"),
                gas_limit=gas_limit,
                gas_price=gas_price,
            )

            self._deployed_address = deployment["address"]
            self._transaction_hash = deployment["transaction_hash"]
            self._status = ContractStatus.DEPLOYED

            # Register in Smart402 registry
            await self._register()

            return {
                "success": True,
                "address": deployment["address"],
                "transaction_hash": deployment["transaction_hash"],
                "network": deployment["network"],
                "block_number": deployment.get("block_number"),
                "contract_id": self.id,
            }

        except Exception as e:
            self._status = ContractStatus.FAILED
            raise e

    async def compile(self, target: str = "solidity") -> str:
        """
        Compile contract to target language.

        Args:
            target: Target language ('solidity', 'javascript', 'rust')

        Returns:
            Compiled contract code

        Example:
            >>> solidity = await contract.compile('solidity')
            >>> javascript = await contract.compile('javascript')
        """
        from ..utils.compiler import compile_contract

        return await compile_contract(self.ucl, target=target)

    async def execute_payment(
        self,
        amount: Optional[float] = None,
        from_address: Optional[str] = None,
        to_address: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute payment manually.

        Args:
            amount: Payment amount (defaults to contract amount)
            from_address: Sender address
            to_address: Recipient address

        Returns:
            Payment result

        Example:
            >>> result = await contract.execute_payment()
            >>> print(f"Payment: {result['transaction_hash']}")
        """
        if self._status != ContractStatus.DEPLOYED:
            raise ValueError("Contract must be deployed before executing payments")

        payment = await self.x402.execute_payment(
            contract_id=self.id,
            contract_address=self._deployed_address,
            amount=amount or self.ucl["payment"]["amount"],
            token=self.ucl["payment"]["token"],
            network=self.options.get("network", "polygon"),
            from_address=from_address,
            to_address=to_address,
        )

        return payment

    async def start_monitoring(
        self,
        frequency: str = "medium",
        webhook: Optional[str] = None,
    ) -> None:
        """
        Start automatic monitoring and execution.

        Args:
            frequency: Monitoring frequency ('realtime', 'high', 'medium', 'low', 'daily')
            webhook: Webhook URL for notifications

        Example:
            >>> await contract.start_monitoring(frequency='hourly', webhook='https://...')
        """
        if self._status != ContractStatus.DEPLOYED:
            raise ValueError("Contract must be deployed before monitoring")

        await self.x402.start_monitoring(
            contract_id=self.id,
            contract_address=self._deployed_address,
            conditions=self.ucl.get("conditions", {}).get("required", []),
            oracles=self.ucl.get("oracles", []),
            frequency=frequency,
            webhook=webhook,
        )

        print(f"Monitoring started for contract {self.id}")

    async def stop_monitoring(self) -> None:
        """Stop automatic monitoring."""
        await self.x402.stop_monitoring(self.id)
        print(f"Monitoring stopped for contract {self.id}")

    async def check_conditions(self) -> Dict[str, Any]:
        """
        Check if conditions are met.

        Returns:
            Condition check result

        Example:
            >>> status = await contract.check_conditions()
            >>> print(f"All met: {status['all_met']}")
        """
        result = await self.x402.check_conditions(
            contract_id=self.id,
            conditions=self.ucl.get("conditions", {}).get("required", []),
            oracles=self.ucl.get("oracles", []),
        )

        return result

    async def export(self, format: str = "yaml") -> str:
        """
        Export contract to format.

        Args:
            format: Export format ('yaml', 'json', 'ucl')

        Returns:
            Exported contract string

        Example:
            >>> yaml_str = await contract.export('yaml')
            >>> json_str = await contract.export('json')
        """
        from ..utils.export import export_contract

        return await export_contract(self.ucl, format=format)

    def get_summary(self) -> str:
        """
        Get natural language summary.

        Returns:
            Contract summary

        Example:
            >>> print(contract.get_summary())
        """
        return self.ucl.get("summary", {}).get("plain_english", "No summary available")

    def get_aeo_score(self) -> float:
        """
        Get AEO discoverability score.

        Returns:
            AEO score (0-100)
        """
        return self.aeo.get("score", 0)

    def get_parties(self) -> List[Dict[str, str]]:
        """
        Get contract parties.

        Returns:
            List of parties
        """
        return self.ucl.get("metadata", {}).get("parties", [])

    def get_payment_terms(self) -> Dict[str, Any]:
        """
        Get payment terms.

        Returns:
            Payment terms dictionary
        """
        payment = self.ucl.get("payment", {})
        return {
            "amount": payment.get("amount"),
            "frequency": payment.get("frequency"),
            "token": payment.get("token"),
            "blockchain": payment.get("blockchain"),
        }

    async def validate(self) -> Dict[str, Any]:
        """
        Validate contract structure.

        Returns:
            Validation result
        """
        from ..utils.validator import validate_ucl

        return await validate_ucl(self.ucl)

    def get_url(self) -> str:
        """
        Get contract URL for viewing.

        Returns:
            Contract URL
        """
        if self._deployed_address:
            network = self.options.get("network", "polygon")
            explorer = self._get_explorer_url(network)
            return f"{explorer}/address/{self._deployed_address}"
        return f"https://smart402.io/contracts/{self.id}"

    def _get_explorer_url(self, network: str) -> str:
        """Get block explorer URL for network."""
        explorers = {
            "ethereum": "https://etherscan.io",
            "polygon": "https://polygonscan.com",
            "arbitrum": "https://arbiscan.io",
            "optimism": "https://optimistic.etherscan.io",
            "base": "https://basescan.org",
        }
        return explorers.get(network, explorers["polygon"])

    async def _register(self) -> None:
        """Register contract in Smart402 registry."""
        print(f"Registering contract {self.id} in registry...")
        # Placeholder for registry registration

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert contract to dictionary.

        Returns:
            Contract dictionary
        """
        return {
            "id": self.id,
            "ucl": self.ucl,
            "aeo": self.aeo,
            "status": self._status.value,
            "address": self._deployed_address,
            "transaction_hash": self._transaction_hash,
        }

    @property
    def status(self) -> ContractStatus:
        """Get contract status."""
        return self._status

    @property
    def address(self) -> Optional[str]:
        """Get deployed address."""
        return self._deployed_address

    @property
    def transaction_hash(self) -> Optional[str]:
        """Get deployment transaction hash."""
        return self._transaction_hash
