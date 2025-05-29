#!/usr/bin/env python3
"""
小艾服务gRPC实现
实现xiaoai_service.proto中定义的服务接口
"""

import logging
import time
import uuid

from ..agent.agent_manager import AgentManager
from ..orchestrator.diagnosis_coordinator import DiagnosisCoordinator
from ..repository.diagnosis_repository import DiagnosisRepository
from ..repository.session_repository import SessionRepository
from ..utils.config_loader import get_config
from ..utils.metrics import get_metrics_collector

# 导入生成的gRPC代码
try:
    import os
    import sys
    # 添加项目根目录到路径以便导入 api 模块
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
    import api.grpc.xiaoai_service_pb2 as xiaoai_pb2
    import api.grpc.xiaoai_service_pb2_grpc as xiaoai_pb2_grpc
except ImportError:
    logging.error("无法导入gRPC生成的代码, 请确保先生成protobuf代码")
    raise

logger = logging.getLogger(__name__)

class XiaoAIServiceImpl(xiaoai_pb2_grpc.XiaoAIServiceServicer):
    """小艾服务gRPC实现类"""

    def __init__(self):
        """初始化小艾服务实现"""
        self.config = get_config()
        self.metrics = get_metrics_collector()

        # 初始化依赖组件
        self.sessionrepository = SessionRepository()
        self.diagnosisrepository = DiagnosisRepository()
        self.agentmanager = AgentManager(self.sessionrepository)
        self.diagnosiscoordinator = DiagnosisCoordinator(
            self.agentmanager,
            self.diagnosis_repository
        )

        logger.info("小艾服务gRPC实现初始化完成")

    async def ChatStream(self, request, context):
        """
        流式聊天接口实现

        Args:
            request: ChatRequest请求对象
            context: gRPC上下文

        Yields:
            ChatResponse: 流式响应消息
        """
        time.time()

        # 记录请求指标
        self.metrics.increment_active_requests("ChatStream")

        try:
            # 从请求获取参数
            userid = request.user_id
            message = request.message
            sessionid = request.session_id if request.session_id else str(uuid.uuid4())

            # 调用智能体管理器处理消息
            await self.agent_manager.chat(
                userid, message, sessionid, context_size
            )

            # 构建响应
            response = xiaoai_pb2.ChatResponse(
                message_id=chat_response.get('message_id', str(uuid.uuid4())),
                message=chat_response.get('message', ''),
                confidence=chat_response.get('confidence', 0.0),
                timestamp=int(time.time())
            )

            # 添加建议动作
            for action in chat_response.get('suggested_actions', []):
                response.suggested_actions.append(action)

            # 添加元数据
            for key, value in chat_response.get('metadata', {}).items():
                response.metadata[key] = str(value)

            # 记录请求指标
            latency = time.time() - start_time
            self.metrics.track_request("gRPC", "ChatStream", 200, latency)

            # 返回响应
            yield response

        except Exception as e:
            logger.error("聊天流处理失败: %s", str(e))

            # 记录错误指标
            latency = time.time() - start_time
            self.metrics.track_request("gRPC", "ChatStream", 500, latency)

            # 返回错误响应
            xiaoai_pb2.ChatResponse(
                message_id=str(uuid.uuid4()),
                message=f"处理消息时出错: {e!s}",
                confidence=0.0,
                timestamp=int(time.time())
            )
            error_response.metadata["error"] = str(e)

            yield error_response

        finally:
            # 减少活跃请求计数
            self.metrics.decrement_active_requests("ChatStream")

    async def CoordinateDiagnosis(self, request, context):
        """
        四诊协调接口实现

        Args:
            request: DiagnosisCoordinationRequest请求对象
            context: gRPC上下文

        Returns:
            DiagnosisCoordinationResponse: 协调响应
        """
        time.time()

        # 记录请求指标
        self.metrics.increment_active_requests("CoordinateDiagnosis")

        try:
            # 调用四诊协调引擎
            response = await self.diagnosis_coordinator.coordinate_diagnosis(request)

            # 记录请求指标
            latency = time.time() - start_time
            self.metrics.track_request("gRPC", "CoordinateDiagnosis", 200, latency)

            return response

        except Exception as e:
            logger.error("四诊协调失败: %s", str(e))

            # 记录错误指标
            latency = time.time() - start_time
            self.metrics.track_request("gRPC", "CoordinateDiagnosis", 500, latency)

            # 创建错误响应
            return xiaoai_pb2.DiagnosisCoordinationResponse(
                coordination_id=str(uuid.uuid4()),
                summary=f"四诊协调失败: {e!s}",
                timestamp=int(time.time())
            )

        finally:
            # 减少活跃请求计数
            self.metrics.decrement_active_requests("CoordinateDiagnosis")

    async def ProcessMultimodalInput(self, request, context):
        """
        多模态输入处理接口实现

        Args:
            request: MultimodalRequest请求对象
            context: gRPC上下文

        Returns:
            MultimodalResponse: 处理响应
        """
        time.time()

        # 记录请求指标
        self.metrics.increment_active_requests("ProcessMultimodalInput")

        try:
            # 从请求获取参数
            userid = request.user_id
            request.session_id if request.session_id else str(uuid.uuid4())

            # 创建输入数据字典
            inputdata = {}

            # 判断输入类型并提取数据
            if request.HasField('voice'):
                input_data['voice'] = request.voice
            elif request.HasField('image'):
                input_data['image'] = request.image
            elif request.HasField('text'):
                input_data['text'] = request.text.text  # 提取文本内容
            elif request.HasField('sign'):
                input_data['sign'] = request.sign
            else:
                raise ValueError("未指定输入数据类型")

            # 复制元数据
            input_data['metadata'] = {}
            for key, value in request.metadata.items():
                input_data['metadata'][key] = value

            # 调用智能体管理器处理多模态输入
            result = await self.agent_manager.process_multimodal_input(
                userid, inputdata, session_id
            )

            # 构建响应
            response = xiaoai_pb2.MultimodalResponse(
                request_id=result.get('request_id', str(uuid.uuid4())),
                confidence=result.get('confidence', 0.0),
                error_message=result.get('error_message', ''),
                timestamp=int(time.time())
            )

            # 设置处理结果
            if 'voice_result' in result:
                # 设置语音处理结果
                voiceresult = xiaoai_pb2.VoiceResult(
                    transcription=result['voice_result'].get('transcription', ''),
                    detected_language=result['voice_result'].get('detected_language', ''),
                    detected_dialect=result['voice_result'].get('detected_dialect', ''),
                    speech_rate=result['voice_result'].get('speech_rate', 0.0)
                )

                # 设置情绪分析
                for emotion, score in result['voice_result'].get('emotions', {}).items():
                    voice_result.emotions[emotion] = score

                # 设置语音特征
                for feature in result['voice_result'].get('features', []):
                    voice_result.features.append(xiaoai_pb2.SpeechFeature(
                        feature_name=feature.get('feature_name', ''),
                        value=feature.get('value', 0.0),
                        description=feature.get('description', '')
                    ))

                response.voice_result.CopyFrom(voiceresult)

            elif 'image_result' in result:
                # 设置图像处理结果
                imageresult = xiaoai_pb2.ImageResult(
                    image_type=result['image_result'].get('image_type', ''),
                    processed_image=result['image_result'].get('processed_image', b'')
                )

                # 设置图像特征
                for feature in result['image_result'].get('features', []):
                    imgfeature = xiaoai_pb2.ImageFeature(
                        feature_name=feature.get('feature_name', ''),
                        confidence=feature.get('confidence', 0.0),
                        description=feature.get('description', '')
                    )

                    # 设置边界框
                    if 'location' in feature:
                        loc = feature['location']
                        img_feature.location.xmin = loc.get('x_min', 0.0)
                        img_feature.location.ymin = loc.get('y_min', 0.0)
                        img_feature.location.xmax = loc.get('x_max', 0.0)
                        img_feature.location.ymax = loc.get('y_max', 0.0)

                    image_result.features.append(imgfeature)

                # 设置分类结果
                for cls, score in result['image_result'].get('classifications', {}).items():
                    image_result.classifications[cls] = score

                # 设置可视化结果
                for _visname, vis_data in result['image_result'].get('visualizations', {}).items():
                    image_result.visualizations[vis_name] = vis_data

                response.image_result.CopyFrom(imageresult)

            elif 'text_result' in result:
                # 设置文本处理结果
                textresult = xiaoai_pb2.TextResult(
                    processed_text=result['text_result'].get('processed_text', ''),
                    detected_language=result['text_result'].get('detected_language', ''),
                    sentiment_score=result['text_result'].get('sentiment_score', 0.0)
                )

                # 设置意图分数
                for intent, score in result['text_result'].get('intent_scores', {}).items():
                    text_result.intent_scores[intent] = score

                # 设置实体识别结果
                for entity, value in result['text_result'].get('entities', {}).items():
                    text_result.entities[entity] = value

                response.text_result.CopyFrom(textresult)

            elif 'sign_result' in result:
                # 设置手语处理结果
                signresult = xiaoai_pb2.SignLanguageResult(
                    transcription=result['sign_result'].get('transcription', ''),
                    confidence=result['sign_result'].get('confidence', 0.0)
                )

                # 设置手势识别结果
                for gesture in result['sign_result'].get('gestures', []):
                    sign_result.gestures.append(xiaoai_pb2.SignGesture(
                        gesture_type=gesture.get('gesture_type', ''),
                        meaning=gesture.get('meaning', ''),
                        confidence=gesture.get('confidence', 0.0),
                        timestamp_ms=gesture.get('timestamp_ms', 0)
                    ))

                response.sign_result.CopyFrom(signresult)

            # 添加元数据
            for key, value in result.get('metadata', {}).items():
                response.metadata[key] = str(value)

            # 记录请求指标
            latency = time.time() - start_time
            self.metrics.track_request("gRPC", "ProcessMultimodalInput", 200, latency)

            return response

        except Exception as e:
            logger.error("多模态输入处理失败: %s", str(e))

            # 记录错误指标
            latency = time.time() - start_time
            self.metrics.track_request("gRPC", "ProcessMultimodalInput", 500, latency)

            # 返回错误响应
            return xiaoai_pb2.MultimodalResponse(
                request_id=str(uuid.uuid4()),
                error_message=f"处理多模态输入失败: {e!s}",
                confidence=0.0,
                timestamp=int(time.time())
            )

        finally:
            # 减少活跃请求计数
            self.metrics.decrement_active_requests("ProcessMultimodalInput")

    async def QueryHealthRecord(self, request, context):
        """
        查询用户健康记录接口实现

        Args:
            request: HealthRecordRequest请求对象
            context: gRPC上下文

        Returns:
            HealthRecordResponse: 健康记录响应
        """
        time.time()

        # 记录请求指标
        self.metrics.increment_active_requests("QueryHealthRecord")

        try:
            # 从请求获取参数
            userid = request.user_id
            request.end_time or int(time.time())

            # 现在返回模拟数据
            records = [
                {
                    'record_id': str(uuid.uuid4()),
                    'user_id': userid,
                    'record_type': record_type or '健康检查',
                    'title': '例行健康检查',
                    'content': '血压、心率、体温等指标正常',
                    'metadata': {'source': 'xiaoai', 'importance': 'normal'},
                    'created_at': int(time.time()) - 86400,
                    'updated_at': int(time.time()) - 86400
                }
            ]

            # 构建响应
            response = xiaoai_pb2.HealthRecordResponse(
                total_count=len(records),
                has_more=False
            )

            # 添加记录
            for record in records:
                healthrecord = xiaoai_pb2.HealthRecord(
                    record_id=record['record_id'],
                    user_id=record['user_id'],
                    record_type=record['record_type'],
                    title=record['title'],
                    content=record['content'],
                    created_at=record['created_at'],
                    updated_at=record['updated_at']
                )

                # 添加元数据
                for key, value in record.get('metadata', {}).items():
                    health_record.metadata[key] = str(value)

                response.records.append(healthrecord)

            # 记录请求指标
            latency = time.time() - start_time
            self.metrics.track_request("gRPC", "QueryHealthRecord", 200, latency)

            return response

        except Exception as e:
            logger.error("查询健康记录失败: %s", str(e))

            # 记录错误指标
            latency = time.time() - start_time
            self.metrics.track_request("gRPC", "QueryHealthRecord", 500, latency)

            # 返回错误响应
            return xiaoai_pb2.HealthRecordResponse(
                total_count=0,
                has_more=False
            )

        finally:
            # 减少活跃请求计数
            self.metrics.decrement_active_requests("QueryHealthRecord")

    async def GenerateHealthSummary(self, request, context):
        """
        生成用户健康摘要接口实现

        Args:
            request: HealthSummaryRequest请求对象
            context: gRPC上下文

        Returns:
            HealthSummaryResponse: 健康摘要响应
        """
        time.time()

        # 记录请求指标
        self.metrics.increment_active_requests("GenerateHealthSummary")

        try:
            # 从请求获取参数
            userid = request.user_id
            starttime_ms = request.start_time or 0
            endtime_ms = request.end_time or int(time.time())
            categories = list(request.categories)
            includecharts = request.include_charts

            # 调用智能体管理器生成健康摘要
            healthdata = {
                'start_time': starttime_ms,
                'end_time': endtime_ms,
                'categories': categories,
                'include_charts': includecharts,
                'include_recommendations': include_recommendations
            }

            summary = await self.agent_manager.generate_health_summary(userid, healthdata)

            # 构建响应
            response = xiaoai_pb2.HealthSummaryResponse(
                summary_id=summary.get('summary_id', str(uuid.uuid4())),
                user_id=userid,
                text_summary=summary.get('text_summary', '未找到健康数据'),
                generated_at=int(time.time())
            )

            # 添加健康趋势
            for trend in summary.get('trends', []):
                response.trends.append(xiaoai_pb2.HealthTrend(
                    metric_name=trend.get('metric_name', ''),
                    trend_direction=trend.get('trend_direction', ''),
                    change_percentage=trend.get('change_percentage', 0.0),
                    description=trend.get('description', ''),
                    priority=trend.get('priority', 1)
                ))

            # 添加健康指标
            for metric in summary.get('metrics', []):
                response.metrics.append(xiaoai_pb2.HealthMetric(
                    name=metric.get('name', ''),
                    value=metric.get('value', ''),
                    unit=metric.get('unit', ''),
                    status=metric.get('status', ''),
                    reference_range=metric.get('reference_range', '')
                ))

            # 添加建议
            if include_recommendations:
                for rec in summary.get('recommendations', []):
                    recommendation = xiaoai_pb2.Recommendation(
                        content=rec.get('content', ''),
                        reason=rec.get('reason', ''),
                        priority=rec.get('priority', 1)
                    )

                    # 设置建议类型
                    rectype = rec.get('type', '').upper()
                    if rectype == 'DIET':
                        recommendation.type = xiaoai_pb2.Recommendation.DIET
                    elif rectype == 'EXERCISE':
                        recommendation.type = xiaoai_pb2.Recommendation.EXERCISE
                    elif rectype == 'LIFESTYLE':
                        recommendation.type = xiaoai_pb2.Recommendation.LIFESTYLE
                    elif rectype == 'MEDICATION':
                        recommendation.type = xiaoai_pb2.Recommendation.MEDICATION
                    elif rectype == 'FOLLOW_UP':
                        recommendation.type = xiaoai_pb2.Recommendation.FOLLOW_UP
                    elif rectype == 'CONSULTATION':
                        recommendation.type = xiaoai_pb2.Recommendation.CONSULTATION

                    # 添加元数据
                    for key, value in rec.get('metadata', {}).items():
                        recommendation.metadata[key] = str(value)

                    response.recommendations.append(recommendation)

            # 添加图表数据
            if include_charts:
                for _chartname, chart_data in summary.get('charts', {}).items():
                    response.charts[chart_name] = chart_data

            # 记录请求指标
            latency = time.time() - start_time
            self.metrics.track_request("gRPC", "GenerateHealthSummary", 200, latency)

            return response

        except Exception as e:
            logger.error("生成健康摘要失败: %s", str(e))

            # 记录错误指标
            latency = time.time() - start_time
            self.metrics.track_request("gRPC", "GenerateHealthSummary", 500, latency)

            # 返回错误响应
            return xiaoai_pb2.HealthSummaryResponse(
                summary_id=str(uuid.uuid4()),
                user_id=request.userid,
                text_summary=f"生成健康摘要失败: {e!s}",
                generated_at=int(time.time())
            )

        finally:
            # 减少活跃请求计数
            self.metrics.decrement_active_requests("GenerateHealthSummary")

    async def HealthCheck(self, request, context):
        """
        健康检查接口实现

        Args:
            request: HealthCheckRequest请求对象
            context: gRPC上下文

        Returns:
            HealthCheckResponse: 健康检查响应
        """
        try:
            # 检查依赖组件健康状态
            details = {}

            # 检查MongoDB连接
            details['mongodb'] = 'connected' if mongo_status else 'disconnected'

            # 检查LLM服务
            details['llm_service'] = 'available'

            # 检查服务集成状态
            for service_name in ['look_service', 'listen_service', 'inquiry_service', 'palpation_service']:
                details[service_name] = 'connected'

            # 构建响应
            response = xiaoai_pb2.HealthCheckResponse(
                status=xiaoai_pb2.HealthCheckResponse.SERVING
            )

            # 如果请求详细信息, 添加详细状态
            if request.include_details:
                for key, value in details.items():
                    response.details[key] = value

            return response

        except Exception as e:
            logger.error("健康检查失败: %s", str(e))

            # 返回错误响应
            response = xiaoai_pb2.HealthCheckResponse(
                status=xiaoai_pb2.HealthCheckResponse.NOT_SERVING
            )

            response.details['error'] = str(e)
            return response
