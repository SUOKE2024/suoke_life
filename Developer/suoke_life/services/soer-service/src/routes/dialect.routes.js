/**
 * 索儿服务 - 方言相关路由
 */

const express = require('express');
const router = express.Router();
const dialectController = require('../controllers/dialect.controller');
const { authenticate } = require('../middlewares/auth.middleware');
const { upload } = require('../middlewares/upload.middleware');

/**
 * @route GET /api/dialects/child-friendly
 * @desc 获取适合儿童的方言列表
 * @access Public
 */
router.get('/child-friendly', dialectController.getChildFriendlyDialects);

/**
 * @route POST /api/dialects/detect-for-children
 * @desc 儿童版方言检测
 * @access Public
 */
router.post('/detect-for-children', upload.single('audio'), dialectController.detectDialectForChildren);

/**
 * @route GET /api/dialects/:dialectCode/games
 * @desc 获取方言学习游戏
 * @access Public
 */
router.get('/:dialectCode/games', dialectController.getDialectLearningGames);

/**
 * @route GET /api/dialects/:dialectCode/games/:ageGroup
 * @desc 获取特定年龄组的方言学习游戏
 * @access Public
 */
router.get('/:dialectCode/games/:ageGroup', dialectController.getDialectLearningGames);

/**
 * @route POST /api/dialects/adventure
 * @desc 创建儿童方言探险任务
 * @access Private
 */
router.post('/adventure', authenticate, dialectController.createDialectAdventure);

/**
 * @route GET /api/dialects/adventure/:adventureId
 * @desc 获取探险任务详情
 * @access Private
 */
router.get('/adventure/:adventureId', authenticate, dialectController.getDialectAdventure);

/**
 * @route PUT /api/dialects/adventure/:adventureId/progress
 * @desc 更新探险任务进度
 * @access Private
 */
router.put('/adventure/:adventureId/progress', authenticate, dialectController.updateAdventureProgress);

module.exports = router;