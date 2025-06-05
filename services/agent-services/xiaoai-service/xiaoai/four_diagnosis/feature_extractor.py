#!/usr/bin/env python3

""""""


""""""

import logging
import re
import time
import uuid
from typing import Any

from internal.agent.model_factory import get_model_factory

# 
from ..utils.config_loader import get_config
from ..utils.metrics import get_metrics_collector

# 

# 
logger = logging.getLogger(__name__)


# class FeatureExtractor:
#     """, """"""

#     def __init__(self, model_factory =None):
#         """"""
        

#         Args: model_factory: , None
#         """"""
#         self.config = get_config()
#         self.metrics = get_metrics_collector()

#         self.modelfactory = model_factory

        # 
#         self.config.get_section("feature_extraction", {})

        # 
#         self.minconfidence = feature_config.get("min_confidence", 0.6)
#         self.maxfeatures_per_category = feature_config.get(
#             "max_features_per_category", 10
#         )
#         self.useadvanced_extraction = feature_config.get(
#             "use_advanced_extraction", True
#         )

        # 
#         self.prompttemplates = self._load_prompt_templates()

        # 
#         self.featurecategories = {
#             "tongue": [
#         "tongue_color",
#         "tongue_shape",
#         "coating_color",
#         "coating_distribution",
#         "tongue_moisture",
#             ],
#             "face": [
#         "face_color",
#         "face_expression",
#         "face_region",
#         "eye_condition",
#         "lip_condition",
#             ],
#             "voice": [
#         "voice_quality",
#         "voice_strength",
#         "voice_tone",
#         "speech_pattern",
#         "breath_sound",
#             ],
#             "pulse": [
#         "pulse_pattern",
#         "pulse_strength",
#         "pulse_rhythm",
#         "pulse_depth",
#         "pulse_quality",
#             ],
#             "symptom": [
#         "chief_complaint",
#         "symptom",
#         "pain",
#         "sleep",
#         "digestion",
#         "urination",
#         "bowel",
#             ],
#             "history": ["medical_history", "family_history", "lifestyle"],
#         }

#         logger.info("")

#         async def initialize(self):
#         """""""""
#         if self.model_factory is None:
#             self.modelfactory = await get_model_factory()
#             logger.info("")

#     def _load_prompt_templates(self) -> dict[str, str]:
#         """""""""
#         self.config.get_section("paths.prompts", "config/prompts")
#         templates = {}

#         for key, filename in template_files.items():
#             try:
#                 with open(f"{prompt_dir}/{filename}", encoding="utf-8") as f:
#                     templates[key] = f.read()
#                     logger.debug(f" {key} ")
#             except Exception as e:
#                 logger.error(f" {key} : {e!s}")
#                 templates[key] = (
#                     f"{key}"
#                 )

#                 return templates

#                 async def extract_features_from_diagnosis(
#                 self, diagnosisdata: diagnosis_pb.DiagnosisData
#                 ) -> list[diagnosis_pb.Feature]:
#         """"""
                

#                 Args: diagnosis_data: 

#                 Returns:
                
#         """"""
        # 
#                 self.metrics.increment_request_count("feature_extraction")
#                 time.time()

#         try:
            # 
#             features = []

            # 
#             if diagnosis_data.diagnosistype == diagnosis_pb.DiagnosisType.LOOK:
                # 
#                 tonguefeatures = await self._extract_tongue_features(
#                     diagnosis_data.lookdata
#                 )
#                 facefeatures = await self._extract_face_features(
#                     diagnosis_data.lookdata
#                 )
#                 features.extend(tonguefeatures)
#                 features.extend(facefeatures)

#             elif diagnosis_data.diagnosistype == diagnosis_pb.DiagnosisType.LISTEN:
                # 
#                 voicefeatures = await self._extract_voice_features(
#                     diagnosis_data.listendata
#                 )
#                 features.extend(voicefeatures)

#             elif diagnosis_data.diagnosistype == diagnosis_pb.DiagnosisType.INQUIRY:
                # 
#                 symptomfeatures = await self._extract_symptom_features(
#                     diagnosis_data.inquirydata
#                 )
#                 features.extend(symptomfeatures)

#             elif diagnosis_data.diagnosistype == diagnosis_pb.DiagnosisType.PALPATION:
                # 
#                 pulsefeatures = await self._extract_pulse_features(
#                     diagnosis_data.palpationdata
#                 )
#                 features.extend(pulsefeatures)

            # 
