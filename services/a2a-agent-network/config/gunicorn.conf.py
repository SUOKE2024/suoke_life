"""
Gunicorn 配置文件
用于 A2A 智能体网络微服务的生产环境部署
"""

import multiprocessing
import os
from pathlib import Path

# 基础配置
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2

# 日志配置
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程配置
preload_app = True
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL 配置（如果需要）
keyfile = os.getenv("SSL_KEYFILE")
certfile = os.getenv("SSL_CERTFILE")

# 性能调优
worker_tmp_dir = "/dev/shm"
enable_stdio_inheritance = True


# 钩子函数
def on_starting(server):
    """服务器启动时调用"""
    server.log.info("A2A 智能体网络微服务正在启动...")


def on_reload(server):
    """服务器重载时调用"""
    server.log.info("A2A 智能体网络微服务正在重载...")


def when_ready(server):
    """服务器准备就绪时调用"""
    server.log.info("A2A 智能体网络微服务已准备就绪")


def worker_int(worker):
    """工作进程收到 SIGINT 信号时调用"""
    worker.log.info("工作进程 %s 收到中断信号", worker.pid)


def pre_fork(server, worker):
    """工作进程 fork 前调用"""
    server.log.info("工作进程 %s 即将启动", worker.pid)


def post_fork(server, worker):
    """工作进程 fork 后调用"""
    server.log.info("工作进程 %s 已启动", worker.pid)


def post_worker_init(worker):
    """工作进程初始化后调用"""
    worker.log.info("工作进程 %s 初始化完成", worker.pid)


def worker_abort(worker):
    """工作进程异常退出时调用"""
    worker.log.info("工作进程 %s 异常退出", worker.pid)


def pre_exec(server):
    """服务器重新执行前调用"""
    server.log.info("服务器即将重新执行")


def pre_request(worker, req):
    """处理请求前调用"""
    worker.log.debug("处理请求: %s %s", req.method, req.path)


def post_request(worker, req, environ, resp):
    """处理请求后调用"""
    worker.log.debug("请求处理完成: %s %s - %s", req.method, req.path, resp.status_code)


# 环境变量配置
raw_env = [
    f"PYTHONPATH={Path.cwd()}",
    f"CONFIG_PATH={Path.cwd() / 'config' / 'config.yaml'}",
]

# 开发环境特殊配置
if os.getenv("FLASK_ENV") == "development":
    reload = True
    reload_extra_files = [
        "config/config.yaml",
        "internal/",
        "api/",
        "cmd/",
    ]
    workers = 1
    loglevel = "debug"
