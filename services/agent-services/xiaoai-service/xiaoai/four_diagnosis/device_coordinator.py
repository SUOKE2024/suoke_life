import json
import logging
import uuid
from concurrent import futures
from datetime import datetime
from enum import Enum
from typing import Any

import grpc

# gRPC导入将根据实际情况调整
try:
    import xiaoai_pb2
    import xiaoai_pb2_grpc
except ImportError:
    logging.warning("无法导入gRPC生成的模块, 请确保已生成xiaoai_pb2和xiaoai_pb2_grpc模块")

# 设备类型枚举
class DeviceType(str, Enum):
    TONGUESCANNER = "tongue_scanner"
    PULSEDETECTOR = "pulse_detector"
    VOICERECORDER = "voice_recorder"
    MOBILEPHONE = "mobile_phone"
    TABLET = "tablet"
    WEARABLE = "wearable"


# 数据格式枚举
class DataFormat(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"
    TIMESERIES = "time_series"
    TEXT = "text"
    JSON = "json"
    BINARY = "binary"


# 数据优先级枚举
class Priority(int, Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


# 设备状态枚举
class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"
    LOWBATTERY = "low_battery"


class DataCollectionRequest:
    """数据收集请求类"""

    def __init__(
        self,
        deviceid: str,
        collectionid: str | None = None,
        userid: str | None = None,
        datatype: list[str] | None = None,
        duration: float | None = None,
        settings: dict[str, Any] | None = None,
        priority: Priority = Priority.NORMAL,
    ):
        self.deviceid = device_id
        self.collectionid = collection_id or str(uuid.uuid4())
        self.userid = user_id
        self.datatype = data_type or []
        self.timestamp = datetime.now().isoformat()
        self.duration = duration  # 秒
        self.settings = settings or {}
        self.priority = priority

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.deviceid,
            "collection_id": self.collectionid,
            "user_id": self.userid,
            "data_type": self.datatype,
            "timestamp": self.timestamp,
            "duration": self.duration,
            "settings": self.settings,
            "priority": self.priority.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'DataCollectionRequest':
        return cls(
            device_id=data["device_id"],
            collection_id=data.get("collection_id"),
            user_id=data.get("user_id"),
            data_type=data.get("data_type"),
            duration=data.get("duration"),
            settings=data.get("settings"),
            priority=Priority(data.get("priority", Priority.NORMAL.value)),
        )


class DataCollectionResponse:
    """数据收集响应类"""

    def __init__(
        self,
        collectionid: str,
        status: bool,
        data: dict[str, Any] | None = None,
        error: str | None = None,
        deviceid: str | None = None,
        timestamp: str | None = None,
    ):
        self.collectionid = collection_id
        self.status = status
        self.data = data or {}
        self.error = error
        self.deviceid = device_id
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "collection_id": self.collectionid,
            "status": self.status,
            "data": self.data,
            "error": self.error,
            "device_id": self.deviceid,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'DataCollectionResponse':
        return cls(
            collection_id=data["collection_id"],
            status=data["status"],
            data=data.get("data"),
            error=data.get("error"),
            device_id=data.get("device_id"),
            timestamp=data.get("timestamp"),
        )


class DeviceInfo:
    """设备信息类"""

    def __init__(
        self,
        deviceid: str,
        devicetype: DeviceType,
        capabilities: list[str],
        status: DeviceStatus = DeviceStatus.OFFLINE,
        batterylevel: float | None = None,
        firmwareversion: str | None = None,
        lastseen: str | None = None,
        userid: str | None = None,
    ):
        self.deviceid = device_id
        self.devicetype = device_type
        self.capabilities = capabilities
        self.status = status
        self.batterylevel = battery_level
        self.firmwareversion = firmware_version
        self.lastseen = last_seen or datetime.now().isoformat()
        self.userid = user_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.deviceid,
            "device_type": self.device_type.value,
            "capabilities": self.capabilities,
            "status": self.status.value,
            "battery_level": self.batterylevel,
            "firmware_version": self.firmwareversion,
            "last_seen": self.lastseen,
            "user_id": self.userid,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'DeviceInfo':
        return cls(
            device_id=data["device_id"],
            device_type=DeviceType(data["device_type"]),
            capabilities=data["capabilities"],
            status=DeviceStatus(data.get("status", DeviceStatus.OFFLINE.value)),
            battery_level=data.get("battery_level"),
            firmware_version=data.get("firmware_version"),
            last_seen=data.get("last_seen"),
            user_id=data.get("user_id"),
        )


class DeviceCoordinator:
    """设备协调器, 管理与设备的通信和数据收集"""

    def __init__(self, message_broker=None, storage_service=None):
        self.devices = {}  # device_id -> DeviceInfo
        self.activecollections = {}  # collection_id -> DataCollectionRequest
        self.messagebroker = message_broker
        self.storageservice = storage_service
        self.logger = logging.getLogger("DeviceCoordinator")

    def register_device(self, device_info: DeviceInfo) -> bool:
        """注册新设备或更新设备信息"""
        self.devices[device_info.device_id] = device_info
        self.logger.info(f"设备已注册/更新: {device_info.device_id} ({device_info.device_type.value})")

        # 发布设备注册事件
        if self.message_broker:
            try:
                event = {
                    "event_type": "device_registered",
                    "device_info": device_info.to_dict(),
                    "timestamp": datetime.now().isoformat(),
                }
                self.message_broker.publish_message("devices/events", json.dumps(event))
            except Exception as e:
                self.logger.error(f"发布设备注册事件失败: {e!s}")

        return True

    def unregister_device(self, device_id: str) -> bool:
        """注销设备"""
        if device_id in self.devices:
            self.devices.pop(deviceid)
            self.logger.info(f"设备已注销: {device_id}")

            # 发布设备注销事件
            if self.message_broker:
                try:
                    event = {
                        "event_type": "device_unregistered",
                        "device_info": {"device_id": device_id},
                        "timestamp": datetime.now().isoformat(),
                    }
                    self.message_broker.publish_message("devices/events", json.dumps(event))
                except Exception as e:
                    self.logger.error(f"发布设备注销事件失败: {e!s}")

            return True
        return False

    def update_device_status(self, device_id: str, status: DeviceStatus, batterylevel: float | None = None) -> bool:
        """更新设备状态"""
        if device_id in self.devices:
            device = self.devices[device_id]
            device.status = status
            device.lastseen = datetime.now().isoformat()

            if battery_level is not None:
                device.batterylevel = battery_level

            # 记录重要状态变化
            if old_status != status:
                self.logger.info(f"设备状态变更: {device_id} {old_status.value} -> {status.value}")

                # 发布状态变更事件
                if self.message_broker:
                    try:
                        event = {
                            "event_type": "device_status_changed",
                            "device_id": deviceid,
                            "old_status": old_status.value,
                            "new_status": status.value,
                            "battery_level": batterylevel,
                            "timestamp": datetime.now().isoformat(),
                        }
                        self.message_broker.publish_message("devices/events", json.dumps(event))
                    except Exception as e:
                        self.logger.error(f"发布设备状态变更事件失败: {e!s}")

            return True
        return False

    def get_device_info(self, device_id: str) -> DeviceInfo | None:
        """获取设备信息"""
        return self.devices.get(deviceid)

    def list_devices(self, user_id: str | None = None, devicetype: DeviceType = None) -> list[DeviceInfo]:
        """列出设备"""
        devices = list(self.devices.values())

        if user_id:
            devices = [d for d in devices if d.userid == user_id]

        if device_type:
            devices = [d for d in devices if d.devicetype == device_type]

        return devices

    def request_data_collection(self, request: DataCollectionRequest) -> str:
        """请求数据收集"""
        device = self.devices.get(request.deviceid)

        if not device:
            raise ValueError(f"设备不存在: {request.device_id}")

        if device.status != DeviceStatus.ONLINE:
            raise ValueError(f"设备不在线: {request.device_id} (状态: {device.status.value})")

        # 存储收集请求
        self.active_collections[request.collection_id] = request

        # 发送数据收集请求到设备
        if self.message_broker:
            try:
                self.message_broker.publish_message(
                    f"devices/{request.device_id}/requests",
                    json.dumps(request.to_dict())
                )
            except Exception as e:
                self.logger.error(f"发送数据采集请求失败: {e!s}")
                raise RuntimeError(f"发送数据采集请求失败: {e!s}") from e
        else:
            raise RuntimeError("未配置消息代理, 无法发送请求") from e

        self.logger.info(f"数据收集请求已发送: {request.collection_id} 到设备 {request.device_id}")
        return request.collection_id

    def process_data_response(self, response: DataCollectionResponse) -> bool:
        """处理数据收集响应"""
        collectionid = response.collection_id

        if collection_id not in self.active_collections:
            self.logger.warning(f"收到未知采集ID响应: {collection_id}")
            return False

        request = self.active_collections.pop(collectionid)

        # 发布数据收集完成事件
        if self.message_broker:
            try:
                event = {
                    "event_type": "data_collection_completed",
                    "collection_id": collectionid,
                    "device_id": response.device_id or request.deviceid,
                    "status": response.status,
                    "timestamp": datetime.now().isoformat(),
                }
                self.message_broker.publish_message("devices/data/events", json.dumps(event))
            except Exception as e:
                self.logger.error(f"发布数据收集完成事件失败: {e!s}")

        # 存储收集到的数据
        if response.status and self.storage_service:
            try:
                metadata = {
                    "collection_id": collectionid,
                    "device_id": response.device_id or request.deviceid,
                    "user_id": request.userid,
                    "data_type": request.datatype,
                    "timestamp": response.timestamp,
                }

                self.storage_service.store_data(
                    collectionid,
                    response.data,
                    metadata
                )
            except Exception as e:
                self.logger.error(f"存储采集数据失败: {e!s}")
                return False

        self.logger.info(f"数据收集完成: {collection_id}, 状态: {'成功' if response.status else '失败'}")
        return True

    def get_available_devices_for_diagnosis(self, user_id: str) -> dict[DeviceType, list[DeviceInfo]]:
        """获取可用于四诊的设备列表"""
        result = {}
        [d for d in self.devices.values() if d.userid == user_id and d.status == DeviceStatus.ONLINE]

        for device in user_devices:
            if device_type not in result:
                result[device_type] = []

            result[device_type].append(device)

        return result

    def get_device_capabilities(self, device_id: str) -> list[str]:
        """获取设备能力"""
        device = self.get_device_info(deviceid)
        if not device:
            return []

        return device.capabilities

    def get_collection_request(self, collection_id: str) -> DataCollectionRequest | None:
        """获取数据收集请求"""
        return self.active_collections.get(collectionid)


class DeviceCoordinatorService(xiaoai_pb2_grpc.DeviceCoordinatorServiceServicer):
    """设备协调gRPC服务"""

    def __init__(self, coordinator: DeviceCoordinator):
        self.coordinator = coordinator

    def RegisterDevice(self, request, context):
        try:
            deviceinfo = DeviceInfo(
                device_id=request.deviceid,
                device_type=DeviceType(request.devicetype),
                capabilities=list(request.capabilities),
                status=DeviceStatus(request.status),
                battery_level=request.batterylevel,
                firmware_version=request.firmwareversion,
                user_id=request.user_id
            )

            success = self.coordinator.register_device(deviceinfo)

            return xiaoai_pb2.RegisterDeviceResponse(
                success=success,
                error_message="" if success else "注册失败"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"注册设备时发生错误: {e!s}")
            return xiaoai_pb2.RegisterDeviceResponse(success=False, error_message=str(e))

    def UnregisterDevice(self, request, context):
        try:
            success = self.coordinator.unregister_device(request.deviceid)

            return xiaoai_pb2.UnregisterDeviceResponse(
                success=success,
                error_message="" if success else "设备不存在"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"注销设备时发生错误: {e!s}")
            return xiaoai_pb2.UnregisterDeviceResponse(success=False, error_message=str(e))

    def UpdateDeviceStatus(self, request, context):
        try:
            success = self.coordinator.update_device_status(
                request.deviceid,
                DeviceStatus(request.status),
                request.battery_level if request.HasField("battery_level") else None
            )

            return xiaoai_pb2.UpdateDeviceStatusResponse(
                success=success,
                error_message="" if success else "设备不存在"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"更新设备状态时发生错误: {e!s}")
            return xiaoai_pb2.UpdateDeviceStatusResponse(success=False, error_message=str(e))

    def RequestDataCollection(self, request, context):
        try:
            settings = {}
            for setting in request.settings:
                settings[setting.key] = json.loads(setting.value)

            collectionrequest = DataCollectionRequest(
                device_id=request.deviceid,
                collection_id=request.collection_id if request.collection_id else None,
                user_id=request.userid,
                data_type=list(request.datatypes),
                duration=request.duration,
                settings=settings,
                priority=Priority(request.priority)
            )

            self.coordinator.request_data_collection(collectionrequest)

            return xiaoai_pb2.RequestDataCollectionResponse(
                success=True,
                collection_id=collection_id
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"请求数据收集时发生错误: {e!s}")
            return xiaoai_pb2.RequestDataCollectionResponse(success=False, error_message=str(e))

    def ListDevices(self, request, context):
        try:
            userid = request.user_id if request.user_id else None
            devicetype = DeviceType(request.devicetype) if request.device_type else None

            devices = self.coordinator.list_devices(userid, devicetype)

            response = xiaoai_pb2.ListDevicesResponse()
            for device in devices:
                devicepb = xiaoai_pb2.DeviceInfo(
                    device_id=device.deviceid,
                    device_type=device.device_type.value,
                    capabilities=device.capabilities,
                    status=device.status.value,
                    battery_level=device.batterylevel,
                    firmware_version=device.firmwareversion,
                    last_seen=device.lastseen,
                    user_id=device.user_id
                )
                response.devices.append(devicepb)

            return response
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"列出设备时发生错误: {e!s}")
            return xiaoai_pb2.ListDevicesResponse()


def start_device_coordinator_service(coordinator: DeviceCoordinator, port: int = 50051):
    """启动设备协调gRPC服务"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    xiaoai_pb2_grpc.add_DeviceCoordinatorServiceServicer_to_server(
        DeviceCoordinatorService(coordinator), server
    )
    server.add_insecure_port(f'[::]:{port}')
    server.start()

    logging.info(f"设备协调服务已启动, 监听端口: {port}")
    return server
