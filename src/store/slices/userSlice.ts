import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { API_URL, STORAGE_KEYS } from '../../config/constants';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// 用户相关接口定义
export interface User {
  id: string;
  mobile: string;
  username: string;
  avatar?: string;
  email?: string;
  bio?: string;
  createTime: number;
  lastLoginTime: number;
}

export interface UserProfile {
  id: string;
  userId: string;
  age?: number;
  gender?: string;
  height?: number;
  weight?: number;
  bloodType?: string;
  medicalHistory?: string[];
  allergies?: string[];
  lastUpdateTime: number;
}

// 登录请求接口
export interface LoginRequest {
  mobile: string;
  password: string;
}

// 注册请求接口
export interface RegisterRequest {
  mobile: string;
  password: string;
  confirmPassword: string;
  username?: string;
  verificationCode: string;
}

// 重置密码请求接口
export interface ResetPasswordRequest {
  mobile: string;
  verificationCode: string;
  newPassword?: string;
}

export interface UserState {
  currentUser: User | null;
  profile: UserProfile | null;
  isLoading: boolean;
  error: string | null;
}

// 初始状态
const initialState: UserState = {
  currentUser: null,
  profile: null,
  isLoading: false,
  error: null
};

// 异步登录
export const login = createAsyncThunk('user/login', async (credentials: LoginRequest, { rejectWithValue }) => {
  try {
    const response = await axios.post(`${API_URL}/auth/login`, credentials);
    
    if (response.data.success) {
      const { token, user } = response.data.data;
      // 保存token
      await AsyncStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
      
      // 保存用户信息
      await AsyncStorage.setItem(STORAGE_KEYS.USER_INFO, JSON.stringify(user));
      
      return user;
    }
    
    return rejectWithValue(response.data.message || '登录失败');
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.message || '服务器错误');
  }
});

// 异步注册
export const register = createAsyncThunk('user/register', async (data: RegisterRequest, { rejectWithValue }) => {
  try {
    const response = await axios.post(`${API_URL}/auth/register`, data);
    
    if (response.data.success) {
      return response.data.data;
    }
    
    return rejectWithValue(response.data.message || '注册失败');
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.message || '服务器错误');
  }
});

// 获取用户个人资料
export const fetchUserProfile = createAsyncThunk('user/fetchProfile', async (userId: string, { rejectWithValue }) => {
  try {
    const response = await axios.get(`${API_URL}/users/${userId}/profile`);
    
    if (response.data.success) {
      return response.data.data;
    }
    
    return rejectWithValue(response.data.message || '获取个人资料失败');
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.message || '服务器错误');
  }
});

// 更新用户个人资料
export const updateUserProfile = createAsyncThunk('user/updateProfile', 
  async (profileData: Partial<UserProfile>, { rejectWithValue, getState }) => {
    try {
      const state = getState() as { user: UserState };
      const userId = state.user.currentUser?.id;
      
      if (!userId) {
        return rejectWithValue('用户未登录');
      }
      
      const response = await axios.put(`${API_URL}/users/${userId}/profile`, profileData);
      
      if (response.data.success) {
        return response.data.data;
      }
      
      return rejectWithValue(response.data.message || '更新个人资料失败');
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || '服务器错误');
    }
});

// 初始化认证状态
export const initializeAuth = createAsyncThunk('user/initializeAuth', async (_, { dispatch }) => {
  try {
    const token = await AsyncStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
    const userJson = await AsyncStorage.getItem(STORAGE_KEYS.USER_INFO);
    
    if (token && userJson) {
      try {
        const user = JSON.parse(userJson) as User;
        
        // 设置axios默认请求头
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        
        // 加载用户个人资料（使用尝试-捕获以避免阻止加载）
        try {
          dispatch(fetchUserProfile(user.id));
        } catch (profileError) {
          console.error('获取用户档案失败:', profileError);
          // 继续流程，不阻塞启动
        }
        
        return user;
      } catch (parseError) {
        console.error('解析用户数据失败:', parseError);
        // 清除无效数据
        await AsyncStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
        await AsyncStorage.removeItem(STORAGE_KEYS.USER_INFO);
        return null;
      }
    }
    
    return null;
  } catch (error) {
    console.error('初始化认证时出错:', error);
    return null;
  }
});

// 登出
export const logout = createAsyncThunk('user/logout', async () => {
  await AsyncStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
  await AsyncStorage.removeItem(STORAGE_KEYS.USER_INFO);
  
  // 清除请求头
  delete axios.defaults.headers.common['Authorization'];
  
  return null;
});

// 请求重置密码
export const requestPasswordReset = createAsyncThunk(
  'user/requestPasswordReset', 
  async (data: ResetPasswordRequest, { rejectWithValue }) => {
    try {
      const response = await axios.post(`${API_URL}/auth/reset-password-request`, data);
      
      if (response.data.success) {
        return response.data.data;
      }
      
      return rejectWithValue(response.data.message || '重置密码请求失败');
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || '服务器错误');
    }
  }
);

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<User>) => {
      state.currentUser = action.payload;
    },
    clearUser: (state) => {
      state.currentUser = null;
      state.profile = null;
    },
    clearError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // 登录
      .addCase(login.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentUser = action.payload;
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // 注册
      .addCase(register.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state) => {
        state.isLoading = false;
      })
      .addCase(register.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // 获取用户个人资料
      .addCase(fetchUserProfile.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchUserProfile.fulfilled, (state, action) => {
        state.isLoading = false;
        state.profile = action.payload;
      })
      .addCase(fetchUserProfile.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // 更新用户个人资料
      .addCase(updateUserProfile.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(updateUserProfile.fulfilled, (state, action) => {
        state.isLoading = false;
        state.profile = action.payload;
      })
      .addCase(updateUserProfile.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // 初始化认证状态
      .addCase(initializeAuth.fulfilled, (state, action) => {
        state.currentUser = action.payload;
      })
      
      // 登出
      .addCase(logout.fulfilled, (state) => {
        state.currentUser = null;
        state.profile = null;
      })
      
      // 请求重置密码
      .addCase(requestPasswordReset.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(requestPasswordReset.fulfilled, (state) => {
        state.isLoading = false;
      })
      .addCase(requestPasswordReset.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  }
});

export const { setUser, clearUser, clearError } = userSlice.actions;
export default userSlice.reducer;