#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
小艾(xiaoai)智能体服务实现
集成无障碍服务，支持四诊协调和多模态输入的无障碍功能
"""

import logging
import asyncio
import time
from typing import Dict, Any, Optional, List, Union

# 导入无障碍客户端
from ..integration.accessibility_client import AccessibilityServiceClient, AccessibilityConfig
from ..integration.enhanced_accessibility_client import EnhancedAccessibilityClient

logger = logging.getLogger(__name__)


class XiaoaiServiceImpl:
    """小艾智能体服务实现，集成无障碍功能"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化小艾服务
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        # 创建无障碍配置对象
        accessibility_config = AccessibilityConfig(enabled=False)  # 测试模式
        
        # 初始化增强版无障碍客户端
        self.accessibility_client = EnhancedAccessibilityClient(accessibility_config)
        # 保留原始客户端作为备用
        self.basic_accessibility_client = AccessibilityServiceClient(accessibility_config)
        
        logger.info("小艾智能体服务初始化完成，已集成无障碍功能")
    
    async def coordinate_four_diagnoses_accessible(self, diagnosis_request: Dict[str, Any], 
                                                 user_id: str, accessibility_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        四诊协调（无障碍版本）
        
        Args:
            diagnosis_request: 诊断请求
            user_id: 用户ID
            accessibility_options: 无障碍选项
            
        Returns:
            无障碍格式的四诊协调结果
        """
        try:
            logger.info(f"开始四诊协调（无障碍）: 用户={user_id}")
            
            # 执行四诊协调
            coordination_result = await self._coordinate_four_diagnoses(diagnosis_request, user_id)
            
            # 转换为无障碍格式
            accessibility_options = accessibility_options or {}
            target_format = accessibility_options.get('format', 'audio')
            
            accessible_result = await self.accessibility_client.convert_four_diagnoses_to_accessible(
                coordination_result, user_id, target_format
            )
            
            return {
                'coordination_result': coordination_result,
                'accessible_content': accessible_result,
                'success': True,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"四诊协调（无障碍）失败: {e}")
            return {
                'coordination_result': {},
                'accessible_content': {
                    'accessible_content': f'四诊协调失败: {str(e)}',
                    'success': False,
                    'error': str(e)
                },
                'success': False,
                'error': str(e)
            }
    
    async def process_multimodal_input_accessible(self, multimodal_request: Dict[str, Any], 
                                                user_id: str, accessibility_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        多模态输入处理（无障碍版本）
        
        Args:
            multimodal_request: 多模态请求
            user_id: 用户ID
            accessibility_options: 无障碍选项
            
        Returns:
            无障碍格式的多模态处理结果
        """
        try:
            logger.info(f"开始多模态输入处理（无障碍）: 用户={user_id}")
            
            # 根据输入类型进行处理
            input_type = multimodal_request.get('input_type', 'unknown')
            input_data = multimodal_request.get('input_data', {})
            
            processing_result = {}
            
            if input_type == 'voice':
                # 处理语音输入
                audio_data = input_data.get('audio_data', b'')
                voice_result = await self.accessibility_client.process_voice_input(
                    audio_data, user_id, 'diagnosis'
                )
                processing_result['voice_processing'] = voice_result
                
            elif input_type == 'image':
                # 处理图像输入
                image_data = input_data.get('image_data', b'')
                image_type = input_data.get('image_type', 'tongue')
                image_result = await self.accessibility_client.process_image_input(
                    image_data, user_id, image_type, 'looking_diagnosis'
                )
                processing_result['image_processing'] = image_result
                
            elif input_type == 'sign_language':
                # 处理手语输入
                video_data = input_data.get('video_data', b'')
                sign_result = await self.accessibility_client.process_sign_language_input(
                    video_data, user_id, 'csl'
                )
                processing_result['sign_language_processing'] = sign_result
                
            elif input_type == 'text':
                # 处理文本输入
                text_content = input_data.get('text', '')
                text_result = await self._process_text_input(text_content, user_id)
                processing_result['text_processing'] = text_result
            
            # 转换为无障碍格式
            accessibility_options = accessibility_options or {}
            target_format = accessibility_options.get('format', 'audio')
            
            accessible_result = await self.accessibility_client.convert_multimodal_input_to_accessible(
                processing_result, user_id, target_format
            )
            
            return {
                'processing_result': processing_result,
                'accessible_content': accessible_result,
                'success': True,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"多模态输入处理（无障碍）失败: {e}")
            return {
                'processing_result': {},
                'accessible_content': {
                    'accessible_content': f'多模态输入处理失败: {str(e)}',
                    'success': False,
                    'error': str(e)
                },
                'success': False,
                'error': str(e)
            }
    
    async def query_health_records_accessible(self, query_request: Dict[str, Any], 
                                            user_id: str, accessibility_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        健康记录查询（无障碍版本）
        
        Args:
            query_request: 查询请求
            user_id: 用户ID
            accessibility_options: 无障碍选项
            
        Returns:
            无障碍格式的健康记录
        """
        try:
            logger.info(f"开始健康记录查询（无障碍）: 用户={user_id}")
            
            # 执行健康记录查询
            query_result = await self._query_health_records(query_request, user_id)
            
            # 转换为无障碍格式
            accessibility_options = accessibility_options or {}
            target_format = accessibility_options.get('format', 'audio')
            
            accessible_result = await self.accessibility_client.convert_health_records_to_accessible(
                query_result, user_id, target_format
            )
            
            return {
                'query_result': query_result,
                'accessible_content': accessible_result,
                'success': True,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"健康记录查询（无障碍）失败: {e}")
            return {
                'query_result': {},
                'accessible_content': {
                    'accessible_content': f'健康记录查询失败: {str(e)}',
                    'success': False,
                    'error': str(e)
                },
                'success': False,
                'error': str(e)
            }
    
    async def provide_voice_interaction_accessible(self, audio_data: bytes, 
                                                 user_id: str, context: str = "general") -> Dict[str, Any]:
        """
        语音交互（无障碍版本）
        
        Args:
            audio_data: 音频数据
            user_id: 用户ID
            context: 交互上下文
            
        Returns:
            语音交互结果
        """
        try:
            logger.info(f"开始语音交互（无障碍）: 用户={user_id}, 上下文={context}")
            
            # 使用无障碍服务进行语音处理
            voice_result = await self.accessibility_client.process_voice_input_for_diagnosis(
                audio_data, user_id, context
            )
            
            # 如果语音识别成功，进行进一步处理
            if voice_result.get('success'):
                recognized_text = voice_result.get('recognized_text', '')
                
                # 根据识别的文本进行相应处理
                if '四诊' in recognized_text or '诊断' in recognized_text:
                    # 触发四诊协调
                    diagnosis_request = self._extract_diagnosis_request_from_text(recognized_text)
                    coordination_result = await self.coordinate_four_diagnoses_accessible(
                        diagnosis_request, user_id, {'format': 'audio'}
                    )
                    voice_result['diagnosis_coordination'] = coordination_result
                
                elif '健康记录' in recognized_text or '病历' in recognized_text:
                    # 触发健康记录查询
                    query_request = self._extract_query_request_from_text(recognized_text)
                    query_result = await self.query_health_records_accessible(
                        query_request, user_id, {'format': 'audio'}
                    )
                    voice_result['health_records'] = query_result
                
                elif '症状' in recognized_text or '不舒服' in recognized_text:
                    # 触发症状分析
                    symptom_analysis = await self._analyze_symptoms_from_text(recognized_text, user_id)
                    voice_result['symptom_analysis'] = symptom_analysis
            
            return voice_result
            
        except Exception as e:
            logger.error(f"语音交互（无障碍）失败: {e}")
            return {
                'recognized_text': '',
                'response_text': f'语音交互失败: {str(e)}',
                'response_audio': b'',
                'success': False,
                'error': str(e)
            }
    
    async def generate_accessible_health_report(self, report_request: Dict[str, Any], 
                                              user_id: str) -> Dict[str, Any]:
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
            base_report = await self._generate_health_report(report_request, user_id)
            
            # 转换为多种无障碍格式
            accessible_formats = {}
            
            # 音频格式
            audio_result = await self.accessibility_client.generate_accessible_health_content(
                base_report.get('content', ''), user_id, 'health_report', 'audio'
            )
            accessible_formats['audio'] = audio_result
            
            # 简化文本格式
            simplified_result = await self.accessibility_client.generate_accessible_health_content(
                base_report.get('content', ''), user_id, 'health_report', 'simplified'
            )
            accessible_formats['simplified'] = simplified_result
            
            # 盲文格式
            braille_result = await self.accessibility_client.generate_accessible_health_content(
                base_report.get('content', ''), user_id, 'health_report', 'braille'
            )
            accessible_formats['braille'] = braille_result
            
            return {
                'base_report': base_report,
                'accessible_formats': accessible_formats,
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
    async def _coordinate_four_diagnoses(self, diagnosis_request: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """执行四诊协调"""
        # 模拟四诊协调
        await asyncio.sleep(0.3)
        
        return {
            'coordination_id': f"coord_{int(time.time())}",
            'user_id': user_id,
            'diagnosis_results': [
                {
                    'type': 'looking',
                    'findings': '舌质偏红，苔薄白',
                    'confidence': 0.85,
                    'features': ['舌红', '苔薄白']
                },
                {
                    'type': 'listening',
                    'findings': '声音洪亮，呼吸平稳',
                    'confidence': 0.90,
                    'features': ['声洪亮', '呼吸稳']
                },
                {
                    'type': 'inquiry',
                    'findings': '头痛，口干，睡眠不佳',
                    'confidence': 0.95,
                    'features': ['头痛', '口干', '失眠']
                },
                {
                    'type': 'palpation',
                    'findings': '脉象弦数',
                    'confidence': 0.80,
                    'features': ['脉弦', '脉数']
                }
            ],
            'syndrome_analysis': {
                'primary_syndrome': '肝火上炎',
                'secondary_syndrome': '阴虚内热',
                'confidence': 0.88
            },
            'constitution_analysis': {
                'constitution_type': '阴虚质',
                'score': 0.75
            },
            'recommendations': [
                {
                    'type': 'diet',
                    'content': '多食滋阴清热食物，如银耳、百合',
                    'priority': 1
                },
                {
                    'type': 'lifestyle',
                    'content': '保证充足睡眠，避免熬夜',
                    'priority': 2
                }
            ]
        }
    
    async def _query_health_records(self, query_request: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """执行健康记录查询"""
        # 模拟健康记录查询
        await asyncio.sleep(0.2)
        
        return {
            'user_id': user_id,
            'records': [
                {
                    'record_id': 'rec_001',
                    'date': '2024-01-15',
                    'type': 'diagnosis',
                    'content': '中医四诊：肝火上炎证',
                    'doctor': '张中医',
                    'location': '索克生活健康中心'
                },
                {
                    'record_id': 'rec_002',
                    'date': '2024-01-10',
                    'type': 'treatment',
                    'content': '针灸治疗，穴位：太冲、行间',
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
    
    async def _process_text_input(self, text_content: str, user_id: str) -> Dict[str, Any]:
        """处理文本输入"""
        # 模拟文本处理
        await asyncio.sleep(0.1)
        
        return {
            'input_text': text_content,
            'processed_content': f"已处理文本输入：{text_content}",
            'extracted_symptoms': self._extract_symptoms_from_text(text_content),
            'confidence': 0.90
        }
    
    async def _generate_health_report(self, report_request: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """生成健康报告"""
        # 模拟健康报告生成
        await asyncio.sleep(0.25)
        
        return {
            'report_id': f"report_{int(time.time())}",
            'user_id': user_id,
            'report_type': report_request.get('type', 'comprehensive'),
            'content': """
            健康报告摘要：
            
            1. 体质分析：阴虚质，需要滋阴养血
            2. 主要症状：头痛、口干、失眠
            3. 诊断结果：肝火上炎证
            4. 治疗建议：
               - 饮食调理：多食滋阴清热食物
               - 生活方式：规律作息，避免熬夜
               - 中药调理：可服用知柏地黄丸
            5. 随访计划：2周后复诊
            """,
            'generation_time': time.time(),
            'validity_period': '30天'
        }
    
    async def _analyze_symptoms_from_text(self, text: str, user_id: str) -> Dict[str, Any]:
        """从文本中分析症状"""
        # 模拟症状分析
        await asyncio.sleep(0.15)
        
        symptoms = self._extract_symptoms_from_text(text)
        
        return {
            'user_id': user_id,
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
                '如症状持续，请及时就医'
            ]
        }
    
    def _extract_symptoms_from_text(self, text: str) -> List[str]:
        """从文本中提取症状"""
        symptoms = []
        
        symptom_keywords = ['头痛', '头晕', '失眠', '口干', '咳嗽', '发热', '乏力', '胸闷', '腹痛']
        
        for keyword in symptom_keywords:
            if keyword in text:
                symptoms.append(keyword)
        
        return symptoms
    
    def _extract_diagnosis_request_from_text(self, text: str) -> Dict[str, Any]:
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
    
    def _extract_query_request_from_text(self, text: str) -> Dict[str, Any]:
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