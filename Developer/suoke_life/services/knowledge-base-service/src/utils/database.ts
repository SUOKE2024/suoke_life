/**
 * 数据库连接工具
 */

import mongoose from 'mongoose';
import logger from './logger';

/**
 * 连接到MongoDB数据库
 */
export const connectToDatabase = async (): Promise<void> => {
  const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/knowledge_base';
  
  try {
    await mongoose.connect(MONGODB_URI, {
      // 选项配置会根据mongoose版本自动处理
    });
    
    logger.info('成功连接到MongoDB数据库');
    
    // 监听连接事件
    mongoose.connection.on('error', (err) => {
      logger.error('MongoDB连接错误', { error: err });
    });
    
    mongoose.connection.on('disconnected', () => {
      logger.warn('MongoDB连接断开，尝试重新连接');
      setTimeout(connectToDatabase, 5000);
    });
    
    process.on('SIGINT', async () => {
      await mongoose.connection.close();
      logger.info('MongoDB连接已关闭');
      process.exit(0);
    });
    
  } catch (error) {
    logger.error('MongoDB连接失败', { error });
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
    logger.error('关闭MongoDB连接失败', { error });
    throw error;
  }
};