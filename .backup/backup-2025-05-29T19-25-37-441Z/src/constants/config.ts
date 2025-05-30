// 环境配置
export const Environment = {
  DEV: 'development',
  STAGING: 'staging',
  PROD: 'production',
} as const;

// 当前环境
export const currentEnv = __DEV__ ? Environment.DEV : Environment.PROD;

// API配置
export const API_CONFIG = {
  // 基础配置
  BASE_URL: __DEV__ ? 'http://localhost:8000' : 'https://api.suoke.life',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,

  // 智能体服务端点
  AGENTS: {
    XIAOAI: __DEV__ ? 'http://localhost:8015' : 'https://xiaoai.suoke.life',
    XIAOKE: __DEV__ ? 'http://localhost:8016' : 'https://xiaoke.suoke.life',
    LAOKE: __DEV__ ? 'http://localhost:8017' : 'https://laoke.suoke.life',
    SOER: __DEV__ ? 'http://localhost:8018' : 'https://soer.suoke.life',
  },

  // 五诊断服务端点
  DIAGNOSIS: {
    LOOK: __DEV__ ? 'http://localhost:8019' : 'https://look.suoke.life',
    LISTEN: __DEV__ ? 'http://localhost:8020' : 'https://listen.suoke.life',
    INQUIRY: __DEV__
      ? 'http://localhost:8021'
      : 'https://inquiry.suoke.life',
    PALPATION: __DEV__
      ? 'http://localhost:8022'
      : 'https://palpation.suoke.life',
    CALCULATION: __DEV__
      ? 'http://localhost:8023'
      : 'https://calculation.suoke.life',
  },

  // 其他服务端点
  SERVICES: {
    AUTH: __DEV__ ? 'http://localhost:8001' : 'https://auth.suoke.life',
    USER: __DEV__ ? 'http://localhost:8006' : 'https://user.suoke.life',
    HEALTH: __DEV__ ? 'http://localhost:8002' : 'https://health.suoke.life',
    BLOCKCHAIN: __DEV__
      ? 'http://localhost:8003'
      : 'https://blockchain.suoke.life',
    RAG: __DEV__ ? 'http://localhost:8005' : 'https://rag.suoke.life',
    GATEWAY: __DEV__
      ? 'http://localhost:8000'
      : 'https://gateway.suoke.life',
  },
};

// 缓存配置
export const CACHE_CONFIG = {
  // 缓存TTL (秒)
  TTL: {
    SHORT: 5 * 60, // 5分钟
    MEDIUM: 30 * 60, // 30分钟
    LONG: 24 * 60 * 60, // 24小时
    WEEK: 7 * 24 * 60 * 60, // 7天
  },

  // 缓存键前缀
  KEYS: {
    USER_PROFILE: 'user_profile_',
    HEALTH_DATA: 'health_data_',
    AGENT_CONVERSATION: 'agent_conversation_',
    DIAGNOSIS_SESSION: 'diagnosis_session_',
    CONSTITUTION_DATA: 'constitution_data_',
  },

  // 最大缓存条目数
  MAX_ENTRIES: 1000,

  // 清理间隔 (毫秒)
  CLEANUP_INTERVAL: 10 * 60 * 1000, // 10分钟
};

// 存储配置
export const STORAGE_CONFIG = {
  // AsyncStorage键
  KEYS: {
    AUTH_TOKEN: 'auth_token',
    REFRESH_TOKEN: 'refresh_token',
    USER_ID: 'user_id',
    LANGUAGE: 'language',
    THEME: 'theme',
    FIRST_LAUNCH: 'first_launch',
    DEVICE_ID: 'device_id',
    PUSH_TOKEN: 'push_token',
    PRIVACY_SETTINGS: 'privacy_settings',
    BIOMETRIC_ENABLED: 'biometric_enabled',
  },

  // SQLite数据库配置
  DATABASE: {
    NAME: 'suoke_life.db',
    VERSION: 1,
    SIZE: 50 * 1024 * 1024, // 50MB
  },
};

