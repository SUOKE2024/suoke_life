/**
 * 索克生活 Agentic AI 架构集成配置示例
 * 展示如何配置与现有 API Gateway 和 Communication Service 的集成
 */

import { ArchitectureIntegrationConfig } from '../ArchitectureIntegration';
import { AgenticAIConfig } from '../AgenticAIManager';

// ============================================================================
// 开发环境配置
// ============================================================================

export const developmentArchitectureConfig: ArchitectureIntegrationConfig = {
  // API Gateway 配置
  apiGateway: {
    endpoint: 'http://localhost:8000',
    healthCheck: 'http://localhost:8000/health',
    serviceDiscovery: 'http://localhost:8000/api/v1/services'
  },
  
  // Communication Service 配置
  communicationService: {
    endpoint: 'http://localhost:8030',
    messageBus: 'http://localhost:8030/api/v1/message-bus',
    ragService: 'http://localhost:8030/api/v1/rag',
    eventBus: 'http://localhost:8030/api/v1/events'
  },
  
  // 集成策略配置
  integrationStrategy: {
    useExistingMessageBus: true,        // 使用现有消息总线
    useExistingServiceDiscovery: true,  // 使用现有服务发现
    useExistingEventSystem: true,       // 使用现有事件系统
    enableDirectServiceCalls: false     // 禁用直接服务调用，通过Gateway
  }
};

// ============================================================================
// 生产环境配置
// ============================================================================

export const productionArchitectureConfig: ArchitectureIntegrationConfig = {
  // API Gateway 配置（生产环境）
  apiGateway: {
    endpoint: 'https://api.suoke.life',
    healthCheck: 'https://api.suoke.life/health',
    serviceDiscovery: 'https://api.suoke.life/api/v1/services'
  },
  
  // Communication Service 配置（生产环境）
  communicationService: {
    endpoint: 'https://comm.suoke.life',
    messageBus: 'https://comm.suoke.life/api/v1/message-bus',
    ragService: 'https://comm.suoke.life/api/v1/rag',
    eventBus: 'https://comm.suoke.life/api/v1/events'
  },
  
  // 生产环境集成策略
  integrationStrategy: {
    useExistingMessageBus: true,
    useExistingServiceDiscovery: true,
    useExistingEventSystem: true,
    enableDirectServiceCalls: false
  }
};

// ============================================================================
// 完整的 Agentic AI 配置示例
// ============================================================================

export const developmentAgenticConfig: AgenticAIConfig = {
  // 功能开关
  enableWorkflow: true,
  enableReflection: true,
  enableToolOrchestration: true,
  enablePlanning: true,
  enableCollaboration: true,
  enableAutonomy: true,
  enableNLU: true,
  
  // 性能阈值
  performanceThresholds: {
    workflow: 5000,      // 5秒
    reflection: 3000,    // 3秒
    planning: 8000,      // 8秒
    collaboration: 10000 // 10秒
  },
  
  // 集成设置
  integrationSettings: {
    crossSystemCommunication: true,
    sharedKnowledgeBase: true,
    unifiedLogging: true,
    realTimeSync: true
  },
  
  // 架构集成配置
  architectureIntegration: developmentArchitectureConfig
};

export const productionAgenticConfig: AgenticAIConfig = {
  // 功能开关（生产环境更保守）
  enableWorkflow: true,
  enableReflection: true,
  enableToolOrchestration: true,
  enablePlanning: true,
  enableCollaboration: true,
  enableAutonomy: false,  // 生产环境暂时关闭自治性
  enableNLU: true,
  
  // 更严格的性能阈值
  performanceThresholds: {
    workflow: 3000,      // 3秒
    reflection: 2000,    // 2秒
    planning: 5000,      // 5秒
    collaboration: 8000  // 8秒
  },
  
  // 集成设置
  integrationSettings: {
    crossSystemCommunication: true,
    sharedKnowledgeBase: true,
    unifiedLogging: true,
    realTimeSync: true
  },
  
  // 架构集成配置
  architectureIntegration: productionArchitectureConfig
};

// ============================================================================
// 配置工厂函数
// ============================================================================

export function createAgenticConfig(environment: 'development' | 'production' | 'test'): AgenticAIConfig {
  switch (environment) {
    case 'development':
      return developmentAgenticConfig;
    case 'production':
      return productionAgenticConfig;
    case 'test':
      return {
        ...developmentAgenticConfig,
        // 测试环境特殊配置
        performanceThresholds: {
          workflow: 1000,
          reflection: 500,
          planning: 1000,
          collaboration: 2000
        },
        architectureIntegration: {
          ...developmentArchitectureConfig,
          // 测试环境使用模拟端点
          apiGateway: {
            endpoint: 'http://localhost:8888',
            healthCheck: 'http://localhost:8888/health',
            serviceDiscovery: 'http://localhost:8888/api/v1/services'
          },
          communicationService: {
            endpoint: 'http://localhost:8889',
            messageBus: 'http://localhost:8889/api/v1/message-bus',
            ragService: 'http://localhost:8889/api/v1/rag',
            eventBus: 'http://localhost:8889/api/v1/events'
          }
        }
      };
    default:
      throw new Error(`Unsupported environment: ${environment}`);
  }
}

// ============================================================================
// 配置验证函数
// ============================================================================

export function validateAgenticConfig(config: AgenticAIConfig): boolean {
  // 验证必需字段
  if (!config.architectureIntegration) {
    throw new Error('架构集成配置缺失');
  }
  
  if (!config.architectureIntegration.apiGateway.endpoint) {
    throw new Error('API Gateway 端点配置缺失');
  }
  
  if (!config.architectureIntegration.communicationService.endpoint) {
    throw new Error('Communication Service 端点配置缺失');
  }
  
  // 验证性能阈值
  const thresholds = config.performanceThresholds;
  if (thresholds.workflow <= 0 || thresholds.reflection <= 0 || 
      thresholds.planning <= 0 || thresholds.collaboration <= 0) {
    throw new Error('性能阈值必须大于0');
  }
  
  return true;
}

// ============================================================================
// 使用示例
// ============================================================================

/*
// 在应用启动时使用配置
import { AgenticAIManager } from '../AgenticAIManager';
import { createAgenticConfig, validateAgenticConfig } from './architecture-integration.example';

async function initializeAgenticAI() {
  // 1. 创建配置
  const environment = process.env.NODE_ENV as 'development' | 'production' | 'test';
  const config = createAgenticConfig(environment);
  
  // 2. 验证配置
  validateAgenticConfig(config);
  
  // 3. 初始化系统
  const agenticManager = new AgenticAIManager(config);
  await agenticManager.initialize();
  
  console.log('🚀 Agentic AI 系统已启动，已集成现有架构');
  
  return agenticManager;
}

// 使用示例
initializeAgenticAI()
  .then(manager => {
    console.log('✅ 系统初始化成功');
    // 开始处理请求...
  })
  .catch(error => {
    console.error('❌ 系统初始化失败:', error);
  });
*/