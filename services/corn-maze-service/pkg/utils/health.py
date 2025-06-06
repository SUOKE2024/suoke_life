"""
health - 索克生活项目模块
"""

from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, HTTPServer
from pkg.utils.config import get_value
from typing import Any
import json
import logging
import threading
import time

#!/usr/bin/env python3

"""
健康检查服务
"""



# 初始化日志
logger = logging.getLogger(__name__)

# 健康检查状态常量
STATUS_STARTING = "starting"
STATUS_READY = "ready"
STATUS_NOT_READY = "not_ready"
STATUS_STOPPING = "stopping"


class HealthManager:
    """健康检查管理器"""

    def __init__(self):
        """初始化健康检查管理器"""
        self._health_status = STATUS_STARTING
        self._health_checks = []
        self._health_mutex = threading.Lock()
        self._server = None

    def register_health_check(self, name: str, check_func: Callable[[], bool]) -> None:
        """
        注册健康检查函数

        Args:
            name: 检查名称
            check_func: 检查函数，返回布尔值表示健康状态
        """
        with self._health_mutex:
            self._health_checks.append({
                "name": name,
                "check": check_func,
                "status": True,
                "last_checked": time.time(),
                "failures": 0
            })

        logger.info(f"注册健康检查: {name}")

    def set_status(self, status: str) -> None:
        """
        设置全局健康状态

        Args:
            status: 健康状态
        """
        with self._health_mutex:
            old_status = self._health_status
            self._health_status = status

        logger.info(f"健康状态从 {old_status} 变更为 {status}")

    def get_status(self) -> str:
        """
        获取当前健康状态

        Returns:
            str: 健康状态
        """
        with self._health_mutex:
            return self._health_status

    def get_health_report(self) -> dict[str, Any]:
        """
        获取健康报告

        Returns:
            Dict: 健康报告
        """
        with self._health_mutex:
            checks_result = []
            overall_healthy = True

            for check in self._health_checks:
                checks_result.append({
                    "name": check["name"],
                    "status": "healthy" if check["status"] else "unhealthy",
                    "last_checked": check["last_checked"],
                    "failures": check["failures"]
                })

                if not check["status"]:
                    overall_healthy = False

            status = self._health_status
            if status == STATUS_READY and not overall_healthy:
                status = STATUS_NOT_READY

            return {
                "status": status,
                "version": get_value("app.version", "1.0.0"),
                "start_time": get_value("app.start_time", time.time()),
                "uptime_seconds": time.time() - get_value("app.start_time", time.time()),
                "checks": checks_result
            }

    def update_health_checks(self) -> None:
        """更新所有健康检查"""
        with self._health_mutex:
            for check in self._health_checks:
                try:
                    result = check["check"]()
                    check["status"] = result
                    check["last_checked"] = time.time()

                    if not result:
                        check["failures"] += 1
                        logger.warning(f"健康检查失败: {check['name']}, 连续失败次数: {check['failures']}")
                    else:
                        if check["failures"] > 0:
                            logger.info(f"健康检查恢复: {check['name']}, 之前失败次数: {check['failures']}")
                        check["failures"] = 0

                except Exception as e:
                    check["status"] = False
                    check["last_checked"] = time.time()
                    check["failures"] += 1
                    logger.error(f"健康检查出错: {check['name']}, 错误: {e!s}")

    def start_health_server(self, port: int) -> HTTPServer:
        """
        启动健康检查HTTP服务器

        Args:
            port: 服务器端口

        Returns:
            HTTPServer: HTTP服务器实例
        """
        try:
            # 创建请求处理器类，绑定健康管理器
            class HealthRequestHandler(BaseHTTPRequestHandler):
                def __init__(self, *args, health_manager=None, **kwargs):
                    self.health_manager = health_manager
                    super().__init__(*args, **kwargs)

                def do_GET(self):
                    """处理GET请求"""
                    if self.path in {"/health", "/"}:
                        self._handle_health()
                    elif self.path == "/health/ready":
                        self._handle_ready()
                    elif self.path == "/health/live":
                        self._handle_live()
                    else:
                        self.send_response(404)
                        self.end_headers()

                def _handle_health(self):
                    """处理健康检查请求"""
                    health_report = self.health_manager.get_health_report()
                    status_code = 200

                    if health_report["status"] != STATUS_READY:
                        status_code = 503

                    self.send_response(status_code)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(health_report).encode())

                def _handle_ready(self):
                    """处理就绪检查请求"""
                    status = self.health_manager.get_status()
                    health_report = self.health_manager.get_health_report()

                    if status == STATUS_READY and health_report["status"] == STATUS_READY:
                        self.send_response(200)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(b"OK")
                    else:
                        self.send_response(503)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(f"Not Ready: {status}".encode())

                def _handle_live(self):
                    """处理存活检查请求"""
                    status = self.health_manager.get_status()

                    if status != STATUS_STOPPING:
                        self.send_response(200)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(b"OK")
                    else:
                        self.send_response(503)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(b"Stopping")

                def log_message(self, format, *args):
                    """重写日志方法以避免过多的访问日志"""
                    pass

            # 创建处理器工厂函数
            def handler_factory(*args, **kwargs):
                return HealthRequestHandler(*args, health_manager=self, **kwargs)

            # 创建并启动服务器
            self._server = HTTPServer(("", port), handler_factory)

            # 在单独线程中运行服务器
            server_thread = threading.Thread(
                target=self._server.serve_forever,
                daemon=True,
                name="HealthServer"
            )
            server_thread.start()

            logger.info(f"健康检查服务器已启动, 端口: {port}")
            return self._server

        except Exception as e:
            logger.error(f"启动健康检查服务器失败: {e!s}")
            raise

    def stop_health_server(self):
        """停止健康检查服务器"""
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            logger.info("健康检查服务器已停止")


