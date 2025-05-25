#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据管道和ETL模块 - 处理RAG数据流和中医知识库更新
"""

import asyncio
import time
import uuid
import json
from typing import Dict, List, Any, Optional, Callable, Union, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import aiofiles
from loguru import logger

from ..observability.metrics import MetricsCollector


class PipelineStatus(str, Enum):
    """管道状态"""
    IDLE = "idle"               # 空闲
    RUNNING = "running"         # 运行中
    PAUSED = "paused"           # 暂停
    FAILED = "failed"           # 失败
    COMPLETED = "completed"     # 完成


class DataFormat(str, Enum):
    """数据格式"""
    JSON = "json"               # JSON格式
    CSV = "csv"                 # CSV格式
    XML = "xml"                 # XML格式
    TEXT = "text"               # 纯文本
    MARKDOWN = "markdown"       # Markdown格式
    PDF = "pdf"                 # PDF格式
    DOCX = "docx"              # Word文档


class ProcessingMode(str, Enum):
    """处理模式"""
    BATCH = "batch"             # 批处理
    STREAM = "stream"           # 流处理
    REAL_TIME = "real_time"     # 实时处理


@dataclass
class DataSource:
    """数据源"""
    id: str
    name: str
    type: str                   # file, database, api, stream
    config: Dict[str, Any]
    format: DataFormat
    enabled: bool = True
    last_processed: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "config": self.config,
            "format": self.format.value,
            "enabled": self.enabled,
            "last_processed": self.last_processed
        }


@dataclass
class DataRecord:
    """数据记录"""
    id: str
    source_id: str
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    processed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "processed": self.processed
        }


@dataclass
class ProcessingStep:
    """处理步骤"""
    id: str
    name: str
    processor: Callable
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    order: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "config": self.config,
            "enabled": self.enabled,
            "order": self.order
        }


@dataclass
class Pipeline:
    """数据管道"""
    id: str
    name: str
    description: str
    sources: List[DataSource]
    steps: List[ProcessingStep]
    mode: ProcessingMode = ProcessingMode.BATCH
    status: PipelineStatus = PipelineStatus.IDLE
    schedule: Optional[str] = None  # cron表达式
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    last_run: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "sources": [s.to_dict() for s in self.sources],
            "steps": [s.to_dict() for s in self.steps],
            "mode": self.mode.value,
            "status": self.status.value,
            "schedule": self.schedule,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_run": self.last_run
        }


class DataExtractor:
    """数据提取器"""
    
    def __init__(self):
        self.extractors = {
            "file": self._extract_from_file,
            "database": self._extract_from_database,
            "api": self._extract_from_api,
            "stream": self._extract_from_stream
        }
    
    async def extract(self, source: DataSource) -> AsyncGenerator[DataRecord, None]:
        """提取数据"""
        extractor = self.extractors.get(source.type)
        if not extractor:
            raise ValueError(f"不支持的数据源类型: {source.type}")
        
        async for record in extractor(source):
            yield record
    
    async def _extract_from_file(self, source: DataSource) -> AsyncGenerator[DataRecord, None]:
        """从文件提取数据"""
        file_path = source.config.get("path")
        if not file_path:
            raise ValueError("文件路径未配置")
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            if source.format == DataFormat.JSON:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    data = json.loads(content)
                    
                    if isinstance(data, list):
                        for i, item in enumerate(data):
                            yield DataRecord(
                                id=f"{source.id}_{i}",
                                source_id=source.id,
                                content=item,
                                metadata={"file_path": file_path, "index": i}
                            )
                    else:
                        yield DataRecord(
                            id=f"{source.id}_0",
                            source_id=source.id,
                            content=data,
                            metadata={"file_path": file_path}
                        )
            
            elif source.format == DataFormat.TEXT:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    yield DataRecord(
                        id=f"{source.id}_0",
                        source_id=source.id,
                        content=content,
                        metadata={"file_path": file_path}
                    )
            
            elif source.format == DataFormat.CSV:
                # 简化的CSV处理
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    lines = await f.readlines()
                    headers = lines[0].strip().split(',') if lines else []
                    
                    for i, line in enumerate(lines[1:], 1):
                        values = line.strip().split(',')
                        if len(values) == len(headers):
                            record_data = dict(zip(headers, values))
                            yield DataRecord(
                                id=f"{source.id}_{i}",
                                source_id=source.id,
                                content=record_data,
                                metadata={"file_path": file_path, "row": i}
                            )
            
        except Exception as e:
            logger.error(f"文件提取失败: {file_path} - {e}")
            raise
    
    async def _extract_from_database(self, source: DataSource) -> AsyncGenerator[DataRecord, None]:
        """从数据库提取数据"""
        # 简化实现，实际应该支持各种数据库
        db_config = source.config
        query = db_config.get("query", "SELECT * FROM documents")
        
        # 模拟数据库查询
        logger.info(f"执行数据库查询: {query}")
        
        # 这里应该是实际的数据库连接和查询
        mock_data = [
            {"id": 1, "title": "中医基础理论", "content": "中医基础理论内容..."},
            {"id": 2, "title": "方剂学", "content": "方剂学内容..."},
        ]
        
        for i, item in enumerate(mock_data):
            yield DataRecord(
                id=f"{source.id}_db_{i}",
                source_id=source.id,
                content=item,
                metadata={"query": query, "row_id": item.get("id")}
            )
    
    async def _extract_from_api(self, source: DataSource) -> AsyncGenerator[DataRecord, None]:
        """从API提取数据"""
        import aiohttp
        
        api_config = source.config
        url = api_config.get("url")
        headers = api_config.get("headers", {})
        params = api_config.get("params", {})
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if isinstance(data, list):
                            for i, item in enumerate(data):
                                yield DataRecord(
                                    id=f"{source.id}_api_{i}",
                                    source_id=source.id,
                                    content=item,
                                    metadata={"url": url, "index": i}
                                )
                        else:
                            yield DataRecord(
                                id=f"{source.id}_api_0",
                                source_id=source.id,
                                content=data,
                                metadata={"url": url}
                            )
                    else:
                        raise Exception(f"API请求失败: {response.status}")
        
        except Exception as e:
            logger.error(f"API提取失败: {url} - {e}")
            raise
    
    async def _extract_from_stream(self, source: DataSource) -> AsyncGenerator[DataRecord, None]:
        """从流提取数据"""
        # 模拟流数据
        stream_config = source.config
        topic = stream_config.get("topic", "default")
        
        logger.info(f"连接到流: {topic}")
        
        # 这里应该是实际的流连接（如Kafka、Redis Stream等）
        for i in range(10):  # 模拟10条流数据
            await asyncio.sleep(0.1)  # 模拟流延迟
            
            yield DataRecord(
                id=f"{source.id}_stream_{i}",
                source_id=source.id,
                content={"message": f"流消息 {i}", "timestamp": time.time()},
                metadata={"topic": topic, "offset": i}
            )


class DataTransformer:
    """数据转换器"""
    
    def __init__(self):
        self.transformers = {
            "text_cleaner": self._clean_text,
            "tcm_extractor": self._extract_tcm_entities,
            "document_splitter": self._split_document,
            "metadata_enricher": self._enrich_metadata,
            "format_converter": self._convert_format,
            "deduplicator": self._deduplicate
        }
    
    async def transform(self, record: DataRecord, step: ProcessingStep) -> List[DataRecord]:
        """转换数据"""
        transformer_name = step.config.get("transformer")
        transformer = self.transformers.get(transformer_name)
        
        if not transformer:
            raise ValueError(f"不支持的转换器: {transformer_name}")
        
        return await transformer(record, step.config)
    
    async def _clean_text(self, record: DataRecord, config: Dict[str, Any]) -> List[DataRecord]:
        """清理文本"""
        content = record.content
        
        if isinstance(content, str):
            # 基础文本清理
            cleaned = content.strip()
            cleaned = ' '.join(cleaned.split())  # 规范化空白字符
            
            # 移除特殊字符（可配置）
            if config.get("remove_special_chars", False):
                import re
                cleaned = re.sub(r'[^\w\s\u4e00-\u9fff]', '', cleaned)
            
            record.content = cleaned
            record.metadata["cleaned"] = True
        
        elif isinstance(content, dict) and "text" in content:
            # 处理包含文本字段的字典
            content["text"] = content["text"].strip()
            record.content = content
            record.metadata["cleaned"] = True
        
        return [record]
    
    async def _extract_tcm_entities(self, record: DataRecord, config: Dict[str, Any]) -> List[DataRecord]:
        """提取中医实体"""
        import jieba
        
        # 中医术语词典（简化版）
        tcm_terms = {
            "症状": ["头痛", "发热", "咳嗽", "胸闷", "腹痛", "失眠", "乏力"],
            "体质": ["气虚质", "阳虚质", "阴虚质", "痰湿质", "湿热质", "血瘀质", "气郁质", "特禀质", "平和质"],
            "脏腑": ["心", "肝", "脾", "肺", "肾", "胆", "胃", "大肠", "小肠", "膀胱", "三焦"],
            "中药": ["人参", "黄芪", "当归", "川芎", "白术", "茯苓", "甘草", "生姜", "大枣"],
            "方剂": ["四君子汤", "四物汤", "逍遥散", "补中益气汤", "六味地黄丸"]
        }
        
        content = record.content
        text = content if isinstance(content, str) else content.get("text", "")
        
        # 分词
        words = jieba.lcut(text)
        
        # 提取中医实体
        entities = {}
        for category, terms in tcm_terms.items():
            found_terms = [term for term in terms if term in text]
            if found_terms:
                entities[category] = found_terms
        
        # 更新记录
        if isinstance(record.content, dict):
            record.content["tcm_entities"] = entities
        else:
            record.content = {
                "text": text,
                "tcm_entities": entities
            }
        
        record.metadata["tcm_extracted"] = True
        record.metadata["entity_count"] = sum(len(terms) for terms in entities.values())
        
        return [record]
    
    async def _split_document(self, record: DataRecord, config: Dict[str, Any]) -> List[DataRecord]:
        """分割文档"""
        chunk_size = config.get("chunk_size", 1000)
        overlap = config.get("overlap", 100)
        
        content = record.content
        text = content if isinstance(content, str) else content.get("text", "")
        
        if len(text) <= chunk_size:
            return [record]
        
        # 分割文本
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            
            # 创建新的记录
            chunk_record = DataRecord(
                id=f"{record.id}_chunk_{chunk_id}",
                source_id=record.source_id,
                content=chunk_text if isinstance(record.content, str) else {
                    **record.content,
                    "text": chunk_text
                },
                metadata={
                    **record.metadata,
                    "chunk_id": chunk_id,
                    "chunk_start": start,
                    "chunk_end": end,
                    "original_id": record.id
                }
            )
            
            chunks.append(chunk_record)
            
            start = end - overlap
            chunk_id += 1
        
        return chunks
    
    async def _enrich_metadata(self, record: DataRecord, config: Dict[str, Any]) -> List[DataRecord]:
        """丰富元数据"""
        content = record.content
        text = content if isinstance(content, str) else content.get("text", "")
        
        # 计算文本统计
        record.metadata.update({
            "char_count": len(text),
            "word_count": len(text.split()),
            "line_count": text.count('\n') + 1,
            "enriched_at": time.time()
        })
        
        # 检测语言（简化）
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        if chinese_chars > len(text) * 0.3:
            record.metadata["language"] = "zh"
        else:
            record.metadata["language"] = "en"
        
        return [record]
    
    async def _convert_format(self, record: DataRecord, config: Dict[str, Any]) -> List[DataRecord]:
        """转换格式"""
        target_format = config.get("target_format", "json")
        
        if target_format == "json" and not isinstance(record.content, dict):
            record.content = {"text": str(record.content)}
        elif target_format == "text" and isinstance(record.content, dict):
            record.content = record.content.get("text", str(record.content))
        
        record.metadata["format"] = target_format
        return [record]
    
    async def _deduplicate(self, record: DataRecord, config: Dict[str, Any]) -> List[DataRecord]:
        """去重"""
        # 简化的去重实现
        content_hash = hash(str(record.content))
        record.metadata["content_hash"] = content_hash
        
        # 实际应该维护一个去重缓存
        return [record]


class DataLoader:
    """数据加载器"""
    
    def __init__(self):
        self.loaders = {
            "vector_db": self._load_to_vector_db,
            "knowledge_graph": self._load_to_knowledge_graph,
            "file": self._load_to_file,
            "database": self._load_to_database,
            "cache": self._load_to_cache
        }
    
    async def load(self, records: List[DataRecord], config: Dict[str, Any]) -> bool:
        """加载数据"""
        loader_type = config.get("type", "file")
        loader = self.loaders.get(loader_type)
        
        if not loader:
            raise ValueError(f"不支持的加载器类型: {loader_type}")
        
        return await loader(records, config)
    
    async def _load_to_vector_db(self, records: List[DataRecord], config: Dict[str, Any]) -> bool:
        """加载到向量数据库"""
        try:
            # 这里应该是实际的向量数据库操作
            logger.info(f"加载 {len(records)} 条记录到向量数据库")
            
            for record in records:
                # 模拟向量化和存储
                text = record.content if isinstance(record.content, str) else record.content.get("text", "")
                
                # 这里应该调用实际的嵌入模型
                vector = [0.1] * 768  # 模拟向量
                
                # 存储到向量数据库
                logger.debug(f"存储向量: {record.id}")
            
            return True
            
        except Exception as e:
            logger.error(f"向量数据库加载失败: {e}")
            return False
    
    async def _load_to_knowledge_graph(self, records: List[DataRecord], config: Dict[str, Any]) -> bool:
        """加载到知识图谱"""
        try:
            logger.info(f"加载 {len(records)} 条记录到知识图谱")
            
            for record in records:
                # 提取实体和关系
                entities = record.metadata.get("tcm_entities", {})
                
                # 这里应该调用知识图谱API
                logger.debug(f"创建知识图谱节点: {record.id}")
            
            return True
            
        except Exception as e:
            logger.error(f"知识图谱加载失败: {e}")
            return False
    
    async def _load_to_file(self, records: List[DataRecord], config: Dict[str, Any]) -> bool:
        """加载到文件"""
        try:
            output_path = config.get("path", "output.json")
            format_type = config.get("format", "json")
            
            data = [record.to_dict() for record in records]
            
            async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
                if format_type == "json":
                    await f.write(json.dumps(data, ensure_ascii=False, indent=2))
                else:
                    for record in records:
                        await f.write(str(record.content) + '\n')
            
            logger.info(f"数据已保存到文件: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"文件加载失败: {e}")
            return False
    
    async def _load_to_database(self, records: List[DataRecord], config: Dict[str, Any]) -> bool:
        """加载到数据库"""
        try:
            # 这里应该是实际的数据库操作
            table_name = config.get("table", "documents")
            logger.info(f"加载 {len(records)} 条记录到数据库表: {table_name}")
            
            for record in records:
                # 模拟数据库插入
                logger.debug(f"插入记录: {record.id}")
            
            return True
            
        except Exception as e:
            logger.error(f"数据库加载失败: {e}")
            return False
    
    async def _load_to_cache(self, records: List[DataRecord], config: Dict[str, Any]) -> bool:
        """加载到缓存"""
        try:
            # 这里应该是实际的缓存操作
            logger.info(f"加载 {len(records)} 条记录到缓存")
            
            for record in records:
                # 模拟缓存存储
                logger.debug(f"缓存记录: {record.id}")
            
            return True
            
        except Exception as e:
            logger.error(f"缓存加载失败: {e}")
            return False


class PipelineExecutor:
    """管道执行器"""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        self.extractor = DataExtractor()
        self.transformer = DataTransformer()
        self.loader = DataLoader()
        self.metrics_collector = metrics_collector
        self.running_pipelines: Dict[str, asyncio.Task] = {}
    
    async def execute_pipeline(self, pipeline: Pipeline) -> bool:
        """执行管道"""
        if pipeline.id in self.running_pipelines:
            logger.warning(f"管道已在运行: {pipeline.name}")
            return False
        
        pipeline.status = PipelineStatus.RUNNING
        pipeline.last_run = time.time()
        
        try:
            # 创建执行任务
            task = asyncio.create_task(self._run_pipeline(pipeline))
            self.running_pipelines[pipeline.id] = task
            
            # 等待执行完成
            success = await task
            
            pipeline.status = PipelineStatus.COMPLETED if success else PipelineStatus.FAILED
            
            # 记录指标
            if self.metrics_collector:
                await self.metrics_collector.increment_counter(
                    "pipeline_executions",
                    {
                        "pipeline": pipeline.name,
                        "status": "success" if success else "failed"
                    }
                )
            
            return success
            
        except Exception as e:
            logger.error(f"管道执行失败: {pipeline.name} - {e}")
            pipeline.status = PipelineStatus.FAILED
            return False
        
        finally:
            # 清理运行状态
            if pipeline.id in self.running_pipelines:
                del self.running_pipelines[pipeline.id]
    
    async def _run_pipeline(self, pipeline: Pipeline) -> bool:
        """运行管道"""
        start_time = time.time()
        total_records = 0
        processed_records = 0
        
        try:
            # 按顺序执行处理步骤
            sorted_steps = sorted(pipeline.steps, key=lambda x: x.order)
            
            for source in pipeline.sources:
                if not source.enabled:
                    continue
                
                logger.info(f"处理数据源: {source.name}")
                
                # 提取数据
                async for record in self.extractor.extract(source):
                    total_records += 1
                    current_records = [record]
                    
                    # 应用转换步骤
                    for step in sorted_steps:
                        if not step.enabled:
                            continue
                        
                        new_records = []
                        for current_record in current_records:
                            transformed = await self.transformer.transform(current_record, step)
                            new_records.extend(transformed)
                        
                        current_records = new_records
                    
                    # 加载数据
                    if current_records:
                        load_config = pipeline.steps[-1].config if pipeline.steps else {}
                        success = await self.loader.load(current_records, load_config)
                        
                        if success:
                            processed_records += len(current_records)
                        else:
                            logger.error(f"记录加载失败: {record.id}")
                
                # 更新数据源最后处理时间
                source.last_processed = time.time()
            
            # 记录执行统计
            duration = time.time() - start_time
            
            if self.metrics_collector:
                await self.metrics_collector.record_histogram(
                    "pipeline_duration",
                    duration,
                    {"pipeline": pipeline.name}
                )
                
                await self.metrics_collector.record_histogram(
                    "pipeline_records_processed",
                    processed_records,
                    {"pipeline": pipeline.name}
                )
            
            logger.info(f"管道执行完成: {pipeline.name}, 处理 {processed_records}/{total_records} 条记录, 耗时 {duration:.2f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"管道运行失败: {pipeline.name} - {e}")
            return False
    
    async def stop_pipeline(self, pipeline_id: str) -> bool:
        """停止管道"""
        if pipeline_id not in self.running_pipelines:
            return False
        
        task = self.running_pipelines[pipeline_id]
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        del self.running_pipelines[pipeline_id]
        logger.info(f"管道已停止: {pipeline_id}")
        
        return True
    
    def get_running_pipelines(self) -> List[str]:
        """获取运行中的管道"""
        return list(self.running_pipelines.keys())


class DataPipelineManager:
    """数据管道管理器"""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        self.pipelines: Dict[str, Pipeline] = {}
        self.executor = PipelineExecutor(metrics_collector)
        self.scheduler_running = False
        self.metrics_collector = metrics_collector
    
    async def create_pipeline(
        self,
        name: str,
        description: str,
        sources: List[DataSource],
        steps: List[ProcessingStep],
        mode: ProcessingMode = ProcessingMode.BATCH,
        schedule: Optional[str] = None
    ) -> str:
        """创建管道"""
        pipeline_id = str(uuid.uuid4())
        
        pipeline = Pipeline(
            id=pipeline_id,
            name=name,
            description=description,
            sources=sources,
            steps=steps,
            mode=mode,
            schedule=schedule
        )
        
        self.pipelines[pipeline_id] = pipeline
        
        logger.info(f"管道已创建: {name} ({pipeline_id})")
        
        return pipeline_id
    
    async def run_pipeline(self, pipeline_id: str) -> bool:
        """运行管道"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            logger.error(f"管道不存在: {pipeline_id}")
            return False
        
        return await self.executor.execute_pipeline(pipeline)
    
    async def stop_pipeline(self, pipeline_id: str) -> bool:
        """停止管道"""
        return await self.executor.stop_pipeline(pipeline_id)
    
    async def get_pipeline(self, pipeline_id: str) -> Optional[Pipeline]:
        """获取管道"""
        return self.pipelines.get(pipeline_id)
    
    async def list_pipelines(self) -> List[Pipeline]:
        """列出所有管道"""
        return list(self.pipelines.values())
    
    async def delete_pipeline(self, pipeline_id: str) -> bool:
        """删除管道"""
        if pipeline_id in self.pipelines:
            # 先停止管道
            await self.stop_pipeline(pipeline_id)
            
            # 删除管道
            del self.pipelines[pipeline_id]
            
            logger.info(f"管道已删除: {pipeline_id}")
            return True
        
        return False
    
    async def start_scheduler(self):
        """启动调度器"""
        if self.scheduler_running:
            return
        
        self.scheduler_running = True
        asyncio.create_task(self._scheduler_loop())
        logger.info("管道调度器已启动")
    
    async def stop_scheduler(self):
        """停止调度器"""
        self.scheduler_running = False
        logger.info("管道调度器已停止")
    
    async def _scheduler_loop(self):
        """调度器循环"""
        while self.scheduler_running:
            try:
                current_time = time.time()
                
                for pipeline in self.pipelines.values():
                    if pipeline.schedule and pipeline.status == PipelineStatus.IDLE:
                        # 简化的调度逻辑（实际应该使用cron解析）
                        if self._should_run_pipeline(pipeline, current_time):
                            logger.info(f"调度执行管道: {pipeline.name}")
                            asyncio.create_task(self.executor.execute_pipeline(pipeline))
                
                await asyncio.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                logger.error(f"调度器错误: {e}")
                await asyncio.sleep(5)
    
    def _should_run_pipeline(self, pipeline: Pipeline, current_time: float) -> bool:
        """判断是否应该运行管道"""
        # 简化的调度逻辑
        if not pipeline.last_run:
            return True
        
        # 如果超过1小时没运行，就运行一次
        return current_time - pipeline.last_run > 3600
    
    async def get_pipeline_statistics(self) -> Dict[str, Any]:
        """获取管道统计"""
        total_pipelines = len(self.pipelines)
        running_pipelines = len(self.executor.get_running_pipelines())
        
        status_counts = {}
        for pipeline in self.pipelines.values():
            status = pipeline.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_pipelines": total_pipelines,
            "running_pipelines": running_pipelines,
            "status_distribution": status_counts,
            "scheduler_running": self.scheduler_running
        }


