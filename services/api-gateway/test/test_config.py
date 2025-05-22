#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置加载和验证测试
"""

import os
import sys
import tempfile
import yaml
from unittest.mock import patch, mock_open

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pkg.utils.config import load_config
from internal.model.config import (
    GatewayConfig, RouteConfig, ServiceDiscoveryConfig, 
    MiddlewareConfig, CacheConfig, AuthConfig, JwtConfig
)


class TestConfig:
    """配置测试类"""
    
    @pytest.fixture
    def config_dict(self):
        """创建配置字典"""
        return {
            "app_name": "test-gateway",
            "host": "0.0.0.0",
            "port": 8080,
            "debug": True,
            "routes": [
                {
                    "name": "user-service",
                    "prefix": "/api/users/",
                    "service": "user-service",
                    "methods": ["GET", "POST", "PUT", "DELETE"],
                    "auth_required": True,
                    "rewrite_path": "^/api/users/(.*)$ => /users/$1"
                },
                {
                    "name": "auth-service",
                    "prefix": "/api/auth/",
                    "service": "auth-service",
                    "methods": ["GET", "POST"],
                    "auth_required": False
                }
            ],
            "service_discovery": {
                "type": "static",
                "services": {
                    "user-service": {
                        "name": "user-service",
                        "version": "v1",
                        "endpoints": [
                            {"host": "user-service", "port": 8001}
                        ]
                    },
                    "auth-service": {
                        "name": "auth-service",
                        "version": "v1",
                        "endpoints": [
                            {"host": "auth-service", "port": 8002}
                        ]
                    }
                }
            },
            "middleware": {
                "auth": {
                    "enabled": True,
                    "public_paths": ["/api/auth/login", "/api/auth/register", "/health"],
                    "jwt": {
                        "secret_key": "test-secret-key",
                        "algorithm": "HS256",
                        "expire_minutes": 30
                    }
                },
                "rate_limit": {
                    "enabled": True,
                    "max_requests": 100,
                    "reset_interval": 60
                },
                "cors": {
                    "enabled": True,
                    "allow_origins": ["*"],
                    "allow_methods": ["*"],
                    "allow_headers": ["*"]
                }
            },
            "cache": {
                "enabled": True,
                "type": "memory",
                "ttl": 60,
                "max_size": 1000
            }
        }
    
    @pytest.fixture
    def yaml_config(self, config_dict):
        """创建YAML配置"""
        return yaml.dump(config_dict)
    
    def test_load_config_from_dict(self, config_dict):
        """测试从字典加载配置"""
        config = load_config(config_data=config_dict)
        
        assert isinstance(config, GatewayConfig)
        assert config.app_name == "test-gateway"
        assert config.port == 8080
        assert config.debug is True
        
        # 验证路由配置
        assert len(config.routes) == 2
        assert config.routes[0].name == "user-service"
        assert config.routes[0].prefix == "/api/users/"
        assert "GET" in config.routes[0].methods
        assert config.routes[0].auth_required is True
        
        # 验证服务发现配置
        assert config.service_discovery.type == "static"
        assert len(config.service_discovery.services) == 2
        assert "user-service" in config.service_discovery.services
        
        # 验证中间件配置
        assert config.middleware.auth.enabled is True
        assert len(config.middleware.auth.public_paths) == 3
        assert "/health" in config.middleware.auth.public_paths
        assert config.middleware.auth.jwt.secret_key == "test-secret-key"
        
        # 验证缓存配置
        assert config.cache.enabled is True
        assert config.cache.type == "memory"
        assert config.cache.ttl == 60
        assert config.cache.max_size == 1000
    
    def test_load_config_from_yaml_file(self, yaml_config):
        """测试从YAML文件加载配置"""
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as config_file:
            config_file.write(yaml_config)
            config_path = config_file.name
        
        try:
            # 加载配置
            config = load_config(config_path=config_path)
            
            # 验证基本配置
            assert isinstance(config, GatewayConfig)
            assert config.app_name == "test-gateway"
            assert config.port == 8080
            
            # 验证路由配置
            assert len(config.routes) == 2
            assert config.routes[0].name == "user-service"
            
            # 验证服务发现配置
            assert config.service_discovery.type == "static"
            assert "user-service" in config.service_discovery.services
            
            # 验证中间件配置
            assert config.middleware.auth.enabled is True
            assert "/health" in config.middleware.auth.public_paths
            
            # 验证缓存配置
            assert config.cache.enabled is True
            assert config.cache.type == "memory"
            
        finally:
            # 删除临时文件
            os.unlink(config_path)
    
    def test_load_config_default_values(self):
        """测试配置默认值"""
        # 最小配置
        minimal_config = {}
        
        config = load_config(config_data=minimal_config)
        
        # 验证默认值
        assert config.app_name == "suoke-api-gateway"
        assert config.host == "0.0.0.0"
        assert config.port == 8000
        assert config.debug is False
        
        # 默认中间件配置
        assert config.middleware is not None
        
        # 默认缓存配置
        assert config.cache is not None
        assert config.cache.enabled is False
        assert config.cache.type == "memory"
    
    def test_load_config_override_with_env(self, config_dict):
        """测试使用环境变量覆盖配置"""
        # 设置环境变量
        with patch.dict(os.environ, {
            "API_GATEWAY_PORT": "9000",
            "API_GATEWAY_DEBUG": "true",
            "API_GATEWAY_JWT_SECRET_KEY": "env-secret-key"
        }):
            config = load_config(config_data=config_dict)
            
            # 验证环境变量覆盖
            assert config.port == 9000
            assert config.debug is True
            assert config.middleware.auth.jwt.secret_key == "env-secret-key"
    
    def test_load_config_validation(self):
        """测试配置验证"""
        # 无效路由配置
        invalid_route_config = {
            "routes": [
                {
                    "name": "user-service",
                    # 缺少必需字段prefix和service
                    "methods": ["GET"]
                }
            ]
        }
        
        # 使用pytest.raises验证是否抛出ValidationError
        with pytest.raises(Exception) as excinfo:
            load_config(config_data=invalid_route_config)
        
        # 验证错误消息中包含缺失字段信息
        assert "prefix" in str(excinfo.value) or "service" in str(excinfo.value)
    
    def test_nested_config_objects(self, config_dict):
        """测试嵌套配置对象"""
        config = load_config(config_data=config_dict)
        
        # 验证嵌套对象
        assert isinstance(config.routes[0], RouteConfig)
        assert isinstance(config.service_discovery, ServiceDiscoveryConfig)
        assert isinstance(config.middleware, MiddlewareConfig)
        assert isinstance(config.middleware.auth, AuthConfig)
        assert isinstance(config.middleware.auth.jwt, JwtConfig)
        assert isinstance(config.cache, CacheConfig)


if __name__ == "__main__":
    pytest.main(["-v", "test_config.py"]) 