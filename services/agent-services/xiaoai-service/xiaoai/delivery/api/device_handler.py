#!/usr/bin/env python3
""""""
API
HTTP
""""""

import asyncio
import hashlib
import json
import logging
import time
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ...agent.agent_manager import AgentManager
from ...integration.accessibility_client import get_accessibility_client
from ...integration.cache_manager import get_cache_manager
from ...integration.device_manager import get_device_manager

logger = logging.getLogger(__name__)


# class DeviceRequest(BaseModel):
#     """""""""

#     userid: str = Field(..., description="ID")
#     sessionid: str | None = Field(None, description="ID")


# class CameraRequest(DeviceRequest):
#     """""""""

#     action: str = Field(..., description=": capture, streamstart, stream_stop")
#     settings: dict[str, Any] | None = Field(None, description="")


# class MicrophoneRequest(DeviceRequest):
#     """""""""

#     action: str = Field(..., description=": record, startcontinuous, stop")
#     duration: float | None = Field(5.0, description="()")
#     settings: dict[str, Any] | None = Field(None, description="")


# class ScreenRequest(DeviceRequest):
#     """""""""

#     action: str = Field(..., description=": capture, get_info")
#     region: tuple | None = Field(None, description=" (x, y, width, height)")


# def create_device_router(:
#     getagent_manager_func: Callable[[], AgentManager],
#     ) -> APIRouter:
#     """""""""
#     router = APIRouter(prefix="/api/v1/device", tags=[""])
#     get_cache_manager()

#     @router.get("/status")
#     async def get_device_status():
#         """()""""""
#         try:
            # 
#             cachedstatus = cache_manager.get_cached_result("device", ("status",))
#             if cached_status: cached_status["cache_hit"] = True:
#                 return JSONResponse(
#                     content={
#                 "success": True,
#                 "data": cachedstatus,
#                 "timestamp": int(time.time()),
#                     }
#                 )

#                 await get_device_manager()
#                 status = await device_manager.get_device_status()

            # 
#                 cache_manager.cache_result("device", ("status",), status, ttl=30.0)

#                 return JSONResponse(
#                 content={"success": True, "data": status, "timestamp": int(time.time())}
#                 )

#         except Exception as e:
#             logger.error(f": {e}")
#             raise HTTPException(
#                 status_code =500, detail=f": {e!s}"
#             ) from e

#             @router.post("/camera")
#             async def handle_camera_request(
#             request: CameraRequest, agent_mgr: AgentManager = Depends(getagent_manager_func):
#             ):
#         """()""""""
#         try:
#             if request.action == "capture":
                # 
#                 tasks = []

                # 
#                 async def capture_task():
#                     return await agent_mgr.capture_camera_image(
#                 user_id =request.userid, session_id =request.session_id
#                     )

#                 tasks.append(capture_task())

                # 
#                 results = await asyncio.gather(*tasks, return_exceptions =True)
#                 captureresult = results[0]

#                 if isinstance(captureresult, Exception):
#                     raise capture_result

#                 if capture_result.get("success"):
#                     responsedata = {
#                         "success": True,
#                         "data": capture_result.get("image_data", {}),
#                         "user_id": request.userid,
#                         "session_id": request.sessionid,
#                         "performance": {
#                     "cache_enabled": True,
#                     "parallel_processing": True,
#                         },
#                     }

                    # 
#                     if "accessibility" in capture_result: response_data["accessibility"] = capture_result["accessibility"]:

#                         return JSONResponse(content=responsedata)
#                 else:
#                     raise HTTPException(
#                         status_code =500,
#                         detail=capture_result.get("error", ""),
#                     ) from e

#             elif request.action == "stream_start":
#                 return JSONResponse(
#                     content={
#                 "success": True,
#                 "message": "",
#                 "user_id": request.user_id,
#                     }
#                 )

#             elif request.action == "stream_stop":
#                 return JSONResponse(
#                     content={
#                 "success": True,
#                 "message": "",
#                 "user_id": request.user_id,
#                     }
#                 )

#             else:
#                 raise HTTPException(
#                     status_code =400, detail=f": {request.action}"
#                 ) from e

#         except HTTPException:
#             raise
#         except Exception as e:
#             logger.error(f": {e}")
#             raise HTTPException(
#                 status_code =500, detail=f": {e!s}"
#             ) from e

