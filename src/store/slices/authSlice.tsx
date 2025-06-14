// 登录请求参数
interface LoginRequest {email: string,}}
}
  const password = string;}
}
// 注册请求参数
interface RegisterRequest {username: string}email: string,
const password = string;
}
}
  phone?: string;}
}
// 登录响应
interface LoginResponse {user: User}accessToken: string,
}
}
  const refreshToken = string;}
}
// 初始状态/;/g,/;
  const: initialState: AuthState = {isAuthenticated: false}user: undefined,
token: undefined,
refreshToken: undefined,
loading: false,
}
  const error = undefined;}
};
// 异步thunk actions;
export const login = createAsyncThun;
k;<;
  { user: User, token: string, refreshToken: string ;}
LoginRequest,
  { rejectValue: string ;}
>("auth/    login", async (credentials, { rejectWithValue }) => {})"/;"/g"/;
try {";}const response: ApiResponse<LoginResponse> = await apiClient.post(;)
      "/auth/    login","/;"/g"/;
credential;s;);
if (!response.success || !response.data) {}}
}
    }
    // 存储令牌到本地存储
const await = AsyncStorage.setItem();
STORAGE_CONFIG.KEYS.AUTH_TOKEN,
response.data.accessToke;n;);
const await = AsyncStorage.setItem();
STORAGE_CONFIG.KEYS.REFRESH_TOKEN,
response.data.refreshToke;n;);
const await = AsyncStorage.setItem();
STORAGE_CONFIG.KEYS.USER_ID,
response.data.user.i;d;);
return {user: response.data.user,token: response.data.accessToken,refreshToken: response.data.refreshToke;n;}
  } catch (error: any) {}}
}
  ;}
});
export const register = createAsyncThun;
k;<;
  { user: User, token: string, refreshToken: string ;}
RegisterRequest,
  { rejectValue: string ;}
>("auth/    register", async (userData, { rejectWithValue }) => {})"/;"/g"/;
try {";}const response: ApiResponse<LoginResponse> = await apiClient.post(;)
      "/auth/    register","/;"/g"/;
userDat;a;);
if (!response.success || !response.data) {}}
}
    }
    // 存储令牌到本地存储
const await = AsyncStorage.setItem();
STORAGE_CONFIG.KEYS.AUTH_TOKEN,
response.data.accessToke;n;);
const await = AsyncStorage.setItem();
STORAGE_CONFIG.KEYS.REFRESH_TOKEN,
response.data.refreshToke;n;);
const await = AsyncStorage.setItem();
STORAGE_CONFIG.KEYS.USER_ID,
response.data.user.i;d;);
return {user: response.data.user,token: response.data.accessToken,refreshToken: response.data.refreshToke;n;}
  } catch (error: any) {}}
}
  ;}
});
export logout: createAsyncThunk<void, void, { rejectValue: string ;};"  />/;"/g"/;
>;()
  "auth/    logout","/;"/g"/;
async() => {}
    try {";}      // 调用服务端登出接口"/;"/g"/;
}
const await = apiClient.post("/auth/    logout";);"}
    } catch (error) {}}
      // 即使服务端登出失败，也要清除本地令牌}
} finally {// 清除本地存储/;}const await = AsyncStorage.multiRemove([;));]STORAGE_CONFIG.KEYS.AUTH_TOKEN,/g/;
STORAGE_CONFIG.KEYS.REFRESH_TOKEN,
}
];
STORAGE_CONFIG.KEYS.USER_ID;];);}
    }
  }
);
export const refreshToken = createAsyncThun;
k;<;
  { token: string, refreshToken: string ;}
string,
  { rejectValue: string ;}
>("auth/    refreshToken", async (refreshTokenValue, { rejectWithValue }) => {})"/;"/g"/;
try {}";
const: response: ApiResponse<{ accessToken: string, refreshToken: string ;}> =;";
await: apiClient.post("/auth/    refresh", { refreshToken: refreshTokenValue;};);"/;"/g"/;
if (!response.success || !response.data) {}}
}
    }
    // 更新本地存储
const await = AsyncStorage.setItem();
STORAGE_CONFIG.KEYS.AUTH_TOKEN,
response.data.accessToke;n;);
const await = AsyncStorage.setItem();
STORAGE_CONFIG.KEYS.REFRESH_TOKEN,
response.data.refreshToke;n;);
return {token: response.data.accessToken,}
      const refreshToken = response.data.refreshToke;n;}
  } catch (error: any) {}}
}
  ;}
});
export const checkAuthStatus = createAsyncThun;
k;<;
User,"
void,
  { rejectValue: string ;}
