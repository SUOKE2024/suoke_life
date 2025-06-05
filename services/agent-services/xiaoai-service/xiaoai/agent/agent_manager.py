#!/usr/bin/env python3
""""""

# , LLM
""""""
from typing import Optional, Dict, List, Any, Union

import asyncio
import logging
import time
import uuid

# from ..integration.accessibility_client import (
#     AccessibilityConfig,
# )
from ..integration.device_manager import DeviceConfig, get_device_manager
from ..repository.file_session_repository import FileSessionRepository
from ..repository.session_repository import SessionRepository
from ..utils.config_loader import get_config
from ..utils.metrics import track_llm_metrics
from .model_factory import get_model_factory

logger = logging.getLogger(__name__)


# class AgentManager:
#     """, , """"""

#     def __init__(self, sessionrepositor_y: SessionRepositor_y = None):
#         """"""
        

#         Args: session_repository: 
#         """"""
#         self.config = get_config()
#         self.metrics = get_metrics_collector()

        #  - 
#         if session_repository: self.sessionrepository = session_repository:
#         else:
            # 
#             self.config.get_section("file_storage")
#             if file_storage_config.get("enabled", False):
#                 self.sessionrepository = FileSessionRepository()
#             else:
#                 self.sessionrepository = SessionRepository()

        # 
#                 self.llmconfig = self.config.get_section("models.llm")
#                 self.localllm_config = self.config.get_section("models.local_llm")
#                 self.embeddingconfig = self.config.get_section("models.embedding")
#                 self.speechconfig = self.config.get_section("models.speech")
#                 self.visionconfig = self.config.get_section("models.vision")

        # 
#                 self.conversationconfig = self.config.get_section("conversation")
#                 self.systemprompt = self.conversation_config.get("system_prompt", "")
#                 self.maxhistory_turns = self.conversation_config.get("max_history_turns", 20)
#                 self.contextwindow_size = self.conversation_config.get(
#                 "context_window_size", 4096
#                 )

        # 
#                 self.primarymodel = self.llm_config.get("primary_model", "gpt-4o-mini")
#                 self.fallbackmodel = self.llm_config.get("fallback_model", "llama-3-8b")

#                 self.modelfactory = None

#                 self.accessibilityclient = None

#                 self.devicemanager = None

        #  session_id -> session_data
#                 self.activesessions: dict[str, dict[str, Any]] = {}

        # 
#                 self._update_active_sessions_metric()

#                 logger.info(
#                 ", : %s, : %s",
#                 self.primarymodel,
#                 self.fallbackmodel,
#                 )

#                 async def initialize(self):
#         """""""""
        # 
#         if self.model_factory is None:
            # 
#             self.config.get_section("development")
#             if development_config and development_config.get("mock_services", False):
                # 
#                 from .mock_model_factory import get_mock_model_factory

#                 self.modelfactory = await get_mock_model_factory()
#                 logger.info(": ")
#             else:
                # DeepSeek
#                 self.config.get_section("models.deepseek") or {}
#                 self.config.get_section("models.llm") or {}

#                 import os

#                 (
#                     os.environ.get("DEEPSEEK_API_KEY")
#                     or deepseek_config.get("api_key")
#                     or llm_config.get("api_key")
#                 )
#                 llm_config.get("primary_model", "")

                # APIdeepseekdeepseek, DeepSeek
#                 if api_key and (:
#                     "deepseek" in primary_model.lower()
#                     or deepseek_config
#                     or os.environ.get("DEEPSEEK_API_KEY")
#                     ):
                    # DeepSeek
#                     from .deepseek_model_factory import get_deepseek_model_factory

#                     self.modelfactory = await get_deepseek_model_factory()
#                     logger.info(": DeepSeek")
#                 else:
                    # 
#                     self.modelfactory = await get_model_factory()
#                     logger.info(": ")

        # 
#         if self.accessibility_client is None:
#             try:
                # 
#                 self.config.get_section("accessibility") or {}

