#!/usr/bin/env python

"""
预约存储库
负责医疗预约数据的存储和检索
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from internal.domain.models import AppointmentStatus
from pkg.utils.config_loader import get_config

logger = logging.getLogger(__name__)

class AppointmentRepository:
    """预约存储库"""

    def __init__(self):
        """初始化预约存储库"""
        self.config = get_config()
        self.db_config = self.config.get_section("database")

        # 初始化PostgreSQL连接
        postgres_config = self.db_config.get("postgres", {})
        postgres_url = f"postgresql+asyncpg://{postgres_config.get('user')}:{postgres_config.get('password')}@{postgres_config.get('host')}:{postgres_config.get('port')}/{postgres_config.get('database')}"

        self.engine = create_async_engine(postgres_url)
        self.async_session = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

        # 初始化MongoDB连接
        mongodb_config = self.db_config.get("mongodb", {})
        mongodb_uri = mongodb_config.get("uri")
        mongodb_db = mongodb_config.get("database")

        self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_uri)
        self.mongo_db = self.mongo_client[mongodb_db]
        self.appointments_collection = self.mongo_db["appointments"]

        logger.info("预约存储库初始化完成")

    async def create_appointment(self, appointment_data: dict[str, Any]) -> str:
        """
        创建预约

        Args:
            appointment_data: 预约数据

        Returns:
            str: 预约ID
        """
        try:
            # 生成预约ID（如果没有提供）
            if "id" not in appointment_data:
                appointment_data["_id"] = str(uuid.uuid4())
            else:
                appointment_data["_id"] = appointment_data.pop("id")

            # 添加创建时间和更新时间
            current_time = datetime.now().isoformat()
            appointment_data["created_at"] = current_time
            appointment_data["updated_at"] = current_time

            # 插入数据
            result = await self.appointments_collection.insert_one(appointment_data)

            # 返回预约ID
            return str(result.inserted_id)

        except Exception as e:
            logger.error(f"创建预约失败: {e!s}", exc_info=True)
            raise

    async def get_appointment_by_id(
        self, appointment_id: str
    ) -> dict[str, Any] | None:
        """
        根据ID获取预约

        Args:
            appointment_id: 预约ID

        Returns:
            Optional[Dict[str, Any]]: 预约信息
        """
        try:
            # 查询条件
            query = {"_id": appointment_id}

            # 执行查询
            appointment = await self.appointments_collection.find_one(query)

            # 处理结果
            if appointment:
                appointment["id"] = str(appointment.pop("_id"))
                return appointment

            return None

        except Exception as e:
            logger.error(f"查询预约失败: {e!s}", exc_info=True)
            return None

    async def update_appointment(
        self, appointment_id: str, appointment_data: dict[str, Any]
    ) -> bool:
        """
        更新预约

        Args:
            appointment_id: 预约ID
            appointment_data: 更新的预约数据

        Returns:
            bool: 更新是否成功
        """
        try:
            # 更新时间
            appointment_data["updated_at"] = datetime.now().isoformat()

            # 执行更新
            result = await self.appointments_collection.update_one(
                {"_id": appointment_id}, {"$set": appointment_data}
            )

            # 判断是否成功
            return result.modified_count > 0

        except Exception as e:
            logger.error(f"更新预约失败: {e!s}", exc_info=True)
            return False

    async def delete_appointment(self, appointment_id: str) -> bool:
        """
        删除预约

        Args:
            appointment_id: 预约ID

        Returns:
            bool: 删除是否成功
        """
        try:
            # 执行删除
            result = await self.appointments_collection.delete_one(
                {"_id": appointment_id}
            )

            # 判断是否成功
            return result.deleted_count > 0

        except Exception as e:
            logger.error(f"删除预约失败: {e!s}", exc_info=True)
            return False

    async def get_appointments_by_user(
        self, user_id: str, status: str | None = None, page: int = 1, page_size: int = 20
    ) -> dict[str, Any]:
        """
        获取用户的预约列表

        Args:
            user_id: 用户ID
            status: 预约状态（可选）
            page: 页码
            page_size: 每页大小

        Returns:
            Dict[str, Any]: 预约列表和分页信息
        """
        try:
            # 查询条件
            query = {"user_id": user_id}
            if status:
                query["status"] = status

            # 计算跳过的文档数
            skip = (page - 1) * page_size

            # 执行查询
            cursor = (
                self.appointments_collection.find(query)
                .sort("created_at", -1)
                .skip(skip)
                .limit(page_size)
            )

            # 获取结果
            appointments = await cursor.to_list(length=page_size)

            # 查询总数
            total_count = await self.appointments_collection.count_documents(query)

            # 计算总页数
            total_pages = (total_count + page_size - 1) // page_size

            # 处理结果
            for appointment in appointments:
                appointment["id"] = str(appointment.pop("_id"))

            # 构建响应
            return {
                "appointments": appointments,
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
            }

        except Exception as e:
            logger.error(f"查询用户预约失败: {e!s}", exc_info=True)
            return {
                "appointments": [],
                "page": page,
                "page_size": page_size,
                "total_count": 0,
                "total_pages": 0,
            }

    async def get_appointments_by_doctor(
        self, doctor_id: str, status: str | None = None, page: int = 1, page_size: int = 20
    ) -> dict[str, Any]:
        """
        获取医生的预约列表

        Args:
            doctor_id: 医生ID
            status: 预约状态（可选）
            page: 页码
            page_size: 每页大小

        Returns:
            Dict[str, Any]: 预约列表和分页信息
        """
        try:
            # 查询条件
            query = {"doctor_id": doctor_id}
            if status:
                query["status"] = status

            # 计算跳过的文档数
            skip = (page - 1) * page_size

            # 执行查询
            cursor = (
                self.appointments_collection.find(query)
                .sort("created_at", -1)
                .skip(skip)
                .limit(page_size)
            )

            # 获取结果
            appointments = await cursor.to_list(length=page_size)

            # 查询总数
            total_count = await self.appointments_collection.count_documents(query)

            # 计算总页数
            total_pages = (total_count + page_size - 1) // page_size

            # 处理结果
            for appointment in appointments:
                appointment["id"] = str(appointment.pop("_id"))

            # 构建响应
            return {
                "appointments": appointments,
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
            }

        except Exception as e:
            logger.error(f"查询医生预约失败: {e!s}", exc_info=True)
            return {
                "appointments": [],
                "page": page,
                "page_size": page_size,
                "total_count": 0,
                "total_pages": 0,
            }

    async def get_appointments_by_time(
        self, doctor_id: str, time_slot: str
    ) -> list[dict[str, Any]]:
        """
        获取指定时间段的预约

        Args:
            doctor_id: 医生ID
            time_slot: 时间段

        Returns:
            List[Dict[str, Any]]: 预约列表
        """
        try:
            # 查询条件
            query = {
                "doctor_id": doctor_id,
                "$or": [
                    {"preferred_time": {"$regex": f"^{time_slot}"}},
                    {"confirmed_time": {"$regex": f"^{time_slot}"}},
                ],
                "status": {
                    "$in": [
                        AppointmentStatus.CONFIRMED.value,
                        AppointmentStatus.PENDING.value,
                    ]
                },
            }

            # 执行查询
            cursor = self.appointments_collection.find(query)

            # 获取结果
            appointments = await cursor.to_list(length=100)

            # 处理结果
            for appointment in appointments:
                appointment["id"] = str(appointment.pop("_id"))

            return appointments

        except Exception as e:
            logger.error(f"查询时间段预约失败: {e!s}", exc_info=True)
            return []

    async def update_appointment_status(self, appointment_id: str, status: str) -> bool:
        """
        更新预约状态

        Args:
            appointment_id: 预约ID
            status: 新状态

        Returns:
            bool: 更新是否成功
        """
        try:
            # 执行更新
            result = await self.appointments_collection.update_one(
                {"_id": appointment_id},
                {"$set": {"status": status, "updated_at": datetime.now().isoformat()}},
            )

            # 判断是否成功
            return result.modified_count > 0

        except Exception as e:
            logger.error(f"更新预约状态失败: {e!s}", exc_info=True)
            return False

    async def get_appointments_by_date_range(
        self, doctor_id: str, start_date: str, end_date: str
    ) -> list[dict[str, Any]]:
        """
        获取日期范围内的预约

        Args:
            doctor_id: 医生ID
            start_date: 开始日期（ISO 8601格式）
            end_date: 结束日期（ISO 8601格式）

        Returns:
            List[Dict[str, Any]]: 预约列表
        """
        try:
            # 查询条件
            query = {
                "doctor_id": doctor_id,
                "$or": [
                    {"preferred_time": {"$gte": start_date, "$lte": end_date}},
                    {"confirmed_time": {"$gte": start_date, "$lte": end_date}},
                ],
            }

            # 执行查询
            cursor = self.appointments_collection.find(query).sort("confirmed_time", 1)

            # 获取结果
            appointments = await cursor.to_list(length=1000)

            # 处理结果
            for appointment in appointments:
                appointment["id"] = str(appointment.pop("_id"))

            return appointments

        except Exception as e:
            logger.error(f"查询日期范围预约失败: {e!s}", exc_info=True)
            return []
