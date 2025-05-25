#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
记忆辅助服务接口定义
为认知障碍用户提供记忆支持和认知辅助功能的标准接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum


class MemoryType(Enum):
    """记忆类型"""
    SHORT_TERM = "short_term"           # 短期记忆
    LONG_TERM = "long_term"             # 长期记忆
    WORKING = "working"                 # 工作记忆
    EPISODIC = "episodic"               # 情景记忆
    SEMANTIC = "semantic"               # 语义记忆
    PROCEDURAL = "procedural"           # 程序性记忆


class ReminderType(Enum):
    """提醒类型"""
    MEDICATION = "medication"           # 用药提醒
    APPOINTMENT = "appointment"         # 预约提醒
    TASK = "task"                      # 任务提醒
    PERSON = "person"                  # 人物提醒
    LOCATION = "location"              # 位置提醒
    EVENT = "event"                    # 事件提醒
    ROUTINE = "routine"                # 日常提醒


class CognitiveLevel(Enum):
    """认知水平"""
    NORMAL = "normal"                  # 正常
    MILD_IMPAIRMENT = "mild"           # 轻度障碍
    MODERATE_IMPAIRMENT = "moderate"   # 中度障碍
    SEVERE_IMPAIRMENT = "severe"       # 重度障碍


class AssistanceMode(Enum):
    """辅助模式"""
    PROACTIVE = "proactive"            # 主动提醒
    REACTIVE = "reactive"              # 被动响应
    ADAPTIVE = "adaptive"              # 自适应
    SCHEDULED = "scheduled"            # 定时提醒


class MemoryTrigger(Enum):
    """记忆触发器"""
    TIME_BASED = "time_based"          # 基于时间
    LOCATION_BASED = "location_based"  # 基于位置
    CONTEXT_BASED = "context_based"    # 基于上下文
    PERSON_BASED = "person_based"      # 基于人物
    ACTIVITY_BASED = "activity_based"  # 基于活动
    EMOTION_BASED = "emotion_based"    # 基于情绪


class MemoryCategory(Enum):
    """记忆分类"""
    PERSONAL = "personal"              # 个人记忆
    MEDICAL = "medical"                # 医疗记忆
    SOCIAL = "social"                  # 社交记忆
    WORK = "work"                      # 工作记忆
    FAMILY = "family"                  # 家庭记忆
    EDUCATION = "education"            # 教育记忆
    HOBBY = "hobby"                    # 爱好记忆


class AssistanceLevel(Enum):
    """辅助级别"""
    MINIMAL = "minimal"                # 最小辅助
    MODERATE = "moderate"              # 中等辅助
    INTENSIVE = "intensive"            # 密集辅助
    COMPREHENSIVE = "comprehensive"    # 全面辅助


