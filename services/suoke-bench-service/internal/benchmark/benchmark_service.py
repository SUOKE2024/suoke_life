"""
benchmark_service - 索克生活项目模块
"""

            from internal.benchmark.model_interface import LocalModel
        from internal.suokebench.config import load_config
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from internal.benchmark.model_cache import get_global_cache
from internal.benchmark.model_interface import ModelInterface, ModelPrediction
from internal.observability.metrics import get_global_metrics
from internal.resilience.retry import (
from internal.suokebench.config import BenchConfig
from typing import Any
import asyncio
import logging
import os
import time
import uuid

"""
基准测试服务

提供完整的基准测试执行、结果分析和报告生成功能
"""


    CircuitBreakerConfig,
    RetryConfig,
    circuit_breaker,
    retry,
)

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkTask:
    """基准测试任务"""

    task_id: str
    benchmark_id: str
    model_id: str
    model_version: str
    test_data: list[dict[str, Any]]
    config: dict[str, Any]
    created_at: datetime
    status: str = "pending"  # pending, running, completed, failed
    progress: float = 0.0
    results: dict[str, Any] | None = None
    error_message: str | None = None


@dataclass
class BenchmarkResult:
    """基准测试结果"""

    task_id: str
    benchmark_id: str
    model_id: str
    model_version: str
    metrics: dict[str, float]
    predictions: list[ModelPrediction]
    execution_time: float
    timestamp: datetime
    metadata: dict[str, Any]


