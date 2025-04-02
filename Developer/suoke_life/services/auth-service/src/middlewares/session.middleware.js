/**
 * 会话中间件
 * 用于处理用户会话相关的验证和处理
 */
const jwt = require('jsonwebtoken');
const Redis = require('ioredis');
const config = require('../config');
const { logger } = require('@suoke/shared').utils;
const sessionService = require('../services/session.service');

// 创建Redis客户端
const redis = new Redis({
  host: config.redis.host,
  port: config.redis.port
});

/**
 * 验证会话有效性中间件
 * 必须在 verifyToken 中间件之后使用
 */
const verifySession = async (req, res, next) => {
  try {
    // 确保已经通过认证中间件
    if (!req.user) {
      return res.status(401).json({ 
        success: false, 
        message: '未授权访问', 
        code: 'auth/unauthorized' 
      });
    }
    
    // 从令牌中获取会话ID
    const authHeader = req.headers.authorization;
    const token = authHeader.substring(7); // 去掉'Bearer '前缀
    
    // 验证令牌，不抛出异常，只解码
    const decoded = jwt.decode(token);
    const sessionId = decoded.sid;
    
    if (!sessionId) {
      return res.status(401).json({
        success: false,
        message: '无效的会话令牌',
        code: 'auth/invalid-session'
      });
    }
    
    // 验证会话是否有效
    const sessionExists = await sessionService.isSessionValid(sessionId, req.user.id);
    if (!sessionExists) {
      return res.status(401).json({
        success: false,
        message: '会话已过期或无效',
        code: 'auth/expired-session'
      });
    }
    
    // 更新会话活动状态
    await sessionService.updateSessionActivity(sessionId);
    
    // 将会话ID附加到请求对象
    req.session = {
      id: sessionId
    };
    
    next();
  } catch (error) {
    logger.error(`验证会话错误: ${error.message}`, { error });
    return res.status(500).json({
      success: false,
      message: '内部服务器错误',
      code: 'server/internal-error'
    });
  }
};

/**
 * 检查会话可疑性中间件
 * 基于用户行为和访问模式检测可疑会话
 * 在verifySession中间件之后使用
 */
const checkSuspiciousSession = async (req, res, next) => {
  try {
    // 确保会话已验证
    if (!req.session || !req.session.id) {
      return next();
    }
    
    // 获取会话详情
    const session = await sessionService.getSessionById(req.session.id, req.user.id);
    
    // 如果会话状态是可疑的，返回警告
    if (session && session.status === 'suspicious') {
      // 添加警告标志但允许请求继续
      req.session.suspicious = true;
      
      // 在响应头中添加可疑会话标记
      res.set('X-Session-Status', 'suspicious');
    }
    
    next();
  } catch (error) {
    // 只记录错误但不阻止请求
    logger.error(`检查可疑会话错误: ${error.message}`, { error, sessionId: req.session?.id });
    next();
  }
};

module.exports = {
  verifySession,
  checkSuspiciousSession
};