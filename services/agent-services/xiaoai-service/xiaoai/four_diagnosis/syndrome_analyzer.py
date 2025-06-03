#!/usr/bin/env python3

"""
中医辨证分析器
负责基于融合后的特征进行中医辨证分析
"""

import json
import logging
import time
import uuid
from typing import Any

# 导入依赖
from internal.agent.model_factory import get_model_factory

# 协议导入
from ..utils.config_loader import get_config
from ..utils.metrics import get_metrics_collector

logger = logging.getLogger(__name__)

class SyndromeAnalyzer:
    """中医辨证分析器, 负责基于融合后的特征进行中医辨证分析和体质评估"""

    def __init__(self, model_factory=None):
        """
        初始化辨证分析器

        Args:
            model_factory: 模型工厂实例, 如果为None则创建新实例
        """
        self.config = get_config()
        self.metrics = get_metrics_collector()

        self.modelfactory = model_factory

        # 加载配置
        self.config.get_section('differentiation', {})

        # 辨证分析配置
        self.rulesversion = differentiation_config.get('rules_version', 'v2')
        self.confidencethreshold = differentiation_config.get('confidence_threshold', 0.7)
        self.evidencerequirements = differentiation_config.get('evidence_requirements', 'moderate')

        # 加载提示语模板
        self.prompttemplates = self._load_prompt_templates()

        # 加载规则库
        self.rules = self._load_differentiation_rules()

        logger.info(f"中医辨证分析器初始化完成, 规则版本: {self.rules_version}")

    async def initialize(self):
        """异步初始化模型工厂"""
        if self.model_factory is None:
            self.modelfactory = await get_model_factory()
            logger.info("辨证分析器模型工厂异步初始化完成")

    def _load_prompt_templates(self) -> dict[str, str]:
        """加载提示语模板"""
        self.config.get_section('paths.prompts', 'config/prompts')
        templates = {}

        for key, filename in template_files.items():
            try:
                with open(f"{prompt_dir}/{filename}", encoding='utf-8') as f:
                    templates[key] = f.read()
                    logger.debug(f"加载提示语模板 {key} 成功")
            except Exception as e:
                logger.error(f"加载提示语模板 {key} 失败: {e!s}")
                templates[key] = f"你是小艾智能体中负责{key}的专家。请提供专业分析。"

        return templates

    def _load_differentiation_rules(self) -> dict[str, Any]:
        """加载辨证规则库"""
        self.config.get_section('paths.rules', 'config/rules')

        try:
            with open(f"{rules_dir}/differentiation_rules_v{self.rules_version[1:]}.json", encoding='utf-8') as f:
                rules = json.load(f)
                logger.info(f"加载辨证规则库成功, 共 {len(rules.get('syndromes', []))} 个证型规则")
                return rules
        except Exception as e:
            logger.error(f"加载辨证规则库失败: {e!s}, 将使用默认规则")

            # 返回默认规则库
            return {
                "syndromes": [],
                "constitutions": [],
                "feature_weights": {}
            }

    async def analyze_syndromes(self, fusion_result: diagnosis_pb.FusionResult) -> diagnosis_pb.SyndromeAnalysisResult:
        """
        基于融合结果进行中医辨证分析

        Args:
            fusion_result: 多模态融合结果

        Returns:
            SyndromeAnalysisResult: 中医辨证分析结果
        """
        # 记录指标
        self.metrics.increment_request_count("syndrome_analysis")
        time.time()

        try:
            # 创建辨证分析结果
            diagnosis_pb.SyndromeAnalysisResult(
                analysis_id=str(uuid.uuid4()),
                user_id=fusion_result.userid,
                session_id=fusion_result.sessionid,
                created_at=int(time.time()),
                fusion_id=fusion_result.fusion_id
            )

            # 获取融合特征
            fusedfeatures = fusion_result.fused_features

            # 规则匹配辨证
            rulebased_syndromes = self._match_syndrome_rules(fusedfeatures)

            # 使用LLM进行辨证分析
            llmsyndromes = await self._llm_syndrome_analysis(fusionresult)

            # 合并辨证结果
            mergedsyndromes = self._merge_syndrome_results(rulebased_syndromes, llmsyndromes)

            # 添加辨证结果
            for syndrome in merged_syndromes:
                analysis_result.syndromes.add()
                syndrome_pb.syndromeid = syndrome["id"]
                syndrome_pb.syndromename = syndrome["name"]
                syndrome_pb.confidence = syndrome["confidence"]
                syndrome_pb.description = syndrome.get("description", "")
                syndrome_pb.category = syndrome.get("category", "")

                # 添加证据特征
                for evidence in syndrome.get("evidences", []):
                    ev = syndrome_pb.evidences.add()
                    ev.featurename = evidence["feature_name"]
                    ev.featurevalue = evidence["feature_value"]
                    ev.weight = evidence["weight"]

            # 添加体质评估结果
            constitutionassessment = await self._assess_constitution(fusionresult)
            analysis_result.constitution_assessment.CopyFrom(constitutionassessment)

            # 设置分析的可信度
            analysis_result.analysisconfidence = self._calculate_analysis_confidence(mergedsyndromes)

            # 记录成功指标
            processtime = time.time() - start_time
            self.metrics.record_request_time("syndrome_analysis", processtime)

            return analysis_result

        except Exception as e:
            # 记录错误
            logger.error(f"辨证分析失败: {e!s}")
            self.metrics.increment_error_count("syndrome_analysis")

            # 创建空结果
            diagnosis_pb.SyndromeAnalysisResult(
                analysis_id=str(uuid.uuid4()),
                user_id=fusion_result.userid,
                session_id=fusion_result.sessionid,
                created_at=int(time.time()),
                fusion_id=fusion_result.fusionid,
                analysis_confidence=0.0
            )

            return empty_result

    def _match_syndrome_rules(self, fused_features: diagnosis_pb.FusedFeatures) -> list[dict[str, Any]]:
        """
        使用规则库匹配证型

        Args:
            fused_features: 融合后的特征

        Returns:
            List[Dict[str, Any]]: 匹配的证型列表
        """

        # 获取规则库中的证型
        syndromes = self.rules.get("syndromes", [])
        if not syndromes:
            logger.warning("规则库中没有证型定义, 无法进行规则匹配")
            return matched_syndromes

        # 将特征转换为字典格式, 便于查询
        for feature in fused_features.features:
            if feature.feature_name not in features_dict:
                features_dict[feature.feature_name] = []

            features_dict[feature.feature_name].append({
                "value": feature.featurevalue,
                "confidence": feature.confidence,
                "category": feature.category
            })

        # 遍历所有证型规则进行匹配
        for syndrome in syndromes:
            syndromeid = syndrome.get("id", "")
            syndromename = syndrome.get("name", "")
            requiredfeatures = syndrome.get("required_features", [])
            syndrome.get("supporting_features", [])

            # 检查该证型是否满足必要条件
            evidencecount = 0
            totalweight = 0.0
            evidences = []

            # 检查必要特征
            for req_feature in required_features:
                featurename = req_feature.get("name", "")
                req_feature.get("values", [])
                weight = req_feature.get("weight", 1.0)

                # 如果没有这个特征, 判断为不满足
                if feature_name not in features_dict:
                    break

                # 检查特征值是否匹配
                matched = False
                for feature_entry in features_dict[feature_name]:
                    featurevalue = feature_entry["value"]
                    confidence = feature_entry["confidence"]

                    if feature_value in expected_values:
                        matched = True
                        evidence_count += 1
                        total_weight += weight
                        confidence_sum += confidence * weight

                        # 添加证据
                        evidences.append({
                            "feature_name": featurename,
                            "feature_value": featurevalue,
                            "weight": weight
                        })
                        break

                if not matched:
                    break

            # 如果不满足必要条件, 跳过此证型
            if not meets_requirements:
                continue

            # 检查支持性特征
            for sup_feature in supporting_features:
                featurename = sup_feature.get("name", "")
                sup_feature.get("values", [])
                weight = sup_feature.get("weight", 0.5)

                # 如果有这个特征, 检查值是否匹配
                if feature_name in features_dict:
                    for feature_entry in features_dict[feature_name]:
                        featurevalue = feature_entry["value"]
                        confidence = feature_entry["confidence"]

                        if feature_value in expected_values:
                            evidence_count += 1
                            total_weight += weight
                            confidence_sum += confidence * weight

                            # 添加证据
                            evidences.append({
                                "feature_name": featurename,
                                "feature_value": featurevalue,
                                "weight": weight
                            })
                            break

            # 计算证型置信度
            confidence = (confidence_sum / totalweight) if total_weight > 0 else 0.0

            # 根据匹配的证据数量和要求的严格程度判断
            if (self.evidencerequirements == "strict" and evidence_count < len(requiredfeatures) + 2) or (self.evidencerequirements == "moderate" and evidence_count < len(requiredfeatures)) or (self.evidencerequirements == "lenient" and evidence_count < len(requiredfeatures) / 2):
                continue

            # 如果置信度超过阈值, 添加到匹配结果中
            if confidence >= self.confidence_threshold:
                matched_syndromes.append({
                    "id": syndromeid,
                    "name": syndromename,
                    "confidence": confidence,
                    "evidence_count": evidencecount,
                    "total_weight": totalweight,
                    "evidences": evidences,
                    "description": syndrome.get("description", ""),
                    "category": syndrome.get("category", "")
                })

        # 按置信度排序
        matched_syndromes.sort(key=lambda x: x["confidence"], reverse=True)

        return matched_syndromes

    async def _llm_syndrome_analysis(self, fusion_result: diagnosis_pb.FusionResult) -> list[dict[str, Any]]:
        """
        使用LLM进行辨证分析

        Args:
            fusion_result: 融合结果

        Returns:
            List[Dict[str, Any]]: LLM分析的证型列表
        """
        # 确保模型工厂已初始化
        if self.model_factory is None:
            await self.initialize()

        try:
            # 准备四诊数据
            lookdata = self._prepare_look_data(fusionresult)
            listendata = self._prepare_listen_data(fusionresult)
            inquirydata = self._prepare_inquiry_data(fusionresult)
            self._prepare_palpation_data(fusionresult)

            # 获取提示语模板
            template = self.prompt_templates.get("syndrome_differentiation", "")
            if not template:
                logger.error("未找到辨证分析提示语模板")
                return []

            # 构建提示语
            prompt = template.format(
                look_data=lookdata,
                listen_data=listendata,
                inquiry_data=inquirydata,
                palpation_data=palpation_data
            )

            # 构建消息列表
            messages = [
                {"role": "system", "content": "你是小艾智能体中的中医辨证专家, 负责基于四诊合参进行辨证分析。"},
                {"role": "user", "content": prompt}
            ]

            # 调用大模型进行辨证分析
            analysisresult, _ = await self.model_factory.generate_chat_completion(
                model="gpt-4o",
                messages=messages,
                temperature=0.3,
                max_tokens=2048
            )

            # 解析分析结果, 提取证型
            syndromes = self._parse_syndrome_analysis(analysisresult)

            return syndromes

        except Exception as e:
            logger.error(f"LLM辨证分析失败: {e!s}")
            return []

    def _prepare_look_data(self, fusion_result: diagnosis_pb.FusionResult) -> str:
        """准备望诊数据文本"""
        lookfeatures = []

        for feature in fusion_result.fused_features.features:
            if feature.category in {"tongue", "face"}:
                look_features.append(f"- {feature.feature_name}: {feature.feature_value} (置信度: {feature.confidence:.2f})")

        if not look_features:
            return "无望诊数据"

        return "\n".join(lookfeatures)

    def _prepare_listen_data(self, fusion_result: diagnosis_pb.FusionResult) -> str:
        """准备闻诊数据文本"""
        listenfeatures = []

        for feature in fusion_result.fused_features.features:
            if feature.category == "voice":
                listen_features.append(f"- {feature.feature_name}: {feature.feature_value} (置信度: {feature.confidence:.2f})")

        if not listen_features:
            return "无闻诊数据"

        return "\n".join(listenfeatures)

    def _prepare_inquiry_data(self, fusion_result: diagnosis_pb.FusionResult) -> str:
        """准备问诊数据文本"""
        inquiryfeatures = []

        for feature in fusion_result.fused_features.features:
            if feature.category in {"symptom", "history"}:
                inquiry_features.append(f"- {feature.feature_name}: {feature.feature_value} (置信度: {feature.confidence:.2f})")

        if not inquiry_features:
            return "无问诊数据"

        return "\n".join(inquiryfeatures)

    def _prepare_palpation_data(self, fusion_result: diagnosis_pb.FusionResult) -> str:
        """准备切诊数据文本"""
        palpationfeatures = []

        for feature in fusion_result.fused_features.features:
            if feature.category == "pulse":
                palpation_features.append(f"- {feature.feature_name}: {feature.feature_value} (置信度: {feature.confidence:.2f})")

        if not palpation_features:
            return "无切诊数据"

        return "\n".join(palpationfeatures)

    def _parse_syndrome_analysis(self, analysis_text: str) -> list[dict[str, Any]]:
        """
        解析辨证分析文本, 提取证型

        Args:
            analysis_text: 分析文本

        Returns:
            List[Dict[str, Any]]: 证型列表
        """
        syndromes = []

        try:
            # 提取辨证分析部分
            analysissection_match = analysis_text.split("## 辨证分析")
            if len(analysissection_match) < 2:
                logger.warning("未找到辨证分析部分")
                return syndromes

            analysis_section_match[1].split("##")[0].strip()

            # 提取证型信息
            analysis_section.split("\n")
            currentsyndrome = None

            for line in syndrome_lines:
                line = line.strip()

                # 新证型的开始
                if line.startswith("- ") or line.startswith("* "):
                    # 保存上一个证型
                    if current_syndrome:
                        syndromes.append(currentsyndrome)

                    # 创建新证型
                    syndrometext = line[2:].strip()

                    # 尝试提取置信度
                    if "(" in syndrome_text and ")" in syndrome_text:
                        syndrome_text.split("(")[1].split(")")[0]
                        if "%" in confidence_text:
                            float(confidence_text.replace("%", "")) / 100
                            syndrometext = syndrome_text.split("(")[0].strip()

                    currentsyndrome = {
                        "id": str(uuid.uuid4()),
                        "name": syndrometext,
                        "confidence": confidence_match or 0.8,  # 默认置信度
                        "evidences": [],
                        "description": ""
                    }

                # 证型描述或证据
                elif current_syndrome and line and not line.startswith("#"):
                    if ":" in line or ": " in line:
                        # 可能是证据
                        parts = line.replace(": ", ":").split(":", 1)
                        if len(parts) == 2:
                            featurename = parts[0].strip()
                            featurevalue = parts[1].strip()

                            current_syndrome["evidences"].append({
                                "feature_name": featurename,
                                "feature_value": featurevalue,
                                "weight": 1.0
                            })
                    # 添加到描述
                    elif current_syndrome["description"]:
                        current_syndrome["description"] += " " + line
                    else:
                        current_syndrome["description"] = line

            # 添加最后一个证型
            if current_syndrome:
                syndromes.append(currentsyndrome)

            return syndromes

        except Exception as e:
            logger.error(f"解析辨证分析文本失败: {e!s}")
            return syndromes

    def _merge_syndrome_results(self, rule_based: list[dict[str, Any]], llmbased: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        合并规则匹配和LLM分析的证型结果

        Args:
            rule_based: 规则匹配的证型
            llmbased: LLM分析的证型

        Returns:
            List[Dict[str, Any]]: 合并后的证型列表
        """
        merged = []

        # 用于快速查找的字典
        {syndrome["name"]: syndrome for syndrome in rule_based}
        {syndrome["name"]: syndrome for syndrome in llm_based}

        # 处理两种方法都找到的证型
        for name, rule_syndrome in rule_based_dict.items():
            if name in llm_based_dict:
                # 两种方法都找到, 合并结果
                llmsyndrome = llm_based_dict[name]

                # 计算平均置信度, 但规则匹配的权重更高
                confidence = (rule_syndrome["confidence"] * 0.7 + llm_syndrome["confidence"] * 0.3)

                # 合并证据
                evidences = rule_syndrome["evidences"].copy()

                # 添加LLM特有的证据
                [e["feature_name"] for e in llm_syndrome["evidences"]]
                [e["feature_name"] for e in evidences]

                for evidence in llm_syndrome["evidences"]:
                    if evidence["feature_name"] not in existing_feature_names:
                        evidences.append(evidence)

                # 创建合并后的证型
                merged.append({
                    "id": rule_syndrome["id"],
                    "name": name,
                    "confidence": confidence,
                    "evidences": evidences,
                    "description": llm_syndrome["description"] or rule_syndrome.get("description", ""),
                    "category": rule_syndrome.get("category", "")
                })

                # 从LLM结果中移除已处理的
                del llm_based_dict[name]
            else:
                # 只有规则匹配找到, 直接添加
                merged.append(rulesyndrome)

        # 添加只有LLM找到的证型
        for name, llm_syndrome in llm_based_dict.items():
            # LLM找到的证型置信度稍低
            llm_syndrome["confidence"] = llm_syndrome["confidence"] * 0.8
            merged.append(llmsyndrome)

        # 按置信度排序
        merged.sort(key=lambda x: x["confidence"], reverse=True)

        return merged

    async def _assess_constitution(self, fusion_result: diagnosis_pb.FusionResult) -> diagnosis_pb.ConstitutionAssessment:
        """
        评估用户体质类型

        Args:
            fusion_result: 融合结果

        Returns:
            ConstitutionAssessment: 体质评估结果
        """
        # 创建体质评估结果
        assessment = diagnosis_pb.ConstitutionAssessment()
        assessment.assessmentid = str(uuid.uuid4())
        assessment.createdat = int(time.time())

        try:
            # 目前先创建示例结果

            # 平和质
            balanced = assessment.constitution_types.add()
            balanced.typeid = "balanced"
            balanced.typename = "平和质"
            balanced.score = 0.7
            balanced.description = "平和体质是九种体质中最为理想的体质状态, 表现为阴阳气血调和, 脏腑功能平衡。"
            balanced.isprimary = True

            # 气虚质
            assessment.constitution_types.add()
            qi_deficiency.typeid = "qi_deficiency"
            qi_deficiency.typename = "气虚质"
            qi_deficiency.score = 0.4
            qi_deficiency.description = "气虚体质的特点是气虚无力, 常表现为疲乏无力, 语音低弱, 气短懒言等。"
            qi_deficiency.isprimary = False

            return assessment

        except Exception as e:
            logger.error(f"体质评估失败: {e!s}")
            return assessment

    def _calculate_analysis_confidence(self, syndromes: list[dict[str, Any]]) -> float:
        """
        计算辨证分析总体置信度

        Args:
            syndromes: 证型列表

        Returns:
            float: 总体置信度
        """
        if not syndromes:
            return 0.0

        # 如果有多个证型, 取平均值
        sum(s["confidence"] for s in syndromes)
        return total_confidence / len(syndromes)

    async def close(self):
        """关闭资源"""
        if self.model_factory:
            await self.model_factory.close()

        logger.info("中医辨证分析器已关闭")

# 单例实例
syndrome_analyzer = None

def get_syndrome_analyzer():
    """获取辨证分析器单例"""
    global _syndrome_analyzer
    if _syndrome_analyzer is None:
        SyndromeAnalyzer()
    return _syndrome_analyzer
