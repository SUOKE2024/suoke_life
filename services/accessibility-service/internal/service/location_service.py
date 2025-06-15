#!/usr/bin/env python

"""
位置服务 - 增强空间感知能力
支持GPS定位、室内定位、空间导航、地理围栏等功能
"""

import asyncio
import logging
import math
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class LocationType(Enum):
    """位置类型枚举"""

    OUTDOOR = "outdoor"
    INDOOR = "indoor"
    VEHICLE = "vehicle"
    UNDERGROUND = "underground"
    UNKNOWN = "unknown"


class NavigationMode(Enum):
    """导航模式枚举"""

    WALKING = "walking"
    DRIVING = "driving"
    CYCLING = "cycling"
    PUBLIC_TRANSPORT = "public_transport"
    WHEELCHAIR = "wheelchair"


@dataclass
class Coordinate:
    """地理坐标"""

    latitude: float
    longitude: float
    altitude: float | None = None
    accuracy: float | None = None
    timestamp: float | None = None


@dataclass
class Location:
    """位置信息"""

    coordinate: Coordinate
    location_type: LocationType
    address: str | None = None
    place_name: str | None = None
    indoor_info: dict[str, Any] | None = None
    confidence: float = 0.0


@dataclass
class NavigationInstruction:
    """导航指令"""

    instruction: str
    distance: float
    duration: float
    direction: str
    landmark: str | None = None
    audio_guidance: bytes | None = None


@dataclass
class Route:
    """路线信息"""

    start_location: Location
    end_location: Location
    waypoints: list[Location]
    instructions: list[NavigationInstruction]
    total_distance: float
    total_duration: float
    navigation_mode: NavigationMode


