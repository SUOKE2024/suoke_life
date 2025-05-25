#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据验证和序列化服务

提供数据验证、序列化、反序列化等功能。
"""

import json
import re
import base64
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union, Type, get_type_hints
from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime, date
from enum import Enum

from structlog import get_logger

logger = get_logger()


class ValidationError(Exception):
    """验证错误"""
    def __init__(self, message: str, field: str = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(message)


class SerializationError(Exception):
    """序列化错误"""
    pass


@dataclass
class ValidationRule:
    """验证规则"""
    field_name: str
    required: bool = True
    data_type: Type = str
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    choices: Optional[List[Any]] = None
    custom_validator: Optional[callable] = None
    error_message: Optional[str] = None


class Validator(ABC):
    """验证器抽象基类"""
    
    @abstractmethod
    def validate(self, value: Any) -> bool:
        """验证值"""
        pass
    
    @abstractmethod
    def get_error_message(self) -> str:
        """获取错误消息"""
        pass


class RequiredValidator(Validator):
    """必填验证器"""
    
    def validate(self, value: Any) -> bool:
        return value is not None and value != ""
    
    def get_error_message(self) -> str:
        return "字段不能为空"


class TypeValidator(Validator):
    """类型验证器"""
    
    def __init__(self, expected_type: Type):
        self.expected_type = expected_type
    
    def validate(self, value: Any) -> bool:
        if value is None:
            return True
        return isinstance(value, self.expected_type)
    
    def get_error_message(self) -> str:
        return f"字段类型必须是 {self.expected_type.__name__}"


class LengthValidator(Validator):
    """长度验证器"""
    
    def __init__(self, min_length: int = None, max_length: int = None):
        self.min_length = min_length
        self.max_length = max_length
    
    def validate(self, value: Any) -> bool:
        if value is None:
            return True
        
        if not hasattr(value, '__len__'):
            return False
        
        length = len(value)
        
        if self.min_length is not None and length < self.min_length:
            return False
        
        if self.max_length is not None and length > self.max_length:
            return False
        
        return True
    
    def get_error_message(self) -> str:
        if self.min_length and self.max_length:
            return f"长度必须在 {self.min_length} 到 {self.max_length} 之间"
        elif self.min_length:
            return f"长度不能少于 {self.min_length}"
        elif self.max_length:
            return f"长度不能超过 {self.max_length}"
        return "长度无效"


class RangeValidator(Validator):
    """范围验证器"""
    
    def __init__(self, min_value: Union[int, float] = None, max_value: Union[int, float] = None):
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, value: Any) -> bool:
        if value is None:
            return True
        
        if not isinstance(value, (int, float)):
            return False
        
        if self.min_value is not None and value < self.min_value:
            return False
        
        if self.max_value is not None and value > self.max_value:
            return False
        
        return True
    
    def get_error_message(self) -> str:
        if self.min_value is not None and self.max_value is not None:
            return f"值必须在 {self.min_value} 到 {self.max_value} 之间"
        elif self.min_value is not None:
            return f"值不能小于 {self.min_value}"
        elif self.max_value is not None:
            return f"值不能大于 {self.max_value}"
        return "值超出范围"


class PatternValidator(Validator):
    """正则表达式验证器"""
    
    def __init__(self, pattern: str):
        self.pattern = pattern
        self.regex = re.compile(pattern)
    
    def validate(self, value: Any) -> bool:
        if value is None:
            return True
        
        if not isinstance(value, str):
            return False
        
        return bool(self.regex.match(value))
    
    def get_error_message(self) -> str:
        return f"格式不匹配，必须符合模式: {self.pattern}"


class ChoicesValidator(Validator):
    """选择验证器"""
    
    def __init__(self, choices: List[Any]):
        self.choices = choices
    
    def validate(self, value: Any) -> bool:
        if value is None:
            return True
        return value in self.choices
    
    def get_error_message(self) -> str:
        return f"值必须是以下选项之一: {self.choices}"


class EmailValidator(PatternValidator):
    """邮箱验证器"""
    
    def __init__(self):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        super().__init__(email_pattern)
    
    def get_error_message(self) -> str:
        return "邮箱格式无效"


class ImageDataValidator(Validator):
    """图像数据验证器"""
    
    def __init__(self, max_size: int = 10 * 1024 * 1024, allowed_formats: List[str] = None):
        self.max_size = max_size
        self.allowed_formats = allowed_formats or ['JPEG', 'PNG', 'GIF', 'BMP']
    
    def validate(self, value: Any) -> bool:
        if value is None:
            return True
        
        if not isinstance(value, bytes):
            return False
        
        # 检查大小
        if len(value) > self.max_size:
            return False
        
        # 简单的格式检查（基于文件头）
        if value.startswith(b'\xff\xd8\xff'):  # JPEG
            return 'JPEG' in self.allowed_formats
        elif value.startswith(b'\x89PNG\r\n\x1a\n'):  # PNG
            return 'PNG' in self.allowed_formats
        elif value.startswith(b'GIF87a') or value.startswith(b'GIF89a'):  # GIF
            return 'GIF' in self.allowed_formats
        elif value.startswith(b'BM'):  # BMP
            return 'BMP' in self.allowed_formats
        
        return False
    
    def get_error_message(self) -> str:
        return f"图像数据无效，最大大小: {self.max_size} 字节，支持格式: {self.allowed_formats}"


class ValidationService:
    """验证服务"""
    
    def __init__(self):
        self.rules: Dict[str, List[ValidationRule]] = {}
        self.validators: Dict[str, List[Validator]] = {}
    
    def add_rule(self, schema_name: str, rule: ValidationRule):
        """添加验证规则"""
        if schema_name not in self.rules:
            self.rules[schema_name] = []
        self.rules[schema_name].append(rule)
        
        # 构建验证器
        self._build_validators_for_rule(schema_name, rule)
    
    def _build_validators_for_rule(self, schema_name: str, rule: ValidationRule):
        """为规则构建验证器"""
        if schema_name not in self.validators:
            self.validators[schema_name] = {}
        
        if rule.field_name not in self.validators[schema_name]:
            self.validators[schema_name][rule.field_name] = []
        
        field_validators = self.validators[schema_name][rule.field_name]
        
        # 必填验证器
        if rule.required:
            field_validators.append(RequiredValidator())
        
        # 类型验证器
        if rule.data_type:
            field_validators.append(TypeValidator(rule.data_type))
        
        # 长度验证器
        if rule.min_length is not None or rule.max_length is not None:
            field_validators.append(LengthValidator(rule.min_length, rule.max_length))
        
        # 范围验证器
        if rule.min_value is not None or rule.max_value is not None:
            field_validators.append(RangeValidator(rule.min_value, rule.max_value))
        
        # 正则表达式验证器
        if rule.pattern:
            field_validators.append(PatternValidator(rule.pattern))
        
        # 选择验证器
        if rule.choices:
            field_validators.append(ChoicesValidator(rule.choices))
        
        # 自定义验证器
        if rule.custom_validator:
            field_validators.append(rule.custom_validator)
    
    def validate(self, schema_name: str, data: Dict[str, Any]) -> List[ValidationError]:
        """验证数据"""
        errors = []
        
        if schema_name not in self.validators:
            return errors
        
        schema_validators = self.validators[schema_name]
        
        for field_name, field_validators in schema_validators.items():
            value = data.get(field_name)
            
            for validator in field_validators:
                try:
                    if not validator.validate(value):
                        error = ValidationError(
                            message=validator.get_error_message(),
                            field=field_name,
                            value=value
                        )
                        errors.append(error)
                        break  # 一个字段遇到第一个错误就停止
                except Exception as e:
                    error = ValidationError(
                        message=f"验证过程中发生错误: {str(e)}",
                        field=field_name,
                        value=value
                    )
                    errors.append(error)
                    break
        
        return errors
    
    def validate_and_raise(self, schema_name: str, data: Dict[str, Any]):
        """验证数据，如果有错误则抛出异常"""
        errors = self.validate(schema_name, data)
        if errors:
            error_messages = [f"{error.field}: {error.message}" for error in errors]
            raise ValidationError(f"数据验证失败: {'; '.join(error_messages)}")


class SerializationService:
    """序列化服务"""
    
    def __init__(self):
        self.custom_serializers: Dict[Type, callable] = {}
        self.custom_deserializers: Dict[Type, callable] = {}
        
        # 注册默认序列化器
        self._register_default_serializers()
    
    def _register_default_serializers(self):
        """注册默认序列化器"""
        # 日期时间序列化器
        self.custom_serializers[datetime] = lambda dt: dt.isoformat()
        self.custom_serializers[date] = lambda d: d.isoformat()
        
        # 枚举序列化器
        self.custom_serializers[Enum] = lambda e: e.value
        
        # 字节序列化器
        self.custom_serializers[bytes] = lambda b: base64.b64encode(b).decode('utf-8')
        
        # 反序列化器
        self.custom_deserializers[datetime] = datetime.fromisoformat
        self.custom_deserializers[date] = date.fromisoformat
        self.custom_deserializers[bytes] = lambda s: base64.b64decode(s.encode('utf-8'))
    
    def register_serializer(self, data_type: Type, serializer: callable):
        """注册自定义序列化器"""
        self.custom_serializers[data_type] = serializer
    
    def register_deserializer(self, data_type: Type, deserializer: callable):
        """注册自定义反序列化器"""
        self.custom_deserializers[data_type] = deserializer
    
    def serialize(self, obj: Any) -> Any:
        """序列化对象"""
        try:
            return self._serialize_recursive(obj)
        except Exception as e:
            raise SerializationError(f"序列化失败: {str(e)}")
    
    def _serialize_recursive(self, obj: Any) -> Any:
        """递归序列化"""
        if obj is None:
            return None
        
        obj_type = type(obj)
        
        # 检查自定义序列化器
        for registered_type, serializer in self.custom_serializers.items():
            if (registered_type == obj_type or 
                (isinstance(registered_type, type) and isinstance(obj, registered_type))):
                return serializer(obj)
        
        # 基本类型
        if isinstance(obj, (str, int, float, bool)):
            return obj
        
        # 列表和元组
        if isinstance(obj, (list, tuple)):
            return [self._serialize_recursive(item) for item in obj]
        
        # 字典
        if isinstance(obj, dict):
            return {key: self._serialize_recursive(value) for key, value in obj.items()}
        
        # 数据类
        if is_dataclass(obj):
            return {
                field.name: self._serialize_recursive(getattr(obj, field.name))
                for field in fields(obj)
            }
        
        # 对象属性
        if hasattr(obj, '__dict__'):
            return {
                key: self._serialize_recursive(value)
                for key, value in obj.__dict__.items()
                if not key.startswith('_')
            }
        
        # 默认转换为字符串
        return str(obj)
    
    def deserialize(self, data: Any, target_type: Type = None) -> Any:
        """反序列化数据"""
        try:
            return self._deserialize_recursive(data, target_type)
        except Exception as e:
            raise SerializationError(f"反序列化失败: {str(e)}")
    
    def _deserialize_recursive(self, data: Any, target_type: Type = None) -> Any:
        """递归反序列化"""
        if data is None:
            return None
        
        # 如果没有指定目标类型，直接返回数据
        if target_type is None:
            return data
        
        # 检查自定义反序列化器
        if target_type in self.custom_deserializers:
            return self.custom_deserializers[target_type](data)
        
        # 基本类型
        if target_type in (str, int, float, bool):
            return target_type(data)
        
        # 列表
        if target_type == list or (hasattr(target_type, '__origin__') and target_type.__origin__ == list):
            if not isinstance(data, list):
                raise ValueError(f"期望列表类型，得到 {type(data)}")
            
            # 获取元素类型
            if hasattr(target_type, '__args__') and target_type.__args__:
                element_type = target_type.__args__[0]
                return [self._deserialize_recursive(item, element_type) for item in data]
            else:
                return data
        
        # 字典
        if target_type == dict or (hasattr(target_type, '__origin__') and target_type.__origin__ == dict):
            if not isinstance(data, dict):
                raise ValueError(f"期望字典类型，得到 {type(data)}")
            
            # 获取键值类型
            if hasattr(target_type, '__args__') and len(target_type.__args__) >= 2:
                key_type, value_type = target_type.__args__[:2]
                return {
                    self._deserialize_recursive(k, key_type): self._deserialize_recursive(v, value_type)
                    for k, v in data.items()
                }
            else:
                return data
        
        # 数据类
        if is_dataclass(target_type):
            if not isinstance(data, dict):
                raise ValueError(f"期望字典类型用于数据类，得到 {type(data)}")
            
            field_types = get_type_hints(target_type)
            kwargs = {}
            
            for field in fields(target_type):
                field_name = field.name
                if field_name in data:
                    field_type = field_types.get(field_name, field.type)
                    kwargs[field_name] = self._deserialize_recursive(data[field_name], field_type)
            
            return target_type(**kwargs)
        
        # 默认返回原始数据
        return data
    
    def to_json(self, obj: Any, indent: int = None) -> str:
        """序列化为JSON字符串"""
        serialized = self.serialize(obj)
        return json.dumps(serialized, ensure_ascii=False, indent=indent)
    
    def from_json(self, json_str: str, target_type: Type = None) -> Any:
        """从JSON字符串反序列化"""
        data = json.loads(json_str)
        return self.deserialize(data, target_type)


# 预定义的验证规则
def create_user_analysis_validation_rules() -> List[ValidationRule]:
    """创建用户分析请求验证规则"""
    return [
        ValidationRule(
            field_name="user_id",
            required=True,
            data_type=str,
            min_length=1,
            max_length=100,
            pattern=r'^[a-zA-Z0-9_-]+$',
            error_message="用户ID格式无效"
        ),
        ValidationRule(
            field_name="image",
            required=True,
            data_type=bytes,
            custom_validator=ImageDataValidator(),
            error_message="图像数据无效"
        ),
        ValidationRule(
            field_name="analysis_type",
            required=True,
            data_type=str,
            choices=["face", "body", "tongue"],
            error_message="分析类型无效"
        ),
        ValidationRule(
            field_name="save_result",
            required=False,
            data_type=bool,
            error_message="保存结果标志必须是布尔值"
        )
    ]


# 全局实例
validation_service = ValidationService()
serialization_service = SerializationService()

# 注册预定义规则
for rule in create_user_analysis_validation_rules():
    validation_service.add_rule("user_analysis_request", rule) 