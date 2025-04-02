/**
 * Swagger API文档配置
 */
import swaggerJsdoc from 'swagger-jsdoc';
import swaggerUi from 'swagger-ui-express';
import { Express } from 'express';
import config from './config';

// Swagger定义
const swaggerOptions = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: '索克生活知识库服务API',
      version: '1.0.0',
      description: '索克生活知识库服务的API文档，提供知识管理、版本控制和审核功能',
      contact: {
        name: '索克生活开发团队',
        url: 'http://suoke.life',
        email: 'dev@suoke.life'
      },
      license: {
        name: '© 2024 索克科技. 版权所有',
        url: 'https://suoke.life'
      }
    },
    servers: [
      {
        url: `${config.app.protocol || 'http'}://${config.app.host || 'localhost'}:${config.app.port}/api`,
        description: '开发服务器'
      },
      {
        url: 'https://api.suoke.life/knowledge-base',
        description: '生产服务器'
      }
    ],
    components: {
      securitySchemes: {
        bearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT'
        },
        apiKeyAuth: {
          type: 'apiKey',
          in: 'header',
          name: 'X-API-KEY'
        }
      },
      schemas: {
        // 基础响应模型
        SuccessResponse: {
          type: 'object',
          properties: {
            success: {
              type: 'boolean',
              example: true
            },
            message: {
              type: 'string',
              example: '操作成功'
            },
            data: {
              type: 'object'
            }
          }
        },
        ErrorResponse: {
          type: 'object',
          properties: {
            success: {
              type: 'boolean',
              example: false
            },
            message: {
              type: 'string',
              example: '操作失败'
            },
            error: {
              type: 'string',
              example: 'ValidationError'
            },
            statusCode: {
              type: 'integer',
              example: 400
            }
          }
        }
      }
    },
    security: [
      {
        bearerAuth: []
      }
    ],
    tags: [
      {
        name: '知识管理',
        description: '基础知识管理功能'
      },
      {
        name: '营养知识',
        description: '营养相关知识管理'
      },
      {
        name: '生活方式',
        description: '健康生活方式知识管理'
      },
      {
        name: '医学知识',
        description: '现代医学知识管理'
      },
      {
        name: 'TCM',
        description: '中医知识管理'
      },
      {
        name: '环境健康',
        description: '环境健康知识管理'
      },
      {
        name: '心理健康',
        description: '心理健康知识管理'
      },
      {
        name: '分类管理',
        description: '知识分类管理'
      },
      {
        name: '标签管理',
        description: '知识标签管理'
      },
      {
        name: '版本管理',
        description: '知识版本控制功能'
      },
      {
        name: '审核管理',
        description: '知识审核流程管理'
      },
      {
        name: '系统',
        description: '系统管理功能'
      }
    ]
  },
  apis: ['./src/routes/*.ts', './src/controllers/*.ts', './src/models/*.ts', './src/interfaces/*.ts']
};

// 生成Swagger规范
const swaggerSpec = swaggerJsdoc(swaggerOptions);

/**
 * 配置Swagger文档
 * @param app Express应用实例
 */
export const setupSwagger = (app: Express): void => {
  const isProduction = process.env.NODE_ENV === 'production';
  
  // 仅在非生产环境或明确启用文档的情况下提供Swagger UI
  if (!isProduction || process.env.ENABLE_API_DOCS === 'true') {
    // Swagger UI设置
    const swaggerUiOptions = {
      explorer: true,
      customCss: '.swagger-ui .topbar { display: none }',
      customSiteTitle: '索克生活知识库服务API文档',
      customfavIcon: 'https://suoke.life/favicon.ico',
      swaggerOptions: {
        persistAuthorization: true,
        docExpansion: 'none',
        filter: true,
        displayRequestDuration: true
      }
    };
    
    // 设置基本认证（仅在生产环境或指定时）
    if ((isProduction || process.env.API_DOCS_BASIC_AUTH === 'true') && 
        process.env.API_DOCS_USERNAME && 
        process.env.API_DOCS_PASSWORD) {
      const basicAuth = require('express-basic-auth');
      app.use('/api-docs', basicAuth({
        users: { 
          [process.env.API_DOCS_USERNAME]: process.env.API_DOCS_PASSWORD
        },
        challenge: true,
        realm: '索克生活知识库服务API文档'
      }));
    }
    
    // 设置Swagger路由
    app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec, swaggerUiOptions));
    
    // 提供Swagger JSON
    app.get('/api-docs.json', (req, res) => {
      res.setHeader('Content-Type', 'application/json');
      res.send(swaggerSpec);
    });
    
    console.log(`📚 API文档可在 http://${config.app.host || 'localhost'}:${config.app.port}/api-docs 访问`);
  }
};