/**
 * 索克生活统一智能体接口标准
 * 定义所有智能体必须遵循的统一接口规范
 * 
 * 设计原则：
 * 1. 统一性：所有智能体使用相同的接口标准
 * 2. 扩展性：支持不同类型智能体的特殊能力
 * 3. 兼容性：与现有系统平滑集成
 * 4. 性能：高效的通信和状态管理
 */

import { EventEmitter } from 'events';

// ============================================================================
// 核心类型定义
// ============================================================================

export enum AgentType {
  XIAOAI = 'xiaoai',    // 小艾 - 中医诊断智能体
  XIAOKE = 'xiaoke',    // 小克 - 名医资源智能体  
  LAOKE = 'laoke',      // 老克 - 知识管理智能体
  SOER = 'soer'         // 索儿 - 生活数据智能体
}

export enum AgentStatus {
  INITIALIZING = 'initializing',
  AVAILABLE = 'available',
  BUSY = 'busy',
  OFFLINE = 'offline',
  ERROR = 'error',
  MAINTENANCE = 'maintenance'
}

export enum TaskType {
  DIAGNOSIS = 'diagnosis',           // 诊断任务
  CONSULTATION = 'consultation',     // 咨询任务
  ANALYSIS = 'analysis',            // 分析任务
  RECOMMENDATION = 'recommendation', // 推荐任务
  MONITORING = 'monitoring',        // 监控任务
  EDUCATION = 'education',          // 教育任务
  COLLABORATION = 'collaboration'   // 协作任务
}

export enum CapabilityType {
  DIAGNOSTIC = 'diagnostic',         // 诊断能力
  ANALYTICAL = 'analytical',         // 分析能力
  COMMUNICATIVE = 'communicative',   // 沟通能力
  THERAPEUTIC = 'therapeutic',       // 治疗能力
  EDUCATIONAL = 'educational',       // 教育能力
  COORDINATION = 'coordination'      // 协调能力
}

// ============================================================================
// 数据结构定义
// ============================================================================

export interface AgentCapability {
  type: CapabilityType;
  name: string;
  description: string;
  proficiency: number;      // 0-1, 熟练度
  reliability: number;      // 0-1, 可靠性
  speed: number;           // 0-1, 处理速度
  accuracy: number;        // 0-1, 准确性
  lastUpdated: Date;
}

export interface AgentSpecialization {
  domain: string;           // 专业领域
  expertise: number;        // 0-1, 专业程度
  experience: number;       // 经验年数
  certifications: string[]; // 认证列表
  successRate: number;      // 0-1, 成功率
}

export interface AgentPerformance {
  taskCompletionRate: number;    // 任务完成率
  averageResponseTime: number;   // 平均响应时间(ms)
  qualityScore: number;          // 质量评分
  collaborationRating: number;   // 协作评分
  userSatisfaction: number;      // 用户满意度
  learningRate: number;          // 学习速度
  adaptabilityScore: number;     // 适应性评分
  lastEvaluated: Date;
}

export interface AgentConfiguration {
  id: string;
  type: AgentType;
  name: string;
  version: string;
  description: string;
  capabilities: AgentCapability[];
  specializations: AgentSpecialization[];
  maxConcurrentTasks: number;
  timeoutSettings: {
    defaultTimeout: number;
    maxTimeout: number;
    retryAttempts: number;
  };
  resourceLimits: {
    memory: number;
    cpu: number;
    storage: number;
  };
  communicationSettings: {
    protocols: string[];
    endpoints: string[];
    authentication: any;
  };
}

export interface AgentContext {
  sessionId: string;
  userId?: string;
  taskId?: string;
  conversationHistory?: ConversationMessage[];
  userProfile?: UserProfile;
  environmentalFactors?: EnvironmentalFactor[];
  constraints?: TaskConstraint[];
  metadata?: Record<string, any>;
}

export interface ConversationMessage {
  id: string;
  role: 'user' | 'agent' | 'system';
  content: string;
  timestamp: Date;
  agentId?: string;
  metadata?: Record<string, any>;
}

export interface UserProfile {
  id: string;
  basicInfo: {
    age: number;
    gender: string;
    name?: string;
  };
  medicalHistory: MedicalRecord[];
  preferences: UserPreferences;
  accessibilityNeeds?: AccessibilityNeeds;
}

export interface MedicalRecord {
  id: string;
  type: string;
  description: string;
  date: Date;
  severity?: string;
  status?: string;
}

