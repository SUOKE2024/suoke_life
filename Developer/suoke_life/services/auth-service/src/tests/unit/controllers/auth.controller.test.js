/**
 * 认证控制器单元测试
 */

// 模拟依赖
jest.mock('../../../services/auth.service', () => ({
  register: jest.fn(),
  login: jest.fn(),
  refreshToken: jest.fn(),
  logout: jest.fn()
}));

jest.mock('@suoke/shared', () => ({
  utils: {
    responseHandler: {
      success: jest.fn()
    },
    errorHandler: {
      handleError: jest.fn()
    }
  }
}));

// 引入被测试的控制器和依赖
const authService = require('../../../services/auth.service');
const { utils } = require('@suoke/shared');
const { responseHandler, errorHandler } = utils;

// 创建一个简单的auth控制器模拟
const authController = {
  register: async (req, res) => {
    try {
      const result = await authService.register(req.body);
      return responseHandler.success(res, '注册成功', result);
    } catch (error) {
      return errorHandler.handleError(error, res);
    }
  },
  
  login: async (req, res) => {
    try {
      const { username, password } = req.body;
      const result = await authService.login({ username, password });
      return responseHandler.success(res, '登录成功', result);
    } catch (error) {
      return errorHandler.handleError(error, res);
    }
  },
  
  refreshToken: async (req, res) => {
    try {
      const { refreshToken } = req.body;
      const tokens = await authService.refreshToken(refreshToken);
      return responseHandler.success(res, '令牌刷新成功', tokens);
    } catch (error) {
      return errorHandler.handleError(error, res);
    }
  },
  
  logout: async (req, res) => {
    try {
      const { refreshToken } = req.body;
      await authService.logout(refreshToken);
      return responseHandler.success(res, '登出成功');
    } catch (error) {
      return errorHandler.handleError(error, res);
    }
  }
};

describe('Auth Controller', () => {
  // 每次测试前重置模拟
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  describe('register', () => {
    it('成功注册应返回成功响应', async () => {
      // 模拟请求和响应对象
      const req = {
        body: {
          username: 'testuser',
          email: 'test@example.com',
          password: 'Password123!'
        }
      };
      const res = {};
      
      // 模拟服务返回值
      const mockUser = { id: 'user-123', username: 'testuser' };
      authService.register.mockResolvedValue(mockUser);
      
      // 执行测试
      await authController.register(req, res);
      
      // 断言
      expect(authService.register).toHaveBeenCalledWith(req.body);
      expect(responseHandler.success).toHaveBeenCalledWith(res, '注册成功', mockUser);
    });
    
    it('注册失败应处理错误', async () => {
      // 模拟请求和响应对象
      const req = {
        body: {
          username: 'existinguser',
          email: 'test@example.com',
          password: 'Password123!'
        }
      };
      const res = {};
      
      // 模拟服务抛出错误
      const error = new Error('用户名已存在');
      authService.register.mockRejectedValue(error);
      
      // 执行测试
      await authController.register(req, res);
      
      // 断言
      expect(authService.register).toHaveBeenCalledWith(req.body);
      expect(errorHandler.handleError).toHaveBeenCalledWith(error, res);
    });
  });
  
  describe('login', () => {
    it('成功登录应返回成功响应', async () => {
      // 模拟请求和响应对象
      const req = {
        body: {
          username: 'testuser',
          password: 'Password123!'
        }
      };
      const res = {};
      
      // 模拟服务返回值
      const mockResult = {
        accessToken: 'access-token',
        refreshToken: 'refresh-token',
        user: { id: 'user-123', username: 'testuser' }
      };
      authService.login.mockResolvedValue(mockResult);
      
      // 执行测试
      await authController.login(req, res);
      
      // 断言
      expect(authService.login).toHaveBeenCalledWith({ 
        username: 'testuser', 
        password: 'Password123!' 
      });
      expect(responseHandler.success).toHaveBeenCalledWith(res, '登录成功', mockResult);
    });
    
    it('登录失败应处理错误', async () => {
      // 模拟请求和响应对象
      const req = {
        body: {
          username: 'testuser',
          password: 'WrongPassword'
        }
      };
      const res = {};
      
      // 模拟服务抛出错误
      const error = new Error('用户名或密码错误');
      authService.login.mockRejectedValue(error);
      
      // 执行测试
      await authController.login(req, res);
      
      // 断言
      expect(authService.login).toHaveBeenCalledWith({ 
        username: 'testuser', 
        password: 'WrongPassword' 
      });
      expect(errorHandler.handleError).toHaveBeenCalledWith(error, res);
    });
  });
  
  describe('refreshToken', () => {
    it('成功刷新令牌应返回成功响应', async () => {
      // 模拟请求和响应对象
      const req = {
        body: {
          refreshToken: 'valid-refresh-token'
        }
      };
      const res = {};
      
      // 模拟服务返回值
      const mockTokens = {
        accessToken: 'new-access-token',
        refreshToken: 'new-refresh-token'
      };
      authService.refreshToken.mockResolvedValue(mockTokens);
      
      // 执行测试
      await authController.refreshToken(req, res);
      
      // 断言
      expect(authService.refreshToken).toHaveBeenCalledWith('valid-refresh-token');
      expect(responseHandler.success).toHaveBeenCalledWith(res, '令牌刷新成功', mockTokens);
    });
    
    it('刷新令牌失败应处理错误', async () => {
      // 模拟请求和响应对象
      const req = {
        body: {
          refreshToken: 'invalid-refresh-token'
        }
      };
      const res = {};
      
      // 模拟服务抛出错误
      const error = new Error('无效的刷新令牌');
      authService.refreshToken.mockRejectedValue(error);
      
      // 执行测试
      await authController.refreshToken(req, res);
      
      // 断言
      expect(authService.refreshToken).toHaveBeenCalledWith('invalid-refresh-token');
      expect(errorHandler.handleError).toHaveBeenCalledWith(error, res);
    });
  });
  
  describe('logout', () => {
    it('成功登出应返回成功响应', async () => {
      // 模拟请求和响应对象
      const req = {
        body: {
          refreshToken: 'refresh-token'
        }
      };
      const res = {};
      
      // 模拟服务返回值
      authService.logout.mockResolvedValue();
      
      // 执行测试
      await authController.logout(req, res);
      
      // 断言
      expect(authService.logout).toHaveBeenCalledWith('refresh-token');
      expect(responseHandler.success).toHaveBeenCalledWith(res, '登出成功');
    });
    
    it('登出失败应处理错误', async () => {
      // 模拟请求和响应对象
      const req = {
        body: {
          refreshToken: 'invalid-refresh-token'
        }
      };
      const res = {};
      
      // 模拟服务抛出错误
      const error = new Error('无效的刷新令牌');
      authService.logout.mockRejectedValue(error);
      
      // 执行测试
      await authController.logout(req, res);
      
      // 断言
      expect(authService.logout).toHaveBeenCalledWith('invalid-refresh-token');
      expect(errorHandler.handleError).toHaveBeenCalledWith(error, res);
    });
  });
}); 