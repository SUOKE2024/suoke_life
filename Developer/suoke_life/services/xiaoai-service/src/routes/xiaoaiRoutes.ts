import { Router } from 'express';
import { agentController } from '../controllers/agentController';
import { messageController } from '../controllers/messageController';

const router = Router();

// 获取智能体状态
router.get('/status', agentController.getAgentStatus);

// 更新智能体状态
router.put('/status', agentController.updateAgentStatus);

// 获取智能体能力
router.get('/capabilities', agentController.getAgentCapabilities);

// 重置智能体
router.post('/reset', agentController.resetAgent);

// 获取用户会话
router.get('/conversation/:userId', agentController.getConversationWithUser);

// 获取智能体指标
router.get('/metrics', agentController.getAgentMetrics);

// 文本消息处理
router.post('/messages/text', messageController.processTextMessage);

// 语音消息处理
router.post('/messages/voice', messageController.processVoiceMessage);

// 图像消息处理
router.post('/messages/image', messageController.processImageMessage);

// 获取会话历史
router.get('/messages/history/:userId', messageController.getUserMessageHistory);

// 清除会话历史
router.delete('/messages/history/:userId', messageController.clearUserMessageHistory);

export default router;
