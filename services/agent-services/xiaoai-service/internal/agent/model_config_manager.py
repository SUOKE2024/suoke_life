#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型配置管理器
负责管理系统级和用户级的大模型配置，支持动态更新和安全存储
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import aioredis
import asyncpg
from dataclasses import dataclass, asdict
from enum import Enum

from pkg.utils.config_loader import get_config
from pkg.utils.metrics import get_metrics_collector

logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """模型提供商枚举"""
    OPENAI = "openai"
    ZHIPU = "zhipu"
    BAIDU = "baidu"
    LOCAL = "local"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    CUSTOM = "custom"


class ConfigScope(Enum):
    """配置作用域枚举"""
    SYSTEM = "system"  # 系统级配置
    USER = "user"      # 用户级配置
    TENANT = "tenant"  # 租户级配置


@dataclass
class ModelConfig:
    """模型配置数据类"""
    model_id: str
    provider: ModelProvider
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model_name: str = ""
    max_tokens: int = 2048
    temperature: float = 0.7
    enabled: bool = True
    priority: int = 1
    rate_limit: int = 60  # 每分钟请求数
    timeout: int = 30     # 超时时间（秒）
    extra_params: Dict[str, Any] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.extra_params is None:
            self.extra_params = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


class ModelConfigManager:
    """
    大模型配置管理器
    支持系统级和用户级配置管理，提供安全的API密钥存储和动态配置更新
    """
    
    def __init__(self):
        """初始化配置管理器"""
        self.config = get_config()
        self.metrics = get_metrics_collector()
        
        # 数据库连接
        self.db_pool = None
        self.redis_client = None
        
        # 加密密钥（用于API密钥加密）
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
        # 配置缓存
        self.config_cache = {}
        self.cache_ttl = 300  # 5分钟缓存
        
        # 系统默认配置
        self.system_configs = {}
        
        logger.info("模型配置管理器初始化完成")
    
    async def initialize(self):
        """异步初始化"""
        try:
            # 初始化数据库连接
            await self._init_database()
            
            # 初始化Redis连接
            await self._init_redis()
            
            # 创建数据库表
            await self._create_tables()
            
            # 加载系统默认配置
            await self._load_system_configs()
            
            logger.info("模型配置管理器异步初始化完成")
            
        except Exception as e:
            logger.error(f"模型配置管理器初始化失败: {e}")
            raise
    
    async def _init_database(self):
        """初始化数据库连接"""
        try:
            db_config = self.config.get_section('database.postgres')
            self.db_pool = await asyncpg.create_pool(
                dsn=db_config.get('uri'),
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("数据库连接池初始化成功")
            
        except Exception as e:
            logger.error(f"数据库连接初始化失败: {e}")
            raise
    
    async def _init_redis(self):
        """初始化Redis连接"""
        try:
            redis_config = self.config.get_section('database.redis')
            self.redis_client = await aioredis.from_url(
                redis_config.get('uri'),
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Redis连接初始化成功")
            
        except Exception as e:
            logger.error(f"Redis连接初始化失败: {e}")
            raise
    
    async def _create_tables(self):
        """创建数据库表"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS model_configs (
            id SERIAL PRIMARY KEY,
            model_id VARCHAR(100) NOT NULL,
            scope VARCHAR(20) NOT NULL,
            scope_id VARCHAR(100) DEFAULT 'default',
            provider VARCHAR(50) NOT NULL,
            api_key_encrypted TEXT,
            api_base VARCHAR(500),
            model_name VARCHAR(100) NOT NULL,
            max_tokens INTEGER DEFAULT 2048,
            temperature FLOAT DEFAULT 0.7,
            enabled BOOLEAN DEFAULT true,
            priority INTEGER DEFAULT 1,
            rate_limit INTEGER DEFAULT 60,
            timeout INTEGER DEFAULT 30,
            extra_params JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(model_id, scope, scope_id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_model_configs_scope ON model_configs(scope, scope_id);
        CREATE INDEX IF NOT EXISTS idx_model_configs_provider ON model_configs(provider);
        CREATE INDEX IF NOT EXISTS idx_model_configs_enabled ON model_configs(enabled);
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(create_table_sql)
        
        logger.info("数据库表创建完成")
    
    def _get_or_create_encryption_key(self) -> bytes:
        """获取或创建加密密钥"""
        key_file = "config/encryption.key"
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # 创建新密钥
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            logger.info("创建新的加密密钥")
            return key
    
    def _encrypt_api_key(self, api_key: str) -> str:
        """加密API密钥"""
        if not api_key:
            return ""
        return self.cipher.encrypt(api_key.encode()).decode()
    
    def _decrypt_api_key(self, encrypted_key: str) -> str:
        """解密API密钥"""
        if not encrypted_key:
            return ""
        try:
            return self.cipher.decrypt(encrypted_key.encode()).decode()
        except Exception as e:
            logger.error(f"API密钥解密失败: {e}")
            return ""
    
    async def _load_system_configs(self):
        """加载系统默认配置"""
        try:
            # 从配置文件加载系统默认配置
            models_config = self.config.get_section('models')
            
            # OpenAI配置
            if 'llm' in models_config:
                llm_config = models_config['llm']
                openai_config = ModelConfig(
                    model_id="system_openai",
                    provider=ModelProvider.OPENAI,
                    api_key=llm_config.get('api_key', ''),
                    api_base=llm_config.get('api_base', 'https://api.openai.com/v1'),
                    model_name=llm_config.get('primary_model', 'gpt-4o-mini'),
                    max_tokens=llm_config.get('max_tokens', 2048),
                    temperature=llm_config.get('temperature', 0.7),
                    priority=1
                )
                await self.save_config(openai_config, ConfigScope.SYSTEM)
            
            # 智谱AI配置
            if 'zhipu' in models_config:
                zhipu_config_data = models_config['zhipu']
                zhipu_config = ModelConfig(
                    model_id="system_zhipu",
                    provider=ModelProvider.ZHIPU,
                    api_key=zhipu_config_data.get('api_key', ''),
                    api_base=zhipu_config_data.get('api_base', 'https://open.bigmodel.cn/api/paas/v4'),
                    model_name="glm-4",
                    max_tokens=zhipu_config_data.get('max_tokens', 2048),
                    temperature=zhipu_config_data.get('temperature', 0.7),
                    priority=2
                )
                await self.save_config(zhipu_config, ConfigScope.SYSTEM)
            
            # 百度配置
            if 'baidu' in models_config:
                baidu_config_data = models_config['baidu']
                baidu_config = ModelConfig(
                    model_id="system_baidu",
                    provider=ModelProvider.BAIDU,
                    api_key=baidu_config_data.get('api_key', ''),
                    api_base=baidu_config_data.get('api_url', ''),
                    model_name="ernie-bot-4",
                    max_tokens=baidu_config_data.get('max_tokens', 2048),
                    temperature=baidu_config_data.get('temperature', 0.7),
                    priority=3,
                    extra_params={'secret_key': baidu_config_data.get('secret_key', '')}
                )
                await self.save_config(baidu_config, ConfigScope.SYSTEM)
            
            # 本地LLM配置
            if 'local_llm' in models_config:
                local_config_data = models_config['local_llm']
                local_config = ModelConfig(
                    model_id="system_local",
                    provider=ModelProvider.LOCAL,
                    api_base=local_config_data.get('endpoint_url', ''),
                    model_name=local_config_data.get('default_model', 'llama-3-8b'),
                    max_tokens=local_config_data.get('max_tokens', 4096),
                    temperature=local_config_data.get('temperature', 0.7),
                    priority=4
                )
                await self.save_config(local_config, ConfigScope.SYSTEM)
            
            logger.info("系统默认配置加载完成")
            
        except Exception as e:
            logger.error(f"加载系统默认配置失败: {e}")
    
    async def save_config(self, config: ModelConfig, scope: ConfigScope, scope_id: str = "default") -> bool:
        """保存模型配置"""
        try:
            # 加密API密钥
            encrypted_api_key = self._encrypt_api_key(config.api_key) if config.api_key else None
            
            # 更新时间戳
            config.updated_at = datetime.utcnow()
            
            # 保存到数据库
            insert_sql = """
            INSERT INTO model_configs (
                model_id, scope, scope_id, provider, api_key_encrypted, api_base,
                model_name, max_tokens, temperature, enabled, priority, rate_limit,
                timeout, extra_params, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
            ON CONFLICT (model_id, scope, scope_id) 
            DO UPDATE SET
                provider = EXCLUDED.provider,
                api_key_encrypted = EXCLUDED.api_key_encrypted,
                api_base = EXCLUDED.api_base,
                model_name = EXCLUDED.model_name,
                max_tokens = EXCLUDED.max_tokens,
                temperature = EXCLUDED.temperature,
                enabled = EXCLUDED.enabled,
                priority = EXCLUDED.priority,
                rate_limit = EXCLUDED.rate_limit,
                timeout = EXCLUDED.timeout,
                extra_params = EXCLUDED.extra_params,
                updated_at = EXCLUDED.updated_at
            """
            
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    insert_sql,
                    config.model_id, scope.value, scope_id, config.provider.value,
                    encrypted_api_key, config.api_base, config.model_name,
                    config.max_tokens, config.temperature, config.enabled,
                    config.priority, config.rate_limit, config.timeout,
                    json.dumps(config.extra_params), config.created_at, config.updated_at
                )
            
            # 清除缓存
            cache_key = f"model_config:{scope.value}:{scope_id}:{config.model_id}"
            await self.redis_client.delete(cache_key)
            
            # 记录指标
            # self.metrics.increment_counter(
            #     "model_config_saved",
            #     tags={"scope": scope.value, "provider": config.provider.value}
            # )
            
            logger.info(f"模型配置保存成功: {config.model_id} (scope: {scope.value})")
            return True
            
        except Exception as e:
            logger.error(f"保存模型配置失败: {e}")
            return False
    
    async def get_config(self, model_id: str, scope: ConfigScope, scope_id: str = "default") -> Optional[ModelConfig]:
        """获取模型配置"""
        try:
            # 检查缓存
            cache_key = f"model_config:{scope.value}:{scope_id}:{model_id}"
            cached_config = await self.redis_client.get(cache_key)
            
            if cached_config:
                config_data = json.loads(cached_config)
                config = ModelConfig(**config_data)
                # 解密API密钥
                if config.api_key:
                    config.api_key = self._decrypt_api_key(config.api_key)
                return config
            
            # 从数据库查询
            select_sql = """
            SELECT model_id, provider, api_key_encrypted, api_base, model_name,
                   max_tokens, temperature, enabled, priority, rate_limit, timeout,
                   extra_params, created_at, updated_at
            FROM model_configs
            WHERE model_id = $1 AND scope = $2 AND scope_id = $3
            """
            
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(select_sql, model_id, scope.value, scope_id)
            
            if not row:
                return None
            
            # 构建配置对象
            config = ModelConfig(
                model_id=row['model_id'],
                provider=ModelProvider(row['provider']),
                api_key=self._decrypt_api_key(row['api_key_encrypted']) if row['api_key_encrypted'] else None,
                api_base=row['api_base'],
                model_name=row['model_name'],
                max_tokens=row['max_tokens'],
                temperature=row['temperature'],
                enabled=row['enabled'],
                priority=row['priority'],
                rate_limit=row['rate_limit'],
                timeout=row['timeout'],
                extra_params=row['extra_params'] or {},
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            
            # 缓存配置（不包含解密后的API密钥）
            cache_data = asdict(config)
            cache_data['api_key'] = row['api_key_encrypted']  # 缓存加密后的密钥
            await self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(cache_data, default=str))
            
            return config
            
        except Exception as e:
            logger.error(f"获取模型配置失败: {e}")
            return None
    
    async def list_configs(self, scope: ConfigScope, scope_id: str = "default", enabled_only: bool = False) -> List[ModelConfig]:
        """列出模型配置"""
        try:
            where_clause = "WHERE scope = $1 AND scope_id = $2"
            params = [scope.value, scope_id]
            
            if enabled_only:
                where_clause += " AND enabled = true"
            
            select_sql = f"""
            SELECT model_id, provider, api_key_encrypted, api_base, model_name,
                   max_tokens, temperature, enabled, priority, rate_limit, timeout,
                   extra_params, created_at, updated_at
            FROM model_configs
            {where_clause}
            ORDER BY priority ASC, model_id ASC
            """
            
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(select_sql, *params)
            
            configs = []
            for row in rows:
                config = ModelConfig(
                    model_id=row['model_id'],
                    provider=ModelProvider(row['provider']),
                    api_key=self._decrypt_api_key(row['api_key_encrypted']) if row['api_key_encrypted'] else None,
                    api_base=row['api_base'],
                    model_name=row['model_name'],
                    max_tokens=row['max_tokens'],
                    temperature=row['temperature'],
                    enabled=row['enabled'],
                    priority=row['priority'],
                    rate_limit=row['rate_limit'],
                    timeout=row['timeout'],
                    extra_params=row['extra_params'] or {},
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                configs.append(config)
            
            return configs
            
        except Exception as e:
            logger.error(f"列出模型配置失败: {e}")
            return []
    
    async def delete_config(self, model_id: str, scope: ConfigScope, scope_id: str = "default") -> bool:
        """删除模型配置"""
        try:
            delete_sql = "DELETE FROM model_configs WHERE model_id = $1 AND scope = $2 AND scope_id = $3"
            
            async with self.db_pool.acquire() as conn:
                result = await conn.execute(delete_sql, model_id, scope.value, scope_id)
            
            # 清除缓存
            cache_key = f"model_config:{scope.value}:{scope_id}:{model_id}"
            await self.redis_client.delete(cache_key)
            
            # 记录指标
            # self.metrics.increment_counter(
            #     "model_config_deleted",
            #     tags={"scope": scope.value}
            # )
            
            logger.info(f"模型配置删除成功: {model_id} (scope: {scope.value})")
            return True
            
        except Exception as e:
            logger.error(f"删除模型配置失败: {e}")
            return False
    
    async def get_effective_config(self, model_id: str, user_id: str = None) -> Optional[ModelConfig]:
        """
        获取有效配置（优先级：用户配置 > 系统配置）
        """
        # 首先尝试获取用户配置
        if user_id:
            user_config = await self.get_config(model_id, ConfigScope.USER, user_id)
            if user_config and user_config.enabled:
                return user_config
        
        # 然后尝试获取系统配置
        system_config = await self.get_config(model_id, ConfigScope.SYSTEM)
        if system_config and system_config.enabled:
            return system_config
        
        return None
    
    async def validate_config(self, config: ModelConfig) -> Dict[str, Any]:
        """验证模型配置"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # 基本验证
            if not config.model_id:
                validation_result["errors"].append("模型ID不能为空")
            
            if not config.model_name:
                validation_result["errors"].append("模型名称不能为空")
            
            if config.max_tokens <= 0:
                validation_result["errors"].append("最大token数必须大于0")
            
            if not (0 <= config.temperature <= 2):
                validation_result["errors"].append("温度参数必须在0-2之间")
            
            # 提供商特定验证
            if config.provider in [ModelProvider.OPENAI, ModelProvider.ZHIPU]:
                if not config.api_key:
                    validation_result["errors"].append(f"{config.provider.value}需要API密钥")
            
            if config.provider == ModelProvider.BAIDU:
                if not config.api_key:
                    validation_result["errors"].append("百度需要API密钥")
                if not config.extra_params.get('secret_key'):
                    validation_result["errors"].append("百度需要Secret密钥")
            
            if config.provider == ModelProvider.LOCAL:
                if not config.api_base:
                    validation_result["errors"].append("本地模型需要端点URL")
            
            # 设置验证结果
            validation_result["valid"] = len(validation_result["errors"]) == 0
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"验证过程出错: {str(e)}")
        
        return validation_result
    
    async def close(self):
        """关闭连接"""
        try:
            if self.db_pool:
                await self.db_pool.close()
            
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("模型配置管理器连接已关闭")
            
        except Exception as e:
            logger.error(f"关闭连接失败: {e}")


# 全局实例
_config_manager = None


async def get_model_config_manager() -> ModelConfigManager:
    """获取模型配置管理器实例"""
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ModelConfigManager()
        await _config_manager.initialize()
    
    return _config_manager 