"""
intelligent_rehabilitation_engine - 索克生活项目模块
"""

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger
from typing import Dict, List, Any, Optional, Tuple, Union, Set, Callable
import warnings

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能康复训练引擎 - 提供个性化康复训练方案
结合中医康复理念和现代康复医学，为用户制定科学的康复训练计划
"""

warnings.filterwarnings('ignore')


class RehabilitationType(str, Enum):
    """康复类型"""
    PHYSICAL_THERAPY = "physical_therapy"           # 物理治疗
    OCCUPATIONAL_THERAPY = "occupational_therapy"   # 作业治疗
    SPEECH_THERAPY = "speech_therapy"               # 言语治疗
    TCM_REHABILITATION = "tcm_rehabilitation"       # 中医康复
    SPORTS_REHABILITATION = "sports_rehabilitation" # 运动康复
    CARDIAC_REHABILITATION = "cardiac_rehabilitation" # 心脏康复
    NEUROLOGICAL_REHABILITATION = "neurological_rehabilitation" # 神经康复
    RESPIRATORY_REHABILITATION = "respiratory_rehabilitation" # 呼吸康复

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
    RELAXATION = "relaxation"                       # 放松训练
    TCM_QIGONG = "tcm_qigong"                      # 中医气功
    TCM_TAICHI = "tcm_taichi"                      # 中医太极
    TCM_MASSAGE = "tcm_massage"                    # 中医按摩

class DifficultyLevel(str, Enum):
    """难度级别"""
    BEGINNER = "beginner"           # 初级
    INTERMEDIATE = "intermediate"   # 中级
    ADVANCED = "advanced"           # 高级
    EXPERT = "expert"               # 专家级

class ProgressStatus(str, Enum):
    """进度状态"""
    NOT_STARTED = "not_started"     # 未开始
    IN_PROGRESS = "in_progress"     # 进行中
    COMPLETED = "completed"         # 已完成
    PAUSED = "paused"               # 暂停
    MODIFIED = "modified"           # 已修改
    DISCONTINUED = "discontinued"   # 已停止

class InjuryType(str, Enum):
    """损伤类型"""
    ACUTE_INJURY = "acute_injury"           # 急性损伤
    CHRONIC_INJURY = "chronic_injury"       # 慢性损伤
    POST_SURGICAL = "post_surgical"         # 术后康复
    NEUROLOGICAL = "neurological"           # 神经系统
    MUSCULOSKELETAL = "musculoskeletal"     # 肌肉骨骼
    CARDIOVASCULAR = "cardiovascular"       # 心血管
    RESPIRATORY = "respiratory"             # 呼吸系统
    METABOLIC = "metabolic"                 # 代谢性疾病

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
class PatientProfile:
    """患者档案"""
    user_id: str
    age: int
    gender: str
    height: float                           # 身高(cm)
    weight: float                           # 体重(kg)
    bmi: float = field(init=False)
    injury_type: InjuryType
    injury_description: str
    injury_date: datetime
    current_pain_level: int = 0             # 疼痛等级 (0-10)
    mobility_limitations: List[str] = field(default_factory=list)
    medical_conditions: List[str] = field(default_factory=list)
    medications: List[str] = field(default_factory=list)
    previous_injuries: List[str] = field(default_factory=list)
    fitness_level: str = "beginner"         # beginner, intermediate, advanced
    tcm_constitution: Optional[TCMConstitution] = None
    goals: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        self.bmi = self.weight / ((self.height / 100) ** 2)

@dataclass
class Exercise:
    """运动项目"""
    id: str
    name: str
    description: str
    exercise_type: ExerciseType
    difficulty_level: DifficultyLevel
    target_muscles: List[str] = field(default_factory=list)
    equipment_needed: List[str] = field(default_factory=list)
    duration_minutes: int = 10
    repetitions: Optional[int] = None
    sets: Optional[int] = None
    hold_time_seconds: Optional[int] = None
    rest_time_seconds: int = 30
    instructions: List[str] = field(default_factory=list)
    precautions: List[str] = field(default_factory=list)
    modifications: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    video_url: Optional[str] = None
    image_urls: List[str] = field(default_factory=list)
    tcm_meridians: List[str] = field(default_factory=list)  # 相关经络
    tcm_acupoints: List[str] = field(default_factory=list)  # 相关穴位

@dataclass
class RehabilitationSession:
    """康复训练课程"""
    id: str
    name: str
    description: str
    rehabilitation_type: RehabilitationType
    exercises: List[Exercise]
    total_duration_minutes: int = field(init=False)
    warm_up_exercises: List[Exercise] = field(default_factory=list)
    cool_down_exercises: List[Exercise] = field(default_factory=list)
    difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER
    target_goals: List[str] = field(default_factory=list)
    session_notes: Optional[str] = None
    
    def __post_init__(self):
        total_duration = sum(ex.duration_minutes for ex in self.exercises)
        total_duration += sum(ex.duration_minutes for ex in self.warm_up_exercises)
        total_duration += sum(ex.duration_minutes for ex in self.cool_down_exercises)
        self.total_duration_minutes = total_duration

@dataclass
class RehabilitationPlan:
    """康复计划"""
    id: str
    user_id: str
    name: str
    description: str
    rehabilitation_type: RehabilitationType
    start_date: datetime
    end_date: datetime
    sessions: List[RehabilitationSession]
    frequency_per_week: int = 3
    total_weeks: int = field(init=False)
    goals: List[str] = field(default_factory=list)
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    progress_metrics: List[str] = field(default_factory=list)
    created_by: str = "system"
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    notes: Optional[str] = None
    
    def __post_init__(self):
        self.total_weeks = (self.end_date - self.start_date).days // 7

@dataclass
class ProgressRecord:
    """进度记录"""
    id: str
    user_id: str
    plan_id: str
    session_id: str
    exercise_id: str
    completion_date: datetime
    completed: bool = True
    pain_level_before: int = 0              # 训练前疼痛等级
    pain_level_after: int = 0               # 训练后疼痛等级
    perceived_exertion: int = 5             # 主观疲劳度 (1-10)
    actual_repetitions: Optional[int] = None
    actual_sets: Optional[int] = None
    actual_duration_minutes: Optional[int] = None
    modifications_used: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    side_effects: List[str] = field(default_factory=list)
    satisfaction_rating: int = 5            # 满意度 (1-10)

@dataclass
class AssessmentResult:
    """评估结果"""
    user_id: str
    assessment_date: datetime
    functional_scores: Dict[str, float] = field(default_factory=dict)
    range_of_motion: Dict[str, float] = field(default_factory=dict)
    strength_measurements: Dict[str, float] = field(default_factory=dict)
    balance_scores: Dict[str, float] = field(default_factory=dict)
    pain_levels: Dict[str, int] = field(default_factory=dict)
    quality_of_life_score: float = 0.0
    functional_independence: float = 0.0
    overall_progress: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    next_assessment_date: Optional[datetime] = None

class ExerciseLibrary:
    """运动库"""
    
    def __init__(self):
        self.exercises = {}
        self._load_exercise_database()
    
    def _load_exercise_database(self):
        """加载运动数据库"""
        # 力量训练
        self.exercises["strength_001"] = Exercise(
            id="strength_001",
            name="墙壁俯卧撑",
            description="适合初学者的上肢力量训练",
            exercise_type=ExerciseType.STRENGTH_TRAINING,
            difficulty_level=DifficultyLevel.BEGINNER,
            target_muscles=["胸大肌", "三角肌前束", "肱三头肌"],
            equipment_needed=["墙壁"],
            duration_minutes=5,
            repetitions=10,
            sets=2,
            instructions=[
                "面向墙壁站立，距离约一臂长",
                "双手平放在墙上，与肩同宽",
                "身体向前倾斜，然后推回原位",
                "保持身体挺直，核心收紧"
            ],
            precautions=["避免过度前倾", "保持呼吸顺畅"],
            benefits=["增强上肢力量", "改善姿态", "提高核心稳定性"]
        )
        
        # 柔韧性训练
        self.exercises["flexibility_001"] = Exercise(
            id="flexibility_001",
            name="颈部拉伸",
            description="缓解颈部紧张和僵硬",
            exercise_type=ExerciseType.FLEXIBILITY,
            difficulty_level=DifficultyLevel.BEGINNER,
            target_muscles=["颈部肌群", "斜方肌"],
            equipment_needed=[],
            duration_minutes=3,
            hold_time_seconds=15,
            sets=3,
            instructions=[
                "坐直或站立，肩膀放松",
                "缓慢将头向右侧倾斜",
                "保持15秒，感受左侧颈部拉伸",
                "回到中间位置，重复另一侧"
            ],
            precautions=["动作要缓慢", "不要强迫拉伸"],
            benefits=["缓解颈部紧张", "改善颈部活动度", "减少头痛"]
        )
        
        # 平衡训练
        self.exercises["balance_001"] = Exercise(
            id="balance_001",
            name="单腿站立",
            description="基础平衡能力训练",
            exercise_type=ExerciseType.BALANCE,
            difficulty_level=DifficultyLevel.BEGINNER,
            target_muscles=["小腿肌群", "核心肌群", "臀部肌群"],
            equipment_needed=[],
            duration_minutes=2,
            hold_time_seconds=30,
            sets=3,
            instructions=[
                "双脚并拢站立",
                "抬起一只脚，保持平衡",
                "保持30秒，然后换腿",
                "可以扶墙或椅子辅助"
            ],
            precautions=["确保周围安全", "可以扶持物体"],
            benefits=["提高平衡能力", "增强本体感觉", "预防跌倒"]
        )
        
        # 中医气功
        self.exercises["qigong_001"] = Exercise(
            id="qigong_001",
            name="八段锦 - 双手托天理三焦",
            description="传统中医气功，调理三焦气机",
            exercise_type=ExerciseType.TCM_QIGONG,
            difficulty_level=DifficultyLevel.BEGINNER,
            target_muscles=["全身肌群"],
            equipment_needed=[],
            duration_minutes=5,
            repetitions=8,
            sets=1,
            instructions=[
                "自然站立，双脚与肩同宽",
                "双手在腹前交叉，掌心向上",
                "缓慢上举至头顶，掌心向上托天",
                "停顿片刻，缓慢放下至腹前"
            ],
            precautions=["动作要缓慢柔和", "配合呼吸"],
            benefits=["调理三焦", "疏通经络", "调和气血"],
            tcm_meridians=["三焦经", "任脉", "督脉"],
            tcm_acupoints=["百会", "膻中", "丹田"]
        )
        
        # 太极拳
        self.exercises["taichi_001"] = Exercise(
            id="taichi_001",
            name="太极起势",
            description="太极拳基础动作，调息养神",
            exercise_type=ExerciseType.TCM_TAICHI,
            difficulty_level=DifficultyLevel.BEGINNER,
            target_muscles=["全身肌群"],
            equipment_needed=[],
            duration_minutes=3,
            repetitions=5,
            sets=1,
            instructions=[
                "自然站立，双脚与肩同宽",
                "双臂自然下垂，全身放松",
                "缓慢抬起双臂至胸前",
                "掌心向下，缓慢下按至腹前"
            ],
            precautions=["心静体松", "呼吸自然"],
            benefits=["调和阴阳", "宁心安神", "强身健体"],
            tcm_meridians=["任脉", "督脉", "带脉"],
            tcm_acupoints=["百会", "印堂", "膻中", "丹田"]
        )
        
        # 呼吸训练
        self.exercises["breathing_001"] = Exercise(
            id="breathing_001",
            name="腹式呼吸",
            description="深度呼吸训练，改善肺功能",
            exercise_type=ExerciseType.BREATHING,
            difficulty_level=DifficultyLevel.BEGINNER,
            target_muscles=["膈肌", "腹肌"],
            equipment_needed=[],
            duration_minutes=5,
            repetitions=10,
            sets=1,
            instructions=[
                "舒适坐位或仰卧位",
                "一手放胸前，一手放腹部",
                "缓慢深吸气，腹部隆起",
                "缓慢呼气，腹部下沉"
            ],
            precautions=["不要过度用力", "保持放松"],
            benefits=["改善肺功能", "减少焦虑", "促进放松"]
        )

class RehabilitationPlanGenerator:
    """康复计划生成器"""
    
    def __init__(self):
        self.exercise_library = ExerciseLibrary()
        self.plan_templates = {}
        self._load_plan_templates()
    
    def _load_plan_templates(self):
        """加载计划模板"""
        # 术后康复模板
        self.plan_templates["post_surgical"] = {
            "phases": [
                {
                    "name": "急性期康复",
                    "duration_weeks": 2,
                    "focus": ["疼痛管理", "基础活动", "预防并发症"],
                    "exercise_types": [ExerciseType.BREATHING, ExerciseType.RANGE_OF_MOTION],
                    "intensity": "low"
                },
                {
                    "name": "亚急性期康复",
                    "duration_weeks": 4,
                    "focus": ["恢复活动度", "基础力量", "功能训练"],
                    "exercise_types": [ExerciseType.FLEXIBILITY, ExerciseType.STRENGTH_TRAINING, ExerciseType.FUNCTIONAL],
                    "intensity": "moderate"
                },
                {
                    "name": "功能恢复期",
                    "duration_weeks": 6,
                    "focus": ["力量提升", "功能恢复", "回归日常"],
                    "exercise_types": [ExerciseType.STRENGTH_TRAINING, ExerciseType.FUNCTIONAL, ExerciseType.ENDURANCE],
                    "intensity": "moderate_to_high"
                }
            ]
        }
        
        # 慢性疼痛康复模板
        self.plan_templates["chronic_pain"] = {
            "phases": [
                {
                    "name": "疼痛管理期",
                    "duration_weeks": 3,
                    "focus": ["疼痛缓解", "放松训练", "基础活动"],
                    "exercise_types": [ExerciseType.RELAXATION, ExerciseType.TCM_QIGONG, ExerciseType.FLEXIBILITY],
                    "intensity": "low"
                },
                {
                    "name": "功能改善期",
                    "duration_weeks": 6,
                    "focus": ["活动度改善", "力量恢复", "功能训练"],
                    "exercise_types": [ExerciseType.FLEXIBILITY, ExerciseType.STRENGTH_TRAINING, ExerciseType.FUNCTIONAL],
                    "intensity": "moderate"
                },
                {
                    "name": "维持期",
                    "duration_weeks": 12,
                    "focus": ["维持功能", "预防复发", "生活质量"],
                    "exercise_types": [ExerciseType.STRENGTH_TRAINING, ExerciseType.ENDURANCE, ExerciseType.TCM_TAICHI],
                    "intensity": "moderate"
                }
            ]
        }
        
        # 神经康复模板
        self.plan_templates["neurological"] = {
            "phases": [
                {
                    "name": "早期康复",
                    "duration_weeks": 4,
                    "focus": ["基础功能", "平衡训练", "协调性"],
                    "exercise_types": [ExerciseType.BALANCE, ExerciseType.COORDINATION, ExerciseType.RANGE_OF_MOTION],
                    "intensity": "low"
                },
                {
                    "name": "功能重建期",
                    "duration_weeks": 8,
                    "focus": ["运动控制", "功能训练", "日常活动"],
                    "exercise_types": [ExerciseType.FUNCTIONAL, ExerciseType.COORDINATION, ExerciseType.STRENGTH_TRAINING],
                    "intensity": "moderate"
                },
                {
                    "name": "功能优化期",
                    "duration_weeks": 12,
                    "focus": ["技能提升", "社会参与", "生活质量"],
                    "exercise_types": [ExerciseType.FUNCTIONAL, ExerciseType.ENDURANCE, ExerciseType.TCM_TAICHI],
                    "intensity": "moderate_to_high"
                }
            ]
        }
    
    async def generate_personalized_plan(
        self,
        patient_profile: PatientProfile,
        assessment_result: Optional[AssessmentResult] = None
    ) -> RehabilitationPlan:
        """生成个性化康复计划"""
        try:
            # 确定康复类型
            rehab_type = self._determine_rehabilitation_type(patient_profile)
            
            # 选择计划模板
            template = self._select_plan_template(patient_profile, rehab_type)
            
            # 生成康复计划
            plan = await self._create_rehabilitation_plan(
                patient_profile, 
                template, 
                rehab_type,
                assessment_result
            )
            
            # 中医体质调整
            if patient_profile.tcm_constitution:
                plan = await self._adjust_for_tcm_constitution(plan, patient_profile.tcm_constitution)
            
            logger.info(f"Generated rehabilitation plan for user {patient_profile.user_id}")
            return plan
            
        except Exception as e:
            logger.error(f"Error generating rehabilitation plan: {str(e)}")
            raise
    
    def _determine_rehabilitation_type(self, patient_profile: PatientProfile) -> RehabilitationType:
        """确定康复类型"""
        injury_type_mapping = {
            InjuryType.POST_SURGICAL: RehabilitationType.PHYSICAL_THERAPY,
            InjuryType.NEUROLOGICAL: RehabilitationType.NEUROLOGICAL_REHABILITATION,
            InjuryType.CARDIOVASCULAR: RehabilitationType.CARDIAC_REHABILITATION,
            InjuryType.RESPIRATORY: RehabilitationType.RESPIRATORY_REHABILITATION,
            InjuryType.MUSCULOSKELETAL: RehabilitationType.SPORTS_REHABILITATION,
            InjuryType.ACUTE_INJURY: RehabilitationType.SPORTS_REHABILITATION,
            InjuryType.CHRONIC_INJURY: RehabilitationType.PHYSICAL_THERAPY,
            InjuryType.METABOLIC: RehabilitationType.PHYSICAL_THERAPY
        }
        
        return injury_type_mapping.get(patient_profile.injury_type, RehabilitationType.PHYSICAL_THERAPY)
    
    def _select_plan_template(self, patient_profile: PatientProfile, rehab_type: RehabilitationType) -> Dict[str, Any]:
        """选择计划模板"""
        if patient_profile.injury_type == InjuryType.POST_SURGICAL:
            return self.plan_templates["post_surgical"]
        elif patient_profile.injury_type in [InjuryType.CHRONIC_INJURY, InjuryType.MUSCULOSKELETAL]:
            return self.plan_templates["chronic_pain"]
        elif patient_profile.injury_type == InjuryType.NEUROLOGICAL:
            return self.plan_templates["neurological"]
        else:
            return self.plan_templates["chronic_pain"]  # 默认模板
    
    async def _create_rehabilitation_plan(
        self,
        patient_profile: PatientProfile,
        template: Dict[str, Any],
        rehab_type: RehabilitationType,
        assessment_result: Optional[AssessmentResult] = None
    ) -> RehabilitationPlan:
        """创建康复计划"""
        plan_id = f"plan_{patient_profile.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 计算计划时长
        total_weeks = sum(phase["duration_weeks"] for phase in template["phases"])
        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=total_weeks)
        
        # 生成训练课程
        sessions = []
        current_week = 0
        
        for phase in template["phases"]:
            phase_sessions = await self._generate_phase_sessions(
                phase, 
                patient_profile, 
                current_week,
                assessment_result
            )
            sessions.extend(phase_sessions)
            current_week += phase["duration_weeks"]
        
        # 设定目标和里程碑
        goals = self._generate_goals(patient_profile, template)
        milestones = self._generate_milestones(template)
        
        plan = RehabilitationPlan(
            id=plan_id,
            user_id=patient_profile.user_id,
            name=f"{patient_profile.injury_description}康复计划",
            description=f"针对{patient_profile.injury_description}的个性化康复训练计划",
            rehabilitation_type=rehab_type,
            start_date=start_date,
            end_date=end_date,
            sessions=sessions,
            frequency_per_week=3,
            goals=goals,
            milestones=milestones,
            progress_metrics=["疼痛等级", "活动度", "力量", "功能评分", "生活质量"]
        )
        
        return plan
    
    async def _generate_phase_sessions(
        self,
        phase: Dict[str, Any],
        patient_profile: PatientProfile,
        start_week: int,
        assessment_result: Optional[AssessmentResult] = None
    ) -> List[RehabilitationSession]:
        """生成阶段训练课程"""
        sessions = []
        
        # 根据阶段生成不同的训练课程
        for week in range(phase["duration_weeks"]):
            for session_num in range(3):  # 每周3次
                session_id = f"session_{start_week + week}_{session_num}"
                
                # 选择适合的运动
                exercises = await self._select_exercises_for_session(
                    phase["exercise_types"],
                    patient_profile,
                    phase["intensity"],
                    assessment_result
                )
                
                session = RehabilitationSession(
                    id=session_id,
                    name=f"{phase['name']} - 第{week+1}周 课程{session_num+1}",
                    description=f"专注于{', '.join(phase['focus'])}",
                    rehabilitation_type=RehabilitationType.PHYSICAL_THERAPY,
                    exercises=exercises,
                    difficulty_level=self._get_difficulty_for_intensity(phase["intensity"]),
                    target_goals=phase["focus"]
                )
                
                sessions.append(session)
        
        return sessions
    
    async def _select_exercises_for_session(
        self,
        exercise_types: List[ExerciseType],
        patient_profile: PatientProfile,
        intensity: str,
        assessment_result: Optional[AssessmentResult] = None
    ) -> List[Exercise]:
        """为训练课程选择运动"""
        exercises = []
        
        # 从运动库中筛选合适的运动
        available_exercises = [
            ex for ex in self.exercise_library.exercises.values()
            if ex.exercise_type in exercise_types
        ]
        
        # 根据患者情况筛选
        suitable_exercises = []
        for exercise in available_exercises:
            if self._is_exercise_suitable(exercise, patient_profile, intensity):
                suitable_exercises.append(exercise)
        
        # 选择3-5个运动组成一个课程
        if len(suitable_exercises) >= 3:
            exercises = suitable_exercises[:5]
        else:
            exercises = suitable_exercises
        
        return exercises
    
    def _is_exercise_suitable(
        self,
        exercise: Exercise,
        patient_profile: PatientProfile,
        intensity: str
    ) -> bool:
        """判断运动是否适合患者"""
        # 检查禁忌症
        for contraindication in exercise.contraindications:
            if contraindication in patient_profile.contraindications:
                return False
        
        # 检查难度级别
        intensity_difficulty_mapping = {
            "low": [DifficultyLevel.BEGINNER],
            "moderate": [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE],
            "moderate_to_high": [DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED],
            "high": [DifficultyLevel.ADVANCED, DifficultyLevel.EXPERT]
        }
        
        if exercise.difficulty_level not in intensity_difficulty_mapping.get(intensity, []):
            return False
        
        # 检查患者健身水平
        fitness_difficulty_mapping = {
            "beginner": [DifficultyLevel.BEGINNER],
            "intermediate": [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE],
            "advanced": [DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED, DifficultyLevel.EXPERT]
        }
        
        if exercise.difficulty_level not in fitness_difficulty_mapping.get(patient_profile.fitness_level, []):
            return False
        
        return True
    
    def _get_difficulty_for_intensity(self, intensity: str) -> DifficultyLevel:
        """根据强度获取难度级别"""
        intensity_mapping = {
            "low": DifficultyLevel.BEGINNER,
            "moderate": DifficultyLevel.INTERMEDIATE,
            "moderate_to_high": DifficultyLevel.INTERMEDIATE,
            "high": DifficultyLevel.ADVANCED
        }
        return intensity_mapping.get(intensity, DifficultyLevel.BEGINNER)
    
    def _generate_goals(self, patient_profile: PatientProfile, template: Dict[str, Any]) -> List[str]:
        """生成康复目标"""
        goals = [
            "减轻疼痛和不适",
            "恢复正常活动度",
            "提高肌肉力量",
            "改善功能能力",
            "提高生活质量"
        ]
        
        # 根据损伤类型添加特定目标
        if patient_profile.injury_type == InjuryType.POST_SURGICAL:
            goals.extend(["促进伤口愈合", "预防并发症", "恢复术前功能"])
        elif patient_profile.injury_type == InjuryType.NEUROLOGICAL:
            goals.extend(["改善平衡和协调", "提高运动控制", "增强认知功能"])
        elif patient_profile.injury_type == InjuryType.CARDIOVASCULAR:
            goals.extend(["改善心肺功能", "控制血压", "提高运动耐力"])
        
        return goals
    
    def _generate_milestones(self, template: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成里程碑"""
        milestones = []
        current_week = 0
        
        for i, phase in enumerate(template["phases"]):
            milestone = {
                "week": current_week + phase["duration_weeks"],
                "phase": phase["name"],
                "targets": phase["focus"],
                "assessment_required": True
            }
            milestones.append(milestone)
            current_week += phase["duration_weeks"]
        
        return milestones
    
    async def _adjust_for_tcm_constitution(
        self,
        plan: RehabilitationPlan,
        constitution: TCMConstitution
    ) -> RehabilitationPlan:
        """根据中医体质调整康复计划"""
        # 根据不同体质添加相应的中医康复运动
        tcm_exercises = []
        
        if constitution == TCMConstitution.QI_DEFICIENCY:
            # 气虚质：补气养血
            tcm_exercises.extend(["qigong_001", "taichi_001"])
        elif constitution == TCMConstitution.YANG_DEFICIENCY:
            # 阳虚质：温阳补肾
            tcm_exercises.extend(["qigong_001"])
        elif constitution == TCMConstitution.YIN_DEFICIENCY:
            # 阴虚质：滋阴润燥
            tcm_exercises.extend(["taichi_001"])
        elif constitution == TCMConstitution.PHLEGM_DAMPNESS:
            # 痰湿质：化痰除湿
            tcm_exercises.extend(["qigong_001"])
        elif constitution == TCMConstitution.BLOOD_STASIS:
            # 血瘀质：活血化瘀
            tcm_exercises.extend(["taichi_001"])
        
        # 将中医运动添加到计划中
        for session in plan.sessions:
            for exercise_id in tcm_exercises:
                if exercise_id in self.exercise_library.exercises:
                    tcm_exercise = self.exercise_library.exercises[exercise_id]
                    if tcm_exercise not in session.exercises:
                        session.exercises.append(tcm_exercise)
        
        return plan

