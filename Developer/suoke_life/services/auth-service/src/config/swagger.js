const swaggerJsdoc = require('swagger-jsdoc');

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: '索克生活认证服务API',
      version: '1.0.0',
      description: '索克生活APP认证服务的API文档',
      contact: {
        name: '索克生活团队',
        url: 'https://suoke.life',
        email: 'tech@suoke.life'
      },
    },
    servers: [
      {
        url: 'http://localhost:3001/api/v1',
        description: '开发环境API服务',
      },
      {
        url: 'http://118.31.223.213/api/v1',
        description: '生产环境API服务',
      },
    ],
    components: {
      securitySchemes: {
        bearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT',
        },
      },
    },
    security: [
      {
        bearerAuth: [],
      },
    ],
  },
  apis: ['./src/routes/*.js', './src/models/entities/*.js'],
};

const specs = swaggerJsdoc(options);

module.exports = specs; 