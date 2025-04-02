/**
 * 生活方式服务
 * 处理用户生活方式管理、饮食习惯分析和相关建议
 */

const axios = require('axios');
const { createError } = require('../utils/error-handler');
const logger = require('../utils/logger');

class LifestyleService {
  constructor(config, integrations = {}) {
    this.config = config;
    this.integrations = integrations;
    this.mockData = true; // 在实际数据接入前使用模拟数据
    
    logger.info('生活方式服务初始化完成');
  }

  /**
   * 获取用户饮食习惯分析
   * @param {string} userId - 用户ID
   * @param {string} period - 分析周期 'week'|'month'|'quarter'|'year'
   * @returns {Promise<Object>} 饮食习惯分析
   */
  async getDietaryHabitsAnalysis(userId, period = 'month') {
    // 验证用户ID
    if (!userId || userId.length < 3) {
      throw createError('invalid_user_id', '无效的用户ID', 400);
    }
    
    try {
      // 尝试从数据库或API获取用户饮食数据
      let dietaryData = null;
      
      // 如果有数据库连接，可以从数据库查询
      if (this.integrations?.database) {
        try {
          // 实现查询数据库获取用户饮食数据的逻辑
          // ...
        } catch (dbError) {
          logger.error(`从数据库获取饮食数据失败: ${dbError.message}`);
        }
      }
      
      // 整合知识图谱中的相关健康知识
      let knowledgeLinks = [];
      if (this.integrations?.knowledge_integration) {
        try {
          const knowledgeResponse = await this.integrations.knowledge_integration.findRelatedKnowledge({
            concepts: ['饮食习惯', '营养均衡', '三餐规律'],
            limit: 5
          });
          
          if (knowledgeResponse && knowledgeResponse.nodes) {
            knowledgeLinks = knowledgeResponse.nodes.map(node => node.id);
          }
        } catch (knowledgeError) {
          logger.warn(`获取知识图谱数据失败: ${knowledgeError.message}`);
          // 继续处理，不影响主流程
        }
      }
      
      // 如果没有从数据库或API获取到数据，使用模拟数据
      if (!dietaryData || this.mockData) {
        dietaryData = this._getMockDietaryHabitsData(userId, period, knowledgeLinks);
      }
      
      return dietaryData;
    } catch (error) {
      if (error.isCustom) {
        throw error;
      }
      
      logger.error(`获取用户饮食习惯分析失败: ${error.message}`);
      throw createError('dietary_habits_analysis_failed', '获取用户饮食习惯分析失败', 500);
    }
  }
  
  /**
   * 获取生活方式综合分析
   * @param {string} userId - 用户ID
   * @returns {Promise<Object>} 生活方式综合分析
   */
  async getLifestyleAnalysis(userId) {
    // 验证用户ID
    if (!userId || userId.length < 3) {
      throw createError('invalid_user_id', '无效的用户ID', 400);
    }
    
    try {
      // 尝试从数据库或API获取用户生活方式数据
      let lifestyleData = null;
      
      // 如果有数据库连接，可以从数据库查询
      if (this.integrations?.database) {
        try {
          // 实现查询数据库获取用户生活方式数据的逻辑
          // ...
        } catch (dbError) {
          logger.error(`从数据库获取生活方式数据失败: ${dbError.message}`);
        }
      }
      
      // 如果没有从数据库或API获取到数据，使用模拟数据
      if (!lifestyleData || this.mockData) {
        lifestyleData = this._getMockLifestyleAnalysis(userId);
      }
      
      return lifestyleData;
    } catch (error) {
      if (error.isCustom) {
        throw error;
      }
      
      logger.error(`获取用户生活方式分析失败: ${error.message}`);
      throw createError('lifestyle_analysis_failed', '获取用户生活方式分析失败', 500);
    }
  }

