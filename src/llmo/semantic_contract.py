"""
Semantic Contract Structures for LLMO Layer

This module implements the machine-interpretable contract format
exactly as specified in the Smart402 plan.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum


class ContractType(Enum):
    """Contract type enumeration"""
    SaaS_RESELLER = "SaaS_Reseller_Agreement"
    VENDOR_SLA = "Vendor_Performance_SLA"
    SUPPLY_CHAIN = "Supply_Chain_Finance"
    FREELANCER = "Freelancer_Contract"
    AFFILIATE = "Affiliate_Partner_Network"
    NDA = "Non_Disclosure_Agreement"
    PURCHASE = "Purchase_Agreement"


class PaymentStructure(Enum):
    """Payment structure types"""
    TIERED_COMMISSION = "tiered_commission"
    FIXED_AMOUNT = "fixed_amount"
    PERCENTAGE = "percentage"
    MILESTONE_BASED = "milestone_based"


@dataclass
class TieredRate:
    """Tiered commission rate"""
    threshold: float
    rate: float


@dataclass
class ContractMetadata:
    """
    CONTRACT_METADATA structure as per Smart402 spec
    """
    type: str
    parties: List[str]
    effective_date: str
    term_duration: str
    renewal: str
    jurisdiction: Optional[str] = None
    industry: Optional[str] = None
    execution_requirements: Optional[List[str]] = None


@dataclass
class PaymentTerms:
    """
    PAYMENT_TERMS structure as per Smart402 spec
    """
    structure: str
    tier_1: Optional[Dict[str, float]] = None
    tier_2: Optional[Dict[str, float]] = None
    tier_3: Optional[Dict[str, float]] = None
    payment_frequency: str = "monthly"
    payment_method: str = "blockchain_automatic"
    due_date: str = "net_30_from_invoice"
    payment_token: str = "USDC"
    settlement_blockchain: str = "Polygon"


@dataclass
class PerformanceCondition:
    """
    PERFORMANCE_CONDITIONS structure
    """
    condition_id: str
    description: str
    validation_method: str
    penalty: Optional[str] = None
    cure_period: Optional[str] = None
    measurement_source: Optional[str] = None


@dataclass
class ServiceLevel:
    """
    SERVICE_LEVELS structure
    """
    metric_name: str
    target_value: str
    measurement_source: str
    penalty_for_breach: Optional[str] = None


@dataclass
class DataSource:
    """
    DATA_SOURCE for oracle integration
    """
    source_id: str
    source_url: str
    authentication: str
    refresh_rate: str
    validation_required: bool
    timestamp_validation: str


@dataclass
class ContractRule:
    """
    LLM-Parseable contract rules in IF-THEN format
    """
    rule_id: str
    rule_name: str
    conditions: List[str]
    actions: List[str]
    enabled: bool = True


class SemanticContract:
    """
    Complete semantic contract structure that AI can understand

    This follows the exact format specified in Smart402 plan:
    - Machine-interpretable format
    - Natural language explanations
    - Oracle integration points
    - Automated compliance checking
    """

    def __init__(
        self,
        metadata: ContractMetadata,
        payment_terms: PaymentTerms,
        performance_conditions: List[PerformanceCondition],
        service_levels: List[ServiceLevel],
        data_sources: List[DataSource],
        rules: List[ContractRule]
    ):
        self.metadata = metadata
        self.payment_terms = payment_terms
        self.performance_conditions = performance_conditions
        self.service_levels = service_levels
        self.data_sources = data_sources
        self.rules = rules
        self.created_at = datetime.now()
        self.contract_id = self._generate_contract_id()

    def _generate_contract_id(self) -> str:
        """Generate unique contract ID"""
        import hashlib
        data = f"{self.metadata.type}:{self.metadata.parties}:{self.created_at}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_yaml_format(self) -> str:
        """
        Export to YAML format as shown in Smart402 spec
        """
        yaml_str = f"""
CONTRACT_METADATA:
  - type: "{self.metadata.type}"
  - parties: {self.metadata.parties}
  - effective_date: "{self.metadata.effective_date}"
  - term_duration: "{self.metadata.term_duration}"
  - renewal: "{self.metadata.renewal}"
  - jurisdiction: "{self.metadata.jurisdiction or 'Not specified'}"

PAYMENT_TERMS:
  - structure: "{self.payment_terms.structure}"
"""

        if self.payment_terms.tier_1:
            yaml_str += f"""  - tier_1: {{threshold: {self.payment_terms.tier_1['threshold']}, rate: {self.payment_terms.tier_1['rate']}}}
  - tier_2: {{threshold: {self.payment_terms.tier_2['threshold']}, rate: {self.payment_terms.tier_2['rate']}}}
  - tier_3: {{threshold: {self.payment_terms.tier_3['threshold']}, rate: {self.payment_terms.tier_3['rate']}}}
"""

        yaml_str += f"""  - payment_frequency: "{self.payment_terms.payment_frequency}"
  - payment_method: "{self.payment_terms.payment_method}"
  - due_date: "{self.payment_terms.due_date}"
  - payment_token: "{self.payment_terms.payment_token}"
  - settlement_blockchain: "{self.payment_terms.settlement_blockchain}"

