# Smart402 Python SDK

**Universal Protocol for AI-Native Smart Contracts**

The official Python SDK for creating, deploying, and managing Smart402 contracts that are discoverable by ANY AI, understandable by ANY LLM, and executable automatically.

## Quick Start

### Installation

```bash
pip install smart402
```

### 5-Minute Example

```python
from smart402 import Smart402

# Create a monthly subscription contract
contract = await Smart402.create({
    'type': 'saas-subscription',
    'parties': ['vendor@example.com', 'customer@example.com'],
    'payment': {
        'amount': 99,
        'frequency': 'monthly',
        'token': 'USDC'
    }
})

# Deploy to Polygon
await contract.deploy(network='polygon')

# Start automatic monitoring
await contract.start_monitoring(frequency='hourly')

print(f'Contract deployed: {contract.address}')
# ✅ Payments will execute automatically when conditions met!
```

## Features

✨ **5-Minute Setup** - From install to deployed contract
🤖 **AI-Native** - Discoverable by ChatGPT, Claude, Gemini
🔄 **Automatic Execution** - Payments trigger when conditions met
⛓️ **Multi-Chain** - Ethereum, Polygon, Arbitrum, Optimism, Base
🐍 **Pythonic** - Clean, intuitive Python API
🛠️ **CLI Tools** - Command-line interface included
📚 **Templates** - Pre-built templates for common use cases

## Installation

### pip

```bash
pip install smart402
```

### From source

```bash
git clone https://github.com/smart402/framework
cd framework/sdk/python
pip install -e .
```

## Usage

### Basic Usage

```python
from smart402 import Smart402

# Initialize
smart402 = Smart402(
    network='polygon',
    private_key='your_private_key'
)

# Create contract
contract = await smart402.create_contract({
    'type': 'saas-subscription',
    'parties': ['0xVendor...', '0xCustomer...'],
    'payment': {
        'amount': 99,
        'token': 'USDC',
        'frequency': 'monthly'
    }
})

# Deploy
deployment = await contract.deploy()
print(f'Deployed to: {deployment["address"]}')
```

### Using Templates

```python
from smart402 import Smart402

# List templates
templates = Smart402.get_templates()
print(templates)
# ['saas-subscription', 'freelancer-milestone', ...]

# Create from template
contract = await Smart402.from_template('saas-subscription', {
    'vendor': '0xVendor...',
    'customer': '0xCustomer...',
    'monthly_price': 99,
    'uptime': 0.99
})

await contract.deploy(network='polygon')
```

### Automatic Monitoring

```python
# Start monitoring - payments execute automatically
await contract.start_monitoring(
    frequency='hourly',  # realtime, high, medium, low, daily
    webhook='https://api.example.com/webhooks/payment'
)

# Check conditions manually
status = await contract.check_conditions()
print(f'All conditions met: {status["all_met"]}')

# Execute payment manually
if status['all_met']:
    payment = await contract.execute_payment()
    print(f'Payment: {payment["transaction_hash"]}')

# Stop monitoring
await contract.stop_monitoring()
```

### Contract Information

```python
# Get summary
print(contract.get_summary())
# "This contract charges $99/month for SaaS service..."

# Get payment terms
terms = contract.get_payment_terms()
print(terms)
# {'amount': 99, 'frequency': 'monthly', 'token': 'USDC', ...}

# Get parties
parties = contract.get_parties()

# Get AEO score
print(f'AEO Score: {contract.get_aeo_score()}/100')

# Get contract URL
print(f'View: {contract.get_url()}')

# Export contract
yaml_str = await contract.export('yaml')
json_str = await contract.export('json')
```

## CLI Usage

Install globally:

```bash
pip install smart402
```

### Commands

```bash
# Create contract
smart402 create

# Create from template
smart402 create --template saas-subscription

# Deploy
smart402 deploy contract.yaml --network polygon

# Monitor continuously
smart402 monitor smart402:saas:abc123 --frequency hourly

# Check once
smart402 monitor smart402:saas:abc123 --dry-run

# Check status
smart402 status smart402:saas:abc123

# List templates
smart402 templates

# Initialize config
smart402 init
```

