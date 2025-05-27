#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小艾智能体 A2A 协议适配器
XiaoAI Agent A2A Protocol Adapter

将小艾智能体服务包装为符合 A2A 协议的智能体
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from python_a2a import A2AServer, AgentCard, skill, agent, TaskStatus, TaskState, Message, TextContent, MessageRole

from .service.xiaoai_service_impl import XiaoaiServiceImpl

logger = logging.getLogger(__name__)


@agent(
    name="小艾智能体",
    description="索克生活平台的智能健康管理助手，专注于用户交互、四诊协调和多模态输入处理",
    version="1.0.0",
    capabilities={
        "four_diagnoses_coordination": True,
        "multimodal_input_processing": True,
        "health_records_query": True,
        "voice_interaction": True,
        "accessibility_support": True,
        "google_a2a_compatible": True
    }
)
class XiaoAIA2AAgent(A2AServer):
    """小艾智能体 A2A 协议实现"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化小艾 A2A 智能体
        
        Args:
            config: 配置字典
        """
        # 创建智能体卡片
        agent_card = AgentCard(
            name="小艾智能体",
            description="索克生活平台的智能健康管理助手，专注于用户交互、四诊协调和多模态输入处理",
            url="http://localhost:5001",
            version="1.0.0",
            capabilities={
                "four_diagnoses_coordination": True,
                "multimodal_input_processing": True,
                "health_records_query": True,
                "voice_interaction": True,
                "accessibility_support": True,
                "google_a2a_compatible": True
            }
        )
        
        # 初始化 A2A 服务器
        super().__init__(agent_card=agent_card)
        
        # 初始化小艾服务实现
        self.xiaoai_service = XiaoaiServiceImpl(config)
        
        logger.info("小艾 A2A 智能体初始化完成")
    
    @skill(
        name="四诊协调",
        description="协调望、闻、问、切四种诊断方法，提供综合性的中医诊断建议",
        tags=["中医诊断", "四诊", "健康评估"]
    )
    async def coordinate_four_diagnoses(self, diagnosis_request: Dict[str, Any], 
                                      user_id: str, accessibility_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        四诊协调技能
        
        Args:
            diagnosis_request: 诊断请求数据
            user_id: 用户ID
            accessibility_options: 无障碍选项
            
        Returns:
            四诊协调结果
        """
        try:
            result = await self.xiaoai_service.coordinate_four_diagnoses_accessible(
                diagnosis_request, user_id, accessibility_options
            )
            return result
        except Exception as e:
            logger.error(f"四诊协调失败: {e}")
            return {"success": False, "error": str(e)}
    
    @skill(
        name="多模态输入处理",
        description="处理语音、图像、手语、文本等多种输入模式，支持无障碍交互",
        tags=["多模态", "无障碍", "语音识别", "图像分析"]
    )
    async def process_multimodal_input(self, multimodal_request: Dict[str, Any], 
                                     user_id: str, accessibility_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        多模态输入处理技能
        
        Args:
            multimodal_request: 多模态输入请求
            user_id: 用户ID
            accessibility_options: 无障碍选项
            
        Returns:
            多模态处理结果
        """
        try:
            result = await self.xiaoai_service.process_multimodal_input_accessible(
                multimodal_request, user_id, accessibility_options
            )
            return result
        except Exception as e:
            logger.error(f"多模态输入处理失败: {e}")
            return {"success": False, "error": str(e)}
    
    @skill(
        name="健康记录查询",
        description="查询用户的健康记录和历史数据，支持无障碍格式输出",
        tags=["健康记录", "数据查询", "历史数据"]
    )
    async def query_health_records(self, query_request: Dict[str, Any], 
                                 user_id: str, accessibility_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        健康记录查询技能
        
        Args:
            query_request: 查询请求
            user_id: 用户ID
            accessibility_options: 无障碍选项
            
        Returns:
            健康记录查询结果
        """
        try:
            result = await self.xiaoai_service.query_health_records_accessible(
                query_request, user_id, accessibility_options
            )
            return result
        except Exception as e:
            logger.error(f"健康记录查询失败: {e}")
            return {"success": False, "error": str(e)}
    
    @skill(
        name="语音交互",
        description="提供语音输入和输出的交互功能，支持多种语言和方言",
        tags=["语音交互", "语音识别", "语音合成"]
    )
    async def voice_interaction(self, audio_data: bytes, user_id: str, 
                              context: str = "general") -> Dict[str, Any]:
        """
        语音交互技能
        
        Args:
            audio_data: 音频数据
            user_id: 用户ID
            context: 交互上下文
            
        Returns:
            语音交互结果
        """
        try:
            result = await self.xiaoai_service.provide_voice_interaction_accessible(
                audio_data, user_id, context
            )
            return result
        except Exception as e:
            logger.error(f"语音交互失败: {e}")
            return {"success": False, "error": str(e)}
    
    @skill(
        name="生成健康报告",
        description="生成个性化的健康报告，支持多种格式和无障碍输出",
        tags=["健康报告", "个性化", "数据分析"]
    )
    async def generate_health_report(self, report_request: Dict[str, Any], 
                                   user_id: str) -> Dict[str, Any]:
        """
        生成健康报告技能
        
        Args:
            report_request: 报告请求
            user_id: 用户ID
            
        Returns:
            健康报告生成结果
        """
        try:
            result = await self.xiaoai_service.generate_accessible_health_report(
                report_request, user_id
            )
            return result
        except Exception as e:
            logger.error(f"健康报告生成失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def handle_task(self, task):
        """
        处理 A2A 任务
        
        Args:
            task: A2A 任务对象
            
        Returns:
            处理后的任务对象
        """
        try:
            # 解析消息内容
            message_data = task.message or {}
            content = message_data.get("content", {})
            
            if isinstance(content, dict):
                text = content.get("text", "")
            else:
                text = str(content)
            
            # 提取用户ID（从任务上下文或默认值）
            user_id = getattr(task, 'user_id', 'default_user')
            
            # 根据消息内容路由到相应的技能
            if "四诊" in text or "诊断" in text:
                # 四诊协调请求
                diagnosis_request = self._extract_diagnosis_request(text)
                result = await self.coordinate_four_diagnoses(diagnosis_request, user_id)
                
            elif "语音" in text or "说话" in text:
                # 语音交互请求
                result = {"message": "请提供音频数据进行语音交互", "type": "voice_request"}
                
            elif "健康记录" in text or "查询" in text:
                # 健康记录查询请求
                query_request = self._extract_query_request(text)
                result = await self.query_health_records(query_request, user_id)
                
            elif "报告" in text:
                # 健康报告生成请求
                report_request = self._extract_report_request(text)
                result = await self.generate_health_report(report_request, user_id)
                
            else:
                # 通用健康咨询
                result = await self._handle_general_health_consultation(text, user_id)
            
            # 构建响应
            response_text = self._format_response(result)
            
            task.artifacts = [{
                "parts": [{"type": "text", "text": response_text}]
            }]
            task.status = TaskStatus(state=TaskState.COMPLETED)
            
        except Exception as e:
            logger.error(f"任务处理失败: {e}")
            task.artifacts = [{
                "parts": [{"type": "text", "text": f"处理失败: {str(e)}"}]
            }]
            task.status = TaskStatus(
                state=TaskState.FAILED,
                message={"role": "agent", "content": {"type": "text", "text": f"处理失败: {str(e)}"}}
            )
        
        return task
    
    def _extract_diagnosis_request(self, text: str) -> Dict[str, Any]:
        """从文本中提取诊断请求"""
        return {
            "symptoms": self._extract_symptoms(text),
            "request_type": "four_diagnoses",
            "text": text
        }
    
    def _extract_query_request(self, text: str) -> Dict[str, Any]:
        """从文本中提取查询请求"""
        return {
            "query_type": "health_records",
            "keywords": text.split(),
            "text": text
        }
    
    def _extract_report_request(self, text: str) -> Dict[str, Any]:
        """从文本中提取报告请求"""
        return {
            "report_type": "comprehensive",
            "format": "text",
            "text": text
        }
    
    def _extract_symptoms(self, text: str) -> List[str]:
        """从文本中提取症状"""
        # 简单的症状提取逻辑
        symptom_keywords = ["头痛", "发热", "咳嗽", "乏力", "失眠", "食欲不振", "腹痛", "胸闷"]
        symptoms = []
        for keyword in symptom_keywords:
            if keyword in text:
                symptoms.append(keyword)
        return symptoms
    
    async def _handle_general_health_consultation(self, text: str, user_id: str) -> Dict[str, Any]:
        """处理通用健康咨询"""
        return {
            "response": f"您好！我是小艾智能体，您的健康管理助手。关于您的问题：{text}，我建议您可以通过四诊协调功能进行更详细的健康评估。",
            "suggestions": [
                "进行四诊协调评估",
                "查询历史健康记录",
                "生成个性化健康报告"
            ],
            "success": True
        }
    
    def _format_response(self, result: Dict[str, Any]) -> str:
        """格式化响应内容"""
        if not result.get("success", True):
            return f"处理失败: {result.get('error', '未知错误')}"
        
        if "response" in result:
            return result["response"]
        elif "accessible_content" in result:
            accessible = result["accessible_content"]
            if isinstance(accessible, dict):
                return accessible.get("accessible_content", str(accessible))
            return str(accessible)
        else:
            return json.dumps(result, ensure_ascii=False, indent=2)
    
    def close(self):
        """关闭智能体"""
        if hasattr(self.xiaoai_service, 'close'):
            self.xiaoai_service.close()
        logger.info("小艾 A2A 智能体已关闭")


# 创建智能体实例的工厂函数
def create_xiaoai_a2a_agent(config: Optional[Dict[str, Any]] = None) -> XiaoAIA2AAgent:
    """
    创建小艾 A2A 智能体实例
    
    Args:
        config: 配置字典
        
    Returns:
        小艾 A2A 智能体实例
    """
    return XiaoAIA2AAgent(config) 