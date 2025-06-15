/**
 * 索克生活 Agentic AI 架构集成优化
 * 解决与现有 API Gateway 和 Communication Service 的冗余和耦合问题
 */

import { EventEmitter } from 'events';

// ============================================================================
// 架构集成接口定义
// ============================================================================

export interface ArchitectureIntegrationConfig {
  // 现有服务端点
  apiGateway: {
    endpoint: string;
    healthCheck: string;
    serviceDiscovery: string;
  };
  
  communicationService: {
    endpoint: string;
    messageBus: string;
    ragService: string;
    eventBus: string;
  };
  
  // 集成策略
  integrationStrategy: {
    useExistingMessageBus: boolean;
    useExistingServiceDiscovery: boolean;
    useExistingEventSystem: boolean;
    enableDirectServiceCalls: boolean;
  };
}

export interface ServiceAdapter {
  id: string;
  name: string;
  type: 'api-gateway' | 'communication-service' | 'business-service';
  endpoint: string;
  capabilities: string[];
  healthStatus: 'healthy' | 'unhealthy' | 'unknown';
}

// ============================================================================
// 架构集成管理器
// ============================================================================

export class ArchitectureIntegrationManager extends EventEmitter {
  private config: ArchitectureIntegrationConfig;
  private serviceAdapters: Map<string, ServiceAdapter> = new Map();
  private communicationAdapter: CommunicationServiceAdapter;
  private gatewayAdapter: APIGatewayAdapter;
  
  constructor(config: ArchitectureIntegrationConfig) {
    super();
    this.config = config;
    this.communicationAdapter = new CommunicationServiceAdapter(config.communicationService);
    this.gatewayAdapter = new APIGatewayAdapter(config.apiGateway);
  }

  /**
   * 初始化架构集成
   */
  async initialize(): Promise<void> {
    console.log('🔧 初始化架构集成...');
    
    // 1. 检查现有服务健康状态
    await this.checkExistingServices();
    
    // 2. 注册服务适配器
    await this.registerServiceAdapters();
    
    // 3. 配置集成策略
    await this.configureIntegrationStrategy();
    
    console.log('✅ 架构集成初始化完成');
  }

  /**
   * 检查现有服务状态
   */
  private async checkExistingServices(): Promise<void> {
    const services = [
      { name: 'API Gateway', adapter: this.gatewayAdapter },
      { name: 'Communication Service', adapter: this.communicationAdapter }
    ];

    for (const service of services) {
      try {
        const isHealthy = await service.adapter.healthCheck();
        console.log(`📊 ${service.name}: ${isHealthy ? '✅ 健康' : '❌ 不健康'}`);
      } catch (error) {
        console.warn(`⚠️ ${service.name} 健康检查失败:`, error);
      }
    }
  }

  /**
   * 注册服务适配器
   */
  private async registerServiceAdapters(): Promise<void> {
    // 注册API Gateway适配器
    this.serviceAdapters.set('api-gateway', {
      id: 'api-gateway',
      name: 'API Gateway',
      type: 'api-gateway',
      endpoint: this.config.apiGateway.endpoint,
      capabilities: ['routing', 'authentication', 'rate-limiting', 'load-balancing'],
      healthStatus: 'unknown'
    });

    // 注册Communication Service适配器
    this.serviceAdapters.set('communication-service', {
      id: 'communication-service',
      name: 'Communication Service',
      type: 'communication-service',
      endpoint: this.config.communicationService.endpoint,
      capabilities: ['message-bus', 'event-driven', 'rag-service'],
      healthStatus: 'unknown'
    });
  }

  /**
   * 配置集成策略
   */
  private async configureIntegrationStrategy(): Promise<void> {
    const strategy = this.config.integrationStrategy;
    
    console.log('🔄 配置集成策略:');
    console.log(`  - 使用现有消息总线: ${strategy.useExistingMessageBus ? '✅' : '❌'}`);
    console.log(`  - 使用现有服务发现: ${strategy.useExistingServiceDiscovery ? '✅' : '❌'}`);
    console.log(`  - 使用现有事件系统: ${strategy.useExistingEventSystem ? '✅' : '❌'}`);
    console.log(`  - 启用直接服务调用: ${strategy.enableDirectServiceCalls ? '✅' : '❌'}`);
  }

  /**
   * 获取优化后的工具调用策略
   */
  getOptimizedToolCallStrategy(): ToolCallStrategy {
    return new OptimizedToolCallStrategy(this.gatewayAdapter, this.communicationAdapter);
  }

  /**
   * 获取优化后的通信策略
   */
  getOptimizedCommunicationStrategy(): CommunicationStrategy {
    return new OptimizedCommunicationStrategy(this.communicationAdapter);
  }
}

// ============================================================================
// 服务适配器实现
// ============================================================================

export class APIGatewayAdapter {
  private config: ArchitectureIntegrationConfig['apiGateway'];
  
  constructor(config: ArchitectureIntegrationConfig['apiGateway']) {
    this.config = config;
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.config.endpoint}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * 通过API Gateway调用服务
   */
  async callService(serviceName: string, path: string, options: RequestInit = {}): Promise<Response> {
    const url = `${this.config.endpoint}/api/v1/proxy/${serviceName}${path}`;
    return fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
  }

