# Getting Started with Smart402

Welcome to Smart402! This guide will help you get up and running with the AI-Native Smart Contract Framework.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Core Concepts](#core-concepts)
4. [First Contract](#first-contract)
5. [Next Steps](#next-steps)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Install from Source

```bash
# Clone the repository
git clone https://github.com/smart402/smart402.git
cd smart402

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Install with Development Tools

```bash
# Install with development dependencies
pip install -e ".[dev]"
```

### Verify Installation

```bash
# Run tests to verify installation
pytest tests/

# Check version
python -c "import src; print('Smart402 installed successfully!')"
```

## Quick Start

### Basic Usage

Here's a minimal example to process a contract:

```python
import asyncio
from src import Smart402Orchestrator

async def main():
    # Initialize orchestrator
    orchestrator = Smart402Orchestrator()

    # Run for 10 seconds
    await orchestrator.run(duration=10)

    # Get statistics
    stats = orchestrator.get_statistics()
    print(f"Total contracts processed: {stats['total_contracts']}")
    print(f"Success rate: {stats['state_machine']['success_rate']:.2%}")

# Run
asyncio.run(main())
```

### Processing a Single Contract

```python
from src.aeo.engine import AEOEngine
from src.llmo.engine import LLMOEngine
from src.scc.engine import SCCEngine
from src.x402.engine import X402Engine
import asyncio

async def process_contract():
    # Define contract
    contract = {
        'id': 'my_contract_001',
        'type': 'payment',
        'amount': 10000,
        'parties': ['Alice', 'Bob'],
        'terms': 'Payment for services upon completion',
        'conditions': ['Service delivered', 'Quality verified']
    }

    # Stage 1: AEO - Optimize for AI discovery
    print("Stage 1: AEO Processing...")
    aeo = AEOEngine()
    contracts = await aeo.optimize_discovery([contract])
    print(f"✓ AEO Score: {contracts[0]['aeo_score']:.3f}")

    # Stage 2: LLMO - Ensure AI understanding
    print("\nStage 2: LLMO Processing...")
    llmo = LLMOEngine()
    contracts = await llmo.optimize_understanding(contracts)
    print(f"✓ Understanding Score: {contracts[0]['understanding_score']:.3f}")

    # Stage 3: SCC - Compile to smart contract
    print("\nStage 3: SCC Processing...")
    scc = SCCEngine()
    contracts = await scc.compile_and_verify(contracts)
    print(f"✓ Compilation: {contracts[0]['compilation_status']}")
    print(f"✓ Gas Estimate: {contracts[0].get('gas_estimate', 0):,}")

    # Stage 4: X402 - Execute payment
    print("\nStage 4: X402 Processing...")
    x402 = X402Engine()
    contracts = await x402.optimize_execution(contracts)
    print(f"✓ Execution: {contracts[0]['execution_status']}")

    print("\n✅ Contract processing complete!")
    return contracts[0]

# Run
result = asyncio.run(process_contract())
```

## Core Concepts

### The Four Pillars

Smart402 integrates four core technologies:

#### 1. **AEO (Answer Engine Optimization)**

Optimizes contracts for maximum AI visibility across platforms like ChatGPT, Claude, and Perplexity.

```python
from src.aeo.scoring import AEOScorer

scorer = AEOScorer()
score = scorer.calculate_aeo_score(contract)
print(f"AEO Score: {score:.3f}")
```

**Key Features:**
- Semantic relevance scoring
- Citation frequency analysis
- Content freshness optimization
- Cross-platform presence tracking

#### 2. **LLMO (Large Language Model Optimization)**

Ensures perfect AI comprehension through semantic parsing and universal encoding.

```python
from src.llmo.understanding import UnderstandingScorer

scorer = UnderstandingScorer()
score = scorer.calculate_llmo_score(contract)
print(f"Understanding Score: {score:.3f}")
```

**Key Features:**
- Perplexity-based comprehension analysis
- Dependency parsing
- Transformer-based encoding
- Multi-model ensemble

#### 3. **SCC (Smart Contract Compilation)**

Automatically compiles natural language contracts to blockchain-ready smart contracts.

```python
from src.scc.compiler import SmartContractCompiler

compiler = SmartContractCompiler(target_blockchain="ethereum")
result = compiler.compile(contract)
print(f"Bytecode: {result.bytecode}")
print(f"Gas: {result.gas_estimate}")
```

**Key Features:**
- NL → AST → IR → Bytecode pipeline
- Formal verification
- Storage optimization
- Security auditing

#### 4. **X402 (Payment Protocol)**

Executes payments with Byzantine fault tolerance and atomic swaps.

```python
from src.x402.payment import PaymentExecutor

executor = PaymentExecutor()
result = executor.execute_payment(contract, conditions={})
print(f"Transaction: {result.tx_hash}")
```

**Key Features:**
- Byzantine consensus (PBFT)
- Atomic swaps (HTLC)
- Cross-chain routing
- Payment optimization

### State Machine

Smart402 uses a probabilistic state machine for contract processing:

```python
from src.core.state_machine import Smart402StateMachine, ContractState

# Initialize state machine
sm = Smart402StateMachine()

# Transition through states
sm.transition(ContractState.DISCOVERY)
sm.transition(ContractState.UNDERSTANDING)
sm.transition(ContractState.COMPILATION)
# ... etc

# Get statistics
stats = sm.get_statistics()
print(f"Success rate: {stats['success_rate']:.2%}")
```

**States:**
- IDLE → DISCOVERY → UNDERSTANDING → COMPILATION → VERIFICATION → EXECUTION → SETTLEMENT → COMPLETED

### Optimization Function

The master optimization function balances multiple objectives:

```python
from src.core.optimization import MasterOptimizationFunction, ContractMetrics

optimizer = MasterOptimizationFunction()

metrics = ContractMetrics(
    value=0.8,
    discoverability=0.7,
    understanding=0.9,
    compilation_score=0.85,
    execution_efficiency=0.75,
    risk=0.2
)

objective = optimizer.calculate_objective(metrics)
print(f"Objective value: {objective:.4f}")
```

**Formula:**
```
F(C) = α₁·V(C) + α₂·D(C) + α₃·U(C) + α₄·S(C) + α₅·E(C) - γ·R(C)
```

## First Contract

Let's create a complete example:

```python
import asyncio
from src import Smart402Orchestrator

async def my_first_contract():
    # Define contract
    my_contract = {
        'id': 'first_contract',
        'type': 'payment',
        'amount': 5000,
        'parties': ['Company A', 'Company B'],
        'terms': '''
            Company A agrees to pay Company B $5,000 upon successful
            delivery of software module as specified in Exhibit A.
        ''',
        'conditions': [
            'Software delivered and functional',
            'Passes all unit tests',
            'Documentation complete'
        ],
        'target_query': 'software payment smart contract'
    }

    # Initialize orchestrator
    orchestrator = Smart402Orchestrator()

    # Process manually through each stage
    from src.aeo.engine import AEOEngine
    from src.llmo.engine import LLMOEngine
    from src.scc.engine import SCCEngine
    from src.x402.engine import X402Engine

    aeo = AEOEngine()
    llmo = LLMOEngine()
    scc = SCCEngine()
    x402 = X402Engine()

    # Pipeline
    result = [my_contract]
    result = await aeo.optimize_discovery(result)
    result = await llmo.optimize_understanding(result)
    result = await scc.compile_and_verify(result)
    result = await x402.optimize_execution(result)

    # Display results
    final = result[0]
    print("\n" + "="*60)
    print("CONTRACT PROCESSING COMPLETE")
    print("="*60)
    print(f"ID: {final['id']}")
    print(f"AEO Score: {final.get('aeo_score', 0):.3f}")
    print(f"Understanding Score: {final.get('understanding_score', 0):.3f}")
    print(f"Compilation: {final.get('compilation_status', 'N/A')}")
    print(f"Execution: {final.get('execution_status', 'N/A')}")
    print(f"Transaction Hash: {final.get('tx_hash', 'N/A')}")
    print("="*60)

    return final

# Run
asyncio.run(my_first_contract())
```

## Next Steps

### Explore the Documentation

- [API Reference](api-reference.md) - Complete API documentation
- [Algorithms](algorithms.md) - Mathematical formulations
- [Architecture](architecture.md) - System design details

### Run Examples

```bash
# Basic usage example
python examples/basic_usage.py

# Contract processing example
python examples/contract_example.py
```

### Explore the Dashboard

Open the web dashboard to visualize real-time metrics:

```bash
# Open in browser
open web/dashboard.html
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Join the Community

- **GitHub**: https://github.com/smart402/smart402
- **Documentation**: https://docs.smart402.io
- **Discord**: https://discord.gg/smart402

## Troubleshooting

### Common Issues

**Import Error:**
```bash
# Make sure you're in the correct directory
cd smart402

# Reinstall
pip install -e .
```

**Test Failures:**
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Clear cache
pytest --cache-clear
```

**Performance Issues:**
```bash
# Check system resources
# Smart402 benefits from multi-core processors

# Adjust configuration
orchestrator.current_configuration['parallel_processing'] = True
```

## Support

If you encounter any issues:

1. Check the [FAQ](faq.md)
2. Search [GitHub Issues](https://github.com/smart402/smart402/issues)
3. Join our [Discord](https://discord.gg/smart402)
4. Email support: team@smart402.io

## License

Smart402 is released under the MIT License. See [LICENSE](../LICENSE) for details.
