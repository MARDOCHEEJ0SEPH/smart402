"""
Oracle Integration for Smart402

This module implements oracle integration for connecting smart contracts
to real-world data sources as specified in the Smart402 plan.

Supports:
- Multiple oracle validation
- Chainlink integration
- Custom API oracles
- IoT sensor data
- Dispute resolution when oracles disagree
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import asyncio
import aiohttp


class OracleType(Enum):
    """Oracle type enumeration"""
    CHAINLINK = "chainlink"
    CUSTOM_API = "custom_api"
    IOT_SENSOR = "iot_sensor"
    MANUAL = "manual"
    HYBRID = "hybrid"


class DataValidationStatus(Enum):
    """Data validation status"""
    VALID = "valid"
    INVALID = "invalid"
    PENDING = "pending"
    DISPUTED = "disputed"
    TIMEOUT = "timeout"


@dataclass
class OracleDataPoint:
    """
    Single data point from an oracle
    """
    oracle_id: str
    oracle_type: OracleType
    data_source: str
    value: Any
    timestamp: datetime
    signature: Optional[str] = None
    confidence: float = 1.0
    validation_status: DataValidationStatus = DataValidationStatus.PENDING

    def is_fresh(self, max_age_seconds: int = 3600) -> bool:
        """
        Check if data point is fresh enough

        Args:
            max_age_seconds: Maximum age in seconds

        Returns:
            True if data is fresh
        """
        age = (datetime.now() - self.timestamp).total_seconds()
        return age <= max_age_seconds

    def verify_signature(self, expected_signer: str) -> bool:
        """
        Verify cryptographic signature of data

        Args:
            expected_signer: Expected signer address

        Returns:
            True if signature valid
        """
        if not self.signature:
            return False

        # In production, this would verify actual cryptographic signature
        # For now, we simulate signature verification
        data_to_sign = f"{self.oracle_id}:{self.value}:{self.timestamp}"
        expected_signature = hashlib.sha256(data_to_sign.encode()).hexdigest()

        return self.signature == expected_signature


@dataclass
class OracleConfig:
    """
    Oracle configuration
    """
    oracle_id: str
    oracle_type: OracleType
    endpoint_url: str
    authentication: Dict[str, str]
    refresh_rate_seconds: int = 3600
    timeout_seconds: int = 30
    retry_attempts: int = 3
    weight: float = 1.0  # Weight for consensus calculation
    is_active: bool = True


class OracleConnector:
    """
    Base oracle connector class
    """

    def __init__(self, config: OracleConfig):
        self.config = config
        self.last_fetch: Optional[datetime] = None
        self.last_value: Optional[Any] = None
        self.error_count: int = 0

    async def fetch_data(self, query: Dict[str, Any]) -> Optional[OracleDataPoint]:
        """
        Fetch data from oracle

        Args:
            query: Query parameters

        Returns:
            OracleDataPoint or None if fetch failed
        """
        raise NotImplementedError("Subclasses must implement fetch_data")

    def should_refresh(self) -> bool:
        """
        Check if data should be refreshed

        Returns:
            True if refresh needed
        """
        if not self.last_fetch:
            return True

        age = (datetime.now() - self.last_fetch).total_seconds()
        return age >= self.config.refresh_rate_seconds


class ChainlinkOracle(OracleConnector):
    """
    Chainlink oracle connector

    Chainlink is a decentralized oracle network that provides
    tamper-proof data feeds for smart contracts.
    """

    async def fetch_data(self, query: Dict[str, Any]) -> Optional[OracleDataPoint]:
        """
        Fetch data from Chainlink oracle

        Args:
            query: Contains 'feed_id' and 'data_key'

        Returns:
            OracleDataPoint with Chainlink data
        """
        feed_id = query.get('feed_id')
        data_key = query.get('data_key')

        try:
            async with aiohttp.ClientSession() as session:
                # In production, this would connect to actual Chainlink node
                # For now, we simulate the response
                url = f"{self.config.endpoint_url}/feeds/{feed_id}"

                async with session.get(url, timeout=self.config.timeout_seconds) as response:
                    if response.status == 200:
                        data = await response.json()

                        value = data.get(data_key)
                        timestamp = datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()))

                        self.last_fetch = datetime.now()
                        self.last_value = value

                        return OracleDataPoint(
                            oracle_id=self.config.oracle_id,
                            oracle_type=OracleType.CHAINLINK,
                            data_source=f"chainlink:{feed_id}",
                            value=value,
                            timestamp=timestamp,
                            signature=data.get('signature'),
                            confidence=0.99,  # Chainlink has high confidence
                            validation_status=DataValidationStatus.VALID
                        )

        except asyncio.TimeoutError:
            self.error_count += 1
            return None
        except Exception as e:
            self.error_count += 1
            print(f"Chainlink oracle error: {e}")
            return None

        return None


class CustomAPIOracle(OracleConnector):
    """
    Custom API oracle connector

    Connects to custom APIs (Stripe, Zendesk, etc.) for
    business-specific data.
    """

    async def fetch_data(self, query: Dict[str, Any]) -> Optional[OracleDataPoint]:
        """
        Fetch data from custom API

        Args:
            query: API-specific query parameters

        Returns:
            OracleDataPoint with API data
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = self.config.authentication.copy()

                async with session.get(
                    self.config.endpoint_url,
                    headers=headers,
                    params=query,
                    timeout=self.config.timeout_seconds
                ) as response:

                    if response.status == 200:
                        data = await response.json()

                        # Extract value from response
                        value = self._extract_value(data, query.get('value_path', 'value'))

                        self.last_fetch = datetime.now()
                        self.last_value = value

                        # Generate signature for data integrity
                        data_to_sign = f"{self.config.oracle_id}:{value}:{self.last_fetch}"
                        signature = hashlib.sha256(data_to_sign.encode()).hexdigest()

                        return OracleDataPoint(
                            oracle_id=self.config.oracle_id,
                            oracle_type=OracleType.CUSTOM_API,
                            data_source=self.config.endpoint_url,
                            value=value,
                            timestamp=self.last_fetch,
                            signature=signature,
                            confidence=0.95,
                            validation_status=DataValidationStatus.VALID
                        )

        except asyncio.TimeoutError:
            self.error_count += 1
            return None
        except Exception as e:
            self.error_count += 1
            print(f"Custom API oracle error: {e}")
            return None

        return None

    def _extract_value(self, data: Dict, path: str) -> Any:
        """
        Extract value from nested dictionary using dot notation

        Args:
            data: Response data
            path: Dot-separated path (e.g., 'metrics.revenue.total')

        Returns:
            Extracted value
        """
        keys = path.split('.')
        value = data

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None

        return value


