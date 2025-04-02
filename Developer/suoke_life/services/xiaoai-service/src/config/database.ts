import mongoose from 'mongoose';
import { logger } from '../index';

/**
 * 初始化数据库连接
 */
export const initDatabaseConnection = async (): Promise<void> => {
  const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/xiaoai-service';
  
  try {
    await mongoose.connect(MONGODB_URI);
    logger.info('MongoDB数据库连接成功');
    
    // 设置连接监听事件
    mongoose.connection.on('error', (err) => {
      logger.error('MongoDB连接错误:', err);
    });
    
    mongoose.connection.on('disconnected', () => {
      logger.warn('MongoDB连接断开，尝试重新连接...');
      setTimeout(() => {
        initDatabaseConnection();
      }, 5000);
    });
    
  } catch (error) {
    logger.error('MongoDB连接失败:', error);
    throw error;
  }
};

/**
 * 关闭数据库连接
 */
export const closeDatabaseConnection = async (): Promise<void> => {
  try {
    await mongoose.connection.close();
    logger.info('MongoDB连接已关闭');
  } catch (error) {
    logger.error('关闭MongoDB连接时出错:', error);
    throw error;
  }
};