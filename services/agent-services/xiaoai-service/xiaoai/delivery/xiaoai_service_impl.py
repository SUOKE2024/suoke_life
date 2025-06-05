#!/usr/bin/env python3
""""""
gRPC
xiaoai_service.proto
""""""

import logging
import time
import uuid

from ..agent.agent_manager import AgentManager
from ..orchestrator.diagnosis_coordinator import DiagnosisCoordinator
from ..repository.diagnosis_repository import DiagnosisRepository
from ..repository.session_repository import SessionRepository
from ..utils.config_loader import get_config
from ..utils.metrics import get_metrics_collector

# gRPC
# try:
#     import os
#     import sys

    #  api 
#     sys.path.insert(
#         0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
#     )
# except ImportError:
#     logging.error("gRPC, protobuf")
#     raise

#     logger = logging.getLogger(__name__)


# class XiaoAIServiceImpl(xiaoai_pb2_grpc.XiaoAIServiceServicer):
#     """gRPC""""""

#     def __init__(self):
#         """""""""
#         self.config = get_config()
#         self.metrics = get_metrics_collector()

        # 
#         self.sessionrepository = SessionRepository()
#         self.diagnosisrepository = DiagnosisRepository()
#         self.agentmanager = AgentManager(self.sessionrepository)
#         self.diagnosiscoordinator = DiagnosisCoordinator(
#             self.agentmanager, self.diagnosis_repository
#         )

#         logger.info("gRPC")

#         async def ChatStream(self, request, context):
#         """"""
        

#         Args:
#             request: ChatRequest
#             context: gRPC

#         Yields:
#             ChatResponse: 
#         """"""
#         time.time()

        # 
#         self.metrics.increment_active_requests("ChatStream")

#         try:
            # 
#             userid = request.user_id
#             message = request.message
#             sessionid = request.session_id if request.session_id else str(uuid.uuid4())

            # 
#             await self.agent_manager.chat(userid, message, sessionid, context_size)

            # 
#             response = xiaoai_pb2.ChatResponse(
#                 message_id =chat_response.get("message_id", str(uuid.uuid4())),
#                 message=chat_response.get("message", ""),
#                 confidence=chat_response.get("confidence", 0.0),
#                 timestamp=int(time.time()),
#             )

            # 
#             for action in chat_response.get("suggested_actions", []):
#                 response.suggested_actions.append(action)

            # 
#             for key, value in chat_response.get("metadata", {}).items():
#                 response.metadata[key] = str(value)

            # 
#                 latency = time.time() - start_time
#                 self.metrics.track_request("gRPC", "ChatStream", 200, latency)

            # 
#                 yield response

#         except Exception as e:
#             logger.error(": %s", str(e))

            # 
#             latency = time.time() - start_time
#             self.metrics.track_request("gRPC", "ChatStream", 500, latency)

            # 
#             xiaoai_pb2.ChatResponse(
#                 message_id =str(uuid.uuid4()),
#                 message=f": {e!s}",
#                 confidence=0.0,
#                 timestamp=int(time.time()),
#             )
#             error_response.metadata["error"] = str(e)

#             yield error_response

#         finally:
            # 
#             self.metrics.decrement_active_requests("ChatStream")

#             async def CoordinateDiagnosis(self, request, context):
#         """"""
            

#             Args:
#             request: DiagnosisCoordinationRequest
#             context: gRPC

#             Returns:
#             DiagnosisCoordinationResponse: 
#         """"""
#             time.time()

        # 
#             self.metrics.increment_active_requests("CoordinateDiagnosis")

#         try:
            # 
#             response = await self.diagnosis_coordinator.coordinate_diagnosis(request)

            # 
#             latency = time.time() - start_time
#             self.metrics.track_request("gRPC", "CoordinateDiagnosis", 200, latency)

#             return response

#         except Exception as e:
#             logger.error(": %s", str(e))

            # 
#             latency = time.time() - start_time
#             self.metrics.track_request("gRPC", "CoordinateDiagnosis", 500, latency)

            # 
#             return xiaoai_pb2.DiagnosisCoordinationResponse(
#                 coordination_id =str(uuid.uuid4()),
#                 summary=f": {e!s}",
#                 timestamp=int(time.time()),
#             )

#         finally:
            # 
#             self.metrics.decrement_active_requests("CoordinateDiagnosis")

