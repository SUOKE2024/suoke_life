/**
 * 安全配置
 */
const config = require('./default');

/**
 * 安全相关事件类型常量
 */
const SECURITY_EVENT_TYPES = {
  // 认证相关
  LOGIN_SUCCESS: 'login_success',
  LOGIN_FAILED: 'login_failed',
  LOGIN_ATTEMPT_BLOCKED: 'login_attempt_blocked',
  PASSWORD_CHANGED: 'password_changed',
  PASSWORD_RESET_REQUESTED: 'password_reset_requested',
  PASSWORD_RESET_COMPLETED: 'password_reset_completed',
  
  // 会话相关
  SESSION_CREATED: 'session_created',
  SESSION_DESTROYED: 'session_destroyed',
  SESSION_EXPIRED: 'session_expired',
  SESSION_INVALIDATED: 'session_invalidated',
  
  // 账户相关
  ACCOUNT_CREATED: 'account_created',
  ACCOUNT_UPDATED: 'account_updated',
  ACCOUNT_LOCKED: 'account_locked',
  ACCOUNT_UNLOCKED: 'account_unlocked',
  ACCOUNT_DELETED: 'account_deleted',
  
  // 二因素认证相关
  TWO_FACTOR_ENABLED: 'two_factor_enabled',
  TWO_FACTOR_DISABLED: 'two_factor_disabled',
  TWO_FACTOR_VERIFIED: 'two_factor_verified',
  TWO_FACTOR_FAILED: 'two_factor_failed',
  RECOVERY_CODE_GENERATED: 'recovery_code_generated',
  RECOVERY_CODE_USED: 'recovery_code_used',
  RECOVERY_CODE_FAILED: 'recovery_code_failed',
  
  // 设备相关
  DEVICE_REGISTERED: 'device_registered',
  DEVICE_TRUSTED: 'device_trusted',
  DEVICE_UNTRUSTED: 'device_untrusted',
  DEVICE_REMOVED: 'device_removed',
  DEVICE_FINGERPRINT_COLLISION: 'device_fingerprint_collision',
  DEVICE_FINGERPRINT_PROCESSED: 'device_fingerprint_processed',
  
  // 验证相关
  DEVICE_VERIFICATION: 'device_verification',
  DEVICE_VERIFICATION_SUCCESS: 'device_verification_success',
  DEVICE_VERIFICATION_FAILED: 'device_verification_failed',
  DEVICE_VERIFICATION_RESENT: 'device_verification_resent',
  DEVICE_VERIFICATION_METHOD_CHANGED: 'device_verification_method_changed',
  
  // 权限相关
  PERMISSION_GRANTED: 'permission_granted',
  PERMISSION_REVOKED: 'permission_revoked',
  UNAUTHORIZED_ACCESS_ATTEMPT: 'unauthorized_access_attempt',
  
  // API相关
  API_ACCESS: 'api_access',
  API_RATE_LIMIT_EXCEEDED: 'api_rate_limit_exceeded',
  API_KEY_CREATED: 'api_key_created',
  API_KEY_REVOKED: 'api_key_revoked',
  
  // 可疑活动
  SUSPICIOUS_ACTIVITY: 'suspicious_activity',
  BRUTE_FORCE_ATTEMPT: 'brute_force_attempt',
  UNUSUAL_LOCATION_ACCESS: 'unusual_location_access',
  UNUSUAL_BEHAVIOR: 'unusual_behavior',
  MULTIPLE_FAILED_ATTEMPTS: 'multiple_failed_attempts'
};

/**
 * 异常行为检测配置
 */
const ANOMALY_DETECTION = {
  // 失败尝试触发锁定的阈值
  failedAttemptsThreshold: config.security?.anomalyDetection?.failedAttemptsThreshold || 5,
  
  // 记录失败尝试的过期时间（秒）
  failedAttemptsTTL: config.security?.anomalyDetection?.failedAttemptsTTL || 3600, // 1小时
  
  // IP信誉分数阈值
  ipReputationThreshold: config.security?.anomalyDetection?.ipReputationThreshold || 50,
  
  // 历史登录记录保留时间（天）
  loginHistoryDays: config.security?.anomalyDetection?.loginHistoryDays || 30,
  
  // 缓存的用户位置数量
  maxCachedLocations: config.security?.anomalyDetection?.maxCachedLocations || 5,
  
  // 用于检测的位置变化阈值（公里）
  locationChangeThreshold: config.security?.anomalyDetection?.locationChangeThreshold || 500,
  
  // 风险评分阈值
  riskScoreThresholds: {
    low: config.security?.anomalyDetection?.riskScoreThresholds?.low || 30,
    medium: config.security?.anomalyDetection?.riskScoreThresholds?.medium || 60,
    high: config.security?.anomalyDetection?.riskScoreThresholds?.high || 80
  },
  
  // 需要进行设备验证的风险等级
  verificationRequiredLevel: config.security?.anomalyDetection?.verificationRequiredLevel || 'medium',
  
  // 是否对可疑活动进行自动锁定
  autoLockSuspiciousActivity: config.security?.anomalyDetection?.autoLockSuspiciousActivity || false,
  
  // 锁定持续时间（秒）
  lockDuration: config.security?.anomalyDetection?.lockDuration || 1800, // 30分钟
  
  // 可疑活动通知配置
  notification: {
    enabled: config.security?.anomalyDetection?.notification?.enabled || true,
    methods: config.security?.anomalyDetection?.notification?.methods || ['email']
  }
};

