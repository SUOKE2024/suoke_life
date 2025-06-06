"""
gil_performance_test - 索克生活项目模块
"""

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import List, Dict, Any
import asyncio
import json
import multiprocessing
import pickle
import psutil
import time
import zlib

#!/usr/bin/env python3
"""
GIL性能影响测试脚本
用于评估项目中CPU密集型任务的GIL影响
"""


class GILPerformanceTester:
    """GIL性能测试器"""
    
    def __init__(self):
        self.results = {}
        self.cpu_count = multiprocessing.cpu_count()
        
    def cpu_intensive_task(self, n: int = 1000000) -> int:
        """CPU密集型任务模拟"""
        result = 0
        for i in range(n):
            result += i ** 2
        return result
    
    def numpy_computation_task(self, size: int = 10000) -> np.ndarray:
        """NumPy计算任务"""
        arr1 = np.random.rand(size, size)
        arr2 = np.random.rand(size, size)
        return np.dot(arr1, arr2)
    
    def pandas_processing_task(self, rows: int = 100000) -> pd.DataFrame:
        """Pandas数据处理任务"""
        df = pd.DataFrame({
            'A': np.random.randn(rows),
            'B': np.random.randn(rows),
            'C': np.random.randn(rows)
        })
        
        # 模拟数据处理操作
        df['D'] = df['A'] * df['B']
        df['E'] = df.groupby(pd.cut(df['C'], 10))['A'].transform('mean')
        return df.describe()
    
    def serialization_task(self, data_size: int = 1000000) -> bytes:
        """序列化任务"""
        data = {'numbers': list(range(data_size)), 'text': 'test' * 1000}
        serialized = pickle.dumps(data)
        compressed = zlib.compress(serialized)
        return compressed
    
    def test_single_thread(self, task_func, *args, **kwargs) -> Dict[str, Any]:
        """单线程测试"""
        start_time = time.time()
        
        results = []
        for _ in range(4):
            result = task_func(*args, **kwargs)
            results.append(result)
        
        end_time = time.time()
        
        return {
            'execution_time': end_time - start_time,
            'results_count': len(results),
            'cpu_usage_before': psutil.cpu_percent(),
            'memory_usage': psutil.Process().memory_info().rss / 1024 / 1024  # MB
        }
    
    def test_multi_thread(self, task_func, *args, **kwargs) -> Dict[str, Any]:
        """多线程测试（受GIL限制）"""
        start_time = time.time()
        cpu_before = psutil.cpu_percent()
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(task_func, *args, **kwargs) for _ in range(4)]
            results = [f.result() for f in futures]
        
        end_time = time.time()
        cpu_after = psutil.cpu_percent()
        
        return {
            'execution_time': end_time - start_time,
            'results_count': len(results),
            'cpu_usage_before': cpu_before,
            'cpu_usage_after': cpu_after,
            'memory_usage': psutil.Process().memory_info().rss / 1024 / 1024  # MB
        }
    
    def test_multi_process(self, task_func, *args, **kwargs) -> Dict[str, Any]:
        """多进程测试（绕过GIL）"""
        start_time = time.time()
        cpu_before = psutil.cpu_percent()
        
        with ProcessPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(task_func, *args, **kwargs) for _ in range(4)]
            results = [f.result() for f in futures]
        
        end_time = time.time()
        cpu_after = psutil.cpu_percent()
        
        return {
            'execution_time': end_time - start_time,
            'results_count': len(results),
            'cpu_usage_before': cpu_before,
            'cpu_usage_after': cpu_after,
            'memory_usage': psutil.Process().memory_info().rss / 1024 / 1024  # MB
        }
    
    async def test_async_io(self, delay: float = 0.1) -> Dict[str, Any]:
        """异步I/O测试（不受GIL限制）"""
        start_time = time.time()
        
        async def async_task():
            await asyncio.sleep(delay)
            return "completed"
        
        tasks = [async_task() for _ in range(4)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        
        return {
            'execution_time': end_time - start_time,
            'results_count': len(results),
            'memory_usage': psutil.Process().memory_info().rss / 1024 / 1024  # MB
        }
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """运行综合性能测试"""
        print("🚀 开始GIL性能影响测试...")
        print(f"CPU核心数: {self.cpu_count}")
        print(f"当前内存使用: {psutil.Process().memory_info().rss / 1024 / 1024:.2f}MB")
        print("-" * 60)
        
        test_cases = [
            ("CPU密集型计算", self.cpu_intensive_task, (), {}),
            ("NumPy矩阵运算", self.numpy_computation_task, (1000,), {}),
            ("Pandas数据处理", self.pandas_processing_task, (50000,), {}),
            ("序列化压缩", self.serialization_task, (100000,), {}),
        ]
        
        for test_name, task_func, args, kwargs in test_cases:
            print(f"\n📊 测试: {test_name}")
            
            # 单线程基准
            single_result = self.test_single_thread(task_func, *args, **kwargs)
            print(f"  单线程: {single_result['execution_time']:.2f}s")
            
            # 多线程测试
            multi_thread_result = self.test_multi_thread(task_func, *args, **kwargs)
            thread_speedup = single_result['execution_time'] / multi_thread_result['execution_time']
            print(f"  多线程: {multi_thread_result['execution_time']:.2f}s (加速比: {thread_speedup:.2f}x)")
            
            # 多进程测试
            try:
                multi_process_result = self.test_multi_process(task_func, *args, **kwargs)
                process_speedup = single_result['execution_time'] / multi_process_result['execution_time']
                print(f"  多进程: {multi_process_result['execution_time']:.2f}s (加速比: {process_speedup:.2f}x)")
            except Exception as e:
                print(f"  多进程: 测试失败 - {e}")
                multi_process_result = None
                process_speedup = 0
            
            # GIL影响分析
            gil_impact = self._analyze_gil_impact(thread_speedup, process_speedup)
            print(f"  GIL影响: {gil_impact}")
            
            # 保存结果
            self.results[test_name] = {
                'single_thread': single_result,
                'multi_thread': multi_thread_result,
                'multi_process': multi_process_result,
                'thread_speedup': thread_speedup,
                'process_speedup': process_speedup,
                'gil_impact': gil_impact
            }
        
        # 异步I/O测试
        print(f"\n📊 测试: 异步I/O")
        async_result = asyncio.run(self.test_async_io(0.1))
        print(f"  异步I/O: {async_result['execution_time']:.2f}s (理论最优: 0.10s)")
        
        self.results['异步I/O'] = async_result
        
        return self.results
    
    def _analyze_gil_impact(self, thread_speedup: float, process_speedup: float) -> str:
        """分析GIL影响程度"""
        if thread_speedup < 1.2:
            if process_speedup > 2.0:
                return "🔴 高GIL影响 - 建议使用多进程或异步"
            else:
                return "🟡 中等GIL影响 - 考虑算法优化"
        elif thread_speedup < 2.0:
            return "🟡 轻微GIL影响 - 可接受"
        else:
            return "🟢 无明显GIL影响"
    
    def generate_report(self, output_file: str = "gil_performance_report.json"):
        """生成性能报告"""
        report = {
            'test_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'system_info': {
                'cpu_count': self.cpu_count,
                'total_memory_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
                'python_version': f"{multiprocessing.sys.version_info.major}.{multiprocessing.sys.version_info.minor}",
            },
            'test_results': self.results,
            'recommendations': self._generate_recommendations()
        }
        
        # 保存JSON报告
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 性能报告已保存到: {output_file}")
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        for test_name, result in self.results.items():
            if test_name == '异步I/O':
                continue
                
            thread_speedup = result.get('thread_speedup', 0)
            process_speedup = result.get('process_speedup', 0)
            
            if thread_speedup < 1.2 and process_speedup > 2.0:
                recommendations.append(
                    f"{test_name}: 严重受GIL限制，建议使用ProcessPoolExecutor替代ThreadPoolExecutor"
                )
            elif thread_speedup < 1.5:
                recommendations.append(
                    f"{test_name}: 受GIL影响，考虑使用Numba JIT编译或C扩展优化"
                )
        
        if not recommendations:
            recommendations.append("当前测试场景下GIL影响较小，继续监控生产环境性能")
        
        return recommendations
    
    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("🎯 GIL性能测试摘要")
        print("="*60)
        
        high_impact_count = 0
        medium_impact_count = 0
        
        for test_name, result in self.results.items():
            if test_name == '异步I/O':
                continue
                
            gil_impact = result.get('gil_impact', '')
            if '🔴' in gil_impact:
                high_impact_count += 1
            elif '🟡' in gil_impact:
                medium_impact_count += 1
        
        print(f"高GIL影响任务: {high_impact_count}")
        print(f"中等GIL影响任务: {medium_impact_count}")
        print(f"总测试任务: {len(self.results) - 1}")  # 排除异步I/O
        
        if high_impact_count > 0:
            print("\n⚠️  建议立即优化高GIL影响的任务")
        elif medium_impact_count > 0:
            print("\n💡 考虑优化中等GIL影响的任务")
        else:
            print("\n✅ 当前GIL影响在可接受范围内")

def main():
    """主函数"""
    tester = GILPerformanceTester()
    
    # 运行测试
    results = tester.run_comprehensive_test()
    
    # 打印摘要
    tester.print_summary()
    
    # 生成报告
    report = tester.generate_report()
    
    # 打印建议
    print("\n💡 优化建议:")
    for i, recommendation in enumerate(report['recommendations'], 1):
        print(f"  {i}. {recommendation}")

if __name__ == "__main__":
    main() 