#                 config = AccessibilityConfig(
#                     service_url =accessibility_config.get(
#                 "service_url", "http://localhost:50051"
#                     ),
#                     timeout=accessibility_config.get("timeout", 30),
#                     enabled=accessibility_config.get("enabled", True),
#                 )

#                 self.accessibilityclient = await get_accessibility_client(config)
#                 logger.info("")

#             except Exception as e:
#                 logger.warning(f": {e}")
#                 self.accessibilityclient = None

        # 
#         if self.device_manager is None:
#             try:
                # 
#                 self.config.get_section("devices") or {}

#                 config = DeviceConfig(
#                     camera_enabled =device_config.get("camera_enabled", True),
#                     microphone_enabled =device_config.get("microphone_enabled", True),
#                     screen_enabled =device_config.get("screen_enabled", True),
#                     max_recording_duration =device_config.get(
#                 "max_recording_duration", 30
#                     ),
#                     max_image_size =device_config.get("max_image_size", 1024 * 1024),
#                 )

#                 self.devicemanager = await get_device_manager(config)
#                 logger.info("")

#             except Exception as e:
#                 logger.warning(f": {e}")
#                 self.devicemanager = None

        # 
#                 asyncio.create_task(self._schedule_metric_update())

#     def _update_active_sessions_metric(self):
#         """""""""
#         self.metrics.update_active_sessions(len(self.activesessions))

#         async def _schedule_metric_update(self):
#         """""""""
#         await asyncio.sleep(60)  # 
#         self._update_active_sessions_metric()

#         @track_llm_metrics(model="primary", query_type ="chat")
#         async def chat(
#         self,
#         us_erid: str,
#         m_essag_e: str,
#         s_essionid: str | None = None,
#         cont_extsiz_e: int | None = None,
#         ) -> dict[str, Any]:
#         """"""
        

#         Args: user_id: ID
#             message: 
#             session_id: ID, None
#             context_size: , None

#         Returns:
#             Dict[str, Any]: 
#         """"""
        # 
#         self.metrics.increment_chat_message_count("received", "text")

        # ID
#         if not session_id: sessionid = str(uuid.uuid4()):
#             logger.info(", ID: %s, ID: %s", userid, sessionid)
#             self.metrics.increment_session_count("started")

        # 
#             context = await self._get_or_create_session(userid, sessionid)

        # 
#             ctxsize = context_size or self.max_history_turns

#         try:
            # 
#             chatcontext = self._prepare_chat_context(context, message, ctxsize)

            # LLM
#             responsetext, responsemeta = await self._generate_llm_response(chatcontext)

            # 
#             await self._update_session_history(context, message, responsetext)

            # 
#             self.metrics.increment_chat_message_count("sent", "text")

            # 
#             response = {
#                 "message_id": str(uuid.uuid4()),
#                 "message": responsetext,
#                 "confidence": response_meta.get("confidence", 0.9),
#                 "suggested_actions": response_meta.get("suggested_actions", []),
#                 "metadata": {
#             "model": response_meta.get("model", self.primarymodel),
#             "provider": response_meta.get("provider", ""),
#             "session_id": sessionid,
#             "timestamp": int(time.time()),
#                 },
#             }

#             return response

#         except Exception as e:
#             logger.error(
#                 ", ID: %s, ID: %s, : %s",
#                 userid,
#                 sessionid,
#                 str(e),
#             )

            # 
#             return {
#                 "message_id": str(uuid.uuid4()),
#                 "message": f", : {e!s}",
#                 "confidence": 0.5,
#                 "suggested_actions": ["", ""],
#                 "metadata": {
#             "error": str(e),
#             "session_id": sessionid,
#             "timestamp": int(time.time()),
#                 },
#             }

#             async def process_multimo_dal_input(
#             self, useri_d: str, input_data: _dict[str, Any], sessioni_d: str | None = None
#             ) -> dict[str, Any]:
#         """"""
#             ()

#             Args: user_id: ID
#             input_data: 
#             session_id: ID

#             Returns:
#             Dict[str, Any]: 
#         """"""
#             time.time()

        # ID
