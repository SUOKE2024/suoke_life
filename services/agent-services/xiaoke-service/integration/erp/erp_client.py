#!/usr/bin/env python

"""
ERP系统集成客户端
提供与医院ERP系统的对接接口
"""

import json
import logging
import os
import time
import uuid
from typing import Any

import backoff
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from internal.observability.metrics import metrics

logger = logging.getLogger(__name__)


class ERPError(Exception):
    """ERP系统错误"""

    def __init__(self, message, status_code=None, response=None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class ERPClient:
    """
    ERP系统集成客户端
    """

    def __init__(self, api_url=None, api_key=None, timeout=30, max_retries=3):
        """
        初始化ERP客户端

        Args:
            api_url: ERP系统API地址
            api_key: ERP系统API密钥
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.api_url = api_url or os.getenv("ERP_API_URL", "https://erp-api.suoke.life")
        self.api_key = api_key or os.getenv("ERP_API_KEY", "")
        self.timeout = timeout or int(os.getenv("ERP_TIMEOUT", "30"))
        self.max_retries = max_retries

        # 创建会话并配置重试策略
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=0.5,  # 指数级退避因子
            status_forcelist=[429, 500, 502, 503, 504],  # 触发重试的HTTP状态码
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        logger.info(
            f"初始化ERP客户端，API地址: {self.api_url}，超时时间: {self.timeout}秒"
        )

    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.RequestException, ERPError),
        max_tries=3,
        giveup=lambda e: getattr(e, "status_code", None) in [400, 401, 403, 404],
    )
    def check_doctor_availability(
        self, doctor_id: str, start_time: str, end_time: str
    ) -> dict[str, Any]:
        """
        检查医生可用性

        Args:
            doctor_id: 医生ID
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            医生可用性信息
        """
        logger.info(f"检查医生 {doctor_id} 在 {start_time} 至 {end_time} 的可用性")

        # 构建请求
        endpoint = f"/api/doctors/{doctor_id}/availability"
        payload = {"start_time": start_time, "end_time": end_time}

        # 调用API
        return self._make_api_request("GET", endpoint, payload)

    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.RequestException, ERPError),
        max_tries=3,
        giveup=lambda e: getattr(e, "status_code", None) in [400, 401, 403],
    )
    def create_appointment(
        self,
        doctor_id: str,
        patient_id: str,
        appointment_time: str,
        appointment_type: str,
        symptoms: str = "",
        metadata: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        创建预约

        Args:
            doctor_id: 医生ID
            patient_id: 患者ID
            appointment_time: 预约时间
            appointment_type: 预约类型
            symptoms: 症状描述
            metadata: 元数据

        Returns:
            预约信息
        """
        logger.info(f"为患者 {patient_id} 创建与医生 {doctor_id} 的预约")

        # 构建请求
        endpoint = "/api/appointments"
        payload = {
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "appointment_time": appointment_time,
            "appointment_type": appointment_type,
            "symptoms": symptoms,
            "metadata": metadata or {},
        }

        # 调用API
        return self._make_api_request("POST", endpoint, payload)

    @backoff.on_exception(
        backoff.expo, (requests.exceptions.RequestException, ERPError), max_tries=3
    )
    def check_inventory(self, product_ids: list[str]) -> dict[str, Any]:
        """
        检查库存

        Args:
            product_ids: 产品ID列表

        Returns:
            库存信息
        """
        logger.info(f"检查产品库存: {', '.join(product_ids)}")

        # 构建请求
        endpoint = "/api/inventory/check"
        payload = {"product_ids": product_ids}

        # 调用API
        return self._make_api_request("GET", endpoint, payload)

    @backoff.on_exception(
        backoff.expo, (requests.exceptions.RequestException, ERPError), max_tries=3
    )
    def update_order_status(
        self, order_id: str, status: str, metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        更新订单状态

        Args:
            order_id: 订单ID
            status: 新状态
            metadata: 元数据

        Returns:
            更新后的订单信息
        """
        logger.info(f"更新订单 {order_id} 的状态为 {status}")

        # 构建请求
        endpoint = f"/api/orders/{order_id}/status"
        payload = {
            "status": status,
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "metadata": metadata or {},
        }

        # 调用API
        return self._make_api_request("PUT", endpoint, payload)

    @backoff.on_exception(
        backoff.expo, (requests.exceptions.RequestException, ERPError), max_tries=3
    )
    def get_product_details(self, product_id: str) -> dict[str, Any]:
        """
        获取产品详情

        Args:
            product_id: 产品ID

        Returns:
            产品详情
        """
        logger.info(f"获取产品 {product_id} 的详情")

        # 构建请求
        endpoint = f"/api/products/{product_id}"

        # 调用API
        return self._make_api_request("GET", endpoint)

    @backoff.on_exception(
        backoff.expo, (requests.exceptions.RequestException, ERPError), max_tries=3
    )
    def create_order(
        self,
        user_id: str,
        products: list[dict[str, Any]],
        delivery_info: dict[str, Any] | None = None,
        payment_method: str = "PENDING",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        创建订单

        Args:
            user_id: 用户ID
            products: 产品列表，每个产品包含id、quantity、price等字段
            delivery_info: 配送信息
            payment_method: 支付方式
            metadata: 元数据

        Returns:
            订单信息
        """
        logger.info(f"为用户 {user_id} 创建订单，包含 {len(products)} 个产品")

        # 构建请求
        endpoint = "/api/orders"
        payload = {
            "user_id": user_id,
            "products": products,
            "delivery_info": delivery_info or {},
            "payment_method": payment_method,
            "metadata": metadata or {},
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }

        # 调用API
        return self._make_api_request("POST", endpoint, payload)

    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.RequestException, ERPError),
        max_tries=3,
        giveup=lambda e: getattr(e, "status_code", None) == 404,
    )
    def trace_product(
        self, product_id: str, batch_id: str | None = None, trace_token: str | None = None
    ) -> dict[str, Any]:
        """
        产品溯源

        Args:
            product_id: 产品ID
            batch_id: 批次ID（可选）
            trace_token: 溯源令牌（可选）

        Returns:
            溯源信息
        """
        logger.info(f"溯源产品 {product_id}，批次 {batch_id or '无'}")

        # 构建请求
        endpoint = "/api/products/trace"
        payload = {"product_id": product_id}

        if batch_id:
            payload["batch_id"] = batch_id
        if trace_token:
            payload["trace_token"] = trace_token

        # 调用API
        return self._make_api_request("GET", endpoint, payload)

    def _make_api_request(
        self, method: str, endpoint: str, payload=None
    ) -> dict[str, Any]:
        """
        发起API请求

        Args:
            method: HTTP方法
            endpoint: API端点
            payload: 请求数据

        Returns:
            API响应

        Raises:
            ERPError: ERP系统错误
        """
        # 构建完整URL
        url = f"{self.api_url}{endpoint}"

        # 构建请求头
        request_id = str(uuid.uuid4())
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "X-Request-ID": request_id,
            "User-Agent": "XiaokeServiceClient/1.0",
        }

        start_time = time.time()
        status = "success"

        try:
            # 发起请求
            if method.upper() == "GET":
                response = self.session.get(
                    url, headers=headers, params=payload, timeout=self.timeout
                )
            elif method.upper() == "POST":
                response = self.session.post(
                    url, headers=headers, json=payload, timeout=self.timeout
                )
            elif method.upper() == "PUT":
                response = self.session.put(
                    url, headers=headers, json=payload, timeout=self.timeout
                )
            elif method.upper() == "DELETE":
                response = self.session.delete(
                    url, headers=headers, params=payload, timeout=self.timeout
                )
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")

            # 记录请求延迟
            latency = time.time() - start_time
            endpoint_name = (
                endpoint.split("?")[0].split("/")[2]
                if len(endpoint.split("/")) > 2
                else endpoint
            )

            # 检查响应状态
            if response.status_code >= 400:
                status = "error"
                error_message = f"ERP API请求失败: {method} {endpoint}, 状态码: {response.status_code}"
                logger.error(error_message)

                try:
                    error_data = response.json()
                    error_message = f"{error_message}, 错误: {error_data.get('message', 'Unknown error')}"
                except (ValueError, KeyError):
                    error_data = {}

                raise ERPError(
                    message=error_message,
                    status_code=response.status_code,
                    response=error_data,
                )

            # 解析JSON响应
            response_data = response.json()

            # 记录API调用指标
            metrics.record_erp_api_call(endpoint_name, status, latency)

            return response_data

        except requests.RequestException as e:
            status = "error"
            latency = time.time() - start_time
            endpoint_name = (
                endpoint.split("?")[0].split("/")[2]
                if len(endpoint.split("/")) > 2
                else endpoint
            )

            # 记录API调用指标
            metrics.record_erp_api_call(endpoint_name, status, latency)

            logger.error(
                f"ERP API请求错误: {method} {endpoint}, 错误: {e!s}", exc_info=True
            )
            raise ERPError(message=f"ERP API请求失败: {e!s}")

        except (ValueError, json.JSONDecodeError) as e:
            status = "error"
            latency = time.time() - start_time
            endpoint_name = (
                endpoint.split("?")[0].split("/")[2]
                if len(endpoint.split("/")) > 2
                else endpoint
            )

            # 记录API调用指标
            metrics.record_erp_api_call(endpoint_name, status, latency)

            logger.error(
                f"ERP API响应解析错误: {method} {endpoint}, 错误: {e!s}",
                exc_info=True,
            )
            raise ERPError(message=f"ERP API响应解析失败: {e!s}")

        finally:
            if status == "success":
                logger.debug(
                    f"ERP API请求完成: {method} {endpoint}, 耗时: {time.time() - start_time:.3f}秒"
                )

    def __del__(self):
        """关闭会话"""
        try:
            if hasattr(self, "session") and self.session:
                self.session.close()
        except Exception:
            pass
