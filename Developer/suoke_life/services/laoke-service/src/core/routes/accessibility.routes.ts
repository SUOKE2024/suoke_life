import express from 'express';
import * as accessibilityController from '../../services/accessibility/accessibility.controller';
import { authenticate } from '../middleware/auth';
import { validateRequest } from '../middleware/validation';
import { accessibilityProfileSchema } from '../validation/accessibility.schema';

const router = express.Router();

// 获取无障碍资源
router.get('/resources', accessibilityController.getAccessibilityResources);

// 获取用户无障碍配置
router.get('/profile/:userId', authenticate, accessibilityController.getUserAccessibilityProfile);

// 更新用户无障碍配置
router.put('/profile/:userId', authenticate, validateRequest(accessibilityProfileSchema), accessibilityController.updateUserAccessibilityProfile);

export default router; 