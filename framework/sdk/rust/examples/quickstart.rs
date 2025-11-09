//! Smart402 Quickstart Example
//!
//! This example demonstrates the complete workflow:
//! 1. Creating a contract
//! 2. Deploying to blockchain
//! 3. Monitoring and auto-execution

use smart402::{Smart402, ContractConfig, PaymentConfig};
use std::error::Error;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    println!("🚀 Smart402 Quickstart Example\n");

    // Step 1: Create Contract
    println!("1️⃣  Creating SaaS subscription contract...");

    let config = ContractConfig {
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
    };

    let mut contract = Smart402::create(config).await?;
    println!("   ✓ Contract created: {}", contract.ucl.contract_id);
    println!("   ✓ Summary: {}\n", contract.get_summary());

    // Step 2: Get AEO Score
    println!("2️⃣  Calculating AEO Score...");
    use smart402::AEOEngine;
    let aeo = AEOEngine::new();
    let score = aeo.calculate_score(&contract.ucl)?;
    println!("   ✓ AEO Score: {:.2}/1.0", score.total);
    println!("     - Semantic Richness: {:.2}", score.semantic_richness);
    println!("     - Citation Friendliness: {:.2}", score.citation_friendliness);
    println!("     - Findability: {:.2}\n", score.findability);

    // Step 3: Validate Contract
    println!("3️⃣  Validating contract...");
    use smart402::LLMOEngine;
    let llmo = LLMOEngine::new();
    let validation = llmo.validate(&contract.ucl)?;
    if validation.valid {
        println!("   ✓ Contract is valid");
    } else {
        println!("   ✗ Validation errors: {:?}", validation.errors);
    }
    if !validation.warnings.is_empty() {
        println!("   ⚠ Warnings: {:?}", validation.warnings);
    }
    println!();

    // Step 4: Generate Explanation
    println!("4️⃣  Generating plain-English explanation...");
    let explanation = llmo.explain(&contract.ucl)?;
    println!("{}\n", explanation);

    // Step 5: Compile to Target Languages
    println!("5️⃣  Compiling to target languages...");

    let solidity = llmo.compile(&contract.ucl, "solidity")?;
    println!("   ✓ Solidity code generated ({} bytes)", solidity.len());

    let javascript = llmo.compile(&contract.ucl, "javascript")?;
    println!("   ✓ JavaScript code generated ({} bytes)", javascript.len());

    let rust = llmo.compile(&contract.ucl, "rust")?;
    println!("   ✓ Rust code generated ({} bytes)\n", rust.len());

    // Step 6: Deploy Contract
    println!("6️⃣  Deploying to Polygon...");
    let deploy_result = contract.deploy("polygon").await?;
    println!("   ✓ Contract deployed!");
    println!("     - Address: {}", deploy_result.address);
    println!("     - Transaction: {}", deploy_result.transaction_hash);
    println!("     - Network: {}", deploy_result.network);
    if let Some(block) = deploy_result.block_number {
        println!("     - Block: {}", block);
    }
    println!();

    // Step 7: Generate X402 Headers
    println!("7️⃣  Generating X402 payment headers...");
    use smart402::X402Client;
    let x402 = X402Client::new("https://api.smart402.io".to_string());
    let headers = x402.generate_headers(&contract.ucl, true)?;
    println!("   ✓ X402 headers generated:");
    println!("     - X402-Contract-ID: {}", headers.contract_id);
    println!("     - X402-Payment-Amount: {}", headers.payment_amount);
    println!("     - X402-Payment-Token: {}", headers.payment_token);
    println!("     - X402-Conditions-Met: {}\n", headers.conditions_met);

    // Step 8: Check Conditions
    println!("8️⃣  Checking contract conditions...");
    let conditions = contract.check_conditions().await?;
    println!("   ✓ Conditions checked:");
    println!("     - All Met: {}", conditions.all_met);
    println!("     - Timestamp: {}\n", conditions.timestamp);

    // Step 9: Execute Payment
    if conditions.all_met {
        println!("9️⃣  Executing payment...");
        let payment_result = contract.execute_payment().await?;
        println!("   ✓ Payment executed!");
        println!("     - Success: {}", payment_result.success);
        println!("     - Transaction: {}", payment_result.transaction_hash);
        println!("     - Amount: {}", payment_result.amount);
        println!("     - Token: {}", payment_result.token);
        println!("     - From: {}", payment_result.from);
        println!("     - To: {}\n", payment_result.to);
    }

    // Step 10: Export Contract
    println!("🔟 Exporting contract...");
    use smart402::utils;
    use std::path::Path;

    utils::save_contract(&contract.ucl, Path::new("contract.yaml"), "yaml")?;
    println!("   ✓ Contract saved to contract.yaml");

    let json = utils::export_json(&contract.ucl)?;
    println!("   ✓ JSON export generated ({} bytes)", json.len());

    println!("\n✨ Quickstart complete! All systems operational.");
    println!("\nNext steps:");
    println!("  • Start monitoring: smart402 monitor contract.yaml");
    println!("  • Check status: smart402 status {}", contract.ucl.contract_id);
    println!("  • View templates: smart402 templates");

    Ok(())
}
