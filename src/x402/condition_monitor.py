"""
Automatic Condition Monitoring Agent

This module implements the automatic condition monitoring agent
as specified in the Smart402 plan.

The agent:
- Continuously monitors contract conditions
- Fetches data from oracles
- Evaluates payment conditions
- Triggers payments when all conditions met
- Handles failures and retries with exponential backoff
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging

from src.x402.http_protocol import PaymentCondition, PaymentFlow, X402Protocol, PaymentStatus
from src.oracle.integration import OracleAggregator, OracleConsensus, OracleConnector


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitoringFrequency(Enum):
    """Monitoring frequency options"""
    REAL_TIME = "real_time"  # Every few seconds
    HIGH = "high"  # Every minute
    MEDIUM = "medium"  # Every 5 minutes
    LOW = "low"  # Every hour
    DAILY = "daily"  # Once per day


@dataclass
class MonitoringJob:
    """
    Monitoring job for a contract
    """
    job_id: str
    contract_id: str
    payment_flow: PaymentFlow
    oracle_aggregator: OracleAggregator
    frequency: MonitoringFrequency
    is_active: bool = True
    last_check: Optional[datetime] = None
    next_check: Optional[datetime] = None
    check_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    retry_count: int = 0
    max_retries: int = 5
    backoff_multiplier: float = 2.0

    def should_check_now(self) -> bool:
        """
        Determine if condition should be checked now

        Returns:
            True if check is due
        """
        if not self.is_active:
            return False

        if self.next_check is None:
            return True

        return datetime.now() >= self.next_check

    def calculate_next_check(self) -> datetime:
        """
        Calculate next check time based on frequency

        Returns:
            Next check datetime
        """
        now = datetime.now()

        if self.frequency == MonitoringFrequency.REAL_TIME:
            return now + timedelta(seconds=5)
        elif self.frequency == MonitoringFrequency.HIGH:
            return now + timedelta(minutes=1)
        elif self.frequency == MonitoringFrequency.MEDIUM:
            return now + timedelta(minutes=5)
        elif self.frequency == MonitoringFrequency.LOW:
            return now + timedelta(hours=1)
        elif self.frequency == MonitoringFrequency.DAILY:
            return now + timedelta(days=1)
        else:
            return now + timedelta(minutes=5)

    def calculate_retry_delay(self) -> float:
        """
        Calculate retry delay with exponential backoff

        Returns:
            Delay in seconds
        """
        if self.retry_count == 0:
            return 2.0  # Initial 2 second delay

        # Exponential backoff: 2s, 4s, 8s, 16s, 32s
        delay = 2.0 * (self.backoff_multiplier ** (self.retry_count - 1))

        # Cap at 60 seconds
        return min(delay, 60.0)


@dataclass
class ConditionCheckResult:
    """
    Result of condition checking
    """
    job_id: str
    contract_id: str
    timestamp: datetime
    all_conditions_met: bool
    condition_results: Dict[str, bool]
    oracle_data: Dict[str, Any]
    payment_triggered: bool = False
    payment_result: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)


class ConditionMonitoringAgent:
    """
    Automatic condition monitoring agent

    Monitors contracts continuously and triggers payments
    when all conditions are satisfied.

    As specified in Smart402 plan:
    1. Monitor oracle data sources
    2. Evaluate contract conditions
    3. Trigger payment when all conditions met
    4. Handle failures with exponential backoff
    5. Send webhook notifications
    """

    def __init__(
        self,
        x402_protocol: X402Protocol,
        default_frequency: MonitoringFrequency = MonitoringFrequency.MEDIUM
    ):
        self.x402_protocol = x402_protocol
        self.default_frequency = default_frequency
        self.monitoring_jobs: Dict[str, MonitoringJob] = {}
        self.check_results: List[ConditionCheckResult] = []
        self.is_running = False
        self.task: Optional[asyncio.Task] = None

    def register_contract(
        self,
        contract_id: str,
        payment_flow: PaymentFlow,
        oracle_aggregator: OracleAggregator,
        frequency: Optional[MonitoringFrequency] = None
    ) -> str:
        """
        Register contract for automatic monitoring

        Args:
            contract_id: Contract ID
            payment_flow: PaymentFlow object
            oracle_aggregator: OracleAggregator for data fetching
            frequency: Monitoring frequency

        Returns:
            Job ID
        """
        import hashlib

        job_id = hashlib.sha256(f"{contract_id}:{datetime.now()}".encode()).hexdigest()[:16]

        job = MonitoringJob(
            job_id=job_id,
            contract_id=contract_id,
            payment_flow=payment_flow,
            oracle_aggregator=oracle_aggregator,
            frequency=frequency or self.default_frequency,
            next_check=datetime.now()  # Check immediately
        )

        self.monitoring_jobs[job_id] = job

        logger.info(f"Registered contract {contract_id} for monitoring (job_id: {job_id})")

        return job_id

    def unregister_contract(self, job_id: str) -> bool:
        """
        Stop monitoring a contract

        Args:
            job_id: Job ID

        Returns:
            True if unregistered successfully
        """
        if job_id in self.monitoring_jobs:
            self.monitoring_jobs[job_id].is_active = False
            del self.monitoring_jobs[job_id]
            logger.info(f"Unregistered monitoring job {job_id}")
            return True

        return False

    async def check_conditions(self, job: MonitoringJob) -> ConditionCheckResult:
        """
        Check all conditions for a contract

        Args:
            job: MonitoringJob to check

        Returns:
            ConditionCheckResult
        """
        result = ConditionCheckResult(
            job_id=job.job_id,
            contract_id=job.contract_id,
            timestamp=datetime.now(),
            all_conditions_met=False,
            condition_results={},
            oracle_data={}
        )

        try:
            # Fetch oracle data
            oracle_queries = self._build_oracle_queries(job.payment_flow.conditions)

            for query_key, query in oracle_queries.items():
                try:
                    consensus = await job.oracle_aggregator.fetch_consensus(query)

                    if consensus:
                        result.oracle_data[query_key] = consensus.consensus_value
                    else:
                        result.errors.append(f"Failed to fetch oracle data for {query_key}")

                except Exception as e:
                    result.errors.append(f"Oracle error for {query_key}: {str(e)}")

            # Evaluate conditions
            all_met = True

            for condition in job.payment_flow.conditions:
                is_met = condition.evaluate(result.oracle_data)
                result.condition_results[condition.condition_id] = is_met

                if not is_met:
                    all_met = False

            result.all_conditions_met = all_met

            # If all conditions met, trigger payment
            if all_met and job.payment_flow.status == PaymentStatus.PENDING:
                logger.info(f"All conditions met for contract {job.contract_id}, triggering payment")

                # Update payment flow status
                job.payment_flow.status = PaymentStatus.CONDITIONS_MET

                # Trigger payment
                payment_result = job.payment_flow.initiate_payment(
                    settlement_address=f"0x{job.contract_id}_settlement"
                )

                result.payment_triggered = True
                result.payment_result = payment_result

                # Send webhook notification
                webhook_url = f"https://webhook.contract.io/{job.contract_id}"
                job.payment_flow.send_webhook_notification(
                    webhook_url=webhook_url,
                    event="payment_initiated",
                    data=payment_result
                )

                logger.info(f"Payment initiated for contract {job.contract_id}: {payment_result['tx_hash']}")

            job.success_count += 1
            job.retry_count = 0  # Reset retry count on success

        except Exception as e:
            result.errors.append(f"Condition check error: {str(e)}")
            job.failure_count += 1
            job.retry_count += 1
            logger.error(f"Error checking conditions for {job.contract_id}: {e}")

        finally:
            job.last_check = datetime.now()
            job.check_count += 1

        # Store result
        self.check_results.append(result)

        # Keep only last 1000 results
        if len(self.check_results) > 1000:
            self.check_results = self.check_results[-1000:]

        return result

    def _build_oracle_queries(self, conditions: List[PaymentCondition]) -> Dict[str, Dict[str, Any]]:
        """
        Build oracle queries from payment conditions

        Args:
            conditions: List of payment conditions

        Returns:
            Dictionary of oracle queries
        """
        queries = {}

        for condition in conditions:
            # Map condition data source to oracle query
            if condition.data_source == "reseller_api":
                queries[condition.condition_id] = {
                    'value_path': 'revenue.monthly_total',
                    'metric': condition.condition_id
                }
            elif condition.data_source == "monitoring_api":
                queries[condition.condition_id] = {
                    'value_path': 'uptime.percentage',
                    'metric': condition.condition_id
                }
            elif condition.data_source == "ticketing_system":
                queries[condition.condition_id] = {
                    'value_path': 'metrics.response_time',
                    'metric': condition.condition_id
                }
            else:
                # Generic query
                queries[condition.condition_id] = {
                    'value_path': 'value',
                    'metric': condition.condition_id
                }

        return queries

    async def monitoring_loop(self):
        """
        Main monitoring loop

        Continuously checks all active monitoring jobs
        """
        logger.info("Starting condition monitoring loop")

        while self.is_running:
            try:
                # Get jobs that need checking
                jobs_to_check = [
                    job for job in self.monitoring_jobs.values()
                    if job.should_check_now()
                ]

                if jobs_to_check:
                    logger.info(f"Checking {len(jobs_to_check)} contracts")

                    # Check all jobs concurrently
                    check_tasks = [self.check_conditions(job) for job in jobs_to_check]
                    results = await asyncio.gather(*check_tasks, return_exceptions=True)

                    # Update next check times
                    for job in jobs_to_check:
                        if job.retry_count > 0 and job.retry_count < job.max_retries:
                            # Use exponential backoff for retries
                            delay = job.calculate_retry_delay()
                            job.next_check = datetime.now() + timedelta(seconds=delay)
                            logger.info(f"Scheduling retry for {job.contract_id} in {delay}s")
                        else:
                            # Normal schedule
                            job.next_check = job.calculate_next_check()

                        # Disable job if too many retries
                        if job.retry_count >= job.max_retries:
                            logger.error(f"Max retries exceeded for {job.contract_id}, disabling job")
                            job.is_active = False

                # Sleep for a short time
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Back off on error

        logger.info("Condition monitoring loop stopped")

    def start(self):
        """
        Start the monitoring agent
        """
        if self.is_running:
            logger.warning("Monitoring agent already running")
            return

        self.is_running = True
        self.task = asyncio.create_task(self.monitoring_loop())
        logger.info("Condition monitoring agent started")

    async def stop(self):
        """
        Stop the monitoring agent
        """
        if not self.is_running:
            logger.warning("Monitoring agent not running")
            return

        logger.info("Stopping condition monitoring agent")
        self.is_running = False

        if self.task:
            await self.task

        logger.info("Condition monitoring agent stopped")

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of monitoring job

        Args:
            job_id: Job ID

        Returns:
            Job status dictionary
        """
        if job_id not in self.monitoring_jobs:
            return None

        job = self.monitoring_jobs[job_id]

        return {
            'job_id': job.job_id,
            'contract_id': job.contract_id,
            'is_active': job.is_active,
            'frequency': job.frequency.value,
            'last_check': job.last_check.isoformat() if job.last_check else None,
            'next_check': job.next_check.isoformat() if job.next_check else None,
            'check_count': job.check_count,
            'success_count': job.success_count,
            'failure_count': job.failure_count,
            'retry_count': job.retry_count,
            'payment_status': job.payment_flow.status.value,
            'conditions_summary': {
                'total': len(job.payment_flow.conditions),
                'met': sum(1 for c in job.payment_flow.conditions if c.is_met)
            }
        }

    def get_all_jobs_status(self) -> List[Dict[str, Any]]:
        """
        Get status of all monitoring jobs

        Returns:
            List of job status dictionaries
        """
        return [self.get_job_status(job_id) for job_id in self.monitoring_jobs.keys()]

    def get_recent_results(self, count: int = 10) -> List[ConditionCheckResult]:
        """
        Get recent condition check results

        Args:
            count: Number of results to return

        Returns:
            List of recent results
        """
        return self.check_results[-count:]