PERFORMANCE_CONDITIONS:
"""

        for i, cond in enumerate(self.performance_conditions, 1):
            yaml_str += f"""  - condition_{i}: "{cond.description}"
  - validation_method: "{cond.validation_method}"
  - penalty: "{cond.penalty or 'None'}"
  - cure_period: "{cond.cure_period or 'None'}"
"""

        yaml_str += "\nSERVICE_LEVELS:\n"
        for sl in self.service_levels:
            yaml_str += f"""  - {sl.metric_name}: {sl.target_value}
  - measurement_source: "{sl.measurement_source}"
"""

        return yaml_str

    def to_natural_language(self) -> str:
        """
        Generate natural language summary for AI understanding
        """
        nl_summary = f"""
SMART CONTRACT SUMMARY

Contract Type: {self.metadata.type}
Parties: {', '.join(self.metadata.parties)}
Duration: {self.metadata.term_duration}
Effective Date: {self.metadata.effective_date}

PAYMENT TERMS:
This contract uses a {self.payment_terms.structure} payment structure.
Payments are made {self.payment_terms.payment_frequency} via {self.payment_terms.payment_method}.
Payment token: {self.payment_terms.payment_token} on {self.payment_terms.settlement_blockchain} blockchain.
Payment due: {self.payment_terms.due_date}
"""

        if self.payment_terms.tier_1:
            nl_summary += f"""
