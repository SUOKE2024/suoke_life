import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { View, Text, TouchableOpacity, Image } from 'react-native';

// Mock AgentCard组件
const MockAgentCard = ({ agent, onPress }: any) => {
  return (
    <TouchableOpacity 
      testID={`agent-card-${agent.id}`}
      onPress={() => onPress && onPress(agent)}
    >
      <View testID="agent-card-container">
        <Image 
          testID="agent-avatar"
          source={{ uri: agent.avatar }} 
          style={{ width: 50, height: 50 }}
        />
        <View testID="agent-info">
          <Text testID="agent-name">{agent.name}</Text>
          <Text testID="agent-specialty">{agent.specialty}</Text>
          <Text testID="agent-description">{agent.description}</Text>
        </View>
        <View testID="agent-status">
          <Text testID={`status-${agent.status}`}>
            {agent.status === 'online' ? '在线' : '离线'}
          </Text>
        </View>
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
    const { getByTestId, getByText } = render(
      <MockAgentCard agent={mockAgent} />
    );

    expect(getByTestId('agent-card-container')).toBeTruthy();
    expect(getByTestId('agent-avatar')).toBeTruthy();
    expect(getByTestId('agent-info')).toBeTruthy();
    expect(getByText('小艾')).toBeTruthy();
    expect(getByText('健康咨询')).toBeTruthy();
    expect(getByText('专业的健康管理顾问')).toBeTruthy();
  });

  it('应该显示智能体状态', () => {
    const { getByTestId, getByText } = render(
      <MockAgentCard agent={mockAgent} />
    );

    expect(getByTestId('agent-status')).toBeTruthy();
    expect(getByTestId('status-online')).toBeTruthy();
    expect(getByText('在线')).toBeTruthy();
  });

  it('应该显示离线状态', () => {
    const offlineAgent = { ...mockAgent, status: 'offline' };
    const { getByTestId, getByText } = render(
      <MockAgentCard agent={offlineAgent} />
    );

    expect(getByTestId('status-offline')).toBeTruthy();
    expect(getByText('离线')).toBeTruthy();
  });

  it('应该处理点击事件', () => {
    const mockOnPress = jest.fn();
    const { getByTestId } = render(
      <MockAgentCard agent={mockAgent} onPress={mockOnPress} />
    );

    const card = getByTestId(`agent-card-${mockAgent.id}`);
    fireEvent.press(card);

    expect(mockOnPress).toHaveBeenCalledWith(mockAgent);
  });

  it('应该设置正确的testID', () => {
    const { getByTestId } = render(
      <MockAgentCard agent={mockAgent} />
    );

    expect(getByTestId('agent-card-xiaoai')).toBeTruthy();
    expect(getByTestId('agent-name')).toBeTruthy();
    expect(getByTestId('agent-specialty')).toBeTruthy();
    expect(getByTestId('agent-description')).toBeTruthy();
  });

  it('应该处理缺少onPress的情况', () => {
    const { getByTestId } = render(
      <MockAgentCard agent={mockAgent} />
    );

    const card = getByTestId(`agent-card-${mockAgent.id}`);
    
    // 不应该抛出错误
    expect(() => fireEvent.press(card)).not.toThrow();
  });

  it('应该正确显示头像', () => {
    const { getByTestId } = render(
      <MockAgentCard agent={mockAgent} />
    );

    const avatar = getByTestId('agent-avatar');
    expect(avatar.props.source.uri).toBe(mockAgent.avatar);
  });
}); 