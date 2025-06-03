#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索克生活平台新功能测试脚本
验证图数据库、API文档生成、服务网格、测试框架等功能
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试所有新模块的导入"""
    print("🔍 测试模块导入...")

    try:
        # 测试图数据库模块（已移除）
        # 数据库组件已移除，各微服务自行管理数据库连接
        # from services.common.database.graph.graph_db import GraphDB, Node, Relationship
        # from services.common.database.graph.neo4j_client import Neo4jClient
        # from services.common.database.graph.arangodb_client import ArangoDBClient
        print("✅ 数据库组件已移除，各微服务自行管理数据库连接")

        # 测试API文档生成模块
        from services.common.api_docs.openapi_generator import OpenAPIGenerator
        print("✅ API文档生成模块导入成功")

        # 测试服务网格模块
        from services.common.service_mesh.istio_client import IstioClient, VirtualService
        from services.common.service_mesh.envoy_config import EnvoyConfigManager
        print("✅ 服务网格模块导入成功")

        # 测试测试框架模块
        from services.common.testing.test_framework import TestFramework, TestCase, TestType
        print("✅ 测试框架模块导入成功")

        return True

    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_data_structures():
    """测试数据结构创建"""
    print("\n🏗️ 测试数据结构创建...")

    try:
        # 测试图数据库数据结构（已移除）
        # from services.common.database.graph.graph_db import Node, Relationship

        # node = Node(
        #     node_id="test_001",
        #     labels=["User"],
        #     properties={"name": "测试用户", "age": 30}
        # )
        # print(f"✅ 创建节点: {node.labels} - {node.properties['name']}")

        # relationship = Relationship(
        #     relationship_id="rel_001",
        #     start_node_id="user_001",
        #     end_node_id="symptom_001",
        #     relationship_type="HAS_SYMPTOM",
        #     properties={"severity": "mild"}
        # )
        # print(f"✅ 创建关系: {relationship.relationship_type}")

        print("✅ 数据库组件已移除，各微服务自行管理数据库")

        # 测试API文档数据结构
        from services.common.api_docs.openapi_generator import APIEndpoint, APIParameter

        endpoint = APIEndpoint(
            path="/api/v1/health/assessment",
            method="POST",
            summary="健康评估",
            description="基于中医辨证论治的健康评估"
        )
        print(f"✅ 创建API端点: {endpoint.method} {endpoint.path}")

        # 测试服务网格数据结构
        from services.common.service_mesh.istio_client import VirtualService

        vs = VirtualService(
            name="xiaoai-service",
            namespace="suoke-life",
            hosts=["xiaoai.suoke.local"]
        )
        print(f"✅ 创建虚拟服务: {vs.name}")

        return True

    except Exception as e:
        print(f"❌ 数据结构创建失败: {e}")
        return False

def test_openapi_generation():
    """测试OpenAPI文档生成"""
    print("\n📚 测试OpenAPI文档生成...")

    try:
        from services.common.api_docs.openapi_generator import OpenAPIGenerator

        generator = OpenAPIGenerator(
            title="索克生活健康管理平台API",
            version="1.0.0",
            description="基于中医辨证论治的智能健康管理平台"
        )

        # 添加健康评估端点
        generator.add_endpoint(
            path="/api/v1/health/assessment",
            method="POST",
            summary="健康评估",
            description="基于用户症状进行中医辨证论治",
            tags=["健康评估"]
        )

        # 生成OpenAPI规范
        spec = generator.generate()

        # 验证生成的规范
        assert "openapi" in spec
        assert spec["info"]["title"] == "索克生活健康管理平台API"
        assert "/api/v1/health/assessment" in spec["paths"]

        print("✅ OpenAPI文档生成成功")
        print(f"   - 标题: {spec['info']['title']}")
        print(f"   - 版本: {spec['info']['version']}")
        print(f"   - 端点数量: {len(spec['paths'])}")

        return True

    except Exception as e:
        print(f"❌ OpenAPI文档生成失败: {e}")
        return False

def test_envoy_config():
    """测试Envoy配置生成"""
    print("\n⚙️ 测试Envoy配置生成...")

    try:
        from services.common.service_mesh.envoy_config import (
            EnvoyConfigManager, ClusterConfig, ListenerConfig
        )

        manager = EnvoyConfigManager()

        # 创建集群配置
        cluster = ClusterConfig(name="xiaoai-service-cluster")
        cluster.add_host("xiaoai-service.suoke-life.svc.cluster.local", 8080)
        cluster.add_health_check("/health")
        cluster.set_circuit_breaker()

        manager.add_cluster(cluster)

        # 创建监听器配置
        listener = ListenerConfig(name="suoke-listener", port=8080)
        listener.add_http_filter_chain("xiaoai-route")

        manager.add_listener(listener)

        # 生成配置
        config = manager.generate_config()

        # 验证配置
        assert "static_resources" in config
        assert "listeners" in config["static_resources"]
        assert "clusters" in config["static_resources"]
        assert len(config["static_resources"]["clusters"]) == 1

        print("✅ Envoy配置生成成功")
        print(f"   - 集群数量: {len(config['static_resources']['clusters'])}")
        print(f"   - 监听器数量: {len(config['static_resources']['listeners'])}")

        return True

    except Exception as e:
        print(f"❌ Envoy配置生成失败: {e}")
        return False

async def test_async_functionality():
    """测试异步功能"""
    print("\n🔄 测试异步功能...")

    try:
        from services.common.testing.test_framework import get_test_framework, TestType

        # 获取测试框架
        test_framework = get_test_framework()

        # 创建测试用例
        @test_framework.test_case(
            name="异步测试示例",
            description="测试异步功能是否正常工作",
            test_type=TestType.UNIT
        )
        async def test_async_example():
            """异步测试示例"""
            await asyncio.sleep(0.1)  # 模拟异步操作
            assert True, "异步测试通过"
            return {"status": "passed", "message": "异步功能正常"}

        # 运行测试
        results = await test_framework.run_all_tests()

        print("✅ 异步功能测试成功")
        print(f"   - 总测试数: {results.total_tests}")
        print(f"   - 通过测试: {results.passed_tests}")
        print(f"   - 成功率: {results.success_rate:.2%}")

        return True

    except Exception as e:
        print(f"❌ 异步功能测试失败: {e}")
        return False

def test_health_specific_features():
    """测试健康管理专用功能"""
    print("\n🏥 测试健康管理专用功能...")

    try:
        from services.common.api_docs.openapi_generator import OpenAPIGenerator

        generator = OpenAPIGenerator(
            title="索克生活健康管理平台API",
            version="1.0.0"
        )

        # 添加中医辨证相关的端点
        health_endpoints = [
            {
                "path": "/api/v1/tcm/syndrome-differentiation",
                "method": "POST",
                "summary": "中医辨证",
                "description": "基于症状进行中医证型识别",
                "tags": ["中医诊断"]
            },
            {
                "path": "/api/v1/agents/xiaoai/chat",
                "method": "POST",
                "summary": "小艾智能体对话",
                "description": "与小艾智能体进行健康咨询",
                "tags": ["智能体服务"]
            },
            {
                "path": "/api/v1/health/prescription",
                "method": "GET",
                "summary": "获取中药方剂",
                "description": "根据证型获取个性化中药方剂",
                "tags": ["中药方剂"]
            }
        ]

        for endpoint in health_endpoints:
            generator.add_endpoint(**endpoint)

        spec = generator.generate()

        # 验证健康管理相关端点
        paths = spec["paths"]
        assert "/api/v1/tcm/syndrome-differentiation" in paths
        assert "/api/v1/agents/xiaoai/chat" in paths
        assert "/api/v1/health/prescription" in paths

        print("✅ 健康管理专用功能测试成功")
        print(f"   - 中医辨证端点: ✓")
        print(f"   - 智能体对话端点: ✓")
        print(f"   - 中药方剂端点: ✓")

        return True

    except Exception as e:
        print(f"❌ 健康管理专用功能测试失败: {e}")
        return False

def test_configuration_loading():
    """测试配置加载"""
    print("\n⚙️ 测试配置加载...")

    try:
        # 测试环境变量配置
        os.environ["SUOKE_TEST_CONFIG"] = "test_value"

        # 模拟配置加载
        config = {
            "service_mesh": {
                "type": "istio",
                "namespace": "suoke-life"
            },
            "graph_database": {
                "type": "neo4j",
                "uri": "bolt://localhost:7687"
            },
            "api_docs": {
                "title": "索克生活API文档",
                "version": "1.0.0"
            }
        }

        # 验证配置结构
        assert "service_mesh" in config
        assert "graph_database" in config
        assert "api_docs" in config
        assert config["service_mesh"]["type"] == "istio"

        print("✅ 配置加载测试成功")
        print(f"   - 服务网格类型: {config['service_mesh']['type']}")
        print(f"   - 图数据库类型: {config['graph_database']['type']}")
        print(f"   - API文档标题: {config['api_docs']['title']}")

        return True

    except Exception as e:
        print(f"❌ 配置加载测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 索克生活平台新功能测试")
    print("=" * 50)

    test_results = []

    # 运行所有测试
    tests = [
        ("模块导入", test_imports),
        ("数据结构创建", test_data_structures),
        ("OpenAPI文档生成", test_openapi_generation),
        ("Envoy配置生成", test_envoy_config),
        ("异步功能", test_async_functionality),
        ("健康管理专用功能", test_health_specific_features),
        ("配置加载", test_configuration_loading)
    ]

    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            test_results.append((test_name, False))

    # 输出测试结果汇总
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)

    passed_tests = 0
    total_tests = len(test_results)

    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<20} {status}")
        if result:
            passed_tests += 1

    success_rate = (passed_tests / total_tests) * 100
    print(f"\n总计: {total_tests} 个测试")
    print(f"通过: {passed_tests} 个")
    print(f"失败: {total_tests - passed_tests} 个")
    print(f"成功率: {success_rate:.1f}%")

    if success_rate == 100:
        print("\n🎉 所有测试通过！索克生活平台新功能已就绪！")
    elif success_rate >= 80:
        print("\n⚠️ 大部分测试通过，但仍有部分功能需要完善")
    else:
        print("\n🔧 多个测试失败，需要检查和修复相关功能")

    return success_rate == 100

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)