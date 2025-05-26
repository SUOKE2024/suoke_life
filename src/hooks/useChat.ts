import { useState, useCallback, useRef } from 'react';
import { FlatList } from 'react-native';
import { Message } from '../screens/components/ChatMessage';
import { AgentType } from '../screens/components/AgentCard';

export interface UseChatReturn {
  messages: Message[];
  isTyping: boolean;
  sendMessage: (text: string, agent: AgentType, generateResponse?: (input: string, agent: AgentType) => string) => Promise<void>;
  addMessage: (message: Message) => void;
  clearMessages: () => void;
  scrollToBottom: () => void;
  flatListRef: React.RefObject<FlatList | null>;
}

export const useChat = (initialMessages: Message[] = []): UseChatReturn => {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [isTyping, setIsTyping] = useState(false);
  const flatListRef = useRef<FlatList>(null);

  const addMessage = useCallback((message: Message) => {
    setMessages(prev => [...prev, message]);
  }, []);

  const sendMessage = useCallback(async (
    text: string,
    agent: AgentType,
    generateResponse?: (input: string, agent: AgentType) => string
  ) => {
    if (!text.trim()) {
      return;
    }

    // 添加用户消息
    const userMessage: Message = {
      id: Date.now().toString(),
      text: text.trim(),
      sender: 'user',
      timestamp: new Date(),
      status: 'sent',
    };

    addMessage(userMessage);
    setIsTyping(true);

    // 模拟智能体回复
    try {
      const delay = 1000 + Math.random() * 2000; // 1-3秒随机延迟
      
      await new Promise<void>(resolve => setTimeout(() => resolve(), delay));

      const responseText = generateResponse 
        ? generateResponse(text, agent)
        : '收到您的消息，正在处理中...';

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: responseText,
        sender: agent,
        timestamp: new Date(),
        status: 'delivered',
      };

      addMessage(agentMessage);
    } catch (error) {
      console.error('发送消息失败:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        text: '抱歉，我暂时无法回复您的消息，请稍后再试。',
        sender: agent,
        timestamp: new Date(),
        status: 'failed',
      };

      addMessage(errorMessage);
    } finally {
      setIsTyping(false);
    }
  }, [addMessage]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const scrollToBottom = useCallback(() => {
    if (flatListRef.current && messages.length > 0) {
      flatListRef.current.scrollToEnd({ animated: true });
    }
  }, [messages.length]);

  return {
    messages,
    isTyping,
    sendMessage,
    addMessage,
    clearMessages,
    scrollToBottom,
    flatListRef,
  };
}; 