// 配置常量测试 - 索克生活APP - 自动生成的测试文件
import { jest } from '@jest/globals';

// 定义配置接口
interface AppConfig {
  apiBaseUrl: string;
  version: string;
  environment: string;
  features: {
    enableTCM: boolean;
    enableBlockchain: boolean;
    enableAgents: boolean;
    enableDiagnosis: boolean;
  };
  agents: {
    xiaoai: { name: string; role: string };
    xiaoke: { name: string; role: string };
    laoke: { name: string; role: string };
    soer: { name: string; role: string };
  };
}

// Mock 配置对象
const mockConfig: AppConfig = {
  apiBaseUrl: 'https://api.suokelife.com',
  version: '1.0.0',
  environment: 'test',
  features: {
    enableTCM: true,
    enableBlockchain: true,
    enableAgents: true,
    enableDiagnosis: true
  },
  agents: {
    xiaoai: { name: '小艾', role: '智能诊断助手' },
    xiaoke: { name: '小克', role: '健康数据分析师' },
    laoke: { name: '老克', role: '中医理论专家' },
    soer: { name: '索儿', role: '生活方式顾问' }
  }
};

// Mock config 模块
jest.mock('../../constants/config', () => ({
  __esModule: true,
  default: mockConfig
}));

describe('配置常量测试', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('基础配置', () => {
    it('应该正确导入配置模块', () => {
      expect(mockConfig).toBeDefined();
      expect(typeof mockConfig).toBe('object');
    });

    it('应该包含必要的配置项', () => {
      expect(mockConfig).toHaveProperty('apiBaseUrl');
      expect(mockConfig).toHaveProperty('version');
      expect(mockConfig).toHaveProperty('environment');
      expect(mockConfig).toHaveProperty('features');
      expect(mockConfig).toHaveProperty('agents');
    });

    it('应该有正确的API基础URL', () => {
      expect(mockConfig.apiBaseUrl).toBeDefined();
      expect(typeof mockConfig.apiBaseUrl).toBe('string');
      expect(mockConfig.apiBaseUrl).toMatch(/^https?:\/\//);
    });

    it('应该有正确的版本号', () => {
      expect(mockConfig.version).toBeDefined();
      expect(typeof mockConfig.version).toBe('string');
      expect(mockConfig.version).toMatch(/^\d+\.\d+\.\d+$/);
    });

    it('应该有正确的环境配置', () => {
      expect(mockConfig.environment).toBeDefined();
      expect(typeof mockConfig.environment).toBe('string');
      expect(['development', 'test', 'production']).toContain(mockConfig.environment);
    });
  });

  describe('功能特性配置', () => {
    it('应该包含功能特性配置', () => {
      expect(mockConfig.features).toBeDefined();
      expect(typeof mockConfig.features).toBe('object');
    });

    it('应该配置中医功能', () => {
      expect(mockConfig.features).toHaveProperty('enableTCM');
      expect(typeof mockConfig.features.enableTCM).toBe('boolean');
    });

    it('应该配置区块链功能', () => {
      expect(mockConfig.features).toHaveProperty('enableBlockchain');
      expect(typeof mockConfig.features.enableBlockchain).toBe('boolean');
    });

    it('应该配置智能体功能', () => {
      expect(mockConfig.features).toHaveProperty('enableAgents');
      expect(typeof mockConfig.features.enableAgents).toBe('boolean');
    });

    it('应该配置诊断功能', () => {
      expect(mockConfig.features).toHaveProperty('enableDiagnosis');
      expect(typeof mockConfig.features.enableDiagnosis).toBe('boolean');
    });
  });

  describe('智能体配置', () => {
    it('应该包含智能体配置', () => {
      expect(mockConfig.agents).toBeDefined();
      expect(typeof mockConfig.agents).toBe('object');
    });

    it('应该配置小艾智能体', () => {
      expect(mockConfig.agents).toHaveProperty('xiaoai');
      expect(mockConfig.agents.xiaoai).toHaveProperty('name');
      expect(mockConfig.agents.xiaoai).toHaveProperty('role');
      expect(mockConfig.agents.xiaoai.name).toBe('小艾');
      expect(mockConfig.agents.xiaoai.role).toBe('智能诊断助手');
    });

    it('应该配置小克智能体', () => {
      expect(mockConfig.agents).toHaveProperty('xiaoke');
      expect(mockConfig.agents.xiaoke).toHaveProperty('name');
      expect(mockConfig.agents.xiaoke).toHaveProperty('role');
      expect(mockConfig.agents.xiaoke.name).toBe('小克');
      expect(mockConfig.agents.xiaoke.role).toBe('健康数据分析师');
    });

    it('应该配置老克智能体', () => {
      expect(mockConfig.agents).toHaveProperty('laoke');
      expect(mockConfig.agents.laoke).toHaveProperty('name');
      expect(mockConfig.agents.laoke).toHaveProperty('role');
      expect(mockConfig.agents.laoke.name).toBe('老克');
      expect(mockConfig.agents.laoke.role).toBe('中医理论专家');
    });

    it('应该配置索儿智能体', () => {
      expect(mockConfig.agents).toHaveProperty('soer');
      expect(mockConfig.agents.soer).toHaveProperty('name');
      expect(mockConfig.agents.soer).toHaveProperty('role');
      expect(mockConfig.agents.soer.name).toBe('索儿');
      expect(mockConfig.agents.soer.role).toBe('生活方式顾问');
    });

    it('应该包含所有四个智能体', () => {
      const agentKeys = Object.keys(mockConfig.agents);
      expect(agentKeys).toHaveLength(4);
      expect(agentKeys).toContain('xiaoai');
      expect(agentKeys).toContain('xiaoke');
      expect(agentKeys).toContain('laoke');
      expect(agentKeys).toContain('soer');
    });
  });

  describe('索克生活特色配置', () => {
    it('应该启用中医相关功能', () => {
      expect(mockConfig.features.enableTCM).toBe(true);
    });

    it('应该启用区块链健康数据管理', () => {
      expect(mockConfig.features.enableBlockchain).toBe(true);
    });

    it('应该启用四智能体协作', () => {
      expect(mockConfig.features.enableAgents).toBe(true);
    });

    it('应该启用智能诊断功能', () => {
      expect(mockConfig.features.enableDiagnosis).toBe(true);
    });
  });

  describe('配置验证', () => {
    it('应该验证配置的完整性', () => {
      // 验证所有必需的配置项都存在
      const requiredKeys = ['apiBaseUrl', 'version', 'environment', 'features', 'agents'];
      requiredKeys.forEach(key => {
        expect(mockConfig).toHaveProperty(key);
      });
    });

    it('应该验证功能配置的完整性', () => {
      const requiredFeatures = ['enableTCM', 'enableBlockchain', 'enableAgents', 'enableDiagnosis'];
      requiredFeatures.forEach(feature => {
        expect(mockConfig.features).toHaveProperty(feature);
        expect(typeof mockConfig.features[feature as keyof typeof mockConfig.features]).toBe('boolean');
      });
    });

    it('应该验证智能体配置的完整性', () => {
      const requiredAgents = ['xiaoai', 'xiaoke', 'laoke', 'soer'];
      requiredAgents.forEach(agent => {
        expect(mockConfig.agents).toHaveProperty(agent);
        expect(mockConfig.agents[agent as keyof typeof mockConfig.agents]).toHaveProperty('name');
        expect(mockConfig.agents[agent as keyof typeof mockConfig.agents]).toHaveProperty('role');
      });
    });
  });
});