// 索克生活 - 智能体基础类型定义
// 所有智能体共用的基础接口和类型
// 智能体状态枚举
export type AgentStatus = | 'idle';
  | 'active'
  | 'processing'
  | 'error'
  | 'offline'
  | 'maintenance
// 智能体类型枚举'/,'/g'/;
export enum AgentType {'XIAOAI = 'xiaoai', // 小艾 - AI推理专家'/,'/g'/;
XIAOKE = 'xiaoke', // 小克 - 健康监测专家'/,'/g'/;
LAOKE = 'laoke', // 老克 - 中医养生专家'/;'/g'/;
}
}
  SOER = 'soer', // 索儿 - 生活服务专家'}''/;'/g'/;
}
// 智能体能力枚举'
export enum AgentCapability {';}  // 小艾的能力'/,'/g'/;
AI_INFERENCE = 'ai_inference','
VOICE_INTERACTION = 'voice_interaction','
MULTIMODAL_ANALYSIS = 'multimodal_analysis','
MEDICAL_CONSULTATION = 'medical_consultation','
TONGUE_DIAGNOSIS = 'tongue_diagnosis','
FACE_ANALYSIS = 'face_analysis','
ACCESSIBILITY_SERVICE = 'accessibility_service','
SIGN_LANGUAGE = 'sign_language','
VOICE_GUIDANCE = 'voice_guidance','
HEALTH_RECORD_MANAGEMENT = 'health_record_management','
  // 小克的能力'/,'/g'/;
SERVICE_RECOMMENDATION = 'service_recommendation','
DOCTOR_MATCHING = 'doctor_matching','
PRODUCT_MANAGEMENT = 'product_management','
SUPPLY_CHAIN = 'supply_chain','
APPOINTMENT_BOOKING = 'appointment_booking','
SUBSCRIPTION_MANAGEMENT = 'subscription_management','
AGRICULTURAL_TRACEABILITY = 'agricultural_traceability','
THIRD_PARTY_INTEGRATION = 'third_party_integration','
SHOP_MANAGEMENT = 'shop_management','
PAYMENT_PROCESSING = 'payment_processing','
LOGISTICS_MANAGEMENT = 'logistics_management','
  // 老克的能力'/,'/g'/;
KNOWLEDGE_RETRIEVAL = 'knowledge_retrieval','
LEARNING_PATH = 'learning_path','
CONTENT_MANAGEMENT = 'content_management','
EDUCATION_SYSTEM = 'education_system','
GAME_NPC = 'game_npc','
BLOG_MANAGEMENT = 'blog_management','
KNOWLEDGE_GRAPH = 'knowledge_graph','
RAG_SYSTEM = 'rag_system','
AR_VR_INTERACTION = 'ar_vr_interaction','
CONTENT_MODERATION = 'content_moderation','
  // 索儿的能力'/,'/g'/;
LIFESTYLE_MANAGEMENT = 'lifestyle_management','
HEALTH_MONITORING = 'health_monitoring','
SENSOR_INTEGRATION = 'sensor_integration','
BEHAVIOR_INTERVENTION = 'behavior_intervention','
EMOTIONAL_SUPPORT = 'emotional_support','
ENVIRONMENT_SENSING = 'environment_sensing','
PERSONALIZED_RECOMMENDATIONS = 'personalized_recommendations','
HABIT_TRACKING = 'habit_tracking','
WELLNESS_COACHING = 'wellness_coaching',
}
}
  DATA_FUSION = 'data_fusion',}
}
// 中医体质枚举'/,'/g'/;
export enum ConstitutionType {'BALANCED = 'balanced', // 平和质'/,'/g'/;
QI_DEFICIENCY = 'qi_deficiency', // 气虚质'/,'/g'/;
YANG_DEFICIENCY = 'yang_deficiency', // 阳虚质'/,'/g'/;
YIN_DEFICIENCY = 'yin_deficiency', // 阴虚质'/,'/g'/;
PHLEGM_DAMPNESS = 'phlegm_dampness', // 痰湿质'/,'/g'/;
DAMP_HEAT = 'damp_heat', // 湿热质'/,'/g'/;
BLOOD_STASIS = 'blood_stasis', // 血瘀质'/,'/g'/;
QI_STAGNATION = 'qi_stagnation', // 气郁质'/;'/g'/;
}
}
  SPECIAL_CONSTITUTION = 'special_constitution', // 特禀质'}''/;'/g'/;
}
// 基础智能体接口
export interface Agent {id: string}name: string,;
description: string,
capabilities: AgentCapability[],
const status = AgentStatus;
getId(): string;
getName(): string;
getDescription(): string;
getCapabilities(): AgentCapability[];
getStatus(): AgentStatus;
getMetrics(): AgentMetrics;
initialize(): Promise<void>;
shutdown(): Promise<void>;
}
}
  processTask(task: AgentTask): Promise<any>}
}
// 智能体性能指标
export interface AgentMetrics {tasksProcessed: number}successRate: number,;
averageResponseTime: number,
}
}
  const lastActive = Date}
}
// 智能体任务
export interface AgentTask {taskId: string}type: string,;
data: unknown,'
priority: 'low' | 'medium' | 'high' | 'urgent,'';
const timestamp = Date;
userId?: string;
timeout?: number;
}
}
  retryCount?: number}
}
// 智能体响应
export interface AgentResponse {success: boolean}const response = string;
data?: unknown;
error?: string;
  timestamp: Date,
