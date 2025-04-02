'use strict';

/**
 * 健康洞察路由
 * 处理健康数据分析和洞察生成的API接口
 */
module.exports = async function (fastify, opts) {
  // 获取用户健康洞察
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
          timeframe: { type: 'string', enum: ['day', 'week', 'month', 'year', 'all'] },
          type: { type: 'string', enum: ['health', 'lifestyle', 'nutrition', 'all'] }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            userId: { type: 'string' },
            insights: { 
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  id: { type: 'string' },
                  type: { type: 'string' },
                  title: { type: 'string' },
                  description: { type: 'string' },
                  confidence: { type: 'number' },
                  severity: { type: 'string', enum: ['low', 'medium', 'high'] },
                  createdAt: { type: 'string', format: 'date-time' },
                  dataPoints: { type: 'array', items: { type: 'object' } },
                  recommendations: {
                    type: 'array',
                    items: {
                      type: 'object',
                      properties: {
                        id: { type: 'string' },
                        content: { type: 'string' },
                        priority: { type: 'string', enum: ['low', 'medium', 'high'] }
                      }
                    }
                  }
                }
              }
            },
            summary: {
              type: 'object',
              properties: {
                total: { type: 'integer' },
                byType: { type: 'object' },
                bySeverity: { type: 'object' }
              }
            },
            generatedAt: { type: 'string', format: 'date-time' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId } = request.params;
    const { timeframe = 'week', type = 'all' } = request.query;
    
    // 验证用户ID
    if (!userId || userId.length < 3) {
      return reply.code(400).send({
        error: 'invalid_user_id',
        message: '无效的用户ID'
      });
    }
    
    try {
      // 获取健康数据
      let healthData = null;
      if (fastify.integrations?.health_service) {
        try {
          const healthClient = fastify.integrations.health_service.client;
          const response = await healthClient.get(`/users/${userId}/health-data`, {
            params: { timeframe }
          });
          
          if (response.status === 200) {
            healthData = response.data;
          }
        } catch (error) {
          fastify.log.error(`获取健康数据失败: ${error.message}`);
          // 不抛出错误，继续执行
        }
      }
      
      // 如果没有健康数据，返回空结果
      if (!healthData) {
        return {
          userId,
          insights: [],
          summary: {
            total: 0,
            byType: {},
            bySeverity: {}
          },
          generatedAt: new Date().toISOString()
        };
      }
      
      // 生成健康洞察
      let insights = [];
      
      if (
        fastify.agentService.models.health_analyzer?.loaded && 
        healthData
      ) {
        try {
          // 这里应该实现使用健康分析器模型生成洞察
          // 以下是模拟实现
          
          // 生成一些模拟的健康洞察
          insights = generateMockInsights(userId, healthData, type);
          
        } catch (error) {
          fastify.log.error(`生成健康洞察失败: ${error.message}`);
          // 不抛出错误，返回空结果
        }
      }
      
      // 生成摘要统计
      const summary = {
        total: insights.length,
        byType: {},
        bySeverity: {}
      };
      
      // 按类型统计
      for (const insight of insights) {
        if (!summary.byType[insight.type]) {
          summary.byType[insight.type] = 0;
        }
        summary.byType[insight.type]++;
        
        if (!summary.bySeverity[insight.severity]) {
          summary.bySeverity[insight.severity] = 0;
        }
        summary.bySeverity[insight.severity]++;
      }
      
      return {
        userId,
        insights,
        summary,
        generatedAt: new Date().toISOString()
      };
      
    } catch (error) {
      fastify.log.error(`处理健康洞察请求失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'insight_generation_failed',
        message: '生成健康洞察失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });

  // 获取单个健康洞察详情
  fastify.get('/user/:userId/insight/:insightId', {
    schema: {
      params: {
        type: 'object',
        required: ['userId', 'insightId'],
        properties: {
          userId: { type: 'string' },
          insightId: { type: 'string' }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            userId: { type: 'string' },
            type: { type: 'string' },
            title: { type: 'string' },
            description: { type: 'string' },
            confidence: { type: 'number' },
            severity: { type: 'string', enum: ['low', 'medium', 'high'] },
            createdAt: { type: 'string', format: 'date-time' },
            dataPoints: { 
              type: 'array', 
              items: { 
                type: 'object',
                properties: {
                  name: { type: 'string' },
                  value: { type: 'string' },
                  unit: { type: 'string' },
                  timestamp: { type: 'string', format: 'date-time' },
                  source: { type: 'string' }
                }
              } 
            },
            analysis: { type: 'string' },
            recommendations: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  id: { type: 'string' },
                  content: { type: 'string' },
                  priority: { type: 'string', enum: ['low', 'medium', 'high'] },
                  reasoning: { type: 'string' }
                }
              }
            },
            relatedContent: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  title: { type: 'string' },
                  type: { type: 'string' },
                  url: { type: 'string' }
                }
              }
            }
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
    const { userId, insightId } = request.params;
    
    // 验证参数
    if (!userId || userId.length < 3) {
      return reply.code(400).send({
        error: 'invalid_user_id',
        message: '无效的用户ID'
      });
    }
    
    if (!insightId) {
      return reply.code(400).send({
        error: 'invalid_insight_id',
        message: '无效的洞察ID'
      });
    }
    
    try {
      // 这里应该实现从数据库或缓存中获取特定洞察
      // 以下是模拟实现
      
      // 生成一个模拟的洞察详情
      const insight = generateMockInsightDetail(userId, insightId);
      
      if (!insight) {
        return reply.code(404).send({
          error: 'insight_not_found',
          message: '未找到指定的健康洞察'
        });
      }
      
      return insight;
      
    } catch (error) {
      fastify.log.error(`获取健康洞察详情失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'insight_retrieval_failed',
        message: '获取健康洞察详情失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });

  // 生成季节性健康洞察
  fastify.get('/seasonal', {
    schema: {
      querystring: {
        type: 'object',
        properties: {
          season: { type: 'string', enum: ['spring', 'summer', 'autumn', 'winter'] },
          solarTerm: { type: 'string' }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            season: { type: 'string' },
            solarTerm: { type: 'string' },
            currentDate: { type: 'string', format: 'date' },
            insights: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  title: { type: 'string' },
                  content: { type: 'string' },
                  category: { type: 'string' },
                  recommendations: {
                    type: 'array',
                    items: {
                      type: 'object',
                      properties: {
                        title: { type: 'string' },
                        content: { type: 'string' }
                      }
                    }
                  }
                }
              }
            },
            generatedAt: { type: 'string', format: 'date-time' }
          }
        }
      }
    }
  }, async (request, reply) => {
    // 获取季节和节气信息
    let { season, solarTerm } = request.query;
    
    // 如果未指定，根据当前日期确定
    if (!season || !solarTerm) {
      const currentSeasonInfo = getCurrentSeasonInfo();
      season = season || currentSeasonInfo.season;
      solarTerm = solarTerm || currentSeasonInfo.solarTerm;
    }
    
    try {
      // 从知识库中获取季节性健康知识
      let seasonalKnowledge = null;
      if (fastify.integrations?.rag_service) {
        try {
          const ragClient = fastify.integrations.rag_service.client;
          const response = await ragClient.get('/knowledge/seasonal', {
            params: { season, solarTerm }
          });
          
          if (response.status === 200) {
            seasonalKnowledge = response.data;
          }
        } catch (error) {
          fastify.log.error(`获取季节性知识失败: ${error.message}`);
          // 不抛出错误，继续使用模拟数据
        }
      }
      
      // 如果没有获取到季节性知识，使用模拟数据
      if (!seasonalKnowledge) {
        seasonalKnowledge = getMockSeasonalKnowledge(season, solarTerm);
      }
      
      // 构建响应
      return {
        season,
        solarTerm,
        currentDate: new Date().toISOString().split('T')[0],
        insights: seasonalKnowledge.insights || [],
        generatedAt: new Date().toISOString()
      };
      
    } catch (error) {
      fastify.log.error(`生成季节性健康洞察失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'seasonal_insight_generation_failed',
        message: '生成季节性健康洞察失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });
};

// 生成模拟健康洞察
function generateMockInsights(userId, healthData, type) {
  const insights = [
    {
      id: 'ins_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
      type: 'health',
      title: '睡眠质量偏低',
      description: '过去一周的睡眠数据显示，您的深度睡眠时间低于健康标准。',
      confidence: 0.85,
      severity: 'medium',
      createdAt: new Date().toISOString(),
      dataPoints: [
        { name: '平均睡眠时间', value: '6.2', unit: '小时' },
        { name: '深度睡眠比例', value: '15', unit: '%' }
      ],
      recommendations: [
        {
          id: 'rec_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
          content: '尝试在睡前1小时关闭电子设备，减少蓝光暴露',
          priority: 'high'
        },
        {
          id: 'rec_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
          content: '保持规律的睡眠时间，每晚尽量在同一时间入睡',
          priority: 'medium'
        }
      ]
    },
    {
      id: 'ins_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
      type: 'lifestyle',
      title: '久坐行为增加',
      description: '数据显示您每天久坐时间超过9小时，这可能增加多种健康风险。',
      confidence: 0.9,
      severity: 'medium',
      createdAt: new Date().toISOString(),
      dataPoints: [
        { name: '平均久坐时间', value: '9.5', unit: '小时/天' },
        { name: '活动提醒响应率', value: '35', unit: '%' }
      ],
      recommendations: [
        {
          id: 'rec_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
          content: '每小时起身活动5分钟，可以使用计时器提醒',
          priority: 'high'
        },
        {
          id: 'rec_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
          content: '考虑使用站立式办公桌，每天至少站立工作2小时',
          priority: 'medium'
        }
      ]
    },
    {
      id: 'ins_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
      type: 'nutrition',
      title: '蛋白质摄入不足',
      description: '您的饮食记录显示蛋白质摄入低于推荐水平，这可能影响肌肉恢复和免疫功能。',
      confidence: 0.8,
      severity: 'low',
      createdAt: new Date().toISOString(),
      dataPoints: [
        { name: '平均蛋白质摄入', value: '45', unit: '克/天' },
        { name: '推荐摄入量', value: '60-75', unit: '克/天' }
      ],
      recommendations: [
        {
          id: 'rec_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
          content: '增加优质蛋白质来源，如鱼类、鸡蛋、豆制品的摄入',
          priority: 'medium'
        },
        {
          id: 'rec_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
          content: '考虑在早餐中添加高蛋白食物，如希腊酸奶或蛋类',
          priority: 'low'
        }
      ]
    }
  ];
  
  // 根据类型过滤
  if (type !== 'all') {
    return insights.filter(insight => insight.type === type);
  }
  
  return insights;
}

// 生成模拟洞察详情
function generateMockInsightDetail(userId, insightId) {
  // 在实际应用中，应该从数据库中获取
  return {
    id: insightId,
    userId: userId,
    type: 'health',
    title: '睡眠质量偏低',
    description: '过去一周的睡眠数据显示，您的深度睡眠时间低于健康标准。',
    confidence: 0.85,
    severity: 'medium',
    createdAt: new Date().toISOString(),
    dataPoints: [
      { 
        name: '平均睡眠时间', 
        value: '6.2', 
        unit: '小时',
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        source: '智能手环'
      },
      { 
        name: '深度睡眠比例', 
        value: '15', 
        unit: '%',
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        source: '智能手环'
      },
      { 
        name: '入睡时间', 
        value: '23:45', 
        unit: '',
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        source: '智能手环'
      },
      { 
        name: '睡眠中断次数', 
        value: '3', 
        unit: '次',
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        source: '智能手环'
      }
    ],
    analysis: '良好的睡眠质量对身体恢复和认知功能至关重要。您的睡眠数据显示深度睡眠比例仅为15%，低于18-25%的健康标准。深度睡眠阶段对免疫系统恢复、记忆巩固和细胞修复尤为重要。您的睡眠中断次数较多，可能是导致深度睡眠不足的原因之一。',
    recommendations: [
      {
        id: 'rec_001',
        content: '尝试在睡前1小时关闭电子设备，减少蓝光暴露',
        priority: 'high',
        reasoning: '蓝光会抑制褪黑素的分泌，褪黑素是调节睡眠的关键激素。减少睡前的蓝光暴露有助于自然入睡。'
      },
      {
        id: 'rec_002',
        content: '保持规律的睡眠时间，每晚尽量在同一时间入睡',
        priority: 'medium',
        reasoning: '规律的睡眠-觉醒周期有助于优化生物钟，提高睡眠质量和深度睡眠比例。'
      },
      {
        id: 'rec_003',
        content: '睡前进行舒缓活动，如冥想、深呼吸或轻度拉伸',
        priority: 'medium',
        reasoning: '放松活动可以降低压力激素皮质醇的水平，帮助身体进入适合睡眠的状态。'
      },
      {
        id: 'rec_004',
        content: '确保睡眠环境舒适，温度控制在20-22°C，保持安静和黑暗',
        priority: 'low',
        reasoning: '适宜的睡眠环境可以减少夜间醒来的次数，延长深度睡眠时间。'
      }
    ],
    relatedContent: [
      {
        title: '如何科学提升睡眠质量',
        type: 'article',
        url: '/content/articles/sleep-quality-improvement'
      },
      {
        title: '深度睡眠的重要性',
        type: 'video',
        url: '/content/videos/deep-sleep-importance'
      },
      {
        title: '入睡困难?试试这5个放松技巧',
        type: 'audio',
        url: '/content/audios/relaxation-techniques'
      }
    ]
  };
}

// 获取当前季节和节气信息
function getCurrentSeasonInfo() {
  // 这里应该实现根据当前日期判断季节和节气
  // 以下是简化实现
  const now = new Date();
  const month = now.getMonth() + 1; // 1-12
  
  // 简化的季节判断
  let season;
  if (month >= 3 && month <= 5) {
    season = 'spring';
  } else if (month >= 6 && month <= 8) {
    season = 'summer';
  } else if (month >= 9 && month <= 11) {
    season = 'autumn';
  } else {
    season = 'winter';
  }
  
  // 简化的节气判断（实际应该使用农历或更准确的算法）
  const solarTerms = [
    '立春', '雨水', '惊蛰', '春分', '清明', '谷雨',
    '立夏', '小满', '芒种', '夏至', '小暑', '大暑',
    '立秋', '处暑', '白露', '秋分', '寒露', '霜降',
    '立冬', '小雪', '大雪', '冬至', '小寒', '大寒'
  ];
  
  // 简化判断，实际应该根据精确日期确定
  const termIndex = Math.floor((month - 1) * 2 + (now.getDate() > 15 ? 1 : 0)) % 24;
  const solarTerm = solarTerms[termIndex];
  
  return { season, solarTerm };
}

// 获取模拟季节性知识
function getMockSeasonalKnowledge(season, solarTerm) {
  // 根据季节返回不同的建议
  const seasonalInsights = {
    spring: {
      insights: [
        {
          title: '春季养生要点',
          content: '春季阳气生发，是调养肝脏的最佳时期。宜疏肝理气，饮食宜清淡，多食用具有疏肝解郁作用的食物，如春笋、芹菜、荠菜等。',
          category: 'nutrition',
          recommendations: [
            { title: '春季饮食', content: '建议多食用新鲜蔬菜，适量食用辛甘发散的食物，如葱、姜、蒜等，帮助疏通阳气。' },
            { title: '春季活动', content: '可进行舒缓的伸展运动，如太极、瑜伽等，帮助疏通经络，调和气血。' }
          ]
        },
        {
          title: '春季常见健康问题',
          content: '春季气温多变，容易诱发呼吸道疾病和过敏反应。同时，春季情绪易波动，要注意调节情绪，防止肝气郁结。',
          category: 'health',
          recommendations: [
            { title: '增强免疫力', content: '保持良好作息，适当增加户外活动时间，增强自身免疫力。' },
            { title: '情绪调节', content: '可以尝试冥想、深呼吸等放松方法，保持心情愉悦，避免情绪波动过大。' }
          ]
        }
      ]
    },
    summer: {
      insights: [
        {
          title: '夏季养生要点',
          content: '夏季气温高，阳气外发，易耗伤阴精。养生应以清暑益气、健脾祛湿为主，注意防暑降温，保护心脏。',
          category: 'nutrition',
          recommendations: [
            { title: '夏季饮食', content: '饮食宜清淡，可多食用具有清热解暑功效的食物，如绿豆、西瓜、苦瓜等。' },
            { title: '防暑降温', content: '避免长时间在烈日下活动，多补充水分，可适量饮用含有电解质的饮料。' }
          ]
        },
        {
          title: '夏季常见健康问题',
          content: '夏季常见的健康问题包括中暑、食物中毒、肠胃不适等。同时，夏季也是心脑血管疾病的高发期。',
          category: 'health',
          recommendations: [
            { title: '预防中暑', content: '外出携带遮阳工具，穿着宽松透气的衣物，避免在最热的时段外出活动。' },
            { title: '保护心脑血管', content: '避免剧烈运动，保持情绪稳定，早晚可进行适量的有氧运动。' }
          ]
        }
      ]
    },
    autumn: {
      insights: [
        {
          title: '秋季养生要点',
          content: '秋季气候干燥，易伤肺阴。养生重在养收敛之气，润燥护肺，防风寒，调畅情志。',
          category: 'nutrition',
          recommendations: [
            { title: '秋季饮食', content: '可多食用滋阴润燥的食物，如百合、银耳、梨、蜂蜜等，少食辛辣刺激食物。' },
            { title: '秋季保湿', content: '注意皮肤和呼吸道的保湿，可使用加湿器，多饮水，避免皮肤干燥和呼吸道不适。' }
          ]
        },
        {
          title: '秋季常见健康问题',
          content: '秋季常见呼吸道疾病、皮肤干燥问题，以及情绪波动、抑郁等心理问题。',
          category: 'health',
          recommendations: [
            { title: '呼吸道保护', content: '保持室内空气清新，勤开窗通风，外出时戴口罩防护，预防呼吸道感染。' },
            { title: '心理调适', content: '可通过户外活动、欣赏美景等方式调节情绪，避免秋季抑郁。' }
          ]
        }
      ]
    },
    winter: {
      insights: [
        {
          title: '冬季养生要点',
          content: '冬季气候寒冷，养生重在"藏"，保护阳气，温补肾阳，防寒保暖，调养脾胃。',
          category: 'nutrition',
          recommendations: [
            { title: '冬季饮食', content: '可适当食用温热性食物，如羊肉、牛肉、大枣、姜等，增强阳气，但不宜过于油腻。' },
            { title: '冬季运动', content: '坚持适量运动，可选择室内温和的活动，如太极、游泳、瑜伽等，避免大量出汗。' }
          ]
        },
        {
          title: '冬季常见健康问题',
          content: '冬季是心脑血管疾病、呼吸道疾病和关节炎等疾病的高发期，同时也要注意预防冻伤。',
          category: 'health',
          recommendations: [
            { title: '保暖防寒', content: '注意保暖，尤其是头部、颈部、腰部和脚部，避免受凉感冒。' },
            { title: '心脑血管保护', content: '避免情绪激动和剧烈运动，保持血压平稳，适当进行有氧运动。' }
          ]
        }
      ]
    }
  };
  
  // 返回对应季节的建议
  return seasonalInsights[season] || { insights: [] };
}