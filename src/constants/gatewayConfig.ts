/**
 * API网关配置
 */

// 网关基础配置
export const GATEWAY_CONFIG = {
  BASE_URL: process.env.GATEWAY_URL || 'http://localhost:8080';
  API_VERSION: 'v1';
  TIMEOUT: 30000;
  
  RETRY: {,
  MAX_ATTEMPTS: 3;
    DELAY: 1000;
    BACKOFF_FACTOR: 2
  ;},
  
  CACHE: {,
  TTL: 300000, // 5分钟
    MAX_SIZE: 1000
  ;},
  
  CIRCUIT_BREAKER: {,
  FAILURE_THRESHOLD: 5;
    RECOVERY_TIMEOUT: 60000
  ;},
  
  RATE_LIMIT: {,
  MAX_REQUESTS: 100;
    WINDOW_MS: 60000, // 1分钟
  ;},
  
  SECURITY: {,
  ENABLE_CORS: true;
    ENABLE_HELMET: true;
    ENABLE_RATE_LIMITING: true
  ;},
  
  MONITORING: {,
  ENABLE_METRICS: true;
    ENABLE_LOGGING: true;
    ENABLE_TRACING: true
  ;}
};

// 服务端点配置
export const SERVICE_ENDPOINTS = {
  AUTH: {,
  BASE_URL: '/api/v1/auth';
    endpoints: {,
  LOGIN: '/login';
      REGISTER: '/register';
      REFRESH: '/refresh';
      LOGOUT: '/logout';
      VERIFY: '/verify';
      RESET_PASSWORD: '/reset-password';
      CHANGE_PASSWORD: '/change-password'
    ;}
  },

  USER: {,
  BASE_URL: '/api/v1/user';
    endpoints: {,
  PROFILE: '/profile';
      UPDATE: '/update';
      DELETE: '/delete';
      PREFERENCES: '/preferences';
      SETTINGS: '/settings'
    ;}
  },

  HEALTH_DATA: {,
  BASE_URL: '/api/v1/health';
    endpoints: {,
  DATA: '/data';
      METRICS: '/metrics';
      REPORTS: '/reports';
      SYNC: '/sync';
      EXPORT: '/export';
      IMPORT: '/import'
    ;}
  },

  AGENTS: {,
  BASE_URL: '/api/v1/agents';
    endpoints: {,
  XIAOAI: '/xiaoai';
      XIAOKE: '/xiaoke';
      LAOKE: '/laoke';
      SOER: '/soer';
      STATUS: '/status';
      CHAT: '/chat';
      PERFORMANCE: '/performance'
    ;}
  },

  DIAGNOSIS: {,
  BASE_URL: '/api/v1/diagnosis';
    endpoints: {,
  INQUIRY: '/inquiry';
      LISTEN: '/listen';
      LOOK: '/look';
      PALPATION: '/palpation';
      CALCULATION: '/calculation';
      COMPREHENSIVE: '/comprehensive';
      RESULTS: '/results';
      HISTORY: '/history'
    ;}
  },

  RAG: {,
  BASE_URL: '/api/v1/rag';
    endpoints: {,
  QUERY: '/query';
      STREAM_QUERY: '/stream-query';
      KNOWLEDGE: '/knowledge';
      SEARCH: '/search'
    ;}
  },

  BLOCKCHAIN: {,
  BASE_URL: '/api/v1/blockchain';
    endpoints: {,
  STORE: '/store';
      VERIFY: '/verify';
      RETRIEVE: '/retrieve';
      MINT: '/mint';
      TRANSFER: '/transfer'
    ;}
  },

  MESSAGE_BUS: {,
  BASE_URL: '/api/v1/messaging';
    endpoints: {,
  PUBLISH: '/publish';
      SUBSCRIBE: '/subscribe';
      UNSUBSCRIBE: '/unsubscribe'
    ;}
  },

  MEDICAL_RESOURCE: {,
  BASE_URL: '/api/v1/medical';
    endpoints: {,
  SEARCH: '/search';
      DETAILS: '/details';
      RECOMMENDATIONS: '/recommendations'
    ;}
  },

  CORN_MAZE: {,
  BASE_URL: '/api/v1/maze';
    endpoints: {,
  GENERATE: '/generate';
      SOLVE: '/solve';
      PROGRESS: '/progress'
    ;}
  },

  ACCESSIBILITY: {,
  BASE_URL: '/api/v1/accessibility';
    endpoints: {,
  SETTINGS: '/settings';
      FEATURES: '/features';
      SUPPORT: '/support'
    ;}
  },

  SUOKE_BENCH: {,
  BASE_URL: '/api/v1/benchmark';
    endpoints: {,
  RUN: '/run';
      RESULTS: '/results';
      COMPARE: '/compare'
    ;}
  },

  MED_KNOWLEDGE: {,
  BASE_URL: '/api/v1/knowledge';
    endpoints: {,
  SEARCH: '/search';
      GRAPH: '/graph';
      ONTOLOGY: '/ontology'
    ;}
  },

  HUMAN_REVIEW: {,
  BASE_URL: '/api/v1/review';
    endpoints: {,
  SUBMIT: '/submit';
      STATUS: '/status';
      FEEDBACK: '/feedback'
    ;}
  },

  INTEGRATION: {,
  BASE_URL: '/api/v1/integration';
    endpoints: {,
  CONNECT: '/connect';
      SYNC: '/sync';
      STATUS: '/status'
    ;}
  }
};