class ProgressTracker:
    """进度跟踪器"""
    
    def __init__(self):
        self.progress_records = {}
        self.assessment_history = {}
    
    async def record_session_completion(
        self,
        user_id: str,
        plan_id: str,
        session_id: str,
        exercise_completions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """记录训练课程完成情况"""
        try:
            completion_date = datetime.now()
            session_records = []
            
            for completion in exercise_completions:
                record = ProgressRecord(
                    id=f"record_{user_id}_{session_id}_{completion['exercise_id']}_{completion_date.strftime('%Y%m%d_%H%M%S')}",
                    user_id=user_id,
                    plan_id=plan_id,
                    session_id=session_id,
                    exercise_id=completion["exercise_id"],
                    completion_date=completion_date,
                    completed=completion.get("completed", True),
                    pain_level_before=completion.get("pain_level_before", 0),
                    pain_level_after=completion.get("pain_level_after", 0),
                    perceived_exertion=completion.get("perceived_exertion", 5),
                    actual_repetitions=completion.get("actual_repetitions"),
                    actual_sets=completion.get("actual_sets"),
                    actual_duration_minutes=completion.get("actual_duration_minutes"),
                    modifications_used=completion.get("modifications_used", []),
                    notes=completion.get("notes"),
                    side_effects=completion.get("side_effects", []),
                    satisfaction_rating=completion.get("satisfaction_rating", 5)
                )
                session_records.append(record)
            
            # 存储记录
            if user_id not in self.progress_records:
                self.progress_records[user_id] = []
            self.progress_records[user_id].extend(session_records)
            
            # 分析进度
            progress_analysis = await self._analyze_session_progress(session_records)
            
            logger.info(f"Recorded session completion for user {user_id}, session {session_id}")
            return {
                "status": "success",
                "records_count": len(session_records),
                "progress_analysis": progress_analysis
            }
            
        except Exception as e:
            logger.error(f"Error recording session completion: {str(e)}")
            raise
    
    async def _analyze_session_progress(self, records: List[ProgressRecord]) -> Dict[str, Any]:
        """分析训练课程进度"""
        if not records:
            return {}
        
        # 计算完成率
        completed_count = sum(1 for r in records if r.completed)
        completion_rate = completed_count / len(records) * 100
        
        # 计算平均疼痛变化
        pain_changes = []
        for record in records:
            if record.pain_level_before is not None and record.pain_level_after is not None:
                pain_changes.append(record.pain_level_before - record.pain_level_after)
        
        avg_pain_reduction = np.mean(pain_changes) if pain_changes else 0
        
        # 计算平均疲劳度
        avg_exertion = np.mean([r.perceived_exertion for r in records if r.perceived_exertion])
        
        # 计算平均满意度
        avg_satisfaction = np.mean([r.satisfaction_rating for r in records if r.satisfaction_rating])
        
        # 收集副作用
        all_side_effects = []
        for record in records:
            all_side_effects.extend(record.side_effects)
        
        return {
            "completion_rate": completion_rate,
            "average_pain_reduction": avg_pain_reduction,
            "average_exertion": avg_exertion,
            "average_satisfaction": avg_satisfaction,
            "side_effects": list(set(all_side_effects)),
            "recommendations": self._generate_session_recommendations(records)
        }
    
    def _generate_session_recommendations(self, records: List[ProgressRecord]) -> List[str]:
        """生成训练建议"""
        recommendations = []
        
        # 基于疼痛水平的建议
        high_pain_count = sum(1 for r in records if r.pain_level_after > 6)
        if high_pain_count > len(records) * 0.3:
            recommendations.append("建议降低训练强度，疼痛水平较高")
        
        # 基于疲劳度的建议
        avg_exertion = np.mean([r.perceived_exertion for r in records if r.perceived_exertion])
        if avg_exertion > 8:
            recommendations.append("训练强度可能过高，建议适当调整")
        elif avg_exertion < 4:
            recommendations.append("训练强度可以适当提高")
        
        # 基于完成率的建议
        completion_rate = sum(1 for r in records if r.completed) / len(records) * 100
        if completion_rate < 70:
            recommendations.append("完成率较低，建议调整训练计划或提供更多支持")
        
        # 基于满意度的建议
        avg_satisfaction = np.mean([r.satisfaction_rating for r in records if r.satisfaction_rating])
        if avg_satisfaction < 6:
            recommendations.append("满意度较低，建议了解具体原因并调整计划")
        
        return recommendations
    
    async def conduct_assessment(
        self,
        user_id: str,
        assessment_data: Dict[str, Any]
    ) -> AssessmentResult:
        """进行康复评估"""
        try:
            assessment_result = AssessmentResult(
                user_id=user_id,
                assessment_date=datetime.now(),
                functional_scores=assessment_data.get("functional_scores", {}),
                range_of_motion=assessment_data.get("range_of_motion", {}),
                strength_measurements=assessment_data.get("strength_measurements", {}),
                balance_scores=assessment_data.get("balance_scores", {}),
                pain_levels=assessment_data.get("pain_levels", {}),
                quality_of_life_score=assessment_data.get("quality_of_life_score", 0.0),
                functional_independence=assessment_data.get("functional_independence", 0.0)
            )
            
            # 计算总体进度
            assessment_result.overall_progress = await self._calculate_overall_progress(
                user_id, assessment_result
            )
            
            # 生成建议
            assessment_result.recommendations = await self._generate_assessment_recommendations(
                assessment_result
            )
            
            # 设定下次评估日期
            assessment_result.next_assessment_date = datetime.now() + timedelta(weeks=4)
            
            # 存储评估结果
            if user_id not in self.assessment_history:
                self.assessment_history[user_id] = []
            self.assessment_history[user_id].append(assessment_result)
            
            logger.info(f"Conducted assessment for user {user_id}")
            return assessment_result
            
        except Exception as e:
            logger.error(f"Error conducting assessment: {str(e)}")
            raise
    
    async def _calculate_overall_progress(
        self,
        user_id: str,
        current_assessment: AssessmentResult
    ) -> float:
        """计算总体进度"""
        # 如果没有历史评估，返回基础分数
        if user_id not in self.assessment_history or not self.assessment_history[user_id]:
            return 50.0  # 基础分数
        
        # 获取最近的评估
        previous_assessment = self.assessment_history[user_id][-1]
        
        # 计算各项指标的改善程度
        improvements = []
        
        # 功能评分改善
        for key in current_assessment.functional_scores:
            if key in previous_assessment.functional_scores:
                improvement = (
                    current_assessment.functional_scores[key] - 
                    previous_assessment.functional_scores[key]
                ) / previous_assessment.functional_scores[key] * 100
                improvements.append(improvement)
        
        # 疼痛水平改善（疼痛降低是好的）
        for key in current_assessment.pain_levels:
            if key in previous_assessment.pain_levels:
                improvement = (
                    previous_assessment.pain_levels[key] - 
                    current_assessment.pain_levels[key]
                ) / max(previous_assessment.pain_levels[key], 1) * 100
                improvements.append(improvement)
        
        # 生活质量改善
        if previous_assessment.quality_of_life_score > 0:
            qol_improvement = (
                current_assessment.quality_of_life_score - 
                previous_assessment.quality_of_life_score
            ) / previous_assessment.quality_of_life_score * 100
            improvements.append(qol_improvement)
        
        # 计算平均改善程度
        if improvements:
            avg_improvement = np.mean(improvements)
            # 将改善程度转换为0-100的进度分数
            progress = max(0, min(100, 50 + avg_improvement))
        else:
            progress = 50.0
        
        return progress
    
    async def _generate_assessment_recommendations(
        self,
        assessment_result: AssessmentResult
    ) -> List[str]:
        """生成评估建议"""
        recommendations = []
        
        # 基于疼痛水平的建议
        avg_pain = np.mean(list(assessment_result.pain_levels.values())) if assessment_result.pain_levels else 0
        if avg_pain > 7:
            recommendations.append("疼痛水平较高，建议调整训练强度并考虑疼痛管理策略")
        elif avg_pain < 3:
            recommendations.append("疼痛控制良好，可以考虑适当增加训练强度")
        
        # 基于功能评分的建议
        if assessment_result.functional_scores:
            avg_functional = np.mean(list(assessment_result.functional_scores.values()))
            if avg_functional < 60:
                recommendations.append("功能评分较低，建议加强功能性训练")
            elif avg_functional > 85:
                recommendations.append("功能恢复良好，可以考虑进入维持期训练")
        
        # 基于生活质量的建议
        if assessment_result.quality_of_life_score < 60:
            recommendations.append("生活质量有待提高，建议关注心理健康和社会支持")
        
        # 基于总体进度的建议
        if assessment_result.overall_progress < 40:
            recommendations.append("康复进度较慢，建议重新评估训练计划")
        elif assessment_result.overall_progress > 80:
            recommendations.append("康复进度良好，继续保持当前训练计划")
        
        return recommendations
    
    async def get_progress_summary(self, user_id: str) -> Dict[str, Any]:
        """获取进度总结"""
        try:
            # 获取训练记录
            user_records = self.progress_records.get(user_id, [])
            
            # 获取评估历史
            user_assessments = self.assessment_history.get(user_id, [])
            
            if not user_records and not user_assessments:
                return {"message": "暂无进度数据"}
            
            # 计算训练统计
            training_stats = await self._calculate_training_statistics(user_records)
            
            # 计算评估趋势
            assessment_trends = await self._calculate_assessment_trends(user_assessments)
            
            # 生成总体建议
            overall_recommendations = await self._generate_overall_recommendations(
                training_stats, assessment_trends
            )
            
            return {
                "user_id": user_id,
                "training_statistics": training_stats,
                "assessment_trends": assessment_trends,
                "overall_recommendations": overall_recommendations,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting progress summary: {str(e)}")
            raise
    
    async def _calculate_training_statistics(self, records: List[ProgressRecord]) -> Dict[str, Any]:
        """计算训练统计"""
        if not records:
            return {}
        
        # 按日期排序
        sorted_records = sorted(records, key=lambda x: x.completion_date)
        
        # 计算总体统计
        total_sessions = len(set(r.session_id for r in records))
        total_exercises = len(records)
        completed_exercises = sum(1 for r in records if r.completed)
        completion_rate = completed_exercises / total_exercises * 100 if total_exercises > 0 else 0
        
        # 计算疼痛趋势
        pain_data = [(r.completion_date, r.pain_level_after) for r in records if r.pain_level_after is not None]
        pain_trend = "stable"
        if len(pain_data) >= 2:
            recent_pain = np.mean([p[1] for p in pain_data[-5:]])  # 最近5次
            early_pain = np.mean([p[1] for p in pain_data[:5]])    # 最早5次
            if recent_pain < early_pain - 1:
                pain_trend = "improving"
            elif recent_pain > early_pain + 1:
                pain_trend = "worsening"
        
        # 计算满意度趋势
        satisfaction_data = [r.satisfaction_rating for r in records if r.satisfaction_rating is not None]
        avg_satisfaction = np.mean(satisfaction_data) if satisfaction_data else 0
        
        return {
            "total_sessions": total_sessions,
            "total_exercises": total_exercises,
            "completion_rate": completion_rate,
            "pain_trend": pain_trend,
            "average_satisfaction": avg_satisfaction,
            "training_period_days": (sorted_records[-1].completion_date - sorted_records[0].completion_date).days if len(sorted_records) > 1 else 0
        }
    
    async def _calculate_assessment_trends(self, assessments: List[AssessmentResult]) -> Dict[str, Any]:
        """计算评估趋势"""
        if len(assessments) < 2:
            return {"message": "需要至少2次评估才能分析趋势"}
        
        # 按日期排序
        sorted_assessments = sorted(assessments, key=lambda x: x.assessment_date)
        
        # 计算进度趋势
        progress_values = [a.overall_progress for a in sorted_assessments]
        progress_trend = "stable"
        if len(progress_values) >= 2:
            if progress_values[-1] > progress_values[0] + 10:
                progress_trend = "improving"
            elif progress_values[-1] < progress_values[0] - 10:
                progress_trend = "declining"
        
        # 计算生活质量趋势
        qol_values = [a.quality_of_life_score for a in sorted_assessments]
        qol_trend = "stable"
        if len(qol_values) >= 2:
            if qol_values[-1] > qol_values[0] + 10:
                qol_trend = "improving"
            elif qol_values[-1] < qol_values[0] - 10:
                qol_trend = "declining"
        
        return {
            "progress_trend": progress_trend,
            "quality_of_life_trend": qol_trend,
            "latest_progress": progress_values[-1] if progress_values else 0,
            "latest_qol_score": qol_values[-1] if qol_values else 0,
            "assessment_count": len(assessments)
        }
    
    async def _generate_overall_recommendations(
        self,
        training_stats: Dict[str, Any],
        assessment_trends: Dict[str, Any]
    ) -> List[str]:
        """生成总体建议"""
        recommendations = []
        
        # 基于完成率的建议
        completion_rate = training_stats.get("completion_rate", 0)
        if completion_rate < 70:
            recommendations.append("训练完成率较低，建议调整训练计划或寻求更多支持")
        elif completion_rate > 90:
            recommendations.append("训练完成率很高，保持良好的训练习惯")
        
        # 基于疼痛趋势的建议
        pain_trend = training_stats.get("pain_trend", "stable")
        if pain_trend == "worsening":
            recommendations.append("疼痛有恶化趋势，建议咨询医疗专业人员")
        elif pain_trend == "improving":
            recommendations.append("疼痛有改善趋势，继续当前的康复计划")
        
        # 基于进度趋势的建议
        progress_trend = assessment_trends.get("progress_trend", "stable")
        if progress_trend == "declining":
            recommendations.append("康复进度有下降趋势，建议重新评估康复策略")
        elif progress_trend == "improving":
            recommendations.append("康复进度良好，继续保持当前的康复计划")
        
        # 基于满意度的建议
        avg_satisfaction = training_stats.get("average_satisfaction", 0)
        if avg_satisfaction < 6:
            recommendations.append("训练满意度较低，建议了解具体问题并调整计划")
        
        return recommendations

class IntelligentRehabilitationEngine:
    """智能康复训练引擎"""
    
    def __init__(self, config: Dict[str, Any], metrics_collector: Optional[MetricsCollector] = None):
        self.config = config
        self.metrics_collector = metrics_collector
        self.plan_generator = RehabilitationPlanGenerator()
        self.progress_tracker = ProgressTracker()
        self.patient_profiles = {}
        self.active_plans = {}
        self.is_initialized = False
    
    async def initialize(self):
        """初始化康复引擎"""
        try:
            await self._load_configuration()
            await self._initialize_components()
            self.is_initialized = True
            logger.info("Intelligent rehabilitation engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing rehabilitation engine: {str(e)}")
            raise
    
    async def _load_configuration(self):
        """加载配置"""
        self.max_plan_duration_weeks = self.config.get("max_plan_duration_weeks", 24)
        self.default_frequency_per_week = self.config.get("default_frequency_per_week", 3)
        self.assessment_interval_weeks = self.config.get("assessment_interval_weeks", 4)
        self.enable_tcm_integration = self.config.get("enable_tcm_integration", True)
    
    async def _initialize_components(self):
        """初始化组件"""
        # 初始化计划生成器
        if hasattr(self.plan_generator, 'initialize'):
            await self.plan_generator.initialize()
        
        # 初始化进度跟踪器
        if hasattr(self.progress_tracker, 'initialize'):
            await self.progress_tracker.initialize()
    
    @trace_operation("rehabilitation_engine.create_patient_profile", SpanKind.INTERNAL)
    async def create_patient_profile(
        self,
        user_id: str,
        profile_data: Dict[str, Any]
    ) -> PatientProfile:
        """创建患者档案"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # 创建患者档案
            profile = PatientProfile(
                user_id=user_id,
                age=profile_data["age"],
                gender=profile_data["gender"],
                height=profile_data["height"],
                weight=profile_data["weight"],
                injury_type=InjuryType(profile_data["injury_type"]),
                injury_description=profile_data["injury_description"],
                injury_date=datetime.fromisoformat(profile_data["injury_date"]),
                current_pain_level=profile_data.get("current_pain_level", 0),
                mobility_limitations=profile_data.get("mobility_limitations", []),
                medical_conditions=profile_data.get("medical_conditions", []),
                medications=profile_data.get("medications", []),
                previous_injuries=profile_data.get("previous_injuries", []),
                fitness_level=profile_data.get("fitness_level", "beginner"),
                tcm_constitution=TCMConstitution(profile_data["tcm_constitution"]) if profile_data.get("tcm_constitution") else None,
                goals=profile_data.get("goals", []),
                contraindications=profile_data.get("contraindications", [])
            )
            
            # 存储档案
            self.patient_profiles[user_id] = profile
            
            # 记录指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "rehabilitation_patient_profiles_created",
                    {"injury_type": profile.injury_type.value}
                )
            
            logger.info(f"Created patient profile for user {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error creating patient profile: {str(e)}")
            raise
    
    @trace_operation("rehabilitation_engine.generate_plan", SpanKind.INTERNAL)
    async def generate_rehabilitation_plan(
        self,
        user_id: str,
        assessment_result: Optional[AssessmentResult] = None
    ) -> RehabilitationPlan:
        """生成康复计划"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # 获取患者档案
            if user_id not in self.patient_profiles:
                raise ValueError(f"Patient profile not found for user {user_id}")
            
            patient_profile = self.patient_profiles[user_id]
            
            # 生成个性化康复计划
            plan = await self.plan_generator.generate_personalized_plan(
                patient_profile, assessment_result
            )
            
            # 存储活动计划
            self.active_plans[user_id] = plan
            
            # 记录指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "rehabilitation_plans_generated",
                    {
                        "rehabilitation_type": plan.rehabilitation_type.value,
                        "total_weeks": str(plan.total_weeks)
                    }
                )
            
            logger.info(f"Generated rehabilitation plan for user {user_id}")
            return plan
            
        except Exception as e:
            logger.error(f"Error generating rehabilitation plan: {str(e)}")
            raise
    
    @trace_operation("rehabilitation_engine.record_session", SpanKind.INTERNAL)
    async def record_training_session(
        self,
        user_id: str,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """记录训练课程"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # 获取活动计划
            if user_id not in self.active_plans:
                raise ValueError(f"No active rehabilitation plan found for user {user_id}")
            
            plan = self.active_plans[user_id]
            
            # 记录课程完成情况
            result = await self.progress_tracker.record_session_completion(
                user_id=user_id,
                plan_id=plan.id,
                session_id=session_data["session_id"],
                exercise_completions=session_data["exercise_completions"]
            )
            
            # 记录指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "rehabilitation_sessions_completed",
                    {"user_id": user_id}
                )
                
                # 记录完成率
                completion_rate = result["progress_analysis"].get("completion_rate", 0)
                self.metrics_collector.record_histogram(
                    "rehabilitation_session_completion_rate",
                    completion_rate,
                    {"user_id": user_id}
                )
            
            logger.info(f"Recorded training session for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error recording training session: {str(e)}")
            raise
    
    @trace_operation("rehabilitation_engine.conduct_assessment", SpanKind.INTERNAL)
    async def conduct_assessment(
        self,
        user_id: str,
        assessment_data: Dict[str, Any]
    ) -> AssessmentResult:
        """进行康复评估"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # 进行评估
            assessment_result = await self.progress_tracker.conduct_assessment(
                user_id, assessment_data
            )
            
            # 记录指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "rehabilitation_assessments_conducted",
                    {"user_id": user_id}
                )
                
                # 记录进度分数
                self.metrics_collector.record_histogram(
                    "rehabilitation_progress_score",
                    assessment_result.overall_progress,
                    {"user_id": user_id}
                )
            
            logger.info(f"Conducted assessment for user {user_id}")
            return assessment_result
            
        except Exception as e:
            logger.error(f"Error conducting assessment: {str(e)}")
            raise
    
    async def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """获取用户进度"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            progress_summary = await self.progress_tracker.get_progress_summary(user_id)
            
            # 添加当前计划信息
            if user_id in self.active_plans:
                plan = self.active_plans[user_id]
                progress_summary["current_plan"] = {
                    "id": plan.id,
                    "name": plan.name,
                    "rehabilitation_type": plan.rehabilitation_type.value,
                    "start_date": plan.start_date.isoformat(),
                    "end_date": plan.end_date.isoformat(),
                    "total_weeks": plan.total_weeks,
                    "status": plan.status.value
                }
            
            return progress_summary
            
        except Exception as e:
            logger.error(f"Error getting user progress: {str(e)}")
            raise
    
    async def get_next_session(self, user_id: str) -> Optional[RehabilitationSession]:
        """获取下一个训练课程"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # 获取活动计划
            if user_id not in self.active_plans:
                return None
            
            plan = self.active_plans[user_id]
            
            # 获取已完成的课程
            user_records = self.progress_tracker.progress_records.get(user_id, [])
            completed_sessions = set(r.session_id for r in user_records)
            
            # 找到下一个未完成的课程
            for session in plan.sessions:
                if session.id not in completed_sessions:
                    return session
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting next session: {str(e)}")
            raise
    
    async def update_plan(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> RehabilitationPlan:
        """更新康复计划"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # 获取当前计划
            if user_id not in self.active_plans:
                raise ValueError(f"No active rehabilitation plan found for user {user_id}")
            
            plan = self.active_plans[user_id]
            
            # 应用更新
            if "frequency_per_week" in updates:
                plan.frequency_per_week = updates["frequency_per_week"]
            
            if "end_date" in updates:
                plan.end_date = datetime.fromisoformat(updates["end_date"])
                plan.total_weeks = (plan.end_date - plan.start_date).days // 7
            
            if "status" in updates:
                plan.status = ProgressStatus(updates["status"])
            
            if "notes" in updates:
                plan.notes = updates["notes"]
            
            # 记录指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "rehabilitation_plans_updated",
                    {"user_id": user_id}
                )
            
            logger.info(f"Updated rehabilitation plan for user {user_id}")
            return plan
            
        except Exception as e:
            logger.error(f"Error updating plan: {str(e)}")
            raise
    
    async def get_rehabilitation_statistics(self) -> Dict[str, Any]:
        """获取康复统计信息"""
        try:
            total_patients = len(self.patient_profiles)
            active_plans = len(self.active_plans)
            
            # 统计损伤类型分布
            injury_type_counts = {}
            for profile in self.patient_profiles.values():
                injury_type = profile.injury_type.value
                injury_type_counts[injury_type] = injury_type_counts.get(injury_type, 0) + 1
            
            # 统计康复类型分布
            rehab_type_counts = {}
            for plan in self.active_plans.values():
                rehab_type = plan.rehabilitation_type.value
                rehab_type_counts[rehab_type] = rehab_type_counts.get(rehab_type, 0) + 1
            
            # 统计中医体质分布
            tcm_constitution_counts = {}
            for profile in self.patient_profiles.values():
                if profile.tcm_constitution:
                    constitution = profile.tcm_constitution.value
                    tcm_constitution_counts[constitution] = tcm_constitution_counts.get(constitution, 0) + 1
            
            return {
                "total_patients": total_patients,
                "active_plans": active_plans,
                "injury_type_distribution": injury_type_counts,
                "rehabilitation_type_distribution": rehab_type_counts,
                "tcm_constitution_distribution": tcm_constitution_counts,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting rehabilitation statistics: {str(e)}")
            raise

def initialize_rehabilitation_engine(
    config: Dict[str, Any],
    metrics_collector: Optional[MetricsCollector] = None
) -> IntelligentRehabilitationEngine:
    """初始化智能康复训练引擎"""
    return IntelligentRehabilitationEngine(config, metrics_collector)

# 全局实例
_rehabilitation_engine = None

def get_rehabilitation_engine() -> Optional[IntelligentRehabilitationEngine]:
    """获取智能康复训练引擎实例"""
    return _rehabilitation_engine 