class LocationService:
    """位置服务核心类"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化位置服务

        Args:
            config: 服务配置
        """
        self.config = config
        self.enabled = config.get("location_service", {}).get("enabled", False)
        self.gps_enabled = config.get("location_service", {}).get("gps_enabled", True)
        self.indoor_positioning_enabled = config.get("location_service", {}).get(
            "indoor_positioning_enabled", True
        )

        # 位置历史记录
        self.location_history = {}  # user_id -> List[Location]
        self.current_locations = {}  # user_id -> Location

        # 地理围栏
        self.geofences = {}  # fence_id -> geofence_config
        self.user_geofences = {}  # user_id -> List[fence_id]

        # 导航会话
        self.navigation_sessions = {}  # session_id -> navigation_data

        # 位置提供者
        self.gps_provider = None
        self.indoor_provider = None
        self.network_provider = None

        # 缓存和性能优化
        self.location_cache = {}
        self.reverse_geocoding_cache = {}

        if self.enabled:
            self._initialize_location_providers()

        logger.info(
            f"位置服务初始化完成 - GPS: {self.gps_enabled}, 室内定位: {self.indoor_positioning_enabled}"
        )

    def _initialize_location_providers(self):
        """初始化位置提供者"""
        try:
            if self.gps_enabled:
                self.gps_provider = GPSProvider(self.config)

            if self.indoor_positioning_enabled:
                self.indoor_provider = IndoorPositioningProvider(self.config)

            self.network_provider = NetworkLocationProvider(self.config)

            logger.info("位置提供者初始化成功")
        except Exception as e:
            logger.error(f"位置提供者初始化失败: {e!s}")

    async def get_current_location(
        self, user_id: str, high_accuracy: bool = False
    ) -> Location | None:
        """
        获取当前位置

        Args:
            user_id: 用户ID
            high_accuracy: 是否需要高精度定位

        Returns:
            当前位置信息
        """
        if not self.enabled:
            logger.warning("位置服务未启用")
            return None

        try:
            # 尝试从多个位置提供者获取位置
            locations = []

            # GPS定位
            if self.gps_provider and (
                high_accuracy or self._is_outdoor_context(user_id)
            ):
                gps_location = await self.gps_provider.get_location()
                if gps_location:
                    locations.append(gps_location)

            # 室内定位
            if self.indoor_provider and self._is_indoor_context(user_id):
                indoor_location = await self.indoor_provider.get_location(user_id)
                if indoor_location:
                    locations.append(indoor_location)

            # 网络定位作为备选
            if not locations and self.network_provider:
                network_location = await self.network_provider.get_location()
                if network_location:
                    locations.append(network_location)

            # 选择最佳位置
            best_location = self._select_best_location(locations)

            if best_location:
                # 更新当前位置
                self.current_locations[user_id] = best_location

                # 添加到历史记录
                self._add_to_history(user_id, best_location)

                # 检查地理围栏
                await self._check_geofences(user_id, best_location)

                logger.info(
                    f"获取用户 {user_id} 当前位置成功: {best_location.coordinate.latitude}, {best_location.coordinate.longitude}"
                )
                return best_location
            else:
                logger.warning(f"无法获取用户 {user_id} 的位置信息")
                return None

        except Exception as e:
            logger.error(f"获取位置失败: {e!s}", exc_info=True)
            return None

    def _select_best_location(self, locations: list[Location]) -> Location | None:
        """选择最佳位置"""
        if not locations:
            return None

        if len(locations) == 1:
            return locations[0]

        # 根据精度和置信度选择最佳位置
        best_location = None
        best_score = 0

        for location in locations:
            # 计算位置质量分数
            accuracy_score = (
                1.0 / (location.coordinate.accuracy or 100)
                if location.coordinate.accuracy
                else 0.1
            )
            confidence_score = location.confidence
            freshness_score = (
                1.0
                if location.coordinate.timestamp
                and (time.time() - location.coordinate.timestamp) < 60
                else 0.5
            )

            total_score = (
                accuracy_score * 0.4 + confidence_score * 0.4 + freshness_score * 0.2
            )

            if total_score > best_score:
                best_score = total_score
                best_location = location

        return best_location

    def _is_outdoor_context(self, user_id: str) -> bool:
        """判断是否为户外环境"""
        # 基于历史位置、传感器数据等判断
        if user_id in self.current_locations:
            return self.current_locations[user_id].location_type == LocationType.OUTDOOR
        return True  # 默认假设为户外

    def _is_indoor_context(self, user_id: str) -> bool:
        """判断是否为室内环境"""
        if user_id in self.current_locations:
            return self.current_locations[user_id].location_type == LocationType.INDOOR
        return False

    def _add_to_history(self, user_id: str, location: Location):
        """添加位置到历史记录"""
        if user_id not in self.location_history:
            self.location_history[user_id] = []

        self.location_history[user_id].append(location)

        # 保持历史记录在合理范围内
        if len(self.location_history[user_id]) > 1000:
            self.location_history[user_id] = self.location_history[user_id][-500:]

    async def _check_geofences(self, user_id: str, location: Location):
        """检查地理围栏"""
        if user_id not in self.user_geofences:
            return

        for fence_id in self.user_geofences[user_id]:
            if fence_id in self.geofences:
                fence = self.geofences[fence_id]
                if self._is_inside_geofence(location, fence):
                    await self._trigger_geofence_event(
                        user_id, fence_id, "enter", location
                    )

    def _is_inside_geofence(self, location: Location, geofence: dict[str, Any]) -> bool:
        """检查位置是否在地理围栏内"""
        fence_center = geofence["center"]
        fence_radius = geofence["radius"]

        distance = self._calculate_distance(
            location.coordinate.latitude,
            location.coordinate.longitude,
            fence_center["latitude"],
            fence_center["longitude"],
        )

        return distance <= fence_radius

    def _calculate_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """计算两点间距离（米）"""
        # 使用Haversine公式
        R = 6371000  # 地球半径（米）

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    async def _trigger_geofence_event(
        self, user_id: str, fence_id: str, event_type: str, location: Location
    ):
        """触发地理围栏事件"""
        logger.info(f"地理围栏事件: 用户 {user_id}, 围栏 {fence_id}, 事件 {event_type}")
        # 这里可以发送通知或触发其他操作

    async def create_navigation_route(
        self,
        user_id: str,
        start_location: Location,
        end_location: Location,
        mode: NavigationMode,
        preferences: dict[str, Any] = None,
    ) -> Route | None:
        """
        创建导航路线

        Args:
            user_id: 用户ID
            start_location: 起始位置
            end_location: 目标位置
            mode: 导航模式
            preferences: 用户偏好

        Returns:
            路线信息
        """
        try:
            # 计算路线
            route = await self._calculate_route(
                start_location, end_location, mode, preferences
            )

            if route:
                # 创建导航会话
                session_id = f"{user_id}_{int(time.time())}"
                self.navigation_sessions[session_id] = {
                    "user_id": user_id,
                    "route": route,
                    "current_step": 0,
                    "started_at": time.time(),
                    "status": "active",
                }

                logger.info(f"为用户 {user_id} 创建导航路线成功，会话ID: {session_id}")
                return route
            else:
                logger.warning(f"无法为用户 {user_id} 计算路线")
                return None

        except Exception as e:
            logger.error(f"创建导航路线失败: {e!s}", exc_info=True)
            return None

    async def _calculate_route(
        self,
        start: Location,
        end: Location,
        mode: NavigationMode,
        preferences: dict[str, Any] = None,
    ) -> Route | None:
        """计算路线"""
        # 这里应该调用真实的路线规划服务（如Google Maps API、高德地图API等）
        # 目前返回模拟路线

        distance = self._calculate_distance(
            start.coordinate.latitude,
            start.coordinate.longitude,
            end.coordinate.latitude,
            end.coordinate.longitude,
        )

        # 模拟导航指令
        instructions = [
            NavigationInstruction(
                instruction="从起点出发", distance=0, duration=0, direction="forward"
            ),
            NavigationInstruction(
                instruction=f"直行 {distance:.0f} 米到达目的地",
                distance=distance,
                duration=distance / self._get_speed_for_mode(mode),
                direction="forward",
            ),
        ]

        route = Route(
            start_location=start,
            end_location=end,
            waypoints=[],
            instructions=instructions,
            total_distance=distance,
            total_duration=distance / self._get_speed_for_mode(mode),
            navigation_mode=mode,
        )

        return route

    def _get_speed_for_mode(self, mode: NavigationMode) -> float:
        """获取不同导航模式的平均速度（米/秒）"""
        speeds = {
            NavigationMode.WALKING: 1.4,  # 5 km/h
            NavigationMode.CYCLING: 4.2,  # 15 km/h
            NavigationMode.DRIVING: 13.9,  # 50 km/h
            NavigationMode.PUBLIC_TRANSPORT: 8.3,  # 30 km/h
            NavigationMode.WHEELCHAIR: 1.1,  # 4 km/h
        }
        return speeds.get(mode, 1.4)

    async def get_reverse_geocoding(self, coordinate: Coordinate) -> str | None:
        """
        反向地理编码 - 根据坐标获取地址

        Args:
            coordinate: 地理坐标

        Returns:
            地址字符串
        """
        cache_key = f"{coordinate.latitude:.6f},{coordinate.longitude:.6f}"

        # 检查缓存
        if cache_key in self.reverse_geocoding_cache:
            cached_result = self.reverse_geocoding_cache[cache_key]
            if time.time() - cached_result["timestamp"] < 3600:  # 1小时缓存
                return cached_result["address"]

        try:
            # 这里应该调用真实的反向地理编码服务
            # 目前返回模拟地址
            address = f"模拟地址 {coordinate.latitude:.4f}, {coordinate.longitude:.4f}"

            # 缓存结果
            self.reverse_geocoding_cache[cache_key] = {
                "address": address,
                "timestamp": time.time(),
            }

            return address

        except Exception as e:
            logger.error(f"反向地理编码失败: {e!s}")
            return None

    def add_geofence(
        self,
        user_id: str,
        fence_id: str,
        center: Coordinate,
        radius: float,
        name: str = None,
    ) -> bool:
        """
        添加地理围栏

        Args:
            user_id: 用户ID
            fence_id: 围栏ID
            center: 围栏中心坐标
            radius: 围栏半径（米）
            name: 围栏名称

        Returns:
            是否添加成功
        """
        try:
            geofence = {
                "id": fence_id,
                "name": name or fence_id,
                "center": {"latitude": center.latitude, "longitude": center.longitude},
                "radius": radius,
                "created_at": time.time(),
            }

            self.geofences[fence_id] = geofence

            if user_id not in self.user_geofences:
                self.user_geofences[user_id] = []

            if fence_id not in self.user_geofences[user_id]:
                self.user_geofences[user_id].append(fence_id)

            logger.info(f"为用户 {user_id} 添加地理围栏 {fence_id} 成功")
            return True

        except Exception as e:
            logger.error(f"添加地理围栏失败: {e!s}")
            return False

    def get_location_history(self, user_id: str, limit: int = 100) -> list[Location]:
        """获取位置历史记录"""
        if user_id in self.location_history:
            return self.location_history[user_id][-limit:]
        return []

    def get_stats(self) -> dict[str, Any]:
        """获取服务统计信息"""
        return {
            "enabled": self.enabled,
            "gps_enabled": self.gps_enabled,
            "indoor_positioning_enabled": self.indoor_positioning_enabled,
            "active_users": len(self.current_locations),
            "total_geofences": len(self.geofences),
            "active_navigation_sessions": len(
                [
                    s
                    for s in self.navigation_sessions.values()
                    if s["status"] == "active"
                ]
            ),
            "cache_size": len(self.reverse_geocoding_cache),
        }


