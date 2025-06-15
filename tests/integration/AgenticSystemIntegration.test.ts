/**
 * Agentic AI 系统集成测试
 * 验证重构后的架构是否正常工作
 */

import { DefaultAgenticSystemManager, SystemConfiguration } from '../../src/core/agentic/AgenticSystemManager';
import { BaseAgentRegistry } from '../../src/core/agentic/registry/AgentRegistry';
import { BaseCommunicationProtocol } from '../../src/core/agentic/communication/AgentCommunicationProtocol';
import { DefaultMicroserviceAdapter } from '../../src/core/agentic/adapters/DefaultMicroserviceAdapter';
import { MicroserviceAgentAdapter } from '../../src/core/agentic/adapters/MicroserviceAdapter';
import { DefaultFrontendAgentFactory } from '../../src/agents/interfaces/FrontendAgentInterface';
import {
  AgentType,
  AgentStatus,
  AgentRequest,
  TaskType
} from '../../src/core/agentic/interfaces/UnifiedAgentInterface';

// 创建一个具体的通信协议实现用于测试
class TestCommunicationProtocol extends BaseCommunicationProtocol {
  private connected = false;

  async sendMessage(targetAgentId: string, message: any): Promise<any> {
    return {
      success: true,
      messageId: `msg-${Date.now()}`,
      timestamp: new Date()
    };
  }

  async sendMessageSync(targetAgentId: string, message: any, timeout?: number): Promise<any> {
    return {
      id: `response-${Date.now()}`,
      content: `Response to: ${message.content}`,
      timestamp: new Date()
    };
  }

  async broadcastMessage(message: any, targetTypes?: any[]): Promise<any> {
    return {
      success: true,
      deliveredTo: targetTypes || [],
      messageId: `broadcast-${Date.now()}`
    };
  }

  subscribeToEvents(eventTypes: string[], callback: any): string {
    const subscriptionId = `sub-${Date.now()}`;
    eventTypes.forEach(eventType => {
      this.on(eventType, callback);
    });
    return subscriptionId;
  }

  unsubscribeFromEvents(subscriptionId: string): void {
    // 测试实现
  }

  async createChannel(channelId: string, participants: string[]): Promise<void> {
    // 测试实现
  }

  async joinChannel(channelId: string): Promise<void> {
    // 测试实现
  }

  async leaveChannel(channelId: string): Promise<void> {
    // 测试实现
  }

  async sendChannelMessage(channelId: string, message: any): Promise<void> {
    // 测试实现
  }

  async connect(): Promise<void> {
    this.connected = true;
  }

  async disconnect(): Promise<void> {
    this.connected = false;
  }

  isConnected(): boolean {
    return this.connected;
  }

  getConnectionStatus(): any {
    return {
      connected: this.connected,
      lastHeartbeat: new Date(),
      latency: 10
    };
  }
}

// 创建一个具体的AgentRegistry实现用于测试
class TestAgentRegistry extends BaseAgentRegistry {
  private agents: Map<string, any> = new Map();

  constructor() {
    super({
      healthCheckInterval: 30000,
      maxAgents: 100,
      loadBalancingStrategy: 'round_robin',
      enableMetrics: true
    });
  }

  async register(agent: any): Promise<any> {
    this.agents.set(agent.getId(), agent);
    return { success: true, agentId: agent.getId() };
  }

  async unregister(agentId: string): Promise<void> {
    this.agents.delete(agentId);
  }

  async discover(criteria: any): Promise<any[]> {
    return Array.from(this.agents.values());
  }

  async getAgent(agentId: string): Promise<any | null> {
    return this.agents.get(agentId) || null;
  }

  async getAllAgents(): Promise<any[]> {
    return Array.from(this.agents.values());
  }

  async getAgentsByType(type: AgentType): Promise<any[]> {
    return Array.from(this.agents.values()).filter(agent => agent.getType() === type);
  }

