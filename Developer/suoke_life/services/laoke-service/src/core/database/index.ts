import mongoose from 'mongoose';
import logger from '../utils/logger';

/**
 * 连接MongoDB数据库
 */
export const connectDatabase = async () => {
  try {
    // 设置选项
    const options = {
      autoIndex: true,
      serverSelectionTimeoutMS: 5000,
      socketTimeoutMS: 45000,
    };
    
    // 构建连接字符串
    const mongoUri = process.env.MONGODB_URI || 'mongodb://localhost:27017/laoke_service';
    
    // 连接数据库
    await mongoose.connect(mongoUri, options);
    
    // 连接成功
    logger.info('MongoDB数据库连接成功');
    
    // 监听错误事件
    mongoose.connection.on('error', (err) => {
      logger.error('MongoDB数据库连接错误:', err);
    });
    
    // 监听断开连接事件
    mongoose.connection.on('disconnected', () => {
      logger.warn('MongoDB数据库断开连接');
    });
    
    // 监听重新连接事件
    mongoose.connection.on('reconnected', () => {
      logger.info('MongoDB数据库重新连接成功');
    });
    
    return mongoose.connection;
  } catch (error) {
    logger.error('MongoDB数据库连接失败:', error);
    throw error;
  }
};

/**
 * 断开MongoDB数据库连接
 */
export const disconnectDatabase = async () => {
  try {
    if (mongoose.connection.readyState === 1) {
      await mongoose.connection.close();
      logger.info('MongoDB数据库连接已关闭');
    }
  } catch (error) {
    logger.error('关闭MongoDB数据库连接出错:', error);
    throw error;
  }
};

/**
 * 获取MongoDB连接
 */
export const getConnection = () => {
  return mongoose.connection;
};

/**
 * 获取连接状态
 */
export const getConnectionStatus = () => {
  const states = {
    0: 'disconnected',
    1: 'connected',
    2: 'connecting',
    3: 'disconnecting'
  };
  
  return {
    state: states[mongoose.connection.readyState] || 'unknown',
    readyState: mongoose.connection.readyState
  };
}; 