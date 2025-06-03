#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
本地生成器实现
"""

import re
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator, Tuple
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from loguru import logger

from ..model.document import Document, DocumentReference
from .base import BaseGenerator

class LocalGenerator(BaseGenerator):
    """
    基于本地模型的生成器实现
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化本地生成器
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.model_path = config['local'].get('model_path', '/app/data/models/llm')
        self.device = config['local'].get('device', 'cuda' if torch.cuda.is_available() else 'cpu')
        self.max_length = config['local'].get('max_length', 1024)
        self.model = None
        self.tokenizer = None
        
    async def initialize(self):
        """初始化生成器"""
        logger.info(f"Initializing local generator with model from: {self.model_path}")
        logger.info(f"Using device: {self.device}")
        
        # 在非阻塞线程中加载模型，避免阻塞事件循环
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._load_model)
        
        logger.info("Local generator initialized successfully")
    
    def _load_model(self):
        """加载模型和分词器"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map=self.device
            )
            logger.info("Model and tokenizer loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    async def _do_generate(
        self,
        query: str,
        context_documents: List[Document],
        system_prompt: Optional[str] = None,
        generation_params: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Tuple[str, List[DocumentReference]]:
        """
        使用本地模型生成回答
        
        Args:
            query: 用户查询
            context_documents: 上下文文档
            system_prompt: 系统提示词
            generation_params: 生成参数
            user_id: 用户ID
            
        Returns:
            生成的回答和引用的文档
        """
        if self.model is None or self.tokenizer is None:
            logger.error("Model or tokenizer not initialized")
            return "抱歉，生成服务尚未完成初始化，请稍后再试。", []
        
        # 合并生成参数
        params = {
            "max_length": self.max_length,
            "temperature": 0.7,
            "top_p": 0.9,
            "repetition_penalty": 1.1,
            "do_sample": True
        }
        
        if generation_params:
            params.update(generation_params)
        
        # 创建提示
        prompt = self.create_prompt(query, context_documents, system_prompt)
        
        try:
            # 在非阻塞线程中进行推理
            loop = asyncio.get_event_loop()
            answer = await loop.run_in_executor(None, self._generate_text, prompt, params)
            
            # 从回答中提取引用
            references = self.extract_references(answer, context_documents)
            
            return answer, references
            
        except Exception as e:
            logger.error(f"Error generating with local model: {str(e)}")
            return "抱歉，生成回答时出现错误，请稍后再试。", []
    
    def _generate_text(self, prompt: str, params: Dict[str, Any]) -> str:
        """在模型上执行文本生成"""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                attention_mask=inputs.attention_mask,
                pad_token_id=self.tokenizer.eos_token_id,
                **params
            )
        
        # 解码输出
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 移除提示部分，只保留生成的回答
        answer = generated_text[len(prompt):].strip()
        
        return answer
    
    async def stream_generate(
        self,
        query: str,
        context_documents: List[Document],
        system_prompt: Optional[str] = None,
        generation_params: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> AsyncGenerator[Tuple[str, bool, Optional[List[DocumentReference]]], None]:
        """
        流式生成回答（模拟实现，本地模型一般不支持真正的流式生成）
        
        Args:
            query: 用户查询
            context_documents: 上下文文档
            system_prompt: 系统提示词
            generation_params: 生成参数
            user_id: 用户ID
            
        Yields:
            元组: (答案片段, 是否最后一个片段, 引用的文档[仅在最后一个片段中])
        """
        try:
            # 先完整生成回答
            answer, references = await self._do_generate(
                query, context_documents, system_prompt, generation_params, user_id
            )
            
            # 然后模拟流式输出
            chunk_size = 10  # 每个片段的大约字符数
            
            for i in range(0, len(answer), chunk_size):
                chunk = answer[i:i+chunk_size]
                is_final = (i + chunk_size) >= len(answer)
                
                if is_final:
                    yield chunk, True, references
                else:
                    yield chunk, False, None
                    
                # 模拟流式生成的延迟
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error in stream generation with local model: {str(e)}")
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
        
        system_content = system_prompt or "你是索克生活平台的中医健康顾问，基于提供的背景知识回答用户问题。"
        
        # 构建完整提示
        complete_prompt = f"""<系统>
{system_content}
</系统>

<背景知识>
{context_text}
</背景知识>

<用户>
{query}
</用户>

<助手>
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
        # 释放模型资源
        if self.model is not None:
            del self.model
            self.model = None
        
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        
        # 清理CUDA缓存
        if torch.cuda.is_available():
            torch.cuda.empty_cache() 