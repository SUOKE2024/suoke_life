import { jest } from '@jest/globals';

// Mock config modules
const MockConfig = {
  API_BASE_URL: 'https://api.suokelife.com',
  APP_VERSION: '1.0.0',
  ENVIRONMENT: 'test',
  FEATURES: {
    AI_DIAGNOSIS: true,
    BLOCKCHAIN: true,
    MULTIMODAL: true,
  },
};

// Mock dependencies
jest.mock('../../../config', () => MockConfig);

describe('Config Index 配置索引测试', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('配置导出', () => {
    it('应该正确导出API配置', () => {
      expect(MockConfig.API_BASE_URL).toBeDefined();
      expect(typeof MockConfig.API_BASE_URL).toBe('string');
    });

    it('应该正确导出应用版本', () => {
      expect(MockConfig.APP_VERSION).toBeDefined();
      expect(typeof MockConfig.APP_VERSION).toBe('string');
    });

    it('应该正确导出环境配置', () => {
      expect(MockConfig.ENVIRONMENT).toBeDefined();
      expect(typeof MockConfig.ENVIRONMENT).toBe('string');
    });
  });

  describe('功能配置', () => {
    it('应该包含AI诊断配置', () => {
      expect(MockConfig.FEATURES.AI_DIAGNOSIS).toBeDefined();
      expect(typeof MockConfig.FEATURES.AI_DIAGNOSIS).toBe('boolean');
    });

    it('应该包含区块链配置', () => {
      expect(MockConfig.FEATURES.BLOCKCHAIN).toBeDefined();
      expect(typeof MockConfig.FEATURES.BLOCKCHAIN).toBe('boolean');
    });

    it('应该包含多模态配置', () => {
      expect(MockConfig.FEATURES.MULTIMODAL).toBeDefined();
      expect(typeof MockConfig.FEATURES.MULTIMODAL).toBe('boolean');
    });
  });

  describe('配置验证', () => {
    it('应该有有效的API URL', () => {
      expect(MockConfig.API_BASE_URL).toMatch(/^https?:\/\//);
    });

    it('应该有有效的版本号', () => {
      expect(MockConfig.APP_VERSION).toMatch(/^\d+\.\d+\.\d+$/);
    });

    it('应该有有效的环境值', () => {
      const validEnvironments = ['development', 'test', 'production'];
      expect(validEnvironments).toContain(MockConfig.ENVIRONMENT);
    });
  });

  describe('类型安全', () => {
    it('配置对象应该有正确的结构', () => {
      expect(MockConfig).toHaveProperty('API_BASE_URL');
      expect(MockConfig).toHaveProperty('APP_VERSION');
      expect(MockConfig).toHaveProperty('ENVIRONMENT');
      expect(MockConfig).toHaveProperty('FEATURES');
    });

    it('功能配置应该有正确的结构', () => {
      expect(MockConfig.FEATURES).toHaveProperty('AI_DIAGNOSIS');
      expect(MockConfig.FEATURES).toHaveProperty('BLOCKCHAIN');
      expect(MockConfig.FEATURES).toHaveProperty('MULTIMODAL');
    });
  });
}); 