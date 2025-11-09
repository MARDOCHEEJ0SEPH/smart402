# Smart402 JavaScript SDK

**Universal Protocol for AI-Native Smart Contracts**

The official JavaScript SDK for creating, deploying, and managing Smart402 contracts that are discoverable by ANY AI, understandable by ANY LLM, and executable automatically.

## Quick Start

### Installation

```bash
npm install @smart402/sdk
```

### 5-Minute Example

```javascript
const { Smart402 } = require('@smart402/sdk');

// Create a monthly subscription contract
const contract = await Smart402.create({
  type: 'saas-subscription',
  parties: ['vendor@example.com', 'customer@example.com'],
  payment: {
    amount: 99,
    frequency: 'monthly',
    token: 'USDC'
  }
});

// Deploy to Polygon
await contract.deploy({ network: 'polygon' });

// Start automatic monitoring
await contract.startMonitoring({ frequency: 'hourly' });

console.log('Contract deployed:', contract.address);
// ✅ Payments will execute automatically when conditions met!
```

## Features

✨ **5-Minute Setup** - From install to deployed contract in minutes
🤖 **AI-Native** - Discoverable by ChatGPT, Claude, Gemini, any AI
🔄 **Automatic Execution** - Payments trigger automatically when conditions met
⛓️ **Multi-Chain** - Deploy to Ethereum, Polygon, Arbitrum, Optimism, Base
📝 **Type-Safe** - Full TypeScript support with comprehensive types
🛠️ **CLI Tools** - Command-line interface for quick operations
📚 **Templates** - Pre-built templates for common use cases

## Installation

### npm

```bash
npm install @smart402/sdk
```

### yarn

```bash
yarn add @smart402/sdk
```

### pnpm

```bash
pnpm add @smart402/sdk
```

## Usage

### Basic Usage

```javascript
const { Smart402 } = require('@smart402/sdk');

// Initialize with options
const smart402 = new Smart402({
  network: 'polygon',
  privateKey: process.env.PRIVATE_KEY
});

// Create contract
const contract = await smart402.createContract({
  type: 'saas-subscription',
  parties: ['0xVendor...', '0xCustomer...'],
  payment: {
    amount: 99,
    token: 'USDC',
    frequency: 'monthly'
  }
});

// Deploy
const deployment = await contract.deploy();
console.log('Deployed to:', deployment.address);
```

### Using Templates

```javascript
const { Smart402 } = require('@smart402/sdk');

// List available templates
const templates = Smart402.getTemplates();
console.log(templates);
// ['saas-subscription', 'freelancer-milestone', 'supply-chain', ...]

// Create from template
const contract = await Smart402.fromTemplate('saas-subscription', {
  vendor: '0xVendor...',
  customer: '0xCustomer...',
  monthlyPrice: 99,
  uptime: 0.99
});

await contract.deploy({ network: 'polygon' });
```

### Automatic Monitoring

```javascript
// Start monitoring - payments execute automatically when conditions met
await contract.startMonitoring({
  frequency: 'hourly',  // realtime, high, medium, low, daily
  webhook: 'https://api.example.com/webhooks/payment'
});

// Check conditions manually
const status = await contract.checkConditions();
console.log('All conditions met:', status.allMet);
console.log('Condition details:', status.conditions);

// Execute payment manually
if (status.allMet) {
  const payment = await contract.executePayment();
  console.log('Payment completed:', payment.transactionHash);
}

// Stop monitoring
await contract.stopMonitoring();
```

### Contract Information

```javascript
// Get contract summary
console.log(contract.getSummary());
// "This contract charges $99/month for SaaS service..."

// Get payment terms
const terms = contract.getPaymentTerms();
console.log(terms);
// { amount: 99, frequency: 'monthly', token: 'USDC', blockchain: 'polygon' }

// Get parties
const parties = contract.getParties();
console.log(parties);
// [{ role: 'vendor', identifier: '0xVendor...', name: 'Vendor Corp' }, ...]

// Get AEO score (discoverability rating)
console.log('AEO Score:', contract.getAEOScore());
// 85/100

// Get contract URL
console.log('View contract:', contract.getURL());
// https://polygonscan.com/address/0x...

// Export contract
const yaml = await contract.export('yaml');
const json = await contract.export('json');
```

