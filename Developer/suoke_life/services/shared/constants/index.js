/**
 * 索克生活常量定义
 * 集中管理应用中使用的所有常量
 */

// HTTP状态码
const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503
};

// 用户角色
const USER_ROLES = {
  ADMIN: 'admin',
  USER: 'user',
  GUEST: 'guest'
};

// 体质类型
const CONSTITUTION_TYPES = {
  BALANCED: 'balanced',
  QI_DEFICIENCY: 'qiDeficiency',
  YANG_DEFICIENCY: 'yangDeficiency',
  YIN_DEFICIENCY: 'yinDeficiency',
  PHLEGM_DAMPNESS: 'phlegmDampness',
  DAMP_HEAT: 'dampHeat',
  BLOOD_STASIS: 'bloodStasis',
  QI_DEPRESSION: 'qiDepression',
  SPECIAL: 'special'
};

// 错误代码
const ERROR_CODES = {
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  AUTHENTICATION_ERROR: 'AUTHENTICATION_ERROR',
  AUTHORIZATION_ERROR: 'AUTHORIZATION_ERROR',
  RESOURCE_NOT_FOUND: 'RESOURCE_NOT_FOUND',
  DUPLICATE_RESOURCE: 'DUPLICATE_RESOURCE',
  INTERNAL_SERVER_ERROR: 'INTERNAL_SERVER_ERROR',
  DATABASE_ERROR: 'DATABASE_ERROR',
  EXTERNAL_SERVICE_ERROR: 'EXTERNAL_SERVICE_ERROR'
};

// 缓存键前缀
const CACHE_PREFIXES = {
  USER: 'user:',
  PROFILE: 'profile:',
  SESSION: 'session:',
  KNOWLEDGE_NODE: 'knowledge:node:',
  HEALTH_RECORD: 'health:record:'
};

// 文件类型
const FILE_TYPES = {
  IMAGE: 'image',
  DOCUMENT: 'document',
  AUDIO: 'audio',
  VIDEO: 'video'
};

module.exports = {
  HTTP_STATUS,
  USER_ROLES,
  CONSTITUTION_TYPES,
  ERROR_CODES,
  CACHE_PREFIXES,
  FILE_TYPES
}; 