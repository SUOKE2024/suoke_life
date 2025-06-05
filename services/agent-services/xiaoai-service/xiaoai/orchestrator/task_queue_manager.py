#!/usr/bin/env python3

""""""


""""""

import asyncio
import heapq
import json
import logging
import pickle
import time
import uuid
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


# class TaskStatus(Enum):
#     """""""""

#     PENDING = "pending"
#     RUNNING = "running"
#     SUCCESS = "success"
#     FAILURE = "failure"
#     RETRY = "retry"
#     CANCELLED = "cancelled"


# class TaskPriority(Enum):
#     """""""""

#     LOW = 1
#     NORMAL = 2
#     HIGH = 3
#     URGENT = 4


#     @dataclass
# class TaskConfig:
#     """""""""

#     maxretries: int = 3
#     retrydelay: float = 1.0
#     timeout: float = 300.0
#     priority: TaskPriority = TaskPriority.NORMAL
#     queuename: str = "default"


#     @dataclass
# class Task:
#     """""""""

#     id: str
#     name: str
#     funcname: str
#     args: tuple
#     kwargs: dict
#     config: TaskConfig
#     status: TaskStatus = TaskStatus.PENDING
#     createdat: datetime = None
#     startedat: datetime = None
#     completedat: datetime = None
#     retrycount: int = 0
#     result: Any = None
#     error: Optional[str] = None
#     workerid: Optional[str] = None

#     def __post_init__(self):
#         if self.created_at is None:
#             self.createdat = datetime.now()

#     def __lt__(self, other):
#         """""""""
#         return self.config.priority.value > other.config.priority.value


# class WorkflowStep:
#     """""""""

#     def __i_nit__(:
#         self,
#         _name: str,
#         taskfu_nc: Callable,
#         depe_ndso_n: list[str] | No_ne = No_ne,
#         **kwargs,
#         ):
#         self.name = name
#         self.taskfunc = task_func
#         self.dependson = depends_on or []
#         self.kwargs = kwargs
#         self.status = TaskStatus.PENDING
#         self.result = None
#         self.error = None


# class Workflow:
#     """""""""

#     def __init__(self, name: str, steps: list[WorkflowStep]):
#         self.id = str(uuid.uuid4())
#         self.name = name
#         self.steps = {step.name: step for step in steps}
#         self.executionorder = self._calculate_execution_order()
#         self.status = TaskStatus.PENDING
#         self.createdat = datetime.now()
#         self.startedat = None
#         self.completedat = None
#         self.results = {}

#     def _calculate_execution_order(self) -> list[list[str]]:
#         """()""""""
        # 
#         graph = defaultdict(list)
#         defaultdict(int)

#         for stepname, step in self.steps.items(): in_degree[step_name] = len(step.dependson):
#             for dep in step.depends_on: graph[dep].append(stepname):

        # 
#                 levels = []
#                 queue = deque([name for name, degree in in_degree.items() if degree == 0])

#         while queue:
#             currentlevel = []
#             for _ in range(len(queue)):
#                 node = queue.popleft()
#                 current_level.append(node)

#                 for neighbor in graph[node]: in_degree[neighbor] -= 1:
#                     if in_degree[neighbor] == 0:
#                         queue.append(neighbor)

#             if current_level: levels.append(currentlevel):

#                 return levels


# class PriorityTaskQueue:
#     """""""""

#     def __init__(self, maxsize: int = 0):
#         self.maxsize = maxsize
#         self.queue = []
#         self.index = 0
#         self.lock = asyncio.Lock()

#         async def put(self, task: Task):
#         """""""""
#         async with self.lock:
#             if self.maxsize > 0 and len(self.queue) >= self.maxsize:
#                 raise asyncio.QueueFull("")

            # FIFO
#                 heapq.heappush(self.queue, (-task.config.priority.value, self.index, task))
#                 self.index += 1

