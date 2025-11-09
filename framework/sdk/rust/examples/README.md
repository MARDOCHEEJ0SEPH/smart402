# Smart402 Rust SDK - Examples

This directory contains examples demonstrating the Smart402 Rust SDK capabilities.

## Examples

### 1. Quickstart (`quickstart.rs`)
**Difficulty**: Beginner
**Duration**: 5 minutes

Complete workflow demonstration covering:
- Creating a SaaS subscription contract
- Calculating AEO scores for AI discoverability
- Contract validation and explanation
- Multi-target compilation (Solidity, JavaScript, Rust)
- Deployment to Polygon
- X402 header generation
- Condition checking and payment execution
- Export to YAML/JSON

**Run it:**
```bash
cargo run --example quickstart
```

---

### 2. Book Seller (`book-seller.rs`)
**Difficulty**: Intermediate
**Duration**: 10 minutes

Digital book seller with conditional pricing:
- **Free Option**: Smart402 Introduction eBook (no payment)
- **Premium Option**: Workshop Book + Materials ($10 USDC)
- Deployment to EVM testnet (Polygon Mumbai)
- Automatic fulfillment after payment
- X402 payment integration
- Instant digital delivery

**Features:**
- Conditional payment (free vs paid)
- Testnet deployment with real transaction links
- AEO scoring for AI discoverability
- JSON-LD generation for SEO
- X402 payment headers
- Automatic delivery after verification
- Block explorer integration

**What's Included:**

**Free eBook:**
- Smart402 Introduction PDF
- Getting Started Guide

**Workshop Book ($10 USDC):**
- Workshop Book PDF
- Video Tutorials (5 hours)
- Source Code Repository Access
- Live Q&A Session Access
- Certificate of Completion

**Run it:**
```bash
cargo run --example book-seller
```

**Expected Output:**
```
📚 Smart402 Book Seller Example

Welcome to the Smart402 Bookstore!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 Available Books:

1. Free Option:
   Smart402 Introduction - Free eBook
   ...

2. Premium Option:
   Smart402 Workshop - Premium Book + Materials
   Price: $10 USDC
   ...

✓ Selected: Smart402 Workshop - Premium Book + Materials

📝 Creating purchase contract...
   ✓ Contract created: smart402:digital-product-purchase:abc123

📋 Contract Details:
  ...

🤖 AI Discoverability Check (AEO):
  Overall Score: 85.2%
  ...

✅ Validating Contract:
  ✓ Contract is valid and ready for deployment

🚀 Deploying to Polygon Mumbai Testnet:
  ✓ Deployment successful!

  Deployment Details:
    Contract Address: 0x1234...
    Transaction Hash: 0xabc...
    Network: polygon-mumbai

  📊 View on Block Explorer:
    Contract: https://mumbai.polygonscan.com/address/0x1234...
    Transaction: https://mumbai.polygonscan.com/tx/0xabc...

💳 Processing Payment:
  Payment Details:
    Amount: $10 USDC
    ...

  ✓ Payment executed successfully!

📦 Fulfillment:
  ✓ Payment verified
  ✓ Generating download links...

  Your Books & Materials:
    1. Workshop Book PDF - Ready to download
       https://downloads.smart402.io/...
    2. Video Tutorials - Ready to download
       https://downloads.smart402.io/...
    ...

✨ Book purchase completed successfully!
```

---

## Running Examples

### Run a specific example:
```bash
cargo run --example quickstart
cargo run --example book-seller
```

### Run with release optimizations:
```bash
cargo run --release --example quickstart
cargo run --release --example book-seller
```

### Build all examples:
```bash
cargo build --examples
```

## Prerequisites

1. **Rust Installation:**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

2. **Dependencies:**
All dependencies are automatically handled by Cargo based on `Cargo.toml`

3. **Environment Variables** (Optional):
Create `.env` file for blockchain operations:
```env
DEFAULT_NETWORK=polygon-mumbai
PRIVATE_KEY=your_testnet_private_key_here
RPC_URL=https://rpc-mumbai.maticvigil.com
```

## Testnet Setup (for book-seller example)

