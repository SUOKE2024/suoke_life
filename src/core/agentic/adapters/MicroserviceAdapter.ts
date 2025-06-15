/**
 * 微服务适配器
 * 将 Agentic AI 系统与现有微服务架构连接
 * 实现服务发现、负载均衡和故障转移
 */

import { EventEmitter } from 'events';
import {
  UnifiedAgentInterface,
  AgentType,
  AgentStatus,
  AgentRequest,
  AgentResponse,
  AgentConfiguration,
  AgentPerformance,
  HealthCheckResult
} from '../interfaces/UnifiedAgentInterface';

// ============================================================================
// 微服务适配器接口
// ============================================================================

export interface MicroserviceAdapter extends EventEmitter {
  // 服务发现
  discoverServices(): Promise<ServiceInfo[]>;
  getServiceByType(type: AgentType): Promise<ServiceInfo | null>;
  
  // 服务调用
  callService(serviceId: string, request: ServiceRequest): Promise<ServiceResponse>;
  callServiceWithRetry(serviceId: string, request: ServiceRequest, retryOptions?: RetryOptions): Promise<ServiceResponse>;
  
  // 健康检查
  checkServiceHealth(serviceId: string): Promise<ServiceHealthStatus>;
  checkAllServicesHealth(): Promise<ServiceHealthReport>;
  
  // 负载均衡
  selectService(criteria: ServiceSelectionCriteria): Promise<ServiceInfo | null>;
  
  // 配置管理
  updateServiceConfiguration(serviceId: string, config: any): Promise<void>;
  getServiceConfiguration(serviceId: string): Promise<any>;
}

// ============================================================================
// 服务信息定义
// ============================================================================

export interface ServiceInfo {
  id: string;
  name: string;
  type: AgentType;
  version: string;
  status: ServiceStatus;
  
  // 网络信息
  endpoints: ServiceEndpoint[];
  protocol: 'http' | 'grpc' | 'websocket';
  
  // 性能信息
  performance: ServicePerformance;
  capacity: ServiceCapacity;
  
  // 元数据
  metadata: Record<string, any>;
  tags: string[];
  
  // 注册信息
  registeredAt: Date;
  lastHeartbeat: Date;
  lastHealthCheck: Date;
}

export interface ServiceEndpoint {
  type: 'api' | 'grpc' | 'websocket' | 'health';
  url: string;
  port: number;
  path?: string;
  secure: boolean;
  authentication?: AuthenticationInfo;
}

export interface AuthenticationInfo {
  type: 'none' | 'basic' | 'bearer' | 'oauth' | 'api_key';
  credentials?: any;
  headers?: Record<string, string>;
}

export enum ServiceStatus {
  UNKNOWN = 'unknown',
  STARTING = 'starting',
  HEALTHY = 'healthy',
  DEGRADED = 'degraded',
  UNHEALTHY = 'unhealthy',
  STOPPING = 'stopping',
  STOPPED = 'stopped'
}

export interface ServicePerformance {
  averageResponseTime: number;  // ms
  throughput: number;          // requests/second
  errorRate: number;           // 0-1
  availability: number;        // 0-1
  lastUpdated: Date;
}

export interface ServiceCapacity {
  maxConcurrentRequests: number;
  currentLoad: number;         // 0-1
  queueLength: number;
  resourceUsage: {
    cpu: number;               // 0-1
    memory: number;            // 0-1
    network: number;           // 0-1
  };
}

// ============================================================================
// 请求和响应定义
// ============================================================================

export interface ServiceRequest {
  id: string;
  method: string;
  path: string;
  headers?: Record<string, string>;
  body?: any;
  timeout?: number;
  retryable?: boolean;
  priority?: 'low' | 'normal' | 'high' | 'urgent';
}

export interface ServiceResponse {
  requestId: string;
  status: number;
  headers?: Record<string, string>;
  body?: any;
  executionTime: number;
  error?: ServiceError;
}

