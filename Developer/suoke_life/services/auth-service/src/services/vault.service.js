/**
 * Vault服务
 * 用于安全凭证管理，支持与HashiCorp Vault集成
 */
const axios = require('axios');
const { logger } = require('@suoke/shared').utils;

// 凭证缓存
let secretsCache = {};
let tokenCache = null;
let lastFetchTime = 0;
const CACHE_TTL = 3600000; // 缓存有效期1小时

class VaultService {
  constructor() {
    this.vaultEnabled = process.env.VAULT_ENABLED === 'true';
    this.vaultUrl = process.env.VAULT_URL || 'http://vault:8200';
    this.vaultToken = process.env.VAULT_TOKEN || '';
    this.vaultRoleId = process.env.VAULT_ROLE_ID || '';
    this.vaultSecretId = process.env.VAULT_SECRET_ID || '';
    this.vaultAuthMethod = process.env.VAULT_AUTH_METHOD || 'token'; // token, approle, k8s
    this.vaultSecretPath = process.env.VAULT_SECRET_PATH || 'kv/data/auth-service';
    this.k8sServiceAccount = process.env.K8S_SERVICE_ACCOUNT_PATH || '/var/run/secrets/kubernetes.io/serviceaccount/token';
    
    // 如果未启用Vault，使用环境变量作为后备
    if (!this.vaultEnabled) {
      logger.info('Vault未启用，使用环境变量作为密钥源');
      this._loadSecretsFromEnvironment();
    }
  }

  /**
   * 从环境变量加载凭证
   * @private
   */
  _loadSecretsFromEnvironment() {
    secretsCache = {
      'database': {
        'host': process.env.DB_HOST,
        'user': process.env.DB_USER,
        'password': process.env.DB_PASSWORD,
        'database': process.env.DB_NAME
      },
      'redis': {
        'host': process.env.REDIS_HOST,
        'port': process.env.REDIS_PORT,
        'password': process.env.REDIS_PASSWORD
      },
      'auth': {
        'jwt_secret': process.env.JWT_SECRET,
        'refresh_token_secret': process.env.REFRESH_TOKEN_SECRET
      },
      'encryption': {
        'key': process.env.ENCRYPTION_KEY
      }
    };
    
    lastFetchTime = Date.now();
  }