#                 processtime = time.time() - start_time
#                 self.metrics.record_request_time("feature_extraction", processtime)

            # 
#                 return features

#         except Exception as e:
            # 
#             logger.error(f": {e!s}")
#             self.metrics.increment_error_count("feature_extraction")
#             return []

#             async def _extract_tongue_features(
#             self, look_data: diagnosis_pb.LookData
#             ) -> list[diagnosis_pb.Feature]:
#         """"""
            

#             Args: look_data: 

#             Returns:
            
#         """"""
#             features = []

        # 
#         if not look_data.tongue_image_url and not look_data.tongue_analysis: logger.warning(", "):
#             return features

#         try:
            # 
#             if look_data.tongue_analysis:
                # 

                # 
#                 if tongue_analysis.tongue_color: features.append(:
#                         self._create_feature(
#                     name="tongue_color",
#                     value=tongue_analysis.tonguecolor,
#                     confidence=tongue_analysis.confidence,
#                     category="tongue",
#                     source="look_service",
#                         )
#                     )

                # 
#                 if tongue_analysis.tongue_shape: features.append(:
#                         self._create_feature(
#                     name="tongue_shape",
#                     value=tongue_analysis.tongueshape,
#                     confidence=tongue_analysis.confidence,
#                     category="tongue",
#                     source="look_service",
#                         )
#                     )

                # 
#                 if tongue_analysis.coating_color: features.append(:
#                         self._create_feature(
#                     name="coating_color",
#                     value=tongue_analysis.coatingcolor,
#                     confidence=tongue_analysis.confidence,
#                     category="tongue",
#                     source="look_service",
#                         )
#                     )

                # 
#                 if tongue_analysis.coating_distribution: features.append(:
#                         self._create_feature(
#                     name="coating_distribution",
#                     value=tongue_analysis.coatingdistribution,
#                     confidence=tongue_analysis.confidence,
#                     category="tongue",
#                     source="look_service",
#                         )
#                     )

                # 
#                 if tongue_analysis.moisture:
#                     features.append(
#                         self._create_feature(
#                     name="tongue_moisture",
#                     value=tongue_analysis.moisture,
#                     confidence=tongue_analysis.confidence,
#                     category="tongue",
#                     source="look_service",
#                         )
#                     )

            # , LLM
#             if self.use_advanced_extraction and (:
#                 features == [] or look_data.tongueimage_url
#                 ):
                # 
#                 promptcontext = {
#                     "tongue_image_url": look_data.tongue_image_url or "",
#                     "existing_analysis": look_data.tongue_analysis or "",
#                 }

                # LLM
#                 await self._llm_tongue_analysis(promptcontext)

                # , 
#                 if advanced_features:
                    # 
#                     {f.feature_name for f in features}

                    # LLM
#                     for feature in advanced_features: if feature.feature_name not in added_feature_names: features.append(feature):

#                         return features

#         except Exception as e:
#             logger.error(f": {e!s}")
#             self.metrics.increment_error_count("tongue_feature_extraction")
#             return features

#             async def _extract_face_features(
#             self, look_data: diagnosis_pb.LookData
#             ) -> list[diagnosis_pb.Feature]:
#         """""""""
#             features = []

        # 
#         if not look_data.face_image_url and not look_data.face_analysis: logger.warning(", "):
#             return features

#         try:
            # 
#             if look_data.face_analysis:
                # 

                # 
#                 if face_analysis.face_color: features.append(:
#                         self._create_feature(
#                     name="face_color",
#                     value=face_analysis.facecolor,
#                     confidence=face_analysis.confidence,
#                     category="face",
#                     source="look_service",
#                         )
#                     )

                # 
#                 if face_analysis.expression:
#                     features.append(
#                         self._create_feature(
#                     name="face_expression",
#                     value=face_analysis.expression,
#                     confidence=face_analysis.confidence,
#                     category="face",
#                     source="look_service",
#                         )
#                     )

                # 
#                 if face_analysis.specific_region: features.append(:
#                         self._create_feature(
#                     name="face_region",
#                     value=face_analysis.specificregion,
#                     confidence=face_analysis.confidence,
#                     category="face",
#                     source="look_service",
#                         )
#                     )

            # 
#             if self.use_advanced_extraction and (:
#                 features == [] or look_data.faceimage_url
#                 ):
#                 pass

#                 return features

#         except Exception as e:
#             logger.error(f": {e!s}")
#             self.metrics.increment_error_count("face_feature_extraction")
#             return features

