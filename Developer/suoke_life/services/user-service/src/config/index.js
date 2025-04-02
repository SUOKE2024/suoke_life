/**
 * 用户服务配置文件
 */
require('dotenv').config();

module.exports = {
  // 服务配置
  serviceName: 'user-service',
  port: process.env.PORT || 3001,
  
  // 数据库配置
  database: {
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 3306,
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || '',
    database: process.env.DB_NAME || 'suoke_users',
    connectionLimit: parseInt(process.env.DB_CONNECTION_LIMIT || '10'),
    timezone: '+08:00'
  },
  
  // Redis配置
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT || 6379,
    password: process.env.REDIS_PASSWORD || '',
    db: parseInt(process.env.REDIS_DB || '0')
  },
  
  // JWT配置
  jwt: {
    secret: process.env.JWT_SECRET || 'suoke-life-secret-key',
    expiresIn: process.env.JWT_EXPIRES_IN || '7d',
    refreshExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '30d'
  },
  
  // 加密配置
  crypto: {
    saltRounds: parseInt(process.env.CRYPTO_SALT_ROUNDS || '10'),
    verificationTokenSecret: process.env.VERIFICATION_TOKEN_SECRET || 'suoke-verification-secret'
  },
  
  // 邮件配置
  email: {
    host: process.env.EMAIL_HOST || 'smtp.example.com',
    port: parseInt(process.env.EMAIL_PORT || '587'),
    secure: process.env.EMAIL_SECURE === 'true',
    auth: {
      user: process.env.EMAIL_USER || 'user@example.com',
      pass: process.env.EMAIL_PASS || 'password'
    },
    from: process.env.EMAIL_FROM || 'Suoke Life <noreply@suoke.life>'
  },
  
  // 短信配置
  sms: {
    provider: process.env.SMS_PROVIDER || 'aliyun',
    accessKeyId: process.env.SMS_ACCESS_KEY_ID || '',
    accessKeySecret: process.env.SMS_ACCESS_KEY_SECRET || '',
    signName: process.env.SMS_SIGN_NAME || '索克生活',
    templateCode: process.env.SMS_TEMPLATE_CODE || ''
  },
  
  // CORS配置
  cors: {
    origin: process.env.CORS_ORIGIN || '*',
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization']
  },
  
  // 缓存配置
  cache: {
    enabled: process.env.CACHE_ENABLED !== 'false',
    ttl: parseInt(process.env.CACHE_TTL || '3600', 10), // 默认缓存1小时
    enableRedis: process.env.CACHE_ENABLE_REDIS !== 'false' && process.env.REDIS_HOST,
    prefix: process.env.CACHE_PREFIX || 'suoke:user-service:',
    userTtl: parseInt(process.env.USER_CACHE_TTL || '1800') // 用户缓存30分钟
  },
  
  // 验证码配置
  verificationCode: {
    length: parseInt(process.env.VERIFICATION_CODE_LENGTH || '6'),
    expiresIn: parseInt(process.env.VERIFICATION_CODE_EXPIRES_IN || '300') // 5分钟
  },
  
  // 健康资料配置
  healthProfile: {
    privacyLevels: ['private', 'friends', 'public'],
    defaultPrivacyLevel: 'private',
    constitutionTypes: [
      '平和质', '气虚质', '阳虚质', '阴虚质', 
      '痰湿质', '湿热质', '血瘀质', '气郁质', '特禀质'
    ]
  },

  // 指标收集配置
  metrics: {
    enabled: process.env.METRICS_ENABLED === 'true',
    prefix: process.env.METRICS_PREFIX || 'user_',
    interval: parseInt(process.env.METRICS_INTERVAL || '15'),
    defaultLabels: {
      service: 'user-service',
      environment: process.env.NODE_ENV || 'development'
    }
  },

  // OpenAI兼容配置
  openai: {
    enabled: process.env.OPENAI_ENABLED === 'true',
    apiVersion: process.env.OPENAI_API_VERSION || '2023-07-01',
    apiKeyHeader: process.env.OPENAI_API_KEY_HEADER || 'X-OpenAI-Api-Key',
    toolsEnabled: process.env.OPENAI_TOOLS_ENABLED === 'true',
    responseFormat: process.env.OPENAI_RESPONSE_FORMAT || 'openai_compatible',
    endpointsPrefix: process.env.OPENAI_ENDPOINTS_PREFIX || '/api/v1/openai',
    toolsConfigPath: process.env.OPENAI_TOOLS_CONFIG_PATH || '/app/config/openai/openai-tools.json'
  },

  // 会话管理配置
  session: {
    maxConcurrentSessions: 5,
    terminateOldestOnExceed: true,
    trackDeviceInfo: true,
    invalidateOnPasswordChange: true
  },

  // 安全配置
  security: {
    encryption: {
      algorithm: 'aes-256-gcm',
      sensitiveFields: [
        'phone', 'email', 'birthdate', 'medicalHistory', 
        'healthData', 'geneticInfo', 'insuranceInfo'
      ]
    },
    sessionManagement: {
      maxConcurrentSessions: 5,
      terminateOldestOnExceed: true,
      trackDeviceInfo: true,
      invalidateOnPasswordChange: true
    },
    rateLimiting: {
      enabled: true,
      maxRequestsPerMin: 60,
      whitelistedIPs: [],
      blacklistedIPs: []
    }
  },

  // 依赖服务配置
  services: {
    auth: {
      url: process.env.AUTH_SERVICE_URL || 'http://auth-service',
      timeout: parseInt(process.env.AUTH_SERVICE_TIMEOUT || '5000')
    },
    constitution: {
      url: process.env.CONSTITUTION_SERVICE_URL || 'http://constitution-service',
      timeout: parseInt(process.env.CONSTITUTION_SERVICE_TIMEOUT || '5000')
    },
    storage: {
      url: process.env.STORAGE_SERVICE_URL || 'http://storage-service',
      timeout: parseInt(process.env.STORAGE_SERVICE_TIMEOUT || '5000')
    },
    payment: {
      url: process.env.PAYMENT_SERVICE_URL || 'http://payment-service',
      timeout: parseInt(process.env.PAYMENT_SERVICE_TIMEOUT || '5000')
    }
  },
  
  // 国际化配置
  i18n: {
    enabled: process.env.I18N_ENABLED !== 'false',
    defaultLanguage: process.env.I18N_DEFAULT_LANGUAGE || 'zh-CN',
    supportedLanguages: (process.env.I18N_SUPPORTED_LANGUAGES || 'zh-CN,en-US,zh-TW').split(','),
    detectFrom: (process.env.I18N_DETECT_FROM || 'header,query,cookie').split(','),
    fallbackLanguage: process.env.I18N_FALLBACK_LANGUAGE || 'zh-CN',
    storeLangInCookie: process.env.I18N_STORE_LANG_IN_COOKIE !== 'false'
  },

  // 日志配置
  logging: {
    level: process.env.LOG_LEVEL || (process.env.NODE_ENV === 'production' ? 'info' : 'debug'),
    format: process.env.LOG_FORMAT || 'json',
    directory: process.env.LOG_DIR || './logs',
    maxSize: process.env.LOG_MAX_SIZE || '10m',
    maxFiles: parseInt(process.env.LOG_MAX_FILES || '10', 10),
    console: process.env.LOG_CONSOLE !== 'false'
  }
}; 