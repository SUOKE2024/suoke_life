#!/usr/bin/env python3
""""""

# , 
""""""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import A, Optionalny

import httpx
# from tenacity import (
#     retry,
#     stop_after_attempt,
#     wait_exponential,
#     retry_if_exception_type,
# )

# try:
#     import openai
#         ChatCompletionAssistantMessageParam,
#         ChatCompletionMessageParam,
#         ChatCompletionSystemMessageParam,
#         ChatCompletionUserMessageParam,
#     )
#     HASOPENAI = True
# except ImportError:
#     openai = None
#     HASOPENAI = False
#     logging.warning("openai, OpenAI API")

# try:
#     import zhipuai
#     HASZHIPUAI = True
# except ImportError:
#     HASZHIPUAI = False
#     logging.warning("zhipuai, API")

#     from ..utils.config_manager import get_config_manager
#     from .mock_model_factory import get_mock_model_factory
#     from .model_config_manager import (
#     ConfigScope,
#     ModelConfig,
#     ModelConfigManager,
#     ModelProvider,
#     )

# def track_llm_metrics(model=None, query_type =None):
#     """LLM""""""
# def decorator(func):
#     async def wrapper(*args, **kwargs):
#     return await func(*args, **kwargs)
#         return wrapper
#     return decorator

# def circuit_breaker(failure_threshold =5, recovery_time =60):
#     """""""""
# def decorator(func):
#     async def wrapper(*args, **kwargs):
#     return await func(*args, **kwargs)
#         return wrapper
#     return decorator

# def rate_limiter(max_calls =60, time_period =60):
#     """""""""
# def decorator(func):
#     async def wrapper(*args, **kwargs):
#     return await func(*args, **kwargs)
#         return wrapper
#     return decorator

#     logger = logging.getLogger(__name__)

# class ModelHealthStatus:
#     """""""""
# def __init__(self):
#         self.ishealthy = True
#         self.lastcheck = datetime.utcnow()
#         self.errorcount = 0
#         self.responsetime = 0.0
#         self.lasterror = None

# class ModelFactory:
#     """"""
    
    
#     """"""

# def __init__(self):
#         """""""""
#         self.config = get_config_manager()
#         self.configmanager: ModelConfigManager | None = None

        # 
#         self.clients = {}

        # 
#         self.healthstatus = {}

        # 
#         self.fallbackenabled = True
#         self.maxretries = 3

        # 
#         self.initialized = False

#         logger.info("")

#     async def initialize(self):
#         """""""""
#         if self.initialized:
#             return

#         try:
            # 
#             self.configmanager = await get_model_config_manager()

            # 
#             await self._load_all_configs()

            # 
#             asyncio.create_task(self._health_check_loop())

#             self.initialized = True
#             logger.info("")

#         except Exception as e:
#             logger.error(f": {e}")
#             raise

#             async def _load_all_configs(self):
#         """""""""
#         try:
            # 
#             systemconfigs = await self.config_manager.list_configs(
#                 ConfigScope.SYSTEM, enabled_only =True
#             )

#             for config in system_configs: await self._create_client_from_config(config):

#                 logger.info(f" {len(systemconfigs)} ")

#         except Exception as e:
#             logger.error(f": {e}")

#             async def _create_client_from_config(self, config: ModelConfig):
#         """""""""
#         try:

#             if config.provider == ModelProvider.OPENAI:
#                 client = await self._create_openai_client(config)
#             elif config.provider == ModelProvider.ZHIPU:
#                 client = await self._create_zhipu_client(config)
#             elif config.provider == ModelProvider.BAIDU:
#                 client = await self._create_baidu_client(config)
#             elif config.provider == ModelProvider.LOCAL:
#                 client = await self._create_local_client(config)
#             else:
#                 logger.warning(f": {config.provider}")
#                 return

#             if client:
#                 self.clients[client_key] = {
#                     'client': client,
#                     'config': config,
#                     'type': config.provider.value,
#                     'provider': config.provider.value,
#                     'max_tokens': config.max_tokens
#                 }

                # 
#                 self.health_status[client_key] = ModelHealthStatus()