  /**
   * 获取季节性生活调整建议
   * @param {string} userId - 用户ID
   * @returns {Promise<Object>} 季节性生活调整建议
   */
  async getSeasonalLifestyleGuidance(userId) {
    // 验证用户ID
    if (!userId || userId.length < 3) {
      throw createError('invalid_user_id', '无效的用户ID', 400);
    }
    
    try {
      const today = new Date();
      const month = today.getMonth();
      
      // 确定当前季节
      const season = ['春', '夏', '秋', '冬'][Math.floor(month / 3) % 4];
      
      // 获取用户基本数据
      let userData = null;
      if (this.integrations?.user_service) {
        try {
          const response = await this.integrations.user_service.getUserInfo(userId);
          if (response && response.data) {
            userData = response.data;
          }
        } catch (error) {
          logger.warn(`获取用户数据失败: ${error.message}`);
        }
      }
      
      // 生成季节性建议
      let seasonalGuidance;
      if (this.integrations?.ai_service && !this.mockData) {
        try {
          // 通过AI服务生成个性化的季节建议
          seasonalGuidance = await this.integrations.ai_service.generateSeasonalGuidance({
            userId,
            userData,
            season
          });
        } catch (aiError) {
          logger.error(`通过AI生成季节建议失败: ${aiError.message}`);
          // 使用模拟数据作为后备
          seasonalGuidance = this._getMockSeasonalGuidance(season, userData);
        }
      } else {
        // 使用模拟数据
        seasonalGuidance = this._getMockSeasonalGuidance(season, userData);
      }
      
      return {
        userId,
        season,
        generatedAt: new Date().toISOString(),
        guidance: seasonalGuidance
      };
    } catch (error) {
      if (error.isCustom) {
        throw error;
      }
      
      logger.error(`获取季节性生活调整建议失败: ${error.message}`);
      throw createError('seasonal_guidance_failed', '获取季节性生活调整建议失败', 500);
    }
  }

  /**
   * 更新用户生活方式设置
   * @param {string} userId - 用户ID
   * @param {Object} settings - 生活方式设置
   * @returns {Promise<Object>} 更新结果
   */
  async updateLifestyleSettings(userId, settings) {
    // 验证用户ID
    if (!userId || userId.length < 3) {
      throw createError('invalid_user_id', '无效的用户ID', 400);
    }
    
    // 验证设置数据
    if (!settings || typeof settings !== 'object') {
      throw createError('invalid_settings', '无效的设置数据', 400);
    }
    
    try {
      logger.info(`更新用户生活方式设置: ${userId}`, { settings });
      
      // 如果有数据库连接，将设置保存到数据库
      let saveResult = null;
      if (this.integrations?.database) {
        try {
          // 实现保存设置到数据库的逻辑
          // ...
          saveResult = { success: true };
        } catch (dbError) {
          logger.error(`保存生活方式设置失败: ${dbError.message}`);
          throw createError('settings_save_failed', '保存设置失败', 500);
        }
      } else {
        // 模拟保存结果
        saveResult = {
          success: true,
          message: '设置已保存',
          timestamp: new Date().toISOString()
        };
      }
      
      return saveResult;
    } catch (error) {
      if (error.isCustom) {
        throw error;
      }
      
      logger.error(`更新生活方式设置失败: ${error.message}`);
      throw createError('update_lifestyle_settings_failed', '更新生活方式设置失败', 500);
    }
  }

