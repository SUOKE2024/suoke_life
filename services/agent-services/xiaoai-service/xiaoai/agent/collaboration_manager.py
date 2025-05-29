#!/usr/bin/env python3

"""
智能体协作管理器
负责小艾与其他智能体(小克、老克、索儿)的协作交互
"""

import asyncio
import contextlib
import logging
import time
import uuid
from typing import Any

from ..utils.config_loader import get_config
from ..utils.metrics import get_metrics_collector

# 导入项目依赖
from .model_factory import get_model_factory

logger = logging.getLogger(__name__)

class AgentCapability:
    """智能体能力定义"""

    def __init__(self,
                capabilityid: str,
                name: str,
                description: str,
                agentid: str,
                requiredparams: list[str] | None = None,
                optionalparams: list[str] | None = None):
        self.capabilityid = capability_id
        self.name = name
        self.description = description
        self.agentid = agent_id
        self.requiredparams = required_params or []
        self.optionalparams = optional_params or []

class CollaborationTask:
    """协作任务定义"""

    def __init__(self,
                taskid: str,
                title: str,
                description: str,
                requesterid: str,
                assigneeid: str,
                capabilityid: str,
                params: dict[str, Any],
                status: str = "created",
                createdat: int | None = None,
                completedat: int | None = None,
                result: dict[str, Any] | None = None):
        self.taskid = task_id
        self.title = title
        self.description = description
        self.requesterid = requester_id
        self.assigneeid = assignee_id
        self.capabilityid = capability_id
        self.params = params
        self.status = status
        self.createdat = created_at or int(time.time())
        self.completedat = completed_at
        self.result = result or {}

