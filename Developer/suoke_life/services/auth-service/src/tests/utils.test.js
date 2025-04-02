/**
 * 工具函数测试文件
 */
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const { 
  generateAccessToken, 
  generateRefreshToken, 
  validateEmail, 
  validatePassword,
  sanitizeUser
} = require('../utils/auth.utils');

// 模拟环境变量和外部模块
jest.mock('bcrypt');
jest.mock('jsonwebtoken');
jest.mock('uuid');

describe('Auth Utils', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // 设置测试环境变量
    process.env.JWT_SECRET = 'test-jwt-secret';
    process.env.JWT_REFRESH_SECRET = 'test-jwt-refresh-secret';
    process.env.JWT_EXPIRES_IN = '1h';
    process.env.JWT_REFRESH_EXPIRES_IN = '7d';
    
    // 设置通用模拟
    jwt.sign.mockReturnValue('mock-token');
    uuidv4.mockReturnValue('mock-uuid');
  });
  
  describe('generateAccessToken', () => {
    it('should generate an access token', () => {
      // 执行测试
      const token = generateAccessToken('1', 'admin');
      
      // 验证结果
      expect(token).toBe('mock-token');
      
      // 验证函数调用
      expect(jwt.sign).toHaveBeenCalledWith(
        { userId: '1', role: 'admin' },
        'test-jwt-secret',
        { expiresIn: '1h' }
      );
    });
  });
  
  describe('generateRefreshToken', () => {
    it('should generate a refresh token', () => {
      // 执行测试
      const token = generateRefreshToken('1');
      
      // 验证结果
      expect(token).toBe('mock-token');
      
      // 验证函数调用
      expect(jwt.sign).toHaveBeenCalledWith(
        { userId: '1' },
        'test-jwt-refresh-secret',
        { expiresIn: '7d' }
      );
    });
  });
  
  describe('validateEmail', () => {
    it('should validate a correct email format', () => {
      // 执行测试
      const result = validateEmail('test@example.com');
      
      // 验证结果
      expect(result).toBe(true);
    });
    
    it('should reject an incorrect email format', () => {
      // 执行测试
      const result = validateEmail('invalid-email');
      
      // 验证结果
      expect(result).toBe(false);
    });
  });
  
  describe('validatePassword', () => {
    it('should validate a strong password', () => {
      // 执行测试
      const result = validatePassword('StrongPassword123');
      
      // 验证结果
      expect(result).toBe(true);
    });
    
    it('should reject a short password', () => {
      // 执行测试
      const result = validatePassword('short');
      
      // 验证结果
      expect(result).toBe(false);
    });
    
    it('should reject a password without numbers', () => {
      // 执行测试
      const result = validatePassword('OnlyLetters');
      
      // 验证结果
      expect(result).toBe(false);
    });
    
    it('should reject a password without uppercase letters', () => {
      // 执行测试
      const result = validatePassword('onlylowercase123');
      
      // 验证结果
      expect(result).toBe(false);
    });
  });
  
  describe('sanitizeUser', () => {
    it('should remove sensitive fields from user object', () => {
      // 准备测试数据
      const user = {
        id: '1',
        username: 'testuser',
        email: 'test@example.com',
        password: 'hashed_password',
        role: 'user',
        created_at: new Date(),
        updated_at: new Date()
      };
      
      // 执行测试
      const sanitized = sanitizeUser(user);
      
      // 验证结果
      expect(sanitized).toHaveProperty('id');
      expect(sanitized).toHaveProperty('username');
      expect(sanitized).toHaveProperty('email');
      expect(sanitized).toHaveProperty('role');
      expect(sanitized).not.toHaveProperty('password');
    });
    
    it('should handle null or undefined input', () => {
      // 执行测试
      const sanitizedNull = sanitizeUser(null);
      const sanitizedUndefined = sanitizeUser(undefined);
      
      // 验证结果
      expect(sanitizedNull).toBeNull();
      expect(sanitizedUndefined).toBeUndefined();
    });
  });
}); 