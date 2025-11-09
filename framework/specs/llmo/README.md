# LLMO Protocol Specification
## Large Language Model Optimization - Universal Contract Language (UCL)

**Version:** 1.0.0
**Status:** Draft
**Last Updated:** 2024-01-01

---

## Abstract

The LLMO (Large Language Model Optimization) protocol defines the **Universal Contract Language (UCL)** - a standard format for encoding smart contracts that any LLM can understand, verify, and reason about.

UCL contracts are simultaneously:
- **Human-readable** (natural language)
- **Machine-readable** (structured data)
- **LLM-optimized** (semantic clarity)
- **Executable** (compilable to blockchain code)

---

## 1. Design Principles

### 1.1 Universal Comprehension
- **Any LLM** can parse and understand UCL
- **Multi-model compatibility** (GPT, Claude, Gemini, etc.)
- **Future-proof** against model architecture changes

### 1.2 Self-Describing
Contracts explain themselves:
```
"I am a monthly subscription contract.
I charge $99/month if service uptime > 99%.
Payment happens automatically on the 1st."
```

### 1.3 Layered Representation

UCL has 4 layers:
1. **Natural Language** - Humans read this
2. **Structured Format** - LLMs parse this
3. **Logic Rules** - Machines execute this
4. **Blockchain Code** - Chain runs this

---

## 2. UCL Structure

### 2.1 Complete UCL Format

