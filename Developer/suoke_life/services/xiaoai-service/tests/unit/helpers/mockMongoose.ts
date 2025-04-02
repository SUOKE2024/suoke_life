/**
 * Mongoose测试模拟助手
 * 提供Mongoose模型的模拟实现
 */
import { Document, Model, Query } from 'mongoose';

/**
 * 创建模拟的Mongoose执行链
 */
export const createMockExec = (result: any) => jest.fn().mockResolvedValue(result);

/**
 * 创建模拟的Mongoose模型
 */
export function createMockModel<T extends Document>(mockData: Partial<T>[] = []): jest.Mocked<Model<T>> {
  // 创建内部数据存储
  let data = [...mockData];
  
  // 创建基本查询模拟，支持链式调用
  const createMockQuery = (queryResult: any) => {
    const mockQuery = {
      exec: createMockExec(queryResult),
      limit: jest.fn().mockReturnThis(),
      skip: jest.fn().mockReturnThis(),
      sort: jest.fn().mockReturnThis(),
      select: jest.fn().mockReturnThis(),
      populate: jest.fn().mockReturnThis(),
      lean: jest.fn().mockReturnThis(),
    };
    return mockQuery as unknown as jest.Mocked<Query<any, any>>;
  };
  
  // 创建模拟的模型方法
  const mockModel = {
    find: jest.fn().mockImplementation(() => createMockQuery(data)),
    findOne: jest.fn().mockImplementation(() => createMockQuery(data[0] || null)),
    findById: jest.fn().mockImplementation((id) => createMockQuery(data.find(item => (item as any)._id === id) || null)),
    create: jest.fn().mockImplementation((newData) => {
      const created = { 
        _id: `mock-id-${Date.now()}`, 
        ...newData,
        toObject: () => ({ ...newData }),
        save: jest.fn().mockResolvedValue(newData),
      };
      data.push(created as any);
      return Promise.resolve(created);
    }),
    findByIdAndUpdate: jest.fn().mockImplementation((id, update) => {
      return createMockQuery(
        data.find(item => (item as any)._id === id) 
          ? { _id: id, ...update.$set || update }
          : null
      );
    }),
    findOneAndUpdate: jest.fn().mockImplementation((filter, update) => {
      return createMockQuery(
        data.length > 0 
          ? { ...data[0], ...update.$set || update } 
          : null
      );
    }),
    updateMany: jest.fn().mockImplementation(() => {
      return createMockQuery({ modifiedCount: Math.min(data.length, 1) });
    }),
    findByIdAndDelete: jest.fn().mockImplementation((id) => {
      const index = data.findIndex(item => (item as any)._id === id);
      return createMockQuery(index >= 0 ? data[index] : null);
    }),
    deleteOne: jest.fn().mockImplementation(() => {
      return createMockQuery({ deletedCount: Math.min(data.length, 1) });
    }),
    deleteMany: jest.fn().mockImplementation(() => {
      const count = data.length;
      data = [];
      return createMockQuery({ deletedCount: count });
    }),
    countDocuments: jest.fn().mockImplementation(() => {
      return createMockQuery(data.length);
    }),
  };
  
  return mockModel as unknown as jest.Mocked<Model<T>>;
}

/**
 * 创建模拟的文档实例
 */
export function createMockDocument<T extends Document>(data: Partial<T>): Partial<T> & Document {
  return {
    _id: `mock-id-${Date.now()}`,
    ...data,
    save: jest.fn().mockResolvedValue(data),
    toObject: jest.fn().mockReturnValue(data),
  } as any;
}

/**
 * 清除所有模拟
 */
export function clearAllMocks() {
  jest.clearAllMocks();
} 