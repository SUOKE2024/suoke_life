import swaggerJSDoc from 'swagger-jsdoc';
import swaggerUi from 'swagger-ui-express';
import { Express } from 'express';
import config from './index';

/**
 * Swagger配置
 */
const options: swaggerJSDoc.Options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: '索克生活问诊诊断微服务 API',
      version: '1.0.0',
      description: '提供问诊诊断服务的RESTful API，包括中医辨证、诊断分析等功能',
      contact: {
        name: '索克生活技术团队',
        url: 'https://suoke.life',
        email: 'tech@suoke.life'
      },
      license: {
        name: '© 2024 索克科技. 版权所有',
        url: 'https://suoke.life'
      }
    },
    servers: [
      {
        url: `${config.server.protocol}://${config.server.host}:${config.server.port}/api`,
        description: '开发环境'
      },
      {
        url: 'https://api.suoke.life/inquiry-diagnosis',
        description: '生产环境'
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
        // Swagger已有的schema定义会自动合并
      }
    },
    security: [
      {
        bearerAuth: []
      }
    ],
    tags: [
      {
        name: '问诊',
        description: '问诊会话管理和交互'
      },
      {
        name: '诊断',
        description: '中医辨证分析和诊断结果'
      },
      {
        name: '四诊协调',
        description: '四诊协调服务和回调管理'
      }
    ]
  },
  apis: [
    './src/routes/*.ts',
    './src/controllers/*.ts',
    './src/models/*.ts',
    './src/interfaces/*.ts'
  ]
};

/**
 * Swagger文档JSON
 */
const swaggerSpec = swaggerJSDoc(options);

/**
 * Swagger UI配置
 */
const swaggerUiOptions = {
  explorer: true,
  customCss: '.swagger-ui .topbar { display: none }',
  customSiteTitle: '索克生活问诊诊断服务API文档',
  customfavIcon: 'https://suoke.life/favicon.ico',
  swaggerOptions: {
    persistAuthorization: true,
    docExpansion: 'none',
    filter: true,
    displayRequestDuration: true
  }
};

/**
 * 设置Swagger
 * @param app Express应用
 */
export const setupSwagger = (app: Express): void => {
  const isProduction = process.env.NODE_ENV === 'production';
  
  // 仅在非生产环境或明确启用文档的情况下提供Swagger UI
  if (!isProduction || process.env.ENABLE_API_DOCS === 'true') {
    // 提供Swagger JSON端点
    app.get('/api-docs.json', (req, res) => {
      res.setHeader('Content-Type', 'application/json');
      res.send(swaggerSpec);
    });

    // 设置基本认证（仅在生产环境）
    if (isProduction && process.env.API_DOCS_BASIC_AUTH === 'true') {
      const basicAuth = require('express-basic-auth');
      app.use('/api-docs', basicAuth({
        users: { 
          [process.env.API_DOCS_USERNAME || 'admin']: process.env.API_DOCS_PASSWORD || 'suoke2024'
        },
        challenge: true,
        realm: '索克生活问诊诊断服务API文档'
      }));
    }

    // 设置Swagger UI
    app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec, swaggerUiOptions));
    
    console.log(`📚 API文档可通过 http://${config.server.host}:${config.server.port}/api-docs 访问`);
  }
};

export default { setupSwagger };