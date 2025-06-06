"""
document_manager - 索克生活项目模块
"""

                from sqlalchemy import update
            from bs4 import BeautifulSoup
            from sqlalchemy import delete
            from sqlalchemy import select
            from sqlalchemy import select, and_, or_
            from sqlalchemy import select, func
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy import Column, String, DateTime, Integer, Text, Float, Boolean, JSON
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Dict, List, Any, Optional, Tuple, Set, Union, BinaryIO
import aiofiles
import asyncio
import docx
import fitz  # PyMuPDF
import hashlib
import jieba
import json
import uuid

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文档管理器 - 高级文档索引、分类、版本控制和元数据管理系统
"""


Base = declarative_base()

class DocumentType(Enum):
    """文档类型"""
    TEXT = "text"                    # 纯文本
    PDF = "pdf"                      # PDF文档
    WORD = "word"                    # Word文档
    EXCEL = "excel"                  # Excel表格
    IMAGE = "image"                  # 图片
    AUDIO = "audio"                  # 音频
    VIDEO = "video"                  # 视频
    HTML = "html"                    # HTML网页
    MARKDOWN = "markdown"            # Markdown文档
    JSON = "json"                    # JSON数据
    XML = "xml"                      # XML文档
    CSV = "csv"                      # CSV文件
    MEDICAL_RECORD = "medical_record" # 病历
    TCM_PRESCRIPTION = "tcm_prescription" # 中医处方
    RESEARCH_PAPER = "research_paper"     # 研究论文

class DocumentStatus(Enum):
    """文档状态"""
    PENDING = "pending"              # 待处理
    PROCESSING = "processing"        # 处理中
    INDEXED = "indexed"              # 已索引
    FAILED = "failed"               # 处理失败
    ARCHIVED = "archived"           # 已归档
    DELETED = "deleted"             # 已删除

class DocumentCategory(Enum):
    """文档分类"""
    GENERAL_HEALTH = "general_health"           # 一般健康
    TCM_THEORY = "tcm_theory"                   # 中医理论
    SYMPTOM_ANALYSIS = "symptom_analysis"       # 症状分析
    TREATMENT_PLAN = "treatment_plan"           # 治疗方案
    PREVENTION = "prevention"                   # 预防保健
    LIFESTYLE = "lifestyle"                     # 生活方式
    NUTRITION = "nutrition"                     # 营养学
    EXERCISE = "exercise"                       # 运动健身
    MENTAL_HEALTH = "mental_health"             # 心理健康
    EMERGENCY = "emergency"                     # 急救医学
    RESEARCH = "research"                       # 研究文献
    CASE_STUDY = "case_study"                   # 病例研究
    DRUG_INFO = "drug_info"                     # 药物信息
    MEDICAL_DEVICE = "medical_device"           # 医疗器械
    REGULATION = "regulation"                   # 法规政策

class ProcessingPriority(Enum):
    """处理优先级"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

@dataclass
class DocumentMetadata:
    """文档元数据"""
    title: str
    author: Optional[str] = None
    source: Optional[str] = None
    language: str = "zh"
    keywords: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    file_size: Optional[int] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    quality_score: float = 0.0
    confidence_score: float = 0.0
    custom_fields: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DocumentVersion:
    """文档版本"""
    version_id: str
    version_number: str
    created_at: datetime
    created_by: str
    changes: List[str]
    file_hash: str
    file_path: str
    metadata: DocumentMetadata

@dataclass
class DocumentChunk:
    """文档块"""
    chunk_id: str
    document_id: str
    content: str
    chunk_index: int
    start_position: int
    end_position: int
    chunk_type: str  # paragraph, section, table, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)

class DocumentModel(Base):
    """文档数据模型"""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)
    category = Column(String, nullable=False)
    status = Column(String, nullable=False)
    priority = Column(Integer, default=2)
    file_path = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)
    file_size = Column(Integer)
    content_hash = Column(String)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    indexed_at = Column(DateTime)
    version_count = Column(Integer, default=1)
    current_version = Column(String)
    is_active = Column(Boolean, default=True)

class DocumentVersionModel(Base):
    """文档版本数据模型"""
    __tablename__ = "document_versions"
    
    id = Column(String, primary_key=True)
    document_id = Column(String, nullable=False)
    version_number = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)
    changes = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    metadata = Column(JSON)
    is_current = Column(Boolean, default=False)

