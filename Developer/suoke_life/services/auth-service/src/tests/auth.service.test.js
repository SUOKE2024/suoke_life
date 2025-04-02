/**
 * 认证服务测试文件
 */
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');

// 导入模拟模块
const mockRedisClient = require('./mocks/redis.mock');
const mockDb = require('./mocks/db.mock');

// 模拟外部模块
jest.mock('../config/redis', () => mockRedisClient);
jest.mock('../config/db', () => mockDb);
jest.mock('bcrypt');
jest.mock('jsonwebtoken');
jest.mock('uuid');

// 导入要测试的服务
const authService = require('../services/auth.service');

describe('AuthService', () => {
  // 在每个测试前重置模拟
  beforeEach(() => {
    jest.clearAllMocks();
    mockRedisClient.clearAll();
    mockDb.resetMocks();
    
    // 设置通用模拟
    bcrypt.hash.mockResolvedValue('hashed-password');
    bcrypt.compare.mockResolvedValue(true);
    jwt.sign.mockReturnValue('mock-token');
    uuidv4.mockReturnValue('mock-uuid');
  });
  
  describe('register', () => {
    it('should register a new user successfully', async () => {
      // 准备测试数据
      const userData = {
        username: 'newuser',
        email: 'newuser@example.com',
        password: 'Password123',
        bio: '新用户'
      };
      
      // 执行测试
      const result = await authService.register(userData);
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result.user).toBeDefined();
      expect(result.user.username).toBe(userData.username);
      expect(result.user.email).toBe(userData.email);
      expect(result.user.password).toBeUndefined(); // 确保密码不会返回
      expect(result.accessToken).toBeDefined();
      expect(result.refreshToken).toBeDefined();
      
      // 验证函数调用
      expect(bcrypt.hash).toHaveBeenCalledWith(userData.password, 10);
      expect(mockDb).toHaveBeenCalledWith('users');
      expect(jwt.sign).toHaveBeenCalledTimes(2);
      expect(mockRedisClient.set).toHaveBeenCalled();
    });
    
    it('should throw an error if username already exists', async () => {
      // 准备测试数据
      const userData = {
        username: 'admin', // 已存在的用户名
        email: 'newadmin@example.com',
        password: 'Password123',
        bio: '管理员'
      };
      
      // 执行测试并验证
      await expect(authService.register(userData)).rejects.toThrow('用户名已存在');
    });
  });
  
  describe('login', () => {
    it('should login a user successfully', async () => {
      // 准备测试数据
      const loginData = {
        username: 'admin',
        password: 'admin123'
      };
      
      // 执行测试
      const result = await authService.login(loginData);
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result.user).toBeDefined();
      expect(result.user.username).toBe(loginData.username);
      expect(result.user.password).toBeUndefined(); // 确保密码不会返回
      expect(result.accessToken).toBeDefined();
      expect(result.refreshToken).toBeDefined();
      
      // 验证函数调用
      expect(mockDb).toHaveBeenCalledWith('users');
      expect(bcrypt.compare).toHaveBeenCalled();
      expect(jwt.sign).toHaveBeenCalledTimes(2);
      expect(mockRedisClient.set).toHaveBeenCalled();
    });
    
    it('should throw an error if username is invalid', async () => {
      // 准备测试数据
      const loginData = {
        username: 'nonexistent',
        password: 'password123'
      };
      
      // 模拟数据库返回空结果
      mockDb.mockImplementationOnce(() => ({
        where: jest.fn().mockReturnThis(),
        orWhere: jest.fn().mockReturnThis(),
        first: jest.fn().mockResolvedValue(null)
      }));
      
      // 执行测试并验证
      await expect(authService.login(loginData)).rejects.toThrow('用户名或密码不正确');
    });
    
    it('should throw an error if password is invalid', async () => {
      // 准备测试数据
      const loginData = {
        username: 'admin',
        password: 'wrongpassword'
      };
      
      // 模拟密码比较失败
      bcrypt.compare.mockResolvedValueOnce(false);
      
      // 执行测试并验证
      await expect(authService.login(loginData)).rejects.toThrow('用户名或密码不正确');
    });
  });
  
  describe('refreshToken', () => {
    it('should refresh tokens successfully', async () => {
      // 准备测试数据
      const refreshToken = 'valid-refresh-token';
      const userId = '1';
      
      // 模拟Redis获取用户ID
      mockRedisClient.get.mockResolvedValue(userId);
      
      // 模拟JWT验证
      jwt.verify.mockImplementation((token, secret, callback) => {
        callback(null, { userId });
      });
      
      // 执行测试
      const result = await authService.refreshToken(refreshToken);
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result.accessToken).toBeDefined();
      expect(result.refreshToken).toBeDefined();
      
      // 验证函数调用
      expect(jwt.verify).toHaveBeenCalled();
      expect(mockRedisClient.get).toHaveBeenCalled();
      expect(jwt.sign).toHaveBeenCalledTimes(2);
      expect(mockRedisClient.del).toHaveBeenCalled();
      expect(mockRedisClient.set).toHaveBeenCalled();
    });
  });
  
  describe('logout', () => {
    it('should logout a user successfully', async () => {
      // 准备测试数据
      const refreshToken = 'valid-refresh-token';
      
      // 执行测试
      await authService.logout(refreshToken);
      
      // 验证函数调用
      expect(mockRedisClient.del).toHaveBeenCalledWith(`refresh_token:${refreshToken}`);
    });
  });
  
  describe('validateToken', () => {
    it('should validate an access token successfully', async () => {
      // 准备测试数据
      const token = 'valid-access-token';
      const decodedToken = { userId: '1' };
      
      // 模拟JWT验证
      jwt.verify.mockImplementation((token, secret, callback) => {
        callback(null, decodedToken);
      });
      
      // 执行测试
      const result = await authService.validateToken(token);
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result).toEqual(decodedToken);
      
      // 验证函数调用
      expect(jwt.verify).toHaveBeenCalled();
    });
    
    it('should throw an error for invalid token', async () => {
      // 准备测试数据
      const token = 'invalid-token';
      
      // 模拟JWT验证错误
      jwt.verify.mockImplementation((token, secret, callback) => {
        callback(new Error('Invalid token'), null);
      });
      
      // 执行测试并验证
      await expect(authService.validateToken(token)).rejects.toThrow('Invalid token');
    });
  });
}); 