#             async def ProcessMultimodalInput(self, request, context):
#         """"""
            

#             Args:
#             request: MultimodalRequest
#             context: gRPC

#             Returns:
#             MultimodalResponse: 
#         """"""
#             time.time()

        # 
#             self.metrics.increment_active_requests("ProcessMultimodalInput")

#         try:
            # 
#             userid = request.user_id
#             request.session_id if request.session_id else str(uuid.uuid4())

            # 
#             inputdata = {}

            # 
#             if request.HasField("voice"): input_data["voice"] = request.voice:
#             elif request.HasField("image"): input_data["image"] = request.image:
#             elif request.HasField("text"): input_data["text"] = request.text.text  # :
#             elif request.HasField("sign"): input_data["sign"] = request.sign:
#             else:
#                 raise ValueError("")

            # 
#                 input_data["metadata"] = {}
#             for key, value in request.metadata.items(): input_data["metadata"][key] = value:

            # 
#                 result = await self.agent_manager.process_multimodal_input(
#                 userid, inputdata, session_id
#                 )

            # 
#                 response = xiaoai_pb2.MultimodalResponse(
#                 request_id =result.get("request_id", str(uuid.uuid4())),
#                 confidence=result.get("confidence", 0.0),
#                 error_message =result.get("error_message", ""),
#                 timestamp=int(time.time()),
#                 )

            # 
#             if "voice_result" in result:
                # 
#                 voiceresult = xiaoai_pb2.VoiceResult(
#                     transcription=result["voice_result"].get("transcription", ""),
#                     detected_language =result["voice_result"].get(
#                 "detected_language", ""
#                     ),
#                     detected_dialect =result["voice_result"].get("detected_dialect", ""),
#                     speech_rate =result["voice_result"].get("speech_rate", 0.0),
#                 )

                # 
#                 for emotion, score in (:
#                     result["voice_result"].get("emotions", {}).items()
#                     ): voice_result.emotions[emotion] = score

                # 
#                 for feature in result["voice_result"].get("features", []): voice_result.features.append(:
#                         xiaoai_pb2.SpeechFeature(
#                     feature_name =feature.get("feature_name", ""),
#                     value=feature.get("value", 0.0),
#                     description=feature.get("description", ""),
#                         )
#                     )

#                     response.voice_result.CopyFrom(voiceresult)

#             elif "image_result" in result:
                # 
#                 imageresult = xiaoai_pb2.ImageResult(
#                     image_type =result["image_result"].get("image_type", ""),
#                     processed_image =result["image_result"].get("processed_image", b""),
#                 )

                # 
#                 for feature in result["image_result"].get("features", []):
#                     imgfeature = xiaoai_pb2.ImageFeature(
#                         feature_name =feature.get("feature_name", ""),
#                         confidence=feature.get("confidence", 0.0),
#                         description=feature.get("description", ""),
#                     )

                    # 
#                     if "location" in feature:
#                         loc = feature["location"]
#                         img_feature.location.xmin = loc.get("x_min", 0.0)
#                         img_feature.location.ymin = loc.get("y_min", 0.0)
#                         img_feature.location.xmax = loc.get("x_max", 0.0)
#                         img_feature.location.ymax = loc.get("y_max", 0.0)

#                         image_result.features.append(imgfeature)

                # 
#                 for cls, score in (:
#                     result["image_result"].get("classifications", {}).items()
#                     ): image_result.classifications[cls] = score

                # 
#                 for _visname, vis_data in (:
#                     result["image_result"].get("visualizations", {}).items()
#                     ): image_result.visualizations[vis_name] = vis_data

#                     response.image_result.CopyFrom(imageresult)

#             elif "text_result" in result:
                # 
#                 textresult = xiaoai_pb2.TextResult(
#                     processed_text =result["text_result"].get("processed_text", ""),
#                     detected_language =result["text_result"].get(
#                 "detected_language", ""
#                     ),
#                     sentiment_score =result["text_result"].get("sentiment_score", 0.0),
#                 )

                # 
#                 for intent, score in (:
#                     result["text_result"].get("intent_scores", {}).items()
#                     ): text_result.intent_scores[intent] = score

                # 
#                 for entity, value in result["text_result"].get("entities", {}).items(): text_result.entities[entity] = value:

#                     response.text_result.CopyFrom(textresult)

#             elif "sign_result" in result:
                # 
