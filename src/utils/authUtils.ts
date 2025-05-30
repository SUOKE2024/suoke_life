import AsyncStorage from "@react-native-async-storage/async-storage";
import { STORAGE_CONFIG } from "../constants/config";

// 邮箱验证正则表达式
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// 手机号验证正则表达式（中国大陆）
const PHONE_REGEX = /^1[3-9]\d{9}$/;

// 密码强度正则表达式
const PASSWORD_REGEX = {
  // 至少包含字母和数字
  BASIC: /^(?=.*[a-zA-Z])(?=.*\d).{6,}$/,
  // 包含大小写字母、数字和特殊字符
  STRONG:
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
};

// 验证邮箱格式
export const validateEmail = (email: string): boolean => {
  return EMAIL_REGEX.test(email.trim());
};

// 验证手机号格式
export const validatePhone = (phone: string): boolean => {
  return PHONE_REGEX.test(phone.trim());
};

// 验证密码强度
export const validatePassword = (
  password: string,
  level: "basic" | "strong" = "basic"
): boolean => {
  if (level === "strong") {
    return PASSWORD_REGEX.STRONG.test(password);
  }
  return PASSWORD_REGEX.BASIC.test(password);
};

// 获取密码强度等级
export const getPasswordStrength = (
  password: string
): "weak" | "medium" | "strong" => {
  if (password.length < 6) {
    return "weak";
  }

  let score = 0;

  // 长度检查
  if (password.length >= 8) {
    score += 1;
  }
  if (password.length >= 12) {
    score += 1;
  }

  // 字符类型检查
  if (/[a-z]/.test(password)) {
    score += 1;
  }
  if (/[A-Z]/.test(password)) {
    score += 1;
  }
  if (/\d/.test(password)) {
    score += 1;
  }
  if (/[@$!%*?&]/.test(password)) {
    score += 1;
  }

  if (score <= 2) {
    return "weak";
  }
  if (score <= 4) {
    return "medium";
  }
  return "strong";
};

// 验证用户名
export const validateUsername = (username: string): boolean => {
  const trimmed = username.trim();
  return trimmed.length >= 2 && trimmed.length <= 20;
};

// 验证验证码
export const validateVerificationCode = (
  code: string,
  length: number = 6
): boolean => {
  const trimmed = code.trim();
  return trimmed.length === length && /^\d+$/.test(trimmed);
};

// 登录表单验证
export interface LoginFormData {
  email: string;
  password: string;
}

export interface LoginFormErrors {
  email?: string;
  password?: string;
}

export const validateLoginForm = (data: LoginFormData): LoginFormErrors => {
  const errors: LoginFormErrors = {};

  if (!data.email.trim()) {
    errors.email = "请输入邮箱";
  } else if (!validateEmail(data.email)) {
    errors.email = "请输入有效的邮箱地址";
  }

  if (!data.password) {
    errors.password = "请输入密码";
  } else if (data.password.length < 6) {
    errors.password = "密码至少6个字符";
  }

  return errors;
};

// 注册表单验证
export interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  phone?: string;
}

export interface RegisterFormErrors {
  username?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  phone?: string;
}

export const validateRegisterForm = (
  data: RegisterFormData
): RegisterFormErrors => {
  const errors: RegisterFormErrors = {};

  // 用户名验证
  if (!data.username.trim()) {
    errors.username = "请输入用户名";
  } else if (!validateUsername(data.username)) {
    errors.username = "用户名长度应为2-20个字符";
  }

  // 邮箱验证
  if (!data.email.trim()) {
    errors.email = "请输入邮箱";
  } else if (!validateEmail(data.email)) {
    errors.email = "请输入有效的邮箱地址";
  }

  // 密码验证
  if (!data.password) {
    errors.password = "请输入密码";
  } else if (!validatePassword(data.password)) {
    errors.password = "密码必须包含字母和数字，至少6个字符";
  }

  // 确认密码验证
  if (!data.confirmPassword) {
    errors.confirmPassword = "请确认密码";
  } else if (data.password !== data.confirmPassword) {
    errors.confirmPassword = "两次输入的密码不一致";
  }

  // 手机号验证（可选）
  if (data.phone && data.phone.trim()) {
    if (!validatePhone(data.phone)) {
      errors.phone = "请输入有效的手机号";
    }
  }

  return errors;
};

// 忘记密码表单验证
export interface ForgotPasswordFormData {
  email: string;
  verificationCode?: string;
  newPassword?: string;
  confirmPassword?: string;
}

