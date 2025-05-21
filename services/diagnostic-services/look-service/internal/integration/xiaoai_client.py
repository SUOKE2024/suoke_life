#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小艾服务集成客户端模块

负责与小艾服务(xiaoai-service)进行通信，发送望诊分析结果，
并接收小艾服务的综合分析结果，实现中医四诊合参。
"""

import os
import time
import json
from enum import Enum
from typing import Dict, List, Any, Optional, Union
import uuid
import grpc
from structlog import get_logger

from api.grpc import look_service_pb2
from pkg.utils.exceptions import DependencyError, ThirdPartyServiceError, TimeoutError

# 由于没有提供xiaoai_service的proto文件，这里仅模拟导入
# 实际项目中应该导入正确的生成类
try:
    from services.agent_services.xiaoai_service.api.grpc import xiaoai_service_pb2
    from services.agent_services.xiaoai_service.api.grpc import xiaoai_service_pb2_grpc
    MOCK_XIAOAI = False
except ImportError:
    # 如果无法导入，使用模拟实现
    MOCK_XIAOAI = True
    

# 设置日志
logger = get_logger()


class AnalysisType(str, Enum):
    """分析类型枚举"""
    FACE = "face"          # 面色分析
    BODY = "body"          # 形体分析
    TONGUE = "tongue"      # 舌象分析
    INQUIRY = "inquiry"    # 问诊
    LISTENING = "listening" # 闻诊
    PALPATION = "palpation" # 切诊
    COMBINED = "combined"  # 四诊合参


class DiagnosisLevel(str, Enum):
    """诊断级别枚举"""
    PRIMARY = "primary"      # 初级诊断
    INTERMEDIATE = "intermediate"  # 中级诊断
    ADVANCED = "advanced"    # 高级诊断
    COMPREHENSIVE = "comprehensive"  # 综合诊断


class XiaoAiClient:
    """
    小艾服务客户端类
    
    负责与小艾服务进行通信，发送望诊分析结果并接收综合诊断结果。
    支持断路器模式和重试机制，确保通信的可靠性。
    """
    
    def __init__(
        self,
        server_address: str = None,
        timeout: int = 10,
        max_retries: int = 3,
        enable_circuit_breaker: bool = True,
        circuit_break_threshold: int = 5,
        circuit_recovery_time: int = 60
    ):
        """
        初始化小艾服务客户端
        
        Args:
            server_address: 服务器地址，如不提供则从配置中读取
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            enable_circuit_breaker: 是否启用断路器
            circuit_break_threshold: 断路器开启阈值
            circuit_recovery_time: 断路器恢复时间（秒）
        """
        from config.config import get_config
        
        config = get_config()
        self.server_address = server_address or config.get("integration.xiaoai.address", "localhost:50051")
        self.timeout = timeout or config.get("integration.xiaoai.timeout", 10)
        self.max_retries = max_retries or config.get("integration.xiaoai.max_retries", 3)
        
        # 断路器设置
        self.enable_circuit_breaker = enable_circuit_breaker
        self.circuit_break_threshold = circuit_break_threshold
        self.circuit_recovery_time = circuit_recovery_time
        self.failure_count = 0
        self.circuit_open = False
        self.last_failure_time = 0
        
        # 请求统计
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        
        # 创建gRPC通道和存根（如果不是模拟模式）
        if not MOCK_XIAOAI:
            try:
                self.channel = grpc.insecure_channel(self.server_address)
                self.stub = xiaoai_service_pb2_grpc.XiaoAiServiceStub(self.channel)
                logger.info("已连接到小艾服务", server_address=self.server_address)
            except Exception as e:
                logger.error("连接小艾服务失败", error=str(e), server_address=self.server_address)
                self.channel = None
                self.stub = None
        else:
            logger.warning("使用模拟小艾服务客户端")
            self.channel = None
            self.stub = None
            
        logger.info("小艾客户端初始化完成", 
                  server_address=self.server_address, 
                  timeout=self.timeout,
                  max_retries=self.max_retries,
                  circuit_breaker=self.enable_circuit_breaker)
    
    def _check_circuit_breaker(self):
        """
        检查断路器状态
        
        如果断路器打开，则根据恢复时间决定是否尝试半开状态
        
        Raises:
            DependencyError: 当断路器打开时
        """
        if not self.enable_circuit_breaker:
            return
            
        # 如果断路器打开
        if self.circuit_open:
            current_time = time.time()
            # 检查是否达到恢复时间
            if current_time - self.last_failure_time >= self.circuit_recovery_time:
                # 进入半开状态，允许一次尝试
                logger.info("断路器进入半开状态", 
                          last_failure=self.last_failure_time,
                          current_time=current_time)
                self.circuit_open = False
                self.failure_count = 0
            else:
                # 断路器仍然打开，拒绝请求
                raise DependencyError(
                    f"小艾服务断路器打开，请等待{self.circuit_recovery_time}秒后重试"
                )
    
    def _update_circuit_breaker(self, success: bool):
        """
        更新断路器状态
        
        Args:
            success: 请求是否成功
        """
        if not self.enable_circuit_breaker:
            return
            
        if success:
            # 请求成功，重置失败计数
            self.failure_count = 0
            self.circuit_open = False
        else:
            # 请求失败，增加失败计数
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            # 如果失败次数达到阈值，打开断路器
            if self.failure_count >= self.circuit_break_threshold:
                self.circuit_open = True
                logger.warning("断路器已打开", 
                             failure_count=self.failure_count,
                             threshold=self.circuit_break_threshold,
                             recovery_time=self.circuit_recovery_time)
    
    def send_face_analysis(
        self,
        user_id: str,
        analysis_id: str,
        face_color: str,
        features: List[Dict[str, Any]],
        organ_correlations: List[Dict[str, Any]],
        summary: str,
        detail_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发送面色分析结果到小艾服务
        
        Args:
            user_id: 用户ID
            analysis_id: 分析ID
            face_color: 面色
            features: 特征列表
            organ_correlations: 脏腑关联列表
            summary: 分析摘要
            detail_data: 详细分析数据（可选）
            
        Returns:
            小艾服务的响应结果
            
        Raises:
            DependencyError: 当服务不可用时
            ThirdPartyServiceError: 当服务返回错误时
            TimeoutError: 当请求超时时
        """
        return self._send_analysis(
            user_id=user_id,
            analysis_id=analysis_id,
            analysis_type=AnalysisType.FACE,
            primary_result=face_color,
            features=features,
            correlations=organ_correlations,
            summary=summary,
            detail_data=detail_data
        )
    
    def send_body_analysis(
        self,
        user_id: str,
        analysis_id: str,
        body_type: str,
        posture: str,
        features: List[Dict[str, Any]],
        summary: str,
        detail_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发送形体分析结果到小艾服务
        
        Args:
            user_id: 用户ID
            analysis_id: 分析ID
            body_type: 体型
            posture: 姿态
            features: 特征列表
            summary: 分析摘要
            detail_data: 详细分析数据（可选）
            
        Returns:
            小艾服务的响应结果
            
        Raises:
            DependencyError: 当服务不可用时
            ThirdPartyServiceError: 当服务返回错误时
            TimeoutError: 当请求超时时
        """
        combined_primary = f"{body_type}，{posture}"
        return self._send_analysis(
            user_id=user_id,
            analysis_id=analysis_id,
            analysis_type=AnalysisType.BODY,
            primary_result=combined_primary,
            features=features,
            correlations=[],  # 形体分析通常不直接关联脏腑
            summary=summary,
            detail_data=detail_data
        )
    
    def send_tongue_analysis(
        self,
        user_id: str,
        analysis_id: str,
        tongue_color: str,
        tongue_shape: str,
        coating_color: str,
        features: List[Dict[str, Any]],
        organ_correlations: List[Dict[str, Any]],
        summary: str,
        detail_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发送舌象分析结果到小艾服务
        
        Args:
            user_id: 用户ID
            analysis_id: 分析ID
            tongue_color: 舌色
            tongue_shape: 舌形
            coating_color: 苔色
            features: 特征列表
            organ_correlations: 脏腑关联列表
            summary: 分析摘要
            detail_data: 详细分析数据（可选）
            
        Returns:
            小艾服务的响应结果
            
        Raises:
            DependencyError: 当服务不可用时
            ThirdPartyServiceError: 当服务返回错误时
            TimeoutError: 当请求超时时
        """
        combined_primary = f"舌色：{tongue_color}，舌形：{tongue_shape}，苔色：{coating_color}"
        return self._send_analysis(
            user_id=user_id,
            analysis_id=analysis_id,
            analysis_type=AnalysisType.TONGUE,
            primary_result=combined_primary,
            features=features,
            correlations=organ_correlations,
            summary=summary,
            detail_data=detail_data
        )
    
    def _send_analysis(
        self,
        user_id: str,
        analysis_id: str,
        analysis_type: AnalysisType,
        primary_result: str,
        features: List[Dict[str, Any]],
        correlations: List[Dict[str, Any]],
        summary: str,
        detail_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发送分析结果到小艾服务的通用方法
        
        Args:
            user_id: 用户ID
            analysis_id: 分析ID
            analysis_type: 分析类型
            primary_result: 主要分析结果
            features: 特征列表
            correlations: 关联列表
            summary: 分析摘要
            detail_data: 详细分析数据（可选）
            
        Returns:
            小艾服务的响应结果
            
        Raises:
            DependencyError: 当服务不可用时
            ThirdPartyServiceError: 当服务返回错误时
            TimeoutError: 当请求超时时
        """
        self.request_count += 1
        
        # 检查断路器状态
        try:
            self._check_circuit_breaker()
        except DependencyError as e:
            logger.warning("请求被断路器拒绝", 
                         user_id=user_id, 
                         analysis_type=analysis_type)
            self.error_count += 1
            raise
            
        # 转换分析类型为字符串
        if isinstance(analysis_type, AnalysisType):
            analysis_type = analysis_type.value
            
        # 序列化详细数据
        detail_json = json.dumps(detail_data) if detail_data else None
        
        # 准备重试
        retries = 0
        last_error = None
        
        while retries <= self.max_retries:
            try:
                # 如果是模拟模式，返回模拟响应
                if MOCK_XIAOAI or self.stub is None:
                    response = self._mock_xiaoai_response(
                        user_id, analysis_id, analysis_type, primary_result, summary
                    )
                else:
                    # 构建请求
                    features_json = json.dumps(features)
                    correlations_json = json.dumps(correlations)
                    
                    # 创建请求对象
                    request = xiaoai_service_pb2.AnalysisDataRequest(
                        user_id=user_id,
                        analysis_id=analysis_id,
                        diagnosis_type=analysis_type,
                        primary_result=primary_result,
                        features=features_json,
                        correlations=correlations_json,
                        summary=summary,
                        detail_data=detail_json
                    )
                    
                    # 发送请求
                    response = self.stub.ReceiveAnalysisData(
                        request, timeout=self.timeout
                    )
                    
                    # 将响应转换为字典
                    response = {
                        'request_id': response.request_id,
                        'status': response.status,
                        'combined_diagnosis': response.combined_diagnosis,
                        'suggestions': list(response.suggestions),
                        'detail': json.loads(response.detail) if response.detail else {}
                    }
                
                # 请求成功，更新断路器状态
                self._update_circuit_breaker(True)
                self.success_count += 1
                
                logger.info("发送分析结果到小艾服务成功", 
                          user_id=user_id, 
                          analysis_type=analysis_type,
                          analysis_id=analysis_id)
                
                return response
                
            except grpc.RpcError as e:
                # gRPC错误处理
                if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                    last_error = TimeoutError(f"请求小艾服务超时: {str(e)}")
                elif e.code() == grpc.StatusCode.UNAVAILABLE:
                    last_error = DependencyError(f"小艾服务不可用: {str(e)}")
                else:
                    last_error = ThirdPartyServiceError(f"小艾服务返回错误: {str(e)}")
            except Exception as e:
                # 其他错误
                last_error = ThirdPartyServiceError(f"与小艾服务通信时发生错误: {str(e)}")
            
            # 记录重试
            retries += 1
            if retries <= self.max_retries:
                logger.warning("重试发送分析结果到小艾服务", 
                             retry=retries, 
                             max_retries=self.max_retries,
                             error=str(last_error))
                # 指数退避
                time.sleep(0.5 * (2 ** retries))
        
        # 所有重试失败，更新断路器状态
        self._update_circuit_breaker(False)
        self.error_count += 1
        
        logger.error("发送分析结果到小艾服务失败", 
                   user_id=user_id, 
                   analysis_type=analysis_type,
                   retries=retries,
                   error=str(last_error))
        
        # 抛出最后一个错误
        raise last_error
    
    def get_combined_diagnosis(
        self,
        user_id: str,
        diagnosis_level: Union[str, DiagnosisLevel] = DiagnosisLevel.COMPREHENSIVE
    ) -> Dict[str, Any]:
        """
        获取用户的综合诊断结果
        
        Args:
            user_id: 用户ID
            diagnosis_level: 诊断级别
            
        Returns:
            综合诊断结果
            
        Raises:
            DependencyError: 当服务不可用时
            ThirdPartyServiceError: 当服务返回错误时
            TimeoutError: 当请求超时时
        """
        self.request_count += 1
        
        # 检查断路器状态
        try:
            self._check_circuit_breaker()
        except DependencyError as e:
            logger.warning("请求被断路器拒绝", 
                         user_id=user_id, 
                         diagnosis_level=diagnosis_level)
            self.error_count += 1
            raise
            
        # 转换诊断级别为字符串
        if isinstance(diagnosis_level, DiagnosisLevel):
            diagnosis_level = diagnosis_level.value
            
        # 准备重试
        retries = 0
        last_error = None
        
        while retries <= self.max_retries:
            try:
                # 如果是模拟模式，返回模拟响应
                if MOCK_XIAOAI or self.stub is None:
                    response = self._mock_combined_diagnosis(user_id, diagnosis_level)
                else:
                    # 创建请求对象
                    request = xiaoai_service_pb2.CombinedDiagnosisRequest(
                        user_id=user_id,
                        diagnosis_level=diagnosis_level
                    )
                    
                    # 发送请求
                    response = self.stub.GetCombinedDiagnosis(
                        request, timeout=self.timeout
                    )
                    
                    # 将响应转换为字典
                    response = {
                        'request_id': response.request_id,
                        'diagnosis_level': response.diagnosis_level,
                        'constitution_types': list(response.constitution_types),
                        'primary_diagnosis': response.primary_diagnosis,
                        'detailed_diagnosis': response.detailed_diagnosis,
                        'recommendations': list(response.recommendations),
                        'detail': json.loads(response.detail) if response.detail else {}
                    }
                
                # 请求成功，更新断路器状态
                self._update_circuit_breaker(True)
                self.success_count += 1
                
                logger.info("获取综合诊断结果成功", 
                          user_id=user_id, 
                          diagnosis_level=diagnosis_level)
                
                return response
                
            except grpc.RpcError as e:
                # gRPC错误处理
                if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                    last_error = TimeoutError(f"请求小艾服务超时: {str(e)}")
                elif e.code() == grpc.StatusCode.UNAVAILABLE:
                    last_error = DependencyError(f"小艾服务不可用: {str(e)}")
                else:
                    last_error = ThirdPartyServiceError(f"小艾服务返回错误: {str(e)}")
            except Exception as e:
                # 其他错误
                last_error = ThirdPartyServiceError(f"与小艾服务通信时发生错误: {str(e)}")
            
            # 记录重试
            retries += 1
            if retries <= self.max_retries:
                logger.warning("重试获取综合诊断结果", 
                             retry=retries, 
                             max_retries=self.max_retries,
                             error=str(last_error))
                # 指数退避
                time.sleep(0.5 * (2 ** retries))
        
        # 所有重试失败，更新断路器状态
        self._update_circuit_breaker(False)
        self.error_count += 1
        
        logger.error("获取综合诊断结果失败", 
                   user_id=user_id, 
                   diagnosis_level=diagnosis_level,
                   retries=retries,
                   error=str(last_error))
        
        # 抛出最后一个错误
        raise last_error
    
    def _mock_xiaoai_response(
        self,
        user_id: str,
        analysis_id: str,
        analysis_type: str,
        primary_result: str,
        summary: str
    ) -> Dict[str, Any]:
        """
        生成模拟的小艾服务响应
        
        Args:
            user_id: 用户ID
            analysis_id: 分析ID
            analysis_type: 分析类型
            primary_result: 主要分析结果
            summary: 分析摘要
            
        Returns:
            模拟的响应结果
        """
        # 模拟处理延迟
        time.sleep(0.2)
        
        # 模拟服务不可用的情况（5%概率）
        if time.time() % 100 < 5:
            raise DependencyError("模拟的小艾服务暂时不可用")
        
        # 生成请求ID
        request_id = str(uuid.uuid4())
        
        # 根据分析类型生成不同的响应内容
        if analysis_type == AnalysisType.FACE.value:
            combined_diagnosis = "根据面色分析，检测到您面色偏红，眼白部分有血丝，舌苔薄黄，脉搏有力，可能为热证。"
            suggestions = [
                "建议保持情绪平和，避免过度紧张和劳累",
                "饮食宜清淡，多食新鲜蔬果，少食辛辣刺激性食物",
                "可适当食用菊花、决明子、绿茶等清热食物"
            ]
        elif analysis_type == AnalysisType.BODY.value:
            combined_diagnosis = "根据形体分析，您体型偏瘦，肌肉张力不足，腰背略弯，可能为气虚体质。"
            suggestions = [
                "建议适当进行力量训练，增强肌肉力量",
                "注意保持正确姿势，避免长时间低头和久坐",
                "饮食上宜温补，可多食大枣、山药、鸡肉等补气食物"
            ]
        elif analysis_type == AnalysisType.TONGUE.value:
            combined_diagnosis = "根据舌象分析，舌质淡红，舌苔薄白，舌体胖大有齿痕，可能为脾虚湿盛证。"
            suggestions = [
                "建议饮食规律，少食生冷，避免损伤脾胃",
                "可适当食用健脾祛湿的食物，如薏苡仁、山药、扁豆等",
                "保持适度运动，促进水湿代谢"
            ]
        else:
            combined_diagnosis = f"收到{analysis_type}分析数据，{primary_result}，需要更多诊断数据进行综合分析。"
            suggestions = ["请完成四诊数据采集，以获取更准确的诊断结果"]
        
        # 生成详细信息
        detail = {
            "analysis_received": True,
            "analysis_id": analysis_id,
            "user_id": user_id,
            "analysis_type": analysis_type,
            "received_at": int(time.time()),
            "analysis_factors": [
                {"factor": "主观情况", "value": "正常"},
                {"factor": "生活状态", "value": "良好"},
                {"factor": "睡眠质量", "value": "一般"}
            ]
        }
        
        # 返回模拟响应
        return {
            'request_id': request_id,
            'status': 'success',
            'combined_diagnosis': combined_diagnosis,
            'suggestions': suggestions,
            'detail': detail
        }
    
    def _mock_combined_diagnosis(
        self, 
        user_id: str, 
        diagnosis_level: str
    ) -> Dict[str, Any]:
        """
        生成模拟的综合诊断结果
        
        Args:
            user_id: 用户ID
            diagnosis_level: 诊断级别
            
        Returns:
            模拟的综合诊断结果
        """
        # 模拟处理延迟
        time.sleep(0.3)
        
        # 模拟服务不可用的情况（5%概率）
        if time.time() % 100 < 5:
            raise DependencyError("模拟的小艾服务暂时不可用")
        
        # 生成请求ID
        request_id = str(uuid.uuid4())
        
        # 根据诊断级别生成不同的响应内容
        if diagnosis_level == DiagnosisLevel.PRIMARY.value:
            constitution_types = ["阳虚质"]
            primary_diagnosis = "初步诊断为阳虚质，表现为畏寒怕冷，手足不温，面色偏白"
            detailed_diagnosis = "根据目前采集的信息，您属于阳虚体质，阳气不足，温煦功能减弱，易感寒邪"
            recommendations = [
                "建议保暖防寒，避免受凉",
                "可适当食用羊肉、生姜等温阳食物"
            ]
        elif diagnosis_level == DiagnosisLevel.INTERMEDIATE.value:
            constitution_types = ["阳虚质", "气虚质"]
            primary_diagnosis = "诊断为阳虚兼气虚，表现为畏寒怕冷，疲乏无力，少气懒言"
            detailed_diagnosis = (
                "综合分析您的望、闻、问、切四诊信息，您主要表现为阳虚兼气虚证。"
                "阳气不足导致温煦功能减弱，气虚导致推动无力，合并后表现为畏寒、乏力、倦怠等症状。"
            )
            recommendations = [
                "建议保暖防寒，适当运动增强体质",
                "饮食宜温热，可食用党参、黄芪、肉桂等补气温阳食物",
                "保持规律作息，避免过度劳累"
            ]
        elif diagnosis_level == DiagnosisLevel.ADVANCED.value or diagnosis_level == DiagnosisLevel.COMPREHENSIVE.value:
            constitution_types = ["阳虚质", "气虚质", "血瘀质"]
            primary_diagnosis = "诊断为阳气虚弱，气滞血瘀，表现为畏寒怕冷，疲乏无力，肢体麻木，舌暗有瘀点"
            detailed_diagnosis = (
                "通过四诊合参，全面分析您的体质状态，您属于阳虚、气虚兼有血瘀的复合体质。"
                "阳虚导致温煦不足，气虚使推动无力，进而导致血行不畅，出现血瘀症状。"
                "主要表现为怕冷畏寒，疲乏无力，肢体麻木刺痛，舌质暗淡有瘀点，脉沉细涩。"
                "这种体质状态若不及时调理，长期可能导致多种慢性疾病的发生。"
            )
            recommendations = [
                "建议保暖防寒，适当参加温和的有氧运动，如太极、散步等",
                "饮食宜温补，可食用桂圆、红枣、当归等补血活血食物",
                "避免熬夜，保持充足睡眠，减轻精神压力",
                "可在中医师指导下使用温阳补气、活血化瘀的中药调理",
                "定期进行健康检查，监测血液循环状况"
            ]
        else:
            constitution_types = ["未知体质"]
            primary_diagnosis = "诊断级别参数错误"
            detailed_diagnosis = f"不支持的诊断级别: {diagnosis_level}"
            recommendations = ["请使用正确的诊断级别参数"]
        
        # 生成详细信息
        detail = {
            "user_id": user_id,
            "diagnosis_level": diagnosis_level,
            "diagnosis_time": int(time.time()),
            "available_diagnosis_types": ["face", "body", "tongue", "inquiry"],
            "missing_diagnosis_types": ["listening", "palpation"],
            "confidence_score": 0.85
        }
        
        # 返回模拟响应
        return {
            'request_id': request_id,
            'diagnosis_level': diagnosis_level,
            'constitution_types': constitution_types,
            'primary_diagnosis': primary_diagnosis,
            'detailed_diagnosis': detailed_diagnosis,
            'recommendations': recommendations,
            'detail': detail
        }
    
    def get_client_stats(self) -> Dict[str, Any]:
        """
        获取客户端统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'server_address': self.server_address,
            'request_count': self.request_count,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'success_rate': (self.success_count / self.request_count * 100) if self.request_count > 0 else 0,
            'circuit_breaker': {
                'enabled': self.enable_circuit_breaker,
                'status': 'open' if self.circuit_open else 'closed',
                'failure_count': self.failure_count,
                'threshold': self.circuit_break_threshold,
                'recovery_time': self.circuit_recovery_time,
                'last_failure_time': self.last_failure_time
            }
        }
    
    def close(self):
        """关闭gRPC通道"""
        if self.channel:
            self.channel.close()
            logger.info("已关闭小艾服务客户端通道") 