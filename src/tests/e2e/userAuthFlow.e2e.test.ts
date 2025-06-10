describe("Test Suite", () => {';}';'';
}
import { authService } from "../../services/authService";""/;,"/g"/;
import { apiClient } from "../../services/apiClient";""/;"/g"/;
// Mock React Native modules,'/;,'/g'/;
jest.mock('react-native', () => ({)')'';}}'';
  Platform: { OS: 'ios' ;},')'';
const Alert = { alert: jest.fn() ;}
}));';,'';
jest.mock('@react-native-async-storage/async-storage', () => ({/;)')'';,}getItem: jest.fn(),;,'/g,'/;
  setItem: jest.fn(),;
removeItem: jest.fn(),;
multiSet: jest.fn(),;
multiGet: jest.fn(),;
const clear = jest.fn();
}
 }));';,'';
jest.mock('react-native-device-info', () => ({)')'';,}getUniqueId: jest.fn(() => Promise.resolve('test-device-id'));','';
getSystemName: jest.fn(() => 'iOS');','';
getSystemVersion: jest.fn(() => '15.0');','';
getModel: jest.fn(() => 'iPhone 13')';'';
}
;}));';,'';
describe("End-to-End User Authentication Flow", () => {';,}beforeEach(async () => {jest.clearAllMocks();,}const await = clearAuthTokens();'';
}
  });';,'';
describe('Complete User Journey', () => {';,}it('should handle complete user registration and login flow', async () => {';}      // Mock API responses for registration,/;,'/g,'/;
  const: mockRegisterResponse = {success: true,data: {user: {,';,}id: "user-123";",";
username: 'newuser',email: 'newuser@example.com',createdAt: new Date().toISOString();';'';
}
          },';,'';
accessToken: 'register-access-token';','';
refreshToken: 'register-refresh-token';','';
const expiresIn = 3600;
        ;};
      };
      // Mock API responses for login,/;,/g,/;
  const: mockLoginResponse = {success: true,data: {user: {,';,}id: "user-123";",";
username: 'newuser',email: 'newuser@example.com';';'';
}
          },accessToken: 'login-access-token',refreshToken: 'login-refresh-token',expiresIn: 3600;';'';
        };
      };
      // Mock user profile response,/;,/g,/;
  const: mockUserProfileResponse = {success: true,data: {,';,}id: "user-123";",";
username: 'newuser',email: 'newuser@example.com',profile: {','';,}name: "New User";",";
age: 25,gender: 'male';';'';
}
          },preferences: {,';,}language: "zh-CN";",";
const timezone = 'Asia/Shanghai';'/;'/g'/;
}
          };
        };
      };
      // Setup API mocks,'/;,'/g,'/;
  mockRequest: jest.spyOn(apiClient, 'request');';,'';
mockRequest;
        .mockResolvedValueOnce(mockRegisterResponse) // Register/;/g/;
        .mockResolvedValueOnce(mockLoginResponse) // Login/;/g/;
        .mockResolvedValueOnce(mockUserProfileResponse) // Get user profile/;/g/;
        .mockResolvedValueOnce({ success: true ;}) // Update last active/;/g/;
        .mockResolvedValueOnce({ success: true ;}); // Logout/;/g/;
      // Step 1: User Registration,/;,/g/;
const  registerResult = await authService.register({)';,}username: "newuser";",")";,"";
email: 'newuser@example.com',password: 'password123',phone: '+86 138 0013 8000';')'';'';
}
      });
expect(registerResult).toEqual(mockRegisterResponse.data);
expect(mockRequest).toHaveBeenCalledWith({)';,}url: "/auth/register";",""/;,"/g,"/;
  method: 'POST';','';
data: expect.objectContaining({,';,)username: "newuser";","";,}email: 'newuser@example.com';','';
password: 'password123';',)'';
const phone = '+86 138 0013 8000')';'';
}
        ;});
      });
      // Step 2: User Login,/;,/g/;
const  loginResult = await authService.login({)';,}email: "newuser@example.com";",")";,"";
password: 'password123',rememberMe: true;')'';'';
}
      });
