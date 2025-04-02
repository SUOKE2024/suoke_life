/**
 * 推荐服务
 * 处理健康和生活建议推荐的业务逻辑
 */

const axios = require('axios');
const { createError } = require('../utils/error-handler');
const logger = require('../utils/logger');

class RecommendationsService {
  constructor(config, integrations = {}) {
    this.config = config;
    this.integrations = integrations;
    this.mockData = true; // 在实际数据接入前使用模拟数据
    
    logger.info('推荐服务初始化完成');
  }

  /**
   * 获取用户个性化推荐
   * @param {string} userId - 用户ID
   * @param {object} options - 选项
   * @param {string} options.category - 推荐类别
   * @param {number} options.count - 推荐数量
   * @returns {Promise<Array>} 推荐列表
   */
  async getUserRecommendations(userId, options = {}) {
    const { category = 'all', count = 5 } = options;
    
    // 验证用户ID
    if (!userId || userId.length < 3) {
      throw createError('invalid_user_id', '无效的用户ID', 400);
    }
    
    try {
      // 获取用户数据
      let userData = null;
      
      // 尝试从健康服务获取用户数据
      if (this.integrations?.health_service) {
        try {
          const healthClient = this.integrations.health_service.client;
          const response = await healthClient.get(`/users/${userId}/profile`);
          
          if (response.status === 200) {
            userData = response.data;
          }
        } catch (error) {
          logger.error(`获取用户数据失败: ${error.message}`);
          // 不抛出错误，继续使用模拟数据
        }
      }
      
      // 生成推荐
      let recommendations = [];
      
      if (this.integrations?.recommendation_engine?.available) {
        try {
          // 调用推荐引擎生成个性化推荐
          const engineResponse = await this.integrations.recommendation_engine.generateRecommendations({
            userId,
            userProfile: userData,
            category,
            count
          });
          
          if (engineResponse && engineResponse.recommendations) {
            recommendations = engineResponse.recommendations;
          }
        } catch (error) {
          logger.error(`生成推荐失败: ${error.message}`);
          // 不抛出错误，使用模拟数据
        }
      }
      
      // 如果没有获取到推荐，使用模拟数据
      if (recommendations.length === 0 || this.mockData) {
        const mockRecs = this._getMockRecommendations(userId, userData);
        
        // 根据类别过滤
        if (category !== 'all') {
          recommendations = mockRecs
            .filter(rec => rec.category === category)
            .slice(0, count);
        } else {
          // 从每个类别中选择一些推荐
          const categories = ['diet', 'exercise', 'sleep', 'stress'];
          let remaining = count;
          let categoryIndex = 0;
          
          while (remaining > 0 && categoryIndex < categories.length) {
            const currentCategory = categories[categoryIndex];
            const categoryRecs = mockRecs.filter(rec => rec.category === currentCategory);
            
            // 从当前类别中取出一部分
            const takeCount = Math.min(Math.ceil(remaining / (categories.length - categoryIndex)), categoryRecs.length);
            
            recommendations = recommendations.concat(categoryRecs.slice(0, takeCount));
            remaining -= takeCount;
            categoryIndex++;
          }
        }
      }
      
      return {
        userId,
        recommendations,
        generatedAt: new Date().toISOString()
      };
      
    } catch (error) {
      if (error.isCustom) {
        throw error;
      }
      
      logger.error(`处理推荐请求失败: ${error.message}`);
      throw createError('recommendation_generation_failed', '生成推荐失败', 500);
    }
  }
  
  /**
   * 获取单个推荐详情
   * @param {string} userId - 用户ID
   * @param {string} recommendationId - 推荐ID
   * @returns {Promise<Object>} 推荐详情
   */
  async getRecommendationDetail(userId, recommendationId) {
    // 验证用户ID和推荐ID
    if (!userId || userId.length < 3) {
      throw createError('invalid_user_id', '无效的用户ID', 400);
    }
    
    if (!recommendationId) {
      throw createError('invalid_recommendation_id', '无效的推荐ID', 400);
    }
    
    try {
      // 尝试从数据库或API获取推荐详情
      let recommendationDetail = null;
      
      // 如果有数据库连接，可以从数据库查询
      if (this.integrations?.database) {
        try {
          // 实现查询数据库获取推荐详情的逻辑
          // ...
        } catch (dbError) {
          logger.error(`从数据库获取推荐详情失败: ${dbError.message}`);
        }
      }
      
      // 如果没有从数据库获取到详情，使用模拟数据
      if (!recommendationDetail || this.mockData) {
        recommendationDetail = this._getMockRecommendationDetail(userId, recommendationId);
      }
      
      if (!recommendationDetail) {
        throw createError('recommendation_not_found', '找不到指定的推荐', 404);
      }
      
      return recommendationDetail;
    } catch (error) {
      if (error.isCustom) {
        throw error;
      }
      
      logger.error(`获取推荐详情失败: ${error.message}`);
      throw createError('recommendation_detail_error', '获取推荐详情失败', 500);
    }
  }
  