COMMISSION TIERS:
- Up to ${self.payment_terms.tier_1['threshold']:,.0f}: {self.payment_terms.tier_1['rate']*100}% commission
- ${self.payment_terms.tier_2['threshold']:,.0f} and above: {self.payment_terms.tier_2['rate']*100}% commission
- ${self.payment_terms.tier_3['threshold']:,.0f} and above: {self.payment_terms.tier_3['rate']*100}% commission
"""

        nl_summary += "\nPERFORMANCE REQUIREMENTS:\n"
        for cond in self.performance_conditions:
            nl_summary += f"- {cond.description}\n"
            if cond.penalty:
                nl_summary += f"  Penalty if not met: {cond.penalty}\n"

        nl_summary += "\nSERVICE LEVEL AGREEMENTS:\n"
        for sl in self.service_levels:
            nl_summary += f"- {sl.metric_name}: {sl.target_value}\n"

        return nl_summary

    def evaluate_rule(self, rule_id: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a contract rule against current context

        Args:
            rule_id: Rule to evaluate
            context: Current state/data

        Returns:
            True if all conditions met
        """
        rule = next((r for r in self.rules if r.rule_id == rule_id), None)
        if not rule or not rule.enabled:
            return False

        # Evaluate all conditions
        for condition in rule.conditions:
            if not self._evaluate_condition(condition, context):
                return False

        return True

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a single condition string against context

        Example condition: "monthly_revenue_reported == true"
        """
        # Parse condition (simplified - would use proper parser in production)
        if "==" in condition:
            var, expected = condition.split("==")
            var = var.strip()
            expected = expected.strip()

            actual = context.get(var)

            if expected.lower() == "true":
                return actual is True
            elif expected.lower() == "false":
                return actual is False
            else:
                try:
                    return str(actual) == expected
                except:
                    return False

        elif ">" in condition:
            var, threshold = condition.split(">")
            var = var.strip()
            threshold = float(threshold.strip())
            actual = context.get(var, 0)
            return float(actual) > threshold

        elif "<" in condition:
            var, threshold = condition.split("<")
            var = var.strip()
            threshold = float(threshold.strip())
            actual = context.get(var, 0)
            return float(actual) < threshold

        return False

    def execute_rule_actions(self, rule_id: str, context: Dict[str, Any]) -> List[str]:
        """
        Execute actions for a rule

        Returns:
            List of action descriptions that were executed
        """
        rule = next((r for r in self.rules if r.rule_id == rule_id), None)
        if not rule:
            return []

        executed_actions = []
        for action in rule.actions:
            # Parse and execute action
            # In production, this would integrate with payment systems
            executed_actions.append(action)

        return executed_actions

    def check_compliance(self) -> Dict[str, Any]:
        """
        Automated compliance checking

        Returns:
            Compliance report with issues found
        """
        issues = []
        warnings = []

        # Check required fields
        if not self.metadata.parties or len(self.metadata.parties) < 2:
            issues.append("Contract must have at least 2 parties")

        if not self.metadata.effective_date:
            issues.append("Effective date is required")

        # Check payment terms validity
        if self.payment_terms.structure == "tiered_commission":
            if not all([self.payment_terms.tier_1, self.payment_terms.tier_2, self.payment_terms.tier_3]):
                issues.append("Tiered commission requires all 3 tiers defined")

        # Check jurisdiction-specific rules
        if self.metadata.jurisdiction:
            if self.metadata.jurisdiction in ["California", "New York"]:
                # Check specific rules
                if self.payment_terms.due_date.startswith("net_") and int(self.payment_terms.due_date.split("_")[1]) > 60:
                    warnings.append(f"{self.metadata.jurisdiction} recommends payment terms under 60 days")

        # Check service levels are realistic
        for sl in self.service_levels:
            if "24_hours" in sl.target_value and "response_time" in sl.metric_name:
                # This is a reasonable SLA
                pass
            elif "1_hour" in sl.target_value:
                warnings.append(f"Very aggressive SLA: {sl.metric_name} - {sl.target_value}")

        return {
            "is_compliant": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "checked_at": datetime.now().isoformat()
        }

    def to_json_ld(self) -> Dict:
        """
        Export to JSON-LD format for AI engine discovery

        This enables AEO - contracts can be indexed and cited by ChatGPT/Perplexity
        """
        return {
            "@context": "https://schema.org/",
            "@type": "Contract",
            "@id": f"smart402:contract:{self.contract_id}",
            "name": f"{self.metadata.type} - {', '.join(self.metadata.parties)}",
            "contractType": self.metadata.type,
            "parties": [
                {
                    "@type": "Organization",
                    "name": party
                }
                for party in self.metadata.parties
            ],
            "effectiveDate": self.metadata.effective_date,
            "duration": self.metadata.term_duration,
            "paymentTerms": {
                "@type": "PaymentTerms",
                "paymentMethod": self.payment_terms.payment_method,
                "paymentFrequency": self.payment_terms.payment_frequency,
                "paymentDue": self.payment_terms.due_date
            },
            "serviceLevel": [
                {
                    "@type": "ServiceLevelAgreement",
                    "metric": sl.metric_name,
                    "target": sl.target_value
                }
                for sl in self.service_levels
            ],
            "description": self.to_natural_language(),
            "url": f"https://smart402.io/contracts/{self.contract_id}",
            "industry": self.metadata.industry,
            "jurisdiction": self.metadata.jurisdiction
        }


def create_saas_reseller_contract(
    vendor: str,
    reseller: str,
    tier_thresholds: List[float] = [100000, 500000, 1000000],
    tier_rates: List[float] = [0.15, 0.20, 0.25]
) -> SemanticContract:
    """
    Create a SaaS Reseller Agreement (Use Case 1 from Smart402 plan)

    Args:
        vendor: Vendor company name
        reseller: Reseller company name
        tier_thresholds: Revenue thresholds for commission tiers
        tier_rates: Commission rates for each tier

    Returns:
        Semantic contract ready for AI understanding and blockchain deployment
    """
    metadata = ContractMetadata(
        type=ContractType.SaaS_RESELLER.value,
        parties=[vendor, reseller],
        effective_date=datetime.now().strftime("%Y-%m-%d"),
        term_duration="12 months",
        renewal="auto_renew_unless_terminated_30_days_prior",
        industry="SaaS",
        jurisdiction="Delaware"
    )

    payment_terms = PaymentTerms(
        structure=PaymentStructure.TIERED_COMMISSION.value,
        tier_1={"threshold": tier_thresholds[0], "rate": tier_rates[0]},
        tier_2={"threshold": tier_thresholds[1], "rate": tier_rates[1]},
        tier_3={"threshold": tier_thresholds[2], "rate": tier_rates[2]},
        payment_frequency="monthly",
        payment_method="blockchain_automatic",
        due_date="net_30_from_invoice",
        payment_token="USDC",
        settlement_blockchain="Polygon"
    )

    performance_conditions = [
        PerformanceCondition(
            condition_id="uptime_requirement",
            description="Reseller must maintain 99% uptime",
            validation_method="api_monitoring",
            penalty="commission_reduction_5_percent",
            cure_period="7_days"
        )
    ]

    service_levels = [
        ServiceLevel(
            metric_name="response_time",
            target_value="24_hours",
            measurement_source="ticketing_system_api",
            penalty_for_breach="5_percent_discount"
        ),
        ServiceLevel(
            metric_name="resolution_rate",
            target_value="95_percent",
            measurement_source="ticketing_system_api"
        )
    ]

    data_sources = [
        DataSource(
            source_id="monthly_revenue",
            source_url="reseller_api.company.com/revenue",
            authentication="OAuth2_with_contract_id",
            refresh_rate="daily",
            validation_required=True,
            timestamp_validation="+/- 2_hours"
        ),
        DataSource(
            source_id="support_metrics",
            source_url="zendesk_api",
            authentication="API_key",
            refresh_rate="daily",
            validation_required=True,
            timestamp_validation="+/- 2_hours"
        )
    ]

    rules = [
        ContractRule(
            rule_id="automatic_payment_trigger",
            rule_name="Automatic Monthly Commission Payment",
            conditions=[
                "monthly_revenue_reported == true",
                "revenue_amount > 0",
                "account_status == active",
                "last_payment_date > 30_days_ago"
            ],
            actions=[
                "execute_payment(invoice_amount = revenue * commission_rate, days_until_due = 30)"
            ]
        )
    ]

    return SemanticContract(
        metadata=metadata,
        payment_terms=payment_terms,
        performance_conditions=performance_conditions,
        service_levels=service_levels,
        data_sources=data_sources,
        rules=rules
    )
