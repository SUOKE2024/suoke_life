/**
 * 测试环境设置文件
 */
import mongoose from 'mongoose';
import { MongoMemoryServer } from 'mongodb-memory-server';
import logger from '../src/utils/logger';

// 禁用日志输出
logger.silent = true;

let mongo: MongoMemoryServer;

// 测试前的设置
beforeAll(async () => {
  // 设置测试环境变量
  process.env.NODE_ENV = 'test';
  
  // 创建内存MongoDB实例
  mongo = await MongoMemoryServer.create();
  const mongoUri = mongo.getUri();
  
  // 连接到内存数据库
  await mongoose.connect(mongoUri);
});

// 每个测试前清空数据库集合
beforeEach(async () => {
  const collections = await mongoose.connection.db.collections();
  
  for (let collection of collections) {
    await collection.deleteMany({});
  }
});

// 测试后的清理
afterAll(async () => {
  // 断开数据库连接
  if (mongoose.connection.readyState !== 0) {
    await mongoose.disconnect();
  }
  
  // 停止内存MongoDB实例
  if (mongo) {
    await mongo.stop();
  }
});

// 模拟用户授权中间件
jest.mock('../src/middlewares/require-auth', () => ({
  requireAuth: (req: any, res: any, next: any) => {
    req.currentUser = {
      id: 'test-user-id',
      email: 'test@example.com'
    };
    next();
  }
}));

// 模拟管理员授权中间件
jest.mock('../src/middlewares/require-admin', () => ({
  requireAdmin: (req: any, res: any, next: any) => {
    req.currentUser = {
      id: 'test-admin-id',
      email: 'admin@example.com',
      isAdmin: true
    };
    next();
  }
}));