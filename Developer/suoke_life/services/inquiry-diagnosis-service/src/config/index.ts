import dotenv from 'dotenv';
import path from 'path';

// 加载环境变量
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

// 配置对象
const config = {
  server: {
    port: process.env.PORT ? parseInt(process.env.PORT, 10) : 3007,
    host: process.env.HOST || 'localhost',
    protocol: process.env.SERVER_PROTOCOL || 'http',
    env: process.env.NODE_ENV || 'development',
    isDev: (process.env.NODE_ENV || 'development') === 'development',
    isProd: process.env.NODE_ENV === 'production',
    isTest: process.env.NODE_ENV === 'test'
  },
  database: {
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT ? parseInt(process.env.DB_PORT, 10) : 27017,
    name: process.env.DB_NAME || 'inquiry_diagnosis',
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    uri: process.env.DB_URI || `mongodb://${process.env.DB_HOST || 'localhost'}:${process.env.DB_PORT || '27017'}/${process.env.DB_NAME || 'inquiry_diagnosis'}`
  },
  auth: {
    jwtSecret: process.env.JWT_SECRET || 'default_jwt_secret_for_dev_only',
    jwtExpiresIn: process.env.JWT_EXPIRES_IN || '1d',
    apiKey: process.env.API_KEY || 'default_api_key_for_dev_only'
  },
  cors: {
    origin: process.env.CORS_ORIGIN || '*'
  },
  logs: {
    level: process.env.LOG_LEVEL || 'info'
  },
  services: {
    xiaoAi: {
      url: process.env.XIAOAI_SERVICE_URL || 'http://localhost:3000'
    },
    knowledgeBase: {
      url: process.env.KNOWLEDGE_BASE_SERVICE_URL || 'http://localhost:3001'
    },
    knowledgeGraph: {
      url: process.env.KNOWLEDGE_GRAPH_SERVICE_URL || 'http://localhost:3002'
    },
    tcmAnalysis: {
      url: process.env.TCM_ANALYSIS_SERVICE_URL || 'http://localhost:3003'
    },
    fourDiagnosisCoordinator: {
      url: process.env.FOUR_DIAGNOSIS_COORDINATOR_URL || 'http://localhost:3004',
      apiKey: process.env.COORDINATOR_API_KEY || 'default_coordinator_key',
      webhookUrl: process.env.COORDINATOR_WEBHOOK_URL || 'http://localhost:3007/api/coordinator/webhook'
    },
    healthProfile: {
      url: process.env.HEALTH_PROFILE_SERVICE_URL || 'http://localhost:3005'
    },
    ai: {
      enabled: process.env.AI_SERVICE_ENABLED === 'true',
      url: process.env.AI_SERVICE_URL || 'http://localhost:3006',
      apiKey: process.env.AI_SERVICE_API_KEY || 'default_ai_key'
    },
    llm: {
      url: process.env.LLM_SERVICE_URL || 'http://localhost:3008/api/llm'
    },
    nlp: {
      url: process.env.NLP_SERVICE_URL || 'http://localhost:3009/api/nlp'
    }
  },
  apiDocs: {
    enabled: process.env.ENABLE_API_DOCS === 'true' || process.env.NODE_ENV !== 'production',
    basicAuth: process.env.API_DOCS_BASIC_AUTH === 'true',
    username: process.env.API_DOCS_USERNAME || 'admin',
    password: process.env.API_DOCS_PASSWORD || 'suoke2024'
  },
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT ? parseInt(process.env.REDIS_PORT, 10) : 6379,
    password: process.env.REDIS_PASSWORD || '',
    db: process.env.REDIS_DB ? parseInt(process.env.REDIS_DB, 10) : 0
  },
  monitoring: {
    enabled: process.env.MONITORING_ENABLED === 'true',
    prometheusPort: process.env.PROMETHEUS_METRICS_PORT ? parseInt(process.env.PROMETHEUS_METRICS_PORT, 10) : 9090
  },
  tracing: {
    enabled: process.env.TRACING_ENABLED === 'true',
    jaegerHost: process.env.JAEGER_AGENT_HOST || 'localhost',
    jaegerPort: process.env.JAEGER_AGENT_PORT ? parseInt(process.env.JAEGER_AGENT_PORT, 10) : 6832
  },
  healthCheck: {
    interval: process.env.HEALTH_CHECK_INTERVAL ? parseInt(process.env.HEALTH_CHECK_INTERVAL, 10) : 30000
  }
};

export default config;