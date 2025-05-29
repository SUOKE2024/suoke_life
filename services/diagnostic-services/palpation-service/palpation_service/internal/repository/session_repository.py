#!/usr/bin/env python

"""
会话存储库
负责管理切诊会话数据的存储与检索
"""

import logging
import time
from typing import Any

from pymongo import MongoClient

logger = logging.getLogger(__name__)


class SessionRepository:
    """会话存储库，管理脉诊会话数据"""

    def __init__(self, db_config):
        """
        初始化会话存储库

        Args:
            db_config: 数据库配置
        """
        self.db_config = db_config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db_client = self._init_db_client()
        self.db = self.db_client[db_config.get("name", "palpation_db")]

        # 获取集合名
        collections = db_config.get("collections", {})
        self.pulse_sessions_collection = self.db[collections.get("sessions", "pulse_sessions")]
        self.abdominal_analyses_collection = self.db[collections.get("analyses", "pulse_analyses")]
        self.skin_analyses_collection = self.db[collections.get("analyses", "pulse_analyses")]
        self.reports_collection = self.db[collections.get("reports", "palpation_reports")]

        # 创建索引
        self._create_indexes()

        logger.info("会话存储库初始化完成")

    def _init_db_client(self):
        """初始化数据库客户端"""
        # 构建连接字符串
        host = self.db_config.get("host", "localhost")
        port = self.db_config.get("port", 27017)
        username = self.db_config.get("username", "")
        password = self.db_config.get("password", "")

        if username and password:
            connection_string = f"mongodb://{username}:{password}@{host}:{port}/"
        else:
            connection_string = f"mongodb://{host}:{port}/"

        # 连接选项
        connection_options = {
            "serverSelectionTimeoutMS": self.db_config.get("timeout", 5000),
            "connectTimeoutMS": self.db_config.get("connect_timeout", 10000),
            "maxPoolSize": self.db_config.get("max_pool_size", 10),
            "minPoolSize": self.db_config.get("min_pool_size", 1),
        }

        try:
            client = MongoClient(connection_string, **connection_options)
            # 测试连接
            client.admin.command("ping")
            logger.info("MongoDB连接成功")
            return client
        except Exception as e:
            logger.error(f"MongoDB连接失败: {e}")
            raise

    def _create_indexes(self):
        """创建数据库索引"""
        try:
            # 脉诊会话索引
            self.pulse_sessions_collection.create_index([("session_id", 1)], unique=True)
            self.pulse_sessions_collection.create_index([("user_id", 1), ("created_at", -1)])
            self.pulse_sessions_collection.create_index([("status", 1)])

            # 腹诊分析索引
            self.abdominal_analyses_collection.create_index([("analysis_id", 1)], unique=True)
            self.abdominal_analyses_collection.create_index([("user_id", 1), ("created_at", -1)])

            # 皮肤触诊分析索引
            self.skin_analyses_collection.create_index([("analysis_id", 1)], unique=True)
            self.skin_analyses_collection.create_index([("user_id", 1), ("created_at", -1)])

            # 报告索引
            self.reports_collection.create_index([("report_id", 1)], unique=True)
            self.reports_collection.create_index([("user_id", 1), ("created_at", -1)])
            self.reports_collection.create_index([("analysis_id", 1)])

            logger.info("数据库索引创建完成")
        except Exception as e:
            logger.warning(f"创建索引时出现错误（可能索引已存在）: {e}")

    def create_session(self, session_id: str, session_data: dict[str, Any]) -> bool:
        """
        创建新的脉诊会话

        Args:
            session_id: 会话ID
            session_data: 会话数据

        Returns:
            创建是否成功
        """
        try:
            # 添加创建时间
            if "created_at" not in session_data:
                session_data["created_at"] = time.time()

            # 存储会话数据
            result = self.pulse_sessions_collection.insert_one(session_data)

            return result.acknowledged
        except Exception as e:
            logger.exception(f"创建脉诊会话失败: {e!s}")
            return False

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """
        获取脉诊会话

        Args:
            session_id: 会话ID

        Returns:
            会话数据，不存在时返回None
        """
        try:
            session = self.pulse_sessions_collection.find_one({"session_id": session_id})
            return session
        except Exception as e:
            logger.exception(f"获取脉诊会话失败: {e!s}")
            return None

    def update_session(self, session_id: str, session_data: dict[str, Any]) -> bool:
        """
        更新脉诊会话

        Args:
            session_id: 会话ID
            session_data: 新的会话数据

        Returns:
            更新是否成功
        """
        try:
            # 添加更新时间
            session_data["updated_at"] = time.time()

            # 更新会话数据
            result = self.pulse_sessions_collection.replace_one(
                {"session_id": session_id}, session_data
            )

            return result.acknowledged
        except Exception as e:
            logger.exception(f"更新脉诊会话失败: {e!s}")
            return False

    def delete_session(self, session_id: str) -> bool:
        """
        删除脉诊会话

        Args:
            session_id: 会话ID

        Returns:
            删除是否成功
        """
        try:
            result = self.pulse_sessions_collection.delete_one({"session_id": session_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.exception(f"删除脉诊会话失败: {e!s}")
            return False

    def get_user_sessions(
        self, user_id: str, limit: int = 10, skip: int = 0
    ) -> list[dict[str, Any]]:
        """
        获取用户的脉诊会话列表

        Args:
            user_id: 用户ID
            limit: 返回的最大会话数
            skip: 跳过的会话数

        Returns:
            会话列表
        """
        try:
            sessions = list(
                self.pulse_sessions_collection.find(
                    {"user_id": user_id}, {"data_packets": 0}  # 不返回数据包，减少数据量
                )
                .sort("created_at", -1)
                .skip(skip)
                .limit(limit)
            )

            return sessions
        except Exception as e:
            logger.exception(f"获取用户脉诊会话列表失败: {e!s}")
            return []

    def create_abdominal_analysis(self, analysis_id: str, analysis_data: dict[str, Any]) -> bool:
        """
        创建腹诊分析记录

        Args:
            analysis_id: 分析ID
            analysis_data: 分析数据

        Returns:
            创建是否成功
        """
        try:
            # 添加创建时间
            if "created_at" not in analysis_data:
                analysis_data["created_at"] = time.time()

            # 存储分析数据
            result = self.abdominal_analyses_collection.insert_one(analysis_data)

            return result.acknowledged
        except Exception as e:
            logger.exception(f"创建腹诊分析记录失败: {e!s}")
            return False

    def get_abdominal_analysis(self, analysis_id: str) -> dict[str, Any] | None:
        """
        获取腹诊分析记录

        Args:
            analysis_id: 分析ID

        Returns:
            分析数据，不存在时返回None
        """
        try:
            analysis = self.abdominal_analyses_collection.find_one({"analysis_id": analysis_id})
            return analysis
        except Exception as e:
            logger.exception(f"获取腹诊分析记录失败: {e!s}")
            return None

    def get_user_abdominal_analyses(
        self, user_id: str, limit: int = 10, skip: int = 0
    ) -> list[dict[str, Any]]:
        """
        获取用户的腹诊分析记录列表

        Args:
            user_id: 用户ID
            limit: 返回的最大记录数
            skip: 跳过的记录数

        Returns:
            分析记录列表
        """
        try:
            analyses = list(
                self.abdominal_analyses_collection.find({"user_id": user_id})
                .sort("created_at", -1)
                .skip(skip)
                .limit(limit)
            )

            return analyses
        except Exception as e:
            logger.exception(f"获取用户腹诊分析记录列表失败: {e!s}")
            return []

    def create_skin_analysis(self, analysis_id: str, analysis_data: dict[str, Any]) -> bool:
        """
        创建皮肤触诊分析记录

        Args:
            analysis_id: 分析ID
            analysis_data: 分析数据

        Returns:
            创建是否成功
        """
        try:
            # 添加创建时间
            if "created_at" not in analysis_data:
                analysis_data["created_at"] = time.time()

            # 存储分析数据
            result = self.skin_analyses_collection.insert_one(analysis_data)

            return result.acknowledged
        except Exception as e:
            logger.exception(f"创建皮肤触诊分析记录失败: {e!s}")
            return False

    def get_skin_analysis(self, analysis_id: str) -> dict[str, Any] | None:
        """
        获取皮肤触诊分析记录

        Args:
            analysis_id: 分析ID

        Returns:
            分析数据，不存在时返回None
        """
        try:
            analysis = self.skin_analyses_collection.find_one({"analysis_id": analysis_id})
            return analysis
        except Exception as e:
            logger.exception(f"获取皮肤触诊分析记录失败: {e!s}")
            return None

    def get_user_skin_analyses(
        self, user_id: str, limit: int = 10, skip: int = 0
    ) -> list[dict[str, Any]]:
        """
        获取用户的皮肤触诊分析记录列表

        Args:
            user_id: 用户ID
            limit: 返回的最大记录数
            skip: 跳过的记录数

        Returns:
            分析记录列表
        """
        try:
            analyses = list(
                self.skin_analyses_collection.find({"user_id": user_id})
                .sort("created_at", -1)
                .skip(skip)
                .limit(limit)
            )

            return analyses
        except Exception as e:
            logger.exception(f"获取用户皮肤触诊分析记录列表失败: {e!s}")
            return []

    def create_report(self, report_id: str, report_data: dict[str, Any]) -> bool:
        """
        创建切诊报告

        Args:
            report_id: 报告ID
            report_data: 报告数据

        Returns:
            创建是否成功
        """
        try:
            # 添加创建时间
            if "created_at" not in report_data:
                report_data["created_at"] = time.time()

            # 存储报告数据
            result = self.reports_collection.insert_one(report_data)

            return result.acknowledged
        except Exception as e:
            logger.exception(f"创建切诊报告失败: {e!s}")
            return False

    def get_report(self, report_id: str) -> dict[str, Any] | None:
        """
        获取切诊报告

        Args:
            report_id: 报告ID

        Returns:
            报告数据，不存在时返回None
        """
        try:
            report = self.reports_collection.find_one({"report_id": report_id})
            return report
        except Exception as e:
            logger.exception(f"获取切诊报告失败: {e!s}")
            return None

    def get_user_reports(
        self, user_id: str, limit: int = 10, skip: int = 0
    ) -> list[dict[str, Any]]:
        """
        获取用户的切诊报告列表

        Args:
            user_id: 用户ID
            limit: 返回的最大报告数
            skip: 跳过的报告数

        Returns:
            报告列表
        """
        try:
            reports = list(
                self.reports_collection.find({"user_id": user_id})
                .sort("created_at", -1)
                .skip(skip)
                .limit(limit)
            )

            return reports
        except Exception as e:
            logger.exception(f"获取用户切诊报告列表失败: {e!s}")
            return []

    def ping(self):
        """
        检查数据库连接状态

        Returns:
            bool: 如果数据库连接正常则返回True

        Raises:
            Exception: 如果数据库连接失败则抛出异常
        """
        try:
            # 执行简单的命令检查连接状态
            self.db.command("ping")
            return True
        except Exception as e:
            self.logger.error(f"数据库连接检查失败: {e}")
            raise

    def get_session_ids_by_timeframe(
        self, user_id: str, start_timestamp: int, end_timestamp: int
    ) -> list[str]:
        """
        根据时间范围获取会话ID列表

        Args:
            user_id: 用户ID
            start_timestamp: 开始时间戳
            end_timestamp: 结束时间戳

        Returns:
            会话ID列表
        """
        try:
            sessions = list(
                self.pulse_sessions_collection.find(
                    {
                        "user_id": user_id,
                        "created_at": {"$gte": start_timestamp, "$lte": end_timestamp},
                    },
                    {"session_id": 1},  # 只返回session_id字段
                )
            )

            return [session["session_id"] for session in sessions]
        except Exception as e:
            logger.exception(f"根据时间范围获取会话ID失败: {e!s}")
            return []

    def save_analysis_result(self, analysis_id: str, analysis_data: dict[str, Any]) -> bool:
        """
        保存综合分析结果

        Args:
            analysis_id: 分析ID
            analysis_data: 分析数据

        Returns:
            保存是否成功
        """
        try:
            # 添加创建时间
            if "created_at" not in analysis_data:
                analysis_data["created_at"] = time.time()

            # 保存到分析集合
            result = self.abdominal_analyses_collection.insert_one(analysis_data)

            return result.acknowledged
        except Exception as e:
            logger.exception(f"保存综合分析结果失败: {e!s}")
            return False

    def get_analysis_result(self, analysis_id: str) -> dict[str, Any] | None:
        """
        获取综合分析结果

        Args:
            analysis_id: 分析ID

        Returns:
            分析数据，不存在时返回None
        """
        try:
            # 从多个集合中查找
            analysis = self.abdominal_analyses_collection.find_one({"analysis_id": analysis_id})
            if analysis:
                return analysis

            # 尝试从报告集合查找
            report = self.reports_collection.find_one({"analysis_id": analysis_id})
            if report:
                return report

            return None
        except Exception as e:
            logger.exception(f"获取综合分析结果失败: {e!s}")
            return None

    def cleanup_old_sessions(self, days_to_keep: int = 30) -> int:
        """
        清理旧的会话数据

        Args:
            days_to_keep: 保留的天数

        Returns:
            删除的记录数
        """
        try:
            cutoff_time = time.time() - (days_to_keep * 24 * 3600)

            # 清理脉诊会话
            result = self.pulse_sessions_collection.delete_many(
                {
                    "created_at": {"$lt": cutoff_time},
                    "status": {"$in": ["completed", "failed", "expired"]},
                }
            )

            deleted_count = result.deleted_count
            logger.info(f"清理了 {deleted_count} 个旧会话")

            return deleted_count
        except Exception as e:
            logger.exception(f"清理旧会话失败: {e!s}")
            return 0

    def get_session_statistics(self, user_id: str) -> dict[str, Any]:
        """
        获取用户会话统计信息

        Args:
            user_id: 用户ID

        Returns:
            统计信息字典
        """
        try:
            # 使用聚合管道计算统计信息
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            ]

            status_counts = list(self.pulse_sessions_collection.aggregate(pipeline))

            # 转换为字典格式
            statistics = {"total_sessions": 0, "status_breakdown": {}}

            for item in status_counts:
                status = item["_id"]
                count = item["count"]
                statistics["status_breakdown"][status] = count
                statistics["total_sessions"] += count

            # 获取最近会话时间
            latest_session = self.pulse_sessions_collection.find_one(
                {"user_id": user_id}, sort=[("created_at", -1)]
            )

            if latest_session:
                statistics["latest_session_time"] = latest_session.get("created_at", 0)
            else:
                statistics["latest_session_time"] = 0

            return statistics
        except Exception as e:
            logger.exception(f"获取会话统计信息失败: {e!s}")
            return {"total_sessions": 0, "status_breakdown": {}, "latest_session_time": 0}
