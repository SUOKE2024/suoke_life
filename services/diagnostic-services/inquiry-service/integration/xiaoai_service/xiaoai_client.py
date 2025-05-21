#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
小艾服务客户端
用于与小艾服务(xiaoai-service)进行gRPC通信
提供重试机制、断路器和监控指标
"""

import asyncio
import logging
import grpc
import time
import os
from typing import Dict, List, Optional, Any, Tuple
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import pybreaker

# 导入生成的gRPC代码
from .xiaoai_pb2 import *
from .xiaoai_pb2_grpc import XiaoaiServiceStub

logger = logging.getLogger(__name__)

# 断路器实例
circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=30,
    exclude=[grpc.RpcError],  # 排除某些错误类型
    name="xiaoai_service"
)


class XiaoaiServiceClient:
    """小艾服务客户端"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化客户端
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.integration_config = config.get("integration", {}).get("xiaoai_service", {})
        
        # 获取服务地址
        self.service_host = self.integration_config.get("host", "localhost")
        self.service_port = self.integration_config.get("port", 50051)
        self.service_address = f"{self.service_host}:{self.service_port}"
        
        # 超时设置
        self.timeout_seconds = self.integration_config.get("timeout_seconds", 10)
        
        # 重试设置
        self.max_retries = self.integration_config.get("max_retries", 3)
        self.retry_delay_ms = self.integration_config.get("retry_delay_ms", 500)
        
        # 是否使用模拟模式
        self.use_mock = self.integration_config.get("mock_enabled", False)
        self.mock_delay_ms = self.integration_config.get("mock_delay_ms", 200)
        
        # 是否启用TLS/SSL
        self.use_tls = self.integration_config.get("use_tls", False)
        self.cert_path = self.integration_config.get("cert_path", "")
        
        # 检查是否为测试模式
        self.is_test_mode = os.environ.get("TEST_MODE", "false").lower() in ["true", "1", "yes"]
        
        # 客户端连接池
        self._channel = None
        self._stub = None
        
        logger.info(f"小艾服务客户端初始化完成: {self.service_address}, mock模式: {self.use_mock}")

    def setup_channel(self) -> None:
        """设置gRPC通道"""
        if self._channel is not None:
            return

        # 频道选项
        options = [
            ("grpc.max_receive_message_length", self.integration_config.get("max_message_size", 10485760)),
            ("grpc.max_send_message_length", self.integration_config.get("max_message_size", 10485760)),
            ("grpc.keepalive_time_ms", self.integration_config.get("keep_alive_time", 60000)),
            ("grpc.keepalive_timeout_ms", self.integration_config.get("keep_alive_timeout", 20000)),
        ]
        
        # 创建通道
        if self.use_tls and self.cert_path:
            # TLS安全连接
            with open(self.cert_path, "rb") as f:
                creds = grpc.ssl_channel_credentials(f.read())
            self._channel = grpc.aio.secure_channel(self.service_address, creds, options=options)
        else:
            # 不安全连接
            self._channel = grpc.aio.insecure_channel(self.service_address, options=options)
            
        # 创建存根
        self._stub = XiaoaiServiceStub(self._channel)
        
    async def close_channel(self) -> None:
        """关闭gRPC通道"""
        if self._channel is not None:
            await self._channel.close()
            self._channel = None
            self._stub = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(grpc.RpcError),
        reraise=True
    )
    @circuit_breaker
    async def get_inquiry_analysis(self, session_id: str, symptoms: List[Dict], tcm_patterns: List[Dict]) -> Dict:
        """
        获取问诊分析结果
        
        Args:
            session_id: 会话ID
            symptoms: 症状列表
            tcm_patterns: 中医证型列表
            
        Returns:
            分析结果字典
        """
        if self.use_mock:
            return await self._mock_get_inquiry_analysis(session_id, symptoms, tcm_patterns)
            
        try:
            start_time = time.time()
            self.setup_channel()
            
            # 构建请求
            symptom_protos = []
            for symptom in symptoms:
                symptom_proto = InquirySymptom(
                    symptom_name=symptom.get("symptom_name", ""),
                    severity=symptom.get("severity", "MODERATE"),
                    description=symptom.get("description", ""),
                    confidence=float(symptom.get("confidence", 0.8))
                )
                symptom_protos.append(symptom_proto)
                
            pattern_protos = []
            for pattern in tcm_patterns:
                pattern_proto = TCMPattern(
                    pattern_name=pattern.get("pattern_name", ""),
                    category=pattern.get("category", ""),
                    match_score=float(pattern.get("match_score", 0.0)),
                    description=pattern.get("description", "")
                )
                # 添加相关症状
                related_symptoms = pattern.get("related_symptoms", [])
                pattern_proto.related_symptoms.extend(related_symptoms)
                pattern_protos.append(pattern_proto)
                
            # 创建请求对象
            request = InquiryAnalysisRequest(
                session_id=session_id,
                symptoms=symptom_protos,
                tcm_patterns=pattern_protos
            )
            
            # 发送请求
            response = await self._stub.GetInquiryAnalysis(
                request,
                timeout=self.timeout_seconds
            )
            
            # 处理响应
            result = {
                "analysis_id": response.analysis_id,
                "inquiry_summary": response.inquiry_summary,
                "diagnosis_confidence": response.diagnosis_confidence,
                "recommended_actions": list(response.recommended_actions),
                "flags": list(response.flags)
            }
            
            # 记录和监控
            elapsed_time = time.time() - start_time
            logger.info(f"小艾服务调用成功 (GetInquiryAnalysis): session_id={session_id}, elapsed_time={elapsed_time:.3f}s")
            
            return result
            
        except grpc.RpcError as e:
            # gRPC错误处理
            status_code = e.code()
            elapsed_time = time.time() - start_time
            
            logger.error(f"小艾服务调用失败 (GetInquiryAnalysis): status={status_code.name}, "
                         f"details={e.details()}, elapsed_time={elapsed_time:.3f}s")
            
            # 根据错误类型处理
            if status_code == grpc.StatusCode.UNAVAILABLE:
                logger.warning("小艾服务不可用，尝试重试...")
                raise  # 触发重试
            elif status_code == grpc.StatusCode.DEADLINE_EXCEEDED:
                logger.warning("小艾服务响应超时，尝试重试...")
                raise  # 触发重试
            else:
                # 其他错误直接返回空结果
                return {
                    "analysis_id": "",
                    "inquiry_summary": "无法获取分析结果，服务异常",
                    "diagnosis_confidence": 0.0,
                    "recommended_actions": [],
                    "flags": ["SERVICE_ERROR"]
                }
                
        except Exception as e:
            # 其他异常处理
            elapsed_time = time.time() - start_time
            logger.exception(f"小艾服务调用发生未知异常 (GetInquiryAnalysis): error={str(e)}, "
                            f"elapsed_time={elapsed_time:.3f}s")
            
            return {
                "analysis_id": "",
                "inquiry_summary": "处理请求时发生错误",
                "diagnosis_confidence": 0.0,
                "recommended_actions": [],
                "flags": ["UNKNOWN_ERROR"]
            }
            
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(grpc.RpcError),
        reraise=True
    )
    @circuit_breaker
    async def sync_inquiry_status(self, session_id: str, status: str, metadata: Dict[str, Any]) -> bool:
        """
        同步问诊状态到小艾服务
        
        Args:
            session_id: 会话ID
            status: 状态，可以是 "STARTED", "IN_PROGRESS", "COMPLETED", "CANCELLED"
            metadata: 元数据字典
            
        Returns:
            是否同步成功
        """
        if self.use_mock:
            return await self._mock_sync_inquiry_status(session_id, status, metadata)
            
        try:
            start_time = time.time()
            self.setup_channel()
            
            # 构建请求
            metadata_items = []
            for key, value in metadata.items():
                # 如果值是复杂类型，转换为字符串
                if not isinstance(value, str):
                    value = str(value)
                    
                metadata_items.append(MetadataItem(key=key, value=value))
                
            # 创建请求对象
            request = InquiryStatusUpdate(
                session_id=session_id,
                status=status,
                metadata=metadata_items,
                timestamp=int(time.time())
            )
            
            # 发送请求
            response = await self._stub.SyncInquiryStatus(
                request,
                timeout=self.timeout_seconds
            )
            
            # 处理响应
            success = response.success
            
            # 记录和监控
            elapsed_time = time.time() - start_time
            logger.info(f"小艾服务调用成功 (SyncInquiryStatus): session_id={session_id}, "
                       f"status={status}, elapsed_time={elapsed_time:.3f}s")
            
            return success
            
        except grpc.RpcError as e:
            # gRPC错误处理
            status_code = e.code()
            elapsed_time = time.time() - start_time
            
            logger.error(f"小艾服务调用失败 (SyncInquiryStatus): status={status_code.name}, "
                        f"details={e.details()}, elapsed_time={elapsed_time:.3f}s")
            
            # 根据错误类型处理
            if status_code in [grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED]:
                logger.warning(f"小艾服务 {status_code.name}，尝试重试...")
                raise  # 触发重试
            else:
                # 其他错误直接返回失败
                return False
                
        except Exception as e:
            # 其他异常处理
            elapsed_time = time.time() - start_time
            logger.exception(f"小艾服务调用发生未知异常 (SyncInquiryStatus): error={str(e)}, "
                            f"elapsed_time={elapsed_time:.3f}s")
            
            return False
    
    # ---- 模拟数据实现 ----
    
    async def _mock_get_inquiry_analysis(self, session_id: str, symptoms: List[Dict], tcm_patterns: List[Dict]) -> Dict:
        """
        模拟获取问诊分析结果
        """
        # 模拟处理延迟
        await asyncio.sleep(self.mock_delay_ms / 1000.0)
        
        # 根据症状和证型生成模拟诊断
        symptom_names = [s.get("symptom_name", "") for s in symptoms]
        tcm_names = [p.get("pattern_name", "") for p in tcm_patterns]
        
        # 模拟分析信息
        summary = f"患者主要表现为{'、'.join(symptom_names[:3])}等症状"
        if tcm_names:
            summary += f"，符合{'、'.join(tcm_names[:2])}等证型特征"
        
        # 模拟建议
        actions = []
        if "头痛" in str(symptom_names):
            actions.append("建议进行头部检查")
        if "气虚" in str(tcm_names):
            actions.append("建议补气养血")
        if "湿热" in str(tcm_names):
            actions.append("建议清热祛湿")
        
        # 如果没有提取出足够的信息
        if not actions:
            actions = ["建议继续观察", "平衡饮食，规律作息"]
        
        return {
            "analysis_id": f"mock-analysis-{session_id}",
            "inquiry_summary": summary,
            "diagnosis_confidence": min(0.7 + 0.1 * len(symptoms), 0.95),
            "recommended_actions": actions,
            "flags": ["MOCK_DATA"]
        }
    
    async def _mock_sync_inquiry_status(self, session_id: str, status: str, metadata: Dict[str, Any]) -> bool:
        """
        模拟同步问诊状态
        """
        # 模拟处理延迟
        await asyncio.sleep(self.mock_delay_ms / 1000.0)
        
        # 简单记录状态变更
        logger.info(f"[模拟] 同步问诊状态: session_id={session_id}, status={status}")
        
        # 几乎总是成功
        return True