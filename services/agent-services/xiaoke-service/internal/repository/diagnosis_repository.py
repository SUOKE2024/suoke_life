"""
diagnosis_repository - 索克生活项目模块
"""

from datetime import UTC, datetime, timedelta
from pkg.utils.config_loader import get_config
from pkg.utils.metrics import get_metrics_collector
from pymongo.errors import PyMongoError
from typing import Any
import logging
import uuid

#!/usr/bin/env python

"""
小克智能体服务 - 诊断知识存储库
提供中医辨证、症状诊断和健康状态的存储和检索功能
"""




logger = logging.getLogger(__name__)
metrics = get_metrics_collector()

class DiagnosisRepository:
    """诊断知识存储库，提供中医辨证、症状诊断和健康状态的存储和检索功能"""

    def __init__(self):
        """初始化诊断知识存储库"""
        self.config = get_config()
        self.db_config = self.config.get_section("database.mongodb")

        # 连接到MongoDB
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.db_config.get("uri"))
        self.db = self.client[self.db_config.get("database", "xiaoke_db")]

        # 集合
        self.symptom_patterns = self.db.symptom_patterns  # 症状模式集合
        self.tcm_syndromes = self.db.tcm_syndromes  # 中医证型集合
        self.user_diagnosis = self.db.user_diagnosis  # 用户诊断历史
        self.health_records = self.db.health_records  # 用户健康记录
        self.knowledge_base = self.db.diagnosis_knowledge  # 诊断知识库

        logger.info("诊断知识存储库已初始化")

    async def init_indexes(self):
        """初始化数据库索引"""
        try:
            # 症状模式索引
            await self.symptom_patterns.create_index("pattern_id", unique=True)
            await self.symptom_patterns.create_index("category")
            await self.symptom_patterns.create_index(
                [("name", "text"), ("description", "text")]
            )

            # 中医证型索引
            await self.tcm_syndromes.create_index("syndrome_id", unique=True)
            await self.tcm_syndromes.create_index("type")
            await self.tcm_syndromes.create_index(
                [("name", "text"), ("description", "text")]
            )

            # 用户诊断历史索引
            await self.user_diagnosis.create_index("user_id")
            await self.user_diagnosis.create_index("diagnosis_id", unique=True)
            await self.user_diagnosis.create_index("created_at")

            # 用户健康记录索引
            await self.health_records.create_index(
                [("user_id", 1), ("record_date", -1)]
            )
            await self.health_records.create_index("record_id", unique=True)

            # 诊断知识库索引
            await self.knowledge_base.create_index("knowledge_id", unique=True)
            await self.knowledge_base.create_index("category")
            await self.knowledge_base.create_index(
                [("title", "text"), ("content", "text")]
            )

            logger.info("诊断知识存储库索引已初始化")
        except PyMongoError as e:
            logger.error(f"初始化诊断知识存储库索引失败: {e!s}")
            raise

    @metrics.measure_execution_time("diagnosis_repo_create_symptom_pattern")
    async def create_symptom_pattern(
        self, pattern_data: dict[str, Any]
    ) -> str | None:
        """
        创建症状模式

        Args:
            pattern_data: 症状模式数据

        Returns:
            Optional[str]: 创建的症状模式ID，失败时返回None
        """
        try:
            # 确保数据中没有"_id"字段
            pattern_data.pop("_id", None)

            # 设置ID和创建时间
            pattern_data["pattern_id"] = pattern_data.get(
                "pattern_id", str(uuid.uuid4())
            )
            pattern_data["created_at"] = datetime.now(UTC).isoformat()
            pattern_data["updated_at"] = pattern_data["created_at"]

            # 插入数据
            await self.symptom_patterns.insert_one(pattern_data)

            return pattern_data["pattern_id"]
        except PyMongoError as e:
            logger.error(f"创建症状模式失败: {e!s}")
            metrics.increment_counter(
                "diagnosis_repo_errors", {"method": "create_symptom_pattern"}
            )
            return None

    @metrics.measure_execution_time("diagnosis_repo_find_symptom_patterns")
    async def find_symptom_patterns(
        self,
        category: str | None = None,
        keywords: list[str] | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        查找症状模式

        Args:
            category: 症状类别
            keywords: 关键词列表
            limit: 返回条目数量限制
            offset: 分页偏移量

        Returns:
            List[Dict[str, Any]]: 症状模式列表
        """
        try:
            # 构建查询条件
            query = {}
            if category:
                query["category"] = category

            if keywords and len(keywords) > 0:
                text_query = " ".join(keywords)
                query["$text"] = {"$search": text_query}

            # 执行查询
            cursor = self.symptom_patterns.find(query)

            # 如果使用了全文搜索，按相关性排序
            if keywords and len(keywords) > 0:
                cursor = cursor.sort([("score", {"$meta": "textScore"})])
            else:
                cursor = cursor.sort("name", 1)

            cursor = cursor.skip(offset).limit(limit)

            patterns = await cursor.to_list(length=limit)

            # 处理ObjectId
            for pattern in patterns:
                if "_id" in pattern:
                    pattern["id"] = str(pattern.pop("_id"))

            return patterns
        except PyMongoError as e:
            logger.error(f"查找症状模式失败: {e!s}")
            metrics.increment_counter(
                "diagnosis_repo_errors", {"method": "find_symptom_patterns"}
            )
            return []

    @metrics.measure_execution_time("diagnosis_repo_create_tcm_syndrome")
    async def create_tcm_syndrome(self, syndrome_data: dict[str, Any]) -> str | None:
        """
        创建中医证型

        Args:
            syndrome_data: 证型数据

        Returns:
            Optional[str]: 创建的证型ID，失败时返回None
        """
        try:
            # 确保数据中没有"_id"字段
            syndrome_data.pop("_id", None)

            # 设置ID和创建时间
            syndrome_data["syndrome_id"] = syndrome_data.get(
                "syndrome_id", str(uuid.uuid4())
            )
            syndrome_data["created_at"] = datetime.now(UTC).isoformat()
            syndrome_data["updated_at"] = syndrome_data["created_at"]

            # 插入数据
            await self.tcm_syndromes.insert_one(syndrome_data)

            return syndrome_data["syndrome_id"]
        except PyMongoError as e:
            logger.error(f"创建中医证型失败: {e!s}")
            metrics.increment_counter(
                "diagnosis_repo_errors", {"method": "create_tcm_syndrome"}
            )
            return None

    @metrics.measure_execution_time("diagnosis_repo_find_tcm_syndromes")
    async def find_tcm_syndromes(
        self,
        syndrome_type: str | None = None,
        keywords: list[str] | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        查找中医证型

        Args:
            syndrome_type: 证型类别
            keywords: 关键词列表
            limit: 返回条目数量限制
            offset: 分页偏移量

        Returns:
            List[Dict[str, Any]]: 证型列表
        """
        try:
            # 构建查询条件
            query = {}
            if syndrome_type:
                query["type"] = syndrome_type

            if keywords and len(keywords) > 0:
                text_query = " ".join(keywords)
                query["$text"] = {"$search": text_query}

            # 执行查询
            cursor = self.tcm_syndromes.find(query)

            # 如果使用了全文搜索，按相关性排序
            if keywords and len(keywords) > 0:
                cursor = cursor.sort([("score", {"$meta": "textScore"})])
            else:
                cursor = cursor.sort("name", 1)

            cursor = cursor.skip(offset).limit(limit)

            syndromes = await cursor.to_list(length=limit)

            # 处理ObjectId
            for syndrome in syndromes:
                if "_id" in syndrome:
                    syndrome["id"] = str(syndrome.pop("_id"))

            return syndromes
        except PyMongoError as e:
            logger.error(f"查找中医证型失败: {e!s}")
            metrics.increment_counter(
                "diagnosis_repo_errors", {"method": "find_tcm_syndromes"}
            )
            return []

    @metrics.measure_execution_time("diagnosis_repo_get_tcm_syndrome")
    async def get_tcm_syndrome(self, syndrome_id: str) -> dict[str, Any] | None:
        """
        获取中医证型详情

        Args:
            syndrome_id: 证型ID

        Returns:
            Optional[Dict[str, Any]]: 证型详情，未找到时返回None
        """
        try:
            syndrome = await self.tcm_syndromes.find_one({"syndrome_id": syndrome_id})

            if syndrome:
                # 处理ObjectId
                if "_id" in syndrome:
                    syndrome["id"] = str(syndrome.pop("_id"))

                return syndrome

            return None
        except PyMongoError as e:
            logger.error(f"获取中医证型失败: {e!s}")
            metrics.increment_counter(
                "diagnosis_repo_errors", {"method": "get_tcm_syndrome"}
            )
            return None

    @metrics.measure_execution_time("diagnosis_repo_save_user_diagnosis")
    async def save_user_diagnosis(
        self, user_id: str, diagnosis_data: dict[str, Any]
    ) -> str | None:
        """
        保存用户诊断结果

        Args:
            user_id: 用户ID
            diagnosis_data: 诊断数据

        Returns:
            Optional[str]: 诊断记录ID，失败时返回None
        """
        try:
            # 添加基本字段
            diagnosis_id = str(uuid.uuid4())
            now = datetime.now(UTC).isoformat()

            diagnosis_record = {
                "diagnosis_id": diagnosis_id,
                "user_id": user_id,
                "created_at": now,
                "symptoms": diagnosis_data.get("symptoms", []),
                "syndromes": diagnosis_data.get("syndromes", []),
                "constitution_type": diagnosis_data.get("constitution_type", ""),
                "diagnosis_result": diagnosis_data.get("diagnosis_result", {}),
                "treatment_suggestions": diagnosis_data.get(
                    "treatment_suggestions", []
                ),
                "metadata": diagnosis_data.get("metadata", {}),
                "session_id": diagnosis_data.get("session_id", ""),
            }

            # 保存诊断记录
            await self.user_diagnosis.insert_one(diagnosis_record)

            return diagnosis_id
        except PyMongoError as e:
            logger.error(f"保存用户诊断结果失败: {e!s}")
            metrics.increment_counter(
                "diagnosis_repo_errors", {"method": "save_user_diagnosis"}
            )
            return None

    @metrics.measure_execution_time("diagnosis_repo_get_user_diagnosis_history")
    async def get_user_diagnosis_history(
        self, user_id: str, limit: int = 10, offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        获取用户诊断历史

        Args:
            user_id: 用户ID
            limit: 返回记录数量限制
            offset: 分页偏移量

        Returns:
            List[Dict[str, Any]]: 诊断历史记录
        """
        try:
            cursor = (
                self.user_diagnosis.find({"user_id": user_id})
                .sort("created_at", -1)
                .skip(offset)
                .limit(limit)
            )

            diagnoses = await cursor.to_list(length=limit)

            # 处理ObjectId
            for diagnosis in diagnoses:
                if "_id" in diagnosis:
                    diagnosis["id"] = str(diagnosis.pop("_id"))

            return diagnoses
        except PyMongoError as e:
            logger.error(f"获取用户诊断历史失败: {e!s}")
            metrics.increment_counter(
                "diagnosis_repo_errors", {"method": "get_user_diagnosis_history"}
            )
            return []

    @metrics.measure_execution_time("diagnosis_repo_get_diagnosis_details")
    async def get_diagnosis_details(
        self, diagnosis_id: str
    ) -> dict[str, Any] | None:
        """
        获取诊断详情

        Args:
            diagnosis_id: 诊断ID

        Returns:
            Optional[Dict[str, Any]]: 诊断详情，未找到时返回None
        """
        try:
            diagnosis = await self.user_diagnosis.find_one(
                {"diagnosis_id": diagnosis_id}
            )

            if diagnosis:
                # 处理ObjectId
                if "_id" in diagnosis:
                    diagnosis["id"] = str(diagnosis.pop("_id"))

                # 获取关联的证型详情
                syndrome_ids = diagnosis.get("syndromes", [])
                syndromes = []

                for syndrome_id in syndrome_ids:
                    syndrome = await self.get_tcm_syndrome(syndrome_id)
                    if syndrome:
                        syndromes.append(syndrome)

                diagnosis["syndrome_details"] = syndromes

                return diagnosis

            return None
        except PyMongoError as e:
            logger.error(f"获取诊断详情失败: {e!s}")
            metrics.increment_counter(
                "diagnosis_repo_errors", {"method": "get_diagnosis_details"}
            )
            return None

    @metrics.measure_execution_time("diagnosis_repo_save_health_record")
    async def save_health_record(
        self, user_id: str, record_data: dict[str, Any]
    ) -> str | None:
        """
        保存用户健康记录

        Args:
            user_id: 用户ID
            record_data: 健康记录数据

        Returns:
            Optional[str]: 健康记录ID，失败时返回None
        """
        try:
            # 添加基本字段
            record_id = str(uuid.uuid4())
            now = datetime.now(UTC)

            record = {
                "record_id": record_id,
                "user_id": user_id,
                "created_at": now.isoformat(),
                "record_date": record_data.get("record_date", now.date().isoformat()),
                "vital_signs": record_data.get("vital_signs", {}),
                "symptoms": record_data.get("symptoms", []),
                "lifestyle_data": record_data.get("lifestyle_data", {}),
                "notes": record_data.get("notes", ""),
                "source": record_data.get("source", "manual"),
            }

            # 保存健康记录
            await self.health_records.insert_one(record)

            return record_id
        except PyMongoError as e:
            logger.error(f"保存用户健康记录失败: {e!s}")
            metrics.increment_counter(
                "diagnosis_repo_errors", {"method": "save_health_record"}
            )
            return None

    @metrics.measure_execution_time("diagnosis_repo_get_user_health_records")
    async def get_user_health_records(
        self,
        user_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 30,
    ) -> list[dict[str, Any]]:
        """
        获取用户健康记录

        Args:
            user_id: 用户ID
            start_date: 开始日期 (ISO格式: YYYY-MM-DD)
            end_date: 结束日期 (ISO格式: YYYY-MM-DD)
            limit: 返回记录数量限制

        Returns:
            List[Dict[str, Any]]: 健康记录列表
        """
        try:
            query = {"user_id": user_id}

            # 添加日期过滤
            if start_date or end_date:
                date_query = {}
                if start_date:
                    date_query["$gte"] = start_date
                if end_date:
                    date_query["$lte"] = end_date

                if date_query:
                    query["record_date"] = date_query

            cursor = (
                self.health_records.find(query).sort("record_date", -1).limit(limit)
            )

            records = await cursor.to_list(length=limit)

            # 处理ObjectId
            for record in records:
                if "_id" in record:
                    record["id"] = str(record.pop("_id"))

            return records
        except PyMongoError as e:
            logger.error(f"获取用户健康记录失败: {e!s}")
            metrics.increment_counter(
                "diagnosis_repo_errors", {"method": "get_user_health_records"}
            )
            return []

    @metrics.measure_execution_time("diagnosis_repo_get_latest_health_record")
    async def get_latest_health_record(self, user_id: str) -> dict[str, Any] | None:
        """
        获取用户最新的健康记录

        Args:
            user_id: 用户ID

        Returns:
            Optional[Dict[str, Any]]: 最新健康记录，未找到时返回None
        """
        try:
            record = await self.health_records.find_one(
                {"user_id": user_id}, sort=[("record_date", -1)]
            )

            if record:
                # 处理ObjectId
                if "_id" in record:
                    record["id"] = str(record.pop("_id"))

                return record

            return None
        except PyMongoError as e:
            logger.error(f"获取用户最新健康记录失败: {e!s}")
            metrics.increment_counter(
                "diagnosis_repo_errors", {"method": "get_latest_health_record"}
            )
            return None

    @metrics.measure_execution_time("diagnosis_repo_create_knowledge_item")
    async def create_knowledge_item(
        self, knowledge_data: dict[str, Any]
    ) -> str | None:
        """
        创建诊断知识条目

        Args:
            knowledge_data: 知识数据

        Returns:
            Optional[str]: 创建的知识条目ID，失败时返回None
        """
        try:
            # 确保数据中没有"_id"字段
            knowledge_data.pop("_id", None)

            # 设置ID和创建时间
            knowledge_data["knowledge_id"] = knowledge_data.get(
                "knowledge_id", str(uuid.uuid4())
            )
            knowledge_data["created_at"] = datetime.now(UTC).isoformat()
            knowledge_data["updated_at"] = knowledge_data["created_at"]

            # 插入数据
            await self.knowledge_base.insert_one(knowledge_data)

            return knowledge_data["knowledge_id"]
        except PyMongoError as e:
            logger.error(f"创建诊断知识条目失败: {e!s}")
            metrics.increment_counter(
                "diagnosis_repo_errors", {"method": "create_knowledge_item"}
            )
            return None

    @metrics.measure_execution_time("diagnosis_repo_search_knowledge")
    async def search_knowledge(
        self, query: str, category: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        搜索诊断知识

        Args:
            query: 搜索关键词
            category: 知识类别
            limit: 返回条目数量限制

        Returns:
            List[Dict[str, Any]]: 搜索结果
        """
        try:
            # 构建查询条件
            search_query = {"$text": {"$search": query}}
            if category:
                search_query["category"] = category

            # 执行全文搜索
            cursor = (
                self.knowledge_base.find(
                    search_query, {"score": {"$meta": "textScore"}}
                )
                .sort([("score", {"$meta": "textScore"})])
                .limit(limit)
            )

            results = await cursor.to_list(length=limit)

            # 处理ObjectId
            for item in results:
                if "_id" in item:
                    item["id"] = str(item.pop("_id"))

            return results
        except PyMongoError as e:
            logger.error(f"搜索诊断知识失败: {e!s}")
            metrics.increment_counter(
                "diagnosis_repo_errors", {"method": "search_knowledge"}
            )
            return []

    @metrics.measure_execution_time("diagnosis_repo_get_related_knowledge")
    async def get_related_knowledge(
        self,
        syndrome_id: str | None = None,
        symptom_ids: list[str] | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        获取相关诊断知识

        Args:
            syndrome_id: 中医证型ID
            symptom_ids: 症状ID列表
            limit: 返回条目数量限制

        Returns:
            List[Dict[str, Any]]: 相关知识列表
        """
        try:
            if not syndrome_id and not symptom_ids:
                return []

            # 构建查询条件
            query = {}
            if syndrome_id:
                query["related_syndromes"] = syndrome_id
            if symptom_ids:
                query["related_symptoms"] = {"$in": symptom_ids}

            # 执行查询
            cursor = self.knowledge_base.find(query).limit(limit)
            results = await cursor.to_list(length=limit)

            # 处理ObjectId
            for item in results:
                if "_id" in item:
                    item["id"] = str(item.pop("_id"))

            return results
        except PyMongoError as e:
            logger.error(f"获取相关诊断知识失败: {e!s}")
            metrics.increment_counter(
                "diagnosis_repo_errors", {"method": "get_related_knowledge"}
            )
            return []

    @metrics.measure_execution_time("diagnosis_repo_get_user_constitution_type")
    async def get_user_constitution_type(
        self, user_id: str
    ) -> dict[str, Any] | None:
        """
        获取用户的体质类型
        基于最近的诊断结果

        Args:
            user_id: 用户ID

        Returns:
            Optional[Dict[str, Any]]: 用户体质类型信息，未找到时返回None
        """
        try:
            # 获取最近的诊断结果
            latest_diagnosis = await self.user_diagnosis.find_one(
                {"user_id": user_id}, sort=[("created_at", -1)]
            )

            if not latest_diagnosis:
                return None

            constitution_type = latest_diagnosis.get("constitution_type", "")
            if not constitution_type:
                return None

            # 获取体质类型详情
            constitution_data = {
                "type": constitution_type,
                "diagnosis_id": latest_diagnosis["diagnosis_id"],
                "diagnosis_date": latest_diagnosis["created_at"],
                "syndromes": latest_diagnosis.get("syndromes", []),
                "treatment_suggestions": latest_diagnosis.get(
                    "treatment_suggestions", []
                ),
            }

            return constitution_data
        except PyMongoError as e:
            logger.error(f"获取用户体质类型失败: {e!s}")
            metrics.increment_counter(
                "diagnosis_repo_errors", {"method": "get_user_constitution_type"}
            )
            return None

    @metrics.measure_execution_time("diagnosis_repo_find_similar_diagnoses")
    async def find_similar_diagnoses(
        self, symptoms: list[str], limit: int = 5
    ) -> list[dict[str, Any]]:
        """
        查找相似的诊断记录

        Args:
            symptoms: 症状列表
            limit: 返回记录数量限制

        Returns:
            List[Dict[str, Any]]: 相似诊断记录
        """
        try:
            if not symptoms or len(symptoms) == 0:
                return []

            # 使用症状列表进行匹配
            pipeline = [
                # 匹配包含至少一个相同症状的记录
                {"$match": {"symptoms": {"$in": symptoms}}},
                # 计算匹配的症状数量
                {
                    "$addFields": {
                        "matching_symptoms": {
                            "$size": {"$setIntersection": ["$symptoms", symptoms]}
                        }
                    }
                },
                # 按匹配数量排序
                {"$sort": {"matching_symptoms": -1, "created_at": -1}},
                # 限制结果数量
                {"$limit": limit},
            ]

            cursor = self.user_diagnosis.aggregate(pipeline)
            results = await cursor.to_list(length=limit)

            # 处理ObjectId
            for item in results:
                if "_id" in item:
                    item["id"] = str(item.pop("_id"))

            return results
        except PyMongoError as e:
            logger.error(f"查找相似诊断记录失败: {e!s}")
            metrics.increment_counter(
                "diagnosis_repo_errors", {"method": "find_similar_diagnoses"}
            )
            return []

    @metrics.measure_execution_time("diagnosis_repo_analyze_symptom_trend")
    async def analyze_symptom_trend(
        self, user_id: str, symptom: str, days: int = 90
    ) -> dict[str, Any]:
        """
        分析用户症状趋势

        Args:
            user_id: 用户ID
            symptom: 症状名称
            days: 分析天数

        Returns:
            Dict[str, Any]: 趋势分析结果
        """
        try:
            # 计算开始日期
            start_date = (datetime.now(UTC) - timedelta(days=days)).isoformat()

            # 查询包含该症状的健康记录
            pipeline = [
                # 匹配用户和日期范围
                {
                    "$match": {
                        "user_id": user_id,
                        "created_at": {"$gte": start_date},
                        "symptoms": symptom,
                    }
                },
                # 按日期分组
                {
                    "$group": {
                        "_id": {
                            "$substr": ["$record_date", 0, 10]
                        },  # 按日期分组 (YYYY-MM-DD)
                        "count": {"$sum": 1},
                        "records": {
                            "$push": {
                                "record_id": "$record_id",
                                "created_at": "$created_at",
                                "notes": "$notes",
                            }
                        },
                    }
                },
                # 按日期排序
                {"$sort": {"_id": 1}},
            ]

            cursor = self.health_records.aggregate(pipeline)
            results = await cursor.to_list(length=None)

            # 查询包含该症状的诊断记录
            diagnosis_pipeline = [
                # 匹配用户和日期范围
                {
                    "$match": {
                        "user_id": user_id,
                        "created_at": {"$gte": start_date},
                        "symptoms": symptom,
                    }
                },
                # 按日期分组
                {
                    "$group": {
                        "_id": {
                            "$substr": ["$created_at", 0, 10]
                        },  # 按日期分组 (YYYY-MM-DD)
                        "count": {"$sum": 1},
                        "diagnoses": {
                            "$push": {
                                "diagnosis_id": "$diagnosis_id",
                                "created_at": "$created_at",
                                "syndromes": "$syndromes",
                            }
                        },
                    }
                },
                # 按日期排序
                {"$sort": {"_id": 1}},
            ]

            diagnosis_cursor = self.user_diagnosis.aggregate(diagnosis_pipeline)
            diagnosis_results = await diagnosis_cursor.to_list(length=None)

            # 合并结果
            trend_data = {
                "symptom": symptom,
                "user_id": user_id,
                "analysis_period_days": days,
                "health_records": results,
                "diagnosis_records": diagnosis_results,
                "total_occurrences": sum(r["count"] for r in results)
                + sum(r["count"] for r in diagnosis_results),
                "first_occurrence": results[0]["_id"] if results else None,
                "latest_occurrence": results[-1]["_id"] if results else None,
            }

            return trend_data
        except PyMongoError as e:
            logger.error(f"分析用户症状趋势失败: {e!s}")
            metrics.increment_counter(
                "diagnosis_repo_errors", {"method": "analyze_symptom_trend"}
            )
            return {"error": str(e)}

    @metrics.measure_execution_time("diagnosis_repo_get_common_user_symptoms")
    async def get_common_user_symptoms(
        self, user_id: str, limit: int = 10
    ) -> list[dict[str, str]]:
        """
        获取用户常见症状

        Args:
            user_id: 用户ID
            limit: 返回条目数量限制

        Returns:
            List[Dict[str, str]]: 常见症状列表
        """
        try:
            # 聚合用户的症状出现频率
            pipeline = [
                # 匹配用户
                {"$match": {"user_id": user_id}},
                # 展开症状数组
                {"$unwind": "$symptoms"},
                # 按症状分组并计数
                {
                    "$group": {
                        "_id": "$symptoms",
                        "count": {"$sum": 1},
                        "latest": {"$max": "$created_at"},
                    }
                },
                # 按出现次数排序
                {"$sort": {"count": -1, "latest": -1}},
                # 限制结果数量
                {"$limit": limit},
                # 格式化输出
                {"$project": {"_id": 0, "symptom": "$_id", "count": 1, "latest": 1}},
            ]

            cursor = self.user_diagnosis.aggregate(pipeline)
            results = await cursor.to_list(length=limit)

            return results
        except PyMongoError as e:
            logger.error(f"获取用户常见症状失败: {e!s}")
            metrics.increment_counter(
                "diagnosis_repo_errors", {"method": "get_common_user_symptoms"}
            )
            return []
