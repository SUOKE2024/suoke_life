#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识图谱索引器 - 中医知识的图谱化存储和检索系统
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
from loguru import logger

from ..service.embedding_service import EmbeddingService
    KnowledgeGraphNode, KnowledgeGraphRelation, 
    Syndrome, SingleHerb, HerbFormula, Symptom,
    ConstitutionType, PathologicalFactor
)

class NodeType(Enum):
    """节点类型"""
    SYNDROME = "syndrome"  # 证型
    SYMPTOM = "symptom"  # 症状
    HERB = "herb"  # 中药
    FORMULA = "formula"  # 方剂
    CONSTITUTION = "constitution"  # 体质
    ORGAN = "organ"  # 脏腑
    MERIDIAN = "meridian"  # 经络
    ACUPOINT = "acupoint"  # 穴位
    PATHOLOGY = "pathology"  # 病理因素
    TREATMENT = "treatment"  # 治疗方法
    DISEASE = "disease"  # 疾病

class RelationType(Enum):
    """关系类型"""
    TREATS = "treats"  # 治疗
    CAUSES = "causes"  # 导致
    CONTAINS = "contains"  # 包含
    BELONGS_TO = "belongs_to"  # 属于
    SIMILAR_TO = "similar_to"  # 相似
    OPPOSITE_TO = "opposite_to"  # 相反
    ENHANCES = "enhances"  # 增强
    INHIBITS = "inhibits"  # 抑制
    TRANSFORMS_TO = "transforms_to"  # 转化为
    LOCATED_IN = "located_in"  # 位于
    MANIFESTS_AS = "manifests_as"  # 表现为
    COMPATIBLE_WITH = "compatible_with"  # 配伍
    INCOMPATIBLE_WITH = "incompatible_with"  # 相反

@dataclass
class GraphNode:
    """图节点"""
    id: str
    type: NodeType
    name: str
    properties: Dict[str, Any]
    embedding: Optional[List[float]] = None
    aliases: List[str] = None
    description: str = ""

@dataclass
class GraphRelation:
    """图关系"""
    id: str
    source_id: str
    target_id: str
    type: RelationType
    properties: Dict[str, Any]
    weight: float = 1.0
    confidence: float = 1.0

@dataclass
class GraphQuery:
    """图查询"""
    node_types: List[NodeType] = None
    relation_types: List[RelationType] = None
    keywords: List[str] = None
    semantic_query: str = ""
    max_depth: int = 2
    max_results: int = 50

@dataclass
class GraphQueryResult:
    """图查询结果"""
    nodes: List[GraphNode]
    relations: List[GraphRelation]
    paths: List[List[str]]  # 路径（节点ID序列）
    subgraph: Dict[str, Any]  # 子图结构
    confidence: float
    reasoning: List[str]

