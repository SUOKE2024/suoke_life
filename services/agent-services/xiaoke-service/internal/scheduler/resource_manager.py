#!/usr/bin/env python

"""
资源管理器
负责医疗资源的调度、预约管理和资源分配
"""

import logging
import time
import uuid
from datetime import datetime
from typing import Any

from internal.domain.models import AppointmentStatus
from internal.repository.appointment_repository import AppointmentRepository
from internal.repository.resource_repository import ResourceRepository
from pkg.utils.config_loader import get_config
from pkg.utils.metrics import get_metrics_collector

logger = logging.getLogger(__name__)


class ResourceManager:
    """医疗资源管理器，负责资源调度与预约管理"""

    def __init__(self):
        """初始化资源管理器"""
        self.config = get_config()
        self.metrics = get_metrics_collector()

        # 加载调度配置
        self.scheduler_config = self.config.get_section("scheduler.resource_matching")
        self.weights = self.scheduler_config.get(
            "weights",
            {
                "constitution_match": 0.4,
                "location_proximity": 0.2,
                "rating": 0.2,
                "availability": 0.2,
            },
        )

        self.max_recommendations = self.scheduler_config.get("max_recommendations", 5)

        # 初始化存储库
        self.resource_repo = ResourceRepository()
        self.appointment_repo = AppointmentRepository()

        logger.info("资源管理器初始化完成，使用权重: %s", self.weights)

    async def schedule_resources(
        self,
        user_id: str,
        resource_type: str,
        constitution_type: str,
        location: str,
        requirements: list[str],
        page_size: int = 10,
        page_number: int = 1,
    ) -> dict[str, Any]:
        """
        调度医疗资源，根据用户需求和体质类型匹配最佳资源

        Args:
            user_id: 用户ID
            resource_type: 资源类型（如DOCTOR, HOSPITAL等）
            constitution_type: 用户体质类型
            location: 位置信息
            requirements: 特殊需求列表
            page_size: 每页结果数
            page_number: 页码

        Returns:
            Dict[str, Any]: 调度结果，包含匹配的资源列表
        """
        try:
            # 记录请求指标
            self.metrics.increment_resource_request_count(resource_type)
            start_time = time.time()

            # 获取所有可用资源
            all_resources = await self.resource_repo.get_resources_by_type(
                resource_type
            )

            # 根据匹配算法对资源进行评分和排序
            scored_resources = self._score_resources(
                resources=all_resources,
                constitution_type=constitution_type,
                location=location,
                requirements=requirements,
            )

            # 分页处理
            total_count = len(scored_resources)
            page_count = (total_count + page_size - 1) // page_size

            start_idx = (page_number - 1) * page_size
            end_idx = min(start_idx + page_size, total_count)

            paged_resources = scored_resources[start_idx:end_idx]

            # 记录响应指标
            response_time = time.time() - start_time
            self.metrics.record_resource_scheduling_time(response_time)

            # 构建响应
            return {
                "request_id": str(uuid.uuid4()),
                "resources": paged_resources,
                "total_count": total_count,
                "page_count": page_count,
            }

        except Exception as e:
            logger.error(f"资源调度失败: {e!s}", exc_info=True)
            raise

    async def manage_appointment(
        self,
        user_id: str,
        doctor_id: str,
        appointment_type: str,
        preferred_time: str,
        symptoms: str,
        constitution_type: str,
        metadata: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        管理医疗预约

        Args:
            user_id: 用户ID
            doctor_id: 医生ID
            appointment_type: 预约类型
            preferred_time: 首选时间（ISO 8601格式）
            symptoms: 症状描述
            constitution_type: 体质类型
            metadata: 元数据

        Returns:
            Dict[str, Any]: 预约结果
        """
        try:
            # 记录请求指标
            self.metrics.increment_appointment_request_count(appointment_type)
            start_time = time.time()

            # 验证医生是否存在
            doctor = await self.resource_repo.get_resource_by_id(doctor_id)
            if not doctor:
                raise ValueError(f"未找到医生: {doctor_id}")

            # 验证时间格式
            try:
                preferred_datetime = datetime.fromisoformat(preferred_time)
            except ValueError:
                raise ValueError(f"时间格式无效: {preferred_time}，应为ISO 8601格式")

            # 检查医生可用性
            is_available = await self._check_doctor_availability(
                doctor_id, preferred_datetime
            )

            # 创建预约
            appointment_id = str(uuid.uuid4())
            status = (
                AppointmentStatus.CONFIRMED
                if is_available
                else AppointmentStatus.PENDING
            )

            # 如果是线上咨询，生成会议链接
            meeting_link = ""
            if appointment_type == "ONLINE_CONSULTATION" and is_available:
                meeting_link = (
                    f"https://meeting.suoke.life/consultation/{appointment_id}"
                )

            # 确认时间，如果不可用，则推荐下一个可用时间
            confirmed_time = preferred_time
            if not is_available:
                next_available = await self._find_next_available_time(
                    doctor_id, preferred_datetime
                )
                if next_available:
                    confirmed_time = next_available.isoformat()

            # 保存预约
            await self.appointment_repo.create_appointment(
                {
                    "id": appointment_id,
                    "user_id": user_id,
                    "doctor_id": doctor_id,
                    "type": appointment_type,
                    "preferred_time": preferred_time,
                    "confirmed_time": confirmed_time,
                    "symptoms": symptoms,
                    "constitution_type": constitution_type,
                    "status": status.value,
                    "meeting_link": meeting_link,
                    "metadata": metadata or {},
                    "created_at": datetime.now().isoformat(),
                }
            )

            # 记录响应指标
            response_time = time.time() - start_time
            self.metrics.record_appointment_processing_time(response_time)

            # 构建响应
            return {
                "appointment_id": appointment_id,
                "status": status.value,
                "confirmed_time": confirmed_time,
                "doctor_name": doctor.get("name", ""),
                "location": doctor.get("location", ""),
                "meeting_link": meeting_link,
                "metadata": metadata or {},
            }

        except Exception as e:
            logger.error(f"预约管理失败: {e!s}", exc_info=True)
            raise

    def _score_resources(
        self,
        resources: list[dict[str, Any]],
        constitution_type: str,
        location: str,
        requirements: list[str],
    ) -> list[dict[str, Any]]:
        """
        对资源进行评分和排序

        Args:
            resources: 资源列表
            constitution_type: 体质类型
            location: 位置信息
            requirements: 特殊需求

        Returns:
            List[Dict[str, Any]]: 评分后的资源列表
        """
        scored_resources = []

        for resource in resources:
            # 计算各维度的匹配分数
            constitution_score = self._calculate_constitution_match(
                resource, constitution_type
            )
            location_score = self._calculate_location_proximity(resource, location)
            rating_score = float(resource.get("rating", 0)) / 5.0  # 假设评分满分为5
            availability_score = self._calculate_availability(resource)

            # 计算加权总分
            total_score = (
                self.weights["constitution_match"] * constitution_score
                + self.weights["location_proximity"] * location_score
                + self.weights["rating"] * rating_score
                + self.weights["availability"] * availability_score
            )

            # 添加额外需求的匹配情况
            requirement_match = self._check_requirements(resource, requirements)

            # 构建结果对象
            resource_result = resource.copy()
            resource_result["score"] = total_score
            resource_result["requirement_match"] = requirement_match

            scored_resources.append(resource_result)

        # 按分数降序排序
        scored_resources.sort(key=lambda x: x["score"], reverse=True)

        return scored_resources

    def _calculate_constitution_match(
        self, resource: dict[str, Any], constitution_type: str
    ) -> float:
        """计算资源与用户体质的匹配度"""
        # 获取资源支持的体质类型
        supported_types = resource.get("supported_constitution_types", [])

        # 如果资源没有体质匹配信息，返回中等分数
        if not supported_types:
            return 0.5

        # 如果完全匹配
        if constitution_type in supported_types:
            return 1.0

        # 如果支持所有体质
        if "ALL" in supported_types:
            return 0.8

        # 部分匹配的情况
        # 这里可以实现更复杂的匹配逻辑，例如基于中医体质理论的相关性计算
        return 0.3

    def _calculate_location_proximity(
        self, resource: dict[str, Any], location: str
    ) -> float:
        """计算位置接近度"""
        # 简化实现，实际应使用地理坐标计算距离
        if not location or not resource.get("location"):
            return 0.5

        if location == resource.get("location"):
            return 1.0

        # 这里可以实现更复杂的地理位置匹配算法
        # 例如基于省市区划分的层级匹配或地理坐标的距离计算
        return 0.4

    def _calculate_availability(self, resource: dict[str, Any]) -> float:
        """计算资源可用性分数"""
        available_times = resource.get("available_times", [])

        if not available_times:
            return 0.0

        # 计算可用时间段数量，越多分数越高
        return min(1.0, len(available_times) / 10.0)  # 假设10个时间段为满分

    def _check_requirements(
        self, resource: dict[str, Any], requirements: list[str]
    ) -> dict[str, bool]:
        """检查资源是否满足特殊需求"""
        result = {}
        specialties = resource.get("specialties", [])

        for req in requirements:
            result[req] = req in specialties

        return result

    async def _check_doctor_availability(
        self, doctor_id: str, preferred_time: datetime
    ) -> bool:
        """检查医生在指定时间是否可用"""
        # 获取医生可用时间
        doctor = await self.resource_repo.get_resource_by_id(doctor_id)
        available_times = doctor.get("available_times", [])

        # 检查预约时间是否在可用时段内
        preferred_time_str = preferred_time.strftime("%Y-%m-%dT%H:%M")
        for time_slot in available_times:
            if time_slot.startswith(preferred_time_str):
                # 检查该时间是否已被预约
                existing_appointments = (
                    await self.appointment_repo.get_appointments_by_time(
                        doctor_id, preferred_time_str
                    )
                )
                return len(existing_appointments) == 0

        return False

    async def _find_next_available_time(
        self, doctor_id: str, from_time: datetime
    ) -> datetime | None:
        """查找医生下一个可用时间"""
        # 获取医生可用时间
        doctor = await self.resource_repo.get_resource_by_id(doctor_id)
        available_times = doctor.get("available_times", [])

        # 按时间排序
        available_times.sort()

        # 寻找晚于from_time的第一个可用时间
        from_time_str = from_time.strftime("%Y-%m-%dT%H:%M")

        for time_slot in available_times:
            if time_slot > from_time_str:
                # 检查该时间是否已被预约
                existing_appointments = (
                    await self.appointment_repo.get_appointments_by_time(
                        doctor_id, time_slot
                    )
                )
                if len(existing_appointments) == 0:
                    return datetime.fromisoformat(time_slot)

        # 如果找不到可用时间，返回None
        return None
