/**
 * 推荐服务控制器
 */
const { recommendationService } = require('../services');
const { asyncHandler } = require('../utils/async-handler');
const logger = require('../utils/logger');

/**
 * 获取用户推荐内容
 */
const getRecommendedContent = asyncHandler(async (req, res) => {
  const { userId } = req.params;
  const { 
    limit = 10, 
    includeHistory = false,
    domains,
    types
  } = req.query;
  
  // 验证用户ID是否匹配当前认证用户
  if (req.user.id !== userId && !req.user.isAdmin) {
    return res.status(403).json({
      success: false,
      message: '没有权限获取此用户的推荐内容'
    });
  }
  
  // 格式化过滤参数
  const options = {
    limit: parseInt(limit, 10),
    includeHistory: includeHistory === 'true',
    domainFilter: domains ? domains.split(',') : [],
    typeFilter: types ? types.split(',') : []
  };
  
  // 获取推荐内容
  const recommendedContent = await recommendationService.getRecommendedContent(userId, options);
  
  res.json({
    success: true,
    data: recommendedContent
  });
});

/**
 * 获取基于AI的推荐内容
 */
const getLLMRecommendedContent = asyncHandler(async (req, res) => {
  const { userId } = req.params;
  const { limit = 5 } = req.query;
  
  // 验证用户ID是否匹配当前认证用户
  if (req.user.id !== userId && !req.user.isAdmin) {
    return res.status(403).json({
      success: false,
      message: '没有权限获取此用户的AI推荐内容'
    });
  }
  
  // 获取AI推荐内容
  const recommendedContent = await recommendationService.getLLMRecommendedContent(userId, { 
    limit: parseInt(limit, 10) 
  });
  
  res.json({
    success: true,
    data: recommendedContent
  });
});

/**
 * 记录推荐反馈
 */
const recordRecommendationFeedback = asyncHandler(async (req, res) => {
  const { userId } = req.params;
  const { contentId, feedbackType } = req.body;
  
  // 验证用户ID是否匹配当前认证用户
  if (req.user.id !== userId && !req.user.isAdmin) {
    return res.status(403).json({
      success: false,
      message: '没有权限提交此用户的反馈'
    });
  }
  
  // 验证请求参数
  if (!contentId || !feedbackType) {
    return res.status(400).json({
      success: false,
      message: '缺少必要参数: contentId和feedbackType'
    });
  }
  
  // 验证feedbackType是否有效
  const validFeedbackTypes = ['clicked', 'liked', 'disliked', 'ignored'];
  if (!validFeedbackTypes.includes(feedbackType)) {
    return res.status(400).json({
      success: false,
      message: `反馈类型无效，有效类型为: ${validFeedbackTypes.join(', ')}`
    });
  }
  
  // 记录反馈
  const result = await recommendationService.recordRecommendationFeedback(userId, contentId, feedbackType);
  
  res.json({
    success: true,
    data: { recorded: result }
  });
});

module.exports = {
  getRecommendedContent,
  getLLMRecommendedContent,
  recordRecommendationFeedback
};