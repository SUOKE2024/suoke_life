from typing import List, Dict, Optional
from dataclasses import dataclass
import re
import jieba
import jieba.posseg as pseg
from loguru import logger

from config.rag_config import (
    DocumentType,
    DocumentProcessConfig,
)

@dataclass
class Document:
    """文档"""
    id: str
    content: str
    doc_type: DocumentType
    title: str
    source: str
    metadata: Dict = None
    chunks: List[Dict] = None

class TCMDocumentProcessor:
    """中医文档处理器"""
    
    def __init__(self, config: DocumentProcessConfig):
        """初始化处理器
        
        Args:
            config: 文档处理配置
        """
        self.config = config
        self._load_tcm_dictionary()
        
    def _load_tcm_dictionary(self):
        """加载中医词典"""
        try:
            # TODO: 加载自定义中医词典
            jieba.load_userdict("data/dictionaries/tcm_dict.txt")
        except Exception as e:
            logger.warning(f"Failed to load TCM dictionary: {e}")
    
    def process_document(self, document: Document) -> Document:
        """处理单个文档
        
        Args:
            document: 待处理的文档
            
        Returns:
            处理后的文档
        """
        try:
            # 1. 文本预处理
            cleaned_text = self._preprocess_text(document.content)
            
            # 2. 分块
            chunks = self._split_into_chunks(cleaned_text)
            
            # 3. 提取关键信息
            enriched_chunks = [
                self._enrich_chunk(chunk, document) 
                for chunk in chunks
            ]
            
            # 4. 更新文档
            document.chunks = enriched_chunks
            return document
            
        except Exception as e:
            logger.error(f"Error processing document {document.id}: {e}")
            return document
    
    def _preprocess_text(self, text: str) -> str:
        """文本预处理
        
        Args:
            text: 原始文本
            
        Returns:
            处理后的文本
        """
        # 1. 移除多余空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 2. 统一标点符号
        text = text.replace('；', ';').replace('，', ',')
        
        # 3. 移除特殊字符
        text = re.sub(r'[^\w\s;,。？！：""《》、]', '', text)
        
        return text.strip()
    
    def _split_into_chunks(self, text: str) -> List[str]:
        """文本分块
        
        Args:
            text: 预处理后的文本
            
        Returns:
            文本块列表
        """
        chunks = []
        
        # 1. 按自然段落分割
        paragraphs = text.split('\n')
        
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para)
            
            # 如果当前段落超过最大块大小，需要进一步分割
            if para_length > self.config.max_chunk_size:
                if current_chunk:
                    chunks.append(''.join(current_chunk))
                    current_chunk = []
                    current_length = 0
                
                # 按句子分割长段落
                sentences = re.split(r'[。！？]', para)
                for sent in sentences:
                    if len(sent) > self.config.max_chunk_size:
                        # 对超长句子进行滑动窗口分割
                        for i in range(0, len(sent), self.config.chunk_size):
                            chunk = sent[i:i + self.config.chunk_size]
                            if len(chunk) >= self.config.min_chunk_size:
                                chunks.append(chunk)
                    elif len(sent) >= self.config.min_chunk_size:
                        chunks.append(sent)
                        
            # 当前段落可以作为一个块
            elif current_length + para_length <= self.config.chunk_size:
                current_chunk.append(para)
                current_length += para_length
                
            # 当前段落导致块超过大小限制
            else:
                if current_chunk:
                    chunks.append(''.join(current_chunk))
                current_chunk = [para]
                current_length = para_length
        
        # 处理最后一个块
        if current_chunk:
            chunks.append(''.join(current_chunk))
            
        return chunks
    
    def _enrich_chunk(self, chunk: str, document: Document) -> Dict:
        """丰富文本块信息
        
        Args:
            chunk: 文本块
            document: 原始文档
            
        Returns:
            丰富后的文本块信息
        """
        # 1. 分词和词性标注
        words = pseg.cut(chunk)
        
        # 2. 提取关键术语
        tcm_terms = []
        for word, flag in words:
            if self._is_tcm_term(word, flag):
                tcm_terms.append(word)
        
        # 3. 计算块权重
        weight = self._calculate_chunk_weight(
            chunk, 
            tcm_terms,
            document.doc_type
        )
        
        return {
            "content": chunk,
            "tcm_terms": tcm_terms,
            "weight": weight,
            "doc_type": document.doc_type.value,
            "source": document.source,
            "title": document.title,
            "metadata": document.metadata
        }
    
    def _is_tcm_term(self, word: str, flag: str) -> bool:
        """判断是否为中医术语
        
        Args:
            word: 词
            flag: 词性
            
        Returns:
            是否为中医术语
        """
        # TODO: 实现更复杂的术语判断逻辑
        return len(word) >= 2 and flag in ['n', 'v', 'a']
    
    def _calculate_chunk_weight(
        self,
        chunk: str,
        tcm_terms: List[str],
        doc_type: DocumentType
    ) -> float:
        """计算文本块权重
        
        Args:
            chunk: 文本块
            tcm_terms: 中医术语列表
            doc_type: 文档类型
            
        Returns:
            权重分数
        """
        try:
            # 1. 基础权重：文档类型权重
            base_weight = self.config.type_weights.get(doc_type, 1.0)
            
            # 2. 术语密度权重
            term_density = len(tcm_terms) / len(chunk)
            term_weight = min(term_density * 2, 1.0)
            
            # 3. 计算最终权重
            final_weight = base_weight * (0.7 + 0.3 * term_weight)
            
            return round(final_weight, 3)
            
        except Exception as e:
            logger.error(f"Error calculating chunk weight: {e}")
            return 1.0 