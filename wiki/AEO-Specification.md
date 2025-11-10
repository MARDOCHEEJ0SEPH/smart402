# AEO Specification

**Answer Engine Optimization** - Making Smart Contracts Discoverable by AI Systems

## Overview

AEO (Answer Engine Optimization) is a protocol for optimizing smart contracts to be discoverable and citable by AI systems like ChatGPT, Claude, Perplexity, Gemini, and future AI platforms.

## The Problem

Traditional SEO optimizes for search engines. But in the AI era:
- Users ask AI assistants questions instead of searching
- AI systems need to discover, understand, and cite contracts
- Traditional SEO techniques don't work for AI discovery

## The Solution

AEO provides a comprehensive framework for making contracts AI-discoverable through:
- **Semantic markup** using JSON-LD and Schema.org
- **Citation-friendly formatting** for easy AI reference
- **Multi-dimensional scoring** to measure discoverability
- **Distribution strategies** across AI-accessible channels

## Core Components

### 1. AEO Score Formula

The AEO score is calculated using 5 dimensions:

```
AEO_Score = w₁·SR + w₂·CF + w₃·F + w₄·AS + w₅·CP

Where:
SR = Semantic Richness (0-1)
CF = Citation Friendliness (0-1)
F = Findability (0-1)
AS = Authority Signals (0-1)
CP = Citation Presence (0-1)

Default weights:
w₁ = 0.25 (Semantic Richness)
w₂ = 0.20 (Citation Friendliness)
w₃ = 0.25 (Findability)
w₄ = 0.15 (Authority Signals)
w₅ = 0.15 (Citation Presence)
```

### 2. Semantic Richness (SR)

Measures how well the contract describes itself:

```
SR = (metadata_completeness + entity_richness + relationship_clarity) / 3

Factors:
- Clear title and description
- Comprehensive metadata
- Entity relationships
- Intent clarity
- Use case documentation
```

**Example:**
```json
{
  "title": "Monthly SaaS Subscription Contract",
  "description": "Automated monthly payment for software service with 99.9% uptime SLA",
  "category": "saas",
  "tags": ["subscription", "automated-payment", "sla"],
  "use_cases": ["recurring-revenue", "service-monitoring"]
}
```

### 3. Citation Friendliness (CF)

Measures how easy it is for AI to cite the contract:

```
CF = (clarity_score + reference_format + attribution_quality) / 3

Factors:
- Clear contract ID
- Canonical URL
- Version information
- Author attribution
- License clarity
- Citation format examples
```

**Example:**
```json
{
  "contract_id": "smart402:saas:2024:abc123",
  "canonical_url": "https://contracts.smart402.io/saas/abc123",
  "version": "1.0.0",
  "author": "Example Corp",
  "license": "MIT",
  "citation": "Smart402 SaaS Contract (v1.0.0, 2024)"
}
```

### 4. Findability (F)

Measures how easily AI can discover the contract:

```
F = (distribution_score + indexing_quality + freshness) / 3

Factors:
- Multi-platform presence
- Proper indexing
- Content freshness
- Sitemap inclusion
- API discoverability
```

**Distribution Channels:**
- Contract registries
- IPFS/decentralized storage
- GitHub repositories
- API endpoints
- Documentation sites

### 5. Authority Signals (AS)

Measures contract credibility:

```
AS = (usage_metrics + verification_status + community_trust) / 3

Factors:
- Deployment history
- Transaction volume
- Community endorsements
- Audit status
- Creator reputation
```

### 6. Citation Presence (CP)

Measures existing citations:

```
CP = (citation_count + citation_quality + citation_diversity) / 3

Factors:
- Number of citations
- Citation source quality
- Citation context relevance
- Cross-platform citations
```

## JSON-LD Implementation

### Basic Structure

```json
{
  "@context": "https://schema.org/",
  "@type": "SmartContract",
  "identifier": "smart402:saas:abc123",
  "name": "Monthly SaaS Subscription",
  "description": "Automated monthly payment contract with SLA monitoring",
  "version": "1.0.0",
  "datePublished": "2024-01-15",
  "author": {
    "@type": "Organization",
    "name": "Example Corp",
    "url": "https://example.com"
  },
  "license": "https://opensource.org/licenses/MIT",
  "programmingLanguage": {
    "@type": "ComputerLanguage",
    "name": "Solidity",
    "version": "0.8.0"
  },
  "keywords": ["saas", "subscription", "automated-payment", "sla"],
  "category": "Financial Contract",
  "offers": {
    "@type": "Offer",
    "price": "99",
    "priceCurrency": "USD",
    "recurring": "P1M"
  }
}
```

### Extended Metadata

```json
{
  "@context": ["https://schema.org/", "https://smart402.io/context"],
  "@type": ["SmartContract", "Smart402Contract"],
  "contractType": "saas-subscription",
  "blockchain": "polygon",
  "aeoScore": {
    "@type": "AEOScore",
    "total": 0.85,
    "semanticRichness": 0.90,
    "citationFriendliness": 0.85,
    "findability": 0.82,
    "authoritySignals": 0.75,
    "citationPresence": 0.80
  },
  "parties": [
    {
      "@type": "Organization",
      "role": "Vendor",
      "identifier": "vendor@example.com"
    },
    {
      "@type": "Organization",
      "role": "Customer",
      "identifier": "customer@example.com"
    }
  ],
  "paymentTerms": {
    "@type": "PaymentTerms",
    "amount": "99",
    "currency": "USDC",
    "frequency": "monthly",
    "blockchain": "polygon"
  },
  "conditions": [
    {
      "@type": "Condition",
      "name": "Uptime SLA",
      "description": "Service must maintain 99.9% uptime",
      "threshold": 0.999
    }
  ]
}
```

