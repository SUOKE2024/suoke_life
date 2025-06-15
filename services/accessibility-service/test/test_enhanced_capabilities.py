#!/usr/bin/env python

"""
增强功能测试 - 测试桌面自动化、位置服务和传感器管理器
"""

import os

# 导入要测试的模块
import sys
import time

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "internal", "service"))

from desktop_automation import (
    ActionResult,
    ActionType,
    DesktopAction,
    DesktopAutomationService,
    Point,
)
from location_service import (
    Coordinate,
    Location,
    LocationService,
    LocationType,
    NavigationMode,
)


class TestDesktopAutomationService:
    """桌面自动化服务测试"""

    @pytest.fixture
    def config(self) -> None:
        """测试配置"""
        return {
            "desktop_automation": {
                "enabled": True,
                "security_policy": {
                    "max_actions_per_minute": 60,
                    "allowed_apps": [],
                    "blocked_areas": [],
                },
            }
        }

    @pytest.fixture
    def desktop_service(self, config):
        """创建桌面自动化服务实例"""
        return DesktopAutomationService(config)

    def test_service_initialization(self, desktop_service):
        """测试服务初始化"""
        assert desktop_service.enabled is True
        assert desktop_service.platform is not None
        assert desktop_service.action_history == []
        assert desktop_service.stats["total_actions"] == 0

    @pytest.mark.asyncio
    async def test_execute_click_action(self, desktop_service):
        """测试点击操作"""
        action = DesktopAction(
            action_type=ActionType.CLICK, target=Point(x=100, y=200), parameters={}
        )

        result = await desktop_service.execute_action(action, "test_user")

        assert isinstance(result, ActionResult)
        assert result.success is True
        assert result.execution_time >= 0
        assert desktop_service.stats["total_actions"] == 1

    @pytest.mark.asyncio
    async def test_execute_swipe_action(self, desktop_service):
        """测试滑动操作"""
        action = DesktopAction(
            action_type=ActionType.SWIPE,
            target=Point(x=100, y=200),
            parameters={
                "start_point": {"x": 100, "y": 200},
                "end_point": {"x": 300, "y": 400},
                "duration": 1.0,
            },
        )

        result = await desktop_service.execute_action(action, "test_user")

        assert result.success is True
        assert "滑动" in result.message

    @pytest.mark.asyncio
    async def test_execute_input_text_action(self, desktop_service):
        """测试文本输入操作"""
        action = DesktopAction(
            action_type=ActionType.INPUT_TEXT,
            target="input_field",
            parameters={"text": "Hello World", "clear_first": True},
        )

        result = await desktop_service.execute_action(action, "test_user")

        assert result.success is True
        assert "输入" in result.message

    def test_security_check(self, desktop_service):
        """测试安全检查"""
        action = DesktopAction(
            action_type=ActionType.CLICK, target=Point(x=100, y=200), parameters={}
        )

        # 正常操作应该通过安全检查
        check_result = desktop_service._security_check(action, "test_user")
        assert check_result["allowed"] is True

    def test_action_history_recording(self, desktop_service):
        """测试操作历史记录"""
        action = DesktopAction(
            action_type=ActionType.CLICK, target=Point(x=100, y=200), parameters={}
        )

        desktop_service._record_action(action, "test_user")

        assert len(desktop_service.action_history) == 1
        assert desktop_service.action_history[0]["user_id"] == "test_user"
        assert desktop_service.action_history[0]["action_type"] == "click"

    def test_get_stats(self, desktop_service):
        """测试获取统计信息"""
        stats = desktop_service.get_stats()

        assert "enabled" in stats
        assert "platform" in stats
        assert "stats" in stats
        assert stats["enabled"] is True


