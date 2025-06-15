#!/usr/bin/env python

"""
性能监控和优化工具
提供系统性能监控、分析和优化建议

功能特性：
- 实时性能监控
- 内存使用分析
- CPU使用率监控
- 磁盘I/O监控
- 网络性能监控
- 性能瓶颈识别
- 优化建议生成
"""

import asyncio
import json
import logging
import os
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import psutil

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""

    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_read_mb: float
    disk_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    process_count: int
    thread_count: int
    load_average: Tuple[float, float, float]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class PerformanceAlert:
    """性能告警数据类"""

    timestamp: float
    level: str  # INFO, WARNING, CRITICAL
    category: str  # CPU, MEMORY, DISK, NETWORK
    message: str
    value: float
    threshold: float
    suggestion: str


class PerformanceMonitor:
    """性能监控器"""

    def __init__(
        self,
        collection_interval: float = 1.0,
        history_size: int = 3600,
        alert_thresholds: Optional[Dict[str, float]] = None,
    ):
        """
        初始化性能监控器

        Args:
            collection_interval: 数据收集间隔(秒)
            history_size: 历史数据保存数量
            alert_thresholds: 告警阈值配置
        """
        self.collection_interval = collection_interval
        self.history_size = history_size

        # 默认告警阈值
        self.alert_thresholds = alert_thresholds or {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_read_mb": 100.0,
            "disk_write_mb": 100.0,
            "network_sent_mb": 50.0,
            "network_recv_mb": 50.0,
        }

        # 数据存储
        self.metrics_history: deque = deque(maxlen=history_size)
        self.alerts_history: deque = deque(maxlen=1000)

        # 监控状态
        self.is_monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None

        # 性能统计
        self.stats = {
            "total_samples": 0,
            "alerts_count": defaultdict(int),
            "peak_values": {},
            "average_values": {},
        }

        # 初始化网络和磁盘计数器
        self._last_network_io = psutil.net_io_counters()
        self._last_disk_io = psutil.disk_io_counters()
        self._last_timestamp = time.time()

    async def start_monitoring(self) -> None:
        """开始监控"""
        if self.is_monitoring:
            logger.warning("性能监控已在运行")
            return

        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("性能监控已启动")

    async def stop_monitoring(self) -> None:
        """停止监控"""
        if not self.is_monitoring:
            return

        self.is_monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass

        logger.info("性能监控已停止")

    async def _monitoring_loop(self) -> None:
        """监控循环"""
        try:
            while self.is_monitoring:
                metrics = await self._collect_metrics()
                self.metrics_history.append(metrics)

                # 检查告警
                alerts = self._check_alerts(metrics)
                for alert in alerts:
                    self.alerts_history.append(alert)
                    logger.warning(f"性能告警: {alert.message}")

                # 更新统计信息
                self._update_stats(metrics)

                await asyncio.sleep(self.collection_interval)

        except asyncio.CancelledError:
            logger.info("监控循环已取消")
        except Exception as e:
            logger.error(f"监控循环异常: {e}")

    async def _collect_metrics(self) -> PerformanceMetrics:
        """收集性能指标"""
        current_time = time.time()

        # CPU和内存
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()

        # 磁盘I/O
        current_disk_io = psutil.disk_io_counters()
        disk_read_mb = 0.0
        disk_write_mb = 0.0

        if self._last_disk_io and current_disk_io:
            time_delta = current_time - self._last_timestamp
            if time_delta > 0:
                disk_read_mb = (
                    (current_disk_io.read_bytes - self._last_disk_io.read_bytes)
                    / (1024 * 1024)
                    / time_delta
                )
                disk_write_mb = (
                    (current_disk_io.write_bytes - self._last_disk_io.write_bytes)
                    / (1024 * 1024)
                    / time_delta
                )

        # 网络I/O
        current_network_io = psutil.net_io_counters()
        network_sent_mb = 0.0
        network_recv_mb = 0.0

        if self._last_network_io and current_network_io:
            time_delta = current_time - self._last_timestamp
            if time_delta > 0:
                network_sent_mb = (
                    (current_network_io.bytes_sent - self._last_network_io.bytes_sent)
                    / (1024 * 1024)
                    / time_delta
                )
                network_recv_mb = (
                    (current_network_io.bytes_recv - self._last_network_io.bytes_recv)
                    / (1024 * 1024)
                    / time_delta
                )

        # 进程和线程数
        process_count = len(psutil.pids())
        thread_count = sum(
            p.num_threads()
            for p in psutil.process_iter(["num_threads"])
            if p.info["num_threads"]
        )

        # 负载平均值
        try:
            load_average = os.getloadavg()
        except (OSError, AttributeError):
            load_average = (0.0, 0.0, 0.0)

        # 更新上次记录
        self._last_disk_io = current_disk_io
        self._last_network_io = current_network_io
        self._last_timestamp = current_time

        return PerformanceMetrics(
            timestamp=current_time,
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / (1024 * 1024),
            memory_available_mb=memory.available / (1024 * 1024),
            disk_read_mb=disk_read_mb,
            disk_write_mb=disk_write_mb,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            process_count=process_count,
            thread_count=thread_count,
            load_average=load_average,
        )

    def _check_alerts(self, metrics: PerformanceMetrics) -> List[PerformanceAlert]:
        """检查告警条件"""
        alerts = []

        # CPU告警
        if metrics.cpu_percent > self.alert_thresholds["cpu_percent"]:
            alerts.append(
                PerformanceAlert(
                    timestamp=metrics.timestamp,
                    level="WARNING" if metrics.cpu_percent < 90 else "CRITICAL",
                    category="CPU",
                    message=f"CPU使用率过高: {metrics.cpu_percent:.1f}%",
                    value=metrics.cpu_percent,
                    threshold=self.alert_thresholds["cpu_percent"],
                    suggestion="考虑优化CPU密集型任务或增加CPU资源",
                )
            )

        # 内存告警
        if metrics.memory_percent > self.alert_thresholds["memory_percent"]:
            alerts.append(
                PerformanceAlert(
                    timestamp=metrics.timestamp,
                    level="WARNING" if metrics.memory_percent < 95 else "CRITICAL",
                    category="MEMORY",
                    message=f"内存使用率过高: {metrics.memory_percent:.1f}%",
                    value=metrics.memory_percent,
                    threshold=self.alert_thresholds["memory_percent"],
                    suggestion="考虑释放内存或增加内存资源",
                )
            )

        # 磁盘I/O告警
        if metrics.disk_read_mb > self.alert_thresholds["disk_read_mb"]:
            alerts.append(
                PerformanceAlert(
                    timestamp=metrics.timestamp,
                    level="WARNING",
                    category="DISK",
                    message=f"磁盘读取速度过高: {metrics.disk_read_mb:.1f} MB/s",
                    value=metrics.disk_read_mb,
                    threshold=self.alert_thresholds["disk_read_mb"],
                    suggestion="检查磁盘I/O密集型操作",
                )
            )

        if metrics.disk_write_mb > self.alert_thresholds["disk_write_mb"]:
            alerts.append(
                PerformanceAlert(
                    timestamp=metrics.timestamp,
                    level="WARNING",
                    category="DISK",
                    message=f"磁盘写入速度过高: {metrics.disk_write_mb:.1f} MB/s",
                    value=metrics.disk_write_mb,
                    threshold=self.alert_thresholds["disk_write_mb"],
                    suggestion="检查磁盘I/O密集型操作",
                )
            )

        # 网络I/O告警
        if metrics.network_sent_mb > self.alert_thresholds["network_sent_mb"]:
            alerts.append(
                PerformanceAlert(
                    timestamp=metrics.timestamp,
                    level="WARNING",
                    category="NETWORK",
                    message=f"网络发送速度过高: {metrics.network_sent_mb:.1f} MB/s",
                    value=metrics.network_sent_mb,
                    threshold=self.alert_thresholds["network_sent_mb"],
                    suggestion="检查网络密集型操作",
                )
            )

        if metrics.network_recv_mb > self.alert_thresholds["network_recv_mb"]:
            alerts.append(
                PerformanceAlert(
                    timestamp=metrics.timestamp,
                    level="WARNING",
                    category="NETWORK",
                    message=f"网络接收速度过高: {metrics.network_recv_mb:.1f} MB/s",
                    value=metrics.network_recv_mb,
                    threshold=self.alert_thresholds["network_recv_mb"],
                    suggestion="检查网络密集型操作",
                )
            )

        return alerts

    def _update_stats(self, metrics: PerformanceMetrics) -> None:
        """更新统计信息"""
        self.stats["total_samples"] += 1

        # 更新峰值
        metrics_dict = metrics.to_dict()
        for key, value in metrics_dict.items():
            if isinstance(value, (int, float)) and key != "timestamp":
                if key not in self.stats["peak_values"]:
                    self.stats["peak_values"][key] = value
                else:
                    self.stats["peak_values"][key] = max(
                        self.stats["peak_values"][key], value
                    )

    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """获取当前性能指标"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return None

    def get_metrics_history(
        self, duration_minutes: int = 60
    ) -> List[PerformanceMetrics]:
        """获取历史性能指标"""
        if not self.metrics_history:
            return []

        cutoff_time = time.time() - (duration_minutes * 60)
        return [m for m in self.metrics_history if m.timestamp >= cutoff_time]

    def get_alerts_history(self, duration_minutes: int = 60) -> List[PerformanceAlert]:
        """获取历史告警"""
        if not self.alerts_history:
            return []

        cutoff_time = time.time() - (duration_minutes * 60)
        return [a for a in self.alerts_history if a.timestamp >= cutoff_time]

    def generate_performance_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        if not self.metrics_history:
            return {"error": "没有性能数据"}

        # 计算统计信息
        recent_metrics = self.get_metrics_history(60)  # 最近1小时
        if not recent_metrics:
            return {"error": "没有最近的性能数据"}

        # 转换为DataFrame进行分析
        df = pd.DataFrame([m.to_dict() for m in recent_metrics])

        report = {
            "summary": {
                "total_samples": len(recent_metrics),
                "time_range": {
                    "start": datetime.fromtimestamp(df["timestamp"].min()).isoformat(),
                    "end": datetime.fromtimestamp(df["timestamp"].max()).isoformat(),
                },
            },
            "cpu": {
                "average": float(df["cpu_percent"].mean()),
                "peak": float(df["cpu_percent"].max()),
                "min": float(df["cpu_percent"].min()),
                "std": float(df["cpu_percent"].std()),
            },
            "memory": {
                "average_percent": float(df["memory_percent"].mean()),
                "peak_percent": float(df["memory_percent"].max()),
                "average_used_mb": float(df["memory_used_mb"].mean()),
                "peak_used_mb": float(df["memory_used_mb"].max()),
            },
            "disk_io": {
                "average_read_mb": float(df["disk_read_mb"].mean()),
                "peak_read_mb": float(df["disk_read_mb"].max()),
                "average_write_mb": float(df["disk_write_mb"].mean()),
                "peak_write_mb": float(df["disk_write_mb"].max()),
            },
            "network_io": {
                "average_sent_mb": float(df["network_sent_mb"].mean()),
                "peak_sent_mb": float(df["network_sent_mb"].max()),
                "average_recv_mb": float(df["network_recv_mb"].mean()),
                "peak_recv_mb": float(df["network_recv_mb"].max()),
            },
            "alerts": {
                "total_count": len(self.get_alerts_history(60)),
                "by_category": dict(self.stats["alerts_count"]),
            },
            "recommendations": self._generate_recommendations(df),
        }

        return report

    def _generate_recommendations(self, df: pd.DataFrame) -> List[str]:
        """生成优化建议"""
        recommendations = []

        # CPU优化建议
        avg_cpu = df["cpu_percent"].mean()
        if avg_cpu > 70:
            recommendations.append(
                "CPU使用率较高，建议优化CPU密集型任务或考虑增加CPU资源"
            )
        elif avg_cpu < 20:
            recommendations.append("CPU使用率较低，可以考虑增加并发处理能力")

        # 内存优化建议
        avg_memory = df["memory_percent"].mean()
        if avg_memory > 80:
            recommendations.append("内存使用率较高，建议检查内存泄漏或增加内存资源")

        # 磁盘I/O优化建议
        avg_disk_read = df["disk_read_mb"].mean()
        avg_disk_write = df["disk_write_mb"].mean()
        if avg_disk_read > 50 or avg_disk_write > 50:
            recommendations.append("磁盘I/O较高，建议使用缓存或优化数据访问模式")

        # 网络I/O优化建议
        avg_network_sent = df["network_sent_mb"].mean()
        avg_network_recv = df["network_recv_mb"].mean()
        if avg_network_sent > 20 or avg_network_recv > 20:
            recommendations.append("网络I/O较高，建议优化网络请求或使用连接池")

        if not recommendations:
            recommendations.append("系统性能良好，无需特别优化")

        return recommendations

    def export_metrics(self, filepath: str, format: str = "json") -> None:
        """导出性能指标"""
        if not self.metrics_history:
            logger.warning("没有性能数据可导出")
            return

        data = [m.to_dict() for m in self.metrics_history]

        if format.lower() == "json":
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif format.lower() == "csv":
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
        else:
            raise ValueError(f"不支持的格式: {format}")

        logger.info(f"性能数据已导出到: {filepath}")

    def create_performance_charts(self, output_dir: str) -> None:
        """创建性能图表"""
        if not self.metrics_history:
            logger.warning("没有性能数据可绘制")
            return

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 转换为DataFrame
        df = pd.DataFrame([m.to_dict() for m in self.metrics_history])
        df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")

        # 创建子图
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle("系统性能监控图表", fontsize=16)

        # CPU使用率
        axes[0, 0].plot(df["datetime"], df["cpu_percent"], "b-", linewidth=1)
        axes[0, 0].set_title("CPU使用率 (%)")
        axes[0, 0].set_ylabel("百分比")
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].axhline(
            y=self.alert_thresholds["cpu_percent"], color="r", linestyle="--", alpha=0.7
        )

        # 内存使用率
        axes[0, 1].plot(df["datetime"], df["memory_percent"], "g-", linewidth=1)
        axes[0, 1].set_title("内存使用率 (%)")
        axes[0, 1].set_ylabel("百分比")
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].axhline(
            y=self.alert_thresholds["memory_percent"],
            color="r",
            linestyle="--",
            alpha=0.7,
        )

        # 磁盘I/O
        axes[1, 0].plot(
            df["datetime"], df["disk_read_mb"], "r-", linewidth=1, label="读取"
        )
        axes[1, 0].plot(
            df["datetime"], df["disk_write_mb"], "orange", linewidth=1, label="写入"
        )
        axes[1, 0].set_title("磁盘I/O (MB/s)")
        axes[1, 0].set_ylabel("MB/s")
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)

        # 网络I/O
        axes[1, 1].plot(
            df["datetime"], df["network_sent_mb"], "purple", linewidth=1, label="发送"
        )
        axes[1, 1].plot(
            df["datetime"], df["network_recv_mb"], "brown", linewidth=1, label="接收"
        )
        axes[1, 1].set_title("网络I/O (MB/s)")
        axes[1, 1].set_ylabel("MB/s")
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)

        # 调整布局
        plt.tight_layout()

        # 保存图表
        chart_path = output_path / "performance_charts.png"
        plt.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"性能图表已保存到: {chart_path}")


class PerformanceOptimizer:
    """性能优化器"""

    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor

    def analyze_performance_bottlenecks(self) -> Dict[str, Any]:
        """分析性能瓶颈"""
        report = self.monitor.generate_performance_report()
        if "error" in report:
            return report

        bottlenecks = {
            "cpu_bottlenecks": [],
            "memory_bottlenecks": [],
            "disk_bottlenecks": [],
            "network_bottlenecks": [],
            "overall_score": 0,
        }

        # CPU瓶颈分析
        cpu_avg = report["cpu"]["average"]
        cpu_peak = report["cpu"]["peak"]

        if cpu_avg > 80:
            bottlenecks["cpu_bottlenecks"].append(
                {
                    "severity": "high",
                    "issue": f"CPU平均使用率过高: {cpu_avg:.1f}%",
                    "suggestion": "考虑优化算法、使用异步处理或增加CPU资源",
                }
            )
        elif cpu_peak > 95:
            bottlenecks["cpu_bottlenecks"].append(
                {
                    "severity": "medium",
                    "issue": f"CPU峰值使用率过高: {cpu_peak:.1f}%",
                    "suggestion": "检查CPU密集型任务的调度",
                }
            )

        # 内存瓶颈分析
        memory_avg = report["memory"]["average_percent"]
        memory_peak = report["memory"]["peak_percent"]

        if memory_avg > 85:
            bottlenecks["memory_bottlenecks"].append(
                {
                    "severity": "high",
                    "issue": f"内存平均使用率过高: {memory_avg:.1f}%",
                    "suggestion": "检查内存泄漏、优化数据结构或增加内存",
                }
            )
        elif memory_peak > 95:
            bottlenecks["memory_bottlenecks"].append(
                {
                    "severity": "medium",
                    "issue": f"内存峰值使用率过高: {memory_peak:.1f}%",
                    "suggestion": "优化内存使用模式",
                }
            )

        # 磁盘I/O瓶颈分析
        disk_read_avg = report["disk_io"]["average_read_mb"]
        disk_write_avg = report["disk_io"]["average_write_mb"]

        if disk_read_avg > 100 or disk_write_avg > 100:
            bottlenecks["disk_bottlenecks"].append(
                {
                    "severity": "medium",
                    "issue": f"磁盘I/O较高 (读: {disk_read_avg:.1f}, 写: {disk_write_avg:.1f} MB/s)",
                    "suggestion": "使用缓存、批量操作或SSD存储",
                }
            )

        # 网络I/O瓶颈分析
        network_sent_avg = report["network_io"]["average_sent_mb"]
        network_recv_avg = report["network_io"]["average_recv_mb"]

        if network_sent_avg > 50 or network_recv_avg > 50:
            bottlenecks["network_bottlenecks"].append(
                {
                    "severity": "medium",
                    "issue": f"网络I/O较高 (发送: {network_sent_avg:.1f}, 接收: {network_recv_avg:.1f} MB/s)",
                    "suggestion": "优化网络请求、使用连接池或CDN",
                }
            )

        # 计算总体性能评分 (0-100)
        cpu_score = max(0, 100 - cpu_avg)
        memory_score = max(0, 100 - memory_avg)
        disk_score = max(0, 100 - min(disk_read_avg + disk_write_avg, 100))
        network_score = max(0, 100 - min(network_sent_avg + network_recv_avg, 100))

        bottlenecks["overall_score"] = int(
            (cpu_score + memory_score + disk_score + network_score) / 4
        )

        return bottlenecks

    def generate_optimization_plan(self) -> Dict[str, Any]:
        """生成优化计划"""
        bottlenecks = self.analyze_performance_bottlenecks()

        if "error" in bottlenecks:
            return bottlenecks

        plan = {
            "priority_actions": [],
            "medium_term_actions": [],
            "long_term_actions": [],
            "estimated_impact": {},
        }

        # 高优先级行动
        for category in ["cpu_bottlenecks", "memory_bottlenecks"]:
            for bottleneck in bottlenecks[category]:
                if bottleneck["severity"] == "high":
                    plan["priority_actions"].append(
                        {
                            "category": category.replace("_bottlenecks", ""),
                            "action": bottleneck["suggestion"],
                            "impact": "high",
                        }
                    )

        # 中期行动
        for category in ["disk_bottlenecks", "network_bottlenecks"]:
            for bottleneck in bottlenecks[category]:
                plan["medium_term_actions"].append(
                    {
                        "category": category.replace("_bottlenecks", ""),
                        "action": bottleneck["suggestion"],
                        "impact": "medium",
                    }
                )

        # 长期行动
        if bottlenecks["overall_score"] < 70:
            plan["long_term_actions"].extend(
                [
                    {
                        "category": "architecture",
                        "action": "考虑微服务架构重构",
                        "impact": "high",
                    },
                    {
                        "category": "infrastructure",
                        "action": "评估硬件升级需求",
                        "impact": "high",
                    },
                ]
            )

        # 预估影响
        plan["estimated_impact"] = {
            "performance_improvement": f"{min(30, 100 - bottlenecks['overall_score'])}%",
            "resource_savings": "10-25%",
            "response_time_improvement": "15-40%",
        }

        return plan


async def main():
    """主函数 - 演示性能监控功能"""
    print("🚀 索克生活无障碍服务 - 性能监控工具")
    print("=" * 50)

    # 创建性能监控器
    monitor = PerformanceMonitor(
        collection_interval=1.0,
        history_size=3600,
    )

    # 创建性能优化器
    optimizer = PerformanceOptimizer(monitor)

    try:
        # 启动监控
        await monitor.start_monitoring()

        # 运行一段时间收集数据
        print("📊 开始收集性能数据...")
        await asyncio.sleep(10)

        # 生成报告
        print("\n📈 生成性能报告...")
        report = monitor.generate_performance_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))

        # 分析瓶颈
        print("\n🔍 分析性能瓶颈...")
        bottlenecks = optimizer.analyze_performance_bottlenecks()
        print(json.dumps(bottlenecks, indent=2, ensure_ascii=False))

        # 生成优化计划
        print("\n💡 生成优化计划...")
        plan = optimizer.generate_optimization_plan()
        print(json.dumps(plan, indent=2, ensure_ascii=False))

        # 导出数据
        print("\n💾 导出性能数据...")
        monitor.export_metrics("performance_data.json")

        # 创建图表
        print("\n📊 创建性能图表...")
        monitor.create_performance_charts("charts")

    except KeyboardInterrupt:
        print("\n⏹️  监控已停止")
    finally:
        await monitor.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(main())
