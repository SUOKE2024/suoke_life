import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { AuthState, User, ApiResponse } from "../../types";
import { apiClient } from "../../services/apiClient";
import { STORAGE_CONFIG } from "../../constants/config";



// 登录请求参数
interface LoginRequest {
  email: string;
  password: string;
}

// 注册请求参数
interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  phone?: string;
}

// 登录响应
interface LoginResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
}

// 初始状态
const initialState: AuthState = {
  isAuthenticated: false,
  user: undefined,
  token: undefined,
  refreshToken: undefined,
  loading: false,
  error: undefined,
};

// 异步thunk actions
export const login = createAsyncThunk<
  { user: User; token: string; refreshToken: string },
  LoginRequest,
  { rejectValue: string }
>("auth/login", async (credentials, { rejectWithValue }) => {
  try {
    const response: ApiResponse<LoginResponse> = await apiClient.post(
      "/auth/login",
      credentials
    );

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || "登录失败");
    }

    // 存储令牌到本地存储
    await AsyncStorage.setItem(
      STORAGE_CONFIG.KEYS.AUTH_TOKEN,
      response.data.accessToken
    );
    await AsyncStorage.setItem(
      STORAGE_CONFIG.KEYS.REFRESH_TOKEN,
      response.data.refreshToken
    );
    await AsyncStorage.setItem(
      STORAGE_CONFIG.KEYS.USER_ID,
      response.data.user.id
    );

    return {
      user: response.data.user,
      token: response.data.accessToken,
      refreshToken: response.data.refreshToken,
    };
  } catch (error: any) {
    return rejectWithValue(error.message || "登录失败");
  }
});

export const register = createAsyncThunk<
  { user: User; token: string; refreshToken: string },
  RegisterRequest,
  { rejectValue: string }
>("auth/register", async (userData, { rejectWithValue }) => {
  try {
    const response: ApiResponse<LoginResponse> = await apiClient.post(
      "/auth/register",
      userData
    );

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || "注册失败");
    }

    // 存储令牌到本地存储
    await AsyncStorage.setItem(
      STORAGE_CONFIG.KEYS.AUTH_TOKEN,
      response.data.accessToken
    );
    await AsyncStorage.setItem(
      STORAGE_CONFIG.KEYS.REFRESH_TOKEN,
      response.data.refreshToken
    );
    await AsyncStorage.setItem(
      STORAGE_CONFIG.KEYS.USER_ID,
      response.data.user.id
    );

    return {
      user: response.data.user,
      token: response.data.accessToken,
      refreshToken: response.data.refreshToken,
    };
  } catch (error: any) {
    return rejectWithValue(error.message || "注册失败");
  }
});

export const logout = createAsyncThunk<void, void, { rejectValue: string }>(
  "auth/logout",
  async () => {
    try {
      // 调用服务端登出接口
      await apiClient.post("/auth/logout");
    } catch (error) {
      // 即使服务端登出失败，也要清除本地令牌
      console.warn("Server logout failed:", error);
    } finally {
      // 清除本地存储
      await AsyncStorage.multiRemove([
        STORAGE_CONFIG.KEYS.AUTH_TOKEN,
        STORAGE_CONFIG.KEYS.REFRESH_TOKEN,
        STORAGE_CONFIG.KEYS.USER_ID,
      ]);
    }
  }
);

export const refreshToken = createAsyncThunk<
  { token: string; refreshToken: string },
  string,
  { rejectValue: string }
>("auth/refreshToken", async (refreshTokenValue, { rejectWithValue }) => {
  try {
    const response: ApiResponse<{ accessToken: string; refreshToken: string }> =
      await apiClient.post("/auth/refresh", {
        refreshToken: refreshTokenValue,
      });

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || "刷新令牌失败");
    }

    // 更新本地存储
    await AsyncStorage.setItem(
      STORAGE_CONFIG.KEYS.AUTH_TOKEN,
      response.data.accessToken
    );
    await AsyncStorage.setItem(
      STORAGE_CONFIG.KEYS.REFRESH_TOKEN,
      response.data.refreshToken
    );

    return {
      token: response.data.accessToken,
      refreshToken: response.data.refreshToken,
    };
  } catch (error: any) {
    return rejectWithValue(error.message || "刷新令牌失败");
  }
});

export const checkAuthStatus = createAsyncThunk<
  User,
  void,
  { rejectValue: string }
>("auth/checkStatus", async (_, { rejectWithValue }) => {
  try {
    // 检查本地存储的token
    const token = await AsyncStorage.getItem(STORAGE_CONFIG.KEYS.AUTH_TOKEN);
    if (!token) {
      throw new Error("No token found");
    }

    // 验证token有效性
    const response: ApiResponse<User> = await apiClient.get("/auth/me");

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || "验证失败");
    }

    return response.data;
  } catch (error: any) {
    // 清除无效的认证信息
    await AsyncStorage.multiRemove([
      STORAGE_CONFIG.KEYS.AUTH_TOKEN,
      STORAGE_CONFIG.KEYS.REFRESH_TOKEN,
      STORAGE_CONFIG.KEYS.USER_ID,
    ]);
    return rejectWithValue(error.message || "验证失败");
  }
});

