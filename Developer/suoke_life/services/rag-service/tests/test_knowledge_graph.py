import pytest
from unittest.mock import patch, MagicMock

from src.knowledge_graph.knowledge_graph import KnowledgeGraph, Node, Relation

@pytest.fixture
def mock_neo4j_driver():
    """Neo4j驱动的模拟对象"""
    mock_driver = MagicMock()
    with patch("knowledge_graph.knowledge_graph.GraphDatabase") as mock_db:
        mock_db.driver.return_value = mock_driver
        yield mock_driver

@pytest.fixture
def graph(mock_neo4j_driver):
    """知识图谱实例"""
    return KnowledgeGraph("bolt://localhost:7687", "neo4j", "password")

def test_init(graph):
    """测试初始化"""
    assert graph is not None
    assert graph.driver is not None

def test_add_node(graph):
    """测试添加节点"""
    node = Node(id="1", name="气虚质", type="Constitution")
    success = graph.add_node(node)
    assert success is True

def test_add_relation(graph):
    """测试添加关系"""
    relation = Relation(start_node="1", end_node="2", type="HAS_SYMPTOM")
    success = graph.add_relation(relation)
    assert success is True

def test_get_node(graph):
    """测试获取节点"""
    node = graph.get_node("1")
    assert node is not None

def test_get_neighbors(graph):
    """测试获取邻居节点"""
    neighbors = graph.get_neighbors("1", max_depth=2)
    assert isinstance(neighbors, list)

def test_search_nodes(graph):
    """测试搜索节点"""
    nodes = graph.search_nodes("气虚", node_types=["Constitution"])
    assert isinstance(nodes, list)

def test_update_node(graph):
    """测试更新节点"""
    node = Node(id="1", name="气虚质", type="Constitution")
    success = graph.update_node(node)
    assert success is True

def test_delete_node(graph):
    """测试删除节点"""
    success = graph.delete_node("1")
    assert success is True

def test_delete_relation(graph):
    """测试删除关系"""
    relation = Relation(start_node="1", end_node="2", type="HAS_SYMPTOM")
    success = graph.delete_relation(relation)
    assert success is True

def test_close(graph):
    """测试关闭连接"""
    graph.close()
    assert graph.driver.close.called

def test_error_handling(graph):
    """测试错误处理"""
    graph.driver.session.side_effect = Exception("Database error")
    assert graph.add_node(Node(id="1", name="test", type="test")) is False
    assert graph.get_node("1") is None
    assert len(graph.search_nodes("test")) == 0
    assert graph.update_node(Node(id="1", name="test", type="test")) is False
    assert graph.delete_node("1") is False 