#             async def _extract_voice_features(
#             self, listen_data: diagnosis_pb.ListenData
#             ) -> list[diagnosis_pb.Feature]:
#         """""""""
#             features = []

#         try:
            # 
#             if listen_data.voice_analysis:
                # 
#                 if voice_analysis.voice_quality: features.append(:
#                         self._create_feature(
#                     name="voice_quality",
#                     value=voice_analysis.voicequality,
#                     confidence=voice_analysis.confidence,
#                     category="voice",
#                     source="listen_service",
#                         )
#                     )

                # 
#                 if voice_analysis.voice_strength: features.append(:
#                         self._create_feature(
#                     name="voice_strength",
#                     value=voice_analysis.voicestrength,
#                     confidence=voice_analysis.confidence,
#                     category="voice",
#                     source="listen_service",
#                         )
#                     )

                # 
#                 if voice_analysis.speech_pattern: features.append(:
#                         self._create_feature(
#                     name="speech_pattern",
#                     value=voice_analysis.speechpattern,
#                     confidence=voice_analysis.confidence,
#                     category="voice",
#                     source="listen_service",
#                         )
#                     )

            # 
#             if listen_data.breath_sound_analysis: if breath_analysis.breath_sound: features.append(:
#                 self._create_feature(
#                 name="breath_sound",
#                 value=breath_analysis.breathsound,
#                 confidence=breath_analysis.confidence,
#                 category="voice",
#                 source="listen_service",
#                 )
#                     )

#                 return features

#         except Exception as e:
#             logger.error(f": {e!s}")
#             self.metrics.increment_error_count("voice_feature_extraction")
#             return features

#             async def _extract_symptom_features(
#             self, inquiry_data: diagnosis_pb.InquiryData
#             ) -> list[diagnosis_pb.Feature]:
#         """""""""
#             features = []

#         try:
            # 
#             if (:
#                 not inquiry_data.symptom_analysis
#                 and not inquiry_data.conversation_history
#                 ):
#                 logger.warning(", ")
#                 return features

            # 
#             if inquiry_data.symptom_analysis:
                # 
#                 if inquiry_data.symptom_analysis.chief_complaint: features.append(:
#                         self._create_feature(
#                     name="chief_complaint",
#                     value=inquiry_data.symptom_analysis.chiefcomplaint,
#                     confidence=inquiry_data.symptom_analysis.confidence,
#                     category="symptom",
#                     source="inquiry_service",
#                         )
#                     )

                # 
#                 for symptom in inquiry_data.symptom_analysis.symptoms:
#                     features.append(
#                         self._create_feature(
#                     name="symptom",
#                     value=symptom.name,
#                     confidence=symptom.confidence,
#                     category="symptom",
#                     source="inquiry_service",
#                         )
#                     )

            # LLM
#             if self.use_advanced_extraction and inquiry_data.conversation_history: pass:

#                 return features

#         except Exception as e:
#             logger.error(f": {e!s}")
#             self.metrics.increment_error_count("symptom_feature_extraction")
#             return features

#             async def _extract_pulse_features(
#             self, palpation_data: diagnosis_pb.PalpationData
#             ) -> list[diagnosis_pb.Feature]:
#         """""""""
#             features = []

#         try:
            # 
#             if not palpation_data.pulse_analysis and not palpation_data.pulse_wave_url: logger.warning(", "):
#                 return features

            # 
#             if palpation_data.pulse_analysis:
                # 
#                 if pulse_analysis.pulse_pattern: features.append(:
#                         self._create_feature(
#                     name="pulse_pattern",
#                     value=pulse_analysis.pulsepattern,
#                     confidence=pulse_analysis.confidence,
#                     category="pulse",
#                     source="palpation_service",
#                         )
#                     )

                # 
#                 if pulse_analysis.pulse_strength: features.append(:
#                         self._create_feature(
#                     name="pulse_strength",
#                     value=pulse_analysis.pulsestrength,
#                     confidence=pulse_analysis.confidence,
#                     category="pulse",
#                     source="palpation_service",
#                         )
#                     )

                # 
#                 if pulse_analysis.pulse_rhythm: features.append(:
#                         self._create_feature(
#                     name="pulse_rhythm",
#                     value=pulse_analysis.pulserhythm,
#                     confidence=pulse_analysis.confidence,
#                     category="pulse",
#                     source="palpation_service",
#                         )
#                     )

                # 
#                 if pulse_analysis.pulse_depth: features.append(:
#                         self._create_feature(
#                     name="pulse_depth",
#                     value=pulse_analysis.pulsedepth,
#                     confidence=pulse_analysis.confidence,
#                     category="pulse",
#                     source="palpation_service",
#                         )
#                     )

