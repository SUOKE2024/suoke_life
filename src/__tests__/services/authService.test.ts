import { Alert } from 'react-native';
import authService from '../../services/authService';

// Mock apiClient
jest.mock('../../services/apiClient', () => ({
  apiClient: {
    post: jest.fn(),
    get: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  },
}));

// Mock authUtils
jest.mock('../../utils/authUtils', () => ({
  storeAuthTokens: jest.fn(),
  clearAuthTokens: jest.fn(),
  getAuthToken: jest.fn(),
  getRefreshToken: jest.fn(),
  getDeviceId: jest.fn().mockResolvedValue('mock-device-id'),
}));

// Mock Alert
jest.mock('react-native', () => ({
  Alert: {
    alert: jest.fn(),
  },
}));

import { apiClient } from '../../services/apiClient';

const mockApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('登录功能', () => {
    it('应该成功登录用户', async () => {
      const mockLoginResponse = {
        user: {
          id: 'user123',
          email: 'test@example.com',
          username: '测试用户',
        },
        accessToken: 'mock-access-token',
        refreshToken: 'mock-refresh-token',
        expiresIn: 3600,
      };

      mockApiClient.post.mockResolvedValue({
        success: true,
        data: mockLoginResponse,
        timestamp: Date.now(),
      });

      const result = await authService.login({
        email: 'test@example.com',
        password: 'password123',
      });

      expect(result).toEqual(mockLoginResponse);
      expect(mockApiClient.post).toHaveBeenCalledWith('/auth/login', {
        email: 'test@example.com',
        password: 'password123',
        deviceId: 'mock-device-id',
      });
    });

    it('应该处理登录失败', async () => {
      mockApiClient.post.mockResolvedValue({
        success: false,
        error: {
          code: 'INVALID_CREDENTIALS',
          message: '用户名或密码错误',
        },
        timestamp: Date.now(),
      });

      await expect(authService.login({
        email: 'test@example.com',
        password: 'wrongpassword',
      })).rejects.toThrow('用户名或密码错误');
    });
  });

  describe('注册功能', () => {
    it('应该成功注册新用户', async () => {
      const mockRegisterResponse = {
        user: {
          id: 'user123',
          email: 'newuser@example.com',
          username: '新用户',
        },
        accessToken: 'mock-access-token',
        refreshToken: 'mock-refresh-token',
        expiresIn: 3600,
      };

      mockApiClient.post.mockResolvedValue({
        success: true,
        data: mockRegisterResponse,
        timestamp: Date.now(),
      });

      const result = await authService.register({
        username: '新用户',
        email: 'newuser@example.com',
        password: 'password123',
      });

      expect(result).toEqual(mockRegisterResponse);
    });
  });

  describe('令牌管理', () => {
    it('应该成功刷新令牌', async () => {
      const mockRefreshResponse = {
        accessToken: 'new-access-token',
        refreshToken: 'new-refresh-token',
        expiresIn: 3600,
      };

      // Mock getRefreshToken
      const { getRefreshToken } = require('../../utils/authUtils');
      getRefreshToken.mockResolvedValue('old-refresh-token');

      mockApiClient.post.mockResolvedValue({
        success: true,
        data: mockRefreshResponse,
        timestamp: Date.now(),
      });

      const result = await authService.refreshAccessToken();

      expect(result).toEqual(mockRefreshResponse);
      expect(mockApiClient.post).toHaveBeenCalledWith('/auth/refresh', {
        refreshToken: 'old-refresh-token',
      });
    });
  });

  describe('用户信息管理', () => {
    it('应该获取当前用户信息', async () => {
      const mockUser = {
        id: 'user123',
        email: 'test@example.com',
        username: '测试用户',
      };

      mockApiClient.get.mockResolvedValue({
        success: true,
        data: mockUser,
        timestamp: Date.now(),
      });

      const result = await authService.getCurrentUser();

      expect(result).toEqual(mockUser);
      expect(mockApiClient.get).toHaveBeenCalledWith('/auth/me');
    });
  });

  describe('密码管理', () => {
    it('应该成功修改密码', async () => {
      mockApiClient.post.mockResolvedValue({
        success: true,
        timestamp: Date.now(),
      });

      await expect(authService.changePassword('oldPassword', 'newPassword')).resolves.not.toThrow();

      expect(mockApiClient.post).toHaveBeenCalledWith('/auth/change-password', {
        oldPassword: 'oldPassword',
        newPassword: 'newPassword',
      });
    });

    it('应该成功重置密码', async () => {
      mockApiClient.post.mockResolvedValue({
        success: true,
        timestamp: Date.now(),
      });

      await expect(authService.resetPassword({
        email: 'test@example.com',
        code: '123456',
        newPassword: 'newPassword',
      })).resolves.not.toThrow();
    });
  });

  describe('登出功能', () => {
    it('应该成功登出用户', async () => {
      mockApiClient.post.mockResolvedValue({
        success: true,
        timestamp: Date.now(),
      });

      await expect(authService.logout()).resolves.not.toThrow();

      expect(mockApiClient.post).toHaveBeenCalledWith('/auth/logout');
    });
  });
}); 