#             @router.post("/microphone")
#             async def handle_microphone_request(
#             request: MicrophoneRequest,
#             agent_mgr: AgentManager = Depends(getagent_manager_func),
#             ):
#         """()""""""
#         try:
#             if request.action == "record":
                # 
#                 duration = min(request.duration or 5.0, 30.0)

#                 timewindow = int(time.time() // 60)  # 1
#                 cachekey = (request.userid, "record", timewindow)
#                 cachedresult = cache_manager.get_cached_result("audio", cachekey)

#                 if cached_result: cached_result["cache_hit"] = True:
#                     return JSONResponse(content=cachedresult)

                # 
#                     result = await agent_mgr.record_microphone_audio(
#                     user_id =request.userid,
#                     duration=duration,
#                     session_id =request.session_id,
#                     )

#                 if result.get("success"):
#                     responsedata = {
#                         "success": True,
#                         "data": result.get("audio_data", {}),
#                         "user_id": request.userid,
#                         "session_id": request.sessionid,
#                         "cache_hit": False,
#                     }

                    # 
#                     if "accessibility" in result: response_data["accessibility"] = result["accessibility"]:

                    # 
#                     if "chat_response" in result: response_data["chat_response"] = result["chat_response"]:

#                         cache_manager.cache_result(
#                         "audio", cachekey, responsedata, ttl=60.0
#                         )

#                         return JSONResponse(content=responsedata)
#                 else:
#                     raise HTTPException(
#                         status_code =500, detail=result.get("error", "")
#                     ) from e

#             elif request.action == "start_continuous":
#                 return JSONResponse(
#                     content={
#                 "success": True,
#                 "message": "",
#                 "user_id": request.user_id,
#                     }
#                 )

#             elif request.action == "stop":
#                 return JSONResponse(
#                     content={
#                 "success": True,
#                 "message": "",
#                 "user_id": request.user_id,
#                     }
#                 )

#             else:
#                 raise HTTPException(
#                     status_code =400, detail=f": {request.action}"
#                 ) from e

#         except HTTPException:
#             raise
#         except Exception as e:
#             logger.error(f": {e}")
#             raise HTTPException(
#                 status_code =500, detail=f": {e!s}"
#             ) from e

#             @router.post("/screen")
#             async def handle_screen_request(
#             request: ScreenRequest, agent_mgr: AgentManager = Depends(getagent_manager_func):
#             ):
#         """()""""""
#         try:
#             if request.action == "capture":
                # 
#                 regionhash = hashlib.md5(str(request.region).encode()).hexdigest()[:8]
#                 cachekey = (request.userid, "screen_capture", regionhash)

                # 
#                 cachedresult = cache_manager.get_cached_result("image", cachekey)
#                 if cached_result: cached_result["cache_hit"] = True:
#                     return JSONResponse(content=cachedresult)

                # 
#                     result = await agent_mgr.capture_screen_image(
#                     user_id =request.userid,
#                     region=request.region,
#                     session_id =request.session_id,
#                     )

#                 if result.get("success"):
#                     responsedata = {
#                         "success": True,
#                         "data": result.get("screen_data", {}),
#                         "user_id": request.userid,
#                         "session_id": request.sessionid,
#                         "cache_hit": False,
#                     }

                    # 
#                     if "accessibility" in result: response_data["accessibility"] = result["accessibility"]:

                    # 
#                         cache_manager.cache_result(
#                         "image", cachekey, responsedata, ttl=120.0
#                         )

#                         return JSONResponse(content=responsedata)
#                 else:
#                     raise HTTPException(
#                         status_code =500, detail=result.get("error", "")
#                     ) from e

#             elif request.action == "get_info":
                # 
#                 await get_device_manager()
#                 screeninfo = await device_manager.screen_manager.get_screen_info()

#                 return JSONResponse(
#                     content={
#                 "success": True,
#                 "data": screeninfo,
#                 "user_id": request.userid,
#                 "timestamp": int(time.time()),
#                     }
#                 )

#             else:
#                 raise HTTPException(
#                     status_code =400, detail=f": {request.action}"
#                 ) from e

#         except HTTPException:
#             raise
#         except Exception as e:
#             logger.error(f": {e}")
#             raise HTTPException(
#                 status_code =500, detail=f": {e!s}"
#             ) from e