const agentId = string;
}
}
  taskId?: string}
}
// 智能体配置
export interface AgentConfig {maxConcurrentTasks: number}timeoutMs: number,;
retryAttempts: number,
cacheEnabled: boolean,
const cacheTTL = number;
}
}
  [key: string]: unknown}
}
// 智能体上下文
export interface AgentContext {;
const userId = string;
sessionId?: string;
userProfile?: UserProfile;
healthData?: HealthData;
preferences?: UserPreferences;
location?: LocationInfo;
deviceInfo?: DeviceInfo;
timestamp?: Date;
conversationHistory?: ConversationMessage[];
currentChannel?: string; // 当前频道：首页、SUOKE、探索、LIFE
}
  [key: string]: any}
}
// 支付相关类型'/,'/g'/;
export type PaymentMethod = ';
  | 'alipay'
  | 'wechat'
  | 'credit_card'
  | 'bank_transfer';
// 通用数据类型
export interface Location {latitude: number}const longitude = number;
address?: string;
city?: string;
province?: string;
}
}
  country?: string}
}
export interface ContactInfo {;
phone?: string;
email?: string;
wechat?: string;
}
  emergencyContact?: EmergencyContact}
}
export interface EmergencyContact {name: string}relationship: string,;
const phone = string;
}
}
  email?: string}
}
// 时间相关类型
export interface TimeRange {;
start: Date,
}
  const end = Date}
}
export interface Schedule {;
}
  [day: string]: string[]}
}
// 评分和反馈
export interface Rating {score: number}maxScore: number,;
}
}
  const reviewCount = number}
  distribution?: { [score: number]: number ;
}
export interface Feedback {id: string}userId: string,;
const rating = number;
comment?: string;
const timestamp = Date;
}
}
  helpful?: number}
}
// 通知类型
export interface Notification {id: string}userId: string,;
type: string,
title: string,
message: string,'
priority: 'low' | 'medium' | 'high' | 'urgent,'';
read: boolean,
const timestamp = Date;
expiresAt?: Date;
}
}
  actionUrl?: string}
}
// 错误类型
export interface AgentError {code: string}const message = string;
details?: unknown;
  timestamp: Date,
