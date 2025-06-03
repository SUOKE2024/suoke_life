#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能运动训练引擎 - 提供个性化运动训练方案和训练管理
结合中医运动养生理念和现代运动科学，为用户制定科学的运动训练计划
"""

from typing import Dict, List, Any, Optional, Tuple, Union, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from loguru import logger
import warnings
warnings.filterwarnings('ignore')

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind

class ExerciseType(str, Enum):
    """运动类型"""
    CARDIO = "cardio"                       # 有氧运动
    STRENGTH = "strength"                   # 力量训练
    FLEXIBILITY = "flexibility"             # 柔韧性训练
    BALANCE = "balance"                     # 平衡训练
    COORDINATION = "coordination"           # 协调性训练
    ENDURANCE = "endurance"                 # 耐力训练
    HIIT = "hiit"                          # 高强度间歇训练
    YOGA = "yoga"                          # 瑜伽
    PILATES = "pilates"                    # 普拉提
    FUNCTIONAL = "functional"               # 功能性训练
    SPORTS_SPECIFIC = "sports_specific"     # 专项运动
    TCM_QIGONG = "tcm_qigong"              # 中医气功
    TCM_TAICHI = "tcm_taichi"              # 中医太极
    TCM_WUQINXI = "tcm_wuqinxi"            # 中医五禽戏
    TCM_BADUANJIN = "tcm_baduanjin"        # 中医八段锦

class IntensityLevel(str, Enum):
    """强度级别"""
    VERY_LOW = "very_low"       # 极低强度 (40-50% HRmax)
    LOW = "low"                 # 低强度 (50-60% HRmax)
    MODERATE = "moderate"       # 中等强度 (60-70% HRmax)
    HIGH = "high"               # 高强度 (70-85% HRmax)
    VERY_HIGH = "very_high"     # 极高强度 (85-95% HRmax)
    MAXIMUM = "maximum"         # 最大强度 (95-100% HRmax)

class FitnessLevel(str, Enum):
    """健身水平"""
    BEGINNER = "beginner"           # 初学者
    NOVICE = "novice"               # 新手
    INTERMEDIATE = "intermediate"   # 中级
    ADVANCED = "advanced"           # 高级
    EXPERT = "expert"               # 专家级
    ELITE = "elite"                 # 精英级

class TrainingGoal(str, Enum):
    """训练目标"""
    WEIGHT_LOSS = "weight_loss"             # 减重
    MUSCLE_BUILDING = "muscle_building"     # 增肌
    STRENGTH_GAIN = "strength_gain"         # 增力
    ENDURANCE_IMPROVEMENT = "endurance_improvement" # 提升耐力
    FLEXIBILITY_IMPROVEMENT = "flexibility_improvement" # 提升柔韧性
    BALANCE_IMPROVEMENT = "balance_improvement" # 提升平衡
    GENERAL_FITNESS = "general_fitness"     # 综合健身
    SPORTS_PERFORMANCE = "sports_performance" # 运动表现
    REHABILITATION = "rehabilitation"       # 康复训练
    STRESS_RELIEF = "stress_relief"         # 压力缓解
    HEALTH_MAINTENANCE = "health_maintenance" # 健康维持
    TCM_WELLNESS = "tcm_wellness"           # 中医养生

class EquipmentType(str, Enum):
    """器械类型"""
    BODYWEIGHT = "bodyweight"               # 自重
    DUMBBELLS = "dumbbells"                 # 哑铃
    BARBELLS = "barbells"                   # 杠铃
    RESISTANCE_BANDS = "resistance_bands"   # 阻力带
    KETTLEBELLS = "kettlebells"             # 壶铃
    MACHINES = "machines"                   # 器械
    CARDIO_EQUIPMENT = "cardio_equipment"   # 有氧器械
    YOGA_PROPS = "yoga_props"               # 瑜伽用具
    BALANCE_TOOLS = "balance_tools"         # 平衡工具
    FUNCTIONAL_TOOLS = "functional_tools"   # 功能性工具
    NONE = "none"                           # 无器械

class WorkoutStatus(str, Enum):
    """训练状态"""
    PLANNED = "planned"             # 已计划
    IN_PROGRESS = "in_progress"     # 进行中
    COMPLETED = "completed"         # 已完成
    SKIPPED = "skipped"             # 已跳过
    PAUSED = "paused"               # 已暂停
    CANCELLED = "cancelled"         # 已取消
    MODIFIED = "modified"           # 已修改

class TCMConstitution(str, Enum):
    """中医体质类型"""
    BALANCED = "balanced"                   # 平和质
    QI_DEFICIENCY = "qi_deficiency"         # 气虚质
    YANG_DEFICIENCY = "yang_deficiency"     # 阳虚质
    YIN_DEFICIENCY = "yin_deficiency"       # 阴虚质
    PHLEGM_DAMPNESS = "phlegm_dampness"     # 痰湿质
    DAMP_HEAT = "damp_heat"                 # 湿热质
    BLOOD_STASIS = "blood_stasis"           # 血瘀质
    QI_STAGNATION = "qi_stagnation"         # 气郁质
    SPECIAL_CONSTITUTION = "special_constitution" # 特禀质

@dataclass
class UserFitnessProfile:
    """用户健身档案"""
    user_id: str
    age: int
    gender: str
    height: float                           # 身高(cm)
    weight: float                           # 体重(kg)
    bmi: float = field(init=False)
    body_fat_percentage: Optional[float] = None
    resting_heart_rate: Optional[int] = None
    max_heart_rate: Optional[int] = None
    fitness_level: FitnessLevel = FitnessLevel.BEGINNER
    training_goals: List[TrainingGoal] = field(default_factory=list)
    available_equipment: List[EquipmentType] = field(default_factory=list)
    workout_frequency: int = 3              # 每周训练次数
    session_duration: int = 60              # 每次训练时长(分钟)
    preferred_workout_times: List[str] = field(default_factory=list)
    medical_conditions: List[str] = field(default_factory=list)
    injuries: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    tcm_constitution: Optional[TCMConstitution] = None
    stress_level: Optional[int] = None      # 压力水平 (1-10)
    sleep_quality: Optional[int] = None     # 睡眠质量 (1-10)
    energy_level: Optional[int] = None      # 精力水平 (1-10)
    motivation_level: Optional[int] = None  # 动机水平 (1-10)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        self.bmi = self.weight / ((self.height / 100) ** 2)
        if self.max_heart_rate is None:
            self.max_heart_rate = 220 - self.age

@dataclass
class Exercise:
    """运动项目"""
    id: str
    name: str
    description: str
    exercise_type: ExerciseType
    intensity_level: IntensityLevel
    target_muscles: List[str] = field(default_factory=list)
    equipment_needed: List[EquipmentType] = field(default_factory=list)
    duration_minutes: Optional[int] = None
    repetitions: Optional[int] = None
    sets: Optional[int] = None
    rest_seconds: Optional[int] = None
    calories_per_minute: Optional[float] = None
    difficulty_level: int = 1               # 难度级别 (1-10)
    instructions: List[str] = field(default_factory=list)
    form_cues: List[str] = field(default_factory=list)
    safety_tips: List[str] = field(default_factory=list)
    modifications: List[str] = field(default_factory=list)
    progressions: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    video_url: Optional[str] = None
    image_urls: List[str] = field(default_factory=list)
    # 中医属性
    tcm_meridians: List[str] = field(default_factory=list)
    tcm_effects: List[str] = field(default_factory=list)
    tcm_constitution_suitability: List[TCMConstitution] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkoutSession:
    """训练课程"""
    id: str
    name: str
    description: str
    workout_type: ExerciseType
    target_duration: int                    # 目标时长(分钟)
    target_intensity: IntensityLevel
    exercises: List[Exercise]
    warm_up_exercises: List[Exercise] = field(default_factory=list)
    cool_down_exercises: List[Exercise] = field(default_factory=list)
    estimated_calories: Optional[float] = None
    difficulty_rating: int = 1              # 难度评级 (1-10)
    equipment_required: List[EquipmentType] = field(default_factory=list)
    space_requirements: Optional[str] = None
    target_goals: List[TrainingGoal] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    session_notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class TrainingPlan:
    """训练计划"""
    id: str
    user_id: str
    name: str
    description: str
    plan_type: str                          # weekly, monthly, custom
    duration_weeks: int
    sessions_per_week: int
    primary_goals: List[TrainingGoal]
    workout_sessions: List[WorkoutSession]
    weekly_schedule: Dict[str, List[str]] = field(default_factory=dict)  # {day: [session_ids]}
    progression_strategy: str = "linear"    # linear, undulating, block
    deload_weeks: List[int] = field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: WorkoutStatus = WorkoutStatus.PLANNED
    progress_percentage: float = 0.0
    created_by: str = "system"
    notes: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkoutLog:
    """训练日志"""
    id: str
    user_id: str
    session_id: str
    plan_id: Optional[str] = None
    workout_date: datetime
    actual_duration: int                    # 实际时长(分钟)
    exercises_completed: List[Dict[str, Any]] = field(default_factory=list)  # {exercise_id, sets, reps, weight, etc.}
    exercises_skipped: List[str] = field(default_factory=list)
    perceived_exertion: Optional[int] = None # 主观疲劳度 (1-10)
    mood_before: Optional[int] = None       # 训练前情绪 (1-10)
    mood_after: Optional[int] = None        # 训练后情绪 (1-10)
    energy_before: Optional[int] = None     # 训练前精力 (1-10)
    energy_after: Optional[int] = None      # 训练后精力 (1-10)
    pain_level: Optional[int] = None        # 疼痛程度 (0-10)
    satisfaction_rating: Optional[int] = None # 满意度 (1-10)
    calories_burned: Optional[float] = None
    heart_rate_data: Dict[str, Any] = field(default_factory=dict)
    notes: Optional[str] = None
    achievements: List[str] = field(default_factory=list)
    challenges: List[str] = field(default_factory=list)
    status: WorkoutStatus = WorkoutStatus.COMPLETED
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class FitnessAssessment:
    """健身评估"""
    id: str
    user_id: str
    assessment_date: datetime
    assessment_type: str                    # initial, progress, final
    # 体能测试结果
    cardiovascular_fitness: Optional[float] = None  # VO2 max或类似指标
    muscular_strength: Dict[str, float] = field(default_factory=dict)
    muscular_endurance: Dict[str, float] = field(default_factory=dict)
    flexibility_scores: Dict[str, float] = field(default_factory=dict)
    balance_scores: Dict[str, float] = field(default_factory=dict)
    body_composition: Dict[str, float] = field(default_factory=dict)
    # 功能性评估
    movement_quality: Dict[str, int] = field(default_factory=dict)  # 动作质量评分
    injury_risk_factors: List[str] = field(default_factory=list)
    # 主观评估
    fitness_confidence: Optional[int] = None # 健身信心 (1-10)
    exercise_enjoyment: Optional[int] = None # 运动享受度 (1-10)
    # 目标进展
    goal_progress: Dict[str, float] = field(default_factory=dict)
    # 建议
    recommendations: List[str] = field(default_factory=list)
    next_assessment_date: Optional[datetime] = None
    assessor: Optional[str] = None
    notes: Optional[str] = None

@dataclass
class ProgressMetrics:
    """进度指标"""
    user_id: str
    calculation_date: datetime
    period_start: datetime
    period_end: datetime
    # 训练统计
    total_workouts: int = 0
    planned_workouts: int = 0
    completion_rate: float = 0.0
    average_workout_duration: float = 0.0
    total_training_time: float = 0.0
    # 强度分析
    intensity_distribution: Dict[IntensityLevel, int] = field(default_factory=dict)
    average_perceived_exertion: Optional[float] = None
    # 体能改善
    strength_improvements: Dict[str, float] = field(default_factory=dict)
    endurance_improvements: Dict[str, float] = field(default_factory=dict)
    flexibility_improvements: Dict[str, float] = field(default_factory=dict)
    # 身体变化
    weight_change: Optional[float] = None
    body_fat_change: Optional[float] = None
    muscle_mass_change: Optional[float] = None
    # 主观指标
    average_satisfaction: Optional[float] = None
    average_energy_improvement: Optional[float] = None
    average_mood_improvement: Optional[float] = None
    # 目标达成
    goals_achieved: List[str] = field(default_factory=list)
    goals_in_progress: List[str] = field(default_factory=list)
    # 预测指标
    predicted_goal_achievement: Dict[str, datetime] = field(default_factory=dict)
    injury_risk_score: Optional[float] = None
    burnout_risk_score: Optional[float] = None

class ExerciseLibrary:
    """运动库"""
    
    def __init__(self):
        self.exercises: Dict[str, Exercise] = {}
        self.exercise_categories: Dict[ExerciseType, List[str]] = {}
        self._load_exercise_database()
    
    def _load_exercise_database(self):
        """加载运动数据库"""
        # 有氧运动
        cardio_exercises = [
            Exercise(
                id="running",
                name="跑步",
                description="基础有氧运动，提升心肺功能",
                exercise_type=ExerciseType.CARDIO,
                intensity_level=IntensityLevel.MODERATE,
                target_muscles=["腿部", "核心"],
                equipment_needed=[EquipmentType.NONE],
                duration_minutes=30,
                calories_per_minute=10.0,
                difficulty_level=3,
                instructions=[
                    "保持直立姿势，目视前方",
                    "脚掌中部着地，避免脚跟重击",
                    "保持自然呼吸节奏",
                    "手臂自然摆动"
                ],
                benefits=["提升心肺功能", "燃烧脂肪", "增强腿部力量", "改善情绪"],
                tcm_effects=["疏通经络", "调和气血", "强健脾胃"]
            ),
            Exercise(
                id="cycling",
                name="骑行",
                description="低冲击有氧运动，适合关节保护",
                exercise_type=ExerciseType.CARDIO,
                intensity_level=IntensityLevel.MODERATE,
                target_muscles=["腿部", "臀部"],
                equipment_needed=[EquipmentType.CARDIO_EQUIPMENT],
                duration_minutes=45,
                calories_per_minute=8.0,
                difficulty_level=2,
                benefits=["保护关节", "提升耐力", "强化下肢", "环保出行"]
            ),
            Exercise(
                id="swimming",
                name="游泳",
                description="全身有氧运动，低冲击高效果",
                exercise_type=ExerciseType.CARDIO,
                intensity_level=IntensityLevel.MODERATE,
                target_muscles=["全身"],
                equipment_needed=[EquipmentType.NONE],
                duration_minutes=30,
                calories_per_minute=12.0,
                difficulty_level=4,
                benefits=["全身锻炼", "关节友好", "提升肺活量", "塑形效果好"]
            )
        ]
        
        # 力量训练
        strength_exercises = [
            Exercise(
                id="push_ups",
                name="俯卧撑",
                description="经典上肢力量训练动作",
                exercise_type=ExerciseType.STRENGTH,
                intensity_level=IntensityLevel.MODERATE,
                target_muscles=["胸肌", "三头肌", "肩部", "核心"],
                equipment_needed=[EquipmentType.BODYWEIGHT],
                repetitions=15,
                sets=3,
                rest_seconds=60,
                difficulty_level=3,
                instructions=[
                    "双手撑地，与肩同宽",
                    "身体保持一条直线",
                    "下降至胸部接近地面",
                    "推起至手臂伸直"
                ],
                modifications=["膝盖着地", "墙面俯卧撑", "斜坡俯卧撑"],
                progressions=["钻石俯卧撑", "单手俯卧撑", "击掌俯卧撑"]
            ),
            Exercise(
                id="squats",
                name="深蹲",
                description="下肢力量训练之王",
                exercise_type=ExerciseType.STRENGTH,
                intensity_level=IntensityLevel.MODERATE,
                target_muscles=["股四头肌", "臀大肌", "腘绳肌", "核心"],
                equipment_needed=[EquipmentType.BODYWEIGHT],
                repetitions=20,
                sets=3,
                rest_seconds=60,
                difficulty_level=2,
                instructions=[
                    "双脚与肩同宽站立",
                    "脚尖略向外",
                    "下蹲至大腿平行地面",
                    "保持膝盖与脚尖方向一致"
                ],
                benefits=["增强下肢力量", "提升功能性", "燃烧卡路里", "改善姿态"]
            ),
            Exercise(
                id="deadlifts",
                name="硬拉",
                description="全身力量训练复合动作",
                exercise_type=ExerciseType.STRENGTH,
                intensity_level=IntensityLevel.HIGH,
                target_muscles=["腘绳肌", "臀大肌", "背部", "核心"],
                equipment_needed=[EquipmentType.BARBELLS],
                repetitions=8,
                sets=3,
                rest_seconds=120,
                difficulty_level=6,
                safety_tips=["保持背部挺直", "重量从地面拉起", "避免圆背"]
            )
        ]
        
        # 柔韧性训练
        flexibility_exercises = [
            Exercise(
                id="forward_fold",
                name="前屈伸展",
                description="拉伸腘绳肌和下背部",
                exercise_type=ExerciseType.FLEXIBILITY,
                intensity_level=IntensityLevel.LOW,
                target_muscles=["腘绳肌", "小腿", "下背部"],
                equipment_needed=[EquipmentType.NONE],
                duration_minutes=2,
                difficulty_level=1,
                instructions=[
                    "站立，双脚并拢",
                    "慢慢向前弯腰",
                    "尽量触碰脚趾",
                    "保持膝盖微弯"
                ]
            ),
            Exercise(
                id="cat_cow_stretch",
                name="猫牛式伸展",
                description="脊柱灵活性训练",
                exercise_type=ExerciseType.FLEXIBILITY,
                intensity_level=IntensityLevel.LOW,
                target_muscles=["脊柱", "核心"],
                equipment_needed=[EquipmentType.NONE],
                repetitions=10,
                difficulty_level=1,
                benefits=["改善脊柱灵活性", "缓解背部紧张", "增强核心稳定性"]
            )
        ]
        
        # 中医传统运动
        tcm_exercises = [
            Exercise(
                id="taichi_24_form",
                name="太极拳24式",
                description="传统中医养生运动，调和阴阳",
                exercise_type=ExerciseType.TCM_TAICHI,
                intensity_level=IntensityLevel.LOW,
                target_muscles=["全身"],
                equipment_needed=[EquipmentType.NONE],
                duration_minutes=20,
                difficulty_level=3,
                instructions=[
                    "动作缓慢连贯",
                    "呼吸自然深长",
                    "意念集中",
                    "虚实分明"
                ],
                tcm_effects=["调和阴阳", "疏通经络", "宁心安神", "强身健体"],
                tcm_constitution_suitability=[
                    TCMConstitution.QI_DEFICIENCY,
                    TCMConstitution.YANG_DEFICIENCY,
                    TCMConstitution.QI_STAGNATION
                ]
            ),
            Exercise(
                id="baduanjin",
                name="八段锦",
                description="传统健身气功，八个动作段落",
                exercise_type=ExerciseType.TCM_BADUANJIN,
                intensity_level=IntensityLevel.LOW,
                target_muscles=["全身"],
                equipment_needed=[EquipmentType.NONE],
                duration_minutes=15,
                difficulty_level=2,
                tcm_effects=["调理脏腑", "疏通经络", "强筋健骨", "延年益寿"],
                tcm_meridians=["任脉", "督脉", "十二经脉"]
            ),
            Exercise(
                id="wuqinxi",
                name="五禽戏",
                description="模仿五种动物的传统养生功法",
                exercise_type=ExerciseType.TCM_WUQINXI,
                intensity_level=IntensityLevel.LOW,
                target_muscles=["全身"],
                equipment_needed=[EquipmentType.NONE],
                duration_minutes=25,
                difficulty_level=3,
                instructions=[
                    "虎戏：强筋骨，壮腰肾",
                    "鹿戏：舒筋活络，益肾强腰",
                    "熊戏：健脾胃，助消化",
                    "猿戏：灵活关节，宁心安神",
                    "鸟戏：疏理三焦，调和气血"
                ],
                tcm_effects=["强身健体", "延年益寿", "调和脏腑", "疏通经络"]
            )
        ]
        
        # 瑜伽
        yoga_exercises = [
            Exercise(
                id="sun_salutation",
                name="拜日式",
                description="经典瑜伽序列，唤醒身体",
                exercise_type=ExerciseType.YOGA,
                intensity_level=IntensityLevel.MODERATE,
                target_muscles=["全身"],
                equipment_needed=[EquipmentType.YOGA_PROPS],
                duration_minutes=10,
                repetitions=5,
                difficulty_level=3,
                benefits=["增强柔韧性", "提升力量", "改善平衡", "减压放松"]
            ),
            Exercise(
                id="warrior_pose",
                name="战士式",
                description="增强腿部力量和平衡的瑜伽体式",
                exercise_type=ExerciseType.YOGA,
                intensity_level=IntensityLevel.MODERATE,
                target_muscles=["腿部", "核心", "肩部"],
                equipment_needed=[EquipmentType.YOGA_PROPS],
                duration_minutes=3,
                difficulty_level=2
            )
        ]
        
        # 高强度间歇训练
        hiit_exercises = [
            Exercise(
                id="burpees",
                name="波比跳",
                description="全身高强度复合动作",
                exercise_type=ExerciseType.HIIT,
                intensity_level=IntensityLevel.VERY_HIGH,
                target_muscles=["全身"],
                equipment_needed=[EquipmentType.BODYWEIGHT],
                repetitions=10,
                sets=4,
                rest_seconds=30,
                calories_per_minute=15.0,
                difficulty_level=7,
                instructions=[
                    "站立开始",
                    "下蹲双手撑地",
                    "跳跃成俯卧撑姿势",
                    "做一个俯卧撑",
                    "跳回下蹲姿势",
                    "向上跳跃"
                ],
                benefits=["全身燃脂", "提升爆发力", "增强心肺", "时间高效"]
            ),
            Exercise(
                id="mountain_climbers",
                name="登山者",
                description="核心和心肺训练动作",
                exercise_type=ExerciseType.HIIT,
                intensity_level=IntensityLevel.HIGH,
                target_muscles=["核心", "肩部", "腿部"],
                equipment_needed=[EquipmentType.BODYWEIGHT],
                duration_minutes=1,
                sets=3,
                rest_seconds=30,
                difficulty_level=5
            )
        ]
        
        # 整合所有运动
        all_exercises = (cardio_exercises + strength_exercises + 
                        flexibility_exercises + tcm_exercises + 
                        yoga_exercises + hiit_exercises)
        
        for exercise in all_exercises:
            self.exercises[exercise.id] = exercise
            
            if exercise.exercise_type not in self.exercise_categories:
                self.exercise_categories[exercise.exercise_type] = []
            self.exercise_categories[exercise.exercise_type].append(exercise.id)
        
        logger.info(f"加载了 {len(self.exercises)} 个运动项目")
    
    def get_exercise_by_id(self, exercise_id: str) -> Optional[Exercise]:
        """根据ID获取运动"""
        return self.exercises.get(exercise_id)
    
    def get_exercises_by_type(self, exercise_type: ExerciseType) -> List[Exercise]:
        """根据类型获取运动"""
        exercise_ids = self.exercise_categories.get(exercise_type, [])
        return [self.exercises[eid] for eid in exercise_ids]
    
    def search_exercises(
        self,
        exercise_type: Optional[ExerciseType] = None,
        intensity_level: Optional[IntensityLevel] = None,
        equipment_available: Optional[List[EquipmentType]] = None,
        target_muscles: Optional[List[str]] = None,
        max_difficulty: Optional[int] = None,
        tcm_constitution: Optional[TCMConstitution] = None
    ) -> List[Exercise]:
        """搜索符合条件的运动"""
        filtered_exercises = []
        
        for exercise in self.exercises.values():
            # 类型过滤
            if exercise_type and exercise.exercise_type != exercise_type:
                continue
            
            # 强度过滤
            if intensity_level and exercise.intensity_level != intensity_level:
                continue
            
            # 器械过滤
            if equipment_available is not None:
                if not all(eq in equipment_available for eq in exercise.equipment_needed):
                    continue
            
            # 目标肌群过滤
            if target_muscles:
                if not any(muscle in exercise.target_muscles for muscle in target_muscles):
                    continue
            
            # 难度过滤
            if max_difficulty and exercise.difficulty_level > max_difficulty:
                continue
            
            # 中医体质过滤
            if tcm_constitution:
                if (exercise.tcm_constitution_suitability and 
                    tcm_constitution not in exercise.tcm_constitution_suitability):
                    continue
            
            filtered_exercises.append(exercise)
        
        return filtered_exercises
    
    def get_progression_exercise(self, current_exercise_id: str) -> Optional[Exercise]:
        """获取进阶运动"""
        current = self.exercises.get(current_exercise_id)
        if not current:
            return None
        
        # 寻找同类型但难度更高的运动
        candidates = [
            ex for ex in self.exercises.values()
            if (ex.exercise_type == current.exercise_type and
                ex.difficulty_level > current.difficulty_level)
        ]
        
        if candidates:
            # 返回难度最接近的进阶运动
            return min(candidates, key=lambda x: x.difficulty_level)
        
        return None

class WorkoutPlanGenerator:
    """训练计划生成器"""
    
    def __init__(self, exercise_library: ExerciseLibrary):
        self.exercise_library = exercise_library
        self.plan_templates = self._load_plan_templates()
    
    def _load_plan_templates(self) -> Dict[str, Any]:
        """加载计划模板"""
        return {
            "beginner_general": {
                "name": "初学者综合健身",
                "duration_weeks": 8,
                "sessions_per_week": 3,
                "session_duration": 45,
                "goals": [TrainingGoal.GENERAL_FITNESS],
                "phases": [
                    {
                        "name": "适应期",
                        "weeks": [1, 2],
                        "intensity": IntensityLevel.LOW,
                        "focus": ["基础动作学习", "建立运动习惯"]
                    },
                    {
                        "name": "发展期",
                        "weeks": [3, 4, 5, 6],
                        "intensity": IntensityLevel.MODERATE,
                        "focus": ["力量提升", "耐力改善"]
                    },
                    {
                        "name": "巩固期",
                        "weeks": [7, 8],
                        "intensity": IntensityLevel.MODERATE,
                        "focus": ["技能巩固", "习惯养成"]
                    }
                ]
            },
            "weight_loss": {
                "name": "减重训练计划",
                "duration_weeks": 12,
                "sessions_per_week": 4,
                "session_duration": 60,
                "goals": [TrainingGoal.WEIGHT_LOSS],
                "phases": [
                    {
                        "name": "基础期",
                        "weeks": [1, 2, 3],
                        "intensity": IntensityLevel.MODERATE,
                        "focus": ["有氧基础", "代谢激活"]
                    },
                    {
                        "name": "强化期",
                        "weeks": [4, 5, 6, 7, 8, 9],
                        "intensity": IntensityLevel.HIGH,
                        "focus": ["HIIT训练", "力量保持"]
                    },
                    {
                        "name": "维持期",
                        "weeks": [10, 11, 12],
                        "intensity": IntensityLevel.MODERATE,
                        "focus": ["习惯维持", "效果巩固"]
                    }
                ]
            },
            "muscle_building": {
                "name": "增肌训练计划",
                "duration_weeks": 16,
                "sessions_per_week": 4,
                "session_duration": 75,
                "goals": [TrainingGoal.MUSCLE_BUILDING],
                "phases": [
                    {
                        "name": "适应期",
                        "weeks": [1, 2, 3, 4],
                        "intensity": IntensityLevel.MODERATE,
                        "focus": ["动作学习", "神经适应"]
                    },
                    {
                        "name": "增长期",
                        "weeks": [5, 6, 7, 8, 9, 10, 11, 12],
                        "intensity": IntensityLevel.HIGH,
                        "focus": ["肌肉增长", "力量提升"]
                    },
                    {
                        "name": "强化期",
                        "weeks": [13, 14, 15, 16],
                        "intensity": IntensityLevel.VERY_HIGH,
                        "focus": ["力量峰值", "肌肉质量"]
                    }
                ]
            },
            "tcm_wellness": {
                "name": "中医养生计划",
                "duration_weeks": 12,
                "sessions_per_week": 5,
                "session_duration": 30,
                "goals": [TrainingGoal.TCM_WELLNESS],
                "phases": [
                    {
                        "name": "调理期",
                        "weeks": [1, 2, 3, 4],
                        "intensity": IntensityLevel.LOW,
                        "focus": ["经络疏通", "气血调和"]
                    },
                    {
                        "name": "强化期",
                        "weeks": [5, 6, 7, 8],
                        "intensity": IntensityLevel.LOW,
                        "focus": ["脏腑调理", "体质改善"]
                    },
                    {
                        "name": "养生期",
                        "weeks": [9, 10, 11, 12],
                        "intensity": IntensityLevel.LOW,
                        "focus": ["养生保健", "延年益寿"]
                    }
                ]
            }
        }
    
    async def generate_personalized_plan(
        self,
        profile: UserFitnessProfile,
        preferences: Dict[str, Any] = None
    ) -> TrainingPlan:
        """生成个性化训练计划"""
        try:
            # 选择合适的模板
            template = self._select_plan_template(profile)
            
            # 生成训练课程
            workout_sessions = await self._generate_workout_sessions(
                template, profile, preferences
            )
            
            # 创建周计划
            weekly_schedule = self._create_weekly_schedule(
                workout_sessions, template["sessions_per_week"]
            )
            
            # 计算计划时间
            start_date = datetime.now()
            end_date = start_date + timedelta(weeks=template["duration_weeks"])
            
            plan = TrainingPlan(
                id=f"plan_{profile.user_id}_{int(start_date.timestamp())}",
                user_id=profile.user_id,
                name=template["name"],
                description=f"为{profile.user_id}定制的{template['name']}",
                plan_type="custom",
                duration_weeks=template["duration_weeks"],
                sessions_per_week=template["sessions_per_week"],
                primary_goals=template["goals"],
                workout_sessions=workout_sessions,
                weekly_schedule=weekly_schedule,
                start_date=start_date,
                end_date=end_date
            )
            
            # 根据中医体质调整
            if profile.tcm_constitution:
                plan = await self._adjust_for_tcm_constitution(plan, profile.tcm_constitution)
            
            logger.info(f"为用户 {profile.user_id} 生成了训练计划: {plan.name}")
            return plan
            
        except Exception as e:
            logger.error(f"生成训练计划失败: {e}")
            raise
    
    def _select_plan_template(self, profile: UserFitnessProfile) -> Dict[str, Any]:
        """选择合适的计划模板"""
        # 根据主要目标选择模板
        primary_goal = profile.training_goals[0] if profile.training_goals else TrainingGoal.GENERAL_FITNESS
        
        if primary_goal == TrainingGoal.WEIGHT_LOSS:
            return self.plan_templates["weight_loss"]
        elif primary_goal == TrainingGoal.MUSCLE_BUILDING:
            return self.plan_templates["muscle_building"]
        elif primary_goal == TrainingGoal.TCM_WELLNESS:
            return self.plan_templates["tcm_wellness"]
        else:
            return self.plan_templates["beginner_general"]
    
    async def _generate_workout_sessions(
        self,
        template: Dict[str, Any],
        profile: UserFitnessProfile,
        preferences: Dict[str, Any] = None
    ) -> List[WorkoutSession]:
        """生成训练课程"""
        sessions = []
        
        # 根据目标生成不同类型的训练课程
        if TrainingGoal.WEIGHT_LOSS in template["goals"]:
            sessions.extend(await self._create_cardio_sessions(profile))
            sessions.extend(await self._create_hiit_sessions(profile))
            sessions.extend(await self._create_strength_sessions(profile, focus="endurance"))
        
        elif TrainingGoal.MUSCLE_BUILDING in template["goals"]:
            sessions.extend(await self._create_strength_sessions(profile, focus="hypertrophy"))
            sessions.extend(await self._create_functional_sessions(profile))
        
        elif TrainingGoal.TCM_WELLNESS in template["goals"]:
            sessions.extend(await self._create_tcm_sessions(profile))
            sessions.extend(await self._create_flexibility_sessions(profile))
        
        else:  # 综合健身
            sessions.extend(await self._create_cardio_sessions(profile))
            sessions.extend(await self._create_strength_sessions(profile))
            sessions.extend(await self._create_flexibility_sessions(profile))
        
        return sessions
    
    async def _create_cardio_sessions(self, profile: UserFitnessProfile) -> List[WorkoutSession]:
        """创建有氧训练课程"""
        cardio_exercises = self.exercise_library.get_exercises_by_type(ExerciseType.CARDIO)
        
        # 根据可用器械过滤
        available_exercises = [
            ex for ex in cardio_exercises
            if all(eq in profile.available_equipment for eq in ex.equipment_needed)
        ]
        
        if not available_exercises:
            available_exercises = [
                ex for ex in cardio_exercises
                if EquipmentType.NONE in ex.equipment_needed
            ]
        
        sessions = []
        
        # 低强度有氧
        low_intensity_session = WorkoutSession(
            id="cardio_low",
            name="低强度有氧训练",
            description="提升心肺功能，燃烧脂肪",
            workout_type=ExerciseType.CARDIO,
            target_duration=45,
            target_intensity=IntensityLevel.LOW,
            exercises=available_exercises[:2],
            target_goals=[TrainingGoal.WEIGHT_LOSS, TrainingGoal.GENERAL_FITNESS]
        )
        sessions.append(low_intensity_session)
        
        # 中强度有氧
        moderate_intensity_session = WorkoutSession(
            id="cardio_moderate",
            name="中强度有氧训练",
            description="提升耐力，改善心血管健康",
            workout_type=ExerciseType.CARDIO,
            target_duration=30,
            target_intensity=IntensityLevel.MODERATE,
            exercises=available_exercises[:2],
            target_goals=[TrainingGoal.ENDURANCE_IMPROVEMENT]
        )
        sessions.append(moderate_intensity_session)
        
        return sessions
    
    async def _create_strength_sessions(
        self, 
        profile: UserFitnessProfile, 
        focus: str = "general"
    ) -> List[WorkoutSession]:
        """创建力量训练课程"""
        strength_exercises = self.exercise_library.get_exercises_by_type(ExerciseType.STRENGTH)
        
        # 根据可用器械过滤
        available_exercises = [
            ex for ex in strength_exercises
            if all(eq in profile.available_equipment for eq in ex.equipment_needed)
        ]
        
        sessions = []
        
        # 上肢力量训练
        upper_body_exercises = [
            ex for ex in available_exercises
            if any(muscle in ["胸肌", "背部", "肩部", "三头肌", "二头肌"] 
                   for muscle in ex.target_muscles)
        ]
        
        upper_session = WorkoutSession(
            id="strength_upper",
            name="上肢力量训练",
            description="增强上肢肌肉力量和耐力",
            workout_type=ExerciseType.STRENGTH,
            target_duration=60,
            target_intensity=IntensityLevel.MODERATE,
            exercises=upper_body_exercises[:4],
            target_goals=[TrainingGoal.MUSCLE_BUILDING, TrainingGoal.STRENGTH_GAIN]
        )
        sessions.append(upper_session)
        
        # 下肢力量训练
        lower_body_exercises = [
            ex for ex in available_exercises
            if any(muscle in ["股四头肌", "腘绳肌", "臀大肌", "小腿"] 
                   for muscle in ex.target_muscles)
        ]
        
        lower_session = WorkoutSession(
            id="strength_lower",
            name="下肢力量训练",
            description="增强下肢肌肉力量和功能",
            workout_type=ExerciseType.STRENGTH,
            target_duration=60,
            target_intensity=IntensityLevel.MODERATE,
            exercises=lower_body_exercises[:4],
            target_goals=[TrainingGoal.MUSCLE_BUILDING, TrainingGoal.STRENGTH_GAIN]
        )
        sessions.append(lower_session)
        
        return sessions
    
    async def _create_hiit_sessions(self, profile: UserFitnessProfile) -> List[WorkoutSession]:
        """创建HIIT训练课程"""
        hiit_exercises = self.exercise_library.get_exercises_by_type(ExerciseType.HIIT)
        
        # 根据健身水平调整难度
        max_difficulty = {
            FitnessLevel.BEGINNER: 4,
            FitnessLevel.NOVICE: 5,
            FitnessLevel.INTERMEDIATE: 7,
            FitnessLevel.ADVANCED: 8,
            FitnessLevel.EXPERT: 10,
            FitnessLevel.ELITE: 10
        }.get(profile.fitness_level, 4)
        
        suitable_exercises = [
            ex for ex in hiit_exercises
            if ex.difficulty_level <= max_difficulty
        ]
        
        hiit_session = WorkoutSession(
            id="hiit_training",
            name="高强度间歇训练",
            description="高效燃脂，提升心肺功能",
            workout_type=ExerciseType.HIIT,
            target_duration=25,
            target_intensity=IntensityLevel.VERY_HIGH,
            exercises=suitable_exercises[:4],
            target_goals=[TrainingGoal.WEIGHT_LOSS, TrainingGoal.SPORTS_PERFORMANCE]
        )
        
        return [hiit_session]
    
    async def _create_tcm_sessions(self, profile: UserFitnessProfile) -> List[WorkoutSession]:
        """创建中医养生训练课程"""
        tcm_exercises = []
        
        # 获取所有中医运动
        for exercise_type in [ExerciseType.TCM_TAICHI, ExerciseType.TCM_QIGONG, 
                             ExerciseType.TCM_BADUANJIN, ExerciseType.TCM_WUQINXI]:
            tcm_exercises.extend(self.exercise_library.get_exercises_by_type(exercise_type))
        
        # 根据体质选择合适的运动
        if profile.tcm_constitution:
            suitable_exercises = [
                ex for ex in tcm_exercises
                if (not ex.tcm_constitution_suitability or 
                    profile.tcm_constitution in ex.tcm_constitution_suitability)
            ]
        else:
            suitable_exercises = tcm_exercises
        
        sessions = []
        
        # 太极拳课程
        taichi_exercises = [ex for ex in suitable_exercises if ex.exercise_type == ExerciseType.TCM_TAICHI]
        if taichi_exercises:
            taichi_session = WorkoutSession(
                id="tcm_taichi",
                name="太极拳养生",
                description="调和阴阳，疏通经络",
                workout_type=ExerciseType.TCM_TAICHI,
                target_duration=30,
                target_intensity=IntensityLevel.LOW,
                exercises=taichi_exercises,
                target_goals=[TrainingGoal.TCM_WELLNESS, TrainingGoal.STRESS_RELIEF]
            )
            sessions.append(taichi_session)
        
        # 八段锦课程
        baduanjin_exercises = [ex for ex in suitable_exercises if ex.exercise_type == ExerciseType.TCM_BADUANJIN]
        if baduanjin_exercises:
            baduanjin_session = WorkoutSession(
                id="tcm_baduanjin",
                name="八段锦健身",
                description="调理脏腑，强身健体",
                workout_type=ExerciseType.TCM_BADUANJIN,
                target_duration=20,
                target_intensity=IntensityLevel.LOW,
                exercises=baduanjin_exercises,
                target_goals=[TrainingGoal.TCM_WELLNESS, TrainingGoal.HEALTH_MAINTENANCE]
            )
            sessions.append(baduanjin_session)
        
        return sessions
    
    async def _create_flexibility_sessions(self, profile: UserFitnessProfile) -> List[WorkoutSession]:
        """创建柔韧性训练课程"""
        flexibility_exercises = self.exercise_library.get_exercises_by_type(ExerciseType.FLEXIBILITY)
        yoga_exercises = self.exercise_library.get_exercises_by_type(ExerciseType.YOGA)
        
        all_flexibility = flexibility_exercises + yoga_exercises
        
        flexibility_session = WorkoutSession(
            id="flexibility_training",
            name="柔韧性训练",
            description="提升身体柔韧性，预防运动损伤",
            workout_type=ExerciseType.FLEXIBILITY,
            target_duration=30,
            target_intensity=IntensityLevel.LOW,
            exercises=all_flexibility[:6],
            target_goals=[TrainingGoal.FLEXIBILITY_IMPROVEMENT, TrainingGoal.STRESS_RELIEF]
        )
        
        return [flexibility_session]
    
    async def _create_functional_sessions(self, profile: UserFitnessProfile) -> List[WorkoutSession]:
        """创建功能性训练课程"""
        functional_exercises = self.exercise_library.search_exercises(
            exercise_type=ExerciseType.FUNCTIONAL
        )
        
        if not functional_exercises:
            # 如果没有专门的功能性运动，选择复合动作
            functional_exercises = [
                ex for ex in self.exercise_library.exercises.values()
                if len(ex.target_muscles) >= 3  # 多肌群参与的复合动作
            ]
        
        functional_session = WorkoutSession(
            id="functional_training",
            name="功能性训练",
            description="提升日常生活功能性动作能力",
            workout_type=ExerciseType.FUNCTIONAL,
            target_duration=45,
            target_intensity=IntensityLevel.MODERATE,
            exercises=functional_exercises[:5],
            target_goals=[TrainingGoal.GENERAL_FITNESS, TrainingGoal.SPORTS_PERFORMANCE]
        )
        
        return [functional_session]
    
    def _create_weekly_schedule(
        self, 
        sessions: List[WorkoutSession], 
        sessions_per_week: int
    ) -> Dict[str, List[str]]:
        """创建周训练计划"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        schedule = {day: [] for day in days}
        
        # 根据每周训练次数分配训练日
        if sessions_per_week == 3:
            training_days = ["Monday", "Wednesday", "Friday"]
        elif sessions_per_week == 4:
            training_days = ["Monday", "Tuesday", "Thursday", "Friday"]
        elif sessions_per_week == 5:
            training_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        elif sessions_per_week == 6:
            training_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        else:
            training_days = days[:sessions_per_week]
        
        # 分配训练课程到训练日
        for i, day in enumerate(training_days):
            if i < len(sessions):
                schedule[day].append(sessions[i].id)
        
        return schedule
    
    async def _adjust_for_tcm_constitution(
        self, 
        plan: TrainingPlan, 
        constitution: TCMConstitution
    ) -> TrainingPlan:
        """根据中医体质调整训练计划"""
        constitution_adjustments = {
            TCMConstitution.QI_DEFICIENCY: {
                "intensity_reduction": 0.8,
                "recommended_types": [ExerciseType.TCM_TAICHI, ExerciseType.TCM_QIGONG],
                "avoid_types": [ExerciseType.HIIT],
                "notes": "气虚体质宜缓慢柔和的运动，避免大汗淋漓"
            },
            TCMConstitution.YANG_DEFICIENCY: {
                "intensity_reduction": 0.9,
                "recommended_types": [ExerciseType.TCM_BADUANJIN, ExerciseType.STRENGTH],
                "avoid_types": [ExerciseType.CARDIO],
                "notes": "阳虚体质宜温和的力量训练，避免过度出汗"
            },
            TCMConstitution.YIN_DEFICIENCY: {
                "intensity_reduction": 0.85,
                "recommended_types": [ExerciseType.YOGA, ExerciseType.TCM_TAICHI],
                "avoid_types": [ExerciseType.HIIT],
                "notes": "阴虚体质宜静态拉伸和缓慢运动"
            },
            TCMConstitution.PHLEGM_DAMPNESS: {
                "intensity_increase": 1.1,
                "recommended_types": [ExerciseType.CARDIO, ExerciseType.HIIT],
                "avoid_types": [],
                "notes": "痰湿体质宜多做有氧运动，促进代谢"
            },
            TCMConstitution.DAMP_HEAT: {
                "intensity_reduction": 0.9,
                "recommended_types": [ExerciseType.CARDIO, ExerciseType.FLEXIBILITY],
                "avoid_types": [ExerciseType.HIIT],
                "notes": "湿热体质宜适度有氧运动，避免过度出汗"
            }
        }
        
        if constitution in constitution_adjustments:
            adjustments = constitution_adjustments[constitution]
            
            # 调整训练强度
            if "intensity_reduction" in adjustments:
                for session in plan.workout_sessions:
                    if session.target_intensity == IntensityLevel.HIGH:
                        session.target_intensity = IntensityLevel.MODERATE
                    elif session.target_intensity == IntensityLevel.VERY_HIGH:
                        session.target_intensity = IntensityLevel.HIGH
            
            # 添加推荐运动类型的课程
            if "recommended_types" in adjustments:
                for exercise_type in adjustments["recommended_types"]:
                    tcm_exercises = self.exercise_library.get_exercises_by_type(exercise_type)
                    if tcm_exercises:
                        tcm_session = WorkoutSession(
                            id=f"tcm_{exercise_type.value}",
                            name=f"中医{exercise_type.value}训练",
                            description=f"适合{constitution.value}体质的运动",
                            workout_type=exercise_type,
                            target_duration=30,
                            target_intensity=IntensityLevel.LOW,
                            exercises=tcm_exercises[:2],
                            target_goals=[TrainingGoal.TCM_WELLNESS]
                        )
                        plan.workout_sessions.append(tcm_session)
            
            # 添加体质调理说明
            if plan.notes:
                plan.notes += f"\n{adjustments.get('notes', '')}"
            else:
                plan.notes = adjustments.get('notes', '')
        
        return plan

