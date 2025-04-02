import { Router } from 'express';
import * as accessibilityController from '../../controllers/accessibility/accessibility.controller';

const router = Router();

// 用户无障碍配置管理
router.get('/profile/:userId', accessibilityController.getUserProfile);
router.post('/profile/:userId', accessibilityController.createOrUpdateUserProfile);
router.delete('/profile/:userId', accessibilityController.deleteUserProfile);

// 屏幕阅读器相关
router.get('/screen-reader/settings/:userId', accessibilityController.getScreenReaderSettings);
router.put('/screen-reader/settings/:userId', accessibilityController.updateScreenReaderSettings);
router.post('/screen-reader/read/:userId', accessibilityController.readText);
router.post('/screen-reader/stop/:userId', accessibilityController.stopReading);

// UI元素注册
router.post('/ui/element', accessibilityController.registerUIElement);
router.post('/ui/elements', accessibilityController.registerUIElements);

// 语音导航相关
router.get('/navigation/settings/:userId', accessibilityController.getNavigationSettings);
router.put('/navigation/settings/:userId', accessibilityController.updateNavigationSettings);
router.post('/navigation/start/:userId', accessibilityController.startNavigation);
router.post('/navigation/end/:userId', accessibilityController.endNavigation);
router.post('/navigation/location/:userId', accessibilityController.updateUserLocation);

// 兴趣点管理
router.get('/points-of-interest', accessibilityController.getPointsOfInterest);

// 辅助功能工具
router.post('/announcement/:userId', accessibilityController.createAccessibilityAnnouncement);

// 初始化示例数据
router.post('/init-sample-data', accessibilityController.initSampleData);

export default router;