# 全局管道管理器实例
_pipeline_manager: Optional[DataPipelineManager] = None


def initialize_pipeline_manager(metrics_collector: Optional[MetricsCollector] = None) -> DataPipelineManager:
    """初始化管道管理器"""
    global _pipeline_manager
    _pipeline_manager = DataPipelineManager(metrics_collector)
    return _pipeline_manager


def get_pipeline_manager() -> Optional[DataPipelineManager]:
    """获取管道管理器实例"""
    return _pipeline_manager


# 便捷的管道构建器
class PipelineBuilder:
    """管道构建器"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.sources: List[DataSource] = []
        self.steps: List[ProcessingStep] = []
        self.mode = ProcessingMode.BATCH
        self.schedule = None
    
    def add_file_source(
        self,
        name: str,
        file_path: str,
        format: DataFormat = DataFormat.JSON
    ) -> 'PipelineBuilder':
        """添加文件数据源"""
        source = DataSource(
            id=str(uuid.uuid4()),
            name=name,
            type="file",
            config={"path": file_path},
            format=format
        )
        self.sources.append(source)
        return self
    
    def add_processing_step(
        self,
        name: str,
        transformer: str,
        config: Optional[Dict[str, Any]] = None,
        order: int = 0
    ) -> 'PipelineBuilder':
        """添加处理步骤"""
        step = ProcessingStep(
            id=str(uuid.uuid4()),
            name=name,
            processor=lambda x: x,  # 占位符
            config={**(config or {}), "transformer": transformer},
            order=order
        )
        self.steps.append(step)
        return self
    
    def set_mode(self, mode: ProcessingMode) -> 'PipelineBuilder':
        """设置处理模式"""
        self.mode = mode
        return self
    
    def set_schedule(self, schedule: str) -> 'PipelineBuilder':
        """设置调度"""
        self.schedule = schedule
        return self
    
    async def build(self) -> str:
        """构建管道"""
        if not _pipeline_manager:
            raise RuntimeError("管道管理器未初始化")
        
        return await _pipeline_manager.create_pipeline(
            name=self.name,
            description=self.description,
            sources=self.sources,
            steps=self.steps,
            mode=self.mode,
            schedule=self.schedule
        ) 