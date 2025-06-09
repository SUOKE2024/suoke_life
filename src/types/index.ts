// 索克生活核心类型定义
// 用户类型
export interface User {
  id: string;,
  username: string;
  email: string;
  phone?: string;
  avatar?: string;
  profile?: UserProfile;
  createdAt: string;,
  updatedAt: string;
}
// 用户档案
export interface UserProfile {
  name: string;
  age?: number;
  gender?: 'male' | 'female' | 'other';
  height?: number;
  weight?: number;
  constitution?: string;
  medicalHistory?: string[];
  allergies?: string[];
}
// 认证状态
export interface AuthState {
  isAuthenticated: boolean;
  user?: User;
  token?: string;
  refreshToken?: string;
  loading: boolean;
  error?: string;
}
// API响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    message: string;
    code?: string;
  };
  message?: string;
}
// 导出智能体类型
export * from './agents';
// 导出中医辨证类型
export * from './TCM';
// 导出其他核心类型
export * from './core';
export * from './api';
export * from './chat';
export * from './explore';
export * from './life';
export * from './navigation';
export * from './profile';
export * from './suoke';