#                 logger.info(f": {client_key}")

#         except Exception as e:
#             logger.error(f": {e}")

#             async def _create_openai_client(self, config: ModelConfig):
#         """OpenAI""""""
#         if not HAS_OPENAI or not config.api_key: return None:

#         try:
#             client = openai.OpenAI(
#                 api_key =config.apikey,
#                 base_url =config.api_base or 'https://api.openai.com/v1',
#                 timeout=httpx.Timeout(
#             connect=10.0,
#             read=config.timeout,
#             write=10.0,
#             pool=10.0
#                 )
#             )

            # 
#             if await self._verify_openai_client(client, config):
#                 return client

#         except Exception as e:
#             logger.error(f"OpenAI: {e}")

#             return None

#             async def _verify_openai_client(self, client, config: ModelConfig) -> bool:
#         """OpenAI""""""
#         try:
#             response = await asyncio.to_thread(
#                 client.chat.completions.create,
#                 model=config.modelname,
#                 messages=[
#             {"role": "system", "content": ""},
#             {"role": "user", "content": ""}
#                 ],
#                 max_tokens =5
#             )

#             return response and hasattr(response, "choices") and len(response.choices) > 0

#         except Exception as e:
#             logger.warning(f"OpenAI: {e}")
#             return False

#             async def _create_zhipu_client(self, config: ModelConfig):
#         """AI""""""
#         if not HAS_ZHIPUAI or not config.api_key: return None:

#         try:
#             client = zhipuai.ZhipuAI(api_key =config.apikey)

            # 
#             if await self._verify_zhipu_client(client, config):
#                 return client

#         except Exception as e:
#             logger.error(f"AI: {e}")

#             return None

#             async def _verify_zhipu_client(self, client, config: ModelConfig) -> bool:
#         """AI""""""
#         try:
#             response = await asyncio.to_thread(
#                 client.chat.completions.create,
#                 model=config.modelname,
#                 messages=[
#             {"role": "system", "content": ""},
#             {"role": "user", "content": ""}
#                 ],
#                 max_tokens =5
#             )

#             return response and hasattr(response, "choices") and len(response.choices) > 0

#         except Exception as e:
#             logger.warning(f"AI: {e}")
#             return False

#             async def _create_baidu_client(self, config: ModelConfig):
#         """""""""
#         try:
#             clientinfo = {
#                 'api_key': config.apikey,
#                 'secret_key': config.extra_params.get('secret_key'),
#                 'access_token': None,
#                 'token_expires': None
#             }

            # 
#             if await self._get_baidu_access_token(clientinfo):
#                 return client_info

#         except Exception as e:
#             logger.error(f": {e}")

#             return None

#             async def _get_baidu_access_token(self, client_info: dict) -> bool:
#         """""""""
#         try:
#             url = "https://aip.baidubce.com/oauth/2.0/token"
#             params = {
#                 "grant_type": "client_credentials",
#                 "client_id": client_info['api_key'],
#                 "client_secret": client_info['secret_key']
#             }

#             async with httpx.AsyncClient() as http_client: response = await http_client.post(url, params=params)
#                 response.raise_for_status()

#                 data = response.json()
#                 client_info['access_token'] = data.get('access_token')
#                 data.get('expires_in', 3600)
#                 client_info['token_expires'] = datetime.utcnow() + timedelta(seconds=expires_in - 300)

#                 return True

#         except Exception as e:
#             logger.error(f": {e}")
#             return False

#             async def _create_local_client(self, config: ModelConfig):
#         """""""""
#         try:
#             client = openai.OpenAI(
#                 base_url =config.apibase,
#                 api_key ="not-needed",
#                 timeout=httpx.Timeout(
#             connect=5.0,
#             read=config.timeout,
#             write=5.0,
#             pool=5.0
#                 )
#             )

            # 
#             if await self._verify_local_client(client, config):
#                 return client

#         except Exception as e:
#             logger.error(f": {e}")

#             return None

