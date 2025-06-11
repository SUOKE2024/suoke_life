/* 置 */
 */
// 网关基础配置
export const GATEWAY_CONFIG = {BASE_URL: process.env.GATEWAY_URL || 'http://localhost:8080,''/,'/g,'/;
  API_VERSION: 'v1,'';
TIMEOUT: 30000,
RETRY: {MAX_ATTEMPTS: 3,
DELAY: 1000,
}
    const BACKOFF_FACTOR = 2}
  }
CACHE: {TTL: 300000, // 5分钟
}
    const MAX_SIZE = 1000}
  }
CIRCUIT_BREAKER: {FAILURE_THRESHOLD: 5,
}
    const RECOVERY_TIMEOUT = 60000}
  }
RATE_LIMIT: {MAX_REQUESTS: 100,
}
    WINDOW_MS: 60000, // 1分钟}
  }
SECURITY: {ENABLE_CORS: true,
ENABLE_HELMET: true,
}
    const ENABLE_RATE_LIMITING = true}
  }
MONITORING: {ENABLE_METRICS: true,
ENABLE_LOGGING: true,
}
    const ENABLE_TRACING = true}
  }
};
// 服务端点配置'
export const SERVICE_ENDPOINTS = {'AUTH: {,'BASE_URL: '/api/v1/auth,''/,'/g,'/;
  endpoints: {,'LOGIN: '/login,''/,'/g,'/;
  REGISTER: '/register,''/,'/g,'/;
  REFRESH: '/refresh,''/,'/g,'/;
  LOGOUT: '/logout,''/,'/g,'/;
  VERIFY: '/verify,''/,'/g,'/;
  RESET_PASSWORD: '/reset-password,''/;'/g'/;
}
      const CHANGE_PASSWORD = '/change-password'}''/;'/g'/;
    }
  }
USER: {,'BASE_URL: '/api/v1/user,''/,'/g,'/;
  endpoints: {,'PROFILE: '/profile,''/,'/g,'/;
  UPDATE: '/update,''/,'/g,'/;
  DELETE: '/delete,''/,'/g,'/;
  PREFERENCES: '/preferences,''/;'/g'/;
}
      const SETTINGS = '/settings'}''/;'/g'/;
    }
  }
HEALTH_DATA: {,'BASE_URL: '/api/v1/health,''/,'/g,'/;
  endpoints: {,'DATA: '/data,''/,'/g,'/;
  METRICS: '/metrics,''/,'/g,'/;
  REPORTS: '/reports,''/,'/g,'/;
  SYNC: '/sync,''/,'/g,'/;
  EXPORT: '/export,''/;'/g'/;
}
      const IMPORT = '/import'}''/;'/g'/;
    }
  }
AGENTS: {,'BASE_URL: '/api/v1/agents,''/,'/g,'/;
  endpoints: {,'XIAOAI: '/xiaoai,''/,'/g,'/;
  XIAOKE: '/xiaoke,''/,'/g,'/;
  LAOKE: '/laoke,''/,'/g,'/;
  SOER: '/soer,''/,'/g,'/;
  STATUS: '/status,''/,'/g,'/;
  CHAT: '/chat,''/;'/g'/;
}
      const PERFORMANCE = '/performance'}''/;'/g'/;
    }
  }
DIAGNOSIS: {,'BASE_URL: '/api/v1/diagnosis,''/,'/g,'/;
  endpoints: {,'INQUIRY: '/inquiry,''/,'/g,'/;
  LISTEN: '/listen,''/,'/g,'/;
  LOOK: '/look,''/,'/g,'/;
  PALPATION: '/palpation,''/,'/g,'/;
  CALCULATION: '/calculation,''/,'/g,'/;
  COMPREHENSIVE: '/comprehensive,''/,'/g,'/;
  RESULTS: '/results,''/;'/g'/;
}
      const HISTORY = '/history'}''/;'/g'/;
    }
  }
RAG: {,'BASE_URL: '/api/v1/rag,''/,'/g,'/;
  endpoints: {,'QUERY: '/query,''/,'/g,'/;
  STREAM_QUERY: '/stream-query,''/,'/g,'/;
  KNOWLEDGE: '/knowledge,''/;'/g'/;
}
      const SEARCH = '/search'}''/;'/g'/;
    }
  }
