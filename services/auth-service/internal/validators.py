"""
输入验证和数据清理模块

提供统一的数据验证、清理和安全检查功能。
"""
import re
import html
import logging
from typing import Optional, Dict, Any, List
from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, Field, validator
from .config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ValidationResult:
    """验证结果类"""
    
    def __init__(self, is_valid: bool, message: str = "", cleaned_data: Any = None):
        self.is_valid = is_valid
        self.message = message
        self.cleaned_data = cleaned_data


class InputValidator:
    """输入验证器"""
    
    # 常用正则表达式
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,30}$')
    PHONE_PATTERN = re.compile(r'^\+?[1-9]\d{1,14}$')  # E.164格式
    PASSWORD_SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # 危险字符和SQL注入模式
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # XSS
        r'javascript:',  # JavaScript协议
        r'on\w+\s*=',  # 事件处理器
        r'(union|select|insert|update|delete|drop|create|alter)\s+',  # SQL关键字
        r'(\-\-|\#|\/\*|\*\/)',  # SQL注释
    ]
    
    @classmethod
    def validate_username(cls, username: str) -> ValidationResult:
        """验证用户名"""
        if not username:
            return ValidationResult(False, "用户名不能为空")
        
        # 清理输入
        cleaned_username = cls._clean_string(username)
        
        # 长度检查
        if len(cleaned_username) < 3:
            return ValidationResult(False, "用户名长度不能少于3个字符")
        if len(cleaned_username) > 30:
            return ValidationResult(False, "用户名长度不能超过30个字符")
        
        # 格式检查
        if not cls.USERNAME_PATTERN.match(cleaned_username):
            return ValidationResult(False, "用户名只能包含字母、数字、下划线和连字符")
        
        # 安全检查
        if cls._contains_dangerous_patterns(cleaned_username):
            return ValidationResult(False, "用户名包含不安全字符")
        
        return ValidationResult(True, "用户名验证通过", cleaned_username)
    
    @classmethod
    def validate_email(cls, email: str) -> ValidationResult:
        """验证邮箱地址"""
        if not email:
            return ValidationResult(False, "邮箱地址不能为空")
        
        # 清理输入
        cleaned_email = cls._clean_string(email).lower()
        
        try:
            # 使用email-validator库验证
            valid_email = validate_email(cleaned_email)
            normalized_email = valid_email.email
            
            # 安全检查
            if cls._contains_dangerous_patterns(normalized_email):
                return ValidationResult(False, "邮箱地址包含不安全字符")
            
            return ValidationResult(True, "邮箱验证通过", normalized_email)
            
        except EmailNotValidError as e:
            return ValidationResult(False, f"邮箱格式无效: {str(e)}")
    
    @classmethod
    def validate_password(cls, password: str) -> ValidationResult:
        """验证密码强度"""
        if not password:
            return ValidationResult(False, "密码不能为空")
        
        errors = []
        
        # 长度检查
        if len(password) < settings.password_min_length:
            errors.append(f"密码长度不能少于{settings.password_min_length}个字符")
        
        if len(password) > 128:  # 防止过长密码
            errors.append("密码长度不能超过128个字符")
        
        # 复杂度检查
        if settings.password_require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("密码必须包含至少一个大写字母")
        
        if settings.password_require_lowercase and not re.search(r'[a-z]', password):
            errors.append("密码必须包含至少一个小写字母")
        
        if settings.password_require_numbers and not re.search(r'\d', password):
            errors.append("密码必须包含至少一个数字")
        
        if settings.password_require_special and not any(c in cls.PASSWORD_SPECIAL_CHARS for c in password):
            errors.append(f"密码必须包含至少一个特殊字符: {cls.PASSWORD_SPECIAL_CHARS}")
        
        # 常见弱密码检查
        weak_passwords = [
            "password", "123456", "qwerty", "admin", "root", "user",
            "password123", "123456789", "12345678", "1234567890"
        ]
        if password.lower() in weak_passwords:
            errors.append("密码过于简单，请使用更复杂的密码")
        
        if errors:
            return ValidationResult(False, "; ".join(errors))
        
        return ValidationResult(True, "密码强度验证通过", password)
    
    @classmethod
    def validate_phone(cls, phone: str) -> ValidationResult:
        """验证手机号码"""
        if not phone:
            return ValidationResult(False, "手机号码不能为空")
        
        # 清理输入（移除空格和特殊字符）
        cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # 格式检查
        if not cls.PHONE_PATTERN.match(cleaned_phone):
            return ValidationResult(False, "手机号码格式无效")
        
        # 安全检查
        if cls._contains_dangerous_patterns(cleaned_phone):
            return ValidationResult(False, "手机号码包含不安全字符")
        
        return ValidationResult(True, "手机号码验证通过", cleaned_phone)
    
    @classmethod
    def validate_mfa_code(cls, code: str) -> ValidationResult:
        """验证MFA验证码"""
        if not code:
            return ValidationResult(False, "验证码不能为空")
        
        # 清理输入
        cleaned_code = re.sub(r'\s', '', code)
        
        # 长度和格式检查
        if not re.match(r'^\d{6,8}$', cleaned_code):
            return ValidationResult(False, "验证码必须是6-8位数字")
        
        return ValidationResult(True, "验证码格式验证通过", cleaned_code)
    
    @classmethod
    def validate_json_data(cls, data: Dict[str, Any], max_depth: int = 5) -> ValidationResult:
        """验证JSON数据安全性"""
        try:
            # 检查嵌套深度
            if cls._get_dict_depth(data) > max_depth:
                return ValidationResult(False, f"JSON数据嵌套层级不能超过{max_depth}层")
            
            # 检查数据大小
            import json
            json_str = json.dumps(data)
            if len(json_str) > 1024 * 1024:  # 1MB限制
                return ValidationResult(False, "JSON数据大小不能超过1MB")
            
            # 递归检查所有字符串值
            cleaned_data = cls._clean_json_data(data)
            
            return ValidationResult(True, "JSON数据验证通过", cleaned_data)
            
        except Exception as e:
            return ValidationResult(False, f"JSON数据验证失败: {str(e)}")
    
    @classmethod
    def _clean_string(cls, text: str) -> str:
        """清理字符串输入"""
        if not text:
            return ""
        
        # 移除前后空白
        cleaned = text.strip()
        
        # HTML转义
        cleaned = html.escape(cleaned)
        
        # 移除控制字符
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned)
        
        return cleaned
    
    @classmethod
    def _contains_dangerous_patterns(cls, text: str) -> bool:
        """检查是否包含危险模式"""
        text_lower = text.lower()
        
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"检测到危险模式: {pattern} in {text[:50]}...")
                return True
        
        return False
    
    @classmethod
    def _get_dict_depth(cls, d: Dict[str, Any], depth: int = 0) -> int:
        """获取字典嵌套深度"""
        if not isinstance(d, dict):
            return depth
        
        max_depth = depth
        for value in d.values():
            if isinstance(value, dict):
                max_depth = max(max_depth, cls._get_dict_depth(value, depth + 1))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        max_depth = max(max_depth, cls._get_dict_depth(item, depth + 1))
        
        return max_depth
    
    @classmethod
    def _clean_json_data(cls, data: Any) -> Any:
        """递归清理JSON数据"""
        if isinstance(data, str):
            return cls._clean_string(data)
        elif isinstance(data, dict):
            return {key: cls._clean_json_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [cls._clean_json_data(item) for item in data]
        else:
            return data


class UserRegistrationValidator(BaseModel):
    """用户注册数据验证器"""
    
    username: str = Field(..., min_length=3, max_length=30)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    phone_number: Optional[str] = Field(None, max_length=20)
    profile_data: Optional[Dict[str, Any]] = Field(None)
    
    @validator('username')
    def validate_username(cls, v):
        result = InputValidator.validate_username(v)
        if not result.is_valid:
            raise ValueError(result.message)
        return result.cleaned_data
    
    @validator('email')
    def validate_email(cls, v):
        result = InputValidator.validate_email(v)
        if not result.is_valid:
            raise ValueError(result.message)
        return result.cleaned_data
    
    @validator('password')
    def validate_password(cls, v):
        result = InputValidator.validate_password(v)
        if not result.is_valid:
            raise ValueError(result.message)
        return result.cleaned_data
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is None:
            return v
        result = InputValidator.validate_phone(v)
        if not result.is_valid:
            raise ValueError(result.message)
        return result.cleaned_data
    
    @validator('profile_data')
    def validate_profile_data(cls, v):
        if v is None:
            return v
        result = InputValidator.validate_json_data(v)
        if not result.is_valid:
            raise ValueError(result.message)
        return result.cleaned_data


class UserUpdateValidator(BaseModel):
    """用户更新数据验证器"""
    
    username: Optional[str] = Field(None, min_length=3, max_length=30)
    email: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)
    profile_data: Optional[Dict[str, Any]] = Field(None)
    
    @validator('username')
    def validate_username(cls, v):
        if v is None:
            return v
        result = InputValidator.validate_username(v)
        if not result.is_valid:
            raise ValueError(result.message)
        return result.cleaned_data
    
    @validator('email')
    def validate_email(cls, v):
        if v is None:
            return v
        result = InputValidator.validate_email(v)
        if not result.is_valid:
            raise ValueError(result.message)
        return result.cleaned_data
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is None:
            return v
        result = InputValidator.validate_phone(v)
        if not result.is_valid:
            raise ValueError(result.message)
        return result.cleaned_data
    
    @validator('profile_data')
    def validate_profile_data(cls, v):
        if v is None:
            return v
        result = InputValidator.validate_json_data(v)
        if not result.is_valid:
            raise ValueError(result.message)
        return result.cleaned_data


class LoginValidator(BaseModel):
    """登录数据验证器"""
    
    username: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)
    
    @validator('username')
    def validate_username(cls, v):
        # 登录时用户名可以是邮箱或用户名
        cleaned = InputValidator._clean_string(v)
        if InputValidator._contains_dangerous_patterns(cleaned):
            raise ValueError("用户名包含不安全字符")
        return cleaned
    
    @validator('password')
    def validate_password(cls, v):
        # 登录时不验证密码强度，只检查安全性
        if InputValidator._contains_dangerous_patterns(v):
            raise ValueError("密码包含不安全字符")
        return v


def sanitize_log_data(data: Any, max_length: int = 100) -> str:
    """清理日志数据，防止日志注入"""
    if data is None:
        return "None"
    
    # 转换为字符串
    text = str(data)
    
    # 移除换行符和控制字符
    text = re.sub(r'[\r\n\t\x00-\x1f\x7f-\x9f]', ' ', text)
    
    # 限制长度
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text 