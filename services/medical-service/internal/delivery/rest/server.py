#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import threading
from flask import Flask, jsonify
from flask_cors import CORS
import connexion
from connexion.resolver import RestyResolver

# 导入健康检查处理器
from internal.delivery.rest.handlers.health import health_bp

logger = logging.getLogger(__name__)

class RestServer:
    """REST API服务器"""
    
    def __init__(self, config, services):
        """
        初始化REST服务器
        
        Args:
            config: 服务配置
            services: 服务对象字典
        """
        self.config = config
        self.services = services
        self.app = None
        self.server_thread = None
        self.is_running = False
    
    def create_app(self):
        """
        创建并配置Flask应用
        
        Returns:
            Flask应用实例
        """
        try:
            # 使用Connexion创建应用，支持OpenAPI规范
            connexion_app = connexion.App(
                __name__,
                specification_dir='../../../api/rest/',
                options={"swagger_ui": True}
            )
            
            # 尝试加载OpenAPI规范文件
            try:
                connexion_app.add_api(
                    'medical-api.yaml',
                    resolver=RestyResolver('internal.delivery.rest.controllers')
                )
            except Exception as e:
                logger.warning(f"无法加载OpenAPI规范文件: {str(e)}，将使用基本Flask应用")
            
            # 获取Flask应用实例
            app = connexion_app.app
            
            # 配置应用
            app.config['SERVICE_NAME'] = self.config.server.name
            app.config['SERVICE_VERSION'] = self.config.server.version
            app.config['DATABASE'] = {
                'host': self.config.database.host,
                'port': self.config.database.port,
                'user': self.config.database.user,
                'password': self.config.database.password,
                'dbname': self.config.database.dbname
            }
            
            # 启用CORS
            CORS(app)
            
            # 注册健康检查蓝图
            app.register_blueprint(health_bp, url_prefix='/api')
            
            # 注册服务到应用上下文
            app.services = self.services
            
            # 注册错误处理器
            @app.errorhandler(404)
            def not_found(error):
                return jsonify({
                    'error': '未找到请求的资源',
                    'status_code': 404
                }), 404
            
            @app.errorhandler(500)
            def internal_error(error):
                logger.error(f"服务器内部错误: {str(error)}")
                return jsonify({
                    'error': '服务器内部错误',
                    'status_code': 500
                }), 500
            
            # 注册REST控制器路由（如果没有使用OpenAPI规范）
            from internal.delivery.rest.controllers import (
                medical_record_controller,
                diagnosis_controller,
                treatment_controller,
                health_risk_controller,
                medical_query_controller
            )
            
            # 示例路由注册
            app.register_blueprint(medical_record_controller.bp, url_prefix='/api/medical-records')
            app.register_blueprint(diagnosis_controller.bp, url_prefix='/api/diagnosis')
            app.register_blueprint(treatment_controller.bp, url_prefix='/api/treatments')
            app.register_blueprint(health_risk_controller.bp, url_prefix='/api/health-risks')
            app.register_blueprint(medical_query_controller.bp, url_prefix='/api/medical-queries')
            
            return app
            
        except Exception as e:
            logger.error(f"创建Flask应用失败: {str(e)}")
            raise
    
    def start(self):
        """启动REST服务器"""
        if self.is_running:
            logger.warning("REST服务器已经在运行")
            return
        
        try:
            # 创建Flask应用
            self.app = self.create_app()
            
            # 获取服务器配置
            host = '0.0.0.0'  # 绑定到所有网络接口
            port = self.config.server.rest.port
            
            # 创建服务器线程
            self.server_thread = threading.Thread(
                target=self._run_server,
                args=(host, port),
                daemon=True  # 设置为守护线程，主线程退出时自动退出
            )
            
            # 启动服务器线程
            self.server_thread.start()
            self.is_running = True
            
            logger.info(f"REST服务器已启动，监听地址: {host}:{port}")
            
        except Exception as e:
            logger.error(f"启动REST服务器失败: {str(e)}")
            raise
    
    def _run_server(self, host, port):
        """
        在线程中运行Flask服务器
        
        Args:
            host: 服务器监听地址
            port: 服务器监听端口
        """
        try:
            # 使用Werkzeug开发服务器
            self.app.run(
                host=host,
                port=port,
                threaded=True,
                use_reloader=False  # 禁用重载器，因为我们在线程中运行
            )
        except Exception as e:
            logger.error(f"Flask服务器运行失败: {str(e)}")
            self.is_running = False
    
    def stop(self):
        """停止REST服务器"""
        if not self.is_running:
            logger.warning("REST服务器未运行")
            return
        
        try:
            # 停止服务器
            logger.info("正在停止REST服务器...")
            self.is_running = False
            
            # 服务器线程会自动退出，因为是守护线程
            
            logger.info("REST服务器已停止")
            
        except Exception as e:
            logger.error(f"停止REST服务器失败: {str(e)}")
            raise

def create_rest_server(config, services):
    """
    创建REST服务器
    
    Args:
        config: 服务配置
        services: 服务对象字典
        
    Returns:
        REST服务器实例
    """
    return RestServer(config, services)