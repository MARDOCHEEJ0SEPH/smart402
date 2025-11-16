"""
Cache Manager
Multi-level caching system with TTL, LRU eviction, and distributed cache support
"""

import asyncio
import time
import hashlib
import json
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
from collections import OrderedDict
import pickle


class CacheStrategy(Enum):
    """Cache eviction strategies"""
    LRU = "lru"           # Least Recently Used
    LFU = "lfu"           # Least Frequently Used
    FIFO = "fifo"         # First In First Out
    TTL = "ttl"           # Time To Live
    ADAPTIVE = "adaptive"  # Adaptive based on access patterns


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: float
    accessed_at: float
    access_count: int = 0
    ttl: Optional[float] = None
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.ttl is None:
            return False
        return (time.time() - self.created_at) > self.ttl


class CacheLayer:
    """
    Single cache layer implementation

    Features:
    - Multiple eviction strategies
    - TTL support
    - Size-based limits
    - Hit/miss statistics
    """

    def __init__(
        self,
        max_size: int = 1000,
        max_memory_mb: int = 100,
        strategy: CacheStrategy = CacheStrategy.LRU,
        default_ttl: Optional[float] = None
    ):
        """
        Initialize cache layer

        Args:
            max_size: Maximum number of entries
            max_memory_mb: Maximum memory in megabytes
            strategy: Eviction strategy
            default_ttl: Default TTL in seconds
        """
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.strategy = strategy
        self.default_ttl = default_ttl

        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.current_memory = 0

        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if key not in self.cache:
            self.misses += 1
            return None

        entry = self.cache[key]

        # Check expiration
        if entry.is_expired():
            self.remove(key)
            self.misses += 1
            return None

        # Update access metadata
        entry.accessed_at = time.time()
        entry.access_count += 1

        # Move to end for LRU
        if self.strategy == CacheStrategy.LRU:
            self.cache.move_to_end(key)

        self.hits += 1
        return entry.value

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None
    ) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL override

        Returns:
            Success status
        """
        # Calculate size
        try:
            size_bytes = len(pickle.dumps(value))
        except:
            size_bytes = 0

        # Remove old entry if exists
        if key in self.cache:
            self.remove(key)

        # Check if we need to evict
        while (len(self.cache) >= self.max_size or
               self.current_memory + size_bytes > self.max_memory_bytes):
            if not self._evict_one():
                return False  # Can't evict, cache full

        # Create entry
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=time.time(),
            accessed_at=time.time(),
            access_count=1,
            ttl=ttl or self.default_ttl,
            size_bytes=size_bytes
        )

        # Add to cache
        self.cache[key] = entry
        self.current_memory += size_bytes

        return True

    def remove(self, key: str) -> bool:
        """
        Remove entry from cache

        Args:
            key: Cache key

        Returns:
            Success status
        """
        if key not in self.cache:
            return False

        entry = self.cache[key]
        self.current_memory -= entry.size_bytes
        del self.cache[key]

        return True

    def _evict_one(self) -> bool:
        """
        Evict one entry based on strategy

        Returns:
            Success status
        """
        if not self.cache:
            return False

        if self.strategy == CacheStrategy.LRU:
            # Evict least recently used (first item)
            key = next(iter(self.cache))

        elif self.strategy == CacheStrategy.LFU:
            # Evict least frequently used
            key = min(self.cache.keys(),
                     key=lambda k: self.cache[k].access_count)

        elif self.strategy == CacheStrategy.FIFO:
            # Evict oldest (first item)
            key = next(iter(self.cache))

        elif self.strategy == CacheStrategy.TTL:
            # Evict expired or oldest
            expired = [k for k, e in self.cache.items() if e.is_expired()]
            if expired:
                key = expired[0]
            else:
                key = next(iter(self.cache))

        else:  # ADAPTIVE
            # Adaptive: consider both recency and frequency
            scores = {
                k: (e.access_count / (time.time() - e.accessed_at + 1))
                for k, e in self.cache.items()
            }
            key = min(scores.keys(), key=lambda k: scores[k])

        self.remove(key)
        self.evictions += 1
        return True

    def clear(self):
        """Clear all entries"""
        self.cache.clear()
        self.current_memory = 0

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / max(total_requests, 1)

        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'memory_mb': self.current_memory / (1024 * 1024),
            'max_memory_mb': self.max_memory_bytes / (1024 * 1024),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'evictions': self.evictions,
            'strategy': self.strategy.value
        }


class CacheManager:
    """
    Multi-level cache manager with distributed cache support

    Architecture:
    - L1: In-memory cache (fast, small)
    - L2: Process cache (medium, larger)
    - L3: Distributed cache (slow, unlimited)

    Features:
    - Automatic cache key generation
    - Cache warming
    - Intelligent prefetching
    - Cache invalidation patterns
    """

    def __init__(
        self,
        enable_l1: bool = True,
        enable_l2: bool = True,
        enable_l3: bool = False,
        l1_size: int = 100,
        l2_size: int = 1000,
        l1_ttl: float = 60,
        l2_ttl: float = 300
    ):
        """
        Initialize multi-level cache

        Args:
            enable_l1: Enable L1 cache
            enable_l2: Enable L2 cache
            enable_l3: Enable L3 distributed cache
            l1_size: L1 cache size
            l2_size: L2 cache size
            l1_ttl: L1 TTL in seconds
            l2_ttl: L2 TTL in seconds
        """
        self.layers: Dict[str, Optional[CacheLayer]] = {}

        # L1: Fast in-memory cache
        if enable_l1:
            self.layers['l1'] = CacheLayer(
                max_size=l1_size,
                max_memory_mb=10,
                strategy=CacheStrategy.LRU,
                default_ttl=l1_ttl
            )

        # L2: Larger process cache
        if enable_l2:
            self.layers['l2'] = CacheLayer(
                max_size=l2_size,
                max_memory_mb=100,
                strategy=CacheStrategy.ADAPTIVE,
                default_ttl=l2_ttl
            )

        # L3: Distributed cache (Redis-like)
        if enable_l3:
            # Would integrate with actual Redis/Memcached
            self.layers['l3'] = None

        self.key_patterns: Dict[str, str] = {
            'aeo_score': 'aeo:score:{contract_id}',
            'llmo_score': 'llmo:score:{contract_id}',
            'scc_compiled': 'scc:compiled:{contract_id}',
            'x402_payment': 'x402:payment:{contract_id}'
        }

    def generate_key(self, pattern: str, **params) -> str:
        """
        Generate cache key from pattern

        Args:
            pattern: Key pattern name
            params: Pattern parameters

        Returns:
            Cache key
        """
        if pattern in self.key_patterns:
            template = self.key_patterns[pattern]
            return template.format(**params)

        # Hash-based key for arbitrary data
        data_str = json.dumps(params, sort_keys=True)
        hash_val = hashlib.sha256(data_str.encode()).hexdigest()[:16]
        return f"{pattern}:{hash_val}"

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache (multi-level)

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        # Try L1 first
        if 'l1' in self.layers:
            value = self.layers['l1'].get(key)
            if value is not None:
                return value

        # Try L2
        if 'l2' in self.layers:
            value = self.layers['l2'].get(key)
            if value is not None:
                # Promote to L1
                if 'l1' in self.layers:
                    self.layers['l1'].set(key, value)
                return value

        # Try L3 (distributed)
        if 'l3' in self.layers and self.layers['l3']:
            value = await self._get_from_l3(key)
            if value is not None:
                # Promote to L1 and L2
                if 'l2' in self.layers:
                    self.layers['l2'].set(key, value)
                if 'l1' in self.layers:
                    self.layers['l1'].set(key, value)
                return value

        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None
    ):
        """
        Set value in cache (all levels)

        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL
        """
        # Set in all enabled layers
        if 'l1' in self.layers:
            self.layers['l1'].set(key, value, ttl)

        if 'l2' in self.layers:
            self.layers['l2'].set(key, value, ttl)

        if 'l3' in self.layers and self.layers['l3']:
            await self._set_to_l3(key, value, ttl)

    async def invalidate(self, key: str):
        """
        Invalidate key in all cache levels

        Args:
            key: Cache key
        """
        for layer in self.layers.values():
            if layer:
                layer.remove(key)

    async def invalidate_pattern(self, pattern: str):
        """
        Invalidate all keys matching pattern

        Args:
            pattern: Key pattern (supports wildcards)
        """
        for layer in self.layers.values():
            if not layer:
                continue

            # Find matching keys
            matching_keys = [
                k for k in layer.cache.keys()
                if self._match_pattern(k, pattern)
            ]

            # Remove them
            for key in matching_keys:
                layer.remove(key)

    def _match_pattern(self, key: str, pattern: str) -> bool:
        """
        Check if key matches pattern

        Args:
            key: Cache key
            pattern: Pattern with wildcards

        Returns:
            Match status
        """
        # Simple wildcard matching
        pattern = pattern.replace('*', '.*')
        import re
        return bool(re.match(pattern, key))

    async def warm_cache(self, contracts: List[Dict]):
        """
        Warm cache with contract data

        Args:
            contracts: Contracts to cache
        """
        for contract in contracts:
            contract_id = contract.get('id')
            if not contract_id:
                continue

            # Cache AEO score
            if 'aeo_score' in contract:
                key = self.generate_key('aeo_score', contract_id=contract_id)
                await self.set(key, contract['aeo_score'])

            # Cache LLMO score
            if 'llmo_score' in contract:
                key = self.generate_key('llmo_score', contract_id=contract_id)
                await self.set(key, contract['llmo_score'])

    async def _get_from_l3(self, key: str) -> Optional[Any]:
        """Get from distributed cache (Redis)"""
        # Would integrate with actual Redis
        await asyncio.sleep(0.001)  # Simulate network latency
        return None

    async def _set_to_l3(self, key: str, value: Any, ttl: Optional[float]):
        """Set to distributed cache (Redis)"""
        # Would integrate with actual Redis
        await asyncio.sleep(0.001)  # Simulate network latency

    def get_stats(self) -> Dict:
        """Get statistics for all cache levels"""
        return {
            layer_name: layer.get_stats() if layer else None
            for layer_name, layer in self.layers.items()
        }

    def clear_all(self):
        """Clear all cache levels"""
        for layer in self.layers.values():
            if layer:
                layer.clear()
