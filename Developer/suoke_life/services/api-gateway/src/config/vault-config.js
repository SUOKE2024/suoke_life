/**
 * Vault配置模块
 * 用于与Vault集成，获取动态配置和敏感信息
 */
const fs = require('fs');
const axios = require('axios');
const logger = require('../utils/logger');

class VaultConfig {
  constructor() {
    this.enabled = process.env.VAULT_ENABLED === 'true';
    this.endpoint = process.env.VAULT_ENDPOINT || 'http://vault:8200';
    this.token = process.env.VAULT_TOKEN;
    this.path = process.env.VAULT_PATH || 'secret/data/api-gateway';
    this.authMethod = process.env.VAULT_AUTH_METHOD || 'token';
    this.vaultK8sRole = process.env.VAULT_K8S_ROLE || 'api-gateway';
    this.k8sServiceAccountPath = process.env.K8S_SERVICE_ACCOUNT_PATH || '/var/run/secrets/kubernetes.io/serviceaccount/token';
    this.vaultConfigPath = process.env.VAULT_CONFIG_PATH || '/vault/secrets/config';
    
    // 从Vault代理注入的配置
    this.vaultMountedConfig = null;
    this.vaultToken = null;
    
    // 配置缓存
    this.configCache = null;
    this.lastFetchTime = 0;
    this.cacheTTL = 300000; // 5分钟缓存
  }
  
  /**
   * 初始化Vault配置
   */
  async initialize() {
    if (!this.enabled) {
      logger.info('Vault集成未启用');
      return;
    }
    
    try {
      logger.info('初始化Vault配置');
      
      // 尝试读取Vault代理注入的配置
      await this._loadInjectedConfig();
      
      // 使用K8S认证获取令牌
      if (this.authMethod === 'k8s' && !this.vaultToken) {
        await this._authenticateWithK8s();
      }
      
      // 获取配置
      await this.refreshConfig();
      
      logger.info('Vault配置初始化完成');
    } catch (error) {
      logger.error('Vault配置初始化失败', { error: error.message });
    }
  }
  
  /**
   * 从Vault Sidecar注入的文件加载配置
   */
  async _loadInjectedConfig() {
    try {
      if (fs.existsSync(this.vaultConfigPath)) {
        const configContent = fs.readFileSync(this.vaultConfigPath, 'utf8');
        this.vaultMountedConfig = JSON.parse(configContent);
        logger.info('已加载Vault注入的配置');
      }
    } catch (error) {
      logger.warn('读取Vault注入配置失败', { error: error.message });
    }
  }
  
  /**
   * 使用Kubernetes身份验证
   */
  async _authenticateWithK8s() {
    try {
      // 读取K8s服务账号令牌
      if (!fs.existsSync(this.k8sServiceAccountPath)) {
        throw new Error('K8s服务账号令牌文件不存在');
      }
      
      const k8sToken = fs.readFileSync(this.k8sServiceAccountPath, 'utf8');
      
      // 向Vault发送K8s令牌获取Vault令牌
      const response = await axios.post(
        `${this.endpoint}/v1/auth/kubernetes/login`,
        {
          role: this.vaultK8sRole,
          jwt: k8sToken
        },
        {
          headers: {
            'Content-Type': 'application/json'
          },
          timeout: 5000
        }
      );
      
      if (response.status === 200 && response.data && response.data.auth) {
        this.vaultToken = response.data.auth.client_token;
        logger.info('Vault K8s认证成功');
      } else {
        throw new Error('Vault K8s认证响应无效');
      }
    } catch (error) {
      logger.error('Vault K8s认证失败', { error: error.message });
      throw error;
    }
  }
  
  /**
   * 刷新配置
   */
  async refreshConfig() {
    try {
      // 如果缓存有效，使用缓存
      const now = Date.now();
      if (this.configCache && (now - this.lastFetchTime < this.cacheTTL)) {
        return this.configCache;
      }
      
      // 优先使用Vault注入的配置
      if (this.vaultMountedConfig) {
        this.configCache = this.vaultMountedConfig;
        this.lastFetchTime = now;
        return this.configCache;
      }
      
      // 如果Vault启用且有令牌，则从Vault获取
      if (this.enabled && this.vaultToken) {
        const response = await axios.get(
          `${this.endpoint}/v1/${this.path}`,
          {
            headers: {
              'X-Vault-Token': this.vaultToken
            },
            timeout: 5000
          }
        );
        
        if (response.status === 200 && response.data && response.data.data && response.data.data.data) {
          this.configCache = response.data.data.data;
          this.lastFetchTime = now;
          logger.info('从Vault刷新配置成功');
        } else {
          throw new Error('从Vault获取配置响应无效');
        }
      } else {
        logger.warn('无法从Vault获取配置：Vault未启用或缺少令牌');
      }
      
      return this.configCache;
    } catch (error) {
      logger.error('从Vault刷新配置失败', { error: error.message });
      // 返回上次的缓存，如果有的话
      return this.configCache;
    }
  }
  
  /**
   * 获取配置
   */
  async getConfig() {
    // 优先使用缓存配置
    if (this.configCache) {
      return this.configCache;
    }
    
    // 否则刷新配置
    return await this.refreshConfig();
  }
  
  /**
   * 获取特定配置项
   * @param {string} key 配置键
   * @param {any} defaultValue 默认值
   */
  async getConfigValue(key, defaultValue = null) {
    const config = await this.getConfig();
    
    if (!config) {
      return defaultValue;
    }
    
    const parts = key.split('.');
    let value = config;
    
    for (const part of parts) {
      if (value === null || value === undefined || typeof value !== 'object') {
        return defaultValue;
      }
      
      value = value[part];
      
      if (value === undefined) {
        return defaultValue;
      }
    }
    
    return value !== null && value !== undefined ? value : defaultValue;
  }
}

// 导出单例
module.exports = new VaultConfig();