# Smart402 Rust SDK

[![Crates.io](https://img.shields.io/crates/v/smart402.svg)](https://crates.io/crates/smart402)
[![Documentation](https://docs.rs/smart402/badge.svg)](https://docs.rs/smart402)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Universal Protocol for AI-Native Smart Contracts - Rust SDK

Smart402 combines three revolutionary technologies:
- **AEO (Answer Engine Optimization)**: Makes contracts discoverable by AI systems
- **LLMO (Large Language Model Optimization)**: Structures contracts for LLM understanding
- **X402 Protocol**: HTTP extension for automatic machine-to-machine payments

## Quick Start

### Installation

Add to your `Cargo.toml`:

```toml
[dependencies]
smart402 = "1.0.0"
tokio = { version = "1", features = ["full"] }
```

Or install the CLI:

```bash
cargo install smart402
```

### 5-Minute Example

```rust
use smart402::{Smart402, ContractConfig, PaymentConfig};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create contract
    let contract = Smart402::create(ContractConfig {
        contract_type: "saas-subscription".to_string(),
        parties: vec![
            "vendor@example.com".to_string(),
            "customer@example.com".to_string(),
        ],
        payment: PaymentConfig {
            amount: 1000.0,
            token: "USDC".to_string(),
            blockchain: "polygon".to_string(),
            frequency: "monthly".to_string(),
        },
        conditions: None,
        metadata: None,
    }).await?;

    // Deploy
    let result = contract.deploy("polygon").await?;
    println!("Deployed: {}", result.address);

    // Monitor and auto-execute
    contract.start_monitoring("hourly", None).await?;

    Ok(())
}
```

## CLI Usage

### Create Contract

```bash
# Interactive creation
smart402 create

# From template
smart402 create --template saas-subscription

# Save to specific file
smart402 create --output my-contract.yaml
```

### Deploy Contract

```bash
smart402 deploy contract.yaml --network polygon
```

### Monitor & Auto-Execute

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

### Initialize Configuration

```bash
smart402 init
```

## Library Usage

### Creating Contracts

```rust
use smart402::{Smart402, ContractConfig, PaymentConfig};

let config = ContractConfig {
    contract_type: "freelancer-payment".to_string(),
    parties: vec![
        "freelancer@example.com".to_string(),
        "client@example.com".to_string(),
    ],
    payment: PaymentConfig {
        amount: 5000.0,
        token: "USDC".to_string(),
        blockchain: "polygon".to_string(),
        frequency: "one-time".to_string(),
    },
    conditions: None,
    metadata: None,
};

let contract = Smart402::create(config).await?;
```

### Using Templates

```rust
use std::collections::HashMap;

let mut variables = HashMap::new();
variables.insert("vendor_email".to_string(), "vendor@example.com".into());
variables.insert("customer_email".to_string(), "customer@example.com".into());
variables.insert("amount".to_string(), 1000.0.into());

let contract = Smart402::from_template(
    "saas-subscription".to_string(),
    variables
).await?;
```

### Deploying Contracts

```rust
let mut contract = Smart402::create(config).await?;

let result = contract.deploy("polygon").await?;
println!("Contract Address: {}", result.address);
println!("Transaction Hash: {}", result.transaction_hash);
println!("Block Number: {:?}", result.block_number);
```

### Monitoring & Execution

```rust
// Start monitoring
contract.start_monitoring("hourly", None).await?;

// Manual condition check
let check_result = contract.check_conditions().await?;
if check_result.all_met {
    let payment_result = contract.execute_payment().await?;
    println!("Payment executed: {}", payment_result.transaction_hash);
}
```

### Compiling to Target Languages

```rust
use smart402::LLMOEngine;

let llmo = LLMOEngine::new();

// Compile to Solidity
let solidity_code = llmo.compile(&contract.ucl, "solidity")?;

// Compile to JavaScript
let js_code = llmo.compile(&contract.ucl, "javascript")?;

// Compile to Rust
let rust_code = llmo.compile(&contract.ucl, "rust")?;
```

### AEO Score

```rust
use smart402::AEOEngine;

let aeo = AEOEngine::new();
let score = aeo.calculate_score(&contract.ucl)?;

println!("AEO Score: {}", score.total);
println!("  Semantic Richness: {}", score.semantic_richness);
println!("  Citation Friendliness: {}", score.citation_friendliness);
println!("  Findability: {}", score.findability);
```

### X402 Protocol

```rust
use smart402::X402Client;

let client = X402Client::new("https://api.smart402.io".to_string());

// Generate headers
let headers = client.generate_headers(&contract.ucl, true)?;

// Send payment request
let response = client.send_payment_request(headers, payload).await?;
println!("Payment Status: {}", response.status);
```

### Export & Import

```rust
use smart402::utils;
use std::path::Path;

// Save to file
utils::save_contract(&contract.ucl, Path::new("contract.yaml"), "yaml")?;

// Load from file
let loaded_ucl = utils::load_contract(Path::new("contract.yaml"))?;

// Export to JSON
let json = utils::export_json(&contract.ucl)?;

// Export to YAML
let yaml = utils::export_yaml(&contract.ucl)?;
```

## Features

### Core Features
- ✅ Contract creation with intuitive API
- ✅ Template system for common use cases
- ✅ Blockchain deployment (Ethereum, Polygon, etc.)
- ✅ Automatic condition monitoring
- ✅ Payment execution
- ✅ Multi-format export (YAML, JSON)

### AEO (Answer Engine Optimization)
- ✅ AI discoverability scoring
- ✅ JSON-LD markup generation
- ✅ Schema.org integration
- ✅ Citation-friendly formatting

### LLMO (Large Language Model Optimization)
- ✅ Universal Contract Language (UCL)
- ✅ Contract validation
- ✅ Plain-English explanations
- ✅ Multi-target compilation (Solidity, JavaScript, Rust)

### X402 Protocol
- ✅ HTTP header generation
- ✅ Payment request handling
- ✅ Signature verification
- ✅ Webhook support

## Architecture

```
smart402/
├── src/
│   ├── lib.rs              # Main library entry
│   ├── main.rs             # CLI binary
│   ├── types.rs            # Type definitions
│   ├── error.rs            # Error types
│   ├── core/
│   │   ├── smart402.rs     # Main SDK struct
│   │   └── contract.rs     # Contract instance
│   ├── aeo/
│   │   └── engine.rs       # AEO engine
│   ├── llmo/
│   │   └── engine.rs       # LLMO engine
│   ├── x402/
│   │   └── client.rs       # X402 client
│   └── utils/
│       └── mod.rs          # Utilities
├── examples/
│   └── quickstart.rs
└── Cargo.toml
```

## Documentation

- [Framework Overview](../../README.md)
- [AEO Specification](../../specs/aeo/README.md)
- [LLMO Specification](../../specs/llmo/README.md)
- [X402 Specification](../../specs/x402/README.md)
- [API Documentation](https://docs.rs/smart402)

## Examples

See the [examples](./examples) directory for complete examples:

- [quickstart.rs](./examples/quickstart.rs) - Complete workflow example

## Requirements

- Rust 1.70 or higher
- Tokio runtime for async operations

## Contributing

Contributions are welcome! Please see our [Contributing Guidelines](../../CONTRIBUTING.md).

## License

MIT License - see [LICENSE](../../LICENSE) for details.

## Author

Mardochée JOSEPH

## Support

- Documentation: https://docs.smart402.io
- Issues: https://github.com/smart402/framework/issues
- Discord: https://discord.gg/smart402
