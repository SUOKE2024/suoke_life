"""
Consul服务发现客户端
提供服务注册、发现、健康检查等功能
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging
import socket
import threading
import time

import consul

logger = logging.getLogger(__name__)


@dataclass
class ServiceInstance:
    """服务实例信息"""

    service_id: str
    service_name: str
    address: str
    port: int
    tags: list[str] = None
    meta: dict[str, str] = None
    health_status: str = "passing"
    last_updated: datetime = None


class ConsulServiceRegistry:
    """Consul服务注册中心客户端"""

    def __init__(self, consul_host: str = "localhost", consul_port: int = 8500):
        self.consul = consul.Consul(host=consul_host, port=consul_port)
        self.registered_services = {}
        self.service_cache = {}
        self.cache_ttl = 30  # 缓存30秒
        self.health_check_interval = 10  # 健康检查间隔10秒
        self._stop_event = threading.Event()
        self._health_check_thread = None

    def register_service(
        self,
        service_name: str,
        service_id: str,
        address: str,
        port: int,
        health_check_url: str | None = None,
        tags: list[str] | None = None,
        meta: dict[str, str] | None = None,
    ) -> bool:
        """注册服务到Consul"""
        try:
            # 构建健康检查配置
            check = None
            if health_check_url:
                check = consul.Check.http(
                    health_check_url, interval="10s", timeout="5s"
                )
            else:
                # 默认TCP检查
                check = consul.Check.tcp(
                    f"{address}:{port}", interval="10s", timeout="3s"
                )

            # 注册服务
            success = self.consul.agent.service.register(
                name=service_name,
                service_id=service_id,
                address=address,
                port=port,
                tags=tags or [],
                meta=meta or {},
                check=check,
            )

            if success:
                # 记录已注册的服务
                self.registered_services[service_id] = ServiceInstance(
                    service_id=service_id,
                    service_name=service_name,
                    address=address,
                    port=port,
                    tags=tags,
                    meta=meta,
                    last_updated=datetime.now(),
                )

                logger.info(
                    f"Service registered: {service_name} ({service_id}) at {address}:{port}"
                )

                # 启动健康检查线程
                if (
                    not self._health_check_thread
                    or not self._health_check_thread.is_alive()
                ):
                    self._start_health_check_thread()

                return True
            else:
                logger.error(f"Failed to register service: {service_name}")
                return False

        except Exception as e:
            logger.error(f"Error registering service {service_name}: {e}")
            return False

    def discover_service(
        self, service_name: str, healthy_only: bool = True
    ) -> list[ServiceInstance]:
        """发现服务实例"""
        try:
            # 检查缓存
            cache_key = f"{service_name}_{healthy_only}"
            if cache_key in self.service_cache:
                cached_data, cache_time = self.service_cache[cache_key]
                if datetime.now() - cache_time < timedelta(seconds=self.cache_ttl):
                    return cached_data

            # 从Consul获取服务实例
            _, services = self.consul.health.service(service_name, passing=healthy_only)

            instances = []
            for service in services:
                service_info = service["Service"]
                health_info = service["Checks"]

                # 确定健康状态
                health_status = "passing"
                for check in health_info:
                    if check["Status"] != "passing":
                        health_status = check["Status"]
                        break

                instance = ServiceInstance(
                    service_id=service_info["ID"],
                    service_name=service_info["Service"],
                    address=service_info["Address"],
                    port=service_info["Port"],
                    tags=service_info.get("Tags", []),
                    meta=service_info.get("Meta", {}),
                    health_status=health_status,
                    last_updated=datetime.now(),
                )
                instances.append(instance)

            # 更新缓存
            self.service_cache[cache_key] = (instances, datetime.now())

            logger.debug(
                f"Discovered {len(instances)} instances for service: {service_name}"
            )
            return instances

        except Exception as e:
            logger.error(f"Error discovering service {service_name}: {e}")
            return []

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
            import random

            instance = random.choice(instances)
        else:
            # 默认返回第一个
            instance = instances[0]

        return f"http://{instance.address}:{instance.port}"

    def deregister_service(self, service_id: str) -> bool:
        """注销服务"""
        try:
            success = self.consul.agent.service.deregister(service_id)
            if success and service_id in self.registered_services:
                del self.registered_services[service_id]
                logger.info(f"Service deregistered: {service_id}")
            return success
        except Exception as e:
            logger.error(f"Error deregistering service {service_id}: {e}")
            return False

    def watch_service(
        self, service_name: str, callback: Callable[[list[ServiceInstance]], None]
    ):
        """监听服务变化"""

        def watch_thread():
            index = None
            while not self._stop_event.is_set():
                try:
                    index, services = self.consul.health.service(
                        service_name, index=index, wait="30s"
                    )

                    instances = []
                    for service in services:
                        service_info = service["Service"]
                        instance = ServiceInstance(
                            service_id=service_info["ID"],
                            service_name=service_info["Service"],
                            address=service_info["Address"],
                            port=service_info["Port"],
                            tags=service_info.get("Tags", []),
                            meta=service_info.get("Meta", {}),
                            last_updated=datetime.now(),
                        )
                        instances.append(instance)

                    # 调用回调函数
                    callback(instances)

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
                        if self._check_service_health(instance):
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

    def _check_service_health(self, instance: ServiceInstance) -> bool:
        """检查服务健康状态"""
        try:
            # 简单的TCP连接检查
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((instance.address, instance.port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def clear_cache(self):
        """清空服务缓存"""
        self.service_cache.clear()
        logger.debug("Service cache cleared")

    def get_all_services(self) -> dict[str, list[ServiceInstance]]:
        """获取所有服务"""
        try:
            services = self.consul.agent.services()
            result = {}

            for service_id, service_info in services.items():
                service_name = service_info["Service"]
                if service_name not in result:
                    result[service_name] = []

                instance = ServiceInstance(
                    service_id=service_id,
                    service_name=service_name,
                    address=service_info["Address"],
                    port=service_info["Port"],
                    tags=service_info.get("Tags", []),
                    meta=service_info.get("Meta", {}),
                    last_updated=datetime.now(),
                )
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
        service_name="xiaoai-service",
        service_id="xiaoai-service-1",
        address="127.0.0.1",
        port=8080,
        health_check_url="http://127.0.0.1:8080/health",
        tags=["ai", "tcm", "diagnosis"],
        meta={"version": "1.0.0", "region": "beijing"},
    )

    # 发现服务
    instances = client.discover_service("xiaoai-service")
    for instance in instances:
        print(
            f"Found service: {instance.service_name} at {instance.address}:{instance.port}"
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
