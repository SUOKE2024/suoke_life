/**
 * 知识路由中间件
 * 
 * 根据查询内容智能分发到不同的知识服务
 */
const { createProxyMiddleware } = require('http-proxy-middleware');
const logger = require('../utils/logger');

/**
 * 路由模式
 */
const ROUTE_PATTERNS = {
  // 路径匹配
  PATH_PATTERN: /^\/api\/v1\/knowledge(\/|$)/,
  
  // 领域关键词
  PRECISION_MEDICINE: /基因|遗传|基因组|测序|精准医学|个体化医疗/,
  MULTIMODAL_HEALTH: /多模态|生物信号|声学特征|图像特征|多因素|交互模型/,
  ENVIRONMENTAL_HEALTH: /环境|空气质量|水质|污染物|室内环境|PM2.5|辐射/,
  PSYCHOLOGICAL_HEALTH: /心理|焦虑|抑郁|压力|精神|情绪|认知/,
  TRADITIONAL_CULTURE: /中医|针灸|艾灸|经络|穴位|四诊|望闻问切|阴阳|五行|辨证/,
  MODERN_MEDICINE: /西医|诊断|治疗|临床|药物|症状|疾病|手术|检查|影像/
};

/**
 * 服务类型
 */
const SERVICE_TYPES = {
  PRECISION_MEDICINE: 'precision-medicine',
  MULTIMODAL_HEALTH: 'multimodal-health',
  ENVIRONMENTAL_HEALTH: 'environmental-health',
  PSYCHOLOGICAL_HEALTH: 'psychological-health',
  TRADITIONAL_CULTURE: 'traditional-culture',
  MODERN_MEDICINE: 'modern-medicine',
  DEFAULT: 'default'
};

/**
 * 从请求对象中获取查询内容
 * @param {Object} req Express请求对象
 * @returns {string} 查询内容或空字符串
 */
function getQueryContent(req) {
  // 从q或query参数获取
  return (req.query.q || req.query.query || '').toString();
}

/**
 * 判断查询内容所属领域
 * @param {string} query 查询内容
 * @returns {string} 领域类型
 */
function getDomainType(query) {
  if (ROUTE_PATTERNS.PRECISION_MEDICINE.test(query)) {
    return SERVICE_TYPES.PRECISION_MEDICINE;
  }
  
  if (ROUTE_PATTERNS.MULTIMODAL_HEALTH.test(query)) {
    return SERVICE_TYPES.MULTIMODAL_HEALTH;
  }
  
  if (ROUTE_PATTERNS.ENVIRONMENTAL_HEALTH.test(query)) {
    return SERVICE_TYPES.ENVIRONMENTAL_HEALTH;
  }
  
  if (ROUTE_PATTERNS.PSYCHOLOGICAL_HEALTH.test(query)) {
    return SERVICE_TYPES.PSYCHOLOGICAL_HEALTH;
  }
  
  if (ROUTE_PATTERNS.TRADITIONAL_CULTURE.test(query)) {
    return SERVICE_TYPES.TRADITIONAL_CULTURE;
  }
  
  if (ROUTE_PATTERNS.MODERN_MEDICINE.test(query)) {
    return SERVICE_TYPES.MODERN_MEDICINE;
  }
  
  return SERVICE_TYPES.DEFAULT;
}

/**
 * 获取适合领域类型的服务
 * @param {string} domainType 领域类型
 * @returns {string} 服务名称
 */
function getServiceForDomain(domainType) {
  switch (domainType) {
    case SERVICE_TYPES.PRECISION_MEDICINE:
      return 'knowledge-base-service';
    
    case SERVICE_TYPES.MULTIMODAL_HEALTH:
      return 'knowledge-base-service';
    
    case SERVICE_TYPES.ENVIRONMENTAL_HEALTH:
      return 'knowledge-base-service';
    
    case SERVICE_TYPES.PSYCHOLOGICAL_HEALTH:
      return 'knowledge-base-service';
    
    case SERVICE_TYPES.TRADITIONAL_CULTURE:
      return 'knowledge-graph-service';
    
    case SERVICE_TYPES.MODERN_MEDICINE:
      return 'knowledge-base-service';
    
    case SERVICE_TYPES.DEFAULT:
    default:
      return 'agent-coordinator-service';
  }
}

/**
 * 知识路由中间件
 * @param {Object} req Express请求对象
 * @param {Object} res Express响应对象
 * @param {Function} next Express下一个中间件
 */
function knowledgeRouter(req, res, next) {
  try {
    // 检查是否匹配知识路由路径
    if (!ROUTE_PATTERNS.PATH_PATTERN.test(req.path)) {
      return next();
    }
    
    // 获取查询内容
    const query = getQueryContent(req);
    logger.debug(`知识路由查询内容: ${query}`);
    
    // 获取领域类型
    const domainType = getDomainType(query);
    logger.debug(`查询领域分类: ${domainType}`);
    
    // 获取适合的服务
    const serviceName = getServiceForDomain(domainType);
    logger.debug(`选择服务: ${serviceName}`);
    
    // 获取负载均衡器映射
    const serviceLBMap = req.app.get('serviceLBMap');
    
    if (!serviceLBMap || !serviceLBMap.has(serviceName)) {
      logger.error(`未找到服务负载均衡器: ${serviceName}`);
      return res.status(503).json({ error: '服务暂不可用' });
    }
    
    // 获取负载均衡器
    const lb = serviceLBMap.get(serviceName);
    
    // 获取目标URL
    const targetUrl = lb.getNextUrl();
    logger.debug(`转发到目标URL: ${targetUrl}`);
    
    // 创建代理
    const proxy = createProxyMiddleware({
      target: targetUrl,
      changeOrigin: true,
      pathRewrite: {
        '^/api/v1/knowledge': '/api/v1'  // 重写路径
      },
      logLevel: 'warn'
    });
    
    // 执行代理
    return proxy(req, res, next);
  } catch (error) {
    logger.error(`知识路由中间件错误: ${error.message}`);
    return res.status(500).json({ error: '服务器内部错误' });
  }
}

module.exports = knowledgeRouter;