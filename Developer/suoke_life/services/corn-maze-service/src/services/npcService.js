/**
 * NPC服务
 * 处理游戏中NPC角色的交互、对话和行为
 */
const logger = require('../utils/logger');
const { createError } = require('../middlewares/errorHandler');
const { getRedisClient } = require('../config/redis');
const axios = require('axios');
const config = require('../config');
const { generateResponseHash } = require('../utils/crypto');

// 对话记忆行数限制
const MAX_CONTEXT_MESSAGES = 10;
// 对话上下文过期时间（24小时）
const CONTEXT_EXPIRY = 24 * 60 * 60;
// AI模型请求超时时间
const MODEL_TIMEOUT = 10000;

// NPC角色定义
const NPC_CHARACTERS = {
  GUIDE: {
    name: '向导老农',
    personality: '和蔼可亲，知识渊博，了解迷宫的各种秘密',
    backstory: '在这片玉米地工作了40年，见证了迷宫的建立和发展',
    dialogueStyle: '耐心、详细，喜欢用农村谚语',
    helpfulness: 0.9, // 非常乐于助人
    knowledgeLevel: 0.95 // 知识丰富
  },
  MERCHANT: {
    name: '杂货商人',
    personality: '精明能干，喜欢做交易，但也很友善',
    backstory: '来自远方的商人，收集各种奇特物品并出售',
    dialogueStyle: '直接、幽默，总是想推销东西',
    helpfulness: 0.7, // 相对乐于助人
    knowledgeLevel: 0.8 // 对物品知识丰富
  },
  TREASURE_HUNTER: {
    name: '宝藏猎人',
    personality: '冒险刺激，神秘，喜欢谜语',
    backstory: '一生都在寻找各种稀有宝藏，拥有丰富的探险经验',
    dialogueStyle: '神秘、含糊，喜欢说谜语，提供线索而非直接答案',
    helpfulness: 0.5, // 帮助有限，更多是提供线索
    knowledgeLevel: 0.9 // 对宝藏知识丰富
  },
  MAZE_KEEPER: {
    name: '迷宫守护者',
    personality: '严肃，神秘，保护迷宫的秘密',
    backstory: '迷宫的守护者，确保迷宫的规则被遵守',
    dialogueStyle: '简短、正式，有时会说一些谜语般的话',
    helpfulness: 0.3, // 不太乐于助人
    knowledgeLevel: 1.0 // 对迷宫了如指掌
  }
};

/**
 * 获取NPC对话缓存键
 * @param {String} userId - 用户ID
 * @param {String} npcId - NPC ID
 * @returns {String} 缓存键
 */
const getContextCacheKey = (userId, npcId) => `npc:context:${userId}:${npcId}`;

/**
 * 获取用户与NPC的对话上下文
 * @param {String} userId - 用户ID
 * @param {String} npcId - NPC ID
 * @returns {Promise<Array>} 对话上下文
 */
const getConversationContext = async (userId, npcId) => {
  try {
    const redisClient = getRedisClient();
    const cacheKey = getContextCacheKey(userId, npcId);
    
    const cachedContext = await redisClient.get(cacheKey);
    if (cachedContext) {
      return JSON.parse(cachedContext);
    }
    
    return [];
  } catch (error) {
    logger.warn(`获取对话上下文失败: ${userId}/${npcId}`, error);
    return [];
  }
};

/**
 * 保存用户与NPC的对话上下文
 * @param {String} userId - 用户ID
 * @param {String} npcId - NPC ID
 * @param {Array} context - 对话上下文
 * @returns {Promise<Boolean>} 是否成功
 */
const saveConversationContext = async (userId, npcId, context) => {
  try {
    const redisClient = getRedisClient();
    const cacheKey = getContextCacheKey(userId, npcId);
    
    // 只保留最近的N条消息
    const limitedContext = context.slice(-MAX_CONTEXT_MESSAGES);
    
    await redisClient.set(cacheKey, JSON.stringify(limitedContext));
    await redisClient.expire(cacheKey, CONTEXT_EXPIRY);
    
    return true;
  } catch (error) {
    logger.warn(`保存对话上下文失败: ${userId}/${npcId}`, error);
    return false;
  }
};

/**
 * 清除用户与NPC的对话上下文
 * @param {String} userId - 用户ID
 * @param {String} npcId - NPC ID
 * @returns {Promise<Boolean>} 是否成功
 */
const clearConversationContext = async (userId, npcId) => {
  try {
    const redisClient = getRedisClient();
    const cacheKey = getContextCacheKey(userId, npcId);
    
    await redisClient.del(cacheKey);
    
    return true;
  } catch (error) {
    logger.warn(`清除对话上下文失败: ${userId}/${npcId}`, error);
    return false;
  }
};

/**
 * 添加消息到对话上下文
 * @param {Array} context - 当前上下文
 * @param {String} role - 消息角色
 * @param {String} content - 消息内容
 * @returns {Array} 更新后的上下文
 */
const addMessageToContext = (context, role, content) => {
  return [
    ...context,
    {
      role,
      content,
      timestamp: Date.now()
    }
  ];
};

