/**
* API Gateway 配置文件
* 定义所有微服务的路由映射和网关配置
*/
export const GATEWAY_CONFIG = {
  // 网关基础配置
  BASE_URL: process.env.REACT_APP_GATEWAY_URL || 'http://localhost:8000',
  API_VERSION: 'v1',
  TIMEOUT: 30000,
  // 重试配置
  RETRY: {,
  ATTEMPTS: 3,
    DELAY: 1000,
    BACKOFF_FACTOR: 2,
  },
  // 缓存配置
  CACHE: {,
  DEFAULT_TTL: 300000, // 5分钟
    MAX_SIZE: 1000,
    ENABLED: true,
  },
  // 熔断器配置
  CIRCUIT_BREAKER: {,
  FAILURE_THRESHOLD: 5,
    RECOVERY_TIMEOUT: 60000,
    ENABLED: true,
  },
  // 限流配置
  RATE_LIMIT: {,
  ENABLED: true,
    REQUESTS_PER_MINUTE: 1000,
    BURST_SIZE: 100,
  },
  // 安全配置
  SECURITY: {,
  ENABLE_CORS: true,
    ENABLE_CSRF: true,
    ENABLE_JWT: true,
    JWT_HEADER: 'Authorization',
    JWT_PREFIX: 'Bearer ',
  },
  // 监控配置
  MONITORING: {,
  ENABLE_METRICS: true,
    ENABLE_TRACING: true,
    ENABLE_LOGGING: true,
    LOG_LEVEL: 'info',
  },
};
// 微服务路由映射
export const SERVICE_ROUTES = {
  // 认证服务
  AUTH: {,
  name: 'auth-service',
    baseUrl: '/api/v1/auth',
    endpoints: {,
  login: '/login',
      register: '/register',
      logout: '/logout',
      refresh: '/refresh',
      me: '/me',
      forgotPassword: '/forgot-password',
      resetPassword: '/reset-password',
      changePassword: '/change-password',
      verifyPassword: '/verify-password',
      checkEmail: '/check-email',
      checkUsername: '/check-username',
      sendEmailVerification: '/send-email-verification',
      verifyEmailCode: '/verify-email-code',
    },
    healthCheck: '/health',
    timeout: 10000,
    retries: 3,
  },
  // 用户服务
  USER: {,
  name: 'user-service',
    baseUrl: '/api/v1/user',
    endpoints: {,
  profile: '/profile',
      settings: '/settings',
      preferences: '/preferences',
      healthProfile: '/health-profile',
      avatar: '/avatar',
      notifications: '/notifications',
    },
    healthCheck: '/health',
    timeout: 15000,
    retries: 2,
  },
  // 健康数据服务
  HEALTH_DATA: {,
  name: 'health-data-service',
    baseUrl: '/api/v1/health',
    endpoints: {,
  data: '/data',
      batch: '/data/batch',
      metrics: '/metrics',
      export: '/export',
      sync: '/sync',
      goals: '/goals',
      reports: '/reports',
    },
    healthCheck: '/health',
    timeout: 20000,
    retries: 2,
  },
  // 智能体服务
  AGENTS: {,
  name: 'agent-services',
    baseUrl: '/api/v1/agents',
    endpoints: {,
  status: '/status',
      chat: '/chat',
      performance: '/performance',
      settings: '/settings',
      xiaoai: '/xiaoai',
      xiaoke: '/xiaoke',
      laoke: '/laoke',
      soer: '/soer',
    },
    healthCheck: '/health',
    timeout: 30000,
    retries: 1,
  },
  // 五诊服务 (原四诊服务升级)
  DIAGNOSIS: {,
  name: 'diagnostic-services',
    baseUrl: '/api/v1/diagnosis',
    endpoints: {
      // 传统四诊
      look: '/look',
      listen: '/listen',
      inquiry: '/inquiry',
      palpation: '/palpation',
      // 新增算诊 (第五诊)
      calculation: '/calculation',
      // 综合分析
      comprehensive: '/comprehensive',
      fiveDiagnosis: '/five-diagnosis',
      // 历史记录
      history: '/history',
      // 算诊专用端点
      ziwu: '/calculation/ziwu',
      constitution: '/calculation/constitution',
      bagua: '/calculation/bagua',
      wuyun: '/calculation/wuyun',
      calculationComprehensive: '/calculation/comprehensive',
    },
    healthCheck: '/health',
    timeout: 45000,
    retries: 1,
  },
  // RAG服务
  RAG: {,
  name: 'rag-service',
    baseUrl: '/api/v1/rag',
    endpoints: {,
  query: '/query',
      streamQuery: '/stream-query',
      multimodalQuery: '/multimodal-query',
      tcm: '/tcm',
      knowledge: '/knowledge',
      index: '/index',
    },
    healthCheck: '/health',
    timeout: 60000,
    retries: 1,
  },
  // 区块链服务
  BLOCKCHAIN: {,
  name: 'blockchain-service',
    baseUrl: '/api/v1/blockchain',
    endpoints: {,
  records: '/records',
      verify: '/verify',
      mint: '/mint',
      transfer: '/transfer',
      wallet: '/wallet',
      transactions: '/transactions',
    },
    healthCheck: '/health',
    timeout: 30000,
    retries: 2,
  },
  // 消息总线服务
  MESSAGE_BUS: {,
  name: 'message-bus',
    baseUrl: '/api/v1/messaging',
    endpoints: {,
  publish: '/publish',
      subscribe: '/subscribe',
      topics: '/topics',
      queues: '/queues',
      events: '/events',
    },
    healthCheck: '/health',
    timeout: 15000,
    retries: 3,
  },
  // 医疗资源服务
  MEDICAL_RESOURCE: {,
  name: 'medical-resource-service',
    baseUrl: '/api/v1/medical',
    endpoints: {,
  resources: '/resources',
      hospitals: '/hospitals',
      doctors: '/doctors',
      appointments: '/appointments',
      medicines: '/medicines',
    },
    healthCheck: '/health',
    timeout: 20000,
    retries: 2,
  },
  // 玉米迷宫服务
  CORN_MAZE: {,
  name: 'corn-maze-service',
    baseUrl: '/api/v1/maze',
    endpoints: {,
  status: '/status',
      start: '/start',
      move: '/move',
      leaderboard: '/leaderboard',
      achievements: '/achievements',
    },
    healthCheck: '/health',
    timeout: 10000,
    retries: 2,
  },
  // 无障碍服务
  ACCESSIBILITY: {,
  name: 'accessibility-service',
    baseUrl: '/api/v1/accessibility',
    endpoints: {,
  settings: '/settings',
      features: '/features',
      support: '/support',
      feedback: '/feedback',
    },
    healthCheck: '/health',
    timeout: 10000,
    retries: 2,
  },
  // 基准测试服务
  SUOKE_BENCH: {,
  name: 'suoke-bench-service',
    baseUrl: '/api/v1/benchmark',
    endpoints: {,
  run: '/run',
      results: '/results',
      models: '/models',
      datasets: '/datasets',
      metrics: '/metrics',
    },
    healthCheck: '/health',
    timeout: 120000,
    retries: 1,
  },
  // 中医知识服务
  MED_KNOWLEDGE: {,
  name: 'med-knowledge',
    baseUrl: '/api/v1/knowledge',
    endpoints: {,
  herbs: '/herbs',
      formulas: '/formulas',
      symptoms: '/symptoms',
      syndromes: '/syndromes',
      constitution: '/constitution',
      search: '/search',
    },
    healthCheck: '/health',
    timeout: 30000,
    retries: 2,
  },
  // 人工审核服务
  HUMAN_REVIEW: {,
  name: 'human-review-service',
    baseUrl: '/api/v1/review',
    endpoints: {,
  submit: '/submit',
      status: '/status',
      feedback: '/feedback',
      queue: '/queue',
    },
    healthCheck: '/health',
    timeout: 20000,
    retries: 2,
  },
  // 集成服务
  INTEGRATION: {,
  name: 'integration-service',
    baseUrl: '/api/v1/integration',
    endpoints: {,
  sync: '/sync',
      webhooks: '/webhooks',
      external: '/external',
      connectors: '/connectors',
    },
    healthCheck: '/health',
    timeout: 25000,
    retries: 2,
  },
};
// 负载均衡策略
export const LOAD_BALANCING = {
      DEFAULT_STRATEGY: "round_robin",
      STRATEGIES: {,
  ROUND_ROBIN: 'round_robin',
    WEIGHTED_ROUND_ROBIN: 'weighted_round_robin',
    LEAST_CONNECTIONS: 'least_connections',
    RANDOM: 'random',
    IP_HASH: 'ip_hash',
  },
};
// 服务发现配置
export const SERVICE_DISCOVERY = {
  ENABLED: true,
  REGISTRY_URL: process.env.REACT_APP_REGISTRY_URL || 'http://localhost:8500',
  HEALTH_CHECK_INTERVAL: 30000,
  REGISTRATION_TTL: 60000,
  AUTO_DEREGISTER: true,
};
// WebSocket配置
export const WEBSOCKET_CONFIG = {
  ENABLED: true,
  BASE_URL: process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws',
  RECONNECT_ATTEMPTS: 5,
  RECONNECT_DELAY: 3000,
  HEARTBEAT_INTERVAL: 30000,
};
// 缓存策略配置
export const CACHE_STRATEGIES = {
  // 认证相关 - 短期缓存
  AUTH: {,
  TTL: 300000, // 5分钟
    STRATEGY: 'memory',
  },
  // 用户数据 - 中期缓存
  USER_DATA: {,
  TTL: 900000, // 15分钟
    STRATEGY: 'memory',
  },
  // 健康数据 - 短期缓存
  HEALTH_DATA: {,
  TTL: 180000, // 3分钟
    STRATEGY: 'memory',
  },
  // 静态数据 - 长期缓存
  STATIC_DATA: {,
  TTL: 3600000, // 1小时
    STRATEGY: 'memory',
  },
  // RAG查询 - 中期缓存
  RAG_QUERIES: {,
  TTL: 600000, // 10分钟
    STRATEGY: 'memory',
  },
};
// 错误处理配置
export const ERROR_HANDLING = {
  // 重试的HTTP状态码
  RETRYABLE_STATUS_CODES: [408, 429, 500, 502, 503, 504],
  // 不重试的HTTP状态码
  NON_RETRYABLE_STATUS_CODES: [400, 401, 403, 404, 422],
  // 错误分类
  ERROR_CATEGORIES: {,
  NETWORK: 'network',
    AUTHENTICATION: 'authentication',
    AUTHORIZATION: 'authorization',
    VALIDATION: 'validation',
    SERVER: 'server',
    TIMEOUT: 'timeout',
    RATE_LIMIT: 'rate_limit',
  },
};
// 性能监控配置
export const PERFORMANCE_CONFIG = {
  // 性能指标阈值
  THRESHOLDS: {,
  RESPONSE_TIME_WARNING: 1000, // 1秒
    RESPONSE_TIME_CRITICAL: 3000, // 3秒
    ERROR_RATE_WARNING: 0.05, // 5%
    ERROR_RATE_CRITICAL: 0.1, // 10%
  },
  // 采样率
  SAMPLING_RATE: 0.1, // 10%
  // 指标收集间隔
  METRICS_INTERVAL: 60000, // 1分钟
};
// 安全配置
export const SECURITY_CONFIG = {
  // CORS配置
  CORS: {,
  ALLOWED_ORIGINS: [
      "http:localhost:8081',
      'https://suoke.life',
    ],
    ALLOWED_METHODS: ["GET",POST', "PUT",DELETE', 'OPTIONS'],
    ALLOWED_HEADERS: ["Content-Type",Authorization', 'X-Request-ID'],
    CREDENTIALS: true,
  },
  // 请求头验证
  REQUIRED_HEADERS: {
    'X-Request-ID': true,
    'User-Agent': false,
  },
  // 输入验证
  INPUT_VALIDATION: {,
  MAX_REQUEST_SIZE: 10 * 1024 * 1024, // 10MB;
    MAX_QUERY_PARAMS: 50,
    MAX_HEADER_SIZE: 8192,
  },
};
// 导出完整配置
export const API_GATEWAY_CONFIG = {
  ...GATEWAY_CONFIG,
  SERVICES: SERVICE_ROUTES,
  LOAD_BALANCING,
  SERVICE_DISCOVERY,
  WEBSOCKET: WEBSOCKET_CONFIG,
  CACHE: CACHE_STRATEGIES,
  ERROR_HANDLING,
  PERFORMANCE: PERFORMANCE_CONFIG,
  SECURITY: SECURITY_CONFIG,
};
export default API_GATEWAY_CONFIG;