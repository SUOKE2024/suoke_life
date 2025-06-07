import { apiClient } from './apiClient';
import { ApiResponse, User } from '../types';
import { storeUserId, getUserId } from '../utils/authUtils';
// 用户信息更新请求
export interface UpdateUserRequest {
  username?: string;
  email?: string;
  phone?: string;
  avatar?: string;
  dateOfBirth?: string;
  gender?: 'male' | 'female' | 'other';
  height?: number;
  weight?: number;
  bloodType?: string;
  emergencyContact?: {
    name: string;
  phone: string;
    relationship: string;
};
}
// 用户偏好设置
export interface UserPreferences {
  language: string;
  timezone: string;
  notifications: {;
  push: boolean;
    email: boolean;
  sms: boolean;
    healthReminders: boolean;
  appointmentReminders: boolean;
};
  privacy: {,
  profileVisibility: 'public' | 'private' | 'friends';
    dataSharing: boolean,
  analyticsOptIn: boolean;
  };
  healthGoals: {
    dailySteps?: number;
    weeklyExercise?: number;
    sleepHours?: number;
    waterIntake?: number;
  };
}
// 设备信息
export interface DeviceInfo {
  id: string;
  name: string;
  type: 'mobile' | 'tablet' | 'wearable' | 'sensor';
  platform: string;
  version: string;
  lastActive: string;
  isActive: boolean;
}
// 健康数据记录
export interface HealthRecord {
  id: string;
  type: 'vital_signs' | 'symptoms' | 'medication' | 'exercise' | 'diet' | 'sleep';
  data: any;
  timestamp: string;
  source: string;
  verified: boolean;
}
// 用户统计信息
export interface UserStats {
  totalHealthRecords: number;
  lastCheckup: string;
  healthScore: number;
  activeDevices: number;
  dataPoints: {;
  vitals: number;
    symptoms: number;
  medications: number;
    exercises: number;
};
}
class UserService {
  // 获取当前用户信息
  async getCurrentUser(): Promise<User> {
    try {
      const response: ApiResponse<User> = await apiClient.get('/users/me');
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || '获取用户信息失败');
      }
      // 存储用户ID;
      if (response.data.id) {
        await storeUserId(response.data.id);
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || '获取用户信息失败');
    }
  }
  // 更新用户信息
  async updateUser(userData: UpdateUserRequest): Promise<User> {
    try {
      const response: ApiResponse<User> = await apiClient.put('/users/me', userData);
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || '更新用户信息失败');
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || '更新用户信息失败');
    }
  }
  // 上传用户头像
  async uploadAvatar(imageFile: File | Blob): Promise<string> {
    try {
      const formData = new FormData();
      formData.append('avatar', imageFile);
      const response: ApiResponse<{ avatarUrl: string }> = await apiClient.post(
        '/users/me/avatar',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || '上传头像失败');
      }
      return response.data.avatarUrl;
    } catch (error: any) {
      throw new Error(error.message || '上传头像失败');
    }
  }
  // 获取用户偏好设置
  async getUserPreferences(): Promise<UserPreferences> {
    try {
      const response: ApiResponse<UserPreferences> = await apiClient.get('/users/me/preferences');
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || '获取用户偏好失败');
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || '获取用户偏好失败');
    }
  }
  // 更新用户偏好设置
  async updateUserPreferences(preferences: Partial<UserPreferences>): Promise<UserPreferences> {
    try {
      const response: ApiResponse<UserPreferences> = await apiClient.put(
        '/users/me/preferences',
        preferences;
      );
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || '更新用户偏好失败');
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || '更新用户偏好失败');
    }
  }
  // 获取用户设备列表
  async getUserDevices(): Promise<DeviceInfo[]> {
    try {
      const response: ApiResponse<DeviceInfo[]> = await apiClient.get('/users/me/devices');
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || '获取设备列表失败');
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || '获取设备列表失败');
    }
  }
  // 注册新设备
  async registerDevice(
    deviceInfo: Omit<DeviceInfo, 'id' | 'lastActive' | 'isActive'>
  ): Promise<DeviceInfo> {
    try {
      const response: ApiResponse<DeviceInfo> = await apiClient.post(
        '/users/me/devices',
        deviceInfo;
      );
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || '注册设备失败');
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || '注册设备失败');
    }
  }
  // 移除设备
  async removeDevice(deviceId: string): Promise<void> {
    try {
      const response: ApiResponse = await apiClient.delete(`/users/me/devices/${deviceId}`);
      if (!response.success) {
        throw new Error(response.error?.message || '移除设备失败');
      }
    } catch (error: any) {
      throw new Error(error.message || '移除设备失败');
    }
  }
  // 获取健康记录
  async getHealthRecords(
    type?: string,
    startDate?: string,
    endDate?: string,
    limit?: number,
    offset?: number;
  ): Promise<{ records: HealthRecord[]; total: number }> {
    try {
      const params = new URLSearchParams();
      if (type) params.append('type', type);
      if (startDate) params.append('startDate', startDate);
      if (endDate) params.append('endDate', endDate);
      if (limit) params.append('limit', limit.toString());
      if (offset) params.append('offset', offset.toString());
      const response: ApiResponse<{ records: HealthRecord[]; total: number }> = await apiClient.get(
        `/users/me/health-records?${params.toString()}`
      );
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || '获取健康记录失败');
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || '获取健康记录失败');
    }
  }
  // 添加健康记录
  async addHealthRecord(
    record: Omit<HealthRecord, 'id' | 'timestamp' | 'verified'>
  ): Promise<HealthRecord> {
    try {
      const response: ApiResponse<HealthRecord> = await apiClient.post(
        '/users/me/health-records',
        record;
      );
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || '添加健康记录失败');
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || '添加健康记录失败');
    }
  }
  // 更新健康记录
  async updateHealthRecord(
    recordId: string,
    updates: Partial<HealthRecord>
  ): Promise<HealthRecord> {
    try {
      const response: ApiResponse<HealthRecord> = await apiClient.put(
        `/users/me/health-records/${recordId}`,
        updates;
      );
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || '更新健康记录失败');
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || '更新健康记录失败');
    }
  }
  // 删除健康记录
  async deleteHealthRecord(recordId: string): Promise<void> {
    try {
      const response: ApiResponse = await apiClient.delete(`/users/me/health-records/${recordId}`);
      if (!response.success) {
        throw new Error(response.error?.message || '删除健康记录失败');
      }
    } catch (error: any) {
      throw new Error(error.message || '删除健康记录失败');
    }
  }
  // 获取用户统计信息
  async getUserStats(): Promise<UserStats> {
    try {
      const response: ApiResponse<UserStats> = await apiClient.get('/users/me/stats');
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || '获取用户统计失败');
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || '获取用户统计失败');
    }
  }
  // 导出用户数据
  async exportUserData(format: 'json' | 'csv' | 'pdf' = 'json'): Promise<Blob> {
    try {
      const response = await apiClient.get(`/users/me/export?format=${format}`, {responseType: 'blob';
      });
      return response as Blob;
    } catch (error: any) {
      throw new Error(error.message || '导出用户数据失败');
    }
  }
  // 删除用户账户
  async deleteAccount(password: string): Promise<void> {
    try {
      const response: ApiResponse = await apiClient.delete('/users/me', {
        data: { password }
      });
      if (!response.success) {
        throw new Error(response.error?.message || '删除账户失败');
      }
    } catch (error: any) {
      throw new Error(error.message || '删除账户失败');
    }
  }
  // 获取用户活动日志
  async getActivityLog(
    startDate?: string,
    endDate?: string,
    limit?: number,
    offset?: number;
  ): Promise<{ activities: any[]; total: number }> {
    try {
      const params = new URLSearchParams();
      if (startDate) params.append('startDate', startDate);
      if (endDate) params.append('endDate', endDate);
      if (limit) params.append('limit', limit.toString());
      if (offset) params.append('offset', offset.toString());
      const response: ApiResponse<{ activities: any[]; total: number }> = await apiClient.get(
        `/users/me/activity-log?${params.toString()}`
      );
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || '获取活动日志失败');
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || '获取活动日志失败');
    }
  }
  // 更新最后活跃时间
  async updateLastActive(): Promise<void> {
    try {
      await apiClient.post('/users/me/last-active');
    } catch (error) {
      // 静默失败，不影响用户体验
      console.warn('更新最后活跃时间失败:', error);
    }
  }
  // 检查用户名是否可用
  async checkUsernameAvailability(username: string): Promise<boolean> {
    try {
      const response: ApiResponse<{ available: boolean }> = await apiClient.get(
        `/users/check-username?username=${encodeURIComponent(username)}`
      );
      if (!response.success) {
        return false;
      }
      return response.data?.available || false;
    } catch (error) {
      return false;
    }
  }
  // 检查邮箱是否可用
  async checkEmailAvailability(email: string): Promise<boolean> {
    try {
      const response: ApiResponse<{ available: boolean }> = await apiClient.get(
        `/users/check-email?email=${encodeURIComponent(email)}`
      );
      if (!response.success) {
        return false;
      }
      return response.data?.available || false;
    } catch (error) {
      return false;
    }
  }
}
// 导出单例实例
export const userService = new UserService();
export default userService;
