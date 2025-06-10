import { apiClient } from "./apiClient";""/;,"/g"/;
import { ApiResponse, User } from "../types";""/;,"/g"/;
import { storeUserId, getUserId } from "../utils/authUtils";""/;"/g"/;
// 用户信息更新请求/;,/g/;
export interface UpdateUserRequest {;,}username?: string;
email?: string;
phone?: string;
avatar?: string;";,"";
dateOfBirth?: string;';,'';
gender?: 'male' | 'female' | 'other';';,'';
height?: number;
weight?: number;
bloodType?: string;
emergencyContact?: {name: string}phone: string,;
}
}
  const relationship = string;}
};
}
// 用户偏好设置/;,/g/;
export interface UserPreferences {language: string}timezone: string,;
notifications: {push: boolean,;
email: boolean,;
sms: boolean,;
healthReminders: boolean,;
}
}
  const appointmentReminders = boolean;}
};';,'';
privacy: {,';,}profileVisibility: 'public' | 'private' | 'friends';','';
dataSharing: boolean,;
}
  const analyticsOptIn = boolean;}
  };
const healthGoals = {dailySteps?: number;,}weeklyExercise?: number;
sleepHours?: number;
}
    waterIntake?: number;}
  };
}
// 设备信息/;,/g/;
export interface DeviceInfo {id: string,';,}name: string,';,'';
type: 'mobile' | 'tablet' | 'wearable' | 'sensor';','';
platform: string,;
version: string,;
lastActive: string,;
}
}
  const isActive = boolean;}
}
// 健康数据记录/;,/g/;
export interface HealthRecord {';,}id: string,';,'';
type: 'vital_signs' | 'symptoms' | 'medication' | 'exercise' | 'diet' | 'sleep';','';
data: any,;
timestamp: string,;
source: string,;
}
}
  const verified = boolean;}
}
// 用户统计信息/;,/g/;
export interface UserStats {totalHealthRecords: number}lastCheckup: string,;
healthScore: number,;
activeDevices: number,;
dataPoints: {vitals: number,;
symptoms: number,;
medications: number,;
}
}
  const exercises = number;}
};
}
class UserService {// 获取当前用户信息/;,}const async = getCurrentUser(): Promise<User> {';,}try {';,}const response: ApiResponse<User> = await apiClient.get('/users/me');'/;,'/g'/;
if (!response.success || !response.data) {}}
}
}
      }
      // 存储用户ID;/;,/g/;
if (response.data.id) {}}
        const await = storeUserId(response.data.id);}
      }
      return response.data;
    } catch (error: any) {}}
}
    ;}
  }
  // 更新用户信息/;,/g/;
const async = updateUser(userData: UpdateUserRequest): Promise<User> {';,}try {';,}const response: ApiResponse<User> = await apiClient.put('/users/me', userData);'/;,'/g'/;
if (!response.success || !response.data) {}}
}
      }
      return response.data;
    } catch (error: any) {}}
}
    ;}
  }
  // 上传用户头像/;,/g/;
const async = uploadAvatar(imageFile: File | Blob): Promise<string> {try {';,}const formData = new FormData();';'';
}
      formData.append('avatar', imageFile);'}'';
const  response: ApiResponse<{ avatarUrl: string ;}> = await apiClient.post()';'';
        '/users/me/avatar','/;,'/g'/;
formData,;
        {';,}const headers = {';}}'';
            'Content-Type': 'multipart/form-data'}''/;'/g'/;
          ;}
        }
      );
if (!response.success || !response.data) {}}
}
      }
      return response.data.avatarUrl;
    } catch (error: any) {}}
}
    ;}
  }
  // 获取用户偏好设置/;,/g/;
const async = getUserPreferences(): Promise<UserPreferences> {';,}try {';,}const response: ApiResponse<UserPreferences> = await apiClient.get('/users/me/preferences');'/;,'/g'/;
if (!response.success || !response.data) {}}
}
      }
      return response.data;
    } catch (error: any) {}}
}
    ;}
  }
  // 更新用户偏好设置/;,/g/;
const async = updateUserPreferences(preferences: Partial<UserPreferences>): Promise<UserPreferences> {try {';,}const  response: ApiResponse<UserPreferences> = await apiClient.put()';'';
        '/users/me/preferences';'/;,'/g'/;
preferences;
      );
if (!response.success || !response.data) {}}
}
      }
      return response.data;
    } catch (error: any) {}}
}
    ;}
  }
  // 获取用户设备列表/;,/g/;
const async = getUserDevices(): Promise<DeviceInfo[]> {';,}try {';,}const response: ApiResponse<DeviceInfo[]> = await apiClient.get('/users/me/devices');'/;,'/g'/;
if (!response.success || !response.data) {}}
}
      }
      return response.data;
    } catch (error: any) {}}
}
    ;}
  }
  // 注册新设备'/;,'/g'/;
const async = registerDevice()';,'';
deviceInfo: Omit<DeviceInfo, 'id' | 'lastActive' | 'isActive'>';'';
  ): Promise<DeviceInfo> {try {';,}const  response: ApiResponse<DeviceInfo> = await apiClient.post()';'';
        '/users/me/devices';'/;,'/g'/;
deviceInfo;
      );
if (!response.success || !response.data) {}}
}
      }
      return response.data;
    } catch (error: any) {}}
}
    ;}
  }
  // 移除设备/;,/g/;
