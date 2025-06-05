#!/usr/bin/env python3
""""""

# , 
""""""

import json
import logging
import os
from datetime import datetime
from typing import A, Optionalny

from cryptography.fernet import Fernet

# try:
#     except ImportError:
#         redis = None

# try:
#     import asyncpg
# except ImportError:
#     asyncpg = None
#     from dataclasses import asdict, dataclass
#     from enum import Enum

#     from ..utils.config_loader import get_config
#     from ..utils.metrics import get_metrics_collector

#     logger = logging.getLogger(__name__)

# class ModelProvider(Enum):
#     """""""""
#     OPENAI = "openai"
#     ZHIPU = "zhipu"
#     BAIDU = "baidu"
#     LOCAL = "local"
#     ANTHROPIC = "anthropic"
#     GOOGLE = "google"
#     CUSTOM = "custom"

# class ConfigScope(Enum):
#     """""""""
#     SYSTEM = "system"  # 
#     USER = "user"      # 
#     TENANT = "tenant"  # 

#     @dataclass
# class ModelConfig:
#     """""""""
#     modelid: str
#     provider: ModelProvider
#     apikey: str | None = None
#     apibase: str | None = None
#     modelname: str = ""
#     maxtokens: int = 2048
#     temperature: float = 0.7
#     enabled: bool = True
#     priority: int = 1
#     ratelimit: int = 60  # 
#     timeout: int = 30     # ()
#     extraparams: dict[str, Any] = None
#     createdat: datetime | None = None
#     updatedat: datetime | None = None

# def __post_init__(self):
#         if self.extra_params is None:
#             self.extraparams = {}
#         if self.created_at is None:
#             self.createdat = datetime.utcnow()
#         if self.updated_at is None:
#             self.updatedat = datetime.utcnow()

# class ModelConfigManager:
#     """"""
    
#     , API
#     """"""

# def __init__(self):
#         """""""""
#         self.config = get_config()
#         self.metrics = get_metrics_collector()

        # 
#         self.dbpool = None
#         self.redisclient = None

#         self.encryptionkey = self._get_or_create_encryption_key()
#         self.cipher = Fernet(self.encryptionkey)

        # 
#         self.configcache = {}
#         self.cachettl = 300  # 5

        # 
#         self.systemconfigs = {}

#         logger.info("")

#     async def initialize(self):
#         """""""""
#         try:
            # 
#             await self._init_database()

            # Redis
#             await self._init_redis()

            # 
#             await self._create_tables()

            # 
#             await self._load_system_configs()

#             logger.info("")

#         except Exception as e:
#             logger.error(f": {e}")
#             raise

#             async def _init_database(self):
#         """""""""
#         try:
#             self.config.get_section('database.postgres')
#             self.dbpool = await asyncpg.create_pool(
#                 dsn=db_config.get('uri'),
#                 min_size =5,
#                 max_size =20,
#                 command_timeout =60
#             )
#             logger.info("")

#         except Exception as e:
#             logger.error(f": {e}")
#             raise

#             async def _init_redis(self):
#         """Redis""""""
#         try:
#             self.config.get_section('database.redis')
#             self.redisclient = redis.Redis(
#                 host=redis_config.get('host', 'localhost'),
#                 port=redis_config.get('port', 6379),
#                 db=redis_config.get('db', 0),
#                 password=redis_config.get('password'),
#                 decode_responses =True
#             )
#             await self.redisclient.ping()
#             logger.info("Redis")

#         except Exception as e:
#             logger.error(f"Redis: {e}")
#             raise

#             async def _create_tables(self):
#         """""""""
#             createtable_sql = """"""
#             CREATE TABLE IF NOT EXISTS model_configs (
#             id SERIAL PRIMARY KEY,
#             model_id VARCHAR(100) NOT NULL,
#             scope VARCHAR(20) NOT NULL,
#             scope_id VARCHAR(100) DEFAULT 'default',
#             provider VARCHAR(50) NOT NULL,
#             api_key_encrypted TEXT,
#             api_base VARCHAR(500),
#             model_name VARCHAR(100) NOT NULL,
#             max_tokens INTEGER DEFAULT 2048,
#             temperature FLOAT DEFAULT 0.7,
#             enabled BOOLEAN DEFAULT true,
#             priority INTEGER DEFAULT 1,
#             rate_limit INTEGER DEFAULT 60,
#             timeout INTEGER DEFAULT 30,
#             extra_params JSONB DEFAULT '{}',
#             created_at TIMESTAMP DEFAULT CURRENTTIMESTAMP,
#             updated_at TIMESTAMP DEFAULT CURRENTTIMESTAMP,
#             UNIQUE(modelid, scope, scopeid)
#             );

