/**
 * 默认配置文件
 */
module.exports = {
  // 环境设置
  env: process.env.NODE_ENV || 'development',
  
  // 服务端口
  port: parseInt(process.env.PORT || '3001'),
  
  // 数据库配置
  database: {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '3306'),
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || '',
    database: process.env.DB_NAME || 'suoke_auth',
    connectionLimit: parseInt(process.env.DB_CONNECTION_LIMIT || '10')
  },
  
  // Redis配置
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379'),
    password: process.env.REDIS_PASSWORD || '',
    db: parseInt(process.env.REDIS_DB || '0')
  },
  
  // JWT配置
  jwt: {
    secret: process.env.JWT_SECRET || 'suoke_auth_secret_key',
    accessTokenExpiry: parseInt(process.env.JWT_ACCESS_TOKEN_EXPIRY || '86400'), // 默认1天
    refreshTokenExpiry: parseInt(process.env.JWT_REFRESH_TOKEN_EXPIRY || '604800') // 默认7天
  },
  
  // CORS配置
  cors: {
    origins: process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(',') : ['*'],
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization']
  },
  
  // 认证配置
  authentication: {
    // 密码登录
    passwordLogin: {
      enabled: process.env.PASSWORD_LOGIN_ENABLED !== 'false',
      maxFailedAttempts: parseInt(process.env.MAX_FAILED_LOGIN_ATTEMPTS || '5'),
      lockoutDuration: parseInt(process.env.LOCKOUT_DURATION || '900') // 15分钟
    },
    
    // 手机号登录
    phoneLogin: {
      enabled: process.env.PHONE_LOGIN_ENABLED !== 'false',
      dailyLimit: parseInt(process.env.PHONE_LOGIN_DAILY_LIMIT || '10'),
      codeExpiration: parseInt(process.env.PHONE_LOGIN_CODE_EXPIRATION || '300') // 5分钟
    },
    
    // JWT配置
    jwt: {
      accessTokenExpiry: parseInt(process.env.JWT_ACCESS_TOKEN_EXPIRY || '86400'), // 默认1天
      refreshTokenExpiry: parseInt(process.env.JWT_REFRESH_TOKEN_EXPIRY || '604800'), // 默认7天
      secret: process.env.JWT_SECRET || 'suoke_auth_secret_key'
    }
  },
  
  // OAuth配置
  oauth: {
    // 微信
    wechat: {
      enabled: process.env.WECHAT_OAUTH_ENABLED === 'true',
      appId: process.env.WECHAT_APP_ID,
      appSecret: process.env.WECHAT_APP_SECRET,
      callbackUrl: process.env.WECHAT_CALLBACK_URL || '/api/auth/oauth/wechat/callback'
    },
    
    // 支付宝
    alipay: {
      enabled: process.env.ALIPAY_OAUTH_ENABLED === 'true',
      appId: process.env.ALIPAY_APP_ID,
      privateKey: process.env.ALIPAY_PRIVATE_KEY,
      publicKey: process.env.ALIPAY_PUBLIC_KEY,
      callbackUrl: process.env.ALIPAY_CALLBACK_URL || '/api/auth/oauth/alipay/callback'
    }
  },
  
  // 短信服务配置
  sms: {
    // 默认短信提供商，可选 'alicloud'、'tencent'、'test'
    provider: process.env.SMS_PROVIDER || 'test',
    
    // 验证码配置
    verification: {
      codeLength: parseInt(process.env.SMS_CODE_LENGTH || '6'), // 验证码长度
      expiry: parseInt(process.env.SMS_CODE_EXPIRY || '300'), // 验证码有效期（秒）
      maxAttempts: parseInt(process.env.SMS_MAX_ATTEMPTS || '3'), // 最大尝试次数
      throttleLimit: parseInt(process.env.SMS_THROTTLE_LIMIT || '60') // 发送频率限制（秒）
    },
    
    // 提供商配置
    providers: {
      // 阿里云短信服务
      alicloud: {
        accessKeyId: process.env.ALICLOUD_SMS_ACCESS_KEY_ID,
        accessKeySecret: process.env.ALICLOUD_SMS_ACCESS_KEY_SECRET,
        endpoint: process.env.ALICLOUD_SMS_ENDPOINT || 'dysmsapi.aliyuncs.com',
        apiVersion: process.env.ALICLOUD_SMS_API_VERSION || '2017-05-25',
        signName: process.env.ALICLOUD_SMS_SIGN_NAME || '索克生活',
        templateCode: process.env.ALICLOUD_SMS_TEMPLATE_CODE
      },
      
      // 腾讯云短信服务
      tencent: {
        secretId: process.env.TENCENT_SMS_SECRET_ID,
        secretKey: process.env.TENCENT_SMS_SECRET_KEY,
        endpoint: process.env.TENCENT_SMS_ENDPOINT || 'sms.tencentcloudapi.com',
        region: process.env.TENCENT_SMS_REGION || 'ap-guangzhou',
        sdkAppId: process.env.TENCENT_SMS_SDK_APP_ID,
        signName: process.env.TENCENT_SMS_SIGN_NAME || '索克生活',
        templateId: process.env.TENCENT_SMS_TEMPLATE_ID
      }
    }
  },
  
  // 邮件服务配置
  email: {
    enabled: process.env.EMAIL_ENABLED !== 'false',
    provider: process.env.EMAIL_PROVIDER || 'smtp',
    defaultFrom: process.env.EMAIL_DEFAULT_FROM || '"索克生活" <noreply@suoke.life>',
    baseUrl: process.env.EMAIL_BASE_URL || 'https://app.suoke.life',
    
    // SMTP配置
    smtp: {
      host: process.env.EMAIL_SMTP_HOST || 'smtp.example.com',
      port: parseInt(process.env.EMAIL_SMTP_PORT || '587'),
      secure: process.env.EMAIL_SMTP_SECURE === 'true',
      user: process.env.EMAIL_SMTP_USER,
      password: process.env.EMAIL_SMTP_PASSWORD
    },
    
    // SendGrid配置
    sendgrid: {
      apiKey: process.env.SENDGRID_API_KEY,
      user: process.env.SENDGRID_USER || 'apikey'
    },
    
    // 阿里云邮件配置
    aliyun: {
      accessKeyId: process.env.ALIYUN_EMAIL_ACCESS_KEY_ID,
      accessKeySecret: process.env.ALIYUN_EMAIL_ACCESS_KEY_SECRET,
      accountName: process.env.ALIYUN_EMAIL_ACCOUNT_NAME,
      fromAlias: process.env.ALIYUN_EMAIL_FROM_ALIAS || '索克生活',
      user: process.env.ALIYUN_EMAIL_USER,
      password: process.env.ALIYUN_EMAIL_PASSWORD
    },
    
    // 邮件模板配置
    templates: {
      welcome: {
        subject: '欢迎加入索克生活',
        templateId: process.env.EMAIL_TEMPLATE_WELCOME_ID
      },
      resetPassword: {
        subject: '密码重置 - 索克生活',
        templateId: process.env.EMAIL_TEMPLATE_RESET_PASSWORD_ID,
        expiry: parseInt(process.env.PASSWORD_RESET_EXPIRY || '3600') // 1小时
      },
      verifyEmail: {
        subject: '邮箱验证 - 索克生活',
        templateId: process.env.EMAIL_TEMPLATE_VERIFY_EMAIL_ID,
        expiry: parseInt(process.env.EMAIL_VERIFY_EXPIRY || '86400') // 24小时
      }
    }
  },
  
  // 安全配置
  security: {
    // 密码策略
    passwordPolicy: {
      minLength: parseInt(process.env.PASSWORD_MIN_LENGTH || '10'), // 最小长度
      requireLowercase: process.env.PASSWORD_REQUIRE_LOWERCASE !== 'false', // 要求小写字母
      requireUppercase: process.env.PASSWORD_REQUIRE_UPPERCASE !== 'false', // 要求大写字母
      requireNumbers: process.env.PASSWORD_REQUIRE_NUMBERS !== 'false', // 要求数字
      requireSpecialChars: process.env.PASSWORD_REQUIRE_SPECIAL_CHARS !== 'false', // 要求特殊字符
      maxRepeatingChars: parseInt(process.env.PASSWORD_MAX_REPEATING_CHARS || '3'), // 最大重复字符
      preventCommonPasswords: process.env.PASSWORD_PREVENT_COMMON !== 'false' // 防止常见密码
    },
    
    // 高级保护
    advancedProtection: {
      // 泄露密码检查
      breachedPasswordCheck: {
        enabled: process.env.BREACHED_PASSWORD_CHECK_ENABLED !== 'false', // 是否启用
        apiEndpoint: process.env.BREACHED_PASSWORD_API_ENDPOINT || 'https://api.pwnedpasswords.com/range/', // API端点
        cacheResults: process.env.BREACHED_PASSWORD_CACHE_RESULTS !== 'false', // 缓存结果
        cacheTTL: parseInt(process.env.BREACHED_PASSWORD_CACHE_TTL || '86400') // 缓存有效期（秒）
      }
    },
    
    // 二因素认证配置
    twoFactor: {
      enabled: process.env.TWO_FACTOR_ENABLED !== 'false', // 是否启用
      forceForAdmins: process.env.TWO_FACTOR_FORCE_FOR_ADMINS !== 'false', // 管理员必须启用
      forceForSensitiveOperations: process.env.TWO_FACTOR_FORCE_FOR_SENSITIVE !== 'false', // 敏感操作必须使用
      availableMethods: process.env.TWO_FACTOR_METHODS ? process.env.TWO_FACTOR_METHODS.split(',') : ['totp', 'sms'], // 可用的二因素认证方法
      totpWindowSize: parseInt(process.env.TOTP_WINDOW_SIZE || '1'), // TOTP窗口大小
      recoveryCodesCount: parseInt(process.env.RECOVERY_CODES_COUNT || '10') // 恢复码数量
    },
    
    // 设备管理配置
    deviceManagement: {
      enabled: process.env.DEVICE_MANAGEMENT_ENABLED !== 'false', // 是否启用设备管理
      verifyNewDevices: process.env.VERIFY_NEW_DEVICES !== 'false', // 是否验证新设备
      maxDevicesPerUser: parseInt(process.env.MAX_DEVICES_PER_USER || '10'), // 每用户最大设备数
      trustByDefault: process.env.TRUST_DEVICES_BY_DEFAULT === 'true', // 默认信任设备
      untrustedDeviceSessionDuration: parseInt(process.env.UNTRUSTED_DEVICE_SESSION_DURATION || '86400'), // 非信任设备会话时长（秒）
      trustedDeviceSessionDuration: parseInt(process.env.TRUSTED_DEVICE_SESSION_DURATION || '2592000'), // 信任设备会话时长（30天）
      deviceRememberDuration: parseInt(process.env.DEVICE_REMEMBER_DURATION || '180'), // 记住设备时长（天）
      deviceInactiveTimeout: parseInt(process.env.DEVICE_INACTIVE_TIMEOUT || '60'), // 设备不活跃超时（天）
      fingerprinting: {
        useClientHints: process.env.USE_CLIENT_HINTS !== 'false', // 使用客户端信息
        useIpLocation: process.env.USE_IP_LOCATION !== 'false', // 使用IP位置
        useTrustworthiness: process.env.USE_TRUSTWORTHINESS !== 'false' // 使用可信度算法
      },
      notifications: {
        notifyOnNewDevice: process.env.NOTIFY_ON_NEW_DEVICE !== 'false', // 新设备登录通知
        notifyOnRemoteLogout: process.env.NOTIFY_ON_REMOTE_LOGOUT !== 'false', // 远程登出通知
        notifyOnDeviceRemoved: process.env.NOTIFY_ON_DEVICE_REMOVED !== 'false' // 设备移除通知
      }
    },
    
    // CSRF保护
    csrf: {
      enabled: process.env.CSRF_PROTECTION_ENABLED !== 'false',
      cookieName: process.env.CSRF_COOKIE_NAME || 'XSRF-TOKEN',
      headerName: process.env.CSRF_HEADER_NAME || 'X-XSRF-TOKEN'
    },
    
    // 刷新令牌配置
    refreshToken: {
      useCookie: process.env.REFRESH_TOKEN_USE_COOKIE !== 'false',
      cookieName: process.env.REFRESH_TOKEN_COOKIE_NAME || 'refresh_token'
    },
    
    // 安全日志配置
    securityLogs: {
      enabled: process.env.SECURITY_LOGS_ENABLED !== 'false',
      retentionDays: parseInt(process.env.SECURITY_LOGS_RETENTION_DAYS || '30'),
      notifyOnSuspiciousActivity: process.env.NOTIFY_ON_SUSPICIOUS_ACTIVITY !== 'false'
    }
  },
  
  // 日志配置
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    file: process.env.LOG_FILE || './logs/auth-service.log'
  },
  
  // 指标收集配置
  metrics: {
    enabled: process.env.METRICS_ENABLED !== 'false',
    interval: parseInt(process.env.METRICS_INTERVAL || '15'),
    prefix: process.env.METRICS_PREFIX || 'auth_',
    defaultLabels: {
      service: 'auth-service',
      environment: process.env.NODE_ENV || 'development',
      region: process.env.POD_REGION || 'unknown'
    },
    histograms: {
      requestDuration: {
        enabled: true,
        buckets: [10, 50, 100, 250, 500, 1000, 2500, 5000, 10000]
      },
      tokenGenerationTime: {
        enabled: true,
        buckets: [5, 10, 25, 50, 100, 250, 500]
      }
    },
    counters: {
      authFailures: {
        enabled: true,
        labels: ['method', 'reason', 'provider']
      },
      authSuccess: {
        enabled: true,
        labels: ['method', 'provider']
      },
      rateLimit: {
        enabled: true
      }
    }
  },
  
  // 跨区域同步配置
  crossRegionSync: {
    enabled: process.env.CROSS_REGION_SYNC_ENABLED === 'true',
    primaryRegion: process.env.PRIMARY_REGION || 'cn-east-1',
    backupRegions: process.env.BACKUP_REGIONS ? process.env.BACKUP_REGIONS.split(',') : ['cn-north-1', 'cn-southwest-1'],
    syncInterval: parseInt(process.env.CROSS_REGION_SYNC_INTERVAL || '60'),
    strategy: process.env.CROSS_REGION_SYNC_STRATEGY || 'sync',
    consistencyLevel: process.env.CROSS_REGION_CONSISTENCY_LEVEL || 'strong',
    maxReplicationLag: parseInt(process.env.CROSS_REGION_MAX_REPLICATION_LAG || '500'),
    conflictResolution: process.env.CROSS_REGION_CONFLICT_RESOLUTION || 'timestamp-based',
    healthCheck: {
      enabled: process.env.CROSS_REGION_HEALTH_CHECK_ENABLED !== 'false',
      interval: parseInt(process.env.CROSS_REGION_HEALTH_CHECK_INTERVAL || '30'),
      timeout: parseInt(process.env.CROSS_REGION_HEALTH_CHECK_TIMEOUT || '5'),
      failureThreshold: parseInt(process.env.CROSS_REGION_HEALTH_CHECK_FAILURE_THRESHOLD || '3')
    },
    failover: {
      enabled: process.env.CROSS_REGION_FAILOVER_ENABLED !== 'false',
      autoFailover: process.env.CROSS_REGION_AUTO_FAILOVER !== 'false',
      failbackDelay: parseInt(process.env.CROSS_REGION_FAILBACK_DELAY || '300'),
      dataValidation: process.env.CROSS_REGION_DATA_VALIDATION !== 'false'
    }
  }
}; 