export interface ServiceError {
  code: string;
  message: string;
  details?: any;
  retryable: boolean;
  retryAfter?: number;
}

// ============================================================================
// 重试和故障处理
// ============================================================================

export interface RetryOptions {
  maxAttempts: number;
  initialDelay: number;
  maxDelay: number;
  backoffMultiplier: number;
  jitterEnabled: boolean;
  retryableErrors?: string[];
}

export interface CircuitBreakerConfig {
  failureThreshold: number;
  recoveryTimeout: number;
  monitoringPeriod: number;
  minimumRequests: number;
}

export enum CircuitBreakerState {
  CLOSED = 'closed',
  OPEN = 'open',
  HALF_OPEN = 'half_open'
}

// ============================================================================
// 健康检查
// ============================================================================

export interface ServiceHealthStatus {
  serviceId: string;
  status: ServiceStatus;
  lastChecked: Date;
  responseTime: number;
  checks: HealthCheck[];
  issues: HealthIssue[];
}

export interface HealthCheck {
  name: string;
  status: 'pass' | 'fail' | 'warn';
  description?: string;
  observedValue?: any;
  observedUnit?: string;
  time: Date;
}

export interface HealthIssue {
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: 'connectivity' | 'performance' | 'resource' | 'configuration';
  description: string;
  impact: string;
  suggestedAction?: string;
}

export interface ServiceHealthReport {
  timestamp: Date;
  overallStatus: ServiceStatus;
  totalServices: number;
  healthyServices: number;
  degradedServices: number;
  unhealthyServices: number;
  serviceDetails: ServiceHealthStatus[];
  systemIssues: SystemIssue[];
}

export interface SystemIssue {
  type: 'connectivity' | 'performance' | 'capacity' | 'configuration';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  affectedServices: string[];
  suggestedAction: string;
}

// ============================================================================
// 服务选择和负载均衡
// ============================================================================

export interface ServiceSelectionCriteria {
  type?: AgentType;
  minPerformance?: Partial<ServicePerformance>;
  maxLoad?: number;
  requiredTags?: string[];
  excludeServices?: string[];
  preferredRegion?: string;
}

export enum LoadBalancingStrategy {
  ROUND_ROBIN = 'round_robin',
  LEAST_CONNECTIONS = 'least_connections',
  LEAST_RESPONSE_TIME = 'least_response_time',
  WEIGHTED_ROUND_ROBIN = 'weighted_round_robin',
  RANDOM = 'random',
  CONSISTENT_HASH = 'consistent_hash'
}

// ============================================================================
// 微服务智能体适配器
// ============================================================================

export class MicroserviceAgentAdapter extends EventEmitter implements UnifiedAgentInterface {
  private serviceInfo: ServiceInfo;
  private adapter: MicroserviceAdapter;
  private circuitBreaker: CircuitBreaker;
  private retryOptions: RetryOptions;
  
  constructor(
    serviceInfo: ServiceInfo,
    adapter: MicroserviceAdapter,
    options?: {
      retryOptions?: RetryOptions;
      circuitBreakerConfig?: CircuitBreakerConfig;
    }
  ) {
    super();
    this.serviceInfo = serviceInfo;
    this.adapter = adapter;
    this.retryOptions = options?.retryOptions || this.getDefaultRetryOptions();
    this.circuitBreaker = new CircuitBreaker(
      options?.circuitBreakerConfig || this.getDefaultCircuitBreakerConfig()
    );
  }
  
  // ============================================================================
  // UnifiedAgentInterface 实现
  // ============================================================================
  
  get id(): string {
    return this.serviceInfo.id;
  }
  
  get type(): AgentType {
    return this.serviceInfo.type;
  }
  
  get configuration(): AgentConfiguration {
    return this.convertServiceInfoToConfiguration(this.serviceInfo);
  }
  
  get status(): AgentStatus {
    return this.convertServiceStatusToAgentStatus(this.serviceInfo.status);
  }
  