class IMemoryAssistanceService(ABC):
    """
    记忆辅助服务接口
    为认知障碍用户提供记忆支持和认知辅助功能
    """
    
    @abstractmethod
    async def initialize(self):
        """
        初始化记忆辅助服务
        """
        pass
    
    @abstractmethod
    async def create_user_profile(self, 
                                user_id: str,
                                cognitive_level: CognitiveLevel,
                                memory_preferences: Dict[str, Any],
                                medical_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        创建用户认知档案
        
        Args:
            user_id: 用户ID
            cognitive_level: 认知水平
            memory_preferences: 记忆偏好设置
            medical_info: 医疗信息
            
        Returns:
            档案创建结果
        """
        pass
    
    @abstractmethod
    async def store_memory(self, 
                         user_id: str,
                         memory_content: Dict[str, Any],
                         memory_type: MemoryType,
                         importance_level: int = 5) -> Dict[str, Any]:
        """
        存储记忆信息
        
        Args:
            user_id: 用户ID
            memory_content: 记忆内容
            memory_type: 记忆类型
            importance_level: 重要性级别 (1-10)
            
        Returns:
            存储结果
        """
        pass
    
    @abstractmethod
    async def retrieve_memory(self, 
                            user_id: str,
                            query: Dict[str, Any],
                            memory_types: List[MemoryType] = None) -> Dict[str, Any]:
        """
        检索记忆信息
        
        Args:
            user_id: 用户ID
            query: 查询条件
            memory_types: 记忆类型列表
            
        Returns:
            检索结果
        """
        pass
    
    @abstractmethod
    async def create_reminder(self, 
                            user_id: str,
                            reminder_type: ReminderType,
                            content: Dict[str, Any],
                            schedule: Dict[str, Any],
                            settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        创建提醒
        
        Args:
            user_id: 用户ID
            reminder_type: 提醒类型
            content: 提醒内容
            schedule: 调度设置
            settings: 提醒设置
            
        Returns:
            创建结果
        """
        pass
    
    @abstractmethod
    async def update_reminder(self, 
                            user_id: str,
                            reminder_id: str,
                            updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新提醒
        
        Args:
            user_id: 用户ID
            reminder_id: 提醒ID
            updates: 更新内容
            
        Returns:
            更新结果
        """
        pass
    
    @abstractmethod
    async def delete_reminder(self, 
                            user_id: str,
                            reminder_id: str) -> Dict[str, Any]:
        """
        删除提醒
        
        Args:
            user_id: 用户ID
            reminder_id: 提醒ID
            
        Returns:
            删除结果
        """
        pass
    
    @abstractmethod
    async def get_user_reminders(self, 
                               user_id: str,
                               reminder_type: ReminderType = None,
                               status: str = None) -> Dict[str, Any]:
        """
        获取用户提醒列表
        
        Args:
            user_id: 用户ID
            reminder_type: 提醒类型过滤
            status: 状态过滤
            
        Returns:
            提醒列表
        """
        pass
    
    @abstractmethod
    async def perform_cognitive_assessment(self, 
                                         user_id: str,
                                         assessment_type: str = "comprehensive") -> Dict[str, Any]:
        """
        执行认知评估
        
        Args:
            user_id: 用户ID
            assessment_type: 评估类型
            
        Returns:
            评估结果
        """
        pass
    
    @abstractmethod
    async def get_cognitive_exercises(self, 
                                    user_id: str,
                                    cognitive_domain: str = None,
                                    difficulty_level: int = None) -> Dict[str, Any]:
        """
        获取认知训练练习
        
        Args:
            user_id: 用户ID
            cognitive_domain: 认知域
            difficulty_level: 难度级别
            
        Returns:
            练习列表
        """
        pass
    
    @abstractmethod
    async def record_exercise_result(self, 
                                   user_id: str,
                                   exercise_id: str,
                                   result: Dict[str, Any]) -> Dict[str, Any]:
        """
        记录练习结果
        
        Args:
            user_id: 用户ID
            exercise_id: 练习ID
            result: 练习结果
            
        Returns:
            记录结果
        """
        pass
    
    @abstractmethod
    async def analyze_memory_patterns(self, 
                                    user_id: str,
                                    time_range: Dict[str, str] = None) -> Dict[str, Any]:
        """
        分析记忆模式
        
        Args:
            user_id: 用户ID
            time_range: 时间范围
            
        Returns:
            分析结果
        """
        pass
    
    @abstractmethod
    async def get_memory_insights(self, 
                                user_id: str,
                                insight_type: str = "summary") -> Dict[str, Any]:
        """
        获取记忆洞察
        
        Args:
            user_id: 用户ID
            insight_type: 洞察类型
            
        Returns:
            洞察结果
        """
        pass
    
    @abstractmethod
    async def create_memory_association(self, 
                                      user_id: str,
                                      memory_id1: str,
                                      memory_id2: str,
                                      association_type: str,
                                      strength: float = 1.0) -> Dict[str, Any]:
        """
        创建记忆关联
        
        Args:
            user_id: 用户ID
            memory_id1: 记忆ID1
            memory_id2: 记忆ID2
            association_type: 关联类型
            strength: 关联强度
            
        Returns:
            创建结果
        """
        pass
    
    @abstractmethod
    async def get_memory_network(self, 
                               user_id: str,
                               memory_id: str = None,
                               depth: int = 2) -> Dict[str, Any]:
        """
        获取记忆网络
        
        Args:
            user_id: 用户ID
            memory_id: 中心记忆ID
            depth: 网络深度
            
        Returns:
            记忆网络
        """
        pass
    
    @abstractmethod
    async def optimize_reminder_schedule(self, 
                                       user_id: str,
                                       optimization_criteria: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        优化提醒调度
        
        Args:
            user_id: 用户ID
            optimization_criteria: 优化标准
            
        Returns:
            优化结果
        """
        pass
    
    @abstractmethod
    async def get_cognitive_trends(self, 
                                 user_id: str,
                                 time_range: Dict[str, str] = None,
                                 metrics: List[str] = None) -> Dict[str, Any]:
        """
        获取认知趋势
        
        Args:
            user_id: 用户ID
            time_range: 时间范围
            metrics: 指标列表
            
        Returns:
            趋势数据
        """
        pass
    
    @abstractmethod
    async def create_care_plan(self, 
                             user_id: str,
                             plan_type: str,
                             goals: List[Dict[str, Any]],
                             duration: int = 30) -> Dict[str, Any]:
        """
        创建护理计划
        
        Args:
            user_id: 用户ID
            plan_type: 计划类型
            goals: 目标列表
            duration: 持续时间（天）
            
        Returns:
            计划创建结果
        """
        pass
    
    @abstractmethod
    async def update_care_plan_progress(self, 
                                      user_id: str,
                                      plan_id: str,
                                      progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新护理计划进度
        
        Args:
            user_id: 用户ID
            plan_id: 计划ID
            progress_data: 进度数据
            
        Returns:
            更新结果
        """
        pass
    
    @abstractmethod
    async def get_emergency_contacts(self, 
                                   user_id: str) -> Dict[str, Any]:
        """
        获取紧急联系人
        
        Args:
            user_id: 用户ID
            
        Returns:
            紧急联系人列表
        """
        pass
    
    @abstractmethod
    async def trigger_emergency_alert(self, 
                                    user_id: str,
                                    alert_type: str,
                                    context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        触发紧急警报
        
        Args:
            user_id: 用户ID
            alert_type: 警报类型
            context: 上下文信息
            
        Returns:
            警报结果
        """
        pass
    
    @abstractmethod
    async def get_service_status(self) -> Dict[str, Any]:
        """
        获取服务状态
        
        Returns:
            服务状态信息
        """
        pass
    
    @abstractmethod
    async def cleanup(self):
        """
        清理服务资源
        """
        pass 