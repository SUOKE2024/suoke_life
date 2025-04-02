/**
 * 会话管理路由
 */
import { Router } from 'express';
import { SessionController } from '../controllers/session-controller';
import { validateCreateSession, validateUpdateSession } from '../middlewares/validation-middleware';

const router = Router();
const sessionController = new SessionController();

/**
 * @swagger
 * /api/sessions:
 *   post:
 *     summary: 创建新的用户会话
 *     description: 为用户创建新的智能体会话
 *     tags: [Sessions]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - userId
 *             properties:
 *               userId:
 *                 type: string
 *               preferredAgentId:
 *                 type: string
 *               initialContext:
 *                 type: object
 *     responses:
 *       201:
 *         description: 会话创建成功
 */
router.post('/', validateCreateSession, sessionController.createSession);

/**
 * @swagger
 * /api/sessions/{sessionId}:
 *   get:
 *     summary: 获取会话信息
 *     description: 根据会话ID获取会话详细信息
 *     tags: [Sessions]
 *     parameters:
 *       - in: path
 *         name: sessionId
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: 会话信息
 */
router.get('/:sessionId', sessionController.getSession);

/**
 * @swagger
 * /api/sessions/{sessionId}:
 *   put:
 *     summary: 更新会话信息
 *     description: 更新会话上下文或状态
 *     tags: [Sessions]
 *     parameters:
 *       - in: path
 *         name: sessionId
 *         required: true
 *         schema:
 *           type: string
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               context:
 *                 type: object
 *               status:
 *                 type: string
 *                 enum: [active, paused, completed]
 *     responses:
 *       200:
 *         description: 会话更新成功
 */
router.put('/:sessionId', validateUpdateSession, sessionController.updateSession);

/**
 * @swagger
 * /api/sessions/{sessionId}:
 *   delete:
 *     summary: 结束会话
 *     description: 结束并清理会话资源
 *     tags: [Sessions]
 *     parameters:
 *       - in: path
 *         name: sessionId
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       204:
 *         description: 会话已结束
 */
router.delete('/:sessionId', sessionController.endSession);

/**
 * @swagger
 * /api/sessions/{sessionId}/messages:
 *   get:
 *     summary: 获取会话消息历史
 *     description: 获取指定会话的消息历史记录
 *     tags: [Sessions]
 *     parameters:
 *       - in: path
 *         name: sessionId
 *         required: true
 *         schema:
 *           type: string
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 50
 *       - in: query
 *         name: offset
 *         schema:
 *           type: integer
 *           default: 0
 *     responses:
 *       200:
 *         description: 消息历史列表
 */
router.get('/:sessionId/messages', sessionController.getSessionMessages);

export default router;