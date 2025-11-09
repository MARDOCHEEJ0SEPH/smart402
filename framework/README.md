# Smart402 Framework

**The Universal Protocol for AI-Native Smart Contracts**

> Making contracts discoverable by ANY AI, understandable by ANY LLM, and executable by ANY machine.

## Quick Start (5 Minutes)

```bash
# Install the Smart402 SDK
npm install @smart402/sdk

# Create your first AI-native contract
const { Smart402 } = require('@smart402/sdk');

const contract = await Smart402.create({
  type: 'saas-subscription',
  parties: ['vendor@example.com', 'customer@example.com'],
  payment: {
    amount: 1000,
    frequency: 'monthly',
    token: 'USDC'
  }
});

// Deploy to blockchain
await contract.deploy({ network: 'polygon' });

// Contract is now:
// ✓ Discoverable by ChatGPT, Claude, Gemini
// ✓ Understandable by any LLM
// ✓ Executable automatically
```

## What is Smart402?

Smart402 is an **open protocol framework** that combines three revolutionary technologies:

### 🔍 **AEO (Answer Engine Optimization)**
Makes your contracts discoverable and citable by AI engines like ChatGPT, Claude, and Perplexity.

### 🧠 **LLMO (Large Language Model Optimization)**
Structures contracts so any LLM can understand, verify, and reason about the terms.

### 💳 **X402 Protocol**
HTTP extension that enables automatic machine-to-machine payments.

## Why Smart402?

### Traditional Smart Contracts
```
❌ Not discoverable by AI
❌ Not readable by LLMs
❌ Require manual execution
❌ Platform-specific
```

### Smart402 Contracts
```
✅ Any AI can find them
✅ Any LLM can understand them
✅ Machines execute automatically
✅ Works everywhere
```

## Framework Architecture

```
┌─────────────────────────────────────────┐
│     Your Application / AI Agent         │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         Smart402 SDK Layer              │
│   (JavaScript, Python, Rust, Go)        │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────┐
│  AEO   │  │  LLMO  │  │  X402  │
│Protocol│  │Protocol│  │Protocol│
└────────┘  └────────┘  └────────┘
    │            │            │
    └────────────┼────────────┘
                 ▼
        ┌────────────────┐
        │   Blockchain   │
        │  (Any Chain)   │
        └────────────────┘
```

## Protocol Specifications

### 📄 [AEO Protocol Spec](./specs/aeo/README.md)
Standards for making contracts AI-discoverable:
- Semantic markup formats
- Content optimization rules
- Citation frameworks
- Cross-platform distribution

### 📄 [LLMO Protocol Spec](./specs/llmo/README.md)
Universal Contract Language (UCL) specification:
- Contract structure standards
- Machine-readable format
- Natural language mapping
- Verification rules

### 📄 [X402 Protocol Spec](./specs/x402/README.md)
HTTP extension for automated payments:
- Header specifications
- Payment flow protocol
- Settlement standards
- Dispute resolution

## SDK Implementations

### JavaScript SDK
```bash
npm install @smart402/sdk
```
[Documentation](./sdk/javascript/README.md) | [Examples](./examples/javascript/)

### Python SDK
```bash
pip install smart402
```
[Documentation](./sdk/python/README.md) | [Examples](./examples/python/)

### Rust SDK
```bash
cargo add smart402
```
[Documentation](./sdk/rust/README.md) | [Examples](./examples/rust/)

### Go SDK
```bash
go get github.com/smart402/sdk-go
```
[Documentation](./sdk/go/README.md) | [Examples](./examples/go/)

## Universal Contract Templates

Smart402 provides ready-to-use templates for common scenarios:

```javascript
// SaaS Subscription
Smart402.templates.saasSubscription({ ... })

// Freelancer Payment
Smart402.templates.freelancerMilestone({ ... })

// Supply Chain
Smart402.templates.supplyChainDelivery({ ... })

// Affiliate Commission
Smart402.templates.affiliateCommission({ ... })

// Vendor SLA
Smart402.templates.vendorSLA({ ... })
```

[View All Templates](./contracts/README.md)

## Developer Tools

### CLI Tool
```bash
# Install
npm install -g @smart402/cli

# Create new contract
smart402 create --type saas-subscription

# Deploy
smart402 deploy --network polygon

# Monitor
smart402 monitor --contract-id abc123
```

### Testing Framework
```bash
npm install --save-dev @smart402/testing
```

### VS Code Extension
Search for "Smart402" in VS Code marketplace for:
- Contract syntax highlighting
- Auto-completion
- Validation
- Deployment tools

## Quick Examples

### 1. Monthly SaaS Payment
```javascript
const contract = await Smart402.create({
  type: 'saas-subscription',
  vendor: '0xVendor...',
  customer: '0xCustomer...',
  amount: 99,
  frequency: 'monthly',
  conditions: {
    serviceUptime: 0.99,
    support: '24/7'
  }
});
```

