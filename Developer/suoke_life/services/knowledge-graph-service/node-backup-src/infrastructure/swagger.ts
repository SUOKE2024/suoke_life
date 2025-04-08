import { FastifyInstance } from 'fastify';
import fastifySwagger from '@fastify/swagger';
import fastifySwaggerUi from '@fastify/swagger-ui';
import { version } from '../../package.json';

interface SwaggerOptions {
  routePrefix?: string;
  uiConfig?: Record<string, any>;
  staticCSP?: boolean;
  transformStaticCSP?: (header: string) => string;
  theme?: Record<string, any>;
  isProtected?: boolean;
  username?: string;
  password?: string;
}

/**
 * 注册Swagger文档插件
 * @param fastify Fastify实例
 * @param options Swagger UI选项
 */
export const registerSwagger = async (
  fastify: FastifyInstance,
  options: SwaggerOptions = {}
): Promise<void> => {
  const {
    routePrefix = '/api-docs',
    uiConfig = {
      deepLinking: true,
      showExtensions: true,
      showCommonExtensions: true,
      defaultModelsExpandDepth: 3,
      defaultModelExpandDepth: 3,
      docExpansion: 'list',
      supportedSubmitMethods: ['get', 'put', 'post', 'delete', 'patch']
    },
    staticCSP = true,
    transformStaticCSP,
    theme = {
      title: '索克生活知识图谱服务API文档',
      theme: {
        colors: {
          primary: {
            main: '#35BB78' // 索克绿
          }
        },
        typography: {
          fontSize: '16px',
          fontFamily: 'Roboto, "Helvetica Neue", Arial, sans-serif'
        }
      }
    },
    isProtected = process.env.SWAGGER_PROTECTED === 'true',
    username = process.env.SWAGGER_USERNAME || 'admin',
    password = process.env.SWAGGER_PASSWORD || 'suoke@2024'
  } = options;

  // 注册Swagger插件
  await fastify.register(fastifySwagger, {
    openapi: {
      info: {
        title: '索克生活知识图谱服务API',
        description: `
          ## 索克生活知识图谱服务API文档
          
          本API提供了访问和管理索克生活知识图谱的接口。知识图谱存储了关于中医健康、食疗、农产品等领域的结构化知识。
          
          ### 主要功能:
          
          - 知识图谱节点和关系的CRUD操作
          - 图谱查询和导航
          - 知识图谱可视化（2D、3D、AR）
          - 向量搜索和语义查询
          
          ### 身份验证:
          
          部分API端点需要身份验证。使用JWT Bearer令牌进行身份验证。
        `,
        version,
        contact: {
          name: '索克生活技术团队',
          url: 'https://suoke.life',
          email: 'tech@suoke.life'
        },
        license: {
          name: '专有软件',
          url: 'https://suoke.life/terms'
        }
      },
      externalDocs: {
        url: 'https://suoke.life/docs',
        description: '查看更多文档'
      },
      tags: [
        { name: '知识图谱', description: '知识图谱节点和关系操作' },
        { name: '可视化', description: '图谱可视化相关接口' },
        { name: '搜索', description: '知识图谱搜索相关接口' },
        { name: '系统', description: '系统相关接口' }
      ],
      components: {
        securitySchemes: {
          bearerAuth: {
            type: 'http',
            scheme: 'bearer',
            bearerFormat: 'JWT'
          }
        }
      }
    }
  });

  // 注册Swagger UI插件
  await fastify.register(fastifySwaggerUi, {
    routePrefix,
    uiConfig,
    staticCSP,
    transformStaticCSP,
    theme,
    // 如果启用了保护，添加基本身份验证
    ...(isProtected ? {
      uiHooks: {
        onRequest: (request, reply, next) => {
          const auth = request.headers.authorization;
          if (!auth) {
            reply.header('WWW-Authenticate', 'Basic');
            return reply.code(401).send('认证失败');
          }

          const [scheme, credentials] = auth.split(' ');
          if (scheme !== 'Basic') {
            return reply.code(400).send('认证方案不支持');
          }

          const [user, pass] = Buffer.from(credentials, 'base64').toString().split(':');
          if (user !== username || pass !== password) {
            reply.header('WWW-Authenticate', 'Basic');
            return reply.code(401).send('认证失败');
          }

          next();
        }
      }
    } : {})
  });
};