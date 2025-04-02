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
    name: 'xiaoke-service',
    version: '1.0.0',
    env,
    port: parseInt(process.env.PORT || '3011', 10),
    metricsPort: parseInt(process.env.METRICS_PORT || '9464', 10),
    logLevel: process.env.LOG_LEVEL || 'info',
    logDir: process.env.LOG_DIR || path.join(process.cwd(), 'logs')
  },
  
  // MongoDB配置
  mongodb: {
    uri: process.env.MONGODB_URI || 'mongodb://localhost:27017/xiaoke-service',
    options: {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      serverSelectionTimeoutMS: 5000,
      socketTimeoutMS: 45000
    },
    user: process.env.MONGODB_USER,
    password: process.env.MONGODB_PASSWORD
  },
  
  // Redis配置
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379', 10),
    password: process.env.REDIS_PASSWORD,
    ttl: {
      default: parseInt(process.env.CACHE_TTL || '3600', 10),
      product: parseInt(process.env.PRODUCT_CACHE_TTL || '86400', 10),
      order: parseInt(process.env.ORDER_CACHE_TTL || '1800', 10)
    }
  },
  
  // 供应链API配置
  supplyChainApi: {
    key: process.env.SUPPLY_CHAIN_API_KEY,
    url: process.env.SUPPLY_CHAIN_API_URL || 'http://supply-chain-api:8080/api/v1'
  },
  
  // 区块链配置
  blockchain: {
    endpoint: process.env.BLOCKCHAIN_ENDPOINT || 'http://blockchain-node:8545',
    apiKey: process.env.BLOCKCHAIN_API_KEY,
    productTrackerContract: process.env.PRODUCT_TRACKER_CONTRACT
  },
  
  // 第三方API配置
  thirdPartyApis: {
    weather: {
      key: process.env.WEATHER_API_KEY,
      url: process.env.WEATHER_API_URL || 'https://api.weather.com'
    },
    logistics: {
      key: process.env.LOGISTICS_API_KEY,
      url: process.env.LOGISTICS_API_URL || 'https://api.logistics-provider.com'
    }
  },
  
  // 微服务配置
  services: {
    auth: process.env.AUTH_SERVICE_URL || 'http://auth-service:3000',
    user: process.env.USER_SERVICE_URL || 'http://user-service:3001',
    rag: process.env.RAG_SERVICE_URL || 'http://rag-service:3002'
  },
  
  // 知识服务配置
  knowledge: {
    serviceUrl: process.env.KNOWLEDGE_SERVICE_URL || 'http://knowledge-service:3012/api/knowledge',
    graphUrl: process.env.KNOWLEDGE_GRAPH_URL || 'http://knowledge-graph-service:3013/api/graph',
    apiKey: process.env.KNOWLEDGE_API_KEY,
    cacheTTL: parseInt(process.env.KNOWLEDGE_CACHE_TTL || '7200', 10),
    vectorDbUrl: process.env.VECTOR_DB_URL || 'http://vector-db:6333',
    semanticSearchThreshold: parseFloat(process.env.SEMANTIC_SEARCH_THRESHOLD || '0.75')
  },
  
  // 智能体配置
  agent: {
    configPath: process.env.AGENT_CONFIG_PATH || path.join(process.cwd(), 'config/agent-config.json'),
    modelPath: process.env.LLM_MODEL_PATH || '/app/models/supply-chain-llm-v1.0.0.onnx',
    embeddingModelPath: process.env.EMBEDDING_MODEL_PATH || '/app/models/tcm-embedding-model.onnx'
  },
  
  // 安全配置
  security: {
    jwtSecret: process.env.JWT_SECRET || 'your-secret-key-here',
    apiRateLimit: parseInt(process.env.API_RATE_LIMIT || '100', 10),
    corsOrigins: process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(',') : ['*']
  },
  
  // 指标监控配置
  metrics: {
    enabled: process.env.ENABLE_PROMETHEUS === 'true',
    prefix: 'xiaoke_'
  }
};

export default config; 