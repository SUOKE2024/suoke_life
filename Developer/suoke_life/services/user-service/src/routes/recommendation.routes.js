/**
 * 推荐服务路由
 */
const express = require('express');
const { recommendationController } = require('../controllers');
const { authMiddleware } = require('../middlewares');

const router = express.Router();

/**
 * @route   GET /api/users/:userId/recommendations
 * @desc    获取用户推荐内容
 * @access  Private
 * @param   {string} userId - 用户ID
 * @query   {number} limit - 返回结果数量 (默认10)
 * @query   {boolean} includeHistory - 是否包含历史内容 (默认false)
 * @query   {string} domains - 逗号分隔的领域过滤器
 * @query   {string} types - 逗号分隔的内容类型过滤器
 */
router.get(
  '/users/:userId/recommendations',
  authMiddleware,
  recommendationController.getRecommendedContent
);

/**
 * @route   GET /api/users/:userId/ai-recommendations
 * @desc    获取基于AI的推荐内容
 * @access  Private
 * @param   {string} userId - 用户ID
 * @query   {number} limit - 返回结果数量 (默认5)
 */
router.get(
  '/users/:userId/ai-recommendations',
  authMiddleware,
  recommendationController.getLLMRecommendedContent
);

/**
 * @route   POST /api/users/:userId/recommendation-feedback
 * @desc    记录推荐反馈
 * @access  Private
 * @param   {string} userId - 用户ID
 * @body    {string} contentId - 内容ID
 * @body    {string} feedbackType - 反馈类型 (clicked, liked, disliked, ignored)
 */
router.post(
  '/users/:userId/recommendation-feedback',
  authMiddleware,
  recommendationController.recordRecommendationFeedback
);

module.exports = router;