# Example usage
if __name__ == "__main__":
    async def main():
        from src.oracle.integration import CustomAPIOracle, OracleConfig, OracleType

        # Create X402 protocol
        protocol = X402Protocol()

        # Create payment flow
        conditions = [
            PaymentCondition(
                condition_id="monthly_revenue_reported",
                description="Monthly revenue has been reported",
                data_source="reseller_api",
                validation_method="boolean",
                expected_value=True
            ),
            PaymentCondition(
                condition_id="revenue_amount",
                description="Revenue exceeds minimum threshold",
                data_source="reseller_api",
                validation_method="greater_than",
                expected_value=100000
            )
        ]

        payment_flow = protocol.create_payment_flow(
            contract_id="test_contract_001",
            conditions=conditions,
            payment_amount=15000,
            payment_token="USDC"
        )

        # Create oracle
        oracle_config = OracleConfig(
            oracle_id="test_oracle",
            oracle_type=OracleType.CUSTOM_API,
            endpoint_url="https://api.test.com/data",
            authentication={"Authorization": "Bearer test"},
            refresh_rate_seconds=300
        )

        oracle = CustomAPIOracle(oracle_config)
        from src.oracle.integration import OracleAggregator
        aggregator = OracleAggregator([oracle], min_oracles=1)

        # Create monitoring agent
        agent = ConditionMonitoringAgent(protocol, MonitoringFrequency.HIGH)

        # Register contract
        job_id = agent.register_contract(
            contract_id="test_contract_001",
            payment_flow=payment_flow,
            oracle_aggregator=aggregator,
            frequency=MonitoringFrequency.HIGH
        )

        print(f"Registered monitoring job: {job_id}")

        # Start agent
        agent.start()

        # Run for 10 seconds
        await asyncio.sleep(10)

        # Check status
        status = agent.get_job_status(job_id)
        print(f"Job status: {status}")

        # Stop agent
        await agent.stop()

    asyncio.run(main())
