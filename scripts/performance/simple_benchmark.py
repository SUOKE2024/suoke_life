"""
simple_benchmark - 索克生活项目模块
"""

from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from numba import jit
from typing import Dict, List, Any
import json
import logging
import multiprocessing
import psutil
import time

#!/usr/bin/env python3
"""
索克生活 - 简化性能基准测试
验证基础优化效果
"""


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
    speedup: float
    additional_metrics: Dict[str, Any]

@jit(nopython=True)
def jit_vector_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """JIT优化的向量相似度计算"""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)

@jit(nopython=True)
def jit_matrix_multiply(matrix1: np.ndarray, matrix2: np.ndarray) -> np.ndarray:
    """JIT优化的矩阵乘法"""
    return np.dot(matrix1, matrix2)

def cpu_intensive_task(data_size: int) -> float:
    """CPU密集型任务"""
    data = np.random.rand(data_size, data_size)
    result = np.sum(np.dot(data, data.T))
    return result

class SimpleBenchmark:
    """简化性能基准测试"""

    def __init__(self):
        self.results: List[BenchmarkResult] = []

    def run_all_benchmarks(self) -> Dict[str, Any]:
        """运行所有基准测试"""
        logger.info("🚀 开始运行简化性能基准测试...")

        # 1. JIT编译优化测试
        self._test_jit_optimization()

        # 2. 进程池优化测试
        self._test_process_pool_optimization()

        # 3. 内存优化测试
        self._test_memory_optimization()

        # 生成报告
        return self._generate_report()

    def _test_jit_optimization(self):
        """测试JIT编译优化"""
        logger.info("📊 测试JIT编译优化...")

        # 准备测试数据
        vec1 = np.random.rand(10000).astype(np.float32)
        vec2 = np.random.rand(10000).astype(np.float32)
        matrix1 = np.random.rand(1000, 1000).astype(np.float32)
        matrix2 = np.random.rand(1000, 1000).astype(np.float32)

        iterations = 100

        # 测试普通计算
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        for _ in range(iterations):
            # 普通向量相似度
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            similarity = dot_product / (norm1 * norm2)

        normal_time = time.time() - start_time
        normal_memory = psutil.Process().memory_info().rss / 1024 / 1024 - start_memory

        # 测试JIT优化计算
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        for _ in range(iterations):
            # JIT优化向量相似度
            similarity = jit_vector_similarity(vec1, vec2)

        jit_time = time.time() - start_time
        jit_memory = psutil.Process().memory_info().rss / 1024 / 1024 - start_memory

        speedup = normal_time / jit_time if jit_time > 0 else 1.0

        self.results.append(BenchmarkResult(
            test_name="JIT编译优化",
            execution_time=jit_time,
            memory_usage=jit_memory,
            throughput=iterations / jit_time,
            speedup=speedup,
            additional_metrics={
                "normal_time": normal_time,
                "jit_time": jit_time,
                "iterations": iterations,
                "vector_size": len(vec1)
            }
        ))

        logger.info(f"✅ JIT优化测试完成 - 加速比: {speedup:.2f}x")

    def _test_process_pool_optimization(self):
        """测试进程池优化"""
        logger.info("📊 测试进程池优化...")

        data_sizes = [300, 300, 300, 300]  # 4个任务

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

        speedup = serial_time / parallel_time if parallel_time > 0 else 1.0

        self.results.append(BenchmarkResult(
            test_name="进程池优化",
            execution_time=parallel_time,
            memory_usage=parallel_memory,
            throughput=len(data_sizes) / parallel_time,
            speedup=speedup,
            additional_metrics={
                "serial_time": serial_time,
                "parallel_time": parallel_time,
                "cpu_cores": multiprocessing.cpu_count(),
                "tasks_count": len(data_sizes)
            }
        ))

        logger.info(f"✅ 进程池优化测试完成 - 加速比: {speedup:.2f}x")

    def _test_memory_optimization(self):
        """测试内存优化"""
        logger.info("📊 测试内存优化...")

        def memory_efficient_processing(data_size: int) -> Dict[str, float]:
            """内存高效的数据处理"""
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024

            # 使用生成器避免大量内存分配
            def data_generator():
                for i in range(data_size):
                    yield np.random.rand(100)

            # 流式处理
            total_sum = 0.0
            count = 0
            for data_chunk in data_generator():
                total_sum += np.sum(data_chunk)
                count += 1

            end_memory = psutil.Process().memory_info().rss / 1024 / 1024

            return {
                "average": total_sum / count if count > 0 else 0.0,
                "memory_used": end_memory - start_memory,
                "processed_chunks": count
            }

        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        result = memory_efficient_processing(10000)

        execution_time = time.time() - start_time
        memory_usage = psutil.Process().memory_info().rss / 1024 / 1024 - start_memory

        self.results.append(BenchmarkResult(
            test_name="内存优化",
            execution_time=execution_time,
            memory_usage=memory_usage,
            throughput=result["processed_chunks"] / execution_time,
            speedup=1.0,  # 基准值
            additional_metrics={
                "processed_chunks": result["processed_chunks"],
                "average_value": result["average"],
                "memory_efficiency": result["processed_chunks"] / memory_usage if memory_usage > 0 else 0
            }
        ))

        logger.info(f"✅ 内存优化测试完成 - 处理了 {result['processed_chunks']} 个数据块")

    def _generate_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        logger.info("📋 生成性能报告...")

        total_speedup = sum(result.speedup for result in self.results) / len(self.results)
        total_memory = sum(result.memory_usage for result in self.results)
        total_throughput = sum(result.throughput for result in self.results)

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(self.results),
                "average_speedup": total_speedup,
                "total_memory_usage_mb": total_memory,
                "total_throughput": total_throughput,
                "cpu_cores": multiprocessing.cpu_count(),
                "system_memory_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024
            },
            "detailed_results": [
                {
                    "test_name": result.test_name,
                    "execution_time_s": result.execution_time,
                    "memory_usage_mb": result.memory_usage,
                    "throughput": result.throughput,
                    "speedup": result.speedup,
                    "additional_metrics": result.additional_metrics
                }
                for result in self.results
            ],
            "recommendations": self._generate_recommendations()
        }

        # 保存报告
        report_file = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"📊 性能报告已保存到: {report_file}")

        # 打印摘要
        print("\n" + "="*60)
        print("🎯 索克生活 - 性能优化基准测试报告")
        print("="*60)
        print(f"📈 平均加速比: {total_speedup:.2f}x")
        print(f"💾 总内存使用: {total_memory:.2f} MB")
        print(f"⚡ 总吞吐量: {total_throughput:.2f} ops/s")
        print(f"🖥️  CPU核心数: {multiprocessing.cpu_count()}")
        print(f"🧠 系统内存: {psutil.virtual_memory().total / 1024 / 1024 / 1024:.1f} GB")
        print("\n📋 详细结果:")

        for result in self.results:
            print(f"  • {result.test_name}:")
            print(f"    - 执行时间: {result.execution_time:.3f}s")
            print(f"    - 内存使用: {result.memory_usage:.2f}MB")
            print(f"    - 加速比: {result.speedup:.2f}x")
            print(f"    - 吞吐量: {result.throughput:.2f} ops/s")

        print("\n💡 优化建议:")
        for i, recommendation in enumerate(report["recommendations"], 1):
            print(f"  {i}. {recommendation}")

        print("="*60)

        return report

    def _generate_recommendations(self) -> List[str]:
        """生成优化建议"""
        recommendations = []

        # 基于测试结果生成建议
        jit_result = next((r for r in self.results if r.test_name == "JIT编译优化"), None)
        if jit_result and jit_result.speedup > 2.0:
            recommendations.append("JIT编译显著提升性能，建议在数值计算密集的模块中广泛使用")

        process_result = next((r for r in self.results if r.test_name == "进程池优化"), None)
        if process_result and process_result.speedup > 1.5:
            recommendations.append("进程池优化效果良好，建议在CPU密集型任务中使用多进程")

        memory_result = next((r for r in self.results if r.test_name == "内存优化"), None)
        if memory_result and memory_result.memory_usage < 100:
            recommendations.append("内存使用效率高，建议继续使用流式处理和生成器模式")

        # 通用建议
        recommendations.extend([
            "继续监控生产环境性能指标",
            "定期运行基准测试验证优化效果",
            "考虑使用缓存机制进一步提升性能"
        ])

        return recommendations

def main():
    """主函数"""
    benchmark = SimpleBenchmark()
    report = benchmark.run_all_benchmarks()
    return report

if __name__ == "__main__":
    main() 