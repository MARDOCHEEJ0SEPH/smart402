"""
Basic Usage Example for Smart402

This example demonstrates the complete workflow:
1. Contract discovery (AEO)
2. Contract understanding (LLMO)
3. Smart contract compilation (SCC)
4. Payment execution (X402)
"""

import asyncio
from src import Smart402Orchestrator


async def main():
    """Main example function"""
    print("Smart402 - Complete Algorithmic Framework Demo")
    print("=" * 60)

    # Initialize orchestrator
    orchestrator = Smart402Orchestrator()
    print("\n✓ Orchestrator initialized")

    # Run orchestration for a short duration
    print("\n▶ Running Smart402 orchestration...")
    print("  This will demonstrate all 4 components:")
    print("  - AEO (Answer Engine Optimization)")
    print("  - LLMO (Large Language Model Optimization)")
    print("  - SCC (Smart Contract Compilation)")
    print("  - X402 (Payment Protocol)")

    # Run for 5 seconds
    await orchestrator.run(duration=5)

    # Get statistics
    stats = orchestrator.get_statistics()

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    print(f"\nState Machine:")
    print(f"  Current State: {stats['state_machine']['current_state']}")
    print(f"  Total Transitions: {stats['state_machine']['total_transitions']}")
    print(f"  Success Rate: {stats['state_machine']['success_rate']:.2%}")

    print(f"\nContract Processing:")
    print(f"  Total Contracts: {stats['total_contracts']}")
    print(f"  Registry Size: {stats['registry_size']}")

    print(f"\nOptimization:")
    print(f"  Best Fitness: {stats['best_fitness']:.4f}")

    print("\n" + "=" * 60)
    print("✓ Demo completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
