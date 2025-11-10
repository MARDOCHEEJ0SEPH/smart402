# Frequently Asked Questions

## General Questions

### What is Smart402?

Smart402 is a universal protocol for AI-native smart contracts. It combines three technologies (AEO, LLMO, X402) to make contracts discoverable by AI systems, understandable by LLMs, and executable with automatic payments.

### Why "Smart402"?

- **Smart**: Intelligent, AI-native contracts
- **402**: HTTP status code for "Payment Required" - we've extended it for blockchain

### Is Smart402 open source?

Yes! MIT License. Contributions welcome on [GitHub](https://github.com/MARDOCHEEJ0SEPH/smart402).

### Which programming languages are supported?

Three official SDKs:
- **JavaScript/TypeScript** (Node.js, browsers)
- **Python** (3.8+)
- **Rust** (1.70+)

### Which blockchains are supported?

All EVM-compatible chains:
- Ethereum
- Polygon
- Arbitrum
- Optimism
- Base
- And more...

## Technical Questions

### How does AEO work?

AEO optimizes contracts for AI discovery through:
1. **Semantic markup** (JSON-LD, Schema.org)
2. **5-dimension scoring** (semantic richness, citation friendliness, findability, authority, citations)
3. **Multi-platform distribution**

See [AEO Specification](AEO-Specification) for details.

### What is UCL (Universal Contract Language)?

UCL is a 4-layer contract representation:
1. **Human-readable**: Plain English
2. **LLM-structured**: For AI understanding
3. **Machine-executable**: Programmatic format
4. **Blockchain-compilable**: Solidity/bytecode

See [LLMO Specification](LLMO-Specification) for details.

### How does X402 differ from HTTP 402?

X402 extends HTTP 402 with:
- Blockchain-native payments
- Cryptographic verification
- Automatic settlement
- Cross-chain support
- Machine-readable terms

See [X402 Specification](X402-Specification) for details.

### Is Smart402 gas efficient?

Yes! Features include:
- **Batch settlements** (67% gas savings)
- **Optimized storage** patterns
- **Conditional execution** (only when needed)
- **Off-chain verification** when possible

### How secure is Smart402?

Security measures:
- ✅ Formal verification
- ✅ Comprehensive test suites (>90% coverage)
- ✅ Cryptographic signatures
- ✅ Escrow support
- ✅ Dispute resolution
- ✅ Open source auditing

## Usage Questions

### How do I get started?

Three steps:
1. Install SDK: `npm install @smart402/sdk`
2. Create contract: `Smart402.create({...})`
3. Deploy: `contract.deploy({network: 'polygon'})`

See [Quick Start](Quick-Start) for details.

### Can I use Smart402 for free?

Yes! The SDK is free and open source. You only pay:
- Blockchain gas fees
- Token payments (if your contract requires them)

### Do I need to know blockchain programming?

No! Smart402 abstracts blockchain complexity:
- No Solidity required
- No web3 boilerplate
- Simple JavaScript/Python/Rust API

### Can I test before deploying to mainnet?

Absolutely! Use testnets:
- **Polygon Mumbai**: Recommended for testing
- **Ethereum Goerli/Sepolia**: Also supported
- **Free testnet tokens**: Available from faucets

### How do I deploy to mainnet?

```javascript
// Just change the network
await contract.deploy({ network: 'polygon' }); // mainnet
```

**Important**: Test thoroughly on testnet first!

### Can Smart402 work with existing contracts?

Yes! You can:
1. Wrap existing contracts with Smart402
2. Use Smart402 as middleware
3. Migrate gradually

## Payment Questions

### Which tokens are supported?

Major stablecoins:
- USDC
- USDT
- DAI
- Native tokens (ETH, MATIC, etc.)

### How are payments processed?

Two modes:
1. **On-chain**: Direct smart contract execution
2. **X402 Protocol**: HTTP-based automatic payments

### What happens if payment fails?

Configurable behavior:
- Retry logic
- Fallback mechanisms
- Dispute resolution
- Refund procedures

### Can I do recurring payments?

Yes! Supported frequencies:
- Hourly
- Daily
- Weekly
- Monthly
- Quarterly
- Custom intervals

### Is there escrow support?

Yes! Perfect for:
- Freelancer payments
- Multi-party agreements
- Milestone-based releases

## Development Questions

### How do I add custom conditions?

```javascript
const contract = await Smart402.create({
  // ...
  conditions: [
    {
      id: 'my_condition',
      type: 'api',
      description: 'Custom check',
      endpoint: 'https://api.example.com/check',
      threshold: 0.95
    }
  ]
});
```

### Can I customize the templates?

Yes! Either:
1. Modify existing templates
2. Create new templates
3. Use base configuration

### How do I handle errors?

```javascript
try {
  await contract.deploy({...});
} catch (error) {
  if (error.code === 'DEPLOYMENT_ERROR') {
    // Handle deployment failure
  }
}
```

### Is TypeScript supported?

Yes! Full TypeScript definitions included:

```typescript
import { Smart402, Contract, ContractConfig } from '@smart402/sdk';
```

### How do I run tests?

```bash
# JavaScript
npm test

# Python
pytest

# Rust
cargo test
```

See [Testing Guide](Testing-Guide) for details.

## Deployment Questions

### What are the gas costs?

Typical costs (on Polygon):
- **Deployment**: ~$0.01-0.05
- **Payment execution**: ~$0.001-0.01
- **Condition checking**: ~$0.001

Much cheaper than Ethereum mainnet!

### How long does deployment take?

- **Testnet**: 2-10 seconds
- **Mainnet**: 15-30 seconds (Polygon)
- **Ethereum**: 15 seconds - 5 minutes

### Can I cancel a deployment?

Before mining: Yes, if transaction is pending.
After mining: No, contract is on-chain.

### How do I verify my contract?

Smart402 automatically generates verification data:
```javascript
const verification = contract.getVerificationData();
// Submit to block explorer
```

## Monitoring Questions

### How does automatic monitoring work?

Smart402 checks conditions at your specified frequency:
1. **Quick**: Every 15 minutes
2. **Medium**: Hourly
3. **Slow**: Daily

### Can I use webhooks?

Yes! Get notified of events:

```javascript
await contract.startMonitoring({
  frequency: 'hourly',
  webhook: 'https://your-api.com/webhook'
});
```

### What events are available?

- `condition_check`: Condition was checked
- `payment_due`: Payment is due
- `payment_executed`: Payment completed
- `condition_failed`: Condition not met
- `dispute_raised`: Dispute initiated

### Can I stop monitoring?

```javascript
await contract.stopMonitoring();
```

## Troubleshooting

### Contract not deploying?

Check:
1. ✅ Sufficient gas (testnet MATIC)
2. ✅ Valid RPC endpoint
3. ✅ Network connectivity
4. ✅ Contract validation passed

### Payment not executing?

Check:
1. ✅ Conditions are met
2. ✅ Token approval granted
3. ✅ Sufficient balance
4. ✅ Monitoring is active

### AEO score is low?

Improve by:
1. ✅ Adding more metadata
2. ✅ Clear descriptions
3. ✅ Comprehensive documentation
4. ✅ Proper JSON-LD markup

See [AEO Specification](AEO-Specification) for optimization tips.

### Tests are failing?

```bash
# Clean and reinstall
npm install  # or pip install, cargo clean
npm test     # or pytest, cargo test
```

## Community Questions

### How can I contribute?

See [Contributing Guide](Contributing) for:
- Code contributions
- Documentation improvements
- Bug reports
- Feature requests

### Where can I get help?

- **GitHub Issues**: Bug reports, feature requests
- **Discord**: Real-time community support
- **Stack Overflow**: Tag with `smart402`
- **Email**: team@smart402.io

### Is there a roadmap?

Yes! Check [GitHub Projects](https://github.com/MARDOCHEEJ0SEPH/smart402/projects) for:
- Planned features
- Current priorities
- Community requests

### Can I use Smart402 commercially?

Yes! MIT License allows commercial use. No restrictions.

## More Questions?

- Check the [Documentation](Home)
- Join our [Discord](https://discord.gg/smart402)
- Open an [Issue](https://github.com/MARDOCHEEJ0SEPH/smart402/issues)

---

[← Home](Home) | [Contributing →](Contributing)
