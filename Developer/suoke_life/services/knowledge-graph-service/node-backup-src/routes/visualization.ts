import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { KnowledgeGraphService } from '../domain/services/knowledge-graph-service';
import { VisualizationService } from '../domain/services/visualization-service';
import { sendSuccessResponse, sendErrorResponse } from '../infrastructure/utils/response';
import { VisualizationOptions } from '../domain/interfaces/api-response.interface';

/**
 * 知识图谱可视化相关路由
 */
export const visualizationRoutes = async (fastify: FastifyInstance) => {
  // 注册服务依赖
  const knowledgeGraphService = fastify.diContainer.resolve('knowledgeGraphService') as KnowledgeGraphService;
  const visualizationService = fastify.diContainer.resolve('visualizationService') as VisualizationService;
  
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

  // 标准图形可视化响应模型
  const graphVisualizationSchema = {
    type: 'object',
    properties: {
      nodes: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            label: { type: 'string' },
            type: { type: 'string' },
            attributes: { type: 'object', additionalProperties: true },
            x: { type: 'number' },
            y: { type: 'number' },
            size: { type: 'number' },
            color: { type: 'string' }
          }
        }
      },
      edges: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            source: { type: 'string' },
            target: { type: 'string' },
            label: { type: 'string' },
            attributes: { type: 'object', additionalProperties: true },
            size: { type: 'number' },
            color: { type: 'string' }
          }
        }
      },
      meta: {
        type: 'object',
        properties: {
          nodeCount: { type: 'integer' },
          edgeCount: { type: 'integer' },
          layout: { type: 'string' }
        }
      }
    }
  };

  // 3D可视化响应模型
  const threeDVisualizationSchema = {
    type: 'object',
    properties: {
      nodes: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            label: { type: 'string' },
            type: { type: 'string' },
            attributes: { type: 'object', additionalProperties: true },
            x: { type: 'number' },
            y: { type: 'number' },
            z: { type: 'number' },
            size: { type: 'number' },
            color: { type: 'string' },
            geometry: { 
              type: 'string',
              enum: ['sphere', 'cube', 'cylinder', 'cone', 'custom'],
              description: '3D几何形状'
            }
          }
        }
      },
      edges: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            source: { type: 'string' },
            target: { type: 'string' },
            label: { type: 'string' },
            attributes: { type: 'object', additionalProperties: true },
            size: { type: 'number' },
            color: { type: 'string' },
            curve: { type: 'number', description: '曲线弯曲程度' }
          }
        }
      },
      meta: {
        type: 'object',
        properties: {
          nodeCount: { type: 'integer' },
          edgeCount: { type: 'integer' },
          layout: { type: 'string' },
          dimensions: { type: 'string', enum: ['2D', '3D'] }
        }
      }
    }
  };

  // AR可视化响应模型
  const arVisualizationSchema = {
    type: 'object',
    properties: {
      scenes: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            name: { type: 'string' },
            anchor: {
              type: 'object',
              properties: {
                type: { type: 'string', enum: ['image', 'plane', 'face', 'world'] },
                value: { type: 'string', description: 'Anchor参考值，如图像URL' }
              }
            },
            objects: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  id: { type: 'string' },
                  nodeId: { type: 'string', description: '对应的知识图谱节点ID' },
                  type: { type: 'string' },
                  model: { 
                    type: 'string', 
                    description: '3D模型URL或标识符' 
                  },
                  position: {
                    type: 'object',
                    properties: { x: { type: 'number' }, y: { type: 'number' }, z: { type: 'number' } }
                  },
                  rotation: {
                    type: 'object',
                    properties: { x: { type: 'number' }, y: { type: 'number' }, z: { type: 'number' } }
                  },
                  scale: {
                    type: 'object',
                    properties: { x: { type: 'number' }, y: { type: 'number' }, z: { type: 'number' } }
                  },
                  interactive: { type: 'boolean' },
                  animation: { type: 'string' }
                }
              }
            },
            connections: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  id: { type: 'string' },
                  source: { type: 'string' },
                  target: { type: 'string' },
                  type: { type: 'string' },
                  visualType: { 
                    type: 'string', 
                    enum: ['line', 'arrow', 'particle', 'custom'],
                    description: '连接的可视化类型'
                  },
                  color: { type: 'string' }
                }
              }
            }
          }
        }
      },
      meta: {
        type: 'object',
        properties: {
          version: { type: 'string' },
          sceneCount: { type: 'integer' },
          objectCount: { type: 'integer' },
          connectionCount: { type: 'integer' }
        }
      }
    }
  };

  // 获取图可视化数据
  fastify.get('/visualization/graph', {
    schema: {
      description: '获取知识图谱的可视化数据（节点和边）',
      tags: ['可视化'],
      querystring: {
        type: 'object',
        properties: {
          rootNodeId: { 
            type: 'string', 
            description: '根节点ID，如果提供则以此节点为中心进行可视化' 
          },
          maxDepth: { 
            type: 'integer', 
            minimum: 1, 
            maximum: 5, 
            default: 2,
            description: '最大深度' 
          },
          maxNodes: { 
            type: 'integer', 
            minimum: 5, 
            maximum: 1000, 
            default: 100,
            description: '最大节点数量' 
          },
          layout: { 
            type: 'string', 
            enum: ['force', 'circular', 'hierarchical', 'radial'],
            default: 'force',
            description: '布局算法' 
          },
          nodeTypes: { 
            type: 'array', 
            items: { type: 'string' },
            description: '节点类型过滤' 
          },
          relationshipTypes: { 
            type: 'array', 
            items: { type: 'string' },
            description: '关系类型过滤' 
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
          description: '成功获取可视化数据',
          ...dataResponseSchema,
          properties: {
            ...dataResponseSchema.properties,
            data: graphVisualizationSchema
          }
        },
        400: {
          description: '请求参数错误',
          ...errorResponseSchema
        },
        404: {
          description: '根节点不存在',
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
        rootNodeId?: string;
        maxDepth?: number;
        maxNodes?: number;
        layout?: 'force' | 'circular' | 'hierarchical' | 'radial';
        nodeTypes?: string[];
        relationshipTypes?: string[];
        domains?: string[];
      }
    }>, reply: FastifyReply) => {
      try {
        const { 
          rootNodeId, 
          maxDepth = 2, 
          maxNodes = 100, 
          layout = 'force',
          nodeTypes,
          relationshipTypes,
          domains
        } = request.query;
        
        const options: VisualizationOptions = {
          maxDepth,
          maxNodes,
          layout,
          nodeTypes,
          relationshipTypes,
          domains
        };
        
        const visualizationData = await visualizationService.getGraphVisualization(rootNodeId, options);
        
        return sendSuccessResponse(reply, visualizationData);
      } catch (error) {
        if (error.message.includes('节点不存在')) {
          return sendErrorResponse(reply, error.message, 'NotFoundError', 404);
        }
        
        request.log.error(`获取图谱可视化数据失败: ${error.message}`);
        return sendErrorResponse(
          reply,
          '获取图谱可视化数据失败',
          error.name || 'InternalServerError',
          error.statusCode || 500
        );
      }
    }
  });

  // 获取3D可视化数据
  fastify.get('/visualization/3d', {
    schema: {
      description: '获取知识图谱的3D可视化数据',
      tags: ['可视化'],
      querystring: {
        type: 'object',
        properties: {
          rootNodeId: { 
            type: 'string', 
            description: '根节点ID，如果提供则以此节点为中心进行可视化' 
          },
          maxDepth: { 
            type: 'integer', 
            minimum: 1, 
            maximum: 5, 
            default: 2,
            description: '最大深度' 
          },
          maxNodes: { 
            type: 'integer', 
            minimum: 5, 
            maximum: 500, 
            default: 100,
            description: '最大节点数量' 
          },
          layout: { 
            type: 'string', 
            enum: ['force3d', 'sphere', 'grid'],
            default: 'force3d',
            description: '3D布局算法' 
          },
          nodeTypes: { 
            type: 'array', 
            items: { type: 'string' },
            description: '节点类型过滤' 
          },
          relationshipTypes: { 
            type: 'array', 
            items: { type: 'string' },
            description: '关系类型过滤' 
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
          description: '成功获取3D可视化数据',
          ...dataResponseSchema,
          properties: {
            ...dataResponseSchema.properties,
            data: threeDVisualizationSchema
          }
        },
        400: {
          description: '请求参数错误',
          ...errorResponseSchema
        },
        404: {
          description: '根节点不存在',
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
        rootNodeId?: string;
        maxDepth?: number;
        maxNodes?: number;
        layout?: 'force3d' | 'sphere' | 'grid';
        nodeTypes?: string[];
        relationshipTypes?: string[];
        domains?: string[];
      }
    }>, reply: FastifyReply) => {
      try {
        const { 
          rootNodeId, 
          maxDepth = 2, 
          maxNodes = 100, 
          layout = 'force3d',
          nodeTypes,
          relationshipTypes,
          domains
        } = request.query;
        
        const options: VisualizationOptions = {
          maxDepth,
          maxNodes,
          layout,
          nodeTypes,
          relationshipTypes,
          domains,
          dimensions: '3D'
        };
        
        const visualizationData = await visualizationService.get3DVisualization(rootNodeId, options);
        
        return sendSuccessResponse(reply, visualizationData);
      } catch (error) {
        if (error.message.includes('节点不存在')) {
          return sendErrorResponse(reply, error.message, 'NotFoundError', 404);
        }
        
        request.log.error(`获取3D可视化数据失败: ${error.message}`);
        return sendErrorResponse(
          reply,
          '获取3D可视化数据失败',
          error.name || 'InternalServerError',
          error.statusCode || 500
        );
      }
    }
  });

  // 获取AR可视化数据
  fastify.get('/visualization/ar', {
    schema: {
      description: '获取知识图谱的AR增强现实可视化数据',
      tags: ['可视化'],
      querystring: {
        type: 'object',
        properties: {
          rootNodeId: { 
            type: 'string', 
            description: '根节点ID，如果提供则以此节点为中心进行可视化' 
          },
          anchorType: { 
            type: 'string', 
            enum: ['image', 'plane', 'face', 'world'],
            default: 'world',
            description: 'AR锚点类型' 
          },
          anchorValue: { 
            type: 'string',
            description: 'AR锚点值，如图像URL' 
          },
          maxNodes: { 
            type: 'integer', 
            minimum: 1, 
            maximum: 50, 
            default: 10,
            description: '最大节点数量' 
          },
          nodeTypes: { 
            type: 'array', 
            items: { type: 'string' },
            description: '节点类型过滤' 
          },
          relationshipTypes: { 
            type: 'array', 
            items: { type: 'string' },
            description: '关系类型过滤' 
          },
          domain: { 
            type: 'string',
            description: '领域' 
          }
        }
      },
      response: {
        200: {
          description: '成功获取AR可视化数据',
          ...dataResponseSchema,
          properties: {
            ...dataResponseSchema.properties,
            data: arVisualizationSchema
          }
        },
        400: {
          description: '请求参数错误',
          ...errorResponseSchema
        },
        404: {
          description: '根节点不存在',
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
        rootNodeId?: string;
        anchorType?: 'image' | 'plane' | 'face' | 'world';
        anchorValue?: string;
        maxNodes?: number;
        nodeTypes?: string[];
        relationshipTypes?: string[];
        domain?: string;
      }
    }>, reply: FastifyReply) => {
      try {
        const { 
          rootNodeId, 
          anchorType = 'world', 
          anchorValue,
          maxNodes = 10,
          nodeTypes,
          relationshipTypes,
          domain
        } = request.query;
        
        const options = {
          anchorType,
          anchorValue,
          maxNodes,
          nodeTypes,
          relationshipTypes,
          domain
        };
        
        const arData = await visualizationService.getARVisualization(rootNodeId, options);
        
        return sendSuccessResponse(reply, arData);
      } catch (error) {
        if (error.message.includes('节点不存在')) {
          return sendErrorResponse(reply, error.message, 'NotFoundError', 404);
        }
        
        request.log.error(`获取AR可视化数据失败: ${error.message}`);
        return sendErrorResponse(
          reply,
          '获取AR可视化数据失败',
          error.name || 'InternalServerError',
          error.statusCode || 500
        );
      }
    }
  });

  // 获取场景预设可视化
  fastify.get('/visualization/presets/:presetId', {
    schema: {
      description: '获取预设的知识图谱可视化场景',
      tags: ['可视化'],
      params: {
        type: 'object',
        required: ['presetId'],
        properties: {
          presetId: { 
            type: 'string', 
            description: '预设场景ID' 
          }
        }
      },
      querystring: {
        type: 'object',
        properties: {
          format: { 
            type: 'string', 
            enum: ['2d', '3d', 'ar', 'vr'],
            default: '2d',
            description: '可视化格式' 
          },
          customParams: { 
            type: 'object',
            additionalProperties: true,
            description: '自定义参数' 
          }
        }
      },
      response: {
        200: {
          description: '成功获取预设可视化场景',
          ...dataResponseSchema,
          properties: {
            ...dataResponseSchema.properties,
            data: {
              type: 'object',
              properties: {
                preset: {
                  type: 'object',
                  properties: {
                    id: { type: 'string' },
                    name: { type: 'string' },
                    description: { type: 'string' },
                    type: { type: 'string' },
                    format: { type: 'string' }
                  }
                },
                visualization: {
                  type: 'object',
                  description: '根据format返回对应的可视化数据结构'
                }
              }
            }
          }
        },
        404: {
          description: '预设场景不存在',
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
        presetId: string;
      },
      Querystring: {
        format?: '2d' | '3d' | 'ar' | 'vr';
        customParams?: Record<string, any>;
      }
    }>, reply: FastifyReply) => {
      try {
        const { presetId } = request.params;
        const { format = '2d', customParams = {} } = request.query;
        
        const preset = await visualizationService.getPresetVisualization(presetId, format, customParams);
        
        if (!preset) {
          return sendErrorResponse(reply, '预设场景不存在', 'NotFoundError', 404);
        }
        
        return sendSuccessResponse(reply, preset);
      } catch (error) {
        request.log.error(`获取预设可视化场景失败: ${error.message}`);
        return sendErrorResponse(
          reply,
          '获取预设可视化场景失败',
          error.name || 'InternalServerError',
          error.statusCode || 500
        );
      }
    }
  });
};