### Polygon Mumbai Testnet

1. **Get Testnet MATIC:**
   - Visit: https://faucet.polygon.technology/
   - Enter your wallet address
   - Receive free testnet MATIC

2. **Get Testnet USDC:**
   - Testnet USDC contract: `0x0FA8781a83E46826621b3BC094Ea2A0212e71B23`
   - Use Polygon Mumbai faucet or test token faucet

3. **Add Network to MetaMask:**
   - Network Name: Polygon Mumbai
   - RPC URL: https://rpc-mumbai.maticvigil.com
   - Chain ID: 80001
   - Currency Symbol: MATIC
   - Block Explorer: https://mumbai.polygonscan.com

4. **View Transactions:**
   - All transactions will be visible on Mumbai PolygonScan
   - Links are automatically generated in the example output

## Key Concepts Demonstrated

### Book Seller Example

**Conditional Pricing:**
```rust
let price = match book_type {
    BookType::FreeEbook => 0.0,
    BookType::WorkshopBook => 10.0,
};
```

**Testnet Deployment:**
```rust
let result = contract.deploy("polygon-mumbai").await?;
println!("Contract: https://mumbai.polygonscan.com/address/{}", result.address);
```

**X402 Payment:**
```rust
let x402 = X402Client::new("https://x402.smart402.io".to_string());
let headers = x402.generate_headers(&contract.ucl, true)?;
```

**Automatic Fulfillment:**
```rust
if payment_verified {
    deliver_digital_products(&customer, &book.deliverables()).await?;
}
```

### Quickstart Example

**Complete Workflow:**
- Contract creation
- AEO scoring
- Validation
- Compilation
- Deployment
- Payment execution

## Use Cases

1. **Digital Product Sales**
   - eBooks, courses, software
   - Instant delivery
   - Conditional pricing

2. **Subscription Services**
   - Monthly/annual payments
   - Auto-renewal
   - SLA monitoring

3. **Freelance Work**
   - Milestone payments
   - Escrow protection
   - Delivery verification

4. **Supply Chain**
   - IoT integration
   - Multi-party contracts
   - Condition-based payments

5. **API Monetization**
   - Pay-per-use
   - X402 integration
   - Micropayments

## Architecture Patterns

- **Conditional Payment**: Free vs paid tiers
- **Instant Fulfillment**: Automatic delivery after payment
- **Testnet First**: Deploy and test before mainnet
- **X402 Integration**: HTTP-based automatic payments
- **AEO Optimization**: AI discoverability
- **Block Explorer**: Transaction transparency

## Best Practices

1. **Always test on testnet first**
2. **Validate contracts before deployment**
3. **Check AEO scores for discoverability**
4. **Use X402 for automatic payments**
5. **Implement proper error handling**
6. **Export contracts for record-keeping**
7. **Provide transaction links for transparency**

## Troubleshooting

### Common Issues

**1. Compilation Errors:**
```bash
cargo clean
cargo build --examples
```

**2. Missing Dependencies:**
```bash
cargo update
```

**3. Testnet Connection Issues:**
- Check RPC URL in `.env`
- Verify testnet is operational
- Try alternative RPC endpoint

**4. Payment Failures:**
- Ensure sufficient testnet MATIC for gas
- Verify USDC token balance
- Check contract approval

## Next Steps

After exploring the examples:

1. **Customize for your use case**
2. **Deploy to mainnet** (after thorough testing)
3. **Integrate with your application**
4. **Add custom conditions and logic**
5. **Implement webhooks for events**

## Documentation

- [Rust SDK Documentation](https://docs.rs/smart402)
- [Framework Overview](../../README.md)
- [AEO Specification](../../specs/aeo/README.md)
- [LLMO Specification](../../specs/llmo/README.md)
- [X402 Specification](../../specs/x402/README.md)

## Support

- GitHub Issues: https://github.com/smart402/framework/issues
- Documentation: https://docs.smart402.io
- Discord: https://discord.gg/smart402

## License

MIT License - see [LICENSE](../../LICENSE) for details.

## Author

Mardochée JOSEPH
