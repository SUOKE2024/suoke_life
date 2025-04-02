'use strict';

const path = require('path');
const fs = require('fs').promises;
const ort = require('onnxruntime-node');
const axios = require('axios');
const Redis = require('ioredis');
const knowledgeIntegrationService = require('./knowledgeIntegrationService');

// 智能体服务
class AgentService {
  constructor() {
    this.initialized = false;
    this.models = {};
    this.sessionData = new Map();
    this.integrations = {};
    this.logger = null;
    this.redis = null;
    this.config = null;
    this.fastify = null;
    this.knowledgeIntegrationService = null;
  }

  /**
   * 初始化智能体服务
   * @param {FastifyInstance} fastify Fastify实例
   */
  async initialize(fastify) {
    this.fastify = fastify;
    this.logger = fastify.log;
    this.redis = fastify.redis;
    this.config = fastify.agentConfig;
    
    this.logger.info('正在初始化索儿智能体服务...');
    
    try {
      // 初始化集成服务
      await this.initializeIntegrations(fastify);
      
      // 加载模型
      await this.loadModels();
      
      // 初始化知识集成服务
      await knowledgeIntegrationService.initialize(fastify);
      this.knowledgeIntegrationService = knowledgeIntegrationService;
      
      // 初始化完成
      this.initialized = true;
      this.logger.info('索儿智能体服务初始化完成');
      
      return true;
    } catch (error) {
      this.logger.error(`智能体服务初始化失败: ${error.message}`);
      this.logger.error(error.stack);
      return false;
    }
  }

  /**
   * 初始化与其他服务的集成
   */
  async initializeIntegrations(fastify) {
    this.logger.info('正在初始化服务集成...');
    
    // 创建HTTP客户端，包含基本认证和错误处理
    const createHttpClient = (baseUrl) => {
      const client = axios.create({
        baseURL: baseUrl,
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'Soer-Agent/1.0.0'
        }
      });
      
      // 请求拦截器（添加认证）
      client.interceptors.request.use(
        config => {
          if (process.env.AUTH_SECRET) {
            config.headers.Authorization = `Bearer ${process.env.AUTH_SECRET}`;
          }
          return config;
        },
        error => Promise.reject(error)
      );
      
      // 响应拦截器（错误处理）
      client.interceptors.response.use(
        response => response,
        error => {
          const { response } = error;
          if (response) {
            this.logger.error(`API请求失败: ${response.status} ${response.statusText} - ${response.config.url}`);
          } else {
            this.logger.error(`API请求失败: ${error.message}`);
          }
          return Promise.reject(error);
        }
      );
      
      return client;
    };
    
    // 替换配置中的环境变量占位符
    const replaceEnvVars = (url) => {
      return url.replace(/\${(\w+)}/g, (match, varName) => {
        return process.env[varName] || match;
      });
    };
    
    // 初始化各个集成服务的HTTP客户端
    const { integrations } = this.config;
    for (const [name, integration] of Object.entries(integrations)) {
      const endpoint = replaceEnvVars(integration.endpoint);
      this.integrations[name] = {
        ...integration,
        endpoint,
        client: createHttpClient(endpoint)
      };
      this.logger.info(`已配置集成服务: ${name} - ${endpoint}`);
    }
    
