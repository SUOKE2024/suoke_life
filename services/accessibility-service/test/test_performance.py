#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
性能测试
测试并发性能、响应时间、内存使用、缓存性能等
"""

import pytest
import asyncio
import time
import psutil
import statistics
from unittest.mock import Mock, AsyncMock
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

# 导入服务组件
from internal.service.coordinators import AccessibilityServiceCoordinator
from internal.service.factories import AccessibilityServiceFactory
from internal.service.implementations import (
    BlindAssistanceServiceImpl,
    VoiceAssistanceServiceImpl,
    SignLanguageServiceImpl,
    ScreenReadingServiceImpl,
    ContentConversionServiceImpl
)


class TestPerformanceBenchmarks:
    """性能基准测试类"""
    
    @pytest.fixture
    async def performance_coordinator(self):
        """创建性能测试用协调器"""
        mock_model_manager = Mock()
        mock_model_manager.load_model = AsyncMock(return_value=Mock())
        mock_model_manager.unload_model = AsyncMock()
        
        mock_cache_manager = Mock()
        mock_cache_manager.get = AsyncMock(return_value=None)
        mock_cache_manager.set = AsyncMock()
        mock_cache_manager.delete = AsyncMock()
        
        factory = AccessibilityServiceFactory()
        factory._model_manager = mock_model_manager
        factory._cache_manager = mock_cache_manager
        
        await factory.initialize()
        
        coordinator = AccessibilityServiceCoordinator(factory)
        await coordinator.initialize()
        
        return coordinator
    
    @pytest.mark.asyncio
    async def test_concurrent_request_performance(self, performance_coordinator):
        """测试并发请求性能"""
        # 测试参数
        concurrent_users = [10, 50, 100, 200]
        requests_per_user = 5
        
        performance_results = {}
        
        for user_count in concurrent_users:
            print(f"\n测试 {user_count} 个并发用户...")
            
            # 记录开始时间和内存
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            # 创建并发任务
            tasks = []
            for user_id in range(user_count):
                for req_id in range(requests_per_user):
                    task = performance_coordinator.analyze_scene(
                        b'fake_image_data',
                        f'user_{user_id}',
                        {'detail_level': 'basic'},
                        {'lat': 39.9, 'lng': 116.4}
                    )
                    tasks.append(task)
            
            # 执行并发请求
            start_exec_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_exec_time = time.time()
            
            # 记录结束时间和内存
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            # 计算性能指标
            total_requests = user_count * requests_per_user
            execution_time = end_exec_time - start_exec_time
            total_time = end_time - start_time
            memory_usage = end_memory - start_memory
            
            # 统计成功和失败的请求
            successful_requests = sum(1 for r in results if not isinstance(r, Exception))
            failed_requests = total_requests - successful_requests
            
            # 计算响应时间统计
            response_times = []
            for result in results:
                if not isinstance(result, Exception) and 'processing_time_ms' in result:
                    response_times.append(result['processing_time_ms'])
            
            performance_results[user_count] = {
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'failed_requests': failed_requests,
                'success_rate': successful_requests / total_requests * 100,
                'execution_time': execution_time,
                'total_time': total_time,
                'qps': total_requests / execution_time,
                'avg_response_time': statistics.mean(response_times) if response_times else 0,
                'p95_response_time': statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0,
                'p99_response_time': statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else 0,
                'memory_usage_mb': memory_usage
            }
            
            print(f"  QPS: {performance_results[user_count]['qps']:.2f}")
            print(f"  成功率: {performance_results[user_count]['success_rate']:.2f}%")
            print(f"  平均响应时间: {performance_results[user_count]['avg_response_time']:.2f}ms")
            print(f"  内存使用: {performance_results[user_count]['memory_usage_mb']:.2f}MB")
        
        # 验证性能要求
        for user_count, metrics in performance_results.items():
            # 成功率应该 > 99%
            assert metrics['success_rate'] > 99.0, f"{user_count}用户时成功率过低: {metrics['success_rate']:.2f}%"
            
            # QPS应该 > 50（根据实际情况调整）
            if user_count >= 50:
                assert metrics['qps'] > 50, f"{user_count}用户时QPS过低: {metrics['qps']:.2f}"
            
            # 平均响应时间应该 < 500ms
            assert metrics['avg_response_time'] < 500, f"{user_count}用户时响应时间过长: {metrics['avg_response_time']:.2f}ms"
        
        return performance_results
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, performance_coordinator):
        """测试负载下的内存使用"""
        # 记录初始内存
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # 执行大量请求
        tasks = []
        for i in range(1000):
            task = performance_coordinator.analyze_scene(
                b'fake_image_data' * 100,  # 增大数据量
                f'user_{i}',
                {'detail_level': 'detailed'},
                {'lat': 39.9, 'lng': 116.4}
            )
            tasks.append(task)
        
        # 分批执行以避免内存爆炸
        batch_size = 100
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            await asyncio.gather(*batch, return_exceptions=True)
            
            # 检查内存使用
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_increase = current_memory - initial_memory
            
            print(f"批次 {i//batch_size + 1}: 内存使用 {current_memory:.2f}MB (+{memory_increase:.2f}MB)")
            
            # 内存增长不应该超过500MB
            assert memory_increase < 500, f"内存使用过高: {memory_increase:.2f}MB"
        
        # 最终内存检查
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        total_increase = final_memory - initial_memory
        
        print(f"总内存增长: {total_increase:.2f}MB")
        assert total_increase < 300, f"总内存增长过高: {total_increase:.2f}MB"
    
    @pytest.mark.asyncio
    async def test_service_startup_performance(self):
        """测试服务启动性能"""
        startup_times = {}
        
        # 测试各个服务的启动时间
        services_to_test = [
            ('BlindAssistanceService', BlindAssistanceServiceImpl),
            ('VoiceAssistanceService', VoiceAssistanceServiceImpl),
            ('SignLanguageService', SignLanguageServiceImpl),
            ('ScreenReadingService', ScreenReadingServiceImpl),
            ('ContentConversionService', ContentConversionServiceImpl)
        ]
        
        for service_name, service_class in services_to_test:
            # 准备模拟依赖
            mock_model_manager = Mock()
            mock_model_manager.load_model = AsyncMock(return_value=Mock())
            mock_model_manager.unload_model = AsyncMock()
            
            mock_cache_manager = Mock()
            mock_cache_manager.get = AsyncMock(return_value=None)
            mock_cache_manager.set = AsyncMock()
            mock_cache_manager.delete = AsyncMock()
            
            # 测试启动时间
            start_time = time.time()
            
            service = service_class(
                mock_model_manager, mock_cache_manager, enabled=True
            )
            await service.initialize()
            
            end_time = time.time()
            startup_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            startup_times[service_name] = startup_time
            print(f"{service_name} 启动时间: {startup_time:.2f}ms")
            
            # 清理
            await service.cleanup()
            
            # 启动时间应该 < 5秒
            assert startup_time < 5000, f"{service_name} 启动时间过长: {startup_time:.2f}ms"
        
        # 总体启动时间应该合理
        total_startup_time = sum(startup_times.values())
        print(f"所有服务总启动时间: {total_startup_time:.2f}ms")
        assert total_startup_time < 20000, f"总启动时间过长: {total_startup_time:.2f}ms"
        
        return startup_times


class TestCachePerformance:
    """缓存性能测试类"""
    
    @pytest.fixture
    async def cache_test_service(self):
        """创建缓存测试服务"""
        mock_model_manager = Mock()
        mock_model_manager.load_model = AsyncMock(return_value=Mock())
        mock_model_manager.unload_model = AsyncMock()
        
        # 模拟缓存管理器，记录缓存操作
        mock_cache_manager = Mock()
        mock_cache_manager.cache_hits = 0
        mock_cache_manager.cache_misses = 0
        
        async def mock_get(key):
            if 'cached_key' in key:
                mock_cache_manager.cache_hits += 1
                return {'cached': True, 'data': 'cached_result'}
            else:
                mock_cache_manager.cache_misses += 1
                return None
        
        mock_cache_manager.get = AsyncMock(side_effect=mock_get)
        mock_cache_manager.set = AsyncMock()
        mock_cache_manager.delete = AsyncMock()
        
        service = BlindAssistanceServiceImpl(
            mock_model_manager, mock_cache_manager, enabled=True
        )
        await service.initialize()
        
        return service, mock_cache_manager
    
    @pytest.mark.asyncio
    async def test_cache_hit_ratio(self, cache_test_service):
        """测试缓存命中率"""
        service, cache_manager = cache_test_service
        
        # 第一次请求（缓存未命中）
        result1 = await service.analyze_scene(
            b'fake_image_data', 'user1', {}, {'lat': 39.9, 'lng': 116.4}
        )
        
        # 相同请求（应该命中缓存）
        result2 = await service.analyze_scene(
            b'fake_image_data', 'user1', {}, {'lat': 39.9, 'lng': 116.4}
        )
        
        # 不同请求（缓存未命中）
        result3 = await service.analyze_scene(
            b'different_image_data', 'user2', {}, {'lat': 40.0, 'lng': 117.0}
        )
        
        # 验证结果
        assert result1 is not None
        assert result2 is not None
        assert result3 is not None
        
        # 计算缓存命中率
        total_requests = cache_manager.cache_hits + cache_manager.cache_misses
        hit_ratio = cache_manager.cache_hits / total_requests if total_requests > 0 else 0
        
        print(f"缓存命中: {cache_manager.cache_hits}")
        print(f"缓存未命中: {cache_manager.cache_misses}")
        print(f"缓存命中率: {hit_ratio * 100:.2f}%")
        
        # 缓存命中率应该合理（这里期望至少有一些命中）
        assert cache_manager.cache_hits > 0, "应该有缓存命中"
    
    @pytest.mark.asyncio
    async def test_cache_performance_impact(self, cache_test_service):
        """测试缓存对性能的影响"""
        service, cache_manager = cache_test_service
        
        # 测试无缓存性能
        cache_manager.get = AsyncMock(return_value=None)  # 强制缓存未命中
        
        start_time = time.time()
        for i in range(50):
            await service.analyze_scene(
                b'fake_image_data', f'user_{i}', {}, {'lat': 39.9, 'lng': 116.4}
            )
        no_cache_time = time.time() - start_time
        
        # 测试有缓存性能
        cache_manager.get = AsyncMock(return_value={'cached': True, 'data': 'result'})  # 强制缓存命中
        
        start_time = time.time()
        for i in range(50):
            await service.analyze_scene(
                b'fake_image_data', f'user_{i}', {}, {'lat': 39.9, 'lng': 116.4}
            )
        with_cache_time = time.time() - start_time
        
        # 计算性能提升
        performance_improvement = (no_cache_time - with_cache_time) / no_cache_time * 100
        
        print(f"无缓存时间: {no_cache_time:.3f}s")
        print(f"有缓存时间: {with_cache_time:.3f}s")
        print(f"性能提升: {performance_improvement:.2f}%")
        
        # 缓存应该显著提升性能
        assert with_cache_time < no_cache_time, "缓存应该提升性能"
        assert performance_improvement > 30, f"缓存性能提升不足: {performance_improvement:.2f}%"


class TestScalabilityPerformance:
    """可扩展性性能测试类"""
    
    @pytest.mark.asyncio
    async def test_horizontal_scaling_simulation(self):
        """测试水平扩展模拟"""
        # 模拟不同数量的服务实例
        instance_counts = [1, 2, 4, 8]
        performance_metrics = {}
        
        for instance_count in instance_counts:
            print(f"\n测试 {instance_count} 个服务实例...")
            
            # 创建多个服务实例
            services = []
            for i in range(instance_count):
                mock_model_manager = Mock()
                mock_model_manager.load_model = AsyncMock(return_value=Mock())
                mock_model_manager.unload_model = AsyncMock()
                
                mock_cache_manager = Mock()
                mock_cache_manager.get = AsyncMock(return_value=None)
                mock_cache_manager.set = AsyncMock()
                mock_cache_manager.delete = AsyncMock()
                
                service = BlindAssistanceServiceImpl(
                    mock_model_manager, mock_cache_manager, enabled=True
                )
                await service.initialize()
                services.append(service)
            
            # 测试负载分发
            total_requests = 200
            requests_per_instance = total_requests // instance_count
            
            start_time = time.time()
            
            # 为每个实例分配请求
            all_tasks = []
            for i, service in enumerate(services):
                instance_tasks = []
                for j in range(requests_per_instance):
                    task = service.analyze_scene(
                        b'fake_image_data',
                        f'user_{i}_{j}',
                        {},
                        {'lat': 39.9, 'lng': 116.4}
                    )
                    instance_tasks.append(task)
                all_tasks.extend(instance_tasks)
            
            # 并行执行所有请求
            results = await asyncio.gather(*all_tasks, return_exceptions=True)
            end_time = time.time()
            
            # 计算性能指标
            execution_time = end_time - start_time
            successful_requests = sum(1 for r in results if not isinstance(r, Exception))
            qps = successful_requests / execution_time
            
            performance_metrics[instance_count] = {
                'execution_time': execution_time,
                'successful_requests': successful_requests,
                'qps': qps,
                'efficiency': qps / instance_count  # 每实例QPS
            }
            
            print(f"  执行时间: {execution_time:.3f}s")
            print(f"  成功请求: {successful_requests}")
            print(f"  QPS: {qps:.2f}")
            print(f"  每实例效率: {performance_metrics[instance_count]['efficiency']:.2f} QPS/实例")
            
            # 清理服务
            for service in services:
                await service.cleanup()
        
        # 验证扩展性
        # QPS应该随实例数量增加而增加
        for i in range(1, len(instance_counts)):
            current_count = instance_counts[i]
            previous_count = instance_counts[i-1]
            
            current_qps = performance_metrics[current_count]['qps']
            previous_qps = performance_metrics[previous_count]['qps']
            
            # QPS增长应该是正向的
            assert current_qps > previous_qps, f"QPS没有随实例数增加: {previous_qps} -> {current_qps}"
            
            # 效率不应该显著下降（允许一定的开销）
            current_efficiency = performance_metrics[current_count]['efficiency']
            previous_efficiency = performance_metrics[previous_count]['efficiency']
            efficiency_ratio = current_efficiency / previous_efficiency
            
            assert efficiency_ratio > 0.7, f"扩展效率下降过多: {efficiency_ratio:.2f}"
        
        return performance_metrics
    
    @pytest.mark.asyncio
    async def test_resource_utilization_under_load(self):
        """测试负载下的资源利用率"""
        # 创建服务
        mock_model_manager = Mock()
        mock_model_manager.load_model = AsyncMock(return_value=Mock())
        mock_model_manager.unload_model = AsyncMock()
        
        mock_cache_manager = Mock()
        mock_cache_manager.get = AsyncMock(return_value=None)
        mock_cache_manager.set = AsyncMock()
        mock_cache_manager.delete = AsyncMock()
        
        service = BlindAssistanceServiceImpl(
            mock_model_manager, mock_cache_manager, enabled=True
        )
        await service.initialize()
        
        # 监控资源使用
        process = psutil.Process()
        
        # 记录基线资源使用
        baseline_cpu = process.cpu_percent()
        baseline_memory = process.memory_info().rss / 1024 / 1024
        
        # 执行负载测试
        load_levels = [10, 50, 100, 200]
        resource_metrics = {}
        
        for load_level in load_levels:
            print(f"\n测试负载级别: {load_level} 并发请求")
            
            # 创建负载
            tasks = []
            for i in range(load_level):
                task = service.analyze_scene(
                    b'fake_image_data',
                    f'user_{i}',
                    {},
                    {'lat': 39.9, 'lng': 116.4}
                )
                tasks.append(task)
            
            # 执行并监控资源
            start_time = time.time()
            cpu_samples = []
            memory_samples = []
            
            # 启动资源监控
            async def monitor_resources():
                while True:
                    cpu_samples.append(process.cpu_percent())
                    memory_samples.append(process.memory_info().rss / 1024 / 1024)
                    await asyncio.sleep(0.1)
            
            monitor_task = asyncio.create_task(monitor_resources())
            
            # 执行负载
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 停止监控
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
            
            end_time = time.time()
            
            # 计算资源指标
            if cpu_samples and memory_samples:
                avg_cpu = statistics.mean(cpu_samples)
                max_cpu = max(cpu_samples)
                avg_memory = statistics.mean(memory_samples)
                max_memory = max(memory_samples)
                
                resource_metrics[load_level] = {
                    'avg_cpu_percent': avg_cpu,
                    'max_cpu_percent': max_cpu,
                    'avg_memory_mb': avg_memory,
                    'max_memory_mb': max_memory,
                    'memory_increase_mb': max_memory - baseline_memory,
                    'execution_time': end_time - start_time,
                    'successful_requests': sum(1 for r in results if not isinstance(r, Exception))
                }
                
                print(f"  平均CPU: {avg_cpu:.2f}%")
                print(f"  最大CPU: {max_cpu:.2f}%")
                print(f"  平均内存: {avg_memory:.2f}MB")
                print(f"  最大内存: {max_memory:.2f}MB")
                print(f"  内存增长: {max_memory - baseline_memory:.2f}MB")
                
                # 验证资源使用合理
                assert max_cpu < 90, f"CPU使用率过高: {max_cpu:.2f}%"
                assert max_memory - baseline_memory < 500, f"内存增长过多: {max_memory - baseline_memory:.2f}MB"
        
        await service.cleanup()
        return resource_metrics


if __name__ == "__main__":
    # 运行性能测试
    pytest.main([__file__, "-v", "-s"]) 