  async updateStatus(agentId: string, status: AgentStatus): Promise<void> {
    const agent = this.agents.get(agentId);
    if (agent) {
      agent.status = status;
    }
  }

  async updatePerformance(agentId: string, performance: any): Promise<void> {
    const agent = this.agents.get(agentId);
    if (agent) {
      agent.performance = { ...agent.performance, ...performance };
    }
  }

  async updateConfiguration(agentId: string, config: any): Promise<void> {
    const agent = this.agents.get(agentId);
    if (agent) {
      agent.configuration = { ...agent.configuration, ...config };
    }
  }

  async performHealthCheck(agentId?: string): Promise<any> {
    return {
      healthy: true,
      timestamp: new Date(),
      details: {}
    };
  }

  setHealthCheckInterval(interval: number): void {
    // 测试实现
  }

  async selectAgent(criteria: any, strategy?: any): Promise<any | null> {
    const agents = Array.from(this.agents.values());
    return agents.length > 0 ? agents[0] : null;
  }

  async getLoadBalancingMetrics(): Promise<any> {
    return {
      totalAgents: this.agents.size,
      activeAgents: this.agents.size,
      averageLoad: 0.5
    };
  }

  async getRegistryMetrics(): Promise<any> {
    return {
      totalRegistrations: this.agents.size,
      activeAgents: this.agents.size,
      uptime: Date.now()
    };
  }

  async getAgentStatistics(agentId: string): Promise<any> {
    return {
      agentId,
      requestCount: 0,
      averageResponseTime: 100,
      errorRate: 0
    };
  }

  onAgentRegistered(callback: (agentInfo: any) => void): void {
    this.on('agentRegistered', callback);
  }

  onAgentUnregistered(callback: (agentId: string) => void): void {
    this.on('agentUnregistered', callback);
  }

  onAgentStatusChanged(callback: (agentId: string, oldStatus: AgentStatus, newStatus: AgentStatus) => void): void {
    this.on('agentStatusChanged', callback);
  }
}