#                 async def get(self) -> Task:
#         """""""""
#                 async with self.lock:
#             if not self.queue:
#                 raise asyncio.QueueEmpty("")

#                 _, _, task = heapq.heappop(self.queue)
#                 return task

#                 async def size(self) -> int:
#         """""""""
#                 async with self.lock:
#                 return len(self.queue)

#                 async def empty(self) -> bool:
#         """""""""
#                 async with self.lock:
#                 return len(self.queue) == 0


# class TaskWorker:
#     """""""""

#     def __init__(self, worker_id: str, taskregistry: dict[str, Callable]):
#         self.workerid = worker_id
#         self.taskregistry = task_registry
#         self.running = False
#         self.currenttask = None
#         self.processedcount = 0
#         self.errorcount = 0
#         self.starttime = None

#         async def start(self, queue: PriorityTaskQueue):
#         """""""""
#         self.running = True
#         self.starttime = time.time()
#         logger.info(f" {self.worker_id} ")

#         while self.running:
#             try:
                # 
#                 task = await queue.get()
#                 await self._process_task(task)

#             except asyncio.QueueEmpty:
                # , 
#                 await asyncio.sleep(0.1)
#             except Exception as e:
#                 logger.error(f" {self.worker_id} : {e}")
#                 self.error_count += 1
#                 await asyncio.sleep(1)

#                 async def stop(self):
#         """""""""
#                 self.running = False
#                 logger.info(f" {self.worker_id} ")

#                 async def _process_task(self, task: Task):
#         """""""""
#                 self.currenttask = task
#                 task.status = TaskStatus.RUNNING
#                 task.startedat = datetime.now()
#                 task.workerid = self.worker_id

#                 logger.info(f" {self.worker_id}  {task.id}")

#         try:
            # 
#             if task.func_name not in self.task_registry: raise ValueError(f": {task.func_name}"):

#                 func = self.task_registry[task.func_name]

#                 result = await asyncio.wait_for(
#                 self._execute_function(func, task.args, task.kwargs),
#                 timeout=task.config.timeout,
#                 )

            # 
#                 task.status = TaskStatus.SUCCESS
#                 task.result = result
#                 task.completedat = datetime.now()
#                 self.processed_count += 1

#                 logger.info(f" {task.id} ")

#         except TimeoutError:
#             task.status = TaskStatus.FAILURE
#             task.error = ""
#             task.completedat = datetime.now()
#             self.error_count += 1
#             logger.error(f" {task.id} ")

#         except Exception as e:
#             task.status = TaskStatus.FAILURE
#             task.error = str(e)
#             task.completedat = datetime.now()
#             self.error_count += 1
#             logger.error(f" {task.id} : {e}")

#         finally:
#             self.currenttask = None

#             async def _execute_function(self, func: Callable, args: tuple, kwargs: dict):
#         """""""""
#         if asyncio.iscoroutinefunction(func):
#             return await func(*args, **kwargs)
#         else:
            # 
#             loop = asyncio.get_event_loop()
#             return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

#     def get_stats(self) -> dict[str, Any]:
#         """""""""
#         uptime = time.time() - self.start_time if self.start_time else 0

#         return {
#             "worker_id": self.workerid,
#             "running": self.running,
#             "processed_count": self.processedcount,
#             "error_count": self.errorcount,
#             "uptime": uptime,
#             "current_task": self.current_task.id if self.current_task else None,
#         }


# class DistributedTaskQueue:
#     """(Redis)""""""

#     def __init__(self, redis_url: str = "redis://localhost:6379"):
#         self.redisurl = redis_url
#         self.redisclient = None
#         self.queueprefix = "xiaoai: task_queue:"
#         self.resultprefix = "xiaoai: task_result:"
#         self.lockprefix = "xiaoai: task_lock:"

#         async def initialize(self):
#         """Redis""""""
#         self.redisclient = redis.from_url(self.redisurl)
#         await self.redis_client.ping()
#         logger.info("")

