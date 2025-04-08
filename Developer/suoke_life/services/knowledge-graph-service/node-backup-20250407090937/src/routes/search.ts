import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { SearchService } from '../domain/services/search-service';
import { sendSuccessResponse, sendErrorResponse, sendPaginatedResponse } from '../infrastructure/utils/response';
import { PaginationQuery, SearchQuery } from '../domain/interfaces/api-response.interface';

/**
 * 知识图谱搜索相关路由
 */
export const searchRoutes = async (fastify: FastifyInstance) => {
  // 注册服务依赖
  const searchService = fastify.diContainer.resolve('searchService') as SearchService;
  
  // 响应模式
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
      },
      score: { type: 'number', description: '搜索相关性得分' }
    }
  };

  // 关键词搜索
  fastify.get('/', {
    schema: {
      description: '对知识图谱进行关键词搜索',
      tags: ['搜索'],
      querystring: {
        type: 'object',
        required: ['query'],
        properties: {
          query: { 
            type: 'string', 
            description: '搜索关键词',
            example: '人参 功效'
          },
          page: { 
            type: 'integer', 
            minimum: 1, 
            default: 1,
            description: '页码' 
          },
          limit: { 
            type: 'integer', 
            minimum: 1, 
            maximum: 100, 
            default: 20,
            description: '每页数量' 
          },
          fields: { 
            type: 'array', 
            items: { type: 'string' },
            description: '搜索字段限制' 
          },
          nodeTypes: { 
            type: 'array', 
            items: { type: 'string' },
            description: '节点类型过滤' 
          },
          fuzzy: { 
            type: 'boolean', 
            default: true,
            description: '是否模糊匹配' 
          },
          threshold: { 
            type: 'number', 
            minimum: 0, 
            maximum: 1, 
            default: 0.6,
            description: '搜索相似度阈值' 
          }
        }
      },
      response: {
        200: {
          description: '搜索结果',
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
                },
                meta: {
                  type: 'object',
                  properties: {
                    query: { type: 'string' },
                    processingTimeMs: { type: 'number' }
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
      Querystring: SearchQuery & PaginationQuery & {
        nodeTypes?: string[];
      }
    }>, reply: FastifyReply) => {
      try {
        const { 
          query, 
          page = 1, 
          limit = 20, 
          fields, 
          nodeTypes, 
          fuzzy = true, 
          threshold = 0.6 
        } = request.query;
        
        if (!query) {
          return sendErrorResponse(reply, '搜索关键词不能为空', 'ValidationError', 400);
        }
        
        const startTime = Date.now();
        const result = await searchService.search(query, {
          page,
          limit,
          fields,
          nodeTypes,
          fuzzy,
          threshold
        });
        const processingTimeMs = Date.now() - startTime;
        
        // 添加元数据
        result.meta = {
          query,
          processingTimeMs
        };
        
        return sendPaginatedResponse(reply, result);
      } catch (error) {
        request.log.error(`搜索失败: ${error.message}`);
        return sendErrorResponse(
          reply,
          '搜索失败',
          error.name || 'InternalServerError',
          error.statusCode || 500
        );
      }
    }
  });

  // 向量相似度搜索
  fastify.post('/vector', {
    schema: {
      description: '使用向量相似度在知识图谱中进行语义搜索',
      tags: ['搜索'],
      body: {
        type: 'object',
        required: ['text'],
        properties: {
          text: { 
            type: 'string', 
            description: '搜索文本',
            example: '高血压患者适合吃的食物'
          },
          vector: { 
            type: 'array', 
            items: { type: 'number' },
            description: '自定义向量（可选，如不提供则服务器会计算文本向量）' 
          },
          limit: { 
            type: 'integer', 
            minimum: 1, 
            maximum: 100, 
            default: 20,
            description: '返回结果数量' 
          },
          nodeTypes: { 
            type: 'array', 
            items: { type: 'string' },
            description: '节点类型过滤' 
          },
          threshold: { 
            type: 'number', 
            minimum: 0, 
            maximum: 1, 
            default: 0.7,
            description: '相似度阈值' 
          }
        }
      },
      response: {
        200: {
          description: '向量搜索结果',
          ...dataResponseSchema,
          properties: {
            ...dataResponseSchema.properties,
            data: {
              type: 'object',
              properties: {
                results: {
                  type: 'array',
                  items: {
                    type: 'object',
                    properties: {
                      node: nodeSchema,
                      similarity: { type: 'number' }
                    }
                  }
                },
                meta: {
                  type: 'object',
                  properties: {
                    query: { type: 'string' },
                    vectorDimension: { type: 'integer' },
                    processingTimeMs: { type: 'number' }
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
      Body: {
        text: string;
        vector?: number[];
        limit?: number;
        nodeTypes?: string[];
        threshold?: number;
      }
    }>, reply: FastifyReply) => {
      try {
        const startTime = Date.now();
        const { text, vector, limit = 20, nodeTypes, threshold = 0.7 } = request.body;
        
        if (!text && !vector) {
          return sendErrorResponse(reply, '必须提供搜索文本或向量', 'ValidationError', 400);
        }
        
        const result = await searchService.vectorSearch(text, {
          vector,
          limit,
          nodeTypes,
          threshold
        });
        
        const processingTimeMs = Date.now() - startTime;
        
        // 添加元数据
        const meta = {
          query: text,
          vectorDimension: vector?.length || result.vectorDimension,
          processingTimeMs
        };
        
        return sendSuccessResponse(reply, {
          results: result.items,
          meta
        });
      } catch (error) {
        request.log.error(`向量搜索失败: ${error.message}`);
        return sendErrorResponse(
          reply,
          '向量搜索失败',
          error.name || 'InternalServerError',
          error.statusCode || 500
        );
      }
    }
  });

  // 自然语言查询
  fastify.post('/nlq', {
    schema: {
      description: '使用自然语言查询知识图谱',
      tags: ['搜索'],
      body: {
        type: 'object',
        required: ['question'],
        properties: {
          question: { 
            type: 'string', 
            description: '自然语言问题',
            example: '人参和西洋参有什么区别？'
          },
          context: { 
            type: 'string', 
            description: '提供额外上下文（可选）' 
          },
          domains: { 
            type: 'array', 
            items: { type: 'string' },
            description: '限制搜索领域' 
          },
          includeRawKnowledge: { 
            type: 'boolean', 
            default: false,
            description: '是否包含原始知识信息' 
          }
        }
      },
      response: {
        200: {
          description: '自然语言查询结果',
          ...dataResponseSchema,
          properties: {
            ...dataResponseSchema.properties,
            data: {
              type: 'object',
              properties: {
                answer: { type: 'string' },
                confidence: { type: 'number' },
                relevantNodes: {
                  type: 'array',
                  items: nodeSchema
                },
                rawKnowledge: {
                  type: 'array',
                  items: {
                    type: 'object',
                    properties: {
                      content: { type: 'string' },
                      source: { type: 'string' },
                      relevance: { type: 'number' }
                    }
                  }
                },
                meta: {
                  type: 'object',
                  properties: {
                    question: { type: 'string' },
                    processingTimeMs: { type: 'number' },
                    modelVersion: { type: 'string' }
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
      Body: {
        question: string;
        context?: string;
        domains?: string[];
        includeRawKnowledge?: boolean;
      }
    }>, reply: FastifyReply) => {
      try {
        const startTime = Date.now();
        const { question, context, domains, includeRawKnowledge = false } = request.body;
        
        const result = await searchService.naturalLanguageQuery(question, {
          context,
          domains,
          includeRawKnowledge
        });
        
        const processingTimeMs = Date.now() - startTime;
        
        // 添加元数据
        result.meta = {
          question,
          processingTimeMs,
          modelVersion: result.modelVersion || '1.0'
        };
        
        // 如果不需要包含原始知识，则移除
        if (!includeRawKnowledge) {
          delete result.rawKnowledge;
        }
        
        return sendSuccessResponse(reply, result);
      } catch (error) {
        request.log.error(`自然语言查询失败: ${error.message}`);
        return sendErrorResponse(
          reply,
          '自然语言查询失败',
          error.name || 'InternalServerError',
          error.statusCode || 500
        );
      }
    }
  });

  // 自动完成建议
  fastify.get('/autocomplete', {
    schema: {
      description: '获取搜索关键词自动完成建议',
      tags: ['搜索'],
      querystring: {
        type: 'object',
        required: ['prefix'],
        properties: {
          prefix: { 
            type: 'string', 
            description: '前缀文本',
            example: '人参'
          },
          limit: { 
            type: 'integer', 
            minimum: 1, 
            maximum: 20, 
            default: 10,
            description: '返回结果数量' 
          },
          nodeTypes: { 
            type: 'array', 
            items: { type: 'string' },
            description: '节点类型过滤' 
          }
        }
      },
      response: {
        200: {
          description: '自动完成建议',
          ...dataResponseSchema,
          properties: {
            ...dataResponseSchema.properties,
            data: {
              type: 'object',
              properties: {
                suggestions: {
                  type: 'array',
                  items: {
                    type: 'object',
                    properties: {
                      text: { type: 'string' },
                      nodeType: { type: 'string' },
                      nodeId: { type: 'string' }
                    }
                  }
                },
                prefix: { type: 'string' }
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
      Querystring: {
        prefix: string;
        limit?: number;
        nodeTypes?: string[];
      }
    }>, reply: FastifyReply) => {
      try {
        const { prefix, limit = 10, nodeTypes } = request.query;
        
        if (!prefix || prefix.length < 1) {
          return sendErrorResponse(reply, '前缀文本太短', 'ValidationError', 400);
        }
        
        const suggestions = await searchService.getAutocompleteSuggestions(prefix, {
          limit,
          nodeTypes
        });
        
        return sendSuccessResponse(reply, {
          suggestions,
          prefix
        });
      } catch (error) {
        request.log.error(`获取自动完成建议失败: ${error.message}`);
        return sendErrorResponse(
          reply,
          '获取自动完成建议失败',
          error.name || 'InternalServerError',
          error.statusCode || 500
        );
      }
    }
  });
};