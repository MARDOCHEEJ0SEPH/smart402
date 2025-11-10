//! Smart402 Rust SDK Integration Tests
//!
//! Comprehensive test suite for Smart402 Rust SDK functionality

use smart402::{
    Smart402, Contract, ContractConfig, PaymentConfig,
    AEOEngine, LLMOEngine, X402Client, Error, Result,
};

#[tokio::test]
async fn test_create_basic_contract() -> Result<()> {
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

    assert!(contract.ucl.contract_id.contains("smart402:"));
    assert_eq!(contract.ucl.payment.amount, 99.0);
    assert_eq!(contract.ucl.payment.token, "USDC");
    assert_eq!(contract.ucl.metadata.parties.len(), 2);

    Ok(())
}

#[tokio::test]
async fn test_create_from_template() -> Result<()> {
    let mut variables = std::collections::HashMap::new();
    variables.insert("vendor_email".to_string(), serde_json::json!("vendor@test.com"));
    variables.insert("customer_email".to_string(), serde_json::json!("customer@test.com"));
    variables.insert("amount".to_string(), serde_json::json!(49.0));

    let contract = Smart402::from_template("saas-subscription".to_string(), variables).await?;

    assert_eq!(contract.ucl.payment.amount, 49.0);

    Ok(())
}

#[tokio::test]
async fn test_unique_contract_ids() -> Result<()> {
    let config = ContractConfig {
        contract_type: "test".to_string(),
        parties: vec!["a@test.com".to_string(), "b@test.com".to_string()],
        payment: PaymentConfig {
            amount: 10.0,
            token: "USDC".to_string(),
            blockchain: "polygon".to_string(),
            frequency: "monthly".to_string(),
        },
        conditions: None,
        metadata: None,
    };

    let contract1 = Smart402::create(config.clone()).await?;
    let contract2 = Smart402::create(config).await?;

    assert_ne!(contract1.ucl.contract_id, contract2.ucl.contract_id);

    Ok(())
}

#[tokio::test]
async fn test_calculate_aeo_score() -> Result<()> {
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
        metadata: Some(serde_json::json!({
            "title": "Monthly SaaS Subscription",
            "description": "Automated monthly payment for software service",
            "category": "saas"
        })),
    }).await?;

    let aeo = AEOEngine::new();
    let score = aeo.calculate_score(&contract.ucl)?;

    assert!(score.total >= 0.0 && score.total <= 1.0);
    assert!(score.semantic_richness >= 0.0 && score.semantic_richness <= 1.0);
    assert!(score.citation_friendliness >= 0.0 && score.citation_friendliness <= 1.0);
    assert!(score.findability >= 0.0 && score.findability <= 1.0);

    Ok(())
}

#[tokio::test]
async fn test_generate_jsonld() -> Result<()> {
    let contract = Smart402::create(ContractConfig {
        contract_type: "saas-subscription".to_string(),
        parties: vec!["vendor@example.com".to_string(), "customer@example.com".to_string()],
        payment: PaymentConfig {
            amount: 99.0,
            token: "USDC".to_string(),
            blockchain: "polygon".to_string(),
            frequency: "monthly".to_string(),
        },
        conditions: None,
        metadata: None,
    }).await?;

    let aeo = AEOEngine::new();
    let jsonld = aeo.generate_jsonld(&contract.ucl)?;

    assert!(jsonld.contains("@context"));
    assert!(jsonld.contains("https://schema.org/"));
    assert!(jsonld.contains("SmartContract"));
    assert!(jsonld.contains(&contract.ucl.contract_id));

    Ok(())
}

#[tokio::test]
async fn test_validate_contract() -> Result<()> {
    let contract = Smart402::create(ContractConfig {
        contract_type: "saas-subscription".to_string(),
        parties: vec!["vendor@example.com".to_string(), "customer@example.com".to_string()],
        payment: PaymentConfig {
            amount: 99.0,
            token: "USDC".to_string(),
            blockchain: "polygon".to_string(),
            frequency: "monthly".to_string(),
        },
        conditions: None,
        metadata: None,
    }).await?;

    let llmo = LLMOEngine::new();
    let validation = llmo.validate(&contract.ucl)?;

    assert!(validation.valid);
    assert!(validation.errors.is_empty());

    Ok(())
}

