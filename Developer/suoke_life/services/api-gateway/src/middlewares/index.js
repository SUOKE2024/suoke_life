/**
 * 中间件索引文件
 * 导出所有中间件
 */
const express = require('express');
const helmet = require('helmet');
const compression = require('compression');
const cors = require('cors');
const morgan = require('morgan');
const logger = require('../utils/logger');
const config = require('../config');
const knowledgeRouter = require('./knowledge-router');

/**
 * 安全中间件 - 使用helmet增强应用安全性
 * @param {Express} app Express应用实例
 */
const security = (app) => {
  logger.info('加载安全中间件');
  app.use(helmet(config.security.helmet));
  // 禁用X-Powered-By头以隐藏服务器信息
  app.disable('x-powered-by');
};

/**
 * 压缩中间件 - 压缩响应以减少网络传输量
 * @param {Express} app Express应用实例
 */
const compression = (app) => {
  logger.info('加载压缩中间件');
  app.use(compression());
};

/**
 * CORS中间件 - 处理跨域资源共享
 * @param {Express} app Express应用实例
 */
const cors = (app) => {
  logger.info('加载CORS中间件');
  app.use(cors(config.security.cors));
};

/**
 * JSON解析中间件 - 解析JSON请求体
 * @param {Express} app Express应用实例
 */
const jsonParser = (app) => {
  logger.info('加载JSON解析中间件');
  app.use(express.json({ 
    limit: '1mb',
    strict: true
  }));
};

/**
 * URL编码解析中间件 - 解析URL编码的请求体
 * @param {Express} app Express应用实例
 */
const urlEncodedParser = (app) => {
  logger.info('加载URL编码解析中间件');
  app.use(express.urlencoded({ 
    extended: true,
    limit: '1mb'
  }));
};

/**
 * 请求日志中间件 - 记录HTTP请求
 * @param {Express} app Express应用实例
 */
const requestLogger = (app) => {
  logger.info('加载请求日志中间件');
  
  // 开发环境使用更详细的日志格式
  const morganFormat = config.server.env === 'development' ? 'dev' : 'combined';
  
  // 使用morgan记录HTTP请求日志
  app.use(morgan(morganFormat, { stream: logger.stream }));
  
  // 添加额外的请求/响应记录中间件
  app.use((req, res, next) => {
    // 记录请求开始时间
    req._startTime = Date.now();
    
    // 获取原始的响应end方法
    const originalEnd = res.end;
    
    // 重写响应end方法，以便在响应发送后记录额外信息
    res.end = function(chunk, encoding) {
      // 恢复原始的响应end方法
      res.end = originalEnd;
      
      // 计算请求处理时间
      const responseTime = Date.now() - req._startTime;
      
      // 调用原始方法发送响应
      res.end(chunk, encoding);
      
      // 记录请求/响应详情
      logger.debug('请求处理完成', {
        method: req.method,
        url: req.originalUrl,
        ip: req.ip,
        status: res.statusCode,
        responseTime: `${responseTime}ms`,
        // 只在开发环境记录请求头和响应头
        headers: config.server.env === 'development' ? req.headers : undefined,
        responseHeaders: config.server.env === 'development' ? res.getHeaders() : undefined
      });
    };
    
    next();
  });
};

/**
 * 错误处理中间件 - 捕获并处理应用错误
 * @param {Express} app Express应用实例
 */
const errorHandler = (app) => {
  logger.info('加载错误处理中间件');
  
  // 未捕获的错误处理中间件
  app.use((err, req, res, next) => {
    // 记录错误
    logger.error('请求处理错误', {
      error: err.stack || err,
      method: req.method,
      url: req.originalUrl,
      ip: req.ip
    });
    
    // 设置状态码（使用错误的状态码或默认为500）
    const statusCode = err.statusCode || 500;
    
    // 发送错误响应
    res.status(statusCode).json({
      error: statusCode === 500 ? '服务器内部错误' : err.message,
      message: config.server.env === 'production' ? '发生错误，请稍后再试' : err.message,
      // 只在非生产环境包含堆栈信息
      stack: config.server.env === 'production' ? undefined : err.stack
    });
  });
};

/**
 * 身份验证中间件 - 验证请求身份
 * @param {Express} app Express应用实例
 */
const authentication = (app) => {
  logger.info('加载身份验证中间件');
  
  // TODO: 实现身份验证逻辑，例如JWT验证
  app.use((req, res, next) => {
    // 跳过对公开路由的验证
    if (isPublicRoute(req.path)) {
      return next();
    }
    
    // TODO: 实现身份验证逻辑
    // 例如：从Authorization头中提取JWT令牌并验证
    
    next();
  });
};

/**
 * 检查路径是否为公开路由（无需身份验证）
 * @param {string} path 请求路径
 * @returns {boolean} 是否为公开路由
 */
const isPublicRoute = (path) => {
  const publicRoutes = [
    '/health',
    '/health/ready',
    '/metrics',
    '/api/v1/auth/login',
    '/api/v1/auth/register'
  ];
  
  return publicRoutes.some(route => path.startsWith(route));
};

/**
 * 智能知识路由中间件 - 智能路由知识相关请求
 * @param {Express} app Express应用实例
 */
const intelligentKnowledgeRouter = (app) => {
  logger.info('加载智能知识路由中间件');
  
  // 使用知识路由中间件
  app.use(knowledgeRouter);
};

module.exports = {
  security,
  compression,
  cors,
  jsonParser,
  urlEncodedParser,
  requestLogger,
  errorHandler,
  authentication,
  intelligentKnowledgeRouter
}; 