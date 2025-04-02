import mongoose from 'mongoose';
import { Logger } from '../utils/logger';

// 创建日志实例
const logger = new Logger('Database');

/**
 * 数据库配置接口
 */
interface DatabaseConfig {
  /**
   * MongoDB URI
   */
  uri: string;
  
  /**
   * 数据库选项
   */
  options?: mongoose.ConnectOptions;
}

/**
 * 获取数据库配置
 * @returns 数据库配置对象
 */
export function getDatabaseConfig(): DatabaseConfig {
  // 从环境变量获取数据库配置
  const host = process.env.DB_HOST || 'localhost';
  const port = process.env.DB_PORT || '27017';
  const name = process.env.DB_NAME || 'inquiry_diagnosis';
  const user = process.env.DB_USER;
  const password = process.env.DB_PASSWORD;
  
  let uri: string;
  
  // 构建URI字符串，包含或不包含认证信息
  if (user && password) {
    uri = `mongodb://${user}:${password}@${host}:${port}/${name}`;
  } else {
    uri = `mongodb://${host}:${port}/${name}`;
  }
  
  // 数据库连接选项
  const options: mongoose.ConnectOptions = {
    // 在mongoose 6.x中，这些选项默认为true，不再需要显式设置
    // useNewUrlParser: true,
    // useUnifiedTopology: true,
    // useCreateIndex: true,
    // useFindAndModify: false,
    serverSelectionTimeoutMS: 5000, // 服务器选择超时
    socketTimeoutMS: 45000, // 套接字超时
  };
  
  return { uri, options };
}

/**
 * 连接数据库
 */
export async function connectDatabase(): Promise<void> {
  const config = getDatabaseConfig();
  
  try {
    logger.info('正在连接到MongoDB...');
    await mongoose.connect(config.uri, config.options);
    logger.info('成功连接到MongoDB');
    
    // 设置调试模式（开发环境）
    if (process.env.NODE_ENV === 'development') {
      mongoose.set('debug', true);
    }
    
    // 监听连接事件
    mongoose.connection.on('disconnected', () => {
      logger.warn('与MongoDB的连接已断开');
    });
    
    mongoose.connection.on('reconnected', () => {
      logger.info('已重新连接到MongoDB');
    });
    
    mongoose.connection.on('error', (err) => {
      logger.error('MongoDB连接错误', { error: err });
    });
  } catch (error) {
    logger.error('无法连接到MongoDB', { error });
    // 在生产环境中，可能希望在无法连接到数据库时退出进程
    if (process.env.NODE_ENV === 'production') {
      process.exit(1);
    }
    throw error;
  }
}

/**
 * 断开数据库连接
 */
export async function disconnectDatabase(): Promise<void> {
  try {
    logger.info('正在断开与MongoDB的连接...');
    await mongoose.disconnect();
    logger.info('已成功断开与MongoDB的连接');
  } catch (error) {
    logger.error('断开MongoDB连接时出错', { error });
    throw error;
  }
}