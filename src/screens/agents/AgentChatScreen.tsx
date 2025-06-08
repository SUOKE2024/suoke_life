import { useNavigation, useRoute } from '@react-navigation/native';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
    Alert,
    Animated,
    Dimensions,
    KeyboardAvoidingView,
    Platform,
    ScrollView,
    StyleSheet,
    Text,
    TextInput,
    TouchableOpacity,
    View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { borderRadius, colors, shadows, spacing, typography } from '../../constants/theme';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent';
  timestamp: Date;
  type?: 'text' | 'image' | 'file' | 'suggestion';
  metadata?: any;
}

interface Agent {
  id: string;
  name: string;
  avatar: string;
  specialty: string;
  status: 'online' | 'offline' | 'busy';
  description: string;
}

const AgentChatScreen: React.FC = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const scrollViewRef = useRef<ScrollView>(null);
  const inputRef = useRef<TextInput>(null);
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [agent, setAgent] = useState<Agent | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  
  // 动画值
  const typingAnimation = useRef(new Animated.Value(0)).current;
  const sendButtonScale = useRef(new Animated.Value(1)).current;

  // 模拟智能体数据
  useEffect(() => {
    const agentData: Agent = {
      id: 'xiaoai',
      name: '小艾',
      avatar: '🤖',
      specialty: '健康咨询',
      status: 'online',
      description: '您的专属健康管理助手',
    };
    setAgent(agentData);

    // 初始欢迎消息
    const welcomeMessage: Message = {
      id: '1',
      text: '您好！我是小艾，您的专属健康管理助手。我可以帮您分析健康数据、制定健康计划、回答健康问题。有什么可以帮助您的吗？',
      sender: 'agent',
      timestamp: new Date(),
      type: 'text',
    };
    setMessages([welcomeMessage]);

    // 设置建议
    setSuggestions([
      '分析我的健康数据',
      '制定运动计划',
      '饮食建议',
      '睡眠优化',
    ]);
  }, []);

  // 打字动画
  useEffect(() => {
    if (isTyping) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(typingAnimation, {
            toValue: 1,
            duration: 600,
            useNativeDriver: true,
          }),
          Animated.timing(typingAnimation, {
            toValue: 0,
            duration: 600,
            useNativeDriver: true,
          }),
        ])
      ).start();
    } else {
      typingAnimation.setValue(0);
    }
  }, [isTyping, typingAnimation]);

  // 滚动到底部
  const scrollToBottom = useCallback(() => {
    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({ animated: true });
    }, 100);
  }, []);

  // 发送消息
  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: text.trim(),
      sender: 'user',
      timestamp: new Date(),
      type: 'text',
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);
    scrollToBottom();

    // 按钮动画
    Animated.sequence([
      Animated.timing(sendButtonScale, {
        toValue: 0.8,
        duration: 100,
        useNativeDriver: true,
      }),
      Animated.timing(sendButtonScale, {
        toValue: 1,
        duration: 100,
        useNativeDriver: true,
      }),
    ]).start();

    // 模拟智能体回复
    setTimeout(() => {
      const agentResponse = generateAgentResponse(text);
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: agentResponse,
        sender: 'agent',
        timestamp: new Date(),
        type: 'text',
      };

      setMessages(prev => [...prev, agentMessage]);
      setIsTyping(false);
      scrollToBottom();
    }, 1500 + Math.random() * 1000);
  }, [scrollToBottom, sendButtonScale]);

  // 生成智能体回复
  const generateAgentResponse = (userText: string): string => {
    const responses = {
      '健康数据': '根据您最近的健康数据分析，您的整体健康状况良好。心率平均72bpm，血压120/80mmHg，体重稳定。建议继续保持规律运动和健康饮食。',
      '运动计划': '为您推荐以下运动计划：\n\n🏃‍♂️ 有氧运动：每周3-4次，每次30-45分钟\n💪 力量训练：每周2次，每次20-30分钟\n🧘‍♀️ 瑜伽拉伸：每天10-15分钟\n\n记得循序渐进，量力而行！',
      '饮食': '健康饮食建议：\n\n🥗 多吃蔬菜水果，每天5-7份\n🐟 适量优质蛋白质\n🌾 选择全谷物食品\n💧 每天饮水1.5-2升\n🚫 少油少盐少糖\n\n均衡营养是健康的基础！',
      '睡眠': '优质睡眠建议：\n\n⏰ 规律作息，每天同一时间睡觉起床\n🌙 睡前1小时避免电子设备\n🛏️ 保持卧室安静、黑暗、凉爽\n☕ 下午3点后避免咖啡因\n🧘‍♀️ 睡前可以做些放松练习\n\n良好的睡眠是健康的重要支柱！',
    };

    // 简单的关键词匹配
    for (const [keyword, response] of Object.entries(responses)) {
      if (userText.includes(keyword)) {
        return response;
      }
    }

    return '感谢您的问题！我会根据您的具体情况为您提供个性化的健康建议。如果您有具体的健康问题或需求，请详细描述，我会为您提供更精准的帮助。';
  };

  // 处理建议点击
  const handleSuggestionPress = (suggestion: string) => {
    sendMessage(suggestion);
  };

  // 处理语音录制
  const handleVoiceRecord = () => {
    setIsRecording(!isRecording);
    // TODO: 实现语音录制功能
    Alert.alert('语音功能', '语音录制功能即将上线！');
  };

  // 渲染消息
  const renderMessage = (message: Message, index: number) => {
    const isUser = message.sender === 'user';
    const isLastMessage = index === messages.length - 1;

    return (
      <View
        key={message.id}
        style={[
          styles.messageContainer,
          isUser ? styles.userMessageContainer : styles.agentMessageContainer,
        ]}
      >
        {!isUser && (
          <View style={styles.agentAvatar}>
            <Text style={styles.agentAvatarText}>{agent?.avatar}</Text>
          </View>
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
          <Text
            style={[
              styles.messageTime,
              isUser ? styles.userMessageTime : styles.agentMessageTime,
            ]}
          >
            {message.timestamp.toLocaleTimeString('zh-CN', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </Text>
        </View>

        {isUser && (
          <View style={styles.userAvatar}>
            <Icon name="account" size={20} color={colors.white} />
          </View>
        )}
      </View>
    );
  };

  // 渲染打字指示器
  const renderTypingIndicator = () => {
    if (!isTyping) return null;

    return (
      <View style={styles.typingContainer}>
        <View style={styles.agentAvatar}>
          <Text style={styles.agentAvatarText}>{agent?.avatar}</Text>
        </View>
        <View style={styles.typingBubble}>
          <Animated.View
            style={[
              styles.typingDot,
              {
                opacity: typingAnimation.interpolate({
                  inputRange: [0, 1],
                  outputRange: [0.3, 1],
                }),
              },
            ]}
          />
          <Animated.View
            style={[
              styles.typingDot,
              {
                opacity: typingAnimation.interpolate({
                  inputRange: [0, 0.5, 1],
                  outputRange: [0.3, 1, 0.3],
                }),
              },
            ]}
          />
          <Animated.View
            style={[
              styles.typingDot,
              {
                opacity: typingAnimation.interpolate({
                  inputRange: [0, 1],
                  outputRange: [1, 0.3],
                }),
              },
            ]}
          />
        </View>
      </View>
    );
  };

  // 渲染建议
  const renderSuggestions = () => {
    if (messages.length > 1) return null;

    return (
      <View style={styles.suggestionsContainer}>
        <Text style={styles.suggestionsTitle}>您可以问我：</Text>
        <View style={styles.suggestionsGrid}>
          {suggestions.map((suggestion, index) => (
            <TouchableOpacity
              key={index}
              style={styles.suggestionButton}
              onPress={() => handleSuggestionPress(suggestion)}
            >
              <Text style={styles.suggestionText}>{suggestion}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* 头部 */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Icon name="arrow-left" size={24} color={colors.text} />
        </TouchableOpacity>
        
        <View style={styles.agentInfo}>
          <View style={styles.agentHeaderAvatar}>
            <Text style={styles.agentHeaderAvatarText}>{agent?.avatar}</Text>
          </View>
          <View style={styles.agentDetails}>
            <Text style={styles.agentName}>{agent?.name}</Text>
            <View style={styles.agentStatusContainer}>
              <View
                style={[
                  styles.statusDot,
                  { backgroundColor: agent?.status === 'online' ? colors.success : colors.gray400 },
                ]}
              />
              <Text style={styles.agentStatus}>
                {agent?.status === 'online' ? '在线' : '离线'}
              </Text>
            </View>
          </View>
        </View>

        <TouchableOpacity style={styles.moreButton}>
          <Icon name="dots-vertical" size={24} color={colors.text} />
        </TouchableOpacity>
      </View>

      {/* 消息列表 */}
      <KeyboardAvoidingView
        style={styles.chatContainer}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        <ScrollView
          ref={scrollViewRef}
          style={styles.messagesContainer}
          contentContainerStyle={styles.messagesContent}
          showsVerticalScrollIndicator={false}
          onContentSizeChange={scrollToBottom}
        >
          {messages.map(renderMessage)}
          {renderTypingIndicator()}
          {renderSuggestions()}
        </ScrollView>

        {/* 输入区域 */}
        <View style={styles.inputContainer}>
          <View style={styles.inputWrapper}>
            <TouchableOpacity
              style={styles.attachButton}
              onPress={() => Alert.alert('附件', '附件功能即将上线！')}
            >
              <Icon name="paperclip" size={20} color={colors.textSecondary} />
            </TouchableOpacity>

            <TextInput
              ref={inputRef}
              style={styles.textInput}
              placeholder="输入消息..."
              placeholderTextColor={colors.textSecondary}
              value={inputText}
              onChangeText={setInputText}
              multiline
              maxLength={500}
              onSubmitEditing={() => sendMessage(inputText)}
              blurOnSubmit={false}
            />

            <TouchableOpacity
              style={[styles.voiceButton, isRecording && styles.voiceButtonActive]}
              onPress={handleVoiceRecord}
            >
              <Icon
                name={isRecording ? 'microphone' : 'microphone-outline'}
                size={20}
                color={isRecording ? colors.error : colors.textSecondary}
              />
            </TouchableOpacity>

            <Animated.View style={{ transform: [{ scale: sendButtonScale }] }}>
              <TouchableOpacity
                style={[
                  styles.sendButton,
                  inputText.trim() ? styles.sendButtonActive : styles.sendButtonInactive,
                ]}
                onPress={() => sendMessage(inputText)}
                disabled={!inputText.trim()}
              >
                <Icon
                  name="send"
                  size={20}
                  color={inputText.trim() ? colors.white : colors.textSecondary}
                />
              </TouchableOpacity>
            </Animated.View>
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    ...shadows.sm,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  agentInfo: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: spacing.md,
  },
  agentHeaderAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  agentHeaderAvatarText: {
    fontSize: 20,
  },
  agentDetails: {
    marginLeft: spacing.sm,
  },
  agentName: {
    fontSize: typography.fontSize.base,
    fontWeight: '600' as const,
    color: colors.text,
  },
  agentStatusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 2,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: spacing.xs,
  },
  agentStatus: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  moreButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.gray100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  chatContainer: {
    flex: 1,
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
  },
  messageContainer: {
    flexDirection: 'row',
    marginBottom: spacing.md,
    alignItems: 'flex-end',
  },
  userMessageContainer: {
    justifyContent: 'flex-end',
  },
  agentMessageContainer: {
    justifyContent: 'flex-start',
  },
  agentAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.sm,
  },
  agentAvatarText: {
    fontSize: 16,
  },
  userAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.secondary,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: spacing.sm,
  },
  messageBubble: {
    maxWidth: screenWidth * 0.7,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.lg,
  },
  userMessageBubble: {
    backgroundColor: colors.primary,
    borderBottomRightRadius: 4,
  },
  agentMessageBubble: {
    backgroundColor: colors.surface,
    borderBottomLeftRadius: 4,
    ...shadows.sm,
  },
  messageText: {
    fontSize: typography.fontSize.base,
    lineHeight: 22,
  },
  userMessageText: {
    color: colors.white,
  },
  agentMessageText: {
    color: colors.text,
  },
  messageTime: {
    fontSize: typography.fontSize.xs,
    marginTop: spacing.xs,
  },
  userMessageTime: {
    color: colors.white,
    opacity: 0.8,
    textAlign: 'right',
  },
  agentMessageTime: {
    color: colors.textSecondary,
  },
  typingContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    marginBottom: spacing.md,
  },
  typingBubble: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.lg,
    borderBottomLeftRadius: 4,
    ...shadows.sm,
  },
  typingDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.textSecondary,
    marginHorizontal: 2,
  },
  suggestionsContainer: {
    marginTop: spacing.lg,
  },
  suggestionsTitle: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  suggestionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  suggestionButton: {
    backgroundColor: colors.surface,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    ...shadows.sm,
  },
  suggestionText: {
    fontSize: typography.fontSize.sm,
    color: colors.primary,
  },
  inputContainer: {
    backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    backgroundColor: colors.background,
    borderRadius: borderRadius.xl,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderWidth: 1,
    borderColor: colors.border,
  },
  attachButton: {
    width: 36,
    height: 36,
    justifyContent: 'center',
    alignItems: 'center',
  },
  textInput: {
    flex: 1,
    fontSize: typography.fontSize.base,
    color: colors.text,
    maxHeight: 100,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.xs,
  },
  voiceButton: {
    width: 36,
    height: 36,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 18,
  },
  voiceButtonActive: {
    backgroundColor: colors.error + '20',
  },
  sendButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: spacing.xs,
  },
  sendButtonActive: {
    backgroundColor: colors.primary,
  },
  sendButtonInactive: {
    backgroundColor: colors.gray200,
  },
});

export default AgentChatScreen; 