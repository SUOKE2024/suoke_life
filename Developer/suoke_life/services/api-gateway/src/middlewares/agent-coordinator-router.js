/**
 * 代理协调器路由中间件
 * 处理代理协调器服务的请求路由
 */
const { createProxyMiddleware } = require('http-proxy-middleware');
const config = require('../config');
const logger = require('../utils/logger');

/**
 * 创建代理协调器路由中间件
 */
function agentCoordinatorRouter(req, res, next) {
  // 检查是否匹配代理协调器服务的路径
  if (req.path.startsWith('/api/v1/agents/coordinator')) {
    logger.debug('路由请求到代理协调器服务', { path: req.path });
    
    // 从配置或环境变量获取代理协调器服务URL
    const agentCoordinatorUrl = process.env.AGENT_COORDINATOR_SERVICE_URL || 
                               'http://agent-coordinator-service.suoke.svc.cluster.local';
    
    // 设置代理选项
    const proxyOptions = {
      target: agentCoordinatorUrl,
      changeOrigin: true,
      pathRewrite: {
        '^/api/v1/agents/coordinator': '' // 路径重写
      },
      onProxyReq: (proxyReq, req, res) => {
        // 添加API网关头
        proxyReq.setHeader('X-API-Gateway', 'true');
        
        // 如果有请求ID，转发
        if (req.headers['x-request-id']) {
          proxyReq.setHeader('X-Request-ID', req.headers['x-request-id']);
        } else {
          // 生成请求ID
          const requestId = `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
          proxyReq.setHeader('X-Request-ID', requestId);
        }
        
        logger.debug('代理请求到代理协调器服务', { 
          path: req.path, 
          target: agentCoordinatorUrl,
          method: req.method
        });
      },
      onProxyRes: (proxyRes, req, res) => {
        logger.debug('从代理协调器服务接收响应', { 
          path: req.path,
          status: proxyRes.statusCode
        });
      },
      onError: (err, req, res) => {
        logger.error('代理到代理协调器服务时发生错误', { error: err.message });
        res.status(500).json({
          error: '代理服务请求失败',
          message: '无法连接到代理协调器服务'
        });
      }
    };
    
    // 创建并应用代理中间件
    return createProxyMiddleware(proxyOptions)(req, res, next);
  }
  
  // 不匹配，继续下一个中间件
  next();
}

module.exports = agentCoordinatorRouter;