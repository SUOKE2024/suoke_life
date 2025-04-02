/**
 * 配置模块索引
 * 导出所有配置模块
 */

// 导入配置模块
const jwt = require('./jwt');
const database = require('./database');

/**
 * 整合所有配置项
 */
const config = {
  // 环境配置
  env: process.env.NODE_ENV || 'development',
  
  // 服务配置
  server: {
    port: process.env.PORT || 3000,
    host: process.env.HOST || 'localhost',
    baseUrl: process.env.BASE_URL || 'http://localhost:3000',
    apiPrefix: process.env.API_PREFIX || '/api'
  },
  
  // JWT配置
  jwt,
  
  // 数据库配置
  database: database.config,
  
  // 安全配置
  security: {
    encryptionKey: process.env.ENCRYPTION_KEY || 'suoke-life-encryption-key-dev-only',
    bcryptSaltRounds: 10,
    corsOptions: {
      origin: process.env.CORS_ORIGIN || '*',
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
      credentials: true
    }
  },
  
  // 日志配置
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    directory: process.env.LOG_DIR || 'logs'
  },
  
  // 文件上传配置
  upload: {
    maxSize: process.env.UPLOAD_MAX_SIZE || 5 * 1024 * 1024, // 5MB
    allowedMimeTypes: [
      'image/jpeg', 
      'image/png', 
      'image/gif', 
      'application/pdf', 
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ],
    destination: process.env.UPLOAD_DESTINATION || 'uploads'
  },
  
  // 缓存配置
  cache: {
    ttl: process.env.CACHE_TTL || 3600, // 默认1小时
    checkPeriod: process.env.CACHE_CHECK_PERIOD || 600 // 默认10分钟
  },
  
  // 第三方服务配置
  services: {
    smtp: {
      host: process.env.SMTP_HOST,
      port: process.env.SMTP_PORT || 587,
      secure: process.env.SMTP_SECURE === 'true',
      auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS
      },
      from: process.env.SMTP_FROM || '"索克生活" <noreply@suoke.life>'
    },
    sms: {
      provider: process.env.SMS_PROVIDER || 'aliyun',
      accessKeyId: process.env.SMS_ACCESS_KEY_ID,
      accessKeySecret: process.env.SMS_ACCESS_KEY_SECRET,
      signName: process.env.SMS_SIGN_NAME || '索克生活'
    }
  }
};

module.exports = config; 