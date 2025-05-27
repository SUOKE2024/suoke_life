#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索儿智能体 A2A 协议适配器
Soer Agent A2A Protocol Adapter

将索儿智能体服务包装为符合 A2A 协议的智能体
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from python_a2a import A2AServer, AgentCard, skill, agent, TaskStatus, TaskState, Message, TextContent, MessageRole

logger = logging.getLogger(__name__)


@agent(
    name="索儿智能体",
    description="索克生活平台的健康管理引擎，专注于生活健康管理、多设备数据整合、情绪感知和全生命周期健康陪伴",
    version="1.0.0",
    capabilities={
        "health_lifestyle_management": True,
        "sensor_data_integration": True,
        "emotion_recognition": True,
        "personalized_health_planning": True,
        "health_trend_prediction": True,
        "wellness_companionship": True,
        "nutrition_analysis": True,
        "google_a2a_compatible": True
    }
)
class SoerA2AAgent(A2AServer):
    """索儿智能体 A2A 协议实现"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化索儿 A2A 智能体
        
        Args:
            config: 配置字典
        """
        # 创建智能体卡片
        agent_card = AgentCard(
            name="索儿智能体",
            description="索克生活平台的健康管理引擎，专注于生活健康管理、多设备数据整合、情绪感知和全生命周期健康陪伴",
            url="http://localhost:5004",
            version="1.0.0",
            capabilities={
                "health_lifestyle_management": True,
                "sensor_data_integration": True,
                "emotion_recognition": True,
                "personalized_health_planning": True,
                "health_trend_prediction": True,
                "wellness_companionship": True,
                "nutrition_analysis": True,
                "google_a2a_compatible": True
            }
        )
        
        # 初始化 A2A 服务器
        super().__init__(agent_card=agent_card)
        
        # 初始化索儿服务组件（模拟实现）
        self.health_planner = self._init_health_planner()
        self.sensor_analyzer = self._init_sensor_analyzer()
        self.emotion_engine = self._init_emotion_engine()
        self.nutrition_analyzer = self._init_nutrition_analyzer()
        self.wellness_companion = self._init_wellness_companion()
        
        logger.info("索儿 A2A 智能体初始化完成")
    
    def _init_health_planner(self):
        """初始化健康规划器"""
        return {
            "constitution_plans": {
                "阳虚质": {
                    "diet": ["温热食物", "少食生冷", "适量羊肉、生姜"],
                    "exercise": ["太极拳", "八段锦", "慢跑"],
                    "lifestyle": ["早睡早起", "保暖", "避免过度劳累"]
                },
                "阴虚质": {
                    "diet": ["滋阴润燥", "银耳莲子", "少食辛辣"],
                    "exercise": ["瑜伽", "游泳", "散步"],
                    "lifestyle": ["充足睡眠", "避免熬夜", "保持心情平和"]
                }
            }
        }
    
    def _init_sensor_analyzer(self):
        """初始化传感器分析器"""
        return {
            "supported_devices": ["Apple Watch", "Fitbit", "Samsung Health", "小米手环"],
            "data_types": ["心率", "步数", "睡眠", "血压", "血氧"],
            "analysis_models": ["异常检测", "趋势预测", "健康评分"]
        }
    
    def _init_emotion_engine(self):
        """初始化情绪引擎"""
        return {
            "emotion_types": ["喜", "怒", "忧", "思", "悲", "恐", "惊"],
            "tcm_emotion_mapping": {
                "喜": "心",
                "怒": "肝", 
                "思": "脾",
                "悲": "肺",
                "恐": "肾"
            },
            "intervention_strategies": {
                "压力": ["深呼吸", "冥想", "运动"],
                "焦虑": ["正念练习", "音乐疗法", "芳香疗法"],
                "抑郁": ["阳光疗法", "社交活动", "专业咨询"]
            }
        }
    
    def _init_nutrition_analyzer(self):
        """初始化营养分析器"""
        return {
            "food_database": {
                "苹果": {"热量": 52, "维生素C": 4.6, "纤维": 2.4, "五味": "甘酸"},
                "胡萝卜": {"热量": 41, "维生素A": 835, "纤维": 2.8, "五味": "甘"},
                "菠菜": {"热量": 23, "铁": 2.7, "叶酸": 194, "五味": "甘"}
            },
            "tcm_nutrition": {
                "温热": ["生姜", "肉桂", "羊肉"],
                "寒凉": ["绿豆", "西瓜", "苦瓜"],
                "平性": ["大米", "土豆", "胡萝卜"]
            }
        }
    
    def _init_wellness_companion(self):
        """初始化健康陪伴器"""
        return {
            "companion_modes": ["日常陪伴", "运动督促", "饮食提醒", "情绪支持"],
            "interaction_styles": ["温暖关怀", "专业指导", "轻松幽默", "严格督促"],
            "personalization_factors": ["年龄", "性别", "体质", "健康目标", "生活习惯"]
        }
    
    @skill(
        name="个性化健康计划生成",
        description="基于用户体质、健康目标和生活习惯生成个性化的健康管理计划",
        tags=["健康规划", "个性化", "体质调理"]
    )
    async def generate_health_plan(self, user_id: str, constitution_type: str,
                                 health_goals: List[str] = None,
                                 preferences: Dict[str, Any] = None,
                                 current_season: str = "春季") -> Dict[str, Any]:
        """
        个性化健康计划生成技能
        
        Args:
            user_id: 用户ID
            constitution_type: 体质类型
            health_goals: 健康目标
            preferences: 用户偏好
            current_season: 当前季节
            
        Returns:
            健康计划生成结果
        """
        try:
            # 获取体质对应的基础计划
            base_plan = self.health_planner["constitution_plans"].get(
                constitution_type, 
                self.health_planner["constitution_plans"]["阳虚质"]
            )
            
            # 根据健康目标调整计划
            customized_plan = {
                "plan_id": f"plan_{user_id}_{constitution_type}",
                "user_id": user_id,
                "constitution_type": constitution_type,
                "season": current_season,
                "diet_recommendations": base_plan["diet"].copy(),
                "exercise_recommendations": base_plan["exercise"].copy(),
                "lifestyle_recommendations": base_plan["lifestyle"].copy(),
                "health_goals": health_goals or [],
                "duration": "30天",
                "created_at": "2024-01-01T00:00:00Z"
            }
            
            # 根据健康目标个性化调整
            if health_goals:
                for goal in health_goals:
                    if "减肥" in goal:
                        customized_plan["diet_recommendations"].extend(["控制热量", "增加蛋白质"])
                        customized_plan["exercise_recommendations"].extend(["有氧运动", "力量训练"])
                    elif "改善睡眠" in goal:
                        customized_plan["lifestyle_recommendations"].extend(["睡前冥想", "避免蓝光"])
                    elif "增强免疫" in goal:
                        customized_plan["diet_recommendations"].extend(["维生素C", "益生菌"])
            
            return {"success": True, "health_plan": customized_plan}
        except Exception as e:
            logger.error(f"健康计划生成失败: {e}")
            return {"success": False, "error": str(e)}
    
    @skill(
        name="传感器数据分析",
        description="分析来自多种设备的传感器数据，提供健康见解和异常检测",
        tags=["数据分析", "健康监测", "异常检测"]
    )
    async def analyze_sensor_data(self, user_id: str, device_type: str,
                                data_type: str, data_values: List[float],
                                timestamps: List[str] = None) -> Dict[str, Any]:
        """
        传感器数据分析技能
        
        Args:
            user_id: 用户ID
            device_type: 设备类型
            data_type: 数据类型
            data_values: 数据值列表
            timestamps: 时间戳列表
            
        Returns:
            传感器数据分析结果
        """
        try:
            # 基础数据统计
            if not data_values:
                return {"success": False, "error": "数据为空"}
            
            avg_value = sum(data_values) / len(data_values)
            max_value = max(data_values)
            min_value = min(data_values)
            
            # 健康状态评估
            health_status = "正常"
            recommendations = []
            
            if data_type == "心率":
                if avg_value > 100:
                    health_status = "偏高"
                    recommendations.append("建议适当休息，避免剧烈运动")
                elif avg_value < 60:
                    health_status = "偏低"
                    recommendations.append("建议增加有氧运动")
            elif data_type == "步数":
                if avg_value < 6000:
                    health_status = "活动不足"
                    recommendations.append("建议增加日常活动量")
                elif avg_value > 15000:
                    health_status = "活动充足"
                    recommendations.append("保持良好的运动习惯")
            elif data_type == "睡眠":
                if avg_value < 6:
                    health_status = "睡眠不足"
                    recommendations.append("建议保证充足睡眠时间")
                elif avg_value > 9:
                    health_status = "睡眠过多"
                    recommendations.append("建议调整作息时间")
            
            analysis_result = {
                "user_id": user_id,
                "device_type": device_type,
                "data_type": data_type,
                "statistics": {
                    "average": round(avg_value, 2),
                    "maximum": max_value,
                    "minimum": min_value,
                    "data_points": len(data_values)
                },
                "health_status": health_status,
                "recommendations": recommendations,
                "trend": "稳定" if max_value - min_value < avg_value * 0.2 else "波动较大",
                "analysis_time": "2024-01-01T00:00:00Z"
            }
            
            return {"success": True, "analysis": analysis_result}
        except Exception as e:
            logger.error(f"传感器数据分析失败: {e}")
            return {"success": False, "error": str(e)}
    
    @skill(
        name="情绪识别与干预",
        description="识别用户情绪状态，提供基于中医情志理论的情绪干预建议",
        tags=["情绪识别", "心理健康", "中医情志"]
    )
    async def analyze_emotion(self, user_id: str, input_type: str,
                            input_data: str, context: str = "") -> Dict[str, Any]:
        """
        情绪识别与干预技能
        
        Args:
            user_id: 用户ID
            input_type: 输入类型 (text, voice, physiological)
            input_data: 输入数据
            context: 上下文信息
            
        Returns:
            情绪分析结果
        """
        try:
            # 简单的情绪识别逻辑（实际应用中会使用更复杂的AI模型）
            emotion_keywords = {
                "喜": ["开心", "高兴", "快乐", "兴奋", "愉悦"],
                "怒": ["生气", "愤怒", "烦躁", "恼火", "气愤"],
                "忧": ["担心", "忧虑", "焦虑", "不安", "紧张"],
                "思": ["思考", "纠结", "犹豫", "困惑", "迷茫"],
                "悲": ["伤心", "难过", "沮丧", "失落", "悲伤"],
                "恐": ["害怕", "恐惧", "紧张", "不安", "担忧"],
                "惊": ["惊讶", "震惊", "意外", "吃惊", "惊奇"]
            }
            
            detected_emotions = []
            for emotion, keywords in emotion_keywords.items():
                for keyword in keywords:
                    if keyword in input_data:
                        detected_emotions.append(emotion)
                        break
            
            # 如果没有检测到明确情绪，默认为平和
            if not detected_emotions:
                detected_emotions = ["平和"]
            
            primary_emotion = detected_emotions[0] if detected_emotions else "平和"
            
            # 获取中医情志理论对应的脏腑
            affected_organ = self.emotion_engine["tcm_emotion_mapping"].get(primary_emotion, "心")
            
            # 获取干预策略
            intervention_strategies = []
            if primary_emotion in ["忧", "思"]:
                intervention_strategies = self.emotion_engine["intervention_strategies"]["焦虑"]
            elif primary_emotion == "怒":
                intervention_strategies = ["深呼吸", "散步", "听音乐"]
            elif primary_emotion == "悲":
                intervention_strategies = self.emotion_engine["intervention_strategies"]["抑郁"]
            else:
                intervention_strategies = ["保持当前状态", "适当运动", "规律作息"]
            
            emotion_result = {
                "user_id": user_id,
                "input_type": input_type,
                "detected_emotions": detected_emotions,
                "primary_emotion": primary_emotion,
                "emotion_intensity": "中等",  # 简化处理
                "tcm_analysis": {
                    "affected_organ": affected_organ,
                    "emotion_theory": f"{primary_emotion}伤{affected_organ}"
                },
                "intervention_strategies": intervention_strategies,
                "recommendations": [
                    f"根据中医理论，{primary_emotion}情绪主要影响{affected_organ}",
                    "建议通过以下方式调节情绪"
                ],
                "analysis_time": "2024-01-01T00:00:00Z"
            }
            
            return {"success": True, "emotion_analysis": emotion_result}
        except Exception as e:
            logger.error(f"情绪分析失败: {e}")
            return {"success": False, "error": str(e)}
    
    @skill(
        name="营养分析与建议",
        description="分析用户饮食营养，基于中医五味理论提供饮食建议",
        tags=["营养分析", "饮食建议", "中医五味"]
    )
    async def analyze_nutrition(self, user_id: str, food_items: List[str],
                              constitution_type: str = "", 
                              health_goals: List[str] = None) -> Dict[str, Any]:
        """
        营养分析与建议技能
        
        Args:
            user_id: 用户ID
            food_items: 食物列表
            constitution_type: 体质类型
            health_goals: 健康目标
            
        Returns:
            营养分析结果
        """
        try:
            nutrition_summary = {
                "total_calories": 0,
                "nutrients": {},
                "tcm_properties": {"温热": 0, "寒凉": 0, "平性": 0},
                "five_flavors": {"甘": 0, "酸": 0, "苦": 0, "辛": 0, "咸": 0}
            }
            
            analyzed_foods = []
            
            for food in food_items:
                food_info = self.nutrition_analyzer["food_database"].get(food, {
                    "热量": 50, "维生素C": 0, "纤维": 1, "五味": "甘"
                })
                
                analyzed_foods.append({
                    "name": food,
                    "calories": food_info["热量"],
                    "nutrients": {k: v for k, v in food_info.items() if k != "五味"},
                    "tcm_flavor": food_info.get("五味", "甘")
                })
                
                # 累计营养
                nutrition_summary["total_calories"] += food_info["热量"]
                
                # 累计五味
                flavor = food_info.get("五味", "甘")
                if flavor in nutrition_summary["five_flavors"]:
                    nutrition_summary["five_flavors"][flavor] += 1
                
                # 判断食物性质
                for property_type, foods in self.nutrition_analyzer["tcm_nutrition"].items():
                    if food in foods:
                        nutrition_summary["tcm_properties"][property_type] += 1
                        break
                else:
                    nutrition_summary["tcm_properties"]["平性"] += 1
            
            # 生成建议
            recommendations = []
            
            # 基于体质的建议
            if constitution_type == "阳虚质":
                if nutrition_summary["tcm_properties"]["寒凉"] > nutrition_summary["tcm_properties"]["温热"]:
                    recommendations.append("建议增加温热性食物，减少寒凉食物")
            elif constitution_type == "阴虚质":
                if nutrition_summary["tcm_properties"]["温热"] > nutrition_summary["tcm_properties"]["寒凉"]:
                    recommendations.append("建议增加滋阴润燥的食物，减少温热食物")
            
            # 五味平衡建议
            dominant_flavor = max(nutrition_summary["five_flavors"], key=nutrition_summary["five_flavors"].get)
            if nutrition_summary["five_flavors"][dominant_flavor] > len(food_items) * 0.6:
                recommendations.append(f"饮食中{dominant_flavor}味过多，建议增加其他口味的食物")
            
            nutrition_result = {
                "user_id": user_id,
                "analyzed_foods": analyzed_foods,
                "nutrition_summary": nutrition_summary,
                "tcm_analysis": {
                    "constitution_match": "适合" if len(recommendations) == 0 else "需要调整",
                    "five_flavor_balance": "均衡" if len(set(nutrition_summary["five_flavors"].values())) <= 2 else "不均衡"
                },
                "recommendations": recommendations if recommendations else ["饮食搭配合理，继续保持"],
                "analysis_time": "2024-01-01T00:00:00Z"
            }
            
            return {"success": True, "nutrition_analysis": nutrition_result}
        except Exception as e:
            logger.error(f"营养分析失败: {e}")
            return {"success": False, "error": str(e)}
    
    @skill(
        name="健康陪伴与支持",
        description="提供个性化的健康陪伴服务，包括日常关怀、督促和情感支持",
        tags=["健康陪伴", "情感支持", "行为督促"]
    )
    async def provide_wellness_companionship(self, user_id: str, interaction_type: str,
                                           user_message: str = "", 
                                           companion_mode: str = "日常陪伴") -> Dict[str, Any]:
        """
        健康陪伴与支持技能
        
        Args:
            user_id: 用户ID
            interaction_type: 交互类型 (greeting, encouragement, reminder, support)
            user_message: 用户消息
            companion_mode: 陪伴模式
            
        Returns:
            健康陪伴结果
        """
        try:
            companion_responses = {
                "greeting": [
                    "早上好！新的一天开始了，记得保持良好的心情哦～",
                    "您好！我是您的健康小伙伴索儿，今天感觉怎么样？",
                    "晚上好！今天的健康目标完成得如何？"
                ],
                "encouragement": [
                    "您今天的表现很棒！继续保持这样的健康习惯。",
                    "每一个小小的改变都是进步，为您的坚持点赞！",
                    "健康之路需要坚持，您已经做得很好了！"
                ],
                "reminder": [
                    "该喝水了！保持充足的水分摄入对健康很重要。",
                    "记得按时吃饭，规律的饮食有助于身体健康。",
                    "今天的运动目标还没完成，要不要出去走走？"
                ],
                "support": [
                    "我理解您现在的感受，健康管理确实需要时间和耐心。",
                    "遇到困难是正常的，我们一起想办法解决。",
                    "您并不孤单，我会一直陪伴您的健康之旅。"
                ]
            }
            
            # 选择合适的回应
            responses = companion_responses.get(interaction_type, companion_responses["greeting"])
            selected_response = responses[0]  # 简化选择逻辑
            
            # 根据用户消息个性化回应
            if user_message:
                if "累" in user_message or "疲劳" in user_message:
                    selected_response = "感觉累了吗？适当休息很重要，也可以尝试一些轻松的伸展运动。"
                elif "开心" in user_message or "高兴" in user_message:
                    selected_response = "看到您心情不错，我也很开心！保持这样的好心情对健康很有益。"
                elif "压力" in user_message or "焦虑" in user_message:
                    selected_response = "感受到压力了吗？试试深呼吸或者听听轻松的音乐，我陪着您。"
            
            # 添加个性化建议
            personalized_suggestions = []
            if companion_mode == "运动督促":
                personalized_suggestions = ["今天可以尝试15分钟的散步", "做几个简单的拉伸动作"]
            elif companion_mode == "饮食提醒":
                personalized_suggestions = ["记得吃早餐", "多吃蔬菜水果", "控制零食摄入"]
            elif companion_mode == "情绪支持":
                personalized_suggestions = ["保持积极心态", "与朋友聊天", "做喜欢的事情"]
            
            companionship_result = {
                "user_id": user_id,
                "interaction_type": interaction_type,
                "companion_mode": companion_mode,
                "response": selected_response,
                "personalized_suggestions": personalized_suggestions,
                "emotional_tone": "温暖关怀",
                "follow_up_actions": [
                    "继续关注用户状态",
                    "适时提供健康提醒",
                    "记录用户反馈"
                ],
                "interaction_time": "2024-01-01T00:00:00Z"
            }
            
            return {"success": True, "companionship": companionship_result}
        except Exception as e:
            logger.error(f"健康陪伴失败: {e}")
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
            
            # 提取用户ID
            user_id = getattr(task, 'user_id', 'default_user')
            
            # 根据消息内容路由到相应的技能
            if "健康计划" in text or "制定计划" in text:
                # 健康计划生成请求
                result = await self.generate_health_plan(
                    user_id=user_id,
                    constitution_type="阳虚质",  # 默认体质
                    health_goals=text.split(),
                    current_season="春季"
                )
                
            elif "数据分析" in text or "传感器" in text or "心率" in text or "步数" in text:
                # 传感器数据分析请求
                result = await self.analyze_sensor_data(
                    user_id=user_id,
                    device_type="智能手表",
                    data_type="心率",
                    data_values=[72, 75, 78, 73, 76]  # 模拟数据
                )
                
            elif "情绪" in text or "心情" in text or "感觉" in text:
                # 情绪分析请求
                result = await self.analyze_emotion(
                    user_id=user_id,
                    input_type="text",
                    input_data=text
                )
                
            elif "营养" in text or "饮食" in text or "食物" in text:
                # 营养分析请求
                food_items = ["苹果", "胡萝卜"]  # 简化处理
                result = await self.analyze_nutrition(
                    user_id=user_id,
                    food_items=food_items,
                    constitution_type="阳虚质"
                )
                
            elif "陪伴" in text or "支持" in text or "鼓励" in text:
                # 健康陪伴请求
                result = await self.provide_wellness_companionship(
                    user_id=user_id,
                    interaction_type="support",
                    user_message=text,
                    companion_mode="情绪支持"
                )
                
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
    
    async def _handle_general_health_consultation(self, text: str, user_id: str) -> Dict[str, Any]:
        """处理通用健康咨询"""
        return {
            "response": f"您好！我是索儿智能体，您的健康管理伙伴。关于您的问题：{text}，我可以为您提供以下服务：",
            "services": [
                "个性化健康计划制定",
                "多设备传感器数据分析",
                "情绪识别与心理支持",
                "营养分析与饮食建议",
                "全天候健康陪伴服务"
            ],
            "success": True
        }
    
    def _format_response(self, result: Dict[str, Any]) -> str:
        """格式化响应内容"""
        if not result.get("success", True):
            return f"处理失败: {result.get('error', '未知错误')}"
        
        if "response" in result:
            response = result["response"]
            if "services" in result:
                response += "\n\n可用服务："
                for service in result["services"]:
                    response += f"\n• {service}"
            return response
        elif "health_plan" in result:
            plan = result["health_plan"]
            response = f"为您制定的健康计划（{plan['constitution_type']}）：\n"
            response += f"饮食建议：{', '.join(plan['diet_recommendations'][:3])}\n"
            response += f"运动建议：{', '.join(plan['exercise_recommendations'][:3])}\n"
            response += f"生活建议：{', '.join(plan['lifestyle_recommendations'][:3])}"
            return response
        elif "analysis" in result:
            analysis = result["analysis"]
            response = f"{analysis['data_type']}数据分析结果：\n"
            response += f"平均值：{analysis['statistics']['average']}\n"
            response += f"健康状态：{analysis['health_status']}\n"
            if analysis['recommendations']:
                response += f"建议：{analysis['recommendations'][0]}"
            return response
        elif "emotion_analysis" in result:
            emotion = result["emotion_analysis"]
            response = f"情绪分析结果：\n"
            response += f"主要情绪：{emotion['primary_emotion']}\n"
            response += f"中医分析：{emotion['tcm_analysis']['emotion_theory']}\n"
            response += f"调节建议：{', '.join(emotion['intervention_strategies'][:3])}"
            return response
        elif "nutrition_analysis" in result:
            nutrition = result["nutrition_analysis"]
            response = f"营养分析结果：\n"
            response += f"总热量：{nutrition['nutrition_summary']['total_calories']}卡\n"
            response += f"中医评价：{nutrition['tcm_analysis']['constitution_match']}\n"
            if nutrition['recommendations']:
                response += f"建议：{nutrition['recommendations'][0]}"
            return response
        elif "companionship" in result:
            companion = result["companionship"]
            response = companion["response"]
            if companion["personalized_suggestions"]:
                response += f"\n\n个性化建议：{', '.join(companion['personalized_suggestions'])}"
            return response
        else:
            return json.dumps(result, ensure_ascii=False, indent=2)


# 创建智能体实例的工厂函数
def create_soer_a2a_agent(config: Optional[Dict[str, Any]] = None) -> SoerA2AAgent:
    """
    创建索儿 A2A 智能体实例
    
    Args:
        config: 配置字典
        
    Returns:
        索儿 A2A 智能体实例
    """
    return SoerA2AAgent(config) 