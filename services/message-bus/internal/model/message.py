import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

class Message:
    """
    消息模型类，表示消息总线中传递的消息
    """
    
    def __init__(
        self,
        topic: str,
        payload: Union[bytes, str, Dict[str, Any]],
        attributes: Optional[Dict[str, str]] = None,
        message_id: Optional[str] = None,
        publish_time: Optional[int] = None,
        publisher_id: Optional[str] = None
    ):
        """
        初始化消息对象
        
        Args:
            topic: 消息所属主题
            payload: 消息内容，可以是字节、字符串或字典
            attributes: 消息属性，用于消息过滤和路由
            message_id: 消息ID，如不提供则自动生成
            publish_time: 发布时间戳，如不提供则使用当前时间
            publisher_id: 发布者ID
        """
        self.topic = topic
        self.message_id = message_id or str(uuid.uuid4())
        self.publish_time = publish_time or int(time.time() * 1000)
        self.publisher_id = publisher_id
        self.attributes = attributes or {}
        
        # 处理不同类型的payload
        if isinstance(payload, bytes):
            self.payload = payload
        elif isinstance(payload, str):
            self.payload = payload.encode('utf-8')
        elif isinstance(payload, (dict, list)):
            self.payload = json.dumps(payload).encode('utf-8')
        else:
            raise TypeError(f"不支持的payload类型: {type(payload)}")
    
    @property
    def payload_as_string(self) -> str:
        """
        将载荷解析为字符串
        
        Returns:
            str: 字符串格式的载荷
        """
        return self.payload.decode('utf-8')
    
    @property
    def payload_as_json(self) -> Union[Dict[str, Any], List[Any]]:
        """
        将载荷解析为JSON对象
        
        Returns:
            Dict[str, Any] | List[Any]: JSON格式的载荷
        
        Raises:
            ValueError: 如果载荷不是有效的JSON
        """
        return json.loads(self.payload_as_string)
    
    @property
    def formatted_publish_time(self) -> str:
        """
        格式化的发布时间
        
        Returns:
            str: 格式化的时间字符串
        """
        dt = datetime.fromtimestamp(self.publish_time / 1000)
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典表示
        
        Returns:
            Dict[str, Any]: 消息的字典表示
        """
        return {
            "id": self.message_id,
            "topic": self.topic,
            "payload": self.payload,
            "attributes": self.attributes,
            "publish_time": self.publish_time,
            "publisher_id": self.publisher_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """
        从字典创建消息对象
        
        Args:
            data: 包含消息数据的字典
            
        Returns:
            Message: 消息对象
        """
        return cls(
            topic=data["topic"],
            payload=data["payload"],
            attributes=data.get("attributes", {}),
            message_id=data.get("id"),
            publish_time=data.get("publish_time"),
            publisher_id=data.get("publisher_id")
        )
    
    def __str__(self) -> str:
        """字符串表示"""
        return (
            f"Message(id={self.message_id}, "
            f"topic={self.topic}, "
            f"time={self.formatted_publish_time}, "
            f"attributes={self.attributes})"
        ) 