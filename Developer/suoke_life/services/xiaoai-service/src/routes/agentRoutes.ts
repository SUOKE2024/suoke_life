import { Router } from 'express';
import { agentController } from '../controllers/agentController';

const router = Router();

/**
 * @route GET /api/agent/status
 * @desc 获取小艾智能体状态
 * @access Public
 */
router.get('/status', agentController.getAgentStatus);

/**
 * @route PUT /api/agent/status
 * @desc 更新小艾智能体状态
 * @access Public
 */
router.put('/status', agentController.updateAgentStatus);

/**
 * @route GET /api/agent/capabilities
 * @desc 获取小艾智能体能力列表
 * @access Public
 */
router.get('/capabilities', agentController.getAgentCapabilities);

/**
 * @route POST /api/agent/reset
 * @desc 重置小艾智能体
 * @access Public
 */
router.post('/reset', agentController.resetAgent);

/**
 * @route GET /api/agent/conversation/:userId
 * @desc 获取小艾智能体与特定用户的对话历史
 * @access Public
 */
router.get('/conversation/:userId', agentController.getConversationWithUser);

/**
 * @route GET /api/agent/metrics
 * @desc 获取小艾智能体使用指标
 * @access Public
 */
router.get('/metrics', agentController.getAgentMetrics);

export default router;