const agentId = string;
}
}
  taskId?: string}
}
export interface HealthGoal {id: string}type: string,;
const description = string;
targetValue?: number;
currentValue?: number;
unit?: string;
deadline?: Date;
}
}
  const priority = 'low' | 'medium' | 'high}
}
export interface RiskFactor {';
'factor: string,'
const level = 'low' | 'medium' | 'high';
description?: string;
}
  recommendations?: string[]}
}
export interface Medication {name: string}dosage: string,;
frequency: string,
const startDate = Date;
endDate?: Date;
prescribedBy?: string;
}
}
  purpose?: string}
}
export interface PricingInfo {amount: number}const currency = string;
unit?: string;
}
}
  discounts?: Discount[]}
}
export interface Discount {type: string}value: number,;
const description = string;
validUntil?: Date;
}
}
  conditions?: string[]}
}
export interface AvailabilityInfo {;
const available = boolean;
schedule?: Schedule;
nextAvailable?: Date;
capacity?: number;
}
  restrictions?: string[]}
}
export interface PaymentRequest {amount: number}currency: string,;
description: string,
paymentMethod: PaymentMethod,
const userId = string;
orderId?: string;
}
}
  metadata?: unknown}
}
export interface PaymentTransaction {id: string}userId: string,;
amount: number,
currency: string,
method: PaymentMethod,
const status = '
    | 'pending'
    | 'processing'
    | 'completed'
    | 'failed'
    | 'cancelled'
    | 'refunded';
description: string,
const timestamp = Date;
confirmationCode?: string;
failureReason?: string;
refundAmount?: number;
}
}
  refundDate?: Date}
}
export interface AppointmentAction {';
'const type = 'book' | 'reschedule' | 'cancel' | 'confirm';
appointmentId?: string;
newTime?: Date;
}
  reason?: string}
}
// 用户档案
export interface UserProfile {id: string}name: string,;
age: number,'
const gender = 'male' | 'female' | 'other';
constitution?: ConstitutionType; // 中医体质
medicalHistory?: MedicalRecord[];
allergies?: string[];
medications?: Medication[];
preferences?: UserPreferences;
  createdAt: Date,
}
}
  const updatedAt = Date}
}
// 健康数据
export interface HealthData {;
vitals?: VitalSigns;
symptoms?: Symptom[];
measurements?: HealthMeasurement[];
activities?: ActivityData[];
sleep?: SleepData;
nutrition?: NutritionData;
mood?: MoodData;
}
  const timestamp = Date}
}
// 用户偏好
export interface UserPreferences {language: string}timezone: string,;
notificationSettings: NotificationSettings,
privacySettings: PrivacySettings,
accessibilitySettings: AccessibilitySettings,'
const communicationStyle = 'formal' | 'casual' | 'friendly';
}
}
  preferredAgents?: AgentType[]}
}
// 位置信息
export interface LocationInfo {latitude: number}const longitude = number;
address?: string;
city?: string;
country?: string;
}
}
  timezone?: string}
}
// 设备信息
export interface DeviceInfo {';
'deviceId: string,'
platform: 'ios' | 'android' | 'web,'';
version: string,
const capabilities = string[];
}
  sensors?: string[]}
}
// 对话消息
export interface ConversationMessage {id: string}agentType: AgentType,;
message: string,
timestamp: Date,
const isUser = boolean;
}
}
  metadata?: any}
}
// 医疗记录
export interface MedicalRecord {';
id: string,'date: Date,'
type: 'diagnosis' | 'treatment' | 'prescription' | 'test_result,'';
const description = string;
doctor?: string;
hospital?: string;
}
  attachments?: string[]}
}
// 生命体征
export interface VitalSigns {;
heartRate?: number;
bloodPressure?: {systolic: number,
}
    const diastolic = number}
  };