#                 signresult = xiaoai_pb2.SignLanguageResult(
#                     transcription=result["sign_result"].get("transcription", ""),
#                     confidence=result["sign_result"].get("confidence", 0.0),
#                 )

                # 
#                 for gesture in result["sign_result"].get("gestures", []): sign_result.gestures.append(:
#                         xiaoai_pb2.SignGesture(
#                     gesture_type =gesture.get("gesture_type", ""),
#                     meaning=gesture.get("meaning", ""),
#                     confidence=gesture.get("confidence", 0.0),
#                     timestamp_ms =gesture.get("timestamp_ms", 0),
#                         )
#                     )

#                     response.sign_result.CopyFrom(signresult)

            # 
#             for key, value in result.get("metadata", {}).items():
#                 response.metadata[key] = str(value)

            # 
#                 latency = time.time() - start_time
#                 self.metrics.track_request("gRPC", "ProcessMultimodalInput", 200, latency)

#                 return response

#         except Exception as e:
#             logger.error(": %s", str(e))

            # 
#             latency = time.time() - start_time
#             self.metrics.track_request("gRPC", "ProcessMultimodalInput", 500, latency)

            # 
#             return xiaoai_pb2.MultimodalResponse(
#                 request_id =str(uuid.uuid4()),
#                 error_message =f": {e!s}",
#                 confidence=0.0,
#                 timestamp=int(time.time()),
#             )

#         finally:
            # 
#             self.metrics.decrement_active_requests("ProcessMultimodalInput")

#             async def QueryHealthRecord(self, request, context):
#         """"""
            

#             Args:
#             request: HealthRecordRequest
#             context: gRPC

#             Returns:
#             HealthRecordResponse: 
#         """"""
#             time.time()

        # 
#             self.metrics.increment_active_requests("QueryHealthRecord")

#         try:
            # 
#             userid = request.user_id
#             request.end_time or int(time.time())

            # 
#             records = [
#                 {
#             "record_id": str(uuid.uuid4()),
#             "user_id": userid,
#             "record_type": record_type or "",
#             "title": "",
#             "content": "",
#             "metadata": {"source": "xiaoai", "importance": "normal"},
#             "created_at": int(time.time()) - 86400,
#             "updated_at": int(time.time()) - 86400,
#                 }
#             ]

            # 
#             response = xiaoai_pb2.HealthRecordResponse(
#                 total_count =len(records), has_more =False
#             )

            # 
#             for record in records:
#                 healthrecord = xiaoai_pb2.HealthRecord(
#                     record_id =record["record_id"],
#                     user_id =record["user_id"],
#                     record_type =record["record_type"],
#                     title=record["title"],
#                     content=record["content"],
#                     created_at =record["created_at"],
#                     updated_at =record["updated_at"],
#                 )

                # 
#                 for key, value in record.get("metadata", {}).items(): health_record.metadata[key] = str(value):

#                     response.records.append(healthrecord)

            # 
#                     latency = time.time() - start_time
#                     self.metrics.track_request("gRPC", "QueryHealthRecord", 200, latency)

#                     return response

#         except Exception as e:
#             logger.error(": %s", str(e))

            # 
#             latency = time.time() - start_time
#             self.metrics.track_request("gRPC", "QueryHealthRecord", 500, latency)

            # 
#             return xiaoai_pb2.HealthRecordResponse(total_count =0, has_more =False)

#         finally:
            # 
#             self.metrics.decrement_active_requests("QueryHealthRecord")

#             async def GenerateHealthSummary(self, request, context):
#         """"""
            

#             Args:
#             request: HealthSummaryRequest
#             context: gRPC

#             Returns:
#             HealthSummaryResponse: 
#         """"""
#             time.time()

        # 
#             self.metrics.increment_active_requests("GenerateHealthSummary")

#         try:
            # 
#             userid = request.user_id
#             starttime_ms = request.start_time or 0
#             endtime_ms = request.end_time or int(time.time())
#             categories = list(request.categories)
#             includecharts = request.include_charts

            # 
#             healthdata = {
#                 "start_time": starttime_ms,
#                 "end_time": endtime_ms,
#                 "categories": categories,
#                 "include_charts": includecharts,
#                 "include_recommendations": include_recommendations,
#             }

#             summary = await self.agent_manager.generate_health_summary(
#                 userid, healthdata
#             )

            # 
