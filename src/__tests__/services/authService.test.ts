import { Alert } from 'react-native';
import authService from '../../services/authService';
import { LoginRequest, RegisterRequest, ForgotPasswordRequest } from '../../services/authService';

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

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
}));

// Mock axios
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    post: jest.fn(),
    get: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() },
    },
  })),
}));

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

  describe('login', () => {
    it('should login successfully with valid credentials', async () => {
      const mockResponse = {
        success: true,
        data: {
          user: {
            id: '1',
            email: 'test@example.com',
            username: 'testuser',
          },
          accessToken: 'mock-access-token',
          refreshToken: 'mock-refresh-token',
          expiresIn: 3600,
        },
      };

      const { apiClient } = require('../../services/apiClient');
      apiClient.post.mockResolvedValue(mockResponse);

      const credentials: LoginRequest = {
        email: 'test@example.com',
        password: 'password',
      };

      const result = await authService.login(credentials);

      expect(apiClient.post).toHaveBeenCalledWith('/auth/login', {
        ...credentials,
        deviceId: 'mock-device-id',
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('should throw error for invalid credentials', async () => {
      const mockResponse = {
        success: false,
        error: { message: 'Invalid credentials' },
      };

      const { apiClient } = require('../../services/apiClient');
      apiClient.post.mockResolvedValue(mockResponse);

      const credentials: LoginRequest = {
        email: 'invalid@example.com',
        password: 'wrongpassword',
      };

      await expect(authService.login(credentials)).rejects.toThrow('Invalid credentials');
    });

    it('should handle network errors', async () => {
      const { apiClient } = require('../../services/apiClient');
      apiClient.post.mockRejectedValue(new Error('Network Error'));

      const credentials: LoginRequest = {
        email: 'test@example.com',
        password: 'password',
      };

      await expect(authService.login(credentials)).rejects.toThrow('Network Error');
    });
  });

  describe('register', () => {
    it('should register successfully with valid data', async () => {
      const mockResponse = {
        success: true,
        data: {
          user: {
            id: '1',
            email: 'newuser@example.com',
            username: 'newuser',
          },
          accessToken: 'mock-access-token',
          refreshToken: 'mock-refresh-token',
          expiresIn: 3600,
        },
      };

      const { apiClient } = require('../../services/apiClient');
      apiClient.post.mockResolvedValue(mockResponse);

      const userData: RegisterRequest = {
        username: 'newuser',
        email: 'newuser@example.com',
        password: 'password123',
      };

      const result = await authService.register(userData);

      expect(apiClient.post).toHaveBeenCalledWith('/auth/register', {
        ...userData,
        deviceId: 'mock-device-id',
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('should throw error for duplicate email', async () => {
      const mockResponse = {
        success: false,
        error: { message: 'Email already exists' },
      };

      const { apiClient } = require('../../services/apiClient');
      apiClient.post.mockResolvedValue(mockResponse);

      const userData: RegisterRequest = {
        username: 'existinguser',
        email: 'existing@example.com',
        password: 'password123',
      };

      await expect(authService.register(userData)).rejects.toThrow('Email already exists');
    });
  });

  describe('logout', () => {
    it('should logout successfully', async () => {
      const { apiClient } = require('../../services/apiClient');
      apiClient.post.mockResolvedValue({ success: true });

      await authService.logout();

      expect(apiClient.post).toHaveBeenCalledWith('/auth/logout');
    });

    it('should clear local tokens even if server logout fails', async () => {
      const { apiClient } = require('../../services/apiClient');
      const { clearAuthTokens } = require('../../utils/authUtils');
      
      apiClient.post.mockRejectedValue(new Error('Server error'));

      await authService.logout();

      expect(clearAuthTokens).toHaveBeenCalled();
    });
  });

  describe('getCurrentUser', () => {
    it('should return current user data', async () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        username: 'testuser',
      };

      const mockResponse = {
        success: true,
        data: mockUser,
      };

      const { apiClient } = require('../../services/apiClient');
      apiClient.get.mockResolvedValue(mockResponse);

      const result = await authService.getCurrentUser();

      expect(apiClient.get).toHaveBeenCalledWith('/auth/me');
      expect(result).toEqual(mockUser);
    });

    it('should handle unauthorized access', async () => {
      const mockResponse = {
        success: false,
        error: { message: 'Unauthorized' },
      };

      const { apiClient } = require('../../services/apiClient');
      apiClient.get.mockResolvedValue(mockResponse);

      await expect(authService.getCurrentUser()).rejects.toThrow('Unauthorized');
    });
  });

  describe('refreshAccessToken', () => {
    it('should refresh token successfully', async () => {
      const mockResponse = {
        success: true,
        data: {
          accessToken: 'new-access-token',
          refreshToken: 'new-refresh-token',
          expiresIn: 3600,
        },
      };

      const { apiClient } = require('../../services/apiClient');
      const { getRefreshToken } = require('../../utils/authUtils');
      
      getRefreshToken.mockResolvedValue('old-refresh-token');
      apiClient.post.mockResolvedValue(mockResponse);

      const result = await authService.refreshAccessToken();

      expect(apiClient.post).toHaveBeenCalledWith('/auth/refresh', {
        refreshToken: 'old-refresh-token',
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle missing refresh token', async () => {
      const { getRefreshToken } = require('../../utils/authUtils');
      getRefreshToken.mockResolvedValue(null);

      await expect(authService.refreshAccessToken()).rejects.toThrow('No refresh token available');
    });
  });

  describe('forgotPassword', () => {
    it('should send password reset email', async () => {
      const mockResponse = { success: true };
      const { apiClient } = require('../../services/apiClient');
      apiClient.post.mockResolvedValue(mockResponse);

      const request: ForgotPasswordRequest = {
        email: 'test@example.com',
      };

      await authService.forgotPassword(request);

      expect(apiClient.post).toHaveBeenCalledWith('/auth/forgot-password', request);
    });

    it('should handle non-existent email', async () => {
      const mockResponse = {
        success: false,
        error: { message: 'Email not found' },
      };

      const { apiClient } = require('../../services/apiClient');
      apiClient.post.mockResolvedValue(mockResponse);

      const request: ForgotPasswordRequest = {
        email: 'nonexistent@example.com',
      };

      await expect(authService.forgotPassword(request)).rejects.toThrow('Email not found');
    });
  });

  describe('resetPassword', () => {
    it('should reset password successfully', async () => {
      const mockResponse = { data: { message: 'Password reset successful' } };
      const mockPost = jest.fn().mockResolvedValue(mockResponse);
      (authService as any).api.post = mockPost;

      const result = await authService.resetPassword(
        'reset-token',
        'newpassword123'
      );

      expect(mockPost).toHaveBeenCalledWith('/auth/reset-password', {
        token: 'reset-token',
        password: 'newpassword123',
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle invalid reset token', async () => {
      const mockError = new Error('Invalid or expired token');
      const mockPost = jest.fn().mockRejectedValue(mockError);
      (authService as any).api.post = mockPost;

      await expect(
        authService.resetPassword('invalid-token', 'newpassword123')
      ).rejects.toThrow('Invalid or expired token');
    });
  });

  describe('validateToken', () => {
    it('should validate token successfully', async () => {
      const mockResponse = { data: { valid: true } };
      const mockPost = jest.fn().mockResolvedValue(mockResponse);
      (authService as any).api.post = mockPost;

      const result = await authService.validateToken('valid-token');

      expect(mockPost).toHaveBeenCalledWith('/auth/validate', {
        token: 'valid-token',
      });
      expect(result).toBe(true);
    });

    it('should return false for invalid token', async () => {
      const mockError = new Error('Invalid token');
      const mockPost = jest.fn().mockRejectedValue(mockError);
      (authService as any).api.post = mockPost;

      const result = await authService.validateToken('invalid-token');

      expect(result).toBe(false);
    });
  });

  describe('updateProfile', () => {
    it('should update user profile successfully', async () => {
      const mockResponse = {
        data: {
          id: '1',
          email: 'test@example.com',
          name: 'Updated Name',
          avatar: 'new-avatar-url',
        },
      };

      const mockPut = jest.fn().mockResolvedValue(mockResponse);
      (authService as any).api.put = mockPut;

      const updateData = {
        name: 'Updated Name',
        avatar: 'new-avatar-url',
      };

      const result = await authService.updateProfile(updateData);

      expect(mockPut).toHaveBeenCalledWith('/auth/profile', updateData);
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle profile update errors', async () => {
      const mockError = new Error('Update failed');
      const mockPut = jest.fn().mockRejectedValue(mockError);
      (authService as any).api.put = mockPut;

      const updateData = { name: 'Updated Name' };

      await expect(authService.updateProfile(updateData)).rejects.toThrow(
        'Update failed'
      );
    });
  });

  describe('changePassword', () => {
    it('should change password successfully', async () => {
      const mockResponse = { success: true };
      const { apiClient } = require('../../services/apiClient');
      apiClient.post.mockResolvedValue(mockResponse);

      await authService.changePassword('oldpassword', 'newpassword123');

      expect(apiClient.post).toHaveBeenCalledWith('/auth/change-password', {
        oldPassword: 'oldpassword',
        newPassword: 'newpassword123',
      });
    });

    it('should handle incorrect old password', async () => {
      const mockResponse = {
        success: false,
        error: { message: 'Incorrect old password' },
      };

      const { apiClient } = require('../../services/apiClient');
      apiClient.post.mockResolvedValue(mockResponse);

      await expect(
        authService.changePassword('wrongpassword', 'newpassword123')
      ).rejects.toThrow('Incorrect old password');
    });
  });

  describe('checkEmailExists', () => {
    it('should return true for existing email', async () => {
      const mockResponse = {
        success: true,
        data: { exists: true },
      };

      const { apiClient } = require('../../services/apiClient');
      apiClient.get.mockResolvedValue(mockResponse);

      const result = await authService.checkEmailExists('existing@example.com');

      expect(result).toBe(true);
      expect(apiClient.get).toHaveBeenCalledWith('/auth/check-email/existing@example.com');
    });

    it('should return false for non-existent email', async () => {
      const mockResponse = {
        success: true,
        data: { exists: false },
      };

      const { apiClient } = require('../../services/apiClient');
      apiClient.get.mockResolvedValue(mockResponse);

      const result = await authService.checkEmailExists('new@example.com');

      expect(result).toBe(false);
    });
  });

  describe('checkAuthStatus', () => {
    it('should return true for valid authentication', async () => {
      const { getAuthToken } = require('../../utils/authUtils');
      const { apiClient } = require('../../services/apiClient');
      
      getAuthToken.mockResolvedValue('valid-token');
      apiClient.get.mockResolvedValue({ success: true });

      const result = await authService.checkAuthStatus();

      expect(result).toBe(true);
    });

    it('should return false for invalid authentication', async () => {
      const { getAuthToken } = require('../../utils/authUtils');
      
      getAuthToken.mockResolvedValue(null);

      const result = await authService.checkAuthStatus();

      expect(result).toBe(false);
    });
  });
}); 