## Optimization Strategies

### 1. Semantic Optimization

**DO:**
- ✅ Use clear, descriptive titles
- ✅ Provide comprehensive descriptions
- ✅ Include relevant keywords naturally
- ✅ Document all use cases
- ✅ Explain contract logic in plain English

**DON'T:**
- ❌ Keyword stuffing
- ❌ Ambiguous terminology
- ❌ Missing metadata
- ❌ Incomplete documentation

### 2. Citation Optimization

**DO:**
- ✅ Provide clear contract IDs
- ✅ Include version information
- ✅ Add author attribution
- ✅ Use canonical URLs
- ✅ Provide citation examples

**DON'T:**
- ❌ Generic identifiers
- ❌ Missing versioning
- ❌ Unclear ownership
- ❌ Broken links

### 3. Distribution Optimization

**DO:**
- ✅ Publish to multiple platforms
- ✅ Use decentralized storage
- ✅ Provide API access
- ✅ Submit to contract registries
- ✅ Keep content fresh

**DON'T:**
- ❌ Single point of failure
- ❌ Centralized-only storage
- ❌ Hidden from indexing
- ❌ Stale content

## SDK Integration

### JavaScript

```javascript
const { Smart402, AEOEngine } = require('@smart402/sdk');

// Create contract
const contract = await Smart402.create({
  type: 'saas-subscription',
  // ... config
});

// Get AEO score
const aeoEngine = new AEOEngine();
const score = aeoEngine.calculateScore(contract.ucl);

console.log('AEO Score:', score.total);
console.log('Semantic Richness:', score.semantic_richness);
console.log('Citation Friendliness:', score.citation_friendliness);

// Generate JSON-LD
const jsonld = aeoEngine.generateJSONLD(contract.ucl);
console.log('JSON-LD:', jsonld);
```

### Python

```python
from smart402 import Smart402
from smart402.aeo import AEOEngine

# Create contract
contract = await Smart402.create({
    'type': 'saas-subscription',
    # ... config
})

# Get AEO score
aeo_engine = AEOEngine()
score = aeo_engine.calculate_score(contract.ucl)

print(f'AEO Score: {score["total"]}')
print(f'Semantic Richness: {score["semantic_richness"]}')

# Generate JSON-LD
jsonld = aeo_engine.generate_jsonld(contract.ucl)
print(f'JSON-LD: {jsonld}')
```

### Rust

```rust
use smart402::{Smart402, AEOEngine};

// Create contract
let contract = Smart402::create(config).await?;

// Get AEO score
let aeo_engine = AEOEngine::new();
let score = aeo_engine.calculate_score(&contract.ucl)?;

println!("AEO Score: {}", score.total);
println!("Semantic Richness: {}", score.semantic_richness);

// Generate JSON-LD
let jsonld = aeo_engine.generate_jsonld(&contract.ucl)?;
println!("JSON-LD: {}", jsonld);
```

## Best Practices

### 1. Write for Humans First

AI systems understand human language best. Write clear, natural descriptions.

**Good:**
```
"Monthly SaaS subscription with automated payment of $99 USDC.
Includes 99.9% uptime SLA with automatic service credits."
```

**Bad:**
```
"Contract_SaaS_v1_monthly_99_USDC_polygon_automated"
```

### 2. Provide Context

Explain what, why, when, and who:

```json
{
  "what_it_does": "Automates monthly subscription payments",
  "who_its_for": "SaaS vendors and enterprise customers",
  "when_it_executes": "1st day of each month",
  "why_it_matters": "Eliminates manual billing and ensures SLA compliance"
}
```

### 3. Use Structured Data

Always include JSON-LD markup for AI parsing:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org/",
  "@type": "SmartContract",
  ...
}
</script>
```

### 4. Maintain Freshness

Update contracts regularly:
- Add new use cases
- Update documentation
- Refresh examples
- Update version history

### 5. Build Authority

- Deploy to testnets for verification
- Get community feedback
- Document successful executions
- Maintain public audit trail

## Measuring Success

### Target Scores

- **Excellent**: AEO Score > 0.80
- **Good**: AEO Score > 0.65
- **Needs Improvement**: AEO Score < 0.50

### Monitoring

Track your AEO score over time:

```javascript
const history = [];

setInterval(async () => {
  const score = aeoEngine.calculateScore(contract.ucl);
  history.push({
    timestamp: Date.now(),
    score: score.total,
    details: score
  });

  console.log('Current AEO Score:', score.total);
}, 86400000); // Daily
```

## Resources

- **[LLMO Specification](LLMO-Specification)** - LLM understanding
- **[X402 Specification](X402-Specification)** - Payment protocol
- **[Examples](Examples)** - Real-world AEO implementations
- **Schema.org**: https://schema.org/
- **JSON-LD**: https://json-ld.org/

---

[← Home](Home) | [LLMO Specification →](LLMO-Specification)
