/**
 * 生活方式路由
 * 处理用户生活方式相关的API路由
 */

const express = require('express');
const router = express.Router();
const LifestyleController = require('../../controllers/lifestyle.controller');

// 创建路由处理函数
module.exports = function(app) {
  // 获取服务实例
  const lifestyleService = app.services.lifestyleService;
  
  // 如果服务实例不存在，记录警告并返回模拟路由
  if (!lifestyleService) {
    app.logger.warn('生活方式服务实例不可用，使用模拟响应');
    return mockLifestyleRoutes(router);
  }
  
  // 创建控制器实例
  const lifestyleController = new LifestyleController(lifestyleService);
  
  // 获取用户饮食习惯分析
  router.get('/user/:userId/dietary-habits', lifestyleController.getDietaryHabitsAnalysis);
  
  // 获取生活方式综合分析
  router.get('/user/:userId/analysis', lifestyleController.getLifestyleAnalysis);
  
  // 获取季节性生活调整建议
  router.get('/user/:userId/seasonal-guidance', lifestyleController.getSeasonalLifestyleGuidance);
  
  // 更新用户生活方式设置
  router.put('/user/:userId/settings', lifestyleController.updateLifestyleSettings);
  
  return router;
};

/**
 * 创建模拟生活方式路由
 * 当生活方式服务不可用时使用
 */
function mockLifestyleRoutes(router) {
  // 获取用户饮食习惯分析
  router.get('/user/:userId/dietary-habits', (req, res) => {
    const { userId } = req.params;
    const { period = 'month' } = req.query;
    
    res.json({
      userId,
      analysisDate: new Date().toISOString(),
      dietaryProfile: {
        mainDietType: '混合型饮食',
        preferences: ['蔬菜水果', '五谷杂粮', '家禽肉类'],
        avoidances: ['油炸食品', '过于辛辣食物'],
        regularMeals: 2.5,
        nutritionBalance: 0.75,
        mealTiming: {
          breakfast: '07:30 - 08:30',
          lunch: '12:00 - 13:00',
          dinner: '18:30 - 19:30'
        }
      },
      analysis: {
        strengths: [
          '饮食中包含丰富的蔬菜水果',
          '很少食用油炸和过度加工食品',
          '三餐时间较为规律'
        ],
        improvements: [
          '早餐营养较为单一，可增加蛋白质来源',
          '水分摄入不足，应增加饮水量',
          '晚餐时间偏晚，建议提前至18:00前完成'
        ],
        tcmPerspective: '根据中医理论，您的饮食状态偏于"脾胃湿热"，建议增加具有清热利湿功效的食物，如冬瓜、绿豆等。',
        seasonalCompatibility: 0.82
      },
      recommendations: [
        {
          type: 'diet',
          title: '增加早餐蛋白质摄入',
          description: '在早餐中添加鸡蛋、豆浆或坚果，提高蛋白质含量。',
          reasoning: '充足的早餐蛋白质有助于稳定血糖，提供持久能量。'
        },
        {
          type: 'habit',
          title: '调整晚餐时间',
          description: '将晚餐时间提前至18:00前，有助于消化和睡眠。',
          reasoning: '中医认为脾胃消化功能在申时(15:00-17:00)最强，此时进食更有利于消化吸收。'
        }
      ]
    });
  });
  
  // 获取生活方式综合分析
  router.get('/user/:userId/analysis', (req, res) => {
    const { userId } = req.params;
    
    res.json({
      userId,
      timestamp: new Date().toISOString(),
      overallScore: 78,
      categories: {
        diet: {
          score: 82,
          strengths: [
            '饮食多样化',
            '摄入充足蔬果',
            '规律进餐'
          ],
          weaknesses: [
            '晚餐过晚',
            '加工食品摄入较多'
          ]
        },
        activity: {
          score: 65,
          strengths: [
            '每周进行中等强度运动',
            '日常活动水平适中'
          ],
          weaknesses: [
            '久坐时间过长',
            '缺乏力量训练'
          ]
        },
        sleep: {
          score: 75,
          strengths: [
            '睡眠时间充足',
            '睡眠环境良好'
          ],
          weaknesses: [
            '入睡困难',
            '睡前使用电子设备'
          ]
        }
      },
      recommendations: [
        {
          category: 'diet',
          priority: 'high',
          title: '调整晚餐时间',
          description: '将晚餐时间提前至18:00前，并减少晚餐摄入量。'
        },
        {
          category: 'activity',
          priority: 'medium',
          title: '增加日常活动',
          description: '每工作1小时，起身活动5分钟，减少久坐时间。'
        }
      ]
    });
  });
  
  // 获取季节性生活调整建议
  router.get('/user/:userId/seasonal-guidance', (req, res) => {
    const { userId } = req.params;
    const today = new Date();
    const month = today.getMonth();
    const season = ['春', '夏', '秋', '冬'][Math.floor(month / 3) % 4];
    
    res.json({
      userId,
      season,
      generatedAt: new Date().toISOString(),
      guidance: {
        overview: '春季是万物复苏的季节，阳气开始生发，此时应顺应自然，重在"生发"。',
        dietaryGuidance: {
          principles: '春季饮食宜温补阳气，可多食用温性食物如韭菜、香菜等。',
          recommended: ['韭菜', '香椿', '春笋', '菠菜', '豆芽', '草莓'],
          avoid: ['辛辣刺激', '油腻煎炸', '过咸过酸']
        },
        activityGuidance: {
          principles: '春季适合做一些舒展筋骨、舒缓身心的运动，如散步、太极等。',
          recommended: ['早晨慢跑', '太极拳', '五禽戏', '散步'],
          timeOfDay: '清晨是春季锻炼的最佳时段，此时阳气初生，空气清新。'
        },
        healthReminders: [
          '春季气温变化大，应注意适时增减衣物',
          '过敏体质者应注意防护，减少接触过敏原',
          '春困现象常见，可适当午休，但不宜过长'
        ]
      }
    });
  });
  
  // 更新用户生活方式设置
  router.put('/user/:userId/settings', (req, res) => {
    const { userId } = req.params;
    
    res.json({
      success: true,
      message: '设置已保存',
      userId: userId,
      timestamp: new Date().toISOString()
    });
  });
  
  return router;
} 