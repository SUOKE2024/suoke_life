/**
 * Prometheus指标收集工具
 */
const client = require('prom-client');
const config = require('../config');

// 创建注册表
const register = new client.Registry();

// 添加默认指标
client.collectDefaultMetrics({
  prefix: config.metrics?.prefix || 'user_',
  register,
  labels: config.metrics?.defaultLabels || {
    service: 'user-service',
    environment: process.env.NODE_ENV || 'development'
  }
});

// HTTP请求计数器
const httpRequestsTotal = new client.Counter({
  name: 'user_http_requests_total',
  help: '用户服务HTTP请求总数',
  labelNames: ['method', 'endpoint', 'status'],
  registers: [register]
});

// HTTP请求持续时间
const httpRequestDurationSeconds = new client.Histogram({
  name: 'user_request_duration_seconds',
  help: '用户服务HTTP请求持续时间（秒）',
  labelNames: ['method', 'endpoint', 'status'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10],
  registers: [register]
});

// 数据库查询时间
const databaseQueryTimeSeconds = new client.Histogram({
  name: 'user_database_query_time_seconds',
  help: '数据库查询时间（秒）',
  labelNames: ['operation', 'table'],
  buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1],
  registers: [register]
});

// 认证失败计数
const authFailuresTotal = new client.Counter({
  name: 'user_auth_failures_total',
  help: '认证失败总数',
  labelNames: ['method', 'reason'],
  registers: [register]
});

// 认证尝试计数
const authAttemptsTotal = new client.Counter({
  name: 'user_auth_attempts_total',
  help: '认证尝试总数',
  labelNames: ['method', 'result'],
  registers: [register]
});

// 用户操作计数
const userOperationsTotal = new client.Counter({
  name: 'user_operations_total',
  help: '用户操作总数',
  labelNames: ['operation', 'result'],
  registers: [register]
});

// 数据库连接错误
const databaseConnectionErrors = new client.Counter({
  name: 'user_database_connection_errors_total',
  help: '数据库连接错误总数',
  registers: [register]
});

// 活跃会话数
const activeSessions = new client.Gauge({
  name: 'user_active_sessions',
  help: '活跃会话数',
  registers: [register]
});

// Redis连接错误
const redisConnectionErrors = new client.Counter({
  name: 'user_redis_connection_errors_total',
  help: 'Redis连接错误总数',
  registers: [register]
});

// 缓存命中率
const cacheHitRatio = new client.Gauge({
  name: 'user_cache_hit_ratio',
  help: '缓存命中率',
  registers: [register]
});

// 注册用户总数
const registeredUsersTotal = new client.Gauge({
  name: 'user_registered_users_total',
  help: '注册用户总数',
  registers: [register]
});

// 活跃用户数（当日登录）
const activeUsersDaily = new client.Gauge({
  name: 'user_active_users_daily',
  help: '当日活跃用户数',
  registers: [register]
});

// API速率限制触发次数
const rateLimitTriggeredTotal = new client.Counter({
  name: 'user_rate_limit_triggered_total',
  help: 'API速率限制触发次数',
  labelNames: ['endpoint', 'ip'],
  registers: [register]
});

// 授权失败计数
const authorizationFailuresTotal = new client.Counter({
  name: 'user_authorization_failures_total',
  help: '授权失败总数',
  labelNames: ['endpoint', 'role', 'required_permission'],
  registers: [register]
});

// 敏感数据访问计数
const sensitiveDataAccessesTotal = new client.Counter({
  name: 'user_sensitive_data_accesses_total',
  help: '敏感数据访问总数',
  labelNames: ['data_type', 'access_type'],
  registers: [register]
});

// OpenAI工具调用计数
const openaiToolCallsTotal = new client.Counter({
  name: 'user_openai_tool_calls_total',
  help: 'OpenAI工具调用总数',
  labelNames: ['tool_name', 'result'],
  registers: [register]
});

// OpenAI工具调用持续时间
const openaiToolCallDurationSeconds = new client.Histogram({
  name: 'user_openai_tool_call_duration_seconds',
  help: 'OpenAI工具调用持续时间（秒）',
  labelNames: ['tool_name'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10],
  registers: [register]
});