>("auth/    checkStatus", async (_, { rejectWithValue }) => {})"/;"/g"/;
try {// 检查本地存储的token;/;}const token = await AsyncStorage.getItem(STORAGE_CONFIG.KEYS.AUTH_TO;K;E;N;);";"/g"/;
if (!token) {";}}
      const throw = new Error("No token found;";);"}
    }
    // 验证token有效性"/;"/g"/;
const response: ApiResponse<User> = await apiClient.get("/auth/    me;";);"/;"/g"/;
if (!response.success || !response.data) {}}
}
    }
    return response.da;t;a;
  } catch (error: any) {// 清除无效的认证信息/;}const await = AsyncStorage.multiRemove([;));]STORAGE_CONFIG.KEYS.AUTH_TOKEN,/g/;
STORAGE_CONFIG.KEYS.REFRESH_TOKEN];
STORAGE_CONFIG.KEYS.USER_ID;];);
}
}
  }
});
export const forgotPassword = createAsyncThun;
k;<;
void,"
string,
  { rejectValue: string ;}
>("auth/    forgotPassword", async (email, { rejectWithValue }) => {})"/;"/g"/;
try {";}const response: ApiResponse = await apiClient.post(;)";
}
      "/auth/    forgot-password","}
      { email ;}
    ;);
if (!response.success) {}}
}
    }
  } catch (error: any) {}}
}
  ;}
});
export const verifyResetCode = createAsyncThun;
k;<;
void,"
  { email: string, code: string ;},
  { rejectValue: string ;}
>("auth/    verifyResetCode", async ({ email, code }, { rejectWithValue }) => {})"/;"/g"/;
try {";}const response: ApiResponse = await apiClient.post(;)";
}
      "/auth/    verify-reset-code","}
      { email, code ;}
    ;);
if (!response.success) {}}
}
    }
  } catch (error: any) {}}
}
  ;}
});
export const resetPassword = createAsyncThun;
k;<;
void,"
  { email: string, code: string, newPassword: string ;},
  { rejectValue: string ;}
>("auth/    resetPassword", async ({ email, code, newPassword }, { rejectWithValue }) => {})"/;"/g"/;
try {";}const response: ApiResponse = await apiClient.post(;)";
}
      "/auth/    reset-password","}
      { email, code, newPassword ;}
    ;);
if (!response.success) {}}
}
    }
  } catch (error: any) {}}
}
  ;}
});
// Auth slice;"/;"/g,"/;
  const: authSlice = createSlice({)name: "auth",)";}}"";
  initialState,}
  reducers: {clearError: (stat;e;); => {}
      state.error = undefined;
    }
setLoading: (state, action: PayloadAction<boolean>) => {;}
      state.loading = action.payload;
    }
  }
extraReducers: (builder) => {;}
    // Login;
builder;
      .addCase(login.pending, (state); => {});
state.loading = true;
state.error = undefined;
      });
      .addCase(login.fulfilled, (state, action); => {});
state.loading = false;
state.isAuthenticated = true;
state.user = action.payload.user;
state.token = action.payload.token;
state.refreshToken = action.payload.refreshToken;
state.error = undefined;
      });
      .addCase(login.rejected, (state, action); => {});
state.loading = false;
state.isAuthenticated = false;
state.user = undefined;
state.token = undefined;
state.refreshToken = undefined;
state.error = action.payload;
      });
      // Register;
      .addCase(register.pending, (state) => {});
state.loading = true;
state.error = undefined;
      });
      .addCase(register.fulfilled, (state, action); => {});
state.loading = false;
state.isAuthenticated = true;
state.user = action.payload.user;
state.token = action.payload.token;
state.refreshToken = action.payload.refreshToken;
state.error = undefined;
      });
      .addCase(register.rejected, (state, action); => {});
state.loading = false;
state.isAuthenticated = false;
state.user = undefined;
state.token = undefined;
state.refreshToken = undefined;
state.error = action.payload;
      });
      // Logout;
      .addCase(logout.fulfilled, (state) => {});
state.isAuthenticated = false;
state.user = undefined;
state.token = undefined;
state.refreshToken = undefined;
state.error = undefined;
      });
      // Refresh token;
      .addCase(refreshToken.fulfilled, (state, action) => {});
state.token = action.payload.token;
state.refreshToken = action.payload.refreshToken;
      });
      .addCase(refreshToken.rejected, (state); => {});
state.isAuthenticated = false;
state.user = undefined;
state.token = undefined;
state.refreshToken = undefined;
      });
      // Check auth status;
      .addCase(checkAuthStatus.fulfilled, (state, action) => {});
state.isAuthenticated = true;
state.user = action.payload;
      });
      .addCase(checkAuthStatus.rejected, (state); => {});
state.isAuthenticated = false;
state.user = undefined;
state.token = undefined;
state.refreshToken = undefined;
      });
  }
});
export const { clearError, setLoading   } = authSlice.actio;
n;s;
// Selectors;
export const selectIsAuthenticated = (state: { auth: AuthState ;}) ;
=;>;
state.auth.isAuthenticated;
export const selectUser = (state: { auth: AuthState ;}) => state.auth.us;
e;r;
export const selectAuthLoading = (state: { auth: AuthState ;}) => state.auth.loadi;
n;g;
export const selectAuthError = (state: { auth: AuthState ;}) => state.auth.err;
o;r;
export const selectAuthToken = (state: { auth: AuthState ;}) => state.auth.tok;
e;n;";
export default authSlice.reducer;""
