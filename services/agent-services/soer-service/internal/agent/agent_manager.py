#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索尔智能体管理器
负责协调索尔智能体的不同功能组件，处理用户请求，生成健康计划和生活建议
"""
import logging
import asyncio
import uuid
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

from internal.agent.model_factory import ModelFactory
from pkg.utils.config_loader import get_config
from pkg.utils.metrics import get_metrics_collector

logger = logging.getLogger(__name__)

class AgentManager:
    """索尔智能体管理器"""
    
    def __init__(self):
        """初始化智能体管理器"""
        logger.info("初始化索尔智能体管理器")
        self.config = get_config()
        self.metrics = get_metrics_collector()
        
        # 初始化模型工厂
        self.model_factory = ModelFactory(self.config)
        
        # 加载提示词模板
        self.prompt_templates = self._load_prompt_templates()
        
        # 活跃会话状态
        self.active_sessions = {}
        
        logger.info("索尔智能体管理器初始化完成")
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载提示词模板"""
        prompts = {}
        prompts_dir = os.path.join('config', 'prompts', 'templates')
        
        # 检查目录是否存在，不存在则创建
        if not os.path.exists(prompts_dir):
            os.makedirs(prompts_dir, exist_ok=True)
            logger.warning(f"提示词模板目录不存在，已创建: {prompts_dir}")
            
            # 创建默认的健康计划提示词模板
            health_plan_template = """
你是索尔，一个专注于健康生活管理的AI助手。请根据用户的体质特点、健康目标和偏好生成一个个性化的健康计划。

用户信息:
- 用户ID: {user_id}
- 体质类型: {constitution_type}
- 健康目标: {health_goals}
- 个人偏好: {preferences}
- 当前季节: {current_season}

健康数据:
{health_data_formatted}

请提供以下方面的具体建议:
1. 饮食建议 (考虑中医五味理论和用户偏好)
2. 运动建议 (考虑用户的体质特点和运动偏好)
3. 生活作息建议 (考虑节气养生理念)
4. 营养补充建议 (如需要)
5. 日程安排 (一个典型的日计划)

每个建议应该具体且可执行，并与用户的体质类型相匹配。
            """
            
            # 创建默认的生活方式建议提示词模板
            lifestyle_template = """
你是索尔，一个专注于健康生活管理的AI助手。请根据用户当前的情境和环境，提供个性化的生活方式建议。

用户信息:
- 用户ID: {user_id}
- 体质类型: {constitution_type}
- 当前情境: {context}
- 所在位置: {location}
- 环境数据: {environment_data}
- 当前习惯: {current_habits}
- 工作时间: {work_schedule}
- 健康痛点: {pain_points}

请提供以下几个方面的实用建议:
1. 作息时间安排
2. 工作效率提升方法
3. 家居环境调整建议
4. 压力管理技巧
5. 社交健康维护

每个建议应该考虑用户的体质特点、当前情境和环境因素，并提供具体可行的行动方案。
            """
            
            # 创建默认的情绪分析提示词模板
            emotional_template = """
你是索尔，一个专注于健康生活管理的AI助手。请分析用户当前的情绪状态，并根据中医情志理论提供调节建议。

用户信息:
- 用户ID: {user_id}
- 体质类型: {constitution_type}

情绪输入:
{emotional_inputs}

情绪分析模型结果:
{emotion_analysis_results}

请提供以下内容:
1. 主要情绪状态及强度
2. 情绪对身体健康的影响 (基于中医情志理论)
3. 情绪调节建议 (至少3个针对性的方法)
4. 是否需要进一步的健康干预

分析应融合中医五志理论，说明情绪与相应脏腑的关联，并提供有效缓解的方法。
            """
            
            # 保存默认模板
            with open(os.path.join(prompts_dir, 'health_plan.txt'), 'w', encoding='utf-8') as f:
                f.write(health_plan_template)
            
            with open(os.path.join(prompts_dir, 'lifestyle.txt'), 'w', encoding='utf-8') as f:
                f.write(lifestyle_template)
                
            with open(os.path.join(prompts_dir, 'emotional.txt'), 'w', encoding='utf-8') as f:
                f.write(emotional_template)
        
        # 加载所有提示词模板
        try:
            for root, _, files in os.walk(prompts_dir):
                for file in files:
                    if file.endswith('.txt'):
                        template_name = os.path.splitext(file)[0]
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            prompts[template_name] = f.read()
                            logger.debug(f"已加载提示词模板: {template_name}")
        except Exception as e:
            logger.error(f"加载提示词模板失败: {str(e)}")
        
        return prompts
    
    async def process_request(self, user_id: str, request_data: Dict[str, Any], 
                              session_id: str = None) -> Dict[str, Any]:
        """
        处理用户请求
        
        Args:
            user_id: 用户ID
            request_data: 请求数据
            session_id: 会话ID，如果为None则创建新会话
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        # 如果没有提供会话ID，创建一个新的
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # 获取请求类型
        request_type = request_data.get("type", "")
        logger.info(f"处理用户 {user_id} 的 {request_type} 请求，会话ID: {session_id}")
        
        # 保存会话状态
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "start_time": datetime.now(),
            "request_type": request_type,
            "last_activity": datetime.now()
        }
        
        try:
            # 根据请求类型分发处理
            if request_type == "health_plan":
                result = await self._generate_health_plan(user_id, request_data, session_id)
            elif request_type == "lifestyle_advice":
                result = await self._generate_lifestyle_advice(user_id, request_data, session_id)
            elif request_type == "emotional_analysis":
                result = await self._analyze_emotion(user_id, request_data, session_id)
            else:
                logger.warning(f"未知的请求类型: {request_type}")
                result = {"error": f"不支持的请求类型: {request_type}"}
            
            # 更新会话最后活动时间
            if session_id in self.active_sessions:
                self.active_sessions[session_id]["last_activity"] = datetime.now()
                self.active_sessions[session_id]["status"] = "completed"
            
            return result
            
        except Exception as e:
            logger.error(f"处理请求失败: {str(e)}", exc_info=True)
            
            # 更新会话状态为失败
            if session_id in self.active_sessions:
                self.active_sessions[session_id]["status"] = "failed"
                self.active_sessions[session_id]["error"] = str(e)
            
            return {"error": f"处理请求失败: {str(e)}"}
    
    async def _generate_health_plan(self, user_id: str, request_data: Dict[str, Any], 
                                  session_id: str) -> Dict[str, Any]:
        """生成健康计划"""
        logger.info(f"为用户 {user_id} 生成健康计划")
        
        # 准备提示词模板
        template = self.prompt_templates.get("health_plan", "")
        if not template:
            raise ValueError("未找到健康计划提示词模板")
        
        # 提取请求数据
        constitution_type = request_data.get("constitution_type", "未知")
        health_goals = request_data.get("health_goals", [])
        preferences = request_data.get("preferences", {})
        current_season = request_data.get("current_season", "")
        health_data = request_data.get("health_data", {})
        
        # 格式化健康数据
        health_data_formatted = ""
        if health_data:
            health_data_formatted = "\n".join([f"- {k}: {v}" for k, v in health_data.items()])
        
        # 填充提示词模板
        prompt = template.format(
            user_id=user_id,
            constitution_type=constitution_type,
            health_goals=", ".join(health_goals),
            preferences=json.dumps(preferences, ensure_ascii=False),
            current_season=current_season,
            health_data_formatted=health_data_formatted
        )
        
        # 调用模型生成健康计划
        model = self.model_factory.get_model("health_plan")
        response = await model.generate(prompt)
        
        # 解析结果
        if not response:
            return {
                "error": "生成健康计划失败，模型返回空响应"
            }
        
        result = {
            "health_plan": response,
            "confidence": 0.85,  # 模型输出的置信度，实际应从模型中获取
            "created_at": datetime.now().isoformat()
        }
        
        # 记录指标
        self.metrics.increment_success_count("health_plan_generation")
        
        logger.info(f"用户 {user_id} 的健康计划生成完成")
        return result
    
    async def _generate_lifestyle_advice(self, user_id: str, request_data: Dict[str, Any], 
                                       session_id: str) -> Dict[str, Any]:
        """生成生活方式建议"""
        logger.info(f"为用户 {user_id} 生成生活方式建议")
        
        # 准备提示词模板
        template = self.prompt_templates.get("lifestyle", "")
        if not template:
            raise ValueError("未找到生活方式建议提示词模板")
        
        # 提取请求数据
        constitution_type = request_data.get("constitution_type", "未知")
        context = request_data.get("context", "")
        location = request_data.get("living_environment", {}).get("location", "")
        environment_data = json.dumps(request_data.get("living_environment", {}), ensure_ascii=False)
        current_habits = json.dumps(request_data.get("current_habits", {}), ensure_ascii=False)
        work_schedule = request_data.get("work_schedule", "")
        pain_points = ", ".join(request_data.get("pain_points", []))
        
        # 填充提示词模板
        prompt = template.format(
            user_id=user_id,
            constitution_type=constitution_type,
            context=context,
            location=location,
            environment_data=environment_data,
            current_habits=current_habits,
            work_schedule=work_schedule,
            pain_points=pain_points
        )
        
        # 调用模型生成生活方式建议
        model = self.model_factory.get_model("lifestyle")
        response = await model.generate(prompt)
        
        # 解析结果
        if not response:
            return {
                "error": "生成生活方式建议失败，模型返回空响应"
            }
        
        result = {
            "lifestyle_advice": response,
            "confidence": 0.80,  # 模型输出的置信度，实际应从模型中获取
            "created_at": datetime.now().isoformat()
        }
        
        # 记录指标
        self.metrics.increment_success_count("lifestyle_advice_generation")
        
        logger.info(f"用户 {user_id} 的生活方式建议生成完成")
        return result
    
    async def _analyze_emotion(self, user_id: str, request_data: Dict[str, Any], 
                             session_id: str) -> Dict[str, Any]:
        """分析情绪状态"""
        logger.info(f"分析用户 {user_id} 的情绪状态")
        
        # 准备提示词模板
        template = self.prompt_templates.get("emotional", "")
        if not template:
            raise ValueError("未找到情绪分析提示词模板")
        
        # 提取请求数据
        constitution_type = request_data.get("constitution_type", "未知")
        emotional_inputs = request_data.get("inputs", [])
        emotion_analysis_results = request_data.get("analysis_results", {})
        
        # 格式化情绪输入
        emotional_inputs_formatted = ""
        for i, input_data in enumerate(emotional_inputs):
            emotional_inputs_formatted += f"\n输入 {i+1}:\n"
            emotional_inputs_formatted += f"- 类型: {input_data.get('input_type', '')}\n"
            
            # 处理不同类型的输入
            if input_data.get('input_type') == 'text':
                content = input_data.get('data', b'').decode('utf-8') if isinstance(input_data.get('data'), bytes) else str(input_data.get('data', ''))
                emotional_inputs_formatted += f"- 内容: {content}\n"
            else:
                emotional_inputs_formatted += f"- 内容: [二进制数据]\n"
            
            emotional_inputs_formatted += f"- 时间: {input_data.get('capture_time', datetime.now())}\n"
        
        # 格式化分析结果
        analysis_results_formatted = ""
        if emotion_analysis_results:
            analysis_results_formatted = json.dumps(emotion_analysis_results, ensure_ascii=False, indent=2)
        
        # 填充提示词模板
        prompt = template.format(
            user_id=user_id,
            constitution_type=constitution_type,
            emotional_inputs=emotional_inputs_formatted,
            emotion_analysis_results=analysis_results_formatted
        )
        
        # 调用模型分析情绪
        model = self.model_factory.get_model("emotional")
        response = await model.generate(prompt)
        
        # 解析结果
        if not response:
            return {
                "error": "情绪分析失败，模型返回空响应"
            }
        
        # 解析模型输出的情绪分析结果
        # 这里简化处理，实际应该进行更复杂的解析
        lines = response.strip().split('\n')
        primary_emotion = ""
        health_impact = {}
        suggestions = []
        
        for line in lines:
            if "主要情绪" in line:
                primary_emotion = line.split("：")[-1].strip() if "：" in line else line.split(":")[-1].strip()
            elif "对身体健康的影响" in line:
                health_impact = {"tcm_interpretation": line.split("：")[-1].strip() if "：" in line else line.split(":")[-1].strip()}
            elif "调节建议" in line:
                # 收集后续行作为建议
                start_collecting = True
        
        result = {
            "emotional_analysis": response,
            "primary_emotion": primary_emotion,
            "health_impact": health_impact,
            "suggestions": suggestions,
            "confidence": 0.75,  # 模型输出的置信度，实际应从模型中获取
            "created_at": datetime.now().isoformat()
        }
        
        # 记录指标
        self.metrics.increment_success_count("emotional_analysis")
        
        logger.info(f"用户 {user_id} 的情绪分析完成")
        return result
    
    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """获取活跃会话列表"""
        return self.active_sessions
    
    def cleanup_expired_sessions(self, max_age_minutes: int = 60) -> int:
        """清理过期会话"""
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            last_activity = session.get("last_activity", session.get("start_time"))
            age_minutes = (now - last_activity).total_seconds() / 60
            
            if age_minutes > max_age_minutes:
                expired_sessions.append(session_id)
        
        # 删除过期会话
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
        
        return len(expired_sessions) 