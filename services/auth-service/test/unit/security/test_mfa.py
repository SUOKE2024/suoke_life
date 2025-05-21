#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多因素认证工具单元测试
"""
import re
import base64
from io import BytesIO

import pytest
import pyotp
from PIL import Image

from internal.security.mfa import (
    generate_totp_secret,
    create_totp_qrcode,
    verify_totp,
    generate_verification_code,
    enable_mfa,
    verify_mfa_code
)
from internal.model.errors import MFAVerificationError


class TestMFASecurity:
    """多因素认证功能测试"""
    
    def test_generate_totp_secret(self):
        """测试生成TOTP密钥"""
        # 生成密钥
        secret = generate_totp_secret()
        
        # 验证密钥格式
        assert secret is not None
        assert isinstance(secret, str)
        assert len(secret) > 0
        
        # 验证是否是有效的Base32编码字符串
        assert re.match(r'^[A-Z2-7]+=*$', secret) is not None
    
    def test_create_totp_qrcode(self):
        """测试创建TOTP二维码"""
        # 准备测试数据
        secret = generate_totp_secret()
        username = "testuser"
        issuer = "测试应用"
        
        # 创建二维码
        qrcode_uri = create_totp_qrcode(secret, username, issuer)
        
        # 验证URI格式
        assert qrcode_uri.startswith("data:image/png;base64,")
        
        # 尝试解码图像数据
        image_data = qrcode_uri.replace("data:image/png;base64,", "")
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        
        # 验证图像格式
        assert image.format == "PNG"
        assert image.size[0] > 0 and image.size[1] > 0
    
    def test_verify_totp(self):
        """测试验证TOTP码"""
        # 生成密钥
        secret = generate_totp_secret()
        
        # 创建TOTP对象
        totp = pyotp.TOTP(secret)
        
        # 生成当前有效码
        valid_code = totp.now()
        
        # 验证有效码
        assert verify_totp(secret, valid_code) is True
        
        # 验证无效码
        invalid_code = "123456"  # 假设这不是当前的有效码
        assert verify_totp(secret, invalid_code) is False
    
    def test_generate_verification_code(self):
        """测试生成验证码"""
        # 生成默认长度的验证码
        code = generate_verification_code()
        
        # 验证长度和格式
        assert isinstance(code, str)
        assert len(code) == 6
        assert code.isdigit()
        
        # 测试自定义长度
        custom_length = 8
        code = generate_verification_code(custom_length)
        assert len(code) == custom_length
        assert code.isdigit()
    
    def test_enable_mfa_totp(self):
        """测试启用TOTP多因素认证"""
        # 准备测试数据
        mfa_type = "totp"
        username = "testuser"
        
        # 启用MFA
        result = enable_mfa(mfa_type, username)
        
        # 验证结果
        assert result is not None
        assert result["mfa_type"] == mfa_type
        assert "secret_key" in result
        assert "qr_code_url" in result
        assert result["qr_code_url"].startswith("data:image/png;base64,")
    
    def test_enable_mfa_sms(self):
        """测试启用SMS多因素认证"""
        # 准备测试数据
        mfa_type = "sms"
        username = "testuser"
        
        # 启用MFA
        result = enable_mfa(mfa_type, username)
        
        # 验证结果
        assert result is not None
        assert result["mfa_type"] == mfa_type
        assert "secret_key" in result
        assert "qr_code_url" not in result
    
    def test_enable_mfa_email(self):
        """测试启用电子邮件多因素认证"""
        # 准备测试数据
        mfa_type = "email"
        username = "testuser"
        
        # 启用MFA
        result = enable_mfa(mfa_type, username)
        
        # 验证结果
        assert result is not None
        assert result["mfa_type"] == mfa_type
        assert "secret_key" in result
        assert "qr_code_url" not in result
    
    def test_enable_mfa_invalid_type(self):
        """测试启用无效类型的多因素认证"""
        # 准备测试数据
        mfa_type = "invalid_type"
        username = "testuser"
        
        # 尝试启用无效类型，应抛出异常
        with pytest.raises(ValueError) as exc_info:
            enable_mfa(mfa_type, username)
        
        # 验证异常信息
        assert "不支持的多因素认证类型" in str(exc_info.value)
    
    def test_verify_mfa_code_totp_valid(self):
        """测试验证有效的TOTP码"""
        # 准备测试数据
        mfa_type = "totp"
        mfa_result = enable_mfa(mfa_type, "testuser")
        secret = mfa_result["secret_key"]
        
        # 创建有效的TOTP码
        totp = pyotp.TOTP(secret)
        valid_code = totp.now()
        
        # 验证有效码
        assert verify_mfa_code(mfa_type, secret, valid_code) is True
    
    def test_verify_mfa_code_totp_invalid(self):
        """测试验证无效的TOTP码"""
        # 准备测试数据
        mfa_type = "totp"
        mfa_result = enable_mfa(mfa_type, "testuser")
        secret = mfa_result["secret_key"]
        
        # 创建无效的TOTP码
        invalid_code = "000000"  # 假设这不是当前有效的TOTP码
        
        # 验证无效码
        assert verify_mfa_code(mfa_type, secret, invalid_code) is False
    
    def test_verify_mfa_code_non_totp(self):
        """测试验证非TOTP类型的验证码"""
        # 准备测试数据
        mfa_type = "sms"
        secret = "some_secret"
        code = "123456"
        
        # 尝试验证，应抛出异常
        with pytest.raises(ValueError) as exc_info:
            verify_mfa_code(mfa_type, secret, code)
        
        # 验证异常信息
        assert "应在服务层处理" in str(exc_info.value) 