  /**
   * 获取Vault认证令牌
   * @returns {Promise<string>} 认证令牌
   * @private
   */
  async _getVaultToken() {
    try {
      // 如果已有缓存的令牌并且未过期，直接返回
      if (tokenCache && tokenCache.expiresAt > Date.now()) {
        return tokenCache.token;
      }
      
      // 根据认证方法获取令牌
      let token;
      
      switch (this.vaultAuthMethod) {
        case 'token':
          // 直接使用配置的令牌
          token = this.vaultToken;
          break;
          
        case 'approle':
          // 使用AppRole认证
          if (!this.vaultRoleId || !this.vaultSecretId) {
            throw new Error('使用AppRole认证时必须提供Role ID和Secret ID');
          }
          
          const appRoleResponse = await axios.post(
            `${this.vaultUrl}/v1/auth/approle/login`,
            {
              role_id: this.vaultRoleId,
              secret_id: this.vaultSecretId
            }
          );
          
          token = appRoleResponse.data.auth.client_token;
          break;
          
        case 'k8s':
          // 使用Kubernetes认证
          // 读取服务账号令牌
          const fs = require('fs');
          const k8sToken = fs.readFileSync(this.k8sServiceAccount, 'utf8');
          
          // 使用服务账号令牌向Vault验证
          const k8sAuthResponse = await axios.post(
            `${this.vaultUrl}/v1/auth/kubernetes/login`,
            {
              role: process.env.VAULT_K8S_ROLE || 'auth-service',
              jwt: k8sToken
            }
          );
          
          token = k8sAuthResponse.data.auth.client_token;
          break;
          
        default:
          throw new Error(`不支持的Vault认证方法: ${this.vaultAuthMethod}`);
      }
      
      // 缓存令牌（默认TTL为1小时，除非响应中指定了不同的值）
      const ttl = 3600000; // 默认1小时
      tokenCache = {
        token,
        expiresAt: Date.now() + ttl
      };
      
      return token;
    } catch (error) {
      logger.error(`获取Vault令牌失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 从Vault获取凭证
   * @returns {Promise<Object>} 凭证对象
   * @private
   */
  async _fetchSecretsFromVault() {
    try {
      // 如果Vault未启用，使用环境变量
      if (!this.vaultEnabled) {
        this._loadSecretsFromEnvironment();
        return secretsCache;
      }
      
      // 获取认证令牌
      const token = await this._getVaultToken();
      
      // 从Vault获取凭证
      const response = await axios.get(
        `${this.vaultUrl}/v1/${this.vaultSecretPath}`,
        {
          headers: {
            'X-Vault-Token': token
          }
        }
      );
      
      // 提取数据
      const secrets = response.data.data.data;
      
      // 更新缓存
      secretsCache = secrets;
      lastFetchTime = Date.now();
      
      logger.info('成功从Vault获取凭证');
      
      return secrets;
    } catch (error) {
      logger.error(`从Vault获取凭证失败: ${error.message}`);
      
      // 如果请求失败但有缓存的凭证，使用缓存
      if (Object.keys(secretsCache).length > 0) {
        logger.info('使用缓存的凭证');
        return secretsCache;
      }
      
      // 作为后备，使用环境变量
      logger.info('使用环境变量作为凭证后备');
      this._loadSecretsFromEnvironment();
      return secretsCache;
    }
  }

  /**
   * 获取凭证
   * @param {string} category 凭证类别（database, redis, auth等）
   * @param {string} key 凭证键名
   * @returns {Promise<string>} 凭证值
   */
  async getSecret(category, key) {
    try {
      // 检查缓存是否过期
      if (Date.now() - lastFetchTime > CACHE_TTL) {
        await this._fetchSecretsFromVault();
      }
      
      // 从缓存中获取凭证
      if (secretsCache[category] && secretsCache[category][key] !== undefined) {
        return secretsCache[category][key];
      }
      
      // 如果在缓存中找不到，尝试从环境变量获取
      // 遵循命名约定，例如 DATABASE_PASSWORD 对应 database.password
      const envKey = `${category.toUpperCase()}_${key.toUpperCase()}`;
      if (process.env[envKey]) {
        return process.env[envKey];
      }
      
      // 找不到凭证
      logger.warn(`找不到凭证: ${category}.${key}`);
      return null;
    } catch (error) {
      logger.error(`获取凭证失败: ${error.message}`);
      
      // 尝试从环境变量获取
      const envKey = `${category.toUpperCase()}_${key.toUpperCase()}`;
      return process.env[envKey] || null;
    }
  }

  /**
   * 获取特定类别的所有凭证
   * @param {string} category 凭证类别
   * @returns {Promise<Object>} 凭证对象
   */
  async getSecretCategory(category) {
    try {
      // 检查缓存是否过期
      if (Date.now() - lastFetchTime > CACHE_TTL) {
        await this._fetchSecretsFromVault();
      }
      
      // 从缓存中获取凭证类别
      if (secretsCache[category]) {
        return secretsCache[category];
      }
      
      // 找不到凭证类别
      logger.warn(`找不到凭证类别: ${category}`);
      return {};
    } catch (error) {
      logger.error(`获取凭证类别失败: ${error.message}`);
      return {};
    }
  }

  /**
   * 刷新凭证缓存
   * @returns {Promise<Object>} 结果对象
   */
  async refreshSecrets() {
    try {
      await this._fetchSecretsFromVault();
      return { success: true };
    } catch (error) {
      logger.error(`刷新凭证失败: ${error.message}`);
      return { success: false, message: error.message };
    }
  }

  /**
   * 获取数据库凭证
   * @returns {Promise<Object>} 数据库连接配置
   */
  async getDatabaseCredentials() {
    return await this.getSecretCategory('database');
  }

  /**
   * 获取Redis凭证
   * @returns {Promise<Object>} Redis连接配置
   */
  async getRedisCredentials() {
    return await this.getSecretCategory('redis');
  }

  /**
   * 获取JWT密钥
   * @returns {Promise<string>} JWT密钥
   */
  async getJwtSecret() {
    return await this.getSecret('auth', 'jwt_secret');
  }

  /**
   * 获取刷新令牌密钥
   * @returns {Promise<string>} 刷新令牌密钥
   */
  async getRefreshTokenSecret() {
    return await this.getSecret('auth', 'refresh_token_secret');
  }

  /**
   * 获取加密密钥
   * @returns {Promise<string>} 加密密钥
   */
  async getEncryptionKey() {
    return await this.getSecret('encryption', 'key');
  }

  /**
   * 健康检查
   * @returns {Promise<boolean>} 是否健康
   */
  async healthCheck() {
    try {
      // 如果Vault未启用，直接返回成功
      if (!this.vaultEnabled) {
        return true;
      }
      
      // 检查与Vault的连接
      const response = await axios.get(`${this.vaultUrl}/v1/sys/health`);
      return response.status === 200 && response.data.initialized === true;
    } catch (error) {
      logger.error(`Vault健康检查失败: ${error.message}`);
      
      // 如果有缓存的凭证，依然认为是健康的
      return Object.keys(secretsCache).length > 0;
    }
  }
}

const vaultService = new VaultService();

module.exports = {
  vaultService
};