temperature?: number;
respiratoryRate?: number;
oxygenSaturation?: number;
weight?: number;
height?: number;
bmi?: number;
}
// 症状
export interface Symptom {name: string}severity: 1 | 2 | 3 | 4 | 5; // 1-轻微, 5-严重
const duration = string;
description?: string;
location?: string;
triggers?: string[];
}
}
  relievingFactors?: string[]}
}
// 健康测量
export interface HealthMeasurement {type: string}value: number,;
unit: string,
const timestamp = Date;
device?: string;
}
}
  notes?: string}
}
// 活动数据'/,'/g'/;
export interface ActivityData {';
'type: 'walking' | 'running' | 'cycling' | 'swimming' | 'other,'
duration: number; // 分钟,'/,'/g'/;
const intensity = 'low' | 'moderate' | 'high';
calories?: number;
distance?: number;
}
  const timestamp = Date}
}
// 睡眠数据
export interface SleepData {bedtime: Date}wakeTime: Date,;
duration: number; // 小时,
const quality = 1 | 2 | 3 | 4 | 5;
deepSleep?: number;
lightSleep?: number;
remSleep?: number;
}
}
  interruptions?: number}
}
// 营养数据
export interface NutritionData {meals: Meal[]}totalCalories: number,;
macronutrients: {carbs: number,
protein: number,
}
}
    const fat = number}
  };
micronutrients?: { [key: string]: number ;
hydration?: number; // 毫升
}
// 餐食'/,'/g'/;
export interface Meal {';
'type: 'breakfast' | 'lunch' | 'dinner' | 'snack,'';
foods: Food[],
timestamp: Date,
}
  const calories = number}
}
// 食物
export interface Food {name: string}quantity: number,;
unit: string,
}
}
  const calories = number}
  nutrients?: { [key: string]: number ;
}
// 情绪数据'/,'/g'/;
export interface MoodData {';
'mood: 'very_sad' | 'sad' | 'neutral' | 'happy' | 'very_happy,'';
stress: 1 | 2 | 3 | 4 | 5,
const energy = 1 | 2 | 3 | 4 | 5;
notes?: string;
}
  const timestamp = Date}
}
// 通知设置
export interface NotificationSettings {enabled: boolean}healthReminders: boolean,;
appointmentReminders: boolean,
medicationReminders: boolean,
exerciseReminders: boolean,
sleepReminders: boolean,
quietHours: {start: string,
}
}
    const end = string}
  };
}
// 隐私设置
export interface PrivacySettings {dataSharing: boolean}anonymousAnalytics: boolean,;
locationTracking: boolean,
healthDataSharing: boolean,
}
}
  const marketingCommunications = boolean}
}
// 无障碍设置
export interface AccessibilitySettings {voiceGuidance: boolean}signLanguage: boolean,;
highContrast: boolean,
largeText: boolean,
screenReader: boolean,
hapticFeedback: boolean,
}
}
  const slowAnimations = boolean}
}
// 智能体健康状态
export interface AgentHealthStatus {';
'agentType: AgentType,'
status: 'healthy' | 'warning' | 'error' | 'initializing' | 'shutdown,'';
load: number; // 0-1,/,/g,/;
  responseTime: number; // 毫秒,/,/g,/;
  errorRate: number; // 0-1,/,/g,/;
  lastCheck: Date,
capabilities: AgentCapability[],
const version = string;
uptime?: number;
memoryUsage?: number;
cpuUsage?: number;
throughput?: number;
}
  specialFeatures?: string[]}
}
// 智能体协作消息
export interface AgentCollaborationMessage {id: string}fromAgent: AgentType,;
toAgent: AgentType,'
messageType: 'request' | 'response' | 'notification' | 'data_share,'';
content: any,'
priority: 'low' | 'normal' | 'high' | 'urgent,'';
const timestamp = Date;
correlationId?: string;
}
}
  metadata?: any}
}
// 智能体决策结果
export interface AgentDecisionResult {decision: string}confidence: number,;
const reasoning = string[];
alternatives?: string[];
recommendedActions?: string[];
}
}
  metadata?: any}
}
''
