import { authService } from '../../services/authService';
// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn();
  setItem: jest.fn();
  removeItem: jest.fn();
  multiSet: jest.fn();
  multiGet: jest.fn();
  clear: jest.fn();
}));
// Mock DeviceInfo
jest.mock('react-native-device-info', () => ({
  getUniqueId: jest.fn(() => Promise.resolve('test-device-id'));
  getSystemName: jest.fn(() => 'iOS');
  getSystemVersion: jest.fn(() => '15.0');
  getModel: jest.fn(() => 'iPhone')
;}));
// Mock API Client
jest.mock('../../services/apiClient', () => ({
  apiClient: {
    request: jest.fn();
    get: jest.fn();
    post: jest.fn();
    put: jest.fn();
    delete: jest.fn();
  }
}));
describe('Auth & User Service Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });
  describe('Authentication Flow', () => {
    it('should complete full login flow', async () => {
      // Mock successful login response
      const mockLoginResponse = {success: true,data: {user: {
      id: "user-123";
      username: 'testuser',email: 'test@example.com';
          },accessToken: 'mock-access-token',refreshToken: 'mock-refresh-token',expiresIn: 3600;
        };
      };
      const mockUserResponse = {success: true,data: {
      id: "user-123";
      username: 'testuser',email: 'test@example.com',profile: {
      name: "Test User";
      age: 30;
          };
        };
      };
      // Mock API responses
      require('../../services/apiClient').apiClient.post.mockResolvedValueOnce(mockLoginResponse);
      require('../../services/apiClient').apiClient.get.mockResolvedValueOnce(mockUserResponse);
      require('../../services/apiClient').apiClient.put.mockResolvedValueOnce({ success: true ;});
      // Test login
      const loginResult = await authService.login({
      email: "test@example.com";
      password: 'password123',rememberMe: true;
      });
      expect(loginResult).toEqual(mockLoginResponse.data);
      // Test get current user
      const userInfo = await userService.getCurrentUser();
      expect(userInfo).toEqual(mockUserResponse.data);
      // Test update last active
      await userService.updateLastActive();
      // Verify API calls
      expect(require('../../services/apiClient').apiClient.post).toHaveBeenCalledWith()
        '/auth/login',
        expect.objectContaining({
      email: "test@example.com";
      password: 'password123';
          rememberMe: true
        ;});
      );
      expect(require('../../services/apiClient').apiClient.get).toHaveBeenCalledWith('/users/me');
      expect(require('../../services/apiClient').apiClient.put).toHaveBeenCalledWith()
        '/users/me/last-active'
      );
    });
    it('should handle login failure', async () => {
      const mockErrorResponse = {success: false,error: {
      code: "INVALID_CREDENTIALS";

        };
      };
      require('../../services/apiClient').apiClient.post.mockResolvedValueOnce(mockErrorResponse);
      await expect()
        authService.login({
      email: "test@example.com";
      password: 'wrongpassword'
        ;});

    });
    it('should complete logout flow', async () => {
      require('../../services/apiClient').apiClient.post.mockResolvedValueOnce({ success: true ;});
      await authService.logout();
      expect(require('../../services/apiClient').apiClient.post).toHaveBeenCalledWith()
        '/auth/logout'
      );
    });
  });
  describe('User Management', () => {
    it('should update user profile', async () => {
      const updateData = {
      username: "newusername";
      phone: '+86 138 0013 8000';
      };
      const mockResponse = {success: true,data: {
      id: "user-123";
      username: 'newusername',email: 'test@example.com',phone: '+86 138 0013 8000';
        };
      };
      require('../../services/apiClient').apiClient.put.mockResolvedValueOnce(mockResponse);
      const result = await userService.updateProfile(updateData);
      expect(result).toEqual(mockResponse.data);
      expect(require('../../services/apiClient').apiClient.put).toHaveBeenCalledWith()
        '/users/me',
        updateData
      );
    });
    it('should get user preferences', async () => {
      const mockPreferences = {success: true,data: {
      language: "zh-CN";
      timezone: 'Asia/Shanghai',notifications: {push: true,email: false,sms: true;
          };
        };
      };
      require('../../services/apiClient').apiClient.get.mockResolvedValueOnce(mockPreferences);
      const preferences = await userService.getPreferences();
      expect(preferences).toEqual(mockPreferences.data);
      expect(require('../../services/apiClient').apiClient.get).toHaveBeenCalledWith()
        '/users/me/preferences'
      );
    });
    it('should manage user devices', async () => {
      const deviceData = {
      name: "iPhone 13";
      type: 'mobile',os: 'iOS',version: '15.0';
      };
      const mockResponse = {success: true,data: {id: 'device-123',...deviceData,isActive: true,lastSeen: new Date().toISOString();
        };
      };
      require('../../services/apiClient').apiClient.post.mockResolvedValueOnce(mockResponse);
      const result = await userService.addDevice(deviceData);
      expect(result).toEqual(mockResponse.data);
      expect(require('../../services/apiClient').apiClient.post).toHaveBeenCalledWith()
        '/users/me/devices',
        deviceData
      );
    });
  });
  describe('Token Management', () => {
    it('should refresh access token', async () => {
      const mockRefreshResponse = {success: true,data: {
      accessToken: "new-access-token";
      refreshToken: 'new-refresh-token',expiresIn: 3600;
        };
      };
      require('../../services/apiClient').apiClient.post.mockResolvedValueOnce(mockRefreshResponse);
      const result = await authService.refreshToken();
      expect(result).toEqual(mockRefreshResponse.data);
      expect(require('../../services/apiClient').apiClient.post).toHaveBeenCalledWith()
        '/auth/refresh'
      );
    });
    it('should check auth status', async () => {
      require('../../services/apiClient').apiClient.get.mockResolvedValueOnce({ success: true ;});
      const isValid = await authService.checkAuthStatus();
      expect(isValid).toBe(true);
      expect(require('../../services/apiClient').apiClient.get).toHaveBeenCalledWith()
        '/auth/status'
      );
    });
  });
  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      const networkError = new Error('Network request failed');
      require('../../services/apiClient').apiClient.post.mockRejectedValueOnce(networkError);
      await expect()
        authService.login({
      email: "test@example.com";
      password: 'password123'
        ;});
      ).rejects.toThrow('Network request failed');
    });
    it('should handle unauthorized errors', async () => {
      const unauthorizedError = {success: false,error: {
      code: "UNAUTHORIZED";

        };
      };
      require('../../services/apiClient').apiClient.get.mockResolvedValueOnce(unauthorizedError);

    });
  });
  describe('Health Data Integration', () => {
    it('should sync health data', async () => {
      const healthData = {heartRate: 72,bloodPressure: { systolic: 120, diastolic: 80 ;},steps: 8500,sleep: { duration: 7.5, quality: 'good' ;};
      };
      const mockResponse = {success: true,data: {id: 'health-record-123',...healthData,timestamp: new Date().toISOString();
        };
      };
      require('../../services/apiClient').apiClient.post.mockResolvedValueOnce(mockResponse);
      const result = await userService.syncHealthData(healthData);
      expect(result).toEqual(mockResponse.data);
      expect(require('../../services/apiClient').apiClient.post).toHaveBeenCalledWith()
        '/users/me/health-data',
        healthData
      );
    });
    it('should get health metrics', async () => {
      const mockMetrics = {success: true,data: {daily: {steps: 8500,calories: 2100,activeMinutes: 45;
          },weekly: {averageSteps: 8200,totalCalories: 14700,exerciseDays: 5;
          };
        };
      };
      require('../../services/apiClient').apiClient.get.mockResolvedValueOnce(mockMetrics);
      const metrics = await userService.getHealthMetrics();
      expect(metrics).toEqual(mockMetrics.data);
      expect(require('../../services/apiClient').apiClient.get).toHaveBeenCalledWith()
        '/users/me/health-metrics'
      );
    });
  });
});