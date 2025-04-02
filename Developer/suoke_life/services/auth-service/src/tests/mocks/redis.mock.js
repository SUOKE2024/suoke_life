/**
 * Redis客户端模拟文件
 */

// 创建内存存储对象模拟Redis存储
const redisStore = new Map();

// 模拟Redis客户端
const mockRedisClient = {
  // 设置键值对
  set: jest.fn((key, value, options) => {
    redisStore.set(key, value);
    return Promise.resolve('OK');
  }),
  
  // 通过键获取值
  get: jest.fn((key) => {
    return Promise.resolve(redisStore.get(key) || null);
  }),
  
  // 删除键
  del: jest.fn((key) => {
    redisStore.delete(key);
    return Promise.resolve(1);
  }),
  
  // 设置键值对并设置过期时间
  setex: jest.fn((key, seconds, value) => {
    redisStore.set(key, value);
    return Promise.resolve('OK');
  }),
  
  // 获取所有匹配模式的键
  keys: jest.fn((pattern) => {
    const allKeys = Array.from(redisStore.keys());
    // 简单实现模式匹配（仅支持*通配符的简单情况）
    if (pattern === '*') {
      return Promise.resolve(allKeys);
    }
    
    const patternRegex = new RegExp(
      '^' + pattern.replace(/\*/g, '.*') + '$'
    );
    
    return Promise.resolve(
      allKeys.filter(key => patternRegex.test(key))
    );
  }),
  
  // 检查键是否存在
  exists: jest.fn((key) => {
    return Promise.resolve(redisStore.has(key) ? 1 : 0);
  }),
  
  // 设置键的过期时间
  expire: jest.fn((key, seconds) => {
    if (redisStore.has(key)) {
      return Promise.resolve(1);
    }
    return Promise.resolve(0);
  }),
  
  // 模拟连接方法
  connect: jest.fn().mockResolvedValue(undefined),
  
  // 模拟关闭方法
  quit: jest.fn().mockResolvedValue('OK'),
  
  // 清除所有测试数据
  clearAll: () => {
    redisStore.clear();
  }
};

// 导出模拟Redis客户端
module.exports = mockRedisClient; 