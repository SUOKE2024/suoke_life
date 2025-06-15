/**
 * 索克生活智能体注册中心
 * 提供智能体的注册、发现、状态管理和负载均衡功能
 */

import { EventEmitter } from 'events';
import {
  UnifiedAgentInterface,
  AgentType,
  AgentStatus,
  AgentConfiguration,
  AgentPerformance,
  AgentCriteria,
  ValidationResult,
  ValidationError,
  ValidationWarning
} from '../interfaces/UnifiedAgentInterface';

// ============================================================================
// 注册中心接口
// ============================================================================

export interface AgentRegistry extends EventEmitter {
  // 基本注册管理
  register(agent: UnifiedAgentInterface): Promise<RegistrationResult>;
  unregister(agentId: string): Promise<void>;
  
  // 发现和查询
  discover(criteria: AgentCriteria): Promise<AgentInfo[]>;
  getAgent(agentId: string): Promise<AgentInfo | null>;
  getAllAgents(): Promise<AgentInfo[]>;
  getAgentsByType(type: AgentType): Promise<AgentInfo[]>;
  
  // 状态管理
  updateStatus(agentId: string, status: AgentStatus): Promise<void>;
  updatePerformance(agentId: string, performance: Partial<AgentPerformance>): Promise<void>;
  updateConfiguration(agentId: string, config: Partial<AgentConfiguration>): Promise<void>;
  
  // 健康检查
  performHealthCheck(agentId?: string): Promise<HealthCheckReport>;
  setHealthCheckInterval(interval: number): void;
  
  // 负载均衡
  selectAgent(criteria: AgentCriteria, strategy?: LoadBalancingStrategy): Promise<AgentInfo | null>;
  getLoadBalancingMetrics(): Promise<LoadBalancingMetrics>;
  
  // 监控和统计
  getRegistryMetrics(): Promise<RegistryMetrics>;
  getAgentStatistics(agentId: string): Promise<AgentStatistics>;
  
  // 事件订阅
  onAgentRegistered(callback: (agentInfo: AgentInfo) => void): void;
  onAgentUnregistered(callback: (agentId: string) => void): void;
  onAgentStatusChanged(callback: (agentId: string, oldStatus: AgentStatus, newStatus: AgentStatus) => void): void;
}

// ============================================================================
// 数据结构定义
// ============================================================================

export interface AgentInfo {
  id: string;
  type: AgentType;
  configuration: AgentConfiguration;
  status: AgentStatus;
  performance: AgentPerformance;
  
  // 注册信息
  registeredAt: Date;
  lastHeartbeat: Date;
  lastStatusUpdate: Date;
  
  // 运行时信息
  currentLoad: number;        // 0-1, 当前负载
  availableCapacity: number;  // 0-1, 可用容量
  activeConnections: number;
  queuedTasks: number;
  
  // 网络信息
  endpoints: AgentEndpoint[];
  networkLatency: number;     // ms
  
  // 元数据
  tags: string[];
  metadata: Record<string, any>;
}

export interface AgentEndpoint {
  type: 'http' | 'grpc' | 'websocket' | 'tcp' | 'udp';
  address: string;
  port: number;
  protocol?: string;
  secure: boolean;
  healthCheckPath?: string;
}

export interface RegistrationResult {
  success: boolean;
  agentId: string;
  registrationToken?: string;
  expiresAt?: Date;
  errors?: RegistrationError[];
  warnings?: RegistrationWarning[];
}

export interface RegistrationError {
  code: string;
  message: string;
  field?: string;
  details?: any;
}

export interface RegistrationWarning {
  code: string;
  message: string;
  suggestion?: string;
}

// ============================================================================
// 健康检查
// ============================================================================

export interface HealthCheckReport {
  timestamp: Date;
  overallHealth: 'healthy' | 'degraded' | 'unhealthy';
  totalAgents: number;
  healthyAgents: number;
  degradedAgents: number;
  unhealthyAgents: number;
  offlineAgents: number;
  
  agentHealthDetails: AgentHealthDetail[];
  systemIssues: SystemIssue[];
  recommendations: string[];
}

export interface AgentHealthDetail {
  agentId: string;
  status: AgentStatus;
  health: 'healthy' | 'degraded' | 'unhealthy';
  lastHeartbeat: Date;
  responseTime: number;
  issues: HealthIssue[];
  metrics: HealthMetrics;
}

export interface HealthIssue {
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: 'performance' | 'connectivity' | 'resource' | 'configuration';
  description: string;
  impact: string;
  suggestedFix?: string;
  firstDetected: Date;
}

