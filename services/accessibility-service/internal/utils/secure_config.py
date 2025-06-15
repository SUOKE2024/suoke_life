"""
安全配置管理模块
提供敏感信息的安全存储和访问机制
"""

import base64
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

try:
    from cryptography.fernet import Fernet

    CRYPTO_AVAILABLE = True
except ImportError:
    logger.warning("cryptography库不可用，将使用基础编码")
    CRYPTO_AVAILABLE = False


@dataclass
class SecureConfig:
    """安全配置管理器"""

    def __init__(self):
        self.encryption_key = self._get_encryption_key()
        self.cipher = self._init_cipher()
        self.config_file = (
            Path(__file__).parent.parent.parent / "config" / "secure_config.enc"
        )
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

    def _get_encryption_key(self) -> bytes | None:
        """获取加密密钥"""
        # 优先从环境变量获取
        key_str = os.environ.get("SUOKE_ENCRYPTION_KEY")
        if key_str:
            try:
                return base64.urlsafe_b64decode(key_str)
            except Exception as e:
                logger.warning(f"加密密钥格式错误: {e}")

        # 从密钥文件获取
        key_file = Path(__file__).parent.parent.parent / "config" / "encryption.key"
        if key_file.exists():
            try:
                with open(key_file, "rb") as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"读取密钥文件失败: {e}")

        # 生成新密钥并保存
        if CRYPTO_AVAILABLE:
            key = Fernet.generate_key()
            key_str = base64.urlsafe_b64encode(key).decode()

            # 保存到文件
            try:
                key_file.parent.mkdir(parents=True, exist_ok=True)
                with open(key_file, "wb") as f:
                    f.write(key)
                logger.info(f"新密钥已保存到: {key_file}")
            except Exception as e:
                logger.error(f"保存密钥文件失败: {e}")

            logger.warning(
                f"生成新的加密密钥，建议设置环境变量 SUOKE_ENCRYPTION_KEY: {key_str}"
            )
            return key

        return None

    def _init_cipher(self) -> Any | None:
        """初始化加密器"""
        if CRYPTO_AVAILABLE and self.encryption_key:
            try:
                return Fernet(self.encryption_key)
            except Exception as e:
                logger.error(f"加密器初始化失败: {e}")
        return None

    def encrypt_value(self, value: str) -> str:
        """加密值"""
        if self.cipher:
            try:
                encrypted = self.cipher.encrypt(value.encode())
                return base64.urlsafe_b64encode(encrypted).decode()
            except Exception as e:
                logger.error(f"值加密失败: {e}")

        # 回退到简单编码（不安全，仅用于开发）
        logger.warning("使用不安全的编码方式存储敏感信息")
        return base64.b64encode(value.encode()).decode()

    def decrypt_value(self, encrypted_value: str) -> str:
        """解密值"""
        if self.cipher:
            try:
                encrypted_data = base64.urlsafe_b64decode(encrypted_value)
                decrypted = self.cipher.decrypt(encrypted_data)
                return decrypted.decode()
            except Exception as e:
                logger.error(f"值解密失败: {e}")

        # 回退到简单解码
        try:
            return base64.b64decode(encrypted_value).decode()
        except Exception as e:
            logger.error(f"值解码失败: {e}")
            return encrypted_value

    def get_secure_config(self, config_key: str, default: str = "") -> str:
        """获取安全配置"""
        # 优先从环境变量获取
        env_value = os.environ.get(f"SUOKE_{config_key.upper()}")
        if env_value:
            return env_value

        # 从加密配置文件获取
        try:
            if self.config_file.exists():
                with open(self.config_file, encoding="utf-8") as f:
                    encrypted_configs = json.load(f)
                    if config_key in encrypted_configs:
                        encrypted_value = encrypted_configs[config_key]
                        return self.decrypt_value(encrypted_value)
        except Exception as e:
            logger.error(f"读取加密配置失败: {e}")

        return default

    def save_secure_config(self, config_key: str, value: str) -> bool:
        """保存安全配置"""
        try:
            # 读取现有配置
            existing_configs = {}
            if self.config_file.exists():
                with open(self.config_file, encoding="utf-8") as f:
                    existing_configs = json.load(f)

            # 加密并更新配置
            encrypted_value = self.encrypt_value(value)
            existing_configs[config_key] = encrypted_value

            # 写入文件
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(existing_configs, f, indent=2)

            logger.info(f"安全配置已保存: {config_key}")
            return True
        except Exception as e:
            logger.error(f"保存安全配置失败: {e}")
            return False

    def delete_secure_config(self, config_key: str) -> bool:
        """删除安全配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, encoding="utf-8") as f:
                    existing_configs = json.load(f)

                if config_key in existing_configs:
                    del existing_configs[config_key]

                    with open(self.config_file, "w", encoding="utf-8") as f:
                        json.dump(existing_configs, f, indent=2)

                    logger.info(f"安全配置已删除: {config_key}")
                    return True
            return False
        except Exception as e:
            logger.error(f"删除安全配置失败: {e}")
            return False

    def list_config_keys(self) -> list:
        """列出所有配置键"""
        try:
            if self.config_file.exists():
                with open(self.config_file, encoding="utf-8") as f:
                    existing_configs = json.load(f)
                    return list(existing_configs.keys())
        except Exception as e:
            logger.error(f"读取配置键失败: {e}")
        return []

    def validate_config(self) -> dict[str, Any]:
        """验证配置完整性"""
        result = {
            "encryption_available": CRYPTO_AVAILABLE,
            "cipher_initialized": self.cipher is not None,
            "config_file_exists": self.config_file.exists(),
            "config_keys_count": len(self.list_config_keys()),
            "environment_variables": [],
        }

        # 检查环境变量
        for key in os.environ:
            if key.startswith("SUOKE_"):
                result["environment_variables"].append(key)

        return result


# 全局安全配置实例
secure_config = SecureConfig()


def get_secure_password(config_key: str, default: str = "") -> str:
    """获取安全密码的便捷函数"""
    return secure_config.get_secure_config(config_key, default)


def save_secure_password(config_key: str, password: str) -> bool:
    """保存安全密码的便捷函数"""
    return secure_config.save_secure_config(config_key, password)


def get_database_config() -> dict[str, str]:
    """获取数据库配置"""
    return {
        "host": secure_config.get_secure_config("db_host", "localhost"),
        "port": secure_config.get_secure_config("db_port", "5432"),
        "database": secure_config.get_secure_config("db_name", "suoke_accessibility"),
        "username": secure_config.get_secure_config("db_username", "postgres"),
        "password": secure_config.get_secure_config("db_password", ""),
    }


def get_email_config() -> dict[str, str]:
    """获取邮件配置"""
    return {
        "smtp_host": secure_config.get_secure_config(
            "email_smtp_host", "smtp.gmail.com"
        ),
        "smtp_port": secure_config.get_secure_config("email_smtp_port", "587"),
        "username": secure_config.get_secure_config("email_username", ""),
        "password": secure_config.get_secure_config("email_password", ""),
        "use_tls": secure_config.get_secure_config("email_use_tls", "true").lower()
        == "true",
    }


def get_api_keys() -> dict[str, str]:
    """获取API密钥"""
    return {
        "openai_api_key": secure_config.get_secure_config("openai_api_key", ""),
        "azure_api_key": secure_config.get_secure_config("azure_api_key", ""),
        "google_api_key": secure_config.get_secure_config("google_api_key", ""),
        "baidu_api_key": secure_config.get_secure_config("baidu_api_key", ""),
    }


class SecureConfigManager:
    """安全配置管理器的高级接口"""

    def __init__(self):
        self.config = secure_config

    def setup_initial_config(self) -> bool:
        """设置初始配置"""
        try:
            # 检查是否已有配置
            if self.config.list_config_keys():
                logger.info("配置已存在，跳过初始化")
                return True

            # 设置默认配置
            default_configs = {
                "db_host": "localhost",
                "db_port": "5432",
                "db_name": "suoke_accessibility",
                "email_smtp_host": "smtp.gmail.com",
                "email_smtp_port": "587",
                "email_use_tls": "true",
            }

            for key, value in default_configs.items():
                self.config.save_secure_config(key, value)

            logger.info("初始配置已设置")
            return True
        except Exception as e:
            logger.error(f"设置初始配置失败: {e}")
            return False

    def backup_config(self, backup_path: str | None = None) -> bool:
        """备份配置"""
        try:
            if backup_path is None:
                backup_path = str(
                    self.config.config_file.parent
                    / f"secure_config_backup_{int(time.time())}.enc"
                )

            if self.config.config_file.exists():
                import shutil

                shutil.copy2(self.config.config_file, backup_path)
                logger.info(f"配置已备份到: {backup_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"备份配置失败: {e}")
            return False

    def restore_config(self, backup_path: str) -> bool:
        """恢复配置"""
        try:
            import shutil

            shutil.copy2(backup_path, self.config.config_file)
            logger.info(f"配置已从备份恢复: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"恢复配置失败: {e}")
            return False


# 导入时间模块
import time
