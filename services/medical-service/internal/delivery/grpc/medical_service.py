#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import uuid
from datetime import datetime
from typing import Dict, Any

import grpc
from google.protobuf.timestamp_pb2 import Timestamp

from api.grpc import medical_pb2
from api.grpc import medical_pb2_grpc
from internal.model.medical_query import MedicalQuery, SourceReference

logger = logging.getLogger(__name__)

class MedicalServicer(medical_pb2_grpc.MedicalServiceServicer):
    """医疗服务gRPC实现"""
    
    def __init__(self, services):
        """
        初始化医疗服务实现
        
        Args:
            services: 服务对象字典
        """
        self.services = services
        # 获取依赖服务
        self.medical_query_service = services.get('medical_query_service')
        self.medical_record_service = services.get('medical_record_service')
        self.diagnosis_service = services.get('diagnosis_service')
        self.treatment_service = services.get('treatment_service')
        self.health_risk_service = services.get('health_risk_service')
    
    def SubmitMedicalQuery(self, request, context):
        """
        提交医疗查询
        
        Args:
            request: 查询请求
            context: gRPC上下文
            
        Returns:
            医疗查询响应
        """
        try:
            logger.info(f"收到医疗查询请求: {request.query_text}")
            
            # 调用服务
            query = self.medical_query_service.submit_medical_query(
                user_id=request.user_id,
                query_text=request.query_text,
                related_symptoms=list(request.related_symptoms),
                related_conditions=list(request.related_conditions),
                include_western_medicine=request.include_western_medicine,
                include_tcm=request.include_tcm
            )
            
            # 转换为响应
            response = self._convert_query_to_proto(query)
            
            logger.info(f"处理医疗查询请求成功: {query.id}")
            return response
            
        except Exception as e:
            logger.error(f"处理医疗查询请求失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"处理医疗查询失败: {str(e)}")
            return medical_pb2.MedicalQueryResponse()
    
    def GetMedicalQuery(self, request, context):
        """
        获取医疗查询记录
        
        Args:
            request: 获取请求
            context: gRPC上下文
            
        Returns:
            医疗查询响应
        """
        try:
            logger.info(f"收到获取医疗查询请求: {request.query_id}")
            
            # 调用服务
            query = self.medical_query_service.get_query_by_id(request.query_id)
            
            if not query:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"未找到ID为{request.query_id}的医疗查询")
                return medical_pb2.MedicalQueryResponse()
            
            # 转换为响应
            response = self._convert_query_to_proto(query)
            
            logger.info(f"获取医疗查询成功: {query.id}")
            return response
            
        except Exception as e:
            logger.error(f"获取医疗查询失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"获取医疗查询失败: {str(e)}")
            return medical_pb2.MedicalQueryResponse()
    
    def ListMedicalQueriesByUser(self, request, context):
        """
        获取用户的医疗查询历史记录
        
        Args:
            request: 查询列表请求
            context: gRPC上下文
            
        Returns:
            医疗查询列表响应
        """
        try:
            logger.info(f"收到获取用户医疗查询列表请求: {request.user_id}")
            
            # 调用服务
            queries = self.medical_query_service.list_queries_by_user(
                user_id=request.user_id,
                limit=request.limit if request.limit > 0 else 10,
                offset=request.offset if request.offset >= 0 else 0
            )
            
            # 获取总数
            total = self.medical_query_service.get_query_count_by_user(request.user_id)
            
            # 创建响应
            response = medical_pb2.ListMedicalQueriesResponse()
            response.total = total
            
            # 添加查询记录
            for query in queries:
                query_proto = self._convert_query_to_proto(query)
                response.queries.append(query_proto)
            
            logger.info(f"获取用户医疗查询列表成功, 共{len(queries)}条记录")
            return response
            
        except Exception as e:
            logger.error(f"获取用户医疗查询列表失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"获取用户医疗查询列表失败: {str(e)}")
            return medical_pb2.ListMedicalQueriesResponse()
    
    def SearchMedicalQueries(self, request, context):
        """
        搜索医疗查询记录
        
        Args:
            request: 搜索请求
            context: gRPC上下文
            
        Returns:
            医疗查询列表响应
        """
        try:
            logger.info(f"收到搜索医疗查询请求: 用户={request.user_id}, 关键词={request.keyword}")
            
            # 调用服务
            queries = self.medical_query_service.search_queries(
                user_id=request.user_id,
                keyword=request.keyword,
                limit=request.limit if request.limit > 0 else 10,
                offset=request.offset if request.offset >= 0 else 0
            )
            
            # 获取搜索结果总数
            total = self.medical_query_service.get_search_count(
                user_id=request.user_id,
                keyword=request.keyword
            )
            
            # 创建响应
            response = medical_pb2.ListMedicalQueriesResponse()
            response.total = total
            
            # 添加查询记录
            for query in queries:
                query_proto = self._convert_query_to_proto(query)
                response.queries.append(query_proto)
            
            logger.info(f"搜索医疗查询成功, 共{len(queries)}条记录")
            return response
            
        except Exception as e:
            logger.error(f"搜索医疗查询失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"搜索医疗查询失败: {str(e)}")
            return medical_pb2.ListMedicalQueriesResponse()
    
    def DeleteMedicalQuery(self, request, context):
        """
        删除医疗查询记录
        
        Args:
            request: 删除请求
            context: gRPC上下文
            
        Returns:
            删除响应
        """
        try:
            logger.info(f"收到删除医疗查询请求: {request.query_id}")
            
            # 调用服务
            success = self.medical_query_service.delete_query(request.query_id)
            
            if not success:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"未找到ID为{request.query_id}的医疗查询")
                return medical_pb2.DeleteMedicalQueryResponse(success=False)
            
            logger.info(f"删除医疗查询成功: {request.query_id}")
            return medical_pb2.DeleteMedicalQueryResponse(success=True)
            
        except Exception as e:
            logger.error(f"删除医疗查询失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"删除医疗查询失败: {str(e)}")
            return medical_pb2.DeleteMedicalQueryResponse(success=False)
    
    def _convert_query_to_proto(self, query: MedicalQuery) -> medical_pb2.MedicalQueryResponse:
        """
        将MedicalQuery对象转换为protobuf响应对象
        
        Args:
            query: 医疗查询对象
            
        Returns:
            protobuf响应对象
        """
        response = medical_pb2.MedicalQueryResponse(
            response_id=query.id,
            user_id=query.user_id,
            query_text=query.query_text,
            answer=query.answer or "",
            is_emergency_advice=query.is_emergency_advice,
            disclaimer=query.disclaimer or ""
        )
        
        # 添加来源引用
        for source in query.sources:
            source_proto = medical_pb2.SourceReference(
                title=source.title or "",
                author=source.author or "",
                publication=source.publication or "",
                url=source.url or "",
                citation=source.citation or ""
            )
            response.sources.append(source_proto)
        
        # 添加后续问题
        for question in query.follow_up_questions:
            response.follow_up_questions.append(question)
        
        # 添加时间戳
        if query.created_at:
            created_at = Timestamp()
            created_at.FromDatetime(query.created_at)
            response.created_at.CopyFrom(created_at)
        
        if query.updated_at:
            updated_at = Timestamp()
            updated_at.FromDatetime(query.updated_at)
            response.updated_at.CopyFrom(updated_at)
        
        return response 