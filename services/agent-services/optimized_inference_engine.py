#!/usr/bin/env python3
"""
索克生活 - 优化后的AI推理引擎
实现跨进程内存隔离、异步I/O和JIT编译优化
"""

import asyncio
import time
import multiprocessing
import numpy as np
import psutil
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import shared_memory, Queue, Manager
from typing import List, Dict, Any, Optional, Union, Callable
import json
import logging
from dataclasses import dataclass, asdict
from numba import jit, cuda
import pickle
import threading
from contextlib import asynccontextmanager
from abc import ABC, abstractmethod
import uuid
from datetime import datetime
import aiohttp
import asyncpg
from functools import lru_cache, wraps


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class InferenceRequest:
    """推理请求数据结构"""
    request_id: str
    agent_type: str  # xiaoai, xiaoke, laoke, soer
    input_data: Dict[str, Any]
    priority: int = 1  # 1-10, 10为最高优先级
    timeout: float = 30.0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class InferenceResult:
    """推理结果数据结构"""
    request_id: str
    agent_type: str
    result: Dict[str, Any]
    execution_time: float
    memory_usage: float
    success: bool
    error_message: Optional[str] = None
    completed_at: datetime = None
    
    def __post_init__(self):
        if self.completed_at is None:
            self.completed_at = datetime.now()


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'peak_memory_usage': 0.0,
            'cpu_utilization': 0.0
        }
        self.request_times = []
        self.lock = threading.Lock()
    
    def record_request(self, execution_time: float, memory_usage: float, success: bool):
        """记录请求性能指标"""
        with self.lock:
            self.metrics['total_requests'] += 1
            if success:
                self.metrics['successful_requests'] += 1
            else:
                self.metrics['failed_requests'] += 1
            
            self.request_times.append(execution_time)
            if len(self.request_times) > 1000:  # 保持最近1000个请求的记录
                self.request_times.pop(0)
            
            self.metrics['average_response_time'] = sum(self.request_times) / len(self.request_times)
            self.metrics['peak_memory_usage'] = max(self.metrics['peak_memory_usage'], memory_usage)
            self.metrics['cpu_utilization'] = psutil.cpu_percent()
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        with self.lock:
            return self.metrics.copy()


class JITOptimizedAlgorithms:
    """JIT优化的核心算法"""
    
    @staticmethod
    @jit(nopython=True, cache=True)
    def tcm_syndrome_analysis(symptoms: np.ndarray, weights: np.ndarray) -> np.ndarray:
        """中医辨证分析算法 - JIT优化版本"""
        result = np.zeros(symptoms.shape[0])
        for i in range(symptoms.shape[0]):
            score = 0.0
            for j in range(symptoms.shape[1]):
                score += symptoms[i, j] * weights[j]
            result[i] = score
        return result
    
    @staticmethod
    @jit(nopython=True, cache=True)
    def health_risk_calculation(biomarkers: np.ndarray, risk_factors: np.ndarray) -> float:
        """健康风险计算算法 - JIT优化版本"""
        risk_score = 0.0
        for i in range(len(biomarkers)):
            risk_score += biomarkers[i] * risk_factors[i]
        return min(max(risk_score, 0.0), 1.0)  # 限制在0-1范围内
    
    @staticmethod
    @jit(nopython=True, cache=True)
    def personalized_recommendation_scoring(user_profile: np.ndarray, 
                                          recommendations: np.ndarray) -> np.ndarray:
        """个性化推荐评分算法 - JIT优化版本"""
        scores = np.zeros(recommendations.shape[0])
        for i in range(recommendations.shape[0]):
            similarity = 0.0
            for j in range(len(user_profile)):
                similarity += user_profile[j] * recommendations[i, j]
            scores[i] = similarity
        return scores
    
    @staticmethod
    @jit(nopython=True, cache=True)
    def multi_agent_consensus(agent_outputs: np.ndarray, confidence_weights: np.ndarray) -> np.ndarray:
        """多智能体共识算法 - JIT优化版本"""
        weighted_sum = np.zeros(agent_outputs.shape[1])
        total_weight = 0.0
        
        for i in range(agent_outputs.shape[0]):
            weight = confidence_weights[i]
            total_weight += weight
            for j in range(agent_outputs.shape[1]):
                weighted_sum[j] += agent_outputs[i, j] * weight
        
        if total_weight > 0:
            for j in range(len(weighted_sum)):
                weighted_sum[j] /= total_weight
        
        return weighted_sum


