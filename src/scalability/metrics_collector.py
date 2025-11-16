"""
Metrics Collector
System-wide metrics collection and monitoring
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import asyncio


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Metric:
    """Metric data point"""
    name: str
    type: MetricType
    value: float
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    System-wide metrics collection

    Features:
    - Multiple metric types
    - Time-series data
    - Aggregation
    - Export to monitoring systems
    """

    def __init__(
        self,
        retention_period: float = 3600.0,
        max_samples: int = 10000
    ):
        """
        Initialize metrics collector

        Args:
            retention_period: How long to keep metrics (seconds)
            max_samples: Maximum samples per metric
        """
        self.retention_period = retention_period
        self.max_samples = max_samples

        # Metric storage
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, deque] = {}
        self.summaries: Dict[str, deque] = {}

        # Time-series data
        self.timeseries: Dict[str, deque] = {}

    def increment_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict] = None
    ):
        """
        Increment counter metric

        Args:
            name: Metric name
            value: Increment value
            labels: Optional labels
        """
        key = self._make_key(name, labels)

        if key not in self.counters:
            self.counters[key] = 0

        self.counters[key] += value

        # Record to timeseries
        self._record_timeseries(key, self.counters[key])

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict] = None
    ):
        """
        Set gauge metric

        Args:
            name: Metric name
            value: Current value
            labels: Optional labels
        """
        key = self._make_key(name, labels)
        self.gauges[key] = value

        # Record to timeseries
        self._record_timeseries(key, value)

    def observe_histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict] = None
    ):
        """
        Observe histogram value

        Args:
            name: Metric name
            value: Observed value
            labels: Optional labels
        """
        key = self._make_key(name, labels)

        if key not in self.histograms:
            self.histograms[key] = deque(maxlen=self.max_samples)

        self.histograms[key].append(value)

        # Record to timeseries
        self._record_timeseries(key, value)

    def observe_summary(
        self,
        name: str,
        value: float,
        labels: Optional[Dict] = None
    ):
        """
        Observe summary value

        Args:
            name: Metric name
            value: Observed value
            labels: Optional labels
        """
        key = self._make_key(name, labels)

        if key not in self.summaries:
            self.summaries[key] = deque(maxlen=self.max_samples)

        self.summaries[key].append(value)

        # Record to timeseries
        self._record_timeseries(key, value)

    def get_counter(
        self,
        name: str,
        labels: Optional[Dict] = None
    ) -> float:
        """Get counter value"""
        key = self._make_key(name, labels)
        return self.counters.get(key, 0.0)

    def get_gauge(
        self,
        name: str,
        labels: Optional[Dict] = None
    ) -> Optional[float]:
        """Get gauge value"""
        key = self._make_key(name, labels)
        return self.gauges.get(key)

    def get_histogram_stats(
        self,
        name: str,
        labels: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Get histogram statistics"""
        key = self._make_key(name, labels)

        if key not in self.histograms or not self.histograms[key]:
            return None

        values = list(self.histograms[key])
        values.sort()

        return {
            'count': len(values),
            'sum': sum(values),
            'min': values[0],
            'max': values[-1],
            'mean': sum(values) / len(values),
            'p50': self._percentile(values, 50),
            'p90': self._percentile(values, 90),
            'p95': self._percentile(values, 95),
            'p99': self._percentile(values, 99)
        }

    def _percentile(self, values: List[float], p: int) -> float:
        """Calculate percentile"""
        k = (len(values) - 1) * p / 100
        f = int(k)
        c = f + 1

        if c >= len(values):
            return values[-1]

        d0 = values[f] * (c - k)
        d1 = values[c] * (k - f)

        return d0 + d1

    def _make_key(self, name: str, labels: Optional[Dict] = None) -> str:
        """Generate metric key from name and labels"""
        if not labels:
            return name

        label_str = ",".join(
            f"{k}={v}" for k, v in sorted(labels.items())
        )

        return f"{name}{{{label_str}}}"

    def _record_timeseries(self, key: str, value: float):
        """Record metric to timeseries"""
        if key not in self.timeseries:
            self.timeseries[key] = deque(maxlen=self.max_samples)

        self.timeseries[key].append({
            'value': value,
            'timestamp': time.time()
        })

    def get_timeseries(
        self,
        name: str,
        labels: Optional[Dict] = None,
        duration: Optional[float] = None
    ) -> List[Dict]:
        """
        Get timeseries data

        Args:
            name: Metric name
            labels: Optional labels
            duration: Duration to retrieve (seconds)

        Returns:
            List of timeseries points
        """
        key = self._make_key(name, labels)

        if key not in self.timeseries:
            return []

        data = list(self.timeseries[key])

        if duration:
            cutoff = time.time() - duration
            data = [
                d for d in data
                if d['timestamp'] >= cutoff
            ]

        return data

    async def cleanup_old_metrics(self):
        """Background task to clean up old metrics"""
        while True:
            try:
                cutoff = time.time() - self.retention_period

                # Clean timeseries
                for key in list(self.timeseries.keys()):
                    series = self.timeseries[key]

                    # Remove old entries
                    while series and series[0]['timestamp'] < cutoff:
                        series.popleft()

                    # Remove empty series
                    if not series:
                        del self.timeseries[key]

                await asyncio.sleep(60)  # Cleanup every minute

            except Exception as e:
                print(f"Metrics cleanup error: {e}")
                await asyncio.sleep(60)

    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus format

        Returns:
            Prometheus-formatted metrics
        """
        lines = []

        # Export counters
        for key, value in self.counters.items():
            lines.append(f"{key} {value}")

        # Export gauges
        for key, value in self.gauges.items():
            lines.append(f"{key} {value}")

        return "\n".join(lines)

    def get_all_metrics(self) -> Dict:
        """Get all metrics"""
        return {
            'counters': dict(self.counters),
            'gauges': dict(self.gauges),
            'histograms': {
                k: self.get_histogram_stats(k.split('{')[0])
                for k in self.histograms.keys()
            }
        }
