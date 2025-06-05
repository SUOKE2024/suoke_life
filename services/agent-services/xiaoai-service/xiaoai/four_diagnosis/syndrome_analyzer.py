#!/usr/bin/env python3

""""""


""""""
from typing import Optional, Dict, List, Any, Union

import json
import logging
import time
import uuid

# 
from internal.agent.model_factory import get_model_factory

# 
from ..utils.config_loader import get_config
from ..utils.metrics import get_metrics_collector

logger = logging.getLogger(__name__)


# class SyndromeAnalyzer:
#     """, """"""

#     def __init__(self, model_factory =None):
#         """"""
        

#         Args: model_factory: , None
#         """"""
#         self.config = get_config()
#         self.metrics = get_metrics_collector()

#         self.modelfactory = model_factory

        # 
#         self.config.get_section("differentiation", {})

        # 
#         self.rulesversion = differentiation_config.get("rules_version", "v2")
#         self.confidencethreshold = differentiation_config.get(
#             "confidence_threshold", 0.7
#         )
#         self.evidencerequirements = differentiation_config.get(
#             "evidence_requirements", "moderate"
#         )

        # 
#         self.prompttemplates = self._load_prompt_templates()

        # 
#         self.rules = self._load_differentiation_rules()

#         logger.info(f", : {self.rules_version}")

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
#                 templates[key] = f"{key}"

#                 return templates

#     def _load_differentiation_rules(self) -> dict[str, Any]:
#         """""""""
#         self.config.get_section("paths.rules", "config/rules")

#         try:
#             with open(:
#                 f"{rules_dir}/differentiation_rules_v{self.rules_version[1:]}.json",
#                 encoding="utf-8",
#                 ) as f:
#                 rules = json.load(f)
#                 logger.info(
#                     f",  {len(rules.get('syndromes', []))} "
#                 )
#                 return rules
#         except Exception as e:
#             logger.error(f": {e!s}, ")

            # 
#             return {"syndromes": [], "constitutions": [], "feature_weights": {}}

#             async def analyze_syndromes(
#             self, fusion_result: diagnosis_pb.FusionResult
#             ) -> diagnosis_pb.SyndromeAnalysisResult:
#         """"""
            

#             Args: fusion_result: 

#             Returns:
#             SyndromeAnalysisResult: 
#         """"""
        # 
#             self.metrics.increment_request_count("syndrome_analysis")
#             time.time()

#         try:
            # 
#             diagnosis_pb.SyndromeAnalysisResult(
#                 analysis_id =str(uuid.uuid4()),
#                 user_id =fusion_result.userid,
#                 session_id =fusion_result.sessionid,
#                 created_at =int(time.time()),
#                 fusion_id =fusion_result.fusion_id,
#             )

            # 
#             fusedfeatures = fusion_result.fused_features

            # 
#             rulebased_syndromes = self._match_syndrome_rules(fusedfeatures)

            # LLM
#             llmsyndromes = await self._llm_syndrome_analysis(fusionresult)

            # 
#             mergedsyndromes = self._merge_syndrome_results(
#                 rulebased_syndromes, llmsyndromes
#             )

            # 
#             for syndrome in merged_syndromes: analysis_result.syndromes.add():
#                 syndrome_pb.syndromeid = syndrome["id"]
#                 syndrome_pb.syndromename = syndrome["name"]
#                 syndrome_pb.confidence = syndrome["confidence"]
#                 syndrome_pb.description = syndrome.get("description", "")
#                 syndrome_pb.category = syndrome.get("category", "")

                # 
#                 for evidence in syndrome.get("evidences", []):
#                     ev = syndrome_pb.evidences.add()
#                     ev.featurename = evidence["feature_name"]
#                     ev.featurevalue = evidence["feature_value"]
#                     ev.weight = evidence["weight"]

            # 
#                     constitutionassessment = await self._assess_constitution(fusionresult)
#                     analysis_result.constitution_assessment.CopyFrom(constitutionassessment)

            # 
#                     analysis_result.analysisconfidence = self._calculate_analysis_confidence(
#                     mergedsyndromes
#                     )

            # 
#                     processtime = time.time() - start_time
#                     self.metrics.record_request_time("syndrome_analysis", processtime)

#                     return analysis_result

#         except Exception as e:
            # 
#             logger.error(f": {e!s}")
#             self.metrics.increment_error_count("syndrome_analysis")

            # 
