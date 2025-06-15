"""知识库服务模块

提供中医知识库管理、检索和向量化功能。
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from xiaoke_service.core.config import settings
from xiaoke_service.core.logging import get_ai_logger
from xiaoke_service.core.exceptions import KnowledgeBaseError
from dataclasses import dataclass
import hashlib
import re

logger = get_ai_logger(__name__)


@dataclass
class KnowledgeItem:
    """知识条目数据类"""
    id: str
    title: str
    content: str
    category: str
    tags: List[str]
    relevance_score: float
    metadata: Dict[str, Any]
    created_at: float
    updated_at: float


@dataclass
class SearchResult:
    """搜索结果数据类"""
    items: List[KnowledgeItem]
    total_count: int
    search_time: float
    query: str
    suggestions: List[str]


class KnowledgeService:
    """知识库服务类
    
    管理中医知识库，提供知识检索、分类管理和向量化功能。
    支持全文搜索、语义搜索和模糊匹配。
    """

    def __init__(self):
        """初始化知识库服务"""
        self.knowledge_base: Dict[str, KnowledgeItem] = {}
        self.categories: Dict[str, Dict[str, Any]] = {}
        self.search_index: Dict[str, List[str]] = {}  # 简单的倒排索引
        self._initialized = False
        
        # 初始化默认分类
        self._init_default_categories()
        
        # 初始化模拟知识库
        self._init_mock_knowledge()

    async def initialize(self) -> None:
        """初始化知识库服务"""
        try:
            # 这里可以初始化向量数据库、加载知识库等
            await self._load_knowledge_base()
            await self._build_search_index()
            
            self._initialized = True
            logger.info("知识库服务初始化成功", 
                       knowledge_count=len(self.knowledge_base),
                       categories_count=len(self.categories))
            
        except Exception as e:
            logger.error("知识库服务初始化失败", error=str(e))
            raise KnowledgeBaseError(f"知识库服务初始化失败: {e}") from e

    def _init_default_categories(self) -> None:
        """初始化默认分类"""
        self.categories = {
            "tcm_theory": {
                "name": "中医理论",
                "description": "中医基础理论知识",
                "count": 0,
                "tags": ["阴阳", "五行", "气血", "脏腑"]
            },
            "herbs": {
                "name": "中药材",
                "description": "中药材的性味归经和功效",
                "count": 0,
                "tags": ["性味", "归经", "功效", "用法"]
            },
            "acupuncture": {
                "name": "针灸",
                "description": "针灸穴位和手法",
                "count": 0,
                "tags": ["穴位", "经络", "手法", "适应症"]
            },
            "diet_therapy": {
                "name": "食疗",
                "description": "中医食疗和药膳同源",
                "count": 0,
                "tags": ["食物性味", "食疗方", "药膳", "养生"]
            },
            "constitution": {
                "name": "体质辨识",
                "description": "中医体质分类和调理",
                "count": 0,
                "tags": ["体质类型", "辨识方法", "调理方案", "养生指导"]
            },
            "syndrome": {
                "name": "辨证论治",
                "description": "中医辨证论治方法",
                "count": 0,
                "tags": ["证型", "病因", "病机", "治法"]
            }
        }

    def _init_mock_knowledge(self) -> None:
        """初始化模拟知识库数据"""
        mock_knowledge = [
            {
                "title": "气血两虚证",
                "content": "气血两虚证是指气虚和血虚同时存在的证候。主要表现为神疲乏力、气短懒言、面色苍白或萎黄、心悸失眠、头晕眼花等。治法宜气血双补，常用八珍汤、十全大补汤等方剂。",
                "category": "syndrome",
                "tags": ["气虚", "血虚", "辨证", "治法"]
            },
            {
                "title": "人参",
                "content": "人参，性平，味甘、微苦，归脾、肺、心、肾经。功效：大补元气，复脉固脱，补脾益肺，生津养血，安神益智。主治大病久病、元气欲脱、脾肺气虚等。",
                "category": "herbs",
                "tags": ["补气", "元气", "脾肺", "安神"]
            },
            {
                "title": "百会穴",
                "content": "百会穴位于头顶部，当前发际正中直上7寸，或头顶正中线与两耳尖连线的交点处。功效：安神定志，升阳举陷，益气固脱。主治头痛、眩病、失眠、健忘等。",
                "category": "acupuncture",
                "tags": ["头顶部", "安神", "升阳", "头痛"]
            },
            {
                "title": "山药粥",
                "content": "山药粥由山药、米饭等材料制成。山药性平，味甘，归脾、肺、肾经，有补脾养胃、生津益肺、补肾涩精的功效。适合脾胃虚弱、食少体倦、泄泻便溏等情况。",
                "category": "diet_therapy",
                "tags": ["山药", "补脾", "养胃", "食疗"]
            },
            {
                "title": "气虚质",
                "content": "气虚质是指元气不足，以疲乏、气短、自汗等气虚表现为主要特征的体质状态。常见表现：平素语音低弱，气短懒言，容易疲乏，精神不振，易出汗，动则加重。调养方法：补气养气，平素可服用人参、黄芝等。",
                "category": "constitution",
                "tags": ["气虚", "体质", "疲乏", "调养"]
            },
            {
                "title": "阴阳学说",
                "content": "阴阳学说是中医理论的核心，认为世界上一切事物都存在着阴阳两个方面。阴阳既是对立的，又是统一的，在对立中达到统一，在统一中存在着对立。在人体，阴阳的相对平衡，是维持正常生理功能的基础。",
                "category": "tcm_theory",
                "tags": ["阴阳", "对立统一", "平衡", "理论"]
            }
        ]
        
        for i, item_data in enumerate(mock_knowledge):
            item_id = f"kb_{i+1:03d}"
            item = KnowledgeItem(
                id=item_id,
                title=item_data["title"],
                content=item_data["content"],
                category=item_data["category"],
                tags=item_data["tags"],
                relevance_score=1.0,
                metadata={
                    "source": "mock_data",
                    "verified": True,
                    "difficulty": "basic"
                },
                created_at=time.time(),
                updated_at=time.time()
            )
            self.knowledge_base[item_id] = item
            
            # 更新分类计数
            if item.category in self.categories:
                self.categories[item.category]["count"] += 1

    async def _load_knowledge_base(self) -> None:
        """加载知识库（从数据库或文件）"""
        # 这里可以实现从 MongoDB 或其他数据源加载知识
        # 目前使用模拟数据
        await asyncio.sleep(0.1)  # 模拟加载时间
        logger.info("知识库加载完成", count=len(self.knowledge_base))

    async def _build_search_index(self) -> None:
        """构建搜索索引"""
        self.search_index.clear()
        
        for item_id, item in self.knowledge_base.items():
            # 分词并建立索引
            words = self._tokenize(item.title + " " + item.content + " " + " ".join(item.tags))
            
            for word in words:
                if word not in self.search_index:
                    self.search_index[word] = []
                if item_id not in self.search_index[word]:
                    self.search_index[word].append(item_id)
        
        logger.info("搜索索引构建完成", index_size=len(self.search_index))

    def _tokenize(self, text: str) -> List[str]:
        """简单分词（可以集成 jieba 等工具）"""
        # 移除标点符号并转为小写
        text = re.sub(r'[^\w\s一-鿿]', ' ', text)
        # 按空格和单个字符分割
        words = []
        for word in text.split():
            if len(word) > 1:
                words.append(word)
            # 中文单字也加入索引
            for char in word:
                if '\u4e00' <= char <= '\u9fff':
                    words.append(char)
        return [w for w in words if len(w.strip()) > 0]

    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        include_metadata: bool = False
    ) -> SearchResult:
        """搜索知识库
        
        Args:
            query: 搜索查询
            category: 分类过滤
            limit: 结果数量限制
            offset: 结果偏移
            include_metadata: 是否包含元数据
            
        Returns:
            SearchResult: 搜索结果
        """
        start_time = time.time()
        
        try:
            # 分词
            query_words = self._tokenize(query)
            
            # 获取候选文档
            candidate_ids = set()
            for word in query_words:
                if word in self.search_index:
                    candidate_ids.update(self.search_index[word])
            
            # 计算相关性并排序
            scored_items = []
            for item_id in candidate_ids:
                if item_id in self.knowledge_base:
                    item = self.knowledge_base[item_id]
                    
                    # 分类过滤
                    if category and item.category != category:
                        continue
                    
                    # 计算相关性分数
                    score = self._calculate_relevance_score(query, query_words, item)
                    scored_items.append((score, item))
            
            # 按分数排序
            scored_items.sort(key=lambda x: x[0], reverse=True)
            
            # 分页
            total_count = len(scored_items)
            paged_items = scored_items[offset:offset + limit]
            
            # 构建结果
            result_items = []
            for score, item in paged_items:
                # 更新相关性分数
                item.relevance_score = score
                
                # 如果不包含元数据，则清空
                if not include_metadata:
                    item.metadata = {}
                
                result_items.append(item)
            
            # 生成搜索建议
            suggestions = self._generate_search_suggestions(query, query_words)
            
            search_time = time.time() - start_time
            
            # 记录搜索日志
            logger.log_knowledge_query(
                query=query,
                results_count=len(result_items),
                duration=search_time
            )
            
            return SearchResult(
                items=result_items,
                total_count=total_count,
                search_time=search_time,
                query=query,
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error("知识库搜索失败", error=str(e), query=query)
            raise KnowledgeBaseError(f"知识库搜索失败: {e}") from e

    def _calculate_relevance_score(self, query: str, query_words: List[str], item: KnowledgeItem) -> float:
        """计算相关性分数"""
        score = 0.0
        
        # 标题匹配（权重更高）
        title_words = self._tokenize(item.title)
        for word in query_words:
            if word in title_words:
                score += 2.0
            elif word in item.title:
                score += 1.5
        
        # 内容匹配
        content_words = self._tokenize(item.content)
        for word in query_words:
            if word in content_words:
                score += 1.0
            elif word in item.content:
                score += 0.5
        
        # 标签匹配
        for word in query_words:
            if word in item.tags:
                score += 1.5
        
        # 完全匹配加分
        if query in item.title:
            score += 3.0
        elif query in item.content:
            score += 2.0
        
        # 按文档长度正规化
        doc_length = len(item.title) + len(item.content)
        if doc_length > 0:
            score = score / (1 + doc_length / 1000)
        
        return score

    def _generate_search_suggestions(self, query: str, query_words: List[str]) -> List[str]:
        """生成搜索建议"""
        suggestions = []
        
        # 基于分类的建议
        for category_id, category_info in self.categories.items():
            if category_info["count"] > 0:
                suggestions.append(f"搜索{category_info['name']}相关内容")
        
        # 基于热门标签的建议
        popular_tags = ["气血", "阴阳", "脾胃", "辨证", "养生"]
        for tag in popular_tags:
            if tag not in query:
                suggestions.append(f"了解{tag}相关知识")
        
        return suggestions[:3]  # 返回前3个建议

    async def get_item(self, item_id: str) -> Optional[KnowledgeItem]:
        """获取知识条目
        
        Args:
            item_id: 条目 ID
            
        Returns:
            KnowledgeItem: 知识条目，不存在返回 None
        """
        return self.knowledge_base.get(item_id)

    async def get_categories(self) -> Dict[str, Dict[str, Any]]:
        """获取所有分类
        
        Returns:
            Dict: 分类信息
        """
        return self.categories.copy()

    async def add_item(
        self,
        title: str,
        content: str,
        category: str,
        tags: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """添加知识条目
        
        Args:
            title: 标题
            content: 内容
            category: 分类
            tags: 标签
            metadata: 元数据
            
        Returns:
            str: 新添加条目的 ID
        """
        # 生成 ID
        item_id = hashlib.md5(f"{title}_{content}_{time.time()}".encode()).hexdigest()[:12]
        
        # 创建条目
        item = KnowledgeItem(
            id=item_id,
            title=title,
            content=content,
            category=category,
            tags=tags,
            relevance_score=1.0,
            metadata=metadata or {},
            created_at=time.time(),
            updated_at=time.time()
        )
        
        # 添加到知识库
        self.knowledge_base[item_id] = item
        
        # 更新分类计数
        if category in self.categories:
            self.categories[category]["count"] += 1
        
        # 更新搜索索引
        await self._update_search_index(item_id, item)
        
        logger.info("添加知识条目", item_id=item_id, title=title, category=category)
        
        return item_id

    async def _update_search_index(self, item_id: str, item: KnowledgeItem) -> None:
        """更新搜索索引"""
        words = self._tokenize(item.title + " " + item.content + " " + " ".join(item.tags))
        
        for word in words:
            if word not in self.search_index:
                self.search_index[word] = []
            if item_id not in self.search_index[word]:
                self.search_index[word].append(item_id)

    async def get_statistics(self) -> Dict[str, Any]:
        """获取知识库统计信息
        
        Returns:
            Dict: 统计信息
        """
        return {
            "total_items": len(self.knowledge_base),
            "total_categories": len(self.categories),
            "index_size": len(self.search_index),
            "categories": {
                cat_id: {
                    "name": cat_info["name"],
                    "count": cat_info["count"]
                }
                for cat_id, cat_info in self.categories.items()
            },
            "last_updated": max(
                (item.updated_at for item in self.knowledge_base.values()),
                default=time.time()
            )
        }

    async def close(self) -> None:
        """关闭知识库服务"""
        # 清理资源
        self.knowledge_base.clear()
        self.search_index.clear()
        
        logger.info("知识库服务已关闭")