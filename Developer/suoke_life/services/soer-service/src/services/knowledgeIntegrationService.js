'use strict';

/**
 * 知识集成服务
 * 提供与知识库、知识图谱的交互功能
 */

const axios = require('axios');

class KnowledgeIntegrationService {
  constructor() {
    this.initialized = false;
    this.config = null;
    this.logger = null;
    this.knowledgeBaseClient = null;
    this.knowledgeGraphClient = null;
  }

  /**
   * 初始化知识集成服务
   * @param {object} fastify Fastify实例
   */
  async initialize(fastify) {
    this.logger = fastify.log;
    this.logger.info('正在初始化知识集成服务...');

    try {
      // 设置知识库客户端
      if (process.env.KNOWLEDGE_BASE_URL) {
        this.knowledgeBaseClient = axios.create({
          baseURL: process.env.KNOWLEDGE_BASE_URL,
          timeout: 10000,
          headers: {
            'Content-Type': 'application/json',
            'User-Agent': 'Soer-Agent/1.0.0'
          }
        });
        
        // 请求拦截器（添加认证）
        this.knowledgeBaseClient.interceptors.request.use(
          config => {
            if (process.env.AUTH_SECRET) {
              config.headers.Authorization = `Bearer ${process.env.AUTH_SECRET}`;
            }
            return config;
          },
          error => Promise.reject(error)
        );
        
        this.logger.info('知识库客户端已配置');
      }

      // 设置知识图谱客户端
      if (process.env.KNOWLEDGE_GRAPH_URL) {
        this.knowledgeGraphClient = axios.create({
          baseURL: process.env.KNOWLEDGE_GRAPH_URL,
          timeout: 10000,
          headers: {
            'Content-Type': 'application/json',
            'User-Agent': 'Soer-Agent/1.0.0'
          }
        });
        
        // 请求拦截器（添加认证）
        this.knowledgeGraphClient.interceptors.request.use(
          config => {
            if (process.env.AUTH_SECRET) {
              config.headers.Authorization = `Bearer ${process.env.AUTH_SECRET}`;
            }
            return config;
          },
          error => Promise.reject(error)
        );
        
        this.logger.info('知识图谱客户端已配置');
      }

      // 测试连接
      const clients = [
        { name: '知识库', client: this.knowledgeBaseClient },
        { name: '知识图谱', client: this.knowledgeGraphClient }
      ];

      for (const { name, client } of clients) {
        if (client) {
          try {
            const response = await client.get('/health');
            if (response.status === 200) {
              this.logger.info(`${name}服务连接成功`);
            } else {
              this.logger.warn(`${name}服务连接异常 - 状态码: ${response.status}`);
            }
          } catch (error) {
            this.logger.warn(`${name}服务连接测试失败: ${error.message}`);
            // 不抛出错误，仍然继续初始化
          }
        }
      }

      this.initialized = true;
      this.logger.info('知识集成服务初始化完成');
      return true;
    } catch (error) {
      this.logger.error(`知识集成服务初始化失败: ${error.message}`);
      this.logger.error(error.stack);
      return false;
    }
  }