/**
 * 构建AI模型的系统提示
 * @param {Object} npcCharacter - NPC角色定义
 * @param {Object} gameContext - 游戏上下文
 * @returns {String} 系统提示
 */
const buildSystemPrompt = (npcCharacter, gameContext) => {
  const { mazeInfo, playerInfo, gameSettings } = gameContext;
  
  return `你是一个名为"${npcCharacter.name}"的NPC角色，在AR玉米迷宫游戏中与玩家互动。

角色设定:
- 性格: ${npcCharacter.personality}
- 背景故事: ${npcCharacter.backstory}
- 对话风格: ${npcCharacter.dialogueStyle}

游戏环境:
- 迷宫名称: ${mazeInfo.name || '玉米迷宫'}
- 迷宫难度: ${mazeInfo.difficulty || '中等'}
- 当前季节: ${gameSettings.currentSeason || '秋季'}

玩家信息:
- 玩家名称: ${playerInfo.name || '冒险者'}
- 玩家等级: ${playerInfo.level || '初级探索者'}
- 收集宝藏数: ${playerInfo.treasuresFound || 0}/${mazeInfo.totalTreasures || '未知'}

你的回复应该:
1. 保持在角色设定范围内
2. 简洁明了，每次回复不超过3句话
3. 提供有用但不会直接泄露所有迷宫秘密的信息
4. 用自然、符合角色的语气回应玩家

不要:
- 不要表现得像AI或聊天机器人
- 不要使用不符合你角色设定的现代术语
- 不要直接告诉玩家最短路径或所有宝藏位置
- 不要提及与游戏世界观不符的元素`;
};

/**
 * 使用AI模型生成NPC回复
 * @param {String} systemPrompt - 系统提示
 * @param {Array} messages - 对话消息
 * @returns {Promise<String>} 生成的回复
 */