#[tokio::test]
async fn test_generate_explanation() -> Result<()> {
    let contract = Smart402::create(ContractConfig {
        contract_type: "saas-subscription".to_string(),
        parties: vec!["vendor@example.com".to_string(), "customer@example.com".to_string()],
        payment: PaymentConfig {
            amount: 99.0,
            token: "USDC".to_string(),
            blockchain: "polygon".to_string(),
            frequency: "monthly".to_string(),
        },
        conditions: None,
        metadata: None,
    }).await?;

    let llmo = LLMOEngine::new();
    let explanation = llmo.explain(&contract.ucl)?;

    assert!(!explanation.is_empty());
    assert!(explanation.to_lowercase().contains("contract"));
    assert!(explanation.to_lowercase().contains("payment"));

    Ok(())
}

#[tokio::test]
async fn test_compile_to_solidity() -> Result<()> {
    let contract = Smart402::create(ContractConfig {
        contract_type: "saas-subscription".to_string(),
        parties: vec!["vendor@example.com".to_string(), "customer@example.com".to_string()],
        payment: PaymentConfig {
            amount: 99.0,
            token: "USDC".to_string(),
            blockchain: "polygon".to_string(),
            frequency: "monthly".to_string(),
        },
        conditions: None,
        metadata: None,
    }).await?;

    let llmo = LLMOEngine::new();
    let solidity = llmo.compile(&contract.ucl, "solidity")?;

    assert!(solidity.contains("pragma solidity"));
    assert!(solidity.contains("contract"));
    assert!(solidity.contains("function"));

    Ok(())
}

#[tokio::test]
async fn test_compile_to_javascript() -> Result<()> {
    let contract = Smart402::create(ContractConfig {
        contract_type: "saas-subscription".to_string(),
        parties: vec!["vendor@example.com".to_string(), "customer@example.com".to_string()],
        payment: PaymentConfig {
            amount: 99.0,
            token: "USDC".to_string(),
            blockchain: "polygon".to_string(),
            frequency: "monthly".to_string(),
        },
        conditions: None,
        metadata: None,
    }).await?;

    let llmo = LLMOEngine::new();
    let javascript = llmo.compile(&contract.ucl, "javascript")?;

    assert!(javascript.contains("class"));
    assert!(javascript.contains("async"));
    assert!(javascript.contains("executePayment"));

    Ok(())
}

#[tokio::test]
async fn test_compile_to_rust() -> Result<()> {
    let contract = Smart402::create(ContractConfig {
        contract_type: "saas-subscription".to_string(),
        parties: vec!["vendor@example.com".to_string(), "customer@example.com".to_string()],
        payment: PaymentConfig {
            amount: 99.0,
            token: "USDC".to_string(),
            blockchain: "polygon".to_string(),
            frequency: "monthly".to_string(),
        },
        conditions: None,
        metadata: None,
    }).await?;

    let llmo = LLMOEngine::new();
    let rust = llmo.compile(&contract.ucl, "rust")?;

    assert!(rust.contains("pub struct"));
    assert!(rust.contains("impl"));
    assert!(rust.contains("execute_payment"));

    Ok(())
}

#[tokio::test]
async fn test_generate_x402_headers() -> Result<()> {
    let contract = Smart402::create(ContractConfig {
        contract_type: "api-payment".to_string(),
        parties: vec!["provider@api.com".to_string(), "consumer@client.com".to_string()],
        payment: PaymentConfig {
            amount: 0.10,
            token: "USDC".to_string(),
            blockchain: "polygon".to_string(),
            frequency: "per-request".to_string(),
        },
        conditions: None,
        metadata: None,
    }).await?;

    let x402 = X402Client::new("https://x402.smart402.io".to_string());
    let headers = x402.generate_headers(&contract.ucl, true)?;

    assert_eq!(headers.contract_id, contract.ucl.contract_id);
    assert_eq!(headers.payment_amount, "0.1");
    assert_eq!(headers.payment_token, "USDC");
    assert_eq!(headers.settlement_network, "polygon");
    assert!(!headers.signature.is_empty());
    assert!(!headers.nonce.is_empty());

    Ok(())
}

