"""
中医知识服务
提供中医知识图谱数据访问,集成缓存和监控功能
"""

import hashlib

from app.core.logger import get_logger
from app.models.entities import (
    Acupoint,
    AcupointListResponse,
    Biomarker,
    BiomarkerListResponse,
    Constitution,
    ConstitutionListResponse,
    Herb,
    HerbListResponse,
    IntegratedTreatment,
    IntegratedTreatmentListResponse,
    LifestyleIntervention,
    LifestyleInterventionListResponse,
    PreventionEvidence,
    PreventionEvidenceListResponse,
    RecommendationListResponse,
    SearchResponse,
    Symptom,
    SymptomListResponse,
    Syndrome,
    SyndromeListResponse,
    SyndromePathwaysResponse,
    WesternDisease,
    WesternDiseaseListResponse,
)
from app.repositories.neo4j_repository import Neo4jRepository
from app.services.cache_service import CacheKeys, CacheService
from app.services.metrics_service import MetricsService, monitor_performance

logger = get_logger()


class KnowledgeService:
    """中医知识服务"""

    def __init__(
        self,
        repository: Neo4jRepository,
        cache_service: CacheService | None = None,
        metrics_service: MetricsService | None = None,
    ):
        self.repository = repository
        self.cache_service = cache_service
        self.metrics_service = metrics_service

    @monitor_performance()
    async def get_node_count(self) -> int:
        """获取知识图谱节点数量"""
        cache_key = CacheKeys.GRAPH_STATISTICS

        # 尝试从缓存获取
        if self.cache_service:
            cached_stats = await self.cache_service.get(cache_key)
            if cached_stats and isinstance(cached_stats, dict):
                node_count = cached_stats.get("node_count")
                if node_count is not None:
                    if self.metrics_service:
                        self.metrics_service.record_cache_operation("get", "hit")
                    return node_count

            if self.metrics_service:
                self.metrics_service.record_cache_operation("get", "miss")

        # 从数据库获取
        try:
            node_count = await self.repository.get_node_count()

            # 缓存结果
            if self.cache_service:
                stats = {"node_count": node_count}
                await self.cache_service.set(cache_key, stats, ttl=3600)  # 缓存1小时

            if self.metrics_service:
                self.metrics_service.record_knowledge_request("graph", "node_count")

            return node_count

        except Exception as e:
            logger.error(f"获取节点数量失败: {e}")
            if self.metrics_service:
                self.metrics_service.record_knowledge_request("graph", "node_count_error")
            raise

    @monitor_performance()
    async def get_relationship_count(self) -> int:
        """获取知识图谱关系数量"""
        cache_key = CacheKeys.GRAPH_STATISTICS

        # 尝试从缓存获取
        if self.cache_service:
            cached_stats = await self.cache_service.get(cache_key)
            if cached_stats and isinstance(cached_stats, dict):
                relationship_count = cached_stats.get("relationship_count")
                if relationship_count is not None:
                    if self.metrics_service:
                        self.metrics_service.record_cache_operation("get", "hit")
                    return relationship_count

            if self.metrics_service:
                self.metrics_service.record_cache_operation("get", "miss")

        # 从数据库获取
        try:
            relationship_count = await self.repository.get_relationship_count()

            # 更新缓存
            if self.cache_service:
                cached_stats = await self.cache_service.get(cache_key) or {}
                cached_stats["relationship_count"] = relationship_count
                await self.cache_service.set(cache_key, cached_stats, ttl=3600)

            if self.metrics_service:
                self.metrics_service.record_knowledge_request("graph", "relationship_count")

            return relationship_count

        except Exception as e:
            logger.error(f"获取关系数量失败: {e}")
            if self.metrics_service:
                self.metrics_service.record_knowledge_request("graph", "relationship_count_error")
            raise

    @monitor_performance()
    async def get_constitution_by_id(self, constitution_id: str) -> Constitution | None:
        """根据ID获取体质信息"""
        cache_key = CacheKeys.format_key(
            CacheKeys.CONSTITUTION_DETAIL, constitution_id=constitution_id
        )

        # 尝试从缓存获取
        if self.cache_service:
            cached_constitution = await self.cache_service.get(cache_key, Constitution)
            if cached_constitution:
                if self.metrics_service:
                    self.metrics_service.record_cache_operation("get", "hit")
                    self.metrics_service.record_knowledge_request("constitution", "get_by_id")
                return cached_constitution

            if self.metrics_service:
                self.metrics_service.record_cache_operation("get", "miss")

        # 从数据库获取
        try:
            constitution = await self.repository.get_constitution_by_id(constitution_id)

            # 缓存结果
            if constitution and self.cache_service:
                await self.cache_service.set(cache_key, constitution, ttl=7200)  # 缓存2小时

            if self.metrics_service:
                self.metrics_service.record_knowledge_request("constitution", "get_by_id")

            return constitution

        except Exception as e:
            logger.error(f"获取体质信息失败 constitution_id={constitution_id}: {e}")
            if self.metrics_service:
                self.metrics_service.record_knowledge_request("constitution", "get_by_id_error")
            return None

    @monitor_performance()
    async def get_constitutions(self, limit: int, offset: int) -> ConstitutionListResponse:
        """获取所有体质信息"""
        cache_key = f"{CacheKeys.CONSTITUTION_LIST}:limit_{limit}:offset_{offset}"

        # 尝试从缓存获取
        if self.cache_service:
            cached_response = await self.cache_service.get(cache_key, ConstitutionListResponse)
            if cached_response:
                if self.metrics_service:
                    self.metrics_service.record_cache_operation("get", "hit")
                    self.metrics_service.record_knowledge_request("constitution", "list")
                return cached_response

            if self.metrics_service:
                self.metrics_service.record_cache_operation("get", "miss")

        # 从数据库获取
        try:
            response = await self.repository.get_constitutions(limit, offset)

            # 缓存结果
            if self.cache_service:
                await self.cache_service.set(cache_key, response, ttl=1800)  # 缓存30分钟

            if self.metrics_service:
                self.metrics_service.record_knowledge_request("constitution", "list")

            return response

        except Exception as e:
            logger.error(f"获取体质列表失败 limit={limit} offset={offset}: {e}")
            if self.metrics_service:
                self.metrics_service.record_knowledge_request("constitution", "list_error")
            return ConstitutionListResponse(data=[], total=0, limit=limit, offset=offset)

    @monitor_performance()
    async def get_symptom_by_id(self, symptom_id: str) -> Symptom | None:
        """根据ID获取症状信息"""
        cache_key = CacheKeys.format_key(CacheKeys.SYMPTOM_DETAIL, symptom_id=symptom_id)

        # 尝试从缓存获取
        if self.cache_service:
            cached_symptom = await self.cache_service.get(cache_key, Symptom)
            if cached_symptom:
                if self.metrics_service:
                    self.metrics_service.record_cache_operation("get", "hit")
                    self.metrics_service.record_knowledge_request("symptom", "get_by_id")
                return cached_symptom

            if self.metrics_service:
                self.metrics_service.record_cache_operation("get", "miss")

        # 从数据库获取
        try:
            symptom = await self.repository.get_symptom_by_id(symptom_id)

            # 缓存结果
            if symptom and self.cache_service:
                await self.cache_service.set(cache_key, symptom, ttl=7200)

            if self.metrics_service:
                self.metrics_service.record_knowledge_request("symptom", "get_by_id")

            return symptom

        except Exception as e:
            logger.error(f"获取症状信息失败 symptom_id={symptom_id}: {e}")
            if self.metrics_service:
                self.metrics_service.record_knowledge_request("symptom", "get_by_id_error")
            return None

    @monitor_performance()
    async def get_symptoms(self, limit: int, offset: int) -> SymptomListResponse:
        """获取所有症状信息"""
        cache_key = f"{CacheKeys.SYMPTOM_LIST}:limit_{limit}:offset_{offset}"

        # 尝试从缓存获取
        if self.cache_service:
            cached_response = await self.cache_service.get(cache_key, SymptomListResponse)
            if cached_response:
                if self.metrics_service:
                    self.metrics_service.record_cache_operation("get", "hit")
                    self.metrics_service.record_knowledge_request("symptom", "list")
                return cached_response

            if self.metrics_service:
                self.metrics_service.record_cache_operation("get", "miss")

        # 从数据库获取
        try:
            response = await self.repository.get_symptoms(limit, offset)

            # 缓存结果
            if self.cache_service:
                await self.cache_service.set(cache_key, response, ttl=1800)

            if self.metrics_service:
                self.metrics_service.record_knowledge_request("symptom", "list")

            return response

        except Exception as e:
            logger.error(f"获取症状列表失败 limit={limit} offset={offset}: {e}")
            if self.metrics_service:
                self.metrics_service.record_knowledge_request("symptom", "list_error")
            return SymptomListResponse(data=[], total=0, limit=limit, offset=offset)

    @monitor_performance()
    async def get_acupoint_by_id(self, acupoint_id: str) -> Acupoint | None:
        """根据ID获取穴位信息"""
        cache_key = CacheKeys.format_key(CacheKeys.ACUPOINT_DETAIL, acupoint_id=acupoint_id)

        # 尝试从缓存获取
        if self.cache_service:
            cached_acupoint = await self.cache_service.get(cache_key, Acupoint)
            if cached_acupoint:
                if self.metrics_service:
                    self.metrics_service.record_cache_operation("get", "hit")
                    self.metrics_service.record_knowledge_request("acupoint", "get_by_id")
                return cached_acupoint

            if self.metrics_service:
                self.metrics_service.record_cache_operation("get", "miss")

        # 从数据库获取
        try:
            acupoint = await self.repository.get_acupoint_by_id(acupoint_id)

            # 缓存结果
            if acupoint and self.cache_service:
                await self.cache_service.set(cache_key, acupoint, ttl=7200)

            if self.metrics_service:
                self.metrics_service.record_knowledge_request("acupoint", "get_by_id")

            return acupoint

        except Exception as e:
            logger.error(f"获取穴位信息失败 acupoint_id={acupoint_id}: {e}")
            if self.metrics_service:
                self.metrics_service.record_knowledge_request("acupoint", "get_by_id_error")
            return None

    @monitor_performance()
    async def get_acupoints(
        self, limit: int, offset: int, meridian: str | None = None
    ) -> AcupointListResponse:
        """获取所有穴位信息"""
        cache_key = f"{CacheKeys.ACUPOINT_LIST}:limit_{limit}:offset_{offset}"
        if meridian:
            cache_key += f":meridian_{meridian}"

        # 尝试从缓存获取
        if self.cache_service:
            cached_response = await self.cache_service.get(cache_key, AcupointListResponse)
            if cached_response:
                if self.metrics_service:
                    self.metrics_service.record_cache_operation("get", "hit")
                    self.metrics_service.record_knowledge_request("acupoint", "list")
                return cached_response

            if self.metrics_service:
                self.metrics_service.record_cache_operation("get", "miss")

        # 从数据库获取
        try:
            response = await self.repository.get_acupoints(limit, offset, meridian)

            # 缓存结果
            if self.cache_service:
                await self.cache_service.set(cache_key, response, ttl=1800)

            if self.metrics_service:
                self.metrics_service.record_knowledge_request("acupoint", "list")

            return response

        except Exception as e:
            logger.error(f"获取穴位列表失败 limit={limit} offset={offset} meridian={meridian}: {e}")
            if self.metrics_service:
                self.metrics_service.record_knowledge_request("acupoint", "list_error")
            return AcupointListResponse(data=[], total=0, limit=limit, offset=offset)

    @monitor_performance()
    async def search_knowledge(
        self, query: str, entity_type: str | None, limit: int, offset: int
    ) -> SearchResponse:
        """搜索知识库"""
        # 生成查询哈希作为缓存键
        query_hash = hashlib.md5(f"{query}:{entity_type}:{limit}:{offset}".encode()).hexdigest()
        cache_key = CacheKeys.format_key(CacheKeys.SEARCH_RESULT, query_hash=query_hash)

        # 尝试从缓存获取
        if self.cache_service:
            cached_response = await self.cache_service.get(cache_key, SearchResponse)
            if cached_response:
                if self.metrics_service:
                    self.metrics_service.record_cache_operation("get", "hit")
                    self.metrics_service.record_knowledge_request("search", "query")
                return cached_response

            if self.metrics_service:
                self.metrics_service.record_cache_operation("get", "miss")

        # 从数据库搜索
        try:
            response = await self.repository.search_knowledge(query, entity_type, limit, offset)

            # 缓存结果(搜索结果缓存时间较短)
            if self.cache_service:
                await self.cache_service.set(cache_key, response, ttl=600)  # 缓存10分钟

            if self.metrics_service:
                self.metrics_service.record_knowledge_request("search", "query")

            return response

        except Exception as e:
            logger.error(f"搜索知识库失败 query={query} entity_type={entity_type}: {e}")
            if self.metrics_service:
                self.metrics_service.record_knowledge_request("search", "query_error")
            return SearchResponse(data=[], total=0, limit=limit, offset=offset)

    @monitor_performance()
    async def get_herb_by_id(self, herb_id: str) -> Herb | None:
        """根据ID获取中药信息"""
        cache_key = CacheKeys.format_key(CacheKeys.HERB_DETAIL, herb_id=herb_id)

        # 尝试从缓存获取
        if self.cache_service:
            cached_herb = await self.cache_service.get(cache_key, Herb)
            if cached_herb:
                if self.metrics_service:
                    self.metrics_service.record_cache_operation("get", "hit")
                    self.metrics_service.record_knowledge_request("herb", "get_by_id")
                return cached_herb

            if self.metrics_service:
                self.metrics_service.record_cache_operation("get", "miss")

        # 从数据库获取
        try:
            herb = await self.repository.get_herb_by_id(herb_id)

            # 缓存结果
            if herb and self.cache_service:
                await self.cache_service.set(cache_key, herb, ttl=7200)

            if self.metrics_service:
                self.metrics_service.record_knowledge_request("herb", "get_by_id")

            return herb

        except Exception as e:
            logger.error(f"获取中药信息失败 herb_id={herb_id}: {e}")
            if self.metrics_service:
                self.metrics_service.record_knowledge_request("herb", "get_by_id_error")
            return None

    @monitor_performance()
    async def get_herbs(
        self, limit: int, offset: int, category: str | None = None
    ) -> HerbListResponse:
        """获取所有中药信息"""
        cache_key = f"{CacheKeys.HERB_LIST}:limit_{limit}:offset_{offset}"
        if category:
            cache_key += f":category_{category}"

        # 尝试从缓存获取
        if self.cache_service:
            cached_response = await self.cache_service.get(cache_key, HerbListResponse)
            if cached_response:
                if self.metrics_service:
                    self.metrics_service.record_cache_operation("get", "hit")
                    self.metrics_service.record_knowledge_request("herb", "list")
                return cached_response

            if self.metrics_service:
                self.metrics_service.record_cache_operation("get", "miss")

        # 从数据库获取
        try:
            response = await self.repository.get_herbs(limit, offset, category)

            # 缓存结果
            if self.cache_service:
                await self.cache_service.set(cache_key, response, ttl=1800)

            if self.metrics_service:
                self.metrics_service.record_knowledge_request("herb", "list")

            return response

        except Exception as e:
            logger.error(f"获取中药列表失败 limit={limit} offset={offset} category={category}: {e}")
            if self.metrics_service:
                self.metrics_service.record_knowledge_request("herb", "list_error")
            return HerbListResponse(data=[], total=0, limit=limit, offset=offset)

    @monitor_performance()
    async def get_syndrome_by_id(self, syndrome_id: str) -> Syndrome | None:
        """根据ID获取证型信息"""
        cache_key = CacheKeys.format_key(CacheKeys.SYNDROME_DETAIL, syndrome_id=syndrome_id)

        # 尝试从缓存获取
        if self.cache_service:
            cached_syndrome = await self.cache_service.get(cache_key, Syndrome)
            if cached_syndrome:
                if self.metrics_service:
                    self.metrics_service.record_cache_operation("get", "hit")
                    self.metrics_service.record_knowledge_request("syndrome", "get_by_id")
                return cached_syndrome

            if self.metrics_service:
                self.metrics_service.record_cache_operation("get", "miss")

        # 从数据库获取
        try:
            syndrome = await self.repository.get_syndrome_by_id(syndrome_id)

            # 缓存结果
            if syndrome and self.cache_service:
                await self.cache_service.set(cache_key, syndrome, ttl=7200)

            if self.metrics_service:
                self.metrics_service.record_knowledge_request("syndrome", "get_by_id")

            return syndrome

        except Exception as e:
            logger.error(f"获取证型信息失败 syndrome_id={syndrome_id}: {e}")
            if self.metrics_service:
                self.metrics_service.record_knowledge_request("syndrome", "get_by_id_error")
            return None

    @monitor_performance()
    async def get_syndromes(self, limit: int, offset: int) -> SyndromeListResponse:
        """获取所有证型信息"""
        cache_key = f"{CacheKeys.SYNDROME_LIST}:limit_{limit}:offset_{offset}"

        # 尝试从缓存获取
        if self.cache_service:
            cached_response = await self.cache_service.get(cache_key, SyndromeListResponse)
            if cached_response:
                if self.metrics_service:
                    self.metrics_service.record_cache_operation("get", "hit")
                    self.metrics_service.record_knowledge_request("syndrome", "list")
                return cached_response

            if self.metrics_service:
                self.metrics_service.record_cache_operation("get", "miss")

        # 从数据库获取
        try:
            response = await self.repository.get_syndromes(limit, offset)

            # 缓存结果
            if self.cache_service:
                await self.cache_service.set(cache_key, response, ttl=1800)

            if self.metrics_service:
                self.metrics_service.record_knowledge_request("syndrome", "list")

            return response

        except Exception as e:
            logger.error(f"获取证型列表失败 limit={limit} offset={offset}: {e}")
            if self.metrics_service:
                self.metrics_service.record_knowledge_request("syndrome", "list_error")
            return SyndromeListResponse(data=[], total=0, limit=limit, offset=offset)

    @monitor_performance()
    async def get_syndrome_pathways(self, syndrome_id: str) -> SyndromePathwaysResponse:
        """获取证型辨证路径"""
        cache_key = CacheKeys.format_key(CacheKeys.SYNDROME_PATHWAYS, syndrome_id=syndrome_id)

        # 尝试从缓存获取
        if self.cache_service:
            cached_response = await self.cache_service.get(cache_key, SyndromePathwaysResponse)
            if cached_response:
                if self.metrics_service:
                    self.metrics_service.record_cache_operation("get", "hit")
                    self.metrics_service.record_knowledge_request("syndrome", "pathways")
                return cached_response

            if self.metrics_service:
                self.metrics_service.record_cache_operation("get", "miss")

        # 从数据库获取
        try:
            response = await self.repository.get_syndrome_pathways(syndrome_id)

            # 缓存结果
            if self.cache_service:
                await self.cache_service.set(cache_key, response, ttl=3600)  # 缓存1小时

            if self.metrics_service:
                self.metrics_service.record_knowledge_request("syndrome", "pathways")

            return response

        except Exception as e:
            logger.error(f"获取证型辨证路径失败 syndrome_id={syndrome_id}: {e}")
            if self.metrics_service:
                self.metrics_service.record_knowledge_request("syndrome", "pathways_error")

            # 返回一个空响应对象
            syndrome = await self.get_syndrome_by_id(syndrome_id)
            return SyndromePathwaysResponse(syndrome=syndrome, pathways=[])

    @monitor_performance()
    async def get_recommendations_by_constitution(
        self, constitution_id: str, types: list[str] | None = None
    ) -> RecommendationListResponse:
        """根据体质获取推荐"""
        cache_key = CacheKeys.format_key(
            CacheKeys.CONSTITUTION_RECOMMENDATIONS, constitution_id=constitution_id
        )
        if types:
            cache_key += f":types_{'_'.join(sorted(types))}"

        # 尝试从缓存获取
        if self.cache_service:
            cached_response = await self.cache_service.get(cache_key, RecommendationListResponse)
            if cached_response:
                if self.metrics_service:
                    self.metrics_service.record_cache_operation("get", "hit")
                    self.metrics_service.record_knowledge_request(
                        "recommendation", "by_constitution"
                    )
                return cached_response

            if self.metrics_service:
                self.metrics_service.record_cache_operation("get", "miss")

        # 从数据库获取
        try:
            response = await self.repository.get_recommendations_by_constitution(
                constitution_id, types
            )

            # 缓存结果
            if self.cache_service:
                await self.cache_service.set(cache_key, response, ttl=3600)

            if self.metrics_service:
                self.metrics_service.record_knowledge_request("recommendation", "by_constitution")

            return response

        except Exception as e:
            logger.error(f"获取体质推荐失败 constitution_id={constitution_id} types={types}: {e}")
            if self.metrics_service:
                self.metrics_service.record_knowledge_request(
                    "recommendation", "by_constitution_error"
                )
            return RecommendationListResponse(data=[], total=0)

    @monitor_performance()
    async def get_biomarker_by_id(self, biomarker_id: str) -> Biomarker | None:
        """根据ID获取生物标志物信息"""
        cache_key = CacheKeys.format_key(CacheKeys.BIOMARKER_DETAIL, biomarker_id=biomarker_id)

        # 尝试从缓存获取
        if self.cache_service:
            cached_biomarker = await self.cache_service.get(cache_key, Biomarker)
            if cached_biomarker:
                if self.metrics_service:
                    self.metrics_service.record_cache_operation("get", "hit")
                    self.metrics_service.record_knowledge_request("biomarker", "get_by_id")
                return cached_biomarker

            if self.metrics_service:
                self.metrics_service.record_cache_operation("get", "miss")

        # 从数据库获取
        try:
            biomarker = await self.repository.get_biomarker_by_id(biomarker_id)

            # 缓存结果
            if biomarker and self.cache_service:
                await self.cache_service.set(cache_key, biomarker, ttl=7200)

            if self.metrics_service:
                self.metrics_service.record_knowledge_request("biomarker", "get_by_id")

            return biomarker

        except Exception as e:
            logger.error(f"获取生物标志物信息失败 biomarker_id={biomarker_id}: {e}")
            if self.metrics_service:
                self.metrics_service.record_knowledge_request("biomarker", "get_by_id_error")
            return None

    @monitor_performance()
    async def get_biomarkers(
        self, limit: int, offset: int, category: str | None = None
    ) -> BiomarkerListResponse:
        """获取所有生物标志物信息"""
        cache_key = f"{CacheKeys.BIOMARKER_LIST}:limit_{limit}:offset_{offset}"
        if category:
            cache_key += f":category_{category}"

        # 尝试从缓存获取
        if self.cache_service:
            cached_response = await self.cache_service.get(cache_key, BiomarkerListResponse)
            if cached_response:
                if self.metrics_service:
                    self.metrics_service.record_cache_operation("get", "hit")
                    self.metrics_service.record_knowledge_request("biomarker", "list")
                return cached_response

            if self.metrics_service:
                self.metrics_service.record_cache_operation("get", "miss")

        # 从数据库获取
        try:
            response = await self.repository.get_biomarkers(limit, offset, category)

            # 缓存结果
            if self.cache_service:
                await self.cache_service.set(cache_key, response, ttl=1800)

            if self.metrics_service:
                self.metrics_service.record_knowledge_request("biomarker", "list")

            return response

        except Exception as e:
            logger.error(
                f"获取生物标志物列表失败 limit={limit} offset={offset} category={category}: {e}"
            )
            if self.metrics_service:
                self.metrics_service.record_knowledge_request("biomarker", "list_error")
            return BiomarkerListResponse(data=[], total=0, limit=limit, offset=offset)

    @monitor_performance()
    async def get_biomarkers_by_constitution(
        self, constitution_id: str, limit: int, offset: int
    ) -> BiomarkerListResponse:
        """获取与特定体质相关的生物标志物"""
        cache_key = (
            CacheKeys.format_key(
                CacheKeys.BIOMARKER_BY_CONSTITUTION, constitution_id=constitution_id
            )
            + f":limit_{limit}:offset_{offset}"
        )

        # 尝试从缓存获取
        if self.cache_service:
            cached_response = await self.cache_service.get(cache_key, BiomarkerListResponse)
            if cached_response:
                if self.metrics_service:
                    self.metrics_service.record_cache_operation("get", "hit")
                    self.metrics_service.record_knowledge_request("biomarker", "by_constitution")
                return cached_response

            if self.metrics_service:
                self.metrics_service.record_cache_operation("get", "miss")

        # 从数据库获取
        try:
            response = await self.repository.get_biomarkers_by_constitution(
                constitution_id, limit, offset
            )

            # 缓存结果
            if self.cache_service:
                await self.cache_service.set(cache_key, response, ttl=3600)

            if self.metrics_service:
                self.metrics_service.record_knowledge_request("biomarker", "by_constitution")

            return response

        except Exception as e:
            logger.error(f"获取体质相关生物标志物失败 constitution_id={constitution_id}: {e}")
            if self.metrics_service:
                self.metrics_service.record_knowledge_request("biomarker", "by_constitution_error")
            return BiomarkerListResponse(data=[], total=0, limit=limit, offset=offset)

    async def get_western_disease_by_id(self, disease_id: str) -> WesternDisease | None:
        """根据ID获取西医疾病信息"""
        try:
            return await self.repository.get_western_disease_by_id(disease_id)
        except Exception as e:
            logger.error(f"获取西医疾病信息失败: {e}")
            return None

    async def get_western_diseases(self, limit: int, offset: int) -> WesternDiseaseListResponse:
        """获取所有西医疾病信息"""
        try:
            return await self.repository.get_western_diseases(limit, offset)
        except Exception as e:
            logger.error(f"获取西医疾病列表失败: {e}")
            return WesternDiseaseListResponse(data=[], total=0, limit=limit, offset=offset)

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
            return WesternDiseaseListResponse(data=[], total=0, limit=limit, offset=offset)

    async def get_prevention_evidence_by_id(self, evidence_id: str) -> PreventionEvidence | None:
        """根据ID获取预防医学证据信息"""
        try:
            return await self.repository.get_prevention_evidence_by_id(evidence_id)
        except Exception as e:
            logger.error(f"获取预防医学证据信息失败: {e}")
            return None

    async def get_prevention_evidence(
        self,
        limit: int,
        offset: int,
        category: str | None = None,
        evidence_level: str | None = None,
    ) -> PreventionEvidenceListResponse:
        """获取所有预防医学证据信息"""
        try:
            return await self.repository.get_prevention_evidence(
                limit, offset, category, evidence_level
            )
        except Exception as e:
            logger.error(f"获取预防医学证据列表失败: {e}")
            return PreventionEvidenceListResponse(data=[], total=0, limit=limit, offset=offset)

    async def get_integrated_treatment_by_id(self, treatment_id: str) -> IntegratedTreatment | None:
        """根据ID获取中西医结合治疗方案信息"""
        try:
            return await self.repository.get_integrated_treatment_by_id(treatment_id)
        except Exception as e:
            logger.error(f"获取中西医结合治疗方案信息失败: {e}")
            return None

    async def get_integrated_treatments(
        self, limit: int, offset: int, target_condition: str | None = None
    ) -> IntegratedTreatmentListResponse:
        """获取所有中西医结合治疗方案信息"""
        try:
            return await self.repository.get_integrated_treatments(limit, offset, target_condition)
        except Exception as e:
            logger.error(f"获取中西医结合治疗方案列表失败: {e}")
            return IntegratedTreatmentListResponse(data=[], total=0, limit=limit, offset=offset)

    async def get_lifestyle_intervention_by_id(
        self, intervention_id: str
    ) -> LifestyleIntervention | None:
        """根据ID获取生活方式干预信息"""
        try:
            return await self.repository.get_lifestyle_intervention_by_id(intervention_id)
        except Exception as e:
            logger.error(f"获取生活方式干预信息失败: {e}")
            return None

    async def get_lifestyle_interventions(
        self, limit: int, offset: int, category: str | None = None
    ) -> LifestyleInterventionListResponse:
        """获取所有生活方式干预信息"""
        try:
            return await self.repository.get_lifestyle_interventions(limit, offset, category)
        except Exception as e:
            logger.error(f"获取生活方式干预列表失败: {e}")
            return LifestyleInterventionListResponse(data=[], total=0, limit=limit, offset=offset)

    async def get_lifestyle_interventions_by_constitution(
        self, constitution_id: str, limit: int, offset: int, category: str | None = None
    ) -> LifestyleInterventionListResponse:
        """获取适合特定体质的生活方式干预"""
        try:
            return await self.repository.get_lifestyle_interventions_by_constitution(
                constitution_id, limit, offset, category
            )
        except Exception as e:
            logger.error(f"获取体质相关生活方式干预失败: {e}")
            return LifestyleInterventionListResponse(data=[], total=0, limit=limit, offset=offset)

    # 五诊相关知识
    if '五诊' in query or '望闻问切算' in query:
        knowledge_items.extend([
            {
                'id': 'tcm_5d_001',
                'title': '中医五诊概述',
                'content': '中医五诊包括望、闻、问、切、算五种诊断方法，是中医诊断学的核心内容。',
                'category': '中医诊断',
                'tags': ['五诊', '诊断方法'],
                'confidence': 0.95
            },
            {
                'id': 'tcm_5d_002', 
                'title': '算诊在五诊中的作用',
                'content': '算诊是基于易学、天文历法的计算诊断方法，是传统五诊的重要补充。',
                'category': '中医诊断',