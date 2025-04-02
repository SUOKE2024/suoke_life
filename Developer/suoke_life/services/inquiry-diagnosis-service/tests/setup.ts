/**
 * 测试环境设置
 */

// 设置测试环境变量
process.env.NODE_ENV = 'test';

// 在这里可以添加全局的测试设置，例如:
// - 模拟外部服务
// - 设置测试数据库连接
// - 创建全局测试工具等

// 控制测试日志输出级别
process.env.LOG_LEVEL = 'error';

// 禁用测试环境中的控制台日志
jest.spyOn(console, 'log').mockImplementation(() => {});
jest.spyOn(console, 'info').mockImplementation(() => {});
jest.spyOn(console, 'warn').mockImplementation(() => {});
// 保留错误日志以便于调试
// jest.spyOn(console, 'error').mockImplementation(() => {}); 