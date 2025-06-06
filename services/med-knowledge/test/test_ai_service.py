"""
test_ai_service - 索克生活项目模块
"""

from app.services.ai_service import AIService
from app.services.cache_service import CacheService
from app.services.knowledge_graph_service import KnowledgeGraphService
from app.services.knowledge_service import KnowledgeService
from app.services.metrics_service import MetricsService
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock
import pytest

"""
AI服务测试
"""




@pytest.fixture
def mock_knowledge_service():
    """模拟知识服务"""
    service = AsyncMock(spec=KnowledgeService)
    service.get_constitution_by_id.return_value = None
    service.search_knowledge.return_value = MagicMock(data=[])
    return service


@pytest.fixture
def mock_graph_service():
    """模拟知识图谱服务"""
    service = AsyncMock(spec=KnowledgeGraphService)
    service.find_paths.return_value = []
    return service


@pytest.fixture
def mock_cache_service():
    """模拟缓存服务"""
    service = AsyncMock(spec=CacheService)
    service.get.return_value = None
    service.set.return_value = True
    return service


@pytest.fixture
def mock_metrics_service():
    """模拟指标服务"""
    service = MagicMock(spec=MetricsService)
    service.record_cache_operation = MagicMock()
    service.record_knowledge_request = MagicMock()
    return service


@pytest.fixture
def ai_service(mock_knowledge_service, mock_graph_service, mock_cache_service, mock_metrics_service):
    """AI服务实例"""
    return AIService(
        knowledge_service=mock_knowledge_service,
        graph_service=mock_graph_service,
        cache_service=mock_cache_service,
        metrics_service=mock_metrics_service
    )