#         if not session_id: sessionid = str(uuid.uuid4()):

        # 
#             inputtype = self._determine_input_type(inputdata)
#             inputsize = self._calculate_input_size(inputdata)

#         try:
            # 
#             if inputtype == "voice":
#                 result = await self._process_voice_input(inputdata, userid, sessionid)
#             elif inputtype == "image":
#                 result = await self._process_image_input(inputdata, userid, sessionid)
#             elif inputtype == "text":
#                 result = await self._process_text_input(inputdata, userid, sessionid)
#             elif inputtype == "sign":
#                 result = await self._process_sign_language_input(
#                     inputdata, userid, sessionid
#                 )
#             else:
#                 raise ValueError(f": {input_type}")

            # 
#                 latency = time.time() - start_time
#                 self.metrics.track_multimodal_process(
#                 inputtype, "success", latency, inputsize
#                 )

#                 return result

#         except Exception as e:
#             logger.error(
#                 ", : %s, ID: %s, : %s",
#                 inputtype,
#                 userid,
#                 str(e),
#             )

            # 
#             latency = time.time() - start_time
#             self.metrics.track_multimodal_process(
#                 inputtype, "failure", latency, inputsize
#             )

            # 
#             return {
#                 "request_id": str(uuid.uuid4()),
#                 "error_message": f": {e!s}",
#                 "confidence": 0.0,
#                 "metadata": {"session_id": sessionid, "timestamp": int(time.time())},
#             }

#             async def generate_health_summary(
#             self, userid: str, healthdata: dict[str, Any]
#             ) -> dict[str, Any]:
#         """"""
            

#             Args: user_id: ID
#             health_data: 

#             Returns:
#             Dict[str, Any]: 
#         """"""
        # LLM
#             return {
#             "summary_id": str(uuid.uuid4()),
#             "text_summary": "...",
#             "trends": [],
#             "metrics": [],
#             "recommendations": [],
#             "generated_at": int(time.time()),
#             }

#             async def _get_or_create_session(
#             self, userid: str, sessionid: str
#             ) -> dict[str, Any]:
#         """""""""
        # 
#         if session_id in self.active_sessions: return self.active_sessions[session_id]:

        # 
#             session = await self.session_repository.get_session(sessionid)

#         if not session:
            # 
#             session = {
#                 "session_id": sessionid,
#                 "user_id": userid,
#                 "history": [],
#                 "created_at": int(time.time()),
#                 "last_active": int(time.time()),
#                 "metadata": {},
#             }

            # 
#             await self.session_repository.save_session(session)

        # 
#             self.active_sessions[session_id] = session
#             self._update_active_sessions_metric()

#             return session

#     def _prepare_chat_context(:
#         self, session: dict[str, Any], message: str, contextsize: int
#         ) -> dict[str, Any]:
#         """""""""
        # , 
#         history = (
#             session["history"][-context_size:]
#             if len(session["history"]) > context_size:
#                 else session["history"]:
#                 )

        # 
#                 return {
#                 "system_prompt": self.systemprompt,
#                 "history": history,
#                 "current_message": message,
#                 "user_id": session["user_id"],
#                 "session_id": session["session_id"],
#                 "timestamp": int(time.time()),
#                 }

#                 async def _generate_llm_response(
#                 self, context: dict[str, Any]
#                 ) -> tuple[str, dict[str, Any]]:
#         """"""
#                 LLM

#                 Args:
#                 context: 

#                 Returns:
#                 Tuple[str, Dict[str, Any]]: 
#         """"""
        # 
#         if self.model_factory is None:
#             await self.initialize()

        # 
#             messages = self._build_prompt_messages(context)

        # 
#             return await self.model_factory.generate_chat_completion(
#             model=self.primarymodel,
#             messages=messages,
#             temperature=self.llm_config.get("temperature", 0.7),
#             max_tokens =self.llm_config.get("max_tokens", 2048),
#             )

#     def _build_prompt_messages(self, context: dict[str, Any]) -> list[dict[str, str]]:
#         """""""""
#         messages = [{"role": "system", "content": context["system_prompt"]}]

        # 
