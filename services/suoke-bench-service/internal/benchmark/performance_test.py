"""
performance_test - 索克生活项目模块
"""

from collections.abc import Callable
from datetime import datetime
from enum import Enum
from typing import Any
import aiohttp
import asyncio
import json
import logging
import os
import random
import statistics
import time
import uuid

"""
性能测试模块 - 提供用于基准测试和性能优化的工具

该模块实现了全面的性能测试框架，用于评估API网关和各微服务的响应时间、
吞吐量和资源利用率，以及识别系统瓶颈。
"""



# 设置日志记录
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class TestPhase(str, Enum):
    """测试阶段枚举"""

    WARMUP = "warmup"  # 预热阶段
    RAMP_UP = "ramp_up"  # 加压阶段
    PEAK = "peak"  # 峰值阶段
    RAMP_DOWN = "ramp_down"  # 减压阶段
    COOLDOWN = "cooldown"  # 冷却阶段

class ServiceType(str, Enum):
    """服务类型枚举"""

    API_GATEWAY = "api_gateway"  # API网关
    USER_SERVICE = "user_service"  # 用户服务
    AUTH_SERVICE = "auth_service"  # 认证服务
    FIVE_DIAGNOSIS = "five_diagnosis"  # 五诊服务
    KNOWLEDGE_SERVICE = "knowledge_service"  # 知识服务
    HEALTH_SERVICE = "health_service"  # 健康服务
    AI_SERVICE = "ai_service"  # AI服务