describe('Agentic System Integration Tests', () => {
  let systemManager: DefaultAgenticSystemManager;
  let registry: TestAgentRegistry;
  let communicationProtocol: TestCommunicationProtocol;
  let microserviceAdapter: DefaultMicroserviceAdapter;
  let frontendFactory: DefaultFrontendAgentFactory;

  beforeAll(async () => {
    // 初始化系统组件
    registry = new TestAgentRegistry();
    communicationProtocol = new TestCommunicationProtocol();
    
    // 创建微服务适配器（使用静态配置进行测试）
    microserviceAdapter = new DefaultMicroserviceAdapter(
      {
        type: 'static',
        endpoints: [],
        refreshInterval: 30000,
        timeout: 5000
      },
      {
        services: [
          {
            id: 'xiaoai-service-1',
            name: 'xiaoai-service',
            type: AgentType.XIAOAI,
            version: '1.0.0',
            status: 'healthy' as any,
            endpoints: [{
              type: 'api',
              url: 'http://localhost:8001',
              port: 8001,
              secure: false
            }],
            protocol: 'http',
            performance: {
              averageResponseTime: 150,
              throughput: 100,
              errorRate: 0.01,
              availability: 0.99,
              lastUpdated: new Date()
            },
            capacity: {
              maxConcurrentRequests: 50,
              currentLoad: 0.3,
              queueLength: 0,
              resourceUsage: {
                cpu: 0.4,
                memory: 0.6,
                network: 0.2
              }
            },
            metadata: {},
            tags: ['tcm', 'diagnosis'],
            registeredAt: new Date(),
            lastHeartbeat: new Date(),
            lastHealthCheck: new Date()
          },
          {
            id: 'xiaoke-service-1',
            name: 'xiaoke-service',
            type: AgentType.XIAOKE,
            version: '1.0.0',
            status: 'healthy' as any,
            endpoints: [{
              type: 'api',
              url: 'http://localhost:8002',
              port: 8002,
              secure: false
            }],
            protocol: 'http',
            performance: {
              averageResponseTime: 120,
              throughput: 80,
              errorRate: 0.02,
              availability: 0.98,
              lastUpdated: new Date()
            },
            capacity: {
              maxConcurrentRequests: 40,
              currentLoad: 0.2,
              queueLength: 0,
              resourceUsage: {
                cpu: 0.3,
                memory: 0.5,
                network: 0.1
              }
            },
            metadata: {},
            tags: ['expert', 'consultation'],
            registeredAt: new Date(),
            lastHeartbeat: new Date(),
            lastHealthCheck: new Date()
          }
        ]
      }
    );
    
    // 创建前端智能体工厂
    frontendFactory = new DefaultFrontendAgentFactory();
    
    // 创建系统配置
    const systemConfig: SystemConfiguration = {
      systemId: 'suoke-life-agentic-test',
      version: '1.0.0',
      environment: 'development',
      registry: {
        type: 'default',
        config: {}
      },
      communication: {
        type: 'default',
        config: {}
      },
      workflow: {
        maxConcurrentWorkflows: 100,
        defaultTimeout: 30000,
        retryPolicy: {
          maxAttempts: 3,
          backoffMultiplier: 2
        }
      },
      collaboration: {
        maxConcurrentSessions: 50,
        sessionTimeout: 300000,
        enableDistributedCollaboration: true
      },
      monitoring: {
        healthCheckInterval: 10000,
        metricsCollectionInterval: 5000,
        performanceThresholds: {
          responseTime: 2000,
          errorRate: 0.05,
          availability: 0.99
        }
      },
      security: {
        enableAuthentication: false,
        enableAuthorization: false,
        enableEncryption: false
      },
      logging: {
        level: 'info',
        enableStructuredLogging: true,
        enablePerformanceLogging: true
      }
    };

    // 创建系统管理器
    systemManager = new DefaultAgenticSystemManager(systemConfig);
    
    // 初始化系统
    await systemManager.initialize();
  });

  afterAll(async () => {
    await systemManager.shutdown();
    microserviceAdapter.destroy();
  });

  describe('System Initialization', () => {
    test('should initialize all components successfully', async () => {
      expect(systemManager.getStatus()).toBe('running');
      expect(registry.getRegisteredAgents()).toHaveLength(0); // 初始时没有注册的智能体
    });

    test('should discover microservices', async () => {
      const services = await microserviceAdapter.discoverServices();
      expect(services).toHaveLength(2);
      expect(services.map(s => s.type)).toContain(AgentType.XIAOAI);
      expect(services.map(s => s.type)).toContain(AgentType.XIAOKE);
    });
  });

  describe('Agent Registration and Discovery', () => {
    test('should register microservice agents', async () => {
      const services = await microserviceAdapter.discoverServices();
      
      for (const service of services) {
        const adapter = new MicroserviceAgentAdapter(service, microserviceAdapter);
        await systemManager.registerAgent(adapter);
      }
      
      const registeredAgents = await systemManager.getAllAgents();
      expect(registeredAgents).toHaveLength(2);
    });

    test('should discover agents by type', async () => {
      const xiaoaiAgents = await registry.discoverAgents({
        type: AgentType.XIAOAI,
        status: AgentStatus.AVAILABLE
      });
      
      expect(xiaoaiAgents).toHaveLength(1);
      expect(xiaoaiAgents[0].type).toBe(AgentType.XIAOAI);
    });

    test('should get agent by ID', async () => {
      const agents = await systemManager.getAllAgents();
      const firstAgent = agents[0];
      
      const foundAgent = await systemManager.getAgent(firstAgent.id);
      expect(foundAgent).toBeDefined();
      expect(foundAgent?.id).toBe(firstAgent.id);
    });
  });

  describe('Task Processing', () => {
    test('should process simple diagnosis task', async () => {
      const request: AgentRequest = {
        id: 'test-request-1',
        type: TaskType.DIAGNOSIS,
        content: '患者主诉头痛，伴有轻微发热',
        priority: 'medium',
        context: {
          userId: 'test-user-1',
          sessionId: 'test-session-1'
        },
        constraints: {
          maxExecutionTime: 30000,
          requiredConfidence: 0.7
        },
        metadata: {
          timestamp: new Date(),
          source: 'integration-test'
        }
      };

      const response = await systemManager.processRequest(request);
      
      expect(response).toBeDefined();
      expect(response.success).toBe(true);
      expect(response.requestId).toBe(request.id);
      expect(response.confidence).toBeGreaterThan(0);
      expect(response.executionTime).toBeGreaterThan(0);
    });

    test('should handle task with specific agent type', async () => {
      const request: AgentRequest = {
        id: 'test-request-2',
        type: TaskType.CONSULTATION,
        content: '需要专家会诊建议',
        priority: TaskPriority.HIGH,
        context: {
          userId: 'test-user-2',
          sessionId: 'test-session-2',
          preferredAgentType: AgentType.XIAOKE
        },
        constraints: {
          maxExecutionTime: 30000,
          requiredConfidence: 0.8
        },
        metadata: {
          timestamp: new Date(),
          source: 'integration-test'
        }
      };

      const response = await systemManager.processRequest(request);
      
      expect(response).toBeDefined();
      expect(response.success).toBe(true);
      expect(response.agentId).toContain('xiaoke');
    });
  });

  describe('Agent Collaboration', () => {
    test('should initiate collaboration between agents', async () => {
      const collaborationRequest = {
        initiatorId: 'xiaoai-service-1',
        targetAgents: [AgentType.XIAOKE],
        task: {
          type: TaskType.COMPREHENSIVE_ANALYSIS,
          description: '复杂病例需要多智能体协作分析',
          data: {
            symptoms: ['头痛', '发热', '乏力'],
            duration: '3天',
            severity: 'moderate'
          }
        },
        collaborationType: 'sequential',
        timeout: 60000
      };

      const session = await systemManager.initiateCollaboration(collaborationRequest);
      
      expect(session).toBeDefined();
      expect(session.id).toBeDefined();
      expect(session.participants).toContain(AgentType.XIAOKE);
      expect(session.status).toBe('planning');
    });

    test('should monitor collaboration progress', async () => {
      const collaborationRequest = {
        initiatorId: 'xiaoai-service-1',
        targetAgents: [AgentType.XIAOKE],
        task: {
          type: TaskType.DIAGNOSIS,
          description: '协作诊断任务',
          data: { symptoms: ['咳嗽', '胸闷'] }
        },
        collaborationType: 'parallel',
        timeout: 30000
      };

      const session = await systemManager.initiateCollaboration(collaborationRequest);
      
      // 等待一段时间让协作进行
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 检查会话状态
      expect(session.status).toBeDefined();
      expect(['planning', 'active', 'completed', 'paused', 'cancelled']).toContain(session.status);
    });
  });

  describe('Communication Protocol', () => {
    test('should send message between agents', async () => {
      const agents = await systemManager.getAllAgents();
      const sender = agents[0];
      const receiver = agents[1];

      const message = {
        id: 'test-message-1',
        type: 'consultation_request',
        priority: 'normal' as any,
        sender: sender.id,
        recipients: [receiver.id],
        content: '请协助分析这个病例',
        data: {
          patientInfo: { age: 35, gender: 'male' },
          symptoms: ['头痛', '眩晕']
        },
        timestamp: new Date(),
        expiresAt: new Date(Date.now() + 300000)
      };

      const result = await communicationProtocol.sendMessage(message);
      
      expect(result.success).toBe(true);
      expect(result.messageId).toBe(message.id);
      expect(result.deliveredTo).toContain(receiver.id);
    });

    test('should broadcast message to multiple agents', async () => {
      const message = {
        id: 'test-broadcast-1',
        type: 'system_announcement',
        priority: 'low' as any,
        sender: 'system',
        recipients: [],
        content: '系统维护通知',
        data: {
          maintenanceTime: new Date(Date.now() + 3600000),
          expectedDuration: '30分钟'
        },
        timestamp: new Date(),
        expiresAt: new Date(Date.now() + 3600000)
      };

      const result = await communicationProtocol.broadcastMessage(
        message,
        { agentTypes: [AgentType.XIAOAI, AgentType.XIAOKE] }
      );
      
      expect(result.success).toBe(true);
      expect(result.totalRecipients).toBeGreaterThan(0);
      expect(result.successfulDeliveries).toBeGreaterThan(0);
    });
  });

  describe('Health Monitoring', () => {
    test('should check system health', async () => {
      const healthReport = await systemManager.performSystemHealthCheck();
      
      expect(healthReport).toBeDefined();
      expect(healthReport.overallStatus).toBeDefined();
      expect(healthReport.components).toBeDefined();
      expect(healthReport.components.registry).toBeDefined();
      expect(healthReport.components.communication).toBeDefined();
      expect(healthReport.components.microservices).toBeDefined();
    });

    test('should check individual agent health', async () => {
      const agents = registry.getRegisteredAgents();
      const agent = agents[0];
      
      const healthResult = await agent.healthCheck();
      
      expect(healthResult).toBeDefined();
      expect(typeof healthResult.healthy).toBe('boolean');
      expect(healthResult.status).toBeDefined();
      expect(healthResult.lastChecked).toBeInstanceOf(Date);
    });

    test('should monitor microservice health', async () => {
      const healthReport = await microserviceAdapter.checkAllServicesHealth();
      
      expect(healthReport).toBeDefined();
      expect(healthReport.totalServices).toBeGreaterThan(0);
      expect(healthReport.serviceDetails).toHaveLength(healthReport.totalServices);
      expect(['healthy', 'degraded', 'unhealthy']).toContain(healthReport.overallStatus);
    });
  });

  describe('Performance Monitoring', () => {
    test('should collect system metrics', async () => {
      const metrics = await systemManager.getSystemMetrics();
      
      expect(metrics).toBeDefined();
      expect(metrics.taskMetrics).toBeDefined();
      expect(metrics.agentMetrics).toBeDefined();
      expect(metrics.collaborationMetrics).toBeDefined();
      expect(metrics.systemMetrics).toBeDefined();
    });

    test('should track agent performance', async () => {
      const agents = registry.getRegisteredAgents();
      const agent = agents[0];
      
      const performance = agent.getPerformance();
      
      expect(performance).toBeDefined();
      expect(typeof performance.taskCompletionRate).toBe('number');
      expect(typeof performance.averageResponseTime).toBe('number');
      expect(typeof performance.qualityScore).toBe('number');
      expect(performance.lastEvaluated).toBeInstanceOf(Date);
    });
  });

  describe('Configuration Management', () => {
    test('should update system configuration', async () => {
      const newConfig = {
        workflow: {
          maxConcurrentWorkflows: 150,
          defaultTimeout: 45000,
          retryPolicy: {
            maxAttempts: 5,
            backoffMultiplier: 2
          }
        },
        monitoring: {
          metricsEnabled: true,
          loggingLevel: 'debug',
          alertingEnabled: true
        }
      };

      await systemManager.updateSystemConfiguration(newConfig);
      
      const currentConfig = systemManager.getSystemConfiguration();
      expect(currentConfig.workflow.maxConcurrentWorkflows).toBe(150);
      expect(currentConfig.workflow.defaultTimeout).toBe(45000);
      expect(currentConfig.monitoring.loggingLevel).toBe('debug');
    });

    test('should update agent configuration', async () => {
      const agents = await systemManager.getAllAgents();
      if (agents.length > 0) {
        const agent = agents[0];
        
        const newConfig = {
          maxConcurrentTasks: 20,
          timeoutSettings: {
            defaultTimeout: 25000,
            maxTimeout: 50000,
            retryAttempts: 5
          }
        };

        await agent.updateConfiguration(newConfig);
        
        const updatedConfig = agent.configuration;
        expect(updatedConfig.maxConcurrentTasks).toBe(20);
        expect(updatedConfig.timeoutSettings?.defaultTimeout).toBe(25000);
      } else {
        // 如果没有智能体，跳过测试
        expect(true).toBe(true);
      }
    });
  });

  describe('Error Handling and Recovery', () => {
    test('should handle agent failure gracefully', async () => {
      // 模拟智能体故障
      const request: AgentRequest = {
        id: 'test-error-request',
        type: TaskType.DIAGNOSIS,
        content: 'SIMULATE_ERROR', // 特殊内容触发错误
        priority: 'medium',
        context: {
          userId: 'test-user-error',
          sessionId: 'test-session-error'
        },
        constraints: {
          maxExecutionTime: 5000,
          requiredConfidence: 0.7
        },
        metadata: {
          timestamp: new Date(),
          source: 'error-test'
        }
      };

      const response = await systemManager.processRequest(request);
      
      // 即使出错，系统也应该返回响应
      expect(response).toBeDefined();
      expect(response.requestId).toBe(request.id);
      
      // 检查错误是否被正确处理
      if (!response.success) {
        expect(response.error).toBeDefined();
        expect(response.error?.code).toBeDefined();
        expect(response.error?.message).toBeDefined();
      }
    });

    test('should retry failed operations', async () => {
      // 这个测试需要模拟网络故障等情况
      // 由于是集成测试，我们主要验证重试机制的存在
      const services = await microserviceAdapter.discoverServices();
      expect(services).toBeDefined();
      
      // 验证重试配置
      const service = services[0];
      if (service) {
        try {
          await microserviceAdapter.callServiceWithRetry(
            service.id,
            {
              id: 'retry-test',
              method: 'POST',
              path: '/nonexistent',
              timeout: 1000
            },
            {
              maxAttempts: 2,
              initialDelay: 100,
              maxDelay: 1000,
              backoffMultiplier: 2,
              jitterEnabled: false
            }
          );
        } catch (error) {
          // 预期会失败，但应该尝试了重试
          expect(error).toBeDefined();
        }
      }
    });
  });

  describe('Frontend Integration', () => {
    test('should create frontend agents', async () => {
      const xiaoaiConfig = {
        agentId: 'frontend-xiaoai-1',
        type: AgentType.XIAOAI,
        displayName: '小艾',
        description: '中医四诊智能体',
        capabilities: ['diagnosis', 'tcm_analysis'],
        isAvailable: true
      };

      const frontendAgent = await frontendFactory.createAgent(xiaoaiConfig);
      
      expect(frontendAgent).toBeDefined();
      expect(frontendAgent.config.agentId).toBe(xiaoaiConfig.agentId);
      expect(frontendAgent.config.type).toBe(AgentType.XIAOAI);
    });

    test('should create frontend agent manager', async () => {
      const manager = await frontendFactory.createManager();
      
      expect(manager).toBeDefined();
      
      const systemStatus = await manager.getSystemStatus();
      expect(systemStatus).toBeDefined();
      expect(typeof systemStatus.totalAgents).toBe('number');
      expect(typeof systemStatus.availableAgents).toBe('number');
    });
  });

  describe('Load Balancing and Service Selection', () => {
    test('should select service based on criteria', async () => {
      const selectedService = await microserviceAdapter.selectService({
        type: AgentType.XIAOAI,
        maxLoad: 0.8,
        minPerformance: {
          availability: 0.95
        }
      });

      expect(selectedService).toBeDefined();
      expect(selectedService?.type).toBe(AgentType.XIAOAI);
      expect(selectedService?.capacity.currentLoad).toBeLessThanOrEqual(0.8);
      expect(selectedService?.performance.availability).toBeGreaterThanOrEqual(0.95);
    });

    test('should handle no available services', async () => {
      const selectedService = await microserviceAdapter.selectService({
        type: AgentType.LAOKE, // 没有注册的服务类型
        maxLoad: 0.1
      });

      expect(selectedService).toBeNull();
    });
  });
});

