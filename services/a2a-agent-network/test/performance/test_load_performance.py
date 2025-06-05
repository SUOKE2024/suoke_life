#!/usr/bin/env python3
"""
负载性能测试
Load Performance Tests
"""

import asyncio
import statistics
import sys
import time
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from internal.model.agent import AgentInfo, AgentStatus
from internal.model.workflow import WorkflowDefinition, WorkflowStep
from internal.service.agent_manager import AgentManager
from internal.service.workflow_engine import WorkflowEngine


class TestLoadPerformance:
    """负载性能测试类"""

    @pytest.fixture
    def config(self):
        """测试配置"""
        return {
            "agents": {
                "xiaoai": {
                    "name": "小艾智能体",
                    "url": "http://localhost:5001",
                    "timeout": 30,
                    "retry_count": 3,
                    "health_check_interval": 60,
                    "capabilities": ["diagnosis", "consultation"],
                },
                "xiaoke": {
                    "name": "小克智能体",
                    "url": "http://localhost:5002",
                    "timeout": 30,
                    "retry_count": 3,
                    "health_check_interval": 60,
                    "capabilities": ["resource_management", "customization"],
                },
                "laoke": {
                    "name": "老克智能体",
                    "url": "http://localhost:5003",
                    "timeout": 30,
                    "retry_count": 3,
                    "health_check_interval": 60,
                    "capabilities": ["elderly_care", "monitoring"],
                },
                "soer": {
                    "name": "索儿智能体",
                    "url": "http://localhost:5004",
                    "timeout": 30,
                    "retry_count": 3,
                    "health_check_interval": 60,
                    "capabilities": ["child_care", "education"],
                },
            }
        }

    @pytest.fixture
    async def agent_manager(self, config):
        """创建智能体管理器实例"""
        manager = AgentManager(config)
        await manager.start()
        
        # 设置所有智能体为在线状态
        for agent_id in manager.agents:
            manager.agents[agent_id].status = AgentStatus.ONLINE
            
        yield manager
        await manager.stop()

    @pytest.fixture
    def workflow_engine(self, agent_manager):
        """创建工作流引擎实例"""
        return WorkflowEngine(agent_manager)

    @pytest.fixture
    def simple_workflow(self):
        """简单工作流定义"""
        steps = [
            WorkflowStep(
                id="step1",
                name="处理请求",
                agent="xiaoai",
                action="process_request",
                description="处理用户请求",
                timeout=10,
                retry_count=1,
                parameters={"type": "simple"},
                dependencies=[],
            )
        ]

        return WorkflowDefinition(
            id="simple_workflow",
            name="简单工作流",
            description="用于性能测试的简单工作流",
            version="1.0.0",
            timeout=30,
            retry_count=1,
            steps=steps,
            metadata={"category": "performance"},
            tags=["performance", "test"],
        )

    @pytest.fixture
    def complex_workflow(self):
        """复杂工作流定义"""
        steps = [
            WorkflowStep(
                id="step1",
                name="初始处理",
                agent="xiaoai",
                action="initial_process",
                description="初始处理",
                timeout=10,
                retry_count=1,
                parameters={"type": "initial"},
                dependencies=[],
            ),
            WorkflowStep(
                id="step2",
                name="数据分析",
                agent="xiaoke",
                action="analyze_data",
                description="数据分析",
                timeout=15,
                retry_count=1,
                parameters={"type": "analysis"},
                dependencies=["step1"],
            ),
            WorkflowStep(
                id="step3",
                name="资源调度",
                agent="laoke",
                action="schedule_resources",
                description="资源调度",
                timeout=10,
                retry_count=1,
                parameters={"type": "scheduling"},
                dependencies=["step2"],
            ),
            WorkflowStep(
                id="step4",
                name="结果处理",
                agent="soer",
                action="process_result",
                description="结果处理",
                timeout=10,
                retry_count=1,
                parameters={"type": "result"},
                dependencies=["step3"],
            ),
        ]

        return WorkflowDefinition(
            id="complex_workflow",
            name="复杂工作流",
            description="用于性能测试的复杂工作流",
            version="1.0.0",
            timeout=60,
            retry_count=1,
            steps=steps,
            metadata={"category": "performance"},
            tags=["performance", "test", "complex"],
        )

    async def mock_fast_agent_response(self, request):
        """快速智能体响应模拟"""
        from internal.model.agent import AgentResponse
        
        # 模拟快速处理（10ms）
        await asyncio.sleep(0.01)
        
        return AgentResponse(
            success=True,
            data={"result": f"success_{request.request_id}"},
            error=None,
            agent_id=request.agent_id,
            request_id=request.request_id,
            execution_time=0.01,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

    async def mock_slow_agent_response(self, request):
        """慢速智能体响应模拟"""
        from internal.model.agent import AgentResponse
        
        # 模拟慢速处理（100ms）
        await asyncio.sleep(0.1)
        
        return AgentResponse(
            success=True,
            data={"result": f"success_{request.request_id}"},
            error=None,
            agent_id=request.agent_id,
            request_id=request.request_id,
            execution_time=0.1,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_concurrent_agent_requests(self, agent_manager):
        """测试并发智能体请求性能"""
        with patch.object(agent_manager, "send_request", side_effect=self.mock_fast_agent_response):
            # 测试不同并发级别
            concurrency_levels = [10, 50, 100, 200]
            results = {}

            for concurrency in concurrency_levels:
                start_time = time.time()
                
                # 创建并发请求
                from internal.model.agent import AgentRequest
                tasks = []
                for i in range(concurrency):
                    request = AgentRequest(
                        agent_id="xiaoai",
                        action="test_action",
                        parameters={"test": f"data_{i}"},
                        request_id=f"req_{i}",
                        user_id=f"user_{i}",
                        timeout=30,
                    )
                    tasks.append(agent_manager.send_request(request))

                # 执行并发请求
                responses = await asyncio.gather(*tasks)
                
                end_time = time.time()
                duration = end_time - start_time
                
                # 计算性能指标
                successful_requests = sum(1 for r in responses if r.success)
                requests_per_second = concurrency / duration
                
                results[concurrency] = {
                    "duration": duration,
                    "successful_requests": successful_requests,
                    "requests_per_second": requests_per_second,
                    "success_rate": successful_requests / concurrency * 100,
                }

                print(f"并发级别 {concurrency}: {requests_per_second:.2f} req/s, "
                      f"成功率 {results[concurrency]['success_rate']:.1f}%")

            # 验证性能要求
            assert results[10]["requests_per_second"] > 100  # 低并发应该 > 100 req/s
            assert results[50]["requests_per_second"] > 50   # 中并发应该 > 50 req/s
            assert all(r["success_rate"] == 100.0 for r in results.values())  # 100% 成功率

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_workflow_execution_performance(
        self, agent_manager, workflow_engine, simple_workflow
    ):
        """测试工作流执行性能"""
        with patch.object(agent_manager, "send_request", side_effect=self.mock_fast_agent_response):
            workflow_engine.register_workflow(simple_workflow)
            
            # 测试不同批次大小
            batch_sizes = [10, 25, 50, 100]
            results = {}

            for batch_size in batch_sizes:
                start_time = time.time()
                
                # 创建并发工作流执行
                tasks = []
                for i in range(batch_size):
                    task = workflow_engine.execute_workflow(
                        workflow_id="simple_workflow",
                        parameters={"user_id": f"user_{i}", "data": f"test_{i}"},
                        user_id=f"user_{i}",
                    )
                    tasks.append(task)

                # 执行并发工作流
                executions = await asyncio.gather(*tasks)
                
                # 等待所有工作流完成
                await asyncio.sleep(1)
                
                end_time = time.time()
                duration = end_time - start_time
                
                # 计算性能指标
                workflows_per_second = batch_size / duration
                
                results[batch_size] = {
                    "duration": duration,
                    "workflows_per_second": workflows_per_second,
                }

                print(f"批次大小 {batch_size}: {workflows_per_second:.2f} workflows/s")

            # 验证性能要求
            assert results[10]["workflows_per_second"] > 9    # 应该 > 9 workflows/s
            assert results[25]["workflows_per_second"] > 5    # 应该 > 5 workflows/s

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_complex_workflow_performance(
        self, agent_manager, workflow_engine, complex_workflow
    ):
        """测试复杂工作流性能"""
        with patch.object(agent_manager, "send_request", side_effect=self.mock_fast_agent_response):
            workflow_engine.register_workflow(complex_workflow)
            
            # 测试复杂工作流执行时间
            execution_times = []
            num_tests = 20

            for i in range(num_tests):
                start_time = time.time()
                
                execution = await workflow_engine.execute_workflow(
                    workflow_id="complex_workflow",
                    parameters={"user_id": f"user_{i}", "data": f"test_{i}"},
                    user_id=f"user_{i}",
                )
                
                # 等待工作流完成
                await asyncio.sleep(2)
                
                end_time = time.time()
                execution_time = end_time - start_time
                execution_times.append(execution_time)

            # 计算统计指标
            avg_time = statistics.mean(execution_times)
            median_time = statistics.median(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)
            std_dev = statistics.stdev(execution_times)

            print(f"复杂工作流性能统计:")
            print(f"  平均时间: {avg_time:.3f}s")
            print(f"  中位数时间: {median_time:.3f}s")
            print(f"  最小时间: {min_time:.3f}s")
            print(f"  最大时间: {max_time:.3f}s")
            print(f"  标准差: {std_dev:.3f}s")

            # 验证性能要求
            assert avg_time < 5.0      # 平均执行时间应该 < 5s
            assert max_time < 10.0     # 最大执行时间应该 < 10s
            assert std_dev < 2.0       # 标准差应该 < 2s（稳定性）

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_memory_usage_under_load(self, agent_manager, workflow_engine, simple_workflow):
        """测试负载下的内存使用"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        with patch.object(agent_manager, "send_request", side_effect=self.mock_fast_agent_response):
            workflow_engine.register_workflow(simple_workflow)
            
            # 执行大量工作流
            num_workflows = 500
            batch_size = 50
            
            for batch in range(0, num_workflows, batch_size):
                tasks = []
                for i in range(batch, min(batch + batch_size, num_workflows)):
                    task = workflow_engine.execute_workflow(
                        workflow_id="simple_workflow",
                        parameters={"user_id": f"user_{i}", "data": f"test_{i}"},
                        user_id=f"user_{i}",
                    )
                    tasks.append(task)

                await asyncio.gather(*tasks)
                await asyncio.sleep(0.1)  # 短暂等待

            # 等待所有工作流完成
            await asyncio.sleep(2)
            
            # 检查内存使用
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory

            print(f"内存使用情况:")
            print(f"  初始内存: {initial_memory:.2f} MB")
            print(f"  最终内存: {final_memory:.2f} MB")
            print(f"  内存增长: {memory_increase:.2f} MB")

            # 验证内存使用合理
            assert memory_increase < 100  # 内存增长应该 < 100MB
            assert final_memory < 500     # 总内存使用应该 < 500MB

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_response_time_distribution(self, agent_manager):
        """测试响应时间分布"""
        response_times = []
        num_requests = 100

        with patch.object(agent_manager, "send_request", side_effect=self.mock_fast_agent_response):
            for i in range(num_requests):
                start_time = time.time()
                
                from internal.model.agent import AgentRequest
                request = AgentRequest(
                    agent_id="xiaoai",
                    action="test_action",
                    parameters={"test": f"data_{i}"},
                    request_id=f"req_{i}",
                    user_id=f"user_{i}",
                    timeout=30,
                )
                
                response = await agent_manager.send_request(request)
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # ms
                response_times.append(response_time)

        # 计算百分位数
        response_times.sort()
        p50 = response_times[int(len(response_times) * 0.5)]
        p90 = response_times[int(len(response_times) * 0.9)]
        p95 = response_times[int(len(response_times) * 0.95)]
        p99 = response_times[int(len(response_times) * 0.99)]

        print(f"响应时间分布:")
        print(f"  P50: {p50:.2f} ms")
        print(f"  P90: {p90:.2f} ms")
        print(f"  P95: {p95:.2f} ms")
        print(f"  P99: {p99:.2f} ms")

        # 验证响应时间要求
        assert p50 < 50   # P50 应该 < 50ms
        assert p90 < 100  # P90 应该 < 100ms
        assert p95 < 150  # P95 应该 < 150ms
        assert p99 < 200  # P99 应该 < 200ms

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_throughput_under_different_loads(self, agent_manager):
        """测试不同负载下的吞吐量"""
        loads = [
            {"concurrency": 10, "duration": 5},
            {"concurrency": 50, "duration": 5},
            {"concurrency": 100, "duration": 5},
        ]

        with patch.object(agent_manager, "send_request", side_effect=self.mock_fast_agent_response):
            for load in loads:
                concurrency = load["concurrency"]
                duration = load["duration"]
                
                start_time = time.time()
                end_time = start_time + duration
                completed_requests = 0

                async def worker():
                    nonlocal completed_requests
                    request_id = 0
                    
                    while time.time() < end_time:
                        from internal.model.agent import AgentRequest
                        request = AgentRequest(
                            agent_id="xiaoai",
                            action="test_action",
                            parameters={"test": f"data_{request_id}"},
                            request_id=f"req_{request_id}",
                            user_id=f"user_{request_id}",
                            timeout=30,
                        )
                        
                        await agent_manager.send_request(request)
                        completed_requests += 1
                        request_id += 1

                # 启动工作协程
                workers = [worker() for _ in range(concurrency)]
                await asyncio.gather(*workers)

                actual_duration = time.time() - start_time
                throughput = completed_requests / actual_duration

                print(f"负载测试 - 并发: {concurrency}, 持续: {duration}s")
                print(f"  完成请求: {completed_requests}")
                print(f"  实际持续: {actual_duration:.2f}s")
                print(f"  吞吐量: {throughput:.2f} req/s")

                # 验证吞吐量要求
                if concurrency == 10:
                    assert throughput > 100  # 低并发应该 > 100 req/s
                elif concurrency == 50:
                    assert throughput > 200  # 中并发应该 > 200 req/s 