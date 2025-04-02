/**
 * Vault中间件
 * 用于确保在请求处理前已初始化Vault配置
 */
const vaultConfig = require('../config/vault-config');
const logger = require('../utils/logger');

/**
 * 初始化Vault配置的中间件
 */
async function initializeVault(req, res, next) {
  try {
    // 确保Vault配置已经初始化
    if (vaultConfig.enabled && !vaultConfig.configCache) {
      await vaultConfig.initialize();
    }
    
    // 将Vault配置添加到请求中，便于后续中间件和路由使用
    req.vaultConfig = vaultConfig;
    
    next();
  } catch (error) {
    logger.error('Vault初始化失败', { error: error.message });
    next(error);
  }
}

module.exports = {
  initializeVault
};