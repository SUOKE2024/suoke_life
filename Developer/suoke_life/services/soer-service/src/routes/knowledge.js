'use strict';

const knowledgeIntegrationService = require('../services/knowledgeIntegrationService');
const agentService = require('../services/agentService');

/**
 * 知识图谱与知识库相关API路由
 * @param {FastifyInstance} fastify Fastify实例
 * @param {Object} opts 配置选项
 */
module.exports = async function (fastify, opts) {
  /**
   * 搜索知识
   */
  fastify.post('/search', {
    schema: {
      description: '搜索知识库和知识图谱',
      tags: ['知识'],
      summary: '使用组合搜索从知识库和知识图谱中检索知识',
      body: {
        type: 'object',
        required: ['query'],
        properties: {
          query: { type: 'string', description: '搜索查询文本' },
          limit: { type: 'integer', default: 10, description: '结果数量限制' },
          filters: { 
            type: 'object', 
            properties: {
              domains: { 
                type: 'array', 
                items: { type: 'string' },
                description: '领域过滤器'
              }
            },
            description: '搜索过滤器'
          }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            query: { type: 'string', description: '原始查询' },
            combined: { 
              type: 'array', 
              items: { 
                type: 'object',
                properties: {
                  id: { type: 'string', description: '知识条目ID' },
                  type: { type: 'string', description: '条目类型' },
                  title: { type: 'string', description: '标题' },
                  content: { type: 'string', description: '内容' },
                  source: { type: 'string', description: '来源' },
                  relevance: { type: 'number', description: '相关性评分' }
                }
              },
              description: '组合搜索结果' 
            },
            timestamp: { type: 'string', format: 'date-time', description: '搜索时间戳' }
          }
        },
        400: {
          type: 'object',
          properties: {
            statusCode: { type: 'integer' },
            error: { type: 'string' },
            message: { type: 'string' }
          }
        },
        500: {
          type: 'object',
          properties: {
            statusCode: { type: 'integer' },
            error: { type: 'string' },
            message: { type: 'string' }
          }
        }
      }
    },
    handler: async (request, reply) => {
      try {
        // 确保知识集成服务已初始化
        if (!knowledgeIntegrationService.initialized) {
          return reply.code(503).send({
            statusCode: 503,
            error: 'Service Unavailable',
            message: '知识集成服务尚未初始化'
          });
        }

        const { query, limit = 10, filters = {} } = request.body;
        
        // 执行组合搜索
        const searchResults = await knowledgeIntegrationService.combinedSearch(query, {
          limit,
          filters
        });
        
        // 返回结果
        return reply.send(searchResults);
      } catch (error) {
        request.log.error(`知识搜索失败: ${error.message}`);
        return reply.code(500).send({
          statusCode: 500,
          error: 'Internal Server Error',
          message: `知识搜索失败: ${error.message}`
        });
      }
    }
  });

  /**
   * 获取知识条目详情
   */
  fastify.get('/item/:id', {
    schema: {
      description: '获取知识条目详情',
      tags: ['知识'],
      summary: '获取特定知识条目的详细信息',
      params: {
        type: 'object',
        required: ['id'],
        properties: {
          id: { type: 'string', description: '知识条目ID' }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            id: { type: 'string', description: '知识条目ID' },
            title: { type: 'string', description: '标题' },
            content: { type: 'string', description: '内容' },
            metadata: { 
              type: 'object',
              description: '元数据'
            },
            timestamp: { type: 'string', format: 'date-time', description: '时间戳' }
          }
        },
        404: {
          type: 'object',
          properties: {
            statusCode: { type: 'integer' },
            error: { type: 'string' },
            message: { type: 'string' }
          }
        },
        500: {
          type: 'object',
          properties: {
            statusCode: { type: 'integer' },
            error: { type: 'string' },
            message: { type: 'string' }
          }
        }
      }
    },
    handler: async (request, reply) => {
      try {
        // 确保知识集成服务已初始化
        if (!knowledgeIntegrationService.initialized) {
          return reply.code(503).send({
            statusCode: 503,
            error: 'Service Unavailable',
            message: '知识集成服务尚未初始化'
          });
        }

        const { id } = request.params;
        
        // 获取知识条目
        try {
          const item = await knowledgeIntegrationService.getKnowledgeItem(id);
          return reply.send(item);
        } catch (error) {
          request.log.error(`获取知识条目失败: ${error.message}`);
          return reply.code(404).send({
            statusCode: 404,
            error: 'Not Found',
            message: `找不到ID为${id}的知识条目`
          });
        }
      } catch (error) {
        request.log.error(`知识条目获取失败: ${error.message}`);
        return reply.code(500).send({
          statusCode: 500,
          error: 'Internal Server Error',
          message: `知识条目获取失败: ${error.message}`
        });
      }
    }
  });
  
  /**
   * 获取知识图谱节点
   */
  fastify.get('/node/:id', {
    schema: {
      description: '获取知识图谱节点',
      tags: ['知识'],
      summary: '获取特定知识图谱节点的详细信息',
      params: {
        type: 'object',
        required: ['id'],
        properties: {
          id: { type: 'string', description: '节点ID' }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            id: { type: 'string', description: '节点ID' },
            name: { type: 'string', description: '节点名称' },
            type: { type: 'string', description: '节点类型' },
            description: { type: 'string', description: '节点描述' },
            properties: { 
              type: 'object',
              description: '节点属性'
            },
            timestamp: { type: 'string', format: 'date-time', description: '时间戳' }
          }
        },
        404: {
          type: 'object',
          properties: {
            statusCode: { type: 'integer' },
            error: { type: 'string' },
            message: { type: 'string' }
          }
        },
        500: {
          type: 'object',
          properties: {
            statusCode: { type: 'integer' },
            error: { type: 'string' },
            message: { type: 'string' }
          }
        }
      }
    },
    handler: async (request, reply) => {
      try {
        // 确保知识集成服务已初始化
        if (!knowledgeIntegrationService.initialized) {
          return reply.code(503).send({
            statusCode: 503,
            error: 'Service Unavailable',
            message: '知识集成服务尚未初始化'
          });
        }

        const { id } = request.params;
        
        // 获取图谱节点
        try {
          const node = await knowledgeIntegrationService.getGraphNode(id);
          return reply.send(node);
        } catch (error) {
          request.log.error(`获取图谱节点失败: ${error.message}`);
          return reply.code(404).send({
            statusCode: 404,
            error: 'Not Found',
            message: `找不到ID为${id}的图谱节点`
          });
        }
      } catch (error) {
        request.log.error(`图谱节点获取失败: ${error.message}`);
        return reply.code(500).send({
          statusCode: 500,
          error: 'Internal Server Error',
          message: `图谱节点获取失败: ${error.message}`
        });
      }
    }
  });
  
  /**
   * 获取关系路径
   */
  fastify.get('/path', {
    schema: {
      description: '获取两个节点之间的关系路径',
      tags: ['知识'],
      summary: '在知识图谱中查找两个节点之间的关系路径',
      querystring: {
        type: 'object',
        required: ['from', 'to'],
        properties: {
          from: { type: 'string', description: '起始节点ID' },
          to: { type: 'string', description: '目标节点ID' },
          maxDepth: { type: 'integer', default: 3, description: '最大路径深度' }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            from: { type: 'string', description: '起始节点ID' },
            to: { type: 'string', description: '目标节点ID' },
            paths: { 
              type: 'array', 
              items: {
                type: 'array',
                items: {
                  type: 'object',
                  properties: {
                    node: { type: 'string', description: '节点ID' },
                    relation: { type: 'string', description: '关系类型' }
                  }
                }
              },
              description: '关系路径' 
            },
            timestamp: { type: 'string', format: 'date-time', description: '时间戳' }
          }
        },
        404: {
          type: 'object',
          properties: {
            statusCode: { type: 'integer' },
            error: { type: 'string' },
            message: { type: 'string' }
          }
        },
        500: {
          type: 'object',
          properties: {
            statusCode: { type: 'integer' },
            error: { type: 'string' },
            message: { type: 'string' }
          }
        }
      }
    },
    handler: async (request, reply) => {
      try {
        // 确保知识集成服务已初始化
        if (!knowledgeIntegrationService.initialized) {
          return reply.code(503).send({
            statusCode: 503,
            error: 'Service Unavailable',
            message: '知识集成服务尚未初始化'
          });
        }

        const { from, to, maxDepth = 3 } = request.query;
        
        // 获取关系路径
        try {
          const paths = await knowledgeIntegrationService.getRelationshipPath(from, to, { maxDepth });
          return reply.send(paths);
        } catch (error) {
          request.log.error(`获取关系路径失败: ${error.message}`);
          return reply.code(404).send({
            statusCode: 404,
            error: 'Not Found',
            message: `找不到节点${from}和${to}之间的关系路径`
          });
        }
      } catch (error) {
        request.log.error(`关系路径获取失败: ${error.message}`);
        return reply.code(500).send({
          statusCode: 500,
          error: 'Internal Server Error',
          message: `关系路径获取失败: ${error.message}`
        });
      }
    }
  });
  
  /**
   * 知识图谱可视化数据
   */
  fastify.get('/visualization', {
    schema: {
      description: '获取知识图谱可视化数据',
      tags: ['知识'],
      summary: '获取用于可视化的知识图谱数据',
      querystring: {
        type: 'object',
        required: ['centralNode'],
        properties: {
          centralNode: { type: 'string', description: '中心节点ID或查询' },
          depth: { type: 'integer', default: 2, description: '图谱遍历深度' },
          limit: { type: 'integer', default: 50, description: '节点数量限制' }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            nodes: { 
              type: 'array', 
              items: {
                type: 'object',
                properties: {
                  id: { type: 'string', description: '节点ID' },
                  name: { type: 'string', description: '节点名称' },
                  type: { type: 'string', description: '节点类型' },
                  properties: { type: 'object', description: '节点属性' }
                }
              },
              description: '图谱节点' 
            },
            edges: { 
              type: 'array', 
              items: {
                type: 'object',
                properties: {
                  source: { type: 'string', description: '源节点ID' },
                  target: { type: 'string', description: '目标节点ID' },
                  type: { type: 'string', description: '关系类型' },
                  properties: { type: 'object', description: '关系属性' }
                }
              },
              description: '图谱边' 
            },
            centralNode: { type: 'string', description: '中心节点ID' },
            timestamp: { type: 'string', format: 'date-time', description: '时间戳' }
          }
        },
        400: {
          type: 'object',
          properties: {
            statusCode: { type: 'integer' },
            error: { type: 'string' },
            message: { type: 'string' }
          }
        },
        500: {
          type: 'object',
          properties: {
            statusCode: { type: 'integer' },
            error: { type: 'string' },
            message: { type: 'string' }
          }
        }
      }
    },
    handler: async (request, reply) => {
      try {
        // 确保知识集成服务已初始化
        if (!knowledgeIntegrationService.initialized) {
          return reply.code(503).send({
            statusCode: 503,
            error: 'Service Unavailable',
            message: '知识集成服务尚未初始化'
          });
        }

        const { centralNode, depth = 2, limit = 50 } = request.query;
        
        // 获取可视化数据
        try {
          const visualizationData = await knowledgeIntegrationService.getVisualizationData(centralNode, {
            depth,
            limit
          });
          return reply.send(visualizationData);
        } catch (error) {
          request.log.error(`获取可视化数据失败: ${error.message}`);
          return reply.code(400).send({
            statusCode: 400,
            error: 'Bad Request',
            message: `获取可视化数据失败: ${error.message}`
          });
        }
      } catch (error) {
        request.log.error(`知识图谱可视化失败: ${error.message}`);
        return reply.code(500).send({
          statusCode: 500,
          error: 'Internal Server Error',
          message: `知识图谱可视化失败: ${error.message}`
        });
      }
    }
  });
};