### 2. Freelancer Milestone
```javascript
const contract = await Smart402.create({
  type: 'freelancer-milestone',
  client: '0xClient...',
  freelancer: '0xFreelancer...',
  milestones: [
    { name: 'Design', amount: 2500, dueDate: '2024-02-01' },
    { name: 'Development', amount: 5000, dueDate: '2024-03-01' },
    { name: 'Testing', amount: 1500, dueDate: '2024-03-15' }
  ],
  escrow: true
});
```

### 3. Supply Chain Payment
```javascript
const contract = await Smart402.create({
  type: 'supply-chain',
  supplier: '0xSupplier...',
  buyer: '0xBuyer...',
  amount: 50000,
  conditions: {
    delivery: 'confirmed',
    quality: 'ISO-9001',
    timeline: '30-days'
  },
  oracles: ['chainlink', 'fedex-api']
});
```

## How It Works

### 1. **Discovery** (AEO)
```
User asks ChatGPT: "I need a freelancer payment contract"
              ↓
ChatGPT finds Smart402 contract template
              ↓
Returns optimized contract for user's needs
```

### 2. **Understanding** (LLMO)
```
LLM reads contract in Universal Contract Language
              ↓
Understands terms, conditions, payment logic
              ↓
Can explain, verify, and reason about contract
```

### 3. **Execution** (X402)
```
Oracle detects: Work completed ✓
              ↓
X402 protocol: Triggers automatic payment
              ↓
Blockchain: Settles transaction
```

## Integration Examples

### With AI Agents
```javascript
// Your AI agent can create contracts directly
const agent = new AIAgent();
const contract = await agent.createContract({
  prompt: "Create a monthly payment contract for $1000 USDC"
});
```

### With Existing Apps
```javascript
// Drop-in replacement for manual contracts
app.checkout.onComplete(async (order) => {
  await Smart402.create({
    type: 'one-time-payment',
    amount: order.total,
    recipient: order.vendor
  });
});
```

### With Web3 Apps
```javascript
// Works with any Web3 wallet
const contract = await Smart402.create({
  wallet: await ethereum.request({ method: 'eth_requestAccounts' }),
  // ... contract details
});
```

## Why Developers Love Smart402

### 🚀 **5-Minute Setup**
```bash
npm install @smart402/sdk
# You're ready to go
```

### 🎯 **Simple API**
```javascript
// That's it!
Smart402.create({ type, parties, payment })
```

### 🔌 **Works Everywhere**
- Any blockchain (Ethereum, Polygon, Arbitrum, Solana)
- Any language (JavaScript, Python, Rust, Go)
- Any AI (ChatGPT, Claude, Gemini)

### 📚 **Great Docs**
- [5-Minute Quickstart](./docs/quickstart.md)
- [Full API Reference](./docs/api-reference.md)
- [Contract Templates](./docs/templates.md)
- [Video Tutorials](./docs/videos.md)

### 🧪 **Easy Testing**
```javascript
const { testContract } = require('@smart402/testing');

testContract(myContract)
  .checkAEOScore()
  .checkLLMOCompliance()
  .simulateExecution();
```

### 🌍 **Open Source**
- MIT License
- Public specifications
- Community-driven
- No vendor lock-in

## Ecosystem

### Built on Smart402
- **ContractGPT** - AI contract generator
- **PayStream** - Automated payment platform
- **ChainLegal** - Legal compliance checker
- **FreelanceDAO** - Decentralized marketplace

[View Ecosystem](./docs/ecosystem.md)

## Roadmap

### ✅ Phase 1 (Q1 2024) - Foundation
- [x] Protocol specifications
- [x] JavaScript SDK
- [x] Python SDK
- [x] 5 contract templates

### 🚧 Phase 2 (Q2 2024) - Expansion
- [ ] Rust SDK
- [ ] Go SDK
- [ ] 20 more templates
- [ ] VS Code extension

### 📋 Phase 3 (Q3 2024) - Ecosystem
- [ ] Developer portal
- [ ] Template marketplace
- [ ] AI training dataset
- [ ] Standards body submission (W3C, IEEE)

### 🌟 Phase 4 (Q4 2024) - Adoption
- [ ] 1000+ deployed contracts
- [ ] 10 AI integrations
- [ ] Enterprise partnerships
- [ ] X402 HTTP standard proposal

## Community

- **Discord**: [Join our community](https://discord.gg/smart402)
- **GitHub**: [Contribute](https://github.com/smart402/framework)
- **Twitter**: [@smart402](https://twitter.com/smart402)
- **Forum**: [discuss.smart402.io](https://discuss.smart402.io)

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md)

### Ways to Contribute
- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Submit PRs
- 🌍 Translate docs
- 🎓 Create tutorials

## License

MIT License - see [LICENSE](./LICENSE)

## Citation

```bibtex
@misc{smart402,
  title={Smart402: Universal Protocol for AI-Native Smart Contracts},
  author={Smart402 Contributors},
  year={2024},
  url={https://github.com/smart402/framework}
}
```

## Learn More

- [Full Documentation](./docs/)
- [Protocol Specifications](./specs/)
- [Video Tutorials](./docs/videos.md)
- [Blog](https://blog.smart402.io)
- [Case Studies](./docs/case-studies/)

---

**Smart402: The TCP/IP of Commerce**

*Making every contract discoverable, understandable, and executable by AI.*
