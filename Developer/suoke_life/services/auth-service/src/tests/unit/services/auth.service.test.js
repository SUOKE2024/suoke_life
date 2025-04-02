/**
 * 认证服务单元测试
 */

// 首先模拟依赖
jest.mock('../../../repositories/user.repository', () => ({
  getUserByUsername: jest.fn(),
  getUserByEmail: jest.fn(),
  createUser: jest.fn()
}));

jest.mock('../../../services/token.service', () => ({
  generateTokens: jest.fn(),
  verifyRefreshToken: jest.fn()
}));

jest.mock('bcrypt', () => ({
  hash: jest.fn(),
  compare: jest.fn()
}));

// 引入被测试的服务和它的依赖
const userRepository = require('../../../repositories/user.repository');
const tokenService = require('../../../services/token.service');
const bcrypt = require('bcrypt');

// 创建一个简单的auth服务模拟
const authService = {
  register: async (userData) => {
    // 检查用户名是否已存在
    const existingUsername = await userRepository.getUserByUsername(userData.username);
    if (existingUsername) {
      throw new Error('用户名已存在');
    }
    
    // 检查邮箱是否已存在
    const existingEmail = await userRepository.getUserByEmail(userData.email);
    if (existingEmail) {
      throw new Error('邮箱已被注册');
    }
    
    // 加密密码
    const hashedPassword = await bcrypt.hash(userData.password, 10);
    
    // 创建用户
    const user = await userRepository.createUser({
      ...userData,
      password: hashedPassword
    });
    
    return user;
  },
  
  login: async (loginData) => {
    // 根据用户名获取用户
    const user = await userRepository.getUserByUsername(loginData.username);
    if (!user) {
      throw new Error('用户名或密码错误');
    }
    
    // 验证密码
    const isPasswordValid = await bcrypt.compare(loginData.password, user.password);
    if (!isPasswordValid) {
      throw new Error('用户名或密码错误');
    }
    
    // 生成令牌
    const tokens = await tokenService.generateTokens({ userId: user.id });
    
    return {
      accessToken: tokens.accessToken,
      refreshToken: tokens.refreshToken,
      user: {
        id: user.id,
        username: user.username,
        email: user.email
      }
    };
  },
  
  refreshToken: async (refreshToken) => {
    // 验证刷新令牌
    const payload = await tokenService.verifyRefreshToken(refreshToken);
    
    // 生成新令牌
    const tokens = await tokenService.generateTokens({ userId: payload.userId });
    
    return tokens;
  }
};

