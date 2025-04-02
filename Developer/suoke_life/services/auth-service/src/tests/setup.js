/**
 * Jest 测试设置文件
 */

// 设置环境变量
process.env.NODE_ENV = 'test';
process.env.JWT_SECRET = 'test-secret';
process.env.DB_HOST = 'localhost';
process.env.DB_USER = 'test';
process.env.DB_PASSWORD = 'test';
process.env.DB_NAME = 'auth_test';

// 全局 Jest 配置
jest.setTimeout(30000); // 30秒超时

// 全局模拟
// 模拟HTTP响应对象
global.mockResponse = () => {
  const res = {};
  res.status = jest.fn().mockReturnValue(res);
  res.json = jest.fn().mockReturnValue(res);
  res.send = jest.fn().mockReturnValue(res);
  res.cookie = jest.fn().mockReturnValue(res);
  res.clearCookie = jest.fn().mockReturnValue(res);
  res.header = jest.fn().mockReturnValue(res);
  return res;
};

// 模拟HTTP请求对象
global.mockRequest = (body = {}, params = {}, query = {}, headers = {}, user = null) => {
  return {
    body,
    params,
    query,
    headers,
    user,
    get: jest.fn(key => headers[key]),
    cookies: {},
    ip: '127.0.0.1',
    method: 'GET',
    path: '/',
    session: {}
  };
};

// 全局辅助函数
global.sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

// 在所有测试运行前执行
beforeAll(async () => {
  console.log('开始执行测试...');
});

// 在所有测试运行后执行
afterAll(async () => {
  console.log('所有测试执行完成');
  // 清理一些可能的全局资源
  jest.clearAllMocks();
}); 