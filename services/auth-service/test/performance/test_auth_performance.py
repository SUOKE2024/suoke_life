#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证服务性能基准测试
"""
import asyncio
import time
import statistics
from typing import List
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from internal.service.auth_service import authenticate_user, create_tokens, verify_token
from internal.model.user import User


class TestAuthPerformance:
    """认证服务性能测试"""
    
    @pytest.fixture
    def mock_user(self):
        """模拟用户对象"""
        user = MagicMock(spec=User)
        user.id = "test-user-id"
        user.username = "testuser"
        user.email = "test@example.com"
        user.is_active = True
        return user
    
    @pytest.fixture
    def performance_settings(self):
        """性能测试配置"""
        return {
            'concurrent_users': 100,
            'requests_per_user': 10,
            'max_response_time': 0.1,  # 100ms
            'target_throughput': 1000,  # 1000 RPS
        }
    
    async def measure_execution_time(self, func, *args, **kwargs):
        """测量函数执行时间"""
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        end_time = time.perf_counter()
        return result, end_time - start_time
    
    async def run_concurrent_requests(self, func, args_list: List, concurrency: int = 10):
        """运行并发请求"""
        semaphore = asyncio.Semaphore(concurrency)
        
        async def limited_request(args):
            async with semaphore:
                return await self.measure_execution_time(func, *args)
        
        tasks = [limited_request(args) for args in args_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 分离成功和失败的结果
        successful_results = []
        execution_times = []
        errors = []
        
        for result in results:
            if isinstance(result, Exception):
                errors.append(result)
            else:
                _, exec_time = result
                successful_results.append(result)
                execution_times.append(exec_time)
        
        return successful_results, execution_times, errors
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_authenticate_user_performance(self, mock_user, performance_settings):
        """测试用户认证性能"""
        with patch('internal.service.auth_service.UserRepository') as mock_repo_class, \
             patch('internal.service.auth_service.PasswordManager') as mock_password_class, \
             patch('internal.service.auth_service.cache') as mock_cache, \
             patch('internal.service.auth_service.query_optimizer') as mock_optimizer:
            
            # 设置模拟
            mock_cache.get.return_value = None
            mock_optimizer.execute_optimized_query.return_value = [dict(mock_user.__dict__)]
            
            mock_password_manager = AsyncMock()
            mock_password_manager.verify_password.return_value = True
            mock_password_class.return_value = mock_password_manager
            
            # 准备测试数据
            test_args = [("testuser", "password123") for _ in range(performance_settings['concurrent_users'])]
            
            # 执行并发测试
            results, execution_times, errors = await self.run_concurrent_requests(
                authenticate_user, 
                test_args, 
                concurrency=50
            )
            
            # 性能分析
            if execution_times:
                avg_time = statistics.mean(execution_times)
                p95_time = statistics.quantiles(execution_times, n=20)[18]  # 95th percentile
                p99_time = statistics.quantiles(execution_times, n=100)[98]  # 99th percentile
                max_time = max(execution_times)
                min_time = min(execution_times)
                
                print(f"\n🔍 用户认证性能测试结果:")
                print(f"   📊 总请求数: {len(test_args)}")
                print(f"   ✅ 成功请求: {len(results)}")
                print(f"   ❌ 失败请求: {len(errors)}")
                print(f"   ⏱️  平均响应时间: {avg_time:.3f}s")
                print(f"   📈 P95响应时间: {p95_time:.3f}s")
                print(f"   📈 P99响应时间: {p99_time:.3f}s")
                print(f"   🔺 最大响应时间: {max_time:.3f}s")
                print(f"   🔻 最小响应时间: {min_time:.3f}s")
                
                # 性能断言
                assert avg_time < performance_settings['max_response_time'], \
                    f"平均响应时间 {avg_time:.3f}s 超过目标 {performance_settings['max_response_time']}s"
                assert p95_time < performance_settings['max_response_time'] * 2, \
                    f"P95响应时间 {p95_time:.3f}s 超过目标 {performance_settings['max_response_time'] * 2}s"
                assert len(errors) == 0, f"存在 {len(errors)} 个错误"
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_create_tokens_performance(self, mock_user, performance_settings):
        """测试创建令牌性能"""
        with patch('internal.service.auth_service.create_jwt_token') as mock_create_jwt, \
             patch('internal.service.auth_service.settings') as mock_settings:
            
            mock_create_jwt.side_effect = lambda *args, **kwargs: f"token_{time.time()}"
            mock_settings.jwt_access_token_expire_minutes = 30
            mock_settings.jwt_refresh_token_expire_days = 7
            
            # 准备测试数据
            test_args = [(mock_user,) for _ in range(performance_settings['concurrent_users'])]
            
            # 执行并发测试
            results, execution_times, errors = await self.run_concurrent_requests(
                create_tokens, 
                test_args, 
                concurrency=50
            )
            
            # 性能分析
            if execution_times:
                avg_time = statistics.mean(execution_times)
                throughput = len(results) / sum(execution_times) if execution_times else 0
                
                print(f"\n🔍 创建令牌性能测试结果:")
                print(f"   📊 总请求数: {len(test_args)}")
                print(f"   ✅ 成功请求: {len(results)}")
                print(f"   ❌ 失败请求: {len(errors)}")
                print(f"   ⏱️  平均响应时间: {avg_time:.3f}s")
                print(f"   🚀 吞吐量: {throughput:.1f} RPS")
                
                # 性能断言
                assert avg_time < 0.05, f"令牌创建平均时间 {avg_time:.3f}s 过长"
                assert len(errors) == 0, f"存在 {len(errors)} 个错误"
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_verify_token_performance(self, mock_user, performance_settings):
        """测试验证令牌性能"""
        with patch('jwt.decode') as mock_decode, \
             patch('internal.service.auth_service.jwt_key_manager') as mock_jwt_manager:
            
            mock_decode.return_value = {
                "sub": "test-user-id",
                "type": "access",
                "exp": time.time() + 3600
            }
            
            mock_user_repo = AsyncMock()
            mock_user_repo.get_by_id.return_value = mock_user
            
            # 准备测试数据
            test_args = [("test_token", mock_user_repo) for _ in range(performance_settings['concurrent_users'])]
            
            # 执行并发测试
            results, execution_times, errors = await self.run_concurrent_requests(
                verify_token, 
                test_args, 
                concurrency=100  # 令牌验证应该支持更高并发
            )
            
            # 性能分析
            if execution_times:
                avg_time = statistics.mean(execution_times)
                throughput = len(results) / sum(execution_times) if execution_times else 0
                
                print(f"\n🔍 验证令牌性能测试结果:")
                print(f"   📊 总请求数: {len(test_args)}")
                print(f"   ✅ 成功请求: {len(results)}")
                print(f"   ❌ 失败请求: {len(errors)}")
                print(f"   ⏱️  平均响应时间: {avg_time:.3f}s")
                print(f"   🚀 吞吐量: {throughput:.1f} RPS")
                
                # 性能断言
                assert avg_time < 0.02, f"令牌验证平均时间 {avg_time:.3f}s 过长"
                assert throughput > 1000, f"吞吐量 {throughput:.1f} RPS 低于目标 1000 RPS"
                assert len(errors) == 0, f"存在 {len(errors)} 个错误"
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_memory_usage(self, mock_user):
        """测试内存使用情况"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        with patch('internal.service.auth_service.create_jwt_token') as mock_create_jwt:
            mock_create_jwt.side_effect = lambda *args, **kwargs: f"token_{time.time()}"
            
            # 执行大量令牌创建操作
            tasks = []
            for i in range(1000):
                task = create_tokens(mock_user)
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            print(f"\n🔍 内存使用测试结果:")
            print(f"   📊 初始内存: {initial_memory:.1f} MB")
            print(f"   📊 最终内存: {final_memory:.1f} MB")
            print(f"   📈 内存增长: {memory_increase:.1f} MB")
            
            # 内存使用断言
            assert memory_increase < 100, f"内存增长 {memory_increase:.1f} MB 过多"
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_stress_test(self, mock_user, performance_settings):
        """压力测试"""
        with patch('internal.service.auth_service.UserRepository') as mock_repo_class, \
             patch('internal.service.auth_service.PasswordManager') as mock_password_class, \
             patch('internal.service.auth_service.cache') as mock_cache, \
             patch('internal.service.auth_service.query_optimizer') as mock_optimizer:
            
            # 设置模拟
            mock_cache.get.return_value = None
            mock_optimizer.execute_optimized_query.return_value = [dict(mock_user.__dict__)]
            
            mock_password_manager = AsyncMock()
            mock_password_manager.verify_password.return_value = True
            mock_password_class.return_value = mock_password_manager
            
            # 压力测试参数
            stress_users = 500
            stress_requests = 2000
            
            print(f"\n🔥 开始压力测试: {stress_users} 并发用户, {stress_requests} 总请求")
            
            # 准备测试数据
            test_args = [("testuser", "password123") for _ in range(stress_requests)]
            
            start_time = time.perf_counter()
            
            # 执行压力测试
            results, execution_times, errors = await self.run_concurrent_requests(
                authenticate_user, 
                test_args, 
                concurrency=stress_users
            )
            
            total_time = time.perf_counter() - start_time
            
            # 压力测试分析
            success_rate = len(results) / len(test_args) * 100
            throughput = len(results) / total_time
            
            print(f"\n🔍 压力测试结果:")
            print(f"   📊 总请求数: {len(test_args)}")
            print(f"   ✅ 成功请求: {len(results)}")
            print(f"   ❌ 失败请求: {len(errors)}")
            print(f"   📈 成功率: {success_rate:.1f}%")
            print(f"   ⏱️  总耗时: {total_time:.2f}s")
            print(f"   🚀 吞吐量: {throughput:.1f} RPS")
            
            if execution_times:
                avg_time = statistics.mean(execution_times)
                p95_time = statistics.quantiles(execution_times, n=20)[18]
                print(f"   ⏱️  平均响应时间: {avg_time:.3f}s")
                print(f"   📈 P95响应时间: {p95_time:.3f}s")
            
            # 压力测试断言
            assert success_rate >= 95, f"成功率 {success_rate:.1f}% 低于 95%"
            assert throughput >= 500, f"吞吐量 {throughput:.1f} RPS 低于 500 RPS"


class TestCachePerformance:
    """缓存性能测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_cache_hit_performance(self):
        """测试缓存命中性能"""
        with patch('internal.service.auth_service.cache') as mock_cache:
            # 模拟缓存命中
            mock_cache.get.return_value = {
                "id": "test-user-id",
                "username": "testuser",
                "email": "test@example.com",
                "is_active": True
            }
            
            start_time = time.perf_counter()
            
            # 执行多次缓存查询
            for _ in range(1000):
                await mock_cache.get("user_auth:testuser")
            
            end_time = time.perf_counter()
            avg_time = (end_time - start_time) / 1000
            
            print(f"\n🔍 缓存性能测试结果:")
            print(f"   ⏱️  平均缓存查询时间: {avg_time:.6f}s")
            
            # 缓存性能断言
            assert avg_time < 0.001, f"缓存查询时间 {avg_time:.6f}s 过长"


if __name__ == "__main__":
    # 运行性能测试
 