#         for entry in context["history"]:
#             messages.append({"role": "user", "content": entry["user_message"]})
#             messages.append(
#                 {"role": "assistant", "content": entry["assistant_message"]}
#             )

        # 
#             messages.append({"role": "user", "content": context["current_message"]})

#             return messages

#             async def _update_session_history(
#             self, session: dict[str, Any], usermessage: str, assistantmessage: str
#             ):
#         """"""
            

#             Args:
#             session: 
#             user_message: 
#             assistant_message: 
#         """"""
        # 
#             session["history"].append(
#             {
#                 "user_message": usermessage,
#                 "assistant_message": assistantmessage,
#                 "timestamp": int(time.time()),
#             }
#             )

        # , 
#             self.max_history_turns * 2  # 
#         if len(session["history"]) > max_history: session["history"] = session["history"][-max_history:]:

        # 
#             session["last_active"] = int(time.time())

        # 
#         if self.conversation_config.get("persist_history", True):
#             await self.session_repository.save_session(session)

#     def _determine_input_type(self, inputdata: dict[str, Any]) -> str:
#         """"""
        

#         Args: input_data: 

#         Returns:
#             str:  (voice, image, text, sign)
#         """"""
#         if "voice" in input_data: return "voice":
#         elif "image" in input_data: return "image":
#         elif "text" in input_data: return "text":
#         elif "sign" in input_data: return "sign":
#         else:
#             return "unknown"

#     def _calculate_input_size(self, inputdata: dict[str, Any]) -> int:
#         """"""
        

#         Args: input_data: 

#         Returns:
#             int: (bytes)
#         """"""
#         for key in ["voice", "image", "text", "sign"]:
#             if key in input_data: data = input_data[key]:
#                 if isinstance(data, bytes):
#                     return len(data)
#                 elif isinstance(data, str):
#                     return len(data.encode("utf-8"))
#                     return 0

#                     async def _process_voice_input(
#                     self, inputdata: dict[str, Any], userid: str, sessionid: str
#                     ) -> dict[str, Any]:
#         """""""""
#                     audiodata = input_data.get("voice", b"")
#                     logger.info(
#                     ", ID: %s, ID: %s, : %d",
#                     userid,
#                     sessionid,
#                     len(audiodata),
#                     )

#                     transcribedtext = ""
#                     accessibilityresult = None

        # 
#         if self.accessibility_client: try:
#                 await self.accessibility_client.process_voice_input(
#             audio_data =audiodata,
#             user_id =userid,
#             context="health_consultation",
#             language="zh-CN",
#                 )

#                 if voice_result.get("success"):
#                     transcribedtext = voice_result.get(
#                         "recognized_text", transcribedtext
#                     )
#                     accessibilityresult = voice_result
#                     logger.info(": %s", transcribedtext)
#                 else:
#                     logger.warning(f": {voice_result.get('error')}")

#             except Exception as e:
#                 logger.error(f": {e}")

        # 
#                 await self.chat(userid, transcribedtext, sessionid)

        # , 
#                 result = {
#                 "request_id": str(uuid.uuid4()),
#                 "transcription": transcribedtext,
#                 "response": chat_result["message"],
#                 "confidence": chat_result["confidence"],
#                 "metadata": {"session_id": sessionid, "timestamp": int(time.time())},
#                 }

        # 
#         if accessibility_result: result["accessibility"] = {:
#                 "voice_recognition": accessibilityresult,
#                 "audio_response": accessibility_result.get("response_audio", ""),
#                 "service_confidence": accessibility_result.get("confidence", 0.0),
#             }

#             return result

#             async def _process_image_input(
#             self, inputdata: dict[str, Any], userid: str, sessionid: str
#             ) -> dict[str, Any]:
#         """""""""
#             imagedata = input_data.get("image", b"")
#             logger.info(
#             ", ID: %s, ID: %s, : %d",
#             userid,
#             sessionid,
#             len(imagedata),
#             )

