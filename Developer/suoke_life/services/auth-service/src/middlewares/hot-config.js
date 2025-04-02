/**
 * 配置热加载中间件
 * 支持动态配置刷新
 */
const fs = require('fs');
const path = require('path');
const logger = require('../utils/logger');
const config = require('../config');

class HotConfigManager {
  constructor() {
    this.configPaths = [];
    this.watchInterval = null;
    this.watchTimeoutMs = 30000; // 默认30秒
    this.configCache = new Map();
    this.subscribers = new Map();
    this.initialized = false;
    
    // 读取配置
    this.hotConfig = config.configReload || {};
    this.enabled = this.hotConfig.enabled !== false;
    
    if (this.enabled) {
      // 设置监视目录
      const configPaths = this.hotConfig.configPaths || ['/app/dynamic-config'];
      this.configPaths = Array.isArray(configPaths) ? configPaths : [configPaths];
      
      // 设置监视间隔
      this.watchTimeoutMs = (this.hotConfig.watchInterval || 30) * 1000;
      
      // 初始化
      this._init();
    } else {
      logger.info('配置热加载功能已关闭');
    }
  }
  
  /**
   * 初始化配置热加载
   * @private
   */
  _init() {
    try {
      // 加载所有配置文件
      this._loadAllConfigFiles();
      
      // 设置监视间隔
      this.watchInterval = setInterval(() => {
        this._checkConfigChanges();
      }, this.watchTimeoutMs);
      
      // 设置SIGHUP信号处理
      process.on('SIGHUP', () => {
        logger.info('收到SIGHUP信号，重新加载配置');
        this._loadAllConfigFiles(true);
      });
      
      this.initialized = true;
      logger.info(`配置热加载已初始化，监视目录: ${this.configPaths.join(', ')}, 检查间隔: ${this.watchTimeoutMs}ms`);
    } catch (error) {
      logger.error(`配置热加载初始化失败: ${error.message}`, { error });
    }
  }
  
  /**
   * 加载所有配置文件
   * @private
   * @param {boolean} notify - 是否通知订阅者
   */
  _loadAllConfigFiles(notify = false) {
    try {
      // 加载所有目录中的配置文件
      for (const configPath of this.configPaths) {
        if (!fs.existsSync(configPath)) {
          logger.warn(`配置目录不存在: ${configPath}`);
          continue;
        }
        
        const files = fs.readdirSync(configPath);
        
        for (const file of files) {
          if (file.endsWith('.json') || file.endsWith('.js')) {
            const filePath = path.join(configPath, file);
            this._loadConfigFile(filePath, notify);
          }
        }
      }
    } catch (error) {
      logger.error(`加载配置文件失败: ${error.message}`, { error });
    }
  }
  
  /**
   * 加载单个配置文件
   * @private
   * @param {string} filePath - 配置文件路径
   * @param {boolean} notify - 是否通知订阅者
   */
  _loadConfigFile(filePath, notify = false) {
    try {
      // 清除Node.js模块缓存
      if (filePath.endsWith('.js')) {
        delete require.cache[require.resolve(filePath)];
      }
      
      // 读取文件内容
      const content = fs.readFileSync(filePath, 'utf8');
      
      // 解析配置
      let configData;
      if (filePath.endsWith('.json')) {
        configData = JSON.parse(content);
      } else if (filePath.endsWith('.js')) {
        configData = require(filePath);
      }
      
      // 获取配置名（文件名去除扩展名）
      const configName = path.basename(filePath).replace(/\.(json|js)$/, '');
      
      // 检查配置是否变更
      const previousConfig = this.configCache.get(configName);
      const hasChanged = !previousConfig || 
        JSON.stringify(previousConfig) !== JSON.stringify(configData);
      
      // 更新缓存
      this.configCache.set(configName, configData);
      
      // 如果配置已变更且需要通知，则通知订阅者
      if (notify && hasChanged) {
        this._notifySubscribers(configName, configData, previousConfig);
      }
      
      logger.debug(`已加载配置文件: ${filePath}, 变更: ${hasChanged}`);
    } catch (error) {
      logger.error(`加载配置文件失败: ${filePath} - ${error.message}`, { error });
    }
  }
  
