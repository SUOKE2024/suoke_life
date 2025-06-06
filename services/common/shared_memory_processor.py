"""
shared_memory_processor - 索克生活项目模块
"""

from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime
from multiprocessing import shared_memory, Lock, Value, Array
from numba import jit, cuda
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
import asyncio
import logging
import multiprocessing
import threading
import uuid

#!/usr/bin/env python3
"""
索克生活 - 共享内存大数据处理器
实现跨进程的高效数据共享和大数据处理
"""


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SharedMemoryBlock:
    """共享内存块信息"""
    block_id: str
    name: str
    size: int
    dtype: str
    shape: Tuple[int, ...]
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    is_locked: bool = False
    owner_pid: int = None
    
    def __post_init__(self):
        if self.owner_pid is None:
            self.owner_pid = multiprocessing.current_process().pid

@dataclass
class ProcessingTask:
    """数据处理任务"""
    task_id: str
    task_type: str
    input_blocks: List[str]
    output_block: Optional[str]
    parameters: Dict[str, Any]
    created_at: datetime
    priority: int = 1
    timeout: float = 300.0
    
    def __post_init__(self):
        if not hasattr(self, 'created_at') or self.created_at is None:
            self.created_at = datetime.now()

class SharedMemoryManager:
    """共享内存管理器"""
    
    def __init__(self, max_memory_gb: float = 4.0):
        self.max_memory_bytes = int(max_memory_gb * 1024 * 1024 * 1024)
        self.blocks: Dict[str, SharedMemoryBlock] = {}
        self.shared_memories: Dict[str, shared_memory.SharedMemory] = {}
        self.lock = threading.Lock()
        self.cleanup_threshold = 0.8  # 内存使用率超过80%时清理
        
        # 内存使用统计
        self.total_allocated = 0
        self.peak_usage = 0
        
        logger.info(f"共享内存管理器初始化，最大内存: {max_memory_gb}GB")
    
    def create_shared_array(self, block_id: str, shape: Tuple[int, ...], 
                           dtype: np.dtype = np.float32) -> np.ndarray:
        """创建共享内存数组"""
        with self.lock:
            if block_id in self.blocks:
                raise ValueError(f"共享内存块已存在: {block_id}")
            
            # 计算所需内存大小
            size = int(np.prod(shape) * np.dtype(dtype).itemsize)
            
            # 检查内存限制
            if self.total_allocated + size > self.max_memory_bytes:
                self._cleanup_unused_blocks()
                if self.total_allocated + size > self.max_memory_bytes:
                    raise MemoryError(f"共享内存不足，需要 {size} 字节")
            
            # 创建共享内存
            shm_name = f"suoke_{block_id}_{uuid.uuid4().hex[:8]}"
            shm = shared_memory.SharedMemory(create=True, size=size, name=shm_name)
            
            # 创建numpy数组视图
            array = np.ndarray(shape, dtype=dtype, buffer=shm.buf)
            array.fill(0)  # 初始化为0
            
            # 记录块信息
            block_info = SharedMemoryBlock(
                block_id=block_id,
                name=shm_name,
                size=size,
                dtype=str(dtype),
                shape=shape,
                created_at=datetime.now(),
                last_accessed=datetime.now()
            )
            
            self.blocks[block_id] = block_info
            self.shared_memories[block_id] = shm
            self.total_allocated += size
            self.peak_usage = max(self.peak_usage, self.total_allocated)
            
            logger.info(f"创建共享内存块: {block_id}, 大小: {size} 字节, 形状: {shape}")
            return array
    
    def get_shared_array(self, block_id: str) -> Optional[np.ndarray]:
        """获取共享内存数组"""
        with self.lock:
            if block_id not in self.blocks:
                return None
            
            block_info = self.blocks[block_id]
            
            # 更新访问信息
            block_info.last_accessed = datetime.now()
            block_info.access_count += 1
            
            # 获取共享内存
            if block_id in self.shared_memories:
                shm = self.shared_memories[block_id]
            else:
                # 重新连接到现有共享内存
                try:
                    shm = shared_memory.SharedMemory(name=block_info.name)
                    self.shared_memories[block_id] = shm
                except FileNotFoundError:
                    logger.error(f"共享内存块不存在: {block_id}")
                    return None
            
            # 创建numpy数组视图
            dtype = np.dtype(block_info.dtype)
            array = np.ndarray(block_info.shape, dtype=dtype, buffer=shm.buf)
            
            return array
    
    def delete_shared_array(self, block_id: str):
        """删除共享内存数组"""
        with self.lock:
            if block_id not in self.blocks:
                return
            
            block_info = self.blocks[block_id]
            
            # 关闭共享内存
            if block_id in self.shared_memories:
                shm = self.shared_memories[block_id]
                try:
                    shm.close()
                    shm.unlink()
                except Exception as e:
                    logger.warning(f"删除共享内存时出错: {e}")
                del self.shared_memories[block_id]
            
            # 更新统计
            self.total_allocated -= block_info.size
            del self.blocks[block_id]
            
            logger.info(f"删除共享内存块: {block_id}")
    
    def _cleanup_unused_blocks(self):
        """清理未使用的内存块"""
        current_time = datetime.now()
        blocks_to_delete = []
        
        for block_id, block_info in self.blocks.items():
            # 删除超过1小时未访问的块
            if (current_time - block_info.last_accessed).total_seconds() > 3600:
                blocks_to_delete.append(block_id)
        
        for block_id in blocks_to_delete:
            self.delete_shared_array(block_id)
        
        logger.info(f"清理了 {len(blocks_to_delete)} 个未使用的内存块")
    
    @contextmanager
    def lock_block(self, block_id: str):
        """锁定内存块"""
        with self.lock:
            if block_id in self.blocks:
                self.blocks[block_id].is_locked = True
        
        try:
            yield
        finally:
            with self.lock:
                if block_id in self.blocks:
                    self.blocks[block_id].is_locked = False
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取内存使用统计"""
        with self.lock:
            return {
                "total_blocks": len(self.blocks),
                "total_allocated_bytes": self.total_allocated,
                "total_allocated_mb": self.total_allocated / (1024 * 1024),
                "peak_usage_bytes": self.peak_usage,
                "peak_usage_mb": self.peak_usage / (1024 * 1024),
                "usage_percentage": (self.total_allocated / self.max_memory_bytes) * 100,
                "max_memory_gb": self.max_memory_bytes / (1024 * 1024 * 1024),
                "blocks_info": {
                    block_id: {
                        "size_mb": block.size / (1024 * 1024),
                        "shape": block.shape,
                        "dtype": block.dtype,
                        "access_count": block.access_count,
                        "last_accessed": block.last_accessed.isoformat(),
                        "is_locked": block.is_locked
                    }
                    for block_id, block in self.blocks.items()
                }
            }

class BigDataProcessor:
    """大数据处理器"""
    
    def __init__(self, memory_manager: SharedMemoryManager, 
                 max_workers: Optional[int] = None):
        self.memory_manager = memory_manager
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.process_pool = ProcessPoolExecutor(max_workers=self.max_workers)
        self.processing_tasks: Dict[str, ProcessingTask] = {}
        self.lock = threading.Lock()
        
        logger.info(f"大数据处理器初始化，工作进程数: {self.max_workers}")
    
    @jit(nopython=True, parallel=True)
    def _jit_matrix_operations(self, data: np.ndarray, operation: str) -> np.ndarray:
        """JIT优化的矩阵运算"""
        if operation == "normalize":
            # 标准化
            mean = np.mean(data)
            std = np.std(data)
            return (data - mean) / std if std > 0 else data
        elif operation == "square":
            return data ** 2
        elif operation == "sqrt":
            return np.sqrt(np.abs(data))
        else:
            return data
    
    async def process_health_data_batch(self, input_block_id: str, 
                                      output_block_id: str,
                                      operation: str = "normalize") -> str:
        """批量处理健康数据"""
        task_id = str(uuid.uuid4())
        
        task = ProcessingTask(
            task_id=task_id,
            task_type="health_data_batch",
            input_blocks=[input_block_id],
            output_block=output_block_id,
            parameters={"operation": operation}
        )
        
        with self.lock:
            self.processing_tasks[task_id] = task
        
        # 异步执行处理
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.process_pool,
            self._process_health_data_worker,
            input_block_id,
            output_block_id,
            operation
        )
        
        logger.info(f"健康数据批处理完成: {task_id}")
        return task_id
    
    def _process_health_data_worker(self, input_block_id: str, 
                                  output_block_id: str, operation: str):
        """健康数据处理工作进程"""
        # 获取输入数据
        input_array = self.memory_manager.get_shared_array(input_block_id)
        if input_array is None:
            raise ValueError(f"输入数据块不存在: {input_block_id}")
        
        # 执行JIT优化的运算
        result = self._jit_matrix_operations(input_array, operation)
        
        # 创建或获取输出数组
        output_array = self.memory_manager.get_shared_array(output_block_id)
        if output_array is None:
            output_array = self.memory_manager.create_shared_array(
                output_block_id, result.shape, result.dtype
            )
        
        # 复制结果
        output_array[:] = result
        
        return output_block_id
    
    async def process_tcm_syndrome_analysis(self, symptoms_block_id: str,
                                          weights_block_id: str,
                                          result_block_id: str) -> str:
        """中医证候分析处理"""
        task_id = str(uuid.uuid4())
        
        task = ProcessingTask(
            task_id=task_id,
            task_type="tcm_syndrome_analysis",
            input_blocks=[symptoms_block_id, weights_block_id],
            output_block=result_block_id,
            parameters={}
        )
        
        with self.lock:
            self.processing_tasks[task_id] = task
        
        # 异步执行处理
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.process_pool,
            self._process_tcm_syndrome_worker,
            symptoms_block_id,
            weights_block_id,
            result_block_id
        )
        
        logger.info(f"中医证候分析完成: {task_id}")
        return task_id
    
    def _process_tcm_syndrome_worker(self, symptoms_block_id: str,
                                   weights_block_id: str, result_block_id: str):
        """中医证候分析工作进程"""
        # 获取症状和权重数据
        symptoms = self.memory_manager.get_shared_array(symptoms_block_id)
        weights = self.memory_manager.get_shared_array(weights_block_id)
        
        if symptoms is None or weights is None:
            raise ValueError("输入数据块不存在")
        
        # 执行证候分析计算
        syndrome_scores = self._calculate_syndrome_scores(symptoms, weights)
        
        # 创建结果数组
        result_array = self.memory_manager.get_shared_array(result_block_id)
        if result_array is None:
            result_array = self.memory_manager.create_shared_array(
                result_block_id, syndrome_scores.shape, syndrome_scores.dtype
            )
        
        result_array[:] = syndrome_scores
        return result_block_id
    
    @jit(nopython=True)
    def _calculate_syndrome_scores(self, symptoms: np.ndarray, 
                                 weights: np.ndarray) -> np.ndarray:
        """计算证候评分（JIT优化）"""
        # 加权症状评分
        weighted_symptoms = symptoms * weights
        
        # 计算各证候的匹配度
        syndrome_patterns = np.array([
            [1.0, 0.8, 0.6, 0.4],  # 气虚证
            [0.9, 1.0, 0.7, 0.5],  # 血瘀证
            [0.7, 0.9, 1.0, 0.8],  # 痰湿证
            [0.6, 0.7, 0.8, 1.0]   # 阴虚证
        ])
        
        scores = np.zeros(syndrome_patterns.shape[0])
        for i in range(syndrome_patterns.shape[0]):
            scores[i] = np.dot(weighted_symptoms, syndrome_patterns[i])
        
        return scores / np.sum(scores) if np.sum(scores) > 0 else scores
    
    async def process_nutrition_optimization(self, user_data_block_id: str,
                                           nutrition_db_block_id: str,
                                           result_block_id: str) -> str:
        """营养优化处理"""
        task_id = str(uuid.uuid4())
        
        task = ProcessingTask(
            task_id=task_id,
            task_type="nutrition_optimization",
            input_blocks=[user_data_block_id, nutrition_db_block_id],
            output_block=result_block_id,
            parameters={}
        )
        
        with self.lock:
            self.processing_tasks[task_id] = task
        
        # 异步执行处理
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.process_pool,
            self._process_nutrition_worker,
            user_data_block_id,
            nutrition_db_block_id,
            result_block_id
        )
        
        logger.info(f"营养优化处理完成: {task_id}")
        return task_id
    
    def _process_nutrition_worker(self, user_data_block_id: str,
                                nutrition_db_block_id: str, result_block_id: str):
        """营养优化工作进程"""
        # 获取用户数据和营养数据库
        user_data = self.memory_manager.get_shared_array(user_data_block_id)
        nutrition_db = self.memory_manager.get_shared_array(nutrition_db_block_id)
        
        if user_data is None or nutrition_db is None:
            raise ValueError("输入数据块不存在")
        
        # 执行营养优化算法
        optimization_result = self._optimize_nutrition(user_data, nutrition_db)
        
        # 创建结果数组
        result_array = self.memory_manager.get_shared_array(result_block_id)
        if result_array is None:
            result_array = self.memory_manager.create_shared_array(
                result_block_id, optimization_result.shape, optimization_result.dtype
            )
        
        result_array[:] = optimization_result
        return result_block_id
    
    @jit(nopython=True)
    def _optimize_nutrition(self, user_data: np.ndarray, 
                          nutrition_db: np.ndarray) -> np.ndarray:
        """营养优化算法（JIT优化）"""
        # 用户需求向量（蛋白质、碳水化合物、脂肪、维生素等）
        user_needs = user_data[:8]  # 假设前8个是营养需求
        
        # 计算每种食物的营养匹配度
        food_scores = np.zeros(nutrition_db.shape[0])
        
        for i in range(nutrition_db.shape[0]):
            food_nutrition = nutrition_db[i, :8]  # 食物营养成分
            
            # 计算匹配度（余弦相似度）
            dot_product = np.dot(user_needs, food_nutrition)
            norm_user = np.linalg.norm(user_needs)
            norm_food = np.linalg.norm(food_nutrition)
            
            if norm_user > 0 and norm_food > 0:
                food_scores[i] = dot_product / (norm_user * norm_food)
        
        return food_scores
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        with self.lock:
            return {
                "total_tasks": len(self.processing_tasks),
                "memory_stats": self.memory_manager.get_memory_stats(),
                "worker_count": self.max_workers,
                "tasks": {
                    task_id: {
                        "task_type": task.task_type,
                        "input_blocks": task.input_blocks,
                        "output_block": task.output_block,
                        "created_at": task.created_at.isoformat(),
                        "parameters": task.parameters
                    }
                    for task_id, task in self.processing_tasks.items()
                }
            }

class SharedMemoryDataPipeline:
    """共享内存数据管道"""
    
    def __init__(self, max_memory_gb: float = 4.0, max_workers: Optional[int] = None):
        self.memory_manager = SharedMemoryManager(max_memory_gb)
        self.processor = BigDataProcessor(self.memory_manager, max_workers)
        self.pipelines: Dict[str, List[Callable]] = {}
        
        logger.info("共享内存数据管道初始化完成")
    
    def register_pipeline(self, pipeline_name: str, 
                         processing_steps: List[Callable]):
        """注册数据处理管道"""
        self.pipelines[pipeline_name] = processing_steps
        logger.info(f"注册数据管道: {pipeline_name}, 步骤数: {len(processing_steps)}")
    
    async def execute_pipeline(self, pipeline_name: str, 
                             input_data: np.ndarray,
                             pipeline_params: Dict[str, Any] = None) -> str:
        """执行数据处理管道"""
        if pipeline_name not in self.pipelines:
            raise ValueError(f"未知的数据管道: {pipeline_name}")
        
        pipeline_id = str(uuid.uuid4())
        steps = self.pipelines[pipeline_name]
        params = pipeline_params or {}
        
        # 创建输入数据块
        input_block_id = f"{pipeline_id}_input"
        input_array = self.memory_manager.create_shared_array(
            input_block_id, input_data.shape, input_data.dtype
        )
        input_array[:] = input_data
        
        current_block_id = input_block_id
        
        # 逐步执行管道
        for i, step in enumerate(steps):
            step_output_id = f"{pipeline_id}_step_{i}"
            
            # 执行处理步骤
            await step(current_block_id, step_output_id, params)
            
            # 清理中间结果（保留最后一个）
            if i > 0:
                self.memory_manager.delete_shared_array(current_block_id)
            
            current_block_id = step_output_id
        
        logger.info(f"数据管道执行完成: {pipeline_name} -> {current_block_id}")
        return current_block_id
    
    async def health_data_analysis_pipeline(self, health_data: np.ndarray) -> str:
        """健康数据分析管道"""
        async def normalize_step(input_id: str, output_id: str, params: Dict):
            await self.processor.process_health_data_batch(
                input_id, output_id, "normalize"
            )
        
        async def feature_extraction_step(input_id: str, output_id: str, params: Dict):
            await self.processor.process_health_data_batch(
                input_id, output_id, "square"
            )
        
        # 注册管道
        self.register_pipeline("health_analysis", [
            normalize_step,
            feature_extraction_step
        ])
        
        # 执行管道
        return await self.execute_pipeline("health_analysis", health_data)
    
    def cleanup_all(self):
        """清理所有共享内存"""
        for block_id in list(self.memory_manager.blocks.keys()):
            self.memory_manager.delete_shared_array(block_id)
        
        logger.info("所有共享内存已清理")

# 全局实例
shared_memory_pipeline = SharedMemoryDataPipeline()

async def initialize_shared_memory_system(max_memory_gb: float = 4.0,
                                        max_workers: Optional[int] = None):
    """初始化共享内存系统"""
    global shared_memory_pipeline
    shared_memory_pipeline = SharedMemoryDataPipeline(max_memory_gb, max_workers)
    logger.info("共享内存系统初始化完成")
    return shared_memory_pipeline

def cleanup_shared_memory_system():
    """清理共享内存系统"""
    global shared_memory_pipeline
    if shared_memory_pipeline:
        shared_memory_pipeline.cleanup_all() 