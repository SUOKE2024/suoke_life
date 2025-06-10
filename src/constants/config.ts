/* 置 *//;/g/;
 *//;/g/;

// API密钥配置/;,/g/;
export const API_KEYS = {;,}OPENAI: process.env.OPENAI_API_KEY || '';','';
ANTHROPIC: process.env.ANTHROPIC_API_KEY || ';',';,'';
GOOGLE: process.env.GOOGLE_API_KEY || ';',';,'';
AZURE: process.env.AZURE_API_KEY || ';',';,'';
BAIDU: process.env.BAIDU_API_KEY || ';',';,'';
TENCENT: process.env.TENCENT_API_KEY || ';',';'';
}
  const ALIBABA = process.env.ALIBABA_API_KEY || ';'}'';'';
};

// 应用基础配置'/;,'/g'/;
export const APP_CONFIG = {';,}NAME: 'Suoke Life';','';
VERSION: '1.0.0';','';
ENVIRONMENT: process.env.NODE_ENV || 'development';','';
DEBUG: process.env.DEBUG === 'true';','';
API_TIMEOUT: 30000,;
RETRY_ATTEMPTS: 3,;
CACHE_TTL: 300000, // 5分钟/;,/g,/;
  AGENTS: {RESPONSE_TIMEOUT: 30000,;
MAX_RETRIES: 3,;
}
    const CONCURRENT_LIMIT = 5;}
  }
};

// API网关配置'/;,'/g'/;
export const API_GATEWAY_CONFIG = {';,}BASE_URL: process.env.GATEWAY_URL || 'http://localhost:8080';',''/;,'/g,'/;
  TIMEOUT: 30000,;
RETRY_ATTEMPTS: 3,;
SERVICES: {,';,}AUTH: {,';,}BASE_URL: '/api/v1/auth';',''/;,'/g,'/;
  ENDPOINTS: {,';,}LOGIN: '/login';',''/;,'/g,'/;
  REGISTER: '/register';',''/;,'/g,'/;
  REFRESH: '/refresh';',''/;'/g'/;
}
        const LOGOUT = '/logout';'}''/;'/g'/;
      }
    }
';,'';
USER: {,';,}BASE_URL: '/api/v1/user';',''/;,'/g,'/;
  ENDPOINTS: {,';,}PROFILE: '/profile';',''/;,'/g,'/;
  UPDATE: '/update';',''/;'/g'/;
}
        const DELETE = '/delete';'}''/;'/g'/;
      }
    }
';,'';
HEALTH: {,';,}BASE_URL: '/api/v1/health';',''/;,'/g,'/;
  ENDPOINTS: {,';,}DATA: '/data';',''/;,'/g,'/;
  METRICS: '/metrics';',''/;'/g'/;
}
        const REPORTS = '/reports';'}''/;'/g'/;
      }
    }
';,'';
AGENTS: {,';,}BASE_URL: '/api/v1/agents';',''/;,'/g,'/;
  ENDPOINTS: {,';,}XIAOAI: '/xiaoai';',''/;,'/g,'/;
  XIAOKE: '/xiaoke';',''/;,'/g,'/;
  LAOKE: '/laoke';',''/;'/g'/;
}
        const SOER = '/soer';'}''/;'/g'/;
      }
    }
';,'';
DIAGNOSIS: {,';,}BASE_URL: '/api/v1/diagnosis';',''/;,'/g,'/;
  ENDPOINTS: {,';,}INQUIRY: '/inquiry';',''/;,'/g,'/;
  LISTEN: '/listen';',''/;,'/g,'/;
  LOOK: '/look';',''/;,'/g,'/;
  PALPATION: '/palpation';',''/;'/g'/;
}
        const CALCULATION = '/calculation';'}''/;'/g'/;
      }
    }
';,'';
RAG: {,';,}BASE_URL: '/api/v1/rag';',''/;,'/g,'/;
  ENDPOINTS: {,';,}QUERY: '/query';',''/;,'/g,'/;
  KNOWLEDGE: '/knowledge';',''/;'/g'/;
}
        const SEARCH = '/search';'}''/;'/g'/;
      }
    }
';,'';
BLOCKCHAIN: {,';,}BASE_URL: '/api/v1/blockchain';',''/;,'/g,'/;
  ENDPOINTS: {,';,}STORE: '/store';',''/;,'/g,'/;
  VERIFY: '/verify';',''/;'/g'/;
}
        const RETRIEVE = '/retrieve';'}''/;'/g'/;
      }
    }
  }
};

// 获取服务URL的辅助函数/;,/g/;
export const getServiceUrl = (service: keyof typeof API_GATEWAY_CONFIG.SERVICES);
) => {};
return `${API_GATEWAY_CONFIG.BASE_URL;}${API_GATEWAY_CONFIG.SERVICES[service].BASE_URL}`;````;```;
};

// 获取智能体URL的辅助函数/;,/g/;
export const getAgentUrl = (agent: keyof typeof API_GATEWAY_CONFIG.SERVICES.AGENTS.ENDPOINTS)';'';
) => {'}'';
return `${getServiceUrl('AGENTS');}${API_GATEWAY_CONFIG.SERVICES.AGENTS.ENDPOINTS[agent]}`;````;```;
};

