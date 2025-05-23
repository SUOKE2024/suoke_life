import axios from 'axios';
import apiClient from './apiClient';

// 登录请求类型
export interface LoginRequest {
  mobile: string;
  password: string;
}

// 注册请求类型
export interface RegisterRequest {
  mobile: string;
  password: string;
  nickname: string;
  verificationCode: string;
}

// 验证码请求类型
export interface VerificationCodeRequest {
  mobile: string;
}

// 认证API服务
const authApi = {
  /**
   * 用户登录
   * @param data 登录信息
   * @returns 包含用户信息和令牌的响应
   */
  login: async (data: LoginRequest) => {
    try {
      const response = await apiClient.post('/auth/login', data);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        // 处理特定API错误
        const message = error.response?.data?.message || '登录失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 用户注册
   * @param data 注册信息
   * @returns 注册成功的响应
   */
  register: async (data: RegisterRequest) => {
    try {
      const response = await apiClient.post('/auth/register', data);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '注册失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 发送验证码
   * @param data 包含手机号的请求数据
   * @returns 发送验证码的响应
   */
  sendVerificationCode: async (data: VerificationCodeRequest) => {
    try {
      const response = await apiClient.post('/auth/send-verification-code', data);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '发送验证码失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 退出登录
   * @param token 认证令牌
   * @returns 退出登录的响应
   */
  logout: async (token: string) => {
    try {
      const response = await apiClient.post('/auth/logout', {}, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      return response.data;
    } catch (error) {
      // 退出登录即使失败也不会阻止用户在客户端登出
      return { success: true };
    }
  },

  /**
   * 刷新令牌
   * @param refreshToken 刷新令牌
   * @returns 新的访问令牌
   */
  refreshToken: async (refreshToken: string) => {
    try {
      const response = await apiClient.post('/auth/refresh-token', { refreshToken });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '刷新令牌失败，请重新登录';
        throw new Error(message);
      }
      throw error;
    }
  },
};

export default authApi; 