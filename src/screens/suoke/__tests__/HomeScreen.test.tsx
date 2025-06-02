import React from 'react';
import { render } from '@testing-library/react-native';
import HomeScreen from '../HomeScreen';

// Mock navigation
jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({
    navigate: jest.fn(),
    goBack: jest.fn(),
  }),
}));

// Mock SafeAreaView
jest.mock('react-native-safe-area-context', () => ({
  SafeAreaView: ({ children }: any) => children,
}));

describe('HomeScreen 聊天频道测试', () => {
  it('应该正确渲染', () => {
    const { getByPlaceholderText } = render(<HomeScreen />);
    
    // 检查搜索框是否存在
    expect(getByPlaceholderText('搜索联系人或专业领域')).toBeTruthy();
  });

  it('应该显示四大智能体分组', () => {
    const { getByText } = render(<HomeScreen />);
    
    // 检查四大智能体分组标题
    expect(getByText('四大智能体')).toBeTruthy();
  });

  it('应该显示名医专家分组', () => {
    const { getByText } = render(<HomeScreen />);
    
    // 检查名医专家分组标题
    expect(getByText('名医专家')).toBeTruthy();
  });

  it('应该显示智能体联系人', () => {
    const { getByText } = render(<HomeScreen />);
    
    // 检查智能体是否显示
    expect(getByText('小艾')).toBeTruthy();
    expect(getByText('小克')).toBeTruthy();
    expect(getByText('老克')).toBeTruthy();
    expect(getByText('索儿')).toBeTruthy();
  });

  it('应该显示名医联系人', () => {
    const { getByText } = render(<HomeScreen />);
    
    // 检查名医是否显示
    expect(getByText('张仲景')).toBeTruthy();
    expect(getByText('华佗')).toBeTruthy();
  });
}); 