```yaml
# ============================================
# SMART402 UNIVERSAL CONTRACT LANGUAGE (UCL)
# ============================================

contract_id: "smart402:saas:abc123"
version: "1.0.0"
standard: "UCL-1.0"

# ==================
# HUMAN LAYER
# ==================
summary:
  title: "Monthly SaaS Subscription"
  plain_english: |
    This contract automates monthly subscription payments.
    Customer pays $99/month for SaaS service.
    Payment triggered automatically if service meets 99% uptime.

  what_it_does: "Automates recurring payments with quality guarantees"
  who_its_for: "SaaS vendors and customers"
  when_it_executes: "Monthly on the 1st if conditions met"

# ==================
# METADATA
# ==================
metadata:
  type: "saas-subscription"
  category: "recurring-payment"
  parties:
    - role: "vendor"
      identifier: "0xVendor..."
      name: "SaaS Provider Inc"
    - role: "customer"
      identifier: "0xCustomer..."
      name: "Customer Corp"

  dates:
    effective: "2024-01-01"
    duration: "12 months"
    renewal: "auto-renew with 30-day notice"

  jurisdiction: "Delaware"
  governing_law: "Delaware Commercial Code"

# ==================
# PAYMENT TERMS
# ==================
payment:
  structure: "recurring"
  amount: 99
  currency: "USD"
  token: "USDC"
  blockchain: "Polygon"
  frequency: "monthly"
  day_of_month: 1
  timezone: "UTC"

  calculation:
    base_amount: 99
    adjustments:
      - condition: "uptime < 0.99"
        type: "discount"
        value: "10%"
      - condition: "uptime < 0.95"
        type: "discount"
        value: "20%"

# ==================
# CONDITIONS
# ==================
conditions:
  required:
    - id: "service_active"
      description: "Service must be active"
      source: "service_api"
      operator: "equals"
      expected: true

    - id: "uptime_met"
      description: "Service uptime >= 99%"
      source: "monitoring_api"
      metric: "uptime_percentage"
      operator: "greater_than_or_equal"
      threshold: 0.99

    - id: "payment_not_disputed"
      description: "No active payment disputes"
      source: "dispute_registry"
      operator: "equals"
      expected: false

  optional:
    - id: "customer_feedback"
      description: "Customer satisfaction score"
      source: "feedback_api"
      metric: "satisfaction_score"
      operator: "greater_than"
      threshold: 4.0
      penalty: "5% discount if below threshold"

# ==================
# EXECUTION RULES
# ==================
rules:
  - rule_id: "monthly_payment"
    name: "Execute Monthly Payment"
    trigger: "time_based"
    schedule: "0 0 1 * *"  # Cron: 1st of month at midnight

    conditions:
      all_of:
        - "service_active == true"
        - "uptime_met == true"
        - "payment_not_disputed == false"

    actions:
      - action: "calculate_amount"
        inputs:
          base: "${payment.amount}"
          adjustments: "${payment.calculation.adjustments}"
        output: "final_amount"

      - action: "execute_payment"
        from: "${parties.customer.identifier}"
        to: "${parties.vendor.identifier}"
        amount: "${final_amount}"
        token: "${payment.token}"
        network: "${payment.blockchain}"

      - action: "emit_event"
        event: "payment_executed"
        data:
          amount: "${final_amount}"
          timestamp: "${now()}"

    on_success:
      - "log_payment(final_amount)"
      - "send_receipt(customer.email)"
      - "update_subscription_status()"

    on_failure:
      - "log_error(error_details)"
      - "notify_parties(failure_reason)"
      - "schedule_retry(exponential_backoff)"

# ==================
# DATA SOURCES (ORACLES)
# ==================
oracles:
  - id: "service_api"
    type: "custom_api"
    endpoint: "https://api.vendor.com/service/status"
    authentication: "oauth2"
    refresh_rate: "1 hour"
    required: true

  - id: "monitoring_api"
    type: "custom_api"
    endpoint: "https://monitor.vendor.com/uptime"
    authentication: "api_key"
    refresh_rate: "5 minutes"
    required: true

  - id: "dispute_registry"
    type: "smart_contract"
    address: "0xDispute..."
    blockchain: "Polygon"
    method: "hasActiveDispute"
    required: true

# ==================
# DISPUTE RESOLUTION
# ==================
dispute:
  method: "multisig"
  signers:
    - "${parties.vendor.identifier}"
    - "${parties.customer.identifier}"
    - "0xArbitrator..."  # Neutral third party
  required_signatures: 2
  timeout: "7 days"

  escalation:
    - level: 1
      method: "automated_review"
      timeout: "24 hours"

    - level: 2
      method: "human_arbitrator"
      timeout: "7 days"

    - level: 3
      method: "dao_vote"
      timeout: "14 days"

# ==================
# TERMINATION
# ==================
termination:
  notice_period: "30 days"
  final_payment: "prorated"
  data_retention: "90 days"

  conditions:
    - "Either party may terminate with 30-day notice"
    - "Immediate termination if material breach"
    - "Auto-terminate if 3 consecutive payment failures"

# ==================
# SELF-DESCRIPTION (for LLMs)
# ==================
llm_instructions:
  how_to_read: |
    This contract has four main sections:
    1. PAYMENT: Look at "payment.amount" for the price
    2. CONDITIONS: Check "conditions.required" for what must be true
    3. RULES: See "rules" for when and how payments execute
    4. ORACLES: Find "oracles" for data sources

  how_to_verify: |
    To verify this contract:
    1. Check all required conditions are defined
    2. Verify oracle endpoints are accessible
    3. Confirm payment logic is unambiguous
    4. Ensure dispute resolution is specified

  common_questions:
    - q: "How much does this contract cost?"
      a: "Base price is ${payment.amount} ${payment.currency} per ${payment.frequency}"

    - q: "When do payments happen?"
      a: "On day ${payment.day_of_month} of each month at ${payment.timezone}"

    - q: "What if something goes wrong?"
      a: "See 'dispute.method' for resolution process: ${dispute.method}"

    - q: "Can I cancel?"
      a: "Yes, with ${termination.notice_period} notice"

# ==================
# COMPLIANCE
# ==================
compliance:
  standards:
    - "UCL-1.0"
    - "ERC-20 compatible"
    - "GDPR compliant"

  certifications:
    - type: "security_audit"
      auditor: "CertiK"
      date: "2024-01-01"
      report: "ipfs://QmAudit..."

  legal:
    jurisdiction: "Delaware"
    governing_law: "Delaware Commercial Code Section 12"
    arbitration: "AAA Commercial Arbitration Rules"
```