class DocumentChunkModel(Base):
    """文档块数据模型"""
    __tablename__ = "document_chunks"
    
    id = Column(String, primary_key=True)
    document_id = Column(String, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String, nullable=False)
    start_position = Column(Integer)
    end_position = Column(Integer)
    chunk_type = Column(String)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    vector_id = Column(String)  # 向量数据库中的ID

class DocumentManager:
    """文档管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化文档管理器
        
        Args:
            config: 配置信息
        """
        self.config = config
        
        # 数据库连接
        self.engine = None
        self.async_session = None
        
        # Redis连接
        self.redis_client = None
        
        # 文档存储路径
        self.storage_path = Path(config.get('storage_path', './documents'))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 支持的文件类型
        self.supported_types = {
            '.txt': DocumentType.TEXT,
            '.pdf': DocumentType.PDF,
            '.doc': DocumentType.WORD,
            '.docx': DocumentType.WORD,
            '.xls': DocumentType.EXCEL,
            '.xlsx': DocumentType.EXCEL,
            '.jpg': DocumentType.IMAGE,
            '.jpeg': DocumentType.IMAGE,
            '.png': DocumentType.IMAGE,
            '.gif': DocumentType.IMAGE,
            '.mp3': DocumentType.AUDIO,
            '.wav': DocumentType.AUDIO,
            '.mp4': DocumentType.VIDEO,
            '.avi': DocumentType.VIDEO,
            '.html': DocumentType.HTML,
            '.htm': DocumentType.HTML,
            '.md': DocumentType.MARKDOWN,
            '.json': DocumentType.JSON,
            '.xml': DocumentType.XML,
            '.csv': DocumentType.CSV
        }
        
        # 文档分类器
        self.classifier = None
        self.vectorizer = None
        
        # 处理队列
        self.processing_queue = asyncio.Queue()
        
        # 统计信息
        self.stats = {
            "total_documents": 0,
            "documents_by_type": {},
            "documents_by_category": {},
            "documents_by_status": {},
            "processing_time_avg": 0.0,
            "storage_size": 0,
            "index_size": 0
        }
    
    async def initialize(self):
        """初始化文档管理器"""
        logger.info("Initializing document manager")
        
        # 初始化数据库
        await self._init_database()
        
        # 初始化Redis
        await self._init_redis()
        
        # 初始化分类器
        await self._init_classifier()
        
        # 启动处理任务
        asyncio.create_task(self._processing_loop())
        asyncio.create_task(self._maintenance_loop())
        
        logger.info("Document manager initialized successfully")
    
    async def _init_database(self):
        """初始化数据库"""
        db_config = self.config.get('database', {})
        database_url = db_config.get('url', 'sqlite+aiosqlite:///./documents.db')
        
        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # 创建表
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def _init_redis(self):
        """初始化Redis"""
        redis_config = self.config.get('redis', {})
        self.redis_client = redis.Redis(
            host=redis_config.get('host', 'localhost'),
            port=redis_config.get('port', 6379),
            db=redis_config.get('db', 1),
            decode_responses=True
        )
    
    async def _init_classifier(self):
        """初始化文档分类器"""
        # 这里可以加载预训练的分类模型
        # 暂时使用简单的关键词分类
        self.category_keywords = {
            DocumentCategory.TCM_THEORY: ["中医", "中药", "针灸", "推拿", "经络", "穴位", "阴阳", "五行", "气血"],
            DocumentCategory.SYMPTOM_ANALYSIS: ["症状", "体征", "诊断", "检查", "化验", "影像"],
            DocumentCategory.TREATMENT_PLAN: ["治疗", "方案", "处方", "用药", "手术", "康复"],
            DocumentCategory.PREVENTION: ["预防", "保健", "养生", "健康管理", "体检"],
            DocumentCategory.NUTRITION: ["营养", "饮食", "食疗", "维生素", "矿物质"],
            DocumentCategory.EXERCISE: ["运动", "锻炼", "健身", "体育", "康复训练"],
            DocumentCategory.MENTAL_HEALTH: ["心理", "精神", "情绪", "压力", "焦虑", "抑郁"],
            DocumentCategory.EMERGENCY: ["急救", "急诊", "紧急", "抢救", "创伤"],
            DocumentCategory.RESEARCH: ["研究", "论文", "实验", "临床试验", "统计"],
            DocumentCategory.DRUG_INFO: ["药物", "药品", "药理", "副作用", "禁忌"]
        }
        
        # 初始化TF-IDF向量化器
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=None,  # 中文停用词需要自定义
            ngram_range=(1, 2)
        )
    
    async def add_document(
        self,
        file_path: Union[str, Path],
        title: Optional[str] = None,
        category: Optional[DocumentCategory] = None,
        metadata: Optional[DocumentMetadata] = None,
        priority: ProcessingPriority = ProcessingPriority.MEDIUM,
        user_id: Optional[str] = None
    ) -> str:
        """
        添加文档
        
        Args:
            file_path: 文件路径
            title: 文档标题
            category: 文档分类
            metadata: 元数据
            priority: 处理优先级
            user_id: 用户ID
            
        Returns:
            文档ID
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # 生成文档ID
        document_id = str(uuid.uuid4())
        
        # 检测文档类型
        doc_type = self._detect_document_type(file_path)
        
        # 计算文件哈希
        file_hash = await self._calculate_file_hash(file_path)
        
        # 检查重复文档
        existing_doc = await self._find_document_by_hash(file_hash)
        if existing_doc:
            logger.warning(f"Document already exists: {existing_doc['id']}")
            return existing_doc['id']
        
        # 复制文件到存储目录
        storage_file_path = await self._store_file(file_path, document_id, doc_type)
        
        # 创建文档记录
        document = DocumentModel(
            id=document_id,
            title=title or file_path.stem,
            type=doc_type.value,
            category=category.value if category else DocumentCategory.GENERAL_HEALTH.value,
            status=DocumentStatus.PENDING.value,
            priority=priority.value,
            file_path=str(storage_file_path),
            file_hash=file_hash,
            file_size=file_path.stat().st_size,
            metadata=metadata.__dict__ if metadata else {},
            current_version="1.0"
        )
        
        # 保存到数据库
        async with self.async_session() as session:
            session.add(document)
            await session.commit()
        
        # 添加到处理队列
        await self.processing_queue.put({
            "document_id": document_id,
            "action": "index",
            "priority": priority.value,
            "user_id": user_id
        })
        
        # 更新统计信息
        self.stats["total_documents"] += 1
        self.stats["documents_by_type"][doc_type.value] = self.stats["documents_by_type"].get(doc_type.value, 0) + 1
        
        logger.info(f"Document added: {document_id} - {title}")
        return document_id
    
    async def update_document(
        self,
        document_id: str,
        file_path: Optional[Union[str, Path]] = None,
        title: Optional[str] = None,
        category: Optional[DocumentCategory] = None,
        metadata: Optional[DocumentMetadata] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """
        更新文档
        
        Args:
            document_id: 文档ID
            file_path: 新文件路径（可选）
            title: 新标题（可选）
            category: 新分类（可选）
            metadata: 新元数据（可选）
            user_id: 用户ID
            
        Returns:
            是否成功
        """
        async with self.async_session() as session:
            # 查找文档
            result = await session.get(DocumentModel, document_id)
            if not result:
                return False
            
            document = result
            changes = []
            
            # 如果有新文件，创建新版本
            if file_path:
                file_path = Path(file_path)
                if file_path.exists():
                    # 计算新文件哈希
                    new_file_hash = await self._calculate_file_hash(file_path)
                    
                    if new_file_hash != document.file_hash:
                        # 创建新版本
                        version_id = await self._create_document_version(
                            document_id, file_path, user_id, ["文件内容更新"]
                        )
                        
                        # 更新文档记录
                        document.file_hash = new_file_hash
                        document.file_size = file_path.stat().st_size
                        document.version_count += 1
                        document.current_version = f"{document.version_count}.0"
                        document.status = DocumentStatus.PENDING.value
                        changes.append("文件内容更新")
            
            # 更新其他字段
            if title and title != document.title:
                document.title = title
                changes.append(f"标题更新: {title}")
            
            if category and category.value != document.category:
                document.category = category.value
                changes.append(f"分类更新: {category.value}")
            
            if metadata:
                document.metadata = metadata.__dict__
                changes.append("元数据更新")
            
            document.updated_at = datetime.utcnow()
            
            await session.commit()
            
            # 如果有变更，重新索引
            if changes:
                await self.processing_queue.put({
                    "document_id": document_id,
                    "action": "reindex",
                    "priority": ProcessingPriority.HIGH.value,
                    "user_id": user_id,
                    "changes": changes
                })
            
            logger.info(f"Document updated: {document_id} - Changes: {changes}")
            return True
    
    async def delete_document(self, document_id: str, user_id: Optional[str] = None) -> bool:
        """
        删除文档
        
        Args:
            document_id: 文档ID
            user_id: 用户ID
            
        Returns:
            是否成功
        """
        async with self.async_session() as session:
            # 查找文档
            result = await session.get(DocumentModel, document_id)
            if not result:
                return False
            
            document = result
            
            # 标记为删除
            document.status = DocumentStatus.DELETED.value
            document.is_active = False
            document.updated_at = datetime.utcnow()
            
            await session.commit()
            
            # 从向量数据库中删除
            await self._remove_from_vector_db(document_id)
            
            # 删除文件（可选，也可以移动到回收站）
            # await self._delete_document_files(document_id)
            
            logger.info(f"Document deleted: {document_id}")
            return True
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        获取文档信息
        
        Args:
            document_id: 文档ID
            
        Returns:
            文档信息
        """
        async with self.async_session() as session:
            result = await session.get(DocumentModel, document_id)
            if not result or not result.is_active:
                return None
            
            document = result
            
            return {
                "id": document.id,
                "title": document.title,
                "type": document.type,
                "category": document.category,
                "status": document.status,
                "file_path": document.file_path,
                "file_size": document.file_size,
                "metadata": document.metadata,
                "created_at": document.created_at.isoformat(),
                "updated_at": document.updated_at.isoformat(),
                "indexed_at": document.indexed_at.isoformat() if document.indexed_at else None,
                "version_count": document.version_count,
                "current_version": document.current_version
            }
    
    async def search_documents(
        self,
        query: Optional[str] = None,
        category: Optional[DocumentCategory] = None,
        doc_type: Optional[DocumentType] = None,
        status: Optional[DocumentStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        搜索文档
        
        Args:
            query: 搜索查询
            category: 文档分类
            doc_type: 文档类型
            status: 文档状态
            date_from: 开始日期
            date_to: 结束日期
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            搜索结果
        """
        # 这里应该实现更复杂的搜索逻辑
        # 包括全文搜索、向量搜索等
        
        async with self.async_session() as session:
            
            # 构建查询条件
            conditions = [DocumentModel.is_active == True]
            
            if category:
                conditions.append(DocumentModel.category == category.value)
            
            if doc_type:
                conditions.append(DocumentModel.type == doc_type.value)
            
            if status:
                conditions.append(DocumentModel.status == status.value)
            
            if date_from:
                conditions.append(DocumentModel.created_at >= date_from)
            
            if date_to:
                conditions.append(DocumentModel.created_at <= date_to)
            
            # 如果有查询词，添加文本搜索条件
            if query:
                text_conditions = or_(
                    DocumentModel.title.contains(query),
                    # 这里可以添加更多的文本搜索条件
                )
                conditions.append(text_conditions)
            
            # 执行查询
            stmt = select(DocumentModel).where(and_(*conditions)).offset(offset).limit(limit)
            result = await session.execute(stmt)
            documents = result.scalars().all()[:1000]  # 限制查询结果数量
            
            # 计算总数
            count_stmt = select(DocumentModel).where(and_(*conditions))
            count_result = await session.execute(count_stmt)
            total_count = len(count_result.scalars().all()[:1000]  # 限制查询结果数量)
            
            # 转换结果
            results = []
            for doc in documents:
                results.append({
                    "id": doc.id,
                    "title": doc.title,
                    "type": doc.type,
                    "category": doc.category,
                    "status": doc.status,
                    "file_size": doc.file_size,
                    "created_at": doc.created_at.isoformat(),
                    "updated_at": doc.updated_at.isoformat(),
                    "current_version": doc.current_version
                })
            
            return {
                "documents": results,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + len(results) < total_count
            }
    
    async def get_document_content(self, document_id: str) -> Optional[str]:
        """
        获取文档内容
        
        Args:
            document_id: 文档ID
            
        Returns:
            文档内容
        """
        document = await self.get_document(document_id)
        if not document:
            return None
        
        file_path = Path(document["file_path"])
        if not file_path.exists():
            return None
        
        doc_type = DocumentType(document["type"])
        
        try:
            return await self._extract_content(file_path, doc_type)
        except Exception as e:
            logger.error(f"Error extracting content from {document_id}: {e}")
            return None
    
    async def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        """
        获取文档块
        
        Args:
            document_id: 文档ID
            
        Returns:
            文档块列表
        """
        async with self.async_session() as session:
            
            stmt = select(DocumentChunkModel).where(
                DocumentChunkModel.document_id == document_id
            ).order_by(DocumentChunkModel.chunk_index)
            
            result = await session.execute(stmt)
            chunks = result.scalars().all()[:1000]  # 限制查询结果数量
            
            return [
                DocumentChunk(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    content=chunk.content,
                    chunk_index=chunk.chunk_index,
                    start_position=chunk.start_position or 0,
                    end_position=chunk.end_position or 0,
                    chunk_type=chunk.chunk_type or "paragraph",
                    metadata=chunk.metadata or {}
                )
                for chunk in chunks
            ]
    
    async def _processing_loop(self):
        """文档处理循环"""
        while True:
            try:
                # 获取处理任务
                task = await self.processing_queue.get()
                
                document_id = task["document_id"]
                action = task["action"]
                
                logger.info(f"Processing document: {document_id} - Action: {action}")
                
                if action == "index":
                    await self._index_document(document_id)
                elif action == "reindex":
                    await self._reindex_document(document_id)
                elif action == "classify":
                    await self._classify_document(document_id)
                
                self.processing_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                await asyncio.sleep(5)
    
    async def _index_document(self, document_id: str):
        """索引文档"""
        start_time = datetime.now()
        
        try:
            # 更新状态为处理中
            await self._update_document_status(document_id, DocumentStatus.PROCESSING)
            
            # 获取文档信息
            document = await self.get_document(document_id)
            if not document:
                return
            
            # 提取内容
            content = await self.get_document_content(document_id)
            if not content:
                await self._update_document_status(document_id, DocumentStatus.FAILED)
                return
            
            # 自动分类
            if document["category"] == DocumentCategory.GENERAL_HEALTH.value:
                category = await self._auto_classify_document(content)
                if category:
                    await self._update_document_category(document_id, category)
            
            # 提取元数据
            metadata = await self._extract_metadata(document_id, content)
            await self._update_document_metadata(document_id, metadata)
            
            # 分块处理
            chunks = await self._chunk_document(document_id, content)
            await self._save_document_chunks(document_id, chunks)
            
            # 向量化并存储到向量数据库
            await self._vectorize_and_store(document_id, chunks)
            
            # 更新状态为已索引
            await self._update_document_status(document_id, DocumentStatus.INDEXED)
            
            # 记录索引时间
            async with self.async_session() as session:
                result = await session.get(DocumentModel, document_id)
                if result:
                    result.indexed_at = datetime.utcnow()
                    await session.commit()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Document indexed successfully: {document_id} - Time: {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error indexing document {document_id}: {e}")
            await self._update_document_status(document_id, DocumentStatus.FAILED)
    
    async def _reindex_document(self, document_id: str):
        """重新索引文档"""
        # 删除旧的索引数据
        await self._remove_from_vector_db(document_id)
        await self._delete_document_chunks(document_id)
        
        # 重新索引
        await self._index_document(document_id)
    
    async def _classify_document(self, document_id: str):
        """分类文档"""
        content = await self.get_document_content(document_id)
        if not content:
            return
        
        category = await self._auto_classify_document(content)
        if category:
            await self._update_document_category(document_id, category)
    
    async def _auto_classify_document(self, content: str) -> Optional[DocumentCategory]:
        """自动分类文档"""
        # 使用关键词匹配进行简单分类
        content_lower = content.lower()
        
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                score += content_lower.count(keyword)
            
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            # 返回得分最高的分类
            best_category = max(category_scores, key=category_scores.get)
            return best_category
        
        return None
    
    async def _extract_metadata(self, document_id: str, content: str) -> DocumentMetadata:
        """提取文档元数据"""
        # 提取关键词
        keywords = jieba.analyse.extract_tags(content, topK=10)
        
        # 计算质量分数（基于内容长度、结构等）
        quality_score = min(1.0, len(content) / 10000)  # 简单的质量评估
        
        # 生成摘要（这里简化处理）
        sentences = content.split('。')
        summary = '。'.join(sentences[:3]) if len(sentences) > 3 else content[:200]
        
        return DocumentMetadata(
            title="",  # 将在后续更新
            keywords=keywords,
            summary=summary,
            word_count=len(content),
            quality_score=quality_score,
            confidence_score=0.8  # 默认置信度
        )
    
    async def _chunk_document(self, document_id: str, content: str) -> List[str]:
        """分块文档"""
        # 简单的分块策略：按段落分块
        paragraphs = content.split('\n\n')
        
        chunks = []
        current_chunk = ""
        max_chunk_size = self.config.get('max_chunk_size', 1000)
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) > max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def _save_document_chunks(self, document_id: str, chunks: List[str]):
        """保存文档块"""
        async with self.async_session() as session:
            # 删除旧的块
            await session.execute(
                delete(DocumentChunkModel).where(
                    DocumentChunkModel.document_id == document_id
                )
            )
            
            # 保存新的块
            for i, chunk_content in enumerate(chunks):
                chunk = DocumentChunkModel(
                    id=str(uuid.uuid4()),
                    document_id=document_id,
                    chunk_index=i,
                    content=chunk_content,
                    content_hash=hashlib.md5(chunk_content.encode()).hexdigest(),
                    chunk_type="paragraph"
                )
                session.add(chunk)
            
            await session.commit()
    
    async def _vectorize_and_store(self, document_id: str, chunks: List[str]):
        """向量化并存储到向量数据库"""
        # 这里应该调用向量数据库的API
        # 暂时跳过实际的向量化过程
        logger.info(f"Vectorizing document: {document_id} with {len(chunks)} chunks")
    
    async def _remove_from_vector_db(self, document_id: str):
        """从向量数据库中删除"""
        # 这里应该调用向量数据库的删除API
        logger.info(f"Removing document from vector DB: {document_id}")
    
    async def _delete_document_chunks(self, document_id: str):
        """删除文档块"""
        async with self.async_session() as session:
            await session.execute(
                delete(DocumentChunkModel).where(
                    DocumentChunkModel.document_id == document_id
                )
            )
            await session.commit()
    
    async def _update_document_status(self, document_id: str, status: DocumentStatus):
        """更新文档状态"""
        async with self.async_session() as session:
            result = await session.get(DocumentModel, document_id)
            if result:
                result.status = status.value
                result.updated_at = datetime.utcnow()
                await session.commit()
    
    async def _update_document_category(self, document_id: str, category: DocumentCategory):
        """更新文档分类"""
        async with self.async_session() as session:
            result = await session.get(DocumentModel, document_id)
            if result:
                result.category = category.value
                result.updated_at = datetime.utcnow()
                await session.commit()
    
    async def _update_document_metadata(self, document_id: str, metadata: DocumentMetadata):
        """更新文档元数据"""
        async with self.async_session() as session:
            result = await session.get(DocumentModel, document_id)
            if result:
                result.metadata = metadata.__dict__
                result.updated_at = datetime.utcnow()
                await session.commit()
    
    async def _create_document_version(
        self,
        document_id: str,
        file_path: Path,
        user_id: str,
        changes: List[str]
    ) -> str:
        """创建文档版本"""
        version_id = str(uuid.uuid4())
        
        # 复制文件到版本存储目录
        version_file_path = await self._store_version_file(file_path, document_id, version_id)
        
        # 计算文件哈希
        file_hash = await self._calculate_file_hash(file_path)
        
        # 获取当前版本号
        async with self.async_session() as session:
            result = await session.get(DocumentModel, document_id)
            if result:
                current_version = result.version_count + 1
                version_number = f"{current_version}.0"
                
                # 创建版本记录
                version = DocumentVersionModel(
                    id=version_id,
                    document_id=document_id,
                    version_number=version_number,
                    file_path=str(version_file_path),
                    file_hash=file_hash,
                    changes=changes,
                    created_by=user_id,
                    is_current=True
                )
                
                # 将之前的版本标记为非当前版本
                await session.execute(
                    update(DocumentVersionModel)
                    .where(DocumentVersionModel.document_id == document_id)
                    .values(is_current=False)
                )
                
                session.add(version)
                await session.commit()
                
                return version_id
        
        return ""
    
    def _detect_document_type(self, file_path: Path) -> DocumentType:
        """检测文档类型"""
        suffix = file_path.suffix.lower()
        return self.supported_types.get(suffix, DocumentType.TEXT)
    
    async def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希"""
        hash_md5 = hashlib.md5()
        async with aiofiles.open(file_path, 'rb') as f:
            async for chunk in f:
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    async def _find_document_by_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """根据哈希查找文档"""
        async with self.async_session() as session:
            
            stmt = select(DocumentModel).where(
                DocumentModel.file_hash == file_hash,
                DocumentModel.is_active == True
            )
            result = await session.execute(stmt)
            document = result.scalar_one_or_none()
            
            if document:
                return {"id": document.id, "title": document.title}
            
            return None
    
    async def _store_file(self, source_path: Path, document_id: str, doc_type: DocumentType) -> Path:
        """存储文件"""
        # 创建存储目录结构
        type_dir = self.storage_path / doc_type.value
        type_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成存储文件名
        file_extension = source_path.suffix
        storage_filename = f"{document_id}{file_extension}"
        storage_path = type_dir / storage_filename
        
        # 复制文件
        async with aiofiles.open(source_path, 'rb') as src:
            async with aiofiles.open(storage_path, 'wb') as dst:
                async for chunk in src:
                    await dst.write(chunk)
        
        return storage_path
    
    async def _store_version_file(self, source_path: Path, document_id: str, version_id: str) -> Path:
        """存储版本文件"""
        # 创建版本存储目录
        version_dir = self.storage_path / "versions" / document_id
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成版本文件名
        file_extension = source_path.suffix
        version_filename = f"{version_id}{file_extension}"
        version_path = version_dir / version_filename
        
        # 复制文件
        async with aiofiles.open(source_path, 'rb') as src:
            async with aiofiles.open(version_path, 'wb') as dst:
                async for chunk in src:
                    await dst.write(chunk)
        
        return version_path
    
    async def _extract_content(self, file_path: Path, doc_type: DocumentType) -> str:
        """提取文档内容"""
        if doc_type == DocumentType.TEXT:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        
        elif doc_type == DocumentType.PDF:
            return await self._extract_pdf_content(file_path)
        
        elif doc_type == DocumentType.WORD:
            return await self._extract_word_content(file_path)
        
        elif doc_type == DocumentType.EXCEL:
            return await self._extract_excel_content(file_path)
        
        elif doc_type == DocumentType.HTML:
            return await self._extract_html_content(file_path)
        
        elif doc_type == DocumentType.MARKDOWN:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        
        elif doc_type == DocumentType.JSON:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                data = json.loads(await f.read())
                return json.dumps(data, ensure_ascii=False, indent=2)
        
        elif doc_type == DocumentType.CSV:
            return await self._extract_csv_content(file_path)
        
        else:
            # 对于其他类型，尝试作为文本读取
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    return await f.read()
            except:
                return ""
    
    async def _extract_pdf_content(self, file_path: Path) -> str:
        """提取PDF内容"""
        try:
            doc = fitz.open(str(file_path))
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Error extracting PDF content: {e}")
            return ""
    
    async def _extract_word_content(self, file_path: Path) -> str:
        """提取Word内容"""
        try:
            doc = docx.Document(str(file_path))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting Word content: {e}")
            return ""
    
    async def _extract_excel_content(self, file_path: Path) -> str:
        """提取Excel内容"""
        try:
            df = pd.read_excel(str(file_path))
            return df.to_string()
        except Exception as e:
            logger.error(f"Error extracting Excel content: {e}")
            return ""
    
    async def _extract_html_content(self, file_path: Path) -> str:
        """提取HTML内容"""
        try:
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                html_content = await f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text()
        except Exception as e:
            logger.error(f"Error extracting HTML content: {e}")
            return ""
    
    async def _extract_csv_content(self, file_path: Path) -> str:
        """提取CSV内容"""
        try:
            df = pd.read_csv(str(file_path))
            return df.to_string()
        except Exception as e:
            logger.error(f"Error extracting CSV content: {e}")
            return ""
    
    async def _maintenance_loop(self):
        """维护循环"""
        while True:
            try:
                # 清理过期的临时文件
                await self._cleanup_temp_files()
                
                # 更新统计信息
                await self._update_statistics()
                
                # 优化数据库
                await self._optimize_database()
                
                await asyncio.sleep(3600)  # 每小时执行一次
                
            except Exception as e:
                logger.error(f"Error in maintenance loop: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_temp_files(self):
        """清理临时文件"""
        # 清理超过7天的临时文件
        cutoff_time = datetime.now() - timedelta(days=7)
        
        temp_dir = self.storage_path / "temp"
        if temp_dir.exists():
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    if datetime.fromtimestamp(stat.st_mtime) < cutoff_time:
                        try:
                            file_path.unlink()
                            logger.debug(f"Cleaned up temp file: {file_path}")
                        except Exception as e:
                            logger.error(f"Error cleaning up temp file {file_path}: {e}")
    
    async def _update_statistics(self):
        """更新统计信息"""
        async with self.async_session() as session:
            
            # 总文档数
            total_result = await session.execute(
                select(func.count(DocumentModel.id)).where(DocumentModel.is_active == True)
            )
            self.stats["total_documents"] = total_result.scalar()
            
            # 按类型统计
            type_result = await session.execute(
                select(DocumentModel.type, func.count(DocumentModel.id))
                .where(DocumentModel.is_active == True)
                .group_by(DocumentModel.type)
            )
            self.stats["documents_by_type"] = dict(type_result.all()[:1000]  # 限制查询结果数量)
            
            # 按分类统计
            category_result = await session.execute(
                select(DocumentModel.category, func.count(DocumentModel.id))
                .where(DocumentModel.is_active == True)
                .group_by(DocumentModel.category)
            )
            self.stats["documents_by_category"] = dict(category_result.all()[:1000]  # 限制查询结果数量)
            
            # 按状态统计
            status_result = await session.execute(
                select(DocumentModel.status, func.count(DocumentModel.id))
                .where(DocumentModel.is_active == True)
                .group_by(DocumentModel.status)
            )
            self.stats["documents_by_status"] = dict(status_result.all()[:1000]  # 限制查询结果数量)
            
            # 存储大小统计
            size_result = await session.execute(
                select(func.sum(DocumentModel.file_size))
                .where(DocumentModel.is_active == True)
            )
            self.stats["storage_size"] = size_result.scalar() or 0
    
    async def _optimize_database(self):
        """优化数据库"""
        # 这里可以执行数据库优化操作
        # 如清理过期数据、重建索引等
        pass
    
    async def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        await self._update_statistics()
        return self.stats.copy()
    
    async def get_document_versions(self, document_id: str) -> List[Dict[str, Any]]:
        """获取文档版本列表"""
        async with self.async_session() as session:
            
            stmt = select(DocumentVersionModel).where(
                DocumentVersionModel.document_id == document_id
            ).order_by(DocumentVersionModel.created_at.desc())
            
            result = await session.execute(stmt)
            versions = result.scalars().all()[:1000]  # 限制查询结果数量
            
            return [
                {
                    "id": version.id,
                    "version_number": version.version_number,
                    "created_at": version.created_at.isoformat(),
                    "created_by": version.created_by,
                    "changes": version.changes,
                    "is_current": version.is_current
                }
                for version in versions
            ]
    
    async def restore_document_version(self, document_id: str, version_id: str) -> bool:
        """恢复文档版本"""
        async with self.async_session() as session:
            # 获取版本信息
            version = await session.get(DocumentVersionModel, version_id)
            if not version or version.document_id != document_id:
                return False
            
            # 获取文档信息
            document = await session.get(DocumentModel, document_id)
            if not document:
                return False
            
            # 复制版本文件到当前位置
            version_file_path = Path(version.file_path)
            current_file_path = Path(document.file_path)
            
            if version_file_path.exists():
                async with aiofiles.open(version_file_path, 'rb') as src:
                    async with aiofiles.open(current_file_path, 'wb') as dst:
                        async for chunk in src:
                            await dst.write(chunk)
                
                # 更新文档信息
                document.file_hash = version.file_hash
                document.status = DocumentStatus.PENDING.value
                document.updated_at = datetime.utcnow()
                
                # 更新当前版本标记
                await session.execute(
                    update(DocumentVersionModel)
                    .where(DocumentVersionModel.document_id == document_id)
                    .values(is_current=False)
                )
                
                version.is_current = True
                
                await session.commit()
                
                # 重新索引
                await self.processing_queue.put({
                    "document_id": document_id,
                    "action": "reindex",
                    "priority": ProcessingPriority.HIGH.value
                })
                
                logger.info(f"Document version restored: {document_id} -> {version_id}")
                return True
        
        return False 