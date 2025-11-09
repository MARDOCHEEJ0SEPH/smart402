//! Smart402 CLI

use clap::{Parser, Subcommand};
use colored::Colorize;
use dialoguer::{Input, Select, Confirm};
use smart402::{ContractConfig, Smart402, PaymentConfig};
use std::path::PathBuf;

#[derive(Parser)]
#[command(name = "smart402")]
#[command(about = "Smart402 CLI - Universal Protocol for AI-Native Smart Contracts", long_about = None)]
#[command(version)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Create a new Smart402 contract
    Create {
        /// Output file path
        #[arg(short, long)]
        output: Option<PathBuf>,

        /// Use template
        #[arg(short, long)]
        template: Option<String>,
    },

    /// Deploy contract to blockchain
    Deploy {
        /// Contract file path
        contract: PathBuf,

        /// Network to deploy to
        #[arg(short, long, default_value = "polygon")]
        network: String,
    },

    /// Monitor contract and auto-execute
    Monitor {
        /// Contract file path
        contract: PathBuf,

        /// Check frequency (quick/medium/slow)
        #[arg(short, long, default_value = "medium")]
        frequency: String,

        /// Webhook URL for notifications
        #[arg(short, long)]
        webhook: Option<String>,
    },

    /// Check contract status
    Status {
        /// Contract ID
        contract_id: String,
    },

    /// List available templates
    Templates,

    /// Initialize Smart402 configuration
    Init,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Create { output, template } => {
            create_contract(output, template).await?;
        }
        Commands::Deploy { contract, network } => {
            deploy_contract(contract, network).await?;
        }
        Commands::Monitor { contract, frequency, webhook } => {
            monitor_contract(contract, frequency, webhook).await?;
        }
        Commands::Status { contract_id } => {
            check_status(contract_id).await?;
        }
        Commands::Templates => {
            list_templates().await?;
        }
        Commands::Init => {
            init_config().await?;
        }
    }

    Ok(())
}

async fn create_contract(output: Option<PathBuf>, template: Option<String>) -> anyhow::Result<()> {
    println!("{}", "\n🚀 Smart402 Contract Creator\n".blue().bold());

    let contract = if let Some(template_name) = template {
        // Use template
        println!("Creating from template: {}", template_name.green());
        let variables = std::collections::HashMap::new();
        Smart402::from_template(template_name, variables).await?
    } else {
        // Interactive creation
        let contract_type = Input::<String>::new()
            .with_prompt("Contract type (saas-subscription, freelancer, supply-chain, etc.)")
            .default("custom".to_string())
            .interact()?;

        let party1 = Input::<String>::new()
            .with_prompt("First party email")
            .interact()?;

        let party2 = Input::<String>::new()
            .with_prompt("Second party email")
            .interact()?;

        let amount = Input::<f64>::new()
            .with_prompt("Payment amount")
            .interact()?;

        let token = Input::<String>::new()
            .with_prompt("Payment token")
            .default("USDC".to_string())
            .interact()?;

        let blockchain = Input::<String>::new()
            .with_prompt("Blockchain network")
            .default("polygon".to_string())
            .interact()?;

        let frequency = Input::<String>::new()
            .with_prompt("Payment frequency")
            .default("monthly".to_string())
            .interact()?;

        let config = ContractConfig {
            contract_type,
            parties: vec![party1, party2],
            payment: PaymentConfig {
                amount,
                token,
                blockchain,
                frequency,
            },
            conditions: None,
            metadata: None,
        };

        Smart402::create(config).await?
    };

    // Save contract
    let output_path = output.unwrap_or_else(|| PathBuf::from("contract.yaml"));
    smart402::utils::save_contract(&contract.ucl, &output_path, "yaml")?;

    println!("\n{}", "✓ Contract created successfully!".green());
    println!("  File: {}", output_path.display().to_string().cyan());
    println!("  Contract ID: {}", contract.ucl.contract_id.cyan());

    println!("\n{}", contract.get_summary());

    Ok(())
}

