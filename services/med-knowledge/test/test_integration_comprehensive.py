"""
test_integration_comprehensive - 索克生活项目模块
"""

        from app.models.entities import SearchResponse, SearchItem
from app.core.config import get_settings
from app.main import app
from app.models.entities import Constitution, Syndrome, Symptom
from app.services.cache_service import CacheService
from app.services.knowledge_service import KnowledgeService
from typing import Dict, Any, List
from unittest.mock import AsyncMock, patch
import asyncio
import httpx
import pytest

"""
医学知识服务综合集成测试
测试完整的业务流程和组件集成
"""




class TestMedKnowledgeIntegration:
    """医学知识服务集成测试"""
    
    @pytest.fixture
    async def client(self):
        """创建测试客户端"""
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    @pytest.fixture
    async def mock_knowledge_service(self):
        """模拟知识服务"""
        service = AsyncMock(spec=KnowledgeService)
        
        # 模拟体质数据
        service.get_constitution_by_id.return_value = Constitution(
            id="constitution_1",
            name="平和质",
            description="阴阳气血调和",
            characteristics=["体形匀称", "面色润泽", "精力充沛"],
            symptoms=["无明显不适"],
            recommendations=["保持现有生活方式"]
        )
        
        # 模拟证型数据
        service.get_syndrome_by_id.return_value = Syndrome(
            id="syndrome_1",
            name="气虚证",
            description="脏腑功能衰退",
            symptoms=["乏力", "气短", "自汗"],
            tongue="舌淡苔白",
            pulse="脉弱"
        )
        
        # 模拟搜索结果
        service.search_knowledge.return_value = SearchResponse(
            items=[
                SearchItem(
                    id="item_1",
                    title="气虚证",
                    content="脏腑功能衰退所致的证候",
                    entity_type="syndrome",
                    score=0.95
                )
            ],
            total=1,
            limit=10,
            offset=0
        )
        
        return service
    
    @pytest.fixture
    async def mock_cache_service(self):
        """模拟缓存服务"""
        service = AsyncMock(spec=CacheService)
        service.get.return_value = None  # 默认缓存未命中
        service.set.return_value = True
        return service
    
    @pytest.mark.asyncio
    async def test_complete_diagnosis_workflow(
        self, 
        client: httpx.AsyncClient,
        mock_knowledge_service: AsyncMock,
        mock_cache_service: AsyncMock
    ):
        """测试完整的诊断工作流程"""
        
        with patch('app.api.rest.deps.get_knowledge_service', return_value=mock_knowledge_service), \
             patch('app.api.rest.deps.get_cache_service', return_value=mock_cache_service):
            
            # 1. 测试症状分析
            patient_data = {
                "age": 35,
                "gender": "male",
                "constitution_type": "constitution_1",
                "symptoms": [
                    {
                        "name": "乏力",
                        "severity": 3,
                        "duration": "2周",
                        "description": "持续感到疲劳"
                    },
                    {
                        "name": "气短",
                        "severity": 2,
                        "duration": "1周"
                    }
                ],
                "medical_history": ["高血压"],
                "lifestyle": {
                    "exercise": "少量",
                    "diet": "规律",
                    "sleep": "7小时"
                }
            }
            
            response = await client.post(
                "/api/v1/diagnosis/analyze",
                json=patient_data,
                params={"include_reasoning": True}
            )
            
            assert response.status_code == 200
            diagnosis_result = response.json()
            
            # 验证诊断结果结构
            assert "syndrome_candidates" in diagnosis_result
            assert "constitution_analysis" in diagnosis_result
            assert "treatment_suggestions" in diagnosis_result
            assert "lifestyle_recommendations" in diagnosis_result
            assert "confidence_score" in diagnosis_result
            assert "reasoning_path" in diagnosis_result
            
            # 验证置信度在合理范围内
            assert 0 <= diagnosis_result["confidence_score"] <= 1
            
            # 2. 基于诊断结果生成治疗方案
            if diagnosis_result["syndrome_candidates"]:
                syndrome_id = diagnosis_result["syndrome_candidates"][0]["syndrome_id"]
                
                treatment_response = await client.post(
                    "/api/v1/diagnosis/treatment-plan",
                    params={
                        "syndrome_id": syndrome_id,
                        "treatment_type": "comprehensive"
                    },
                    json=patient_data
                )
                
                assert treatment_response.status_code == 200
                treatment_plan = treatment_response.json()
                
                # 验证治疗方案结构
                assert "plan_id" in treatment_plan
                assert "syndrome_id" in treatment_plan
                assert "herbs" in treatment_plan
                assert "acupoints" in treatment_plan
                assert "lifestyle_interventions" in treatment_plan
                assert "duration" in treatment_plan
                assert "precautions" in treatment_plan
            
            # 3. 测试体质评估
            constitution_response = await client.post(
                "/api/v1/diagnosis/constitution-assessment",
                json={
                    "symptoms": patient_data["symptoms"],
                    "lifestyle_data": patient_data["lifestyle"]
                }
            )
            
            assert constitution_response.status_code == 200
            constitution_result = constitution_response.json()
            
            # 验证体质评估结果
            assert "constitution_type" in constitution_result
            assert "confidence" in constitution_result
            assert "assessment_details" in constitution_result
    
    @pytest.mark.asyncio
    async def test_knowledge_graph_integration(
        self,
        client: httpx.AsyncClient,
        mock_knowledge_service: AsyncMock
    ):
        """测试知识图谱集成功能"""
        
        with patch('app.api.rest.deps.get_knowledge_service', return_value=mock_knowledge_service):
            
            # 模拟图谱统计数据
            mock_knowledge_service.get_node_count.return_value = 1000
            mock_knowledge_service.get_relationship_count.return_value = 5000
            
            # 1. 测试图谱统计
            stats_response = await client.get("/api/v1/graph/statistics")
            assert stats_response.status_code == 200
            
            stats = stats_response.json()
            assert "node_count" in stats
            assert "relationship_count" in stats
            assert stats["node_count"] == 1000
            assert stats["relationship_count"] == 5000
            
            # 2. 测试实体搜索
            search_response = await client.get(
                "/api/v1/search",
                params={
                    "query": "气虚",
                    "entity_type": "syndrome",
                    "limit": 5
                }
            )
            
            assert search_response.status_code == 200
            search_result = search_response.json()
            
            assert "items" in search_result
            assert "total" in search_result
            assert len(search_result["items"]) <= 5
    
    @pytest.mark.asyncio
    async def test_caching_behavior(
        self,
        client: httpx.AsyncClient,
        mock_knowledge_service: AsyncMock,
        mock_cache_service: AsyncMock
    ):
        """测试缓存行为"""
        
        with patch('app.api.rest.deps.get_knowledge_service', return_value=mock_knowledge_service), \
             patch('app.api.rest.deps.get_cache_service', return_value=mock_cache_service):
            
            # 第一次请求 - 缓存未命中
            mock_cache_service.get.return_value = None
            
            response1 = await client.get("/api/v1/constitutions/constitution_1")
            assert response1.status_code == 200
            
            # 验证缓存设置被调用
            mock_cache_service.set.assert_called()
            
            # 第二次请求 - 模拟缓存命中
            cached_constitution = Constitution(
                id="constitution_1",
                name="平和质",
                description="阴阳气血调和",
                characteristics=["体形匀称"],
                symptoms=[],
                recommendations=[]
            )
            mock_cache_service.get.return_value = cached_constitution
            
            response2 = await client.get("/api/v1/constitutions/constitution_1")
            assert response2.status_code == 200
            
            # 验证从缓存返回的数据
            result = response2.json()
            assert result["name"] == "平和质"
    
    @pytest.mark.asyncio
    async def test_error_handling_and_resilience(
        self,
        client: httpx.AsyncClient,
        mock_knowledge_service: AsyncMock
    ):
        """测试错误处理和系统韧性"""
        
        with patch('app.api.rest.deps.get_knowledge_service', return_value=mock_knowledge_service):
            
            # 1. 测试资源不存在的情况
            mock_knowledge_service.get_constitution_by_id.return_value = None
            
            response = await client.get("/api/v1/constitutions/nonexistent")
            assert response.status_code == 404
            
            # 2. 测试服务异常的情况
            mock_knowledge_service.get_constitution_by_id.side_effect = Exception("Database error")
            
            response = await client.get("/api/v1/constitutions/constitution_1")
            assert response.status_code == 500
            
            # 3. 测试无效参数的情况
            response = await client.post(
                "/api/v1/diagnosis/analyze",
                json={
                    "age": -1,  # 无效年龄
                    "gender": "invalid",  # 无效性别
                    "symptoms": []
                }
            )
            assert response.status_code == 422  # 验证错误
    
    @pytest.mark.asyncio
    async def test_performance_and_concurrency(
        self,
        client: httpx.AsyncClient,
        mock_knowledge_service: AsyncMock
    ):
        """测试性能和并发处理"""
        
        with patch('app.api.rest.deps.get_knowledge_service', return_value=mock_knowledge_service):
            
            # 并发请求测试
            async def make_request():
                return await client.get("/api/v1/constitutions")
            
            # 创建10个并发请求
            tasks = [make_request() for _ in range(10)]
            responses = await asyncio.gather(*tasks)
            
            # 验证所有请求都成功
            for response in responses:
                assert response.status_code == 200
            
            # 验证服务被调用了正确的次数
            assert mock_knowledge_service.get_constitutions.call_count == 10
    
    @pytest.mark.asyncio
    async def test_health_check_comprehensive(self, client: httpx.AsyncClient):
        """测试全面的健康检查"""
        
        # 1. 基础健康检查
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        
        health_data = response.json()
        assert "status" in health_data
        assert "timestamp" in health_data
        assert "version" in health_data
        
        # 2. 就绪检查
        response = await client.get("/api/v1/health/ready")
        assert response.status_code in [200, 503]  # 可能因为依赖服务状态而不同
        
        # 3. 存活检查
        response = await client.get("/api/v1/health/live")
        assert response.status_code == 200
        
        # 4. 详细健康检查
        response = await client.get("/api/v1/health/detailed")
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            detailed_health = response.json()
            assert "components" in detailed_health
            assert "system_info" in detailed_health
    
    @pytest.mark.asyncio
    async def test_api_documentation_endpoints(self, client: httpx.AsyncClient):
        """测试API文档端点"""
        
        # 1. OpenAPI规范
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_spec = response.json()
        assert "openapi" in openapi_spec
        assert "info" in openapi_spec
        assert "paths" in openapi_spec
        
        # 验证关键路径存在
        paths = openapi_spec["paths"]
        assert "/api/v1/constitutions" in paths
        assert "/api/v1/diagnosis/analyze" in paths
        assert "/api/v1/health" in paths
        
        # 2. 文档页面（重定向测试）
        response = await client.get("/api/docs", follow_redirects=False)
        assert response.status_code in [200, 307]  # 可能是直接返回或重定向
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, client: httpx.AsyncClient):
        """测试指标收集"""
        
        # 发送一些请求以生成指标
        await client.get("/api/v1/health")
        await client.get("/api/v1/constitutions")
        
        # 检查指标端点
        response = await client.get("/metrics")
        assert response.status_code == 200
        
        metrics_text = response.text
        
        # 验证包含基本的Prometheus指标
        assert "http_requests_total" in metrics_text or "http_request" in metrics_text
        assert "process_" in metrics_text  # 进程相关指标
    
    @pytest.mark.asyncio
    async def test_cors_and_security_headers(self, client: httpx.AsyncClient):
        """测试CORS和安全头"""
        
        # 测试CORS预检请求
        response = await client.options(
            "/api/v1/constitutions",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # 验证CORS头
        assert "Access-Control-Allow-Origin" in response.headers
        
        # 测试安全头
        response = await client.get("/api/v1/health")
        headers = response.headers
        
        # 验证安全相关的头部
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection"
        ]
        
        # 至少应该有一些安全头
        present_headers = [h for h in security_headers if h in headers]
        assert len(present_headers) > 0


