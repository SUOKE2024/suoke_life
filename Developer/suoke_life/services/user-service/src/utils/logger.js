/**
 * 日志工具
 * 确保日志输出到/app/logs目录，符合k8s配置
 */
const winston = require('winston');
const path = require('path');
const fs = require('fs');
const config = require('../config');

// 确保日志目录存在
const logDir = process.env.NODE_ENV === 'production' ? '/app/logs' : path.join(process.cwd(), 'logs');

try {
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }
} catch (error) {
  console.error(`创建日志目录失败: ${error.message}`);
}

// 创建格式化器
const formatter = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
  winston.format.errors({ stack: true }),
  config.logs?.format === 'json' 
    ? winston.format.json()
    : winston.format.printf(info => {
        const { timestamp, level, message, ...rest } = info;
        return `${timestamp} [${level.toUpperCase()}]: ${message} ${Object.keys(rest).length ? JSON.stringify(rest) : ''}`;
      })
);

// 创建logger实例
const logger = winston.createLogger({
  level: config.logs?.level || 'info',
  format: formatter,
  defaultMeta: { 
    service: 'user-service',
    environment: process.env.NODE_ENV || 'development'
  },
  transports: [
    // 控制台输出
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        formatter
      )
    }),
    // 文件输出
    new winston.transports.File({ 
      filename: path.join(logDir, 'error.log'), 
      level: 'error',
      maxsize: 10 * 1024 * 1024, // 10MB
      maxFiles: 5,
    }),
    new winston.transports.File({ 
      filename: path.join(logDir, 'combined.log'),
      maxsize: 10 * 1024 * 1024, // 10MB
      maxFiles: 5,
    })
  ]
});

// 敏感数据过滤器
const sensitiveKeys = ['password', 'token', 'secret', 'key', 'credentials'];

const maskSensitiveData = (obj) => {
  if (typeof obj !== 'object' || obj === null) {
    return obj;
  }
  
  const maskedObj = { ...obj };
  
  for (const key in maskedObj) {
    if (sensitiveKeys.some(sensitiveKey => key.toLowerCase().includes(sensitiveKey))) {
      maskedObj[key] = '******';
    } else if (typeof maskedObj[key] === 'object') {
      maskedObj[key] = maskSensitiveData(maskedObj[key]);
    }
  }
  
  return maskedObj;
};

// 包装logger方法以过滤敏感数据
const wrappedLogger = {};

['error', 'warn', 'info', 'debug', 'verbose', 'silly'].forEach(level => {
  wrappedLogger[level] = (message, meta = {}) => {
    const maskedMeta = maskSensitiveData(meta);
    return logger[level](message, maskedMeta);
  };
});

// 添加自定义日志方法
wrappedLogger.access = (req, res) => {
  const { method, originalUrl, ip, user } = req;
  const { statusCode } = res;
  const responseTime = res.responseTime;

  return logger.info('访问日志', {
    method,
    url: originalUrl,
    statusCode,
    responseTime,
    ip,
    userId: user?.id || 'anonymous'
  });
};

wrappedLogger.audit = (action, resource, userId, details = {}) => {
  return logger.info('审计日志', {
    action,
    resource,
    userId,
    details: maskSensitiveData(details)
  });
};

// 日志生命周期事件
wrappedLogger.startService = () => {
  logger.info('用户服务启动', {
    timestamp: new Date().toISOString(),
    nodeVersion: process.version,
    platform: process.platform,
    arch: process.arch,
    pid: process.pid
  });
};

wrappedLogger.stopService = () => {
  logger.info('用户服务停止', {
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
};

// 导出
module.exports = wrappedLogger; 