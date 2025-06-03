#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能康复训练引擎 - 提供个性化康复训练计划制定、进度跟踪、效果评估
结合现代康复医学和中医传统康复理念，为用户提供科学的康复训练方案
"""

from typing import Dict, List, Any, Optional, Tuple, Union, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from loguru import logger
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind

class RehabilitationType(str, Enum):
    """康复类型"""
    PHYSICAL_THERAPY = "physical_therapy"           # 物理治疗
    OCCUPATIONAL_THERAPY = "occupational_therapy"   # 作业治疗
    SPEECH_THERAPY = "speech_therapy"               # 言语治疗
    COGNITIVE_THERAPY = "cognitive_therapy"         # 认知治疗
    CARDIAC_REHAB = "cardiac_rehab"                 # 心脏康复
    PULMONARY_REHAB = "pulmonary_rehab"            # 肺康复
    NEUROLOGICAL_REHAB = "neurological_rehab"       # 神经康复
    ORTHOPEDIC_REHAB = "orthopedic_rehab"          # 骨科康复
    TCM_REHAB = "tcm_rehab"                        # 中医康复
    SPORTS_REHAB = "sports_rehab"                  # 运动康复

class ExerciseType(str, Enum):
    """运动类型"""
    STRENGTH_TRAINING = "strength_training"         # 力量训练
    FLEXIBILITY = "flexibility"                     # 柔韧性训练
    BALANCE = "balance"                             # 平衡训练
    COORDINATION = "coordination"                   # 协调性训练
    ENDURANCE = "endurance"                         # 耐力训练
    RANGE_OF_MOTION = "range_of_motion"            # 关节活动度训练
    FUNCTIONAL = "functional"                       # 功能性训练
    BREATHING = "breathing"                         # 呼吸训练
    COGNITIVE = "cognitive"                         # 认知训练
    RELAXATION = "relaxation"                       # 放松训练

class DifficultyLevel(str, Enum):
    """难度级别"""
    BEGINNER = "beginner"       # 初级
    EASY = "easy"               # 简单
    MODERATE = "moderate"       # 中等
    HARD = "hard"               # 困难
    EXPERT = "expert"           # 专家级

class ProgressStatus(str, Enum):
    """进度状态"""
    NOT_STARTED = "not_started"     # 未开始
    IN_PROGRESS = "in_progress"     # 进行中
    COMPLETED = "completed"         # 已完成
    PAUSED = "paused"               # 暂停
    CANCELLED = "cancelled"         # 取消
    MODIFIED = "modified"           # 已修改

class AssessmentType(str, Enum):
    """评估类型"""
    INITIAL = "initial"             # 初始评估
    PROGRESS = "progress"           # 进度评估
    FINAL = "final"                 # 最终评估
    PERIODIC = "periodic"           # 定期评估
    EMERGENCY = "emergency"         # 紧急评估

@dataclass
class RehabilitationGoal:
    """康复目标"""
    id: str
    name: str
    description: str
    target_value: float
    current_value: float = 0.0
    unit: str = ""
    priority: int = 1                               # 优先级 (1-5)
    target_date: Optional[datetime] = None
    achieved: bool = False
    achievement_date: Optional[datetime] = None
    progress_percentage: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Exercise:
    """运动项目"""
    id: str
    name: str
    description: str
    exercise_type: ExerciseType
    difficulty_level: DifficultyLevel
    duration_minutes: int
    repetitions: Optional[int] = None
    sets: Optional[int] = None
    rest_seconds: Optional[int] = None
    equipment_needed: List[str] = field(default_factory=list)
    instructions: List[str] = field(default_factory=list)
    precautions: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    target_muscles: List[str] = field(default_factory=list)
    calories_burned: Optional[float] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None

@dataclass
class TrainingSession:
    """训练会话"""
    id: str
    user_id: str
    plan_id: str
    exercises: List[Exercise]
    scheduled_date: datetime
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    completed_exercises: List[str] = field(default_factory=list)
    skipped_exercises: List[str] = field(default_factory=list)
    modified_exercises: Dict[str, Dict] = field(default_factory=dict)
    pain_level_before: Optional[int] = None         # 训练前疼痛等级 (0-10)
    pain_level_after: Optional[int] = None          # 训练后疼痛等级 (0-10)
    fatigue_level: Optional[int] = None             # 疲劳等级 (0-10)
    satisfaction_score: Optional[int] = None        # 满意度 (1-5)
    notes: Optional[str] = None
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RehabilitationPlan:
    """康复计划"""
    id: str
    user_id: str
    name: str
    description: str
    rehabilitation_type: RehabilitationType
    goals: List[RehabilitationGoal]
    total_duration_weeks: int
    sessions_per_week: int
    session_duration_minutes: int
    difficulty_progression: bool = True
    created_date: datetime = field(default_factory=datetime.now)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    progress_percentage: float = 0.0
    created_by: Optional[str] = None                # 创建者（医生/治疗师）
    approved_by: Optional[str] = None               # 审批者
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FunctionalAssessment:
    """功能评估"""
    id: str
    user_id: str
    assessment_type: AssessmentType
    assessment_date: datetime
    assessor: Optional[str] = None
    
    # 基础功能评估
    range_of_motion: Dict[str, float] = field(default_factory=dict)  # 关节活动度
    muscle_strength: Dict[str, float] = field(default_factory=dict)  # 肌力
    balance_score: Optional[float] = None
    coordination_score: Optional[float] = None
    endurance_score: Optional[float] = None
    
    # 疼痛评估
    pain_level: Optional[int] = None                # 疼痛等级 (0-10)
    pain_locations: List[str] = field(default_factory=list)
    pain_description: Optional[str] = None
    
    # 功能性评估
    activities_of_daily_living: Dict[str, float] = field(default_factory=dict)
    quality_of_life_score: Optional[float] = None
    
    # 心理评估
    motivation_level: Optional[int] = None          # 动机水平 (1-5)
    anxiety_level: Optional[int] = None             # 焦虑水平 (1-5)
    depression_score: Optional[float] = None
    
    # 整体评分
    overall_function_score: Optional[float] = None
    improvement_percentage: Optional[float] = None
    
    notes: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProgressMetrics:
    """进度指标"""
    user_id: str
    plan_id: str
    measurement_date: datetime
    
    # 训练指标
    sessions_completed: int = 0
    sessions_planned: int = 0
    completion_rate: float = 0.0
    average_session_duration: float = 0.0
    
    # 功能改善指标
    functional_improvement: Dict[str, float] = field(default_factory=dict)
    pain_reduction: Optional[float] = None
    strength_improvement: Dict[str, float] = field(default_factory=dict)
    
    # 目标达成指标
    goals_achieved: int = 0
    total_goals: int = 0
    goal_achievement_rate: float = 0.0
    
    # 满意度指标
    average_satisfaction: Optional[float] = None
    adherence_rate: float = 0.0
    
    # 预测指标
    predicted_completion_date: Optional[datetime] = None
    success_probability: Optional[float] = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)

class ExerciseLibrary:
    """运动库"""
    
    def __init__(self):
        self.exercises = {}
        self.exercise_categories = {}
        self.progression_rules = {}
        self._load_exercise_database()
    
    def _load_exercise_database(self):
        """加载运动数据库"""
        # 力量训练运动
        self.exercises.update({
            "wall_push_up": Exercise(
                id="wall_push_up",
                name="靠墙俯卧撑",
                description="站立面对墙壁进行的俯卧撑变式",
                exercise_type=ExerciseType.STRENGTH_TRAINING,
                difficulty_level=DifficultyLevel.BEGINNER,
                duration_minutes=5,
                repetitions=10,
                sets=2,
                rest_seconds=30,
                instructions=[
                    "面对墙壁站立，距离约一臂长",
                    "双手平放在墙上，与肩同宽",
                    "身体向前倾斜，然后推回原位",
                    "保持身体挺直"
                ],
                target_muscles=["胸肌", "三角肌", "三头肌"],
                precautions=["避免过度用力", "保持呼吸顺畅"]
            ),
            
            "seated_leg_extension": Exercise(
                id="seated_leg_extension",
                name="坐姿腿部伸展",
                description="坐在椅子上进行的腿部力量训练",
                exercise_type=ExerciseType.STRENGTH_TRAINING,
                difficulty_level=DifficultyLevel.EASY,
                duration_minutes=8,
                repetitions=12,
                sets=2,
                rest_seconds=45,
                equipment_needed=["椅子"],
                instructions=[
                    "坐在椅子上，背部挺直",
                    "缓慢伸直一条腿",
                    "保持2秒，然后缓慢放下",
                    "交替进行"
                ],
                target_muscles=["股四头肌"],
                precautions=["动作要缓慢控制", "避免膝关节过度伸展"]
            )
        })
        
        # 柔韧性训练
        self.exercises.update({
            "neck_stretch": Exercise(
                id="neck_stretch",
                name="颈部拉伸",
                description="缓解颈部紧张的拉伸运动",
                exercise_type=ExerciseType.FLEXIBILITY,
                difficulty_level=DifficultyLevel.BEGINNER,
                duration_minutes=5,
                instructions=[
                    "坐直或站立，肩膀放松",
                    "缓慢将头向一侧倾斜",
                    "保持15-30秒",
                    "回到中心位置，换另一侧"
                ],
                target_muscles=["颈部肌群"],
                precautions=["动作要轻柔", "避免强迫拉伸"]
            ),
            
            "shoulder_roll": Exercise(
                id="shoulder_roll",
                name="肩部转动",
                description="改善肩部活动度的运动",
                exercise_type=ExerciseType.FLEXIBILITY,
                difficulty_level=DifficultyLevel.BEGINNER,
                duration_minutes=3,
                repetitions=10,
                instructions=[
                    "站立或坐直",
                    "缓慢向前转动肩膀",
                    "然后向后转动",
                    "保持动作流畅"
                ],
                target_muscles=["肩部肌群"],
                precautions=["避免快速转动"]
            )
        })
        
        # 平衡训练
        self.exercises.update({
            "single_leg_stand": Exercise(
                id="single_leg_stand",
                name="单腿站立",
                description="提高平衡能力的基础训练",
                exercise_type=ExerciseType.BALANCE,
                difficulty_level=DifficultyLevel.EASY,
                duration_minutes=5,
                instructions=[
                    "站立，双脚并拢",
                    "抬起一只脚，保持平衡",
                    "尽量保持30秒",
                    "换另一只脚"
                ],
                equipment_needed=["椅子（支撑用）"],
                precautions=["旁边准备支撑物", "避免在湿滑地面进行"],
                contraindications=["严重平衡障碍", "未控制的眩晕"]
            )
        })
        
        # 呼吸训练
        self.exercises.update({
            "diaphragmatic_breathing": Exercise(
                id="diaphragmatic_breathing",
                name="腹式呼吸",
                description="改善呼吸模式的训练",
                exercise_type=ExerciseType.BREATHING,
                difficulty_level=DifficultyLevel.BEGINNER,
                duration_minutes=10,
                instructions=[
                    "舒适地坐着或躺下",
                    "一手放在胸部，一手放在腹部",
                    "通过鼻子缓慢吸气，腹部上升",
                    "通过嘴巴缓慢呼气，腹部下降"
                ],
                precautions=["不要强迫呼吸", "如感到头晕立即停止"]
            )
        })
        
        # 中医康复运动
        self.exercises.update({
            "tai_chi_basic": Exercise(
                id="tai_chi_basic",
                name="太极基础动作",
                description="太极拳基础动作练习",
                exercise_type=ExerciseType.COORDINATION,
                difficulty_level=DifficultyLevel.MODERATE,
                duration_minutes=15,
                instructions=[
                    "站立，双脚与肩同宽",
                    "双手自然下垂",
                    "缓慢抬起双臂至胸前",
                    "配合呼吸，动作要缓慢流畅"
                ],
                target_muscles=["全身肌群"],
                precautions=["动作要缓慢", "注意呼吸配合"]
            ),
            
            "qigong_standing": Exercise(
                id="qigong_standing",
                name="气功站桩",
                description="气功基础站桩练习",
                exercise_type=ExerciseType.BALANCE,
                difficulty_level=DifficultyLevel.MODERATE,
                duration_minutes=10,
                instructions=[
                    "双脚与肩同宽站立",
                    "微屈膝盖，身体放松",
                    "双臂环抱，如抱球状",
                    "保持自然呼吸"
                ],
                precautions=["不要过度用力", "感到疲劳时及时休息"]
            )
        })
        
        # 运动分类
        self.exercise_categories = {
            ExerciseType.STRENGTH_TRAINING: ["wall_push_up", "seated_leg_extension"],
            ExerciseType.FLEXIBILITY: ["neck_stretch", "shoulder_roll"],
            ExerciseType.BALANCE: ["single_leg_stand", "qigong_standing"],
            ExerciseType.BREATHING: ["diaphragmatic_breathing"],
            ExerciseType.COORDINATION: ["tai_chi_basic"]
        }
        
        # 进阶规则
        self.progression_rules = {
            "wall_push_up": {
                "next_exercise": "knee_push_up",
                "progression_criteria": {"repetitions": 15, "sets": 3}
            },
            "seated_leg_extension": {
                "next_exercise": "standing_leg_extension",
                "progression_criteria": {"repetitions": 15, "sets": 3}
            }
        }
    
    async def get_exercises_by_type(self, exercise_type: ExerciseType) -> List[Exercise]:
        """根据类型获取运动"""
        exercise_ids = self.exercise_categories.get(exercise_type, [])
        return [self.exercises[ex_id] for ex_id in exercise_ids if ex_id in self.exercises]
    
    async def get_exercise_by_id(self, exercise_id: str) -> Optional[Exercise]:
        """根据ID获取运动"""
        return self.exercises.get(exercise_id)
    
    async def get_progression_exercise(self, current_exercise_id: str) -> Optional[Exercise]:
        """获取进阶运动"""
        progression_info = self.progression_rules.get(current_exercise_id)
        if progression_info:
            next_exercise_id = progression_info["next_exercise"]
            return self.exercises.get(next_exercise_id)
        return None
    
    async def filter_exercises(
        self,
        exercise_type: Optional[ExerciseType] = None,
        difficulty_level: Optional[DifficultyLevel] = None,
        max_duration: Optional[int] = None,
        equipment_available: Optional[List[str]] = None
    ) -> List[Exercise]:
        """筛选运动"""
        filtered_exercises = []
        
        for exercise in self.exercises.values():
            # 类型筛选
            if exercise_type and exercise.exercise_type != exercise_type:
                continue
            
            # 难度筛选
            if difficulty_level and exercise.difficulty_level != difficulty_level:
                continue
            
            # 时长筛选
            if max_duration and exercise.duration_minutes > max_duration:
                continue
            
            # 器材筛选
            if equipment_available is not None:
                if exercise.equipment_needed and not all(
                    equipment in equipment_available for equipment in exercise.equipment_needed
                ):
                    continue
            
            filtered_exercises.append(exercise)
        
        return filtered_exercises

class PlanGenerator:
    """计划生成器"""
    
    def __init__(self, exercise_library: ExerciseLibrary):
        self.exercise_library = exercise_library
        self.plan_templates = {}
        self._load_plan_templates()
    
    def _load_plan_templates(self):
        """加载计划模板"""
        # 骨科康复模板
        self.plan_templates[RehabilitationType.ORTHOPEDIC_REHAB] = {
            "phases": [
                {
                    "name": "急性期",
                    "duration_weeks": 2,
                    "focus": ["疼痛控制", "炎症减轻"],
                    "exercise_types": [ExerciseType.FLEXIBILITY, ExerciseType.BREATHING],
                    "intensity": "low"
                },
                {
                    "name": "亚急性期",
                    "duration_weeks": 4,
                    "focus": ["活动度恢复", "轻度力量训练"],
                    "exercise_types": [ExerciseType.RANGE_OF_MOTION, ExerciseType.STRENGTH_TRAINING],
                    "intensity": "moderate"
                },
                {
                    "name": "功能恢复期",
                    "duration_weeks": 6,
                    "focus": ["力量恢复", "功能训练"],
                    "exercise_types": [ExerciseType.STRENGTH_TRAINING, ExerciseType.FUNCTIONAL],
                    "intensity": "high"
                }
            ]
        }
        
        # 神经康复模板
        self.plan_templates[RehabilitationType.NEUROLOGICAL_REHAB] = {
            "phases": [
                {
                    "name": "早期康复",
                    "duration_weeks": 4,
                    "focus": ["基础功能", "平衡训练"],
                    "exercise_types": [ExerciseType.BALANCE, ExerciseType.COORDINATION],
                    "intensity": "low"
                },
                {
                    "name": "中期康复",
                    "duration_weeks": 8,
                    "focus": ["功能改善", "技能训练"],
                    "exercise_types": [ExerciseType.FUNCTIONAL, ExerciseType.COGNITIVE],
                    "intensity": "moderate"
                },
                {
                    "name": "后期康复",
                    "duration_weeks": 12,
                    "focus": ["独立生活", "社会参与"],
                    "exercise_types": [ExerciseType.FUNCTIONAL, ExerciseType.ENDURANCE],
                    "intensity": "high"
                }
            ]
        }
        
        # 中医康复模板
        self.plan_templates[RehabilitationType.TCM_REHAB] = {
            "phases": [
                {
                    "name": "调理期",
                    "duration_weeks": 4,
                    "focus": ["气血调和", "经络疏通"],
                    "exercise_types": [ExerciseType.BREATHING, ExerciseType.FLEXIBILITY],
                    "intensity": "low"
                },
                {
                    "name": "强化期",
                    "duration_weeks": 6,
                    "focus": ["体质增强", "功能改善"],
                    "exercise_types": [ExerciseType.COORDINATION, ExerciseType.BALANCE],
                    "intensity": "moderate"
                },
                {
                    "name": "巩固期",
                    "duration_weeks": 8,
                    "focus": ["功能巩固", "预防复发"],
                    "exercise_types": [ExerciseType.ENDURANCE, ExerciseType.FUNCTIONAL],
                    "intensity": "moderate"
                }
            ]
        }
    
    async def generate_personalized_plan(
        self,
        user_id: str,
        rehabilitation_type: RehabilitationType,
        initial_assessment: FunctionalAssessment,
        goals: List[RehabilitationGoal],
        constraints: Dict[str, Any] = None
    ) -> RehabilitationPlan:
        """生成个性化康复计划"""
        try:
            # 获取计划模板
            template = self.plan_templates.get(rehabilitation_type)
            if not template:
                raise ValueError(f"不支持的康复类型: {rehabilitation_type}")
            
            # 计算总时长
            total_weeks = sum(phase["duration_weeks"] for phase in template["phases"])
            
            # 根据评估结果调整计划
            adjusted_template = await self._adjust_plan_based_on_assessment(
                template, initial_assessment, constraints
            )
            
            # 创建康复计划
            plan = RehabilitationPlan(
                id=f"plan_{user_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                name=f"{rehabilitation_type.value}康复计划",
                description=f"基于初始评估的个性化{rehabilitation_type.value}康复计划",
                rehabilitation_type=rehabilitation_type,
                goals=goals,
                total_duration_weeks=total_weeks,
                sessions_per_week=self._calculate_session_frequency(initial_assessment),
                session_duration_minutes=self._calculate_session_duration(initial_assessment),
                difficulty_progression=True
            )
            
            return plan
            
        except Exception as e:
            logger.error(f"生成康复计划失败: {e}")
            raise
    
    async def _adjust_plan_based_on_assessment(
        self,
        template: Dict[str, Any],
        assessment: FunctionalAssessment,
        constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """根据评估结果调整计划"""
        adjusted_template = template.copy()
        
        # 根据疼痛水平调整
        if assessment.pain_level and assessment.pain_level > 7:
            # 高疼痛水平，延长急性期
            for phase in adjusted_template["phases"]:
                if "急性" in phase["name"] or "early" in phase["name"].lower():
                    phase["duration_weeks"] += 1
        
        # 根据功能评分调整
        if assessment.overall_function_score and assessment.overall_function_score < 0.3:
            # 功能严重受限，增加基础训练时间
            for phase in adjusted_template["phases"]:
                if phase["intensity"] == "low":
                    phase["duration_weeks"] += 2
        
        # 根据年龄调整（如果有约束条件）
        if constraints and "age" in constraints:
            age = constraints["age"]
            if age > 65:
                # 老年人，降低强度，延长时间
                for phase in adjusted_template["phases"]:
                    if phase["intensity"] == "high":
                        phase["intensity"] = "moderate"
                        phase["duration_weeks"] += 2
        
        return adjusted_template
    
    def _calculate_session_frequency(self, assessment: FunctionalAssessment) -> int:
        """计算训练频率"""
        base_frequency = 3  # 每周3次
        
        # 根据功能评分调整
        if assessment.overall_function_score:
            if assessment.overall_function_score < 0.3:
                return 2  # 功能严重受限，减少频率
            elif assessment.overall_function_score > 0.7:
                return 4  # 功能较好，可以增加频率
        
        # 根据疼痛水平调整
        if assessment.pain_level:
            if assessment.pain_level > 7:
                return 2  # 高疼痛，减少频率
            elif assessment.pain_level < 3:
                return 4  # 低疼痛，可以增加频率
        
        return base_frequency
    
    def _calculate_session_duration(self, assessment: FunctionalAssessment) -> int:
        """计算单次训练时长"""
        base_duration = 45  # 45分钟
        
        # 根据耐力评分调整
        if assessment.endurance_score:
            if assessment.endurance_score < 0.3:
                return 30  # 耐力差，缩短时间
            elif assessment.endurance_score > 0.7:
                return 60  # 耐力好，可以延长
        
        # 根据年龄调整（通过元数据获取）
        if "age" in assessment.metadata:
            age = assessment.metadata["age"]
            if age > 65:
                return 30  # 老年人，缩短时间
            elif age < 30:
                return 60  # 年轻人，可以延长
        
        return base_duration

class ProgressTracker:
    """进度跟踪器"""
    
    def __init__(self):
        self.progress_data = {}
        self.prediction_models = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """初始化预测模型"""
        self.prediction_models = {
            "completion_predictor": RandomForestRegressor(n_estimators=100, random_state=42),
            "success_predictor": RandomForestRegressor(n_estimators=100, random_state=42)
        }
    
    async def track_session_progress(
        self,
        session: TrainingSession,
        user_id: str
    ) -> Dict[str, Any]:
        """跟踪训练会话进度"""
        try:
            # 计算会话完成度
            completion_rate = len(session.completed_exercises) / len(session.exercises) if session.exercises else 0
            
            # 计算训练效果指标
            effectiveness_metrics = await self._calculate_session_effectiveness(session)
            
            # 更新用户进度数据
            if user_id not in self.progress_data:
                self.progress_data[user_id] = {
                    "sessions": [],
                    "total_sessions": 0,
                    "completed_sessions": 0,
                    "average_completion_rate": 0.0,
                    "trend_analysis": {}
                }
            
            user_progress = self.progress_data[user_id]
            user_progress["sessions"].append({
                "session_id": session.id,
                "date": session.scheduled_date,
                "completion_rate": completion_rate,
                "effectiveness": effectiveness_metrics,
                "pain_change": self._calculate_pain_change(session),
                "satisfaction": session.satisfaction_score
            })
            
            user_progress["total_sessions"] += 1
            if completion_rate >= 0.8:  # 80%以上完成度视为完成
                user_progress["completed_sessions"] += 1
            
            # 更新平均完成率
            user_progress["average_completion_rate"] = (
                user_progress["completed_sessions"] / user_progress["total_sessions"]
            )
            
            # 趋势分析
            trend_analysis = await self._analyze_progress_trends(user_id)
            user_progress["trend_analysis"] = trend_analysis
            
            return {
                "session_completion_rate": completion_rate,
                "effectiveness_metrics": effectiveness_metrics,
                "overall_progress": user_progress["average_completion_rate"],
                "trend_analysis": trend_analysis,
                "recommendations": await self._generate_progress_recommendations(user_id, session)
            }
            
        except Exception as e:
            logger.error(f"跟踪训练进度失败: {e}")
            raise
    
    async def _calculate_session_effectiveness(self, session: TrainingSession) -> Dict[str, float]:
        """计算训练会话效果"""
        effectiveness = {}
        
        # 疼痛改善效果
        if session.pain_level_before is not None and session.pain_level_after is not None:
            pain_improvement = session.pain_level_before - session.pain_level_after
            effectiveness["pain_improvement"] = pain_improvement / 10.0  # 标准化到0-1
        
        # 完成度效果
        completion_rate = len(session.completed_exercises) / len(session.exercises) if session.exercises else 0
        effectiveness["completion_effectiveness"] = completion_rate
        
        # 满意度效果
        if session.satisfaction_score:
            effectiveness["satisfaction_effectiveness"] = session.satisfaction_score / 5.0  # 标准化到0-1
        
        # 疲劳控制效果（疲劳越低越好）
        if session.fatigue_level is not None:
            effectiveness["fatigue_control"] = 1.0 - (session.fatigue_level / 10.0)
        
        # 综合效果评分
        effectiveness["overall_effectiveness"] = np.mean(list(effectiveness.values()))
        
        return effectiveness
    
    def _calculate_pain_change(self, session: TrainingSession) -> Optional[float]:
        """计算疼痛变化"""
        if session.pain_level_before is not None and session.pain_level_after is not None:
            return session.pain_level_before - session.pain_level_after
        return None
    
    async def _analyze_progress_trends(self, user_id: str) -> Dict[str, Any]:
        """分析进度趋势"""
        if user_id not in self.progress_data:
            return {}
        
        user_sessions = self.progress_data[user_id]["sessions"]
        if len(user_sessions) < 3:  # 需要至少3次会话才能分析趋势
            return {"status": "insufficient_data"}
        
        # 提取时间序列数据
        dates = [session["date"] for session in user_sessions[-10:]]  # 最近10次
        completion_rates = [session["completion_rate"] for session in user_sessions[-10:]]
        effectiveness_scores = [
            session["effectiveness"].get("overall_effectiveness", 0) 
            for session in user_sessions[-10:]
        ]
        
        # 计算趋势
        completion_trend = np.polyfit(range(len(completion_rates)), completion_rates, 1)[0]
        effectiveness_trend = np.polyfit(range(len(effectiveness_scores)), effectiveness_scores, 1)[0]
        
        # 计算变异系数（稳定性指标）
        completion_stability = 1 - (np.std(completion_rates) / np.mean(completion_rates)) if np.mean(completion_rates) > 0 else 0
        
        return {
            "completion_trend": "improving" if completion_trend > 0.01 else "declining" if completion_trend < -0.01 else "stable",
            "effectiveness_trend": "improving" if effectiveness_trend > 0.01 else "declining" if effectiveness_trend < -0.01 else "stable",
            "stability_score": completion_stability,
            "recent_performance": {
                "average_completion": np.mean(completion_rates),
                "average_effectiveness": np.mean(effectiveness_scores)
            }
        }
    
    async def _generate_progress_recommendations(
        self,
        user_id: str,
        current_session: TrainingSession
    ) -> List[str]:
        """生成进度建议"""
        recommendations = []
        
        if user_id not in self.progress_data:
            return recommendations
        
        user_progress = self.progress_data[user_id]
        trend_analysis = user_progress.get("trend_analysis", {})
        
        # 基于完成率的建议
        avg_completion = user_progress["average_completion_rate"]
        if avg_completion < 0.6:
            recommendations.append("建议降低训练难度或减少训练量")
        elif avg_completion > 0.9:
            recommendations.append("可以考虑增加训练难度或训练量")
        
        # 基于趋势的建议
        if trend_analysis.get("completion_trend") == "declining":
            recommendations.append("注意到完成率下降趋势，建议调整训练计划")
        
        if trend_analysis.get("effectiveness_trend") == "declining":
            recommendations.append("训练效果有下降趋势，建议咨询治疗师")
        
        # 基于疼痛的建议
        if current_session.pain_level_after and current_session.pain_level_after > 6:
            recommendations.append("训练后疼痛较重，建议减少训练强度")
        
        # 基于疲劳的建议
        if current_session.fatigue_level and current_session.fatigue_level > 7:
            recommendations.append("疲劳程度较高，建议增加休息时间")
        
        # 基于满意度的建议
        if current_session.satisfaction_score and current_session.satisfaction_score < 3:
            recommendations.append("满意度较低，建议调整训练内容或方式")
        
        return recommendations
    
    async def predict_completion_time(
        self,
        user_id: str,
        plan: RehabilitationPlan
    ) -> Optional[datetime]:
        """预测完成时间"""
        if user_id not in self.progress_data:
            return None
        
        user_progress = self.progress_data[user_id]
        if user_progress["total_sessions"] < 5:  # 需要足够的历史数据
            return None
        
        # 计算平均进度速度
        avg_completion_rate = user_progress["average_completion_rate"]
        if avg_completion_rate <= 0:
            return None
        
        # 估算剩余时间
        total_planned_sessions = plan.total_duration_weeks * plan.sessions_per_week
        completed_sessions = user_progress["completed_sessions"]
        remaining_sessions = total_planned_sessions - completed_sessions
        
        # 考虑当前完成率，预测需要的实际会话数
        estimated_actual_sessions = remaining_sessions / avg_completion_rate
        
        # 计算预测完成日期
        days_per_session = 7 / plan.sessions_per_week
        estimated_days = estimated_actual_sessions * days_per_session
        
        predicted_date = datetime.now() + timedelta(days=estimated_days)
        return predicted_date
    
    async def calculate_success_probability(
        self,
        user_id: str,
        goals: List[RehabilitationGoal]
    ) -> float:
        """计算成功概率"""
        if user_id not in self.progress_data:
            return 0.5  # 默认概率
        
        user_progress = self.progress_data[user_id]
        
        # 基于历史表现计算成功概率
        factors = []
        
        # 完成率因子
        completion_factor = min(user_progress["average_completion_rate"] * 1.2, 1.0)
        factors.append(completion_factor)
        
        # 趋势因子
        trend_analysis = user_progress.get("trend_analysis", {})
        if trend_analysis.get("completion_trend") == "improving":
            trend_factor = 0.8
        elif trend_analysis.get("completion_trend") == "declining":
            trend_factor = 0.4
        else:
            trend_factor = 0.6
        factors.append(trend_factor)
        
        # 稳定性因子
        stability_score = trend_analysis.get("stability_score", 0.5)
        factors.append(stability_score)
        
        # 目标合理性因子（简化评估）
        achievable_goals = sum(1 for goal in goals if goal.progress_percentage > 0.1)
        goal_factor = achievable_goals / len(goals) if goals else 0.5
        factors.append(goal_factor)
        
        # 计算综合成功概率
        success_probability = np.mean(factors)
        return min(max(success_probability, 0.1), 0.95)  # 限制在10%-95%之间

class IntelligentRehabilitationTrainer:
    """智能康复训练引擎主类"""
    
    def __init__(self, config: Dict[str, Any], metrics_collector: Optional[MetricsCollector] = None):
        self.config = config
        self.metrics_collector = metrics_collector
        
        # 初始化组件
        self.exercise_library = ExerciseLibrary()
        self.plan_generator = PlanGenerator(self.exercise_library)
        self.progress_tracker = ProgressTracker()
        
        # 存储
        self.active_plans = {}
        self.assessments = {}
        self.training_sessions = {}
        
        logger.info("智能康复训练引擎初始化完成")
    
    async def initialize(self):
        """初始化引擎"""
        try:
            # 加载配置
            await self._load_configuration()
            
            # 初始化数据
            await self._initialize_data()
            
            logger.info("智能康复训练引擎初始化成功")
            
        except Exception as e:
            logger.error(f"智能康复训练引擎初始化失败: {e}")
            raise
    
    async def _load_configuration(self):
        """加载配置"""
        self.rehab_config = self.config.get("rehabilitation", {})
        self.max_session_duration = self.rehab_config.get("max_session_duration", 90)
        self.min_session_duration = self.rehab_config.get("min_session_duration", 15)
        self.default_plan_duration = self.rehab_config.get("default_plan_duration", 12)
        self.enable_ai_adjustment = self.rehab_config.get("enable_ai_adjustment", True)
    
    async def _initialize_data(self):
        """初始化数据"""
        # 这里可以从数据库加载历史数据
        pass
    
    @trace_operation("rehab_trainer.create_assessment", SpanKind.INTERNAL)
    async def create_functional_assessment(
        self,
        user_id: str,
        assessment_type: AssessmentType,
        assessment_data: Dict[str, Any],
        assessor: Optional[str] = None
    ) -> FunctionalAssessment:
        """创建功能评估"""
        try:
            assessment = FunctionalAssessment(
                id=f"assess_{user_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                assessment_type=assessment_type,
                assessment_date=datetime.now(),
                assessor=assessor,
                **assessment_data
            )
            
            # 计算整体功能评分
            assessment.overall_function_score = await self._calculate_overall_function_score(assessment)
            
            # 生成建议
            assessment.recommendations = await self._generate_assessment_recommendations(assessment)
            
            # 存储评估
            if user_id not in self.assessments:
                self.assessments[user_id] = []
            self.assessments[user_id].append(assessment)
            
            # 记录指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "assessments_created",
                    {"user_id": user_id, "assessment_type": assessment_type.value}
                )
            
            logger.info(f"功能评估已创建: {assessment.id}")
            return assessment
            
        except Exception as e:
            logger.error(f"创建功能评估失败: {e}")
            raise
    
    async def _calculate_overall_function_score(self, assessment: FunctionalAssessment) -> float:
        """计算整体功能评分"""
        scores = []
        
        # 关节活动度评分
        if assessment.range_of_motion:
            rom_scores = list(assessment.range_of_motion.values())
            if rom_scores:
                scores.append(np.mean(rom_scores))
        
        # 肌力评分
        if assessment.muscle_strength:
            strength_scores = list(assessment.muscle_strength.values())
            if strength_scores:
                scores.append(np.mean(strength_scores))
        
        # 平衡评分
        if assessment.balance_score is not None:
            scores.append(assessment.balance_score)
        
        # 协调评分
        if assessment.coordination_score is not None:
            scores.append(assessment.coordination_score)
        
        # 耐力评分
        if assessment.endurance_score is not None:
            scores.append(assessment.endurance_score)
        
        # 日常生活活动评分
        if assessment.activities_of_daily_living:
            adl_scores = list(assessment.activities_of_daily_living.values())
            if adl_scores:
                scores.append(np.mean(adl_scores))
        
        # 生活质量评分
        if assessment.quality_of_life_score is not None:
            scores.append(assessment.quality_of_life_score)
        
        # 疼痛影响（反向评分）
        if assessment.pain_level is not None:
            pain_impact = 1.0 - (assessment.pain_level / 10.0)
            scores.append(pain_impact)
        
        return np.mean(scores) if scores else 0.5
    
    async def _generate_assessment_recommendations(self, assessment: FunctionalAssessment) -> List[str]:
        """生成评估建议"""
        recommendations = []
        
        # 基于疼痛水平的建议
        if assessment.pain_level is not None:
            if assessment.pain_level > 7:
                recommendations.append("疼痛水平较高，建议先进行疼痛管理")
            elif assessment.pain_level < 3:
                recommendations.append("疼痛控制良好，可以进行积极的康复训练")
        
        # 基于功能评分的建议
        if assessment.overall_function_score is not None:
            if assessment.overall_function_score < 0.3:
                recommendations.append("功能严重受限，建议从基础训练开始")
            elif assessment.overall_function_score > 0.7:
                recommendations.append("功能状态良好，可以进行进阶训练")
        
        # 基于平衡能力的建议
        if assessment.balance_score is not None and assessment.balance_score < 0.5:
            recommendations.append("平衡能力需要改善，建议增加平衡训练")
        
        # 基于肌力的建议
        if assessment.muscle_strength:
            weak_muscles = [muscle for muscle, strength in assessment.muscle_strength.items() if strength < 0.5]
            if weak_muscles:
                recommendations.append(f"以下肌群需要加强: {', '.join(weak_muscles)}")
        
        # 基于心理状态的建议
        if assessment.motivation_level is not None and assessment.motivation_level < 3:
            recommendations.append("动机水平较低，建议心理支持和鼓励")
        
        if assessment.anxiety_level is not None and assessment.anxiety_level > 3:
            recommendations.append("焦虑水平较高，建议放松训练和心理疏导")
        
        return recommendations
    
    @trace_operation("rehab_trainer.create_plan", SpanKind.INTERNAL)
    async def create_rehabilitation_plan(
        self,
        user_id: str,
        rehabilitation_type: RehabilitationType,
        goals: List[RehabilitationGoal],
        initial_assessment: Optional[FunctionalAssessment] = None,
        constraints: Dict[str, Any] = None
    ) -> RehabilitationPlan:
        """创建康复计划"""
        try:
            # 如果没有初始评估，创建一个基础评估
            if not initial_assessment:
                initial_assessment = FunctionalAssessment(
                    id=f"basic_assess_{user_id}",
                    user_id=user_id,
                    assessment_type=AssessmentType.INITIAL,
                    assessment_date=datetime.now(),
                    overall_function_score=0.5  # 默认中等功能水平
                )
            
            # 生成个性化计划
            plan = await self.plan_generator.generate_personalized_plan(
                user_id, rehabilitation_type, initial_assessment, goals, constraints
            )
            
            # 存储计划
            self.active_plans[plan.id] = plan
            
            # 记录指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "rehabilitation_plans_created",
                    {"user_id": user_id, "rehabilitation_type": rehabilitation_type.value}
                )
            
            logger.info(f"康复计划已创建: {plan.id}")
            return plan
            
        except Exception as e:
            logger.error(f"创建康复计划失败: {e}")
            raise
    
    @trace_operation("rehab_trainer.generate_session", SpanKind.INTERNAL)
    async def generate_training_session(
        self,
        plan_id: str,
        session_date: datetime,
        user_preferences: Dict[str, Any] = None
    ) -> TrainingSession:
        """生成训练会话"""
        try:
            if plan_id not in self.active_plans:
                raise ValueError(f"康复计划不存在: {plan_id}")
            
            plan = self.active_plans[plan_id]
            
            # 确定当前阶段
            current_phase = await self._determine_current_phase(plan, session_date)
            
            # 选择适合的运动
            exercises = await self._select_session_exercises(plan, current_phase, user_preferences)
            
            # 创建训练会话
            session = TrainingSession(
                id=f"session_{plan.user_id}_{int(session_date.timestamp())}",
                user_id=plan.user_id,
                plan_id=plan_id,
                exercises=exercises,
                scheduled_date=session_date
            )
            
            # 存储会话
            self.training_sessions[session.id] = session
            
            # 记录指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "training_sessions_generated",
                    {"user_id": plan.user_id, "plan_id": plan_id}
                )
            
            logger.info(f"训练会话已生成: {session.id}")
            return session
            
        except Exception as e:
            logger.error(f"生成训练会话失败: {e}")
            raise
    
    async def _determine_current_phase(self, plan: RehabilitationPlan, session_date: datetime) -> Dict[str, Any]:
        """确定当前康复阶段"""
        if not plan.start_date:
            # 如果计划还没开始，返回第一阶段
            template = self.plan_generator.plan_templates.get(plan.rehabilitation_type)
            return template["phases"][0] if template else {}
        
        # 计算已经过的周数
        weeks_elapsed = (session_date - plan.start_date).days // 7
        
        # 获取计划模板
        template = self.plan_generator.plan_templates.get(plan.rehabilitation_type)
        if not template:
            return {}
        
        # 确定当前阶段
        cumulative_weeks = 0
        for phase in template["phases"]:
            cumulative_weeks += phase["duration_weeks"]
            if weeks_elapsed < cumulative_weeks:
                return phase
        
        # 如果超过了所有阶段，返回最后一个阶段
        return template["phases"][-1]
    
    async def _select_session_exercises(
        self,
        plan: RehabilitationPlan,
        current_phase: Dict[str, Any],
        user_preferences: Dict[str, Any] = None
    ) -> List[Exercise]:
        """选择会话运动"""
        selected_exercises = []
        
        # 获取当前阶段的运动类型
        exercise_types = current_phase.get("exercise_types", [])
        
        # 确定难度级别
        difficulty_level = self._map_intensity_to_difficulty(current_phase.get("intensity", "moderate"))
        
        # 为每种运动类型选择运动
        for exercise_type in exercise_types:
            type_exercises = await self.exercise_library.get_exercises_by_type(exercise_type)
            
            # 筛选适合的运动
            suitable_exercises = [
                ex for ex in type_exercises 
                if ex.difficulty_level == difficulty_level and 
                   ex.duration_minutes <= plan.session_duration_minutes // len(exercise_types)
            ]
            
            if suitable_exercises:
                # 选择一个运动（可以根据用户偏好进一步筛选）
                selected_exercise = suitable_exercises[0]  # 简化选择逻辑
                selected_exercises.append(selected_exercise)
        
        # 确保总时长不超过计划时长
        total_duration = sum(ex.duration_minutes for ex in selected_exercises)
        if total_duration > plan.session_duration_minutes:
            # 按比例缩减时长
            scale_factor = plan.session_duration_minutes / total_duration
            for exercise in selected_exercises:
                exercise.duration_minutes = int(exercise.duration_minutes * scale_factor)
        
        return selected_exercises
    
    def _map_intensity_to_difficulty(self, intensity: str) -> DifficultyLevel:
        """将强度映射到难度级别"""
        intensity_mapping = {
            "low": DifficultyLevel.BEGINNER,
            "moderate": DifficultyLevel.EASY,
            "high": DifficultyLevel.MODERATE
        }
        return intensity_mapping.get(intensity, DifficultyLevel.EASY)
    
    @trace_operation("rehab_trainer.record_session", SpanKind.INTERNAL)
    async def record_session_completion(
        self,
        session_id: str,
        completion_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """记录训练会话完成情况"""
        try:
            if session_id not in self.training_sessions:
                raise ValueError(f"训练会话不存在: {session_id}")
            
            session = self.training_sessions[session_id]
            
            # 更新会话数据
            session.actual_start_time = completion_data.get("start_time")
            session.actual_end_time = completion_data.get("end_time")
            session.completed_exercises = completion_data.get("completed_exercises", [])
            session.skipped_exercises = completion_data.get("skipped_exercises", [])
            session.modified_exercises = completion_data.get("modified_exercises", {})
            session.pain_level_before = completion_data.get("pain_level_before")
            session.pain_level_after = completion_data.get("pain_level_after")
            session.fatigue_level = completion_data.get("fatigue_level")
            session.satisfaction_score = completion_data.get("satisfaction_score")
            session.notes = completion_data.get("notes")
            session.status = ProgressStatus.COMPLETED
            
            # 跟踪进度
            progress_result = await self.progress_tracker.track_session_progress(session, session.user_id)
            
            # 更新计划进度
            await self._update_plan_progress(session.plan_id)
            
            # 记录指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "training_sessions_completed",
                    {"user_id": session.user_id, "plan_id": session.plan_id}
                )
                
                completion_rate = len(session.completed_exercises) / len(session.exercises) if session.exercises else 0
                self.metrics_collector.record_histogram(
                    "session_completion_rate",
                    completion_rate,
                    {"user_id": session.user_id}
                )
            
            logger.info(f"训练会话完成记录: {session_id}")
            return progress_result
            
        except Exception as e:
            logger.error(f"记录训练会话失败: {e}")
            raise
    
    async def _update_plan_progress(self, plan_id: str):
        """更新计划进度"""
        if plan_id not in self.active_plans:
            return
        
        plan = self.active_plans[plan_id]
        
        # 计算已完成的会话数
        completed_sessions = len([
            session for session in self.training_sessions.values()
            if session.plan_id == plan_id and session.status == ProgressStatus.COMPLETED
        ])
        
        # 计算总计划会话数
        total_sessions = plan.total_duration_weeks * plan.sessions_per_week
        
        # 更新进度百分比
        plan.progress_percentage = (completed_sessions / total_sessions) * 100 if total_sessions > 0 else 0
        
        # 更新目标进度
        for goal in plan.goals:
            # 这里可以根据具体的目标类型和评估结果更新目标进度
            # 简化实现：假设目标进度与计划进度相关
            goal.progress_percentage = min(plan.progress_percentage * 1.2, 100)
            if goal.progress_percentage >= 100:
                goal.achieved = True
                goal.achievement_date = datetime.now()
    
    async def get_user_progress_summary(self, user_id: str) -> Dict[str, Any]:
        """获取用户进度摘要"""
        try:
            # 获取用户的活跃计划
            user_plans = [plan for plan in self.active_plans.values() if plan.user_id == user_id]
            
            # 获取用户的训练会话
            user_sessions = [session for session in self.training_sessions.values() if session.user_id == user_id]
            
            # 获取用户的评估记录
            user_assessments = self.assessments.get(user_id, [])
            
            # 计算总体统计
            total_sessions = len(user_sessions)
            completed_sessions = len([s for s in user_sessions if s.status == ProgressStatus.COMPLETED])
            completion_rate = completed_sessions / total_sessions if total_sessions > 0 else 0
            
            # 计算平均满意度
            satisfaction_scores = [s.satisfaction_score for s in user_sessions if s.satisfaction_score is not None]
            avg_satisfaction = np.mean(satisfaction_scores) if satisfaction_scores else None
            
            # 获取最新评估
            latest_assessment = max(user_assessments, key=lambda x: x.assessment_date) if user_assessments else None
            
            # 获取进度趋势
            progress_trends = {}
            if user_id in self.progress_tracker.progress_data:
                progress_trends = self.progress_tracker.progress_data[user_id].get("trend_analysis", {})
            
            # 计算目标达成情况
            all_goals = []
            for plan in user_plans:
                all_goals.extend(plan.goals)
            
            achieved_goals = len([goal for goal in all_goals if goal.achieved])
            total_goals = len(all_goals)
            goal_achievement_rate = achieved_goals / total_goals if total_goals > 0 else 0
            
            return {
                "user_id": user_id,
                "active_plans": len(user_plans),
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "completion_rate": completion_rate,
                "average_satisfaction": avg_satisfaction,
                "goal_achievement_rate": goal_achievement_rate,
                "latest_assessment": {
                    "date": latest_assessment.assessment_date if latest_assessment else None,
                    "overall_score": latest_assessment.overall_function_score if latest_assessment else None
                },
                "progress_trends": progress_trends,
                "recommendations": await self._generate_user_recommendations(user_id)
            }
            
        except Exception as e:
            logger.error(f"获取用户进度摘要失败: {e}")
            return {}
    
    async def _generate_user_recommendations(self, user_id: str) -> List[str]:
        """生成用户建议"""
        recommendations = []
        
        # 基于进度数据生成建议
        if user_id in self.progress_tracker.progress_data:
            user_progress = self.progress_tracker.progress_data[user_id]
            
            # 基于完成率的建议
            if user_progress["average_completion_rate"] < 0.7:
                recommendations.append("建议提高训练的规律性和完成度")
            
            # 基于趋势的建议
            trend_analysis = user_progress.get("trend_analysis", {})
            if trend_analysis.get("completion_trend") == "declining":
                recommendations.append("注意到训练完成率有下降趋势，建议调整训练计划")
        
        # 基于最新评估的建议
        user_assessments = self.assessments.get(user_id, [])
        if user_assessments:
            latest_assessment = max(user_assessments, key=lambda x: x.assessment_date)
            recommendations.extend(latest_assessment.recommendations)
        
        return recommendations
    
    async def get_rehabilitation_statistics(self) -> Dict[str, Any]:
        """获取康复统计信息"""
        try:
            total_plans = len(self.active_plans)
            total_sessions = len(self.training_sessions)
            completed_sessions = len([s for s in self.training_sessions.values() if s.status == ProgressStatus.COMPLETED])
            
            # 康复类型分布
            rehab_type_distribution = {}
            for plan in self.active_plans.values():
                rehab_type = plan.rehabilitation_type.value
                rehab_type_distribution[rehab_type] = rehab_type_distribution.get(rehab_type, 0) + 1
            
            # 平均完成率
            completion_rates = []
            for user_id in self.progress_tracker.progress_data:
                user_data = self.progress_tracker.progress_data[user_id]
                completion_rates.append(user_data["average_completion_rate"])
            
            avg_completion_rate = np.mean(completion_rates) if completion_rates else 0
            
            # 满意度统计
            satisfaction_scores = [
                s.satisfaction_score for s in self.training_sessions.values() 
                if s.satisfaction_score is not None
            ]
            avg_satisfaction = np.mean(satisfaction_scores) if satisfaction_scores else None
            
            return {
                "total_plans": total_plans,
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "overall_completion_rate": completed_sessions / total_sessions if total_sessions > 0 else 0,
                "average_user_completion_rate": avg_completion_rate,
                "average_satisfaction": avg_satisfaction,
                "rehabilitation_type_distribution": rehab_type_distribution,
                "active_users": len(set(plan.user_id for plan in self.active_plans.values())),
                "total_assessments": sum(len(assessments) for assessments in self.assessments.values())
            }
            
        except Exception as e:
            logger.error(f"获取康复统计失败: {e}")
            return {}

def initialize_rehabilitation_trainer(
    config: Dict[str, Any],
    metrics_collector: Optional[MetricsCollector] = None
) -> IntelligentRehabilitationTrainer:
    """初始化智能康复训练引擎"""
    trainer = IntelligentRehabilitationTrainer(config, metrics_collector)
    return trainer

# 全局实例
_rehabilitation_trainer: Optional[IntelligentRehabilitationTrainer] = None

def get_rehabilitation_trainer() -> Optional[IntelligentRehabilitationTrainer]:
    """获取智能康复训练引擎实例"""
    return _rehabilitation_trainer 