class IoTSensorOracle(OracleConnector):
    """
    IoT sensor oracle connector

    Connects to IoT devices for real-time sensor data
    (temperature, GPS location, delivery confirmation, etc.)
    """

    async def fetch_data(self, query: Dict[str, Any]) -> Optional[OracleDataPoint]:
        """
        Fetch data from IoT sensor

        Args:
            query: Contains 'sensor_id' and 'metric'

        Returns:
            OracleDataPoint with sensor data
        """
        sensor_id = query.get('sensor_id')
        metric = query.get('metric')

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.config.endpoint_url}/sensors/{sensor_id}/{metric}"

                async with session.get(url, timeout=self.config.timeout_seconds) as response:
                    if response.status == 200:
                        data = await response.json()

                        value = data.get('value')
                        timestamp = datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()))

                        self.last_fetch = datetime.now()
                        self.last_value = value

                        return OracleDataPoint(
                            oracle_id=self.config.oracle_id,
                            oracle_type=OracleType.IOT_SENSOR,
                            data_source=f"iot:{sensor_id}:{metric}",
                            value=value,
                            timestamp=timestamp,
                            signature=data.get('signature'),
                            confidence=0.90,
                            validation_status=DataValidationStatus.VALID
                        )

        except asyncio.TimeoutError:
            self.error_count += 1
            return None
        except Exception as e:
            self.error_count += 1
            print(f"IoT sensor oracle error: {e}")
            return None

        return None


@dataclass
class OracleConsensus:
    """
    Multi-oracle consensus result
    """
    data_points: List[OracleDataPoint]
    consensus_value: Any
    confidence: float
    disagreement_detected: bool
    timestamp: datetime = field(default_factory=datetime.now)

    def get_outliers(self) -> List[OracleDataPoint]:
        """
        Get oracle data points that disagree with consensus

        Returns:
            List of outlier data points
        """
        outliers = []

        for dp in self.data_points:
            if dp.value != self.consensus_value:
                # Check if difference is significant
                try:
                    if abs(float(dp.value) - float(self.consensus_value)) / float(self.consensus_value) > 0.05:
                        outliers.append(dp)
                except (ValueError, TypeError, ZeroDivisionError):
                    # Non-numeric comparison
                    if dp.value != self.consensus_value:
                        outliers.append(dp)

        return outliers


