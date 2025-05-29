#!/usr/bin/env python3

"""
四诊特征提取器
负责从多模态四诊数据中提取健康特征
"""

import logging
import re
import time
import uuid
from typing import Any

from internal.agent.model_factory import get_model_factory

# 协议导入
from ...api.grpc import four_diagnosis_pb2 as diagnosis_pb
from ..utils.config_loader import get_config
from ..utils.metrics import get_metrics_collector

# 导入依赖

# 日志配置
logger = logging.getLogger(__name__)

class FeatureExtractor:
    """四诊特征提取器, 负责从多模态数据中提取关键健康特征"""

    def __init__(self, model_factory=None):
        """
        初始化特征提取器

        Args:
            model_factory: 模型工厂实例, 如果为None则创建新实例
        """
        self.config = get_config()
        self.metrics = get_metrics_collector()

        self.modelfactory = model_factory

        # 加载配置
        self.config.get_section('feature_extraction', {})

        # 特征提取配置
        self.minconfidence = feature_config.get('min_confidence', 0.6)
        self.maxfeatures_per_category = feature_config.get('max_features_per_category', 10)
        self.useadvanced_extraction = feature_config.get('use_advanced_extraction', True)

        # 加载提示语模板
        self.prompttemplates = self._load_prompt_templates()

        # 特征分类映射
        self.featurecategories = {
            'tongue': ['tongue_color', 'tongue_shape', 'coating_color', 'coating_distribution', 'tongue_moisture'],
            'face': ['face_color', 'face_expression', 'face_region', 'eye_condition', 'lip_condition'],
            'voice': ['voice_quality', 'voice_strength', 'voice_tone', 'speech_pattern', 'breath_sound'],
            'pulse': ['pulse_pattern', 'pulse_strength', 'pulse_rhythm', 'pulse_depth', 'pulse_quality'],
            'symptom': ['chief_complaint', 'symptom', 'pain', 'sleep', 'digestion', 'urination', 'bowel'],
            'history': ['medical_history', 'family_history', 'lifestyle']
        }

        logger.info("四诊特征提取器初始化完成")

    async def initialize(self):
        """异步初始化模型工厂"""
        if self.model_factory is None:
            self.modelfactory = await get_model_factory()
            logger.info("特征提取器模型工厂异步初始化完成")

    def _load_prompt_templates(self) -> dict[str, str]:
        """加载提示语模板"""
        self.config.get_section('paths.prompts', 'config/prompts')
        templates = {}


        for key, filename in template_files.items():
            try:
                with open(f"{prompt_dir}/{filename}", encoding='utf-8') as f:
                    templates[key] = f.read()
                    logger.debug(f"加载提示语模板 {key} 成功")
            except Exception as e:
                logger.error(f"加载提示语模板 {key} 失败: {e!s}")
                templates[key] = f"你是小艾智能体中负责{key}的专家。请提取关键健康特征。"

        return templates

    async def extract_features_from_diagnosis(self,
                                             diagnosisdata: diagnosis_pb.DiagnosisData) -> list[diagnosis_pb.Feature]:
        """
        从诊断数据中提取特征

        Args:
            diagnosis_data: 诊断数据

        Returns:
            特征列表
        """
        # 记录指标
        self.metrics.increment_request_count("feature_extraction")
        time.time()

        try:
            # 按照诊断类型分类
            features = []

            # 根据诊断类型调用相应的特征提取方法
            if diagnosis_data.diagnosistype == diagnosis_pb.DiagnosisType.LOOK:
                # 处理望诊数据
                tonguefeatures = await self._extract_tongue_features(diagnosis_data.lookdata)
                facefeatures = await self._extract_face_features(diagnosis_data.lookdata)
                features.extend(tonguefeatures)
                features.extend(facefeatures)

            elif diagnosis_data.diagnosistype == diagnosis_pb.DiagnosisType.LISTEN:
                # 处理闻诊数据
                voicefeatures = await self._extract_voice_features(diagnosis_data.listendata)
                features.extend(voicefeatures)

            elif diagnosis_data.diagnosistype == diagnosis_pb.DiagnosisType.INQUIRY:
                # 处理问诊数据
                symptomfeatures = await self._extract_symptom_features(diagnosis_data.inquirydata)
                features.extend(symptomfeatures)

            elif diagnosis_data.diagnosistype == diagnosis_pb.DiagnosisType.PALPATION:
                # 处理切诊数据
                pulsefeatures = await self._extract_pulse_features(diagnosis_data.palpationdata)
                features.extend(pulsefeatures)

            # 记录成功指标
            processtime = time.time() - start_time
            self.metrics.record_request_time("feature_extraction", processtime)

            # 返回提取的特征
            return features

        except Exception as e:
            # 记录错误
            logger.error(f"特征提取失败: {e!s}")
            self.metrics.increment_error_count("feature_extraction")
            return []

    async def _extract_tongue_features(self, look_data: diagnosis_pb.LookData) -> list[diagnosis_pb.Feature]:
        """
        从舌象图像中提取特征

        Args:
            look_data: 望诊数据

        Returns:
            特征列表
        """
        features = []

        # 检查是否有舌象图像
        if not look_data.tongue_image_url and not look_data.tongue_analysis:
            logger.warning("没有舌象数据, 跳过舌象特征提取")
            return features

        try:
            # 使用现有的舌象分析结果
            if look_data.tongue_analysis:
                # 解析现有分析结果

                # 舌色特征
                if tongue_analysis.tongue_color:
                    features.append(self._create_feature(
                        name="tongue_color",
                        value=tongue_analysis.tonguecolor,
                        confidence=tongue_analysis.confidence,
                        category="tongue",
                        source="look_service"
                    ))

                # 舌形特征
                if tongue_analysis.tongue_shape:
                    features.append(self._create_feature(
                        name="tongue_shape",
                        value=tongue_analysis.tongueshape,
                        confidence=tongue_analysis.confidence,
                        category="tongue",
                        source="look_service"
                    ))

                # 舌苔特征
                if tongue_analysis.coating_color:
                    features.append(self._create_feature(
                        name="coating_color",
                        value=tongue_analysis.coatingcolor,
                        confidence=tongue_analysis.confidence,
                        category="tongue",
                        source="look_service"
                    ))

                # 舌苔分布
                if tongue_analysis.coating_distribution:
                    features.append(self._create_feature(
                        name="coating_distribution",
                        value=tongue_analysis.coatingdistribution,
                        confidence=tongue_analysis.confidence,
                        category="tongue",
                        source="look_service"
                    ))

                # 舌质润燥
                if tongue_analysis.moisture:
                    features.append(self._create_feature(
                        name="tongue_moisture",
                        value=tongue_analysis.moisture,
                        confidence=tongue_analysis.confidence,
                        category="tongue",
                        source="look_service"
                    ))

            # 如果需要增强分析, 使用LLM进行深度分析
            if self.use_advanced_extraction and (features == [] or look_data.tongueimage_url):
                # 构建提示语上下文
                promptcontext = {
                    "tongue_image_url": look_data.tongue_image_url or "无图像链接",
                    "existing_analysis": look_data.tongue_analysis or "无已有分析"
                }

                # 使用LLM进行舌象分析
                await self._llm_tongue_analysis(promptcontext)

                # 合并特征, 优先使用服务分析结果
                if advanced_features:
                    # 记录已添加的特征名称
                    {f.feature_name for f in features}

                    # 添加LLM分析的新特征
                    for feature in advanced_features:
                        if feature.feature_name not in added_feature_names:
                            features.append(feature)

            return features

        except Exception as e:
            logger.error(f"舌象特征提取失败: {e!s}")
            self.metrics.increment_error_count("tongue_feature_extraction")
            return features

    async def _extract_face_features(self, look_data: diagnosis_pb.LookData) -> list[diagnosis_pb.Feature]:
        """从面诊数据中提取特征"""
        features = []

        # 检查是否有面诊数据
        if not look_data.face_image_url and not look_data.face_analysis:
            logger.warning("没有面诊数据, 跳过面诊特征提取")
            return features

        try:
            # 使用现有的面诊分析结果
            if look_data.face_analysis:
                # 解析现有分析结果

                # 面色特征
                if face_analysis.face_color:
                    features.append(self._create_feature(
                        name="face_color",
                        value=face_analysis.facecolor,
                        confidence=face_analysis.confidence,
                        category="face",
                        source="look_service"
                    ))

                # 面部表情
                if face_analysis.expression:
                    features.append(self._create_feature(
                        name="face_expression",
                        value=face_analysis.expression,
                        confidence=face_analysis.confidence,
                        category="face",
                        source="look_service"
                    ))

                # 重点面部区域
                if face_analysis.specific_region:
                    features.append(self._create_feature(
                        name="face_region",
                        value=face_analysis.specificregion,
                        confidence=face_analysis.confidence,
                        category="face",
                        source="look_service"
                    ))

            # 高级特征提取
            if self.use_advanced_extraction and (features == [] or look_data.faceimage_url):
                pass

            return features

        except Exception as e:
            logger.error(f"面诊特征提取失败: {e!s}")
            self.metrics.increment_error_count("face_feature_extraction")
            return features

    async def _extract_voice_features(self, listen_data: diagnosis_pb.ListenData) -> list[diagnosis_pb.Feature]:
        """从闻诊数据中提取特征"""
        features = []

        try:
            # 使用现有的语音分析结果
            if listen_data.voice_analysis:

                # 语音质量
                if voice_analysis.voice_quality:
                    features.append(self._create_feature(
                        name="voice_quality",
                        value=voice_analysis.voicequality,
                        confidence=voice_analysis.confidence,
                        category="voice",
                        source="listen_service"
                    ))

                # 语音强度
                if voice_analysis.voice_strength:
                    features.append(self._create_feature(
                        name="voice_strength",
                        value=voice_analysis.voicestrength,
                        confidence=voice_analysis.confidence,
                        category="voice",
                        source="listen_service"
                    ))

                # 说话模式
                if voice_analysis.speech_pattern:
                    features.append(self._create_feature(
                        name="speech_pattern",
                        value=voice_analysis.speechpattern,
                        confidence=voice_analysis.confidence,
                        category="voice",
                        source="listen_service"
                    ))

            # 呼吸声分析
            if listen_data.breath_sound_analysis:

                if breath_analysis.breath_sound:
                    features.append(self._create_feature(
                        name="breath_sound",
                        value=breath_analysis.breathsound,
                        confidence=breath_analysis.confidence,
                        category="voice",
                        source="listen_service"
                    ))

            return features

        except Exception as e:
            logger.error(f"闻诊特征提取失败: {e!s}")
            self.metrics.increment_error_count("voice_feature_extraction")
            return features

    async def _extract_symptom_features(self, inquiry_data: diagnosis_pb.InquiryData) -> list[diagnosis_pb.Feature]:
        """从问诊数据中提取特征"""
        features = []

        try:
            # 检查是否有症状分析
            if not inquiry_data.symptom_analysis and not inquiry_data.conversation_history:
                logger.warning("没有问诊数据, 跳过问诊特征提取")
                return features

            # 使用现有的症状分析
            if inquiry_data.symptom_analysis:
                # 主诉
                if inquiry_data.symptom_analysis.chief_complaint:
                    features.append(self._create_feature(
                        name="chief_complaint",
                        value=inquiry_data.symptom_analysis.chiefcomplaint,
                        confidence=inquiry_data.symptom_analysis.confidence,
                        category="symptom",
                        source="inquiry_service"
                    ))

                # 症状列表
                for symptom in inquiry_data.symptom_analysis.symptoms:
                    features.append(self._create_feature(
                        name="symptom",
                        value=symptom.name,
                        confidence=symptom.confidence,
                        category="symptom",
                        source="inquiry_service"
                    ))

            # 使用LLM分析对话历史
            if self.use_advanced_extraction and inquiry_data.conversation_history:
                pass

            return features

        except Exception as e:
            logger.error(f"问诊特征提取失败: {e!s}")
            self.metrics.increment_error_count("symptom_feature_extraction")
            return features

    async def _extract_pulse_features(self, palpation_data: diagnosis_pb.PalpationData) -> list[diagnosis_pb.Feature]:
        """从切诊数据中提取特征"""
        features = []

        try:
            # 检查是否有脉象分析
            if not palpation_data.pulse_analysis and not palpation_data.pulse_wave_url:
                logger.warning("没有切诊数据, 跳过切诊特征提取")
                return features

            # 使用现有的脉象分析
            if palpation_data.pulse_analysis:

                # 脉象类型
                if pulse_analysis.pulse_pattern:
                    features.append(self._create_feature(
                        name="pulse_pattern",
                        value=pulse_analysis.pulsepattern,
                        confidence=pulse_analysis.confidence,
                        category="pulse",
                        source="palpation_service"
                    ))

                # 脉搏强度
                if pulse_analysis.pulse_strength:
                    features.append(self._create_feature(
                        name="pulse_strength",
                        value=pulse_analysis.pulsestrength,
                        confidence=pulse_analysis.confidence,
                        category="pulse",
                        source="palpation_service"
                    ))

                # 脉搏节律
                if pulse_analysis.pulse_rhythm:
                    features.append(self._create_feature(
                        name="pulse_rhythm",
                        value=pulse_analysis.pulserhythm,
                        confidence=pulse_analysis.confidence,
                        category="pulse",
                        source="palpation_service"
                    ))

                # 脉象深浅
                if pulse_analysis.pulse_depth:
                    features.append(self._create_feature(
                        name="pulse_depth",
                        value=pulse_analysis.pulsedepth,
                        confidence=pulse_analysis.confidence,
                        category="pulse",
                        source="palpation_service"
                    ))

            return features

        except Exception as e:
            logger.error(f"切诊特征提取失败: {e!s}")
            self.metrics.increment_error_count("pulse_feature_extraction")
            return features

    async def _llm_tongue_analysis(self, context: dict[str, Any]) -> list[diagnosis_pb.Feature]:
        """使用LLM进行舌象分析"""
        try:
            # 准备提示语
            template = self.prompt_templates.get('tongue_analysis', '')
            if not template:
                logger.error("未找到舌象分析提示语模板")
                return []

            # 构建舌象分析提示语
            prompt = template.format(
                tongue_image_url=context.get('tongue_image_url', '无图像链接'),
                existing_analysis=context.get('existing_analysis', '无已有分析')
            )

            # 构建消息列表
            messages = [
                {"role": "system", "content": "你是小艾智能体中的舌象分析专家, 负责从舌象图像中提取中医诊断特征。"},
                {"role": "user", "content": prompt}
            ]

            # 调用大模型进行舌象分析
            analysisresult, _ = await self.model_factory.generate_chat_completion(
                model="gpt-4-vision-preview" if context.get('tongue_image_url') else "gpt-4o-mini",
                messages=messages,
                temperature=0.2,
                max_tokens=1024
            )

            # 解析分析结果, 提取特征
            features = self._parse_tongue_analysis_result(analysisresult)

            return features

        except Exception as e:
            logger.error(f"LLM舌象分析失败: {e!s}")
            return []

    def _parse_tongue_analysis_result(self, analysis_text: str) -> list[diagnosis_pb.Feature]:
        """
        解析舌象分析文本, 提取特征

        Args:
            analysis_text: 分析文本

        Returns:
            特征列表
        """
        features = []

        try:
            # 使用正则表达式提取特征
            # 舌色
            re.search(r'舌色[: :]\s*(\S+)', analysistext)
            if tongue_color_match:
                features.append(self._create_feature(
                    name="tongue_color",
                    value=tongue_color_match.group(1),
                    confidence=0.8,  # 默认置信度
                    category="tongue",
                    source="llm_analysis"
                ))

            # 舌形
            re.search(r'舌形[: :]\s*(\S+)', analysistext)
            if tongue_shape_match:
                features.append(self._create_feature(
                    name="tongue_shape",
                    value=tongue_shape_match.group(1),
                    confidence=0.8,
                    category="tongue",
                    source="llm_analysis"
                ))

            # 舌苔色
            re.search(r'舌苔色[: :]\s*(\S+)', analysistext)
            if coating_color_match:
                features.append(self._create_feature(
                    name="coating_color",
                    value=coating_color_match.group(1),
                    confidence=0.8,
                    category="tongue",
                    source="llm_analysis"
                ))

            # 舌苔分布
            re.search(r'舌苔分布[: :]\s*(\S+)', analysistext)
            if coating_distribution_match:
                features.append(self._create_feature(
                    name="coating_distribution",
                    value=coating_distribution_match.group(1),
                    confidence=0.8,
                    category="tongue",
                    source="llm_analysis"
                ))

            # 舌质润燥
            re.search(r'舌质润燥[: :]\s*(\S+)', analysistext)
            if moisture_match:
                features.append(self._create_feature(
                    name="tongue_moisture",
                    value=moisture_match.group(1),
                    confidence=0.8,
                    category="tongue",
                    source="llm_analysis"
                ))

            return features

        except Exception as e:
            logger.error(f"解析舌象分析结果失败: {e!s}")
            return features

    def _create_feature(self, name: str, value: str, confidence: float, category: str, source: str) -> diagnosis_pb.Feature:
        """
        创建特征对象

        Args:
            name: 特征名称
            value: 特征值
            confidence: 置信度
            category: 类别
            source: 来源

        Returns:
            特征对象
        """
        feature = diagnosis_pb.Feature()
        feature.featureid = str(uuid.uuid4())
        feature.featurename = name
        feature.featurevalue = value
        feature.confidence = confidence
        feature.category = category
        feature.source = source
        feature.timestamp = int(time.time())

        return feature

    async def close(self):
        """关闭资源"""
        if self.model_factory:
            await self.model_factory.close()

        logger.info("四诊特征提取器已关闭")

# 单例实例
feature_extractor = None

def get_feature_extractor():
    """获取特征提取器单例"""
    global _feature_extractor
    if _feature_extractor is None:
        FeatureExtractor()
    return _feature_extractor