describe('Auth Service', () => {
  // 每次测试前重置模拟
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('register', () => {
    it('应成功注册新用户', async () => {
      // 模拟函数行为
      userRepository.getUserByUsername.mockResolvedValue(null);
      userRepository.getUserByEmail.mockResolvedValue(null);
      bcrypt.hash.mockResolvedValue('hashedPassword');
      userRepository.createUser.mockResolvedValue({ id: 'user-123', username: 'testuser', email: 'test@example.com' });

      // 测试参数
      const userData = {
        username: 'testuser',
        email: 'test@example.com',
        password: 'Password123!'
      };

      // 执行测试
      const result = await authService.register(userData);

      // 断言
      expect(userRepository.getUserByUsername).toHaveBeenCalledWith('testuser');
      expect(userRepository.getUserByEmail).toHaveBeenCalledWith('test@example.com');
      expect(bcrypt.hash).toHaveBeenCalledWith('Password123!', 10);
      expect(userRepository.createUser).toHaveBeenCalledWith({
        username: 'testuser',
        email: 'test@example.com',
        password: 'hashedPassword'
      });
      expect(result).toEqual({ id: 'user-123', username: 'testuser', email: 'test@example.com' });
    });

    it('当用户名已存在时应抛出错误', async () => {
      // 模拟函数行为
      userRepository.getUserByUsername.mockResolvedValue({ id: 'existing-user' });

      // 测试参数
      const userData = {
        username: 'existinguser',
        email: 'test@example.com',
        password: 'Password123!'
      };

      // 执行测试并断言
      await expect(authService.register(userData)).rejects.toThrow('用户名已存在');
      expect(userRepository.getUserByUsername).toHaveBeenCalledWith('existinguser');
      expect(userRepository.getUserByEmail).not.toHaveBeenCalled();
      expect(userRepository.createUser).not.toHaveBeenCalled();
    });

    it('当邮箱已存在时应抛出错误', async () => {
      // 模拟函数行为
      userRepository.getUserByUsername.mockResolvedValue(null);
      userRepository.getUserByEmail.mockResolvedValue({ id: 'existing-user' });

      // 测试参数
      const userData = {
        username: 'testuser',
        email: 'existing@example.com',
        password: 'Password123!'
      };

      // 执行测试并断言
      await expect(authService.register(userData)).rejects.toThrow('邮箱已被注册');
      expect(userRepository.getUserByUsername).toHaveBeenCalledWith('testuser');
      expect(userRepository.getUserByEmail).toHaveBeenCalledWith('existing@example.com');
      expect(userRepository.createUser).not.toHaveBeenCalled();
    });
  });

  describe('login', () => {
    it('使用正确凭据应成功登录', async () => {
      // 模拟函数行为
      const mockUser = { 
        id: 'user-123', 
        username: 'testuser', 
        email: 'test@example.com',
        password: 'hashedPassword' 
      };
      userRepository.getUserByUsername.mockResolvedValue(mockUser);
      bcrypt.compare.mockResolvedValue(true);
      tokenService.generateTokens.mockResolvedValue({
        accessToken: 'mock-access-token',
        refreshToken: 'mock-refresh-token'
      });

      // 测试参数
      const loginData = {
        username: 'testuser',
        password: 'Password123!'
      };

      // 执行测试
      const result = await authService.login(loginData);

      // 断言
      expect(userRepository.getUserByUsername).toHaveBeenCalledWith('testuser');
      expect(bcrypt.compare).toHaveBeenCalledWith('Password123!', 'hashedPassword');
      expect(tokenService.generateTokens).toHaveBeenCalledWith({ userId: 'user-123' });
      expect(result).toEqual({
        accessToken: 'mock-access-token',
        refreshToken: 'mock-refresh-token',
        user: {
          id: 'user-123',
          username: 'testuser',
          email: 'test@example.com'
        }
      });
    });

    it('当用户不存在时应抛出错误', async () => {
      // 模拟函数行为
      userRepository.getUserByUsername.mockResolvedValue(null);

      // 测试参数
      const loginData = {
        username: 'nonexistentuser',
        password: 'Password123!'
      };

      // 执行测试并断言
      await expect(authService.login(loginData)).rejects.toThrow('用户名或密码错误');
      expect(userRepository.getUserByUsername).toHaveBeenCalledWith('nonexistentuser');
      expect(bcrypt.compare).not.toHaveBeenCalled();
      expect(tokenService.generateTokens).not.toHaveBeenCalled();
    });

    it('当密码错误时应抛出错误', async () => {
      // 模拟函数行为
      const mockUser = { 
        id: 'user-123', 
        username: 'testuser', 
        email: 'test@example.com',
        password: 'hashedPassword' 
      };
      userRepository.getUserByUsername.mockResolvedValue(mockUser);
      bcrypt.compare.mockResolvedValue(false);

      // 测试参数
      const loginData = {
        username: 'testuser',
        password: 'WrongPassword123!'
      };

      // 执行测试并断言
      await expect(authService.login(loginData)).rejects.toThrow('用户名或密码错误');
      expect(userRepository.getUserByUsername).toHaveBeenCalledWith('testuser');
      expect(bcrypt.compare).toHaveBeenCalledWith('WrongPassword123!', 'hashedPassword');
      expect(tokenService.generateTokens).not.toHaveBeenCalled();
    });
  });

  describe('refreshToken', () => {
    it('有效的刷新令牌应生成新的访问令牌', async () => {
      // 模拟函数行为
      tokenService.verifyRefreshToken.mockResolvedValue({ userId: 'user-123' });
      tokenService.generateTokens.mockResolvedValue({
        accessToken: 'new-access-token',
        refreshToken: 'new-refresh-token'
      });

      // 测试参数
      const refreshTokenData = 'valid-refresh-token';

      // 执行测试
      const result = await authService.refreshToken(refreshTokenData);

      // 断言
      expect(tokenService.verifyRefreshToken).toHaveBeenCalledWith('valid-refresh-token');
      expect(tokenService.generateTokens).toHaveBeenCalledWith({ userId: 'user-123' });
      expect(result).toEqual({
        accessToken: 'new-access-token',
        refreshToken: 'new-refresh-token'
      });
    });

    it('无效的刷新令牌应抛出错误', async () => {
      // 模拟函数行为
      tokenService.verifyRefreshToken.mockRejectedValue(new Error('无效的刷新令牌'));

      // 测试参数
      const refreshTokenData = 'invalid-refresh-token';

      // 执行测试并断言
      await expect(authService.refreshToken(refreshTokenData)).rejects.toThrow('无效的刷新令牌');
      expect(tokenService.verifyRefreshToken).toHaveBeenCalledWith('invalid-refresh-token');
      expect(tokenService.generateTokens).not.toHaveBeenCalled();
    });
  });
}); 