import mongoose from 'mongoose';
import { Logger } from '../utils/logger';

const logger = new Logger('Database');

/**
 * 数据库连接管理类
 */
export class Database {
  private static instance: Database;
  private isConnected: boolean = false;
  private uri: string;

  /**
   * 构造函数
   */
  private constructor() {
    this.uri = process.env.MONGODB_URI || 'mongodb://localhost:27017/smell-diagnosis';
    this.setupMongooseEvents();
  }

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
   * 连接数据库
   */
  public async connect(): Promise<void> {
    if (this.isConnected) {
      logger.info('数据库已连接');
      return;
    }

    try {
      logger.info('连接到MongoDB...', { uri: this.uri.replace(/\/\/([^:]+):([^@]+)@/, '//***:***@') });
      
      await mongoose.connect(this.uri);
      
      this.isConnected = true;
      logger.info('MongoDB连接成功');
    } catch (error) {
      logger.error('MongoDB连接失败', { error: (error as Error).message });
      throw error;
    }
  }

  /**
   * 断开数据库连接
   */
  public async disconnect(): Promise<void> {
    if (!this.isConnected) {
      return;
    }

    try {
      await mongoose.disconnect();
      this.isConnected = false;
      logger.info('MongoDB连接已断开');
    } catch (error) {
      logger.error('断开MongoDB连接失败', { error: (error as Error).message });
      throw error;
    }
  }

  /**
   * 检查数据库连接状态
   */
  public isConnectedToDatabase(): boolean {
    return this.isConnected && mongoose.connection.readyState === 1;
  }

  /**
   * 设置Mongoose事件监听
   */
  private setupMongooseEvents(): void {
    mongoose.connection.on('connected', () => {
      logger.info('Mongoose连接成功');
    });

    mongoose.connection.on('error', (err) => {
      logger.error('Mongoose连接错误', { error: err.message });
      this.isConnected = false;
    });

    mongoose.connection.on('disconnected', () => {
      logger.info('Mongoose连接断开');
      this.isConnected = false;
    });

    // 处理应用程序终止
    process.on('SIGINT', async () => {
      await this.disconnect();
      process.exit(0);
    });
  }
}

// 导出数据库实例
export const db = Database.getInstance();