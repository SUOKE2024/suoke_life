"""
cross_process_benchmark - 索克生活项目模块
"""

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass
from multiprocessing import shared_memory
from numba import jit
from typing import List, Dict, Any, Callable
import asyncio
import json
import multiprocessing
import psutil
import time

#!/usr/bin/env python3
"""
跨进程内存隔离性能基准测试
评估不同GIL优化策略的性能表现
"""


@dataclass
class BenchmarkResult:
    strategy: str
    execution_time: float
    memory_usage: float
    cpu_utilization: float
    throughput: float
    scalability_score: float

class CrossProcessBenchmark:
    """跨进程性能基准测试"""
    
    def __init__(self):
        self.cpu_count = multiprocessing.cpu_count()
        self.results = {}
        
    def cpu_intensive_task(self, n: int = 5000000) -> int:
        """CPU密集型任务"""
        result = 0
        for i in range(n):
            result += i * i + i * 3 + i // 2
        return result
    
    def memory_intensive_task(self, size: int = 10000) -> np.ndarray:
        """内存密集型任务"""
        # 创建大型矩阵并进行计算
        matrix1 = np.random.rand(size, size).astype(np.float32)
        matrix2 = np.random.rand(size, size).astype(np.float32)
        
        # 多次矩阵运算
        result = matrix1
        for _ in range(5):
            result = np.dot(result, matrix2)
            result = np.transpose(result)
        
        return result
    
    @staticmethod
    @jit(nopython=True)
    def jit_optimized_task(n: int = 5000000) -> int:
        """JIT优化的CPU密集型任务"""
        result = 0
        for i in range(n):
            result += i * i + i * 3 + i // 2
        return result
    
    def io_simulation_task(self, delay: float = 0.1) -> str:
        """I/O模拟任务"""
        time.sleep(delay)
        return f"IO task completed after {delay}s"
    
    async def async_io_task(self, delay: float = 0.1) -> str:
        """异步I/O任务"""
        await asyncio.sleep(delay)
        return f"Async IO task completed after {delay}s"
    
    def benchmark_single_thread(self, task_func: Callable, *args, **kwargs) -> BenchmarkResult:
        """单线程基准测试"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        start_cpu = psutil.cpu_percent(interval=None)
        
        # 执行任务
        results = []
        for _ in range(8):  # 模拟8个任务
            result = task_func(*args, **kwargs)
            results.append(result)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        end_cpu = psutil.cpu_percent(interval=None)
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        cpu_utilization = (start_cpu + end_cpu) / 2
        throughput = len(results) / execution_time
        
        return BenchmarkResult(
            strategy="single_thread",
            execution_time=execution_time,
            memory_usage=memory_usage,
            cpu_utilization=cpu_utilization,
            throughput=throughput,
            scalability_score=1.0  # 基准分数
        )
    
    def benchmark_thread_pool(self, task_func: Callable, *args, **kwargs) -> BenchmarkResult:
        """线程池基准测试"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        with ThreadPoolExecutor(max_workers=self.cpu_count) as executor:
            futures = [executor.submit(task_func, *args, **kwargs) for _ in range(8)]
            results = [f.result() for f in futures]
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        cpu_utilization = psutil.cpu_percent()
        throughput = len(results) / execution_time
        
        single_thread_result = self.benchmark_single_thread(task_func, *args, **kwargs)
        
        return BenchmarkResult(
            strategy="thread_pool",
            execution_time=execution_time,
            memory_usage=memory_usage,
            cpu_utilization=cpu_utilization,
            throughput=throughput,
            scalability_score=throughput / single_thread_result.throughput
        )
    
    def benchmark_process_pool(self, task_func: Callable, *args, **kwargs) -> BenchmarkResult:
        """进程池基准测试"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        with ProcessPoolExecutor(max_workers=self.cpu_count) as executor:
            futures = [executor.submit(task_func, *args, **kwargs) for _ in range(8)]
            results = [f.result() for f in futures]
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        cpu_utilization = psutil.cpu_percent()
        throughput = len(results) / execution_time
        
        single_thread_result = self.benchmark_single_thread(task_func, *args, **kwargs)
        
        return BenchmarkResult(
            strategy="process_pool",
            execution_time=execution_time,
            memory_usage=memory_usage,
            cpu_utilization=cpu_utilization,
            throughput=throughput,
            scalability_score=throughput / single_thread_result.throughput
        )
    
    async def benchmark_async_io(self, task_func: Callable, *args, **kwargs) -> BenchmarkResult:
        """异步I/O基准测试"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        tasks = [task_func(*args, **kwargs) for _ in range(8)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        cpu_utilization = psutil.cpu_percent()
        throughput = len(results) / execution_time
        
        return BenchmarkResult(
            strategy="async_io",
            execution_time=execution_time,
            memory_usage=memory_usage,
            cpu_utilization=cpu_utilization,
            throughput=throughput,
            scalability_score=throughput / 8.0  # 理论最优为并发执行
        )
    
    def benchmark_shared_memory(self, size: int = 5000) -> BenchmarkResult:
        """共享内存基准测试"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # 创建共享内存数组
        shm_size = size * size * 4  # float32
        shm = shared_memory.SharedMemory(create=True, size=shm_size)
        
        try:
            # 创建numpy数组视图
            shared_array = np.ndarray((size, size), dtype=np.float32, buffer=shm.buf)
            shared_array[:] = np.random.rand(size, size)
            
            # 多进程处理共享数组
            def process_shared_array(shm_name: str, shape: tuple):
                existing_shm = shared_memory.SharedMemory(name=shm_name)
                array = np.ndarray(shape, dtype=np.float32, buffer=existing_shm.buf)
                # 执行计算
                result = np.sum(array * array)
                existing_shm.close()
                return result
            
            with ProcessPoolExecutor(max_workers=self.cpu_count) as executor:
                futures = [
                    executor.submit(process_shared_array, shm.name, (size, size))
                    for _ in range(8)
                ]
                results = [f.result() for f in futures]
        
        finally:
            shm.close()
            shm.unlink()
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        cpu_utilization = psutil.cpu_percent()
        throughput = len(results) / execution_time
        
        return BenchmarkResult(
            strategy="shared_memory",
            execution_time=execution_time,
            memory_usage=memory_usage,
            cpu_utilization=cpu_utilization,
            throughput=throughput,
            scalability_score=throughput / 2.0  # 相对基准
        )
    
    def benchmark_hybrid_approach(self) -> BenchmarkResult:
        """混合方法基准测试"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        async def hybrid_execution():
            # CPU密集型任务使用进程池
            cpu_pool = ProcessPoolExecutor(max_workers=self.cpu_count // 2)
            # I/O密集型任务使用异步
            
            loop = asyncio.get_event_loop()
            
            # 并行执行不同类型的任务
            cpu_tasks = [
                loop.run_in_executor(cpu_pool, self.cpu_intensive_task, 1000000)
                for _ in range(4)
            ]
            
            io_tasks = [
                self.async_io_task(0.05)
                for _ in range(4)
            ]
            
            # 等待所有任务完成
            cpu_results = await asyncio.gather(*cpu_tasks)
            io_results = await asyncio.gather(*io_tasks)
            
            cpu_pool.shutdown(wait=True)
            return cpu_results + io_results
        
        results = asyncio.run(hybrid_execution())
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        cpu_utilization = psutil.cpu_percent()
        throughput = len(results) / execution_time
        
        return BenchmarkResult(
            strategy="hybrid_approach",
            execution_time=execution_time,
            memory_usage=memory_usage,
            cpu_utilization=cpu_utilization,
            throughput=throughput,
            scalability_score=throughput / 4.0  # 相对基准
        )
    
    def run_comprehensive_benchmark(self) -> Dict[str, Dict[str, BenchmarkResult]]:
        """运行综合基准测试"""
        print("🚀 开始跨进程内存隔离性能基准测试...")
        print(f"系统配置: {self.cpu_count} CPU核心")
        print("-" * 80)
        
        test_scenarios = {
            "CPU密集型任务": {
                "function": self.cpu_intensive_task,
                "args": (1000000,),
                "kwargs": {}
            },
            "内存密集型任务": {
                "function": self.memory_intensive_task,
                "args": (3000,),
                "kwargs": {}
            },
            "I/O模拟任务": {
                "function": self.io_simulation_task,
                "args": (0.05,),
                "kwargs": {}
            }
        }
        
        all_results = {}
        
        for scenario_name, scenario_config in test_scenarios.items():
            print(f"\n📊 测试场景: {scenario_name}")
            scenario_results = {}
            
            # 单线程基准
            print("  测试: 单线程基准...")
            scenario_results["single_thread"] = self.benchmark_single_thread(
                scenario_config["function"],
                *scenario_config["args"],
                **scenario_config["kwargs"]
            )
            
            # 线程池测试
            print("  测试: 线程池...")
            scenario_results["thread_pool"] = self.benchmark_thread_pool(
                scenario_config["function"],
                *scenario_config["args"],
                **scenario_config["kwargs"]
            )
            
            # 进程池测试
            print("  测试: 进程池...")
            scenario_results["process_pool"] = self.benchmark_process_pool(
                scenario_config["function"],
                *scenario_config["args"],
                **scenario_config["kwargs"]
            )
            
            all_results[scenario_name] = scenario_results
        
        # 异步I/O测试
        print(f"\n📊 测试场景: 异步I/O")
        async_result = asyncio.run(self.benchmark_async_io(self.async_io_task, 0.05))
        all_results["异步I/O"] = {"async_io": async_result}
        
        # 共享内存测试
        print(f"\n📊 测试场景: 共享内存")
        shared_memory_result = self.benchmark_shared_memory(2000)
        all_results["共享内存"] = {"shared_memory": shared_memory_result}
        
        # 混合方法测试
        print(f"\n📊 测试场景: 混合方法")
        hybrid_result = self.benchmark_hybrid_approach()
        all_results["混合方法"] = {"hybrid": hybrid_result}
        
        self.results = all_results
        return all_results
    
    def generate_performance_report(self, output_file: str = "cross_process_benchmark_report.json"):
        """生成性能报告"""
        # 计算性能指标
        performance_summary = self._calculate_performance_metrics()
        
        report = {
            "benchmark_timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "system_info": {
                "cpu_count": self.cpu_count,
                "total_memory_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
                "python_version": f"{multiprocessing.sys.version_info.major}.{multiprocessing.sys.version_info.minor}"
            },
            "detailed_results": self._serialize_results(),
            "performance_summary": performance_summary,
            "recommendations": self._generate_recommendations(performance_summary)
        }
        
        # 保存报告
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 性能报告已保存到: {output_file}")
        return report
    
    def _serialize_results(self) -> Dict:
        """序列化结果"""
        serialized = {}
        for scenario, strategies in self.results.items():
            serialized[scenario] = {}
            for strategy, result in strategies.items():
                serialized[scenario][strategy] = {
                    "execution_time": result.execution_time,
                    "memory_usage": result.memory_usage,
                    "cpu_utilization": result.cpu_utilization,
                    "throughput": result.throughput,
                    "scalability_score": result.scalability_score
                }
        return serialized
    
    def _calculate_performance_metrics(self) -> Dict:
        """计算性能指标"""
        metrics = {}
        
        for scenario, strategies in self.results.items():
            if len(strategies) < 2:
                continue
                
            # 找到最佳策略
            best_strategy = max(strategies.items(), key=lambda x: x[1].scalability_score)
            worst_strategy = min(strategies.items(), key=lambda x: x[1].scalability_score)
            
            metrics[scenario] = {
                "best_strategy": {
                    "name": best_strategy[0],
                    "scalability_score": best_strategy[1].scalability_score,
                    "throughput": best_strategy[1].throughput
                },
                "worst_strategy": {
                    "name": worst_strategy[0],
                    "scalability_score": worst_strategy[1].scalability_score,
                    "throughput": worst_strategy[1].throughput
                },
                "performance_gap": best_strategy[1].scalability_score / worst_strategy[1].scalability_score
            }
        
        return metrics
    
    def _generate_recommendations(self, performance_summary: Dict) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        for scenario, metrics in performance_summary.items():
            best_strategy = metrics["best_strategy"]["name"]
            performance_gap = metrics["performance_gap"]
            
            if performance_gap > 3.0:
                recommendations.append(
                    f"{scenario}: 强烈建议使用{best_strategy}，性能提升{performance_gap:.1f}倍"
                )
            elif performance_gap > 1.5:
                recommendations.append(
                    f"{scenario}: 建议考虑使用{best_strategy}，性能提升{performance_gap:.1f}倍"
                )
            else:
                recommendations.append(
                    f"{scenario}: 当前策略已较优，性能差异不大"
                )
        
        # 总体建议
        recommendations.append("总体建议: 采用混合架构，根据任务类型选择最优策略")
        
        return recommendations
    
    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "="*80)
        print("🎯 跨进程内存隔离性能基准测试摘要")
        print("="*80)
        
        for scenario, strategies in self.results.items():
            print(f"\n📊 {scenario}:")
            
            # 按性能排序
            sorted_strategies = sorted(
                strategies.items(),
                key=lambda x: x[1].scalability_score,
                reverse=True
            )
            
            for i, (strategy, result) in enumerate(sorted_strategies, 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📊"
                print(f"  {emoji} {strategy}:")
                print(f"    执行时间: {result.execution_time:.3f}s")
                print(f"    吞吐量: {result.throughput:.2f} tasks/s")
                print(f"    可扩展性: {result.scalability_score:.2f}x")
                print(f"    内存使用: {result.memory_usage:.1f}MB")

def main():
    """主函数"""
    benchmark = CrossProcessBenchmark()
    
    # 运行基准测试
    results = benchmark.run_comprehensive_benchmark()
    
    # 打印摘要
    benchmark.print_summary()
    
    # 生成报告
    report = benchmark.generate_performance_report()
    
    # 打印建议
    print("\n💡 优化建议:")
    for i, recommendation in enumerate(report['recommendations'], 1):
        print(f"  {i}. {recommendation}")

if __name__ == "__main__":
    main() 