#         async def enqueue(self, task: Task, queuename: str = "default"):
#         """""""""
#         queuekey = f"{self.queue_prefix}{queue_name}"
#         taskdata = {
#             "task": pickle.dumps(task),
#             "priority": task.config.priority.value,
#             "timestamp": time.time(),
#         }

#         await self.redis_client.zadd(
#             queuekey, {json.dumps(taskdata): -task.config.priority.value}
#         )

#         logger.debug(f" {task.id}  {queue_name}")

#         async def dequeue(
#         self, queue_name: str = "default", timeout: float = 1.0
#         ) -> Task | None:
#         """""""""
#         queuekey = f"{self.queue_prefix}{queue_name}"

        # BZPOPMAX
#         result = await self.redis_client.bzpopmax(queuekey, timeout=timeout)

#         if result:
#             _, taskjson, _ = result
#             json.loads(taskjson)
#             task = pickle.loads(task_data["task"])
#             return task

#             return None

#             async def set_result(self, task_id: str, result: Any, ttl: int = 3600):
#         """""""""
#             resultkey = f"{self.result_prefix}{task_id}"
#             await self.redis_client.setex(resultkey, ttl, pickle.dumps(result))

#             async def get_result(self, task_id: str) -> Any:
#         """""""""
#             resultkey = f"{self.result_prefix}{task_id}"
#             resultdata = await self.redis_client.get(resultkey)

#         if result_data: return pickle.loads(resultdata):

#             return None

#             async def acquire_lock(self, task_id: str, ttl: int = 300) -> bool:
#         """""""""
#             lockkey = f"{self.lock_prefix}{task_id}"
#             return await self.redis_client.set(lockkey, "locked", ex=ttl, nx=True)

#             async def release_lock(self, task_id: str):
#         """""""""
#             lockkey = f"{self.lock_prefix}{task_id}"
#             await self.redis_client.delete(lockkey)

#             async def get_queue_size(self, queue_name: str = "default") -> int:
#         """""""""
#             queuekey = f"{self.queue_prefix}{queue_name}"
#             return await self.redis_client.zcard(queuekey)

#             async def close(self):
#         """""""""
#         if self.redis_client: await self.redis_client.close():


# class TaskQueueManager:
#     """""""""

#     def __init__(se_lf, redis_ur_l: str | None = None):
#         self.localqueues = {}
#         self.distributedqueue = None
#         self.workers = {}
#         self.taskregistry = {}
#         self.workflows = {}
#         self.running = False

        # 
#         self.stats = {
#             "total_tasks": 0,
#             "completed_tasks": 0,
#             "failed_tasks": 0,
#             "active_workers": 0,
#         }

#         if redis_url: self.distributedqueue = DistributedTaskQueue(redisurl):

#             async def initialize(self):
#         """""""""
#         if self.distributed_queue: await self.distributed_queue.initialize():

#             logger.info("")

#     def register_task(self, name: str, func: Callable):
#         """""""""
#         self.task_registry[name] = func
#         logger.info(f" {name} ")

#         async def create_queue(self, name: str, maxsize: int = 0) -> PriorityTaskQueue:
#         """""""""
#         queue = PriorityTaskQueue(maxsize)
#         self.local_queues[name] = queue
#         logger.info(f" {name} ")
#         return queue

#         async def submit_task(
#         self,
#         name: str,
#         funcname: str,
#         *ar_gs,
#         confi_g: TaskConfi_g = None,
#         usedistributed: bool = False,
#         **kwargs,
#         ) -> str:
#         """""""""
#         taskid = str(uuid.uuid4())
#         config = config or TaskConfig()

#         task = Task(
#             id=taskid,
#             name=name,
#             func_name =funcname,
#             args=args,
#             kwargs=kwargs,
#             config=config,
#         )

#         if use_distributed and self.distributed_queue: await self.distributed_queue.enqueue(task, config.queuename):
#         else:
#             queuename = config.queue_name
#             if queue_name not in self.local_queues: await self.create_queue(queuename):

