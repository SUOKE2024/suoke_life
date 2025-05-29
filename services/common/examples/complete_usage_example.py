"""
索克生活平台通用组件完整使用示例
展示如何使用所有通用组件构建微服务
"""

import asyncio
import json
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """主函数 - 演示所有组件的使用"""

    # 1. 初始化通用组件
    logger.info("🚀 开始初始化索克生活平台通用组件...")

    # 组件配置
    config = {
        "config": {
            "sources": [
                {"name": "main_config", "type": "file", "path": "./config/main.yaml"}
            ]
        },
        "security": {
            "encryption": {"algorithm": "fernet", "key_rotation_hours": 24},
            "auth": {"jwt_secret": "your-secret-key", "token_expiry_hours": 24},
        },
        "database": {
            "engine": {
                "postgresql": {
                    "url": "postgresql://localhost:5432/suoke_life",
                    "pool_size": 10,
                },
                "redis": {"host": "localhost", "port": 6379, "db": 0},
            },
            "graph": {
                "neo4j": {
                    "uri": "bolt://localhost:7687",
                    "user": "neo4j",
                    "password": "password",
                }
            },
            # 'timeseries': {  # 数据库组件已移除
            #     'influxdb': {
            #         'url': 'http://localhost:8086',
            #         'token': 'your-token',
            #         'org': 'suoke-life',
            #         'bucket': 'health-data'
            #     }
            # }
        },
        "messaging": {
            "kafka": {
                "bootstrap_servers": ["localhost:9092"],
                "topics": ["health-events", "user-actions"],
            },
            "rabbitmq": {"url": "amqp://localhost:5672", "exchange": "suoke-exchange"},
        },
        "governance": {
            "circuit_breaker": {"failure_threshold": 5, "recovery_timeout": 60},
            "rate_limiter": {"default_limit": 1000, "window_size": 60},
        },
        "observability": {
            "metrics": {"prometheus_port": 9090},
            "tracing": {"jaeger_endpoint": "http://localhost:14268/api/traces"},
        },
        "performance": {
            "cache": {"redis_url": "redis://localhost:6379/1", "default_ttl": 300}
        },
        "service_registry": {"consul": {"host": "localhost", "port": 8500}},
        "load_balancer": {
            "default_strategy": "round_robin",
            "endpoints": {
                "xiaoai-service": {
                    "endpoints": [
                        {"host": "localhost", "port": 8001, "weight": 1},
                        {"host": "localhost", "port": 8002, "weight": 2},
                    ]
                },
                "xiaoke-service": {
                    "endpoints": [
                        {"host": "localhost", "port": 8003, "weight": 1},
                        {"host": "localhost", "port": 8004, "weight": 1},
                    ]
                },
            },
        },
        "health": {
            "thresholds": {"cpu_percent": 80, "memory_percent": 85, "disk_percent": 90},
            "database": {
                "postgresql": {
                    "url": "postgresql://localhost:5432/suoke_life",
                    "timeout": 5,
                },
                "redis": {"host": "localhost", "port": 6379, "timeout": 5},
            },
            "services": {
                "xiaoai-service": {
                    "url": "http://localhost:8001/health",
                    "timeout": 10,
                },
                "xiaoke-service": {
                    "url": "http://localhost:8003/health",
                    "timeout": 10,
                },
            },
        },
    }

    try:
        # 导入并初始化组件管理器
        from services.common import get_components

        components = await get_components(config)
        logger.info("✅ 通用组件初始化成功")

        # 2. 演示安全组件使用
        logger.info("🔒 演示安全组件...")

        security = components.get_component("security")

        # 加密数据
        encryption = security["encryption"]
        sensitive_data = "用户健康数据：血压140/90，心率75"
        encrypted_data = await encryption.encrypt(sensitive_data)
        decrypted_data = await encryption.decrypt(encrypted_data)
        logger.info(f"加密解密测试: {decrypted_data == sensitive_data}")

        # JWT认证
        auth = security["auth"]
        user_data = {"user_id": "user_001", "role": "patient"}
        token = await auth.create_token(user_data)
        verified_data = await auth.verify_token(token)
        logger.info(f"JWT认证测试: {verified_data['user_id'] == 'user_001'}")

        # 3. 数据库组件已移除，各微服务自行管理
        logger.info("💾 数据库组件已移除，各微服务自行管理数据库连接...")

        # database = components.get_component('database')  # 已移除

        # 图数据库操作（已移除）
        # graph_db = database['graph']
        # user_node = await graph_db.create_node(
        #     labels=['User'],
        #     properties={'user_id': 'user_001', 'name': '张三', 'age': 35}
        # )
        # logger.info(f"创建用户节点: {user_node}")

        # 时序数据库操作（已移除）
        # timeseries_db = database['timeseries']
        health_data = {
            "measurement": "vital_signs",
            "tags": {"user_id": "user_001", "device": "smartwatch"},
            "fields": {
                "heart_rate": 75,
                "blood_pressure_sys": 120,
                "blood_pressure_dia": 80,
            },
            "timestamp": asyncio.get_event_loop().time(),
        }
        # await timeseries_db.write_point(health_data)  # 已移除
        logger.info("数据库组件已移除，各微服务自行管理数据库连接")

        # 4. 演示消息组件使用
        logger.info("📨 演示消息组件...")

        messaging = components.get_component("messaging")

        # Kafka消息发送
        kafka = messaging["kafka"]
        health_event = {
            "event_type": "vital_signs_updated",
            "user_id": "user_001",
            "data": health_data,
            "timestamp": asyncio.get_event_loop().time(),
        }
        await kafka.send_message("health-events", health_event)
        logger.info("发送健康事件到Kafka")

        # 5. 演示服务治理组件
        logger.info("⚖️ 演示服务治理组件...")

        governance = components.get_component("governance")

        # 断路器测试
        circuit_breaker = governance["circuit_breaker"]

        async def test_service_call():
            """模拟服务调用"""
            # 这里可以是实际的服务调用
            return "服务调用成功"

        result = await circuit_breaker.call("test-service", test_service_call)
        logger.info(f"断路器保护的服务调用: {result}")

        # 限流器测试
        rate_limiter = governance["rate_limiter"]
        allowed = await rate_limiter.is_allowed("user_001", "api_call")
        logger.info(f"限流检查结果: {allowed}")

        # 6. 演示可观测性组件
        logger.info("📊 演示可观测性组件...")

        observability = components.get_component("observability")

        # 指标收集
        metrics = observability["metrics"]
        await metrics.increment_counter("api_requests_total", {"endpoint": "/health"})
        await metrics.record_histogram(
            "request_duration_seconds", 0.123, {"endpoint": "/health"}
        )
        logger.info("记录API请求指标")

        # 分布式追踪
        tracing = observability["tracing"]
        with await tracing.start_span("health_assessment") as span:
            span.set_attribute("user_id", "user_001")
            span.set_attribute("assessment_type", "tcm_constitution")
            # 模拟健康评估处理
            await asyncio.sleep(0.1)
            span.set_status("OK")
        logger.info("创建分布式追踪span")

        # 7. 演示负载均衡组件
        logger.info("⚖️ 演示负载均衡组件...")

        # 获取负载均衡器
        from services.common.load_balancer import LoadBalancer, LoadBalancingStrategy

        load_balancer = LoadBalancer()
        await load_balancer.initialize(config["load_balancer"])

        # 选择服务端点
        endpoint = await load_balancer.select_endpoint(
            "xiaoai-service",
            LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN,
            {"client_ip": "192.168.1.100"},
        )

        if endpoint:
            logger.info(f"选择的服务端点: {endpoint.address}")

            # 模拟请求处理
            await asyncio.sleep(0.1)
            endpoint.record_success(0.1)

            # 释放端点
            await load_balancer.release_endpoint(endpoint)

        # 获取负载均衡统计
        stats = await load_balancer.get_all_stats()
        logger.info(f"负载均衡统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")

        # 8. 演示健康检查组件
        logger.info("🏥 演示健康检查组件...")

        from services.common.health import HealthChecker

        health_checker = HealthChecker()
        await health_checker.initialize(config["health"])

        # 执行健康检查
        health_result = await health_checker.health_check()
        logger.info(f"系统健康状态: {health_result['status']}")
        logger.info(
            f"健康检查详情: {json.dumps(health_result, indent=2, ensure_ascii=False)}"
        )

        # 9. 演示API文档生成
        logger.info("📚 演示API文档生成...")

        api_docs = components.get_component("api_docs")
        openapi_gen = api_docs["openapi"]

        # 生成API文档
        await openapi_gen.generate_spec(
            {
                "title": "索克生活健康管理平台API",
                "version": "1.0.0",
                "description": "基于中医辨证论治的智能健康管理平台",
            }
        )
        logger.info("生成OpenAPI文档规范")

        # 10. 演示完整的健康评估流程
        logger.info("🩺 演示完整的健康评估流程...")

        # 模拟用户健康数据收集
        user_health_data = {
            "user_id": "user_001",
            "symptoms": ["头痛", "失眠", "食欲不振"],
            "vital_signs": {
                "heart_rate": 75,
                "blood_pressure": "120/80",
                "temperature": 36.5,
            },
            "lifestyle": {"sleep_hours": 6, "exercise_frequency": 2, "stress_level": 7},
        }

        # 1) 数据加密存储
        await encryption.encrypt(json.dumps(user_health_data))

        # 2) 写入时序数据库（已移除）
        # for vital_sign, value in user_health_data['vital_signs'].items():
        #     if isinstance(value, (int, float)):
        #         await timeseries_db.write_point({
        #             'measurement': 'vital_signs',
        #             'tags': {'user_id': user_health_data['user_id'], 'type': vital_sign},
        #             'fields': {'value': value},
        #             'timestamp': asyncio.get_event_loop().time()
        #         })

        # 3) 创建知识图谱关系（已移除）
        # for symptom in user_health_data['symptoms']:
        #     symptom_node = await graph_db.create_node(
        #         labels=['Symptom'],
        #         properties={'name': symptom, 'severity': 'moderate'}
        #     )
        #
        #     # 创建用户-症状关系
        #     await graph_db.create_relationship(
        #         start_node_id=user_node['node_id'],
        #         end_node_id=symptom_node['node_id'],
        #         relationship_type='HAS_SYMPTOM',
        #         properties={'reported_at': asyncio.get_event_loop().time()}
        #     )

        logger.info("数据库操作已移除，各微服务自行管理数据库连接")

        # 4) 发送健康评估事件
        assessment_event = {
            "event_type": "health_assessment_requested",
            "user_id": user_health_data["user_id"],
            "data": user_health_data,
            "timestamp": asyncio.get_event_loop().time(),
        }
        await kafka.send_message("health-events", assessment_event)

        # 5) 记录评估指标
        await metrics.increment_counter(
            "health_assessments_total",
            {"user_type": "patient", "assessment_type": "comprehensive"},
        )

        logger.info("✅ 完整健康评估流程演示完成")

        # 11. 系统整体健康检查
        logger.info("🔍 执行系统整体健康检查...")

        overall_health = await components.health_check()
        logger.info(f"系统整体健康状态: {overall_health['status']}")

        # 显示各组件状态
        for component_name, component_health in overall_health["components"].items():
            status = component_health.get("status", "unknown")
            logger.info(f"  {component_name}: {status}")

        logger.info("🎉 索克生活平台通用组件演示完成！")

    except Exception as e:
        logger.error(f"❌ 演示过程中发生错误: {e}")
        raise

    finally:
        # 清理资源
        logger.info("🧹 清理资源...")
        try:
            from services.common import shutdown_components

            await shutdown_components()
            logger.info("✅ 资源清理完成")
        except Exception as e:
            logger.error(f"❌ 资源清理失败: {e}")


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())
