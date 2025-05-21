"""
闻诊服务实现 - 实现gRPC接口定义
"""
import os
import time
import logging
import grpc
import concurrent.futures
from typing import Dict, List, Optional, Any, Tuple

import numpy as np

from api.grpc import listen_service_pb2 as pb2
from api.grpc import listen_service_pb2_grpc as pb2_grpc
from internal.audio.audio_analyzer import AudioAnalyzer
from internal.audio.voice_feature_extractor import VoiceFeatureExtractor
from internal.audio.sound_analyzer import SoundAnalyzer
from internal.audio.emotion_analyzer import EmotionAnalyzer
from internal.repository.audio_repository import get_audio_repository
from pkg.utils.config_loader import get_config
from pkg.utils.metrics import get_metrics

logger = logging.getLogger(__name__)

class ListenServiceServicer(pb2_grpc.ListenServiceServicer):
    """闻诊服务实现类，实现gRPC服务接口"""
    
    def __init__(self):
        """初始化闻诊服务"""
        self.config = get_config()
        self.metrics = get_metrics("listen-service")
        
        # 加载各分析器
        self.voice_analyzer = VoiceFeatureExtractor(self.config.config)
        self.sound_analyzer = SoundAnalyzer(self.config.config)
        self.emotion_analyzer = EmotionAnalyzer(self.config.config)
        
        # 获取存储库
        self.repository = get_audio_repository()
        
        # 线程池
        max_workers = self.config.get("server.max_workers", 10)
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        
        # 初始化健康状态
        self.healthy = True
        self.metrics.set_health_status(True)
        
        logger.info("闻诊服务初始化完成")
    
    def AnalyzeVoice(self, request, context):
        """
        分析语音特征
        
        Args:
            request: gRPC请求对象
            context: gRPC上下文
            
        Returns:
            VoiceAnalysisResponse: 语音分析结果
        """
        start_time = time.time()
        method_name = "AnalyzeVoice"
        
        try:
            # 提取请求参数
            user_id = request.user_id
            session_id = request.session_id
            audio_data = request.audio_data
            audio_format = request.audio_format
            sample_rate = request.sample_rate
            channels = request.channels
            metadata = dict(request.metadata)
            apply_preprocessing = request.apply_preprocessing
            
            # 记录指标
            audio_size = len(audio_data)
            self.metrics.audio_size.labels(audio_format).observe(audio_size)
            
            # 参数验证
            if not audio_data:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("音频数据不能为空")
                self.metrics.error_counter.labels("empty_audio", "voice_analyzer").inc()
                return pb2.VoiceAnalysisResponse()
            
            # 分析语音
            logger.info(f"开始分析语音: user_id={user_id}, session_id={session_id}")
            analysis = self.voice_analyzer.analyze_voice(
                audio_data=audio_data,
                audio_format=audio_format,
                sample_rate=sample_rate,
                apply_preprocessing=apply_preprocessing
            )
            
            # 异步保存结果
            self.thread_pool.submit(
                self.repository.save_voice_analysis, 
                analysis, user_id, session_id
            )
            
            # 转换为响应对象
            response = self._convert_to_voice_response(analysis)
            
            # 记录指标
            processing_time = time.time() - start_time
            self.metrics.track_request(method_name, "success", processing_time)
            self.metrics.track_audio_processing(
                "voice", processing_time, audio_size, audio_format, 
                analysis.get("duration", 0)
            )
            self.metrics.track_model_inference(
                "voice_analyzer", processing_time, analysis.get("confidence", 0)
            )
            
            logger.info(f"语音分析完成: analysis_id={response.analysis_id}, 耗时={processing_time:.3f}秒")
            return response
            
        except Exception as e:
            error_msg = f"语音分析失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(error_msg)
            self.metrics.error_counter.labels("internal_error", "voice_analyzer").inc()
            self.metrics.track_request(method_name, "error", time.time() - start_time)
            return pb2.VoiceAnalysisResponse()
    
    def AnalyzeSound(self, request, context):
        """
        分析声音特征（咳嗽声、呼吸声等非语言声音）
        
        Args:
            request: gRPC请求对象
            context: gRPC上下文
            
        Returns:
            SoundAnalysisResponse: 声音分析结果
        """
        start_time = time.time()
        method_name = "AnalyzeSound"
        
        try:
            # 提取请求参数
            user_id = request.user_id
            session_id = request.session_id
            audio_data = request.audio_data
            audio_format = request.audio_format
            sample_rate = request.sample_rate
            sound_type = pb2.SoundType.Name(request.sound_type)
            metadata = dict(request.metadata)
            apply_preprocessing = request.apply_preprocessing
            
            # 记录指标
            audio_size = len(audio_data)
            self.metrics.audio_size.labels(audio_format).observe(audio_size)
            
            # 参数验证
            if not audio_data:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("音频数据不能为空")
                self.metrics.error_counter.labels("empty_audio", "sound_analyzer").inc()
                return pb2.SoundAnalysisResponse()
            
            # 分析声音
            logger.info(f"开始分析声音: user_id={user_id}, session_id={session_id}, sound_type={sound_type}")
            analysis = self.sound_analyzer.analyze_sound(
                audio_data=audio_data,
                audio_format=audio_format,
                sound_type=sound_type if sound_type != "SOUND_UNKNOWN" else None,
                sample_rate=sample_rate,
                apply_preprocessing=apply_preprocessing
            )
            
            # 异步保存结果
            self.thread_pool.submit(
                self.repository.save_sound_analysis, 
                analysis, user_id, session_id
            )
            
            # 转换为响应对象
            response = self._convert_to_sound_response(analysis)
            
            # 记录指标
            processing_time = time.time() - start_time
            self.metrics.track_request(method_name, "success", processing_time)
            self.metrics.track_audio_processing(
                "sound", processing_time, audio_size, audio_format, 
                analysis.get("duration", 0)
            )
            self.metrics.track_model_inference(
                "sound_analyzer", processing_time, analysis.get("confidence", 0)
            )
            
            logger.info(f"声音分析完成: analysis_id={response.analysis_id}, 声音类型={response.sound_type}, 耗时={processing_time:.3f}秒")
            return response
            
        except Exception as e:
            error_msg = f"声音分析失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(error_msg)
            self.metrics.error_counter.labels("internal_error", "sound_analyzer").inc()
            self.metrics.track_request(method_name, "error", time.time() - start_time)
            return pb2.SoundAnalysisResponse()
    
    def AnalyzeEmotion(self, request, context):
        """
        分析语音情绪
        
        Args:
            request: gRPC请求对象
            context: gRPC上下文
            
        Returns:
            EmotionAnalysisResponse: 情绪分析结果
        """
        start_time = time.time()
        method_name = "AnalyzeEmotion"
        
        try:
            # 提取请求参数
            user_id = request.user_id
            session_id = request.session_id
            audio_data = request.audio_data
            audio_format = request.audio_format
            sample_rate = request.sample_rate
            text_transcript = request.text_transcript
            metadata = dict(request.metadata)
            
            # 记录指标
            audio_size = len(audio_data)
            self.metrics.audio_size.labels(audio_format).observe(audio_size)
            
            # 参数验证
            if not audio_data:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("音频数据不能为空")
                self.metrics.error_counter.labels("empty_audio", "emotion_analyzer").inc()
                return pb2.EmotionAnalysisResponse()
            
            # 分析情绪
            logger.info(f"开始分析情绪: user_id={user_id}, session_id={session_id}")
            analysis = self.emotion_analyzer.analyze_emotion(
                audio_data=audio_data,
                audio_format=audio_format,
                sample_rate=sample_rate,
                text_transcript=text_transcript if text_transcript else None
            )
            
            # 异步保存结果
            self.thread_pool.submit(
                self.repository.save_emotion_analysis, 
                analysis, user_id, session_id
            )
            
            # 转换为响应对象
            response = self._convert_to_emotion_response(analysis)
            
            # 记录指标
            processing_time = time.time() - start_time
            self.metrics.track_request(method_name, "success", processing_time)
            self.metrics.track_audio_processing(
                "emotion", processing_time, audio_size, audio_format, 
                analysis.get("duration", 0) if "duration" in analysis else 0
            )
            self.metrics.track_model_inference(
                "emotion_analyzer", processing_time, analysis.get("confidence", 0)
            )
            
            logger.info(f"情绪分析完成: analysis_id={response.analysis_id}, 耗时={processing_time:.3f}秒")
            return response
            
        except Exception as e:
            error_msg = f"情绪分析失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(error_msg)
            self.metrics.error_counter.labels("internal_error", "emotion_analyzer").inc()
            self.metrics.track_request(method_name, "error", time.time() - start_time)
            return pb2.EmotionAnalysisResponse()
    
    def DetectDialect(self, request, context):
        """
        检测方言
        
        Args:
            request: gRPC请求对象
            context: gRPC上下文
            
        Returns:
            DialectDetectionResponse: 方言检测结果
        """
        start_time = time.time()
        method_name = "DetectDialect"
        
        try:
            # 提取请求参数
            user_id = request.user_id
            session_id = request.session_id
            audio_data = request.audio_data
            audio_format = request.audio_format
            sample_rate = request.sample_rate
            text_transcript = request.text_transcript
            metadata = dict(request.metadata)
            
            # 记录指标
            audio_size = len(audio_data)
            self.metrics.audio_size.labels(audio_format).observe(audio_size)
            
            # 参数验证
            if not audio_data:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("音频数据不能为空")
                self.metrics.error_counter.labels("empty_audio", "dialect_detector").inc()
                return pb2.DialectDetectionResponse()
            
            # 方言检测（临时模拟，实际应实现方言检测器）
            logger.info(f"开始方言检测: user_id={user_id}, session_id={session_id}")
            
            # 模拟方言检测结果
            detection = {
                "detection_id": f"dialect_{int(time.time()*1000)}",
                "primary_dialect": "普通话",
                "primary_dialect_region": "华北",
                "primary_dialect_confidence": 0.85,
                "candidates": [
                    {"dialect": "普通话", "region": "华北", "confidence": 0.85},
                    {"dialect": "东北话", "region": "东北", "confidence": 0.10},
                    {"dialect": "四川话", "region": "西南", "confidence": 0.05}
                ],
                "timestamp": int(time.time())
            }
            
            # 异步保存结果
            self.thread_pool.submit(
                self.repository.save_dialect_detection, 
                detection, user_id, session_id
            )
            
            # 转换为响应对象
            response = self._convert_to_dialect_response(detection)
            
            # 记录指标
            processing_time = time.time() - start_time
            self.metrics.track_request(method_name, "success", processing_time)
            self.metrics.track_model_inference(
                "dialect_detector", processing_time, detection.get("primary_dialect_confidence", 0)
            )
            
            logger.info(f"方言检测完成: detection_id={response.detection_id}, 方言={response.primary_dialect}, 耗时={processing_time:.3f}秒")
            return response
            
        except Exception as e:
            error_msg = f"方言检测失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(error_msg)
            self.metrics.error_counter.labels("internal_error", "dialect_detector").inc()
            self.metrics.track_request(method_name, "error", time.time() - start_time)
            return pb2.DialectDetectionResponse()
    
    def TranscribeAudio(self, request, context):
        """
        语音转写
        
        Args:
            request: gRPC请求对象
            context: gRPC上下文
            
        Returns:
            TranscriptionResponse: 语音转写结果
        """
        start_time = time.time()
        method_name = "TranscribeAudio"
        
        try:
            # 提取请求参数
            user_id = request.user_id
            session_id = request.session_id
            audio_data = request.audio_data
            audio_format = request.audio_format
            sample_rate = request.sample_rate
            language = request.language
            detect_dialect = request.detect_dialect
            metadata = dict(request.metadata)
            
            # 记录指标
            audio_size = len(audio_data)
            self.metrics.audio_size.labels(audio_format).observe(audio_size)
            
            # 参数验证
            if not audio_data:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("音频数据不能为空")
                self.metrics.error_counter.labels("empty_audio", "transcription").inc()
                return pb2.TranscriptionResponse()
            
            # 语音转写（临时模拟，实际应实现语音转写功能）
            logger.info(f"开始语音转写: user_id={user_id}, session_id={session_id}")
            
            # 模拟语音转写结果
            transcription = {
                "transcription_id": f"trans_{int(time.time()*1000)}",
                "text": "这是一段示例的转写文本，用于模拟语音转写功能。",
                "language": language or "zh-CN",
                "dialect": "普通话" if detect_dialect else "",
                "confidence": 0.92,
                "segments": [
                    {"text": "这是一段示例的转写文本，", "start_time": 0.0, "end_time": 2.5, "confidence": 0.95},
                    {"text": "用于模拟语音转写功能。", "start_time": 2.5, "end_time": 4.5, "confidence": 0.90}
                ],
                "timestamp": int(time.time())
            }
            
            # 异步保存结果
            self.thread_pool.submit(
                self.repository.save_transcription, 
                transcription, user_id, session_id
            )
            
            # 转换为响应对象
            response = self._convert_to_transcription_response(transcription)
            
            # 记录指标
            processing_time = time.time() - start_time
            self.metrics.track_request(method_name, "success", processing_time)
            self.metrics.track_model_inference(
                "transcription_model", processing_time, transcription.get("confidence", 0)
            )
            
            logger.info(f"语音转写完成: transcription_id={response.transcription_id}, 耗时={processing_time:.3f}秒")
            return response
            
        except Exception as e:
            error_msg = f"语音转写失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(error_msg)
            self.metrics.error_counter.labels("internal_error", "transcription").inc()
            self.metrics.track_request(method_name, "error", time.time() - start_time)
            return pb2.TranscriptionResponse()
    
    def BatchAnalyze(self, request, context):
        """
        批量分析
        
        Args:
            request: gRPC请求对象
            context: gRPC上下文
            
        Returns:
            BatchAnalysisResponse: 批量分析结果
        """
        start_time = time.time()
        method_name = "BatchAnalyze"
        
        try:
            # 提取请求参数
            user_id = request.user_id
            session_id = request.session_id
            audio_data = request.audio_data
            audio_format = request.audio_format
            sample_rate = request.sample_rate
            analysis_types = list(request.analysis_types)
            metadata = dict(request.metadata)
            
            # 记录指标
            audio_size = len(audio_data)
            self.metrics.audio_size.labels(audio_format).observe(audio_size)
            
            # 参数验证
            if not audio_data:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("音频数据不能为空")
                self.metrics.error_counter.labels("empty_audio", "batch_analyze").inc()
                return pb2.BatchAnalysisResponse()
            
            # 如果未指定分析类型，默认执行所有分析
            if not analysis_types:
                analysis_types = ["voice", "sound", "emotion", "dialect", "transcription"]
            
            # 批量分析结果
            batch_result = {
                "batch_id": f"batch_{int(time.time()*1000)}",
                "timestamp": int(time.time())
            }
            
            # 执行请求的各类分析
            if "voice" in analysis_types:
                voice_analysis = self.voice_analyzer.analyze_voice(
                    audio_data=audio_data,
                    audio_format=audio_format,
                    sample_rate=sample_rate
                )
                batch_result["voice_analysis"] = voice_analysis
            
            if "sound" in analysis_types:
                sound_analysis = self.sound_analyzer.analyze_sound(
                    audio_data=audio_data,
                    audio_format=audio_format,
                    sample_rate=sample_rate
                )
                batch_result["sound_analysis"] = sound_analysis
            
            if "emotion" in analysis_types:
                emotion_analysis = self.emotion_analyzer.analyze_emotion(
                    audio_data=audio_data,
                    audio_format=audio_format,
                    sample_rate=sample_rate
                )
                batch_result["emotion"] = emotion_analysis
            
            if "dialect" in analysis_types:
                # 模拟方言检测
                dialect_detection = {
                    "detection_id": f"dialect_{int(time.time()*1000)}",
                    "primary_dialect": "普通话",
                    "primary_dialect_region": "华北",
                    "primary_dialect_confidence": 0.85,
                    "candidates": [
                        {"dialect": "普通话", "region": "华北", "confidence": 0.85},
                        {"dialect": "东北话", "region": "东北", "confidence": 0.10}
                    ],
                    "timestamp": int(time.time())
                }
                batch_result["dialect"] = dialect_detection
            
            if "transcription" in analysis_types:
                # 模拟语音转写
                transcription = {
                    "transcription_id": f"trans_{int(time.time()*1000)}",
                    "text": "这是一段示例的转写文本，用于批量分析功能。",
                    "language": "zh-CN",
                    "confidence": 0.92,
                    "segments": [
                        {"text": "这是一段示例的转写文本，", "start_time": 0.0, "end_time": 2.5, "confidence": 0.95},
                        {"text": "用于批量分析功能。", "start_time": 2.5, "end_time": 4.0, "confidence": 0.90}
                    ],
                    "timestamp": int(time.time())
                }
                batch_result["transcription"] = transcription
            
            # 生成综合诊断结果
            diagnosis_result = self._generate_combined_diagnosis(batch_result)
            batch_result["diagnosis"] = diagnosis_result
            
            # 异步保存结果
            self.thread_pool.submit(
                self.repository.save_batch_analysis, 
                batch_result, user_id, session_id
            )
            
            # 转换为响应对象
            response = self._convert_to_batch_response(batch_result)
            
            # 记录指标
            processing_time = time.time() - start_time
            self.metrics.track_request(method_name, "success", processing_time)
            self.metrics.track_audio_processing(
                "batch", processing_time, audio_size, audio_format, 
                batch_result.get("voice_analysis", {}).get("duration", 0)
            )
            
            logger.info(f"批量分析完成: batch_id={response.batch_id}, 分析类型={','.join(analysis_types)}, 耗时={processing_time:.3f}秒")
            return response
            
        except Exception as e:
            error_msg = f"批量分析失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(error_msg)
            self.metrics.error_counter.labels("internal_error", "batch_analyze").inc()
            self.metrics.track_request(method_name, "error", time.time() - start_time)
            return pb2.BatchAnalysisResponse() 