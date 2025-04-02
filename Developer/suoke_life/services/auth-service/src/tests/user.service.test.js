/**
 * 用户服务测试文件
 */
const bcrypt = require('bcrypt');
const { v4: uuidv4 } = require('uuid');

// 导入模拟模块
const mockDb = require('./mocks/db.mock');

// 模拟外部模块
jest.mock('../config/db', () => mockDb);
jest.mock('bcrypt');
jest.mock('uuid');

// 导入要测试的服务
const userService = require('../services/user.service');

describe('UserService', () => {
  // 在每个测试前重置模拟
  beforeEach(() => {
    jest.clearAllMocks();
    mockDb.resetMocks();
    
    // 设置通用模拟
    bcrypt.hash.mockResolvedValue('hashed-password');
    bcrypt.compare.mockResolvedValue(true);
    uuidv4.mockReturnValue('mock-uuid');
  });
  
  describe('getUserById', () => {
    it('should get a user by ID successfully', async () => {
      // 准备测试数据
      const userId = '1';
      
      // 执行测试
      const result = await userService.getUserById(userId);
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result.id).toBe(userId);
      expect(result.username).toBe('admin');
      expect(result.email).toBe('admin@suoke.life');
      expect(result.password).toBeUndefined(); // 确保密码不会返回
      
      // 验证函数调用
      expect(mockDb).toHaveBeenCalledWith('users');
    });
    
    it('should return null when user is not found', async () => {
      // 准备测试数据
      const userId = 'nonexistent';
      
      // 模拟数据库返回空结果
      mockDb.mockImplementationOnce(() => ({
        where: jest.fn().mockReturnThis(),
        first: jest.fn().mockResolvedValue(null)
      }));
      
      // 执行测试
      const result = await userService.getUserById(userId);
      
      // 验证结果
      expect(result).toBeNull();
      
      // 验证函数调用
      expect(mockDb).toHaveBeenCalledWith('users');
    });
  });
  
  describe('getUserByUsername', () => {
    it('should get a user by username successfully', async () => {
      // 准备测试数据
      const username = 'admin';
      
      // 执行测试
      const result = await userService.getUserByUsername(username);
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result.username).toBe(username);
      expect(result.email).toBe('admin@suoke.life');
      expect(result.password).toBeUndefined(); // 确保密码不会返回
      
      // 验证函数调用
      expect(mockDb).toHaveBeenCalledWith('users');
    });
  });
  
  describe('getUserByEmail', () => {
    it('should get a user by email successfully', async () => {
      // 准备测试数据
      const email = 'admin@suoke.life';
      
      // 执行测试
      const result = await userService.getUserByEmail(email);
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result.email).toBe(email);
      expect(result.username).toBe('admin');
      expect(result.password).toBeUndefined(); // 确保密码不会返回
      
      // 验证函数调用
      expect(mockDb).toHaveBeenCalledWith('users');
    });
  });
  
  describe('updateUser', () => {
    it('should update a user successfully', async () => {
      // 准备测试数据
      const userId = '1';
      const userData = {
        bio: '更新后的简介',
        is_active: true
      };
      
      // 执行测试
      const result = await userService.updateUser(userId, userData);
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result.id).toBe(userId);
      expect(result.bio).toBe(userData.bio);
      expect(result.is_active).toBe(userData.is_active);
      expect(result.password).toBeUndefined(); // 确保密码不会返回
      
      // 验证函数调用
      expect(mockDb).toHaveBeenCalledWith('users');
    });
    
    it('should throw an error when user is not found', async () => {
      // 准备测试数据
      const userId = 'nonexistent';
      const userData = {
        bio: '更新后的简介'
      };
      
      // 模拟数据库返回空结果
      mockDb.mockImplementationOnce(() => ({
        where: jest.fn().mockReturnThis(),
        first: jest.fn().mockResolvedValue(null)
      }));
      
      // 执行测试并验证
      await expect(userService.updateUser(userId, userData)).rejects.toThrow('用户不存在');
      
      // 验证函数调用
      expect(mockDb).toHaveBeenCalledWith('users');
    });
  });
  
  describe('changePassword', () => {
    it('should change password successfully', async () => {
      // 准备测试数据
      const userId = '1';
      const currentPassword = 'admin123';
      const newPassword = 'newPassword123';
      
      // 执行测试
      const result = await userService.changePassword(userId, currentPassword, newPassword);
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      
      // 验证函数调用
      expect(mockDb).toHaveBeenCalledWith('users');
      expect(bcrypt.compare).toHaveBeenCalled();
      expect(bcrypt.hash).toHaveBeenCalledWith(newPassword, 10);
    });
    
    it('should throw an error when current password is invalid', async () => {
      // 准备测试数据
      const userId = '1';
      const currentPassword = 'wrongPassword';
      const newPassword = 'newPassword123';
      
      // 模拟密码比较失败
      bcrypt.compare.mockResolvedValueOnce(false);
      
      // 执行测试并验证
      await expect(userService.changePassword(userId, currentPassword, newPassword)).rejects.toThrow('当前密码不正确');
      
      // 验证函数调用
      expect(mockDb).toHaveBeenCalledWith('users');
      expect(bcrypt.compare).toHaveBeenCalled();
    });
  });
  
  describe('deactivateUser', () => {
    it('should deactivate a user successfully', async () => {
      // 准备测试数据
      const userId = '1';
      
      // 执行测试
      const result = await userService.deactivateUser(userId);
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      
      // 验证函数调用
      expect(mockDb).toHaveBeenCalledWith('users');
    });
  });
  
  describe('activateUser', () => {
    it('should activate a user successfully', async () => {
      // 准备测试数据
      const userId = '1';
      
      // 执行测试
      const result = await userService.activateUser(userId);
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      
      // 验证函数调用
      expect(mockDb).toHaveBeenCalledWith('users');
    });
  });
}); 