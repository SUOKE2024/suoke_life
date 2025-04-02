/**
 * 代理服务路由
 */
import { Router } from 'express';
import { AgentController } from '../controllers/agent-controller';
import { validateAgentRequest } from '../middlewares/validation-middleware';

const router = Router();
const agentController = new AgentController();

/**
 * @swagger
 * /api/agents:
 *   get:
 *     summary: 获取可用代理列表
 *     description: 获取系统中所有可用的智能体及其能力
 *     tags: [Agents]
 *     responses:
 *       200:
 *         description: 代理列表
 */
router.get('/', agentController.getAgents);

/**
 * @swagger
 * /api/agents/{agentId}:
 *   get:
 *     summary: 获取代理详情
 *     description: 获取指定代理的详细信息
 *     tags: [Agents]
 *     parameters:
 *       - in: path
 *         name: agentId
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: 代理详情
 */
router.get('/:agentId', agentController.getAgentById);

/**
 * @swagger
 * /api/agents/{agentId}/capabilities:
 *   get:
 *     summary: 检查代理能力
 *     description: 检查代理是否具有某种能力
 *     tags: [Agents]
 *     parameters:
 *       - in: path
 *         name: agentId
 *         required: true
 *         schema:
 *           type: string
 *       - in: query
 *         name: capability
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: 代理能力检查结果
 */
router.get('/:agentId/capabilities', agentController.checkAgentCapability);

/**
 * @swagger
 * /api/agents/{agentId}/query:
 *   post:
 *     summary: 向特定代理发送请求
 *     description: 直接向特定智能体发送查询请求
 *     tags: [Agents]
 *     parameters:
 *       - in: path
 *         name: agentId
 *         required: true
 *         schema:
 *           type: string
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
 *         description: 代理响应
 */
router.post('/:agentId/query', validateAgentRequest, agentController.queryAgent);

/**
 * @swagger
 * /api/agents/{agentId}/health:
 *   get:
 *     summary: 检查代理健康状态
 *     description: 检查特定代理服务的健康状态
 *     tags: [Agents]
 *     parameters:
 *       - in: path
 *         name: agentId
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: 代理健康状态
 */
router.get('/:agentId/health', agentController.checkAgentHealth);

export default router;