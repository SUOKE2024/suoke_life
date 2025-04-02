/**
 * 内部认证中间件
 * 用于服务间安全通信
 */
const { logger } = require('@suoke/shared').utils;

/**
 * 验证内部API调用的令牌
 */
const internalAuthMiddleware = (req, res, next) => {
  try {
    // 获取同步令牌
    const syncToken = req.headers['x-sync-token'];
    const sourceRegion = req.headers['x-source-region'];
    const internalApiKey = req.headers['x-internal-api-key'];
    const serviceKey = process.env.INTERNAL_SERVICE_KEY;
    
    // 如果提供了内部API密钥，验证它
    if (internalApiKey) {
      if (internalApiKey === serviceKey) {
        return next(); // 密钥匹配，允许访问
      } else {
        logger.warn('内部API密钥无效');
        return res.status(401).json({ success: false, message: '内部认证失败' });
      }
    }
    
    // 如果提供了同步令牌，验证它 (用于跨区域同步)
    if (syncToken && sourceRegion) {
      const isValidSyncToken = validateSyncToken(syncToken, sourceRegion);
      
      if (isValidSyncToken) {
        return next(); // 同步令牌有效，允许访问
      } else {
        logger.warn(`来自区域 ${sourceRegion} 的同步令牌无效`);
        return res.status(401).json({ success: false, message: '同步令牌无效' });
      }
    }
    
    // 检查请求来源IP
    const requestIp = getClientIp(req);
    
    // 允许的内部IP地址或CIDR范围
    const allowedInternalIps = getAllowedInternalIps();
    
    // 检查请求IP是否在允许列表中
    if (isIpAllowed(requestIp, allowedInternalIps)) {
      return next(); // IP在允许列表中，允许访问
    }
    
    // 如果运行在开发环境中，允许来自本地回环地址的访问
    if (process.env.NODE_ENV === 'development' && isLocalhost(requestIp)) {
      return next();
    }
    
    // 所有认证方法都失败
    logger.warn(`内部API调用认证失败，来源IP: ${requestIp}`);
    return res.status(401).json({ success: false, message: '内部认证失败' });
  } catch (error) {
    logger.error(`内部认证中间件错误: ${error.message}`);
    return res.status(500).json({ success: false, message: '内部服务器错误' });
  }
};

/**
 * 获取客户端IP地址
 * @param {Object} req 请求对象
 * @returns {string} IP地址
 */
const getClientIp = (req) => {
  // 检查常见的代理头
  const xForwardedFor = req.headers['x-forwarded-for'];
  if (xForwardedFor) {
    // X-Forwarded-For可能包含多个IP，第一个通常是客户端的真实IP
    const ips = xForwardedFor.split(',').map(ip => ip.trim());
    return ips[0];
  }
  
  // 检查其他可能的代理头
  if (req.headers['x-real-ip']) {
    return req.headers['x-real-ip'];
  }
  
  // 回退到链接的远程地址
  return req.connection.remoteAddress || 
         req.socket.remoteAddress || 
         (req.connection.socket ? req.connection.socket.remoteAddress : null) || 
         '0.0.0.0';
};

/**
 * 获取允许的内部IP地址列表
 * @returns {Array} 允许的IP列表
 */
const getAllowedInternalIps = () => {
  // 从环境变量中获取允许的内部IP地址
  const envAllowedIps = process.env.ALLOWED_INTERNAL_IPS || '';
  const internalIpList = envAllowedIps.split(',').map(ip => ip.trim()).filter(Boolean);
  
  // 服务网格IP范围
  const serviceMeshRange = process.env.SERVICE_MESH_CIDR || '10.0.0.0/8';
  
  // 添加Kubernetes集群内网络
  const kubeServices = ['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'];
  
  // 本地回环地址
  const localhostRange = ['127.0.0.0/8', '::1/128'];
  
  // 返回完整的允许列表
  return [
    ...internalIpList,
    serviceMeshRange,
    ...kubeServices,
    ...localhostRange
  ];
};

