/**
 * 配置模块
 */
const path = require('path');
const fs = require('fs');
const dotenv = require('dotenv');

// 加载环境变量
dotenv.config();

// 尝试加载配置文件
let config;
try {
  const configPath = path.join(__dirname, '../../config/api-gateway.json');
  const configData = fs.readFileSync(configPath, 'utf8');
  
  // 替换环境变量占位符
  const configStr = configData.replace(/\${([^}]+)}/g, (_, varName) => {
    return process.env[varName] || '';
  });
  
  config = JSON.parse(configStr);
} catch (err) {
  console.warn('未能加载配置文件，使用默认配置:', err.message);
  
  // 默认配置
  config = {
    service: {
      name: 'api-gateway',
      version: '1.0.0',
      port: process.env.PORT || 3000,
      log_level: process.env.LOG_LEVEL || 'info',
      environment: process.env.NODE_ENV || 'development'
    },
    cors: {
      origin: process.env.CORS_ORIGIN || '*',
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization']
    },
    rate_limit: {
      window: parseInt(process.env.RATE_LIMIT_WINDOW || '60000', 10),
      max: parseInt(process.env.RATE_LIMIT_MAX || '100', 10),
      message: '请求过于频繁，请稍后再试'
    },
    services: []
  };
  
  // 添加环境变量中配置的服务
  if (process.env.USER_SERVICE_URL) {
    config.services.push({
      name: 'user-service',
      url: process.env.USER_SERVICE_URL,
      prefix: '/api/v1/users'
    });
  }
  
  if (process.env.AUTH_SERVICE_URL) {
    config.services.push({
      name: 'auth-service',
      url: process.env.AUTH_SERVICE_URL,
      prefix: '/api/v1/auth'
    });
  }
  
  if (process.env.KNOWLEDGE_GRAPH_SERVICE_URL) {
    config.services.push({
      name: 'knowledge-graph-service',
      url: process.env.KNOWLEDGE_GRAPH_SERVICE_URL,
      prefix: '/api/v1/knowledge/graph'
    });
  }
  
  if (process.env.KNOWLEDGE_BASE_SERVICE_URL) {
    config.services.push({
      name: 'knowledge-base-service',
      url: process.env.KNOWLEDGE_BASE_SERVICE_URL,
      prefix: '/api/v1/knowledge/base'
    });
  }
  
  if (process.env.RAG_SERVICE_URL) {
    config.services.push({
      name: 'rag-service',
      url: process.env.RAG_SERVICE_URL,
      prefix: '/api/v1/rag'
    });
  }
  
  if (process.env.AGENT_COORDINATOR_SERVICE_URL) {
    config.services.push({
      name: 'agent-coordinator-service',
      url: process.env.AGENT_COORDINATOR_SERVICE_URL,
      prefix: '/api/v1/agents/coordinate'
    });
  }
}

module.exports = config;