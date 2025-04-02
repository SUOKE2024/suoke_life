/**
 * BiometricService 单元测试
 */
const { describe, it, expect, beforeEach, afterEach } = require('@jest/globals');
const ValidationError = require('../../../utils/errors').ValidationError;

// 模拟依赖
jest.mock('../../../utils/logger', () => ({
  info: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  debug: jest.fn()
}));

jest.mock('../../../utils/redis', () => ({
  get: jest.fn(),
  set: jest.fn(),
  del: jest.fn(),
  expire: jest.fn(),
  getClient: jest.fn(() => ({
    get: jest.fn(),
    set: jest.fn(),
    del: jest.fn(),
    expire: jest.fn()
  }))
}));

// 模拟数据库操作
jest.mock('../../../database', () => ({
  query: jest.fn(),
  transaction: jest.fn(callback => callback({
    query: jest.fn()
  }))
}));

// 模拟指标服务
jest.mock('../../../services/metrics.service', () => ({
  increment: jest.fn(),
  timing: jest.fn(),
  gauge: jest.fn()
}));

const BiometricService = require('../../../services/biometric.service');
const db = require('../../../database');
const redis = require('../../../utils/redis');
const logger = require('../../../utils/logger');
const metricsService = require('../../../services/metrics.service');

describe('BiometricService', () => {
  let biometricService;
  const mockConfig = {
    authentication: {
      biometric: {
        enabled: true,
        validTypes: ['face', 'fingerprint'],
        challengeExpiration: 300,
        maxAttempts: 5
      }
    }
  };

  const mockUser = {
    id: 'user-123',
    email: 'test@example.com'
  };

  const mockDevice = {
    id: 'device-456',
    user_id: 'user-123'
  };

  beforeEach(() => {
    // 重置所有模拟
    jest.clearAllMocks();
    
    // 创建服务实例
    biometricService = new BiometricService(mockConfig);
    
    // 模拟数据库查询返回值
    db.query.mockImplementation((sql, params) => {
      if (sql.includes('SELECT * FROM users')) {
        return Promise.resolve([mockUser]);
      }
      if (sql.includes('SELECT * FROM devices')) {
        return Promise.resolve([mockDevice]);
      }
      if (sql.includes('SELECT * FROM biometric_credentials')) {
        return Promise.resolve([{
          id: 'cred-789',
          user_id: 'user-123',
          device_id: 'device-456',
          type: 'fingerprint',
          public_key: 'mock-public-key',
          created_at: new Date()
        }]);
      }
      if (sql.includes('INSERT INTO biometric_credentials')) {
        return Promise.resolve({ insertId: 'new-cred-id' });
      }
      if (sql.includes('UPDATE biometric_credentials')) {
        return Promise.resolve({ affectedRows: 1 });
      }
      return Promise.resolve([]);
    });
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('register', () => {
    it('应该成功注册生物特征凭证', async () => {
      const result = await biometricService.register({
        userId: 'user-123',
        deviceId: 'device-456',
        type: 'fingerprint',
        publicKey: 'mock-public-key'
      });

      expect(result).toBeTruthy();
      expect(db.query).toHaveBeenCalled();
      expect(metricsService.increment).toHaveBeenCalledWith('biometric_register_success', { type: 'fingerprint' });
    });

    it('应该更新现有的生物特征凭证', async () => {
      const result = await biometricService.register({
        userId: 'user-123',
        deviceId: 'device-456',
        type: 'fingerprint',
        publicKey: 'new-public-key'
      });

      expect(result).toBeTruthy();
      expect(db.query).toHaveBeenCalled();
      expect(metricsService.increment).toHaveBeenCalledWith('biometric_register_success', { type: 'fingerprint' });
    });

    it('如果服务被禁用，应该抛出错误', async () => {
      biometricService = new BiometricService({
        authentication: {
          biometric: {
            enabled: false
          }
        }
      });

      await expect(biometricService.register({
        userId: 'user-123',
        deviceId: 'device-456',
        type: 'fingerprint',
        publicKey: 'mock-public-key'
      })).rejects.toThrow();
      
      expect(metricsService.increment).toHaveBeenCalledWith('biometric_register_error', { reason: 'disabled' });
    });

    it('如果使用不支持的生物特征类型，应该抛出错误', async () => {
      await expect(biometricService.register({
        userId: 'user-123',
        deviceId: 'device-456',
        type: 'voice', // 不支持的类型
        publicKey: 'mock-public-key'
      })).rejects.toThrow();
      
      expect(metricsService.increment).toHaveBeenCalledWith('biometric_register_error', { reason: 'invalid_type' });
    });
  });

  describe('verify', () => {
    it('应该成功验证生物特征凭证', async () => {
      // 模拟挑战生成
      redis.get.mockResolvedValue(JSON.stringify({
        challenge: 'mock-challenge',
        attempts: 0,
        expired: false
      }));

      const result = await biometricService.verify({
        userId: 'user-123',
        deviceId: 'device-456',
        type: 'fingerprint',
        signedChallenge: 'signed-challenge-data'
      });

      expect(result).toBeTruthy();
      expect(redis.del).toHaveBeenCalled();
      expect(metricsService.increment).toHaveBeenCalledWith('biometric_verify_success', { type: 'fingerprint' });
    });

    it('如果挑战过期，应该抛出错误', async () => {
      redis.get.mockResolvedValue(JSON.stringify({
        challenge: 'mock-challenge',
        attempts: 0,
        expired: true
      }));

      await expect(biometricService.verify({
        userId: 'user-123',
        deviceId: 'device-456',
        type: 'fingerprint',
        signedChallenge: 'signed-challenge-data'
      })).rejects.toThrow();
      
      expect(metricsService.increment).toHaveBeenCalledWith('biometric_verify_error', { reason: 'challenge_expired' });
    });
  });

  describe('generateChallenge', () => {
    it('应该生成一个有效的挑战值', async () => {
      const challenge = await biometricService.generateChallenge({
        userId: 'user-123',
        deviceId: 'device-456',
        type: 'fingerprint'
      });

      expect(challenge).toBeTruthy();
      expect(typeof challenge).toBe('string');
      expect(redis.set).toHaveBeenCalled();
      expect(redis.expire).toHaveBeenCalled();
      expect(metricsService.increment).toHaveBeenCalledWith('biometric_challenge_generated', { type: 'fingerprint' });
    });

    it('如果用户没有注册生物特征凭证，应该抛出错误', async () => {
      db.query.mockImplementationOnce(() => Promise.resolve([])); // 没有找到凭证

      await expect(biometricService.generateChallenge({
        userId: 'user-123',
        deviceId: 'device-456',
        type: 'fingerprint'
      })).rejects.toThrow();
      
      expect(metricsService.increment).toHaveBeenCalledWith('biometric_challenge_error', { reason: 'no_credentials' });
    });
  });
});