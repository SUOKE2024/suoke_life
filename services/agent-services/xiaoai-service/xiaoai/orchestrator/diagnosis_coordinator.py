#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四诊协调引擎
负责协调望、闻、问、切四诊服务，整合结果并生成辨证分析
"""

import logging
import time
import uuid
import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
import grpc

from ..agent.agent_manager import AgentManager
from ..repository.diagnosis_repository import DiagnosisRepository
from ..utils.config_loader import get_config
from ..utils.metrics import get_metrics_collector, track_service_call_metrics

# 导入生成的gRPC客户端
# 注意：这些导入会在proto文件编译后生成
try:
    import api.grpc.xiaoai_service_pb2 as xiaoai_pb2
    import api.grpc.xiaoai_service_pb2_grpc as xiaoai_pb2_grpc
    import api.grpc.look_service_pb2 as look_pb2
    import api.grpc.look_service_pb2_grpc as look_pb2_grpc
    import api.grpc.listen_service_pb2 as listen_pb2
    import api.grpc.listen_service_pb2_grpc as listen_pb2_grpc
    import api.grpc.inquiry_service_pb2 as inquiry_pb2
    import api.grpc.inquiry_service_pb2_grpc as inquiry_pb2_grpc
    import api.grpc.palpation_service_pb2 as palpation_pb2
    import api.grpc.palpation_service_pb2_grpc as palpation_pb2_grpc
except ImportError:
    logging.warning("无法导入gRPC客户端，请确保proto文件已编译")

logger = logging.getLogger(__name__)

class DiagnosisCoordinator:
    """四诊协调引擎，负责协调和整合各诊断服务的结果"""
    
    def __init__(self, 
                 agent_manager: AgentManager = None,
                 diagnosis_repository: DiagnosisRepository = None):
        """
        初始化四诊协调引擎
        
        Args:
            agent_manager: 智能体管理器，提供LLM推理能力
            diagnosis_repository: 诊断结果存储库
        """
        self.config = get_config()
        self.metrics = get_metrics_collector()
        
        # 设置依赖组件
        self.agent_manager = agent_manager or AgentManager()
        self.diagnosis_repository = diagnosis_repository or DiagnosisRepository()
        
        # 从配置中获取各诊断服务的连接信息
        self.services_config = {
            'looking': self.config.get_section('integrations.look_service'),
            'listening': self.config.get_section('integrations.listen_service'),
            'inquiry': self.config.get_section('integrations.inquiry_service'),
            'palpation': self.config.get_section('integrations.palpation_service')
        }
        
        # 从配置中获取四诊协调的配置
        self.coord_config = self.config.get_section('four_diagnosis')
        self.coordination_mode = self.coord_config.get('coordinator_mode', 'sequential')
        self.confidence_threshold = self.coord_config.get('confidence_threshold', 0.75)
        self.timeout_seconds = self.coord_config.get('timeout_seconds', 30)
        self.retry_count = self.coord_config.get('retry_count', 3)
        
        # 设置诊断服务的权重
        self.service_weights = {
            'looking': self.config.get_nested('four_diagnosis', 'looking', 'base_weight', default=1.0),
            'listening': self.config.get_nested('four_diagnosis', 'listening', 'base_weight', default=1.0),
            'inquiry': self.config.get_nested('four_diagnosis', 'inquiry', 'base_weight', default=1.5),
            'palpation': self.config.get_nested('four_diagnosis', 'palpation', 'base_weight', default=1.0)
        }
        
        # 诊断服务的启用状态
        self.service_enabled = {
            'looking': self.config.get_nested('four_diagnosis', 'looking', 'enabled', default=True),
            'listening': self.config.get_nested('four_diagnosis', 'listening', 'enabled', default=True),
            'inquiry': self.config.get_nested('four_diagnosis', 'inquiry', 'enabled', default=True),
            'palpation': self.config.get_nested('four_diagnosis', 'palpation', 'enabled', default=True)
        }
        
        # 初始化gRPC客户端
        self._init_grpc_clients()
        
        logger.info("四诊协调引擎初始化完成, 协调模式: %s", self.coordination_mode)
    
    def _init_grpc_clients(self):
        """初始化与各诊断服务的gRPC连接"""
        # 各服务的gRPC客户端
        self.grpc_clients = {}
        self.grpc_channels = {}
        
        # 尝试连接望诊服务
        if self.service_enabled['looking']:
            try:
                looking_config = self.services_config['looking']
                looking_addr = f"{looking_config.get('host', 'look-service')}:{looking_config.get('port', 50051)}"
                self.grpc_channels['looking'] = grpc.aio.insecure_channel(looking_addr)
                self.grpc_clients['looking'] = look_pb2_grpc.LookServiceStub(self.grpc_channels['looking'])
                logger.info("成功连接望诊服务: %s", looking_addr)
            except Exception as e:
                logger.error("连接望诊服务失败: %s", str(e))
        
        # 尝试连接闻诊服务
        if self.service_enabled['listening']:
            try:
                listening_config = self.services_config['listening']
                listening_addr = f"{listening_config.get('host', 'listen-service')}:{listening_config.get('port', 50052)}"
                self.grpc_channels['listening'] = grpc.aio.insecure_channel(listening_addr)
                self.grpc_clients['listening'] = listen_pb2_grpc.ListenServiceStub(self.grpc_channels['listening'])
                logger.info("成功连接闻诊服务: %s", listening_addr)
            except Exception as e:
                logger.error("连接闻诊服务失败: %s", str(e))
        
        # 尝试连接问诊服务
        if self.service_enabled['inquiry']:
            try:
                inquiry_config = self.services_config['inquiry']
                inquiry_addr = f"{inquiry_config.get('host', 'inquiry-service')}:{inquiry_config.get('port', 50053)}"
                self.grpc_channels['inquiry'] = grpc.aio.insecure_channel(inquiry_addr)
                self.grpc_clients['inquiry'] = inquiry_pb2_grpc.InquiryServiceStub(self.grpc_channels['inquiry'])
                logger.info("成功连接问诊服务: %s", inquiry_addr)
            except Exception as e:
                logger.error("连接问诊服务失败: %s", str(e))
        
        # 尝试连接切诊服务
        if self.service_enabled['palpation']:
            try:
                palpation_config = self.services_config['palpation']
                palpation_addr = f"{palpation_config.get('host', 'palpation-service')}:{palpation_config.get('port', 50054)}"
                self.grpc_channels['palpation'] = grpc.aio.insecure_channel(palpation_addr)
                self.grpc_clients['palpation'] = palpation_pb2_grpc.PalpationServiceStub(self.grpc_channels['palpation'])
                logger.info("成功连接切诊服务: %s", palpation_addr)
            except Exception as e:
                logger.error("连接切诊服务失败: %s", str(e))
    
    async def close(self):
        """关闭所有gRPC连接"""
        for service_name, channel in self.grpc_channels.items():
            try:
                await channel.close()
                logger.info("已关闭%s服务的gRPC连接", service_name)
            except Exception as e:
                logger.error("关闭%s服务gRPC连接失败: %s", service_name, str(e))
    
    async def coordinate_diagnosis(self, request: xiaoai_pb2.DiagnosisCoordinationRequest) -> xiaoai_pb2.DiagnosisCoordinationResponse:
        """
        协调四诊服务，整合结果并生成辨证分析
        
        Args:
            request: 诊断协调请求
        
        Returns:
            DiagnosisCoordinationResponse: 协调结果响应
        """
        coordination_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 记录请求信息
        logger.info("开始四诊协调，协调ID: %s, 用户ID: %s, 会话ID: %s", 
                   coordination_id, request.user_id, request.session_id)
        
        # 获取参与协调的服务列表
        included_services = self._get_included_services(request)
        if not included_services:
            logger.warning("未指定任何诊断服务，协调ID: %s", coordination_id)
            return self._create_empty_response(coordination_id)
        
        included_services_str = ",".join(included_services)
        
        try:
            # 根据协调模式选择执行方式
            if self.coordination_mode == 'parallel':
                diagnosis_results = await self._coordinate_parallel(request, included_services)
            else:  # sequential
                diagnosis_results = await self._coordinate_sequential(request, included_services)
            
            # 整合诊断结果
            syndrome_analysis = await self._analyze_syndromes(diagnosis_results)
            constitution_analysis = await self._analyze_constitution(diagnosis_results)
            
            # 生成健康建议
            recommendations = await self._generate_recommendations(
                diagnosis_results, syndrome_analysis, constitution_analysis
            )
            
            # 创建诊断总结
            summary = await self._generate_summary(
                diagnosis_results, syndrome_analysis, constitution_analysis
            )
            
            # 保存诊断结果
            await self.diagnosis_repository.save_diagnosis_coordination(
                coordination_id, request.user_id, request.session_id,
                diagnosis_results, syndrome_analysis, constitution_analysis,
                recommendations, summary
            )
            
            # 构建响应
            response = self._build_coordination_response(
                coordination_id, diagnosis_results, syndrome_analysis,
                constitution_analysis, recommendations, summary
            )
            
            # 记录协调完成
            duration = time.time() - start_time
            logger.info("四诊协调完成，协调ID: %s, 用户ID: %s, 耗时: %.2f秒", 
                       coordination_id, request.user_id, duration)
            
            # 记录指标
            self.metrics.track_diagnosis_coordination(
                self.coordination_mode, "success", included_services_str, duration
            )
            
            return response
            
        except Exception as e:
            # 记录错误
            duration = time.time() - start_time
            logger.error("四诊协调失败，协调ID: %s, 用户ID: %s, 错误: %s", 
                        coordination_id, request.user_id, str(e))
            
            # 记录指标
            self.metrics.track_diagnosis_coordination(
                self.coordination_mode, "failure", included_services_str, duration
            )
            
            # 返回基本响应
            return self._create_error_response(coordination_id, str(e))
    
    def _get_included_services(self, request) -> List[str]:
        """获取参与协调的服务列表"""
        included_services = []
        
        if request.include_looking and self.service_enabled['looking']:
            included_services.append('looking')
        
        if request.include_listening and self.service_enabled['listening']:
            included_services.append('listening')
        
        if request.include_inquiry and self.service_enabled['inquiry']:
            included_services.append('inquiry')
        
        if request.include_palpation and self.service_enabled['palpation']:
            included_services.append('palpation')
        
        return included_services
    
    async def _coordinate_parallel(self, request, included_services: List[str]) -> List[Dict[str, Any]]:
        """
        并行协调多个诊断服务
        
        Args:
            request: 诊断协调请求
            included_services: 参与协调的服务列表
        
        Returns:
            List[Dict[str, Any]]: 诊断结果列表
        """
        logger.info("使用并行模式进行四诊协调")
        
        # 准备每个服务的协调任务
        tasks = []
        for service in included_services:
            if service == 'looking' and request.looking_data:
                tasks.append(self._process_looking_diagnosis(request))
            elif service == 'listening' and request.listening_data:
                tasks.append(self._process_listening_diagnosis(request))
            elif service == 'inquiry' and request.inquiry_data:
                tasks.append(self._process_inquiry_diagnosis(request))
            elif service == 'palpation' and request.palpation_data:
                tasks.append(self._process_palpation_diagnosis(request))
        
        # 并行执行诊断
        results = []
        if tasks:
            # 设置超时
            timeout = self.timeout_seconds * len(tasks)
            try:
                completed_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 处理结果
                for result in completed_results:
                    if isinstance(result, Exception):
                        logger.error("诊断过程中出现错误: %s", str(result))
                    else:
                        results.append(result)
            
            except asyncio.TimeoutError:
                logger.warning("四诊协调超时，部分服务未能完成")
        
        return results
    
    async def _coordinate_sequential(self, request, included_services: List[str]) -> List[Dict[str, Any]]:
        """
        顺序协调多个诊断服务
        
        Args:
            request: 诊断协调请求
            included_services: 参与协调的服务列表
        
        Returns:
            List[Dict[str, Any]]: 诊断结果列表
        """
        logger.info("使用顺序模式进行四诊协调")
        
        results = []
        
        # 顺序执行每个诊断服务
        for service in included_services:
            try:
                if service == 'looking' and request.looking_data:
                    result = await self._process_looking_diagnosis(request)
                    results.append(result)
                
                elif service == 'listening' and request.listening_data:
                    result = await self._process_listening_diagnosis(request)
                    results.append(result)
                
                elif service == 'inquiry' and request.inquiry_data:
                    result = await self._process_inquiry_diagnosis(request)
                    results.append(result)
                
                elif service == 'palpation' and request.palpation_data:
                    result = await self._process_palpation_diagnosis(request)
                    results.append(result)
            
            except Exception as e:
                logger.error("%s诊断失败: %s", service, str(e))
                # 继续处理下一个诊断
        
        return results
    
    @track_service_call_metrics(service="look_service", method="AnalyzeTongueImage")
    async def _process_looking_diagnosis(self, request) -> Dict[str, Any]:
        """处理望诊服务"""
        logger.info("开始处理望诊数据")
        
        # 调用望诊服务
        if 'looking' not in self.grpc_clients:
            raise ValueError("望诊服务未连接")
        
        try:
            # 创建望诊服务请求
            image_type = look_pb2.AnalyzeImageRequest.ImageType.TONGUE
            if hasattr(request, 'image_type') and request.image_type:
                if request.image_type.lower() == 'face':
                    image_type = look_pb2.AnalyzeImageRequest.ImageType.FACE
                elif request.image_type.lower() == 'body':
                    image_type = look_pb2.AnalyzeImageRequest.ImageType.BODY
            
            look_request = look_pb2.AnalyzeImageRequest(
                user_id=request.user_id,
                session_id=request.session_id,
                image_data=request.looking_data,
                image_format="jpg",  # 假设是jpg格式，实际应该从请求中获取
                image_type=image_type,
                apply_preprocessing=True,
                include_visualization=True
            )
            
            # 调用服务，添加重试机制
            for retry in range(self.retry_count):
                try:
                    response = await self.grpc_clients['looking'].AnalyzeImage(
                        look_request, 
                        timeout=self.timeout_seconds
                    )
                    break
                except Exception as e:
                    if retry < self.retry_count - 1:
                        logger.warning("望诊服务调用失败，第%d次重试: %s", retry + 1, str(e))
                        await asyncio.sleep(0.5 * (retry + 1))  # 指数退避
                    else:
                        raise
            
            # 提取特征
            features = []
            for feature in response.features:
                features.append({
                    'name': feature.name,
                    'value': feature.value,
                    'confidence': feature.confidence,
                    'category': feature.category
                })
            
            # 转换为内部格式
            result = {
                'type': 'LOOKING',
                'diagnosis_id': response.diagnosis_id,
                'source_service': 'look-service',
                'confidence': response.confidence,
                'features': features,
                'detailed_result': response.detailed_result,
                'timestamp': response.timestamp or int(time.time())
            }
            
            # 如果有舌象分析结果
            if response.HasField('tongue_result'):
                tongue_result = response.tongue_result
                result['tongue_analysis'] = {
                    'tongue_color': tongue_result.tongue_color,
                    'tongue_shape': tongue_result.tongue_shape,
                    'coating_color': tongue_result.coating_color,
                    'coating_thickness': tongue_result.coating_thickness
                }
                
                # 添加证候相关性
                result['syndrome_correlations'] = [
                    {
                        'syndrome_name': corr.syndrome_name,
                        'correlation': corr.correlation,
                        'rationale': corr.rationale
                    }
                    for corr in tongue_result.syndrome_correlations
                ]
            
            logger.info("望诊数据处理完成，诊断ID: %s", response.diagnosis_id)
            return result
            
        except Exception as e:
            logger.error("望诊处理失败: %s", str(e))
            # 返回简化的错误结果
            return {
                'type': 'LOOKING',
                'diagnosis_id': str(uuid.uuid4()),
                'source_service': 'look-service',
                'confidence': 0.0,
                'features': [],
                'detailed_result': json.dumps({'error': str(e)}),
                'timestamp': int(time.time()),
                'error': str(e)
            }
    
    @track_service_call_metrics(service="listen_service", method="AnalyzeVoice")
    async def _process_listening_diagnosis(self, request) -> Dict[str, Any]:
        """处理闻诊服务"""
        logger.info("开始处理闻诊数据")
        
        # 调用闻诊服务
        if 'listening' not in self.grpc_clients:
            raise ValueError("闻诊服务未连接")
        
        try:
            # 创建闻诊服务请求
            listen_request = listen_pb2.AnalyzeVoiceRequest(
                user_id=request.user_id,
                session_id=request.session_id,
                audio_data=request.listening_data,
                audio_format="wav",  # 假设是wav格式，实际应该从请求中获取
                sample_rate=44100,   # 假设采样率，实际应该从请求中获取
                bit_depth=16,        # 假设位深度，实际应该从请求中获取
                channels=1,          # 假设单声道，实际应该从请求中获取
                detect_dialect=True  # 启用方言检测
            )
            
            # 调用服务，添加重试机制
            for retry in range(self.retry_count):
                try:
                    response = await self.grpc_clients['listening'].AnalyzeVoice(
                        listen_request, 
                        timeout=self.timeout_seconds
                    )
                    break
                except Exception as e:
                    if retry < self.retry_count - 1:
                        logger.warning("闻诊服务调用失败，第%d次重试: %s", retry + 1, str(e))
                        await asyncio.sleep(0.5 * (retry + 1))  # 指数退避
                    else:
                        raise
            
            # 提取特征
            features = []
            for feature in response.features:
                features.append({
                    'name': feature.name,
                    'value': feature.value,
                    'confidence': feature.confidence,
                    'category': feature.category
                })
            
            # 转换为内部格式
            result = {
                'type': 'LISTENING',
                'diagnosis_id': response.diagnosis_id,
                'source_service': 'listen-service',
                'confidence': response.confidence,
                'features': features,
                'detailed_result': response.detailed_result,
                'timestamp': response.timestamp or int(time.time())
            }
            
            # 如果有语音分析结果
            if response.HasField('voice_result'):
                voice_result = response.voice_result
                result['voice_analysis'] = {
                    'voice_quality': voice_result.voice_quality,
                    'voice_strength': voice_result.voice_strength,
                    'speech_rhythm': voice_result.speech_rhythm,
                    'dialect_detected': voice_result.dialect_detected,
                    'emotions': {k: v for k, v in voice_result.emotions.items()}
                }
                
                # 添加语音模式
                result['voice_patterns'] = [
                    {
                        'pattern_name': pattern.pattern_name,
                        'description': pattern.description,
                        'confidence': pattern.confidence
                    }
                    for pattern in voice_result.patterns
                ]
            
            logger.info("闻诊数据处理完成，诊断ID: %s", response.diagnosis_id)
            return result
            
        except Exception as e:
            logger.error("闻诊处理失败: %s", str(e))
            # 返回简化的错误结果
            return {
                'type': 'LISTENING',
                'diagnosis_id': str(uuid.uuid4()),
                'source_service': 'listen-service',
                'confidence': 0.0,
                'features': [],
                'detailed_result': json.dumps({'error': str(e)}),
                'timestamp': int(time.time()),
                'error': str(e)
            }
    
    @track_service_call_metrics(service="inquiry_service", method="ConductInquiry")
    async def _process_inquiry_diagnosis(self, request) -> Dict[str, Any]:
        """处理问诊服务"""
        logger.info("开始处理问诊数据")
        
        # 调用问诊服务
        if 'inquiry' not in self.grpc_clients:
            raise ValueError("问诊服务未连接")
        
        try:
            # 创建问诊服务请求
            inquiry_request = inquiry_pb2.InquiryRequest(
                user_id=request.user_id,
                session_id=request.session_id,
                user_message=request.inquiry_data,  # 假设是文本格式
                max_response_tokens=1024,
                include_analysis=True
            )
            
            # 调用服务，添加重试机制
            for retry in range(self.retry_count):
                try:
                    response = await self.grpc_clients['inquiry'].ConductInquiry(
                        inquiry_request, 
                        timeout=self.timeout_seconds
                    )
                    break
                except Exception as e:
                    if retry < self.retry_count - 1:
                        logger.warning("问诊服务调用失败，第%d次重试: %s", retry + 1, str(e))
                        await asyncio.sleep(0.5 * (retry + 1))  # 指数退避
                    else:
                        raise
            
            # 提取症状信息
            symptoms = []
            for symptom in response.symptoms:
                symptoms.append({
                    'name': symptom.name,
                    'description': symptom.description,
                    'severity': str(symptom.severity),
                    'duration_days': symptom.duration_days,
                    'confidence': symptom.confidence
                })
            
            # 提取辨证参考
            syndrome_references = []
            for syndrome in response.syndrome_references:
                syndrome_references.append({
                    'syndrome_name': syndrome.syndrome_name,
                    'relevance': syndrome.relevance,
                    'matching_symptoms': list(syndrome.matching_symptoms),
                    'description': syndrome.description
                })
            
            # 转换为内部格式
            result = {
                'type': 'INQUIRY',
                'diagnosis_id': response.inquiry_id,
                'source_service': 'inquiry-service',
                'confidence': response.confidence,
                'features': [{'name': s['name'], 'value': s['severity'], 'confidence': s['confidence'], 'category': 'symptom'} for s in symptoms],
                'symptoms': symptoms,
                'syndrome_references': syndrome_references,
                'detailed_result': response.detailed_analysis,
                'timestamp': response.timestamp or int(time.time())
            }
            
            logger.info("问诊数据处理完成，诊断ID: %s", response.inquiry_id)
            return result
            
        except Exception as e:
            logger.error("问诊处理失败: %s", str(e))
            # 返回简化的错误结果
            return {
                'type': 'INQUIRY',
                'diagnosis_id': str(uuid.uuid4()),
                'source_service': 'inquiry-service',
                'confidence': 0.0,
                'features': [],
                'detailed_result': json.dumps({'error': str(e)}),
                'timestamp': int(time.time()),
                'error': str(e)
            }
    
    @track_service_call_metrics(service="palpation_service", method="AnalyzePulse")
    async def _process_palpation_diagnosis(self, request) -> Dict[str, Any]:
        """处理切诊服务"""
        logger.info("开始处理切诊数据")
        
        # 调用切诊服务
        if 'palpation' not in self.grpc_clients:
            raise ValueError("切诊服务未连接")
        
        try:
            # 创建切诊服务请求 - 假设我们处理的是脉象数据
            pulse_request = palpation_pb2.PulseRequest(
                user_id=request.user_id,
                session_id=request.session_id,
                pulse_data=request.palpation_data,
                data_format="raw",  # 假设是原始数据格式
                sampling_rate=1000,  # 假设采样率
                include_detailed_analysis=True
            )
            
            # 调用服务，添加重试机制
            for retry in range(self.retry_count):
                try:
                    response = await self.grpc_clients['palpation'].AnalyzePulse(
                        pulse_request, 
                        timeout=self.timeout_seconds
                    )
                    break
                except Exception as e:
                    if retry < self.retry_count - 1:
                        logger.warning("切诊服务调用失败，第%d次重试: %s", retry + 1, str(e))
                        await asyncio.sleep(0.5 * (retry + 1))  # 指数退避
                    else:
                        raise
            
            # 提取特征
            features = []
            for feature in response.features:
                features.append({
                    'name': feature.name,
                    'value': feature.value,
                    'confidence': feature.confidence,
                    'category': feature.category
                })
            
            # 转换为内部格式
            result = {
                'type': 'PALPATION',
                'diagnosis_id': response.diagnosis_id,
                'source_service': 'palpation-service',
                'confidence': response.confidence,
                'features': features,
                'detailed_result': response.detailed_result,
                'timestamp': response.timestamp or int(time.time())
            }
            
            # 如果有脉象分析结果
            if response.HasField('pulse_result'):
                pulse_result = response.pulse_result
                result['pulse_analysis'] = {
                    'pulse_overall_type': pulse_result.pulse_overall_type,
                    'pulse_rhythm': pulse_result.pulse_rhythm,
                    'pulse_force': pulse_result.pulse_force,
                    'pulse_width': pulse_result.pulse_width,
                    'pulse_depth': pulse_result.pulse_depth
                }
                
                # 添加证候指征
                result['syndrome_indicators'] = [
                    {
                        'syndrome': indicator.syndrome,
                        'correlation': indicator.correlation,
                        'evidence': indicator.evidence
                    }
                    for indicator in pulse_result.syndrome_indicators
                ]
            
            logger.info("切诊数据处理完成，诊断ID: %s", response.diagnosis_id)
            return result
            
        except Exception as e:
            logger.error("切诊处理失败: %s", str(e))
            # 返回简化的错误结果
            return {
                'type': 'PALPATION',
                'diagnosis_id': str(uuid.uuid4()),
                'source_service': 'palpation-service',
                'confidence': 0.0,
                'features': [],
                'detailed_result': json.dumps({'error': str(e)}),
                'timestamp': int(time.time()),
                'error': str(e)
            }
    
    async def _analyze_syndromes(self, diagnosis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        基于诊断结果分析证型
        
        Args:
            diagnosis_results: 诊断结果列表
        
        Returns:
            Dict[str, Any]: 辨证分析结果
        """
        logger.info("开始分析证型")
        
        # 实际实现中，这里会使用LLM或规则引擎进行辨证分析
        # 这里返回模拟数据
        return {
            'primary_syndromes': [
                {
                    'name': '脾胃湿热证',
                    'confidence': 0.82,
                    'description': '脾胃湿热证是指湿热之邪侵犯脾胃所致。症见：脘腹胀满，疼痛，纳呆，恶心呕吐，口苦口粘，大便溏薄或秘结不爽，小便短黄，舌红苔黄腻，脉滑数。',
                    'related_features': ['舌苔黄腻', '脉滑数']
                }
            ],
            'secondary_syndromes': [
                {
                    'name': '肝郁气滞证',
                    'confidence': 0.65,
                    'description': '肝郁气滞证是指肝的疏泄功能失调，气机郁滞所致。症见：胁肋胀痛，情志抑郁，脘腹胀闷，嗳气叹息，食欲不振，嘈杂泛酸，咽喉梗塞感，月经不调，舌淡红，苔薄白，脉弦。',
                    'related_features': ['情志抑郁', '脉弦']
                }
            ],
            'analysis_summary': '患者主要表现为脾胃湿热证，同时伴有肝郁气滞证的表现。',
            'confidence': 0.85
        }
    
    async def _analyze_constitution(self, diagnosis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        基于诊断结果分析体质
        
        Args:
            diagnosis_results: 诊断结果列表
        
        Returns:
            Dict[str, Any]: 体质分析结果
        """
        logger.info("开始分析体质")
        
        # 实际实现中，这里会使用LLM或规则引擎进行体质分析
        # 这里返回模拟数据
        return {
            'constitutions': [
                {
                    'type': '痰湿质',
                    'score': 0.75,
                    'description': '痰湿质是指体内水液代谢失常，痰湿内生的体质状态。特征：形体肥胖，腹部肥满松软，面部皮肤油脂较多，常感胸闷，痰多，口粘腻或甜，喜食肥甘甜黏，苔腻。',
                    'dominant': True
                },
                {
                    'type': '气郁质',
                    'score': 0.62,
                    'description': '气郁质是指气机郁滞，情志抑郁的体质状态。特征：神情抑郁，情感脆弱，容易烦闷不乐，嗳气叹息，胸胁胀痛，女性易出现乳房胀痛、经行不畅。',
                    'dominant': False
                },
                {
                    'type': '平和质',
                    'score': 0.31,
                    'description': '平和质是指阴阳气血调和，脏腑功能平衡的理想体质状态。特征：面色红润，精力充沛，体形适中，体态壮实，睡眠良好，大小便正常，适应能力强，鲜少生病。',
                    'dominant': False
                }
            ],
            'analysis_summary': '患者以痰湿质为主，兼有气郁质，平和质特征较少。',
            'confidence': 0.8
        }
    
    async def _generate_recommendations(self, diagnosis_results: List[Dict[str, Any]], 
                                      syndrome_analysis: Dict[str, Any],
                                      constitution_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        基于诊断结果和分析生成健康建议
        
        Args:
            diagnosis_results: 诊断结果列表
            syndrome_analysis: 辨证分析结果
            constitution_analysis: 体质分析结果
        
        Returns:
            List[Dict[str, Any]]: 健康建议列表
        """
        logger.info("开始生成健康建议")
        
        # 实际实现中，这里会使用LLM或规则引擎生成个性化建议
        # 这里返回模拟数据
        return [
            {
                'type': 'DIET',
                'content': '饮食宜清淡，少食辛辣刺激、油腻煎炸食物。可多食具有利湿作用的食物，如薏米、赤小豆、冬瓜等。',
                'reason': '针对脾胃湿热证和痰湿质，调整饮食结构可帮助祛湿清热。',
                'priority': 5,
                'metadata': {}
            },
            {
                'type': 'EXERCISE',
                'content': '建议进行适度有氧运动，如散步、太极拳、八段锦等，每日30-60分钟。',
                'reason': '适度运动可促进气血运行，有利于痰湿代谢和肝气疏泄。',
                'priority': 4,
                'metadata': {}
            },
            {
                'type': 'LIFESTYLE',
                'content': '保持心情舒畅，避免情绪波动。可尝试冥想、深呼吸等放松方法。保持良好作息，避免熬夜。',
                'reason': '情志调畅有助于缓解肝郁气滞证，规律作息可改善脾胃功能。',
                'priority': 3,
                'metadata': {}
            }
        ]
    
    async def _generate_summary(self, diagnosis_results: List[Dict[str, Any]],
                              syndrome_analysis: Dict[str, Any],
                              constitution_analysis: Dict[str, Any]) -> str:
        """生成诊断总结"""
        # 实际实现中会使用LLM生成更个性化的总结
        # 这里返回简单总结
        return (
            f"通过四诊合参分析，您目前的主要证型为{syndrome_analysis['primary_syndromes'][0]['name']}，"
            f"体质类型为{constitution_analysis['constitutions'][0]['type']}。"
            f"建议您调整饮食结构，增加适度运动，保持情绪舒畅，规律作息。"
            f"若症状持续，建议咨询专业中医师进行进一步诊治。"
        )
    
    def _build_coordination_response(self, coordination_id: str, 
                                   diagnosis_results: List[Dict[str, Any]],
                                   syndrome_analysis: Dict[str, Any],
                                   constitution_analysis: Dict[str, Any],
                                   recommendations: List[Dict[str, Any]],
                                   summary: str) -> xiaoai_pb2.DiagnosisCoordinationResponse:
        """构建协调响应"""
        response = xiaoai_pb2.DiagnosisCoordinationResponse(
            coordination_id=coordination_id,
            summary=summary,
            timestamp=int(time.time())
        )
        
        # 添加诊断结果
        for result in diagnosis_results:
            diag_result = xiaoai_pb2.DiagnosisResult(
                diagnosis_id=result['diagnosis_id'],
                source_service=result['source_service'],
                confidence=result['confidence'],
                detailed_result=result['detailed_result'],
                timestamp=result['timestamp']
            )
            
            # 设置诊断类型
            if result['type'] == 'LOOKING':
                diag_result.type = xiaoai_pb2.DiagnosisResult.LOOKING
            elif result['type'] == 'LISTENING':
                diag_result.type = xiaoai_pb2.DiagnosisResult.LISTENING
            elif result['type'] == 'INQUIRY':
                diag_result.type = xiaoai_pb2.DiagnosisResult.INQUIRY
            elif result['type'] == 'PALPATION':
                diag_result.type = xiaoai_pb2.DiagnosisResult.PALPATION
            
            # 添加特征
            for feature in result['features']:
                diag_result.features.append(xiaoai_pb2.Feature(
                    name=feature['name'],
                    value=feature['value'],
                    confidence=feature['confidence'],
                    category=feature['category']
                ))
            
            response.diagnosis_results.append(diag_result)
        
        # 添加辨证分析
        syndrome_analysis_pb = xiaoai_pb2.SyndromeAnalysis(
            analysis_summary=syndrome_analysis['analysis_summary'],
            confidence=syndrome_analysis['confidence']
        )
        
        # 添加主要证型
        for syndrome in syndrome_analysis['primary_syndromes']:
            syndrome_analysis_pb.primary_syndromes.append(xiaoai_pb2.Syndrome(
                name=syndrome['name'],
                confidence=syndrome['confidence'],
                description=syndrome['description'],
                related_features=syndrome['related_features']
            ))
        
        # 添加次要证型
        for syndrome in syndrome_analysis['secondary_syndromes']:
            syndrome_analysis_pb.secondary_syndromes.append(xiaoai_pb2.Syndrome(
                name=syndrome['name'],
                confidence=syndrome['confidence'],
                description=syndrome['description'],
                related_features=syndrome['related_features']
            ))
        
        response.syndrome_analysis.CopyFrom(syndrome_analysis_pb)
        
        # 添加体质分析
        constitution_analysis_pb = xiaoai_pb2.ConstitutionAnalysis(
            analysis_summary=constitution_analysis['analysis_summary'],
            confidence=constitution_analysis['confidence']
        )
        
        for constitution in constitution_analysis['constitutions']:
            constitution_analysis_pb.constitutions.append(xiaoai_pb2.Constitution(
                type=constitution['type'],
                score=constitution['score'],
                description=constitution['description'],
                dominant=constitution['dominant']
            ))
        
        response.constitution_analysis.CopyFrom(constitution_analysis_pb)
        
        # 添加建议
        for rec in recommendations:
            recommendation_pb = xiaoai_pb2.Recommendation(
                content=rec['content'],
                reason=rec['reason'],
                priority=rec['priority']
            )
            
            # 设置建议类型
            if rec['type'] == 'DIET':
                recommendation_pb.type = xiaoai_pb2.Recommendation.DIET
            elif rec['type'] == 'EXERCISE':
                recommendation_pb.type = xiaoai_pb2.Recommendation.EXERCISE
            elif rec['type'] == 'LIFESTYLE':
                recommendation_pb.type = xiaoai_pb2.Recommendation.LIFESTYLE
            elif rec['type'] == 'MEDICATION':
                recommendation_pb.type = xiaoai_pb2.Recommendation.MEDICATION
            elif rec['type'] == 'FOLLOW_UP':
                recommendation_pb.type = xiaoai_pb2.Recommendation.FOLLOW_UP
            elif rec['type'] == 'CONSULTATION':
                recommendation_pb.type = xiaoai_pb2.Recommendation.CONSULTATION
            
            # 添加元数据
            if 'metadata' in rec and rec['metadata']:
                for key, value in rec['metadata'].items():
                    recommendation_pb.metadata[key] = value
            
            response.recommendations.append(recommendation_pb)
        
        return response
    
    def _create_empty_response(self, coordination_id: str) -> xiaoai_pb2.DiagnosisCoordinationResponse:
        """创建空响应"""
        return xiaoai_pb2.DiagnosisCoordinationResponse(
            coordination_id=coordination_id,
            summary="未执行任何诊断服务",
            timestamp=int(time.time())
        )
    
    def _create_error_response(self, coordination_id: str, error_message: str) -> xiaoai_pb2.DiagnosisCoordinationResponse:
        """创建错误响应"""
        return xiaoai_pb2.DiagnosisCoordinationResponse(
            coordination_id=coordination_id,
            summary=f"四诊协调过程中发生错误: {error_message}",
            timestamp=int(time.time())
        ) 