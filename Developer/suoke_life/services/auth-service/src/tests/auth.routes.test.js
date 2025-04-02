/**
 * 认证路由测试文件
 */
const express = require('express');
const request = require('supertest');
const { errorHandler, responseHandler } = require('@suoke/shared');

// 模拟认证服务
const mockAuthService = {
  register: jest.fn(),
  login: jest.fn(),
  refreshToken: jest.fn(),
  logout: jest.fn(),
  validateToken: jest.fn()
};

// 模拟外部服务
jest.mock('../services/auth.service', () => mockAuthService);
jest.mock('@suoke/shared', () => {
  return {
    errorHandler: {
      handleError: jest.fn((err, req, res, next) => {
        res.status(500).json({ error: err.message });
      }),
      wrapAsync: (fn) => {
        return async (req, res, next) => {
          try {
            await fn(req, res, next);
          } catch (error) {
            next(error);
          }
        };
      }
    },
    responseHandler: {
      success: jest.fn((res, data) => res.json(data)),
      created: jest.fn((res, data) => res.status(201).json(data)),
      badRequest: jest.fn((res, message) => res.status(400).json({ message })),
      unauthorized: jest.fn((res, message) => res.status(401).json({ message })),
      notFound: jest.fn((res, message) => res.status(404).json({ message }))
    },
    logger: {
      info: jest.fn(),
      error: jest.fn()
    },
    validators: {
      validateRegistration: jest.fn().mockImplementation(() => (req, res, next) => next()),
      validateLogin: jest.fn().mockImplementation(() => (req, res, next) => next())
    }
  };
});

// 导入认证控制器
const authController = require('../controllers/auth.controller');

// 创建测试应用
const app = express();
app.use(express.json());

// 导入认证路由
const authRoutes = require('../routes/auth.routes');
app.use('/api/v1/auth', authRoutes);

// 错误处理中间件
app.use(errorHandler.handleError);

describe('Auth Routes', () => {
  // 每个测试前重置模拟
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  describe('POST /api/v1/auth/register', () => {
    it('should register a new user', async () => {
      // 模拟认证服务响应
      mockAuthService.register.mockResolvedValue({
        user: {
          id: 'mock-id',
          username: 'testuser',
          email: 'test@example.com',
          role: 'user'
        },
        accessToken: 'mock-access-token',
        refreshToken: 'mock-refresh-token'
      });
      
      // 发送请求
      const res = await request(app)
        .post('/api/v1/auth/register')
        .send({
          username: 'testuser',
          email: 'test@example.com',
          password: 'Password123',
          bio: '测试用户'
        });
      
      // 验证响应
      expect(res.status).toBe(201);
      expect(res.body).toHaveProperty('user');
      expect(res.body).toHaveProperty('accessToken');
      expect(res.body).toHaveProperty('refreshToken');
      expect(res.body.user.username).toBe('testuser');
      
      // 验证服务调用
      expect(mockAuthService.register).toHaveBeenCalledWith({
        username: 'testuser',
        email: 'test@example.com',
        password: 'Password123',
        bio: '测试用户'
      });
    });
  });
  
  describe('POST /api/v1/auth/login', () => {
    it('should login a user', async () => {
      // 模拟认证服务响应
      mockAuthService.login.mockResolvedValue({
        user: {
          id: 'mock-id',
          username: 'testuser',
          email: 'test@example.com',
          role: 'user'
        },
        accessToken: 'mock-access-token',
        refreshToken: 'mock-refresh-token'
      });
      
      // 发送请求
      const res = await request(app)
        .post('/api/v1/auth/login')
        .send({
          username: 'testuser',
          password: 'Password123'
        });
      
      // 验证响应
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('user');
      expect(res.body).toHaveProperty('accessToken');
      expect(res.body).toHaveProperty('refreshToken');
      expect(res.body.user.username).toBe('testuser');
      
      // 验证服务调用
      expect(mockAuthService.login).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'Password123'
      });
    });
  });
  
  describe('POST /api/v1/auth/refresh-token', () => {
    it('should refresh tokens', async () => {
      // 模拟认证服务响应
      mockAuthService.refreshToken.mockResolvedValue({
        accessToken: 'new-access-token',
        refreshToken: 'new-refresh-token'
      });
      
      // 发送请求
      const res = await request(app)
        .post('/api/v1/auth/refresh-token')
        .send({
          refreshToken: 'mock-refresh-token'
        });
      
      // 验证响应
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('accessToken');
      expect(res.body).toHaveProperty('refreshToken');
      
      // 验证服务调用
      expect(mockAuthService.refreshToken).toHaveBeenCalledWith('mock-refresh-token');
    });
  });
  
  describe('POST /api/v1/auth/logout', () => {
    it('should logout a user', async () => {
      // 模拟认证服务响应
      mockAuthService.logout.mockResolvedValue(undefined);
      
      // 发送请求
      const res = await request(app)
        .post('/api/v1/auth/logout')
        .send({
          refreshToken: 'mock-refresh-token'
        });
      
      // 验证响应
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('message');
      
      // 验证服务调用
      expect(mockAuthService.logout).toHaveBeenCalledWith('mock-refresh-token');
    });
  });
  
  describe('GET /api/v1/auth/validate-token', () => {
    it('should validate a token', async () => {
      // 模拟认证服务响应
      mockAuthService.validateToken.mockResolvedValue({
        userId: 'mock-id',
        role: 'user'
      });
      
      // 发送请求
      const res = await request(app)
        .get('/api/v1/auth/validate-token')
        .set('Authorization', 'Bearer mock-access-token');
      
      // 验证响应
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('userId');
      expect(res.body).toHaveProperty('role');
      
      // 验证服务调用
      expect(mockAuthService.validateToken).toHaveBeenCalledWith('mock-access-token');
    });
  });
}); 