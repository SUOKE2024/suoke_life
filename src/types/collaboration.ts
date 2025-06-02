import { HealthContext } from './health';

/**
 * 任务优先级枚举
 */
export enum TaskPriority {
  LOW = 1,
  MEDIUM = 2,
  HIGH = 3,
  CRITICAL = 4
}

/**
 * 任务状态枚举
 */
export enum TaskStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

/**
 * 协作任务接口
 */
export interface CollaborationTask {
  id: string;
  healthContext: HealthContext;
  requiredCapabilities: string[];
  priority: TaskPriority;
  status: TaskStatus;
  createdAt: Date;
  updatedAt?: Date;
  completedAt?: Date;
  assignedAgents: string[];
  result: CollaborationResult | null;
  metadata?: Record<string, any>;
}

/**
 * 协作结果接口
 */
export interface CollaborationResult {
  analysis: AnalysisResult;
  diagnosis: DiagnosisResult;
  treatment: TreatmentResult;
  lifestyle: LifestyleResult;
  confidence: number;
  recommendations: string[];
  timestamp: Date;
}

/**
 * 分析结果接口
 */
export interface AnalysisResult {
  userInteraction: {
    symptoms: Symptom[];
    concerns: string[];
    duration: string;
  };
  healthAssessment: {
    constitution: ConstitutionType;
    vitalSigns: VitalSigns;
    riskFactors: string[];
    labResults?: LabResult[];
  };
  timestamp: Date;
}

/**
 * 诊断结果接口
 */
export interface DiagnosisResult {
  tcmDiagnosis: TCMDiagnosis;
  modernDiagnosis: ModernDiagnosis;
  seniorAdvice: SeniorAdvice;
  confidence: number;
}

/**
 * 中医诊断接口
 */
export interface TCMDiagnosis {
  syndrome: string; // 证候
  pattern: string; // 证型
  constitution: ConstitutionType; // 体质
  meridians: string[]; // 相关经络
  organs: string[]; // 相关脏腑
  pathogenesis: string; // 病机
  treatment_principle: string; // 治则
  confidence: number;
}

/**
 * 现代医学诊断接口
 */
export interface ModernDiagnosis {
  primary_diagnosis: string;
  differential_diagnosis: string[];
  icd_codes: string[];
  severity: 'mild' | 'moderate' | 'severe';
  prognosis: string;
  recommended_tests: string[];
  confidence: number;
}

/**
 * 资深建议接口
 */
export interface SeniorAdvice {
  clinical_experience: string;
  risk_assessment: string;
  treatment_modifications: string[];
  follow_up_recommendations: string[];
  confidence: number;
}

/**
 * 治疗结果接口
 */
export interface TreatmentResult {
  plan: TreatmentPlan;
  validation: TreatmentValidation;
  adjustments: string[];
}

/**
 * 治疗方案接口
 */
export interface TreatmentPlan {
  tcm_treatment: {
    herbal_formula: HerbalFormula;
    acupuncture_points: AcupuncturePoint[];
    massage_techniques: string[];
    dietary_therapy: DietaryTherapy;
  };
  modern_treatment: {
    medications: Medication[];
    procedures: string[];
    lifestyle_modifications: string[];
  };
  integrated_approach: {
    combination_therapy: string[];
    monitoring_plan: string[];
    safety_considerations: string[];
  };
  duration: string;
  targetConstitution: ConstitutionType;
}

/**
 * 治疗验证接口
 */
export interface TreatmentValidation {
  safety_check: boolean;
  drug_interactions: string[];
  contraindications: string[];
  suggestedAdjustments: string[];
  approval_status: 'approved' | 'needs_modification' | 'rejected';
}

/**
 * 生活方式结果接口
 */
export interface LifestyleResult {
  nutrition: NutritionGuidance;
  wellness: WellnessGuidance;
  dailyRoutine: DailyRoutine;
}

/**
 * 营养指导接口
 */
export interface NutritionGuidance {
  seasonal_foods: string[];
  constitution_foods: string[];
  avoid_foods: string[];
  meal_timing: string[];
  cooking_methods: string[];
  supplements: string[];
}

/**
 * 养生指导接口
 */
export interface WellnessGuidance {
  exercise_recommendations: ExerciseRecommendation[];
  meditation_practices: string[];
  breathing_exercises: string[];
  environmental_factors: string[];
  seasonal_adjustments: string[];
}

/**
 * 每日作息接口
 */
export interface DailyRoutine {
  morning: string;
  noon: string;
  evening: string;
  sleep: string;
  weekly_schedule?: WeeklySchedule;
}

/**
 * 症状接口
 */
export interface Symptom {
  name: string;
  severity: number; // 1-10
  duration: string;
  frequency: string;
  triggers?: string[];
  location?: string;
}

/**
 * 体质类型枚举
 */