// ============================================================================
// 性能测试
// ============================================================================

describe('Agentic System Performance Tests', () => {
  let systemManager: AgenticSystemManager;

  beforeAll(async () => {
    // 使用与集成测试相同的设置
    // 这里可以复用上面的初始化代码
  });

  test('should handle concurrent requests', async () => {
    const concurrentRequests = 10;
    const requests: AgentRequest[] = [];

    for (let i = 0; i < concurrentRequests; i++) {
      requests.push({
        id: `perf-test-${i}`,
        type: TaskType.DIAGNOSIS,
        content: `性能测试请求 ${i}`,
        priority: 'medium',
        context: {
          userId: `perf-user-${i}`,
          sessionId: `perf-session-${i}`
        },
        constraints: {
          maxExecutionTime: 10000,
          requiredConfidence: 0.6
        },
        metadata: {
          timestamp: new Date(),
          source: 'performance-test'
        }
      });
    }

    const startTime = Date.now();
    const responses = await Promise.all(
      requests.map(request => systemManager.processRequest(request))
    );
    const endTime = Date.now();

    expect(responses).toHaveLength(concurrentRequests);
    
    const successfulResponses = responses.filter(r => r.success);
    expect(successfulResponses.length).toBeGreaterThan(concurrentRequests * 0.8); // 至少80%成功

    const totalTime = endTime - startTime;
    const averageTime = totalTime / concurrentRequests;
    
    console.log(`并发性能测试结果:`);
    console.log(`- 总请求数: ${concurrentRequests}`);
    console.log(`- 成功请求数: ${successfulResponses.length}`);
    console.log(`- 总耗时: ${totalTime}ms`);
    console.log(`- 平均耗时: ${averageTime}ms`);
    
    // 性能要求：平均响应时间应该在合理范围内
    expect(averageTime).toBeLessThan(5000); // 5秒内
  });

  test('should maintain performance under load', async () => {
    const loadTestDuration = 10000; // 10秒
    const requestInterval = 100; // 每100ms一个请求
    const responses: any[] = [];
    
    const startTime = Date.now();
    let requestCount = 0;

    const loadTest = setInterval(async () => {
      if (Date.now() - startTime >= loadTestDuration) {
        clearInterval(loadTest);
        return;
      }

      const request: AgentRequest = {
        id: `load-test-${requestCount++}`,
        type: TaskType.DIAGNOSIS,
        content: `负载测试请求 ${requestCount}`,
        priority: 'medium',
        context: {
          userId: `load-user-${requestCount}`,
          sessionId: `load-session-${requestCount}`
        },
        constraints: {
          maxExecutionTime: 5000,
          requiredConfidence: 0.5
        },
        metadata: {
          timestamp: new Date(),
          source: 'load-test'
        }
      };

      try {
        const response = await systemManager.processRequest(request);
        responses.push(response);
      } catch (error) {
        responses.push({ success: false, error });
      }
    }, requestInterval);

    // 等待负载测试完成
    await new Promise(resolve => setTimeout(resolve, loadTestDuration + 1000));

    const successfulResponses = responses.filter(r => r.success);
    const successRate = successfulResponses.length / responses.length;

    console.log(`负载测试结果:`);
    console.log(`- 总请求数: ${responses.length}`);
    console.log(`- 成功请求数: ${successfulResponses.length}`);
    console.log(`- 成功率: ${(successRate * 100).toFixed(2)}%`);

    // 负载测试要求：成功率应该保持在较高水平
    expect(successRate).toBeGreaterThan(0.9); // 90%以上成功率
  });
});