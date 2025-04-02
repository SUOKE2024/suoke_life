/**
 * 索儿服务配置模块
 * 基于环境变量和默认配置管理服务参数
 */
import dotenv from 'dotenv';
import path from 'path';

// 加载环境变量
dotenv.config();

// 环境配置
const env = process.env.NODE_ENV || 'development';

/**
 * 配置对象
 */
const config = {
  // 应用配置
  app: {
    name: 'soer-service',
    version: '1.0.0',
    env,
    port: parseInt(process.env.PORT || '3006', 10),
    host: process.env.HOST || '0.0.0.0',
    metricsPort: parseInt(process.env.METRICS_PORT || '9464', 10),
    logLevel: process.env.LOG_LEVEL || 'info',
    logDir: process.env.LOG_DIR || path.join(process.cwd(), 'logs')
  },
  
  // 数据库配置
  database: {
    host: process.env.DATABASE_HOST || 'localhost',
    port: parseInt(process.env.DATABASE_PORT || '27017', 10),
    name: process.env.DATABASE_NAME || 'soer_db',
    user: process.env.DATABASE_USER,
    password: process.env.DATABASE_PASSWORD,
    options: {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      serverSelectionTimeoutMS: 5000,
      socketTimeoutMS: 45000
    }
  },
  
  // Redis配置
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379', 10),
    password: process.env.REDIS_PASSWORD,
    ttl: {
      default: parseInt(process.env.CACHE_TTL || '3600', 10),
      knowledge: parseInt(process.env.KNOWLEDGE_CACHE_TTL || '7200', 10)
    }
  },
  
  // 微服务配置
  services: {
    health: process.env.HEALTH_SERVICE_URL || 'http://health-service:3002',
    lifeRecord: process.env.LIFE_RECORD_SERVICE_URL || 'http://life-record-service:3003',
    rag: process.env.RAG_SERVICE_URL || 'http://rag-service:3004',
    aiAgent: process.env.AI_AGENT_SERVICE_URL || 'http://ai-agent-service:3005',
    sensing: process.env.SENSING_SERVICE_URL || 'http://sensing-service:3007',
    knowledgeBase: process.env.KNOWLEDGE_BASE_URL || 'http://knowledge-base-service:3008',
    knowledgeGraph: process.env.KNOWLEDGE_GRAPH_URL || 'http://knowledge-graph-service:3009'
  },
  
  // 知识服务配置
  knowledge: {
    enabled: process.env.ENABLE_KNOWLEDGE_INTEGRATION === 'true',
    cacheTTL: parseInt(process.env.KNOWLEDGE_CACHE_TTL || '3600', 10),
    searchLimit: parseInt(process.env.KNOWLEDGE_SEARCH_LIMIT || '10', 10),
    graphDepth: parseInt(process.env.KNOWLEDGE_GRAPH_DEPTH || '2', 10),
    vectorDbUrl: process.env.VECTOR_DB_URL || 'http://vector-db:6333',
    semanticSearchThreshold: parseFloat(process.env.SEMANTIC_SEARCH_THRESHOLD || '0.75')
  },
  
  // 安全配置
  security: {
    authSecret: process.env.AUTH_SECRET || 'soer_auth_secret_key_1234567890',
    allowedOrigins: process.env.ALLOWED_ORIGINS ? process.env.ALLOWED_ORIGINS.split(',') : ['*'],
    apiRateLimit: parseInt(process.env.API_RATE_LIMIT || '100', 10)
  },
  
  // 模型配置
  model: {
    configPath: process.env.MODEL_CONFIG_PATH || path.join(process.cwd(), 'config/agent-config.json'),
    basePath: process.env.MODEL_BASE_PATH || path.join(process.cwd(), 'models')
  },
  
  // 指标监控配置
  metrics: {
    enabled: process.env.ENABLE_PROMETHEUS === 'true',
    prefix: 'soer_'
  },
  
  // OpenTelemetry配置
  telemetry: {
    enabled: process.env.ENABLE_TELEMETRY === 'true',
    serviceName: process.env.SERVICE_NAME || 'soer-service',
    serviceVersion: process.env.SERVICE_VERSION || '1.0.0',
    collectorUrl: process.env.OTEL_COLLECTOR_URL || 'http://opentelemetry-collector.monitoring:4318',
    samplingRatio: parseFloat(process.env.OTEL_TRACES_SAMPLER_ARG || '0.5')
  },
  
  // 断路器配置
  circuitBreaker: {
    timeout: parseInt(process.env.CIRCUIT_BREAKER_TIMEOUT || '5000', 10),
    errorThresholdPercentage: parseInt(process.env.CIRCUIT_BREAKER_ERROR_THRESHOLD || '50', 10),
    resetTimeout: parseInt(process.env.CIRCUIT_BREAKER_RESET_TIMEOUT || '10000', 10)
  }
};

export default config;