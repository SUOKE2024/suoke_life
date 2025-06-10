/**
 * 索克生活应用配置
 */

// API密钥配置
export const API_KEYS = {
  OPENAI: process.env.OPENAI_API_KEY || '',
  ANTHROPIC: process.env.ANTHROPIC_API_KEY || '',
  GOOGLE: process.env.GOOGLE_API_KEY || '',
  AZURE: process.env.AZURE_API_KEY || '',
  BAIDU: process.env.BAIDU_API_KEY || '',
  TENCENT: process.env.TENCENT_API_KEY || '',
  ALIBABA: process.env.ALIBABA_API_KEY || '',
};

// 应用基础配置
export const APP_CONFIG = {
  NAME: 'Suoke Life',
  VERSION: '1.0.0',
  ENVIRONMENT: process.env.NODE_ENV || 'development',
  DEBUG: process.env.DEBUG === 'true',
  API_TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  CACHE_TTL: 300000, // 5分钟
  AGENTS: {
    RESPONSE_TIMEOUT: 30000,
    MAX_RETRIES: 3,
    CONCURRENT_LIMIT: 5,
  },
};

// API网关配置
export const API_GATEWAY_CONFIG = {
  BASE_URL: process.env.GATEWAY_URL || 'http://localhost:8080',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,

  SERVICES: {
    AUTH: {
      BASE_URL: '/api/v1/auth',
      ENDPOINTS: {
        LOGIN: '/login',
        REGISTER: '/register',
        REFRESH: '/refresh',
        LOGOUT: '/logout',
      },
    },

    USER: {
      BASE_URL: '/api/v1/user',
      ENDPOINTS: {
        PROFILE: '/profile',
        UPDATE: '/update',
        DELETE: '/delete',
      },
    },

    HEALTH: {
      BASE_URL: '/api/v1/health',
      ENDPOINTS: {
        DATA: '/data',
        METRICS: '/metrics',
        REPORTS: '/reports',
      },
    },

    AGENTS: {
      BASE_URL: '/api/v1/agents',
      ENDPOINTS: {
        XIAOAI: '/xiaoai',
        XIAOKE: '/xiaoke',
        LAOKE: '/laoke',
        SOER: '/soer',
      },
    },

    DIAGNOSIS: {
      BASE_URL: '/api/v1/diagnosis',
      ENDPOINTS: {
        INQUIRY: '/inquiry',
        LISTEN: '/listen',
        LOOK: '/look',
        PALPATION: '/palpation',
        CALCULATION: '/calculation',
      },
    },

    RAG: {
      BASE_URL: '/api/v1/rag',
      ENDPOINTS: {
        QUERY: '/query',
        KNOWLEDGE: '/knowledge',
        SEARCH: '/search',
      },
    },

    BLOCKCHAIN: {
      BASE_URL: '/api/v1/blockchain',
      ENDPOINTS: {
        STORE: '/store',
        VERIFY: '/verify',
        RETRIEVE: '/retrieve',
      },
    },
  },
};

// 获取服务URL的辅助函数
export const getServiceUrl = (
  service: keyof typeof API_GATEWAY_CONFIG.SERVICES
) => {
  return `${API_GATEWAY_CONFIG.BASE_URL}${API_GATEWAY_CONFIG.SERVICES[service].BASE_URL}`;
};

// 获取智能体URL的辅助函数
export const getAgentUrl = (
  agent: keyof typeof API_GATEWAY_CONFIG.SERVICES.AGENTS.ENDPOINTS
) => {
  return `${getServiceUrl('AGENTS')}${API_GATEWAY_CONFIG.SERVICES.AGENTS.ENDPOINTS[agent]}`;
};

// 获取诊断服务URL的辅助函数
export const getDiagnosisUrl = (
  diagnosis: keyof typeof API_GATEWAY_CONFIG.SERVICES.DIAGNOSIS.ENDPOINTS
) => {
  return `${getServiceUrl('DIAGNOSIS')}${API_GATEWAY_CONFIG.SERVICES.DIAGNOSIS.ENDPOINTS[diagnosis]}`;
};