class KnowledgeGraphIndexer:
    """知识图谱索引器"""
    
    def __init__(
        self,
        config: Dict[str, Any],
        embedding_service: EmbeddingService
    ):
        """
        初始化知识图谱索引器
        
        Args:
            config: 配置信息
            embedding_service: 嵌入服务
        """
        self.config = config
        self.embedding_service = embedding_service
        
        # 初始化图数据库
        self.graph = nx.MultiDiGraph()
        
        # 节点和关系存储
        self.nodes: Dict[str, GraphNode] = {}
        self.relations: Dict[str, GraphRelation] = {}
        
        # 索引
        self.node_type_index: Dict[NodeType, Set[str]] = {}
        self.name_index: Dict[str, str] = {}  # name -> node_id
        self.embedding_index: Dict[str, np.ndarray] = {}
        
        # 初始化索引
        self._initialize_indexes()
        
        # 加载预定义知识
        asyncio.create_task(self._load_predefined_knowledge())
    
    def _initialize_indexes(self) -> None:
        """初始化索引"""
        for node_type in NodeType:
            self.node_type_index[node_type] = set()
    
    async def _load_predefined_knowledge(self) -> None:
        """加载预定义的中医知识"""
        try:
            # 加载基础中医概念
            await self._load_basic_tcm_concepts()
            
            # 加载证型知识
            await self._load_syndrome_knowledge()
            
            # 加载中药知识
            await self._load_herb_knowledge()
            
            # 加载方剂知识
            await self._load_formula_knowledge()
            
            # 加载症状知识
            await self._load_symptom_knowledge()
            
            # 建立关系
            await self._build_relationships()
            
            logger.info(f"知识图谱加载完成，节点数: {len(self.nodes)}, 关系数: {len(self.relations)}")
            
        except Exception as e:
            logger.error(f"加载预定义知识失败: {str(e)}")
    
    async def _load_basic_tcm_concepts(self) -> None:
        """加载基础中医概念"""
        # 脏腑
        organs = [
            ("heart", "心", "主血脉，藏神"),
            ("liver", "肝", "主疏泄，藏血"),
            ("spleen", "脾", "主运化，统血"),
            ("lung", "肺", "主气，司呼吸"),
            ("kidney", "肾", "主水，藏精"),
            ("gallbladder", "胆", "主决断，贮胆汁"),
            ("stomach", "胃", "主受纳，腐熟水谷"),
            ("small_intestine", "小肠", "主分清浊"),
            ("large_intestine", "大肠", "主传导"),
            ("bladder", "膀胱", "主贮尿，司排泄"),
            ("triple_heater", "三焦", "主气化，通水道")
        ]
        
        for organ_id, name, description in organs:
            await self.add_node(
                node_id=organ_id,
                node_type=NodeType.ORGAN,
                name=name,
                properties={"description": description, "category": "脏腑"},
                description=description
            )
        
        # 病理因素
        pathological_factors = [
            ("qi_deficiency", "气虚", "元气不足，功能减退"),
            ("blood_deficiency", "血虚", "血液不足，濡养失职"),
            ("yin_deficiency", "阴虚", "阴液不足，虚热内生"),
            ("yang_deficiency", "阳虚", "阳气不足，温煦失职"),
            ("qi_stagnation", "气滞", "气机不畅，运行阻滞"),
            ("blood_stasis", "血瘀", "血行不畅，瘀血内停"),
            ("phlegm", "痰", "津液代谢失常，聚而成痰"),
            ("dampness", "湿", "水湿内停，运化失司"),
            ("heat", "热", "阳热偏盛，耗伤阴津"),
            ("cold", "寒", "阴寒偏盛，阳气受损")
        ]
        
        for factor_id, name, description in pathological_factors:
            await self.add_node(
                node_id=factor_id,
                node_type=NodeType.PATHOLOGY,
                name=name,
                properties={"description": description, "category": "病理因素"},
                description=description
            )
    
    async def _load_syndrome_knowledge(self) -> None:
        """加载证型知识"""
        syndromes = [
            ("spleen_qi_deficiency", "脾气虚", "脾气不足，运化失司", ["qi_deficiency"]),
            ("kidney_yin_deficiency", "肾阴虚", "肾阴不足，虚火内扰", ["yin_deficiency"]),
            ("kidney_yang_deficiency", "肾阳虚", "肾阳不足，温煦失职", ["yang_deficiency"]),
            ("liver_qi_stagnation", "肝气郁结", "肝失疏泄，气机郁滞", ["qi_stagnation"]),
            ("heart_blood_stasis", "心血瘀阻", "心脉瘀阻，血行不畅", ["blood_stasis"]),
            ("phlegm_dampness", "痰湿", "脾失健运，痰湿内生", ["phlegm", "dampness"]),
            ("damp_heat", "湿热", "湿热蕴结，清浊不分", ["dampness", "heat"])
        ]
        
        for syndrome_id, name, description, pathological_factors in syndromes:
            await self.add_node(
                node_id=syndrome_id,
                node_type=NodeType.SYNDROME,
                name=name,
                properties={
                    "description": description,
                    "pathological_factors": pathological_factors,
                    "category": "证型"
                },
                description=description
            )
            
            # 建立与病理因素的关系
            for factor in pathological_factors:
                await self.add_relation(
                    source_id=syndrome_id,
                    target_id=factor,
                    relation_type=RelationType.CONTAINS,
                    properties={"description": f"{name}包含{factor}病理因素"}
                )
    
    async def _load_herb_knowledge(self) -> None:
        """加载中药知识"""
        herbs = [
            ("ginseng", "人参", "大补元气，复脉固脱", ["qi_deficiency"], "甘、微苦，微温"),
            ("astragalus", "黄芪", "补气升阳，固表止汗", ["qi_deficiency"], "甘，微温"),
            ("angelica", "当归", "补血活血，调经止痛", ["blood_deficiency"], "甘、辛，温"),
            ("rehmannia", "熟地黄", "滋阴补血，益精填髓", ["yin_deficiency", "blood_deficiency"], "甘，微温"),
            ("cinnamon", "肉桂", "补火助阳，引火归源", ["yang_deficiency"], "辛、甘，大热"),
            ("bupleurum", "柴胡", "疏肝解郁，升阳举陷", ["qi_stagnation"], "苦、辛，微寒"),
            ("safflower", "红花", "活血通经，散瘀止痛", ["blood_stasis"], "辛，温"),
            ("pinellia", "半夏", "燥湿化痰，降逆止呕", ["phlegm"], "辛，温"),
            ("poria", "茯苓", "利水渗湿，健脾宁心", ["dampness"], "甘、淡，平"),
            ("coptis", "黄连", "清热燥湿，泻火解毒", ["heat"], "苦，寒")
        ]
        
        for herb_id, name, functions, indications, properties in herbs:
            await self.add_node(
                node_id=herb_id,
                node_type=NodeType.HERB,
                name=name,
                properties={
                    "functions": functions,
                    "indications": indications,
                    "properties": properties,
                    "category": "中药"
                },
                description=functions
            )
            
            # 建立与病理因素的治疗关系
            for indication in indications:
                await self.add_relation(
                    source_id=herb_id,
                    target_id=indication,
                    relation_type=RelationType.TREATS,
                    properties={"description": f"{name}治疗{indication}"}
                )
    
    async def _load_formula_knowledge(self) -> None:
        """加载方剂知识"""
        formulas = [
            ("sijunzi_decoction", "四君子汤", "益气健脾", 
             ["ginseng", "atractylodes", "poria", "licorice"], ["spleen_qi_deficiency"]),
            ("liuwei_dihuang_pill", "六味地黄丸", "滋阴补肾",
             ["rehmannia", "cornus", "dioscorea", "alisma", "poria", "moutan"], ["kidney_yin_deficiency"]),
            ("xiaoyao_powder", "逍遥散", "疏肝健脾",
             ["bupleurum", "angelica", "atractylodes", "poria", "licorice", "mint"], ["liver_qi_stagnation"])
        ]
        
        for formula_id, name, functions, composition, indications in formulas:
            await self.add_node(
                node_id=formula_id,
                node_type=NodeType.FORMULA,
                name=name,
                properties={
                    "functions": functions,
                    "composition": composition,
                    "indications": indications,
                    "category": "方剂"
                },
                description=functions
            )
            
            # 建立与组成药物的关系
            for herb in composition:
                if herb in self.name_index:
                    herb_id = self.name_index[herb]
                    await self.add_relation(
                        source_id=formula_id,
                        target_id=herb_id,
                        relation_type=RelationType.CONTAINS,
                        properties={"description": f"{name}包含{herb}"}
                    )
            
            # 建立与适应证的关系
            for indication in indications:
                await self.add_relation(
                    source_id=formula_id,
                    target_id=indication,
                    relation_type=RelationType.TREATS,
                    properties={"description": f"{name}治疗{indication}"}
                )
    
    async def _load_symptom_knowledge(self) -> None:
        """加载症状知识"""
        symptoms = [
            ("fatigue", "乏力", "精神疲倦，体力不支", ["qi_deficiency"]),
            ("dizziness", "眩晕", "头晕目眩，视物旋转", ["yin_deficiency", "phlegm"]),
            ("insomnia", "失眠", "不易入睡，睡眠不深", ["yin_deficiency", "qi_stagnation"]),
            ("palpitation", "心悸", "心跳加快，心慌不安", ["qi_deficiency", "blood_deficiency"]),
            ("chest_tightness", "胸闷", "胸部闷胀，呼吸不畅", ["qi_stagnation", "phlegm"]),
            ("abdominal_pain", "腹痛", "腹部疼痛，程度不一", ["qi_stagnation", "cold"]),
            ("constipation", "便秘", "大便干燥，排便困难", ["yin_deficiency", "qi_stagnation"]),
            ("diarrhea", "腹泻", "大便稀溏，次数增多", ["yang_deficiency", "dampness"]),
            ("night_sweats", "盗汗", "睡中汗出，醒后汗止", ["yin_deficiency"]),
            ("cold_limbs", "四肢厥冷", "手足冰冷，畏寒怕冷", ["yang_deficiency"])
        ]
        
        for symptom_id, name, description, related_pathologies in symptoms:
            await self.add_node(
                node_id=symptom_id,
                node_type=NodeType.SYMPTOM,
                name=name,
                properties={
                    "description": description,
                    "related_pathologies": related_pathologies,
                    "category": "症状"
                },
                description=description
            )
            
            # 建立与病理因素的关系
            for pathology in related_pathologies:
                await self.add_relation(
                    source_id=pathology,
                    target_id=symptom_id,
                    relation_type=RelationType.MANIFESTS_AS,
                    properties={"description": f"{pathology}表现为{name}"}
                )
    
    async def _build_relationships(self) -> None:
        """建立复杂关系"""
        # 脏腑与病理因素的关系
        organ_pathology_relations = [
            ("spleen", "qi_deficiency", "脾主运化，脾虚则气虚"),
            ("kidney", "yin_deficiency", "肾藏精，肾虚则阴虚"),
            ("kidney", "yang_deficiency", "肾为阳气之根，肾虚则阳虚"),
            ("liver", "qi_stagnation", "肝主疏泄，肝郁则气滞"),
            ("heart", "blood_stasis", "心主血脉，心病则血瘀")
        ]
        
        for organ, pathology, description in organ_pathology_relations:
            await self.add_relation(
                source_id=organ,
                target_id=pathology,
                relation_type=RelationType.CAUSES,
                properties={"description": description}
            )
        
        # 病理因素之间的转化关系
        pathology_transformations = [
            ("qi_deficiency", "blood_deficiency", "气虚日久，血亦虚"),
            ("qi_stagnation", "blood_stasis", "气滞日久，血必瘀"),
            ("yang_deficiency", "qi_deficiency", "阳虚则气虚"),
            ("yin_deficiency", "heat", "阴虚则生内热"),
            ("dampness", "phlegm", "湿聚成痰")
        ]
        
        for source, target, description in pathology_transformations:
            await self.add_relation(
                source_id=source,
                target_id=target,
                relation_type=RelationType.TRANSFORMS_TO,
                properties={"description": description}
            )
    
    async def add_node(
        self,
        node_id: str,
        node_type: NodeType,
        name: str,
        properties: Dict[str, Any],
        description: str = "",
        aliases: List[str] = None
    ) -> None:
        """
        添加节点
        
        Args:
            node_id: 节点ID
            node_type: 节点类型
            name: 节点名称
            properties: 节点属性
            description: 节点描述
            aliases: 别名列表
        """
        # 生成嵌入向量
        text_for_embedding = f"{name} {description}"
        embedding = await self.embedding_service.embed_text(text_for_embedding)
        
        # 创建节点
        node = GraphNode(
            id=node_id,
            type=node_type,
            name=name,
            properties=properties,
            embedding=embedding,
            aliases=aliases or [],
            description=description
        )
        
        # 存储节点
        self.nodes[node_id] = node
        self.graph.add_node(node_id, **asdict(node))
        
        # 更新索引
        self.node_type_index[node_type].add(node_id)
        self.name_index[name] = node_id
        
        if aliases:
            for alias in aliases:
                self.name_index[alias] = node_id
        
        if embedding:
            self.embedding_index[node_id] = np.array(embedding)
        
        logger.debug(f"添加节点: {name} ({node_type.value})")
    
    async def add_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
        properties: Dict[str, Any] = None,
        weight: float = 1.0,
        confidence: float = 1.0
    ) -> None:
        """
        添加关系
        
        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            relation_type: 关系类型
            properties: 关系属性
            weight: 关系权重
            confidence: 置信度
        """
        if source_id not in self.nodes or target_id not in self.nodes:
            logger.warning(f"关系的节点不存在: {source_id} -> {target_id}")
            return
        
        relation_id = f"{source_id}_{relation_type.value}_{target_id}"
        
        relation = GraphRelation(
            id=relation_id,
            source_id=source_id,
            target_id=target_id,
            type=relation_type,
            properties=properties or {},
            weight=weight,
            confidence=confidence
        )
        
        # 存储关系
        self.relations[relation_id] = relation
        self.graph.add_edge(
            source_id, target_id,
            key=relation_type.value,
            **asdict(relation)
        )
        
        logger.debug(f"添加关系: {source_id} -{relation_type.value}-> {target_id}")
    
    async def query_graph(self, query: GraphQuery) -> GraphQueryResult:
        """
        查询知识图谱
        
        Args:
            query: 图查询
            
        Returns:
            查询结果
        """
        logger.info(f"执行图查询: {query}")
        
        try:
            # 初始化结果
            result_nodes = []
            result_relations = []
            paths = []
            reasoning = []
            
            # 1. 基于节点类型过滤
            candidate_nodes = set()
            if query.node_types:
                for node_type in query.node_types:
                    candidate_nodes.update(self.node_type_index.get(node_type, set()))
                reasoning.append(f"基于节点类型过滤，候选节点: {len(candidate_nodes)}")
            else:
                candidate_nodes = set(self.nodes.keys())
            
            # 2. 基于关键词过滤
            if query.keywords:
                keyword_matched = set()
                for node_id in candidate_nodes:
                    node = self.nodes[node_id]
                    node_text = f"{node.name} {node.description} {' '.join(node.aliases)}"
                    
                    if any(keyword in node_text for keyword in query.keywords):
                        keyword_matched.add(node_id)
                
                candidate_nodes = candidate_nodes.intersection(keyword_matched)
                reasoning.append(f"基于关键词过滤，匹配节点: {len(candidate_nodes)}")
            
            # 3. 基于语义相似度过滤
            if query.semantic_query:
                semantic_matched = await self._semantic_search(
                    query.semantic_query, candidate_nodes, top_k=query.max_results
                )
                candidate_nodes = set(semantic_matched)
                reasoning.append(f"基于语义相似度过滤，匹配节点: {len(candidate_nodes)}")
            
            # 4. 扩展相关节点
            expanded_nodes = set(candidate_nodes)
            for node_id in list(candidate_nodes)[:10]:  # 限制扩展的起始节点数量
                neighbors = await self._get_neighbors(
                    node_id, query.max_depth, query.relation_types
                )
                expanded_nodes.update(neighbors)
            
            reasoning.append(f"扩展相关节点，总节点数: {len(expanded_nodes)}")
            
            # 5. 构建结果
            for node_id in list(expanded_nodes)[:query.max_results]:
                if node_id in self.nodes:
                    result_nodes.append(self.nodes[node_id])
            
            # 6. 获取节点间的关系
            for relation in self.relations.values():
                if (relation.source_id in expanded_nodes and 
                    relation.target_id in expanded_nodes):
                    if not query.relation_types or relation.type in query.relation_types:
                        result_relations.append(relation)
            
            # 7. 查找路径
            if len(candidate_nodes) >= 2:
                paths = await self._find_paths(
                    list(candidate_nodes)[:5], query.max_depth
                )
            
            # 8. 构建子图
            subgraph = await self._build_subgraph(expanded_nodes)
            
            # 9. 计算置信度
            confidence = len(result_nodes) / max(query.max_results, 1)
            
            return GraphQueryResult(
                nodes=result_nodes,
                relations=result_relations,
                paths=paths,
                subgraph=subgraph,
                confidence=confidence,
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"图查询失败: {str(e)}")
            raise
    
    async def _semantic_search(
        self,
        query_text: str,
        candidate_nodes: Set[str],
        top_k: int = 50
    ) -> List[str]:
        """语义搜索"""
        if not candidate_nodes:
            return []
        
        # 生成查询嵌入
        query_embedding = await self.embedding_service.embed_text(query_text)
        query_vector = np.array(query_embedding)
        
        # 计算相似度
        similarities = []
        for node_id in candidate_nodes:
            if node_id in self.embedding_index:
                node_vector = self.embedding_index[node_id]
                similarity = np.dot(query_vector, node_vector) / (
                    np.linalg.norm(query_vector) * np.linalg.norm(node_vector)
                )
                similarities.append((node_id, similarity))
        
        # 排序并返回top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [node_id for node_id, _ in similarities[:top_k]]
    
    async def _get_neighbors(
        self,
        node_id: str,
        max_depth: int,
        relation_types: Optional[List[RelationType]] = None
    ) -> Set[str]:
        """获取邻居节点"""
        neighbors = set()
        visited = set()
        queue = [(node_id, 0)]
        
        while queue:
            current_id, depth = queue.pop(0)
            
            if current_id in visited or depth >= max_depth:
                continue
            
            visited.add(current_id)
            neighbors.add(current_id)
            
            # 获取直接邻居
            if current_id in self.graph:
                for neighbor_id in self.graph.neighbors(current_id):
                    if neighbor_id not in visited:
                        # 检查关系类型
                        edge_data = self.graph.get_edge_data(current_id, neighbor_id)
                        if edge_data:
                            for key, data in edge_data.items():
                                if not relation_types or RelationType(key) in relation_types:
                                    queue.append((neighbor_id, depth + 1))
                                    break
                
                # 获取反向邻居
                for predecessor_id in self.graph.predecessors(current_id):
                    if predecessor_id not in visited:
                        edge_data = self.graph.get_edge_data(predecessor_id, current_id)
                        if edge_data:
                            for key, data in edge_data.items():
                                if not relation_types or RelationType(key) in relation_types:
                                    queue.append((predecessor_id, depth + 1))
                                    break
        
        return neighbors
    
    async def _find_paths(
        self,
        start_nodes: List[str],
        max_depth: int
    ) -> List[List[str]]:
        """查找节点间的路径"""
        paths = []
        
        for i, start_node in enumerate(start_nodes):
            for end_node in start_nodes[i+1:]:
                try:
                    # 使用NetworkX查找最短路径
                    if nx.has_path(self.graph, start_node, end_node):
                        path = nx.shortest_path(self.graph, start_node, end_node)
                        if len(path) <= max_depth + 1:
                            paths.append(path)
                except nx.NetworkXNoPath:
                    continue
        
        return paths[:10]  # 限制路径数量
    
    async def _build_subgraph(self, node_ids: Set[str]) -> Dict[str, Any]:
        """构建子图"""
        subgraph_nodes = []
        subgraph_edges = []
        
        # 添加节点
        for node_id in node_ids:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                subgraph_nodes.append({
                    "id": node.id,
                    "type": node.type.value,
                    "name": node.name,
                    "properties": node.properties
                })
        
        # 添加边
        for relation in self.relations.values():
            if (relation.source_id in node_ids and 
                relation.target_id in node_ids):
                subgraph_edges.append({
                    "source": relation.source_id,
                    "target": relation.target_id,
                    "type": relation.type.value,
                    "weight": relation.weight,
                    "properties": relation.properties
                })
        
        return {
            "nodes": subgraph_nodes,
            "edges": subgraph_edges,
            "node_count": len(subgraph_nodes),
            "edge_count": len(subgraph_edges)
        }
    
    async def get_node_by_name(self, name: str) -> Optional[GraphNode]:
        """根据名称获取节点"""
        node_id = self.name_index.get(name)
        if node_id:
            return self.nodes.get(node_id)
        return None
    
    async def get_related_nodes(
        self,
        node_id: str,
        relation_type: RelationType,
        direction: str = "out"  # "out", "in", "both"
    ) -> List[GraphNode]:
        """获取相关节点"""
        related_nodes = []
        
        if node_id not in self.graph:
            return related_nodes
        
        if direction in ["out", "both"]:
            # 出边
            for target_id in self.graph.neighbors(node_id):
                edge_data = self.graph.get_edge_data(node_id, target_id)
                if edge_data and relation_type.value in edge_data:
                    if target_id in self.nodes:
                        related_nodes.append(self.nodes[target_id])
        
        if direction in ["in", "both"]:
            # 入边
            for source_id in self.graph.predecessors(node_id):
                edge_data = self.graph.get_edge_data(source_id, node_id)
                if edge_data and relation_type.value in edge_data:
                    if source_id in self.nodes:
                        related_nodes.append(self.nodes[source_id])
        
        return related_nodes
    
    async def recommend_related_knowledge(
        self,
        query_text: str,
        node_types: List[NodeType] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """推荐相关知识"""
        # 构建查询
        graph_query = GraphQuery(
            node_types=node_types,
            semantic_query=query_text,
            max_depth=2,
            max_results=max_results
        )
        
        # 执行查询
        result = await self.query_graph(graph_query)
        
        # 格式化推荐结果
        recommendations = []
        for node in result.nodes:
            recommendation = {
                "id": node.id,
                "type": node.type.value,
                "name": node.name,
                "description": node.description,
                "properties": node.properties,
                "relevance_score": 0.8  # 简化的相关性评分
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    async def get_graph_statistics(self) -> Dict[str, Any]:
        """获取图统计信息"""
        stats = {
            "total_nodes": len(self.nodes),
            "total_relations": len(self.relations),
            "node_types": {},
            "relation_types": {},
            "graph_density": 0.0,
            "average_degree": 0.0
        }
        
        # 节点类型统计
        for node_type, node_ids in self.node_type_index.items():
            stats["node_types"][node_type.value] = len(node_ids)
        
        # 关系类型统计
        for relation in self.relations.values():
            relation_type = relation.type.value
            stats["relation_types"][relation_type] = stats["relation_types"].get(relation_type, 0) + 1
        
        # 图密度和平均度
        if len(self.nodes) > 1:
            stats["graph_density"] = nx.density(self.graph)
            total_degree = sum(dict(self.graph.degree()).values())
            stats["average_degree"] = total_degree / len(self.nodes)
        
        return stats
    
    async def export_graph(self, format: str = "json") -> Dict[str, Any]:
        """导出图数据"""
        if format == "json":
            return {
                "nodes": [asdict(node) for node in self.nodes.values()],
                "relations": [asdict(relation) for relation in self.relations.values()],
                "metadata": await self.get_graph_statistics()
            }
        else:
            raise ValueError(f"不支持的导出格式: {format}")
    
    async def import_graph(self, graph_data: Dict[str, Any]) -> None:
        """导入图数据"""
        try:
            # 导入节点
            for node_data in graph_data.get("nodes", []):
                node = GraphNode(**node_data)
                self.nodes[node.id] = node
                self.graph.add_node(node.id, **asdict(node))
                
                # 更新索引
                self.node_type_index[node.type].add(node.id)
                self.name_index[node.name] = node.id
                
                if node.aliases:
                    for alias in node.aliases:
                        self.name_index[alias] = node.id
                
                if node.embedding:
                    self.embedding_index[node.id] = np.array(node.embedding)
            
            # 导入关系
            for relation_data in graph_data.get("relations", []):
                relation = GraphRelation(**relation_data)
                self.relations[relation.id] = relation
                self.graph.add_edge(
                    relation.source_id, relation.target_id,
                    key=relation.type.value,
                    **asdict(relation)
                )
            
            logger.info(f"成功导入图数据，节点: {len(self.nodes)}, 关系: {len(self.relations)}")
            
        except Exception as e:
            logger.error(f"导入图数据失败: {str(e)}")
            raise 