    // 测试连接
    for (const [name, integration] of Object.entries(this.integrations)) {
      try {
        const { client } = integration;
        const response = await client.get('/health');
        if (response.status === 200) {
          this.logger.info(`服务连接成功: ${name}`);
        } else {
          this.logger.warn(`服务连接异常: ${name} - 状态码: ${response.status}`);
        }
      } catch (error) {
        this.logger.warn(`服务连接测试失败: ${name} - ${error.message}`);
        // 不抛出错误，仍然继续初始化
      }
    }
  }

  /**
   * 加载AI模型
   */
  async loadModels() {
    this.logger.info('正在加载模型...');
    
    const { models } = this.config;
    for (const [name, model] of Object.entries(models)) {
      try {
        // 检查模型文件是否存在
        const modelPath = model.path;
        try {
          await fs.access(modelPath);
          this.logger.info(`模型文件存在: ${modelPath}`);
        } catch (error) {
          this.logger.error(`模型文件不存在: ${modelPath}`);
          continue;
        }
        
        // 创建ONNX会话
        const session = await ort.InferenceSession.create(modelPath);
        
        // 存储模型和会话
        this.models[name] = {
          ...model,
          session,
          loaded: true,
          loadTime: new Date()
        };
        
        this.logger.info(`模型加载成功: ${name} (${model.type})`);
      } catch (error) {
        this.logger.error(`模型加载失败: ${name} - ${error.message}`);
        this.logger.error(error.stack);
        
        // 记录为加载失败
        this.models[name] = {
          ...model,
          loaded: false,
          error: error.message
        };
      }
    }
    
    // 检查核心模型是否加载成功
    if (!this.models.primary?.loaded) {
      throw new Error('核心LLM模型加载失败，无法继续');
    }
  }

  /**
   * 检查服务是否已初始化
   */
  async isInitialized() {
    return this.initialized;
  }

  /**
   * 检查服务是否已就绪
   */
  async isReady() {
    // 检查服务是否已初始化并且核心模型已加载
    return this.initialized && this.models.primary?.loaded;
  }

  /**
   * 获取服务状态
   */
  async getStatus() {
    // 构建状态报告
    const modelsStatus = {};
    for (const [name, model] of Object.entries(this.models)) {
      modelsStatus[name] = {
        loaded: model.loaded,
        type: model.type,
        loadTime: model.loadTime ? model.loadTime.toISOString() : null,
        error: model.error
      };
    }
    
    // 集成服务状态
    const integrationsStatus = {};
    for (const [name, integration] of Object.entries(this.integrations)) {
      integrationsStatus[name] = {
        endpoint: integration.endpoint,
        dataTypes: integration.data_types,
        syncFrequency: integration.sync_frequency
      };
    }
    
    return {
      initialized: this.initialized,
      models: modelsStatus,
      integrations: integrationsStatus,
      activeSessions: this.sessionData.size
    };
  }

  /**
   * 处理用户消息
   * @param {string} userId 用户ID
   * @param {string} message 用户消息
   * @param {object} context 上下文信息
   */
  async processMessage(userId, message, context = {}) {
    if (!this.initialized) {
      throw new Error('智能体服务尚未初始化');
    }
    
    this.logger.info(`处理来自用户 ${userId} 的消息`);
    
    try {
      // 获取或创建会话
      const session = this.getOrCreateSession(userId);
      
      // 添加消息到历史
      session.history.push({
        role: 'user',
        content: message,
        timestamp: new Date()
      });
      
      // 合并上下文信息
      const fullContext = {
        ...session.context,
        ...context
      };
      
      // 预处理消息（意图识别等）
      const processedInput = await this.preprocessMessage(message, fullContext);
      
      // 获取相关知识和数据
      const knowledgeContext = await this.retrieveKnowledge(processedInput, fullContext);
      
      // 生成回复
      const response = await this.generateResponse(
        processedInput,
        knowledgeContext,
        session.history,
        fullContext
      );
      
      // 添加回复到历史
      session.history.push({
        role: 'assistant',
        content: response.content,
        timestamp: new Date()
      });
      
      // 保存会话
      await this.saveSession(userId, session);
      
      return response;
    } catch (error) {
      this.logger.error(`处理消息失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 检索与查询相关的知识
   * @param {string} query 用户查询
   * @param {object} context 上下文
   * @returns {object} 检索到的知识
   */
  async retrieveKnowledge(query, context = {}) {
    if (!this.initialized) {
      throw new Error('代理服务未初始化');
    }
    
    try {
      let retrievedKnowledge = {
        relevantData: [],
        sourcesUsed: [],
        timestamp: new Date().toISOString()
      };
      
      // 如果知识集成服务可用，使用它来检索知识
      if (this.knowledgeIntegrationService && this.knowledgeIntegrationService.initialized) {
        try {
          const searchOptions = {
            limit: 5,
            filters: {
              domains: ['health', 'tcm', 'nutrition', 'lifestyle', 'fitness'],
              ...context.knowledgeFilters
            }
          };
          
          const searchResults = await this.knowledgeIntegrationService.combinedSearch(query, searchOptions);
          
          if (searchResults && searchResults.combined && searchResults.combined.length > 0) {
            retrievedKnowledge.relevantData = searchResults.combined;
            retrievedKnowledge.hasKnowledgeBaseResults = !!searchResults.knowledgeBase;
            retrievedKnowledge.hasKnowledgeGraphResults = !!searchResults.knowledgeGraph;
            retrievedKnowledge.sourcesUsed.push('knowledge_integration');
          }
        } catch (error) {
          this.logger.error(`知识集成服务检索失败: ${error.message}`);
          // 继续使用其他方法进行检索
        }
      }
      
      // 使用现有的检索方法作为备选
      if (retrievedKnowledge.relevantData.length === 0) {
        // 使用现有实现
        // ... existing code for retrieveKnowledge ...
      }
      
      return retrievedKnowledge;
    } catch (error) {
      this.logger.error(`知识检索失败: ${error.message}`);
      return {
        relevantData: [],
        sourcesUsed: [],
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  // 其余方法将在其他文件中实现
}

// 导出单例
const agentService = new AgentService();
module.exports = agentService;