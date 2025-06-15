"""
性能测试与基准测试

提供全面的性能测试工具，包括压力测试、负载测试和性能基准测试。
"""
import asyncio
import aiohttp
import time
import statistics
import logging
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import random
import string

from internal.config.settings import get_settings
from internal.database.connection_manager import get_connection_manager
from internal.cache.redis_cache import get_redis_cache
from internal.async_tasks.task_manager import get_task_manager

logger = logging.getLogger(__name__)
settings = get_settings()


class TestType(Enum):
    """测试类型"""
    LOAD_TEST = "load_test"           # 负载测试
    STRESS_TEST = "stress_test"       # 压力测试
    SPIKE_TEST = "spike_test"         # 峰值测试
    VOLUME_TEST = "volume_test"       # 容量测试
    ENDURANCE_TEST = "endurance_test" # 耐久性测试


class TestStatus(Enum):
    """测试状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TestConfig:
    """测试配置"""
    test_type: TestType
    name: str
    description: str = ""
    
    # 并发配置
    concurrent_users: int = 10
    ramp_up_time: int = 60      # 爬坡时间（秒）
    test_duration: int = 300    # 测试持续时间（秒）
    ramp_down_time: int = 30    # 下降时间（秒）
    
    # 请求配置
    base_url: str = "http://localhost:8000"
    endpoints: List[Dict[str, Any]] = field(default_factory=list)
    request_timeout: float = 30.0
    think_time: Tuple[float, float] = (1.0, 3.0)  # 思考时间范围
    
    # 数据配置
    test_data: Dict[str, Any] = field(default_factory=dict)
    use_random_data: bool = True
    
    # 阈值配置
    max_response_time: float = 2.0      # 最大响应时间（秒）
    max_error_rate: float = 5.0         # 最大错误率（%）
    min_throughput: float = 100.0       # 最小吞吐量（请求/秒）


@dataclass
class RequestResult:
    """请求结果"""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    request_size: int
    response_size: int
    timestamp: datetime
    error: Optional[str] = None
    
    @property
    def is_success(self) -> bool:
        """是否成功"""
        return 200 <= self.status_code < 400 and self.error is None


@dataclass
class TestMetrics:
    """测试指标"""
    test_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # 请求统计
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # 响应时间统计
    response_times: List[float] = field(default_factory=list)
    min_response_time: float = 0.0
    max_response_time: float = 0.0
    avg_response_time: float = 0.0
    p50_response_time: float = 0.0
    p90_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    
    # 吞吐量统计
    requests_per_second: float = 0.0
    peak_rps: float = 0.0
    
    # 错误统计
    error_rate: float = 0.0
    errors_by_type: Dict[str, int] = field(default_factory=dict)
    
    # 资源使用统计
    cpu_usage: List[float] = field(default_factory=list)
    memory_usage: List[float] = field(default_factory=list)
    
    def calculate_statistics(self):
        """计算统计信息"""
        if not self.response_times:
            return
        
        self.min_response_time = min(self.response_times)
        self.max_response_time = max(self.response_times)
        self.avg_response_time = statistics.mean(self.response_times)
        
        sorted_times = sorted(self.response_times)
        self.p50_response_time = statistics.median(sorted_times)
        self.p90_response_time = self._percentile(sorted_times, 90)
        self.p95_response_time = self._percentile(sorted_times, 95)
        self.p99_response_time = self._percentile(sorted_times, 99)
        
        if self.end_time and self.start_time:
            duration = (self.end_time - self.start_time).total_seconds()
            self.requests_per_second = self.total_requests / duration if duration > 0 else 0
        
        self.error_rate = (self.failed_requests / self.total_requests * 100) if self.total_requests > 0 else 0
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not data:
            return 0.0
        
        k = (len(data) - 1) * percentile / 100
        f = int(k)
        c = k - f
        
        if f + 1 < len(data):
            return data[f] * (1 - c) + data[f + 1] * c
        else:
            return data[f]


class PerformanceTest:
    """性能测试器"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.test_id = str(uuid.uuid4())
        self.status = TestStatus.PENDING
        self.metrics = TestMetrics(test_id=self.test_id, start_time=datetime.utcnow())
        
        self.session: Optional[aiohttp.ClientSession] = None
        self.workers: List[asyncio.Task] = []
        self.is_running = False
        self.should_stop = False
        
        # 监控任务
        self.monitor_task: Optional[asyncio.Task] = None
        
        # 结果收集
        self.results: List[RequestResult] = []
        self.results_lock = asyncio.Lock()
    
    async def start(self) -> str:
        """开始测试"""
        if self.is_running:
            raise ValueError("测试已在运行中")
        
        try:
            self.status = TestStatus.RUNNING
            self.is_running = True
            self.metrics.start_time = datetime.utcnow()
            
            logger.info(f"开始性能测试: {self.config.name} ({self.test_id})")
            
            # 创建HTTP会话
            timeout = aiohttp.ClientTimeout(total=self.config.request_timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            # 启动监控任务
            self.monitor_task = asyncio.create_task(self._monitor_resources())
            
            # 执行测试
            await self._execute_test()
            
            # 完成测试
            await self._finish_test()
            
            return self.test_id
            
        except Exception as e:
            self.status = TestStatus.FAILED
            logger.error(f"性能测试失败: {str(e)}")
            raise
        finally:
            await self._cleanup()
    
    async def stop(self):
        """停止测试"""
        self.should_stop = True
        logger.info(f"停止性能测试: {self.test_id}")
    
    async def _execute_test(self):
        """执行测试"""
        if self.config.test_type == TestType.LOAD_TEST:
            await self._run_load_test()
        elif self.config.test_type == TestType.STRESS_TEST:
            await self._run_stress_test()
        elif self.config.test_type == TestType.SPIKE_TEST:
            await self._run_spike_test()
        elif self.config.test_type == TestType.VOLUME_TEST:
            await self._run_volume_test()
        elif self.config.test_type == TestType.ENDURANCE_TEST:
            await self._run_endurance_test()
        else:
            raise ValueError(f"不支持的测试类型: {self.config.test_type}")
    
    async def _run_load_test(self):
        """运行负载测试"""
        logger.info(f"运行负载测试: {self.config.concurrent_users} 并发用户")
        
        # 爬坡阶段
        await self._ramp_up()
        
        # 稳定负载阶段
        await self._steady_load()
        
        # 下降阶段
        await self._ramp_down()
    
    async def _run_stress_test(self):
        """运行压力测试"""
        logger.info("运行压力测试: 逐步增加负载直到系统崩溃")
        
        current_users = 1
        max_users = self.config.concurrent_users * 2
        step_duration = 60  # 每步持续60秒
        
        while current_users <= max_users and not self.should_stop:
            logger.info(f"压力测试阶段: {current_users} 并发用户")
            
            # 启动当前阶段的工作器
            await self._start_workers(current_users, step_duration)
            
            # 检查系统是否还能正常响应
            if self._is_system_overloaded():
                logger.warning(f"系统过载，停止在 {current_users} 并发用户")
                break
            
            current_users += max(1, current_users // 4)  # 每次增加25%
    
    async def _run_spike_test(self):
        """运行峰值测试"""
        logger.info("运行峰值测试: 突然增加负载")
        
        # 正常负载
        normal_users = max(1, self.config.concurrent_users // 4)
        await self._start_workers(normal_users, 60)
        
        # 突然峰值
        spike_users = self.config.concurrent_users
        await self._start_workers(spike_users, 120)
        
        # 回到正常负载
        await self._start_workers(normal_users, 60)
    
    async def _run_volume_test(self):
        """运行容量测试"""
        logger.info("运行容量测试: 大量数据处理")
        
        # 生成大量测试数据
        await self._generate_volume_data()
        
        # 执行标准负载测试
        await self._run_load_test()
    
    async def _run_endurance_test(self):
        """运行耐久性测试"""
        logger.info(f"运行耐久性测试: {self.config.test_duration} 秒持续负载")
        
        # 长时间稳定负载
        await self._start_workers(self.config.concurrent_users, self.config.test_duration)
    
    async def _ramp_up(self):
        """爬坡阶段"""
        if self.config.ramp_up_time <= 0:
            await self._start_workers(self.config.concurrent_users, 0)
            return
        
        logger.info(f"爬坡阶段: {self.config.ramp_up_time} 秒内达到 {self.config.concurrent_users} 用户")
        
        step_duration = 5  # 每5秒增加一批用户
        steps = self.config.ramp_up_time // step_duration
        users_per_step = max(1, self.config.concurrent_users // steps)
        
        current_users = 0
        for step in range(steps):
            if self.should_stop:
                break
            
            current_users = min(current_users + users_per_step, self.config.concurrent_users)
            await self._start_workers(current_users, step_duration)
    
    async def _steady_load(self):
        """稳定负载阶段"""
        logger.info(f"稳定负载阶段: {self.config.test_duration} 秒")
        await self._start_workers(self.config.concurrent_users, self.config.test_duration)
    
    async def _ramp_down(self):
        """下降阶段"""
        if self.config.ramp_down_time <= 0:
            return
        
        logger.info(f"下降阶段: {self.config.ramp_down_time} 秒")
        
        # 逐步停止工作器
        step_duration = 5
        steps = self.config.ramp_down_time // step_duration
        users_per_step = max(1, len(self.workers) // steps)
        
        for step in range(steps):
            workers_to_stop = self.workers[:users_per_step]
            for worker in workers_to_stop:
                worker.cancel()
            
            self.workers = self.workers[users_per_step:]
            await asyncio.sleep(step_duration)
    
    async def _start_workers(self, num_workers: int, duration: float):
        """启动工作器"""
        # 停止多余的工作器
        while len(self.workers) > num_workers:
            worker = self.workers.pop()
            worker.cancel()
        
        # 启动新的工作器
        while len(self.workers) < num_workers:
            worker = asyncio.create_task(self._worker())
            self.workers.append(worker)
        
        # 等待指定时间
        if duration > 0:
            await asyncio.sleep(duration)
    
    async def _worker(self):
        """工作器协程"""
        try:
            while not self.should_stop:
                # 选择端点
                endpoint_config = random.choice(self.config.endpoints)
                
                # 执行请求
                result = await self._make_request(endpoint_config)
                
                # 记录结果
                async with self.results_lock:
                    self.results.append(result)
                    self._update_metrics(result)
                
                # 思考时间
                think_time = random.uniform(*self.config.think_time)
                await asyncio.sleep(think_time)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"工作器错误: {str(e)}")
    
    async def _make_request(self, endpoint_config: Dict[str, Any]) -> RequestResult:
        """发起请求"""
        method = endpoint_config.get("method", "GET")
        path = endpoint_config.get("path", "/")
        headers = endpoint_config.get("headers", {})
        data = endpoint_config.get("data")
        
        url = f"{self.config.base_url}{path}"
        start_time = time.time()
        
        try:
            # 准备请求数据
            if data and self.config.use_random_data:
                data = self._generate_random_data(data)
            
            # 发起请求
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data if method in ["POST", "PUT", "PATCH"] else None
            ) as response:
                response_text = await response.text()
                response_time = time.time() - start_time
                
                return RequestResult(
                    endpoint=path,
                    method=method,
                    status_code=response.status,
                    response_time=response_time,
                    request_size=len(json.dumps(data)) if data else 0,
                    response_size=len(response_text),
                    timestamp=datetime.utcnow()
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            return RequestResult(
                endpoint=path,
                method=method,
                status_code=0,
                response_time=response_time,
                request_size=0,
                response_size=0,
                timestamp=datetime.utcnow(),
                error=str(e)
            )
    
    def _generate_random_data(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """生成随机测试数据"""
        result = {}
        
        for key, value in template.items():
            if isinstance(value, str):
                if value == "{{random_string}}":
                    result[key] = ''.join(random.choices(string.ascii_letters, k=10))
                elif value == "{{random_email}}":
                    result[key] = f"test_{random.randint(1000, 9999)}@example.com"
                elif value == "{{random_password}}":
                    result[key] = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
                else:
                    result[key] = value
            elif isinstance(value, int):
                result[key] = random.randint(1, 1000)
            else:
                result[key] = value
        
        return result
    
    def _update_metrics(self, result: RequestResult):
        """更新指标"""
        self.metrics.total_requests += 1
        
        if result.is_success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
            
            # 记录错误类型
            error_type = f"{result.status_code}" if result.status_code > 0 else "network_error"
            self.metrics.errors_by_type[error_type] = self.metrics.errors_by_type.get(error_type, 0) + 1
        
        self.metrics.response_times.append(result.response_time)
        
        # 更新峰值RPS
        current_time = datetime.utcnow()
        recent_requests = [
            r for r in self.results
            if (current_time - r.timestamp).total_seconds() <= 1.0
        ]
        current_rps = len(recent_requests)
        self.metrics.peak_rps = max(self.metrics.peak_rps, current_rps)
    
    async def _monitor_resources(self):
        """监控资源使用"""
        try:
            while self.is_running:
                # 这里可以添加CPU、内存监控
                # 简化版本，只记录时间戳
                await asyncio.sleep(5)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"资源监控失败: {str(e)}")
    
    def _is_system_overloaded(self) -> bool:
        """检查系统是否过载"""
        if not self.results:
            return False
        
        # 检查最近的错误率
        recent_results = self.results[-100:]  # 最近100个请求
        error_count = sum(1 for r in recent_results if not r.is_success)
        error_rate = (error_count / len(recent_results)) * 100
        
        # 检查响应时间
        recent_times = [r.response_time for r in recent_results if r.is_success]
        if recent_times:
            avg_response_time = statistics.mean(recent_times)
            if avg_response_time > self.config.max_response_time * 2:
                return True
        
        return error_rate > self.config.max_error_rate * 2
    
    async def _generate_volume_data(self):
        """生成大量测试数据"""
        # 这里可以预先生成大量测试数据
        logger.info("生成容量测试数据")
        pass
    
    async def _finish_test(self):
        """完成测试"""
        self.metrics.end_time = datetime.utcnow()
        self.metrics.calculate_statistics()
        self.status = TestStatus.COMPLETED
        
        logger.info(f"性能测试完成: {self.test_id}")
        logger.info(f"总请求数: {self.metrics.total_requests}")
        logger.info(f"成功率: {(self.metrics.successful_requests / self.metrics.total_requests * 100):.2f}%")
        logger.info(f"平均响应时间: {self.metrics.avg_response_time:.3f}秒")
        logger.info(f"吞吐量: {self.metrics.requests_per_second:.2f} RPS")
    
    async def _cleanup(self):
        """清理资源"""
        self.is_running = False
        
        # 停止所有工作器
        for worker in self.workers:
            worker.cancel()
        
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)
        
        # 停止监控任务
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        # 关闭HTTP会话
        if self.session:
            await self.session.close()
    
    def get_report(self) -> Dict[str, Any]:
        """获取测试报告"""
        return {
            "test_id": self.test_id,
            "config": {
                "name": self.config.name,
                "type": self.config.test_type.value,
                "concurrent_users": self.config.concurrent_users,
                "test_duration": self.config.test_duration,
                "endpoints": len(self.config.endpoints)
            },
            "status": self.status.value,
            "metrics": {
                "start_time": self.metrics.start_time.isoformat(),
                "end_time": self.metrics.end_time.isoformat() if self.metrics.end_time else None,
                "duration": (self.metrics.end_time - self.metrics.start_time).total_seconds() if self.metrics.end_time else 0,
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "error_rate": self.metrics.error_rate,
                "response_time": {
                    "min": self.metrics.min_response_time,
                    "max": self.metrics.max_response_time,
                    "avg": self.metrics.avg_response_time,
                    "p50": self.metrics.p50_response_time,
                    "p90": self.metrics.p90_response_time,
                    "p95": self.metrics.p95_response_time,
                    "p99": self.metrics.p99_response_time
                },
                "throughput": {
                    "requests_per_second": self.metrics.requests_per_second,
                    "peak_rps": self.metrics.peak_rps
                },
                "errors_by_type": self.metrics.errors_by_type
            },
            "thresholds": {
                "max_response_time": self.config.max_response_time,
                "max_error_rate": self.config.max_error_rate,
                "min_throughput": self.config.min_throughput
            },
            "passed": self._check_thresholds()
        }
    
    def _check_thresholds(self) -> bool:
        """检查是否通过阈值"""
        if self.metrics.avg_response_time > self.config.max_response_time:
            return False
        
        if self.metrics.error_rate > self.config.max_error_rate:
            return False
        
        if self.metrics.requests_per_second < self.config.min_throughput:
            return False
        
        return True


class PerformanceTestSuite:
    """性能测试套件"""
    
    def __init__(self):
        self.tests: Dict[str, PerformanceTest] = {}
        self.test_configs: List[TestConfig] = []
    
    def add_test_config(self, config: TestConfig):
        """添加测试配置"""
        self.test_configs.append(config)
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        results = {}
        
        for config in self.test_configs:
            logger.info(f"运行测试: {config.name}")
            
            test = PerformanceTest(config)
            self.tests[test.test_id] = test
            
            try:
                await test.start()
                results[config.name] = test.get_report()
            except Exception as e:
                logger.error(f"测试失败 {config.name}: {str(e)}")
                results[config.name] = {"error": str(e)}
        
        return results
    
    def get_default_auth_tests(self) -> List[TestConfig]:
        """获取默认的认证服务测试配置"""
        return [
            # 登录负载测试
            TestConfig(
                test_type=TestType.LOAD_TEST,
                name="登录负载测试",
                description="测试登录接口的负载能力",
                concurrent_users=50,
                test_duration=300,
                endpoints=[
                    {
                        "method": "POST",
                        "path": "/auth/login",
                        "data": {
                            "username": "{{random_email}}",
                            "password": "{{random_password}}"
                        }
                    }
                ],
                max_response_time=1.0,
                max_error_rate=5.0,
                min_throughput=100.0
            ),
            
            # 令牌验证压力测试
            TestConfig(
                test_type=TestType.STRESS_TEST,
                name="令牌验证压力测试",
                description="测试令牌验证接口的压力承受能力",
                concurrent_users=100,
                test_duration=180,
                endpoints=[
                    {
                        "method": "GET",
                        "path": "/auth/verify",
                        "headers": {
                            "Authorization": "Bearer test_token"
                        }
                    }
                ],
                max_response_time=0.5,
                max_error_rate=10.0,
                min_throughput=200.0
            ),
            
            # 注册峰值测试
            TestConfig(
                test_type=TestType.SPIKE_TEST,
                name="注册峰值测试",
                description="测试注册接口的峰值处理能力",
                concurrent_users=30,
                test_duration=240,
                endpoints=[
                    {
                        "method": "POST",
                        "path": "/auth/register",
                        "data": {
                            "username": "{{random_string}}",
                            "email": "{{random_email}}",
                            "password": "{{random_password}}"
                        }
                    }
                ],
                max_response_time=2.0,
                max_error_rate=8.0,
                min_throughput=50.0
            )
        ]


# 便捷函数

async def run_quick_load_test(
    base_url: str = "http://localhost:8000",
    concurrent_users: int = 10,
    duration: int = 60
) -> Dict[str, Any]:
    """快速负载测试"""
    config = TestConfig(
        test_type=TestType.LOAD_TEST,
        name="快速负载测试",
        concurrent_users=concurrent_users,
        test_duration=duration,
        base_url=base_url,
        endpoints=[
            {"method": "GET", "path": "/health"},
            {"method": "GET", "path": "/monitoring/health"}
        ]
    )
    
    test = PerformanceTest(config)
    await test.start()
    return test.get_report()


async def benchmark_auth_service() -> Dict[str, Any]:
    """认证服务基准测试"""
    suite = PerformanceTestSuite()
    
    # 添加默认测试
    for config in suite.get_default_auth_tests():
        suite.add_test_config(config)
    
    # 运行所有测试
    results = await suite.run_all_tests()
    
    return {
        "benchmark_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "service": "auth-service",
        "version": "1.0.0",
        "results": results,
        "summary": _generate_benchmark_summary(results)
    }


def _generate_benchmark_summary(results: Dict[str, Any]) -> Dict[str, Any]:
    """生成基准测试总结"""
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r.get("passed", False))
    
    avg_response_time = statistics.mean([
        r.get("metrics", {}).get("response_time", {}).get("avg", 0)
        for r in results.values()
        if "metrics" in r
    ]) if results else 0
    
    total_throughput = sum([
        r.get("metrics", {}).get("throughput", {}).get("requests_per_second", 0)
        for r in results.values()
        if "metrics" in r
    ])
    
    return {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
        "avg_response_time": avg_response_time,
        "total_throughput": total_throughput,
        "performance_grade": _calculate_performance_grade(passed_tests, total_tests, avg_response_time)
    }


def _calculate_performance_grade(passed_tests: int, total_tests: int, avg_response_time: float) -> str:
    """计算性能等级"""
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    if pass_rate >= 95 and avg_response_time <= 0.5:
        return "A+"
    elif pass_rate >= 90 and avg_response_time <= 1.0:
        return "A"
    elif pass_rate >= 80 and avg_response_time <= 2.0:
        return "B"
    elif pass_rate >= 70 and avg_response_time <= 3.0:
        return "C"
    else:
        return "D" 