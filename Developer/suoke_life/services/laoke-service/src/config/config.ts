import Joi from 'joi';
import dotenv from 'dotenv';
import path from 'path';
import fs from 'fs';
import logger from '../core/utils/logger';

// 加载.env文件
const envPath = path.resolve(process.cwd(), '.env');
if (fs.existsSync(envPath)) {
  dotenv.config();
  logger.info(`已从 ${envPath} 加载环境变量`);
}

// 定义环境变量验证架构
const envVarsSchema = Joi.object()
  .keys({
    // 基本配置
    NODE_ENV: Joi.string().valid('development', 'production', 'test').default('development'),
    PORT: Joi.number().default(3012),
    API_VERSION: Joi.string().default('v1'),
    API_PREFIX: Joi.string().default('/api/v1'),
    SERVICE_NAME: Joi.string().required().default('laoke-service'),
    
    // 数据库配置
    MONGODB_URI: Joi.string().required().description('MongoDB连接字符串'),
    MONGO_USER: Joi.string().description('MongoDB用户名'),
    MONGO_PASSWORD: Joi.string().description('MongoDB密码'),
    MONGO_AUTH_SOURCE: Joi.string().description('MongoDB验证数据库'),
    
    // 缓存配置
    REDIS_URI: Joi.string().required().description('Redis连接字符串'),
    REDIS_PASSWORD: Joi.string().allow('').description('Redis密码'),
    CACHE_TTL: Joi.number().default(3600).description('缓存有效期(秒)'),
    
    // JWT 配置
    JWT_SECRET: Joi.string().required().description('JWT密钥'),
    JWT_EXPIRATION: Joi.string().default('1d').description('JWT过期时间'),
    JWT_REFRESH_EXPIRATION: Joi.string().default('7d').description('JWT刷新令牌过期时间'),
    
    // 日志配置
    LOG_LEVEL: Joi.string().valid('error', 'warn', 'info', 'debug', 'trace').default('info'),
    LOG_FILE_PATH: Joi.string().default('logs/laoke-service.log'),
    
    // 跨域配置
    ALLOWED_ORIGINS: Joi.string().default('*'),
    
    // 监控指标
    METRICS_PORT: Joi.number().default(9465),
    METRICS_PATH: Joi.string().default('/metrics'),
    HEALTH_CHECK_PATH: Joi.string().default('/health'),
    
    // OpenTelemetry配置
    OTEL_ENABLED: Joi.boolean().default(false),
    OTEL_EXPORTER_OTLP_ENDPOINT: Joi.string().when('OTEL_ENABLED', {
      is: true,
      then: Joi.required(),
      otherwise: Joi.optional()
    }),
    OTEL_SERVICE_NAME: Joi.string().default('laoke-service'),
    
    // AI服务配置
    AI_MODEL_ENDPOINT: Joi.string().required().description('AI模型服务端点'),
    AI_MODEL_API_KEY: Joi.string().required().description('AI模型API密钥'),
    AI_MODEL_TIMEOUT: Joi.number().default(30000).description('AI模型请求超时时间(毫秒)'),
    AI_MODEL_MAX_TOKENS: Joi.number().default(1024).description('AI模型最大令牌数'),
    
    // S3存储配置
    S3_ENDPOINT: Joi.string().required().description('S3端点'),
    S3_ACCESS_KEY: Joi.string().required().description('S3访问密钥'),
    S3_SECRET_KEY: Joi.string().required().description('S3秘密密钥'),
    S3_REGION: Joi.string().default('us-east-1').description('S3区域'),
    S3_BUCKET: Joi.string().required().description('S3存储桶名称'),
    S3_USE_PATH_STYLE: Joi.boolean().default(true).description('是否使用路径样式URL'),
    
    // 媒体流配置
    MEDIA_STREAMS_ENABLED: Joi.boolean().default(true),
    MAX_CONCURRENT_STREAMS: Joi.number().default(100),
    STREAM_BUFFER_SIZE: Joi.number().default(8192),
    STREAM_CHUNK_DURATION_MS: Joi.number().default(200),
    AUDIO_SAMPLE_RATE: Joi.number().default(16000),
    AUDIO_CHANNELS: Joi.number().default(1),
    VIDEO_MAX_RESOLUTION: Joi.string().default('720p'),
    
    // 语音识别配置
    WHISPER_API_ENDPOINT: Joi.string().when('MEDIA_STREAMS_ENABLED', {
      is: true,
      then: Joi.required(),
      otherwise: Joi.optional()
    }),
    WHISPER_API_KEY: Joi.string().when('MEDIA_STREAMS_ENABLED', {
      is: true,
      then: Joi.required(),
      otherwise: Joi.optional()
    }),
    WHISPER_MODEL: Joi.string().default('whisper-1'),
    WHISPER_TIMEOUT: Joi.number().default(30000),
    WHISPER_CACHE_TTL: Joi.number().default(86400),
    
    // 方言支持配置
    DIALECT_SUPPORT_ENABLED: Joi.boolean().default(true),
    DEFAULT_DIALECT: Joi.string().default('mandarin'),
    DIALECT_DETECTION_THRESHOLD: Joi.number().default(0.7),
    DIALECT_SAMPLES_BUCKET: Joi.string().default('dialect-samples'),
    MIN_SAMPLES_PER_DIALECT: Joi.number().default(500),
    SAMPLE_QUALITY_THRESHOLD: Joi.number().default(0.7),
    
    // 集群配置
    CLUSTER_ENABLED: Joi.boolean().default(false),
    INSTANCE_ID: Joi.number().default(1),
    REDIS_CLUSTER_URL: Joi.string().when('CLUSTER_ENABLED', {
      is: true,
      then: Joi.required(),
      otherwise: Joi.optional()
    }),
    TASK_DISTRIBUTION_STRATEGY: Joi.string().valid('round-robin', 'consistent-hash', 'least-loaded').default('round-robin'),
    
    // 功能开关
    DEBUG_MODE: Joi.boolean().default(false),
    MAINTENANCE_MODE: Joi.boolean().default(false),
    AR_VR_FEATURES_ENABLED: Joi.boolean().default(true),
    VOICE_CHANGER_ENABLED: Joi.boolean().default(true),
  })
  .unknown();

