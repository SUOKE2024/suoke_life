"""
distributed_computing - 索克生活项目模块
"""

                import psutil
            import cupy
        import psutil
    import sys
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
import asyncio
import hashlib
import json
import logging
import multiprocessing
import numpy as np
import pickle
import redis
import socket
import threading
import time
import zmq
import zmq.asyncio

#!/usr/bin/env python3
"""
索克生活 - 分布式计算集成模块
支持多节点计算、任务分发、结果聚合等功能
"""


logger = logging.getLogger(__name__)


class NodeType(Enum):
    """节点类型"""
    MASTER = "master"           # 主节点
    WORKER = "worker"           # 工作节点
    COORDINATOR = "coordinator" # 协调节点
    STORAGE = "storage"         # 存储节点


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"         # 等待中
    ASSIGNED = "assigned"       # 已分配
    RUNNING = "running"         # 运行中
    COMPLETED = "completed"     # 已完成
    FAILED = "failed"           # 失败
    CANCELLED = "cancelled"     # 已取消


class ComputeMode(Enum):
    """计算模式"""
    MAP_REDUCE = "map_reduce"           # MapReduce模式
    PARAMETER_SERVER = "parameter_server" # 参数服务器模式
    PEER_TO_PEER = "peer_to_peer"       # 点对点模式
    PIPELINE = "pipeline"               # 流水线模式
    BROADCAST = "broadcast"             # 广播模式


@dataclass
class NodeInfo:
    """节点信息"""
    node_id: str
    node_type: NodeType
    host: str
    port: int
    capabilities: Dict[str, Any]
    status: str = "active"
    last_heartbeat: Optional[datetime] = None
    load: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0


@dataclass
class DistributedTask:
    """分布式任务"""
    task_id: str
    task_type: str
    function_name: str
    input_data: Any
    parameters: Dict[str, Any]
    compute_mode: ComputeMode
    priority: int = 5
    timeout: int = 300
    retry_count: int = 3
    created_at: datetime = None
    status: TaskStatus = TaskStatus.PENDING
    assigned_nodes: List[str] = None
    result: Any = None
    error: Optional[str] = None


@dataclass
class DistributedConfig:
    """分布式配置"""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    zmq_base_port: int = 5555
    heartbeat_interval: int = 30
    task_timeout: int = 300
    max_retries: int = 3
    enable_compression: bool = True
    enable_encryption: bool = False
    data_serialization: str = "pickle"  # pickle, json, msgpack


