//! Utility functions

use crate::{Result, UCLContract};
use std::fs;
use std::path::Path;

/// Export contract to YAML
pub fn export_yaml(ucl: &UCLContract) -> Result<String> {
    Ok(serde_yaml::to_string(ucl)?)
}

/// Export contract to JSON
pub fn export_json(ucl: &UCLContract) -> Result<String> {
    Ok(serde_json::to_string_pretty(ucl)?)
}

/// Save contract to file
pub fn save_contract(ucl: &UCLContract, path: &Path, format: &str) -> Result<()> {
    let content = match format {
        "yaml" | "yml" => export_yaml(ucl)?,
        "json" => export_json(ucl)?,
        _ => return Err(crate::Error::ValidationError(format!("Unsupported format: {}", format))),
    };

    fs::write(path, content)?;
    Ok(())
}

/// Load contract from file
pub fn load_contract(path: &Path) -> Result<UCLContract> {
    let content = fs::read_to_string(path)?;

    // Try YAML first, then JSON
    if let Ok(ucl) = serde_yaml::from_str::<UCLContract>(&content) {
        return Ok(ucl);
    }

    if let Ok(ucl) = serde_json::from_str::<UCLContract>(&content) {
        return Ok(ucl);
    }

    Err(crate::Error::ValidationError("Could not parse contract file".to_string()))
}

/// Generate contract ID
pub fn generate_contract_id(contract_type: &str) -> String {
    use std::time::{SystemTime, UNIX_EPOCH};
    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs();
    format!("smart402:{}:{:x}", contract_type, timestamp)
}
