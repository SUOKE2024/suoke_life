// 智能体基础类型定义   所有智能体共用的基础接口和类型
// 基础智能体接口 * export interface Agent {////  ;
 /////    ;
  getId(): string;
  getName(): string;
  getDescription(): string;
  getCapabilities(): AgentCapability[];
  getStatus(): AgentStatus;
  getMetrics(): AgentMetrics;
  initialize(): Promise<void>;
  shutdown(): Promise<void>;
  processTask(task: AgentTask): Promise<any>;
}
// 智能体状态 * export type AgentStatus = | "idl;"////;
e"; /////    "
  | "processing"
  | "error"
  | "offline"
  | "maintenance"
// 智能体能力 * export type AgentCapability = / 小艾能力* // | "health_monitorin;";
g;"; * /////     | "tcm_diagnosis""
  | "symptom_analysis"
  | "health_assessment"
  | "personalized_recommendations"
  | "data_integration"
  | "alert_management"
  | "trend_analysis"
  | "preventive_care"
  | "emergency_detection"
  | "health_coaching"
  // 小克能力 // | "service_recommendation"
  | "doctor_matching"
  | "product_management"
  | "supply_chain"
  | "appointment_booking"
  | "subscription_management"
  | "agricultural_traceability"
  | "third_party_integration"
  | "shop_management"
  | "payment_processing"
  | "logistics_management"
  // 老克能力 // | "knowledge_management"
  | "education"
  | "content_curation"
  | "game_npc"
  | "blog_management"
  | "learning_paths"
  | "tcm_knowledge_rag"
  | "community_management"
  | "certification_system"
  | "content_quality_assurance"
  | "maze_game_guidance"
  // 索儿能力 // | "lifestyle_management"
  | "emotional_support"
  | "habit_tracking"
  | "environmental_sensing"
  | "wellness_planning"
  | "behavior_intervention"
  | "multi_device_integration"
  | "stress_management"
  | "companionship"
  | "crisis_support"
// 智能体性能指标 * export interface AgentMetrics { tasksProcessed: number, ////
  successRate: number,
  averageResponseTime: number,
  lastActive: Date;
}
// 智能体任务 * export interface AgentTask { taskId: string, ,////
  type: string,
  data: unknown,
  priority: "low" | "medium" | "high" | "urgent",
  timestamp: Date,
  userId?: string,
  timeout?: number,
  retryCount?: number;
}
// 智能体响应 * export interface AgentResponse { success: boolean////  ;
 /////    ;
  data?: unknown,
  error?: string,
  timestamp: Date,
  agentId: string,
  taskId?: string;
}
// 智能体配置 * export interface AgentConfig { maxConcurrentTasks: number, ////
  timeoutMs: number,
  retryAttempts: number,
  cacheEnabled: boolean,
  cacheTTL: number,
  [key: string]: unknown;
}
// 智能体上下文 * export interface AgentContext {////  ;
 /////    ;
  userId?: string,
  sessionId?: string,
  userProfile?: unknown,
  preferences?: unknown,
  history?: unknown[],
  [key: string]: unknown;
}
// 通用数据类型 * export interface Location { latitude: number, ////  ;
;
  longitude: number,
  address?: string,
  city?: string,
  province?: string,
  country?: string;
}
export interface ContactInfo  {phone?: string,
  email?: string,
  wechat?: string,
  emergencyContact?: EmergencyContact;
}
export interface EmergencyContact { name: string,
  relationship: string,
  phone: string,
  email?: string;
}
// 时间相关类型 * export interface TimeRange { start: Date, ////
  end: Date;
}
export interface Schedule  {[day: string]: string[];
}
// 评分和反馈 * export interface Rating { score: number, ////  ;
  maxScore: number,
  reviewCount: number,
  distribution?: { [score: number]: number};
}
export interface Feedback { id: string,
  userId: string,
  rating: number,
  comment?: string,
  timestamp: Date,
  helpful?: number;
}
// 通知类型 * export interface Notification { id: string, ,////
  userId: string,
  type: string,
  title: string,
  message: string,
  priority: "low" | "medium" | "high" | "urgent",
  read: boolean,
  timestamp: Date,
  expiresAt?: Date,
  actionUrl?: string;
}
// 错误类型 * export interface AgentError { code: string, ////  ;
;
  message: string,
  details?: unknown,
  timestamp: Date,
  agentId: string,
  taskId?: string;
}
// 健康相关基础类型 * export type ConstitutionType = | "balance;"////;
d;
"
  | "qi_deficiency"
  | "yang_deficiency"
  | "yin_deficiency"
  | "phlegm_dampness"
  | "damp_heat"
  | "blood_stasis"
  | "qi_stagnation"
  | "special_constitution";
