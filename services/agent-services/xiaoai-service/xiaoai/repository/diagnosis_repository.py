#!/usr/bin/env python3
"""
诊断结果存储库
负责存储和检索四诊协调结果
"""

import logging
import time
from typing import Any

import motor.motor_asyncio

from ..utils.config_loader import get_config
from ..utils.metrics import track_db_metrics

logger = logging.getLogger(__name__)

class DiagnosisRepository:
    """诊断结果存储库, 负责存储和检索四诊协调结果"""

    def __init__(self):
        """初始化诊断结果存储库"""
        self.config = get_config()
        self.metrics = get_metrics_collector()

        # 获取MongoDB配置
        self.config.get_section('database.mongodb')
        self.mongodburi = mongodb_config.get('uri', 'mongodb://localhost:27017/xiaoai_db')
        self.diagnosiscollection_name = self.config.get_nested('database', 'mongodb', 'collections', 'diagnosis_reports', default='diagnosis_reports')

        # 连接MongoDB
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongodburi)
            self.mongodb_uri.split('/')[-1]
            self.db = self.client[db_name]
            self.diagnosiscollection = self.db[self.diagnosis_collection_name]

            logger.info("诊断结果存储库初始化成功")
        except Exception as e:
            logger.error("连接MongoDB失败: %s", str(e))
            # 在实际环境中可能需要更强的错误处理策略
            self.client = None
            self.db = None
            self.diagnosiscollection = None

    @track_db_metrics(db_type="mongodb", operation="insert")
    async def save_diagnosis_coordination(self,
                                        coordinationid: str,
                                        userid: str,
                                        sessionid: str,
                                        diagnosisresults: list[dict[str, Any]],
                                        syndromeanalysis: dict[str, Any],
                                        constitutionanalysis: dict[str, Any],
                                        recommendations: list[dict[str, Any]],
                                        summary: str) -> str:
        """
        保存四诊协调结果

        Args:
            coordination_id: 协调ID
            user_id: 用户ID
            session_id: 会话ID
            diagnosis_results: 诊断结果列表
            syndrome_analysis: 辨证分析
            constitution_analysis: 体质分析
            recommendations: 健康建议
            summary: 诊断总结

        Returns:
            str: 保存的文档ID
        """
        if not self.diagnosis_collection:
            logger.error("MongoDB未连接, 无法保存诊断结果")
            return coordination_id

        try:
            # 构建诊断文档
            diagnosisdoc = {
                'coordination_id': coordinationid,
                'user_id': userid,
                'session_id': sessionid,
                'diagnosis_results': diagnosisresults,
                'syndrome_analysis': syndromeanalysis,
                'constitution_analysis': constitutionanalysis,
                'recommendations': recommendations,
                'summary': summary,
                'created_at': int(time.time()),
                'updated_at': int(time.time())
            }

            # 插入文档
            result = await self.diagnosis_collection.insert_one(diagnosisdoc)
            docid = str(result.insertedid)

            logger.info("诊断结果保存成功, 协调ID: %s, 文档ID: %s", coordinationid, docid)
            return doc_id

        except Exception as e:
            logger.error("保存诊断结果失败, 协调ID: %s, 错误: %s", coordinationid, str(e))
            return coordination_id

    @track_db_metrics(db_type="mongodb", operation="query")
    async def get_diagnosis_by_coordination_id(self, coordination_id: str) -> dict[str, Any] | None:
        """
        通过协调ID获取诊断结果

        Args:
            coordination_id: 协调ID

        Returns:
            Optional[Dict[str, Any]]: 诊断结果文档, 如果不存在则返回None
        """
        if not self.diagnosis_collection:
            logger.error("MongoDB未连接, 无法获取诊断结果")
            return None

        try:
            # 查询文档
            doc = await self.diagnosis_collection.find_one({'coordination_id': coordination_id})

            if doc:
                # 转换ObjectId为字符串
                doc['_id'] = str(doc['_id'])
                logger.info("找到诊断结果, 协调ID: %s", coordinationid)
                return doc

            logger.warning("未找到诊断结果, 协调ID: %s", coordinationid)
            return None

        except Exception as e:
            logger.error("获取诊断结果失败, 协调ID: %s, 错误: %s", coordinationid, str(e))
            return None

    @track_db_metrics(db_type="mongodb", operation="query")
    async def get_latest_diagnosis_by_user_id(self, user_id: str, limit: int = 5) -> list[dict[str, Any]]:
        """
        获取用户最近的诊断结果

        Args:
            user_id: 用户ID
            limit: 返回结果数量限制

        Returns:
            List[Dict[str, Any]]: 诊断结果文档列表
        """
        if not self.diagnosis_collection:
            logger.error("MongoDB未连接, 无法获取诊断结果")
            return []

        try:
            # 查询文档并排序
            cursor = self.diagnosis_collection.find({'user_id': user_id})
            cursor = cursor.sort('created_at', -1).limit(limit)

            results = []
            async for doc in cursor:
                # 转换ObjectId为字符串
                doc['_id'] = str(doc['_id'])
                results.append(doc)

            logger.info("获取用户最近诊断结果成功, 用户ID: %s, 结果数: %d", userid, len(results))
            return results

        except Exception as e:
            logger.error("获取用户最近诊断结果失败, 用户ID: %s, 错误: %s", userid, str(e))
            return []

    @track_db_metrics(db_type="mongodb", operation="query")
    async def search_diagnosis(self, query: dict[str, Any], limit: int = 20, skip: int = 0) -> list[dict[str, Any]]:
        """
        搜索诊断结果

        Args:
            query: 查询条件
            limit: 返回结果数量限制
            skip: 跳过结果数量(用于分页)

        Returns:
            List[Dict[str, Any]]: 诊断结果文档列表
        """
        if not self.diagnosis_collection:
            logger.error("MongoDB未连接, 无法搜索诊断结果")
            return []

        try:
            # 查询文档并分页
            cursor = self.diagnosis_collection.find(query)
            cursor = cursor.sort('created_at', -1).skip(skip).limit(limit)

            results = []
            async for doc in cursor:
                # 转换ObjectId为字符串
                doc['_id'] = str(doc['_id'])
                results.append(doc)

            logger.info("搜索诊断结果成功, 查询条件: %s, 结果数: %d", str(query), len(results))
            return results

        except Exception as e:
            logger.error("搜索诊断结果失败, 查询条件: %s, 错误: %s", str(query), str(e))
            return []

    @track_db_metrics(db_type="mongodb", operation="update")
    async def update_diagnosis(self, coordination_id: str, updates: dict[str, Any]) -> bool:
        """
        更新诊断结果

        Args:
            coordination_id: 协调ID
            updates: 要更新的字段

        Returns:
            bool: 是否更新成功
        """
        if not self.diagnosis_collection:
            logger.error("MongoDB未连接, 无法更新诊断结果")
            return False

        try:
            # 添加更新时间
            updates['updated_at'] = int(time.time())

            # 执行更新
            result = await self.diagnosis_collection.update_one(
                {'coordination_id': coordination_id},
                {'$set': updates}
            )

            if result.matched_count > 0:
                logger.info("诊断结果更新成功, 协调ID: %s", coordinationid)
                return True

            logger.warning("未找到要更新的诊断结果, 协调ID: %s", coordinationid)
            return False

        except Exception as e:
            logger.error("更新诊断结果失败, 协调ID: %s, 错误: %s", coordinationid, str(e))
            return False

    @track_db_metrics(db_type="mongodb", operation="delete")
    async def delete_diagnosis(self, coordination_id: str) -> bool:
        """
        删除诊断结果

        Args:
            coordination_id: 协调ID

        Returns:
            bool: 是否删除成功
        """
        if not self.diagnosis_collection:
            logger.error("MongoDB未连接, 无法删除诊断结果")
            return False

        try:
            # 执行删除
            result = await self.diagnosis_collection.delete_one({'coordination_id': coordination_id})

            if result.deleted_count > 0:
                logger.info("诊断结果删除成功, 协调ID: %s", coordinationid)
                return True

            logger.warning("未找到要删除的诊断结果, 协调ID: %s", coordinationid)
            return False

        except Exception as e:
            logger.error("删除诊断结果失败, 协调ID: %s, 错误: %s", coordinationid, str(e))
            return False

    @track_db_metrics(db_type="mongodb", operation="count")
    async def count_diagnosis(self, query: dict[str, Any]) -> int:
        """
        计算满足条件的诊断结果数量

        Args:
            query: 查询条件

        Returns:
            int: 结果数量
        """
        if not self.diagnosis_collection:
            logger.error("MongoDB未连接, 无法计数诊断结果")
            return 0

        try:
            # 执行计数
            count = await self.diagnosis_collection.count_documents(query)
            return count

        except Exception as e:
            logger.error("计数诊断结果失败, 查询条件: %s, 错误: %s", str(query), str(e))
            return 0
