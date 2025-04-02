/**
 * 配置文件
 */
const path = require('path');
require('dotenv').config({ path: path.resolve(process.cwd(), '.env') });

// 默认配置
const defaultConfig = require('./default');

// 根据环境加载特定配置
let envConfig = {};
const env = process.env.NODE_ENV || 'development';

try {
  envConfig = require(`./${env}`);
} catch (error) {
  console.log(`未找到环境配置文件: ${env}.js，使用默认配置`);
}

// 合并配置
const config = {
  ...defaultConfig,
  ...envConfig,
  env
};

/**
 * 索克生活认证服务配置
 */

/**
 * 服务器配置
 */
const server = {
  port: process.env.PORT || 3000,
  host: process.env.HOST || 'localhost',
  env: process.env.NODE_ENV || 'development'
};

/**
 * 安全配置
 */
const security = {
  jwt: {
    secret: process.env.JWT_SECRET || 'suoke-auth-secret-key-dev',
    expiresIn: process.env.JWT_EXPIRES_IN || '24h',
    refreshExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '7d'
  },
  passwordHash: {
    saltRounds: parseInt(process.env.PASSWORD_SALT_ROUNDS || '10', 10)
  }
};

/**
 * 跨域资源共享配置
 */
const cors = {
  origin: process.env.CORS_ORIGIN ? process.env.CORS_ORIGIN.split(',') : '*',
  methods: 'GET,HEAD,PUT,PATCH,POST,DELETE',
  preflightContinue: false,
  optionsSuccessStatus: 204,
  credentials: true
};

/**
 * 会话配置
 */
const session = {
  secret: process.env.SESSION_SECRET || 'suoke-session-secret-dev',
  name: 'suoke.sid',
  ttl: parseInt(process.env.SESSION_TTL || '86400', 10)
};

/**
 * Cookie配置
 */
const cookies = {
  secret: process.env.COOKIE_SECRET || 'suoke-cookie-secret-dev',
  options: {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 24 * 60 * 60 * 1000 // 24小时
  }
};

/**
 * 日志配置
 */
const logs = {
  level: process.env.LOG_LEVEL || 'info',
  dir: process.env.LOG_DIR || 'logs',
  maxSize: process.env.LOG_MAX_SIZE || '10m',
  maxFiles: process.env.LOG_MAX_FILES || '7d'
};

/**
 * 监控指标配置
 */
const metrics = {
  enabled: process.env.METRICS_ENABLED !== 'false',
  prefix: process.env.METRICS_PREFIX || 'suoke_auth_',
  defaultLabels: {
    service: 'auth-service'
  }
};

/**
 * Redis配置
 */
const redis = {
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT || '6379', 10),
  password: process.env.REDIS_PASSWORD || '',
  db: parseInt(process.env.REDIS_DB || '0', 10)
};

/**
 * 短信配置
 */
const sms = {
  provider: process.env.SMS_PROVIDER || 'aliyun',
  accessKeyId: process.env.SMS_ACCESS_KEY_ID,
  accessKeySecret: process.env.SMS_ACCESS_KEY_SECRET,
  signName: process.env.SMS_SIGN_NAME || '索克生活',
  templateCode: process.env.SMS_TEMPLATE_CODE,
  codeLength: parseInt(process.env.SMS_CODE_LENGTH || '6', 10),
  codeExpiration: parseInt(process.env.SMS_CODE_EXPIRATION || '300', 10) // 秒
};

/**
 * 导出配置
 */
module.exports = {
  server,
  security,
  cors,
  session,
  cookies,
  logs,
  metrics,
  redis,
  sms
}; 