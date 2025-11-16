"""
Smart402 Scalability Demo
Demonstrates enterprise-grade scalability features
"""

import asyncio
import time
import numpy as np
from src.scalability import (
    ScalableSmart402Orchestrator,
    DistributedProcessor,
    CacheManager,
    LoadBalancer,
    LoadBalancingStrategy,
    RateLimiter,
    RateLimitStrategy,
    MessageQueue,
    QueuePriority
)


async def demo_basic_scalability():
    """Demonstrate basic scalability features"""
    print("=" * 60)
    print("Smart402 Scalability Demo")
    print("=" * 60)

    # Initialize scalable orchestrator
    print("\n1. Initializing Scalable Orchestrator...")
    orchestrator = ScalableSmart402Orchestrator(
        enable_caching=True,
        enable_load_balancing=True,
        enable_sharding=True,
        enable_auto_scaling=True
    )

    await orchestrator.initialize()
    print("   ✓ Orchestrator initialized with all scalability features")

    # Generate sample contracts
    print("\n2. Generating sample contracts...")
    contracts = [
        {
            'id': f'contract_{i}',
            'type': 'payment',
            'amount': np.random.randint(100, 10000),
            'parties': ['party_a', 'party_b'],
            'description': f'Payment contract {i}'
        }
        for i in range(100)
    ]
    print(f"   ✓ Generated {len(contracts)} contracts")

    # Process contracts with caching
    print("\n3. Processing contracts with caching...")
    start_time = time.time()

    # First pass - cache misses
    for contract in contracts[:10]:
        await orchestrator.process_contract(contract, client_id='demo_client')

    first_pass_time = time.time() - start_time

    # Second pass - cache hits
    start_time = time.time()
    for contract in contracts[:10]:
        await orchestrator.process_contract(contract, client_id='demo_client')

    second_pass_time = time.time() - start_time

    speedup = first_pass_time / max(second_pass_time, 0.001)
    print(f"   ✓ First pass (cache miss): {first_pass_time:.3f}s")
    print(f"   ✓ Second pass (cache hit): {second_pass_time:.3f}s")
    print(f"   ✓ Speedup from caching: {speedup:.2f}x")

    # Batch processing with distributed workers
    print("\n4. Batch processing with distributed workers...")
    start_time = time.time()

    results = await orchestrator.process_batch(
        contracts[10:50],
        client_id='demo_client'
    )

    batch_time = time.time() - start_time
    throughput = len(results) / batch_time

    print(f"   ✓ Processed {len(results)} contracts in {batch_time:.3f}s")
    print(f"   ✓ Throughput: {throughput:.2f} contracts/second")

    # Get comprehensive statistics
    print("\n5. System Statistics:")
    stats = orchestrator.get_comprehensive_stats()

    print(f"   Orchestrator:")
    print(f"     - Total contracts: {stats['orchestrator']['total_contracts_processed']}")
    print(f"     - Successful: {stats['orchestrator']['successful_contracts']}")
    print(f"     - Failed: {stats['orchestrator']['failed_contracts']}")
    print(f"     - Cache hits: {stats['orchestrator']['cache_hits']}")
    print(f"     - Cache misses: {stats['orchestrator']['cache_misses']}")

    if 'cache' in stats:
        cache_stats = stats['cache']
        print(f"\n   Cache (L1):")
        print(f"     - Hit rate: {cache_stats['l1']['hit_rate']:.2%}")
        print(f"     - Size: {cache_stats['l1']['size']}/{cache_stats['l1']['max_size']}")

    print(f"\n   Rate Limiter:")
    print(f"     - Total requests: {stats['rate_limiter']['total_requests']}")
    print(f"     - Allowed: {stats['rate_limiter']['allowed_requests']}")
    print(f"     - Blocked: {stats['rate_limiter']['blocked_requests']}")

    print(f"\n   Circuit Breaker:")
    print(f"     - State: {stats['circuit_breaker']['state']}")
    print(f"     - Total calls: {stats['circuit_breaker']['total_calls']}")
    print(f"     - Error rate: {stats['circuit_breaker']['error_rate']:.2%}")

    if 'load_balancer' in stats:
        print(f"\n   Load Balancer:")
        print(f"     - Strategy: {stats['load_balancer']['strategy']}")
        print(f"     - Total backends: {stats['load_balancer']['total_backends']}")
        print(f"     - Healthy backends: {stats['load_balancer']['healthy_backends']}")

    if 'shard_manager' in stats:
        print(f"\n   Shard Manager:")
        print(f"     - Strategy: {stats['shard_manager']['strategy']}")
        print(f"     - Master shards: {stats['shard_manager']['master_shards']}")
        print(f"     - Replica shards: {stats['shard_manager']['replica_shards']}")

    if 'auto_scaler' in stats:
        print(f"\n   Auto Scaler:")
        print(f"     - Current instances: {stats['auto_scaler']['current_instances']}")
        print(f"     - Scale ups: {stats['auto_scaler']['total_scale_ups']}")
        print(f"     - Scale downs: {stats['auto_scaler']['total_scale_downs']}")

    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