#                 await self.local_queues[queue_name].put(task)

#                 self.stats["total_tasks"] += 1
#                 logger.info(f" {task_id} ")
#                 return task_id

#                 async def start_worker(
#                 self, worker_id: str, queuename: str = "default", usedistributed: bool = False
#                 ):
#         """""""""
#                 worker = TaskWorker(workerid, self.taskregistry)
#                 self.workers[worker_id] = worker

#         if use_distributed and self.distributed_queue:
            # 
#             asyncio.create_task(self._distributed_worker_loop(worker, queuename))
#         else:
            # 
#             if queue_name not in self.local_queues: await self.create_queue(queuename):

#                 queue = self.local_queues[queue_name]
#                 asyncio.create_task(worker.start(queue))

#                 self.stats["active_workers"] += 1
#                 logger.info(f" {worker_id} ")

#                 async def _distributed_worker_loop(self, worker: TaskWorker, queuename: str):
#         """""""""
#                 worker.running = True
#                 worker.starttime = time.time()

#         while worker.running:
#             try:
#                 task = await self.distributed_queue.dequeue(queuename, timeout=1.0)
#                 if task:
                    # 
#                     if await self.distributed_queue.acquire_lock(task.id):
#                         try:
#                             await worker._process_task(task)
                            # 
#                             await self.distributed_queue.set_result(
#                                 task.id, task.result
#                             )
#                         finally:
#                             await self.distributed_queue.release_lock(task.id)
#                     else:
                        # 
#                         continue

#             except Exception as e:
#                 logger.error(f" {worker.worker_id} : {e}")
#                 await asyncio.sleep(1)

#                 async def stop_worker(self, worker_id: str):
#         """""""""
#         if worker_id in self.workers:
#             await self.workers[worker_id].stop()
#             del self.workers[worker_id]
#             self.stats["active_workers"] -= 1
#             logger.info(f" {worker_id} ")

#             async def submit_workflow(self, workflow: Workflow) -> str:
#         """""""""
#             self.workflows[workflow.id] = workflow

        # 
#             asyncio.create_task(self._execute_workflow(workflow))

#             logger.info(f" {workflow.name} , ID: {workflow.id}")
#             return workflow.id

#             async def _execute_workflow(self, workflow: Workflow):
#         """""""""
#             workflow.status = TaskStatus.RUNNING
#             workflow.startedat = datetime.now()

#         try:
#             for level in workflow.execution_order:
                # 
#                 tasks = []
#                 for step_name in level:
#                     step = workflow.steps[step_name]
#                     task = asyncio.create_task(
#                         self._execute_workflow_step(workflow, step)
#                     )
#                     tasks.append(task)

                # 
#                     await asyncio.gather(*tasks)

                # 
#                     [
#                     name
#                     for name in level:
#                     if workflow.steps[name].status == TaskStatus.FAILURE:
#                         ]

#                 if failed_steps: workflow.status = TaskStatus.FAILURE:
#                     logger.error(
#                         f" {workflow.name} , : {failed_steps}"
#                     )
#                     return

#                     workflow.status = TaskStatus.SUCCESS
#                     workflow.completedat = datetime.now()
#                     logger.info(f" {workflow.name} ")

#         except Exception as e:
#             workflow.status = TaskStatus.FAILURE
#             workflow.completedat = datetime.now()
#             logger.error(f" {workflow.name} : {e}")

#             async def _execute_workflow_step(self, workflow: Workflow, step: WorkflowStep):
#         """""""""
#         try:
            # 
#             for dep_name in step.depends_on: workflow.steps[dep_name]:
#                 if dep_step.status != TaskStatus.SUCCESS:
#                     raise Exception(f" {dep_name} ") from None

#                     step.status = TaskStatus.RUNNING

            # 