export interface HealthGoal { id: string,
  type: string,
  description: string,
  targetValue?: number,
  currentValue?: number,
  unit?: string,
  deadline?: Date,
  priority: "low" | "medium" | "high";
}
export interface RiskFactor { factor: string,
  level: "low" | "medium" | "high",
  description?: string,
  recommendations?: string[];
}
export interface Medication { name: string,
  dosage: string,
  frequency: string,
  startDate: Date,
  endDate?: Date,
  prescribedBy?: string,
  purpose?: string;
}
// 服务相关基础类型 * export interface ServiceProvider { id: string, ////
  name: string,
  type: string,
  rating: number,
  verified: boolean,
  contact: ContactInfo,
  location?: Location;
}
export interface PricingInfo { amount: number,
  currency: string,
  unit?: string,
  discounts?: Discount[]
}
export interface Discount { type: string,
  value: number,
  description: string,
  validUntil?: Date,
  conditions?: string[];
}
export interface AvailabilityInfo { available: boolean,
  schedule?: Schedule,
  nextAvailable?: Date,
  capacity?: number,
  restrictions?: string[];
}
// 支付相关基础类型 * export interface PaymentMethod { id: string, ,////
  type: | "credit_card"| "debit_card"| "alipay",
    | "wechat_pay"
    | "bank_transfer"
    | "cash",
  provider: string,
  details: unknown,
  default: boolean,
  verified: boolean;
}
export interface PaymentRequest { amount: number,
  currency: string,
  description: string,
  paymentMethod: PaymentMethod,
  userId: string,
  orderId?: string,
  metadata?: unknown;
}
export interface PaymentTransaction { id: string,
  userId: string,
  amount: number,
  currency: string,
  method: PaymentMethod,
  status: | "pending"| "processing"| "completed",
    | "failed"| "cancelled"| "refunded",
  description: string,
  timestamp: Date,
  confirmationCode?: string,
  failureReason?: string,
  refundAmount?: number,
  refundDate?: Date;
}
// 订阅相关基础类型 * export interface SubscriptionPlan { id: string, ////
  name: string,
  description: string,
  price: PricingInfo,
  duration: string,
  features: string[],
  limitations?: unknown,
  popular?: boolean;
}
export interface AppointmentAction { type: "book" | "reschedule" | "cancel" | "confirm",
  appointmentId?: string,
  newTime?: Date,
  reason?: string;
}
// 导出所有类型 * export * from ". / xiaoai * types"////   ;
 / export * from "./xiaoke/////    types";
/export * from "./laoke/////    types";
/export * from "./soer/////    types";
// /**
 * 智能体类型枚举
 */
export enum AgentType {
  XIAOAI = 'xiaoai',    // 小艾 - AI推理专家
  XIAOKE = 'xiaoke',    // 小克 - 健康监测专家
  LAOKE = 'laoke',      // 老克 - 中医养生专家
  SOER = 'soer'         // 索儿 - 生活服务专家
}

/**
 * 智能体能力枚举
 */
export enum AgentCapability {
  // 小艾的能力
  AI_INFERENCE = 'ai_inference',
  VOICE_INTERACTION = 'voice_interaction',
  MULTIMODAL_ANALYSIS = 'multimodal_analysis',
  MEDICAL_CONSULTATION = 'medical_consultation',
  TONGUE_DIAGNOSIS = 'tongue_diagnosis',
  FACE_ANALYSIS = 'face_analysis',
  ACCESSIBILITY_SERVICE = 'accessibility_service',
  SIGN_LANGUAGE = 'sign_language',
  VOICE_GUIDANCE = 'voice_guidance',
  HEALTH_RECORD_MANAGEMENT = 'health_record_management',

  // 小克的能力
  SERVICE_RECOMMENDATION = 'service_recommendation',
  DOCTOR_MATCHING = 'doctor_matching',
  PRODUCT_MANAGEMENT = 'product_management',
  SUPPLY_CHAIN = 'supply_chain',
  APPOINTMENT_BOOKING = 'appointment_booking',
  SUBSCRIPTION_MANAGEMENT = 'subscription_management',
  AGRICULTURAL_TRACEABILITY = 'agricultural_traceability',
  THIRD_PARTY_INTEGRATION = 'third_party_integration',
  SHOP_MANAGEMENT = 'shop_management',
  PAYMENT_PROCESSING = 'payment_processing',
  LOGISTICS_MANAGEMENT = 'logistics_management',

