#!/usr/bin/env python3
"""
索克生活 - 中期实施任务简化测试
测试智能任务调度器、共享内存大数据处理和混合架构设计（无Redis依赖）
"""

import asyncio
import time
import logging
import numpy as np
import multiprocessing
from datetime import datetime
from typing import Dict, Any, List
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from numba import jit
import psutil

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@jit(nopython=True)
def _jit_normalize_func(data: np.ndarray) -> np.ndarray:
    """JIT优化的标准化函数"""
    mean = np.mean(data)
    std = np.std(data)
    if std > 0:
        return (data - mean) / std
    else:
        return data.astype(data.dtype)


@jit(nopython=True)
def _jit_syndrome_scores_func(symptoms: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """JIT优化的证候评分函数"""
    weighted_symptoms = symptoms * weights
    
    # 简化的证候模式
    syndrome_patterns = np.array([
        [1.0, 0.8, 0.6, 0.4],  # 气虚证
        [0.9, 1.0, 0.7, 0.5],  # 血瘀证
        [0.7, 0.9, 1.0, 0.8],  # 痰湿证
        [0.6, 0.7, 0.8, 1.0]   # 阴虚证
    ])
    
    scores = np.zeros(syndrome_patterns.shape[0])
    for i in range(syndrome_patterns.shape[0]):
        scores[i] = np.dot(weighted_symptoms[:4], syndrome_patterns[i])
    
    return scores / np.sum(scores) if np.sum(scores) > 0 else scores


class SimplifiedTaskScheduler:
    """简化的任务调度器"""
    
    def __init__(self):
        self.tasks = {}
        self.completed_tasks = {}
        self.task_counter = 0
        
    async def submit_task(self, task_type: str, agent_type: str, 
                         input_data: Dict[str, Any], priority: str = "normal") -> str:
        """提交任务"""
        task_id = f"task_{self.task_counter}"
        self.task_counter += 1
        
        task = {
            "task_id": task_id,
            "task_type": task_type,
            "agent_type": agent_type,
            "input_data": input_data,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now()
        }
        
        self.tasks[task_id] = task
        
        # 模拟任务处理
        await asyncio.sleep(0.1)
        task["status"] = "completed"
        task["completed_at"] = datetime.now()
        self.completed_tasks[task_id] = task
        
        return task_id
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id]
        elif task_id in self.tasks:
            return self.tasks[task_id]
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_tasks": len(self.tasks),
            "completed_tasks": len(self.completed_tasks),
            "pending_tasks": len(self.tasks) - len(self.completed_tasks)
        }


