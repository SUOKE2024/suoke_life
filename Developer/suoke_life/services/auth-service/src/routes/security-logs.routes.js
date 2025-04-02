/**
 * 安全日志路由
 */
const express = require('express');
const router = express.Router();
const { verifyToken, verifyAdmin } = require('../middlewares/auth.middleware');
const securityLogService = require('../services/security-log.service');

/**
 * @swagger
 * /api/auth/security-logs:
 *   get:
 *     tags:
 *       - 安全日志
 *     summary: 获取当前用户的安全日志
 *     description: 返回当前用户的安全事件日志列表
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 20
 *         description: 要返回的日志数量
 *       - in: query
 *         name: offset
 *         schema:
 *           type: integer
 *           default: 0
 *         description: 分页偏移量
 *       - in: query
 *         name: startTime
 *         schema:
 *           type: string
 *           format: date-time
 *         description: 开始时间（ISO格式）
 *       - in: query
 *         name: endTime
 *         schema:
 *           type: string
 *           format: date-time
 *         description: 结束时间（ISO格式）
 *     responses:
 *       200:
 *         description: 成功获取安全日志
 *       401:
 *         description: 未授权
 *       500:
 *         description: 服务器错误
 */
router.get('/', verifyToken, async (req, res, next) => {
  try {
    const userId = req.user.id;
    
    // 获取查询参数
    const limit = parseInt(req.query.limit) || 20;
    const offset = parseInt(req.query.offset) || 0;
    const startTime = req.query.startTime;
    const endTime = req.query.endTime;
    
    // 从服务获取日志
    const logs = await securityLogService.getUserSecurityLogs(userId, {
      limit,
      offset,
      startTime,
      endTime
    });
    
    return res.status(200).json({
      success: true,
      data: logs,
      pagination: {
        limit,
        offset,
        total: logs.length // 注意: 这里不是真正的总数，只是当前返回的数量
      }
    });
  } catch (error) {
    return next(error);
  }
});

/**
 * @swagger
 * /api/auth/security-logs/user/{userId}:
 *   get:
 *     tags:
 *       - 安全日志
 *     summary: 获取指定用户的安全日志（仅限管理员）
 *     description: 管理员可以获取任何用户的安全事件日志
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: userId
 *         required: true
 *         schema:
 *           type: string
 *         description: 用户ID
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 20
 *         description: 要返回的日志数量
 *       - in: query
 *         name: offset
 *         schema:
 *           type: integer
 *           default: 0
 *         description: 分页偏移量
 *       - in: query
 *         name: startTime
 *         schema:
 *           type: string
 *           format: date-time
 *         description: 开始时间（ISO格式）
 *       - in: query
 *         name: endTime
 *         schema:
 *           type: string
 *           format: date-time
 *         description: 结束时间（ISO格式）
 *     responses:
 *       200:
 *         description: 成功获取安全日志
 *       401:
 *         description: 未授权
 *       403:
 *         description: 权限不足
 *       404:
 *         description: 用户不存在
 *       500:
 *         description: 服务器错误
 */
router.get('/user/:userId', verifyToken, verifyAdmin, async (req, res, next) => {
  try {
    const userId = req.params.userId;
    
    // 验证用户存在
    const { db } = require('../config/database');
    const user = await db('users').where('id', userId).first();
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: '用户不存在',
        code: 'auth/user-not-found'
      });
    }
    
    // 获取查询参数
    const limit = parseInt(req.query.limit) || 20;
    const offset = parseInt(req.query.offset) || 0;
    const startTime = req.query.startTime;
    const endTime = req.query.endTime;
    
    // 从服务获取日志
    const logs = await securityLogService.getUserSecurityLogs(userId, {
      limit,
      offset,
      startTime,
      endTime
    });
    
    return res.status(200).json({
      success: true,
      data: logs,
      user: {
        id: user.id,
        username: user.username,
        email: user.email
      },
      pagination: {
        limit,
        offset,
        total: logs.length
      }
    });
  } catch (error) {
    return next(error);
  }
});

module.exports = router;