expect(loginResult).toEqual(mockLoginResponse.data);
expect(mockRequest).toHaveBeenCalledWith({)';,}url: "/auth/login";",""/;,"/g,"/;
  method: 'POST';','';
data: expect.objectContaining({,';,)email: "newuser@example.com";","";,}password: 'password123';',')'';
const rememberMe = true);
}
        ;});
      });
      // Step 3: Get User Profile,/;,/g/;
const userProfile = await userService.getCurrentUser();
expect(userProfile).toEqual(mockUserProfileResponse.data);
      // Step 4: Update Last Active,/;,/g/;
const await = userService.updateLastActive();
expect(mockRequest).toHaveBeenCalledWith({)';,}url: "/users/me/last-active";",")"/;,"/g"/;
const method = 'PUT')';'';
}
      ;});
      // Step 5: Check Authentication Status,/;,/g/;
const isAuthenticated = await isLoggedIn();
expect(isAuthenticated).toBe(true);
      // Step 6: Logout,/;,/g/;
const await = authService.logout();
expect(mockRequest).toHaveBeenCalledWith({)';,}url: "/auth/logout";",")"/;,"/g"/;
const method = 'POST')';'';
}
      ;});
    });';,'';
it('should handle user profile management flow', async () => {';}      // Mock login first,/;,'/g,'/;
  const: mockLoginResponse = {success: true,data: {user: {,';,}id: "user-123";","";"";
}
      username: 'testuser', email: 'test@example.com' ;},accessToken: 'access-token',refreshToken: 'refresh-token',expiresIn: 3600;';'';
        };
      };
      // Mock profile update responses,/;,/g,/;
  const: mockUpdateProfileResponse = {success: true,data: {,';,}id: "user-123";",";
username: 'updateduser',email: 'test@example.com',phone: '+86 138 0013 8000',profile: {','';,}name: "Updated User";",";
age: 30,gender: 'female';';'';
}
          };
        };
      };
const: mockPreferencesResponse = {success: true,data: {,';,}language: "en-US";",";
timezone: 'America/New_York',notifications: {push: true,email: false,sms: true;'/;}}'/g'/;
          };
        };
      };
const: mockHealthDataResponse = {success: true,data: {,';,}id: "health-record-123";","";"";
}
      heartRate: 75,bloodPressure: { systolic: 120, diastolic: 80 ;},steps: 10000,timestamp: new Date().toISOString();
        };
      };";,"";
mockRequest: jest.spyOn(apiClient, 'request');';,'';
mockRequest;
        .mockResolvedValueOnce(mockLoginResponse) // Login/;/g/;
        .mockResolvedValueOnce(mockUpdateProfileResponse) // Update profile/;/g/;
        .mockResolvedValueOnce(mockPreferencesResponse) // Update preferences/;/g/;
        .mockResolvedValueOnce(mockHealthDataResponse); // Sync health data/;/g/;
      // Step 1: Login,/;,/g/;
const await = authService.login({)';,}email: "test@example.com";",")";,"";
const password = 'password123')';'';
}
      ;});
      // Step 2: Update Profile,/;,/g/;
const  updatedProfile = await userService.updateUser({)';,}username: "updateduser";",";
phone: '+86 138 0013 8000',profile: {','';,}name: "Updated User";",";
age: 30,gender: 'female';')'';'';
}
        };);
      });
expect(updatedProfile).toEqual(mockUpdateProfileResponse.data);
expect(mockRequest).toHaveBeenCalledWith({)';,}url: "/users/me";",""/;,"/g,"/;
  method: 'PUT';','';
data: expect.objectContaining({,';,)username: "updateduser";",)"";,}const phone = '+86 138 0013 8000')';'';
}
        ;});
      });
      // Step 3: Update Preferences,/;,/g/;
const  preferences = await userService.updateUserPreferences({)';,}language: "en-US";",";
timezone: 'America/New_York',notifications: {push: true,email: false,sms: true;')''/;}}'/g'/;
        };);
      });
expect(preferences).toEqual(mockPreferencesResponse.data);
      // Step 4: Sync Health Data,/;,/g,/;
  healthData: await userService.syncHealthData({heartRate: 75,bloodPressure: { systolic: 120, diastolic: 80 ;},steps: 10000;);
      });
expect(healthData).toEqual(mockHealthDataResponse.data);
    });';,'';