# 全局健康管理器实例
_health_manager = HealthManager()


# 向后兼容的函数接口
def register_health_check(name: str, check_func: Callable[[], bool]) -> None:
    """注册健康检查函数（向后兼容）"""
    _health_manager.register_health_check(name, check_func)


def set_status_starting() -> None:
    """设置状态为启动中"""
    _health_manager.set_status(STATUS_STARTING)


def set_status_ready() -> None:
    """设置状态为就绪"""
    _health_manager.set_status(STATUS_READY)


def set_status_not_ready() -> None:
    """设置状态为未就绪"""
    _health_manager.set_status(STATUS_NOT_READY)


def set_status_stopping() -> None:
    """设置状态为停止中"""
    _health_manager.set_status(STATUS_STOPPING)


def get_status() -> str:
    """获取当前健康状态（向后兼容）"""
    return _health_manager.get_status()


def get_health_report() -> dict[str, Any]:
    """获取健康报告（向后兼容）"""
    return _health_manager.get_health_report()


def start_health_server(port: int) -> HTTPServer:
    """启动健康检查服务器（向后兼容）"""
    return _health_manager.start_health_server(port)


def stop_health_server():
    """停止健康检查服务器（向后兼容）"""
    _health_manager.stop_health_server()


def _health_check_worker() -> None:
    """健康检查工作线程"""
    while True:
        try:
            _health_manager.update_health_checks()
            time.sleep(get_value("health.check_interval", 30))
        except Exception as e:
            logger.error(f"健康检查工作线程出错: {e!s}")
            time.sleep(5)


def setup_health_server() -> HTTPServer | None:
    """设置健康检查服务器"""
    try:
        port = get_value("health.port", 8080)
        server = start_health_server(port)

        # 启动健康检查工作线程
        worker_thread = threading.Thread(
            target=_health_check_worker,
            daemon=True,
            name="HealthCheckWorker"
        )
        worker_thread.start()

        return server
    except Exception as e:
        logger.error(f"设置健康检查服务器失败: {e!s}")
        return None
