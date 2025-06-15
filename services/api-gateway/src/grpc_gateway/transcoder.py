"""
gRPC转码器模块

提供JSON和Protobuf之间的转换功能
"""

import json
from typing import Dict, Any, Optional, Type, Union
from google.protobuf import message
from google.protobuf.json_format import MessageToJson, Parse
from google.protobuf.descriptor import Descriptor
import structlog

logger = structlog.get_logger(__name__)


class GrpcTranscoder:
    """gRPC转码器"""
    
    def __init__(self):
        self._message_types: Dict[str, Type[message.Message]] = {}
        
    def register_message_type(
        self,
        type_name: str,
        message_class: Type[message.Message]
    ) -> None:
        """注册消息类型"""
        self._message_types[type_name] = message_class
        logger.info(
            "gRPC消息类型已注册",
            type_name=type_name,
            class_name=message_class.__name__
        )
    
    def json_to_protobuf(
        self,
        json_data: Union[str, Dict[str, Any]],
        message_type: str
    ) -> message.Message:
        """将JSON转换为Protobuf消息"""
        try:
            # 获取消息类型
            if message_type not in self._message_types:
                raise ValueError(f"未注册的消息类型: {message_type}")
            
            message_class = self._message_types[message_type]
            
            # 创建消息实例
            proto_message = message_class()
            
            # 转换JSON数据
            if isinstance(json_data, str):
                Parse(json_data, proto_message)
            else:
                json_str = json.dumps(json_data)
                Parse(json_str, proto_message)
            
            logger.debug(
                "JSON转Protobuf成功",
                message_type=message_type,
                json_size=len(str(json_data))
            )
            
            return proto_message
            
        except Exception as e:
            logger.error(
                "JSON转Protobuf失败",
                message_type=message_type,
                error=str(e)
            )
            raise
    
    def protobuf_to_json(
        self,
        proto_message: message.Message,
        message_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """将Protobuf消息转换为JSON"""
        try:
            # 转换为JSON字符串
            json_str = MessageToJson(
                proto_message,
                preserving_proto_field_name=True,
                including_default_value_fields=True
            )
            
            # 解析为字典
            json_data = json.loads(json_str)
            
            logger.debug(
                "Protobuf转JSON成功",
                message_type=message_type or proto_message.__class__.__name__,
                json_size=len(json_str)
            )
            
            return json_data
            
        except Exception as e:
            logger.error(
                "Protobuf转JSON失败",
                message_type=message_type or proto_message.__class__.__name__,
                error=str(e)
            )
            raise
    
    def validate_json_schema(
        self,
        json_data: Dict[str, Any],
        message_type: str
    ) -> bool:
        """验证JSON数据是否符合Protobuf消息模式"""
        try:
            # 尝试转换为Protobuf消息
            proto_message = self.json_to_protobuf(json_data, message_type)
            
            # 检查必填字段
            descriptor = proto_message.DESCRIPTOR
            for field in descriptor.fields:
                if field.label == field.LABEL_REQUIRED:
                    if not proto_message.HasField(field.name):
                        logger.warning(
                            "缺少必填字段",
                            message_type=message_type,
                            field=field.name
                        )
                        return False
            
            return True
            
        except Exception as e:
            logger.error(
                "JSON模式验证失败",
                message_type=message_type,
                error=str(e)
            )
            return False
    
    def get_message_schema(self, message_type: str) -> Dict[str, Any]:
        """获取消息类型的JSON模式"""
        if message_type not in self._message_types:
            raise ValueError(f"未注册的消息类型: {message_type}")
        
        message_class = self._message_types[message_type]
        descriptor = message_class.DESCRIPTOR
        
        return self._descriptor_to_schema(descriptor)
    
    def _descriptor_to_schema(self, descriptor: Descriptor) -> Dict[str, Any]:
        """将Protobuf描述符转换为JSON模式"""
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for field in descriptor.fields:
            field_schema = self._field_to_schema(field)
            schema["properties"][field.name] = field_schema
            
            if field.label == field.LABEL_REQUIRED:
                schema["required"].append(field.name)
        
        return schema
    
    def _field_to_schema(self, field) -> Dict[str, Any]:
        """将Protobuf字段转换为JSON模式"""
        # 基本类型映射
        type_mapping = {
            field.TYPE_DOUBLE: {"type": "number"},
            field.TYPE_FLOAT: {"type": "number"},
            field.TYPE_INT64: {"type": "integer"},
            field.TYPE_UINT64: {"type": "integer"},
            field.TYPE_INT32: {"type": "integer"},
            field.TYPE_FIXED64: {"type": "integer"},
            field.TYPE_FIXED32: {"type": "integer"},
            field.TYPE_BOOL: {"type": "boolean"},
            field.TYPE_STRING: {"type": "string"},
            field.TYPE_BYTES: {"type": "string", "format": "byte"},
            field.TYPE_UINT32: {"type": "integer"},
            field.TYPE_SFIXED32: {"type": "integer"},
            field.TYPE_SFIXED64: {"type": "integer"},
            field.TYPE_SINT32: {"type": "integer"},
            field.TYPE_SINT64: {"type": "integer"},
        }
        
        if field.type in type_mapping:
            field_schema = type_mapping[field.type].copy()
        elif field.type == field.TYPE_MESSAGE:
            # 嵌套消息
            field_schema = self._descriptor_to_schema(field.message_type)
        elif field.type == field.TYPE_ENUM:
            # 枚举类型
            enum_values = [value.name for value in field.enum_type.values]
            field_schema = {
                "type": "string",
                "enum": enum_values
            }
        else:
            field_schema = {"type": "string"}
        
        # 处理重复字段
        if field.label == field.LABEL_REPEATED:
            field_schema = {
                "type": "array",
                "items": field_schema
            }
        
        return field_schema
    
    def get_registered_types(self) -> Dict[str, str]:
        """获取已注册的消息类型"""
        return {
            type_name: message_class.__name__
            for type_name, message_class in self._message_types.items()
        }
    
    def clear_types(self) -> None:
        """清空已注册的消息类型"""
        self._message_types.clear()
        logger.info("已清空所有注册的消息类型")


class ProtobufRegistry:
    """Protobuf消息注册表"""
    
    def __init__(self):
        self._registry: Dict[str, Type[message.Message]] = {}
    
    def register_from_module(self, module) -> None:
        """从模块注册所有消息类型"""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, message.Message) and 
                attr != message.Message):
                
                type_name = f"{module.__name__}.{attr_name}"
                self._registry[type_name] = attr
                
                logger.info(
                    "从模块注册消息类型",
                    module=module.__name__,
                    type_name=type_name,
                    class_name=attr_name
                )
    
    def register_message(
        self,
        type_name: str,
        message_class: Type[message.Message]
    ) -> None:
        """注册单个消息类型"""
        self._registry[type_name] = message_class
        logger.info(
            "注册消息类型",
            type_name=type_name,
            class_name=message_class.__name__
        )
    
    def get_message_class(self, type_name: str) -> Type[message.Message]:
        """获取消息类型"""
        if type_name not in self._registry:
            raise ValueError(f"未注册的消息类型: {type_name}")
        return self._registry[type_name]
    
    def list_types(self) -> Dict[str, str]:
        """列出所有注册的类型"""
        return {
            type_name: message_class.__name__
            for type_name, message_class in self._registry.items()
        }
    
    def create_transcoder(self) -> GrpcTranscoder:
        """创建转码器并注册所有类型"""
        transcoder = GrpcTranscoder()
        
        for type_name, message_class in self._registry.items():
            transcoder.register_message_type(type_name, message_class)
        
        return transcoder 