class TestAIService:
    """AI服务测试类"""

    @pytest.mark.asyncio
    async def test_intelligent_diagnosis_success(self, ai_service):
        """测试智能诊断成功"""
        symptoms = [
            {"name": "头痛", "severity": 3, "duration": "1周"},
            {"name": "失眠", "severity": 4, "duration": "1月"}
        ]
        patient_info = {
            "constitution_type": "气虚质",
            "age": 35,
            "gender": "女"
        }
        
        result = await ai_service.intelligent_diagnosis(symptoms, patient_info)
        
        assert result["success"] is True
        assert "diagnosis" in result
        assert "confidence" in result
        assert "reasoning" in result
        assert "symptom_analysis" in result
        assert "constitution_analysis" in result
        assert "syndrome_inference" in result
        assert "graph_analysis" in result
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_intelligent_diagnosis_empty_symptoms(self, ai_service):
        """测试空症状列表的智能诊断"""
        symptoms = []
        patient_info = {"constitution_type": None, "age": 30, "gender": "男"}
        
        result = await ai_service.intelligent_diagnosis(symptoms, patient_info)
        
        assert result["success"] is True
        assert result["symptom_analysis"]["symptom_count"] == 0

    @pytest.mark.asyncio
    async def test_multimodal_analysis_text_only(self, ai_service):
        """测试仅文本的多模态分析"""
        text_data = "患者主诉头痛、失眠，持续一周"
        
        result = await ai_service.multimodal_analysis(text_data=text_data)
        
        assert result["success"] is True
        assert "individual_results" in result
        assert "text" in result["individual_results"]
        assert "fusion_result" in result
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_multimodal_analysis_image_only(self, ai_service):
        """测试仅图像的多模态分析"""
        image_data = b"fake_image_data"
        context = {"image_type": "tongue"}
        
        result = await ai_service.multimodal_analysis(image_data=image_data, context=context)
        
        assert result["success"] is True
        assert "individual_results" in result
        assert "image" in result["individual_results"]
        assert "fusion_result" in result

    @pytest.mark.asyncio
    async def test_multimodal_analysis_audio_only(self, ai_service):
        """测试仅音频的多模态分析"""
        audio_data = b"fake_audio_data"
        
        result = await ai_service.multimodal_analysis(audio_data=audio_data)
        
        assert result["success"] is True
        assert "individual_results" in result
        assert "audio" in result["individual_results"]
        assert "fusion_result" in result

    @pytest.mark.asyncio
    async def test_multimodal_analysis_combined(self, ai_service):
        """测试多模态综合分析"""
        text_data = "患者主诉头痛"
        image_data = b"fake_image_data"
        audio_data = b"fake_audio_data"
        context = {"image_type": "face"}
        
        result = await ai_service.multimodal_analysis(
            text_data=text_data,
            image_data=image_data,
            audio_data=audio_data,
            context=context
        )
        
        assert result["success"] is True
        assert "individual_results" in result
        assert "text" in result["individual_results"]
        assert "image" in result["individual_results"]
        assert "audio" in result["individual_results"]
        assert "fusion_result" in result

    @pytest.mark.asyncio
    async def test_knowledge_enhanced_rag(self, ai_service):
        """测试知识增强RAG"""
        query = "什么是肝郁脾虚证？"
        
        result = await ai_service.knowledge_enhanced_rag(query)
        
        assert result["success"] is True
        assert result["query"] == query
        assert "retrieval_results" in result
        assert "generated_response" in result
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_knowledge_enhanced_rag_with_context(self, ai_service):
        """测试带上下文的知识增强RAG"""
        query = "如何治疗失眠？"
        context = {"patient_age": 35, "constitution": "气虚质"}
        max_results = 5
        
        result = await ai_service.knowledge_enhanced_rag(
            query=query,
            context=context,
            max_results=max_results
        )
        
        assert result["success"] is True
        assert result["query"] == query

    def test_calculate_symptom_weight(self, ai_service):
        """测试症状权重计算"""
        # 测试急性症状
        weight1 = ai_service._calculate_symptom_weight(5, "急性")
        assert weight1 >= 1.0  # 修改为 >= 因为可能正好等于1.0
        
        # 测试慢性症状
        weight2 = ai_service._calculate_symptom_weight(3, "慢性")
        assert weight2 < 0.6
        
        # 测试正常症状
        weight3 = ai_service._calculate_symptom_weight(3, "1周")
        assert 0.5 < weight3 < 0.7

    def test_identify_primary_symptoms(self, ai_service):
        """测试主要症状识别"""
        symptom_scores = {
            "头痛": {"normalized_score": 4.0},
            "失眠": {"normalized_score": 3.5},
            "乏力": {"normalized_score": 2.0},
            "食欲不振": {"normalized_score": 1.5}
        }
        
        primary_symptoms = ai_service._identify_primary_symptoms(symptom_scores)
        
        assert len(primary_symptoms) == 3
        assert primary_symptoms[0] == "头痛"
        assert primary_symptoms[1] == "失眠"
        assert primary_symptoms[2] == "乏力"

    def test_categorize_age(self, ai_service):
        """测试年龄分组"""
        assert ai_service._categorize_age(10) == "儿童"
        assert ai_service._categorize_age(25) == "青年"
        assert ai_service._categorize_age(45) == "中年"
        assert ai_service._categorize_age(70) == "老年"

    def test_analyze_query_intent(self, ai_service):
        """测试查询意图分析"""
        assert ai_service._analyze_query_intent("我头痛是什么病？") == "diagnosis"
        assert ai_service._analyze_query_intent("如何治疗失眠？") == "treatment"
        assert ai_service._analyze_query_intent("什么是气虚质？") == "knowledge"
        assert ai_service._analyze_query_intent("你好") == "general"

    @pytest.mark.asyncio
    async def test_get_syndromes_by_symptoms(self, ai_service):
        """测试根据症状获取证型"""
        symptoms = ["头痛", "失眠", "乏力"]
        
        syndromes = await ai_service._get_syndromes_by_symptoms(symptoms)
        
        assert isinstance(syndromes, list)
        assert len(syndromes) > 0
        for syndrome in syndromes:
            assert "id" in syndrome
            assert "name" in syndrome
            assert "relevance_score" in syndrome

    @pytest.mark.asyncio
    async def test_analyze_constitution_tendencies(self, ai_service):
        """测试体质倾向性分析"""
        result = await ai_service._analyze_constitution_tendencies("气虚质", 35, "女")
        
        assert "disease_tendency" in result
        assert "seasonal_sensitivity" in result
        assert "lifestyle_recommendations" in result

    def test_identify_risk_factors(self, ai_service):
        """测试风险因素识别"""
        risk_factors = ai_service._identify_risk_factors("气虚质", 35, "女")
        
        assert isinstance(risk_factors, list)
        assert len(risk_factors) > 0

    @pytest.mark.asyncio
    async def test_analyze_text_data(self, ai_service):
        """测试文本数据分析"""
        text = "患者主诉头痛、失眠，持续一周，情绪低落"
        
        result = await ai_service._analyze_text_data(text)
        
        assert "keywords" in result
        assert "sentiment" in result
        assert "entities" in result
        assert "text_length" in result
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_analyze_tongue_image(self, ai_service):
        """测试舌诊图像分析"""
        image_data = b"fake_tongue_image"
        
        result = await ai_service._analyze_tongue_image(image_data)
        
        assert "tongue_color" in result
        assert "tongue_coating" in result
        assert "tongue_shape" in result
        assert "health_indicators" in result
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_analyze_face_image(self, ai_service):
        """测试面诊图像分析"""
        image_data = b"fake_face_image"
        
        result = await ai_service._analyze_face_image(image_data)
        
        assert "complexion" in result
        assert "facial_features" in result
        assert "health_indicators" in result
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_fuse_multimodal_results(self, ai_service):
        """测试多模态结果融合"""
        results = {
            "text": {
                "confidence": 0.8,
                "entities": [{"entity": "头痛", "type": "symptom"}]
            },
            "image": {
                "confidence": 0.7
            },
            "audio": {
                "confidence": 0.6
            }
        }
        
        fusion_result = await ai_service._fuse_multimodal_results(results)
        
        assert "fusion_confidence" in fusion_result
        assert "fusion_insights" in fusion_result
        assert "combined_entities" in fusion_result
        assert "recommendation" in fusion_result
        assert fusion_result["fusion_confidence"] > 0

    def test_generate_diagnosis_cache_key(self, ai_service):
        """测试诊断缓存键生成"""
        symptoms = [{"name": "头痛"}, {"name": "失眠"}]
        patient_info = {"constitution_type": "气虚质", "age": 35, "gender": "女"}
        
        key1 = ai_service._generate_diagnosis_cache_key(symptoms, patient_info)
        key2 = ai_service._generate_diagnosis_cache_key(symptoms, patient_info)
        
        assert key1 == key2  # 相同输入应该生成相同的键
        assert key1.startswith("ai_diagnosis:")

    @pytest.mark.asyncio
    async def test_enhanced_knowledge_retrieval(self, ai_service):
        """测试增强知识检索"""
        query = "肝郁脾虚证"
        context = {"patient_age": 35}
        max_results = 10
        
        results = await ai_service._enhanced_knowledge_retrieval(query, context, max_results)
        
        assert isinstance(results, list)
        assert len(results) <= max_results

    @pytest.mark.asyncio
    async def test_generate_enhanced_response(self, ai_service):
        """测试增强回答生成"""
        query = "什么是肝郁脾虚证？"
        retrieval_results = [
            {"id": "syndrome_001", "name": "肝郁脾虚证", "description": "..."}
        ]
        
        response = await ai_service._generate_enhanced_response(query, retrieval_results)
        
        assert "intent" in response
        assert "response" in response
        assert "confidence" in response
        assert "sources" in response
        assert "reasoning" in response

    @pytest.mark.asyncio
    async def test_caching_behavior(self, ai_service, mock_cache_service):
        """测试缓存行为"""
        # 设置缓存返回值
        cached_result = {
            "success": True,
            "diagnosis": {"syndrome": "test"},
            "confidence": 0.8,
            "reasoning": ["cached"]
        }
        mock_cache_service.get.return_value = cached_result
        
        symptoms = [{"name": "头痛", "severity": 3, "duration": "1周"}]
        patient_info = {"constitution_type": "气虚质", "age": 35, "gender": "女"}
        
        result = await ai_service.intelligent_diagnosis(symptoms, patient_info)
        
        # 验证返回了缓存的结果
        assert result == cached_result
        
        # 验证调用了缓存服务
        mock_cache_service.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_handling(self, ai_service, mock_knowledge_service):
        """测试错误处理"""
        # 模拟服务异常
        mock_knowledge_service.get_constitution_by_id.side_effect = Exception("Service error")
        
        symptoms = [{"name": "头痛", "severity": 3, "duration": "1周"}]
        patient_info = {"constitution_type": "气虚质", "age": 35, "gender": "女"}
        
        result = await ai_service.intelligent_diagnosis(symptoms, patient_info)
        
        assert result["success"] is False
        assert "error" in result
        assert result["confidence"] == 0.0 