BLOCKCHAIN: {,'BASE_URL: '/api/v1/blockchain,''/,'/g,'/;
  endpoints: {,'STORE: '/store,''/,'/g,'/;
  VERIFY: '/verify,''/,'/g,'/;
  RETRIEVE: '/retrieve,''/,'/g,'/;
  MINT: '/mint,''/;'/g'/;
}
      const TRANSFER = '/transfer'}''/;'/g'/;
    }
  }
MESSAGE_BUS: {,'BASE_URL: '/api/v1/messaging,''/,'/g,'/;
  endpoints: {,'PUBLISH: '/publish,''/,'/g,'/;
  SUBSCRIBE: '/subscribe,''/;'/g'/;
}
      const UNSUBSCRIBE = '/unsubscribe'}''/;'/g'/;
    }
  }
MEDICAL_RESOURCE: {,'BASE_URL: '/api/v1/medical,''/,'/g,'/;
  endpoints: {,'SEARCH: '/search,''/,'/g,'/;
  DETAILS: '/details,''/;'/g'/;
}
      const RECOMMENDATIONS = '/recommendations'}''/;'/g'/;
    }
  }
CORN_MAZE: {,'BASE_URL: '/api/v1/maze,''/,'/g,'/;
  endpoints: {,'GENERATE: '/generate,''/,'/g,'/;
  SOLVE: '/solve,''/;'/g'/;
}
      const PROGRESS = '/progress'}''/;'/g'/;
    }
  }
ACCESSIBILITY: {,'BASE_URL: '/api/v1/accessibility,''/,'/g,'/;
  endpoints: {,'SETTINGS: '/settings,''/,'/g,'/;
  FEATURES: '/features,''/;'/g'/;
}
      const SUPPORT = '/support'}''/;'/g'/;
    }
  }
SUOKE_BENCH: {,'BASE_URL: '/api/v1/benchmark,''/,'/g,'/;
  endpoints: {,'RUN: '/run,''/,'/g,'/;
  RESULTS: '/results,''/;'/g'/;
}
      const COMPARE = '/compare'}''/;'/g'/;
    }
  }
MED_KNOWLEDGE: {,'BASE_URL: '/api/v1/knowledge,''/,'/g,'/;
  endpoints: {,'SEARCH: '/search,''/,'/g,'/;
  GRAPH: '/graph,''/;'/g'/;
}
      const ONTOLOGY = '/ontology'}''/;'/g'/;
    }
  }
HUMAN_REVIEW: {,'BASE_URL: '/api/v1/review,''/,'/g,'/;
  endpoints: {,'SUBMIT: '/submit,''/,'/g,'/;
  STATUS: '/status,''/;'/g'/;
}
      const FEEDBACK = '/feedback'}''/;'/g'/;
    }
  }
INTEGRATION: {,'BASE_URL: '/api/v1/integration,''/,'/g,'/;
  endpoints: {,'CONNECT: '/connect,''/,'/g,'/;
  SYNC: '/sync,''/;'/g'/;
}
      const STATUS = '/status'}''/;'/g'/;
    }
  }
};
// 负载均衡配置'
export const LOAD_BALANCER_CONFIG = {'STRATEGIES: {,'ROUND_ROBIN: 'round_robin,';
LEAST_CONNECTIONS: 'least_connections,'
}
    const WEIGHTED = 'weighted'}
  }
HEALTH_CHECK: {INTERVAL: 30000,
TIMEOUT: 5000,
}
    const RETRIES = 3}
  }
};
// 缓存策略配置'
export const CACHE_STRATEGIES = {AUTH: {,'TTL: 3600000, // 1小时'/;'/g'/;
}
    const STRATEGY = 'memory'}
  }
USER_DATA: {,'TTL: 1800000, // 30分钟'/;'/g'/;
}
    const STRATEGY = 'hybrid'}
  }
HEALTH_DATA: {,'TTL: 300000, // 5分钟'/;'/g'/;
}
    const STRATEGY = 'storage'}
  }
STATIC_DATA: {,'TTL: 86400000, // 24小时'/;'/g'/;
}
    const STRATEGY = 'memory'}
  }
RAG_QUERIES: {,'TTL: 600000, // 10分钟'/;'/g'/;
}
    const STRATEGY = 'hybrid'}
  }
};
// 错误处理配置'
export const ERROR_HANDLING = {'ERROR_CATEGORIES: {,'NETWORK: 'network,';
AUTHENTICATION: 'auth,'
AUTHORIZATION: 'authz,'
VALIDATION: 'validation,'
BUSINESS_LOGIC: 'business,'
}
    const SYSTEM = 'system'}
  }