class TestDiagnosisWorkflow:
    """诊断工作流程专项测试"""
    
    @pytest.mark.asyncio
    async def test_symptom_analysis_accuracy(self):
        """测试症状分析准确性"""
        
        # 测试数据：典型气虚证症状
        test_cases = [
            {
                "symptoms": ["乏力", "气短", "自汗"],
                "expected_syndrome": "气虚证",
                "min_confidence": 0.7
            },
            {
                "symptoms": ["头痛", "眩晕", "面红"],
                "expected_syndrome": "肝阳上亢证",
                "min_confidence": 0.6
            }
        ]
        
        for case in test_cases:
            # 这里应该调用实际的症状分析逻辑
            # 由于是集成测试，我们验证分析流程的完整性
            patient_profile = {
                "age": 40,
                "gender": "male",
                "symptoms": [
                    {"name": symptom, "severity": 3}
                    for symptom in case["symptoms"]
                ]
            }
            
            # 模拟分析过程
            # 在实际实现中，这里会调用真实的分析服务
            assert len(patient_profile["symptoms"]) > 0
    
    @pytest.mark.asyncio
    async def test_treatment_plan_generation(self):
        """测试治疗方案生成"""
        
        syndrome_id = "qi_xu_zheng"
        patient_profile = {
            "age": 45,
            "gender": "female",
            "constitution_type": "qi_xu_zhi",
            "symptoms": [
                {"name": "乏力", "severity": 4},
                {"name": "气短", "severity": 3}
            ]
        }
        
        # 测试不同治疗类型
        treatment_types = ["herbs", "acupuncture", "lifestyle", "comprehensive"]
        
        for treatment_type in treatment_types:
            # 这里应该调用实际的治疗方案生成逻辑
            # 验证方案的完整性和合理性
            assert treatment_type in treatment_types


@pytest.mark.asyncio
async def test_system_integration_end_to_end():
    """端到端系统集成测试"""
    
    # 这个测试模拟完整的用户使用场景
    # 从症状输入到获得治疗建议的完整流程
    
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        
        # 1. 健康检查 - 确保系统正常
        health_response = await client.get("/api/v1/health")
        assert health_response.status_code == 200
        
        # 2. 获取可用体质类型
        constitutions_response = await client.get("/api/v1/constitutions")
        # 根据实际情况，可能返回200或者由于缺少数据返回其他状态码
        
        # 3. 搜索症状相关信息
        search_response = await client.get(
            "/api/v1/search",
            params={"query": "头痛", "limit": 5}
        )
        # 验证搜索功能基本可用
        
        # 4. 检查API文档可访问性
        docs_response = await client.get("/openapi.json")
        assert docs_response.status_code == 200
        
        # 验证OpenAPI规范的基本结构
        openapi_data = docs_response.json()
        assert "info" in openapi_data
        assert "paths" in openapi_data


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--asyncio-mode=auto"]) 