---

## 3. LLM Optimization Patterns

### 3.1 Clear Intent Declaration

Start every section with its purpose:

```yaml
payment:
  # PURPOSE: Defines how much and when customer pays
  # READS: Customer expects to see pricing here
  # MACHINES: Extract amount, frequency, token for execution
  amount: 99
  frequency: "monthly"
```

### 3.2 Natural Language Mapping

Provide NL equivalent for every structured element:

```yaml
condition:
  id: "uptime_check"
  operator: "gte"
  threshold: 0.99

  # Natural language equivalent:
  plain_english: "Service uptime must be at least 99%"
```

### 3.3 Example-Driven Documentation

Include examples inline:

```yaml
payment_calculation:
  formula: "base * (1 - discount)"

  examples:
    - scenario: "Normal month, 99.5% uptime"
      base: 99
      discount: 0
      result: 99

    - scenario: "Poor month, 97% uptime"
      base: 99
      discount: 0.10
      result: 89.10
```

---

## 4. Semantic Validation Rules

### 4.1 Required Fields

Every UCL contract MUST have:

```yaml
required:
  - contract_id         # Unique identifier
  - version            # UCL version
  - metadata.type      # Contract type
  - metadata.parties   # At least 2 parties
  - payment            # Payment terms
  - conditions         # Execution conditions
  - rules              # Execution rules
  - llm_instructions   # LLM guidance
```

### 4.2 Type Safety

Define types for all fields:

```yaml
types:
  payment.amount:
    type: "number"
    min: 0
    max: 1000000000
    precision: 2

  payment.frequency:
    type: "enum"
    values: ["one-time", "daily", "weekly", "monthly", "yearly"]

  conditions[].operator:
    type: "enum"
    values: ["equals", "not_equals", "greater_than", "less_than",
             "greater_than_or_equal", "less_than_or_equal", "contains"]
```

### 4.3 Logical Consistency

Contracts must be internally consistent:

```yaml
consistency_rules:
  - if: "payment.frequency == 'monthly'"
    then: "payment.day_of_month must be between 1 and 28"

  - if: "conditions.required exists"
    then: "rules must reference those conditions"

  - if: "oracles defined"
    then: "conditions must use those oracle IDs"
```

---

## 5. Compilation Targets

### 5.1 To Solidity

```javascript
const { compile } = require('@smart402/compiler');

const solidity = compile(uclContract, {
  target: 'solidity',
  version: '0.8.20',
  optimize: true
});

// Output: Deployable Solidity contract
```

### 5.2 To JavaScript

```javascript
const js = compile(uclContract, {
  target: 'javascript',
  runtime: 'node',
  async: true
});

// Output: Executable JS module
```

### 5.3 To Rust

```javascript
const rust = compile(uclContract, {
  target: 'rust',
  framework: 'substrate',
  optimize: 'speed'
});

// Output: Rust smart contract
```

---

## 6. LLM Interaction Patterns

### 6.1 Contract Q&A

LLMs should be able to answer:

```python
def answer_question(contract, question):
    """
    LLM answers questions about contract
    """
    if "how much" in question.lower():
        return f"${contract.payment.amount} per {contract.payment.frequency}"

    if "when" in question.lower():
        return f"On day {contract.payment.day_of_month} of each month"

    if "cancel" in question.lower():
        return f"Yes, with {contract.termination.notice_period} notice"

    # LLM generates answer from contract structure
    return llm.generate_answer(contract, question)
```

### 6.2 Contract Verification

```python
def verify_contract(contract):
    """
    LLM verifies contract is well-formed
    """
    checks = {
        'has_parties': len(contract.metadata.parties) >= 2,
        'has_payment': contract.payment is not None,
        'has_conditions': len(contract.conditions.required) > 0,
        'has_rules': len(contract.rules) > 0,
        'oracles_defined': all(
            oracle in contract.oracles
            for condition in contract.conditions
            for oracle in condition.sources
        )
    }

    return all(checks.values()), checks
```