  /**
   * 检查配置变更
   * @private
   */
  _checkConfigChanges() {
    try {
      // 检查所有目录中的配置文件
      for (const configPath of this.configPaths) {
        if (!fs.existsSync(configPath)) {
          continue;
        }
        
        const files = fs.readdirSync(configPath);
        
        for (const file of files) {
          if (file.endsWith('.json') || file.endsWith('.js')) {
            const filePath = path.join(configPath, file);
            
            // 获取文件状态
            const stats = fs.statSync(filePath);
            const fileKey = `${filePath}:${stats.mtime.getTime()}`;
            
            // 检查文件是否已变更
            if (this.configCache.get(`${filePath}:mtime`) !== fileKey) {
              // 更新修改时间缓存
              this.configCache.set(`${filePath}:mtime`, fileKey);
              
              // 加载配置并通知
              this._loadConfigFile(filePath, true);
            }
          }
        }
      }
    } catch (error) {
      logger.error(`检查配置变更失败: ${error.message}`, { error });
    }
  }
  
  /**
   * 通知订阅者
   * @private
   * @param {string} configName - 配置名称
   * @param {Object} newConfig - 新配置
   * @param {Object} oldConfig - 旧配置
   */
  _notifySubscribers(configName, newConfig, oldConfig) {
    try {
      // 通知指定配置的订阅者
      const subscribers = this.subscribers.get(configName) || [];
      for (const subscriber of subscribers) {
        try {
          subscriber(newConfig, oldConfig);
        } catch (error) {
          logger.error(`配置订阅者处理失败: ${error.message}`, { error });
        }
      }
      
      // 通知全局订阅者
      const globalSubscribers = this.subscribers.get('*') || [];
      for (const subscriber of globalSubscribers) {
        try {
          subscriber({ [configName]: newConfig }, { [configName]: oldConfig });
        } catch (error) {
          logger.error(`全局配置订阅者处理失败: ${error.message}`, { error });
        }
      }
      
      logger.info(`配置已更新: ${configName}, 通知了 ${subscribers.length} 个订阅者和 ${globalSubscribers.length} 个全局订阅者`);
    } catch (error) {
      logger.error(`通知配置订阅者失败: ${error.message}`, { error });
    }
  }
  
  /**
   * 获取配置
   * @param {string} configName - 配置名称
   * @returns {Object} 配置对象
   */
  getConfig(configName) {
    return this.configCache.get(configName);
  }
  
  /**
   * 订阅配置变更
   * @param {string} configName - 配置名称，使用 '*' 订阅所有配置
   * @param {Function} callback - 回调函数
   * @returns {Function} 取消订阅函数
   */
  subscribe(configName, callback) {
    if (!this.enabled) {
      return () => {};
    }
    
    if (!this.subscribers.has(configName)) {
      this.subscribers.set(configName, []);
    }
    
    const subscribers = this.subscribers.get(configName);
    subscribers.push(callback);
    
    // 立即触发回调
    const currentConfig = this.configCache.get(configName);
    if (currentConfig) {
      try {
        callback(currentConfig, null);
      } catch (error) {
        logger.error(`配置订阅者初始回调失败: ${error.message}`, { error });
      }
    }
    
    // 返回取消订阅函数
    return () => {
      const index = subscribers.indexOf(callback);
      if (index >= 0) {
        subscribers.splice(index, 1);
      }
    };
  }
  
  /**
   * 关闭配置热加载
   */
  close() {
    if (this.watchInterval) {
      clearInterval(this.watchInterval);
      this.watchInterval = null;
    }
    
    this.subscribers.clear();
    this.configCache.clear();
    this.initialized = false;
    
    logger.info('配置热加载已关闭');
  }
}

// 单例模式
const hotConfigManager = new HotConfigManager();

/**
 * 创建配置刷新端点中间件
 * @returns {Function} Express中间件函数
 */
function createConfigReloadEndpoint() {
  return async (req, res) => {
    try {
      // 重新加载所有配置
      hotConfigManager._loadAllConfigFiles(true);
      
      // 返回结果
      res.status(200).json({
        success: true,
        message: '配置已刷新',
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      logger.error(`配置刷新失败: ${error.message}`, { error });
      
      res.status(500).json({
        success: false,
        message: `配置刷新失败: ${error.message}`
      });
    }
  };
}

module.exports = {
  hotConfigManager,
  createConfigReloadEndpoint
}; 