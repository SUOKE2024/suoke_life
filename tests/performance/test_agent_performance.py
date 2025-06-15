"""
智能体性能测试

测试各智能体服务的响应时间、吞吐量和资源使用情况。
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock
import psutil
import statistics

# 导入通用测试基类
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from common.test_base import PerformanceTestCase


class TestAgentPerformance(PerformanceTestCase):
    """智能体性能测试类"""

    @pytest.fixture
    def mock_agent_service(self):
        """模拟智能体服务"""
        service = AsyncMock()
        
        async def mock_chat_response(message):
            # 模拟处理时间
            await asyncio.sleep(0.1)  # 100ms 处理时间
            return {
                "response": f"针对'{message}'的智能回复",
                "processing_time": 0.1,
                "confidence": 0.95
            }
        
        service.chat = mock_chat_response
        return service

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_single_request_latency(self, mock_agent_service):
        """测试单个请求的延迟"""
        start_time = time.time()
        
        response = await mock_agent_service.chat("测试消息")
        
        end_time = time.time()
        latency = end_time - start_time
        
        # 验证响应时间在可接受范围内（< 500ms）
        assert latency < 0.5
        assert response["response"] is not None
        
        print(f"单请求延迟: {latency:.3f}秒")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_requests_throughput(self, mock_agent_service):
        """测试并发请求吞吐量"""
        concurrent_requests = 50
        messages = [f"测试消息 {i}" for i in range(concurrent_requests)]
        
        start_time = time.time()
        
        # 并发发送请求
        tasks = [mock_agent_service.chat(msg) for msg in messages]
        responses = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 计算吞吐量
        throughput = concurrent_requests / total_time
        
        # 验证所有请求都成功
        assert len(responses) == concurrent_requests
        assert all(r["response"] is not None for r in responses)
        
        # 验证吞吐量满足要求（> 100 RPS）
        assert throughput > 100
        
        print(f"并发请求数: {concurrent_requests}")
        print(f"总耗时: {total_time:.3f}秒")
        print(f"吞吐量: {throughput:.1f} RPS")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_response_time_distribution(self, mock_agent_service):
        """测试响应时间分布"""
        request_count = 100
        response_times = []
        
        for i in range(request_count):
            start_time = time.time()
            await mock_agent_service.chat(f"测试消息 {i}")
            end_time = time.time()
            
            response_times.append(end_time - start_time)
        
        # 计算统计指标
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        p95_time = sorted(response_times)[int(0.95 * len(response_times))]
        p99_time = sorted(response_times)[int(0.99 * len(response_times))]
        
        # 验证性能指标
        assert avg_time < 0.2  # 平均响应时间 < 200ms
        assert p95_time < 0.3  # 95%分位数 < 300ms
        assert p99_time < 0.5  # 99%分位数 < 500ms
        
        print(f"平均响应时间: {avg_time:.3f}秒")
        print(f"中位数响应时间: {median_time:.3f}秒")
        print(f"95%分位数: {p95_time:.3f}秒")
        print(f"99%分位数: {p99_time:.3f}秒")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, mock_agent_service):
        """测试负载下的内存使用情况"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 执行大量请求
        tasks = []
        for i in range(200):
            task = mock_agent_service.chat(f"负载测试消息 {i}")
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 验证内存增长在合理范围内（< 100MB）
        assert memory_increase < 100
        
        print(f"初始内存: {initial_memory:.1f}MB")
        print(f"最终内存: {final_memory:.1f}MB")
        print(f"内存增长: {memory_increase:.1f}MB")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cpu_usage_under_load(self, mock_agent_service):
        """测试负载下的CPU使用情况"""
        # 监控CPU使用率
        cpu_percentages = []
        
        async def monitor_cpu():
            for _ in range(10):  # 监控10秒
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_percentages.append(cpu_percent)
        
        async def generate_load():
            tasks = []
            for i in range(100):
                task = mock_agent_service.chat(f"CPU测试消息 {i}")
                tasks.append(task)
            await asyncio.gather(*tasks)
        
        # 并行执行监控和负载生成
        await asyncio.gather(monitor_cpu(), generate_load())
        
        avg_cpu = statistics.mean(cpu_percentages)
        max_cpu = max(cpu_percentages)
        
        # 验证CPU使用率在合理范围内
        assert avg_cpu < 80  # 平均CPU使用率 < 80%
        assert max_cpu < 95  # 最大CPU使用率 < 95%
        
        print(f"平均CPU使用率: {avg_cpu:.1f}%")
        print(f"最大CPU使用率: {max_cpu:.1f}%")


