
import Icon from './Icon';
import { colors, spacing, fonts } from '../../constants/theme';
import { accessibilityService, AgentAccessibilityHelper } from '../../services/accessibilityService';

import React, { useState, useRef, useEffect } from 'react';
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  Modal,
  Animated,
  Dimensions,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';

export type AgentType = 'xiaoai' | 'xiaoke' | 'laoke' | 'soer';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  metadata?: {
    suggestions?: string[];
    actions?: any[];
    diagnosisResults?: any;
  };
}

interface AgentChatInterfaceProps {
  visible: boolean;
  onClose: () => void;
  agentType: AgentType;
  userId: string;
  initialMessage?: string;
  accessibilityEnabled?: boolean;
}

const { width, height } = Dimensions.get('window');

// 智能体配置
const AGENT_CONFIG = useMemo(() => useMemo(() => {
  xiaoai: {
    name: '小艾',
    emoji: '🤖',
    color: '#007AFF',
    specialization: '健康诊断与建议',
    welcomeMessage: '你好！我是小艾，你的健康助手。我可以帮你进行健康咨询、五诊分析，还能为你提供个性化的健康建议。有什么我可以帮助你的吗？',
    quickReplies: ['我想做健康检查', '最近感觉不舒服', '想了解我的体质', '需要健康建议'],
  },
  xiaoke: {
    name: '小克',
    emoji: '👨‍⚕️',
    color: '#34C759',
    specialization: '医疗服务管理',
    welcomeMessage: '您好！我是小克，您的专业医疗服务管理助手。我可以帮您选择合适的诊断服务、预约医疗服务、管理健康订阅，还能为您推荐健康产品。',
    quickReplies: ['预约医生', '查看健康报告', '购买健康产品', '管理订阅服务'],
  },
  laoke: {
    name: '老克',
    emoji: '👴',
    color: '#8E44AD',
    specialization: '中医养生教育',
    welcomeMessage: '小友，你好！老夫是老克，专注中医养生教育多年。中医养生之道，在于顺应自然，调和阴阳。有什么养生问题，尽管问老夫。',
    quickReplies: ['学习中医理论', '了解养生方法', '体质调养建议', '中药材知识'],
  },
  soer: {
    name: '索儿',
    emoji: '👧',
    color: '#FF2D92',
    specialization: '生活方式指导',
    welcomeMessage: '嗨！我是索儿，你的生活方式指导助手。我会帮你规划健康的生活安排，提供个性化的生活建议，让你的每一天都充满活力！',
    quickReplies: ['制定生活计划', '健康生活建议', '工作生活平衡', '心情调节方法'],
  },
}, []), []);

