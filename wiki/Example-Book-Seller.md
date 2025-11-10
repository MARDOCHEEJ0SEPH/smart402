# Example: Book Seller with Testnet Deployment

Complete example of a digital book seller with free and paid tiers, deployed to Polygon Mumbai testnet.

## Overview

This example demonstrates:
- Conditional pricing (free vs paid)
- Testnet deployment
- Automatic fulfillment
- Real blockchain transactions

## Use Case

Digital bookstore selling Smart402 resources:
- **Free eBook**: Smart402 Introduction (no payment)
- **Workshop Book**: Premium content for $10 USDC

## Code Example (Rust)

```rust
use smart402::{Smart402, ContractConfig, PaymentConfig, AEOEngine, LLMOEngine};
use colored::Colorize;

#[derive(Debug, Clone)]
enum BookType {
    FreeEbook,
    WorkshopBook,
}

impl BookType {
    fn name(&self) -> &str {
        match self {
            BookType::FreeEbook => "Smart402 Introduction - Free eBook",
            BookType::WorkshopBook => "Smart402 Workshop - Premium Book + Materials",
        }
    }

    fn price(&self) -> f64 {
        match self {
            BookType::FreeEbook => 0.0,
            BookType::WorkshopBook => 10.0,
        }
    }

    fn deliverables(&self) -> Vec<String> {
        match self {
            BookType::FreeEbook => vec![
                "smart402-intro.pdf".to_string(),
                "Getting Started Guide".to_string(),
            ],
            BookType::WorkshopBook => vec![
                "smart402-workshop-book.pdf".to_string(),
                "Video Tutorials (5 hours)".to_string(),
                "Source Code Repository Access".to_string(),
                "Live Q&A Session Access".to_string(),
                "Certificate of Completion".to_string(),
            ],
        }
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("{}", "\n📚 Smart402 Book Seller Example\n".blue().bold());

    // User selects workshop book
    let selected_book = BookType::WorkshopBook;
    println!("{}", format!("✓ Selected: {}", selected_book.name()).green());

    // Create purchase contract
    let is_free = matches!(selected_book, BookType::FreeEbook);

    let contract = Smart402::create(ContractConfig {
        contract_type: "digital-product-purchase".to_string(),
        parties: vec![
            "bookstore@smart402.io".to_string(),
            "customer@example.com".to_string(),
        ],
        payment: PaymentConfig {
            amount: selected_book.price(),
            token: if is_free { "NONE".to_string() } else { "USDC".to_string() },
            blockchain: "polygon-mumbai".to_string(), // Testnet!
            frequency: "one-time".to_string(),
        },
        conditions: Some(vec![
            serde_json::json!({
                "id": "payment_received",
                "type": "payment",
                "description": if is_free {
                    "No payment required for free book"
                } else {
                    "Payment of 10 USDC required"
                },
                "required": !is_free,
            }),
            serde_json::json!({
                "id": "email_verified",
                "type": "verification",
                "description": "Customer email verified",
                "required": true,
            }),
        ]),
        metadata: Some(serde_json::json!({
            "title": selected_book.name(),
            "category": "digital-product",
            "product_type": "book",
            "format": "digital",
            "instant_delivery": true,
            "deliverables": selected_book.deliverables(),
        })),
    }).await?;

    println!("{}", "✓ Contract created".green());
    println!("  Contract ID: {}", contract.ucl.contract_id);
    println!("  Price: ${} {}", contract.ucl.payment.amount, contract.ucl.payment.token);
    println!();

    // Check AEO score
    let aeo = AEOEngine::new();
    let score = aeo.calculate_score(&contract.ucl)?;
    println!("🤖 AI Discoverability: {:.1}%", score.total * 100.0);
    println!();

    // Validate contract
    let llmo = LLMOEngine::new();
    let validation = llmo.validate(&contract.ucl)?;
    if validation.valid {
        println!("{}", "✓ Contract is valid".green());
    }
    println!();

    // Deploy to testnet
    println!("{}", "🚀 Deploying to Polygon Mumbai Testnet...".yellow());
    let mut contract = contract;
    let result = contract.deploy("polygon-mumbai").await?;

    println!("{}", "✓ Deployment successful!".green());
    println!("  Contract Address: {}", result.address);
    println!("  Transaction Hash: {}", result.transaction_hash);
    println!("  Network: {}", result.network);
    println!();

    // View on block explorer
    println!("📊 View on Block Explorer:");
    println!("  https://mumbai.polygonscan.com/address/{}", result.address);
    println!("  https://mumbai.polygonscan.com/tx/{}", result.transaction_hash);
    println!();

    // Process payment (if not free)
    if !is_free {
        println!("{}", "💳 Processing Payment...".yellow());

        // Generate X402 headers
        let x402 = smart402::X402Client::new("https://x402.smart402.io".to_string());
        let headers = x402.generate_headers(&contract.ucl, true)?;

        println!("  X402-Payment-Amount: {}", headers.payment_amount);
        println!("  X402-Payment-Token: {}", headers.payment_token);
        println!();

        // Execute payment
        let payment_result = contract.execute_payment().await?;
        println!("{}", "✓ Payment executed!".green());
        println!("  Transaction: {}", payment_result.transaction_hash);
        println!();
    }

    // Automatic fulfillment
    println!("{}", "📦 Fulfillment:".yellow());
    println!("{}", "  ✓ Payment verified".green());
    println!("{}", "  ✓ Generating download links...".green());
    println!();

    println!("  Your Books & Materials:");
    for (i, deliverable) in selected_book.deliverables().iter().enumerate() {
        println!("    {}. {} - {}", i + 1, deliverable, "Ready to download".green());
        let link = format!(
            "https://downloads.smart402.io/{}/{}",
            contract.ucl.contract_id,
            deliverable.replace(" ", "-").to_lowercase()
        );
        println!("       {}", link);
    }
    println!();

    println!("{}", "✨ Book purchase completed successfully!".green().bold());

    Ok(())
}
```

