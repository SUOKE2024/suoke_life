import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  StatusBar,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
// 消息类型定义
interface ChatMessage {
  id: string;
  content: string;
  timestamp: number;
  sender: 'user' | 'agent' | 'doctor' | 'other';
  senderName?: string;
  type: 'text' | 'image' | 'audio' | 'file';
  status?: 'sending' | 'sent' | 'delivered' | 'read' | 'failed';
}
// 路由参数类型
type ChatDetailRouteParams = {
  chatId: string,
  chatType: string;
  chatName: string;
};
type MainTabParamList = {
  ChatDetail: ChatDetailRouteParams;
};
type ChatDetailScreenNavigationProp = NativeStackNavigationProp<MainTabParamList, 'ChatDetail'>;
type ChatDetailScreenRouteProp = RouteProp<MainTabParamList, 'ChatDetail'>;
const ChatDetailScreen: React.FC = () => {
  const navigation = useNavigation<ChatDetailScreenNavigationProp>();
  const route = useRoute<ChatDetailScreenRouteProp>();
  const { chatId, chatType, chatName } = route.params;
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const flatListRef = useRef<FlatList>(null);
  // 从Redux获取用户信息
  const authState = useSelector(state: RootState) => state.auth);
  const user = 'user' in authState ? authState.user : null;
  // 生成智能体回复
  const generateAgentReply = (agentId: string, userMessage: string): string => {
    const replies: Record<string, string[]> = {
      xiaoai: [
        "我正在分析您的健康数据，请稍等...",根据您的描述，建议您注意休息和饮食调理。',
        "我为您推荐一些适合的健康建议，您可以参考一下。",您的健康状况看起来不错，继续保持良好的生活习惯。',
      ],
      xiaoke: [
        "从中医角度来看，您的症状可能与体质有关。",建议您进行四诊合参的全面检查。',
        "根据中医理论，这种情况需要辨证论治。",我建议您调整作息，配合适当的中医调理。',
      ],
      laoke: [
        "让我为您制定一个个性化的健康管理方案。",根据您的年龄和体质，我推荐以下康复训练。',
        "健康管理是一个长期过程，需要坚持和耐心。",您的康复进展很好，继续按照计划执行。',
      ],
      soer: [
        "生活方式的改变需要循序渐进，不要急于求成。",我为您推荐一些简单易行的日常保健方法。',
        "保持积极的心态对健康很重要。",今天的运动目标完成得如何？记得适量运动。',
      ],
    };
    const agentReplies = replies[agentId] || replies.xiaoai;
    return agentReplies[Math.floor(Math.random() * agentReplies.length)];
  };
  // 生成医生回复
  const generateDoctorReply = (userMessage: string): string => {
    const replies = [
      "感谢您的咨询，我会仔细查看您的情况。",根据您的描述，建议您到医院进行进一步检查。',
      "请按时服药，有任何不适及时联系我。",您的恢复情况良好，继续按照治疗方案执行。',
      '建议您注意饮食和作息，配合药物治疗。',
    ];
    return replies[Math.floor(Math.random() * replies.length)];
  };
  // 加载聊天历史
  const loadChatHistory = useCallback(async () => {
    try {
      setLoading(true);
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 1000));
      // 生成模拟聊天历史
      const mockMessages: ChatMessage[] = [
        {
      id: "1",
      content: chatType === 'agent' ?
            `您好！我是${chatName}，有什么可以帮助您的吗？` :
            chatType === 'doctor' ?
            `您好，我是${chatName}，请问有什么健康问题需要咨询？` :
            `欢迎加入${chatName}！`,
          timestamp: Date.now() - 3600000, // 1小时前
          sender: chatType === 'user' ? 'other' : chatType as any,
          senderName: chatName,
          type: 'text',
          status: 'read',
        },
        {
      id: "2",
      content: '您好，我想咨询一下健康管理的问题。',
          timestamp: Date.now() - 3000000, // 50分钟前
          sender: 'user',
          type: 'text',
          status: 'read',
        },
        {
      id: "3",
      content: chatType === 'agent' ?
            generateAgentReply(chatId, '健康管理') :
            chatType === 'doctor' ?
            generateDoctorReply('健康管理') :
            '这是一个很好的话题，大家可以一起讨论。',
          timestamp: Date.now() - 2700000, // 45分钟前
          sender: chatType === 'user' ? 'other' : chatType as any,
          senderName: chatType === 'user' ? '群成员' : chatName,
          type: 'text',
          status: 'read',
        },
      ];
      setMessages(mockMessages);
    } catch (error) {
      console.error('加载聊天历史失败:', error);
      Alert.alert("错误",加载聊天历史失败');
    } finally {
      setLoading(false);
    }
  }, [chatId, chatType, chatName]);
  // 发送消息
  const sendMessage = useCallback(async () => {
    if (!inputText.trim() || sending) return;
    const messageText = inputText.trim();
    setInputText('');
    setSending(true);
    // 创建用户消息
    const userMessage: ChatMessage = {,
  id: Date.now().toString(),
      content: messageText,
      timestamp: Date.now(),
      sender: 'user',
      type: 'text',
      status: 'sending',
    };
    setMessages(prev => [...prev, userMessage]);
    try {
      // 模拟发送延迟
      await new Promise(resolve => setTimeout(resolve, 500));
      // 更新消息状态为已发送
      setMessages(prev => prev.map(msg =>
        msg.id === userMessage.id ? { ...msg, status: 'sent' } : msg,
      ));
      // 生成回复（仅对智能体和医生）
      if (chatType === 'agent' || chatType === 'doctor') {
        setTimeout(async () => {
          const replyContent = chatType === 'agent' ?
            generateAgentReply(chatId, messageText) :
            generateDoctorReply(messageText);
          const replyMessage: ChatMessage = {,
  id: (Date.now() + 1).toString(),
            content: replyContent,
            timestamp: Date.now(),
            sender: chatType as any,
            senderName: chatName,
            type: 'text',
            status: 'read',
          };
          setMessages(prev => [...prev, replyMessage]);
        }, 1000 + Math.random() * 2000); // 1-3秒后回复
      }
    } catch (error) {
      console.error('发送消息失败:', error);
      // 更新消息状态为失败
      setMessages(prev => prev.map(msg =>
        msg.id === userMessage.id ? { ...msg, status: 'failed' } : msg,
      ));
      Alert.alert("错误",发送消息失败，请重试');
    } finally {
      setSending(false);
    }
  }, [inputText, sending, chatType, chatId, chatName]);
  // 初始化加载
  useEffect() => {
    loadChatHistory();
  }, [loadChatHistory]);
  // 自动滚动到底部
  useEffect() => {
    if (messages.length > 0) {
      setTimeout() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages]);
  // 格式化时间
  const formatTime = (timestamp: number): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    if (diffMins < 1) return '刚刚';
    if (diffMins < 60) return `${diffMins}分钟前`;
    if (diffHours < 24) return date.toLocaleTimeString('zh-CN', {
      hour: "2-digit",
      minute: '2-digit' });
    return date.toLocaleDateString('zh-CN', {
      month: "short",
      day: 'numeric' });
  };
  // 获取消息状态图标
  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'sending':
        return <ActivityIndicator size="small" color="#999" />;
      case 'sent':
        return <Icon name="check" size={16} color="#999" />;
      case 'delivered':
        return <Icon name="check-all" size={16} color="#999" />;
      case 'read':
        return <Icon name="check-all" size={16} color="#007AFF" />;
      case 'failed':
        return <Icon name="alert-circle" size={16} color="#FF3B30" />;
      default:
        return null;
    }
  };
  // 渲染消息项
  const renderMessage = ({ item }: { item: ChatMessage }) => {
    const isUser = item.sender === 'user';
    return (
      <View style={[styles.messageContainer, isUser ? styles.userMessage : styles.otherMessage]}>
        {!isUser && item.senderName && (
          <Text style={styles.senderName}>{item.senderName}</Text>
        )}
        <View style={[styles.messageBubble, isUser ? styles.userBubble : styles.otherBubble]}>
          <Text style={[styles.messageText, isUser ? styles.userText : styles.otherText]}>
            {item.content}
          </Text>
        </View>
        <View style={[styles.messageInfo, isUser ? styles.userInfo : styles.otherInfo]}>
          <Text style={styles.timeText}>{formatTime(item.timestamp)}</Text>
          {isUser && getStatusIcon(item.status)}
        </View>
      </View>
    );
  };
  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
            <Icon name="arrow-left" size={24} color="#333" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>{chatName}</Text>
          <TouchableOpacity style={styles.moreButton}>
            <Icon name="dots-vertical" size={24} color="#333" />
          </TouchableOpacity>
        </View>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>加载中...</Text>
        </View>
      </SafeAreaView>
    );
  }
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#fff" />
      {}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Icon name="arrow-left" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{chatName}</Text>
        <TouchableOpacity style={styles.moreButton}>
          <Icon name="dots-vertical" size={24} color="#333" />
        </TouchableOpacity>
      </View>
      <KeyboardAvoidingView;
        style={styles.content}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        {}
        <FlatList;
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={(item) => item.id}
          style={styles.messagesList}
          contentContainerStyle={styles.messagesContent}
          showsVerticalScrollIndicator={false}
        />
        {}
        <View style={styles.inputContainer}>
          <TextInput;
            style={styles.textInput}
            placeholder="输入消息..."
            value={inputText}
            onChangeText={setInputText}
            multiline;
            maxLength={500}
            placeholderTextColor="#999"
          />
          <TouchableOpacity;
            style={[styles.sendButton, (!inputText.trim() || sending) && styles.sendButtonDisabled]}
            onPress={sendMessage}
            disabled={!inputText.trim() || sending}
          >
            {sending ? (
              <ActivityIndicator size="small" color="#fff" />
            ) : (
              <Icon name="send" size={20} color="#fff" />
            )}
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#f6f6f6',
  },
  header: {,
  flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  backButton: {,
  padding: 8,
    marginRight: 8,
  },
  headerTitle: {,
  flex: 1,
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  moreButton: {,
  padding: 8,
  },
  content: {,
  flex: 1,
  },
  loadingContainer: {,
  flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {,
  fontSize: 16,
    color: '#666',
    marginTop: 10,
  },
  messagesList: {,
  flex: 1,
  },
  messagesContent: {,
  padding: 16,
  },
  messageContainer: {,
  marginBottom: 16,
  },
  userMessage: {,
  alignItems: 'flex-end',
  },
  otherMessage: {,
  alignItems: 'flex-start',
  },
  senderName: {,
  fontSize: 12,
    color: '#666',
    marginBottom: 4,
    marginLeft: 8,
  },
  messageBubble: {,
  maxWidth: '80%',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
  },
  userBubble: {,
  backgroundColor: '#007AFF',
  },
  otherBubble: {,
  backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  messageText: {,
  fontSize: 16,
    lineHeight: 22,
  },
  userText: {,
  color: '#fff',
  },
  otherText: {,
  color: '#333',
  },
  messageInfo: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  userInfo: {,
  justifyContent: 'flex-end',
  },
  otherInfo: {,
  justifyContent: 'flex-start',
  },
  timeText: {,
  fontSize: 12,
    color: '#999',
    marginHorizontal: 4,
  },
  inputContainer: {,
  flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  textInput: {,
  flex: 1,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    marginRight: 12,
    maxHeight: 100,
    fontSize: 16,
    color: '#333',
  },
  sendButton: {,
  width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonDisabled: {,
  backgroundColor: '#ccc',
  },
});
export default ChatDetailScreen;