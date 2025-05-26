import React, { useState, useRef, useEffect } from 'react';
import {
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
} from 'react-native';
import Icon from '../../../components/common/Icon';
import { colors } from '../../../constants/theme';
import { xiaoaiAgent } from '../../../agents/xiaoai/XiaoaiAgent';
import {
  ChatContext,
  ChatMessage,
  ChatResponse,
  UserProfile,
} from '../../../agents/xiaoai/types';

interface XiaoaiChatInterfaceProps {
  visible: boolean;
  onClose: () => void;
  userId: string;
}

const { width, height } = Dimensions.get('window');

const XiaoaiChatInterface: React.FC<XiaoaiChatInterfaceProps> = ({
  visible,
  onClose,
  userId,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const scrollViewRef = useRef<ScrollView>(null);
  const slideAnim = useRef(new Animated.Value(height)).current;

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

  const initializeChat = () => {
    const welcomeMessage: ChatMessage = {
      id: `msg_${Date.now()}`,
      role: 'assistant',
      content: '你好！我是小艾，你的健康助手。我可以帮你进行健康咨询、四诊分析，还能为你提供个性化的健康建议。有什么我可以帮助你的吗？',
      timestamp: Date.now(),
    };

    setMessages([welcomeMessage]);
  };

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: inputText.trim(),
      timestamp: Date.now(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      // 构建聊天上下文
      const context: ChatContext = {
        userId,
        sessionId,
        conversationHistory: [...messages, userMessage],
        timestamp: Date.now(),
      };

      // 调用小艾智能体
      const response = await xiaoaiAgent.chat(userMessage.content, context);

      const assistantMessage: ChatMessage = {
        id: `msg_${Date.now()}`,
        role: 'assistant',
        content: response.text,
        timestamp: response.timestamp,
        metadata: {
          diagnosisResults: response.diagnosisResults,
          suggestions: response.suggestions,
        },
      };

      setMessages(prev => [...prev, assistantMessage]);

      // 如果有建议的操作，显示快捷按钮
      if (response.actions && response.actions.length > 0) {
        showActionButtons(response.actions);
      }

    } catch (error) {
      console.error('发送消息失败:', error);
      
      const errorMessage: ChatMessage = {
        id: `msg_${Date.now()}`,
        role: 'assistant',
        content: '抱歉，我现在遇到了一些技术问题。请稍后再试，或者换个方式描述你的问题。',
        timestamp: Date.now(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const showActionButtons = (actions: any[]) => {
    const actionTexts = actions.map(action => action.prompt).join('\n\n');
    
    Alert.alert(
      '建议的操作',
      actionTexts,
      [
        { text: '稍后再说', style: 'cancel' },
        { text: '好的，继续', onPress: () => handleActionAccepted(actions) }
      ]
    );
  };

  const handleActionAccepted = (actions: any[]) => {
    // 处理用户接受的操作建议
    actions.forEach(action => {
      if (action.autoStart) {
        // 自动开始某些操作
        console.log('自动开始操作:', action.type);
      }
    });
  };

  const handleSuggestionPress = (suggestion: string) => {
    setInputText(suggestion);
  };

  const scrollToBottom = () => {
    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({ animated: true });
    }, 100);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const renderMessage = (message: ChatMessage) => {
    const isUser = message.role === 'user';
    
    return (
      <View
        key={message.id}
        style={[
          styles.messageContainer,
          isUser ? styles.userMessage : styles.assistantMessage,
        ]}
      >
        <View style={[
          styles.messageBubble,
          isUser ? styles.userBubble : styles.assistantBubble,
        ]}>
          <Text style={[
            styles.messageText,
            isUser ? styles.userText : styles.assistantText,
          ]}>
            {message.content}
          </Text>
          
          {/* 显示诊断结果 */}
          {message.metadata?.diagnosisResults && (
            <View style={styles.diagnosisResults}>
              <Text style={styles.diagnosisTitle}>诊断分析</Text>
              {message.metadata.diagnosisResults.integrated && (
                <Text style={styles.diagnosisText}>
                  {message.metadata.diagnosisResults.integrated.overallAssessment}
                </Text>
              )}
            </View>
          )}
          
          {/* 显示建议 */}
          {message.metadata?.suggestions && message.metadata.suggestions.length > 0 && (
            <View style={styles.suggestionsContainer}>
              <Text style={styles.suggestionsTitle}>建议操作：</Text>
              {message.metadata.suggestions.map((suggestion, index) => (
                <TouchableOpacity
                  key={index}
                  style={styles.suggestionButton}
                  onPress={() => handleSuggestionPress(suggestion)}
                >
                  <Text style={styles.suggestionText}>{suggestion}</Text>
                </TouchableOpacity>
              ))}
            </View>
          )}
        </View>
        
        <Text style={styles.timestamp}>
          {new Date(message.timestamp).toLocaleTimeString()}
        </Text>
      </View>
    );
  };

  return (
    <Modal
      visible={visible}
      transparent
      animationType="none"
      onRequestClose={onClose}
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
          <View style={styles.header}>
            <View style={styles.headerLeft}>
              <View style={styles.avatarContainer}>
                <Icon name="robot" size={24} color={colors.white} />
              </View>
              <View>
                <Text style={styles.headerTitle}>小艾</Text>
                <Text style={styles.headerSubtitle}>健康助手</Text>
              </View>
            </View>
            
            <TouchableOpacity onPress={onClose} style={styles.closeButton}>
              <Icon name="close" size={24} color={colors.text} />
            </TouchableOpacity>
          </View>

          {/* 消息列表 */}
          <ScrollView
            ref={scrollViewRef}
            style={styles.messagesContainer}
            showsVerticalScrollIndicator={false}
          >
            {messages.map(renderMessage)}
            
            {isLoading && (
              <View style={styles.loadingContainer}>
                <View style={styles.loadingBubble}>
                  <Text style={styles.loadingText}>小艾正在思考...</Text>
                </View>
              </View>
            )}
          </ScrollView>

          {/* 输入区域 */}
          <KeyboardAvoidingView
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
            style={styles.inputContainer}
          >
            <View style={styles.inputRow}>
              <TextInput
                style={styles.textInput}
                value={inputText}
                onChangeText={setInputText}
                placeholder="输入你的健康问题..."
                placeholderTextColor={colors.textSecondary}
                multiline
                maxLength={500}
                onSubmitEditing={sendMessage}
                blurOnSubmit={false}
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
                  color={(!inputText.trim() || isLoading) ? colors.textSecondary : colors.white} 
                />
              </TouchableOpacity>
            </View>
            
            {/* 快捷建议 */}
            <ScrollView
              horizontal
              style={styles.quickSuggestions}
              showsHorizontalScrollIndicator={false}
            >
              {['我感觉头痛', '最近失眠', '想做体检', '查看舌象', '听听咳嗽'].map((suggestion, index) => (
                <TouchableOpacity
                  key={index}
                  style={styles.quickSuggestionButton}
                  onPress={() => handleSuggestionPress(suggestion)}
                >
                  <Text style={styles.quickSuggestionText}>{suggestion}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </KeyboardAvoidingView>
        </Animated.View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  container: {
    height: height * 0.85,
    backgroundColor: colors.background,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    overflow: 'hidden',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatarContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text,
  },
  headerSubtitle: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  closeButton: {
    padding: 8,
  },
  messagesContainer: {
    flex: 1,
    padding: 16,
  },
  messageContainer: {
    marginBottom: 16,
  },
  userMessage: {
    alignItems: 'flex-end',
  },
  assistantMessage: {
    alignItems: 'flex-start',
  },
  messageBubble: {
    maxWidth: '80%',
    padding: 12,
    borderRadius: 16,
  },
  userBubble: {
    backgroundColor: colors.primary,
    borderBottomRightRadius: 4,
  },
  assistantBubble: {
    backgroundColor: colors.white,
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: colors.border,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  userText: {
    color: colors.white,
  },
  assistantText: {
    color: colors.text,
  },
  timestamp: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 4,
  },
  diagnosisResults: {
    marginTop: 8,
    padding: 8,
    backgroundColor: colors.background,
    borderRadius: 8,
  },
  diagnosisTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: colors.primary,
    marginBottom: 4,
  },
  diagnosisText: {
    fontSize: 14,
    color: colors.text,
  },
  suggestionsContainer: {
    marginTop: 8,
  },
  suggestionsTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: 8,
  },
  suggestionButton: {
    backgroundColor: colors.background,
    padding: 8,
    borderRadius: 8,
    marginBottom: 4,
  },
  suggestionText: {
    fontSize: 14,
    color: colors.primary,
  },
  loadingContainer: {
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  loadingBubble: {
    backgroundColor: colors.white,
    padding: 12,
    borderRadius: 16,
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: colors.border,
  },
  loadingText: {
    fontSize: 16,
    color: colors.textSecondary,
    fontStyle: 'italic',
  },
  inputContainer: {
    backgroundColor: colors.white,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    padding: 16,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    marginBottom: 12,
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginRight: 12,
    maxHeight: 100,
    fontSize: 16,
    color: colors.text,
  },
  sendButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: colors.border,
  },
  quickSuggestions: {
    flexDirection: 'row',
  },
  quickSuggestionButton: {
    backgroundColor: colors.background,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 16,
    marginRight: 8,
    borderWidth: 1,
    borderColor: colors.border,
  },
  quickSuggestionText: {
    fontSize: 14,
    color: colors.text,
  },
});

export default XiaoaiChatInterface; 