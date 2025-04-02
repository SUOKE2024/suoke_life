/**
 * 会话管理路由
 */
const express = require('express');
const router = express.Router();
const sessionController = require('../controllers/session.controller');
const { verifyToken } = require('../middlewares/auth.middleware');

/**
 * @swagger
 * /api/v1/auth/sessions:
 *   get:
 *     tags:
 *       - 会话管理
 *     summary: 获取当前用户的所有会话
 *     description: 获取当前登录用户的所有会话信息
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: activeOnly
 *         schema:
 *           type: boolean
 *           default: true
 *         description: 是否只返回活动会话
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *           default: 1
 *         description: 页码
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 10
 *         description: 每页数量
 *     responses:
 *       200:
 *         description: 成功返回会话列表
 *       401:
 *         description: 未授权
 *       500:
 *         description: 服务器错误
 */
router.get('/', verifyToken, sessionController.getUserSessions);

/**
 * @swagger
 * /api/v1/auth/sessions/{sessionId}:
 *   get:
 *     tags:
 *       - 会话管理
 *     summary: 获取会话详情
 *     description: 获取特定会话的详细信息
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: sessionId
 *         schema:
 *           type: string
 *         required: true
 *         description: 会话ID
 *     responses:
 *       200:
 *         description: 成功返回会话详情
 *       401:
 *         description: 未授权
 *       403:
 *         description: 无权访问该会话
 *       404:
 *         description: 会话不存在
 *       500:
 *         description: 服务器错误
 */
router.get('/:sessionId', verifyToken, sessionController.getSessionDetail);

/**
 * @swagger
 * /api/v1/auth/sessions/{sessionId}/revoke:
 *   post:
 *     tags:
 *       - 会话管理
 *     summary: 撤销会话
 *     description: 撤销（注销）指定的会话
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: sessionId
 *         schema:
 *           type: string
 *         required: true
 *         description: 会话ID
 *     requestBody:
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               reason:
 *                 type: string
 *                 description: 撤销原因
 *     responses:
 *       200:
 *         description: 会话已成功撤销
 *       400:
 *         description: 无法撤销当前活动会话
 *       401:
 *         description: 未授权
 *       403:
 *         description: 无权撤销该会话
 *       404:
 *         description: 会话不存在
 *       500:
 *         description: 服务器错误
 */
router.post('/:sessionId/revoke', verifyToken, sessionController.revokeSession);

/**
 * @swagger
 * /api/v1/auth/sessions/revoke-all:
 *   post:
 *     tags:
 *       - 会话管理
 *     summary: 撤销所有会话
 *     description: 撤销当前用户的所有会话（除当前会话外）
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               reason:
 *                 type: string
 *                 description: 撤销原因
 *     responses:
 *       200:
 *         description: 所有会话已成功撤销
 *       401:
 *         description: 未授权
 *       500:
 *         description: 服务器错误
 */
router.post('/revoke-all', verifyToken, sessionController.revokeAllSessions);

/**
 * @swagger
 * /api/v1/auth/sessions/{sessionId}/set-current:
 *   post:
 *     tags:
 *       - 会话管理
 *     summary: 设置当前会话
 *     description: 将指定会话设为当前会话
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: sessionId
 *         schema:
 *           type: string
 *         required: true
 *         description: 会话ID
 *     responses:
 *       200:
 *         description: 当前会话已成功设置
 *       400:
 *         description: 只能将活动会话设为当前会话
 *       401:
 *         description: 未授权
 *       403:
 *         description: 无权修改该会话
 *       404:
 *         description: 会话不存在
 *       500:
 *         description: 服务器错误
 */
router.post('/:sessionId/set-current', verifyToken, sessionController.setCurrentSession);

/**
 * @swagger
 * /api/v1/auth/sessions/suspicious:
 *   get:
 *     tags:
 *       - 会话管理
 *     summary: 获取可疑会话
 *     description: 获取当前用户的所有可疑会话
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: 成功返回可疑会话列表
 *       401:
 *         description: 未授权
 *       500:
 *         description: 服务器错误
 */
router.get('/suspicious', verifyToken, sessionController.getSuspiciousSessions);

/**
 * @swagger
 * /api/v1/auth/sessions/{sessionId}/approve:
 *   post:
 *     tags:
 *       - 会话管理
 *     summary: 确认可疑会话
 *     description: 将可疑会话标记为安全会话
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: sessionId
 *         schema:
 *           type: string
 *         required: true
 *         description: 会话ID
 *     responses:
 *       200:
 *         description: 会话已确认为可信会话
 *       400:
 *         description: 只能确认可疑会话
 *       401:
 *         description: 未授权
 *       403:
 *         description: 无权修改该会话
 *       404:
 *         description: 会话不存在
 *       500:
 *         description: 服务器错误
 */
router.post('/:sessionId/approve', verifyToken, sessionController.approveSuspiciousSession);

module.exports = router; 