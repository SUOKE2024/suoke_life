//////     应用配置常量
export const STORAGE_CONFIG = {
  KEYS: {
    AUTH_TOKEN: "@suoke_life:auth_token",
    REFRESH_TOKEN: "@suoke_life:refresh_token",
    USER_ID: "@suoke_life:user_id",
    USER_PREFERENCES: "@suoke_life:user_preferences",
    THEME: "@suoke_life:theme",
    LANGUAGE: "@suoke_life:language",
    DEVICE_ID: "@suoke_life:device_id"
  }
};

export const API_CONFIG = {
  BASE_URL: "https://api.suokelife.com",
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
  SERVICES: {
    AUTH: "/auth",
    USER: "/users",
    HEALTH: "/health",
    DIAGNOSIS: "/diagnosis",
    AGENTS: "/agents",
    RAG: "/rag",
    TCM: "/tcm",
    MED_KNOWLEDGE: "/med-knowledge"
  }
};

export const ERROR_CODES = {
  NETWORK_ERROR: "NETWORK_ERROR",
  OPERATION_FAILED: "OPERATION_FAILED",
  UNAUTHORIZED: "UNAUTHORIZED",
  FORBIDDEN: "FORBIDDEN",
  NOT_FOUND: "NOT_FOUND",
  VALIDATION_ERROR: "VALIDATION_ERROR",
  SERVER_ERROR: "SERVER_ERROR",
  TIMEOUT: "TIMEOUT"
};

export const APP_CONFIG = {
  NAME: "索克生活",
  VERSION: "1.0.0",
  BUILD_NUMBER: "1",
  ENVIRONMENT: process.env.NODE_ENV || "development"
};

export const THEME_CONFIG = {
  LIGHT: "light",
  DARK: "dark",
  SYSTEM: "system"
};

export const LANGUAGE_CONFIG = {
  ZH_CN: "zh-CN",
  EN_US: "en-US"
};

export const HEALTH_CONFIG = {
  VITAL_SIGNS: {
    HEART_RATE: { min: 60, max: 100 },
    BLOOD_PRESSURE: { systolic: { min: 90, max: 140 }, diastolic: { min: 60, max: 90 } },
    TEMPERATURE: { min: 36.1, max: 37.2 },
    OXYGEN_SATURATION: { min: 95, max: 100 }
  },
  ACTIVITY_GOALS: {
    DAILY_STEPS: 10000,
    WEEKLY_EXERCISE: 150, // minutes
    SLEEP_HOURS: 8,
    WATER_INTAKE: 2000 // ml
  }
};

export const NOTIFICATION_CONFIG = {
  TYPES: {
    HEALTH_REMINDER: "health_reminder",
    APPOINTMENT: "appointment",
    MEDICATION: "medication",
    EXERCISE: "exercise",
    SYSTEM: "system"
  },
  PRIORITIES: {
    LOW: "low",
    MEDIUM: "medium",
    HIGH: "high",
    URGENT: "urgent"
  }
};

// RAG服务配置
export const RAG_CONFIG = {
  SERVICE_URL: process.env.RAG_SERVICE_URL || "http://localhost:8080",
  TCM_SERVICE_URL: process.env.TCM_SERVICE_URL || "http://localhost:8081",
  ENDPOINTS: {
    QUERY: "/api/v1/query",
    STREAM_QUERY: "/api/v1/stream-query",
    MULTIMODAL_QUERY: "/api/v1/multimodal-query",
    TCM_ANALYSIS: "/api/v1/tcm/analysis",
    HERB_RECOMMENDATION: "/api/v1/tcm/herbs",
    SYNDROME_ANALYSIS: "/api/v1/tcm/syndrome",
    CONSTITUTION_ANALYSIS: "/api/v1/tcm/constitution",
    HEALTH_ASSESSMENT: "/api/v1/health/assessment",
    PREVENTION_ADVICE: "/api/v1/health/prevention"
  },
  CACHE: {
    TTL: 300000, // 5分钟
    MAX_SIZE: 100,
    ENABLE_PERSISTENCE: true
  },
  PERFORMANCE: {
    TIMEOUT: 30000, // 30秒
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000,
    STREAM_TIMEOUT: 60000 // 1分钟
  },
  FEATURES: {
    ENABLE_STREAMING: true,
    ENABLE_MULTIMODAL: true,
    ENABLE_TCM: true,
    ENABLE_OFFLINE: true,
    ENABLE_ANALYTICS: true
  }
};

// 环境特定配置
export const ENV_CONFIG = {
  development: {
    API_BASE_URL: "http://localhost:8000",
    MED_KNOWLEDGE_URL: "http://localhost:8007",
    RAG_SERVICE_URL: "http://localhost:8080",
    TCM_SERVICE_URL: "http://localhost:8081",
    BENCHMARK_SERVICE_URL: "http://localhost:8000",
    DEBUG: true,
    LOG_LEVEL: "debug",
    ENABLE_MOCK: true,
    CACHE_ENABLED: false
  },
  staging: {
    API_BASE_URL: "https://staging-api.suokelife.com",
    MED_KNOWLEDGE_URL: "https://staging-med-knowledge.suokelife.com",
    RAG_SERVICE_URL: "https://staging-rag.suokelife.com",
    TCM_SERVICE_URL: "https://staging-tcm.suokelife.com",
    BENCHMARK_SERVICE_URL: "https://staging-benchmark.suokelife.com",
    DEBUG: false,
    LOG_LEVEL: "info",
    ENABLE_MOCK: false,
    CACHE_ENABLED: true
  },
  production: {
    API_BASE_URL: "https://api.suokelife.com",
    MED_KNOWLEDGE_URL: "https://med-knowledge.suokelife.com",
    RAG_SERVICE_URL: "https://rag.suokelife.com",
    TCM_SERVICE_URL: "https://tcm.suokelife.com",
    BENCHMARK_SERVICE_URL: "https://benchmark.suokelife.com",
    DEBUG: false,
    LOG_LEVEL: "error",
    ENABLE_MOCK: false,
    CACHE_ENABLED: true
  }
};

// 获取当前环境配置
export const getCurrentEnvConfig = () => {
  const env = APP_CONFIG.ENVIRONMENT as keyof typeof ENV_CONFIG;
  return ENV_CONFIG[env] || ENV_CONFIG.development;
};