// 获取诊断服务URL的辅助函数/;,/g/;
export const getDiagnosisUrl = (diagnosis: keyof typeof API_GATEWAY_CONFIG.SERVICES.DIAGNOSIS.ENDPOINTS)';'';
) => {'}'';
return `${getServiceUrl('DIAGNOSIS');}${API_GATEWAY_CONFIG.SERVICES.DIAGNOSIS.ENDPOINTS[diagnosis]}`;````;```;
};

// 健康数据配置/;,/g/;
export const HEALTH_CONFIG = {SYNC_INTERVAL: 60000, // 1分钟/;,}BATCH_SIZE: 100,;,/g,/;
  MAX_HISTORY_DAYS: 365,;

}
  VITAL_SIGNS: {,};
HEART_RATE: { MIN: 60, MAX: 100 ;}
BLOOD_PRESSURE: {,}
      SYSTOLIC: { MIN: 90, MAX: 140 ;}
DIASTOLIC: { MIN: 60, MAX: 90 ;}
    }
TEMPERATURE: { MIN: 36.0, MAX: 37.5 ;}
  }
ACTIVITY_GOALS: {STEPS: 10000,;
CALORIES: 2000,;
}
    const EXERCISE_MINUTES = 30;}
  }
};

// 诊断配置/;,/g/;
export const DIAGNOSIS_CONFIG = {const TYPES = {}}
};
  ;}
PRIORITIES: {LOW: 1,;
MEDIUM: 2,;
HIGH: 3,;
}
    const CRITICAL = 4;}
  }
const TIMEOUT = 30000;
};

// 缓存配置/;,/g/;
export const CACHE_CONFIG = {';,}STRATEGIES: {,';,}MEMORY: 'memory';','';
STORAGE: 'storage';','';'';
}
    const HYBRID = 'hybrid';'}'';'';
  }
TTL: {SHORT: 60000, // 1分钟/;,/g,/;
  MEDIUM: 300000, // 5分钟/;/g/;
}
    LONG: 3600000, // 1小时}/;/g/;
  ;}
};

// 错误处理配置/;,/g/;
export const ERROR_CONFIG = {CIRCUIT_BREAKER: {FAILURE_THRESHOLD: 5,;
RECOVERY_TIMEOUT: 60000,;
}
    const MONITOR_TIMEOUT = 30000;}
  }
RETRY: {MAX_ATTEMPTS: 3,;
DELAY: 1000,;
}
    const BACKOFF_FACTOR = 2;}
  }
};

// 存储配置'/;,'/g'/;
export const STORAGE_CONFIG = {';,}PREFIX: 'suoke_life_';','';
VERSION: '1.0.0';','';'';
}
  const ENCRYPTION = true;}
};

// 环境特定配置/;,/g/;
export const ENV_CONFIG = {';,}development: {,';,}GATEWAY_URL: 'http://localhost:8080';',''/;,'/g,'/;
  ENABLE_LOGGING: true,;
ENABLE_DEBUG: true,;
ENABLE_MOCK_DATA: true,;
}
    const ENABLE_GATEWAY_MONITOR = true;}
  }
';,'';
staging: {,';,}GATEWAY_URL: 'https://staging-api.suoke.life';',''/;,'/g,'/;
  ENABLE_LOGGING: true,;
ENABLE_DEBUG: false,;
ENABLE_MOCK_DATA: false,;
}
    const ENABLE_GATEWAY_MONITOR = true;}
  }
';,'';
production: {,';,}GATEWAY_URL: 'https://api.suoke.life';',''/;,'/g,'/;
  ENABLE_LOGGING: false,;
ENABLE_DEBUG: false,;
ENABLE_MOCK_DATA: false,;
}
    const ENABLE_GATEWAY_MONITOR = false;}
  }
};

// 获取当前环境配置/;,/g/;
export const getCurrentEnvConfig = useCallback(() => {;,}const env = APP_CONFIG.ENVIRONMENT as keyof typeof ENV_CONFIG;
}
  return ENV_CONFIG[env] || ENV_CONFIG.development;}
};

// 默认导出/;,/g/;
export default {API_KEYS}APP_CONFIG,;
API_GATEWAY_CONFIG,;
HEALTH_CONFIG,;
DIAGNOSIS_CONFIG,;
CACHE_CONFIG,;
ERROR_CONFIG,;
STORAGE_CONFIG,;
ENV_CONFIG,;
getCurrentEnvConfig,;
getServiceUrl,;
getAgentUrl,;
}
  getDiagnosisUrl,};
};';'';
''';