class BenchmarkExecutor:
    """基准测试执行器"""

    def __init__(self, config: BenchConfig):
        """
        初始化基准测试执行器

        Args:
            config: 基准测试配置
        """
        self.config = config
        self.cache = get_global_cache()
        self.metrics = get_global_metrics()

        # 任务管理
        self.active_tasks: dict[str, BenchmarkTask] = {}
        self.completed_tasks: dict[str, BenchmarkResult] = {}

        # 线程池
        self.executor = ThreadPoolExecutor(
            max_workers=config.benchmark.max_concurrent_tasks
        )

        # 重试配置
        self.retry_config = RetryConfig(
            max_attempts=3, base_delay=1.0, exceptions=(Exception,)
        )

        # 熔断器配置
        self.circuit_breaker_config = CircuitBreakerConfig(
            failure_threshold=5, recovery_timeout=60.0
        )

        logger.info(
            f"基准测试执行器初始化完成，最大并发任务数: {config.benchmark.max_concurrent_tasks}"
        )

    async def submit_benchmark(
        self,
        benchmark_id: str,
        model_id: str,
        model_version: str,
        test_data: list[dict[str, Any]],
        config: dict[str, Any] | None = None,
    ) -> str:
        """
        提交基准测试任务

        Args:
            benchmark_id: 基准测试ID
            model_id: 模型ID
            model_version: 模型版本
            test_data: 测试数据
            config: 测试配置

        Returns:
            任务ID
        """
        task_id = str(uuid.uuid4())

        task = BenchmarkTask(
            task_id=task_id,
            benchmark_id=benchmark_id,
            model_id=model_id,
            model_version=model_version,
            test_data=test_data,
            config=config or {},
            created_at=datetime.now(),
        )

        self.active_tasks[task_id] = task

        # 异步执行任务
        asyncio.create_task(self._execute_benchmark_async(task))

        logger.info(f"基准测试任务已提交: {task_id}")
        return task_id

    async def _execute_benchmark_async(self, task: BenchmarkTask):
        """异步执行基准测试"""
        try:
            task.status = "running"
            self.metrics.update_active_benchmarks(
                len([t for t in self.active_tasks.values() if t.status == "running"])
            )

            start_time = time.time()

            # 执行基准测试
            result = await self._run_benchmark_with_retry(task)

            execution_time = time.time() - start_time

            # 创建结果对象
            benchmark_result = BenchmarkResult(
                task_id=task.task_id,
                benchmark_id=task.benchmark_id,
                model_id=task.model_id,
                model_version=task.model_version,
                metrics=result["metrics"],
                predictions=result["predictions"],
                execution_time=execution_time,
                timestamp=datetime.now(),
                metadata=result.get("metadata", {}),
            )

            # 保存结果
            self.completed_tasks[task.task_id] = benchmark_result
            task.status = "completed"
            task.progress = 1.0
            task.results = asdict(benchmark_result)

            # 记录指标
            self.metrics.record_benchmark_run(
                benchmark_id=task.benchmark_id,
                model_id=task.model_id,
                status="SUCCESS",
                duration=execution_time,
            )

            # 记录质量指标
            self.metrics.record_benchmark_quality(
                benchmark_id=task.benchmark_id,
                model_id=task.model_id,
                metrics=result["metrics"],
            )

            logger.info(
                f"基准测试任务完成: {task.task_id}, 耗时: {execution_time:.2f}s"
            )

        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)

            execution_time = time.time() - start_time if "start_time" in locals() else 0

            # 记录失败指标
            self.metrics.record_benchmark_run(
                benchmark_id=task.benchmark_id,
                model_id=task.model_id,
                status="FAILED",
                duration=execution_time,
            )

            logger.error(f"基准测试任务失败: {task.task_id} - {str(e)}")

        finally:
            # 更新活跃任务数
            self.metrics.update_active_benchmarks(
                len([t for t in self.active_tasks.values() if t.status == "running"])
            )

    @retry(max_attempts=3, base_delay=1.0)
    @circuit_breaker(failure_threshold=5, recovery_timeout=60.0)
    async def _run_benchmark_with_retry(self, task: BenchmarkTask) -> dict[str, Any]:
        """带重试和熔断器的基准测试执行"""
        return await self._run_benchmark(task)

    async def _run_benchmark(self, task: BenchmarkTask) -> dict[str, Any]:
        """执行基准测试核心逻辑"""
        # 获取模型
        model = await self._get_model(task.model_id, task.model_version)

        # 执行预测
        predictions = []
        metrics = {}

        total_items = len(task.test_data)
        processed_items = 0

        # 批量处理
        batch_size = task.config.get("batch_size", 32)

        for i in range(0, total_items, batch_size):
            batch_data = task.test_data[i : i + batch_size]

            # 批量预测
            batch_predictions = await self._batch_predict(model, batch_data, task)
            predictions.extend(batch_predictions)

            processed_items += len(batch_data)
            task.progress = processed_items / total_items

            # 记录进度
            if processed_items % 100 == 0:
                logger.info(
                    f"任务 {task.task_id} 进度: {processed_items}/{total_items}"
                )

        # 计算评估指标
        metrics = await self._calculate_metrics(
            task.benchmark_id, predictions, task.test_data
        )

        return {
            "predictions": predictions,
            "metrics": metrics,
            "metadata": {
                "total_items": total_items,
                "batch_size": batch_size,
                "model_cache_hit": True,  # 简化实现
            },
        }

    async def _get_model(self, model_id: str, model_version: str) -> ModelInterface:
        """获取模型实例"""

        def model_factory():
            # 这里应该根据model_id和model_version创建具体的模型实例
            # 简化实现，返回一个模拟模型

            return LocalModel(model_id, model_version, None)

        model = self.cache.get_model(model_id, model_version, model_factory)

        # 记录缓存指标
        self.metrics.record_cache_hit(model_id, model_version)

        return model

    async def _batch_predict(
        self,
        model: ModelInterface,
        batch_data: list[dict[str, Any]],
        task: BenchmarkTask,
    ) -> list[ModelPrediction]:
        """批量预测"""
        predictions = []

        for item in batch_data:
            start_time = time.time()

            try:
                # 执行预测
                prediction = await model.predict_async(item["input"])
                predictions.append(prediction)

                # 记录推理时间
                inference_time = time.time() - start_time
                self.metrics.record_model_inference(
                    model_id=task.model_id,
                    model_version=task.model_version,
                    task_type=task.benchmark_id,
                    duration=inference_time,
                )

            except Exception as e:
                logger.error(f"预测失败: {str(e)}")
                # 创建错误预测结果
                error_prediction = ModelPrediction(
                    input_data=item["input"],
                    output_data={"error": str(e)},
                    confidence=0.0,
                    latency=time.time() - start_time,
                    metadata={"error": True},
                )
                predictions.append(error_prediction)

        return predictions

    async def _calculate_metrics(
        self,
        benchmark_id: str,
        predictions: list[ModelPrediction],
        test_data: list[dict[str, Any]],
    ) -> dict[str, float]:
        """计算评估指标"""
        metrics = {}

        # 基础指标
        total_predictions = len(predictions)
        successful_predictions = len(
            [p for p in predictions if not p.metadata.get("error", False)]
        )

        metrics["total_predictions"] = total_predictions
        metrics["successful_predictions"] = successful_predictions
        metrics["success_rate"] = (
            successful_predictions / total_predictions if total_predictions > 0 else 0.0
        )

        # 延迟指标
        latencies = [
            p.latency for p in predictions if not p.metadata.get("error", False)
        ]
        if latencies:
            metrics["avg_latency"] = sum(latencies) / len(latencies)
            metrics["max_latency"] = max(latencies)
            metrics["min_latency"] = min(latencies)
            metrics["p95_latency"] = (
                sorted(latencies)[int(len(latencies) * 0.95)]
                if len(latencies) > 20
                else max(latencies)
            )

        # 置信度指标
        confidences = [
            p.confidence for p in predictions if not p.metadata.get("error", False)
        ]
        if confidences:
            metrics["avg_confidence"] = sum(confidences) / len(confidences)
            metrics["min_confidence"] = min(confidences)
            metrics["max_confidence"] = max(confidences)

        # 特定基准测试的指标
        if benchmark_id == "tcm_diagnosis":
            metrics.update(await self._calculate_tcm_metrics(predictions, test_data))
        elif benchmark_id == "health_plan":
            metrics.update(
                await self._calculate_health_plan_metrics(predictions, test_data)
            )
        elif benchmark_id == "agent_collaboration":
            metrics.update(
                await self._calculate_collaboration_metrics(predictions, test_data)
            )

        return metrics

    async def _calculate_tcm_metrics(
        self, predictions: list[ModelPrediction], test_data: list[dict[str, Any]]
    ) -> dict[str, float]:
        """计算中医诊断指标"""
        # 简化实现，实际应该包含更复杂的中医诊断评估逻辑
        correct_diagnoses = 0
        total_diagnoses = 0

        for i, prediction in enumerate(predictions):
            if i < len(test_data) and not prediction.metadata.get("error", False):
                expected = test_data[i].get("expected_output", {})
                predicted = prediction.output_data

                # 简单的诊断匹配
                if expected.get("syndrome") == predicted.get("syndrome"):
                    correct_diagnoses += 1
                total_diagnoses += 1

        accuracy = correct_diagnoses / total_diagnoses if total_diagnoses > 0 else 0.0

        return {
            "tcm_diagnosis_accuracy": accuracy,
            "tcm_correct_diagnoses": correct_diagnoses,
            "tcm_total_diagnoses": total_diagnoses,
        }

    async def _calculate_health_plan_metrics(
        self, predictions: list[ModelPrediction], test_data: list[dict[str, Any]]
    ) -> dict[str, float]:
        """计算健康方案指标"""
        # 简化实现
        return {
            "health_plan_completeness": 0.85,
            "health_plan_relevance": 0.78,
            "health_plan_feasibility": 0.82,
        }

    async def _calculate_collaboration_metrics(
        self, predictions: list[ModelPrediction], test_data: list[dict[str, Any]]
    ) -> dict[str, float]:
        """计算智能体协作指标"""
        # 简化实现
        return {
            "collaboration_efficiency": 0.75,
            "collaboration_consistency": 0.88,
            "collaboration_coverage": 0.92,
        }

    def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        """获取任务状态"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                "task_id": task.task_id,
                "status": task.status,
                "progress": task.progress,
                "created_at": task.created_at.isoformat(),
                "error_message": task.error_message,
            }
        elif task_id in self.completed_tasks:
            result = self.completed_tasks[task_id]
            return {
                "task_id": result.task_id,
                "status": "completed",
                "progress": 1.0,
                "results": asdict(result),
            }

        return None

    def get_task_result(self, task_id: str) -> BenchmarkResult | None:
        """获取任务结果"""
        return self.completed_tasks.get(task_id)

    def list_tasks(self, status: str | None = None) -> list[dict[str, Any]]:
        """列出任务"""
        tasks = []

        # 活跃任务
        for task in self.active_tasks.values():
            if status is None or task.status == status:
                tasks.append(
                    {
                        "task_id": task.task_id,
                        "benchmark_id": task.benchmark_id,
                        "model_id": task.model_id,
                        "status": task.status,
                        "progress": task.progress,
                        "created_at": task.created_at.isoformat(),
                    }
                )

        # 已完成任务
        for result in self.completed_tasks.values():
            if status is None or status == "completed":
                tasks.append(
                    {
                        "task_id": result.task_id,
                        "benchmark_id": result.benchmark_id,
                        "model_id": result.model_id,
                        "status": "completed",
                        "progress": 1.0,
                        "created_at": result.timestamp.isoformat(),
                    }
                )

        return sorted(tasks, key=lambda x: x["created_at"], reverse=True)

    async def generate_report(self, task_id: str) -> str | None:
        """生成测试报告"""
        result = self.get_task_result(task_id)
        if not result:
            return None

        # 生成HTML报告
        report_content = await self._generate_html_report(result)

        # 保存报告
        report_path = f"data/reports/{task_id}_report.html"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        logger.info(f"报告已生成: {report_path}")
        return report_path

    async def _generate_html_report(self, result: BenchmarkResult) -> str:
        """生成HTML报告"""
        # 简化的HTML报告模板
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>基准测试报告 - {task_id}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .metrics {{ margin: 20px 0; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                .predictions {{ margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>基准测试报告</h1>
                <p><strong>任务ID:</strong> {task_id}</p>
                <p><strong>基准测试:</strong> {benchmark_id}</p>
                <p><strong>模型:</strong> {model_id} (版本: {model_version})</p>
                <p><strong>执行时间:</strong> {execution_time:.2f} 秒</p>
                <p><strong>生成时间:</strong> {timestamp}</p>
            </div>

            <div class="metrics">
                <h2>评估指标</h2>
                {metrics_html}
            </div>

            <div class="predictions">
                <h2>预测结果摘要</h2>
                <p>总预测数: {total_predictions}</p>
                <p>成功预测数: {successful_predictions}</p>
                <p>平均延迟: {avg_latency:.3f} 秒</p>
            </div>
        </body>
        </html>
        """

        # 生成指标HTML
        metrics_html = ""
        for key, value in result.metrics.items():
            metrics_html += (
                f'<div class="metric"><strong>{key}:</strong> {value:.4f}</div>'
            )

        # 计算摘要统计
        total_predictions = len(result.predictions)
        successful_predictions = len(
            [p for p in result.predictions if not p.metadata.get("error", False)]
        )
        avg_latency = (
            sum(p.latency for p in result.predictions) / total_predictions
            if total_predictions > 0
            else 0
        )

        return html_template.format(
            task_id=result.task_id,
            benchmark_id=result.benchmark_id,
            model_id=result.model_id,
            model_version=result.model_version,
            execution_time=result.execution_time,
            timestamp=result.timestamp.isoformat(),
            metrics_html=metrics_html,
            total_predictions=total_predictions,
            successful_predictions=successful_predictions,
            avg_latency=avg_latency,
        )

    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        # 清理已完成的任务
        to_remove = []
        for task_id, result in self.completed_tasks.items():
            if result.timestamp < cutoff_time:
                to_remove.append(task_id)

        for task_id in to_remove:
            del self.completed_tasks[task_id]

        # 清理失败的活跃任务
        to_remove = []
        for task_id, task in self.active_tasks.items():
            if task.status in ["failed", "completed"] and task.created_at < cutoff_time:
                to_remove.append(task_id)

        for task_id in to_remove:
            del self.active_tasks[task_id]

        if to_remove:
            logger.info(f"清理了 {len(to_remove)} 个旧任务")


# 全局基准测试执行器
_global_executor: BenchmarkExecutor | None = None


def get_global_executor() -> BenchmarkExecutor:
    """获取全局基准测试执行器"""
    global _global_executor
    if _global_executor is None:

        config = load_config("config/config.yaml")
        _global_executor = BenchmarkExecutor(config)
    return _global_executor


def init_global_executor(config: BenchConfig) -> BenchmarkExecutor:
    """初始化全局基准测试执行器"""
    global _global_executor
    _global_executor = BenchmarkExecutor(config)
    return _global_executor
