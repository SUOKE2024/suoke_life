/**
 * 索儿服务 - 方言服务集成
 * 
 * 该服务封装了共享方言服务的功能，为儿童用户提供适合儿童的方言学习和互动能力
 */

const path = require('path');
const fs = require('fs');
const logger = require('../utils/logger');

// 导入共享服务
const sharedServices = require('../../shared/services');
const dialectService = sharedServices.dialect;

// 配置
const DIALECT_SUPPORT_ENABLED = process.env.DIALECT_SUPPORT_ENABLED === 'true';
const DEFAULT_DIALECT = process.env.DEFAULT_DIALECT || 'mandarin';
const DIALECT_DETECTION_THRESHOLD = parseFloat(process.env.DIALECT_DETECTION_THRESHOLD || '0.7');

/**
 * 方言服务类 - 专注于儿童方言学习和互动
 */
class DialectService {
  /**
   * 获取适合儿童的方言列表
   * @returns {Promise<Object>} 方言列表
   */
  async getChildFriendlyDialects() {
    try {
      if (!DIALECT_SUPPORT_ENABLED) {
        return { success: true, dialects: [] };
      }
      
      // 使用Mongoose模型
      const { Dialect } = require('../../shared/models/dialect.model');
      
      // 获取所有活跃且支持级别较高的方言
      const dialects = await Dialect.find({
        status: 'active',
        supportLevel: { $gt: 2 } // 至少支持级别为3才适合儿童
      }).select('code name region supportLevel sampleStats metadata').lean();
      
      // 添加儿童友好的描述和图标
      const childFriendlyDialects = dialects.map(dialect => ({
        code: dialect.code,
        name: dialect.name,
        region: dialect.region,
        supportLevel: dialect.supportLevel,
        // 添加儿童友好的描述
        childFriendlyName: this._getChildFriendlyName(dialect.name),
        description: this._simplifyDescription(dialect.metadata?.description || ''),
        // 添加动物或卡通图标（实际应从资源文件获取）
        icon: this._getDialectIcon(dialect.code),
        // 简化区域表示
        simpleRegion: `${dialect.region.province}${dialect.region.city ? ' ' + dialect.region.city : ''}`
      }));
      
      return {
        success: true,
        count: childFriendlyDialects.length,
        dialects: childFriendlyDialects
      };
    } catch (error) {
      logger.error(`获取儿童友好方言列表失败: ${error.message}`);
      return {
        success: false,
        error: `获取方言列表失败: ${error.message}`
      };
    }
  }

