'use strict';

/**
 * 智能体服务方法扩展
 * 这个文件包含AgentService类的附加方法实现
 */

// 获取AgentService实例
const agentService = require('./agentService');

/**
 * 获取或创建用户会话
 * @param {string} userId 用户ID
 */
agentService.getOrCreateSession = function(userId) {
  if (!this.sessionData.has(userId)) {
    // 创建新会话
    this.sessionData.set(userId, {
      userId,
      created: new Date(),
      lastActive: new Date(),
      history: [],
      context: {
        userData: null,
        preferences: null,
        healthData: null
      }
    });
  } else {
    // 更新最后活动时间
    const session = this.sessionData.get(userId);
    session.lastActive = new Date();
  }
  
  return this.sessionData.get(userId);
};

/**
 * 保存用户会话
 * @param {string} userId 用户ID
 * @param {object} session 会话数据
 */
agentService.saveSession = async function(userId, session) {
  // 更新内存中的会话
  this.sessionData.set(userId, session);
  
  // 如果有Redis，同时保存到Redis
  if (this.redis) {
    try {
      const sessionKey = `session:${userId}`;
      await this.redis.set(
        sessionKey,
        JSON.stringify(session),
        'EX',
        60 * 60 * 24 // 24小时过期
      );
      this.logger.debug(`会话已保存到Redis: ${sessionKey}`);
    } catch (error) {
      this.logger.error(`保存会话到Redis失败: ${error.message}`);
      // 不抛出错误，继续运行
    }
  }
};

/**
 * 预处理用户消息
 * @param {string} message 用户消息
 * @param {object} context 上下文信息
 */
agentService.preprocessMessage = async function(message, context) {
  this.logger.debug('预处理用户消息');
  
  // 基本消息清理
  let processedMessage = message.trim();
  
  // 提取意图和实体
  // 注：在实际实现中，这里应该使用NLP工具来处理
  const intent = {
    type: 'general_query',
    confidence: 0.8,
    entities: []
  };
  
  // 健康相关关键词检测
  const healthKeywords = [
    '健康', '疾病', '症状', '治疗', '体检', '饮食', '睡眠', '运动',
    '血压', '血糖', '心率', '体重', '药物', '医生', '医院'
  ];
  
  for (const keyword of healthKeywords) {
    if (processedMessage.includes(keyword)) {
      intent.type = 'health_query';
      intent.entities.push({
        type: 'health_topic',
        value: keyword
      });
    }
  }
  
  // 生活习惯关键词检测
  const lifestyleKeywords = [
    '习惯', '作息', '锻炼', '健身', '饮食', '营养', '减肥', '增重',
    '压力', '焦虑', '放松', '冥想', '瑜伽'
  ];
  
  for (const keyword of lifestyleKeywords) {
    if (processedMessage.includes(keyword)) {
      if (intent.type !== 'health_query') {
        intent.type = 'lifestyle_query';
      }
      intent.entities.push({
        type: 'lifestyle_topic',
        value: keyword
      });
    }
  }
  
  // 如果有意图分类器模型，使用模型进行更精确的分类
  if (this.models.lifestyle_classifier?.loaded) {
    try {
      const result = await this.classifyMessageIntent(processedMessage);
      if (result.confidence > 0.6) {
        intent.type = result.type;
        intent.confidence = result.confidence;
        // 合并实体
        for (const entity of result.entities) {
          if (!intent.entities.find(e => e.type === entity.type && e.value === entity.value)) {
            intent.entities.push(entity);
          }
        }
      }
    } catch (error) {
      this.logger.error(`意图分类失败: ${error.message}`);
      // 继续使用基本分类结果
    }
  }
  
  return {
    original: message,
    processed: processedMessage,
    intent,
    timestamp: new Date()
  };
};

/**
 * 分类消息意图
 * @param {string} message 用户消息
 */
agentService.classifyMessageIntent = async function(message) {
  // 这里应该实现使用分类器模型进行意图分类
  // 以下是一个模拟实现
  return {
    type: 'general_query',
    confidence: 0.8,
    entities: []
  };
};

/**
 * 检索相关知识
 * @param {object} processedInput 处理后的输入
 * @param {object} context 上下文信息
 */
