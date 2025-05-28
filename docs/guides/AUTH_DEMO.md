# 索克生活 - 认证流程演示

## 快速开始

这个演示展示了如何在索克生活应用中使用完整的认证流程。

## 1. 用户注册演示

```typescript
// RegisterScreen.tsx 中的使用示例
import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { register } from '../store/slices/authSlice';
import { validateRegisterForm } from '../utils/authUtils';

const RegisterDemo = () => {
  const dispatch = useDispatch();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    phone: '',
  });

  const handleRegister = async () => {
    // 1. 表单验证
    const errors = validateRegisterForm(formData);
    if (Object.keys(errors).length > 0) {
      console.log('表单验证失败:', errors);
      return;
    }

    // 2. 发起注册请求
    try {
      const result = await dispatch(register({
        username: formData.username.trim(),
        email: formData.email.trim().toLowerCase(),
        password: formData.password,
        phone: formData.phone.trim() || undefined,
      }));
      
      console.log('注册成功:', result);
    } catch (error) {
      console.error('注册失败:', error);
    }
  };

  return (
    // UI 组件...
  );
};
```

## 2. 用户登录演示

```typescript
// LoginScreen.tsx 中的使用示例
import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { login } from '../store/slices/authSlice';
import { validateLoginForm } from '../utils/authUtils';

const LoginDemo = () => {
  const dispatch = useDispatch();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const handleLogin = async () => {
    // 1. 表单验证
    const errors = validateLoginForm(formData);
    if (Object.keys(errors).length > 0) {
      console.log('表单验证失败:', errors);
      return;
    }

    // 2. 发起登录请求
    try {
      const result = await dispatch(login({
        email: formData.email.trim().toLowerCase(),
        password: formData.password,
      }));
      
      console.log('登录成功:', result);
    } catch (error) {
      console.error('登录失败:', error);
    }
  };

  return (
    // UI 组件...
  );
};
```

## 3. 忘记密码演示

```typescript
// ForgotPasswordScreen.tsx 中的使用示例
import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { forgotPassword, verifyResetCode, resetPassword } from '../store/slices/authSlice';

const ForgotPasswordDemo = () => {
  const dispatch = useDispatch();
  const [currentStep, setCurrentStep] = useState<'email' | 'verification' | 'reset'>('email');
  const [formData, setFormData] = useState({
    email: '',
    verificationCode: '',
    newPassword: '',
    confirmPassword: '',
  });

  // 步骤1: 发送重置邮件
  const handleSendResetEmail = async () => {
    try {
      await dispatch(forgotPassword(formData.email.trim().toLowerCase()));
      setCurrentStep('verification');
      console.log('重置邮件发送成功');
    } catch (error) {
      console.error('发送失败:', error);
    }
  };

  // 步骤2: 验证重置码
  const handleVerifyCode = async () => {
    try {
      await dispatch(verifyResetCode({
        email: formData.email.trim().toLowerCase(),
        code: formData.verificationCode.trim(),
      }));
      setCurrentStep('reset');
      console.log('验证码验证成功');
    } catch (error) {
      console.error('验证失败:', error);
    }
  };

  // 步骤3: 重置密码
  const handleResetPassword = async () => {
    try {
      await dispatch(resetPassword({
        email: formData.email.trim().toLowerCase(),
        code: formData.verificationCode.trim(),
        newPassword: formData.newPassword,
      }));
      console.log('密码重置成功');
    } catch (error) {
      console.error('重置失败:', error);
    }
  };

  return (
    // UI 组件...
  );
};
```

## 4. 认证状态管理演示

```typescript
// App.tsx 或主组件中的使用示例
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { 
  checkAuthStatus, 
  selectIsAuthenticated, 
  selectUser, 
  selectAuthLoading 
} from '../store/slices/authSlice';

const AuthStatusDemo = () => {
  const dispatch = useDispatch();
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const user = useSelector(selectUser);
  const loading = useSelector(selectAuthLoading);

  // 应用启动时检查认证状态
  useEffect(() => {
    dispatch(checkAuthStatus());
  }, [dispatch]);

  if (loading) {
    return <LoadingScreen />;
  }

  if (isAuthenticated && user) {
    return <MainApp user={user} />;
  }

  return <AuthNavigator />;
};
```