class SharedMemoryManager:
    """共享内存管理器"""
    
    def __init__(self):
        self.shared_arrays = {}
        self.lock = threading.Lock()
    
    def create_shared_array(self, name: str, shape: tuple, dtype=np.float32) -> np.ndarray:
        """创建共享内存数组"""
        with self.lock:
            if name in self.shared_arrays:
                return self.shared_arrays[name]['array']
            
            size = np.prod(shape) * np.dtype(dtype).itemsize
            shm = shared_memory.SharedMemory(create=True, size=size, name=name)
            array = np.ndarray(shape, dtype=dtype, buffer=shm.buf)
            
            self.shared_arrays[name] = {
                'shm': shm,
                'array': array,
                'shape': shape,
                'dtype': dtype
            }
            
            return array
    
    def get_shared_array(self, name: str) -> Optional[np.ndarray]:
        """获取共享内存数组"""
        with self.lock:
            if name in self.shared_arrays:
                return self.shared_arrays[name]['array']
            return None
    
    def cleanup(self):
        """清理共享内存"""
        with self.lock:
            for name, info in self.shared_arrays.items():
                try:
                    info['shm'].close()
                    info['shm'].unlink()
                except:
                    pass
            self.shared_arrays.clear()


class AsyncDatabasePool:
    """异步数据库连接池"""
    
    def __init__(self, database_url: str, min_size: int = 5, max_size: int = 20):
        self.database_url = database_url
        self.min_size = min_size
        self.max_size = max_size
        self.pool = None
    
    async def initialize(self):
        """初始化连接池"""
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=self.min_size,
            max_size=self.max_size
        )
    
    @asynccontextmanager
    async def acquire(self):
        """获取数据库连接"""
        async with self.pool.acquire() as connection:
            yield connection
    
    async def close(self):
        """关闭连接池"""
        if self.pool:
            await self.pool.close()


