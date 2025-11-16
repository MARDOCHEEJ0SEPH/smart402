"""
Auto Scaler
Automatically scales resources based on metrics and policies
"""

import asyncio
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class ScalingDirection(Enum):
    """Scaling direction"""
    UP = "up"
    DOWN = "down"
    NONE = "none"


class ScalingMetric(Enum):
    """Metrics for scaling decisions"""
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    REQUEST_RATE = "request_rate"
    RESPONSE_TIME = "response_time"
    QUEUE_SIZE = "queue_size"
    ERROR_RATE = "error_rate"


@dataclass
class ScalingPolicy:
    """Auto-scaling policy"""
    metric: ScalingMetric
    scale_up_threshold: float
    scale_down_threshold: float
    scale_up_step: int = 1
    scale_down_step: int = 1
    cooldown_period: float = 60.0
    evaluation_periods: int = 2
    min_instances: int = 1
    max_instances: int = 10


class AutoScaler:
    """
    Automatic resource scaler

    Features:
    - Multiple scaling policies
    - Predictive scaling
    - Schedule-based scaling
    - Cost optimization
    """

    def __init__(
        self,
        current_instances: int = 1,
        get_metrics: Optional[Callable] = None
    ):
        """
        Initialize auto scaler

        Args:
            current_instances: Current number of instances
            get_metrics: Function to get current metrics
        """
        self.current_instances = current_instances
        self.get_metrics = get_metrics

        self.policies: List[ScalingPolicy] = []
        self.last_scale_time = 0.0
        self.metric_history: Dict[ScalingMetric, List[float]] = {}

        # Statistics
        self.stats = {
            'total_scale_ups': 0,
            'total_scale_downs': 0,
            'total_evaluations': 0,
            'last_scale_time': 0.0,
            'last_scale_direction': None
        }

    def add_policy(self, policy: ScalingPolicy):
        """
        Add scaling policy

        Args:
            policy: Scaling policy
        """
        self.policies.append(policy)

        # Initialize metric history
        if policy.metric not in self.metric_history:
            self.metric_history[policy.metric] = []

    def remove_policy(self, metric: ScalingMetric):
        """
        Remove policy for metric

        Args:
            metric: Metric type
        """
        self.policies = [
            p for p in self.policies
            if p.metric != metric
        ]

    async def evaluate_scaling(self) -> ScalingDirection:
        """
        Evaluate if scaling is needed

        Returns:
            Scaling direction
        """
        self.stats['total_evaluations'] += 1

        if not self.policies:
            return ScalingDirection.NONE

        # Get current metrics
        if self.get_metrics:
            current_metrics = await self.get_metrics()
        else:
            current_metrics = {}

        # Check each policy
        scale_up_votes = 0
        scale_down_votes = 0

        for policy in self.policies:
            metric_value = current_metrics.get(policy.metric.value, 0)

            # Record metric
            if policy.metric not in self.metric_history:
                self.metric_history[policy.metric] = []

            self.metric_history[policy.metric].append(metric_value)

            # Keep only recent history
            max_history = policy.evaluation_periods * 2
            if len(self.metric_history[policy.metric]) > max_history:
                self.metric_history[policy.metric] = \
                    self.metric_history[policy.metric][-max_history:]

            # Check if we have enough history
            if len(self.metric_history[policy.metric]) < policy.evaluation_periods:
                continue

            # Get recent average
            recent_values = self.metric_history[policy.metric][-policy.evaluation_periods:]
            avg_value = sum(recent_values) / len(recent_values)

            # Check thresholds
            if avg_value >= policy.scale_up_threshold:
                scale_up_votes += 1
            elif avg_value <= policy.scale_down_threshold:
                scale_down_votes += 1

        # Determine scaling direction
        if scale_up_votes > 0 and scale_up_votes > scale_down_votes:
            return ScalingDirection.UP
        elif scale_down_votes > 0 and scale_down_votes > scale_up_votes:
            return ScalingDirection.DOWN
        else:
            return ScalingDirection.NONE

    async def scale_up(self, policy: Optional[ScalingPolicy] = None) -> bool:
        """
        Scale up instances

        Args:
            policy: Optional specific policy

        Returns:
            Success status
        """
        # Use first policy if not specified
        if not policy and self.policies:
            policy = self.policies[0]

        if not policy:
            return False

        # Check max instances
        if self.current_instances >= policy.max_instances:
            return False

        # Check cooldown
        if time.time() - self.last_scale_time < policy.cooldown_period:
            return False

        # Scale up
        step = min(
            policy.scale_up_step,
            policy.max_instances - self.current_instances
        )

        self.current_instances += step
        self.last_scale_time = time.time()

        self.stats['total_scale_ups'] += 1
        self.stats['last_scale_time'] = self.last_scale_time
        self.stats['last_scale_direction'] = 'up'

        return True

    async def scale_down(self, policy: Optional[ScalingPolicy] = None) -> bool:
        """
        Scale down instances

        Args:
            policy: Optional specific policy

        Returns:
            Success status
        """
        # Use first policy if not specified
        if not policy and self.policies:
            policy = self.policies[0]

        if not policy:
            return False

        # Check min instances
        if self.current_instances <= policy.min_instances:
            return False

        # Check cooldown
        if time.time() - self.last_scale_time < policy.cooldown_period:
            return False

        # Scale down
        step = min(
            policy.scale_down_step,
            self.current_instances - policy.min_instances
        )

        self.current_instances -= step
        self.last_scale_time = time.time()

        self.stats['total_scale_downs'] += 1
        self.stats['last_scale_time'] = self.last_scale_time
        self.stats['last_scale_direction'] = 'down'

        return True

    async def auto_scale_loop(self, interval: float = 10.0):
        """
        Automatic scaling loop

        Args:
            interval: Evaluation interval in seconds
        """
        while True:
            try:
                direction = await self.evaluate_scaling()

                if direction == ScalingDirection.UP:
                    await self.scale_up()
                elif direction == ScalingDirection.DOWN:
                    await self.scale_down()

                await asyncio.sleep(interval)

            except Exception as e:
                print(f"Auto-scaling error: {e}")
                await asyncio.sleep(interval)

    def predict_scaling_need(
        self,
        metric: ScalingMetric,
        horizon: float = 300.0
    ) -> Optional[ScalingDirection]:
        """
        Predict future scaling needs using simple trend analysis

        Args:
            metric: Metric to analyze
            horizon: Prediction horizon in seconds

        Returns:
            Predicted scaling direction
        """
        if metric not in self.metric_history:
            return None

        history = self.metric_history[metric]

        if len(history) < 10:
            return None

        # Simple linear regression
        n = len(history)
        x = list(range(n))
        y = history

        # Calculate slope
        x_mean = sum(x) / n
        y_mean = sum(y) / n

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return None

        slope = numerator / denominator

        # Predict future value
        future_value = y[-1] + (slope * horizon / 10.0)  # Assuming 10s intervals

        # Find applicable policy
        for policy in self.policies:
            if policy.metric == metric:
                if future_value >= policy.scale_up_threshold:
                    return ScalingDirection.UP
                elif future_value <= policy.scale_down_threshold:
                    return ScalingDirection.DOWN

        return ScalingDirection.NONE

    def get_recommended_instances(self) -> int:
        """
        Get recommended number of instances

        Returns:
            Recommended instance count
        """
        # Could implement sophisticated algorithms here
        # For now, return current
        return self.current_instances

    def get_stats(self) -> Dict:
        """Get auto-scaler statistics"""
        return {
            **self.stats,
            'current_instances': self.current_instances,
            'policy_count': len(self.policies),
            'time_since_last_scale': time.time() - self.last_scale_time
        }