const generateAIResponse = async (systemPrompt, messages) => {
  try {
    const formattedMessages = [
      { role: 'system', content: systemPrompt },
      ...messages.map(msg => ({
        role: msg.role === 'user' ? 'user' : 'assistant',
        content: msg.content
      }))
    ];
    
    const response = await axios.post(
      config.AI_MODEL_ENDPOINT,
      {
        model: config.AI_MODEL_NAME,
        messages: formattedMessages,
        temperature: 0.7,
        max_tokens: 150
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${config.AI_MODEL_API_KEY}`
        },
        timeout: MODEL_TIMEOUT
      }
    );
    
    if (response.data && response.data.choices && response.data.choices.length > 0) {
      return response.data.choices[0].message.content.trim();
    }
    
    throw new Error('AI模型未返回有效回复');
  } catch (error) {
    logger.error('AI回复生成失败:', error);
    
    // 返回备用回复
    return '对不起，我现在有点忙。请稍后再和我交谈。';
  }
};

/**
 * 从缓存中获取相似问题的回复
 * @param {String} npcType - NPC类型
 * @param {String} userMessage - 用户消息
 * @returns {Promise<String|null>} 缓存的回复或null
 */
const getCachedResponse = async (npcType, userMessage) => {
  try {
    const redisClient = getRedisClient();
    
    // 生成请求的哈希值
    const requestHash = generateResponseHash(npcType, userMessage);
    const cacheKey = `npc:response:${npcType}:${requestHash}`;
    
    const cachedResponse = await redisClient.get(cacheKey);
    if (cachedResponse) {
      logger.debug(`使用缓存的NPC回复: ${cacheKey}`);
      return cachedResponse;
    }
    
    return null;
  } catch (error) {
    logger.warn('获取缓存回复失败:', error);
    return null;
  }
};

/**
 * 缓存NPC回复
 * @param {String} npcType - NPC类型
 * @param {String} userMessage - 用户消息
 * @param {String} response - NPC回复
 * @returns {Promise<Boolean>} 是否成功
 */
const cacheResponse = async (npcType, userMessage, response) => {
  try {
    const redisClient = getRedisClient();
    
    // 生成请求的哈希值
    const requestHash = generateResponseHash(npcType, userMessage);
    const cacheKey = `npc:response:${npcType}:${requestHash}`;
    
    // 缓存有效期7天
    await redisClient.set(cacheKey, response);
    await redisClient.expire(cacheKey, 7 * 24 * 60 * 60);
    
    return true;
  } catch (error) {
    logger.warn('缓存NPC回复失败:', error);
    return false;
  }
};

/**
 * 分析用户消息情感和意图
 * @param {String} message - 用户消息
 * @returns {Object} 分析结果
 */
const analyzeUserMessage = (message) => {
  // 简化的意图和情感分析
  const analysis = {
    intent: 'unknown',
    sentiment: 'neutral',
    isQuestion: false,
    keywords: []
  };
  
  // 判断是否是问题
  analysis.isQuestion = message.includes('?') || message.includes('？') || 
                        message.includes('什么') || message.includes('怎么') || 
                        message.includes('如何') || message.includes('哪里');
  
  // 简单的意图识别
  if (message.includes('你好') || message.includes('嗨') || message.includes('早上好') || 
      message.includes('下午好') || message.includes('晚上好')) {
    analysis.intent = 'greeting';
  } else if (message.includes('再见') || message.includes('拜拜') || message.includes('告辞')) {
    analysis.intent = 'farewell';
  } else if (message.includes('谢谢') || message.includes('感谢')) {
    analysis.intent = 'gratitude';
  } else if (message.includes('宝藏') || message.includes('藏品') || message.includes('奖励')) {
    analysis.intent = 'treasure_info';
  } else if (message.includes('路') || message.includes('方向') || message.includes('走') || 
            message.includes('迷路') || message.includes('出口')) {
    analysis.intent = 'navigation_help';
  } else if (message.includes('提示') || message.includes('帮助') || message.includes('帮我')) {
    analysis.intent = 'help_request';
  } else if (analysis.isQuestion) {
    analysis.intent = 'question';
  }
  
  // 简单的情感分析
  if (message.includes('生气') || message.includes('烦') || message.includes('讨厌') || 
      message.includes('滚') || message.includes('笨蛋') || message.includes('傻')) {
    analysis.sentiment = 'negative';
  } else if (message.includes('喜欢') || message.includes('棒') || message.includes('厉害') || 
            message.includes('好') || message.includes('智能') || message.includes('聪明')) {
    analysis.sentiment = 'positive';
  }
  
  // 提取关键词
  const potentialKeywords = [
    '宝藏', '地图', '提示', '出口', '入口', '奖励', '帮助', 
    '迷宫', '玉米', '路径', '任务', '怪物', '游戏'
  ];
  
  potentialKeywords.forEach(keyword => {
    if (message.includes(keyword)) {
      analysis.keywords.push(keyword);
    }
  });
  
  return analysis;
};

/**
 * 处理用户与NPC的对话
 * @param {String} userId - 用户ID
 * @param {String} npcType - NPC类型
 * @param {String} message - 用户消息
 * @param {Object} gameContext - 游戏上下文
 * @returns {Promise<Object>} 对话结果
 */
const handleNpcConversation = async (userId, npcType, message, gameContext) => {
  try {
    // 验证NPC类型
    if (!NPC_CHARACTERS[npcType]) {
      throw createError(`无效的NPC类型: ${npcType}`, 400);
    }
    
    const npcCharacter = NPC_CHARACTERS[npcType];
    const npcId = `${npcType}_${gameContext.mazeInfo.id || 'default'}`;
    
    // 分析用户消息
    const analysis = analyzeUserMessage(message);
    logger.debug(`用户消息分析: ${JSON.stringify(analysis)}`);
    
    // 尝试从缓存获取相似问题的回复
    const cachedResponse = await getCachedResponse(npcType, message);
    if (cachedResponse && analysis.intent !== 'greeting' && analysis.intent !== 'farewell') {
      // 简单的问候和告别每次都应该生成新的回复，体现互动性
      return {
        npcId,
        npcName: npcCharacter.name,
        message: cachedResponse,
        fromCache: true,
        analysis
      };
    }
    
    // 获取对话上下文
    let context = await getConversationContext(userId, npcId);
    
    // 将用户消息添加到上下文
    context = addMessageToContext(context, 'user', message);
    
    // 构建系统提示
    const systemPrompt = buildSystemPrompt(npcCharacter, gameContext);
    
    // 生成回复
    const response = await generateAIResponse(systemPrompt, context);
    
    // 将NPC回复添加到上下文
    context = addMessageToContext(context, 'assistant', response);
    
    // 保存更新后的上下文
    await saveConversationContext(userId, npcId, context);
    
    // 缓存回复（除非是问候或告别）
    if (analysis.intent !== 'greeting' && analysis.intent !== 'farewell') {
      await cacheResponse(npcType, message, response);
    }
    
    return {
      npcId,
      npcName: npcCharacter.name,
      message: response,
      fromCache: false,
      analysis
    };
  } catch (error) {
    logger.error(`NPC对话处理失败: ${userId}/${npcType}`, error);
    
    if (error.statusCode) {
      throw error;
    }
    
    throw createError('NPC对话处理失败', 500);
  }
};

/**
 * 获取NPC信息
 * @param {String} npcType - NPC类型
 * @returns {Object} NPC信息
 */
const getNpcInfo = (npcType) => {
  if (!NPC_CHARACTERS[npcType]) {
    throw createError(`无效的NPC类型: ${npcType}`, 400);
  }
  
  return {
    type: npcType,
    ...NPC_CHARACTERS[npcType]
  };
};

/**
 * 获取迷宫中的所有NPC
 * @param {String} mazeId - 迷宫ID
 * @returns {Promise<Array>} NPC列表
 */
const getMazeNpcs = async (mazeId) => {
  // 这里应该从数据库中获取迷宫NPC配置
  // 简化实现，返回默认NPC
  
  return Object.entries(NPC_CHARACTERS).map(([type, character]) => ({
    id: `${type}_${mazeId}`,
    type,
    position: { x: 0, y: 0 }, // 应该从配置中获取
    ...character
  }));
};

module.exports = {
  handleNpcConversation,
  getNpcInfo,
  getMazeNpcs,
  clearConversationContext
}; 