## Examples

### Example 1: SaaS Subscription

```python
contract = await Smart402.create({
    'type': 'saas-subscription',
    'parties': ['vendor@saas.com', 'customer@company.com'],
    'payment': {
        'amount': 99,
        'token': 'USDC',
        'frequency': 'monthly'
    },
    'conditions': [
        {
            'id': 'uptime',
            'description': 'Service uptime >= 99%',
            'source': 'monitoring_api',
            'operator': 'gte',
            'threshold': 0.99
        }
    ]
})

await contract.deploy(network='polygon')
await contract.start_monitoring(frequency='daily')
```

### Example 2: Freelancer Milestones

```python
contract = await Smart402.from_template('freelancer-milestone', {
    'client': '0xClient...',
    'freelancer': '0xFreelancer...',
    'milestones': [
        {'name': 'Design', 'amount': 2500, 'due_date': '2024-02-01'},
        {'name': 'Development', 'amount': 5000, 'due_date': '2024-03-01'},
        {'name': 'Testing', 'amount': 1500, 'due_date': '2024-03-15'}
    ],
    'total_budget': 9000,
    'token': 'USDC'
})

await contract.deploy(network='polygon')
```

### Example 3: Supply Chain

```python
contract = await Smart402.create({
    'type': 'supply-chain',
    'parties': ['supplier@factory.com', 'buyer@retailer.com'],
    'payment': {
        'amount': 50000,
        'token': 'USDC',
        'frequency': 'one-time'
    },
    'conditions': [
        {
            'id': 'delivery',
            'description': 'Delivery confirmed',
            'source': 'fedex_api',
            'operator': 'equals',
            'threshold': 'delivered'
        }
    ]
})

await contract.deploy(network='ethereum')
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
  "private_key": "your_private_key",
  "rpc_url": "https://polygon-rpc.com",
  "api_key": "your_api_key"
}
```

**⚠️ Important:** Add `.smart402.json` to `.gitignore`!

## Available Templates

| Template | Description |
|----------|-------------|
| `saas-subscription` | Monthly/yearly SaaS payments with uptime SLA |
| `freelancer-milestone` | Project-based payments with milestones |
| `supply-chain` | Payment upon delivery confirmation |
| `affiliate-commission` | Commission payments for referrals |
| `vendor-sla` | SLA with automatic penalties |
| `escrow` | Multi-sig escrow for secure transactions |

## API Reference

### Smart402 Class

#### `Smart402.create(config, **options)`
Create a new contract.

#### `Smart402.from_template(template, variables, **options)`
Create from template.

#### `Smart402.load(contract_id, **options)`
Load existing contract.

#### `Smart402.get_templates()`
Get available templates.

### Contract Class

#### `await contract.deploy(**options)`
Deploy to blockchain.

#### `await contract.start_monitoring(**options)`
Start auto-monitoring.

#### `await contract.check_conditions()`
Check if conditions met.

#### `await contract.execute_payment()`
Execute payment manually.

#### `await contract.compile(target='solidity')`
Compile to target language.

#### `await contract.export(format='yaml')`
Export contract.

## Testing

```python
from smart402.testing import test_contract

# Test before deployment
await test_contract(contract) \
    .check_aeo_score() \
    .check_llmo_compliance() \
    .simulate_execution() \
    .run()
```

## Development

```bash
# Clone repository
git clone https://github.com/smart402/framework
cd framework/sdk/python

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black smart402/

# Type check
mypy smart402/
```

## Troubleshooting

### Common Issues

**"Network connection failed"**
- Check RPC URL
- Ensure internet connection
- Try different RPC provider

**"Insufficient funds"**
- Check wallet balance
- Ensure enough tokens for gas

**"Contract validation failed"**
- Review validation errors
- Check all required fields present

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