export enum ConstitutionType {
  BALANCED = 'balanced', // 平和质
  QI_DEFICIENCY = 'qi_deficiency', // 气虚质
  YANG_DEFICIENCY = 'yang_deficiency', // 阳虚质
  YIN_DEFICIENCY = 'yin_deficiency', // 阴虚质
  PHLEGM_DAMPNESS = 'phlegm_dampness', // 痰湿质
  DAMP_HEAT = 'damp_heat', // 湿热质
  BLOOD_STASIS = 'blood_stasis', // 血瘀质
  QI_STAGNATION = 'qi_stagnation', // 气郁质
  SPECIAL_CONSTITUTION = 'special_constitution' // 特禀质
}

/**
 * 生命体征接口
 */
export interface VitalSigns {
  blood_pressure: {
    systolic: number;
    diastolic: number;
  };
  heart_rate: number;
  temperature: number;
  respiratory_rate: number;
  oxygen_saturation?: number;
  weight?: number;
  height?: number;
  bmi?: number;
}

/**
 * 实验室检查结果接口
 */
export interface LabResult {
  test_name: string;
  value: number | string;
  unit: string;
  reference_range: string;
  status: 'normal' | 'high' | 'low' | 'critical';
  date: Date;
}

/**
 * 中药方剂接口
 */
export interface HerbalFormula {
  name: string;
  ingredients: HerbalIngredient[];
  preparation_method: string;
  dosage: string;
  administration: string;
  duration: string;
  modifications?: string[];
}

/**
 * 中药成分接口
 */
export interface HerbalIngredient {
  name: string;
  latin_name: string;
  dosage: string;
  function: string;
  processing?: string;
}

/**
 * 针灸穴位接口
 */
export interface AcupuncturePoint {
  name: string;
  location: string;
  meridian: string;
  function: string;
  technique: string;
  duration: string;
}

/**
 * 食疗接口
 */
export interface DietaryTherapy {
  therapeutic_foods: string[];
  meal_plans: MealPlan[];
  cooking_instructions: string[];
  timing_recommendations: string[];
}

/**
 * 膳食计划接口
 */
export interface MealPlan {
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  foods: string[];
  portions: string[];
  preparation: string;
  benefits: string[];
}

/**
 * 药物接口
 */
export interface Medication {
  name: string;
  generic_name: string;
  dosage: string;
  frequency: string;
  duration: string;
  instructions: string[];
  side_effects: string[];
  interactions: string[];
}

/**
 * 运动推荐接口
 */
export interface ExerciseRecommendation {
  type: string;
  intensity: 'low' | 'moderate' | 'high';
  duration: string;
  frequency: string;
  instructions: string[];
  benefits: string[];
  precautions: string[];
}

/**
 * 周计划接口
 */
export interface WeeklySchedule {
  monday: DailyActivity[];
  tuesday: DailyActivity[];
  wednesday: DailyActivity[];
  thursday: DailyActivity[];
  friday: DailyActivity[];
  saturday: DailyActivity[];
  sunday: DailyActivity[];
}

/**
 * 每日活动接口
 */
export interface DailyActivity {
  time: string;
  activity: string;
  duration: string;
  notes?: string;
}

/**
 * 协作事件接口
 */
export interface CollaborationEvent {
  type: 'task_created' | 'task_started' | 'task_completed' | 'task_failed' | 'agent_joined' | 'agent_left';
  taskId: string;
  agentId?: string;
  timestamp: Date;
  data?: any;
}

/**
 * 智能体能力枚举
 */
export enum AgentCapability {
  // 小艾的能力
  USER_INTERACTION = 'user_interaction',
  HEALTH_ASSESSMENT = 'health_assessment',
  SYMPTOM_ANALYSIS = 'symptom_analysis',
  
  // 小克的能力
  TCM_DIAGNOSIS = 'tcm_diagnosis',
  MODERN_DIAGNOSIS = 'modern_diagnosis',
  SYNDROME_DIFFERENTIATION = 'syndrome_differentiation',
  
  // 老克的能力
  TREATMENT_PLANNING = 'treatment_planning',
  HEALTH_MANAGEMENT = 'health_management',
  LIFESTYLE_GUIDANCE = 'lifestyle_guidance',
  
  // 索儿的能力
  LIFESTYLE_SERVICES = 'lifestyle_services',
  FOOD_AGRICULTURE = 'food_agriculture',
  WELLNESS_TOURISM = 'wellness_tourism'
}

/**
 * 协作模式枚举
 */
export enum CollaborationMode {
  SEQUENTIAL = 'sequential', // 顺序协作
  PARALLEL = 'parallel', // 并行协作
  CONSENSUS = 'consensus', // 共识协作
  HIERARCHICAL = 'hierarchical' // 层次协作
}

export default {
  TaskPriority,
  TaskStatus,
  ConstitutionType,
  AgentCapability,
  CollaborationMode
}; 