# 位置提供者类
class GPSProvider:
    """GPS位置提供者"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.enabled = True

    async def get_location(self) -> Location | None:
        """获取GPS位置"""
        try:
            # 在实际实现中，这里会调用系统GPS API
            # 目前返回模拟位置
            await asyncio.sleep(0.1)  # 模拟GPS定位延迟

            coordinate = Coordinate(
                latitude=39.9042 + (time.time() % 100) * 0.0001,  # 模拟位置变化
                longitude=116.4074 + (time.time() % 100) * 0.0001,
                accuracy=5.0,
                timestamp=time.time(),
            )

            return Location(
                coordinate=coordinate,
                location_type=LocationType.OUTDOOR,
                confidence=0.9,
            )

        except Exception as e:
            logger.error(f"GPS定位失败: {e!s}")
            return None


class IndoorPositioningProvider:
    """室内定位提供者"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.enabled = True

    async def get_location(self, user_id: str) -> Location | None:
        """获取室内位置"""
        try:
            # 在实际实现中，这里会使用WiFi、蓝牙信标、UWB等技术
            # 目前返回模拟室内位置
            await asyncio.sleep(0.05)  # 模拟室内定位延迟

            coordinate = Coordinate(
                latitude=39.9042,
                longitude=116.4074,
                accuracy=2.0,
                timestamp=time.time(),
            )

            indoor_info = {
                "building": "索克生活大厦",
                "floor": 3,
                "room": "会议室A",
                "zone": "东区",
            }

            return Location(
                coordinate=coordinate,
                location_type=LocationType.INDOOR,
                indoor_info=indoor_info,
                confidence=0.8,
            )

        except Exception as e:
            logger.error(f"室内定位失败: {e!s}")
            return None


class NetworkLocationProvider:
    """网络位置提供者"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.enabled = True

    async def get_location(self) -> Location | None:
        """获取网络位置"""
        try:
            # 在实际实现中，这里会基于IP地址、WiFi网络等进行定位
            # 目前返回模拟网络位置
            await asyncio.sleep(0.02)  # 模拟网络定位延迟

            coordinate = Coordinate(
                latitude=39.9042,
                longitude=116.4074,
                accuracy=100.0,  # 网络定位精度较低
                timestamp=time.time(),
            )

            return Location(
                coordinate=coordinate,
                location_type=LocationType.UNKNOWN,
                confidence=0.6,
            )

        except Exception as e:
            logger.error(f"网络定位失败: {e!s}")
            return None
