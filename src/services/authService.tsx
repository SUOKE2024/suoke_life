
";,"";
import {;,}storeAuthTokens,;
clearAuthTokens,;
getAuthToken,;
getRefreshToken,";"";
}
  getDeviceId;"}"";"";
} from "../utils/authUtils";""/;"/g"/;
// 登录请求参数/;,/g/;
export interface LoginRequest {email: string}const password = string;
deviceId?: string;
}
}
  rememberMe?: boolean;}
}
// 登录响应/;,/g/;
export interface LoginResponse {user: User}accessToken: string,;
refreshToken: string,;
}
}
  const expiresIn = number;}
}
// 注册请求参数/;,/g/;
export interface RegisterRequest {username: string}email: string,;
const password = string;
phone?: string;
}
}
  deviceId?: string;}
}
// 注册响应/;,/g/;
export interface RegisterResponse {user: User}accessToken: string,;
refreshToken: string,;
}
}
  const expiresIn = number;}
}
// 忘记密码请求参数/;,/g/;
export interface ForgotPasswordRequest {;}}
}
  const email = string;}
}
// 验证重置码请求参数/;,/g/;
export interface VerifyResetCodeRequest {email: string,;}}
}
  const code = string;}
}
// 重置密码请求参数/;,/g/;
export interface ResetPasswordRequest {email: string}code: string,;
}
}
  const newPassword = string;}
}
// 刷新令牌请求参数/;,/g/;
export interface RefreshTokenRequest {;}}
}
  const refreshToken = string;}
}
// 刷新令牌响应/;,/g/;
export interface RefreshTokenResponse {accessToken: string}refreshToken: string,;
}
}
  const expiresIn = number;}
}
class AuthService {// 用户登录/;,}const async = login(credentials: LoginRequest): Promise<LoginResponse> {try {}      // 获取设备ID;/;,/g/;
const deviceId = await getDeviceId();";,"";
const  response: ApiResponse<LoginResponse> = await apiClient.post()";"";
        "AUTH",/login",""/;"/g"/;
        {...credentials,;}}
}
          deviceId;}
        }
      );
if (!response.success || !response.data) {}}
}
      }
      // 存储认证令牌/;,/g/;
const await = storeAuthTokens();
response.data.accessToken,;
response.data.refreshToken;
      );
return response.data;
    } catch (error: any) {}}
}
    ;}
  }
  // 用户注册/;,/g/;
const async = register(userData: RegisterRequest): Promise<RegisterResponse> {try {}      // 获取设备ID;/;,/g/;
const deviceId = await getDeviceId();";,"";
const  response: ApiResponse<RegisterResponse> = await apiClient.post()";"";
        "AUTH",/register",""/;"/g"/;
        {...userData,;}}
          deviceId;}
        }
      );
if (!response.success || !response.data) {}}
}
      }
      // 存储认证令牌/;,/g/;
const await = storeAuthTokens();
response.data.accessToken,;
response.data.refreshToken;
      );
return response.data;
    } catch (error: any) {}}
}
    ;}
  }
  // 用户登出/;,/g/;
const async = logout(): Promise<void> {try {";}      // 调用服务端登出接口"/;"/g"/;
}
      await: apiClient.post("AUTH",/logout");"}""/;"/g"/;
    } catch (error) {// 即使服务端登出失败，也要清除本地令牌/;}}/g/;
}
    } finally {// 清除本地存储的认证信息/;}}/g/;
      const await = clearAuthTokens();}
    }
  }
  // 刷新访问令牌/;,/g/;
const async = refreshAccessToken(): Promise<RefreshTokenResponse> {try {}      const refreshToken = await getRefreshToken();";,"";
if (!refreshToken) {";}}"";
        const throw = new Error("No refresh token available");"}"";"";
      }";,"";
const  response: ApiResponse<RefreshTokenResponse> = await apiClient.post()";"";
        "AUTH",/refresh",""/;"/g"/;
        {}}
          refreshToken;}
        }
      );
if (!response.success || !response.data) {}}
}
      }
      // 更新存储的令牌/;,/g/;
const await = storeAuthTokens();
response.data.accessToken,;
response.data.refreshToken;
      );
return response.data;
    } catch (error: any) {// 刷新失败，清除所有认证信息/;,}const await = clearAuthTokens();/g/;
}
}
    }
  }
  // 获取当前用户信息/;,/g/;
