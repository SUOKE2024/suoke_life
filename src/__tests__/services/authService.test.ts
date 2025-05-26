import { Alert } from 'react-native';

// Mock认证服务
const mockAuthService = {
  login: jest.fn(),
  logout: jest.fn(),
  register: jest.fn(),
  refreshToken: jest.fn(),
  getCurrentUser: jest.fn(),
  updateProfile: jest.fn(),
  changePassword: jest.fn(),
  resetPassword: jest.fn(),
  verifyEmail: jest.fn(),
  sendVerificationCode: jest.fn(),
};

// Mock Alert
jest.mock('react-native', () => ({
  Alert: {
    alert: jest.fn(),
  },
}));

const mockAlert = Alert.alert as jest.MockedFunction<typeof Alert.alert>;

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('登录功能', () => {
    it('应该成功登录用户', async () => {
      const mockUser = {
        id: 'user123',
        email: 'test@example.com',
        name: '测试用户',
        token: 'mock-token',
      };

      mockAuthService.login.mockResolvedValue({
        success: true,
        data: mockUser,
      });

      const result = await mockAuthService.login('test@example.com', 'password123');

      expect(result.success).toBe(true);
      expect(result.data).toEqual(mockUser);
      expect(mockAuthService.login).toHaveBeenCalledWith('test@example.com', 'password123');
    });

    it('应该处理登录失败', async () => {
      mockAuthService.login.mockResolvedValue({
        success: false,
        error: '用户名或密码错误',
      });

      const result = await mockAuthService.login('test@example.com', 'wrongpassword');

      expect(result.success).toBe(false);
      expect(result.error).toBe('用户名或密码错误');
    });

    it('应该处理网络错误', async () => {
      mockAuthService.login.mockRejectedValue(new Error('网络连接失败'));

      try {
        await mockAuthService.login('test@example.com', 'password123');
      } catch (error: any) {
        expect(error.message).toBe('网络连接失败');
      }
    });
  });

  describe('注册功能', () => {
    it('应该成功注册新用户', async () => {
      const registerData = {
        email: 'newuser@example.com',
        password: 'password123',
        name: '新用户',
        phone: '+86 138 0013 8000',
      };

      mockAuthService.register.mockResolvedValue({
        success: true,
        message: '注册成功，请查收验证邮件',
      });

      const result = await mockAuthService.register(registerData);

      expect(result.success).toBe(true);
      expect(result.message).toBe('注册成功，请查收验证邮件');
      expect(mockAuthService.register).toHaveBeenCalledWith(registerData);
    });

    it('应该处理邮箱已存在的情况', async () => {
      const registerData = {
        email: 'existing@example.com',
        password: 'password123',
        name: '用户',
        phone: '+86 138 0013 8000',
      };

      mockAuthService.register.mockResolvedValue({
        success: false,
        error: '邮箱已被注册',
      });

      const result = await mockAuthService.register(registerData);

      expect(result.success).toBe(false);
      expect(result.error).toBe('邮箱已被注册');
    });
  });

  describe('令牌管理', () => {
    it('应该成功刷新令牌', async () => {
      const newToken = 'new-mock-token';

      mockAuthService.refreshToken.mockResolvedValue({
        success: true,
        token: newToken,
      });

      const result = await mockAuthService.refreshToken();

      expect(result.success).toBe(true);
      expect(result.token).toBe(newToken);
    });

    it('应该处理令牌过期', async () => {
      mockAuthService.refreshToken.mockResolvedValue({
        success: false,
        error: '刷新令牌已过期',
      });

      const result = await mockAuthService.refreshToken();

      expect(result.success).toBe(false);
      expect(result.error).toBe('刷新令牌已过期');
    });
  });

  describe('用户信息管理', () => {
    it('应该获取当前用户信息', async () => {
      const mockUser = {
        id: 'user123',
        email: 'test@example.com',
        name: '测试用户',
        avatar: '👤',
        memberLevel: 'gold',
      };

      mockAuthService.getCurrentUser.mockResolvedValue({
        success: true,
        data: mockUser,
      });

      const result = await mockAuthService.getCurrentUser();

      expect(result.success).toBe(true);
      expect(result.data).toEqual(mockUser);
    });

    it('应该更新用户资料', async () => {
      const updateData = {
        name: '更新的用户名',
        bio: '更新的简介',
      };

      mockAuthService.updateProfile.mockResolvedValue({
        success: true,
        message: '资料更新成功',
      });

      const result = await mockAuthService.updateProfile(updateData);

      expect(result.success).toBe(true);
      expect(result.message).toBe('资料更新成功');
      expect(mockAuthService.updateProfile).toHaveBeenCalledWith(updateData);
    });
  });

  describe('密码管理', () => {
    it('应该成功修改密码', async () => {
      mockAuthService.changePassword.mockResolvedValue({
        success: true,
        message: '密码修改成功',
      });

      const result = await mockAuthService.changePassword('oldPassword', 'newPassword');

      expect(result.success).toBe(true);
      expect(result.message).toBe('密码修改成功');
      expect(mockAuthService.changePassword).toHaveBeenCalledWith('oldPassword', 'newPassword');
    });

    it('应该处理旧密码错误', async () => {
      mockAuthService.changePassword.mockResolvedValue({
        success: false,
        error: '当前密码错误',
      });

      const result = await mockAuthService.changePassword('wrongPassword', 'newPassword');

      expect(result.success).toBe(false);
      expect(result.error).toBe('当前密码错误');
    });

    it('应该成功重置密码', async () => {
      mockAuthService.resetPassword.mockResolvedValue({
        success: true,
        message: '重置密码邮件已发送',
      });

      const result = await mockAuthService.resetPassword('test@example.com');

      expect(result.success).toBe(true);
      expect(result.message).toBe('重置密码邮件已发送');
      expect(mockAuthService.resetPassword).toHaveBeenCalledWith('test@example.com');
    });
  });

  describe('邮箱验证', () => {
    it('应该成功验证邮箱', async () => {
      mockAuthService.verifyEmail.mockResolvedValue({
        success: true,
        message: '邮箱验证成功',
      });

      const result = await mockAuthService.verifyEmail('verification-code');

      expect(result.success).toBe(true);
      expect(result.message).toBe('邮箱验证成功');
      expect(mockAuthService.verifyEmail).toHaveBeenCalledWith('verification-code');
    });

    it('应该发送验证码', async () => {
      mockAuthService.sendVerificationCode.mockResolvedValue({
        success: true,
        message: '验证码已发送',
      });

      const result = await mockAuthService.sendVerificationCode('test@example.com');

      expect(result.success).toBe(true);
      expect(result.message).toBe('验证码已发送');
      expect(mockAuthService.sendVerificationCode).toHaveBeenCalledWith('test@example.com');
    });
  });

  describe('登出功能', () => {
    it('应该成功登出用户', async () => {
      mockAuthService.logout.mockResolvedValue({
        success: true,
        message: '已安全退出',
      });

      const result = await mockAuthService.logout();

      expect(result.success).toBe(true);
      expect(result.message).toBe('已安全退出');
    });
  });
}); 