## 5. 工具函数使用演示

```typescript
// 表单验证演示
import {
  validateEmail,
  validatePassword,
  validateUsername,
  getPasswordStrength,
  validateLoginForm,
  validateRegisterForm
} from '../utils/authUtils';

// 单个字段验证
const email = 'user@example.com';
const isValidEmail = validateEmail(email); // true

const password = 'password123';
const isValidPassword = validatePassword(password); // true
const passwordStrength = getPasswordStrength(password); // 'medium'

const username = 'testuser';
const isValidUsername = validateUsername(username); // true

// 整个表单验证
const loginData = {
  email: 'user@example.com',
  password: 'password123'
};
const loginErrors = validateLoginForm(loginData); // {}

const registerData = {
  username: 'testuser',
  email: 'user@example.com',
  password: 'password123',
  confirmPassword: 'password123',
  phone: '13800138000'
};
const registerErrors = validateRegisterForm(registerData); // {}
```

## 6. 令牌管理演示

```typescript
// 令牌管理演示
import {
  storeAuthTokens,
  getAuthToken,
  clearAuthTokens,
  isAuthenticated
} from '../utils/authUtils';

// 存储令牌
await storeAuthTokens('access_token_here', 'refresh_token_here');

// 获取令牌
const token = await getAuthToken(); // 'access_token_here'

// 检查认证状态
const authenticated = await isAuthenticated(); // true

// 清除令牌
await clearAuthTokens();
```

## 7. 错误处理演示

```typescript
// 错误处理演示
import { formatAuthError } from '../utils/authUtils';

try {
  await dispatch(login(credentials));
} catch (error) {
  const errorMessage = formatAuthError(error);
  console.error('登录错误:', errorMessage);
  
  // 显示用户友好的错误消息
  Alert.alert('登录失败', errorMessage);
}
```

## 8. 完整的认证流程

```typescript
// 完整的认证流程演示
const AuthFlowDemo = () => {
  const dispatch = useDispatch();
  const { isAuthenticated, user, loading, error } = useSelector(selectAuth);

  // 注册 -> 登录 -> 使用应用
  const completeAuthFlow = async () => {
    try {
      // 1. 注册新用户
      await dispatch(register({
        username: 'newuser',
        email: 'newuser@example.com',
        password: 'password123',
      }));

      // 2. 注册成功后自动登录（由authSlice处理）
      console.log('用户已注册并登录:', user);

      // 3. 应用正常使用...
      
    } catch (error) {
      console.error('认证流程失败:', error);
      
      // 4. 如果注册失败，尝试登录
      try {
        await dispatch(login({
          email: 'newuser@example.com',
          password: 'password123',
        }));
        console.log('用户登录成功:', user);
      } catch (loginError) {
        console.error('登录也失败了:', loginError);
      }
    }
  };

  return (
    <View>
      {loading && <Text>处理中...</Text>}
      {error && <Text>错误: {error}</Text>}
      {isAuthenticated ? (
        <Text>欢迎, {user?.username}!</Text>
      ) : (
        <Button title="开始认证流程" onPress={completeAuthFlow} />
      )}
    </View>
  );
};
```

## 测试建议

1. **单元测试**: 使用Jest测试工具函数
2. **集成测试**: 测试完整的认证流程
3. **UI测试**: 使用React Native Testing Library测试组件
4. **端到端测试**: 使用Detox测试完整的用户流程

## 安全注意事项

1. **密码安全**: 永远不要在日志中记录密码
2. **令牌存储**: 使用安全的本地存储方式
3. **网络安全**: 确保所有API调用都使用HTTPS
4. **输入验证**: 始终验证用户输入
5. **错误处理**: 不要在错误消息中泄露敏感信息

---

这个演示展示了索克生活应用中认证系统的完整使用方法。通过这些示例，开发者可以快速理解和实现认证功能。 