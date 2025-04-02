#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
索克生活RAG服务
===========
主入口文件
"""

import os
import sys
import logging
from loguru import logger
import gunicorn.app.base
from fastapi import FastAPI
from fastapi.middleware.cors

from config import (
    SERVICE_NAME,
    VERSION,
    HOST,
    PORT,
    WORKERS,
    THREADS,
    DEBUG,
    LOG_LEVEL
)
from api import create_app


def setup_logging():
    """配置日志"""
    # 设置loguru日志级别
    logger.remove()
    logger.add(
        sys.stderr,
        level=LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # 将Python标准日志重定向到loguru
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            logger_opt = logger.opt(depth=6, exception=record.exc_info)
            logger_opt.log(record.levelname, record.getMessage())
    
    # 设置标准库日志拦截
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    
    # 设置Flask和Werkzeug日志
    for log_name in ['werkzeug', 'gunicorn', 'gunicorn.access', 'gunicorn.error']:
        logging.getLogger(log_name).handlers = [InterceptHandler()]


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    """Gunicorn应用封装，用于以编程方式运行Gunicorn服务器"""
    
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()
    
    def load_config(self):
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)
    
    def load(self):
        return self.application


def create_gunicorn_app():
    """创建Gunicorn应用"""
    setup_logging()
    
    # 创建Flask应用
    flask_app = create_app()
    
    # 配置Gunicorn选项
    options = {
        'bind': f"{HOST}:{PORT}",
        'workers': WORKERS,
        'threads': THREADS,
        'worker_class': 'gthread',
        'timeout': 120,
        'keepalive': 5,
        'accesslog': '-',
        'errorlog': '-',
        'loglevel': LOG_LEVEL.lower(),
        'proc_name': SERVICE_NAME,
    }
    
    return StandaloneApplication(flask_app, options)


if __name__ == "__main__":
    """主入口函数"""
    logger.info(f"启动 {SERVICE_NAME} v{VERSION}")
    
    try:
        if DEBUG:
            # 开发模式：使用Flask内置服务器
            logger.warning("以开发模式启动服务，不建议在生产环境使用")
            app = create_app()
            app.run(host=HOST, port=PORT, debug=DEBUG)
        else:
            # 生产模式：使用Gunicorn
            logger.info("以生产模式启动服务")
            gunicorn_app = create_gunicorn_app()
            gunicorn_app.run()
            
    except KeyboardInterrupt:
        logger.info("接收到中断信号，正在关闭服务...")
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        sys.exit(1)
