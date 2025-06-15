#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多因素认证工具

提供TOTP、短信和电子邮件验证码等多因素认证方式
"""
import base64
import logging
import os
import uuid
from io import BytesIO
from typing import Dict, Any, Tuple

import pyotp
import qrcode
from qrcode.image.pil import PilImage

from internal.model.errors import MFAVerificationError, InvalidVerificationCodeError


logger = logging.getLogger(__name__)


def generate_totp_secret() -> str:
    """
    生成TOTP密钥
    
    Returns:
        str: Base32编码的密钥
    """
    # 使用pyotp生成随机密钥
    return pyotp.random_base32()


def create_totp_qrcode(secret: str, username: str, issuer: str = "索克生活") -> str:
    """
    创建TOTP二维码
    
    Args:
        secret: TOTP密钥
        username: 用户名
        issuer: 发行方名称，默认"索克生活"
        
    Returns:
        str: Base64编码的二维码图像
    """
    # 创建TOTP URI
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(name=username, issuer_name=issuer)
    
    # 生成二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 将图像转换为Base64字符串
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return f"data:image/png;base64,{img_str}"


def verify_totp(secret: str, code: str) -> bool:
    """
    验证TOTP码
    
    Args:
        secret: TOTP密钥
        code: 用户提供的验证码
        
    Returns:
        bool: 验证是否通过
    """
    try:
        totp = pyotp.TOTP(secret)
        return totp.verify(code)
    except Exception as e:
        logger.exception("TOTP验证过程中发生错误")
        return False


def generate_verification_code(length: int = 6) -> str:
    """
    生成数字验证码
    
    Args:
        length: 验证码长度，默认6位
        
    Returns:
        str: 验证码
    """
    # 使用os.urandom生成随机数
    random_bytes = os.urandom(length)
    code = ''.join(str(b % 10) for b in random_bytes)
    return code


def enable_mfa(mfa_type: str, username: str, issuer: str = "索克生活") -> Dict[str, Any]:
    """
    为用户启用多因素认证
    
    Args:
        mfa_type: 多因素认证类型 ('totp', 'sms', 'email')
        username: 用户名
        issuer: 发行方名称，默认"索克生活"
        
    Returns:
        Dict: 包含密钥和相关信息
        
    Raises:
        ValueError: 不支持的多因素认证类型
    """
    if mfa_type == 'totp':
        # 生成TOTP密钥
        secret = generate_totp_secret()
        
        # 创建二维码
        qr_code_url = create_totp_qrcode(secret, username, issuer)
        
        return {
            "mfa_type": mfa_type,
            "secret_key": secret,
            "qr_code_url": qr_code_url
        }
    elif mfa_type == 'sms' or mfa_type == 'email':
        # 对于SMS和Email，只需要生成一个随机密钥作为标识符
        secret = str(uuid.uuid4())
        
        return {
            "mfa_type": mfa_type,
            "secret_key": secret
        }
    else:
        raise ValueError(f"不支持的多因素认证类型: {mfa_type}")


def verify_mfa_code(mfa_type: str, secret: str, code: str) -> bool:
    """
    验证多因素认证码
    
    Args:
        mfa_type: 多因素认证类型 ('totp', 'sms', 'email')
        secret: 密钥
        code: 用户提供的验证码
        
    Returns:
        bool: 验证是否通过
        
    Raises:
        MFAVerificationError: 验证失败
        ValueError: 不支持的多因素认证类型
    """
    try:
        if mfa_type == 'totp':
            # 对于TOTP，使用pyotp验证
            return verify_totp(secret, code)
        elif mfa_type == 'sms' or mfa_type == 'email':
            # 对于SMS和Email，验证码通常存储在Redis中
            # 这部分验证逻辑在服务层处理
            raise ValueError(f"SMS和Email验证应在服务层处理，不应使用此函数")
        else:
            raise ValueError(f"不支持的多因素认证类型: {mfa_type}")
    except Exception as e:
        logger.exception(f"{mfa_type}验证过程中发生错误")
        raise MFAVerificationError(f"验证失败: {str(e)}") 