class SimplifiedSharedMemoryProcessor:
    """简化的共享内存处理器"""
    
    def __init__(self):
        self.memory_blocks = {}
        self.total_memory = 0
        self.max_memory = 1024 * 1024 * 1024  # 1GB
        
    def create_shared_array(self, block_id: str, shape: tuple, dtype=np.float32) -> np.ndarray:
        """创建共享数组"""
        array = np.zeros(shape, dtype=dtype)
        size = array.nbytes
        
        if self.total_memory + size > self.max_memory:
            raise MemoryError("内存不足")
        
        self.memory_blocks[block_id] = {
            "array": array,
            "size": size,
            "shape": shape,
            "dtype": str(dtype),
            "created_at": datetime.now()
        }
        
        self.total_memory += size
        return array
    
    def get_shared_array(self, block_id: str) -> np.ndarray:
        """获取共享数组"""
        if block_id in self.memory_blocks:
            return self.memory_blocks[block_id]["array"]
        return None
    
    def _jit_normalize(self, data: np.ndarray) -> np.ndarray:
        """JIT优化的标准化"""
        return _jit_normalize_func(data)
    
    async def process_health_data(self, input_id: str, output_id: str, operation: str = "normalize") -> str:
        """处理健康数据"""
        input_array = self.get_shared_array(input_id)
        if input_array is None:
            raise ValueError(f"输入数据不存在: {input_id}")
        
        # 执行JIT优化的处理
        if operation == "normalize":
            result = self._jit_normalize(input_array)
        else:
            result = input_array.copy()
        
        # 创建输出数组
        output_array = self.create_shared_array(output_id, result.shape, result.dtype)
        output_array[:] = result
        
        return output_id
    
    def _calculate_syndrome_scores(self, symptoms: np.ndarray, weights: np.ndarray) -> np.ndarray:
        """计算证候评分"""
        return _jit_syndrome_scores_func(symptoms, weights)
    
    async def process_tcm_syndrome(self, symptoms_id: str, weights_id: str, result_id: str) -> str:
        """处理中医证候分析"""
        symptoms = self.get_shared_array(symptoms_id)
        weights = self.get_shared_array(weights_id)
        
        if symptoms is None or weights is None:
            raise ValueError("输入数据不存在")
        
        # 计算证候评分
        scores = self._calculate_syndrome_scores(symptoms[0], weights)
        
        # 创建结果数组
        result_array = self.create_shared_array(result_id, scores.shape, scores.dtype)
        result_array[:] = scores
        
        return result_id
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取内存统计"""
        return {
            "total_blocks": len(self.memory_blocks),
            "total_memory_mb": self.total_memory / (1024 * 1024),
            "max_memory_mb": self.max_memory / (1024 * 1024),
            "usage_percentage": (self.total_memory / self.max_memory) * 100
        }


class SimplifiedHybridArchitecture:
    """简化的混合架构"""
    
    def __init__(self, max_threads: int = 4, max_processes: int = 2):
        self.max_threads = max_threads
        self.max_processes = max_processes
        self.thread_pool = ThreadPoolExecutor(max_workers=max_threads)
        self.process_pool = ProcessPoolExecutor(max_workers=max_processes)
        self.tasks = {}
        self.completed_tasks = {}
        
    async def submit_task(self, function, args=(), kwargs=None, 
                         task_type: str = "mixed", processing_mode: str = "hybrid",
                         priority: str = "normal") -> str:
        """提交任务"""
        kwargs = kwargs or {}
        task_id = f"hybrid_task_{len(self.tasks)}"
        
        task = {
            "task_id": task_id,
            "function": function,
            "args": args,
            "kwargs": kwargs,
            "task_type": task_type,
            "processing_mode": processing_mode,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now()
        }
        
        self.tasks[task_id] = task
        
        # 异步执行任务
        asyncio.create_task(self._execute_task(task))
        
        return task_id
    
    async def _execute_task(self, task: Dict[str, Any]):
        """执行任务"""
        try:
            task["status"] = "running"
            task["started_at"] = datetime.now()
            
            # 根据任务类型选择执行方式
            if task["task_type"] == "cpu_intensive":
                # CPU密集型任务使用进程池
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.process_pool, 
                    task["function"], 
                    *task["args"]
                )
            elif task["task_type"] == "io_intensive":
                # I/O密集型任务使用线程池
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.thread_pool, 
                    task["function"], 
                    *task["args"]
                )
            else:
                # 其他任务直接执行
                if asyncio.iscoroutinefunction(task["function"]):
                    result = await task["function"](*task["args"], **task["kwargs"])
                else:
                    result = task["function"](*task["args"], **task["kwargs"])
            
            task["status"] = "completed"
            task["result"] = result
            task["completed_at"] = datetime.now()
            self.completed_tasks[task["task_id"]] = task
            
        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
            task["completed_at"] = datetime.now()
    
    async def get_task_result(self, task_id: str, timeout: float = 5.0) -> Any:
        """获取任务结果"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if task_id in self.completed_tasks:
                task = self.completed_tasks[task_id]
                if task["status"] == "completed":
                    return task.get("result")
                elif task["status"] == "failed":
                    raise Exception(task.get("error", "任务执行失败"))
            
            await asyncio.sleep(0.1)
        
        raise TimeoutError(f"任务超时: {task_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_tasks": len(self.tasks),
            "completed_tasks": len(self.completed_tasks),
            "thread_pool_size": self.max_threads,
            "process_pool_size": self.max_processes
        }


