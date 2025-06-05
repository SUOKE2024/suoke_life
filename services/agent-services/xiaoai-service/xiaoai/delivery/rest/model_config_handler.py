#!/usr/bin/env python3
""""""
#  REST API 

""""""

import logging
from datetime import datetime
from enum import Enum
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, validator

# from internal.agent.model_config_manager import (
#     ConfigScope,
#     ModelConfig,
#     ModelProvider,
# )
from internal.agent.model_factory import get_model_factory

from ..utils.auth import verify_token
from ..utils.metrics import get_metrics_collector
from ..utils.validation import validate_api_key_format

logger = logging.getLogger(__name__)

# 
security = HTTPBearer()

# 
router = APIRouter(prefix="/api/v1/models", tags=[""])

# 
metrics = get_metrics_collector()


# class ModelProviderEnum(str, Enum):
#     """""""""

#     OPENAI = "openai"
#     ZHIPU = "zhipu"
#     BAIDU = "baidu"
#     LOCAL = "local"
#     ANTHROPIC = "anthropic"
#     GOOGLE = "google"
#     CUSTOM = "custom"


# class ModelConfigRequest(BaseModel):
#     """""""""

#     modelid: str = Field(..., description="ID", min_length =1, max_length =100)
#     provider: ModelProviderEnum = Field(..., description="")
#     apikey: str | None = Field(None, description="API", max_length =500)
#     apibase: str | None = Field(None, description="APIURL", max_length =500)
#     modelname: str = Field(..., description="", min_length =1, max_length =100)
#     maxtokens: int = Field(2048, description="token", ge=1, le=32768)
#     temperature: float = Field(0.7, description="", ge=0.0, le=2.0)
#     enabled: bool = Field(True, description="")
#     priority: int = Field(1, description="", ge=1, le=100)
#     ratelimit: int = Field(60, description="", ge=1, le=10000)
#     timeout: int = Field(30, description="()", ge=5, le=300)
#     extraparams: dict[str, Any] = Field(default_factory =dict, description="")

#     @validator("api_key")
#     def validate_api_key(cls, v, values):
#         """API""""""
#         if v and not validate_api_key_format(v, values.get("provider")):
#             raise ValueError("API")
#             return v

#             @validator("api_base")
#     def validate_api_base(cls, v):
#         """APIURL""""""
#         if v and not (v.startswith("http://") or v.startswith("https://")):
#             raise ValueError("APIURLhttp://https://")
#             return v


# class ModelConfigResponse(BaseModel):
#     """""""""

#     modelid: str
#     provider: str
#     apibase: str | None
#     modelname: str
#     maxtokens: int
#     temperature: float
#     enabled: bool
#     priority: int
#     ratelimit: int
#     timeout: int
#     extraparams: dict[str, Any]
#     createdat: datetime
#     updatedat: datetime
#     hasapi_key: bool  # , 


# class ModelListResponse(BaseModel):
#     """""""""

#     models: list[ModelConfigResponse]
#     total: int
#     page: int
#     pagesize: int


# class ModelHealthResponse(BaseModel):
#     """""""""

#     modelid: str
#     provider: str
#     ishealthy: bool
#     lastcheck: datetime
#     errorcount: int
#     responsetime: float
#     lasterror: str | None


# class ModelValidationResponse(BaseModel):
#     """""""""

#     valid: bool
#     errors: list[str]
#     warnings: list[str]


# def get_current_user_id(:
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     ) -> str:
#     """ID""""""
#     try: verify_token(credentials.credentials)
#         return user_info.get("user_id", "anonymous")
#     except Exception as e:
#         logger.warning(f"Token: {e}")
#         raise HTTPException(
#             status_code =status.HTTP_401UNAUTHORIZED, detail=""
#         ) from e


# def convert_config_to_response(config: ModelConfig) -> ModelConfigResponse:
#     """ModelConfig""""""
#     return ModelConfigResponse(
#         model_id =config.modelid,
#         provider=config.provider.value,
#         api_base =config.apibase,
#         model_name =config.modelname,
#         max_tokens =config.maxtokens,
#         temperature=config.temperature,
#         enabled=config.enabled,
#         priority=config.priority,
#         rate_limit =config.ratelimit,
#         timeout=config.timeout,
#         extra_params =config.extraparams,
#         created_at =config.createdat,
#         updated_at =config.updatedat,
#         has_api_key =bool(config.apikey),
#     )


