/**
 * 配置加载工具
 */
import fs from 'fs';
import path from 'path';

// 配置缓存
let configCache: any = null;

/**
 * 加载配置文件
 */
export function loadConfig(): any {
  // 如果已经加载过配置，则直接返回缓存
  if (configCache) {
    return configCache;
  }
  
  // 获取配置文件路径
  const configPath = process.env.CONFIG_PATH || path.join(__dirname, '../../config/coordinator-config.json');
  
  try {
    // 读取配置文件
    const configContent = fs.readFileSync(configPath, 'utf8');
    configCache = JSON.parse(configContent);
    return configCache;
  } catch (error) {
    console.error(`加载配置文件失败: ${configPath}`, error);
    
    // 测试环境下返回默认配置，避免测试失败
    if (process.env.NODE_ENV === 'test') {
      return getDefaultConfig();
    }
    
    // 生产环境下抛出错误
    throw new Error(`无法加载配置文件: ${configPath}`);
  }
}

/**
 * 获取默认配置（仅用于测试环境）
 */
function getDefaultConfig(): any {
  return {
    agentCoordination: {
      enableOpenAIStyleHandoffs: true,
      handoffProtocol: 'assistants-api',
      trackConversationContext: true,
      maxHandoffsPerConversation: 5,
      persistStateAcrossHandoffs: true
    },
    agents: [
      {
        id: 'xiaoke',
        name: '小克',
        serviceUrl: 'http://xiaoke-service:8080',
        capabilities: ['服务订阅', '农产品预制', '供应链管理', '农事活动体验'],
        isDefault: true,
        description: '小克是索克生活APP的商务服务智能体，专注于农产品订制、供应链管理和商务服务'
      }
    ],
    toolRegistry: {
      tools: [],
      enableToolObservability: true,
      toolTimeoutSeconds: 30
    },
    routing: {
      routingMode: 'capability-based',
      fallbackAgent: 'soer',
      routingRules: []
    },
    logging: {
      level: 'info',
      format: 'json',
      enableRequestLogging: false,
      enableAgentInteractionLogging: false
    },
    security: {
      enableApiAuthentication: false,
      enableAgentAuthentication: false,
      rateLimiting: {
        enabled: false,
        maxRequestsPerMinute: 60
      }
    },
    performance: {
      cacheEnabled: true,
      cacheTtlSeconds: 300,
      maxConcurrentSessions: 1000
    }
  };
}