/**
 * 推荐路由
 * 处理健康和生活建议推荐的API路由
 */

const express = require('express');
const router = express.Router();
const RecommendationsController = require('../../controllers/recommendations.controller');

// 创建路由处理函数
module.exports = function(app) {
  // 获取服务实例
  const recommendationsService = app.services.recommendationsService;
  
  // 如果服务实例不存在，记录警告并返回模拟路由
  if (!recommendationsService) {
    app.logger.warn('推荐服务实例不可用，使用模拟响应');
    return mockRecommendationsRoutes(router);
  }
  
  // 创建控制器实例
  const recommendationsController = new RecommendationsController(recommendationsService);
  
  // 获取用户个性化推荐
  router.get('/user/:userId', recommendationsController.getUserRecommendations);
  
  // 获取推荐详情
  router.get('/user/:userId/recommendation/:recommendationId', recommendationsController.getRecommendationDetail);
  
  // 获取每日建议
  router.get('/user/:userId/daily-advice', recommendationsController.getDailyAdvice);
  
  // 提供推荐反馈
  router.post('/user/:userId/recommendation/:recommendationId/feedback', recommendationsController.provideRecommendationFeedback);
  
  return router;
};

/**
 * 创建模拟推荐路由
 * 当推荐服务不可用时使用
 */
function mockRecommendationsRoutes(router) {
  // 获取用户个性化推荐
  router.get('/user/:userId', (req, res) => {
    const { userId } = req.params;
    const { category = 'all', count = 5 } = req.query;
    
    res.json({
      userId,
      recommendations: [
        {
          id: 'mock_rec_1',
          category: 'diet',
          title: '增加蔬菜水果摄入',
          content: '每天摄入至少5份蔬菜水果，提高膳食纤维和微量元素摄入。',
          priority: 'high',
          difficulty: 'easy',
          timeRequired: '每天',
          benefits: ['提高免疫力', '改善消化系统健康'],
          createdAt: new Date().toISOString()
        },
        {
          id: 'mock_rec_2',
          category: 'exercise',
          title: '每天进行有氧运动',
          content: '每天进行30分钟中等强度有氧运动，如快走、慢跑或骑车。',
          priority: 'medium',
          difficulty: 'moderate',
          timeRequired: '30分钟/天',
          benefits: ['增强心肺功能', '改善代谢健康'],
          createdAt: new Date().toISOString()
        }
      ],
      generatedAt: new Date().toISOString()
    });
  });
  
  // 获取推荐详情
  router.get('/user/:userId/recommendation/:recommendationId', (req, res) => {
    const { userId, recommendationId } = req.params;
    
    res.json({
      id: recommendationId,
      userId: userId,
      category: 'diet',
      title: '增加蔬菜水果摄入',
      content: '每天摄入至少5份蔬菜水果，提高膳食纤维和微量元素摄入。',
      detailedDescription: '蔬菜水果富含多种维生素、矿物质和抗氧化物质，对保持身体健康至关重要。研究表明，每天摄入足够的蔬菜水果可以降低多种慢性疾病的风险。',
      priority: 'high',
      difficulty: 'easy',
      timeRequired: '每天',
      benefits: ['提高免疫力', '改善消化系统健康', '降低慢性疾病风险'],
      steps: [
        { step: 1, title: '了解每日需求', description: '了解成人每日需要摄入的蔬菜水果量和种类。' },
        { step: 2, title: '制定饮食计划', description: '规划每日三餐和零食中如何纳入蔬菜水果。' },
        { step: 3, title: '购买新鲜食材', description: '定期购买多种新鲜蔬菜和水果，保证多样性。' }
      ],
      resources: [
        { title: '健康饮食指南', type: '指南', url: 'https://www.example.com/healthy-eating' },
        { title: '季节性蔬果选购', type: '文章', url: 'https://www.example.com/seasonal-produce' }
      ],
      createdAt: new Date().toISOString()
    });
  });
  
  // 获取每日建议
  router.get('/user/:userId/daily-advice', (req, res) => {
    const { userId } = req.params;
    const today = new Date();
    
    res.json({
      userId: userId,
      date: today.toISOString().split('T')[0],
      weatherTip: '今天天气晴朗，适合户外活动，记得防晒。',
      seasonalTip: '春季气温多变，注意适时增减衣物，预防感冒。',
      dietTip: '今天可以多食用深色蔬菜，富含抗氧化物质，有助提高免疫力。',
      exerciseTip: '今天适合进行一些户外活动，接触大自然，放松心情。',
      mindfulnessTip: '记得今天抽出10分钟时间冥想或深呼吸，保持内心平静。',
      tcmTip: '按摩太阳穴和风池穴，可缓解眼疲劳和头痛。',
      quote: '健康不是一切，但没有健康就没有一切。'
    });
  });
  
  // 提供推荐反馈
  router.post('/user/:userId/recommendation/:recommendationId/feedback', (req, res) => {
    const { userId, recommendationId } = req.params;
    
    res.json({
      success: true,
      message: '反馈已记录',
      userId: userId,
      recommendationId: recommendationId,
      timestamp: new Date().toISOString()
    });
  });
  
  return router;
} 