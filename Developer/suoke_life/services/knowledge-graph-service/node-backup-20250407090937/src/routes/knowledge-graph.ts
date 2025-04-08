import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { KnowledgeGraphService } from '../domain/services/knowledge-graph-service';
import { sendSuccessResponse, sendErrorResponse, sendPaginatedResponse, sendCreatedResponse, sendNoContentResponse } from '../infrastructure/utils/response';
import { GraphNode, GraphRelationship, PaginationQuery, SearchQuery } from '../domain/interfaces/api-response.interface';

/**
 * 知识图谱相关路由
 */
export const knowledgeGraphRoutes = async (fastify: FastifyInstance) => {
  // 注册服务依赖
  const knowledgeGraphService = fastify.diContainer.resolve('knowledgeGraphService') as KnowledgeGraphService;
  
  // 节点基础模式
  const nodeSchema = {
    type: 'object',
    properties: {
      id: { type: 'string', description: '节点ID' },
      type: { type: 'string', description: '节点类型' },
      labels: { 
        type: 'array', 
        items: { type: 'string' }, 
        description: '节点标签' 
      },
      properties: { 
        type: 'object', 
        additionalProperties: true,
        description: '节点属性' 
      }
    }
  };

  // 关系基础模式
  const relationshipSchema = {
    type: 'object',
    properties: {
      id: { type: 'string', description: '关系ID' },
      type: { type: 'string', description: '关系类型' },
      startNodeId: { type: 'string', description: '起始节点ID' },
      endNodeId: { type: 'string', description: '目标节点ID' },
      properties: { 
        type: 'object', 
        additionalProperties: true,
        description: '关系属性' 
      }
    }
  };

  // 基础成功响应模式
  const successResponseSchema = {
    type: 'object',
    properties: {
      success: { type: 'boolean', example: true },
      message: { type: 'string' },
      timestamp: { type: 'string', format: 'date-time' }
    }
  };

  // 数据响应模式
  const dataResponseSchema = {
    type: 'object',
    properties: {
      success: { type: 'boolean', example: true },
      message: { type: 'string' },
      data: { type: 'object' },
      timestamp: { type: 'string', format: 'date-time' }
    }
  };

  // 错误响应模式
  const errorResponseSchema = {
    type: 'object',
    properties: {
      success: { type: 'boolean', example: false },
      message: { type: 'string' },
      error: { type: 'string' },
      statusCode: { type: 'integer' },
      timestamp: { type: 'string', format: 'date-time' }
    }
  };

  // 分页响应模式
  const paginatedResponseSchema = {
    type: 'object',
    properties: {
      success: { type: 'boolean', example: true },
      message: { type: 'string' },
      data: {
        type: 'object',
        properties: {
          items: { 
            type: 'array',
            items: { type: 'object' }
          },
          pagination: {
            type: 'object',
            properties: {
              totalItems: { type: 'integer' },
              totalPages: { type: 'integer' },
              currentPage: { type: 'integer' },
              itemsPerPage: { type: 'integer' }
            }
          }
        }
      },
      timestamp: { type: 'string', format: 'date-time' }
    }
  };

  // 获取所有节点
  fastify.get('/nodes', {
    schema: {
      description: '获取知识图谱节点列表',
      tags: ['知识图谱'],
      querystring: {
        type: 'object',
        properties: {
          page: { type: 'integer', minimum: 1, default: 1, description: '页码' },
          limit: { type: 'integer', minimum: 1, maximum: 100, default: 20, description: '每页数量' },
          sortBy: { type: 'string', default: 'created', description: '排序字段' },
          sortDirection: { type: 'string', enum: ['asc', 'desc'], default: 'desc', description: '排序方向' },
          nodeTypes: { 
            type: 'array', 
            items: { type: 'string' },
            description: '节点类型过滤' 
          },
          domains: { 
            type: 'array', 
            items: { type: 'string' },
            description: '领域过滤' 
          }
        }
      },
      response: {
        200: {
          description: '成功获取节点列表',
          ...paginatedResponseSchema,
          properties: {
            ...paginatedResponseSchema.properties,
            data: {
              type: 'object',
              properties: {
                items: { 
                  type: 'array',
                  items: nodeSchema
                },
                pagination: {
                  type: 'object',
                  properties: {
                    totalItems: { type: 'integer' },
                    totalPages: { type: 'integer' },
                    currentPage: { type: 'integer' },
                    itemsPerPage: { type: 'integer' }
                  }
                }
              }
            }
          }
        },
        400: {
          description: '请求参数错误',
          ...errorResponseSchema
        },
        500: {
          description: '服务器错误',
          ...errorResponseSchema
        }
      }
    },
    handler: async (request: FastifyRequest<{
      Querystring: PaginationQuery & {
        nodeTypes?: string[];
        domains?: string[];
      }
    }>, reply: FastifyReply) => {
      try {
        const { page = 1, limit = 20, sortBy, sortDirection, nodeTypes, domains } = request.query;
        
        const result = await knowledgeGraphService.getNodes({
          page,
          limit,
          sortBy,
          sortDirection,
          nodeTypes,
          domains
        });
        
        return sendPaginatedResponse(reply, result);
      } catch (error) {
        request.log.error(`获取节点列表失败: ${error.message}`);
        return sendErrorResponse(
          reply,
          '获取节点列表失败',
          error.name || 'InternalServerError',
          error.statusCode || 500
        );
      }
    }
  });

  // 创建节点
  fastify.post('/nodes', {
    schema: {
      description: '创建新的知识图谱节点',
      tags: ['知识图谱'],
      body: {
        type: 'object',
        required: ['type', 'properties'],
        properties: {
          type: { 
            type: 'string', 
            description: '节点类型',
            example: 'TCMHerb'
          },
          labels: { 
            type: 'array', 
            items: { type: 'string' },
            description: '节点标签',
            example: ['中药', '植物类']
          },
          properties: {
            type: 'object',
            additionalProperties: true,
            description: '节点属性',
            example: {
              name: '人参',
              pinyin: 'renshen',
              description: '补气补血药'
            }
          }
        }
      },
      security: [
        { bearerAuth: [] }
      ],
      response: {
        201: {
          description: '节点创建成功',
          ...dataResponseSchema,
          properties: {
            ...dataResponseSchema.properties,
            data: nodeSchema
          }
        },
        400: {
          description: '请求参数错误',
          ...errorResponseSchema
        },
        401: {
          description: '未授权',
          ...errorResponseSchema
        },
        500: {
          description: '服务器错误',
          ...errorResponseSchema
        }
      }
    },
    handler: async (request: FastifyRequest<{
      Body: {
        type: string;
        labels?: string[];
        properties: Record<string, any>;
      }
    }>, reply: FastifyReply) => {
      try {
        const { type, labels, properties } = request.body;
        
        // 这里可以添加用户ID或其他认证信息
        const userId = request.user?.id;
        
        const result = await knowledgeGraphService.createNode({
          type,
          labels: labels || [],
          properties,
          createdBy: userId
        });
        
        return sendCreatedResponse(reply, result);
      } catch (error) {
        request.log.error(`创建节点失败: ${error.message}`);
        return sendErrorResponse(
          reply,
          '创建节点失败',
          error.name || 'InternalServerError',
          error.statusCode || 500
        );
      }
    }
  });

  // 获取特定节点
  fastify.get('/nodes/:id', {
    schema: {
      description: '获取特定知识图谱节点',
      tags: ['知识图谱'],
      params: {
        type: 'object',
        required: ['id'],
        properties: {
          id: { 
            type: 'string', 
            description: '节点ID' 
          }
        }
      },
      querystring: {
        type: 'object',
        properties: {
          includeRelationships: { 
            type: 'boolean', 
            default: false,
            description: '是否包含关系' 
          },
          maxDepth: { 
            type: 'integer', 
            minimum: 1, 
            maximum: 5, 
            default: 1,
            description: '包含关系时的最大深度' 
          }
        }
      },
      response: {
        200: {
          description: '成功获取节点',
          ...dataResponseSchema,
          properties: {
            ...dataResponseSchema.properties,
            data: {
              type: 'object',
              properties: {
                node: nodeSchema,
                relationships: {
                  type: 'array',
                  items: relationshipSchema,
                  description: '关联的关系（如果请求包含关系）'
                }
              }
            }
          }
        },
        404: {
          description: '节点不存在',
          ...errorResponseSchema
        },
        500: {
          description: '服务器错误',
          ...errorResponseSchema
        }
      }
    },
    handler: async (request: FastifyRequest<{
      Params: {
        id: string;
      },
      Querystring: {
        includeRelationships?: boolean;
        maxDepth?: number;
      }
    }>, reply: FastifyReply) => {
      try {
        const { id } = request.params;
        const { includeRelationships = false, maxDepth = 1 } = request.query;
        
        const result = await knowledgeGraphService.getNodeById(id, {
          includeRelationships,
          maxDepth
        });
        
        if (!result) {
          return sendErrorResponse(reply, '节点不存在', 'NotFoundError', 404);
        }
        
        return sendSuccessResponse(reply, result);
      } catch (error) {
        request.log.error(`获取节点失败: ${error.message}`);
        return sendErrorResponse(
          reply,
          '获取节点失败',
          error.name || 'InternalServerError',
          error.statusCode || 500
        );
      }
    }
  });

  // 更新节点
  fastify.put('/nodes/:id', {
    schema: {
      description: '更新知识图谱节点',
      tags: ['知识图谱'],
      params: {
        type: 'object',
        required: ['id'],
        properties: {
          id: { 
            type: 'string', 
            description: '节点ID' 
          }
        }
      },
      body: {
        type: 'object',
        properties: {
          labels: { 
            type: 'array', 
            items: { type: 'string' },
            description: '节点标签' 
          },
          properties: {
            type: 'object',
            additionalProperties: true,
            description: '节点属性'
          }
        }
      },
      security: [
        { bearerAuth: [] }
      ],
      response: {
        200: {
          description: '节点更新成功',
          ...dataResponseSchema,
          properties: {
            ...dataResponseSchema.properties,
            data: nodeSchema
          }
        },
        400: {
          description: '请求参数错误',
          ...errorResponseSchema
        },
        401: {
          description: '未授权',
          ...errorResponseSchema
        },
        404: {
          description: '节点不存在',
          ...errorResponseSchema
        },
        500: {
          description: '服务器错误',
          ...errorResponseSchema
        }
      }
    },
    handler: async (request: FastifyRequest<{
      Params: {
        id: string;
      },
      Body: {
        labels?: string[];
        properties?: Record<string, any>;
      }
    }>, reply: FastifyReply) => {
      try {
        const { id } = request.params;
        const { labels, properties } = request.body;
        
        // 这里可以添加用户ID或其他认证信息
        const userId = request.user?.id;
        
        const result = await knowledgeGraphService.updateNode(id, {
          labels,
          properties,
          updatedBy: userId
        });
        
        if (!result) {
          return sendErrorResponse(reply, '节点不存在', 'NotFoundError', 404);
        }
        
        return sendSuccessResponse(reply, result);
      } catch (error) {
        request.log.error(`更新节点失败: ${error.message}`);
        return sendErrorResponse(
          reply,
          '更新节点失败',
          error.name || 'InternalServerError',
          error.statusCode || 500
        );
      }
    }
  });

  // 删除节点
  fastify.delete('/nodes/:id', {
    schema: {
      description: '删除知识图谱节点',
      tags: ['知识图谱'],
      params: {
        type: 'object',
        required: ['id'],
        properties: {
          id: { 
            type: 'string', 
            description: '节点ID' 
          }
        }
      },
      querystring: {
        type: 'object',
        properties: {
          force: { 
            type: 'boolean', 
            default: false,
            description: '是否强制删除（包括关联关系）' 
          }
        }
      },
      security: [
        { bearerAuth: [] }
      ],
      response: {
        204: {
          description: '节点删除成功',
          type: 'null'
        },
        400: {
          description: '请求参数错误',
          ...errorResponseSchema
        },
        401: {
          description: '未授权',
          ...errorResponseSchema
        },
        404: {
          description: '节点不存在',
          ...errorResponseSchema
        },
        409: {
          description: '节点存在依赖关系，无法删除',
          ...errorResponseSchema
        },
        500: {
          description: '服务器错误',
          ...errorResponseSchema
        }
      }
    },
    handler: async (request: FastifyRequest<{
      Params: {
        id: string;
      },
      Querystring: {
        force?: boolean;
      }
    }>, reply: FastifyReply) => {
      try {
        const { id } = request.params;
        const { force = false } = request.query;
        
        const result = await knowledgeGraphService.deleteNode(id, { force });
        
        if (result === false) {
          return sendErrorResponse(reply, '节点不存在', 'NotFoundError', 404);
        }
        
        return sendNoContentResponse(reply);
      } catch (error) {
        if (error.message.includes('依赖关系')) {
          return sendErrorResponse(
            reply,
            '节点存在依赖关系，无法删除',
            'ConflictError',
            409
          );
        }
        
        request.log.error(`删除节点失败: ${error.message}`);
        return sendErrorResponse(
          reply,
          '删除节点失败',
          error.name || 'InternalServerError',
          error.statusCode || 500
        );
      }
    }
  });

  // 获取所有关系
  fastify.get('/relationships', {
    schema: {
      description: '获取知识图谱关系列表',
      tags: ['知识图谱'],
      querystring: {
        type: 'object',
        properties: {
          page: { type: 'integer', minimum: 1, default: 1, description: '页码' },
          limit: { type: 'integer', minimum: 1, maximum: 100, default: 20, description: '每页数量' },
          sortBy: { type: 'string', default: 'created', description: '排序字段' },
          sortDirection: { type: 'string', enum: ['asc', 'desc'], default: 'desc', description: '排序方向' },
          types: { 
            type: 'array', 
            items: { type: 'string' },
            description: '关系类型过滤' 
          },
          startNodeId: { 
            type: 'string',
            description: '起始节点ID过滤' 
          },
          endNodeId: { 
            type: 'string',
            description: '目标节点ID过滤' 
          }
        }
      },
      response: {
        200: {
          description: '成功获取关系列表',
          ...paginatedResponseSchema,
          properties: {
            ...paginatedResponseSchema.properties,
            data: {
              type: 'object',
              properties: {
                items: { 
                  type: 'array',
                  items: relationshipSchema
                },
                pagination: {
                  type: 'object',
                  properties: {
                    totalItems: { type: 'integer' },
                    totalPages: { type: 'integer' },
                    currentPage: { type: 'integer' },
                    itemsPerPage: { type: 'integer' }
                  }
                }
              }
            }
          }
        },
        400: {
          description: '请求参数错误',
          ...errorResponseSchema
        },
        500: {
          description: '服务器错误',
          ...errorResponseSchema
        }
      }
    },
    handler: async (request: FastifyRequest<{
      Querystring: PaginationQuery & {
        types?: string[];
        startNodeId?: string;
        endNodeId?: string;
      }
    }>, reply: FastifyReply) => {
      try {
        const { page = 1, limit = 20, sortBy, sortDirection, types, startNodeId, endNodeId } = request.query;
        
        const result = await knowledgeGraphService.getRelationships({
          page,
          limit,
          sortBy,
          sortDirection,
          types,
          startNodeId,
          endNodeId
        });
        
        return sendPaginatedResponse(reply, result);
      } catch (error) {
        request.log.error(`获取关系列表失败: ${error.message}`);
        return sendErrorResponse(
          reply,
          '获取关系列表失败',
          error.name || 'InternalServerError',
          error.statusCode || 500
        );
      }
    }
  });

  // 创建关系
  fastify.post('/relationships', {
    schema: {
      description: '创建新的知识图谱关系',
      tags: ['知识图谱'],
      body: {
        type: 'object',
        required: ['type', 'startNodeId', 'endNodeId'],
        properties: {
          type: { 
            type: 'string', 
            description: '关系类型',
            example: 'TREATS'
          },
          startNodeId: { 
            type: 'string', 
            description: '起始节点ID',
            example: '123e4567-e89b-12d3-a456-426614174000'
          },
          endNodeId: { 
            type: 'string', 
            description: '目标节点ID',
            example: '123e4567-e89b-12d3-a456-426614174001'
          },
          properties: {
            type: 'object',
            additionalProperties: true,
            description: '关系属性',
            example: {
              strength: '强',
              evidence: '《本草纲目》记载',
              confidence: 0.95
            }
          }
        }
      },
      security: [
        { bearerAuth: [] }
      ],
      response: {
        201: {
          description: '关系创建成功',
          ...dataResponseSchema,
          properties: {
            ...dataResponseSchema.properties,
            data: relationshipSchema
          }
        },
        400: {
          description: '请求参数错误',
          ...errorResponseSchema
        },
        401: {
          description: '未授权',
          ...errorResponseSchema
        },
        404: {
          description: '节点不存在',
          ...errorResponseSchema
        },
        500: {
          description: '服务器错误',
          ...errorResponseSchema
        }
      }
    },
    handler: async (request: FastifyRequest<{
      Body: {
        type: string;
        startNodeId: string;
        endNodeId: string;
        properties?: Record<string, any>;
      }
    }>, reply: FastifyReply) => {
      try {
        const { type, startNodeId, endNodeId, properties } = request.body;
        
        // 这里可以添加用户ID或其他认证信息
        const userId = request.user?.id;
        
        const result = await knowledgeGraphService.createRelationship({
          type,
          startNodeId,
          endNodeId,
          properties: properties || {},
          createdBy: userId
        });
        
        return sendCreatedResponse(reply, result);
      } catch (error) {
        if (error.message.includes('节点不存在')) {
          return sendErrorResponse(reply, error.message, 'NotFoundError', 404);
        }
        
        request.log.error(`创建关系失败: ${error.message}`);
        return sendErrorResponse(
          reply,
          '创建关系失败',
          error.name || 'InternalServerError',
          error.statusCode || 500
        );
      }
    }
  });

  // 知识图谱统计
  fastify.get('/stats', {
    schema: {
      description: '获取知识图谱统计信息',
      tags: ['知识图谱'],
      querystring: {
        type: 'object',
        properties: {
          domains: { 
            type: 'array', 
            items: { type: 'string' },
            description: '领域过滤' 
          }
        }
      },
      response: {
        200: {
          description: '成功获取统计信息',
          ...dataResponseSchema,
          properties: {
            ...dataResponseSchema.properties,
            data: {
              type: 'object',
              properties: {
                nodeCount: { type: 'integer', description: '节点总数' },
                relationshipCount: { type: 'integer', description: '关系总数' },
                nodeCountByType: { 
                  type: 'object', 
                  additionalProperties: { type: 'integer' },
                  description: '按类型统计的节点数量' 
                },
                relationshipCountByType: { 
                  type: 'object', 
                  additionalProperties: { type: 'integer' },
                  description: '按类型统计的关系数量' 
                },
                nodeCountByDomain: { 
                  type: 'object', 
                  additionalProperties: { type: 'integer' },
                  description: '按领域统计的节点数量' 
                }
              }
            }
          }
        },
        500: {
          description: '服务器错误',
          ...errorResponseSchema
        }
      }
    },
    handler: async (request: FastifyRequest<{
      Querystring: {
        domains?: string[];
      }
    }>, reply: FastifyReply) => {
      try {
        const { domains } = request.query;
        
        const stats = await knowledgeGraphService.getGraphStats({ domains });
        
        return sendSuccessResponse(reply, stats);
      } catch (error) {
        request.log.error(`获取图谱统计失败: ${error.message}`);
        return sendErrorResponse(
          reply,
          '获取图谱统计失败',
          error.name || 'InternalServerError',
          error.statusCode || 500
        );
      }
    }
  });

  // 添加其他特殊查询路由
  fastify.get('/query/path', {
    schema: {
      description: '查找两个节点之间的路径',
      tags: ['知识图谱'],
      querystring: {
        type: 'object',
        required: ['startNodeId', 'endNodeId'],
        properties: {
          startNodeId: { 
            type: 'string', 
            description: '起始节点ID' 
          },
          endNodeId: { 
            type: 'string', 
            description: '目标节点ID' 
          },
          maxDepth: { 
            type: 'integer', 
            minimum: 1, 
            maximum: 10, 
            default: 5,
            description: '最大路径深度' 
          },
          relationshipTypes: { 
            type: 'array', 
            items: { type: 'string' },
            description: '关系类型过滤' 
          }
        }
      },
      response: {
        200: {
          description: '成功获取路径',
          ...dataResponseSchema,
          properties: {
            ...dataResponseSchema.properties,
            data: {
              type: 'object',
              properties: {
                paths: {
                  type: 'array',
                  items: {
                    type: 'object',
                    properties: {
                      nodes: {
                        type: 'array',
                        items: nodeSchema
                      },
                      relationships: {
                        type: 'array',
                        items: relationshipSchema
                      },
                      length: { type: 'integer' }
                    }
                  }
                },
                count: { type: 'integer' }
              }
            }
          }
        },
        404: {
          description: '节点不存在或路径不存在',
          ...errorResponseSchema
        },
        500: {
          description: '服务器错误',
          ...errorResponseSchema
        }
      }
    },
    handler: async (request: FastifyRequest<{
      Querystring: {
        startNodeId: string;
        endNodeId: string;
        maxDepth?: number;
        relationshipTypes?: string[];
      }
    }>, reply: FastifyReply) => {
      try {
        const { startNodeId, endNodeId, maxDepth = 5, relationshipTypes } = request.query;
        
        const paths = await knowledgeGraphService.findPaths(startNodeId, endNodeId, {
          maxDepth,
          relationshipTypes
        });
        
        if (paths.length === 0) {
          return sendSuccessResponse(reply, { paths: [], count: 0 }, '未找到路径');
        }
        
        return sendSuccessResponse(reply, {
          paths,
          count: paths.length
        });
      } catch (error) {
        if (error.message.includes('节点不存在')) {
          return sendErrorResponse(reply, error.message, 'NotFoundError', 404);
        }
        
        request.log.error(`查找路径失败: ${error.message}`);
        return sendErrorResponse(
          reply,
          '查找路径失败',
          error.name || 'InternalServerError',
          error.statusCode || 500
        );
      }
    }
  });
};