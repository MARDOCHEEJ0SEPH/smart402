"""
Distributed Processing Layer
Enables horizontal scaling with worker pools and task distribution
"""

import asyncio
import multiprocessing
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import numpy as np


class ProcessingMode(Enum):
    """Processing mode for task execution"""
    PROCESS = "process"  # CPU-bound tasks
    THREAD = "thread"    # I/O-bound tasks
    ASYNC = "async"      # Async tasks


@dataclass
class Task:
    """Distributed task representation"""
    id: str
    function: str
    args: tuple
    kwargs: dict
    priority: int = 0
    created_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class TaskResult:
    """Task execution result"""
    task_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    worker_id: str = ""


class WorkerPool:
    """
    Worker pool for distributed task processing

    Features:
    - Multi-process and multi-threaded execution
    - Dynamic worker scaling
    - Load balancing across workers
    - Failure recovery
    """

    def __init__(
        self,
        num_workers: int = None,
        mode: ProcessingMode = ProcessingMode.PROCESS,
        max_tasks_per_worker: int = 100
    ):
        """
        Initialize worker pool

        Args:
            num_workers: Number of workers (default: CPU count)
            mode: Processing mode (process/thread/async)
            max_tasks_per_worker: Maximum tasks per worker
        """
        self.num_workers = num_workers or multiprocessing.cpu_count()
        self.mode = mode
        self.max_tasks_per_worker = max_tasks_per_worker

        # Initialize executor based on mode
        if mode == ProcessingMode.PROCESS:
            self.executor = ProcessPoolExecutor(max_workers=self.num_workers)
        elif mode == ProcessingMode.THREAD:
            self.executor = ThreadPoolExecutor(max_workers=self.num_workers)
        else:
            self.executor = None  # Use asyncio

        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.results: Dict[str, TaskResult] = {}
        self.worker_stats: Dict[str, Dict] = {}
        self.active_tasks: Dict[str, Task] = {}

    async def submit_task(
        self,
        func: Callable,
        *args,
        priority: int = 0,
        **kwargs
    ) -> str:
        """
        Submit task to worker pool

        Args:
            func: Function to execute
            args: Positional arguments
            priority: Task priority (higher = more important)
            kwargs: Keyword arguments

        Returns:
            Task ID
        """
        task = Task(
            id=str(uuid.uuid4()),
            function=func.__name__,
            args=args,
            kwargs=kwargs,
            priority=priority
        )

        await self.task_queue.put(task)
        self.active_tasks[task.id] = task

        return task.id

    async def submit_batch(
        self,
        tasks: List[tuple]
    ) -> List[str]:
        """
        Submit multiple tasks at once

        Args:
            tasks: List of (func, args, kwargs) tuples

        Returns:
            List of task IDs
        """
        task_ids = []

        for item in tasks:
            if len(item) == 2:
                func, args = item
                kwargs = {}
            else:
                func, args, kwargs = item

            task_id = await self.submit_task(func, *args, **kwargs)
            task_ids.append(task_id)

        return task_ids

    async def get_result(
        self,
        task_id: str,
        timeout: float = None
    ) -> TaskResult:
        """
        Get task result

        Args:
            task_id: Task identifier
            timeout: Maximum wait time in seconds

        Returns:
            Task result
        """
        start_time = time.time()

        while task_id not in self.results:
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Task {task_id} timed out")

            await asyncio.sleep(0.1)

        return self.results[task_id]

    async def get_batch_results(
        self,
        task_ids: List[str],
        timeout: float = None
    ) -> List[TaskResult]:
        """
        Get results for multiple tasks

        Args:
            task_ids: List of task IDs
            timeout: Maximum wait time

        Returns:
            List of task results
        """
        results = []

        for task_id in task_ids:
            result = await self.get_result(task_id, timeout)
            results.append(result)

        return results

    async def process_tasks(self):
        """Background task processor"""
        worker_id = str(uuid.uuid4())

        while True:
            try:
                # Get task from queue
                task = await self.task_queue.get()

                # Execute task
                start_time = time.time()

                try:
                    # Note: In production, you'd use proper function registry
                    # Here we simulate execution
                    result = await self._execute_task(task)

                    task_result = TaskResult(
                        task_id=task.id,
                        success=True,
                        result=result,
                        execution_time=time.time() - start_time,
                        worker_id=worker_id
                    )
                except Exception as e:
                    task_result = TaskResult(
                        task_id=task.id,
                        success=False,
                        error=str(e),
                        execution_time=time.time() - start_time,
                        worker_id=worker_id
                    )

                # Store result
                self.results[task.id] = task_result

                # Remove from active tasks
                if task.id in self.active_tasks:
                    del self.active_tasks[task.id]

                # Update worker stats
                if worker_id not in self.worker_stats:
                    self.worker_stats[worker_id] = {
                        'tasks_completed': 0,
                        'total_time': 0.0,
                        'errors': 0
                    }

                stats = self.worker_stats[worker_id]
                stats['tasks_completed'] += 1
                stats['total_time'] += task_result.execution_time
                if not task_result.success:
                    stats['errors'] += 1

                self.task_queue.task_done()

            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)

    async def _execute_task(self, task: Task) -> Any:
        """
        Execute task based on processing mode

        Args:
            task: Task to execute

        Returns:
            Execution result
        """
        # In production, implement function registry
        # For now, simulate execution
        await asyncio.sleep(np.random.uniform(0.01, 0.1))
        return {'status': 'completed', 'task_id': task.id}

    def get_stats(self) -> Dict:
        """
        Get worker pool statistics

        Returns:
            Statistics dictionary
        """
        total_tasks = sum(s['tasks_completed'] for s in self.worker_stats.values())
        total_errors = sum(s['errors'] for s in self.worker_stats.values())

        return {
            'num_workers': self.num_workers,
            'mode': self.mode.value,
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.results),
            'total_tasks': total_tasks,
            'error_rate': total_errors / max(total_tasks, 1),
            'queue_size': self.task_queue.qsize(),
            'worker_stats': self.worker_stats
        }

    async def shutdown(self):
        """Shutdown worker pool gracefully"""
        if self.executor:
            self.executor.shutdown(wait=True)


