'use strict';

// 导入依赖
const path = require('path');
const Fastify = require('fastify');
const dotenv = require('dotenv');

// 加载环境变量
dotenv.config({ path: path.join(__dirname, '..', '.env') });

// 创建Fastify实例
const fastify = Fastify({
  logger: {
    level: process.env.LOG_LEVEL || 'info',
    transport: {
      target: 'pino-pretty',
      options: {
        translateTime: 'HH:MM:ss Z',
        ignore: 'pid,hostname',
      },
    },
  },
  trustProxy: true,
});

// 注册插件
async function registerPlugins() {
  // CORS
  await fastify.register(require('@fastify/cors'), {
    origin: (origin, cb) => {
      const allowedOrigins = (process.env.ALLOWED_ORIGINS || '').split(',');
      if (!origin || allowedOrigins.includes(origin)) {
        cb(null, true);
        return;
      }
      cb(new Error('不允许的跨域请求'), false);
    },
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    credentials: true,
  });

  // 安全头信息
  await fastify.register(require('@fastify/helmet'), {
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        imgSrc: ["'self'", 'data:'],
        scriptSrc: ["'self'"],
      },
    },
  });

  // Redis连接
  if (process.env.REDIS_HOST) {
    await fastify.register(require('@fastify/redis'), {
      host: process.env.REDIS_HOST,
      port: process.env.REDIS_PORT || 6379,
      password: process.env.REDIS_PASSWORD,
      maxRetriesPerRequest: 3,
      enableReadyCheck: true,
      namespace: 'soer:',
    });
    fastify.log.info('Redis连接已配置');
  }

  // 接口限流
  await fastify.register(require('@fastify/rate-limit'), {
    max: 100,
    timeWindow: '1 minute',
    redis: fastify.redis,
    keyGenerator: (req) => {
      return req.headers['x-client-id'] || req.ip;
    },
    errorResponseBuilder: (req, context) => {
      return {
        statusCode: 429,
        error: '请求过多',
        message: `请求频率超限，请在${context.after}秒后重试`,
      };
    },
  });

  // API文档
  await fastify.register(require('@fastify/swagger'), {
    routePrefix: '/documentation',
    swagger: {
      info: {
        title: '索儿智能体API文档',
        description: '索儿智能体代理微服务API接口文档',
        version: '1.0.0',
      },
      externalDocs: {
        url: 'https://suoke.life/docs',
        description: '索克生活平台文档',
      },
      securityDefinitions: {
        apiKey: {
          type: 'apiKey',
          name: 'Authorization',
          in: 'header',
        },
      },
    },
    exposeRoute: true,
  });

  // 加载路由
  await fastify.register(require('./routes/health'), { prefix: '/health' });
  await fastify.register(require('./routes/agent'), { prefix: '/api/v1/agent' });
  await fastify.register(require('./routes/insights'), { prefix: '/api/v1/insights' });
  await fastify.register(require('./routes/recommendations'), { prefix: '/api/v1/recommendations' });
  await fastify.register(require('./routes/sensing'), { prefix: '/api/v1/sensing' });
  await fastify.register(require('./routes/metrics'), { prefix: '/metrics' });
  await fastify.register(require('./routes/knowledge'), { prefix: '/api/v1/knowledge' });
}

// 注册钩子
fastify.addHook('onRequest', async (request, reply) => {
  // 添加请求ID和时间戳
  request.requestId = request.headers['x-request-id'] || require('uuid').v4();
  request.requestTime = Date.now();
  reply.header('X-Request-ID', request.requestId);
});

fastify.addHook('onResponse', async (request, reply) => {
  // 记录响应时间
  const responseTime = Date.now() - request.requestTime;
  fastify.log.info({
    requestId: request.requestId,
    method: request.method,
    url: request.url,
    statusCode: reply.statusCode,
    responseTime: `${responseTime}ms`,
  }, 'request completed');
});

// 未处理的路由
fastify.setNotFoundHandler((request, reply) => {
  reply.status(404).send({
    statusCode: 404,
    error: '未找到',
    message: `路由 ${request.method}:${request.url} 不存在`,
  });
});

// 错误处理
fastify.setErrorHandler((error, request, reply) => {
  fastify.log.error(error);
  
  // 自定义错误响应
  const statusCode = error.statusCode || 500;
  const errorMessage = error.message || '服务器内部错误';
  
  reply.status(statusCode).send({
    statusCode,
    error: statusCode === 500 ? '服务器内部错误' : error.name || '请求错误',
    message: process.env.NODE_ENV === 'production' && statusCode === 500 
      ? '服务器内部错误，请稍后再试' 
      : errorMessage,
    requestId: request.requestId,
  });
});

// 启动服务器
async function start() {
  try {
    // 注册插件
    await registerPlugins();
    
    // 加载智能体配置
    const agentConfigPath = process.env.MODEL_CONFIG_PATH || path.join(__dirname, '..', 'config', 'agent-config.json');
    const agentConfig = require(agentConfigPath);
    fastify.decorate('agentConfig', agentConfig);
    fastify.log.info(`已加载智能体配置: ${agentConfigPath}`);
    
    // 初始化智能体服务
    const agentService = require('./services/agentService');
    await agentService.initialize(fastify);
    fastify.decorate('agentService', agentService);
    fastify.log.info('索儿智能体服务已初始化');
    
    // 初始化推荐服务
    const RecommendationsService = require('./services/recommendationsService');
    const recommendationsService = new RecommendationsService(fastify.agentConfig, {
      health_service: fastify.integrations?.health_service,
      recommendation_engine: agentService.models.recommendation_engine,
      database: fastify.integrations?.database
    });
    fastify.decorate('recommendationsService', recommendationsService);
    fastify.log.info('推荐服务已初始化');
    
    // 初始化生活方式服务
    const LifestyleService = require('./services/lifestyleService');
    const lifestyleService = new LifestyleService(fastify.agentConfig, {
      health_service: fastify.integrations?.health_service,
      knowledge_integration: fastify.knowledgeIntegrationService,
      ai_service: agentService,
      database: fastify.integrations?.database
    });
    fastify.decorate('lifestyleService', lifestyleService);
    fastify.log.info('生活方式服务已初始化');
    
    // 初始化日常活动数据库表
    const dbService = require('./models/db.service');
    const { createTables } = require('./models/dailyActivities.model');

    // 异步初始化数据库表
    (async () => {
      try {
        await dbService.connect();
        await createTables(dbService);
        fastify.log.info('数据库表初始化成功');
      } catch (error) {
        fastify.log.error('数据库表初始化失败', { error: error.message });
        // 不抛出错误，允许应用程序继续启动
      }
    })();
    
    // 启动服务监听
    const port = process.env.PORT || 3006;
    const host = process.env.HOST || '0.0.0.0';
    
    await fastify.listen({ port, host });
    fastify.log.info(`索儿服务已启动，监听地址: ${host}:${port}`);
    
    // 优雅关闭处理
    const shutdown = async () => {
      fastify.log.info('正在关闭索儿服务...');
      await fastify.close();
      fastify.log.info('索儿服务已安全关闭');
      process.exit(0);
    };
    
    process.on('SIGTERM', shutdown);
    process.on('SIGINT', shutdown);
    
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
}

// 捕获未处理的异常和拒绝
process.on('uncaughtException', (err) => {
  console.error('未捕获的异常:', err);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('未处理的Promise拒绝:', reason);
});

// 启动服务
if (require.main === module) {
  start();
}

module.exports = fastify;