class DistributedComputeNode:
    """分布式计算节点"""
    
    def __init__(self, node_id: str, node_type: NodeType, 
                 host: str = "localhost", port: int = None,
                 config: Optional[DistributedConfig] = None):
        self.node_id = node_id
        self.node_type = node_type
        self.host = host
        self.port = port or self._get_free_port()
        self.config = config or DistributedConfig()
        
        # 节点状态
        self.is_running = False
        self.capabilities = self._detect_capabilities()
        self.load = 0.0
        
        # 通信组件
        self.redis_client = None
        self.zmq_context = None
        self.zmq_socket = None
        
        # 任务管理
        self.active_tasks = {}
        self.task_history = {}
        self.task_queue = asyncio.Queue()
        
        # 线程池
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.process_pool = ProcessPoolExecutor(max_workers=2)
        
        # 注册的函数
        self.registered_functions = {}
        
        # 初始化组件
        self._initialize_components()
    
    def _get_free_port(self) -> int:
        """获取空闲端口"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    def _detect_capabilities(self) -> Dict[str, Any]:
        """检测节点能力"""
        
        return {
            "cpu_count": multiprocessing.cpu_count(),
            "memory_gb": psutil.virtual_memory().total / (1024**3),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "numpy_available": True,
            "gpu_available": self._check_gpu_availability(),
            "max_concurrent_tasks": multiprocessing.cpu_count() * 2
        }
    
    def _check_gpu_availability(self) -> bool:
        """检查GPU可用性"""
        try:
            return cupy.cuda.is_available()
        except ImportError:
            return False
    
    def _initialize_components(self):
        """初始化组件"""
        try:
            # 初始化Redis连接
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                decode_responses=True
            )
            
            # 初始化ZMQ
            self.zmq_context = zmq.asyncio.Context()
            
            if self.node_type == NodeType.MASTER:
                self.zmq_socket = self.zmq_context.socket(zmq.REP)
                self.zmq_socket.bind(f"tcp://*:{self.port}")
            else:
                self.zmq_socket = self.zmq_context.socket(zmq.REQ)
            
            logger.info(f"节点 {self.node_id} 初始化完成")
            
        except Exception as e:
            logger.error(f"节点初始化失败: {e}")
            raise
    
    async def start(self):
        """启动节点"""
        self.is_running = True
        
        # 注册节点
        await self._register_node()
        
        # 启动心跳
        asyncio.create_task(self._heartbeat_loop())
        
        # 启动任务处理
        asyncio.create_task(self._task_processing_loop())
        
        # 启动消息监听
        if self.node_type == NodeType.MASTER:
            asyncio.create_task(self._master_message_loop())
        else:
            asyncio.create_task(self._worker_message_loop())
        
        logger.info(f"节点 {self.node_id} 已启动")
    
    async def stop(self):
        """停止节点"""
        self.is_running = False
        
        # 注销节点
        await self._unregister_node()
        
        # 清理资源
        if self.zmq_socket:
            self.zmq_socket.close()
        if self.zmq_context:
            self.zmq_context.term()
        
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        
        logger.info(f"节点 {self.node_id} 已停止")
    
    async def _register_node(self):
        """注册节点"""
        node_info = NodeInfo(
            node_id=self.node_id,
            node_type=self.node_type,
            host=self.host,
            port=self.port,
            capabilities=self.capabilities,
            last_heartbeat=datetime.now()
        )
        
        # 存储到Redis
        self.redis_client.hset(
            "distributed:nodes",
            self.node_id,
            json.dumps(asdict(node_info), default=str)
        )
        
        logger.info(f"节点 {self.node_id} 已注册")
    
    async def _unregister_node(self):
        """注销节点"""
        self.redis_client.hdel("distributed:nodes", self.node_id)
        logger.info(f"节点 {self.node_id} 已注销")
    
    async def _heartbeat_loop(self):
        """心跳循环"""
        while self.is_running:
            try:
                # 更新心跳时间
                self.redis_client.hset(
                    f"distributed:heartbeat:{self.node_id}",
                    "timestamp",
                    datetime.now().isoformat()
                )
                
                # 更新负载信息
                self.load = len(self.active_tasks)
                cpu_usage = psutil.cpu_percent()
                memory_usage = psutil.virtual_memory().percent
                
                self.redis_client.hset(
                    f"distributed:heartbeat:{self.node_id}",
                    "load",
                    self.load
                )
                self.redis_client.hset(
                    f"distributed:heartbeat:{self.node_id}",
                    "cpu_usage",
                    cpu_usage
                )
                self.redis_client.hset(
                    f"distributed:heartbeat:{self.node_id}",
                    "memory_usage",
                    memory_usage
                )
                
                await asyncio.sleep(self.config.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"心跳发送失败: {e}")
                await asyncio.sleep(5)
    
    async def _task_processing_loop(self):
        """任务处理循环"""
        while self.is_running:
            try:
                # 从队列获取任务
                task = await asyncio.wait_for(
                    self.task_queue.get(), 
                    timeout=1.0
                )
                
                # 处理任务
                await self._process_task(task)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"任务处理失败: {e}")
    
    async def _process_task(self, task: DistributedTask):
        """处理单个任务"""
        task.status = TaskStatus.RUNNING
        self.active_tasks[task.task_id] = task
        
        try:
            # 获取注册的函数
            if task.function_name not in self.registered_functions:
                raise ValueError(f"未注册的函数: {task.function_name}")
            
            func = self.registered_functions[task.function_name]
            
            # 执行任务
            if asyncio.iscoroutinefunction(func):
                result = await func(task.input_data, **task.parameters)
            else:
                # 在线程池中执行同步函数
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.thread_pool,
                    func,
                    task.input_data,
                    **task.parameters
                )
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            
            # 存储结果
            await self._store_task_result(task)
            
            logger.info(f"任务 {task.task_id} 完成")
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            logger.error(f"任务 {task.task_id} 失败: {e}")
        
        finally:
            # 从活跃任务中移除
            self.active_tasks.pop(task.task_id, None)
            self.task_history[task.task_id] = task
    
    async def _store_task_result(self, task: DistributedTask):
        """存储任务结果"""
        result_data = {
            "task_id": task.task_id,
            "status": task.status.value,
            "result": self._serialize_data(task.result),
            "error": task.error,
            "completed_at": datetime.now().isoformat(),
            "node_id": self.node_id
        }
        
        self.redis_client.hset(
            "distributed:results",
            task.task_id,
            json.dumps(result_data)
        )
    
    async def _master_message_loop(self):
        """主节点消息循环"""
        while self.is_running:
            try:
                # 接收消息
                message = await self.zmq_socket.recv_json()
                
                # 处理消息
                response = await self._handle_master_message(message)
                
                # 发送响应
                await self.zmq_socket.send_json(response)
                
            except Exception as e:
                logger.error(f"主节点消息处理失败: {e}")
    
    async def _worker_message_loop(self):
        """工作节点消息循环"""
        # 工作节点主要通过Redis和任务队列工作
        pass
    
    async def _handle_master_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理主节点消息"""
        msg_type = message.get("type")
        
        if msg_type == "submit_task":
            return await self._handle_submit_task(message)
        elif msg_type == "get_task_status":
            return await self._handle_get_task_status(message)
        elif msg_type == "cancel_task":
            return await self._handle_cancel_task(message)
        elif msg_type == "get_cluster_status":
            return await self._handle_get_cluster_status(message)
        else:
            return {"status": "error", "message": f"未知消息类型: {msg_type}"}
    
    async def _handle_submit_task(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理任务提交"""
        try:
            task_data = message["task"]
            task = DistributedTask(**task_data)
            
            # 选择工作节点
            selected_nodes = await self._select_worker_nodes(task)
            
            if not selected_nodes:
                return {
                    "status": "error",
                    "message": "没有可用的工作节点"
                }
            
            # 分发任务
            await self._distribute_task(task, selected_nodes)
            
            return {
                "status": "success",
                "task_id": task.task_id,
                "assigned_nodes": selected_nodes
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _select_worker_nodes(self, task: DistributedTask) -> List[str]:
        """选择工作节点"""
        # 获取所有活跃的工作节点
        nodes_data = self.redis_client.hgetall("distributed:nodes")
        worker_nodes = []
        
        for node_id, node_data in nodes_data.items():
            node_info = json.loads(node_data)
            if (node_info["node_type"] == NodeType.WORKER.value and
                node_info["status"] == "active"):
                
                # 检查心跳
                heartbeat_data = self.redis_client.hgetall(
                    f"distributed:heartbeat:{node_id}"
                )
                
                if heartbeat_data:
                    last_heartbeat = datetime.fromisoformat(
                        heartbeat_data["timestamp"]
                    )
                    
                    # 如果心跳在2分钟内，认为节点活跃
                    if datetime.now() - last_heartbeat < timedelta(minutes=2):
                        load = float(heartbeat_data.get("load", 0))
                        worker_nodes.append((node_id, load))
        
        # 按负载排序，选择负载最低的节点
        worker_nodes.sort(key=lambda x: x[1])
        
        # 根据计算模式选择节点数量
        if task.compute_mode == ComputeMode.MAP_REDUCE:
            # MapReduce需要多个节点
            return [node[0] for node in worker_nodes[:min(4, len(worker_nodes))]]
        else:
            # 其他模式选择一个节点
            return [worker_nodes[0][0]] if worker_nodes else []
    
    async def _distribute_task(self, task: DistributedTask, nodes: List[str]):
        """分发任务到工作节点"""
        task.assigned_nodes = nodes
        task.status = TaskStatus.ASSIGNED
        
        # 存储任务信息
        task_data = asdict(task)
        task_data["created_at"] = task.created_at.isoformat() if task.created_at else None
        
        self.redis_client.hset(
            "distributed:tasks",
            task.task_id,
            json.dumps(task_data, default=str)
        )
        
        # 将任务推送到工作节点队列
        for node_id in nodes:
            self.redis_client.lpush(
                f"distributed:queue:{node_id}",
                task.task_id
            )
        
        logger.info(f"任务 {task.task_id} 已分发到节点: {nodes}")
    
    def register_function(self, name: str, func: Callable):
        """注册可执行函数"""
        self.registered_functions[name] = func
        logger.info(f"函数 {name} 已注册")
    
    def _serialize_data(self, data: Any) -> str:
        """序列化数据"""
        if self.config.data_serialization == "pickle":
            return pickle.dumps(data).hex()
        elif self.config.data_serialization == "json":
            return json.dumps(data, default=str)
        else:
            return str(data)
    
    def _deserialize_data(self, data: str) -> Any:
        """反序列化数据"""
        if self.config.data_serialization == "pickle":
            return pickle.loads(bytes.fromhex(data))
        elif self.config.data_serialization == "json":
            return json.loads(data)
        else:
            return data


class DistributedComputeCluster:
    """分布式计算集群"""
    
    def __init__(self, config: Optional[DistributedConfig] = None):
        self.config = config or DistributedConfig()
        self.master_node = None
        self.worker_nodes = {}
        self.is_running = False
        
        # ZMQ客户端
        self.zmq_context = zmq.asyncio.Context()
        self.zmq_socket = None
    
    async def start_master(self, master_host: str = "localhost", 
                          master_port: int = 5555) -> DistributedComputeNode:
        """启动主节点"""
        self.master_node = DistributedComputeNode(
            node_id="master",
            node_type=NodeType.MASTER,
            host=master_host,
            port=master_port,
            config=self.config
        )
        
        # 注册内置函数
        self._register_builtin_functions(self.master_node)
        
        await self.master_node.start()
        
        # 连接到主节点
        self.zmq_socket = self.zmq_context.socket(zmq.REQ)
        self.zmq_socket.connect(f"tcp://{master_host}:{master_port}")
        
        self.is_running = True
        logger.info("分布式计算集群主节点已启动")
        
        return self.master_node
    
    async def add_worker(self, worker_id: str, 
                        host: str = "localhost") -> DistributedComputeNode:
        """添加工作节点"""
        worker_node = DistributedComputeNode(
            node_id=worker_id,
            node_type=NodeType.WORKER,
            host=host,
            config=self.config
        )
        
        # 注册内置函数
        self._register_builtin_functions(worker_node)
        
        # 启动工作节点任务监听
        asyncio.create_task(self._worker_task_listener(worker_node))
        
        await worker_node.start()
        self.worker_nodes[worker_id] = worker_node
        
        logger.info(f"工作节点 {worker_id} 已添加")
        return worker_node
    
    async def _worker_task_listener(self, worker_node: DistributedComputeNode):
        """工作节点任务监听器"""
        redis_client = worker_node.redis_client
        queue_key = f"distributed:queue:{worker_node.node_id}"
        
        while worker_node.is_running:
            try:
                # 从Redis队列获取任务
                task_id = redis_client.brpop(queue_key, timeout=1)
                
                if task_id:
                    task_id = task_id[1]  # brpop返回(key, value)
                    
                    # 获取任务详情
                    task_data = redis_client.hget("distributed:tasks", task_id)
                    
                    if task_data:
                        task_dict = json.loads(task_data)
                        task_dict["created_at"] = datetime.fromisoformat(
                            task_dict["created_at"]
                        ) if task_dict["created_at"] else None
                        
                        task = DistributedTask(**task_dict)
                        
                        # 添加到任务队列
                        await worker_node.task_queue.put(task)
                
            except Exception as e:
                logger.error(f"工作节点任务监听失败: {e}")
                await asyncio.sleep(1)
    
    def _register_builtin_functions(self, node: DistributedComputeNode):
        """注册内置函数"""
        # 中医证候分析
        node.register_function("tcm_syndrome_analysis", self._tcm_syndrome_analysis)
        
        # 健康数据处理
        node.register_function("health_data_processing", self._health_data_processing)
        
        # 营养优化
        node.register_function("nutrition_optimization", self._nutrition_optimization)
        
        # 大数据聚合
        node.register_function("data_aggregation", self._data_aggregation)
        
        # 模式识别
        node.register_function("pattern_recognition", self._pattern_recognition)
    
    async def submit_task(self, task_type: str, function_name: str,
                         input_data: Any, parameters: Dict[str, Any] = None,
                         compute_mode: ComputeMode = ComputeMode.MAP_REDUCE,
                         priority: int = 5) -> str:
        """提交分布式任务"""
        if not self.is_running:
            raise RuntimeError("集群未启动")
        
        task_id = f"task_{int(time.time() * 1000)}_{hash(str(input_data)) % 10000}"
        
        task = DistributedTask(
            task_id=task_id,
            task_type=task_type,
            function_name=function_name,
            input_data=input_data,
            parameters=parameters or {},
            compute_mode=compute_mode,
            priority=priority,
            created_at=datetime.now()
        )
        
        # 发送任务到主节点
        message = {
            "type": "submit_task",
            "task": asdict(task)
        }
        
        await self.zmq_socket.send_json(message)
        response = await self.zmq_socket.recv_json()
        
        if response["status"] == "success":
            return task_id
        else:
            raise RuntimeError(f"任务提交失败: {response['message']}")
    
    async def get_task_result(self, task_id: str, timeout: int = 300) -> Any:
        """获取任务结果"""
        start_time = time.time()
        redis_client = self.master_node.redis_client
        
        while time.time() - start_time < timeout:
            # 检查结果
            result_data = redis_client.hget("distributed:results", task_id)
            
            if result_data:
                result = json.loads(result_data)
                
                if result["status"] == "completed":
                    return self._deserialize_result(result["result"])
                elif result["status"] == "failed":
                    raise RuntimeError(f"任务失败: {result['error']}")
            
            await asyncio.sleep(1)
        
        raise TimeoutError(f"任务超时: {task_id}")
    
    def _deserialize_result(self, data: str) -> Any:
        """反序列化结果"""
        if self.config.data_serialization == "pickle":
            return pickle.loads(bytes.fromhex(data))
        elif self.config.data_serialization == "json":
            return json.loads(data)
        else:
            return data
    
    async def get_cluster_status(self) -> Dict[str, Any]:
        """获取集群状态"""
        message = {"type": "get_cluster_status"}
        
        await self.zmq_socket.send_json(message)
        response = await self.zmq_socket.recv_json()
        
        return response
    
    # 内置分布式函数
    async def _tcm_syndrome_analysis(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """分布式中医证候分析"""
        symptoms = np.array(data["symptoms"])
        weights = np.array(data["weights"])
        patterns = np.array(data["patterns"])
        
        # 计算证候评分
        weighted_symptoms = symptoms * weights
        scores = np.dot(patterns, weighted_symptoms)
        total = np.sum(scores)
        normalized_scores = scores / total if total > 0 else scores
        
        return {
            "syndrome_scores": normalized_scores.tolist(),
            "dominant_syndrome": int(np.argmax(normalized_scores)),
            "confidence": float(np.max(normalized_scores))
        }
    
    async def _health_data_processing(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """分布式健康数据处理"""
        health_data = np.array(data["health_data"])
        operation = kwargs.get("operation", "normalize")
        
        if operation == "normalize":
            mean = np.mean(health_data, axis=0)
            std = np.std(health_data, axis=0)
            std = np.where(std > 1e-8, std, 1.0)
            normalized = (health_data - mean) / std
            
            return {
                "processed_data": normalized.tolist(),
                "statistics": {
                    "mean": mean.tolist(),
                    "std": std.tolist(),
                    "shape": health_data.shape
                }
            }
        
        elif operation == "feature_extract":
            features = {
                "mean": np.mean(health_data, axis=1).tolist(),
                "std": np.std(health_data, axis=1).tolist(),
                "max": np.max(health_data, axis=1).tolist(),
                "min": np.min(health_data, axis=1).tolist()
            }
            
            return {"features": features}
        
        return {"error": f"未知操作: {operation}"}
    
    async def _nutrition_optimization(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """分布式营养优化"""
        user_profile = np.array(data["user_profile"])
        food_database = np.array(data["food_database"])
        
        # 计算余弦相似度
        user_norm = np.linalg.norm(user_profile)
        food_norms = np.linalg.norm(food_database, axis=1)
        
        if user_norm > 1e-8:
            dot_products = np.dot(food_database, user_profile)
            similarities = dot_products / (user_norm * food_norms + 1e-8)
        else:
            similarities = np.zeros(len(food_database))
        
        # 获取推荐食物
        top_indices = np.argsort(similarities)[::-1][:10]
        
        return {
            "similarity_scores": similarities.tolist(),
            "recommended_foods": top_indices.tolist(),
            "top_scores": similarities[top_indices].tolist()
        }
    
    async def _data_aggregation(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """分布式数据聚合"""
        datasets = data["datasets"]
        operation = kwargs.get("operation", "mean")
        
        if operation == "mean":
            result = np.mean([np.array(d) for d in datasets], axis=0)
        elif operation == "sum":
            result = np.sum([np.array(d) for d in datasets], axis=0)
        elif operation == "max":
            result = np.max([np.array(d) for d in datasets], axis=0)
        elif operation == "min":
            result = np.min([np.array(d) for d in datasets], axis=0)
        else:
            return {"error": f"未知聚合操作: {operation}"}
        
        return {
            "aggregated_data": result.tolist(),
            "operation": operation,
            "input_count": len(datasets)
        }
    
    async def _pattern_recognition(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """分布式模式识别"""
        input_data = np.array(data["input_data"])
        patterns = np.array(data["patterns"])
        threshold = kwargs.get("threshold", 0.8)
        
        matches = []
        
        for i, pattern in enumerate(patterns):
            # 计算相关系数
            correlation = np.corrcoef(input_data.flatten(), pattern.flatten())[0, 1]
            
            if not np.isnan(correlation) and correlation >= threshold:
                matches.append({
                    "pattern_id": i,
                    "correlation": float(correlation),
                    "match_strength": "strong" if correlation > 0.9 else "moderate"
                })
        
        return {
            "matches": matches,
            "total_patterns": len(patterns),
            "match_count": len(matches)
        }
    
    async def stop(self):
        """停止集群"""
        self.is_running = False
        
        # 停止所有工作节点
        for worker in self.worker_nodes.values():
            await worker.stop()
        
        # 停止主节点
        if self.master_node:
            await self.master_node.stop()
        
        # 清理ZMQ资源
        if self.zmq_socket:
            self.zmq_socket.close()
        if self.zmq_context:
            self.zmq_context.term()
        
        logger.info("分布式计算集群已停止")


# 便捷函数
async def create_distributed_cluster(num_workers: int = 2,
                                   config: Optional[DistributedConfig] = None) -> DistributedComputeCluster:
    """创建分布式计算集群"""
    cluster = DistributedComputeCluster(config)
    
    # 启动主节点
    await cluster.start_master()
    
    # 添加工作节点
    for i in range(num_workers):
        await cluster.add_worker(f"worker_{i}")
    
    return cluster


if __name__ == "__main__":
    
    async def test_distributed_computing():
        """测试分布式计算"""
        print("索克生活 - 分布式计算测试")
        
        try:
            # 创建集群
            cluster = await create_distributed_cluster(num_workers=2)
            
            # 测试中医证候分析
            tcm_data = {
                "symptoms": np.random.rand(20).tolist(),
                "weights": np.random.rand(20).tolist(),
                "patterns": np.random.rand(4, 20).tolist()
            }
            
            task_id = await cluster.submit_task(
                task_type="tcm_analysis",
                function_name="tcm_syndrome_analysis",
                input_data=tcm_data,
                compute_mode=ComputeMode.MAP_REDUCE
            )
            
            print(f"提交任务: {task_id}")
            
            # 获取结果
            result = await cluster.get_task_result(task_id, timeout=30)
            print(f"任务结果: {result}")
            
            # 测试健康数据处理
            health_data = {
                "health_data": np.random.rand(100, 30).tolist()
            }
            
            task_id2 = await cluster.submit_task(
                task_type="health_processing",
                function_name="health_data_processing",
                input_data=health_data,
                parameters={"operation": "normalize"}
            )
            
            result2 = await cluster.get_task_result(task_id2, timeout=30)
            print(f"健康数据处理结果形状: {np.array(result2['processed_data']).shape}")
            
            # 获取集群状态
            status = await cluster.get_cluster_status()
            print(f"集群状态: {status}")
            
            # 停止集群
            await cluster.stop()
            
        except Exception as e:
            print(f"测试失败: {e}")
    
    # 运行测试
    asyncio.run(test_distributed_computing()) 