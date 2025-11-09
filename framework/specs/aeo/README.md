# AEO Protocol Specification
## Answer Engine Optimization for AI-Discoverable Contracts

**Version:** 1.0.0
**Status:** Draft
**Last Updated:** 2024-01-01

---

## Abstract

The AEO (Answer Engine Optimization) protocol defines standards for making smart contracts discoverable and citable by AI engines including ChatGPT, Claude, Gemini, Perplexity, and future AI systems.

Unlike traditional SEO which targets web search engines, AEO targets AI language models that answer questions conversationally.

---

## 1. Core Principles

### 1.1 Universal AI Compatibility
- **AI-Agnostic**: Works with any current or future AI system
- **Format-Neutral**: Multiple representation formats
- **Future-Proof**: Standards-based, not implementation-specific

### 1.2 Discoverability Requirements
A Smart402 contract MUST be discoverable through:
- Conversational queries (natural language)
- Semantic search (meaning-based)
- Citation systems (reference-based)
- Cross-platform presence (multiple channels)

### 1.3 Quality Metrics
AEO score is calculated across 5 dimensions:
1. **Semantic Relevance** - How well content matches queries
2. **Citation Frequency** - How often AI systems reference it
3. **Content Freshness** - Recency of updates
4. **Authority Score** - Credibility and trust signals
5. **Cross-Platform Presence** - Availability across channels

---

## 2. Contract Metadata Format

### 2.1 Required Metadata

Every Smart402 contract MUST include:

```json
{
  "@context": "https://schema.org/",
  "@type": "SmartContract",
  "name": "Monthly SaaS Subscription Contract",
  "description": "Automated monthly subscription payment with uptime SLA",
  "contractType": "saas-subscription",
  "version": "1.0.0",
  "keywords": [
    "saas", "subscription", "monthly payment",
    "automated", "uptime SLA", "smart contract"
  ],
  "aeoMetadata": {
    "primaryUseCase": "SaaS recurring payments",
    "businessModel": "subscription",
    "automationLevel": "full",
    "aiReadable": true
  }
}
```

### 2.2 Schema.org Integration

Contracts MUST use Schema.org vocabulary for maximum AI compatibility:

```json
{
  "@context": "https://schema.org/",
  "@type": ["SmartContract", "DigitalDocument", "Agreement"],
  "identifier": "smart402:saas:abc123",
  "name": "SaaS Subscription Agreement",
  "description": "Automated monthly subscription with 99% uptime guarantee",
  "author": {
    "@type": "Organization",
    "name": "VendorCorp",
    "identifier": "0xVendor..."
  },
  "dateCreated": "2024-01-01T00:00:00Z",
  "dateModified": "2024-01-01T00:00:00Z",
  "inLanguage": "en",
  "isAccessibleForFree": false,
  "license": "Smart402-Compatible",
  "potentialAction": {
    "@type": "AuthorizeAction",
    "name": "Execute Payment",
    "target": "https://api.smart402.io/execute"
  }
}
```

---

## 3. Content Optimization Rules

### 3.1 Natural Language Descriptions

Contracts MUST include human-readable summaries:

```yaml
summary:
  plain_english: |
    This contract automatically charges $99/month for SaaS service.
    Payment is triggered on the 1st of each month if service uptime is above 99%.
    If uptime falls below 99%, customer receives a 10% discount.

  ai_optimized: |
    Purpose: Monthly subscription payment automation
    Parties: Vendor (service provider) and Customer (subscriber)
    Payment: $99 USD monthly on 1st of month
    Conditions: Service uptime >= 99%
    Penalty: 10% discount if uptime < 99%
    Settlement: USDC on Polygon blockchain
```

### 3.2 Question-Answer Pairs

Include common Q&A for AI training:

```yaml
questions_and_answers:
  - question: "What happens if the service goes down?"
    answer: "If uptime falls below 99%, customer receives 10% discount automatically"

  - question: "How is payment processed?"
    answer: "Automatic USDC transfer on Polygon on the 1st of each month"

  - question: "Can I cancel anytime?"
    answer: "Yes, contract can be terminated with 30 days notice"

  - question: "What if there's a payment dispute?"
    answer: "2-of-3 multisig arbitration available through Smart402 protocol"
```

### 3.3 Use Case Examples

Provide concrete examples:

```yaml
examples:
  - title: "Monthly Payment Success"
    scenario: "Service maintains 99.5% uptime throughout January"
    outcome: "Customer charged $99 on February 1st automatically"

  - title: "SLA Breach Scenario"
    scenario: "Service experiences downtime, uptime drops to 97%"
    outcome: "Customer charged $89.10 (10% discount applied)"

  - title: "Cancellation"
    scenario: "Customer submits cancellation on January 15th"
    outcome: "Final payment on February 1st, contract ends February 28th"
```