  /**
   * 从知识库中检索知识
   * @param {string} query 查询文本
   * @param {object} options 选项
   * @returns {Promise<object>} 检索结果
   */
  async searchKnowledge(query, options = {}) {
    if (!this.initialized || !this.knowledgeBaseClient) {
      throw new Error('知识集成服务未初始化或知识库客户端不可用');
    }

    try {
      const response = await this.knowledgeBaseClient.post('/api/search', {
        query,
        limit: options.limit || 5,
        filters: options.filters || {},
        type: options.type || 'semantic'
      });

      return response.data;
    } catch (error) {
      this.logger.error(`知识库检索失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 获取知识条目详情
   * @param {string} id 知识条目ID
   * @returns {Promise<object>} 知识条目详情
   */
  async getKnowledgeItem(id) {
    if (!this.initialized || !this.knowledgeBaseClient) {
      throw new Error('知识集成服务未初始化或知识库客户端不可用');
    }

    try {
      const response = await this.knowledgeBaseClient.get(`/api/items/${id}`);
      return response.data;
    } catch (error) {
      this.logger.error(`获取知识条目失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 从知识图谱中查询节点
   * @param {string} query 查询文本
   * @param {object} options 选项
   * @returns {Promise<object>} 查询结果
   */
  async queryKnowledgeGraph(query, options = {}) {
    if (!this.initialized || !this.knowledgeGraphClient) {
      throw new Error('知识集成服务未初始化或知识图谱客户端不可用');
    }

    try {
      const response = await this.knowledgeGraphClient.post('/api/query', {
        query,
        limit: options.limit || 10,
        depth: options.depth || 2,
        filters: options.filters || {}
      });

      return response.data;
    } catch (error) {
      this.logger.error(`知识图谱查询失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 获取知识图谱节点详情
   * @param {string} id 节点ID
   * @returns {Promise<object>} 节点详情
   */
  async getGraphNode(id) {
    if (!this.initialized || !this.knowledgeGraphClient) {
      throw new Error('知识集成服务未初始化或知识图谱客户端不可用');
    }

    try {
      const response = await this.knowledgeGraphClient.get(`/api/nodes/${id}`);
      return response.data;
    } catch (error) {
      this.logger.error(`获取图谱节点失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 获取节点之间的关系路径
   * @param {string} fromId 起始节点ID
   * @param {string} toId 目标节点ID
   * @param {object} options 选项
   * @returns {Promise<object>} 关系路径
   */
  async getRelationshipPath(fromId, toId, options = {}) {
    if (!this.initialized || !this.knowledgeGraphClient) {
      throw new Error('知识集成服务未初始化或知识图谱客户端不可用');
    }

    try {
      const response = await this.knowledgeGraphClient.get('/api/relationships/path', {
        params: {
          from: fromId,
          to: toId,
          maxDepth: options.maxDepth || 3
        }
      });

      return response.data;
    } catch (error) {
      this.logger.error(`获取关系路径失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 根据类型获取知识图谱节点
   * @param {string} type 节点类型
   * @param {object} options 选项
   * @returns {Promise<object>} 节点列表
   */
  async getNodesByType(type, options = {}) {
    if (!this.initialized || !this.knowledgeGraphClient) {
      throw new Error('知识集成服务未初始化或知识图谱客户端不可用');
    }

    try {
      const response = await this.knowledgeGraphClient.get('/api/nodes', {
        params: {
          type,
          limit: options.limit || 20,
          offset: options.offset || 0
        }
      });

      return response.data;
    } catch (error) {
      this.logger.error(`按类型获取节点失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 获取用于可视化的图谱数据
   * @param {string} centralNode 中心节点ID或查询
   * @param {object} options 选项
   * @returns {Promise<object>} 可视化数据
   */
  async getVisualizationData(centralNode, options = {}) {
    if (!this.initialized || !this.knowledgeGraphClient) {
      throw new Error('知识集成服务未初始化或知识图谱客户端不可用');
    }

    try {
      const response = await this.knowledgeGraphClient.get('/api/visualization', {
        params: {
          centralNode,
          depth: options.depth || 2,
          limit: options.limit || 50
        }
      });

      return response.data;
    } catch (error) {
      this.logger.error(`获取可视化数据失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 组合搜索（知识库+知识图谱）
   * @param {string} query 查询文本
   * @param {object} options 选项
   * @returns {Promise<object>} 组合结果
   */
  async combinedSearch(query, options = {}) {
    if (!this.initialized) {
      throw new Error('知识集成服务未初始化');
    }

    try {
      const results = {
        query,
        knowledgeBase: null,
        knowledgeGraph: null,
        combined: [],
        timestamp: new Date().toISOString()
      };

      // 并行执行查询
      const searchPromises = [];

      // 知识库搜索
      if (this.knowledgeBaseClient) {
        searchPromises.push(
          this.searchKnowledge(query, options)
            .then(data => {
              results.knowledgeBase = data;
              return data;
            })
            .catch(error => {
              this.logger.error(`知识库搜索失败: ${error.message}`);
              return null;
            })
        );
      }

      // 知识图谱查询
      if (this.knowledgeGraphClient) {
        searchPromises.push(
          this.queryKnowledgeGraph(query, options)
            .then(data => {
              results.knowledgeGraph = data;
              return data;
            })
            .catch(error => {
              this.logger.error(`知识图谱查询失败: ${error.message}`);
              return null;
            })
        );
      }

      // 等待所有查询完成
      await Promise.all(searchPromises);

      // 组合结果
      const combined = [];

      // 添加知识库结果
      if (results.knowledgeBase && results.knowledgeBase.items) {
        for (const item of results.knowledgeBase.items) {
          combined.push({
            id: item.id,
            type: 'knowledge_item',
            title: item.title,
            content: item.content,
            source: 'knowledge_base',
            relevance: item.score || 0.5
          });
        }
      }

      // 添加知识图谱结果
      if (results.knowledgeGraph && results.knowledgeGraph.nodes) {
        for (const node of results.knowledgeGraph.nodes) {
          combined.push({
            id: node.id,
            type: 'graph_node',
            title: node.name || node.id,
            content: node.description || '',
            source: 'knowledge_graph',
            relevance: node.relevance || 0.5,
            nodeType: node.type,
            properties: node.properties
          });
        }
      }

      // 根据相关性排序
      combined.sort((a, b) => b.relevance - a.relevance);

      // 限制结果数量
      results.combined = combined.slice(0, options.limit || 10);

      return results;
    } catch (error) {
      this.logger.error(`组合搜索失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 为健康洞察提供相关知识
   * @param {object} insight 健康洞察
   * @returns {Promise<object>} 增强的健康洞察
   */
  async enhanceHealthInsight(insight) {
    if (!this.initialized) {
      throw new Error('知识集成服务未初始化');
    }

    try {
      // 构建查询文本
      const query = `${insight.title} ${insight.type}`;
      
      // 执行组合搜索
      const searchResults = await this.combinedSearch(query, {
        limit: 5,
        filters: {
          domains: ['health', 'tcm', 'nutrition']
        }
      });

      // 增强洞察
      const enhancedInsight = {
        ...insight,
        relatedKnowledge: searchResults.combined,
        knowledgeContext: {
          summary: this.generateKnowledgeSummary(searchResults.combined),
          timestamp: new Date().toISOString()
        }
      };

      return enhancedInsight;
    } catch (error) {
      this.logger.error(`增强健康洞察失败: ${error.message}`);
      // 返回原始洞察，不抛出错误
      return insight;
    }
  }

  /**
   * 为生活建议提供相关知识支持
   * @param {object} recommendation 生活建议
   * @returns {Promise<object>} 增强的生活建议
   */
  async enhanceRecommendation(recommendation) {
    if (!this.initialized) {
      throw new Error('知识集成服务未初始化');
    }

    try {
      // 构建查询文本
      const query = recommendation.content;
      
      // 执行组合搜索
      const searchResults = await this.combinedSearch(query, {
        limit: 3,
        filters: {
          domains: ['lifestyle', 'tcm', 'nutrition', 'fitness']
        }
      });

      // 增强建议
      const enhancedRecommendation = {
        ...recommendation,
        knowledgeSupport: searchResults.combined,
        references: this.extractReferences(searchResults.combined)
      };

      return enhancedRecommendation;
    } catch (error) {
      this.logger.error(`增强生活建议失败: ${error.message}`);
      // 返回原始建议，不抛出错误
      return recommendation;
    }
  }

  /**
   * 生成知识摘要
   * @param {Array} knowledgeItems 知识条目
   * @returns {string} 摘要文本
   */
  generateKnowledgeSummary(knowledgeItems) {
    if (!knowledgeItems || knowledgeItems.length === 0) {
      return '没有找到相关知识。';
    }

    const keyPoints = knowledgeItems
      .slice(0, 3)
      .map(item => item.content.substring(0, 100).trim() + '...')
      .join(' ');

    return `从${knowledgeItems.length}个相关知识点中提取的关键信息：${keyPoints}`;
  }

  /**
   * 从知识条目中提取参考文献
   * @param {Array} knowledgeItems 知识条目
   * @returns {Array} 参考文献列表
   */
  extractReferences(knowledgeItems) {
    if (!knowledgeItems || knowledgeItems.length === 0) {
      return [];
    }

    return knowledgeItems.map(item => ({
      title: item.title,
      type: item.type,
      source: item.source,
      id: item.id
    }));
  }
}

module.exports = new KnowledgeIntegrationService();