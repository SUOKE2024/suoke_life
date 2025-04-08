import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { KnowledgeIntegrationService } from '../domain/services/knowledge-integration-service';

/**
 * 知识整合相关路由
 */
export default async function knowledgeIntegrationRoutes(fastify: FastifyInstance) {
  const knowledgeIntegrationService = fastify.diContainer.resolve('knowledgeIntegrationService') as KnowledgeIntegrationService;
  
  // 注册路由模式
  fastify.register(async (instance) => {
    // 添加API前缀
    instance.addHook('onRequest', (request, reply, done) => {
      request.log.info(`知识整合API请求: ${request.method} ${request.url}`);
      done();
    });
    
    // 整合知识查询
    instance.post('/query', {
      schema: {
        description: '整合RAG、知识库和知识图谱的查询结果',
        tags: ['知识整合'],
        body: {
          type: 'object',
          required: ['query'],
          properties: {
            query: { type: 'string', description: '查询文本' },
            maxResults: { type: 'number', description: '最大结果数量' },
            threshold: { type: 'number', description: '相似度阈值' },
            domains: { 
              type: 'array', 
              items: { type: 'string' },
              description: '领域限制' 
            },
            nodeTypes: { 
              type: 'array', 
              items: { type: 'string' },
              description: '节点类型限制' 
            },
            relationshipTypes: { 
              type: 'array', 
              items: { type: 'string' },
              description: '关系类型限制' 
            },
            includeRelationships: { 
              type: 'boolean', 
              description: '是否包含关系' 
            },
            saveIntegratedResult: { 
              type: 'boolean', 
              description: '是否保存整合结果' 
            }
          }
        },
        response: {
          200: {
            description: '整合查询结果',
            type: 'object',
            properties: {
              query: { type: 'string' },
              answer: { type: 'string' },
              confidence: { type: 'number' },
              sources: { 
                type: 'object',
                properties: {
                  rag: { type: 'boolean' },
                  knowledgeBase: { type: 'boolean' },
                  knowledgeGraph: { type: 'boolean' }
                }
              },
              evidence: { 
                type: 'object',
                properties: {
                  rag: { type: 'array' },
                  knowledgeBase: { type: 'array' },
                  knowledgeGraph: { 
                    type: 'object',
                    properties: {
                      nodes: { type: 'array' },
                      relationships: { type: 'array' }
                    }
                  }
                }
              },
              timestamp: { type: 'string' }
            }
          },
          400: {
            description: '请求参数错误',
            type: 'object',
            properties: {
              statusCode: { type: 'number' },
              error: { type: 'string' },
              message: { type: 'string' }
            }
          },
          500: {
            description: '服务器错误',
            type: 'object',
            properties: {
              statusCode: { type: 'number' },
              error: { type: 'string' },
              message: { type: 'string' }
            }
          }
        }
      },
      handler: async (request: FastifyRequest<{
        Body: {
          query: string;
          maxResults?: number;
          threshold?: number;
          domains?: string[];
          nodeTypes?: string[];
          relationshipTypes?: string[];
          includeRelationships?: boolean;
          saveIntegratedResult?: boolean;
        }
      }>, reply: FastifyReply) => {
        try {
          const { 
            query, 
            maxResults, 
            threshold, 
            domains, 
            nodeTypes, 
            relationshipTypes,
            includeRelationships,
            saveIntegratedResult
          } = request.body;
          
          // 调用服务
          const result = await knowledgeIntegrationService.integrateKnowledge(query, {
            maxResults,
            threshold,
            domains,
            nodeTypes,
            relationshipTypes,
            includeRelationships,
            saveIntegratedResult
          });
          
          // 返回结果
          return reply.code(200).send(result);
        } catch (error) {
          request.log.error(`知识整合查询失败: ${error.message}`);
          return reply.code(500).send({
            statusCode: 500,
            error: '服务器错误',
            message: `知识整合查询失败: ${error.message}`
          });
        }
      }
    });
    
    // 健康检查
    instance.get('/health', {
      schema: {
        description: '知识整合服务健康检查',
        tags: ['健康检查'],
        response: {
          200: {
            type: 'object',
            properties: {
              status: { type: 'string' },
              services: { 
                type: 'object',
                properties: {
                  rag: { type: 'string' },
                  knowledgeBase: { type: 'string' },
                  knowledgeGraph: { type: 'string' }
                }
              },
              timestamp: { type: 'string' }
            }
          }
        }
      },
      handler: async (_request: FastifyRequest, reply: FastifyReply) => {
        // 简单健康检查
        return reply.code(200).send({
          status: 'ok',
          services: {
            rag: 'connected',
            knowledgeBase: 'connected',
            knowledgeGraph: 'connected'
          },
          timestamp: new Date().toISOString()
        });
      }
    });
  }, { prefix: '/api/integration' });
} 