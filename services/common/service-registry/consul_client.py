"""
consul_client - 索克生活项目模块
"""

            import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Dict, List, Optional
import consul
import json
import logging
import threading
import time

"""
Consul服务发现客户端
提供服务注册、发现、健康检查等功能
"""



logger = logging.getLogger(__name__)

@dataclass
class ServiceInfo:
    """服务信息"""
    name: str
    service_id: str
    address: str
    port: int
    health_check_url: str
    tags: List[str] = None
    meta: Dict[str, str] = None

class ConsulServiceRegistry:
    """Consul服务注册客户端"""

    def __init__(self, consul_host: str = "localhost", consul_port: int = 8500):
        self.consul = consul.Consul(host=consul_host, port=consul_port)
        self.registered_services = {}
        self.service_cache = {}
        self.cache_ttl = 30  # 缓存30秒
        self.health_check_interval = 10  # 健康检查间隔10秒
        self._stop_event = threading.Event()
        self._health_check_thread = None
        self.logger = logger

    def register_service(self, service_info: ServiceInfo) -> bool:
        """注册服务到Consul"""
        try:
            self.consul.agent.service.register(
                name=service_info.name,
                service_id=service_info.service_id,
                address=service_info.address,
                port=service_info.port,
                tags=service_info.tags or [],
                meta=service_info.meta or {},
                check=consul.Check.http(
                    service_info.health_check_url, 
                    interval="10s",
                    timeout="5s"
                )
            )
            self.logger.info(f"Service {service_info.service_id} registered successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register service {service_info.service_id}: {e}")
            return False

    def discover_service(self, service_name: str) -> List[Dict]:
        """发现服务实例"""
        try:
            _, services = self.consul.health.service(service_name, passing=True)
            return [
                {
                    "address": service["Service"]["Address"],
                    "port": service["Service"]["Port"],
                    "service_id": service["Service"]["ID"],
                    "tags": service["Service"]["Tags"],
                    "meta": service["Service"]["Meta"]
                }
                for service in services
            ]
        except Exception as e:
            self.logger.error(f"Failed to discover service {service_name}: {e}")
            return []

    def deregister_service(self, service_id: str) -> bool:
        """注销服务"""
        try:
            self.consul.agent.service.deregister(service_id)
            self.logger.info(f"Service {service_id} deregistered successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to deregister service {service_id}: {e}")
            return False

    def health_check(self, service_id: str) -> bool:
        """检查服务健康状态"""
        try:
            checks = self.consul.health.service(service_id)[1]
            return all(check["Checks"][0]["Status"] == "passing" for check in checks)
        except Exception as e:
            self.logger.error(f"Failed to check health for service {service_id}: {e}")
            return False

    def get_service_endpoint(
        self, service_name: str, load_balance: str = "round_robin"
    ) -> str | None:
        """获取服务端点（带负载均衡）"""
        instances = self.discover_service(service_name)
        if not instances:
            return None

        if load_balance == "round_robin":
            # 简单轮询
            index = getattr(self, f"_{service_name}_index", 0)
            instance = instances[index % len(instances)]
            setattr(self, f"_{service_name}_index", index + 1)
        elif load_balance == "random":

            instance = random.choice(instances)
        else:
            # 默认返回第一个
            instance = instances[0]

        return f"http://{instance['address']}:{instance['port']}"

    def watch_service(
        self, service_name: str, callback: Callable[[list[dict]], None]
    ):
        """监听服务变化"""

        def watch_thread():
            index = None
            while not self._stop_event.is_set():
                try:
                    index, services = self.consul.health.service(
                        service_name, index=index, wait="30s"
                    )

                    # 调用回调函数
                    callback(services)

                except Exception as e:
                    logger.error(f"Error watching service {service_name}: {e}")
                    time.sleep(5)

        thread = threading.Thread(target=watch_thread, daemon=True)
        thread.start()
        return thread

    def get_service_config(self, key: str, default: any | None = None) -> any:
        """获取配置值"""
        try:
            _, data = self.consul.kv.get(key)
            if data:
                value = data["Value"].decode()
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
        except Exception as e:
            logger.error(f"Error getting config {key}: {e}")

        return default

    def set_service_config(self, key: str, value: any) -> bool:
        """设置配置值"""
        try:
            if isinstance(value, dict | list):
                value = json.dumps(value)
            elif not isinstance(value, str):
                value = str(value)

            return self.consul.kv.put(key, value)
        except Exception as e:
            logger.error(f"Error setting config {key}: {e}")
            return False

    def _start_health_check_thread(self):
        """启动健康检查线程"""

        def health_check_loop():
            while not self._stop_event.is_set():
                try:
                    for service_id, instance in self.registered_services.items():
                        # 执行健康检查
                        if self.health_check(service_id):
                            logger.debug(f"Health check passed for {service_id}")
                        else:
                            logger.warning(f"Health check failed for {service_id}")

                    time.sleep(self.health_check_interval)

                except Exception as e:
                    logger.error(f"Health check error: {e}")
                    time.sleep(5)

        self._health_check_thread = threading.Thread(
            target=health_check_loop, daemon=True
        )
        self._health_check_thread.start()

    def clear_cache(self):
        """清空服务缓存"""
        self.service_cache.clear()
        logger.debug("Service cache cleared")

    def get_all_services(self) -> dict[str, list[dict]]:
        """获取所有服务"""
        try:
            services = self.consul.agent.services()
            result = {}

            for service_id, service_info in services.items():
                service_name = service_info["Service"]
                if service_name not in result:
                    result[service_name] = []

                instance = {
                    "address": service_info["Address"],
                    "port": service_info["Port"],
                    "service_id": service_id,
                    "tags": service_info.get("Tags", []),
                    "meta": service_info.get("Meta", {})
                }
                result[service_name].append(instance)

            return result

        except Exception as e:
            logger.error(f"Error getting all services: {e}")
            return {}

    def shutdown(self):
        """关闭客户端"""
        logger.info("Shutting down Consul client...")

        # 停止健康检查线程
        self._stop_event.set()

        # 注销所有已注册的服务
        for service_id in list(self.registered_services.keys()):
            self.deregister_service(service_id)

        # 等待健康检查线程结束
        if self._health_check_thread and self._health_check_thread.is_alive():
            self._health_check_thread.join(timeout=5)

        logger.info("Consul client shutdown complete")

