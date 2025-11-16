"""
Scalable Orchestrator
Enterprise-grade orchestrator with all scalability features integrated
"""

import asyncio
import time
from typing import Dict, List, Optional
import numpy as np

from .distributed_processor import DistributedProcessor
from .cache_manager import CacheManager
from .message_queue import MessageQueue, MessageBroker, QueuePriority
from .load_balancer import LoadBalancer, LoadBalancingStrategy
from .database_sharding import ShardManager, ShardingStrategy
from .rate_limiter import RateLimiter, RateLimitStrategy
from .circuit_breaker import CircuitBreaker
from .metrics_collector import MetricsCollector, MetricType
from .auto_scaler import AutoScaler, ScalingPolicy, ScalingMetric

from ..core.state_machine import Smart402StateMachine, ContractState


class ScalableSmart402Orchestrator:
    """
    Scalable Smart402 Orchestrator

    Features:
    - Distributed processing with worker pools
    - Multi-level caching
    - Message queue for async processing
    - Load balancing across instances
    - Database sharding
    - Rate limiting
    - Circuit breakers
    - Metrics collection
    - Auto-scaling

    Architecture:
    ┌──────────────────────────────────────────┐
    │         Load Balancer                     │
    │      (Multi-strategy routing)             │
    └────────────────┬─────────────────────────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
    ┌────────┐  ┌────────┐  ┌────────┐
    │Worker 1│  │Worker 2│  │Worker N│
    └────┬───┘  └────┬───┘  └────┬───┘
         │           │           │
         └───────────┼───────────┘
                     ▼
         ┌───────────────────────┐
         │   Distributed Cache    │
         │   Message Queue        │
         │   Sharded Database     │
         └───────────────────────┘
    """

    def __init__(
        self,
        enable_caching: bool = True,
        enable_load_balancing: bool = True,
        enable_sharding: bool = True,
        enable_auto_scaling: bool = True
    ):
        """
        Initialize scalable orchestrator

        Args:
            enable_caching: Enable caching layer
            enable_load_balancing: Enable load balancing
            enable_sharding: Enable database sharding
            enable_auto_scaling: Enable auto-scaling
        """
        # Core components
        self.state_machine = Smart402StateMachine()

        # Scalability components
        self.distributed_processor = DistributedProcessor()

        self.cache_manager = CacheManager(
            enable_l1=enable_caching,
            enable_l2=enable_caching,
            l1_size=1000,
            l2_size=10000
        ) if enable_caching else None

        self.message_broker = MessageBroker()
        self.queue = self.message_broker.create_queue('contracts', max_size=50000)

        self.load_balancer = LoadBalancer(
            strategy=LoadBalancingStrategy.ADAPTIVE
        ) if enable_load_balancing else None

        self.shard_manager = ShardManager(
            strategy=ShardingStrategy.CONSISTENT_HASH,
            replication_factor=2
        ) if enable_sharding else None

        self.rate_limiter = RateLimiter(
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            rate=1000,
            window=60.0
        )

        self.circuit_breaker = CircuitBreaker()
        self.metrics = MetricsCollector()

        self.auto_scaler = AutoScaler(
            current_instances=1,
            get_metrics=self.get_scaling_metrics
        ) if enable_auto_scaling else None

        # Contract registry (sharded)
        self.contract_registry: Dict[str, Dict] = {}

        # Statistics
        self.stats = {
            'total_contracts_processed': 0,
            'successful_contracts': 0,
            'failed_contracts': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }

    async def initialize(self):
        """Initialize all components"""
        # Start distributed processor
        await self.distributed_processor.start()

        # Initialize shards
        if self.shard_manager:
            self._initialize_shards()

        # Initialize load balancer backends
        if self.load_balancer:
            self._initialize_backends()

        # Add auto-scaling policies
        if self.auto_scaler:
            self._initialize_auto_scaling()

        # Start background tasks
        asyncio.create_task(self.metrics.cleanup_old_metrics())
        asyncio.create_task(self.queue.start_ack_monitor())

        if self.load_balancer:
            asyncio.create_task(self.load_balancer.start_health_checks())

        if self.auto_scaler:
            asyncio.create_task(self.auto_scaler.auto_scale_loop(interval=30.0))

    def _initialize_shards(self):
        """Initialize database shards"""
        # Create 3 shards with replicas
        for i in range(3):
            shard_id = f"shard_{i}"
            self.shard_manager.add_shard(
                shard_id=shard_id,
                host=f"db-{i}.smart402.local",
                port=5432,
                database="smart402",
                weight=1
            )

            # Add replica
            replica_id = f"shard_{i}_replica"
            self.shard_manager.add_replica(
                master_id=shard_id,
                replica_id=replica_id,
                host=f"db-{i}-replica.smart402.local",
                port=5432,
                database="smart402"
            )

    def _initialize_backends(self):
        """Initialize load balancer backends"""
        # Add backend instances
        for i in range(3):
            self.load_balancer.add_backend(
                backend_id=f"backend_{i}",
                host=f"smart402-{i}.local",
                port=8000,
                weight=1
            )

    def _initialize_auto_scaling(self):
        """Initialize auto-scaling policies"""
        # CPU-based scaling
        self.auto_scaler.add_policy(ScalingPolicy(
            metric=ScalingMetric.CPU_UTILIZATION,
            scale_up_threshold=0.7,
            scale_down_threshold=0.3,
            scale_up_step=2,
            scale_down_step=1,
            cooldown_period=120.0,
            evaluation_periods=3,
            min_instances=1,
            max_instances=20
        ))

        # Queue-based scaling
        self.auto_scaler.add_policy(ScalingPolicy(
            metric=ScalingMetric.QUEUE_SIZE,
            scale_up_threshold=1000,
            scale_down_threshold=100,
            scale_up_step=3,
            scale_down_step=1,
            cooldown_period=60.0,
            evaluation_periods=2,
            min_instances=1,
            max_instances=20
        ))

    async def process_contract(
        self,
        contract: Dict,
        client_id: str = "default"
    ) -> Dict:
        """
        Process single contract through scalable pipeline

        Args:
            contract: Contract to process
            client_id: Client identifier for rate limiting

        Returns:
            Processed contract
        """
        contract_id = contract.get('id', 'unknown')

        # Rate limiting
        rate_limit_result = await self.rate_limiter.check_limit(client_id)
        if not rate_limit_result.allowed:
            self.metrics.increment_counter('rate_limited_requests')
            raise Exception(f"Rate limited. Retry after {rate_limit_result.retry_after}s")

        self.metrics.increment_counter('total_requests')
        start_time = time.time()

        try:
            # Check cache
            if self.cache_manager:
                cache_key = self.cache_manager.generate_key(
                    'processed_contract',
                    contract_id=contract_id
                )

                cached = await self.cache_manager.get(cache_key)
                if cached:
                    self.stats['cache_hits'] += 1
                    self.metrics.increment_counter('cache_hits')
                    return cached
                else:
                    self.stats['cache_misses'] += 1
                    self.metrics.increment_counter('cache_misses')

            # Execute with circuit breaker
            async def process_pipeline():
                # AEO phase
                contract = await self._process_phase(contract, 'aeo')

                # LLMO phase
                contract = await self._process_phase(contract, 'llmo')

                # SCC phase
                contract = await self._process_phase(contract, 'scc')

                # X402 phase
                contract = await self._process_phase(contract, 'x402')

                return contract

            # Process with circuit breaker
            processed = await self.circuit_breaker.call(process_pipeline)

            # Cache result
            if self.cache_manager:
                await self.cache_manager.set(cache_key, processed, ttl=300)

            # Store in sharded database
            if self.shard_manager:
                await self._store_contract(contract_id, processed)

            # Update stats
            self.stats['total_contracts_processed'] += 1
            self.stats['successful_contracts'] += 1

            # Record metrics
            processing_time = time.time() - start_time
            self.metrics.observe_histogram('contract_processing_time', processing_time)
            self.metrics.increment_counter('successful_contracts')

            return processed

        except Exception as e:
            self.stats['failed_contracts'] += 1
            self.metrics.increment_counter('failed_contracts')

            # Record error
            processing_time = time.time() - start_time
            self.metrics.observe_histogram('failed_contract_time', processing_time)

            raise

    async def _process_phase(
        self,
        contract: Dict,
        phase: str
    ) -> Dict:
        """
        Process contract through single phase

        Args:
            contract: Contract to process
            phase: Phase name (aeo, llmo, scc, x402)

        Returns:
            Processed contract
        """
        # Check phase-specific cache
        if self.cache_manager:
            cache_key = self.cache_manager.generate_key(
                f'{phase}_processed',
                contract_id=contract.get('id')
            )

            cached = await self.cache_manager.get(cache_key)
            if cached:
                return cached

        # Simulate processing
        await asyncio.sleep(np.random.uniform(0.01, 0.05))

        contract[f'{phase}_processed'] = True
        contract[f'{phase}_score'] = np.random.uniform(0.7, 1.0)
        contract[f'{phase}_timestamp'] = time.time()

        # Cache result
        if self.cache_manager:
            await self.cache_manager.set(cache_key, contract, ttl=60)

        return contract

    async def _store_contract(
        self,
        contract_id: str,
        contract: Dict
    ):
        """
        Store contract in sharded database

        Args:
            contract_id: Contract identifier
            contract: Contract data
        """
        if not self.shard_manager:
            self.contract_registry[contract_id] = contract
            return

        # Write with replication
        async def write_operation(shard, **kwargs):
            # Simulate database write
            await asyncio.sleep(0.01)
            return True

        await self.shard_manager.write_with_replication(
            contract_id,
            write_operation
        )

        # Also keep in local registry for demo
        self.contract_registry[contract_id] = contract

    async def process_batch(
        self,
        contracts: List[Dict],
        client_id: str = "default"
    ) -> List[Dict]:
        """
        Process batch of contracts using distributed processing

        Args:
            contracts: Contracts to process
            client_id: Client identifier

        Returns:
            Processed contracts
        """
        self.metrics.increment_counter('batch_requests')
        self.metrics.observe_histogram('batch_size', len(contracts))

        # Use distributed processor for parallel processing
        processed = await self.distributed_processor.process_pipeline(
            contracts,
            phases=['aeo', 'llmo', 'scc', 'x402']
        )

        return processed

    async def get_scaling_metrics(self) -> Dict:
        """
        Get metrics for auto-scaling decisions

        Returns:
            Scaling metrics
        """
        return {
            'cpu_utilization': np.random.uniform(0.3, 0.8),  # Simulated
            'memory_utilization': np.random.uniform(0.4, 0.7),  # Simulated
            'request_rate': self.metrics.get_counter('total_requests'),
            'queue_size': self.queue.get_stats()['current_size'],
            'error_rate': (
                self.stats['failed_contracts'] /
                max(self.stats['total_contracts_processed'], 1)
            )
        }

    def get_comprehensive_stats(self) -> Dict:
        """Get comprehensive system statistics"""
        stats = {
            'orchestrator': self.stats,
            'rate_limiter': self.rate_limiter.get_stats(),
            'circuit_breaker': self.circuit_breaker.get_stats(),
            'metrics': self.metrics.get_all_metrics(),
            'message_queue': self.queue.get_stats(),
            'distributed_processor': self.distributed_processor.get_stats()
        }

        if self.cache_manager:
            stats['cache'] = self.cache_manager.get_stats()

        if self.load_balancer:
            stats['load_balancer'] = self.load_balancer.get_stats()

        if self.shard_manager:
            stats['shard_manager'] = self.shard_manager.get_stats()

        if self.auto_scaler:
            stats['auto_scaler'] = self.auto_scaler.get_stats()

        return stats

    async def shutdown(self):
        """Graceful shutdown"""
        await self.distributed_processor.shutdown()
