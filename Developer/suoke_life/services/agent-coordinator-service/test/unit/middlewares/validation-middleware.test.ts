import { Request, Response, NextFunction } from 'express';
import { validateCreateSession, validateUpdateSession } from '../../../src/middlewares/validation-middleware';

// 模拟express-validator模块，但实际验证中间件并没有使用它，而是使用了自定义验证逻辑
jest.mock('express-validator', () => ({
  body: jest.fn().mockReturnThis(),
  validationResult: jest.fn(),
  param: jest.fn().mockReturnThis(),
  check: jest.fn().mockReturnThis(),
  isEmpty: jest.fn(),
  notEmpty: jest.fn().mockReturnThis(),
  isString: jest.fn().mockReturnThis(),
  isObject: jest.fn().mockReturnThis(),
  optional: jest.fn().mockReturnThis(),
}));

describe('验证中间件', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let nextFunction: jest.Mock;
  
  beforeEach(() => {
    // 重置模拟
    jest.clearAllMocks();
    
    // 创建模拟请求和响应对象
    mockRequest = {
      body: {},
      params: {}
    };
    
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn().mockReturnThis()
    };
    
    nextFunction = jest.fn();
  });
  
  describe('创建会话验证', () => {
    it('如果请求有效，应调用next', () => {
      // 设置有效的请求体
      mockRequest.body = {
        userId: 'test-user',
        initialPrompt: '你好'
      };
      
      validateCreateSession(mockRequest as Request, mockResponse as Response, nextFunction);
      
      expect(nextFunction).toHaveBeenCalled();
      expect(mockResponse.status).not.toHaveBeenCalled();
    });
    
    it('如果请求无效，应返回400错误', () => {
      // 设置无效的请求体（缺少必填字段）
      mockRequest.body = {};
      
      validateCreateSession(mockRequest as Request, mockResponse as Response, nextFunction);
      
      expect(nextFunction).not.toHaveBeenCalled();
      expect(mockResponse.status).toHaveBeenCalledWith(400);
      expect(mockResponse.json).toHaveBeenCalledWith({
        success: false,
        message: '用户ID不能为空'
      });
    });
  });
  
  describe('更新会话验证', () => {
    it('如果请求有效，应调用next', () => {
      // 设置有效的请求参数和请求体
      mockRequest.params = { sessionId: 'test-session-123' };
      mockRequest.body = { status: 'active' };
      
      validateUpdateSession(mockRequest as Request, mockResponse as Response, nextFunction);
      
      expect(nextFunction).toHaveBeenCalled();
      expect(mockResponse.status).not.toHaveBeenCalled();
    });
    
    it('如果会话ID缺失，应返回400错误', () => {
      // 设置无效的请求（缺少sessionId）
      mockRequest.params = {};
      mockRequest.body = { status: 'active' };
      
      validateUpdateSession(mockRequest as Request, mockResponse as Response, nextFunction);
      
      expect(nextFunction).not.toHaveBeenCalled();
      expect(mockResponse.status).toHaveBeenCalledWith(400);
      expect(mockResponse.json).toHaveBeenCalledWith({
        success: false,
        message: '会话ID不能为空'
      });
    });
    
    it('如果会话状态无效，应返回400错误', () => {
      // 设置无效的会话状态
      mockRequest.params = { sessionId: 'test-session-123' };
      mockRequest.body = { status: 'invalid-status' };
      
      validateUpdateSession(mockRequest as Request, mockResponse as Response, nextFunction);
      
      expect(nextFunction).not.toHaveBeenCalled();
      expect(mockResponse.status).toHaveBeenCalledWith(400);
      expect(mockResponse.json).toHaveBeenCalledWith({
        success: false,
        message: '无效的会话状态'
      });
    });
  });
}); 