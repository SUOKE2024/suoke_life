#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RAG服务主应用入口
"""

import os
import logging
from flask import Flask, jsonify
from src.api.routes.web_search import web_search_bp
from src.config import load_config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def create_app(config_path=None):
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 加载配置
    config = load_config(config_path)
    app.config.update(config)
    
    # 注册蓝图
    app.register_blueprint(web_search_bp, url_prefix='/api/web-search')
    
    # 健康检查端点
    @app.route('/health')
    def health_check():
        return jsonify({
            "status": "healthy",
            "version": "2.0.0"
        })
    
    @app.route('/')
    def index():
        return jsonify({
            "service": "rag-service",
            "status": "running",
            "version": "2.0.0",
            "features": ["semantic_search", "knowledge_graph", "web_search"]
        })
    
    logger.info("RAG应用已创建和配置")
    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True) 