class OracleAggregator:
    """
    Aggregates data from multiple oracles and calculates consensus

    As specified in Smart402 plan:
    - Fetch from multiple oracles
    - Calculate weighted consensus
    - Detect disagreements
    - Trigger dispute resolution if needed
    """

    def __init__(self, oracles: List[OracleConnector], min_oracles: int = 2):
        self.oracles = oracles
        self.min_oracles = min_oracles
        self.consensus_history: List[OracleConsensus] = []

    async def fetch_consensus(self, query: Dict[str, Any]) -> Optional[OracleConsensus]:
        """
        Fetch data from all oracles and calculate consensus

        Args:
            query: Query parameters for oracles

        Returns:
            OracleConsensus with aggregated result
        """
        # Fetch from all oracles concurrently
        tasks = [oracle.fetch_data(query) for oracle in self.oracles if oracle.config.is_active]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out failures and exceptions
        data_points = [r for r in results if isinstance(r, OracleDataPoint) and r is not None]

        if len(data_points) < self.min_oracles:
            print(f"Not enough oracles responded ({len(data_points)} < {self.min_oracles})")
            return None

        # Calculate consensus
        consensus = self._calculate_consensus(data_points)

        # Store in history
        self.consensus_history.append(consensus)

        return consensus

    def _calculate_consensus(self, data_points: List[OracleDataPoint]) -> OracleConsensus:
        """
        Calculate consensus value from multiple oracle data points

        Uses weighted median for numeric values, majority vote for categorical

        Args:
            data_points: List of oracle data points

        Returns:
            OracleConsensus result
        """
        if not data_points:
            return OracleConsensus(
                data_points=[],
                consensus_value=None,
                confidence=0.0,
                disagreement_detected=True
            )

        # Check if numeric values
        try:
            numeric_values = [(float(dp.value), dp.confidence * self.oracles[i].config.weight)
                            for i, dp in enumerate(data_points)]

            # Weighted median
            sorted_values = sorted(numeric_values, key=lambda x: x[0])
            total_weight = sum(w for _, w in sorted_values)

            cumulative_weight = 0
            consensus_value = sorted_values[0][0]

            for value, weight in sorted_values:
                cumulative_weight += weight
                if cumulative_weight >= total_weight / 2:
                    consensus_value = value
                    break

            # Calculate confidence (higher if values agree)
            value_range = max(v for v, _ in numeric_values) - min(v for v, _ in numeric_values)
            median_value = sorted_values[len(sorted_values)//2][0]
            disagreement = value_range / median_value if median_value != 0 else 0

            confidence = 1.0 - min(disagreement, 1.0)
            disagreement_detected = disagreement > 0.05  # 5% threshold

        except (ValueError, TypeError):
            # Categorical values - use majority vote
            value_counts: Dict[Any, float] = {}

            for i, dp in enumerate(data_points):
                weight = dp.confidence * self.oracles[i].config.weight
                value_counts[dp.value] = value_counts.get(dp.value, 0) + weight

            consensus_value = max(value_counts, key=value_counts.get)
            total_weight = sum(value_counts.values())
            confidence = value_counts[consensus_value] / total_weight if total_weight > 0 else 0

            # Disagreement if no clear majority (>80%)
            disagreement_detected = confidence < 0.8

        return OracleConsensus(
            data_points=data_points,
            consensus_value=consensus_value,
            confidence=confidence,
            disagreement_detected=disagreement_detected
        )

    def get_oracle_accuracy(self, oracle_id: str, lookback_count: int = 10) -> float:
        """
        Calculate oracle accuracy based on historical consensus

        Args:
            oracle_id: Oracle ID
            lookback_count: Number of recent consensus results to check

        Returns:
            Accuracy score (0-1)
        """
        recent_consensus = self.consensus_history[-lookback_count:]

        if not recent_consensus:
            return 1.0  # No history, assume perfect

        matches = 0
        total = 0

        for consensus in recent_consensus:
            for dp in consensus.data_points:
                if dp.oracle_id == oracle_id:
                    total += 1
                    if dp.value == consensus.consensus_value:
                        matches += 1

        return matches / total if total > 0 else 1.0


class DisputeResolver:
    """
    Resolves disputes when oracles disagree

    As specified in Smart402 plan:
    - Escalate to manual review
    - Apply oracle reputation scores
    - Penalize consistently inaccurate oracles
    """

    def __init__(self, aggregator: OracleAggregator):
        self.aggregator = aggregator
        self.disputes: List[Dict[str, Any]] = []

    async def resolve_dispute(
        self,
        consensus: OracleConsensus,
        resolution_method: str = "weighted_majority"
    ) -> Dict[str, Any]:
        """
        Resolve dispute between oracles

        Args:
            consensus: OracleConsensus with disagreement
            resolution_method: Method to use (weighted_majority, manual, arbitrator)

        Returns:
            Resolution result
        """
        if not consensus.disagreement_detected:
            return {
                'resolution_needed': False,
                'consensus_value': consensus.consensus_value,
                'confidence': consensus.confidence
            }

        dispute_id = hashlib.sha256(f"{datetime.now()}:{consensus.timestamp}".encode()).hexdigest()[:16]

        outliers = consensus.get_outliers()

        dispute_record = {
            'dispute_id': dispute_id,
            'timestamp': datetime.now(),
            'consensus_value': consensus.consensus_value,
            'outlier_values': [dp.value for dp in outliers],
            'outlier_oracles': [dp.oracle_id for dp in outliers],
            'resolution_method': resolution_method,
            'status': 'pending'
        }

        if resolution_method == "weighted_majority":
            # Use consensus value (already weighted)
            dispute_record['resolved_value'] = consensus.consensus_value
            dispute_record['status'] = 'resolved_automatic'

        elif resolution_method == "manual":
            # Flag for manual review
            dispute_record['status'] = 'pending_manual_review'
            dispute_record['resolved_value'] = None

        elif resolution_method == "arbitrator":
            # Send to arbitrator oracle
            dispute_record['status'] = 'pending_arbitrator'
            dispute_record['resolved_value'] = None

        # Penalize inaccurate oracles
        for outlier in outliers:
            oracle = next((o for o in self.aggregator.oracles if o.config.oracle_id == outlier.oracle_id), None)
            if oracle:
                # Reduce weight for consistently inaccurate oracles
                accuracy = self.aggregator.get_oracle_accuracy(outlier.oracle_id)
                if accuracy < 0.80:
                    oracle.config.weight *= 0.9  # Reduce weight by 10%
                    dispute_record['penalties'] = dispute_record.get('penalties', [])
                    dispute_record['penalties'].append({
                        'oracle_id': outlier.oracle_id,
                        'accuracy': accuracy,
                        'new_weight': oracle.config.weight
                    })

        self.disputes.append(dispute_record)

        return dispute_record


# Example usage
if __name__ == "__main__":
    async def main():
        # Create oracle configurations
        chainlink_config = OracleConfig(
            oracle_id="chainlink_eth_usd",
            oracle_type=OracleType.CHAINLINK,
            endpoint_url="https://api.chain.link",
            authentication={},
            refresh_rate_seconds=300,
            weight=1.5  # Higher weight for Chainlink
        )

        api_config = OracleConfig(
            oracle_id="stripe_revenue",
            oracle_type=OracleType.CUSTOM_API,
            endpoint_url="https://api.stripe.com/v1/revenue",
            authentication={"Authorization": "Bearer sk_test_..."},
            refresh_rate_seconds=3600,
            weight=1.0
        )

        iot_config = OracleConfig(
            oracle_id="delivery_sensor",
            oracle_type=OracleType.IOT_SENSOR,
            endpoint_url="https://iot-gateway.company.com",
            authentication={"API-Key": "..."},
            refresh_rate_seconds=60,
            weight=1.2
        )

        # Create oracle connectors
        oracles = [
            ChainlinkOracle(chainlink_config),
            CustomAPIOracle(api_config),
            IoTSensorOracle(iot_config)
        ]

        # Create aggregator
        aggregator = OracleAggregator(oracles, min_oracles=2)

        # Fetch consensus
        query = {
            'feed_id': 'ETH_USD',
            'data_key': 'price'
        }

        consensus = await aggregator.fetch_consensus(query)

        if consensus:
            print(f"Consensus value: {consensus.consensus_value}")
            print(f"Confidence: {consensus.confidence:.2%}")
            print(f"Disagreement: {consensus.disagreement_detected}")

            if consensus.disagreement_detected:
                resolver = DisputeResolver(aggregator)
                resolution = await resolver.resolve_dispute(consensus)
                print(f"Dispute resolution: {resolution}")

    # Run example
    asyncio.run(main())
