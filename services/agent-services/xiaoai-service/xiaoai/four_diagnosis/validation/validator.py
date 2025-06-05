#!/usr/bin/env python3

# """""""""

import logging

# Proto

logger = logging.getLogger(__name__)


# class DiagnosticValidator:
#     """""""""

#     def __init__(:
#         self,
#         minconfidence_threshold: float = 0.5,
#         minfeatures_count: int = 3,
#         mindiagnostic_services: int = 2,
#         ):
#         """"""
        

#         Args: min_confidence_threshold: 
#             min_features_count: 
#             min_diagnostic_services: 
#         """"""
#         self.minconfidence_threshold = min_confidence_threshold
#         self.minfeatures_count = min_features_count
#         self.mindiagnostic_services = min_diagnostic_services

        # 
#         self.incompatiblesyndromes = {
#             "": ["", ""],
#             "": [""],
#             "": [""],
#             "": [""],
#             "": [""],
#             "": [""],
#             "": [""],
#             "": [""],
#             "": [""],
#         }

        # 
#         self.incompatibleconstitutions = {
#             "": [
#         "",
#         "",
#         "",
#         "",
#         "",
#         "",
#         "",
#         "",
#             ],
#             "": ["", ""],
#             "": ["", ""],
#             "": [""],
#         }

#     def validate_diagnostic_report(:
#         self, report: diagnosis_pb.DiagnosisReport
#         ) -> tuple[bool, str, list[str]]:
#         """"""
        

#         Args:
#             report: 

#         Returns:
            
#         """"""
#         problems = []

        # 
#         sum()
#             [
#         1 if report.HasField("look_result") else 0,
#         1 if report.HasField("listen_result") else 0,
#         1 if report.HasField("inquiry_result") else 0,
#         1 if report.HasField("palpation_result") else 0,
#             ]
#         )

#         if diagnostic_services_count < self.min_diagnostic_services: problems.append(:
#                 f", : {diagnostic_services_count}, : {self.min_diagnostic_services}"
#             )

        # 
#         if report.overall_confidence < self.min_confidence_threshold: problems.append(:
#                 f", : {report.overall_confidence}, : {self.min_confidence_threshold}"
#             )

        # 
#         if report.HasField("syndrome_analysis"):
#             syndromevalid, syndromeproblems = self._validate_syndrome_analysis(
#                 report.syndromeanalysis
#             )
#             problems.extend(syndromeproblems)

        # 
#         if report.HasField("constitution_analysis"):
#             constitutionvalid, constitutionproblems = (
#                 self._validate_constitution_analysis(report.constitutionanalysis)
#             )
#             problems.extend(constitutionproblems)

        # 
#         if len(report.recommendations) > 0:
#             recommendationsvalid, recommendationsproblems = (
#                 self._validate_recommendations(report.recommendations)
#             )
#             problems.extend(recommendationsproblems)

        # 
#             valid = len(problems) == 0
#             message = "" if valid else ""

#             return valid, message, problems

#     def _validate_syndrome_analysis(:
#         self, syndrome_analysis: diagnosis_pb.SyndromeAnalysisResult
#         ) -> tuple[bool, list[str]]:
#         """"""
        

#         Args: syndrome_analysis: 

#         Returns:
            
#         """"""
#         problems = []

        # 
#         if not syndrome_analysis.syndromes:
#             problems.append("")
#             return False, problems

        # 
#         if syndrome_analysis.overall_confidence < self.min_confidence_threshold: problems.append(:
#                 f", : {syndrome_analysis.overall_confidence}, : {self.min_confidence_threshold}"
#             )

        # 
#             syndromes = [s.syndrome_name for s in syndrome_analysis.syndromes]
#             self._check_incompatible_items(syndromes, self.incompatiblesyndromes)

#         for pair in incompatible_pairs: problems.append(f": {pair[0]}{pair[1]}"):

        # 
#             valid = len(problems) == 0

#             return valid, problems

#     def _validate_constitution_analysis(:
#         self, constitution_analysis: diagnosis_pb.ConstitutionAnalysisResult
#         ) -> tuple[bool, list[str]]:
#         """"""
        

#         Args: constitution_analysis: 

#         Returns:
            
#         """"""
#         problems = []

        # 
#         if not constitution_analysis.constitutions:
#             problems.append("")
#             return False, problems

        # 
#         if constitution_analysis.overall_confidence < self.min_confidence_threshold: problems.append(:
#                 f", : {constitution_analysis.overall_confidence}, : {self.min_confidence_threshold}"
#             )

        # 
#             constitutions = [
#             c.constitution_name for c in constitution_analysis.constitutions
#             ]
#             self._check_incompatible_items(constitutions, self.incompatibleconstitutions)

#         for pair in incompatible_pairs: problems.append(f": {pair[0]}{pair[1]}"):

        # , 
#         if "" in constitutions and len(constitutions) > 1:
#             problems.append("")

        # 
#             valid = len(problems) == 0

#             return valid, problems

#     def _validate_recommendations(:
#         self, recommendations: list[diagnosis_pb.RecommendationItem]
#         ) -> tuple[bool, list[str]]:
#         """"""
        

#         Args:
#             recommendations: 

#         Returns:
            
#         """"""
#         problems = []

        # 
#         if not recommendations:
#             problems.append("")
#             return False, problems

        # 
#             {r.type for r in recommendations}

#             expected_types - recommendation_types
#         if missing_types: missingtype_names = [str(t) for t in missing_types]:
#             problems.append(f": {', '.join(missingtype_names)}")

        # 
#         for rec in recommendations:
#             if not rec.content:
#                 problems.append(f": {rec.type}")

#             if not rec.rationale:
#                 problems.append(f": {rec.type}")

#             if not rec.target_issue: problems.append(f": {rec.type}"):

        # 
#                 valid = len(problems) == 0

#                 return valid, problems

#     def _check_incompatible_items(:
#         self, items: list[str], incompatibledict: dict[str, list[str]]
#         ) -> list[tuple[str, str]]:
#         """"""
        

#         Args:
#             items: 
#             incompatible_dict: 

#         Returns:
            
#         """"""

#         for i, item1 in enumerate(items):
#             if item1 in incompatible_dict: for item2 in items[i + 1 :]:
#                     if item2 in incompatible_dict[item1]: incompatible_pairs.append((item1, item2)):

#                         return incompatible_pairs
