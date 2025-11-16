"""
Load Balancer
Distributes requests across multiple instances with health checking
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import random
import hashlib


class LoadBalancingStrategy(Enum):
    """Load balancing algorithms"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    RANDOM = "random"
    IP_HASH = "ip_hash"
    ADAPTIVE = "adaptive"


@dataclass
class Backend:
    """Backend server instance"""
    id: str
    host: str
    port: int
    weight: int = 1
    is_healthy: bool = True
    active_connections: int = 0
    total_requests: int = 0
    total_errors: int = 0
    response_times: List[float] = None
    max_response_times: int = 100

    def __post_init__(self):
        if self.response_times is None:
            self.response_times = []

    @property
    def avg_response_time(self) -> float:
        """Get average response time"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)

    @property
    def error_rate(self) -> float:
        """Get error rate"""
        if self.total_requests == 0:
            return 0.0
        return self.total_errors / self.total_requests

    def record_response(self, response_time: float, success: bool):
        """Record request response"""
        self.total_requests += 1

        if not success:
            self.total_errors += 1

        # Keep last N response times
        self.response_times.append(response_time)
        if len(self.response_times) > self.max_response_times:
            self.response_times.pop(0)


class LoadBalancer:
    """
    Load balancer with multiple strategies and health checking

    Features:
    - Multiple load balancing algorithms
    - Health checking with circuit breaker
    - Connection tracking
    - Performance metrics
    - Automatic failover
    - Sticky sessions
    """

    def __init__(
        self,
        strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN,
        health_check_interval: float = 5.0,
        health_check_timeout: float = 2.0,
        max_failures: int = 3
    ):
        """
        Initialize load balancer

        Args:
            strategy: Load balancing strategy
            health_check_interval: Health check frequency in seconds
            health_check_timeout: Health check timeout
            max_failures: Max failures before marking unhealthy
        """
        self.strategy = strategy
        self.health_check_interval = health_check_interval
        self.health_check_timeout = health_check_timeout
        self.max_failures = max_failures

        self.backends: Dict[str, Backend] = {}
        self.current_index = 0  # For round-robin
        self.sticky_sessions: Dict[str, str] = {}  # session_id -> backend_id

        # Health check tracking
        self.failure_counts: Dict[str, int] = {}

        # Statistics
        self.stats = {
            'total_requests': 0,
            'total_errors': 0,
            'backend_failures': 0
        }

    def add_backend(
        self,
        backend_id: str,
        host: str,
        port: int,
        weight: int = 1
    ):
        """
        Add backend server

        Args:
            backend_id: Unique backend identifier
            host: Backend host
            port: Backend port
            weight: Weight for weighted strategies
        """
        backend = Backend(
            id=backend_id,
            host=host,
            port=port,
            weight=weight
        )

        self.backends[backend_id] = backend
        self.failure_counts[backend_id] = 0

    def remove_backend(self, backend_id: str):
        """
        Remove backend server

        Args:
            backend_id: Backend identifier
        """
        if backend_id in self.backends:
            del self.backends[backend_id]
            del self.failure_counts[backend_id]

            # Clean up sticky sessions
            self.sticky_sessions = {
                k: v for k, v in self.sticky_sessions.items()
                if v != backend_id
            }

    def get_backend(
        self,
        session_id: Optional[str] = None,
        client_ip: Optional[str] = None
    ) -> Optional[Backend]:
        """
        Select backend based on strategy

        Args:
            session_id: Optional session ID for sticky sessions
            client_ip: Optional client IP for IP hash

        Returns:
            Selected backend or None
        """
        # Check sticky session
        if session_id and session_id in self.sticky_sessions:
            backend_id = self.sticky_sessions[session_id]
            backend = self.backends.get(backend_id)
            if backend and backend.is_healthy:
                return backend

        # Get healthy backends
        healthy_backends = [
            b for b in self.backends.values()
            if b.is_healthy
        ]

        if not healthy_backends:
            return None

        # Select based on strategy
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            backend = self._round_robin(healthy_backends)

        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            backend = self._weighted_round_robin(healthy_backends)

        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            backend = self._least_connections(healthy_backends)

        elif self.strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
            backend = self._least_response_time(healthy_backends)

        elif self.strategy == LoadBalancingStrategy.RANDOM:
            backend = random.choice(healthy_backends)

        elif self.strategy == LoadBalancingStrategy.IP_HASH:
            backend = self._ip_hash(healthy_backends, client_ip or "")

        else:  # ADAPTIVE
            backend = self._adaptive(healthy_backends)

        # Save sticky session
        if session_id and backend:
            self.sticky_sessions[session_id] = backend.id

        return backend

    def _round_robin(self, backends: List[Backend]) -> Backend:
        """Round-robin selection"""
        backend = backends[self.current_index % len(backends)]
        self.current_index += 1
        return backend

    def _weighted_round_robin(self, backends: List[Backend]) -> Backend:
        """Weighted round-robin selection"""
        # Calculate total weight
        total_weight = sum(b.weight for b in backends)

        # Select based on weight
        rand_weight = random.uniform(0, total_weight)
        cumulative = 0

        for backend in backends:
            cumulative += backend.weight
            if rand_weight <= cumulative:
                return backend

        return backends[-1]

    def _least_connections(self, backends: List[Backend]) -> Backend:
        """Select backend with least active connections"""
        return min(backends, key=lambda b: b.active_connections)

    def _least_response_time(self, backends: List[Backend]) -> Backend:
        """Select backend with lowest response time"""
        return min(backends, key=lambda b: b.avg_response_time or 0)

    def _ip_hash(self, backends: List[Backend], client_ip: str) -> Backend:
        """Hash-based selection (consistent hashing)"""
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        index = hash_value % len(backends)
        return backends[index]

    def _adaptive(self, backends: List[Backend]) -> Backend:
        """
        Adaptive selection based on multiple factors

        Factors:
        - Response time (40%)
        - Error rate (30%)
        - Active connections (20%)
        - Weight (10%)
        """
        scores = []

        # Normalize metrics
        max_response_time = max((b.avg_response_time or 0.001 for b in backends))
        max_connections = max((b.active_connections for b in backends)) or 1
        max_weight = max((b.weight for b in backends))

        for backend in backends:
            # Lower is better for response time and connections
            response_score = 1 - (backend.avg_response_time / max_response_time)
            connection_score = 1 - (backend.active_connections / max_connections)
            error_score = 1 - backend.error_rate
            weight_score = backend.weight / max_weight

            # Weighted combination
            score = (
                0.4 * response_score +
                0.3 * error_score +
                0.2 * connection_score +
                0.1 * weight_score
            )

            scores.append((score, backend))

        # Select backend with highest score
        return max(scores, key=lambda x: x[0])[1]

    async def execute_request(
        self,
        func: Callable,
        *args,
        session_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Execute request on selected backend

        Args:
            func: Function to execute
            args: Positional arguments
            session_id: Optional session ID
            client_ip: Optional client IP
            kwargs: Keyword arguments

        Returns:
            Request result

        Raises:
            Exception if all backends fail
        """
        self.stats['total_requests'] += 1

        # Try backends until success or all fail
        max_attempts = len(self.backends)
        attempt = 0

        while attempt < max_attempts:
            backend = self.get_backend(session_id, client_ip)

            if not backend:
                raise Exception("No healthy backends available")

            # Track connection
            backend.active_connections += 1

            try:
                start_time = time.time()

                # Execute request
                result = await func(*args, backend=backend, **kwargs)

                # Record success
                response_time = time.time() - start_time
                backend.record_response(response_time, success=True)
                self.failure_counts[backend.id] = 0  # Reset failures

                return result

            except Exception as e:
                # Record failure
                response_time = time.time() - start_time
                backend.record_response(response_time, success=False)

                self.failure_counts[backend.id] += 1
                self.stats['total_errors'] += 1

                # Mark unhealthy if too many failures
                if self.failure_counts[backend.id] >= self.max_failures:
                    backend.is_healthy = False
                    self.stats['backend_failures'] += 1

                # Try next backend
                attempt += 1

                if attempt >= max_attempts:
                    raise

            finally:
                # Release connection
                backend.active_connections -= 1

        raise Exception("All backends failed")

    async def health_check(self, backend: Backend) -> bool:
        """
        Perform health check on backend

        Args:
            backend: Backend to check

        Returns:
            Health status
        """
        try:
            # In production, implement actual health check
            # (e.g., HTTP GET to /health endpoint)
            await asyncio.sleep(0.01)  # Simulate check

            # Simulate 95% success rate
            return random.random() > 0.05

        except:
            return False

    async def start_health_checks(self):
        """Start background health checking"""
        while True:
            try:
                for backend in self.backends.values():
                    is_healthy = await asyncio.wait_for(
                        self.health_check(backend),
                        timeout=self.health_check_timeout
                    )

                    if is_healthy and not backend.is_healthy:
                        # Backend recovered
                        backend.is_healthy = True
                        self.failure_counts[backend.id] = 0

                    elif not is_healthy and backend.is_healthy:
                        # Backend became unhealthy
                        self.failure_counts[backend.id] += 1

                        if self.failure_counts[backend.id] >= self.max_failures:
                            backend.is_healthy = False
                            self.stats['backend_failures'] += 1

                await asyncio.sleep(self.health_check_interval)

            except Exception as e:
                print(f"Health check error: {e}")
                await asyncio.sleep(self.health_check_interval)

    def get_stats(self) -> Dict:
        """Get load balancer statistics"""
        healthy_count = sum(1 for b in self.backends.values() if b.is_healthy)

        backend_stats = {
            backend_id: {
                'is_healthy': backend.is_healthy,
                'active_connections': backend.active_connections,
                'total_requests': backend.total_requests,
                'error_rate': backend.error_rate,
                'avg_response_time': backend.avg_response_time
            }
            for backend_id, backend in self.backends.items()
        }

        return {
            **self.stats,
            'strategy': self.strategy.value,
            'total_backends': len(self.backends),
            'healthy_backends': healthy_count,
            'backends': backend_stats
        }

    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            'total_requests': 0,
            'total_errors': 0,
            'backend_failures': 0
        }

        for backend in self.backends.values():
            backend.total_requests = 0
            backend.total_errors = 0
            backend.response_times.clear()