  /**
   * 获取模拟饮食习惯数据
   * @private
   */
  _getMockDietaryHabitsData(userId, period, knowledgeLinks = []) {
    const analysisDate = new Date().toISOString();
    
    // 根据不同的周期返回不同的详细程度
    let nutritionBalance = 0.75;
    let regularMeals = 2.5;
    
    // 模拟不同周期的数据差异
    if (period === 'week') {
      nutritionBalance = 0.78;
      regularMeals = 2.7;
    } else if (period === 'quarter') {
      nutritionBalance = 0.72;
      regularMeals = 2.3;
    } else if (period === 'year') {
      nutritionBalance = 0.68;
      regularMeals = 2.1;
    }
    
    return {
      userId,
      analysisDate,
      dietaryProfile: {
        mainDietType: '混合型饮食',
        preferences: ['蔬菜水果', '五谷杂粮', '家禽肉类'],
        avoidances: ['油炸食品', '过于辛辣食物'],
        regularMeals: regularMeals,
        nutritionBalance: nutritionBalance,
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
          reasoning: '充足的早餐蛋白质有助于稳定血糖，提供持久能量。',
          knowledgeLinks: knowledgeLinks.slice(0, 2)
        },
        {
          type: 'habit',
          title: '调整晚餐时间',
          description: '将晚餐时间提前至18:00前，有助于消化和睡眠。',
          reasoning: '中医认为脾胃消化功能在申时(15:00-17:00)最强，此时进食更有利于消化吸收。',
          knowledgeLinks: knowledgeLinks.slice(2, 4)
        },
        {
          type: 'nutrition',
          title: '增加水分摄入',
          description: '每天至少饮用1.5-2升水，可在餐间饮用温水。',
          reasoning: '充足的水分有助于代谢废物排出，维持体内平衡。',
          knowledgeLinks: knowledgeLinks.slice(0, 1)
        }
      ]
    };
  }
  
  /**
   * 获取模拟生活方式分析数据
   * @private
   */
  _getMockLifestyleAnalysis(userId) {
    return {
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
        },
        stress: {
          score: 68,
          strengths: [
            '有良好的社交支持',
            '能够识别压力来源'
          ],
          weaknesses: [
            '缺乏有效的减压策略',
            '工作与生活平衡不佳'
          ]
        },
        environment: {
          score: 85,
          strengths: [
            '居住环境空气质量良好',
            '生活空间整洁有序'
          ],
          weaknesses: [
            '噪音干扰',
            '室内植物较少'
          ]
        }
      },
      tcmAnalysis: {
        constitution: '脾胃湿热体质',
        suggestions: [
          '饮食宜清淡，避免辛辣油腻',
          '保持情绪舒畅，避免忧思过度',
          '适当体育锻炼，避免久坐不动'
        ]
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
        },
        {
          category: 'sleep',
          priority: 'high',
          title: '建立睡前仪式',
          description: '睡前1小时关闭所有电子设备，进行冥想或阅读。'
        }
      ]
    };
  }
  
  /**
   * 获取模拟季节性生活调整建议
   * @private
   */
  _getMockSeasonalGuidance(season, userData = null) {
    const seasonalGuidance = {
      '春': {
        overview: '春季是万物复苏的季节，阳气开始生发，此时应顺应自然，重在"生发"。',
        dietaryGuidance: {
          principles: '春季饮食宜温补阳气，可多食用温性食物如韭菜、香菜等。',
          recommended: ['韭菜', '香椿', '春笋', '菠菜', '豆芽', '草莓'],
          avoid: ['辛辣刺激', '油腻煎炸', '过咸过酸'],
          recipes: [
            {
              name: '春笋炒肉',
              description: '鲜嫩春笋与瘦肉同炒，具有健脾养胃的功效。'
            },
            {
              name: '香椿豆腐',
              description: '春季时令香椿与豆腐搭配，清新可口，补充植物蛋白。'
            }
          ]
        },
        activityGuidance: {
          principles: '春季适合做一些舒展筋骨、舒缓身心的运动，如散步、太极等。',
          recommended: ['早晨慢跑', '太极拳', '五禽戏', '散步'],
          timeOfDay: '清晨是春季锻炼的最佳时段，此时阳气初生，空气清新。',
          duration: '每天30-60分钟的中等强度活动最为适宜。'
        },
        sleepGuidance: {
          principles: '春季作息应"早睡早起"，顺应阳气生发。',
          bedtime: '晚上10点前入睡',
          waketime: '早上5-6点起床',
          tips: [
            '保持房间温度适宜，避免风寒',
            '睡前可用热水泡脚，帮助入眠',
            '早晨醒来可做舒展运动，帮助阳气生发'
          ]
        },
        emotionalGuidance: {
          seasonalEmotion: '根据中医理论，春季对应肝，易怒伤肝，应保持心情舒畅。',
          recommendations: [
            '避免情绪激动，保持心情平和',
            '可通过读书、听音乐等方式放松心情',
            '适当亲近自然，感受春天生机'
          ]
        },
        healthReminders: [
          '春季气温变化大，应注意适时增减衣物',
          '过敏体质者应注意防护，减少接触过敏原',
          '春困现象常见，可适当午休，但不宜过长'
        ]
      },
      '夏': {
        overview: '夏季气候炎热，阳气充沛，人体阳气外发，此时应注重"清泄"。',
        dietaryGuidance: {
          principles: '夏季饮食宜清淡，多食用苦瓜、绿豆等清热食物，以防暑热。',
          recommended: ['苦瓜', '绿豆', '西瓜', '黄瓜', '莲子', '荷叶'],
          avoid: ['辛辣燥热', '油腻厚重', '烧烤煎炸'],
          recipes: [
            {
              name: '绿豆汤',
              description: '清热解暑的夏季佳饮，可加入少量冰糖提味。'
            },
            {
              name: '凉拌黄瓜',
              description: '黄瓜切丝凉拌，加入少量蒜末和醋，开胃消暑。'
            }
          ]
        },
        activityGuidance: {
          principles: '夏季运动应避开高温时段，选择清晨或傍晚，强度不宜过大。',
          recommended: ['游泳', '晨练', '傍晚散步', '太极'],
          timeOfDay: '早晨6-8点或傍晚6点后是夏季运动的较佳时段。',
          duration: '避免长时间高强度运动，每次30-45分钟为宜。'
        },
        sleepGuidance: {
          principles: '夏季可适当"晚睡早起"，保持充足睡眠。',
          bedtime: '晚上10-11点入睡',
          waketime: '早上5-6点起床',
          tips: [
            '睡前洗个温水澡，帮助降温入睡',
            '保持卧室通风凉爽，避免空调温度过低',
            '午休不宜过长，20-30分钟为宜'
          ]
        },
        emotionalGuidance: {
          seasonalEmotion: '夏季对应心，应保持心情愉悦，避免烦躁。',
          recommendations: [
            '保持心情舒畅，多参与愉快的社交活动',
            '避免过度兴奋，保持情绪稳定',
            '可尝试冥想放松心神'
          ]
        },
        healthReminders: [
          '注意防暑降温，避免长时间在高温环境中活动',
          '及时补充水分，防止脱水',
          '注意食品安全，防止肠道疾病'
        ]
      },
      '秋': {
        overview: '秋季气候干燥，阳气收敛，养生当以"收敛"为主。',
        dietaryGuidance: {
          principles: '秋季气候干燥，注意润肺养阴，可食用梨、百合等滋阴润燥的食物。',
          recommended: ['梨', '百合', '银耳', '蜂蜜', '莲藕', '山药'],
          avoid: ['辛辣燥热', '烧烤煎炸', '过咸过酸'],
          recipes: [
            {
              name: '百合银耳羹',
              description: '百合银耳清炖，加入适量冰糖，具有滋阴润肺的功效。'
            },
            {
              name: '莲藕排骨汤',
              description: '莲藕与排骨同炖，滋补养阴，适合秋季食用。'
            }
          ]
        },
        activityGuidance: {
          principles: '秋季运动应避免大汗淋漓，以中等强度为宜，注重收敛。',
          recommended: ['快步走', '太极拳', '八段锦', '游泳'],
          timeOfDay: '早晨或傍晚是秋季运动的较佳时段。',
          duration: '每天30-60分钟的中等强度活动为宜。'
        },
        sleepGuidance: {
          principles: '秋季应"早睡早起"，与日落日出相协调。',
          bedtime: '晚上9-10点入睡',
          waketime: '早上5-7点起床',
          tips: [
            '睡前可饮用温热的蜂蜜水，润燥安神',
            '注意保持卧室湿度适宜，防止干燥',
            '早晨起床后可做深呼吸，呼吸新鲜空气'
          ]
        },
        emotionalGuidance: {
          seasonalEmotion: '秋季对应肺，易悲伤，应保持情志舒畅，避免忧郁。',
          recommendations: [
            '保持乐观心态，多参与户外活动',
            '可尝试冥想或瑜伽，平衡身心',
            '欣赏秋景，感受自然变化之美'
          ]
        },
        healthReminders: [
          '注意保暖，预防感冒',
          '保持室内湿度适宜，防止皮肤干燥',
          '多饮水，保持充分水分摄入'
        ]
      },
      '冬': {
        overview: '冬季寒冷，阳气潜藏，养生应以"藏精"为主。',
        dietaryGuidance: {
          principles: '冬季注重养阳护阴，可适当食用羊肉、韭菜等温补食物，增强抵抗力。',
          recommended: ['羊肉', '韭菜', '核桃', '黑芝麻', '姜', '大枣'],
          avoid: ['过于寒凉', '生冷食物', '油腻过重'],
          recipes: [
            {
              name: '羊肉萝卜汤',
              description: '羊肉与白萝卜同炖，温补脾胃，适合冬季食用。'
            },
            {
              name: '核桃红枣粥',
              description: '核桃、红枣与大米同煮，补血养气，增强冬季体质。'
            }
          ]
        },
        activityGuidance: {
          principles: '冬季运动应避免大汗淋漓，以室内或温度适宜环境中进行为宜。',
          recommended: ['室内健身', '瑜伽', '八段锦', '室内慢跑'],
          timeOfDay: '冬季最好在上午9-11点进行锻炼，此时气温相对较高。',
          duration: '每天30-45分钟的中等强度活动为宜。'
        },
        sleepGuidance: {
          principles: '冬季应"早睡晚起"，增加睡眠时间，保存阳气。',
          bedtime: '晚上9点前入睡',
          waketime: '早上7点左右起床',
          tips: [
            '睡前可用热水泡脚，促进血液循环',
            '保持卧室温度适宜，被褥温暖',
            '早晨不宜立即起床，可在床上稍做舒展'
          ]
        },
        emotionalGuidance: {
          seasonalEmotion: '冬季对应肾，易恐，应保持心态平和，增强自信。',
          recommendations: [
            '保持情绪稳定，避免过度紧张和焦虑',
            '多与亲友交流，增强社交支持',
            '可尝试静心冥想，培养内心平静'
          ]
        },
        healthReminders: [
          '注意保暖，特别是颈部、腰部和足部',
          '室内保持适当通风，防止空气污浊',
          '保持适度锻炼，增强抵抗力'
        ]
      }
    };
    
    return seasonalGuidance[season] || {
      overview: '请根据当前季节调整生活方式，顺应自然变化。',
      dietaryGuidance: {
        principles: '饮食应根据季节变化调整，遵循"春生、夏长、秋收、冬藏"的原则。',
        recommended: ['应季蔬果', '粗粮', '适量优质蛋白'],
        avoid: ['过度加工食品', '反季节食物', '过咸过甜'],
        recipes: []
      },
      activityGuidance: {
        principles: '运动应适应季节变化，调整强度和方式。',
        recommended: ['散步', '太极', '舒缓运动'],
        timeOfDay: '选择气温适宜的时段进行户外活动。',
        duration: '每天30-60分钟的中等强度活动为宜。'
      },
      healthReminders: [
        '注意调整作息，保证充足睡眠',
        '及时增减衣物，适应温度变化',
        '保持乐观心态，顺应自然规律'
      ]
    };
  }
}

module.exports = LifestyleService; 