  /**
   * 检测音频中的方言（儿童友好版本）
   * @param {Buffer} audioBuffer 音频数据
   * @returns {Promise<Object>} 检测结果
   */
  async detectDialectForChildren(audioBuffer) {
    try {
      if (!DIALECT_SUPPORT_ENABLED) {
        return { 
          success: true, 
          detected: false,
          dialectCode: DEFAULT_DIALECT,
          friendlyName: '普通话',
          message: '说的是普通话呢！' 
        };
      }
      
      // 验证音频数据
      if (!audioBuffer || audioBuffer.length === 0) {
        throw new Error('没有听到声音哦');
      }
      
      logger.info(`开始检测儿童音频中的方言，数据大小: ${audioBuffer.length} 字节`);
      
      // TODO: 实现实际的方言检测逻辑
      // 这里应该调用实际的方言检测模型
      // 为演示目的，返回模拟结果
      
      const possibleDialects = ['cantonese', 'sichuanese', 'shanghainese', DEFAULT_DIALECT];
      const mockDetection = {
        dialectCode: possibleDialects[Math.floor(Math.random() * possibleDialects.length)],
        confidence: 0.75 + Math.random() * 0.2
      };
      
      // 获取方言名称和儿童友好名称
      let dialectName = '普通话';
      if (mockDetection.dialectCode !== DEFAULT_DIALECT) {
        try {
          const { Dialect } = require('../../shared/models/dialect.model');
          const dialectInfo = await Dialect.findOne({ code: mockDetection.dialectCode })
            .select('name')
            .lean();
          
          if (dialectInfo) {
            dialectName = dialectInfo.name;
          }
        } catch (nameError) {
          logger.warn(`获取方言名称失败: ${nameError.message}`);
        }
      }
      
      const friendlyName = this._getChildFriendlyName(dialectName);
      
      // 记录方言样本（如果允许）
      if (mockDetection.confidence > DIALECT_DETECTION_THRESHOLD) {
        try {
          // 使用共享服务记录样本来源
          await dialectService.sample.recordSampleSource(mockDetection.dialectCode, {
            method: 'user-upload',
            location: {
              province: '全国',
              city: '儿童用户'
            }
          });
          
          logger.debug(`已记录儿童方言样本来源: ${mockDetection.dialectCode}`);
        } catch (sampleError) {
          logger.warn(`记录方言样本失败: ${sampleError.message}`);
        }
      }
      
      // 返回儿童友好的消息
      const detected = mockDetection.confidence > DIALECT_DETECTION_THRESHOLD;
      let friendlyMessage = '';
      
      if (detected) {
        if (mockDetection.dialectCode === DEFAULT_DIALECT) {
          friendlyMessage = '你说的是标准普通话，真棒！';
        } else {
          friendlyMessage = `哇！你说的是${friendlyName}，好有趣！`;
        }
      } else {
        friendlyMessage = '我没听清楚你说的是什么方言，再试一次好吗？';
      }
      
      return {
        success: true,
        detected,
        dialectCode: mockDetection.dialectCode,
        dialectName,
        friendlyName,
        confidence: mockDetection.confidence,
        message: friendlyMessage,
        // 添加儿童友好的奖励
        reward: detected ? {
          points: Math.floor(Math.random() * 5) + 1,
          badge: mockDetection.dialectCode === DEFAULT_DIALECT ? '普通话小达人' : `${friendlyName}探险家`
        } : null
      };
    } catch (error) {
      logger.error(`儿童方言检测失败: ${error.message}`);
      return {
        success: false,
        error: `听不清楚呢，我们再试一次好吗？`,
        dialectCode: DEFAULT_DIALECT,
        friendlyName: '普通话'
      };
    }
  }

