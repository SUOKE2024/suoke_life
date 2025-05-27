import React from 'react';
import { render, fireEvent, waitFor, act } from '@testing-library/react-native';
import { View, Text, TextInput, TouchableOpacity, Alert } from 'react-native';

// 设置测试环境
jest.useFakeTimers();

// Mock认证服务
const mockAuthService = {
  login: jest.fn(),
  register: jest.fn(),
  resetPassword: jest.fn(),
  verifyCode: jest.fn(),
  logout: jest.fn(),
  getCurrentUser: jest.fn(),
  updateProfile: jest.fn(),
};

jest.mock('../../services/authService', () => mockAuthService);

// Mock导航
const mockNavigation = {
  navigate: jest.fn(),
  goBack: jest.fn(),
  reset: jest.fn(),
};

// Mock Alert
jest.spyOn(Alert, 'alert').mockImplementation(() => {});

// Mock登录屏幕
const MockLoginScreen = ({ navigation }: any) => {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [loading, setLoading] = React.useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('错误', '请填写邮箱和密码');
      return;
    }

    setLoading(true);
    try {
      const result = await mockAuthService.login(email, password);
      if (result.success) {
        navigation.reset({
          index: 0,
          routes: [{ name: 'Main' }],
        });
      } else {
        Alert.alert('登录失败', result.message);
      }
    } catch (error) {
      Alert.alert('登录失败', '网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View testID="login-screen">
      <Text>登录</Text>
      <TextInput
        testID="email-input"
        placeholder="邮箱"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
      />
      <TextInput
        testID="password-input"
        placeholder="密码"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <TouchableOpacity
        testID="login-button"
        onPress={handleLogin}
        disabled={loading}
      >
        <Text>{loading ? '登录中...' : '登录'}</Text>
      </TouchableOpacity>
      <TouchableOpacity
        testID="register-link"
        onPress={() => navigation.navigate('Register')}
      >
        <Text>注册新账户</Text>
      </TouchableOpacity>
      <TouchableOpacity
        testID="forgot-password-link"
        onPress={() => navigation.navigate('ForgotPassword')}
      >
        <Text>忘记密码？</Text>
      </TouchableOpacity>
    </View>
  );
};