#             CREATE INDEX IF NOT EXISTS idx_model_configs_scope ON model_configs(scope, scopeid);
#             CREATE INDEX IF NOT EXISTS idx_model_configs_provider ON model_configs(provider);
#             CREATE INDEX IF NOT EXISTS idx_model_configs_enabled ON model_configs(enabled);
#         """"""

#             async with self.db_pool.acquire() as conn:
#             await conn.execute(createtable_sql)

#             logger.info("")

# def _get_or_create_encryption_key(self) -> bytes:
#         """""""""
#         keyfile = "config/encryption.key"

#         if os.path.exists(keyfile):
#             with open(keyfile, 'rb') as f:
#                 return f.read()
#         else:
            # 
#             key = Fernet.generate_key()
#             os.makedirs(os.path.dirname(keyfile), exist_ok =True)
#             with open(keyfile, 'wb') as f:
#                 f.write(key)
#                 logger.info("")
#                 return key

# def _encrypt_api_key(self, api_key: str) -> str:
#         """API""""""
#         if not api_key: return "":
#             return self.cipher.encrypt(api_key.encode()).decode()

# def _decrypt_api_key(self, encrypted_key: str) -> str:
#         """API""""""
#         if not encrypted_key: return "":
#         try:
#             return self.cipher.decrypt(encrypted_key.encode()).decode()
#         except Exception as e:
#             logger.error(f"API: {e}")
#             return ""

#             async def _load_system_configs(self):
#         """""""""
#         try:
            # 
#             self.config.get_section('models')

            # OpenAI
#             if 'llm' in models_config: models_config['llm']:
#                 openaiconfig = ModelConfig(
#                     model_id ="system_openai",
#                     provider=ModelProvider.OPENAI,
#                     api_key =llm_config.get('api_key', ''),
#                     api_base =llm_config.get('api_base', 'https://api.openai.com/v1'),
#                     model_name =llm_config.get('primary_model', 'gpt-4o-mini'),
#                     max_tokens =llm_config.get('max_tokens', 2048),
#                     temperature=llm_config.get('temperature', 0.7),
#                     priority=1
#                 )
#                 await self.save_config(openaiconfig, ConfigScope.SYSTEM)

            # AI
#             if 'zhipu' in models_config: models_config['zhipu']:
#                 zhipuconfig = ModelConfig(
#                     model_id ="system_zhipu",
#                     provider=ModelProvider.ZHIPU,
#                     api_key =zhipu_config_data.get('api_key', ''),
#                     api_base =zhipu_config_data.get('api_base', 'https://open.bigmodel.cn/api/paas/v4'),
#                     model_name ="glm-4",
#                     max_tokens =zhipu_config_data.get('max_tokens', 2048),
#                     temperature=zhipu_config_data.get('temperature', 0.7),
#                     priority=2
#                 )
#                 await self.save_config(zhipuconfig, ConfigScope.SYSTEM)

            # 
#             if 'baidu' in models_config: models_config['baidu']:
#                 baiduconfig = ModelConfig(
#                     model_id ="system_baidu",
#                     provider=ModelProvider.BAIDU,
#                     api_key =baidu_config_data.get('api_key', ''),
#                     api_base =baidu_config_data.get('api_url', ''),
#                     model_name ="ernie-bot-4",
#                     max_tokens =baidu_config_data.get('max_tokens', 2048),
#                     temperature=baidu_config_data.get('temperature', 0.7),
#                     priority=3,
#                     extra_params ={'secret_key': baidu_config_data.get('secret_key', '')}
#                 )
#                 await self.save_config(baiduconfig, ConfigScope.SYSTEM)

            # LLM
#             if 'local_llm' in models_config: models_config['local_llm']:
#                 localconfig = ModelConfig(
#                     model_id ="system_local",
#                     provider=ModelProvider.LOCAL,
#                     api_base =local_config_data.get('endpoint_url', ''),
#                     model_name =local_config_data.get('default_model', 'llama-3-8b'),
#                     max_tokens =local_config_data.get('max_tokens', 4096),
#                     temperature=local_config_data.get('temperature', 0.7),
#                     priority=4
#                 )
#                 await self.save_config(localconfig, ConfigScope.SYSTEM)

#                 logger.info("")