export interface ForgotPasswordFormErrors {
  email?: string;
  verificationCode?: string;
  newPassword?: string;
  confirmPassword?: string;
}

export const validateForgotPasswordForm = (
  data: ForgotPasswordFormData,
  step: "email" | "verification" | "reset"
): ForgotPasswordFormErrors => {
  const errors: ForgotPasswordFormErrors = {};

  if (step === "email") {
    if (!data.email.trim()) {
      errors.email = "请输入邮箱";
    } else if (!validateEmail(data.email)) {
      errors.email = "请输入有效的邮箱地址";
    }
  }

  if (step === "verification") {
    if (!data.verificationCode?.trim()) {
      errors.verificationCode = "请输入验证码";
    } else if (!validateVerificationCode(data.verificationCode)) {
      errors.verificationCode = "验证码应为6位数字";
    }
  }

  if (step === "reset") {
    if (!data.newPassword) {
      errors.newPassword = "请输入新密码";
    } else if (!validatePassword(data.newPassword)) {
      errors.newPassword = "密码必须包含字母和数字，至少6个字符";
    }

    if (!data.confirmPassword) {
      errors.confirmPassword = "请确认新密码";
    } else if (data.newPassword !== data.confirmPassword) {
      errors.confirmPassword = "两次输入的密码不一致";
    }
  }

  return errors;
};

// 存储认证令牌
export const storeAuthTokens = async (
  token: string,
  refreshToken?: string
): Promise<void> => {
  try {
    await AsyncStorage.setItem(STORAGE_CONFIG.KEYS.AUTH_TOKEN, token);
    if (refreshToken) {
      await AsyncStorage.setItem(
        STORAGE_CONFIG.KEYS.REFRESH_TOKEN,
        refreshToken
      );
    }
  } catch (error) {
    console.error("Failed to store auth tokens:", error);
    throw new Error("存储认证信息失败");
  }
};

// 获取认证令牌
export const getAuthToken = async (): Promise<string | null> => {
  try {
    return await AsyncStorage.getItem(STORAGE_CONFIG.KEYS.AUTH_TOKEN);
  } catch (error) {
    console.error("Failed to get auth token:", error);
    return null;
  }
};

// 获取刷新令牌
export const getRefreshToken = async (): Promise<string | null> => {
  try {
    return await AsyncStorage.getItem(STORAGE_CONFIG.KEYS.REFRESH_TOKEN);
  } catch (error) {
    console.error("Failed to get refresh token:", error);
    return null;
  }
};

// 清除认证令牌
export const clearAuthTokens = async (): Promise<void> => {
  try {
    await AsyncStorage.multiRemove([
      STORAGE_CONFIG.KEYS.AUTH_TOKEN,
      STORAGE_CONFIG.KEYS.REFRESH_TOKEN,
      STORAGE_CONFIG.KEYS.USER_ID,
    ]);
  } catch (error) {
    console.error("Failed to clear auth tokens:", error);
    throw new Error("清除认证信息失败");
  }
};

// 检查是否已登录
export const isAuthenticated = async (): Promise<boolean> => {
  try {
    const token = await getAuthToken();
    return !!token;
  } catch (error) {
    console.error("Failed to check authentication status:", error);
    return false;
  }
};

// 格式化错误消息
export const formatAuthError = (error: any): string => {
  if (typeof error === "string") {
    return error;
  }

  if (error?.message) {
    return error.message;
  }

  if (error?.error?.message) {
    return error.error.message;
  }

  return "操作失败，请稍后重试";
};

// 生成随机设备ID
export const generateDeviceId = (): string => {
  const chars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let result = "";
  for (let i = 0; i < 32; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
};

// 存储设备ID
export const storeDeviceId = async (): Promise<string> => {
  try {
    let deviceId = await AsyncStorage.getItem(STORAGE_CONFIG.KEYS.DEVICE_ID);
    if (!deviceId) {
      deviceId = generateDeviceId();
      await AsyncStorage.setItem(STORAGE_CONFIG.KEYS.DEVICE_ID, deviceId);
    }
    return deviceId;
  } catch (error) {
    console.error("Failed to store device ID:", error);
    return generateDeviceId();
  }
};

// 获取设备ID
export const getDeviceId = async (): Promise<string> => {
  try {
    const deviceId = await AsyncStorage.getItem(STORAGE_CONFIG.KEYS.DEVICE_ID);
    return deviceId || (await storeDeviceId());
  } catch (error) {
    console.error("Failed to get device ID:", error);
    return generateDeviceId();
  }
};