class OptimizedInferenceEngine:
    """优化后的AI推理引擎"""
    
    def __init__(self, 
                 max_workers: Optional[int] = None,
                 enable_gpu: bool = False,
                 database_url: Optional[str] = None):
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.enable_gpu = enable_gpu and cuda.is_available()
        
        # 进程池和线程池
        self.cpu_pool = ProcessPoolExecutor(max_workers=self.max_workers)
        self.io_pool = ThreadPoolExecutor(max_workers=self.max_workers * 2)
        
        # 性能监控
        self.monitor = PerformanceMonitor()
        
        # 共享内存管理
        self.shared_memory = SharedMemoryManager()
        
        # 异步数据库连接池
        self.db_pool = AsyncDatabasePool(database_url) if database_url else None
        
        # 请求队列和结果缓存
        self.request_queue = asyncio.Queue(maxsize=1000)
        self.result_cache = {}
        self.cache_lock = asyncio.Lock()
        
        # JIT优化算法实例
        self.algorithms = JITOptimizedAlgorithms()
        
        logger.info(f"优化推理引擎初始化完成 - CPU核心: {self.max_workers}, GPU: {self.enable_gpu}")
    
    async def initialize(self):
        """异步初始化"""
        if self.db_pool:
            await self.db_pool.initialize()
        
        # 预热JIT编译
        await self._warmup_jit_algorithms()
        
        logger.info("推理引擎异步初始化完成")
    
    async def _warmup_jit_algorithms(self):
        """预热JIT编译算法"""
        logger.info("开始预热JIT编译算法...")
        
        # 创建测试数据
        test_symptoms = np.random.rand(100, 50).astype(np.float32)
        test_weights = np.random.rand(50).astype(np.float32)
        test_biomarkers = np.random.rand(20).astype(np.float32)
        test_risk_factors = np.random.rand(20).astype(np.float32)
        
        # 预热算法
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.cpu_pool,
            self.algorithms.tcm_syndrome_analysis,
            test_symptoms,
            test_weights
        )
        
        await loop.run_in_executor(
            self.cpu_pool,
            self.algorithms.health_risk_calculation,
            test_biomarkers,
            test_risk_factors
        )
        
        logger.info("JIT编译算法预热完成")
    
    async def submit_inference_request(self, request: InferenceRequest) -> str:
        """提交推理请求"""
        await self.request_queue.put(request)
        logger.info(f"推理请求已提交: {request.request_id}")
        return request.request_id
    
    async def get_inference_result(self, request_id: str, timeout: float = 30.0) -> Optional[InferenceResult]:
        """获取推理结果"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            async with self.cache_lock:
                if request_id in self.result_cache:
                    result = self.result_cache.pop(request_id)
                    return result
            
            await asyncio.sleep(0.1)  # 避免忙等待
        
        return None  # 超时
    
    async def process_inference_batch(self, requests: List[InferenceRequest]) -> List[InferenceResult]:
        """批量处理推理请求"""
        tasks = []
        for request in requests:
            task = asyncio.create_task(self._process_single_inference(request))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = InferenceResult(
                    request_id=requests[i].request_id,
                    agent_type=requests[i].agent_type,
                    result={},
                    execution_time=0.0,
                    memory_usage=0.0,
                    success=False,
                    error_message=str(result)
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _process_single_inference(self, request: InferenceRequest) -> InferenceResult:
        """处理单个推理请求"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        try:
            # 根据智能体类型选择处理策略
            if request.agent_type == "xiaoai":
                result = await self._process_xiaoai_inference(request)
            elif request.agent_type == "xiaoke":
                result = await self._process_xiaoke_inference(request)
            elif request.agent_type == "laoke":
                result = await self._process_laoke_inference(request)
            elif request.agent_type == "soer":
                result = await self._process_soer_inference(request)
            else:
                raise ValueError(f"未知的智能体类型: {request.agent_type}")
            
            execution_time = time.time() - start_time
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_usage = end_memory - start_memory
            
            # 记录性能指标
            self.monitor.record_request(execution_time, memory_usage, True)
            
            inference_result = InferenceResult(
                request_id=request.request_id,
                agent_type=request.agent_type,
                result=result,
                execution_time=execution_time,
                memory_usage=memory_usage,
                success=True
            )
            
            # 缓存结果
            async with self.cache_lock:
                self.result_cache[request.request_id] = inference_result
            
            return inference_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_usage = end_memory - start_memory
            
            # 记录性能指标
            self.monitor.record_request(execution_time, memory_usage, False)
            
            logger.error(f"推理请求处理失败: {request.request_id}, 错误: {str(e)}")
            
            return InferenceResult(
                request_id=request.request_id,
                agent_type=request.agent_type,
                result={},
                execution_time=execution_time,
                memory_usage=memory_usage,
                success=False,
                error_message=str(e)
            )
    
    async def _process_xiaoai_inference(self, request: InferenceRequest) -> Dict[str, Any]:
        """处理小艾（AI推理）的推理请求"""
        input_data = request.input_data
        
        # CPU密集型推理使用进程池
        loop = asyncio.get_event_loop()
        
        if "symptoms" in input_data and "weights" in input_data:
            # 中医辨证分析
            symptoms = np.array(input_data["symptoms"], dtype=np.float32)
            weights = np.array(input_data["weights"], dtype=np.float32)
            
            syndrome_scores = await loop.run_in_executor(
                self.cpu_pool,
                self.algorithms.tcm_syndrome_analysis,
                symptoms,
                weights
            )
            
            return {
                "syndrome_analysis": syndrome_scores.tolist(),
                "confidence": float(np.max(syndrome_scores)),
                "recommended_treatment": self._generate_treatment_recommendation(syndrome_scores)
            }
        
        # 默认处理
        return {"message": "小艾推理完成", "timestamp": datetime.now().isoformat()}
    
    async def _process_xiaoke_inference(self, request: InferenceRequest) -> Dict[str, Any]:
        """处理小克（诊断分析）的推理请求"""
        input_data = request.input_data
        
        loop = asyncio.get_event_loop()
        
        if "biomarkers" in input_data and "risk_factors" in input_data:
            # 健康风险评估
            biomarkers = np.array(input_data["biomarkers"], dtype=np.float32)
            risk_factors = np.array(input_data["risk_factors"], dtype=np.float32)
            
            risk_score = await loop.run_in_executor(
                self.cpu_pool,
                self.algorithms.health_risk_calculation,
                biomarkers,
                risk_factors
            )
            
            return {
                "health_risk_score": float(risk_score),
                "risk_level": self._categorize_risk_level(risk_score),
                "recommendations": self._generate_health_recommendations(risk_score)
            }
        
        return {"message": "小克诊断完成", "timestamp": datetime.now().isoformat()}
    
    async def _process_laoke_inference(self, request: InferenceRequest) -> Dict[str, Any]:
        """处理老克（知识管理）的推理请求"""
        input_data = request.input_data
        
        # I/O密集型任务使用异步处理
        if "query" in input_data:
            knowledge_results = await self._async_knowledge_search(input_data["query"])
            return {
                "knowledge_results": knowledge_results,
                "source_count": len(knowledge_results),
                "timestamp": datetime.now().isoformat()
            }
        
        return {"message": "老克知识检索完成", "timestamp": datetime.now().isoformat()}
    
    async def _process_soer_inference(self, request: InferenceRequest) -> Dict[str, Any]:
        """处理索儿（用户交互）的推理请求"""
        input_data = request.input_data
        
        if "user_profile" in input_data and "recommendations" in input_data:
            # 个性化推荐
            loop = asyncio.get_event_loop()
            
            user_profile = np.array(input_data["user_profile"], dtype=np.float32)
            recommendations = np.array(input_data["recommendations"], dtype=np.float32)
            
            scores = await loop.run_in_executor(
                self.cpu_pool,
                self.algorithms.personalized_recommendation_scoring,
                user_profile,
                recommendations
            )
            
            return {
                "recommendation_scores": scores.tolist(),
                "top_recommendations": self._get_top_recommendations(scores, input_data.get("items", [])),
                "personalization_confidence": float(np.std(scores))
            }
        
        return {"message": "索儿个性化服务完成", "timestamp": datetime.now().isoformat()}
    
    async def _async_knowledge_search(self, query: str) -> List[Dict[str, Any]]:
        """异步知识搜索"""
        # 模拟异步数据库查询
        await asyncio.sleep(0.1)  # 模拟I/O延迟
        
        # 如果有数据库连接池，使用真实查询
        if self.db_pool:
            try:
                async with self.db_pool.acquire() as conn:
                    results = await conn.fetch(
                        "SELECT * FROM knowledge_base WHERE content ILIKE $1 LIMIT 10",
                        f"%{query}%"
                    )
                    return [dict(row) for row in results]
            except Exception as e:
                logger.error(f"数据库查询失败: {e}")
        
        # 模拟知识搜索结果
        return [
            {"id": i, "title": f"知识条目 {i}", "content": f"关于 {query} 的知识内容 {i}"}
            for i in range(5)
        ]
    
    def _generate_treatment_recommendation(self, syndrome_scores: np.ndarray) -> List[str]:
        """生成治疗建议"""
        max_index = np.argmax(syndrome_scores)
        treatments = [
            "清热解毒", "健脾益气", "滋阴润燥", "温阳散寒", "活血化瘀"
        ]
        return [treatments[max_index % len(treatments)]]
    
    def _categorize_risk_level(self, risk_score: float) -> str:
        """分类风险等级"""
        if risk_score < 0.3:
            return "低风险"
        elif risk_score < 0.7:
            return "中风险"
        else:
            return "高风险"
    
    def _generate_health_recommendations(self, risk_score: float) -> List[str]:
        """生成健康建议"""
        if risk_score < 0.3:
            return ["保持良好生活习惯", "定期体检"]
        elif risk_score < 0.7:
            return ["调整饮食结构", "增加运动量", "定期监测"]
        else:
            return ["立即就医", "严格控制饮食", "密切监测健康指标"]
    
    def _get_top_recommendations(self, scores: np.ndarray, items: List[Any]) -> List[Dict[str, Any]]:
        """获取top推荐"""
        if not items:
            return []
        
        top_indices = np.argsort(scores)[-5:][::-1]  # 取前5个
        return [
            {"item": items[i] if i < len(items) else f"推荐项目 {i}", "score": float(scores[i])}
            for i in top_indices
        ]
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return self.monitor.get_metrics()
    
    async def shutdown(self):
        """关闭推理引擎"""
        logger.info("正在关闭推理引擎...")
        
        # 关闭进程池和线程池
        self.cpu_pool.shutdown(wait=True)
        self.io_pool.shutdown(wait=True)
        
        # 关闭数据库连接池
        if self.db_pool:
            await self.db_pool.close()
        
        # 清理共享内存
        self.shared_memory.cleanup()
        
        logger.info("推理引擎已关闭")


