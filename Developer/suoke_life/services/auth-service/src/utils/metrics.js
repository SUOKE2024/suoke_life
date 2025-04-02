/**
 * 指标收集工具
 * 用于监控认证服务性能和状态
 */
const client = require('prom-client');
const config = require('../config');
const logger = require('./logger');

class MetricsService {
  constructor() {
    // 读取指标配置
    this.config = config.metrics || {};
    this.enabled = this.config.enabled !== false;
    this.prefix = this.config.prefix || 'auth_';
    this.defaultLabels = this.config.defaultLabels || {};
    
    if (!this.enabled) {
      logger.info('指标收集功能已关闭');
      return;
    }
    
    // 设置默认标签
    client.register.setDefaultLabels(this.defaultLabels);
    
    // 创建指标收集间隔
    this.collectInterval = null;
    
    // 初始化指标
    this._initializeMetrics();
    
    // 设置收集间隔
    const collectIntervalMs = (this.config.interval || 15) * 1000;
    this.collectInterval = setInterval(() => {
      this._collectMetrics();
    }, collectIntervalMs);
    
    logger.info(`指标收集服务已初始化，前缀: ${this.prefix}, 间隔: ${collectIntervalMs}ms`);
  }
  
  /**
   * 初始化指标
   * @private
   */
  _initializeMetrics() {
    try {
      // HTTP请求计数器
      this.httpRequestsTotal = new client.Counter({
        name: `${this.prefix}http_requests_total`,
        help: 'HTTP请求总数',
        labelNames: ['method', 'path', 'status']
      });
      
      // 请求持续时间直方图
      this.requestDurationHistogram = new client.Histogram({
        name: `${this.prefix}request_duration_seconds`,
        help: '请求处理时间（秒）',
        labelNames: ['method', 'path', 'status'],
        buckets: this.config.histograms?.requestDuration?.buckets || 
                [0.01, 0.05, 0.1, 0.5, 1, 2.5, 5, 10]
      });
      
      // 认证计数器
      this.authSuccessCounter = new client.Counter({
        name: `${this.prefix}auth_success_total`,
        help: '成功认证次数',
        labelNames: ['method', 'provider']
      });
      
      this.authFailuresCounter = new client.Counter({
        name: `${this.prefix}auth_failures_total`,
        help: '认证失败次数',
        labelNames: ['method', 'reason', 'provider']
      });
      
      // 令牌生成计数器和直方图
      this.tokenGenerationCounter = new client.Counter({
        name: `${this.prefix}token_generation_total`,
        help: '令牌生成次数',
        labelNames: ['type']
      });
      
      this.tokenGenerationDurationHistogram = new client.Histogram({
        name: `${this.prefix}token_generation_duration_seconds`,
        help: '令牌生成时间（秒）',
        labelNames: ['type'],
        buckets: this.config.histograms?.tokenGenerationTime?.buckets || 
                [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5]
      });
      
      // 速率限制计数器
      this.rateLimitCounter = new client.Counter({
        name: `${this.prefix}rate_limit_total`,
        help: '速率限制触发次数',
        labelNames: ['path']
      });
      
      // 数据库操作计数器和直方图
      this.dbOperationsCounter = new client.Counter({
        name: `${this.prefix}db_operations_total`,
        help: '数据库操作次数',
        labelNames: ['operation', 'table', 'status']
      });
      
      this.dbOperationsDurationHistogram = new client.Histogram({
        name: `${this.prefix}db_operations_duration_seconds`,
        help: '数据库操作时间（秒）',
        labelNames: ['operation', 'table'],
        buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1]
      });
      
      // Redis操作计数器和直方图
      this.redisOperationsCounter = new client.Counter({
        name: `${this.prefix}redis_operations_total`,
        help: 'Redis操作次数',
        labelNames: ['operation', 'status']
      });
      
      this.redisOperationsDurationHistogram = new client.Histogram({
        name: `${this.prefix}redis_operations_duration_seconds`,
        help: 'Redis操作时间（秒）',
        labelNames: ['operation'],
        buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
      });
      
      // 活跃用户会话计量器
      this.activeSessionsGauge = new client.Gauge({
        name: `${this.prefix}active_sessions`,
        help: '当前活跃会话数'
      });
      
      // 系统资源计量器
      this.resourceUsageGauge = new client.Gauge({
        name: `${this.prefix}system_resource_usage`,
        help: '系统资源使用情况',
        labelNames: ['resource']
      });
      
      // 跨区域同步指标
      this.crossRegionSyncCounter = new client.Counter({
        name: `${this.prefix}cross_region_sync_total`,
        help: '跨区域同步操作次数',
        labelNames: ['operation', 'region', 'status']
      });
      
      this.crossRegionSyncDurationHistogram = new client.Histogram({
        name: `${this.prefix}cross_region_sync_duration_seconds`,
        help: '跨区域同步时间（秒）',
        labelNames: ['operation', 'region'],
        buckets: [0.1, 0.5, 1, 2, 5, 10, 30]
      });
      
      this.crossRegionSyncLatencyGauge = new client.Gauge({
        name: `${this.prefix}cross_region_sync_latency_seconds`,
        help: '跨区域同步延迟（秒）',
        labelNames: ['region']
      });
      
    } catch (error) {
      logger.error(`指标初始化失败: ${error.message}`, { error });
    }
  }
  
  /**
   * 收集指标
   * @private
   */
  _collectMetrics() {
    try {
      // 收集系统资源使用情况
      const memoryUsage = process.memoryUsage();
      this.resourceUsageGauge.set({ resource: 'memory_rss' }, memoryUsage.rss / 1024 / 1024);
      this.resourceUsageGauge.set({ resource: 'memory_heap_total' }, memoryUsage.heapTotal / 1024 / 1024);
      this.resourceUsageGauge.set({ resource: 'memory_heap_used' }, memoryUsage.heapUsed / 1024 / 1024);
      this.resourceUsageGauge.set({ resource: 'memory_external' }, memoryUsage.external / 1024 / 1024);
      
      // 收集进程信息
      this.resourceUsageGauge.set({ resource: 'uptime' }, process.uptime());
      
      // 其他动态指标将通过中间件和服务调用进行收集
    } catch (error) {
      logger.error(`指标收集失败: ${error.message}`, { error });
    }
  }
  
  /**
   * 获取指标Registry
   * @returns {Object} Prometheus客户端注册表
   */
  getRegistry() {
    return client.register;
  }
  
  /**
   * 记录HTTP请求
   * @param {string} method - HTTP方法
   * @param {string} path - 请求路径
   * @param {number} status - 响应状态码
   * @param {number} duration - 请求处理时间（毫秒）
   */
  recordHttpRequest(method, path, status, duration) {
    if (!this.enabled) return;
    
    try {
      // 简化路径，移除ID等动态部分
      const simplifiedPath = this._simplifyPath(path);
      
      // 记录请求计数
      this.httpRequestsTotal.inc({ 
        method, 
        path: simplifiedPath, 
        status 
      });
      
      // 记录请求时间
      this.requestDurationHistogram.observe(
        { method, path: simplifiedPath, status },
        duration / 1000 // 转换为秒
      );
    } catch (error) {
      logger.debug(`记录HTTP请求指标失败: ${error.message}`);
    }
  }
  
  /**
   * 记录认证成功
   * @param {string} method - 认证方法（如password, oauth, phone）
   * @param {string} provider - 提供商（如wechat, alipay）
   */
  recordAuthSuccess(method, provider = 'internal') {
    if (!this.enabled) return;
    
    try {
      this.authSuccessCounter.inc({ method, provider });
    } catch (error) {
      logger.debug(`记录认证成功指标失败: ${error.message}`);
    }
  }
  
  /**
   * 记录认证失败
   * @param {string} method - 认证方法
   * @param {string} reason - 失败原因
   * @param {string} provider - 提供商
   */
  recordAuthFailure(method, reason, provider = 'internal') {
    if (!this.enabled) return;
    
    try {
      this.authFailuresCounter.inc({ method, reason, provider });
    } catch (error) {
      logger.debug(`记录认证失败指标失败: ${error.message}`);
    }
  }
  
  /**
   * 记录令牌生成
   * @param {string} type - 令牌类型（如access, refresh）
   * @param {number} duration - 生成时间（毫秒）
   */
  recordTokenGeneration(type, duration) {
    if (!this.enabled) return;
    
    try {
      this.tokenGenerationCounter.inc({ type });
      this.tokenGenerationDurationHistogram.observe({ type }, duration / 1000);
    } catch (error) {
      logger.debug(`记录令牌生成指标失败: ${error.message}`);
    }
  }
  
  /**
   * 记录速率限制
   * @param {string} path - 请求路径
   */
  recordRateLimit(path) {
    if (!this.enabled) return;
    
    try {
      const simplifiedPath = this._simplifyPath(path);
      this.rateLimitCounter.inc({ path: simplifiedPath });
    } catch (error) {
      logger.debug(`记录速率限制指标失败: ${error.message}`);
    }
  }
  
  /**
   * 记录数据库操作
   * @param {string} operation - 操作类型（如select, insert）
   * @param {string} table - 表名
   * @param {string} status - 状态（success, error）
   * @param {number} duration - 操作时间（毫秒）
   */
  recordDbOperation(operation, table, status, duration) {
    if (!this.enabled) return;
    
    try {
      this.dbOperationsCounter.inc({ operation, table, status });
      this.dbOperationsDurationHistogram.observe({ operation, table }, duration / 1000);
    } catch (error) {
      logger.debug(`记录数据库操作指标失败: ${error.message}`);
    }
  }
  
  /**
   * 记录Redis操作
   * @param {string} operation - 操作类型
   * @param {string} status - 状态
   * @param {number} duration - 操作时间（毫秒）
   */
  recordRedisOperation(operation, status, duration) {
    if (!this.enabled) return;
    
    try {
      this.redisOperationsCounter.inc({ operation, status });
      this.redisOperationsDurationHistogram.observe({ operation }, duration / 1000);
    } catch (error) {
      logger.debug(`记录Redis操作指标失败: ${error.message}`);
    }
  }
  
  /**
   * 更新活跃会话数
   * @param {number} count - 活跃会话数
   */
  updateActiveSessions(count) {
    if (!this.enabled) return;
    
    try {
      this.activeSessionsGauge.set(count);
    } catch (error) {
      logger.debug(`更新活跃会话指标失败: ${error.message}`);
    }
  }
  
  /**
   * 记录跨区域同步操作
   * @param {string} operation - 操作类型
   * @param {string} region - 区域
   * @param {string} status - 状态
   * @param {number} duration - 操作时间（毫秒）
   */
  recordCrossRegionSync(operation, region, status, duration) {
    if (!this.enabled) return;
    
    try {
      this.crossRegionSyncCounter.inc({ operation, region, status });
      this.crossRegionSyncDurationHistogram.observe({ operation, region }, duration / 1000);
    } catch (error) {
      logger.debug(`记录跨区域同步指标失败: ${error.message}`);
    }
  }
  
  /**
   * 更新跨区域同步延迟
   * @param {string} region - 区域
   * @param {number} latency - 延迟（秒）
   */
  updateCrossRegionLatency(region, latency) {
    if (!this.enabled) return;
    
    try {
      this.crossRegionSyncLatencyGauge.set({ region }, latency);
    } catch (error) {
      logger.debug(`更新跨区域同步延迟指标失败: ${error.message}`);
    }
  }
  
  /**
   * 简化路径
   * @private
   * @param {string} path - 原始路径
   * @returns {string} 简化后的路径
   */
  _simplifyPath(path) {
    try {
      // 移除路径中的ID和其他动态参数
      return path
        .replace(/\/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi, '/:id')
        .replace(/\/[0-9a-f]{24}/gi, '/:id')
        .replace(/\/\d+/g, '/:id');
    } catch (error) {
      return path;
    }
  }
  
  /**
   * 关闭指标收集服务
   */
  close() {
    if (this.collectInterval) {
      clearInterval(this.collectInterval);
      this.collectInterval = null;
    }
    
    logger.info('指标收集服务已关闭');
  }
}

module.exports = new MetricsService(); 