## CLI Usage

Install globally:

```bash
npm install -g @smart402/sdk
```

### Create Contract

Interactive mode:

```bash
smart402 create
```

From template:

```bash
smart402 create --template saas-subscription
```

### Deploy Contract

```bash
smart402 deploy contract.yaml --network polygon
```

### Monitor Contract

```bash
# Continuous monitoring
smart402 monitor smart402:saas:abc123 --frequency hourly

# Check once
smart402 monitor smart402:saas:abc123 --dry-run
```

### Check Status

```bash
smart402 status smart402:saas:abc123
```

### List Templates

```bash
smart402 templates
```

### Initialize Configuration

```bash
smart402 init
```

Creates `.smart402.json` with your default settings.

## Examples

### Example 1: Monthly SaaS Subscription

```javascript
const contract = await Smart402.create({
  type: 'saas-subscription',
  parties: ['vendor@saas.com', 'customer@company.com'],
  payment: {
    amount: 99,
    token: 'USDC',
    frequency: 'monthly'
  },
  conditions: [
    {
      id: 'uptime',
      description: 'Service uptime >= 99%',
      source: 'monitoring_api',
      operator: 'gte',
      threshold: 0.99
    }
  ]
});

await contract.deploy({ network: 'polygon' });
await contract.startMonitoring({ frequency: 'daily' });
```

### Example 2: Freelancer Milestone Payments

```javascript
const contract = await Smart402.fromTemplate('freelancer-milestone', {
  client: '0xClient...',
  freelancer: '0xFreelancer...',
  milestones: [
    { name: 'Design', amount: 2500, dueDate: '2024-02-01' },
    { name: 'Development', amount: 5000, dueDate: '2024-03-01' },
    { name: 'Testing', amount: 1500, dueDate: '2024-03-15' }
  ],
  totalBudget: 9000,
  token: 'USDC'
});

await contract.deploy({ network: 'polygon' });
```

### Example 3: Supply Chain Payment

```javascript
const contract = await Smart402.create({
  type: 'supply-chain',
  parties: ['supplier@factory.com', 'buyer@retailer.com'],
  payment: {
    amount: 50000,
    token: 'USDC',
    frequency: 'one-time'
  },
  conditions: [
    {
      id: 'delivery',
      description: 'Delivery confirmed',
      source: 'fedex_api',
      operator: 'equals',
      threshold: 'delivered'
    },
    {
      id: 'quality',
      description: 'Quality inspection passed',
      source: 'qc_system',
      operator: 'equals',
      threshold: 'passed'
    }
  ]
});

await contract.deploy({ network: 'ethereum' });
```

### Example 4: Affiliate Commission

```javascript
const contract = await Smart402.fromTemplate('affiliate-commission', {
  merchant: '0xMerchant...',
  affiliate: '0xAffiliate...',
  commissionRate: 0.10,  // 10%
  minimumPayout: 100,
  cookieDuration: 30  // days
});

await contract.deploy({ network: 'polygon' });
```

## TypeScript Support

Full TypeScript support with comprehensive types:

```typescript
import { Smart402, Contract, ContractConfig, DeployOptions } from '@smart402/sdk';

const config: ContractConfig = {
  type: 'saas-subscription',
  parties: ['vendor@example.com', 'customer@example.com'],
  payment: {
    amount: 99,
    frequency: 'monthly',
    token: 'USDC'
  }
};

const contract: Contract = await Smart402.create(config);

const deployment: DeployResult = await contract.deploy({
  network: 'polygon',
  gasLimit: 1000000
});
```

## Configuration

### Environment Variables

```bash
SMART402_NETWORK=polygon
SMART402_PRIVATE_KEY=your_private_key
SMART402_RPC_URL=https://polygon-rpc.com
SMART402_API_KEY=your_api_key
```

### Configuration File

Create `.smart402.json`:

```json
{
  "network": "polygon",
  "privateKey": "your_private_key",
  "rpcUrl": "https://polygon-rpc.com",
  "apiKey": "your_api_key"
}
```

**⚠️ Important:** Add `.smart402.json` to `.gitignore`!