agentService.retrieveKnowledge = async function(processedInput, context) {
  this.logger.debug('检索相关知识');
  
  // 初始化知识上下文
  const knowledgeContext = {
    relevantInfo: [],
    healthData: null,
    recommendations: []
  };
  
  // 使用embedding模型和RAG服务检索相关知识
  if (this.models.embedding?.loaded && this.integrations.rag_service) {
    try {
      const ragClient = this.integrations.rag_service.client;
      const response = await ragClient.post('/query', {
        query: processedInput.processed,
        intent: processedInput.intent.type,
        limit: 5
      });
      
      if (response.status === 200 && response.data.results) {
        knowledgeContext.relevantInfo = response.data.results;
      }
    } catch (error) {
      this.logger.error(`RAG检索失败: ${error.message}`);
      // 失败时不抛出错误，继续执行
    }
  }
  
  // 如果是健康相关查询，获取用户健康数据
  if (
    processedInput.intent.type === 'health_query' && 
    this.integrations.health_service && 
    context.userData?.userId
  ) {
    try {
      const healthClient = this.integrations.health_service.client;
      const response = await healthClient.get(`/users/${context.userData.userId}/health-data/summary`);
      
      if (response.status === 200) {
        knowledgeContext.healthData = response.data;
      }
    } catch (error) {
      this.logger.error(`健康数据获取失败: ${error.message}`);
      // 失败时不抛出错误，继续执行
    }
  }
  
  // 生成推荐
  if (this.models.recommendation_engine?.loaded) {
    try {
      // 这里应该实现使用推荐引擎模型生成推荐
      // 以下是模拟实现
      knowledgeContext.recommendations = [
        {
          type: 'lifestyle',
          content: '建议每天保持30分钟中等强度的身体活动',
          confidence: 0.85
        }
      ];
    } catch (error) {
      this.logger.error(`生成推荐失败: ${error.message}`);
      // 失败时不抛出错误，继续执行
    }
  }
  
  return knowledgeContext;
};

/**
 * 生成回复
 * @param {object} processedInput 处理后的输入
 * @param {object} knowledgeContext 知识上下文
 * @param {array} history 对话历史
 * @param {object} context 上下文信息
 */
agentService.generateResponse = async function(processedInput, knowledgeContext, history, context) {
  this.logger.debug('生成回复');
  
  // 构建提示信息
  let prompt = this.buildPrompt(processedInput, knowledgeContext, history, context);
  
  // 默认回复（如果生成失败）
  let content = '抱歉，我现在无法回答这个问题。请稍后再试。';
  let responseType = 'fallback';
  
  // 使用LLM生成回复
  if (this.models.primary?.loaded) {
    try {
      // 这里应该实现使用LLM模型生成回复
      // 以下是一个模拟实现
      
      // 根据意图类型生成不同的回复
      if (processedInput.intent.type === 'health_query') {
        content = '我注意到您询问了健康相关的问题。作为您的生活健康助手，我建议您保持均衡饮食和规律作息。如果有特定的健康问题，我可以提供更具针对性的建议。';
        responseType = 'health_advice';
      } else if (processedInput.intent.type === 'lifestyle_query') {
        content = '关于生活习惯，保持规律作息、适当运动、均衡饮食是健康生活的基础。您有没有特定的生活习惯想要改善呢？';
        responseType = 'lifestyle_advice';
      } else {
        content = '感谢您的问题。作为您的生活健康助手，我随时准备为您提供健康管理和生活指导。有什么特定的问题我可以帮您解答吗？';
        responseType = 'general_response';
      }
      
      // 添加推荐（如果有）
      if (knowledgeContext.recommendations && knowledgeContext.recommendations.length > 0) {
        content += '\n\n基于您的情况，我的建议是：' + knowledgeContext.recommendations[0].content;
      }
      
    } catch (error) {
      this.logger.error(`生成回复失败: ${error.message}`);
      // 使用默认回复
    }
  }
  
  return {
    content,
    type: responseType,
    intent: processedInput.intent,
    timestamp: new Date()
  };
};

/**
 * 构建提示信息
 * @param {object} processedInput 处理后的输入
 * @param {object} knowledgeContext 知识上下文
 * @param {array} history 对话历史
 * @param {object} context 上下文信息
 */
agentService.buildPrompt = function(processedInput, knowledgeContext, history, context) {
  // 构建系统提示
  let systemPrompt = `你是索儿，索克生活APP的生活健康助手智能体。你专注于用户健康管理和生活指导，提供贴心的生活健康服务。
当前时间：${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}`;

  // 添加用户信息（如果有）
  if (context.userData) {
    systemPrompt += `\n用户信息：${JSON.stringify(context.userData)}`;
  }

  // 添加健康数据（如果有）
  if (knowledgeContext.healthData) {
    systemPrompt += `\n健康数据摘要：${JSON.stringify(knowledgeContext.healthData)}`;
  }

  // 添加相关知识
  if (knowledgeContext.relevantInfo && knowledgeContext.relevantInfo.length > 0) {
    systemPrompt += '\n相关知识：\n';
    for (const info of knowledgeContext.relevantInfo) {
      systemPrompt += `- ${info.content}\n`;
    }
  }

  // 行为指导
  systemPrompt += `\n行为指南：
- 保持友好、亲切的交流风格
- 提供准确、有用的健康和生活建议
- 适当表达关心和共情
- 避免过度医疗建议，必要时推荐咨询专业医生
- 鼓励用户养成健康的生活习惯`;

  // 构建对话历史
  let conversationHistory = '';
  const recentHistory = history.slice(-10); // 最近10条消息
  for (const message of recentHistory) {
    const role = message.role === 'user' ? '用户' : '索儿';
    conversationHistory += `${role}：${message.content}\n`;
  }

  // 最终提示
  return {
    systemPrompt,
    conversationHistory,
    userQuery: processedInput.processed,
    intent: processedInput.intent.type
  };
};

module.exports = agentService;