class TestLocationService:
    """位置服务测试"""

    @pytest.fixture
    def config(self) -> None:
        """测试配置"""
        return {
            "location_service": {
                "enabled": True,
                "gps_enabled": True,
                "indoor_positioning_enabled": True,
            }
        }

    @pytest.fixture
    def location_service(self, config):
        """创建位置服务实例"""
        return LocationService(config)

    def test_service_initialization(self, location_service):
        """测试服务初始化"""
        assert location_service.enabled is True
        assert location_service.gps_enabled is True
        assert location_service.indoor_positioning_enabled is True
        assert location_service.location_history == {}
        assert location_service.current_locations == {}

    @pytest.mark.asyncio
    async def test_get_current_location(self, location_service):
        """测试获取当前位置"""
        location = await location_service.get_current_location("test_user")

        assert location is not None
        assert isinstance(location, Location)
        assert location.coordinate.latitude is not None
        assert location.coordinate.longitude is not None
        assert location.location_type in [
            LocationType.OUTDOOR,
            LocationType.INDOOR,
            LocationType.UNKNOWN,
        ]

    @pytest.mark.asyncio
    async def test_create_navigation_route(self, location_service):
        """测试创建导航路线"""
        # 首先获取当前位置
        current_location = await location_service.get_current_location("test_user")
        assert current_location is not None

        # 创建目标位置
        dest_coordinate = Coordinate(latitude=39.9042, longitude=116.4074)
        dest_location = Location(
            coordinate=dest_coordinate, location_type=LocationType.UNKNOWN
        )

        # 创建路线
        route = await location_service.create_navigation_route(
            "test_user", current_location, dest_location, NavigationMode.WALKING
        )

        assert route is not None
        assert route.start_location == current_location
        assert route.end_location == dest_location
        assert route.navigation_mode == NavigationMode.WALKING
        assert len(route.instructions) > 0

    def test_calculate_distance(self, location_service):
        """测试距离计算"""
        # 北京天安门到故宫的距离（大约1公里）
        distance = location_service._calculate_distance(
            39.9042, 116.4074, 39.9163, 116.3972  # 天安门  # 故宫
        )

        assert 800 < distance < 1200  # 距离应该在800-1200米之间

    @pytest.mark.asyncio
    async def test_reverse_geocoding(self, location_service):
        """测试反向地理编码"""
        coordinate = Coordinate(latitude=39.9042, longitude=116.4074)
        address = await location_service.get_reverse_geocoding(coordinate)

        assert address is not None
        assert isinstance(address, str)
        assert len(address) > 0

    def test_add_geofence(self, location_service):
        """测试添加地理围栏"""
        center = Coordinate(latitude=39.9042, longitude=116.4074)
        success = location_service.add_geofence(
            "test_user", "home", center, 100.0, "家"
        )

        assert success is True
        assert "home" in location_service.geofences
        assert "test_user" in location_service.user_geofences
        assert "home" in location_service.user_geofences["test_user"]

    def test_get_location_history(self, location_service):
        """测试获取位置历史"""
        # 添加一些历史位置
        location = Location(
            coordinate=Coordinate(latitude=39.9042, longitude=116.4074),
            location_type=LocationType.OUTDOOR,
        )
        location_service._add_to_history("test_user", location)

        history = location_service.get_location_history("test_user")

        assert len(history) == 1
        assert history[0] == location

    def test_get_stats(self, location_service):
        """测试获取统计信息"""
        stats = location_service.get_stats()

        assert "enabled" in stats
        assert "gps_enabled" in stats
        assert "indoor_positioning_enabled" in stats
        assert "active_users" in stats
        assert "total_geofences" in stats


class TestSensorManager:
    """传感器管理器测试"""

    @pytest.fixture
    def config(self) -> None:
        """测试配置"""
        return {
            "sensor_manager": {
                "enabled": True,
                "sensors": {
                    "accelerometer": {
                        "enabled": True,
                        "sampling_rate": 50.0,
                        "buffer_size": 100,
                        "filters": ["low_pass"],
                    },
                    "light": {"enabled": True, "sampling_rate": 5.0, "buffer_size": 50},
                    "microphone": {
                        "enabled": True,
                        "sampling_rate": 10.0,
                        "buffer_size": 100,
                    },
                },
            }
        }

    @pytest.fixture
    def sensor_manager(self, config):
        """创建传感器管理器实例"""
        return SensorManager(config)

    def test_service_initialization(self, sensor_manager):
        """测试服务初始化"""
        assert sensor_manager.enabled is True
        assert len(sensor_manager.sensor_configs) > 0
        assert len(sensor_manager.sensor_handlers) > 0
        assert SensorType.ACCELEROMETER in sensor_manager.sensor_configs
        assert SensorType.LIGHT in sensor_manager.sensor_configs

    @pytest.mark.asyncio
    async def test_start_sensor(self, sensor_manager):
        """测试启动传感器"""
        success = await sensor_manager.start_sensor(SensorType.ACCELEROMETER)

        assert success is True
        assert (
            sensor_manager.get_sensor_status(SensorType.ACCELEROMETER).value == "active"
        )

    @pytest.mark.asyncio
    async def test_stop_sensor(self, sensor_manager):
        """测试停止传感器"""
        # 先启动传感器
        await sensor_manager.start_sensor(SensorType.ACCELEROMETER)

        # 然后停止
        success = await sensor_manager.stop_sensor(SensorType.ACCELEROMETER)

        assert success is True
        assert (
            sensor_manager.get_sensor_status(SensorType.ACCELEROMETER).value
            == "inactive"
        )

    def test_get_latest_reading(self, sensor_manager):
        """测试获取最新传感器读数"""
        # 模拟添加一些传感器数据
        reading = SensorReading(
            sensor_type=SensorType.ACCELEROMETER,
            timestamp=time.time(),
            values=[1.0, 2.0, 9.8],
            accuracy=0.1,
        )
        sensor_manager._store_reading(SensorType.ACCELEROMETER, reading)

        latest = sensor_manager.get_latest_reading(SensorType.ACCELEROMETER)

        assert latest is not None
        assert latest.sensor_type == SensorType.ACCELEROMETER
        assert len(latest.values) == 3

    def test_get_readings(self, sensor_manager):
        """测试获取多个传感器读数"""
        # 添加多个读数
        for i in range(5):
            reading = SensorReading(
                sensor_type=SensorType.LIGHT,
                timestamp=time.time() + i,
                values=[100.0 + i * 10],
                accuracy=1.0,
            )
            sensor_manager._store_reading(SensorType.LIGHT, reading)

        readings = sensor_manager.get_readings(SensorType.LIGHT, count=3)

        assert len(readings) == 3
        assert all(r.sensor_type == SensorType.LIGHT for r in readings)

    def test_apply_calibration(self, sensor_manager):
        """测试传感器校准"""
        reading = SensorReading(
            sensor_type=SensorType.ACCELEROMETER,
            timestamp=time.time(),
            values=[1.0, 2.0, 9.8],
            accuracy=0.1,
        )

        calibration = {"offset_0": 0.1, "offset_1": 0.2, "scale_0": 1.1, "scale_1": 1.2}

        calibrated = sensor_manager._apply_calibration(reading, calibration)

        assert calibrated.values[0] == (1.0 - 0.1) * 1.1  # 应用偏移和缩放
        assert calibrated.values[1] == (2.0 - 0.2) * 1.2
        assert calibrated.values[2] == 9.8  # 没有校准参数，保持原值

    def test_register_callback(self, sensor_manager):
        """测试注册数据回调"""
        callback_called = False

        def test_callback(sensor_type, data):
            nonlocal callback_called
            callback_called = True

        sensor_manager.register_callback(SensorType.ACCELEROMETER, test_callback)

        # 触发回调
        sensor_manager._trigger_callbacks(SensorType.ACCELEROMETER, {"test": "data"})

        assert callback_called is True

    def test_get_all_sensor_status(self, sensor_manager):
        """测试获取所有传感器状态"""
        status = sensor_manager.get_all_sensor_status()

        assert isinstance(status, dict)
        assert len(status) > 0
        assert "accelerometer" in status
        assert "light" in status

    def test_get_stats(self, sensor_manager):
        """测试获取统计信息"""
        stats = sensor_manager.get_stats()

        assert "total_readings" in stats
        assert "readings_per_sensor" in stats
        assert "errors_per_sensor" in stats
        assert "average_latency" in stats

    @pytest.mark.asyncio
    async def test_shutdown(self, sensor_manager):
        """测试关闭传感器管理器"""
        # 启动一些传感器
        await sensor_manager.start_sensor(SensorType.ACCELEROMETER)
        await sensor_manager.start_sensor(SensorType.LIGHT)

        # 关闭管理器
        await sensor_manager.shutdown()

        # 验证所有传感器都已停止
        assert sensor_manager.stop_event.is_set()


