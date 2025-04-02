/**
 * 会话管理控制器
 */
const sessionService = require('../services/session.service');
const securityLogService = require('../services/security-log.service');
const { logger } = require('@suoke/shared').utils;
const { ApplicationError } = require('../utils/errors');

/**
 * 获取当前用户的所有会话
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const getUserSessions = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { activeOnly = true, page = 1, limit = 10 } = req.query;
    
    const offset = (parseInt(page) - 1) * parseInt(limit);
    
    const result = await sessionService.getUserSessions(userId, {
      activeOnly: activeOnly === 'true' || activeOnly === true,
      limit: parseInt(limit),
      offset
    });
    
    res.status(200).json({
      success: true,
      data: result
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 获取特定会话详情
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const getSessionDetail = async (req, res, next) => {
  try {
    const { sessionId } = req.params;
    const userId = req.user.id;
    
    const session = await sessionService.getSession(sessionId);
    
    if (!session) {
      return res.status(404).json({
        success: false,
        message: '会话不存在',
        code: 'session/not-found'
      });
    }
    
    if (session.userId !== userId) {
      // 记录安全日志
      await securityLogService.logSecurityEvent(
        securityLogService.EVENT_TYPES.UNAUTHORIZED_ACCESS,
        {
          userId,
          targetResource: `session:${sessionId}`,
          action: 'get',
          ipAddress: req.ip,
          userAgent: req.headers['user-agent']
        }
      );
      
      return res.status(403).json({
        success: false,
        message: '无权访问此会话',
        code: 'session/access-denied'
      });
    }
    
    res.status(200).json({
      success: true,
      data: session
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 撤销（注销）特定会话
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const revokeSession = async (req, res, next) => {
  try {
    const { sessionId } = req.params;
    const userId = req.user.id;
    
    // 获取会话信息
    const session = await sessionService.getSession(sessionId);
    
    if (!session) {
      return res.status(404).json({
        success: false,
        message: '会话不存在',
        code: 'session/not-found'
      });
    }
    
    // 检查权限
    if (session.userId !== userId && req.user.role !== 'admin') {
      // 记录安全日志
      await securityLogService.logSecurityEvent(
        securityLogService.EVENT_TYPES.UNAUTHORIZED_ACCESS,
        {
          userId,
          targetResource: `session:${sessionId}`,
          action: 'revoke',
          ipAddress: req.ip,
          userAgent: req.headers['user-agent']
        }
      );
      
      return res.status(403).json({
        success: false,
        message: '无权撤销此会话',
        code: 'session/access-denied'
      });
    }
    
    // 检查是否当前会话
    if (session.isCurrent && req.sessionId === sessionId) {
      return res.status(400).json({
        success: false,
        message: '不能撤销当前活动会话，请使用注销功能',
        code: 'session/cannot-revoke-current'
      });
    }
    
    // 撤销会话
    const result = await sessionService.revokeSession(sessionId, {
      userId,
      reason: req.body.reason || '用户手动撤销'
    });
    
    if (!result) {
      return res.status(500).json({
        success: false,
        message: '撤销会话失败',
        code: 'session/revoke-failed'
      });
    }
    
    res.status(200).json({
      success: true,
      message: '会话已成功撤销'
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 撤销所有会话（除当前会话外）
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const revokeAllSessions = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const currentSessionId = req.sessionId;
    
    const count = await sessionService.revokeAllUserSessions(userId, {
      excludeSessionId: currentSessionId,
      reason: req.body.reason || '用户退出所有设备'
    });
    
    res.status(200).json({
      success: true,
      message: `已成功撤销 ${count} 个会话`,
      data: { count }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 将指定会话设为当前会话
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const setCurrentSession = async (req, res, next) => {
  try {
    const { sessionId } = req.params;
    const userId = req.user.id;
    
    // 获取会话信息
    const session = await sessionService.getSession(sessionId);
    
    if (!session) {
      return res.status(404).json({
        success: false,
        message: '会话不存在',
        code: 'session/not-found'
      });
    }
    
    // 检查权限
    if (session.userId !== userId) {
      return res.status(403).json({
        success: false,
        message: '无权修改此会话',
        code: 'session/access-denied'
      });
    }
    
    // 检查会话状态
    if (session.status !== sessionService.SESSION_STATUS.ACTIVE) {
      return res.status(400).json({
        success: false,
        message: '只能将活动会话设为当前会话',
        code: 'session/invalid-status'
      });
    }
    
    // 设置为当前会话
    const result = await sessionService.setCurrentSession(userId, sessionId);
    
    if (!result) {
      return res.status(500).json({
        success: false,
        message: '设置当前会话失败',
        code: 'session/set-current-failed'
      });
    }
    
    res.status(200).json({
      success: true,
      message: '已成功设置当前会话'
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 获取所有可疑会话
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const getSuspiciousSessions = async (req, res, next) => {
  try {
    const userId = req.user.id;
    
    // 查询所有可疑会话
    const sessions = await sessionService.getUserSessions(userId, {
      activeOnly: false,
      suspiciousOnly: true,
      limit: 100,
      offset: 0
    });
    
    res.status(200).json({
      success: true,
      data: sessions
    });
  } catch (error) {
    next(error);
  }
};

/**
 * 允许（确认）可疑会话
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const approveSuspiciousSession = async (req, res, next) => {
  try {
    const { sessionId } = req.params;
    const userId = req.user.id;
    
    // 获取会话信息
    const session = await sessionService.getSession(sessionId);
    
    if (!session) {
      return res.status(404).json({
        success: false,
        message: '会话不存在',
        code: 'session/not-found'
      });
    }
    
    // 检查权限
    if (session.userId !== userId) {
      return res.status(403).json({
        success: false,
        message: '无权修改此会话',
        code: 'session/access-denied'
      });
    }
    
    // 检查会话状态
    if (session.status !== sessionService.SESSION_STATUS.SUSPICIOUS) {
      return res.status(400).json({
        success: false,
        message: '只能确认可疑会话',
        code: 'session/invalid-status'
      });
    }
    
    // 更新会话状态为活动
    await sessionService.updateSessionStatus(sessionId, sessionService.SESSION_STATUS.ACTIVE);
    
    // 记录安全日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.SUSPICIOUS_SESSION_APPROVED,
      {
        userId,
        sessionId,
        ipAddress: req.ip,
        userAgent: req.headers['user-agent']
      }
    );
    
    res.status(200).json({
      success: true,
      message: '已确认会话为可信会话'
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getUserSessions,
  getSessionDetail,
  revokeSession,
  revokeAllSessions,
  setCurrentSession,
  getSuspiciousSessions,
  approveSuspiciousSession
}; 