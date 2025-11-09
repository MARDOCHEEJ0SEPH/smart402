"""
Contract Templates for All Smart402 Use Cases

This module implements all 5 use cases from the Smart402 plan:
1. SaaS Reseller Agreements
2. Vendor Performance SLAs
3. Supply Chain Finance
4. Freelancer Marketplace Contracts
5. Affiliate/Partner Network Agreements
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from src.llmo.semantic_contract import (
    SemanticContract,
    ContractMetadata,
    PaymentTerms,
    PerformanceCondition,
    ServiceLevel,
    DataSource,
    ContractRule,
    ContractType,
    PaymentStructure
)


def create_saas_reseller_contract(
    vendor: str,
    reseller: str,
    tier_thresholds: List[float] = [100000, 500000, 1000000],
    tier_rates: List[float] = [0.15, 0.20, 0.25],
    effective_date: Optional[str] = None
) -> SemanticContract:
    """
    Use Case 1: SaaS Reseller Agreement

    A software vendor uses Smart402 to automate commissions for resellers.
    Tiered commission structure with automatic blockchain payments.

    Args:
        vendor: Vendor company name
        reseller: Reseller company name
        tier_thresholds: Revenue thresholds for commission tiers
        tier_rates: Commission rates for each tier
        effective_date: Contract effective date (defaults to today)

    Returns:
        Semantic contract ready for deployment
    """
    if effective_date is None:
        effective_date = datetime.now().strftime("%Y-%m-%d")

    metadata = ContractMetadata(
        type=ContractType.SaaS_RESELLER.value,
        parties=[vendor, reseller],
        effective_date=effective_date,
        term_duration="12 months",
        renewal="auto_renew_unless_terminated_30_days_prior",
        industry="SaaS",
        jurisdiction="Delaware",
        execution_requirements=["KYC_verification", "wallet_setup", "API_integration"]
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
            description="Reseller must maintain 99% uptime on reseller platform",
            validation_method="api_monitoring",
            measurement_source="uptimerobot_api",
            penalty="commission_reduction_5_percent",
            cure_period="7_days"
        ),
        PerformanceCondition(
            condition_id="support_quality",
            description="Customer satisfaction score must be above 4.0/5.0",
            validation_method="survey_aggregation",
            measurement_source="zendesk_api",
            penalty="warning_first_then_3_percent_reduction",
            cure_period="30_days"
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
            measurement_source="ticketing_system_api",
            penalty_for_breach="3_percent_discount"
        ),
        ServiceLevel(
            metric_name="customer_onboarding_time",
            target_value="72_hours",
            measurement_source="crm_api",
            penalty_for_breach="warning_only"
        )
    ]

    data_sources = [
        DataSource(
            source_id="monthly_revenue",
            source_url="https://reseller-api.company.com/revenue",
            authentication="OAuth2_with_contract_id",
            refresh_rate="daily",
            validation_required=True,
            timestamp_validation="+/- 2_hours"
        ),
        DataSource(
            source_id="support_metrics",
            source_url="https://api.zendesk.com/v2/satisfaction_ratings",
            authentication="API_key",
            refresh_rate="daily",
            validation_required=True,
            timestamp_validation="+/- 2_hours"
        ),
        DataSource(
            source_id="uptime_monitoring",
            source_url="https://api.uptimerobot.com/v2/getMonitors",
            authentication="API_key",
            refresh_rate="hourly",
            validation_required=True,
            timestamp_validation="+/- 1_hour"
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
                "calculate_commission(revenue, tier_rates)",
                "execute_payment(invoice_amount = commission, days_until_due = 30)",
                "send_invoice_email(vendor, reseller, amount, due_date)"
            ]
        ),
        ContractRule(
            rule_id="sla_breach_penalty",
            rule_name="Apply SLA Breach Penalties",
            conditions=[
                "uptime < 0.99",
                "breach_duration > 7_days"
            ],
            actions=[
                "reduce_commission(percentage = 5)",
                "send_warning_notification(reseller)",
                "log_compliance_violation(violation_type = uptime_breach)"
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


def create_vendor_sla_contract(
    vendor: str,
    client: str,
    response_time_hours: int = 24,
    resolution_rate: float = 0.95,
    uptime_target: float = 0.999,
    penalty_per_breach: float = 500.0
) -> SemanticContract:
    """
    Use Case 2: Vendor Performance SLA

    A company contracts with a vendor and needs automatic penalties
    if SLA metrics are not met. Smart402 monitors and enforces automatically.

    Args:
        vendor: Vendor company name
        client: Client company name
        response_time_hours: Maximum response time in hours
        resolution_rate: Minimum resolution rate (0-1)
        uptime_target: Minimum uptime target (0-1)
        penalty_per_breach: Penalty amount per SLA breach

    Returns:
        Semantic contract with SLA monitoring and penalties
    """
    metadata = ContractMetadata(
        type=ContractType.VENDOR_SLA.value,
        parties=[vendor, client],
        effective_date=datetime.now().strftime("%Y-%m-%d"),
        term_duration="12 months",
        renewal="auto_renew_unless_terminated_60_days_prior",
        industry="Technology Services",
        jurisdiction="California",
        execution_requirements=["service_account_setup", "monitoring_integration", "payment_escrow"]
    )

    payment_terms = PaymentTerms(
        structure=PaymentStructure.FIXED_AMOUNT.value,
        tier_1={"threshold": 0, "rate": penalty_per_breach},
        payment_frequency="per_incident",
        payment_method="blockchain_automatic",
        due_date="net_7_from_breach",
        payment_token="USDC",
        settlement_blockchain="Polygon"
    )

    performance_conditions = [
        PerformanceCondition(
            condition_id="response_time_sla",
            description=f"All support tickets must receive initial response within {response_time_hours} hours",
            validation_method="api_monitoring",
            measurement_source="ticketing_system",
            penalty=f"${penalty_per_breach} per breach",
            cure_period="none"
        ),
        PerformanceCondition(
            condition_id="uptime_sla",
            description=f"Service uptime must be at least {uptime_target*100}%",
            validation_method="synthetic_monitoring",
            measurement_source="pingdom_api",
            penalty=f"${penalty_per_breach * 2} per hour of downtime beyond SLA",
            cure_period="immediate"
        ),
        PerformanceCondition(
            condition_id="resolution_rate_sla",
            description=f"At least {resolution_rate*100}% of tickets must be resolved within 7 days",
            validation_method="ticket_analysis",
            measurement_source="ticketing_system",
            penalty=f"${penalty_per_breach} if monthly rate below target",
            cure_period="30_days"
        )
    ]

    service_levels = [
        ServiceLevel(
            metric_name="p1_incident_response",
            target_value="1_hour",
            measurement_source="pagerduty_api",
            penalty_for_breach=f"${penalty_per_breach * 5} per P1 breach"
        ),
        ServiceLevel(
            metric_name="p2_incident_response",
            target_value="4_hours",
            measurement_source="pagerduty_api",
            penalty_for_breach=f"${penalty_per_breach * 2} per P2 breach"
        ),
        ServiceLevel(
            metric_name="monthly_uptime",
            target_value=f"{uptime_target*100}_percent",
            measurement_source="pingdom_api",
            penalty_for_breach=f"${penalty_per_breach * 10} per 0.1% below target"
        )
    ]

    data_sources = [
        DataSource(
            source_id="ticketing_metrics",
            source_url="https://api.zendesk.com/v2/tickets",
            authentication="OAuth2",
            refresh_rate="hourly",
            validation_required=True,
            timestamp_validation="+/- 1_hour"
        ),
        DataSource(
            source_id="uptime_monitoring",
            source_url="https://api.pingdom.com/api/3.1/checks",
            authentication="API_key",
            refresh_rate="5_minutes",
            validation_required=True,
            timestamp_validation="+/- 5_minutes"
        ),
        DataSource(
            source_id="incident_management",
            source_url="https://api.pagerduty.com/incidents",
            authentication="OAuth2",
            refresh_rate="real_time",
            validation_required=True,
            timestamp_validation="+/- 1_minute"
        )
    ]

    rules = [
        ContractRule(
            rule_id="automatic_penalty_trigger",
            rule_name="Automatic SLA Breach Penalty",
            conditions=[
                "sla_breach_detected == true",
                "breach_type in [response_time, uptime, resolution_rate]",
                "vendor_notified == true"
            ],
            actions=[
                "calculate_penalty(breach_type, breach_duration)",
                "execute_payment_from_escrow(amount = penalty)",
                "send_breach_notification(vendor, client, details)",
                "log_sla_breach(timestamp, type, penalty_amount)"
            ]
        ),
        ContractRule(
            rule_id="monthly_sla_report",
            rule_name="Generate Monthly SLA Report",
            conditions=[
                "end_of_month == true"
            ],
            actions=[
                "generate_sla_report(all_metrics)",
                "calculate_total_penalties(month)",
                "send_report_email(vendor, client, report)",
                "update_vendor_score(sla_compliance_rate)"
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


def create_supply_chain_contract(
    supplier: str,
    buyer: str,
    payment_per_unit: float,
    delivery_timeframe_days: int = 30,
    quality_standard: str = "ISO_9001"
) -> SemanticContract:
    """
    Use Case 3: Supply Chain Finance

    Automate supplier payments upon delivery confirmation.
    Payment triggered by IoT sensor data or shipping confirmations.

    Args:
        supplier: Supplier company name
        buyer: Buyer company name
        payment_per_unit: Payment amount per unit
        delivery_timeframe_days: Maximum delivery time in days
        quality_standard: Quality standard requirement

    Returns:
        Semantic contract for supply chain automation
    """
    metadata = ContractMetadata(
        type=ContractType.SUPPLY_CHAIN.value,
        parties=[supplier, buyer],
        effective_date=datetime.now().strftime("%Y-%m-%d"),
        term_duration="24 months",
        renewal="manual_renewal_required",
        industry="Manufacturing",
        jurisdiction="New York",
        execution_requirements=["quality_certification", "insurance_proof", "iot_integration"]
    )

    payment_terms = PaymentTerms(
        structure=PaymentStructure.MILESTONE_BASED.value,
        tier_1={"threshold": 0, "rate": payment_per_unit},
        payment_frequency="per_delivery",
        payment_method="blockchain_automatic",
        due_date="net_7_from_delivery_confirmation",
        payment_token="USDC",
        settlement_blockchain="Ethereum"
    )

    performance_conditions = [
        PerformanceCondition(
            condition_id="delivery_confirmation",
            description="Delivery must be confirmed by buyer or IoT sensors",
            validation_method="iot_sensor_data_or_manual_confirmation",
            measurement_source="shipment_tracking_api",
            penalty="payment_withheld",
            cure_period="immediate"
        ),
        PerformanceCondition(
            condition_id="quality_inspection",
            description=f"Goods must meet {quality_standard} quality standards",
            validation_method="inspection_report",
            measurement_source="quality_inspection_api",
            penalty="10_percent_discount_or_rejection",
            cure_period="14_days_for_replacement"
        ),
        PerformanceCondition(
            condition_id="delivery_timeframe",
            description=f"Delivery within {delivery_timeframe_days} days of order",
            validation_method="timestamp_comparison",
            measurement_source="logistics_api",
            penalty="1_percent_per_day_late",
            cure_period="none"
        )
    ]

    service_levels = [
        ServiceLevel(
            metric_name="on_time_delivery_rate",
            target_value="95_percent",
            measurement_source="logistics_api",
            penalty_for_breach="contract_review_if_below_90_percent"
        ),
        ServiceLevel(
            metric_name="defect_rate",
            target_value="2_percent_max",
            measurement_source="quality_control_api",
            penalty_for_breach="5_percent_discount_on_batch"
        ),
        ServiceLevel(
            metric_name="shipment_accuracy",
            target_value="99_percent",
            measurement_source="inventory_api",
            penalty_for_breach="cost_of_correction"
        )
    ]

    data_sources = [
        DataSource(
            source_id="shipment_tracking",
            source_url="https://api.fedex.com/track/v1/trackingnumbers",
            authentication="API_key",
            refresh_rate="hourly",
            validation_required=True,
            timestamp_validation="+/- 1_hour"
        ),
        DataSource(
            source_id="iot_sensors",
            source_url="https://iot-gateway.company.com/api/shipments",
            authentication="OAuth2",
            refresh_rate="real_time",
            validation_required=True,
            timestamp_validation="+/- 5_minutes"
        ),
        DataSource(
            source_id="quality_inspection",
            source_url="https://qc-system.company.com/api/inspections",
            authentication="API_key",
            refresh_rate="per_delivery",
            validation_required=True,
            timestamp_validation="+/- 1_day"
        )
    ]

    rules = [
        ContractRule(
            rule_id="delivery_payment_trigger",
            rule_name="Automatic Payment on Delivery Confirmation",
            conditions=[
                "delivery_confirmed == true",
                "quality_inspection_passed == true",
                "shipment_matches_order == true"
            ],
            actions=[
                "calculate_payment(quantity * unit_price - penalties)",
                "execute_payment(supplier_wallet, amount)",
                "send_payment_confirmation(supplier, buyer, details)",
                "update_supplier_rating(on_time_delivery)"
            ]
        ),
        ContractRule(
            rule_id="late_delivery_penalty",
            rule_name="Apply Late Delivery Penalties",
            conditions=[
                "delivery_date > order_date + delivery_timeframe_days",
                "days_late > 0"
            ],
            actions=[
                "calculate_late_penalty(days_late * 0.01 * total_amount)",
                "reduce_payment(penalty_amount)",
                "send_penalty_notification(supplier, days_late, penalty)",
                "escalate_if_severely_late(days_late > 14)"
            ]
        ),
        ContractRule(
            rule_id="quality_failure_handling",
            rule_name="Handle Quality Inspection Failures",
            conditions=[
                "quality_inspection_passed == false",
                "defect_rate > acceptable_threshold"
            ],
            actions=[
                "withhold_payment()",
                "request_replacement_or_refund()",
                "send_quality_failure_notification(supplier, defects)",
                "update_supplier_quality_score(defect_rate)"
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


def create_freelancer_contract(
    client: str,
    freelancer: str,
    project_milestones: List[Dict[str, float]],
    total_budget: float,
    deadline_days: int = 30
) -> SemanticContract:
    """
    Use Case 4: Freelancer Marketplace Contract

    Escrow funds released automatically when milestones are approved.
    Automatic payments with multi-sig dispute resolution.

    Args:
        client: Client name
        freelancer: Freelancer name
        project_milestones: List of milestones with percentages
        total_budget: Total project budget
        deadline_days: Project deadline in days

    Returns:
        Semantic contract for freelancer work
    """
    metadata = ContractMetadata(
        type=ContractType.FREELANCER.value,
        parties=[client, freelancer],
        effective_date=datetime.now().strftime("%Y-%m-%d"),
        term_duration=f"{deadline_days} days",
        renewal="none",
        industry="Professional Services",
        jurisdiction="Delaware",
        execution_requirements=["escrow_funding", "milestone_definition", "identity_verification"]
    )

    payment_terms = PaymentTerms(
        structure=PaymentStructure.MILESTONE_BASED.value,
        payment_frequency="per_milestone",
        payment_method="escrow_release",
        due_date="immediate_upon_approval",
        payment_token="USDC",
        settlement_blockchain="Polygon"
    )

    performance_conditions = [
        PerformanceCondition(
            condition_id=f"milestone_{i+1}_completion",
            description=f"Milestone {i+1}: {milestone.get('name', f'Milestone {i+1}')} - {milestone.get('percentage', 0)*100}%",
            validation_method="client_approval",
            measurement_source="platform_api",
            penalty="payment_withheld_until_completion",
            cure_period=f"{milestone.get('cure_days', 7)}_days"
        )
        for i, milestone in enumerate(project_milestones)
    ]

    service_levels = [
        ServiceLevel(
            metric_name="milestone_delivery_time",
            target_value=f"{deadline_days}_days_total",
            measurement_source="platform_api",
            penalty_for_breach="dispute_may_be_opened"
        ),
        ServiceLevel(
            metric_name="communication_responsiveness",
            target_value="24_hours",
            measurement_source="platform_messaging_api",
            penalty_for_breach="warning_only"
        )
    ]

    data_sources = [
        DataSource(
            source_id="milestone_approvals",
            source_url="https://freelancer-platform.com/api/milestones",
            authentication="OAuth2",
            refresh_rate="real_time",
            validation_required=True,
            timestamp_validation="+/- 1_minute"
        ),
        DataSource(
            source_id="work_submissions",
            source_url="https://freelancer-platform.com/api/submissions",
            authentication="OAuth2",
            refresh_rate="real_time",
            validation_required=True,
            timestamp_validation="+/- 1_minute"
        ),
        DataSource(
            source_id="communication_logs",
            source_url="https://freelancer-platform.com/api/messages",
            authentication="OAuth2",
            refresh_rate="hourly",
            validation_required=False,
            timestamp_validation="+/- 1_hour"
        )
    ]

    rules = [
        ContractRule(
            rule_id=f"milestone_{i+1}_payment",
            rule_name=f"Release Payment for Milestone {i+1}",
            conditions=[
                f"milestone_{i+1}_submitted == true",
                f"milestone_{i+1}_approved == true",
                f"previous_milestones_paid == true"
            ],
            actions=[
                f"calculate_milestone_payment(total_budget * {milestone.get('percentage', 0)})",
                "release_from_escrow(freelancer_wallet, milestone_amount)",
                "send_payment_confirmation(client, freelancer, milestone_number)",
                "update_project_progress(milestone_completed)"
            ]
        )
        for i, milestone in enumerate(project_milestones)
    ] + [
        ContractRule(
            rule_id="dispute_resolution",
            rule_name="Handle Milestone Dispute",
            conditions=[
                "dispute_opened == true",
                "milestone_rejected == true",
                "dispute_reason_provided == true"
            ],
            actions=[
                "freeze_escrow()",
                "notify_arbitrator(dispute_details)",
                "request_evidence(client, freelancer)",
                "initiate_multisig_resolution(client, freelancer, arbitrator)"
            ]
        ),
        ContractRule(
            rule_id="project_completion",
            rule_name="Complete Project and Close Contract",
            conditions=[
                "all_milestones_approved == true",
                "all_payments_released == true",
                "final_review_submitted == true"
            ],
            actions=[
                "close_escrow()",
                "update_freelancer_rating(client_rating)",
                "update_client_rating(freelancer_rating)",
                "archive_contract()",
                "send_completion_notifications(client, freelancer)"
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


def create_affiliate_contract(
    merchant: str,
    affiliate: str,
    commission_rate: float = 0.10,
    cookie_duration_days: int = 30,
    minimum_payout: float = 100.0
) -> SemanticContract:
    """
    Use Case 5: Affiliate/Partner Network Agreement

    Affiliate commissions calculated and paid automatically based on
    tracked conversions and sales.

    Args:
        merchant: Merchant company name
        affiliate: Affiliate partner name
        commission_rate: Commission rate (0-1)
        cookie_duration_days: Cookie/attribution window in days
        minimum_payout: Minimum payout threshold

    Returns:
        Semantic contract for affiliate marketing
    """
    metadata = ContractMetadata(
        type=ContractType.AFFILIATE.value,
        parties=[merchant, affiliate],
        effective_date=datetime.now().strftime("%Y-%m-%d"),
        term_duration="12 months",
        renewal="auto_renew_unless_terminated_30_days_prior",
        industry="E-commerce",
        jurisdiction="Delaware",
        execution_requirements=["tracking_link_setup", "payment_threshold_met", "compliance_verification"]
    )

    payment_terms = PaymentTerms(
        structure=PaymentStructure.PERCENTAGE.value,
        tier_1={"threshold": minimum_payout, "rate": commission_rate},
        payment_frequency="monthly",
        payment_method="blockchain_automatic",
        due_date="net_30_from_month_end",
        payment_token="USDC",
        settlement_blockchain="Polygon"
    )

    performance_conditions = [
        PerformanceCondition(
            condition_id="conversion_tracking",
            description="All conversions must be properly tracked and attributed",
            validation_method="tracking_pixel_and_api",
            measurement_source="analytics_api",
            penalty="untracked_sales_not_commissioned",
            cure_period="none"
        ),
        PerformanceCondition(
            condition_id="fraud_prevention",
            description="No fraudulent clicks, fake leads, or invalid traffic",
            validation_method="fraud_detection_ai",
            measurement_source="fraud_detection_api",
            penalty="commission_reversal_and_account_suspension",
            cure_period="none"
        ),
        PerformanceCondition(
            condition_id="minimum_payout_threshold",
            description=f"Minimum ${minimum_payout} in commissions to trigger payment",
            validation_method="balance_check",
            measurement_source="internal_ledger",
            penalty="payment_deferred_to_next_period",
            cure_period="none"
        )
    ]

    service_levels = [
        ServiceLevel(
            metric_name="conversion_rate",
            target_value="2_percent_minimum",
            measurement_source="analytics_api",
            penalty_for_breach="performance_review_if_below_1_percent"
        ),
        ServiceLevel(
            metric_name="traffic_quality_score",
            target_value="80_percent",
            measurement_source="fraud_detection_api",
            penalty_for_breach="account_review_and_possible_termination"
        ),
        ServiceLevel(
            metric_name="brand_compliance",
            target_value="100_percent",
            measurement_source="compliance_monitoring",
            penalty_for_breach="warning_then_suspension"
        )
    ]

    data_sources = [
        DataSource(
            source_id="conversion_tracking",
            source_url="https://analytics.merchant.com/api/conversions",
            authentication="OAuth2",
            refresh_rate="hourly",
            validation_required=True,
            timestamp_validation="+/- 1_hour"
        ),
        DataSource(
            source_id="fraud_detection",
            source_url="https://fraud-detection.service.com/api/check",
            authentication="API_key",
            refresh_rate="real_time",
            validation_required=True,
            timestamp_validation="+/- 5_minutes"
        ),
        DataSource(
            source_id="sales_reconciliation",
            source_url="https://ecommerce.merchant.com/api/orders",
            authentication="OAuth2",
            refresh_rate="daily",
            validation_required=True,
            timestamp_validation="+/- 2_hours"
        )
    ]

    rules = [
        ContractRule(
            rule_id="monthly_commission_payment",
            rule_name="Automatic Monthly Commission Payment",
            conditions=[
                "month_end == true",
                f"total_commissions >= {minimum_payout}",
                "fraud_check_passed == true",
                "no_chargebacks_pending == true"
            ],
            actions=[
                "calculate_total_commissions(conversions, commission_rate)",
                "deduct_chargebacks(if_any)",
                "execute_payment(affiliate_wallet, net_commission)",
                "send_commission_report(affiliate, breakdown)",
                "reset_monthly_counter()"
            ]
        ),
        ContractRule(
            rule_id="conversion_attribution",
            rule_name="Attribute Conversion to Affiliate",
            conditions=[
                "sale_completed == true",
                "affiliate_cookie_present == true",
                f"cookie_age <= {cookie_duration_days}_days",
                "not_attributed_to_other_affiliate == true"
            ],
            actions=[
                "attribute_sale(affiliate_id, sale_amount, timestamp)",
                "calculate_commission(sale_amount * commission_rate)",
                "add_to_monthly_balance(commission)",
                "send_conversion_notification(affiliate, sale_details)"
            ]
        ),
        ContractRule(
            rule_id="fraud_detection_action",
            rule_name="Handle Fraud Detection",
            conditions=[
                "fraud_detected == true",
                "fraud_confidence > 0.8",
                "violation_type in [click_fraud, fake_leads, bot_traffic]"
            ],
            actions=[
                "reverse_fraudulent_commissions()",
                "flag_affiliate_account(fraud_type)",
                "send_fraud_notification(affiliate, evidence)",
                "suspend_account_if_repeat_offender()",
                "update_fraud_score(affiliate)"
            ]
        ),
        ContractRule(
            rule_id="chargeback_handling",
            rule_name="Handle Customer Chargebacks",
            conditions=[
                "chargeback_received == true",
                "sale_was_commissioned == true",
                "commission_not_yet_reversed == true"
            ],
            actions=[
                "reverse_commission(sale_amount * commission_rate)",
                "deduct_from_next_payment(if_already_paid)",
                "send_chargeback_notification(affiliate, details)",
                "update_chargeback_rate(affiliate)"
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


# Template registry for easy access
CONTRACT_TEMPLATES = {
    "saas_reseller": create_saas_reseller_contract,
    "vendor_sla": create_vendor_sla_contract,
    "supply_chain": create_supply_chain_contract,
    "freelancer": create_freelancer_contract,
    "affiliate": create_affiliate_contract
}


def get_template(template_name: str):
    """
    Get contract template by name

    Args:
        template_name: Template name (saas_reseller, vendor_sla, supply_chain, freelancer, affiliate)

    Returns:
        Template function

    Raises:
        ValueError: If template not found
    """
    if template_name not in CONTRACT_TEMPLATES:
        raise ValueError(f"Template '{template_name}' not found. Available: {list(CONTRACT_TEMPLATES.keys())}")

    return CONTRACT_TEMPLATES[template_name]


# Example usage
if __name__ == "__main__":
    # Create SaaS Reseller contract
    saas_contract = create_saas_reseller_contract(
        vendor="CloudCorp Inc.",
        reseller="TechResellers LLC"
    )
    print("SaaS Reseller Contract:")
    print(saas_contract.to_natural_language())
    print("\n" + "="*80 + "\n")

    # Create Vendor SLA contract
    sla_contract = create_vendor_sla_contract(
        vendor="HostingProvider Co.",
        client="Enterprise Corp.",
        penalty_per_breach=1000.0
    )
    print("Vendor SLA Contract:")
    print(sla_contract.to_natural_language())
    print("\n" + "="*80 + "\n")

    # Create Supply Chain contract
    supply_contract = create_supply_chain_contract(
        supplier="ManufacturerX Inc.",
        buyer="RetailChain Corp.",
        payment_per_unit=50.0
    )
    print("Supply Chain Contract:")
    print(supply_contract.to_natural_language())
    print("\n" + "="*80 + "\n")

    # Create Freelancer contract
    freelancer_contract = create_freelancer_contract(
        client="StartupCo",
        freelancer="Jane Developer",
        project_milestones=[
            {"name": "Design mockups", "percentage": 0.25, "cure_days": 7},
            {"name": "Frontend implementation", "percentage": 0.35, "cure_days": 14},
            {"name": "Backend integration", "percentage": 0.25, "cure_days": 14},
            {"name": "Testing and deployment", "percentage": 0.15, "cure_days": 7}
        ],
        total_budget=5000.0,
        deadline_days=45
    )
    print("Freelancer Contract:")
    print(freelancer_contract.to_natural_language())
    print("\n" + "="*80 + "\n")

    # Create Affiliate contract
    affiliate_contract = create_affiliate_contract(
        merchant="OnlineStore Inc.",
        affiliate="MarketingPro LLC",
        commission_rate=0.12,
        minimum_payout=50.0
    )
    print("Affiliate Contract:")
    print(affiliate_contract.to_natural_language())