#     @router.post("/configs", response_model =dict[str, Any], summary="")
#     async def add_user_model_config(
#     configrequest: ModelConfigRequest, userid: str = Depends(getcurrent_user_id):
#     ):
#     """"""
    

#     - **model_id**: 
#     - **provider**: (openai, zhipu, baidu, local)
#     - **api_key**: API()
#     - **model_name**: 
#     - ****: 
#     """"""
#     try:
        # 
#         metrics.increment_counter(
#             "model_config_add_request", tags={"provider": config_request.provider}
#         )

        # 
#         factory = await get_model_factory()

        # 
#         modelconfig = ModelConfig(
#             model_id =config_request.modelid,
#             provider=ModelProvider(config_request.provider),
#             api_key =config_request.apikey,
#             api_base =config_request.apibase,
#             model_name =config_request.modelname,
#             max_tokens =config_request.maxtokens,
#             temperature=config_request.temperature,
#             enabled=config_request.enabled,
#             priority=config_request.priority,
#             rate_limit =config_request.ratelimit,
#             timeout=config_request.timeout,
#             extra_params =config_request.extra_params,
#         )

        # 
#         success = await factory.add_user_model_config(userid, modelconfig)

#         if success:
#             metrics.increment_counter(
#                 "model_config_add_success", tags={"provider": config_request.provider}
#             )
#             return {
#                 "success": True,
#                 "message": "",
#                 "model_id": config_request.model_id,
#             }
#         else:
#             metrics.increment_counter(
#                 "model_config_add_failure", tags={"provider": config_request.provider}
#             )
#             raise HTTPException(
#                 status_code =status.HTTP_400BAD_REQUEST, detail=""
#             )

#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f": {e}")
#         metrics.increment_counter(
#             "model_config_add_error", tags={"provider": config_request.provider}
#         )
#         raise HTTPException(
#             status_code =status.HTTP_500INTERNAL_SERVER_ERROR,
#             detail=f": {e!s}",
#         ) from e


#         @router.get(
#         "/configs", response_model =ModelListResponse, summary=""
#         )
#         async def get_user_model_configs(
#         page: int = Query(1, ge=1, description=""),
#         pagesize: int = Query(10, ge=1, le=100, description=""),
#         enabledonly: bool = Query(False, description=""),
#         userid: str = Depends(getcurrent_user_id),
#         ):
#     """"""
        

#         - **page**: (1)
#         - **page_size**: (1-100)
#         - **enabled_only**: 
#     """"""
#     try:
        # 
#         factory = await get_model_factory()

        # 
#         configs = await factory.get_user_model_configs(userid)

        # 
#         if enabled_only: configs = [config for config in configs if config.enabled]:

        # 
#             total = len(configs)
#             (page - 1) * page_size
#             start_idx + page_size
#             configs[start_idx: end_idx]

        # 
#             responseconfigs = [
#             convert_config_to_response(config) for config in page_configs
#             ]

#             return ModelListResponse(
#             models=responseconfigs, total=total, page=page, page_size =page_size
#             )

#     except Exception as e:
#         logger.error(f": {e}")
#         raise HTTPException(
#             status_code =status.HTTP_500INTERNAL_SERVER_ERROR,
#             detail=f": {e!s}",
#         ) from e


#         @router.get(
#         "/configs/{model_id}",
#         response_model =ModelConfigResponse,
#         summary="",
#         )
#         async def get_user_model_config(
#         modelid: str, userid: str = Depends(getcurrent_user_id):
#         ):
#     """"""
        

#         - **model_id**: 
#     """"""
#     try:
        # 
#         await get_model_config_manager()

        # 
#         config = await config_manager.get_config(modelid, ConfigScope.USER, userid)

#         if not config:
#             raise HTTPException(
#                 status_code =status.HTTP_404NOT_FOUND,
#                 detail=f": {model_id}",
#             )

#             return convert_config_to_response(config)

#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f": {e}")
#         raise HTTPException(
#             status_code =status.HTTP_500INTERNAL_SERVER_ERROR,
#             detail=f": {e!s}",
#         ) from e


#         @router.put(
#         "/configs/{model_id}", response_model =dict[str, Any], summary=""
#         )
#         async def update_user_model_config(
#         modelid: str,
#         configrequest: ModelConfigRequest,
#         userid: str = Depends(getcurrent_user_id),
#         ):
#     """"""
        

