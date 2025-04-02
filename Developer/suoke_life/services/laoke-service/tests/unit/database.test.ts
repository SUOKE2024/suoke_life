import { describe, it, expect, beforeAll, afterAll, jest } from '@jest/globals';
import mongoose from 'mongoose';
import { connectDatabase, disconnectDatabase, getConnectionStatus } from '../../src/core/database';

// 模拟mongoose
jest.mock('mongoose', () => {
  const originalModule = jest.requireActual('mongoose');
  return {
    ...originalModule,
    connect: jest.fn(),
    connection: {
      on: jest.fn(),
      close: jest.fn(),
      readyState: 1
    }
  };
});

describe('数据库连接模块', () => {
  beforeAll(() => {
    process.env.MONGODB_URI = 'mongodb://localhost:27017/test_db';
  });

  afterAll(() => {
    delete process.env.MONGODB_URI;
  });

  it('应成功连接到数据库', async () => {
    (mongoose.connect as jest.Mock).mockResolvedValueOnce(undefined);
    
    await expect(connectDatabase()).resolves.not.toThrow();
    expect(mongoose.connect).toHaveBeenCalledWith(process.env.MONGODB_URI, expect.any(Object));
  });

  it('应成功断开数据库连接', async () => {
    (mongoose.connection.close as jest.Mock).mockResolvedValueOnce(undefined);
    
    await expect(disconnectDatabase()).resolves.not.toThrow();
    expect(mongoose.connection.close).toHaveBeenCalled();
  });

  it('应返回正确的连接状态', () => {
    const status = getConnectionStatus();
    expect(status).toEqual({
      state: 'connected',
      readyState: 1
    });
  });
}); 