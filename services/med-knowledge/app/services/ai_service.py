"""
ai_service - 索克生活项目模块
"""

from app.core.logger import get_logger
from app.models.entities import (
from app.services.cache_service import CacheService, CacheKeys
from app.services.knowledge_graph_service import KnowledgeGraphService
from app.services.knowledge_service import KnowledgeService
from app.services.metrics_service import MetricsService, monitor_performance
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import asyncio
import hashlib
import json

"""
AI服务
提供智能推理、多模态数据处理和知识增强功能
"""


    Constitution, Symptom, Syndrome, Herb, Acupoint,
    RecommendationListResponse, SearchResponse
)

logger = get_logger()


class AIService:
    """AI智能服务"""

    def __init__(
        self,
        knowledge_service: KnowledgeService,
        graph_service: KnowledgeGraphService,
        cache_service: Optional[CacheService] = None,
        metrics_service: Optional[MetricsService] = None,
    ):
        self.knowledge_service = knowledge_service
        self.graph_service = graph_service
        self.cache_service = cache_service
        self.metrics_service = metrics_service

    @monitor_performance()
    async def intelligent_diagnosis(
        self,
        symptoms: List[Dict[str, Any]],
        patient_info: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """智能诊断推理"""
        try:
            # 生成诊断缓存键
            diagnosis_key = self._generate_diagnosis_cache_key(symptoms, patient_info)
            
            # 尝试从缓存获取
            if self.cache_service:
                cached_result = await self.cache_service.get(diagnosis_key)
                if cached_result:
                    if self.metrics_service:
                        self.metrics_service.record_cache_operation("get", "hit")
                    return cached_result

            # 执行智能诊断
            diagnosis_result = await self._perform_intelligent_diagnosis(
                symptoms, patient_info, context
            )

            # 缓存结果
            if self.cache_service:
                await self.cache_service.set(diagnosis_key, diagnosis_result, ttl=1800)

            if self.metrics_service:
                self.metrics_service.record_knowledge_request("ai", "intelligent_diagnosis")

            return diagnosis_result

        except Exception as e:
            logger.error(f"智能诊断失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "diagnosis": None,
                "confidence": 0.0,
                "reasoning": []
            }

    @monitor_performance()
    async def multimodal_analysis(
        self,
        text_data: Optional[str] = None,
        image_data: Optional[bytes] = None,
        audio_data: Optional[bytes] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """多模态数据分析"""
        try:
            analysis_results = {}
            
            # 文本分析
            if text_data:
                text_analysis = await self._analyze_text_data(text_data, context)
                analysis_results["text"] = text_analysis
            
            # 图像分析（舌诊、面诊等）
            if image_data:
                image_analysis = await self._analyze_image_data(image_data, context)
                analysis_results["image"] = image_analysis
            
            # 音频分析（声音诊断）
            if audio_data:
                audio_analysis = await self._analyze_audio_data(audio_data, context)
                analysis_results["audio"] = audio_analysis
            
            # 多模态融合
            fusion_result = await self._fuse_multimodal_results(analysis_results, context)
            
            if self.metrics_service:
                self.metrics_service.record_knowledge_request("ai", "multimodal_analysis")
            
            return {
                "success": True,
                "individual_results": analysis_results,
                "fusion_result": fusion_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"多模态分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "individual_results": {},
                "fusion_result": None
            }

    @monitor_performance()
    async def knowledge_enhanced_rag(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """知识增强的检索增强生成"""
        try:
            # 生成查询缓存键
            rag_key = f"rag:{hashlib.md5(query.encode()).hexdigest()}"
            
            # 尝试从缓存获取
            if self.cache_service:
                cached_result = await self.cache_service.get(rag_key)
                if cached_result:
                    if self.metrics_service:
                        self.metrics_service.record_cache_operation("get", "hit")
                    return cached_result
            
            # 执行知识检索
            retrieval_results = await self._enhanced_knowledge_retrieval(query, context, max_results)
            
            # 生成增强回答
            generated_response = await self._generate_enhanced_response(
                query, retrieval_results, context
            )
            
            result = {
                "success": True,
                "query": query,
                "retrieval_results": retrieval_results,
                "generated_response": generated_response,
                "timestamp": datetime.now().isoformat()
            }
            
            # 缓存结果
            if self.cache_service:
                await self.cache_service.set(rag_key, result, ttl=3600)
            
            if self.metrics_service:
                self.metrics_service.record_knowledge_request("ai", "knowledge_rag")
            
            return result
            
        except Exception as e:
            logger.error(f"知识增强RAG失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "retrieval_results": [],
                "generated_response": None
            }

    # 核心AI功能实现
    async def _perform_intelligent_diagnosis(
        self,
        symptoms: List[Dict[str, Any]],
        patient_info: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行智能诊断推理"""
        
        # 1. 症状分析和权重计算
        symptom_analysis = await self._analyze_symptoms(symptoms)
        
        # 2. 体质分析
        constitution_analysis = await self._analyze_constitution(patient_info)
        
        # 3. 证型推理
        syndrome_inference = await self._infer_syndromes(
            symptom_analysis, constitution_analysis, context
        )
        
        # 4. 知识图谱路径分析
        graph_analysis = await self._analyze_knowledge_paths(
            symptom_analysis, syndrome_inference
        )
        
        # 5. 综合诊断推理
        final_diagnosis = await self._synthesize_diagnosis(
            symptom_analysis, constitution_analysis, syndrome_inference, graph_analysis
        )
        
        return {
            "success": True,
            "diagnosis": final_diagnosis,
            "confidence": final_diagnosis.get("confidence", 0.0),
            "reasoning": final_diagnosis.get("reasoning", []),
            "symptom_analysis": symptom_analysis,
            "constitution_analysis": constitution_analysis,
            "syndrome_inference": syndrome_inference,
            "graph_analysis": graph_analysis,
            "timestamp": datetime.now().isoformat()
        }

    async def _analyze_symptoms(self, symptoms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析症状"""
        symptom_scores = {}
        total_severity = 0
        
        for symptom in symptoms:
            name = symptom.get("name", "")
            severity = symptom.get("severity", 1)
            duration = symptom.get("duration", "")
            
            # 计算症状权重
            weight = self._calculate_symptom_weight(severity, duration)
            symptom_scores[name] = {
                "severity": severity,
                "duration": duration,
                "weight": weight,
                "normalized_score": weight * severity
            }
            total_severity += weight * severity
        
        # 获取相关证型
        related_syndromes = await self._get_syndromes_by_symptoms(list(symptom_scores.keys()))
        
        return {
            "symptoms": symptom_scores,
            "total_severity": total_severity,
            "symptom_count": len(symptoms),
            "related_syndromes": related_syndromes,
            "primary_symptoms": self._identify_primary_symptoms(symptom_scores)
        }

    async def _analyze_constitution(self, patient_info: Dict[str, Any]) -> Dict[str, Any]:
        """分析体质"""
        constitution_type = patient_info.get("constitution_type")
        age = patient_info.get("age", 0)
        gender = patient_info.get("gender", "unknown")
        
        constitution_data = None
        if constitution_type:
            constitution_data = await self.knowledge_service.get_constitution_by_id(constitution_type)
        
        # 体质倾向性分析
        constitution_tendencies = await self._analyze_constitution_tendencies(
            constitution_type, age, gender
        )
        
        return {
            "constitution_type": constitution_type,
            "constitution_data": constitution_data.model_dump() if constitution_data else None,
            "age_group": self._categorize_age(age),
            "gender": gender,
            "tendencies": constitution_tendencies,
            "risk_factors": self._identify_risk_factors(constitution_type, age, gender)
        }

    # 辅助方法
    def _generate_diagnosis_cache_key(self, symptoms: List[Dict[str, Any]], patient_info: Dict[str, Any]) -> str:
        """生成诊断缓存键"""
        key_data = {
            "symptoms": sorted([s.get("name", "") for s in symptoms]),
            "constitution": patient_info.get("constitution_type", ""),
            "age": patient_info.get("age", 0),
            "gender": patient_info.get("gender", "")
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return f"ai_diagnosis:{hashlib.md5(key_string.encode()).hexdigest()}"

    def _calculate_symptom_weight(self, severity: int, duration: str) -> float:
        """计算症状权重"""
        base_weight = severity / 5.0  # 标准化到0-1
        
        # 持续时间权重
        duration_weights = {
            "急性": 1.2, "亚急性": 1.0, "慢性": 0.8,
            "1天": 1.1, "1周": 1.0, "1月": 0.9, "3月": 0.8, "半年": 0.7, "1年": 0.6
        }
        
        duration_weight = 1.0
        for key, weight in duration_weights.items():
            if key in duration:
                duration_weight = weight
                break
        
        return min(base_weight * duration_weight, 1.0)

    def _identify_primary_symptoms(self, symptom_scores: Dict[str, Any]) -> List[str]:
        """识别主要症状"""
        sorted_symptoms = sorted(
            symptom_scores.items(),
            key=lambda x: x[1]["normalized_score"],
            reverse=True
        )
        return [symptom[0] for symptom in sorted_symptoms[:3]]

    def _categorize_age(self, age: int) -> str:
        """年龄分组"""
        if age < 18:
            return "儿童"
        elif age < 35:
            return "青年"
        elif age < 60:
            return "中年"
        else:
            return "老年"

    # 模拟AI模型调用的方法
    async def _get_syndromes_by_symptoms(self, symptom_names: List[str]) -> List[Dict[str, Any]]:
        """根据症状获取相关证型"""
        return [
            {"id": "syndrome_001", "name": "肝郁脾虚证", "relevance_score": 0.8},
            {"id": "syndrome_002", "name": "气血两虚证", "relevance_score": 0.6},
            {"id": "syndrome_003", "name": "肾阳虚证", "relevance_score": 0.4}
        ]

    async def _analyze_constitution_tendencies(self, constitution_type: str, age: int, gender: str) -> Dict[str, Any]:
        """分析体质倾向性"""
        return {
            "disease_tendency": ["脾胃疾病", "情志疾病"],
            "seasonal_sensitivity": ["春季", "秋季"],
            "lifestyle_recommendations": ["规律作息", "适量运动"]
        }

    def _identify_risk_factors(self, constitution_type: str, age: int, gender: str) -> List[str]:
        """识别风险因素"""
        return ["工作压力大", "饮食不规律", "缺乏运动"]

    async def _analyze_text_data(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """分析文本数据"""
        keywords = self._extract_medical_keywords(text)
        sentiment = self._analyze_sentiment(text)
        entities = await self._extract_medical_entities(text)
        
        return {
            "keywords": keywords,
            "sentiment": sentiment,
            "entities": entities,
            "text_length": len(text),
            "confidence": 0.85
        }

    async def _analyze_image_data(self, image_data: bytes, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """分析图像数据（舌诊、面诊等）"""
        image_type = context.get("image_type", "unknown") if context else "unknown"
        
        if image_type == "tongue":
            return await self._analyze_tongue_image(image_data)
        elif image_type == "face":
            return await self._analyze_face_image(image_data)
        else:
            return await self._analyze_general_medical_image(image_data)

    async def _analyze_audio_data(self, audio_data: bytes, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """分析音频数据（声音诊断）"""
        return {
            "voice_quality": "正常",
            "speech_rate": "适中",
            "tone_analysis": {"pitch": "中等", "volume": "正常"},
            "health_indicators": ["声音清晰", "无明显异常"],
            "confidence": 0.75
        }

    async def _fuse_multimodal_results(
        self, results: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """融合多模态分析结果"""
        fusion_confidence = 0.0
        fusion_insights = []
        combined_entities = []
        
        # 文本结果融合
        if "text" in results:
            text_result = results["text"]
            fusion_confidence += text_result.get("confidence", 0.0) * 0.4
            combined_entities.extend(text_result.get("entities", []))
            fusion_insights.append("文本分析提供了症状和病史信息")
        
        # 图像结果融合
        if "image" in results:
            image_result = results["image"]
            fusion_confidence += image_result.get("confidence", 0.0) * 0.4
            fusion_insights.append("图像分析提供了客观体征信息")
        
        # 音频结果融合
        if "audio" in results:
            audio_result = results["audio"]
            fusion_confidence += audio_result.get("confidence", 0.0) * 0.2
            fusion_insights.append("音频分析提供了声音特征信息")
        
        return {
            "fusion_confidence": min(fusion_confidence, 1.0),
            "fusion_insights": fusion_insights,
            "combined_entities": combined_entities,
            "recommendation": "建议结合多模态信息进行综合诊断"
        }

    async def _enhanced_knowledge_retrieval(
        self, query: str, context: Optional[Dict[str, Any]], max_results: int
    ) -> List[Dict[str, Any]]:
        """增强知识检索"""
        # 基础知识搜索
        search_results = await self.knowledge_service.search_knowledge(
            query, None, max_results, 0
        )
        
        # 图谱相关实体检索
        graph_entities = await self._retrieve_graph_entities(query, context)
        
        # 语义相似度检索
        semantic_results = await self._semantic_similarity_search(query, max_results)
        
        # 结果融合和排序
        combined_results = self._combine_and_rank_results(
            search_results.data if hasattr(search_results, 'data') else [],
            graph_entities,
            semantic_results
        )
        
        return combined_results[:max_results]

    async def _generate_enhanced_response(
        self,
        query: str,
        retrieval_results: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """生成增强回答"""
        query_intent = self._analyze_query_intent(query)
        
        if query_intent == "diagnosis":
            response = await self._generate_diagnosis_response(query, retrieval_results, context)
        elif query_intent == "treatment":
            response = await self._generate_treatment_response(query, retrieval_results, context)
        elif query_intent == "knowledge":
            response = await self._generate_knowledge_response(query, retrieval_results, context)
        else:
            response = await self._generate_general_response(query, retrieval_results, context)
        
        return {
            "intent": query_intent,
            "response": response,
            "confidence": response.get("confidence", 0.8),
            "sources": [result.get("id", "") for result in retrieval_results],
            "reasoning": response.get("reasoning", [])
        }

    def _analyze_query_intent(self, query: str) -> str:
        """分析查询意图"""
        diagnosis_keywords = ["诊断", "症状", "病因", "什么病"]
        treatment_keywords = ["治疗", "用药", "方剂", "怎么治"]
        knowledge_keywords = ["什么是", "介绍", "原理", "机制"]
        
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in diagnosis_keywords):
            return "diagnosis"
        elif any(keyword in query_lower for keyword in treatment_keywords):
            return "treatment"
        elif any(keyword in query_lower for keyword in knowledge_keywords):
            return "knowledge"
        else:
            return "general"

    # 更多辅助方法
    def _extract_medical_keywords(self, text: str) -> List[str]:
        """提取医学关键词"""
        return ["头痛", "乏力", "失眠", "食欲不振"]

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """分析情感倾向"""
        return {"polarity": "neutral", "confidence": 0.7}

    async def _extract_medical_entities(self, text: str) -> List[Dict[str, Any]]:
        """提取医学实体"""
        return [
            {"entity": "头痛", "type": "symptom", "confidence": 0.9},
            {"entity": "失眠", "type": "symptom", "confidence": 0.8}
        ]

    async def _analyze_tongue_image(self, image_data: bytes) -> Dict[str, Any]:
        """分析舌诊图像"""
        return {
            "tongue_color": "淡红",
            "tongue_coating": "薄白",
            "tongue_shape": "正常",
            "health_indicators": ["脾胃功能正常", "无明显热象"],
            "confidence": 0.82
        }

    async def _analyze_face_image(self, image_data: bytes) -> Dict[str, Any]:
        """分析面诊图像"""
        return {
            "complexion": "微黄",
            "facial_features": "正常",
            "health_indicators": ["可能存在脾虚", "气血略虚"],
            "confidence": 0.75
        }

    async def _analyze_general_medical_image(self, image_data: bytes) -> Dict[str, Any]:
        """分析一般医学图像"""
        return {
            "image_type": "unknown",
            "features": [],
            "health_indicators": [],
            "confidence": 0.5
        }

    async def _retrieve_graph_entities(self, query: str, context: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """检索图谱实体"""
        return []

    async def _semantic_similarity_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """语义相似度搜索"""
        return []

    def _combine_and_rank_results(self, *result_lists) -> List[Dict[str, Any]]:
        """合并和排序结果"""
        combined = []
        for results in result_lists:
            if isinstance(results, list):
                combined.extend(results)
        return combined

    async def _generate_diagnosis_response(self, query: str, results: List[Dict[str, Any]], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """生成诊断回答"""
        return {
            "response": "基于症状分析，建议进一步检查以确定具体证型。",
            "confidence": 0.8,
            "reasoning": ["症状分析", "证型推理", "知识图谱验证"]
        }

    async def _generate_treatment_response(self, query: str, results: List[Dict[str, Any]], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """生成治疗回答"""
        return {
            "response": "建议采用中西医结合治疗方案，包括中药调理和生活方式干预。",
            "confidence": 0.85,
            "reasoning": ["治疗原则", "方药选择", "生活指导"]
        }

    async def _generate_knowledge_response(self, query: str, results: List[Dict[str, Any]], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """生成知识回答"""
        return {
            "response": "根据中医理论和现代研究，该概念具有重要的临床意义。",
            "confidence": 0.9,
            "reasoning": ["理论基础", "临床应用", "现代研究"]
        }

    async def _generate_general_response(self, query: str, results: List[Dict[str, Any]], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """生成一般回答"""
        return {
            "response": "根据检索到的知识，为您提供以下信息。",
            "confidence": 0.7,
            "reasoning": ["知识检索", "信息整合"]
        }

    # 需要实现的其他核心方法
    async def _infer_syndromes(
        self,
        symptom_analysis: Dict[str, Any],
        constitution_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """推理证型"""
        symptom_syndromes = symptom_analysis.get("related_syndromes", [])
        constitution_syndromes = await self._get_constitution_syndromes(
            constitution_analysis.get("constitution_type")
        )
        
        syndrome_scores = {}
        for syndrome in symptom_syndromes:
            syndrome_id = syndrome.get("id", "")
            base_score = syndrome.get("relevance_score", 0.5)
            
            constitution_bonus = 0.0
            if syndrome_id in [s.get("id", "") for s in constitution_syndromes]:
                constitution_bonus = 0.2
            
            severity_factor = min(symptom_analysis.get("total_severity", 0) / 10.0, 1.0)
            final_score = min((base_score + constitution_bonus) * (1 + severity_factor), 1.0)
            
            syndrome_scores[syndrome_id] = {
                "syndrome": syndrome,
                "base_score": base_score,
                "constitution_bonus": constitution_bonus,
                "severity_factor": severity_factor,
                "final_score": final_score
            }
        
        sorted_syndromes = sorted(
            syndrome_scores.items(),
            key=lambda x: x[1]["final_score"],
            reverse=True
        )
        
        return {
            "candidate_syndromes": syndrome_scores,
            "top_syndromes": sorted_syndromes[:3],
            "primary_syndrome": sorted_syndromes[0] if sorted_syndromes else None,
            "confidence": sorted_syndromes[0][1]["final_score"] if sorted_syndromes else 0.0
        }

    async def _analyze_knowledge_paths(
        self,
        symptom_analysis: Dict[str, Any],
        syndrome_inference: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析知识图谱路径"""
        primary_symptoms = symptom_analysis.get("primary_symptoms", [])
        primary_syndrome = syndrome_inference.get("primary_syndrome")
        
        if not primary_syndrome:
            return {"paths": [], "insights": []}
        
        syndrome_id = primary_syndrome[0]
        paths = []
        insights = []
        
        for symptom_name in primary_symptoms:
            try:
                path_data = await self.graph_service.find_paths(
                    f"symptom_{symptom_name}", syndrome_id, max_depth=3
                )
                if path_data:
                    paths.extend(path_data)
                    insights.append(f"症状'{symptom_name}'通过{len(path_data)}条路径关联到证型")
            except Exception as e:
                logger.warning(f"查找路径失败 {symptom_name} -> {syndrome_id}: {e}")
        
        return {
            "paths": paths,
            "insights": insights,
            "path_count": len(paths),
            "connectivity_score": min(len(paths) / len(primary_symptoms), 1.0) if primary_symptoms else 0.0
        }

    async def _synthesize_diagnosis(
        self,
        symptom_analysis: Dict[str, Any],
        constitution_analysis: Dict[str, Any],
        syndrome_inference: Dict[str, Any],
        graph_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """综合诊断推理"""
        primary_syndrome = syndrome_inference.get("primary_syndrome")
        if not primary_syndrome:
            return {
                "syndrome": None,
                "confidence": 0.0,
                "reasoning": ["无法确定主要证型"],
                "recommendations": []
            }
        
        syndrome_id, syndrome_data = primary_syndrome
        base_confidence = syndrome_data["final_score"]
        
        graph_bonus = graph_analysis.get("connectivity_score", 0.0) * 0.1
        symptom_consistency = self._calculate_symptom_consistency(
            symptom_analysis, syndrome_data["syndrome"]
        )
        
        final_confidence = min(base_confidence + graph_bonus + symptom_consistency, 1.0)
        
        reasoning = [
            f"基于症状分析，识别出{len(symptom_analysis['symptoms'])}个症状",
            f"体质类型：{constitution_analysis.get('constitution_type', '未知')}",
            f"主要证型：{syndrome_data['syndrome'].get('name', '未知')}",
            f"证型置信度：{base_confidence:.2f}",
            f"知识图谱连通性：{graph_analysis.get('connectivity_score', 0.0):.2f}",
            f"最终诊断置信度：{final_confidence:.2f}"
        ]
        
        recommendations = await self._generate_treatment_recommendations(
            syndrome_id, constitution_analysis.get("constitution_type")
        )
        
        return {
            "syndrome": syndrome_data["syndrome"],
            "confidence": final_confidence,
            "reasoning": reasoning,
            "recommendations": recommendations,
            "differential_diagnosis": syndrome_inference.get("top_syndromes", [])[:3]
        }

    async def _get_constitution_syndromes(self, constitution_type: str) -> List[Dict[str, Any]]:
        """获取体质相关证型"""
        return [
            {"id": "syndrome_001", "name": "肝郁脾虚证", "relevance": 0.9},
            {"id": "syndrome_004", "name": "脾气虚证", "relevance": 0.7}
        ]

    def _calculate_symptom_consistency(self, symptom_analysis: Dict[str, Any], syndrome: Dict[str, Any]) -> float:
        """计算症状一致性"""
        return 0.1

    async def _generate_treatment_recommendations(self, syndrome_id: str, constitution_type: str) -> List[Dict[str, Any]]:
        """生成治疗建议"""
        return [
            {
                "type": "中药方剂",
                "name": "逍遥散加减",
                "description": "疏肝解郁，健脾和胃",
                "confidence": 0.85
            },
            {
                "type": "针灸治疗",
                "points": ["太冲", "三阴交", "足三里"],
                "description": "调理肝脾，平衡气血",
                "confidence": 0.80
            }
        ] 