async def demo_distributed_processing():
    """Demonstrate distributed processing"""
    print("\n" + "=" * 60)
    print("Distributed Processing Demo")
    print("=" * 60)

    processor = DistributedProcessor()
    await processor.start()

    # Generate contracts
    contracts = [
        {'id': f'contract_{i}', 'amount': i * 100}
        for i in range(50)
    ]

    print(f"\nProcessing {len(contracts)} contracts across worker pools...")

    start_time = time.time()
    results = await processor.process_pipeline(contracts)
    elapsed = time.time() - start_time

    print(f"✓ Processed {len(results)} contracts in {elapsed:.3f}s")
    print(f"✓ Average time per contract: {elapsed/len(results)*1000:.2f}ms")

    # Get stats
    stats = processor.get_stats()
    print(f"\nWorker Pool Statistics:")
    for pool_name, pool_stats in stats.items():
        print(f"  {pool_name.upper()} Pool:")
        print(f"    - Workers: {pool_stats['num_workers']}")
        print(f"    - Completed tasks: {pool_stats['completed_tasks']}")
        print(f"    - Active tasks: {pool_stats['active_tasks']}")
        print(f"    - Error rate: {pool_stats['error_rate']:.2%}")


async def demo_caching():
    """Demonstrate caching strategies"""
    print("\n" + "=" * 60)
    print("Caching Demo")
    print("=" * 60)

    cache = CacheManager(enable_l1=True, enable_l2=True, l1_size=100, l2_size=1000)

    print("\nTesting cache levels...")

    # Test cache miss and hit
    key = 'test_contract'
    value = {'id': 'contract_123', 'amount': 5000}

    result = await cache.get(key)
    print(f"✓ First get (miss): {result}")

    await cache.set(key, value, ttl=60)
    result = await cache.get(key)
    print(f"✓ Second get (hit): {result}")

    # Test cache warming
    contracts = [
        {'id': f'contract_{i}', 'aeo_score': 0.9, 'llmo_score': 0.85}
        for i in range(10)
    ]

    await cache.warm_cache(contracts)
    print(f"✓ Warmed cache with {len(contracts)} contracts")

    # Get stats
    stats = cache.get_stats()
    print(f"\nCache Statistics:")
    for level, level_stats in stats.items():
        if level_stats:
            print(f"  {level.upper()}:")
            print(f"    - Size: {level_stats['size']}/{level_stats['max_size']}")
            print(f"    - Hit rate: {level_stats['hit_rate']:.2%}")
            print(f"    - Memory: {level_stats['memory_mb']:.2f}MB")


