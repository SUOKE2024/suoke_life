'use strict';

/**
 * 生活方式路由模块
 * 处理用户生活方式管理、饮食习惯分析和相关建议
 */
module.exports = async function(fastify, opts) {
  const { knowledgeIntegrationService } = fastify.services;
  
  // 获取用户饮食习惯分析
  fastify.get('/dietary-habits/:userId', {
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
          period: { type: 'string', enum: ['week', 'month', 'quarter', 'year'], default: 'month' }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            userId: { type: 'string' },
            analysisDate: { type: 'string', format: 'date-time' },
            dietaryProfile: {
              type: 'object',
              properties: {
                mainDietType: { type: 'string' },
                preferences: {
                  type: 'array',
                  items: { type: 'string' }
                },
                avoidances: {
                  type: 'array',
                  items: { type: 'string' }
                },
                regularMeals: { type: 'number' },
                nutritionBalance: { type: 'number' },
                mealTiming: {
                  type: 'object',
                  properties: {
                    breakfast: { type: 'string' },
                    lunch: { type: 'string' },
                    dinner: { type: 'string' }
                  }
                }
              }
            },
            analysis: {
              type: 'object',
              properties: {
                strengths: {
                  type: 'array',
                  items: { type: 'string' }
                },
                improvements: {
                  type: 'array',
                  items: { type: 'string' }
                },
                tcmPerspective: { type: 'string' },
                seasonalCompatibility: { type: 'number' }
              }
            },
            recommendations: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  type: { type: 'string' },
                  title: { type: 'string' },
                  description: { type: 'string' },
                  reasoning: { type: 'string' },
                  knowledgeLinks: {
                    type: 'array',
                    items: { type: 'string' }
                  }
                }
              }
            }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId } = request.params;
    const { period = 'month' } = request.query;
    
    try {
      // 从知识图谱和数据库获取用户的饮食习惯数据
      // 实际项目中，这里应该调用相关服务获取真实数据
      // 此处使用模拟数据进行演示
      
      // 整合知识图谱的相关健康知识
      let knowledgeLinks = [];
      try {
        // 尝试从知识集成服务获取相关知识节点
        if (knowledgeIntegrationService) {
          const knowledgeResponse = await knowledgeIntegrationService.findRelatedKnowledge({
            concepts: ['饮食习惯', '营养均衡', '三餐规律'],
            limit: 5
          });
          
          if (knowledgeResponse && knowledgeResponse.nodes) {
            knowledgeLinks = knowledgeResponse.nodes.map(node => node.id);
          }
        }
      } catch (knowledgeError) {
        fastify.log.warn(`获取知识图谱数据失败: ${knowledgeError.message}`);
        // 继续处理，不影响主流程
      }
      
      const dietaryData = getDietaryHabitsData(userId, period, knowledgeLinks);
      
      return dietaryData;
    } catch (error) {
      fastify.log.error(`获取用户饮食习惯分析失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'dietary_habits_analysis_failed',
        message: '获取用户饮食习惯分析失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });
  
  // 获取生活方式综合分析
  fastify.get('/analysis/:userId', {
    schema: {
      params: {
        type: 'object',
        required: ['userId'],
        properties: {
          userId: { type: 'string' }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            userId: { type: 'string' },
            timestamp: { type: 'string', format: 'date-time' },
            overallScore: { type: 'number' },
            categories: {
              type: 'object',
              properties: {
                diet: {
                  type: 'object',
                  properties: {
                    score: { type: 'number' },
                    strengths: {
                      type: 'array',
                      items: { type: 'string' }
                    },
                    weaknesses: {
                      type: 'array',
                      items: { type: 'string' }
                    }
                  }
                },
                activity: {
                  type: 'object',
                  properties: {
                    score: { type: 'number' },
                    strengths: {
                      type: 'array',
                      items: { type: 'string' }
                    },
                    weaknesses: {
                      type: 'array',
                      items: { type: 'string' }
                    }
                  }
                },
                sleep: {
                  type: 'object',
                  properties: {
                    score: { type: 'number' },
                    strengths: {
                      type: 'array',
                      items: { type: 'string' }
                    },
                    weaknesses: {
                      type: 'array',
                      items: { type: 'string' }
                    }
                  }
                },
                stress: {
                  type: 'object',
                  properties: {
                    score: { type: 'number' },
                    strengths: {
                      type: 'array',
                      items: { type: 'string' }
                    },
                    weaknesses: {
                      type: 'array',
                      items: { type: 'string' }
                    }
                  }
                }
              }
            },
            constitution: { type: 'string' },
            seasonalAdvice: { type: 'string' },
            recommendations: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  category: { type: 'string' },
                  title: { type: 'string' },
                  description: { type: 'string' },
                  priority: { type: 'number' }
                }
              }
            }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId } = request.params;
    
    try {
      // 获取综合生活方式分析
      // 实际项目中，这里应调用相关服务获取真实数据
      
      // 尝试从知识图谱获取相关建议
      let recommendations = [];
      try {
        if (knowledgeIntegrationService) {
          const knowledgeResponse = await knowledgeIntegrationService.getLifestyleRecommendations({
            userId,
            categories: ['diet', 'activity', 'sleep', 'stress']
          });
          
          if (knowledgeResponse && knowledgeResponse.recommendations) {
            recommendations = knowledgeResponse.recommendations;
          }
        }
      } catch (knowledgeError) {
        fastify.log.warn(`获取生活方式建议失败: ${knowledgeError.message}`);
        // 使用默认建议
        recommendations = getDefaultRecommendations();
      }
      
      const analysisData = getLifestyleAnalysisData(userId, recommendations);
      
      return analysisData;
    } catch (error) {
      fastify.log.error(`获取用户生活方式分析失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'lifestyle_analysis_failed',
        message: '获取用户生活方式分析失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });
  
  // 添加或更新饮食偏好
  fastify.post('/dietary-preferences/:userId', {
    schema: {
      params: {
        type: 'object',
        required: ['userId'],
        properties: {
          userId: { type: 'string' }
        }
      },
      body: {
        type: 'object',
        properties: {
          dietType: { type: 'string' },
          preferences: {
            type: 'array',
            items: { type: 'string' }
          },
          avoidances: {
            type: 'array',
            items: { type: 'string' }
          },
          allergies: {
            type: 'array',
            items: { type: 'string' }
          },
          mealTimes: {
            type: 'object',
            properties: {
              breakfast: { type: 'string' },
              lunch: { type: 'string' },
              dinner: { type: 'string' }
            }
          }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            success: { type: 'boolean' },
            message: { type: 'string' },
            updated: {
              type: 'array',
              items: { type: 'string' }
            }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId } = request.params;
    const preferences = request.body;
    
    try {
      // 实际项目中，这里应保存用户的饮食偏好
      // 并可能触发知识图谱的更新
      
      // 模拟保存结果
      const updated = [];
      for (const key in preferences) {
        if (preferences[key]) {
          updated.push(key);
        }
      }
      
      return {
        success: true,
        message: '饮食偏好更新成功',
        updated
      };
    } catch (error) {
      fastify.log.error(`更新用户饮食偏好失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'update_preferences_failed',
        message: '更新用户饮食偏好失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });
  
  // 获取节气饮食建议
  fastify.get('/seasonal-diet', {
    schema: {
      querystring: {
        type: 'object',
        properties: {
          date: { type: 'string', format: 'date' },
          constitution: { type: 'string' }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            currentSolarTerm: { type: 'string' },
            nextSolarTerm: { type: 'string' },
            daysToNext: { type: 'number' },
            season: { type: 'string' },
            seasonalFoods: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  name: { type: 'string' },
                  category: { type: 'string' },
                  benefits: {
                    type: 'array',
                    items: { type: 'string' }
                  }
                }
              }
            },
            dietaryPrinciples: {
              type: 'array',
              items: { type: 'string' }
            },
            recommendations: {
              type: 'object',
              properties: {
                general: {
                  type: 'array',
                  items: { type: 'string' }
                },
                constitutionSpecific: {
                  type: 'array',
                  items: { type: 'string' }
                }
              }
            },
            recipes: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  name: { type: 'string' },
                  description: { type: 'string' },
                  ingredients: {
                    type: 'array',
                    items: { type: 'string' }
                  },
                  benefits: { type: 'string' }
                }
              }
            }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { date = new Date().toISOString().split('T')[0], constitution = '平和质' } = request.query;
    
    try {
      // 从知识图谱获取节气信息和推荐
      let seasonalData;
      
      try {
        if (knowledgeIntegrationService) {
          const knowledgeResponse = await knowledgeIntegrationService.getSeasonalDietRecommendations({
            date,
            constitution
          });
          
          if (knowledgeResponse) {
            seasonalData = knowledgeResponse;
          }
        }
      } catch (knowledgeError) {
        fastify.log.warn(`获取节气饮食知识失败: ${knowledgeError.message}`);
        // 使用备用数据
      }
      
      // 如果知识图谱无数据，使用模拟数据
      if (!seasonalData) {
        seasonalData = getSeasonalDietData(date, constitution);
      }
      
      return seasonalData;
    } catch (error) {
      fastify.log.error(`获取节气饮食建议失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'seasonal_diet_fetch_failed',
        message: '获取节气饮食建议失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });
  
  // 辅助函数 - 获取饮食习惯数据
  function getDietaryHabitsData(userId, period, knowledgeLinks) {
    // 返回模拟数据
    return {
      userId,
      analysisDate: new Date().toISOString(),
      dietaryProfile: {
        mainDietType: '混合饮食',
        preferences: ['蔬菜', '水果', '鱼类', '豆制品'],
        avoidances: ['辛辣食物', '油炸食品'],
        regularMeals: 2.7, // 平均每天规律进餐次数
        nutritionBalance: 0.78, // 营养均衡得分
        mealTiming: {
          breakfast: '07:30-08:00',
          lunch: '12:00-13:00',
          dinner: '18:30-19:30'
        }
      },
      analysis: {
        strengths: [
          '富含新鲜蔬果摄入，有利于维生素和矿物质供应',
          '合理控制了油脂摄入，有助于心血管健康',
          '饮食多样性较好，有助于获取全面营养'
        ],
        improvements: [
          '早餐时间不够规律，可能影响上午精力',
          '晚餐偏晚，可能影响睡眠质量',
          '蛋白质来源可以更加多样化'
        ],
        tcmPerspective: '整体饮食偏寒凉，脾胃功能可能受到影响，建议适当增加温性食物平衡阴阳',
        seasonalCompatibility: 0.82 // 与当前季节的饮食适配度
      },
      recommendations: [
        {
          type: '早餐改进',
          title: '调整早餐时间和内容',
          description: '建议将早餐提前到7:00-7:30，并增加优质蛋白质（如鸡蛋或酸奶）含量',
          reasoning: '规律的早餐时间有助于稳定血糖和提高上午工作效率',
          knowledgeLinks: knowledgeLinks.slice(0, 2)
        },
        {
          type: '晚餐调整',
          title: '晚餐时间提前',
          description: '建议将晚餐时间调整到18:00前，减少碳水化合物摄入',
          reasoning: '提前晚餐时间有助于消化和提高睡眠质量',
          knowledgeLinks: knowledgeLinks.slice(2, 4)
        },
        {
          type: '体质调理',
          title: '平衡寒凉食物',
          description: '适当增加温性食物如姜、红枣、栗子等，特别是在早晚餐中',
          reasoning: '根据中医理论，当前饮食偏寒凉，需要适当平衡阴阳',
          knowledgeLinks: knowledgeLinks.slice(4)
        }
      ]
    };
  }
  
  // 辅助函数 - 获取生活方式分析数据
  function getLifestyleAnalysisData(userId, recommendations) {
    // 返回模拟数据
    return {
      userId,
      timestamp: new Date().toISOString(),
      overallScore: 78,
      categories: {
        diet: {
          score: 82,
          strengths: ['规律饮食', '蔬果充足', '水分充足'],
          weaknesses: ['晚餐过晚', '零食过多']
        },
        activity: {
          score: 65,
          strengths: ['定期步行', '周末户外活动'],
          weaknesses: ['久坐时间长', '缺乏力量训练']
        },
        sleep: {
          score: 70,
          strengths: ['总睡眠时间充足'],
          weaknesses: ['入睡困难', '睡眠不连续']
        },
        stress: {
          score: 75,
          strengths: ['有放松爱好', '社交活动充足'],
          weaknesses: ['工作压力大', '应对方式单一']
        }
      },
      constitution: '气虚质',
      seasonalAdvice: '当前处于夏季，注意清热解暑，保护阳气',
      recommendations: recommendations.length > 0 ? recommendations : [
        {
          category: 'diet',
          title: '调整晚餐时间',
          description: '建议将晚餐时间调整到18:00前，晚餐后可适当进行轻度活动如散步',
          priority: 1
        },
        {
          category: 'activity',
          title: '增加站立时间',
          description: '工作中每小时站立活动5分钟，减少久坐对健康的负面影响',
          priority: 2
        },
        {
          category: 'sleep',
          title: '建立睡前仪式',
          description: '睡前30分钟关闭电子设备，可以做些放松活动如阅读或冥想',
          priority: 1
        },
        {
          category: 'stress',
          title: '呼吸调节练习',
          description: '每天进行3次深呼吸练习，每次5-10分钟，帮助缓解压力',
          priority: 3
        }
      ]
    };
  }
  
  // 辅助函数 - 获取默认生活方式建议
  function getDefaultRecommendations() {
    return [
      {
        category: 'diet',
        title: '增加蛋白质摄入',
        description: '每天确保摄入足够的优质蛋白质，如鱼类、豆制品和瘦肉',
        priority: 2
      },
      {
        category: 'activity',
        title: '加入力量训练',
        description: '每周进行2-3次力量训练，每次20-30分钟，提高肌肉量和代谢率',
        priority: 2
      },
      {
        category: 'sleep',
        title: '规律作息时间',
        description: '保持规律的睡眠-起床时间，包括周末，有助于提高睡眠质量',
        priority: 1
      },
      {
        category: 'stress',
        title: '正念冥想',
        description: '尝试每天10-15分钟的正念冥想，提高对当下的关注力和减轻压力',
        priority: 3
      }
    ];
  }
  
  // 辅助函数 - 获取节气饮食数据
  function getSeasonalDietData(date, constitution) {
    // 这里简化处理，实际应该根据日期计算当前节气
    // 以下是模拟数据
    
    const currentDate = new Date(date);
    const month = currentDate.getMonth() + 1;
    
    // 简单根据月份判断季节和节气（实际应更精确）
    let season, currentSolarTerm, nextSolarTerm, daysToNext;
    
    if (month >= 3 && month <= 5) {
      season = '春季';
      currentSolarTerm = month === 3 ? '惊蛰' : month === 4 ? '清明' : '立夏';
      nextSolarTerm = month === 3 ? '春分' : month === 4 ? '谷雨' : '小满';
      daysToNext = 15;
    } else if (month >= 6 && month <= 8) {
      season = '夏季';
      currentSolarTerm = month === 6 ? '芒种' : month === 7 ? '小暑' : '立秋';
      nextSolarTerm = month === 6 ? '夏至' : month === 7 ? '大暑' : '处暑';
      daysToNext = 15;
    } else if (month >= 9 && month <= 11) {
      season = '秋季';
      currentSolarTerm = month === 9 ? '白露' : month === 10 ? '寒露' : '立冬';
      nextSolarTerm = month === 9 ? '秋分' : month === 10 ? '霜降' : '小雪';
      daysToNext = 15;
    } else {
      season = '冬季';
      currentSolarTerm = month === 12 ? '大雪' : month === 1 ? '小寒' : '雨水';
      nextSolarTerm = month === 12 ? '冬至' : month === 1 ? '大寒' : '惊蛰';
      daysToNext = 15;
    }
    
    // 根据季节返回对应的饮食建议
    let seasonalFoods = [];
    let dietaryPrinciples = [];
    let generalRecommendations = [];
    let constitutionSpecificRecommendations = [];
    let recipes = [];
    
    switch (season) {
      case '春季':
        seasonalFoods = [
          {
            name: '春笋',
            category: '蔬菜',
            benefits: ['润肠通便', '清热化痰', '促进消化']
          },
          {
            name: '菠菜',
            category: '蔬菜',
            benefits: ['补血养血', '润肠通便']
          },
          {
            name: '荠菜',
            category: '蔬菜',
            benefits: ['清热解毒', '凉血止血', '利尿消肿']
          }
        ];
        
        dietaryPrinciples = [
          '春季饮食宜温和升发，少食酸，多食甘',
          '适当增加辛甘发散之品，如葱、香菜等',
          '注意保护阳气，不宜过食寒凉'
        ];
        
        generalRecommendations = [
          '早起早睡，顺应春季阳气升发的特点',
          '饮食宜清淡，少食肥腻',
          '适当增加户外活动，促进阳气生发'
        ];
        
        recipes = [
          {
            name: '春笋炒肉丝',
            description: '鲜嫩春笋配以瘦肉丝，清爽不油腻',
            ingredients: ['春笋', '猪里脊肉', '胡萝卜', '青椒', '姜', '蒜', '料酒'],
            benefits: '健脾开胃，补中益气'
          },
          {
            name: '荠菜饺子',
            description: '荠菜肉馅饺子，鲜香可口',
            ingredients: ['荠菜', '猪肉末', '饺子皮', '姜', '葱', '料酒', '盐'],
            benefits: '清热解毒，开胃消食'
          }
        ];
        break;
        
      case '夏季':
        seasonalFoods = [
          {
            name: '苦瓜',
            category: '蔬菜',
            benefits: ['清热解毒', '明目', '降血糖']
          },
          {
            name: '西瓜',
            category: '水果',
            benefits: ['清热解暑', '生津止渴', '利尿']
          },
          {
            name: '绿豆',
            category: '豆类',
            benefits: ['清热解毒', '消暑除烦', '利尿消肿']
          }
        ];
        
        dietaryPrinciples = [
          '夏季饮食宜清淡，少食辛温燥热之品',
          '适当食用苦味食物，如苦瓜、莴笋，以清泄暑热',
          '注意补充水分，预防中暑'
        ];
        
        generalRecommendations = [
          '保持心情舒畅，避免暴怒伤阴',
          '睡眠宜早起晚睡，午间可适当小憩',
          '饮食宜少量多餐，避免过饱'
        ];
        
        recipes = [
          {
            name: '清炒苦瓜',
            description: '简单清炒的苦瓜，保留清苦味',
            ingredients: ['苦瓜', '蒜', '盐', '植物油'],
            benefits: '清热解暑，消暑除烦'
          },
          {
            name: '绿豆汤',
            description: '清甜可口的绿豆汤，夏日解暑佳品',
            ingredients: ['绿豆', '冰糖'],
            benefits: '清热解毒，消暑除烦'
          }
        ];
        break;
        
      case '秋季':
        seasonalFoods = [
          {
            name: '山药',
            category: '薯类',
            benefits: ['补脾养胃', '益肺止咳', '固肾益精']
          },
          {
            name: '梨',
            category: '水果',
            benefits: ['润肺止咳', '清热生津', '降火']
          },
          {
            name: '银耳',
            category: '菌类',
            benefits: ['滋阴润肺', '益气补脑', '强健脾胃']
          }
        ];
        
        dietaryPrinciples = [
          '秋季饮食宜滋阴润燥，多食甘润之品',
          '适当增加酸味食物，如山楂、柑橘，以收敛肺气',
          '减少辛辣刺激食物，防止耗伤津液'
        ];
        
        generalRecommendations = [
          '保持情绪平稳，避免悲伤伤肺',
          '早睡早起，保证充足睡眠',
          '多食用滋阴润肺的食物，如梨、银耳等'
        ];
        
        recipes = [
          {
            name: '山药排骨汤',
            description: '滋补又营养的家常汤品',
            ingredients: ['山药', '排骨', '枸杞', '姜', '盐'],
            benefits: '补脾养胃，益肺止咳'
          },
          {
            name: '银耳雪梨羹',
            description: '滋阴润燥的甜品',
            ingredients: ['银耳', '雪梨', '冰糖', '枸杞'],
            benefits: '滋阴润肺，益气生津'
          }
        ];
        break;
        
      case '冬季':
        seasonalFoods = [
          {
            name: '羊肉',
            category: '肉类',
            benefits: ['补阳气', '温脾胃', '益气血']
          },
          {
            name: '大枣',
            category: '果品',
            benefits: ['补脾和胃', '益气生津', '调营卫']
          },
          {
            name: '桂圆',
            category: '果品',
            benefits: ['补心脾', '益气血', '安神']
          }
        ];
        
        dietaryPrinciples = [
          '冬季饮食宜温补，少食生冷',
          '适当增加温热食物，如羊肉、生姜等',
          '注意保护阳气，适当进补但不宜过度'
        ];
        
        generalRecommendations = [
          '早睡晚起，保护阳气',
          '饮食宜温热，避免过食寒凉',
          '适当食用温补食物，但不宜燥热太过'
        ];
        
        recipes = [
          {
            name: '羊肉萝卜汤',
            description: '冬季暖身进补汤品',
            ingredients: ['羊肉', '白萝卜', '姜', '葱', '八角', '桂皮', '料酒'],
            benefits: '温阳散寒，补气益血'
          },
          {
            name: '桂圆红枣粥',
            description: '甜润滋补的早餐粥品',
            ingredients: ['桂圆', '红枣', '糯米', '冰糖'],
            benefits: '补心脾，益气血，安神'
          }
        ];
        break;
    }
    
    // 根据体质调整建议
    switch (constitution) {
      case '气虚质':
        constitutionSpecificRecommendations = [
          '适当增加补气食物如党参、黄芪等',
          '少食生冷食物，以免损伤脾胃',
          '注意定时定量进餐，避免过度劳累'
        ];
        break;
      case '阳虚质':
        constitutionSpecificRecommendations = [
          '多食温补阳气的食物，如羊肉、韭菜等',
          '少食寒凉食物，避免生冷饮料',
          '保持身体温暖，避免受寒'
        ];
        break;
      case '阴虚质':
        constitutionSpecificRecommendations = [
          '多食滋阴润燥的食物，如百合、银耳等',
          '少食辛辣温燥食物，避免烧烤油炸',
          '保持心情舒畅，避免暴怒耗阴'
        ];
        break;
      case '痰湿质':
        constitutionSpecificRecommendations = [
          '饮食宜清淡，少食肥甘厚味',
          '多食利湿健脾的食物，如薏米、红豆等',
          '适当运动，促进水湿代谢'
        ];
        break;
      case '湿热质':
        constitutionSpecificRecommendations = [
          '多食清热利湿的食物，如冬瓜、绿豆等',
          '少食辛辣油腻食物，避免烧烤油炸',
          '保持情绪平稳，避免过度劳累'
        ];
        break;
      case '血瘀质':
        constitutionSpecificRecommendations = [
          '多食活血化瘀的食物，如桃仁、红花等',
          '少食油腻粘滞食物，减少胆固醇摄入',
          '保持规律运动，促进血液循环'
        ];
        break;
      case '气郁质':
        constitutionSpecificRecommendations = [
          '多食疏肝解郁的食物，如柴胡、佛手等',
          '保持情绪舒畅，避免过度思虑',
          '适当运动和户外活动，调节情志'
        ];
        break;
      case '特禀质':
        constitutionSpecificRecommendations = [
          '避免接触过敏原',
          '增强体质，提高免疫力',
          '饮食宜清淡，避免刺激性食物'
        ];
        break;
      default: // 平和质
        constitutionSpecificRecommendations = [
          '饮食均衡，不偏不倚',
          '根据季节适当调整饮食结构',
          '保持良好生活习惯，预防疾病'
        ];
    }
    
    return {
      currentSolarTerm,
      nextSolarTerm,
      daysToNext,
      season,
      seasonalFoods,
      dietaryPrinciples,
      recommendations: {
        general: generalRecommendations,
        constitutionSpecific: constitutionSpecificRecommendations
      },
      recipes
    };
  }
};