  get performance(): AgentPerformance {
    return this.convertServicePerformanceToAgentPerformance(this.serviceInfo.performance);
  }
  
  async initialize(): Promise<void> {
    this.emit('initializing');
    // 微服务通常已经初始化，这里主要是建立连接
    await this.checkConnection();
    this.emit('initialized');
  }
  
  async start(): Promise<void> {
    this.emit('starting');
    // 微服务的启动由外部管理，这里主要是验证可用性
    const health = await this.adapter.checkServiceHealth(this.serviceInfo.id);
    if (health.status !== ServiceStatus.HEALTHY) {
      throw new Error(`Service ${this.serviceInfo.id} is not healthy`);
    }
    this.emit('started');
  }
  
  async stop(): Promise<void> {
    this.emit('stopping');
    // 微服务的停止由外部管理，这里主要是清理连接
    this.circuitBreaker.reset();
    this.emit('stopped');
  }
  
  async restart(): Promise<void> {
    await this.stop();
    await this.start();
  }
  
  async shutdown(): Promise<void> {
    await this.stop();
    this.removeAllListeners();
  }
  
  async process(request: AgentRequest): Promise<AgentResponse> {
    const startTime = Date.now();
    
    try {
      // 检查熔断器状态
      if (!this.circuitBreaker.canExecute()) {
        throw new Error('Circuit breaker is open');
      }
      
      // 转换请求格式
      const serviceRequest = this.convertAgentRequestToServiceRequest(request);
      
      // 调用微服务
      const serviceResponse = await this.adapter.callServiceWithRetry(
        this.serviceInfo.id,
        serviceRequest,
        this.retryOptions
      );
      
      // 记录成功
      this.circuitBreaker.recordSuccess();
      
      // 转换响应格式
      const agentResponse = this.convertServiceResponseToAgentResponse(
        serviceResponse,
        request.id,
        Date.now() - startTime
      );
      
      return agentResponse;
      
    } catch (error) {
      // 记录失败
      this.circuitBreaker.recordFailure();
      
      // 返回错误响应
      return {
        requestId: request.id,
        agentId: this.id,
        success: false,
        content: 'Service call failed',
        confidence: 0,
        executionTime: Date.now() - startTime,
        error: {
          code: 'SERVICE_ERROR',
          message: error instanceof Error ? error.message : 'Unknown error',
          recoverable: true,
          suggestedActions: ['Retry the request', 'Check service health']
        }
      };
    }
  }
  
  async *processStream(request: AgentRequest): AsyncGenerator<Partial<AgentResponse>> {
    // 微服务通常不支持流式响应，这里提供一个简单的实现
    const response = await this.process(request);
    yield response;
  }
  
  getStatus(): AgentStatus {
    return this.status;
  }
  
  getPerformance(): AgentPerformance {
    return this.performance;
  }
  
  async updateConfiguration(config: Partial<AgentConfiguration>): Promise<void> {
    // 将配置更新传递给微服务
    await this.adapter.updateServiceConfiguration(this.serviceInfo.id, config);
    this.emit('configurationUpdated', config);
  }
  
  async requestCollaboration(request: any): Promise<any> {
    throw new Error('Collaboration not supported by microservice adapter');
  }
  
  async joinCollaboration(sessionId: string): Promise<void> {
    throw new Error('Collaboration not supported by microservice adapter');
  }
  
  async leaveCollaboration(sessionId: string): Promise<void> {
    throw new Error('Collaboration not supported by microservice adapter');
  }
  
  async learn(feedback: any): Promise<void> {
    // 学习功能可以通过调用微服务的学习接口实现
    console.log('Learning feedback received:', feedback);
  }
  
  async adapt(context: any): Promise<void> {
    // 适应功能可以通过调用微服务的适应接口实现
    console.log('Adaptation context received:', context);
  }
  
