/**
 * 索儿服务配置管理
 */
const path = require('path');
const fs = require('fs');

// 默认配置
const defaultConfig = {
  version: '1.0.0',
  env: process.env.NODE_ENV || 'development',
  port: process.env.PORT || 3000,
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    format: 'json',
    tracing: true
  },
  database: {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT, 10) || 3306,
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || '',
    database: process.env.DB_NAME || 'soer_dev',
    connectionLimit: parseInt(process.env.DB_CONNECTION_LIMIT, 10) || 10,
    connectTimeout: parseInt(process.env.DB_CONNECT_TIMEOUT, 10) || 10000
  },
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT, 10) || 6379,
    password: process.env.REDIS_PASSWORD || '',
    db: parseInt(process.env.REDIS_DB, 10) || 0,
    keyPrefix: process.env.REDIS_PREFIX || 'soer:'
  },
  services: {
    userService: process.env.USER_SERVICE_URL || 'http://localhost:3001',
    contentService: process.env.CONTENT_SERVICE_URL || 'http://localhost:3002',
    notificationService: process.env.NOTIFICATION_SERVICE_URL || 'http://localhost:3003'
  },
  circuit_breaker: {
    timeout: parseInt(process.env.CIRCUIT_BREAKER_TIMEOUT, 10) || 5000,
    errorThresholdPercentage: parseInt(process.env.CIRCUIT_BREAKER_ERROR_THRESHOLD, 10) || 50,
    resetTimeout: parseInt(process.env.CIRCUIT_BREAKER_RESET_TIMEOUT, 10) || 10000
  },
  cors: {
    origin: '*',
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization']
  },
  rateLimit: {
    windowMs: 60000,
    max: 100
  },
  dependencies: []
};

// 加载环境特定配置
function loadConfig() {
  // 确定配置文件路径
  const env = process.env.NODE_ENV || 'development';
  let configPath;
  
  // 首先尝试在Kubernetes配置映射路径查找
  const k8sConfigPath = '/app/config/config.json';
  if (fs.existsSync(k8sConfigPath)) {
    configPath = k8sConfigPath;
  } else {
    // 回退到本地开发环境路径
    configPath = path.resolve(__dirname, '../../config', `${env === 'production' ? 'prod' : env}-config.json`);
  }
  
  let envConfig = {};
  
  // 尝试读取配置文件
  try {
    if (fs.existsSync(configPath)) {
      const configFile = fs.readFileSync(configPath, 'utf8');
      envConfig = JSON.parse(configFile);
      console.log(`已加载配置文件：${configPath}`);
    } else {
      console.warn(`未找到配置文件：${configPath}，将使用默认配置`);
    }
  } catch (error) {
    console.error(`加载配置文件失败：${error.message}`);
  }
  
  // 合并配置
  const mergedConfig = {
    ...defaultConfig,
    ...envConfig
  };
  
  // 环境变量优先级最高，覆盖配置文件值
  if (process.env.DB_HOST) mergedConfig.database.host = process.env.DB_HOST;
  if (process.env.DB_PORT) mergedConfig.database.port = parseInt(process.env.DB_PORT, 10);
  if (process.env.DB_USER) mergedConfig.database.user = process.env.DB_USER;
  if (process.env.DB_PASSWORD) mergedConfig.database.password = process.env.DB_PASSWORD;
  if (process.env.DB_NAME) mergedConfig.database.database = process.env.DB_NAME;
  
  if (process.env.REDIS_HOST) mergedConfig.redis.host = process.env.REDIS_HOST;
  if (process.env.REDIS_PORT) mergedConfig.redis.port = parseInt(process.env.REDIS_PORT, 10);
  if (process.env.REDIS_PASSWORD) mergedConfig.redis.password = process.env.REDIS_PASSWORD;
  
  if (process.env.LOG_LEVEL) mergedConfig.logging.level = process.env.LOG_LEVEL;
  
  return mergedConfig;
}

// 导出配置
module.exports = loadConfig();