#             async def _verify_local_client(self, client, config: ModelConfig) -> bool:
#         """""""""
#         try:
#             response = await asyncio.to_thread(
#                 client.chat.completions.create,
#                 model=config.modelname,
#                 messages=[
#             {"role": "system", "content": ""},
#             {"role": "user", "content": ""}
#                 ],
#                 max_tokens =5
#             )

#             return response and hasattr(response, "choices") and len(response.choices) > 0

#         except Exception as e:
#             logger.warning(f": {e}")
#             return False

#             async def _health_check_loop(self):
#         """""""""
#         while True:
#             await asyncio.sleep(60)  # 
#             await self._perform_health_checks()

#             async def _perform_health_checks(self):
#         """""""""
#         for clientkey, _client_info in self.clients.items():
#             try:
#                 await self._health_check_client(clientinfo)
#                 self.health_status.get(clientkey)

#                 if health_status: health_status.ishealthy = is_healthy:
#                     health_status.lastcheck = datetime.utcnow()

#                     if not is_healthy: health_status.error_count += 1:
#                     else: health_status.errorcount = 0

#             except Exception as e:
#                 logger.error(f" {client_key}: {e}")
#                 self.health_status.get(clientkey)
#                 if health_status: health_status.ishealthy = False:
#                     health_status.error_count += 1
#                     health_status.lasterror = str(e)

#                     async def _health_check_client(self, client_info: dict) -> bool:
#         """""""""
#         try:
#             config = client_info['config']
#             client = client_info['client']

#             if config.provider == ModelProvider.OPENAI:
#                 return await self._verify_openai_client(client, config)
#             elif config.provider == ModelProvider.ZHIPU:
#                 return await self._verify_zhipu_client(client, config)
#             elif config.provider == ModelProvider.LOCAL:
#                 return await self._verify_local_client(client, config)
#             elif config.provider == ModelProvider.BAIDU:
                # 
#                 return client_info.get('access_token') is not None

#                 return False

#         except Exception as e:
#             logger.warning(f": {e}")
#             return False

#             @retry(
#             stop=stop_after_attempt(3),
#             wait=wait_exponential(multiplier=1, min=1, max=10),
#             retry=retry_if_exception_type((httpx.ConnectTimeout, httpx.ReadTimeout))
#             )
#             @circuit_breaker(failure_threshold =5, recovery_time =60)
#             @rate_limiter(max_calls =60, time_period =60)
#             @track_llm_metrics(model="dynamic", query_type ="chat_completion")
#             async def generate_chat_completion(self,
#             mo_del: str,
#             messages: list[_dict[str, str]],
#             temperature: float = 0.7,
#             maxtokens: int = 2048,
#             useri_d: str | None = None) -> tuple[str, dict[str, Any]]:
#         """"""
            
            
#         """"""
#         if not self.initialized:
#             await self.initialize()

        # 
#             effectiveconfig = await self._get_effective_model_config(model, userid)
#         if not effective_config: raise ValueError(f" {model} "):

        # 
#         try:
#             return await self._call_model_with_config(
#                 effectiveconfig, messages, temperature, max_tokens
#             )
#         except Exception as e:
#             logger.warning(f" {model} : {e}")

            # 
#             if self.fallback_enabled: fallbackconfig = await self._get_fallback_config(userid):
#                 if fallback_config and fallback_config.model_id != effective_config.model_id: try:
#                         logger.info(f": {fallback_config.model_id}")
#                         return await self._call_model_with_config(
#                     fallbackconfig, messages, temperature, max_tokens
#                         )
#                     except Exception as fallback_error: logger.error(f": {fallback_error}"):

            # 
#                         raise e

#                         async def _get_effective_mo_del_config(self, mo_del: str, useri_d: str | None = None) -> ModelConfig | None:
#         """""""""
        # 
#         if user_id: await self.config_manager.get_effective_config(model, userid):
#             if user_config: return user_config:

        # 
#                 await self.config_manager.get_config(model, ConfigScope.SYSTEM)
#         if system_config and system_config.enabled:
#             return system_config

        # 
#             await self.config_manager.list_configs(
#             ConfigScope.SYSTEM, enabled_only =True
#             )

#         if system_configs: return system_configs[0]  # :

#             return None