export interface UserPreferences {
  language: string;
  communicationStyle: 'formal' | 'casual' | 'professional';
  privacyLevel: 'low' | 'medium' | 'high';
  notificationSettings: Record<string, boolean>;
}

export interface AccessibilityNeeds {
  visualImpairment: boolean;
  hearingImpairment: boolean;
  motorImpairment: boolean;
  cognitiveSupport: boolean;
  preferredFormats: string[];
}

export interface EnvironmentalFactor {
  type: 'location' | 'weather' | 'social' | 'cultural' | 'economic';
  value: any;
  impact: number; // -1 to 1
  confidence: number; // 0-1
}

export interface TaskConstraint {
  type: 'time' | 'resource' | 'quality' | 'privacy' | 'safety';
  specification: any;
  flexibility: 'rigid' | 'flexible' | 'negotiable';
  importance: number; // 0-1
}

// ============================================================================
// 请求和响应接口
// ============================================================================

export interface AgentRequest {
  id: string;
  type: TaskType;
  content: string;
  context: AgentContext;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  deadline?: Date;
  requiredCapabilities?: CapabilityType[];
  constraints?: TaskConstraint[];
  metadata?: Record<string, any>;
}

export interface AgentResponse {
  requestId: string;
  agentId: string;
  success: boolean;
  content: string;
  data?: any;
  confidence: number;        // 0-1, 置信度
  executionTime: number;     // 执行时间(ms)
  resourcesUsed?: ResourceUsage;
  recommendations?: Recommendation[];
  followUpActions?: FollowUpAction[];
  metadata?: Record<string, any>;
  error?: AgentError;
}

export interface ResourceUsage {
  memory: number;
  cpu: number;
  networkCalls: number;
  storageAccess: number;
  externalAPICalls: number;
}

export interface Recommendation {
  type: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  confidence: number;
  reasoning: string[];
  actions?: string[];
}

export interface FollowUpAction {
  type: string;
  description: string;
  suggestedTiming: string;
  requiredCapabilities?: CapabilityType[];
  estimatedDuration?: number;
}

export interface AgentError {
  code: string;
  message: string;
  details?: any;
  recoverable: boolean;
  suggestedActions?: string[];
}

// ============================================================================
// 协作相关接口
// ============================================================================

export interface CollaborationRequest {
  id: string;
  initiatorId: string;
  targetAgents: AgentType[];
  type: 'consultation' | 'joint_task' | 'knowledge_sharing' | 'peer_review';
  description: string;
  context: AgentContext;
  urgency: 'low' | 'medium' | 'high' | 'critical';
  deadline?: Date;
  expectedOutcome: string;
}

export interface CollaborationResponse {
  requestId: string;
  agentId: string;
  accepted: boolean;
  availability?: Date;
  estimatedDuration?: number;
  conditions?: string[];
  reason?: string;
}

export interface CollaborationSession {
  id: string;
  participants: AgentType[];
  type: string;
  status: 'planning' | 'active' | 'paused' | 'completed' | 'failed';
  context: AgentContext;
  sharedState: Record<string, any>;
  communicationLog: CollaborationMessage[];
  startTime: Date;
  endTime?: Date;
  outcome?: CollaborationOutcome;
}

export interface CollaborationMessage {
  id: string;
  senderId: string;
  recipientIds: string[];
  type: 'information' | 'request' | 'response' | 'coordination';
  content: string;
  timestamp: Date;
  metadata?: Record<string, any>;
}

export interface CollaborationOutcome {
  success: boolean;
  result: any;
  participantContributions: Record<string, any>;
  qualityMetrics: Record<string, number>;
  lessonsLearned: string[];
}

// ============================================================================
// 统一智能体接口
// ============================================================================

export interface UnifiedAgentInterface extends EventEmitter {
  // 基本属性
  readonly id: string;
  readonly type: AgentType;
  readonly configuration: AgentConfiguration;
  readonly status: AgentStatus;
  readonly performance: AgentPerformance;

  // 生命周期管理
  initialize(): Promise<void>;
  start(): Promise<void>;
  stop(): Promise<void>;
  restart(): Promise<void>;
  shutdown(): Promise<void>;

  // 核心功能
  process(request: AgentRequest): Promise<AgentResponse>;
  processStream(request: AgentRequest): AsyncGenerator<Partial<AgentResponse>>;
  
  // 状态管理
  getStatus(): AgentStatus;
  getPerformance(): AgentPerformance;
  updateConfiguration(config: Partial<AgentConfiguration>): Promise<void>;
  
