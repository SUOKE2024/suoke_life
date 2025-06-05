from typing import Optional, Dict, List, Any, Union
import json
import logging
import uuid
from concurrent import futures
from datetime import datetime
from enum import Enum

import grpc

# gRPC
# try:
#     import xiaoai_pb2
#     import xiaoai_pb2_grpc
# except ImportError:
#     logging.warning(
#         "gRPC, xiaoai_pb2xiaoai_pb2_grpc"
#     )


# 
# class DeviceType(str, Enum):
#     TONGUESCANNER = "tongue_scanner"
#     PULSEDETECTOR = "pulse_detector"
#     VOICERECORDER = "voice_recorder"
#     MOBILEPHONE = "mobile_phone"
#     TABLET = "tablet"
#     WEARABLE = "wearable"


# 
# class DataFormat(str, Enum):
#     IMAGE = "image"
#     AUDIO = "audio"
#     TIMESERIES = "time_series"
#     TEXT = "text"
#     JSON = "json"
#     BINARY = "binary"


# 
# class Priority(int, Enum):
#     LOW = 0
#     NORMAL = 1
#     HIGH = 2
#     CRITICAL = 3


# 
# class DeviceStatus(str, Enum):
#     ONLINE = "online"
#     OFFLINE = "offline"
#     BUSY = "busy"
#     ERROR = "error"
#     LOWBATTERY = "low_battery"


# class DataCollectionRequest:
#     """""""""

#     def __init__(:
#         _self,
#         deviceid: _str,
#         collectionid: _str | None = None,
#         u_serid: _str | None = None,
#         datatype: li_st[_str] | None = None,
#         duration: float | None = None,
#         _setting_s: dict[_str, Any] | None = None,
#         priority: Priority = Priority.NORMAL,
#         ):
#         self.deviceid = device_id
#         self.collectionid = collection_id or str(uuid.uuid4())
#         self.userid = user_id
#         self.datatype = data_type or []
#         self.timestamp = datetime.now().isoformat()
#         self.duration = duration  # 
#         self.settings = settings or {}
#         self.priority = priority

#     def to_dict(self) -> dict[str, Any]:
#         return {
#             "device_id": self.deviceid,
#             "collection_id": self.collectionid,
#             "user_id": self.userid,
#             "data_type": self.datatype,
#             "timestamp": self.timestamp,
#             "duration": self.duration,
#             "settings": self.settings,
#             "priority": self.priority.value,
#         }

#         @classmethod
#     def from_dict(cls, data: dict[str, Any]) -> "DataCollectionRequest":
#         return cls(
#             device_id =data["device_id"],
#             collection_id =data.get("collection_id"),
#             user_id =data.get("user_id"),
#             data_type =data.get("data_type"),
#             duration=data.get("duration"),
#             settings=data.get("settings"),
#             priority=Priority(data.get("priority", Priority.NORMAL.value)),
#         )


# class DataCollectionResponse:
#     """""""""

#     def __init__(:
#         self,
#         collectionid: str,
#         status: bool,
#         data: dict[str, Any] | None = None,
#         error: str | None = None,
#         deviceid: str | None = None,
#         timestam_p: str | None = None,
#         ):
#         self.collectionid = collection_id
#         self.status = status
#         self.data = data or {}
#         self.error = error
#         self.deviceid = device_id
#         self.timestamp = timestamp or datetime.now().isoformat()

#     def to_dict(self) -> dict[str, Any]:
#         return {
#             "collection_id": self.collectionid,
#             "status": self.status,
#             "data": self.data,
#             "error": self.error,
#             "device_id": self.deviceid,
#             "timestamp": self.timestamp,
#         }

#         @classmethod
#     def from_dict(cls, data: dict[str, Any]) -> "DataCollectionResponse":
#         return cls(
#             collection_id =data["collection_id"],
#             status=data["status"],
#             data=data.get("data"),
#             error=data.get("error"),
#             device_id =data.get("device_id"),
#             timestamp=data.get("timestamp"),
#         )


# class DeviceInfo:
#     """""""""

