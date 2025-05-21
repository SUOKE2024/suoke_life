#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
后台数据收集服务集成测试
"""

import json
import os
import time
from unittest import mock

import grpc
import pytest
import requests
from google.protobuf.json_format import MessageToDict

from internal.service.collection_service import BackgroundCollectionService
from suoke.accessibility.v1 import accessibility_pb2, accessibility_pb2_grpc

# 模拟服务URL
MOCKSERVER_URL = os.environ.get("MOCKSERVER_URL", "http://localhost:1080")

# 测试用户ID
TEST_USER_ID = "user_test_001"
TEST_DEVICE_ID = "device_test_001"

@pytest.fixture
def collection_service():
    """后台收集服务实例"""
    service = BackgroundCollectionService()
    # 模拟依赖服务的地址
    service.health_data_api_url = f"{MOCKSERVER_URL}/api/health-data"
    service.user_api_url = f"{MOCKSERVER_URL}/api/users"
    service.alert_api_url = f"{MOCKSERVER_URL}/api/alerts"
    service.agent_api_base_url = f"{MOCKSERVER_URL}/api/agents"
    
    yield service

@pytest.fixture
def grpc_channel():
    """gRPC通道"""
    channel = grpc.insecure_channel("localhost:50051")
    yield channel
    channel.close()

@pytest.fixture
def grpc_stub(grpc_channel):
    """gRPC存根"""
    return accessibility_pb2_grpc.AccessibilityServiceStub(grpc_channel)

@mock.patch("internal.platform.battery_bridge.get_battery_info")
def test_configure_background_collection(mock_battery, collection_service):
    """测试配置后台收集"""
    # 模拟电池信息
    mock_battery.return_value = {"level": 85, "charging": True}
    
    # 创建请求
    device_info = accessibility_pb2.DeviceInfo(
        device_id=TEST_DEVICE_ID,
        device_model="Test Model",
        os_version="Android 13",
        app_version="1.0.0",
        sdk_version="1.0.0"
    )
    
    config = accessibility_pb2.CollectionConfiguration(
        collection_interval_seconds=300,
        upload_interval_seconds=3600,
        battery_optimization=True,
        low_battery_threshold=20,
        collect_during_sleep=True,
        storage_policy="ENCRYPT_AND_COMPRESS",
        data_retention_days=30,
        encrypt_data=True
    )
    
    request = accessibility_pb2.BackgroundCollectionRequest(
        user_id=TEST_USER_ID,
        configuration=config,
        data_types=["pulse", "sleep", "activity"],
        device_info=device_info
    )
    
    # 调用服务
    response = collection_service.configure_collection(request, None)
    
    # 验证响应
    assert response.success is True
    assert response.collection_id != ""
    assert response.applied_configuration.collection_interval_seconds == 300
    assert response.applied_configuration.battery_optimization is True

@mock.patch("internal.platform.battery_bridge.get_battery_info")
def test_get_collection_status(mock_battery, collection_service):
    """测试获取收集状态"""
    # 模拟电池信息
    mock_battery.return_value = {"level": 70, "charging": False}
    
    # 创建请求
    request = accessibility_pb2.CollectionStatusRequest(
        user_id=TEST_USER_ID,
        device_id=TEST_DEVICE_ID
    )
    
    # 调用服务
    response = collection_service.get_collection_status(request, None)
    
    # 验证响应
    assert hasattr(response, "is_active")
    assert hasattr(response, "current_configuration")
    assert hasattr(response, "battery_status")
    assert response.battery_status.level == 70
    assert response.battery_status.is_charging is False

@mock.patch("internal.platform.battery_bridge.get_battery_info")
def test_submit_collected_data(mock_battery, collection_service):
    """测试提交收集的数据"""
    # 模拟电池信息
    mock_battery.return_value = {"level": 65, "charging": False}
    
    # 创建请求
    device_info = accessibility_pb2.DeviceInfo(
        device_id=TEST_DEVICE_ID,
        device_model="Test Model",
        os_version="Android 13",
        app_version="1.0.0",
        sdk_version="1.0.0"
    )
    
    # 创建健康数据点
    data_points = [
        accessibility_pb2.HealthDataPoint(
            data_type="pulse",
            value="72",
            timestamp=int(time.time()) - 300,
            confidence=0.95,
            metadata={"position": "wrist", "activity": "resting"}
        ),
        accessibility_pb2.HealthDataPoint(
            data_type="temperature",
            value="36.7",
            timestamp=int(time.time()) - 600,
            confidence=0.98,
            metadata={"measurement_method": "infrared"}
        )
    ]
    
    request = accessibility_pb2.CollectedDataRequest(
        user_id=TEST_USER_ID,
        device_id=TEST_DEVICE_ID,
        collection_id="test_collection_001",
        data_points=data_points,
        device_info=device_info,
        batch_id=f"batch_{int(time.time())}",
        timestamp=int(time.time())
    )
    
    # 调用服务
    response = collection_service.submit_collected_data(request, None)
    
    # 验证响应
    assert response.success is True
    assert response.accepted_points == 2
    assert response.rejected_points == 0

@mock.patch("internal.platform.battery_bridge.get_battery_info")
def test_e2e_background_collection_flow(mock_battery, grpc_stub):
    """端到端测试后台数据收集流程"""
    # 模拟电池信息
    mock_battery.return_value = {"level": 90, "charging": True}
    
    # 步骤1: 配置收集
    device_info = accessibility_pb2.DeviceInfo(
        device_id=TEST_DEVICE_ID,
        device_model="Integration Test Model",
        os_version="Android 13",
        app_version="1.0.0",
        sdk_version="1.0.0"
    )
    
    config = accessibility_pb2.CollectionConfiguration(
        collection_interval_seconds=300,
        upload_interval_seconds=3600,
        battery_optimization=True,
        low_battery_threshold=20
    )
    
    config_request = accessibility_pb2.BackgroundCollectionRequest(
        user_id=TEST_USER_ID,
        configuration=config,
        data_types=["pulse", "sleep", "activity"],
        device_info=device_info
    )
    
    config_response = grpc_stub.ConfigureBackgroundCollection(config_request)
    assert config_response.success is True
    collection_id = config_response.collection_id
    
    # 步骤2: 检查收集状态
    status_request = accessibility_pb2.CollectionStatusRequest(
        user_id=TEST_USER_ID,
        device_id=TEST_DEVICE_ID
    )
    
    status_response = grpc_stub.GetCollectionStatus(status_request)
    assert status_response.is_active is True
    assert status_response.battery_status.level == 90
    
    # 步骤3: 提交收集的数据
    data_points = [
        accessibility_pb2.HealthDataPoint(
            data_type="pulse",
            value="75",
            timestamp=int(time.time()) - 300,
            confidence=0.95
        ),
        accessibility_pb2.HealthDataPoint(
            data_type="activity",
            value="walking",
            timestamp=int(time.time()) - 600,
            confidence=0.92
        )
    ]
    
    submit_request = accessibility_pb2.CollectedDataRequest(
        user_id=TEST_USER_ID,
        device_id=TEST_DEVICE_ID,
        collection_id=collection_id,
        data_points=data_points,
        device_info=device_info,
        batch_id=f"batch_{int(time.time())}",
        timestamp=int(time.time())
    )
    
    submit_response = grpc_stub.SubmitCollectedData(submit_request)
    assert submit_response.success is True
    assert submit_response.accepted_points == 2
    
    # 验证数据提交到健康数据服务
    try:
        health_data_response = requests.get(
            f"{MOCKSERVER_URL}/api/health-data/user/{TEST_USER_ID}"
        )
        assert health_data_response.status_code == 200
        health_data = health_data_response.json()
        assert health_data["user_id"] == TEST_USER_ID
        assert "health_data" in health_data
    except requests.RequestException as e:
        pytest.fail(f"无法验证健康数据服务调用: {str(e)}")
    
    # 检查电池优化功能
    mock_battery.return_value = {"level": 15, "charging": False}
    
    low_battery_status_response = grpc_stub.GetCollectionStatus(status_request)
    assert low_battery_status_response.is_active is True
    
    # 从响应中提取配置, 验证低电量状态下的自动调整
    config_dict = MessageToDict(
        low_battery_status_response.current_configuration,
        preserving_proto_field_name=True
    )
    
    # 低电量时应该降低采集频率
    assert config_dict.get("collection_interval_seconds", 0) > 300

@mock.patch("internal.platform.battery_bridge.get_battery_info")
def test_crisis_alert_integration(mock_battery, collection_service, grpc_stub):
    """测试危机报警与后台数据收集的集成"""
    # 模拟电池信息
    mock_battery.return_value = {"level": 85, "charging": True}
    
    # 创建异常健康数据
    data_points = [
        accessibility_pb2.HealthDataPoint(
            data_type="pulse",
            value="120",  # 异常高的心率
            timestamp=int(time.time()) - 300,
            confidence=0.95,
            metadata={"activity": "resting"}  # 静息状态下心率高
        ),
        accessibility_pb2.HealthDataPoint(
            data_type="pulse",
            value="125",  # 连续两个高心率读数
            timestamp=int(time.time()) - 200,
            confidence=0.96,
            metadata={"activity": "resting"}
        )
    ]
    
    device_info = accessibility_pb2.DeviceInfo(
        device_id=TEST_DEVICE_ID,
        device_model="Test Model",
        os_version="Android 13",
        app_version="1.0.0",
        sdk_version="1.0.0"
    )
    
    request = accessibility_pb2.CollectedDataRequest(
        user_id=TEST_USER_ID,
        device_id=TEST_DEVICE_ID,
        collection_id="test_collection_alert",
        data_points=data_points,
        device_info=device_info,
        batch_id=f"batch_{int(time.time())}",
        timestamp=int(time.time())
    )
    
    # 调用服务
    response = collection_service.submit_collected_data(request, None)
    
    # 验证响应中应包含触发的警报
    assert response.success is True
    assert len(response.alerts) > 0
    
    # 验证警报服务被调用
    try:
        alert_history_response = requests.get(
            f"{MOCKSERVER_URL}/api/alerts/history?user_id={TEST_USER_ID}"
        )
        assert alert_history_response.status_code == 200
        alert_data = alert_history_response.json()
        assert "alerts" in alert_data
    except requests.RequestException as e:
        pytest.fail(f"无法验证警报服务调用: {str(e)}")
    
    # 验证智能体通知
    try:
        agent_response = requests.get(
            f"{MOCKSERVER_URL}/__admin/recordings",
            params={"format": "json"}
        )
        assert agent_response.status_code == 200
        recordings = agent_response.json()
        
        # 查找对智能体的通知请求
        agent_notifications = [
            r for r in recordings.get("requests", [])
            if "/api/agents/" in r.get("path", "") and "/notify" in r.get("path", "")
        ]
        
        # 至少应该有一个智能体被通知
        assert len(agent_notifications) > 0
        
    except requests.RequestException as e:
        pytest.fail(f"无法验证智能体通知: {str(e)}")

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 