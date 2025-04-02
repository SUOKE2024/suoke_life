import mongoose from 'mongoose';
import { logger } from '../../utils/logger';

/**
 * 连接MongoDB数据库
 */
export const connectToDatabase = async (): Promise<typeof mongoose> => {
  try {
    // 获取环境变量
    const uri = process.env.MONGODB_URI || 'mongodb://localhost:27017/xiaoke-service';
    const options: mongoose.ConnectOptions = {
      // MongoDB连接选项
    };

    if (process.env.MONGODB_USER && process.env.MONGODB_PASSWORD) {
      Object.assign(options, {
        user: process.env.MONGODB_USER,
        pass: process.env.MONGODB_PASSWORD,
      });
    }

    // 设置连接事件监听
    mongoose.connection.on('connected', () => {
      logger.info('MongoDB连接成功');
    });

    mongoose.connection.on('error', (err) => {
      logger.error('MongoDB连接错误:', err);
    });

    mongoose.connection.on('disconnected', () => {
      logger.warn('MongoDB连接断开');
    });

    // 连接到数据库
    await mongoose.connect(uri, options);
    return mongoose;
  } catch (error) {
    logger.error('MongoDB连接失败:', error);
    throw error;
  }
};

/**
 * 关闭数据库连接
 */
export const closeDatabase = async (): Promise<void> => {
  try {
    await mongoose.connection.close();
    logger.info('MongoDB连接已关闭');
  } catch (error) {
    logger.error('关闭MongoDB连接时出错:', error);
    throw error;
  }
};

export default {
  connect: connectToDatabase,
  close: closeDatabase,
}; 