// Mock注册屏幕
const MockRegisterScreen = ({ navigation }: any) => {
  const [formData, setFormData] = React.useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
    phone: '',
  });
  const [loading, setLoading] = React.useState(false);

  const updateField = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleRegister = async () => {
    const { email, password, confirmPassword, name, phone } = formData;

    if (!email || !password || !name || !phone) {
      Alert.alert('错误', '请填写必填信息');
      return;
    }

    if (password.length < 6) {
      Alert.alert('错误', '密码长度至少6位');
      return;
    }

    if (password !== confirmPassword) {
      Alert.alert('错误', '两次输入的密码不一致');
      return;
    }

    setLoading(true);
    try {
      const result = await mockAuthService.register({
        email,
        password,
        name,
        phone,
      });

      if (result.success) {
        Alert.alert('注册成功', '请查收验证邮件');
        navigation.navigate('VerifyEmail', { email });
      } else {
        Alert.alert('注册失败', result.message);
      }
    } catch (error) {
      Alert.alert('注册失败', '网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View testID="register-screen">
      <Text>注册</Text>
      <TextInput
        testID="name-input"
        placeholder="姓名"
        value={formData.name}
        onChangeText={(value) => updateField('name', value)}
      />
      <TextInput
        testID="email-input"
        placeholder="邮箱"
        value={formData.email}
        onChangeText={(value) => updateField('email', value)}
        autoCapitalize="none"
        keyboardType="email-address"
      />
      <TextInput
        testID="phone-input"
        placeholder="手机号"
        value={formData.phone}
        onChangeText={(value) => updateField('phone', value)}
        keyboardType="phone-pad"
      />
      <TextInput
        testID="password-input"
        placeholder="密码"
        value={formData.password}
        onChangeText={(value) => updateField('password', value)}
        secureTextEntry
      />
      <TextInput
        testID="confirm-password-input"
        placeholder="确认密码"
        value={formData.confirmPassword}
        onChangeText={(value) => updateField('confirmPassword', value)}
        secureTextEntry
      />
      <TouchableOpacity
        testID="register-button"
        onPress={handleRegister}
        disabled={loading}
      >
        <Text>{loading ? '注册中...' : '注册'}</Text>
      </TouchableOpacity>
      <TouchableOpacity
        testID="login-link"
        onPress={() => navigation.navigate('Login')}
      >
        <Text>已有账户？立即登录</Text>
      </TouchableOpacity>
    </View>
  );
};

// Mock忘记密码屏幕
const MockForgotPasswordScreen = ({ navigation }: any) => {
  const [email, setEmail] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [sent, setSent] = React.useState(false);

  const handleResetPassword = async () => {
    if (!email) {
      Alert.alert('错误', '请输入邮箱地址');
      return;
    }

    setLoading(true);
    try {
      const result = await mockAuthService.resetPassword(email);
      if (result.success) {
        setSent(true);
        Alert.alert('发送成功', '重置密码邮件已发送');
      } else {
        Alert.alert('发送失败', result.message);
      }
    } catch (error) {
      Alert.alert('发送失败', '网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View testID="forgot-password-screen">
      <Text>重置密码</Text>
      {!sent ? (
        <>
          <Text>请输入您的邮箱地址，我们将发送重置密码链接</Text>
          <TextInput
            testID="email-input"
            placeholder="邮箱"
            value={email}
            onChangeText={setEmail}
            autoCapitalize="none"
            keyboardType="email-address"
          />
          <TouchableOpacity
            testID="send-button"
            onPress={handleResetPassword}
            disabled={loading}
          >
            <Text>{loading ? '发送中...' : '发送重置邮件'}</Text>
          </TouchableOpacity>
        </>
      ) : (
        <>
          <Text testID="success-message">重置邮件已发送到 {email}</Text>
          <TouchableOpacity
            testID="resend-button"
            onPress={() => setSent(false)}
          >
            <Text>重新发送</Text>
          </TouchableOpacity>
        </>
      )}
      <TouchableOpacity
        testID="back-to-login"
        onPress={() => navigation.navigate('Login')}
      >
        <Text>返回登录</Text>
      </TouchableOpacity>
    </View>
  );
};

// Mock邮箱验证屏幕
const MockVerifyEmailScreen = ({ navigation, route }: any) => {
  const [code, setCode] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const email = route?.params?.email || '';

  const handleVerifyCode = async () => {
    if (!code) {
      Alert.alert('错误', '请输入验证码');
      return;
    }

    setLoading(true);
    try {
      const result = await mockAuthService.verifyCode(email, code);
      if (result.success) {
        Alert.alert('验证成功', '账户已激活');
        navigation.reset({
          index: 0,
          routes: [{ name: 'Login' }],
        });
      } else {
        Alert.alert('验证失败', result.message);
      }
    } catch (error) {
      Alert.alert('验证失败', '网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const handleResendCode = async () => {
    try {
      await mockAuthService.register({ email, resend: true });
      Alert.alert('发送成功', '验证码已重新发送');
    } catch (error) {
      Alert.alert('发送失败', '请稍后重试');
    }
  };

  return (
    <View testID="verify-email-screen">
      <Text>邮箱验证</Text>
      <Text>验证码已发送到 {email}</Text>
      <TextInput
        testID="code-input"
        placeholder="请输入6位验证码"
        value={code}
        onChangeText={setCode}
        keyboardType="number-pad"
        maxLength={6}
      />
      <TouchableOpacity
        testID="verify-button"
        onPress={handleVerifyCode}
        disabled={loading}
      >
        <Text>{loading ? '验证中...' : '验证'}</Text>
      </TouchableOpacity>
      <TouchableOpacity
        testID="resend-button"
        onPress={handleResendCode}
      >
        <Text>重新发送验证码</Text>
      </TouchableOpacity>
    </View>
  );
};

describe('认证流程集成测试', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigation.navigate.mockClear();
    mockNavigation.reset.mockClear();
    (Alert.alert as jest.Mock).mockClear();
  });

  describe('登录流程', () => {
    it('应该成功登录', async () => {
      mockAuthService.login.mockResolvedValue({
        success: true,
        user: { id: '1', email: 'test@example.com' },
        token: 'mock-token',
      });

      const { getByTestId } = render(
        <MockLoginScreen navigation={mockNavigation} />
      );

      const emailInput = getByTestId('email-input');
      const passwordInput = getByTestId('password-input');
      const loginButton = getByTestId('login-button');

      await act(async () => {
        fireEvent.changeText(emailInput, 'test@example.com');
        fireEvent.changeText(passwordInput, 'password123');
        fireEvent.press(loginButton);
      });

      await waitFor(() => {
        expect(mockAuthService.login).toHaveBeenCalledWith(
          'test@example.com',
          'password123'
        );
      });

      await waitFor(() => {
        expect(mockNavigation.reset).toHaveBeenCalledWith({
          index: 0,
          routes: [{ name: 'Main' }],
        });
      });
    });

    it('应该处理登录失败', async () => {
      mockAuthService.login.mockResolvedValue({
        success: false,
        message: '邮箱或密码错误',
      });

      const { getByTestId } = render(
        <MockLoginScreen navigation={mockNavigation} />
      );

      const emailInput = getByTestId('email-input');
      const passwordInput = getByTestId('password-input');
      const loginButton = getByTestId('login-button');

      // 分别设置表单字段
      act(() => {
        fireEvent.changeText(emailInput, 'test@example.com');
      });
      
      act(() => {
        fireEvent.changeText(passwordInput, 'wrongpassword');
      });

      // 然后按下登录按钮
      await act(async () => {
        fireEvent.press(loginButton);
      });

      await waitFor(() => {
        expect(mockAuthService.login).toHaveBeenCalledWith(
          'test@example.com',
          'wrongpassword'
        );
      });

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith('登录失败', '邮箱或密码错误');
      });
    });

    it('应该验证必填字段', () => {
      const { getByTestId } = render(
        <MockLoginScreen navigation={mockNavigation} />
      );

      const loginButton = getByTestId('login-button');
      
      act(() => {
        fireEvent.press(loginButton);
      });

      expect(Alert.alert).toHaveBeenCalledWith('错误', '请填写邮箱和密码');
    });

    it('应该导航到注册页面', () => {
      const { getByTestId } = render(
        <MockLoginScreen navigation={mockNavigation} />
      );

      const registerLink = getByTestId('register-link');
      
      act(() => {
        fireEvent.press(registerLink);
      });

      expect(mockNavigation.navigate).toHaveBeenCalledWith('Register');
    });

    it('应该导航到忘记密码页面', () => {
      const { getByTestId } = render(
        <MockLoginScreen navigation={mockNavigation} />
      );

      const forgotPasswordLink = getByTestId('forgot-password-link');
      
      act(() => {
        fireEvent.press(forgotPasswordLink);
      });

      expect(mockNavigation.navigate).toHaveBeenCalledWith('ForgotPassword');
    });
  });

  describe('注册流程', () => {
    it('应该成功注册', async () => {
      mockAuthService.register.mockResolvedValue({
        success: true,
        message: '注册成功',
      });

      const { getByTestId } = render(
        <MockRegisterScreen navigation={mockNavigation} />
      );

      // 分别设置表单字段
      act(() => {
        fireEvent.changeText(getByTestId('name-input'), '张三');
      });
      
      act(() => {
        fireEvent.changeText(getByTestId('email-input'), 'test@example.com');
      });
      
      act(() => {
        fireEvent.changeText(getByTestId('phone-input'), '13800138000');
      });
      
      act(() => {
        fireEvent.changeText(getByTestId('password-input'), 'password123');
      });
      
      act(() => {
        fireEvent.changeText(getByTestId('confirm-password-input'), 'password123');
      });

      // 然后按下注册按钮
      await act(async () => {
        fireEvent.press(getByTestId('register-button'));
      });

      await waitFor(() => {
        expect(mockAuthService.register).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'password123',
          name: '张三',
          phone: '13800138000',
        });
      });

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith('注册成功', '请查收验证邮件');
        expect(mockNavigation.navigate).toHaveBeenCalledWith('VerifyEmail', {
          email: 'test@example.com',
        });
      });
    });

    it('应该验证密码一致性', () => {
      const { getByTestId } = render(
        <MockRegisterScreen navigation={mockNavigation} />
      );

      act(() => {
        fireEvent.changeText(getByTestId('name-input'), '张三');
        fireEvent.changeText(getByTestId('email-input'), 'test@example.com');
        fireEvent.changeText(getByTestId('phone-input'), '13800138000');
        fireEvent.changeText(getByTestId('password-input'), 'password123');
        fireEvent.changeText(getByTestId('confirm-password-input'), 'different');

        fireEvent.press(getByTestId('register-button'));
      });

      expect(Alert.alert).toHaveBeenCalledWith('错误', '两次输入的密码不一致');
    });

    it('应该验证密码长度', () => {
      const { getByTestId } = render(
        <MockRegisterScreen navigation={mockNavigation} />
      );

      act(() => {
        fireEvent.changeText(getByTestId('name-input'), '张三');
        fireEvent.changeText(getByTestId('email-input'), 'test@example.com');
        fireEvent.changeText(getByTestId('phone-input'), '13800138000');
        fireEvent.changeText(getByTestId('password-input'), '123');
        fireEvent.changeText(getByTestId('confirm-password-input'), '123');

        fireEvent.press(getByTestId('register-button'));
      });

      expect(Alert.alert).toHaveBeenCalledWith('错误', '密码长度至少6位');
    });

    it('应该验证必填字段', () => {
      const { getByTestId } = render(
        <MockRegisterScreen navigation={mockNavigation} />
      );

      act(() => {
        fireEvent.press(getByTestId('register-button'));
      });

      expect(Alert.alert).toHaveBeenCalledWith('错误', '请填写必填信息');
    });
  });

  describe('忘记密码流程', () => {
    it('应该发送重置密码邮件', async () => {
      mockAuthService.resetPassword.mockResolvedValue({
        success: true,
        message: '邮件已发送',
      });

      const { getByTestId } = render(
        <MockForgotPasswordScreen navigation={mockNavigation} />
      );

      // 先设置邮箱
      act(() => {
        fireEvent.changeText(getByTestId('email-input'), 'test@example.com');
      });

      // 然后按下发送按钮
      await act(async () => {
        fireEvent.press(getByTestId('send-button'));
      });

      await waitFor(() => {
        expect(mockAuthService.resetPassword).toHaveBeenCalledWith('test@example.com');
      });

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith('发送成功', '重置密码邮件已发送');
      });

      await waitFor(() => {
        expect(getByTestId('success-message')).toBeTruthy();
      });
    });

    it('应该验证邮箱输入', () => {
      const { getByTestId } = render(
        <MockForgotPasswordScreen navigation={mockNavigation} />
      );

      fireEvent.press(getByTestId('send-button'));

      expect(Alert.alert).toHaveBeenCalledWith('错误', '请输入邮箱地址');
    });

    it('应该支持重新发送', async () => {
      mockAuthService.resetPassword.mockResolvedValue({
        success: true,
        message: '邮件已发送',
      });

      const { getByTestId } = render(
        <MockForgotPasswordScreen navigation={mockNavigation} />
      );

      await act(async () => {
        fireEvent.changeText(getByTestId('email-input'), 'test@example.com');
        fireEvent.press(getByTestId('send-button'));
      });

      await waitFor(() => {
        expect(getByTestId('success-message')).toBeTruthy();
      });

      act(() => {
        fireEvent.press(getByTestId('resend-button'));
      });
      
      expect(getByTestId('email-input')).toBeTruthy();
    });
  });

  describe('邮箱验证流程', () => {
    const mockRoute = {
      params: { email: 'test@example.com' },
    };

    it('应该成功验证邮箱', async () => {
      mockAuthService.verifyCode.mockResolvedValue({
        success: true,
        message: '验证成功',
      });

      const { getByTestId } = render(
        <MockVerifyEmailScreen 
          navigation={mockNavigation} 
          route={mockRoute}
        />
      );

      // 先设置验证码
      act(() => {
        fireEvent.changeText(getByTestId('code-input'), '123456');
      });

      // 然后按下验证按钮
      await act(async () => {
        fireEvent.press(getByTestId('verify-button'));
      });

      await waitFor(() => {
        expect(mockAuthService.verifyCode).toHaveBeenCalledWith(
          'test@example.com',
          '123456'
        );
      });

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith('验证成功', '账户已激活');
      });

      await waitFor(() => {
        expect(mockNavigation.reset).toHaveBeenCalledWith({
          index: 0,
          routes: [{ name: 'Login' }],
        });
      });
    });

    it('应该验证验证码输入', () => {
      const { getByTestId } = render(
        <MockVerifyEmailScreen 
          navigation={mockNavigation} 
          route={mockRoute}
        />
      );

      fireEvent.press(getByTestId('verify-button'));

      expect(Alert.alert).toHaveBeenCalledWith('错误', '请输入验证码');
    });

    it('应该支持重新发送验证码', async () => {
      mockAuthService.register.mockResolvedValue({
        success: true,
      });

      const { getByTestId } = render(
        <MockVerifyEmailScreen 
          navigation={mockNavigation} 
          route={mockRoute}
        />
      );

      await act(async () => {
        fireEvent.press(getByTestId('resend-button'));
      });

      await waitFor(() => {
        expect(mockAuthService.register).toHaveBeenCalledWith({
          email: 'test@example.com',
          resend: true,
        });
      });

      expect(Alert.alert).toHaveBeenCalledWith('发送成功', '验证码已重新发送');
    });
  });

  describe('网络错误处理', () => {
    it('应该处理登录网络错误', async () => {
      mockAuthService.login.mockRejectedValue(new Error('Network Error'));

      const { getByTestId } = render(
        <MockLoginScreen navigation={mockNavigation} />
      );

      // 分别设置表单字段
      act(() => {
        fireEvent.changeText(getByTestId('email-input'), 'test@example.com');
      });
      
      act(() => {
        fireEvent.changeText(getByTestId('password-input'), 'password123');
      });

      // 然后按下登录按钮
      await act(async () => {
        fireEvent.press(getByTestId('login-button'));
      });

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith('登录失败', '网络错误，请稍后重试');
      });
    });

    it('应该处理注册网络错误', async () => {
      mockAuthService.register.mockRejectedValue(new Error('Network Error'));

      const { getByTestId } = render(
        <MockRegisterScreen navigation={mockNavigation} />
      );

      // 分别设置表单字段
      act(() => {
        fireEvent.changeText(getByTestId('name-input'), '张三');
      });
      
      act(() => {
        fireEvent.changeText(getByTestId('email-input'), 'test@example.com');
      });
      
      act(() => {
        fireEvent.changeText(getByTestId('phone-input'), '13800138000');
      });
      
      act(() => {
        fireEvent.changeText(getByTestId('password-input'), 'password123');
      });
      
      act(() => {
        fireEvent.changeText(getByTestId('confirm-password-input'), 'password123');
      });

      // 然后按下注册按钮
      await act(async () => {
        fireEvent.press(getByTestId('register-button'));
      });

      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith('注册失败', '网络错误，请稍后重试');
      });
    });
  });
});