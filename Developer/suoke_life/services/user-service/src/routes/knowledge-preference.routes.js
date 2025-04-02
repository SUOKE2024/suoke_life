/**
 * 知识偏好路由
 */
const express = require('express');
const { authMiddleware, validationMiddleware } = require('@suoke/shared').middlewares;
const knowledgePreferenceController = require('../controllers/knowledge-preference.controller');
const router = express.Router();

// 所有路由都需要认证
router.use(authMiddleware.isAuthenticated);

/**
 * @route GET /api/v1/users/:userId/knowledge-preferences
 * @desc 获取用户知识偏好
 * @access 私有
 */
router.get('/:userId/knowledge-preferences', knowledgePreferenceController.getUserKnowledgePreferences);

/**
 * @route PUT /api/v1/users/:userId/knowledge-preferences
 * @desc 更新用户知识偏好
 * @access 私有
 */
router.put('/:userId/knowledge-preferences', knowledgePreferenceController.updateUserKnowledgePreferences);

/**
 * @route GET /api/v1/users/:userId/interested-domains
 * @desc 获取用户感兴趣的知识领域
 * @access 私有
 */
router.get('/:userId/interested-domains', knowledgePreferenceController.getUserInterestedDomains);

/**
 * @route GET /api/v1/users/:userId/view-history
 * @desc 获取用户知识内容访问历史
 * @access 私有
 */
router.get('/:userId/view-history', knowledgePreferenceController.getUserViewHistory);

/**
 * @route POST /api/v1/users/view-history
 * @desc 记录用户知识内容访问
 * @access 私有
 */
router.post('/view-history', knowledgePreferenceController.recordContentView);

/**
 * @route GET /api/v1/users/:userId/recommended-content
 * @desc 获取推荐给用户的知识内容
 * @access 私有
 */
router.get('/:userId/recommended-content', knowledgePreferenceController.getRecommendedContent);

/**
 * @route GET /api/v1/users/:userId/favorites
 * @desc 获取用户收藏的知识内容
 * @access 私有
 */
router.get('/:userId/favorites', knowledgePreferenceController.getUserFavorites);

/**
 * @route POST /api/v1/users/favorites
 * @desc 添加知识内容到用户收藏
 * @access 私有
 */
router.post('/favorites', knowledgePreferenceController.addToFavorites);

/**
 * @route DELETE /api/v1/users/favorites/:contentId
 * @desc 从用户收藏中移除知识内容
 * @access 私有
 */
router.delete('/favorites/:contentId', knowledgePreferenceController.removeFromFavorites);

/**
 * @route GET /api/v1/users/:userId/knowledge-graph-interactions
 * @desc 获取用户知识图谱交互历史
 * @access 私有
 */
router.get('/:userId/knowledge-graph-interactions', knowledgePreferenceController.getKnowledgeGraphInteractions);

module.exports = router;