export const forgotPassword = createAsyncThunk<
  void,
  string,
  { rejectValue: string }
>("auth/forgotPassword", async (email, { rejectWithValue }) => {
  try {
    const response: ApiResponse = await apiClient.post(
      "/auth/forgot-password",
      { email }
    );

    if (!response.success) {
      throw new Error(response.error?.message || "发送失败");
    }
  } catch (error: any) {
    return rejectWithValue(error.message || "发送失败");
  }
});

export const verifyResetCode = createAsyncThunk<
  void,
  { email: string; code: string },
  { rejectValue: string }
>("auth/verifyResetCode", async ({ email, code }, { rejectWithValue }) => {
  try {
    const response: ApiResponse = await apiClient.post(
      "/auth/verify-reset-code",
      { email, code }
    );

    if (!response.success) {
      throw new Error(response.error?.message || "验证失败");
    }
  } catch (error: any) {
    return rejectWithValue(error.message || "验证失败");
  }
});

export const resetPassword = createAsyncThunk<
  void,
  { email: string; code: string; newPassword: string },
  { rejectValue: string }
>(
  "auth/resetPassword",
  async ({ email, code, newPassword }, { rejectWithValue }) => {
    try {
      const response: ApiResponse = await apiClient.post(
        "/auth/reset-password",
        {
          email,
          code,
          newPassword,
        }
      );

      if (!response.success) {
        throw new Error(response.error?.message || "重置失败");
      }
    } catch (error: any) {
      return rejectWithValue(error.message || "重置失败");
    }
  }
);

// 创建slice
const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = undefined;
    },
    clearAuth: (state) => {
      state.isAuthenticated = false;
      state.user = undefined;
      state.token = undefined;
      state.refreshToken = undefined;
      state.error = undefined;
    },
    updateUser: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload };
      }
    },
    // 开发者模式 - 快速登录（用于测试）
    devLogin: (state) => {
      state.isAuthenticated = true;
      state.user = {
        id: "dev-user-001",
        username: "测试用户",
        email: "test@suokelife.com",
        phone: "13800138000",
        avatar: "",
        profile: {
          name: "测试用户",
          age: 30,
          gender: "other",
          height: 170,
          weight: 65,
          constitution: "balanced",
          medicalHistory: [],
          allergies: [],
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      state.token = "dev-token-123456";
      state.refreshToken = "dev-refresh-token-123456";
      state.loading = false;
      state.error = undefined;
    },
  },
  extraReducers: (builder) => {
    // 登录
    builder
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.refreshToken = action.payload.refreshToken;
        state.error = undefined;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.isAuthenticated = false;
        state.error = action.payload;
      });

    // 注册
    builder
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(register.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.refreshToken = action.payload.refreshToken;
        state.error = undefined;
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.isAuthenticated = false;
        state.error = action.payload;
      });

    // 退出登录
    builder
      .addCase(logout.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(logout.fulfilled, (state) => {
        state.loading = false;
        state.isAuthenticated = false;
        state.user = undefined;
        state.token = undefined;
        state.refreshToken = undefined;
        state.error = undefined;
      })
      .addCase(logout.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    // 刷新令牌
    builder
      .addCase(refreshToken.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(refreshToken.fulfilled, (state, action) => {
        state.loading = false;
        state.token = action.payload.token;
        state.refreshToken = action.payload.refreshToken;
        state.error = undefined;
      })
      .addCase(refreshToken.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    // 检查认证状态
    builder
      .addCase(checkAuthStatus.pending, (state) => {
        state.loading = true;
      })
      .addCase(checkAuthStatus.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.user = action.payload;
        state.error = undefined;
      })
      .addCase(checkAuthStatus.rejected, (state, action) => {
        state.loading = false;
        state.isAuthenticated = false;
        state.user = undefined;
        state.token = undefined;
        state.refreshToken = undefined;
        state.error = action.payload;
      });

    // 忘记密码相关actions不需要更新状态，只处理loading和error
    builder
      .addCase(forgotPassword.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(forgotPassword.fulfilled, (state) => {
        state.loading = false;
        state.error = undefined;
      })
      .addCase(forgotPassword.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    builder
      .addCase(verifyResetCode.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(verifyResetCode.fulfilled, (state) => {
        state.loading = false;
        state.error = undefined;
      })
      .addCase(verifyResetCode.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    builder
      .addCase(resetPassword.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(resetPassword.fulfilled, (state) => {
        state.loading = false;
        state.error = undefined;
      })
      .addCase(resetPassword.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

// 导出actions
export const { clearError, clearAuth, updateUser, devLogin } =
  authSlice.actions;

// 选择器
export const selectAuth = (state: { auth: AuthState }) => state.auth;
export const selectIsAuthenticated = (state: { auth: AuthState }) =>
  state.auth.isAuthenticated;
export const selectUser = (state: { auth: AuthState }) => state.auth.user;
export const selectAuthLoading = (state: { auth: AuthState }) =>
  state.auth.loading;
export const selectAuthError = (state: { auth: AuthState }) => state.auth.error;

// 导出reducer
export default authSlice.reducer;
