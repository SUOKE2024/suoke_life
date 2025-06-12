"""
算诊服务客户端

提供与算诊服务的通信接口，支持完整的中医算诊方法
"""

import asyncio
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

import aiohttp

from ...utils.exceptions import (
    CommunicationError,
    DiagnosisError,
    ServiceUnavailableError,
)
from ...utils.retry import retry_with_backoff
from ..base import BaseServiceClient
from ..config import get_settings
from .models import (
    CalculationError,
    CalculationRequest,
    CalculationResponse,
    CalculationType,
    PatientInfo,
)

logger = logging.getLogger(__name__)


class CalculationServiceClient(BaseServiceClient):
    """算诊服务客户端"""

    def __init__(self, base_url: Optional[str] = None):
        """初始化客户端"""
        if base_url is None:
            settings = get_settings()
            base_url = f"http://{settings.external_services.calculation_service.host}:{settings.external_services.calculation_service.port}"

        super().__init__(base_url)
        self.service_name = "calculation-service"

    @retry_with_backoff(max_retries=3)
    async def analyze_constitution(
        self,
        user_id: str,
        session_id: str,
        patient_info: PatientInfo,
        options: Optional[Dict[str, Any]] = None,
    ) -> CalculationResponse:
        """体质分析"""
        request = CalculationRequest(
            user_id=user_id,
            session_id=session_id,
            calculation_type=CalculationType.CONSTITUTION,
            patient_info=patient_info,
            options=options or {},
        )

        return await self._make_http_request("/api/v1/calculation/constitution", request)

    @retry_with_backoff(max_retries=3)
    async def analyze_ziwu_liuzhu(
        self,
        user_id: str,
        session_id: str,
        patient_info: PatientInfo,
        current_time: Optional[datetime] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> CalculationResponse:
        """子午流注分析"""
        analysis_params = {"current_time": (current_time or datetime.now()).isoformat()}

        request = CalculationRequest(
            user_id=user_id,
            session_id=session_id,
            calculation_type=CalculationType.ZIWU_LIUZHU,
            patient_info=patient_info,
            analysis_parameters=analysis_params,
            options=options or {},
        )

        return await self._make_http_request("/api/v1/calculation/ziwu-liuzhu", request)

    @retry_with_backoff(max_retries=3)
    async def analyze_wuyun_liuqi(
        self,
        user_id: str,
        session_id: str,
        patient_info: PatientInfo,
        analysis_year: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> CalculationResponse:
        """五运六气分析"""
        analysis_params = {"analysis_year": analysis_year or datetime.now().year}

        request = CalculationRequest(
            user_id=user_id,
            session_id=session_id,
            calculation_type=CalculationType.WUYUN_LIUQI,
            patient_info=patient_info,
            analysis_parameters=analysis_params,
            options=options or {},
        )

        return await self._make_http_request("/api/v1/calculation/wuyun-liuqi", request)

    @retry_with_backoff(max_retries=3)
    async def analyze_bagua(
        self,
        user_id: str,
        session_id: str,
        patient_info: PatientInfo,
        options: Optional[Dict[str, Any]] = None,
    ) -> CalculationResponse:
        """八卦分析"""
        request = CalculationRequest(
            user_id=user_id,
            session_id=session_id,
            calculation_type=CalculationType.BAGUA,
            patient_info=patient_info,
            options=options or {},
        )

        return await self._make_http_request("/api/v1/calculation/bagua", request)

    @retry_with_backoff(max_retries=3)
    async def comprehensive_analysis(
        self,
        user_id: str,
        session_id: str,
        patient_info: PatientInfo,
        include_all: bool = True,
        options: Optional[Dict[str, Any]] = None,
    ) -> CalculationResponse:
        """综合算诊分析"""
        analysis_params = {
            "include_constitution": include_all,
            "include_ziwu_liuzhu": include_all,
            "include_wuyun_liuqi": include_all,
            "include_bagua": include_all,
        }

        request = CalculationRequest(
            user_id=user_id,
            session_id=session_id,
            calculation_type=CalculationType.COMPREHENSIVE,
            patient_info=patient_info,
            analysis_parameters=analysis_params,
            options=options or {},
        )

        return await self._make_http_request("/api/v1/calculation/comprehensive", request)

    # 向后兼容的方法
    @retry_with_backoff(max_retries=3)
    async def calculate_diagnosis(
        self, diagnosis_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        进行算诊计算（向后兼容方法）

        Args:
            diagnosis_data: 诊断数据
            metadata: 可选的元数据

        Returns:
            计算结果
        """
        try:
            # 构造兼容的请求
            request_data = {
                "diagnosis_data": diagnosis_data,
                "metadata": metadata or {},
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/calculate",
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        error_text = await response.text()
                        raise CommunicationError(f"算诊计算失败: {error_text}")

        except Exception as e:
            logger.error(f"算诊计算错误: {e}")
            raise CommunicationError(f"算诊服务通信错误: {e}")

    async def _make_http_request(
        self, endpoint: str, request: CalculationRequest
    ) -> CalculationResponse:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(
                    url,
                    json=request.model_dump(),
                    headers={"Content-Type": "application/json"},
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return CalculationResponse(**data)
                    else:
                        error_text = await response.text()
                        logger.error(f"算诊服务请求失败: {response.status} - {error_text}")
                        raise DiagnosisError(f"算诊服务请求失败: {response.status}")

        except asyncio.TimeoutError:
            logger.error(f"算诊服务请求超时: {url}")
            raise ServiceUnavailableError("算诊服务请求超时")
        except aiohttp.ClientError as e:
            logger.error(f"算诊服务连接错误: {e}")
            raise ServiceUnavailableError(f"算诊服务连接错误: {e}")
        except Exception as e:
            logger.error(f"算诊服务请求异常: {e}")
            raise DiagnosisError(f"算诊服务请求异常: {e}")

    async def get_calculation_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取用户的算诊历史记录

        Args:
            user_id: 用户ID
            limit: 返回记录数限制

        Returns:
            历史记录列表
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/v1/history/{user_id}",
                    params={"limit": limit},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise CommunicationError(f"获取算诊历史失败: {error_text}")

        except Exception as e:
            logger.error(f"获取算诊历史错误: {e}")
            raise CommunicationError(f"算诊服务通信错误: {e}")

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"{self.base_url}/health") as response:
                    return response.status == 200
        except Exception as e:
            logger.warning(f"算诊服务健康检查失败: {e}")
            return False

    async def get_service_info(self) -> Dict[str, Any]:
        """获取服务信息"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(f"{self.base_url}/") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"status": "error", "message": f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"获取算诊服务信息失败: {e}")
            return {"status": "error", "message": str(e)}


# 全局客户端实例（向后兼容）
_calculation_client: Optional[CalculationServiceClient] = None


async def get_calculation_client() -> CalculationServiceClient:
    """获取算诊服务客户端实例"""
    global _calculation_client
    if _calculation_client is None:
        _calculation_client = CalculationServiceClient()
    return _calculation_client


async def close_calculation_client():
    """关闭算诊服务客户端"""
    global _calculation_client
    if _calculation_client is not None:
        await _calculation_client.close()
        _calculation_client = None
