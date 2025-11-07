"""
Contract Processing Example

Demonstrates individual component usage
"""

from src.aeo.engine import AEOEngine
from src.llmo.engine import LLMOEngine
from src.scc.engine import SCCEngine
from src.x402.engine import X402Engine
import asyncio


async def process_contract_example():
    """Process a sample contract through all stages"""

    # Sample contract
    contract = {
        'id': 'contract_001',
        'type': 'payment',
        'amount': 10000,
        'parties': ['Alice', 'Bob'],
        'terms': 'Payment for services rendered',
        'conditions': ['Service completion verified', 'Quality approved'],
        'target_query': 'smart contract payment service'
    }

    print("Smart402 - Individual Component Example")
    print("=" * 60)
    print(f"\nProcessing Contract: {contract['id']}")
    print(f"Type: {contract['type']}")
    print(f"Amount: ${contract['amount']:,.2f}")
    print(f"Parties: {', '.join(contract['parties'])}")

    # Stage 1: AEO
    print("\n" + "-" * 60)
    print("STAGE 1: AEO (Answer Engine Optimization)")
    print("-" * 60)

    aeo_engine = AEOEngine()
    aeo_result = await aeo_engine.optimize_discovery([contract])

    if aeo_result:
        optimized_contract = aeo_result[0]
        print(f"✓ AEO Score: {optimized_contract.get('aeo_score', 0):.3f}")
        print(f"✓ Content Generated: {len(optimized_contract.get('optimized_content', ''))} chars")

    # Stage 2: LLMO
    print("\n" + "-" * 60)
    print("STAGE 2: LLMO (Large Language Model Optimization)")
    print("-" * 60)

    llmo_engine = LLMOEngine()
    llmo_result = await llmo_engine.optimize_understanding(aeo_result)

    if llmo_result:
        understood_contract = llmo_result[0]
        print(f"✓ Understanding Score: {understood_contract.get('understanding_score', 0):.3f}")
        print(f"✓ Semantic Structure Extracted")

    # Stage 3: SCC
    print("\n" + "-" * 60)
    print("STAGE 3: SCC (Smart Contract Compilation)")
    print("-" * 60)

    scc_engine = SCCEngine()
    scc_result = await scc_engine.compile_and_verify(llmo_result)

    if scc_result:
        compiled_contract = scc_result[0]
        print(f"✓ Compilation Status: {compiled_contract.get('compilation_status')}")
        print(f"✓ Gas Estimate: {compiled_contract.get('gas_estimate', 0):,}")

    # Stage 4: X402
    print("\n" + "-" * 60)
    print("STAGE 4: X402 (Payment Protocol)")
    print("-" * 60)

    x402_engine = X402Engine()
    x402_result = await x402_engine.optimize_execution(scc_result)

    if x402_result:
        executed_contract = x402_result[0]
        print(f"✓ Execution Status: {executed_contract.get('execution_status')}")
        print(f"✓ Transaction Hash: {executed_contract.get('tx_hash', 'N/A')[:16]}...")
        print(f"✓ Execution Time: {executed_contract.get('execution_time', 0):.3f}s")

    print("\n" + "=" * 60)
    print("✓ Contract processing completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(process_contract_example())