## Features Demonstrated

### 1. Conditional Pricing

```rust
let price = match book_type {
    BookType::FreeEbook => 0.0,
    BookType::WorkshopBook => 10.0,
};

let token = if price == 0.0 { "NONE" } else { "USDC" };
```

### 2. Testnet Deployment

```rust
PaymentConfig {
    blockchain: "polygon-mumbai".to_string(), // Testnet
    // ...
}
```

### 3. AEO Scoring

```rust
let aeo = AEOEngine::new();
let score = aeo.calculate_score(&contract.ucl)?;
println!("AI Discoverability: {:.1}%", score.total * 100.0);
```

### 4. Contract Validation

```rust
let llmo = LLMOEngine::new();
let validation = llmo.validate(&contract.ucl)?;
if validation.valid {
    println!("✓ Contract is valid");
}
```

### 5. X402 Payment Flow

```rust
let x402 = X402Client::new("https://x402.smart402.io".to_string());
let headers = x402.generate_headers(&contract.ucl, true)?;
// Use headers for payment verification
```

### 6. Automatic Delivery

After payment verification:
- Generate download links
- Grant access to materials
- Send confirmation email
- Update customer portal

## Running the Example

### Prerequisites

1. **Get Testnet Tokens**:
   - Visit https://faucet.polygon.technology/
   - Get free testnet MATIC for gas
   - Get testnet USDC from Mumbai faucet

2. **Set up wallet**:
   - Add Polygon Mumbai to MetaMask
   - Import your private key to `.env`

### Run

```bash
cargo run --example book-seller
```

### Expected Output

```
📚 Smart402 Book Seller Example

✓ Selected: Smart402 Workshop - Premium Book + Materials

✓ Contract created
  Contract ID: smart402:digital-product-purchase:abc123
  Price: $10 USDC

🤖 AI Discoverability: 85.2%

✓ Contract is valid

🚀 Deploying to Polygon Mumbai Testnet...
✓ Deployment successful!
  Contract Address: 0x1234...
  Transaction Hash: 0xabc...
  Network: polygon-mumbai

📊 View on Block Explorer:
  https://mumbai.polygonscan.com/address/0x1234...
  https://mumbai.polygonscan.com/tx/0xabc...

💳 Processing Payment...
  X402-Payment-Amount: 10
  X402-Payment-Token: USDC

✓ Payment executed!
  Transaction: 0xdef...

📦 Fulfillment:
  ✓ Payment verified
  ✓ Generating download links...

  Your Books & Materials:
    1. Workshop Book PDF - Ready to download
       https://downloads.smart402.io/.../workshop-book-pdf
    2. Video Tutorials (5 hours) - Ready to download
       https://downloads.smart402.io/.../video-tutorials
    ...

✨ Book purchase completed successfully!
```

