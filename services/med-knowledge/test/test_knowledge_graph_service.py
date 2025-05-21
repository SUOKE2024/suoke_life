import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.knowledge_graph_service import KnowledgeGraphService


class TestKnowledgeGraphService:
    """知识图谱服务测试类"""
    
    @pytest.fixture
    def repository_mock(self):
        """创建仓库Mock"""
        mock = AsyncMock()
        
        # 设置基本返回值
        mock.get_node_count.return_value = 1000
        mock.get_relationship_count.return_value = 2500
        mock.get_node_types_count.return_value = [
            {"type": "Constitution", "count": 9},
            {"type": "Herb", "count": 100}
        ]
        mock.get_relationship_types_count.return_value = [
            {"type": "RECOMMENDS", "count": 50},
            {"type": "TREATS", "count": 150}
        ]
        
        return mock
    
    @pytest.fixture
    def service(self, repository_mock):
        """创建服务实例"""
        return KnowledgeGraphService(repository_mock)
    
    @pytest.mark.asyncio
    async def test_get_graph_statistics(self, service, repository_mock):
        """测试获取图谱统计信息"""
        # 设置Mock返回值
        repository_mock.get_node_count.return_value = 5000
        repository_mock.get_relationship_count.return_value = 8000
        repository_mock.get_node_type_statistics.return_value = {
            "Constitution": 9,
            "Syndrome": 50,
            "Herb": 300
        }
        repository_mock.get_relationship_type_statistics.return_value = {
            "HAS_SYMPTOM": 200,
            "TREATS": 150
        }
        
        # 调用服务方法
        result = await service.get_graph_statistics()
        
        # 验证结果
        assert result["node_count"] == 5000
        assert result["relationship_count"] == 8000
        assert result["node_types"]["Constitution"] == 9
        assert result["relationship_types"]["TREATS"] == 150
        
        # 验证方法调用
        repository_mock.get_node_count.assert_called_once()
        repository_mock.get_relationship_count.assert_called_once()
        repository_mock.get_node_type_statistics.assert_called_once()
        repository_mock.get_relationship_type_statistics.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_graph_visualization_data(self, service, repository_mock):
        """测试获取图谱可视化数据"""
        # 设置Mock返回值
        mock_data = {
            "nodes": [
                {"id": "c1", "label": "Constitution", "name": "平和质"},
                {"id": "s1", "label": "Syndrome", "name": "肝郁脾虚证"}
            ],
            "edges": [
                {"source": "c1", "target": "s1", "type": "TENDS_TO_DEVELOP"}
            ]
        }
        repository_mock.get_visualization_data.return_value = mock_data
        
        # 调用服务方法
        limit = 100
        relationships = ["TENDS_TO_DEVELOP", "HAS_SYMPTOM"]
        result = await service.get_visualization_data(limit, relationships)
        
        # 验证结果
        assert result == mock_data
        repository_mock.get_visualization_data.assert_called_once_with(limit, relationships)
    
    @pytest.mark.asyncio
    async def test_find_path_between_nodes(self, service, repository_mock):
        """测试查找节点间路径"""
        # 设置Mock返回值
        mock_paths = [
            [
                {"id": "c1", "type": "Constitution", "name": "平和质"},
                {"relationship": "TENDS_TO_DEVELOP", "direction": "outgoing"},
                {"id": "s1", "type": "Syndrome", "name": "肝郁脾虚证"}
            ]
        ]
        repository_mock.find_paths.return_value = mock_paths
        
        # 调用服务方法
        source_id = "c1"
        target_id = "s1"
        max_depth = 3
        result = await service.find_paths(source_id, target_id, max_depth)
        
        # 验证结果
        assert result == mock_paths
        repository_mock.find_paths.assert_called_once_with(source_id, target_id, max_depth)
    
    @pytest.mark.asyncio
    async def test_get_node_relationships(self, service, repository_mock):
        """测试获取节点关系"""
        # 设置Mock返回值
        mock_relationships = [
            {
                "source": {"id": "c1", "type": "Constitution", "name": "平和质"},
                "relationship": "TENDS_TO_DEVELOP",
                "target": {"id": "s1", "type": "Syndrome", "name": "肝郁脾虚证"}
            }
        ]
        repository_mock.get_node_relationships.return_value = mock_relationships
        
        # 调用服务方法
        node_id = "c1"
        relationship_types = ["TENDS_TO_DEVELOP"]
        direction = "outgoing"
        result = await service.get_node_relationships(node_id, relationship_types, direction)
        
        # 验证结果
        assert result == mock_relationships
        repository_mock.get_node_relationships.assert_called_once_with(
            node_id, relationship_types, direction
        )
    
    @pytest.mark.asyncio
    async def test_execute_cypher_query(self, service, repository_mock):
        """测试执行Cypher查询"""
        # 设置Mock返回值
        mock_result = [
            {"name": "平和质", "prevalence": 0.3},
            {"name": "气虚质", "prevalence": 0.2}
        ]
        repository_mock.execute_cypher.return_value = mock_result
        
        # 调用服务方法
        cypher = "MATCH (c:Constitution) RETURN c.name as name, c.prevalence as prevalence"
        params = {}
        result = await service.execute_cypher(cypher, params)
        
        # 验证结果
        assert result == mock_result
        repository_mock.execute_cypher.assert_called_once_with(cypher, params)
    
    @pytest.mark.asyncio
    async def test_get_knowledge_subgraph(self, service, repository_mock):
        """测试获取知识子图"""
        # 设置Mock返回值
        mock_subgraph = {
            "nodes": [
                {"id": "c1", "label": "Constitution", "name": "平和质"},
                {"id": "s1", "label": "Syndrome", "name": "肝郁脾虚证"}
            ],
            "edges": [
                {"source": "c1", "target": "s1", "type": "TENDS_TO_DEVELOP"}
            ]
        }
        repository_mock.get_entity_subgraph.return_value = mock_subgraph
        
        # 调用服务方法
        entity_type = "Constitution"
        entity_id = "c1"
        depth = 2
        relationship_types = ["TENDS_TO_DEVELOP"]
        result = await service.get_entity_subgraph(entity_type, entity_id, depth, relationship_types)
        
        # 验证结果
        assert result == mock_subgraph
        repository_mock.get_entity_subgraph.assert_called_once_with(
            entity_type, entity_id, depth, relationship_types
        )
    
    @pytest.mark.asyncio
    async def test_get_entity_neighbors(self, service, repository_mock):
        """测试获取实体邻居"""
        # 设置Mock返回值
        mock_neighbors = [
            {"id": "s1", "type": "Syndrome", "name": "肝郁脾虚证", "relationship": "TENDS_TO_DEVELOP"}
        ]
        repository_mock.get_entity_neighbors.return_value = mock_neighbors
        
        # 调用服务方法
        entity_type = "Constitution"
        entity_id = "c1"
        relationship_types = ["TENDS_TO_DEVELOP"]
        neighbor_types = ["Syndrome"]
        result = await service.get_entity_neighbors(
            entity_type, entity_id, relationship_types, neighbor_types
        )
        
        # 验证结果
        assert result == mock_neighbors
        repository_mock.get_entity_neighbors.assert_called_once_with(
            entity_type, entity_id, relationship_types, neighbor_types
        )
    
    @pytest.mark.asyncio
    async def test_get_related_entities(self, service, repository_mock):
        """测试获取相关实体"""
        # 设置Mock返回值
        mock_entities = [
            {"id": "s1", "name": "肝郁脾虚证", "relevance_score": 0.85}
        ]
        repository_mock.get_related_entities.return_value = mock_entities
        
        # 调用服务方法
        source_type = "Constitution"
        source_id = "c1"
        target_type = "Syndrome"
        min_relevance = 0.7
        limit = 10
        result = await service.get_related_entities(
            source_type, source_id, target_type, min_relevance, limit
        )
        
        # 验证结果
        assert result == mock_entities
        repository_mock.get_related_entities.assert_called_once_with(
            source_type, source_id, target_type, min_relevance, limit
        )
    
    @pytest.mark.asyncio
    async def test_get_shortest_path(self, service, repository_mock):
        """测试获取两个节点之间的最短路径"""
        # 设置Mock返回值
        mock_path = [
            {"id": "c1", "type": "Constitution", "name": "平和质"},
            {"relationship": "TENDS_TO_DEVELOP", "direction": "outgoing"},
            {"id": "s1", "type": "Syndrome", "name": "肝郁脾虚证"}
        ]
        repository_mock.get_shortest_path.return_value = mock_path
        
        # 调用服务方法
        source_id = "c1"
        target_id = "s1"
        relationship_types = ["TENDS_TO_DEVELOP"]
        result = await service.get_shortest_path(source_id, target_id, relationship_types)
        
        # 验证结果
        assert result == mock_path
        repository_mock.get_shortest_path.assert_called_once_with(
            source_id, target_id, relationship_types
        )
    
    @pytest.mark.asyncio
    async def test_get_common_neighbors(self, service, repository_mock):
        """测试获取两个节点的共同邻居"""
        # 设置Mock返回值
        mock_neighbors = [
            {"id": "h1", "type": "Herb", "name": "当归", "relationships": ["TREATS", "TREATS"]}
        ]
        repository_mock.get_common_neighbors.return_value = mock_neighbors
        
        # 调用服务方法
        node1_id = "s1"
        node2_id = "s2"
        relationship_types = ["TREATS"]
        result = await service.get_common_neighbors(node1_id, node2_id, relationship_types)
        
        # 验证结果
        assert result == mock_neighbors
        repository_mock.get_common_neighbors.assert_called_once_with(
            node1_id, node2_id, relationship_types
        )
    
    @pytest.mark.asyncio
    async def test_exception_handling(self, service, repository_mock):
        """测试异常处理"""
        # 设置Mock抛出异常
        repository_mock.get_graph_statistics.side_effect = Exception("数据库错误")
        
        # 调用服务方法
        result = await service.get_graph_statistics()
        
        # 验证结果：应当返回空结果而不是抛出异常
        assert "node_count" in result
        assert result["node_count"] == 0
        assert len(result["node_types"]) == 0 