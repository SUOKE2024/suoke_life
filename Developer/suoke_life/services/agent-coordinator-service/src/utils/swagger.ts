/**
 * Swagger API文档配置
 */
import swaggerJsdoc from 'swagger-jsdoc';
import { version } from '../../package.json';

const options: swaggerJsdoc.Options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: '代理协调器服务 API',
      version,
      description: '索克生活APP中的AI代理协调器服务的API文档',
      contact: {
        name: 'SuoKe Life Team',
        url: 'https://suoke.life',
      },
      license: {
        name: 'UNLICENSED',
      },
    },
    servers: [
      {
        url: '/api',
        description: '代理协调器API',
      },
    ],
    tags: [
      {
        name: '会话',
        description: '会话管理相关API',
      },
      {
        name: '代理',
        description: '智能体代理相关API',
      },
      {
        name: '协调',
        description: '代理协调操作相关API',
      },
      {
        name: '知识',
        description: '知识服务相关API',
      },
    ],
    components: {
      securitySchemes: {
        apiKey: {
          type: 'apiKey',
          in: 'header',
          name: 'X-API-Key',
        },
      },
      schemas: {
        Error: {
          type: 'object',
          properties: {
            success: {
              type: 'boolean',
              example: false,
            },
            error: {
              type: 'object',
              properties: {
                code: {
                  type: 'string',
                  example: 'INVALID_REQUEST',
                },
                message: {
                  type: 'string',
                  example: '请求无效',
                },
                details: {
                  type: 'object',
                  example: null,
                },
              },
            },
          },
        },
        Session: {
          type: 'object',
          properties: {
            sessionId: {
              type: 'string',
              example: 'd290f1ee-6c54-4b01-90e6-d701748f0851',
            },
            userId: {
              type: 'string',
              example: 'user-123',
            },
            currentAgentId: {
              type: 'string',
              example: 'xiaoke',
            },
            createdAt: {
              type: 'string',
              format: 'date-time',
            },
            updatedAt: {
              type: 'string',
              format: 'date-time',
            },
            active: {
              type: 'boolean',
              example: true,
            },
            metadata: {
              type: 'object',
              example: { source: 'mobile-app' },
            },
          },
        },
        Agent: {
          type: 'object',
          properties: {
            id: {
              type: 'string',
              example: 'xiaoke',
            },
            name: {
              type: 'string',
              example: '小克',
            },
            capabilities: {
              type: 'array',
              items: {
                type: 'string',
              },
              example: ['服务订阅', '农产品预制', '供应链管理'],
            },
            description: {
              type: 'string',
            },
            isDefault: {
              type: 'boolean',
            },
          },
        },
      },
    },
    security: [
      {
        apiKey: [],
      },
    ],
  },
  apis: ['./src/routes/*.ts'],
};

export const swaggerSpec = swaggerJsdoc(options); 