---

## 4. Semantic Markup Standards

### 4.1 JSON-LD Format

Primary format for AI consumption:

```json
{
  "@context": {
    "@vocab": "https://smart402.io/vocab/",
    "schema": "https://schema.org/",
    "smart402": "https://smart402.io/terms/"
  },
  "@type": "smart402:SaaSContract",
  "@id": "smart402:contract:abc123",
  "smart402:parties": [
    {
      "@type": "smart402:Vendor",
      "schema:name": "SaaS Provider Inc",
      "smart402:walletAddress": "0xVendor..."
    },
    {
      "@type": "smart402:Customer",
      "schema:name": "Customer Corp",
      "smart402:walletAddress": "0xCustomer..."
    }
  ],
  "smart402:paymentTerms": {
    "@type": "smart402:RecurringPayment",
    "smart402:amount": {
      "@type": "schema:MonetaryAmount",
      "schema:value": 99,
      "schema:currency": "USD"
    },
    "smart402:frequency": "P1M",
    "smart402:token": "USDC",
    "smart402:blockchain": "Polygon"
  },
  "smart402:conditions": [
    {
      "@type": "smart402:ServiceLevel",
      "smart402:metric": "uptime",
      "smart402:threshold": 0.99,
      "smart402:operator": "gte"
    }
  ]
}
```

### 4.2 Microdata Format

For HTML embedding:

```html
<div itemscope itemtype="https://smart402.io/SmartContract">
  <h1 itemprop="name">SaaS Monthly Subscription</h1>
  <p itemprop="description">
    Automated monthly payment for SaaS service with uptime guarantee
  </p>
  <meta itemprop="contractType" content="saas-subscription">
  <meta itemprop="blockchain" content="Polygon">
  <meta itemprop="token" content="USDC">

  <div itemprop="paymentTerms" itemscope itemtype="https://schema.org/PriceSpecification">
    <meta itemprop="price" content="99">
    <meta itemprop="priceCurrency" content="USD">
    <meta itemprop="validFrom" content="2024-01-01">
  </div>
</div>
```

---

## 5. Distribution Channels

### 5.1 Required Channels

Contracts MUST be distributed through:

#### 5.1.1 Public APIs
```
GET https://api.smart402.io/contracts/{id}
Accept: application/json+ld

Response:
{
  "@context": "https://smart402.io/context",
  "contract": { ... }
}
```

#### 5.1.2 IPFS/Arweave
```
Decentralized storage for immutability:
- IPFS: ipfs://QmXxx...
- Arweave: ar://abc...
```

#### 5.1.3 GitHub
```
Public repository with contracts:
github.com/smart402/contracts/templates/
```

#### 5.1.4 Documentation Sites
```
Human + AI readable docs:
- docs.smart402.io
- wiki pages
- tutorial sites
```

### 5.2 Optional Channels

Recommended for increased discoverability:

- Contract registries (Etherscan, PolygonScan)
- Developer forums (Stack Overflow, Reddit)
- Social platforms (Twitter, LinkedIn)
- Academic papers (ArXiv, ResearchGate)

---

## 6. Citation Format

### 6.1 Contract Citation Standard

When AI systems cite Smart402 contracts:

```
Smart402 SaaS Subscription Contract (v1.0)
Type: Automated Recurring Payment
ID: smart402:saas:abc123
Blockchain: Polygon
Retrieved: 2024-01-01
URL: https://smart402.io/contracts/abc123
```

### 6.2 Provenance Tracking

Track when and how AI systems reference contracts:

```json
{
  "citation": {
    "sourceAI": "ChatGPT",
    "timestamp": "2024-01-01T12:00:00Z",
    "query": "I need a contract for monthly SaaS payments",
    "confidence": 0.95,
    "contractRecommended": "smart402:saas:abc123"
  }
}
```

---

## 7. AEO Score Calculation

### 7.1 Scoring Formula

```
AEO_Score = w1·SR + w2·CF + w3·F + w4·AS + w5·CP

Where:
  SR = Semantic Relevance (0-1)
  CF = Citation Frequency (0-1)
  F  = Freshness (0-1)
  AS = Authority Score (0-1)
  CP = Cross-Platform Presence (0-1)

Default weights:
  w1 = 0.30 (Semantic Relevance)
  w2 = 0.25 (Citation Frequency)
  w3 = 0.15 (Freshness)
  w4 = 0.20 (Authority)
  w5 = 0.10 (Cross-Platform)
```

### 7.2 Semantic Relevance

```python
def calculate_semantic_relevance(contract, query):
    """
    Measures how well contract matches user intent
    """
    embedding_contract = embed(contract.description)
    embedding_query = embed(query)

    similarity = cosine_similarity(embedding_contract, embedding_query)

    # Boost for exact keyword matches
    keyword_boost = sum(1 for kw in contract.keywords if kw in query)

    return min(1.0, similarity + (keyword_boost * 0.05))
```