  /**
   * 获取方言学习游戏
   * @param {String} dialectCode 方言代码
   * @param {Number} ageGroup 年龄组 (3-5, 6-8, 9-12)
   * @returns {Promise<Object>} 游戏列表
   */
  async getDialectLearningGames(dialectCode, ageGroup) {
    try {
      if (!dialectCode) {
        throw new Error('请选择一种方言');
      }
      
      if (!DIALECT_SUPPORT_ENABLED) {
        return { 
          success: false, 
          error: '方言游戏暂时不可用'
        };
      }
      
      // 验证方言是否存在
      const { Dialect } = require('../../shared/models/dialect.model');
      const dialectInfo = await Dialect.findOne({ 
        code: dialectCode,
        status: 'active'
      }).select('name supportLevel').lean();
      
      if (!dialectInfo) {
        throw new Error(`找不到这种方言`);
      }
      
      // 根据年龄组和方言确定适合的游戏
      // 实际应该从专门的儿童游戏数据库获取
      // 为演示目的，返回模拟数据
      
      let games = [];
      const dialectName = dialectInfo.name;
      
      // 3-5岁：简单的听音辨别游戏
      if (!ageGroup || ageGroup === '3-5') {
        games.push(
          {
            id: `${dialectCode}_match_sound_1`,
            name: `${dialectName}动物音`,
            type: '听音匹配',
            description: `听听这些动物用${dialectName}怎么叫，然后找到对应的动物`,
            difficulty: '简单',
            minAge: 3,
            maxAge: 5,
            imageUrl: `https://example.com/games/${dialectCode}/animals.png`,
            duration: '5分钟'
          },
          {
            id: `${dialectCode}_repeat_1`,
            name: `${dialectName}小鹦鹉`,
            type: '模仿发音',
            description: `听听这些简单的${dialectName}词语，然后跟着说出来`,
            difficulty: '简单',
            minAge: 3,
            maxAge: 5,
            imageUrl: `https://example.com/games/${dialectCode}/parrot.png`,
            duration: '3分钟'
          }
        );
      }
      
      // 6-8岁：词汇学习游戏
      if (!ageGroup || ageGroup === '6-8') {
        games.push(
          {
            id: `${dialectCode}_word_match_1`,
            name: `${dialectName}连连看`,
            type: '词汇匹配',
            description: `将${dialectName}词语和对应的图片连起来`,
            difficulty: '中等',
            minAge: 6,
            maxAge: 8,
            imageUrl: `https://example.com/games/${dialectCode}/word_match.png`,
            duration: '8分钟'
          },
          {
            id: `${dialectCode}_memory_1`,
            name: `${dialectName}记忆大师`,
            type: '记忆游戏',
            description: `记住${dialectName}单词和对应的图片，然后找出配对`,
            difficulty: '中等',
            minAge: 6,
            maxAge: 8,
            imageUrl: `https://example.com/games/${dialectCode}/memory.png`,
            duration: '10分钟'
          }
        );
      }
      
      // 9-12岁：对话和故事游戏
      if (!ageGroup || ageGroup === '9-12') {
        games.push(
          {
            id: `${dialectCode}_conversation_1`,
            name: `${dialectName}小剧场`,
            type: '对话练习',
            description: `和虚拟角色用${dialectName}进行简单对话`,
            difficulty: '较难',
            minAge: 9,
            maxAge: 12,
            imageUrl: `https://example.com/games/${dialectCode}/conversation.png`,
            duration: '15分钟'
          },
          {
            id: `${dialectCode}_story_1`,
            name: `${dialectName}故事会`,
            type: '故事填空',
            description: `听${dialectName}故事，然后填入正确的词语`,
            difficulty: '较难',
            minAge: 9,
            maxAge: 12,
            imageUrl: `https://example.com/games/${dialectCode}/story.png`,
            duration: '20分钟'
          }
        );
      }
      
      // 根据年龄组过滤游戏
      if (ageGroup) {
        const [minAge, maxAge] = ageGroup.split('-').map(Number);
        games = games.filter(game => 
          (game.minAge <= maxAge && game.maxAge >= minAge)
        );
      }
      
      logger.info(`获取方言 ${dialectCode} 学习游戏成功，返回 ${games.length} 个游戏`);
      
      return {
        success: true,
        dialectCode,
        dialectName,
        friendlyName: this._getChildFriendlyName(dialectName),
        ageGroup,
        games
      };
    } catch (error) {
      logger.error(`获取方言学习游戏失败: ${error.message}`);
      return {
        success: false,
        error: `获取游戏失败: ${error.message}`
      };
    }
  }

