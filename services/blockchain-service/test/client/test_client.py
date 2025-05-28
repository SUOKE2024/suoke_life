#!/usr/bin/env python3

"""
区块链服务测试客户端
"""

import argparse
import asyncio
from datetime import datetime, timedelta
import logging
import os
import sys
import time

import grpc

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 导入生成的gRPC代码
from api.grpc import blockchain_pb2, blockchain_pb2_grpc


async def test_store_health_data(stub):
    """测试存储健康数据"""
    print("\n=== 测试存储健康数据 ===")

    # 创建请求
    user_id = "test_user_123"
    data_type = "vital_signs"
    data_hash = b"0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    encrypted_data = b"Encrypted health data...this is just an example"

    metadata = {
        "device_id": "device_123",
        "timestamp": str(int(time.time())),
        "source": "health_app"
    }

    request = blockchain_pb2.StoreHealthDataRequest(
        user_id=user_id,
        data_type=data_type,
        data_hash=data_hash,
        encrypted_data=encrypted_data,
        metadata=metadata,
        timestamp=int(time.time())
    )

    # 调用服务
    response = await stub.StoreHealthData(request)

    # 打印结果
    print(f"存储结果: {'成功' if response.success else '失败'}")
    print(f"消息: {response.message}")
    if response.transaction_id:
        print(f"交易ID: {response.transaction_id}")
    if response.block_hash:
        print(f"区块哈希: {response.block_hash}")

    return response.transaction_id if response.success else None


async def test_verify_health_data(stub, transaction_id):
    """测试验证健康数据"""
    print("\n=== 测试验证健康数据 ===")

    if not transaction_id:
        print("错误: 没有有效的交易ID, 跳过验证测试")
        return False

    # 创建请求
    data_hash = b"0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"

    request = blockchain_pb2.VerifyHealthDataRequest(
        transaction_id=transaction_id,
        data_hash=data_hash
    )

    # 调用服务
    response = await stub.VerifyHealthData(request)

    # 打印结果
    print(f"验证结果: {'有效' if response.valid else '无效'}")
    print(f"消息: {response.message}")
    if response.verification_timestamp:
        verification_time = datetime.fromtimestamp(response.verification_timestamp)
        print(f"验证时间: {verification_time}")

    return response.valid


async def test_zkp_verification(stub):
    """测试零知识证明验证"""
    print("\n=== 测试零知识证明验证 ===")

    # 创建请求
    user_id = "test_user_123"
    verifier_id = "doctor_456"
    data_type = "vital_signs"

    # 模拟的零知识证明和公共输入
    # 实际应用中，这些将由专门的ZKP库生成
    proof = b"Sample ZKP proof data"
    public_inputs = b"Sample public inputs data"

    request = blockchain_pb2.VerifyWithZKPRequest(
        user_id=user_id,
        verifier_id=verifier_id,
        data_type=data_type,
        proof=proof,
        public_inputs=public_inputs
    )

    # 调用服务
    response = await stub.VerifyWithZKP(request)

    # 打印结果
    print(f"ZKP验证结果: {'有效' if response.valid else '无效'}")
    print(f"消息: {response.message}")

    # 打印验证详情
    if response.verification_details:
        print("验证详情:")
        for key, value in response.verification_details.items():
            print(f"  {key}: {value}")

    return response.valid


async def test_authorize_access(stub):
    """测试授权访问"""
    print("\n=== 测试授权访问 ===")

    # 创建请求
    user_id = "test_user_123"
    authorized_id = "doctor_456"
    data_types = ["vital_signs", "inquiry", "laboratory"]

    # 设置过期时间（当前时间加7天）
    expiration_time = int((datetime.now() + timedelta(days=7)).timestamp())

    # 设置访问策略
    access_policies = {
        "read_only": "true",
        "require_audit": "true",
        "allowed_purpose": "medical_diagnosis"
    }

    request = blockchain_pb2.AuthorizeAccessRequest(
        user_id=user_id,
        authorized_id=authorized_id,
        data_types=data_types,
        expiration_time=expiration_time,
        access_policies=access_policies
    )

    # 调用服务
    response = await stub.AuthorizeAccess(request)

    # 打印结果
    print(f"授权结果: {'成功' if response.success else '失败'}")
    print(f"消息: {response.message}")
    if response.authorization_id:
        print(f"授权ID: {response.authorization_id}")

    return response.authorization_id if response.success else None


async def test_revoke_access(stub, authorization_id):
    """测试撤销访问"""
    print("\n=== 测试撤销访问 ===")

    if not authorization_id:
        print("错误: 没有有效的授权ID, 跳过撤销测试")
        return False

    # 创建请求
    user_id = "test_user_123"
    revocation_reason = "No longer need this doctor to access my health data"

    request = blockchain_pb2.RevokeAccessRequest(
        authorization_id=authorization_id,
        user_id=user_id,
        revocation_reason=revocation_reason
    )

    # 调用服务
    response = await stub.RevokeAccess(request)

    # 打印结果
    print(f"撤销结果: {'成功' if response.success else '失败'}")
    print(f"消息: {response.message}")
    if response.revocation_timestamp:
        revocation_time = datetime.fromtimestamp(response.revocation_timestamp)
        print(f"撤销时间: {revocation_time}")

    return response.success


async def test_get_blockchain_status(stub):
    """测试获取区块链状态"""
    print("\n=== 测试获取区块链状态 ===")

    # 创建请求，包含节点信息
    request = blockchain_pb2.GetBlockchainStatusRequest(
        include_node_info=True
    )

    # 调用服务
    response = await stub.GetBlockchainStatus(request)

    # 打印结果
    print(f"当前区块高度: {response.current_block_height}")
    print(f"已连接节点数: {response.connected_nodes}")
    print(f"共识状态: {response.consensus_status}")
    print(f"同步百分比: {response.sync_percentage}%")

    if response.last_block_timestamp:
        last_block_time = datetime.fromtimestamp(response.last_block_timestamp)
        print(f"最新区块时间: {last_block_time}")

    # 打印节点信息
    if response.node_info:
        print("节点信息:")
        for key, value in response.node_info.items():
            print(f"  {key}: {value}")

    return True


async def run_tests(server_address):
    """运行测试套件"""
    print(f"连接到区块链服务: {server_address}")

    # 创建gRPC通道
    async with grpc.aio.insecure_channel(server_address) as channel:
        # 创建Stub
        stub = blockchain_pb2_grpc.BlockchainServiceStub(channel)

        try:
            # 存储健康数据并获取交易ID
            transaction_id = await test_store_health_data(stub)

            # 验证健康数据
            if transaction_id:
                await test_verify_health_data(stub, transaction_id)

            # 测试零知识证明验证
            await test_zkp_verification(stub)

            # 授权访问并获取授权ID
            authorization_id = await test_authorize_access(stub)

            # 撤销访问
            if authorization_id:
                await test_revoke_access(stub, authorization_id)

            # 获取区块链状态
            await test_get_blockchain_status(stub)

            print("\n所有测试完成!")

        except grpc.RpcError as e:
            print(f"gRPC错误: {e.code()}: {e.details()}")
        except Exception as e:
            print(f"测试过程中出现异常: {e!s}")


def main():
    """主函数"""
    # 设置命令行参数
    parser = argparse.ArgumentParser(description="区块链服务测试客户端")
    parser.add_argument("--server", type=str, default="localhost:50055",
                        help="服务器地址和端口 (默认: localhost:50055)")
    args = parser.parse_args()

    # 设置日志
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # 运行测试
    asyncio.run(run_tests(args.server))


if __name__ == "__main__":
    main()