  // 老克的能力
  KNOWLEDGE_RETRIEVAL = 'knowledge_retrieval',
  LEARNING_PATH = 'learning_path',
  CONTENT_MANAGEMENT = 'content_management',
  EDUCATION_SYSTEM = 'education_system',
  GAME_NPC = 'game_npc',
  BLOG_MANAGEMENT = 'blog_management',
  KNOWLEDGE_GRAPH = 'knowledge_graph',
  RAG_SYSTEM = 'rag_system',
  AR_VR_INTERACTION = 'ar_vr_interaction',
  CONTENT_MODERATION = 'content_moderation',

  // 索儿的能力
  LIFESTYLE_MANAGEMENT = 'lifestyle_management',
  HEALTH_MONITORING = 'health_monitoring',
  SENSOR_INTEGRATION = 'sensor_integration',
  BEHAVIOR_INTERVENTION = 'behavior_intervention',
  EMOTIONAL_SUPPORT = 'emotional_support',
  ENVIRONMENT_SENSING = 'environment_sensing',
  PERSONALIZED_RECOMMENDATIONS = 'personalized_recommendations',
  HABIT_TRACKING = 'habit_tracking',
  WELLNESS_COACHING = 'wellness_coaching',
  DATA_FUSION = 'data_fusion'
}

/**
 * 中医体质类型
 */
export enum ConstitutionType {
  BALANCED = 'balanced',           // 平和质
  QI_DEFICIENCY = 'qi_deficiency', // 气虚质
  YANG_DEFICIENCY = 'yang_deficiency', // 阳虚质
  YIN_DEFICIENCY = 'yin_deficiency',   // 阴虚质
  PHLEGM_DAMPNESS = 'phlegm_dampness', // 痰湿质
  DAMP_HEAT = 'damp_heat',         // 湿热质
  BLOOD_STASIS = 'blood_stasis',   // 血瘀质
  QI_STAGNATION = 'qi_stagnation', // 气郁质
  SPECIAL_CONSTITUTION = 'special_constitution' // 特禀质
}

/**
 * 智能体上下文
 */
export interface AgentContext {
  userId: string;
  sessionId?: string;
  userProfile?: UserProfile;
  healthData?: HealthData;
  preferences?: UserPreferences;
  location?: LocationInfo;
  deviceInfo?: DeviceInfo;
  timestamp?: Date;
  conversationHistory?: ConversationMessage[];
  currentChannel?: string; // 当前频道：首页、SUOKE、探索、LIFE
  [key: string]: any;
}

/**
 * 智能体响应
 */
export interface AgentResponse {
  success: boolean;
  response: string;
  data?: any;
  error?: string;
  context?: AgentContext;
  metadata?: {
    agentType?: AgentType;
    executionTime?: number;
    confidence?: number;
    intent?: string;
    timestamp?: string;
    responseId?: string;
    [key: string]: any;
  };
}

/**
 * 用户档案
 */