  async healthCheck(): Promise<HealthCheckResult> {
    const healthStatus = await this.adapter.checkServiceHealth(this.serviceInfo.id);
    
    return {
      healthy: healthStatus.status === ServiceStatus.HEALTHY,
      status: this.convertServiceStatusToAgentStatus(healthStatus.status),
      issues: healthStatus.issues.map(issue => ({
        severity: issue.severity,
        category: issue.category,
        description: issue.description,
        impact: issue.impact,
        suggestedFix: issue.suggestedAction
      })),
      lastChecked: healthStatus.lastChecked
    };
  }
  
  async getMetrics(): Promise<any> {
    return {
      performance: this.performance,
      serviceInfo: this.serviceInfo,
      circuitBreakerState: this.circuitBreaker.getState()
    };
  }
  
  async exportState(): Promise<any> {
    return {
      serviceInfo: this.serviceInfo,
      circuitBreakerState: this.circuitBreaker.getState(),
      lastHealthCheck: new Date()
    };
  }
  
  async importState(state: any): Promise<void> {
    // 微服务的状态导入通常不需要实现
    console.log('State import not supported for microservice adapter');
  }
  
  // ============================================================================
  // 私有方法
  // ============================================================================
  
  private async checkConnection(): Promise<void> {
    const health = await this.adapter.checkServiceHealth(this.serviceInfo.id);
    if (health.status === ServiceStatus.UNHEALTHY) {
      throw new Error(`Cannot connect to service ${this.serviceInfo.id}`);
    }
  }
  
  private convertServiceInfoToConfiguration(serviceInfo: ServiceInfo): AgentConfiguration {
    return {
      id: serviceInfo.id,
      type: serviceInfo.type,
      name: serviceInfo.name,
      version: serviceInfo.version,
      description: `Microservice adapter for ${serviceInfo.name}`,
      capabilities: [], // 需要从服务元数据中提取
      specializations: [],
      maxConcurrentTasks: serviceInfo.capacity.maxConcurrentRequests,
      timeoutSettings: {
        defaultTimeout: 30000,
        maxTimeout: 60000,
        retryAttempts: 3
      },
      resourceLimits: {
        memory: 0,
        cpu: 0,
        storage: 0
      },
      communicationSettings: {
        protocols: [serviceInfo.protocol],
        endpoints: serviceInfo.endpoints.map(ep => ep.url),
        authentication: serviceInfo.endpoints[0]?.authentication
      }
    };
  }
  
  private convertServiceStatusToAgentStatus(serviceStatus: ServiceStatus): AgentStatus {
    switch (serviceStatus) {
      case ServiceStatus.HEALTHY:
        return AgentStatus.AVAILABLE;
      case ServiceStatus.DEGRADED:
        return AgentStatus.BUSY;
      case ServiceStatus.UNHEALTHY:
        return AgentStatus.ERROR;
      case ServiceStatus.STARTING:
        return AgentStatus.INITIALIZING;
      case ServiceStatus.STOPPING:
      case ServiceStatus.STOPPED:
        return AgentStatus.OFFLINE;
      default:
        return AgentStatus.OFFLINE;
    }
  }
  
  private convertServicePerformanceToAgentPerformance(servicePerf: ServicePerformance): AgentPerformance {
    return {
      taskCompletionRate: 1 - servicePerf.errorRate,
      averageResponseTime: servicePerf.averageResponseTime,
      qualityScore: servicePerf.availability,
      collaborationRating: 0.8, // 默认值
      userSatisfaction: 0.8, // 默认值
      learningRate: 0.1, // 默认值
      adaptabilityScore: 0.7, // 默认值
      lastEvaluated: servicePerf.lastUpdated
    };
  }
  
  private convertAgentRequestToServiceRequest(agentRequest: AgentRequest): ServiceRequest {
    return {
      id: agentRequest.id,
      method: 'POST',
      path: '/process',
      headers: {
        'Content-Type': 'application/json',
        'X-Request-Type': agentRequest.type,
        'X-Priority': agentRequest.priority
      },
      body: {
        content: agentRequest.content,
        context: agentRequest.context,
        constraints: agentRequest.constraints,
        metadata: agentRequest.metadata
      },
      timeout: 30000,
      retryable: true,
      priority: agentRequest.priority
    };
  }
  