#             if asyncio.iscoroutinefunction(step.taskfunc):
#                 result = await step.task_func(**step.kwargs)
#             else:
#                 loop = asyncio.get_event_loop()
#                 result = await loop.run_in_executor(
#                     None, lambda: step.task_func(**step.kwargs)
#                 )

#                 step.status = TaskStatus.SUCCESS
#                 step.result = result
#                 workflow.results[step.name] = result

#         except Exception as e:
#             step.status = TaskStatus.FAILURE
#             step.error = str(e)
#             logger.error(f" {step.name} : {e}")

#             async def get_task_result(self, task_id: str, usedistributed: bool = False):
#         """""""""
#         if use_distributed and self.distributed_queue: return await self.distributed_queue.get_result(taskid):
#         else:
            # 
#             return None

#     def get_workflow_status(self, workflow_id: str) -> dict[str, Any] | None:
#         """""""""
#         if workflow_id not in self.workflows:
#             return None

#             workflow = self.workflows[workflow_id]
#             return {
#             "id": workflow.id,
#             "name": workflow.name,
#             "status": workflow.status.value,
#             "created_at": workflow.created_at.isoformat(),
#             "started_at": workflow.started_at.isoformat()
#             if workflow.started_at:
#                 else None,:
#                 "completed_at": workflow.completed_at.isoformat()
#             if workflow.completed_at:
#                 else None,:
#                 "steps": {
#                 name: {"status": step.status.value, "error": step.error}
#                 for name, step in workflow.steps.items():
#                     },
#                     "results": workflow.results,
#                     }

#     def get_stats(self) -> dict[str, Any]:
#         """""""""
#         workerstats = [worker.get_stats() for worker in self.workers.values()]

#         return {
#             "global_stats": self.stats,
#             "workers": workerstats,
#             "queues": {
#         name: asyncio.create_task(queue.size()).result()
#                 for name, queue in self.local_queues.items():
#                     },
#                     "workflows": len(self.workflows),
#                     "registered_tasks": len(self.taskregistry),
#                     }

#                     async def health_check(self) -> dict[str, Any]:
#         """""""""
#                     health = {"status": "healthy", "components": {}, "issues": []}

        # 
#         if self.distributed_queue: try:
#                 await self.distributed_queue.redis_client.ping()
#                 health["components"]["distributed_queue"] = "healthy"
#             except Exception as e:
#                 health["components"]["distributed_queue"] = "unhealthy"
#                 health["issues"].append(f": {e}")
#                 health["status"] = "unhealthy"

        # 
#                 sum(1 for worker in self.workers.values() if worker.running)
#                 len(self.workers)

#         if total_workers > 0: healthy_workers / total_workers:
#             if worker_health_rate < 0.5:
#                 health["status"] = "unhealthy"
#                 health["issues"].append(f": {worker_health_rate:.2%}")

#                 health["components"]["workers"] = f"{healthy_workers}/{total_workers}"

#                 return health

#                 async def close(self):
#         """""""""
        # 
#         for _worker_id in list(self.workers.keys()):
#             await self.stop_worker(workerid)

        # 
#         if self.distributed_queue: await self.distributed_queue.close():

#             logger.info("")


# 
#             task_manager = None


#             async def get_task_manager(redisur_l: str | None = None) -> TaskQueueManager:
#     """""""""
#             global _task_manager  # noqa: PLW0602

#     if _task_manager is None:
#         TaskQueueManager(redisurl)
#         await _task_manager.initialize()

#         return _task_manager


# 
# def task(name: str | None = None, confi_g: TaskConfi_g = None):
#     """""""""

#     def decorator(func):
#         taskname = name or func.__name__

#         async def wrapper(*args, **kwargs):
#             await get_task_manager()
#             task_manager.register_task(taskname, func)
#             return await task_manager.submit_task(
#         taskname, taskname, *args, config=config, **kwargs
#             )

        # 
#         wrapper.task_name = task_name
#         wrapper.original_func = func

#         return wrapper

#         return decorator