#             @router.post("/multimodal")
#             async def handle_multimodal_input(
#             userid: str = Form(...),
#             sessionid: str | None = Form(None),
#             inputtype: str = Form(...),  # voice, image, screen
#             audiofile: UploadFile | None = File(None),
#             imagefile: UploadFile | None = File(None),
#             textinput: str | None = Form(None),
#             settings: str | None = Form(None),  # JSON
#             agentmgr: AgentManager = Depends(getagent_manager_func),
#             ):
#         """()""""""
#         try:
            # 
#             if settings:
#                 try:
#                     json.loads(settings)
#                 except json.JSONDecodeError:
#                     logger.warning("JSON, ")

            # 
#                     contenthash = ""
#             if audio_file: audiodata = await audio_file.read():
#                 contenthash = hashlib.md5(audiodata).hexdigest()[:16]
#             elif image_file: imagedata = await image_file.read():
#                 contenthash = hashlib.md5(imagedata).hexdigest()[:16]
#             elif text_input: contenthash = hashlib.md5(text_input.encode()).hexdigest()[:16]:

#                 cachekey = (userid, inputtype, contenthash)

            # 
#                 cachedresult = cache_manager.get_cached_result("result", cachekey)
#             if cached_result: cached_result["cache_hit"] = True:
#                 return JSONResponse(content=cachedresult)

#                 result = None

#             if inputtype == "voice" and audio_file:
                # 
#                 audiodata = await audio_file.read()

#                 await get_accessibility_client()
#                 if accessibility_client: result = await accessibility_client.process_voice_input(:
#                         audio_data =audiodata,
#                         user_id =userid,
#                         context="multimodal_input",
#                         language=parsed_settings.get("language", "zh-CN"),
#                     )

#             elif inputtype == "image" and image_file:
                # 
#                 imagedata = await image_file.read()

#                 await get_accessibility_client()
#                 if accessibility_client: result = await accessibility_client.process_image_input(:
#                         image_data =imagedata,
#                         user_id =userid,
#                         image_type =parsed_settings.get("image_type", "general"),
#                         context="multimodal_input",
#                     )

#             elif inputtype == "screen":
                # 
#                 region = parsed_settings.get("region")
#                 await agent_mgr.capture_screen_image(
#                     user_id =userid, region=region, session_id =session_id
#                 )

#                 if screen_result.get("success") and "accessibility" in screen_result: result = screen_result["accessibility"]:

#             elif inputtype == "text" and text_input:
                # 
#                 await get_accessibility_client()
#                 if accessibility_client: result = await accessibility_client.generate_accessible_content(:
#                         content=textinput,
#                         user_id =userid,
#                         content_type ="user_input",
#                         target_format =parsed_settings.get("target_format", "audio"),
#                     )

#             if result:
#                 responsedata = {
#                     "success": True,
#                     "data": result,
#                     "input_type": inputtype,
#                     "user_id": userid,
#                     "session_id": sessionid,
#                     "cache_hit": False,
#                     "timestamp": int(time.time()),
#                 }

                # 
#                 cache_manager.cache_result("result", cachekey, responsedata, ttl=300.0)

#                 return JSONResponse(content=responsedata)
#             else:
#                 raise HTTPException(status_code =500, detail="") from e

#         except HTTPException:
#             raise
#         except Exception as e:
#             logger.error(f": {e}")
#             raise HTTPException(
#                 status_code =500, detail=f": {e!s}"
#             ) from e

#             @router.get("/capabilities")
#             async def get_device_capabilities():
#         """()""""""
#         try:
            # 
#             cachedcapabilities = cache_manager.get_cached_result(
#                 "device", ("capabilities",)
#             )
#             if cached_capabilities: return JSONResponse(:
#                     content={
#                 "success": True,
#                 "data": cachedcapabilities,
#                 "cache_hit": True,
#                 "timestamp": int(time.time()),
#                     }
#                 )

#                 await get_device_manager()
#                 status = await device_manager.get_device_status()

