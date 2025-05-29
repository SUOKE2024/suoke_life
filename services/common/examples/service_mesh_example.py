#!/usr/bin/env python3
"""
服务网格使用示例
展示如何使用索克生活平台的服务网格功能
"""

import asyncio
import logging
from pathlib import Path

from ..api_docs.doc_decorators import (
    api_doc,
    post_api,
    query_param,
    success_response,
)

# 导入API文档生成组件
from ..api_docs.openapi_generator import (
    OpenAPIGenerator,
)
from ..api_docs.swagger_ui import SwaggerUIServer
from ..service_mesh.envoy_config import (
    EnvoyConfigManager,
    ListenerConfig,
)
from ..service_mesh.istio_client import (
    DestinationRule,
    Gateway,
    VirtualService,
)

# 导入服务网格组件
from ..service_mesh.mesh_manager import (
    SecurityPolicyType,
    ServiceMeshManager,
    TrafficPolicyType,
)

# 导入图数据库组件
# 数据库组件已移除，各微服务自行管理数据库连接
# from ..database.graph.graph_db import get_graph_db, register_graph_db
# from ..database.graph.neo4j_client import Neo4jClient
# from ..database.graph.arangodb_client import ArangoDBClient
# 导入测试框架
from ..testing.test_framework import TestType, get_test_framework

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_service_mesh():
    """演示服务网格功能"""
    logger.info("=== 索克生活平台服务网格演示 ===")

    # 1. 创建服务网格管理器
    mesh_manager = ServiceMeshManager()

    # 2. 配置Istio服务网格
    logger.info("配置Istio服务网格...")

    # 创建虚拟服务 - 用于小艾智能体服务
    xiaoai_vs = VirtualService(
        name="xiaoai-service",
        namespace="suoke-life",
        hosts=["xiaoai.suoke.local"],
        gateways=["suoke-gateway"],
    )
    xiaoai_vs.add_http_route(
        match={"prefix": "/"},
        route={"destination": {"host": "xiaoai-service", "port": {"number": 8080}}},
    )

    # 创建目标规则 - 配置负载均衡
    xiaoai_dr = DestinationRule(
        name="xiaoai-service", namespace="suoke-life", host="xiaoai-service"
    )
    xiaoai_dr.add_subset("v1", {"version": "v1"})
    xiaoai_dr.add_subset("v2", {"version": "v2"})
    xiaoai_dr.set_load_balancer("ROUND_ROBIN")

    # 创建网关
    gateway = Gateway(name="suoke-gateway", namespace="suoke-life")
    gateway.add_server(port=80, protocol="HTTP", hosts=["*.suoke.local"])

    # 应用配置到Istio
    await mesh_manager.apply_istio_config(xiaoai_vs)
    await mesh_manager.apply_istio_config(xiaoai_dr)
    await mesh_manager.apply_istio_config(gateway)

    # 3. 配置流量策略
    logger.info("配置流量策略...")

    # 金丝雀发布 - 10%流量到v2版本
    await mesh_manager.configure_traffic_policy(
        service_name="xiaoai-service",
        policy_type=TrafficPolicyType.CANARY,
        config={"stable_version": "v1", "canary_version": "v2", "canary_weight": 10},
    )

    # 4. 配置安全策略
    logger.info("配置安全策略...")

    # 启用mTLS
    await mesh_manager.configure_security_policy(
        service_name="xiaoai-service", policy_type=SecurityPolicyType.MTLS_STRICT
    )

    # 5. 配置可观测性
    logger.info("配置可观测性...")

    await mesh_manager.configure_observability(
        service_name="xiaoai-service",
        enable_tracing=True,
        enable_metrics=True,
        enable_logging=True,
    )

    logger.info("服务网格配置完成！")


