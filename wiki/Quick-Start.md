# Quick Start

Create and deploy your first Smart402 contract in 5 minutes.

## Choose Your Language

<details>
<summary><strong>JavaScript / TypeScript</strong></summary>

### 1. Install SDK

```bash
npm install @smart402/sdk
```

### 2. Create Contract

```javascript
const { Smart402 } = require('@smart402/sdk');

// Create a monthly SaaS subscription contract
const contract = await Smart402.create({
  type: 'saas-subscription',
  parties: [
    'vendor@example.com',
    'customer@example.com'
  ],
  payment: {
    amount: 99,
    token: 'USDC',
    blockchain: 'polygon',
    frequency: 'monthly'
  }
});

console.log('Contract created:', contract.ucl.contract_id);
```

### 3. Deploy to Blockchain

```javascript
const result = await contract.deploy({
  network: 'polygon-mumbai'  // Use testnet first!
});

console.log('Deployed at:', result.address);
console.log('Transaction:', result.transactionHash);
```

### 4. Start Monitoring

```javascript
await contract.startMonitoring({
  frequency: 'hourly',
  autoExecute: true
});

console.log('✓ Contract is now monitoring and will auto-execute!');
```

### Complete Example

```javascript
const { Smart402 } = require('@smart402/sdk');

async function main() {
  // 1. Create contract
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

  // 2. Deploy
  const result = await contract.deploy({ network: 'polygon-mumbai' });
  console.log('Deployed:', result.address);

  // 3. Monitor
  await contract.startMonitoring({ frequency: 'hourly' });
  console.log('✓ Monitoring started!');
}

main();
```

</details>

<details>
<summary><strong>Python</strong></summary>

### 1. Install SDK

```bash
pip install smart402
```

### 2. Create Contract

```python
from smart402 import Smart402

# Create a monthly SaaS subscription contract
contract = await Smart402.create({
    'type': 'saas-subscription',
    'parties': [
        'vendor@example.com',
        'customer@example.com'
    ],
    'payment': {
        'amount': 99,
        'token': 'USDC',
        'blockchain': 'polygon',
        'frequency': 'monthly'
    }
})

print(f'Contract created: {contract.ucl["contract_id"]}')
```

### 3. Deploy to Blockchain

```python
result = await contract.deploy(network='polygon-mumbai')

print(f'Deployed at: {result["address"]}')
print(f'Transaction: {result["transaction_hash"]}')
```

### 4. Start Monitoring

```python
await contract.start_monitoring(
    frequency='hourly',
    auto_execute=True
)

print('✓ Contract is now monitoring and will auto-execute!')
```

### Complete Example

```python
import asyncio
from smart402 import Smart402

async def main():
    # 1. Create contract
    contract = await Smart402.create({
        'type': 'saas-subscription',
        'parties': ['vendor@example.com', 'customer@example.com'],
        'payment': {
            'amount': 99,
            'token': 'USDC',
            'blockchain': 'polygon',
            'frequency': 'monthly'
        }
    })

    # 2. Deploy
    result = await contract.deploy(network='polygon-mumbai')
    print(f'Deployed: {result["address"]}')

    # 3. Monitor
    await contract.start_monitoring(frequency='hourly')
    print('✓ Monitoring started!')

if __name__ == '__main__':
    asyncio.run(main())
```

</details>

<details>
<summary><strong>Rust</strong></summary>

### 1. Add Dependency

Add to `Cargo.toml`:
```toml
[dependencies]
smart402 = "1.0.0"
tokio = { version = "1", features = ["full"] }
```

### 2. Create Contract

```rust
use smart402::{Smart402, ContractConfig, PaymentConfig};

// Create a monthly SaaS subscription contract
let contract = Smart402::create(ContractConfig {
    contract_type: "saas-subscription".to_string(),
    parties: vec![
        "vendor@example.com".to_string(),
        "customer@example.com".to_string(),
    ],
    payment: PaymentConfig {
        amount: 99.0,
        token: "USDC".to_string(),
        blockchain: "polygon".to_string(),
        frequency: "monthly".to_string(),
    },
    conditions: None,
    metadata: None,
}).await?;

println!("Contract created: {}", contract.ucl.contract_id);
```

### 3. Deploy to Blockchain

```rust
let result = contract.deploy("polygon-mumbai").await?;

println!("Deployed at: {}", result.address);
println!("Transaction: {}", result.transaction_hash);
```

### 4. Start Monitoring

```rust
contract.start_monitoring("hourly", None).await?;

println!("✓ Contract is now monitoring and will auto-execute!");
```

### Complete Example