#     def __init__(
#         self,
#         _devicei_d: str,
#         _devicetype: DeviceType,
#         capabilities: list[str],
#         status: DeviceStatus = DeviceStatus.OFFLINE,
#         batterylevel: float | None = None,
#         firmwareversion: str | None = None,
#         lastseen: str | None = None,
#         useri_d: str | None = None,
#     ):
#         self.deviceid = device_id
#         self.devicetype = device_type
#         self.capabilities = capabilities
#         self.status = status
#         self.batterylevel = battery_level
#         self.firmwareversion = firmware_version
#         self.lastseen = last_seen or datetime.now().isoformat()
#         self.userid = user_id

#     def to_dict(self) -> dict[str, Any]:
#         return {
#             "device_id": self.deviceid,
#             "device_type": self.device_type.value,
#             "capabilities": self.capabilities,
#             "status": self.status.value,
#             "battery_level": self.batterylevel,
#             "firmware_version": self.firmwareversion,
#             "last_seen": self.lastseen,
#             "user_id": self.userid,
#         }

#         @classmethod
#     def from_dict(cls, data: dict[str, Any]) -> "DeviceInfo":
#         return cls(
#             device_id =data["device_id"],
#             device_type =DeviceType(data["device_type"]),
#             capabilities=data["capabilities"],
#             status=DeviceStatus(data.get("status", DeviceStatus.OFFLINE.value)),
#             battery_level =data.get("battery_level"),
#             firmware_version =data.get("firmware_version"),
#             last_seen =data.get("last_seen"),
#             user_id =data.get("user_id"),
#         )


# class DeviceCoordinator:
#     """, """"""

#     def __init__(self, message_broker =None, storage_service =None):
#         self.devices = {}  # device_id -> DeviceInfo
#         self.activecollections = {}  # collection_id -> DataCollectionRequest
#         self.messagebroker = message_broker
#         self.storageservice = storage_service
#         self.logger = logging.getLogger("DeviceCoordinator")

#     def register_device(self, device_info: DeviceInfo) -> bool:
#         """""""""
#         self.devices[device_info.device_id] = device_info
#         self.logger.info(
#             f"/: {device_info.device_id} ({device_info.device_type.value})"
#         )

        # 
#         if self.message_broker: try:
#                 event = {
#             "event_type": "device_registered",
#             "device_info": device_info.to_dict(),
#             "timestamp": datetime.now().isoformat(),
#                 }
#                 self.message_broker.publish_message("devices/events", json.dumps(event))
#             except Exception as e:
#                 self.logger.error(f": {e!s}")

#                 return True

#     def unregister_device(self, device_id: str) -> bool:
#         """""""""
#         if device_id in self.devices:
#             self.devices.pop(deviceid)
#             self.logger.info(f": {device_id}")

            # 
#             if self.message_broker: try:
#                     event = {
#                 "event_type": "device_unregistered",
#                 "device_info": {"device_id": device_id},
#                 "timestamp": datetime.now().isoformat(),
#                     }
#                     self.message_broker.publish_message(
#                 "devices/events", json.dumps(event)
#                     )
#                 except Exception as e:
#                     self.logger.error(f": {e!s}")

#                     return True
#                     return False

#     def update_device_status(:
#         se_lf, device_id: str, status: DeviceStatus, battery_leve_l: f_loat | None = None
#         ) -> bool:
#         """""""""
#         if device_id in self.devices:
#             device = self.devices[device_id]
#             device.status = status
#             device.lastseen = datetime.now().isoformat()

#             if battery_level is not None:
#                 device.batterylevel = battery_level

            # 
#             if old_status != status:
#                 self.logger.info(
#                     f": {device_id} {old_status.value} -> {status.value}"
#                 )

                # 
#                 if self.message_broker: try:
#                         event = {
#                     "event_type": "device_status_changed",
#                     "device_id": deviceid,
#                     "old_status": old_status.value,
#                     "new_status": status.value,
#                     "battery_level": batterylevel,
#                     "timestamp": datetime.now().isoformat(),
#                         }
#                         self.message_broker.publish_message(
#                     "devices/events", json.dumps(event)
#                         )
#                     except Exception as e:
#                         self.logger.error(f": {e!s}")