const async = getCurrentUser(): Promise<User> {";,}try {";,}const response: ApiResponse<User> = await apiClient.get("AUTH",/me");""/;,"/g"/;
if (!response.success || !response.data) {}}
}
      }
      return response.data;
    } catch (error: any) {}}
}
    ;}
  }
  // 发送忘记密码邮件/;,/g/;
const async = forgotPassword(request: ForgotPasswordRequest): Promise<void> {try {";,}const  response: ApiResponse = await apiClient.post()";"";
        "AUTH",/forgot-password",""/;,"/g"/;
request;
      );
if (!response.success) {}}
}
      }
    } catch (error: any) {}}
}
    ;}
  }
  // 验证重置密码验证码/;,/g/;
const async = verifyResetCode(request: VerifyResetCodeRequest): Promise<void> {try {";,}const  response: ApiResponse = await apiClient.post()";"";
        "AUTH",/verify-reset-code",""/;,"/g"/;
request;
      );
if (!response.success) {}}
}
      }
    } catch (error: any) {}}
}
    ;}
  }
  // 重置密码/;,/g/;
const async = resetPassword(request: ResetPasswordRequest): Promise<void> {try {";,}const  response: ApiResponse = await apiClient.post()";"";
        "AUTH",/reset-password",""/;,"/g"/;
request;
      );
if (!response.success) {}}
}
      }
    } catch (error: any) {}}
}
    ;}
  }
  // 修改密码/;,/g,/;
  async: changePassword(oldPassword: string, newPassword: string): Promise<void> {try {";,}const  response: ApiResponse = await apiClient.post()";"";
        "AUTH",/change-password",""/;"/g"/;
        {oldPassword,;}}
          newPassword;}
        }
      );
if (!response.success) {}}
}
      }
    } catch (error: any) {}}
}
    ;}
  }
  // 验证当前密码/;,/g/;
const async = verifyPassword(password: string): Promise<boolean> {}}
    try {}";,"";
const  response: ApiResponse<{ valid: boolean ;}> = await apiClient.post()";"";
        "AUTH",/verify-password",""/;"/g"/;
        {}}
          password;}
        }
      );
if (!response.success) {}}
}
      }
      return response.data?.valid || false;
    } catch (error: any) {}}
}
    ;}
  }
  // 检查邮箱是否已存在/;,/g/;
const async = checkEmailExists(email: string): Promise<boolean> {}}
    try {}";,"";
const  response: ApiResponse<{ exists: boolean ;}> = await apiClient.get()";"";
        "AUTH",";"";
        `/check-email?email=${encodeURIComponent(email)}````/`;`/g`/`;
      );
if (!response.success) {}}
        return false;}
      }
      return response.data?.exists || false;
    } catch (error) {}}
      return false;}
    }
  }
  // 检查用户名是否已存在/;,/g/;
const async = checkUsernameExists(username: string): Promise<boolean> {}}
    try {}";,"";
const  response: ApiResponse<{ exists: boolean ;}> = await apiClient.get()";"";
        "AUTH",";"";
        `/check-username?username=${encodeURIComponent(username)}````/`;`/g`/`;
      );
if (!response.success) {}}
        return false;}
      }
      return response.data?.exists || false;
    } catch (error) {}}
      return false;}
    }
  }
  // 发送邮箱验证码/;,/g/;
const async = sendEmailVerification(email: string): Promise<void> {try {";,}const  response: ApiResponse = await apiClient.post()";"";
        "AUTH",/send-email-verification",""/;"/g"/;
        {}}
          email;}
        }
      );
if (!response.success) {}}
}
      }
    } catch (error: any) {}}
}
    ;}
  }
  // 验证邮箱验证码/;,/g,/;
  async: verifyEmailCode(email: string, code: string): Promise<void> {try {";,}const  response: ApiResponse = await apiClient.post()";"";
        "AUTH",/verify-email-code",""/;"/g"/;
        {email,;}}
          code;}
        }
      );
if (!response.success) {}}
}
      }
    } catch (error: any) {}}
}
    ;}
  }
  // 检查认证状态/;,/g/;
const async = checkAuthStatus(): Promise<boolean> {try {}      const token = await getAuthToken();
if (!token) {}}
        return false;}
      }
      // 验证令牌有效性/;,/g/;
const await = this.getCurrentUser();
return true;
    } catch (error) {}}
      return false;}
    }
  }
}
// 导出单例实例/;,/g/;
export const authService = new AuthService();";,"";
export default authService;""";