  private convertServiceResponseToAgentResponse(
    serviceResponse: ServiceResponse,
    requestId: string,
    executionTime: number
  ): AgentResponse {
    const success = serviceResponse.status >= 200 && serviceResponse.status < 300;
    
    return {
      requestId,
      agentId: this.id,
      success,
      content: serviceResponse.body?.content || serviceResponse.body || '',
      data: serviceResponse.body?.data,
      confidence: serviceResponse.body?.confidence || (success ? 0.8 : 0.1),
      executionTime,
      recommendations: serviceResponse.body?.recommendations,
      followUpActions: serviceResponse.body?.followUpActions,
      metadata: {
        serviceResponse: {
          status: serviceResponse.status,
          headers: serviceResponse.headers
        }
      },
      error: serviceResponse.error ? {
        code: serviceResponse.error.code,
        message: serviceResponse.error.message,
        details: serviceResponse.error.details,
        recoverable: serviceResponse.error.retryable,
        suggestedActions: ['Retry the request']
      } : undefined
    };
  }
  
  private getDefaultRetryOptions(): RetryOptions {
    return {
      maxAttempts: 3,
      initialDelay: 1000,
      maxDelay: 10000,
      backoffMultiplier: 2,
      jitterEnabled: true,
      retryableErrors: ['TIMEOUT', 'CONNECTION_ERROR', 'SERVICE_UNAVAILABLE']
    };
  }
  
  private getDefaultCircuitBreakerConfig(): CircuitBreakerConfig {
    return {
      failureThreshold: 5,
      recoveryTimeout: 60000,
      monitoringPeriod: 10000,
      minimumRequests: 10
    };
  }
}

// ============================================================================
// 熔断器实现
// ============================================================================

class CircuitBreaker {
  private config: CircuitBreakerConfig;
  private state: CircuitBreakerState = CircuitBreakerState.CLOSED;
  private failureCount: number = 0;
  private lastFailureTime: number = 0;
  private requestCount: number = 0;
  
  constructor(config: CircuitBreakerConfig) {
    this.config = config;
  }
  
  canExecute(): boolean {
    const now = Date.now();
    
    switch (this.state) {
      case CircuitBreakerState.CLOSED:
        return true;
        
      case CircuitBreakerState.OPEN:
        if (now - this.lastFailureTime >= this.config.recoveryTimeout) {
          this.state = CircuitBreakerState.HALF_OPEN;
          this.requestCount = 0;
          return true;
        }
        return false;
        
      case CircuitBreakerState.HALF_OPEN:
        return this.requestCount < this.config.minimumRequests;
        
      default:
        return false;
    }
  }
  
  recordSuccess(): void {
    this.failureCount = 0;
    this.requestCount++;
    
    if (this.state === CircuitBreakerState.HALF_OPEN) {
      if (this.requestCount >= this.config.minimumRequests) {
        this.state = CircuitBreakerState.CLOSED;
      }
    }
  }
  
  recordFailure(): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();
    this.requestCount++;
    
    if (this.failureCount >= this.config.failureThreshold) {
      this.state = CircuitBreakerState.OPEN;
    }
  }
  
  getState(): CircuitBreakerState {
    return this.state;
  }
  
  reset(): void {
    this.state = CircuitBreakerState.CLOSED;
    this.failureCount = 0;
    this.requestCount = 0;
    this.lastFailureTime = 0;
  }
}

// ============================================================================
// 导出
// ============================================================================

export {
  MicroserviceAdapter,
  MicroserviceAgentAdapter,
  CircuitBreaker,
  ServiceInfo,
  ServiceRequest,
  ServiceResponse,
  ServiceHealthStatus,
  ServiceHealthReport
};