### 6.3 Contract Reasoning

```python
def reason_about_contract(contract, scenario):
    """
    LLM predicts contract behavior
    """
    # Example: "What happens if uptime is 97%?"
    conditions = evaluate_conditions(contract, scenario)

    if conditions['uptime_met'] == False:
        applicable_adjustments = [
            adj for adj in contract.payment.calculation.adjustments
            if evaluate(adj.condition, scenario)
        ]

        final_amount = calculate_with_adjustments(
            contract.payment.amount,
            applicable_adjustments
        )

        return {
            'payment_will_execute': True,
            'amount': final_amount,
            'reason': f"Uptime discount applied: {applicable_adjustments}"
        }
```

---

## 7. Template System

### 7.1 Template Variables

UCL supports template variables:

```yaml
contract_template:
  payment:
    amount: "{{MONTHLY_PRICE}}"
    currency: "{{CURRENCY}}"
    token: "{{TOKEN}}"

  conditions:
    - id: "uptime_check"
      threshold: "{{MIN_UPTIME}}"
```

### 7.2 Template Instantiation

```javascript
const template = loadTemplate('saas-subscription');

const contract = template.instantiate({
  MONTHLY_PRICE: 99,
  CURRENCY: "USD",
  TOKEN: "USDC",
  MIN_UPTIME: 0.99
});
```

---

## 8. Multi-Language Support

### 8.1 Language Codes

```yaml
contract:
  language: "en"  # Primary language

  translations:
    es:  # Spanish
      summary.title: "Suscripción SaaS Mensual"
      summary.plain_english: "Este contrato automatiza pagos mensuales..."

    fr:  # French
      summary.title: "Abonnement SaaS Mensuel"
      summary.plain_english: "Ce contrat automatise les paiements mensuels..."
```

---

## 9. Validation & Testing

### 9.1 UCL Validator

```bash
npm install -g @smart402/ucl-validator

ucl-validator validate contract.yaml
```

Output:
```
✓ Contract ID is valid
✓ All required fields present
✓ Type constraints satisfied
✓ Logical consistency verified
✓ Oracle endpoints reachable
✓ LLM readability: 95/100

Contract is valid UCL-1.0
```

### 9.2 LLM Comprehension Test

```javascript
const { testLLM } = require('@smart402/testing');

testLLM(contract)
  .canParse()
  .canAnswer("How much does this cost?")
  .canAnswer("When do payments happen?")
  .canPredict({ uptime: 0.97 })
  .minimumScore(0.9)
  .run();
```

---

## 10. Best Practices

### ✅ DO:
- Write clear natural language summaries
- Include `llm_instructions` section
- Provide examples for complex logic
- Use consistent naming
- Document all fields
- Add Q&A pairs

### ❌ DON'T:
- Use ambiguous language
- Leave sections undocumented
- Create circular dependencies
- Omit error handling
- Use proprietary formats

---

## 11. Compliance Checklist

- [ ] Valid UCL-1.0 structure
- [ ] All required fields present
- [ ] Natural language summaries included
- [ ] LLM instructions provided
- [ ] At least 3 common questions answered
- [ ] Type constraints specified
- [ ] Compilation targets tested
- [ ] Multi-LLM compatibility verified

---

## 12. Future Extensions

### Version 1.1 (Planned)
- Conditional logic operators (AND, OR, NOT)
- Nested contract references
- Dynamic pricing formulas
- Multi-party voting mechanisms

### Version 2.0 (Research)
- AI-generated contracts from prompts
- Cross-chain execution coordination
- Privacy-preserving conditions
- Quantum-safe signatures

---

## Appendix A: Full Example

See [ucl-example.yaml](./examples/ucl-example.yaml)

## Appendix B: Schema

See [ucl-schema.json](./schema/ucl-schema.json) for JSON Schema

---

**This specification enables any LLM to understand any contract.**
