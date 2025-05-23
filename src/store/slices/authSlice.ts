import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../index';
import authApi, { LoginRequest, RegisterRequest } from '../../api/authApi';
import { STORAGE_KEYS } from '../../config/constants';
import AsyncStorage from '@react-native-async-storage/async-storage';

// 用户认证类型
export interface User {
  id: string;
  nickname: string;
  avatar: string;
  healthScore: number;
  constitutionType: string;
}

// 认证状态类型
export interface AuthState {
  isAuthenticated: boolean;
  isInitialized: boolean;
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  loading: boolean;
  error: string | null;
}

// 初始状态
const initialState: AuthState = {
  isAuthenticated: false,
  isInitialized: false,
  user: null,
  token: null,
  refreshToken: null,
  loading: false,
  error: null,
};

// 登录异步action
export const login = createAsyncThunk(
  'auth/login',
  async (credentials: LoginRequest, { rejectWithValue }) => {
    try {
      const response = await authApi.login(credentials);
      
      // 保存认证信息到本地存储
      await AsyncStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, response.data.access_token);
      await AsyncStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, response.data.refresh_token);
      await AsyncStorage.setItem(STORAGE_KEYS.USER_INFO, JSON.stringify(response.data.user_info));
      
      return response;
    } catch (error) {
      if (error instanceof Error) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('登录失败，请稍后再试');
    }
  }
);

// 注册异步action
export const register = createAsyncThunk(
  'auth/register',
  async (userData: RegisterRequest, { rejectWithValue }) => {
    try {
      const response = await authApi.register(userData);
      return response;
    } catch (error) {
      if (error instanceof Error) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('注册失败，请稍后再试');
    }
  }
);

// 退出登录异步action
export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { getState }) => {
    try {
      const state = getState() as RootState;
      const token = state.auth.token;

      if (token) {
        await authApi.logout(token);
      }
      
      // 清除本地存储中的认证信息
      await AsyncStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
      await AsyncStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
      await AsyncStorage.removeItem(STORAGE_KEYS.USER_INFO);
      
      return true;
    } catch (error) {
      // 即使API调用失败，我们也要在客户端登出
      return true;
    }
  }
);

// 创建Auth Slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // 清除错误信息
    clearError: (state) => {
      state.error = null;
    },
    // 从本地存储恢复会话
    restoreSession: (state, action: PayloadAction<{
      user: User;
      token: string;
      refreshToken: string;
    }>) => {
      state.isAuthenticated = true;
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.refreshToken = action.payload.refreshToken;
      state.error = null;
    },
    // 更新用户资料
    updateUserProfile: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload };
      }
    },
    setAuthenticated: (state, action) => {
      state.isAuthenticated = action.payload;
    },
    setInitialized: (state, action) => {
      state.isInitialized = action.payload;
    }
  },
  extraReducers: (builder) => {
    builder
      // 登录
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.user = action.payload.data.user_info;
        state.token = action.payload.data.access_token;
        state.refreshToken = action.payload.data.refresh_token;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 注册
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state) => {
        state.loading = false;
        // 注册成功后不自动登录，需要用户主动登录
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 退出登录
      .addCase(logout.pending, (state) => {
        state.loading = true;
      })
      .addCase(logout.fulfilled, (state) => {
        // 重置状态
        return initialState;
      });
  },
});

/**
 * 初始化认证状态：从本地存储加载认证信息
 */
export const initializeAuth = createAsyncThunk(
  'auth/initialize',
  async (_, { dispatch }) => {
    try {
      const token = await AsyncStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
      const refreshToken = await AsyncStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
      const userInfoString = await AsyncStorage.getItem(STORAGE_KEYS.USER_INFO);
      
      if (token && refreshToken && userInfoString) {
        const user = JSON.parse(userInfoString) as User;
        dispatch(restoreSession({ user, token, refreshToken }));
      }
    } catch (error) {
      console.error('Failed to initialize auth:', error);
    }
  }
);

// 导出actions
export const { clearError, restoreSession, updateUserProfile, setAuthenticated, setInitialized } = authSlice.actions;

// 导出reducer
export default authSlice.reducer; 