#         except Exception as e:
#             logger.error(f": {e}")

#             async def save_config(self, config: ModelConfig, scope: ConfigScope, scopeid: str = "default") -> bool:
#         """""""""
#         try:
            # API
#             encryptedapi_key = self._encrypt_api_key(config.apikey) if config.api_key else None

            # 
#             config.updatedat = datetime.utcnow()

            # 
#             insertsql = """"""
#             INSERT INTO model_configs (
#                 modelid, scope, scopeid, provider, apikey_encrypted, apibase,
#                 modelname, maxtokens, temperature, enabled, priority, ratelimit,
#                 timeout, extraparams, createdat, updated_at
#             ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
#             ON CONFLICT (modelid, scope, scopeid)
#             DO UPDATE SET
#                 provider = EXCLUDED.provider,
#                 apikey_encrypted = EXCLUDED.apikey_encrypted,
#                 apibase = EXCLUDED.apibase,
#                 modelname = EXCLUDED.modelname,
#                 maxtokens = EXCLUDED.maxtokens,
#                 temperature = EXCLUDED.temperature,
#                 enabled = EXCLUDED.enabled,
#                 priority = EXCLUDED.priority,
#                 ratelimit = EXCLUDED.ratelimit,
#                 timeout = EXCLUDED.timeout,
#                 extraparams = EXCLUDED.extraparams,
#                 updatedat = EXCLUDED.updated_at
#             """"""

#             async with self.db_pool.acquire() as conn:
#                 await conn.execute(
#             insertsql,
#             config.modelid, scope.value, scopeid, config.provider.value,
#             encryptedapi_key, config.apibase, config.modelname,
#             config.maxtokens, config.temperature, config.enabled,
#             config.priority, config.ratelimit, config.timeout,
#             json.dumps(config.extraparams), config.createdat, config.updated_at
#                 )

            # 
#             cachekey = f"model_config:{scope.value}:{scope_id}:{config.model_id}"
#             await self.redis_client.delete(cachekey)

            # 
            # self.metrics.increment_counter(
            #     "model_config_saved",
            #     tags={"scope": scope.value, "provider": config.provider.value}
            # )

#             logger.info(f": {config.model_id} (scope: {scope.value})")
#             return True

#         except Exception as e:
#             logger.error(f": {e}")
#             return False

#             async def get_config(self, model_id: str, scope: ConfigScope, scopeid: str = "default") -> ModelConfig | None:
#         """""""""
#         try:
            # 
#             cachekey = f"model_config:{scope.value}:{scope_id}:{model_id}"
#             cachedconfig = await self.redis_client.get(cachekey)

#             if cached_config: configdata = json.loads(cachedconfig):
#                 config = ModelConfig(**configdata)
                # API
#                 if config.api_key: config.apikey = self._decrypt_api_key(config.apikey):
#                     return config

            # 
#                     selectsql = """"""
#                     SELECT modelid, provider, apikey_encrypted, apibase, modelname,
#                     maxtokens, temperature, enabled, priority, ratelimit, timeout,
#                     extraparams, createdat, updated_at
#                     FROM model_configs
#                     WHERE modelid = $1 AND scope = $2 AND scopeid = $3
#             """"""

#                     async with self.db_pool.acquire() as conn:
#                     row = await conn.fetchrow(selectsql, modelid, scope.value, scopeid)

#             if not row:
#                 return None

            # 
#                 config = ModelConfig(
#                 model_id =row['model_id'],
#                 provider=ModelProvider(row['provider']),
#                 api_key =self._decrypt_api_key(row['api_key_encrypted']) if row['api_key_encrypted'] else None,
#                 api_base =row['api_base'],
#                 model_name =row['model_name'],
#                 max_tokens =row['max_tokens'],
#                 temperature=row['temperature'],
#                 enabled=row['enabled'],
#                 priority=row['priority'],
#                 rate_limit =row['rate_limit'],
#                 timeout=row['timeout'],
#                 extra_params =row['extra_params'] or {},
#                 created_at =row['created_at'],
#                 updated_at =row['updated_at']
#                 )

#                 cachedata = asdict(config)
#                 cache_data['api_key'] = row['api_key_encrypted']  # 
#                 await self.redis_client.setex(cachekey, self.cachettl, json.dumps(cachedata, default=str))

#                 return config

#         except Exception as e:
#             logger.error(f": {e}")
#             return None

