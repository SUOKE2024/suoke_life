/**
 * 默认微服务适配器实现
 * 提供与现有微服务架构的具体集成
 */

import { EventEmitter } from 'events';
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import {
  MicroserviceAdapter,
  ServiceInfo,
  ServiceRequest,
  ServiceResponse,
  ServiceHealthStatus,
  ServiceHealthReport,
  ServiceSelectionCriteria,
  ServiceStatus,
  LoadBalancingStrategy,
  RetryOptions,
  ServiceError
} from './MicroserviceAdapter';
import { AgentType } from '../interfaces/UnifiedAgentInterface';

// ============================================================================
// 服务发现配置
// ============================================================================

export interface ServiceDiscoveryConfig {
  type: 'static' | 'consul' | 'eureka' | 'kubernetes';
  endpoints: string[];
  refreshInterval: number;
  timeout: number;
  authentication?: {
    type: 'none' | 'basic' | 'bearer';
    credentials?: any;
  };
}

export interface StaticServiceConfig {
  services: ServiceInfo[];
}

// ============================================================================
// 默认微服务适配器
// ============================================================================

export class DefaultMicroserviceAdapter extends EventEmitter implements MicroserviceAdapter {
  private services: Map<string, ServiceInfo> = new Map();
  private httpClient: AxiosInstance;
  private discoveryConfig: ServiceDiscoveryConfig;
  private loadBalancingStrategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN;
  private roundRobinCounters: Map<AgentType, number> = new Map();
  private refreshTimer?: NodeJS.Timeout;
  
  constructor(
    discoveryConfig: ServiceDiscoveryConfig,
    staticConfig?: StaticServiceConfig
  ) {
    super();
    this.discoveryConfig = discoveryConfig;
    this.httpClient = this.createHttpClient();
    
    // 如果提供了静态配置，先加载静态服务
    if (staticConfig) {
      this.loadStaticServices(staticConfig.services);
    }
    
    // 启动服务发现
    this.startServiceDiscovery();
  }
  
  // ============================================================================
  // 服务发现
  // ============================================================================
  
  async discoverServices(): Promise<ServiceInfo[]> {
    try {
      switch (this.discoveryConfig.type) {
        case 'static':
          return Array.from(this.services.values());
          
        case 'consul':
          return await this.discoverFromConsul();
          
        case 'eureka':
          return await this.discoverFromEureka();
          
        case 'kubernetes':
          return await this.discoverFromKubernetes();
          
        default:
          throw new Error(`Unsupported discovery type: ${this.discoveryConfig.type}`);
      }
    } catch (error) {
      console.error('Service discovery failed:', error);
      return Array.from(this.services.values());
    }
  }
  
  async getServiceByType(type: AgentType): Promise<ServiceInfo | null> {
    const services = Array.from(this.services.values())
      .filter(service => service.type === type && service.status === ServiceStatus.HEALTHY);
    
    if (services.length === 0) {
      return null;
    }
    
    return this.selectServiceByStrategy(services, type);
  }
  
  // ============================================================================
  // 服务调用
  // ============================================================================
  
  async callService(serviceId: string, request: ServiceRequest): Promise<ServiceResponse> {
    const service = this.services.get(serviceId);
    if (!service) {
      throw new Error(`Service not found: ${serviceId}`);
    }
    
    const endpoint = this.selectEndpoint(service, 'api');
    if (!endpoint) {
      throw new Error(`No API endpoint found for service: ${serviceId}`);
    }
    
    const startTime = Date.now();
    
    try {
      const config: AxiosRequestConfig = {
        method: request.method as any,
        url: `${endpoint.url}${request.path}`,
        headers: {
          ...request.headers,
          'X-Request-ID': request.id
        },
        data: request.body,
        timeout: request.timeout || 30000
      };
      
      // 添加认证信息
      if (endpoint.authentication) {
        this.addAuthentication(config, endpoint.authentication);
      }
      
      const response = await this.httpClient.request(config);
      
      return {
        requestId: request.id,
        status: response.status,
        headers: response.headers as Record<string, string>,
        body: response.data,
        executionTime: Date.now() - startTime
      };
      
    } catch (error: any) {
      const executionTime = Date.now() - startTime;
      
      if (error.response) {
        // HTTP 错误响应
        return {
          requestId: request.id,
          status: error.response.status,
          headers: error.response.headers,
          body: error.response.data,
          executionTime,
          error: {
            code: `HTTP_${error.response.status}`,
            message: error.response.data?.message || error.message,
            details: error.response.data,
            retryable: this.isRetryableHttpStatus(error.response.status)
          }
        };
      } else if (error.request) {
        // 网络错误
        throw new DefaultServiceError('NETWORK_ERROR', 'Network request failed', error, true);
      } else {
        // 其他错误
        throw new DefaultServiceError('REQUEST_ERROR', error.message, error, false);
      }
    }
  }
  