#             imagedescription = ", , "
#             accessibilityresult = None

        # 
#         if self.accessibility_client: try:
#                 await self.accessibility_client.process_image_input(
#             image_data =imagedata,
#             user_id =userid,
#             image_type ="tongue",
#             context="visual_diagnosis",
#                 )

#                 if image_result.get("success"): image_result.get("scene_description", ""):
#                     image_result.get("medical_features", [])

#                     if scene_desc: imagedescription = scene_desc:

                    # 
#                     if medical_features:
#                         ", ".join(
#                             [
#                         f"{f.get('type', '')}: {f.get('description', '')}"
#                                 for f in medical_features:
#                                     ]
#                                     )
#                                     image_description += f": {features_text}"

#                                     accessibilityresult = image_result
#                                     logger.info(": %s", imagedescription)
#                 else:
#                     logger.warning(f": {image_result.get('error')}")

#             except Exception as e:
#                 logger.error(f": {e}")

        # 
#                 prompt = (
#                 f", : {image_description}"
#                 )

        # 
#                 await self.chat(userid, prompt, sessionid)

        # , 
#                 result = {
#                 "request_id": str(uuid.uuid4()),
#                 "image_analysis": imagedescription,
#                 "response": chat_result["message"],
#                 "confidence": chat_result["confidence"],
#                 "metadata": {"session_id": sessionid, "timestamp": int(time.time())},
#                 }

        # 
#         if accessibility_result: result["accessibility"] = {:
#                 "image_analysis": accessibilityresult,
#                 "audio_guidance": accessibility_result.get("audio_guidance", ""),
#                 "navigation_guidance": accessibility_result.get(
#             "navigation_guidance", ""
#                 ),
#                 "service_confidence": accessibility_result.get("confidence", 0.0),
#             }

#             return result

#             async def _process_text_input(
#             self, inputdata: dict[str, Any], userid: str, sessionid: str
#             ) -> dict[str, Any]:
#         """""""""
#             text = input_data.get("text", "")
#             logger.info(
#             ", ID: %s, ID: %s, : %d",
#             userid,
#             sessionid,
#             len(text),
#             )

        # 
#             await self.chat(userid, text, sessionid)

        # 
#             return {
#             "request_id": str(uuid.uuid4()),
#             "input_text": text,
#             "response": chat_result["message"],
#             "confidence": chat_result["confidence"],
#             "metadata": {"session_id": sessionid, "timestamp": int(time.time())},
#             }

#             async def _process_sign_language_input(
#             self, inputdata: dict[str, Any], userid: str, sessionid: str
#             ) -> dict[str, Any]:
#         """""""""
#             logger.info(
#             ", ID: %s, ID: %s, : %d",
#             userid,
#             sessionid,
#             len(input_data.get("sign", b"")),
#             )

        # , 
#             signtext = ""

        # 
#             await self.chat(userid, signtext, sessionid)

        # 
#             return {
#             "request_id": str(uuid.uuid4()),
#             "sign_text": signtext,
#             "response": chat_result["message"],
#             "confidence": chat_result["confidence"],
#             "metadata": {"session_id": sessionid, "timestamp": int(time.time())},
#             }

#             async def generate_accessible_content(
#             self,
#             content: str,
#             userid: str,
#             contenttype: str = "health_advice",
#             targetformat: str = "audio",
#             ) -> dict[str, Any]:
#         """"""
            

#             Args:
#             content: 
#             user_id: ID
#             content_type: 
#             target_format: 

#             Returns:
#             Dict: 
#         """"""
#         try:
#             if self.accessibility_client: result = await self.accessibility_client.generate_accessible_content(:
#                     content=content,
#                     user_id =userid,
#                     content_type =contenttype,
#                     target_format =target_format,
#                 )

