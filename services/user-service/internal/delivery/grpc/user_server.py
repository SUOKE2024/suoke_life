"""
用户服务gRPC服务器实现

该模块实现了用户服务的gRPC接口。
"""
import logging
from uuid import UUID

import grpc
from google.protobuf import empty_pb2, timestamp_pb2

from internal.model.user import (BindDeviceRequest, CreateUserRequest,
                          UpdateUserPreferencesRequest, UpdateUserRequest,
                          UserRole, UserStatus, VerifyUserRequest)
from internal.repository.sqlite_user_repository import (DeviceAlreadyBoundError,
                                                 DeviceNotFoundError,
                                                 UserAlreadyExistsError,
                                                 UserNotFoundError)
from internal.service.user_service import UserService
from protobuf.suoke.user.v1 import user_pb2, user_pb2_grpc

logger = logging.getLogger(__name__)

class UserServicer(user_pb2_grpc.UserServiceServicer):
    """用户服务gRPC实现"""

    def __init__(self, user_service: UserService):
        """
        初始化用户服务gRPC实现
        
        Args:
            user_service: 用户服务
        """
        self.user_service = user_service
    
    async def CreateUser(self, request, context):
        """创建用户"""
        try:
            create_request = CreateUserRequest(
                username=request.username,
                email=request.email,
                phone=request.phone if request.phone else None,
                full_name=request.full_name if request.full_name else None,
                password=request.password,
                metadata=dict(request.metadata) if request.metadata else {}
            )
            
            user = await self.user_service.create_user(create_request)
            return self._user_to_pb(user)
        except UserAlreadyExistsError as e:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(str(e))
            return user_pb2.UserResponse()
        except Exception as e:
            logger.exception(f"创建用户时发生错误: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部服务错误: {e}")
            return user_pb2.UserResponse()
    
    async def GetUser(self, request, context):
        """获取用户信息"""
        try:
            user = await self.user_service.get_user(request.user_id)
            return self._user_to_pb(user)
        except UserNotFoundError as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return user_pb2.UserResponse()
        except Exception as e:
            logger.exception(f"获取用户时发生错误: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部服务错误: {e}")
            return user_pb2.UserResponse()
    
    async def UpdateUser(self, request, context):
        """更新用户信息"""
        try:
            update_request = UpdateUserRequest(
                username=request.username if request.username else None,
                email=request.email if request.email else None,
                phone=request.phone if request.phone else None,
                full_name=request.full_name if request.full_name else None,
                metadata=dict(request.metadata) if request.metadata else None
            )
            
            user = await self.user_service.update_user(request.user_id, update_request)
            return self._user_to_pb(user)
        except UserNotFoundError as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return user_pb2.UserResponse()
        except UserAlreadyExistsError as e:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(str(e))
            return user_pb2.UserResponse()
        except Exception as e:
            logger.exception(f"更新用户时发生错误: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部服务错误: {e}")
            return user_pb2.UserResponse()
    
    async def DeleteUser(self, request, context):
        """删除用户"""
        try:
            await self.user_service.delete_user(request.user_id)
            return empty_pb2.Empty()
        except UserNotFoundError as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return empty_pb2.Empty()
        except Exception as e:
            logger.exception(f"删除用户时发生错误: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部服务错误: {e}")
            return empty_pb2.Empty()
    
    async def GetUserHealthSummary(self, request, context):
        """获取用户健康摘要"""
        try:
            health_summary = await self.user_service.get_user_health_summary(request.user_id)
            return self._health_summary_to_pb(health_summary)
        except UserNotFoundError as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return user_pb2.UserHealthSummaryResponse()
        except Exception as e:
            logger.exception(f"获取用户健康摘要时发生错误: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部服务错误: {e}")
            return user_pb2.UserHealthSummaryResponse()
    
    async def VerifyUserIdentity(self, request, context):
        """验证用户身份"""
        try:
            verify_request = VerifyUserRequest(
                user_id=UUID(request.user_id),
                token=request.token
            )
            
            result = await self.user_service.verify_user_identity(verify_request)
            
            response = user_pb2.VerifyUserResponse(
                is_valid=result.is_valid
            )
            
            for role in result.roles:
                response.roles.append(self._user_role_to_pb(role))
            
            for key, value in result.permissions.items():
                response.permissions[key] = value
            
            return response
        except Exception as e:
            logger.exception(f"验证用户身份时发生错误: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部服务错误: {e}")
            return user_pb2.VerifyUserResponse(is_valid=False)
    
    async def UpdateUserPreferences(self, request, context):
        """更新用户偏好设置"""
        try:
            update_request = UpdateUserPreferencesRequest(
                preferences=dict(request.preferences) if request.preferences else {}
            )
            
            user = await self.user_service.update_user_preferences(
                request.user_id, update_request
            )
            
            return self._user_to_pb(user)
        except UserNotFoundError as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return user_pb2.UserResponse()
        except Exception as e:
            logger.exception(f"更新用户偏好设置时发生错误: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部服务错误: {e}")
            return user_pb2.UserResponse()
    
    async def BindDevice(self, request, context):
        """绑定设备"""
        try:
            bind_request = BindDeviceRequest(
                device_id=request.device_id,
                device_type=request.device_type,
                device_name=request.device_name if request.device_name else None,
                device_metadata=dict(request.device_metadata) if request.device_metadata else {}
            )
            
            result = await self.user_service.bind_device(request.user_id, bind_request)
            
            response = user_pb2.BindDeviceResponse(
                success=result.success,
                binding_id=result.binding_id,
                binding_time=timestamp_pb2.Timestamp()
            )
            response.binding_time.FromDatetime(result.binding_time)
            
            return response
        except UserNotFoundError as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return user_pb2.BindDeviceResponse(success=False)
        except DeviceAlreadyBoundError as e:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(str(e))
            return user_pb2.BindDeviceResponse(success=False)
        except Exception as e:
            logger.exception(f"绑定设备时发生错误: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部服务错误: {e}")
            return user_pb2.BindDeviceResponse(success=False)
    
    async def GetUserDevices(self, request, context):
        """获取用户设备列表"""
        try:
            result = await self.user_service.get_user_devices(request.user_id)
            
            response = user_pb2.UserDevicesResponse(
                user_id=result.user_id
            )
            
            for device in result.devices:
                device_pb = user_pb2.DeviceInfo(
                    device_id=device.device_id,
                    device_type=device.device_type,
                    device_name=device.device_name or "",
                    binding_id=device.binding_id,
                    is_active=device.is_active
                )
                
                # 设置时间戳
                binding_time_pb = timestamp_pb2.Timestamp()
                binding_time_pb.FromDatetime(device.binding_time)
                device_pb.binding_time.CopyFrom(binding_time_pb)
                
                if device.last_active_time:
                    last_active_time_pb = timestamp_pb2.Timestamp()
                    last_active_time_pb.FromDatetime(device.last_active_time)
                    device_pb.last_active_time.CopyFrom(last_active_time_pb)
                
                # 添加元数据
                for key, value in device.device_metadata.items():
                    device_pb.device_metadata[key] = value
                
                response.devices.append(device_pb)
            
            return response
        except UserNotFoundError as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return user_pb2.UserDevicesResponse()
        except Exception as e:
            logger.exception(f"获取用户设备列表时发生错误: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部服务错误: {e}")
            return user_pb2.UserDevicesResponse()
    
    def _user_to_pb(self, user):
        """将用户模型转换为Protobuf对象"""
        response = user_pb2.UserResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            phone=user.phone or "",
            full_name=user.full_name or "",
            status=self._user_status_to_pb(user.status)
        )
        
        # 设置时间戳
        created_at_pb = timestamp_pb2.Timestamp()
        created_at_pb.FromDatetime(user.created_at)
        response.created_at.CopyFrom(created_at_pb)
        
        updated_at_pb = timestamp_pb2.Timestamp()
        updated_at_pb.FromDatetime(user.updated_at)
        response.updated_at.CopyFrom(updated_at_pb)
        
        # 添加元数据
        for key, value in user.metadata.items():
            response.metadata[key] = value
        
        # 添加角色
        for role in user.roles:
            response.roles.append(self._user_role_to_pb(role))
        
        # 添加偏好设置
        for key, value in user.preferences.items():
            response.preferences[key] = value
        
        return response
    
    def _health_summary_to_pb(self, health_summary):
        """将健康摘要模型转换为Protobuf对象"""
        response = user_pb2.UserHealthSummaryResponse(
            user_id=health_summary.user_id,
            health_score=health_summary.health_score
        )
        
        # 设置体质类型
        if health_summary.dominant_constitution:
            response.dominant_constitution = self._constitution_type_to_pb(
                health_summary.dominant_constitution
            )
        
        # 设置最近评估日期
        if health_summary.last_assessment_date:
            last_assessment_date_pb = timestamp_pb2.Timestamp()
            last_assessment_date_pb.FromDatetime(health_summary.last_assessment_date)
            response.last_assessment_date.CopyFrom(last_assessment_date_pb)
        
        # 添加健康指标
        for metric in health_summary.recent_metrics:
            metric_pb = user_pb2.HealthMetric(
                metric_name=metric.metric_name,
                value=metric.value,
                unit=metric.unit or ""
            )
            
            timestamp_pb = timestamp_pb2.Timestamp()
            timestamp_pb.FromDatetime(metric.timestamp)
            metric_pb.timestamp.CopyFrom(timestamp_pb)
            
            response.recent_metrics.append(metric_pb)
        
        # 添加体质评分
        for constitution_type, score in health_summary.constitution_scores.items():
            response.constitution_scores[constitution_type] = score
        
        return response
    
    def _user_status_to_pb(self, status: UserStatus) -> user_pb2.UserStatus:
        """将用户状态枚举转换为Protobuf枚举"""
        mapping = {
            UserStatus.UNKNOWN: user_pb2.USER_STATUS_UNKNOWN,
            UserStatus.ACTIVE: user_pb2.USER_STATUS_ACTIVE,
            UserStatus.INACTIVE: user_pb2.USER_STATUS_INACTIVE,
            UserStatus.BANNED: user_pb2.USER_STATUS_BANNED,
            UserStatus.PENDING: user_pb2.USER_STATUS_PENDING
        }
        return mapping.get(status, user_pb2.USER_STATUS_UNKNOWN)
    
    def _user_role_to_pb(self, role: UserRole) -> user_pb2.UserRole:
        """将用户角色枚举转换为Protobuf枚举"""
        mapping = {
            UserRole.UNKNOWN: user_pb2.USER_ROLE_UNKNOWN,
            UserRole.USER: user_pb2.USER_ROLE_USER,
            UserRole.ADMIN: user_pb2.USER_ROLE_ADMIN,
            UserRole.DOCTOR: user_pb2.USER_ROLE_DOCTOR,
            UserRole.RESEARCHER: user_pb2.USER_ROLE_RESEARCHER
        }
        return mapping.get(role, user_pb2.USER_ROLE_UNKNOWN)
    
    def _constitution_type_to_pb(self, constitution_type) -> user_pb2.ConstitutionType:
        """将体质类型枚举转换为Protobuf枚举"""
        mapping = {
            "unknown": user_pb2.CONSTITUTION_TYPE_UNKNOWN,
            "balanced": user_pb2.CONSTITUTION_TYPE_BALANCED,
            "qi_deficiency": user_pb2.CONSTITUTION_TYPE_QI_DEFICIENCY,
            "yang_deficiency": user_pb2.CONSTITUTION_TYPE_YANG_DEFICIENCY,
            "yin_deficiency": user_pb2.CONSTITUTION_TYPE_YIN_DEFICIENCY,
            "phlegm_dampness": user_pb2.CONSTITUTION_TYPE_PHLEGM_DAMPNESS,
            "damp_heat": user_pb2.CONSTITUTION_TYPE_DAMP_HEAT,
            "blood_stasis": user_pb2.CONSTITUTION_TYPE_BLOOD_STASIS,
            "qi_depression": user_pb2.CONSTITUTION_TYPE_QI_DEPRESSION,
            "special": user_pb2.CONSTITUTION_TYPE_SPECIAL
        }
        return mapping.get(constitution_type, user_pb2.CONSTITUTION_TYPE_UNKNOWN) 