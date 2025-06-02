#!/usr/bin/env python3
"""
索克生活 - 优化性能基准测试
验证进程池、异步I/O和JIT编译优化的效果
"""

import asyncio
import time
import multiprocessing
import numpy as np
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import aiohttp
import redis.asyncio as aioredis
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import psutil
import uuid
import statistics
from numba import jit
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

# 导入优化后的组件
try:
    from services.agent_services.optimized_inference_engine import OptimizedInferenceEngine, InferenceRequest
    from services.api_gateway.optimized_async_gateway import OptimizedAsyncGateway
    from services.agent_services.optimized_agent_base import OptimizedAgentBase, JITOptimizedAlgorithms
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已创建优化后的组件文件")


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    test_name: str
    execution_time: float
    memory_usage: float
    throughput: float
    success_rate: float
    error_count: int
    additional_metrics: Dict[str, Any]


class OptimizationBenchmark:
    """优化性能基准测试"""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.algorithms = JITOptimizedAlgorithms()
        
    async def run_all_benchmarks(self) -> Dict[str, Any]:
        """运行所有基准测试"""
        logger.info("🚀 开始运行优化性能基准测试...")
        
        # 1. JIT编译优化测试
        await self._test_jit_optimization()
        
        # 2. 进程池优化测试
        await self._test_process_pool_optimization()
        
        # 3. 异步I/O优化测试
        await self._test_async_io_optimization()
        
        # 4. 缓存优化测试
        await self._test_cache_optimization()
        
        # 5. 综合性能测试
        await self._test_integrated_performance()
        
        # 6. 内存优化测试
        await self._test_memory_optimization()
        
        # 7. 并发性能测试
        await self._test_concurrency_performance()
        
        # 生成报告
        return self._generate_report()
    
    async def _test_jit_optimization(self):
        """测试JIT编译优化"""
        logger.info("📊 测试JIT编译优化...")
        
        # 准备测试数据
        large_vec1 = np.random.rand(10000).astype(np.float32)
        large_vec2 = np.random.rand(10000).astype(np.float32)
        large_values = np.random.rand(5000).astype(np.float32)
        large_weights = np.random.rand(5000).astype(np.float32)
        
        # 测试向量相似度计算
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        iterations = 1000
        for _ in range(iterations):
            similarity = self.algorithms.vector_similarity(large_vec1, large_vec2)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        jit_time = end_time - start_time
        jit_memory = end_memory - start_memory
        
        # 测试加权平均计算
        start_time = time.time()
        for _ in range(iterations):
            avg = self.algorithms.weighted_average(large_values, large_weights)
        end_time = time.time()
        
        weighted_avg_time = end_time - start_time
        
        self.results.append(BenchmarkResult(
            test_name="JIT编译优化",
            execution_time=jit_time + weighted_avg_time,
            memory_usage=jit_memory,
            throughput=iterations * 2 / (jit_time + weighted_avg_time),
            success_rate=1.0,
            error_count=0,
            additional_metrics={
                "vector_similarity_time": jit_time,
                "weighted_average_time": weighted_avg_time,
                "iterations": iterations
            }
        ))
        
        logger.info(f"✅ JIT优化测试完成 - 耗时: {jit_time + weighted_avg_time:.3f}s")
    
    async def _test_process_pool_optimization(self):
        """测试进程池优化"""
        logger.info("📊 测试进程池优化...")
        
        def cpu_intensive_task(data_size: int) -> float:
            """CPU密集型任务"""
            data = np.random.rand(data_size, data_size)
            return np.sum(np.dot(data, data.T))
        
        data_sizes = [500, 500, 500, 500]  # 4个任务
        
        # 串行执行
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        serial_results = []
        for size in data_sizes:
            result = cpu_intensive_task(size)
            serial_results.append(result)
        
        serial_time = time.time() - start_time
        serial_memory = psutil.Process().memory_info().rss / 1024 / 1024 - start_memory
        
        # 并行执行（进程池）
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            parallel_results = list(executor.map(cpu_intensive_task, data_sizes))
        
        parallel_time = time.time() - start_time
        parallel_memory = psutil.Process().memory_info().rss / 1024 / 1024 - start_memory
        
        speedup = serial_time / parallel_time
        
        self.results.append(BenchmarkResult(
            test_name="进程池优化",
            execution_time=parallel_time,
            memory_usage=parallel_memory,
            throughput=len(data_sizes) / parallel_time,
            success_rate=1.0,
            error_count=0,
            additional_metrics={
                "serial_time": serial_time,
                "parallel_time": parallel_time,
                "speedup": speedup,
                "cpu_cores": multiprocessing.cpu_count(),
                "tasks_count": len(data_sizes)
            }
        ))
        
        logger.info(f"✅ 进程池优化测试完成 - 加速比: {speedup:.2f}x")
    
    async def _test_async_io_optimization(self):
        """测试异步I/O优化"""
        logger.info("📊 测试异步I/O优化...")
        
        async def async_http_request(session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
            """异步HTTP请求"""
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return {
                        "status": response.status,
                        "size": len(await response.text()),
                        "success": True
                    }
            except Exception as e:
                return {
                    "status": 0,
                    "size": 0,
                    "success": False,
                    "error": str(e)
                }
        
        # 测试URL列表（使用公开的API）
        test_urls = [
            "https://httpbin.org/delay/1",
            "https://httpbin.org/json",
            "https://httpbin.org/uuid",
            "https://httpbin.org/ip",
            "https://httpbin.org/user-agent"
        ] * 4  # 20个请求
        
        # 异步并发请求
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        async with aiohttp.ClientSession() as session:
            tasks = [async_http_request(session, url) for url in test_urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        async_time = time.time() - start_time
        async_memory = psutil.Process().memory_info().rss / 1024 / 1024 - start_memory
        
        # 计算成功率
        successful_requests = sum(1 for r in results if isinstance(r, dict) and r.get("success", False))
        success_rate = successful_requests / len(test_urls)
        
        self.results.append(BenchmarkResult(
            test_name="异步I/O优化",
            execution_time=async_time,
            memory_usage=async_memory,
            throughput=len(test_urls) / async_time,
            success_rate=success_rate,
            error_count=len(test_urls) - successful_requests,
            additional_metrics={
                "total_requests": len(test_urls),
                "successful_requests": successful_requests,
                "requests_per_second": len(test_urls) / async_time
            }
        ))
        
        logger.info(f"✅ 异步I/O优化测试完成 - 成功率: {success_rate:.2%}")
    
    async def _test_cache_optimization(self):
        """测试缓存优化"""
        logger.info("📊 测试缓存优化...")
        
        # 模拟缓存系统
        cache = {}
        
        def expensive_computation(x: int) -> float:
            """昂贵的计算操作"""
            time.sleep(0.01)  # 模拟计算延迟
            return sum(i ** 2 for i in range(x))
        
        def cached_computation(x: int) -> float:
            """带缓存的计算"""
            if x in cache:
                return cache[x]
            result = expensive_computation(x)
            cache[x] = result
            return result
        
        test_values = [100, 200, 100, 300, 200, 100, 400, 300, 200, 100] * 10  # 重复值
        
        # 无缓存测试
        start_time = time.time()
        no_cache_results = [expensive_computation(x) for x in test_values]
        no_cache_time = time.time() - start_time
        
        # 有缓存测试
        cache.clear()
        start_time = time.time()
        cached_results = [cached_computation(x) for x in test_values]
        cached_time = time.time() - start_time
        
        cache_speedup = no_cache_time / cached_time
        cache_hit_rate = (len(test_values) - len(set(test_values))) / len(test_values)
        
        self.results.append(BenchmarkResult(
            test_name="缓存优化",
            execution_time=cached_time,
            memory_usage=sys.getsizeof(cache) / 1024 / 1024,
            throughput=len(test_values) / cached_time,
            success_rate=1.0,
            error_count=0,
            additional_metrics={
                "no_cache_time": no_cache_time,
                "cached_time": cached_time,
                "speedup": cache_speedup,
                "cache_hit_rate": cache_hit_rate,
                "unique_values": len(set(test_values)),
                "total_values": len(test_values)
            }
        ))
        
        logger.info(f"✅ 缓存优化测试完成 - 加速比: {cache_speedup:.2f}x")
    
    async def _test_integrated_performance(self):
        """测试集成性能"""
        logger.info("📊 测试集成性能...")
        
        # 模拟完整的请求处理流程
        async def integrated_request_processing(request_data: Dict[str, Any]) -> Dict[str, Any]:
            """集成请求处理"""
            # 1. 数据预处理（CPU密集型）
            input_array = np.array(request_data["data"], dtype=np.float32)
            processed_data = np.sqrt(np.sum(input_array ** 2))
            
            # 2. 模拟异步数据库查询
            await asyncio.sleep(0.01)
            
            # 3. JIT优化计算
            weights = np.random.rand(len(input_array)).astype(np.float32)
            weighted_result = self.algorithms.weighted_average(input_array, weights)
            
            # 4. 结果组装
            return {
                "processed_value": float(processed_data),
                "weighted_average": float(weighted_result),
                "request_id": request_data["request_id"],
                "timestamp": datetime.now().isoformat()
            }
        
        # 生成测试请求
        test_requests = [
            {
                "request_id": str(uuid.uuid4()),
                "data": np.random.rand(100).tolist()
            }
            for _ in range(100)
        ]
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # 并发处理所有请求
        tasks = [integrated_request_processing(req) for req in test_requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        successful_results = sum(1 for r in results if isinstance(r, dict))
        success_rate = successful_results / len(test_requests)
        
        self.results.append(BenchmarkResult(
            test_name="集成性能",
            execution_time=execution_time,
            memory_usage=memory_usage,
            throughput=len(test_requests) / execution_time,
            success_rate=success_rate,
            error_count=len(test_requests) - successful_results,
            additional_metrics={
                "total_requests": len(test_requests),
                "successful_requests": successful_results,
                "requests_per_second": len(test_requests) / execution_time,
                "average_request_time": execution_time / len(test_requests)
            }
        ))
        
        logger.info(f"✅ 集成性能测试完成 - 吞吐量: {len(test_requests) / execution_time:.1f} req/s")
    
    async def _test_memory_optimization(self):
        """测试内存优化"""
        logger.info("📊 测试内存优化...")
        
        # 测试大数据处理的内存效率
        def memory_efficient_processing(data_size: int) -> Dict[str, float]:
            """内存高效的数据处理"""
            # 使用生成器和流式处理
            def data_generator():
                for i in range(data_size):
                    yield np.random.rand()
            
            # 流式计算统计信息
            count = 0
            sum_val = 0.0
            sum_sq = 0.0
            min_val = float('inf')
            max_val = float('-inf')
            
            for value in data_generator():
                count += 1
                sum_val += value
                sum_sq += value ** 2
                min_val = min(min_val, value)
                max_val = max(max_val, value)
            
            mean = sum_val / count
            variance = (sum_sq / count) - (mean ** 2)
            
            return {
                "count": count,
                "mean": mean,
                "variance": variance,
                "min": min_val,
                "max": max_val
            }
        
        data_sizes = [100000, 500000, 1000000]
        memory_results = []
        
        for size in data_sizes:
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            start_time = time.time()
            
            result = memory_efficient_processing(size)
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            memory_results.append({
                "data_size": size,
                "execution_time": end_time - start_time,
                "memory_usage": end_memory - start_memory,
                "memory_per_item": (end_memory - start_memory) / size * 1024 * 1024  # bytes per item
            })
        
        avg_memory_usage = statistics.mean([r["memory_usage"] for r in memory_results])
        avg_execution_time = statistics.mean([r["execution_time"] for r in memory_results])
        
        self.results.append(BenchmarkResult(
            test_name="内存优化",
            execution_time=avg_execution_time,
            memory_usage=avg_memory_usage,
            throughput=statistics.mean([r["data_size"] / r["execution_time"] for r in memory_results]),
            success_rate=1.0,
            error_count=0,
            additional_metrics={
                "memory_results": memory_results,
                "avg_memory_per_item": statistics.mean([r["memory_per_item"] for r in memory_results])
            }
        ))
        
        logger.info(f"✅ 内存优化测试完成 - 平均内存使用: {avg_memory_usage:.2f}MB")
    
    async def _test_concurrency_performance(self):
        """测试并发性能"""
        logger.info("📊 测试并发性能...")
        
        async def concurrent_task(task_id: int, duration: float) -> Dict[str, Any]:
            """并发任务"""
            start_time = time.time()
            
            # 模拟混合工作负载
            # 1. CPU计算
            data = np.random.rand(1000)
            cpu_result = np.sum(data ** 2)
            
            # 2. I/O等待
            await asyncio.sleep(duration)
            
            # 3. 更多CPU计算
            final_result = cpu_result * np.random.rand()
            
            end_time = time.time()
            
            return {
                "task_id": task_id,
                "result": float(final_result),
                "execution_time": end_time - start_time,
                "success": True
            }
        
        # 测试不同并发级别
        concurrency_levels = [10, 50, 100]
        concurrency_results = []
        
        for concurrency in concurrency_levels:
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            # 创建并发任务
            tasks = [
                concurrent_task(i, 0.1)  # 100ms I/O延迟
                for i in range(concurrency)
            ]
            
            # 并发执行
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            successful_tasks = sum(1 for r in results if isinstance(r, dict) and r.get("success", False))
            
            concurrency_results.append({
                "concurrency_level": concurrency,
                "total_time": end_time - start_time,
                "memory_usage": end_memory - start_memory,
                "successful_tasks": successful_tasks,
                "success_rate": successful_tasks / concurrency,
                "throughput": successful_tasks / (end_time - start_time)
            })
        
        # 计算平均值
        avg_throughput = statistics.mean([r["throughput"] for r in concurrency_results])
        avg_memory = statistics.mean([r["memory_usage"] for r in concurrency_results])
        avg_success_rate = statistics.mean([r["success_rate"] for r in concurrency_results])
        
        self.results.append(BenchmarkResult(
            test_name="并发性能",
            execution_time=statistics.mean([r["total_time"] for r in concurrency_results]),
            memory_usage=avg_memory,
            throughput=avg_throughput,
            success_rate=avg_success_rate,
            error_count=0,
            additional_metrics={
                "concurrency_results": concurrency_results,
                "max_concurrency": max(concurrency_levels),
                "cpu_cores": multiprocessing.cpu_count()
            }
        ))
        
        logger.info(f"✅ 并发性能测试完成 - 平均吞吐量: {avg_throughput:.1f} tasks/s")
    
    def _generate_report(self) -> Dict[str, Any]:
        """生成性能测试报告"""
        logger.info("📋 生成性能测试报告...")
        
        total_execution_time = sum(r.execution_time for r in self.results)
        total_memory_usage = sum(r.memory_usage for r in self.results)
        avg_throughput = statistics.mean([r.throughput for r in self.results])
        avg_success_rate = statistics.mean([r.success_rate for r in self.results])
        
        # 系统信息
        system_info = {
            "cpu_count": multiprocessing.cpu_count(),
            "cpu_percent": psutil.cpu_percent(),
            "memory_total": psutil.virtual_memory().total / 1024 / 1024 / 1024,  # GB
            "memory_available": psutil.virtual_memory().available / 1024 / 1024 / 1024,  # GB
            "memory_percent": psutil.virtual_memory().percent,
            "python_version": sys.version,
            "platform": sys.platform
        }
        
        # 详细结果
        detailed_results = []
        for result in self.results:
            detailed_results.append({
                "test_name": result.test_name,
                "execution_time": result.execution_time,
                "memory_usage": result.memory_usage,
                "throughput": result.throughput,
                "success_rate": result.success_rate,
                "error_count": result.error_count,
                "additional_metrics": result.additional_metrics
            })
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(self.results),
                "total_execution_time": total_execution_time,
                "total_memory_usage": total_memory_usage,
                "average_throughput": avg_throughput,
                "average_success_rate": avg_success_rate
            },
            "system_info": system_info,
            "detailed_results": detailed_results,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 分析结果并生成建议
        for result in self.results:
            if result.test_name == "进程池优化":
                speedup = result.additional_metrics.get("speedup", 1.0)
                if speedup > 2.0:
                    recommendations.append("✅ 进程池优化效果显著，建议在CPU密集型任务中广泛使用")
                else:
                    recommendations.append("⚠️ 进程池优化效果有限，考虑优化任务粒度或使用其他并行策略")
            
            elif result.test_name == "异步I/O优化":
                if result.success_rate > 0.9:
                    recommendations.append("✅ 异步I/O性能良好，建议在I/O密集型场景中使用")
                else:
                    recommendations.append("⚠️ 异步I/O成功率较低，检查网络连接和超时设置")
            
            elif result.test_name == "缓存优化":
                speedup = result.additional_metrics.get("speedup", 1.0)
                if speedup > 3.0:
                    recommendations.append("✅ 缓存优化效果优秀，建议扩大缓存使用范围")
                else:
                    recommendations.append("💡 考虑优化缓存策略，如LRU、TTL等")
        
        # 通用建议
        recommendations.extend([
            "🔧 定期监控性能指标，及时发现性能瓶颈",
            "📊 使用性能分析工具深入分析热点代码",
            "🚀 考虑使用GPU加速计算密集型任务",
            "💾 优化内存使用，避免内存泄漏",
            "🌐 实施分布式架构以提高整体系统性能"
        ])
        
        return recommendations


async def main():
    """主函数"""
    print("🚀 索克生活 - 优化性能基准测试")
    print("=" * 50)
    
    benchmark = OptimizationBenchmark()
    
    try:
        # 运行所有基准测试
        report = await benchmark.run_all_benchmarks()
        
        # 打印报告
        print("\n📋 性能测试报告")
        print("=" * 50)
        
        print(f"📅 测试时间: {report['timestamp']}")
        print(f"🖥️  系统信息: {report['system_info']['cpu_count']} CPU核心, "
              f"{report['system_info']['memory_total']:.1f}GB 内存")
        
        print(f"\n📊 总体结果:")
        print(f"  总测试数: {report['summary']['total_tests']}")
        print(f"  总执行时间: {report['summary']['total_execution_time']:.3f}s")
        print(f"  总内存使用: {report['summary']['total_memory_usage']:.2f}MB")
        print(f"  平均吞吐量: {report['summary']['average_throughput']:.1f} ops/s")
        print(f"  平均成功率: {report['summary']['average_success_rate']:.2%}")
        
        print(f"\n🔍 详细结果:")
        for result in report['detailed_results']:
            print(f"  📈 {result['test_name']}:")
            print(f"    执行时间: {result['execution_time']:.3f}s")
            print(f"    内存使用: {result['memory_usage']:.2f}MB")
            print(f"    吞吐量: {result['throughput']:.1f} ops/s")
            print(f"    成功率: {result['success_rate']:.2%}")
            
            # 显示特殊指标
            if result['test_name'] == "进程池优化":
                speedup = result['additional_metrics'].get('speedup', 1.0)
                print(f"    加速比: {speedup:.2f}x")
            elif result['test_name'] == "缓存优化":
                speedup = result['additional_metrics'].get('speedup', 1.0)
                hit_rate = result['additional_metrics'].get('cache_hit_rate', 0.0)
                print(f"    加速比: {speedup:.2f}x")
                print(f"    缓存命中率: {hit_rate:.2%}")
            
            print()
        
        print(f"💡 优化建议:")
        for i, recommendation in enumerate(report['recommendations'], 1):
            print(f"  {i}. {recommendation}")
        
        # 保存报告到文件
        report_file = f"optimization_benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 详细报告已保存到: {report_file}")
        
    except Exception as e:
        logger.error(f"基准测试失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 