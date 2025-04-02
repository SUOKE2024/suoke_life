/**
 * 负载均衡器工具
 * 
 * 为微服务提供负载均衡功能
 */
const logger = require('./logger');

/**
 * 负载均衡器类
 */
class LoadBalancer {
  /**
   * 创建负载均衡器实例
   * @param {string} serviceName 服务名称
   * @param {Array<string>} urls 服务URL列表
   * @param {Object} options 配置选项
   */
  constructor(serviceName, urls = [], options = {}) {
    this.serviceName = serviceName;
    this.urls = urls || [];
    this.strategy = options.strategy || 'round-robin';
    this.currentIndex = 0;
    this.totalRequests = 0;
    this.urlStats = {};
    this.healthStatus = new Map();
    this.weights = new Map();
    
    // 初始化URL统计和健康状态
    this.urls.forEach(url => {
      this.urlStats[url] = 0;
      this.healthStatus.set(url, true);
    });
    
    logger.info(`创建负载均衡器: ${serviceName}, 服务数: ${this.urls.length}, 策略: ${this.strategy}`);
  }
  
  /**
   * 设置负载均衡策略
   * @param {string} strategy 策略名称：'round-robin', 'random', 'weighted'
   */
  setStrategy(strategy) {
    this.strategy = strategy;
    logger.info(`${this.serviceName} 负载均衡器策略设置为: ${strategy}`);
  }
  
  /**
   * 设置URL权重
   * @param {Object} weights URL权重配置，如 {'http://service1:3000': 5}
   */
  setWeights(weights) {
    this.weights.clear();
    Object.entries(weights).forEach(([url, weight]) => {
      this.weights.set(url, weight);
    });
    
    logger.info(`${this.serviceName} 负载均衡器权重已更新`);
  }
  
  /**
   * 添加URL
   * @param {string} url 要添加的服务URL
   */
  addUrl(url) {
    if (!this.urls.includes(url)) {
      this.urls.push(url);
      this.urlStats[url] = 0;
      this.healthStatus.set(url, true);
      logger.info(`${this.serviceName} 负载均衡器添加URL: ${url}`);
    }
  }
  
  /**
   * 移除URL
   * @param {string} url 要移除的服务URL
   */
  removeUrl(url) {
    const index = this.urls.indexOf(url);
    if (index !== -1) {
      this.urls.splice(index, 1);
      delete this.urlStats[url];
      this.healthStatus.delete(url);
      logger.info(`${this.serviceName} 负载均衡器移除URL: ${url}`);
    }
  }
  
  /**
   * 获取下一个服务URL
   * @returns {string} 下一个服务URL
   */
  getNextUrl() {
    if (this.urls.length === 0) {
      throw new Error('没有可用的服务URL');
    }
    
    // 只使用健康的URL
    const healthyUrls = this.urls.filter(url => this.healthStatus.get(url));
    
    if (healthyUrls.length === 0) {
      logger.warn(`${this.serviceName} 没有健康的服务实例可用，尝试使用所有实例`);
      // 退化为使用所有URL
      healthyUrls.push(...this.urls);
    }
    
    let nextUrl;
    
    // 根据策略选择URL
    switch (this.strategy) {
      case 'random':
        nextUrl = this.getRandomUrl(healthyUrls);
        break;
        
      case 'weighted':
        nextUrl = this.getWeightedUrl(healthyUrls);
        break;
        
      case 'round-robin':
      default:
        nextUrl = this.getRoundRobinUrl(healthyUrls);
        break;
    }
    
    // 记录统计
    this.totalRequests++;
    this.urlStats[nextUrl] = (this.urlStats[nextUrl] || 0) + 1;
    
    return nextUrl;
  }
  
  /**
   * 轮询算法选择URL
   * @param {Array<string>} urls URL列表
   * @returns {string} 选择的URL
   */
  getRoundRobinUrl(urls) {
    if (this.currentIndex >= urls.length) {
      this.currentIndex = 0;
    }
    
    return urls[this.currentIndex++];
  }
  
  /**
   * 随机算法选择URL
   * @param {Array<string>} urls URL列表
   * @returns {string} 选择的URL
   */
  getRandomUrl(urls) {
    const randomIndex = Math.floor(Math.random() * urls.length);
    return urls[randomIndex];
  }
  
  /**
   * 加权算法选择URL
   * @param {Array<string>} urls URL列表
   * @returns {string} 选择的URL
   */
  getWeightedUrl(urls) {
    // 默认权重为1
    const defaultWeight = 1;
    
    // 计算总权重
    let totalWeight = 0;
    const weightedUrls = urls.map(url => {
      const weight = this.weights.get(url) || defaultWeight;
      totalWeight += weight;
      return { url, weight };
    });
    
    // 没有权重配置时，退化为随机选择
    if (totalWeight === 0) {
      return this.getRandomUrl(urls);
    }
    
    // 生成随机数，范围在0-totalWeight之间
    let random = Math.random() * totalWeight;
    
    // 选择URL
    for (const { url, weight } of weightedUrls) {
      random -= weight;
      if (random <= 0) {
        return url;
      }
    }
    
    // 兜底返回第一个URL
    return urls[0];
  }
  
  /**
   * 更新服务健康状态
   * @param {string} url 服务URL
   * @param {boolean} isHealthy 是否健康
   */
  updateHealth(url, isHealthy) {
    this.healthStatus.set(url, isHealthy);
    logger.debug(`${this.serviceName} URL ${url} 健康状态: ${isHealthy ? '健康' : '不健康'}`);
  }
  
  /**
   * 检查所有服务的健康状态
   * @param {Function} healthCheckFn 健康检查函数，接收URL返回Promise<boolean>
   * @returns {Promise<Object>} 健康检查结果
   */
  async checkHealth(healthCheckFn) {
    const results = {};
    
    for (const url of this.urls) {
      try {
        const isHealthy = await healthCheckFn(url);
        this.updateHealth(url, isHealthy);
        results[url] = isHealthy;
      } catch (error) {
        logger.error(`健康检查失败 ${url}: ${error.message}`);
        this.updateHealth(url, false);
        results[url] = false;
      }
    }
    
    return results;
  }
  
  /**
   * 获取总请求数
   * @returns {number} 总请求数
   */
  getTotalRequests() {
    return this.totalRequests;
  }
  
  /**
   * 获取URL请求统计
   * @returns {Object} URL请求统计
   */
  getUrlStats() {
    return { ...this.urlStats };
  }
  
  /**
   * 获取健康URL数量
   * @returns {number} 健康URL数量
   */
  getHealthyCount() {
    return this.urls.filter(url => this.healthStatus.get(url)).length;
  }
  
  /**
   * 重置统计信息
   */
  resetStats() {
    this.totalRequests = 0;
    for (const url of this.urls) {
      this.urlStats[url] = 0;
    }
  }
}

// 默认导出
module.exports = LoadBalancer;
// 同时导出类
module.exports.LoadBalancer = LoadBalancer;