it('should handle error scenarios gracefully', async () => {';,}mockRequest: jest.spyOn(apiClient, 'request');';'';
      // Test login failure,/;,/g/;
mockRequest.mockResolvedValueOnce({)        success: false}error: {,';,}const code = "INVALID_CREDENTIALS";";"";
);
}
        });
      });
const await = expect();
authService.login({)";,}email: "wrong@example.com";",")";,"";
const password = 'wrongpassword')';'';
}
        ;});

      // Test network error,'/;,'/g'/;
mockRequest.mockRejectedValueOnce(new Error('Network Error'));';,'';
const await = expect();
authService.login({)';,}email: "test@example.com";",")";,"";
const password = 'password123')';'';
}
        ;});';'';
      ).rejects.toThrow('Network Error');';'';
      // Test unauthorized error,/;,/g/;
mockRequest.mockResolvedValueOnce({)success: false}error: {,';,}const code = "UNAUTHORIZED";";"";
);
}
        });
      });

    });";,"";
it('should handle token refresh flow', async () => {';,}const: mockRefreshResponse = {success: true,data: {,';,}accessToken: "new-access-token";",";
refreshToken: 'new-refresh-token',expiresIn: 3600;';'';
}
        };
      };
const: mockUserResponse = {success: true,data: {,';,}id: "user-123";",";
username: 'testuser',email: 'test@example.com';';'';
}
        };
      };';,'';
mockRequest: jest.spyOn(apiClient, 'request');';,'';
mockRequest;
        .mockResolvedValueOnce({)success: false}error: {,';,}code: "TOKEN_EXPIRED";",")";"";
}
      const message = 'Token expired' ;}')'';'';
        }) // First request fails/;/g/;
        .mockResolvedValueOnce(mockRefreshResponse) // Refresh token/;/g/;
        .mockResolvedValueOnce(mockUserResponse); // Retry original request/;/g/;
      // This should trigger token refresh and retry,/;,/g/;
const userInfo = await userService.getCurrentUser();
expect(userInfo).toEqual(mockUserResponse.data);
      // Verify refresh token was called,/;,/g/;
expect(mockRequest).toHaveBeenCalledWith({)';,}url: "/auth/refresh";",")"/;,"/g"/;
const method = 'POST')';'';
}
      ;});
    });
  });';,'';
describe('Device Management Flow', () => {';,}it('should handle device registration and management', async () => {';,}const: mockLoginResponse = {success: true,data: {user: {,';,}id: "user-123";","";"";
}
      username: 'testuser', email: 'test@example.com' ;},accessToken: 'access-token',refreshToken: 'refresh-token',expiresIn: 3600;';'';
        };
      };
const: mockDeviceResponse = {success: true,data: {,';,}id: "device-123";",";
name: 'iPhone 13',type: 'mobile',os: 'iOS',version: '15.0',isActive: true,lastSeen: new Date().toISOString();';'';
}
        };
      };
mockDevicesListResponse: {success: true,data: [mockDeviceResponse.data];}}
      };';,'';
mockRequest: jest.spyOn(apiClient, 'request');';,'';
mockRequest;
        .mockResolvedValueOnce(mockLoginResponse) // Login/;/g/;
        .mockResolvedValueOnce(mockDeviceResponse) // Add device/;/g/;
        .mockResolvedValueOnce(mockDevicesListResponse) // Get devices/;/g/;
        .mockResolvedValueOnce({ success: true ;}); // Remove device/;/g/;
      // Login first,/;,/g/;
const await = authService.login({)';,}email: "test@example.com";",")";,"";
const password = 'password123')';'';
}
      ;});
      // Add device,/;,/g/;
const  device = await userService.addDevice({)';,}name: "iPhone 13";",")";,"";
type: 'mobile',os: 'iOS',version: '15.0';')'';'';
}
      });
expect(device).toEqual(mockDeviceResponse.data);
      // Get devices,/;,/g/;
const devices = await userService.getUserDevices();
expect(devices).toEqual(mockDevicesListResponse.data);
      // Remove device,'/;,'/g'/;
const await = userService.removeDevice('device-123');';,'';
expect(mockRequest).toHaveBeenCalledWith({)';,}url: "/users/me/devices/device-123";",")"/;,"/g"/;
const method = 'DELETE')';'';
}
      ;});
    });
  });
});