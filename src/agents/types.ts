// 智能体基础类型定义   所有智能体共用的基础接口和类型
// 基础智能体接口 * export interface Agent {; */;
  getId();: string;
  getName();: string;
  getDescription();: string;
  getCapabilities();: AgentCapability[];
  getStatus();: AgentStatus;
  getMetrics();: AgentMetrics;
  initialize();: Promise<void>;
  shutdown();: Promise<void>;
  processTask(task: AgentTask);: Promise<any>}
// 智能体状态 * export type AgentStatus = | "idl;e"; */;
  | "processing"
  | "error"
  | "offline"
  | "maintenance"
// 智能体能力 * export type AgentCapability = *// 小艾能力* *   | "health_monitorin;g;"; * *//
  | "tcm_diagnosis"
  | "symptom_analysis"
  | "health_assessment"
  | "personalized_recommendations"
  | "data_integration"
  | "alert_management"
  | "trend_analysis"
  | "preventive_care"
  | "emergency_detection"
  | "health_coaching"
  // 小克能力 *   | "service_recommendation" */
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
  // 老克能力 *   | "knowledge_management" */
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
  // 索儿能力 *   | "lifestyle_management" */
  | "emotional_support"
  | "habit_tracking"
  | "environmental_sensing"
  | "wellness_planning"
  | "behavior_intervention"
  | "multi_device_integration"
  | "stress_management"
  | "companionship"
  | "crisis_support";
// 智能体性能指标 * export interface AgentMetrics { tasksProcessed: number, */;
  successRate: number,
  averageResponseTime: number,
  lastActive: Date}
// 智能体任务 * export interface AgentTask { taskId: string, */,
  type: string,
  data: unknown,
  priority: "low" | "medium" | "high" | "urgent",
  timestamp: Date;
  userId?: string;
  timeout?: number;
  retryCount?: number}
// 智能体响应 * export interface AgentResponse { success: boolean; */;
  data?: unknown;
  error?: string;
  timestamp: Date,
  agentId: string;
  taskId?: string}
// 智能体配置 * export interface AgentConfig { maxConcurrentTasks: number, */;
  timeoutMs: number,
  retryAttempts: number,
  cacheEnabled: boolean,
  cacheTTL: number;
  [key: string]: unknown}
// 智能体上下文 * export interface AgentContext {; */;
  userId?: string;
  sessionId?: string;
  userProfile?: unknown;
  preferences?: unknown;
  history?: unknown[];
  [key: string]: unknown}
// 通用数据类型 * export interface Location { latitude: number, */;
  longitude: number;
  address?: string;
  city?: string;
  province?: string;
  country?: string}
export interface ContactInfo {;
  phone?: string;
  email?: string;
  wechat?: string;
  emergencyContact?: EmergencyContact}
export interface EmergencyContact { name: string,
  relationship: string,
  phone: string;
  email?: string}
// 时间相关类型 * export interface TimeRange { start: Date, */;
  end: Date}
export interface Schedule {;
  [day: string]: string[];
}
// 评分和反馈 * export interface Rating { score: number, */;
  maxScore: number,
  reviewCount: number;
  distribution?: { [score: number]: number};
}
export interface Feedback { id: string,
  userId: string,
  rating: number;
  comment?: string;
  timestamp: Date;
  helpful?: number}
// 通知类型 * export interface Notification { id: string, */,
  userId: string,
  type: string,
  title: string,
  message: string,
  priority: "low" | "medium" | "high" | "urgent",
  read: boolean,
  timestamp: Date;
  expiresAt?: Date;
  actionUrl?: string}
// 错误类型 * export interface AgentError { code: string, */;
  message: string;
  details?: unknown;
  timestamp: Date,
  agentId: string,
  taskId?: string}
// 健康相关基础类型 * export type ConstitutionType = | "balance;d;"; */
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
  description: string;
  targetValue?: number;
  currentValue?: number;
  unit?: string;
  deadline?: Date,
  priority: "low" | "medium" | "high"}
export interface RiskFactor { factor: string,
  level: "low" | "medium" | "high";
  description?: string;
  recommendations?: string[];
  }
export interface Medication { name: string,
  dosage: string,
  frequency: string,
  startDate: Date;
  endDate?: Date;
  prescribedBy?: string;
  purpose?: string}
// 服务相关基础类型 * export interface ServiceProvider { id: string, */;
  name: string,
  type: string,
  rating: number,
  verified: boolean,
  contact: ContactInfo;
  location?: Location}
export interface PricingInfo { amount: number,
  currency: string;
  unit?: string;
  discounts?: Discount[];
  }
export interface Discount { type: string,
  value: number,
  description: string;
  validUntil?: Date;
  conditions?: string[];
  }
export interface AvailabilityInfo { available: boolean;
  schedule?: Schedule;
  nextAvailable?: Date;
  capacity?: number;
  restrictions?: string[];
  }
// 支付相关基础类型 * export interface PaymentMethod { id: string, */,
  type: | "credit_card"| "debit_card"| "alipay",
    | "wechat_pay"
    | "bank_transfer"
    | "cash";
  provider: string,
  details: unknown,
  default: boolean,
  verified: boolean}
export interface PaymentRequest { amount: number,
  currency: string,
  description: string,
  paymentMethod: PaymentMethod,
  userId: string;
  orderId?: string,
  metadata?: unknown}
export interface PaymentTransaction { id: string,
  userId: string,
  amount: number,
  currency: string,
  method: PaymentMethod,
  status: | "pending"| "processing"| "completed",
    | "failed"
    | "cancelled"
    | "refunded";
  description: string,
  timestamp: Date;
  confirmationCode?: string;
  failureReason?: string;
  refundAmount?: number;
  refundDate?: Date}
// 订阅相关基础类型 * export interface SubscriptionPlan { id: string, */;
  name: string,
  description: string,
  price: PricingInfo,
  duration: string,
  features: string[];
  limitations?: unknown,
  popular?: boolean}
export interface AppointmentAction { type: "book" | "reschedule" | "cancel" | "confirm";
  appointmentId?: string;
  newTime?: Date,
  reason?: string}
// 导出所有类型 * export * from ". *// xiaoai * types" *//export * from "./xiaoke/types"/export * from "./laoke/types"/export * from "./soer/types";/;