  /**
   * 获取服务发现信息
   */
  async getServiceDiscovery(): Promise<ServiceDiscoveryInfo[]> {
    const response = await fetch(`${this.config.serviceDiscovery}`);
    return response.json();
  }
}

export class CommunicationServiceAdapter {
  private config: ArchitectureIntegrationConfig['communicationService'];
  
  constructor(config: ArchitectureIntegrationConfig['communicationService']) {
    this.config = config;
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.config.endpoint}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * 发布消息到消息总线
   */
  async publishMessage(topic: string, message: any): Promise<void> {
    await fetch(`${this.config.messageBus}/publish`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic, message })
    });
  }

  /**
   * 订阅消息总线主题
   */
  async subscribeToTopic(topic: string, callback: (message: any) => void): Promise<string> {
    // 实现WebSocket或SSE订阅
    const ws = new WebSocket(`${this.config.messageBus}/subscribe/${topic}`);
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      callback(message);
    };
    return `subscription-${Date.now()}`;
  }

  /**
   * 发布事件
   */
  async publishEvent(eventType: string, data: any): Promise<void> {
    await fetch(`${this.config.eventBus}/events`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event_type: eventType, data })
    });
  }

  /**
   * 调用RAG服务
   */
  async queryRAG(query: string, context?: any): Promise<any> {
    const response = await fetch(`${this.config.ragService}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, context })
    });
    return response.json();
  }
}

// ============================================================================
// 优化策略实现
// ============================================================================

export class OptimizedToolCallStrategy {
  constructor(
    private gatewayAdapter: APIGatewayAdapter,
    private communicationAdapter: CommunicationServiceAdapter
  ) {}

  /**
   * 智能工具调用 - 优先使用现有基础设施
   */
  async callTool(toolName: string, parameters: any): Promise<any> {
    // 1. 检查是否为内置工具
    if (this.isBuiltinTool(toolName)) {
      return this.callBuiltinTool(toolName, parameters);
    }

    // 2. 检查是否为RAG相关工具
    if (this.isRAGTool(toolName)) {
      return this.communicationAdapter.queryRAG(parameters.query, parameters.context);
    }

    // 3. 通过API Gateway调用外部服务
    const serviceName = this.extractServiceName(toolName);
    const path = this.extractServicePath(toolName, parameters);
    
    const response = await this.gatewayAdapter.callService(serviceName, path, {
      method: 'POST',
      body: JSON.stringify(parameters)
    });

    return response.json();
  }

  private isBuiltinTool(toolName: string): boolean {
    const builtinTools = ['五诊系统', '中医知识库', '健康评估'];
    return builtinTools.some(tool => toolName.includes(tool));
  }

  private isRAGTool(toolName: string): boolean {
    return toolName.includes('知识检索') || toolName.includes('文档查询');
  }

  private extractServiceName(toolName: string): string {
    // 根据工具名称映射到服务名称
    const serviceMapping: Record<string, string> = {
      '用户管理': 'user-management-service',
      '健康数据': 'unified-health-data-service',
      '诊断服务': 'diagnosis-services',
      '智能体': 'agent-services'
    };

    for (const [key, service] of Object.entries(serviceMapping)) {
      if (toolName.includes(key)) {
        return service;
      }
    }

    return 'default-service';
  }

  private extractServicePath(toolName: string, parameters: any): string {
    // 根据工具名称和参数构建API路径
    return `/api/v1/${toolName.toLowerCase().replace(/\s+/g, '-')}`;
  }

  private async callBuiltinTool(toolName: string, parameters: any): Promise<any> {
    // 调用内置工具逻辑
    return { result: `内置工具 ${toolName} 执行结果`, parameters };
  }
}

export class OptimizedCommunicationStrategy {
  constructor(private communicationAdapter: CommunicationServiceAdapter) {}

  /**
   * 智能体间通信 - 使用现有消息总线
   */
  async sendAgentMessage(fromAgent: string, toAgent: string, message: any): Promise<void> {
    const topic = `agent.${toAgent}.messages`;
    await this.communicationAdapter.publishMessage(topic, {
      from: fromAgent,
      to: toAgent,
      message,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * 广播消息给所有智能体
   */
  async broadcastToAgents(fromAgent: string, message: any): Promise<void> {
    const topic = 'agent.broadcast';
    await this.communicationAdapter.publishMessage(topic, {
      from: fromAgent,
      message,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * 发布智能体事件
   */
  async publishAgentEvent(eventType: string, agentId: string, data: any): Promise<void> {
    await this.communicationAdapter.publishEvent(`agent.${eventType}`, {
      agentId,
      data,
      timestamp: new Date().toISOString()
    });
  }
}

// ============================================================================
// 类型定义
// ============================================================================

export interface ServiceDiscoveryInfo {
  name: string;
  endpoint: string;
  health: 'healthy' | 'unhealthy';
  capabilities: string[];
}

export interface ToolCallStrategy {
  callTool(toolName: string, parameters: any): Promise<any>;
}

export interface CommunicationStrategy {
  sendAgentMessage(fromAgent: string, toAgent: string, message: any): Promise<void>;
  broadcastToAgents(fromAgent: string, message: any): Promise<void>;
  publishAgentEvent(eventType: string, agentId: string, data: any): Promise<void>;
}

// ============================================================================
// 导出
// ============================================================================

export default ArchitectureIntegrationManager;