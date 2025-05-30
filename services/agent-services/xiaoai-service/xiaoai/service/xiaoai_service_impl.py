#!/usr/bin/env python

"""
小艾(xiaoai)智能体服务实现
集成无障碍服务, 支持四诊协调和多模态输入的无障碍功能
"""

import asyncio
import logging
import time
from typing import Any
import httpx

# 导入无障碍客户端
from ..integration.accessibility_client import (
    AccessibilityConfig,
    AccessibilityServiceClient,
)
from ..integration.enhanced_accessibility_client import EnhancedAccessibilityClient

logger = logging.getLogger(__name__)


class XiaoaiServiceImpl:
    """小艾智能体服务实现, 集成无障碍功能"""

    def __init__(self, config: dict[str, Any] | None = None):
        """
        初始化小艾服务

        Args:
            config: 配置字典
        """
        self.config = config or {}

        # 创建无障碍配置对象
        accessibilityconfig = AccessibilityConfig(enabled=False)  # 测试模式

        # 初始化增强版无障碍客户端
        self.accessibilityclient = EnhancedAccessibilityClient(accessibilityconfig)
        # 保留原始客户端作为备用
        self.basicaccessibility_client = AccessibilityServiceClient(accessibilityconfig)

        logger.info("小艾智能体服务初始化完成, 已集成无障碍功能")

    async def coordinate_four_diagnoses_accessible(self, diagnosis_request: dict[str, Any],
                                                 userid: str, accessibilityoptions: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        四诊协调(无障碍版本)

        Args:
            diagnosis_request: 诊断请求
            user_id: 用户ID
            accessibility_options: 无障碍选项

        Returns:
            无障碍格式的四诊协调结果
        """
        try:
            logger.info(f"开始四诊协调(无障碍): 用户={user_id}")

            # 执行四诊协调
            coordinationresult = await self._coordinate_four_diagnoses(diagnosisrequest, userid)

            # 转换为无障碍格式
            accessibility_options.get('format', 'audio')

            accessibleresult = await self.accessibility_client.convert_four_diagnoses_to_accessible(
                coordinationresult, userid, target_format
            )

            return {
                'coordination_result': coordinationresult,
                'accessible_content': accessibleresult,
                'success': True,
                'timestamp': time.time()
            }

        except Exception as e:
            logger.error(f"四诊协调(无障碍)失败: {e}")
            return {
                'coordination_result': {},
                'accessible_content': {
                    'accessible_content': f'四诊协调失败: {e!s}',
                    'success': False,
                    'error': str(e)
                },
                'success': False,
                'error': str(e)
            }

    async def process_multimodal_input_accessible(self, multimodal_request: dict[str, Any],
                                                userid: str, accessibilityoptions: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        多模态输入处理(无障碍版本)

        Args:
            multimodal_request: 多模态请求
            user_id: 用户ID
            accessibility_options: 无障碍选项

        Returns:
            无障碍格式的多模态处理结果
        """
        try:
            logger.info(f"开始多模态输入处理(无障碍): 用户={user_id}")

            # 根据输入类型进行处理
            inputtype = multimodal_request.get('input_type', 'unknown')
            multimodal_request.get('input_data', {})

            processingresult = {}

            if inputtype == 'voice':
                # 处理语音输入
                audiodata = input_data.get('audio_data', b'')
                await self.accessibility_client.process_voice_input(
                    audiodata, userid, 'diagnosis'
                )
                processing_result['voice_processing'] = voice_result

            elif inputtype == 'image':
                # 处理图像输入
                imagedata = input_data.get('image_data', b'')
                imagetype = input_data.get('image_type', 'tongue')
                await self.accessibility_client.process_image_input(
                    imagedata, userid, imagetype, 'looking_diagnosis'
                )
                processing_result['image_processing'] = image_result

            elif inputtype == 'sign_language':
                # 处理手语输入
                videodata = input_data.get('video_data', b'')
                await self.accessibility_client.process_sign_language_input(
                    videodata, userid, 'csl'
                )
                processing_result['sign_language_processing'] = sign_result

            elif inputtype == 'text':
                # 处理文本输入
                textcontent = input_data.get('text', '')
                await self._process_text_input(textcontent, userid)
                processing_result['text_processing'] = text_result

            # 转换为无障碍格式
            accessibility_options.get('format', 'audio')

            accessibleresult = await self.accessibility_client.convert_multimodal_input_to_accessible(
                processingresult, userid, target_format
            )

            return {
                'processing_result': processingresult,
                'accessible_content': accessibleresult,
                'success': True,
                'timestamp': time.time()
            }

        except Exception as e:
            logger.error(f"多模态输入处理(无障碍)失败: {e}")
            return {
                'processing_result': {},
                'accessible_content': {
                    'accessible_content': f'多模态输入处理失败: {e!s}',
                    'success': False,
                    'error': str(e)
                },
                'success': False,
                'error': str(e)
            }

    async def query_health_records_accessible(self, query_request: dict[str, Any],
                                            userid: str, accessibilityoptions: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        健康记录查询(无障碍版本)

        Args:
            query_request: 查询请求
            user_id: 用户ID
            accessibility_options: 无障碍选项

        Returns:
            无障碍格式的健康记录
        """
        try:
            logger.info(f"开始健康记录查询(无障碍): 用户={user_id}")

            # 执行健康记录查询
            queryresult = await self._query_health_records(queryrequest, userid)

            # 转换为无障碍格式
            accessibility_options.get('format', 'audio')

            accessibleresult = await self.accessibility_client.convert_health_records_to_accessible(
                queryresult, userid, target_format
            )

            return {
                'query_result': queryresult,
                'accessible_content': accessibleresult,
                'success': True,
                'timestamp': time.time()
            }

        except Exception as e:
            logger.error(f"健康记录查询(无障碍)失败: {e}")
            return {
                'query_result': {},
                'accessible_content': {
                    'accessible_content': f'健康记录查询失败: {e!s}',
                    'success': False,
                    'error': str(e)
                },
                'success': False,
                'error': str(e)
            }

    async def provide_voice_interaction_accessible(self, audio_data: bytes,
                                                 userid: str, context: str = "general") -> dict[str, Any]:
        """
        语音交互(无障碍版本)

        Args:
            audio_data: 音频数据
            user_id: 用户ID
            context: 交互上下文

        Returns:
            语音交互结果
        """
        try:
            logger.info(f"开始语音交互(无障碍): 用户={user_id}, 上下文={context}")

            # 使用无障碍服务进行语音处理
            await self.accessibility_client.process_voice_input_for_diagnosis(
                audiodata, userid, context
            )

            # 如果语音识别成功, 进行进一步处理
            if voice_result.get('success'):
                recognizedtext = voice_result.get('recognized_text', '')

                # 根据识别的文本进行相应处理
                if '四诊' in recognized_text or '诊断' in recognized_text:
                    # 触发四诊协调
                    diagnosisrequest = self._extract_diagnosis_request_from_text(recognizedtext)
                    await self.coordinate_four_diagnoses_accessible(
                        diagnosisrequest, userid, {'format': 'audio'}
                    )
                    voice_result['diagnosis_coordination'] = coordination_result

                elif '健康记录' in recognized_text or '病历' in recognized_text:
                    # 触发健康记录查询
                    queryrequest = self._extract_query_request_from_text(recognizedtext)
                    await self.query_health_records_accessible(
                        queryrequest, userid, {'format': 'audio'}
                    )
                    voice_result['health_records'] = query_result

                elif '症状' in recognized_text or '不舒服' in recognized_text:
                    # 触发症状分析
                    await self._analyze_symptoms_from_text(recognizedtext, userid)
                    voice_result['symptom_analysis'] = symptom_analysis

            return voice_result

        except Exception as e:
            logger.error(f"语音交互(无障碍)失败: {e}")
            return {
                'recognized_text': '',
                'response_text': f'语音交互失败: {e!s}',
                'response_audio': b'',
                'success': False,
                'error': str(e)
            }

    async def generate_accessible_health_report(self, report_request: dict[str, Any],
                                              userid: str) -> dict[str, Any]:
        """
        生成无障碍健康报告

        Args:
            report_request: 报告请求
            user_id: 用户ID

        Returns:
            无障碍格式的健康报告
        """
        try:
            logger.info(f"生成无障碍健康报告: 用户={user_id}")

            # 生成基础健康报告
            basereport = await self._generate_health_report(reportrequest, userid)

            # 转换为多种无障碍格式
            accessibleformats = {}

            # 音频格式
            await self.accessibility_client.generate_accessible_health_content(
                base_report.get('content', ''), userid, 'health_report', 'audio'
            )
            accessible_formats['audio'] = audio_result

            # 简化文本格式
            await self.accessibility_client.generate_accessible_health_content(
                base_report.get('content', ''), userid, 'health_report', 'simplified'
            )
            accessible_formats['simplified'] = simplified_result

            # 盲文格式
            await self.accessibility_client.generate_accessible_health_content(
                base_report.get('content', ''), userid, 'health_report', 'braille'
            )
            accessible_formats['braille'] = braille_result

            return {
                'base_report': basereport,
                'accessible_formats': accessibleformats,
                'success': True,
                'timestamp': time.time()
            }

        except Exception as e:
            logger.error(f"生成无障碍健康报告失败: {e}")
            return {
                'base_report': {},
                'accessible_formats': {},
                'success': False,
                'error': str(e)
            }

    # 内部辅助方法
    async def _coordinate_four_diagnoses(self, diagnosis_request: dict[str, Any], userid: str) -> dict[str, Any]:
        """执行四诊协调：并发调用diagnostic-services，聚合结果"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 假设diagnostic-services各服务的基础URL
            look_url = "http://diagnostic-look-service:8000/api/routes/analysis/tongue"
            listen_url = "http://diagnostic-listen-service:8000/diagnose/listen"
            inquiry_url = "http://diagnostic-inquiry-service:8000/diagnose/inquiry"
            palpation_url = "http://diagnostic-palpation-service:8000/diagnose/palpation"

            # 构造请求体（可根据实际需求调整）
            look_data = diagnosis_request.get("look", {})
            listen_data = diagnosis_request.get("listen", {})
            inquiry_data = diagnosis_request.get("inquiry", {})
            palpation_data = diagnosis_request.get("palpation", {})

            # 并发请求
            tasks = [
                client.post(look_url, json=look_data),
                client.post(listen_url, json=listen_data),
                client.post(inquiry_url, json=inquiry_data),
                client.post(palpation_url, json=palpation_data),
            ]
            responses = await asyncio.gather(*tasks, return_exceptions=True)

            diagnosis_results = []
            for idx, (service, resp) in enumerate(zip([
                "looking", "listening", "inquiry", "palpation"
            ], responses)):
                if isinstance(resp, Exception):
                    diagnosis_results.append({
                        "type": service,
                        "findings": "服务调用失败",
                        "confidence": 0.0,
                        "features": [],
                        "error": str(resp)
                    })
                elif resp.status_code == 200:
                    data = resp.json()
                    diagnosis_results.append({
                        "type": service,
                        "findings": data.get("findings", "无结果"),
                        "confidence": data.get("confidence", 0.0),
                        "features": data.get("features", []),
                        "raw": data
                    })
                else:
                    diagnosis_results.append({
                        "type": service,
                        "findings": "服务异常",
                        "confidence": 0.0,
                        "features": [],
                        "error": resp.text
                    })

            # 简单聚合分析（可扩展为更复杂的规则/AI分析）
            syndrome_analysis = {
                "primary_syndrome": "待分析",
                "secondary_syndrome": "待分析",
                "confidence": 0.0
            }
            constitution_analysis = {
                "constitution_type": "待分析",
                "score": 0.0
            }
            recommendations = [
                {
                    "type": "diet",
                    "content": "请根据四诊结果调整饮食",
                    "priority": 1
                },
                {
                    "type": "lifestyle",
                    "content": "保持良好作息，适度锻炼",
                    "priority": 2
                }
            ]

            return {
                "coordination_id": f"coord_{int(time.time())}",
                "user_id": userid,
                "diagnosis_results": diagnosis_results,
                "syndrome_analysis": syndrome_analysis,
                "constitution_analysis": constitution_analysis,
                "recommendations": recommendations
            }

    async def _query_health_records(self, query_request: dict[str, Any], userid: str) -> dict[str, Any]:
        """执行健康记录查询"""
        # 模拟健康记录查询
        await asyncio.sleep(0.2)

        return {
            'user_id': userid,
            'records': [
                {
                    'record_id': 'rec_001',
                    'date': '2024-01-15',
                    'type': 'diagnosis',
                    'content': '中医四诊: 肝火上炎证',
                    'doctor': '张中医',
                    'location': '索克生活健康中心'
                },
                {
                    'record_id': 'rec_002',
                    'date': '2024-01-10',
                    'type': 'treatment',
                    'content': '针灸治疗, 穴位: 太冲、行间',
                    'doctor': '李针灸师',
                    'location': '索克生活健康中心'
                }
            ],
            'summary': {
                'total_records': 2,
                'latest_diagnosis': '肝火上炎证',
                'treatment_progress': '症状有所改善'
            }
        }

    async def _process_text_input(self, text_content: str, userid: str) -> dict[str, Any]:
        """处理文本输入"""
        # 模拟文本处理
        await asyncio.sleep(0.1)

        return {
            'input_text': textcontent,
            'processed_content': f"已处理文本输入: {text_content}",
            'extracted_symptoms': self._extract_symptoms_from_text(textcontent),
            'confidence': 0.90
        }

    async def _generate_health_report(self, report_request: dict[str, Any], userid: str) -> dict[str, Any]:
        """生成健康报告"""
        # 模拟健康报告生成
        await asyncio.sleep(0.25)

        return {
            'report_id': f"report_{int(time.time())}",
            'user_id': userid,
            'report_type': report_request.get('type', 'comprehensive'),
            'content': """
            健康报告摘要:

            1. 体质分析: 阴虚质, 需要滋阴养血
            2. 主要症状: 头痛、口干、失眠
            3. 诊断结果: 肝火上炎证
            4. 治疗建议:
               - 饮食调理: 多食滋阴清热食物
               - 生活方式: 规律作息, 避免熬夜
               - 中药调理: 可服用知柏地黄丸
            5. 随访计划: 2周后复诊
            """,
            'generation_time': time.time(),
            'validity_period': '30天'
        }

    async def _analyze_symptoms_from_text(self, text: str, userid: str) -> dict[str, Any]:
        """从文本中分析症状"""
        # 模拟症状分析
        await asyncio.sleep(0.15)

        symptoms = self._extract_symptoms_from_text(text)

        return {
            'user_id': userid,
            'input_text': text,
            'identified_symptoms': symptoms,
            'preliminary_analysis': {
                'possible_syndrome': '肝火上炎' if '头痛' in symptoms else '气血不足',
                'severity': 'moderate',
                'urgency': 'non_urgent'
            },
            'recommendations': [
                '建议进行完整的四诊检查',
                '注意休息和饮食调理',
                '如症状持续, 请及时就医'
            ]
        }

    def _extract_symptoms_from_text(self, text: str) -> list[str]:
        """从文本中提取症状"""
        symptoms = []


        for keyword in symptom_keywords:
            if keyword in text:
                symptoms.append(keyword)

        return symptoms

    def _extract_diagnosis_request_from_text(self, text: str) -> dict[str, Any]:
        """从文本中提取诊断请求"""
        request = {
            'include_looking': True,
            'include_listening': True,
            'include_inquiry': True,
            'include_palpation': True
        }

        if '望诊' in text:
            request['focus'] = 'looking'
        elif '闻诊' in text:
            request['focus'] = 'listening'
        elif '问诊' in text:
            request['focus'] = 'inquiry'
        elif '切诊' in text:
            request['focus'] = 'palpation'

        return request

    def _extract_query_request_from_text(self, text: str) -> dict[str, Any]:
        """从文本中提取查询请求"""
        request = {
            'query_type': 'recent',
            'limit': 10
        }

        if '最近' in text:
            request['query_type'] = 'recent'
        elif '全部' in text:
            request['query_type'] = 'all'
        elif '诊断' in text:
            request['record_type'] = 'diagnosis'
        elif '治疗' in text:
            request['record_type'] = 'treatment'

        return request

    def close(self):
        """关闭服务"""
        if self.accessibility_client:
            self.accessibility_client.close()
        logger.info("小艾智能体服务已关闭")
