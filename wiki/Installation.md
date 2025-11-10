# Installation

Get started with Smart402 in less than 5 minutes.

## Prerequisites

Choose your preferred language:

### JavaScript/Node.js
- **Node.js** >= 16.0.0
- **npm** >= 7.0.0

### Python
- **Python** >= 3.8
- **pip** >= 20.0

### Rust
- **Rust** >= 1.70
- **Cargo** (comes with Rust)

## Installation Methods

### JavaScript SDK

#### NPM
```bash
npm install @smart402/sdk
```

#### Yarn
```bash
yarn add @smart402/sdk
```

#### pnpm
```bash
pnpm add @smart402/sdk
```

### Python SDK

#### pip
```bash
pip install smart402
```

#### pip (development mode)
```bash
git clone https://github.com/MARDOCHEEJ0SEPH/smart402.git
cd smart402/framework/sdk/python
pip install -e ".[dev]"
```

### Rust SDK

#### Cargo.toml
Add to your `Cargo.toml`:
```toml
[dependencies]
smart402 = "1.0.0"
tokio = { version = "1", features = ["full"] }
```

#### CLI Installation
```bash
cargo install smart402
```

## Verify Installation

### JavaScript
```bash
node -e "const {Smart402} = require('@smart402/sdk'); console.log('✓ Smart402 installed');"
```

Or check the version:
```bash
smart402 --version
```

### Python
```bash
python -c "import smart402; print('✓ Smart402 installed')"
```

Or check the version:
```bash
smart402 --version
```

### Rust
```bash
cargo build
```

Or check CLI:
```bash
smart402 --version
```

## Environment Setup

### Create Configuration File

Create a `.env` file in your project root:

```env
# Default blockchain network
DEFAULT_NETWORK=polygon

# Private key for deployments (KEEP SECRET!)
PRIVATE_KEY=your_private_key_here

# RPC endpoints
POLYGON_RPC_URL=https://polygon-rpc.com
POLYGON_MUMBAI_RPC_URL=https://rpc-mumbai.maticvigil.com

# API keys (optional)
INFURA_API_KEY=your_infura_key
ALCHEMY_API_KEY=your_alchemy_key
```

**⚠️ Security Warning**: Never commit `.env` files to version control!

Add to `.gitignore`:
```
.env
.env.local
.env.*.local
```

### Initialize Smart402

Run the initialization command:

```bash
# JavaScript
smart402 init

# Python
smart402 init

# Rust
smart402 init
```

This will create:
- `.env` file with configuration
- Example contract templates
- Configuration for your preferred network

## Testnet Setup

For testing, we recommend using **Polygon Mumbai** testnet:

### 1. Get Testnet Tokens

**Testnet MATIC** (for gas):
- Visit: https://faucet.polygon.technology/
- Enter your wallet address
- Receive free testnet MATIC

**Testnet USDC**:
- Contract: `0x0FA8781a83E46826621b3BC094Ea2A0212e71B23`
- Use Mumbai faucet or testnet token faucet

### 2. Configure MetaMask

Add Polygon Mumbai network:
- **Network Name**: Polygon Mumbai
- **RPC URL**: https://rpc-mumbai.maticvigil.com
- **Chain ID**: 80001
- **Currency Symbol**: MATIC
- **Block Explorer**: https://mumbai.polygonscan.com

### 3. Test Your Setup

```javascript
// JavaScript
const contract = await Smart402.create({
  type: 'test',
  parties: ['alice@test.com', 'bob@test.com'],
  payment: {
    amount: 1,
    token: 'USDC',
    blockchain: 'polygon-mumbai',
    frequency: 'one-time'
  }
});

await contract.deploy({ network: 'polygon-mumbai' });
console.log('✓ Testnet deployment successful!');
```

## IDE Setup

### Visual Studio Code

Recommended extensions:
```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "ms-python.python",
    "rust-lang.rust-analyzer",
    "esbenp.prettier-vscode"
  ]
}
```

### IntelliJ IDEA / WebStorm

1. Install plugins:
   - JavaScript and TypeScript
   - Python
   - Rust
   - ESLint
   - Prettier

2. Enable Smart402 SDK autocomplete

## CLI Tools

After installation, you have access to Smart402 CLI:

```bash
# Create a contract
smart402 create

# Deploy to blockchain
smart402 deploy contract.yaml --network polygon-mumbai

# Monitor contract
smart402 monitor contract.yaml

# Check status
smart402 status smart402:contract:abc123

# List templates
smart402 templates
```

## Troubleshooting

### JavaScript

**Error: Module not found**
```bash
npm install
npm run build
```

**Error: Permission denied**
```bash
sudo npm install -g @smart402/sdk
```

### Python

**Error: No module named 'smart402'**
```bash
pip install --upgrade smart402
```

**Error: Permission denied**
```bash
pip install --user smart402
```

### Rust

**Error: failed to compile**
```bash
cargo clean
cargo build
```

**Error: linker not found**
```bash
# Ubuntu/Debian
sudo apt install build-essential

# macOS
xcode-select --install

# Windows
# Install Visual Studio Build Tools
```

## Next Steps

✅ Installation complete!

Continue to:
- **[Quick Start](Quick-Start)** - Create your first contract
- **[Your First Contract](Your-First-Contract)** - Detailed tutorial
- **[Examples](Examples)** - Real-world use cases

## Getting Help

- **GitHub Issues**: https://github.com/MARDOCHEEJ0SEPH/smart402/issues
- **Discord**: https://discord.gg/smart402
- **Documentation**: https://docs.smart402.io

---

[← Home](Home) | [Quick Start →](Quick-Start)