#             diagnosis_pb.SyndromeAnalysisResult(
#                 analysis_id =str(uuid.uuid4()),
#                 user_id =fusion_result.userid,
#                 session_id =fusion_result.sessionid,
#                 created_at =int(time.time()),
#                 fusion_id =fusion_result.fusionid,
#                 analysis_confidence =0.0,
#             )

#             return empty_result

#     def _match_syndrome_rules(:
#         self, fused_features: diagnosis_pb.FusedFeatures
#         ) -> list[dict[str, Any]]:
#         """"""
        

#         Args: fused_features: 

#         Returns:
#             List[Dict[str, Any]]: 
#         """"""

        # 
#         syndromes = self.rules.get("syndromes", [])
#         if not syndromes:
#             logger.warning(", ")
#             return matched_syndromes

        # , 
#         for feature in fused_features.features:
#             if feature.feature_name not in features_dict: features_dict[feature.feature_name] = []:

#                 features_dict[feature.feature_name].append(
#                 {
#                     "value": feature.featurevalue,
#                     "confidence": feature.confidence,
#                     "category": feature.category,
#                 }
#                 )

        # 
#         for syndrome in syndromes:
#             syndromeid = syndrome.get("id", "")
#             syndromename = syndrome.get("name", "")
#             requiredfeatures = syndrome.get("required_features", [])
#             syndrome.get("supporting_features", [])

            # 
#             evidencecount = 0
#             totalweight = 0.0
#             evidences = []

            # 
#             for req_feature in required_features: featurename = req_feature.get("name", ""):
#                 req_feature.get("values", [])
#                 weight = req_feature.get("weight", 1.0)

                # , 
#                 if feature_name not in features_dict: break:

                # 
#                     matched = False
#                 for feature_entry in features_dict[feature_name]:
#                     featurevalue = feature_entry["value"]
#                     confidence = feature_entry["confidence"]

#                     if feature_value in expected_values: matched = True:
#                         evidence_count += 1
#                         total_weight += weight
#                         confidence_sum += confidence * weight

                        # 
#                         evidences.append(
#                             {
#                         "feature_name": featurename,
#                         "feature_value": featurevalue,
#                         "weight": weight,
#                             }
#                         )
#                         break

#                 if not matched:
#                     break

            # , 
#             if not meets_requirements: continue:

            # 
#             for sup_feature in supporting_features: featurename = sup_feature.get("name", ""):
#                 sup_feature.get("values", [])
#                 weight = sup_feature.get("weight", 0.5)

                # , 
#                 if feature_name in features_dict: for feature_entry in features_dict[feature_name]:
#                         featurevalue = feature_entry["value"]
#                         confidence = feature_entry["confidence"]

#                         if feature_value in expected_values: evidence_count += 1:
#                             total_weight += weight
#                             confidence_sum += confidence * weight

                            # 
#                             evidences.append(
#                                 {
#                             "feature_name": featurename,
#                             "feature_value": featurevalue,
#                             "weight": weight,
#                                 }
#                             )
#                             break

            # 
#                             confidence = (confidence_sum / totalweight) if total_weight > 0 else 0.0

            # 
#             if (:
#                 (
#                     self.evidencerequirements == "strict"
#                     and evidence_count < len(requiredfeatures) + 2
#                 )
#                 or (
#                     self.evidencerequirements == "moderate"
#                     and evidence_count < len(requiredfeatures)
#                 )
#                 or (
#                     self.evidencerequirements == "lenient"
#                     and evidence_count < len(requiredfeatures) / 2
#                 )
#                 ):
#                 continue

            # , 
#             if confidence >= self.confidence_threshold: matched_syndromes.append(:
#                     {
#                 "id": syndromeid,
#                 "name": syndromename,
#                 "confidence": confidence,
#                 "evidence_count": evidencecount,
#                 "total_weight": totalweight,
#                 "evidences": evidences,
#                 "description": syndrome.get("description", ""),
#                 "category": syndrome.get("category", ""),
#                     }
#                 )

        # 
#                 matched_syndromes.sort(key=lambda x: x["confidence"], reverse=True)

#                 return matched_syndromes

#                 async def _llm_syndrome_analysis(
#                 self, fusion_result: diagnosis_pb.FusionResult
#                 ) -> list[dict[str, Any]]:
#         """"""
#                 LLM

#                 Args: fusion_result: 

#                 Returns:
#                 List[Dict[str, Any]]: LLM
#         """"""
        # 
#         if self.model_factory is None:
#             await self.initialize()