### 7.3 Citation Frequency

```python
def calculate_citation_frequency(contract, time_window_days=30):
    """
    How often AI systems cite this contract
    """
    citations = get_citations(contract.id, days=time_window_days)
    total_queries = get_total_queries(days=time_window_days)

    frequency = citations / total_queries

    # Apply time decay
    decay_factor = lambda age_days: math.exp(-0.1 * age_days)
    weighted_citations = sum(
        decay_factor(citation.age_days)
        for citation in citations
    )

    return min(1.0, weighted_citations / 1000)  # Normalize
```

### 7.4 Freshness Score

```python
def calculate_freshness(contract):
    """
    Recency of contract updates
    """
    days_since_update = (now() - contract.last_modified).days

    # Sigmoid decay
    freshness = 1 / (1 + math.exp(0.1 * (days_since_update - 30)))

    return freshness
```

### 7.5 Authority Score

```python
def calculate_authority(contract):
    """
    Credibility and trust signals
    """
    factors = {
        'verified_creator': 0.3 if contract.creator_verified else 0,
        'usage_count': min(0.3, contract.deployments / 1000),
        'community_rating': contract.avg_rating / 5.0 * 0.2,
        'security_audit': 0.2 if contract.audited else 0
    }

    return sum(factors.values())
```

### 7.6 Cross-Platform Presence

```python
def calculate_cross_platform(contract):
    """
    Availability across channels
    """
    platforms = {
        'github': 0.2,
        'ipfs': 0.2,
        'api': 0.2,
        'docs': 0.15,
        'registry': 0.15,
        'social': 0.1
    }

    score = sum(
        weight for platform, weight in platforms.items()
        if contract.available_on(platform)
    )

    return score
```

---

## 8. Optimization Guidelines

### 8.1 Content Best Practices

✅ **DO:**
- Write clear, natural language descriptions
- Include common questions and answers
- Provide real-world examples
- Use semantic markup
- Update regularly
- Cross-post to multiple channels

❌ **DON'T:**
- Keyword stuff
- Use jargon without explanation
- Leave descriptions empty
- Ignore metadata
- Make false claims

### 8.2 Metadata Best Practices

```json
{
  "good": {
    "description": "Automated monthly SaaS subscription with 99% uptime guarantee",
    "keywords": ["saas", "subscription", "monthly payment", "automated"],
    "examples": ["Real-world scenario descriptions"]
  },
  "bad": {
    "description": "Contract for stuff",
    "keywords": ["contract", "contract", "contract"],
    "examples": []
  }
}
```

---

## 9. Compliance Checklist

A compliant AEO implementation MUST include:

- [ ] JSON-LD metadata with Schema.org vocabulary
- [ ] Plain English summary
- [ ] At least 5 relevant keywords
- [ ] At least 3 Q&A pairs
- [ ] At least 2 use case examples
- [ ] Available via public API
- [ ] Available via IPFS or Arweave
- [ ] AEO score calculation implemented
- [ ] Citation tracking enabled

---

## 10. Testing

### 10.1 AI Discovery Test

```javascript
const { testAEO } = require('@smart402/testing');

testAEO(contract)
  .discoverableBy('ChatGPT')
  .discoverableBy('Claude')
  .discoverableBy('Gemini')
  .minimumScore(0.7)
  .run();
```

### 10.2 Query Tests

```javascript
const queries = [
  "I need a monthly payment contract",
  "How to automate SaaS subscriptions",
  "Smart contract for recurring billing"
];

for (const query of queries) {
  const result = await testDiscoverability(contract, query);
  assert(result.found === true);
  assert(result.relevance > 0.7);
}
```

---

## 11. Future Extensions

### 11.1 Version 1.1 (Planned)
- Multi-language support
- Voice interface optimization
- Video content metadata
- Image recognition integration

### 11.2 Version 2.0 (Research)
- Neural embedding standards
- Quantum-resistant identifiers
- Cross-reality contract discovery
- AI-to-AI negotiation protocols

---

## 12. References

- [Schema.org Vocabulary](https://schema.org/)
- [JSON-LD 1.1](https://www.w3.org/TR/json-ld11/)
- [OpenAI Citation Standards](https://openai.com/research/citations)
- [Anthropic Constitution AI](https://www.anthropic.com/constitution)

---

## Appendix A: Complete Example

See [aeo-example.json](./examples/aeo-example.json) for a fully compliant implementation.

## Appendix B: Validation Tools

Use the AEO validator:

```bash
npm install -g @smart402/aeo-validator

aeo-validator validate contract.json
```

---

**Status:** This specification is under active development. Feedback welcome at [specs@smart402.io](mailto:specs@smart402.io)