```rust
use smart402::{Smart402, ContractConfig, PaymentConfig};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 1. Create contract
    let mut contract = Smart402::create(ContractConfig {
        contract_type: "saas-subscription".to_string(),
        parties: vec![
            "vendor@example.com".to_string(),
            "customer@example.com".to_string(),
        ],
        payment: PaymentConfig {
            amount: 99.0,
            token: "USDC".to_string(),
            blockchain: "polygon".to_string(),
            frequency: "monthly".to_string(),
        },
        conditions: None,
        metadata: None,
    }).await?;

    // 2. Deploy
    let result = contract.deploy("polygon-mumbai").await?;
    println!("Deployed: {}", result.address);

    // 3. Monitor
    contract.start_monitoring("hourly", None).await?;
    println!("✓ Monitoring started!");

    Ok(())
}
```

</details>

## Using CLI

If you prefer command-line tools:

```bash
# 1. Initialize
smart402 init

# 2. Create contract (interactive)
smart402 create

# 3. Deploy to testnet
smart402 deploy contract.yaml --network polygon-mumbai

# 4. Monitor contract
smart402 monitor contract.yaml --frequency hourly
```

## What Just Happened?

In those few lines of code, you:

1. ✅ **Created** an AI-native smart contract
2. ✅ **Optimized** it for AI discoverability (AEO)
3. ✅ **Validated** it for LLM understanding (LLMO)
4. ✅ **Deployed** it to blockchain
5. ✅ **Set up** automatic monitoring and execution (X402)

## Understanding the Contract

### AEO Score
Your contract is now discoverable by AI systems:
```javascript
const score = contract.getAEOScore();
console.log('AI Discoverability:', (score.total * 100).toFixed(0) + '%');
```

### LLM Understanding
Get a plain-English explanation:
```javascript
const explanation = contract.explain();
console.log(explanation);
```

### X402 Headers
Generate payment headers for automatic execution:
```javascript
const headers = contract.generateX402Headers(true);
console.log('Payment headers:', headers);
```

## Next Steps

### Try More Examples

- **[SaaS Subscription](Example-SaaS-Subscription)** - Monthly payments with SLA
- **[Freelancer Escrow](Example-Freelancer-Escrow)** - Milestone-based payments
- **[API Monetization](Example-API-Monetization)** - Pay-per-use with X402

### Dive Deeper

- **[Your First Contract](Your-First-Contract)** - Detailed tutorial
- **[JavaScript SDK](JavaScript-SDK)** - Complete SDK documentation
- **[Python SDK](Python-SDK)** - Python-specific features
- **[Rust SDK](Rust-SDK)** - High-performance Rust

### Deploy to Mainnet

Once tested on testnet:

1. Update network to mainnet:
   ```javascript
   await contract.deploy({ network: 'polygon' });
   ```

2. Fund with real tokens (USDC, USDT, etc.)

3. Monitor in production:
   ```javascript
   await contract.startMonitoring({
     frequency: 'hourly',
     webhook: 'https://your-api.com/webhooks/smart402'
   });
   ```

## Common Patterns

### Free Tier + Paid Tier

```javascript
const price = userTier === 'free' ? 0 : 99;

const contract = await Smart402.create({
  type: userTier === 'free' ? 'free-tier' : 'premium-tier',
  payment: {
    amount: price,
    token: price === 0 ? 'NONE' : 'USDC',
    // ...
  }
});
```

### Conditional Execution

```javascript
const contract = await Smart402.create({
  // ...
  conditions: [
    {
      id: 'uptime_check',
      type: 'api',
      description: 'Service uptime > 99%',
      endpoint: 'https://status.example.com/api/uptime',
      threshold: 0.99
    }
  ]
});
```

### Milestone-Based

```javascript
const contract = await Smart402.create({
  type: 'freelancer-escrow',
  milestones: [
    { id: 'setup', amount: 1000, deliverables: ['...'] },
    { id: 'development', amount: 2000, deliverables: ['...'] },
    { id: 'deployment', amount: 500, deliverables: ['...'] }
  ]
});
```

## Troubleshooting

**Contract not deploying?**
- Check you have testnet tokens (MATIC for gas)
- Verify RPC endpoint is correct
- Try increasing gas limit

**Monitoring not working?**
- Ensure contract is deployed first
- Check webhook URL is accessible
- Verify conditions are correctly formatted

**Payment not executing?**
- Confirm all conditions are met
- Check token approval
- Verify sufficient balance

## Getting Help

- 📖 **[Full Documentation](API-Reference)**
- 💬 **[Discord Community](https://discord.gg/smart402)**
- 🐛 **[GitHub Issues](https://github.com/MARDOCHEEJ0SEPH/smart402/issues)**
- 📧 **Email**: team@smart402.io

---

[← Installation](Installation) | [Your First Contract →](Your-First-Contract)