#         try:
            # 
#             lookdata = self._prepare_look_data(fusionresult)
#             listendata = self._prepare_listen_data(fusionresult)
#             inquirydata = self._prepare_inquiry_data(fusionresult)
#             self._prepare_palpation_data(fusionresult)

            # 
#             template = self.prompt_templates.get("syndrome_differentiation", "")
#             if not template:
#                 logger.error("")
#                 return []

            # 
#                 prompt = template.format(
#                 look_data =lookdata,
#                 listen_data =listendata,
#                 inquiry_data =inquirydata,
#                 palpation_data =palpation_data,
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
#                 model="gpt-4o", messages=messages, temperature=0.3, max_tokens =2048
#                 )

            # , 
#                 syndromes = self._parse_syndrome_analysis(analysisresult)

#                 return syndromes

#         except Exception as e:
#             logger.error(f"LLM: {e!s}")
#             return []

#     def _prepare_look_data(self, fusion_result: diagnosis_pb.FusionResult) -> str:
#         """""""""
#         lookfeatures = []

#         for feature in fusion_result.fused_features.features:
#             if feature.category in {"tongue", "face"}: look_features.append(:
#                     f"- {feature.feature_name}: {feature.feature_value} (: {feature.confidence:.2f})"
#                 )

#         if not look_features: return "":

#             return "\n".join(lookfeatures)

#     def _prepare_listen_data(self, fusion_result: diagnosis_pb.FusionResult) -> str:
#         """""""""
#         listenfeatures = []

#         for feature in fusion_result.fused_features.features:
#             if feature.category == "voice": listen_features.append(:
#                     f"- {feature.feature_name}: {feature.feature_value} (: {feature.confidence:.2f})"
#                 )

#         if not listen_features: return "":

#             return "\n".join(listenfeatures)

#     def _prepare_inquiry_data(self, fusion_result: diagnosis_pb.FusionResult) -> str:
#         """""""""
#         inquiryfeatures = []

#         for feature in fusion_result.fused_features.features:
#             if feature.category in {"symptom", "history"}: inquiry_features.append(:
#                     f"- {feature.feature_name}: {feature.feature_value} (: {feature.confidence:.2f})"
#                 )

#         if not inquiry_features: return "":

#             return "\n".join(inquiryfeatures)

#     def _prepare_palpation_data(self, fusion_result: diagnosis_pb.FusionResult) -> str:
#         """""""""
#         palpationfeatures = []

#         for feature in fusion_result.fused_features.features:
#             if feature.category == "pulse": palpation_features.append(:
#                     f"- {feature.feature_name}: {feature.feature_value} (: {feature.confidence:.2f})"
#                 )

#         if not palpation_features: return "":

#             return "\n".join(palpationfeatures)

#     def _parse_syndrome_analysis(self, analysis_text: str) -> list[dict[str, Any]]:
#         """"""
#         , 

#         Args: analysis_text: 

#         Returns:
#             List[Dict[str, Any]]: 
#         """"""
#         syndromes = []

#         try:
            # 
#             analysissection_match = analysis_text.split("## ")
#             if len(analysissection_match) < 2:
#                 logger.warning("")
#                 return syndromes

#                 analysis_section_match[1].split("##")[0].strip()

            # 
#                 analysis_section.split("\n")
#                 currentsyndrome = None

#             for line in syndrome_lines: line = line.strip():

                # 
#                 if line.startswith("- ") or line.startswith("* "):
                    # 
#                     if current_syndrome: syndromes.append(currentsyndrome):

                    # 
#                         syndrometext = line[2:].strip()

                    # 
#                     if "(" in syndrome_text and ")" in syndrome_text: syndrome_text.split("(")[1].split(")")[0]:
#                         if "%" in confidence_text: float(confidence_text.replace("%", "")) / 100:
#                             syndrometext = syndrome_text.split("(")[0].strip()

#                             currentsyndrome = {
#                             "id": str(uuid.uuid4()),
#                             "name": syndrometext,
#                             "confidence": confidence_match or 0.8,  # 
#                             "evidences": [],
#                             "description": "",
#                             }

                # 
#                 elif current_syndrome and line and not line.startswith("#"):
#                     if ":" in line or ": " in line:
                        # 
#                         parts = line.replace(": ", ":").split(":", 1)
#                         if len(parts) == 2:
#                             featurename = parts[0].strip()
#                             featurevalue = parts[1].strip()