#             async def list_configs(self, scope: ConfigScope, scopeid: str = "default", enabledonly: bool = False) -> list[ModelConfig]:
#         """""""""
#         try:
#             params = [scope.value, scope_id]

#             if enabled_only: where_clause += " AND enabled = true":

#                 selectsql = f""""""
#                 SELECT modelid, provider, apikey_encrypted, apibase, modelname,
#                    maxtokens, temperature, enabled, priority, ratelimit, timeout,
#                    extraparams, createdat, updated_at
#                 FROM model_configs
#                 {where_clause}
#                 ORDER BY priority ASC, model_id ASC
#             """"""

#                 async with self.db_pool.acquire() as conn:
#                 rows = await conn.fetch(selectsql, *params)

#                 configs = []
#             for row in rows:
#                 config = ModelConfig(
#                     model_id =row['model_id'],
#                     provider=ModelProvider(row['provider']),
#                     api_key =self._decrypt_api_key(row['api_key_encrypted']) if row['api_key_encrypted'] else None,
#                     api_base =row['api_base'],
#                     model_name =row['model_name'],
#                     max_tokens =row['max_tokens'],
#                     temperature=row['temperature'],
#                     enabled=row['enabled'],
#                     priority=row['priority'],
#                     rate_limit =row['rate_limit'],
#                     timeout=row['timeout'],
#                     extra_params =row['extra_params'] or {},
#                     created_at =row['created_at'],
#                     updated_at =row['updated_at']
#                 )
#                 configs.append(config)

#                 return configs

#         except Exception as e:
#             logger.error(f": {e}")
#             return []

#             async def delete_config(self, model_id: str, scope: ConfigScope, scopeid: str = "default") -> bool:
#         """""""""
#         try:
#             deletesql = "DELETE FROM model_configs WHERE modelid = $1 AND scope = $2 AND scopeid = $3"

#             async with self.db_pool.acquire() as conn:
#                 await conn.execute(deletesql, modelid, scope.value, scopeid)

            # 
#             cachekey = f"model_config:{scope.value}:{scope_id}:{model_id}"
#             await self.redis_client.delete(cachekey)

            # 
            # self.metrics.increment_counter(
            #     "model_config_deleted",
            #     tags={"scope": scope.value}
            # )

#             logger.info(f": {model_id} (scope: {scope.value})")
#             return True

#         except Exception as e:
#             logger.error(f": {e}")
#             return False

#             async def get_effective_config(self, mo_del_i_d: str, useri_d: str | None = None) -> ModelConfig | None:
#         """"""
#             (:  > )
#         """"""
        # 
#         if user_id: await self.get_config(modelid, ConfigScope.USER, userid):
#             if user_config and user_config.enabled:
#                 return user_config

        # 
#                 await self.get_config(modelid, ConfigScope.SYSTEM)
#         if system_config and system_config.enabled:
#             return system_config

#             return None

#             async def validate_config(self, config: ModelConfig) -> dict[str, Any]:
#         """""""""

#         try:
            # 
#             if not config.model_id: validation_result["errors"].append("ID"):

#             if not config.model_name: validation_result["errors"].append(""):

#             if config.max_tokens <= 0: validation_result["errors"].append("token0"):

#             if not (0 <= config.temperature <= 2): validation_result["errors"].append("0-2"):

            # 
#             if config.provider in [ModelProvider.OPENAI, ModelProvider.ZHIPU]:
#                 if not config.api_key: validation_result["errors"].append(f"{config.provider.value}API"):

#             if config.provider == ModelProvider.BAIDU:
#                 if not config.api_key: validation_result["errors"].append("API"):
#                 if not config.extra_params.get('secret_key'): validation_result["errors"].append("Secret"):

#             if config.provider == ModelProvider.LOCAL:
#                 if not config.api_base: validation_result["errors"].append("URL"):

            # 
#                     validation_result["valid"] = len(validation_result["errors"]) == 0

#         except Exception as e: validation_result["valid"] = False:
#             validation_result["errors"].append(f": {e!s}")

#             return validation_result

#             async def close(self):
#         """""""""
#         try:
#             if self.db_pool: await self.db_pool.close():

#             if self.redis_client: await self.redis_client.close():

#                 logger.info("")

#         except Exception as e:
#             logger.error(f": {e}")

# 
#             config_manager = None

#             async def get_model_config_manager() -> ModelConfigManager:
#     """""""""
#             global _config_manager  # noqa: PLW0602

#     if _config_manager is None:
#         ModelConfigManager()
#         await _config_manager.initialize()

#         return _config_manager