// 验证环境变量
const { value: envVars, error } = envVarsSchema.prefs({ errors: { label: 'key' } }).validate(process.env);

if (error) {
  throw new Error(`配置验证错误: ${error.message}`);
}

// 导出配置对象
export default {
  env: envVars.NODE_ENV,
  isProduction: envVars.NODE_ENV === 'production',
  isDevelopment: envVars.NODE_ENV === 'development',
  isTest: envVars.NODE_ENV === 'test',
  
  server: {
    port: envVars.PORT,
    apiVersion: envVars.API_VERSION,
    apiPrefix: envVars.API_PREFIX,
    serviceName: envVars.SERVICE_NAME,
  },
  
  db: {
    uri: envVars.MONGODB_URI,
    user: envVars.MONGO_USER,
    password: envVars.MONGO_PASSWORD,
    authSource: envVars.MONGO_AUTH_SOURCE,
  },
  
  redis: {
    uri: envVars.REDIS_URI,
    password: envVars.REDIS_PASSWORD,
    cacheTtl: envVars.CACHE_TTL,
  },
  
  jwt: {
    secret: envVars.JWT_SECRET,
    expiration: envVars.JWT_EXPIRATION,
    refreshExpiration: envVars.JWT_REFRESH_EXPIRATION,
  },
  
  logging: {
    level: envVars.LOG_LEVEL,
    filePath: envVars.LOG_FILE_PATH,
  },
  
  cors: {
    allowedOrigins: envVars.ALLOWED_ORIGINS.split(','),
  },
  
  metrics: {
    port: envVars.METRICS_PORT,
    path: envVars.METRICS_PATH,
    healthCheckPath: envVars.HEALTH_CHECK_PATH,
  },
  
  telemetry: {
    enabled: envVars.OTEL_ENABLED,
    endpoint: envVars.OTEL_EXPORTER_OTLP_ENDPOINT,
    serviceName: envVars.OTEL_SERVICE_NAME,
  },
  
  ai: {
    modelEndpoint: envVars.AI_MODEL_ENDPOINT,
    apiKey: envVars.AI_MODEL_API_KEY,
    timeout: envVars.AI_MODEL_TIMEOUT,
    maxTokens: envVars.AI_MODEL_MAX_TOKENS,
  },
  
  storage: {
    endpoint: envVars.S3_ENDPOINT,
    accessKey: envVars.S3_ACCESS_KEY,
    secretKey: envVars.S3_SECRET_KEY,
    region: envVars.S3_REGION,
    bucket: envVars.S3_BUCKET,
    usePathStyle: envVars.S3_USE_PATH_STYLE,
  },
  
  media: {
    streamsEnabled: envVars.MEDIA_STREAMS_ENABLED,
    maxConcurrentStreams: envVars.MAX_CONCURRENT_STREAMS,
    streamBufferSize: envVars.STREAM_BUFFER_SIZE,
    streamChunkDurationMs: envVars.STREAM_CHUNK_DURATION_MS,
    audioSampleRate: envVars.AUDIO_SAMPLE_RATE,
    audioChannels: envVars.AUDIO_CHANNELS,
    videoMaxResolution: envVars.VIDEO_MAX_RESOLUTION,
  },
  
  whisper: {
    apiEndpoint: envVars.WHISPER_API_ENDPOINT,
    apiKey: envVars.WHISPER_API_KEY,
    model: envVars.WHISPER_MODEL,
    timeout: envVars.WHISPER_TIMEOUT,
    cacheTtl: envVars.WHISPER_CACHE_TTL,
  },
  
  dialect: {
    enabled: envVars.DIALECT_SUPPORT_ENABLED,
    default: envVars.DEFAULT_DIALECT,
    detectionThreshold: envVars.DIALECT_DETECTION_THRESHOLD,
    samplesBucket: envVars.DIALECT_SAMPLES_BUCKET,
    minSamplesPerDialect: envVars.MIN_SAMPLES_PER_DIALECT,
    sampleQualityThreshold: envVars.SAMPLE_QUALITY_THRESHOLD,
  },
  
  cluster: {
    enabled: envVars.CLUSTER_ENABLED,
    instanceId: envVars.INSTANCE_ID,
    redisClusterUrl: envVars.REDIS_CLUSTER_URL,
    taskDistributionStrategy: envVars.TASK_DISTRIBUTION_STRATEGY,
  },
  
  features: {
    debugMode: envVars.DEBUG_MODE,
    maintenanceMode: envVars.MAINTENANCE_MODE,
    arVrEnabled: envVars.AR_VR_FEATURES_ENABLED,
    voiceChangerEnabled: envVars.VOICE_CHANGER_ENABLED,
  },
}; 