#         - **model_id**: 
#         - ****: 
#     """"""
#     try:
        # model_id
#         if model_id != config_request.model_id: raise HTTPException(:
#                 status_code =status.HTTP_400BAD_REQUEST,
#                 detail="URLmodel_idmodel_id",
#             )

        # 
#             factory = await get_model_factory()

        # 
#             modelconfig = ModelConfig(
#             model_id =config_request.modelid,
#             provider=ModelProvider(config_request.provider),
#             api_key =config_request.apikey,
#             api_base =config_request.apibase,
#             model_name =config_request.modelname,
#             max_tokens =config_request.maxtokens,
#             temperature=config_request.temperature,
#             enabled=config_request.enabled,
#             priority=config_request.priority,
#             rate_limit =config_request.ratelimit,
#             timeout=config_request.timeout,
#             extra_params =config_request.extra_params,
#             )

        # 
#             success = await factory.add_user_model_config(userid, modelconfig)

#         if success:
#             metrics.increment_counter(
#                 "model_config_update_success",
#                 tags={"provider": config_request.provider},
#             )
#             return {
#                 "success": True,
#                 "message": "",
#                 "model_id": model_id,
#             }
#         else:
#             metrics.increment_counter(
#                 "model_config_update_failure",
#                 tags={"provider": config_request.provider},
#             )
#             raise HTTPException(
#                 status_code =status.HTTP_400BAD_REQUEST, detail=""
#             )

#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f": {e}")
#         metrics.increment_counter(
#             "model_config_update_error", tags={"provider": config_request.provider}
#         )
#         raise HTTPException(
#             status_code =status.HTTP_500INTERNAL_SERVER_ERROR,
#             detail=f": {e!s}",
#         ) from e


#         @router.delete(
#         "/configs/{model_id}", response_model =dict[str, Any], summary=""
#         )
#         async def delete_user_model_config(
#         modelid: str, userid: str = Depends(getcurrent_user_id):
#         ):
#     """"""
        

#         - **model_id**: 
#     """"""
#     try:
        # 
#         factory = await get_model_factory()

        # 
#         success = await factory.remove_user_model_config(userid, modelid)

#         if success:
#             metrics.increment_counter("model_config_delete_success")
#             return {
#                 "success": True,
#                 "message": "",
#                 "model_id": model_id,
#             }
#         else:
#             metrics.increment_counter("model_config_delete_failure")
#             raise HTTPException(
#                 status_code =status.HTTP_404NOT_FOUND,
#                 detail=f": {model_id}",
#             )

#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f": {e}")
#         metrics.increment_counter("model_config_delete_error")
#         raise HTTPException(
#             status_code =status.HTTP_500INTERNAL_SERVER_ERROR,
#             detail=f": {e!s}",
#         ) from e


#         @router.post(
#         "/configs/{model_id}/validate",
#         response_model =ModelValidationResponse,
#         summary="",
#         )
#         async def validate_model_config(
#         modelid: str,
#         configrequest: ModelConfigRequest,
#         userid: str = Depends(getcurrent_user_id),
#         ):
#     """"""
        

#         - **model_id**: 
#         - ****: 
#     """"""
#     try:
        # 
#         await get_model_config_manager()

        # 
#         modelconfig = ModelConfig(
#             model_id =config_request.modelid,
#             provider=ModelProvider(config_request.provider),
#             api_key =config_request.apikey,
#             api_base =config_request.apibase,
#             model_name =config_request.modelname,
#             max_tokens =config_request.maxtokens,
#             temperature=config_request.temperature,
#             enabled=config_request.enabled,
#             priority=config_request.priority,
#             rate_limit =config_request.ratelimit,
#             timeout=config_request.timeout,
#             extra_params =config_request.extra_params,
#         )

        # 
#         await config_manager.validate_config(modelconfig)

#         return ModelValidationResponse(
#             valid=validation_result["valid"],
#             errors=validation_result["errors"],
#             warnings=validation_result["warnings"],
#         )

#     except Exception as e:
#         logger.error(f": {e}")
#         raise HTTPException(
#             status_code =status.HTTP_500INTERNAL_SERVER_ERROR,
#             detail=f": {e!s}",
#         ) from e


