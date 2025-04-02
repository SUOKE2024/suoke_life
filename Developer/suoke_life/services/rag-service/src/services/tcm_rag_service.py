from typing import List, Dict, Any, Optional
from loguru import logger

from config.tcm_rag_config import (
    TCMRAGConfig,
    TCMDocumentType,
    RetrievalStrategy
)
from processors.tcm_document_processor import (
    TCMDocument,
    TCMDocumentProcessor
)
from retrievers.tcm_retriever import TCMRetriever
from embeddings.tcm_embeddings import TCMEmbeddingGenerator

class TCMRAGService:
    """中医 RAG 服务"""
    
    def __init__(
        self,
        config: TCMRAGConfig,
        vector_store: Any,
        llm_client: Any,
        knowledge_graph: Any = None
    ):
        """初始化服务
        
        Args:
            config: RAG 配置
            vector_store: 向量存储实例
            llm_client: LLM 客户端实例
            knowledge_graph: 知识图谱实例（可选）
        """
        self.config = config
        self.vector_store = vector_store
        self.llm_client = llm_client
        self.knowledge_graph = knowledge_graph
        
        # 初始化文档处理器
        self.doc_processor = TCMDocumentProcessor(config.document_process)
        
        # 初始化检索器
        self.retriever = TCMRetriever(
            config=config,
            vector_store=vector_store,
            knowledge_graph=knowledge_graph
        )
        
    async def process_and_index_document(
        self,
        document: TCMDocument
    ) -> bool:
        """处理并索引文档
        
        Args:
            document: 待处理的文档
            
        Returns:
            是否成功
        """
        try:
            # 1. 处理文档
            processed_doc = self.doc_processor.process_document(document)
            
            # 2. 生成向量嵌入
            doc_vectors = await self._generate_embeddings(processed_doc)
            
            # 3. 存储向量
            await self.vector_store.add(
                documents=processed_doc.chunks,
                vectors=doc_vectors,
                metadatas=[
                    {
                        "doc_id": document.id,
                        "doc_type": document.doc_type.value,
                        "title": document.title,
                        "source": document.source
                    }
                    for _ in processed_doc.chunks
                ]
            )
            
            # 4. 更新知识图谱
            if self.knowledge_graph:
                await self._update_knowledge_graph(processed_doc)
                
            return True
            
        except Exception as e:
            logger.error(f"Error processing and indexing document: {e}")
            return False
            
    async def query(
        self,
        query: str,
        strategy: RetrievalStrategy = None,
        top_k: int = 5,
        filters: Dict = None
    ) -> Dict:
        """查询处理
        
        Args:
            query: 查询文本
            strategy: 检索策略
            top_k: 返回结果数量
            filters: 过滤条件
            
        Returns:
            处理结果
        """
        try:
            # 1. 检索相关文档
            retrieved_docs = await self.retriever.retrieve(
                query,
                strategy=strategy,
                top_k=top_k,
                filters=filters
            )
            
            if not retrieved_docs:
                return {
                    "answer": "抱歉，未找到相关信息。",
                    "sources": [],
                    "related_docs": []
                }
            
            # 2. 构建提示词
            prompt = self._build_prompt(query, retrieved_docs)
            
            # 3. 调用 LLM
            response = await self._generate_response(prompt)
            
            # 4. 处理响应
            result = {
                "answer": response,
                "sources": self._extract_sources(retrieved_docs),
                "related_docs": retrieved_docs
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "answer": "抱歉，处理查询时出现错误。",
                "sources": [],
                "related_docs": []
            }
            
    async def _generate_embeddings(
        self,
        document: TCMDocument
    ) -> List[List[float]]:
        """生成文档向量
        
        Args:
            document: 处理后的文档
            
        Returns:
            向量列表
        """
        try:
            # TODO: 实现向量生成逻辑
            # 1. 批量生成向量
            # 2. 处理超长文本
            # 3. 错误重试
            return []
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
            
    async def _update_knowledge_graph(
        self,
        document: TCMDocument
    ) -> bool:
        """更新知识图谱
        
        Args:
            document: 处理后的文档
            
        Returns:
            是否成功
        """
        try:
            if not self.knowledge_graph:
                return False
                
            # TODO: 实现知识图谱更新逻辑
            # 1. 实体识别
            # 2. 关系抽取
            # 3. 图谱更新
            return True
            
        except Exception as e:
            logger.error(f"Error updating knowledge graph: {e}")
            return False
            
    def _build_prompt(
        self,
        query: str,
        retrieved_docs: List[Dict]
    ) -> str:
        """构建提示词
        
        Args:
            query: 查询文本
            retrieved_docs: 检索到的文档
            
        Returns:
            完整提示词
        """
        try:
            # 1. 系统提示词
            prompt = self.config.prompt.system_prompt + "\n\n"
            
            # 2. 添加查询前缀
            prompt += self.config.prompt.query_prefix
            
            # 3. 添加查询
            prompt += query + "\n\n"
            
            # 4. 添加上下文
            prompt += "参考资料：\n"
            for i, doc in enumerate(retrieved_docs, 1):
                prompt += f"[{i}] {doc['content']}\n"
                if doc.get("source"):
                    prompt += f"来源：{doc['source']}\n"
                prompt += "\n"
                
            # 5. 添加查询后缀
            prompt += self.config.prompt.query_suffix
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error building prompt: {e}")
            return query
            
    async def _generate_response(self, prompt: str) -> str:
        """生成回复
        
        Args:
            prompt: 完整提示词
            
        Returns:
            生成的回复
        """
        try:
            # 调用 LLM 生成回复
            response = await self.llm_client.generate(
                prompt,
                max_tokens=1024,
                temperature=0.7
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "抱歉，生成回复时出现错误。"
            
    def _extract_sources(self, retrieved_docs: List[Dict]) -> List[Dict]:
        """提取来源信息
        
        Args:
            retrieved_docs: 检索到的文档
            
        Returns:
            来源信息列表
        """
        try:
            sources = []
            for doc in retrieved_docs:
                if doc.get("source"):
                    source = {
                        "title": doc.get("title", "未知标题"),
                        "source": doc["source"],
                        "doc_type": doc.get("doc_type", "未知类型"),
                        "score": doc.get("final_score", 0.0)
                    }
                    if source not in sources:
                        sources.append(source)
            return sources
            
        except Exception as e:
            logger.error(f"Error extracting sources: {e}")
            return [] 