# Smart402 JavaScript SDK - Advanced Examples

This directory contains advanced examples demonstrating the full capabilities of the Smart402 JavaScript SDK.

## Examples Overview

### 01. Quickstart (`01-quickstart.js`)
**Difficulty**: Beginner
**Duration**: 5 minutes

Complete workflow demonstration covering:
- Creating a basic SaaS subscription contract
- Calculating AEO scores for AI discoverability
- Contract validation and explanation
- Multi-target compilation (Solidity, JavaScript, Rust)
- Deployment to Polygon
- X402 header generation
- Condition checking and payment execution
- Export to YAML/JSON

**Run it:**
```bash
node examples/01-quickstart.js
```

---

### 02. SaaS Subscription with SLA (`02-saas-subscription.js`)
**Difficulty**: Intermediate
**Duration**: 10 minutes

Enterprise SaaS contract with advanced features:
- Monthly subscription with uptime SLA requirements
- Multiple condition types (API, metrics, verification)
- Service credit penalties for SLA breaches
- Automated monitoring with webhooks
- JSON-LD generation for SEO
- Conditional payment execution based on SLA compliance

**Key Features:**
- 99.9% uptime requirement
- Support response time monitoring
- Daily backup verification
- Automatic penalty calculations
- Webhook notifications

**Run it:**
```bash
node examples/02-saas-subscription.js
```

---

### 03. Freelancer Escrow (`03-freelancer-escrow.js`)
**Difficulty**: Advanced
**Duration**: 15 minutes

Multi-milestone freelancer contract with escrow protection:
- 4-milestone payment structure ($5,000 total)
- Escrow-based fund holding
- Per-milestone deliverables and conditions
- Automated verification (GitHub, CI/CD, manual review)
- Dispute resolution mechanism
- Progressive payment release

**Milestones:**
1. **Project Setup & Architecture** - $1,000
2. **Core Feature Development** - $2,000
3. **Frontend & Integration** - $1,500
4. **Deployment & Documentation** - $500

**Key Features:**
- Client funds held in escrow
- Work verification before release
- 7-day dispute window
- Transparent on-chain records

**Run it:**
```bash
node examples/03-freelancer-escrow.js
```

---

### 04. Supply Chain with IoT (`04-supply-chain.js`)
**Difficulty**: Advanced
**Duration**: 20 minutes

Pharmaceutical cold chain delivery with IoT monitoring:
- Multi-party contract (supplier, distributor, retailer)
- Real-time IoT sensor integration
- GPS tracking with geofencing
- Temperature and humidity monitoring (2°C - 8°C)
- Tamper detection
- Split payment distribution
- Penalty system for violations

**Monitoring:**
- Continuous temperature control
- Real-time GPS tracking
- Seal integrity verification
- Quality inspection on delivery

**Key Features:**
- Critical vs. standard conditions
- Automatic penalty calculation
- Split payment (60% supplier, 40% distributor)
- Compliance tracking (FDA, WHO-GDP, HACCP)

**Run it:**
```bash
node examples/04-supply-chain.js
```

---

### 05. X402 Protocol Integration (`05-x402-integration.js`)
**Difficulty**: Advanced
**Duration**: 15 minutes

Pay-per-use API service with X402 protocol:
- HTTP header-based automatic payments
- Machine-to-machine payment flow
- Micropayments ($0.10 per API call)
- Batch settlement for gas optimization
- Cryptographic signature verification
- Webhook event system
- Tier pricing (volume discounts)

**X402 Features:**
- Automatic payment with each request
- No manual invoicing needed
- Built-in SLA enforcement
- Gas-optimized batch settlements (~67% savings)
- Real-time payment verification

**Workflow:**
1. Client generates X402 headers
2. API request sent with headers
3. Smart402 verifies signature & conditions
4. API processes request
5. Payment authorized automatically
6. Batch settlement on-chain

**Run it:**
```bash
node examples/05-x402-integration.js
```

---

## Running All Examples

To run all examples in sequence:

```bash
npm run examples
```

Or run individually:

```bash
node examples/01-quickstart.js
node examples/02-saas-subscription.js
node examples/03-freelancer-escrow.js
node examples/04-supply-chain.js
node examples/05-x402-integration.js
```

## Output Files

Examples generate output files in `examples/output/`:
- `saas-contract.yaml` - SaaS subscription contract
- `freelancer-escrow.yaml` - Freelancer escrow contract
- `supply-chain-report.json` - Supply chain tracking report
- `x402-config.json` - X402 integration configuration

## Prerequisites

```bash
npm install
```

Required dependencies:
- `@smart402/sdk` - Smart402 JavaScript SDK
- `chalk` - Terminal styling
- `axios` - HTTP client (for X402 example)

## Environment Variables

Create `.env` file for blockchain operations:

```env
DEFAULT_NETWORK=polygon
PRIVATE_KEY=your_private_key_here
INFURA_API_KEY=your_infura_key_here
```

## Key Concepts Demonstrated

### AEO (Answer Engine Optimization)
- AI discoverability scoring
- JSON-LD markup generation
- Schema.org integration
- Citation-friendly formatting

### LLMO (Large Language Model Optimization)
- Universal Contract Language (UCL)
- Contract validation
- Plain-English explanations
- Multi-target compilation

### X402 Protocol
- HTTP payment headers
- Automatic payment flow
- Signature verification
- Batch settlement
- Webhook events

### Contract Features
- Multi-party agreements
- Milestone-based payments
- Escrow protection
- IoT sensor integration
- Condition monitoring
- Penalty enforcement
- Split payments
- Dispute resolution

## Use Cases Covered

1. **SaaS Subscriptions** - Recurring payments with SLA
2. **Freelance Work** - Milestone-based escrow payments
3. **Supply Chain** - IoT-verified delivery payments
4. **API Monetization** - Pay-per-use with X402
5. **Service Agreements** - Automated compliance checking

## Architecture Patterns

- **Pay-per-use**: X402 micropayments
- **Milestone-based**: Escrow with progressive release
- **Condition-based**: Payment upon verification
- **Split payments**: Multi-party distribution
- **Batch settlement**: Gas optimization

## Best Practices

1. **Always validate contracts** before deployment
2. **Check AEO scores** for AI discoverability
3. **Use escrow** for untrusted parties
4. **Monitor conditions** continuously
5. **Implement webhooks** for real-time updates
6. **Batch payments** to save gas
7. **Export contracts** for record-keeping
8. **Handle errors** gracefully

## Next Steps

After exploring the examples:

1. **Read the Protocol Specs**:
   - [AEO Specification](../../specs/aeo/README.md)
   - [LLMO Specification](../../specs/llmo/README.md)
   - [X402 Specification](../../specs/x402/README.md)

2. **Build Your Own Contract**:
   - Use `smart402 create` CLI
   - Customize for your use case
   - Deploy to testnet first

3. **Integrate with Your App**:
   - Install SDK: `npm install @smart402/sdk`
   - Import: `const { Smart402 } = require('@smart402/sdk')`
   - Create contracts programmatically

4. **Join the Community**:
   - Discord: https://discord.gg/smart402
   - GitHub: https://github.com/smart402/framework
   - Docs: https://docs.smart402.io

## Support

For questions or issues:
- GitHub Issues: https://github.com/smart402/framework/issues
- Documentation: https://docs.smart402.io
- Discord: https://discord.gg/smart402

## License

MIT License - see [LICENSE](../../../LICENSE) for details.

## Author

Mardochée JOSEPH
