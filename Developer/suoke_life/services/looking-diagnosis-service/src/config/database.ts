import mongoose from 'mongoose';
import { Logger } from '../utils/logger';

const logger = new Logger('Database');

/**
 * 数据库连接类
 * 负责建立和管理MongoDB连接
 */
export class Database {
  private static instance: Database;
  private isConnected = false;

  private constructor() {
    // 私有构造函数，防止直接实例化
  }

  /**
   * 获取数据库连接实例
   * @returns Database实例
   */
  public static getInstance(): Database {
    if (!Database.instance) {
      Database.instance = new Database();
    }
    return Database.instance;
  }

  /**
   * 连接到MongoDB数据库
   */
  public async connect(): Promise<void> {
    if (this.isConnected) {
      logger.info('已经连接到数据库');
      return;
    }

    try {
      const uri = process.env.MONGODB_URI || 'mongodb://localhost:27017/looking-diagnosis';
      
      // 设置MongoDB连接选项
      const options = {
        useNewUrlParser: true,
        useUnifiedTopology: true,
      } as mongoose.ConnectOptions;
      
      // 连接到MongoDB
      await mongoose.connect(uri, options);
      
      this.isConnected = true;
      logger.info(`成功连接到MongoDB: ${uri}`);
      
      // 监听MongoDB连接事件
      mongoose.connection.on('error', (err) => {
        logger.error(`MongoDB连接错误: ${err}`);
        this.isConnected = false;
      });
      
      mongoose.connection.on('disconnected', () => {
        logger.warn('MongoDB连接断开');
        this.isConnected = false;
      });
      
    } catch (error) {
      logger.error(`连接数据库失败: ${error.message}`);
      throw error;
    }
  }

  /**
   * 断开MongoDB连接
   */
  public async disconnect(): Promise<void> {
    if (!this.isConnected) {
      logger.info('没有活动的数据库连接');
      return;
    }

    try {
      await mongoose.disconnect();
      this.isConnected = false;
      logger.info('已断开MongoDB连接');
    } catch (error) {
      logger.error(`断开数据库连接失败: ${error.message}`);
      throw error;
    }
  }
}

// 导出单例实例
export const db = Database.getInstance(); 