"""
索克生活项目 - 配置管理器
统一管理项目配置和环境变量
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器"""

    def __init__(self):
        self._load_environment()
        self._validate_required_settings()

    def _load_environment(self):
        """加载环境变量"""
        # 查找 .env 文件
        env_file = Path(__file__).parent.parent.parent.parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            logger.info(f"已加载环境变量文件: {env_file}")
        else:
            logger.warning("未找到 .env 文件，使用系统环境变量")

    def _validate_required_settings(self):
        """验证必需的配置项"""
        required_settings = ["SECRET_KEY", "DATABASE_URL"]

        missing_settings = []
        for setting in required_settings:
            if not self.get(setting):
                missing_settings.append(setting)

        if missing_settings:
            logger.error(f"缺少必需的配置项: {missing_settings}")
            raise ValueError(f"缺少必需的配置项: {missing_settings}")

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """获取配置值"""
        value = os.getenv(key, default)
        if value is None:
            logger.warning(f"配置项 {key} 未设置")
        return value

    def get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔类型配置值"""
        value = self.get(key)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")

    def get_int(self, key: str, default: int = 0) -> int:
        """获取整数类型配置值"""
        value = self.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            logger.warning(f"配置项 {key} 不是有效的整数: {value}")
            return default

    def get_list(self, key: str, separator: str = ",", default: list = None) -> list:
        """获取列表类型配置值"""
        value = self.get(key)
        if value is None:
            return default or []
        return [item.strip() for item in value.split(separator) if item.strip()]

    # 数据库配置
    @property
    def database_url(self) -> str:
        return self.get("DATABASE_URL", "sqlite:///suoke_life.db")

    @property
    def database_password(self) -> Optional[str]:
        return self.get("DATABASE_PASSWORD")

    # 安全配置
    @property
    def secret_key(self) -> str:
        return self.get("SECRET_KEY", "dev-secret-key-change-in-production")

    @property
    def jwt_secret(self) -> str:
        return self.get("JWT_SECRET", self.secret_key)

    # API配置
    @property
    def api_key(self) -> Optional[str]:
        return self.get("API_KEY")

    @property
    def access_token(self) -> Optional[str]:
        return self.get("ACCESS_TOKEN")

    # AWS配置
    @property
    def aws_access_key_id(self) -> Optional[str]:
        return self.get("AWS_ACCESS_KEY_ID")

    @property
    def aws_secret_access_key(self) -> Optional[str]:
        return self.get("AWS_SECRET_ACCESS_KEY")

    # 应用配置
    @property
    def debug(self) -> bool:
        return self.get_bool("DEBUG", False)

    @property
    def log_level(self) -> str:
        return self.get("LOG_LEVEL", "INFO")

    @property
    def host(self) -> str:
        return self.get("HOST", "0.0.0.0")

    @property
    def port(self) -> int:
        return self.get_int("PORT", 8000)


# 全局配置实例
config = ConfigManager()