  /**
   * 获取每日建议
   * @param {string} userId - 用户ID
   * @returns {Promise<Object>} 每日建议
   */
  async getDailyAdvice(userId) {
    try {
      // 验证用户ID
      if (!userId || userId.length < 3) {
        throw createError('invalid_user_id', '无效的用户ID', 400);
      }
      
      const today = new Date();
      
      // 在实际应用中，可以结合用户数据和时令季节等生成每日建议
      // 此处使用模拟数据
      return this._getMockDailyAdvice(today);
    } catch (error) {
      if (error.isCustom) {
        throw error;
      }
      
      logger.error(`获取每日建议失败: ${error.message}`);
      throw createError('daily_advice_error', '获取每日建议失败', 500);
    }
  }
  
  /**
   * 反馈推荐结果
   * @param {string} userId - 用户ID
   * @param {string} recommendationId - 推荐ID
   * @param {object} feedback - 反馈数据
   * @returns {Promise<Object>} 反馈结果
   */
  async provideRecommendationFeedback(userId, recommendationId, feedback) {
    try {
      // 验证参数
      if (!userId || userId.length < 3) {
        throw createError('invalid_user_id', '无效的用户ID', 400);
      }
      
      if (!recommendationId) {
        throw createError('invalid_recommendation_id', '无效的推荐ID', 400);
      }
      
      if (!feedback || typeof feedback !== 'object') {
        throw createError('invalid_feedback', '无效的反馈数据', 400);
      }
      
      // 记录反馈
      logger.info(`用户 ${userId} 对推荐 ${recommendationId} 提供反馈`, { feedback });
      
      // 在实际应用中，应该将反馈存储到数据库并用于改进推荐系统
      
      return {
        success: true,
        message: '反馈已记录',
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      if (error.isCustom) {
        throw error;
      }
      
      logger.error(`处理推荐反馈失败: ${error.message}`);
      throw createError('feedback_processing_failed', '处理反馈失败', 500);
    }
  }
  
  /**
   * 获取模拟推荐数据
   * @private
   */
  _getMockRecommendations(userId, userData = null) {
    // 生成一些模拟推荐数据
    const recommendations = [
      {
        id: 'rec_diet_1',
        category: 'diet',
        title: '增加五谷杂粮摄入',
        content: '每天添加一份杂粮到饮食中，如小米、黑米、燕麦等，增加膳食纤维摄入。',
        priority: 'high',
        difficulty: 'easy',
        timeRequired: '15分钟/天',
        benefits: ['改善消化', '稳定血糖', '增加能量'],
        createdAt: new Date().toISOString()
      },
      {
        id: 'rec_diet_2',
        category: 'diet',
        title: '减少加工食品摄入',
        content: '避免或减少食用高度加工的食品，如即食面、薯片、饼干等，改用新鲜食材自己烹饪。',
        priority: 'medium',
        difficulty: 'moderate',
        timeRequired: '持续习惯养成',
        benefits: ['减少摄入有害添加剂', '控制体重', '改善总体健康'],
        createdAt: new Date().toISOString()
      },
      {
        id: 'rec_exercise_1',
        category: 'exercise',
        title: '每天快走30分钟',
        content: '每天安排30分钟快走，保持中等强度，步频约100-120步/分钟。',
        priority: 'high',
        difficulty: 'easy',
        timeRequired: '30分钟/天',
        benefits: ['增强心肺功能', '提高代谢', '改善心情'],
        createdAt: new Date().toISOString()
      },
      {
        id: 'rec_exercise_2',
        category: 'exercise',
        title: '加入力量训练',
        content: '每周进行2-3次力量训练，包括俯卧撑、深蹲和平板支撑等简单动作。',
        priority: 'medium',
        difficulty: 'moderate',
        timeRequired: '20-30分钟/次',
        benefits: ['增强肌肉力量', '改善姿势', '提高基础代谢率'],
        createdAt: new Date().toISOString()
      },
      {
        id: 'rec_sleep_1',
        category: 'sleep',
        title: '建立睡前放松习惯',
        content: '睡前1小时关闭电子设备，进行阅读、冥想或洗个温水澡来放松身心。',
        priority: 'high',
        difficulty: 'moderate',
        timeRequired: '1小时/晚',
        benefits: ['改善睡眠质量', '减少入睡时间', '增加深度睡眠'],
        createdAt: new Date().toISOString()
      },
      {
        id: 'rec_sleep_2',
        category: 'sleep',
        title: '规律作息时间',
        content: '每天固定时间入睡和起床，包括周末，保持生物钟稳定。',
        priority: 'high',
        difficulty: 'challenging',
        timeRequired: '持续坚持',
        benefits: ['提高睡眠质量', '增强精力', '改善情绪稳定性'],
        createdAt: new Date().toISOString()
      },
      {
        id: 'rec_stress_1',
        category: 'stress',
        title: '每日冥想练习',
        content: '每天安排10-15分钟的冥想练习，关注呼吸，清空思绪。',
        priority: 'medium',
        difficulty: 'moderate',
        timeRequired: '10-15分钟/天',
        benefits: ['减轻压力', '提高专注力', '增强情绪调控能力'],
        createdAt: new Date().toISOString()
      },
      {
        id: 'rec_stress_2',
        category: 'stress',
        title: '减少信息干扰',
        content: '每天设定特定时间查看新闻和社交媒体，避免频繁刷新和信息过载。',
        priority: 'medium',
        difficulty: 'challenging',
        timeRequired: '持续练习',
        benefits: ['减少焦虑', '提高工作效率', '改善注意力'],
        createdAt: new Date().toISOString()
      }
    ];
    
    return recommendations;
  }
  
  /**
   * 获取模拟推荐详情
   * @private
   */
  _getMockRecommendationDetail(userId, recommendationId) {
    // 基础推荐列表
    const recommendations = this._getMockRecommendations(userId);
    
    // 查找匹配的推荐
    const baseRec = recommendations.find(rec => rec.id === recommendationId);
    
    if (!baseRec) {
      return null;
    }
    
    // 扩展详细信息
    const detailedRec = {
      ...baseRec,
      userId: userId,
      detailedDescription: this._getDetailedDescription(baseRec.category, baseRec.title),
      steps: this._getImplementationSteps(baseRec.category, baseRec.id),
      resources: this._getRelatedResources(baseRec.category)
    };
    
    return detailedRec;
  }
  
  /**
   * 获取模拟的每日建议
   * @private
   */
  _getMockDailyAdvice(date) {
    const dayOfWeek = date.getDay();
    const month = date.getMonth();
    
    // 根据星期和季节提供不同的建议
    const seasonalTips = [
      '春季饮食宜温补阳气，可多食用温性食物如韭菜、香菜等。',
      '夏季注意防暑降温，饮食宜清淡，多食用苦瓜、绿豆等清热食物。',
      '秋季气候干燥，注意润肺养阴，可食用梨、百合等滋阴润燥的食物。',
      '冬季注重养阳护阴，可适当食用羊肉、韭菜等温补食物，增强抵抗力。'
    ][Math.floor(month / 3)];
    
    const dailyExerciseTips = [
      '今天可以进行15-30分钟的慢跑或健走，促进血液循环。',
      '建议今天进行一些伸展运动，舒展筋骨，缓解疲劳。',
      '今天适合进行瑜伽或太极等柔和运动，平衡身心。',
      '可以尝试HIIT高强度间歇训练，短时间内提高心肺功能。',
      '今天适合进行一些户外活动，接触大自然，放松心情。',
      '建议今天做一些力量训练，如俯卧撑、深蹲等，增强肌肉力量。',
      '今天可以进行舞蹈或有氧操等节奏性运动，提高心肺功能。'
    ][dayOfWeek];
    
    return {
      date: date.toISOString().split('T')[0],
      weatherTip: '今天天气晴朗，适合户外活动，记得防晒。',
      seasonalTip: seasonalTips,
      dietTip: '今天可以多食用深色蔬菜，富含抗氧化物质，有助提高免疫力。',
      exerciseTip: dailyExerciseTips,
      mindfulnessTip: '记得今天抽出10分钟时间冥想或深呼吸，保持内心平静。',
      tcmTip: '按摩太阳穴和风池穴，可缓解眼疲劳和头痛。',
      quote: '健康不是一切，但没有健康就没有一切。'
    };
  }
  
  /**
   * 获取详细描述
   * @private
   */
  _getDetailedDescription(category, title) {
    const descriptions = {
      diet: {
        '增加五谷杂粮摄入': '五谷杂粮富含膳食纤维、维生素和矿物质，对肠道健康和整体营养平衡非常重要。现代饮食中精制谷物过多，导致膳食纤维摄入不足。通过每天有意识地添加一份杂粮，如小米粥、藜麦饭或燕麦片，可以显著提高膳食质量。中医角度认为，五谷杂粮性平，有健脾养胃之功效。',
        '减少加工食品摄入': '加工食品通常含有高盐、高糖和高脂肪，还添加了各种防腐剂、色素和香料。长期食用可能导致肥胖、代谢综合征和其他慢性病。通过逐步减少加工食品摄入，转而选择新鲜食材自己烹饪，可以更好地控制食物成分，提高饮食质量。中医认为，过多食用加工食品容易导致湿热内生，损伤脾胃功能。'
      },
      exercise: {
        '每天快走30分钟': '快走是一种简单有效的有氧运动，几乎没有任何门槛，适合各年龄段人群。坚持每天快走30分钟可以显著提高心肺功能，促进血液循环，帮助控制体重。研究表明，快走还可以降低心脏病、中风和2型糖尿病的风险。从中医角度看，适度运动可以行气活血，增强体质。',
        '加入力量训练': '力量训练不仅能增强肌肉力量，还能改善身体姿势，预防背痛等问题。更重要的是，肌肉组织比脂肪组织消耗更多能量，增加肌肉量可以提高基础代谢率，帮助维持健康体重。简单的自重训练如俯卧撑、深蹲和平板支撑不需要特殊设备，在家即可完成。中医认为适度的力量训练可强筋健骨，增强人体阳气。'
      },
      sleep: {
        '建立睡前放松习惯': '睡前放松是提高睡眠质量的关键。电子设备发出的蓝光会抑制褪黑素分泌，影响睡眠。通过建立固定的睡前放松习惯，如阅读纸质书、听轻松音乐、冥想或泡温水澡，可以帮助身心放松，更容易入睡。中医认为，安神养血有助于提高睡眠质量，而良好的睡眠习惯是养心安神的基础。',
        '规律作息时间': '人体有内在的生物钟，规律的作息时间可以优化各种生理功能。不规律的睡眠会扰乱生物钟，影响睡眠质量和日间精力。坚持每天同一时间入睡和起床，包括周末，可以培养身体的规律性，提高睡眠效率。中医讲究天人相应，认为作息应当顺应自然规律，早睡早起符合阴阳变化原则。'
      },
      stress: {
        '每日冥想练习': '冥想是一种被广泛研究的减压技术，可以降低压力激素水平，减轻焦虑和抑郁症状。通过每天10-15分钟的正念冥想，关注呼吸，不评判地觉察当下思绪，可以培养平静的心态，提高专注力和情绪管理能力。从中医角度看，冥想可以调和气机，宁心安神。',
        '减少信息干扰': '现代社会的信息过载是导致注意力分散和精神压力的主要原因之一。不断检查手机、社交媒体和新闻会持续激活神经系统的压力反应。通过设定固定时间查看信息，远离电子设备，可以减少认知负担，给大脑必要的休息。中医认为，过度的精神刺激会耗伤心神，导致心火上炎，引起焦虑、失眠等症状。'
      }
    };

    return descriptions[category]?.[title] || 
      '该建议旨在改善您的整体健康状况，根据您的个人情况定制。通过遵循这些指导，您可以逐步建立更健康的生活习惯，提高生活质量。';
  }
  
  /**
   * 获取实施步骤
   * @private
   */
  _getImplementationSteps(category, id) {
    const allSteps = {
      rec_diet_1: [
        { step: 1, title: '了解杂粮种类', description: '了解常见杂粮如小米、黑米、燕麦、藜麦、荞麦等的特性和营养价值。' },
        { step: 2, title: '准备杂粮', description: '购买几种自己喜欢的杂粮，可以混合存放或分开保存。' },
        { step: 3, title: '制定添加计划', description: '计划如何将杂粮融入日常饮食，如早餐吃杂粮粥、午餐混合米饭等。' },
        { step: 4, title: '尝试简单食谱', description: '开始尝试简单的杂粮食谱，如小米粥、燕麦片、杂粮饭等。' },
        { step: 5, title: '逐步增加比例', description: '随着适应程度提高，逐步增加杂粮在饮食中的比例。' }
      ],
      rec_exercise_1: [
        { step: 1, title: '准备合适装备', description: '准备一双合适的运动鞋和舒适的运动服装。' },
        { step: 2, title: '规划行走路线', description: '在家或办公室附近规划几条适合快走的路线，包括平坦路段和小坡。' },
        { step: 3, title: '安排固定时间', description: '在日程表中安排固定的30分钟用于快走，可以是早晨、午休或下班后。' },
        { step: 4, title: '掌握正确姿势', description: '保持挺胸抬头，两臂自然摆动，步幅适中，脚跟先着地然后滚向脚尖。' },
        { step: 5, title: '逐步提高强度', description: '适应基本快走后，可以通过增加速度或选择有坡度的路线来提高强度。' }
      ],
      rec_sleep_1: [
        { step: 1, title: '设定提醒', description: '在睡前1小时设定提醒，提示开始放松准备。' },
        { step: 2, title: '关闭电子设备', description: '关闭或远离手机、电脑、电视等电子设备，减少蓝光摄入。' },
        { step: 3, title: '创建舒适环境', description: '调暗灯光，保持房间安静、凉爽和舒适。' },
        { step: 4, title: '选择放松活动', description: '选择一种放松活动，如阅读、听轻音乐、冥想或洗个温水澡。' },
        { step: 5, title: '养成固定习惯', description: '每晚重复相同的放松活动，让身体形成条件反射，准备入睡。' }
      ]
    };
    
    return allSteps[id] || [
      { step: 1, title: '了解背景', description: '全面了解该建议的背景知识和健康益处。' },
      { step: 2, title: '制定计划', description: '根据个人情况制定具体可行的实施计划。' },
      { step: 3, title: '准备资源', description: '准备需要的资源、工具或环境。' },
      { step: 4, title: '开始实践', description: '按计划开始实践，记录遇到的困难和进展。' },
      { step: 5, title: '坚持调整', description: '坚持执行计划，根据实际情况进行必要调整。' }
    ];
  }
  
  /**
   * 获取相关资源
   * @private
   */
  _getRelatedResources(category) {
    const resources = {
      diet: [
        { title: '《中国居民膳食指南(2022)》', type: '指南', url: 'https://www.example.com/dietary-guidelines' },
        { title: '全谷物与健康', type: '文章', url: 'https://www.example.com/whole-grains' },
        { title: '健康烹饪方法', type: '视频', url: 'https://www.example.com/healthy-cooking' }
      ],
      exercise: [
        { title: '有效步行技巧', type: '文章', url: 'https://www.example.com/walking-techniques' },
        { title: '开始力量训练的指南', type: '指南', url: 'https://www.example.com/strength-training' },
        { title: '居家锻炼系列', type: '视频', url: 'https://www.example.com/home-workouts' }
      ],
      sleep: [
        { title: '改善睡眠质量的科学方法', type: '文章', url: 'https://www.example.com/sleep-science' },
        { title: '睡前放松冥想', type: '音频', url: 'https://www.example.com/sleep-meditation' },
        { title: '睡眠环境优化指南', type: '指南', url: 'https://www.example.com/sleep-environment' }
      ],
      stress: [
        { title: '科学减压技巧', type: '文章', url: 'https://www.example.com/stress-management' },
        { title: '冥想入门指南', type: '指南', url: 'https://www.example.com/meditation-guide' },
        { title: '正念呼吸练习', type: '音频', url: 'https://www.example.com/mindful-breathing' }
      ]
    };
    
    return resources[category] || [
      { title: '健康生活方式指南', type: '指南', url: 'https://www.example.com/healthy-lifestyle' },
      { title: '创建健康习惯的科学', type: '文章', url: 'https://www.example.com/habit-formation' },
      { title: '索克生活健康课堂', type: '视频', url: 'https://www.example.com/suoke-health' }
    ];
  }
}

module.exports = RecommendationsService; 