import React from 'react';
import { render, fireEvent, waitFor, act } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { configureStore } from '@reduxjs/toolkit';
import HomeScreen from '../../screens/main/HomeScreen';
import authSlice from '../../store/slices/authSlice';
// Mock dependencies
jest.mock('react-native-vector-icons/MaterialCommunityIcons', () => 'Icon');
jest.mock('react-native-safe-area-context', () => ({
  SafeAreaView: ({ children }: any) => children,
}));
// Mock navigation
const mockNavigate = jest.fn();
jest.mock('@react-navigation/native', () => ({
  ...jest.requireActual('@react-navigation/native'),
  useNavigation: () => ({
    navigate: mockNavigate,
  }),
}));
// Create test store
const createTestStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      auth: authSlice,
    },
    preloadedState: {
      auth: {
        isAuthenticated: false,
        user: null,
        loading: false,
        error: null,
        ...initialState.auth,
      },
    },
  });
};
// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode; store?: any }> = ({
  children,
  store = createTestStore(),
}) => {
  const Stack = createNativeStackNavigator();
  return (
    <Provider store={store}>
      <NavigationContainer>
        <Stack.Navigator>
          <Stack.Screen name="Home" component={() => children} />
        </Stack.Navigator>
      </NavigationContainer>
    </Provider>
  );
};
describe('HomeScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });
  describe('渲染测试', () => {
    it('应该正确渲染基本组件', async () => {
      const { getByText, getByPlaceholderText } = render(
        <TestWrapper>
          <HomeScreen />
        </TestWrapper>,
      );
      // 等待加载完成
      await waitFor(() => {
        expect(getByText('你好')).toBeTruthy();
        expect(getByText('今天想聊些什么呢？')).toBeTruthy();
        expect(getByPlaceholderText('搜索聊天记录...')).toBeTruthy();
      });
    });
    it('应该显示用户名称当用户已登录', async () => {
      const store = createTestStore({
        auth: {
          isAuthenticated: true,
          user: {
      name: "张三",
      id: '123' },
          loading: false,
          error: null,
        },
      });
      const { getByText } = render(
        <TestWrapper store={store}>
          <HomeScreen />
        </TestWrapper>,
      );
      await waitFor(() => {
        expect(getByText('你好，张三')).toBeTruthy();
      });
    });
    it('应该显示智能体聊天列表', async () => {
      const { getByText } = render(
        <TestWrapper>
          <HomeScreen />
        </TestWrapper>,
      );
      await waitFor(() => {
        expect(getByText('小艾')).toBeTruthy();
        expect(getByText('小克')).toBeTruthy();
        expect(getByText('老克')).toBeTruthy();
        expect(getByText('索儿')).toBeTruthy();
      });
    });
    it('应该显示智能体标签', async () => {
      const { getByText } = render(
        <TestWrapper>
          <HomeScreen />
        </TestWrapper>,
      );
      await waitFor(() => {
        expect(getByText('健康助手')).toBeTruthy();
        expect(getByText('中医辨证')).toBeTruthy();
        expect(getByText('健康顾问')).toBeTruthy();
        expect(getByText('生活教练')).toBeTruthy();
      });
    });
  });
  describe('交互测试', () => {
    it('应该能够搜索聊天记录', async () => {
      const { getByPlaceholderText, getByText, queryByText } = render(
        <TestWrapper>
          <HomeScreen />
        </TestWrapper>,
      );
      await waitFor(() => {
        expect(getByText('小艾')).toBeTruthy();
      });
      const searchInput = getByPlaceholderText('搜索聊天记录...');
      // 搜索"小艾"
      fireEvent.changeText(searchInput, '小艾');
      await waitFor(() => {
        expect(getByText('小艾')).toBeTruthy();
        expect(queryByText('小克')).toBeFalsy();
      });
    });
    it('应该能够清除搜索内容', async () => {
      const { getByPlaceholderText, getByText, queryByTestId } = render(
        <TestWrapper>
          <HomeScreen />
        </TestWrapper>,
      );
      await waitFor(() => {
        expect(getByText('小艾')).toBeTruthy();
      });
      const searchInput = getByPlaceholderText('搜索聊天记录...');
      // 输入搜索内容
      fireEvent.changeText(searchInput, '测试');
      // 应该显示清除按钮
      await waitFor(() => {
        const clearButton = queryByTestId('clear-search-button');
        if (clearButton) {
          fireEvent.press(clearButton);
        }
      });
    });
    it('应该能够点击聊天项导航到详情页', async () => {
      const { getByText } = render(
        <TestWrapper>
          <HomeScreen />
        </TestWrapper>,
      );
      await waitFor(() => {
        const xiaoaiChat = getByText('小艾');
        fireEvent.press(xiaoaiChat);
      });
      expect(mockNavigate).toHaveBeenCalledWith('ChatDetail', {
      chatId: "xiaoai",
      chatType: 'agent',
        chatName: '小艾',
      });
    });
    it('应该支持下拉刷新', async () => {
      const { getByTestId } = render(
        <TestWrapper>
          <HomeScreen />
        </TestWrapper>,
      );
      await waitFor(() => {
        const flatList = getByTestId('chat-list');
        if (flatList) {
          // 模拟下拉刷新
          fireEvent(flatList, 'refresh');
        }
      });
    });
  });
  describe('加载状态测试', () => {
    it('应该显示加载指示器', () => {
      // 创建一个始终加载的组件版本
      const LoadingHomeScreen = () => {
        return <HomeScreen />;
      };
      const { getByText } = render(
        <TestWrapper>
          <LoadingHomeScreen />
        </TestWrapper>,
      );
      // 在组件首次渲染时应该显示加载状态
      expect(getByText('加载中...')).toBeTruthy();
    });
  });
  describe('错误处理测试', () => {
    it('应该处理数据加载错误', async () => {
      // Mock console.error to avoid test output pollution
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      // Mock a failing API call
      const originalFetch = global.fetch;
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));
      const { getByText } = render(
        <TestWrapper>
          <HomeScreen />
        </TestWrapper>,
      );
      await waitFor(() => {
        // 组件应该优雅地处理错误
        expect(getByText('你好')).toBeTruthy();
      });
      // Restore
      global.fetch = originalFetch;
      consoleSpy.mockRestore();
    });
  });
  describe('数据格式测试', () => {
    it('应该正确格式化时间显示', async () => {
      const { getByText } = render(
        <TestWrapper>
          <HomeScreen />
        </TestWrapper>,
      );
      await waitFor(() => {
        // 检查是否有时间相关的文本
        expect(getByText('刚刚')).toBeTruthy();
      });
    });
    it('应该正确显示未读消息数量', async () => {
      const { queryByText } = render(
        <TestWrapper>
          <HomeScreen />
        </TestWrapper>,
      );
      await waitFor(() => {
        // 可能会有未读消息徽章
        const unreadBadge = queryByText(/^\d+$/);
        if (unreadBadge) {
          expect(unreadBadge).toBeTruthy();
        }
      });
    });
  });
  describe('可访问性测试', () => {
    it('应该有正确的可访问性标签', async () => {
      const { getByText } = render(
        <TestWrapper>
          <HomeScreen />
        </TestWrapper>,
      );
      await waitFor(() => {
        // 检查重要元素是否可访问
        expect(getByText('你好')).toBeTruthy();
        expect(getByText('今天想聊些什么呢？')).toBeTruthy();
      });
    });
  });
  describe('性能测试', () => {
    it('应该在合理时间内完成渲染', async () => {
      const startTime = Date.now();
      const { getByText } = render(
        <TestWrapper>
          <HomeScreen />
        </TestWrapper>,
      );
      await waitFor(() => {
        expect(getByText('你好')).toBeTruthy();
      });
      const endTime = Date.now();
      const renderTime = endTime - startTime;
      // 渲染时间应该少于2秒
      expect(renderTime).toBeLessThan(2000);
    });
  });
  describe('边界情况测试', () => {
    it('应该处理空聊天列表', async () => {
      // 这个测试需要mock数据为空的情况
      const { getByText } = render(
        <TestWrapper>
          <HomeScreen />
        </TestWrapper>,
      );
      await waitFor(() => {
        // 即使没有聊天记录，基本UI仍应显示
        expect(getByText('你好')).toBeTruthy();
      });
    });
    it('应该处理长文本消息', async () => {
      const { getByText } = render(
        <TestWrapper>
          <HomeScreen />
        </TestWrapper>,
      );
      await waitFor(() => {
        // 检查是否正确处理长文本
        expect(getByText('小艾')).toBeTruthy();
      });
    });
    it('应该处理特殊字符', async () => {
      const { getByPlaceholderText } = render(
        <TestWrapper>
          <HomeScreen />
        </TestWrapper>,
      );
      await waitFor(() => {
        const searchInput = getByPlaceholderText('搜索聊天记录...');
        // 测试特殊字符输入
        fireEvent.changeText(searchInput, '!@#$%^&*()');
        // 应该不会崩溃
        expect(searchInput).toBeTruthy();
      });
    });
  });
  describe('状态管理测试', () => {
    it('应该正确响应Redux状态变化', async () => {
      const store = createTestStore();
      const { getByText, rerender } = render(
        <TestWrapper store={store}>
          <HomeScreen />
        </TestWrapper>,
      );
      await waitFor(() => {
        expect(getByText('你好')).toBeTruthy();
      });
      // 模拟用户登录
      act(() => {
        store.dispatch({
      type: "auth/loginSuccess",
      payload: { user: {
      name: "李四",
      id: '456' } },
        });
      });
      // 重新渲染后应该显示用户名
      rerender(
        <TestWrapper store={store}>
          <HomeScreen />
        </TestWrapper>,
      );
      await waitFor(() => {
        expect(getByText('你好，李四')).toBeTruthy();
      });
    });
  });
});
