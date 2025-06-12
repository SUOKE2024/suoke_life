import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  Alert,
  Dimensions,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useNavigation, useRoute } from '@react-navigation/native';

// 导入服务
import { IntegratedApiService } from '../../services/IntegratedApiService';

const { width: screenWidth } = Dimensions.get('window');

// 消息类型定义
interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'agent';
  timestamp: Date;
  type: 'text' | 'image' | 'audio' | 'diagnosis';
  status: 'sending' | 'sent' | 'delivered' | 'read' | 'failed';
  metadata?: {
    agentType?: string;
    confidence?: number;
    suggestions?: string[];
    diagnosisData?: any;
  };
}

// 智能体信息
interface AgentInfo {
  id: string;
  name: string;
  avatar: string;
  status: 'online' | 'offline' | 'busy';
  description: string;
  capabilities: string[];
}

const AgentChatScreen: React.FC = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const scrollViewRef = useRef<ScrollView>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [agentInfo, setAgentInfo] = useState<AgentInfo | null>(null);
  const apiService = new IntegratedApiService();

  // 从路由参数获取智能体信息
  const { agentId, agentName, agentType } = route.params as {
    agentId: string;
    agentName: string;
    agentType: string;
  };

  // 初始化智能体信息和聊天历史
  useEffect(() => {
    initializeChat();
  }, [agentId]);

  const initializeChat = useCallback(async () => {
    try {
      setIsLoading(true);

      // 设置智能体信息
      const agentData: AgentInfo = {
        id: agentId,
        name: agentName,
        avatar: getAgentAvatar(agentId),
        status: 'online',
        description: getAgentDescription(agentId),
        capabilities: getAgentCapabilities(agentId),
      };
      setAgentInfo(agentData);

      // 加载聊天历史（这里可以从本地存储或API获取）
      const welcomeMessage: ChatMessage = {
        id: `welcome_${Date.now()}`,
        text: getWelcomeMessage(agentId),
        sender: 'agent',
        timestamp: new Date(),
        type: 'text',
        status: 'read',
        metadata: {
          agentType: agentId,
          confidence: 1.0,
        },
      };

      setMessages([welcomeMessage]);
    } catch (error) {
      console.error('初始化聊天失败:', error);
      Alert.alert('错误', '初始化聊天失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  }, [agentId, agentName]);

  // 获取智能体头像
  const getAgentAvatar = (id: string): string => {
    const avatars: Record<string, string> = {
      xiaoai: '🤖',
      xiaoke: '🏥',
      laoke: '👨‍⚕️',
      soer: '📊',
    };
    return avatars[id] || '🤖';
  };

  // 获取智能体描述
  const getAgentDescription = (id: string): string => {
    const descriptions: Record<string, string> = {
      xiaoai: '多模态感知专家，擅长图像分析、语音处理和健康监测',
      xiaoke: '健康服务专家，提供产品推荐和预约管理',
      laoke: '知识传播专家，专注中医文化和社区管理',
      soer: '营养管理专家，优化生活方式和饮食搭配',
    };
    return descriptions[id] || '智能助手';
  };

  // 获取智能体能力
  const getAgentCapabilities = (id: string): string[] => {
    const capabilities: Record<string, string[]> = {
      xiaoai: ['图像分析', '语音识别', '健康监测', '五诊协调'],
      xiaoke: ['健康服务', '产品推荐', '预约管理', '用户体验'],
      laoke: ['中医知识', '文化传播', '社区管理', '教育服务'],
      soer: ['营养管理', '生活方式', '数据分析', '个性化推荐'],
    };
    return capabilities[id] || ['智能对话'];
  };

  // 获取欢迎消息
  const getWelcomeMessage = (id: string): string => {
    const welcomeMessages: Record<string, string> = {
      xiaoai: '您好！我是小艾，您的健康管理助手。我可以帮您进行健康监测、图像分析和五诊协调。有什么可以为您服务的吗？',
      xiaoke: '您好！我是小克，您的健康服务专家。我可以为您推荐优质的健康产品和服务，还能帮您预约各种医疗服务。',
      laoke: '您好！我是老克，中医文化传播者。我可以为您分享中医养生知识，解答健康疑问，还能为您提供个性化的养生建议。',
      soer: '您好！我是索儿，您的营养管理专家。我可以帮您制定个性化的营养计划，优化生活方式，让您更健康！',
    };
    return welcomeMessages[id] || '您好！我是您的智能助手，有什么可以帮您的吗？';
  };

  // 发送消息
  const sendMessage = useCallback(async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      text: inputText.trim(),
      sender: 'user',
      timestamp: new Date(),
      type: 'text',
      status: 'sending',
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);

    try {
      // 调用智能体API
      const response = await apiService.agents.chat(inputText.trim(), agentId);

      if (response.success && response.data) {
        const agentMessage: ChatMessage = {
          id: `agent_${Date.now()}`,
          text: response.data.response || response.data.text || '抱歉，我暂时无法回答这个问题。',
          sender: 'agent',
          timestamp: new Date(),
          type: 'text',
          status: 'read',
          metadata: {
            agentType: agentId,
            confidence: response.data.confidence || 0.8,
            suggestions: response.data.suggestions || [],
          },
        };

        setMessages((prev) => [
          ...prev.map((msg) =>
            msg.id === userMessage.id ? { ...msg, status: 'delivered' } : msg
          ),
          agentMessage,
        ]);
      } else {
        throw new Error(response.message || '智能体响应失败');
      }
    } catch (error) {
      console.error('发送消息失败:', error);
      
      // 更新用户消息状态为失败
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === userMessage.id ? { ...msg, status: 'failed' } : msg
        )
      );

      // 添加错误消息
      const errorMessage: ChatMessage = {
        id: `error_${Date.now()}`,
        text: '抱歉，我现在无法回复您的消息。请稍后再试。',
        sender: 'agent',
        timestamp: new Date(),
        type: 'text',
        status: 'read',
        metadata: {
          agentType: agentId,
          confidence: 0.0,
        },
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  }, [inputText, isLoading, agentId, apiService]);

  // 重试发送消息
  const retryMessage = useCallback(async (messageId: string) => {
    const message = messages.find((msg) => msg.id === messageId);
    if (!message || message.sender !== 'user') return;

    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === messageId ? { ...msg, status: 'sending' } : msg
      )
    );

    setIsTyping(true);

    try {
      const response = await apiService.agents.chat(message.text, agentId);

      if (response.success && response.data) {
        const agentMessage: ChatMessage = {
          id: `agent_${Date.now()}`,
          text: response.data.response || response.data.text || '抱歉，我暂时无法回答这个问题。',
          sender: 'agent',
          timestamp: new Date(),
          type: 'text',
          status: 'read',
          metadata: {
            agentType: agentId,
            confidence: response.data.confidence || 0.8,
            suggestions: response.data.suggestions || [],
          },
        };

        setMessages((prev) => [
          ...prev.map((msg) =>
            msg.id === messageId ? { ...msg, status: 'delivered' } : msg
          ),
          agentMessage,
        ]);
      } else {
        throw new Error(response.message || '智能体响应失败');
      }
    } catch (error) {
      console.error('重试发送失败:', error);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === messageId ? { ...msg, status: 'failed' } : msg
        )
      );
    } finally {
      setIsTyping(false);
    }
  }, [messages, agentId, apiService]);

  // 滚动到底部
  const scrollToBottom = useCallback(() => {
    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({ animated: true });
    }, 100);
  }, []);

  // 当消息更新时滚动到底部
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // 渲染消息状态图标
  const renderMessageStatus = (status: string) => {
    switch (status) {
      case 'sending':
        return <ActivityIndicator size="small" color="#999" />;
      case 'sent':
        return <Icon name="check" size={16} color="#999" />;
      case 'delivered':
        return <Icon name="done-all" size={16} color="#999" />;
      case 'read':
        return <Icon name="done-all" size={16} color="#4CAF50" />;
      case 'failed':
        return <Icon name="error" size={16} color="#F44336" />;
      default:
        return null;
    }
  };

  // 渲染消息气泡
  const renderMessage = (message: ChatMessage) => {
    const isUser = message.sender === 'user';
    
    return (
      <View
        key={message.id}
        style={[
          styles.messageContainer,
          isUser ? styles.userMessageContainer : styles.agentMessageContainer,
        ]}
      >
        {!isUser && (
          <Text style={styles.agentAvatar}>{agentInfo?.avatar}</Text>
        )}
        <View
          style={[
            styles.messageBubble,
            isUser ? styles.userMessageBubble : styles.agentMessageBubble,
          ]}
        >
          <Text
            style={[
              styles.messageText,
              isUser ? styles.userMessageText : styles.agentMessageText,
            ]}
          >
            {message.text}
          </Text>
          <View style={styles.messageFooter}>
            <Text style={styles.messageTime}>
              {message.timestamp.toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </Text>
            {isUser && (
              <View style={styles.messageStatus}>
                {message.status === 'failed' ? (
                  <TouchableOpacity onPress={() => retryMessage(message.id)}>
                    {renderMessageStatus(message.status)}
                  </TouchableOpacity>
                ) : (
                  renderMessageStatus(message.status)
                )}
              </View>
            )}
          </View>
          {message.metadata?.suggestions && message.metadata.suggestions.length > 0 && (
            <View style={styles.suggestionsContainer}>
              {message.metadata.suggestions.map((suggestion, index) => (
                <TouchableOpacity
                  key={index}
                  style={styles.suggestionButton}
                  onPress={() => setInputText(suggestion)}
                >
                  <Text style={styles.suggestionText}>{suggestion}</Text>
                </TouchableOpacity>
              ))}
            </View>
          )}
        </View>
      </View>
    );
  };

  // 渲染正在输入指示器
  const renderTypingIndicator = () => {
    if (!isTyping) return null;

    return (
      <View style={styles.typingContainer}>
        <Text style={styles.agentAvatar}>{agentInfo?.avatar}</Text>
        <View style={styles.typingBubble}>
          <View style={styles.typingDots}>
            <View style={[styles.typingDot, { animationDelay: '0ms' }]} />
            <View style={[styles.typingDot, { animationDelay: '150ms' }]} />
            <View style={[styles.typingDot, { animationDelay: '300ms' }]} />
          </View>
        </View>
      </View>
    );
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
        <Text style={styles.loadingText}>正在连接{agentName}...</Text>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      {/* 头部 */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Icon name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <View style={styles.agentInfoContainer}>
          <Text style={styles.agentName}>{agentInfo?.name}</Text>
          <Text style={styles.agentStatus}>
            {agentInfo?.status === 'online' ? '在线' : '离线'}
          </Text>
        </View>
        <TouchableOpacity
          style={styles.moreButton}
          onPress={() => {
            // 显示更多选项
            Alert.alert(
              '智能体信息',
              `${agentInfo?.description}\n\n核心能力：\n${agentInfo?.capabilities.join('、')}`,
              [{ text: '确定' }]
            );
          }}
        >
          <Icon name="more-vert" size={24} color="#333" />
        </TouchableOpacity>
      </View>

      {/* 消息列表 */}
      <ScrollView
        ref={scrollViewRef}
        style={styles.messagesContainer}
        contentContainerStyle={styles.messagesContent}
        showsVerticalScrollIndicator={false}
      >
        {messages.map(renderMessage)}
        {renderTypingIndicator()}
      </ScrollView>

      {/* 输入区域 */}
      <View style={styles.inputContainer}>
        <View style={styles.inputWrapper}>
          <TextInput
            style={styles.textInput}
            value={inputText}
            onChangeText={setInputText}
            placeholder={`与${agentName}对话...`}
            multiline
            maxLength={1000}
            editable={!isLoading}
          />
          <TouchableOpacity
            style={[
              styles.sendButton,
              (!inputText.trim() || isLoading) && styles.sendButtonDisabled,
            ]}
            onPress={sendMessage}
            disabled={!inputText.trim() || isLoading}
          >
            <Icon
              name="send"
              size={20}
              color={!inputText.trim() || isLoading ? '#ccc' : '#2196F3'}
            />
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  backButton: {
    marginRight: 12,
  },
  agentInfoContainer: {
    flex: 1,
  },
  agentName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  agentStatus: {
    fontSize: 12,
    color: '#4CAF50',
    marginTop: 2,
  },
  moreButton: {
    marginLeft: 12,
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: 16,
  },
  messageContainer: {
    flexDirection: 'row',
    marginBottom: 16,
    alignItems: 'flex-end',
  },
  userMessageContainer: {
    justifyContent: 'flex-end',
  },
  agentMessageContainer: {
    justifyContent: 'flex-start',
  },
  agentAvatar: {
    fontSize: 24,
    marginRight: 8,
    marginBottom: 4,
  },
  messageBubble: {
    maxWidth: screenWidth * 0.75,
    borderRadius: 18,
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  userMessageBubble: {
    backgroundColor: '#2196F3',
    borderBottomRightRadius: 4,
  },
  agentMessageBubble: {
    backgroundColor: '#ffffff',
    borderBottomLeftRadius: 4,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  userMessageText: {
    color: '#ffffff',
  },
  agentMessageText: {
    color: '#333',
  },
  messageFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 4,
  },
  messageTime: {
    fontSize: 12,
    color: '#999',
  },
  messageStatus: {
    marginLeft: 8,
  },
  suggestionsContainer: {
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  suggestionButton: {
    backgroundColor: '#f0f0f0',
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginBottom: 4,
  },
  suggestionText: {
    fontSize: 14,
    color: '#2196F3',
  },
  typingContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    marginBottom: 16,
  },
  typingBubble: {
    backgroundColor: '#ffffff',
    borderRadius: 18,
    borderBottomLeftRadius: 4,
    paddingHorizontal: 16,
    paddingVertical: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  typingDots: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  typingDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#ccc',
    marginHorizontal: 2,
  },
  inputContainer: {
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    backgroundColor: '#f5f5f5',
    borderRadius: 24,
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  textInput: {
    flex: 1,
    fontSize: 16,
    maxHeight: 100,
    color: '#333',
  },
  sendButton: {
    marginLeft: 12,
    padding: 8,
  },
  sendButtonDisabled: {
    opacity: 0.5,
  },
});

export default AgentChatScreen;