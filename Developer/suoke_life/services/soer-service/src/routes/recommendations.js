'use strict';

/**
 * 推荐路由
 * 处理健康和生活建议推荐的API接口
 */
module.exports = async function (fastify, opts) {
  // 获取个性化推荐
  fastify.get('/user/:userId', {
    schema: {
      params: {
        type: 'object',
        required: ['userId'],
        properties: {
          userId: { type: 'string' }
        }
      },
      querystring: {
        type: 'object',
        properties: {
          category: { type: 'string', enum: ['diet', 'exercise', 'sleep', 'stress', 'all'] },
          count: { type: 'integer', minimum: 1, maximum: 20 }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            userId: { type: 'string' },
            recommendations: { 
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  id: { type: 'string' },
                  category: { type: 'string' },
                  title: { type: 'string' },
                  content: { type: 'string' },
                  priority: { type: 'string', enum: ['low', 'medium', 'high'] },
                  difficulty: { type: 'string', enum: ['easy', 'moderate', 'challenging'] },
                  timeRequired: { type: 'string' },
                  benefits: { type: 'array', items: { type: 'string' } },
                  createdAt: { type: 'string', format: 'date-time' }
                }
              }
            },
            generatedAt: { type: 'string', format: 'date-time' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId } = request.params;
    const { category = 'all', count = 5 } = request.query;
    
    // 验证用户ID
    if (!userId || userId.length < 3) {
      return reply.code(400).send({
        error: 'invalid_user_id',
        message: '无效的用户ID'
      });
    }
    
    try {
      // 获取用户数据
      let userData = null;
      
      // 尝试从健康服务获取用户数据
      if (fastify.integrations?.health_service) {
        try {
          const healthClient = fastify.integrations.health_service.client;
          const response = await healthClient.get(`/users/${userId}/profile`);
          
          if (response.status === 200) {
            userData = response.data;
          }
        } catch (error) {
          fastify.log.error(`获取用户数据失败: ${error.message}`);
          // 不抛出错误，继续使用模拟数据
        }
      }
      
      // 生成推荐
      let recommendations = [];
      
      if (
        fastify.agentService.models.recommendation_engine?.loaded
      ) {
        try {
          // 这里应该实现使用推荐引擎模型生成推荐
          // 以下是模拟实现
          
          // 获取模拟推荐
          const allRecommendations = getMockRecommendations(userId, userData);
          
          // 根据类别过滤
          if (category !== 'all') {
            recommendations = allRecommendations
              .filter(rec => rec.category === category)
              .slice(0, count);
          } else {
            // 从每个类别中选择一些推荐
            const categories = ['diet', 'exercise', 'sleep', 'stress'];
            let remaining = count;
            let categoryIndex = 0;
            
            while (remaining > 0 && categoryIndex < categories.length) {
              const currentCategory = categories[categoryIndex];
              const categoryRecs = allRecommendations.filter(rec => rec.category === currentCategory);
              
              // 从当前类别中取出一部分
              const takeCount = Math.min(Math.ceil(remaining / (categories.length - categoryIndex)), categoryRecs.length);
              
              recommendations = recommendations.concat(categoryRecs.slice(0, takeCount));
              remaining -= takeCount;
              categoryIndex++;
            }
          }
          
        } catch (error) {
          fastify.log.error(`生成推荐失败: ${error.message}`);
          // 不抛出错误，使用模拟数据
        }
      }
      
      // 如果没有获取到推荐，使用模拟数据
      if (recommendations.length === 0) {
        const mockRecs = getMockRecommendations(userId);
        recommendations = mockRecs.slice(0, count);
      }
      
      return {
        userId,
        recommendations,
        generatedAt: new Date().toISOString()
      };
      
    } catch (error) {
      fastify.log.error(`处理推荐请求失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'recommendation_generation_failed',
        message: '生成推荐失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });

  // 获取单个推荐详情
  fastify.get('/user/:userId/recommendation/:recommendationId', {
    schema: {
      params: {
        type: 'object',
        required: ['userId', 'recommendationId'],
        properties: {
          userId: { type: 'string' },
          recommendationId: { type: 'string' }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            userId: { type: 'string' },
            category: { type: 'string' },
            title: { type: 'string' },
            content: { type: 'string' },
            detailedDescription: { type: 'string' },
            priority: { type: 'string', enum: ['low', 'medium', 'high'] },
            difficulty: { type: 'string', enum: ['easy', 'moderate', 'challenging'] },
            timeRequired: { type: 'string' },
            benefits: { type: 'array', items: { type: 'string' } },
            steps: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  step: { type: 'integer' },
                  title: { type: 'string' },
                  description: { type: 'string' }
                }
              }
            },
            resources: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  title: { type: 'string' },
                  type: { type: 'string' },
                  url: { type: 'string' }
                }
              }
            },
            createdAt: { type: 'string', format: 'date-time' }
          }
        },
        404: {
          type: 'object',
          properties: {
            error: { type: 'string' },
            message: { type: 'string' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId, recommendationId } = request.params;
    
    // 验证参数
    if (!userId || userId.length < 3) {
      return reply.code(400).send({
        error: 'invalid_user_id',
        message: '无效的用户ID'
      });
    }
    
    if (!recommendationId) {
      return reply.code(400).send({
        error: 'invalid_recommendation_id',
        message: '无效的推荐ID'
      });
    }
    
    try {
      // 这里应该实现从数据库中获取特定推荐
      // 以下是模拟实现
      
      // 获取模拟推荐详情
      const recommendation = getMockRecommendationDetail(userId, recommendationId);
      
      if (!recommendation) {
        return reply.code(404).send({
          error: 'recommendation_not_found',
          message: '未找到指定的推荐'
        });
      }
      
      return recommendation;
      
    } catch (error) {
      fastify.log.error(`获取推荐详情失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'recommendation_retrieval_failed',
        message: '获取推荐详情失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });

  // 标记推荐为已完成或已拒绝
  fastify.post('/user/:userId/recommendation/:recommendationId/status', {
    schema: {
      params: {
        type: 'object',
        required: ['userId', 'recommendationId'],
        properties: {
          userId: { type: 'string' },
          recommendationId: { type: 'string' }
        }
      },
      body: {
        type: 'object',
        required: ['status'],
        properties: {
          status: { type: 'string', enum: ['accepted', 'completed', 'rejected', 'snoozed'] },
          reason: { type: 'string' },
          feedback: { type: 'string' },
          completedAt: { type: 'string', format: 'date-time' }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            success: { type: 'boolean' },
            message: { type: 'string' },
            updatedAt: { type: 'string', format: 'date-time' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId, recommendationId } = request.params;
    const { status, reason, feedback, completedAt } = request.body;
    
    // 验证参数
    if (!userId || userId.length < 3) {
      return reply.code(400).send({
        error: 'invalid_user_id',
        message: '无效的用户ID'
      });
    }
    
    if (!recommendationId) {
      return reply.code(400).send({
        error: 'invalid_recommendation_id',
        message: '无效的推荐ID'
      });
    }
    
    try {
      // 在实际实现中，应该将状态更新到数据库
      // 这里仅模拟操作
      
      // 记录反馈
      fastify.log.info({
        userId,
        recommendationId,
        status,
        reason,
        hasFeedback: !!feedback,
        completedAt
      }, '推荐状态更新');
      
      // 尝试将状态发送到健康服务
      if (fastify.integrations?.health_service) {
        try {
          const healthClient = fastify.integrations.health_service.client;
          await healthClient.post(`/users/${userId}/recommendations/${recommendationId}/status`, {
            status,
            reason,
            feedback,
            completedAt: completedAt || new Date().toISOString()
          });
        } catch (error) {
          fastify.log.error(`更新推荐状态失败: ${error.message}`);
          // 不抛出错误，继续处理
        }
      }
      
      return {
        success: true,
        message: `推荐已标记为${getStatusText(status)}`,
        updatedAt: new Date().toISOString()
      };
      
    } catch (error) {
      fastify.log.error(`更新推荐状态失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'recommendation_update_failed',
        message: '更新推荐状态失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });

  // 获取今日健康建议
  fastify.get('/daily', {
    schema: {
      querystring: {
        type: 'object',
        properties: {
          date: { type: 'string', format: 'date' }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            date: { type: 'string', format: 'date' },
            quote: {
              type: 'object',
              properties: {
                text: { type: 'string' },
                author: { type: 'string' }
              }
            },
            tips: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  category: { type: 'string' },
                  content: { type: 'string' }
                }
              }
            },
            seasonalAdvice: { type: 'string' },
            generatedAt: { type: 'string', format: 'date-time' }
          }
        }
      }
    }
  }, async (request, reply) => {
    // 获取日期
    let date = request.query.date;
    if (!date) {
      // 使用当前日期
      date = new Date().toISOString().split('T')[0];
    }
    
    try {
      // 从知识库中获取每日建议
      let dailyAdvice = null;
      if (fastify.integrations?.rag_service) {
        try {
          const ragClient = fastify.integrations.rag_service.client;
          const response = await ragClient.get('/content/daily', {
            params: { date }
          });
          
          if (response.status === 200) {
            dailyAdvice = response.data;
          }
        } catch (error) {
          fastify.log.error(`获取每日建议失败: ${error.message}`);
          // 不抛出错误，使用模拟数据
        }
      }
      
      // 如果没有获取到每日建议，使用模拟数据
      if (!dailyAdvice) {
        dailyAdvice = getMockDailyAdvice(date);
      }
      
      return {
        date,
        ...dailyAdvice,
        generatedAt: new Date().toISOString()
      };
      
    } catch (error) {
      fastify.log.error(`生成每日建议失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'daily_advice_generation_failed',
        message: '生成每日建议失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });
};

// 获取状态文本
function getStatusText(status) {
  const statusMap = {
    accepted: '已接受',
    completed: '已完成',
    rejected: '已拒绝',
    snoozed: '已推迟'
  };
  
  return statusMap[status] || status;
}

// 生成模拟推荐
function getMockRecommendations(userId, userData = null) {
  return [
    {
      id: 'rec_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
      category: 'diet',
      title: '增加蔬果摄入量',
      content: '每天摄入至少5份不同颜色的蔬菜和水果，提高膳食纤维和抗氧化物质的摄入。',
      priority: 'high',
      difficulty: 'easy',
      timeRequired: '每日持续',
      benefits: ['改善消化', '增强免疫力', '提供维生素和矿物质'],
      createdAt: new Date().toISOString()
    },
    {
      id: 'rec_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
      category: 'diet',
      title: '减少加工食品摄入',
      content: '限制高度加工食品和含糖饮料的摄入，优先选择天然、未加工的食材。',
      priority: 'medium',
      difficulty: 'moderate',
      timeRequired: '每日持续',
      benefits: ['控制体重', '降低慢性疾病风险', '稳定血糖'],
      createdAt: new Date().toISOString()
    },
    {
      id: 'rec_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
      category: 'exercise',
      title: '每日步行30分钟',
      content: '每天保持30分钟中等强度的步行，可以分散在一天中进行。',
      priority: 'high',
      difficulty: 'easy',
      timeRequired: '每日30分钟',
      benefits: ['增强心肺功能', '改善心情', '控制体重'],
      createdAt: new Date().toISOString()
    },
    {
      id: 'rec_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
      category: 'exercise',
      title: '增加力量训练',
      content: '每周进行2-3次力量训练，锻炼主要肌肉群，每次20-30分钟。',
      priority: 'medium',
      difficulty: 'moderate',
      timeRequired: '每周2-3次',
      benefits: ['增强肌肉力量', '促进新陈代谢', '改善体态'],
      createdAt: new Date().toISOString()
    },
    {
      id: 'rec_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
      category: 'sleep',
      title: '建立睡前放松仪式',
      content: '睡前1小时进行放松活动，如阅读、冥想或舒缓的拉伸，避免电子设备。',
      priority: 'high',
      difficulty: 'moderate',
      timeRequired: '每晚20-30分钟',
      benefits: ['促进睡眠', '降低压力', '改善睡眠质量'],
      createdAt: new Date().toISOString()
    },
    {
      id: 'rec_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
      category: 'sleep',
      title: '保持规律的睡眠时间',
      content: '每天保持相同的睡眠和起床时间，包括周末，建立健康的生物钟。',
      priority: 'high',
      difficulty: 'moderate',
      timeRequired: '持续进行',
      benefits: ['改善睡眠质量', '增加深度睡眠', '日间精力充沛'],
      createdAt: new Date().toISOString()
    },
    {
      id: 'rec_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
      category: 'stress',
      title: '每日冥想练习',
      content: '每天进行10-15分钟的冥想练习，专注于呼吸和当下感受。',
      priority: 'medium',
      difficulty: 'moderate',
      timeRequired: '每日10-15分钟',
      benefits: ['降低压力水平', '改善专注力', '增强情绪稳定性'],
      createdAt: new Date().toISOString()
    },
    {
      id: 'rec_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
      category: 'stress',
      title: '定期社交活动',
      content: '每周安排1-2次与朋友或家人的社交活动，加强社会联系。',
      priority: 'medium',
      difficulty: 'easy',
      timeRequired: '每周1-2次',
      benefits: ['减轻孤独感', '增强幸福感', '建立社会支持网络'],
      createdAt: new Date().toISOString()
    }
  ];
}

// 生成模拟推荐详情
function getMockRecommendationDetail(userId, recommendationId) {
  // 在实际应用中，应该从数据库中获取
  return {
    id: recommendationId,
    userId: userId,
    category: 'exercise',
    title: '每日步行30分钟',
    content: '每天保持30分钟中等强度的步行，可以分散在一天中进行。',
    detailedDescription: '步行是最简单、最经济的有氧运动方式，对提高心肺功能、控制体重和改善情绪有显著效果。研究表明，每天30分钟中等强度的步行可以降低心脏病和中风的风险，同时帮助控制血压和血糖水平。',
    priority: 'high',
    difficulty: 'easy',
    timeRequired: '每日30分钟',
    benefits: [
      '增强心肺功能',
      '改善心情',
      '控制体重',
      '降低心脏病风险',
      '改善睡眠质量',
      '减轻关节疼痛'
    ],
    steps: [
      {
        step: 1,
        title: '准备合适的鞋子',
        description: '选择舒适、支撑性好的运动鞋，以减少受伤风险。'
      },
      {
        step: 2,
        title: '制定步行计划',
        description: '可以安排在早上起床后、午休时间或晚饭后进行，也可以分散为每次10分钟，一天三次。'
      },
      {
        step: 3,
        title: '保持正确姿势',
        description: '头部挺直，肩膀放松，腹部微收，手臂自然摆动，脚跟先着地，然后是脚掌和脚趾。'
      },
      {
        step: 4,
        title: '控制步行强度',
        description: '步行强度应达到中等水平，可以正常交谈但略有气喘。初学者可以从较慢的速度开始，逐渐增加。'
      },
      {
        step: 5,
        title: '养成习惯',
        description: '将步行融入日常生活，如步行上班、购物或与朋友见面，逐渐形成习惯。'
      }
    ],
    resources: [
      {
        title: '如何开始健康的步行习惯',
        type: 'article',
        url: '/content/articles/start-walking-habit'
      },
      {
        title: '步行的健康益处',
        type: 'video',
        url: '/content/videos/walking-benefits'
      },
      {
        title: '步行训练计划应用',
        type: 'app',
        url: '/apps/walking-tracker'
      }
    ],
    createdAt: new Date().toISOString()
  };
}

// 生成模拟每日建议
function getMockDailyAdvice(date) {
  return {
    quote: {
      text: '生命在于运动，健康来自平衡。',
      author: '中医养生谚语'
    },
    tips: [
      {
        category: 'nutrition',
        content: '今天可以尝试增加一份绿叶蔬菜，富含叶酸和抗氧化物质，有助于改善细胞健康。'
      },
      {
        category: 'exercise',
        content: '工作间隙起身活动5分钟，简单的伸展或原地踏步都可以激活身体，提升工作效率。'
      },
      {
        category: 'mindfulness',
        content: '今天请尝试"三次深呼吸法"：当感到压力时，停下来，做三次深呼吸，感受当下的感觉。'
      }
    ],
    seasonalAdvice: '现在正值立夏时节，气温逐渐升高，注意防暑降温，饮食宜清淡，可适量食用绿豆汤、苦瓜等清热解暑的食物。'
  };
}