async fn deploy_contract(contract_path: PathBuf, network: String) -> anyhow::Result<()> {
    println!("{}", "\n🚀 Deploying Smart402 Contract\n".blue().bold());

    // Load contract
    let ucl = smart402::utils::load_contract(&contract_path)?;
    let mut contract = Smart402::create(ContractConfig {
        contract_type: ucl.metadata.contract_type.clone(),
        parties: ucl.metadata.parties.clone(),
        payment: PaymentConfig {
            amount: ucl.payment.amount,
            token: ucl.payment.token.clone(),
            blockchain: ucl.payment.blockchain.clone(),
            frequency: ucl.payment.frequency.clone(),
        },
        conditions: None,
        metadata: None,
    }).await?;

    // Deploy
    let spinner = indicatif::ProgressBar::new_spinner();
    spinner.set_message(format!("Deploying to {}...", network));
    spinner.enable_steady_tick(std::time::Duration::from_millis(100));

    let result = contract.deploy(&network).await?;

    spinner.finish_with_message(format!("{}", "✓ Deployed!".green()));

    println!("\n{}", "Deployment Details:".bold());
    println!("  Contract Address: {}", result.address.cyan());
    println!("  Transaction Hash: {}", result.transaction_hash.cyan());
    println!("  Network: {}", result.network.cyan());
    if let Some(block) = result.block_number {
        println!("  Block Number: {}", block.to_string().cyan());
    }

    Ok(())
}

async fn monitor_contract(
    contract_path: PathBuf,
    frequency: String,
    webhook: Option<String>,
) -> anyhow::Result<()> {
    println!("{}", "\n👁️  Smart402 Contract Monitor\n".blue().bold());

    // Load contract
    let ucl = smart402::utils::load_contract(&contract_path)?;
    let contract = Smart402::create(ContractConfig {
        contract_type: ucl.metadata.contract_type.clone(),
        parties: ucl.metadata.parties.clone(),
        payment: PaymentConfig {
            amount: ucl.payment.amount,
            token: ucl.payment.token.clone(),
            blockchain: ucl.payment.blockchain.clone(),
            frequency: ucl.payment.frequency.clone(),
        },
        conditions: None,
        metadata: None,
    }).await?;

    println!("Starting monitoring...");
    println!("  Contract: {}", ucl.contract_id.cyan());
    println!("  Frequency: {}", frequency.cyan());
    if let Some(ref url) = webhook {
        println!("  Webhook: {}", url.cyan());
    }

    contract.start_monitoring(&frequency, webhook).await?;

    println!("\n{}", "✓ Monitoring started!".green());
    println!("  Contract will be monitored and executed automatically");
    println!("  Press Ctrl+C to stop");

    // Keep running
    tokio::signal::ctrl_c().await?;
    println!("\n{}", "Monitor stopped".yellow());

    Ok(())
}

async fn check_status(contract_id: String) -> anyhow::Result<()> {
    println!("{}", "\n📊 Contract Status\n".blue().bold());

    let contract = Smart402::load(contract_id.clone()).await?;

    println!("Contract ID: {}", contract_id.cyan());
    println!("Status: {:?}", contract.status());
    if let Some(address) = contract.address() {
        println!("Address: {}", address.cyan());
    }
    if let Some(tx) = contract.transaction_hash() {
        println!("Transaction: {}", tx.cyan());
    }

    Ok(())
}

async fn list_templates() -> anyhow::Result<()> {
    println!("{}", "\n📋 Available Templates\n".blue().bold());

    let templates = Smart402::get_templates();

    if templates.is_empty() {
        println!("No templates available yet.");
        return Ok(());
    }

    for template in templates {
        println!("  • {}", template.green());
    }

    println!("\n{}", "Usage:".bold());
    println!("  smart402 create --template <name>");

    Ok(())
}

async fn init_config() -> anyhow::Result<()> {
    println!("{}", "\n⚙️  Initialize Smart402 Configuration\n".blue().bold());

    let has_dotenv = Confirm::new()
        .with_prompt("Create .env file?")
        .default(true)
        .interact()?;

    if has_dotenv {
        let default_network = Input::<String>::new()
            .with_prompt("Default blockchain network")
            .default("polygon".to_string())
            .interact()?;

        let private_key_prompt = Input::<String>::new()
            .with_prompt("Private key (optional, for deployments)")
            .allow_empty(true)
            .interact()?;

        let env_content = format!(
            "# Smart402 Configuration\nDEFAULT_NETWORK={}\nPRIVATE_KEY={}\n",
            default_network,
            if private_key_prompt.is_empty() {
                "your_private_key_here"
            } else {
                &private_key_prompt
            }
        );

        std::fs::write(".env", env_content)?;
        println!("{}", "✓ .env file created".green());
    }

    println!("\n{}", "Configuration complete!".green().bold());
    println!("\nNext steps:");
    println!("  1. Create a contract: {}", "smart402 create".cyan());
    println!("  2. Deploy it: {}", "smart402 deploy contract.yaml".cyan());
    println!("  3. Monitor it: {}", "smart402 monitor contract.yaml".cyan());

    Ok(())
}