class RequestResult:
    """请求结果类"""

    def __init__(
        self,
        service_name: str,
        endpoint: str,
        start_time: float,
        end_time: float,
        status_code: int | None = None,
        response_size: int | None = None,
        error: str | None = None,
        request_id: str | None = None,
        phase: TestPhase | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        初始化请求结果

        Args:
            service_name: 服务名称
            endpoint: 接口路径
            start_time: 开始时间（Unix时间戳，秒）
            end_time: 结束时间（Unix时间戳，秒）
            status_code: HTTP状态码
            response_size: 响应大小（字节）
            error: 错误信息
            request_id: 请求ID
            phase: 测试阶段
            metadata: 元数据
        """
        self.service_name = service_name
        self.endpoint = endpoint
        self.start_time = start_time
        self.end_time = end_time
        self.response_time = (end_time - start_time) * 1000  # 毫秒
        self.status_code = status_code
        self.response_size = response_size
        self.error = error
        self.request_id = request_id or str(uuid.uuid4())
        self.phase = phase
        self.metadata = metadata or {}
        self.timestamp = datetime.fromtimestamp(start_time)

    @property
    def is_success(self) -> bool:
        """请求是否成功"""
        return self.error is None and (
            self.status_code is None or 200 <= self.status_code < 400
        )

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "request_id": self.request_id,
            "service_name": self.service_name,
            "endpoint": self.endpoint,
            "timestamp": self.timestamp.isoformat(),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "response_time": self.response_time,
            "status_code": self.status_code,
            "response_size": self.response_size,
            "is_success": self.is_success,
            "error": self.error,
            "phase": self.phase.value if self.phase else None,
            "metadata": self.metadata,
        }

class TestProfile:
    """测试配置文件类"""

    def __init__(
        self,
        name: str,
        description: str,
        target_rps: int,
        duration: int,
        warmup_duration: int = 30,
        ramp_up_duration: int = 60,
        peak_duration: int | None = None,
        ramp_down_duration: int = 60,
        cooldown_duration: int = 30,
        max_concurrent_requests: int | None = None,
        success_threshold: float = 99.0,
        p95_threshold: float = 500.0,
        metadata: dict[str, Any] | None = None,
    ):
        """
        初始化测试配置文件

        Args:
            name: 测试名称
            description: 测试描述
            target_rps: 目标每秒请求数
            duration: 总测试持续时间（秒）
            warmup_duration: 预热阶段持续时间（秒）
            ramp_up_duration: 加压阶段持续时间（秒）
            peak_duration: 峰值阶段持续时间（秒），如果为None则自动计算
            ramp_down_duration: 减压阶段持续时间（秒）
            cooldown_duration: 冷却阶段持续时间（秒）
            max_concurrent_requests: 最大并发请求数
            success_threshold: 成功率阈值（百分比）
            p95_threshold: 95百分位响应时间阈值（毫秒）
            metadata: 元数据
        """
        self.name = name
        self.description = description
        self.target_rps = target_rps
        self.duration = duration
        self.warmup_duration = warmup_duration
        self.ramp_up_duration = ramp_up_duration

        # 如果未指定峰值阶段持续时间，则自动计算
        if peak_duration is None:
            self.peak_duration = max(
                0,
                duration
                - warmup_duration
                - ramp_up_duration
                - ramp_down_duration
                - cooldown_duration,
            )
        else:
            self.peak_duration = peak_duration

        self.ramp_down_duration = ramp_down_duration
        self.cooldown_duration = cooldown_duration

        # 设置最大并发请求数，默认为目标RPS的2倍
        self.max_concurrent_requests = max_concurrent_requests or (target_rps * 2)

        self.success_threshold = success_threshold
        self.p95_threshold = p95_threshold
        self.metadata = metadata or {}

    def get_phase_at_time(self, elapsed_time: float) -> TestPhase:
        """
        根据已过时间确定当前测试阶段

        Args:
            elapsed_time: 已过时间（秒）

        Returns:
            TestPhase: 当前测试阶段
        """
        if elapsed_time < self.warmup_duration:
            return TestPhase.WARMUP

        elapsed_time -= self.warmup_duration

        if elapsed_time < self.ramp_up_duration:
            return TestPhase.RAMP_UP

        elapsed_time -= self.ramp_up_duration

        if elapsed_time < self.peak_duration:
            return TestPhase.PEAK

        elapsed_time -= self.peak_duration

        if elapsed_time < self.ramp_down_duration:
            return TestPhase.RAMP_DOWN

        return TestPhase.COOLDOWN

    def get_target_rps_at_time(self, elapsed_time: float) -> float:
        """
        根据已过时间计算目标RPS

        Args:
            elapsed_time: 已过时间（秒）

        Returns:
            float: 当前目标RPS
        """
        phase = self.get_phase_at_time(elapsed_time)

        if phase == TestPhase.WARMUP:
            # 预热阶段线性增加到目标RPS的50%
            progress = elapsed_time / self.warmup_duration
            return self.target_rps * 0.5 * progress

        if phase == TestPhase.RAMP_UP:
            # 加压阶段线性增加到目标RPS
            progress = (elapsed_time - self.warmup_duration) / self.ramp_up_duration
            return self.target_rps * (0.5 + 0.5 * progress)

        if phase == TestPhase.PEAK:
            # 峰值阶段保持目标RPS
            return self.target_rps

        if phase == TestPhase.RAMP_DOWN:
            # 减压阶段线性减少到目标RPS的25%
            progress = (
                elapsed_time
                - self.warmup_duration
                - self.ramp_up_duration
                - self.peak_duration
            ) / self.ramp_down_duration
            return self.target_rps * (1.0 - 0.75 * progress)

        # 冷却阶段线性减少到0
        progress = (
            elapsed_time
            - self.warmup_duration
            - self.ramp_up_duration
            - self.peak_duration
            - self.ramp_down_duration
        ) / self.cooldown_duration
        return self.target_rps * 0.25 * (1.0 - progress)

class EndpointSpec:
    """接口规格类"""

    def __init__(
        self,
        service_name: str,
        endpoint: str,
        method: str = "GET",
        weight: int = 1,
        request_generator: Callable[[], dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        初始化接口规格

        Args:
            service_name: 服务名称
            endpoint: 接口路径
            method: HTTP方法
            weight: 权重（影响请求分布）
            request_generator: 请求生成器函数
            metadata: 元数据
        """
        self.service_name = service_name
        self.endpoint = endpoint
        self.method = method.upper()
        self.weight = max(1, weight)  # 确保权重至少为1
        self.request_generator = request_generator
        self.metadata = metadata or {}

    def generate_request(self) -> dict[str, Any]:
        """
        生成请求数据

        Returns:
            Dict[str, Any]: 请求数据
        """
        if self.request_generator:
            return self.request_generator()

        # 默认返回空请求数据
        return {}

class TestResult:
    """测试结果类"""

    def __init__(
        self,
        test_id: str,
        test_name: str,
        start_time: datetime,
        end_time: datetime,
        profile: TestProfile,
        results: list[RequestResult],
        metadata: dict[str, Any] | None = None,
    ):
        """
        初始化测试结果

        Args:
            test_id: 测试ID
            test_name: 测试名称
            start_time: 开始时间
            end_time: 结束时间
            profile: 测试配置文件
            results: 请求结果列表
            metadata: 元数据
        """
        self.test_id = test_id
        self.test_name = test_name
        self.start_time = start_time
        self.end_time = end_time
        self.profile = profile
        self.results = results
        self.metadata = metadata or {}

        # 计算测试持续时间（秒）
        self.duration = (end_time - start_time).total_seconds()

        # 分析结果
        self._analyze_results()

    def _analyze_results(self):
        """分析测试结果"""
        # 计算总请求数
        self.total_requests = len(self.results)

        if self.total_requests == 0:
            logger.warning("测试结果为空，无法分析")
            self.successful_requests = 0
            self.failed_requests = 0
            self.success_rate = 0.0
            self.average_response_time = 0.0
            self.p50_response_time = 0.0
            self.p95_response_time = 0.0
            self.p99_response_time = 0.0
            self.min_response_time = 0.0
            self.max_response_time = 0.0
            self.rps = 0.0
            self.peak_rps = 0.0
            return

        # 计算成功和失败请求数
        self.successful_requests = sum(1 for r in self.results if r.is_success)
        self.failed_requests = self.total_requests - self.successful_requests

        # 计算成功率
        self.success_rate = (self.successful_requests / self.total_requests) * 100

        # 提取响应时间
        response_times = [r.response_time for r in self.results if r.is_success]

        if response_times:
            # 计算响应时间统计
            self.average_response_time = statistics.mean(response_times)
            self.p50_response_time = np.percentile(response_times, 50)
            self.p95_response_time = np.percentile(response_times, 95)
            self.p99_response_time = np.percentile(response_times, 99)
            self.min_response_time = min(response_times)
            self.max_response_time = max(response_times)
        else:
            self.average_response_time = 0.0
            self.p50_response_time = 0.0
            self.p95_response_time = 0.0
            self.p99_response_time = 0.0
            self.min_response_time = 0.0
            self.max_response_time = 0.0

        # 计算每秒请求数 (RPS)
        self.rps = self.total_requests / self.duration if self.duration > 0 else 0

        # 计算峰值 RPS
        # 将测试时间划分为1秒的窗口，计算每个窗口的请求数
        if self.results:
            min(r.start_time for r in self.results)
            max(r.end_time for r in self.results)

            # 创建时间窗口
            windows = {}
            for r in self.results:
                # 将请求放入相应的1秒窗口中
                window = int(r.start_time)
                windows[window] = windows.get(window, 0) + 1

            # 计算峰值 RPS
            self.peak_rps = max(windows.values()) if windows else 0
        else:
            self.peak_rps = 0

        # 按服务和端点分组统计
        self.service_stats = {}
        self.endpoint_stats = {}

        for result in self.results:
            # 服务统计
            if result.service_name not in self.service_stats:
                self.service_stats[result.service_name] = {
                    "total": 0,
                    "success": 0,
                    "failure": 0,
                    "response_times": [],
                }

            stats = self.service_stats[result.service_name]
            stats["total"] += 1
            if result.is_success:
                stats["success"] += 1
                stats["response_times"].append(result.response_time)
            else:
                stats["failure"] += 1

            # 端点统计
            endpoint_key = f"{result.service_name}:{result.endpoint}"
            if endpoint_key not in self.endpoint_stats:
                self.endpoint_stats[endpoint_key] = {
                    "service": result.service_name,
                    "endpoint": result.endpoint,
                    "total": 0,
                    "success": 0,
                    "failure": 0,
                    "response_times": [],
                }

            stats = self.endpoint_stats[endpoint_key]
            stats["total"] += 1
            if result.is_success:
                stats["success"] += 1
                stats["response_times"].append(result.response_time)
            else:
                stats["failure"] += 1

        # 计算各服务和端点的统计指标
        for _service, stats in self.service_stats.items():
            if stats["success"] > 0:
                response_times = stats["response_times"]
                stats["avg_response_time"] = statistics.mean(response_times)
                stats["p95_response_time"] = np.percentile(response_times, 95)
                stats["min_response_time"] = min(response_times)
                stats["max_response_time"] = max(response_times)
            else:
                stats["avg_response_time"] = 0
                stats["p95_response_time"] = 0
                stats["min_response_time"] = 0
                stats["max_response_time"] = 0

            stats["success_rate"] = (
                (stats["success"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            )

            # 删除中间计算用的列表
            del stats["response_times"]

        for _endpoint_key, stats in self.endpoint_stats.items():
            if stats["success"] > 0:
                response_times = stats["response_times"]
                stats["avg_response_time"] = statistics.mean(response_times)
                stats["p95_response_time"] = np.percentile(response_times, 95)
                stats["min_response_time"] = min(response_times)
                stats["max_response_time"] = max(response_times)
            else:
                stats["avg_response_time"] = 0
                stats["p95_response_time"] = 0
                stats["min_response_time"] = 0
                stats["max_response_time"] = 0

            stats["success_rate"] = (
                (stats["success"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            )

            # 删除中间计算用的列表
            del stats["response_times"]

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration": self.duration,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.success_rate,
            "average_response_time": self.average_response_time,
            "p50_response_time": self.p50_response_time,
            "p95_response_time": self.p95_response_time,
            "p99_response_time": self.p99_response_time,
            "min_response_time": self.min_response_time,
            "max_response_time": self.max_response_time,
            "rps": self.rps,
            "peak_rps": self.peak_rps,
            "service_stats": self.service_stats,
            "endpoint_stats": self.endpoint_stats,
            "profile": {
                "name": self.profile.name,
                "target_rps": self.profile.target_rps,
                "duration": self.profile.duration,
                "success_threshold": self.profile.success_threshold,
                "p95_threshold": self.profile.p95_threshold,
            },
            "metadata": self.metadata,
        }

    def save_to_file(self, file_path: str):
        """
        保存测试结果到文件

        Args:
            file_path: 文件路径
        """
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

        logger.info(f"测试结果已保存到: {file_path}")

    def save_raw_results(self, file_path: str):
        """
        保存原始请求结果到文件

        Args:
            file_path: 文件路径
        """
        data = [r.to_dict() for r in self.results]
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"原始请求结果已保存到: {file_path}")

    def save_csv(self, file_path: str):
        """
        保存请求结果为CSV文件

        Args:
            file_path: 文件路径
        """
        data = [r.to_dict() for r in self.results]
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)

        logger.info(f"请求结果已保存为CSV: {file_path}")

    def generate_report(self, output_dir: str, include_plots: bool = True):
        """
        生成测试报告

        Args:
            output_dir: 输出目录
            include_plots: 是否包含图表
        """
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        # 保存测试结果
        self.save_to_file(os.path.join(output_dir, "test_result.json"))
        self.save_raw_results(os.path.join(output_dir, "raw_results.json"))
        self.save_csv(os.path.join(output_dir, "results.csv"))

        # 生成图表
        if include_plots and self.results:
            self._generate_plots(output_dir)

        # 生成HTML报告
        self._generate_html_report(output_dir)

        logger.info(f"测试报告已生成到目录: {output_dir}")

    def _generate_plots(self, output_dir: str):
        """
        生成图表

        Args:
            output_dir: 输出目录
        """
        # 准备数据
        df = pd.DataFrame([r.to_dict() for r in self.results])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.sort_values("timestamp", inplace=True)

        # 设置图表风格
        plt.style.use("ggplot")

        # 响应时间分布图
        plt.figure(figsize=(10, 6))
        plt.hist(df[df["is_success"]]["response_time"], bins=50, alpha=0.7)
        plt.title("响应时间分布")
        plt.xlabel("响应时间 (ms)")
        plt.ylabel("请求数")
        plt.grid(True)
        plt.savefig(os.path.join(output_dir, "response_time_histogram.png"), dpi=300)
        plt.close()

        # 响应时间随时间变化图
        plt.figure(figsize=(12, 6))

        # 计算滚动平均值
        df["rolling_avg"] = (
            df[df["is_success"]]["response_time"].rolling(window=50).mean()
        )

        plt.scatter(
            df["timestamp"], df["response_time"], s=5, alpha=0.3, label="每个请求"
        )
        plt.plot(
            df["timestamp"],
            df["rolling_avg"],
            color="red",
            linewidth=2,
            label="滚动平均值",
        )
        plt.title("响应时间随时间变化")
        plt.xlabel("时间")
        plt.ylabel("响应时间 (ms)")
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(output_dir, "response_time_over_time.png"), dpi=300)
        plt.close()

        # 每秒请求数 (RPS) 图
        plt.figure(figsize=(12, 6))

        # 计算每秒请求数
        df["second"] = df["start_time"].apply(lambda x: int(x))
        rps_df = df.groupby("second").size().reset_index(name="rps")
        rps_df["time"] = pd.to_datetime(rps_df["second"], unit="s")

        plt.plot(rps_df["time"], rps_df["rps"], linewidth=2)
        plt.title("每秒请求数 (RPS)")
        plt.xlabel("时间")
        plt.ylabel("请求/秒")
        plt.grid(True)
        plt.savefig(os.path.join(output_dir, "rps_over_time.png"), dpi=300)
        plt.close()

        # 按服务统计的响应时间箱线图
        plt.figure(figsize=(14, 8))
        service_groups = df[df["is_success"]].groupby("service_name")["response_time"]
        service_data = [group for _, group in service_groups]
        service_names = list(service_groups.groups.keys())

        if service_data:
            plt.boxplot(service_data, labels=service_names, vert=False)
            plt.title("各服务响应时间分布")
            plt.xlabel("响应时间 (ms)")
            plt.ylabel("服务")
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(
                os.path.join(output_dir, "response_time_by_service.png"), dpi=300
            )
        plt.close()

        # 按端点统计的成功率
        endpoint_df = pd.DataFrame(list(self.endpoint_stats.values()))

        if not endpoint_df.empty and len(endpoint_df) > 1:
            plt.figure(figsize=(14, max(6, len(endpoint_df) * 0.4)))
            endpoint_df = endpoint_df.sort_values("success_rate")
            plt.barh(endpoint_df["endpoint"], endpoint_df["success_rate"])
            plt.title("各端点成功率")
            plt.xlabel("成功率 (%)")
            plt.ylabel("端点")
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(
                os.path.join(output_dir, "success_rate_by_endpoint.png"), dpi=300
            )
            plt.close()

    def _generate_html_report(self, output_dir: str):
        """
        生成HTML报告

        Args:
            output_dir: 输出目录
        """
        # 基本HTML模板
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{test_name} - 性能测试报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }}
                h1, h2, h3 {{ color: #444; }}
                h1 {{ border-bottom: 2px solid #eee; padding-bottom: 10px; }}
                .section {{ margin-bottom: 30px; }}
                .summary-box {{ display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 25px; }}
                .summary-item {{ flex: 1; min-width: 200px; border: 1px solid #ddd; border-radius: 5px; padding: 15px; }}
                .summary-item h3 {{ margin-top: 0; color: #555; }}
                .success {{ color: green; }}
                .failure {{ color: red; }}
                .warning {{ color: orange; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f8f8f8; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .chart-container {{ margin: 20px 0; text-align: center; }}
                .chart {{ max-width: 100%; height: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                footer {{ margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; text-align: center; color: #777; }}
            </style>
        </head>
        <body>
            <h1>{test_name} - 性能测试报告</h1>

            <div class="section">
                <h2>测试摘要</h2>
                <div class="summary-box">
                    <div class="summary-item">
                        <h3>测试信息</h3>
                        <p><strong>测试ID:</strong> {test_id}</p>
                        <p><strong>开始时间:</strong> {start_time}</p>
                        <p><strong>结束时间:</strong> {end_time}</p>
                        <p><strong>持续时间:</strong> {duration} 秒</p>
                    </div>
                    <div class="summary-item">
                        <h3>请求统计</h3>
                        <p><strong>总请求数:</strong> {total_requests}</p>
                        <p><strong>成功请求:</strong> {successful_requests}</p>
                        <p><strong>失败请求:</strong> {failed_requests}</p>
                        <p><strong>成功率:</strong> <span class="{success_rate_class}">{success_rate:.2f}%</span></p>
                    </div>
                    <div class="summary-item">
                        <h3>性能指标</h3>
                        <p><strong>平均响应时间:</strong> {average_response_time:.2f} ms</p>
                        <p><strong>95百分位响应时间:</strong> <span class="{p95_class}">{p95_response_time:.2f} ms</span></p>
                        <p><strong>最小响应时间:</strong> {min_response_time:.2f} ms</p>
                        <p><strong>最大响应时间:</strong> {max_response_time:.2f} ms</p>
                    </div>
                    <div class="summary-item">
                        <h3>吞吐量</h3>
                        <p><strong>平均RPS:</strong> {rps:.2f} 请求/秒</p>
                        <p><strong>峰值RPS:</strong> {peak_rps} 请求/秒</p>
                        <p><strong>目标RPS:</strong> {target_rps} 请求/秒</p>
                        <p><strong>RPS达成率:</strong> {rps_achievement:.2f}%</p>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>测试配置</h2>
                <table>
                    <tr>
                        <th>参数</th>
                        <th>值</th>
                    </tr>
                    <tr>
                        <td>测试名称</td>
                        <td>{profile_name}</td>
                    </tr>
                    <tr>
                        <td>目标RPS</td>
                        <td>{target_rps}</td>
                    </tr>
                    <tr>
                        <td>测试持续时间</td>
                        <td>{profile_duration} 秒</td>
                    </tr>
                    <tr>
                        <td>成功率阈值</td>
                        <td>{success_threshold}%</td>
                    </tr>
                    <tr>
                        <td>P95响应时间阈值</td>
                        <td>{p95_threshold} ms</td>
                    </tr>
                </table>
            </div>

            <div class="section">
                <h2>服务性能</h2>
                <table>
                    <tr>
                        <th>服务</th>
                        <th>请求数</th>
                        <th>成功率</th>
                        <th>平均响应时间</th>
                        <th>P95响应时间</th>
                        <th>最小响应时间</th>
                        <th>最大响应时间</th>
                    </tr>
                    {service_rows}
                </table>
            </div>

            <div class="section">
                <h2>端点性能</h2>
                <table>
                    <tr>
                        <th>服务</th>
                        <th>端点</th>
                        <th>请求数</th>
                        <th>成功率</th>
                        <th>平均响应时间</th>
                        <th>P95响应时间</th>
                    </tr>
                    {endpoint_rows}
                </table>
            </div>

            <div class="section">
                <h2>图表</h2>
                <div class="chart-container">
                    <h3>响应时间分布</h3>
                    <img src="response_time_histogram.png" alt="响应时间分布" class="chart">
                </div>
                <div class="chart-container">
                    <h3>响应时间随时间变化</h3>
                    <img src="response_time_over_time.png" alt="响应时间随时间变化" class="chart">
                </div>
                <div class="chart-container">
                    <h3>每秒请求数 (RPS)</h3>
                    <img src="rps_over_time.png" alt="每秒请求数" class="chart">
                </div>
                <div class="chart-container">
                    <h3>各服务响应时间分布</h3>
                    <img src="response_time_by_service.png" alt="各服务响应时间分布" class="chart">
                </div>
                <div class="chart-container">
                    <h3>各端点成功率</h3>
                    <img src="success_rate_by_endpoint.png" alt="各端点成功率" class="chart">
                </div>
            </div>

            <footer>
                <p>索克生活性能测试平台 - 报告生成时间: {generation_time}</p>
            </footer>
        </body>
        </html>
        """

        # 确定成功率和P95响应时间的状态类
        success_rate_class = (
            "success"
            if self.success_rate >= self.profile.success_threshold
            else "failure"
        )
        p95_class = (
            "success"
            if self.p95_response_time <= self.profile.p95_threshold
            else "warning"
        )

        # 生成服务性能表格行
        service_rows = ""
        for service_name, stats in self.service_stats.items():
            service_rows += f"""
            <tr>
                <td>{service_name}</td>
                <td>{stats["total"]}</td>
                <td class="{"success" if stats["success_rate"] >= self.profile.success_threshold else "failure"}">{stats["success_rate"]:.2f}%</td>
                <td>{stats["avg_response_time"]:.2f} ms</td>
                <td class="{"success" if stats["p95_response_time"] <= self.profile.p95_threshold else "warning"}">{stats["p95_response_time"]:.2f} ms</td>
                <td>{stats["min_response_time"]:.2f} ms</td>
                <td>{stats["max_response_time"]:.2f} ms</td>
            </tr>
            """

        # 生成端点性能表格行
        endpoint_rows = ""
        for _endpoint_key, stats in self.endpoint_stats.items():
            endpoint_rows += f"""
            <tr>
                <td>{stats["service"]}</td>
                <td>{stats["endpoint"]}</td>
                <td>{stats["total"]}</td>
                <td class="{"success" if stats["success_rate"] >= self.profile.success_threshold else "failure"}">{stats["success_rate"]:.2f}%</td>
                <td>{stats["avg_response_time"]:.2f} ms</td>
                <td class="{"success" if stats["p95_response_time"] <= self.profile.p95_threshold else "warning"}">{stats["p95_response_time"]:.2f} ms</td>
            </tr>
            """

        # 计算RPS达成率
        rps_achievement = (
            (self.rps / self.profile.target_rps) * 100
            if self.profile.target_rps > 0
            else 0
        )

        # 填充HTML模板
        html_content = html_template.format(
            test_name=self.test_name,
            test_id=self.test_id,
            start_time=self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            end_time=self.end_time.strftime("%Y-%m-%d %H:%M:%S"),
            duration=f"{self.duration:.2f}",
            total_requests=self.total_requests,
            successful_requests=self.successful_requests,
            failed_requests=self.failed_requests,
            success_rate=self.success_rate,
            success_rate_class=success_rate_class,
            average_response_time=self.average_response_time,
            p95_response_time=self.p95_response_time,
            p95_class=p95_class,
            min_response_time=self.min_response_time,
            max_response_time=self.max_response_time,
            rps=self.rps,
            peak_rps=self.peak_rps,
            target_rps=self.profile.target_rps,
            rps_achievement=rps_achievement,
            profile_name=self.profile.name,
            profile_duration=self.profile.duration,
            success_threshold=self.profile.success_threshold,
            p95_threshold=self.profile.p95_threshold,
            service_rows=service_rows,
            endpoint_rows=endpoint_rows,
            generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        # 写入HTML文件
        report_path = os.path.join(output_dir, "report.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    def is_successful(self) -> bool:
        """
        判断测试是否成功

        成功标准:
        1. 成功率达到或超过阈值
        2. P95响应时间低于或等于阈值

        Returns:
            bool: 测试是否成功
        """
        return (
            self.success_rate >= self.profile.success_threshold
            and self.p95_response_time <= self.profile.p95_threshold
        )

class PerformanceTester:
    """性能测试器类"""

    def __init__(
        self,
        base_url: str,
        profile: TestProfile,
        endpoints: list[EndpointSpec],
        headers: dict[str, str] | None = None,
        verify_ssl: bool = True,
        timeout: float = 30.0,
        results_dir: str = "./results",
        auth_token_provider: Callable[[], str] | None = None,
    ):
        """
        初始化性能测试器

        Args:
            base_url: 基础URL
            profile: 测试配置文件
            endpoints: 接口列表
            headers: HTTP头
            verify_ssl: 是否验证SSL证书
            timeout: 请求超时时间（秒）
            results_dir: 结果保存目录
            auth_token_provider: 认证令牌提供器函数
        """
        self.base_url = base_url.rstrip("/")
        self.profile = profile
        self.endpoints = endpoints
        self.headers = headers or {}
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.results_dir = results_dir
        self.auth_token_provider = auth_token_provider

        self.test_id = str(uuid.uuid4())
        self.results = []
        self.is_running = False
        self.start_time = None
        self.end_time = None

        # 创建结果目录
        os.makedirs(results_dir, exist_ok=True)

        # 计算权重总和
        self.total_weight = sum(endpoint.weight for endpoint in endpoints)

        # 验证配置
        if not endpoints:
            raise ValueError("至少需要一个接口规格")

    async def run_test(self) -> TestResult:
        """
        运行测试

        Returns:
            TestResult: 测试结果
        """
        logger.info(f"开始性能测试: {self.profile.name}")
        logger.info(f"测试ID: {self.test_id}")
        logger.info(f"目标RPS: {self.profile.target_rps}")
        logger.info(f"测试持续时间: {self.profile.duration}秒")

        self.is_running = True
        self.start_time = datetime.now()

        if self.auth_token_provider:
            # 获取认证令牌并更新头
            try:
                token = self.auth_token_provider()
                self.headers["Authorization"] = f"Bearer {token}"
            except Exception as e:
                logger.error(f"获取认证令牌失败: {e}")

        # 创建客户端会话
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(
            timeout=timeout,
            headers=self.headers,
            connector=aiohttp.TCPConnector(verify_ssl=self.verify_ssl),
        ) as session:
            # 创建任务队列和结果列表

            # 创建并发请求控制信号量
            semaphore = asyncio.Semaphore(self.profile.max_concurrent_requests)

            # 启动请求生成器任务
            start_time = time.time()

            request_gen_task = asyncio.create_task(
                self._generate_requests(session, start_time, semaphore)
            )

            # 等待请求生成器完成
            await request_gen_task

            self.end_time = datetime.now()
            self.is_running = False

            logger.info(f"测试完成，共发送 {len(self.results)} 个请求")

            # 创建测试结果
            test_result = TestResult(
                test_id=self.test_id,
                test_name=self.profile.name,
                start_time=self.start_time,
                end_time=self.end_time,
                profile=self.profile,
                results=self.results,
                metadata=self.profile.metadata,
            )

            # 生成报告
            test_dir = os.path.join(self.results_dir, f"{self.test_id}")
            test_result.generate_report(test_dir)

            return test_result

    async def _generate_requests(
        self,
        session: aiohttp.ClientSession,
        start_time: float,
        semaphore: asyncio.Semaphore,
    ):
        """
        生成请求

        Args:
            session: HTTP会话
            start_time: 开始时间（Unix时间戳，秒）
            semaphore: 并发控制信号量
        """
        tasks = []
        request_count = 0

        # 主循环，持续发送请求直到测试结束
        while True:
            elapsed_time = time.time() - start_time

            # 检查测试是否应该结束
            if elapsed_time >= self.profile.duration:
                break

            # 获取当前阶段
            phase = self.profile.get_phase_at_time(elapsed_time)

            # 计算当前目标RPS
            current_target_rps = self.profile.get_target_rps_at_time(elapsed_time)

            # 计算本次循环应生成的请求数
            interval = 1.0  # 每次循环1秒
            target_requests = int(current_target_rps * interval)

            # 在这个间隔内生成请求
            for _ in range(target_requests):
                # 随机选择一个端点，基于权重
                endpoint = self._select_endpoint()

                # 创建发送请求的任务
                task = asyncio.create_task(
                    self._send_request(session, endpoint, phase, semaphore)
                )
                tasks.append(task)
                request_count += 1

            # 等待一个间隔
            interval_end = start_time + elapsed_time + interval
            now = time.time()
            if now < interval_end:
                await asyncio.sleep(interval_end - now)

        # 等待所有请求完成
        if tasks:
            await asyncio.gather(*tasks)

    def _select_endpoint(self) -> EndpointSpec:
        """
        基于权重随机选择一个端点

        Returns:
            EndpointSpec: 选择的端点
        """
        r = random.random() * self.total_weight
        cumulative_weight = 0

        for endpoint in self.endpoints:
            cumulative_weight += endpoint.weight
            if r <= cumulative_weight:
                return endpoint

        # 理论上不应该到达这里，但为安全起见
        return self.endpoints[-1]

    async def _send_request(
        self,
        session: aiohttp.ClientSession,
        endpoint: EndpointSpec,
        phase: TestPhase,
        semaphore: asyncio.Semaphore,
    ) -> RequestResult:
        """
        发送请求

        Args:
            session: HTTP会话
            endpoint: 接口规格
            phase: 测试阶段
            semaphore: 并发控制信号量

        Returns:
            RequestResult: 请求结果
        """
        # 使用信号量控制并发数
        async with semaphore:
            # 生成请求数据
            request_data = endpoint.generate_request()

            # 构造URL
            url = f"{self.base_url}{endpoint.endpoint}"

            # 准备请求参数
            method = endpoint.method.upper()
            request_args = {}

            if method in ["POST", "PUT", "PATCH"]:
                request_args["json"] = request_data
            elif method == "GET" and request_data:
                request_args["params"] = request_data

            # 记录开始时间
            start_time = time.time()

            try:
                # 发送请求
                async with session.request(method, url, **request_args) as response:
                    # 记录结束时间
                    end_time = time.time()

                    # 读取响应内容
                    try:
                        response_data = await response.text()
                        response_size = len(response_data)
                    except Exception:
                        response_size = 0

                    # 提取请求ID
                    request_id = response.headers.get("X-Request-ID")

                    # 创建请求结果
                    result = RequestResult(
                        service_name=endpoint.service_name,
                        endpoint=endpoint.endpoint,
                        start_time=start_time,
                        end_time=end_time,
                        status_code=response.status,
                        response_size=response_size,
                        error=None
                        if 200 <= response.status < 400
                        else f"HTTP {response.status}",
                        request_id=request_id,
                        phase=phase,
                        metadata={"method": method, **endpoint.metadata},
                    )
            except TimeoutError:
                # 请求超时
                end_time = time.time()
                result = RequestResult(
                    service_name=endpoint.service_name,
                    endpoint=endpoint.endpoint,
                    start_time=start_time,
                    end_time=end_time,
                    error="Request Timeout",
                    phase=phase,
                    metadata={"method": method, **endpoint.metadata},
                )
            except Exception as e:
                # 其他错误
                end_time = time.time()
                result = RequestResult(
                    service_name=endpoint.service_name,
                    endpoint=endpoint.endpoint,
                    start_time=start_time,
                    end_time=end_time,
                    error=str(e),
                    phase=phase,
                    metadata={"method": method, **endpoint.metadata},
                )

            # 添加到结果列表
            self.results.append(result)

            return result

class SuokeBenchmark:
    """索克基准测试类"""

    def __init__(
        self,
        config_file: str | None = None,
        results_dir: str = "./benchmark_results",
    ):
        """
        初始化基准测试

        Args:
            config_file: 配置文件路径
            results_dir: 结果保存目录
        """
        self.results_dir = results_dir

        # 创建结果目录
        os.makedirs(results_dir, exist_ok=True)

        # 加载配置
        self.config = {}
        if config_file:
            with open(config_file) as f:
                self.config = json.load(f)

    def create_user_service_test(
        self,
        base_url: str,
        target_rps: int = 100,
        duration: int = 300,
        token: str | None = None,
    ) -> PerformanceTester:
        """
        创建用户服务测试

        Args:
            base_url: 基础URL
            target_rps: 目标每秒请求数
            duration: 测试持续时间（秒）
            token: 认证令牌

        Returns:
            PerformanceTester: 性能测试器
        """
        # 创建测试配置
        profile = TestProfile(
            name="用户服务性能测试",
            description="测试用户服务的性能和扩展性",
            target_rps=target_rps,
            duration=duration,
            success_threshold=99.5,
            p95_threshold=200.0,
        )

        # 定义接口列表
        endpoints = [
            EndpointSpec(
                service_name=ServiceType.USER_SERVICE,
                endpoint="/api/v1/users",
                method="GET",
                weight=10,
            ),
            EndpointSpec(
                service_name=ServiceType.USER_SERVICE,
                endpoint="/api/v1/users/{user_id}",
                method="GET",
                weight=30,
                request_generator=lambda: {
                    "user_id": f"user_{random.randint(1, 1000)}"
                },
            ),
            EndpointSpec(
                service_name=ServiceType.USER_SERVICE,
                endpoint="/api/v1/users/{user_id}/health-summary",
                method="GET",
                weight=20,
                request_generator=lambda: {
                    "user_id": f"user_{random.randint(1, 1000)}"
                },
            ),
            EndpointSpec(
                service_name=ServiceType.USER_SERVICE,
                endpoint="/api/v1/users/{user_id}/devices",
                method="GET",
                weight=15,
                request_generator=lambda: {
                    "user_id": f"user_{random.randint(1, 1000)}"
                },
            ),
            EndpointSpec(
                service_name=ServiceType.USER_SERVICE,
                endpoint="/api/v1/users",
                method="POST",
                weight=5,
                request_generator=lambda: {
                    "username": f"testuser_{int(time.time())}",
                    "email": f"test_{int(time.time())}@example.com",
                    "password": "Test@123",
                    "full_name": "Test User",
                },
            ),
            EndpointSpec(
                service_name=ServiceType.USER_SERVICE,
                endpoint="/api/v1/users/{user_id}",
                method="PUT",
                weight=8,
                request_generator=lambda: {
                    "user_id": f"user_{random.randint(1, 1000)}",
                    "full_name": f"Updated User {int(time.time())}",
                },
            ),
            EndpointSpec(
                service_name=ServiceType.USER_SERVICE,
                endpoint="/api/v1/users/{user_id}/preferences",
                method="PUT",
                weight=8,
                request_generator=lambda: {
                    "user_id": f"user_{random.randint(1, 1000)}",
                    "preferences": {
                        "theme": random.choice(["light", "dark", "system"]),
                        "language": random.choice(["zh_CN", "en_US"]),
                        "notifications": random.choice([True, False]),
                    },
                },
            ),
            EndpointSpec(
                service_name=ServiceType.USER_SERVICE,
                endpoint="/api/v1/users/{user_id}/devices",
                method="POST",
                weight=4,
                request_generator=lambda: {
                    "user_id": f"user_{random.randint(1, 1000)}",
                    "device_id": f"device_{int(time.time())}",
                    "device_type": random.choice(["mobile", "tablet", "desktop"]),
                    "device_name": f"Test Device {random.randint(1, 100)}",
                },
            ),
        ]

        # 设置认证头
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # 创建测试器
        tester = PerformanceTester(
            base_url=base_url,
            profile=profile,
            endpoints=endpoints,
            headers=headers,
            results_dir=os.path.join(self.results_dir, "user_service"),
        )

        return tester

    def create_five_diagnosis_test(
        self,
        base_url: str,
        target_rps: int = 50,
        duration: int = 300,
        token: str | None = None,
    ) -> PerformanceTester:
        """
        创建五诊服务测试

        Args:
            base_url: 基础URL
            target_rps: 目标每秒请求数
            duration: 测试持续时间（秒）
            token: 认证令牌

        Returns:
            PerformanceTester: 性能测试器
        """
        # 创建测试配置
        profile = TestProfile(
            name="五诊服务性能测试",
            description="测试五诊服务的性能和响应时间",
            target_rps=target_rps,
            duration=duration,
            success_threshold=98.0,
            p95_threshold=1000.0,  # 1秒，因为AI推理可能较慢
        )

        # 定义接口列表
        endpoints = [
            EndpointSpec(
                service_name=ServiceType.FIVE_DIAGNOSIS,
                endpoint="/api/v1/diagnosis/tongue/analyze",
                method="POST",
                weight=25,
                request_generator=lambda: {
                    "image_id": f"tongue_{random.randint(1, 1000)}",
                    "analysis_type": "full",
                },
            ),
            EndpointSpec(
                service_name=ServiceType.FIVE_DIAGNOSIS,
                endpoint="/api/v1/diagnosis/face/analyze",
                method="POST",
                weight=20,
                request_generator=lambda: {
                    "image_id": f"face_{random.randint(1, 1000)}",
                    "analysis_type": "full",
                },
            ),
            EndpointSpec(
                service_name=ServiceType.FIVE_DIAGNOSIS,
                endpoint="/api/v1/diagnosis/voice/analyze",
                method="POST",
                weight=15,
                request_generator=lambda: {
                    "audio_id": f"voice_{random.randint(1, 1000)}",
                    "analysis_type": "full",
                },
            ),
            EndpointSpec(
                service_name=ServiceType.FIVE_DIAGNOSIS,
                endpoint="/api/v1/diagnosis/pulse/analyze",
                method="POST",
                weight=15,
                request_generator=lambda: {
                    "data_id": f"pulse_{random.randint(1, 1000)}",
                    "analysis_type": "full",
                },
            ),
            EndpointSpec(
                service_name=ServiceType.FIVE_DIAGNOSIS,
                endpoint="/api/v1/diagnosis/calculation/analyze",
                method="POST",
                weight=10,
                request_generator=lambda: {
                    "birth_date": "1990-01-01",
                    "birth_time": "08:00",
                    "current_season": "spring",
                    "analysis_type": "full",
                },
            ),
            EndpointSpec(
                service_name=ServiceType.FIVE_DIAGNOSIS,
                endpoint="/api/v1/diagnosis/fusion/analyze",
                method="POST",
                weight=10,
                request_generator=lambda: {
                    "tongue_id": f"tongue_{random.randint(1, 1000)}",
                    "face_id": f"face_{random.randint(1, 1000)}",
                    "voice_id": f"voice_{random.randint(1, 1000)}",
                    "pulse_id": f"pulse_{random.randint(1, 1000)}",
                    "inquiry_id": f"inquiry_{random.randint(1, 1000)}",
                    "calculation_id": f"calc_{random.randint(1, 1000)}",
                },
            ),
            EndpointSpec(
                service_name=ServiceType.FIVE_DIAGNOSIS,
                endpoint="/api/v1/diagnosis/inquiry/analyze",
                method="POST",
                weight=15,
                request_generator=lambda: {
                    "inquiry_id": f"inquiry_{random.randint(1, 1000)}",
                    "analysis_type": "full",
                },
            ),
        ]

        # 设置认证头
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # 创建测试器
        tester = PerformanceTester(
            base_url=base_url,
            profile=profile,
            endpoints=endpoints,
            headers=headers,
            results_dir=os.path.join(self.results_dir, "four_diagnosis"),
        )

        return tester

    def create_api_gateway_test(
        self,
        base_url: str,
        target_rps: int = 200,
        duration: int = 300,
        token: str | None = None,
    ) -> PerformanceTester:
        """
        创建API网关测试

        Args:
            base_url: 基础URL
            target_rps: 目标每秒请求数
            duration: 测试持续时间（秒）
            token: 认证令牌

        Returns:
            PerformanceTester: 性能测试器
        """
        # 创建测试配置
        profile = TestProfile(
            name="API网关性能测试",
            description="测试API网关的性能、路由和负载均衡能力",
            target_rps=target_rps,
            duration=duration,
            success_threshold=99.9,
            p95_threshold=300.0,
        )

        # 定义接口列表 - 综合各服务常用接口
        endpoints = [
            # 用户服务
            EndpointSpec(
                service_name=ServiceType.API_GATEWAY,
                endpoint="/api/v1/users",
                method="GET",
                weight=15,
            ),
            EndpointSpec(
                service_name=ServiceType.API_GATEWAY,
                endpoint="/api/v1/users/{user_id}",
                method="GET",
                weight=20,
                request_generator=lambda: {
                    "user_id": f"user_{random.randint(1, 1000)}"
                },
            ),
            # 认证服务
            EndpointSpec(
                service_name=ServiceType.API_GATEWAY,
                endpoint="/api/v1/auth/status",
                method="GET",
                weight=10,
            ),
            # 五诊服务
            EndpointSpec(
                service_name=ServiceType.API_GATEWAY,
                endpoint="/api/v1/diagnosis/tongue/analyze",
                method="POST",
                weight=8,
                request_generator=lambda: {
                    "image_id": f"tongue_{random.randint(1, 1000)}",
                    "analysis_type": "simple",
                },
            ),
            # 知识服务
            EndpointSpec(
                service_name=ServiceType.API_GATEWAY,
                endpoint="/api/v1/knowledge/search",
                method="GET",
                weight=12,
                request_generator=lambda: {
                    "q": random.choice(
                        ["舌诊", "脉诊", "面诊", "中医", "养生", "体质"]
                    ),
                    "limit": 10,
                },
            ),
            # 健康服务
            EndpointSpec(
                service_name=ServiceType.API_GATEWAY,
                endpoint="/api/v1/health/recommendations",
                method="GET",
                weight=15,
                request_generator=lambda: {
                    "user_id": f"user_{random.randint(1, 1000)}",
                    "type": random.choice(["diet", "exercise", "lifestyle", "herbs"]),
                },
            ),
            # 设备服务
            EndpointSpec(
                service_name=ServiceType.API_GATEWAY,
                endpoint="/api/v1/devices/status",
                method="GET",
                weight=10,
                request_generator=lambda: {
                    "device_id": f"device_{random.randint(1, 1000)}"
                },
            ),
        ]

        # 设置认证头
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # 创建测试器
        tester = PerformanceTester(
            base_url=base_url,
            profile=profile,
            endpoints=endpoints,
            headers=headers,
            results_dir=os.path.join(self.results_dir, "api_gateway"),
        )

        return tester

    async def run_comprehensive_benchmark(
        self, base_url: str, token: str | None = None
    ) -> list[TestResult]:
        """
        运行全面基准测试

        Args:
            base_url: 基础URL
            token: 认证令牌

        Returns:
            List[TestResult]: 测试结果列表
        """
        logger.info("开始运行全面基准测试")

        # 创建各服务测试器
        user_tester = self.create_user_service_test(
            base_url=base_url, target_rps=100, duration=180, token=token
        )

        four_diagnosis_tester = self.create_four_diagnosis_test(
            base_url=base_url, target_rps=50, duration=180, token=token
        )

        api_gateway_tester = self.create_api_gateway_test(
            base_url=base_url, target_rps=200, duration=180, token=token
        )

        # 运行测试
        logger.info("运行用户服务测试...")
        user_result = await user_tester.run_test()

        logger.info("运行五诊服务测试...")
        four_diagnosis_result = await four_diagnosis_tester.run_test()

        logger.info("运行API网关测试...")
        api_gateway_result = await api_gateway_tester.run_test()

        # 返回结果
        results = [user_result, four_diagnosis_result, api_gateway_result]

        # 生成汇总报告
        await self._generate_summary_report(results)

        return results

    async def _generate_summary_report(self, results: list[TestResult]):
        """
        生成汇总报告

        Args:
            results: 测试结果列表
        """
        logger.info("生成汇总报告...")

        # 创建汇总目录
        summary_dir = os.path.join(self.results_dir, "summary")
        os.makedirs(summary_dir, exist_ok=True)

        # 创建汇总数据
        summary_data = {
            "timestamp": datetime.now().isoformat(),
            "test_count": len(results),
            "tests": [],
        }

        # 收集各测试结果
        for result in results:
            summary_data["tests"].append(
                {
                    "test_id": result.test_id,
                    "test_name": result.test_name,
                    "duration": result.duration,
                    "total_requests": result.total_requests,
                    "success_rate": result.success_rate,
                    "average_response_time": result.average_response_time,
                    "p95_response_time": result.p95_response_time,
                    "rps": result.rps,
                    "target_rps": result.profile.target_rps,
                    "is_successful": result.is_successful(),
                }
            )

        # 保存汇总JSON
        with open(os.path.join(summary_dir, "summary.json"), "w") as f:
            json.dump(summary_data, f, indent=2)

        # 创建对比图表
        self._create_comparison_charts(results, summary_dir)

        # 生成HTML报告
        await self._generate_summary_html(results, summary_dir)

        logger.info(f"汇总报告已生成到目录: {summary_dir}")

    def _create_comparison_charts(self, results: list[TestResult], output_dir: str):
        """
        创建对比图表

        Args:
            results: 测试结果列表
            output_dir: 输出目录
        """
        plt.style.use("ggplot")

        # 响应时间对比图
        plt.figure(figsize=(12, 6))
        test_names = [result.test_name for result in results]
        avg_times = [result.average_response_time for result in results]
        p95_times = [result.p95_response_time for result in results]

        x = range(len(test_names))
        bar_width = 0.35

        plt.bar(
            x, avg_times, width=bar_width, label="平均响应时间", color="blue", alpha=0.7
        )
        plt.bar(
            [i + bar_width for i in x],
            p95_times,
            width=bar_width,
            label="P95响应时间",
            color="red",
            alpha=0.7,
        )

        plt.xlabel("测试")
        plt.ylabel("响应时间 (ms)")
        plt.title("各测试响应时间对比")
        plt.xticks([i + bar_width / 2 for i in x], test_names, rotation=45, ha="right")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "response_time_comparison.png"), dpi=300)
        plt.close()

        # RPS对比图
        plt.figure(figsize=(12, 6))
        actual_rps = [result.rps for result in results]
        target_rps = [result.profile.target_rps for result in results]

        plt.bar(
            x, target_rps, width=bar_width, label="目标RPS", color="green", alpha=0.7
        )
        plt.bar(
            [i + bar_width for i in x],
            actual_rps,
            width=bar_width,
            label="实际RPS",
            color="orange",
            alpha=0.7,
        )

        plt.xlabel("测试")
        plt.ylabel("每秒请求数")
        plt.title("各测试RPS对比")
        plt.xticks([i + bar_width / 2 for i in x], test_names, rotation=45, ha="right")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "rps_comparison.png"), dpi=300)
        plt.close()

        # 成功率对比图
        plt.figure(figsize=(12, 6))
        success_rates = [result.success_rate for result in results]
        thresholds = [result.profile.success_threshold for result in results]

        plt.bar(
            x,
            success_rates,
            color=[
                "green" if sr >= th else "red"
                for sr, th in zip(success_rates, thresholds, strict=False)
            ],
        )

        plt.xlabel("测试")
        plt.ylabel("成功率 (%)")
        plt.title("各测试成功率对比")
        plt.xticks(x, test_names, rotation=45, ha="right")
        plt.axhline(y=min(thresholds), linestyle="--", color="black", label="最低阈值")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "success_rate_comparison.png"), dpi=300)
        plt.close()

    async def _generate_summary_html(self, results: list[TestResult], output_dir: str):
        """
        生成汇总HTML报告

        Args:
            results: 测试结果列表
            output_dir: 输出目录
        """
        # 基本HTML模板
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>索克生活性能测试汇总报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }}
                h1, h2, h3 {{ color: #444; }}
                h1 {{ border-bottom: 2px solid #eee; padding-bottom: 10px; }}
                .section {{ margin-bottom: 30px; }}
                .summary-box {{ display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 25px; }}
                .summary-item {{ flex: 1; min-width: 200px; border: 1px solid #ddd; border-radius: 5px; padding: 15px; }}
                .summary-item h3 {{ margin-top: 0; color: #555; }}
                .success {{ color: green; }}
                .failure {{ color: red; }}
                .warning {{ color: orange; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f8f8f8; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .chart-container {{ margin: 20px 0; text-align: center; }}
                .chart {{ max-width: 100%; height: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                footer {{ margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; text-align: center; color: #777; }}
            </style>
        </head>
        <body>
            <h1>索克生活性能测试汇总报告</h1>

            <div class="section">
                <h2>测试摘要</h2>
                <div class="summary-box">
                    <div class="summary-item">
                        <h3>基本信息</h3>
                        <p><strong>测试时间:</strong> {timestamp}</p>
                        <p><strong>测试数量:</strong> {test_count}</p>
                        <p><strong>成功测试:</strong> {successful_tests} / {test_count}</p>
                    </div>
                    <div class="summary-item">
                        <h3>性能亮点</h3>
                        <p><strong>最高RPS:</strong> {highest_rps:.2f} (在 {highest_rps_test})</p>
                        <p><strong>最快响应:</strong> {fastest_response:.2f} ms (在 {fastest_response_test})</p>
                        <p><strong>最高成功率:</strong> {highest_success_rate:.2f}% (在 {highest_success_rate_test})</p>
                    </div>
                    <div class="summary-item">
                        <h3>性能问题</h3>
                        <p><strong>最慢响应:</strong> {slowest_response:.2f} ms (在 {slowest_response_test})</p>
                        <p><strong>最低成功率:</strong> {lowest_success_rate:.2f}% (在 {lowest_success_rate_test})</p>
                        <p><strong>最低RPS达成率:</strong> {lowest_rps_achievement:.2f}% (在 {lowest_rps_achievement_test})</p>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>测试详情</h2>
                <table>
                    <tr>
                        <th>测试名称</th>
                        <th>总请求数</th>
                        <th>成功率</th>
                        <th>平均响应时间</th>
                        <th>P95响应时间</th>
                        <th>目标RPS</th>
                        <th>实际RPS</th>
                        <th>RPS达成率</th>
                        <th>状态</th>
                    </tr>
                    {test_rows}
                </table>
            </div>

            <div class="section">
                <h2>对比图表</h2>
                <div class="chart-container">
                    <h3>响应时间对比</h3>
                    <img src="response_time_comparison.png" alt="响应时间对比" class="chart">
                </div>
                <div class="chart-container">
                    <h3>RPS对比</h3>
                    <img src="rps_comparison.png" alt="RPS对比" class="chart">
                </div>
                <div class="chart-container">
                    <h3>成功率对比</h3>
                    <img src="success_rate_comparison.png" alt="成功率对比" class="chart">
                </div>
            </div>

            <div class="section">
                <h2>测试报告链接</h2>
                <ul>
                    {report_links}
                </ul>
            </div>

            <footer>
                <p>索克生活性能测试平台 - 报告生成时间: {generation_time}</p>
            </footer>
        </body>
        </html>
        """

        # 计算汇总数据
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_count = len(results)
        successful_tests = sum(1 for result in results if result.is_successful())

        # 找出性能亮点和问题
        highest_rps = max(result.rps for result in results)
        highest_rps_test = next(
            result.test_name for result in results if result.rps == highest_rps
        )

        fastest_response = min(result.average_response_time for result in results)
        fastest_response_test = next(
            result.test_name
            for result in results
            if result.average_response_time == fastest_response
        )

        highest_success_rate = max(result.success_rate for result in results)
        highest_success_rate_test = next(
            result.test_name
            for result in results
            if result.success_rate == highest_success_rate
        )

        slowest_response = max(result.p95_response_time for result in results)
        slowest_response_test = next(
            result.test_name
            for result in results
            if result.p95_response_time == slowest_response
        )

        lowest_success_rate = min(result.success_rate for result in results)
        lowest_success_rate_test = next(
            result.test_name
            for result in results
            if result.success_rate == lowest_success_rate
        )

        rps_achievements = [
            (result.rps / result.profile.target_rps) * 100
            if result.profile.target_rps > 0
            else 0
            for result in results
        ]
        lowest_rps_achievement = min(rps_achievements)
        lowest_rps_achievement_test = results[
            rps_achievements.index(lowest_rps_achievement)
        ].test_name

        # 生成测试行
        test_rows = ""
        for result in results:
            rps_achievement = (
                (result.rps / result.profile.target_rps) * 100
                if result.profile.target_rps > 0
                else 0
            )
            status_class = "success" if result.is_successful() else "failure"
            status_text = "通过" if result.is_successful() else "未通过"

            test_rows += f"""
            <tr>
                <td>{result.test_name}</td>
                <td>{result.total_requests}</td>
                <td class="{"success" if result.success_rate >= result.profile.success_threshold else "failure"}">{result.success_rate:.2f}%</td>
                <td>{result.average_response_time:.2f} ms</td>
                <td class="{"success" if result.p95_response_time <= result.profile.p95_threshold else "warning"}">{result.p95_response_time:.2f} ms</td>
                <td>{result.profile.target_rps}</td>
                <td>{result.rps:.2f}</td>
                <td class="{"success" if rps_achievement >= 90 else "warning" if rps_achievement >= 70 else "failure"}">{rps_achievement:.2f}%</td>
                <td class="{status_class}">{status_text}</td>
            </tr>
            """

        # 生成报告链接
        report_links = ""
        for result in results:
            test_dir = f"{result.test_id}"
            report_links += f"""
            <li><a href="../{test_dir}/report.html" target="_blank">{result.test_name} 详细报告</a></li>
            """

        # 填充HTML模板
        html_content = html_template.format(
            timestamp=timestamp,
            test_count=test_count,
            successful_tests=successful_tests,
            highest_rps=highest_rps,
            highest_rps_test=highest_rps_test,
            fastest_response=fastest_response,
            fastest_response_test=fastest_response_test,
            highest_success_rate=highest_success_rate,
            highest_success_rate_test=highest_success_rate_test,
            slowest_response=slowest_response,
            slowest_response_test=slowest_response_test,
            lowest_success_rate=lowest_success_rate,
            lowest_success_rate_test=lowest_success_rate_test,
            lowest_rps_achievement=lowest_rps_achievement,
            lowest_rps_achievement_test=lowest_rps_achievement_test,
            test_rows=test_rows,
            report_links=report_links,
            generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        # 写入HTML文件
        report_path = os.path.join(output_dir, "summary_report.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

# 直接运行示例
if __name__ == "__main__":

    async def main():
        benchmark = SuokeBenchmark(results_dir="./benchmark_results")

        # 示例：运行API网关测试
        api_gateway_tester = benchmark.create_api_gateway_test(
            base_url="http://api-gateway:8080", target_rps=50, duration=60
        )

        result = await api_gateway_tester.run_test()
        print(f"测试完成: {result.test_name}")
        print(f"成功率: {result.success_rate:.2f}%")
        print(f"平均响应时间: {result.average_response_time:.2f} ms")
        print(f"P95响应时间: {result.p95_response_time:.2f} ms")
        print(f"实际RPS: {result.rps:.2f}")

    asyncio.run(main())
