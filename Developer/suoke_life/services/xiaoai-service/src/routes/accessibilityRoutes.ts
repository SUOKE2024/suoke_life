import { Router } from 'express';
import { accessibilityController } from '../controllers/accessibilityController';

const router = Router();

/**
 * @route GET /api/accessibility/profile/:userId
 * @desc 获取用户的无障碍需求配置
 * @access Public
 */
router.get('/profile/:userId', accessibilityController.getUserAccessibilityProfile);

/**
 * @route PUT /api/accessibility/profile/:userId
 * @desc 更新用户的无障碍需求配置
 * @access Public
 */
router.put('/profile/:userId', accessibilityController.updateUserAccessibilityProfile);

/**
 * @route POST /api/accessibility/voice-guidance
 * @desc 生成语音引导内容
 * @access Public
 */
router.post('/voice-guidance', accessibilityController.generateVoiceGuidance);

/**
 * @route POST /api/accessibility/blind-guidance
 * @desc 为视障用户生成特殊引导
 * @access Public
 */
router.post('/blind-guidance', accessibilityController.generateBlindGuidance);

/**
 * @route POST /api/accessibility/detect
 * @desc 自动检测用户可能的无障碍需求
 * @access Public
 */
router.post('/detect/:userId', accessibilityController.detectUserAccessibilityNeeds);

/**
 * @route GET /api/accessibility/tips/:userId
 * @desc 获取针对用户的无障碍使用提示
 * @access Public
 */
router.get('/tips/:userId', accessibilityController.getAccessibilityTips);

export default router;