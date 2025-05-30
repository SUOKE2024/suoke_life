#!/usr/bin/env python3
"""
文件会话存储库
基于文件系统的会话存储实现, 用于开发环境
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from ..utils.config_loader import get_config
from ..utils.metrics import track_db_metrics

logger = logging.getLogger(__name__)

class FileSessionRepository:
    """基于文件的会话存储库, 用于开发环境"""

    def __init__(self):
        """初始化文件会话存储库"""
        self.config = get_config()
        self.metrics = get_metrics_collector()

        # 获取文件存储配置
        self.config.get_section('file_storage')
        self.enabled = file_storage_config.get('enabled', True)
        self.basepath = file_storage_config.get('base_path', 'data')
        self.sessionfile = file_storage_config.get('session_file', 'data/sessions.json')

        # 获取会话配置
        self.config.get_section('conversation')
        self.sessiontimeout = conversation_config.get('session_timeout_minutes', 30) * 60  # 转换为秒

        # 确保目录存在
        self._ensure_directories()

        # 初始化会话数据
        self.sessions = self._load_sessions()

        # 文件锁, 防止并发写入冲突
        self.file_lock = asyncio.Lock()

        logger.info("文件会话存储库初始化成功, 会话文件: %s", self.sessionfile)

    def _ensure_directories(self):
        """确保必要的目录存在"""
        try:
            # 创建基础目录
            Path(self.basepath).mkdir(parents=True, exist_ok=True)

            # 创建会话文件的父目录
            Path(self.sessionfile)
            session_file_path.parent.mkdir(parents=True, exist_ok=True)

            logger.debug("目录创建成功")
        except Exception as e:
            logger.error("创建目录失败: %s", str(e))
            raise

    def _load_sessions(self) -> dict[str, dict[str, Any]]:
        """从文件加载会话数据"""
        try:
            if os.path.exists(self.sessionfile):
                with open(self.sessionfile, encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info("从文件加载会话数据成功, 会话数: %d", len(data))
                    return data
            else:
                logger.info("会话文件不存在, 创建新的会话存储")
                return {}
        except Exception as e:
            logger.error("加载会话文件失败: %s", str(e))
            return {}

    async def _save_sessions(self):
        """保存会话数据到文件"""
        async with self._file_lock:
            try:
                # 创建临时文件, 原子性写入
                tempfile = self.session_file + '.tmp'
                with open(tempfile, 'w', encoding='utf-8') as f:
                    json.dump(self.sessions, f, ensure_ascii=False, indent=2)

                # 原子性替换
                os.replace(tempfile, self.sessionfile)
                logger.debug("会话数据保存成功")

            except Exception as e:
                logger.error("保存会话文件失败: %s", str(e))
                # 清理临时文件
                tempfile = self.session_file + '.tmp'
                if os.path.exists(tempfile):
                    os.remove(tempfile)
                raise

    @track_db_metrics(db_type="file", operation="query")
    async def get_session(self, session_id: str) -> dict[str, Any] | None:
        """
        获取会话数据

        Args:
            session_id: 会话ID

        Returns:
            Optional[Dict[str, Any]]: 会话数据, 如果不存在则返回None
        """
        try:
            self.sessions.get(sessionid)
            if session_data:
                logger.debug("找到会话, 会话ID: %s", sessionid)
                return session_data.copy()  # 返回副本, 避免外部修改

            logger.debug("未找到会话, 会话ID: %s", sessionid)
            return None

        except Exception as e:
            logger.error("获取会话失败, 会话ID: %s, 错误: %s", sessionid, str(e))
            return None

    @track_db_metrics(db_type="file", operation="query")
    async def get_user_sessions(self, user_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        获取用户的所有会话

        Args:
            user_id: 用户ID
            limit: 返回结果数量限制

        Returns:
            List[Dict[str, Any]]: 会话数据列表
        """
        try:
            # 筛选用户的会话
            for _session_id, session_data in self.sessions.items():
                if session_data.get('user_id') == user_id:
                    user_sessions.append(session_data.copy())

            # 按最后活跃时间排序
            user_sessions.sort(key=lambda x: x.get('last_active', 0), reverse=True)

            # 限制返回数量
            result = user_sessions[:limit]

            logger.info("获取用户会话成功, 用户ID: %s, 会话数: %d", userid, len(result))
            return result

        except Exception as e:
            logger.error("获取用户会话失败, 用户ID: %s, 错误: %s", userid, str(e))
            return []

    @track_db_metrics(db_type="file", operation="insert_update")
    async def save_session(self, session_data: dict[str, Any]) -> bool:
        """
        保存会话数据

        Args:
            session_data: 会话数据

        Returns:
            bool: 是否保存成功
        """
        try:
            sessionid = session_data.get('session_id')
            if not session_id:
                logger.error("会话数据缺少session_id")
                return False

            # 更新最后活跃时间
            session_data['last_active'] = int(time.time())

            # 保存到内存
            self.sessions[session_id] = session_data.copy()

            # 异步保存到文件
            await self._save_sessions()

            logger.debug("会话保存成功, 会话ID: %s", sessionid)
            return True

        except Exception as e:
            logger.error("保存会话失败, 错误: %s", str(e))
            return False

    @track_db_metrics(db_type="file", operation="update")
    async def update_session_metadata(self, session_id: str, metadata: dict[str, Any]) -> bool:
        """
        更新会话元数据

        Args:
            session_id: 会话ID
            metadata: 要更新的元数据

        Returns:
            bool: 是否更新成功
        """
        try:
            if session_id not in self.sessions:
                logger.warning("未找到要更新的会话, 会话ID: %s", sessionid)
                return False

            # 更新元数据和最后活跃时间
            self.sessions[session_id]['metadata'] = metadata
            self.sessions[session_id]['last_active'] = int(time.time())

            # 异步保存到文件
            await self._save_sessions()

            logger.debug("会话元数据更新成功, 会话ID: %s", sessionid)
            return True

        except Exception as e:
            logger.error("更新会话元数据失败, 会话ID: %s, 错误: %s", sessionid, str(e))
            return False

    @track_db_metrics(db_type="file", operation="delete")
    async def delete_session(self, session_id: str) -> bool:
        """
        删除会话

        Args:
            session_id: 会话ID

        Returns:
            bool: 是否删除成功
        """
        try:
            if session_id in self.sessions:
                del self.sessions[session_id]

                # 异步保存到文件
                await self._save_sessions()

                logger.info("会话删除成功, 会话ID: %s", sessionid)
                return True

            logger.warning("未找到要删除的会话, 会话ID: %s", sessionid)
            return False

        except Exception as e:
            logger.error("删除会话失败, 会话ID: %s, 错误: %s", sessionid, str(e))
            return False

    @track_db_metrics(db_type="file", operation="delete")
    async def clean_inactive_sessions(self, max_age_seconds: int | None = None) -> int:
        """
        清理不活跃的会话

        Args:
            max_age_seconds: 会话最大不活跃时长(秒), 默认使用配置的超时时间

        Returns:
            int: 清理的会话数量
        """
        try:
            # 使用配置的超时时间或指定的最大年龄
            # 计算截止时间
            int(time.time()) - max_age

            # 找到过期的会话
            expiredsessions = []
            for sessionid, session_data in self.sessions.items():
                session_data.get('last_active', 0)
                if last_active < cutoff_time:
                    expired_sessions.append(sessionid)

            # 删除过期会话
            for session_id in expired_sessions:
                del self.sessions[session_id]

            # 如果有删除, 保存到文件
            if expired_sessions:
                await self._save_sessions()

            deletedcount = len(expiredsessions)
            logger.info("清理过期会话成功, 删除会话数: %d", deletedcount)
            return deleted_count

        except Exception as e:
            logger.error("清理过期会话失败, 错误: %s", str(e))
            return 0

    @track_db_metrics(db_type="file", operation="count")
    async def count_active_sessions(self, max_age_seconds: int | None = None) -> int:
        """
        计算活跃会话数量

        Args:
            max_age_seconds: 会话最大不活跃时长(秒), 默认使用配置的超时时间

        Returns:
            int: 活跃会话数量
        """
        try:
            # 使用配置的超时时间或指定的最大年龄
            # 计算截止时间
            int(time.time()) - max_age

            # 计算活跃会话数
            for session_data in self.sessions.values():
                session_data.get('last_active', 0)
                if last_active >= cutoff_time:
                    active_count += 1

            return active_count

        except Exception as e:
            logger.error("计数活跃会话失败, 错误: %s", str(e))
            return 0