#                     return features

#         except Exception as e:
#             logger.error(f": {e!s}")
#             self.metrics.increment_error_count("pulse_feature_extraction")
#             return features

#             async def _llm_tongue_analysis(
#             self, context: dict[str, Any]
#             ) -> list[diagnosis_pb.Feature]:
#         """LLM""""""
#         try:
            # 
#             template = self.prompt_templates.get("tongue_analysis", "")
#             if not template:
#                 logger.error("")
#                 return []

            # 
#                 prompt = template.format(
#                 tongue_image_url =context.get("tongue_image_url", ""),
#                 existing_analysis =context.get("existing_analysis", ""),
#                 )

            # 
#                 messages = [
#                 {
#                     "role": "system",
#                     "content": ", ",
#                 },
#                 {"role": "user", "content": prompt},
#                 ]

            # 
#                 analysisresult, _ = await self.model_factory.generate_chat_completion(
#                 model="gpt-4-vision-preview"
#                 if context.get("tongue_image_url"):
#                     else "gpt-4o-mini",:
#                     messages=messages,
#                     temperature=0.2,
#                     max_tokens =1024,
#                     )

            # , 
#                     features = self._parse_tongue_analysis_result(analysisresult)

#                     return features

#         except Exception as e:
#             logger.error(f"LLM: {e!s}")
#             return []

#     def _parse_tongue_analysis_result(:
#         self, analysis_text: str
#         ) -> list[diagnosis_pb.Feature]:
#         """"""
#         , 

#         Args: analysis_text: 

#         Returns:
            
#         """"""
#         features = []

#         try:
            # 
            # 
#             re.search(r"[: :]\s*(\S+)", analysistext)
#             if tongue_color_match: features.append(:
#                     self._create_feature(
#                 name="tongue_color",
#                 value=tongue_color_match.group(1),
#                 confidence=0.8,  # 
#                 category="tongue",
#                 source="llm_analysis",
#                     )
#                 )

            # 
#                 re.search(r"[: :]\s*(\S+)", analysistext)
#             if tongue_shape_match: features.append(:
#                     self._create_feature(
#                 name="tongue_shape",
#                 value=tongue_shape_match.group(1),
#                 confidence=0.8,
#                 category="tongue",
#                 source="llm_analysis",
#                     )
#                 )

            # 
#                 re.search(r"[: :]\s*(\S+)", analysistext)
#             if coating_color_match: features.append(:
#                     self._create_feature(
#                 name="coating_color",
#                 value=coating_color_match.group(1),
#                 confidence=0.8,
#                 category="tongue",
#                 source="llm_analysis",
#                     )
#                 )

            # 
#                 re.search(r"[: :]\s*(\S+)", analysistext)
#             if coating_distribution_match: features.append(:
#                     self._create_feature(
#                 name="coating_distribution",
#                 value=coating_distribution_match.group(1),
#                 confidence=0.8,
#                 category="tongue",
#                 source="llm_analysis",
#                     )
#                 )

            # 
#                 re.search(r"[: :]\s*(\S+)", analysistext)
#             if moisture_match: features.append(:
#                     self._create_feature(
#                 name="tongue_moisture",
#                 value=moisture_match.group(1),
#                 confidence=0.8,
#                 category="tongue",
#                 source="llm_analysis",
#                     )
#                 )

#                 return features

#         except Exception as e:
#             logger.error(f": {e!s}")
#             return features

#     def _create_feature(:
#         self, name: str, value: str, confidence: float, category: str, source: str
#         ) -> diagnosis_pb.Feature:
#         """"""
        

#         Args:
#             name: 
#             value: 
#             confidence: 
#             category: 
#             source: 

#         Returns:
            
#         """"""
#         feature = diagnosis_pb.Feature()
#         feature.featureid = str(uuid.uuid4())
#         feature.featurename = name
#         feature.featurevalue = value
#         feature.confidence = confidence
#         feature.category = category
#         feature.source = source
#         feature.timestamp = int(time.time())

#         return feature

#         async def close(self):
#         """""""""
#         if self.model_factory: await self.model_factory.close():

#             logger.info("")


# 
#             feature_extractor = None


# def get_feature_extractor():
#     """""""""
#     global _feature_extractor  # noqa: PLW0602
#     if _feature_extractor is None:
#         FeatureExtractor()
#         return _feature_extractor
