import mongoose from 'mongoose';
import { Logger } from '../utils/logger';

/**
 * MongoDB连接配置
 */
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/suoke_touch_diagnosis';
const MONGODB_OPTIONS = {
  user: process.env.MONGODB_USER,
  pass: process.env.MONGODB_PASSWORD,
  authSource: process.env.MONGODB_AUTH_SOURCE || 'admin',
  useNewUrlParser: true,
  useUnifiedTopology: true,
};

/**
 * 连接到MongoDB数据库
 */
export const connectToDatabase = async (): Promise<void> => {
  try {
    if (mongoose.connection.readyState === 1) {
      Logger.info('MongoDB 已连接');
      return;
    }

    // MongoDB连接事件监听器
    mongoose.connection.on('connected', () => {
      Logger.info('MongoDB 数据库连接成功');
    });

    mongoose.connection.on('error', (error) => {
      Logger.error('MongoDB 连接错误', { error });
      process.exit(1);
    });

    mongoose.connection.on('disconnected', () => {
      Logger.warn('MongoDB 连接断开，尝试重新连接');
      setTimeout(connectToDatabase, 5000);
    });

    // 连接到MongoDB
    await mongoose.connect(MONGODB_URI, MONGODB_OPTIONS);
  } catch (error) {
    Logger.error('连接MongoDB数据库失败', { error });
    throw error;
  }
};

/**
 * 断开与MongoDB的连接
 */
export const disconnectFromDatabase = async (): Promise<void> => {
  try {
    await mongoose.disconnect();
    Logger.info('已断开与MongoDB的连接');
  } catch (error) {
    Logger.error('断开MongoDB连接失败', { error });
    throw error;
  }
};

/**
 * 获取数据库连接状态
 */
export const getDatabaseStatus = (): { connected: boolean; status: string } => {
  const states = ['未连接', '已连接', '正在连接', '正在断开连接'];
  return {
    connected: mongoose.connection.readyState === 1,
    status: states[mongoose.connection.readyState]
  };
}; 