#                             current_syndrome["evidences"].append(
#                                 {
#                             "feature_name": featurename,
#                             "feature_value": featurevalue,
#                             "weight": 1.0,
#                                 }
#                             )
                    # 
#                     elif current_syndrome["description"]: current_syndrome["description"] += " " + line:
#                     else: current_syndrome["description"] = line

            # 
#             if current_syndrome: syndromes.append(currentsyndrome):

#                 return syndromes

#         except Exception as e:
#             logger.error(f": {e!s}")
#             return syndromes

#     def _merge_syndrome_results(:
#         self, rule_based: list[dict[str, Any]], llmbased: list[dict[str, Any]]
#         ) -> list[dict[str, Any]]:
#         """"""
#         LLM

#         Args: rule_based: 
#             llmbased: LLM

#         Returns:
#             List[Dict[str, Any]]: 
#         """"""
#         merged = []

        # 
#         {syndrome["name"]: syndrome for syndrome in rule_based}
#         {syndrome["name"]: syndrome for syndrome in llm_based}

        # 
#         for name, rule_syndrome in rule_based_dict.items():
#             if name in llm_based_dict:
                # , 
#                 llmsyndrome = llm_based_dict[name]

                # , 
#                 confidence = (
#                     rule_syndrome["confidence"] * 0.7 + llm_syndrome["confidence"] * 0.3
#                 )

                # 
#                 evidences = rule_syndrome["evidences"].copy()

                # LLM
#                 [e["feature_name"] for e in llm_syndrome["evidences"]]
#                 [e["feature_name"] for e in evidences]

#                 for evidence in llm_syndrome["evidences"]:
#                     if evidence["feature_name"] not in existing_feature_names: evidences.append(evidence):

                # 
#                         merged.append(
#                         {
#                         "id": rule_syndrome["id"],
#                         "name": name,
#                         "confidence": confidence,
#                         "evidences": evidences,
#                         "description": llm_syndrome["description"]
#                         or rule_syndrome.get("description", ""),
#                         "category": rule_syndrome.get("category", ""),
#                         }
#                         )

                # LLM
#                         del llm_based_dict[name]
#             else:
                # , 
#                 merged.append(rulesyndrome)

        # LLM
#         for name, llm_syndrome in llm_based_dict.items():
            # LLM
#             llm_syndrome["confidence"] = llm_syndrome["confidence"] * 0.8
#             merged.append(llmsyndrome)

        # 
#             merged.sort(key=lambda x: x["confidence"], reverse=True)

#             return merged

#             async def _assess_constitution(
#             self, fusion_result: diagnosis_pb.FusionResult
#             ) -> diagnosis_pb.ConstitutionAssessment:
#         """"""
            

#             Args: fusion_result: 

#             Returns:
#             ConstitutionAssessment: 
#         """"""
        # 
#             assessment = diagnosis_pb.ConstitutionAssessment()
#             assessment.assessmentid = str(uuid.uuid4())
#             assessment.createdat = int(time.time())

#         try:
            # 

            # 
#             balanced = assessment.constitution_types.add()
#             balanced.typeid = "balanced"
#             balanced.typename = ""
#             balanced.score = 0.7
#             balanced.description = ", , "
#             balanced.isprimary = True

            # 
#             assessment.constitution_types.add()
#             qi_deficiency.typeid = "qi_deficiency"
#             qi_deficiency.typename = ""
#             qi_deficiency.score = 0.4
#             qi_deficiency.description = (
#                 ", , , "
#             )
#             qi_deficiency.isprimary = False

#             return assessment

#         except Exception as e:
#             logger.error(f": {e!s}")
#             return assessment

#     def _calculate_analy_si_s_confidence(_self, _syndrome_s: li_st[dict[_str, Any]]) -> float:
#         """"""
        

#         Arg_s: _syndrome_s: 

#         Return_s: float: 
#         """"""
#         if not _syndrome_s: return 0.0:

        # , 
#             _sum(_s["confidence"] for _s in _syndrome_s)
#             return total_confidence / len(_syndrome_s)

#             a_sync def clo_se(_self):
#         """""""""
#         if _self.model_factory: await _self.model_factory.clo_se():

#             logger.info("")


# 
#             _syndrome_analyzer = None


# def get_syndrome_analyzer():
#     """""""""
#     global _syndrome_analyzer  # noqa: PLW0602
#     if _syndrome_analyzer is None:
#         SyndromeAnalyzer()
#         return _syndrome_analyzer