export interface UserProfile {
  id: string;
  name: string;
  age: number;
  gender: 'male' | 'female' | 'other';
  constitution?: ConstitutionType; // 中医体质
  medicalHistory?: MedicalRecord[];
  allergies?: string[];
  medications?: Medication[];
  preferences?: UserPreferences;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * 健康数据
 */
export interface HealthData {
  vitals?: VitalSigns;
  symptoms?: Symptom[];
  measurements?: HealthMeasurement[];
  activities?: ActivityData[];
  sleep?: SleepData;
  nutrition?: NutritionData;
  mood?: MoodData;
  timestamp: Date;
}

/**
 * 用户偏好
 */
export interface UserPreferences {
  language: string;
  timezone: string;
  notificationSettings: NotificationSettings;
  privacySettings: PrivacySettings;
  accessibilitySettings: AccessibilitySettings;
  communicationStyle: 'formal' | 'casual' | 'friendly';
  preferredAgents?: AgentType[];
}

/**
 * 位置信息
 */
export interface LocationInfo {
  latitude: number;
  longitude: number;
  address?: string;
  city?: string;
  country?: string;
  timezone?: string;
}

/**
 * 设备信息
 */
export interface DeviceInfo {
  deviceId: string;
  platform: 'ios' | 'android' | 'web';
  version: string;
  capabilities: string[];
  sensors?: string[];
}

/**
 * 对话消息
 */
export interface ConversationMessage {
  id: string;
  agentType: AgentType;
  message: string;
  timestamp: Date;
  isUser: boolean;
  metadata?: any;
}

/**
 * 医疗记录
 */
export interface MedicalRecord {
  id: string;
  date: Date;
  type: 'diagnosis' | 'treatment' | 'prescription' | 'test_result';
  description: string;
  doctor?: string;
  hospital?: string;
  attachments?: string[];
}

/**
 * 生命体征
 */
export interface VitalSigns {
  heartRate?: number;
  bloodPressure?: {
    systolic: number;
    diastolic: number;
  };
  temperature?: number;
  respiratoryRate?: number;
  oxygenSaturation?: number;
  weight?: number;
  height?: number;
  bmi?: number;
}

/**
 * 症状
 */
export interface Symptom {
  name: string;
  severity: 1 | 2 | 3 | 4 | 5; // 1-轻微, 5-严重
  duration: string;
  description?: string;
  location?: string;
  triggers?: string[];
  relievingFactors?: string[];
}

/**
 * 健康测量
 */
export interface HealthMeasurement {
  type: string;
  value: number;
  unit: string;
  timestamp: Date;
  device?: string;
  notes?: string;
}

/**
 * 活动数据
 */
export interface ActivityData {
  type: 'walking' | 'running' | 'cycling' | 'swimming' | 'other';
  duration: number; // 分钟
  intensity: 'low' | 'moderate' | 'high';
  calories?: number;
  distance?: number;
  timestamp: Date;
}

/**
 * 睡眠数据
 */
export interface SleepData {
  bedtime: Date;
  wakeTime: Date;
  duration: number; // 小时
  quality: 1 | 2 | 3 | 4 | 5;
  deepSleep?: number;
  lightSleep?: number;
  remSleep?: number;
  interruptions?: number;
}

/**
 * 营养数据
 */
export interface NutritionData {
  meals: Meal[];
  totalCalories: number;
  macronutrients: {
    carbs: number;
    protein: number;
    fat: number;
  };
  micronutrients?: { [key: string]: number };
  hydration?: number; // 毫升
}

/**
 * 餐食
 */
export interface Meal {
  type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  foods: Food[];
  timestamp: Date;
  calories: number;
}

/**
 * 食物
 */
export interface Food {
  name: string;
  quantity: number;
  unit: string;
  calories: number;
  nutrients?: { [key: string]: number };
}

/**
 * 情绪数据
 */
export interface MoodData {
  mood: 'very_sad' | 'sad' | 'neutral' | 'happy' | 'very_happy';
  stress: 1 | 2 | 3 | 4 | 5;
  energy: 1 | 2 | 3 | 4 | 5;
  notes?: string;
  timestamp: Date;
}

/**
 * 通知设置
 */
export interface NotificationSettings {
  enabled: boolean;
  healthReminders: boolean;
  appointmentReminders: boolean;
  medicationReminders: boolean;
  exerciseReminders: boolean;
  sleepReminders: boolean;
  quietHours: {
    start: string;
    end: string;
  };
}

/**
 * 隐私设置
 */
export interface PrivacySettings {
  dataSharing: boolean;
  anonymousAnalytics: boolean;
  locationTracking: boolean;
  healthDataSharing: boolean;
  marketingCommunications: boolean;
}

/**
 * 无障碍设置
 */
export interface AccessibilitySettings {
  voiceGuidance: boolean;
  signLanguage: boolean;
  highContrast: boolean;
  largeText: boolean;
  screenReader: boolean;
  hapticFeedback: boolean;
  slowAnimations: boolean;
}

/**
 * 智能体健康状态
 */
export interface AgentHealthStatus {
  agentType: AgentType;
  status: 'healthy' | 'warning' | 'error' | 'initializing' | 'shutdown';
  load: number; // 0-1
  responseTime: number; // 毫秒
  errorRate: number; // 0-1
  lastCheck: Date;
  capabilities: AgentCapability[];
  version: string;
  uptime?: number;
  memoryUsage?: number;
  cpuUsage?: number;
  throughput?: number;
  specialFeatures?: string[];
}

/**
 * 智能体协作消息
 */
export interface AgentCollaborationMessage {
  id: string;
  fromAgent: AgentType;
  toAgent: AgentType;
  messageType: 'request' | 'response' | 'notification' | 'data_share';
  content: any;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  timestamp: Date;
  correlationId?: string;
  metadata?: any;
}

/**
 * 智能体决策结果
 */
export interface AgentDecisionResult {
  decision: string;
  confidence: number;
  reasoning: string[];
  alternatives?: string[];
  recommendedActions?: string[];
  metadata?: any;
}
// 