## Available Templates

| Template | Type | Description |
|----------|------|-------------|
| `saas-subscription` | Recurring | Monthly/yearly SaaS payments with uptime SLA |
| `freelancer-milestone` | Milestone | Project-based payments with milestone approval |
| `supply-chain` | One-time | Payment upon delivery and quality confirmation |
| `affiliate-commission` | Recurring | Commission payments for referrals |
| `vendor-sla` | Recurring | Service level agreement with automatic penalties |
| `escrow` | One-time | Multi-sig escrow for secure transactions |

Get template details:

```javascript
const doc = Smart402.getTemplateDoc('saas-subscription');
console.log(doc.description);
console.log(doc.variables);
console.log(doc.examples);
```

## API Reference

### Smart402 Class

#### `Smart402.create(config)`
Create a new contract from configuration.

**Parameters:**
- `config: ContractConfig` - Contract configuration

**Returns:** `Promise<Contract>`

#### `Smart402.fromTemplate(template, variables)`
Create contract from template.

**Parameters:**
- `template: string` - Template name
- `variables: Record<string, any>` - Template variables

**Returns:** `Promise<Contract>`

#### `Smart402.load(contractId)`
Load existing contract by ID.

**Parameters:**
- `contractId: string` - Contract ID

**Returns:** `Promise<Contract>`

#### `Smart402.getTemplates()`
Get list of available templates.

**Returns:** `string[]`

#### `Smart402.getTemplateDoc(template)`
Get template documentation.

**Parameters:**
- `template: string` - Template name

**Returns:** `TemplateDocumentation`

### Contract Class

#### `contract.deploy(options)`
Deploy contract to blockchain.

**Parameters:**
- `options: DeployOptions` - Deployment options

**Returns:** `Promise<DeployResult>`

#### `contract.startMonitoring(options)`
Start automatic condition monitoring.

**Parameters:**
- `options: MonitoringOptions` - Monitoring options

**Returns:** `Promise<void>`

#### `contract.checkConditions()`
Check if conditions are met.

**Returns:** `Promise<ConditionCheckResult>`

#### `contract.executePayment()`
Execute payment manually.

**Returns:** `Promise<PaymentResult>`

#### `contract.compile(target)`
Compile contract to target language.

**Parameters:**
- `target: 'solidity' | 'javascript' | 'rust'`

**Returns:** `Promise<string>`

#### `contract.export(format)`
Export contract to format.

**Parameters:**
- `format: 'yaml' | 'json' | 'ucl'`

**Returns:** `Promise<string>`

## Testing

```javascript
const { testContract } = require('@smart402/testing');

// Test contract before deployment
await testContract(contract)
  .checkAEOScore()
  .checkLLMOCompliance()
  .simulateExecution()
  .run();
```

## Troubleshooting

### Common Issues

**1. "Network connection failed"**
- Check your RPC URL is correct
- Ensure you have internet connection
- Try a different RPC provider

**2. "Insufficient funds"**
- Make sure wallet has enough tokens for gas
- Check token balance for payment amount

**3. "Contract validation failed"**
- Review validation errors
- Ensure all required fields are present
- Check condition operators are valid

**4. "Deployment timeout"**
- Increase gas limit
- Try during less congested network times
- Use a faster network (Polygon vs Ethereum)

### Getting Help

- 📖 [Documentation](https://docs.smart402.io)
- 💬 [Discord Community](https://discord.gg/smart402)
- 🐛 [Report Issues](https://github.com/smart402/framework/issues)
- 📧 [Email Support](mailto:support@smart402.io)

## Contributing

We welcome contributions! See [CONTRIBUTING.md](../../CONTRIBUTING.md)

## License

MIT License - see [LICENSE](../../LICENSE)

## Links

- 🌐 [Website](https://smart402.io)
- 📚 [Documentation](https://docs.smart402.io)
- 🐙 [GitHub](https://github.com/smart402/framework)
- 🐦 [Twitter](https://twitter.com/smart402)
- 💬 [Discord](https://discord.gg/smart402)

---

**Made with ❤️ by the Smart402 Community**

*Making every contract discoverable, understandable, and executable by AI.*