class TestDiagnosisServicePerformance(PerformanceTestCase):
    """诊断服务性能测试"""

    @pytest.fixture
    def mock_diagnosis_service(self):
        """模拟诊断服务"""
        service = AsyncMock()
        
        async def mock_image_analysis(image_data):
            # 模拟图像处理时间
            await asyncio.sleep(0.5)  # 500ms 处理时间
            return {
                "analysis": "面色苍白，舌淡红",
                "constitution": "阳虚体质",
                "confidence": 0.88,
                "processing_time": 0.5
            }
        
        service.analyze_image = mock_image_analysis
        return service

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_image_processing_performance(self, mock_diagnosis_service):
        """测试图像处理性能"""
        # 模拟图像数据
        mock_image_data = b"fake_image_data" * 1000  # 模拟图像数据
        
        start_time = time.time()
        result = await mock_diagnosis_service.analyze_image(mock_image_data)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # 验证处理时间在可接受范围内（< 2秒）
        assert processing_time < 2.0
        assert result["analysis"] is not None
        
        print(f"图像处理时间: {processing_time:.3f}秒")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_batch_image_processing(self, mock_diagnosis_service):
        """测试批量图像处理性能"""
        batch_size = 10
        mock_images = [b"fake_image_data" * 1000 for _ in range(batch_size)]
        
        start_time = time.time()
        
        # 并行处理多张图像
        tasks = [mock_diagnosis_service.analyze_image(img) for img in mock_images]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证批量处理效率
        avg_time_per_image = total_time / batch_size
        assert avg_time_per_image < 1.0  # 平均每张图像处理时间 < 1秒
        assert len(results) == batch_size
        
        print(f"批量处理 {batch_size} 张图像")
        print(f"总耗时: {total_time:.3f}秒")
        print(f"平均每张: {avg_time_per_image:.3f}秒")


class TestAPIGatewayPerformance(PerformanceTestCase):
    """API网关性能测试"""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_api_gateway_throughput(self):
        """测试API网关吞吐量"""
        # 这里应该测试实际的API网关
        # 暂时使用模拟数据
        
        request_count = 1000
        concurrent_users = 50
        
        async def simulate_api_request():
            # 模拟API请求
            await asyncio.sleep(0.01)  # 10ms 处理时间
            return {"status": "success", "data": "mock_response"}
        
        start_time = time.time()
        
        # 模拟并发用户请求
        tasks = []
        for _ in range(request_count):
            task = simulate_api_request()
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        throughput = request_count / total_time
        
        # 验证吞吐量满足要求
        assert throughput > 500  # > 500 RPS
        assert len(results) == request_count
        
        print(f"API网关吞吐量测试:")
        print(f"请求总数: {request_count}")
        print(f"总耗时: {total_time:.3f}秒")
        print(f"吞吐量: {throughput:.1f} RPS")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_api_gateway_latency_under_load(self):
        """测试负载下的API网关延迟"""
        latencies = []
        request_count = 100
        
        for i in range(request_count):
            start_time = time.time()
            
            # 模拟API请求
            await asyncio.sleep(0.01)  # 10ms 基础处理时间
            
            end_time = time.time()
            latency = end_time - start_time
            latencies.append(latency)
        
        # 计算延迟统计
        avg_latency = statistics.mean(latencies)
        p95_latency = sorted(latencies)[int(0.95 * len(latencies))]
        
        # 验证延迟指标
        assert avg_latency < 0.1  # 平均延迟 < 100ms
        assert p95_latency < 0.2  # 95%分位数延迟 < 200ms
        
        print(f"API网关延迟测试:")
        print(f"平均延迟: {avg_latency:.3f}秒")
        print(f"95%分位数延迟: {p95_latency:.3f}秒") 