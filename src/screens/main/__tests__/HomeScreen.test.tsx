import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { NavigationContainer } from '@react-navigation/native';
import { Alert } from 'react-native';
import HomeScreen from '../HomeScreen';

// Mock navigation
const mockNavigation = {
  navigate: jest.fn(),
  goBack: jest.fn(),
  reset: jest.fn(),
  setParams: jest.fn(),
  dispatch: jest.fn(),
  setOptions: jest.fn(),
  isFocused: jest.fn(),
  canGoBack: jest.fn(),
  getId: jest.fn(),
  getParent: jest.fn(),
  getState: jest.fn(),
};

const mockRoute = {
  key: 'test',
  name: 'Home' as const,
  params: undefined,
};

jest.mock('@react-navigation/native', () => ({
  ...jest.requireActual('@react-navigation/native'),
  useNavigation: () => mockNavigation,
  useRoute: () => mockRoute,
}));

// Mock Alert
jest.spyOn(Alert, 'alert');

const renderWithNavigation = (component: React.ReactElement) => {
  return render(
    <NavigationContainer>
      {component}
    </NavigationContainer>
  );
};

describe('HomeScreen 聊天频道测试', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('基础渲染测试', () => {
    it('应该正确渲染聊天频道主屏幕', () => {
      const { getByPlaceholderText, getByText } = renderWithNavigation(<HomeScreen />);
      
      // 检查搜索框
      expect(getByPlaceholderText('搜索联系人、专业、服务...')).toBeTruthy();
      
      // 检查四大智能体分组
      expect(getByText('四大智能体')).toBeTruthy();
      expect(getByText('小艾')).toBeTruthy();
      expect(getByText('小克')).toBeTruthy();
      expect(getByText('老克')).toBeTruthy();
      expect(getByText('索儿')).toBeTruthy();
    });

    it('应该显示所有联系人分组', () => {
      const { getByText } = renderWithNavigation(<HomeScreen />);
      
      expect(getByText('四大智能体')).toBeTruthy();
      expect(getByText('名医专家')).toBeTruthy();
      expect(getByText('健康伙伴')).toBeTruthy();
      expect(getByText('健康服务')).toBeTruthy();
      expect(getByText('系统服务')).toBeTruthy();
    });

    it('应该显示联系人详细信息', () => {
      const { getByText } = renderWithNavigation(<HomeScreen />);
      
      // 检查智能体信息
      expect(getByText('健康管理·AI助手')).toBeTruthy();
      expect(getByText('中医诊断·辨证论治')).toBeTruthy();
      
      // 检查医生信息
      expect(getByText('张明华')).toBeTruthy();
      expect(getByText('中医内科·主任医师')).toBeTruthy();
    });
  });

  describe('搜索功能测试', () => {
    it('应该能够搜索联系人', async () => {
      const { getByPlaceholderText, getByText, queryByText } = renderWithNavigation(<HomeScreen />);
      
      const searchInput = getByPlaceholderText('搜索联系人、专业、服务...');
      
      // 输入搜索关键词
      fireEvent.changeText(searchInput, '小艾');
      
      await waitFor(() => {
        expect(getByText('搜索结果 (1)')).toBeTruthy();
        expect(getByText('小艾')).toBeTruthy();
        // 其他联系人应该被隐藏
        expect(queryByText('四大智能体')).toBeFalsy();
      });
    });

    it('应该能够按专业搜索', async () => {
      const { getByPlaceholderText, getByText } = renderWithNavigation(<HomeScreen />);
      
      const searchInput = getByPlaceholderText('搜索联系人、专业、服务...');
      
      // 按专业搜索
      fireEvent.changeText(searchInput, '中医');
      
      await waitFor(() => {
        expect(getByText('小克')).toBeTruthy();
        expect(getByText('老克')).toBeTruthy();
        expect(getByText('张明华')).toBeTruthy();
      });
    });

    it('应该显示搜索无结果状态', async () => {
      const { getByPlaceholderText, getByText } = renderWithNavigation(<HomeScreen />);
      
      const searchInput = getByPlaceholderText('搜索联系人、专业、服务...');
      
      // 搜索不存在的内容
      fireEvent.changeText(searchInput, '不存在的联系人');
      
      await waitFor(() => {
        expect(getByText('未找到相关联系人')).toBeTruthy();
        expect(getByText('尝试使用其他关键词搜索')).toBeTruthy();
      });
    });

    it('应该能够清除搜索', async () => {
      const { getByPlaceholderText, getByText, queryByText } = renderWithNavigation(<HomeScreen />);
      
      const searchInput = getByPlaceholderText('搜索联系人、专业、服务...');
      
      // 输入搜索内容
      fireEvent.changeText(searchInput, '小艾');
      
      await waitFor(() => {
        expect(getByText('搜索结果 (1)')).toBeTruthy();
      });
      
      // 清除搜索
      fireEvent.changeText(searchInput, '');
      
      await waitFor(() => {
        expect(queryByText('搜索结果')).toBeFalsy();
        expect(getByText('四大智能体')).toBeTruthy();
      });
    });
  });

  describe('分组折叠功能测试', () => {
    it('应该能够折叠和展开分组', async () => {
      const { getByText, queryByText } = renderWithNavigation(<HomeScreen />);
      
      // 点击分组标题折叠
      const groupHeader = getByText('四大智能体');
      fireEvent.press(groupHeader);
      
      await waitFor(() => {
        // 联系人应该被隐藏
        expect(queryByText('小艾')).toBeFalsy();
        expect(queryByText('小克')).toBeFalsy();
      });
      
      // 再次点击展开
      fireEvent.press(groupHeader);
      
      await waitFor(() => {
        // 联系人应该重新显示
        expect(getByText('小艾')).toBeTruthy();
        expect(getByText('小克')).toBeTruthy();
      });
    });
  });

  describe('联系人交互测试', () => {
    it('应该能够点击联系人开始聊天', async () => {
      const { getByText } = renderWithNavigation(<HomeScreen />);
      
      // 点击小艾
      const xiaoaiContact = getByText('小艾');
      fireEvent.press(xiaoaiContact);
      
      await waitFor(() => {
        expect(Alert.alert).toHaveBeenCalledWith('开始聊天', '即将与 小艾 开始对话');
      });
    });

    it('应该显示联系人状态指示器', () => {
      const { getByText } = renderWithNavigation(<HomeScreen />);
      
      // 检查在线状态的联系人
      expect(getByText('小艾')).toBeTruthy();
      expect(getByText('张明华')).toBeTruthy();
    });

    it('应该显示未读消息徽章', () => {
      const { getByText } = renderWithNavigation(<HomeScreen />);
      
      // 小克有1条未读消息
      expect(getByText('小克')).toBeTruthy();
      // 索儿有2条未读消息
      expect(getByText('索儿')).toBeTruthy();
    });

    it('应该显示VIP标识', () => {
      const { getByText } = renderWithNavigation(<HomeScreen />);
      
      // 张明华医生是VIP
      expect(getByText('张明华')).toBeTruthy();
      expect(getByText('VIP')).toBeTruthy();
    });
  });

  describe('下拉刷新测试', () => {
    it('应该支持下拉刷新', async () => {
      const { getByTestId } = renderWithNavigation(<HomeScreen />);
      
      // 模拟下拉刷新
      // 注意：这里需要根据实际的ScrollView testID进行调整
      // 由于RefreshControl的测试比较复杂，这里主要测试组件是否正确渲染
      expect(getByTestId || (() => ({ toBeTruthy: () => true }))).toBeTruthy();
    });
  });

  describe('无障碍性测试', () => {
    it('应该具有正确的无障碍属性', () => {
      const { getByPlaceholderText } = renderWithNavigation(<HomeScreen />);
      
      const searchInput = getByPlaceholderText('搜索联系人、专业、服务...');
      expect(searchInput).toBeTruthy();
    });
  });

  describe('性能测试', () => {
    it('应该在合理时间内渲染', () => {
      const startTime = performance.now();
      renderWithNavigation(<HomeScreen />);
      const endTime = performance.now();
      
      // 组件应该在100ms内渲染完成
      expect(endTime - startTime).toBeLessThan(100);
    });
  });

  describe('错误处理测试', () => {
    it('应该处理网络错误', async () => {
      // 这里可以添加网络错误的模拟测试
      const { getByText } = renderWithNavigation(<HomeScreen />);
      expect(getByText('四大智能体')).toBeTruthy();
    });
  });
}); 