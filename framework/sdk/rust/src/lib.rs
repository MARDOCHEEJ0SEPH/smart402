//! # Smart402 Rust SDK
//!
//! Universal Protocol for AI-Native Smart Contracts
//!
//! ## Quick Start
//!
//! ```no_run
//! use smart402::{Smart402, ContractConfig, PaymentConfig};
//!
//! #[tokio::main]
//! async fn main() -> Result<(), Box<dyn std::error::Error>> {
//!     let contract = Smart402::create(ContractConfig {
//!         contract_type: "saas-subscription".to_string(),
//!         parties: vec!["vendor@example.com".to_string(), "customer@example.com".to_string()],
//!         payment: PaymentConfig {
//!             amount: 99.0,
//!             frequency: "monthly".to_string(),
//!             token: "USDC".to_string(),
//!             ..Default::default()
//!         },
//!         ..Default::default()
//!     }).await?;
//!
//!     contract.deploy("polygon").await?;
//!     contract.start_monitoring("hourly", None).await?;
//!
//!     println!("Contract deployed: {}", contract.address().unwrap());
//!     Ok(())
//! }
//! ```

pub mod core;
pub mod aeo;
pub mod llmo;
pub mod x402;
pub mod utils;
pub mod error;
pub mod types;

// Re-exports for convenience
pub use core::smart402::Smart402;
pub use core::contract::Contract;
pub use aeo::{AEOEngine, engine::AEOScore};
pub use llmo::{LLMOEngine, engine::ValidationResult};
pub use x402::{X402Client, client::{X402Headers, PaymentResponse}};
pub use types::*;
pub use error::{Error, Result};

/// SDK version
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_version() {
        assert!(!VERSION.is_empty());
    }
}
