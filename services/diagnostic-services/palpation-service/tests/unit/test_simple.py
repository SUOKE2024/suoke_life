"""
简化测试 - 只测试基本功能，不依赖internal模块
"""

import pytest
from datetime import datetime

from palpation_service.config import settings, get_settings
from palpation_service.models import (
    SuccessResponse, 
    ErrorResponse, 
    SessionCreateRequest,
    SensorDataInput,
    SensorDataPoint,
    SensorType,
    SessionType,
    SessionStatus,
    AnalysisType,
    Gender
)

class TestBasicConfiguration:
    """基本配置测试"""
    
    def test_settings_singleton(self):
        """测试配置单例模式"""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2
    
    def test_default_values(self):
        """测试默认配置值"""
        assert settings.service.name == "palpation-service"
        assert settings.service.version == "1.0.0"
        assert settings.service.port == 8000
        assert settings.service.debug is True
    
    def test_environment_detection(self):
        """测试环境检测"""
        assert settings.is_development is True
        assert settings.is_production is False
    
    def test_fusion_weights(self):
        """测试融合权重配置"""
        weights = settings.fusion.fusion_weights
        assert isinstance(weights, dict)
        assert 'pressure' in weights
        assert 'temperature' in weights
        assert 'texture' in weights
        assert 'vibration' in weights
        
        # 权重总和应该接近1.0
        total_weight = sum(weights.values())
        assert abs(total_weight - 1.0) < 0.01

class TestBasicModels:
    """基本数据模型测试"""
    
    def test_success_response(self):
        """测试成功响应模型"""
        response = SuccessResponse(
            message="测试成功",
            data={"key": "value"}
        )
        
        assert response.message == "测试成功"
        assert response.data == {"key": "value"}
        assert isinstance(response.timestamp, datetime)
    
    def test_error_response(self):
        """测试错误响应模型"""
        response = ErrorResponse(
            error_code="TEST_ERROR",
            error_message="测试错误",
            details={"detail": "详细信息"}
        )
        
        assert response.error_code == "TEST_ERROR"
        assert response.error_message == "测试错误"
        assert response.details == {"detail": "详细信息"}
        assert isinstance(response.timestamp, datetime)
    
    def test_session_create_request(self):
        """测试会话创建请求模型"""
        request = SessionCreateRequest(
            user_id="test_user_123",
            session_type=SessionType.STANDARD,
            metadata={"test": True}
        )
        
        assert request.user_id == "test_user_123"
        assert request.session_type == SessionType.STANDARD
        assert request.metadata == {"test": True}
    
    def test_session_create_request_validation(self):
        """测试会话创建请求验证"""
        # 测试空用户ID
        with pytest.raises(ValueError, match="用户ID不能为空"):
            SessionCreateRequest(user_id="   ")
        
        # 测试用户ID去除空格
        request = SessionCreateRequest(user_id="  test_user  ")
        assert request.user_id == "test_user"
    
    def test_sensor_data_point(self):
        """测试传感器数据点模型"""
        data_point = SensorDataPoint(
            timestamp=datetime.now(),
            value=25.5,
            unit="celsius",
            metadata={"location": "wrist"}
        )
        
        assert data_point.value == 25.5
        assert data_point.unit == "celsius"
        assert data_point.metadata == {"location": "wrist"}
    
    def test_sensor_data_input(self):
        """测试传感器数据输入模型"""
        data_points = [
            SensorDataPoint(
                timestamp=datetime.now(),
                value=25.5,
                unit="celsius"
            )
        ]
        
        sensor_input = SensorDataInput(
            sensor_type=SensorType.TEMPERATURE,
            data_points=data_points,
            quality_indicators={"snr": 0.95}
        )
        
        assert sensor_input.sensor_type == SensorType.TEMPERATURE
        assert len(sensor_input.data_points) == 1
        assert sensor_input.quality_indicators == {"snr": 0.95}
    
    def test_sensor_data_input_validation(self):
        """测试传感器数据输入验证"""
        # 测试空数据点
        with pytest.raises(ValueError, match="数据点不能为空"):
            SensorDataInput(
                sensor_type=SensorType.PRESSURE,
                data_points=[]
            )

class TestEnums:
    """枚举类型测试"""
    
    def test_sensor_types(self):
        """测试传感器类型枚举"""
        assert SensorType.PRESSURE == "pressure"
        assert SensorType.TEMPERATURE == "temperature"
        assert SensorType.TEXTURE == "texture"
        assert SensorType.VIBRATION == "vibration"
    
    def test_session_types(self):
        """测试会话类型枚举"""
        assert SessionType.STANDARD == "standard"
        assert SessionType.QUICK == "quick"
        assert SessionType.DETAILED == "detailed"
        assert SessionType.RESEARCH == "research"
    
    def test_session_status(self):
        """测试会话状态枚举"""
        assert SessionStatus.ACTIVE == "active"
        assert SessionStatus.COMPLETED == "completed"
        assert SessionStatus.CANCELLED == "cancelled"
        assert SessionStatus.ERROR == "error"
    
    def test_analysis_types(self):
        """测试分析类型枚举"""
        assert AnalysisType.PRESSURE_ANALYSIS == "pressure_analysis"
        assert AnalysisType.TEMPERATURE_ANALYSIS == "temperature_analysis"
        assert AnalysisType.TEXTURE_ANALYSIS == "texture_analysis"
        assert AnalysisType.MULTIMODAL_FUSION == "multimodal_fusion"
        assert AnalysisType.HEALTH_ASSESSMENT == "health_assessment"
    
    def test_gender(self):
        """测试性别枚举"""
        assert Gender.MALE == "male"
        assert Gender.FEMALE == "female"
        assert Gender.OTHER == "other"

class TestUtilities:
    """工具函数测试"""
    
    def test_size_parsing(self):
        """测试大小解析功能"""
        test_settings = get_settings()
        
        # 测试不同的大小格式
        assert test_settings._parse_size("1024") == 1024
        assert test_settings._parse_size("1KB") == 1024
        assert test_settings._parse_size("1MB") == 1024 * 1024
        assert test_settings._parse_size("1GB") == 1024 * 1024 * 1024
    
    def test_log_config_generation(self):
        """测试日志配置生成"""
        log_config = settings.get_log_config()
        
        assert "version" in log_config
        assert "formatters" in log_config
        assert "handlers" in log_config
        assert "loggers" in log_config
        
        # 检查格式化器
        assert "default" in log_config["formatters"]
        assert "structured" in log_config["formatters"]
        
        # 检查处理器
        assert "console" in log_config["handlers"]
        
        # 检查日志器
        assert "" in log_config["loggers"]  # 根日志器
        assert "uvicorn" in log_config["loggers"]
        assert "sqlalchemy" in log_config["loggers"]

def test_basic_import():
    """测试基本导入功能"""
    from palpation_service import __version__
    assert __version__ == "1.0.0"

def test_config_access():
    """测试配置访问"""
    config = get_settings()
    assert config is not None
    assert hasattr(config, 'service')
    assert hasattr(config, 'database')
    assert hasattr(config, 'redis') 