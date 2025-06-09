import { RouteProp, useNavigation, useRoute } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Animated,
  Dimensions,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  StatusBar,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';

const { width, height } = Dimensions.get('window');

// 消息类型定义
interface Message {
  id: string;,
  text: string;
  sender: 'user' | 'agent';,
  timestamp: Date;
  type: 'text' | 'image' | 'voice' | 'file' | 'diagnosis';,
  status: 'sending' | 'sent' | 'delivered' | 'read' | 'failed';
  metadata?: {
    imageUrl?: string;
    voiceUrl?: string;
    fileUrl?: string;
    fileName?: string;
    diagnosisData?: any;
  };
}

// 智能体信息类型
interface AgentInfo {
  id: string;,
  name: string;
  avatar: string;,
  description: string;
  capabilities: string[];,
  serviceEndpoint: string;
  status: 'online' | 'offline' | 'busy';,
  colors: {
    primary: string;,
  secondary: string;
    accent: string;
  };
}

// 路由参数类型
type RootStackParamList = {
  AgentChat: { agentId: string; agentName: string };
};

type AgentChatScreenRouteProp = RouteProp<RootStackParamList, 'AgentChat'>;
type AgentChatScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'AgentChat'
>;

const AgentChatScreen: React.FC = () => {
  const navigation = useNavigation<AgentChatScreenNavigationProp>();
  const route = useRoute<AgentChatScreenRouteProp>();
  const { agentId, agentName } = route.params;

  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [agentInfo, setAgentInfo] = useState<AgentInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);

  const flatListRef = useRef<FlatList>(null);
  const typingAnimation = useRef(new Animated.Value(0)).current;

  // 从Redux获取用户信息
  const authState = useSelector(state: RootState) => state.auth);
  const user = 'user' in authState ? authState.user : null;

  // 智能体配置
  const agentConfigs: Record<string, AgentInfo> = {
    xiaoai: {,
  id: 'xiaoai',
      name: '小艾',
      avatar: '🤖',
      description: '多模态感知智能体，擅长图像、语音、文本分析',
      capabilities: ['图像分析', '语音识别', '多模态融合', '健康检测'],
      serviceEndpoint: 'http://localhost:8015',
      status: 'online',
      colors: {,
  primary: '#4A90E2',
        secondary: '#E3F2FD',
        accent: '#2196F3',
      },
    },
    xiaoke: {,
  id: 'xiaoke',
      name: '小克',
      avatar: '🧘‍♂️',
      description: '健康服务智能体，提供个性化健康管理服务',
      capabilities: ['健康评估', '服务推荐', '预约管理', '健康计划'],
      serviceEndpoint: 'http://localhost:8016',
      status: 'online',
      colors: {,
  primary: '#7B68EE',
        secondary: '#F3E5F5',
        accent: '#9C27B0',
      },
    },
    laoke: {,
  id: 'laoke',
      name: '老克',
      avatar: '👨‍⚕️',
      description: '知识传播智能体，分享健康知识和经验',
      capabilities: ['知识问答', '健康教育', '经验分享', '学习指导'],
      serviceEndpoint: 'http://localhost:8017',
      status: 'online',
      colors: {,
  primary: '#FF6B6B',
        secondary: '#FFEBEE',
        accent: '#F44336',
      },
    },
    soer: {,
  id: 'soer',
      name: '索儿',
      avatar: '🏃‍♀️',
      description: '营养生活智能体，制定营养计划和生活方式',
      capabilities: ['营养分析', '运动指导', '生活规划', '习惯养成'],
      serviceEndpoint: 'http://localhost:8018',
      status: 'online',
      colors: {,
  primary: '#4ECDC4',
        secondary: '#E0F2F1',
        accent: '#009688',
      },
    },
  };

  // 初始化智能体信息
  useEffect() => {
    const agent = agentConfigs[agentId];
    if (agent) {
      setAgentInfo(agent);
      // 添加欢迎消息
      const welcomeMessage: Message = {,
  id: 'welcome',
        text: `您好！我是${agent.name}，${agent.description}。有什么可以帮助您的吗？`,
        sender: 'agent',
        timestamp: new Date(),
        type: 'text',
        status: 'read',
      };
      setMessages([welcomeMessage]);
    }
    setLoading(false);
  }, [agentId]);

  // 启动打字动画
  const startTypingAnimation = () => {
    setIsTyping(true);
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
  };

  // 停止打字动画
  const stopTypingAnimation = () => {
    setIsTyping(false);
    typingAnimation.stopAnimation();
    typingAnimation.setValue(0);
  };

  // 发送消息
  const sendMessage = useCallback(async () => {
    if (!inputText.trim() || !agentInfo) return;

    const userMessage: Message = {,
  id: Date.now().toString(),
      text: inputText.trim(),
      sender: 'user',
      timestamp: new Date(),
      type: 'text',
      status: 'sending',
    };

    setMessages(prev) => [...prev, userMessage]);
    setInputText('');

    // 滚动到底部
    setTimeout() => {
      flatListRef.current?.scrollToEnd({ animated: true });
    }, 100);

    try {
      // 更新消息状态为已发送
      setMessages(prev) =>
        prev.map(msg) =>
          msg.id === userMessage.id ? { ...msg, status: 'sent' as const } : msg;
        )
      );

      // 开始打字动画
      startTypingAnimation();

      // 模拟API调用
      const response = await simulateAgentResponse(inputText.trim(), agentInfo);

      // 停止打字动画
      stopTypingAnimation();

      // 添加智能体回复
      const agentMessage: Message = {,
  id: (Date.now() + 1).toString(),
        text: response.text,
        sender: 'agent',
        timestamp: new Date(),
        type: response.type || 'text',
        status: 'read',
        metadata: response.metadata,
      };

      setMessages(prev) => [...prev, agentMessage]);

      // 更新用户消息状态为已读
      setMessages(prev) =>
        prev.map(msg) =>
          msg.id === userMessage.id ? { ...msg, status: 'read' as const } : msg;
        )
      );
    } catch (error) {
      console.error('发送消息失败:', error);
      stopTypingAnimation();

      // 更新消息状态为失败
      setMessages(prev) =>
        prev.map(msg) =>
          msg.id === userMessage.id;
            ? { ...msg, status: 'failed' as const }
            : msg;
        )
      );

      Alert.alert('错误', '发送消息失败，请重试');
    }
  }, [inputText, agentInfo]);

  // 模拟智能体响应
  const simulateAgentResponse = async (userInput: string, agent: AgentInfo) => {
    // 模拟网络延迟
    await new Promise(resolve) =>
      setTimeout(resolve, 1000 + Math.random() * 2000)
    );

    const responses = {
      xiaoai: [
        '我可以帮您分析图像、语音或其他多模态数据。请上传您需要分析的内容。',
        '基于您的描述，我建议进行多模态健康检测。这将包括面部分析、语音分析等。',
        '我的多模态感知能力可以同时处理图像、语音和文本信息，为您提供综合分析。',
      ],
      xiaoke: [
        '根据您的需求，我为您推荐以下健康服务：定期体检、营养咨询、运动指导。',
        '我可以帮您预约专业的健康服务，包括中医诊疗、营养咨询等。',
        '基于您的健康档案，我建议制定个性化的健康管理计划。',
      ],
      laoke: [
        '关于这个健康问题，中医理论认为需要从整体调理的角度来看待。',
        '我来为您分享一些相关的健康知识和养生经验。',
        '根据传统中医理论，这种情况通常与体质和生活习惯有关。',
      ],
      soer: [
        '根据您的情况，我建议调整饮食结构，增加优质蛋白质和维生素的摄入。',
        '我为您制定了一个营养均衡的饮食计划，包括三餐搭配和运动建议。',
        '健康的生活方式包括规律作息、均衡饮食和适量运动。',
      ],
    };

    const agentResponses =
      responses[agent.id as keyof typeof responses] || responses.xiaoai;
    const randomResponse =
      agentResponses[Math.floor(Math.random() * agentResponses.length)];

    return {
      text: randomResponse,
      type: 'text' as const,
      metadata: {},
    };
  };

  // 渲染消息项
  const renderMessage = ({ item: message }: { item: Message }) => {
    const isUser = message.sender === 'user';
    const colors = agentInfo?.colors || agentConfigs.xiaoai.colors;

    return (
      <View;
        style={[
          styles.messageContainer,
          isUser ? styles.userMessageContainer : styles.agentMessageContainer,
        ]}
      >
        {!isUser && (
          <View;
            style={[
              styles.avatarContainer,
              { backgroundColor: colors.secondary },
            ]}
          >
            <Text style={styles.avatarText}>{agentInfo?.avatar}</Text>
          </View>
        )}

        <View;
          style={[
            styles.messageBubble,
            isUser;
              ? [styles.userBubble, { backgroundColor: colors.primary }]
              : styles.agentBubble,
          ]}
        >
          <Text;
            style={[
              styles.messageText,
              isUser ? styles.userMessageText : styles.agentMessageText,
            ]}
          >
            {message.text}
          </Text>

          <View style={styles.messageFooter}>
            <Text;
              style={[
                styles.timestampText,
                isUser ? styles.userTimestampText : styles.agentTimestampText,
              ]}
            >
              {message.timestamp.toLocaleTimeString('zh-CN', {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </Text>

            {isUser && (
              <Icon;
                name={getStatusIcon(message.status)}
                size={12}
                color={getStatusColor(message.status)}
                style={styles.statusIcon}
              />
            )}
          </View>
        </View>
      </View>
    );
  };

  // 获取状态图标
  const getStatusIcon = (status: Message['status']) => {
    switch (status) {
      case 'sending':
        return 'clock-outline';
      case 'sent':
        return 'check';
      case 'delivered':
        return 'check-all';
      case 'read':
        return 'check-all';
      case 'failed':
        return 'alert-circle-outline';
      default:
        return 'check';
    }
  };

  // 获取状态颜色
  const getStatusColor = (status: Message['status']) => {
    switch (status) {
      case 'sending':
        return '#999';
      case 'sent':
        return '#999';
      case 'delivered':
        return '#4CAF50';
      case 'read':
        return '#4CAF50';
      case 'failed':
        return '#F44336';
      default:
        return '#999';
    }
  };

  // 渲染打字指示器
  const renderTypingIndicator = () => {
    if (!isTyping || !agentInfo) return null;

    const colors = agentInfo.colors;

    return (
      <View style={[styles.messageContainer, styles.agentMessageContainer]}>
        <View;
          style={[
            styles.avatarContainer,
            { backgroundColor: colors.secondary },
          ]}
        >
          <Text style={styles.avatarText}>{agentInfo.avatar}</Text>
        </View>

        <View style={styles.typingBubble}>
          <Animated.View;
            style={[styles.typingDot, { opacity: typingAnimation }]}
          />
          <Animated.View;
            style={[
              styles.typingDot,
              {
                opacity: typingAnimation,
                transform: [{ scale: typingAnimation }],
              },
            ]}
          />
          <Animated.View;
            style={[styles.typingDot, { opacity: typingAnimation }]}
          />
        </View>
      </View>
    );
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar;
          barStyle="light-content"
          backgroundColor={agentConfigs.xiaoai.colors.primary}
        />
        <View style={styles.loadingContainer}>
          <ActivityIndicator;
            size="large"
            color={agentConfigs.xiaoai.colors.primary}
          />
          <Text style={styles.loadingText}>连接中...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (!agentInfo) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#F44336" />
        <View style={styles.errorContainer}>
          <Icon name="robot-confused" size={64} color="#F44336" />
          <Text style={styles.errorTitle}>智能体不存在</Text>
          <Text style={styles.errorSubtitle}>请检查智能体ID是否正确</Text>
          <TouchableOpacity;
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.backButtonText}>返回</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const colors = agentInfo.colors;

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={colors.primary} />

      {/* 头部 */}
      <View style={[styles.header, { backgroundColor: colors.primary }]}>
        <TouchableOpacity;
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Icon name="arrow-left" size={24} color="#FFFFFF" />
        </TouchableOpacity>

        <View style={styles.headerInfo}>
          <View;
            style={[styles.headerAvatar, { backgroundColor: colors.secondary }]}
          >
            <Text style={styles.headerAvatarText}>{agentInfo.avatar}</Text>
          </View>
          <View style={styles.headerTextContainer}>
            <Text style={styles.headerTitle}>{agentInfo.name}</Text>
            <Text style={styles.headerSubtitle}>
              {agentInfo.status === 'online' ? '在线' : '离线'}
            </Text>
          </View>
        </View>

        <TouchableOpacity style={styles.moreButton}>
          <Icon name="dots-vertical" size={24} color="#FFFFFF" />
        </TouchableOpacity>
      </View>

      {/* 消息列表 */}
      <KeyboardAvoidingView;
        style={styles.chatContainer}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <FlatList;
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={(item) => item.id}
          style={styles.messagesList}
          contentContainerStyle={styles.messagesContainer}
          showsVerticalScrollIndicator={false}
          onContentSizeChange={() =>
            flatListRef.current?.scrollToEnd({ animated: true })
          }
          ListFooterComponent={renderTypingIndicator}
        />

        {/* 输入框 */}
        <View style={styles.inputContainer}>
          <View style={styles.inputWrapper}>
            <TextInput;
              style={styles.textInput}
              placeholder={`与${agentInfo.name}对话...`}
              placeholderTextColor="#999"
              value={inputText}
              onChangeText={setInputText}
              multiline;
              maxLength={1000}
            />

            <TouchableOpacity;
              style={[
                styles.sendButton,
                { backgroundColor: inputText.trim() ? colors.primary : '#CCC' },
              ]}
              onPress={sendMessage}
              disabled={!inputText.trim()}
            >
              <Icon name="send" size={20} color="#FFFFFF" />
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#F8F9FA',
  },
  loadingContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {,
  marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  errorContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  errorTitle: {,
  fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 16,
    marginBottom: 8,
  },
  errorSubtitle: {,
  fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 24,
  },
  header: {,
  flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  backButton: {,
  padding: 8,
    marginRight: 8,
  },
  headerInfo: {,
  flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerAvatar: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  headerAvatarText: {,
  fontSize: 20,
  },
  headerTextContainer: {,
  flex: 1,
  },
  headerTitle: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  headerSubtitle: {,
  fontSize: 12,
    color: '#E3F2FD',
    marginTop: 2,
  },
  moreButton: {,
  padding: 8,
  },
  chatContainer: {,
  flex: 1,
  },
  messagesList: {,
  flex: 1,
  },
  messagesContainer: {,
  paddingVertical: 16,
  },
  messageContainer: {,
  flexDirection: 'row',
    marginVertical: 4,
    paddingHorizontal: 16,
  },
  userMessageContainer: {,
  justifyContent: 'flex-end',
  },
  agentMessageContainer: {,
  justifyContent: 'flex-start',
  },
  avatarContainer: {,
  width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
    alignSelf: 'flex-end',
  },
  avatarText: {,
  fontSize: 16,
  },
  messageBubble: {,
  maxWidth: width * 0.75,
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 20,
  },
  userBubble: {,
  borderBottomRightRadius: 4,
  },
  agentBubble: {,
  backgroundColor: '#FFFFFF',
    borderBottomLeftRadius: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  messageText: {,
  fontSize: 16,
    lineHeight: 22,
  },
  userMessageText: {,
  color: '#FFFFFF',
  },
  agentMessageText: {,
  color: '#333',
  },
  messageFooter: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
    marginTop: 4,
  },
  timestampText: {,
  fontSize: 11,
    marginRight: 4,
  },
  userTimestampText: {,
  color: 'rgba(255, 255, 255, 0.7)',
  },
  agentTimestampText: {,
  color: '#999',
  },
  statusIcon: {,
  marginLeft: 2,
  },
  typingBubble: {,
  flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 20,
    borderBottomLeftRadius: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  typingDot: {,
  width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#999',
    marginHorizontal: 2,
  },
  inputContainer: {,
  paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  inputWrapper: {,
  flexDirection: 'row',
    alignItems: 'flex-end',
    backgroundColor: '#F5F5F5',
    borderRadius: 25,
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  textInput: {,
  flex: 1,
    fontSize: 16,
    color: '#333',
    maxHeight: 100,
    marginRight: 8,
  },
  sendButton: {,
  width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  backButtonText: {,
  color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default AgentChatScreen;