// 应用常量
export const APP_CONFIG = {
  // 应用信息
  NAME: '索克生活',
  VERSION: '1.0.0',
  BUILD_NUMBER: '1',

  // 支持的语言
  SUPPORTED_LANGUAGES: ['zh', 'en'],
  DEFAULT_LANGUAGE: 'zh',

  // 分页配置
  PAGINATION: {
    DEFAULT_SIZE: 20,
    MAX_SIZE: 100,
  },

  // 文件上传配置
  UPLOAD: {
    MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
    ALLOWED_IMAGE_TYPES: ['jpg', 'jpeg', 'png', 'webp'],
    ALLOWED_AUDIO_TYPES: ['mp3', 'wav', 'aac', 'm4a'],
    ALLOWED_VIDEO_TYPES: ['mp4', 'mov', 'avi'],
  },

  // 健康数据采集间隔
  HEALTH_DATA: {
    COLLECTION_INTERVAL: 60 * 1000, // 1分钟
    BATCH_SIZE: 50,
    SYNC_INTERVAL: 5 * 60 * 1000, // 5分钟
  },

  // 智能体配置
  AGENTS: {
    MAX_MESSAGE_LENGTH: 2000,
    CONVERSATION_HISTORY_LIMIT: 100,
    RESPONSE_TIMEOUT: 30000,
  },

  // 四诊配置
  DIAGNOSIS: {
    SESSION_TIMEOUT: 30 * 60 * 1000, // 30分钟
    MAX_IMAGE_SIZE: 5 * 1024 * 1024, // 5MB
    MAX_AUDIO_DURATION: 5 * 60, // 5分钟
    RETRY_ATTEMPTS: 3,
  },
};

// 智能体信息
export const AGENT_INFO = {
  xiaoai: {
    name: '小艾',
    description: '中医诊断智能体',
    avatar: 'xiaoai_avatar',
    color: '#E8F5E8',
    features: ['五诊合参', '体质辨识', '方剂推荐', '穴位指导'],
    specialty: 'TCM Diagnosis',
  },
  xiaoke: {
    name: '小克',
    description: '服务管理智能体',
    avatar: 'xiaoke_avatar',
    color: '#E3F2FD',
    features: ['库存管理', 'ERP系统', '订单处理', '客户服务'],
    specialty: 'Service Management',
  },
  laoke: {
    name: '老克',
    description: '教育智能体',
    avatar: 'laoke_avatar',
    color: '#FFF3E0',
    features: ['健康教育', '社区互动', '知识分享', '课程推荐'],
    specialty: 'Health Education',
  },
  soer: {
    name: '索儿',
    description: '生活智能体',
    avatar: 'soer_avatar',
    color: '#F3E5F5',
    features: ['营养分析', '食谱推荐', '运动建议', '生活规划'],
    specialty: 'Lifestyle & Nutrition',
  },
};

