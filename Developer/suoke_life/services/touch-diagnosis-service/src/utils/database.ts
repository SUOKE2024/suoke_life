import mongoose from 'mongoose';
import { Logger } from './logger';

const logger = new Logger('Database');

/**
 * 数据库连接管理类
 */
export class Database {
  private static instance: Database;
  private isConnected: boolean = false;
  
  /**
   * 获取单例实例
   */
  public static getInstance(): Database {
    if (!Database.instance) {
      Database.instance = new Database();
    }
    return Database.instance;
  }
  
  /**
   * 初始化数据库连接
   */
  public async connect(): Promise<void> {
    if (this.isConnected) {
      logger.info('数据库已连接，跳过重复连接');
      return;
    }
    
    try {
      const mongoUri = process.env.MONGODB_URI || 'mongodb://localhost:27017/touch-diagnosis';
      
      // 设置连接选项
      const options = {
        useNewUrlParser: true,
        useUnifiedTopology: true,
        serverSelectionTimeoutMS: 5000,
        autoIndex: true,
        retryWrites: true
      };
      
      logger.info(`连接到MongoDB: ${mongoUri.split('@').pop()}`);
      
      // 连接到数据库
      await mongoose.connect(mongoUri);
      
      this.isConnected = true;
      logger.info('MongoDB连接成功');
      
      // 监听连接事件
      mongoose.connection.on('error', (err) => {
        logger.error('MongoDB连接错误:', { error: err });
        this.isConnected = false;
      });
      
      mongoose.connection.on('disconnected', () => {
        logger.warn('MongoDB连接断开');
        this.isConnected = false;
      });
      
      mongoose.connection.on('reconnected', () => {
        logger.info('MongoDB重新连接成功');
        this.isConnected = true;
      });
      
    } catch (error) {
      logger.error('MongoDB连接失败:', { error });
      this.isConnected = false;
      throw error;
    }
  }
  
  /**
   * 断开数据库连接
   */
  public async disconnect(): Promise<void> {
    if (!this.isConnected) {
      logger.info('数据库未连接，无需断开');
      return;
    }
    
    try {
      await mongoose.disconnect();
      this.isConnected = false;
      logger.info('MongoDB连接已断开');
    } catch (error) {
      logger.error('断开MongoDB连接失败:', { error });
      throw error;
    }
  }
  
  /**
   * 获取连接状态
   */
  public isConnectedToDatabase(): boolean {
    return this.isConnected;
  }
}

// 导出默认实例
export default Database.getInstance(); 