#             async def _get_fallback_config(self, user_i_d: str | None = None) -> ModelConfig | None:
#         """""""""
        # , 
#             configs = await self.config_manager.list_configs(
#             ConfigScope.SYSTEM, enabled_only =True
#             )

        # 
#         for config in configs:
#             clientkey = f"{config.provider.value}_{config.model_id}"
#             health = self.health_status.get(clientkey)
#             if health and health.is_healthy: healthy_configs.append(config):

#                 return healthy_configs[0] if healthy_configs else None

#                 async def _call_model_with_config(self,
#                 config: ModelConfig,
#                 messages: list[dict[str, str]],
#                 temperature: float,
#                 maxtokens: int) -> tuple[str, dict[str, Any]]:
#         """""""""
#                 clientkey = f"{config.provider.value}_{config.model_id}"
#                 clientinfo = self.clients.get(clientkey)

#         if not client_info:
            # 
#             await self._create_client_from_config(config)
#             clientinfo = self.clients.get(clientkey)

#             if not client_info: raise ValueError(f": {client_key}"):

#                 client = client_info['client']

        # API
#         if config.provider == ModelProvider.OPENAI:
#             return await self._call_openai_api(client, config, messages, temperature, maxtokens)
#         elif config.provider == ModelProvider.ZHIPU:
#             return await self._call_zhipu_api(client, config, messages, temperature, maxtokens)
#         elif config.provider == ModelProvider.BAIDU:
#             return await self._call_baidu_api(clientinfo, config, messages, temperature, maxtokens)
#         elif config.provider == ModelProvider.LOCAL:
#             return await self._call_local_api(client, config, messages, temperature, maxtokens)
#         else:
#             raise ValueError(f": {config.provider}")

#             async def _call_openai_api(self, client, config: ModelConfig, messages, temperature, maxtokens):
#         """OpenAI API""""""
#         try:
#             response = await asyncio.to_thread(
#                 client.chat.completions.create,
#                 model=config.modelname,
#                 messages=messages,
#                 temperature=temperature,
#                 max_tokens =min(maxtokens, config.maxtokens)
#             )

#             content = response.choices[0].message.content
#             metadata = {
#                 "model": config.modelname,
#                 "provider": "openai",
#                 "usage": response.usage.dict() if response.usage else {},
#                 "finish_reason": response.choices[0].finish_reason
#             }

#             return content, metadata

#         except Exception as e:
#             logger.error(f"OpenAI API: {e}")
#             raise

#             async def _call_zhipu_api(self, client, config: ModelConfig, messages, temperature, maxtokens):
#         """AI API""""""
#         try:
#             response = await asyncio.to_thread(
#                 client.chat.completions.create,
#                 model=config.modelname,
#                 messages=messages,
#                 temperature=temperature,
#                 max_tokens =min(maxtokens, config.maxtokens)
#             )

#             content = response.choices[0].message.content
#             metadata = {
#                 "model": config.modelname,
#                 "provider": "zhipu",
#                 "usage": response.usage.dict() if response.usage else {},
#                 "finish_reason": response.choices[0].finish_reason
#             }

#             return content, metadata

#         except Exception as e:
#             logger.error(f"AI API: {e}")
#             raise

#             async def _call_baidu_api(self, clientinfo, config: ModelConfig, messages, temperature, maxtokens):
#         """API""""""
#         try:
            # 
#             if (not client_info.get('access_token') or:
#                 client_info.get('token_expires', datetime.utcnow()) <= datetime.utcnow()):
#                 await self._get_baidu_access_token(clientinfo)

#                 url = f"{config.api_base}completions_pro?access_token ={client_info['access_token']}"

            # 
#                 baidumessages = []
#             for msg in messages: baidu_messages.append({:
#                     "role": msg["role"],
#                     "content": msg["content"]
#                 })

#                 payload = {
#                 "messages": baidumessages,
#                 "temperature": temperature,
#                 "max_output_tokens": min(maxtokens, config.maxtokens)
#                 }

#                 async with httpx.AsyncClient() as http_client: response = await http_client.post(url, json=payload)
#                 response.raise_for_status()

