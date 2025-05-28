# 索克生活 - 认证流程指南

## 概述

索克生活应用的认证系统提供了完整的用户注册、登录和密码重置功能。本指南将详细介绍如何使用这些功能。

## 功能特性

### 🔐 用户认证
- **用户注册**: 支持邮箱、用户名、密码和可选手机号注册
- **用户登录**: 使用邮箱和密码登录
- **忘记密码**: 通过邮箱验证码重置密码
- **自动登录**: 支持令牌自动刷新和持久化登录状态

### 🛡️ 安全特性
- **密码强度验证**: 要求密码包含字母和数字，至少6个字符
- **表单验证**: 实时表单验证和错误提示
- **令牌管理**: 安全的JWT令牌存储和自动刷新
- **设备管理**: 支持多设备登录和设备ID管理

## 使用方法

### 1. 用户注册

```typescript
import { useDispatch } from 'react-redux';
import { register } from '../store/slices/authSlice';

const handleRegister = async () => {
  const registerData = {
    username: 'testuser',
    email: 'test@example.com',
    password: 'password123',
    phone: '13800138000' // 可选
  };
  
  await dispatch(register(registerData));
};
```

### 2. 用户登录

```typescript
import { useDispatch } from 'react-redux';
import { login } from '../store/slices/authSlice';

const handleLogin = async () => {
  const credentials = {
    email: 'test@example.com',
    password: 'password123'
  };
  
  await dispatch(login(credentials));
};
```

### 3. 忘记密码

```typescript
import { useDispatch } from 'react-redux';
import { forgotPassword, verifyResetCode, resetPassword } from '../store/slices/authSlice';

// 步骤1: 发送重置邮件
await dispatch(forgotPassword('test@example.com'));

// 步骤2: 验证重置码
await dispatch(verifyResetCode({
  email: 'test@example.com',
  code: '123456'
}));

// 步骤3: 重置密码
await dispatch(resetPassword({
  email: 'test@example.com',
  code: '123456',
  newPassword: 'newpassword123'
}));
```

### 4. 检查认证状态

```typescript
import { useDispatch, useSelector } from 'react-redux';
import { checkAuthStatus, selectIsAuthenticated } from '../store/slices/authSlice';

const isAuthenticated = useSelector(selectIsAuthenticated);

// 应用启动时检查认证状态
useEffect(() => {
  dispatch(checkAuthStatus());
}, []);
```

## 表单验证

### 邮箱验证
- 必须符合标准邮箱格式
- 示例: `user@example.com`

### 密码验证
- 最少6个字符
- 必须包含字母和数字
- 示例: `password123`

### 用户名验证
- 长度2-20个字符
- 支持中文、英文、数字和下划线

### 手机号验证（可选）
- 中国大陆手机号格式
- 11位数字，以1开头
- 示例: `13800138000`

## 错误处理

认证系统提供了完整的错误处理机制：

```typescript
import { useSelector } from 'react-redux';
import { selectAuthError } from '../store/slices/authSlice';

const error = useSelector(selectAuthError);

if (error) {
  console.log('认证错误:', error);
  // 显示错误提示
}
```

## 状态管理

### 认证状态结构

```typescript
interface AuthState {
  isAuthenticated: boolean;
  user?: User;
  token?: string;
  refreshToken?: string;
  loading: boolean;
  error?: string;
}
```

### 选择器

```typescript
import {
  selectAuth,
  selectIsAuthenticated,
  selectUser,
  selectAuthLoading,
  selectAuthError
} from '../store/slices/authSlice';

// 获取完整认证状态
const auth = useSelector(selectAuth);

// 获取特定状态
const isAuthenticated = useSelector(selectIsAuthenticated);
const user = useSelector(selectUser);
const loading = useSelector(selectAuthLoading);
const error = useSelector(selectAuthError);
```

## 工具函数

### 表单验证工具

```typescript
import {
  validateEmail,
  validatePassword,
  validateUsername,
  validatePhone,
  getPasswordStrength
} from '../utils/authUtils';

// 验证邮箱
const isValidEmail = validateEmail('test@example.com');

// 验证密码
const isValidPassword = validatePassword('password123');

// 获取密码强度
const strength = getPasswordStrength('password123'); // 'weak' | 'medium' | 'strong'
```

### 令牌管理工具

```typescript
import {
  storeAuthTokens,
  getAuthToken,
  clearAuthTokens,
  isAuthenticated
} from '../utils/authUtils';

// 存储令牌
await storeAuthTokens('access_token', 'refresh_token');

// 获取令牌
const token = await getAuthToken();

// 清除令牌
await clearAuthTokens();

// 检查是否已认证
const authenticated = await isAuthenticated();
```

## 安全最佳实践

1. **密码安全**
   - 使用强密码策略
   - 定期提醒用户更新密码
   - 支持密码强度指示器

2. **令牌管理**
   - 自动刷新过期令牌
   - 安全存储在设备本地
   - 登出时清除所有令牌

3. **设备管理**
   - 生成唯一设备ID
   - 支持远程登出所有设备
   - 监控异常登录行为

4. **数据验证**
   - 前端和后端双重验证
   - 实时表单验证反馈
   - 防止恶意输入攻击

## 故障排除

### 常见问题

1. **登录失败**
   - 检查邮箱和密码是否正确
   - 确认网络连接正常
   - 查看错误消息获取详细信息

2. **注册失败**
   - 检查邮箱是否已被注册
   - 确认密码符合强度要求
   - 验证表单输入格式

3. **忘记密码失败**
   - 检查邮箱地址是否正确
   - 查看垃圾邮件文件夹
   - 确认验证码未过期

### 调试模式

在开发环境中，可以启用详细的日志输出：

```typescript
// 在apiClient中查看请求日志
console.log('🚀 API请求:', method, url);
console.log('📡 API响应:', response.status, responseData);
```

## 更新日志

### v1.0.0
- ✅ 完整的用户注册功能
- ✅ 用户登录和自动登录
- ✅ 忘记密码和重置功能
- ✅ 表单验证和错误处理
- ✅ 令牌管理和安全存储
- ✅ 设备ID管理
- ✅ 完整的TypeScript类型支持

## 技术栈

- **前端框架**: React Native
- **状态管理**: Redux Toolkit
- **网络请求**: Fetch API
- **本地存储**: AsyncStorage
- **类型检查**: TypeScript
- **测试框架**: Jest

## 贡献指南

如需贡献代码或报告问题，请参考项目的贡献指南。

---

**索克生活团队**  
*让健康管理更智能，让生活更美好* 