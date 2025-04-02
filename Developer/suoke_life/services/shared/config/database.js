/**
 * 数据库配置模块
 * 提供MongoDB数据库连接配置
 */
const mongoose = require('mongoose');
const logger = require('../utils/logger');

/**
 * 默认数据库配置选项
 */
const defaultOptions = {
  // 数据库连接URI(应从环境变量读取)
  uri: process.env.MONGODB_URI || 'mongodb://localhost:27017/suoke_life',
  
  // 连接选项
  options: {
    useNewUrlParser: true,
    useUnifiedTopology: true,
    autoIndex: true, // 在生产环境中可以设置为false以提高性能
    serverSelectionTimeoutMS: 5000, // 服务器选择超时
    socketTimeoutMS: 45000, // 套接字超时
    family: 4, // 强制IPv4
    maxPoolSize: 10, // 连接池大小
  },
  
  // 重试设置
  retry: {
    enabled: true,
    count: 5,
    delay: 5000, // 5秒
    factor: 1.5 // 每次重试增加50%延迟
  }
};

/**
 * 根据环境获取数据库配置
 * @param {string} env - 环境名称
 * @returns {Object} 数据库配置
 */
const getConfig = (env = process.env.NODE_ENV || 'development') => {
  // 生产环境配置
  if (env === 'production') {
    if (!process.env.MONGODB_URI) {
      console.warn('警告: 生产环境中未设置MONGODB_URI环境变量');
    }
    
    return {
      ...defaultOptions,
      // 生产环境特定配置覆盖
      options: {
        ...defaultOptions.options,
        autoIndex: false, // 生产环境禁用自动索引
        maxPoolSize: 50 // 更大的连接池
      }
    };
  }
  
  // 测试环境配置
  if (env === 'test') {
    return {
      ...defaultOptions,
      // 测试环境使用独立的测试数据库
      uri: process.env.MONGODB_URI_TEST || 'mongodb://localhost:27017/suoke_life_test',
      options: {
        ...defaultOptions.options,
        autoIndex: true // 测试环境启用自动索引
      }
    };
  }
  
  // 开发环境(默认)配置
  return {
    ...defaultOptions
  };
};

/**
 * 数据库配置
 */
const dbConfig = getConfig();

/**
 * 连接数据库
 * @returns {Promise<mongoose.Connection>} 数据库连接
 */
const connect = async () => {
  try {
    // 设置mongoose全局配置
    mongoose.set('strictQuery', true);
    
    // 连接数据库
    const connection = await mongoose.connect(dbConfig.uri, dbConfig.options);
    
    logger.info('数据库连接成功', { 
      host: connection.connection.host,
      name: connection.connection.name,
      port: connection.connection.port
    });
    
    // 监听连接事件
    mongoose.connection.on('error', (err) => {
      logger.error('数据库连接错误', { error: err.message });
    });
    
    mongoose.connection.on('disconnected', () => {
      logger.warn('数据库连接断开');
      
      // 如果启用了重试，则尝试重新连接
      if (dbConfig.retry.enabled) {
        retryConnect(1);
      }
    });
    
    mongoose.connection.on('reconnected', () => {
      logger.info('数据库重新连接成功');
    });
    
    // 捕获进程退出事件，关闭连接
    process.on('SIGINT', async () => {
      await mongoose.connection.close();
      logger.info('数据库连接已关闭（应用程序终止）');
      process.exit(0);
    });
    
    return connection.connection;
  } catch (error) {
    logger.error('数据库连接失败', { 
      error: error.message,
      uri: dbConfig.uri.replace(/\/\/([^:]+):([^@]+)@/, '//***:***@') // 隐藏凭据
    });
    
    // 如果启用了重试，则尝试重新连接
    if (dbConfig.retry.enabled) {
      retryConnect(1);
    } else {
      throw error;
    }
  }
};

/**
 * 重试连接数据库
 * @param {number} attempt - 当前尝试次数
 */
const retryConnect = (attempt) => {
  const maxAttempts = dbConfig.retry.count;
  const delay = dbConfig.retry.delay * Math.pow(dbConfig.retry.factor, attempt - 1);
  
  if (attempt > maxAttempts) {
    logger.error(`数据库重新连接失败，已达到最大重试次数(${maxAttempts})`);
    return;
  }
  
  logger.info(`尝试重新连接数据库 (${attempt}/${maxAttempts})，等待 ${delay}ms...`);
  
  setTimeout(async () => {
    try {
      await mongoose.connect(dbConfig.uri, dbConfig.options);
      logger.info('数据库重新连接成功');
    } catch (error) {
      logger.error(`数据库重新连接失败 (${attempt}/${maxAttempts})`, { error: error.message });
      retryConnect(attempt + 1);
    }
  }, delay);
};

/**
 * 关闭数据库连接
 * @returns {Promise<void>}
 */
const close = async () => {
  if (mongoose.connection.readyState !== 0) {
    await mongoose.connection.close();
    logger.info('数据库连接已关闭');
  }
};

module.exports = {
  config: dbConfig,
  connect,
  close,
  mongoose
}; 