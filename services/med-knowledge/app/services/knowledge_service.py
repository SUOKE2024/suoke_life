from typing import List, Optional

from app.core.logger import get_logger
from app.models.entities import (
    Constitution, ConstitutionListResponse, Symptom, SymptomListResponse,
    Acupoint, AcupointListResponse, Herb, HerbListResponse,
    Syndrome, SyndromeListResponse, SearchResponse, SyndromePathwaysResponse,
    RecommendationListResponse, Biomarker, BiomarkerListResponse,
    WesternDisease, WesternDiseaseListResponse, PreventionEvidence, 
    PreventionEvidenceListResponse, IntegratedTreatment, IntegratedTreatmentListResponse,
    LifestyleIntervention, LifestyleInterventionListResponse
)
from app.repositories.neo4j_repository import Neo4jRepository

logger = get_logger()


class KnowledgeService:
    """中医知识服务"""
    
    def __init__(self, repository: Neo4jRepository):
        self.repository = repository

    async def get_node_count(self) -> int:
        """获取知识图谱节点数量"""
        return await self.repository.get_node_count()
    
    async def get_relationship_count(self) -> int:
        """获取知识图谱关系数量"""
        return await self.repository.get_relationship_count()
    
    async def get_constitution_by_id(self, constitution_id: str) -> Optional[Constitution]:
        """根据ID获取体质信息"""
        try:
            return await self.repository.get_constitution_by_id(constitution_id)
        except Exception as e:
            logger.error(f"获取体质信息失败: {e}")
            return None
    
    async def get_constitutions(self, limit: int, offset: int) -> ConstitutionListResponse:
        """获取所有体质信息"""
        try:
            return await self.repository.get_constitutions(limit, offset)
        except Exception as e:
            logger.error(f"获取体质列表失败: {e}")
            return ConstitutionListResponse(
                data=[],
                total=0,
                limit=limit,
                offset=offset
            )
    
    async def get_symptom_by_id(self, symptom_id: str) -> Optional[Symptom]:
        """根据ID获取症状信息"""
        try:
            return await self.repository.get_symptom_by_id(symptom_id)
        except Exception as e:
            logger.error(f"获取症状信息失败: {e}")
            return None
    
    async def get_symptoms(self, limit: int, offset: int) -> SymptomListResponse:
        """获取所有症状信息"""
        try:
            return await self.repository.get_symptoms(limit, offset)
        except Exception as e:
            logger.error(f"获取症状列表失败: {e}")
            return SymptomListResponse(
                data=[],
                total=0,
                limit=limit,
                offset=offset
            )
    
    async def get_acupoint_by_id(self, acupoint_id: str) -> Optional[Acupoint]:
        """根据ID获取穴位信息"""
        try:
            return await self.repository.get_acupoint_by_id(acupoint_id)
        except Exception as e:
            logger.error(f"获取穴位信息失败: {e}")
            return None
    
    async def get_acupoints(
        self, limit: int, offset: int, meridian: Optional[str] = None
    ) -> AcupointListResponse:
        """获取所有穴位信息"""
        try:
            return await self.repository.get_acupoints(limit, offset, meridian)
        except Exception as e:
            logger.error(f"获取穴位列表失败: {e}")
            return AcupointListResponse(
                data=[],
                total=0,
                limit=limit,
                offset=offset
            )
    
    async def get_herb_by_id(self, herb_id: str) -> Optional[Herb]:
        """根据ID获取中药信息"""
        try:
            return await self.repository.get_herb_by_id(herb_id)
        except Exception as e:
            logger.error(f"获取中药信息失败: {e}")
            return None
    
    async def get_herbs(
        self, limit: int, offset: int, category: Optional[str] = None
    ) -> HerbListResponse:
        """获取所有中药信息"""
        try:
            return await self.repository.get_herbs(limit, offset, category)
        except Exception as e:
            logger.error(f"获取中药列表失败: {e}")
            return HerbListResponse(
                data=[],
                total=0,
                limit=limit,
                offset=offset
            )
    
    async def get_syndrome_by_id(self, syndrome_id: str) -> Optional[Syndrome]:
        """根据ID获取证型信息"""
        try:
            return await self.repository.get_syndrome_by_id(syndrome_id)
        except Exception as e:
            logger.error(f"获取证型信息失败: {e}")
            return None
    
    async def get_syndromes(self, limit: int, offset: int) -> SyndromeListResponse:
        """获取所有证型信息"""
        try:
            return await self.repository.get_syndromes(limit, offset)
        except Exception as e:
            logger.error(f"获取证型列表失败: {e}")
            return SyndromeListResponse(
                data=[],
                total=0,
                limit=limit,
                offset=offset
            )
    
    async def get_syndrome_pathways(self, syndrome_id: str) -> SyndromePathwaysResponse:
        """获取证型辨证路径"""
        try:
            return await self.repository.get_syndrome_pathways(syndrome_id)
        except Exception as e:
            logger.error(f"获取证型辨证路径失败: {e}")
            # 返回一个空响应对象
            syndrome = await self.get_syndrome_by_id(syndrome_id)
            return SyndromePathwaysResponse(
                syndrome=syndrome,
                pathways=[]
            )
    
    async def search_knowledge(
        self, query: str, entity_type: Optional[str], limit: int, offset: int
    ) -> SearchResponse:
        """搜索知识库"""
        try:
            return await self.repository.search_knowledge(query, entity_type, limit, offset)
        except Exception as e:
            logger.error(f"搜索知识库失败: {e}")
            return SearchResponse(
                data=[],
                total=0,
                limit=limit,
                offset=offset
            )
    
    async def get_recommendations_by_constitution(
        self, constitution_id: str, types: Optional[List[str]] = None
    ) -> RecommendationListResponse:
        """根据体质获取推荐"""
        try:
            return await self.repository.get_recommendations_by_constitution(constitution_id, types)
        except Exception as e:
            logger.error(f"获取体质推荐失败: {e}")
            return RecommendationListResponse(
                data=[],
                total=0
            )
    
    async def get_biomarker_by_id(self, biomarker_id: str) -> Optional[Biomarker]:
        """根据ID获取生物标志物信息"""
        try:
            return await self.repository.get_biomarker_by_id(biomarker_id)
        except Exception as e:
            logger.error(f"获取生物标志物信息失败: {e}")
            return None
    
    async def get_biomarkers(
        self, limit: int, offset: int, category: Optional[str] = None
    ) -> BiomarkerListResponse:
        """获取所有生物标志物信息"""
        try:
            return await self.repository.get_biomarkers(limit, offset, category)
        except Exception as e:
            logger.error(f"获取生物标志物列表失败: {e}")
            return BiomarkerListResponse(
                data=[],
                total=0,
                limit=limit,
                offset=offset
            )
    
    async def get_biomarkers_by_constitution(
        self, constitution_id: str, limit: int, offset: int
    ) -> BiomarkerListResponse:
        """获取与特定体质相关的生物标志物"""
        try:
            return await self.repository.get_biomarkers_by_constitution(
                constitution_id, limit, offset
            )
        except Exception as e:
            logger.error(f"获取体质相关生物标志物失败: {e}")
            return BiomarkerListResponse(
                data=[],
                total=0,
                limit=limit,
                offset=offset
            )
    
    async def get_western_disease_by_id(self, disease_id: str) -> Optional[WesternDisease]:
        """根据ID获取西医疾病信息"""
        try:
            return await self.repository.get_western_disease_by_id(disease_id)
        except Exception as e:
            logger.error(f"获取西医疾病信息失败: {e}")
            return None
    
    async def get_western_diseases(
        self, limit: int, offset: int
    ) -> WesternDiseaseListResponse:
        """获取所有西医疾病信息"""
        try:
            return await self.repository.get_western_diseases(limit, offset)
        except Exception as e:
            logger.error(f"获取西医疾病列表失败: {e}")
            return WesternDiseaseListResponse(
                data=[],
                total=0,
                limit=limit,
                offset=offset
            )
    
    async def get_western_diseases_by_syndrome(
        self, syndrome_id: str, limit: int, offset: int
    ) -> WesternDiseaseListResponse:
        """获取与特定证型相关的西医疾病"""
        try:
            return await self.repository.get_western_diseases_by_syndrome(
                syndrome_id, limit, offset
            )
        except Exception as e:
            logger.error(f"获取证型相关西医疾病失败: {e}")
            return WesternDiseaseListResponse(
                data=[],
                total=0,
                limit=limit,
                offset=offset
            )
    
    async def get_prevention_evidence_by_id(
        self, evidence_id: str
    ) -> Optional[PreventionEvidence]:
        """根据ID获取预防医学证据信息"""
        try:
            return await self.repository.get_prevention_evidence_by_id(evidence_id)
        except Exception as e:
            logger.error(f"获取预防医学证据信息失败: {e}")
            return None
    
    async def get_prevention_evidence(
        self, limit: int, offset: int, 
        category: Optional[str] = None, 
        evidence_level: Optional[str] = None
    ) -> PreventionEvidenceListResponse:
        """获取所有预防医学证据信息"""
        try:
            return await self.repository.get_prevention_evidence(
                limit, offset, category, evidence_level
            )
        except Exception as e:
            logger.error(f"获取预防医学证据列表失败: {e}")
            return PreventionEvidenceListResponse(
                data=[],
                total=0,
                limit=limit,
                offset=offset
            )
    
    async def get_integrated_treatment_by_id(
        self, treatment_id: str
    ) -> Optional[IntegratedTreatment]:
        """根据ID获取中西医结合治疗方案信息"""
        try:
            return await self.repository.get_integrated_treatment_by_id(treatment_id)
        except Exception as e:
            logger.error(f"获取中西医结合治疗方案信息失败: {e}")
            return None
    
    async def get_integrated_treatments(
        self, limit: int, offset: int, 
        target_condition: Optional[str] = None
    ) -> IntegratedTreatmentListResponse:
        """获取所有中西医结合治疗方案信息"""
        try:
            return await self.repository.get_integrated_treatments(
                limit, offset, target_condition
            )
        except Exception as e:
            logger.error(f"获取中西医结合治疗方案列表失败: {e}")
            return IntegratedTreatmentListResponse(
                data=[],
                total=0,
                limit=limit,
                offset=offset
            )
    
    async def get_lifestyle_intervention_by_id(
        self, intervention_id: str
    ) -> Optional[LifestyleIntervention]:
        """根据ID获取生活方式干预信息"""
        try:
            return await self.repository.get_lifestyle_intervention_by_id(intervention_id)
        except Exception as e:
            logger.error(f"获取生活方式干预信息失败: {e}")
            return None
    
    async def get_lifestyle_interventions(
        self, limit: int, offset: int, 
        category: Optional[str] = None
    ) -> LifestyleInterventionListResponse:
        """获取所有生活方式干预信息"""
        try:
            return await self.repository.get_lifestyle_interventions(
                limit, offset, category
            )
        except Exception as e:
            logger.error(f"获取生活方式干预列表失败: {e}")
            return LifestyleInterventionListResponse(
                data=[],
                total=0,
                limit=limit,
                offset=offset
            )
    
    async def get_lifestyle_interventions_by_constitution(
        self, constitution_id: str, limit: int, offset: int, 
        category: Optional[str] = None
    ) -> LifestyleInterventionListResponse:
        """获取适合特定体质的生活方式干预"""
        try:
            return await self.repository.get_lifestyle_interventions_by_constitution(
                constitution_id, limit, offset, category
            )
        except Exception as e:
            logger.error(f"获取体质相关生活方式干预失败: {e}")
            return LifestyleInterventionListResponse(
                data=[],
                total=0,
                limit=limit,
                offset=offset
            ) 