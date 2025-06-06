"""
openai_generator - 索克生活项目模块
"""

from ..model.document import Document, DocumentReference
from .base import BaseGenerator
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import List, Dict, Any, Optional, AsyncGenerator, Tuple
import openai
import os
import re

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OpenAI 生成器实现
"""




class OpenAIGenerator(BaseGenerator):
    """
    基于 OpenAI API 的生成器实现
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化 OpenAI 生成器
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.model_name = config['openai'].get('model_name', 'gpt-3.5-turbo')
        self.temperature = config['openai'].get('temperature', 0.7)
        self.max_tokens = config['openai'].get('max_tokens', 1024)
        self.api_key = config['openai'].get('api_key') or os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not provided in config or environment variables")
        
    async def initialize(self):
        """初始化生成器"""
        logger.info(f"Initializing OpenAI generator with model: {self.model_name}")
        openai.api_key = self.api_key
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _do_generate(
        self,
        query: str,
        context_documents: List[Document],
        system_prompt: Optional[str] = None,
        generation_params: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Tuple[str, List[DocumentReference]]:
        """
        使用 OpenAI API 生成回答
        
        Args:
            query: 用户查询
            context_documents: 上下文文档
            system_prompt: 系统提示词
            generation_params: 生成参数
            user_id: 用户ID
            
        Returns:
            生成的回答和引用的文档
        """
        # 合并生成参数
        params = {
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        
        if generation_params:
            params.update(generation_params)
        
        # 创建提示
        prompt = self.create_prompt(query, context_documents, system_prompt)
        
        try:
            # 调用 OpenAI API
            messages = [
                {"role": "system", "content": system_prompt or "你是索克生活平台的中医健康顾问，基于提供的背景知识回答用户问题。"},
                {"role": "user", "content": prompt}
            ]
            
            response = await openai.ChatCompletion.acreate(
                messages=messages,
                **params
            )
            
            answer = response.choices[0].message.content.strip()
            
            # 提取引用文档
            references = self.extract_references(answer, context_documents)
            
            return answer, references
            
        except Exception as e:
            logger.error(f"Error generating with OpenAI: {str(e)}")
            return "抱歉，生成回答时出现错误，请稍后再试。", []
    
    async def stream_generate(
        self,
        query: str,
        context_documents: List[Document],
        system_prompt: Optional[str] = None,
        generation_params: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> AsyncGenerator[Tuple[str, bool, Optional[List[DocumentReference]]], None]:
        """
        流式生成回答
        
        Args:
            query: 用户查询
            context_documents: 上下文文档
            system_prompt: 系统提示词
            generation_params: 生成参数
            user_id: 用户ID
            
        Yields:
            元组: (答案片段, 是否最后一个片段, 引用的文档[仅在最后一个片段中])
        """
        # 合并生成参数
        params = {
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": True
        }
        
        if generation_params:
            params.update(generation_params)
        
        # 创建提示
        prompt = self.create_prompt(query, context_documents, system_prompt)
        
        try:
            # 调用 OpenAI API
            messages = [
                {"role": "system", "content": system_prompt or "你是索克生活平台的中医健康顾问，基于提供的背景知识回答用户问题。"},
                {"role": "user", "content": prompt}
            ]
            
            stream = await openai.ChatCompletion.acreate(
                messages=messages,
                **params
            )
            
            full_answer = ""
            
            async for chunk in stream:
                if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                    content = chunk.choices[0].delta.content or ""
                    full_answer += content
                    yield content, False, None
            
            # 在最后一个片段中提供引用
            references = self.extract_references(full_answer, context_documents)
            yield "", True, references
            
        except Exception as e:
            logger.error(f"Error in stream generation with OpenAI: {str(e)}")
            yield "抱歉，生成回答时出现错误，请稍后再试。", True, []
    
    def create_prompt(
        self,
        query: str,
        context_documents: List[Document],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        创建包含上下文的提示
        
        Args:
            query: 用户查询
            context_documents: 上下文文档
            system_prompt: 系统提示词
            
        Returns:
            完整的提示
        """
        # 构建上下文文本
        context_text = ""
        for i, doc in enumerate(context_documents):
            context_text += f"\n[文档 {i+1}]: {doc.content}\n"
        
        # 构建完整提示
        complete_prompt = f"""请基于以下背景知识回答用户的问题。
        
背景知识:
{context_text}

用户问题: {query}

要求:
1. 只使用提供的背景知识来回答问题
2. 如果背景知识中没有相关信息，请坦诚告知
3. 回答应简洁、专业、符合中医理论
4. 不要在回答中明确引用文档编号
"""
        
        return complete_prompt
    
    def extract_references(
        self,
        answer: str,
        context_documents: List[Document]
    ) -> List[DocumentReference]:
        """
        从回答和上下文文档中提取引用
        
        Args:
            answer: 生成的回答
            context_documents: 上下文文档
            
        Returns:
            引用的文档列表
        """
        references = []
        
        for doc in context_documents:
            # 检查文档内容是否被引用（简单字符串匹配）
            # 提取文档中的关键句子
            sentences = re.split(r'[.。!！?？;；]', doc.content)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
            
            # 检查是否有任何句子出现在答案中
            is_referenced = False
            matching_snippet = ""
            
            for sentence in sentences:
                if len(sentence) > 15 and sentence in answer:
                    is_referenced = True
                    matching_snippet = sentence
                    break
            
            # 如果没找到匹配的长句子，尝试检查关键词匹配
            if not is_referenced and len(doc.content) > 0:
                # 从文档中提取关键词（简化版实现）
                keywords = [word for word in re.findall(r'[\u4e00-\u9fa5]{2,6}', doc.content) 
                           if len(word) > 1 and word not in ["我们", "您好", "这个", "那个", "什么", "如何", "为什么"]]
                
                # 统计关键词在答案中出现的次数
                keyword_matches = sum(1 for keyword in set(keywords) if keyword in answer)
                
                # 如果匹配了足够多的关键词，认为文档被引用
                if keyword_matches >= 3:
                    is_referenced = True
                    # 使用文档的前30个字符作为片段
                    matching_snippet = doc.content[:min(50, len(doc.content))] + "..."
            
            if is_referenced:
                # 提取文档元数据作为引用
                doc_ref = DocumentReference(
                    id=doc.id,
                    title=doc.metadata.get("title", "未知标题"),
                    source=doc.metadata.get("source", "中医知识库"),
                    url=doc.metadata.get("url", ""),
                    snippet=matching_snippet
                )
                references.append(doc_ref)
        
        return references
    
    async def close(self):
        """关闭生成器及相关连接"""
        pass  # OpenAI API 不需要特殊关闭操作 