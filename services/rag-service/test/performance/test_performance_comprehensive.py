"""
test_performance_comprehensive - 索克生活项目模块
"""

from concurrent.futures import ThreadPoolExecutor
from config.settings import get_settings
from dataclasses import dataclass
from internal.model.entities import Document, SearchQuery, GenerationRequest
from internal.service.rag_service import RAGService
from internal.service.vector_service import VectorService
from loguru import logger
from typing import List, Dict, Any, Tuple
import asyncio
import memory_profiler
import numpy as np
import psutil
import pytest
import statistics
import time

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RAG服务性能测试套件
测试检索、生成、缓存等各项性能指标
"""




@dataclass
class PerformanceMetrics:
    """性能指标"""
    operation: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    throughput: float  # requests per second
    memory_usage_mb: float
    cpu_usage_percent: float
    error_rate: float


class PerformanceProfiler:
    """性能分析器"""
    
    def __init__(self):
        self.response_times = []
        self.start_time = None
        self.end_time = None
        self.memory_usage = []
        self.cpu_usage = []
        self.errors = []
    
    def start_profiling(self):
        """开始性能分析"""
        self.start_time = time.time()
        self.response_times = []
        self.memory_usage = []
        self.cpu_usage = []
        self.errors = []
    
    def record_request(self, response_time: float, success: bool = True, error: str = None):
        """记录请求"""
        self.response_times.append(response_time)
        if not success and error:
            self.errors.append(error)
        
        # 记录系统资源使用
        process = psutil.Process()
        self.memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
        self.cpu_usage.append(process.cpu_percent())
    
    def get_metrics(self, operation: str) -> PerformanceMetrics:
        """获取性能指标"""
        if not self.response_times:
            return PerformanceMetrics(
                operation=operation,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                avg_response_time=0,
                min_response_time=0,
                max_response_time=0,
                p50_response_time=0,
                p95_response_time=0,
                p99_response_time=0,
                throughput=0,
                memory_usage_mb=0,
                cpu_usage_percent=0,
                error_rate=0
            )
        
        total_requests = len(self.response_times)
        failed_requests = len(self.errors)
        successful_requests = total_requests - failed_requests
        
        # 计算响应时间统计
        avg_response_time = statistics.mean(self.response_times)
        min_response_time = min(self.response_times)
        max_response_time = max(self.response_times)
        
        sorted_times = sorted(self.response_times)
        p50_response_time = np.percentile(sorted_times, 50)
        p95_response_time = np.percentile(sorted_times, 95)
        p99_response_time = np.percentile(sorted_times, 99)
        
        # 计算吞吐量
        duration = self.end_time - self.start_time if self.end_time else time.time() - self.start_time
        throughput = total_requests / duration if duration > 0 else 0
        
        # 计算资源使用
        avg_memory = statistics.mean(self.memory_usage) if self.memory_usage else 0
        avg_cpu = statistics.mean(self.cpu_usage) if self.cpu_usage else 0
        
        # 计算错误率
        error_rate = failed_requests / total_requests if total_requests > 0 else 0
        
        return PerformanceMetrics(
            operation=operation,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p50_response_time=p50_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            throughput=throughput,
            memory_usage_mb=avg_memory,
            cpu_usage_percent=avg_cpu,
            error_rate=error_rate
        )
    
    def stop_profiling(self):
        """停止性能分析"""
        self.end_time = time.time()


class RAGPerformanceTest:
    """RAG服务性能测试"""
    
    def __init__(self, rag_service: RAGService, vector_service: VectorService):
        self.rag_service = rag_service
        self.vector_service = vector_service
        self.settings = get_settings()
        self.profiler = PerformanceProfiler()
    
    async def test_search_performance(
        self,
        queries: List[str],
        concurrent_users: int = 10,
        requests_per_user: int = 10
    ) -> PerformanceMetrics:
        """测试搜索性能"""
        logger.info(f"开始搜索性能测试: {concurrent_users} 并发用户, 每用户 {requests_per_user} 请求")
        
        self.profiler.start_profiling()
        
        async def user_session(user_id: int):
            """用户会话"""
            for i in range(requests_per_user):
                query = queries[i % len(queries)]
                start_time = time.time()
                
                try:
                    result = await self.vector_service.search(
                        query=query,
                        top_k=5,
                        user_id=f"user_{user_id}"
                    )
                    response_time = time.time() - start_time
                    self.profiler.record_request(response_time, success=True)
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    self.profiler.record_request(response_time, success=False, error=str(e))
                
                # 模拟用户思考时间
                await asyncio.sleep(0.1)
        
        # 并发执行用户会话
        tasks = [user_session(i) for i in range(concurrent_users)]
        await asyncio.gather(*tasks)
        
        self.profiler.stop_profiling()
        metrics = self.profiler.get_metrics("search")
        
        logger.info(f"搜索性能测试完成: 平均响应时间 {metrics.avg_response_time:.3f}s, 吞吐量 {metrics.throughput:.2f} req/s")
        return metrics
    
    async def test_generation_performance(
        self,
        queries: List[str],
        concurrent_users: int = 5,
        requests_per_user: int = 5
    ) -> PerformanceMetrics:
        """测试生成性能"""
        logger.info(f"开始生成性能测试: {concurrent_users} 并发用户, 每用户 {requests_per_user} 请求")
        
        self.profiler.start_profiling()
        
        async def user_session(user_id: int):
            """用户会话"""
            for i in range(requests_per_user):
                query = queries[i % len(queries)]
                start_time = time.time()
                
                try:
                    request = GenerationRequest(
                        query=query,
                        max_tokens=500,
                        temperature=0.7,
                        user_id=f"user_{user_id}"
                    )
                    
                    result = await self.rag_service.generate_response(request)
                    response_time = time.time() - start_time
                    self.profiler.record_request(response_time, success=True)
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    self.profiler.record_request(response_time, success=False, error=str(e))
                
                # 模拟用户阅读时间
                await asyncio.sleep(0.5)
        
        # 并发执行用户会话
        tasks = [user_session(i) for i in range(concurrent_users)]
        await asyncio.gather(*tasks)
        
        self.profiler.stop_profiling()
        metrics = self.profiler.get_metrics("generation")
        
        logger.info(f"生成性能测试完成: 平均响应时间 {metrics.avg_response_time:.3f}s, 吞吐量 {metrics.throughput:.2f} req/s")
        return metrics
    
    async def test_cache_performance(
        self,
        queries: List[str],
        cache_hit_ratio: float = 0.8
    ) -> Tuple[PerformanceMetrics, PerformanceMetrics]:
        """测试缓存性能"""
        logger.info(f"开始缓存性能测试: 目标缓存命中率 {cache_hit_ratio}")
        
        # 预热缓存
        warmup_queries = queries[:int(len(queries) * cache_hit_ratio)]
        for query in warmup_queries:
            await self.vector_service.search(query=query, top_k=5)
        
        # 测试缓存命中
        self.profiler.start_profiling()
        for query in warmup_queries:
            start_time = time.time()
            try:
                result = await self.vector_service.search(query=query, top_k=5)
                response_time = time.time() - start_time
                self.profiler.record_request(response_time, success=True)
            except Exception as e:
                response_time = time.time() - start_time
                self.profiler.record_request(response_time, success=False, error=str(e))
        
        self.profiler.stop_profiling()
        cache_hit_metrics = self.profiler.get_metrics("cache_hit")
        
        # 测试缓存未命中
        self.profiler.start_profiling()
        miss_queries = queries[int(len(queries) * cache_hit_ratio):]
        for query in miss_queries:
            start_time = time.time()
            try:
                result = await self.vector_service.search(query=query, top_k=5)
                response_time = time.time() - start_time
                self.profiler.record_request(response_time, success=True)
            except Exception as e:
                response_time = time.time() - start_time
                self.profiler.record_request(response_time, success=False, error=str(e))
        
        self.profiler.stop_profiling()
        cache_miss_metrics = self.profiler.get_metrics("cache_miss")
        
        logger.info(f"缓存性能测试完成:")
        logger.info(f"  缓存命中: 平均响应时间 {cache_hit_metrics.avg_response_time:.3f}s")
        logger.info(f"  缓存未命中: 平均响应时间 {cache_miss_metrics.avg_response_time:.3f}s")
        
        return cache_hit_metrics, cache_miss_metrics
    
    async def test_batch_processing_performance(
        self,
        queries: List[str],
        batch_sizes: List[int] = [1, 5, 10, 20, 50]
    ) -> Dict[int, PerformanceMetrics]:
        """测试批处理性能"""
        logger.info(f"开始批处理性能测试: 批次大小 {batch_sizes}")
        
        results = {}
        
        for batch_size in batch_sizes:
            logger.info(f"测试批次大小: {batch_size}")
            self.profiler.start_profiling()
            
            # 分批处理查询
            for i in range(0, len(queries), batch_size):
                batch_queries = queries[i:i + batch_size]
                start_time = time.time()
                
                try:
                    # 并行处理批次中的查询
                    tasks = [
                        self.vector_service.search(query=query, top_k=5)
                        for query in batch_queries
                    ]
                    await asyncio.gather(*tasks)
                    
                    response_time = time.time() - start_time
                    self.profiler.record_request(response_time, success=True)
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    self.profiler.record_request(response_time, success=False, error=str(e))
            
            self.profiler.stop_profiling()
            metrics = self.profiler.get_metrics(f"batch_{batch_size}")
            results[batch_size] = metrics
            
            logger.info(f"批次大小 {batch_size}: 平均响应时间 {metrics.avg_response_time:.3f}s, 吞吐量 {metrics.throughput:.2f} req/s")
        
        return results
    
    async def test_memory_usage(
        self,
        queries: List[str],
        duration_seconds: int = 60
    ) -> Dict[str, Any]:
        """测试内存使用情况"""
        logger.info(f"开始内存使用测试: 持续时间 {duration_seconds}s")
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        memory_samples = []
        start_time = time.time()
        
        async def memory_monitor():
            """内存监控"""
            while time.time() - start_time < duration_seconds:
                memory_usage = process.memory_info().rss / 1024 / 1024
                memory_samples.append(memory_usage)
                await asyncio.sleep(1)
        
        async def workload():
            """工作负载"""
            while time.time() - start_time < duration_seconds:
                query = queries[int(time.time()) % len(queries)]
                try:
                    await self.vector_service.search(query=query, top_k=5)
                except Exception as e:
                    logger.error(f"内存测试中的搜索错误: {e}")
                await asyncio.sleep(0.1)
        
        # 并行运行监控和工作负载
        await asyncio.gather(memory_monitor(), workload())
        
        final_memory = process.memory_info().rss / 1024 / 1024
        
        memory_stats = {
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "memory_increase_mb": final_memory - initial_memory,
            "peak_memory_mb": max(memory_samples) if memory_samples else final_memory,
            "avg_memory_mb": statistics.mean(memory_samples) if memory_samples else final_memory,
            "memory_samples": memory_samples
        }
        
        logger.info(f"内存使用测试完成:")
        logger.info(f"  初始内存: {initial_memory:.2f} MB")
        logger.info(f"  最终内存: {final_memory:.2f} MB")
        logger.info(f"  内存增长: {memory_stats['memory_increase_mb']:.2f} MB")
        logger.info(f"  峰值内存: {memory_stats['peak_memory_mb']:.2f} MB")
        
        return memory_stats
    
    async def test_stress_performance(
        self,
        queries: List[str],
        max_concurrent_users: int = 100,
        ramp_up_time: int = 30,
        steady_time: int = 60,
        ramp_down_time: int = 30
    ) -> List[PerformanceMetrics]:
        """压力测试"""
        logger.info(f"开始压力测试: 最大 {max_concurrent_users} 并发用户")
        
        results = []
        total_time = ramp_up_time + steady_time + ramp_down_time
        
        async def user_worker(user_id: int, start_delay: float, duration: float):
            """用户工作器"""
            await asyncio.sleep(start_delay)
            end_time = time.time() + duration
            
            while time.time() < end_time:
                query = queries[user_id % len(queries)]
                start_time = time.time()
                
                try:
                    await self.vector_service.search(
                        query=query,
                        top_k=5,
                        user_id=f"stress_user_{user_id}"
                    )
                    response_time = time.time() - start_time
                    self.profiler.record_request(response_time, success=True)
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    self.profiler.record_request(response_time, success=False, error=str(e))
                
                await asyncio.sleep(0.1)
        
        # 分阶段启动用户
        tasks = []
        
        # 爬坡阶段
        for i in range(max_concurrent_users):
            start_delay = (i / max_concurrent_users) * ramp_up_time
            duration = total_time - start_delay
            task = user_worker(i, start_delay, duration)
            tasks.append(task)
        
        self.profiler.start_profiling()
        
        # 监控不同阶段的性能
        async def phase_monitor():
            """阶段监控"""
            phases = [
                ("ramp_up", ramp_up_time),
                ("steady", steady_time),
                ("ramp_down", ramp_down_time)
            ]
            
            for phase_name, phase_duration in phases:
                phase_start = time.time()
                await asyncio.sleep(phase_duration)
                
                # 记录当前阶段的指标
                phase_metrics = self.profiler.get_metrics(f"stress_{phase_name}")
                results.append(phase_metrics)
                
                logger.info(f"压力测试 {phase_name} 阶段: 平均响应时间 {phase_metrics.avg_response_time:.3f}s, 错误率 {phase_metrics.error_rate:.2%}")
        
        # 并行运行用户任务和监控
        await asyncio.gather(*tasks, phase_monitor())
        
        self.profiler.stop_profiling()
        
        logger.info("压力测试完成")
        return results


class PerformanceTestSuite:
    """性能测试套件"""
    
    def __init__(self, rag_service: RAGService, vector_service: VectorService):
        self.rag_service = rag_service
        self.vector_service = vector_service
        self.test_runner = RAGPerformanceTest(rag_service, vector_service)
    
    def generate_test_queries(self, count: int = 100) -> List[str]:
        """生成测试查询"""
        base_queries = [
            "头痛的中医治疗方法",
            "气虚体质如何调理",
            "失眠的穴位按摩",
            "胃痛吃什么中药",
            "高血压的中医预防",
            "咳嗽的食疗方法",
            "腰痛的针灸治疗",
            "便秘的中医调理",
            "焦虑症的中医治疗",
            "月经不调的中药方剂"
        ]
        
        # 扩展查询列表
        queries = []
        for i in range(count):
            base_query = base_queries[i % len(base_queries)]
            # 添加一些变化
            variations = [
                base_query,
                f"{base_query}有哪些",
                f"如何{base_query}",
                f"{base_query}的注意事项",
                f"{base_query}效果如何"
            ]
            queries.append(variations[i % len(variations)])
        
        return queries
    
    async def run_comprehensive_performance_test(self) -> Dict[str, Any]:
        """运行全面性能测试"""
        logger.info("开始全面性能测试")
        
        test_queries = self.generate_test_queries(100)
        results = {}
        
        try:
            # 1. 搜索性能测试
            logger.info("=" * 50)
            logger.info("1. 搜索性能测试")
            search_metrics = await self.test_runner.test_search_performance(
                queries=test_queries,
                concurrent_users=10,
                requests_per_user=10
            )
            results["search_performance"] = search_metrics
            
            # 2. 生成性能测试
            logger.info("=" * 50)
            logger.info("2. 生成性能测试")
            generation_metrics = await self.test_runner.test_generation_performance(
                queries=test_queries[:20],  # 生成测试使用较少查询
                concurrent_users=5,
                requests_per_user=5
            )
            results["generation_performance"] = generation_metrics
            
            # 3. 缓存性能测试
            logger.info("=" * 50)
            logger.info("3. 缓存性能测试")
            cache_hit_metrics, cache_miss_metrics = await self.test_runner.test_cache_performance(
                queries=test_queries[:50],
                cache_hit_ratio=0.8
            )
            results["cache_hit_performance"] = cache_hit_metrics
            results["cache_miss_performance"] = cache_miss_metrics
            
            # 4. 批处理性能测试
            logger.info("=" * 50)
            logger.info("4. 批处理性能测试")
            batch_metrics = await self.test_runner.test_batch_processing_performance(
                queries=test_queries[:50],
                batch_sizes=[1, 5, 10, 20]
            )
            results["batch_performance"] = batch_metrics
            
            # 5. 内存使用测试
            logger.info("=" * 50)
            logger.info("5. 内存使用测试")
            memory_stats = await self.test_runner.test_memory_usage(
                queries=test_queries,
                duration_seconds=30
            )
            results["memory_usage"] = memory_stats
            
            # 6. 压力测试
            logger.info("=" * 50)
            logger.info("6. 压力测试")
            stress_metrics = await self.test_runner.test_stress_performance(
                queries=test_queries,
                max_concurrent_users=50,
                ramp_up_time=15,
                steady_time=30,
                ramp_down_time=15
            )
            results["stress_performance"] = stress_metrics
            
            logger.info("=" * 50)
            logger.info("全面性能测试完成")
            
            return results
            
        except Exception as e:
            logger.error(f"性能测试失败: {e}")
            raise
    
    def generate_performance_report(self, results: Dict[str, Any]) -> str:
        """生成性能报告"""
        report = []
        report.append("# RAG服务性能测试报告")
        report.append("")
        
        # 搜索性能
        if "search_performance" in results:
            metrics = results["search_performance"]
            report.append("## 搜索性能")
            report.append(f"- 平均响应时间: {metrics.avg_response_time:.3f}s")
            report.append(f"- P95响应时间: {metrics.p95_response_time:.3f}s")
            report.append(f"- 吞吐量: {metrics.throughput:.2f} req/s")
            report.append(f"- 错误率: {metrics.error_rate:.2%}")
            report.append("")
        
        # 生成性能
        if "generation_performance" in results:
            metrics = results["generation_performance"]
            report.append("## 生成性能")
            report.append(f"- 平均响应时间: {metrics.avg_response_time:.3f}s")
            report.append(f"- P95响应时间: {metrics.p95_response_time:.3f}s")
            report.append(f"- 吞吐量: {metrics.throughput:.2f} req/s")
            report.append(f"- 错误率: {metrics.error_rate:.2%}")
            report.append("")
        
        # 缓存性能
        if "cache_hit_performance" in results and "cache_miss_performance" in results:
            hit_metrics = results["cache_hit_performance"]
            miss_metrics = results["cache_miss_performance"]
            report.append("## 缓存性能")
            report.append(f"- 缓存命中响应时间: {hit_metrics.avg_response_time:.3f}s")
            report.append(f"- 缓存未命中响应时间: {miss_metrics.avg_response_time:.3f}s")
            speedup = miss_metrics.avg_response_time / hit_metrics.avg_response_time if hit_metrics.avg_response_time > 0 else 1
            report.append(f"- 缓存加速比: {speedup:.2f}x")
            report.append("")
        
        # 内存使用
        if "memory_usage" in results:
            memory = results["memory_usage"]
            report.append("## 内存使用")
            report.append(f"- 初始内存: {memory['initial_memory_mb']:.2f} MB")
            report.append(f"- 峰值内存: {memory['peak_memory_mb']:.2f} MB")
            report.append(f"- 内存增长: {memory['memory_increase_mb']:.2f} MB")
            report.append("")
        
        # 批处理性能
        if "batch_performance" in results:
            report.append("## 批处理性能")
            for batch_size, metrics in results["batch_performance"].items():
                report.append(f"- 批次大小 {batch_size}: {metrics.avg_response_time:.3f}s, {metrics.throughput:.2f} req/s")
            report.append("")
        
        return "\n".join(report)


# 测试用例
@pytest.mark.asyncio
@pytest.mark.performance
class TestRAGPerformance:
    """RAG性能测试用例"""
    
    @pytest.fixture
    async def performance_suite(self, rag_service, vector_service):
        """性能测试套件fixture"""
        return PerformanceTestSuite(rag_service, vector_service)
    
    async     @cache(timeout=300)  # 5分钟缓存
def test_search_latency(self, performance_suite):
        """测试搜索延迟"""
        queries = performance_suite.generate_test_queries(10)
        metrics = await performance_suite.test_runner.test_search_performance(
            queries=queries,
            concurrent_users=1,
            requests_per_user=10
        )
        
        # 断言性能要求
        assert metrics.avg_response_time < 1.0, f"搜索平均响应时间过长: {metrics.avg_response_time}s"
        assert metrics.p95_response_time < 2.0, f"搜索P95响应时间过长: {metrics.p95_response_time}s"
        assert metrics.error_rate < 0.01, f"搜索错误率过高: {metrics.error_rate}"
    
    async def test_generation_latency(self, performance_suite):
        """测试生成延迟"""
        queries = performance_suite.generate_test_queries(5)
        metrics = await performance_suite.test_runner.test_generation_performance(
            queries=queries,
            concurrent_users=1,
            requests_per_user=5
        )
        
        # 断言性能要求
        assert metrics.avg_response_time < 10.0, f"生成平均响应时间过长: {metrics.avg_response_time}s"
        assert metrics.error_rate < 0.05, f"生成错误率过高: {metrics.error_rate}"
    
    async def test_concurrent_performance(self, performance_suite):
        """测试并发性能"""
        queries = performance_suite.generate_test_queries(20)
        metrics = await performance_suite.test_runner.test_search_performance(
            queries=queries,
            concurrent_users=20,
            requests_per_user=5
        )
        
        # 断言并发性能要求
        assert metrics.throughput > 10, f"并发吞吐量过低: {metrics.throughput} req/s"
        assert metrics.error_rate < 0.05, f"并发错误率过高: {metrics.error_rate}"
    
    async def test_memory_efficiency(self, performance_suite):
        """测试内存效率"""
        queries = performance_suite.generate_test_queries(50)
        memory_stats = await performance_suite.test_runner.test_memory_usage(
            queries=queries,
            duration_seconds=30
        )
        
        # 断言内存使用要求
        assert memory_stats["memory_increase_mb"] < 100, f"内存增长过多: {memory_stats['memory_increase_mb']} MB"
        assert memory_stats["peak_memory_mb"] < 1000, f"峰值内存过高: {memory_stats['peak_memory_mb']} MB"
    
    @pytest.mark.slow
    async def test_comprehensive_performance(self, performance_suite):
        """全面性能测试"""
        results = await performance_suite.run_comprehensive_performance_test()
        
        # 生成性能报告
        report = performance_suite.generate_performance_report(results)
        logger.info(f"性能测试报告:\n{report}")
        
        # 保存报告到文件
        with open("performance_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        # 基本性能断言
        assert "search_performance" in results
        assert "generation_performance" in results
        assert results["search_performance"].error_rate < 0.05
        assert results["generation_performance"].error_rate < 0.1


if __name__ == "__main__":
    # 运行性能测试
    pytest.main([__file__, "-v", "--asyncio-mode=auto", "-m", "performance"]) 