## JavaScript Version

```javascript
const { Smart402 } = require('@smart402/sdk');

const bookTypes = {
  free: {
    name: 'Smart402 Introduction - Free eBook',
    price: 0,
    deliverables: ['smart402-intro.pdf', 'Getting Started Guide']
  },
  workshop: {
    name: 'Smart402 Workshop - Premium Book',
    price: 10,
    deliverables: [
      'workshop-book.pdf',
      'Video Tutorials (5 hours)',
      'Source Code Access',
      'Live Q&A Access',
      'Certificate'
    ]
  }
};

async function purchaseBook(bookType) {
  const book = bookTypes[bookType];

  // Create contract
  const contract = await Smart402.create({
    type: 'digital-product-purchase',
    parties: ['bookstore@smart402.io', 'customer@example.com'],
    payment: {
      amount: book.price,
      token: book.price === 0 ? 'NONE' : 'USDC',
      blockchain: 'polygon-mumbai',
      frequency: 'one-time'
    },
    metadata: {
      title: book.name,
      deliverables: book.deliverables
    }
  });

  // Deploy to testnet
  const result = await contract.deploy({ network: 'polygon-mumbai' });
  console.log('Deployed:', result.address);

  // Process payment if needed
  if (book.price > 0) {
    const payment = await contract.executePayment();
    console.log('Payment:', payment.transactionHash);
  }

  // Deliver content
  console.log('Delivering:', book.deliverables);

  return contract;
}

// Purchase workshop book
purchaseBook('workshop');
```

## Python Version

```python
from smart402 import Smart402

book_types = {
    'free': {
        'name': 'Smart402 Introduction - Free eBook',
        'price': 0,
        'deliverables': ['smart402-intro.pdf', 'Getting Started Guide']
    },
    'workshop': {
        'name': 'Smart402 Workshop - Premium Book',
        'price': 10,
        'deliverables': [
            'workshop-book.pdf',
            'Video Tutorials (5 hours)',
            'Source Code Access',
            'Live Q&A Access',
            'Certificate'
        ]
    }
}

async def purchase_book(book_type):
    book = book_types[book_type]

    # Create contract
    contract = await Smart402.create({
        'type': 'digital-product-purchase',
        'parties': ['bookstore@smart402.io', 'customer@example.com'],
        'payment': {
            'amount': book['price'],
            'token': 'NONE' if book['price'] == 0 else 'USDC',
            'blockchain': 'polygon-mumbai',
            'frequency': 'one-time'
        },
        'metadata': {
            'title': book['name'],
            'deliverables': book['deliverables']
        }
    })

    # Deploy to testnet
    result = await contract.deploy(network='polygon-mumbai')
    print(f'Deployed: {result["address"]}')

    # Process payment if needed
    if book['price'] > 0:
        payment = await contract.execute_payment()
        print(f'Payment: {payment["transaction_hash"]}')

    # Deliver content
    print(f'Delivering: {book["deliverables"]}')

    return contract

# Purchase workshop book
await purchase_book('workshop')
```

## Key Takeaways

1. **Conditional Logic**: Smart402 supports free and paid tiers
2. **Testnet First**: Always test on testnet before mainnet
3. **Real Transactions**: Deployed to actual blockchain (Mumbai)
4. **Automatic Fulfillment**: Instant delivery after payment
5. **Block Explorer**: Full transparency with transaction links

## Related Examples

- **[SaaS Subscription](Example-SaaS-Subscription)** - Recurring payments
- **[Freelancer Escrow](Example-Freelancer-Escrow)** - Milestone-based
- **[API Monetization](Example-API-Monetization)** - Pay-per-use

---

[← Examples](Examples) | [Next Example →](Example-SaaS-Subscription)
