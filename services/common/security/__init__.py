"""
安全组件模块

提供统一的安全功能，包括：
- 加密和解密
- 认证和授权
- JWT令牌管理
- API密钥管理
- 权限检查
"""

from typing import Any, Dict, List, Optional, Union

try:
    from .auth import APIKeyManager, JWTManager, OAuth2Provider, PermissionChecker
    from .encryption import EncryptionManager

    __all__ = [
        "EncryptionManager",
        "JWTManager",
        "OAuth2Provider",
        "APIKeyManager",
        "PermissionChecker",
    ]

except ImportError as e:
    import logging

    logging.warning(f"安全模块导入失败: {e}")
    __all__ = []


def main() -> None:
    """主函数 - 用于测试安全功能"""
    try:
        # 测试加密管理器
        encryption_manager = EncryptionManager()

        # 测试数据
        test_data = "索克生活健康数据"

        # 加密
        encrypted = encryption_manager.encrypt(test_data)
        print(f"加密后: {encrypted}")

        # 解密
        decrypted = encryption_manager.decrypt(encrypted)
        print(f"解密后: {decrypted}")

        print("安全模块测试成功")

    except Exception as e:
        print(f"安全模块测试失败: {e}")


if __name__ == "__main__":
    main()