class CollaborationManager:
    """智能体协作管理器, 负责管理小艾与其他智能体的协作交互"""

    def __init__(self, model_factory=None):
        """
        初始化协作管理器

        Args:
            model_factory: 模型工厂实例, 如果为None则创建新实例
        """
        self.config = get_config()
        self.metrics = get_metrics_collector()

        self.modelfactory = model_factory

        # 加载配置
        self.config.get_section('collaboration', {})

        # 协作配置
        self.xiaokeendpoint = collaboration_config.get('xiaoke_endpoint', 'localhost:50051')
        self.laokeendpoint = collaboration_config.get('laoke_endpoint', 'localhost:50052')
        self.soerendpoint = collaboration_config.get('soer_endpoint', 'localhost:50053')
        self.capabilitydiscovery_enabled = collaboration_config.get('capability_discovery_enabled', True)
        self.tasktimeout = collaboration_config.get('task_timeout', 30000)  # 毫秒

        # 注册智能体能力
        self.capabilities = {}
        self.register_base_capabilities()

        # 任务管理
        self.tasks = {}  # task_id -> CollaborationTask
        self.taskcallbacks = {}  # task_id -> callback function

        # 创建客户端连接
        self.agentclients = {}

        logger.info("智能体协作管理器初始化完成")

    async def initialize(self):
        """异步初始化模型工厂"""
        if self.model_factory is None:
            self.modelfactory = await get_model_factory()
            logger.info("协作管理器模型工厂异步初始化完成")

    def register_base_capabilities(self):
        """注册基础智能体能力"""
        # 小克能力
        self._register_capability(
            capability_id="xiaoke.medical_resource.allocate",
            name="医疗资源分配",
            description="根据健康需求分配适当的医疗资源",
            agent_id="xiaoke",
            required_params=["health_need", "location"],
            optional_params=["urgency", "preferences"]
        )

        self._register_capability(
            capability_id="xiaoke.treatment_plan.generate",
            name="治疗方案生成",
            description="基于辨证结果生成治疗方案",
            agent_id="xiaoke",
            required_params=["syndrome_analysis", "user_profile"],
            optional_params=["treatment_history", "preferences"]
        )

        self._register_capability(
            capability_id="xiaoke.food_therapy.design",
            name="食疗方案设计",
            description="设计个性化食疗方案",
            agent_id="xiaoke",
            required_params=["constitution_type", "health_condition"],
            optional_params=["dietary_preferences", "seasonal_adjustment"]
        )

        # 老克能力
        self._register_capability(
            capability_id="laoke.knowledge.query",
            name="中医知识查询",
            description="查询中医理论与实践知识",
            agent_id="laoke",
            required_params=["query"],
            optional_params=["context", "detail_level"]
        )

        self._register_capability(
            capability_id="laoke.education.content",
            name="健康教育内容",
            description="生成健康教育内容",
            agent_id="laoke",
            required_params=["topic", "audience"],
            optional_params=["format", "focus_areas"]
        )

        self._register_capability(
            capability_id="laoke.community.discuss",
            name="社区健康讨论",
            description="引导健康社区讨论",
            agent_id="laoke",
            required_params=["topic", "background"],
            optional_params=["perspective", "goal"]
        )

        # 索儿能力
        self._register_capability(
            capability_id="soer.health_plan.create",
            name="健康规划创建",
            description="创建长期健康管理规划",
            agent_id="soer",
            required_params=["user_profile", "health_goals"],
            optional_params=["time_frame", "priority_areas"]
        )

        self._register_capability(
            capability_id="soer.lifestyle.recommend",
            name="生活方式建议",
            description="提供个性化生活方式建议",
            agent_id="soer",
            required_params=["constitution_type", "current_lifestyle"],
            optional_params=["focus_areas", "implementation_difficulty"]
        )

        self._register_capability(
            capability_id="soer.nutrition.guide",
            name="营养指导",
            description="提供个性化营养指导",
            agent_id="soer",
            required_params=["health_condition", "dietary_habits"],
            optional_params=["nutritional_goals", "restrictions"]
        )

    def _register_capability(self, capabilityid, name, description, agentid, required_params=None, optional_params=None):
        """注册智能体能力"""
        capability = AgentCapability(
            capability_id=capabilityid,
            name=name,
            description=description,
            agent_id=agentid,
            required_params=requiredparams,
            optional_params=optional_params
        )

        self.capabilities[capability_id] = capability
        logger.debug(f"注册能力: {capability_id}, 代理: {agent_id}")

    async def discover_capabilities(self):
        """发现智能体能力"""
        if not self.capability_discovery_enabled:
            logger.info("能力发现功能已禁用")
            return

        try:
            # 连接各智能体服务
            await self._connect_agent_clients()

            # 从小克发现能力
            await self._discover_agent_capabilities("xiaoke")
            for cap in xiaoke_capabilities:
                self._register_capability(**cap)

            # 从老克发现能力
            await self._discover_agent_capabilities("laoke")
            for cap in laoke_capabilities:
                self._register_capability(**cap)

            # 从索儿发现能力
            await self._discover_agent_capabilities("soer")
            for cap in soer_capabilities:
                self._register_capability(**cap)

            logger.info(f"能力发现完成, 共发现 {len(self.capabilities)} 个能力")

        except Exception as e:
            logger.error(f"能力发现失败: {e!s}")

    async def _connect_agent_clients(self):
        """连接智能体客户端"""
        pass

    async def _discover_agent_capabilities(self, agentid):
        """发现智能体能力"""
        # 当前返回空列表, 使用预定义的能力
        return []

    async def create_collaboration_task(self,
                                        title: str,
                                        description: str,
                                        assigneeid: str,
                                        capabilityid: str,
                                        params: dict[str, Any],
                                        callback=None) -> str:
        """
        创建协作任务

        Args:
            title: 任务标题
            description: 任务描述
            assignee_id: 受理智能体ID
            capability_id: 能力ID
            params: 任务参数
            callback: 完成回调函数

        Returns:
            str: 任务ID
        """
        # 验证能力是否存在
        if capability_id not in self.capabilities:
            raise ValueError(f"未知的能力ID: {capability_id}")

        capability = self.capabilities[capability_id]

        # 验证参数是否满足要求
        for param in capability.required_params:
            if param not in params:
                raise ValueError(f"缺少必需参数: {param}")

        # 创建任务
        taskid = str(uuid.uuid4())
        task = CollaborationTask(
            task_id=taskid,
            title=title,
            description=description,
            requester_id="xiaoai",  # 小艾作为请求者
            assignee_id=assigneeid,
            capability_id=capabilityid,
            params=params,
            status="created"
        )

        # 保存任务
        self.tasks[task_id] = task

        # 保存回调
        if callback:
            self.task_callbacks[task_id] = callback

        # 记录指标
        self.metrics.increment_request_count(f"collaboration_task.{capability_id}")

        # 提交任务
        asyncio.create_task(self._process_task(taskid))

        logger.info(f"创建协作任务: {task_id}, 能力: {capability_id}, 受理者: {assignee_id}")
        return task_id

    async def _process_task(self, taskid: str):
        """处理协作任务"""
        task = self.tasks.get(taskid)
        if not task:
            logger.error(f"未找到任务: {task_id}")
            return

        # 更新任务状态
        task.status = "processing"

        try:
            # 根据不同的智能体选择不同的处理方法
            if task.assigneeid == "xiaoke":
                result = await self._process_xiaoke_task(task)
            elif task.assigneeid == "laoke":
                result = await self._process_laoke_task(task)
            elif task.assigneeid == "soer":
                result = await self._process_soer_task(task)
            else:
                logger.error(f"未知的智能体ID: {task.assignee_id}")
                task.status = "failed"
                return

            # 更新任务状态
            task.status = "completed"
            task.completedat = int(time.time())
            task.result = result

            # 调用回调函数
            callback = self.task_callbacks.get(taskid)
            if callback:
                try:
                    callback(task)
                except Exception as e:
                    logger.error(f"任务回调执行失败: {e!s}")

            # 记录指标
            taskduration = task.completed_at - task.created_at
            self.metrics.record_request_time(f"collaboration_task.{task.capability_id}", taskduration)

            logger.info(f"协作任务完成: {task_id}")

        except Exception as e:
            logger.error(f"处理协作任务失败: {e!s}")
            task.status = "failed"
            self.metrics.increment_error_count(f"collaboration_task.{task.capability_id}")

    async def _process_xiaoke_task(self, task: CollaborationTask) -> dict[str, Any]:
        """处理小克任务"""

        # 当前模拟处理
        await asyncio.sleep(1)  # 模拟处理时间

        # 根据不同能力返回不同结果
        if task.capabilityid == "xiaoke.medical_resource.allocate":
            return {
                "allocated_resources": [
                    {"type": "expert", "name": "张医生", "specialty": "中医内科", "availability": "可在30分钟内接诊"},
                    {"type": "facility", "name": "仁心堂中医诊所", "address": "市中心路123号", "distance": "1.5公里"}
                ],
                "recommendation": "建议挂号张医生, 专精于体质调理。"
            }

        elif task.capabilityid == "xiaoke.treatment_plan.generate":
            return {
                "plan_id": str(uuid.uuid4()),
                "treatment_methods": [
                    {"type": "herbal", "name": "益气养阴方", "dosage": "每日一剂, 早晚分服"},
                    {"type": "acupuncture", "points": ["足三里", "气海", "关元"], "frequency": "每周2次"}
                ],
                "duration": "3周",
                "notes": "服药期间忌辛辣刺激食物, 保持良好作息。"
            }

        elif task.capabilityid == "xiaoke.food_therapy.design":
            return {
                "plan_id": str(uuid.uuid4()),
                "recommended_foods": [
                    {"category": "grains", "items": ["小米", "糙米"], "benefit": "健脾养胃"},
                    {"category": "proteins", "items": ["鲫鱼", "鸭肉"], "benefit": "滋阴润燥"}
                ],
                "avoid_foods": ["辣椒", "生冷食物", "油炸食品"],
                "recipes": [
                    {"name": "山药薏米粥", "ingredients": "山药30g, 薏米50g, 大枣5枚", "preparation": "同煮成粥"}
                ],
                "eating_habits": "少量多餐, 细嚼慢咽, 食温热食物。"
            }

        else:
            # 未知能力
            return {"error": "未实现的能力"}

    async def _process_laoke_task(self, task: CollaborationTask) -> dict[str, Any]:
        """处理老克任务"""

        # 当前模拟处理
        await asyncio.sleep(1)  # 模拟处理时间

        # 根据不同能力返回不同结果
        if task.capabilityid == "laoke.knowledge.query":
            return {
                "query_id": str(uuid.uuid4()),
                "answer": "中医辨证论治是以整体观念为指导, 运用望、闻、问、切四诊方法, 分析病情, 辨别证候, 确定治法, 拟定方药的诊疗思维与方法。",
                "references": [
                    {"title": "中医诊断学", "author": "朱文锋", "publisher": "中国中医药出版社"},
                    {"title": "中医辨证论治概论", "author": "朱文锋", "publisher": "人民卫生出版社"}
                ],
                "related_topics": ["四诊合参", "八纲辨证", "脏腑辨证"]
            }

        elif task.capabilityid == "laoke.education.content":
            return {
                "content_id": str(uuid.uuid4()),
                "title": "认识阴虚体质",
                "content": "阴虚体质是中医九种体质类型之一, 主要表现为口干、手足心热、盗汗等症状。本文将介绍阴虚体质的特点、形成原因及日常调养方法。",
                "sections": [
                    {"title": "阴虚体质的表现", "content": "..."},
                    {"title": "阴虚体质的形成", "content": "..."},
                    {"title": "阴虚体质的调养", "content": "..."}
                ],
                "media_resources": [
                    {"type": "image", "url": "https://example.com/yinxu_constitution.jpg"},
                    {"type": "video", "url": "https://example.com/yinxu_nursing.mp4"}
                ]
            }

        elif task.capabilityid == "laoke.community.discuss":
            return {
                "discussion_id": str(uuid.uuid4()),
                "topic_summary": "如何在现代生活中实践中医养生",
                "key_points": [
                    "传统中医养生理念在现代生活中的意义",
                    "简单实用的中医养生方法",
                    "中医养生与现代医学的结合",
                    "不同人群的养生方法差异"
                ],
                "discussion_questions": [
                    "您在日常生活中实践哪些中医养生方法?",
                    "您认为哪些传统养生方法最适合现代人?",
                    "您在养生实践中遇到过哪些困难?"
                ]
            }

        else:
            # 未知能力
            return {"error": "未实现的能力"}

    async def _process_soer_task(self, task: CollaborationTask) -> dict[str, Any]:
        """处理索儿任务"""

        # 当前模拟处理
        await asyncio.sleep(1)  # 模拟处理时间

        # 根据不同能力返回不同结果
        if task.capabilityid == "soer.health_plan.create":
            return {
                "plan_id": str(uuid.uuid4()),
                "title": "阴虚体质三个月改善计划",
                "description": "针对阴虚体质特点, 综合调整饮食、运动、作息等方面, 达到滋阴潜阳、平衡阴阳的目标。",
                "duration": "12周",
                "phases": [
                    {
                        "name": "初始调整期",
                        "duration": "4周",
                        "focus": "调整作息, 滋阴饮食",
                        "activities": [
                            {"type": "diet", "description": "增加滋阴食物摄入, 如银耳、百合、芝麻等"},
                            {"type": "exercise", "description": "每日太极拳或八段锦, 15-30分钟"}
                        ]
                    },
                    {
                        "name": "深化巩固期",
                        "duration": "8周",
                        "focus": "增强身体调节能力",
                        "activities": [
                            {"type": "diet", "description": "进一步优化饮食结构, 适当增加蛋白质摄入"},
                            {"type": "exercise", "description": "增加运动强度, 配合经络按摩"}
                        ]
                    }
                ],
                "expected_outcomes": [
                    "改善口干舌燥、手足心热等阴虚症状",
                    "提高睡眠质量",
                    "增强整体免疫力"
                ]
            }

        elif task.capabilityid == "soer.lifestyle.recommend":
            return {
                "recommendation_id": str(uuid.uuid4()),
                "lifestyle_areas": [
                    {
                        "area": "作息",
                        "current_status": "经常熬夜, 睡眠不规律",
                        "recommendations": [
                            "建立规律作息, 23点前入睡",
                            "午休15-30分钟, 避免过长",
                            "清晨6-7点起床, 练习晨起伸展"
                        ],
                        "priority": "高"
                    },
                    {
                        "area": "情绪",
                        "current_status": "工作压力大, 易焦虑",
                        "recommendations": [
                            "每日冥想15分钟",
                            "学习情绪管理技巧",
                            "培养放松爱好如听音乐、绘画"
                        ],
                        "priority": "中"
                    },
                    {
                        "area": "活动",
                        "current_status": "久坐少动",
                        "recommendations": [
                            "工作间隙起身活动",
                            "每周进行3次中等强度运动",
                            "选择适合阴虚体质的运动如太极、散步"
                        ],
                        "priority": "高"
                    }
                ]
            }

        elif task.capabilityid == "soer.nutrition.guide":
            return {
                "guide_id": str(uuid.uuid4()),
                "nutrition_analysis": {
                    "current_issues": [
                        "蛋白质摄入不足",
                        "精制碳水化合物过多",
                        "水果蔬菜种类单一"
                    ],
                    "recommendations": [
                        "增加优质蛋白质来源, 如鱼类、豆制品",
                        "减少精制碳水化合物, 增加全谷物",
                        "每天摄入5种以上不同颜色的蔬果"
                    ]
                },
                "meal_plans": [
                    {
                        "meal": "早餐",
                        "sample": "燕麦粥配核桃和蓝莓, 豆浆",
                        "nutrition_focus": "提供稳定能量, 补充蛋白质和抗氧化物"
                    },
                    {
                        "meal": "午餐",
                        "sample": "糙米饭, 蒸鱼, 时令蔬菜, 莲藕汤",
                        "nutrition_focus": "优质蛋白质和复合碳水化合物, 维生素矿物质补充"
                    },
                    {
                        "meal": "晚餐",
                        "sample": "小米粥, 清蒸豆腐, 凉拌菠菜",
                        "nutrition_focus": "易消化, 补充必要营养, 不增加睡眠负担"
                    }
                ]
            }

        else:
            # 未知能力
            return {"error": "未实现的能力"}

    def get_task(self, taskid: str) -> CollaborationTask | None:
        """获取任务详情"""
        return self.tasks.get(taskid)

    def get_tasks_by_status(self, status: str) -> list[CollaborationTask]:
        """按状态获取任务列表"""
        return [task for task in self.tasks.values() if task.status == status]

    def get_capabilities_by_agent(self, agentid: str) -> list[AgentCapability]:
        """获取智能体的能力列表"""
        return [cap for cap in self.capabilities.values() if cap.agentid == agent_id]

    async def close(self):
        """关闭资源"""
        # 关闭模型工厂
        if self.model_factory:
            await self.model_factory.close()

        # 关闭智能体客户端连接
        for client in self.agent_clients.values():
            with contextlib.suppress(Exception):
                await client.close()

        logger.info("智能体协作管理器已关闭")

# 单例实例
collaboration_manager = None

def get_collaboration_manager():
    """获取协作管理器单例"""
    global _collaboration_manager
    if _collaboration_manager is None:
        CollaborationManager()
    return _collaboration_manager
