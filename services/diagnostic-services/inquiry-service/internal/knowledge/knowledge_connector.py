"""
knowledge_connector - 索克生活项目模块
"""

from api.grpc import med_knowledge_pb2, med_knowledge_pb2_grpc
from tenacity import (
import grpc
import httpx
import json
import logging
import time

#!/usr/bin/env python3

"""
医学知识库连接器 - 实现问诊服务与医学知识库的集成

本模块提供了与索克医学知识库系统的集成，能够根据问诊上下文检索相关医学知识，
增强LLM的医学专业知识，支持更精准的症状识别、辨证和诊断。
"""


    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# 导入proto生成的代码

logger = logging.getLogger(__name__)


class KnowledgeConnector:
    """医学知识库连接器，用于检索和集成医学知识"""

    def __init__(self, config: dict):
        """
        初始化医学知识库连接器

        Args:
            config: 配置字典，包含连接参数
        """
        self.config = config
        self.knowledge_service_host = config.get("med_knowledge_host", "med-knowledge")
        self.knowledge_service_port = config.get("med_knowledge_port", 50060)
        self.knowledge_service_url = (
            f"{self.knowledge_service_host}:{self.knowledge_service_port}"
        )

        # 连接超时设置
        self.timeout_ms = config.get("timeout_ms", 5000)
        self.retry_count = config.get("retry_count", 3)
        self.max_retry_wait_ms = config.get("max_retry_wait_ms", 2000)

        # 缓存设置
        self.use_cache = config.get("use_cache", True)
        self.cache_ttl = config.get("cache_ttl", 3600)  # 1小时
        self._cache = {}

        # 向量检索设置
        self.embedding_model = config.get("embedding_model", "local")
        self.top_k = config.get("top_k", 5)
        self.similarity_threshold = config.get("similarity_threshold", 0.75)

        # gRPC通道
        self.channel = None
        self.stub = None

        # HTTP客户端(备用)
        self.http_client = httpx.AsyncClient(
            timeout=self.timeout_ms / 1000,
            base_url=f"http://{self.knowledge_service_url}",
        )

        logger.info(
            f"医学知识库连接器初始化完成，服务地址: {self.knowledge_service_url}"
        )

    async def connect(self):
        """建立到知识库服务的连接"""
        try:
            # 创建异步gRPC通道
            self.channel = grpc.aio.insecure_channel(self.knowledge_service_url)
            # 创建存根
            self.stub = med_knowledge_pb2_grpc.MedKnowledgeServiceStub(self.channel)
            logger.info(f"已连接到医学知识库服务: {self.knowledge_service_url}")
            return True
        except Exception as e:
            logger.error(f"连接医学知识库服务失败: {e!s}")
            return False

    async def disconnect(self):
        """关闭与知识库服务的连接"""
        if self.channel:
            await self.channel.close()
            self.channel = None
            self.stub = None
        if self.http_client:
            await self.http_client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=5),
        retry=retry_if_exception_type((grpc.RpcError, ConnectionError)),
    )
    async def search_knowledge(
        self, query: str, knowledge_type: str = "general", context: dict = None
    ) -> list[dict]:
        """
        搜索医学知识

        Args:
            query: 查询文本
            knowledge_type: 知识类型，可以是 'general', 'tcm', 'disease', 'symptom', 'herb', 'treatment'
            context: 上下文信息，用于增强搜索

        Returns:
            List[Dict]: 搜索结果列表
        """
        # 检查缓存
        cache_key = f"{query}_{knowledge_type}_{json.dumps(context or {})}"
        if self.use_cache and cache_key in self._cache:
            cache_entry = self._cache[cache_key]
            if time.time() - cache_entry["timestamp"] < self.cache_ttl:
                logger.debug(f"从缓存获取知识结果: {query}")
                return cache_entry["data"]

        # 确保连接已建立
        if not self.stub:
            connected = await self.connect()
            if not connected:
                logger.error("无法连接到医学知识库服务")
                return []

        try:
            # 使用gRPC调用医学知识库服务
            request = med_knowledge_pb2.SearchRequest(
                query=query,
                knowledge_type=knowledge_type,
                top_k=self.top_k,
                context=json.dumps(context or {}),
            )
            response = await self.stub.Search(request, timeout=self.timeout_ms / 1000)
            results = [self._convert_knowledge_item(item) for item in response.results]

            # 缓存结果
            if self.use_cache:
                self._cache[cache_key] = {"data": results, "timestamp": time.time()}

                # 清理过期缓存
                if len(self._cache) > 1000:  # 防止缓存过大
                    self._clean_cache()

            return results

        except grpc.RpcError as e:
            status_code = e.code()
            status_details = e.details()
            logger.error(f"gRPC错误: {status_code}, {status_details}, query={query}")

            # 如果服务不可用，尝试备用HTTP接口
            if status_code == grpc.StatusCode.UNAVAILABLE:
                return await self._fallback_http_search(query, knowledge_type, context)

            return []
        except Exception as e:
            logger.error(f"搜索医学知识失败: {e!s}, query={query}")
            return []

    async def _fallback_http_search(
        self, query: str, knowledge_type: str, context: dict = None
    ) -> list[dict]:
        """备用HTTP接口搜索"""
        try:
            logger.info(f"使用备用HTTP接口搜索: {query}")
            response = await self.http_client.post(
                "/api/v1/search",
                json={
                    "query": query,
                    "type": knowledge_type,
                    "top_k": self.top_k,
                    "context": context or {},
                },
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])
            else:
                logger.error(
                    f"HTTP备用接口错误: {response.status_code}, {response.text}"
                )
                return []
        except Exception as e:
            logger.error(f"HTTP备用接口调用失败: {e!s}")
            return []

    def _convert_knowledge_item(self, item) -> dict:
        """将gRPC响应转换为字典格式"""
        return {
            "id": item.id,
            "title": item.title,
            "content": item.content,
            "source": item.source,
            "relevance": item.relevance,
            "type": item.type,
            "metadata": json.loads(item.metadata) if item.metadata else {},
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=5),
        retry=retry_if_exception_type((grpc.RpcError, ConnectionError)),
    )
    async def get_syndrome_information(self, syndrome_name: str) -> dict:
        """
        获取证型信息

        Args:
            syndrome_name: 证型名称

        Returns:
            Dict: 证型信息
        """
        # 确保连接已建立
        if not self.stub:
            connected = await self.connect()
            if not connected:
                logger.error("无法连接到医学知识库服务")
                return {"name": syndrome_name, "error": "服务连接失败"}

        try:
            # 使用gRPC调用
            request = med_knowledge_pb2.SyndromeRequest(name=syndrome_name)
            response = await self.stub.GetSyndrome(
                request, timeout=self.timeout_ms / 1000
            )
            return self._convert_syndrome(response)

        except grpc.RpcError as e:
            status_code = e.code()
            status_details = e.details()
            logger.error(
                f"获取证型信息失败: {status_code}, {status_details}, syndrome={syndrome_name}"
            )

            # 处理找不到数据的情况
            if status_code == grpc.StatusCode.NOT_FOUND:
                return {"name": syndrome_name, "description": "未找到相关证型信息"}

            raise
        except Exception as e:
            logger.error(f"获取证型信息失败: {e!s}, syndrome={syndrome_name}")
            return {"name": syndrome_name, "error": str(e)}

    def _convert_syndrome(self, response) -> dict:
        """将证型信息gRPC响应转换为字典"""
        return {
            "name": response.name,
            "description": response.description,
            "common_symptoms": list(response.common_symptoms),
            "tongue": response.tongue,
            "pulse": response.pulse,
            "treatment_principles": response.treatment_principles,
            "common_herbs": list(response.common_herbs),
            "related_patterns": list(response.related_patterns),
            "modern_associations": list(response.modern_associations),
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=5),
        retry=retry_if_exception_type((grpc.RpcError, ConnectionError)),
    )
    async def get_herb_information(self, herb_name: str) -> dict:
        """
        获取中药材信息

        Args:
            herb_name: 中药材名称

        Returns:
            Dict: 中药材信息
        """
        # 确保连接已建立
        if not self.stub:
            connected = await self.connect()
            if not connected:
                logger.error("无法连接到医学知识库服务")
                return {"name": herb_name, "error": "服务连接失败"}

        try:
            # 使用gRPC调用
            request = med_knowledge_pb2.HerbRequest(name=herb_name)
            response = await self.stub.GetHerb(request, timeout=self.timeout_ms / 1000)
            return self._convert_herb(response)

        except grpc.RpcError as e:
            status_code = e.code()
            status_details = e.details()
            logger.error(
                f"获取中药材信息失败: {status_code}, {status_details}, herb={herb_name}"
            )

            # 处理找不到数据的情况
            if status_code == grpc.StatusCode.NOT_FOUND:
                return {"name": herb_name, "description": "未找到相关中药材信息"}

            raise
        except Exception as e:
            logger.error(f"获取中药材信息失败: {e!s}, herb={herb_name}")
            return {"name": herb_name, "error": str(e)}

    def _convert_herb(self, response) -> dict:
        """将中药材信息gRPC响应转换为字典"""
        return {
            "name": response.name,
            "pinyin": response.pinyin,
            "taste": response.taste,
            "meridians": list(response.meridians),
            "functions": list(response.functions),
            "indications": list(response.indications),
            "contraindications": list(response.contraindications),
            "dosage": response.dosage,
            "modern_research": response.modern_research,
            "toxicity": response.toxicity,
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=5),
        retry=retry_if_exception_type((grpc.RpcError, ConnectionError)),
    )
    async def get_symptom_analysis(self, symptom: str) -> dict:
        """
        获取症状的中医分析

        Args:
            symptom: 症状名称

        Returns:
            Dict: 症状分析信息
        """
        # 确保连接已建立
        if not self.stub:
            connected = await self.connect()
            if not connected:
                logger.error("无法连接到医学知识库服务")
                return {"name": symptom, "error": "服务连接失败"}

        try:
            # 使用gRPC调用
            request = med_knowledge_pb2.SymptomRequest(name=symptom)
            response = await self.stub.AnalyzeSymptom(
                request, timeout=self.timeout_ms / 1000
            )
            return self._convert_symptom_analysis(response)

        except grpc.RpcError as e:
            status_code = e.code()
            status_details = e.details()
            logger.error(
                f"获取症状分析失败: {status_code}, {status_details}, symptom={symptom}"
            )

            # 处理找不到数据的情况
            if status_code == grpc.StatusCode.NOT_FOUND:
                return {
                    "name": symptom,
                    "tcm_analysis": {
                        "common_causes": ["数据不足"],
                        "differentiation": "未找到相关症状分析",
                    },
                }

            raise
        except Exception as e:
            logger.error(f"获取症状分析失败: {e!s}, symptom={symptom}")
            return {"name": symptom, "error": str(e)}

    def _convert_symptom_analysis(self, response) -> dict:
        """将症状分析gRPC响应转换为字典"""
        return {
            "name": response.name,
            "tcm_analysis": {
                "common_causes": list(response.tcm_analysis.common_causes),
                "related_syndromes": list(response.tcm_analysis.related_syndromes),
                "differentiation": response.tcm_analysis.differentiation,
            },
            "western_correlations": list(response.western_correlations),
            "severity_indicators": response.severity_indicators,
            "diagnostic_value": response.diagnostic_value,
        }

    def generate_tcm_prompt(self, symptoms: list[str], patient_info: dict) -> str:
        """
        根据症状和患者信息生成中医诊断提示

        Args:
            symptoms: 症状列表
            patient_info: 患者信息

        Returns:
            str: 生成的提示文本
        """
        age = patient_info.get("age", "未知")
        gender = patient_info.get("gender", "未知")
        constitution = patient_info.get("constitution", "未知")
        symptom_text = "、".join(symptoms)

        prompt = f"""
针对这位{age}岁{gender}患者，体质倾向为{constitution}，主要症状为{symptom_text}。
根据中医辨证论治方法，分析可能的证型并给出中医诊断建议。

请从以下方面进行分析：
1. 八纲辨证（阴阳、表里、寒热、虚实）
2. 脏腑辨证（涉及的主要脏腑）
3. 可能的证型
4. 治疗原则
5. 适合的中药方剂建议
""".strip()

        return prompt

    def _clean_cache(self):
        """清理过期缓存"""
        now = time.time()
        expired_keys = [
            k for k, v in self._cache.items() if now - v["timestamp"] > self.cache_ttl
        ]
        for key in expired_keys:
            del self._cache[key]

        # 如果缓存仍然很大，删除最旧的条目
        if len(self._cache) > 800:  # 保留前800个最新条目
            sorted_items = sorted(self._cache.items(), key=lambda x: x[1]["timestamp"])
            oldest_items = sorted_items[: len(self._cache) - 800]
            for k, _ in oldest_items:
                del self._cache[k]
