from typing import List, Dict, Any, Optional
import math
import jieba
import jieba.posseg as pseg
from collections import defaultdict
from loguru import logger

class BM25:
    """BM25 检索算法实现"""
    
    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
        epsilon: float = 0.25
    ):
        """初始化 BM25
        
        Args:
            k1: 词频饱和参数
            b: 文档长度归一化参数
            epsilon: 平滑参数
        """
        self.k1 = k1
        self.b = b
        self.epsilon = epsilon
        
        # 词频统计
        self.doc_freqs = defaultdict(int)  # 文档频率
        self.term_freqs = defaultdict(lambda: defaultdict(int))  # 词项频率
        self.doc_lengths = defaultdict(int)  # 文档长度
        self.avg_doc_length = 0  # 平均文档长度
        self.total_docs = 0  # 文档总数
        self.index_built = False  # 索引是否已建立
        
    def _tokenize(self, text: str) -> List[str]:
        """分词
        
        Args:
            text: 待分词文本
            
        Returns:
            词项列表
        """
        # 使用 jieba 进行分词，过滤停用词和标点
        words = pseg.cut(text)
        return [
            word for word, flag in words
            if flag not in ['x', 'u', 'p', 'c', 'w']
        ]
        
    def add_document(self, doc_id: str, text: str):
        """添加文档到索引
        
        Args:
            doc_id: 文档ID
            text: 文档内容
        """
        try:
            # 分词
            terms = self._tokenize(text)
            
            # 更新文档长度
            doc_length = len(terms)
            self.doc_lengths[doc_id] = doc_length
            
            # 更新词频统计
            term_freq = defaultdict(int)
            for term in terms:
                term_freq[term] += 1
                
            # 更新文档频率和词项频率
            for term, freq in term_freq.items():
                self.doc_freqs[term] += 1
                self.term_freqs[term][doc_id] = freq
                
            self.total_docs += 1
            self.index_built = False
            
        except Exception as e:
            logger.error(f"Error adding document {doc_id}: {e}")
            
    def build_index(self):
        """构建索引"""
        try:
            if self.total_docs == 0:
                return
                
            # 计算平均文档长度
            total_length = sum(self.doc_lengths.values())
            self.avg_doc_length = total_length / self.total_docs
            
            self.index_built = True
            
        except Exception as e:
            logger.error(f"Error building index: {e}")
            
    def get_scores(
        self,
        query: str,
        top_k: Optional[int] = None
    ) -> List[Dict]:
        """计算查询结果分数
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            按分数排序的文档列表
        """
        try:
            if not self.index_built:
                self.build_index()
                
            # 对查询进行分词
            query_terms = self._tokenize(query)
            
            # 计算每个文档的得分
            scores = defaultdict(float)
            
            for term in query_terms:
                # 如果词项不在索引中，跳过
                if term not in self.doc_freqs:
                    continue
                    
                # 计算 IDF
                idf = math.log(
                    (self.total_docs - self.doc_freqs[term] + 0.5)
                    / (self.doc_freqs[term] + 0.5)
                    + self.epsilon
                )
                
                # 对每个包含该词项的文档计算得分
                for doc_id, term_freq in self.term_freqs[term].items():
                    # 文档长度归一化
                    doc_length = self.doc_lengths[doc_id]
                    length_norm = 1 - self.b + self.b * (
                        doc_length / self.avg_doc_length
                    )
                    
                    # BM25 得分计算
                    numerator = term_freq * (self.k1 + 1)
                    denominator = term_freq + self.k1 * length_norm
                    
                    scores[doc_id] += idf * (numerator / denominator)
            
            # 将分数转换为列表并排序
            scored_docs = [
                {"id": doc_id, "score": score}
                for doc_id, score in scores.items()
            ]
            
            scored_docs.sort(key=lambda x: x["score"], reverse=True)
            
            # 如果指定了 top_k，截取指定数量的结果
            if top_k:
                scored_docs = scored_docs[:top_k]
            
            return scored_docs
            
        except Exception as e:
            logger.error(f"Error calculating scores: {e}")
            return []
            
class KeywordSearcher:
    """关键词搜索器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化关键词搜索器"""
        self.config = config
        
    async def search(self, query: str, limit: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """搜索方法"""
        # 在实际实现中，这里会执行关键词搜索
        # 这里只返回一个模拟的结果
        return [
            {"id": "1", "content": "测试内容1", "metadata": {"source": "测试来源1", "type": "article"}},
            {"id": "2", "content": "测试内容2", "metadata": {"source": "测试来源2", "type": "book"}}
        ]

    async def search_documents(
        self,
        query: str,
        top_k: int = 10,
        filters: Dict = None
    ) -> List[Dict]:
        """搜索文档
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            filters: 过滤条件
            
        Returns:
            检索结果列表
        """
        try:
            # 使用 BM25 计算相关性得分
            scored_docs = self.bm25.get_scores(query, top_k)
            
            # 添加文档内容
            results = []
            for doc in scored_docs:
                doc_id = doc["id"]
                if doc_id in self.doc_store:
                    # 合并文档信息和得分
                    result = {
                        **self.doc_store[doc_id],
                        "score": doc["score"]
                    }
                    
                    # 应用过滤条件
                    if filters:
                        skip = False
                        for key, value in filters.items():
                            if result.get(key) != value:
                                skip = True
                                break
                        if skip:
                            continue
                            
                    results.append(result)
                    
                    # 如果达到所需数量，提前返回
                    if len(results) >= top_k:
                        break
                        
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return [] 