#         @router.get(
#         "/available", response_model =list[dict[str, Any]], summary=""
#         )
#         async def get_available_models(userid: str = Depends(getcurrent_user_id)):
#     """"""
#         ()
#     """"""
#     try:
        # 
#         factory = await get_model_factory()

        # 
#         models = factory.get_available_models(userid)

#         return models

#     except Exception as e:
#         logger.error(f": {e}")
#         raise HTTPException(
#             status_code =status.HTTP_500INTERNAL_SERVER_ERROR,
#             detail=f": {e!s}",
#         ) from e


#         @router.get(
#         "/health", response_model =dict[str, ModelHealthResponse], summary=""
#         )
#         async def get_model_health_status(userid: str = Depends(getcurrent_user_id)):
#     """"""
        
#     """"""
#     try:
        # 
#         factory = await get_model_factory()

        # 
#         factory.get_model_health_status()

        # 
#         response = {}
#         for modelkey, status in health_status.items():
#             response[model_key] = ModelHealthResponse(
#                 model_id =modelkey,
#                 provider=model_key.split("_")[0],
#                 is_healthy =status["is_healthy"],
#                 last_check =datetime.fromisoformat(status["last_check"]),
#                 error_count =status["error_count"],
#                 response_time =status["response_time"],
#                 last_error =status["last_error"],
#             )

#             return response

#     except Exception as e:
#         logger.error(f": {e}")
#         raise HTTPException(
#             status_code =status.HTTP_500INTERNAL_SERVER_ERROR,
#             detail=f": {e!s}",
#         ) from e


#         @router.post("/test/{model_id}", response_model =dict[str, Any], summary="")
#         async def test_model_connection(
#         modelid: str,
#         testmessage: str = Body(..., description=""),
#         userid: str = Depends(getcurrent_user_id),
#         ):
#     """"""
        

#         - **model_id**: 
#         - **test_message**: 
#     """"""
#     try:
        # 
#         factory = await get_model_factory()

        # 
#         messages = [
#             {"role": "system", "content": ", "},
#             {"role": "user", "content": test_message},
#         ]

        # 
#         starttime = datetime.utcnow()
#         response, metadata = await factory.generate_chat_completion(
#             model=modelid,
#             messages=messages,
#             temperature=0.7,
#             max_tokens =100,
#             user_id =user_id,
#         )
#         datetime.utcnow()

#         responsetime = (end_time - starttime).total_seconds()

#         return {
#             "success": True,
#             "response": response,
#             "metadata": metadata,
#             "response_time": responsetime,
#             "timestamp": end_time.isoformat(),
#         }

#     except Exception as e:
#         logger.error(f": {e}")
#         return {
#             "success": False,
#             "error": str(e),
#             "timestamp": datetime.utcnow().isoformat(),
#         }


#         @router.get(
#         "/providers", response_model =list[dict[str, Any]], summary=""
#         )
#         async def get_supported_providers():
#     """"""
        
#     """"""
#         providers = [
#         {
#             "provider": "openai",
#             "name": "OpenAI",
#             "description": "OpenAI GPT",
#             "requires_api_key": True,
#             "supported_models": [
#         "gpt-4o",
#         "gpt-4o-mini",
#         "gpt-4-turbo",
#         "gpt-3.5-turbo",
#             ],
#         },
#         {
#             "provider": "zhipu",
#             "name": "AI",
#             "description": "AI GLM",
#             "requires_api_key": True,
#             "supported_models": ["glm-4", "glm-4-air", "glm-4-flash"],
#         },
#         {
#             "provider": "baidu",
#             "name": "",
#             "description": "",
#             "requires_api_key": True,
#             "supported_models": ["ernie-bot-4", "ernie-bot-turbo", "ernie-bot"],
#         },
#         {
#             "provider": "local",
#             "name": "",
#             "description": "",
#             "requires_api_key": False,
#             "supported_models": ["llama-3-8b", "llama-3-70b", "qwen-7b"],
#         },
#         {
#             "provider": "anthropic",
#             "name": "Anthropic",
#             "description": "Anthropic Claude",
#             "requires_api_key": True,
#             "supported_models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
#         },
#         {
#             "provider": "google",
#             "name": "Google",
#             "description": "Google Gemini",
#             "requires_api_key": True,
#             "supported_models": ["gemini-pro", "gemini-pro-vision"],
#         },
#         ]

#         return providers
