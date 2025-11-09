//! AEO Engine for AI discoverability

use crate::{Result, UCLContract};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// AEO Score result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AEOScore {
    pub total: f64,
    pub semantic_richness: f64,
    pub citation_friendliness: f64,
    pub findability: f64,
    pub authority_signals: f64,
    pub citation_presence: f64,
}

/// AEO Engine
pub struct AEOEngine {
    weights: HashMap<String, f64>,
}

impl Default for AEOEngine {
    fn default() -> Self {
        let mut weights = HashMap::new();
        weights.insert("semantic_richness".to_string(), 0.25);
        weights.insert("citation_friendliness".to_string(), 0.20);
        weights.insert("findability".to_string(), 0.25);
        weights.insert("authority_signals".to_string(), 0.15);
        weights.insert("citation_presence".to_string(), 0.15);

        Self { weights }
    }
}

impl AEOEngine {
    /// Create new AEO engine
    pub fn new() -> Self {
        Self::default()
    }

    /// Calculate AEO score for contract
    pub fn calculate_score(&self, ucl: &UCLContract) -> Result<AEOScore> {
        let semantic_richness = self.calculate_semantic_richness(ucl);
        let citation_friendliness = self.calculate_citation_friendliness(ucl);
        let findability = self.calculate_findability(ucl);
        let authority_signals = self.calculate_authority_signals(ucl);
        let citation_presence = self.calculate_citation_presence(ucl);

        let total = semantic_richness * self.weights["semantic_richness"]
            + citation_friendliness * self.weights["citation_friendliness"]
            + findability * self.weights["findability"]
            + authority_signals * self.weights["authority_signals"]
            + citation_presence * self.weights["citation_presence"];

        Ok(AEOScore {
            total,
            semantic_richness,
            citation_friendliness,
            findability,
            authority_signals,
            citation_presence,
        })
    }

    /// Generate JSON-LD markup
    pub fn generate_jsonld(&self, ucl: &UCLContract) -> Result<String> {
        let jsonld = serde_json::json!({
            "@context": "https://schema.org/",
            "@type": "SmartContract",
            "identifier": ucl.contract_id,
            "name": ucl.summary.title,
            "description": ucl.summary.plain_english,
            "version": ucl.version,
            "contractType": ucl.metadata.contract_type,
            "category": ucl.metadata.category,
        });

        Ok(serde_json::to_string_pretty(&jsonld)?)
    }

    fn calculate_semantic_richness(&self, ucl: &UCLContract) -> f64 {
        let mut score = 0.0;

        // Check for comprehensive summary
        if !ucl.summary.what_it_does.is_empty() { score += 0.25; }
        if !ucl.summary.who_its_for.is_empty() { score += 0.25; }
        if !ucl.summary.when_it_executes.is_empty() { score += 0.25; }

        // Check metadata completeness
        if !ucl.metadata.parties.is_empty() { score += 0.25; }

        score
    }

    fn calculate_citation_friendliness(&self, ucl: &UCLContract) -> f64 {
        let mut score = 0.0;

        // Clear contract ID
        if ucl.contract_id.starts_with("smart402:") { score += 0.4; }

        // Plain English summary
        if ucl.summary.plain_english.len() > 50 { score += 0.3; }

        // Structured data
        if !ucl.conditions.required.is_empty() { score += 0.3; }

        score
    }

    fn calculate_findability(&self, ucl: &UCLContract) -> f64 {
        let mut score = 0.5; // Base score

        // Category helps findability
        if !ucl.metadata.category.is_empty() { score += 0.25; }

        // Contract type helps findability
        if !ucl.metadata.contract_type.is_empty() { score += 0.25; }

        score
    }

    fn calculate_authority_signals(&self, _ucl: &UCLContract) -> f64 {
        // Placeholder - would check deployment, usage, etc.
        0.5
    }

    fn calculate_citation_presence(&self, _ucl: &UCLContract) -> f64 {
        // Placeholder - would check external citations
        0.5
    }
}