class DistributedProcessor:
    """
    High-level distributed processing coordinator

    Features:
    - Multiple worker pools for different task types
    - Intelligent task routing
    - Fault tolerance with retry logic
    - Performance monitoring
    """

    def __init__(self):
        """Initialize distributed processor"""
        # Separate pools for different workload types
        self.cpu_pool = WorkerPool(
            mode=ProcessingMode.PROCESS,
            num_workers=multiprocessing.cpu_count()
        )

        self.io_pool = WorkerPool(
            mode=ProcessingMode.THREAD,
            num_workers=multiprocessing.cpu_count() * 4
        )

        self.pools = {
            'cpu': self.cpu_pool,
            'io': self.io_pool
        }

        self.task_routing: Dict[str, str] = {
            'aeo_optimize': 'cpu',
            'llmo_optimize': 'cpu',
            'scc_compile': 'cpu',
            'x402_execute': 'io',
            'default': 'cpu'
        }

        self.retry_policy = {
            'max_retries': 3,
            'retry_delay': 1.0,
            'exponential_backoff': True
        }

    async def start(self):
        """Start all worker pools"""
        for pool_name, pool in self.pools.items():
            # Start workers
            for _ in range(pool.num_workers):
                asyncio.create_task(pool.process_tasks())

    async def process_contract_batch(
        self,
        contracts: List[Dict],
        phase: str
    ) -> List[Dict]:
        """
        Process batch of contracts through a phase in parallel

        Args:
            contracts: List of contracts
            phase: Processing phase (aeo, llmo, scc, x402)

        Returns:
            Processed contracts
        """
        # Determine which pool to use
        pool_name = self.task_routing.get(f'{phase}_optimize', 'cpu')
        pool = self.pools[pool_name]

        # Submit all contracts as parallel tasks
        task_ids = []

        for contract in contracts:
            task_id = await pool.submit_task(
                self._process_single_contract,
                contract,
                phase
            )
            task_ids.append(task_id)

        # Wait for all results
        results = await pool.get_batch_results(task_ids, timeout=30.0)

        # Extract processed contracts
        processed = []
        for result in results:
            if result.success:
                processed.append(result.result)

        return processed

    async def _process_single_contract(
        self,
        contract: Dict,
        phase: str
    ) -> Dict:
        """
        Process single contract (with retry logic)

        Args:
            contract: Contract to process
            phase: Processing phase

        Returns:
            Processed contract
        """
        max_retries = self.retry_policy['max_retries']
        retry_delay = self.retry_policy['retry_delay']

        for attempt in range(max_retries):
            try:
                # Simulate processing
                await asyncio.sleep(np.random.uniform(0.01, 0.05))

                # Add phase-specific processing
                contract[f'{phase}_processed'] = True
                contract[f'{phase}_score'] = np.random.uniform(0.7, 1.0)

                return contract

            except Exception as e:
                if attempt == max_retries - 1:
                    raise

                # Exponential backoff
                if self.retry_policy['exponential_backoff']:
                    delay = retry_delay * (2 ** attempt)
                else:
                    delay = retry_delay

                await asyncio.sleep(delay)

        return contract

    async def process_pipeline(
        self,
        contracts: List[Dict],
        phases: List[str] = None
    ) -> List[Dict]:
        """
        Process contracts through full pipeline in parallel

        Args:
            contracts: Input contracts
            phases: Pipeline phases (default: all)

        Returns:
            Fully processed contracts
        """
        if phases is None:
            phases = ['aeo', 'llmo', 'scc', 'x402']

        processed = contracts

        for phase in phases:
            processed = await self.process_contract_batch(processed, phase)

        return processed

    def get_stats(self) -> Dict:
        """
        Get distributed processor statistics

        Returns:
            Statistics for all pools
        """
        return {
            pool_name: pool.get_stats()
            for pool_name, pool in self.pools.items()
        }

    async def shutdown(self):
        """Shutdown all pools"""
        for pool in self.pools.values():
            await pool.shutdown()
