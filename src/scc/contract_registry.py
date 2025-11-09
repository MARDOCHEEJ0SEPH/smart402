"""
Blockchain Contract Registry

This module implements the on-chain contract registry as specified
in the Smart402 plan.

Features:
- Store contract metadata on blockchain
- Version control for contract updates
- Unique contract IDs
- Contract discovery and search
- Immutable audit trail
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import hashlib
import json


class ContractStatus(Enum):
    """Contract status in registry"""
    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    DISPUTED = "disputed"


class BlockchainNetwork(Enum):
    """Supported blockchain networks"""
    ETHEREUM_MAINNET = "ethereum_mainnet"
    ETHEREUM_SEPOLIA = "ethereum_sepolia"
    POLYGON = "polygon"
    POLYGON_MUMBAI = "polygon_mumbai"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"


@dataclass
class ContractVersion:
    """
    Single version of a contract
    """
    version_number: int
    contract_hash: str
    timestamp: datetime
    author: str
    changes_summary: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'version_number': self.version_number,
            'contract_hash': self.contract_hash,
            'timestamp': self.timestamp.isoformat(),
            'author': self.author,
            'changes_summary': self.changes_summary,
            'metadata': self.metadata
        }


@dataclass
class RegistryEntry:
    """
    Contract registry entry

    Stored on blockchain for immutability and discoverability
    """
    contract_id: str
    contract_type: str
    parties: List[str]
    current_version: int
    version_history: List[ContractVersion]
    status: ContractStatus
    created_at: datetime
    updated_at: datetime
    blockchain_network: BlockchainNetwork
    smart_contract_address: Optional[str] = None
    ipfs_hash: Optional[str] = None  # Full contract stored on IPFS
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_current_hash(self) -> Optional[str]:
        """Get hash of current version"""
        if not self.version_history:
            return None

        current = next((v for v in self.version_history if v.version_number == self.current_version), None)
        return current.contract_hash if current else None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'contract_id': self.contract_id,
            'contract_type': self.contract_type,
            'parties': self.parties,
            'current_version': self.current_version,
            'version_history': [v.to_dict() for v in self.version_history],
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'blockchain_network': self.blockchain_network.value,
            'smart_contract_address': self.smart_contract_address,
            'ipfs_hash': self.ipfs_hash,
            'tags': self.tags,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RegistryEntry':
        """Create from dictionary"""
        version_history = [
            ContractVersion(
                version_number=v['version_number'],
                contract_hash=v['contract_hash'],
                timestamp=datetime.fromisoformat(v['timestamp']),
                author=v['author'],
                changes_summary=v['changes_summary'],
                metadata=v['metadata']
            )
            for v in data.get('version_history', [])
        ]

        return cls(
            contract_id=data['contract_id'],
            contract_type=data['contract_type'],
            parties=data['parties'],
            current_version=data['current_version'],
            version_history=version_history,
            status=ContractStatus(data['status']),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            blockchain_network=BlockchainNetwork(data['blockchain_network']),
            smart_contract_address=data.get('smart_contract_address'),
            ipfs_hash=data.get('ipfs_hash'),
            tags=data.get('tags', []),
            metadata=data.get('metadata', {})
        )


class ContractRegistry:
    """
    Blockchain contract registry

    Manages contract storage, versioning, and discovery on blockchain.

    As specified in Smart402 plan:
    - Store contract metadata on-chain
    - Full contract content on IPFS
    - Version history tracking
    - Search and discovery
    - Immutable audit trail
    """

    def __init__(self, blockchain_network: BlockchainNetwork = BlockchainNetwork.POLYGON):
        self.blockchain_network = blockchain_network
        self.registry: Dict[str, RegistryEntry] = {}
        self.contract_by_party: Dict[str, List[str]] = {}  # Index by party
        self.contract_by_type: Dict[str, List[str]] = {}  # Index by type
        self.contract_by_tag: Dict[str, List[str]] = {}  # Index by tag

    def register_contract(
        self,
        contract_data: Dict[str, Any],
        parties: List[str],
        contract_type: str,
        author: str,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Register new contract in registry

        Args:
            contract_data: Complete contract data
            parties: List of party addresses/names
            contract_type: Type of contract
            author: Contract creator
            tags: Optional tags for discovery

        Returns:
            Unique contract ID
        """
        # Generate unique contract ID
        contract_id = self._generate_contract_id(contract_data, parties)

        # Calculate contract hash
        contract_hash = self._calculate_hash(contract_data)

        # Create initial version
        version = ContractVersion(
            version_number=1,
            contract_hash=contract_hash,
            timestamp=datetime.now(),
            author=author,
            changes_summary="Initial contract creation",
            metadata={
                'contract_size': len(json.dumps(contract_data)),
                'parties_count': len(parties)
            }
        )

        # Create registry entry
        entry = RegistryEntry(
            contract_id=contract_id,
            contract_type=contract_type,
            parties=parties,
            current_version=1,
            version_history=[version],
            status=ContractStatus.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            blockchain_network=self.blockchain_network,
            tags=tags or [],
            metadata={
                'creation_method': 'smart402_framework',
                'data_sources_count': len(contract_data.get('data_sources', []))
            }
        )

        # Store in registry
        self.registry[contract_id] = entry

        # Update indexes
        self._update_indexes(contract_id, entry)

        return contract_id

    def update_contract(
        self,
        contract_id: str,
        updated_data: Dict[str, Any],
        author: str,
        changes_summary: str
    ) -> bool:
        """
        Update contract with new version

        Args:
            contract_id: Contract ID
            updated_data: Updated contract data
            author: Update author
            changes_summary: Summary of changes

        Returns:
            True if updated successfully
        """
        if contract_id not in self.registry:
            return False

        entry = self.registry[contract_id]

        # Calculate new hash
        new_hash = self._calculate_hash(updated_data)

        # Create new version
        new_version_number = entry.current_version + 1
        new_version = ContractVersion(
            version_number=new_version_number,
            contract_hash=new_hash,
            timestamp=datetime.now(),
            author=author,
            changes_summary=changes_summary,
            metadata={
                'contract_size': len(json.dumps(updated_data)),
                'previous_version': entry.current_version
            }
        )

        # Add to version history
        entry.version_history.append(new_version)
        entry.current_version = new_version_number
        entry.updated_at = datetime.now()

        return True

    def activate_contract(
        self,
        contract_id: str,
        smart_contract_address: str,
        ipfs_hash: Optional[str] = None
    ) -> bool:
        """
        Activate contract after deployment to blockchain

        Args:
            contract_id: Contract ID
            smart_contract_address: Deployed smart contract address
            ipfs_hash: IPFS hash of full contract

        Returns:
            True if activated successfully
        """
        if contract_id not in self.registry:
            return False

        entry = self.registry[contract_id]
        entry.status = ContractStatus.ACTIVE
        entry.smart_contract_address = smart_contract_address
        entry.ipfs_hash = ipfs_hash
        entry.updated_at = datetime.now()

        return True

    def get_contract(self, contract_id: str) -> Optional[RegistryEntry]:
        """
        Get contract by ID

        Args:
            contract_id: Contract ID

        Returns:
            RegistryEntry or None
        """
        return self.registry.get(contract_id)

    def search_by_party(self, party: str) -> List[RegistryEntry]:
        """
        Search contracts by party

        Args:
            party: Party address/name

        Returns:
            List of contracts involving party
        """
        contract_ids = self.contract_by_party.get(party, [])
        return [self.registry[cid] for cid in contract_ids if cid in self.registry]

    def search_by_type(self, contract_type: str) -> List[RegistryEntry]:
        """
        Search contracts by type

        Args:
            contract_type: Contract type

        Returns:
            List of contracts of type
        """
        contract_ids = self.contract_by_type.get(contract_type, [])
        return [self.registry[cid] for cid in contract_ids if cid in self.registry]

    def search_by_tag(self, tag: str) -> List[RegistryEntry]:
        """
        Search contracts by tag

        Args:
            tag: Tag to search

        Returns:
            List of contracts with tag
        """
        contract_ids = self.contract_by_tag.get(tag, [])
        return [self.registry[cid] for cid in contract_ids if cid in self.registry]

    def search_by_status(self, status: ContractStatus) -> List[RegistryEntry]:
        """
        Search contracts by status

        Args:
            status: Contract status

        Returns:
            List of contracts with status
        """
        return [entry for entry in self.registry.values() if entry.status == status]

    def get_version_history(self, contract_id: str) -> List[ContractVersion]:
        """
        Get complete version history for contract

        Args:
            contract_id: Contract ID

        Returns:
            List of all versions
        """
        entry = self.registry.get(contract_id)
        return entry.version_history if entry else []

    def update_status(self, contract_id: str, new_status: ContractStatus) -> bool:
        """
        Update contract status

        Args:
            contract_id: Contract ID
            new_status: New status

        Returns:
            True if updated successfully
        """
        if contract_id not in self.registry:
            return False

        entry = self.registry[contract_id]
        entry.status = new_status
        entry.updated_at = datetime.now()

        return True

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get registry statistics

        Returns:
            Statistics dictionary
        """
        total_contracts = len(self.registry)

        status_counts = {}
        for status in ContractStatus:
            status_counts[status.value] = len(self.search_by_status(status))

        type_counts = {}
        for contract_type in self.contract_by_type:
            type_counts[contract_type] = len(self.contract_by_type[contract_type])

        total_versions = sum(len(entry.version_history) for entry in self.registry.values())

        return {
            'total_contracts': total_contracts,
            'total_versions': total_versions,
            'status_breakdown': status_counts,
            'type_breakdown': type_counts,
            'unique_parties': len(self.contract_by_party),
            'blockchain_network': self.blockchain_network.value
        }

    def export_to_json(self, contract_id: str) -> Optional[str]:
        """
        Export contract registry entry to JSON

        Args:
            contract_id: Contract ID

        Returns:
            JSON string or None
        """
        entry = self.registry.get(contract_id)
        if not entry:
            return None

        return json.dumps(entry.to_dict(), indent=2)

    def import_from_json(self, json_data: str) -> Optional[str]:
        """
        Import contract from JSON

        Args:
            json_data: JSON string

        Returns:
            Contract ID or None if failed
        """
        try:
            data = json.loads(json_data)
            entry = RegistryEntry.from_dict(data)

            # Add to registry
            self.registry[entry.contract_id] = entry
            self._update_indexes(entry.contract_id, entry)

            return entry.contract_id

        except Exception as e:
            print(f"Import error: {e}")
            return None

    def _generate_contract_id(self, contract_data: Dict[str, Any], parties: List[str]) -> str:
        """
        Generate unique contract ID

        Args:
            contract_data: Contract data
            parties: Parties list

        Returns:
            Unique ID
        """
        data_str = f"{json.dumps(contract_data, sort_keys=True)}:{':'.join(sorted(parties))}:{datetime.now()}"
        return hashlib.sha256(data_str.encode()).hexdigest()[:32]

    def _calculate_hash(self, contract_data: Dict[str, Any]) -> str:
        """
        Calculate hash of contract data

        Args:
            contract_data: Contract data

        Returns:
            SHA-256 hash
        """
        data_str = json.dumps(contract_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _update_indexes(self, contract_id: str, entry: RegistryEntry) -> None:
        """
        Update search indexes

        Args:
            contract_id: Contract ID
            entry: Registry entry
        """
        # Index by party
        for party in entry.parties:
            if party not in self.contract_by_party:
                self.contract_by_party[party] = []
            if contract_id not in self.contract_by_party[party]:
                self.contract_by_party[party].append(contract_id)

        # Index by type
        if entry.contract_type not in self.contract_by_type:
            self.contract_by_type[entry.contract_type] = []
        if contract_id not in self.contract_by_type[entry.contract_type]:
            self.contract_by_type[entry.contract_type].append(contract_id)

        # Index by tags
        for tag in entry.tags:
            if tag not in self.contract_by_tag:
                self.contract_by_tag[tag] = []
            if contract_id not in self.contract_by_tag[tag]:
                self.contract_by_tag[tag].append(contract_id)


# Example usage
if __name__ == "__main__":
    # Create registry
    registry = ContractRegistry(blockchain_network=BlockchainNetwork.POLYGON)

    # Register a contract
    contract_data = {
        'type': 'SaaS_Reseller_Agreement',
        'terms': {
            'commission_rate': 0.15,
            'payment_frequency': 'monthly',
            'min_revenue': 100000
        },
        'data_sources': [
            {'id': 'revenue_api', 'url': 'https://api.example.com/revenue'}
        ]
    }

    contract_id = registry.register_contract(
        contract_data=contract_data,
        parties=['VendorCorp', 'ResellerInc'],
        contract_type='SaaS_Reseller_Agreement',
        author='0xvendor123',
        tags=['saas', 'commission', 'reseller']
    )

    print(f"Registered contract: {contract_id}")

    # Activate contract
    registry.activate_contract(
        contract_id=contract_id,
        smart_contract_address='0x1234567890abcdef',
        ipfs_hash='QmXxx...'
    )

    # Search contracts
    vendor_contracts = registry.search_by_party('VendorCorp')
    print(f"Vendor has {len(vendor_contracts)} contracts")

    # Get statistics
    stats = registry.get_statistics()
    print(f"Registry stats: {json.dumps(stats, indent=2)}")

    # Export to JSON
    exported = registry.export_to_json(contract_id)
    print(f"Exported contract:\n{exported}")
