/**
 * 知识服务注册表
 * 管理所有与知识相关的服务
 */
const logger = require('./logger');

/**
 * 知识服务类型枚举
 * @enum {string}
 */
const KnowledgeServiceType = {
  KNOWLEDGE_BASE: 'knowledge-base',
  KNOWLEDGE_GRAPH: 'knowledge-graph',
  RAG: 'rag',
  PRECISION_MEDICINE: 'precision-medicine',
  MULTIMODAL_HEALTH: 'multimodal-health',
  ENVIRONMENTAL_HEALTH: 'environmental-health',
  MENTAL_HEALTH: 'mental-health'
};

/**
 * 服务能力描述接口
 * @typedef {Object} ServiceCapability
 * @property {string} name 能力名称
 * @property {string} description 能力描述
 * @property {string[]} domains 支持的领域
 * @property {Object} parameters 参数描述
 */

/**
 * 知识服务注册表类
 * 管理所有与知识相关的服务和能力
 */
class KnowledgeServicesRegistry {
  constructor() {
    /**
     * 服务映射表
     * @type {Map<string, Object>}
     */
    this.services = new Map();
    
    /**
     * 服务能力映射表
     * @type {Map<string, ServiceCapability[]>}
     */
    this.capabilities = new Map();
    
    /**
     * 领域到服务的映射
     * @type {Map<string, string[]>}
     */
    this.domainServiceMap = new Map();
  }
  
  /**
   * 注册知识服务
   * @param {string} serviceId 服务ID
   * @param {string} serviceType 服务类型
   * @param {string} serviceUrl 服务URL
   * @param {string[]} supportedDomains 支持的知识领域
   * @param {ServiceCapability[]} capabilities 服务能力
   */
  registerService(serviceId, serviceType, serviceUrl, supportedDomains = [], capabilities = []) {
    try {
      // 注册服务
      this.services.set(serviceId, {
        id: serviceId,
        type: serviceType,
        url: serviceUrl,
        supportedDomains,
        isActive: true,
        lastCheck: Date.now()
      });
      
      // 注册服务能力
      this.capabilities.set(serviceId, capabilities);
      
      // 更新领域到服务的映射
      supportedDomains.forEach(domain => {
        if (!this.domainServiceMap.has(domain)) {
          this.domainServiceMap.set(domain, []);
        }
        
        const services = this.domainServiceMap.get(domain);
        if (!services.includes(serviceId)) {
          services.push(serviceId);
        }
      });
      
      logger.info(`知识服务注册成功: ${serviceId} (${serviceType})`, {
        url: serviceUrl,
        domains: supportedDomains.join(', '),
        capabilities: capabilities.length
      });
      
      return true;
    } catch (error) {
      logger.error(`知识服务注册失败: ${serviceId}`, { error: error.message });
      return false;
    }
  }
  
  /**
   * 注销知识服务
   * @param {string} serviceId 服务ID
   */
  deregisterService(serviceId) {
    try {
      // 检查服务是否存在
      if (!this.services.has(serviceId)) {
        logger.warn(`尝试注销不存在的服务: ${serviceId}`);
        return false;
      }
      
      const service = this.services.get(serviceId);
      
      // 从领域映射中移除
      service.supportedDomains.forEach(domain => {
        if (this.domainServiceMap.has(domain)) {
          const services = this.domainServiceMap.get(domain);
          const index = services.indexOf(serviceId);
          
          if (index >= 0) {
            services.splice(index, 1);
          }
          
          // 如果领域没有服务，移除该领域
          if (services.length === 0) {
            this.domainServiceMap.delete(domain);
          }
        }
      });
      
      // 移除服务能力
      this.capabilities.delete(serviceId);
      
      // 移除服务
      this.services.delete(serviceId);
      
      logger.info(`知识服务注销成功: ${serviceId}`);
      
      return true;
    } catch (error) {
      logger.error(`知识服务注销失败: ${serviceId}`, { error: error.message });
      return false;
    }
  }
  
  /**
   * 根据领域获取服务列表
   * @param {string} domain 知识领域
   * @returns {Array} 服务列表
   */
  getServicesByDomain(domain) {
    const serviceIds = this.domainServiceMap.get(domain) || [];
    
    return serviceIds
      .map(id => this.services.get(id))
      .filter(service => service && service.isActive);
  }
  
  /**
   * 根据服务类型获取服务列表
   * @param {string} serviceType 服务类型
   * @returns {Array} 服务列表
   */
  getServicesByType(serviceType) {
    const result = [];
    
    this.services.forEach(service => {
      if (service.type === serviceType && service.isActive) {
        result.push(service);
      }
    });
    
    return result;
  }
  
  /**
   * 获取服务能力
   * @param {string} serviceId 服务ID
   * @returns {ServiceCapability[]} 服务能力列表
   */
  getServiceCapabilities(serviceId) {
    return this.capabilities.get(serviceId) || [];
  }
  
  /**
   * 检查服务健康状态
   * @param {string} serviceId 服务ID
   * @param {boolean} isHealthy 是否健康
   */
  updateServiceHealth(serviceId, isHealthy) {
    if (this.services.has(serviceId)) {
      const service = this.services.get(serviceId);
      service.isActive = isHealthy;
      service.lastCheck = Date.now();
      
      logger.debug(`更新服务健康状态: ${serviceId} = ${isHealthy ? '健康' : '不健康'}`);
    }
  }
  
  /**
   * 获取所有服务状态
   * @returns {Object} 服务状态概览
   */
  getServicesStatus() {
    const result = {
      total: this.services.size,
      active: 0,
      byType: {},
      byDomain: {}
    };
    
    // 初始化类型计数
    Object.values(KnowledgeServiceType).forEach(type => {
      result.byType[type] = 0;
    });
    
    // 统计服务
    this.services.forEach(service => {
      if (service.isActive) {
        result.active++;
      }
      
      // 按类型统计
      if (!result.byType[service.type]) {
        result.byType[service.type] = 0;
      }
      
      result.byType[service.type]++;
      
      // 按领域统计
      service.supportedDomains.forEach(domain => {
        if (!result.byDomain[domain]) {
          result.byDomain[domain] = 0;
        }
        
        result.byDomain[domain]++;
      });
    });
    
    return result;
  }
}

// 导出单例
module.exports = new KnowledgeServicesRegistry();
module.exports.KnowledgeServiceType = KnowledgeServiceType;