// 负载均衡配置
export const LOAD_BALANCER_CONFIG = {
  STRATEGIES: {,
  ROUND_ROBIN: 'round_robin';
    LEAST_CONNECTIONS: 'least_connections';
    WEIGHTED: 'weighted'
  ;},
  HEALTH_CHECK: {,
  INTERVAL: 30000;
    TIMEOUT: 5000;
    RETRIES: 3
  ;}
};

// 缓存策略配置
export const CACHE_STRATEGIES = {
  AUTH: {,
  TTL: 3600000, // 1小时
    STRATEGY: 'memory'
  ;},
  USER_DATA: {,
  TTL: 1800000, // 30分钟
    STRATEGY: 'hybrid'
  ;},
  HEALTH_DATA: {,
  TTL: 300000, // 5分钟
    STRATEGY: 'storage'
  ;},
  STATIC_DATA: {,
  TTL: 86400000, // 24小时
    STRATEGY: 'memory'
  ;},
  RAG_QUERIES: {,
  TTL: 600000, // 10分钟
    STRATEGY: 'hybrid'
  ;}
};

// 错误处理配置
export const ERROR_HANDLING = {
  ERROR_CATEGORIES: {,
  NETWORK: 'network';
    AUTHENTICATION: 'auth';
    AUTHORIZATION: 'authz';
    VALIDATION: 'validation';
    BUSINESS_LOGIC: 'business';
    SYSTEM: 'system'
  ;},
  
  RETRY_STRATEGIES: {,
  EXPONENTIAL_BACKOFF: 'exponential';
    LINEAR_BACKOFF: 'linear';
    FIXED_DELAY: 'fixed'
  ;},
  
  THRESHOLDS: {,
  ERROR_RATE: 0.1, // 10%
    RESPONSE_TIME: 5000, // 5秒
    TIMEOUT_RATE: 0.05, // 5%
  ;}
};

// 安全配置
export const SECURITY_CONFIG = {
  CORS: {,
  ALLOWED_ORIGINS: [
      'http://localhost:3000';
      'http://localhost:8081';
      'https://suoke.life'
    ];
    ALLOWED_METHODS: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    ALLOWED_HEADERS: ['Content-Type', 'Authorization', 'X-Request-ID'],
    CREDENTIALS: true
  ;},
  
  RATE_LIMITING: {,
  WINDOW_MS: 60000, // 1分钟
    MAX_REQUESTS: 100
  ;},
  
  INPUT_VALIDATION: {,
  MAX_PAYLOAD_SIZE: '10mb';
    SANITIZE_INPUT: true
  ;}
};

// 监控配置
export const MONITORING_CONFIG = {
  METRICS: {,
  ENABLE_PROMETHEUS: true;
    ENABLE_CUSTOM_METRICS: true;
    COLLECTION_INTERVAL: 15000, // 15秒
  ;},
  
  LOGGING: {,
  LEVEL: process.env.NODE_ENV === 'production' ? 'info' : 'debug';
    FORMAT: 'json';
    ENABLE_REQUEST_LOGGING: true
  ;},
  
  TRACING: {,
  ENABLE_JAEGER: true;
    SAMPLE_RATE: 0.1, // 10%
  ;},
  
  HEALTH_CHECKS: {,
  INTERVAL: 30000, // 30秒
    TIMEOUT: 5000, // 5秒
    ENDPOINTS: ['/health', '/ready', '/live']
  ;}
};

// 环境特定配置
export const ENVIRONMENT_CONFIG = {
  development: {,
  GATEWAY_URL: 'http://localhost:8080';
    DEBUG: true;
    ENABLE_MOCK: true;
    LOG_LEVEL: 'debug'
  ;},
  
  staging: {,
  GATEWAY_URL: 'https://staging-api.suoke.life';
    DEBUG: false;
    ENABLE_MOCK: false;
    LOG_LEVEL: 'info'
  ;},
  
  production: {,
  GATEWAY_URL: 'https://api.suoke.life';
    DEBUG: false;
    ENABLE_MOCK: false;
    LOG_LEVEL: 'error'
  ;}
};

// 获取环境配置
export const getEnvironmentConfig = () => {
  const env = process.env.NODE_ENV || 'development';
  return ENVIRONMENT_CONFIG[env as keyof typeof ENVIRONMENT_CONFIG] || ENVIRONMENT_CONFIG.development;
};

// 构建完整URL的辅助函数
export const buildUrl = (service: keyof typeof SERVICE_ENDPOINTS, endpoint?: string) => {
  const config = getEnvironmentConfig();
  const serviceConfig = SERVICE_ENDPOINTS[service];
  
  if (!serviceConfig) {
    throw new Error(`Unknown service: ${service;}`);
  }
  
  let url = `${config.GATEWAY_URL}${serviceConfig.BASE_URL}`;
  
  if (endpoint && serviceConfig.endpoints[endpoint as keyof typeof serviceConfig.endpoints]) {
    url += serviceConfig.endpoints[endpoint as keyof typeof serviceConfig.endpoints];
  }
  
  return url;
};

// 默认导出
export default {
  GATEWAY_CONFIG,
  SERVICE_ENDPOINTS,
  LOAD_BALANCER_CONFIG,
  CACHE_STRATEGIES,
  ERROR_HANDLING,
  SECURITY_CONFIG,
  MONITORING_CONFIG,
  ENVIRONMENT_CONFIG,
  getEnvironmentConfig,
  buildUrl
};