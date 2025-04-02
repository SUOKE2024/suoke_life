import * as fs from 'fs';
import { jest } from '@jest/globals';
import { loadConfig } from '../../../src/utils/config-loader';

// 模拟fs模块
jest.mock('fs', () => ({
  readFileSync: jest.fn(),
  existsSync: jest.fn()
}));

describe('配置加载器', () => {
  const mockConfig = {
    server: { port: 3000 },
    auth: { enabled: true }
  };

  beforeEach(() => {
    jest.resetModules();
    jest.clearAllMocks();
    delete process.env.CONFIG_PATH;
    delete process.env.NODE_ENV;
    
    // 默认配置存在
    (fs.existsSync as jest.Mock).mockReturnValue(true);
    // 默认返回有效JSON
    (fs.readFileSync as jest.Mock).mockReturnValue(JSON.stringify(mockConfig));
  });

  it('应返回有效的配置', () => {
    const config = loadConfig();
    expect(config).toHaveProperty('server');
    expect(config).toHaveProperty('auth');
  });

  it('应在测试环境中处理文件不存在的情况', () => {
    process.env.NODE_ENV = 'test';
    (fs.existsSync as jest.Mock).mockReturnValue(false);
    
    // 不应抛出错误
    expect(() => loadConfig()).not.toThrow();
    
    // 应返回默认配置
    const config = loadConfig();
    expect(config).toBeDefined();
  });
}); 