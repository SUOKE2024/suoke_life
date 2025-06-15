#!/usr/bin/env python

"""
用户体验优化模块 - 界面优化和交互改进
包含可用性分析、界面适配、交互优化、个性化体验等功能
"""

import logging
import time
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

# 可选的科学计算库导入
try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    UX_OPTIMIZER_AVAILABLE = True
except ImportError:
    # 如果没有安装科学计算库，使用简化版本
    UX_OPTIMIZER_AVAILABLE = False

    # 创建简化的替代类
    class np:
        @staticmethod
        def array(data):
            return list(data)

        @staticmethod
        def mean(data):
            return sum(data) / len(data) if data else 0

        @staticmethod
        def std(data):
            if not data:
                return 0
            mean_val = sum(data) / len(data)
            return (sum((x - mean_val) ** 2 for x in data) / len(data)) ** 0.5

        @staticmethod
        def median(data):
            sorted_data = sorted(data)
            n = len(sorted_data)
            if n % 2 == 0:
                return (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
            else:
                return sorted_data[n // 2]

    class KMeans:
        def __init__(self, n_clusters=3, random_state=None):
            self.n_clusters = n_clusters
            self.labels_ = []

        def fit(self, data):
            # 简化的聚类：随机分配

            self.labels_ = [secrets.randbelow(0, self.n_clusters - 1) for _ in data]
            return self

    class StandardScaler:
        def fit_transform(self, data):
            return data


import warnings

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)


class DeviceType(Enum):
    """设备类型枚举"""

    DESKTOP = "desktop"
    LAPTOP = "laptop"
    TABLET = "tablet"
    MOBILE = "mobile"
    WATCH = "watch"
    TV = "tv"
    UNKNOWN = "unknown"


class AccessibilityLevel(Enum):
    """无障碍级别枚举"""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InteractionMode(Enum):
    """交互模式枚举"""

    TOUCH = "touch"
    MOUSE = "mouse"
    KEYBOARD = "keyboard"
    VOICE = "voice"
    GESTURE = "gesture"
    EYE_TRACKING = "eye_tracking"


class UXMetricType(Enum):
    """用户体验指标类型枚举"""

    USABILITY = "usability"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    SATISFACTION = "satisfaction"
    ENGAGEMENT = "engagement"
    EFFICIENCY = "efficiency"


@dataclass
class DeviceProfile:
    """设备配置文件"""

    device_id: str
    device_type: DeviceType
    screen_width: int
    screen_height: int
    screen_density: float
    touch_support: bool
    keyboard_support: bool
    mouse_support: bool
    voice_support: bool
    gesture_support: bool
    operating_system: str
    browser: str
    capabilities: list[str]
    limitations: list[str]


@dataclass
class UserProfile:
    """用户配置文件"""

    user_id: str
    accessibility_needs: list[str]
    accessibility_level: AccessibilityLevel
    preferred_interaction_modes: list[InteractionMode]
    visual_preferences: dict[str, Any]
    motor_abilities: dict[str, Any]
    cognitive_preferences: dict[str, Any]
    language_preferences: list[str]
    experience_level: str  # beginner, intermediate, advanced
    usage_patterns: dict[str, Any]
    created_at: float
    updated_at: float


@dataclass
class UXMetric:
    """用户体验指标"""

    metric_id: str
    metric_type: UXMetricType
    name: str
    value: float
    unit: str
    target_value: float | None
    threshold_warning: float | None
    threshold_critical: float | None
    context: dict[str, Any]
    timestamp: float


@dataclass
class InteractionEvent:
    """交互事件"""

    event_id: str
    user_id: str
    device_id: str
    event_type: str
    element_id: str | None
    coordinates: tuple[int, int] | None
    duration: float
    success: bool
    error_message: str | None
    context: dict[str, Any]
    timestamp: float


@dataclass
class UXRecommendation:
    """用户体验建议"""

    recommendation_id: str
    category: str
    priority: str  # low, medium, high, critical
    title: str
    description: str
    implementation_effort: str  # low, medium, high
    expected_impact: str  # low, medium, high
    target_metrics: list[str]
    implementation_steps: list[str]
    created_at: float


class UsabilityAnalyzer:
    """可用性分析器"""

    def __init__(self) -> None:
        self.interaction_events = deque(maxlen=10000)
        self.usability_metrics = {}
        self.analysis_stats = {
            "events_analyzed": 0,
            "usability_issues": 0,
            "recommendations_generated": 0,
            "analysis_errors": 0,
        }

        # 可用性标准
        self.usability_standards = {
            "task_completion_rate": {"target": 0.95, "warning": 0.85, "critical": 0.75},
            "error_rate": {"target": 0.05, "warning": 0.10, "critical": 0.20},
            "task_completion_time": {
                "target": 30.0,
                "warning": 60.0,
                "critical": 120.0,
            },
            "user_satisfaction": {"target": 4.5, "warning": 3.5, "critical": 2.5},
            "learnability": {"target": 0.8, "warning": 0.6, "critical": 0.4},
            "efficiency": {"target": 0.9, "warning": 0.7, "critical": 0.5},
        }

    async def analyze_interaction_patterns(
        self, user_id: str, time_window: int = 3600
    ) -> dict[str, Any]:
        """分析用户交互模式"""
        try:
            # 获取时间窗口内的交互事件
            current_time = time.time()
            relevant_events = [
                event
                for event in self.interaction_events
                if event.user_id == user_id
                and current_time - event.timestamp <= time_window
            ]

            if not relevant_events:
                return {"error": "没有足够的交互数据"}

            # 分析交互模式
            patterns = {
                "total_interactions": len(relevant_events),
                "successful_interactions": len(
                    [e for e in relevant_events if e.success]
                ),
                "failed_interactions": len(
                    [e for e in relevant_events if not e.success]
                ),
                "average_duration": np.mean([e.duration for e in relevant_events]),
                "interaction_types": Counter([e.event_type for e in relevant_events]),
                "error_patterns": await self._analyze_error_patterns(relevant_events),
                "efficiency_metrics": await self._calculate_efficiency_metrics(
                    relevant_events
                ),
                "accessibility_issues": await self._detect_accessibility_issues(
                    relevant_events
                ),
            }

            # 计算可用性分数
            patterns["usability_score"] = await self._calculate_usability_score(
                patterns
            )

            self.analysis_stats["events_analyzed"] += len(relevant_events)

            logger.debug(
                f"交互模式分析完成，用户: {user_id}, 事件数: {len(relevant_events)}"
            )

            return patterns

        except Exception as e:
            self.analysis_stats["analysis_errors"] += 1
            logger.error(f"交互模式分析失败: {e!s}")
            return {"error": str(e)}

    async def detect_usability_issues(
        self, interaction_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """检测可用性问题"""
        issues = []

        try:
            # 检查任务完成率
            if (
                "successful_interactions" in interaction_data
                and "total_interactions" in interaction_data
            ):
                completion_rate = (
                    interaction_data["successful_interactions"]
                    / interaction_data["total_interactions"]
                )
                if (
                    completion_rate
                    < self.usability_standards["task_completion_rate"]["critical"]
                ):
                    issues.append(
                        {
                            "type": "low_completion_rate",
                            "severity": "critical",
                            "description": f"任务完成率过低: {completion_rate:.2%}",
                            "metric_value": completion_rate,
                            "target_value": self.usability_standards[
                                "task_completion_rate"
                            ]["target"],
                        }
                    )
                elif (
                    completion_rate
                    < self.usability_standards["task_completion_rate"]["warning"]
                ):
                    issues.append(
                        {
                            "type": "low_completion_rate",
                            "severity": "warning",
                            "description": f"任务完成率偏低: {completion_rate:.2%}",
                            "metric_value": completion_rate,
                            "target_value": self.usability_standards[
                                "task_completion_rate"
                            ]["target"],
                        }
                    )

            # 检查错误率
            if (
                "failed_interactions" in interaction_data
                and "total_interactions" in interaction_data
            ):
                error_rate = (
                    interaction_data["failed_interactions"]
                    / interaction_data["total_interactions"]
                )
                if error_rate > self.usability_standards["error_rate"]["critical"]:
                    issues.append(
                        {
                            "type": "high_error_rate",
                            "severity": "critical",
                            "description": f"错误率过高: {error_rate:.2%}",
                            "metric_value": error_rate,
                            "target_value": self.usability_standards["error_rate"][
                                "target"
                            ],
                        }
                    )
                elif error_rate > self.usability_standards["error_rate"]["warning"]:
                    issues.append(
                        {
                            "type": "high_error_rate",
                            "severity": "warning",
                            "description": f"错误率偏高: {error_rate:.2%}",
                            "metric_value": error_rate,
                            "target_value": self.usability_standards["error_rate"][
                                "target"
                            ],
                        }
                    )

            # 检查平均操作时间
            if "average_duration" in interaction_data:
                avg_duration = interaction_data["average_duration"]
                if (
                    avg_duration
                    > self.usability_standards["task_completion_time"]["critical"]
                ):
                    issues.append(
                        {
                            "type": "slow_task_completion",
                            "severity": "critical",
                            "description": f"任务完成时间过长: {avg_duration:.1f}秒",
                            "metric_value": avg_duration,
                            "target_value": self.usability_standards[
                                "task_completion_time"
                            ]["target"],
                        }
                    )
                elif (
                    avg_duration
                    > self.usability_standards["task_completion_time"]["warning"]
                ):
                    issues.append(
                        {
                            "type": "slow_task_completion",
                            "severity": "warning",
                            "description": f"任务完成时间偏长: {avg_duration:.1f}秒",
                            "metric_value": avg_duration,
                            "target_value": self.usability_standards[
                                "task_completion_time"
                            ]["target"],
                        }
                    )

            # 检查无障碍问题
            if "accessibility_issues" in interaction_data:
                for issue in interaction_data["accessibility_issues"]:
                    issues.append(
                        {
                            "type": "accessibility_issue",
                            "severity": issue.get("severity", "medium"),
                            "description": issue.get("description", "无障碍问题"),
                            "details": issue,
                        }
                    )

            self.analysis_stats["usability_issues"] += len(issues)

            return issues

        except Exception as e:
            logger.error(f"可用性问题检测失败: {e!s}")
            return []

    async def _analyze_error_patterns(
        self, events: list[InteractionEvent]
    ) -> dict[str, Any]:
        """分析错误模式"""
        failed_events = [e for e in events if not e.success]

        if not failed_events:
            return {"total_errors": 0}

        error_patterns = {
            "total_errors": len(failed_events),
            "error_types": Counter(
                [e.error_message for e in failed_events if e.error_message]
            ),
            "error_elements": Counter(
                [e.element_id for e in failed_events if e.element_id]
            ),
            "error_timing": [e.timestamp for e in failed_events],
            "repeated_errors": await self._find_repeated_errors(failed_events),
        }

        return error_patterns

    async def _find_repeated_errors(
        self, failed_events: list[InteractionEvent]
    ) -> list[dict[str, Any]]:
        """查找重复错误"""
        repeated_errors = []

        # 按用户和元素分组
        error_groups = defaultdict(list)
        for event in failed_events:
            key = f"{event.user_id}:{event.element_id}"
            error_groups[key].append(event)

        # 查找重复错误
        for key, events in error_groups.items():
            if len(events) >= 3:  # 3次或以上相同错误
                repeated_errors.append(
                    {
                        "user_element": key,
                        "error_count": len(events),
                        "error_messages": [e.error_message for e in events],
                        "time_span": max(e.timestamp for e in events)
                        - min(e.timestamp for e in events),
                    }
                )

        return repeated_errors

    async def _calculate_efficiency_metrics(
        self, events: list[InteractionEvent]
    ) -> dict[str, Any]:
        """计算效率指标"""
        if not events:
            return {}

        successful_events = [e for e in events if e.success]

        metrics = {
            "success_rate": len(successful_events) / len(events),
            "average_success_time": (
                np.mean([e.duration for e in successful_events])
                if successful_events
                else 0
            ),
            "median_success_time": (
                np.median([e.duration for e in successful_events])
                if successful_events
                else 0
            ),
            "efficiency_score": 0.0,
        }

        # 计算效率分数
        if metrics["success_rate"] > 0:
            # 基于成功率和平均时间的效率分数
            time_factor = max(
                0, 1 - (metrics["average_success_time"] - 10) / 60
            )  # 10秒为理想时间
            metrics["efficiency_score"] = metrics["success_rate"] * time_factor

        return metrics

    async def _detect_accessibility_issues(
        self, events: list[InteractionEvent]
    ) -> list[dict[str, Any]]:
        """检测无障碍问题"""
        issues = []

        # 检查长时间操作（可能表示困难）
        long_duration_events = [e for e in events if e.duration > 30]
        if len(long_duration_events) > len(events) * 0.2:  # 超过20%的操作时间过长
            issues.append(
                {
                    "type": "long_operation_time",
                    "severity": "medium",
                    "description": "操作时间过长，可能存在无障碍问题",
                    "affected_events": len(long_duration_events),
                }
            )

        # 检查重复失败（可能表示界面不清晰）
        failed_events = [e for e in events if not e.success]
        if len(failed_events) > len(events) * 0.15:  # 超过15%的操作失败
            issues.append(
                {
                    "type": "high_failure_rate",
                    "severity": "high",
                    "description": "操作失败率过高，可能存在界面可用性问题",
                    "failure_rate": len(failed_events) / len(events),
                }
            )

        return issues

    async def _calculate_usability_score(self, patterns: dict[str, Any]) -> float:
        """计算可用性分数"""
        try:
            score = 0.0
            weight_sum = 0.0

            # 成功率权重 40%
            if (
                "successful_interactions" in patterns
                and "total_interactions" in patterns
            ):
                success_rate = (
                    patterns["successful_interactions"] / patterns["total_interactions"]
                )
                score += success_rate * 0.4
                weight_sum += 0.4

            # 效率权重 30%
            if (
                "efficiency_metrics" in patterns
                and "efficiency_score" in patterns["efficiency_metrics"]
            ):
                efficiency = patterns["efficiency_metrics"]["efficiency_score"]
                score += efficiency * 0.3
                weight_sum += 0.3

            # 错误率权重 20%（反向）
            if "failed_interactions" in patterns and "total_interactions" in patterns:
                error_rate = (
                    patterns["failed_interactions"] / patterns["total_interactions"]
                )
                error_score = max(0, 1 - error_rate * 2)  # 错误率越低分数越高
                score += error_score * 0.2
                weight_sum += 0.2

            # 无障碍性权重 10%
            accessibility_score = 1.0
            if "accessibility_issues" in patterns:
                issue_count = len(patterns["accessibility_issues"])
                accessibility_score = max(0, 1 - issue_count * 0.1)
            score += accessibility_score * 0.1
            weight_sum += 0.1

            # 归一化分数
            if weight_sum > 0:
                score = score / weight_sum

            return min(1.0, max(0.0, score))

        except Exception as e:
            logger.error(f"可用性分数计算失败: {e!s}")
            return 0.5


class InterfaceAdapter:
    """界面适配器"""

    def __init__(self) -> None:
        self.device_profiles = {}
        self.user_profiles = {}
        self.adaptation_rules = {}
        self.adaptation_stats = {
            "adaptations_applied": 0,
            "devices_supported": 0,
            "user_preferences_learned": 0,
            "adaptation_errors": 0,
        }

    async def adapt_interface(
        self, user_id: str, device_id: str, interface_config: dict[str, Any]
    ) -> dict[str, Any]:
        """适配界面"""
        try:
            # 获取用户和设备配置
            user_profile = self.user_profiles.get(user_id)
            device_profile = self.device_profiles.get(device_id)

            if not user_profile or not device_profile:
                logger.warning(
                    f"缺少用户或设备配置: user={user_id}, device={device_id}"
                )
                return interface_config

            adapted_config = interface_config.copy()

            # 设备适配
            adapted_config = await self._adapt_for_device(
                adapted_config, device_profile
            )

            # 用户偏好适配
            adapted_config = await self._adapt_for_user(adapted_config, user_profile)

            # 无障碍适配
            adapted_config = await self._adapt_for_accessibility(
                adapted_config, user_profile
            )

            # 性能优化适配
            adapted_config = await self._adapt_for_performance(
                adapted_config, device_profile
            )

            self.adaptation_stats["adaptations_applied"] += 1

            logger.debug(f"界面适配完成: user={user_id}, device={device_id}")

            return adapted_config

        except Exception as e:
            self.adaptation_stats["adaptation_errors"] += 1
            logger.error(f"界面适配失败: {e!s}")
            return interface_config

    async def _adapt_for_device(
        self, config: dict[str, Any], device_profile: DeviceProfile
    ) -> dict[str, Any]:
        """设备适配"""
        adapted_config = config.copy()

        # 屏幕尺寸适配
        if device_profile.device_type == DeviceType.MOBILE:
            adapted_config["layout"] = "mobile"
            adapted_config["font_size"] = adapted_config.get("font_size", 16) + 2
            adapted_config["button_size"] = "large"
            adapted_config["spacing"] = "compact"
        elif device_profile.device_type == DeviceType.TABLET:
            adapted_config["layout"] = "tablet"
            adapted_config["font_size"] = adapted_config.get("font_size", 16) + 1
            adapted_config["button_size"] = "medium"
        elif device_profile.device_type == DeviceType.DESKTOP:
            adapted_config["layout"] = "desktop"
            adapted_config["button_size"] = "medium"
            adapted_config["spacing"] = "normal"

        # 交互方式适配
        if device_profile.touch_support:
            adapted_config["touch_targets"] = "large"
            adapted_config["hover_effects"] = False
        else:
            adapted_config["touch_targets"] = "normal"
            adapted_config["hover_effects"] = True

        # 屏幕密度适配
        if device_profile.screen_density > 2.0:
            adapted_config["image_quality"] = "high"
            adapted_config["icon_size"] = "large"
        else:
            adapted_config["image_quality"] = "medium"
            adapted_config["icon_size"] = "medium"

        return adapted_config

    async def _adapt_for_user(
        self, config: dict[str, Any], user_profile: UserProfile
    ) -> dict[str, Any]:
        """用户偏好适配"""
        adapted_config = config.copy()

        # 视觉偏好适配
        if user_profile.visual_preferences:
            visual_prefs = user_profile.visual_preferences

            if "font_size_preference" in visual_prefs:
                base_size = adapted_config.get("font_size", 16)
                size_multiplier = visual_prefs["font_size_preference"]
                adapted_config["font_size"] = int(base_size * size_multiplier)

            if "contrast_preference" in visual_prefs:
                if visual_prefs["contrast_preference"] == "high":
                    adapted_config["theme"] = "high_contrast"
                elif visual_prefs["contrast_preference"] == "dark":
                    adapted_config["theme"] = "dark"

            if "color_scheme" in visual_prefs:
                adapted_config["color_scheme"] = visual_prefs["color_scheme"]

        # 认知偏好适配
        if user_profile.cognitive_preferences:
            cognitive_prefs = user_profile.cognitive_preferences

            if cognitive_prefs.get("simplified_interface", False):
                adapted_config["complexity"] = "simple"
                adapted_config["animations"] = "minimal"

            if cognitive_prefs.get("clear_navigation", False):
                adapted_config["navigation_style"] = "breadcrumb"
                adapted_config["progress_indicators"] = True

        # 经验水平适配
        if user_profile.experience_level == "beginner":
            adapted_config["help_tooltips"] = True
            adapted_config["confirmation_dialogs"] = True
            adapted_config["guided_tour"] = True
        elif user_profile.experience_level == "advanced":
            adapted_config["shortcuts"] = True
            adapted_config["advanced_features"] = True
            adapted_config["confirmation_dialogs"] = False

        return adapted_config

    async def _adapt_for_accessibility(
        self, config: dict[str, Any], user_profile: UserProfile
    ) -> dict[str, Any]:
        """无障碍适配"""
        adapted_config = config.copy()

        # 视觉无障碍
        if "visual_impairment" in user_profile.accessibility_needs:
            adapted_config["font_size"] = max(adapted_config.get("font_size", 16), 18)
            adapted_config["contrast"] = "high"
            adapted_config["focus_indicators"] = "strong"
            adapted_config["screen_reader_support"] = True

        # 听觉无障碍
        if "hearing_impairment" in user_profile.accessibility_needs:
            adapted_config["captions"] = True
            adapted_config["visual_alerts"] = True
            adapted_config["sound_alternatives"] = True

        # 运动无障碍
        if "motor_impairment" in user_profile.accessibility_needs:
            adapted_config["large_click_targets"] = True
            adapted_config["keyboard_navigation"] = True
            adapted_config["voice_control"] = True
            adapted_config["gesture_alternatives"] = True

        # 认知无障碍
        if "cognitive_impairment" in user_profile.accessibility_needs:
            adapted_config["simple_language"] = True
            adapted_config["clear_instructions"] = True
            adapted_config["error_prevention"] = True
            adapted_config["consistent_navigation"] = True

        return adapted_config

    async def _adapt_for_performance(
        self, config: dict[str, Any], device_profile: DeviceProfile
    ) -> dict[str, Any]:
        """性能优化适配"""
        adapted_config = config.copy()

        # 低端设备优化
        if device_profile.device_type in [DeviceType.MOBILE, DeviceType.WATCH]:
            adapted_config["animations"] = "reduced"
            adapted_config["image_compression"] = "high"
            adapted_config["lazy_loading"] = True
            adapted_config["cache_strategy"] = "aggressive"

        # 网络优化
        adapted_config["resource_bundling"] = True
        adapted_config["compression"] = True

        return adapted_config

    async def register_device(self, device_profile: DeviceProfile) -> bool:
        """注册设备"""
        try:
            self.device_profiles[device_profile.device_id] = device_profile
            self.adaptation_stats["devices_supported"] += 1

            logger.info(f"设备注册成功: {device_profile.device_id}")
            return True

        except Exception as e:
            logger.error(f"设备注册失败: {e!s}")
            return False

    async def register_user(self, user_profile: UserProfile) -> bool:
        """注册用户"""
        try:
            self.user_profiles[user_profile.user_id] = user_profile
            self.adaptation_stats["user_preferences_learned"] += 1

            logger.info(f"用户注册成功: {user_profile.user_id}")
            return True

        except Exception as e:
            logger.error(f"用户注册失败: {e!s}")
            return False


class PersonalizationEngine:
    """个性化引擎"""

    def __init__(self) -> None:
        self.user_behaviors = defaultdict(list)
        self.preference_models = {}
        self.personalization_stats = {
            "users_profiled": 0,
            "preferences_learned": 0,
            "recommendations_generated": 0,
            "personalization_errors": 0,
        }

    async def learn_user_preferences(
        self, user_id: str, interaction_history: list[InteractionEvent]
    ) -> dict[str, Any]:
        """学习用户偏好"""
        try:
            if not interaction_history:
                return {"error": "没有交互历史数据"}

            # 分析交互模式
            preferences = {
                "interaction_patterns": await self._analyze_interaction_patterns(
                    interaction_history
                ),
                "element_preferences": await self._analyze_element_preferences(
                    interaction_history
                ),
                "timing_preferences": await self._analyze_timing_preferences(
                    interaction_history
                ),
                "error_patterns": await self._analyze_user_errors(interaction_history),
                "efficiency_patterns": await self._analyze_efficiency_patterns(
                    interaction_history
                ),
            }

            # 生成个性化建议
            preferences["personalization_recommendations"] = (
                await self._generate_personalization_recommendations(preferences)
            )

            # 更新用户模型
            self.preference_models[user_id] = preferences
            self.personalization_stats["users_profiled"] += 1
            self.personalization_stats["preferences_learned"] += len(preferences)

            logger.debug(f"用户偏好学习完成: {user_id}")

            return preferences

        except Exception as e:
            self.personalization_stats["personalization_errors"] += 1
            logger.error(f"用户偏好学习失败: {e!s}")
            return {"error": str(e)}

    async def generate_personalized_interface(
        self, user_id: str, base_interface: dict[str, Any]
    ) -> dict[str, Any]:
        """生成个性化界面"""
        try:
            if user_id not in self.preference_models:
                logger.warning(f"用户 {user_id} 没有偏好模型")
                return base_interface

            preferences = self.preference_models[user_id]
            personalized_interface = base_interface.copy()

            # 应用交互模式偏好
            if "interaction_patterns" in preferences:
                personalized_interface = await self._apply_interaction_preferences(
                    personalized_interface, preferences["interaction_patterns"]
                )

            # 应用元素偏好
            if "element_preferences" in preferences:
                personalized_interface = await self._apply_element_preferences(
                    personalized_interface, preferences["element_preferences"]
                )

            # 应用时间偏好
            if "timing_preferences" in preferences:
                personalized_interface = await self._apply_timing_preferences(
                    personalized_interface, preferences["timing_preferences"]
                )

            # 应用效率优化
            if "efficiency_patterns" in preferences:
                personalized_interface = await self._apply_efficiency_optimizations(
                    personalized_interface, preferences["efficiency_patterns"]
                )

            logger.debug(f"个性化界面生成完成: {user_id}")

            return personalized_interface

        except Exception as e:
            self.personalization_stats["personalization_errors"] += 1
            logger.error(f"个性化界面生成失败: {e!s}")
            return base_interface

    async def _analyze_interaction_patterns(
        self, history: list[InteractionEvent]
    ) -> dict[str, Any]:
        """分析交互模式"""
        patterns = {
            "preferred_elements": Counter(
                [e.element_id for e in history if e.element_id]
            ),
            "interaction_types": Counter([e.event_type for e in history]),
            "success_patterns": {},
            "failure_patterns": {},
        }

        # 分析成功和失败模式
        successful_events = [e for e in history if e.success]
        failed_events = [e for e in history if not e.success]

        if successful_events:
            patterns["success_patterns"] = {
                "common_elements": Counter(
                    [e.element_id for e in successful_events if e.element_id]
                ),
                "common_types": Counter([e.event_type for e in successful_events]),
                "average_duration": np.mean([e.duration for e in successful_events]),
            }

        if failed_events:
            patterns["failure_patterns"] = {
                "problematic_elements": Counter(
                    [e.element_id for e in failed_events if e.element_id]
                ),
                "problematic_types": Counter([e.event_type for e in failed_events]),
                "average_duration": np.mean([e.duration for e in failed_events]),
            }

        return patterns

    async def _analyze_element_preferences(
        self, history: list[InteractionEvent]
    ) -> dict[str, Any]:
        """分析元素偏好"""
        element_stats = defaultdict(
            lambda: {"interactions": 0, "successes": 0, "total_time": 0}
        )

        for event in history:
            if event.element_id:
                element_stats[event.element_id]["interactions"] += 1
                element_stats[event.element_id]["total_time"] += event.duration
                if event.success:
                    element_stats[event.element_id]["successes"] += 1

        # 计算偏好分数
        preferences = {}
        for element_id, stats in element_stats.items():
            success_rate = (
                stats["successes"] / stats["interactions"]
                if stats["interactions"] > 0
                else 0
            )
            avg_time = (
                stats["total_time"] / stats["interactions"]
                if stats["interactions"] > 0
                else 0
            )

            # 偏好分数 = 成功率 * 使用频率 / 平均时间
            frequency_score = min(stats["interactions"] / len(history), 1.0)
            time_score = max(0, 1 - avg_time / 60)  # 60秒为基准

            preferences[element_id] = {
                "preference_score": success_rate * frequency_score * time_score,
                "success_rate": success_rate,
                "frequency": frequency_score,
                "efficiency": time_score,
            }

        return preferences

    async def _analyze_timing_preferences(
        self, history: list[InteractionEvent]
    ) -> dict[str, Any]:
        """分析时间偏好"""
        if not history:
            return {}

        # 按小时分组分析活跃时间
        hourly_activity = defaultdict(int)
        for event in history:
            hour = datetime.fromtimestamp(event.timestamp).hour
            hourly_activity[hour] += 1

        # 分析操作速度偏好
        durations = [e.duration for e in history]

        timing_preferences = {
            "active_hours": dict(hourly_activity),
            "peak_hours": sorted(
                hourly_activity.items(), key=lambda x: x[1], reverse=True
            )[:3],
            "average_operation_time": np.mean(durations),
            "preferred_pace": (
                "fast"
                if np.mean(durations) < 10
                else "normal" if np.mean(durations) < 30 else "slow"
            ),
            "consistency": np.std(durations),  # 操作时间的一致性
        }

        return timing_preferences

    async def _analyze_user_errors(
        self, history: list[InteractionEvent]
    ) -> dict[str, Any]:
        """分析用户错误模式"""
        failed_events = [e for e in history if not e.success]

        if not failed_events:
            return {"error_rate": 0}

        error_patterns = {
            "error_rate": len(failed_events) / len(history),
            "common_errors": Counter(
                [e.error_message for e in failed_events if e.error_message]
            ),
            "error_elements": Counter(
                [e.element_id for e in failed_events if e.element_id]
            ),
            "error_recovery_time": [],
            "repeated_errors": 0,
        }

        # 分析错误恢复时间
        for i, event in enumerate(history):
            if not event.success and i < len(history) - 1:
                next_success = None
                for j in range(i + 1, len(history)):
                    if history[j].success and history[j].element_id == event.element_id:
                        next_success = history[j]
                        break

                if next_success:
                    recovery_time = next_success.timestamp - event.timestamp
                    error_patterns["error_recovery_time"].append(recovery_time)

        # 计算重复错误
        error_sequences = []
        for i in range(len(failed_events) - 1):
            if (
                failed_events[i].element_id == failed_events[i + 1].element_id
                and failed_events[i + 1].timestamp - failed_events[i].timestamp < 300
            ):  # 5分钟内
                error_patterns["repeated_errors"] += 1

        return error_patterns

    async def _analyze_efficiency_patterns(
        self, history: list[InteractionEvent]
    ) -> dict[str, Any]:
        """分析效率模式"""
        successful_events = [e for e in history if e.success]

        if not successful_events:
            return {}

        # 按任务类型分组分析效率
        task_efficiency = defaultdict(list)
        for event in successful_events:
            task_efficiency[event.event_type].append(event.duration)

        efficiency_patterns = {
            "overall_efficiency": np.mean([e.duration for e in successful_events]),
            "task_efficiency": {},
            "improvement_trend": await self._calculate_improvement_trend(
                successful_events
            ),
            "efficiency_variance": np.std([e.duration for e in successful_events]),
        }

        # 计算各任务类型的效率
        for task_type, durations in task_efficiency.items():
            efficiency_patterns["task_efficiency"][task_type] = {
                "average_time": np.mean(durations),
                "best_time": min(durations),
                "consistency": np.std(durations),
            }

        return efficiency_patterns

    async def _calculate_improvement_trend(
        self, events: list[InteractionEvent]
    ) -> float:
        """计算改进趋势"""
        if len(events) < 10:
            return 0.0

        # 将事件按时间排序并分组
        sorted_events = sorted(events, key=lambda x: x.timestamp)

        # 计算前半部分和后半部分的平均时间
        mid_point = len(sorted_events) // 2
        early_avg = np.mean([e.duration for e in sorted_events[:mid_point]])
        late_avg = np.mean([e.duration for e in sorted_events[mid_point:]])

        # 改进趋势 = (早期时间 - 后期时间) / 早期时间
        if early_avg > 0:
            improvement = (early_avg - late_avg) / early_avg
            return improvement

        return 0.0

    async def _generate_personalization_recommendations(
        self, preferences: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """生成个性化建议"""
        recommendations = []

        # 基于交互模式的建议
        if "interaction_patterns" in preferences:
            patterns = preferences["interaction_patterns"]

            # 推荐常用元素
            if "preferred_elements" in patterns:
                top_elements = patterns["preferred_elements"].most_common(3)
                if top_elements:
                    recommendations.append(
                        {
                            "type": "element_prioritization",
                            "description": "将常用功能放在更显眼的位置",
                            "elements": [elem[0] for elem in top_elements],
                        }
                    )

        # 基于错误模式的建议
        if "error_patterns" in preferences:
            error_patterns = preferences["error_patterns"]

            if error_patterns.get("error_rate", 0) > 0.1:  # 错误率超过10%
                recommendations.append(
                    {
                        "type": "error_reduction",
                        "description": "提供更清晰的操作指导和错误预防",
                        "priority": "high",
                    }
                )

        # 基于效率模式的建议
        if "efficiency_patterns" in preferences:
            efficiency = preferences["efficiency_patterns"]

            if efficiency.get("improvement_trend", 0) > 0.2:  # 有明显改进趋势
                recommendations.append(
                    {
                        "type": "advanced_features",
                        "description": "提供高级功能和快捷方式",
                        "priority": "medium",
                    }
                )

        self.personalization_stats["recommendations_generated"] += len(recommendations)

        return recommendations

    async def _apply_interaction_preferences(
        self, interface: dict[str, Any], patterns: dict[str, Any]
    ) -> dict[str, Any]:
        """应用交互偏好"""
        adapted_interface = interface.copy()

        # 优先显示常用元素
        if "preferred_elements" in patterns:
            top_elements = [
                elem[0] for elem in patterns["preferred_elements"].most_common(5)
            ]
            adapted_interface["priority_elements"] = top_elements

        # 根据成功模式调整界面
        if "success_patterns" in patterns:
            success_patterns = patterns["success_patterns"]
            if "common_types" in success_patterns:
                preferred_interactions = list(success_patterns["common_types"].keys())
                adapted_interface["preferred_interactions"] = preferred_interactions

        return adapted_interface

    async def _apply_element_preferences(
        self, interface: dict[str, Any], preferences: dict[str, Any]
    ) -> dict[str, Any]:
        """应用元素偏好"""
        adapted_interface = interface.copy()

        # 根据偏好分数调整元素布局
        high_preference_elements = [
            elem_id
            for elem_id, prefs in preferences.items()
            if prefs.get("preference_score", 0) > 0.7
        ]

        if high_preference_elements:
            adapted_interface["featured_elements"] = high_preference_elements
            adapted_interface["layout_priority"] = "user_preferred"

        return adapted_interface

    async def _apply_timing_preferences(
        self, interface: dict[str, Any], timing_prefs: dict[str, Any]
    ) -> dict[str, Any]:
        """应用时间偏好"""
        adapted_interface = interface.copy()

        # 根据操作速度偏好调整界面
        if "preferred_pace" in timing_prefs:
            pace = timing_prefs["preferred_pace"]

            if pace == "fast":
                adapted_interface["animations"] = "fast"
                adapted_interface["shortcuts"] = True
                adapted_interface["confirmations"] = "minimal"
            elif pace == "slow":
                adapted_interface["animations"] = "slow"
                adapted_interface["help_text"] = "detailed"
                adapted_interface["confirmations"] = "detailed"

        return adapted_interface

    async def _apply_efficiency_optimizations(
        self, interface: dict[str, Any], efficiency_patterns: dict[str, Any]
    ) -> dict[str, Any]:
        """应用效率优化"""
        adapted_interface = interface.copy()

        # 根据效率模式优化界面
        if "improvement_trend" in efficiency_patterns:
            trend = efficiency_patterns["improvement_trend"]

            if trend > 0.2:  # 用户在快速改进
                adapted_interface["complexity"] = "advanced"
                adapted_interface["shortcuts"] = True
            elif trend < -0.1:  # 用户效率在下降
                adapted_interface["complexity"] = "simple"
                adapted_interface["guidance"] = "enhanced"

        return adapted_interface


class UXOptimizer:
    """用户体验优化主类"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化用户体验优化系统

        Args:
            config: 服务配置
        """
        self.config = config
        self.enabled = (
            config.get("ux_optimization", {}).get("enabled", True)
            and UX_OPTIMIZER_AVAILABLE
        )

        # 核心组件
        if UX_OPTIMIZER_AVAILABLE:
            self.usability_analyzer = UsabilityAnalyzer()
            self.interface_adapter = InterfaceAdapter()
            self.personalization_engine = PersonalizationEngine()
        else:
            self.usability_analyzer = None
            self.interface_adapter = None
            self.personalization_engine = None

        # UX指标
        self.ux_metrics = {}
        self.recommendations = {}

        if UX_OPTIMIZER_AVAILABLE:
            logger.info(f"用户体验优化系统初始化完成 - 启用: {self.enabled} (完整功能)")
        else:
            logger.info(
                f"用户体验优化系统初始化完成 - 启用: {self.enabled} (简化功能，缺少科学计算库)"
            )

    async def optimize_user_experience(
        self,
        user_id: str,
        device_id: str,
        interface_config: dict[str, Any],
        interaction_history: list[InteractionEvent] | None = None,
    ) -> dict[str, Any]:
        """优化用户体验"""
        if not self.enabled or not self.interface_adapter:
            return interface_config

        try:
            optimized_config = interface_config.copy()

            # 设备和用户适配
            optimized_config = await self.interface_adapter.adapt_interface(
                user_id, device_id, optimized_config
            )

            # 个性化优化
            if interaction_history:
                # 学习用户偏好
                await self.personalization_engine.learn_user_preferences(
                    user_id, interaction_history
                )

                # 应用个性化
                optimized_config = (
                    await self.personalization_engine.generate_personalized_interface(
                        user_id, optimized_config
                    )
                )

            # 可用性分析和优化
            if interaction_history:
                usability_analysis = (
                    await self.usability_analyzer.analyze_interaction_patterns(user_id)
                )

                if "usability_score" in usability_analysis:
                    # 根据可用性分数调整界面
                    if usability_analysis["usability_score"] < 0.7:
                        optimized_config = await self._apply_usability_improvements(
                            optimized_config, usability_analysis
                        )

            logger.debug(f"用户体验优化完成: user={user_id}, device={device_id}")

            return optimized_config

        except Exception as e:
            logger.error(f"用户体验优化失败: {e!s}")
            return interface_config

    async def analyze_ux_metrics(
        self, user_id: str, time_window: int = 3600
    ) -> dict[str, Any]:
        """分析用户体验指标"""
        try:
            # 可用性分析
            usability_analysis = (
                await self.usability_analyzer.analyze_interaction_patterns(
                    user_id, time_window
                )
            )

            # 检测可用性问题
            usability_issues = await self.usability_analyzer.detect_usability_issues(
                usability_analysis
            )

            # 生成UX指标
            ux_metrics = {
                "usability_score": usability_analysis.get("usability_score", 0.5),
                "task_completion_rate": 0.0,
                "error_rate": 0.0,
                "efficiency_score": 0.0,
                "user_satisfaction": 0.0,
                "accessibility_score": 1.0,
            }

            # 计算具体指标
            if (
                "successful_interactions" in usability_analysis
                and "total_interactions" in usability_analysis
            ):
                ux_metrics["task_completion_rate"] = (
                    usability_analysis["successful_interactions"]
                    / usability_analysis["total_interactions"]
                )
                ux_metrics["error_rate"] = (
                    usability_analysis["failed_interactions"]
                    / usability_analysis["total_interactions"]
                )

            if "efficiency_metrics" in usability_analysis:
                ux_metrics["efficiency_score"] = usability_analysis[
                    "efficiency_metrics"
                ].get("efficiency_score", 0.0)

            # 根据问题数量计算无障碍分数
            accessibility_issues = [
                issue
                for issue in usability_issues
                if issue.get("type") == "accessibility_issue"
            ]
            if accessibility_issues:
                ux_metrics["accessibility_score"] = max(
                    0, 1 - len(accessibility_issues) * 0.2
                )

            # 计算综合满意度分数
            ux_metrics["user_satisfaction"] = (
                ux_metrics["usability_score"] * 0.3
                + ux_metrics["task_completion_rate"] * 0.25
                + (1 - ux_metrics["error_rate"]) * 0.2
                + ux_metrics["efficiency_score"] * 0.15
                + ux_metrics["accessibility_score"] * 0.1
            )

            return {
                "metrics": ux_metrics,
                "issues": usability_issues,
                "analysis": usability_analysis,
                "timestamp": time.time(),
            }

        except Exception as e:
            logger.error(f"UX指标分析失败: {e!s}")
            return {"error": str(e)}

    async def generate_ux_recommendations(
        self, ux_analysis: dict[str, Any]
    ) -> list[UXRecommendation]:
        """生成用户体验建议"""
        recommendations = []

        try:
            metrics = ux_analysis.get("metrics", {})
            issues = ux_analysis.get("issues", [])

            # 基于指标生成建议
            if metrics.get("task_completion_rate", 1.0) < 0.8:
                recommendations.append(
                    UXRecommendation(
                        recommendation_id=f"rec_{int(time.time())}_completion",
                        category="usability",
                        priority="high",
                        title="提高任务完成率",
                        description="任务完成率偏低，需要简化操作流程和提供更清晰的指导",
                        implementation_effort="medium",
                        expected_impact="high",
                        target_metrics=["task_completion_rate"],
                        implementation_steps=[
                            "分析失败任务的共同特征",
                            "简化复杂操作流程",
                            "添加操作指导和提示",
                            "优化错误处理机制",
                        ],
                        created_at=time.time(),
                    )
                )

            if metrics.get("error_rate", 0.0) > 0.1:
                recommendations.append(
                    UXRecommendation(
                        recommendation_id=f"rec_{int(time.time())}_errors",
                        category="usability",
                        priority="high",
                        title="降低错误率",
                        description="用户错误率过高，需要改进界面设计和错误预防机制",
                        implementation_effort="medium",
                        expected_impact="high",
                        target_metrics=["error_rate"],
                        implementation_steps=[
                            "分析常见错误类型",
                            "改进界面元素的可识别性",
                            "添加操作确认机制",
                            "提供更好的错误恢复选项",
                        ],
                        created_at=time.time(),
                    )
                )

            if metrics.get("efficiency_score", 1.0) < 0.7:
                recommendations.append(
                    UXRecommendation(
                        recommendation_id=f"rec_{int(time.time())}_efficiency",
                        category="performance",
                        priority="medium",
                        title="提高操作效率",
                        description="用户操作效率偏低，需要优化界面布局和交互方式",
                        implementation_effort="medium",
                        expected_impact="medium",
                        target_metrics=["efficiency_score"],
                        implementation_steps=[
                            "优化常用功能的访问路径",
                            "提供键盘快捷键",
                            "改进界面响应速度",
                            "减少不必要的操作步骤",
                        ],
                        created_at=time.time(),
                    )
                )

            if metrics.get("accessibility_score", 1.0) < 0.8:
                recommendations.append(
                    UXRecommendation(
                        recommendation_id=f"rec_{int(time.time())}_accessibility",
                        category="accessibility",
                        priority="high",
                        title="改进无障碍性",
                        description="无障碍性需要改进，确保所有用户都能有效使用系统",
                        implementation_effort="high",
                        expected_impact="high",
                        target_metrics=["accessibility_score"],
                        implementation_steps=[
                            "添加键盘导航支持",
                            "改进颜色对比度",
                            "提供屏幕阅读器支持",
                            "添加替代文本和标签",
                        ],
                        created_at=time.time(),
                    )
                )

            # 基于具体问题生成建议
            for issue in issues:
                if issue.get("severity") in ["high", "critical"]:
                    recommendations.append(
                        UXRecommendation(
                            recommendation_id=f"rec_{int(time.time())}_issue_{issue.get('type', 'unknown')}",
                            category="issue_resolution",
                            priority=issue.get("severity", "medium"),
                            title=f"解决{issue.get('type', '未知')}问题",
                            description=issue.get(
                                "description", "需要解决的用户体验问题"
                            ),
                            implementation_effort="medium",
                            expected_impact="medium",
                            target_metrics=[issue.get("type", "unknown")],
                            implementation_steps=[
                                "详细分析问题原因",
                                "设计解决方案",
                                "实施改进措施",
                                "验证改进效果",
                            ],
                            created_at=time.time(),
                        )
                    )

            return recommendations

        except Exception as e:
            logger.error(f"UX建议生成失败: {e!s}")
            return []

    async def _apply_usability_improvements(
        self, config: dict[str, Any], usability_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """应用可用性改进"""
        improved_config = config.copy()

        usability_score = usability_analysis.get("usability_score", 1.0)

        if usability_score < 0.5:
            # 严重可用性问题，应用激进改进
            improved_config["complexity"] = "simple"
            improved_config["help_text"] = "detailed"
            improved_config["confirmations"] = "detailed"
            improved_config["error_prevention"] = True
            improved_config["guided_tour"] = True
        elif usability_score < 0.7:
            # 中等可用性问题，应用适度改进
            improved_config["help_tooltips"] = True
            improved_config["progress_indicators"] = True
            improved_config["error_recovery"] = "enhanced"

        # 根据具体问题应用改进
        if "accessibility_issues" in usability_analysis:
            issues = usability_analysis["accessibility_issues"]
            for issue in issues:
                if issue.get("type") == "long_operation_time":
                    improved_config["loading_indicators"] = True
                    improved_config["progress_feedback"] = True
                elif issue.get("type") == "high_failure_rate":
                    improved_config["error_prevention"] = True
                    improved_config["input_validation"] = "real_time"

        return improved_config

    def get_ux_stats(self) -> dict[str, Any]:
        """获取用户体验统计信息"""
        stats = {
            "enabled": self.enabled,
            "total_recommendations": len(self.recommendations),
        }

        # 在简化模式下，组件可能为None
        if self.usability_analyzer:
            stats["usability_stats"] = self.usability_analyzer.analysis_stats
        else:
            stats["usability_stats"] = {}

        if self.interface_adapter:
            stats["adaptation_stats"] = self.interface_adapter.adaptation_stats
            stats["supported_devices"] = len(self.interface_adapter.device_profiles)
        else:
            stats["adaptation_stats"] = {}
            stats["supported_devices"] = 0

        if self.personalization_engine:
            stats["personalization_stats"] = (
                self.personalization_engine.personalization_stats
            )
            stats["active_users"] = len(self.personalization_engine.preference_models)
        else:
            stats["personalization_stats"] = {}
            stats["active_users"] = 0

        return stats
