"""
Smart402 Main Class

Entry point for creating and managing AI-native smart contracts.
"""

from typing import Dict, Any, Optional, List
from .contract import Contract
from ..aeo.engine import AEOEngine
from ..llmo.engine import LLMOEngine
from ..x402.client import X402Client


class Smart402:
    """
    Main Smart402 SDK class for creating and managing contracts.

    Example:
        >>> smart402 = Smart402(network='polygon', private_key=key)
        >>> contract = await smart402.create_contract({
        ...     'type': 'saas-subscription',
        ...     'parties': ['vendor@example.com', 'customer@example.com'],
        ...     'payment': {'amount': 99, 'frequency': 'monthly', 'token': 'USDC'}
        ... })
        >>> await contract.deploy()
    """

    def __init__(
        self,
        network: str = "polygon",
        private_key: Optional[str] = None,
        rpc_url: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Smart402 SDK.

        Args:
            network: Blockchain network ('polygon', 'ethereum', 'arbitrum', etc.)
            private_key: Private key for transactions
            rpc_url: Custom RPC endpoint URL
            api_key: API key for Smart402 services
            **kwargs: Additional configuration options
        """
        self.options = {
            "network": network,
            "private_key": private_key,
            "rpc_url": rpc_url,
            "api_key": api_key,
            **kwargs,
        }

        self.aeo = AEOEngine(self.options)
        self.llmo = LLMOEngine(self.options)
        self.x402 = X402Client(self.options)

    @classmethod
    async def create(cls, config: Dict[str, Any], **options) -> Contract:
        """
        Create a new Smart402 contract (class method).

        Args:
            config: Contract configuration dictionary
            **options: SDK initialization options

        Returns:
            Contract instance

        Example:
            >>> contract = await Smart402.create({
            ...     'type': 'saas-subscription',
            ...     'parties': ['vendor@example.com', 'customer@example.com'],
            ...     'payment': {'amount': 99, 'frequency': 'monthly', 'token': 'USDC'}
            ... })
        """
        instance = cls(**options)
        return await instance.create_contract(config)

    @classmethod
    async def from_template(
        cls, template_name: str, variables: Dict[str, Any], **options
    ) -> Contract:
        """
        Create contract from template (class method).

        Args:
            template_name: Name of template to use
            variables: Template variables
            **options: SDK initialization options

        Returns:
            Contract instance

        Example:
            >>> contract = await Smart402.from_template('saas-subscription', {
            ...     'vendor': '0xVendor...',
            ...     'customer': '0xCustomer...',
            ...     'monthly_price': 99
            ... })
        """
        instance = cls(**options)
        return await instance.create_from_template(template_name, variables)

    @classmethod
    async def load(cls, contract_id: str, **options) -> Contract:
        """
        Load existing contract by ID (class method).

        Args:
            contract_id: Contract ID to load
            **options: SDK initialization options

        Returns:
            Contract instance

        Example:
            >>> contract = await Smart402.load('smart402:saas:abc123')
        """
        instance = cls(**options)
        return await instance.load_contract(contract_id)

    async def create_contract(self, config: Dict[str, Any]) -> Contract:
        """
        Create contract instance.

        Args:
            config: Contract configuration

        Returns:
            Contract instance
        """
        # Generate UCL contract using LLMO
        ucl_contract = await self.llmo.generate_ucl(config)

        # Optimize for AI discovery using AEO
        aeo_metadata = await self.aeo.optimize(ucl_contract)

        # Create contract instance
        contract = Contract(
            ucl=ucl_contract,
            aeo=aeo_metadata,
            x402=self.x402,
            options=self.options,
        )

        return contract

    async def create_from_template(
        self, template_name: str, variables: Dict[str, Any]
    ) -> Contract:
        """
        Create contract from template.

        Args:
            template_name: Template name
            variables: Template variables

        Returns:
            Contract instance
        """
        from ..core.templates import get_template

        template = get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")

        config = template.instantiate(variables)
        return await self.create_contract(config)

    async def load_contract(self, contract_id: str) -> Contract:
        """
        Load existing contract.

        Args:
            contract_id: Contract ID

        Returns:
            Contract instance
        """
        # Fetch contract from registry
        ucl_contract = await self.llmo.fetch_contract(contract_id)
        aeo_metadata = await self.aeo.fetch_metadata(contract_id)

        contract = Contract(
            ucl=ucl_contract,
            aeo=aeo_metadata,
            x402=self.x402,
            options=self.options,
        )

        return contract

    @staticmethod
    def get_templates() -> List[str]:
        """
        Get list of available templates.

        Returns:
            List of template names
        """
        from ..core.templates import TEMPLATES

        return list(TEMPLATES.keys())

    @staticmethod
    def get_template_doc(template_name: str) -> Dict[str, Any]:
        """
        Get template documentation.

        Args:
            template_name: Template name

        Returns:
            Template documentation

        Raises:
            ValueError: If template not found
        """
        from ..core.templates import get_template

        template = get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")

        return template.documentation

    @property
    def aeo_engine(self) -> AEOEngine:
        """Access AEO engine directly."""
        return self.aeo

    @property
    def llmo_engine(self) -> LLMOEngine:
        """Access LLMO engine directly."""
        return self.llmo

    @property
    def x402_client(self) -> X402Client:
        """Access X402 client directly."""
        return self.x402


# Convenience functions
async def create(config: Dict[str, Any], **options) -> Contract:
    """
    Create contract (convenience function).

    Args:
        config: Contract configuration
        **options: SDK options

    Returns:
        Contract instance
    """
    return await Smart402.create(config, **options)


async def from_template(
    template_name: str, variables: Dict[str, Any], **options
) -> Contract:
    """
    Create from template (convenience function).

    Args:
        template_name: Template name
        variables: Template variables
        **options: SDK options

    Returns:
        Contract instance
    """
    return await Smart402.from_template(template_name, variables, **options)


async def load(contract_id: str, **options) -> Contract:
    """
    Load contract (convenience function).

    Args:
        contract_id: Contract ID
        **options: SDK options

    Returns:
        Contract instance
    """
    return await Smart402.load(contract_id, **options)