async def demo_load_balancing():
    """Demonstrate load balancing"""
    print("\n" + "=" * 60)
    print("Load Balancing Demo")
    print("=" * 60)

    lb = LoadBalancer(strategy=LoadBalancingStrategy.ADAPTIVE)

    # Add backends
    for i in range(3):
        lb.add_backend(f'backend_{i}', f'host{i}', 8000, weight=i+1)

    print(f"✓ Added {len(lb.backends)} backends")

    # Start health checks
    asyncio.create_task(lb.start_health_checks())

    # Simulate requests
    async def process_request(backend):
        await asyncio.sleep(0.01)
        return f"Processed on {backend.id}"

    print("\nSimulating 20 requests...")
    for i in range(20):
        result = await lb.execute_request(process_request, client_ip=f'192.168.1.{i}')

    # Get stats
    stats = lb.get_stats()
    print(f"\nLoad Balancer Statistics:")
    print(f"  Strategy: {stats['strategy']}")
    print(f"  Total requests: {stats['total_requests']}")
    print(f"  Total errors: {stats['total_errors']}")
    print(f"  Healthy backends: {stats['healthy_backends']}/{stats['total_backends']}")

    print(f"\n  Backend Distribution:")
    for backend_id, backend_stats in stats['backends'].items():
        print(f"    {backend_id}:")
        print(f"      - Requests: {backend_stats['total_requests']}")
        print(f"      - Avg response time: {backend_stats['avg_response_time']:.4f}s")


async def demo_rate_limiting():
    """Demonstrate rate limiting"""
    print("\n" + "=" * 60)
    print("Rate Limiting Demo")
    print("=" * 60)

    limiter = RateLimiter(
        strategy=RateLimitStrategy.TOKEN_BUCKET,
        rate=10,  # 10 requests
        window=1.0,  # per second
        burst=15  # burst up to 15
    )

    print("\nSending 20 requests (limit: 10/second, burst: 15)...")

    allowed = 0
    blocked = 0

    for i in range(20):
        result = await limiter.check_limit('client_1')
        if result.allowed:
            allowed += 1
        else:
            blocked += 1

    print(f"✓ Allowed: {allowed}")
    print(f"✓ Blocked: {blocked}")

    stats = limiter.get_stats()
    print(f"\nRate Limiter Statistics:")
    print(f"  Strategy: {stats['strategy']}")
    print(f"  Rate: {stats['rate']}/{stats['window']}s")
    print(f"  Block rate: {stats['block_rate']:.2%}")


async def demo_message_queue():
    """Demonstrate message queue"""
    print("\n" + "=" * 60)
    print("Message Queue Demo")
    print("=" * 60)

    queue = MessageQueue(max_size=1000)

    # Start ack monitor
    asyncio.create_task(queue.start_ack_monitor())

    print("\nPublishing messages with different priorities...")

    # Publish messages
    await queue.publish('contracts.high', {'id': 1}, QueuePriority.HIGH)
    await queue.publish('contracts.normal', {'id': 2}, QueuePriority.NORMAL)
    await queue.publish('contracts.low', {'id': 3}, QueuePriority.LOW)

    print("✓ Published 3 messages")

    # Consume messages (should come out in priority order)
    print("\nConsuming messages (priority order)...")
    for i in range(3):
        msg = await queue.consume(timeout=1.0)
        if msg:
            print(f"  Consumed: topic={msg.topic}, priority={msg.priority}")
            await queue.ack(msg.id)

    # Get stats
    stats = queue.get_stats()
    print(f"\nQueue Statistics:")
    print(f"  Published: {stats['messages_published']}")
    print(f"  Consumed: {stats['messages_consumed']}")
    print(f"  Current size: {stats['current_size']}")


async def main():
    """Run all demos"""
    # Run basic scalability demo
    await demo_basic_scalability()

    # Run component demos
    await demo_distributed_processing()
    await demo_caching()
    await demo_load_balancing()
    await demo_rate_limiting()
    await demo_message_queue()


if __name__ == '__main__':
    asyncio.run(main())
