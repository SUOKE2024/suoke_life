/**
 * 索克生活应用程序常量配置文件
 */

// API相关配置
export const API_URL = 'http://localhost:3000/v1';

// 智能体服务的实际端口配置
export const AGENT_SERVICE_PORTS = {
  xiaoai: 50051,  // 小艾服务 - 四诊协调
  xiaoke: 9083,   // 小克服务 - 资源调度
  laoke: 8080,    // 老克服务 - 知识传播
  soer: 8054      // 索儿服务 - 生活管理
};

// 本地存储键
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'suoke.authToken',
  REFRESH_TOKEN: 'suoke.refreshToken',
  USER_INFO: 'suoke.userInfo',
  SETTINGS: 'suoke.settings',
  HEALTH_DATA: 'suoke.healthData',
  AGENT_PREFERENCES: 'suoke.agentPreferences',
  LOCALE: 'suoke.locale',
  CHAT_SESSIONS: 'suoke.chatSessions'
};

// 主题颜色
export const THEME_COLORS = {
  // 品牌主色
  primary: '#4CAF50',
  primaryVariant: '#388E3C',
  
  // 辅助色
  secondary: '#FF9800',
  secondaryVariant: '#F57C00',
  
  // 状态颜色
  error: '#F44336',
  warning: '#FFC107',
  success: '#8BC34A',
  info: '#2196F3',
  
  // 中医特色色调
  wood: '#4CAF50', // 木-绿色
  fire: '#F44336',  // 火-红色
  earth: '#FFC107', // 土-黄色
  metal: '#BDBDBD', // 金-灰白色
  water: '#2196F3'  // 水-蓝色
};

// 路由名称
export const ROUTES = {
  HOME: 'Home',
  EXPLORE: 'Explore',
  LIFE: 'Life',
  SUOKE: 'Suoke',
  PROFILE: 'Profile',
  
  // 认证
  LOGIN: 'Login',
  REGISTER: 'Register',
  FORGOT_PASSWORD: 'ForgotPassword',
  
  // 智能体
  AGENT_CHAT: 'AgentChat',
  
  // 健康
  HEALTH_REPORT: 'HealthReport',
  HEALTH_PLAN: 'HealthPlan',
  
  // 诊断
  DIAGNOSTIC_DETAIL: 'DiagnosticDetail'
};

// 屏幕尺寸
export const SCREEN_DIMENSIONS = {
  XS: 320,
  SM: 360,
  MD: 411,
  LG: 768,
  XL: 1024
};

// 时间格式
export const DATE_FORMATS = {
  FULL_DATE: 'YYYY-MM-DD',
  FULL_DATETIME: 'YYYY-MM-DD HH:mm:ss',
  TIME: 'HH:mm',
  MONTH_DAY: 'MM-DD',
  YEAR_MONTH: 'YYYY-MM'
};

// 缓存过期时间（毫秒）
export const CACHE_EXPIRY = {
  HEALTH_DATA: 24 * 60 * 60 * 1000, // 1天
  AGENT_DATA: 7 * 24 * 60 * 60 * 1000, // 7天
  USER_PROFILE: 12 * 60 * 60 * 1000 // 12小时
};

// API服务的基础URL
export const API_BASE_URL = 'http://localhost:3000/v1';

// 超时设置（毫秒）
export const API_TIMEOUT = 10000;

// 图片资源基础URL
export const IMAGE_BASE_URL = 'https://assets.suoke.life';

// 各个服务的URL路径
export const SERVICE_PATHS = {
  AUTH: '/auth',
  USER: '/users',
  HEALTH_DATA: '/health-data',
  MEDICAL: '/medical',
  DIAGNOSTIC: '/diagnostic',
  RAG: '/rag',
  MESSAGE_BUS: '/messaging',
  AGENTS: {
    XIAOAI: '/agents/xiaoai',
    XIAOKE: '/agents/xiaoke',
    LAOKE: '/agents/laoke',
    SOER: '/agents/soer'
  }
};

// 四诊服务路径
export const DIAGNOSTIC_PATHS = {
  LOOK: '/diagnostic/look',
  LISTEN: '/diagnostic/listen',
  INQUIRY: '/diagnostic/inquiry',
  PALPATION: '/diagnostic/palpation'
};

// 应用环境配置
export const APP_ENV = {
  DEVELOPMENT: 'development',
  STAGING: 'staging',
  PRODUCTION: 'production'
};

// 默认分页大小
export const DEFAULT_PAGE_SIZE = 20;

// 重试策略配置
export const RETRY_CONFIG = {
  MAX_ATTEMPTS: 3,
  DELAY_MS: 1000,
  BACKOFF_FACTOR: 2
};

// 响应状态码
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
};

// 验证码有效期（秒）
export const VERIFICATION_CODE_EXPIRY = 60;