#[tokio::test]
async fn test_deploy_to_testnet() -> Result<()> {
    let mut contract = Smart402::create(ContractConfig {
        contract_type: "test".to_string(),
        parties: vec!["a@test.com".to_string(), "b@test.com".to_string()],
        payment: PaymentConfig {
            amount: 10.0,
            token: "USDC".to_string(),
            blockchain: "polygon-mumbai".to_string(),
            frequency: "one-time".to_string(),
        },
        conditions: None,
        metadata: None,
    }).await?;

    let result = contract.deploy("polygon-mumbai").await?;

    assert_eq!(result.network, "polygon-mumbai");
    assert!(result.address.starts_with("0x"));
    assert_eq!(result.address.len(), 42);
    assert!(result.transaction_hash.starts_with("0x"));

    Ok(())
}

#[tokio::test]
async fn test_check_conditions() -> Result<()> {
    let contract = Smart402::create(ContractConfig {
        contract_type: "saas-subscription".to_string(),
        parties: vec!["vendor@example.com".to_string(), "customer@example.com".to_string()],
        payment: PaymentConfig {
            amount: 99.0,
            token: "USDC".to_string(),
            blockchain: "polygon".to_string(),
            frequency: "monthly".to_string(),
        },
        conditions: Some(vec![serde_json::json!({
            "id": "uptime_check",
            "type": "api",
            "description": "Service uptime > 99%",
            "threshold": 0.99
        })]),
        metadata: None,
    }).await?;

    let result = contract.check_conditions().await?;

    assert!(result.timestamp > 0);

    Ok(())
}

#[tokio::test]
async fn test_execute_payment() -> Result<()> {
    let contract = Smart402::create(ContractConfig {
        contract_type: "test".to_string(),
        parties: vec!["a@test.com".to_string(), "b@test.com".to_string()],
        payment: PaymentConfig {
            amount: 99.0,
            token: "USDC".to_string(),
            blockchain: "polygon".to_string(),
            frequency: "monthly".to_string(),
        },
        conditions: None,
        metadata: None,
    }).await?;

    let result = contract.execute_payment().await?;

    assert!(result.success);
    assert!(result.transaction_hash.starts_with("0x"));
    assert_eq!(result.amount, 99.0);
    assert_eq!(result.token, "USDC");

    Ok(())
}

#[tokio::test]
async fn test_export_yaml() -> Result<()> {
    let contract = Smart402::create(ContractConfig {
        contract_type: "test".to_string(),
        parties: vec!["a@test.com".to_string(), "b@test.com".to_string()],
        payment: PaymentConfig {
            amount: 10.0,
            token: "USDC".to_string(),
            blockchain: "polygon".to_string(),
            frequency: "monthly".to_string(),
        },
        conditions: None,
        metadata: None,
    }).await?;

    let yaml = smart402::utils::export_yaml(&contract.ucl)?;

    assert!(yaml.contains("contract_id:"));
    assert!(yaml.contains("payment:"));
    assert!(yaml.contains("amount: 10"));

    Ok(())
}

#[tokio::test]
async fn test_export_json() -> Result<()> {
    let contract = Smart402::create(ContractConfig {
        contract_type: "test".to_string(),
        parties: vec!["a@test.com".to_string(), "b@test.com".to_string()],
        payment: PaymentConfig {
            amount: 10.0,
            token: "USDC".to_string(),
            blockchain: "polygon".to_string(),
            frequency: "monthly".to_string(),
        },
        conditions: None,
        metadata: None,
    }).await?;

    let json = smart402::utils::export_json(&contract.ucl)?;
    let parsed: serde_json::Value = serde_json::from_str(&json)?;

    assert!(parsed.get("contract_id").is_some());
    assert!(parsed.get("payment").is_some());
    assert_eq!(parsed["payment"]["amount"].as_f64().unwrap(), 10.0);

    Ok(())
}

#[tokio::test]
async fn test_list_templates() {
    let templates = Smart402::get_templates();

    assert!(!templates.is_empty());
    assert!(templates.len() > 0);
}

