# JavaScript SDK

Complete guide to the Smart402 JavaScript/TypeScript SDK.

## Installation

```bash
npm install @smart402/sdk
```

## Quick Example

```javascript
const { Smart402 } = require('@smart402/sdk');

const contract = await Smart402.create({
  type: 'saas-subscription',
  parties: ['vendor@example.com', 'customer@example.com'],
  payment: {
    amount: 99,
    token: 'USDC',
    blockchain: 'polygon',
    frequency: 'monthly'
  }
});

await contract.deploy({ network: 'polygon' });
```

## Core API

### Smart402 Class

Main entry point for SDK operations.

#### `Smart402.create(config)`

Create a new contract.

```javascript
const contract = await Smart402.create({
  type: string,              // Contract type
  parties: string[],         // Email addresses
  payment: {
    amount: number,          // Payment amount
    token: string,           // Token symbol (USDC, USDT, DAI)
    blockchain: string,      // Network (polygon, ethereum, etc.)
    frequency: string        // Payment frequency
  },
  conditions?: object[],     // Optional conditions
  metadata?: object          // Optional metadata
});
```

#### `Smart402.fromTemplate(template, variables)`

Create from template.

```javascript
const contract = await Smart402.fromTemplate('saas-subscription', {
  vendor_email: 'vendor@example.com',
  customer_email: 'customer@example.com',
  amount: 99
});
```

#### `Smart402.load(contractId)`

Load existing contract.

```javascript
const contract = await Smart402.load('smart402:saas:abc123');
```

#### `Smart402.getTemplates()`

List available templates.

```javascript
const templates = Smart402.getTemplates();
// ['saas-subscription', 'freelancer-payment', 'supply-chain', ...]
```

### Contract Class

Represents a deployed or deployable contract.

#### `contract.deploy(options)`

Deploy to blockchain.

```javascript
const result = await contract.deploy({
  network: 'polygon',        // Target network
  gasLimit: 500000,          // Optional gas limit
  escrowEnabled: false       // Optional escrow
});

// Returns:
// {
//   address: '0x...',
//   transactionHash: '0x...',
//   network: 'polygon',
//   blockNumber: 12345,
//   gasUsed: 150000
// }
```

#### `contract.startMonitoring(options)`

Start automatic monitoring.

```javascript
await contract.startMonitoring({
  frequency: 'hourly',       // Check frequency
  webhook: 'https://...',    // Webhook URL
  autoExecute: true          // Auto-execute when conditions met
});
```

#### `contract.checkConditions()`

Check if conditions are met.

```javascript
const result = await contract.checkConditions();

// Returns:
// {
//   allMet: true,
//   conditions: [...],
//   timestamp: 1234567890
// }
```

#### `contract.executePayment()`

Execute payment manually.

```javascript
const result = await contract.executePayment();

// Returns:
// {
//   success: true,
//   transactionHash: '0x...',
//   amount: 99,
//   token: 'USDC',
//   from: '0x...',
//   to: '0x...',
//   timestamp: 1234567890
// }
```

#### `contract.getAEOScore()`

Get AI discoverability score.

```javascript
const score = contract.getAEOScore();

// Returns:
// {
//   total: 0.85,
//   semantic_richness: 0.90,
//   citation_friendliness: 0.85,
//   findability: 0.82,
//   authority_signals: 0.75,
//   citation_presence: 0.80
// }
```

#### `contract.validate()`

Validate contract structure.

```javascript
const validation = contract.validate();

// Returns:
// {
//   valid: true,
//   errors: [],
//   warnings: []
// }
```

#### `contract.explain()`

Get plain-English explanation.

```javascript
const explanation = contract.explain();
// "This is a monthly SaaS subscription contract between..."
```

#### `contract.compile(target)`

Compile to target language.

```javascript
const solidity = await contract.compile('solidity');
const javascript = await contract.compile('javascript');
const rust = await contract.compile('rust');
```

#### `contract.generateX402Headers(conditionsMet)`

Generate X402 payment headers.

```javascript
const headers = contract.generateX402Headers(true);

// Returns:
// {
//   'X402-Contract-ID': 'smart402:saas:abc123',
//   'X402-Payment-Amount': '99',
//   'X402-Payment-Token': 'USDC',
//   'X402-Settlement-Network': 'polygon',
//   'X402-Conditions-Met': 'true',
//   'X402-Signature': 'sig_...',
//   'X402-Nonce': '1234567890'
// }
```

#### `contract.generateJSONLD()`

Generate JSON-LD markup.

```javascript
const jsonld = contract.generateJSONLD();
```

#### `contract.exportYAML()`

Export to YAML.

```javascript
const yaml = contract.exportYAML();
```

#### `contract.exportJSON()`

