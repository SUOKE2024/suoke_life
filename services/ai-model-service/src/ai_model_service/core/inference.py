"""推理引擎"""

import time
from typing import Dict, Optional

import httpx
import structlog

from ..models.inference import InferenceRequest, InferenceResult
from ..utils.metrics import MetricsCollector

logger = structlog.get_logger(__name__)


class InferenceEngine:
    """推理引擎"""

    def __init__(self, metrics: Optional[MetricsCollector] = None) -> None:
        """初始化推理引擎

        Args:
            metrics: 指标收集器
        """
        self.metrics = metrics
        self.client = httpx.AsyncClient(timeout=60.0)

    async def inference(self, request: InferenceRequest) -> InferenceResult:
        """执行推理

        Args:
            request: 推理请求

        Returns:
            推理结果
        """
        start_time = time.time()

        try:
            logger.debug(
                "开始执行推理", request_id=request.request_id, model_id=request.model_id
            )

            # 获取模型端点URL（这里需要从模型管理器获取）
            endpoint_url = await self._get_model_endpoint(request.model_id)
            if not endpoint_url:
                raise ValueError(f"模型 {request.model_id} 的端点不可用")

            # 构建推理请求
            inference_payload = {
                "input_data": request.input_data,
                "parameters": request.parameters,
            }

            # 发送推理请求
            response = await self.client.post(
                f"{endpoint_url}/inference",
                json=inference_payload,
                timeout=request.timeout,
            )
            response.raise_for_status()

            # 解析响应
            result_data = response.json()
            processing_time = (time.time() - start_time) * 1000  # 转换为毫秒

            # 构建推理结果
            result = InferenceResult(
                request_id=request.request_id,
                model_id=request.model_id,
                result=result_data.get("result", {}),
                confidence=result_data.get("confidence", 0.0),
                processing_time=processing_time,
                model_version=result_data.get("model_version", "unknown"),
                resource_usage=result_data.get("resource_usage", {}),
                error_message=None,
            )

            # 记录指标
            if self.metrics:
                self.metrics.record_inference(
                    model_id=request.model_id,
                    status="success",
                    duration=processing_time / 1000,  # 转换为秒
                )

            logger.debug(
                "推理执行完成",
                request_id=request.request_id,
                processing_time=processing_time,
            )

            return result

        except httpx.TimeoutException:
            processing_time = (time.time() - start_time) * 1000
            error_message = f"推理请求超时 ({request.timeout}秒)"

            logger.error(
                "推理请求超时", request_id=request.request_id, timeout=request.timeout
            )

            if self.metrics:
                self.metrics.record_inference(
                    model_id=request.model_id,
                    status="timeout",
                    duration=processing_time / 1000,
                )

            return InferenceResult(
                request_id=request.request_id,
                model_id=request.model_id,
                result={},
                confidence=0.0,
                processing_time=processing_time,
                model_version="unknown",
                resource_usage={},
                error_message=error_message,
            )

        except httpx.HTTPStatusError as e:
            processing_time = (time.time() - start_time) * 1000
            error_message = f"推理请求失败: HTTP {e.response.status_code}"

            logger.error(
                "推理请求HTTP错误",
                request_id=request.request_id,
                status_code=e.response.status_code,
                response_text=e.response.text,
            )

            if self.metrics:
                self.metrics.record_inference(
                    model_id=request.model_id,
                    status="http_error",
                    duration=processing_time / 1000,
                )

            return InferenceResult(
                request_id=request.request_id,
                model_id=request.model_id,
                result={},
                confidence=0.0,
                processing_time=processing_time,
                model_version="unknown",
                resource_usage={},
                error_message=error_message,
            )

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            error_message = f"推理执行异常: {str(e)}"

            logger.error("推理执行异常", request_id=request.request_id, error=str(e))

            if self.metrics:
                self.metrics.record_inference(
                    model_id=request.model_id,
                    status="error",
                    duration=processing_time / 1000,
                )

            return InferenceResult(
                request_id=request.request_id,
                model_id=request.model_id,
                result={},
                confidence=0.0,
                processing_time=processing_time,
                model_version="unknown",
                resource_usage={},
                error_message=error_message,
            )

    async def batch_inference(
        self, requests: list[InferenceRequest]
    ) -> list[InferenceResult]:
        """批量推理

        Args:
            requests: 推理请求列表

        Returns:
            推理结果列表
        """
        logger.info("开始批量推理", batch_size=len(requests))

        # 按模型ID分组
        model_groups: Dict[str, list[InferenceRequest]] = {}
        for request in requests:
            if request.model_id not in model_groups:
                model_groups[request.model_id] = []
            model_groups[request.model_id].append(request)

        # 并发执行推理
        results = []
        for model_id, model_requests in model_groups.items():
            model_results = await self._batch_inference_for_model(
                model_id, model_requests
            )
            results.extend(model_results)

        logger.info(
            "批量推理完成", batch_size=len(requests), results_count=len(results)
        )
        return results

    async def _batch_inference_for_model(
        self, model_id: str, requests: list[InferenceRequest]
    ) -> list[InferenceResult]:
        """为单个模型执行批量推理

        Args:
            model_id: 模型ID
            requests: 推理请求列表

        Returns:
            推理结果列表
        """
        try:
            endpoint_url = await self._get_model_endpoint(model_id)
            if not endpoint_url:
                # 如果端点不可用，返回错误结果
                return [
                    InferenceResult(
                        request_id=req.request_id,
                        model_id=req.model_id,
                        result={},
                        confidence=0.0,
                        processing_time=0.0,
                        model_version="unknown",
                        resource_usage={},
                        error_message=f"模型 {model_id} 的端点不可用",
                    )
                    for req in requests
                ]

            # 构建批量推理请求
            batch_payload = {
                "requests": [
                    {
                        "request_id": req.request_id,
                        "input_data": req.input_data,
                        "parameters": req.parameters,
                    }
                    for req in requests
                ]
            }

            start_time = time.time()

            # 发送批量推理请求
            response = await self.client.post(
                f"{endpoint_url}/batch_inference",
                json=batch_payload,
                timeout=max(req.timeout for req in requests),
            )
            response.raise_for_status()

            # 解析响应
            batch_results = response.json().get("results", [])
            processing_time = (time.time() - start_time) * 1000

            # 构建推理结果
            results = []
            for i, result_data in enumerate(batch_results):
                if i < len(requests):
                    request = requests[i]
                    result = InferenceResult(
                        request_id=request.request_id,
                        model_id=request.model_id,
                        result=result_data.get("result", {}),
                        confidence=result_data.get("confidence", 0.0),
                        processing_time=result_data.get(
                            "processing_time", processing_time / len(requests)
                        ),
                        model_version=result_data.get("model_version", "unknown"),
                        resource_usage=result_data.get("resource_usage", {}),
                        error_message=result_data.get("error_message"),
                    )
                    results.append(result)

            return results

        except Exception as e:
            logger.error("批量推理失败", model_id=model_id, error=str(e))

            # 返回错误结果
            return [
                InferenceResult(
                    request_id=req.request_id,
                    model_id=req.model_id,
                    result={},
                    confidence=0.0,
                    processing_time=0.0,
                    model_version="unknown",
                    resource_usage={},
                    error_message=f"批量推理失败: {str(e)}",
                )
                for req in requests
            ]

    async def _get_model_endpoint(self, model_id: str) -> str:
        """获取模型端点URL

        Args:
            model_id: 模型ID

        Returns:
            端点URL
        """
        # 这里应该从模型管理器获取端点信息
        # 目前返回模拟的端点URL
        return f"http://{model_id}-service.suoke-life.svc.cluster.local:8080"

    async def close(self) -> None:
        """关闭推理引擎"""
        await self.client.aclose()
        logger.info("推理引擎已关闭")
