/**
 * 用户路由测试文件
 */
const express = require('express');
const request = require('supertest');
const { errorHandler, responseHandler } = require('@suoke/shared');

// 模拟用户服务
const mockUserService = {
  getUserById: jest.fn(),
  getUserByUsername: jest.fn(),
  getUserByEmail: jest.fn(),
  updateUser: jest.fn(),
  changePassword: jest.fn(),
  deactivateUser: jest.fn(),
  activateUser: jest.fn()
};

// 模拟身份验证中间件
const mockAuthMiddleware = (req, res, next) => {
  req.user = {
    userId: '1',
    role: 'admin'
  };
  next();
};

// 模拟外部服务
jest.mock('../services/user.service', () => mockUserService);
jest.mock('../middlewares/auth.middleware', () => ({
  verifyToken: jest.fn().mockImplementation(() => mockAuthMiddleware)
}));
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
      validateUpdateUser: jest.fn().mockImplementation(() => (req, res, next) => next()),
      validateChangePassword: jest.fn().mockImplementation(() => (req, res, next) => next())
    }
  };
});

// 创建测试应用
const app = express();
app.use(express.json());

// 导入用户路由
const userRoutes = require('../routes/user.routes');
app.use('/api/v1/users', userRoutes);

// 错误处理中间件
app.use(errorHandler.handleError);

describe('User Routes', () => {
  // 每个测试前重置模拟
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  describe('GET /api/v1/users/:id', () => {
    it('should get a user by ID', async () => {
      // 模拟用户服务响应
      mockUserService.getUserById.mockResolvedValue({
        id: '1',
        username: 'admin',
        email: 'admin@suoke.life',
        role: 'admin',
        bio: '系统管理员',
        is_active: true
      });
      
      // 发送请求
      const res = await request(app)
        .get('/api/v1/users/1')
        .set('Authorization', 'Bearer mock-token');
      
      // 验证响应
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('id', '1');
      expect(res.body).toHaveProperty('username', 'admin');
      expect(res.body).not.toHaveProperty('password');
      
      // 验证服务调用
      expect(mockUserService.getUserById).toHaveBeenCalledWith('1');
    });
    
    it('should return 404 when user is not found', async () => {
      // 模拟用户服务响应
      mockUserService.getUserById.mockResolvedValue(null);
      
      // 发送请求
      const res = await request(app)
        .get('/api/v1/users/999')
        .set('Authorization', 'Bearer mock-token');
      
      // 验证响应
      expect(res.status).toBe(404);
      expect(res.body).toHaveProperty('message');
      
      // 验证服务调用
      expect(mockUserService.getUserById).toHaveBeenCalledWith('999');
    });
  });
  
  describe('PUT /api/v1/users/:id', () => {
    it('should update a user', async () => {
      // 模拟用户服务响应
      mockUserService.updateUser.mockResolvedValue({
        id: '1',
        username: 'admin',
        email: 'admin@suoke.life',
        role: 'admin',
        bio: '更新后的简介',
        is_active: true
      });
      
      // 发送请求
      const res = await request(app)
        .put('/api/v1/users/1')
        .set('Authorization', 'Bearer mock-token')
        .send({
          bio: '更新后的简介'
        });
      
      // 验证响应
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('id', '1');
      expect(res.body).toHaveProperty('bio', '更新后的简介');
      expect(res.body).not.toHaveProperty('password');
      
      // 验证服务调用
      expect(mockUserService.updateUser).toHaveBeenCalledWith('1', {
        bio: '更新后的简介'
      });
    });
  });
  
  describe('PUT /api/v1/users/:id/password', () => {
    it('should change user password', async () => {
      // 模拟用户服务响应
      mockUserService.changePassword.mockResolvedValue({
        success: true
      });
      
      // 发送请求
      const res = await request(app)
        .put('/api/v1/users/1/password')
        .set('Authorization', 'Bearer mock-token')
        .send({
          currentPassword: 'currentPassword123',
          newPassword: 'newPassword123'
        });
      
      // 验证响应
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('success', true);
      
      // 验证服务调用
      expect(mockUserService.changePassword).toHaveBeenCalledWith(
        '1',
        'currentPassword123',
        'newPassword123'
      );
    });
  });
  
  describe('PUT /api/v1/users/:id/deactivate', () => {
    it('should deactivate a user', async () => {
      // 模拟用户服务响应
      mockUserService.deactivateUser.mockResolvedValue({
        success: true
      });
      
      // 发送请求
      const res = await request(app)
        .put('/api/v1/users/1/deactivate')
        .set('Authorization', 'Bearer mock-token');
      
      // 验证响应
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('success', true);
      
      // 验证服务调用
      expect(mockUserService.deactivateUser).toHaveBeenCalledWith('1');
    });
  });
  
  describe('PUT /api/v1/users/:id/activate', () => {
    it('should activate a user', async () => {
      // 模拟用户服务响应
      mockUserService.activateUser.mockResolvedValue({
        success: true
      });
      
      // 发送请求
      const res = await request(app)
        .put('/api/v1/users/1/activate')
        .set('Authorization', 'Bearer mock-token');
      
      // 验证响应
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('success', true);
      
      // 验证服务调用
      expect(mockUserService.activateUser).toHaveBeenCalledWith('1');
    });
  });
}); 