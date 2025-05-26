#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
中医辨证分析器
负责基于融合后的特征进行中医辨证分析
"""

import logging
import time
import uuid
import json
from typing import Dict, List, Any, Optional, Tuple
import asyncio

# 导入依赖
from internal.agent.model_factory import get_model_factory
from ..utils.config_loader import get_config
from ..utils.metrics import get_metrics_collector

# 协议导入
from ...api.grpc import four_diagnosis_pb2 as diagnosis_pb

logger = logging.getLogger(__name__)

class SyndromeAnalyzer:
    """中医辨证分析器，负责基于融合后的特征进行中医辨证分析和体质评估"""
    
    def __init__(self, model_factory=None):
        """
        初始化辨证分析器
        
        Args:
            model_factory: 模型工厂实例，如果为None则创建新实例
        """
        self.config = get_config()
        self.metrics = get_metrics_collector()
        
        # 设置模型工厂（将在异步方法中初始化）
        self.model_factory = model_factory
        
        # 加载配置
        differentiation_config = self.config.get_section('differentiation', {})
        
        # 辨证分析配置
        self.rules_version = differentiation_config.get('rules_version', 'v2')
        self.confidence_threshold = differentiation_config.get('confidence_threshold', 0.7)
        self.evidence_requirements = differentiation_config.get('evidence_requirements', 'moderate')
        
        # 加载提示语模板
        self.prompt_templates = self._load_prompt_templates()
        
        # 加载规则库
        self.rules = self._load_differentiation_rules()
        
        logger.info(f"中医辨证分析器初始化完成，规则版本: {self.rules_version}")
    
    async def initialize(self):
        """异步初始化模型工厂"""
        if self.model_factory is None:
            self.model_factory = await get_model_factory()
            logger.info("辨证分析器模型工厂异步初始化完成")
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载提示语模板"""
        prompt_dir = self.config.get_section('paths.prompts', 'config/prompts')
        templates = {}
        
        template_files = {
            'syndrome_differentiation': 'diagnosis_analysis.txt',
            'constitution_assessment': 'constitution_assessment.txt'
        }
        
        for key, filename in template_files.items():
            try:
                with open(f"{prompt_dir}/{filename}", 'r', encoding='utf-8') as f:
                    templates[key] = f.read()
                    logger.debug(f"加载提示语模板 {key} 成功")
            except Exception as e:
                logger.error(f"加载提示语模板 {key} 失败: {str(e)}")
                templates[key] = f"你是小艾智能体中负责{key}的专家。请提供专业分析。"
        
        return templates
    
    def _load_differentiation_rules(self) -> Dict[str, Any]:
        """加载辨证规则库"""
        rules_dir = self.config.get_section('paths.rules', 'config/rules')
        
        try:
            with open(f"{rules_dir}/differentiation_rules_v{self.rules_version[1:]}.json", 'r', encoding='utf-8') as f:
                rules = json.load(f)
                logger.info(f"加载辨证规则库成功，共 {len(rules.get('syndromes', []))} 个证型规则")
                return rules
        except Exception as e:
            logger.error(f"加载辨证规则库失败: {str(e)}，将使用默认规则")
            
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
        start_time = time.time()
        
        try:
            # 创建辨证分析结果
            analysis_result = diagnosis_pb.SyndromeAnalysisResult(
                analysis_id=str(uuid.uuid4()),
                user_id=fusion_result.user_id,
                session_id=fusion_result.session_id,
                created_at=int(time.time()),
                fusion_id=fusion_result.fusion_id
            )
            
            # 获取融合特征
            fused_features = fusion_result.fused_features
            
            # 规则匹配辨证
            rule_based_syndromes = self._match_syndrome_rules(fused_features)
            
            # 使用LLM进行辨证分析
            llm_syndromes = await self._llm_syndrome_analysis(fusion_result)
            
            # 合并辨证结果
            merged_syndromes = self._merge_syndrome_results(rule_based_syndromes, llm_syndromes)
            
            # 添加辨证结果
            for syndrome in merged_syndromes:
                syndrome_pb = analysis_result.syndromes.add()
                syndrome_pb.syndrome_id = syndrome["id"]
                syndrome_pb.syndrome_name = syndrome["name"]
                syndrome_pb.confidence = syndrome["confidence"]
                syndrome_pb.description = syndrome.get("description", "")
                syndrome_pb.category = syndrome.get("category", "")
                
                # 添加证据特征
                for evidence in syndrome.get("evidences", []):
                    ev = syndrome_pb.evidences.add()
                    ev.feature_name = evidence["feature_name"]
                    ev.feature_value = evidence["feature_value"]
                    ev.weight = evidence["weight"]
            
            # 添加体质评估结果
            constitution_assessment = await self._assess_constitution(fusion_result)
            analysis_result.constitution_assessment.CopyFrom(constitution_assessment)
            
            # 设置分析的可信度
            analysis_result.analysis_confidence = self._calculate_analysis_confidence(merged_syndromes)
            
            # 记录成功指标
            process_time = time.time() - start_time
            self.metrics.record_request_time("syndrome_analysis", process_time)
            
            return analysis_result
            
        except Exception as e:
            # 记录错误
            logger.error(f"辨证分析失败: {str(e)}")
            self.metrics.increment_error_count("syndrome_analysis")
            
            # 创建空结果
            empty_result = diagnosis_pb.SyndromeAnalysisResult(
                analysis_id=str(uuid.uuid4()),
                user_id=fusion_result.user_id,
                session_id=fusion_result.session_id,
                created_at=int(time.time()),
                fusion_id=fusion_result.fusion_id,
                analysis_confidence=0.0
            )
            
            return empty_result
    
    def _match_syndrome_rules(self, fused_features: diagnosis_pb.FusedFeatures) -> List[Dict[str, Any]]:
        """
        使用规则库匹配证型
        
        Args:
            fused_features: 融合后的特征
            
        Returns:
            List[Dict[str, Any]]: 匹配的证型列表
        """
        matched_syndromes = []
        
        # 获取规则库中的证型
        syndromes = self.rules.get("syndromes", [])
        if not syndromes:
            logger.warning("规则库中没有证型定义，无法进行规则匹配")
            return matched_syndromes
        
        # 将特征转换为字典格式，便于查询
        features_dict = {}
        for feature in fused_features.features:
            if feature.feature_name not in features_dict:
                features_dict[feature.feature_name] = []
            
            features_dict[feature.feature_name].append({
                "value": feature.feature_value,
                "confidence": feature.confidence,
                "category": feature.category
            })
        
        # 遍历所有证型规则进行匹配
        for syndrome in syndromes:
            syndrome_id = syndrome.get("id", "")
            syndrome_name = syndrome.get("name", "")
            required_features = syndrome.get("required_features", [])
            supporting_features = syndrome.get("supporting_features", [])
            
            # 检查该证型是否满足必要条件
            meets_requirements = True
            evidence_count = 0
            total_weight = 0.0
            confidence_sum = 0.0
            evidences = []
            
            # 检查必要特征
            for req_feature in required_features:
                feature_name = req_feature.get("name", "")
                expected_values = req_feature.get("values", [])
                weight = req_feature.get("weight", 1.0)
                
                # 如果没有这个特征，判断为不满足
                if feature_name not in features_dict:
                    meets_requirements = False
                    break
                
                # 检查特征值是否匹配
                matched = False
                for feature_entry in features_dict[feature_name]:
                    feature_value = feature_entry["value"]
                    confidence = feature_entry["confidence"]
                    
                    if feature_value in expected_values:
                        matched = True
                        evidence_count += 1
                        total_weight += weight
                        confidence_sum += confidence * weight
                        
                        # 添加证据
                        evidences.append({
                            "feature_name": feature_name,
                            "feature_value": feature_value,
                            "weight": weight
                        })
                        break
                
                if not matched:
                    meets_requirements = False
                    break
            
            # 如果不满足必要条件，跳过此证型
            if not meets_requirements:
                continue
            
            # 检查支持性特征
            for sup_feature in supporting_features:
                feature_name = sup_feature.get("name", "")
                expected_values = sup_feature.get("values", [])
                weight = sup_feature.get("weight", 0.5)
                
                # 如果有这个特征，检查值是否匹配
                if feature_name in features_dict:
                    for feature_entry in features_dict[feature_name]:
                        feature_value = feature_entry["value"]
                        confidence = feature_entry["confidence"]
                        
                        if feature_value in expected_values:
                            evidence_count += 1
                            total_weight += weight
                            confidence_sum += confidence * weight
                            
                            # 添加证据
                            evidences.append({
                                "feature_name": feature_name,
                                "feature_value": feature_value,
                                "weight": weight
                            })
                            break
            
            # 计算证型置信度
            confidence = (confidence_sum / total_weight) if total_weight > 0 else 0.0
            
            # 根据匹配的证据数量和要求的严格程度判断
            if self.evidence_requirements == "strict" and evidence_count < len(required_features) + 2:
                continue
            elif self.evidence_requirements == "moderate" and evidence_count < len(required_features):
                continue
            elif self.evidence_requirements == "lenient" and evidence_count < len(required_features) / 2:
                continue
            
            # 如果置信度超过阈值，添加到匹配结果中
            if confidence >= self.confidence_threshold:
                matched_syndromes.append({
                    "id": syndrome_id,
                    "name": syndrome_name,
                    "confidence": confidence,
                    "evidence_count": evidence_count,
                    "total_weight": total_weight,
                    "evidences": evidences,
                    "description": syndrome.get("description", ""),
                    "category": syndrome.get("category", "")
                })
        
        # 按置信度排序
        matched_syndromes.sort(key=lambda x: x["confidence"], reverse=True)
        
        return matched_syndromes
    
    async def _llm_syndrome_analysis(self, fusion_result: diagnosis_pb.FusionResult) -> List[Dict[str, Any]]:
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
            look_data = self._prepare_look_data(fusion_result)
            listen_data = self._prepare_listen_data(fusion_result)
            inquiry_data = self._prepare_inquiry_data(fusion_result)
            palpation_data = self._prepare_palpation_data(fusion_result)
            
            # 获取提示语模板
            template = self.prompt_templates.get("syndrome_differentiation", "")
            if not template:
                logger.error("未找到辨证分析提示语模板")
                return []
            
            # 构建提示语
            prompt = template.format(
                look_data=look_data,
                listen_data=listen_data,
                inquiry_data=inquiry_data,
                palpation_data=palpation_data
            )
            
            # 构建消息列表
            messages = [
                {"role": "system", "content": "你是小艾智能体中的中医辨证专家，负责基于四诊合参进行辨证分析。"},
                {"role": "user", "content": prompt}
            ]
            
            # 调用大模型进行辨证分析
            analysis_result, _ = await self.model_factory.generate_chat_completion(
                model="gpt-4o",
                messages=messages,
                temperature=0.3,
                max_tokens=2048
            )
            
            # 解析分析结果，提取证型
            syndromes = self._parse_syndrome_analysis(analysis_result)
            
            return syndromes
            
        except Exception as e:
            logger.error(f"LLM辨证分析失败: {str(e)}")
            return []
    
    def _prepare_look_data(self, fusion_result: diagnosis_pb.FusionResult) -> str:
        """准备望诊数据文本"""
        look_features = []
        
        for feature in fusion_result.fused_features.features:
            if feature.category == "tongue" or feature.category == "face":
                look_features.append(f"- {feature.feature_name}: {feature.feature_value} (置信度: {feature.confidence:.2f})")
        
        if not look_features:
            return "无望诊数据"
        
        return "\n".join(look_features)
    
    def _prepare_listen_data(self, fusion_result: diagnosis_pb.FusionResult) -> str:
        """准备闻诊数据文本"""
        listen_features = []
        
        for feature in fusion_result.fused_features.features:
            if feature.category == "voice":
                listen_features.append(f"- {feature.feature_name}: {feature.feature_value} (置信度: {feature.confidence:.2f})")
        
        if not listen_features:
            return "无闻诊数据"
        
        return "\n".join(listen_features)
    
    def _prepare_inquiry_data(self, fusion_result: diagnosis_pb.FusionResult) -> str:
        """准备问诊数据文本"""
        inquiry_features = []
        
        for feature in fusion_result.fused_features.features:
            if feature.category == "symptom" or feature.category == "history":
                inquiry_features.append(f"- {feature.feature_name}: {feature.feature_value} (置信度: {feature.confidence:.2f})")
        
        if not inquiry_features:
            return "无问诊数据"
        
        return "\n".join(inquiry_features)
    
    def _prepare_palpation_data(self, fusion_result: diagnosis_pb.FusionResult) -> str:
        """准备切诊数据文本"""
        palpation_features = []
        
        for feature in fusion_result.fused_features.features:
            if feature.category == "pulse":
                palpation_features.append(f"- {feature.feature_name}: {feature.feature_value} (置信度: {feature.confidence:.2f})")
        
        if not palpation_features:
            return "无切诊数据"
        
        return "\n".join(palpation_features)
    
    def _parse_syndrome_analysis(self, analysis_text: str) -> List[Dict[str, Any]]:
        """
        解析辨证分析文本，提取证型
        
        Args:
            analysis_text: 分析文本
            
        Returns:
            List[Dict[str, Any]]: 证型列表
        """
        syndromes = []
        
        try:
            # 提取辨证分析部分
            analysis_section_match = analysis_text.split("## 辨证分析")
            if len(analysis_section_match) < 2:
                logger.warning("未找到辨证分析部分")
                return syndromes
            
            analysis_section = analysis_section_match[1].split("##")[0].strip()
            
            # 提取证型信息
            syndrome_lines = analysis_section.split("\n")
            current_syndrome = None
            
            for line in syndrome_lines:
                line = line.strip()
                
                # 新证型的开始
                if line.startswith("- ") or line.startswith("* "):
                    # 保存上一个证型
                    if current_syndrome:
                        syndromes.append(current_syndrome)
                    
                    # 创建新证型
                    syndrome_text = line[2:].strip()
                    confidence_match = None
                    
                    # 尝试提取置信度
                    if "（" in syndrome_text and "）" in syndrome_text:
                        confidence_text = syndrome_text.split("（")[1].split("）")[0]
                        if "%" in confidence_text:
                            confidence_value = float(confidence_text.replace("%", "")) / 100
                            syndrome_text = syndrome_text.split("（")[0].strip()
                            confidence_match = confidence_value
                    
                    current_syndrome = {
                        "id": str(uuid.uuid4()),
                        "name": syndrome_text,
                        "confidence": confidence_match or 0.8,  # 默认置信度
                        "evidences": [],
                        "description": ""
                    }
                
                # 证型描述或证据
                elif current_syndrome and line and not line.startswith("#"):
                    if ":" in line or "：" in line:
                        # 可能是证据
                        parts = line.replace("：", ":").split(":", 1)
                        if len(parts) == 2:
                            feature_name = parts[0].strip()
                            feature_value = parts[1].strip()
                            
                            current_syndrome["evidences"].append({
                                "feature_name": feature_name,
                                "feature_value": feature_value,
                                "weight": 1.0
                            })
                    else:
                        # 添加到描述
                        if current_syndrome["description"]:
                            current_syndrome["description"] += " " + line
                        else:
                            current_syndrome["description"] = line
            
            # 添加最后一个证型
            if current_syndrome:
                syndromes.append(current_syndrome)
            
            return syndromes
            
        except Exception as e:
            logger.error(f"解析辨证分析文本失败: {str(e)}")
            return syndromes
    
    def _merge_syndrome_results(self, rule_based: List[Dict[str, Any]], llm_based: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        合并规则匹配和LLM分析的证型结果
        
        Args:
            rule_based: 规则匹配的证型
            llm_based: LLM分析的证型
            
        Returns:
            List[Dict[str, Any]]: 合并后的证型列表
        """
        merged = []
        
        # 用于快速查找的字典
        rule_based_dict = {syndrome["name"]: syndrome for syndrome in rule_based}
        llm_based_dict = {syndrome["name"]: syndrome for syndrome in llm_based}
        
        # 处理两种方法都找到的证型
        for name, rule_syndrome in rule_based_dict.items():
            if name in llm_based_dict:
                # 两种方法都找到，合并结果
                llm_syndrome = llm_based_dict[name]
                
                # 计算平均置信度，但规则匹配的权重更高
                confidence = (rule_syndrome["confidence"] * 0.7 + llm_syndrome["confidence"] * 0.3)
                
                # 合并证据
                evidences = rule_syndrome["evidences"].copy()
                
                # 添加LLM特有的证据
                llm_evidence_feature_names = [e["feature_name"] for e in llm_syndrome["evidences"]]
                existing_feature_names = [e["feature_name"] for e in evidences]
                
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
                # 只有规则匹配找到，直接添加
                merged.append(rule_syndrome)
        
        # 添加只有LLM找到的证型
        for name, llm_syndrome in llm_based_dict.items():
            # LLM找到的证型置信度稍低
            llm_syndrome["confidence"] = llm_syndrome["confidence"] * 0.8
            merged.append(llm_syndrome)
        
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
        assessment.assessment_id = str(uuid.uuid4())
        assessment.created_at = int(time.time())
        
        try:
            # TODO: 体质评估逻辑待实现
            # 目前先创建示例结果
            
            # 平和质
            balanced = assessment.constitution_types.add()
            balanced.type_id = "balanced"
            balanced.type_name = "平和质"
            balanced.score = 0.7
            balanced.description = "平和体质是九种体质中最为理想的体质状态，表现为阴阳气血调和，脏腑功能平衡。"
            balanced.is_primary = True
            
            # 气虚质
            qi_deficiency = assessment.constitution_types.add()
            qi_deficiency.type_id = "qi_deficiency"
            qi_deficiency.type_name = "气虚质"
            qi_deficiency.score = 0.4
            qi_deficiency.description = "气虚体质的特点是气虚无力，常表现为疲乏无力，语音低弱，气短懒言等。"
            qi_deficiency.is_primary = False
            
            return assessment
            
        except Exception as e:
            logger.error(f"体质评估失败: {str(e)}")
            return assessment
    
    def _calculate_analysis_confidence(self, syndromes: List[Dict[str, Any]]) -> float:
        """
        计算辨证分析总体置信度
        
        Args:
            syndromes: 证型列表
            
        Returns:
            float: 总体置信度
        """
        if not syndromes:
            return 0.0
        
        # 如果有多个证型，取平均值
        total_confidence = sum(s["confidence"] for s in syndromes)
        return total_confidence / len(syndromes)
    
    async def close(self):
        """关闭资源"""
        if self.model_factory:
            await self.model_factory.close()
        
        logger.info("中医辨证分析器已关闭")

# 单例实例
_syndrome_analyzer = None

def get_syndrome_analyzer():
    """获取辨证分析器单例"""
    global _syndrome_analyzer
    if _syndrome_analyzer is None:
        _syndrome_analyzer = SyndromeAnalyzer()
    return _syndrome_analyzer 