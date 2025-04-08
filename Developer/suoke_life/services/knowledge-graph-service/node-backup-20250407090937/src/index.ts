import fastify, { FastifyInstance } from 'fastify';
import { config } from './infrastructure/config';
import { logger } from './infrastructure/logger';
import { registerSwagger } from './infrastructure/swagger';
import { registerPlugins } from './infrastructure/plugins';
import { knowledgeGraphRoutes } from './routes/knowledge-graph';
import { visualizationRoutes } from './routes/visualization';
import { searchRoutes } from './routes/search';
import { setupDependencyInjection } from './infrastructure/di-container';

const server: FastifyInstance = fastify({
  logger,
  trustProxy: true,
  ignoreTrailingSlash: true
});

// 设置依赖注入容器
setupDependencyInjection(server);

// 注册插件
registerPlugins(server);

// 注册Swagger文档
registerSwagger(server, {
  isProtected: config.swagger.isProtected,
  username: config.swagger.username,
  password: config.swagger.password
});

// 健康检查路由
server.get('/health', {
  schema: {
    description: '健康检查端点',
    tags: ['系统'],
    response: {
      200: {
        description: '服务健康状态',
        type: 'object',
        properties: {
          status: { type: 'string', enum: ['ok', 'error'], example: 'ok' },
          version: { type: 'string', example: '1.0.0' },
          timestamp: { type: 'string', format: 'date-time' }
        }
      }
    }
  },
  handler: async (request, reply) => {
    reply.send({
      status: 'ok',
      version: config.version,
      timestamp: new Date().toISOString()
    });
  }
});

// 注册路由
server.register(knowledgeGraphRoutes, { prefix: '/api/v1/graph' });
server.register(visualizationRoutes, { prefix: '/api/v1' });
server.register(searchRoutes, { prefix: '/api/v1/search' });

// 启动服务器
const start = async () => {
  try {
    await server.listen({ port: config.server.port, host: config.server.host });
    
    // 打印API文档访问信息
    const swaggerUrl = `http://${config.server.host}:${config.server.port}/api-docs`;
    server.log.info(`服务器已启动: http://${config.server.host}:${config.server.port}`);
    server.log.info(`API文档地址: ${swaggerUrl}`);
    if (config.swagger.isProtected) {
      server.log.info('API文档已启用身份验证保护');
    }
  } catch (err) {
    server.log.error(err);
    process.exit(1);
  }
};

// 处理进程关闭信号
process.on('SIGINT', async () => {
  server.log.info('接收到SIGINT信号，正在关闭服务...');
  await server.close();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  server.log.info('接收到SIGTERM信号，正在关闭服务...');
  await server.close();
  process.exit(0);
});

// 未捕获的异常处理
process.on('uncaughtException', (err) => {
  server.log.error({ err }, '未捕获的异常');
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  server.log.error({ reason }, '未处理的Promise拒绝');
});

// 开始服务
start();