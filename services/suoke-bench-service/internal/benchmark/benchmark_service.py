"""
基准测试服务实现
"""

import logging
import time
import uuid
from concurrent import futures
from datetime import datetime
from typing import Any, Dict, List, Optional

import grpc

from api.grpc import benchmark_pb2, benchmark_pb2_grpc
from internal.benchmark.runner import BenchmarkRunner
from internal.suokebench.config import BenchConfig

logger = logging.getLogger(__name__)


class BenchmarkService(benchmark_pb2_grpc.BenchmarkServiceServicer):
    """基准测试服务实现"""

    def __init__(self, config: BenchConfig):
        """
        初始化基准测试服务
        
        Args:
            config: 服务配置
        """
        self.config = config
        self.runners: Dict[str, BenchmarkRunner] = {}
        self.results: Dict[str, Any] = {}
        self.executor = futures.ThreadPoolExecutor(max_workers=config.max_workers)
        logger.info("基准测试服务已初始化")

    def RunBenchmark(
        self, request: benchmark_pb2.RunBenchmarkRequest, context: grpc.ServicerContext
    ) -> benchmark_pb2.RunBenchmarkResponse:
        """运行基准测试"""
        
        # 生成唯一运行ID
        run_id = str(uuid.uuid4())
        
        # 检查基准测试任务是否存在
        benchmark_id = request.benchmark_id
        if benchmark_id not in self.config.tasks:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"找不到基准测试任务: {benchmark_id}")
            return benchmark_pb2.RunBenchmarkResponse(
                run_id="", status="FAILED", message=f"找不到基准测试任务: {benchmark_id}"
            )
        
        # 获取任务配置
        task_config = self.config.tasks[benchmark_id]
        
        # 创建运行器
        runner = BenchmarkRunner(
            run_id=run_id,
            benchmark_id=benchmark_id,
            model_id=request.model_id,
            model_version=request.model_version,
            task_config=task_config,
            config=self.config,
            parameters=dict(request.parameters),
        )
        
        # 存储运行器
        self.runners[run_id] = runner
        
        # 异步执行基准测试
        future = self.executor.submit(runner.run)
        future.add_done_callback(lambda f: self._handle_benchmark_completion(run_id, f))
        
        logger.info(f"启动基准测试: {benchmark_id}, 运行ID: {run_id}")
        
        return benchmark_pb2.RunBenchmarkResponse(
            run_id=run_id,
            status="RUNNING",
            message=f"基准测试 {benchmark_id} 已启动",
        )

    def GetBenchmarkResult(
        self, request: benchmark_pb2.GetBenchmarkResultRequest, context: grpc.ServicerContext
    ) -> benchmark_pb2.GetBenchmarkResultResponse:
        """获取基准测试结果"""
        
        run_id = request.run_id
        include_details = request.include_details
        
        # 检查运行ID是否存在
        if run_id not in self.runners and run_id not in self.results:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"找不到运行ID: {run_id}")
            return benchmark_pb2.GetBenchmarkResultResponse()
        
        # 如果测试仍在运行
        if run_id in self.runners:
            runner = self.runners[run_id]
            
            # 构建基本响应
            response = benchmark_pb2.GetBenchmarkResultResponse(
                run_id=run_id,
                benchmark_id=runner.benchmark_id,
                model_id=runner.model_id,
                model_version=runner.model_version,
                status="RUNNING",
                task=self._get_task_enum(runner.task_config.type),
                created_at=runner.start_time.isoformat() if runner.start_time else "",
            )
            
            # 如果有进行中的指标，添加
            if runner.current_metrics:
                for name, value in runner.current_metrics.items():
                    metric_result = benchmark_pb2.MetricResult(
                        name=name,
                        value=value,
                        unit=self.config.metrics.get(name, {}).get("unit", ""),
                    )
                    response.metrics[name].CopyFrom(metric_result)
                    
            return response
            
        # 如果测试已完成
        result = self.results[run_id]
        
        # 构建响应
        response = benchmark_pb2.GetBenchmarkResultResponse(
            run_id=run_id,
            benchmark_id=result["benchmark_id"],
            model_id=result["model_id"],
            model_version=result["model_version"],
            status=result["status"],
            task=self._get_task_enum(result["task_type"]),
            created_at=result["created_at"],
            completed_at=result["completed_at"],
        )
        
        # 添加指标结果
        for name, metric in result["metrics"].items():
            metric_result = benchmark_pb2.MetricResult(
                name=name,
                value=metric["value"],
                unit=metric["unit"],
                threshold=metric["threshold"],
                pass=metric["pass"],
                comparison=metric.get("comparison", ""),
            )
            response.metrics[name].CopyFrom(metric_result)
        
        # 如果需要详情，添加样本结果
        if include_details and "samples" in result:
            for sample in result["samples"]:
                sample_result = benchmark_pb2.SampleResult(
                    sample_id=sample["id"],
                    input=sample["input"],
                    expected=sample["expected"],
                    actual=sample["actual"],
                    correct=sample["correct"],
                )
                
                # 添加详细分数
                for score_name, score_value in sample.get("scores", {}).items():
                    sample_result.scores[score_name] = score_value
                
                response.samples.append(sample_result)
        
        return response

    def ListBenchmarks(
        self, request: benchmark_pb2.ListBenchmarksRequest, context: grpc.ServicerContext
    ) -> benchmark_pb2.ListBenchmarksResponse:
        """列出基准测试任务"""
        
        task_filter = request.task_filter
        tag = request.tag
        
        benchmarks = []
        
        # 遍历所有任务
        for task_id, task in self.config.tasks.items():
            # 应用任务类型过滤
            if task_filter != benchmark_pb2.UNKNOWN and self._get_task_enum(task.type) != task_filter:
                continue
                
            # 应用标签过滤
            if tag and tag not in task.tags:
                continue
                
            # 构建测试信息
            benchmark_info = benchmark_pb2.BenchmarkInfo(
                id=task_id,
                name=task.name,
                description=task.description,
                task=self._get_task_enum(task.type),
                tags=task.tags,
                sample_count=self._get_dataset_size(task.datasets),
            )
            
            # 添加指标
            for metric in task.metrics:
                benchmark_info.metrics.append(metric)
                
            # 添加参数
            for param_name, param_desc in task.parameters.items():
                benchmark_info.parameters[param_name] = param_desc
                
            benchmarks.append(benchmark_info)
            
        return benchmark_pb2.ListBenchmarksResponse(benchmarks=benchmarks)

    def CompareBenchmarks(
        self, request: benchmark_pb2.CompareBenchmarksRequest, context: grpc.ServicerContext
    ) -> benchmark_pb2.CompareBenchmarksResponse:
        """比较基准测试结果"""
        
        baseline_id = request.baseline_run_id
        compare_id = request.compare_run_id
        
        # 检查两个运行ID是否都存在且已完成
        if baseline_id not in self.results:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"找不到基线运行ID: {baseline_id}")
            return benchmark_pb2.CompareBenchmarksResponse()
            
        if compare_id not in self.results:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"找不到比较运行ID: {compare_id}")
            return benchmark_pb2.CompareBenchmarksResponse()
            
        # 获取结果
        baseline = self.results[baseline_id]
        compare = self.results[compare_id]
        
        # 检查任务类型是否相同
        if baseline["benchmark_id"] != compare["benchmark_id"]:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("只能比较相同任务类型的基准测试")
            return benchmark_pb2.CompareBenchmarksResponse()
            
        # 构建响应
        response = benchmark_pb2.CompareBenchmarksResponse(
            baseline_model=f"{baseline['model_id']}:{baseline['model_version']}",
            compare_model=f"{compare['model_id']}:{compare['model_version']}",
        )
        
        # 比较指标
        for metric_name in baseline["metrics"].keys():
            if metric_name in compare["metrics"]:
                baseline_value = baseline["metrics"][metric_name]["value"]
                compare_value = compare["metrics"][metric_name]["value"]
                
                # 计算差异
                diff = compare_value - baseline_value
                diff_percent = (diff / baseline_value) * 100 if baseline_value != 0 else 0
                
                # 确定差异是否显著
                metric_config = self.config.metrics.get(metric_name, {})
                higher_is_better = metric_config.get("higher_is_better", True)
                threshold = metric_config.get("threshold", 0)
                significant = abs(diff_percent) > 5  # 差异超过5%认为显著
                
                comparison_result = benchmark_pb2.ComparisonResult(
                    baseline_value=baseline_value,
                    compare_value=compare_value,
                    diff=diff,
                    diff_percent=diff_percent,
                    significant=significant,
                )
                
                response.metrics[metric_name].CopyFrom(comparison_result)
        
        # 添加案例比较（如果有样本数据）
        if "samples" in baseline and "samples" in compare:
            # 创建样本ID到样本的映射
            baseline_samples = {s["id"]: s for s in baseline["samples"]}
            compare_samples = {s["id"]: s for s in compare["samples"]}
            
            # 找到共同的样本ID
            common_sample_ids = set(baseline_samples.keys()) & set(compare_samples.keys())
            
            # 添加案例比较
            for sample_id in common_sample_ids:
                b_sample = baseline_samples[sample_id]
                c_sample = compare_samples[sample_id]
                
                case_comparison = benchmark_pb2.CaseComparison(
                    sample_id=sample_id,
                    input=b_sample["input"],
                    expected=b_sample["expected"],
                    baseline_output=b_sample["actual"],
                    compare_output=c_sample["actual"],
                    baseline_correct=b_sample.get("correct", False),
                    compare_correct=c_sample.get("correct", False),
                )
                
                response.case_comparisons.append(case_comparison)
        
        # 添加比较总结
        response.summary = self._generate_comparison_summary(response)
        
        return response

    def ExportReport(
        self, request: benchmark_pb2.ExportReportRequest, context: grpc.ServicerContext
    ) -> benchmark_pb2.ExportReportResponse:
        """导出评测报告"""
        
        run_id = request.run_id
        format_enum = request.format
        include_samples = request.include_samples
        metrics = list(request.metrics) if request.metrics else None
        
        # 检查运行ID是否存在且已完成
        if run_id not in self.results:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"找不到运行ID或测试尚未完成: {run_id}")
            return benchmark_pb2.ExportReportResponse()
            
        # 确定格式
        format_map = {
            benchmark_pb2.HTML: "html",
            benchmark_pb2.PDF: "pdf",
            benchmark_pb2.JSON: "json",
            benchmark_pb2.MARKDOWN: "md",
        }
        
        report_format = format_map.get(format_enum, "html")
        
        # 在这里实现报告生成逻辑
        # 实际项目中应该调用报告生成模块
        # 这里简单返回一个模拟的URL
        
        # 生成报告文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"report_{run_id}_{timestamp}.{report_format}"
        report_url = f"/reports/{filename}"
        
        return benchmark_pb2.ExportReportResponse(
            report_url=report_url,
            message=f"报告已生成: {filename}",
        )

    def MonitorBenchmark(
        self, request: benchmark_pb2.MonitorBenchmarkRequest, context: grpc.ServicerContext
    ):
        """监控基准测试进度"""
        
        run_id = request.run_id
        
        # 检查运行ID是否存在
        if run_id not in self.runners and run_id not in self.results:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"找不到运行ID: {run_id}")
            return
            
        # 如果测试已完成
        if run_id in self.results:
            result = self.results[run_id]
            progress = benchmark_pb2.BenchmarkProgress(
                run_id=run_id,
                status=result["status"],
                progress=100.0,
                current_stage="完成",
                processed_samples=result.get("total_samples", 0),
                total_samples=result.get("total_samples", 0),
                message="基准测试已完成",
            )
            
            # 添加指标
            for metric_name, metric in result["metrics"].items():
                progress.current_metrics[metric_name] = metric["value"]
                
            yield progress
            return
        
        # 如果测试还在运行
        runner = self.runners[run_id]
        
        try:
            # 发送初始进度
            progress = benchmark_pb2.BenchmarkProgress(
                run_id=run_id,
                status="RUNNING",
                progress=runner.progress,
                current_stage=runner.current_stage,
                processed_samples=runner.processed_samples,
                total_samples=runner.total_samples,
                message="基准测试运行中",
            )
            
            # 添加当前指标
            for metric_name, metric_value in runner.current_metrics.items():
                progress.current_metrics[metric_name] = metric_value
                
            yield progress
            
            # 持续监控进度
            while run_id in self.runners:
                time.sleep(1)  # 每秒更新一次
                
                # 检查连接是否已关闭
                if context.is_active():
                    progress = benchmark_pb2.BenchmarkProgress(
                        run_id=run_id,
                        status="RUNNING" if runner.is_running else "COMPLETED",
                        progress=runner.progress,
                        current_stage=runner.current_stage,
                        processed_samples=runner.processed_samples,
                        total_samples=runner.total_samples,
                        message="基准测试运行中" if runner.is_running else "基准测试已完成",
                    )
                    
                    # 添加当前指标
                    for metric_name, metric_value in runner.current_metrics.items():
                        progress.current_metrics[metric_name] = metric_value
                        
                    yield progress
                else:
                    # 客户端已断开连接
                    break
                
                # 检查测试是否已完成
                if not runner.is_running and run_id in self.results:
                    result = self.results[run_id]
                    final_progress = benchmark_pb2.BenchmarkProgress(
                        run_id=run_id,
                        status=result["status"],
                        progress=100.0,
                        current_stage="完成",
                        processed_samples=result.get("total_samples", 0),
                        total_samples=result.get("total_samples", 0),
                        message="基准测试已完成",
                    )
                    
                    # 添加指标
                    for metric_name, metric in result["metrics"].items():
                        final_progress.current_metrics[metric_name] = metric["value"]
                        
                    yield final_progress
                    break
                    
        except Exception as e:
            logger.error(f"监控基准测试失败: {str(e)}", exc_info=True)
            # 出错时也要发送状态
            error_progress = benchmark_pb2.BenchmarkProgress(
                run_id=run_id,
                status="ERROR",
                progress=runner.progress,
                current_stage="错误",
                processed_samples=runner.processed_samples,
                total_samples=runner.total_samples,
                message=f"监控出错: {str(e)}",
            )
            yield error_progress

    def _handle_benchmark_completion(self, run_id: str, future: futures.Future):
        """处理基准测试完成"""
        try:
            # 获取结果
            result = future.result()
            
            # 存储结果
            self.results[run_id] = result
            
            # 清理运行器
            if run_id in self.runners:
                del self.runners[run_id]
                
            logger.info(f"基准测试完成: {run_id}")
        except Exception as e:
            logger.error(f"基准测试失败: {run_id}, 错误: {str(e)}", exc_info=True)
            
            # 记录错误结果
            if run_id in self.runners:
                runner = self.runners[run_id]
                self.results[run_id] = {
                    "benchmark_id": runner.benchmark_id,
                    "model_id": runner.model_id,
                    "model_version": runner.model_version,
                    "status": "ERROR",
                    "task_type": runner.task_config.type,
                    "created_at": runner.start_time.isoformat() if runner.start_time else "",
                    "completed_at": datetime.now().isoformat(),
                    "error": str(e),
                    "metrics": {},
                }
                
                # 清理运行器
                del self.runners[run_id]

    def _get_task_enum(self, task_type: str) -> benchmark_pb2.BenchmarkTask:
        """
        将任务类型字符串转换为枚举值
        
        Args:
            task_type: 任务类型字符串
            
        Returns:
            任务类型枚举值
        """
        task_map = {
            "TCM_DIAGNOSIS": benchmark_pb2.TCM_DIAGNOSIS,
            "TONGUE_RECOGNITION": benchmark_pb2.TONGUE_RECOGNITION,
            "FACE_RECOGNITION": benchmark_pb2.FACE_RECOGNITION,
            "PULSE_RECOGNITION": benchmark_pb2.PULSE_RECOGNITION,
            "HEALTH_PLAN_GENERATION": benchmark_pb2.HEALTH_PLAN_GENERATION,
            "AGENT_COLLABORATION": benchmark_pb2.AGENT_COLLABORATION,
            "PRIVACY_VERIFICATION": benchmark_pb2.PRIVACY_VERIFICATION,
            "EDGE_PERFORMANCE": benchmark_pb2.EDGE_PERFORMANCE,
            "DIALECT_RECOGNITION": benchmark_pb2.DIALECT_RECOGNITION,
        }
        return task_map.get(task_type, benchmark_pb2.UNKNOWN)

    def _get_dataset_size(self, dataset_ids: List[str]) -> int:
        """
        获取数据集样本总数
        
        Args:
            dataset_ids: 数据集ID列表
            
        Returns:
            样本总数
        """
        total_size = 0
        for dataset_id in dataset_ids:
            if dataset_id in self.config.datasets:
                total_size += self.config.datasets[dataset_id].size
        return total_size

    def _generate_comparison_summary(
        self, comparison: benchmark_pb2.CompareBenchmarksResponse
    ) -> str:
        """
        生成比较总结
        
        Args:
            comparison: 比较结果
            
        Returns:
            比较总结文本
        """
        # 统计改进和退步的指标数量
        improved = 0
        degraded = 0
        
        for metric_name, result in comparison.metrics.items():
            metric_config = self.config.metrics.get(metric_name, {})
            higher_is_better = metric_config.get("higher_is_better", True)
            
            # 根据指标类型判断是改进还是退步
            if (higher_is_better and result.diff > 0) or (not higher_is_better and result.diff < 0):
                improved += 1
            elif (higher_is_better and result.diff < 0) or (not higher_is_better and result.diff > 0):
                degraded += 1
        
        # 案例比较统计
        baseline_only_correct = 0
        compare_only_correct = 0
        both_correct = 0
        both_wrong = 0
        
        for case in comparison.case_comparisons:
            if case.baseline_correct and case.compare_correct:
                both_correct += 1
            elif case.baseline_correct and not case.compare_correct:
                baseline_only_correct += 1
            elif not case.baseline_correct and case.compare_correct:
                compare_only_correct += 1
            else:
                both_wrong += 1
        
        # 生成总结
        summary = f"比较 {comparison.baseline_model} 与 {comparison.compare_model}:\n"
        summary += f"- 改进指标: {improved}, 退步指标: {degraded}\n"
        
        if comparison.case_comparisons:
            summary += f"- 案例分析: 双方正确 {both_correct}, 仅基线正确 {baseline_only_correct}, "
            summary += f"仅对比正确 {compare_only_correct}, 双方错误 {both_wrong}\n"
        
        # 总体结论
        if improved > degraded:
            summary += "- 总体结论: 对比模型相对基线模型有所改进"
        elif improved < degraded:
            summary += "- 总体结论: 对比模型相对基线模型有所退步"
        else:
            summary += "- 总体结论: 对比模型与基线模型表现相当"
            
        return summary