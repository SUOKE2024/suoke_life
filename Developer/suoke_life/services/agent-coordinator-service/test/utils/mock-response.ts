import { Response } from 'express';
import { jest } from '@jest/globals';

/**
 * 创建一个类型安全的模拟Express Response对象
 * 用于测试控制器
 */
export function createMockResponse() {
  const mockResponse = {
    status: jest.fn().mockReturnThis(),
    json: jest.fn().mockReturnThis(),
    send: jest.fn().mockReturnThis(),
    sendStatus: jest.fn().mockReturnThis(),
    end: jest.fn().mockReturnThis(),
    set: jest.fn().mockReturnThis(),
    type: jest.fn().mockReturnThis(),
    cookie: jest.fn().mockReturnThis(),
    clearCookie: jest.fn().mockReturnThis(),
    attachment: jest.fn().mockReturnThis(),
    download: jest.fn().mockReturnThis(),
    format: jest.fn().mockReturnThis(),
    links: jest.fn().mockReturnThis(),
    locals: {},
    headersSent: false,
    app: { locals: {} } as any,
    req: {} as any,
    charset: '',
    get: jest.fn(),
    header: jest.fn(),
    redirect: jest.fn().mockReturnThis(),
    render: jest.fn().mockReturnThis(),
    vary: jest.fn().mockReturnThis(),
    append: jest.fn().mockReturnThis(),
    write: jest.fn().mockReturnThis(),
    setHeader: jest.fn().mockReturnThis(),
    getHeader: jest.fn().mockReturnThis(),
    location: jest.fn().mockReturnThis(),
    contentType: jest.fn().mockReturnThis(),
  };
  
  return mockResponse;
}

/**
 * 用于测试的类型安全辅助函数
 * 将createMockResponse的结果转换为Response类型
 */
export function mockResponseAsResponse(mockResponse: ReturnType<typeof createMockResponse>): Response {
  return mockResponse as unknown as Response;
} 