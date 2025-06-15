"""
性能测试

测试关键功能的性能指标
"""

import asyncio
import time
import pytest
from unittest.mock import AsyncMock, patch
from statistics import mean, median


class TestPerformance:
    """性能测试类"""

    @pytest.mark.asyncio
    async def test_auth_service_performance(self, auth_service, sample_user_data):
        """测试认证服务性能"""
        # 测试密码哈希性能
        start_time = time.time()
        for _ in range(100):
            auth_service.hash_password("testpassword123")
        hash_time = time.time() - start_time
        
        # 密码哈希应该在合理时间内完成
        assert hash_time < 5.0  # 100次哈希应在5秒内完成
        
        # 测试令牌创建性能
        user_data = {
            "user_id": "test_user_id",
            "username": "testuser",
            "role": "user"
        }
        
        start_time = time.time()
        for _ in range(1000):
            auth_service.create_access_token(user_data)
        token_time = time.time() - start_time
        
        # 1000次令牌创建应在1秒内完成
        assert token_time < 1.0

    @pytest.mark.asyncio
    async def test_agent_service_response_time(self, agent_service):
        """测试智能体服务响应时间"""
        # 模拟AI响应
        with patch('soer_service.services.agent_service.AgentService._call_ai_service') as mock_ai:
            mock_ai.return_value = {
                "response": "这是一个测试响应",
                "confidence": 0.95
            }
            
            response_times = []
            
            # 测试多次请求的响应时间
            for _ in range(10):
                start_time = time.time()
                await agent_service.process_message("test_user_id", "测试消息", {})
                response_time = time.time() - start_time
                response_times.append(response_time)
            
            # 平均响应时间应小于1秒
            avg_response_time = mean(response_times)
            assert avg_response_time < 1.0
            
            # 95%的请求应在2秒内完成
            response_times.sort()
            p95_time = response_times[int(len(response_times) * 0.95)]
            assert p95_time < 2.0

    @pytest.mark.asyncio
    async def test_health_data_processing_performance(self, health_service, sample_health_data):
        """测试健康数据处理性能"""
        # 模拟数据库操作
        health_service.mongodb["health_data"].insert_one = AsyncMock()
        
        processing_times = []
        
        # 测试批量数据处理
        for _ in range(50):
            start_time = time.time()
            await health_service.submit_health_data("test_user_id", sample_health_data)
            processing_time = time.time() - start_time
            processing_times.append(processing_time)
        
        # 平均处理时间应小于0.1秒
        avg_processing_time = mean(processing_times)
        assert avg_processing_time < 0.1

    @pytest.mark.asyncio
    async def test_nutrition_analysis_performance(self, nutrition_service, sample_nutrition_data):
        """测试营养分析性能"""
        # 模拟数据库和外部API调用
        nutrition_service.mongodb["nutrition_data"].insert_one = AsyncMock()
        
        with patch.object(nutrition_service, '_get_food_nutrition') as mock_nutrition:
            mock_nutrition.return_value = {
                "calories": 100,
                "protein": 5,
                "carbohydrates": 20,
                "fat": 2
            }
            
            analysis_times = []
            
            # 测试多次营养分析
            for _ in range(20):
                start_time = time.time()
                await nutrition_service.analyze_food(
                    sample_nutrition_data["foods"], 
                    "test_user_id"
                )
                analysis_time = time.time() - start_time
                analysis_times.append(analysis_time)
            
            # 平均分析时间应小于0.5秒
            avg_analysis_time = mean(analysis_times)
            assert avg_analysis_time < 0.5

    @pytest.mark.asyncio
    async def test_concurrent_requests_performance(self, agent_service):
        """测试并发请求性能"""
        # 模拟AI响应
        with patch('soer_service.services.agent_service.AgentService._call_ai_service') as mock_ai:
            mock_ai.return_value = {
                "response": "并发测试响应",
                "confidence": 0.95
            }
            
            async def single_request():
                return await agent_service.process_message("test_user_id", "并发测试", {})
            
            # 测试10个并发请求
            start_time = time.time()
            tasks = [single_request() for _ in range(10)]
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            # 10个并发请求应在3秒内完成
            assert total_time < 3.0
            assert len(results) == 10

    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, health_service, sample_health_data):
        """测试内存使用稳定性"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 模拟数据库操作
        health_service.mongodb["health_data"].insert_one = AsyncMock()
        
        # 执行大量操作
        for _ in range(100):
            await health_service.submit_health_data("test_user_id", sample_health_data)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # 内存增长应控制在合理范围内（50MB）
        assert memory_increase < 50 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_database_query_performance(self, health_service):
        """测试数据库查询性能"""
        # 模拟数据库查询
        mock_results = [
            {"data_id": f"test_{i}", "value": i} 
            for i in range(100)
        ]
        
        health_service.mongodb["health_data"].find = AsyncMock()
        health_service.mongodb["health_data"].find.return_value.to_list = AsyncMock(
            return_value=mock_results
        )
        
        query_times = []
        
        # 测试多次查询
        for _ in range(20):
            start_time = time.time()
            await health_service._get_health_history("test_user_id", days=30)
            query_time = time.time() - start_time
            query_times.append(query_time)
        
        # 平均查询时间应小于0.05秒
        avg_query_time = mean(query_times)
        assert avg_query_time < 0.05

    @pytest.mark.asyncio
    async def test_api_endpoint_throughput(self, client):
        """测试API端点吞吐量"""
        # 测试健康检查端点的吞吐量
        start_time = time.time()
        
        # 发送100个请求
        tasks = []
        for _ in range(100):
            tasks.append(client.get("/health"))
        
        responses = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # 计算吞吐量（请求/秒）
        throughput = len(responses) / total_time
        
        # 吞吐量应大于50 RPS
        assert throughput > 50
        
        # 所有请求都应该成功
        for response in responses:
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_large_data_processing(self, nutrition_service):
        """测试大数据量处理性能"""
        # 创建大量食物数据
        large_food_list = [
            {
                "name": f"食物_{i}",
                "quantity": 100,
                "unit": "g"
            }
            for i in range(100)
        ]
        
        # 模拟营养数据获取
        with patch.object(nutrition_service, '_get_food_nutrition') as mock_nutrition:
            mock_nutrition.return_value = {
                "calories": 100,
                "protein": 5,
                "carbohydrates": 20,
                "fat": 2
            }
            
            nutrition_service.mongodb["nutrition_data"].insert_one = AsyncMock()
            
            start_time = time.time()
            result = await nutrition_service.analyze_food(large_food_list, "test_user_id")
            processing_time = time.time() - start_time
            
            # 处理100个食物项目应在5秒内完成
            assert processing_time < 5.0
            assert result is not None

    @pytest.mark.asyncio
    async def test_cache_performance(self, agent_service):
        """测试缓存性能"""
        # 模拟Redis缓存
        agent_service.redis.get = AsyncMock(return_value=None)
        agent_service.redis.set = AsyncMock()
        
        # 第一次调用（无缓存）
        with patch('soer_service.services.agent_service.AgentService._call_ai_service') as mock_ai:
            mock_ai.return_value = {
                "response": "缓存测试响应",
                "confidence": 0.95
            }
            
            start_time = time.time()
            await agent_service.process_message("test_user_id", "缓存测试", {})
            first_call_time = time.time() - start_time
        
        # 第二次调用（有缓存）
        agent_service.redis.get = AsyncMock(return_value='{"response": "缓存响应"}')
        
        start_time = time.time()
        await agent_service.process_message("test_user_id", "缓存测试", {})
        cached_call_time = time.time() - start_time
        
        # 缓存调用应该明显更快
        assert cached_call_time < first_call_time * 0.5