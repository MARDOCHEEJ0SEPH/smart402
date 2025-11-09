# Smart402 API Reference

Complete API documentation for all Smart402 components.

## Table of Contents

1. [Core API](#core-api)
2. [AEO API](#aeo-api)
3. [LLMO API](#llmo-api)
4. [SCC API](#scc-api)
5. [X402 API](#x402-api)
6. [REST API](#rest-api)

## Core API

### Smart402Orchestrator

Main orchestration class integrating all components.

```python
from src.core.orchestrator import Smart402Orchestrator

orchestrator = Smart402Orchestrator()
```

#### Methods

**`async run(duration: Optional[float] = None)`**

Run the orchestration loop.

- **Parameters:**
  - `duration` (float, optional): Runtime duration in seconds
- **Returns:** None

**Example:**

```python
await orchestrator.run(duration=10)
```

---

**`get_statistics() -> Dict`**

Get system statistics.

- **Returns:** Dictionary containing:
  - `total_contracts` (int): Total contracts processed
  - `registry_size` (int): Number of contracts in registry
  - `best_fitness` (float): Best fitness score achieved
  - `state_machine` (dict): State machine statistics
  - `current_configuration` (dict): Current configuration

**Example:**

```python
stats = orchestrator.get_statistics()
print(f"Total contracts: {stats['total_contracts']}")
```

---

### Smart402StateMachine

Probabilistic state machine for contract processing.

```python
from src.core.state_machine import Smart402StateMachine, ContractState

sm = Smart402StateMachine(beta=1.0)
```

#### Methods

**`transition(to_state: ContractState, condition: str = "success", metadata: Optional[Dict] = None) -> bool`**

Execute state transition.

- **Parameters:**
  - `to_state` (ContractState): Target state
  - `condition` (str): Transition condition
  - `metadata` (dict, optional): Additional metadata
- **Returns:** True if transition successful

**Example:**

```python
success = sm.transition(ContractState.DISCOVERY)
```

---

**`get_state_history() -> List[StateTransition]`**

Get complete state transition history.

- **Returns:** List of StateTransition objects

**Example:**

```python
history = sm.get_state_history()
for transition in history:
    print(f"{transition.from_state} → {transition.to_state}")
```

---

### MasterOptimizationFunction

Master optimization function for the system.

```python
from src.core.optimization import MasterOptimizationFunction, ContractMetrics

optimizer = MasterOptimizationFunction(
    alpha1=0.3, alpha2=0.15, alpha3=0.2, alpha4=0.15, alpha5=0.2, gamma=0.5
)
```

#### Methods

**`calculate_objective(metrics: ContractMetrics, constraints: Optional[OptimizationConstraints] = None) -> float`**

Calculate objective function value.

- **Parameters:**
  - `metrics` (ContractMetrics): Contract metrics
  - `constraints` (OptimizationConstraints, optional): Constraints
- **Returns:** Objective value

**Example:**

```python
metrics = ContractMetrics(
    value=0.8,
    discoverability=0.7,
    understanding=0.9,
    compilation_score=0.85,
    execution_efficiency=0.75,
    risk=0.2
)
objective = optimizer.calculate_objective(metrics)
```

---

## AEO API

### AEOEngine

Main AEO engine for answer engine optimization.

```python
from src.aeo.engine import AEOEngine

aeo = AEOEngine()
```

#### Methods

**`async optimize_discovery(contracts: Optional[List[Dict]] = None) -> List[Dict]`**

Optimize contracts for AI discovery.

- **Parameters:**
  - `contracts` (list, optional): List of contracts to optimize
- **Returns:** Optimized contracts with AEO scores

**Example:**

```python
result = await aeo.optimize_discovery([{
    'id': 'contract_001',
    'type': 'payment',
    'description': 'Payment contract',
    'amount': 10000
}])
```

---

### AEOScorer

Calculate AEO visibility scores.

```python
from src.aeo.scoring import AEOScorer

scorer = AEOScorer()
```

#### Methods

**`calculate_aeo_score(contract: Dict) -> float`**

Calculate comprehensive AEO score.

- **Parameters:**
  - `contract` (dict): Contract data
- **Returns:** AEO score [0, 1]

**Example:**

```python
score = scorer.calculate_aeo_score(contract)
print(f"AEO Score: {score:.3f}")
```

---

**`semantic_relevance(contract: Dict) -> float`**

Calculate semantic relevance score.

- **Returns:** Semantic relevance [0, 1]

---

**`citation_frequency(contract: Dict) -> float`**

Calculate citation frequency with time decay.

- **Returns:** Citation frequency [0, 1]

---

**`content_freshness(contract: Dict) -> float`**

Calculate content freshness.

- **Returns:** Freshness score [0, 1]

---

### ContentGenerator

Generate AEO-optimized content.

```python
from src.aeo.content_generator import ContentGenerator

generator = ContentGenerator()
```

#### Methods

**`generate_aeo_content(contract: Dict, target_query: str, max_length: int = 500) -> str`**

Generate AEO-optimized content.

- **Parameters:**
  - `contract` (dict): Contract data
  - `target_query` (str): Target search query
  - `max_length` (int): Maximum content length
- **Returns:** Optimized content string

**Example:**

```python
content = generator.generate_aeo_content(
    contract,
    target_query='smart contract payment'
)
```

---

## LLMO API

### LLMOEngine

Main LLMO engine for LLM optimization.

```python
from src.llmo.engine import LLMOEngine

llmo = LLMOEngine()
```

#### Methods

**`async optimize_understanding(contracts: Optional[List[Dict]] = None) -> List[Dict]`**

Optimize contracts for LLM understanding.

- **Parameters:**
  - `contracts` (list, optional): Contracts to process
- **Returns:** Contracts with understanding optimization

**Example:**

```python
result = await llmo.optimize_understanding(contracts)
```

---

### UnderstandingScorer

Calculate understanding scores.

```python
from src.llmo.understanding import UnderstandingScorer

scorer = UnderstandingScorer()
```

#### Methods

**`calculate_llmo_score(contract: Dict, llm_model: str = "default") -> float`**

Calculate overall LLMO understanding score.

- **Parameters:**
  - `contract` (dict): Contract data
  - `llm_model` (str): LLM model identifier
- **Returns:** Understanding score [0, 1]

**Example:**

```python
score = scorer.calculate_llmo_score(contract)
```

---

**`ensemble_understanding(contract: Dict) -> float`**

Multi-model ensemble understanding.

- **Parameters:**
  - `contract` (dict): Contract data
- **Returns:** Ensemble score [0, 1]

---

## SCC API

### SCCEngine

Main smart contract compilation engine.

```python
from src.scc.engine import SCCEngine

scc = SCCEngine(target_blockchain="ethereum")
```

#### Methods

**`async compile_and_verify(contracts: Optional[List[Dict]] = None) -> List[Dict]`**

Compile and verify contracts.

- **Parameters:**
  - `contracts` (list, optional): Contracts to compile
- **Returns:** Compiled and verified contracts

**Example:**

```python
result = await scc.compile_and_verify(contracts)
```

---

### SmartContractCompiler

Compile contracts to smart contract bytecode.

```python
from src.scc.compiler import SmartContractCompiler

compiler = SmartContractCompiler(target_blockchain="ethereum")
```

#### Methods

**`compile(contract_terms: Dict) -> CompilationResult`**

Compile contract to smart contract.

- **Parameters:**
  - `contract_terms` (dict): Contract terms
- **Returns:** CompilationResult object

**Example:**

```python
result = compiler.compile(contract)
print(f"Bytecode: {result.bytecode}")
print(f"Gas: {result.gas_estimate}")
```

---

### SmartContractVerifier

Formal verification of smart contracts.

```python
from src.scc.verifier import SmartContractVerifier

verifier = SmartContractVerifier()
```

#### Methods

**`verify(contract_code: Dict, formal_spec: Optional[Dict] = None) -> VerificationResult`**

Verify smart contract against specification.

- **Parameters:**
  - `contract_code` (dict): Compiled contract
  - `formal_spec` (dict, optional): Formal specification
- **Returns:** VerificationResult object

**Example:**

```python
result = verifier.verify(contract_code)
print(f"Valid: {result.is_valid}")
print(f"Violations: {result.violations}")
```

---

## X402 API

### X402Engine

Main X402 payment protocol engine.

```python
from src.x402.engine import X402Engine

x402 = X402Engine()
```

#### Methods

**`async optimize_execution(contracts: Optional[List[Dict]] = None) -> List[Dict]`**

Optimize and execute payments.

- **Parameters:**
  - `contracts` (list, optional): Contracts to execute
- **Returns:** Executed contracts

**Example:**

```python
result = await x402.optimize_execution(contracts)
```

---

### PaymentExecutor

Execute payments with Byzantine consensus.

```python
from src.x402.payment import PaymentExecutor

executor = PaymentExecutor(num_nodes=7)
```

#### Methods

**`execute_payment(contract: Dict, conditions: Dict) -> PaymentResult`**

Execute payment with condition verification.

- **Parameters:**
  - `contract` (dict): Contract data
  - `conditions` (dict): Payment conditions
- **Returns:** PaymentResult object

**Example:**

```python
result = executor.execute_payment(contract, conditions={})
print(f"Success: {result.success}")
print(f"TX Hash: {result.tx_hash}")
```

---

### PaymentRouter

Optimize payment routing.

```python
from src.x402.routing import PaymentRouter

router = PaymentRouter()
```

#### Methods

**`find_optimal_route(source: str, destination: str, amount: float) -> Optional[PaymentRoute]`**

Find optimal payment route.

- **Parameters:**
  - `source` (str): Source network
  - `destination` (str): Destination network
  - `amount` (float): Payment amount
- **Returns:** PaymentRoute object or None

**Example:**

```python
route = router.find_optimal_route('ethereum', 'polygon', 10000)
print(f"Path: {route.path}")
print(f"Cost: {route.cost}")
```

---

## REST API

Base URL: `http://localhost:5000/api`

### Health Check

**GET `/health`**

Check API health status.

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "aeo": "operational",
    "llmo": "operational",
    "scc": "operational",
    "x402": "operational"
  }
}
```

---

### System Statistics

**GET `/stats`**

Get system statistics.

**Response:**

```json
{
  "totalContracts": 1234,
  "registrySize": 567,
  "bestFitness": 0.8765,
  "stateMachine": {
    "current_state": "s0",
    "success_rate": 0.92
  },
  "configuration": {...}
}
```

---

### Process Contract

**POST `/contract/process`**

Process a contract through all stages.

**Request Body:**

```json
{
  "id": "contract_001",
  "type": "payment",
  "amount": 10000,
  "parties": ["Alice", "Bob"],
  "terms": "Payment for services",
  "conditions": ["Service delivered"],
  "target_query": "smart contract payment"
}
```

**Response:**

```json
{
  "contractId": "contract_001",
  "status": "completed",
  "stages": [
    {
      "name": "AEO",
      "status": "success",
      "score": 0.875,
      "details": {...}
    },
    ...
  ],
  "finalContract": {...}
}
```

---

### Calculate AEO Score

**POST `/aeo/score`**

Calculate AEO score for contract.

**Request Body:**

```json
{
  "description": "Smart contract for payment",
  "amount": 10000,
  ...
}
```

**Response:**

```json
{
  "aeoScore": 0.875,
  "components": {
    "semanticRelevance": 0.92,
    "citationFrequency": 0.85,
    "contentFreshness": 0.88,
    "authorityScore": 0.80,
    "crossPlatformPresence": 0.75
  }
}
```

---

### Find Payment Route

**POST `/x402/route`**

Find optimal payment route.

**Request Body:**

```json
{
  "source": "ethereum",
  "destination": "polygon",
  "amount": 10000
}
```

**Response:**

```json
{
  "path": ["ethereum", "polygon"],
  "cost": 25.50,
  "estimatedTime": 12.5,
  "liquidityAvailable": 1000000
}
```

---

## Error Handling

All API endpoints return appropriate HTTP status codes:

- `200 OK` - Successful request
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

**Error Response Format:**

```json
{
  "error": "Description of the error"
}
```

## Rate Limiting

The API implements rate limiting:

- 100 requests per minute per IP
- Burst limit: 10 requests

## Authentication

Currently, the API does not require authentication. In production, implement:

- API keys
- OAuth 2.0
- JWT tokens
