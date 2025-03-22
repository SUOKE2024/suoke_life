/**
 * 路由索引文件
 */
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const config = require('../config');
const { healthController, metricsController } = require('../controllers');
const LoadBalancer = require('../utils/load-balancer');
const logger = require('../utils/logger');

const router = express.Router();

// 服务负载均衡器映射
const serviceLBMap = new Map();

// 初始化负载均衡器
Object.entries(config.services).forEach(([key, service]) => {
  const serviceName = service.name;
  const loadBalancer = new LoadBalancer(
    service.instances,
    service.loadBalanceStrategy
  );
  serviceLBMap.set(serviceName, loadBalancer);
  logger.info(`初始化负载均衡器: ${serviceName}, 策略: ${service.loadBalanceStrategy}, 实例数: ${service.instances.length}`);
});

// 服务路由配置
const serviceRoutes = {
  // 用户服务
  '/api/v1/users': {
    targetResolver: () => serviceLBMap.get('user-service').getNextUrl(),
    pathRewrite: { '^/api/v1/users': '/api/v1/users' },
    serviceName: 'user-service'
  },
  '/api/v1/profiles': {
    targetResolver: () => serviceLBMap.get('user-service').getNextUrl(),
    pathRewrite: { '^/api/v1/profiles': '/api/v1/profiles' },
    serviceName: 'user-service'
  },
  '/api/v1/health-profiles': {
    targetResolver: () => serviceLBMap.get('user-service').getNextUrl(),
    pathRewrite: { '^/api/v1/health-profiles': '/api/v1/health-profiles' },
    serviceName: 'user-service'
  },
  
  // 认证服务
  '/api/v1/auth': {
    targetResolver: () => serviceLBMap.get('auth-service').getNextUrl(),
    pathRewrite: { '^/api/v1/auth': '/api/v1/auth' },
    serviceName: 'auth-service'
  },
  
  // 认证服务 - 直接路径
  '/auth': {
    targetResolver: () => serviceLBMap.get('auth-service').getNextUrl(),
    pathRewrite: { '^/auth': '/api/v1/auth' },
    serviceName: 'auth-service'
  },
  
  // AI代理服务 - 老客代理
  '/api/v1/agents/laoke': {
    targetResolver: () => serviceLBMap.get('laoke-agent-service').getNextUrl(),
    pathRewrite: { '^/api/v1/agents/laoke': '/api/v1/agents/laoke' },
    serviceName: 'laoke-agent-service'
  },

  // AI代理服务 - 健康助手代理
  '/api/v1/agents/health-assistant': {
    targetResolver: () => serviceLBMap.get('health-assistant-agent-service').getNextUrl(),
    pathRewrite: { '^/api/v1/agents/health-assistant': '/api/v1/agents/health-assistant' },
    serviceName: 'health-assistant-agent-service'
  },

  // AI代理服务 - 代理协调器
  '/api/v1/agents/handoff': {
    targetResolver: () => serviceLBMap.get('agent-coordinator-service').getNextUrl(),
    pathRewrite: { '^/api/v1/agents/handoff': '/api/v1/agents/handoff' },
    serviceName: 'agent-coordinator-service'
  },
  
  '/api/v1/agents/coordinate': {
    targetResolver: () => serviceLBMap.get('agent-coordinator-service').getNextUrl(),
    pathRewrite: { '^/api/v1/agents/coordinate': '/api/v1/agents/coordinate' },
    serviceName: 'agent-coordinator-service'
  },

  // 工具服务 - 文件搜索
  '/api/v1/tools/file_search': {
    targetResolver: () => serviceLBMap.get('file-search-service').getNextUrl(),
    pathRewrite: { '^/api/v1/tools/file_search': '/api/v1/tools/file_search' },
    serviceName: 'file-search-service'
  },

  // 工具服务 - 网络搜索
  '/api/v1/tools/web_search': {
    targetResolver: () => serviceLBMap.get('web-search-service').getNextUrl(),
    pathRewrite: { '^/api/v1/tools/web_search': '/api/v1/tools/web_search' },
    serviceName: 'web-search-service'
  },

  // 代理协调器服务 - 响应管理
  '/api/v1/responses': {
    targetResolver: () => serviceLBMap.get('agent-coordinator-service').getNextUrl(),
    pathRewrite: { '^/api/v1/responses': '/api/v1/responses' },
    serviceName: 'agent-coordinator-service'
  },

  // 代理协调器服务 - 助手管理
  '/api/v1/assistants': {
    targetResolver: () => serviceLBMap.get('agent-coordinator-service').getNextUrl(),
    pathRewrite: { '^/api/v1/assistants': '/api/v1/assistants' },
    serviceName: 'agent-coordinator-service'
  },

  // 代理协调器服务 - 对话线程管理
  '/api/v1/threads': {
    targetResolver: () => serviceLBMap.get('agent-coordinator-service').getNextUrl(),
    pathRewrite: { '^/api/v1/threads': '/api/v1/threads' },
    serviceName: 'agent-coordinator-service'
  },

  // 代理协调器服务 - 运行管理
  '/api/v1/runs': {
    targetResolver: () => serviceLBMap.get('agent-coordinator-service').getNextUrl(),
    pathRewrite: { '^/api/v1/runs': '/api/v1/runs' },
    serviceName: 'agent-coordinator-service'
  },

  // 文件搜索服务 - 向量存储
  '/api/v1/vector_stores': {
    targetResolver: () => serviceLBMap.get('file-search-service').getNextUrl(),
    pathRewrite: { '^/api/v1/vector_stores': '/api/v1/vector_stores' },
    serviceName: 'file-search-service'
  },

  // 文件搜索服务 - 文件管理
  '/api/v1/files': {
    targetResolver: () => serviceLBMap.get('file-search-service').getNextUrl(),
    pathRewrite: { '^/api/v1/files': '/api/v1/files' },
    serviceName: 'file-search-service'
  },
  
  // 健康服务
  '/api/v1/health': {
    targetResolver: () => serviceLBMap.get('health-service').getNextUrl(),
    pathRewrite: { '^/api/v1/health': '/api/v1/health' },
    serviceName: 'health-service'
  },
  
  // 生活记录服务
  '/api/v1/life-records': {
    targetResolver: () => serviceLBMap.get('life-record-service').getNextUrl(),
    pathRewrite: { '^/api/v1/life-records': '/api/v1/life-records' },
    serviceName: 'life-record-service'
  },
  
  // 知识图谱服务
  '/api/v1/knowledge': {
    targetResolver: () => serviceLBMap.get('knowledge-graph-service').getNextUrl(),
    pathRewrite: { '^/api/v1/knowledge': '/api/v1/knowledge' },
    serviceName: 'knowledge-graph-service'
  },
  
  // 多模态处理服务
  '/api/v1/multimodal': {
    targetResolver: () => serviceLBMap.get('multimodal-processor-service').getNextUrl(),
    pathRewrite: { '^/api/v1/multimodal': '/api/v1/multimodal' },
    serviceName: 'multimodal-processor-service'
  },
  
  // RAG服务
  '/api/v1/rag': {
    targetResolver: () => serviceLBMap.get('rag-service').getNextUrl(),
    pathRewrite: { '^/api/v1/rag': '/api/v1/rag' },
    serviceName: 'rag-service'
  }
};