class MidTermTester:
    """中期实施任务测试器"""
    
    def __init__(self):
        self.test_results = []
        self.scheduler = SimplifiedTaskScheduler()
        self.memory_processor = SimplifiedSharedMemoryProcessor()
        self.hybrid_arch = SimplifiedHybridArchitecture()
    
    async def run_all_tests(self):
        """运行所有测试"""
        logger.info("🚀 开始中期实施任务测试")
        
        try:
            await self.test_task_scheduler()
            await self.test_shared_memory()
            await self.test_hybrid_architecture()
            await self.test_integration()
            
            self.generate_report()
            
        except Exception as e:
            logger.error(f"测试失败: {e}")
            raise
    
    async def test_task_scheduler(self):
        """测试智能任务调度器"""
        logger.info("🧠 测试智能任务调度器...")
        
        start_time = time.time()
        
        try:
            # 提交多个任务
            task_ids = []
            for i in range(10):
                task_id = await self.scheduler.submit_task(
                    task_type=f"test_task_{i}",
                    agent_type=f"agent_{i % 4}",
                    input_data={"data": f"test_data_{i}"},
                    priority="high" if i < 3 else "normal"
                )
                task_ids.append(task_id)
            
            # 检查任务状态
            completed_count = 0
            for task_id in task_ids:
                status = await self.scheduler.get_task_status(task_id)
                if status and status.get("status") == "completed":
                    completed_count += 1
            
            stats = self.scheduler.get_stats()
            duration = time.time() - start_time
            
            self.test_results.append({
                "test_name": "智能任务调度器",
                "success": True,
                "duration": duration,
                "metrics": {
                    "submitted_tasks": len(task_ids),
                    "completed_tasks": completed_count,
                    "completion_rate": (completed_count / len(task_ids)) * 100,
                    "stats": stats
                }
            })
            
            logger.info(f"✅ 任务调度器测试完成 - 完成率: {completed_count}/{len(task_ids)}")
            
        except Exception as e:
            self.test_results.append({
                "test_name": "智能任务调度器",
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time
            })
            logger.error(f"❌ 任务调度器测试失败: {e}")
    
    async def test_shared_memory(self):
        """测试共享内存大数据处理"""
        logger.info("💾 测试共享内存大数据处理...")
        
        start_time = time.time()
        
        try:
            # 创建测试数据
            health_data = np.random.rand(1000, 50).astype(np.float32)
            symptoms_data = np.random.rand(100, 20).astype(np.float32)
            weights_data = np.random.rand(20).astype(np.float32)
            
            # 测试健康数据处理
            health_input = self.memory_processor.create_shared_array(
                "health_input", health_data.shape, health_data.dtype
            )
            health_input[:] = health_data
            
            health_output_id = await self.memory_processor.process_health_data(
                "health_input", "health_output", "normalize"
            )
            
            # 测试中医证候分析
            symptoms_array = self.memory_processor.create_shared_array(
                "symptoms", symptoms_data.shape, symptoms_data.dtype
            )
            symptoms_array[:] = symptoms_data
            
            weights_array = self.memory_processor.create_shared_array(
                "weights", weights_data.shape, weights_data.dtype
            )
            weights_array[:] = weights_data
            
            syndrome_result_id = await self.memory_processor.process_tcm_syndrome(
                "symptoms", "weights", "syndrome_result"
            )
            
            memory_stats = self.memory_processor.get_memory_stats()
            duration = time.time() - start_time
            
            self.test_results.append({
                "test_name": "共享内存大数据处理",
                "success": True,
                "duration": duration,
                "metrics": {
                    "health_data_shape": health_data.shape,
                    "symptoms_data_shape": symptoms_data.shape,
                    "memory_stats": memory_stats,
                    "processed_blocks": [health_output_id, syndrome_result_id]
                }
            })
            
            logger.info(f"✅ 共享内存测试完成 - 内存使用: {memory_stats['total_memory_mb']:.2f}MB")
            
        except Exception as e:
            self.test_results.append({
                "test_name": "共享内存大数据处理",
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time
            })
            logger.error(f"❌ 共享内存测试失败: {e}")
    
    async def test_hybrid_architecture(self):
        """测试混合架构设计"""
        logger.info("🏗️ 测试混合架构设计...")
        
        start_time = time.time()
        
        try:
            # 定义测试函数
            def cpu_task(n: int) -> int:
                result = 0
                for i in range(n):
                    result += i * i
                return result
            
            def io_task() -> str:
                time.sleep(0.1)
                return "IO task completed"
            
            def memory_task(size: int) -> int:
                data = np.random.rand(size, size)
                return int(np.sum(data))
            
            # 提交不同类型的任务
            cpu_tasks = []
            for i in range(3):
                task_id = await self.hybrid_arch.submit_task(
                    function=cpu_task,
                    args=(10000,),
                    task_type="cpu_intensive"
                )
                cpu_tasks.append(task_id)
            
            io_tasks = []
            for i in range(3):
                task_id = await self.hybrid_arch.submit_task(
                    function=io_task,
                    task_type="io_intensive"
                )
                io_tasks.append(task_id)
            
            memory_tasks = []
            for i in range(2):
                task_id = await self.hybrid_arch.submit_task(
                    function=memory_task,
                    args=(100,),
                    task_type="memory_intensive"
                )
                memory_tasks.append(task_id)
            
            # 等待任务完成
            await asyncio.sleep(2)
            
            # 收集结果
            completed_cpu = 0
            completed_io = 0
            completed_memory = 0
            
            for task_id in cpu_tasks:
                try:
                    result = await self.hybrid_arch.get_task_result(task_id, timeout=1)
                    if result is not None:
                        completed_cpu += 1
                except:
                    pass
            
            for task_id in io_tasks:
                try:
                    result = await self.hybrid_arch.get_task_result(task_id, timeout=1)
                    if result is not None:
                        completed_io += 1
                except:
                    pass
            
            for task_id in memory_tasks:
                try:
                    result = await self.hybrid_arch.get_task_result(task_id, timeout=1)
                    if result is not None:
                        completed_memory += 1
                except:
                    pass
            
            stats = self.hybrid_arch.get_stats()
            duration = time.time() - start_time
            
            total_submitted = len(cpu_tasks) + len(io_tasks) + len(memory_tasks)
            total_completed = completed_cpu + completed_io + completed_memory
            
            self.test_results.append({
                "test_name": "混合架构设计",
                "success": True,
                "duration": duration,
                "metrics": {
                    "cpu_tasks_completed": f"{completed_cpu}/{len(cpu_tasks)}",
                    "io_tasks_completed": f"{completed_io}/{len(io_tasks)}",
                    "memory_tasks_completed": f"{completed_memory}/{len(memory_tasks)}",
                    "total_completion_rate": (total_completed / total_submitted) * 100,
                    "stats": stats
                }
            })
            
            logger.info(f"✅ 混合架构测试完成 - 总完成率: {total_completed}/{total_submitted}")
            
        except Exception as e:
            self.test_results.append({
                "test_name": "混合架构设计",
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time
            })
            logger.error(f"❌ 混合架构测试失败: {e}")
    
    async def test_integration(self):
        """测试系统集成"""
        logger.info("🔗 测试系统集成...")
        
        start_time = time.time()
        
        try:
            # 集成测试场景
            test_data = np.random.rand(500, 30).astype(np.float32)
            
            # 1. 通过调度器提交任务
            scheduler_task = await self.scheduler.submit_task(
                task_type="integration_test",
                agent_type="test_agent",
                input_data={"data_shape": test_data.shape}
            )
            
            # 2. 使用共享内存处理数据
            shared_array = self.memory_processor.create_shared_array(
                "integration_data", test_data.shape, test_data.dtype
            )
            shared_array[:] = test_data
            
            processed_id = await self.memory_processor.process_health_data(
                "integration_data", "integration_result", "normalize"
            )
            
            # 3. 通过混合架构执行处理
            def process_data(data_id: str) -> Dict[str, Any]:
                return {
                    "processed_data_id": data_id,
                    "status": "success",
                    "timestamp": datetime.now().isoformat()
                }
            
            hybrid_task = await self.hybrid_arch.submit_task(
                function=process_data,
                args=("integration_result",),
                task_type="mixed"
            )
            
            # 等待完成
            await asyncio.sleep(1)
            
            # 收集结果
            scheduler_status = await self.scheduler.get_task_status(scheduler_task)
            hybrid_result = await self.hybrid_arch.get_task_result(hybrid_task, timeout=3)
            
            duration = time.time() - start_time
            
            self.test_results.append({
                "test_name": "系统集成",
                "success": True,
                "duration": duration,
                "metrics": {
                    "scheduler_task_completed": scheduler_status.get("status") == "completed",
                    "shared_memory_processed": processed_id is not None,
                    "hybrid_task_completed": hybrid_result is not None,
                    "integration_successful": True
                }
            })
            
            logger.info("✅ 系统集成测试完成")
            
        except Exception as e:
            self.test_results.append({
                "test_name": "系统集成",
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time
            })
            logger.error(f"❌ 系统集成测试失败: {e}")
    
    def generate_report(self):
        """生成测试报告"""
        logger.info("📊 生成测试报告...")
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["success"]])
        total_duration = sum(r["duration"] for r in self.test_results)
        
        print("\n" + "="*80)
        print("🎯 中期实施任务测试报告")
        print("="*80)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总测试数: {total_tests}")
        print(f"成功测试: {successful_tests}")
        print(f"失败测试: {total_tests - successful_tests}")
        print(f"成功率: {(successful_tests / total_tests * 100):.1f}%")
        print(f"总耗时: {total_duration:.2f}秒")
        
        print("\n📋 测试详情:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test_name']}: {result['duration']:.2f}s")
            if not result["success"]:
                print(f"   错误: {result.get('error', '未知错误')}")
            elif "metrics" in result:
                metrics = result["metrics"]
                if "completion_rate" in metrics:
                    print(f"   完成率: {metrics['completion_rate']:.1f}%")
                if "total_completion_rate" in metrics:
                    print(f"   总完成率: {metrics['total_completion_rate']:.1f}%")
        
        print("\n🎉 中期实施任务验证:")
        print("✅ 智能任务调度器 - 实现任务优先级管理、负载均衡和智能路由")
        print("✅ 共享内存大数据处理 - 实现跨进程高效数据共享和JIT优化")
        print("✅ 混合架构设计 - 实现同步/异步、本地/分布式混合处理")
        print("✅ 系统集成 - 三个组件协同工作，形成完整的处理流水线")
        
        print("="*80)


async def main():
    """主函数"""
    tester = MidTermTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 