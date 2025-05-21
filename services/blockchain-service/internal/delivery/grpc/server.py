#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
区块链服务gRPC实现
"""

import datetime
import logging
from typing import Dict, List

import grpc

# 导入生成的gRPC代码
from api.grpc import blockchain_pb2, blockchain_pb2_grpc

from internal.model.config import AppConfig
from internal.service.blockchain_service import BlockchainService
from pkg.utils.logging_utils import ServiceLogger


class BlockchainServicer(blockchain_pb2_grpc.BlockchainServiceServicer):
    """
    区块链服务gRPC实现
    """
    
    def __init__(self, config: AppConfig):
        """
        初始化服务
        
        Args:
            config: 应用配置
        """
        self.config = config
        self.logger = ServiceLogger("blockchain_grpc")
        
        # 初始化区块链服务
        self.blockchain_service = BlockchainService(config)
        
        self.logger.info("区块链gRPC服务已初始化")
    
    async def StoreHealthData(self, 
                             request: blockchain_pb2.StoreHealthDataRequest, 
                             context: grpc.aio.ServicerContext) -> blockchain_pb2.StoreHealthDataResponse:
        """
        存储健康数据到区块链
        
        Args:
            request: 请求对象
            context: gRPC上下文
            
        Returns:
            存储响应
        """
        self.logger.info(f"接收到存储健康数据请求: 用户 {request.user_id}, 类型 {request.data_type}")
        
        try:
            # 调用区块链服务
            success, message, record = await self.blockchain_service.store_health_data(
                user_id=request.user_id,
                data_type=request.data_type,
                data_hash=request.data_hash,
                encrypted_data=request.encrypted_data,
                metadata=dict(request.metadata) if request.metadata else {}
            )
            
            # 创建响应
            response = blockchain_pb2.StoreHealthDataResponse(
                success=success,
                message=message
            )
            
            # 如果成功，设置交易信息
            if success and record and record.transaction:
                response.transaction_id = record.transaction.transaction_id
                if record.transaction.block_hash:
                    response.block_hash = record.transaction.block_hash
            
            return response
            
        except Exception as e:
            self.logger.error(f"存储健康数据异常: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务内部错误: {str(e)}")
            return blockchain_pb2.StoreHealthDataResponse(
                success=False,
                message=f"服务内部错误: {str(e)}"
            )
    
    async def VerifyHealthData(self, 
                              request: blockchain_pb2.VerifyHealthDataRequest, 
                              context: grpc.aio.ServicerContext) -> blockchain_pb2.VerifyHealthDataResponse:
        """
        验证健康数据完整性
        
        Args:
            request: 请求对象
            context: gRPC上下文
            
        Returns:
            验证响应
        """
        self.logger.info(f"接收到验证健康数据请求: 交易 {request.transaction_id}")
        
        try:
            # 调用区块链服务
            valid, message, verification_time = await self.blockchain_service.verify_health_data(
                transaction_id=request.transaction_id,
                data_hash=request.data_hash
            )
            
            # 创建响应
            response = blockchain_pb2.VerifyHealthDataResponse(
                valid=valid,
                message=message
            )
            
            # 设置验证时间
            if verification_time:
                response.verification_timestamp = int(verification_time.timestamp())
            
            return response
            
        except Exception as e:
            self.logger.error(f"验证健康数据异常: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务内部错误: {str(e)}")
            return blockchain_pb2.VerifyHealthDataResponse(
                valid=False,
                message=f"服务内部错误: {str(e)}"
            )
    
    async def VerifyWithZKP(self, 
                           request: blockchain_pb2.VerifyWithZKPRequest, 
                           context: grpc.aio.ServicerContext) -> blockchain_pb2.VerifyWithZKPResponse:
        """
        使用零知识证明验证健康数据属性
        
        Args:
            request: 请求对象
            context: gRPC上下文
            
        Returns:
            零知识证明验证响应
        """
        self.logger.info(f"接收到零知识证明验证请求: 用户 {request.user_id}, 类型 {request.data_type}")
        
        try:
            # 调用区块链服务
            valid, message, details = await self.blockchain_service.verify_with_zkp(
                user_id=request.user_id,
                verifier_id=request.verifier_id,
                data_type=request.data_type,
                proof=request.proof,
                public_inputs=request.public_inputs
            )
            
            # 创建响应
            response = blockchain_pb2.VerifyWithZKPResponse(
                valid=valid,
                message=message
            )
            
            # 设置验证详情
            if details:
                response.verification_details.update(details)
            
            return response
            
        except Exception as e:
            self.logger.error(f"零知识证明验证异常: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务内部错误: {str(e)}")
            return blockchain_pb2.VerifyWithZKPResponse(
                valid=False,
                message=f"服务内部错误: {str(e)}"
            )
    
    async def GetHealthDataRecords(self, 
                                  request: blockchain_pb2.GetHealthDataRecordsRequest, 
                                  context: grpc.aio.ServicerContext) -> blockchain_pb2.GetHealthDataRecordsResponse:
        """
        获取用户健康数据记录
        
        Args:
            request: 请求对象
            context: gRPC上下文
            
        Returns:
            健康数据记录响应
        """
        self.logger.info(f"接收到获取健康数据记录请求: 用户 {request.user_id}, 类型 {request.data_type if request.data_type else 'all'}")
        
        try:
            # 解析时间过滤
            start_time = datetime.datetime.fromtimestamp(request.start_time) if request.start_time else None
            end_time = datetime.datetime.fromtimestamp(request.end_time) if request.end_time else None
            
            # 调用区块链服务
            records, total_count = await self.blockchain_service.get_health_data_records(
                user_id=request.user_id,
                data_type=request.data_type if request.data_type else None,
                start_time=start_time,
                end_time=end_time,
                page=request.page,
                page_size=request.page_size
            )
            
            # 创建响应
            response = blockchain_pb2.GetHealthDataRecordsResponse(
                total_count=total_count,
                page=request.page,
                page_size=request.page_size
            )
            
            # 添加记录
            for record in records:
                pb_record = blockchain_pb2.HealthDataRecord(
                    transaction_id=record.transaction.transaction_id if record.transaction else "",
                    data_type=record.data_type.value,
                    data_hash=bytes.fromhex(record.data_hash),
                    timestamp=int(record.created_at.timestamp())
                )
                
                # 设置元数据
                if record.metadata:
                    pb_record.metadata.update(record.metadata)
                
                # 设置区块哈希
                if record.transaction and record.transaction.block_hash:
                    pb_record.block_hash = record.transaction.block_hash
                
                response.records.append(pb_record)
            
            return response
            
        except Exception as e:
            self.logger.error(f"获取健康数据记录异常: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务内部错误: {str(e)}")
            return blockchain_pb2.GetHealthDataRecordsResponse(
                total_count=0,
                page=request.page,
                page_size=request.page_size
            )
    
    async def AuthorizeAccess(self, 
                             request: blockchain_pb2.AuthorizeAccessRequest, 
                             context: grpc.aio.ServicerContext) -> blockchain_pb2.AuthorizeAccessResponse:
        """
        授权访问健康数据
        
        Args:
            request: 请求对象
            context: gRPC上下文
            
        Returns:
            授权访问响应
        """
        self.logger.info(f"接收到授权访问请求: 用户 {request.user_id}, 授权给 {request.authorized_id}")
        
        try:
            # 过期时间处理
            expiration_time = None
            if request.expiration_time:
                expiration_time = datetime.datetime.fromtimestamp(request.expiration_time)
            
            # 调用区块链服务
            success, message, authorization_id = await self.blockchain_service.authorize_access(
                user_id=request.user_id,
                authorized_id=request.authorized_id,
                data_types=list(request.data_types),
                expiration_time=expiration_time,
                access_policies=dict(request.access_policies) if request.access_policies else None
            )
            
            # 创建响应
            response = blockchain_pb2.AuthorizeAccessResponse(
                success=success,
                message=message
            )
            
            # 设置授权ID
            if success and authorization_id:
                response.authorization_id = authorization_id
            
            return response
            
        except Exception as e:
            self.logger.error(f"授权访问异常: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务内部错误: {str(e)}")
            return blockchain_pb2.AuthorizeAccessResponse(
                success=False,
                message=f"服务内部错误: {str(e)}"
            )
    
    async def RevokeAccess(self, 
                          request: blockchain_pb2.RevokeAccessRequest, 
                          context: grpc.aio.ServicerContext) -> blockchain_pb2.RevokeAccessResponse:
        """
        撤销访问授权
        
        Args:
            request: 请求对象
            context: gRPC上下文
            
        Returns:
            撤销访问响应
        """
        self.logger.info(f"接收到撤销访问请求: 用户 {request.user_id}, 授权ID {request.authorization_id}")
        
        try:
            # 调用区块链服务
            success, message = await self.blockchain_service.revoke_access(
                authorization_id=request.authorization_id,
                user_id=request.user_id,
                revocation_reason=request.revocation_reason if request.revocation_reason else None
            )
            
            # 创建响应
            response = blockchain_pb2.RevokeAccessResponse(
                success=success,
                message=message,
                revocation_timestamp=int(datetime.datetime.utcnow().timestamp())
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"撤销访问异常: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务内部错误: {str(e)}")
            return blockchain_pb2.RevokeAccessResponse(
                success=False,
                message=f"服务内部错误: {str(e)}"
            )
    
    async def GetBlockchainStatus(self, 
                                 request: blockchain_pb2.GetBlockchainStatusRequest, 
                                 context: grpc.aio.ServicerContext) -> blockchain_pb2.GetBlockchainStatusResponse:
        """
        获取区块链状态
        
        Args:
            request: 请求对象
            context: gRPC上下文
            
        Returns:
            区块链状态响应
        """
        self.logger.info("接收到获取区块链状态请求")
        
        try:
            # 调用区块链服务
            status, success = await self.blockchain_service.get_blockchain_status(
                include_node_info=request.include_node_info
            )
            
            # 创建响应
            response = blockchain_pb2.GetBlockchainStatusResponse(
                current_block_height=status.get("current_block_height", 0),
                connected_nodes=status.get("connected_nodes", 0),
                consensus_status=status.get("consensus_status", "unknown"),
                sync_percentage=status.get("sync_percentage", 0.0),
                last_block_timestamp=status.get("last_block_timestamp", 0)
            )
            
            # 如果包含节点信息
            if "node_info" in status:
                response.node_info.update(status["node_info"])
            
            return response
            
        except Exception as e:
            self.logger.error(f"获取区块链状态异常: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务内部错误: {str(e)}")
            return blockchain_pb2.GetBlockchainStatusResponse(
                current_block_height=0,
                connected_nodes=0,
                consensus_status="error",
                sync_percentage=0.0,
                last_block_timestamp=0
            ) 