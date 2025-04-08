#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Flask应用工厂
==========
创建并配置Flask应用
"""

import os
import json
from typing import Dict, Any, Optional
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from loguru import logger

from ..config import (
    SERVICE_NAME, 
    VERSION,
    MAX_REQUEST_SIZE_MB,
    RATE_LIMIT_ENABLED,
    RATE_LIMIT_DEFAULT,
    load_config
)
from .routes import api_bp, web_search_bp, specialized_bp


def create_app(config: Optional[Dict[str, Any]] = None) -> Flask:
    """
    创建并配置Flask应用实例
    
    Args:
        config: 额外的配置参数
        
    Returns:
        Flask: 配置好的Flask应用实例
    """
    app = Flask(SERVICE_NAME)
    
    # 基本配置
    app.config["MAX_CONTENT_LENGTH"] = MAX_REQUEST_SIZE_MB * 1024 * 1024
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False
    app.config["JSON_SORT_KEYS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    
    # 添加额外配置
    if config:
        app.config.update(config)
    
    # 允许跨域访问
    CORS(app, supports_credentials=True)
    
    # 加载配置
    config = load_config()
    app.config.update(config)
    
    # 配置web-search模块
    web_search_config = {}
    if os.path.exists(os.environ.get('WEB_SEARCH_CONFIG_PATH', './config/web_search_config.json')):
        try:
            with open(os.environ.get('WEB_SEARCH_CONFIG_PATH', './config/web_search_config.json'), 'r') as f:
                web_search_config = json.load(f)
        except Exception as e:
            logger.error(f"加载Web搜索配置失败: {e}")
    
    app.config['WEB_SEARCH_CONFIG'] = web_search_config
    
    # 注册蓝图
    app.register_blueprint(api_bp)
    app.register_blueprint(web_search_bp)
    app.register_blueprint(specialized_bp)
    
    # 注册错误处理
    register_error_handlers(app)
    
    logger.info(f"创建了 {SERVICE_NAME} v{VERSION} Flask应用")
    return app


def register_error_handlers(app: Flask) -> None:
    """
    注册错误处理器
    
    Args:
        app: Flask应用实例
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": True,
            "message": "请求参数无效",
            "details": str(error)
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": True,
            "message": "未找到请求的资源",
            "details": str(error)
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "error": True,
            "message": "请求方法不允许",
            "details": str(error)
        }), 405
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            "error": True,
            "message": f"请求体过大，最大允许{MAX_REQUEST_SIZE_MB}MB",
            "details": str(error)
        }), 413
    
    @app.errorhandler(429)
    def too_many_requests(error):
        return jsonify({
            "error": True,
            "message": "请求过于频繁，请稍后再试",
            "details": str(error)
        }), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"服务器内部错误: {error}")
        return jsonify({
            "error": True,
            "message": "服务器内部错误",
            "details": str(error)
        }), 500
    
    # 拦截所有未处理的异常
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"未处理的异常: {error}")
        return jsonify({
            "error": True,
            "message": "服务器内部错误",
            "details": str(error)
        }), 500

    # 添加全局错误处理
    @app.errorhandler(404)
    def handle_404(e):
        return {"error": "资源不存在"}, 404
        
    @app.errorhandler(500)
    def handle_500(e):
        return {"error": "服务器内部错误"}, 500
    
    # 添加根路由
    @app.route('/')
    def index():
        return jsonify({
            "service": "rag-service",
            "version": VERSION,
            "status": "healthy",
            "features": ["semantic_search", "knowledge_graph", "web_search"]
        })
    
    # 添加健康检查路由
    @app.route('/health')
    def health():
        return jsonify({
            "status": "healthy",
            "version": VERSION
        }) 