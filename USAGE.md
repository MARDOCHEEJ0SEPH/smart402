# Smart402 Usage Guide

## Installation

```bash
# Install from source
git clone https://github.com/smart402/smart402.git
cd smart402
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

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
    print(stats)

asyncio.run(main())
```

### Processing Individual Contracts

```python
from src.aeo.engine import AEOEngine
from src.llmo.engine import LLMOEngine
from src.scc.engine import SCCEngine
from src.x402.engine import X402Engine
import asyncio

async def process_contract():
    # Sample contract
    contract = {
        'id': 'contract_001',
        'type': 'payment',
        'amount': 10000,
        'parties': ['Alice', 'Bob'],
        'terms': 'Payment for services'
    }

    # Stage 1: AEO - Optimize for AI discovery
    aeo = AEOEngine()
    aeo_result = await aeo.optimize_discovery([contract])

    # Stage 2: LLMO - Ensure AI understanding
    llmo = LLMOEngine()
    llmo_result = await llmo.optimize_understanding(aeo_result)

    # Stage 3: SCC - Compile to smart contract
    scc = SCCEngine()
    scc_result = await scc.compile_and_verify(llmo_result)

    # Stage 4: X402 - Execute payment
    x402 = X402Engine()
    x402_result = await x402.optimize_execution(scc_result)

    return x402_result

asyncio.run(process_contract())
```

## Component Details

### AEO (Answer Engine Optimization)

Optimizes contracts for AI discovery:

```python
from src.aeo.scoring import AEOScorer

scorer = AEOScorer()
contract = {'description': 'smart contract payment', ...}
score = scorer.calculate_aeo_score(contract)
print(f"AEO Score: {score:.3f}")
```

### LLMO (Large Language Model Optimization)

Ensures perfect AI comprehension:

```python
from src.llmo.understanding import UnderstandingScorer

scorer = UnderstandingScorer()
score = scorer.calculate_llmo_score(contract)
print(f"Understanding Score: {score:.3f}")
```

### SCC (Smart Contract Compilation)

Compiles natural language to smart contracts:

```python
from src.scc.compiler import SmartContractCompiler

compiler = SmartContractCompiler(target_blockchain="ethereum")
result = compiler.compile(contract)
print(f"Bytecode: {result.bytecode}")
print(f"Gas: {result.gas_estimate}")
```

### X402 (Payment Protocol)

Executes payments with Byzantine consensus:

```python
from src.x402.payment import PaymentExecutor

executor = PaymentExecutor()
result = executor.execute_payment(contract, conditions={})
print(f"Success: {result.success}")
print(f"TX Hash: {result.tx_hash}")
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_core.py
```

## Examples

See the `examples/` directory for complete examples:

- `basic_usage.py` - Complete orchestration demo
- `contract_example.py` - Individual component usage

```bash
python examples/basic_usage.py
python examples/contract_example.py
```

## Configuration

Default configuration can be modified:

```python
orchestrator = Smart402Orchestrator()

# Modify weights
orchestrator.current_configuration = {
    'aeo_weight': 0.20,
    'llmo_weight': 0.25,
    'scc_weight': 0.20,
    'x402_weight': 0.25,
    'value_weight': 0.10,
    'risk_aversion': 0.5
}
```

## Advanced Usage

### Custom State Machine

```python
from src.core.state_machine import Smart402StateMachine, ContractState

sm = Smart402StateMachine(beta=1.5)
sm.transition(ContractState.DISCOVERY)
sm.update_quality(ContractState.IDLE, 'success', ContractState.DISCOVERY, 0.9)
```

### Consensus Configuration

```python
from src.consensus.byzantine import ByzantineConsensus

consensus = ByzantineConsensus(node_id="node_1", num_nodes=7)
result = consensus.run_consensus({'value': 'contract_data'})
```

### Machine Learning

```python
from src.ml.classifier import ContractClassifier
from src.ml.anomaly_detector import AnomalyDetector

# Classification
classifier = ContractClassifier()
category = classifier.classify(contract)

# Anomaly detection
detector = AnomalyDetector()
detector.fit(training_contracts)
is_anomaly = detector.detect(new_contract)
```

## API Reference

See docstrings in source code for detailed API documentation.
