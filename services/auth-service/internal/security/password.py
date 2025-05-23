#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
密码安全工具

提供密码哈希、验证和策略验证功能
"""
import re
import secrets
import string
from typing import Dict, Optional, Tuple

from passlib.hash import argon2
from passlib.context import CryptContext

from internal.model.errors import PasswordPolicyError

# 创建密码上下文
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    使用Argon2id算法对密码进行哈希处理
    
    Args:
        password: 明文密码
        
    Returns:
        哈希后的密码
        
    Raises:
        ValueError: 如果密码为空
    """
    if not password:
        raise ValueError("密码不能为空")
    
    return pwd_context.hash(password)


# 为了兼容性提供的别名函数
def get_password_hash(password: str) -> str:
    """
    hash_password函数的别名，用于兼容性

    Args:
        password: 明文密码
        
    Returns:
        哈希后的密码
    """
    return hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码是否与哈希密码匹配
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
        
    Returns:
        密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_policy(password: str, policy: Dict) -> Tuple[bool, Optional[str]]:
    """
    验证密码是否符合安全策略
    
    Args:
        password: 要验证的密码
        policy: 密码策略配置
            - min_length: 最小长度
            - require_uppercase: 是否需要大写字母
            - require_lowercase: 是否需要小写字母
            - require_numbers: 是否需要数字
            - require_special: 是否需要特殊字符
            
    Returns:
        (是否有效, 无效原因)
    """
    # 如果未指定策略，默认所有密码有效
    if not policy:
        return True, None
    
    # 检查长度
    min_length = policy.get("min_length", 0)
    if len(password) < min_length:
        return False, f"密码长度必须至少为{min_length}个字符"
    
    # 检查大写字母
    if policy.get("require_uppercase") and not any(c.isupper() for c in password):
        return False, "密码必须包含至少一个大写字母"
    
    # 检查小写字母
    if policy.get("require_lowercase") and not any(c.islower() for c in password):
        return False, "密码必须包含至少一个小写字母"
    
    # 检查数字
    if policy.get("require_numbers") and not any(c.isdigit() for c in password):
        return False, "密码必须包含至少一个数字"
    
    # 检查特殊字符
    if policy.get("require_special") and not re.search(r'[^A-Za-z0-9]', password):
        return False, "密码必须包含至少一个特殊字符"
    
    # 所有检查通过
    return True, None


def enforce_password_policy(password: str, policy: Optional[Dict] = None) -> None:
    """
    强制执行密码策略检查，不符合则抛出异常
    
    Args:
        password: 要检查的密码
        policy: 密码策略配置
        
    Raises:
        PasswordPolicyError: 如果密码不符合策略
    """
    if policy is None:
        return
    
    valid, message = validate_password_policy(password, policy)
    if not valid:
        raise PasswordPolicyError(f"密码策略验证失败: {message}")


def generate_secure_password(length: int = 16) -> str:
    """
    生成符合安全要求的随机密码
    
    Args:
        length: 密码长度，默认16位
        
    Returns:
        随机生成的安全密码
    """
    # 确保密码长度至少为8位
    if length < 8:
        length = 8
    
    # 定义字符集
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*()-_=+[]{}|;:,.<>?"
    
    # 确保密码包含各种字符类型
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special)
    ]
    
    # 添加剩余随机字符
    all_chars = lowercase + uppercase + digits + special
    password.extend(secrets.choice(all_chars) for _ in range(length - 4))
    
    # 打乱密码顺序
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)


# 添加PasswordHasher类以匹配测试期望
class PasswordHasher:
    """
    密码哈希处理类
    为了向后兼容提供的类包装器，实际使用模块级函数
    """
    
    def hash_password(self, password: str) -> str:
        """
        使用Argon2id算法对密码进行哈希处理
        
        Args:
            password: 明文密码
            
        Returns:
            哈希后的密码
        """
        return hash_password(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        验证明文密码是否与哈希密码匹配
        
        Args:
            plain_password: 明文密码
            hashed_password: 哈希后的密码
            
        Returns:
            如果密码匹配则返回True，否则返回False
        """
        return verify_password(plain_password, hashed_password)
    
    @staticmethod
    def enforce_password_policy(password: str) -> Tuple[bool, Optional[str]]:
        """
        强制执行密码策略
        
        Args:
            password: 要验证的密码
            
        Returns:
            (是否通过验证, 失败原因)
        """
        return enforce_password_policy(password)
    
    @staticmethod
    def generate_secure_password(length: int = 12) -> str:
        """
        生成符合密码策略的随机安全密码
        
        Args:
            length: 密码长度，默认为12
            
        Returns:
            符合密码策略的随机密码
        """
        return generate_secure_password(length) 