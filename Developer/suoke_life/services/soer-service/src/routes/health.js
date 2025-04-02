'use strict';

/**
 * 健康检查路由
 * 用于Kubernetes健康检查和服务状态监控
 */
module.exports = async function (fastify, opts) {
  // 常规健康检查
  fastify.get('/', async (request, reply) => {
    return { status: 'ok', service: 'soer-service', timestamp: new Date().toISOString() };
  });

  // 就绪探针
  fastify.get('/ready', async (request, reply) => {
    // 检查依赖服务连接状态
    const checks = {
      redis: fastify.redis ? await checkRedisConnection(fastify.redis) : 'not_configured',
      agent: fastify.agentService ? await fastify.agentService.isReady() : false
    };

    const isReady = Object.values(checks).every(status => 
      status === true || status === 'not_configured'
    );

    if (!isReady) {
      reply.code(503);
      return {
        status: 'not_ready',
        checks,
        timestamp: new Date().toISOString()
      };
    }

    return {
      status: 'ready',
      checks,
      timestamp: new Date().toISOString()
    };
  });

  // 启动探针
  fastify.get('/startup', async (request, reply) => {
    // 检查服务是否已启动完成必要的初始化
    const agentReady = fastify.agentService ? await fastify.agentService.isInitialized() : false;

    if (!agentReady) {
      reply.code(503);
      return {
        status: 'initializing',
        message: '智能体服务正在初始化',
        timestamp: new Date().toISOString()
      };
    }

    return {
      status: 'started',
      message: '服务已完成启动',
      timestamp: new Date().toISOString()
    };
  });

  // 详细状态
  fastify.get('/status', async (request, reply) => {
    const memory = process.memoryUsage();
    const uptime = process.uptime();
    
    // 服务状态数据
    let serviceStatus = {
      status: 'healthy',
      uptime: formatUptime(uptime),
      uptime_seconds: uptime,
      memory: {
        rss: `${Math.round(memory.rss / 1024 / 1024)} MB`,
        heapTotal: `${Math.round(memory.heapTotal / 1024 / 1024)} MB`,
        heapUsed: `${Math.round(memory.heapUsed / 1024 / 1024)} MB`,
        external: `${Math.round(memory.external / 1024 / 1024)} MB`
      },
      version: fastify.agentConfig?.agent?.version || '1.0.0',
      node_version: process.version,
      platform: process.platform,
      timestamp: new Date().toISOString()
    };
    
    // 如果有可用的智能体服务，获取其状态
    if (fastify.agentService) {
      const agentStatus = await fastify.agentService.getStatus();
      serviceStatus.agent = agentStatus;
    }
    
    // 如果有可用的Redis，获取其状态
    if (fastify.redis) {
      try {
        const redisInfo = await fastify.redis.info();
        serviceStatus.redis = {
          status: 'connected',
          info: parseRedisInfo(redisInfo)
        };
      } catch (error) {
        serviceStatus.redis = {
          status: 'error',
          error: error.message
        };
      }
    }
    
    return serviceStatus;
  });

  // 内部帮助函数
  
  // 检查Redis连接
  async function checkRedisConnection(redis) {
    try {
      await redis.ping();
      return true;
    } catch (error) {
      fastify.log.error(`Redis连接检查失败: ${error.message}`);
      return false;
    }
  }
  
  // 格式化运行时间
  function formatUptime(uptime) {
    const days = Math.floor(uptime / 86400);
    const hours = Math.floor((uptime % 86400) / 3600);
    const minutes = Math.floor((uptime % 3600) / 60);
    const seconds = Math.floor(uptime % 60);
    
    const parts = [];
    if (days > 0) parts.push(`${days}天`);
    if (hours > 0) parts.push(`${hours}小时`);
    if (minutes > 0) parts.push(`${minutes}分钟`);
    if (seconds > 0 || parts.length === 0) parts.push(`${seconds}秒`);
    
    return parts.join(' ');
  }
  
  // 解析Redis信息
  function parseRedisInfo(info) {
    const lines = info.split('\r\n');
    const parsed = {};
    let currentSection = '';
    
    lines.forEach(line => {
      if (line.startsWith('#')) {
        currentSection = line.substring(2).toLowerCase();
        parsed[currentSection] = {};
      } else if (line.includes(':')) {
        const [key, value] = line.split(':');
        if (currentSection && key) {
          parsed[currentSection][key] = value;
        }
      }
    });
    
    // 只返回关键信息
    return {
      server: parsed.server ? {
        redis_version: parsed.server.redis_version,
        uptime_in_seconds: parsed.server.uptime_in_seconds
      } : undefined,
      memory: parsed.memory ? {
        used_memory_human: parsed.memory.used_memory_human,
        used_memory_peak_human: parsed.memory.used_memory_peak_human
      } : undefined,
      clients: parsed.clients ? {
        connected_clients: parsed.clients.connected_clients
      } : undefined
    };
  }
};