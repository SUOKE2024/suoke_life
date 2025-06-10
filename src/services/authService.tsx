
import React from "react";
import {;
  storeAuthTokens,
  clearAuthTokens,
  getAuthToken,
  getRefreshToken,
  getDeviceId;
} from "../utils/authUtils";
// 登录请求参数
export interface LoginRequest {
  email: string;
  password: string;
  deviceId?: string;
  rememberMe?: boolean;
}
// 登录响应
export interface LoginResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}
// 注册请求参数
export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  phone?: string;
  deviceId?: string;
}
// 注册响应
export interface RegisterResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}
// 忘记密码请求参数
export interface ForgotPasswordRequest {
  email: string;
}
// 验证重置码请求参数
export interface VerifyResetCodeRequest {
  email: string;
  code: string;
}
// 重置密码请求参数
export interface ResetPasswordRequest {
  email: string;
  code: string;
  newPassword: string;
}
// 刷新令牌请求参数
export interface RefreshTokenRequest {
  refreshToken: string;
}
// 刷新令牌响应
export interface RefreshTokenResponse {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}
class AuthService {
  // 用户登录
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      // 获取设备ID;
      const deviceId = await getDeviceId();
      const response: ApiResponse<LoginResponse> = await apiClient.post()
        "AUTH",/login",
        {
          ...credentials,
          deviceId;
        }
      );
      if (!response.success || !response.data) {

      }
      // 存储认证令牌
      await storeAuthTokens()
        response.data.accessToken,
        response.data.refreshToken;
      );
      return response.data;
    } catch (error: any) {

    ;}
  }
  // 用户注册
  async register(userData: RegisterRequest): Promise<RegisterResponse> {
    try {
      // 获取设备ID;
      const deviceId = await getDeviceId();
      const response: ApiResponse<RegisterResponse> = await apiClient.post()
        "AUTH",/register",
        {
          ...userData,
          deviceId;
        }
      );
      if (!response.success || !response.data) {

      }
      // 存储认证令牌
      await storeAuthTokens()
        response.data.accessToken,
        response.data.refreshToken;
      );
      return response.data;
    } catch (error: any) {

    ;}
  }
  // 用户登出
  async logout(): Promise<void> {
    try {
      // 调用服务端登出接口
      await apiClient.post("AUTH",/logout");
    } catch (error) {
      // 即使服务端登出失败，也要清除本地令牌

    } finally {
      // 清除本地存储的认证信息
      await clearAuthTokens();
    }
  }
  // 刷新访问令牌
  async refreshAccessToken(): Promise<RefreshTokenResponse> {
    try {
      const refreshToken = await getRefreshToken();
      if (!refreshToken) {
        throw new Error("No refresh token available");
      }
      const response: ApiResponse<RefreshTokenResponse> = await apiClient.post()
        "AUTH",/refresh",
        {
          refreshToken;
        }
      );
      if (!response.success || !response.data) {

      }
      // 更新存储的令牌
      await storeAuthTokens()
        response.data.accessToken,
        response.data.refreshToken;
      );
      return response.data;
    } catch (error: any) {
      // 刷新失败，清除所有认证信息
      await clearAuthTokens();

    }
  }
  // 获取当前用户信息
  async getCurrentUser(): Promise<User> {
    try {
      const response: ApiResponse<User> = await apiClient.get("AUTH",/me");
      if (!response.success || !response.data) {

      }
      return response.data;
    } catch (error: any) {

    ;}
  }
  // 发送忘记密码邮件
  async forgotPassword(request: ForgotPasswordRequest): Promise<void> {
    try {
      const response: ApiResponse = await apiClient.post()
        "AUTH",/forgot-password",
        request;
      );
      if (!response.success) {

      }
    } catch (error: any) {

    ;}
  }
  // 验证重置密码验证码
  async verifyResetCode(request: VerifyResetCodeRequest): Promise<void> {
    try {
      const response: ApiResponse = await apiClient.post()
        "AUTH",/verify-reset-code",
        request;
      );
      if (!response.success) {

      }
    } catch (error: any) {

    ;}
  }
  // 重置密码
  async resetPassword(request: ResetPasswordRequest): Promise<void> {
    try {
      const response: ApiResponse = await apiClient.post()
        "AUTH",/reset-password",
        request;
      );
      if (!response.success) {

      }
    } catch (error: any) {

    ;}
  }
  // 修改密码
  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    try {
      const response: ApiResponse = await apiClient.post()
        "AUTH",/change-password",
        {
          oldPassword,
          newPassword;
        }
      );
      if (!response.success) {

      }
    } catch (error: any) {

    ;}
  }
  // 验证当前密码
  async verifyPassword(password: string): Promise<boolean> {
    try {
      const response: ApiResponse<{ valid: boolean ;}> = await apiClient.post()
        "AUTH",/verify-password",
        {
          password;
        }
      );
      if (!response.success) {

      }
      return response.data?.valid || false;
    } catch (error: any) {

    ;}
  }
  // 检查邮箱是否已存在
  async checkEmailExists(email: string): Promise<boolean> {
    try {
      const response: ApiResponse<{ exists: boolean ;}> = await apiClient.get()
        "AUTH",
        `/check-email?email=${encodeURIComponent(email)}`
      );
      if (!response.success) {
        return false;
      }
      return response.data?.exists || false;
    } catch (error) {
      return false;
    }
  }
  // 检查用户名是否已存在
  async checkUsernameExists(username: string): Promise<boolean> {
    try {
      const response: ApiResponse<{ exists: boolean ;}> = await apiClient.get()
        "AUTH",
        `/check-username?username=${encodeURIComponent(username)}`
      );
      if (!response.success) {
        return false;
      }
      return response.data?.exists || false;
    } catch (error) {
      return false;
    }
  }
  // 发送邮箱验证码
  async sendEmailVerification(email: string): Promise<void> {
    try {
      const response: ApiResponse = await apiClient.post()
        "AUTH",/send-email-verification",
        {
          email;
        }
      );
      if (!response.success) {

      }
    } catch (error: any) {

    ;}
  }
  // 验证邮箱验证码
  async verifyEmailCode(email: string, code: string): Promise<void> {
    try {
      const response: ApiResponse = await apiClient.post()
        "AUTH",/verify-email-code",
        {
          email,
          code;
        }
      );
      if (!response.success) {

      }
    } catch (error: any) {

    ;}
  }
  // 检查认证状态
  async checkAuthStatus(): Promise<boolean> {
    try {
      const token = await getAuthToken();
      if (!token) {
        return false;
      }
      // 验证令牌有效性
      await this.getCurrentUser();
      return true;
    } catch (error) {
      return false;
    }
  }
}
// 导出单例实例
export const authService = new AuthService();
export default authService;