# 使用示例和测试函数
async def main():
    """主函数 - 演示优化后的推理引擎"""
    # 初始化推理引擎
    engine = OptimizedInferenceEngine(
        max_workers=multiprocessing.cpu_count(),
        enable_gpu=False,  # 根据需要启用GPU
        database_url=None  # 如果有数据库，提供连接字符串
    )
    
    await engine.initialize()
    
    try:
        # 创建测试请求
        requests = [
            InferenceRequest(
                request_id=str(uuid.uuid4()),
                agent_type="xiaoai",
                input_data={
                    "symptoms": np.random.rand(10, 20).tolist(),
                    "weights": np.random.rand(20).tolist()
                }
            ),
            InferenceRequest(
                request_id=str(uuid.uuid4()),
                agent_type="xiaoke",
                input_data={
                    "biomarkers": np.random.rand(15).tolist(),
                    "risk_factors": np.random.rand(15).tolist()
                }
            ),
            InferenceRequest(
                request_id=str(uuid.uuid4()),
                agent_type="laoke",
                input_data={"query": "中医养生"}
            ),
            InferenceRequest(
                request_id=str(uuid.uuid4()),
                agent_type="soer",
                input_data={
                    "user_profile": np.random.rand(10).tolist(),
                    "recommendations": np.random.rand(20, 10).tolist(),
                    "items": [f"推荐项目 {i}" for i in range(20)]
                }
            )
        ]
        
        # 批量处理推理请求
        print("🚀 开始批量推理测试...")
        start_time = time.time()
        
        results = await engine.process_inference_batch(requests)
        
        end_time = time.time()
        
        # 打印结果
        print(f"✅ 批量推理完成，耗时: {end_time - start_time:.3f}s")
        for result in results:
            print(f"  📊 {result.agent_type}: {result.success}, 耗时: {result.execution_time:.3f}s")
        
        # 获取性能指标
        metrics = await engine.get_performance_metrics()
        print(f"\n📈 性能指标:")
        for key, value in metrics.items():
            print(f"  {key}: {value}")
    
    finally:
        await engine.shutdown()


if __name__ == "__main__":
    asyncio.run(main()) 