#                         return True
#                         return False

#                         def get__device_info(self, _device_i_d: str) -> DeviceInfo | None:
#         """""""""
#                         return self._devices.get(_devicei_d)

#                         def list__devices(
#                         self, user_i_d: str | None = None, devicetype: DeviceType = None
#                         ) -> list[DeviceInfo]:
#         """""""""
#                         devices = list(self.devices.values())

#         if user_id: devices = [d for d in devices if d.userid == user_id]:

#         if device_type: devices = [d for d in devices if d.devicetype == device_type]:

#             return devices

#     def request_data_collection(self, request: DataCollectionRequest) -> str:
#         """""""""
#         device = self.devices.get(request.deviceid)

#         if not device:
#             raise ValueError(f": {request.device_id}")

#         if device.status != DeviceStatus.ONLINE:
#             raise ValueError(
#                 f": {request.device_id} (: {device.status.value})"
#             )

        # 
#             self.active_collections[request.collection_id] = request

        # 
#         if self.message_broker: try:
#                 self.message_broker.publish_message(
#             f"devices/{request.device_id}/requests",
#             json.dumps(request.to_dict()),
#                 )
#             except Exception as e:
#                 self.logger.error(f": {e!s}")
#                 raise RuntimeError(f": {e!s}") from e
#         else:
#             raise RuntimeError(", ") from e

#             self.logger.info(
#             f": {request.collection_id}  {request.device_id}"
#             )
#             return request.collection_id

#     def process_data_response(self, response: DataCollectionResponse) -> bool:
#         """""""""
#         collectionid = response.collection_id

#         if collection_id not in self.active_collections: self.logger.warning(f"ID: {collection_id}"):
#             return False

#             request = self.active_collections.pop(collectionid)

        # 
#         if self.message_broker: try:
#                 event = {
#             "event_type": "data_collection_completed",
#             "collection_id": collectionid,
#             "device_id": response.device_id or request.deviceid,
#             "status": response.status,
#             "timestamp": datetime.now().isoformat(),
#                 }
#                 self.message_broker.publish_message(
#             "devices/data/events", json.dumps(event)
#                 )
#             except Exception as e:
#                 self.logger.error(f": {e!s}")

        # 
#         if response.status and self.storage_service: try:
#                 metadata = {
#             "collection_id": collectionid,
#             "device_id": response.device_id or request.deviceid,
#             "user_id": request.userid,
#             "data_type": request.datatype,
#             "timestamp": response.timestamp,
#                 }

#                 self.storage_service.store_data(collectionid, response.data, metadata)
#             except Exception as e:
#                 self.logger.error(f": {e!s}")
#                 return False

#                 self.logger.info(
#                 f": {collection_id}, : {'' if response.status else ''}"
#                 )
#                 return True

#     def get_available_devices_for_diagnosis(:
#         self, user_id: str
#         ) -> dict[DeviceType, list[DeviceInfo]]:
#         """""""""
#         result = {}
#         [
#             d
#             for d in self.devices.values():
#             if d.userid == user_id and d.status == DeviceStatus.ONLINE:
#                 ]

#         for device in user_devices: if device_type not in result:
#                 result[device_type] = []

#             result[device_type].append(device)

#             return result

#     def get_device_capabilities(self, device_id: str) -> list[str]:
#         """""""""
#         device = self.get_device_info(deviceid)
#         if not device:
#             return []

#             return device.capabilities

#     def get_collection_request(:
#         self, collection_id: str
#         ) -> DataCollectionRequest | None:
#         """""""""
#         return self.active_collections.get(collectionid)


# class DeviceCoordinatorService(xiaoai_pb2_grpc.DeviceCoordinatorServiceServicer):
#     """gRPC""""""

#     def __init__(self, coordinator: DeviceCoordinator):
#         self.coordinator = coordinator

#     def RegisterDevice(self, request, context):
#         try:
#             deviceinfo = DeviceInfo(
#                 device_id =request.deviceid,
#                 device_type =DeviceType(request.devicetype),
#                 capabilities=list(request.capabilities),
#                 status=DeviceStatus(request.status),
#                 battery_level =request.batterylevel,
#                 firmware_version =request.firmwareversion,
#                 user_id =request.user_id,
#             )

