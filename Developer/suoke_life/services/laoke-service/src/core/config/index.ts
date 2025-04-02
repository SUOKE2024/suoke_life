import dotenv from 'dotenv';
import path from 'path';

// 加载环境变量
dotenv.config();

// 默认配置
const DEFAULT = {
  port: 3012,
  metricsPort: 9465,
  apiPrefix: '/api/v1',
  env: 'development',
  version: '1.0.0',
  
  // 数据库配置
  mongo: {
    uri: 'mongodb://localhost:27017/laoke-service',
    user: '',
    password: '',
    options: 'retryWrites=true&w=majority'
  },
  
  // Redis配置
  redis: {
    host: 'localhost',
    port: 6379,
    password: '',
    prefix: 'laoke:'
  },
  
  // 安全配置
  jwt: {
    secret: 'default-secret-key-should-be-changed-in-production',
    expiresIn: '7d'
  },
  cors: {
    origins: ['http://localhost:3000', 'http://localhost:8080']
  },
  
  // 日志配置
  logs: {
    level: 'info',
    filePath: './logs'
  },
  
  // 文件上传配置
  uploads: {
    directory: './uploads',
    maxFileSize: 10485760, // 10MB
    tempDirectory: './uploads/temp',
    audioDirectory: './uploads/audio'
  },
  
  // AI服务配置
  aiModel: {
    endpoint: 'http://localhost:11434',
    apiKey: '',
    name: 'llama3'
  },
  
  // 语音引导模块配置
  aiServices: {
    apiKey: 'default-api-key',
    commandMatching: 'http://localhost:3013/command-matching',
    commandExecution: 'http://localhost:3013/command-execution',
    contextEvaluation: 'http://localhost:3013/context-evaluation',
    conversationalAI: 'http://localhost:3013/conversational-ai',
    textToSpeech: 'http://localhost:3013/text-to-speech',
    speechRecognition: 'http://localhost:3013/speech-recognition'
  },
  
  // 命令匹配阈值
  commandMatchThreshold: 0.6,
  
  // 方言模块配置
  dialect: {
    apiEndpoint: 'http://localhost:3014/dialect',
    recognitionThreshold: 0.7
  }
};

// 环境配置
const config = {
  port: parseInt(process.env.PORT || '') || DEFAULT.port,
  metricsPort: parseInt(process.env.METRICS_PORT || '') || DEFAULT.metricsPort,
  apiPrefix: process.env.API_PREFIX || DEFAULT.apiPrefix,
  env: process.env.NODE_ENV || DEFAULT.env,
  version: process.env.SERVICE_VERSION || DEFAULT.version,
  
  mongo: {
    uri: process.env.MONGO_URI || DEFAULT.mongo.uri,
    user: process.env.MONGO_USER || DEFAULT.mongo.user,
    password: process.env.MONGO_PASSWORD || DEFAULT.mongo.password,
    options: process.env.MONGO_OPTIONS || DEFAULT.mongo.options
  },
  
  redis: {
    host: process.env.REDIS_HOST || DEFAULT.redis.host,
    port: parseInt(process.env.REDIS_PORT || '') || DEFAULT.redis.port,
    password: process.env.REDIS_PASSWORD || DEFAULT.redis.password,
    prefix: process.env.REDIS_PREFIX || DEFAULT.redis.prefix
  },
  
  jwt: {
    secret: process.env.JWT_SECRET || DEFAULT.jwt.secret,
    expiresIn: process.env.JWT_EXPIRES_IN || DEFAULT.jwt.expiresIn
  },
  
  cors: {
    origins: process.env.CORS_ORIGINS ? 
      process.env.CORS_ORIGINS.split(',') : 
      DEFAULT.cors.origins
  },
  
  logs: {
    level: process.env.LOG_LEVEL || DEFAULT.logs.level,
    filePath: process.env.LOG_FILE_PATH || DEFAULT.logs.filePath
  },
  
  uploads: {
    directory: process.env.UPLOAD_DIR || DEFAULT.uploads.directory,
    maxFileSize: parseInt(process.env.MAX_FILE_SIZE || '') || DEFAULT.uploads.maxFileSize,
    tempDirectory: process.env.TEMP_FILES_PATH || DEFAULT.uploads.tempDirectory,
    audioDirectory: process.env.AUDIO_FILES_PATH || DEFAULT.uploads.audioDirectory
  },
  
  vault: {
    addr: process.env.VAULT_ADDR,
    token: process.env.VAULT_TOKEN,
    path: process.env.VAULT_PATH
  },
  
  aiModel: {
    endpoint: process.env.AI_MODEL_ENDPOINT || DEFAULT.aiModel.endpoint,
    apiKey: process.env.AI_MODEL_API_KEY || DEFAULT.aiModel.apiKey,
    name: process.env.AI_MODEL_NAME || DEFAULT.aiModel.name
  },
  
  aiServices: {
    apiKey: process.env.AI_SERVICES_API_KEY || DEFAULT.aiServices.apiKey,
    commandMatching: process.env.AI_SERVICES_COMMAND_MATCHING || DEFAULT.aiServices.commandMatching,
    commandExecution: process.env.AI_SERVICES_COMMAND_EXECUTION || DEFAULT.aiServices.commandExecution,
    contextEvaluation: process.env.AI_SERVICES_CONTEXT_EVALUATION || DEFAULT.aiServices.contextEvaluation,
    conversationalAI: process.env.AI_SERVICES_CONVERSATIONAL_AI || DEFAULT.aiServices.conversationalAI,
    textToSpeech: process.env.AI_SERVICES_TEXT_TO_SPEECH || DEFAULT.aiServices.textToSpeech,
    speechRecognition: process.env.AI_SERVICES_SPEECH_RECOGNITION || DEFAULT.aiServices.speechRecognition
  },
  
  commandMatchThreshold: parseFloat(process.env.COMMAND_MATCH_THRESHOLD || '') || DEFAULT.commandMatchThreshold,
  
  dialect: {
    apiEndpoint: process.env.DIALECT_API_ENDPOINT || DEFAULT.dialect.apiEndpoint,
    recognitionThreshold: parseFloat(process.env.DIALECT_RECOGNITION_THRESHOLD || '') || DEFAULT.dialect.recognitionThreshold
  }
};

// 确保目录存在
export const ensureDirectoriesExist = () => {
  const fs = require('fs');
  const dirs = [
    config.uploads.directory,
    config.uploads.tempDirectory,
    config.uploads.audioDirectory,
    config.logs.filePath
  ];
  
  dirs.forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
};

export default config; 