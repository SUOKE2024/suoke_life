#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
密码工具单元测试
"""
import pytest
import re

from internal.security.password import (
    hash_password, 
    verify_password, 
    validate_password_policy,
    enforce_password_policy,
    generate_secure_password
)
from internal.model.errors import PasswordPolicyError


class TestPasswordSecurity:
    """密码安全功能测试"""
    
    def test_password_hash_verify(self):
        """测试密码哈希和验证"""
        # 测试常规密码
        password = "SecurePassword123!"
        hashed = hash_password(password)
        
        # 确保哈希值不是原始密码
        assert hashed != password
        
        # 确保哈希值符合Argon2格式
        assert hashed.startswith("$argon2")
        
        # 确保可以验证成功
        assert verify_password(password, hashed) is True
        
        # 确保错误密码验证失败
        assert verify_password("WrongPassword", hashed) is False
        
        # 测试空密码处理
        with pytest.raises(ValueError):
            hash_password("")
            
        # 测试不同长度的密码
        long_password = "A" * 100 + "b" * 100 + "1" * 100 + "!" * 10
        long_hashed = hash_password(long_password)
        assert verify_password(long_password, long_hashed) is True
    
    def test_password_policy_validation(self):
        """测试密码策略验证"""
        # 定义测试策略
        policy = {
            "min_length": 8,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_numbers": True,
            "require_special": True
        }
        
        # 测试符合所有要求的密码
        password = "SecureP@ss123"
        valid, message = validate_password_policy(password, policy)
        assert valid is True
        assert message is None
        
        # 测试长度不足
        short_password = "Sec@1"
        valid, message = validate_password_policy(short_password, policy)
        assert valid is False
        assert "长度" in message
        
        # 测试缺少大写字母
        no_upper_password = "securep@ss123"
        valid, message = validate_password_policy(no_upper_password, policy)
        assert valid is False
        assert "大写" in message
        
        # 测试缺少小写字母
        no_lower_password = "SECUREP@SS123"
        valid, message = validate_password_policy(no_lower_password, policy)
        assert valid is False
        assert "小写" in message
        
        # 测试缺少数字
        no_digit_password = "SecureP@ssword"
        valid, message = validate_password_policy(no_digit_password, policy)
        assert valid is False
        assert "数字" in message
        
        # 测试缺少特殊字符
        no_special_password = "SecurePassword123"
        valid, message = validate_password_policy(no_special_password, policy)
        assert valid is False
        assert "特殊字符" in message
        
        # 测试空策略（应默认为有效）
        empty_policy = {}
        valid, message = validate_password_policy("any_password", empty_policy)
        assert valid is True
        
        # 测试仅检查长度的策略
        length_policy = {"min_length": 10}
        valid, message = validate_password_policy("short", length_policy)
        assert valid is False
        valid, message = validate_password_policy("long_enough_password", length_policy)
        assert valid is True
        
        # 测试极端长度密码
        very_long_password = "A" * 1000
        valid, message = validate_password_policy(very_long_password, policy)
        assert valid is False  # 缺少其他要求的字符类型
    
    def test_enforce_password_policy(self):
        """测试强制密码策略"""
        # 定义测试策略
        policy = {
            "min_length": 8,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_numbers": True,
            "require_special": False
        }
        
        # 测试符合要求的密码（不应抛出异常）
        good_password = "SecurePassword123"
        enforce_password_policy(good_password, policy)
        
        # 测试不符合要求的密码（应抛出异常）
        with pytest.raises(PasswordPolicyError) as excinfo:
            bad_password = "weak"
            enforce_password_policy(bad_password, policy)
        
        # 验证异常消息包含适当的信息
        assert "密码策略" in str(excinfo.value)
        
        # 测试策略为None的情况
        enforce_password_policy("any_password", None)  # 不应抛出异常
    
    def test_generate_secure_password(self):
        """测试安全密码生成功能"""
        # 测试生成的密码是否符合默认策略
        password = generate_secure_password()
        assert len(password) >= 12
        
        # 检查生成的密码是否包含所有必要的字符类型
        assert re.search(r'[A-Z]', password)  # 大写字母
        assert re.search(r'[a-z]', password)  # 小写字母
        assert re.search(r'[0-9]', password)  # 数字
        assert re.search(r'[^A-Za-z0-9]', password)  # 特殊字符
        
        # 测试指定长度生成密码
        password = generate_secure_password(length=20)
        assert len(password) == 20
        
        # 测试生成密码的随机性
        passwords = [generate_secure_password() for _ in range(10)]
        # 确保生成的密码都不相同
        assert len(set(passwords)) == 10 