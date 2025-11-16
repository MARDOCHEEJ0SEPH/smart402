"""
Database Sharding
Horizontal partitioning for scalable data storage with replication
"""

import hashlib
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio


class ShardingStrategy(Enum):
    """Database sharding strategies"""
    HASH = "hash"                # Hash-based sharding
    RANGE = "range"              # Range-based sharding
    DIRECTORY = "directory"       # Lookup table sharding
    GEOGRAPHIC = "geographic"     # Geographic sharding
    CONSISTENT_HASH = "consistent_hash"  # Consistent hashing


@dataclass
class Shard:
    """Database shard"""
    id: str
    host: str
    port: int
    database: str
    is_master: bool = True
    is_active: bool = True
    replicas: List[str] = None
    weight: int = 1

    def __post_init__(self):
        if self.replicas is None:
            self.replicas = []


@dataclass
class ShardRange:
    """Range for range-based sharding"""
    start: Any
    end: Any
    shard_id: str


class ConsistentHashRing:
    """
    Consistent hash ring for even distribution

    Features:
    - Virtual nodes for better distribution
    - Minimal redistribution on shard add/remove
    """

    def __init__(self, virtual_nodes: int = 150):
        """
        Initialize hash ring

        Args:
            virtual_nodes: Number of virtual nodes per shard
        """
        self.virtual_nodes = virtual_nodes
        self.ring: Dict[int, str] = {}
        self.shards: List[str] = []

    def add_shard(self, shard_id: str):
        """
        Add shard to ring

        Args:
            shard_id: Shard identifier
        """
        self.shards.append(shard_id)

        for i in range(self.virtual_nodes):
            virtual_key = f"{shard_id}:{i}"
            hash_value = self._hash(virtual_key)
            self.ring[hash_value] = shard_id

    def remove_shard(self, shard_id: str):
        """
        Remove shard from ring

        Args:
            shard_id: Shard identifier
        """
        if shard_id in self.shards:
            self.shards.remove(shard_id)

        # Remove virtual nodes
        keys_to_remove = [
            k for k, v in self.ring.items()
            if v == shard_id
        ]

        for key in keys_to_remove:
            del self.ring[key]

    def get_shard(self, key: str) -> Optional[str]:
        """
        Get shard for key

        Args:
            key: Partition key

        Returns:
            Shard ID
        """
        if not self.ring:
            return None

        hash_value = self._hash(key)

        # Find next shard in ring
        for ring_hash in sorted(self.ring.keys()):
            if hash_value <= ring_hash:
                return self.ring[ring_hash]

        # Wrap around to first shard
        return self.ring[min(self.ring.keys())]

    def _hash(self, key: str) -> int:
        """Hash key to integer"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)


class ShardManager:
    """
    Database shard manager with routing and replication

    Features:
    - Multiple sharding strategies
    - Read replica support
    - Automatic failover
    - Shard rebalancing
    - Cross-shard queries
    """

    def __init__(
        self,
        strategy: ShardingStrategy = ShardingStrategy.HASH,
        replication_factor: int = 2
    ):
        """
        Initialize shard manager

        Args:
            strategy: Sharding strategy
            replication_factor: Number of replicas per shard
        """
        self.strategy = strategy
        self.replication_factor = replication_factor

        self.shards: Dict[str, Shard] = {}
        self.ranges: List[ShardRange] = []  # For range-based sharding
        self.directory: Dict[str, str] = {}  # For directory-based sharding
        self.hash_ring = ConsistentHashRing()  # For consistent hashing

        # Statistics
        self.stats = {
            'total_shards': 0,
            'active_shards': 0,
            'total_queries': 0,
            'cross_shard_queries': 0,
            'failovers': 0
        }

    def add_shard(
        self,
        shard_id: str,
        host: str,
        port: int,
        database: str,
        weight: int = 1
    ):
        """
        Add database shard

        Args:
            shard_id: Shard identifier
            host: Database host
            port: Database port
            database: Database name
            weight: Shard weight for weighted strategies
        """
        shard = Shard(
            id=shard_id,
            host=host,
            port=port,
            database=database,
            weight=weight
        )

        self.shards[shard_id] = shard

        # Add to consistent hash ring
        if self.strategy == ShardingStrategy.CONSISTENT_HASH:
            self.hash_ring.add_shard(shard_id)

        self.stats['total_shards'] = len(self.shards)
        self.stats['active_shards'] = sum(
            1 for s in self.shards.values() if s.is_active
        )

    def add_replica(
        self,
        master_id: str,
        replica_id: str,
        host: str,
        port: int,
        database: str
    ):
        """
        Add read replica for shard

        Args:
            master_id: Master shard ID
            replica_id: Replica shard ID
            host: Replica host
            port: Replica port
            database: Database name
        """
        if master_id not in self.shards:
            raise ValueError(f"Master shard {master_id} not found")

        # Create replica shard
        replica = Shard(
            id=replica_id,
            host=host,
            port=port,
            database=database,
            is_master=False
        )

        self.shards[replica_id] = replica

        # Link to master
        self.shards[master_id].replicas.append(replica_id)

        self.stats['total_shards'] = len(self.shards)

    def add_range(
        self,
        start: Any,
        end: Any,
        shard_id: str
    ):
        """
        Add range for range-based sharding

        Args:
            start: Range start (inclusive)
            end: Range end (exclusive)
            shard_id: Shard ID for this range
        """
        if shard_id not in self.shards:
            raise ValueError(f"Shard {shard_id} not found")

        shard_range = ShardRange(
            start=start,
            end=end,
            shard_id=shard_id
        )

        self.ranges.append(shard_range)
        self.ranges.sort(key=lambda r: r.start)

    def get_shard_for_key(
        self,
        key: str,
        for_write: bool = True
    ) -> Optional[Shard]:
        """
        Get shard for partition key

        Args:
            key: Partition key
            for_write: True for write operations (use master)

        Returns:
            Shard instance
        """
        self.stats['total_queries'] += 1

        # Determine shard ID based on strategy
        if self.strategy == ShardingStrategy.HASH:
            shard_id = self._hash_shard(key)

        elif self.strategy == ShardingStrategy.RANGE:
            shard_id = self._range_shard(key)

        elif self.strategy == ShardingStrategy.DIRECTORY:
            shard_id = self.directory.get(key)

        elif self.strategy == ShardingStrategy.CONSISTENT_HASH:
            shard_id = self.hash_ring.get_shard(key)

        else:  # GEOGRAPHIC or other
            shard_id = self._geographic_shard(key)

        if not shard_id or shard_id not in self.shards:
            return None

        shard = self.shards[shard_id]

        # For reads, optionally use replica
        if not for_write and shard.replicas:
            # Load balance across replicas
            replica_id = shard.replicas[
                hash(key) % len(shard.replicas)
            ]
            if replica_id in self.shards and self.shards[replica_id].is_active:
                return self.shards[replica_id]

        # Use master
        if not shard.is_active:
            # Try failover to replica
            for replica_id in shard.replicas:
                replica = self.shards.get(replica_id)
                if replica and replica.is_active:
                    self.stats['failovers'] += 1
                    return replica

            return None

        return shard

    def _hash_shard(self, key: str) -> Optional[str]:
        """Hash-based shard selection"""
        if not self.shards:
            return None

        # Simple hash modulo
        active_shards = [
            s for s in self.shards.values()
            if s.is_active and s.is_master
        ]

        if not active_shards:
            return None

        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
        index = hash_value % len(active_shards)

        return active_shards[index].id

    def _range_shard(self, key: Any) -> Optional[str]:
        """Range-based shard selection"""
        for shard_range in self.ranges:
            if shard_range.start <= key < shard_range.end:
                return shard_range.shard_id

        return None

    def _geographic_shard(self, key: str) -> Optional[str]:
        """Geographic shard selection (example: based on country code)"""
        # In production, parse location from key
        # For now, use simple hash
        return self._hash_shard(key)

    async def execute_on_shard(
        self,
        shard_id: str,
        operation: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute operation on specific shard

        Args:
            shard_id: Shard identifier
            operation: Async operation to execute
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Operation result
        """
        if shard_id not in self.shards:
            raise ValueError(f"Shard {shard_id} not found")

        shard = self.shards[shard_id]

        if not shard.is_active:
            raise Exception(f"Shard {shard_id} is not active")

        # Execute operation
        # In production, pass actual database connection
        result = await operation(*args, shard=shard, **kwargs)

        return result

    async def scatter_gather(
        self,
        operation: Callable,
        *args,
        **kwargs
    ) -> List[Any]:
        """
        Execute operation on all shards (scatter-gather)

        Args:
            operation: Async operation to execute
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            List of results from all shards
        """
        self.stats['cross_shard_queries'] += 1

        # Get active master shards
        active_shards = [
            s for s in self.shards.values()
            if s.is_active and s.is_master
        ]

        # Execute on all shards in parallel
        tasks = [
            self.execute_on_shard(shard.id, operation, *args, **kwargs)
            for shard in active_shards
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_results = [
            r for r in results
            if not isinstance(r, Exception)
        ]

        return valid_results

    async def write_with_replication(
        self,
        key: str,
        operation: Callable,
        *args,
        **kwargs
    ) -> bool:
        """
        Write to master and replicas

        Args:
            key: Partition key
            operation: Write operation
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Success status
        """
        master = self.get_shard_for_key(key, for_write=True)

        if not master:
            return False

        # Write to master
        try:
            await self.execute_on_shard(
                master.id,
                operation,
                *args,
                **kwargs
            )
        except Exception as e:
            print(f"Master write failed: {e}")
            return False

        # Replicate to replicas asynchronously
        if master.replicas:
            replica_tasks = [
                self.execute_on_shard(replica_id, operation, *args, **kwargs)
                for replica_id in master.replicas
                if replica_id in self.shards
            ]

            # Don't wait for replicas (async replication)
            asyncio.gather(*replica_tasks, return_exceptions=True)

        return True

    async def rebalance_shards(self):
        """
        Rebalance data across shards

        This is a complex operation that would:
        1. Calculate ideal distribution
        2. Move data between shards
        3. Update routing tables
        """
        # In production, implement actual rebalancing logic
        # This would involve:
        # - Analyzing current distribution
        # - Determining target distribution
        # - Migrating data with minimal downtime
        # - Updating routing configuration

        print("Shard rebalancing not yet implemented")

    def get_shard_stats(self, shard_id: str) -> Optional[Dict]:
        """
        Get statistics for specific shard

        Args:
            shard_id: Shard identifier

        Returns:
            Shard statistics
        """
        if shard_id not in self.shards:
            return None

        shard = self.shards[shard_id]

        return {
            'id': shard.id,
            'host': shard.host,
            'port': shard.port,
            'is_master': shard.is_master,
            'is_active': shard.is_active,
            'replica_count': len(shard.replicas),
            'weight': shard.weight
        }

    def get_stats(self) -> Dict:
        """Get shard manager statistics"""
        master_shards = [
            s for s in self.shards.values()
            if s.is_master
        ]

        replica_shards = [
            s for s in self.shards.values()
            if not s.is_master
        ]

        return {
            **self.stats,
            'strategy': self.strategy.value,
            'master_shards': len(master_shards),
            'replica_shards': len(replica_shards),
            'replication_factor': self.replication_factor
        }
