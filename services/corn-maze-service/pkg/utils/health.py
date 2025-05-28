#!/usr/bin/env python3

"""
健康检查服务
"""

from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
import threading
import time
from typing import Any

from pkg.utils.config import get_value

# 初始化日志
logger = logging.getLogger(__name__)

# 健康检查状态
STATUS_STARTING = "starting"
STATUS_READY = "ready"
STATUS_NOT_READY = "not_ready"
STATUS_STOPPING = "stopping"

# 全局健康状态
_health_status = STATUS_STARTING
_health_checks = []
_health_mutex = threading.Lock()


def register_health_check(name: str, check_func: Callable[[], bool]) -> None:
    """
    注册健康检查函数
    
    Args:
        name: 检查名称
        check_func: 检查函数，返回布尔值表示健康状态
    """
    global _health_checks

    with _health_mutex:
        _health_checks.append({
            "name": name,
            "check": check_func,
            "status": True,
            "last_checked": time.time(),
            "failures": 0
        })

    logger.info(f"注册健康检查: {name}")


def set_status(status: str) -> None:
    """
    设置全局健康状态
    
    Args:
        status: 健康状态
    """
    global _health_status

    with _health_mutex:
        old_status = _health_status
        _health_status = status

    logger.info(f"健康状态从 {old_status} 变更为 {status}")


def get_status() -> str:
    """
    获取当前健康状态
    
    Returns:
        str: 健康状态
    """
    with _health_mutex:
        return _health_status


def get_health_report() -> dict[str, Any]:
    """
    获取健康报告
    
    Returns:
        Dict: 健康报告
    """
    with _health_mutex:
        checks_result = []
        overall_healthy = True

        for check in _health_checks:
            checks_result.append({
                "name": check["name"],
                "status": "healthy" if check["status"] else "unhealthy",
                "last_checked": check["last_checked"],
                "failures": check["failures"]
            })

            if not check["status"]:
                overall_healthy = False

        status = _health_status
        if status == STATUS_READY and not overall_healthy:
            status = STATUS_NOT_READY

        return {
            "status": status,
            "version": get_value("app.version", "1.0.0"),
            "start_time": get_value("app.start_time", time.time()),
            "uptime_seconds": time.time() - get_value("app.start_time", time.time()),
            "checks": checks_result
        }


def update_health_checks() -> None:
    """更新所有健康检查"""
    global _health_checks

    with _health_mutex:
        for check in _health_checks:
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


class HealthRequestHandler(BaseHTTPRequestHandler):
    """健康检查HTTP请求处理器"""

    def do_GET(self):
        """处理GET请求"""
        if self.path == "/health" or self.path == "/":
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
        health_report = get_health_report()
        status_code = 200

        if health_report["status"] != STATUS_READY:
            status_code = 503

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(health_report).encode())

    def _handle_ready(self):
        """处理就绪检查请求"""
        status = get_status()
        health_report = get_health_report()

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
        status = get_status()

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
        """重写日志消息，使用我们的日志系统"""
        logger.debug(f"{self.address_string()} - {format % args}")


def run_health_server(port: int) -> HTTPServer:
    """
    运行健康检查服务器
    
    Args:
        port: 服务器端口
        
    Returns:
        HTTPServer: HTTP服务器实例
    """
    server = HTTPServer(('', port), HealthRequestHandler)
    logger.info(f"启动健康检查服务器在端口 {port}")

    # 启动服务器线程
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    # 启动健康检查更新线程
    health_thread = threading.Thread(target=_health_check_worker, daemon=True)
    health_thread.start()

    return server


def _health_check_worker() -> None:
    """健康检查工作线程"""
    while True:
        try:
            update_health_checks()
        except Exception as e:
            logger.error(f"健康检查更新失败: {e!s}")

        time.sleep(10)  # 每10秒检查一次


def setup_health_server() -> HTTPServer | None:
    """
    设置健康检查服务器
    
    Returns:
        Optional[HTTPServer]: 如果启用了健康检查，返回HTTP服务器实例
    """
    health_enabled = get_value("health.enabled", True)
    if not health_enabled:
        logger.info("健康检查已禁用")
        return None

    health_port = get_value("health.port", 51058)
    server = run_health_server(health_port)

    # 注册默认健康检查
    register_health_check("service-status", lambda: get_status() == STATUS_READY)

    return server