#[tokio::test]
async fn test_invalid_payment_amount() {
    let result = Smart402::create(ContractConfig {
        contract_type: "test".to_string(),
        parties: vec!["a@test.com".to_string(), "b@test.com".to_string()],
        payment: PaymentConfig {
            amount: -100.0,  // Invalid: negative amount
            token: "USDC".to_string(),
            blockchain: "polygon".to_string(),
            frequency: "monthly".to_string(),
        },
        conditions: None,
        metadata: None,
    }).await;

    assert!(result.is_err());
}

#[tokio::test]
async fn test_contract_summary() -> Result<()> {
    let contract = Smart402::create(ContractConfig {
        contract_type: "saas-subscription".to_string(),
        parties: vec!["vendor@example.com".to_string(), "customer@example.com".to_string()],
        payment: PaymentConfig {
            amount: 99.0,
            token: "USDC".to_string(),
            blockchain: "polygon".to_string(),
            frequency: "monthly".to_string(),
        },
        conditions: None,
        metadata: None,
    }).await?;

    let summary = contract.get_summary();

    assert!(summary.contains("99"));
    assert!(summary.contains("USDC"));
    assert!(summary.contains("monthly"));

    Ok(())
}

#[tokio::test]
async fn test_aeo_score_improvement_with_metadata() -> Result<()> {
    let basic_contract = Smart402::create(ContractConfig {
        contract_type: "test".to_string(),
        parties: vec!["a@test.com".to_string(), "b@test.com".to_string()],
        payment: PaymentConfig {
            amount: 10.0,
            token: "USDC".to_string(),
            blockchain: "polygon".to_string(),
            frequency: "monthly".to_string(),
        },
        conditions: None,
        metadata: None,
    }).await?;

    let rich_contract = Smart402::create(ContractConfig {
        contract_type: "test".to_string(),
        parties: vec!["a@test.com".to_string(), "b@test.com".to_string()],
        payment: PaymentConfig {
            amount: 10.0,
            token: "USDC".to_string(),
            blockchain: "polygon".to_string(),
            frequency: "monthly".to_string(),
        },
        conditions: None,
        metadata: Some(serde_json::json!({
            "title": "Comprehensive Test Contract",
            "description": "Detailed description with rich metadata",
            "category": "testing",
            "tags": ["test", "example", "smart402"]
        })),
    }).await?;

    let aeo = AEOEngine::new();
    let basic_score = aeo.calculate_score(&basic_contract.ucl)?;
    let rich_score = aeo.calculate_score(&rich_contract.ucl)?;

    assert!(rich_score.total >= basic_score.total);

    Ok(())
}

#[tokio::test]
async fn test_validation_errors() -> Result<()> {
    let invalid_contract = Smart402::create(ContractConfig {
        contract_type: "test".to_string(),
        parties: vec![],  // Invalid: no parties
        payment: PaymentConfig {
            amount: -10.0,  // Invalid: negative amount
            token: "USDC".to_string(),
            blockchain: "polygon".to_string(),
            frequency: "monthly".to_string(),
        },
        conditions: None,
        metadata: None,
    }).await?;

    let llmo = LLMOEngine::new();
    let validation = llmo.validate(&invalid_contract.ucl)?;

    assert!(!validation.valid);
    assert!(!validation.errors.is_empty());

    Ok(())
}

#[tokio::test]
async fn test_x402_unique_nonce() -> Result<()> {
    let contract = Smart402::create(ContractConfig {
        contract_type: "api-payment".to_string(),
        parties: vec!["provider@api.com".to_string(), "consumer@client.com".to_string()],
        payment: PaymentConfig {
            amount: 0.10,
            token: "USDC".to_string(),
            blockchain: "polygon".to_string(),
            frequency: "per-request".to_string(),
        },
        conditions: None,
        metadata: None,
    }).await?;

    let x402 = X402Client::new("https://x402.smart402.io".to_string());
    let headers1 = x402.generate_headers(&contract.ucl, true)?;

    // Sleep to ensure different timestamp
    tokio::time::sleep(tokio::time::Duration::from_millis(10)).await;

    let headers2 = x402.generate_headers(&contract.ucl, true)?;

    assert_ne!(headers1.nonce, headers2.nonce);

    Ok(())
}
