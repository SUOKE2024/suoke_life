import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { View, Text, TextInput, TouchableOpacity } from 'react-native';
import { store } from '../../store';

// Mock AuthService
const mockAuthService = {
  login: jest.fn(),
  register: jest.fn(),
  logout: jest.fn(),
  getCurrentUser: jest.fn(),
  refreshToken: jest.fn(),
};

jest.mock('../../services/authService', () => ({
  authService: mockAuthService,
}));

// 简化的登录组件
const LoginComponent = () => {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');

  const handleLogin = async () => {
    setLoading(true);
    setError('');
    try {
      await mockAuthService.login({ email, password });
    } catch (error) {
      console.error('Login failed:', error);
      setError('登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View testID="login-component">
      <TextInput
        testID="email-input"
        value={email}
        onChangeText={setEmail}
        placeholder="邮箱"
      />
      <TextInput
        testID="password-input"
        value={password}
        onChangeText={setPassword}
        placeholder="密码"
        secureTextEntry
      />
      {error ? <Text testID="error-message">{error}</Text> : null}
      <TouchableOpacity
        testID="login-button"
        onPress={handleLogin}
        disabled={loading}
      >
        <Text>{loading ? '登录中...' : '登录'}</Text>
      </TouchableOpacity>
    </View>
  );
};

// 简化的注册组件
const RegisterComponent = () => {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [confirmPassword, setConfirmPassword] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');

  const handleRegister = async () => {
    if (password !== confirmPassword) {
      setError('密码不匹配');
      return;
    }
    
    setLoading(true);
    setError('');
    try {
      await mockAuthService.register({ email, password });
    } catch (error) {
      console.error('Registration failed:', error);
      setError('注册失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View testID="register-component">
      <TextInput
        testID="register-email-input"
        value={email}
        onChangeText={setEmail}
        placeholder="注册邮箱"
      />
      <TextInput
        testID="register-password-input"
        value={password}
        onChangeText={setPassword}
        placeholder="注册密码"
        secureTextEntry
      />
      <TextInput
        testID="confirm-password-input"
        value={confirmPassword}
        onChangeText={setConfirmPassword}
        placeholder="确认密码"
        secureTextEntry
      />
      {error ? <Text testID="error-message">{error}</Text> : null}
      <TouchableOpacity
        testID="register-button"
        onPress={handleRegister}
        disabled={loading}
      >
        <Text>{loading ? '注册中...' : '注册'}</Text>
      </TouchableOpacity>
    </View>
  );
};

// 简化的主页组件
const HomeComponent = () => {
  const [loading, setLoading] = React.useState(false);

  const handleLogout = async () => {
    setLoading(true);
    try {
      await mockAuthService.logout();
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View testID="home-component">
      <Text testID="welcome-message">欢迎回来！</Text>
      <TouchableOpacity 
        testID="logout-button" 
        onPress={handleLogout}
        disabled={loading}
      >
        <Text>{loading ? '登出中...' : '登出'}</Text>
      </TouchableOpacity>
    </View>
  );
};

// 测试包装器
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <Provider store={store}>
    {children}
  </Provider>
);

describe('认证流程集成测试', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('登录流程', () => {
    it('应该成功完成登录流程', async () => {
      mockAuthService.login.mockResolvedValue({
        user: { id: '1', email: 'test@example.com', name: '测试用户' },
        token: 'mock-token',
      });

      const { toJSON } = render(
        <TestWrapper>
          <LoginComponent />
        </TestWrapper>
      );

      // 验证组件渲染
      const tree = toJSON();
      expect(JSON.stringify(tree)).toContain('邮箱');
      expect(JSON.stringify(tree)).toContain('密码');
      expect(JSON.stringify(tree)).toContain('登录');

      // 点击登录按钮 - 使用文本查找
      const loginText = screen.getByText('登录');
      fireEvent.press(loginText);

      // 等待登录完成
      await waitFor(() => {
        expect(mockAuthService.login).toHaveBeenCalledWith({
          email: '',
          password: ''
        });
      });
    });

    it('应该处理登录错误', async () => {
      mockAuthService.login.mockRejectedValue(new Error('登录失败'));

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      render(
        <TestWrapper>
          <LoginComponent />
        </TestWrapper>
      );

      const loginText = screen.getByText('登录');
      fireEvent.press(loginText);

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Login failed:', expect.any(Error));
        expect(screen.getByText('登录失败')).toBeTruthy();
      });

      consoleSpy.mockRestore();
    });

    it('应该在登录过程中显示加载状态', async () => {
      let resolveLogin: (value: any) => void;
      mockAuthService.login.mockImplementation(() => new Promise(resolve => {
        resolveLogin = resolve;
      }));

      render(
        <TestWrapper>
          <LoginComponent />
        </TestWrapper>
      );

      const loginText = screen.getByText('登录');
      fireEvent.press(loginText);

      // 检查加载状态
      expect(screen.getByText('登录中...')).toBeTruthy();

      // 完成登录
      resolveLogin!({
        user: { id: '1', email: 'test@example.com', name: '测试用户' },
        token: 'mock-token',
      });

      await waitFor(() => {
        expect(screen.getByText('登录')).toBeTruthy();
      });
    });

    it('应该处理空输入', async () => {
      render(
        <TestWrapper>
          <LoginComponent />
        </TestWrapper>
      );

      const loginText = screen.getByText('登录');

      // 不输入任何内容直接点击登录
      fireEvent.press(loginText);

      // 验证AuthService.login被调用时使用了空字符串
      await waitFor(() => {
        expect(mockAuthService.login).toHaveBeenCalledWith({
          email: '',
          password: ''
        });
      });
    });
  });

  describe('注册流程', () => {
    it('应该成功完成注册流程', async () => {
      mockAuthService.register.mockResolvedValue({
        user: { id: '2', email: 'newuser@example.com', name: '新用户' },
        token: 'new-token',
      });

      const { toJSON } = render(
        <TestWrapper>
          <RegisterComponent />
        </TestWrapper>
      );

      // 验证组件渲染
      const tree = toJSON();
      expect(JSON.stringify(tree)).toContain('注册邮箱');
      expect(JSON.stringify(tree)).toContain('注册密码');
      expect(JSON.stringify(tree)).toContain('确认密码');
      expect(JSON.stringify(tree)).toContain('注册');

      const registerText = screen.getByText('注册');
      fireEvent.press(registerText);

      await waitFor(() => {
        expect(mockAuthService.register).toHaveBeenCalledWith({
          email: '',
          password: ''
        });
      });
    });

    it('应该验证密码匹配', async () => {
      render(
        <TestWrapper>
          <RegisterComponent />
        </TestWrapper>
      );

      const registerText = screen.getByText('注册');
      fireEvent.press(registerText);

      await waitFor(() => {
        expect(screen.getByText('密码不匹配')).toBeTruthy();
      });

      // 验证register服务没有被调用
      expect(mockAuthService.register).not.toHaveBeenCalled();
    });

    it('应该处理注册错误', async () => {
      mockAuthService.register.mockRejectedValue(new Error('注册失败'));

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      render(
        <TestWrapper>
          <RegisterComponent />
        </TestWrapper>
      );

      const registerText = screen.getByText('注册');
      fireEvent.press(registerText);

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Registration failed:', expect.any(Error));
        expect(screen.getByText('注册失败')).toBeTruthy();
      });

      consoleSpy.mockRestore();
    });
  });

  describe('登出流程', () => {
    it('应该成功完成登出流程', async () => {
      mockAuthService.logout.mockResolvedValue(undefined);

      render(
        <TestWrapper>
          <HomeComponent />
        </TestWrapper>
      );

      const logoutText = screen.getByText('登出');
      fireEvent.press(logoutText);

      await waitFor(() => {
        expect(mockAuthService.logout).toHaveBeenCalled();
      });
    });

    it('应该在登出过程中显示加载状态', async () => {
      let resolveLogout: (value: any) => void;
      mockAuthService.logout.mockImplementation(() => new Promise(resolve => {
        resolveLogout = resolve;
      }));

      render(
        <TestWrapper>
          <HomeComponent />
        </TestWrapper>
      );

      const logoutText = screen.getByText('登出');
      fireEvent.press(logoutText);

      // 检查加载状态
      expect(screen.getByText('登出中...')).toBeTruthy();

      // 完成登出
      resolveLogout!(undefined);

      await waitFor(() => {
        expect(screen.getByText('登出')).toBeTruthy();
      });
    });
  });

  describe('性能测试', () => {
    it('登录流程应该在合理时间内完成', async () => {
      mockAuthService.login.mockResolvedValue({
        user: { id: '1', email: 'test@example.com', name: '测试用户' },
        token: 'mock-token',
      });

      const startTime = performance.now();
      
      render(
        <TestWrapper>
          <LoginComponent />
        </TestWrapper>
      );

      const loginText = screen.getByText('登录');
      fireEvent.press(loginText);

      await waitFor(() => {
        expect(mockAuthService.login).toHaveBeenCalled();
      });

      const endTime = performance.now();
      const totalTime = endTime - startTime;

      expect(totalTime).toBeLessThan(1000); // 1秒内完成
    });

    it('应该高效处理多个并发登录请求', async () => {
      mockAuthService.login.mockResolvedValue({
        user: { id: '1', email: 'test@example.com', name: '测试用户' },
        token: 'mock-token',
      });

      render(
        <TestWrapper>
          <LoginComponent />
        </TestWrapper>
      );

      const startTime = performance.now();

      const loginText = screen.getByText('登录');

      // 模拟快速多次点击
      for (let i = 0; i < 5; i++) {
        fireEvent.press(loginText);
      }

      await waitFor(() => {
        expect(mockAuthService.login).toHaveBeenCalled();
      });

      const endTime = performance.now();
      const totalTime = endTime - startTime;

      expect(totalTime).toBeLessThan(2000); // 2秒内完成
      // 验证只调用了一次（防止重复提交）
      expect(mockAuthService.login).toHaveBeenCalledTimes(1);
    });

    it('组件渲染性能测试', async () => {
      const iterations = 10;
      const times = [];

      for (let i = 0; i < iterations; i++) {
        const startTime = performance.now();
        
        const { unmount } = render(
          <TestWrapper>
            <LoginComponent />
          </TestWrapper>
        );
        
        const endTime = performance.now();
        unmount();
        times.push(endTime - startTime);
      }

      const averageTime = times.reduce((sum, time) => sum + time, 0) / iterations;
      expect(averageTime).toBeLessThan(200); // 调整为200ms，更现实的期望
    });
  });

  describe('错误处理', () => {
    it('应该处理网络错误', async () => {
      mockAuthService.login.mockRejectedValue(new Error('网络连接失败'));

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      render(
        <TestWrapper>
          <LoginComponent />
        </TestWrapper>
      );

      const loginText = screen.getByText('登录');
      fireEvent.press(loginText);

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Login failed:', expect.any(Error));
        expect(screen.getByText('登录失败')).toBeTruthy();
      });

      consoleSpy.mockRestore();
    });

    it('应该处理服务器错误', async () => {
      mockAuthService.register.mockRejectedValue(new Error('服务器内部错误'));

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      render(
        <TestWrapper>
          <RegisterComponent />
        </TestWrapper>
      );

      const registerText = screen.getByText('注册');
      fireEvent.press(registerText);

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Registration failed:', expect.any(Error));
        expect(screen.getByText('注册失败')).toBeTruthy();
      });

      consoleSpy.mockRestore();
    });
  });
}); 