  async callServiceWithRetry(
    serviceId: string,
    request: ServiceRequest,
    retryOptions?: RetryOptions
  ): Promise<ServiceResponse> {
    const options = retryOptions || this.getDefaultRetryOptions();
    let lastError: any;
    
    for (let attempt = 1; attempt <= options.maxAttempts; attempt++) {
      try {
        const response = await this.callService(serviceId, request);
        
        // 检查是否需要重试
        if (response.error && !response.error.retryable) {
          return response;
        }
        
        if (response.status >= 200 && response.status < 300) {
          return response;
        }
        
        // 如果是最后一次尝试，返回响应
        if (attempt === options.maxAttempts) {
          return response;
        }
        
        lastError = response.error;
        
      } catch (error) {
        lastError = error;
        
        // 如果是最后一次尝试，抛出错误
        if (attempt === options.maxAttempts) {
          throw error;
        }
        
        // 检查是否可重试
        if (error instanceof DefaultServiceError && !error.retryable) {
          throw error;
        }
      }
      
      // 计算延迟时间
      const delay = this.calculateRetryDelay(attempt, options);
      await this.sleep(delay);
    }
    
    throw lastError;
  }
  
  // ============================================================================
  // 健康检查
  // ============================================================================
  
  async checkServiceHealth(serviceId: string): Promise<ServiceHealthStatus> {
    const service = this.services.get(serviceId);
    if (!service) {
      throw new Error(`Service not found: ${serviceId}`);
    }
    
    const healthEndpoint = this.selectEndpoint(service, 'health');
    if (!healthEndpoint) {
      // 如果没有专门的健康检查端点，使用 API 端点
      return await this.checkServiceHealthViaApi(service);
    }
    
    const startTime = Date.now();
    
    try {
      const response = await this.httpClient.get(healthEndpoint.url, {
        timeout: 5000
      });
      
      const responseTime = Date.now() - startTime;
      
      return {
        serviceId,
        status: this.parseHealthStatus(response.data),
        lastChecked: new Date(),
        responseTime,
        checks: this.parseHealthChecks(response.data),
        issues: this.parseHealthIssues(response.data)
      };
      
    } catch (error) {
      return {
        serviceId,
        status: ServiceStatus.UNHEALTHY,
        lastChecked: new Date(),
        responseTime: Date.now() - startTime,
        checks: [],
        issues: [{
          severity: 'critical',
          category: 'connectivity',
          description: `Health check failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
          impact: 'Service is not accessible'
        }]
      };
    }
  }
  
  async checkAllServicesHealth(): Promise<ServiceHealthReport> {
    const timestamp = new Date();
    const serviceDetails: ServiceHealthStatus[] = [];
    
    // 并行检查所有服务的健康状态
    const healthChecks = Array.from(this.services.keys()).map(async (serviceId) => {
      try {
        return await this.checkServiceHealth(serviceId);
      } catch (error) {
        return {
          serviceId,
          status: ServiceStatus.UNKNOWN,
          lastChecked: timestamp,
          responseTime: 0,
          checks: [],
          issues: [{
            severity: 'critical' as const,
            category: 'connectivity' as const,
            description: `Health check error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            impact: 'Cannot determine service health'
          }]
        };
      }
    });
    
    const results = await Promise.all(healthChecks);
    serviceDetails.push(...results);
    
    // 统计健康状态
    const totalServices = serviceDetails.length;
    const healthyServices = serviceDetails.filter(s => s.status === ServiceStatus.HEALTHY).length;
    const degradedServices = serviceDetails.filter(s => s.status === ServiceStatus.DEGRADED).length;
    const unhealthyServices = serviceDetails.filter(s => 
      s.status === ServiceStatus.UNHEALTHY || s.status === ServiceStatus.UNKNOWN
    ).length;
    
    // 确定整体状态
    let overallStatus: ServiceStatus;
    if (unhealthyServices > totalServices / 2) {
      overallStatus = ServiceStatus.UNHEALTHY;
    } else if (degradedServices > 0 || unhealthyServices > 0) {
      overallStatus = ServiceStatus.DEGRADED;
    } else {
      overallStatus = ServiceStatus.HEALTHY;
    }
    
    return {
      timestamp,
      overallStatus,
      totalServices,
      healthyServices,
      degradedServices,
      unhealthyServices,
      serviceDetails,
      systemIssues: this.analyzeSystemIssues(serviceDetails)
    };
  }
  
  // ============================================================================
  // 负载均衡
  // ============================================================================
  
  async selectService(criteria: ServiceSelectionCriteria): Promise<ServiceInfo | null> {
    let candidates = Array.from(this.services.values());
    
    // 按类型过滤
    if (criteria.type) {
      candidates = candidates.filter(service => service.type === criteria.type);
    }
    
    // 按状态过滤
    candidates = candidates.filter(service => service.status === ServiceStatus.HEALTHY);
    
    // 按负载过滤
    if (criteria.maxLoad !== undefined) {
      candidates = candidates.filter(service => service.capacity.currentLoad <= criteria.maxLoad);
    }
    
    // 按标签过滤
    if (criteria.requiredTags && criteria.requiredTags.length > 0) {
      candidates = candidates.filter(service => 
        criteria.requiredTags!.every(tag => service.tags.includes(tag))
      );
    }
    
    // 排除指定服务
    if (criteria.excludeServices && criteria.excludeServices.length > 0) {
      candidates = candidates.filter(service => 
        !criteria.excludeServices!.includes(service.id)
      );
    }
    
    // 按性能要求过滤
    if (criteria.minPerformance) {
      candidates = candidates.filter(service => {
        const perf = service.performance;
        const minPerf = criteria.minPerformance!;
        
        return (
          (!minPerf.averageResponseTime || perf.averageResponseTime <= minPerf.averageResponseTime) &&
          (!minPerf.throughput || perf.throughput >= minPerf.throughput) &&
          (!minPerf.errorRate || perf.errorRate <= minPerf.errorRate) &&
          (!minPerf.availability || perf.availability >= minPerf.availability)
        );
      });
    }
    
    if (candidates.length === 0) {
      return null;
    }
    
    return this.selectServiceByStrategy(candidates, criteria.type);
  }
  
  // ============================================================================
  // 配置管理
  // ============================================================================
  
  async updateServiceConfiguration(serviceId: string, config: any): Promise<void> {
    const service = this.services.get(serviceId);
    if (!service) {
      throw new Error(`Service not found: ${serviceId}`);
    }
    
    const endpoint = this.selectEndpoint(service, 'api');
    if (!endpoint) {
      throw new Error(`No API endpoint found for service: ${serviceId}`);
    }
    
    try {
      await this.httpClient.put(`${endpoint.url}/config`, config, {
        timeout: 10000
      });
      
      this.emit('serviceConfigurationUpdated', serviceId, config);
      
    } catch (error) {
      throw new Error(`Failed to update configuration for service ${serviceId}: ${error}`);
    }
  }
  
  async getServiceConfiguration(serviceId: string): Promise<any> {
    const service = this.services.get(serviceId);
    if (!service) {
      throw new Error(`Service not found: ${serviceId}`);
    }
    
    const endpoint = this.selectEndpoint(service, 'api');
    if (!endpoint) {
      throw new Error(`No API endpoint found for service: ${serviceId}`);
    }
    
    try {
      const response = await this.httpClient.get(`${endpoint.url}/config`, {
        timeout: 10000
      });
      
      return response.data;
      
    } catch (error) {
      throw new Error(`Failed to get configuration for service ${serviceId}: ${error}`);
    }
  }
  
  // ============================================================================
  // 私有方法
  // ============================================================================
  
  private createHttpClient(): AxiosInstance {
    return axios.create({
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'Suoke-Life-Agentic-System/1.0'
      }
    });
  }
  
  private loadStaticServices(services: ServiceInfo[]): void {
    for (const service of services) {
      this.services.set(service.id, service);
    }
    this.emit('servicesUpdated', Array.from(this.services.values()));
  }
  
  private startServiceDiscovery(): void {
    if (this.discoveryConfig.type === 'static') {
      return; // 静态配置不需要定期刷新
    }
    
    // 立即执行一次发现
    this.performServiceDiscovery();
    
    // 设置定期刷新
    this.refreshTimer = setInterval(() => {
      this.performServiceDiscovery();
    }, this.discoveryConfig.refreshInterval);
  }
  
  private async performServiceDiscovery(): Promise<void> {
    try {
      const discoveredServices = await this.discoverServices();
      
      // 更新服务列表
      const newServices = new Map<string, ServiceInfo>();
      for (const service of discoveredServices) {
        newServices.set(service.id, service);
      }
      
      // 检查变化
      const added: ServiceInfo[] = [];
      const removed: string[] = [];
      const updated: ServiceInfo[] = [];
      
      // 检查新增和更新的服务
      for (const [id, service] of newServices) {
        const existing = this.services.get(id);
        if (!existing) {
          added.push(service);
        } else if (this.hasServiceChanged(existing, service)) {
          updated.push(service);
        }
      }
      
      // 检查移除的服务
      for (const id of this.services.keys()) {
        if (!newServices.has(id)) {
          removed.push(id);
        }
      }
      
      // 应用变化
      this.services = newServices;
      
      // 发出事件
      if (added.length > 0) {
        this.emit('servicesAdded', added);
      }
      if (removed.length > 0) {
        this.emit('servicesRemoved', removed);
      }
      if (updated.length > 0) {
        this.emit('servicesUpdated', updated);
      }
      
    } catch (error) {
      console.error('Service discovery failed:', error);
      this.emit('discoveryError', error);
    }
  }
  
  private async discoverFromConsul(): Promise<ServiceInfo[]> {
    // Consul 服务发现实现
    const services: ServiceInfo[] = [];
    
    for (const endpoint of this.discoveryConfig.endpoints) {
      try {
        const response = await this.httpClient.get(`${endpoint}/v1/catalog/services`);
        const consulServices = response.data;
        
        for (const [serviceName, tags] of Object.entries(consulServices)) {
          const serviceResponse = await this.httpClient.get(
            `${endpoint}/v1/catalog/service/${serviceName}`
          );
          
          for (const instance of serviceResponse.data) {
            const service = this.convertConsulServiceToServiceInfo(instance, tags as string[]);
            if (service) {
              services.push(service);
            }
          }
        }
      } catch (error) {
        console.error(`Failed to discover from Consul endpoint ${endpoint}:`, error);
      }
    }
    
    return services;
  }
  
  private async discoverFromEureka(): Promise<ServiceInfo[]> {
    // Eureka 服务发现实现
    const services: ServiceInfo[] = [];
    
    for (const endpoint of this.discoveryConfig.endpoints) {
      try {
        const response = await this.httpClient.get(`${endpoint}/eureka/apps`, {
          headers: {
            'Accept': 'application/json'
          }
        });
        
        const applications = response.data.applications?.application || [];
        
        for (const app of applications) {
          const instances = Array.isArray(app.instance) ? app.instance : [app.instance];
          
          for (const instance of instances) {
            const service = this.convertEurekaInstanceToServiceInfo(instance);
            if (service) {
              services.push(service);
            }
          }
        }
      } catch (error) {
        console.error(`Failed to discover from Eureka endpoint ${endpoint}:`, error);
      }
    }
    
    return services;
  }
  
  private async discoverFromKubernetes(): Promise<ServiceInfo[]> {
    // Kubernetes 服务发现实现
    const services: ServiceInfo[] = [];
    
    // 这里需要实现 Kubernetes API 调用
    // 通常通过 kubectl proxy 或者直接调用 Kubernetes API
    
    return services;
  }
  
  private convertConsulServiceToServiceInfo(consulService: any, tags: string[]): ServiceInfo | null {
    try {
      // 从标签中提取智能体类型
      const agentTypeTag = tags.find(tag => tag.startsWith('agent-type:'));
      if (!agentTypeTag) {
        return null; // 不是智能体服务
      }
      
      const agentType = agentTypeTag.split(':')[1] as AgentType;
      
      return {
        id: `${consulService.ServiceName}-${consulService.ServiceID}`,
        name: consulService.ServiceName,
        type: agentType,
        version: consulService.ServiceMeta?.version || '1.0.0',
        status: consulService.ServiceMeta?.status === 'healthy' ? ServiceStatus.HEALTHY : ServiceStatus.UNKNOWN,
        endpoints: [{
          type: 'api',
          url: `http://${consulService.ServiceAddress}:${consulService.ServicePort}`,
          port: consulService.ServicePort,
          secure: false
        }],
        protocol: 'http',
        performance: {
          averageResponseTime: 0,
          throughput: 0,
          errorRate: 0,
          availability: 1,
          lastUpdated: new Date()
        },
        capacity: {
          maxConcurrentRequests: 100,
          currentLoad: 0,
          queueLength: 0,
          resourceUsage: {
            cpu: 0,
            memory: 0,
            network: 0
          }
        },
        metadata: consulService.ServiceMeta || {},
        tags,
        registeredAt: new Date(),
        lastHeartbeat: new Date(),
        lastHealthCheck: new Date()
      };
    } catch (error) {
      console.error('Failed to convert Consul service:', error);
      return null;
    }
  }
  
  private convertEurekaInstanceToServiceInfo(eurekaInstance: any): ServiceInfo | null {
    try {
      // 从元数据中提取智能体类型
      const agentType = eurekaInstance.metadata?.['agent-type'] as AgentType;
      if (!agentType) {
        return null; // 不是智能体服务
      }
      
      return {
        id: `${eurekaInstance.app}-${eurekaInstance.instanceId}`,
        name: eurekaInstance.app,
        type: agentType,
        version: eurekaInstance.metadata?.version || '1.0.0',
        status: eurekaInstance.status === 'UP' ? ServiceStatus.HEALTHY : ServiceStatus.UNHEALTHY,
        endpoints: [{
          type: 'api',
          url: `${eurekaInstance.homePageUrl}`,
          port: eurekaInstance.port?.$,
          secure: eurekaInstance.securePort?.['@enabled'] === 'true'
        }],
        protocol: 'http',
        performance: {
          averageResponseTime: 0,
          throughput: 0,
          errorRate: 0,
          availability: 1,
          lastUpdated: new Date()
        },
        capacity: {
          maxConcurrentRequests: 100,
          currentLoad: 0,
          queueLength: 0,
          resourceUsage: {
            cpu: 0,
            memory: 0,
            network: 0
          }
        },
        metadata: eurekaInstance.metadata || {},
        tags: [],
        registeredAt: new Date(),
        lastHeartbeat: new Date(),
        lastHealthCheck: new Date()
      };
    } catch (error) {
      console.error('Failed to convert Eureka instance:', error);
      return null;
    }
  }
  
  private selectServiceByStrategy(services: ServiceInfo[], type?: AgentType): ServiceInfo {
    switch (this.loadBalancingStrategy) {
      case LoadBalancingStrategy.ROUND_ROBIN:
        return this.selectByRoundRobin(services, type);
        
      case LoadBalancingStrategy.LEAST_CONNECTIONS:
        return this.selectByLeastConnections(services);
        
      case LoadBalancingStrategy.LEAST_RESPONSE_TIME:
        return this.selectByLeastResponseTime(services);
        
      case LoadBalancingStrategy.RANDOM:
        return services[Math.floor(Math.random() * services.length)];
        
      default:
        return services[0];
    }
  }
  
  private selectByRoundRobin(services: ServiceInfo[], type?: AgentType): ServiceInfo {
    if (!type) {
      return services[0];
    }
    
    const counter = this.roundRobinCounters.get(type) || 0;
    const index = counter % services.length;
    this.roundRobinCounters.set(type, counter + 1);
    
    return services[index];
  }
  
  private selectByLeastConnections(services: ServiceInfo[]): ServiceInfo {
    return services.reduce((best, current) => 
      current.capacity.currentLoad < best.capacity.currentLoad ? current : best
    );
  }
  
  private selectByLeastResponseTime(services: ServiceInfo[]): ServiceInfo {
    return services.reduce((best, current) => 
      current.performance.averageResponseTime < best.performance.averageResponseTime ? current : best
    );
  }
  
  private selectEndpoint(service: ServiceInfo, type: string): any {
    return service.endpoints.find(endpoint => endpoint.type === type);
  }
  
  private addAuthentication(config: AxiosRequestConfig, auth: any): void {
    switch (auth.type) {
      case 'basic':
        config.auth = auth.credentials;
        break;
        
      case 'bearer':
        config.headers = {
          ...config.headers,
          'Authorization': `Bearer ${auth.credentials.token}`
        };
        break;
        
      case 'api_key':
        config.headers = {
          ...config.headers,
          ...auth.headers
        };
        break;
    }
  }
  
  private isRetryableHttpStatus(status: number): boolean {
    return status >= 500 || status === 408 || status === 429;
  }
  
  private getDefaultRetryOptions(): RetryOptions {
    return {
      maxAttempts: 3,
      initialDelay: 1000,
      maxDelay: 10000,
      backoffMultiplier: 2,
      jitterEnabled: true,
      retryableErrors: ['TIMEOUT', 'NETWORK_ERROR', 'SERVICE_UNAVAILABLE']
    };
  }
  
  private calculateRetryDelay(attempt: number, options: RetryOptions): number {
    let delay = options.initialDelay * Math.pow(options.backoffMultiplier, attempt - 1);
    delay = Math.min(delay, options.maxDelay);
    
    if (options.jitterEnabled) {
      delay = delay * (0.5 + Math.random() * 0.5);
    }
    
    return delay;
  }
  
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  private async checkServiceHealthViaApi(service: ServiceInfo): Promise<ServiceHealthStatus> {
    const endpoint = this.selectEndpoint(service, 'api');
    if (!endpoint) {
      throw new Error(`No API endpoint found for service: ${service.id}`);
    }
    
    const startTime = Date.now();
    
    try {
      await this.httpClient.get(`${endpoint.url}/ping`, {
        timeout: 5000
      });
      
      return {
        serviceId: service.id,
        status: ServiceStatus.HEALTHY,
        lastChecked: new Date(),
        responseTime: Date.now() - startTime,
        checks: [{
          name: 'api_ping',
          status: 'pass',
          description: 'API endpoint is responding',
          time: new Date()
        }],
        issues: []
      };
      
    } catch (error) {
      return {
        serviceId: service.id,
        status: ServiceStatus.UNHEALTHY,
        lastChecked: new Date(),
        responseTime: Date.now() - startTime,
        checks: [{
          name: 'api_ping',
          status: 'fail',
          description: 'API endpoint is not responding',
          time: new Date()
        }],
        issues: [{
          severity: 'critical',
          category: 'connectivity',
          description: `API ping failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
          impact: 'Service is not accessible via API'
        }]
      };
    }
  }
  
  private parseHealthStatus(healthData: any): ServiceStatus {
    if (healthData.status === 'UP' || healthData.status === 'healthy') {
      return ServiceStatus.HEALTHY;
    } else if (healthData.status === 'DEGRADED' || healthData.status === 'degraded') {
      return ServiceStatus.DEGRADED;
    } else {
      return ServiceStatus.UNHEALTHY;
    }
  }
  
  private parseHealthChecks(healthData: any): any[] {
    return healthData.checks || [];
  }
  
  private parseHealthIssues(healthData: any): any[] {
    return healthData.issues || [];
  }
  
  private hasServiceChanged(existing: ServiceInfo, updated: ServiceInfo): boolean {
    return (
      existing.status !== updated.status ||
      existing.version !== updated.version ||
      JSON.stringify(existing.endpoints) !== JSON.stringify(updated.endpoints)
    );
  }
  
  private analyzeSystemIssues(serviceDetails: ServiceHealthStatus[]): any[] {
    const issues: any[] = [];
    
    const unhealthyServices = serviceDetails.filter(s => 
      s.status === ServiceStatus.UNHEALTHY || s.status === ServiceStatus.UNKNOWN
    );
    
    if (unhealthyServices.length > serviceDetails.length / 2) {
      issues.push({
        type: 'connectivity',
        severity: 'critical',
        description: 'More than half of the services are unhealthy',
        affectedServices: unhealthyServices.map(s => s.serviceId),
        suggestedAction: 'Check network connectivity and service infrastructure'
      });
    }
    
    return issues;
  }
  
  // ============================================================================
  // 清理
  // ============================================================================
  
  destroy(): void {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
    }
    this.removeAllListeners();
  }
}

// ============================================================================
// 服务错误类
// ============================================================================

export class DefaultServiceError extends Error {
  public readonly code: string;
  public readonly details: any;
  public readonly retryable: boolean;
  
  constructor(code: string, message: string, details?: any, retryable: boolean = false) {
    super(message);
    this.name = 'DefaultServiceError';
    this.code = code;
    this.details = details;
    this.retryable = retryable;
  }
}

// ============================================================================
// 导出
// ============================================================================

export {
  DefaultMicroserviceAdapter,
  ServiceDiscoveryConfig,
  StaticServiceConfig,
  DefaultServiceError
};