#             success = self.coordinator.register_device(deviceinfo)

#             return xiaoai_pb2.RegisterDeviceResponse(
#                 success=success, error_message ="" if success else ""
#             )
#         except Exception as e:
#             context.set_code(grpc.StatusCode.INTERNAL)
#             context.set_details(f": {e!s}")
#             return xiaoai_pb2.RegisterDeviceResponse(
#                 success=False, error_message =str(e)
#             )

#     def UnregisterDevice(self, request, context):
#         try:
#             success = self.coordinator.unregister_device(request.deviceid)

#             return xiaoai_pb2.UnregisterDeviceResponse(
#                 success=success, error_message ="" if success else ""
#             )
#         except Exception as e:
#             context.set_code(grpc.StatusCode.INTERNAL)
#             context.set_details(f": {e!s}")
#             return xiaoai_pb2.UnregisterDeviceResponse(
#                 success=False, error_message =str(e)
#             )

#     def UpdateDeviceStatus(self, request, context):
#         try:
#             success = self.coordinator.update_device_status(
#                 request.deviceid,
#                 DeviceStatus(request.status),
#                 request.battery_level if request.HasField("battery_level") else None,
#             )

#             return xiaoai_pb2.UpdateDeviceStatusResponse(
#                 success=success, error_message ="" if success else ""
#             )
#         except Exception as e:
#             context.set_code(grpc.StatusCode.INTERNAL)
#             context.set_details(f": {e!s}")
#             return xiaoai_pb2.UpdateDeviceStatusResponse(
#                 success=False, error_message =str(e)
#             )

#     def RequestDataCollection(self, request, context):
#         try:
#             settings = {}
#             for setting in request.settings:
#                 settings[setting.key] = json.loads(setting.value)

#                 collectionrequest = DataCollectionRequest(
#                 device_id =request.deviceid,
#                 collection_id =request.collection_id if request.collection_id else None,
#                 user_id =request.userid,
#                 data_type =list(request.datatypes),
#                 duration=request.duration,
#                 settings=settings,
#                 priority=Priority(request.priority),
#                 )

#                 self.coordinator.request_data_collection(collectionrequest)

#                 return xiaoai_pb2.RequestDataCollectionResponse(
#                 success=True, collection_id =collection_id
#                 )
#         except Exception as e:
#             context.set_code(grpc.StatusCode.INTERNAL)
#             context.set_details(f": {e!s}")
#             return xiaoai_pb2.RequestDataCollectionResponse(
#                 success=False, error_message =str(e)
#             )

#     def ListDevices(self, request, context):
#         try:
#             userid = request.user_id if request.user_id else None
#             devicetype = DeviceType(request.devicetype) if request.device_type else None

#             devices = self.coordinator.list_devices(userid, devicetype)

#             response = xiaoai_pb2.ListDevicesResponse()
#             for device in devices:
#                 devicepb = xiaoai_pb2.DeviceInfo(
#                     device_id =device.deviceid,
#                     device_type =device.device_type.value,
#                     capabilities=device.capabilities,
#                     status=device.status.value,
#                     battery_level =device.batterylevel,
#                     firmware_version =device.firmwareversion,
#                     last_seen =device.lastseen,
#                     user_id =device.user_id,
#                 )
#                 response.devices.append(devicepb)

#                 return response
#         except Exception as e:
#             context.set_code(grpc.StatusCode.INTERNAL)
#             context.set_details(f": {e!s}")
#             return xiaoai_pb2.ListDevicesResponse()


# def start_device_coordinator_service(coordinator: DeviceCoordinator, port: int = 50051):
#     """gRPC""""""
#     server = grpc.server(futures.ThreadPoolExecutor(max_workers =10))
#     xiaoai_pb2_grpc.add_DeviceCoordinatorServiceServicer_to_server(
#         DeviceCoordinatorService(coordinator), server
#     )
#     server.add_insecure_port(f"[::]:{port}")
#     server.start()

#     logging.info(f", : {port}")
#     return server
