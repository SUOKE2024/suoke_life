// 应用配置常量
import { API_GATEWAY_CONFIG as GATEWAY_CONFIG } from './gatewayConfig';
export const STORAGE_CONFIG = {
  KEYS: {,
  AUTH_TOKEN: '@suoke_life:auth_token',
    REFRESH_TOKEN: '@suoke_life:refresh_token',
    USER_ID: '@suoke_life:user_id',
    USER_PREFERENCES: '@suoke_life:user_preferences',
    THEME: '@suoke_life:theme',
    LANGUAGE: '@suoke_life:language',
    DEVICE_ID: '@suoke_life:device_id',
  },
};
// 统一API网关配置
export const API_GATEWAY_CONFIG = {
  // 网关基础URL;
  GATEWAY_URL: 'http://localhost:8000',
  // 网关API版本
  API_VERSION: 'v1',
  // 网关路由前缀
  GATEWAY_PREFIX: '/api/v1/gateway',
  // 超时配置
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
  // 通过网关的服务端点
  SERVICES: {
    // 认证服务
    AUTH: '/auth-service',
    // 用户服务
    USER: '/user-service',
    // 健康数据服务
    HEALTH_DATA: '/health-data-service',
    // 区块链服务
    BLOCKCHAIN: '/blockchain-service',
    // RAG服务
    RAG: '/rag-service',
    // 医学知识服务
    MED_KNOWLEDGE: '/med-knowledge-service',
    // 智能体服务
    AGENTS: {,
  XIAOAI: '/agent-services/xiaoai-service',
      XIAOKE: '/agent-services/xiaoke-service',
      LAOKE: '/agent-services/laoke-service',
      SOER: '/agent-services/soer-service',
    },
    // 四诊服务
    DIAGNOSIS: {,
  LOOK: '/diagnostic-services/look-service',
      LISTEN: '/diagnostic-services/listen-service',
      INQUIRY: '/diagnostic-services/inquiry-service',
      PALPATION: '/diagnostic-services/palpation-service',
      CALCULATION: '/diagnostic-services/calculation-service',
    },
    // 其他服务
    MESSAGE_BUS: '/message-bus-service',
    CORN_MAZE: '/corn-maze-service',
    MEDICAL_RESOURCE: '/medical-resource-service',
    HUMAN_REVIEW: '/human-review-service',
    ACCESSIBILITY: '/accessibility-service',
    INTEGRATION: '/integration-service',
    SUOKE_BENCH: '/suoke-bench-service',
  },
  // 服务端点映射
  ENDPOINTS: {
    // 认证相关
    AUTH: {,
  LOGIN: '/auth/login',
      LOGOUT: '/auth/logout',
      REFRESH: '/auth/refresh',
      REGISTER: '/auth/register',
      PROFILE: '/auth/profile',
      VERIFY: '/auth/verify',
    },
    // 用户相关
    USER: {,
  PROFILE: '/users/profile',
      SETTINGS: '/users/settings',
      PREFERENCES: '/users/preferences',
      HEALTH_PROFILE: '/users/health-profile',
    },
    // 健康数据
    HEALTH: {,
  DATA: '/health-data',
      METRICS: '/health-data/metrics',
      EXPORT: '/health-data/export',
      ANALYSIS: '/health-data/analysis',
    },
    // 智能体
    AGENTS: {,
  STATUS: '/agents/status',
      CHAT: '/agents/chat',
      PERFORMANCE: '/agents/performance',
      SETTINGS: '/agents/settings',
    },
    // 四诊
    DIAGNOSIS: {,
  LOOK: '/diagnosis/look',
      LISTEN: '/diagnosis/listen',
      INQUIRY: '/diagnosis/inquiry',
      PALPATION: '/diagnosis/palpation',
      COMPREHENSIVE: '/diagnosis/comprehensive',
    },
    // RAG服务
    RAG: {,
  QUERY: '/rag/query',
      STREAM_QUERY: '/rag/stream-query',
      MULTIMODAL_QUERY: '/rag/multimodal-query',
      TCM_ANALYSIS: '/rag/tcm/analysis',
      HERB_RECOMMENDATION: '/rag/tcm/herbs',
      SYNDROME_ANALYSIS: '/rag/tcm/syndrome',
      CONSTITUTION_ANALYSIS: '/rag/tcm/constitution',
    },
    // 区块链
    BLOCKCHAIN: {,
  RECORDS: '/blockchain/records',
      VERIFY: '/blockchain/verify',
      MINT: '/blockchain/mint',
      TRANSFER: '/blockchain/transfer',
    },
  },
};
// 构建完整的API URL;
export const buildApiUrl = (service: string, endpoint: string = ''): string => {
  const { GATEWAY_URL, GATEWAY_PREFIX } = API_GATEWAY_CONFIG;
  const serviceUrl = API_GATEWAY_CONFIG.SERVICES[service as keyof typeof API_GATEWAY_CONFIG.SERVICES];
  if (!serviceUrl) {
    throw new Error(`Unknown service: ${service}`);
  }
  return `${GATEWAY_URL}${GATEWAY_PREFIX}${serviceUrl}${endpoint}`;
};
// 构建智能体服务URL;
export const buildAgentUrl = (agent: string, endpoint: string = ''): string => {
  const agentService = API_GATEWAY_CONFIG.SERVICES.AGENTS[agent as keyof typeof API_GATEWAY_CONFIG.SERVICES.AGENTS];
  if (!agentService) {
    throw new Error(`Unknown agent: ${agent}`);
  }
  return `${API_GATEWAY_CONFIG.GATEWAY_URL}${API_GATEWAY_CONFIG.GATEWAY_PREFIX}${agentService}${endpoint}`;
};
// 构建四诊服务URL;
export const buildDiagnosisUrl = (diagnosis: string, endpoint: string = ''): string => {
  const diagnosisService = API_GATEWAY_CONFIG.SERVICES.DIAGNOSIS[diagnosis as keyof typeof API_GATEWAY_CONFIG.SERVICES.DIAGNOSIS];
  if (!diagnosisService) {
    throw new Error(`Unknown diagnosis service: ${diagnosis}`);
  }
  return `${API_GATEWAY_CONFIG.GATEWAY_URL}${API_GATEWAY_CONFIG.GATEWAY_PREFIX}${diagnosisService}${endpoint}`;
};
export const ERROR_CODES = {
      NETWORK_ERROR: "NETWORK_ERROR",
      OPERATION_FAILED: 'OPERATION_FAILED',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  NOT_FOUND: 'NOT_FOUND',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  TIMEOUT: 'TIMEOUT',
  GATEWAY_ERROR: 'GATEWAY_ERROR',
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE',
};
export const APP_CONFIG = {
      NAME: "索克生活",
      VERSION: '1.0.0',
  BUILD_NUMBER: '1',
  ENVIRONMENT: process.env.NODE_ENV || 'development',
};
export const THEME_CONFIG = {
      LIGHT: "light",
      DARK: 'dark',
  SYSTEM: 'system',
};
export const LANGUAGE_CONFIG = {
      ZH_CN: "zh-CN",
      EN_US: 'en-US',
};
export const HEALTH_CONFIG = {
  VITAL_SIGNS: {,
  HEART_RATE: { min: 60, max: 100 },
    BLOOD_PRESSURE: {,
  systolic: { min: 90, max: 140 },
      diastolic: { min: 60, max: 90 },
    },
    TEMPERATURE: { min: 36.1, max: 37.2 },
    OXYGEN_SATURATION: { min: 95, max: 100 },
  },
  ACTIVITY_GOALS: {,
  DAILY_STEPS: 10000,
    WEEKLY_EXERCISE: 150, // minutes;
    SLEEP_HOURS: 8,
    WATER_INTAKE: 2000, // ml;
  },
};
export const NOTIFICATION_CONFIG = {
  TYPES: {,
  HEALTH_REMINDER: 'health_reminder',
    APPOINTMENT: 'appointment',
    MEDICATION: 'medication',
    EXERCISE: 'exercise',
    SYSTEM: 'system',
  },
  PRIORITIES: {,
  LOW: 'low',
    MEDIUM: 'medium',
    HIGH: 'high',
    URGENT: 'urgent',
  },
};
// 网关缓存配置
export const GATEWAY_CACHE_CONFIG = {
  TTL: 300000, // 5分钟
  MAX_SIZE: 100,
  ENABLE_PERSISTENCE: true,
  STRATEGIES: {,
  HEALTH_DATA: 60000, // 1分钟
    USER_PROFILE: 300000, // 5分钟
    AGENT_STATUS: 30000, // 30秒
    DIAGNOSIS_RESULTS: 600000, // 10分钟
  },
};
// 网关性能配置
export const GATEWAY_PERFORMANCE_CONFIG = {
  TIMEOUT: 30000, // 30秒
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
  STREAM_TIMEOUT: 60000, // 1分钟
  CIRCUIT_BREAKER: {,
  FAILURE_THRESHOLD: 5,
    RECOVERY_TIMEOUT: 60000,
    MONITORING_PERIOD: 30000,
  },
};
// 网关特性开关
export const GATEWAY_FEATURES = {
  ENABLE_STREAMING: true,
  ENABLE_MULTIMODAL: true,
  ENABLE_TCM: true,
  ENABLE_OFFLINE: true,
  ENABLE_ANALYTICS: true,
  ENABLE_CACHING: true,
  ENABLE_CIRCUIT_BREAKER: true,
  ENABLE_RATE_LIMITING: true,
  ENABLE_AUTHENTICATION: true,
  ENABLE_MONITORING: true,
};
// 环境特定配置 - 统一通过网关
export const ENV_CONFIG = {
  development: {,
  GATEWAY_URL: 'http://localhost:8000',
    API_PREFIX: '/api/v1/gateway',
    DEBUG: true,
    LOG_LEVEL: 'debug',
    ENABLE_MOCK: false, // 通过网关，不需要mock;
    CACHE_ENABLED: true,
    MONITORING_ENABLED: true,
  },
  staging: {,
  GATEWAY_URL: 'https://staging-gateway.suokelife.com',
    API_PREFIX: '/api/v1/gateway',
    DEBUG: false,
    LOG_LEVEL: 'info',
    ENABLE_MOCK: false,
    CACHE_ENABLED: true,
    MONITORING_ENABLED: true,
  },
  production: {,
  GATEWAY_URL: 'https://gateway.suokelife.com',
    API_PREFIX: '/api/v1/gateway',
    DEBUG: false,
    LOG_LEVEL: 'error',
    ENABLE_MOCK: false,
    CACHE_ENABLED: true,
    MONITORING_ENABLED: true,
  },
};
// 获取当前环境配置
export const getCurrentEnvConfig = () => {
  const env = APP_CONFIG.ENVIRONMENT as keyof typeof ENV_CONFIG;
  const envConfig = ENV_CONFIG[env] || ENV_CONFIG.development;
  // 合并网关配置
  return {
    ...envConfig,
    ...API_GATEWAY_CONFIG,
    GATEWAY_URL: envConfig.GATEWAY_URL,
  };
};
// 服务发现配置
export const SERVICE_DISCOVERY_CONFIG = {
  ENABLED: true,
  REFRESH_INTERVAL: 30000, // 30秒
  HEALTH_CHECK_INTERVAL: 10000, // 10秒
  RETRY_FAILED_SERVICES: true,
  MAX_RETRY_ATTEMPTS: 3,
};
// 获取服务健康状态URL;
export const getServiceHealthUrl = (service?: string): string => {
  const { GATEWAY_URL, GATEWAY_PREFIX } = getCurrentEnvConfig();
  if (service) {
    return `${GATEWAY_URL}${GATEWAY_PREFIX}/services/${service}/health`;
  }
  return `${GATEWAY_URL}${GATEWAY_PREFIX}/services`;
};