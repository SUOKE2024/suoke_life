/**
 * 小克服务 - 方言相关路由
 */

import { Router } from 'express';
import * as dialectController from '../controllers/dialect.controller';
import { authenticate } from '../middlewares/auth.middleware';
import { upload } from '../middlewares/upload.middleware';

const router = Router();

/**
 * @route GET /api/dialects
 * @desc 获取支持的方言列表
 * @access Public
 */
router.get('/', dialectController.getAllSupportedDialects);

/**
 * @route POST /api/dialects/detect
 * @desc 检测音频中的方言
 * @access Public
 */
router.post('/detect', upload.single('audio'), dialectController.detectDialect);

/**
 * @route POST /api/dialects/translate
 * @desc 将方言音频翻译为标准普通话
 * @access Public
 */
router.post('/translate', upload.single('audio'), dialectController.translateDialect);

/**
 * @route GET /api/dialects/stats
 * @desc 获取方言统计信息
 * @access Public
 */
router.get('/stats', dialectController.getDialectStats);

/**
 * @route GET /api/dialects/user/:userId/progress
 * @desc 获取用户的方言学习进度
 * @access Private
 */
router.get('/user/:userId/progress', authenticate, dialectController.getUserDialectProgress);

export default router;