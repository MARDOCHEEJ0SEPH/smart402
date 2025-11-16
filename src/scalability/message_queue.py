"""
Message Queue System
Asynchronous message queuing for decoupled processing with priority support
"""

import asyncio
import time
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import heapq
from collections import defaultdict


class QueuePriority(Enum):
    """Message priority levels"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


@dataclass(order=True)
class Message:
    """
    Message in queue

    Uses priority queue with timestamp as tiebreaker
    """
    priority: int = field(compare=True)
    timestamp: float = field(compare=True)
    id: str = field(compare=False, default_factory=lambda: str(uuid.uuid4()))
    topic: str = field(compare=False, default="")
    payload: Any = field(compare=False, default=None)
    headers: Dict = field(compare=False, default_factory=dict)
    retry_count: int = field(compare=False, default=0)
    max_retries: int = field(compare=False, default=3)


class MessageQueue:
    """
    High-performance message queue with priority support

    Features:
    - Priority-based message ordering
    - Topic-based routing
    - Dead letter queue for failed messages
    - Message acknowledgment
    - Consumer groups
    - Rate limiting
    - Message persistence (optional)
    """

    def __init__(
        self,
        max_size: int = 10000,
        enable_persistence: bool = False,
        dead_letter_ttl: int = 86400
    ):
        """
        Initialize message queue

        Args:
            max_size: Maximum queue size
            enable_persistence: Enable message persistence
            dead_letter_ttl: Dead letter queue TTL in seconds
        """
        self.max_size = max_size
        self.enable_persistence = enable_persistence
        self.dead_letter_ttl = dead_letter_ttl

        # Priority queue (min-heap)
        self.queue: List[Message] = []

        # Topic subscriptions
        self.subscriptions: Dict[str, List[Callable]] = defaultdict(list)

        # Dead letter queue
        self.dead_letter_queue: List[Message] = []

        # Statistics
        self.stats = {
            'messages_published': 0,
            'messages_consumed': 0,
            'messages_failed': 0,
            'messages_dead_letter': 0,
            'current_size': 0
        }

        # Message tracking
        self.in_flight: Dict[str, Message] = {}
        self.ack_timeout = 30.0  # seconds

    async def publish(
        self,
        topic: str,
        payload: Any,
        priority: QueuePriority = QueuePriority.NORMAL,
        headers: Optional[Dict] = None
    ) -> str:
        """
        Publish message to queue

        Args:
            topic: Message topic
            payload: Message payload
            priority: Message priority
            headers: Optional headers

        Returns:
            Message ID
        """
        if len(self.queue) >= self.max_size:
            raise Exception("Queue is full")

        message = Message(
            priority=priority.value,
            timestamp=time.time(),
            topic=topic,
            payload=payload,
            headers=headers or {}
        )

        heapq.heappush(self.queue, message)

        self.stats['messages_published'] += 1
        self.stats['current_size'] = len(self.queue)

        # Trigger topic subscribers
        await self._notify_subscribers(message)

        return message.id

    async def publish_batch(
        self,
        messages: List[tuple]
    ) -> List[str]:
        """
        Publish multiple messages at once

        Args:
            messages: List of (topic, payload, priority) tuples

        Returns:
            List of message IDs
        """
        message_ids = []

        for item in messages:
            if len(item) == 2:
                topic, payload = item
                priority = QueuePriority.NORMAL
            else:
                topic, payload, priority = item

            msg_id = await self.publish(topic, payload, priority)
            message_ids.append(msg_id)

        return message_ids

    async def consume(
        self,
        timeout: Optional[float] = None
    ) -> Optional[Message]:
        """
        Consume message from queue

        Args:
            timeout: Maximum wait time in seconds

        Returns:
            Message or None
        """
        start_time = time.time()

        while True:
            if self.queue:
                message = heapq.heappop(self.queue)

                # Track in-flight
                self.in_flight[message.id] = message

                self.stats['messages_consumed'] += 1
                self.stats['current_size'] = len(self.queue)

                return message

            if timeout and (time.time() - start_time) > timeout:
                return None

            await asyncio.sleep(0.01)

    async def consume_batch(
        self,
        batch_size: int,
        timeout: Optional[float] = None
    ) -> List[Message]:
        """
        Consume multiple messages at once

        Args:
            batch_size: Number of messages to consume
            timeout: Maximum wait time

        Returns:
            List of messages
        """
        messages = []
        start_time = time.time()

        while len(messages) < batch_size:
            remaining_timeout = None
            if timeout:
                elapsed = time.time() - start_time
                remaining_timeout = max(0, timeout - elapsed)

            message = await self.consume(timeout=remaining_timeout)
            if message:
                messages.append(message)
            else:
                break

        return messages

    async def ack(self, message_id: str):
        """
        Acknowledge message processing

        Args:
            message_id: Message ID
        """
        if message_id in self.in_flight:
            del self.in_flight[message_id]

    async def nack(self, message_id: str, requeue: bool = True):
        """
        Negative acknowledgment (message processing failed)

        Args:
            message_id: Message ID
            requeue: Whether to requeue message
        """
        if message_id not in self.in_flight:
            return

        message = self.in_flight[message_id]
        del self.in_flight[message_id]

        if requeue and message.retry_count < message.max_retries:
            # Retry message
            message.retry_count += 1
            message.timestamp = time.time()
            heapq.heappush(self.queue, message)
        else:
            # Send to dead letter queue
            message.headers['failed_at'] = time.time()
            message.headers['retry_count'] = message.retry_count
            self.dead_letter_queue.append(message)

            self.stats['messages_failed'] += 1
            self.stats['messages_dead_letter'] += 1

    async def subscribe(
        self,
        topic: str,
        handler: Callable
    ):
        """
        Subscribe to topic

        Args:
            topic: Topic pattern (supports wildcards)
            handler: Async callback function
        """
        self.subscriptions[topic].append(handler)

    async def unsubscribe(
        self,
        topic: str,
        handler: Callable
    ):
        """
        Unsubscribe from topic

        Args:
            topic: Topic pattern
            handler: Handler to remove
        """
        if topic in self.subscriptions:
            if handler in self.subscriptions[topic]:
                self.subscriptions[topic].remove(handler)

    async def _notify_subscribers(self, message: Message):
        """
        Notify topic subscribers

        Args:
            message: Published message
        """
        for topic_pattern, handlers in self.subscriptions.items():
            if self._match_topic(message.topic, topic_pattern):
                for handler in handlers:
                    try:
                        asyncio.create_task(handler(message))
                    except Exception as e:
                        print(f"Subscription handler error: {e}")

    def _match_topic(self, topic: str, pattern: str) -> bool:
        """
        Match topic against pattern

        Args:
            topic: Message topic
            pattern: Topic pattern (supports * wildcard)

        Returns:
            Match status
        """
        if pattern == "*":
            return True

        if "*" in pattern:
            import re
            regex = pattern.replace("*", ".*")
            return bool(re.match(f"^{regex}$", topic))

        return topic == pattern

    async def purge(self, topic: Optional[str] = None):
        """
        Purge messages from queue

        Args:
            topic: Optional topic to purge (all if None)
        """
        if topic is None:
            self.queue.clear()
            self.in_flight.clear()
        else:
            # Remove messages for specific topic
            self.queue = [m for m in self.queue if m.topic != topic]
            heapq.heapify(self.queue)

            self.in_flight = {
                k: v for k, v in self.in_flight.items()
                if v.topic != topic
            }

        self.stats['current_size'] = len(self.queue)

    async def get_dead_letters(self) -> List[Message]:
        """
        Get messages from dead letter queue

        Returns:
            List of failed messages
        """
        # Clean expired messages
        cutoff = time.time() - self.dead_letter_ttl
        self.dead_letter_queue = [
            m for m in self.dead_letter_queue
            if m.headers.get('failed_at', 0) > cutoff
        ]

        return self.dead_letter_queue

    async def retry_dead_letter(self, message_id: str):
        """
        Retry message from dead letter queue

        Args:
            message_id: Message ID to retry
        """
        for i, message in enumerate(self.dead_letter_queue):
            if message.id == message_id:
                # Remove from dead letter
                message = self.dead_letter_queue.pop(i)

                # Reset and requeue
                message.retry_count = 0
                message.timestamp = time.time()
                heapq.heappush(self.queue, message)

                break

    def get_stats(self) -> Dict:
        """
        Get queue statistics

        Returns:
            Statistics dictionary
        """
        return {
            **self.stats,
            'in_flight': len(self.in_flight),
            'dead_letter_size': len(self.dead_letter_queue),
            'subscription_count': len(self.subscriptions),
            'utilization': len(self.queue) / self.max_size
        }

    async def start_ack_monitor(self):
        """Background task to monitor message acknowledgments"""
        while True:
            try:
                current_time = time.time()

                # Find timed-out messages
                timed_out = [
                    msg_id for msg_id, msg in self.in_flight.items()
                    if (current_time - msg.timestamp) > self.ack_timeout
                ]

                # Requeue or dead letter
                for msg_id in timed_out:
                    await self.nack(msg_id, requeue=True)

                await asyncio.sleep(1)

            except Exception as e:
                print(f"Ack monitor error: {e}")
                await asyncio.sleep(5)


class MessageBroker:
    """
    Multi-queue message broker with routing

    Features:
    - Multiple named queues
    - Cross-queue routing
    - Fanout exchanges
    - Topic exchanges
    """

    def __init__(self):
        """Initialize message broker"""
        self.queues: Dict[str, MessageQueue] = {}
        self.exchanges: Dict[str, Dict] = {}

    def create_queue(
        self,
        name: str,
        max_size: int = 10000
    ) -> MessageQueue:
        """
        Create named queue

        Args:
            name: Queue name
            max_size: Maximum size

        Returns:
            Message queue
        """
        if name in self.queues:
            return self.queues[name]

        queue = MessageQueue(max_size=max_size)
        self.queues[name] = queue
        return queue

    def get_queue(self, name: str) -> Optional[MessageQueue]:
        """
        Get queue by name

        Args:
            name: Queue name

        Returns:
            Message queue or None
        """
        return self.queues.get(name)

    def create_exchange(
        self,
        name: str,
        exchange_type: str = "direct"
    ):
        """
        Create exchange for routing

        Args:
            name: Exchange name
            exchange_type: Type (direct, fanout, topic)
        """
        self.exchanges[name] = {
            'type': exchange_type,
            'bindings': []
        }

    async def publish_to_exchange(
        self,
        exchange: str,
        routing_key: str,
        payload: Any,
        priority: QueuePriority = QueuePriority.NORMAL
    ):
        """
        Publish message to exchange

        Args:
            exchange: Exchange name
            routing_key: Routing key
            payload: Message payload
            priority: Message priority
        """
        if exchange not in self.exchanges:
            raise ValueError(f"Exchange {exchange} not found")

        exchange_config = self.exchanges[exchange]

        # Route to appropriate queues
        for binding in exchange_config['bindings']:
            queue_name = binding['queue']
            binding_key = binding['key']

            if self._should_route(
                exchange_config['type'],
                routing_key,
                binding_key
            ):
                queue = self.queues.get(queue_name)
                if queue:
                    await queue.publish(
                        routing_key,
                        payload,
                        priority
                    )

    def bind_queue(
        self,
        exchange: str,
        queue: str,
        routing_key: str = ""
    ):
        """
        Bind queue to exchange

        Args:
            exchange: Exchange name
            queue: Queue name
            routing_key: Routing key pattern
        """
        if exchange not in self.exchanges:
            raise ValueError(f"Exchange {exchange} not found")

        if queue not in self.queues:
            raise ValueError(f"Queue {queue} not found")

        self.exchanges[exchange]['bindings'].append({
            'queue': queue,
            'key': routing_key
        })

    def _should_route(
        self,
        exchange_type: str,
        routing_key: str,
        binding_key: str
    ) -> bool:
        """Determine if message should be routed to queue"""
        if exchange_type == "fanout":
            return True
        elif exchange_type == "direct":
            return routing_key == binding_key
        elif exchange_type == "topic":
            # Simple wildcard matching
            import re
            pattern = binding_key.replace("*", ".*")
            return bool(re.match(f"^{pattern}$", routing_key))

        return False

    def get_stats(self) -> Dict:
        """Get broker statistics"""
        return {
            'queues': {
                name: queue.get_stats()
                for name, queue in self.queues.items()
            },
            'exchange_count': len(self.exchanges)
        }
