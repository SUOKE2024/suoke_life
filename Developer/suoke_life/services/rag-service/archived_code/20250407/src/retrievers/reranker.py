from typing import List, Dict, Any, Optional
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from loguru import logger

from config.tcm_rag_config import RerankerConfig

class RerankerDataset(Dataset):
    """重排序数据集"""
    
    def __init__(
        self,
        query: str,
        texts: List[str],
        tokenizer: Any,
        max_length: int
    ):
        """初始化数据集
        
        Args:
            query: 查询文本
            texts: 文档文本列表
            tokenizer: 分词器
            max_length: 最大长度
        """
        self.query = query
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def __len__(self) -> int:
        return len(self.texts)
        
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        text = self.texts[idx]
        
        # 使用交叉编码器的方式编码查询和文档
        encoding = self.tokenizer(
            self.query,
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "token_type_ids": encoding["token_type_ids"].squeeze()
        }

class Reranker:
    """重排序器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化重排序器"""
        self.config = config
        self.model_name = config.get("model_name", "default_model")
        self.device = config.get("device", "cpu")
        
    async def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """重排序方法"""
        # 在实际实现中，这里会调用实际的重排序模型
        # 这里只返回一个模拟的结果
        for i, doc in enumerate(documents):
            doc["score"] = 0.9 - (i * 0.1)  # 模拟分数
            
        return sorted(documents, key=lambda x: x.get("score", 0), reverse=True)[:top_k]

    async def rerank_with_diversity(
        self,
        query: str,
        documents: List[Dict],
        diversity_threshold: float = 0.7
    ) -> List[Dict]:
        """考虑多样性的重排序
        
        Args:
            query: 查询文本
            documents: 待重排序的文档列表
            diversity_threshold: 多样性阈值
            
        Returns:
            重排序后的文档列表
        """
        try:
            # 1. 基础重排序
            reranked_docs = await self.rerank(query, documents)
            
            if len(reranked_docs) <= 1:
                return reranked_docs
                
            # 2. 应用最大边际相关性算法
            selected_docs = [reranked_docs[0]]  # 选择得分最高的文档
            remaining_docs = reranked_docs[1:]
            
            while remaining_docs and len(selected_docs) < self.config.top_k:
                # 计算每个候选文档与已选文档的最大相似度
                max_similarities = []
                
                for doc in remaining_docs:
                    similarities = [
                        self._calculate_similarity(doc, selected)
                        for selected in selected_docs
                    ]
                    max_similarities.append(max(similarities))
                    
                # 选择相似度低且得分高的文档
                scores = []
                for doc, max_sim in zip(remaining_docs, max_similarities):
                    if max_sim > diversity_threshold:
                        score = 0.0  # 相似度过高，不选择
                    else:
                        # 平衡相关性和多样性
                        score = doc["score"] * (1 - max_sim)
                    scores.append(score)
                    
                if not scores:
                    break
                    
                # 选择得分最高的文档
                best_idx = scores.index(max(scores))
                selected_docs.append(remaining_docs[best_idx])
                remaining_docs.pop(best_idx)
            
            return selected_docs
            
        except Exception as e:
            logger.error(f"Error reranking with diversity: {e}")
            return documents
            
    def _calculate_similarity(
        self,
        doc1: Dict,
        doc2: Dict
    ) -> float:
        """计算两个文档的相似度
        
        Args:
            doc1: 第一个文档
            doc2: 第二个文档
            
        Returns:
            相似度分数
        """
        try:
            # TODO: 实现更复杂的相似度计算
            # 1. 使用文档向量计算余弦相似度
            # 2. 考虑文档类型和来源
            # 3. 使用 n-gram 重叠度
            
            # 简单实现：使用文档类型和来源判断
            if doc1.get("doc_type") == doc2.get("doc_type"):
                if doc1.get("source") == doc2.get("source"):
                    return 0.8  # 同源同类型
                return 0.5  # 同类型不同源
            return 0.3  # 不同类型
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0 