export interface HealthMetrics {
  cpuUsage: number;          // 0-1
  memoryUsage: number;       // 0-1
  diskUsage: number;         // 0-1
  networkLatency: number;    // ms
  errorRate: number;         // 0-1
  throughput: number;        // requests/second
}

export interface SystemIssue {
  type: 'capacity' | 'performance' | 'availability' | 'configuration';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  affectedAgents: string[];
  suggestedAction: string;
}

// ============================================================================
// 负载均衡
// ============================================================================

export enum LoadBalancingStrategy {
  ROUND_ROBIN = 'round_robin',
  LEAST_CONNECTIONS = 'least_connections',
  LEAST_RESPONSE_TIME = 'least_response_time',
  WEIGHTED_ROUND_ROBIN = 'weighted_round_robin',
  PERFORMANCE_BASED = 'performance_based',
  RANDOM = 'random',
  CONSISTENT_HASH = 'consistent_hash'
}

export interface LoadBalancingMetrics {
  strategy: LoadBalancingStrategy;
  totalRequests: number;
  requestDistribution: Record<string, number>;
  averageResponseTime: number;
  failureRate: number;
  
  agentLoadMetrics: AgentLoadMetrics[];
  hotspots: LoadHotspot[];
  recommendations: LoadBalancingRecommendation[];
}

export interface AgentLoadMetrics {
  agentId: string;
  requestCount: number;
  averageResponseTime: number;
  errorRate: number;
  currentLoad: number;
  capacity: number;
  efficiency: number;        // 0-1
}

export interface LoadHotspot {
  agentId: string;
  loadLevel: 'high' | 'critical';
  duration: number;          // ms
  impact: string;
  suggestedAction: string;
}

export interface LoadBalancingRecommendation {
  type: 'scale_up' | 'scale_down' | 'redistribute' | 'optimize';
  description: string;
  priority: 'low' | 'medium' | 'high';
  estimatedImpact: string;
  implementation: string;
}

// ============================================================================
// 统计和监控
// ============================================================================

export interface RegistryMetrics {
  totalAgents: number;
  agentsByType: Record<AgentType, number>;
  agentsByStatus: Record<AgentStatus, number>;
  
  registrationRate: number;   // registrations/hour
  unregistrationRate: number; // unregistrations/hour
  
  averageUptime: number;      // percentage
  averageResponseTime: number; // ms
  
  resourceUtilization: {
    cpu: number;              // 0-1
    memory: number;           // 0-1
    network: number;          // 0-1
  };
  
  performanceMetrics: {
    averageQualityScore: number;
    averageTaskCompletionRate: number;
    averageUserSatisfaction: number;
  };
  
  errorStatistics: {
    totalErrors: number;
    errorsByType: Record<string, number>;
    criticalErrors: number;
  };
}

export interface AgentStatistics {
  agentId: string;
  uptime: number;             // percentage
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
  
  performanceHistory: PerformanceDataPoint[];
  loadHistory: LoadDataPoint[];
  errorHistory: ErrorDataPoint[];
  
  collaborationStats: {
    totalCollaborations: number;
    successfulCollaborations: number;
    averageCollaborationDuration: number;
    partnerRatings: Record<string, number>;
  };
}

export interface PerformanceDataPoint {
  timestamp: Date;
  qualityScore: number;
  responseTime: number;
  throughput: number;
  errorRate: number;
}

export interface LoadDataPoint {
  timestamp: Date;
  cpuUsage: number;
  memoryUsage: number;
  activeConnections: number;
  queuedTasks: number;
}

export interface ErrorDataPoint {
  timestamp: Date;
  errorType: string;
  errorCode: string;
  count: number;
  severity: string;
}

// ============================================================================
// 配置和策略
// ============================================================================

export interface RegistryConfiguration {
  // 基本配置
  maxAgents: number;
  registrationTimeout: number;
  heartbeatInterval: number;
  healthCheckInterval: number;
  
  // 清理策略
  inactiveAgentTimeout: number;
  cleanupInterval: number;
  retainHistoryDuration: number;
  
  // 负载均衡配置
  defaultLoadBalancingStrategy: LoadBalancingStrategy;
  loadBalancingWeights: Record<string, number>;
  
  // 监控配置
  metricsRetentionPeriod: number;
  alertThresholds: AlertThresholds;
  
  // 安全配置
  authenticationRequired: boolean;
  encryptionEnabled: boolean;
  auditLoggingEnabled: boolean;
}

