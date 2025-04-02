import express from 'express';
import { authenticate } from '../middleware/auth';
import { checkRole } from '../middleware/auth';
import * as dialectController from '../../services/dialect/dialect.controller';

const router = express.Router();

/**
 * @route GET /api/v1/dialects
 * @desc 获取方言列表
 * @access Public
 */
router.get('/', dialectController.getAllDialects);

/**
 * @route GET /api/v1/dialects/by-region
 * @desc 按地区分组获取方言列表
 * @access Public
 */
router.get('/by-region', dialectController.getDialectsByRegion);

/**
 * @route GET /api/v1/dialects/:code
 * @desc 获取方言详情
 * @access Public
 */
router.get('/:code', dialectController.getDialectByCode);

/**
 * @route POST /api/v1/dialects
 * @desc 创建方言
 * @access Private (Admin)
 */
router.post('/', authenticate, checkRole(['admin']), dialectController.createDialect);

/**
 * @route PUT /api/v1/dialects/:code
 * @desc 更新方言
 * @access Private (Admin)
 */
router.put('/:code', authenticate, checkRole(['admin']), dialectController.updateDialect);

/**
 * @route DELETE /api/v1/dialects/:code
 * @desc 删除方言
 * @access Private (Admin)
 */
router.delete('/:code', authenticate, checkRole(['admin']), dialectController.deleteDialect);

/**
 * @route POST /api/v1/dialects/detect
 * @desc 检测音频中的方言
 * @access Public
 */
router.post('/detect', dialectController.detectDialect);

/**
 * @route POST /api/v1/dialects/translate
 * @desc 转换方言到标准普通话
 * @access Public
 */
router.post('/translate', dialectController.translateDialectToStandard);

/**
 * @route POST /api/v1/dialects/initialize
 * @desc 初始化默认方言数据
 * @access Private (Admin)
 */
router.post('/initialize', authenticate, checkRole(['admin']), dialectController.initializeDefaultDialects);

export default router; 