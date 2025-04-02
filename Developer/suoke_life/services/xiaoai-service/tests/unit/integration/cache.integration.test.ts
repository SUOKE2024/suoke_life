/**
 * 缓存服务集成测试
 * 注意：这些测试需要实际的Redis连接
 * 在测试环境中运行时，应使用测试专用Redis实例
 */
import { CacheService } from '../../../src/services/CacheService';

// 测试前先设置环境变量
process.env.REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379/1';

describe('缓存服务集成测试', () => {
  let cacheService: CacheService;
  const testPrefix = 'test:';

  beforeAll(async () => {
    cacheService = new CacheService();
    await cacheService.connect();
  });

  beforeEach(async () => {
    // 在每个测试前清除测试数据
    await clearTestKeys();
  });

  afterAll(async () => {
    // 测试结束后清除测试数据并断开连接
    await clearTestKeys();
    await cacheService.disconnect();
  });

  // 帮助函数：清除所有测试键
  async function clearTestKeys() {
    try {
      // 注意：这里我们使用模式匹配清除所有测试键，确保不影响其他数据
      // 在实际实现中可能需要根据Redis客户端的具体方法调整
      await cacheService.flush(testPrefix + '*');
    } catch (error) {
      console.error('清除测试键失败:', error);
    }
  }

  describe('基本字符串操作', () => {
    it('应该设置和获取字符串值', async () => {
      const key = testPrefix + 'string-test';
      const value = { name: '测试', value: 123 };

      await cacheService.set(key, value);
      const result = await cacheService.get(key);

      expect(result).toEqual(value);
    });

    it('应该使用TTL设置值', async () => {
      const key = testPrefix + 'ttl-test';
      const value = 'short-lived';

      await cacheService.set(key, value, 2); // 2秒过期

      // 验证值存在
      const result1 = await cacheService.get(key);
      expect(result1).toBe(value);

      // 等待过期
      await new Promise(resolve => setTimeout(resolve, 2100));

      // 验证值已过期
      const result2 = await cacheService.get(key);
      expect(result2).toBeNull();
    });

    it('应该删除键', async () => {
      const key = testPrefix + 'delete-test';
      await cacheService.set(key, 'to-delete');

      // 验证值存在
      const result1 = await cacheService.get(key);
      expect(result1).toBe('to-delete');

      // 删除键
      await cacheService.del(key);

      // 验证键已删除
      const result2 = await cacheService.get(key);
      expect(result2).toBeNull();
    });
  });

  describe('哈希表操作', () => {
    it('应该设置和获取哈希字段', async () => {
      const key = testPrefix + 'hash-test';
      const field = 'field1';
      const value = { data: '哈希测试', number: 456 };

      await cacheService.hset(key, field, value);
      const result = await cacheService.hget(key, field);

      expect(result).toEqual(value);
    });

    it('应该获取整个哈希表', async () => {
      const key = testPrefix + 'hash-all-test';
      
      await cacheService.hset(key, 'field1', 'value1');
      await cacheService.hset(key, 'field2', 'value2');
      await cacheService.hset(key, 'field3', { complex: true });

      const result = await cacheService.hgetall(key);

      expect(result).toHaveProperty('field1', 'value1');
      expect(result).toHaveProperty('field2', 'value2');
      expect(result).toHaveProperty('field3');
      expect(result.field3).toEqual({ complex: true });
    });

    it('应该删除哈希字段', async () => {
      const key = testPrefix + 'hash-del-test';
      const field = 'to-delete';

      await cacheService.hset(key, field, 'delete-me');
      await cacheService.hset(key, 'keep', 'keep-me');

      // 验证字段存在
      const result1 = await cacheService.hget(key, field);
      expect(result1).toBe('delete-me');

      // 删除字段
      await cacheService.hdel(key, field);

      // 验证字段已删除
      const result2 = await cacheService.hget(key, field);
      expect(result2).toBeNull();

      // 验证其他字段仍然存在
      const result3 = await cacheService.hget(key, 'keep');
      expect(result3).toBe('keep-me');
    });
  });

  describe('列表操作', () => {
    it('应该操作列表', async () => {
      const key = testPrefix + 'list-test';
      
      // 添加元素到列表
      await cacheService.lpush(key, 'item1');
      await cacheService.lpush(key, 'item2');
      await cacheService.rpush(key, 'item3');

      // 获取列表长度
      const length = await cacheService.llen(key);
      expect(length).toBe(3);

      // 获取列表范围
      const range = await cacheService.lrange(key, 0, -1);
      expect(range).toHaveLength(3);
      expect(range).toContain('item1');
      expect(range).toContain('item2');
      expect(range).toContain('item3');
      
      // 弹出元素
      const popped = await cacheService.lpop(key);
      expect(popped).toBe('item2');
      
      // 验证长度减少
      const newLength = await cacheService.llen(key);
      expect(newLength).toBe(2);
    });
  });

  describe('自增/自减操作', () => {
    it('应该增加计数器值', async () => {
      const key = testPrefix + 'counter-test';
      
      // 初始化计数器
      await cacheService.set(key, 5);
      
      // 增加计数器
      const result1 = await cacheService.incr(key);
      expect(result1).toBe(6);
      
      // 增加指定值
      const result2 = await cacheService.incrby(key, 3);
      expect(result2).toBe(9);
      
      // 获取最终值
      const final = await cacheService.get(key);
      expect(final).toBe(9);
    });

    it('应该减少计数器值', async () => {
      const key = testPrefix + 'decr-counter-test';
      
      // 初始化计数器
      await cacheService.set(key, 10);
      
      // 减少计数器
      const result1 = await cacheService.decr(key);
      expect(result1).toBe(9);
      
      // 减少指定值
      const result2 = await cacheService.decrby(key, 4);
      expect(result2).toBe(5);
      
      // 获取最终值
      const final = await cacheService.get(key);
      expect(final).toBe(5);
    });
  });
}); 