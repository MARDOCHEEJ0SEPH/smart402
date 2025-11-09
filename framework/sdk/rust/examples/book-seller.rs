//! Book Seller Smart Contract Example
//!
//! This example demonstrates:
//! - Free book option (digital download)
//! - Paid workshop book ($10 USDC)
//! - Conditional payment based on book type
//! - Deployment to EVM testnet (Polygon Mumbai)
//! - Automatic fulfillment after payment

use smart402::{
    Smart402, ContractConfig, PaymentConfig, AEOEngine, LLMOEngine, X402Client,
};
use colored::Colorize;
use std::collections::HashMap;
use std::error::Error;

/// Book types available
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

    fn description(&self) -> &str {
        match self {
            BookType::FreeEbook => "A comprehensive introduction to Smart402 framework (PDF format)",
            BookType::WorkshopBook => "Complete workshop materials with hands-on exercises, video tutorials, and source code",
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
async fn main() -> Result<(), Box<dyn Error>> {
    println!("{}", "\n📚 Smart402 Book Seller Example\n".blue().bold());
    println!("{}", "Welcome to the Smart402 Bookstore!".cyan());
    println!("{}", "━".repeat(60).blue());

    // Display available books
    display_catalog();

    // Simulate user selecting workshop book
    let selected_book = BookType::WorkshopBook;
    println!("\n{}", format!("✓ Selected: {}", selected_book.name()).green());
    println!("{}", format!("  {}", selected_book.description()).white());
    println!();

    // Create book purchase contract
    let contract = create_book_contract(&selected_book).await?;

    // Display contract details
    display_contract_info(&contract, &selected_book)?;

    // Check AEO score for AI discoverability
    check_aeo_score(&contract)?;

    // Validate contract
    validate_contract(&contract)?;

    // Deploy to testnet
    let deploy_result = deploy_to_testnet(contract).await?;

    // Process payment and fulfillment
    process_purchase(&deploy_result, &selected_book).await?;

    println!("{}", "\n✨ Book purchase completed successfully!\n".green().bold());
    println!("{}", "Thank you for your purchase!".cyan());
    println!();

    Ok(())
}

/// Display book catalog
fn display_catalog() {
    println!("\n{}", "📖 Available Books:".yellow().bold());
    println!();

    // Free eBook
    let free_book = BookType::FreeEbook;
    println!("{}", "1. Free Option:".cyan().bold());
    println!("   {}", free_book.name().white());
    println!("   {}", free_book.description().white());
    println!("   {}", format!("Price: ${} (FREE)", free_book.price()).green().bold());
    println!("   Includes:");
    for item in free_book.deliverables() {
        println!("   {} {}", "✓".green(), item.white());
    }
    println!();

    // Workshop Book
    let workshop_book = BookType::WorkshopBook;
    println!("{}", "2. Premium Option:".cyan().bold());
    println!("   {}", workshop_book.name().white());
    println!("   {}", workshop_book.description().white());
    println!("   {}", format!("Price: ${} USDC", workshop_book.price()).yellow().bold());
    println!("   Includes:");
    for item in workshop_book.deliverables() {
        println!("   {} {}", "✓".green(), item.white());
    }
    println!();
}

/// Create book purchase contract
async fn create_book_contract(book: &BookType) -> Result<smart402::Contract, Box<dyn Error>> {
    println!("{}", "📝 Creating purchase contract...".yellow());

    let is_free = matches!(book, BookType::FreeEbook);

    let config = ContractConfig {
        contract_type: "digital-product-purchase".to_string(),
        parties: vec![
            "bookstore@smart402.io".to_string(),
            "customer@example.com".to_string(),
        ],
        payment: PaymentConfig {
            amount: book.price(),
            token: if is_free { "NONE".to_string() } else { "USDC".to_string() },
            blockchain: "polygon-mumbai".to_string(), // Testnet
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
            serde_json::json!({
                "id": "terms_accepted",
                "type": "verification",
                "description": "Terms of service accepted",
                "required": true,
            }),
        ]),
        metadata: Some(serde_json::json!({
            "title": book.name(),
            "description": book.description(),
            "category": "digital-product",
            "product_type": "book",
            "format": "digital",
            "instant_delivery": true,
            "deliverables": book.deliverables(),
            "license": "single-user",
        })),
    };

    let contract = Smart402::create(config).await?;

    println!("{}", format!("   ✓ Contract created: {}", contract.ucl.contract_id).green());
    println!();

    Ok(contract)
}

/// Display contract information
fn display_contract_info(contract: &smart402::Contract, book: &BookType) -> Result<(), Box<dyn Error>> {
    println!("{}", "📋 Contract Details:".yellow().bold());
    println!();

    println!("{}", "  Basic Information:".cyan());
    println!("    Contract ID: {}", contract.ucl.contract_id.white());
    println!("    Product: {}", book.name().white());
    println!("    Price: {}", format!("${} {}",
        contract.ucl.payment.amount,
        contract.ucl.payment.token
    ).yellow());
    println!("    Network: {}", contract.ucl.payment.blockchain.white());
    println!();

    println!("{}", "  What You'll Receive:".cyan());
    for (i, deliverable) in book.deliverables().iter().enumerate() {
        println!("    {}. {}", i + 1, deliverable.white());
    }
    println!();

    println!("{}", "  Contract Conditions:".cyan());
    for condition in &contract.ucl.conditions.required {
        let required_badge = if condition.required {
            "[REQUIRED]".red()
        } else {
            "[OPTIONAL]".yellow()
        };
        println!("    {} {}", required_badge, condition.description.white());
    }
    println!();

    Ok(())
}

/// Check AEO score for AI discoverability
fn check_aeo_score(contract: &smart402::Contract) -> Result<(), Box<dyn Error>> {
    println!("{}", "🤖 AI Discoverability Check (AEO):".yellow().bold());
    println!();

    let aeo = AEOEngine::new();
    let score = aeo.calculate_score(&contract.ucl)?;

    println!("{}", format!("  Overall Score: {:.1}%", score.total * 100.0).cyan().bold());
    println!("    {} Semantic Richness: {:.1}%", "•".white(), score.semantic_richness * 100.0);
    println!("    {} Citation Friendliness: {:.1}%", "•".white(), score.citation_friendliness * 100.0);
    println!("    {} Findability: {:.1}%", "•".white(), score.findability * 100.0);
    println!("    {} Authority Signals: {:.1}%", "•".white(), score.authority_signals * 100.0);
    println!();

    if score.total > 0.7 {
        println!("{}", "  ✓ Excellent! This contract is highly discoverable by AI systems".green());
    } else if score.total > 0.5 {
        println!("{}", "  ⚠ Good, but could be improved for better AI discovery".yellow());
    } else {
        println!("{}", "  ⚠ Consider adding more metadata for better AI discovery".red());
    }
    println!();

    // Generate JSON-LD for search engines
    let jsonld = aeo.generate_jsonld(&contract.ucl)?;
    println!("{}", "  JSON-LD Markup Generated:".cyan());
    println!("{}", format!("  ({}  bytes for SEO)", jsonld.len()).white());
    println!();

    Ok(())
}

/// Validate contract
fn validate_contract(contract: &smart402::Contract) -> Result<(), Box<dyn Error>> {
    println!("{}", "✅ Validating Contract:".yellow().bold());
    println!();

    let llmo = LLMOEngine::new();
    let validation = llmo.validate(&contract.ucl)?;

    if validation.valid {
        println!("{}", "  ✓ Contract is valid and ready for deployment".green().bold());
    } else {
        println!("{}", "  ✗ Validation errors found:".red().bold());
        for error in &validation.errors {
            println!("    {} {}", "•".red(), error);
        }
    }

    if !validation.warnings.is_empty() {
        println!();
        println!("{}", "  Warnings:".yellow());
        for warning in &validation.warnings {
            println!("    {} {}", "⚠".yellow(), warning);
        }
    }
    println!();

    // Generate human-readable explanation
    println!("{}", "📄 Contract Explanation:".yellow().bold());
    println!();
    let explanation = llmo.explain(&contract.ucl)?;
    println!("{}", explanation.white());
    println!();

    Ok(())
}

/// Deploy contract to testnet
async fn deploy_to_testnet(mut contract: smart402::Contract) -> Result<DeployedContract, Box<dyn Error>> {
    println!("{}", "🚀 Deploying to Polygon Mumbai Testnet:".yellow().bold());
    println!();

    println!("{}", "  Preparing deployment...".white());
    println!("    Network: {}", "Polygon Mumbai (Testnet)".cyan());
    println!("    Chain ID: {}", "80001".cyan());
    println!("    Currency: {}", "MATIC (testnet)".cyan());
    println!();

    // Simulate deployment process
    println!("{}", "  ⏳ Compiling contract to Solidity...".white());
    let llmo = LLMOEngine::new();
    let solidity_code = llmo.compile(&contract.ucl, "solidity")?;
    println!("{}", format!("     ✓ Generated {} bytes of Solidity code", solidity_code.len()).green());

    println!("{}", "  ⏳ Deploying to blockchain...".white());
    let result = contract.deploy("polygon-mumbai").await?;

    println!("{}", "  ✓ Deployment successful!".green().bold());
    println!();

    println!("{}", "  Deployment Details:".cyan().bold());
    println!("    Contract Address: {}", result.address.white());
    println!("    Transaction Hash: {}", result.transaction_hash.white());
    println!("    Network: {}", result.network.white());
    if let Some(block) = result.block_number {
        println!("    Block Number: {}", block.to_string().white());
    }
    println!("    Gas Used: {}", "~150,000 gas".white());
    println!();

    // Display testnet explorer links
    println!("{}", "  📊 View on Block Explorer:".cyan());
    println!("    Contract: {}",
        format!("https://mumbai.polygonscan.com/address/{}", result.address).blue().underline());
    println!("    Transaction: {}",
        format!("https://mumbai.polygonscan.com/tx/{}", result.transaction_hash).blue().underline());
    println!();

    Ok(DeployedContract {
        contract,
        address: result.address,
        transaction_hash: result.transaction_hash,
        network: result.network,
    })
}

/// Process purchase and fulfillment
async fn process_purchase(
    deployed: &DeployedContract,
    book: &BookType,
) -> Result<(), Box<dyn Error>> {
    let is_free = matches!(book, BookType::FreeEbook);

    if !is_free {
        // Process payment for workshop book
        println!("{}", "💳 Processing Payment:".yellow().bold());
        println!();

        println!("{}", "  Checking payment conditions...".white());
        let conditions = deployed.contract.check_conditions().await?;

        if conditions.all_met {
            println!("{}", "  ✓ All conditions met".green());
        } else {
            println!("{}", "  Waiting for payment confirmation...".yellow());
        }
        println!();

        println!("{}", "  Payment Details:".cyan());
        println!("    Amount: {}", format!("${} USDC", book.price()).yellow().bold());
        println!("    Network: {}", "Polygon Mumbai".white());
        println!("    Recipient: {}", deployed.address.white());
        println!();

        // Generate X402 payment headers
        println!("{}", "  Generating X402 Payment Headers:".cyan());
        let x402 = X402Client::new(
            "https://x402.smart402.io".to_string()
        );
        let headers = x402.generate_headers(&deployed.contract.ucl, true)?;

        println!("    X402-Contract-ID: {}", headers.contract_id.white());
        println!("    X402-Payment-Amount: {}", headers.payment_amount.white());
        println!("    X402-Payment-Token: {}", headers.payment_token.white());
        println!("    X402-Settlement-Network: {}", headers.settlement_network.white());
        println!();

        // Execute payment
        println!("{}", "  ⏳ Executing payment transaction...".white());
        let payment_result = deployed.contract.execute_payment().await?;

        println!("{}", "  ✓ Payment executed successfully!".green().bold());
        println!();
        println!("{}", "  Payment Receipt:".cyan());
        println!("    Transaction: {}", payment_result.transaction_hash.white());
        println!("    Amount: {} {}", payment_result.amount, payment_result.token);
        println!("    From: {}", payment_result.from.white());
        println!("    To: {}", payment_result.to.white());
        println!("    Status: {}", "Confirmed".green().bold());
        println!();

        println!("{}", "  🔗 View Transaction:".cyan());
        println!("    {}",
            format!("https://mumbai.polygonscan.com/tx/{}", payment_result.transaction_hash)
                .blue().underline());
        println!();
    } else {
        println!("{}", "🎁 Free Book - No Payment Required".green().bold());
        println!();
    }

    // Automatic fulfillment
    println!("{}", "📦 Fulfillment:".yellow().bold());
    println!();
    println!("{}", "  ✓ Payment verified".green());
    println!("{}", "  ✓ Generating download links...".green());
    println!("{}", "  ✓ Preparing materials...".green());
    println!();

    println!("{}", "  Your Books & Materials:".cyan().bold());
    for (i, deliverable) in book.deliverables().iter().enumerate() {
        println!("    {}. {} - {}",
            i + 1,
            deliverable.white(),
            "Ready to download".green()
        );

        // Generate mock download link
        let link = format!(
            "https://downloads.smart402.io/{}/{}",
            deployed.contract.ucl.contract_id,
            deliverable.replace(" ", "-").to_lowercase()
        );
        println!("       {}", link.blue().underline());
    }
    println!();

    // Send confirmation email (simulated)
    println!("{}", "  📧 Confirmation email sent to: customer@example.com".cyan());
    println!("{}", "  💾 Access granted to customer portal".cyan());
    println!();

    // Contract summary
    println!("{}", "━".repeat(60).blue());
    println!();
    println!("{}", "📊 Purchase Summary:".yellow().bold());
    println!();
    println!("  Product: {}", book.name().white());
    println!("  Price: {}",
        if is_free {
            "FREE".green().bold().to_string()
        } else {
            format!("${} USDC", book.price()).yellow().to_string()
        }
    );
    println!("  Contract: {}", deployed.address.white());
    println!("  Network: {}", deployed.network.white());
    println!("  Status: {}", "Completed".green().bold());
    println!("  Items Delivered: {}", book.deliverables().len().to_string().cyan());
    println!();

    Ok(())
}

/// Deployed contract info
struct DeployedContract {
    contract: smart402::Contract,
    address: String,
    transaction_hash: String,
    network: String,
}