// 体质信息
export const CONSTITUTION_INFO = {
  balanced: {
    name: '平和质',
    description: '阴阳气血调和，体质平和',
    characteristics: ['精力充沛', '睡眠良好', '性格开朗', '适应力强'],
    recommendations: ['保持现状', '均衡饮食', '适量运动', '心情愉悦'],
  },
  qi_deficiency: {
    name: '气虚质',
    description: '元气不足，易疲劳',
    characteristics: ['容易疲劳', '说话声音低', '常出虚汗', '呼吸短促'],
    recommendations: ['补气食物', '适度运动', '充足睡眠', '情志调理'],
  },
  yang_deficiency: {
    name: '阳虚质',
    description: '阳气不足，畏寒怕冷',
    characteristics: ['畏寒怕冷', '手脚冰凉', '精神不振', '夜尿频多'],
    recommendations: ['温阳食物', '艾灸调理', '避免寒凉', '适度运动'],
  },
  yin_deficiency: {
    name: '阴虚质',
    description: '阴液亏少，虚热内生',
    characteristics: ['五心烦热', '咽干口燥', '失眠多梦', '大便干燥'],
    recommendations: ['滋阴食物', '早睡早起', '情志平和', '避免熬夜'],
  },
  phlegm_dampness: {
    name: '痰湿质',
    description: '水液内停，痰湿凝聚',
    characteristics: ['形体肥胖', '腹部肥满', '胸闷痰多', '身重困倦'],
    recommendations: ['祛湿食物', '规律运动', '控制体重', '清淡饮食'],
  },
  damp_heat: {
    name: '湿热质',
    description: '湿热内蕴，油腻垢腻',
    characteristics: ['面部油腻', '口苦口干', '身重困倦', '大便黏滞'],
    recommendations: ['清热祛湿', '避免辛辣', '清淡饮食', '适量运动'],
  },
  blood_stasis: {
    name: '血瘀质',
    description: '血行不畅，瘀血内阻',
    characteristics: ['面色晦暗', '色素沉着', '肌肤粗糙', '易有瘀斑'],
    recommendations: ['活血化瘀', '适度运动', '情志调理', '避免久坐'],
  },
  qi_stagnation: {
    name: '气郁质',
    description: '气机郁滞，情志不畅',
    characteristics: ['情绪不稳', '多愁善感', '胸胁胀满', '叹息频作'],
    recommendations: ['疏肝理气', '情志调理', '户外活动', '社交互动'],
  },
  special_diathesis: {
    name: '特禀质',
    description: '先天禀赋异常，过敏体质',
    characteristics: ['过敏体质', '遗传缺陷', '胎传异常', '药物过敏'],
    recommendations: ['避免过敏原', '增强体质', '谨慎用药', '定期检查'],
  },
};

// 错误代码
export const ERROR_CODES = {
  // 网络错误
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT: 'TIMEOUT',
  CONNECTION_FAILED: 'CONNECTION_FAILED',

  // 认证错误
  UNAUTHORIZED: 'UNAUTHORIZED',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  INVALID_CREDENTIALS: 'INVALID_CREDENTIALS',

  // 业务错误
  USER_NOT_FOUND: 'USER_NOT_FOUND',
  INVALID_INPUT: 'INVALID_INPUT',
  OPERATION_FAILED: 'OPERATION_FAILED',
  RESOURCE_NOT_FOUND: 'RESOURCE_NOT_FOUND',

  // 智能体错误
  AGENT_UNAVAILABLE: 'AGENT_UNAVAILABLE',
  AGENT_TIMEOUT: 'AGENT_TIMEOUT',
  INVALID_AGENT_RESPONSE: 'INVALID_AGENT_RESPONSE',

  // 四诊错误
  DIAGNOSIS_FAILED: 'DIAGNOSIS_FAILED',
  INVALID_DIAGNOSIS_DATA: 'INVALID_DIAGNOSIS_DATA',
  DIAGNOSIS_TIMEOUT: 'DIAGNOSIS_TIMEOUT',
};

// 事件名称
export const EVENTS = {
  // 认证事件
  AUTH_SUCCESS: 'auth_success',
  AUTH_FAILED: 'auth_failed',
  LOGOUT: 'logout',
  TOKEN_REFRESHED: 'token_refreshed',

  // 用户事件
  PROFILE_UPDATED: 'profile_updated',
  HEALTH_DATA_UPDATED: 'health_data_updated',

  // 智能体事件
  AGENT_MESSAGE_RECEIVED: 'agent_message_received',
  AGENT_ERROR: 'agent_error',

  // 四诊事件
  DIAGNOSIS_STARTED: 'diagnosis_started',
  DIAGNOSIS_COMPLETED: 'diagnosis_completed',
  DIAGNOSIS_FAILED: 'diagnosis_failed',

  // 系统事件
  APP_STATE_CHANGED: 'app_state_changed',
  NETWORK_STATE_CHANGED: 'network_state_changed',
  THEME_CHANGED: 'theme_changed',
  LANGUAGE_CHANGED: 'language_changed',
};

export default {
  Environment,
  currentEnv,
  API_CONFIG,
  CACHE_CONFIG,
  STORAGE_CONFIG,
  APP_CONFIG,
  AGENT_INFO,
  CONSTITUTION_INFO,
  ERROR_CODES,
  EVENTS,
};