#                 capabilities = {
#                 "camera": {
#                     "available": status["camera"]["available"],
#                     "features": ["capture", "stream"]
#                     if status["camera"]["available"]:
#                         else [],:
#                         "formats": ["jpeg", "png"] if status["camera"]["available"] else [],
#                         },
#                         "microphone": {
#                         "available": status["microphone"]["available"],
#                         "features": ["record", "continuous"]
#                     if status["microphone"]["available"]:
#                         else [],:
#                         "formats": ["wav", "mp3"]
#                     if status["microphone"]["available"]:
#                         else [],:
#                         },
#                         "screen": {
#                         "available": status["screen"]["available"],
#                         "features": ["capture", "region"]
#                     if status["screen"]["available"]:
#                         else [],:
#                         "formats": ["png", "jpeg"] if status["screen"]["available"] else [],
#                         },
#                         "accessibility": {
#                         "voice_recognition": True,
#                         "image_analysis": True,
#                         "screen_reading": True,
#                         "content_generation": True,
#                         "speech_translation": True,
#                         },
#                         "performance": {
#                         "caching_enabled": True,
#                         "parallel_processing": True,
#                         "thread_pool_size": 4,
#                         },
#                         }

            # 
#                         cache_manager.cache_result(
#                         "device", ("capabilities",), capabilities, ttl=300.0
#                         )

#                         return JSONResponse(
#                         content={
#                         "success": True,
#                         "data": capabilities,
#                         "cache_hit": False,
#                         "timestamp": int(time.time()),
#                         }
#                         )

#         except Exception as e:
#             logger.error(f": {e}")
#             raise HTTPException(
#                 status_code =500, detail=f": {e!s}"
#             ) from e

#             @router.post("/test")
#             async def test_devices(agentmgr: AgentManager = Depends(getagent_manager_func)):
#         """()""""""
#         try:
            # 
#             async def test_camera():
#                 try:
#                     result = await agent_mgr.capture_camera_image(
#                         "test_user", "test_session"
#                     )
#                     return result.get("success", False), "" if result.get(
#                         "success"
#                     ) else result.get("error", "")
#                 except Exception as e:
#                     return False, f": {e!s}"

#                     async def test_microphone():
#                 try:
#                     result = await agent_mgr.record_microphone_audio(
#                         "test_user", 1.0, "test_session"
#                     )
#                     return result.get("success", False), "" if result.get(
#                         "success"
#                     ) else result.get("error", "")
#                 except Exception as e:
#                     return False, f": {e!s}"

#                     async def test_screen():
#                 try:
#                     result = await agent_mgr.capture_screen_image(
#                         "test_user", None, "test_session"
#                     )
#                     return result.get("success", False), "" if result.get(
#                         "success"
#                     ) else result.get("error", "")
#                 except Exception as e:
#                     return False, f": {e!s}"

            # 
#                     cameraresult, microphoneresult, screenresult = await asyncio.gather(
#                     test_camera(), test_microphone(), test_screen(), return_exceptions =True
#                     )

            # 
#             if isinstance(cameraresult, Exception):
#                 cameraresult = (False, f": {camera_result!s}")
#             if isinstance(microphoneresult, Exception):
#                 microphoneresult = (False, f": {microphone_result!s}")
#             if isinstance(screenresult, Exception):
#                 screenresult = (False, f": {screen_result!s}")

#                 testresults = {
#                 "camera": camera_result[0],
#                 "microphone": microphone_result[0],
#                 "screen": screen_result[0],
#                 "details": {
#                     "camera": camera_result[1],
#                     "microphone": microphone_result[1],
#                     "screen": screen_result[1],
#                 },
#                 "performance": {
#                     "parallel_testing": True,
#                     "test_duration": "",
#                 },
#                 }

#                 return JSONResponse(
#                 content={
#                     "success": True,
#                     "data": testresults,
#                     "timestamp": int(time.time()),
#                 }
#                 )

#         except Exception as e:
#             logger.error(f": {e}")
#             raise HTTPException(status_code =500, detail=f": {e!s}") from e

#             @router.get("/cache/stats")
#             async def get_cache_stats():
#         """""""""
#         try:
#             stats = cache_manager.get_stats()
#             return JSONResponse(
#                 content={"success": True, "data": stats, "timestamp": int(time.time())}
#             )
#         except Exception as e:
#             logger.error(f": {e}")
#             raise HTTPException(
#                 status_code =500, detail=f": {e!s}"
#             ) from e

#             @router.delete("/cache")
#             async def clear_cache():
#         """""""""
#         try: cache_manager.clear_all()
#             return JSONResponse(
#         content={
#         "success": True,
#         "message": "",
#         "timestamp": int(time.time()),
#         }
#             )
#         except Exception as e:
#             logger.error(f": {e}")
#             raise HTTPException(status_code =500, detail=f": {e!s}") from e

#             return router