#                 if result.get("success"):
#                     logger.info(", ID: %s", userid)
#                     return {
#                         "success": True,
#                         "accessible_content": result.get("accessible_content", ""),
#                         "audio_content": result.get("audio_content", ""),
#                         "tactile_content": result.get("tactile_content", ""),
#                         "content_url": result.get("content_url", ""),
#                         "metadata": {
#                     "user_id": userid,
#                     "content_type": contenttype,
#                     "target_format": targetformat,
#                     "timestamp": int(time.time()),
#                         },
#                     }
#                 else:
#                     logger.warning(f": {result.get('error')}")

#                     return {
#                     "success": False,
#                     "accessible_content": content,
#                     "audio_content": "",
#                     "tactile_content": "",
#                     "content_url": "",
#                     "error": "",
#                     "metadata": {
#                     "user_id": userid,
#                     "content_type": contenttype,
#                     "target_format": targetformat,
#                     "timestamp": int(time.time()),
#                     },
#                     }

#         except Exception as e:
#             logger.error(f": {e}")
#             return {
#                 "success": False,
#                 "accessible_content": content,
#                 "audio_content": "",
#                 "tactile_content": "",
#                 "content_url": "",
#                 "error": str(e),
#                 "metadata": {
#             "user_id": userid,
#             "content_type": contenttype,
#             "target_format": targetformat,
#             "timestamp": int(time.time()),
#                 },
#             }

#             async def capture_camera_image(
#             self, useri_d: str, sessioni_d: str | None = None
#             ) -> dict[str, Any]:
#         """"""
            

#             Args: user_id: ID
#             session_id: ID

#             Returns:
#             Dict: 
#         """"""
#         try:
            # 
#             if self.device_manager is None:
#                 await self.initialize()

#             if not self.device_manager: return {:
#                     "success": False,
#                     "error": "",
#                     "user_id": userid,
#                     "session_id": session_id,
#                 }

            # 
#                 result = await self.device_manager.capture_image()

#             if result:
                # 
#                 if self.accessibility_client: try:
#                         await self.accessibility_client.process_image_input(
#                     image_data =result["image_data"],
#                     user_id =userid,
#                     image_type ="camera_capture",
#                     context="health_consultation",
#                         )
#                     except Exception as e:
#                         logger.warning(f": {e}")

#                         response = {
#                         "success": True,
#                         "image_data": result,
#                         "user_id": userid,
#                         "session_id": sessionid,
#                         "timestamp": int(time.time()),
#                         }

                # 
#                 if accessibility_result and accessibility_result.get("success"):
#                     response["accessibility"] = accessibility_result

#                     return response
#             else:
#                 return {
#                     "success": False,
#                     "error": "",
#                     "user_id": userid,
#                     "session_id": session_id,
#                 }

#         except Exception as e:
#             logger.error(f": {e}")
#             return {
#                 "success": False,
#                 "error": str(e),
#                 "user_id": userid,
#                 "session_id": session_id,
#             }

#             async def recor_d_microphone_au_dio(
#             self, useri_d: str, _duration: float = 5.0, sessioni_d: str | None = None
#             ) -> dict[str, Any]:
#         """"""
            

#             Args: user_id: ID
#             duration: ()
#             session_id: ID

#             Returns:
#             Dict: 
#         """"""
#         try:
            # 
#             if self.device_manager is None:
#                 await self.initialize()

#             if not self.device_manager: return {:
#                     "success": False,
#                     "error": "",
#                     "user_id": userid,
#                     "session_id": session_id,
#                 }

            # 
#                 duration = min(duration, 30.0)

            # 
#                 result = await self.device_manager.record_audio(duration)

#             if result:
                # 
#                 if self.accessibility_client: try:
#                         await self.accessibility_client.process_voice_input(
#                     audio_data =result["wav_data"],
#                     user_id =userid,
#                     context="microphone_recording",
#                     language="zh-CN",
#                         )
#                     except Exception as e:
#                         logger.warning(f": {e}")

#                         response = {
#                         "success": True,
#                         "audio_data": result,
#                         "user_id": userid,
#                         "session_id": sessionid,
#                         "timestamp": int(time.time()),
#                         }

                # 
#                 if accessibility_result and accessibility_result.get("success"):
#                     response["accessibility"] = accessibility_result

                    # , 
