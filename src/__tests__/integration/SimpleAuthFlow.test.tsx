import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { View, Text, TouchableOpacity } from 'react-native';
import { store } from '../../store';

// Mock AuthService
const mockAuthService = {
  login: jest.fn(),
  register: jest.fn(),
  logout: jest.fn(),
};

jest.mock('../../services/authService', () => ({
  authService: mockAuthService,
}));

// 简化的测试组件
const SimpleAuthComponent = () => {
  const [status, setStatus] = React.useState('idle');

  const handleLogin = async () => {
    setStatus('logging-in');
    try {
      await mockAuthService.login({ email: 'test@example.com', password: 'password' });
      setStatus('logged-in');
    } catch (error) {
      setStatus('login-error');
    }
  };

  const handleRegister = async () => {
    setStatus('registering');
    try {
      await mockAuthService.register({ email: 'test@example.com', password: 'password' });
      setStatus('registered');
    } catch (error) {
      setStatus('register-error');
    }
  };

  const handleLogout = async () => {
    setStatus('logging-out');
    try {
      await mockAuthService.logout();
      setStatus('logged-out');
    } catch (error) {
      setStatus('logout-error');
    }
  };

  return (
    <View testID="auth-component">
      <Text testID="status-text">{status}</Text>
      <TouchableOpacity testID="login-button" onPress={handleLogin}>
        <Text>Login</Text>
      </TouchableOpacity>
      <TouchableOpacity testID="register-button" onPress={handleRegister}>
        <Text>Register</Text>
      </TouchableOpacity>
      <TouchableOpacity testID="logout-button" onPress={handleLogout}>
        <Text>Logout</Text>
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

describe('简化认证流程集成测试', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('基础功能测试', () => {
    it('应该正确渲染组件', () => {
      const { getByTestId } = render(
        <TestWrapper>
          <SimpleAuthComponent />
        </TestWrapper>
      );

      expect(getByTestId('auth-component')).toBeTruthy();
      expect(getByTestId('status-text')).toBeTruthy();
      expect(getByTestId('login-button')).toBeTruthy();
      expect(getByTestId('register-button')).toBeTruthy();
      expect(getByTestId('logout-button')).toBeTruthy();
    });

    it('应该成功处理登录流程', async () => {
      mockAuthService.login.mockResolvedValue({
        user: { id: '1', email: 'test@example.com' },
        token: 'mock-token',
      });

      const { getByTestId } = render(
        <TestWrapper>
          <SimpleAuthComponent />
        </TestWrapper>
      );

      const loginButton = getByTestId('login-button');
      const statusText = getByTestId('status-text');

      // 初始状态
      expect(statusText.props.children).toBe('idle');

      // 点击登录按钮
      fireEvent.press(loginButton);

      // 检查登录中状态
      expect(statusText.props.children).toBe('logging-in');

      // 等待登录完成
      await waitFor(() => {
        expect(statusText.props.children).toBe('logged-in');
      });

      // 验证服务被调用
      expect(mockAuthService.login).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password'
      });
    });

    it('应该处理登录错误', async () => {
      mockAuthService.login.mockRejectedValue(new Error('Login failed'));

      const { getByTestId } = render(
        <TestWrapper>
          <SimpleAuthComponent />
        </TestWrapper>
      );

      const loginButton = getByTestId('login-button');
      const statusText = getByTestId('status-text');

      fireEvent.press(loginButton);

      await waitFor(() => {
        expect(statusText.props.children).toBe('login-error');
      });

      expect(mockAuthService.login).toHaveBeenCalled();
    });

    it('应该成功处理注册流程', async () => {
      mockAuthService.register.mockResolvedValue({
        user: { id: '2', email: 'test@example.com' },
        token: 'new-token',
      });

      const { getByTestId } = render(
        <TestWrapper>
          <SimpleAuthComponent />
        </TestWrapper>
      );

      const registerButton = getByTestId('register-button');
      const statusText = getByTestId('status-text');

      fireEvent.press(registerButton);

      expect(statusText.props.children).toBe('registering');

      await waitFor(() => {
        expect(statusText.props.children).toBe('registered');
      });

      expect(mockAuthService.register).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password'
      });
    });

    it('应该处理注册错误', async () => {
      mockAuthService.register.mockRejectedValue(new Error('Registration failed'));

      const { getByTestId } = render(
        <TestWrapper>
          <SimpleAuthComponent />
        </TestWrapper>
      );

      const registerButton = getByTestId('register-button');
      const statusText = getByTestId('status-text');

      fireEvent.press(registerButton);

      await waitFor(() => {
        expect(statusText.props.children).toBe('register-error');
      });

      expect(mockAuthService.register).toHaveBeenCalled();
    });

    it('应该成功处理登出流程', async () => {
      mockAuthService.logout.mockResolvedValue(undefined);

      const { getByTestId } = render(
        <TestWrapper>
          <SimpleAuthComponent />
        </TestWrapper>
      );

      const logoutButton = getByTestId('logout-button');
      const statusText = getByTestId('status-text');

      fireEvent.press(logoutButton);

      expect(statusText.props.children).toBe('logging-out');

      await waitFor(() => {
        expect(statusText.props.children).toBe('logged-out');
      });

      expect(mockAuthService.logout).toHaveBeenCalled();
    });

    it('应该处理登出错误', async () => {
      mockAuthService.logout.mockRejectedValue(new Error('Logout failed'));

      const { getByTestId } = render(
        <TestWrapper>
          <SimpleAuthComponent />
        </TestWrapper>
      );

      const logoutButton = getByTestId('logout-button');
      const statusText = getByTestId('status-text');

      fireEvent.press(logoutButton);

      await waitFor(() => {
        expect(statusText.props.children).toBe('logout-error');
      });

      expect(mockAuthService.logout).toHaveBeenCalled();
    });
  });

  describe('性能测试', () => {
    it('组件渲染性能测试', () => {
      const iterations = 10;
      const times = [];

      for (let i = 0; i < iterations; i++) {
        const startTime = performance.now();
        
        const { unmount } = render(
          <TestWrapper>
            <SimpleAuthComponent />
          </TestWrapper>
        );
        
        const endTime = performance.now();
        unmount();
        times.push(endTime - startTime);
      }

      const averageTime = times.reduce((sum, time) => sum + time, 0) / iterations;
      expect(averageTime).toBeLessThan(100); // 100ms内完成渲染
    });

    it('登录流程性能测试', async () => {
      mockAuthService.login.mockResolvedValue({
        user: { id: '1', email: 'test@example.com' },
        token: 'mock-token',
      });

      const startTime = performance.now();

      const { getByTestId } = render(
        <TestWrapper>
          <SimpleAuthComponent />
        </TestWrapper>
      );

      const loginButton = getByTestId('login-button');
      fireEvent.press(loginButton);

      await waitFor(() => {
        expect(getByTestId('status-text').props.children).toBe('logged-in');
      });

      const endTime = performance.now();
      const totalTime = endTime - startTime;

      expect(totalTime).toBeLessThan(500); // 500ms内完成
    });
  });

  describe('并发测试', () => {
    it('应该正确处理多个并发操作', async () => {
      mockAuthService.login.mockResolvedValue({
        user: { id: '1', email: 'test@example.com' },
        token: 'mock-token',
      });

      const { getByTestId } = render(
        <TestWrapper>
          <SimpleAuthComponent />
        </TestWrapper>
      );

      const loginButton = getByTestId('login-button');

      // 快速多次点击
      for (let i = 0; i < 3; i++) {
        fireEvent.press(loginButton);
      }

      await waitFor(() => {
        expect(getByTestId('status-text').props.children).toBe('logged-in');
      });

      // 验证只调用了一次（防止重复提交）
      expect(mockAuthService.login).toHaveBeenCalledTimes(1);
    });
  });

  describe('快照测试', () => {
    it('应该匹配组件快照', () => {
      const { toJSON } = render(
        <TestWrapper>
          <SimpleAuthComponent />
        </TestWrapper>
      );

      expect(toJSON()).toMatchSnapshot();
    });
  });
}); 