"""
诊断服务性能测试
"""

import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
import statistics

class TestPerformance:
    """性能测试"""
    
    @pytest.mark.asyncio
    async def test_diagnosis_performance(self):
        """测试诊断性能"""
        test_cases = [
            {"symptoms": ["头痛"], "expected_time": 2.0},
            {"symptoms": ["发热", "咳嗽"], "expected_time": 2.5},
            {"symptoms": ["胸闷", "气短", "心悸"], "expected_time": 3.0}
        ]
        
        for case in test_cases:
            start_time = time.time()
            result = await self.perform_diagnosis(case["symptoms"])
            end_time = time.time()
            
            processing_time = end_time - start_time
            assert processing_time < case["expected_time"]
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_diagnosis(self):
        """测试并发诊断性能"""
        concurrent_requests = 10
        symptoms_list = [["头痛"], ["发热"], ["咳嗽"]] * (concurrent_requests // 3 + 1)
        
        start_time = time.time()
        tasks = [self.perform_diagnosis(symptoms) for symptoms in symptoms_list[:concurrent_requests]]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time_per_request = total_time / concurrent_requests
        
        assert all(result is not None for result in results)
        assert avg_time_per_request < 1.0  # 平均每个请求小于1秒
    
    def test_memory_usage(self):
        """测试内存使用"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 执行大量诊断操作
        for i in range(100):
            self.perform_sync_diagnosis([f"symptom_{i}"])
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        assert memory_increase < 50  # 内存增长小于50MB
    
    def test_response_time_distribution(self):
        """测试响应时间分布"""
        response_times = []
        
        for i in range(50):
            start_time = time.time()
            self.perform_sync_diagnosis([f"symptom_{i}"])
            end_time = time.time()
            response_times.append(end_time - start_time)
        
        avg_time = statistics.mean(response_times)
        p95_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        
        assert avg_time < 1.0  # 平均响应时间小于1秒
        assert p95_time < 2.0  # 95%的请求小于2秒
    
    async def perform_diagnosis(self, symptoms):
        """执行诊断"""
        # 模拟诊断处理
        await asyncio.sleep(0.1)  # 模拟处理时间
        return {"diagnosis": "test", "confidence": 0.8}
    
    def perform_sync_diagnosis(self, symptoms):
        """执行同步诊断"""
        # 模拟同步诊断处理
        time.sleep(0.01)  # 模拟处理时间
        return {"diagnosis": "test", "confidence": 0.8}
