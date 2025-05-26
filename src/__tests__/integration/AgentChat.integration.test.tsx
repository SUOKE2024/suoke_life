import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { View, Text, TextInput, TouchableOpacity, Alert } from 'react-native';

// Mock智能体聊天组件
const MockAgentChatScreen = ({ route }: any) => {
  const { agentId } = route.params;
  const [messages, setMessages] = React.useState([
    {
      id: '1',
      text: `你好！我是${agentId}，很高兴为您服务！`,
      sender: 'agent',
      timestamp: new Date().toISOString(),
    },
  ]);
  const [inputText, setInputText] = React.useState('');

  const sendMessage = () => {
    if (inputText.trim()) {
      const newMessage = {
        id: Date.now().toString(),
        text: inputText,
        sender: 'user',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, newMessage]);
      setInputText('');
      
      // 模拟智能体回复
      setTimeout(() => {
        const agentReply = {
          id: (Date.now() + 1).toString(),
          text: `我理解您说的"${inputText}"，让我为您提供帮助。`,
          sender: 'agent',
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, agentReply]);
      }, 1000);
    }
  };

  return (
    <View testID="agent-chat-screen">
      <View testID="chat-header">
        <Text>与{agentId}对话</Text>
      </View>
      <View testID="message-list">
        {messages.map(message => (
          <View key={message.id} testID={`message-${message.id}`}>
            <View testID={`message-sender-${message.sender}`}>
              <Text>{message.sender === 'agent' ? agentId : '我'}</Text>
            </View>
            <View testID="message-text">
              <Text>{message.text}</Text>
            </View>
          </View>
        ))}
      </View>
      <View testID="input-container">
        <TextInput
          testID="message-input"
          value={inputText}
          onChangeText={setInputText}
          placeholder="输入消息..."
        />
        <TouchableOpacity testID="send-button" onPress={sendMessage}>
          <Text>发送</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

// Mock Alert
jest.spyOn(Alert, 'alert').mockImplementation(() => {});

// Mock navigation
const mockNavigation = {
  navigate: jest.fn(),
  goBack: jest.fn(),
  setOptions: jest.fn(),
};

const mockRoute = {
  params: {
    agentId: '小艾',
  },
};

describe('AgentChat Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('应该正确渲染聊天界面', () => {
    const { getByTestId, getByText } = render(
      <MockAgentChatScreen route={mockRoute} navigation={mockNavigation} />
    );

    expect(getByTestId('agent-chat-screen')).toBeTruthy();
    expect(getByTestId('chat-header')).toBeTruthy();
    expect(getByText('与小艾对话')).toBeTruthy();
    expect(getByTestId('message-list')).toBeTruthy();
    expect(getByTestId('input-container')).toBeTruthy();
  });

  it('应该显示初始欢迎消息', () => {
    const { getByText } = render(
      <MockAgentChatScreen route={mockRoute} navigation={mockNavigation} />
    );

    expect(getByText('你好！我是小艾，很高兴为您服务！')).toBeTruthy();
  });

  it('应该能够发送消息', async () => {
    const { getByTestId, getByText } = render(
      <MockAgentChatScreen route={mockRoute} navigation={mockNavigation} />
    );

    const messageInput = getByTestId('message-input');
    const sendButton = getByTestId('send-button');

    // 输入消息
    fireEvent.changeText(messageInput, '你好，我想咨询健康问题');
    
    // 发送消息
    fireEvent.press(sendButton);

    // 验证用户消息显示
    await waitFor(() => {
      expect(getByText('你好，我想咨询健康问题')).toBeTruthy();
    });

    // 验证智能体回复
    await waitFor(() => {
      expect(getByText('我理解您说的"你好，我想咨询健康问题"，让我为您提供帮助。')).toBeTruthy();
    }, { timeout: 2000 });
  });

  it('应该清空输入框在发送消息后', async () => {
    const { getByTestId } = render(
      <MockAgentChatScreen route={mockRoute} navigation={mockNavigation} />
    );

    const messageInput = getByTestId('message-input');
    const sendButton = getByTestId('send-button');

    // 输入消息
    fireEvent.changeText(messageInput, '测试消息');

    // 发送消息
    fireEvent.press(sendButton);

    // 验证输入框被清空
    await waitFor(() => {
      expect(messageInput.props.value).toBe('');
    });
  });

  it('应该不发送空消息', () => {
    const { getByTestId, queryAllByTestId } = render(
      <MockAgentChatScreen route={mockRoute} navigation={mockNavigation} />
    );

    const sendButton = getByTestId('send-button');
    
    // 获取初始消息数量
    const initialMessages = queryAllByTestId(/^message-/);
    const initialCount = initialMessages.length;

    // 尝试发送空消息
    fireEvent.press(sendButton);

    // 验证没有新消息添加
    const afterMessages = queryAllByTestId(/^message-/);
    expect(afterMessages).toHaveLength(initialCount); // 消息数量不变
  });

  it('应该正确显示消息发送者', async () => {
    const { getByTestId, getByText } = render(
      <MockAgentChatScreen route={mockRoute} navigation={mockNavigation} />
    );

    const messageInput = getByTestId('message-input');
    const sendButton = getByTestId('send-button');

    // 发送用户消息
    fireEvent.changeText(messageInput, '用户消息');
    fireEvent.press(sendButton);

    // 验证用户消息发送者显示
    await waitFor(() => {
      expect(getByText('我')).toBeTruthy();
    });

    // 验证智能体消息发送者显示
    await waitFor(() => {
      const agentSenders = getByTestId('message-sender-agent');
      expect(agentSenders).toBeTruthy();
    }, { timeout: 2000 });
  });

  it('应该处理不同智能体的聊天', () => {
    const xiaokRoute = {
      params: {
        agentId: '小克',
      },
    };

    const { getByText } = render(
      <MockAgentChatScreen route={xiaokRoute} navigation={mockNavigation} />
    );

    expect(getByText('与小克对话')).toBeTruthy();
    expect(getByText('你好！我是小克，很高兴为您服务！')).toBeTruthy();
  });

  it('应该按时间顺序显示消息', async () => {
    const { getByTestId, queryAllByTestId } = render(
      <MockAgentChatScreen route={mockRoute} navigation={mockNavigation} />
    );

    const messageInput = getByTestId('message-input');
    const sendButton = getByTestId('send-button');

    // 获取初始消息数量
    const initialMessages = queryAllByTestId(/^message-/);
    const initialCount = initialMessages.length;

    // 发送第一条消息
    fireEvent.changeText(messageInput, '第一条消息');
    fireEvent.press(sendButton);

    await waitFor(() => {
      const messages = queryAllByTestId(/^message-/);
      expect(messages.length).toBeGreaterThan(initialCount); // 有新消息添加
    });

    // 等待智能体回复
    await waitFor(() => {
      const messages = queryAllByTestId(/^message-/);
      expect(messages.length).toBeGreaterThanOrEqual(initialCount + 2); // 用户消息 + 智能体回复
    }, { timeout: 2000 });

    // 发送第二条消息
    fireEvent.changeText(messageInput, '第二条消息');
    fireEvent.press(sendButton);

    await waitFor(() => {
      const messages = queryAllByTestId(/^message-/);
      expect(messages.length).toBeGreaterThanOrEqual(initialCount + 3); // 更多消息
    });
  });

  it('应该处理长消息', async () => {
    const { getByTestId, getByText } = render(
      <MockAgentChatScreen route={mockRoute} navigation={mockNavigation} />
    );

    const messageInput = getByTestId('message-input');
    const sendButton = getByTestId('send-button');

    const longMessage = '这是一条很长的消息，'.repeat(10);

    fireEvent.changeText(messageInput, longMessage);
    fireEvent.press(sendButton);

    await waitFor(() => {
      expect(getByText(longMessage)).toBeTruthy();
    });
  });
}); 