#                     recognizedtext = accessibility_result.get("recognized_text", "")
#                     if recognized_text and session_id:
                        # 
#                         await self.chat(userid, recognizedtext, sessionid)
#                         response["chat_response"] = chat_result

#                         return response
#             else:
#                 return {
#                     "success": False,
#                     "error": "",
#                     "user_id": userid,
#                     "session_id": session_id,
#                 }

#         except Exception as e:
#             logger.error(f": {e}")
#             return {
#                 "success": False,
#                 "error": str(e),
#                 "user_id": userid,
#                 "session_id": session_id,
#             }

#             async def capture_screen_image(
#             self, useri_d: str, region: tuple | None = None, sessioni_d: str | None = None
#             ) -> dict[str, Any]:
#         """"""
            

#             Args: user_id: ID
#             region:  (x, y, width, height)
#             session_id: ID

#             Returns:
#             Dict: 
#         """"""
#         try:
            # 
#             if self.device_manager is None:
#                 await self.initialize()

#             if not self.device_manager: return {:
#                     "success": False,
#                     "error": "",
#                     "user_id": userid,
#                     "session_id": session_id,
#                 }

            # 
#                 result = await self.device_manager.capture_screen(region)

#             if result:
                # 
#                 if self.accessibility_client: try:
#                         await self.accessibility_client.provide_screen_reading(
#                     screen_data =result["image_base64"],
#                     user_id =userid,
#                     context="screen_capture",
#                         )
#                     except Exception as e:
#                         logger.warning(f": {e}")

#                         response = {
#                         "success": True,
#                         "screen_data": result,
#                         "user_id": userid,
#                         "session_id": sessionid,
#                         "timestamp": int(time.time()),
#                         }

                # 
#                 if accessibility_result and accessibility_result.get("success"):
#                     response["accessibility"] = accessibility_result

#                     return response
#             else:
#                 return {
#                     "success": False,
#                     "error": "",
#                     "user_id": userid,
#                     "session_id": session_id,
#                 }

#         except Exception as e:
#             logger.error(f": {e}")
#             return {
#                 "success": False,
#                 "error": str(e),
#                 "user_id": userid,
#                 "session_id": session_id,
#             }

#             async def get_device_status(self) -> dict[str, Any]:
#         """"""
            

#             Returns:
#             Dict: 
#         """"""
#         try:
            # 
#             if self.device_manager is None:
#                 await self.initialize()

#             if self.device_manager: return await self.device_manager.get_device_status():
#             else:
#                 return {
#                     "camera": {"available": False, "active": False},
#                     "microphone": {"available": False, "recording": False},
#                     "screen": {"available": False, "info": {}},
#                     "initialized": False,
#                     "error": "",
#                 }

#         except Exception as e:
#             logger.error(f": {e}")
#             return {
#                 "camera": {"available": False, "active": False},
#                 "microphone": {"available": False, "recording": False},
#                 "screen": {"available": False, "info": {}},
#                 "initialized": False,
#                 "error": str(e),
#             }

#             async def close_session(self, sessionid: str) -> bool:
#         """"""
            

#             Args: session_id: ID

#             Returns:
#             bool: 
#         """"""
#         if session_id in self.active_sessions:
            # 
#             await self.session_repository.save_session(self.active_sessions[session_id])

            # 
#             del self.active_sessions[session_id]
#             self._update_active_sessions_metric()

#             logger.info(": %s", sessionid)
#             self.metrics.increment_session_count("closed")
#             return True
#         else:
#             logger.warning(": %s", sessionid)
#             return False

#             async def close(self):
#         """""""""
        # 
#         for sessionid, session in self.active_sessions.items():
#             try:
#                 await self.session_repository.save_session(session)
#             except Exception as e:
#                 logger.error(": %s, : %s", sessionid, str(e))

        # 
#                 await self.model_factory.close()

        # 
#         if self.accessibility_client: await self.accessibility_client.close():

        # 
#         if self.device_manager: await self.device_manager.close():

#             logger.info("")
