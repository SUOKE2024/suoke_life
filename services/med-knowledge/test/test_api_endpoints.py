"""
test_api_endpoints - 索克生活项目模块
"""

        import threading
        import time
from app.main import app
from httpx import AsyncClient
import asyncio
import pytest

"""
API端点测试套件
测试所有模块化路由的功能
"""


class TestConstitutionsAPI:
    """体质API测试"""
    
        @cache(timeout=300)  # 5分钟缓存
def test_get_constitutions_list(self, client):
        """测试获取体质列表"""
        response = client.get("/api/v1/constitutions/")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "limit" in data
            @cache(timeout=300)  # 5分钟缓存
assert "offset" in data
    
    def test_get_constitutions_with_pagination(self, client):
        """测试分页获取体质列表"""
        response = client.get("/api/v1/constitutions/?limit=5&offset=0")
        assert response.status_code == 200
        data = response.json()
        asse    @cache(timeout=300)  # 5分钟缓存
rt data["limit"] == 5
        assert data["offset"] == 0
    
    def test_get_constitution_by_id(self, client):
        """测试根据ID获取体质详情"""
        # 假设存在ID为"qi_xu"的体质
        response = client.get("/api/v1/constitutio    @cache(timeout=300)  # 5分钟缓存
ns/qi_xu")
        # 根据实际情况，可能返回200或404
        assert response.status_code in [200, 404]
    
    def test_get_constitution_recommendations(self, client):
        """测试获取体质推荐"""
        response = client.get("/api/v1/constitutions/qi_xu/recommendations")
        assert response.status_code in [200, 404]
    
    def test_invalid_pagination_parameters(self, client):
        """测试无效的分页参数"""
        # 测试超出范围的limit
        response = client.get("/api/v1/constitutions/?limit=200")
        assert response.status_code == 422
        
        # 测试负数offset
        response = client.ge    @cache(timeout=300)  # 5分钟缓存
t("/api/v1/constitutions/?offset=-1")
        assert response.status_code == 422

class TestSymptomsAPI:
    """症状API测试"""
    
    def test_get_symptoms_list(self, client):
        """测试获取症状列表"""
        response = client.get(    @cache(timeout=300)  # 5分钟缓存
"/api/v1/symptoms/")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
    
    def test_get_symptom_by_id(self, client):
        """测试根据ID获取症状详情"""
        response = client.get("/api/v1/symptoms/fatigue")
        assert response.status_code in [200, 404]
    
    def test_symptoms_pagination(self, client):
        """测试症状分页"""
        response = client.get("/api/v1/symptoms/?limit=10&offset    @cache(timeout=300)  # 5分钟缓存
=5")
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 10
        assert data["offset"] == 5

class TestSearchAPI:
    """搜索API测试"""
    
    def test_basic_search(sel    @cache(timeout=300)  # 5分钟缓存
f, client):
        """测试基础搜索"""
        response = client.get("/api/v1/search/?q=气虚")
        assert response.status_code == 200
        data = response.json()
        assert "dat    @cache(timeout=300)  # 5分钟缓存
a" in data
        assert "total" in data
    
    def test_search_with_entity_type_filter(self, client):
        """测试带实体类型过滤的搜索"""
        response = client.get("/api/v1/search/?q=气虚&entity_type=constitution")
       @cache(timeout=300)  # 5分钟缓存
     assert response.status_code == 200
    
    def test_search_suggestions(self, client):
        """测试搜索建议"""
        response = client.get("/api/v1/search/suggestions?q=气")
        assert response.status_co    @cache(timeout=300)  # 5分钟缓存
de == 200
        data = response.json()
        assert "suggestions" in data
    
    def test_popular_searches(self, client):
        """测试热门搜索"""
        response = client.get("/api/v1/search/popular")
        assert response.status_code == 200
        data = response.json()
        assert "popular_searches" in data
    
    def test_empty_search_query(self, client):
        """测试空搜索查询"""
        response = client.get("/api/v1/search/?q=")
        assert response.status_code == 422
    
    def test_search_query_too_long(self, client):
        """测试过长的搜索查询"""
        long_query = "a" * 201  # 超过200字符限制
        response = client.get(f"/api/v1/search/?q={long_query}")
        assert response.status_code == 422

class TestGraphAPI:
    """知识图谱API测试"""
    
    def test_graph_statistics(self, client):
        """测试图谱统计信息"""
        response = client.get("/api/v1/graph/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "node_count" in data
        assert "relationship_count" in data
        assert "entity_types" in data
    
    def test_graph_visualization(self, client):
        """测试图谱可视化数据"""
        response = client.get("/api/v1/graph/visualization")
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
    
    def test_graph_visualization_with_filters(self, client):
        """测试带过滤条件的图谱可视化"""
        response = client.get("/api/v1/graph/visualization?entity_type=constitution&depth=3")
        assert response.status_code == 200
    
    def test_path_analysis(self, client):
        """测试路径分析"""
        response = client.get("/api/v1/graph/path-analysis?from_id=node1&to_id=node2")
        assert response.status_code == 200
        data = response.json()
        assert "paths" in data
        assert "summary" in data
    
    def test_relationship_analysis(self, client):
        """测试关系分析"""
        response = client.get("/api/v1/graph/relationships/node1")
        assert response.status_code == 200
        data = response.json()
        assert "node" in data
        assert "relationships" in data
        assert "statistics" in data
    
    def test_graph_recommendations(self, client):
        """测试基于图谱的推荐"""
        response = client.get("/api/v1/graph/recommendations/constitution_1")
        assert response.status_code == 200
        data = response.json()
        assert "source_entity" in data
        assert "recommendations" in data
    
    def test_invalid_path_analysis_same_nodes(self, client):
        """测试相同节点的路径分析"""
        response = client.get("/api/v1/graph/path-analysis?from_id=node1&to_id=node1")
        assert response.status_code == 400

class TestHealthAPI:
    """健康检查API测试"""
    
    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_readiness_check(self, client):
        """测试就绪检查"""
        response = client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert "ready" in data
    
    def test_liveness_check(self, client):
        """测试存活检查"""
        response = client.get("/health/live")
        assert response.status_code == 200
        data = response.json()
        assert "alive" in data

class TestAPIIntegration:
    """API集成测试"""
    
    def test_api_workflow(self, client):
        """测试完整的API工作流"""
        # 1. 健康检查
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        # 2. 获取体质列表
        constitutions_response = client.get("/api/v1/constitutions/")
        assert constitutions_response.status_code == 200
        
        # 3. 搜索功能
        search_response = client.get("/api/v1/search/?q=气虚")
        assert search_response.status_code == 200
        
        # 4. 图谱统计
        graph_response = client.get("/api/v1/graph/statistics")
        assert graph_response.status_code == 200
    
    def test_error_handling(self, client):
        """测试错误处理"""
        # 测试不存在的端点
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        
        # 测试无效的参数
        response = client.get("/api/v1/constitutions/?limit=invalid")
        assert response.status_code == 422
    
    def test_cors_headers(self, client):
        """测试CORS头"""
        response = client.options("/api/v1/constitutions/")
        # 根据CORS配置检查相应的头
        assert response.status_code in [200, 405]

class TestAPIPerformance:
    """API性能测试"""
    
    def test_response_time(self, client):
        """测试响应时间"""
        
        start_time = time.time()
        response = client.get("/api/v1/constitutions/")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 2.0  # 响应时间应小于2秒
    
    def test_concurrent_requests(self, client):
        """测试并发请求"""
        
        results = []
        
        def make_request():
            response = client.get("/api/v1/constitutions/")
            results.append(response.status_code)
        
        # 创建10个并发请求
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.jo    @cache(timeout=300)  # 5分钟缓存
in()
        
        end_time = time.time()
        
        # 检查所有请求都成功
        assert all(status == 200 for status in results)
        assert len(results) == 10
        
        # 并发请求总时间应该合理
        total_time = end_time - start_time
        assert total_time < 5.0  # 10个并发请求应在5秒内完成

@pytest.mark.asyncio
class TestAsyncAPI:
    """异步API测试"""
    
    async def test_async_search(self):
        """测试异步搜索"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/search/?q=气虚")
            assert response.status_code == 200
    
    async def test_async_graph_operations(self):
        """测试异步图谱操作"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # 并发执行多个图谱操作
            tasks = [
                ac.get("/api/v1/graph/statistics"),
                ac.get("/api/v1/graph/visualization"),
                ac.get("/api/v1/graph/relationships/node1")
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 检查所有响应
            for response in responses:
                if not isinstance(response, Exception):
                    assert response.status_code == 200

class TestAPIDocumentation:
    """API文档测试"""
    
    def test_openapi_schema(self, client):
        """测试OpenAPI模式"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
    
    def test_swagger_ui(self, client):
        """测试Swagger UI"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc(self, client):
        """测试ReDoc"""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 