# 全局实例
_consul_client = None

def get_consul_client(
    consul_host: str = "localhost", consul_port: int = 8500
) -> ConsulServiceRegistry:
    """获取Consul客户端单例"""
    global _consul_client
    if _consul_client is None:
        _consul_client = ConsulServiceRegistry(consul_host, consul_port)
    return _consul_client

# 使用示例
if __name__ == "__main__":
    # 创建客户端
    client = ConsulServiceRegistry()

    # 注册服务
    client.register_service(
        service_info=ServiceInfo(
            name="xiaoai-service",
            service_id="xiaoai-service-1",
            address="127.0.0.1",
            port=8080,
            health_check_url="http://127.0.0.1:8080/health",
            tags=["ai", "tcm", "diagnosis"],
            meta={"version": "1.0.0", "region": "beijing"},
        )
    )

    # 发现服务
    instances = client.discover_service("xiaoai-service")
    for instance in instances:
        print(
            f"Found service: {instance['service_id']} at {instance['address']}:{instance['port']}"
        )

    # 获取服务端点
    endpoint = client.get_service_endpoint("xiaoai-service")
    print(f"Service endpoint: {endpoint}")

    # 监听服务变化
    def on_service_change(instances):
        print(f"Service instances changed: {len(instances)} instances")

    client.watch_service("xiaoai-service", on_service_change)

    # 配置管理
    client.set_service_config("xiaoai/model_version", "v2.1.0")
    model_version = client.get_service_config("xiaoai/model_version")
    print(f"Model version: {model_version}")

    # 保持运行
    try:
        time.sleep(60)
    except KeyboardInterrupt:
        pass
    finally:
        client.shutdown()