  /**
   * 创建儿童方言探险任务
   * @param {String} userId 用户ID
   * @param {Array<String>} dialectCodes 方言代码列表
   * @returns {Promise<Object>} 探险任务
   */
  async createDialectAdventure(userId, dialectCodes) {
    try {
      if (!userId) {
        throw new Error('需要用户ID');
      }
      
      if (!dialectCodes || !Array.isArray(dialectCodes) || dialectCodes.length === 0) {
        // 默认使用几种主要方言
        dialectCodes = ['cantonese', 'sichuanese', 'shanghainese', 'hakka'];
      }
      
      if (!DIALECT_SUPPORT_ENABLED) {
        return { 
          success: false, 
          error: '方言探险暂时不可用'
        };
      }
      
      // 验证方言是否存在
      const { Dialect } = require('../../shared/models/dialect.model');
      const dialects = await Dialect.find({ 
        code: { $in: dialectCodes },
        status: 'active'
      }).select('code name region').lean();
      
      if (dialects.length === 0) {
        throw new Error(`找不到指定的方言`);
      }
      
      // 创建方言探险任务
      // 实际应该保存到数据库并与用户关联
      // 为演示目的，返回模拟数据
      
      logger.info(`为用户 ${userId} 创建方言探险任务`);
      
      // 生成探险地图
      const adventureMap = dialects.map((dialect, index) => ({
        position: index + 1,
        dialectCode: dialect.code,
        dialectName: dialect.name,
        friendlyName: this._getChildFriendlyName(dialect.name),
        region: `${dialect.region.province}${dialect.region.city ? ' ' + dialect.region.city : ''}`,
        icon: this._getDialectIcon(dialect.code),
        tasksRequired: 3,
        tasksCompleted: 0,
        unlocked: index === 0, // 只有第一个位置是解锁的
        treasureFound: false
      }));
      
      const adventure = {
        id: `adv_${Date.now()}`,
        userId,
        title: '中国方言大冒险',
        description: '和索儿一起探索中国不同地区的方言，收集宝藏和徽章！',
        createdAt: new Date(),
        expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30天后过期
        progress: {
          totalPositions: adventureMap.length,
          currentPosition: 1,
          treasuresFound: 0,
          badgesEarned: 0,
          pointsEarned: 0
        },
        rewards: {
          availableBadges: adventureMap.map(pos => `${pos.friendlyName}探险家`),
          finalReward: '方言大师勋章'
        },
        map: adventureMap
      };
      
      return {
        success: true,
        adventure
      };
    } catch (error) {
      logger.error(`创建方言探险任务失败: ${error.message}`);
      return {
        success: false,
        error: `创建探险任务失败: ${error.message}`
      };
    }
  }

  /**
   * 为方言名称生成儿童友好的名称
   * @param {String} dialectName 方言名称
   * @returns {String} 儿童友好的名称
   * @private
   */
  _getChildFriendlyName(dialectName) {
    const friendlyNames = {
      '普通话': '普通话',
      '粤语': '广东话',
      '客家话': '客家话',
      '闽南语': '厦门话',
      '上海话': '上海话',
      '四川话': '川娃子话',
      '东北话': '东北话',
      '湖南话': '湘妹子话',
      '江西话': '赣语话',
      '河南话': '中原话',
      '山东话': '胶东话',
      '陕西话': '秦腔话',
      '安徽话': '徽州话',
      '苏州话': '姑苏话'
    };
    
    return friendlyNames[dialectName] || dialectName;
  }

  /**
   * 简化描述文本，使其适合儿童
   * @param {String} description 原始描述
   * @returns {String} 简化后的描述
   * @private
   */
  _simplifyDescription(description) {
    if (!description) return '这是一种很有趣的方言';
    
    // 移除复杂术语
    let simplified = description
      .replace(/音位/g, '发音')
      .replace(/声调/g, '音调')
      .replace(/语法/g, '说话方式')
      .replace(/词汇/g, '词语')
      .replace(/语音/g, '声音')
      .replace(/方言学/g, '方言研究');
    
    // 限制长度
    if (simplified.length > 100) {
      simplified = simplified.substring(0, 97) + '...';
    }
    
    return simplified;
  }

  /**
   * 获取方言对应的图标
   * @param {String} dialectCode 方言代码
   * @returns {String} 图标URL
   * @private
   */
  _getDialectIcon(dialectCode) {
    const icons = {
      'mandarin': 'panda',
      'cantonese': 'tiger',
      'sichuanese': 'bear',
      'shanghainese': 'dolphin',
      'hakka': 'eagle',
      'hokkien': 'fish',
      'northeastern': 'deer',
      'hunanese': 'rabbit'
    };
    
    const animal = icons[dialectCode] || 'dragon';
    return `https://example.com/icons/animals/${animal}.png`;
  }
}

module.exports = new DialectService();