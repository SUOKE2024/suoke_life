import { Router } from 'express';
import { dialectController } from '../controllers/dialectController';
import { upload } from '../middlewares/upload.middleware';
import { authenticate } from '../middlewares/auth.middleware';

const router = Router();

// 获取所有支持的方言列表
router.get('/supported', dialectController.getSupportedDialects);

// 获取所有活跃的方言列表 
router.get('/', dialectController.getAllActiveDialects);

// 获取用户的方言偏好设置
router.get('/user/:userId', dialectController.getUserDialectPreferences);

// 更新用户的方言偏好设置
router.put('/user/:userId', dialectController.updateUserDialectPreferences);

// 检测文本使用的方言
router.post('/detect-text', dialectController.detectDialect);

// 检测音频中的方言
router.post('/detect-audio', upload.single('audio'), dialectController.detectAudioDialect);

// 将文本翻译成指定方言
router.post('/translate-text', dialectController.translateToDialect);

// 将方言音频翻译为标准普通话
router.post('/translate-audio', upload.single('audio'), dialectController.translateDialect);

// 将方言文本转换为普通话
router.post('/to-mandarin', dialectController.translateToMandarin);

// 获取方言的文化背景信息
router.get('/:dialectCode/cultural-info', dialectController.getDialectCulturalInfo);

// 根据地区获取推荐方言
router.get('/region/:region', dialectController.getDialectsByRegion);

// 创建方言学习计划
router.post('/learning-plan', authenticate, dialectController.createDialectLearningPlan);

export default router;