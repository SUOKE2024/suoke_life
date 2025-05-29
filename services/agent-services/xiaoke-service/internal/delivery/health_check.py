#!/usr/bin/env python

"""
健康检查和就绪检查HTTP处理器
"""

import json
import logging
import os
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer

import psycopg2
import redis
import requests
from pymongo import MongoClient

logger = logging.getLogger(__name__)


class HealthStatus:
    """健康状态常量"""

    OK = "OK"
    DEGRADED = "DEGRADED"
    DOWN = "DOWN"


class ServiceStatus:
    """服务状态信息"""

    def __init__(self):
        self.status = HealthStatus.DOWN
        self.details = {}
        self.last_check = 0
        self.dependencies = {
            "postgres": {"status": HealthStatus.DOWN, "details": {}},
            "mongodb": {"status": HealthStatus.DOWN, "details": {}},
            "redis": {"status": HealthStatus.DOWN, "details": {}},
            "erp": {"status": HealthStatus.DOWN, "details": {}},
        }


class HealthCheckHandler(BaseHTTPRequestHandler):
    """健康检查HTTP处理器"""

    # 服务状态，在服务启动时初始化
    service_status = ServiceStatus()

    def do_GET(self):
        """处理GET请求"""
        if self.path == "/health":
            self._health_check()
        elif self.path == "/ready":
            self._readiness_check()
        elif self.path == "/metrics":
            self._metrics()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def _health_check(self):
        """健康检查端点 - 检查服务是否运行"""
        status_code = 200

        # 基本服务状态检查 - 服务是否在运行
        response = {
            "status": HealthStatus.OK,
            "service": "xiaoke-service",
            "version": os.getenv("SERVICE_VERSION", "1.0.0"),
            "timestamp": int(time.time()),
        }

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode("utf-8"))

    def _readiness_check(self):
        """就绪检查端点 - 检查服务是否准备好处理请求"""
        # 检查上次检查时间，如果较近则返回缓存结果
        current_time = time.time()
        if current_time - self.service_status.last_check < 30:  # 30秒缓存
            status = self.service_status.status
            details = self.service_status.details
        else:
            # 执行完整的依赖检查
            status, details = self._check_dependencies()

            # 更新服务状态
            self.service_status.status = status
            self.service_status.details = details
            self.service_status.last_check = current_time

        # 设置响应状态码
        status_code = 200 if status == HealthStatus.OK else 503

        response = {
            "status": status,
            "service": "xiaoke-service",
            "version": os.getenv("SERVICE_VERSION", "1.0.0"),
            "timestamp": int(current_time),
            "details": details,
        }

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode("utf-8"))

    def _metrics(self):
        """Prometheus指标端点"""
        # 这里应该返回实际的指标数据，这只是一个简单的示例
        metrics = """
# HELP xiaoke_service_up 小克服务运行状态
# TYPE xiaoke_service_up gauge
xiaoke_service_up 1

# HELP xiaoke_service_requests_total 请求总数
# TYPE xiaoke_service_requests_total counter
xiaoke_service_requests_total{endpoint="ScheduleMedicalResource"} 0
xiaoke_service_requests_total{endpoint="ManageAppointment"} 0
xiaoke_service_requests_total{endpoint="CustomizeProduct"} 0
xiaoke_service_requests_total{endpoint="TraceProduct"} 0
xiaoke_service_requests_total{endpoint="ProcessPayment"} 0
xiaoke_service_requests_total{endpoint="ManageSubscription"} 0
xiaoke_service_requests_total{endpoint="RecommendProducts"} 0
        """

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(metrics.encode("utf-8"))

    def _check_dependencies(self):
        """检查所有依赖服务"""
        all_ok = True
        details = {}

        # 检查PostgreSQL连接
        postgres_status, postgres_details = self._check_postgres()
        details["postgres"] = postgres_details
        self.service_status.dependencies["postgres"]["status"] = postgres_status
        self.service_status.dependencies["postgres"]["details"] = postgres_details

        # 检查MongoDB连接
        mongodb_status, mongodb_details = self._check_mongodb()
        details["mongodb"] = mongodb_details
        self.service_status.dependencies["mongodb"]["status"] = mongodb_status
        self.service_status.dependencies["mongodb"]["details"] = mongodb_details

        # 检查Redis连接
        redis_status, redis_details = self._check_redis()
        details["redis"] = redis_details
        self.service_status.dependencies["redis"]["status"] = redis_status
        self.service_status.dependencies["redis"]["details"] = redis_details

        # 检查ERP系统连接
        erp_status, erp_details = self._check_erp()
        details["erp"] = erp_details
        self.service_status.dependencies["erp"]["status"] = erp_status
        self.service_status.dependencies["erp"]["details"] = erp_details

        # 如果任何一个关键依赖故障，服务状态为故障
        critical_services = ["postgres", "mongodb"]
        for service in critical_services:
            if self.service_status.dependencies[service]["status"] != HealthStatus.OK:
                all_ok = False
                break

        # 如果非关键服务故障，服务状态为降级
        service_status = HealthStatus.OK
        if not all_ok:
            service_status = HealthStatus.DOWN
        else:
            # 检查是否有非关键服务降级
            for service, info in self.service_status.dependencies.items():
                if (
                    service not in critical_services
                    and info["status"] != HealthStatus.OK
                ):
                    service_status = HealthStatus.DEGRADED
                    break

        return service_status, details

    def _check_postgres(self):
        """检查PostgreSQL连接"""
        try:
            # 从环境变量或配置文件获取连接信息
            host = os.getenv("POSTGRES_HOST", "postgres")
            port = os.getenv("POSTGRES_PORT", "5432")
            database = os.getenv("POSTGRES_DB", "xiaoke_db")
            user = os.getenv("POSTGRES_USER", "xiaoke")
            password = os.getenv("POSTGRES_PASSWORD", "")

            # 建立连接并执行简单查询
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                connect_timeout=3,
            )
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result and result[0] == 1:
                return HealthStatus.OK, {"status": HealthStatus.OK}
            else:
                return HealthStatus.DOWN, {
                    "status": HealthStatus.DOWN,
                    "error": "无效的查询结果",
                }

        except Exception as e:
            logger.error(f"PostgreSQL健康检查失败: {e!s}")
            return HealthStatus.DOWN, {
                "status": HealthStatus.DOWN,
                "error": str(e),
                "details": traceback.format_exc(),
            }

    def _check_mongodb(self):
        """检查MongoDB连接"""
        try:
            # 从环境变量或配置文件获取连接信息
            uri = os.getenv("MONGO_URI", "")
            if not uri:
                host = os.getenv("MONGO_HOST", "mongodb")
                port = os.getenv("MONGO_PORT", "27017")
                database = os.getenv("MONGO_DB", "xiaoke_db")
                user = os.getenv("MONGO_USER", "xiaoke")
                password = os.getenv("MONGO_PASSWORD", "")

                if user and password:
                    uri = f"mongodb://{user}:{password}@{host}:{port}/{database}?authSource=admin"
                else:
                    uri = f"mongodb://{host}:{port}/{database}"

            # 建立连接并执行简单查询
            client = MongoClient(uri, serverSelectionTimeoutMS=3000)
            db = client.get_database()
            result = db.command("ping")
            client.close()

            if result and result.get("ok") == 1:
                return HealthStatus.OK, {"status": HealthStatus.OK}
            else:
                return HealthStatus.DOWN, {
                    "status": HealthStatus.DOWN,
                    "error": "无效的查询结果",
                }

        except Exception as e:
            logger.error(f"MongoDB健康检查失败: {e!s}")
            return HealthStatus.DOWN, {
                "status": HealthStatus.DOWN,
                "error": str(e),
                "details": traceback.format_exc(),
            }

    def _check_redis(self):
        """检查Redis连接"""
        try:
            # 从环境变量或配置文件获取连接信息
            host = os.getenv("REDIS_HOST", "redis")
            port = os.getenv("REDIS_PORT", "6379")
            password = os.getenv("REDIS_PASSWORD", "")
            db = os.getenv("REDIS_DB", "0")

            # 建立连接并执行简单命令
            r = redis.Redis(
                host=host,
                port=int(port),
                password=password,
                db=int(db),
                socket_timeout=3,
            )
            result = r.ping()

            if result:
                return HealthStatus.OK, {"status": HealthStatus.OK}
            else:
                return HealthStatus.DOWN, {
                    "status": HealthStatus.DOWN,
                    "error": "PING命令失败",
                }

        except Exception as e:
            logger.error(f"Redis健康检查失败: {e!s}")
            return HealthStatus.DOWN, {
                "status": HealthStatus.DOWN,
                "error": str(e),
                "details": traceback.format_exc(),
            }

    def _check_erp(self):
        """检查ERP系统连接"""
        try:
            # 从环境变量或配置文件获取连接信息
            erp_url = os.getenv("ERP_API_URL", "https://erp-api.suoke.life")
            erp_health_url = f"{erp_url}/health"
            erp_api_key = os.getenv("ERP_API_KEY", "")

            headers = {}
            if erp_api_key:
                headers["X-API-Key"] = erp_api_key

            # 发送请求
            response = requests.get(erp_health_url, headers=headers, timeout=3)

            if response.status_code == 200:
                return HealthStatus.OK, {"status": HealthStatus.OK}
            else:
                return HealthStatus.DOWN, {
                    "status": HealthStatus.DOWN,
                    "error": f"状态码: {response.status_code}",
                    "response": response.text[:100],  # 返回部分响应内容
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"ERP健康检查失败: {e!s}")
            return HealthStatus.DOWN, {
                "status": HealthStatus.DOWN,
                "error": str(e),
                "details": traceback.format_exc(),
            }


def start_health_server(host="0.0.0.0", port=51054):
    """启动健康检查服务器"""
    server = HTTPServer((host, port), HealthCheckHandler)
    logger.info(f"健康检查服务器启动在 http://{host}:{port}")

    # 在新线程中启动服务器
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    return server
