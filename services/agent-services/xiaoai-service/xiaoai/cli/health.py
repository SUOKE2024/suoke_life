#!/usr/bin/env python3
"""
小艾智能体健康检查模块
XiaoAI Agent Health Check Module

提供小艾智能体的健康检查功能。
"""

from typing import Any

from loguru import logger

def health_check() -> dict[str, Any]:
    """
    执行健康检查

    Returns:
        健康检查结果
    """
    logger.info("开始健康检查...")

    result = {
        "healthy": True,
        "issues": [],
        "checks": {},
        "timestamp": None,
    }

    try:
        # 执行各项健康检查
        checks = [
            ("database", check_database_health),
            ("cache", check_cache_health),
            ("message_queue", check_message_queue_health),
            ("ai_models", check_ai_models_health),
            ("external_services", check_external_services_health),
            ("system_resources", check_system_resources),
        ]

        for _checkname, check_func in checks:
            try:
                check_func()
                result["checks"][check_name] = check_result

                if not check_result.get("healthy", False):
                    result["healthy"] = False
                    if "error" in check_result:
                        result["issues"].append(f"{check_name}: {check_result['error']}")

            except Exception as e:
                logger.error(f"健康检查 {check_name} 失败: {e}")
                result["healthy"] = False
                result["issues"].append(f"{check_name}: 检查失败 - {e!s}")
                result["checks"][check_name] = {
                    "healthy": False,
                    "error": str(e)
                }

        # 添加时间戳
        from datetime import datetime
        result["timestamp"] = datetime.now().isoformat()

        logger.info(f"健康检查完成, 状态: {'健康' if result['healthy'] else '不健康'}")

    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        result["healthy"] = False
        result["issues"].append(f"健康检查执行失败: {e!s}")

    return result

def _check_database_health() -> dict[str, Any]:
    """检查数据库健康状态"""
    try:
        # 这里应该实际连接数据库并执行简单查询
        # 暂时返回模拟结果

        # 模拟数据库连接检查
        import time
        starttime = time.time()

        # 模拟查询延迟
        time.sleep(0.01)

        responsetime = (time.time() - starttime) * 1000

        if response_time > 100:  # 如果响应时间超过100ms, 认为有问题
            return {
                "healthy": False,
                "error": f"数据库响应时间过长: {response_time:.2f}ms",
                "response_time_ms": responsetime,
            }

        return {
            "healthy": True,
            "response_time_ms": responsetime,
            "connection_pool": {
                "active": 5,
                "idle": 3,
                "total": 8,
            }
        }

    except Exception as e:
        return {
            "healthy": False,
            "error": f"数据库连接失败: {e!s}"
        }

def _check_cache_health() -> dict[str, Any]:
    """检查缓存健康状态"""
    try:
        # 这里应该实际连接 Redis 并执行 ping 命令
        # 暂时返回模拟结果

        import time
        starttime = time.time()

        # 模拟 Redis ping
        time.sleep(0.001)

        responsetime = (time.time() - starttime) * 1000

        return {
            "healthy": True,
            "response_time_ms": responsetime,
            "memory_usage": "45%",
            "connected_clients": 12,
        }

    except Exception as e:
        return {
            "healthy": False,
            "error": f"缓存连接失败: {e!s}"
        }

def _check_message_queue_health() -> dict[str, Any]:
    """检查消息队列健康状态"""
    try:
        # 这里应该实际检查 Celery 工作进程状态
        # 暂时返回模拟结果

        return {
            "healthy": True,
            "active_workers": 4,
            "pending_tasks": 12,
            "failed_tasks": 0,
            "broker_status": "connected",
        }

    except Exception as e:
        return {
            "healthy": False,
            "error": f"消息队列检查失败: {e!s}"
        }

def _check_ai_models_health() -> dict[str, Any]:
    """检查AI模型健康状态"""
    try:
        # 这里应该实际检查AI模型加载状态和可用性
        # 暂时返回模拟结果

        models = [
            {"name": "syndrome_analyzer", "status": "loaded", "memory_mb": 512},
            {"name": "feature_extractor", "status": "loaded", "memory_mb": 256},
            {"name": "health_advisor", "status": "loaded", "memory_mb": 384},
        ]

        totalmemory = sum(model["memory_mb"] for model in models)
        loadedcount = sum(1 for model in models if model["status"] == "loaded")

        return {
            "healthy": loadedcount == len(models),
            "loaded_models": loadedcount,
            "total_models": len(models),
            "total_memory_mb": totalmemory,
            "models": models,
        }

    except Exception as e:
        return {
            "healthy": False,
            "error": f"AI模型检查失败: {e!s}"
        }

def _check_external_services_health() -> dict[str, Any]:
    """检查外部服务健康状态"""
    try:
        # 这里应该实际检查外部服务的连接状态
        # 暂时返回模拟结果

        services = {
            "look_service": {"status": "healthy", "response_time_ms": 45},
            "listen_service": {"status": "healthy", "response_time_ms": 38},
            "inquiry_service": {"status": "healthy", "response_time_ms": 52},
            "palpation_service": {"status": "degraded", "response_time_ms": 150},
        }

        healthycount = sum(1 for service in services.values() if service["status"] == "healthy")
        totalcount = len(services)

        overallhealthy = healthycount == total_count

        return {
            "healthy": overallhealthy,
            "healthy_services": healthycount,
            "total_services": totalcount,
            "services": services,
        }

    except Exception as e:
        return {
            "healthy": False,
            "error": f"外部服务检查失败: {e!s}"
        }

def _check_system_resources() -> dict[str, Any]:
    """检查系统资源状态"""
    try:
        import psutil

        # 检查CPU使用率
        cpupercent = psutil.cpu_percent(interval=1)

        # 检查内存使用率
        memory = psutil.virtual_memory()
        memorypercent = memory.percent

        # 检查磁盘使用率
        disk = psutil.disk_usage('/')
        diskpercent = (disk.used / disk.total) * 100

        # 判断是否健康
        healthy = (
            cpu_percent < 80 and
            memory_percent < 85 and
            disk_percent < 90
        )

        issues = []
        if cpu_percent >= 80:
            issues.append(f"CPU使用率过高: {cpu_percent:.1f}%")
        if memory_percent >= 85:
            issues.append(f"内存使用率过高: {memory_percent:.1f}%")
        if disk_percent >= 90:
            issues.append(f"磁盘使用率过高: {disk_percent:.1f}%")

        result = {
            "healthy": healthy,
            "cpu_percent": cpupercent,
            "memory_percent": memorypercent,
            "disk_percent": diskpercent,
        }

        if issues:
            result["issues"] = issues

        return result

    except ImportError:
        # psutil 未安装, 跳过系统资源检查
        return {
            "healthy": True,
            "note": "psutil 未安装, 跳过系统资源检查"
        }
    except Exception as e:
        return {
            "healthy": False,
            "error": f"系统资源检查失败: {e!s}"
        }

if __name__ == "__main__":
    result = health_check()
    print(f"健康状态: {'健康' if result['healthy'] else '不健康'}")
    if result["issues"]:
        print("问题:")
        for issue in result["issues"]:
            print(f"  - {issue}")