#             response = xiaoai_pb2.HealthSummaryResponse(
#                 summary_id =summary.get("summary_id", str(uuid.uuid4())),
#                 user_id =userid,
#                 text_summary =summary.get("text_summary", ""),
#                 generated_at =int(time.time()),
#             )

            # 
#             for trend in summary.get("trends", []):
#                 response.trends.append(
#                     xiaoai_pb2.HealthTrend(
#                 metric_name =trend.get("metric_name", ""),
#                 trend_direction =trend.get("trend_direction", ""),
#                 change_percentage =trend.get("change_percentage", 0.0),
#                 description=trend.get("description", ""),
#                 priority=trend.get("priority", 1),
#                     )
#                 )

            # 
#             for metric in summary.get("metrics", []):
#                 response.metrics.append(
#                     xiaoai_pb2.HealthMetric(
#                 name=metric.get("name", ""),
#                 value=metric.get("value", ""),
#                 unit=metric.get("unit", ""),
#                 status=metric.get("status", ""),
#                 reference_range =metric.get("reference_range", ""),
#                     )
#                 )

            # 
#             if include_recommendations: for rec in summary.get("recommendations", []):
#                     recommendation = xiaoai_pb2.Recommendation(
#                 content=rec.get("content", ""),
#                 reason=rec.get("reason", ""),
#                 priority=rec.get("priority", 1),
#                     )

                    # 
#                     rectype = rec.get("type", "").upper()
#                     if rectype == "DIET":
#                         recommendation.type = xiaoai_pb2.Recommendation.DIET
#                     elif rectype == "EXERCISE":
#                         recommendation.type = xiaoai_pb2.Recommendation.EXERCISE
#                     elif rectype == "LIFESTYLE":
#                         recommendation.type = xiaoai_pb2.Recommendation.LIFESTYLE
#                     elif rectype == "MEDICATION":
#                         recommendation.type = xiaoai_pb2.Recommendation.MEDICATION
#                     elif rectype == "FOLLOW_UP":
#                         recommendation.type = xiaoai_pb2.Recommendation.FOLLOW_UP
#                     elif rectype == "CONSULTATION":
#                         recommendation.type = xiaoai_pb2.Recommendation.CONSULTATION

                    # 
#                     for key, value in rec.get("metadata", {}).items():
#                         recommendation.metadata[key] = str(value)

#                         response.recommendations.append(recommendation)

            # 
#             if include_charts: for _chartname, chart_data in summary.get("charts", {}).items():
#                     response.charts[chart_name] = chart_data

            # 
#                 latency = time.time() - start_time
#                 self.metrics.track_request("gRPC", "GenerateHealthSummary", 200, latency)

#                 return response

#         except Exception as e:
#             logger.error(": %s", str(e))

            # 
#             latency = time.time() - start_time
#             self.metrics.track_request("gRPC", "GenerateHealthSummary", 500, latency)

            # 
#             return xiaoai_pb2.HealthSummaryResponse(
#                 summary_id =str(uuid.uuid4()),
#                 user_id =request.userid,
#                 text_summary =f": {e!s}",
#                 generated_at =int(time.time()),
#             )

#         finally:
            # 
#             self.metrics.decrement_active_requests("GenerateHealthSummary")

#             async def HealthCheck(self, request, context):
#         """"""
            

#             Args:
#             request: HealthCheckRequest
#             context: gRPC

#             Returns:
#             HealthCheckResponse: 
#         """"""
#         try:
            # 
#             details = {}

            # MongoDB
#             details["mongodb"] = "connected" if mongo_status else "disconnected"

            # LLM
#             details["llm_service"] = "available"

            # 
#             for service_name in [:
#                 "look_service",
#                 "listen_service",
#                 "inquiry_service",
#                 "palpation_service",
#                 ]:
#                 details[service_name] = "connected"

            # 
#                 response = xiaoai_pb2.HealthCheckResponse(
#                 status=xiaoai_pb2.HealthCheckResponse.SERVING
#                 )

            # , 
#             if request.include_details: for key, value in details.items():
#                     response.details[key] = value

#                 return response

#         except Exception as e:
#             logger.error(": %s", str(e))

            # 
#             response = xiaoai_pb2.HealthCheckResponse(
#                 status=xiaoai_pb2.HealthCheckResponse.NOT_SERVING
#             )

#             response.details["error"] = str(e)
#             return response
