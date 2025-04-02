/**
 * Redis测试模拟助手
 * 提供Redis客户端的模拟实现
 */
import { RedisClientType } from 'redis';

/**
 * 创建模拟的Redis客户端
 */
export function createMockRedisClient(): jest.Mocked<Partial<RedisClientType>> {
  // 创建内存存储，模拟Redis数据
  const storage = new Map<string, string>();
  const hashStorage = new Map<string, Map<string, string>>();
  let isConnected = false;
  
  // 事件回调
  const eventHandlers = new Map<string, Function[]>();
  
  const mockClient = {
    // 连接管理
    connect: jest.fn().mockImplementation(() => {
      isConnected = true;
      triggerEvent('connect');
      return Promise.resolve();
    }),
    disconnect: jest.fn().mockImplementation(() => {
      isConnected = false;
      triggerEvent('disconnect');
      return Promise.resolve();
    }),
    
    // 事件处理
    on: jest.fn().mockImplementation((event: string, callback: Function) => {
      if (!eventHandlers.has(event)) {
        eventHandlers.set(event, []);
      }
      eventHandlers.get(event)?.push(callback);
      return mockClient;
    }),
    
    // 字符串操作
    set: jest.fn().mockImplementation((key: string, value: string) => {
      storage.set(key, value);
      return Promise.resolve('OK');
    }),
    setEx: jest.fn().mockImplementation((key: string, ttl: number, value: string) => {
      storage.set(key, value);
      return Promise.resolve('OK');
    }),
    get: jest.fn().mockImplementation((key: string) => {
      return Promise.resolve(storage.get(key) || null);
    }),
    del: jest.fn().mockImplementation((key: string) => {
      const deleted = storage.delete(key);
      return Promise.resolve(deleted ? 1 : 0);
    }),
    exists: jest.fn().mockImplementation((key: string) => {
      return Promise.resolve(storage.has(key) ? 1 : 0);
    }),
    expire: jest.fn().mockImplementation((key: string, seconds: number) => {
      return Promise.resolve(storage.has(key) ? 1 : 0);
    }),
    ttl: jest.fn().mockImplementation((key: string) => {
      return Promise.resolve(storage.has(key) ? 1000 : -2);
    }),
    incr: jest.fn().mockImplementation((key: string) => {
      const value = storage.get(key);
      const num = value ? parseInt(value) + 1 : 1;
      storage.set(key, num.toString());
      return Promise.resolve(num);
    }),
    
    // 哈希表操作
    hSet: jest.fn().mockImplementation((key: string, field: string, value: string) => {
      if (!hashStorage.has(key)) {
        hashStorage.set(key, new Map());
      }
      hashStorage.get(key)?.set(field, value);
      return Promise.resolve(1);
    }),
    hGet: jest.fn().mockImplementation((key: string, field: string) => {
      return Promise.resolve(hashStorage.get(key)?.get(field) || null);
    }),
    hGetAll: jest.fn().mockImplementation((key: string) => {
      if (!hashStorage.has(key)) {
        return Promise.resolve({});
      }
      const map = hashStorage.get(key)!;
      const result: Record<string, string> = {};
      map.forEach((value, field) => {
        result[field] = value;
      });
      return Promise.resolve(result);
    }),
    hDel: jest.fn().mockImplementation((key: string, field: string) => {
      const map = hashStorage.get(key);
      if (!map) return Promise.resolve(0);
      const deleted = map.delete(field);
      return Promise.resolve(deleted ? 1 : 0);
    }),
    
    // 其他操作
    flushAll: jest.fn().mockImplementation(() => {
      storage.clear();
      hashStorage.clear();
      return Promise.resolve('OK');
    }),
  };
  
  // 触发事件辅助函数
  function triggerEvent(event: string, ...args: any[]) {
    const handlers = eventHandlers.get(event) || [];
    handlers.forEach(handler => handler(...args));
  }
  
  return mockClient as jest.Mocked<Partial<RedisClientType>>;
}

/**
 * 清除所有模拟
 */
export function clearRedisMocks() {
  jest.clearAllMocks();
} 