// 用户资料完整度分布
const userProfileCompletenessHistogram = new client.Histogram({
  name: 'user_profile_completeness_percent',
  help: '用户资料完整度百分比分布',
  buckets: [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
  registers: [register]
});

// 健康数据记录计数
const healthDataRecordsTotal = new client.Counter({
  name: 'user_health_data_records_total',
  help: '健康数据记录总数',
  labelNames: ['data_type'],
  registers: [register]
});

// 数据加密操作计数
const encryptionOperationsTotal = new client.Counter({
  name: 'user_encryption_operations_total',
  help: '数据加密操作总数',
  labelNames: ['operation', 'result'],
  registers: [register]
});

// 中间件函数，用于记录HTTP请求指标
const metricsMiddleware = (req, res, next) => {
  // 跳过对指标端点本身的监控
  if (req.path === '/metrics') {
    return next();
  }

  const start = process.hrtime();
  
  // 添加响应回调
  res.on('finish', () => {
    const hrtime = process.hrtime(start);
    const durationInSeconds = hrtime[0] + (hrtime[1] / 1e9);
    
    const routePath = req.route ? req.route.path : req.path;
    const method = req.method;
    const status = res.statusCode;
    
    // 记录请求计数和持续时间
    httpRequestsTotal.inc({
      method,
      endpoint: routePath,
      status
    });
    
    httpRequestDurationSeconds.observe(
      {
        method,
        endpoint: routePath,
        status
      },
      durationInSeconds
    );
    
    // 记录速率限制指标（如果适用）
    if (status === 429) {
      rateLimitTriggeredTotal.inc({
        endpoint: routePath,
        ip: req.ip || 'unknown'
      });
    }
    
    // 记录授权错误（如果适用）
    if (status === 403) {
      authorizationFailuresTotal.inc({
        endpoint: routePath,
        role: req.user?.role || 'anonymous',
        required_permission: req.requiredPermission || 'unknown'
      });
    }
  });
  
  next();
};

// 数据库指标中间件 - 记录数据库操作指标
const dbMetricsMiddleware = (db) => {
  const originalQuery = db.query;
  
  db.query = async (sql, params) => {
    const start = process.hrtime();
    
    try {
      const result = await originalQuery.call(db, sql, params);
      
      // 计算查询时间
      const hrtime = process.hrtime(start);
      const durationInSeconds = hrtime[0] + (hrtime[1] / 1e9);
      
      // 识别操作类型和表名
      const operation = sql.trim().split(' ')[0].toLowerCase();
      let table = 'unknown';
      
      // 简单解析表名
      const matchTable = sql.match(/FROM\s+([^\s,]+)/i) || sql.match(/INTO\s+([^\s,]+)/i) || sql.match(/UPDATE\s+([^\s,]+)/i);
      if (matchTable && matchTable[1]) {
        table = matchTable[1].replace(/[`'"]/g, '');
      }
      
      // 记录数据库查询时间
      databaseQueryTimeSeconds.observe({ operation, table }, durationInSeconds);
      
      return result;
    } catch (error) {
      // 记录数据库连接错误
      if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT' || error.code === 'PROTOCOL_CONNECTION_LOST') {
        databaseConnectionErrors.inc();
      }
      throw error;
    }
  };
  
  return db;
};

// Redis指标中间件 - 记录Redis操作指标
const redisMetricsMiddleware = (redis) => {
  // 增强原始命令方法
  const originalSend = redis.send_command;
  
  redis.send_command = async (...args) => {
    const start = process.hrtime();
    
    try {
      const result = await originalSend.apply(redis, args);
      
      // 计算命令执行时间
      const hrtime = process.hrtime(start);
      const durationInSeconds = hrtime[0] + (hrtime[1] / 1e9);
      
      // TODO: 记录Redis命令执行时间指标
      
      return result;
    } catch (error) {
      // 记录Redis连接错误
      if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT' || error.code === 'CONNECTION_BROKEN') {
        redisConnectionErrors.inc();
      }
      throw error;
    }
  };
  
  return redis;
};

// 统计会话计数的函数
const trackSessionMetrics = (sessionCount) => {
  activeSessions.set(sessionCount);
};

// 记录认证指标的函数
const trackAuthMetrics = (method, success, errorReason = null) => {
  authAttemptsTotal.inc({
    method,
    result: success ? 'success' : 'failure'
  });
  
  if (!success) {
    authFailuresTotal.inc({
      method,
      reason: errorReason || 'unknown'
    });
  }
};

// 跟踪OpenAI工具调用指标
const trackOpenAIToolMetrics = (toolName, success, durationInSeconds) => {
  openaiToolCallsTotal.inc({
    tool_name: toolName,
    result: success ? 'success' : 'failure'
  });
  
  openaiToolCallDurationSeconds.observe({
    tool_name: toolName
  }, durationInSeconds);
};

// 记录加密操作指标
const trackEncryptionMetrics = (operation, success) => {
  encryptionOperationsTotal.inc({
    operation,
    result: success ? 'success' : 'failure'
  });
};

// 记录用户操作指标
const trackUserOperationMetrics = (operation, success) => {
  userOperationsTotal.inc({
    operation,
    result: success ? 'success' : 'failure'
  });
};

// 记录敏感数据访问指标
const trackSensitiveDataAccessMetrics = (dataType, accessType) => {
  sensitiveDataAccessesTotal.inc({
    data_type: dataType,
    access_type: accessType
  });
};

// 更新用户统计指标
const updateUserCountMetrics = async (userRepository) => {
  try {
    // 获取总用户数
    const totalUsers = await userRepository.countUsers();
    registeredUsersTotal.set(totalUsers);
    
    // 获取活跃用户数（今日登录）
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const activeUsers = await userRepository.countActiveUsersSince(today);
    activeUsersDaily.set(activeUsers);
  } catch (error) {
    console.error('更新用户统计指标失败:', error);
  }
};

// 重置所有指标（用于测试）
const resetMetrics = () => {
  register.clear();
};

module.exports = {
  register,
  metricsMiddleware,
  dbMetricsMiddleware,
  redisMetricsMiddleware,
  trackSessionMetrics,
  trackAuthMetrics,
  trackOpenAIToolMetrics,
  trackEncryptionMetrics,
  trackUserOperationMetrics,
  trackSensitiveDataAccessMetrics,
  updateUserCountMetrics,
  // 导出指标对象
  httpRequestsTotal,
  httpRequestDurationSeconds,
  databaseQueryTimeSeconds,
  authFailuresTotal,
  authAttemptsTotal,
  userOperationsTotal,
  databaseConnectionErrors,
  activeSessions,
  redisConnectionErrors,
  cacheHitRatio,
  registeredUsersTotal,
  activeUsersDaily,
  rateLimitTriggeredTotal,
  authorizationFailuresTotal,
  sensitiveDataAccessesTotal,
  openaiToolCallsTotal,
  openaiToolCallDurationSeconds,
  userProfileCompletenessHistogram,
  healthDataRecordsTotal,
  encryptionOperationsTotal,
  resetMetrics
}; 