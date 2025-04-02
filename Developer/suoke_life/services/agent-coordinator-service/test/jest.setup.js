// Jest测试全局设置

// 设置超时为10秒
jest.setTimeout(10000);

// 模拟process.env环境变量
process.env.NODE_ENV = 'test';
process.env.PORT = '4001';
process.env.REDIS_HOST = 'localhost';
process.env.REDIS_PORT = '6379';

// 模拟console以减少测试输出
global.console = {
  ...console,
  log: jest.fn(),
  info: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
};

// 清理所有模拟
beforeEach(() => {
  jest.clearAllMocks();
});

// 添加自定义matcher
expect.extend({
  toBeWithinRange(received, floor, ceiling) {
    const pass = received >= floor && received <= ceiling;
    if (pass) {
      return {
        message: () => `expected ${received} not to be within range ${floor} - ${ceiling}`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected ${received} to be within range ${floor} - ${ceiling}`,
        pass: false,
      };
    }
  },
}); 