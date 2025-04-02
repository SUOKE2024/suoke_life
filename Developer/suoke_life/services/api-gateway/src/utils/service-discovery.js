/**
 * 服务发现工具
 * 支持自动发现和注册服务
 */
const axios = require('axios');
const logger = require('./logger');
const config = require('../config');

/**
 * 服务发现辅助类
 * 支持服务自动发现和注册
 */
class ServiceDiscovery {
  constructor() {
    this.servicesMap = new Map();
    this.isInitialized = false;
    this.updateInterval = config.server.healthCheck.interval || 30000;
    this.discoveryEndpoint = process.env.SERVICE_DISCOVERY_ENDPOINT || 'http://localhost:8080/discovery';
    this.vaultEnabled = process.env.VAULT_ENABLED === 'true';
    this.vaultEndpoint = process.env.VAULT_ENDPOINT || 'http://vault:8200';
    this.vaultToken = process.env.VAULT_TOKEN;
    this.vaultPath = process.env.VAULT_PATH || 'secret/data/api-gateway';
  }

  /**
   * 初始化服务发现
   */
  async initialize() {
    if (this.isInitialized) return;
    
    try {
      // 从Vault加载动态配置
      if (this.vaultEnabled && this.vaultToken) {
        await this._loadConfigFromVault();
      }
      
      // 从配置加载初始服务
      this._loadServicesFromConfig();
      
      // 从服务发现中心获取服务
      if (config.serviceDiscovery && config.serviceDiscovery.enabled) {
        await this._discoveryFromServer();
        
        // 设置定期发现服务
        setInterval(() => {
          this._discoveryFromServer().catch(err => {
            logger.error('服务发现失败', { error: err.message });
          });
        }, this.updateInterval);
      }
      
      this.isInitialized = true;
      logger.info('服务发现初始化完成');
    } catch (error) {
      logger.error('服务发现初始化失败', { error: error.message });
      throw error;
    }
  }

  /**
   * 从Vault加载动态配置
   */
  async _loadConfigFromVault() {
    try {
      logger.info('从Vault加载动态配置', { path: this.vaultPath });
      
      const response = await axios.get(`${this.vaultEndpoint}/v1/${this.vaultPath}`, {
        headers: {
          'X-Vault-Token': this.vaultToken
        },
        timeout: 5000
      });
      
      if (response.status === 200 && response.data && response.data.data && response.data.data.data) {
        const vaultConfig = response.data.data.data;
        
        // 更新服务配置
        if (vaultConfig.services) {
          Object.entries(vaultConfig.services).forEach(([serviceName, serviceConfig]) => {
            if (config.services[serviceName]) {
              // 合并配置
              config.services[serviceName] = {
                ...config.services[serviceName],
                ...serviceConfig
              };
              logger.debug(`从Vault更新服务配置: ${serviceName}`);
            }
          });
        }
        
        // 特殊处理代理协调服务配置
        if (vaultConfig.agentCoordinatorService) {
          const agentConfig = vaultConfig.agentCoordinatorService;
          if (!config.services.agentCoordinatorService) {
            config.services.agentCoordinatorService = {
              name: 'agent-coordinator-service',
              prefix: '/api/v1/agents/coordinator',
              healthCheck: '/health',
              instances: []
            };
          }
          
          if (agentConfig.instances && Array.isArray(agentConfig.instances)) {
            config.services.agentCoordinatorService.instances = agentConfig.instances;
          }
          
          if (agentConfig.prefix) {
            config.services.agentCoordinatorService.prefix = agentConfig.prefix;
          }
        }
        
        logger.info('Vault动态配置加载完成');
      }
    } catch (error) {
      logger.error('从Vault加载配置失败', { error: error.message });
    }
  }

  /**
   * 从配置加载服务
   */
  _loadServicesFromConfig() {
    try {
      // 从配置文件加载服务
      Object.entries(config.services).forEach(([key, service]) => {
        const serviceName = service.name;
        this.servicesMap.set(serviceName, {
          name: serviceName,
          instances: service.instances,
          loadBalanceStrategy: service.loadBalanceStrategy
        });
      });

      logger.info('从配置加载服务完成', { count: this.servicesMap.size });
    } catch (error) {
      logger.error('从配置加载服务失败', { error: error.message });
    }
  }

  /**
   * 从服务发现中心发现服务
   */
  async _discoveryFromServer() {
    try {
      const response = await axios.get(this.discoveryEndpoint, {
        timeout: 5000,
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'SuokeApiGateway/1.0'
        }
      });

      if (response.status === 200 && response.data && response.data.services) {
        // 更新服务列表
        const discoveredServices = response.data.services;
        
        Object.entries(discoveredServices).forEach(([serviceName, serviceDetails]) => {
          this.servicesMap.set(serviceName, {
            name: serviceName,
            instances: serviceDetails.instances || [],
            loadBalanceStrategy: serviceDetails.loadBalanceStrategy || 'round-robin'
          });
        });
        
        logger.info('服务发现更新完成', { count: this.servicesMap.size });
      }
    } catch (error) {
      logger.error('从服务中心发现服务失败', { error: error.message });
    }
  }

  /**
   * 获取所有服务
   * @returns {Map} 服务映射表
   */
  getAllServices() {
    return this.servicesMap;
  }

  /**
   * 获取特定服务
   * @param {string} serviceName 服务名称
   * @returns {Object|null} 服务信息
   */
  getService(serviceName) {
    return this.servicesMap.get(serviceName) || null;
  }

  /**
   * 注册服务
   * @param {string} serviceName 服务名称
   * @param {string} serviceUrl 服务URL
   * @param {string} [loadBalanceStrategy='round-robin'] 负载均衡策略
   */
  registerService(serviceName, serviceUrl, loadBalanceStrategy = 'round-robin') {
    try {
      const existingService = this.servicesMap.get(serviceName);
      
      if (existingService) {
        // 更新现有服务
        if (!existingService.instances.includes(serviceUrl)) {
          existingService.instances.push(serviceUrl);
        }
      } else {
        // 添加新服务
        this.servicesMap.set(serviceName, {
          name: serviceName,
          instances: [serviceUrl],
          loadBalanceStrategy
        });
      }
      
      logger.info(`服务注册成功: ${serviceName} at ${serviceUrl}`);
    } catch (error) {
      logger.error(`服务注册失败: ${serviceName}`, { error: error.message });
    }
  }

  /**
   * 注销服务
   * @param {string} serviceName 服务名称
   * @param {string} serviceUrl 服务URL
   */
  deregisterService(serviceName, serviceUrl) {
    try {
      const existingService = this.servicesMap.get(serviceName);
      
      if (existingService) {
        // 从实例列表中移除URL
        existingService.instances = existingService.instances.filter(url => url !== serviceUrl);
        
        // 如果没有实例，移除整个服务
        if (existingService.instances.length === 0) {
          this.servicesMap.delete(serviceName);
        }
        
        logger.info(`服务注销成功: ${serviceName} at ${serviceUrl}`);
      }
    } catch (error) {
      logger.error(`服务注销失败: ${serviceName}`, { error: error.message });
    }
  }
}

// 导出单例
module.exports = new ServiceDiscovery();