// 健康数据配置
export const HEALTH_CONFIG = {
  SYNC_INTERVAL: 60000, // 1分钟
  BATCH_SIZE: 100,
  MAX_HISTORY_DAYS: 365,

  VITAL_SIGNS: {
    HEART_RATE: { MIN: 60, MAX: 100 },
    BLOOD_PRESSURE: {
      SYSTOLIC: { MIN: 90, MAX: 140 },
      DIASTOLIC: { MIN: 60, MAX: 90 },
    },
    TEMPERATURE: { MIN: 36.0, MAX: 37.5 },
  },

  ACTIVITY_GOALS: {
    STEPS: 10000,
    CALORIES: 2000,
    EXERCISE_MINUTES: 30,
  },
};

// 诊断配置
export const DIAGNOSIS_CONFIG = {
  TYPES: {
    INQUIRY: '问诊',
    LISTEN: '闻诊',
    LOOK: '望诊',
    PALPATION: '切诊',
  },

  PRIORITIES: {
    LOW: 1,
    MEDIUM: 2,
    HIGH: 3,
    CRITICAL: 4,
  },

  TIMEOUT: 30000,
};

// 缓存配置
export const CACHE_CONFIG = {
  STRATEGIES: {
    MEMORY: 'memory',
    STORAGE: 'storage',
    HYBRID: 'hybrid',
  },

  TTL: {
    SHORT: 60000, // 1分钟
    MEDIUM: 300000, // 5分钟
    LONG: 3600000, // 1小时
  },
};

// 错误处理配置
export const ERROR_CONFIG = {
  CIRCUIT_BREAKER: {
    FAILURE_THRESHOLD: 5,
    RECOVERY_TIMEOUT: 60000,
    MONITOR_TIMEOUT: 30000,
  },

  RETRY: {
    MAX_ATTEMPTS: 3,
    DELAY: 1000,
    BACKOFF_FACTOR: 2,
  },
};

// 存储配置
export const STORAGE_CONFIG = {
  PREFIX: 'suoke_life_',
  VERSION: '1.0.0',
  ENCRYPTION: true,
};

// 环境特定配置
export const ENV_CONFIG = {
  development: {
    GATEWAY_URL: 'http://localhost:8080',
    ENABLE_LOGGING: true,
    ENABLE_DEBUG: true,
    ENABLE_MOCK_DATA: true,
    ENABLE_GATEWAY_MONITOR: true,
  },

  staging: {
    GATEWAY_URL: 'https://staging-api.suoke.life',
    ENABLE_LOGGING: true,
    ENABLE_DEBUG: false,
    ENABLE_MOCK_DATA: false,
    ENABLE_GATEWAY_MONITOR: true,
  },

  production: {
    GATEWAY_URL: 'https://api.suoke.life',
    ENABLE_LOGGING: false,
    ENABLE_DEBUG: false,
    ENABLE_MOCK_DATA: false,
    ENABLE_GATEWAY_MONITOR: false,
  },
};

// 获取当前环境配置
export const getCurrentEnvConfig = () => {
  const env = APP_CONFIG.ENVIRONMENT as keyof typeof ENV_CONFIG;
  return ENV_CONFIG[env] || ENV_CONFIG.development;
};

// 默认导出
export default {
  API_KEYS,
  APP_CONFIG,
  API_GATEWAY_CONFIG,
  HEALTH_CONFIG,
  DIAGNOSIS_CONFIG,
  CACHE_CONFIG,
  ERROR_CONFIG,
  STORAGE_CONFIG,
  ENV_CONFIG,
  getCurrentEnvConfig,
  getServiceUrl,
  getAgentUrl,
  getDiagnosisUrl,
};
