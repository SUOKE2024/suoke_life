"""
SuokeBench gRPC服务实现
"""

import logging

import grpc

from api.grpc import benchmark_pb2, benchmark_pb2_grpc
from internal.benchmark.benchmark_service import BenchmarkService as BenchEngine
from internal.benchmark.model_interface import model_registry
from internal.evaluation.report_generator import ReportGenerator
from internal.metrics.basic_metrics import register_basic_metrics
from internal.suokebench.config import BenchConfig

# 初始化基础指标
register_basic_metrics()

# 初始化报告生成器
report_generator = ReportGenerator()

logger = logging.getLogger(__name__)


class SuokeBenchGrpcService(benchmark_pb2_grpc.BenchmarkServiceServicer):
    """
    SuokeBench gRPC服务实现
    """

    def __init__(self, config: BenchConfig):
        """
        初始化gRPC服务

        Args:
            config: 服务配置
        """
        self.config = config
        self.benchmark_engine = BenchEngine(config)
        logger.info("SuokeBench gRPC服务初始化完成")

    def RunBenchmark(
        self, request: benchmark_pb2.RunBenchmarkRequest, context: grpc.ServicerContext
    ) -> benchmark_pb2.RunBenchmarkResponse:
        """
        运行基准测试
        """
        try:
            logger.info(f"接收到运行基准测试请求: {request.benchmark_id}, {request.model_id}:{request.model_version}")

            # 运行基准测试
            run_id = self.benchmark_engine.run_benchmark(
                benchmark_id=request.benchmark_id,
                model_id=request.model_id,
                model_version=request.model_version,
                parameters=dict(request.parameters.items()),
            )

            logger.info(f"基准测试启动成功: {run_id}")

            return benchmark_pb2.RunBenchmarkResponse(
                run_id=run_id,
                status="RUNNING",
                message="基准测试已成功启动",
            )
        except Exception as e:
            logger.error(f"运行基准测试失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"运行基准测试失败: {str(e)}")
            return benchmark_pb2.RunBenchmarkResponse(
                status="ERROR",
                message=f"运行基准测试失败: {str(e)}",
            )

    def GetBenchmarkResult(
        self, request: benchmark_pb2.GetBenchmarkResultRequest, context: grpc.ServicerContext
    ) -> benchmark_pb2.GetBenchmarkResultResponse:
        """
        获取基准测试结果
        """
        try:
            logger.info(f"接收到获取基准测试结果请求: {request.run_id}")

            # 获取结果
            result = self.benchmark_engine.get_benchmark_result(request.run_id)

            if not result:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"找不到运行ID: {request.run_id}")
                return benchmark_pb2.GetBenchmarkResultResponse()

            # 构建响应
            response = benchmark_pb2.GetBenchmarkResultResponse(
                run_id=result["run_id"],
                benchmark_id=result["benchmark_id"],
                model_id=result["model_id"],
                model_version=result["model_version"],
                status=result["status"],
                task=result["task"],
                created_at=result["created_at"],
                completed_at=result["completed_at"] or "",
            )

            # 添加指标
            for name, metric in result["metrics"].items():
                response.metrics[name].CopyFrom(self._convert_metric(name, metric))

            # 如果需要，添加样本详情
            if request.include_details and "samples" in result:
                for sample in result["samples"]:
                    response.samples.append(self._convert_sample(sample))

            logger.info(f"成功获取基准测试结果: {request.run_id}")
            return response
        except Exception as e:
            logger.error(f"获取基准测试结果失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"获取基准测试结果失败: {str(e)}")
            return benchmark_pb2.GetBenchmarkResultResponse()

    def ListBenchmarks(
        self, request: benchmark_pb2.ListBenchmarksRequest, context: grpc.ServicerContext
    ) -> benchmark_pb2.ListBenchmarksResponse:
        """
        列出可用的基准测试
        """
        try:
            logger.info("接收到列出基准测试请求")

            # 获取基准测试列表
            benchmarks = self.benchmark_engine.list_benchmarks(
                task_filter=request.task_filter or None,
                tag=request.tag or None,
            )

            # 构建响应
            response = benchmark_pb2.ListBenchmarksResponse()
            for bench in benchmarks:
                benchmark_info = benchmark_pb2.BenchmarkInfo(
                    id=bench["id"],
                    name=bench["name"],
                    description=bench["description"],
                    task=bench["task"],
                    tags=bench["tags"],
                )

                # 添加支持的指标
                benchmark_info.metrics.extend(bench["metrics"])

                # 添加支持的参数
                for param_name, param in bench["parameters"].items():
                    param_info = benchmark_pb2.ParameterInfo(
                        name=param_name,
                        description=param.get("description", ""),
                        default_value=param.get("default", ""),
                    )
                    benchmark_info.parameters.append(param_info)

                response.benchmarks.append(benchmark_info)

            logger.info(f"成功列出 {len(response.benchmarks)} 个基准测试")
            return response
        except Exception as e:
            logger.error(f"列出基准测试失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"列出基准测试失败: {str(e)}")
            return benchmark_pb2.ListBenchmarksResponse()

    def CompareBenchmarks(
        self, request: benchmark_pb2.CompareBenchmarksRequest, context: grpc.ServicerContext
    ) -> benchmark_pb2.CompareBenchmarksResponse:
        """
        比较基准测试结果
        """
        try:
            logger.info(f"接收到比较基准测试请求: {request.baseline_run_id} vs {request.compare_run_id}")

            # 执行比较
            comparison = self.benchmark_engine.compare_benchmarks(
                baseline_run_id=request.baseline_run_id,
                compare_run_id=request.compare_run_id,
            )

            if not comparison:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("找不到一个或多个运行ID")
                return benchmark_pb2.CompareBenchmarksResponse()

            # 构建响应
            response = benchmark_pb2.CompareBenchmarksResponse(
                baseline_model=f"{comparison['baseline_model']['id']}:{comparison['baseline_model']['version']}",
                compare_model=f"{comparison['compare_model']['id']}:{comparison['compare_model']['version']}",
                summary=comparison["summary"],
            )

            # 添加指标比较
            for name, metric in comparison["metrics"].items():
                response.metrics[name].CopyFrom(self._convert_metric_comparison(name, metric))

            # 添加样本比较
            for case in comparison["case_comparisons"]:
                case_comparison = benchmark_pb2.CaseComparison(
                    id=case["id"],
                    input=case["input"],
                    expected=case["expected"],
                    baseline_output=case["baseline_output"],
                    compare_output=case["compare_output"],
                    baseline_correct=case["baseline_correct"],
                    compare_correct=case["compare_correct"],
                )
                response.case_comparisons.append(case_comparison)

            logger.info("成功比较基准测试结果")
            return response
        except Exception as e:
            logger.error(f"比较基准测试失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"比较基准测试失败: {str(e)}")
            return benchmark_pb2.CompareBenchmarksResponse()

    def GenerateReport(
        self, request: benchmark_pb2.GenerateReportRequest, context: grpc.ServicerContext
    ) -> benchmark_pb2.GenerateReportResponse:
        """
        生成评测报告
        """
        try:
            logger.info(f"接收到生成报告请求: {request.run_id}, 格式: {request.format}")

            # 首先获取测试结果
            result = self.benchmark_engine.get_benchmark_result(
                request.run_id, include_details=request.include_samples
            )

            if not result:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"找不到运行ID: {request.run_id}")
                return benchmark_pb2.GenerateReportResponse()

            # 生成报告
            report_path = report_generator.generate_report(
                result=result,
                format=request.format,
                include_samples=request.include_samples,
                include_metrics=list(request.metrics) if request.metrics else None,
            )

            if not report_path:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("生成报告失败")
                return benchmark_pb2.GenerateReportResponse()

            # 构建响应
            base_url = "/reports/"
            filename = report_path.split("/")[-1]
            report_url = f"{base_url}{filename}"

            return benchmark_pb2.GenerateReportResponse(
                report_url=report_url,
                message="报告已生成",
            )
        except Exception as e:
            logger.error(f"生成报告失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"生成报告失败: {str(e)}")
            return benchmark_pb2.GenerateReportResponse()

    def RegisterModel(
        self, request: benchmark_pb2.RegisterModelRequest, context: grpc.ServicerContext
    ) -> benchmark_pb2.RegisterModelResponse:
        """
        注册模型
        """
        try:
            logger.info(f"接收到注册模型请求: {request.model_id}:{request.model_version}")

            # 转换模型配置
            model_config = dict(request.model_config.items())

            # 注册模型
            model_registry.register_model(
                model_id=request.model_id,
                model_version=request.model_version,
                model_type=request.model_type,
                model_config=model_config,
            )

            logger.info(f"模型注册成功: {request.model_id}:{request.model_version}")

            return benchmark_pb2.RegisterModelResponse(
                status="success",
                message=f"模型 {request.model_id}:{request.model_version} 注册成功",
            )
        except Exception as e:
            logger.error(f"注册模型失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"注册模型失败: {str(e)}")
            return benchmark_pb2.RegisterModelResponse(
                status="error",
                message=f"注册模型失败: {str(e)}",
            )

    def ListModels(
        self, request: benchmark_pb2.ListModelsRequest, context: grpc.ServicerContext
    ) -> benchmark_pb2.ListModelsResponse:
        """
        列出已注册模型
        """
        try:
            logger.info("接收到列出模型请求")

            # 获取模型列表
            models = model_registry.list_models()

            # 构建响应
            response = benchmark_pb2.ListModelsResponse()
            for model in models:
                model_info = benchmark_pb2.ModelInfo(
                    model_id=model["model_id"],
                    model_version=model["model_version"],
                )
                response.models.append(model_info)

            logger.info(f"成功列出 {len(response.models)} 个模型")
            return response
        except Exception as e:
            logger.error(f"列出模型失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"列出模型失败: {str(e)}")
            return benchmark_pb2.ListModelsResponse()

    def UnregisterModel(
        self, request: benchmark_pb2.UnregisterModelRequest, context: grpc.ServicerContext
    ) -> benchmark_pb2.UnregisterModelResponse:
        """
        注销模型
        """
        try:
            logger.info(f"接收到注销模型请求: {request.model_id}:{request.model_version}")

            # 注销模型
            success = model_registry.unregister_model(
                model_id=request.model_id,
                model_version=request.model_version,
            )

            if not success:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"找不到模型: {request.model_id}:{request.model_version}")
                return benchmark_pb2.UnregisterModelResponse(
                    status="error",
                    message=f"找不到模型: {request.model_id}:{request.model_version}",
                )

            logger.info(f"模型注销成功: {request.model_id}:{request.model_version}")

            return benchmark_pb2.UnregisterModelResponse(
                status="success",
                message=f"模型 {request.model_id}:{request.model_version} 注销成功",
            )
        except Exception as e:
            logger.error(f"注销模型失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"注销模型失败: {str(e)}")
            return benchmark_pb2.UnregisterModelResponse(
                status="error",
                message=f"注销模型失败: {str(e)}",
            )

    def GetRunStatus(
        self, request: benchmark_pb2.GetRunStatusRequest, context: grpc.ServicerContext
    ) -> benchmark_pb2.GetRunStatusResponse:
        """
        获取运行状态
        """
        try:
            logger.info(f"接收到获取运行状态请求: {request.run_id}")

            # 获取状态
            status = self.benchmark_engine.get_run_status(request.run_id)

            if not status:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"找不到运行ID: {request.run_id}")
                return benchmark_pb2.GetRunStatusResponse()

            return benchmark_pb2.GetRunStatusResponse(
                run_id=status["run_id"],
                status=status["status"],
                progress=status["progress"],
                message=status["message"],
                started_at=status["started_at"],
                updated_at=status["updated_at"],
            )
        except Exception as e:
            logger.error(f"获取运行状态失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"获取运行状态失败: {str(e)}")
            return benchmark_pb2.GetRunStatusResponse()

    def DeleteRun(
        self, request: benchmark_pb2.DeleteRunRequest, context: grpc.ServicerContext
    ) -> benchmark_pb2.DeleteRunResponse:
        """
        删除评测记录
        """
        try:
            logger.info(f"接收到删除评测记录请求: {request.run_id}")

            # 删除评测记录
            success = self.benchmark_engine.delete_run(request.run_id)

            if not success:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"找不到运行ID: {request.run_id}")
                return benchmark_pb2.DeleteRunResponse(
                    status="error",
                    message=f"找不到运行ID: {request.run_id}",
                )

            logger.info(f"评测记录删除成功: {request.run_id}")

            return benchmark_pb2.DeleteRunResponse(
                status="success",
                message=f"评测记录 {request.run_id} 已成功删除",
            )
        except Exception as e:
            logger.error(f"删除评测记录失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"删除评测记录失败: {str(e)}")
            return benchmark_pb2.DeleteRunResponse(
                status="error",
                message=f"删除评测记录失败: {str(e)}",
            )

    def GetHistory(
        self, request: benchmark_pb2.GetHistoryRequest, context: grpc.ServicerContext
    ) -> benchmark_pb2.GetHistoryResponse:
        """
        获取评测历史
        """
        try:
            logger.info("接收到获取评测历史请求")

            # 获取历史记录
            history = self.benchmark_engine.get_history(
                benchmark_id=request.benchmark_id or None,
                model_id=request.model_id or None,
                limit=request.limit or 10,
            )

            # 构建响应
            response = benchmark_pb2.GetHistoryResponse()
            for item in history:
                history_item = benchmark_pb2.HistoryItem(
                    run_id=item["run_id"],
                    benchmark_id=item["benchmark_id"],
                    model_id=item["model_id"],
                    model_version=item["model_version"],
                    status=item["status"],
                    created_at=item["created_at"],
                    completed_at=item["completed_at"] or "",
                )

                # 添加指标摘要
                if "metrics_summary" in item:
                    for metric_name, metric_value in item["metrics_summary"].items():
                        history_item.metrics_summary[metric_name] = metric_value

                response.history.append(history_item)

            logger.info(f"成功获取 {len(response.history)} 条评测历史")
            return response
        except Exception as e:
            logger.error(f"获取评测历史失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"获取评测历史失败: {str(e)}")
            return benchmark_pb2.GetHistoryResponse()

    def _convert_metric(self, name: str, metric: dict) -> benchmark_pb2.MetricInfo:
        """
        转换指标信息为gRPC消息
        """
        return benchmark_pb2.MetricInfo(
            name=name,
            display_name=metric.get("display_name", name),
            value=float(metric.get("value", 0)),
            threshold=float(metric.get("threshold", 0)),
            pass_=metric.get("pass", False),
            higher_is_better=metric.get("higher_is_better", True),
            unit=metric.get("unit", ""),
        )

    def _convert_sample(self, sample: dict) -> benchmark_pb2.SampleResult:
        """
        转换样本结果为gRPC消息
        """
        result = benchmark_pb2.SampleResult(
            id=sample["id"],
            input=sample["input"],
            expected=sample["expected"],
            actual=sample["actual"],
            correct=sample["correct"],
        )

        # 添加分数
        if "scores" in sample:
            for name, value in sample["scores"].items():
                result.scores[name] = float(value)

        return result

    def _convert_metric_comparison(self, name: str, metric: dict) -> benchmark_pb2.MetricComparison:
        """
        转换指标比较为gRPC消息
        """
        return benchmark_pb2.MetricComparison(
            name=name,
            display_name=metric.get("display_name", name),
            baseline_value=float(metric.get("baseline_value", 0)),
            compare_value=float(metric.get("compare_value", 0)),
            difference=float(metric.get("difference", 0)),
            difference_percent=float(metric.get("difference_percent", 0)),
            higher_is_better=metric.get("higher_is_better", True),
            unit=metric.get("unit", ""),
        )
