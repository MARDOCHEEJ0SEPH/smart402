//! Type definitions for Smart402 SDK

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContractConfig {
    #[serde(rename = "type")]
    pub contract_type: String,
    pub parties: Vec<String>,
    pub payment: PaymentConfig,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub conditions: Option<Vec<ConditionConfig>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metadata: Option<HashMap<String, serde_json::Value>>,
}

impl Default for ContractConfig {
    fn default() -> Self {
        Self {
            contract_type: String::new(),
            parties: Vec::new(),
            payment: PaymentConfig::default(),
            conditions: None,
            metadata: None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct PaymentConfig {
    pub amount: f64,
    pub token: String,
    pub frequency: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub blockchain: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub day_of_month: Option<u8>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConditionConfig {
    pub id: String,
    pub description: String,
    pub source: String,
    pub operator: String,
    pub threshold: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UCLContract {
    pub contract_id: String,
    pub version: String,
    pub standard: String,
    pub summary: ContractSummary,
    pub metadata: ContractMetadata,
    pub payment: PaymentTerms,
    pub conditions: Conditions,
    pub oracles: Vec<OracleDefinition>,
    pub rules: Vec<RuleDefinition>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContractSummary {
    pub title: String,
    pub plain_english: String,
    pub what_it_does: String,
    pub who_its_for: String,
    pub when_it_executes: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContractMetadata {
    #[serde(rename = "type")]
    pub contract_type: String,
    pub category: String,
    pub parties: Vec<PartyInfo>,
    pub dates: DateInfo,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PartyInfo {
    pub role: String,
    pub identifier: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub name: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DateInfo {
    pub effective: String,
    pub duration: String,
    pub renewal: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PaymentTerms {
    pub structure: String,
    pub amount: f64,
    pub currency: String,
    pub token: String,
    pub blockchain: String,
    pub frequency: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Conditions {
    pub required: Vec<ConditionDefinition>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub optional: Option<Vec<ConditionDefinition>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConditionDefinition {
    pub id: String,
    pub description: String,
    pub source: String,
    pub operator: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub threshold: Option<serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OracleDefinition {
    pub id: String,
    #[serde(rename = "type")]
    pub oracle_type: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub endpoint: Option<String>,
    pub refresh_rate: String,
    pub required: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RuleDefinition {
    pub rule_id: String,
    pub name: String,
    pub trigger: String,
    pub conditions: RuleConditions,
    pub actions: Vec<ActionDefinition>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RuleConditions {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub all_of: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub any_of: Option<Vec<String>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ActionDefinition {
    pub action: String,
    #[serde(flatten)]
    pub params: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeployResult {
    pub success: bool,
    pub address: String,
    pub transaction_hash: String,
    pub network: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub block_number: Option<u64>,
    pub contract_id: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PaymentResult {
    pub success: bool,
    pub transaction_hash: String,
    pub amount: f64,
    pub token: String,
    pub network: String,
    pub from: String,
    pub to: String,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ContractStatus {
    Draft,
    Deploying,
    Deployed,
    Active,
    Paused,
    Completed,
    Failed,
}

impl std::fmt::Display for ContractStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ContractStatus::Draft => write!(f, "draft"),
            ContractStatus::Deploying => write!(f, "deploying"),
            ContractStatus::Deployed => write!(f, "deployed"),
            ContractStatus::Active => write!(f, "active"),
            ContractStatus::Paused => write!(f, "paused"),
            ContractStatus::Completed => write!(f, "completed"),
            ContractStatus::Failed => write!(f, "failed"),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConditionCheckResult {
    pub all_met: bool,
    pub conditions: HashMap<String, bool>,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}
