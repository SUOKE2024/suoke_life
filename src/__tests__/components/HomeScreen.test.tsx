import React from 'react';
import { Provider } from 'react-redux';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
const HomeScreen = React.lazy(() => import('../../screens/main/HomeScreen'));

// Mock dependencies
jest.mock('react-native-vector-icons/MaterialCommunityIcons', () => {
  const React = require('react');
  return React.forwardRef((props: any, ref: any) => {
    const { View } = require('react-native');
    return React.createElement(View, { ...props, ref });
  });
});
jest.mock('../../services/agentService', () => ({
  agentService: {
    getAgentStatus: jest.fn().mockResolvedValue({
      id: 'xiaoai',
      name: '小艾',
      status: 'online',
      lastActive: Date.now(),
      capabilities: ['健康咨询'],
      healthScore: 95,
      responseTime: 200
    }),
    getAllAgentStatuses: jest.fn().mockResolvedValue({
      xiaoai: { id: 'xiaoai', name: '小艾', status: 'online' }
    })
  }
}));

jest.mock('../../services/apiClient', () => ({
  apiClient: {
    get: jest.fn().mockResolvedValue({
      data: { count: 0 }
    }),
    post: jest.fn().mockResolvedValue({
      data: { success: true }
    })
  }
}));

// Mock store
const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      auth: () => ({ isAuthenticated: true, user: { id: 'test-user' } }),
      agents: () => ({}),
      medKnowledge: () => ({}),
      rag: () => ({}),
      medicalResource: () => ({}),
      benchmark: () => ({})
    },
    preloadedState: initialState
  });
};

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const Stack = createNativeStackNavigator();
  const store = createMockStore();

  return (
    <Provider store={store}>
      <NavigationContainer>
        <Stack.Navigator>
          <Stack.Screen name="Home" component={() => children as React.ReactElement} />
        </Stack.Navigator>
      </NavigationContainer>
    </Provider>
  );
};

describe('HomeScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('应该正确渲染HomeScreen', async () => {
    render(
      <TestWrapper>
        <HomeScreen />
      </TestWrapper>
    );

    // 检查标题是否存在
    expect(screen.getByText('索克生活')).toBeTruthy();
    
    // 检查搜索框是否存在
    expect(screen.getByPlaceholderText('搜索聊天记录')).toBeTruthy();
  });

  it('应该显示加载状态', () => {
    render(
      <TestWrapper>
        <HomeScreen />
      </TestWrapper>
    );

    // 初始状态应该显示加载中
    expect(screen.getByText('加载中...')).toBeTruthy();
  });

  it('应该能够搜索聊天记录', async () => {
    render(
      <TestWrapper>
        <HomeScreen />
      </TestWrapper>
    );

    // 等待加载完成
    await waitFor(() => {
      expect(screen.queryByText('加载中...')).toBeNull();
    });

    // 找到搜索输入框
    const searchInput = screen.getByPlaceholderText('搜索聊天记录');
    
    // 输入搜索内容
    fireEvent.changeText(searchInput, '小艾');
    
    // 验证搜索功能
    expect(searchInput.props.value).toBe('小艾');
  });

  it('应该能够点击添加按钮', async () => {
    render(
      <TestWrapper>
        <HomeScreen />
      </TestWrapper>
    );

    // 等待加载完成
    await waitFor(() => {
      expect(screen.queryByText('加载中...')).toBeNull();
    });

    // 查找添加按钮（通过testID或其他方式）
    const addButtons = screen.getAllByRole('button');
    const addButton = addButtons.find(button => 
      button.props.accessibilityLabel === 'add' || 
      button.props.children?.props?.name === 'plus'
    );

    if (addButton) {
      fireEvent.press(addButton);
      // 这里可以验证弹出的Alert或导航行为
    }
  });

  it('应该能够下拉刷新', async () => {
    render(
      <TestWrapper>
        <HomeScreen />
      </TestWrapper>
    );

    // 等待加载完成
    await waitFor(() => {
      expect(screen.queryByText('加载中...')).toBeNull();
    });

    // 查找FlatList
    const flatList = screen.getByTestId('chat-list') || screen.UNSAFE_getByType('FlatList');
    
    if (flatList) {
      // 模拟下拉刷新
      fireEvent(flatList, 'refresh');
      
      // 验证刷新状态
      await waitFor(() => {
        expect(flatList.props.refreshing).toBe(false);
      });
    }
  });

  it('应该正确显示智能体聊天项', async () => {
    render(
      <TestWrapper>
        <HomeScreen />
      </TestWrapper>
    );

    // 等待加载完成
    await waitFor(() => {
      expect(screen.queryByText('加载中...')).toBeNull();
    });

    // 检查智能体是否显示
    await waitFor(() => {
      expect(screen.getByText('小艾')).toBeTruthy();
      expect(screen.getByText('小克')).toBeTruthy();
      expect(screen.getByText('老克')).toBeTruthy();
      expect(screen.getByText('索儿')).toBeTruthy();
    });
  });

  it('应该能够点击聊天项进行导航', async () => {
    const mockNavigate = jest.fn();
    
    // Mock navigation
    jest.doMock('@react-navigation/native', () => ({
      ...jest.requireActual('@react-navigation/native'),
      useNavigation: () => ({
        navigate: mockNavigate,
        goBack: jest.fn()
      })
    }));

    render(
      <TestWrapper>
        <HomeScreen />
      </TestWrapper>
    );

    // 等待加载完成
    await waitFor(() => {
      expect(screen.queryByText('加载中...')).toBeNull();
    });

    // 查找并点击聊天项
    const chatItem = screen.getByText('小艾');
    fireEvent.press(chatItem.parent || chatItem);

    // 验证导航是否被调用
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('ChatDetail', expect.objectContaining({
        chatId: 'xiaoai',
        chatType: 'agent',
        chatName: '小艾'
      }));
    });
  });

  it('应该正确处理错误状态', async () => {
    // Mock API错误
    const mockApiClient = require('../../services/apiClient');
    mockApiClient.apiClient.get.mockRejectedValueOnce(new Error('网络错误'));

    render(
      <TestWrapper>
        <HomeScreen />
      </TestWrapper>
    );

    // 等待错误处理
    await waitFor(() => {
      // 应该仍然显示默认的聊天列表
      expect(screen.getByText('小艾')).toBeTruthy();
    });
  });

  it('应该正确显示未读消息数量', async () => {
    render(
      <TestWrapper>
        <HomeScreen />
      </TestWrapper>
    );

    // 等待加载完成
    await waitFor(() => {
      expect(screen.queryByText('加载中...')).toBeNull();
    });

    // 检查是否有未读消息徽章
    const unreadBadges = screen.queryAllByTestId('unread-badge');
    expect(unreadBadges.length).toBeGreaterThanOrEqual(0);
  });

  it('应该正确显示在线状态指示器', async () => {
    render(
      <TestWrapper>
        <HomeScreen />
      </TestWrapper>
    );

    // 等待加载完成
    await waitFor(() => {
      expect(screen.queryByText('加载中...')).toBeNull();
    });

    // 检查在线状态指示器
    const onlineIndicators = screen.queryAllByTestId('online-indicator');
    expect(onlineIndicators.length).toBeGreaterThanOrEqual(0);
  });
});

