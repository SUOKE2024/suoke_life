/**
 * 测试前置配置文件
 */

// 加载环境变量（测试环境）
process.env.NODE_ENV = 'test';

// 确保使用测试环境的端口
process.env.PORT = process.env.TEST_PORT || 4000;

// 模拟日志避免测试输出过多日志
jest.mock('../src/utils/logger', () => ({
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
  debug: jest.fn()
}));

// 为所有测试设置全局超时时间（毫秒）
jest.setTimeout(15000);