/**
 * 数据库连接工具
 */
const mongoose = require('mongoose');
const logger = require('./logger');

/**
 * 连接数据库
 * @returns {Promise} 连接Promise
 */
const connectDatabase = async () => {
  try {
    const dbUri = process.env.DB_URI || 'mongodb://localhost:27017/cornmaze';
    
    // 设置连接选项
    const options = {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      autoIndex: process.env.NODE_ENV !== 'production',
      serverSelectionTimeoutMS: 5000
    };

    // 连接数据库
    await mongoose.connect(dbUri, options);
    
    logger.info('数据库连接成功');
    
    // 监听连接事件
    mongoose.connection.on('error', (err) => {
      logger.error('数据库连接错误:', err);
    });
    
    mongoose.connection.on('disconnected', () => {
      logger.warn('数据库连接断开');
    });
    
    // 进程终止时关闭连接
    process.on('SIGINT', async () => {
      await mongoose.connection.close();
      logger.info('数据库连接已关闭');
      process.exit(0);
    });
    
    return mongoose.connection;
  } catch (error) {
    logger.error('数据库连接失败:', error);
    throw error;
  }
};

module.exports = {
  connectDatabase,
  getConnection: () => mongoose.connection
};