const AgentChatInterface: React.FC<AgentChatInterfaceProps> = ({
  visible,
  onClose,
  agentType,
  userId,
  initialMessage,
  accessibilityEnabled = false,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const scrollViewRef = useMemo(() => useMemo(() => useRef<ScrollView>(null), []), []);
  const slideAnim = useMemo(() => useMemo(() => useRef(new Animated.Value(height)).current, []), []);

  const agentConfig = useMemo(() => useMemo(() => AGENT_CONFIG[agentType], []), []);
  const accessibilityHelper = useMemo(() => useMemo(() => new AgentAccessibilityHelper(accessibilityService, agentType), []), []);

  useEffect(() => {
    if (visible) {
      // 显示动画
      Animated.spring(slideAnim, {
        toValue: 0,
        useNativeDriver: true,
        tension: 100,
        friction: 8,
      }).start();

      // 初始化对话
      initializeChat();
    } else {
      // 隐藏动画
      Animated.spring(slideAnim, {
        toValue: height,
        useNativeDriver: true,
        tension: 100,
        friction: 8,
      }).start();
    }
  }, [visible]);

  useEffect(() => {
    if (initialMessage && visible) {
      setInputText(initialMessage);
    }
  }, [initialMessage, visible]);

  const initializeChat = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    const welcomeMessage: ChatMessage = {
      id: `msg_${Date.now()}`,
      role: 'assistant',
      content: agentConfig.welcomeMessage,
      timestamp: Date.now(),
      metadata: {
        suggestions: agentConfig.quickReplies,
      },
    };

    setMessages([welcomeMessage]);
  };

  const sendMessage = useMemo(() => useMemo(() => async (messageText?: string) => {
    const textToSend = messageText || inputText.trim(), []), []);
    if (!textToSend || isLoading) {return;}

    const userMessage: ChatMessage = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: textToSend,
      timestamp: Date.now(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      // 调用对应的智能体API
      const response = useMemo(() => useMemo(() => await callAgentAPI(textToSend), []), []);

      const assistantMessage: ChatMessage = {
        id: `msg_${Date.now()}`,
        role: 'assistant',
        content: response.text,
        timestamp: response.timestamp,
        metadata: response.metadata,
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error(`与${agentConfig.name}对话失败:`, error);
      
      const errorMessage: ChatMessage = {
        id: `msg_${Date.now()}`,
        role: 'assistant',
        content: `抱歉，我现在遇到了一些技术问题。请稍后再试，或者换个方式描述你的问题。`,
        timestamp: Date.now(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const callAgentAPI = useMemo(() => useMemo(() => async (message: string) => {
    // 根据智能体类型调用不同的API端点
    const apiEndpoints = {
      xiaoai: 'http://localhost:8080/api/agents/xiaoai/chat',
      xiaoke: 'http://localhost:8080/api/agents/xiaoke/chat',
      laoke: 'http://localhost:8080/api/agents/laoke/chat',
      soer: 'http://localhost:8080/api/agents/soer/chat',
    }, []), []);

    const response = useMemo(() => useMemo(() => await fetch(apiEndpoints[agentType], {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        userId,
        sessionId,
        context: {
          conversationHistory: messages,
          timestamp: Date.now(),
        },
      }),
    }), []), []);

    if (!response.ok) {
      throw new Error(`API调用失败: ${response.status}`);
    }

    return await response.json();
  };

  const handleQuickReply = useMemo(() => useMemo(() => useCallback( (reply: string) => {, []), []), []);
    sendMessage(reply);
  };

  // 语音输入处理
  const handleVoiceInput = useMemo(() => useMemo(() => async () => {
    if (!accessibilityEnabled) {return, []), []);}

    try {
      setIsRecording(true);
      // 这里应该集成实际的语音录制功能
      // 暂时模拟语音输入
      Alert.alert('语音输入', '语音输入功能正在开发中，请使用文字输入');
    } catch (error) {
      console.error('语音输入失败:', error);
      Alert.alert('错误', '语音输入失败，请重试');
    } finally {
      setIsRecording(false);
    }
  };

  // 切换语音模式
  const toggleVoiceMode = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    if (!accessibilityEnabled) {
      Alert.alert('提示', '请在设置中启用无障碍功能');
      return;
    }
    setIsVoiceMode(!isVoiceMode);
  };

  // 朗读消息
  const speakMessage = useMemo(() => useMemo(() => async (message: string) => {
    if (!accessibilityEnabled) {return, []), []);}

    try {
      const audioData = useMemo(() => useMemo(() => await accessibilityHelper.generateVoiceOutput(message, userId), []), []);
      if (audioData) {
        // 播放语音
        console.log('播放语音:', message);
      }
    } catch (error) {
      console.error('语音播放失败:', error);
    }
  };

  // 内容无障碍转换
  const makeContentAccessible = useMemo(() => useMemo(() => async (content: string, format: 'audio' | 'large-text' | 'high-contrast') => {
    if (!accessibilityEnabled) {return content, []), []);}

    try {
      const response = useMemo(() => useMemo(() => await accessibilityHelper.makeContentAccessible(content, userId, format), []), []);
      return response.accessibleContent || content;
    } catch (error) {
      console.error('内容转换失败:', error);
      return content;
    }
  };

  const scrollToBottom = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({ animated: true });
    }, 100);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const renderMessage = useMemo(() => useMemo(() => useCallback( (message: ChatMessage) => {, []), []), []);
    const isUser = useMemo(() => useMemo(() => message.role === 'user', []), []);
    
    return (
      <View
        key={message.id}
        style={[
          styles.messageContainer,
          isUser ? styles.userMessage : styles.assistantMessage,
        ]}
      >
        {!isUser && (
          <View style={styles.agentAvatar}>
            <Text style={styles.agentEmoji}>{agentConfig.emoji}</Text>
          </View>
        )}
        
        <View style={[
          styles.messageBubble,
          isUser ? styles.userBubble : styles.assistantBubble,
          { borderColor: agentConfig.color },
        ]}>
          <Text style={[
            styles.messageText,
            isUser ? styles.userText : styles.assistantText,
          ]}>
            {message.content}
          </Text>
          
          {/* 无障碍功能按钮 - 仅对助手消息显示 */}
          {!isUser && accessibilityEnabled && (
            <View style={styles.accessibilityButtons}>
              <TouchableOpacity
                style={styles.accessibilityButton}
                onPress={() => speakMessage(message.content)}
              >
                <Icon name="volume-high" size={16} color={agentConfig.color} />
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.accessibilityButton}
                onPress={() => makeContentAccessible(message.content, 'large-text')}
              >
                <Icon name="format-size" size={16} color={agentConfig.color} />
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.accessibilityButton}
                onPress={() => makeContentAccessible(message.content, 'high-contrast')}
              >
                <Icon name="contrast" size={16} color={agentConfig.color} />
              </TouchableOpacity>
            </View>
          )}
          
          <Text style={styles.messageTime}>
            {new Date(message.timestamp).toLocaleTimeString('zh-CN', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </Text>
        </View>

        {isUser && (
          <View style={styles.userAvatar}>
            <Icon name="account" size={20} color="white" />
          </View>
        )}
      </View>
    );
  };

  const renderQuickReplies = useMemo(() => useMemo(() => (suggestions: string[]) => (
    <View style={styles.quickRepliesContainer}>
      <Text style={styles.quickRepliesTitle}>快速回复：</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        {suggestions.map((suggestion, index) => (
          <TouchableOpacity
            key={index}
            style={[styles.quickReplyButton, { borderColor: agentConfig.color }]}
            onPress={() => handleQuickReply(suggestion)}
          >
            <Text style={[styles.quickReplyText, { color: agentConfig.color }]}>
              {suggestion}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  ), []), []);

  const handleClose = useMemo(() => useMemo(() => useCallback( () => {, []), []), []);
    Animated.spring(slideAnim, {
      toValue: height,
      useNativeDriver: true,
      tension: 100,
      friction: 8,
    }).start(() => {
      onClose();
      // 清理状态
      setMessages([]);
      setInputText('');
      setIsLoading(false);
    });
  };

  return (
    <Modal
      visible={visible}
      transparent={true}
      animationType="none"
      onRequestClose={handleClose}
    >
      <View style={styles.overlay}>
        <Animated.View
          style={[
            styles.container,
            {
              transform: [{ translateY: slideAnim }],
            },
          ]}
        >
          {/* 头部 */}
          <View style={[styles.header, { backgroundColor: agentConfig.color }]}>
            <View style={styles.headerLeft}>
              <Text style={styles.agentEmojiLarge}>{agentConfig.emoji}</Text>
              <View>
                <Text style={styles.agentName}>{agentConfig.name}</Text>
                <Text style={styles.agentSpecialization}>{agentConfig.specialization}</Text>
              </View>
            </View>
            <TouchableOpacity style={styles.closeButton} onPress={handleClose}>
              <Icon name="close" size={24} color="white" />
            </TouchableOpacity>
          </View>

          {/* 消息列表 */}
          <KeyboardAvoidingView
            style={styles.chatContainer}
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          >
            <ScrollView
              ref={scrollViewRef}
              style={styles.messagesContainer}
              showsVerticalScrollIndicator={false}
              contentContainerStyle={styles.messagesContent}
            >
              {messages.map(renderMessage)}
              
              {/* 显示快速回复 */}
              {messages.length > 0 && 
               messages[messages.length - 1].role === 'assistant' && 
               messages[messages.length - 1].metadata?.suggestions && 
               renderQuickReplies(messages[messages.length - 1].metadata!.suggestions!)}
              
              {isLoading && (
                <View style={styles.loadingContainer}>
                  <View style={styles.agentAvatar}>
                    <Text style={styles.agentEmoji}>{agentConfig.emoji}</Text>
                  </View>
                  <View style={[styles.messageBubble, styles.assistantBubble, styles.loadingBubble]}>
                    <ActivityIndicator size="small" color={agentConfig.color} />
                    <Text style={styles.loadingText}>正在思考...</Text>
                  </View>
                </View>
              )}
            </ScrollView>

            {/* 输入框 */}
            <View style={styles.inputContainer}>
              {/* 无障碍功能切换按钮 */}
              {accessibilityEnabled && (
                <TouchableOpacity
                  style={[styles.accessibilityToggle, isVoiceMode && { backgroundColor: agentConfig.color + '20' }]}
                  onPress={toggleVoiceMode}
                >
                  <Icon 
                    name={isVoiceMode ? "microphone" : "microphone-off"} 
                    size={20} 
                    color={isVoiceMode ? agentConfig.color : colors.textSecondary} 
                  />
                </TouchableOpacity>
              )}
              
              <TextInput
                style={[styles.textInput, accessibilityEnabled && styles.textInputWithAccessibility]}
                value={inputText}
                onChangeText={setInputText}
                placeholder={isVoiceMode ? `语音与${agentConfig.name}对话...` : `与${agentConfig.name}对话...`}
                placeholderTextColor={colors.textSecondary}
                multiline
                maxLength={500}
                editable={!isLoading && !isVoiceMode}
              />
              
              {/* 语音输入按钮 */}
              {accessibilityEnabled && isVoiceMode && (
                <TouchableOpacity
                  style={[
                    styles.voiceButton,
                    { backgroundColor: isRecording ? '#FF3B30' : agentConfig.color },
                  ]}
                  onPress={handleVoiceInput}
                  disabled={isLoading}
                >
                  <Icon 
                    name={isRecording ? "stop" : "microphone"} 
                    size={20} 
                    color="white" 
                  />
                </TouchableOpacity>
              )}
              
              {/* 发送按钮 */}
              {(!isVoiceMode || !accessibilityEnabled) && (
                <TouchableOpacity
                  style={[
                    styles.sendButton,
                    { backgroundColor: agentConfig.color },
                    (!inputText.trim() || isLoading) && styles.sendButtonDisabled,
                  ]}
                  onPress={() => sendMessage()}
                  disabled={!inputText.trim() || isLoading}
                >
                  <Icon name="send" size={20} color="white" />
                </TouchableOpacity>
              )}
            </View>
          </KeyboardAvoidingView>
        </Animated.View>
      </View>
    </Modal>
  );
};

const styles = useMemo(() => useMemo(() => StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  container: {
    flex: 1,
    backgroundColor: colors.background,
    marginTop: 50,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: spacing.lg,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  agentEmojiLarge: {
    fontSize: 32,
    marginRight: spacing.md,
  },
  agentName: {
    fontSize: fonts.size.lg,
    fontWeight: '600',
    color: 'white',
  },
  agentSpecialization: {
    fontSize: fonts.size.xs,
    color: 'rgba(255, 255, 255, 0.8)',
    marginTop: 2,
  },
  closeButton: {
    padding: spacing.sm,
  },
  chatContainer: {
    flex: 1,
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: spacing.md,
  },
  messageContainer: {
    flexDirection: 'row',
    marginBottom: spacing.md,
    alignItems: 'flex-end',
  },
  userMessage: {
    justifyContent: 'flex-end',
  },
  assistantMessage: {
    justifyContent: 'flex-start',
  },
  agentAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.surface,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.sm,
  },
  agentEmoji: {
    fontSize: 16,
  },
  userAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: spacing.sm,
  },
  messageBubble: {
    maxWidth: width * 0.7,
    padding: spacing.md,
    borderRadius: 16,
    borderWidth: 1,
  },
  userBubble: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
    borderBottomRightRadius: 4,
  },
  assistantBubble: {
    backgroundColor: colors.surface,
    borderBottomLeftRadius: 4,
  },
  messageText: {
    fontSize: fonts.size.md,
    lineHeight: 20,
  },
  userText: {
    color: 'white',
  },
  assistantText: {
    color: colors.text,
  },
  messageTime: {
    fontSize: fonts.size.xs,
    color: colors.textSecondary,
    marginTop: spacing.xs,
    textAlign: 'right',
  },
  quickRepliesContainer: {
    marginTop: spacing.md,
    marginBottom: spacing.lg,
  },
  quickRepliesTitle: {
    fontSize: fonts.size.xs,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
    marginLeft: 44, // 对齐消息气泡
  },
  quickReplyButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 20,
    borderWidth: 1,
    marginRight: spacing.sm,
    marginLeft: spacing.xs,
  },
  quickReplyText: {
    fontSize: fonts.size.xs,
    fontWeight: '500',
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    marginBottom: spacing.md,
  },
  loadingBubble: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: fonts.size.xs,
    color: colors.textSecondary,
    marginLeft: spacing.sm,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: spacing.md,
    backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 20,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    marginRight: spacing.sm,
    maxHeight: 100,
    fontSize: fonts.size.md,
    color: colors.text,
    backgroundColor: colors.background,
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonDisabled: {
    opacity: 0.5,
  },
  accessibilityButtons: {
    flexDirection: 'row',
    marginTop: spacing.xs,
    marginBottom: spacing.xs,
  },
  accessibilityButton: {
    padding: spacing.xs,
    marginRight: spacing.xs,
    borderRadius: 12,
    backgroundColor: colors.background,
    borderWidth: 1,
    borderColor: colors.border,
  },
  accessibilityToggle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.sm,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  textInputWithAccessibility: {
    marginRight: spacing.sm,
  },
  voiceButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: spacing.sm,
  },
}), []), []);

export default AgentChatInterface; 