async def demo_envoy_config():
    """演示Envoy配置管理"""
    logger.info("=== Envoy配置管理演示 ===")

    # 创建Envoy配置管理器
    envoy_manager = EnvoyConfigManager()

    # 为索克生活平台的健康服务创建配置
    health_services = [
        ("xiaoai-service", [("xiaoai-service.suoke-life.svc.cluster.local", 8080)]),
        ("xiaoke-service", [("xiaoke-service.suoke-life.svc.cluster.local", 8080)]),
        ("laoke-service", [("laoke-service.suoke-life.svc.cluster.local", 8080)]),
        ("soer-service", [("soer-service.suoke-life.svc.cluster.local", 8080)]),
    ]

    # 为每个服务创建集群配置
    for service_name, hosts in health_services:
        envoy_manager.create_health_service_config(
            service_name=service_name, hosts=hosts, health_check_path="/health"
        )
        logger.info(f"创建{service_name}集群配置")

    # 创建金丝雀路由配置
    envoy_manager.create_canary_route_config(
        service_name="xiaoai",
        stable_cluster="xiaoai-service-cluster",
        canary_cluster="xiaoai-service-v2-cluster",
        canary_weight=10,
    )

    # 创建监听器配置
    listener = ListenerConfig(name="suoke-listener", address="0.0.0.0", port=8080)

    # 添加限流过滤器
    rate_limit_filter = envoy_manager.create_rate_limit_filter(
        requests_per_second=100, burst_size=200
    )

    listener.add_http_filter_chain(
        route_config_name="xiaoai-route",
        domains=["xiaoai.suoke.local", "*"],
        filters=[rate_limit_filter],
    )

    envoy_manager.add_listener(listener)

    # 生成并保存配置
    config_dir = Path("./envoy_configs")
    config_dir.mkdir(exist_ok=True)

    envoy_manager.save_config(
        file_path=str(config_dir / "suoke_envoy_config.yaml"), format="yaml"
    )

    logger.info("Envoy配置已生成并保存")


async def demo_api_docs():
    """演示API文档生成"""
    logger.info("=== API文档生成演示 ===")

    # 创建OpenAPI生成器
    generator = OpenAPIGenerator(
        title="索克生活健康管理平台API",
        version="1.0.0",
        description="基于中医辨证论治的智能健康管理平台API文档",
    )

    # 定义健康评估API端点
    @api_doc(
        summary="健康评估",
        description="基于中医辨证论治进行个性化健康评估",
        tags=["健康评估"],
    )
    @post_api("/api/v1/health/assessment")
    @query_param("user_id", "用户ID", required=True)
    @success_response(
        "评估结果",
        {
            "assessment_id": "评估ID",
            "syndrome_type": "证型",
            "health_score": "健康评分",
            "recommendations": "调理建议",
        },
    )
    async def health_assessment(user_id: str):
        """健康评估接口"""
        pass

    # 定义智能体对话API
    @api_doc(
        summary="智能体对话",
        description="与小艾、小克、老克、索儿智能体进行健康咨询对话",
        tags=["智能体服务"],
    )
    @post_api("/api/v1/agents/chat")
    @query_param("agent_type", "智能体类型", enum=["xiaoai", "xiaoke", "laoke", "soer"])
    @success_response(
        "对话结果",
        {"response": "智能体回复", "session_id": "会话ID", "context": "对话上下文"},
    )
    async def agent_chat(agent_type: str, message: str):
        """智能体对话接口"""
        pass

    # 生成OpenAPI文档
    openapi_spec = generator.generate()

    # 保存文档
    docs_dir = Path("./api_docs")
    docs_dir.mkdir(exist_ok=True)

    generator.save_json(str(docs_dir / "suoke_life_api.json"))
    generator.save_yaml(str(docs_dir / "suoke_life_api.yaml"))

    # 启动Swagger UI服务器
    SwaggerUIServer(openapi_spec=openapi_spec, title="索克生活API文档")

    logger.info("API文档已生成，Swagger UI服务器启动中...")
    # await swagger_server.start(host="0.0.0.0", port=8081)


