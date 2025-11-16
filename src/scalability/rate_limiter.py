"""
Rate Limiter
Prevents system overload with multiple rate limiting algorithms
"""

import asyncio
import time
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum
from collections import deque


class RateLimitStrategy(Enum):
    """Rate limiting strategies"""
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW_LOG = "sliding_window_log"
    SLIDING_WINDOW_COUNTER = "sliding_window_counter"


@dataclass
class RateLimitResult:
    """Result of rate limit check"""
    allowed: bool
    remaining: int
    reset_at: float
    retry_after: Optional[float] = None


class RateLimiter:
    """
    Advanced rate limiter with multiple strategies

    Features:
    - Multiple rate limiting algorithms
    - Per-client limits
    - Burst support
    - Distributed rate limiting support
    """

    def __init__(
        self,
        strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET,
        rate: int = 100,  # requests per window
        window: float = 60.0,  # window size in seconds
        burst: int = None  # max burst size
    ):
        """
        Initialize rate limiter

        Args:
            strategy: Rate limiting strategy
            rate: Request limit per window
            window: Time window in seconds
            burst: Maximum burst size (default: rate * 2)
        """
        self.strategy = strategy
        self.rate = rate
        self.window = window
        self.burst = burst or (rate * 2)

        # Per-client state
        self.clients: Dict[str, Dict] = {}

        # Global statistics
        self.stats = {
            'total_requests': 0,
            'allowed_requests': 0,
            'blocked_requests': 0,
            'unique_clients': 0
        }

    async def check_limit(
        self,
        client_id: str,
        cost: int = 1
    ) -> RateLimitResult:
        """
        Check if request is allowed

        Args:
            client_id: Client identifier (IP, API key, etc.)
            cost: Request cost (for weighted limits)

        Returns:
            Rate limit result
        """
        self.stats['total_requests'] += 1

        # Initialize client if new
        if client_id not in self.clients:
            self._init_client(client_id)
            self.stats['unique_clients'] = len(self.clients)

        # Check based on strategy
        if self.strategy == RateLimitStrategy.TOKEN_BUCKET:
            result = self._token_bucket(client_id, cost)

        elif self.strategy == RateLimitStrategy.LEAKY_BUCKET:
            result = self._leaky_bucket(client_id, cost)

        elif self.strategy == RateLimitStrategy.FIXED_WINDOW:
            result = self._fixed_window(client_id, cost)

        elif self.strategy == RateLimitStrategy.SLIDING_WINDOW_LOG:
            result = self._sliding_window_log(client_id, cost)

        else:  # SLIDING_WINDOW_COUNTER
            result = self._sliding_window_counter(client_id, cost)

        # Update stats
        if result.allowed:
            self.stats['allowed_requests'] += 1
        else:
            self.stats['blocked_requests'] += 1

        return result

    def _init_client(self, client_id: str):
        """Initialize client state"""
        current_time = time.time()

        self.clients[client_id] = {
            'tokens': self.rate,
            'last_refill': current_time,
            'queue': deque(),
            'window_start': current_time,
            'window_count': 0,
            'request_log': deque(),
            'buckets': {}
        }

    def _token_bucket(
        self,
        client_id: str,
        cost: int
    ) -> RateLimitResult:
        """
        Token bucket algorithm

        Tokens are added at a constant rate.
        Each request consumes tokens.
        Allows bursts up to bucket capacity.
        """
        client = self.clients[client_id]
        current_time = time.time()

        # Refill tokens based on elapsed time
        elapsed = current_time - client['last_refill']
        refill_rate = self.rate / self.window
        tokens_to_add = elapsed * refill_rate

        client['tokens'] = min(
            self.burst,
            client['tokens'] + tokens_to_add
        )
        client['last_refill'] = current_time

        # Check if enough tokens
        if client['tokens'] >= cost:
            client['tokens'] -= cost
            allowed = True
            remaining = int(client['tokens'])
            retry_after = None
        else:
            allowed = False
            remaining = int(client['tokens'])
            # Calculate when enough tokens will be available
            tokens_needed = cost - client['tokens']
            retry_after = tokens_needed / refill_rate

        reset_at = current_time + (self.burst - client['tokens']) / refill_rate

        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            reset_at=reset_at,
            retry_after=retry_after
        )

    def _leaky_bucket(
        self,
        client_id: str,
        cost: int
    ) -> RateLimitResult:
        """
        Leaky bucket algorithm

        Requests are added to queue.
        Queue processes at constant rate.
        Excess requests overflow (rejected).
        """
        client = self.clients[client_id]
        current_time = time.time()

        # Leak from bucket
        leak_rate = self.rate / self.window
        elapsed = current_time - client['last_refill']
        leaked = int(elapsed * leak_rate)

        # Remove leaked requests
        for _ in range(min(leaked, len(client['queue']))):
            client['queue'].popleft()

        client['last_refill'] = current_time

        # Try to add request
        if len(client['queue']) + cost <= self.burst:
            for _ in range(cost):
                client['queue'].append(current_time)
            allowed = True
            retry_after = None
        else:
            allowed = False
            # Calculate when space will be available
            overflow = len(client['queue']) + cost - self.burst
            retry_after = overflow / leak_rate

        remaining = self.burst - len(client['queue'])
        reset_at = current_time + len(client['queue']) / leak_rate

        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            reset_at=reset_at,
            retry_after=retry_after
        )

    def _fixed_window(
        self,
        client_id: str,
        cost: int
    ) -> RateLimitResult:
        """
        Fixed window algorithm

        Count requests in fixed time windows.
        Simple but can allow bursts at window boundaries.
        """
        client = self.clients[client_id]
        current_time = time.time()

        # Check if window expired
        if current_time - client['window_start'] >= self.window:
            client['window_start'] = current_time
            client['window_count'] = 0

        # Check limit
        if client['window_count'] + cost <= self.rate:
            client['window_count'] += cost
            allowed = True
            retry_after = None
        else:
            allowed = False
            # Retry after current window ends
            retry_after = self.window - (current_time - client['window_start'])

        remaining = self.rate - client['window_count']
        reset_at = client['window_start'] + self.window

        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            reset_at=reset_at,
            retry_after=retry_after
        )

    def _sliding_window_log(
        self,
        client_id: str,
        cost: int
    ) -> RateLimitResult:
        """
        Sliding window log algorithm

        Keep log of all requests.
        Count requests in sliding window.
        Accurate but memory intensive.
        """
        client = self.clients[client_id]
        current_time = time.time()

        # Remove old requests outside window
        window_start = current_time - self.window
        while client['request_log'] and client['request_log'][0] < window_start:
            client['request_log'].popleft()

        # Check limit
        current_count = len(client['request_log'])

        if current_count + cost <= self.rate:
            for _ in range(cost):
                client['request_log'].append(current_time)
            allowed = True
            retry_after = None
        else:
            allowed = False
            # Retry after oldest request expires
            if client['request_log']:
                oldest = client['request_log'][0]
                retry_after = self.window - (current_time - oldest)
            else:
                retry_after = 0

        remaining = self.rate - len(client['request_log'])
        reset_at = current_time + self.window

        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            reset_at=reset_at,
            retry_after=retry_after
        )

    def _sliding_window_counter(
        self,
        client_id: str,
        cost: int
    ) -> RateLimitResult:
        """
        Sliding window counter algorithm

        Hybrid approach using buckets.
        More memory efficient than log.
        Good approximation of sliding window.
        """
        client = self.clients[client_id]
        current_time = time.time()

        # Use sub-windows for approximation
        bucket_size = self.window / 10  # 10 buckets per window
        current_bucket = int(current_time / bucket_size)
        window_start_bucket = int((current_time - self.window) / bucket_size)

        # Clean old buckets
        buckets_to_remove = [
            b for b in client['buckets']
            if b < window_start_bucket
        ]
        for bucket in buckets_to_remove:
            del client['buckets'][bucket]

        # Count requests in window
        total_count = sum(client['buckets'].values())

        # Weighted count for current bucket
        # (to handle partial buckets)
        if total_count + cost <= self.rate:
            if current_bucket not in client['buckets']:
                client['buckets'][current_bucket] = 0
            client['buckets'][current_bucket] += cost
            allowed = True
            retry_after = None
        else:
            allowed = False
            # Approximate retry time
            retry_after = bucket_size

        remaining = self.rate - total_count
        reset_at = (current_bucket + 1) * bucket_size

        return RateLimitResult(
            allowed=allowed,
            remaining=max(0, remaining),
            reset_at=reset_at,
            retry_after=retry_after
        )

    async def wait_if_needed(
        self,
        client_id: str,
        cost: int = 1
    ) -> bool:
        """
        Wait if rate limited, then proceed

        Args:
            client_id: Client identifier
            cost: Request cost

        Returns:
            Always True (after waiting if needed)
        """
        while True:
            result = await self.check_limit(client_id, cost)

            if result.allowed:
                return True

            # Wait before retry
            if result.retry_after:
                await asyncio.sleep(result.retry_after)
            else:
                await asyncio.sleep(0.1)

    def reset_client(self, client_id: str):
        """
        Reset rate limit for client

        Args:
            client_id: Client identifier
        """
        if client_id in self.clients:
            self._init_client(client_id)

    def get_client_stats(self, client_id: str) -> Optional[Dict]:
        """
        Get statistics for specific client

        Args:
            client_id: Client identifier

        Returns:
            Client statistics or None
        """
        if client_id not in self.clients:
            return None

        client = self.clients[client_id]

        return {
            'tokens': int(client.get('tokens', 0)),
            'queue_size': len(client.get('queue', [])),
            'window_count': client.get('window_count', 0),
            'total_requests': len(client.get('request_log', []))
        }

    def get_stats(self) -> Dict:
        """Get global statistics"""
        return {
            **self.stats,
            'strategy': self.strategy.value,
            'rate': self.rate,
            'window': self.window,
            'burst': self.burst,
            'block_rate': (
                self.stats['blocked_requests'] /
                max(self.stats['total_requests'], 1)
            )
        }

    def cleanup_inactive_clients(
        self,
        inactive_threshold: float = 3600.0
    ):
        """
        Clean up inactive clients

        Args:
            inactive_threshold: Inactivity time in seconds
        """
        current_time = time.time()
        inactive_clients = []

        for client_id, client in self.clients.items():
            # Check last activity
            last_activity = client.get('last_refill', 0)

            if current_time - last_activity > inactive_threshold:
                inactive_clients.append(client_id)

        # Remove inactive clients
        for client_id in inactive_clients:
            del self.clients[client_id]

        self.stats['unique_clients'] = len(self.clients)
