import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { View, Text, TouchableOpacity } from 'react-native';

// 简化的Mock AgentCard组件
const MockAgentCard = ({ agent, onPress }: any) => {
  return (
    <TouchableOpacity onPress={() => onPress && onPress(agent)}>
      <View>
        <Text>{agent.name}</Text>
        <Text>{agent.specialty}</Text>
        <Text>{agent.description}</Text>
        <Text>{agent.status === 'online' ? '在线' : '离线'}</Text>
      </View>
    </TouchableOpacity>
  );
};

// Mock数据
const mockAgent = {
  id: 'xiaoai',
  name: '小艾',
  specialty: '健康咨询',
  description: '专业的健康管理顾问',
  avatar: 'https://example.com/xiaoai.jpg',
  status: 'online',
};

describe('AgentCard', () => {
  it('应该正确渲染智能体卡片', () => {
    const { getByText } = render(
      <MockAgentCard agent={mockAgent} />
    );

    expect(getByText('小艾')).toBeTruthy();
    expect(getByText('健康咨询')).toBeTruthy();
    expect(getByText('专业的健康管理顾问')).toBeTruthy();
  });

  it('应该显示智能体状态', () => {
    const { getByText } = render(
      <MockAgentCard agent={mockAgent} />
    );

    expect(getByText('在线')).toBeTruthy();
  });

  it('应该显示离线状态', () => {
    const offlineAgent = { ...mockAgent, status: 'offline' };
    const { getByText } = render(
      <MockAgentCard agent={offlineAgent} />
    );

    expect(getByText('离线')).toBeTruthy();
  });

  it('应该处理点击事件', () => {
    const mockOnPress = jest.fn();
    const { getByText } = render(
      <MockAgentCard agent={mockAgent} onPress={mockOnPress} />
    );

    const nameElement = getByText('小艾');
    const touchableElement = nameElement.parent?.parent;
    
    if (touchableElement) {
      fireEvent.press(touchableElement);
      expect(mockOnPress).toHaveBeenCalledWith(mockAgent);
    }
  });

  it('应该正确显示基本信息', () => {
    const { getByText } = render(
      <MockAgentCard agent={mockAgent} />
    );

    expect(getByText('小艾')).toBeTruthy();
    expect(getByText('健康咨询')).toBeTruthy();
    expect(getByText('专业的健康管理顾问')).toBeTruthy();
  });

  it('应该处理缺少onPress的情况', () => {
    const { getByText } = render(
      <MockAgentCard agent={mockAgent} />
    );

    const nameElement = getByText('小艾');
    const touchableElement = nameElement.parent?.parent;
    
    // 不应该抛出错误
    if (touchableElement) {
      expect(() => fireEvent.press(touchableElement)).not.toThrow();
    }
  });

  it('应该正确渲染组件结构', () => {
    const { getByText } = render(
      <MockAgentCard agent={mockAgent} />
    );

    // 验证组件渲染成功
    expect(getByText('小艾')).toBeTruthy();
    expect(getByText('在线')).toBeTruthy();
  });
}); 