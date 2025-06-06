"""
profile_service - 索克生活项目模块
"""

from datetime import datetime
from typing import Any
import logging

"""
健康画像服务 - 管理用户健康状况全面视图
"""

logger = logging.getLogger(__name__)

class HealthProfile:
    """用户健康画像模型"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

        # 基础健康信息
        self.basic_info = {
            "height": None,  # 身高(cm)
            "weight": None,  # 体重(kg)
            "gender": None,  # 性别
            "age": None,     # 年龄
            "blood_type": None  # 血型
        }

        # 中医体质信息
        self.tcm_constitution = {
            "primary_type": None,  # 主要体质类型
            "secondary_types": [],  # 次要体质类型
            "constitution_scores": {},  # 体质得分 {体质类型: 得分}
            "updated_at": None  # 体质评估更新时间
        }

        # 健康指标
        self.health_metrics = {
            "resting_heart_rate": None,  # 静息心率
            "blood_pressure": {          # 血压
                "systolic": None,        # 收缩压
                "diastolic": None        # 舒张压
            },
            "sleep_quality": None,       # 睡眠质量(0-100)
            "stress_level": None,        # 压力水平(0-100)
            "activity_level": None       # 活动水平(0-100)
        }

        # 健康风险
        self.health_risks = []

        # 慢性健康问题
        self.chronic_conditions = []

        # 情绪状态
        self.emotional_state = {
            "primary_emotion": None,
            "emotion_scores": {},
            "updated_at": None
        }

        # 健康目标
        self.health_goals = []

        # 生活方式偏好
        self.lifestyle_preferences = {
            "diet_restrictions": [],
            "exercise_preferences": [],
            "sleep_schedule": {
                "preferred_bedtime": None,
                "preferred_wake_time": None
            }
        }

        # 健康行为统计
        self.health_behaviors = {
            "average_daily_steps": None,
            "average_sleep_duration": None,
            "exercise_frequency": None,  # 每周运动次数
            "water_intake": None,        # 日均饮水量(ml)
            "meal_regularity": None      # 饮食规律性(0-100)
        }

class HealthProfileService:
    """健康画像服务，管理用户健康状况的全面视图"""

    def __init__(self, config: dict, repos: Any):
        """初始化健康画像服务

        Args:
            config: 服务配置
            repos: 依赖的数据仓库集合
        """
        self.config = config
        self.repos = repos

        # 如果有健康画像仓库，则使用它
        self.profile_repo = getattr(repos, "profile_repo", None)

        # 缓存最近访问的健康画像
        self.profile_cache = {}

        logger.info("健康画像服务初始化完成")

    async def get_profile(self, user_id: str) -> HealthProfile | None:
        """获取用户健康画像

        Args:
            user_id: 用户ID

        Returns:
            用户健康画像对象，如果不存在则返回None
        """
        # 首先尝试从缓存获取
        if user_id in self.profile_cache:
            logger.debug(f"从缓存获取用户健康画像: {user_id}")
            return self.profile_cache[user_id]

        # 如果没有缓存，从数据库查询
        if self.profile_repo:
            try:
                profile_data = await self.profile_repo.get_profile(user_id)
                if profile_data:
                    profile = self._deserialize_profile(profile_data)
                    # 更新缓存
                    self.profile_cache[user_id] = profile
                    logger.info(f"已从数据库获取用户健康画像: {user_id}")
                    return profile
                else:
                    logger.info(f"未找到用户健康画像: {user_id}")
                    return None
            except Exception as e:
                logger.error(f"获取用户健康画像失败: {str(e)}")
                return None
        else:
            logger.warning("健康画像仓库未配置")
            return None

    async def generate_profile(self, user_id: str) -> HealthProfile:
        """生成用户健康画像

        Args:
            user_id: 用户ID

        Returns:
            新生成的用户健康画像对象
        """
        # 创建新的健康画像
        profile = HealthProfile(user_id)

        # 如果有用户信息仓库，获取基本信息
        if hasattr(self.repos, "user_repo"):
            try:
                user_info = await self.repos.user_repo.get_user_info(user_id)
                if user_info:
                    profile.basic_info.update({
                        "height": user_info.get("height"),
                        "weight": user_info.get("weight"),
                        "gender": user_info.get("gender"),
                        "age": user_info.get("age"),
                        "blood_type": user_info.get("blood_type")
                    })
            except Exception as e:
                logger.error(f"获取用户基本信息失败: {str(e)}")

        # 保存健康画像
        await self.save_profile(profile)

        logger.info(f"成功生成用户健康画像: {user_id}")
        return profile

    async def update_profile(self, user_id: str, data: dict = None) -> HealthProfile | None:
        """更新用户健康画像

        Args:
            user_id: 用户ID
            data: 更新数据，如果为None则通过其他数据源更新

        Returns:
            更新后的用户健康画像对象，如果不存在则返回None
        """
        # 获取当前健康画像
        profile = await self.get_profile(user_id)
        if not profile:
            logger.info(f"用户健康画像不存在，正在创建: {user_id}")
            profile = await self.generate_profile(user_id)

        # 如果提供了更新数据，直接更新
        if data:
            self._update_profile_with_data(profile, data)
        else:
            # 否则，从各种数据源获取更新
            await self._update_profile_from_sources(profile)

        # 更新时间戳
        profile.updated_at = datetime.now()

        # 保存更新后的健康画像
        await self.save_profile(profile)

        logger.info(f"成功更新用户健康画像: {user_id}")
        return profile

    async def save_profile(self, profile: HealthProfile) -> bool:
        """保存用户健康画像

        Args:
            profile: 用户健康画像对象

        Returns:
            保存是否成功
        """
        if not self.profile_repo:
            logger.warning("健康画像仓库未配置，无法保存")
            return False

        try:
            # 序列化健康画像
            profile_data = self._serialize_profile(profile)

            # 保存到数据库
            success = await self.profile_repo.save_profile(profile.user_id, profile_data)

            # 更新缓存
            if success:
                self.profile_cache[profile.user_id] = profile
                logger.debug(f"用户健康画像已缓存: {profile.user_id}")

            logger.info(f"用户健康画像保存{'成功' if success else '失败'}: {profile.user_id}")
            return success
        except Exception as e:
            logger.error(f"保存用户健康画像失败: {str(e)}")
            return False

    async def get_tcm_constitution(self, user_id: str) -> dict:
        """获取用户中医体质信息

        Args:
            user_id: 用户ID

        Returns:
            中医体质信息字典
        """
        profile = await self.get_profile(user_id)
        if profile and profile.tcm_constitution.get("primary_type"):
            return profile.tcm_constitution

        # 如果没有体质信息或体质类型为空，尝试从体质服务获取
        try:
            if hasattr(self.repos, "constitution_repo"):
                constitution_data = await self.repos.constitution_repo.get_latest_constitution(user_id)
                if constitution_data:
                    # 更新体质信息
                    if profile:
                        profile.tcm_constitution = constitution_data
                        await self.save_profile(profile)
                    return constitution_data
        except Exception as e:
            logger.error(f"获取用户体质信息失败: {str(e)}")

        return {} if not profile else profile.tcm_constitution

    async def get_health_metrics(self, user_id: str) -> dict:
        """获取用户健康指标

        Args:
            user_id: 用户ID

        Returns:
            健康指标字典
        """
        profile = await self.get_profile(user_id)
        if not profile:
            return {}

        return profile.health_metrics

    async def get_emotional_state(self, user_id: str) -> dict:
        """获取用户情绪状态

        Args:
            user_id: 用户ID

        Returns:
            情绪状态字典
        """
        profile = await self.get_profile(user_id)
        if not profile:
            return {}

        return profile.emotional_state

    async def get_health_summary(self, user_id: str) -> dict:
        """获取用户健康摘要

        Args:
            user_id: 用户ID

        Returns:
            健康摘要字典
        """
        profile = await self.get_profile(user_id)
        if not profile:
            return {
                "user_id": user_id,
                "status": "unknown",
                "message": "未找到用户健康画像"
            }

        # 构建健康摘要
        summary = {
            "user_id": user_id,
            "status": "good",  # 默认状态
            "updated_at": profile.updated_at.isoformat(),
            "basic_info": {
                k: v for k, v in profile.basic_info.items() if v is not None
            },
            "constitution": profile.tcm_constitution.get("primary_type", "未知"),
            "metrics": {
                k: v for k, v in profile.health_metrics.items()
                if v is not None and k != "blood_pressure"
            },
            "goals": profile.health_goals,
            "risks": profile.health_risks[:3]  # 只返回前3个风险
        }

        # 添加血压信息(如果有)
        if (profile.health_metrics.get("blood_pressure", {}).get("systolic") and
            profile.health_metrics.get("blood_pressure", {}).get("diastolic")):
            bp = profile.health_metrics["blood_pressure"]
            summary["metrics"]["blood_pressure"] = f"{bp['systolic']}/{bp['diastolic']}"

        # 确定健康状态
        if profile.health_risks:
            summary["status"] = "attention"

        if profile.chronic_conditions:
            summary["status"] = "monitor"
            summary["chronic_conditions"] = profile.chronic_conditions

        return summary

    def _update_profile_with_data(self, profile: HealthProfile, data: dict) -> None:
        """使用提供的数据更新健康画像

        Args:
            profile: 健康画像对象
            data: 更新数据
        """
        # 更新基本信息
        if "basic_info" in data:
            profile.basic_info.update(data["basic_info"])

        # 更新体质信息
        if "tcm_constitution" in data:
            profile.tcm_constitution.update(data["tcm_constitution"])
            profile.tcm_constitution["updated_at"] = datetime.now()

        # 更新健康指标
        if "health_metrics" in data:
            for key, value in data["health_metrics"].items():
                if key == "blood_pressure" and isinstance(value, dict):
                    # 血压是嵌套的字典
                    if not profile.health_metrics.get("blood_pressure"):
                        profile.health_metrics["blood_pressure"] = {}
                    profile.health_metrics["blood_pressure"].update(value)
                else:
                    profile.health_metrics[key] = value

        # 更新健康风险
        if "health_risks" in data:
            profile.health_risks = data["health_risks"]

        # 更新慢性健康问题
        if "chronic_conditions" in data:
            profile.chronic_conditions = data["chronic_conditions"]

        # 更新情绪状态
        if "emotional_state" in data:
            profile.emotional_state.update(data["emotional_state"])
            profile.emotional_state["updated_at"] = datetime.now()

        # 更新健康目标
        if "health_goals" in data:
            profile.health_goals = data["health_goals"]

        # 更新生活方式偏好
        if "lifestyle_preferences" in data:
            for key, value in data["lifestyle_preferences"].items():
                if key == "sleep_schedule" and isinstance(value, dict):
                    # 睡眠计划是嵌套的字典
                    if not profile.lifestyle_preferences.get("sleep_schedule"):
                        profile.lifestyle_preferences["sleep_schedule"] = {}
                    profile.lifestyle_preferences["sleep_schedule"].update(value)
                else:
                    profile.lifestyle_preferences[key] = value

        # 更新健康行为
        if "health_behaviors" in data:
            profile.health_behaviors.update(data["health_behaviors"])

    async def _update_profile_from_sources(self, profile: HealthProfile) -> None:
        """从各种数据源更新健康画像

        Args:
            profile: 健康画像对象
        """
        # 获取传感器数据最新统计
        if hasattr(self.repos, "sensor_repo"):
            try:
                # 获取最近的心率数据
                heart_rate_data = await self.repos.sensor_repo.get_latest_sensor_data(
                    profile.user_id, "heart_rate", limit=24
                )
                if heart_rate_data:
                    # 计算静息心率(如最近24小时内的最低平均值)
                    hr_values = [d.get("value") for d in heart_rate_data if d.get("value")]
                    if hr_values:
                        profile.health_metrics["resting_heart_rate"] = min(hr_values)

                # 获取最近的血压数据
                bp_data = await self.repos.sensor_repo.get_latest_sensor_data(
                    profile.user_id, "blood_pressure", limit=1
                )
                if bp_data and bp_data[0].get("systolic") and bp_data[0].get("diastolic"):
                    profile.health_metrics["blood_pressure"] = {
                        "systolic": bp_data[0]["systolic"],
                        "diastolic": bp_data[0]["diastolic"]
                    }

                # 获取最近的睡眠数据
                sleep_data = await self.repos.sensor_repo.get_latest_sensor_data(
                    profile.user_id, "sleep", limit=7
                )
                if sleep_data:
                    # 计算平均睡眠时长和质量
                    durations = [d.get("duration") for d in sleep_data if d.get("duration")]
                    qualities = [d.get("quality") for d in sleep_data if d.get("quality")]

                    if durations:
                        profile.health_behaviors["average_sleep_duration"] = sum(durations) / len(durations)

                    if qualities:
                        profile.health_metrics["sleep_quality"] = sum(qualities) / len(qualities)

                # 获取最近的活动数据
                activity_data = await self.repos.sensor_repo.get_latest_sensor_data(
                    profile.user_id, "steps", limit=7
                )
                if activity_data:
                    # 计算平均步数
                    steps = [d.get("value") for d in activity_data if d.get("value")]
                    if steps:
                        profile.health_behaviors["average_daily_steps"] = sum(steps) / len(steps)

                        # 基于步数估算活动水平(示例算法)
                        avg_steps = sum(steps) / len(steps)
                        if avg_steps < 3000:
                            activity_level = 20
                        elif avg_steps < 5000:
                            activity_level = 40
                        elif avg_steps < 8000:
                            activity_level = 60
                        elif avg_steps < 12000:
                            activity_level = 80
                        else:
                            activity_level = 100

                        profile.health_metrics["activity_level"] = activity_level

            except Exception as e:
                logger.error(f"从传感器数据更新健康画像失败: {str(e)}")

        # 获取最新的体质评估
        if hasattr(self.repos, "constitution_repo"):
            try:
                constitution_data = await self.repos.constitution_repo.get_latest_constitution(profile.user_id)
                if constitution_data:
                    profile.tcm_constitution.update(constitution_data)
                    profile.tcm_constitution["updated_at"] = datetime.now()
            except Exception as e:
                logger.error(f"从体质评估更新健康画像失败: {str(e)}")

        # 获取最新的情绪评估
        if hasattr(self.repos, "emotion_repo"):
            try:
                emotion_data = await self.repos.emotion_repo.get_latest_emotion(profile.user_id)
                if emotion_data:
                    profile.emotional_state.update(emotion_data)
                    profile.emotional_state["updated_at"] = datetime.now()
            except Exception as e:
                logger.error(f"从情绪评估更新健康画像失败: {str(e)}")

        # 获取最新的健康风险评估
        if hasattr(self.repos, "risk_repo"):
            try:
                risk_data = await self.repos.risk_repo.get_health_risks(profile.user_id)
                if risk_data:
                    profile.health_risks = risk_data
            except Exception as e:
                logger.error(f"从风险评估更新健康画像失败: {str(e)}")

    def _serialize_profile(self, profile: HealthProfile) -> dict:
        """将健康画像对象序列化为可存储的格式

        Args:
            profile: 健康画像对象

        Returns:
            序列化后的健康画像数据
        """
        # 基本序列化，转换为字典
        profile_dict = {
            "user_id": profile.user_id,
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat(),
            "basic_info": profile.basic_info,
            "tcm_constitution": profile.tcm_constitution,
            "health_metrics": profile.health_metrics,
            "health_risks": profile.health_risks,
            "chronic_conditions": profile.chronic_conditions,
            "emotional_state": profile.emotional_state,
            "health_goals": profile.health_goals,
            "lifestyle_preferences": profile.lifestyle_preferences,
            "health_behaviors": profile.health_behaviors
        }

        # 处理日期时间字段
        if profile.tcm_constitution.get("updated_at"):
            profile_dict["tcm_constitution"]["updated_at"] = profile.tcm_constitution["updated_at"].isoformat()

        if profile.emotional_state.get("updated_at"):
            profile_dict["emotional_state"]["updated_at"] = profile.emotional_state["updated_at"].isoformat()

        return profile_dict

    def _deserialize_profile(self, profile_data: dict) -> HealthProfile:
        """将存储的数据反序列化为健康画像对象

        Args:
            profile_data: 序列化的健康画像数据

        Returns:
            健康画像对象
        """
        # 创建基本对象
        profile = HealthProfile(profile_data["user_id"])

        # 设置时间戳
        profile.created_at = datetime.fromisoformat(profile_data["created_at"])
        profile.updated_at = datetime.fromisoformat(profile_data["updated_at"])

        # 设置其他字段
        profile.basic_info = profile_data["basic_info"]
        profile.tcm_constitution = profile_data["tcm_constitution"]
        profile.health_metrics = profile_data["health_metrics"]
        profile.health_risks = profile_data["health_risks"]
        profile.chronic_conditions = profile_data["chronic_conditions"]
        profile.emotional_state = profile_data["emotional_state"]
        profile.health_goals = profile_data["health_goals"]
        profile.lifestyle_preferences = profile_data["lifestyle_preferences"]
        profile.health_behaviors = profile_data["health_behaviors"]

        # 处理日期时间字段
        if profile.tcm_constitution.get("updated_at"):
            profile.tcm_constitution["updated_at"] = datetime.fromisoformat(
                profile.tcm_constitution["updated_at"])

        if profile.emotional_state.get("updated_at"):
            profile.emotional_state["updated_at"] = datetime.fromisoformat(
                profile.emotional_state["updated_at"])

        return profile
