#!/usr/bin/env python

"""
时间感知模块 - 高级时间感知和时间模式分析
包含时间模式识别、行为预测、健康时间管理、生物钟分析等功能
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class TimePattern(Enum):
    """时间模式类型枚举"""

    DAILY_ROUTINE = "daily_routine"
    WEEKLY_PATTERN = "weekly_pattern"
    SEASONAL_PATTERN = "seasonal_pattern"
    CIRCADIAN_RHYTHM = "circadian_rhythm"
    WORK_SCHEDULE = "work_schedule"
    SLEEP_CYCLE = "sleep_cycle"
    MEAL_TIMING = "meal_timing"
    EXERCISE_TIMING = "exercise_timing"


class TimeContext(Enum):
    """时间上下文枚举"""

    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"
    DAWN = "dawn"
    DUSK = "dusk"
    WORKDAY = "workday"
    WEEKEND = "weekend"
    HOLIDAY = "holiday"


@dataclass
class TimeEvent:
    """时间事件数据结构"""

    event_id: str
    user_id: str
    event_type: str
    timestamp: float
    duration: float | None = None
    context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TimePatternAnalysis:
    """时间模式分析结果"""

    pattern_type: TimePattern
    confidence: float
    frequency: float
    typical_times: list[tuple[int, int]]  # (hour, minute) pairs
    duration_stats: dict[str, float]
    variability: float
    trend: str  # "stable", "increasing", "decreasing"
    last_updated: float


@dataclass
class CircadianProfile:
    """生物钟档案"""

    user_id: str
    chronotype: str  # "morning", "evening", "intermediate"
    sleep_onset: tuple[int, int]  # (hour, minute)
    wake_time: tuple[int, int]
    sleep_duration: float  # hours
    energy_peaks: list[tuple[int, int]]
    energy_dips: list[tuple[int, int]]
    optimal_work_hours: list[tuple[int, int]]
    meal_windows: list[tuple[int, int]]
    confidence: float
    last_updated: float


class TimePatternRecognizer:
    """时间模式识别器"""

    def __init__(self) -> None:
        self.user_patterns = defaultdict(
            dict
        )  # user_id -> pattern_type -> TimePatternAnalysis
        self.event_history = defaultdict(deque)  # user_id -> deque of TimeEvent
        self.pattern_templates = self._initialize_pattern_templates()

    def _initialize_pattern_templates(self) -> dict[str, dict[str, Any]]:
        """初始化时间模式模板"""
        return {
            "morning_routine": {
                "typical_start": (6, 0),
                "typical_end": (9, 0),
                "expected_duration": 3.0,  # hours
                "activities": ["wake_up", "personal_care", "breakfast", "commute"],
            },
            "work_schedule": {
                "typical_start": (9, 0),
                "typical_end": (17, 0),
                "expected_duration": 8.0,
                "activities": ["work", "meetings", "breaks", "lunch"],
            },
            "evening_routine": {
                "typical_start": (18, 0),
                "typical_end": (22, 0),
                "expected_duration": 4.0,
                "activities": ["dinner", "relaxation", "family_time", "entertainment"],
            },
            "sleep_cycle": {
                "typical_start": (22, 0),
                "typical_end": (6, 0),
                "expected_duration": 8.0,
                "activities": ["preparation", "sleep", "wake_up"],
            },
        }

    def add_time_event(self, event: TimeEvent):
        """添加时间事件"""
        try:
            self.event_history[event.user_id].append(event)

            # 保持最近1000个事件
            if len(self.event_history[event.user_id]) > 1000:
                self.event_history[event.user_id].popleft()

            # 触发模式分析
            self._analyze_patterns(event.user_id)

        except Exception as e:
            logger.error(f"添加时间事件失败: {e!s}")

    def _analyze_patterns(self, user_id: str):
        """分析用户的时间模式"""
        try:
            events = list(self.event_history[user_id])
            if len(events) < 10:  # 需要足够的数据
                return

            # 分析不同类型的时间模式
            for pattern_type in TimePattern:
                analysis = self._analyze_specific_pattern(user_id, pattern_type, events)
                if analysis:
                    self.user_patterns[user_id][pattern_type] = analysis

        except Exception as e:
            logger.error(f"时间模式分析失败: {e!s}")

    def _analyze_specific_pattern(
        self, user_id: str, pattern_type: TimePattern, events: list[TimeEvent]
    ) -> TimePatternAnalysis | None:
        """分析特定类型的时间模式"""
        try:
            if pattern_type == TimePattern.DAILY_ROUTINE:
                return self._analyze_daily_routine(events)
            elif pattern_type == TimePattern.SLEEP_CYCLE:
                return self._analyze_sleep_cycle(events)
            elif pattern_type == TimePattern.WORK_SCHEDULE:
                return self._analyze_work_schedule(events)
            elif pattern_type == TimePattern.MEAL_TIMING:
                return self._analyze_meal_timing(events)
            else:
                return None

        except Exception as e:
            logger.error(f"分析模式 {pattern_type.value} 失败: {e!s}")
            return None

    def _analyze_daily_routine(
        self, events: list[TimeEvent]
    ) -> TimePatternAnalysis | None:
        """分析日常作息模式"""
        routine_events = [
            e for e in events if e.event_type in ["wake_up", "sleep", "meal", "work"]
        ]
        if len(routine_events) < 5:
            return None

        # 按事件类型分组
        event_groups = defaultdict(list)
        for event in routine_events:
            event_groups[event.event_type].append(event)

        # 计算典型时间
        typical_times = []
        for event_type, event_list in event_groups.items():
            times = [datetime.fromtimestamp(e.timestamp) for e in event_list]
            avg_hour = np.mean([t.hour for t in times])
            avg_minute = np.mean([t.minute for t in times])
            typical_times.append((int(avg_hour), int(avg_minute)))

        # 计算变异性
        variability = self._calculate_time_variability(routine_events)

        return TimePatternAnalysis(
            pattern_type=TimePattern.DAILY_ROUTINE,
            confidence=min(1.0, len(routine_events) / 50.0),
            frequency=len(routine_events) / 30.0,  # 假设30天的数据
            typical_times=typical_times,
            duration_stats={"mean": 24.0, "std": 2.0},
            variability=variability,
            trend="stable",
            last_updated=time.time(),
        )

    def _analyze_sleep_cycle(
        self, events: list[TimeEvent]
    ) -> TimePatternAnalysis | None:
        """分析睡眠周期模式"""
        sleep_events = [e for e in events if e.event_type in ["sleep", "wake_up"]]
        if len(sleep_events) < 10:
            return None

        # 分离睡眠和起床事件
        sleep_times = [e for e in sleep_events if e.event_type == "sleep"]
        wake_times = [e for e in sleep_events if e.event_type == "wake_up"]

        if not sleep_times or not wake_times:
            return None

        # 计算平均睡眠和起床时间
        sleep_hours = [datetime.fromtimestamp(e.timestamp).hour for e in sleep_times]
        wake_hours = [datetime.fromtimestamp(e.timestamp).hour for e in wake_times]

        avg_sleep_hour = np.mean(sleep_hours)
        avg_wake_hour = np.mean(wake_hours)

        # 计算睡眠时长
        sleep_durations = []
        for i in range(min(len(sleep_times), len(wake_times))):
            sleep_time = sleep_times[i].timestamp
            wake_time = wake_times[i].timestamp
            if wake_time > sleep_time:
                duration = (wake_time - sleep_time) / 3600  # 转换为小时
                sleep_durations.append(duration)

        duration_stats = {
            "mean": np.mean(sleep_durations) if sleep_durations else 8.0,
            "std": np.std(sleep_durations) if sleep_durations else 1.0,
        }

        return TimePatternAnalysis(
            pattern_type=TimePattern.SLEEP_CYCLE,
            confidence=min(1.0, len(sleep_events) / 20.0),
            frequency=len(sleep_events) / 30.0,
            typical_times=[(int(avg_sleep_hour), 0), (int(avg_wake_hour), 0)],
            duration_stats=duration_stats,
            variability=(
                np.std(sleep_hours + wake_hours) if sleep_hours and wake_hours else 1.0
            ),
            trend="stable",
            last_updated=time.time(),
        )

    def _analyze_work_schedule(
        self, events: list[TimeEvent]
    ) -> TimePatternAnalysis | None:
        """分析工作时间模式"""
        work_events = [
            e for e in events if e.event_type in ["work_start", "work_end", "work"]
        ]
        if len(work_events) < 5:
            return None

        # 按工作日分组
        work_days = defaultdict(list)
        for event in work_events:
            dt = datetime.fromtimestamp(event.timestamp)
            if dt.weekday() < 5:  # 工作日
                work_days[dt.date()].append(event)

        # 计算典型工作时间
        start_times = []
        end_times = []
        durations = []

        for day_events in work_days.values():
            if len(day_events) >= 2:
                start_time = min(day_events, key=lambda x: x.timestamp)
                end_time = max(day_events, key=lambda x: x.timestamp)

                start_dt = datetime.fromtimestamp(start_time.timestamp)
                end_dt = datetime.fromtimestamp(end_time.timestamp)

                start_times.append((start_dt.hour, start_dt.minute))
                end_times.append((end_dt.hour, end_dt.minute))

                duration = (end_time.timestamp - start_time.timestamp) / 3600
                durations.append(duration)

        if not start_times:
            return None

        avg_start = (
            int(np.mean([t[0] for t in start_times])),
            int(np.mean([t[1] for t in start_times])),
        )
        avg_end = (
            int(np.mean([t[0] for t in end_times])),
            int(np.mean([t[1] for t in end_times])),
        )

        return TimePatternAnalysis(
            pattern_type=TimePattern.WORK_SCHEDULE,
            confidence=min(1.0, len(work_days) / 20.0),
            frequency=len(work_days) / 30.0,
            typical_times=[avg_start, avg_end],
            duration_stats={
                "mean": np.mean(durations) if durations else 8.0,
                "std": np.std(durations) if durations else 1.0,
            },
            variability=self._calculate_time_variability(work_events),
            trend="stable",
            last_updated=time.time(),
        )

    def _analyze_meal_timing(
        self, events: list[TimeEvent]
    ) -> TimePatternAnalysis | None:
        """分析用餐时间模式"""
        meal_events = [
            e
            for e in events
            if e.event_type in ["breakfast", "lunch", "dinner", "meal"]
        ]
        if len(meal_events) < 5:
            return None

        # 按餐次分组
        meal_types = defaultdict(list)
        for event in meal_events:
            dt = datetime.fromtimestamp(event.timestamp)
            hour = dt.hour

            # 根据时间推断餐次
            if 5 <= hour <= 10:
                meal_type = "breakfast"
            elif 11 <= hour <= 14:
                meal_type = "lunch"
            elif 17 <= hour <= 21:
                meal_type = "dinner"
            else:
                meal_type = "snack"

            meal_types[meal_type].append(event)

        # 计算各餐次的典型时间
        typical_times = []
        for meal_type, events_list in meal_types.items():
            if events_list:
                times = [datetime.fromtimestamp(e.timestamp) for e in events_list]
                avg_hour = int(np.mean([t.hour for t in times]))
                avg_minute = int(np.mean([t.minute for t in times]))
                typical_times.append((avg_hour, avg_minute))

        return TimePatternAnalysis(
            pattern_type=TimePattern.MEAL_TIMING,
            confidence=min(1.0, len(meal_events) / 30.0),
            frequency=len(meal_events) / 30.0,
            typical_times=typical_times,
            duration_stats={"mean": 0.5, "std": 0.2},  # 假设用餐时长
            variability=self._calculate_time_variability(meal_events),
            trend="stable",
            last_updated=time.time(),
        )

    def _calculate_time_variability(self, events: list[TimeEvent]) -> float:
        """计算时间变异性"""
        if len(events) < 2:
            return 0.0

        times = [datetime.fromtimestamp(e.timestamp) for e in events]
        hours = [t.hour + t.minute / 60.0 for t in times]

        return float(np.std(hours))

    def get_user_patterns(self, user_id: str) -> dict[TimePattern, TimePatternAnalysis]:
        """获取用户的时间模式"""
        return self.user_patterns.get(user_id, {})

    def predict_next_event(
        self, user_id: str, current_time: datetime | None = None
    ) -> dict[str, Any] | None:
        """预测下一个可能的事件"""
        if current_time is None:
            current_time = datetime.now()

        patterns = self.user_patterns.get(user_id, {})
        if not patterns:
            return None

        # 基于当前时间和历史模式预测下一个事件
        current_hour = current_time.hour
        current_minute = current_time.minute

        best_prediction = None
        min_time_diff = float("inf")

        for pattern_type, analysis in patterns.items():
            for typical_hour, typical_minute in analysis.typical_times:
                # 计算到下一个典型时间的差值
                target_time = current_time.replace(
                    hour=typical_hour, minute=typical_minute, second=0, microsecond=0
                )

                # 如果目标时间已过，则考虑明天的时间
                if target_time <= current_time:
                    target_time += timedelta(days=1)

                time_diff = (
                    target_time - current_time
                ).total_seconds() / 3600  # 转换为小时

                if time_diff < min_time_diff:
                    min_time_diff = time_diff
                    best_prediction = {
                        "pattern_type": pattern_type.value,
                        "predicted_time": target_time,
                        "time_until": time_diff,
                        "confidence": analysis.confidence,
                    }

        return best_prediction


class CircadianAnalyzer:
    """生物钟分析器"""

    def __init__(self) -> None:
        self.user_profiles = {}  # user_id -> CircadianProfile
        self.chronotype_indicators = {
            "morning": {
                "sleep_onset": (21, 23),
                "wake_time": (5, 7),
                "energy_peak": (8, 12),
            },
            "evening": {
                "sleep_onset": (23, 2),
                "wake_time": (7, 10),
                "energy_peak": (18, 22),
            },
            "intermediate": {
                "sleep_onset": (22, 24),
                "wake_time": (6, 8),
                "energy_peak": (10, 16),
            },
        }

    def analyze_circadian_rhythm(
        self, user_id: str, events: list[TimeEvent]
    ) -> CircadianProfile | None:
        """分析用户的生物钟节律"""
        try:
            sleep_events = [e for e in events if e.event_type in ["sleep", "wake_up"]]
            energy_events = [
                e
                for e in events
                if e.event_type in ["energy_high", "energy_low", "fatigue"]
            ]

            if len(sleep_events) < 10:
                return None

            # 分析睡眠模式
            sleep_times = [e for e in sleep_events if e.event_type == "sleep"]
            wake_times = [e for e in sleep_events if e.event_type == "wake_up"]

            if not sleep_times or not wake_times:
                return None

            # 计算平均睡眠和起床时间
            avg_sleep_time = self._calculate_average_time(sleep_times)
            avg_wake_time = self._calculate_average_time(wake_times)

            # 计算睡眠时长
            sleep_duration = self._calculate_sleep_duration(sleep_times, wake_times)

            # 确定时型
            chronotype = self._determine_chronotype(avg_sleep_time, avg_wake_time)

            # 分析能量峰值和低谷
            energy_peaks, energy_dips = self._analyze_energy_patterns(energy_events)

            # 推荐最佳工作时间
            optimal_work_hours = self._calculate_optimal_work_hours(
                chronotype, energy_peaks
            )

            # 推荐用餐窗口
            meal_windows = self._calculate_meal_windows(avg_wake_time, avg_sleep_time)

            profile = CircadianProfile(
                user_id=user_id,
                chronotype=chronotype,
                sleep_onset=avg_sleep_time,
                wake_time=avg_wake_time,
                sleep_duration=sleep_duration,
                energy_peaks=energy_peaks,
                energy_dips=energy_dips,
                optimal_work_hours=optimal_work_hours,
                meal_windows=meal_windows,
                confidence=min(1.0, len(sleep_events) / 30.0),
                last_updated=time.time(),
            )

            self.user_profiles[user_id] = profile
            return profile

        except Exception as e:
            logger.error(f"生物钟分析失败: {e!s}")
            return None

    def _calculate_average_time(self, events: list[TimeEvent]) -> tuple[int, int]:
        """计算平均时间"""
        times = [datetime.fromtimestamp(e.timestamp) for e in events]

        # 处理跨午夜的时间
        hours = []
        minutes = []

        for t in times:
            hour = t.hour
            minute = t.minute

            # 如果是睡眠时间且在早晨，转换为24+小时格式
            if hour < 6:  # 假设6点前的时间是前一天的延续
                hour += 24

            hours.append(hour)
            minutes.append(minute)

        avg_hour = int(np.mean(hours)) % 24
        avg_minute = int(np.mean(minutes))

        return (avg_hour, avg_minute)

    def _calculate_sleep_duration(
        self, sleep_times: list[TimeEvent], wake_times: list[TimeEvent]
    ) -> float:
        """计算平均睡眠时长"""
        durations = []

        for i in range(min(len(sleep_times), len(wake_times))):
            sleep_time = sleep_times[i].timestamp
            wake_time = wake_times[i].timestamp

            # 处理跨日的情况
            if wake_time < sleep_time:
                wake_time += 24 * 3600  # 加一天

            duration = (wake_time - sleep_time) / 3600  # 转换为小时
            if 4 <= duration <= 12:  # 合理的睡眠时长范围
                durations.append(duration)

        return np.mean(durations) if durations else 8.0

    def _determine_chronotype(
        self, sleep_time: tuple[int, int], wake_time: tuple[int, int]
    ) -> str:
        """确定时型（晨型、夜型、中间型）"""
        sleep_hour = sleep_time[0]
        wake_hour = wake_time[0]

        # 晨型人：早睡早起
        if sleep_hour <= 22 and wake_hour <= 7:
            return "morning"
        # 夜型人：晚睡晚起
        elif sleep_hour >= 23 and wake_hour >= 8:
            return "evening"
        # 中间型
        else:
            return "intermediate"

    def _analyze_energy_patterns(
        self, energy_events: list[TimeEvent]
    ) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
        """分析能量模式"""
        energy_highs = [e for e in energy_events if e.event_type == "energy_high"]
        energy_lows = [
            e for e in energy_events if e.event_type in ["energy_low", "fatigue"]
        ]

        peaks = []
        if energy_highs:
            peak_times = [datetime.fromtimestamp(e.timestamp) for e in energy_highs]
            # 聚类分析找出主要的能量峰值时间
            peak_hours = [t.hour for t in peak_times]
            if peak_hours:
                avg_peak_hour = int(np.mean(peak_hours))
                peaks.append((avg_peak_hour, 0))

        dips = []
        if energy_lows:
            dip_times = [datetime.fromtimestamp(e.timestamp) for e in energy_lows]
            dip_hours = [t.hour for t in dip_times]
            if dip_hours:
                avg_dip_hour = int(np.mean(dip_hours))
                dips.append((avg_dip_hour, 0))

        return peaks, dips

    def _calculate_optimal_work_hours(
        self, chronotype: str, energy_peaks: list[tuple[int, int]]
    ) -> list[tuple[int, int]]:
        """计算最佳工作时间"""
        if chronotype == "morning":
            return [(8, 12), (14, 16)]
        elif chronotype == "evening":
            return [(10, 12), (16, 20)]
        else:  # intermediate
            return [(9, 12), (14, 17)]

    def _calculate_meal_windows(
        self, wake_time: tuple[int, int], sleep_time: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """计算用餐窗口"""
        wake_hour = wake_time[0]

        # 基于起床时间计算用餐时间
        breakfast_time = (wake_hour + 1, 0)
        lunch_time = (wake_hour + 5, 0)
        dinner_time = (wake_hour + 10, 0)

        return [breakfast_time, lunch_time, dinner_time]

    def get_user_profile(self, user_id: str) -> CircadianProfile | None:
        """获取用户生物钟档案"""
        return self.user_profiles.get(user_id)

    def get_current_energy_level(
        self, user_id: str, current_time: datetime | None = None
    ) -> dict[str, Any]:
        """获取当前预期能量水平"""
        if current_time is None:
            current_time = datetime.now()

        profile = self.user_profiles.get(user_id)
        if not profile:
            return {"energy_level": "unknown", "confidence": 0.0}

        current_hour = current_time.hour

        # 基于生物钟档案预测当前能量水平
        energy_level = "medium"
        confidence = 0.5

        # 检查是否在能量峰值时间
        for peak_hour, _ in profile.energy_peaks:
            if abs(current_hour - peak_hour) <= 1:
                energy_level = "high"
                confidence = 0.8
                break

        # 检查是否在能量低谷时间
        for dip_hour, _ in profile.energy_dips:
            if abs(current_hour - dip_hour) <= 1:
                energy_level = "low"
                confidence = 0.8
                break

        # 检查是否在睡眠时间
        sleep_hour = profile.sleep_onset[0]
        wake_hour = profile.wake_time[0]

        if sleep_hour <= current_hour <= 23 or 0 <= current_hour <= wake_hour:
            energy_level = "very_low"
            confidence = 0.9

        return {
            "energy_level": energy_level,
            "confidence": confidence,
            "chronotype": profile.chronotype,
            "recommendations": self._get_energy_recommendations(
                energy_level, current_hour
            ),
        }

    def _get_energy_recommendations(
        self, energy_level: str, current_hour: int
    ) -> list[str]:
        """基于能量水平获取建议"""
        recommendations = []

        if energy_level == "high":
            recommendations.extend(
                ["适合进行重要工作或学习", "可以安排需要专注的任务", "适合进行体力活动"]
            )
        elif energy_level == "low":
            recommendations.extend(
                ["建议进行轻松的活动", "可以考虑短暂休息", "避免重要决策"]
            )
        elif energy_level == "very_low":
            recommendations.extend(
                ["建议准备休息或睡眠", "避免使用电子设备", "可以进行放松活动"]
            )
        else:  # medium
            recommendations.extend(["适合进行日常工作", "可以安排一般性任务"])

        return recommendations


class TemporalAwarenessEngine:
    """时间感知引擎核心类"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化时间感知引擎

        Args:
            config: 服务配置
        """
        self.config = config
        self.enabled = config.get("temporal_awareness", {}).get("enabled", True)

        # 子模块
        self.pattern_recognizer = TimePatternRecognizer()
        self.circadian_analyzer = CircadianAnalyzer()

        # 时间事件队列
        self.event_queue = asyncio.Queue()
        self.processing_task = None

        # 统计信息
        self.stats = {
            "total_events": 0,
            "patterns_detected": 0,
            "predictions_made": 0,
            "accuracy_score": 0.0,
        }

        if self.enabled:
            self._start_processing()

        logger.info(f"时间感知引擎初始化完成 - 启用: {self.enabled}")

    def _start_processing(self) -> None:
        """启动事件处理任务"""
        if self.processing_task is None:
            self.processing_task = asyncio.create_task(self._process_events())

    async def _process_events(self) -> None:
        """处理时间事件队列"""
        while True:
            try:
                event = await self.event_queue.get()

                # 添加到模式识别器
                self.pattern_recognizer.add_time_event(event)

                # 更新统计信息
                self.stats["total_events"] += 1

                # 检查是否需要更新生物钟分析
                if self.stats["total_events"] % 50 == 0:  # 每50个事件更新一次
                    await self._update_circadian_analysis(event.user_id)

                self.event_queue.task_done()

            except Exception as e:
                logger.error(f"处理时间事件失败: {e!s}")

    async def _update_circadian_analysis(self, user_id: str):
        """更新生物钟分析"""
        try:
            events = list(self.pattern_recognizer.event_history[user_id])
            profile = self.circadian_analyzer.analyze_circadian_rhythm(user_id, events)

            if profile:
                logger.info(f"用户 {user_id} 的生物钟档案已更新")

        except Exception as e:
            logger.error(f"更新生物钟分析失败: {e!s}")

    async def add_time_event(self, event: TimeEvent):
        """添加时间事件"""
        if self.enabled:
            await self.event_queue.put(event)

    def get_time_context(self, current_time: datetime | None = None) -> dict[str, Any]:
        """获取当前时间上下文"""
        if current_time is None:
            current_time = datetime.now()

        hour = current_time.hour
        weekday = current_time.weekday()

        # 确定时间段
        if 5 <= hour < 12:
            time_period = TimeContext.MORNING
        elif 12 <= hour < 17:
            time_period = TimeContext.AFTERNOON
        elif 17 <= hour < 21:
            time_period = TimeContext.EVENING
        else:
            time_period = TimeContext.NIGHT

        # 确定日期类型
        if weekday < 5:
            day_type = TimeContext.WORKDAY
        else:
            day_type = TimeContext.WEEKEND

        return {
            "current_time": current_time,
            "time_period": time_period.value,
            "day_type": day_type.value,
            "hour": hour,
            "weekday": weekday,
            "is_weekend": weekday >= 5,
        }

    def predict_user_activity(
        self, user_id: str, target_time: datetime | None = None
    ) -> dict[str, Any] | None:
        """预测用户在指定时间的活动"""
        if target_time is None:
            target_time = datetime.now()

        # 获取用户的时间模式
        patterns = self.pattern_recognizer.get_user_patterns(user_id)
        if not patterns:
            return None

        # 基于时间模式预测活动
        prediction = self.pattern_recognizer.predict_next_event(user_id, target_time)

        if prediction:
            self.stats["predictions_made"] += 1

        return prediction

    def get_health_recommendations(
        self, user_id: str, current_time: datetime | None = None
    ) -> list[dict[str, Any]]:
        """获取基于时间的健康建议"""
        if current_time is None:
            current_time = datetime.now()

        recommendations = []

        # 获取生物钟档案
        profile = self.circadian_analyzer.get_user_profile(user_id)
        if profile:
            # 获取当前能量水平
            energy_info = self.circadian_analyzer.get_current_energy_level(
                user_id, current_time
            )

            recommendations.append(
                {
                    "type": "energy_management",
                    "title": f"当前能量水平: {energy_info['energy_level']}",
                    "recommendations": energy_info["recommendations"],
                    "confidence": energy_info["confidence"],
                }
            )

            # 睡眠建议
            sleep_hour, sleep_minute = profile.sleep_onset
            current_hour = current_time.hour

            if abs(current_hour - sleep_hour) <= 1:
                recommendations.append(
                    {
                        "type": "sleep_preparation",
                        "title": "睡眠准备时间",
                        "recommendations": [
                            "建议开始准备睡眠",
                            "减少屏幕使用",
                            "进行放松活动",
                        ],
                        "confidence": 0.8,
                    }
                )

            # 用餐建议
            for i, (meal_hour, meal_minute) in enumerate(profile.meal_windows):
                if abs(current_hour - meal_hour) <= 1:
                    meal_names = ["早餐", "午餐", "晚餐"]
                    meal_name = meal_names[i] if i < len(meal_names) else "用餐"

                    recommendations.append(
                        {
                            "type": "meal_timing",
                            "title": f"{meal_name}时间",
                            "recommendations": [
                                f"建议在此时间进行{meal_name}",
                                "注意营养均衡",
                                "避免过量进食",
                            ],
                            "confidence": 0.7,
                        }
                    )

        return recommendations

    def get_optimal_schedule(
        self, user_id: str, date: datetime | None = None
    ) -> dict[str, Any]:
        """获取最优时间安排建议"""
        if date is None:
            date = datetime.now()

        profile = self.circadian_analyzer.get_user_profile(user_id)
        patterns = self.pattern_recognizer.get_user_patterns(user_id)

        schedule = {
            "date": date.strftime("%Y-%m-%d"),
            "chronotype": profile.chronotype if profile else "unknown",
            "recommendations": [],
        }

        if profile:
            # 最佳工作时间
            for start_hour, end_hour in profile.optimal_work_hours:
                schedule["recommendations"].append(
                    {
                        "time_range": f"{start_hour:02d}:00-{end_hour:02d}:00",
                        "activity": "重要工作/学习",
                        "priority": "high",
                        "reason": "能量峰值时间",
                    }
                )

            # 用餐时间
            meal_names = ["早餐", "午餐", "晚餐"]
            for i, (meal_hour, meal_minute) in enumerate(profile.meal_windows):
                if i < len(meal_names):
                    schedule["recommendations"].append(
                        {
                            "time_range": f"{meal_hour:02d}:{meal_minute:02d}",
                            "activity": meal_names[i],
                            "priority": "medium",
                            "reason": "最佳用餐时间",
                        }
                    )

            # 睡眠时间
            sleep_hour, sleep_minute = profile.sleep_onset
            schedule["recommendations"].append(
                {
                    "time_range": f"{sleep_hour:02d}:{sleep_minute:02d}",
                    "activity": "睡眠准备",
                    "priority": "high",
                    "reason": "最佳睡眠时间",
                }
            )

        return schedule

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        return {
            "enabled": self.enabled,
            "total_users": len(self.pattern_recognizer.user_patterns),
            "circadian_profiles": len(self.circadian_analyzer.user_profiles),
            **self.stats,
        }

    async def shutdown(self) -> None:
        """关闭时间感知引擎"""
        logger.info("正在关闭时间感知引擎...")

        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass

        logger.info("时间感知引擎已关闭")