// 代理选项配置
const getProxyOptions = (routeConfig) => ({
  // 负载均衡目标
  router: (req) => {
    try {
      const target = routeConfig.targetResolver();
      logger.debug(`路由到服务: ${routeConfig.serviceName}, 目标: ${target}`);
      return target;
    } catch (error) {
      logger.error(`负载均衡失败: ${error.message}`);
      throw error;
    }
  },
  
  // 记录代理请求
  logLevel: config.server.env === 'development' ? 'debug' : 'info',
  
  // 路径重写
  pathRewrite: routeConfig.pathRewrite,
  
  // 指定请求负载大小限制
  proxyTimeout: 30000, // 30秒
  
  // 处理响应错误
  onError: (err, req, res) => {
    const serviceName = routeConfig.serviceName;
    logger.error(`代理请求错误: ${serviceName}`, { error: err.message, path: req.path });
    
    // 如果是连接错误，标记服务不健康
    if (err.code === 'ECONNREFUSED' || err.code === 'ETIMEDOUT') {
      try {
        const target = req.headers['x-forwarded-host'] || '';
        logger.warn(`服务连接失败: ${serviceName}, 目标: ${target}`);
        
        // 尝试获取负载均衡器并标记服务不健康
        const loadBalancer = serviceLBMap.get(serviceName);
        if (loadBalancer) {
          loadBalancer.markUnhealthy(target);
        }
      } catch (error) {
        logger.error(`标记服务不健康失败: ${error.message}`);
      }
    }
    
    res.status(503).json({
      error: '服务暂时不可用',
      message: `服务 ${serviceName} 请求失败: ${err.message}`,
      service: serviceName
    });
  },
  
  // 处理代理请求开始
  onProxyReq: (proxyReq, req, res) => {
    // 可以在这里修改请求头或其他请求属性
    proxyReq.setHeader('X-Forwarded-By', 'Suoke-API-Gateway');
    proxyReq.setHeader('X-Service-Name', routeConfig.serviceName);
    
    // 记录原始主机信息
    const target = proxyReq.getHeaders().host;
    req.headers['x-forwarded-host'] = target;
    
    // 将客户端IP传递给服务
    if (req.ip) {
      proxyReq.setHeader('X-Real-IP', req.ip);
    }
  },
  
  // 处理代理响应
  onProxyRes: (proxyRes, req, res) => {
    // 添加响应头
    proxyRes.headers['X-Powered-By'] = 'Suoke-API-Gateway';
    proxyRes.headers['X-Service'] = routeConfig.serviceName;
    
    // 标记服务健康
    try {
      const target = req.headers['x-forwarded-host'] || '';
      if (target) {
        const loadBalancer = serviceLBMap.get(routeConfig.serviceName);
        if (loadBalancer) {
          loadBalancer.markHealthy(target);
        }
      }
    } catch (error) {
      logger.error(`标记服务健康失败: ${error.message}`);
    }
  },
  
  // 支持动态服务发现
  changeOrigin: true
});

// 注册代理路由
Object.entries(serviceRoutes).forEach(([path, routeConfig]) => {
  router.use(path, createProxyMiddleware(getProxyOptions(routeConfig)));
});

// 健康检查路由
router.get('/health', healthController.getHealth);
router.get('/health/ready', healthController.getReadiness);

// 服务指标路由
router.get('/metrics', metricsController.getMetrics);

// 添加网关内部API
router.get('/api/gateway/services', (req, res) => {
  const services = {};
  
  serviceLBMap.forEach((loadBalancer, serviceName) => {
    services[serviceName] = {
      instances: loadBalancer.serviceUrls,
      health: loadBalancer.getHealthStatus(),
      strategy: loadBalancer.strategy
    };
  });
  
  res.json({
    services,
    timestamp: Date.now()
  });
});

// 启动定期健康检查
setInterval(() => {
  logger.info('开始定期健康检查...');
  
  serviceLBMap.forEach((loadBalancer, serviceName) => {
    loadBalancer.serviceUrls.forEach(url => {
      loadBalancer.checkHealth(url).catch(error => {
        logger.error(`健康检查失败: ${serviceName} ${url}`, { error: error.message });
      });
    });
  });
}, config.server.healthCheck.interval);

module.exports = router; 