RETRY_STRATEGIES: {,'EXPONENTIAL_BACKOFF: 'exponential,'
LINEAR_BACKOFF: 'linear,'
}
    const FIXED_DELAY = 'fixed'}
  }
THRESHOLDS: {ERROR_RATE: 0.1, // 10%/,/g,/;
  RESPONSE_TIME: 5000, // 5秒
}
    TIMEOUT_RATE: 0.05, // 5%}
  }
};
// 安全配置'
export const SECURITY_CONFIG = {CORS: {,'const ALLOWED_ORIGINS = [;]'
      'http: //localhost:3000/;'/g'/;
      'http: //localhost:8081/;'/g'/;
      'https: //suoke.life''/;'/g'/;
];
    ];
ALLOWED_METHODS: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],'
ALLOWED_HEADERS: ['Content-Type', 'Authorization', 'X-Request-ID'],
}
    const CREDENTIALS = true}
  }
RATE_LIMITING: {WINDOW_MS: 60000, // 1分钟
}
    const MAX_REQUESTS = 100}
  }
INPUT_VALIDATION: {,'MAX_PAYLOAD_SIZE: '10mb,'
}
    const SANITIZE_INPUT = true}
  }
};
// 监控配置
export const MONITORING_CONFIG = {METRICS: {ENABLE_PROMETHEUS: true,;
ENABLE_CUSTOM_METRICS: true,
}
    COLLECTION_INTERVAL: 15000, // 15秒};
  }
LOGGING: {,'LEVEL: process.env.NODE_ENV === 'production' ? 'info' : 'debug,'
FORMAT: 'json,'
}
    const ENABLE_REQUEST_LOGGING = true}
  }
TRACING: {ENABLE_JAEGER: true,
}
    SAMPLE_RATE: 0.1, // 10%}
  }
HEALTH_CHECKS: {INTERVAL: 30000, // 30秒'/,'/g,'/;
  TIMEOUT: 5000, // 5秒'/;'/g'/;
}
    ENDPOINTS: ['/health', '/ready', '/live']'}''/;'/g'/;
  }
};
// 环境特定配置'
export const ENVIRONMENT_CONFIG = {'development: {,'GATEWAY_URL: 'http://localhost:8080,''/,'/g,'/;
  DEBUG: true,
ENABLE_MOCK: true,
}
    const LOG_LEVEL = 'debug'}
  }
staging: {,'GATEWAY_URL: 'https://staging-api.suoke.life,''/,'/g,'/;
  DEBUG: false,
ENABLE_MOCK: false,
}
    const LOG_LEVEL = 'info'}
  }
production: {,'GATEWAY_URL: 'https://api.suoke.life,''/,'/g,'/;
  DEBUG: false,
ENABLE_MOCK: false,
}
    const LOG_LEVEL = 'error'}
  }
};
// 获取环境配置'/,'/g'/;
export const getEnvironmentConfig = useCallback(() => {'const env = process.env.NODE_ENV || 'development';
}
  return ENVIRONMENT_CONFIG[env as keyof typeof ENVIRONMENT_CONFIG] || ENVIRONMENT_CONFIG.development}
};
// 构建完整URL的辅助函数
export buildUrl: useCallback((service: keyof typeof SERVICE_ENDPOINTS, endpoint?: string) => {const config = getEnvironmentConfig();
const serviceConfig = SERVICE_ENDPOINTS[service];
}
  if (!serviceConfig) {}
    const throw = new Error(`Unknown service: ${service;}`);````;```;
  }
  let url = `${config.GATEWAY_URL}${serviceConfig.BASE_URL}`;````,```;
if (endpoint && serviceConfig.endpoints[endpoint as keyof typeof serviceConfig.endpoints]) {}
    url += serviceConfig.endpoints[endpoint as keyof typeof serviceConfig.endpoints]}
  }
  return url;
};
// 默认导出
export default {GATEWAY_CONFIG}SERVICE_ENDPOINTS,;
LOAD_BALANCER_CONFIG,
CACHE_STRATEGIES,
ERROR_HANDLING,
SECURITY_CONFIG,
MONITORING_CONFIG,
ENVIRONMENT_CONFIG,
getEnvironmentConfig,
}
  buildUrl}
};