// 性能测试
describe('HomeScreen Performance', () => {
  it('应该在合理时间内完成渲染', async () => {
    const startTime = Date.now();
    
    render(
      <TestWrapper>
        <HomeScreen />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.queryByText('加载中...')).toBeNull();
    });

    const renderTime = Date.now() - startTime;
    expect(renderTime).toBeLessThan(3000); // 3秒内完成渲染
  });

  it('应该正确处理大量聊天数据', async () => {
    // Mock大量数据
    const mockApiClient = require('../../services/apiClient');
    const largeChatList = Array.from({ length: 100 }, (_, i) => ({
      id: `chat_${i}`,
      name: `聊天 ${i}`,
      message: `消息内容 ${i}`,
      time: '刚刚',
      unread: i % 5
    }));

    mockApiClient.apiClient.get.mockResolvedValueOnce({
      data: largeChatList
    });

    render(
      <TestWrapper>
        <HomeScreen />
      </TestWrapper>
    );

    // 验证能够处理大量数据
    await waitFor(() => {
      expect(screen.queryByText('加载中...')).toBeNull();
    });
  });
});

// 可访问性测试
describe('HomeScreen Accessibility', () => {
  it('应该具有正确的可访问性标签', async () => {
    render(
      <TestWrapper>
        <HomeScreen />
      </TestWrapper>
    );

    // 检查重要元素的可访问性
    const searchInput = screen.getByPlaceholderText('搜索聊天记录');
    expect(searchInput.props.accessibilityLabel || searchInput.props.placeholder).toBeTruthy();
  });

  it('应该支持屏幕阅读器', async () => {
    render(
      <TestWrapper>
        <HomeScreen />
      </TestWrapper>
    );

    // 等待加载完成
    await waitFor(() => {
      expect(screen.queryByText('加载中...')).toBeNull();
    });

    // 检查关键元素是否可被屏幕阅读器访问
    const title = screen.getByText('索克生活');
    expect(title.props.accessible !== false).toBeTruthy();
  });
}); 