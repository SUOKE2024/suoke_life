import React from 'react';
import { authService } from '../../services/authService';
import { apiClient } from '../../services/apiClient';
// Mock React Native modules
jest.mock('react-native', () => ({
  Platform: { OS: 'ios' },
  Alert: { alert: jest.fn() }
}));
jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  multiSet: jest.fn(),
  multiGet: jest.fn(),
  clear: jest.fn();
}));
jest.mock('react-native-device-info', () => ({
  getUniqueId: jest.fn(() => Promise.resolve('test-device-id')),
  getSystemName: jest.fn(() => 'iOS'),
  getSystemVersion: jest.fn(() => '15.0'),
  getModel: jest.fn(() => 'iPhone 13')
}));
describe('End-to-End User Authentication Flow', () => {
  beforeEach(async () => {
    jest.clearAllMocks();
    await clearAuthTokens();
  });
  describe('Complete User Journey', () => {
    it('should handle complete user registration and login flow', async () => {
      // Mock API responses for registration
      const mockRegisterResponse = {success: true,data: {user: {
      id: "user-123",
      username: 'newuser',email: 'newuser@example.com',createdAt: new Date().toISOString();
          },
          accessToken: 'register-access-token',
          refreshToken: 'register-refresh-token',
          expiresIn: 3600
        };
      };
      // Mock API responses for login
      const mockLoginResponse = {success: true,data: {user: {
      id: "user-123",
      username: 'newuser',email: 'newuser@example.com';
          },accessToken: 'login-access-token',refreshToken: 'login-refresh-token',expiresIn: 3600;
        };
      };
      // Mock user profile response
      const mockUserProfileResponse = {success: true,data: {
      id: "user-123",
      username: 'newuser',email: 'newuser@example.com',profile: {
      name: "New User",
      age: 25,gender: 'male';
          },preferences: {
      language: "zh-CN",
      timezone: 'Asia/Shanghai';
          };
        };
      };
      // Setup API mocks
      const mockRequest = jest.spyOn(apiClient, 'request');
      mockRequest
        .mockResolvedValueOnce(mockRegisterResponse) // Register
        .mockResolvedValueOnce(mockLoginResponse) // Login
        .mockResolvedValueOnce(mockUserProfileResponse) // Get user profile
        .mockResolvedValueOnce({ success: true }) // Update last active
        .mockResolvedValueOnce({ success: true }); // Logout
      // Step 1: User Registration
      const registerResult = await authService.register({
      username: "newuser",
      email: 'newuser@example.com',password: 'password123',phone: '+86 138 0013 8000';
      });
      expect(registerResult).toEqual(mockRegisterResponse.data);
      expect(mockRequest).toHaveBeenCalledWith({
      url: "/auth/register",
      method: 'POST',
        data: expect.objectContaining({
      username: "newuser",
      email: 'newuser@example.com',
          password: 'password123',
          phone: '+86 138 0013 8000'
        });
      });
      // Step 2: User Login
      const loginResult = await authService.login({
      email: "newuser@example.com",
      password: 'password123',rememberMe: true;
      });
      expect(loginResult).toEqual(mockLoginResponse.data);
      expect(mockRequest).toHaveBeenCalledWith({
      url: "/auth/login",
      method: 'POST',
        data: expect.objectContaining({
      email: "newuser@example.com",
      password: 'password123',
          rememberMe: true
        });
      });
      // Step 3: Get User Profile
      const userProfile = await userService.getCurrentUser();
      expect(userProfile).toEqual(mockUserProfileResponse.data);
      // Step 4: Update Last Active
      await userService.updateLastActive();
      expect(mockRequest).toHaveBeenCalledWith({
      url: "/users/me/last-active",
      method: 'PUT'
      });
      // Step 5: Check Authentication Status
      const isAuthenticated = await isLoggedIn();
      expect(isAuthenticated).toBe(true);
      // Step 6: Logout
      await authService.logout();
      expect(mockRequest).toHaveBeenCalledWith({
      url: "/auth/logout",
      method: 'POST'
      });
    });
    it('should handle user profile management flow', async () => {
      // Mock login first
      const mockLoginResponse = {success: true,data: {user: {
      id: "user-123",
      username: 'testuser', email: 'test@example.com' },accessToken: 'access-token',refreshToken: 'refresh-token',expiresIn: 3600;
        };
      };
      // Mock profile update responses
      const mockUpdateProfileResponse = {success: true,data: {
      id: "user-123",
      username: 'updateduser',email: 'test@example.com',phone: '+86 138 0013 8000',profile: {
      name: "Updated User",
      age: 30,gender: 'female';
          };
        };
      };
      const mockPreferencesResponse = {success: true,data: {
      language: "en-US",
      timezone: 'America/New_York',notifications: {push: true,email: false,sms: true;
          };
        };
      };
      const mockHealthDataResponse = {success: true,data: {
      id: "health-record-123",
      heartRate: 75,bloodPressure: { systolic: 120, diastolic: 80 },steps: 10000,timestamp: new Date().toISOString();
        };
      };
      const mockRequest = jest.spyOn(apiClient, 'request');
      mockRequest
        .mockResolvedValueOnce(mockLoginResponse) // Login
        .mockResolvedValueOnce(mockUpdateProfileResponse) // Update profile
        .mockResolvedValueOnce(mockPreferencesResponse) // Update preferences
        .mockResolvedValueOnce(mockHealthDataResponse); // Sync health data
      // Step 1: Login
      await authService.login({
      email: "test@example.com",
      password: 'password123'
      });
      // Step 2: Update Profile
      const updatedProfile = await userService.updateUser({
      username: "updateduser",
      phone: '+86 138 0013 8000',profile: {
      name: "Updated User",
      age: 30,gender: 'female';
        };
      });
      expect(updatedProfile).toEqual(mockUpdateProfileResponse.data);
      expect(mockRequest).toHaveBeenCalledWith({
      url: "/users/me",
      method: 'PUT',
        data: expect.objectContaining({
      username: "updateduser",
      phone: '+86 138 0013 8000'
        });
      });
      // Step 3: Update Preferences
      const preferences = await userService.updateUserPreferences({
      language: "en-US",
      timezone: 'America/New_York',notifications: {push: true,email: false,sms: true;
        };
      });
      expect(preferences).toEqual(mockPreferencesResponse.data);
      // Step 4: Sync Health Data
      const healthData = await userService.syncHealthData({heartRate: 75,bloodPressure: { systolic: 120, diastolic: 80 },steps: 10000;
      });
      expect(healthData).toEqual(mockHealthDataResponse.data);
    });
    it('should handle error scenarios gracefully', async () => {
      const mockRequest = jest.spyOn(apiClient, 'request');
      // Test login failure
      mockRequest.mockResolvedValueOnce({
        success: false,
        error: {
      code: "INVALID_CREDENTIALS",
      message: '邮箱或密码错误'
        }
      });
      await expect(
        authService.login({
      email: "wrong@example.com",
      password: 'wrongpassword'
        });
      ).rejects.toThrow('邮箱或密码错误');
      // Test network error
      mockRequest.mockRejectedValueOnce(new Error('Network Error'));
      await expect(
        authService.login({
      email: "test@example.com",
      password: 'password123'
        });
      ).rejects.toThrow('Network Error');
      // Test unauthorized error
      mockRequest.mockResolvedValueOnce({
        success: false,
        error: {
      code: "UNAUTHORIZED",
      message: '认证已过期，请重新登录'
        }
      });
      await expect(userService.getCurrentUser()).rejects.toThrow('认证已过期，请重新登录');
    });
    it('should handle token refresh flow', async () => {
      const mockRefreshResponse = {success: true,data: {
      accessToken: "new-access-token",
      refreshToken: 'new-refresh-token',expiresIn: 3600;
        };
      };
      const mockUserResponse = {success: true,data: {
      id: "user-123",
      username: 'testuser',email: 'test@example.com';
        };
      };
      const mockRequest = jest.spyOn(apiClient, 'request');
      mockRequest
        .mockResolvedValueOnce({
          success: false,
          error: {
      code: "TOKEN_EXPIRED",
      message: 'Token expired' }
        }) // First request fails
        .mockResolvedValueOnce(mockRefreshResponse) // Refresh token
        .mockResolvedValueOnce(mockUserResponse); // Retry original request
      // This should trigger token refresh and retry
      const userInfo = await userService.getCurrentUser();
      expect(userInfo).toEqual(mockUserResponse.data);
      // Verify refresh token was called
      expect(mockRequest).toHaveBeenCalledWith({
      url: "/auth/refresh",
      method: 'POST'
      });
    });
  });
  describe('Device Management Flow', () => {
    it('should handle device registration and management', async () => {
      const mockLoginResponse = {success: true,data: {user: {
      id: "user-123",
      username: 'testuser', email: 'test@example.com' },accessToken: 'access-token',refreshToken: 'refresh-token',expiresIn: 3600;
        };
      };
      const mockDeviceResponse = {success: true,data: {
      id: "device-123",
      name: 'iPhone 13',type: 'mobile',os: 'iOS',version: '15.0',isActive: true,lastSeen: new Date().toISOString();
        };
      };
      const mockDevicesListResponse = {success: true,data: [mockDeviceResponse.data];
      };
      const mockRequest = jest.spyOn(apiClient, 'request');
      mockRequest
        .mockResolvedValueOnce(mockLoginResponse) // Login
        .mockResolvedValueOnce(mockDeviceResponse) // Add device
        .mockResolvedValueOnce(mockDevicesListResponse) // Get devices
        .mockResolvedValueOnce({ success: true }); // Remove device
      // Login first
      await authService.login({
      email: "test@example.com",
      password: 'password123'
      });
      // Add device
      const device = await userService.addDevice({
      name: "iPhone 13",
      type: 'mobile',os: 'iOS',version: '15.0';
      });
      expect(device).toEqual(mockDeviceResponse.data);
      // Get devices
      const devices = await userService.getUserDevices();
      expect(devices).toEqual(mockDevicesListResponse.data);
      // Remove device
      await userService.removeDevice('device-123');
      expect(mockRequest).toHaveBeenCalledWith({
      url: "/users/me/devices/device-123",
      method: 'DELETE'
      });
    });
  });
});
