#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康档案管理器
负责用户健康档案的存储、更新和检索
"""
import logging
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ProfileManager:
    """健康档案管理器类"""
    
    def __init__(self, repository=None):
        """初始化健康档案管理器"""
        logger.info("初始化健康档案管理器")
        self.repository = repository
        
        # 临时存储，实际应用中应使用数据库
        self._profiles_dir = os.path.join("data", "profiles")
        if not os.path.exists(self._profiles_dir):
            os.makedirs(self._profiles_dir, exist_ok=True)
            logger.info(f"创建档案存储目录: {self._profiles_dir}")
        
        logger.info("健康档案管理器初始化完成")
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户健康档案
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict[str, Any]: 用户健康档案
        """
        logger.debug(f"获取用户档案: {user_id}")
        
        if self.repository:
            # 使用存储库获取档案
            return self.repository.get_profile(user_id)
        
        # 使用临时文件存储
        profile_path = os.path.join(self._profiles_dir, f"{user_id}.json")
        
        if os.path.exists(profile_path):
            try:
                with open(profile_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"读取用户档案失败: {str(e)}")
                # 返回空档案
                return self._create_default_profile(user_id)
        else:
            # 创建默认档案
            default_profile = self._create_default_profile(user_id)
            self.save_user_profile(user_id, default_profile)
            return default_profile
    
    def save_user_profile(self, user_id: str, profile: Dict[str, Any]) -> bool:
        """
        保存用户健康档案
        
        Args:
            user_id: 用户ID
            profile: 用户健康档案
            
        Returns:
            bool: 是否保存成功
        """
        logger.debug(f"保存用户档案: {user_id}")
        
        if self.repository:
            # 使用存储库保存档案
            return self.repository.save_profile(user_id, profile)
        
        # 使用临时文件存储
        profile_path = os.path.join(self._profiles_dir, f"{user_id}.json")
        
        try:
            # 更新最后修改时间
            profile["last_updated"] = datetime.now().isoformat()
            
            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(profile, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存用户档案失败: {str(e)}")
            return False
    
    def update_profile_field(self, user_id: str, field: str, value: Any) -> bool:
        """
        更新用户健康档案字段
        
        Args:
            user_id: 用户ID
            field: 字段名，支持点分隔的嵌套字段
            value: 字段值
            
        Returns:
            bool: 是否更新成功
        """
        logger.debug(f"更新用户档案字段: {user_id}.{field}")
        
        # 获取当前档案
        profile = self.get_user_profile(user_id)
        
        # 设置字段值
        if "." in field:
            # 处理嵌套字段
            parts = field.split(".")
            current = profile
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    # 最后一个部分是要设置值的字段
                    current[part] = value
                else:
                    # 确保中间路径存在
                    if part not in current or not isinstance(current[part], dict):
                        current[part] = {}
                    current = current[part]
        else:
            # 简单字段
            profile[field] = value
        
        # 保存更新后的档案
        return self.save_user_profile(user_id, profile)
    
    def get_health_data(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户健康数据
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict[str, Any]: 用户健康数据
        """
        logger.debug(f"获取用户健康数据: {user_id}")
        
        profile = self.get_user_profile(user_id)
        return profile.get("health_data", {})
    
    def save_health_record(self, user_id: str, record_type: str, 
                          record_data: Dict[str, Any]) -> str:
        """
        保存健康记录
        
        Args:
            user_id: 用户ID
            record_type: 记录类型
            record_data: 记录数据
            
        Returns:
            str: 记录ID
        """
        logger.debug(f"保存健康记录: {user_id}, 类型: {record_type}")
        
        # 获取当前档案
        profile = self.get_user_profile(user_id)
        
        # 确保健康记录部分存在
        if "health_records" not in profile:
            profile["health_records"] = {}
        
        if record_type not in profile["health_records"]:
            profile["health_records"][record_type] = []
        
        # 创建新记录
        record_id = str(uuid.uuid4())
        record = {
            "id": record_id,
            "type": record_type,
            "created_at": datetime.now().isoformat(),
            "data": record_data
        }
        
        # 添加记录
        profile["health_records"][record_type].append(record)
        
        # 保存更新后的档案
        if self.save_user_profile(user_id, profile):
            return record_id
        else:
            return ""
    
    def get_constitution_type(self, user_id: str) -> str:
        """
        获取用户体质类型
        
        Args:
            user_id: 用户ID
            
        Returns:
            str: 体质类型
        """
        profile = self.get_user_profile(user_id)
        return profile.get("constitution_type", "未知")
    
    def get_health_goals(self, user_id: str) -> List[str]:
        """
        获取用户健康目标
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[str]: 健康目标列表
        """
        profile = self.get_user_profile(user_id)
        return profile.get("health_goals", [])
    
    def _create_default_profile(self, user_id: str) -> Dict[str, Any]:
        """
        创建默认用户健康档案
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict[str, Any]: 默认档案
        """
        return {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "constitution_type": "未知",
            "health_goals": ["改善睡眠", "增强体质"],
            "health_data": {
                "height": 170,
                "weight": 65,
                "blood_pressure": "120/80",
                "heart_rate": 75,
                "sleep_duration": 7.0,
                "activity_level": "中等"
            },
            "allergies": [],
            "medical_conditions": [],
            "medications": [],
            "preferences": {
                "diet_restrictions": [],
                "exercise_preferences": ["步行", "游泳"],
                "lifestyle_preferences": ["早睡早起"]
            },
            "health_records": {},
            "active_plans": []
        } 