/**
 * 协调操作路由
 */
import { Router } from 'express';
import { CoordinationController } from '../controllers/coordination-controller';
import { validateCoordinationRequest } from '../middlewares/validation-middleware';

const router = Router();
const coordinationController = new CoordinationController();

/**
 * @swagger
 * /api/coordination/route:
 *   post:
 *     summary: 智能路由请求
 *     description: 根据用户查询内容自动路由到合适的智能体
 *     tags: [Coordination]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - sessionId
 *               - query
 *             properties:
 *               sessionId:
 *                 type: string
 *               query:
 *                 type: string
 *               context:
 *                 type: object
 *     responses:
 *       200:
 *         description: 路由响应结果
 */
router.post('/route', validateCoordinationRequest, coordinationController.routeRequest);

/**
 * @swagger
 * /api/coordination/handoff:
 *   post:
 *     summary: 代理服务交接
 *     description: 将会话从一个代理交接给另一个代理
 *     tags: [Coordination]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - sessionId
 *               - fromAgentId
 *               - toAgentId
 *               - reason
 *             properties:
 *               sessionId:
 *                 type: string
 *               fromAgentId:
 *                 type: string
 *               toAgentId:
 *                 type: string
 *               reason:
 *                 type: string
 *               context:
 *                 type: object
 *     responses:
 *       200:
 *         description: 交接结果
 */
router.post('/handoff', coordinationController.handoffSession);

/**
 * @swagger
 * /api/coordination/analyze:
 *   post:
 *     summary: 分析用户查询
 *     description: 分析用户查询内容，提供路由建议但不执行实际路由
 *     tags: [Coordination]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - query
 *             properties:
 *               query:
 *                 type: string
 *               context:
 *                 type: object
 *     responses:
 *       200:
 *         description: 分析结果
 */
router.post('/analyze', coordinationController.analyzeQuery);

/**
 * @swagger
 * /api/coordination/capabilities:
 *   get:
 *     summary: 获取系统总体能力
 *     description: 获取所有代理服务的综合能力列表
 *     tags: [Coordination]
 *     responses:
 *       200:
 *         description: 系统能力列表
 */
router.get('/capabilities', coordinationController.getSystemCapabilities);

export default router;