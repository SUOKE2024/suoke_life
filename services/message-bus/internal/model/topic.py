"""
topic - 索克生活项目模块
"""

        import re
from typing import Dict, Any, Optional, List
import time


class Topic:
    """
    主题模型类，表示消息主题
    """
    
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        creation_time: Optional[int] = None,
        partition_count: int = 3,
        retention_hours: int = 24
    ):
        """
        初始化主题对象
        
        Args:
            name: 主题名称
            description: 主题描述
            properties: 主题属性
            creation_time: 创建时间戳，如不提供则使用当前时间
            partition_count: 分区数量
            retention_hours: 消息保留时间(小时)
        """
        self.name = name
        self.description = description or ""
        self.properties = properties or {}
        self.creation_time = creation_time or int(time.time() * 1000)
        self.partition_count = partition_count
        self.retention_hours = retention_hours
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典表示
        
        Returns:
            Dict[str, Any]: 主题的字典表示
        """
        return {
            "name": self.name,
            "description": self.description,
            "properties": self.properties,
            "creation_time": self.creation_time,
            "partition_count": self.partition_count,
            "retention_hours": self.retention_hours
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Topic':
        """
        从字典创建主题对象
        
        Args:
            data: 包含主题数据的字典
            
        Returns:
            Topic: 主题对象
        """
        return cls(
            name=data["name"],
            description=data.get("description"),
            properties=data.get("properties", {}),
            creation_time=data.get("creation_time"),
            partition_count=data.get("partition_count", 3),
            retention_hours=data.get("retention_hours", 24)
        )
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Topic(name={self.name}, partitions={self.partition_count}, retention={self.retention_hours}h)"
    
    @staticmethod
    def validate_topic_name(topic_name: str) -> bool:
        """
        验证主题名称是否有效
        
        Args:
            topic_name: 主题名称
            
        Returns:
            bool: 是否有效
        """
        # 主题名称必须是非空字符串
        if not topic_name or not isinstance(topic_name, str):
            return False
            
        # 主题名称长度在2-64之间
        if len(topic_name) < 2 or len(topic_name) > 64:
            return False
            
        # 主题名称只能包含字母、数字、连字符和点
        if not re.match(r'^[a-zA-Z0-9\-\.]+$', topic_name):
            return False
            
        return True 