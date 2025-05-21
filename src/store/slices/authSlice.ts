import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';
import { RootState } from '../index';

// 用户认证类型
export interface User {
  id: string;
  nickname: string;
  avatar: string;
  healthScore: number;
  constitutionType: string;
}

// 认证状态类型
interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  loading: boolean;
  error: string | null;
}

// 初始状态
const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  token: null,
  refreshToken: null,
  loading: false,
  error: null,
};

// 登录异步action
export const login = createAsyncThunk(
  'auth/login',
  async (credentials: { mobile: string; password: string }, { rejectWithValue }) => {
    try {
      // 实际项目中应该调用真实的API
      const response = await axios.post('/api/v1/auth/login', credentials);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        return rejectWithValue(error.response.data);
      }
      return rejectWithValue('登录失败，请稍后再试');
    }
  }
);

// 退出登录异步action
export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { getState, rejectWithValue }) => {
    try {
      const state = getState() as RootState;
      const token = state.auth.token;

      // 实际项目中应该调用真实的API
      await axios.post('/api/v1/auth/logout', {}, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
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

// 导出actions
export const { clearError, restoreSession, updateUserProfile } = authSlice.actions;

// 导出reducer
export default authSlice.reducer; 