const async = removeDevice(deviceId: string): Promise<void> {}}
    try {}
      const response: ApiResponse = await apiClient.delete(`/users/me/devices/${deviceId;}`);```/`;,`/g`/`;
if (!response.success) {}}
}
      }
    } catch (error: any) {}}
}
    ;}
  }
  // 获取健康记录/;,/g/;
const async = getHealthRecords();
type?: string;
startDate?: string;
endDate?: string;
limit?: number;
offset?: number;
  ): Promise<{ records: HealthRecord[]; total: number ;}> {try {';,}const params = new URLSearchParams();';,'';
if (type) params.append('type', type);';,'';
if (startDate) params.append('startDate', startDate);';,'';
if (endDate) params.append('endDate', endDate);';,'';
if (limit) params.append('limit', limit.toString());';'';
}
      if (offset) params.append('offset', offset.toString());'}'';
const  response: ApiResponse<{ records: HealthRecord[]; total: number ;}> = await apiClient.get();
        `/users/me/health-records?${params.toString()}````/`;`/g`/`;
      );
if (!response.success || !response.data) {}}
}
      }
      return response.data;
    } catch (error: any) {}}
}
    ;}
  }
  // 添加健康记录'/;,'/g'/;
const async = addHealthRecord()';,'';
record: Omit<HealthRecord, 'id' | 'timestamp' | 'verified'>';'';
  ): Promise<HealthRecord> {try {';,}const  response: ApiResponse<HealthRecord> = await apiClient.post()';'';
        '/users/me/health-records';'/;,'/g'/;
record;
      );
if (!response.success || !response.data) {}}
}
      }
      return response.data;
    } catch (error: any) {}}
}
    ;}
  }
  // 更新健康记录/;,/g/;
const async = updateHealthRecord();
recordId: string,;
const updates = Partial<HealthRecord>;
  ): Promise<HealthRecord> {try {}}
      const  response: ApiResponse<HealthRecord> = await apiClient.put()}
        `/users/me/health-records/${recordId;}`,```/`;,`/g`/`;
updates;
      );
if (!response.success || !response.data) {}}
}
      }
      return response.data;
    } catch (error: any) {}}
}
    ;}
  }
  // 删除健康记录/;,/g/;
const async = deleteHealthRecord(recordId: string): Promise<void> {}}
    try {}
      const response: ApiResponse = await apiClient.delete(`/users/me/health-records/${recordId;}`);```/`;,`/g`/`;
if (!response.success) {}}
}
      }
    } catch (error: any) {}}
}
    ;}
  }
  // 获取用户统计信息/;,/g/;
const async = getUserStats(): Promise<UserStats> {';,}try {';,}const response: ApiResponse<UserStats> = await apiClient.get('/users/me/stats');'/;,'/g'/;
if (!response.success || !response.data) {}}
}
      }
      return response.data;
    } catch (error: any) {}}
}
    ;}
  }';'';
  // 导出用户数据'/;,'/g'/;
const async = exportUserData(format: 'json' | 'csv' | 'pdf' = 'json'): Promise<Blob> {';}}'';
    try {'}'';
response: await apiClient.get(`/users/me/export?format=${format;}`, {responseType: 'blob';)'}''/`;`/g`/`;
      });
return response as Blob;
    } catch (error: any) {}}
}
    ;}
  }
  // 删除用户账户/;,/g/;
const async = deleteAccount(password: string): Promise<void> {';,}try {';}}'';
      const: response: ApiResponse = await apiClient.delete('/users/me', {')}''/;,'/g'/;
const data = { password ;});
      });
if (!response.success) {}}
}
      }
    } catch (error: any) {}}
}
    ;}
  }
  // 获取用户活动日志/;,/g/;
const async = getActivityLog();
startDate?: string;
endDate?: string;
limit?: number;
offset?: number;
  ): Promise<{ activities: any[]; total: number ;}> {try {';,}const params = new URLSearchParams();';,'';
if (startDate) params.append('startDate', startDate);';,'';
if (endDate) params.append('endDate', endDate);';,'';
if (limit) params.append('limit', limit.toString());';'';
}
      if (offset) params.append('offset', offset.toString());'}'';
const  response: ApiResponse<{ activities: any[]; total: number ;}> = await apiClient.get();
        `/users/me/activity-log?${params.toString()}````/`;`/g`/`;
      );
if (!response.success || !response.data) {}}
}
      }
      return response.data;
    } catch (error: any) {}}
}
    ;}
  }
  // 更新最后活跃时间/;,/g/;
const async = updateLastActive(): Promise<void> {';,}try {';}}'';
      const await = apiClient.post('/users/me/last-active');'}''/;'/g'/;
    } catch (error) {// 静默失败，不影响用户体验/;}}/g/;
}
    }
  }
  // 检查用户名是否可用/;,/g/;
const async = checkUsernameAvailability(username: string): Promise<boolean> {}}
    try {}
      const  response: ApiResponse<{ available: boolean ;}> = await apiClient.get();
        `/users/check-username?username=${encodeURIComponent(username)}````/`;`/g`/`;
      );
if (!response.success) {}}
        return false;}
      }
      return response.data?.available || false;
    } catch (error) {}}
      return false;}
    }
  }
  // 检查邮箱是否可用/;,/g/;
const async = checkEmailAvailability(email: string): Promise<boolean> {}}
    try {}
      const  response: ApiResponse<{ available: boolean ;}> = await apiClient.get();
        `/users/check-email?email=${encodeURIComponent(email)}````/`;`/g`/`;
      );
if (!response.success) {}}
        return false;}
      }
      return response.data?.available || false;
    } catch (error) {}}
      return false;}
    }
  }
}
// 导出单例实例/;,/g/;
export const userService = new UserService();';,'';
export default userService;