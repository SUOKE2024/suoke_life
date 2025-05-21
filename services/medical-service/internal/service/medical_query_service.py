#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any

import grpc
from grpc import RpcError

from internal.model.medical_query import MedicalQuery, SourceReference

logger = logging.getLogger(__name__)

class MedicalQueryService:
    """医疗查询服务，处理用户的医疗咨询问题"""

    def __init__(self, repository, services_config):
        """
        初始化医疗查询服务
        
        Args:
            repository: 医疗查询存储库
            services_config: 外部服务配置字典
        """
        self.repository = repository
        self.services_config = services_config
        self._rag_client = None
        self._med_knowledge_client = None

    def _get_rag_client(self):
        """获取RAG服务的客户端"""
        if not self._rag_client:
            try:
                # 从配置获取服务地址
                rag_config = self.services_config.get('rag', {})
                host = rag_config.get('host', 'localhost')
                port = rag_config.get('port', 50051)
                
                # 建立gRPC连接
                channel = grpc.insecure_channel(f'{host}:{port}')
                
                # 导入生成的gRPC存根
                from api.grpc import rag_pb2_grpc
                self._rag_client = rag_pb2_grpc.RAGServiceStub(channel)
                
                logger.info(f"已连接到RAG服务: {host}:{port}")
            except Exception as e:
                logger.error(f"连接RAG服务失败: {str(e)}")
                raise
        
        return self._rag_client

    def _get_med_knowledge_client(self):
        """获取医学知识服务的客户端"""
        if not self._med_knowledge_client:
            try:
                # 从配置获取服务地址
                med_knowledge_config = self.services_config.get('med_knowledge', {})
                host = med_knowledge_config.get('host', 'localhost')
                port = med_knowledge_config.get('port', 50051)
                
                # 建立gRPC连接
                channel = grpc.insecure_channel(f'{host}:{port}')
                
                # 导入生成的gRPC存根
                from api.grpc import med_knowledge_pb2_grpc
                self._med_knowledge_client = med_knowledge_pb2_grpc.MedKnowledgeServiceStub(channel)
                
                logger.info(f"已连接到医学知识服务: {host}:{port}")
            except Exception as e:
                logger.error(f"连接医学知识服务失败: {str(e)}")
                raise
        
        return self._med_knowledge_client

    def submit_medical_query(self, user_id: str, query_text: str, related_symptoms: List[str] = None,
                            related_conditions: List[str] = None, include_western_medicine: bool = True,
                            include_tcm: bool = True) -> MedicalQuery:
        """
        提交医疗查询并获取回答
        
        Args:
            user_id: 用户ID
            query_text: 查询文本
            related_symptoms: 相关症状列表
            related_conditions: 相关疾病列表
            include_western_medicine: 是否包含西医知识
            include_tcm: 是否包含中医知识
            
        Returns:
            医疗查询对象，包含回答和相关信息
        """
        try:
            logger.info(f"用户 {user_id} 提交医疗查询: {query_text}")
            
            # 验证输入
            if not user_id or not query_text:
                raise ValueError("用户ID和查询文本不能为空")
            
            # 准备相关元数据
            related_symptoms = related_symptoms or []
            related_conditions = related_conditions or []
            
            # 紧急情况检测
            is_emergency = self._check_if_emergency(query_text, related_symptoms)
            
            # 获取RAG客户端
            rag_client = self._get_rag_client()
            
            # 准备查询参数
            from api.grpc import rag_pb2
            rag_request = rag_pb2.SearchAndGenerateRequest(
                query=query_text,
                metadata={
                    "user_id": user_id,
                    "related_symptoms": ",".join(related_symptoms),
                    "related_conditions": ",".join(related_conditions),
                    "include_western_medicine": str(include_western_medicine).lower(),
                    "include_tcm": str(include_tcm).lower()
                },
                max_results=5
            )
            
            # 调用RAG服务
            rag_response = rag_client.search_and_generate(rag_request)
            
            # 处理响应
            answer = rag_response.answer
            sources = []
            
            for source in rag_response.sources:
                sources.append(SourceReference(
                    title=source.title,
                    author=source.author,
                    publication=source.publication,
                    url=source.url,
                    citation=source.citation
                ))
            
            # 添加免责声明
            disclaimer = "本回答仅供参考，不构成医疗建议。如症状严重，请立即就医。"
            
            # 处理后续问题
            follow_up_questions = list(rag_response.follow_up_questions)
            
            # 创建查询对象
            query = MedicalQuery(
                id=None,  # 由存储库生成
                user_id=user_id,
                query_text=query_text,
                answer=answer,
                sources=sources,
                is_emergency_advice=is_emergency,
                disclaimer=disclaimer,
                follow_up_questions=follow_up_questions
            )
            
            # 保存到存储库
            query_id = self.repository.save_query(query)
            query.id = query_id
            
            logger.info(f"已处理医疗查询: {query_id}")
            return query
            
        except RpcError as e:
            logger.error(f"RAG服务调用失败: {str(e)}")
            # 降级处理: 返回一个基础回答
            query = MedicalQuery(
                id=None,
                user_id=user_id,
                query_text=query_text,
                answer="很抱歉，目前无法处理您的问题。请稍后再试或联系客服。",
                sources=[],
                is_emergency_advice=False,
                disclaimer="本回答仅供参考，不构成医疗建议。如症状严重，请立即就医。",
                follow_up_questions=[]
            )
            query_id = self.repository.save_query(query)
            query.id = query_id
            return query
            
        except Exception as e:
            logger.error(f"处理医疗查询失败: {str(e)}", exc_info=True)
            raise

    def _check_if_emergency(self, query_text: str, symptoms: List[str]) -> bool:
        """
        检查查询是否是紧急情况
        
        Args:
            query_text: 查询文本
            symptoms: 症状列表
            
        Returns:
            是否紧急情况
        """
        # 紧急关键词列表
        emergency_keywords = [
            "急救", "胸痛", "呼吸困难", "大出血", "严重头痛", "昏迷", "休克", "抽搐",
            "突然瘫痪", "严重烧伤", "断肢", "自杀", "急性", "立即", "120", "救护车"
        ]
        
        # 紧急症状列表
        emergency_symptoms = [
            "胸痛", "呼吸困难", "大量出血", "剧烈头痛", "意识丧失", "抽搐", "瘫痪",
            "严重烧伤", "严重外伤", "窒息", "癫痫发作", "过敏性休克"
        ]
        
        # 检查查询文本中是否包含紧急关键词
        for keyword in emergency_keywords:
            if keyword in query_text:
                logger.warning(f"检测到紧急情况关键词: {keyword}")
                return True
        
        # 检查症状列表中是否包含紧急症状
        for symptom in symptoms:
            if symptom in emergency_symptoms:
                logger.warning(f"检测到紧急症状: {symptom}")
                return True
        
        return False
    
    def get_query_by_id(self, query_id: str) -> Optional[MedicalQuery]:
        """
        根据ID获取医疗查询记录
        
        Args:
            query_id: 查询ID
            
        Returns:
            医疗查询对象，如果不存在则返回None
        """
        try:
            logger.info(f"获取医疗查询记录: {query_id}")
            return self.repository.get_query_by_id(query_id)
        except Exception as e:
            logger.error(f"获取医疗查询记录失败: {str(e)}")
            raise

    def list_queries_by_user(self, user_id: str, limit: int = 10, offset: int = 0) -> List[MedicalQuery]:
        """
        获取用户的医疗查询历史记录
        
        Args:
            user_id: 用户ID
            limit: 每页记录数，默认10条
            offset: 偏移量，用于分页
            
        Returns:
            医疗查询对象列表
        """
        try:
            logger.info(f"获取用户 {user_id} 的医疗查询历史记录，限制 {limit}，偏移 {offset}")
            return self.repository.list_queries_by_user(user_id, limit, offset)
        except Exception as e:
            logger.error(f"获取用户医疗查询历史记录失败: {str(e)}")
            raise

    def get_query_count_by_user(self, user_id: str) -> int:
        """
        获取用户的医疗查询历史记录总数
        
        Args:
            user_id: 用户ID
            
        Returns:
            查询记录总数
        """
        try:
            logger.info(f"获取用户 {user_id} 的医疗查询历史记录总数")
            return self.repository.get_query_count_by_user(user_id)
        except Exception as e:
            logger.error(f"获取用户医疗查询历史记录总数失败: {str(e)}")
            raise

    def search_queries(self, user_id: str, keyword: str, limit: int = 10, offset: int = 0) -> List[MedicalQuery]:
        """
        搜索用户的医疗查询历史记录
        
        Args:
            user_id: 用户ID
            keyword: 搜索关键词
            limit: 每页记录数，默认10条
            offset: 偏移量，用于分页
            
        Returns:
            医疗查询对象列表
        """
        try:
            logger.info(f"搜索用户 {user_id} 的医疗查询历史记录，关键词 '{keyword}'")
            return self.repository.search_queries(user_id, keyword, limit, offset)
        except Exception as e:
            logger.error(f"搜索用户医疗查询历史记录失败: {str(e)}")
            raise

    def get_search_count(self, user_id: str, keyword: str) -> int:
        """
        获取搜索结果的总数
        
        Args:
            user_id: 用户ID
            keyword: 搜索关键词
            
        Returns:
            搜索结果总数
        """
        try:
            # 这里假设存储库中有一个类似功能的方法，如果没有，可以先获取所有结果再计数
            # 但这不是一个性能最佳的解决方案，应该由存储库提供此功能
            results = self.repository.search_queries(user_id, keyword, limit=1000, offset=0)
            return len(results)
        except Exception as e:
            logger.error(f"获取搜索结果总数失败: {str(e)}")
            raise

    def delete_query(self, query_id: str) -> bool:
        """
        删除医疗查询记录
        
        Args:
            query_id: 查询ID
            
        Returns:
            删除是否成功
        """
        try:
            logger.info(f"删除医疗查询记录: {query_id}")
            return self.repository.delete_query(query_id)
        except Exception as e:
            logger.error(f"删除医疗查询记录失败: {str(e)}")
            raise