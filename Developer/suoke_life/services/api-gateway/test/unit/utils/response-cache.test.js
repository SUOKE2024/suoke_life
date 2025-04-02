/**
 * 响应缓存单元测试
 */
const { expect } = require('chai');
const sinon = require('sinon');
const { ResponseCache } = require('../../../src/utils/response-cache');

describe('ResponseCache', () => {
  let responseCache;
  let clock;
  
  beforeEach(() => {
    // 创建新的缓存实例用于测试
    responseCache = new ResponseCache({
      maxSize: 10,
      defaultTTL: 5, // 5秒
      cleanupInterval: 10 // 10秒
    });
    
    // 使用sinon假时钟
    clock = sinon.useFakeTimers();
  });
  
  afterEach(() => {
    clock.restore();
    responseCache.destroy();
  });
  
  describe('基本操作', () => {
    it('应正确设置和获取缓存项', () => {
      responseCache.set('key1', 'value1');
      expect(responseCache.get('key1')).to.equal('value1');
    });
    
    it('应正确删除缓存项', () => {
      responseCache.set('key1', 'value1');
      responseCache.delete('key1');
      expect(responseCache.get('key1')).to.be.undefined;
    });
    
    it('应正确清空缓存', () => {
      responseCache.set('key1', 'value1');
      responseCache.set('key2', 'value2');
      
      responseCache.clear();
      
      expect(responseCache.get('key1')).to.be.undefined;
      expect(responseCache.get('key2')).to.be.undefined;
      expect(responseCache.cacheMap.size).to.equal(0);
    });
  });
  
  describe('缓存键处理', () => {
    it('应处理字符串键', () => {
      responseCache.set('simple-key', 'value');
      expect(responseCache.get('simple-key')).to.equal('value');
    });
    
    it('应处理对象键', () => {
      const key = { id: 123, type: 'test' };
      responseCache.set(key, 'object-value');
      expect(responseCache.get(key)).to.equal('object-value');
    });
    
    it('应处理数字键', () => {
      responseCache.set(42, 'number-value');
      expect(responseCache.get(42)).to.equal('number-value');
    });
  });
  
  describe('缓存TTL', () => {
    it('应在TTL过期后返回undefined', () => {
      const key = 'expire-test';
      responseCache.set(key, 'test-value');
      
      // 前进6秒，超过默认TTL
      clock.tick(6000);
      
      expect(responseCache.get(key)).to.be.undefined;
    });
    
    it('应在获取过期项时自动删除', () => {
      const key = 'expire-delete-test';
      responseCache.set(key, 'test-value');
      
      // 前进6秒，超过默认TTL
      clock.tick(6000);
      
      // 尝试获取已过期的缓存项
      responseCache.get(key);
      
      // 验证过期项已从缓存中删除
      expect(responseCache.cacheMap.has(key)).to.be.false;
    });
  });
  
  describe('自定义TTL', () => {
    it('应支持设置自定义TTL', () => {
      responseCache.set('short-ttl', 'short', 1); // 1秒TTL
      responseCache.set('long-ttl', 'long', 10);  // 10秒TTL
      
      // 前进2秒
      clock.tick(2000);
      
      // 短TTL应过期，长TTL应保留
      expect(responseCache.get('short-ttl')).to.be.undefined;
      expect(responseCache.get('long-ttl')).to.equal('long');
    });
  });
  
  describe('容量限制', () => {
    it('应在达到容量限制时驱逐最旧的项', () => {
      // 在测试中使用较小的容量
      const smallCache = new ResponseCache({ maxSize: 3 });
      
      smallCache.set('key1', 'value1', 10);
      smallCache.set('key2', 'value2', 20);
      smallCache.set('key3', 'value3', 30);
      
      // 添加第四项，超出容量
      smallCache.set('key4', 'value4', 40);
      
      // key1应被驱逐
      expect(smallCache.get('key1')).to.be.undefined;
      expect(smallCache.get('key2')).to.equal('value2');
      expect(smallCache.get('key3')).to.equal('value3');
      expect(smallCache.get('key4')).to.equal('value4');
      
      smallCache.destroy();
    });
  });
  
  describe('过期清理', () => {
    it('应自动清理过期项', () => {
      responseCache.set('key1', 'value1', 1); // 1秒后过期
      responseCache.set('key2', 'value2', 2); // 2秒后过期
      responseCache.set('key3', 'value3', 15); // 15秒后过期
      
      // 前进3秒
      clock.tick(3000);
      
      // 触发清理
      responseCache.cleanup();
      
      // key1和key2应被清理
      expect(responseCache.get('key1')).to.be.undefined;
      expect(responseCache.get('key2')).to.be.undefined;
      expect(responseCache.get('key3')).to.not.be.undefined;
      expect(responseCache.cacheMap.size).to.equal(1);
    });
    
    it('应在指定间隔自动清理', () => {
      // 创建一个新的ResponseCache实例，避免与之前的测试互相影响
      const testCache = new ResponseCache({
        cleanupInterval: 1 // 1秒清理间隔
      });
      
      // 直接访问清理方法
      const cleanupSpy = sinon.spy(testCache, 'cleanup');
      
      // 前进1.1秒，应该触发清理
      clock.tick(1100);
      
      // 验证清理方法被调用
      expect(cleanupSpy.called).to.be.true;
      
      // 清理
      cleanupSpy.restore();
      testCache.destroy();
    });
  });
  
  describe('统计信息', () => {
    it('应正确计算命中率', () => {
      responseCache.set('hit-key', 'value');
      
      // 命中
      responseCache.get('hit-key');
      responseCache.get('hit-key');
      
      // 未命中
      responseCache.get('missing-key');
      
      const stats = responseCache.getStats();
      expect(stats.hits).to.equal(2);
      expect(stats.misses).to.equal(1);
      expect(stats.hitRate).to.equal(2/3);
    });
    
    it('应正确计算设置和逐出计数', () => {
      // 使用小缓存
      const smallCache = new ResponseCache({ maxSize: 2 });
      
      smallCache.set('key1', 'value1');
      smallCache.set('key2', 'value2');
      smallCache.set('key3', 'value3'); // 应导致驱逐
      
      const stats = smallCache.getStats();
      expect(stats.sets).to.equal(3);
      expect(stats.evicted).to.equal(1);
      
      smallCache.destroy();
    });
    
    it('应正确重置统计信息', () => {
      responseCache.set('key1', 'value1');
      responseCache.get('key1');
      responseCache.get('missing');
      
      responseCache.resetStats();
      
      const stats = responseCache.getStats();
      expect(stats.hits).to.equal(0);
      expect(stats.misses).to.equal(0);
      expect(stats.sets).to.equal(0);
    });
  });
});