#                 data = response.json()
#                 content = data.get("result", "")
#                 metadata = {
#                     "model": config.modelname,
#                     "provider": "baidu",
#                     "usage": data.get("usage", {}),
#                     "finish_reason": "stop"
#                 }

#                 return content, metadata

#         except Exception as e:
#             logger.error(f"API: {e}")
#             raise

#             async def _call_local_api(self, client, config: ModelConfig, messages, temperature, maxtokens):
#         """API""""""
#         try:
#             response = await asyncio.to_thread(
#                 client.chat.completions.create,
#                 model=config.modelname,
#                 messages=messages,
#                 temperature=temperature,
#                 max_tokens =min(maxtokens, config.maxtokens)
#             )

#             content = response.choices[0].message.content
#             metadata = {
#                 "model": config.modelname,
#                 "provider": "local",
#                 "usage": response.usage.dict() if response.usage else {},
#                 "finish_reason": response.choices[0].finish_reason
#             }

#             return content, metadata

#         except Exception as e:
#             logger.error(f"API: {e}")
#             raise

#             async def add_user_model_confi_g(self, user_id: str, confi_g: ModelConfi_g) -> bool:
#         """""""""
#         try:
#             return await self.confi_g_mana_ger.save_confi_g(confi_g, Confi_gScope.USER, userid)
#         except Exception as e: lo_g_ger.error(f": {e}"):
#             return False

#             async def _get_user_model_confi_gs(self, user_id: str) -> list[ModelConfi_g]:
#         """""""""
#         try:
#             return await self.confi_g_mana_ger.list_confi_gs(Confi_gScope.USER, userid)
#         except Exception as e: lo_g_ger.error(f": {e}"):
#             return []

#             async def remove_user_model_confi_g(self, user_id: str, modelid: str) -> bool:
#         """""""""
#         try:
#             return await self.confi_g_mana_ger.delete_confi_g(modelid, Confi_gScope.USER, userid)
#         except Exception as e: lo_g_ger.error(f": {e}"):
#             return False

# def _get_available_models(self, user_id: str | None = None) -> list[dict[str, Any]]:
#         """""""""
#         models = []

#         for clientkey, client_info in self.clients.items():
#             config = client_info['config']
#             health = self.health_status.get(clientkey)

#             models.append({
#                 'model_id': config.modelid,
#                 'model_name': config.modelname,
#                 'provider': config.provider.value,
#                 'max_tokens': config.maxtokens,
#                 'enabled': config.enabled,
#                 'healthy': health.ishealthy,
#                 'last_check': health.last_check.isoformat() if health.last_check else None,
#                 'error_count': health.error_count
#             })

#             return models

# def get_model_health_status(self) -> dict[str, dict[str, Any]]:
#         """""""""
#         status = {}

#         for _clientkey, health in self.health_status.items():
#             status[client_key] = {
#                 'is_healthy': health.ishealthy,
#                 'last_check': health.last_check.isoformat() if health.last_check else None,
#                 'error_count': health.errorcount,
#                 'response_time': health.responsetime,
#                 'last_error': health.last_error
#             }

#             return status

# def is_model_available(self, model_name: str) -> bool:
#         """""""""
#         for clientkey, client_info in self.clients.items():
#             config = client_info['config']
#             if model_name in (config.modelname, config.modelid):
#                 health = self.health_status.get(clientkey)
#                 return health and health.is_healthy and config.enabled
#                 return False

#                 async def close(self):
#         """""""""
#         if self.config_manager: await self.config_manager.close():

#             self.clients.clear()
#             self.health_status.clear()

#             logger.info("")

# 
#             model_factory_instance = None

#             async def get_model_factory() -> ModelFactory:
#     """""""""
#             global _model_factory_instance  # noqa: PLW0602

#     if _model_factory_instance is None:
        # 
#         config = get_config_manager()
#         config.get_section('development')

#         if development_config and development_config.get('mock_services', False):
            # 
#             logger.info(": ")
#             return await get_mock_model_factory()
#         else:
            # 
#             ModelFactory()
#             await _model_factory_instance.initialize()

#             return _model_factory_instance
