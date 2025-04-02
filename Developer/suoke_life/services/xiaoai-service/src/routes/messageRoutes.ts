import { Router } from 'express';
import { messageController } from '../controllers/messageController';
import { validateMessageRequest } from '../middlewares/validationMiddleware';

const router = Router();

/**
 * @route POST /api/messages/text
 * @desc 处理用户文本消息
 * @access Public
 */
router.post('/text', validateMessageRequest, messageController.processTextMessage);

/**
 * @route POST /api/messages/voice
 * @desc 处理用户语音消息
 * @access Public
 */
router.post('/voice', messageController.processVoiceMessage);

/**
 * @route POST /api/messages/image
 * @desc 处理用户图像消息
 * @access Public
 */
router.post('/image', messageController.processImageMessage);

/**
 * @route GET /api/messages/history/:userId
 * @desc 获取指定用户的消息历史
 * @access Public
 */
router.get('/history/:userId', messageController.getUserMessageHistory);

/**
 * @route DELETE /api/messages/history/:userId
 * @desc 清除指定用户的消息历史
 * @access Public
 */
router.delete('/history/:userId', messageController.clearUserMessageHistory);

export default router;