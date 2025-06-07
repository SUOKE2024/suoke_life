#!/usr/bin/env python3
"""
知识图谱模块 - 提供中医知识图谱管理功能
"""

import time
from typing import Any

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class KnowledgeGraph:
    """知识图谱管理器"""

    def __init__(self):
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: dict[str, list[dict[str, Any]]] = {}
        self.initialized = False

    async def initialize(self):
        """初始化知识图谱"""
        try:
            # 加载基础知识
            await self._load_basic_knowledge()

            # 构建关系网络
            await self._build_relationships()

            self.initialized = True
            logger.info("知识图谱初始化完成")

        except Exception as e:
            logger.error(f"知识图谱初始化失败: {e}")
            raise

    async def _load_basic_knowledge(self):
        """加载基础知识"""
        # 加载症状知识
        symptoms = [
            {"id": "symptom_001", "name": "头痛", "category": "神经系统"},
            {"id": "symptom_002", "name": "发热", "category": "全身症状"},
            {"id": "symptom_003", "name": "咳嗽", "category": "呼吸系统"},
        ]

        for symptom in symptoms:
            self.add_node(symptom["id"], "symptom", symptom)

        # 加载体质知识
        constitutions = [
            {"id": "constitution_001", "name": "平和质", "description": "阴阳气血调和"},
            {"id": "constitution_002", "name": "气虚质", "description": "元气不足"},
        ]

        for constitution in constitutions:
            self.add_node(constitution["id"], "constitution", constitution)

    async def _build_relationships(self):
        """构建关系网络"""
        # 症状与体质的关系
        relationships = [
            {"from": "symptom_001", "to": "constitution_002", "relation": "indicates", "weight": 0.7},
            {"from": "symptom_002", "to": "constitution_001", "relation": "indicates", "weight": 0.5},
        ]

        for rel in relationships:
            self.add_edge(rel["from"], rel["to"], rel["relation"], rel["weight"])

    def add_node(self, node_id: str, node_type: str, properties: dict[str, Any]):
        """添加节点"""
        self.nodes[node_id] = {
            "id": node_id,
            "type": node_type,
            "properties": properties,
            "created_at": time.time(),
        }

    def add_edge(self, from_node: str, to_node: str, relation: str, weight: float = 1.0):
        """添加边"""
        if from_node not in self.edges:
            self.edges[from_node] = []

        self.edges[from_node].append({
            "to": to_node,
            "relation": relation,
            "weight": weight,
            "created_at": time.time(),
        })

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        """获取节点"""
        return self.nodes.get(node_id)

    def get_related_nodes(self, node_id: str, relation: str | None = None) -> list[dict[str, Any]]:
        """获取相关节点"""
        related = []

        if node_id in self.edges:
            for edge in self.edges[node_id]:
                if relation is None or edge["relation"] == relation:
                    target_node = self.get_node(edge["to"])
                    if target_node:
                        related.append({
                            "node": target_node,
                            "relation": edge["relation"],
                            "weight": edge["weight"],
                        })

        return related

    def query_symptoms_by_constitution(self, constitution_type: str) -> list[dict[str, Any]]:
        """根据体质查询相关症状"""
        symptoms = []

        # 查找体质节点
        constitution_node = None
        for node_id, node in self.nodes.items():
            if (node["type"] == "constitution" and
                node["properties"].get("name") == constitution_type):
                constitution_node = node_id
                break

        if constitution_node:
            # 查找指向该体质的症状
            for from_node, edges in self.edges.items():
                for edge in edges:
                    if edge["to"] == constitution_node and edge["relation"] == "indicates":
                        symptom_node = self.get_node(from_node)
                        if symptom_node and symptom_node["type"] == "symptom":
                            symptoms.append({
                                "symptom": symptom_node["properties"],
                                "weight": edge["weight"],
                            })

        return symptoms

    def get_graph_stats(self) -> dict[str, Any]:
        """获取图谱统计信息"""
        node_types = {}
        for node in self.nodes.values():
            node_type = node["type"]
            node_types[node_type] = node_types.get(node_type, 0) + 1

        return {
            "total_nodes": len(self.nodes),
            "total_edges": sum(len(edges) for edges in self.edges.values()),
            "node_types": node_types,
            "initialized": self.initialized,
        }

    async def cleanup(self):
        """清理资源"""
        self.nodes.clear()
        self.edges.clear()
        self.initialized = False
        logger.info("知识图谱资源已清理")


# 全局知识图谱实例
_knowledge_graph: KnowledgeGraph | None = None


def get_knowledge_graph() -> KnowledgeGraph:
    """获取知识图谱实例"""
    global _knowledge_graph
    if _knowledge_graph is None:
        _knowledge_graph = KnowledgeGraph()
    return _knowledge_graph


async def cleanup_knowledge_graph():
    """清理知识图谱资源"""
    global _knowledge_graph
    if _knowledge_graph:
        await _knowledge_graph.cleanup()
        _knowledge_graph = None