export interface AlertThresholds {
  highCpuUsage: number;       // 0-1
  highMemoryUsage: number;    // 0-1
  highErrorRate: number;      // 0-1
  lowAvailability: number;    // 0-1
  highResponseTime: number;   // ms
}

// ============================================================================
// 注册中心实现基类
// ============================================================================

export abstract class BaseAgentRegistry extends EventEmitter implements AgentRegistry {
  protected config: RegistryConfiguration;
  protected agents: Map<string, AgentInfo> = new Map();
  protected healthCheckTimer?: NodeJS.Timeout;
  protected cleanupTimer?: NodeJS.Timeout;
  protected metrics: RegistryMetrics;
  
  constructor(config: RegistryConfiguration) {
    super();
    this.config = config;
    this.initializeMetrics();
    this.startPeriodicTasks();
  }
  
  // 抽象方法
  abstract persistAgentInfo(agentInfo: AgentInfo): Promise<void>;
  abstract loadAgentInfo(agentId: string): Promise<AgentInfo | null>;
  abstract removeAgentInfo(agentId: string): Promise<void>;
  
  // 基本实现
  async register(agent: UnifiedAgentInterface): Promise<RegistrationResult> {
    const validation = this.validateAgent(agent);
    if (!validation.valid) {
      return {
        success: false,
        agentId: agent.id,
        errors: validation.errors?.map(e => ({
          code: e.code,
          message: e.message,
          field: e.field
        }))
      };
    }
    
    const agentInfo: AgentInfo = {
      id: agent.id,
      type: agent.type,
      configuration: agent.configuration,
      status: agent.status,
      performance: agent.performance,
      registeredAt: new Date(),
      lastHeartbeat: new Date(),
      lastStatusUpdate: new Date(),
      currentLoad: 0,
      availableCapacity: 1,
      activeConnections: 0,
      queuedTasks: 0,
      endpoints: this.extractEndpoints(agent),
      networkLatency: 0,
      tags: [],
      metadata: {}
    };
    
    this.agents.set(agent.id, agentInfo);
    await this.persistAgentInfo(agentInfo);
    
    this.emit('agentRegistered', agentInfo);
    
    return {
      success: true,
      agentId: agent.id,
      registrationToken: this.generateRegistrationToken(agent.id),
      warnings: validation.warnings?.map(w => ({
        code: w.code,
        message: w.message,
        suggestion: w.suggestion
      }))
    };
  }
  
  async unregister(agentId: string): Promise<void> {
    const agentInfo = this.agents.get(agentId);
    if (agentInfo) {
      this.agents.delete(agentId);
      await this.removeAgentInfo(agentId);
      this.emit('agentUnregistered', agentId);
    }
  }
  
  async discover(criteria: AgentCriteria): Promise<AgentInfo[]> {
    const allAgents = Array.from(this.agents.values());
    return allAgents.filter(agent => this.matchesCriteria(agent, criteria));
  }
  
  async getAgent(agentId: string): Promise<AgentInfo | null> {
    return this.agents.get(agentId) || null;
  }
  
  async getAllAgents(): Promise<AgentInfo[]> {
    return Array.from(this.agents.values());
  }
  
  async getAgentsByType(type: AgentType): Promise<AgentInfo[]> {
    return Array.from(this.agents.values()).filter(agent => agent.type === type);
  }
  
  async updateStatus(agentId: string, status: AgentStatus): Promise<void> {
    const agentInfo = this.agents.get(agentId);
    if (agentInfo) {
      const oldStatus = agentInfo.status;
      agentInfo.status = status;
      agentInfo.lastStatusUpdate = new Date();
      await this.persistAgentInfo(agentInfo);
      this.emit('agentStatusChanged', agentId, oldStatus, status);
    }
  }
  
  // 其他方法的默认实现...
  protected validateAgent(agent: UnifiedAgentInterface): ValidationResult {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];
    
    if (!agent.id) {
      errors.push({ field: 'id', message: 'Agent ID is required', code: 'MISSING_ID' });
    }
    
    if (!agent.type) {
      errors.push({ field: 'type', message: 'Agent type is required', code: 'MISSING_TYPE' });
    }
    
    if (this.agents.has(agent.id)) {
      errors.push({ field: 'id', message: 'Agent ID already exists', code: 'DUPLICATE_ID' });
    }
    
