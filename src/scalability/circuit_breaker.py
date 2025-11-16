"""
Circuit Breaker
Prevents cascading failures with automatic recovery
"""

import asyncio
import time
from typing import Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout: float = 60.0
    half_open_max_calls: int = 3


class CircuitBreaker:
    """
    Circuit breaker pattern implementation

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests blocked
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        """
        Initialize circuit breaker

        Args:
            config: Configuration
        """
        self.config = config or CircuitBreakerConfig()

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_calls = 0

        # Statistics
        self.stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'rejected_calls': 0,
            'state_changes': 0
        }

    async def call(
        self,
        func: Callable,
        *args,
        fallback: Optional[Callable] = None,
        **kwargs
    ) -> Any:
        """
        Execute function with circuit breaker

        Args:
            func: Function to execute
            args: Positional arguments
            fallback: Fallback function if circuit open
            kwargs: Keyword arguments

        Returns:
            Function result or fallback result

        Raises:
            Exception if circuit open and no fallback
        """
        self.stats['total_calls'] += 1

        # Check circuit state
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                self.stats['rejected_calls'] += 1

                if fallback:
                    return await fallback(*args, **kwargs)

                raise Exception("Circuit breaker is OPEN")

        # Track half-open calls
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1

            if self.half_open_calls > self.config.half_open_max_calls:
                self._transition_to_open()
                self.stats['rejected_calls'] += 1

                if fallback:
                    return await fallback(*args, **kwargs)

                raise Exception("Circuit breaker is OPEN")

        # Execute function
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()

            if fallback:
                return await fallback(*args, **kwargs)

            raise

    def _on_success(self):
        """Handle successful call"""
        self.stats['successful_calls'] += 1

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1

            if self.success_count >= self.config.success_threshold:
                self._transition_to_closed()

        # Reset failure count on success
        self.failure_count = 0

    def _on_failure(self):
        """Handle failed call"""
        self.stats['failed_calls'] += 1
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            self._transition_to_open()

        elif self.failure_count >= self.config.failure_threshold:
            self._transition_to_open()

    def _should_attempt_reset(self) -> bool:
        """Check if should attempt recovery"""
        if self.last_failure_time is None:
            return False

        return (time.time() - self.last_failure_time) >= self.config.timeout

    def _transition_to_closed(self):
        """Transition to CLOSED state"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0
        self.stats['state_changes'] += 1

    def _transition_to_open(self):
        """Transition to OPEN state"""
        self.state = CircuitState.OPEN
        self.success_count = 0
        self.half_open_calls = 0
        self.stats['state_changes'] += 1

    def _transition_to_half_open(self):
        """Transition to HALF_OPEN state"""
        self.state = CircuitState.HALF_OPEN
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0
        self.stats['state_changes'] += 1

    def reset(self):
        """Reset circuit breaker"""
        self._transition_to_closed()
        self.last_failure_time = None

    def get_stats(self) -> dict:
        """Get circuit breaker statistics"""
        return {
            **self.stats,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'error_rate': (
                self.stats['failed_calls'] /
                max(self.stats['total_calls'], 1)
            )
        }
