import express from 'express';
import * as voiceGuidanceController from '../../controllers/voice-guidance.controller';
import { authenticateJWT, isAdmin } from '../middleware/auth.middleware';

const router = express.Router();

// 语音命令相关路由
/**
 * @swagger
 * /api/v1/voice-guidance/commands:
 *   get:
 *     summary: 获取所有语音命令
 *     tags: [VoiceGuidance]
 */
router.get('/commands', voiceGuidanceController.getAllVoiceCommands);

/**
 * @swagger
 * /api/v1/voice-guidance/commands/{id}:
 *   get:
 *     summary: 获取特定语音命令
 *     tags: [VoiceGuidance]
 */
router.get('/commands/scene/:scene', voiceGuidanceController.getVoiceCommandsByScene);

/**
 * @swagger
 * /api/v1/voice-guidance/commands:
 *   post:
 *     summary: 创建语音命令
 *     tags: [VoiceGuidance]
 */
router.post('/commands', authenticateJWT, isAdmin, voiceGuidanceController.createVoiceCommand);

/**
 * @swagger
 * /api/v1/voice-guidance/commands/match:
 *   post:
 *     summary: 匹配语音命令
 *     tags: [VoiceGuidance]
 */
router.post('/commands/match', voiceGuidanceController.matchVoiceCommand);

/**
 * @swagger
 * /api/v1/voice-guidance/commands/{id}:
 *   put:
 *     summary: 更新语音命令
 *     tags: [VoiceGuidance]
 */
router.put('/commands/:id', authenticateJWT, isAdmin, voiceGuidanceController.updateVoiceCommand);

/**
 * @swagger
 * /api/v1/voice-guidance/commands/{id}:
 *   delete:
 *     summary: 删除语音命令
 *     tags: [VoiceGuidance]
 */
router.delete('/commands/:id', authenticateJWT, isAdmin, voiceGuidanceController.deleteVoiceCommand);

// 语音引导内容相关路由
/**
 * @swagger
 * /api/v1/voice-guidance/contents:
 *   get:
 *     summary: 获取语音引导内容
 *     tags: [VoiceGuidance]
 */
router.get('/contents', voiceGuidanceController.getGuidanceContents);

/**
 * @swagger
 * /api/v1/voice-guidance/contents/{sceneType}/{event}:
 *   get:
 *     summary: 根据场景和事件获取匹配的引导内容
 *     tags: [VoiceGuidance]
 */
router.get('/contents/:sceneType/:event', voiceGuidanceController.getContextualGuidance);

/**
 * @swagger
 * /api/v1/voice-guidance/contents/{sceneType}/{sceneId}/{event}:
 *   get:
 *     summary: 根据特定场景ID和事件获取匹配的引导内容
 *     tags: [VoiceGuidance]
 */
router.get('/contents/:sceneType/:sceneId/:event', voiceGuidanceController.getContextualGuidance);

/**
 * @swagger
 * /api/v1/voice-guidance/contents:
 *   post:
 *     summary: 创建语音引导内容
 *     tags: [VoiceGuidance]
 */
router.post('/contents', authenticateJWT, isAdmin, voiceGuidanceController.createGuidanceContent);

/**
 * @swagger
 * /api/v1/voice-guidance/contents/{id}:
 *   put:
 *     summary: 更新语音引导内容
 *     tags: [VoiceGuidance]
 */
router.put('/contents/:id', authenticateJWT, isAdmin, voiceGuidanceController.updateGuidanceContent);

/**
 * @swagger
 * /api/v1/voice-guidance/contents/{id}:
 *   delete:
 *     summary: 删除语音引导内容
 *     tags: [VoiceGuidance]
 */
router.delete('/contents/:id', authenticateJWT, isAdmin, voiceGuidanceController.deleteGuidanceContent);

/**
 * @swagger
 * /api/v1/voice-guidance/contents/{guidanceId}/audio:
 *   post:
 *     summary: 生成引导音频
 *     tags: [VoiceGuidance]
 */
router.post('/contents/:guidanceId/audio', authenticateJWT, voiceGuidanceController.generateGuidanceAudio);

/**
 * @swagger
 * /api/v1/voice-guidance/audio/{fileName}:
 *   get:
 *     summary: 获取音频文件
 *     tags: [VoiceGuidance]
 */
router.get('/audio/:fileName', voiceGuidanceController.getAudioFile);

// 语音会话相关路由
/**
 * @swagger
 * /api/v1/voice-guidance/sessions:
 *   post:
 *     summary: 创建语音会话
 *     tags: [VoiceGuidance]
 */
router.post('/sessions', authenticateJWT, voiceGuidanceController.createVoiceSession);

/**
 * @swagger
 * /api/v1/voice-guidance/sessions/{sessionId}:
 *   post:
 *     summary: 结束语音会话
 *     tags: [VoiceGuidance]
 */
router.post('/sessions/:sessionId/end', authenticateJWT, voiceGuidanceController.endVoiceSession);

/**
 * @swagger
 * /api/v1/voice-guidance/sessions/{sessionId}/context:
 *   put:
 *     summary: 更新会话上下文
 *     tags: [VoiceGuidance]
 */
router.put('/sessions/:sessionId/context', authenticateJWT, voiceGuidanceController.updateSessionContext);

// 语音交互处理路由
/**
 * @swagger
 * /api/v1/voice-guidance/process/voice:
 *   post:
 *     summary: 处理语音输入
 *     tags: [VoiceGuidance]
 */
router.post('/process/voice', authenticateJWT, voiceGuidanceController.upload.single('audio'), voiceGuidanceController.processVoiceInput);

/**
 * @swagger
 * /api/v1/voice-guidance/process/text:
 *   post:
 *     summary: 处理文本输入
 *     tags: [VoiceGuidance]
 */
router.post('/process/text', authenticateJWT, voiceGuidanceController.processTextInput);

// 用户语音偏好设置路由
/**
 * @swagger
 * /api/v1/voice-guidance/preferences/{userId}:
 *   get:
 *     summary: 获取用户语音偏好设置
 *     tags: [VoiceGuidance]
 */
router.get('/preferences/:userId', authenticateJWT, voiceGuidanceController.getVoicePreference);

/**
 * @swagger
 * /api/v1/voice-guidance/preferences/{userId}:
 *   put:
 *     summary: 更新用户语音偏好设置
 *     tags: [VoiceGuidance]
 */
router.put('/preferences/:userId', authenticateJWT, voiceGuidanceController.updateVoicePreference);

export default router; 