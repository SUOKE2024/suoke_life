#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
区块链服务集成测试

测试区块链服务与其他服务之间的交互，包括：
- 与用户服务的集成
- 与健康数据服务的集成
- 与消息总线的集成
- 与ZKP验证服务的集成
"""

import asyncio
import os
import sys
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import grpc
import jwt
import pytest
import yaml

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api.grpc import blockchain_pb2, blockchain_pb2_grpc
from internal.model.config import load_config
from internal.model.entities import DataType, AccessLevel

# 测试配置
TEST_CONFIG = {
    "blockchain_service": {
        "host": "localhost",
        "port": 50055,
        "timeout": 10
    },
    "user_service": {
        "host": "localhost",
        "port": 50051,
        "timeout": 5
    },
    "message_bus": {
        "host": "localhost",
        "port": 5672,
        "user": "guest",
        "password": "guest",
        "exchange": "suokelife.events"
    },
    "health_data_service": {
        "host": "localhost",
        "port": 50053,
        "timeout": 5
    }
}

# 测试用户数据
TEST_USER_ID = "test_user_12345"
TEST_DOCTOR_ID = "test_doctor_67890"
TEST_ADMIN_ID = "test_admin_98765"


# 测试夹具：区块链服务gRPC客户端
@pytest.fixture
async def blockchain_client():
    """创建区块链服务的gRPC客户端"""
    service_config = TEST_CONFIG["blockchain_service"]
    channel = grpc.aio.insecure_channel(f"{service_config['host']}:{service_config['port']}")
    client = blockchain_pb2_grpc.BlockchainServiceStub(channel)
    try:
        yield client
    finally:
        await channel.close()


# 测试夹具：认证令牌
@pytest.fixture
def auth_token():
    """创建用于测试的JWT认证令牌"""
    # 示例认证令牌生成（实际项目中应使用正确的密钥和算法）
    payload = {
        "sub": TEST_USER_ID,
        "name": "测试用户",
        "roles": ["user"],
        "exp": int((datetime.now() + timedelta(hours=1)).timestamp())
    }
    token = jwt.encode(payload, "test_secret_key", algorithm="HS256")
    return token


# 测试夹具：测试数据
@pytest.fixture
def test_health_data():
    """提供用于测试的健康数据"""
    data = {
        "vital_signs": {
            "heart_rate": 75,
            "blood_pressure": "120/80",
            "temperature": 36.5,
            "respiratory_rate": 16,
            "blood_oxygen": 98,
            "timestamp": int(time.time())
        },
        "medication": {
            "name": "测试药物",
            "dosage": "10mg",
            "frequency": "每日一次",
            "start_date": int(time.time()),
            "end_date": int((datetime.now() + timedelta(days=7)).timestamp())
        },
        "syndrome": {
            "main_syndrome": "气虚",
            "secondary_syndrome": "血瘀",
            "syndrome_description": "面色萎黄，气短乏力，舌淡苔白",
            "assessment_date": int(time.time())
        }
    }
    return data


# 辅助函数：计算数据哈希
def calculate_data_hash(data: Dict) -> bytes:
    """计算数据哈希值"""
    import hashlib
    import json
    
    # 确保数据序列化结果一致
    serialized_data = json.dumps(data, sort_keys=True, ensure_ascii=False)
    data_hash = hashlib.sha256(serialized_data.encode('utf-8')).digest()
    return data_hash


# 测试存储健康数据
@pytest.mark.asyncio
async def test_store_health_data(blockchain_client, auth_token, test_health_data):
    """测试存储健康数据到区块链"""
    vital_signs_data = test_health_data["vital_signs"]
    data_hash = calculate_data_hash(vital_signs_data)
    
    # 创建请求
    request = blockchain_pb2.StoreHealthDataRequest(
        user_id=TEST_USER_ID,
        data_type="vital_signs",
        data_hash=data_hash,
        metadata={
            "source": "integration_test",
            "device": "test_device"
        },
        timestamp=int(time.time())
    )
    
    # 调用API
    response = await blockchain_client.StoreHealthData(
        request=request,
        metadata=[("authorization", f"Bearer {auth_token}")]
    )
    
    # 验证响应
    assert response.success, f"存储健康数据失败: {response.message}"
    assert response.transaction_id, "未返回交易ID"
    assert response.block_hash, "未返回区块哈希"
    
    print(f"交易ID: {response.transaction_id}")
    print(f"区块哈希: {response.block_hash}")
    
    return response.transaction_id


# 测试验证健康数据
@pytest.mark.asyncio
async def test_verify_health_data(blockchain_client, auth_token, test_health_data):
    """测试验证已存储的健康数据"""
    # 先存储数据
    transaction_id = await test_store_health_data(blockchain_client, auth_token, test_health_data)
    
    # 计算相同的数据哈希
    vital_signs_data = test_health_data["vital_signs"]
    data_hash = calculate_data_hash(vital_signs_data)
    
    # 创建验证请求
    request = blockchain_pb2.VerifyHealthDataRequest(
        transaction_id=transaction_id,
        data_hash=data_hash
    )
    
    # 调用API
    response = await blockchain_client.VerifyHealthData(
        request=request,
        metadata=[("authorization", f"Bearer {auth_token}")]
    )
    
    # 验证响应
    assert response.valid, f"验证健康数据失败: {response.message}"
    assert response.verification_timestamp > 0, "未返回验证时间戳"
    
    print(f"验证结果: {response.valid}")
    print(f"验证时间: {datetime.fromtimestamp(response.verification_timestamp)}")
    
    # 使用不正确的数据哈希验证
    wrong_data = test_health_data["vital_signs"].copy()
    wrong_data["heart_rate"] = 80  # 修改数据
    wrong_hash = calculate_data_hash(wrong_data)
    
    # 创建验证请求
    wrong_request = blockchain_pb2.VerifyHealthDataRequest(
        transaction_id=transaction_id,
        data_hash=wrong_hash
    )
    
    # 调用API
    wrong_response = await blockchain_client.VerifyHealthData(
        request=wrong_request,
        metadata=[("authorization", f"Bearer {auth_token}")]
    )
    
    # 不正确的哈希应该验证失败
    assert not wrong_response.valid, "使用错误的数据哈希验证应该失败"


# 测试零知识证明验证
@pytest.mark.asyncio
async def test_verify_with_zkp(blockchain_client, auth_token):
    """测试使用零知识证明验证健康数据的特定属性"""
    # 模拟零知识证明数据（实际中这些将由专门的ZKP服务生成）
    zkp_data = {
        "proof": b"\x01\x02\x03\x04" * 32,  # 模拟128字节的证明
        "public_inputs": b"\x05\x06\x07\x08" * 8,  # 模拟32字节的公共输入
        "verifier_type": 5  # VITAL_SIGNS 验证器
    }
    
    # 创建ZKP验证请求
    request = blockchain_pb2.VerifyWithZKPRequest(
        user_id=TEST_USER_ID,
        verifier_id=TEST_DOCTOR_ID,
        data_type="vital_signs",
        proof=zkp_data["proof"],
        public_inputs=zkp_data["public_inputs"]
    )
    
    # 调用API
    response = await blockchain_client.VerifyWithZKP(
        request=request,
        metadata=[("authorization", f"Bearer {auth_token}")]
    )
    
    # 验证响应
    # 注意：这个测试可能成功或失败，取决于模拟的验证逻辑
    print(f"ZKP验证结果: {response.valid}")
    print(f"ZKP验证消息: {response.message}")
    print(f"ZKP验证详情: {response.verification_details}")


# 测试授权和撤销访问
@pytest.mark.asyncio
async def test_authorize_and_revoke_access(blockchain_client, auth_token):
    """测试授权和撤销健康数据访问权限"""
    # 创建授权请求
    auth_request = blockchain_pb2.AuthorizeAccessRequest(
        user_id=TEST_USER_ID,
        authorized_id=TEST_DOCTOR_ID,
        data_types=["vital_signs", "medication"],
        expiration_time=int((datetime.now() + timedelta(days=30)).timestamp()),
        access_policies={
            "read_only": "true",
            "purpose": "medical_diagnosis",
            "audit_required": "true"
        }
    )
    
    # 授权访问
    auth_response = await blockchain_client.AuthorizeAccess(
        request=auth_request,
        metadata=[("authorization", f"Bearer {auth_token}")]
    )
    
    # 验证授权响应
    assert auth_response.success, f"授权访问失败: {auth_response.message}"
    assert auth_response.authorization_id, "未返回授权ID"
    
    authorization_id = auth_response.authorization_id
    print(f"授权ID: {authorization_id}")
    
    # 等待一会儿
    await asyncio.sleep(2)
    
    # 撤销请求
    revoke_request = blockchain_pb2.RevokeAccessRequest(
        authorization_id=authorization_id,
        user_id=TEST_USER_ID,
        revocation_reason="测试撤销授权"
    )
    
    # 撤销访问
    revoke_response = await blockchain_client.RevokeAccess(
        request=revoke_request,
        metadata=[("authorization", f"Bearer {auth_token}")]
    )
    
    # 验证撤销响应
    assert revoke_response.success, f"撤销访问失败: {revoke_response.message}"
    assert revoke_response.revocation_timestamp > 0, "未返回撤销时间戳"
    
    print(f"撤销时间: {datetime.fromtimestamp(revoke_response.revocation_timestamp)}")


# 测试获取健康数据记录
@pytest.mark.asyncio
async def test_get_health_data_records(blockchain_client, auth_token, test_health_data):
    """测试获取用户的健康数据记录"""
    # 先存储一些健康数据
    await test_store_health_data(blockchain_client, auth_token, test_health_data)
    
    # 创建获取记录请求
    request = blockchain_pb2.GetHealthDataRecordsRequest(
        user_id=TEST_USER_ID,
        data_type="vital_signs",  # 可选过滤
        page=1,
        page_size=10
    )
    
    # 调用API
    response = await blockchain_client.GetHealthDataRecords(
        request=request,
        metadata=[("authorization", f"Bearer {auth_token}")]
    )
    
    # 验证响应
    assert response.total_count >= 0, "未返回总记录数"
    print(f"总记录数: {response.total_count}")
    print(f"当前页码: {response.page}")
    print(f"每页大小: {response.page_size}")
    
    # 打印记录详情
    for i, record in enumerate(response.records):
        print(f"记录 {i+1}:")
        print(f"  交易ID: {record.transaction_id}")
        print(f"  数据类型: {record.data_type}")
        print(f"  时间戳: {datetime.fromtimestamp(record.timestamp)}")
        print(f"  元数据: {record.metadata}")


# 测试获取区块链状态
@pytest.mark.asyncio
async def test_get_blockchain_status(blockchain_client, auth_token):
    """测试获取区块链网络和节点的状态信息"""
    # 创建请求
    request = blockchain_pb2.GetBlockchainStatusRequest(
        include_node_info=True
    )
    
    # 调用API
    response = await blockchain_client.GetBlockchainStatus(
        request=request,
        metadata=[("authorization", f"Bearer {auth_token}")]
    )
    
    # 验证响应
    assert response.current_block_height > 0, "未返回当前区块高度"
    assert response.consensus_status, "未返回共识状态"
    
    print(f"当前区块高度: {response.current_block_height}")
    print(f"连接节点数量: {response.connected_nodes}")
    print(f"共识状态: {response.consensus_status}")
    print(f"同步百分比: {response.sync_percentage}%")
    print(f"最新区块时间: {datetime.fromtimestamp(response.last_block_timestamp)}")
    
    # 如果包含节点信息
    if response.node_info:
        print("节点信息:")
        for key, value in response.node_info.items():
            print(f"  {key}: {value}")


# 集成测试：完整健康数据生命周期
@pytest.mark.asyncio
async def test_health_data_lifecycle(blockchain_client, auth_token, test_health_data):
    """测试健康数据在区块链上的完整生命周期"""
    # 1. 存储数据
    print("\n步骤1: 存储健康数据")
    vital_signs_data = test_health_data["vital_signs"]
    data_hash = calculate_data_hash(vital_signs_data)
    
    store_request = blockchain_pb2.StoreHealthDataRequest(
        user_id=TEST_USER_ID,
        data_type="vital_signs",
        data_hash=data_hash,
        metadata={"lifecycle_test": "true"},
        timestamp=int(time.time())
    )
    
    store_response = await blockchain_client.StoreHealthData(
        request=store_request,
        metadata=[("authorization", f"Bearer {auth_token}")]
    )
    assert store_response.success, "存储数据失败"
    transaction_id = store_response.transaction_id
    print(f"交易ID: {transaction_id}")
    
    # 2. 授权医生访问
    print("\n步骤2: 授权医生访问数据")
    auth_request = blockchain_pb2.AuthorizeAccessRequest(
        user_id=TEST_USER_ID,
        authorized_id=TEST_DOCTOR_ID,
        data_types=["vital_signs"],
        expiration_time=int((datetime.now() + timedelta(days=7)).timestamp()),
        access_policies={"purpose": "health_consultation"}
    )
    
    auth_response = await blockchain_client.AuthorizeAccess(
        request=auth_request,
        metadata=[("authorization", f"Bearer {auth_token}")]
    )
    assert auth_response.success, "授权访问失败"
    authorization_id = auth_response.authorization_id
    print(f"授权ID: {authorization_id}")
    
    # 3. 医生验证数据
    print("\n步骤3: 医生验证数据")
    verify_request = blockchain_pb2.VerifyHealthDataRequest(
        transaction_id=transaction_id,
        data_hash=data_hash
    )
    
    # 使用医生的令牌
    doctor_token = jwt.encode({
        "sub": TEST_DOCTOR_ID,
        "name": "测试医生",
        "roles": ["doctor"],
        "exp": int((datetime.now() + timedelta(hours=1)).timestamp())
    }, "test_secret_key", algorithm="HS256")
    
    verify_response = await blockchain_client.VerifyHealthData(
        request=verify_request,
        metadata=[("authorization", f"Bearer {doctor_token}")]
    )
    assert verify_response.valid, "医生验证数据失败"
    print(f"验证结果: {verify_response.valid}")
    
    # 4. 使用零知识证明验证特定属性
    print("\n步骤4: 使用零知识证明验证特定属性")
    zkp_request = blockchain_pb2.VerifyWithZKPRequest(
        user_id=TEST_USER_ID,
        verifier_id=TEST_DOCTOR_ID,
        data_type="vital_signs",
        proof=b"\x01\x02\x03\x04" * 32,
        public_inputs=b"\x05\x06\x07\x08" * 8
    )
    
    zkp_response = await blockchain_client.VerifyWithZKP(
        request=zkp_request,
        metadata=[("authorization", f"Bearer {doctor_token}")]
    )
    print(f"ZKP验证结果: {zkp_response.valid}")
    print(f"ZKP验证详情: {zkp_response.verification_details}")
    
    # 5. 撤销访问权限
    print("\n步骤5: 撤销访问权限")
    revoke_request = blockchain_pb2.RevokeAccessRequest(
        authorization_id=authorization_id,
        user_id=TEST_USER_ID,
        revocation_reason="测试完成后撤销"
    )
    
    revoke_response = await blockchain_client.RevokeAccess(
        request=revoke_request,
        metadata=[("authorization", f"Bearer {auth_token}")]
    )
    assert revoke_response.success, "撤销访问失败"
    print(f"撤销结果: {revoke_response.success}")
    
    # 6. 医生尝试再次验证数据（应该失败，因为已撤销权限）
    print("\n步骤6: 撤销权限后医生尝试验证数据")
    try:
        verify_response_after_revoke = await blockchain_client.VerifyHealthData(
            request=verify_request,
            metadata=[("authorization", f"Bearer {doctor_token}")]
        )
        print(f"验证结果: {verify_response_after_revoke.valid}")
        print(f"验证消息: {verify_response_after_revoke.message}")
    except grpc.RpcError as e:
        print(f"预期的权限错误: {e.details()}")
    
    print("\n健康数据生命周期测试完成")


# 测试与消息总线的集成
@pytest.mark.asyncio
async def test_message_bus_integration(blockchain_client, auth_token, test_health_data):
    """测试区块链服务与消息总线的集成"""
    # 此测试依赖于消息总线服务的运行
    # 实际测试中需要配置正确的消息总线连接
    
    print("测试区块链服务与消息总线的集成")
    
    # 存储数据以触发事件
    vital_signs_data = test_health_data["vital_signs"]
    data_hash = calculate_data_hash(vital_signs_data)
    
    store_request = blockchain_pb2.StoreHealthDataRequest(
        user_id=TEST_USER_ID,
        data_type="vital_signs",
        data_hash=data_hash,
        metadata={"event_test": "true"},
        timestamp=int(time.time())
    )
    
    store_response = await blockchain_client.StoreHealthData(
        request=store_request,
        metadata=[("authorization", f"Bearer {auth_token}")]
    )
    
    assert store_response.success, "存储数据失败"
    print(f"交易ID: {store_response.transaction_id}")
    print("区块链事件应已发布到消息总线")
    
    # 备注：在实际测试中，应该使用消息总线客户端订阅相关事件并验证是否收到


# 执行所有测试脚本
if __name__ == "__main__":
    print("运行区块链服务集成测试...")
    # 使用pytest运行测试
    pytest.main(["-xvs", __file__]) 