Export to JSON.

```javascript
const json = contract.exportJSON();
```

#### `contract.getSummary()`

Get contract summary.

```javascript
const summary = contract.getSummary();
```

## CLI Usage

### Initialize

```bash
smart402 init
```

### Create Contract

```bash
smart402 create
```

Interactive prompts will guide you through contract creation.

### Deploy

```bash
smart402 deploy contract.yaml --network polygon-mumbai
```

### Monitor

```bash
smart402 monitor contract.yaml --frequency hourly
```

### Check Status

```bash
smart402 status smart402:contract:abc123
```

### List Templates

```bash
smart402 templates
```

## Advanced Examples

### SaaS with Conditions

```javascript
const contract = await Smart402.create({
  type: 'saas-subscription',
  parties: ['vendor@example.com', 'customer@example.com'],
  payment: {
    amount: 99,
    token: 'USDC',
    blockchain: 'polygon',
    frequency: 'monthly'
  },
  conditions: [
    {
      id: 'uptime_check',
      type: 'api',
      description: 'Service uptime > 99.9%',
      endpoint: 'https://status.example.com/api/uptime',
      threshold: 0.999
    },
    {
      id: 'support_response',
      type: 'metric',
      description: 'Support response time < 4 hours',
      metric: 'avg_response_time',
      threshold: 4,
      unit: 'hours'
    }
  ]
});
```

### Freelancer Escrow

```javascript
const contract = await Smart402.create({
  type: 'freelancer-escrow',
  parties: ['client@company.com', 'freelancer@dev.com'],
  payment: {
    amount: 5000,
    token: 'USDC',
    blockchain: 'polygon',
    frequency: 'milestone-based',
    escrow: true
  },
  milestones: [
    {
      id: 'milestone_1',
      title: 'Project Setup',
      amount: 1000,
      deliverables: ['Repository setup', 'Documentation'],
      conditions: [...]
    },
    {
      id: 'milestone_2',
      title: 'Development',
      amount: 2000,
      deliverables: ['Core features', 'Tests'],
      conditions: [...]
    },
    // ...
  ]
});

await contract.deploy({ escrowEnabled: true });
```

### API Monetization

```javascript
const contract = await Smart402.create({
  type: 'api-payment',
  parties: ['api-provider@service.com', 'api-consumer@client.com'],
  payment: {
    amount: 0.10,
    token: 'USDC',
    blockchain: 'polygon',
    frequency: 'per-request'
  }
});

// Generate X402 headers for each request
const headers = contract.generateX402Headers(true);

// Make API call with payment
const response = await fetch('https://api.service.com/endpoint', {
  headers: headers
});
```

### Batch Payments

```javascript
const batchResult = await contract.executeBatchPayment({
  requests: [
    { requestId: 'req_1', amount: 0.10 },
    { requestId: 'req_2', amount: 0.10 },
    { requestId: 'req_3', amount: 0.10 }
  ]
});

console.log('Gas saved:', batchResult.gasSaved);
```

## TypeScript Support

Full TypeScript definitions included:

```typescript
import { Smart402, Contract, ContractConfig } from '@smart402/sdk';

const config: ContractConfig = {
  type: 'saas-subscription',
  parties: ['vendor@example.com', 'customer@example.com'],
  payment: {
    amount: 99,
    token: 'USDC',
    blockchain: 'polygon',
    frequency: 'monthly'
  }
};

const contract: Contract = await Smart402.create(config);
```

## Error Handling

```javascript
try {
  const contract = await Smart402.create(config);
  const result = await contract.deploy({ network: 'polygon' });
} catch (error) {
  if (error.code === 'VALIDATION_ERROR') {
    console.error('Invalid contract:', error.message);
  } else if (error.code === 'DEPLOYMENT_ERROR') {
    console.error('Deployment failed:', error.message);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

## Testing

```javascript
const { Smart402 } = require('@smart402/sdk');

describe('Contract Tests', () => {
  test('should create contract', async () => {
    const contract = await Smart402.create({
      type: 'test',
      parties: ['a@test.com', 'b@test.com'],
      payment: {
        amount: 10,
        token: 'USDC',
        blockchain: 'polygon-mumbai',
        frequency: 'one-time'
      }
    });

    expect(contract.ucl.contract_id).toContain('smart402:');
  });
});
```

## Resources

- **[API Reference](API-Reference)** - Complete API documentation
- **[Examples](Examples)** - More examples
- **[TypeScript Definitions](https://github.com/MARDOCHEEJ0SEPH/smart402/tree/main/framework/sdk/javascript/src/types)**
- **[npm Package](https://www.npmjs.com/package/@smart402/sdk)**

---

[← Quick Start](Quick-Start) | [Python SDK →](Python-SDK)
