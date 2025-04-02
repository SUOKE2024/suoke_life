/**
 * SMS服务测试
 */
const { describe, it, expect, beforeEach, afterEach } = require('@jest/globals');
const ValidationError = require('../../utils/errors').ValidationError;

// 模拟配置
const mockConfig = {
  sms: {
    provider: 'aliyun',
    accessKeyId: 'test-key-id',
    accessKeySecret: 'test-key-secret',
    signName: 'TestSign',
    templates: {
      login: 'SMS_123456',
      register: 'SMS_654321',
      verify_phone: 'SMS_111222',
      reset_password: 'SMS_222333'
    }
  },
  security: {
    smsVerification: {
      codeLength: 6,
      codeExpiry: 300,
      sendInterval: 60,
      maxDailySends: 10,
      maxAttempts: 5
    }
  }
};

// 模拟依赖
jest.mock('../../utils/logger', () => ({
  info: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  debug: jest.fn()
}));

jest.mock('../../utils/redis', () => ({
  get: jest.fn(),
  set: jest.fn(),
  del: jest.fn(),
  expire: jest.fn()
}));

// 模拟阿里云SDK
jest.mock('@alicloud/dysmsapi20170525', () => {
  const mockClient = {
    sendSms: jest.fn().mockImplementation(() => {
      return Promise.resolve({
        body: {
          code: 'OK',
          message: '发送成功',
          requestId: 'test-request-id',
          bizId: 'test-biz-id'
        }
      });
    })
  };
  
  return {
    Client: jest.fn().mockImplementation(() => mockClient)
  };
});

// 导入被测试服务
const SMSService = require('../../services/sms.service');
const redis = require('../../utils/redis');
const logger = require('../../utils/logger');

describe('SMSService', () => {
  let smsService;

  beforeEach(() => {
    jest.clearAllMocks();
    smsService = new SMSService(mockConfig);
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('sendVerificationCode', () => {
    it('应成功发送验证码', async () => {
      // 模拟未超过发送限制
      redis.get.mockResolvedValue(null);
      
      const result = await smsService.sendVerificationCode({
        phone: '13800138000',
        type: 'login'
      });
      
      expect(result).toBeTruthy();
      expect(result.success).toBe(true);
      expect(result.requestId).toBeTruthy();
      expect(redis.set).toHaveBeenCalledTimes(2); // 设置验证码和计数器
      expect(redis.expire).toHaveBeenCalledTimes(2);
    });
    
    it('短时间内重复发送应被限制', async () => {
      // 模拟最近已发送
      redis.get.mockResolvedValueOnce(JSON.stringify({
        timestamp: Date.now()
      }));
      
      await expect(smsService.sendVerificationCode({
        phone: '13800138000',
        type: 'login'
      })).rejects.toThrow();
    });
    
    it('超过每日最大发送次数应被限制', async () => {
      // 模拟未超过发送间隔但超过每日限制
      redis.get
        .mockResolvedValueOnce(null) // 发送间隔检查
        .mockResolvedValueOnce('10'); // 每日计数检查
      
      await expect(smsService.sendVerificationCode({
        phone: '13800138000',
        type: 'login'
      })).rejects.toThrow();
    });
    
    it('手机号格式无效应抛出错误', async () => {
      await expect(smsService.sendVerificationCode({
        phone: '1380013', // 无效手机号
        type: 'login'
      })).rejects.toThrow();
    });
    
    it('不支持的短信类型应抛出错误', async () => {
      await expect(smsService.sendVerificationCode({
        phone: '13800138000',
        type: 'unknown_type' // 不支持的类型
      })).rejects.toThrow();
    });
  });
  
  describe('verifyCode', () => {
    it('验证码正确应验证成功', async () => {
      // 模拟存储的验证码
      redis.get.mockResolvedValue(JSON.stringify({
        code: '123456',
        attempts: 0,
        expired: false
      }));
      
      const result = await smsService.verifyCode({
        phone: '13800138000',
        code: '123456',
        type: 'login'
      });
      
      expect(result).toBe(true);
      expect(redis.del).toHaveBeenCalled();
    });
    
    it('验证码错误应验证失败', async () => {
      // 模拟存储的验证码
      redis.get.mockResolvedValue(JSON.stringify({
        code: '123456',
        attempts: 0,
        expired: false
      }));
      
      const result = await smsService.verifyCode({
        phone: '13800138000',
        code: '654321', // 错误的验证码
        type: 'login'
      });
      
      expect(result).toBe(false);
      
      // 尝试次数应增加
      expect(redis.set).toHaveBeenCalled();
    });
    
    it('验证码过期应验证失败', async () => {
      // 模拟存储的过期验证码
      redis.get.mockResolvedValue(JSON.stringify({
        code: '123456',
        attempts: 0,
        expired: true
      }));
      
      const result = await smsService.verifyCode({
        phone: '13800138000',
        code: '123456',
        type: 'login'
      });
      
      expect(result).toBe(false);
    });
    
    it('超过最大尝试次数应验证失败', async () => {
      // 模拟存储的验证码且尝试次数已达上限
      redis.get.mockResolvedValue(JSON.stringify({
        code: '123456',
        attempts: 5,
        expired: false
      }));
      
      const result = await smsService.verifyCode({
        phone: '13800138000',
        code: '123456',
        type: 'login'
      });
      
      expect(result).toBe(false);
      expect(redis.del).toHaveBeenCalled(); // 应删除验证码
    });
    
    it('验证码不存在应验证失败', async () => {
      // 模拟验证码不存在
      redis.get.mockResolvedValue(null);
      
      const result = await smsService.verifyCode({
        phone: '13800138000',
        code: '123456',
        type: 'login'
      });
      
      expect(result).toBe(false);
    });
  });
}); 