class TestIntegration:
    """集成测试"""

    @pytest.fixture
    def full_config(self) -> None:
        """完整的测试配置"""
        return {
            "desktop_automation": {
                "enabled": True,
                "security_policy": {
                    "max_actions_per_minute": 60,
                    "allowed_apps": [],
                    "blocked_areas": [],
                },
            },
            "location_service": {
                "enabled": True,
                "gps_enabled": True,
                "indoor_positioning_enabled": True,
            },
            "sensor_manager": {
                "enabled": True,
                "sensors": {
                    "accelerometer": {
                        "enabled": True,
                        "sampling_rate": 50.0,
                        "buffer_size": 100,
                    },
                    "gps": {"enabled": True, "sampling_rate": 1.0, "buffer_size": 100},
                },
            },
        }

    def test_all_services_initialization(self, full_config):
        """测试所有服务的初始化"""
        desktop_service = DesktopAutomationService(full_config)
        location_service = LocationService(full_config)
        sensor_manager = SensorManager(full_config)

        assert desktop_service.enabled is True
        assert location_service.enabled is True
        assert sensor_manager.enabled is True

    @pytest.mark.asyncio
    async def test_location_aware_desktop_automation(self, full_config):
        """测试位置感知的桌面自动化"""
        location_service = LocationService(full_config)
        desktop_service = DesktopAutomationService(full_config)

        # 获取当前位置
        location = await location_service.get_current_location("test_user")
        assert location is not None

        # 基于位置执行桌面操作
        action = DesktopAction(
            action_type=ActionType.CLICK,
            target=Point(x=100, y=200),
            parameters={"location_context": location.location_type.value},
        )

        result = await desktop_service.execute_action(action, "test_user")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_sensor_based_automation(self, full_config):
        """测试基于传感器的自动化"""
        sensor_manager = SensorManager(full_config)
        desktop_service = DesktopAutomationService(full_config)

        # 启动传感器
        await sensor_manager.start_sensor(SensorType.ACCELEROMETER)

        # 模拟传感器数据触发的自动化操作
        reading = SensorReading(
            sensor_type=SensorType.ACCELEROMETER,
            timestamp=time.time(),
            values=[15.0, 2.0, 9.8],  # 高加速度，可能表示设备被摇晃
            accuracy=0.1,
        )
        sensor_manager._store_reading(SensorType.ACCELEROMETER, reading)

        # 基于传感器数据执行操作
        action = DesktopAction(
            action_type=ActionType.CLICK,
            target=Point(x=100, y=200),
            parameters={"trigger": "motion_detected"},
        )

        result = await desktop_service.execute_action(action, "test_user")
        assert result.success is True


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