/**
 * 检查IP是否在允许列表中
 * @param {string} ip 要检查的IP地址
 * @param {Array} allowedIps 允许的IP列表
 * @returns {boolean} 是否允许
 */
const isIpAllowed = (ip, allowedIps) => {
  try {
    if (!ip) return false;
    
    // 如果IP完全匹配允许列表中的任何一个，直接返回true
    if (allowedIps.includes(ip)) return true;
    
    // 检查IP是否在任何CIDR范围内
    for (const cidr of allowedIps) {
      if (cidr.includes('/')) {
        if (isIpInCidr(ip, cidr)) {
          return true;
        }
      }
    }
    
    return false;
  } catch (error) {
    logger.error(`IP检查错误: ${error.message}`);
    return false;
  }
};

/**
 * 检查IP是否在CIDR范围内
 * 简化版实现
 * @param {string} ip IP地址
 * @param {string} cidr CIDR范围
 * @returns {boolean} 是否在范围内
 */
const isIpInCidr = (ip, cidr) => {
  try {
    // 仅支持IPv4
    if (ip.includes(':') || cidr.includes(':')) {
      // IPv6 - 简单比较前缀
      const ipv6Prefix = ip.split(':').slice(0, 4).join(':');
      const cidrPrefix = cidr.split(':').slice(0, 4).join(':');
      return ipv6Prefix === cidrPrefix;
    }
    
    // IPv4
    const [range, bits = 32] = cidr.split('/');
    const mask = ~(2 ** (32 - bits) - 1);
    
    const ipInt = ipToInt(ip);
    const rangeInt = ipToInt(range);
    
    return (ipInt & mask) === (rangeInt & mask);
  } catch (error) {
    logger.error(`CIDR检查错误: ${error.message}`);
    return false;
  }
};

/**
 * 将IPv4地址转换为整数
 * @param {string} ip IPv4地址
 * @returns {number} 整数表示
 */
const ipToInt = (ip) => {
  return ip.split('.')
    .reduce((int, octet) => (int << 8) + parseInt(octet, 10), 0) >>> 0;
};

/**
 * 检查IP是否是本地回环地址
 * @param {string} ip IP地址
 * @returns {boolean} 是否是本地回环地址
 */
const isLocalhost = (ip) => {
  return ip === '127.0.0.1' || 
         ip === '::1' || 
         ip === '::ffff:127.0.0.1' || 
         ip.startsWith('127.');
};

/**
 * 验证同步令牌
 * @param {string} token 同步令牌
 * @param {string} sourceRegion 源区域
 * @returns {boolean} 令牌是否有效
 */
const validateSyncToken = (token, sourceRegion) => {
  try {
    // Base64解码令牌
    const decoded = Buffer.from(token, 'base64').toString('utf-8');
    const [tokenSourceRegion, targetRegion, timestampStr, secret] = decoded.split(':');
    
    // 验证令牌来源区域与请求头中的区域是否匹配
    if (tokenSourceRegion !== sourceRegion) {
      logger.warn(`同步令牌区域不匹配: ${tokenSourceRegion} != ${sourceRegion}`);
      return false;
    }
    
    // 验证目标区域是否是当前区域
    const currentRegion = process.env.POD_REGION || 'unknown';
    if (targetRegion !== currentRegion) {
      logger.warn(`同步令牌目标区域不匹配: ${targetRegion} != ${currentRegion}`);
      return false;
    }
    
    // 检查令牌时间戳是否在有效期内（10分钟）
    const timestamp = parseInt(timestampStr, 10);
    const now = Math.floor(Date.now() / 1000);
    if (now - timestamp > 600) { // 10分钟有效期
      logger.warn(`同步令牌已过期: ${now - timestamp}秒前`);
      return false;
    }
    
    // 验证令牌中的密钥是否匹配
    const syncSecret = process.env.SYNC_SECRET || 'default-sync-secret';
    if (secret !== syncSecret) {
      logger.warn('同步令牌密钥不匹配');
      return false;
    }
    
    return true;
  } catch (error) {
    logger.error(`验证同步令牌错误: ${error.message}`);
    return false;
  }
};

module.exports = {
  internalAuthMiddleware
}; 