/**
 * 设备验证配置
 */
const DEVICE_VERIFICATION = {
  // 默认验证方法
  defaultMethod: config.security?.deviceVerification?.defaultMethod || 'email',
  
  // 可用的验证方法
  availableMethods: config.security?.deviceVerification?.availableMethods || ['email', 'sms', 'totp', 'recovery_code'],
  
  // 验证码长度
  codeLength: config.security?.deviceVerification?.codeLength || 6,
  
  // 验证码有效期（秒）
  codeTTL: config.security?.deviceVerification?.codeTTL || 900, // 15分钟
  
  // 最大尝试次数
  maxAttempts: config.security?.deviceVerification?.maxAttempts || 5,
  
  // 最大重发次数
  maxResendCount: config.security?.deviceVerification?.maxResendCount || 3,
  
  // 是否自动信任通过验证的设备
  autoTrustVerifiedDevices: config.security?.deviceVerification?.autoTrustVerifiedDevices || true,
  
  // 允许用户选择"记住此设备"
  allowRememberDevice: config.security?.deviceVerification?.allowRememberDevice || true,
  
  // 设备记住持续时间（天）
  rememberDeviceDays: config.security?.deviceVerification?.rememberDeviceDays || 30
};

/**
 * 安全日志配置
 */
const SECURITY_LOGS = {
  // 是否启用安全日志
  enabled: config.security?.securityLogs?.enabled || true,
  
  // 日志保留时间（天）
  retentionDays: config.security?.securityLogs?.retentionDays || 90,
  
  // 是否记录敏感数据
  includeSensitiveData: config.security?.securityLogs?.includeSensitiveData || false,
  
  // 是否记录IP地址
  includeIPAddress: config.security?.securityLogs?.includeIPAddress || true,
  
  // 是否记录用户代理
  includeUserAgent: config.security?.securityLogs?.includeUserAgent || true,
  
  // 高优先级事件类型
  highPriorityEvents: config.security?.securityLogs?.highPriorityEvents || [
    SECURITY_EVENT_TYPES.ACCOUNT_LOCKED,
    SECURITY_EVENT_TYPES.MULTIPLE_FAILED_ATTEMPTS,
    SECURITY_EVENT_TYPES.SUSPICIOUS_ACTIVITY,
    SECURITY_EVENT_TYPES.UNUSUAL_LOCATION_ACCESS
  ]
};

/**
 * 安全通知配置
 */
const SECURITY_NOTIFICATIONS = {
  // 是否启用安全通知
  enabled: config.security?.notifications?.enabled || true,
  
  // 默认通知方法
  defaultMethod: config.security?.notifications?.defaultMethod || 'email',
  
  // 可用的通知方法
  availableMethods: config.security?.notifications?.availableMethods || ['email', 'sms', 'push', 'in_app'],
  
  // 需要发送通知的事件类型
  notifiableEvents: config.security?.notifications?.notifiableEvents || [
    SECURITY_EVENT_TYPES.PASSWORD_CHANGED,
    SECURITY_EVENT_TYPES.PASSWORD_RESET_REQUESTED,
    SECURITY_EVENT_TYPES.ACCOUNT_LOCKED,
    SECURITY_EVENT_TYPES.UNUSUAL_LOCATION_ACCESS,
    SECURITY_EVENT_TYPES.SUSPICIOUS_ACTIVITY,
    SECURITY_EVENT_TYPES.DEVICE_REGISTERED,
    SECURITY_EVENT_TYPES.TWO_FACTOR_ENABLED,
    SECURITY_EVENT_TYPES.TWO_FACTOR_DISABLED,
    SECURITY_EVENT_TYPES.RECOVERY_CODE_USED
  ],
  
  // 节流配置（相同类型的通知最短发送间隔，单位：秒）
  throttling: {
    default: config.security?.notifications?.throttling?.default || 300, // 5分钟
    byEventType: config.security?.notifications?.throttling?.byEventType || {
      [SECURITY_EVENT_TYPES.SUSPICIOUS_ACTIVITY]: 3600, // 1小时
      [SECURITY_EVENT_TYPES.UNUSUAL_LOCATION_ACCESS]: 3600 // 1小时
    }
  }
};

module.exports = {
  SECURITY_EVENT_TYPES,
  ANOMALY_DETECTION,
  DEVICE_VERIFICATION,
  SECURITY_LOGS,
  SECURITY_NOTIFICATIONS
};