  // 协作功能
  requestCollaboration(request: CollaborationRequest): Promise<CollaborationResponse>;
  joinCollaboration(sessionId: string): Promise<void>;
  leaveCollaboration(sessionId: string): Promise<void>;
  
  // 学习和适应
  learn(feedback: AgentFeedback): Promise<void>;
  adapt(context: AgentContext): Promise<void>;
  
  // 监控和诊断
  healthCheck(): Promise<HealthCheckResult>;
  getMetrics(): Promise<AgentMetrics>;
  exportState(): Promise<AgentState>;
  importState(state: AgentState): Promise<void>;
}

export interface AgentFeedback {
  requestId: string;
  rating: number;        // 1-5
  comments?: string;
  specificIssues?: string[];
  suggestions?: string[];
  context?: Record<string, any>;
}

export interface HealthCheckResult {
  healthy: boolean;
  status: AgentStatus;
  issues?: HealthIssue[];
  recommendations?: string[];
  lastChecked: Date;
}

export interface HealthIssue {
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  description: string;
  impact: string;
  suggestedFix?: string;
}

export interface AgentMetrics {
  performance: AgentPerformance;
  resourceUsage: ResourceUsage;
  taskStatistics: TaskStatistics;
  collaborationMetrics: CollaborationMetrics;
  errorStatistics: ErrorStatistics;
}

export interface TaskStatistics {
  totalTasks: number;
  completedTasks: number;
  failedTasks: number;
  averageExecutionTime: number;
  tasksByType: Record<TaskType, number>;
  tasksByPriority: Record<string, number>;
}

export interface CollaborationMetrics {
  totalCollaborations: number;
  successfulCollaborations: number;
  averageCollaborationDuration: number;
  collaborationsByType: Record<string, number>;
  partnerRatings: Record<string, number>;
}

export interface ErrorStatistics {
  totalErrors: number;
  errorsByType: Record<string, number>;
  errorsByCode: Record<string, number>;
  averageRecoveryTime: number;
  criticalErrors: number;
}

export interface AgentState {
  configuration: AgentConfiguration;
  performance: AgentPerformance;
  currentTasks: AgentRequest[];
  collaborationSessions: string[];
  learningData: any;
  customState: Record<string, any>;
  timestamp: Date;
}

// ============================================================================
// 事件类型定义
// ============================================================================

export interface AgentEvent {
  type: string;
  agentId: string;
  timestamp: Date;
  data?: any;
}

export interface AgentLifecycleEvent extends AgentEvent {
  type: 'agent.initialized' | 'agent.started' | 'agent.stopped' | 'agent.error';
}

export interface AgentTaskEvent extends AgentEvent {
  type: 'task.received' | 'task.started' | 'task.completed' | 'task.failed';
  taskId: string;
}

export interface AgentCollaborationEvent extends AgentEvent {
  type: 'collaboration.requested' | 'collaboration.joined' | 'collaboration.left' | 'collaboration.completed';
  sessionId: string;
}

export interface AgentPerformanceEvent extends AgentEvent {
  type: 'performance.updated' | 'performance.degraded' | 'performance.improved';
  metrics: Partial<AgentPerformance>;
}

// ============================================================================
// 工厂和注册接口
// ============================================================================

export interface AgentFactory {
  createAgent(type: AgentType, config: AgentConfiguration): Promise<UnifiedAgentInterface>;
  getAvailableTypes(): AgentType[];
  validateConfiguration(config: AgentConfiguration): ValidationResult;
}

export interface ValidationResult {
  valid: boolean;
  errors?: ValidationError[];
  warnings?: ValidationWarning[];
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface ValidationWarning {
  field: string;
  message: string;
  suggestion?: string;
}

export interface AgentRegistry {
  register(agent: UnifiedAgentInterface): Promise<void>;
  unregister(agentId: string): Promise<void>;
  discover(criteria: AgentCriteria): Promise<UnifiedAgentInterface[]>;
  getAgent(agentId: string): Promise<UnifiedAgentInterface | null>;
  getAllAgents(): Promise<UnifiedAgentInterface[]>;
  updateStatus(agentId: string, status: AgentStatus): Promise<void>;
}

export interface AgentCriteria {
  type?: AgentType;
  capabilities?: CapabilityType[];
  status?: AgentStatus;
  minPerformance?: Partial<AgentPerformance>;
  availability?: boolean;
  location?: string;
}

// ============================================================================
// 导出所有接口
// ============================================================================

export default UnifiedAgentInterface;