class ProgressTracker:
    """进度跟踪器"""
    
    def __init__(self):
        self.workout_logs: Dict[str, List[WorkoutLog]] = {}
        self.fitness_assessments: Dict[str, List[FitnessAssessment]] = {}
        self.progress_metrics: Dict[str, List[ProgressMetrics]] = {}
    
    async def log_workout(
        self,
        user_id: str,
        workout_data: Dict[str, Any]
    ) -> WorkoutLog:
        """记录训练日志"""
        try:
            workout_log = WorkoutLog(
                id=f"log_{user_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                session_id=workout_data.get("session_id", ""),
                plan_id=workout_data.get("plan_id"),
                workout_date=datetime.fromisoformat(workout_data.get("workout_date", datetime.now().isoformat())),
                actual_duration=workout_data.get("actual_duration", 0),
                exercises_completed=workout_data.get("exercises_completed", []),
                exercises_skipped=workout_data.get("exercises_skipped", []),
                perceived_exertion=workout_data.get("perceived_exertion"),
                mood_before=workout_data.get("mood_before"),
                mood_after=workout_data.get("mood_after"),
                energy_before=workout_data.get("energy_before"),
                energy_after=workout_data.get("energy_after"),
                pain_level=workout_data.get("pain_level"),
                satisfaction_rating=workout_data.get("satisfaction_rating"),
                calories_burned=workout_data.get("calories_burned"),
                heart_rate_data=workout_data.get("heart_rate_data", {}),
                notes=workout_data.get("notes"),
                achievements=workout_data.get("achievements", []),
                challenges=workout_data.get("challenges", [])
            )
            
            if user_id not in self.workout_logs:
                self.workout_logs[user_id] = []
            
            self.workout_logs[user_id].append(workout_log)
            
            # 分析训练进展
            progress_analysis = await self._analyze_workout_progress(user_id, workout_log)
            
            logger.info(f"记录用户 {user_id} 的训练日志")
            return workout_log
            
        except Exception as e:
            logger.error(f"记录训练日志失败: {e}")
            raise
    
    async def _analyze_workout_progress(
        self, 
        user_id: str, 
        current_log: WorkoutLog
    ) -> Dict[str, Any]:
        """分析训练进展"""
        user_logs = self.workout_logs.get(user_id, [])
        
        if len(user_logs) < 2:
            return {"status": "insufficient_data"}
        
        # 获取最近的训练记录
        recent_logs = sorted(user_logs, key=lambda x: x.workout_date)[-10:]
        
        analysis = {
            "consistency": self._calculate_consistency(recent_logs),
            "intensity_trend": self._analyze_intensity_trend(recent_logs),
            "satisfaction_trend": self._analyze_satisfaction_trend(recent_logs),
            "duration_trend": self._analyze_duration_trend(recent_logs),
            "recommendations": []
        }
        
        # 生成建议
        if analysis["consistency"] < 0.7:
            analysis["recommendations"].append("建议提高训练一致性，保持规律的运动习惯")
        
        if analysis["satisfaction_trend"] < 0:
            analysis["recommendations"].append("训练满意度下降，建议调整训练内容或强度")
        
        if analysis["intensity_trend"] == "plateau":
            analysis["recommendations"].append("训练强度进入平台期，建议增加训练难度或变化")
        
        return analysis
    
    def _calculate_consistency(self, logs: List[WorkoutLog]) -> float:
        """计算训练一致性"""
        if not logs:
            return 0.0
        
        # 计算完成率
        completed_logs = [log for log in logs if log.status == WorkoutStatus.COMPLETED]
        return len(completed_logs) / len(logs)
    
    def _analyze_intensity_trend(self, logs: List[WorkoutLog]) -> str:
        """分析强度趋势"""
        if len(logs) < 3:
            return "insufficient_data"
        
        # 使用主观疲劳度作为强度指标
        exertion_scores = [log.perceived_exertion for log in logs if log.perceived_exertion is not None]
        
        if len(exertion_scores) < 3:
            return "insufficient_data"
        
        # 计算趋势
        recent_avg = np.mean(exertion_scores[-3:])
        earlier_avg = np.mean(exertion_scores[:-3])
        
        if recent_avg > earlier_avg + 0.5:
            return "increasing"
        elif recent_avg < earlier_avg - 0.5:
            return "decreasing"
        else:
            return "plateau"
    
    def _analyze_satisfaction_trend(self, logs: List[WorkoutLog]) -> float:
        """分析满意度趋势"""
        satisfaction_scores = [log.satisfaction_rating for log in logs if log.satisfaction_rating is not None]
        
        if len(satisfaction_scores) < 2:
            return 0.0
        
        # 计算趋势斜率
        x = np.arange(len(satisfaction_scores))
        slope, _ = np.polyfit(x, satisfaction_scores, 1)
        
        return slope
    
    def _analyze_duration_trend(self, logs: List[WorkoutLog]) -> float:
        """分析训练时长趋势"""
        durations = [log.actual_duration for log in logs]
        
        if len(durations) < 2:
            return 0.0
        
        # 计算趋势斜率
        x = np.arange(len(durations))
        slope, _ = np.polyfit(x, durations, 1)
        
        return slope
    
    async def conduct_fitness_assessment(
        self,
        user_id: str,
        assessment_data: Dict[str, Any]
    ) -> FitnessAssessment:
        """进行健身评估"""
        try:
            assessment = FitnessAssessment(
                id=f"assessment_{user_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                assessment_date=datetime.now(),
                assessment_type=assessment_data.get("assessment_type", "progress"),
                cardiovascular_fitness=assessment_data.get("cardiovascular_fitness"),
                muscular_strength=assessment_data.get("muscular_strength", {}),
                muscular_endurance=assessment_data.get("muscular_endurance", {}),
                flexibility_scores=assessment_data.get("flexibility_scores", {}),
                balance_scores=assessment_data.get("balance_scores", {}),
                body_composition=assessment_data.get("body_composition", {}),
                movement_quality=assessment_data.get("movement_quality", {}),
                injury_risk_factors=assessment_data.get("injury_risk_factors", []),
                fitness_confidence=assessment_data.get("fitness_confidence"),
                exercise_enjoyment=assessment_data.get("exercise_enjoyment"),
                goal_progress=assessment_data.get("goal_progress", {}),
                assessor=assessment_data.get("assessor"),
                notes=assessment_data.get("notes")
            )
            
            # 生成评估建议
            assessment.recommendations = await self._generate_assessment_recommendations(assessment)
            
            # 设置下次评估日期
            assessment.next_assessment_date = datetime.now() + timedelta(weeks=4)
            
            if user_id not in self.fitness_assessments:
                self.fitness_assessments[user_id] = []
            
            self.fitness_assessments[user_id].append(assessment)
            
            logger.info(f"完成用户 {user_id} 的健身评估")
            return assessment
            
        except Exception as e:
            logger.error(f"健身评估失败: {e}")
            raise
    
    async def _generate_assessment_recommendations(
        self, 
        assessment: FitnessAssessment
    ) -> List[str]:
        """生成评估建议"""
        recommendations = []
        
        # 心肺功能建议
        if assessment.cardiovascular_fitness and assessment.cardiovascular_fitness < 30:
            recommendations.append("建议增加有氧运动训练，提升心肺功能")
        
        # 力量建议
        if assessment.muscular_strength:
            weak_areas = [area for area, score in assessment.muscular_strength.items() if score < 3]
            if weak_areas:
                recommendations.append(f"建议加强{', '.join(weak_areas)}的力量训练")
        
        # 柔韧性建议
        if assessment.flexibility_scores:
            tight_areas = [area for area, score in assessment.flexibility_scores.items() if score < 3]
            if tight_areas:
                recommendations.append(f"建议增加{', '.join(tight_areas)}的拉伸训练")
        
        # 平衡能力建议
        if assessment.balance_scores:
            avg_balance = np.mean(list(assessment.balance_scores.values()))
            if avg_balance < 3:
                recommendations.append("建议增加平衡训练，如瑜伽或太极")
        
        # 运动损伤风险建议
        if assessment.injury_risk_factors:
            recommendations.append("存在运动损伤风险，建议在专业指导下进行训练")
        
        # 心理状态建议
        if assessment.fitness_confidence and assessment.fitness_confidence < 5:
            recommendations.append("建议从简单动作开始，逐步建立运动信心")
        
        if assessment.exercise_enjoyment and assessment.exercise_enjoyment < 5:
            recommendations.append("建议尝试不同类型的运动，找到自己喜欢的运动方式")
        
        return recommendations
    
    async def calculate_progress_metrics(
        self,
        user_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> ProgressMetrics:
        """计算进度指标"""
        try:
            user_logs = self.workout_logs.get(user_id, [])
            period_logs = [
                log for log in user_logs
                if period_start <= log.workout_date <= period_end
            ]
            
            metrics = ProgressMetrics(
                user_id=user_id,
                calculation_date=datetime.now(),
                period_start=period_start,
                period_end=period_end
            )
            
            # 训练统计
            metrics.total_workouts = len([log for log in period_logs if log.status == WorkoutStatus.COMPLETED])
            metrics.planned_workouts = len(period_logs)
            metrics.completion_rate = metrics.total_workouts / max(metrics.planned_workouts, 1)
            
            if period_logs:
                metrics.average_workout_duration = np.mean([log.actual_duration for log in period_logs])
                metrics.total_training_time = sum(log.actual_duration for log in period_logs)
            
            # 主观指标
            satisfaction_scores = [log.satisfaction_rating for log in period_logs if log.satisfaction_rating]
            if satisfaction_scores:
                metrics.average_satisfaction = np.mean(satisfaction_scores)
            
            energy_improvements = [
                (log.energy_after - log.energy_before) for log in period_logs
                if log.energy_after and log.energy_before
            ]
            if energy_improvements:
                metrics.average_energy_improvement = np.mean(energy_improvements)
            
            mood_improvements = [
                (log.mood_after - log.mood_before) for log in period_logs
                if log.mood_after and log.mood_before
            ]
            if mood_improvements:
                metrics.average_mood_improvement = np.mean(mood_improvements)
            
            # 计算风险评分
            metrics.injury_risk_score = await self._calculate_injury_risk(user_id, period_logs)
            metrics.burnout_risk_score = await self._calculate_burnout_risk(user_id, period_logs)
            
            if user_id not in self.progress_metrics:
                self.progress_metrics[user_id] = []
            
            self.progress_metrics[user_id].append(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"计算进度指标失败: {e}")
            raise
    
    async def _calculate_injury_risk(
        self, 
        user_id: str, 
        logs: List[WorkoutLog]
    ) -> float:
        """计算运动损伤风险"""
        if not logs:
            return 0.0
        
        risk_factors = 0
        
        # 疼痛水平
        pain_levels = [log.pain_level for log in logs if log.pain_level is not None]
        if pain_levels and np.mean(pain_levels) > 3:
            risk_factors += 0.3
        
        # 过度训练指标
        exertion_levels = [log.perceived_exertion for log in logs if log.perceived_exertion is not None]
        if exertion_levels and np.mean(exertion_levels) > 8:
            risk_factors += 0.2
        
        # 训练频率过高
        if len(logs) > 6 * (len(logs) / 7):  # 每周超过6次
            risk_factors += 0.2
        
        # 满意度下降
        satisfaction_scores = [log.satisfaction_rating for log in logs if log.satisfaction_rating]
        if satisfaction_scores and np.mean(satisfaction_scores) < 3:
            risk_factors += 0.3
        
        return min(risk_factors, 1.0)
    
    async def _calculate_burnout_risk(
        self, 
        user_id: str, 
        logs: List[WorkoutLog]
    ) -> float:
        """计算运动倦怠风险"""
        if not logs:
            return 0.0
        
        risk_factors = 0
        
        # 满意度趋势
        satisfaction_trend = self._analyze_satisfaction_trend(logs)
        if satisfaction_trend < -0.1:
            risk_factors += 0.4
        
        # 能量水平变化
        energy_improvements = [
            (log.energy_after - log.energy_before) for log in logs
            if log.energy_after and log.energy_before
        ]
        if energy_improvements and np.mean(energy_improvements) < 0:
            risk_factors += 0.3
        
        # 训练一致性下降
        consistency = self._calculate_consistency(logs)
        if consistency < 0.6:
            risk_factors += 0.3
        
        return min(risk_factors, 1.0)
    
    async def get_user_progress_summary(self, user_id: str) -> Dict[str, Any]:
        """获取用户进度总结"""
        try:
            # 获取最近30天的数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            recent_metrics = await self.calculate_progress_metrics(user_id, start_date, end_date)
            recent_logs = [
                log for log in self.workout_logs.get(user_id, [])
                if start_date <= log.workout_date <= end_date
            ]
            
            # 获取最新评估
            assessments = self.fitness_assessments.get(user_id, [])
            latest_assessment = max(assessments, key=lambda x: x.assessment_date) if assessments else None
            
            summary = {
                "user_id": user_id,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "training_stats": {
                    "total_workouts": recent_metrics.total_workouts,
                    "completion_rate": recent_metrics.completion_rate,
                    "average_duration": recent_metrics.average_workout_duration,
                    "total_time": recent_metrics.total_training_time
                },
                "performance_trends": {
                    "satisfaction": recent_metrics.average_satisfaction,
                    "energy_improvement": recent_metrics.average_energy_improvement,
                    "mood_improvement": recent_metrics.average_mood_improvement
                },
                "risk_assessment": {
                    "injury_risk": recent_metrics.injury_risk_score,
                    "burnout_risk": recent_metrics.burnout_risk_score
                },
                "latest_assessment": latest_assessment.id if latest_assessment else None,
                "recommendations": await self._generate_progress_recommendations(user_id, recent_metrics, recent_logs)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"获取进度总结失败: {e}")
            return {"error": str(e)}
    
    async def _generate_progress_recommendations(
        self,
        user_id: str,
        metrics: ProgressMetrics,
        logs: List[WorkoutLog]
    ) -> List[str]:
        """生成进度建议"""
        recommendations = []
        
        # 完成率建议
        if metrics.completion_rate < 0.7:
            recommendations.append("训练完成率较低，建议调整训练计划或降低训练强度")
        elif metrics.completion_rate > 0.9:
            recommendations.append("训练完成率很高，可以考虑适当增加训练挑战")
        
        # 满意度建议
        if metrics.average_satisfaction and metrics.average_satisfaction < 6:
            recommendations.append("训练满意度偏低，建议尝试新的运动类型或调整训练内容")
        
        # 风险建议
        if metrics.injury_risk_score and metrics.injury_risk_score > 0.6:
            recommendations.append("运动损伤风险较高，建议降低训练强度并注意休息恢复")
        
        if metrics.burnout_risk_score and metrics.burnout_risk_score > 0.6:
            recommendations.append("存在运动倦怠风险，建议增加训练的趣味性和多样性")
        
        # 进步建议
        if metrics.average_energy_improvement and metrics.average_energy_improvement > 2:
            recommendations.append("训练效果良好，精力水平有明显提升，继续保持")
        
        return recommendations

class IntelligentExerciseEngine:
    """智能运动训练引擎主类"""
    
    def __init__(self, config: Dict[str, Any], metrics_collector: Optional[MetricsCollector] = None):
        self.config = config
        self.metrics_collector = metrics_collector
        
        # 核心组件
        self.exercise_library = ExerciseLibrary()
        self.plan_generator = WorkoutPlanGenerator(self.exercise_library)
        self.progress_tracker = ProgressTracker()
        
        # 用户档案存储
        self.user_profiles: Dict[str, UserFitnessProfile] = {}
        self.training_plans: Dict[str, TrainingPlan] = {}
        
        # 配置参数
        self.max_plan_duration = config.get("max_plan_duration_weeks", 24)
        self.min_session_duration = config.get("min_session_duration", 15)
        self.max_session_duration = config.get("max_session_duration", 120)
        
        # 运行状态
        self.initialized = False
    
    async def initialize(self):
        """初始化运动训练引擎"""
        try:
            # 加载配置
            await self._load_configuration()
            
            # 初始化组件
            await self._initialize_components()
            
            self.initialized = True
            logger.info("智能运动训练引擎初始化完成")
            
        except Exception as e:
            logger.error(f"运动训练引擎初始化失败: {e}")
            raise
    
    async def _load_configuration(self):
        """加载配置"""
        # 这里可以从配置文件或数据库加载配置
        pass
    
    async def _initialize_components(self):
        """初始化组件"""
        # 这里可以进行组件的进一步初始化
        pass
    
    @trace_operation("exercise_engine.create_profile", SpanKind.INTERNAL)
    async def create_fitness_profile(
        self,
        user_id: str,
        profile_data: Dict[str, Any]
    ) -> UserFitnessProfile:
        """创建用户健身档案"""
        try:
            if not self.initialized:
                await self.initialize()
            
            profile = UserFitnessProfile(
                user_id=user_id,
                age=profile_data["age"],
                gender=profile_data["gender"],
                height=profile_data["height"],
                weight=profile_data["weight"],
                body_fat_percentage=profile_data.get("body_fat_percentage"),
                resting_heart_rate=profile_data.get("resting_heart_rate"),
                max_heart_rate=profile_data.get("max_heart_rate"),
                fitness_level=FitnessLevel(profile_data.get("fitness_level", "beginner")),
                training_goals=[TrainingGoal(goal) for goal in profile_data.get("training_goals", [])],
                available_equipment=[EquipmentType(eq) for eq in profile_data.get("available_equipment", [])],
                workout_frequency=profile_data.get("workout_frequency", 3),
                session_duration=profile_data.get("session_duration", 60),
                preferred_workout_times=profile_data.get("preferred_workout_times", []),
                medical_conditions=profile_data.get("medical_conditions", []),
                injuries=profile_data.get("injuries", []),
                limitations=profile_data.get("limitations", []),
                tcm_constitution=TCMConstitution(profile_data["tcm_constitution"]) if profile_data.get("tcm_constitution") else None,
                stress_level=profile_data.get("stress_level"),
                sleep_quality=profile_data.get("sleep_quality"),
                energy_level=profile_data.get("energy_level"),
                motivation_level=profile_data.get("motivation_level")
            )
            
            self.user_profiles[user_id] = profile
            
            # 记录指标
            if self.metrics_collector:
                await self.metrics_collector.increment_counter(
                    "fitness_profiles_created",
                    {"user_id": user_id}
                )
            
            logger.info(f"创建用户健身档案: {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"创建健身档案失败: {e}")
            raise
    
    @trace_operation("exercise_engine.generate_plan", SpanKind.INTERNAL)
    async def generate_training_plan(
        self,
        user_id: str,
        preferences: Dict[str, Any] = None
    ) -> TrainingPlan:
        """生成训练计划"""
        try:
            if not self.initialized:
                await self.initialize()
            
            profile = self.user_profiles.get(user_id)
            if not profile:
                raise ValueError(f"用户 {user_id} 的健身档案不存在")
            
            # 生成个性化训练计划
            plan = await self.plan_generator.generate_personalized_plan(profile, preferences)
            
            self.training_plans[plan.id] = plan
            
            # 记录指标
            if self.metrics_collector:
                await self.metrics_collector.increment_counter(
                    "training_plans_generated",
                    {
                        "user_id": user_id,
                        "plan_type": plan.plan_type,
                        "duration_weeks": str(plan.duration_weeks)
                    }
                )
            
            logger.info(f"为用户 {user_id} 生成训练计划: {plan.name}")
            return plan
            
        except Exception as e:
            logger.error(f"生成训练计划失败: {e}")
            raise
    
    @trace_operation("exercise_engine.log_workout", SpanKind.INTERNAL)
    async def log_workout(
        self,
        user_id: str,
        workout_data: Dict[str, Any]
    ) -> WorkoutLog:
        """记录训练日志"""
        try:
            if not self.initialized:
                await self.initialize()
            
            workout_log = await self.progress_tracker.log_workout(user_id, workout_data)
            
            # 记录指标
            if self.metrics_collector:
                await self.metrics_collector.increment_counter(
                    "workouts_logged",
                    {
                        "user_id": user_id,
                        "status": workout_log.status.value
                    }
                )
                
                if workout_log.actual_duration:
                    await self.metrics_collector.record_histogram(
                        "workout_duration",
                        workout_log.actual_duration,
                        {"user_id": user_id}
                    )
            
            return workout_log
            
        except Exception as e:
            logger.error(f"记录训练日志失败: {e}")
            raise
    
    @trace_operation("exercise_engine.conduct_assessment", SpanKind.INTERNAL)
    async def conduct_fitness_assessment(
        self,
        user_id: str,
        assessment_data: Dict[str, Any]
    ) -> FitnessAssessment:
        """进行健身评估"""
        try:
            if not self.initialized:
                await self.initialize()
            
            assessment = await self.progress_tracker.conduct_fitness_assessment(
                user_id, assessment_data
            )
            
            # 记录指标
            if self.metrics_collector:
                await self.metrics_collector.increment_counter(
                    "fitness_assessments_conducted",
                    {
                        "user_id": user_id,
                        "assessment_type": assessment.assessment_type
                    }
                )
            
            return assessment
            
        except Exception as e:
            logger.error(f"健身评估失败: {e}")
            raise
    
    async def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """获取用户进度"""
        try:
            if not self.initialized:
                await self.initialize()
            
            progress_summary = await self.progress_tracker.get_user_progress_summary(user_id)
            
            return progress_summary
            
        except Exception as e:
            logger.error(f"获取用户进度失败: {e}")
            return {"error": str(e)}
    
    async def search_exercises(
        self,
        search_criteria: Dict[str, Any]
    ) -> List[Exercise]:
        """搜索运动"""
        try:
            if not self.initialized:
                await self.initialize()
            
            exercises = self.exercise_library.search_exercises(
                exercise_type=ExerciseType(search_criteria["exercise_type"]) if search_criteria.get("exercise_type") else None,
                intensity_level=IntensityLevel(search_criteria["intensity_level"]) if search_criteria.get("intensity_level") else None,
                equipment_available=[EquipmentType(eq) for eq in search_criteria.get("equipment_available", [])],
                target_muscles=search_criteria.get("target_muscles"),
                max_difficulty=search_criteria.get("max_difficulty"),
                tcm_constitution=TCMConstitution(search_criteria["tcm_constitution"]) if search_criteria.get("tcm_constitution") else None
            )
            
            return exercises
            
        except Exception as e:
            logger.error(f"搜索运动失败: {e}")
            return []
    
    async def get_exercise_recommendations(
        self,
        user_id: str,
        recommendation_type: str = "general"
    ) -> List[Exercise]:
        """获取运动推荐"""
        try:
            if not self.initialized:
                await self.initialize()
            
            profile = self.user_profiles.get(user_id)
            if not profile:
                return []
            
            # 根据用户档案推荐运动
            if recommendation_type == "tcm":
                # 中医养生运动推荐
                tcm_exercises = []
                for exercise_type in [ExerciseType.TCM_TAICHI, ExerciseType.TCM_QIGONG, 
                                     ExerciseType.TCM_BADUANJIN, ExerciseType.TCM_WUQINXI]:
                    tcm_exercises.extend(self.exercise_library.get_exercises_by_type(exercise_type))
                
                if profile.tcm_constitution:
                    suitable_exercises = [
                        ex for ex in tcm_exercises
                        if (not ex.tcm_constitution_suitability or 
                            profile.tcm_constitution in ex.tcm_constitution_suitability)
                    ]
                    return suitable_exercises[:5]
                else:
                    return tcm_exercises[:5]
            
            elif recommendation_type == "beginner":
                # 初学者推荐
                return self.exercise_library.search_exercises(
                    max_difficulty=3,
                    equipment_available=profile.available_equipment
                )[:10]
            
            else:
                # 综合推荐
                recommendations = []
                
                # 根据训练目标推荐
                for goal in profile.training_goals:
                    if goal == TrainingGoal.WEIGHT_LOSS:
                        recommendations.extend(
                            self.exercise_library.get_exercises_by_type(ExerciseType.CARDIO)[:2]
                        )
                        recommendations.extend(
                            self.exercise_library.get_exercises_by_type(ExerciseType.HIIT)[:2]
                        )
                    elif goal == TrainingGoal.MUSCLE_BUILDING:
                        recommendations.extend(
                            self.exercise_library.get_exercises_by_type(ExerciseType.STRENGTH)[:3]
                        )
                    elif goal == TrainingGoal.FLEXIBILITY_IMPROVEMENT:
                        recommendations.extend(
                            self.exercise_library.get_exercises_by_type(ExerciseType.FLEXIBILITY)[:2]
                        )
                        recommendations.extend(
                            self.exercise_library.get_exercises_by_type(ExerciseType.YOGA)[:2]
                        )
                
                # 去重并限制数量
                unique_recommendations = []
                seen_ids = set()
                for ex in recommendations:
                    if ex.id not in seen_ids:
                        unique_recommendations.append(ex)
                        seen_ids.add(ex.id)
                
                return unique_recommendations[:10]
            
        except Exception as e:
            logger.error(f"获取运动推荐失败: {e}")
            return []
    
    async def update_fitness_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """更新健身档案"""
        try:
            if user_id not in self.user_profiles:
                return False
            
            profile = self.user_profiles[user_id]
            
            for key, value in updates.items():
                if hasattr(profile, key):
                    if key == "training_goals":
                        profile.training_goals = [TrainingGoal(goal) for goal in value]
                    elif key == "available_equipment":
                        profile.available_equipment = [EquipmentType(eq) for eq in value]
                    elif key == "tcm_constitution":
                        profile.tcm_constitution = TCMConstitution(value) if value else None
                    elif key == "fitness_level":
                        profile.fitness_level = FitnessLevel(value)
                    else:
                        setattr(profile, key, value)
            
            profile.updated_at = datetime.now()
            
            logger.info(f"更新用户健身档案: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"更新健身档案失败: {e}")
            return False
    
    async def get_training_plan(self, plan_id: str) -> Optional[TrainingPlan]:
        """获取训练计划"""
        return self.training_plans.get(plan_id)
    
    async def get_user_training_plans(self, user_id: str) -> List[TrainingPlan]:
        """获取用户的训练计划"""
        return [plan for plan in self.training_plans.values() if plan.user_id == user_id]
    
    async def get_exercise_statistics(self) -> Dict[str, Any]:
        """获取运动统计"""
        try:
            total_users = len(self.user_profiles)
            total_plans = len(self.training_plans)
            total_exercises = len(self.exercise_library.exercises)
            
            # 统计训练目标分布
            goal_distribution = {}
            for profile in self.user_profiles.values():
                for goal in profile.training_goals:
                    goal_distribution[goal.value] = goal_distribution.get(goal.value, 0) + 1
            
            # 统计健身水平分布
            fitness_level_distribution = {}
            for profile in self.user_profiles.values():
                level = profile.fitness_level.value
                fitness_level_distribution[level] = fitness_level_distribution.get(level, 0) + 1
            
            # 统计运动类型分布
            exercise_type_distribution = {}
            for exercise in self.exercise_library.exercises.values():
                ex_type = exercise.exercise_type.value
                exercise_type_distribution[ex_type] = exercise_type_distribution.get(ex_type, 0) + 1
            
            return {
                "total_users": total_users,
                "total_plans": total_plans,
                "total_exercises": total_exercises,
                "goal_distribution": goal_distribution,
                "fitness_level_distribution": fitness_level_distribution,
                "exercise_type_distribution": exercise_type_distribution,
                "active_plans": len([p for p in self.training_plans.values() if p.status == WorkoutStatus.PLANNED])
            }
            
        except Exception as e:
            logger.error(f"获取运动统计失败: {e}")
            return {"error": str(e)}

# 全局运动训练引擎实例
_exercise_engine: Optional[IntelligentExerciseEngine] = None

def initialize_exercise_engine(
    config: Dict[str, Any],
    metrics_collector: Optional[MetricsCollector] = None
) -> IntelligentExerciseEngine:
    """初始化运动训练引擎"""
    global _exercise_engine
    _exercise_engine = IntelligentExerciseEngine(config, metrics_collector)
    return _exercise_engine

def get_exercise_engine() -> Optional[IntelligentExerciseEngine]:
    """获取运动训练引擎实例"""
    return _exercise_engine 