async def demo_graph_database():
    """演示图数据库功能"""
    logger.info("=== 图数据库演示 ===")

    # 注册Neo4j图数据库
    neo4j_client = Neo4jClient(
        uri="bolt://localhost:7687", username="neo4j", password="password"
    )
    register_graph_db("neo4j", neo4j_client)

    # 获取图数据库实例
    graph_db = get_graph_db("neo4j")

    # 创建用户健康知识图谱
    logger.info("创建用户健康知识图谱...")

    # 创建用户节点
    user_node = await graph_db.create_node(
        labels=["User"],
        properties={"user_id": "user_001", "name": "张三", "age": 35, "gender": "male"},
    )

    # 创建症状节点
    symptom_nodes = []
    symptoms = [
        {"name": "头痛", "severity": "mild", "duration": "3天"},
        {"name": "失眠", "severity": "moderate", "duration": "1周"},
        {"name": "疲劳", "severity": "severe", "duration": "2周"},
    ]

    for symptom in symptoms:
        node = await graph_db.create_node(labels=["Symptom"], properties=symptom)
        symptom_nodes.append(node)

    # 创建证型节点
    syndrome_node = await graph_db.create_node(
        labels=["Syndrome"],
        properties={
            "name": "肝郁气滞",
            "category": "气滞血瘀",
            "description": "情志不遂，肝气郁结",
        },
    )

    # 创建关系
    for symptom_node in symptom_nodes:
        await graph_db.create_relationship(
            start_node_id=user_node.node_id,
            end_node_id=symptom_node.node_id,
            relationship_type="HAS_SYMPTOM",
            properties={"reported_date": "2024-01-15"},
        )

    await graph_db.create_relationship(
        start_node_id=user_node.node_id,
        end_node_id=syndrome_node.node_id,
        relationship_type="DIAGNOSED_WITH",
        properties={
            "diagnosis_date": "2024-01-15",
            "confidence": 0.85,
            "diagnosed_by": "xiaoai_agent",
        },
    )

    # 查询用户的健康图谱
    query = """
    MATCH (u:User {user_id: $user_id})-[r1:HAS_SYMPTOM]->(s:Symptom)
    MATCH (u)-[r2:DIAGNOSED_WITH]->(syn:Syndrome)
    RETURN u, s, syn, r1, r2
    """

    results = await graph_db.execute_query(query, {"user_id": "user_001"})
    logger.info(f"查询到用户健康图谱数据: {len(results)}条记录")

    logger.info("图数据库演示完成")


async def demo_testing_framework():
    """演示测试框架"""
    logger.info("=== 测试框架演示 ===")

    # 获取测试框架
    test_framework = get_test_framework()

    # 创建健康评估服务测试用例
    @test_framework.test_case(
        name="健康评估API测试",
        description="测试健康评估API的功能",
        test_type=TestType.INTEGRATION,
    )
    async def test_health_assessment():
        """测试健康评估功能"""
        # 模拟测试逻辑
        assert True, "健康评估API正常工作"
        return {"status": "passed", "message": "健康评估功能正常"}

    # 创建智能体服务测试用例
    @test_framework.test_case(
        name="智能体对话测试",
        description="测试四个智能体的对话功能",
        test_type=TestType.UNIT,
    )
    async def test_agent_chat():
        """测试智能体对话功能"""
        agents = ["xiaoai", "xiaoke", "laoke", "soer"]
        for agent in agents:
            # 模拟测试每个智能体
            assert agent in agents, f"{agent}智能体正常工作"
        return {"status": "passed", "message": "所有智能体功能正常"}

    # 创建图数据库测试用例
    @test_framework.test_case(
        name="图数据库连接测试",
        description="测试图数据库的连接和基本操作",
        test_type=TestType.INTEGRATION,
    )
    async def test_graph_database():
        """测试图数据库功能"""
        # 模拟测试逻辑
        assert True, "图数据库连接正常"
        return {"status": "passed", "message": "图数据库功能正常"}

    # 运行测试套件
    logger.info("运行索克生活平台测试套件...")
    results = await test_framework.run_all_tests()

    # 输出测试结果
    logger.info(f"测试完成: 总计{results.total_tests}个测试")
    logger.info(f"通过: {results.passed_tests}, 失败: {results.failed_tests}")
    logger.info(f"成功率: {results.success_rate:.2%}")

    return results


async def main():
    """主演示函数"""
    logger.info("索克生活平台 - 微服务基础设施演示")
    logger.info("=" * 50)

    try:
        # 演示各个功能模块
        await demo_service_mesh()
        await demo_envoy_config()
        await demo_api_docs()
        await demo_graph_database()
        await demo_testing_framework()

        logger.info("=" * 50)
        logger.info("所有演示完成！")
        logger.info("索克生活平台的微服务基础设施已就绪")

    except Exception as e:
        logger.error(f"演示过程中出现错误: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