    return {
      valid: errors.length === 0,
      errors: errors.length > 0 ? errors : undefined,
      warnings: warnings.length > 0 ? warnings : undefined
    };
  }
  
  protected matchesCriteria(agent: AgentInfo, criteria: AgentCriteria): boolean {
    if (criteria.type && agent.type !== criteria.type) return false;
    if (criteria.status && agent.status !== criteria.status) return false;
    if (criteria.availability && agent.status !== AgentStatus.AVAILABLE) return false;
    
    if (criteria.capabilities) {
      const agentCapabilities = agent.configuration.capabilities.map(c => c.type);
      if (!criteria.capabilities.every(cap => agentCapabilities.includes(cap))) {
        return false;
      }
    }
    
    if (criteria.minPerformance) {
      for (const [key, minValue] of Object.entries(criteria.minPerformance)) {
        if ((agent.performance as any)[key] < minValue) return false;
      }
    }
    
    return true;
  }
  
  protected extractEndpoints(agent: UnifiedAgentInterface): AgentEndpoint[] {
    // 从智能体配置中提取端点信息
    return agent.configuration.communicationSettings.endpoints.map(endpoint => ({
      type: 'http',
      address: endpoint,
      port: 80,
      secure: false
    }));
  }
  
  protected generateRegistrationToken(agentId: string): string {
    return `token_${agentId}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  protected initializeMetrics(): void {
    this.metrics = {
      totalAgents: 0,
      agentsByType: {} as Record<AgentType, number>,
      agentsByStatus: {} as Record<AgentStatus, number>,
      registrationRate: 0,
      unregistrationRate: 0,
      averageUptime: 0,
      averageResponseTime: 0,
      resourceUtilization: { cpu: 0, memory: 0, network: 0 },
      performanceMetrics: {
        averageQualityScore: 0,
        averageTaskCompletionRate: 0,
        averageUserSatisfaction: 0
      },
      errorStatistics: {
        totalErrors: 0,
        errorsByType: {},
        criticalErrors: 0
      }
    };
  }
  
  protected startPeriodicTasks(): void {
    // 健康检查定时器
    this.healthCheckTimer = setInterval(
      () => this.performHealthCheck(),
      this.config.healthCheckInterval
    );
    
    // 清理定时器
    this.cleanupTimer = setInterval(
      () => this.cleanupInactiveAgents(),
      this.config.cleanupInterval
    );
  }
  
  protected async cleanupInactiveAgents(): Promise<void> {
    const now = new Date();
    const timeout = this.config.inactiveAgentTimeout;
    
    for (const [agentId, agentInfo] of this.agents.entries()) {
      const timeSinceLastHeartbeat = now.getTime() - agentInfo.lastHeartbeat.getTime();
      if (timeSinceLastHeartbeat > timeout) {
        await this.unregister(agentId);
      }
    }
  }
  
  // 需要子类实现的其他抽象方法
  async updatePerformance(agentId: string, performance: Partial<AgentPerformance>): Promise<void> {
    throw new Error('Method not implemented');
  }
  
  async updateConfiguration(agentId: string, config: Partial<AgentConfiguration>): Promise<void> {
    throw new Error('Method not implemented');
  }
  
  async performHealthCheck(agentId?: string): Promise<HealthCheckReport> {
    throw new Error('Method not implemented');
  }
  
  setHealthCheckInterval(interval: number): void {
    throw new Error('Method not implemented');
  }
  
  async selectAgent(criteria: AgentCriteria, strategy?: LoadBalancingStrategy): Promise<AgentInfo | null> {
    throw new Error('Method not implemented');
  }
  
  async getLoadBalancingMetrics(): Promise<LoadBalancingMetrics> {
    throw new Error('Method not implemented');
  }
  
  async getRegistryMetrics(): Promise<RegistryMetrics> {
    return this.metrics;
  }
  
  async getAgentStatistics(agentId: string): Promise<AgentStatistics> {
    throw new Error('Method not implemented');
  }
  
  onAgentRegistered(callback: (agentInfo: AgentInfo) => void): void {
    this.on('agentRegistered', callback);
  }
  
  onAgentUnregistered(callback: (agentId: string) => void): void {
    this.on('agentUnregistered', callback);
  }
  
  onAgentStatusChanged(callback: (agentId: string, oldStatus: AgentStatus, newStatus: AgentStatus) => void): void {
    this.on('agentStatusChanged', callback);
  }
}

// ============================================================================
// 工厂接口
// ============================================================================

export interface AgentRegistryFactory {
  createRegistry(type: string, config: RegistryConfiguration): AgentRegistry;
  getSupportedTypes(): string[];
}

// ============================================================================
// 导出
// ============================================================================

export {
  AgentRegistry,
  BaseAgentRegistry,
  AgentRegistryFactory
};